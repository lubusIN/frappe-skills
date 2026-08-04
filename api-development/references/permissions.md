```markdown
# API Permissions Reference

## Overview
API permissions in Frappe involve multiple layers: authentication, DocType permissions, document-level permissions, and custom authorization logic.

## Permission Hierarchy

```
┌─────────────────────────────────────┐
│ 1. Authentication                    │  ← Is the request authenticated?
├─────────────────────────────────────┤
│ 2. Role Permissions                  │  ← Does user's role allow this action?
├─────────────────────────────────────┤
│ 3. User Permissions                  │  ← Can user access this specific record?
├─────────────────────────────────────┤
│ 4. Document Permissions (has_perm)   │  ← Custom permission logic on document
├─────────────────────────────────────┤
│ 5. Share Permissions                 │  ← Is document shared with user?
└─────────────────────────────────────┘
```

## REST API Permissions

### Automatic Permission Checks
REST endpoints automatically enforce permissions:

```bash
# GET /api/resource/Customer/CUST-001
# → Checks: read permission on Customer DocType
# → Checks: User Permission filters

# POST /api/resource/Customer
# → Checks: create permission on Customer DocType

# PUT /api/resource/Customer/CUST-001
# → Checks: write permission on Customer DocType
# → Checks: document-level permission

# DELETE /api/resource/Customer/CUST-001
# → Checks: delete permission on Customer DocType
```

### List Permissions
```bash
# GET /api/resource/Customer?filters=[["status","=","Active"]]
# → Returns only documents user has permission to read
# → Applies User Permission filters automatically
```

## RPC Method Permissions

### Always Check Permissions!
```python
@frappe.whitelist()
def update_order_status(order_name, new_status):
    """
    CRITICAL: Whitelisted methods bypass automatic permission checks.
    You MUST check permissions explicitly.
    """
    # Step 1: Get the document
    doc = frappe.get_doc("Sales Order", order_name)
    
    # Step 2: Check document permission
    if not frappe.has_permission("Sales Order", "write", doc):
        frappe.throw(_("Permission denied"), frappe.PermissionError)
    
    # Step 3: Check role for specific action (optional)
    if new_status == "Approved" and "Approver" not in frappe.get_roles():
        frappe.throw(_("Only Approvers can approve orders"), frappe.PermissionError)
    
    # Step 4: Proceed with business logic
    doc.status = new_status
    doc.save()
    
    return doc.name
```

### Permission Check Patterns

```python
# Basic permission check
def check_basic():
    if not frappe.has_permission("DocType", "read"):
        frappe.throw(_("Permission denied"), frappe.PermissionError)

# Document-level permission
def check_document(doc):
    if not frappe.has_permission(doc.doctype, "write", doc):
        frappe.throw(_("Cannot modify this document"), frappe.PermissionError)

# Role-based check
def check_role(required_role):
    if required_role not in frappe.get_roles():
        frappe.throw(_(f"{required_role} role required"), frappe.PermissionError)

# Multiple roles (any)
def check_any_role(roles):
    user_roles = set(frappe.get_roles())
    if not user_roles.intersection(set(roles)):
        frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

# Multiple roles (all)
def check_all_roles(roles):
    user_roles = set(frappe.get_roles())
    if not set(roles).issubset(user_roles):
        frappe.throw(_("Missing required roles"), frappe.PermissionError)
```

## Custom Permission Logic

### permission_query_conditions Hook
Filter list queries with custom SQL:

```python
# hooks.py
permission_query_conditions = {
    "Sales Order": "my_app.permissions.get_order_conditions"
}
```

```python
# my_app/permissions.py
def get_order_conditions(user):
    """Return SQL condition to filter Sales Orders."""
    if not user:
        user = frappe.session.user
    
    # Admin sees all
    if "System Manager" in frappe.get_roles(user):
        return ""
    
    # Sales users see their territory only
    if "Sales User" in frappe.get_roles(user):
        territory = frappe.db.get_value("User", user, "territory")
        if territory:
            return f"`tabSales Order`.territory = {frappe.db.escape(territory)}"
    
    # Default: deny access
    return "1=0"
