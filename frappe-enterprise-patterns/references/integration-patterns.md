```markdown
# Integration Patterns Reference

## Overview
Patterns for integrating Frappe applications with external systems.

## Connector Architecture

### Base Connector Pattern
```python
# base_connector.py
import frappe
from frappe import _
import requests

class BaseConnector:
    """Base class for external integrations"""
    
    def __init__(self, settings=None):
        self.settings = settings or self.get_settings()
        self.session = requests.Session()
        self.setup_session()
    
    def get_settings(self):
        """Override to get connector settings"""
        raise NotImplementedError
    
    def setup_session(self):
        """Configure session with auth, headers, etc."""
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def request(self, method, endpoint, **kwargs):
        """Make authenticated request with error handling"""
        url = f"{self.settings.base_url}/{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else None
        except requests.exceptions.HTTPError as e:
            self.handle_http_error(e, response)
        except requests.exceptions.ConnectionError:
            frappe.throw(_("Connection failed. Check your network."))
        except requests.exceptions.Timeout:
            frappe.throw(_("Request timed out. Please try again."))
    
    def handle_http_error(self, error, response):
        """Handle HTTP errors with appropriate messages"""
        status_code = response.status_code
        
        error_handlers = {
            401: lambda: frappe.throw(_("Authentication failed. Check credentials.")),
            403: lambda: frappe.throw(_("Access denied. Check permissions.")),
            404: lambda: frappe.throw(_("Resource not found.")),
            429: lambda: frappe.throw(_("Rate limited. Please wait.")),
            500: lambda: frappe.throw(_("Server error. Contact support."))
        }
        
        handler = error_handlers.get(status_code)
        if handler:
            handler()
        else:
            frappe.throw(f"Request failed: {response.text}")
```

### OAuth2 Connector
```python
# oauth_connector.py
from datetime import datetime, timedelta

class OAuth2Connector(BaseConnector):
    """Connector with OAuth2 authentication"""
    
    def get_settings(self):
        return frappe.get_single("My Integration Settings")
    
    def setup_session(self):
        super().setup_session()
        self.ensure_valid_token()
    
    def ensure_valid_token(self):
        """Refresh token if expired"""
        if self.token_expired():
            self.refresh_access_token()
        
        self.session.headers["Authorization"] = f"Bearer {self.settings.access_token}"
    
    def token_expired(self):
        if not self.settings.token_expiry:
            return True
        return datetime.now() > self.settings.token_expiry
    
    def refresh_access_token(self):
        """Exchange refresh token for new access token"""
        response = requests.post(
            f"{self.settings.auth_url}/oauth/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.settings.get_password("refresh_token"),
                "client_id": self.settings.client_id,
                "client_secret": self.settings.get_password("client_secret")
            }
        )
        response.raise_for_status()
        data = response.json()
        
        self.settings.access_token = data["access_token"]
        self.settings.token_expiry = datetime.now() + timedelta(seconds=data["expires_in"])
        self.settings.save()
```

## Data Sync Patterns

### Full Sync
```python
def full_sync_customers():
    """Full sync - replace all records"""
    connector = MyConnector()
    
    # Fetch all from external system
    external_customers = connector.get_all_customers()
    
    # Track processed
    synced_ids = []
    
    for ext_customer in external_customers:
        local = sync_customer(ext_customer)
        synced_ids.append(local.name)
    
    # Delete orphaned local records
    frappe.db.sql("""
        DELETE FROM `tabExternal Customer`
        WHERE external_id NOT IN %(ids)s
    """, {"ids": synced_ids})
    
    frappe.db.commit()
```

### Incremental Sync
```python
def incremental_sync_customers():
    """Sync only changed records since last sync"""
    settings = frappe.get_single("Sync Settings")
    last_sync = settings.last_customer_sync or "1970-01-01T00:00:00Z"
    
    connector = MyConnector()
    
    # Fetch changes since last sync
    changes = connector.get_customers(modified_since=last_sync)
    
    for customer in changes["created"]:
        create_local_customer(customer)
    
    for customer in changes["updated"]:
        update_local_customer(customer)
    
    for customer_id in changes["deleted"]:
        delete_local_customer(customer_id)
    
    # Update sync timestamp
    settings.last_customer_sync = frappe.utils.now_datetime()
    settings.save()
