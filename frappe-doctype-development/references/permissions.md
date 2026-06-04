```markdown
# Permissions Reference

## Overview
Frappe uses a multi-layered permission system: Role permissions (DocType level), User Permissions (row level), and Share permissions (document level).

## Permission Levels

### 1. Role Permissions
Define what actions a role can perform on a DocType.

| Permission | Description |
|------------|-------------|
| Read | View documents |
| Write | Modify documents |
| Create | Create new documents |
| Delete | Delete documents |
| Submit | Submit documents (submittable) |
| Cancel | Cancel documents (submittable) |
| Amend | Amend cancelled documents |
| Report | Access reports |
| Import | Import data |
| Export | Export data |
| Print | Print documents |
| Email | Send emails |
| Share | Share with other users |

### 2. User Permissions
Filter which documents a user can access based on Link field values.

```python
# User can only see Sales Orders where customer = "ACME Corp"
frappe.permissions.add_user_permission(
    doctype="Customer",
    name="ACME Corp",
    user="sales@example.com"
)
```

### 3. Share Permissions
Grant access to specific documents.

```python
frappe.share.add(
    doctype="Project",
    name="PROJ-001",
    user="contractor@example.com",
    read=1,
    write=1
)
```

## Setting Role Permissions

### In DocType JSON
```json
{
  "permissions": [
    {
      "role": "Sales User",
      "read": 1,
      "write": 1,
      "create": 1
    },
    {
      "role": "Sales Manager",
      "read": 1,
      "write": 1,
      "create": 1,
      "delete": 1,
      "submit": 1,
      "cancel": 1
    },
    {
      "role": "Guest",
      "read": 1,
      "permlevel": 0
    }
  ]
}
```

### Via Role Permission Manager
1. Go to Setup > Role Permission Manager
2. Select DocType
3. Configure permissions per role

## Permission Levels (permlevel)

Split fields into permission groups:

```json
{
  "fieldname": "internal_notes",
  "fieldtype": "Text",
  "permlevel": 1
}
```

```json
{
  "permissions": [
    {
      "role": "Sales User",
      "read": 1,
      "write": 1,
      "permlevel": 0
    },
    {
      "role": "Sales Manager",
      "read": 1,
      "write": 1,
      "permlevel": 1
    }
  ]
}
```

- **permlevel 0**: Default, accessible by base role
- **permlevel 1+**: Restricted to higher roles

## Checking Permissions in Code

### Basic Checks
```python
# Check DocType permission
if frappe.has_permission("Sales Order", "read"):
    # User can read Sales Orders

# Check document permission
doc = frappe.get_doc("Sales Order", "SO-001")
if frappe.has_permission("Sales Order", "write", doc):
    # User can write to this specific document

# Check with user parameter
if frappe.has_permission("Sales Order", "read", user="other@example.com"):
    # That user can read
```

### Permission Queries
```python
# Get all documents user can read
orders = frappe.get_list("Sales Order")  # Applies permissions

# Bypass permissions (use carefully!)
all_orders = frappe.get_all("Sales Order")  # Ignores permissions

# Check role
if "Sales Manager" in frappe.get_roles():
    # User has Sales Manager role

# Check specific permission
if frappe.has_permission("Sales Order", "submit"):
    # User can submit Sales Orders
```

### In RPC Methods (Critical!)
```python
@frappe.whitelist()
def approve_order(order_name):
    # ALWAYS check permissions in whitelisted methods!
    doc = frappe.get_doc("Sales Order", order_name)
    
    if not frappe.has_permission("Sales Order", "write", doc):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    # Also check role for specific actions
    if "Sales Manager" not in frappe.get_roles():
        frappe.throw(_("Only Sales Managers can approve"))
    
    doc.status = "Approved"
    doc.save()
    return doc.name
```

## User Permissions (Row-Level Security)

### Setting User Permissions
```python
# Via code
frappe.permissions.add_user_permission(
    doctype="Company",
    name="My Company",
    user="employee@example.com",
    ignore_permissions=True
)

