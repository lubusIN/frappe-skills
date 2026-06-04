```markdown
# Advanced Permissions Reference

## Overview
Complex permission patterns for enterprise Frappe applications.

## Role-Based Access Control (RBAC)

### Custom Permission Controller
```python
# permissions.py
import frappe

def get_permission_query_conditions(user):
    """Return SQL conditions for permission filtering"""
    if not user:
        user = frappe.session.user
    
    if "System Manager" in frappe.get_roles(user):
        return ""  # No restrictions
    
    # User can see their own records or records in their territory
    return f"""
        (`tabSales Order`.owner = '{user}'
        OR `tabSales Order`.territory IN (
            SELECT territory FROM `tabUser Permission`
            WHERE user = '{user}' AND allow = 'Territory'
        ))
    """

def has_permission(doc, ptype, user):
    """Custom permission check for documents"""
    if not user:
        user = frappe.session.user
    
    if ptype == "read":
        return check_read_permission(doc, user)
    elif ptype == "write":
        return check_write_permission(doc, user)
    elif ptype == "submit":
        return check_submit_permission(doc, user)
    elif ptype == "cancel":
        return check_cancel_permission(doc, user)
    
    return True

def check_read_permission(doc, user):
    """Check if user can read this document"""
    roles = frappe.get_roles(user)
    
    # Managers see everything
    if "Sales Manager" in roles:
        return True
    
    # Users see own records
    if doc.owner == user:
        return True
    
    # Territory-based access
    user_territories = get_user_territories(user)
    if doc.territory in user_territories:
        return True
    
    return False
```

## User Permission Patterns

### Dynamic User Permissions
```python
def set_dynamic_user_permissions(user):
    """Set user permissions based on user profile"""
    # Clear existing dynamic permissions
    frappe.db.delete("User Permission", {
        "user": user,
        "is_default": 0
    })
    
    employee = frappe.db.get_value("Employee", {"user_id": user})
    if not employee:
        return
    
    employee_doc = frappe.get_doc("Employee", employee)
    
    # Permit user's company
    if employee_doc.company:
        add_user_permission(user, "Company", employee_doc.company)
    
    # Permit user's department
    if employee_doc.department:
        add_user_permission(user, "Department", employee_doc.department)
    
    # Permit user's cost center
    if employee_doc.payroll_cost_center:
        add_user_permission(user, "Cost Center", employee_doc.payroll_cost_center)

def add_user_permission(user, doctype, value):
    frappe.get_doc({
        "doctype": "User Permission",
        "user": user,
        "allow": doctype,
        "for_value": value,
        "is_default": 0
    }).insert(ignore_permissions=True)
```

## Row-Level Security

### Document-Level Restrictions
```python
class Project(Document):
    def has_permission(self, ptype="read", user=None):
        """Row-level security for projects"""
        if not user:
            user = frappe.session.user
        
        # Skip check for admins
        if user == "Administrator":
            return True
        
        # Project members have access
        is_member = frappe.db.exists("Project Member", {
            "parent": self.name,
            "user": user
        })
        
        if is_member:
            return True
        
        # Project owner has full access
        if self.owner == user:
            return True
        
        # Managers of project department have access
        if self.department:
            if is_department_manager(user, self.department):
                return True
        
        return False
```

### Permission Query for Lists
```python
# In hooks.py
permission_query_conditions = {
    "Project": "my_app.permissions.project_query_conditions"
}

# In permissions.py
def project_query_conditions(user):
    """SQL WHERE clause for Project list"""
    if not user:
        user = frappe.session.user
    
    if "Projects Manager" in frappe.get_roles(user):
        return ""
    
    # Build complex condition
    conditions = []
    
    # Own projects
    conditions.append(f"owner = '{user}'")
    
    # Projects where user is member
    conditions.append(f"""
        name IN (
            SELECT parent FROM `tabProject Member`
            WHERE user = '{user}'
        )
    """)
    
    # Projects in user's department
    employee = frappe.db.get_value("Employee", {"user_id": user}, "department")
    if employee:
        conditions.append(f"department = '{frappe.db.escape(employee)}'")
    
    return "(" + " OR ".join(conditions) + ")"
