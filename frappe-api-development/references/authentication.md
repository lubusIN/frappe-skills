```markdown
# Authentication Reference

## Overview
Frappe provides multiple authentication methods for REST and RPC APIs.

## Authentication Methods

### 1. Session-Based (Cookie)
Default for logged-in Desk users.

```javascript
// Automatic via browser cookies after login
frappe.call({
    method: "my_app.api.get_data"
});
```

### 2. Token-Based (API Key + Secret)
Recommended for integrations and external systems.

#### Setup
1. Create a User for API access
2. Go to User → API Access
3. Generate API Key and API Secret

#### Usage (Header)
```bash
# Token format
Authorization: token <api_key>:<api_secret>

# Example
curl -X GET "https://example.com/api/resource/Customer" \
  -H "Authorization: token a1b2c3d4e5f6:xyz789abc123"
```

#### Usage (Basic Auth)
```bash
# Base64 encode api_key:api_secret
Authorization: Basic <base64(api_key:api_secret)>

# Example
curl -X GET "https://example.com/api/resource/Customer" \
  -H "Authorization: Basic YTFiMmMzZDRlNWY2Onh5ejc4OWFiYzEyMw=="
```

### 3. OAuth 2.0
For third-party integrations with authorization flows.

#### Setup OAuth Client
1. Go to OAuth Client → New
2. Set App Name, Redirect URIs
3. Choose Grant Type (Authorization Code, Client Credentials)

#### Authorization Code Flow
```python
# Step 1: Redirect user to authorize
auth_url = f"{frappe_url}/api/method/frappe.integrations.oauth2.authorize"
params = {
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "response_type": "code",
    "scope": "all"
}

# Step 2: Exchange code for token
token_url = f"{frappe_url}/api/method/frappe.integrations.oauth2.get_token"
response = requests.post(token_url, data={
    "grant_type": "authorization_code",
    "code": auth_code,
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI
})
token = response.json()["access_token"]
```

#### Client Credentials Flow
```python
response = requests.post(
    f"{frappe_url}/api/method/frappe.integrations.oauth2.get_token",
    data={
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
)
token = response.json()["access_token"]
```

#### Using Bearer Token
```bash
Authorization: Bearer <access_token>

curl -X GET "https://example.com/api/resource/Customer" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 4. Password-Based (Login)
For user login flows.

```python
# Login endpoint
response = requests.post(
    f"{frappe_url}/api/method/login",
    data={
        "usr": "user@example.com",
        "pwd": "password"
    }
)

# Session cookie returned
session_cookie = response.cookies.get("sid")

# Use cookie for subsequent requests
requests.get(
    f"{frappe_url}/api/resource/Customer",
    cookies={"sid": session_cookie}
)
```

## Implementing Auth in Custom Endpoints

### Public Endpoints (No Auth)
```python
@frappe.whitelist(allow_guest=True)
def public_endpoint():
    """No authentication required."""
    return {"message": "Hello, World!"}
```

### Authenticated Endpoints (Default)
```python
@frappe.whitelist()
def authenticated_endpoint():
    """Requires valid authentication."""
    user = frappe.session.user
    return {"user": user}
```

### Role-Based Access
```python
@frappe.whitelist()
def admin_only():
    """Restrict to specific roles."""
    if "System Manager" not in frappe.get_roles():
        frappe.throw(_("Access denied"), frappe.PermissionError)
    
    return {"status": "admin access granted"}
```

## Creating API Keys Programmatically

```python
def create_api_user(email, full_name, roles=None):
    """Create a user with API access."""
    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": full_name,
        "send_welcome_email": 0,
        "roles": [{"role": r} for r in (roles or ["API User"])]
    })
    user.insert(ignore_permissions=True)
    
    # Generate API credentials
    api_key = frappe.generate_hash(length=15)
    api_secret = frappe.generate_hash(length=15)
    
    user.api_key = api_key
    user.api_secret = api_secret
    user.save(ignore_permissions=True)
    
    return {
        "api_key": api_key,
        "api_secret": api_secret
    }
```

## Validating Tokens

```python
def validate_api_token(api_key, api_secret):
    """Validate API credentials."""
    user = frappe.db.get_value(
        "User",
        {"api_key": api_key, "enabled": 1},
        ["name", "api_secret"],
        as_dict=True
    )
    
    if not user:
        return None
    
    # Compare secret (stored encrypted)
    if frappe.safe_decode(user.api_secret) == api_secret:
        return user.name
    
    return None
```

## Security Best Practices

### Token Security
1. **Never log API secrets** — Mask in logs
2. **Use HTTPS only** — Never send tokens over HTTP
3. **Rotate keys regularly** — Implement key rotation
4. **Limit scope** — Create role-specific API users

### Rate Limiting
```python
from frappe.rate_limiter import rate_limit

@frappe.whitelist(allow_guest=True)
@rate_limit(limit=100, seconds=60)  # 100 requests per minute
def rate_limited_endpoint():
    return {"status": "ok"}
```

### IP Whitelisting
```python
@frappe.whitelist()
def ip_restricted():
    allowed_ips = ["192.168.1.0/24", "10.0.0.1"]
    client_ip = frappe.local.request_ip
    
    if not is_ip_allowed(client_ip, allowed_ips):
        frappe.throw(_("IP not allowed"), frappe.PermissionError)
    
    return {"status": "ok"}
```

## Debugging Auth Issues

### Check Current User
```python
# In console or endpoint
print(frappe.session.user)  # Current authenticated user
print(frappe.get_roles())    # Current user's roles
```

### Verify Token
```bash
# Test token validity
curl -X GET "https://example.com/api/method/frappe.auth.get_logged_user" \
  -H "Authorization: token api_key:api_secret"
```

### Common Issues
| Issue | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid/expired token | Regenerate API credentials |
| 403 Forbidden | Missing permissions | Check role assignments |
| CSRF error | Missing CSRF token | Use proper auth headers |
| Session expired | Cookie timeout | Re-authenticate |

Sources: REST API Authentication, Token Based Auth, OAuth 2.0 (official docs)
```