# Multiple values
frappe.permissions.add_user_permission("Company", "Company A", "user@example.com")
frappe.permissions.add_user_permission("Company", "Company B", "user@example.com")
```

### User Permission Behavior
```python
# User Permissions filter applied automatically
# If user has User Permission for Company = "ACME"
# Then frappe.get_list("Sales Order") only returns orders where company = "ACME"

# Check if strict user permissions apply
from frappe.permissions import get_user_permissions
user_perms = get_user_permissions("user@example.com")
```

### Apply User Permissions to Specific Links
```json
{
  "fieldname": "company",
  "fieldtype": "Link",
  "options": "Company",
  "ignore_user_permissions": 0
}
```

Set `ignore_user_permissions: 1` to bypass filtering for specific Link fields.

## Permission Queries Optimization

### Efficient Permission Checks
```python
# Bad: Check permission for each document
for name in document_names:
    if frappe.has_permission("Order", "read", name):
        process(name)

# Good: Use get_list which applies permissions
permitted_docs = frappe.get_list("Order", filters={"name": ("in", document_names)})
for doc in permitted_docs:
    process(doc.name)
```

### has_permission vs get_list
```python
# has_permission: Single document check
can_read = frappe.has_permission("Order", "read", "ORD-001")

# get_list: Filtered by permissions automatically
orders = frappe.get_list("Order", filters={"status": "Open"})
```

## Custom Permission Logic

### permission_query_conditions
Filter list queries with custom SQL:

```python
# hooks.py
permission_query_conditions = {
    "Sales Order": "my_app.permissions.sales_order_query"
}
```

```python
# my_app/permissions.py
def sales_order_query(user):
    if "Sales Manager" in frappe.get_roles(user):
        return ""  # No restriction
    
    # Restrict to user's territory
    territory = frappe.db.get_value("User", user, "territory")
    if territory:
        return f"`tabSales Order`.territory = {frappe.db.escape(territory)}"
    
    return "1=0"  # No access
```

### has_permission Hook
Custom permission checks:

```python
# hooks.py
has_permission = {
    "Sales Order": "my_app.permissions.sales_order_permission"
}
```

```python
# my_app/permissions.py
def sales_order_permission(doc, ptype, user):
    if ptype == "read":
        return True  # Allow read for all
    
    if ptype == "write":
        # Only allow write if assigned
        return doc.assigned_to == user
    
    return False
```

## Document Sharing

### Share a Document
```python
frappe.share.add(
    doctype="Project",
    name="PROJ-001",
    user="external@example.com",
    read=1,
    write=0,
    share=0
)

# With notify
frappe.share.add("Project", "PROJ-001", "user@example.com", 
    read=1, write=1, notify=1)
```

### Check Shares
```python
# Get share info
shares = frappe.share.get_users("Project", "PROJ-001")

# Check if shared with user
is_shared = frappe.share.get_shared("Project", "PROJ-001", "user@example.com")
```

### Remove Share
```python
frappe.share.remove("Project", "PROJ-001", "user@example.com")
```

## Best Practices

### Always Check Permissions
```python
@frappe.whitelist()
def my_api_method(docname):
    # Rule 1: Always check permissions in whitelisted methods
    doc = frappe.get_doc("My DocType", docname)
    if not frappe.has_permission("My DocType", "write", doc):
        frappe.throw(_("Permission denied"), frappe.PermissionError)
    
    # Rule 2: Check role for sensitive operations
    if "Manager" not in frappe.get_roles():
        frappe.throw(_("Requires Manager role"))
```

### Use Permission-Aware APIs
```python
# Use get_list (permission-aware) instead of get_all
docs = frappe.get_list("Order")  # ✅ Respects permissions
docs = frappe.get_all("Order")   # ❌ Bypasses permissions
```

### Test Permissions
```python
def test_sales_user_cannot_delete(self):
    frappe.set_user("sales@example.com")
    self.assertRaises(
        frappe.PermissionError,
        frappe.delete_doc, "Sales Order", self.order.name
    )
    frappe.set_user("Administrator")
```

Sources: Permissions, Role Permission, User Permissions, Sharing (official docs)
```