```

## Field-Level Permissions

### Conditional Field Access
```python
def set_field_permissions(doc, method):
    """Set field permissions based on user role"""
    user = frappe.session.user
    roles = frappe.get_roles(user)
    
    # Sensitive fields hidden for regular users
    if "Finance Manager" not in roles:
        doc.remove_field_from_interface("cost_price")
        doc.remove_field_from_interface("margin_percent")
    
    # Make fields read-only for certain roles
    if "Sales User" in roles and "Sales Manager" not in roles:
        for field in ["discount_percent", "additional_discount"]:
            setattr(doc, f"{field}_read_only", True)
```

### Permission Level Pattern
```python
def apply_permlevel_restrictions(doctype):
    """Configure permission levels for DocType fields"""
    meta = frappe.get_meta(doctype)
    
    # Define sensitive fields
    sensitive_fields = {
        "cost_price": 1,      # Level 1 - Manager only
        "profit_margin": 1,
        "internal_notes": 2,   # Level 2 - Admin only
        "approval_code": 2
    }
    
    for fieldname, permlevel in sensitive_fields.items():
        field = meta.get_field(fieldname)
        if field:
            frappe.db.set_value("DocField", {
                "parent": doctype,
                "fieldname": fieldname
            }, "permlevel", permlevel)
```

## Hierarchical Permissions

### Department Hierarchy Access
```python
def get_accessible_departments(user):
    """Get departments user can access based on hierarchy"""
    employee = frappe.db.get_value("Employee", {"user_id": user}, "department")
    if not employee:
        return []
    
    # Get all child departments
    return frappe.db.sql_list("""
        SELECT name FROM `tabDepartment`
        WHERE lft >= (SELECT lft FROM `tabDepartment` WHERE name = %(dept)s)
        AND rgt <= (SELECT rgt FROM `tabDepartment` WHERE name = %(dept)s)
    """, {"dept": employee})

def is_manager_of_user(manager_user, target_user):
    """Check if manager_user manages target_user"""
    target_employee = frappe.db.get_value("Employee", 
        {"user_id": target_user}, "name")
    
    # Check reports_to chain
    current = target_employee
    max_depth = 10  # Prevent infinite loops
    
    for _ in range(max_depth):
        reports_to = frappe.db.get_value("Employee", current, "reports_to")
        if not reports_to:
            return False
        
        reports_to_user = frappe.db.get_value("Employee", reports_to, "user_id")
        if reports_to_user == manager_user:
            return True
        
        current = reports_to
    
    return False
```

## Time-Based Permissions

### Temporal Access Control
```python
def check_time_based_permission(doc, user):
    """Permission based on time/date restrictions"""
    from frappe.utils import now_datetime, getdate
    
    # Check if within edit window
    if doc.freeze_after and getdate() > getdate(doc.freeze_after):
        frappe.throw("This document is frozen and cannot be edited")
    
    # Check business hours
    current_hour = now_datetime().hour
    business_hours = frappe.db.get_single_value("System Settings", "business_hours")
    
    if business_hours:
        start_hour, end_hour = map(int, business_hours.split("-"))
        if not (start_hour <= current_hour < end_hour):
            frappe.throw("Document editing is only allowed during business hours")
```

## Audit Trail

### Permission Audit Logging
```python
def log_permission_check(doctype, docname, user, ptype, result):
    """Log permission checks for audit"""
    if frappe.conf.get("enable_permission_audit"):
        frappe.enqueue(
            create_permission_log,
            doctype=doctype,
            docname=docname,
            user=user,
            permission_type=ptype,
            result="Allowed" if result else "Denied",
            timestamp=frappe.utils.now_datetime()
        )

def create_permission_log(**kwargs):
    frappe.get_doc({
        "doctype": "Permission Log",
        **kwargs
    }).insert(ignore_permissions=True)
```

## Best Practices

1. **Cache permission checks** - Use `frappe.cache()` for frequently checked permissions
2. **Avoid N+1 queries** - Use permission query conditions instead of per-document checks
3. **Test edge cases** - Test with users having multiple roles
4. **Document your permissions** - Keep a permission matrix document
5. **Use has_permission sparingly** - It's called on every read, keep it fast

Sources: Frappe Permission System, ERPNext Permissions
```