```markdown
# Rate Limiting Reference

## Overview
Rate limiting protects APIs from abuse and ensures fair resource usage. Frappe provides built-in rate limiting decorators and Redis-based throttling.

## Built-in Rate Limiter

### Basic Usage
```python
from frappe.rate_limiter import rate_limit

@frappe.whitelist(allow_guest=True)
@rate_limit(limit=100, seconds=60)
def my_api_endpoint():
    """Max 100 requests per minute per IP."""
    return {"status": "ok"}
```

### Parameters
| Parameter | Description | Default |
|-----------|-------------|---------|
| `limit` | Max requests in window | Required |
| `seconds` | Time window in seconds | Required |
| `key` | Custom cache key | IP-based |

### Custom Key Functions
```python
@rate_limit(limit=10, seconds=60, key=lambda: frappe.session.user)
def user_rate_limited():
    """Rate limit per user instead of per IP."""
    pass

@rate_limit(limit=5, seconds=3600, key=lambda: frappe.form_dict.get("api_key"))
def api_key_rate_limited():
    """Rate limit per API key."""
    pass
```

## Custom Rate Limiter

### Using Redis
```python
import frappe

def check_rate_limit(key, limit, window_seconds):
    """
    Check if rate limit exceeded.
    Returns (allowed: bool, remaining: int, reset_at: int)
    """
    redis = frappe.cache()
    
    # Create keys
    count_key = f"rate_limit:{key}:count"
    reset_key = f"rate_limit:{key}:reset"
    
    # Get current count
    current = redis.get_value(count_key) or 0
    reset_at = redis.get_value(reset_key)
    
    now = frappe.utils.now_datetime().timestamp()
    
    # Check if window expired
    if reset_at is None or now >= reset_at:
        # Start new window
        reset_at = now + window_seconds
        redis.set_value(count_key, 1, expires_in_sec=window_seconds + 1)
        redis.set_value(reset_key, reset_at, expires_in_sec=window_seconds + 1)
        return True, limit - 1, int(reset_at)
    
    # Check limit
    if current >= limit:
        return False, 0, int(reset_at)
    
    # Increment counter
    redis.set_value(count_key, current + 1, expires_in_sec=window_seconds + 1)
    return True, limit - current - 1, int(reset_at)


@frappe.whitelist(allow_guest=True)
def rate_limited_endpoint():
    """Custom rate limiting with response headers."""
    key = frappe.local.request_ip
    allowed, remaining, reset_at = check_rate_limit(key, limit=100, window_seconds=60)
    
    # Set rate limit headers
    frappe.local.response.headers["X-RateLimit-Limit"] = "100"
    frappe.local.response.headers["X-RateLimit-Remaining"] = str(remaining)
    frappe.local.response.headers["X-RateLimit-Reset"] = str(reset_at)
    
    if not allowed:
        frappe.local.response["http_status_code"] = 429
        frappe.throw("Rate limit exceeded. Try again later.", frappe.RateLimitExceededError)
    
    return {"status": "ok"}
```

## Tiered Rate Limits

### By User Type
```python
def get_rate_limit_for_user():
    """Different limits based on user type."""
    user = frappe.session.user
    
    if user == "Guest":
        return 20, 60  # 20 requests/minute for guests
    
    roles = frappe.get_roles(user)
    
    if "API Premium" in roles:
        return 1000, 60  # Premium API users
    
    if "API User" in roles:
        return 100, 60  # Standard API users
    
    return 50, 60  # Default authenticated users


@frappe.whitelist()
def tiered_rate_limited():
    limit, window = get_rate_limit_for_user()
    key = frappe.session.user or frappe.local.request_ip
    
    allowed, remaining, reset_at = check_rate_limit(key, limit, window)
    
    if not allowed:
        frappe.throw("Rate limit exceeded", frappe.RateLimitExceededError)
    
    return {"status": "ok", "remaining": remaining}
```

### By Endpoint
```python
ENDPOINT_LIMITS = {
    "search": (10, 60),      # Expensive: 10/min
    "list": (100, 60),       # Standard: 100/min
    "read": (200, 60),       # Light: 200/min
    "export": (5, 3600),     # Very limited: 5/hour
}

def rate_limit_endpoint(endpoint_type):
    """Decorator factory for endpoint-specific limits."""
    limit, window = ENDPOINT_LIMITS.get(endpoint_type, (100, 60))
    return rate_limit(limit=limit, seconds=window)

