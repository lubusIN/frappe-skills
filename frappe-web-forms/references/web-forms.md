# Web Forms

## Overview
Web Forms provide an easy way to generate forms for your website with minimal configuration. Forms can be public (anyone can fill them) or require login.

## Creating a Web Form
1. Type "new web form" in awesomebar
2. Enter Title
3. Select DocType for which the record should be created
4. Add introduction (optional)
5. Click "Get Fields" to get all fields from selected DocType, or select fields manually
6. Publish it

## Standard Web Forms
If you check "Is Standard", a new folder is created in the module with:
- `.py` file for server-side customization
- `.js` file for client-side customization

These files are bundled with your app and version controlled. The "Is Standard" field is only visible in developer mode.

## Web Form Settings
- **Login Required**: Require users to log in before filling the form
- **Allow Edit**: Let users edit their submitted entries
- **Allow Multiple**: Let users submit multiple entries
- **Show as Card**: Display as a card layout
- **Max Attachment Size**: Limit file upload sizes

## Customization

### Python Customization
```python
# my_web_form.py
import frappe

def get_context(context):
    # Add custom context variables
    context.custom_var = "value"

def validate(doc):
    # Custom validation before save
    if not doc.email:
        frappe.throw("Email is required")
```

### JavaScript Customization
```javascript
// my_web_form.js
frappe.ready(function() {
    // Custom client-side behavior
    frappe.web_form.on('field_change', function(field, value) {
        // Handle field changes
    });
});
```

## Web Form Permissions
- Use portal roles to control access
- Set explicit user permissions for specific entries

## Use Cases
- Customer-facing forms for data collection
- Support/ticket submission without Desk access
- Public registration or feedback forms
- Self-service portals

Sources: Web Form, Web Form Settings, Web Form Customization (official docs)