```

### Delta Sync with Cursor
```python
def delta_sync_with_cursor():
    """Cursor-based incremental sync"""
    settings = frappe.get_single("Sync Settings")
    cursor = settings.sync_cursor
    
    connector = MyConnector()
    
    while True:
        response = connector.get_changes(cursor=cursor, limit=100)
        
        for item in response["items"]:
            process_sync_item(item)
        
        cursor = response.get("next_cursor")
        settings.sync_cursor = cursor
        settings.save()
        frappe.db.commit()
        
        if not response.get("has_more"):
            break
```

## Webhook Handling

### Webhook Receiver
```python
# api.py
@frappe.whitelist(allow_guest=True)
def webhook_receiver():
    """Handle incoming webhooks"""
    # Verify signature
    signature = frappe.request.headers.get("X-Webhook-Signature")
    if not verify_webhook_signature(signature):
        frappe.throw("Invalid signature", frappe.AuthenticationError)
    
    payload = frappe.request.json
    event_type = payload.get("event")
    
    # Route to handler
    handlers = {
        "customer.created": handle_customer_created,
        "customer.updated": handle_customer_updated,
        "order.placed": handle_order_placed
    }
    
    handler = handlers.get(event_type)
    if handler:
        # Queue for async processing
        frappe.enqueue(
            handler,
            payload=payload,
            queue="default"
        )
    
    return {"status": "received"}

def verify_webhook_signature(signature):
    """Verify webhook HMAC signature"""
    import hmac
    import hashlib
    
    settings = frappe.get_single("Integration Settings")
    secret = settings.get_password("webhook_secret")
    
    expected = hmac.new(
        secret.encode(),
        frappe.request.data,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)
```

### Idempotent Webhook Processing
```python
def handle_webhook_with_idempotency(payload):
    """Process webhook with idempotency key"""
    idempotency_key = payload.get("idempotency_key")
    
    # Check if already processed
    if frappe.db.exists("Webhook Log", {"idempotency_key": idempotency_key}):
        return {"status": "duplicate"}
    
    # Create log entry
    log = frappe.get_doc({
        "doctype": "Webhook Log",
        "idempotency_key": idempotency_key,
        "event_type": payload.get("event"),
        "payload": frappe.as_json(payload),
        "status": "Processing"
    }).insert()
    
    try:
        process_webhook(payload)
        log.status = "Completed"
    except Exception as e:
        log.status = "Failed"
        log.error_message = str(e)
        raise
    finally:
        log.save()
    
    return {"status": "processed"}
```

## Queue Integration

### External Queue Consumer
```python
# queue_consumer.py
import redis
import json

def consume_external_queue():
    """Consume messages from external Redis queue"""
    r = redis.from_url(frappe.conf.get("external_redis_url"))
    
    while True:
        message = r.brpop("integration_queue", timeout=30)
        if message:
            _, data = message
            payload = json.loads(data)
            process_queue_message(payload)

def process_queue_message(payload):
    """Process a queue message"""
    message_type = payload.get("type")
    
    handlers = {
        "sync_customer": sync_customer_from_message,
        "update_inventory": update_inventory_from_message
    }
    
    handler = handlers.get(message_type)
    if handler:
        handler(payload["data"])
```

## Error Handling & Retry

### Retry with Exponential Backoff
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60)
)
def sync_with_retry(data):
    """Sync data with automatic retry"""
    connector = MyConnector()
    return connector.push_data(data)
```

### Integration Error Logging
```python
def log_integration_error(connector_name, operation, error, payload=None):
    """Log integration errors for debugging"""
    frappe.get_doc({
        "doctype": "Integration Error Log",
        "connector": connector_name,
        "operation": operation,
        "error_message": str(error),
        "traceback": frappe.get_traceback(),
        "payload": frappe.as_json(payload) if payload else None,
        "timestamp": frappe.utils.now_datetime()
    }).insert(ignore_permissions=True)
```

## Rate Limiting

### Client-Side Rate Limiting
```python
import time
from collections import deque

class RateLimitedConnector(BaseConnector):
    """Connector with client-side rate limiting"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_times = deque(maxlen=100)
        self.rate_limit = 100  # requests per minute
    
    def request(self, *args, **kwargs):
        self.wait_for_rate_limit()
        self.request_times.append(time.time())
        return super().request(*args, **kwargs)
    
    def wait_for_rate_limit(self):
        """Wait if rate limit would be exceeded"""
        if len(self.request_times) >= self.rate_limit:
            oldest = self.request_times[0]
            elapsed = time.time() - oldest
            if elapsed < 60:
                time.sleep(60 - elapsed)
```

Sources: Frappe API Documentation, Integration Best Practices
```