@frappe.whitelist()
@rate_limit_endpoint("search")
def search_api():
    pass

@frappe.whitelist()
@rate_limit_endpoint("export")
def export_api():
    pass
```

## Sliding Window Rate Limiter

More accurate than fixed windows:

```python
import time

def sliding_window_rate_limit(key, limit, window_seconds):
    """
    Sliding window rate limiter using sorted sets.
    """
    redis = frappe.cache()
    now = time.time()
    window_start = now - window_seconds
    
    sorted_set_key = f"rate_limit_sw:{key}"
    
    # Remove old entries
    redis.zremrangebyscore(sorted_set_key, 0, window_start)
    
    # Count current entries
    current_count = redis.zcard(sorted_set_key)
    
    if current_count >= limit:
        return False, 0
    
    # Add new entry
    redis.zadd(sorted_set_key, {str(now): now})
    redis.expire(sorted_set_key, window_seconds + 1)
    
    return True, limit - current_count - 1
```

## Token Bucket Algorithm

For burst handling:

```python
class TokenBucket:
    def __init__(self, key, capacity, refill_rate):
        """
        capacity: Max tokens (burst limit)
        refill_rate: Tokens added per second
        """
        self.key = f"token_bucket:{key}"
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.redis = frappe.cache()
    
    def consume(self, tokens=1):
        now = time.time()
        
        # Get current state
        data = self.redis.get_value(self.key) or {
            "tokens": self.capacity,
            "last_update": now
        }
        
        # Calculate tokens to add
        elapsed = now - data["last_update"]
        data["tokens"] = min(
            self.capacity,
            data["tokens"] + elapsed * self.refill_rate
        )
        data["last_update"] = now
        
        # Try to consume
        if data["tokens"] >= tokens:
            data["tokens"] -= tokens
            self.redis.set_value(self.key, data, expires_in_sec=3600)
            return True, data["tokens"]
        
        self.redis.set_value(self.key, data, expires_in_sec=3600)
        return False, data["tokens"]


@frappe.whitelist()
def burst_allowed_endpoint():
    """Allows bursts up to 20, refills at 2/second."""
    bucket = TokenBucket(
        key=frappe.session.user,
        capacity=20,
        refill_rate=2
    )
    
    allowed, remaining = bucket.consume(1)
    
    if not allowed:
        frappe.throw("Rate limit exceeded", frappe.RateLimitExceededError)
    
    return {"status": "ok", "tokens_remaining": remaining}
```

## Response Headers

Standard rate limit headers:

```python
def add_rate_limit_headers(limit, remaining, reset_at):
    """Add standard rate limit headers to response."""
    headers = frappe.local.response.headers
    headers["X-RateLimit-Limit"] = str(limit)
    headers["X-RateLimit-Remaining"] = str(max(0, remaining))
    headers["X-RateLimit-Reset"] = str(int(reset_at))
    
    # Draft standard header
    headers["RateLimit-Limit"] = str(limit)
    headers["RateLimit-Remaining"] = str(max(0, remaining))
    headers["RateLimit-Reset"] = str(int(reset_at))
```

## Error Responses

```python
def rate_limit_exceeded_response():
    """Return proper 429 response."""
    frappe.local.response["http_status_code"] = 429
    return {
        "error": "rate_limit_exceeded",
        "message": "Too many requests. Please retry after some time.",
        "retry_after": 60
    }
```

## Monitoring Rate Limits

```python
def log_rate_limit_hit(key, endpoint, allowed):
    """Log rate limit events for monitoring."""
    if not allowed:
        frappe.log_error(
            title="Rate Limit Exceeded",
            message=f"Key: {key}, Endpoint: {endpoint}"
        )

def get_rate_limit_stats():
    """Get rate limiting statistics."""
    redis = frappe.cache()
    # Implementation depends on your monitoring needs
    pass
```

## Best Practices

1. **Set appropriate limits** — Balance protection vs usability
2. **Use different limits for different users** — Premium users get higher limits
3. **Return clear error messages** — Include retry-after time
4. **Add response headers** — Help clients manage their requests
5. **Monitor and alert** — Track rate limit hits
6. **Have a fallback** — Plan for Redis unavailability

Sources: Rate Limiting, API Security (official docs)
```