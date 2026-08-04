```markdown
# OAuth 2.0 Integration Reference

## Overview
Frappe supports OAuth 2.0 for secure third-party integrations. You can act as both an OAuth Provider (let others authenticate with your Frappe site) and OAuth Consumer (authenticate with external OAuth providers).

## Frappe as OAuth Provider

### Setting Up OAuth Server

1. **Enable OAuth**
   - Go to OAuth Provider Settings
   - Enable "OAuth Provider"

2. **Create OAuth Client**
   - Navigate to OAuth Client → New
   - Fill in details:
     - App Name: Your application name
     - Redirect URIs: Callback URLs (one per line)
     - Default Redirect URI: Primary callback
     - Grant Type: Authorization Code (recommended)
     - Scopes: all, openid, etc.

### Authorization Code Flow (Recommended)

```python
# Client application code

# Step 1: Redirect user to authorization
import urllib.parse

auth_params = {
    "client_id": "your-client-id",
    "redirect_uri": "https://yourapp.com/callback",
    "response_type": "code",
    "scope": "all openid",
    "state": "random-state-string"  # CSRF protection
}

auth_url = f"https://frappe-site.com/api/method/frappe.integrations.oauth2.authorize?{urllib.parse.urlencode(auth_params)}"
# Redirect user to auth_url
```

```python
# Step 2: Handle callback and exchange code for token
def handle_oauth_callback(code, state):
    # Verify state matches what you sent
    if state != session["oauth_state"]:
        raise SecurityError("State mismatch")
    
    # Exchange code for access token
    response = requests.post(
        "https://frappe-site.com/api/method/frappe.integrations.oauth2.get_token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI
        }
    )
    
    token_data = response.json()
    access_token = token_data["access_token"]
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data["expires_in"]
    
    return access_token
```

```python
# Step 3: Use access token
response = requests.get(
    "https://frappe-site.com/api/resource/Customer",
    headers={"Authorization": f"Bearer {access_token}"}
)
```

### Client Credentials Flow
For server-to-server communication without user interaction.

```python
def get_client_credentials_token():
    response = requests.post(
        "https://frappe-site.com/api/method/frappe.integrations.oauth2.get_token",
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": "all"
        }
    )
    return response.json()["access_token"]
```

### Refresh Token Flow
```python
def refresh_access_token(refresh_token):
    response = requests.post(
        "https://frappe-site.com/api/method/frappe.integrations.oauth2.get_token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID
        }
    )
    return response.json()
```

### Introspect Token
Verify if a token is valid:

```python
def introspect_token(token):
    response = requests.post(
        "https://frappe-site.com/api/method/frappe.integrations.oauth2.introspect_token",
        data={"token": token},
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    return response.json()
    # Returns: {"active": true, "user": "user@example.com", ...}
```

### Revoke Token
```python
def revoke_token(token):
    response = requests.post(
        "https://frappe-site.com/api/method/frappe.integrations.oauth2.revoke_token",
        data={
            "token": token,
            "client_id": CLIENT_ID
        }
    )
```

## Frappe as OAuth Consumer

### Social Login Configuration

1. **Google Login**
   ```python
   # In Social Login Key DocType
   {
       "provider": "Google",
       "client_id": "your-google-client-id.apps.googleusercontent.com",
       "client_secret": "your-google-client-secret",
       "enable_social_login": 1
   }
   ```

2. **GitHub Login**
   ```python
   {
       "provider": "GitHub",
       "client_id": "github-client-id",
       "client_secret": "github-client-secret",
       "enable_social_login": 1
   }
   ```

### Custom OAuth Provider Integration

```python
# my_app/oauth_providers/custom_provider.py
import frappe
from frappe.integrations.oauth2_logins import decoder_compat

@frappe.whitelist(allow_guest=True)
def login_via_custom(code, state=None):
    """Handle OAuth callback from custom provider."""
    from frappe.utils.oauth import login_via_oauth2
    
    info = get_info_via_oauth(code)
    
    login_via_oauth2(
        provider="custom",
        email_id=info["email"],
        user_id=info["sub"],
        data=info
    )
    
    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = frappe.local.response.get("redirect_to", "/app")

def get_info_via_oauth(code):
    """Exchange code for user info."""
    settings = frappe.get_cached_doc("Social Login Key", "Custom Provider")
    
    # Get access token
    token_response = requests.post(
        "https://custom-provider.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": settings.client_id,
            "client_secret": settings.get_password("client_secret"),
            "redirect_uri": get_redirect_uri()
        }
    )
    token = token_response.json()["access_token"]
    
    # Get user info
    user_response = requests.get(
        "https://custom-provider.com/userinfo",
        headers={"Authorization": f"Bearer {token}"}
    )
    return user_response.json()

def get_redirect_uri():
    return f"{frappe.utils.get_url()}/api/method/my_app.oauth_providers.custom_provider.login_via_custom"
```

## OpenID Connect (OIDC)

### Enabling OIDC
Frappe supports OpenID Connect for identity federation.

```python
# Request with openid scope
auth_params = {
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "response_type": "code",
    "scope": "openid email profile",  # OIDC scopes
    "state": generate_state()
}
```

### ID Token
The token response includes an ID token with user claims:

```python
token_data = {
    "access_token": "...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "...",
    "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# Decode ID token (JWT)
import jwt
id_token_payload = jwt.decode(
    token_data["id_token"],
    options={"verify_signature": False}  # Verify in production!
)
# Contains: sub, email, name, etc.
```

## Security Best Practices

### State Parameter (CSRF Protection)
```python
import secrets

def generate_state():
    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state
    return state

def verify_state(received_state):
    expected_state = session.pop("oauth_state", None)
    if not expected_state or received_state != expected_state:
        raise SecurityError("Invalid state parameter")
```

### PKCE (Proof Key for Code Exchange)
For public clients (mobile apps, SPAs):

```python
import hashlib
import base64

def generate_pkce():
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip("=")
    
    return code_verifier, code_challenge

# In authorization request
auth_params["code_challenge"] = code_challenge
auth_params["code_challenge_method"] = "S256"

# In token request
token_params["code_verifier"] = code_verifier
```

### Token Storage
```python
# Server-side: Store in database
frappe.db.set_value("OAuth Token Store", user, {
    "access_token": encrypt(access_token),
    "refresh_token": encrypt(refresh_token),
    "expires_at": datetime.now() + timedelta(seconds=expires_in)
})

# Never store tokens in:
# - Browser localStorage (XSS vulnerable)
# - URL parameters (leaked in logs)
# - Unencrypted cookies
```

## Error Handling

```python
def handle_oauth_error(error, error_description=None):
    """Handle OAuth error responses."""
    errors = {
        "invalid_request": "The request is missing a required parameter",
        "unauthorized_client": "Client is not authorized for this grant type",
        "access_denied": "User denied the authorization request",
        "invalid_scope": "The requested scope is invalid or unknown",
        "server_error": "The server encountered an error",
        "temporarily_unavailable": "Server is temporarily unavailable"
    }
    
    message = errors.get(error, error_description or "Unknown error")
    frappe.throw(message, frappe.AuthenticationError)
```

Sources: OAuth 2.0, OpenID Connect, Social Login (official docs)
```