```

### has_permission Hook
Custom document-level permission:

```python
# hooks.py
has_permission = {
    "Sales Order": "my_app.permissions.has_order_permission"
}
```

```python
# my_app/permissions.py
def has_order_permission(doc, ptype, user):
    """
    doc: The document to check
    ptype: Permission type (read, write, create, delete, submit, cancel)
    user: User to check (default: current user)
    """
    if not user:
        user = frappe.session.user
    
    # Admin can do anything
    if "System Manager" in frappe.get_roles(user):
        return True
    
    # Read: Allow if assigned or in same territory
    if ptype == "read":
        if doc.assigned_to == user:
            return True
        user_territory = frappe.db.get_value("User", user, "territory")
        return doc.territory == user_territory
    
    # Write: Only assigned user
    if ptype == "write":
        return doc.assigned_to == user
    
    # Submit/Cancel: Only managers
    if ptype in ("submit", "cancel"):
        return "Sales Manager" in frappe.get_roles(user)
    
    return False
```

## API Permission Decorator

```python
from functools import wraps

def require_permission(doctype, ptype):
    """Decorator to check DocType permission."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not frappe.has_permission(doctype, ptype):
                frappe.throw(
                    _("Permission denied: {0} {1}").format(ptype, doctype),
                    frappe.PermissionError
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(*roles):
    """Decorator to check user roles."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_roles = set(frappe.get_roles())
            if not user_roles.intersection(set(roles)):
                frappe.throw(
                    _("Requires role: {0}").format(", ".join(roles)),
                    frappe.PermissionError
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Usage
@frappe.whitelist()
@require_permission("Sales Order", "write")
@require_role("Sales User", "Sales Manager")
def process_order(order_name):
    # Already verified permissions
    pass
```

## Debugging Permissions

### Check Current State
```python
# Current user
print(frappe.session.user)

# User's roles
print(frappe.get_roles())

# User permissions
from frappe.permissions import get_user_permissions
print(get_user_permissions("user@example.com"))

# Check specific permission
print(frappe.has_permission("Sales Order", "write"))
print(frappe.has_permission("Sales Order", "write", doc))
```

### Permission Debug Mode
```python
# In code
from frappe.permissions import has_permission
result = has_permission(
    "Sales Order",
    ptype="write",
    doc=doc,
    user="user@example.com",
    debug=True  # Prints detailed permission checks
)
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| 403 on REST API | Missing DocType permission | Check Role Permission Manager |
| Can't see some records | User Permission filtering | Check User Permissions for user |
| RPC returns data it shouldn't | Missing permission check | Add explicit `has_permission` check |
| Custom logic not applying | Hook not registered | Verify `hooks.py` registration |

## Security Best Practices

### 1. Never Trust Client Data
```python
@frappe.whitelist()
def bad_example(docname, new_owner):
    # ❌ DANGEROUS: No permission check
    frappe.db.set_value("Document", docname, "owner", new_owner)

@frappe.whitelist()
def good_example(docname, new_owner):
    # ✅ SAFE: Check permissions first
    doc = frappe.get_doc("Document", docname)
    if not frappe.has_permission(doc.doctype, "write", doc):
        frappe.throw(_("Permission denied"), frappe.PermissionError)
    if "Admin" not in frappe.get_roles():
        frappe.throw(_("Only Admin can change owner"), frappe.PermissionError)
    doc.owner = new_owner
    doc.save()
```

### 2. Use Permission-Aware APIs
```python
# ❌ Bypasses permissions
all_orders = frappe.get_all("Sales Order")
frappe.db.sql("SELECT * FROM `tabSales Order`")

# ✅ Respects permissions
permitted_orders = frappe.get_list("Sales Order")
```

### 3. Validate References
```python
@frappe.whitelist()
def update_customer_order(order_name, customer):
    doc = frappe.get_doc("Sales Order", order_name)
    
    # Check permission on order
    if not frappe.has_permission("Sales Order", "write", doc):
        frappe.throw(_("Permission denied"), frappe.PermissionError)
    
    # Also check permission on referenced customer
    if not frappe.has_permission("Customer", "read", customer):
        frappe.throw(_("Cannot access customer"), frappe.PermissionError)
    
    doc.customer = customer
    doc.save()
```

Sources: Permissions, Role Permissions, User Permissions, Permission Hooks (official docs)
```