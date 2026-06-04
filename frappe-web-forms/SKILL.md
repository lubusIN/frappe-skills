---
name: frappe-web-forms
description: Build public-facing web forms for data collection without Desk access. Use when creating customer submission forms, feedback forms, or self-service portals with Frappe Web Forms.
---

# Frappe Web Forms

Build public-facing web forms for data collection, submissions, and customer self-service.

## When to use

- Creating forms for external users (no Desk access)
- Building support/ticket submission forms
- Collecting customer feedback or registrations
- Enabling self-service data entry portals
- Replacing simple portal pages with form-based workflows

## Inputs required

- Target DocType for form submissions
- Which fields to expose on the web form
- Authentication requirements (login required vs guest)
- Whether users can edit/resubmit entries
- File upload requirements

## Procedure

### 0) Prerequisites

Ensure the target DocType exists and has the fields you want to expose.

### 1) Create the Web Form

1. Type "new web form" in the awesomebar
2. Enter a Title (becomes the URL slug)
3. Select the DocType for record creation
4. Add introduction text (optional, shown above the form)
5. Click "Get Fields" to import all fields, or add fields manually
6. Set field order and which are required
7. Publish the form

### 2) Configure settings

| Setting | Purpose |
|---------|---------|
| Login Required | Require authentication before form access |
| Allow Edit | Let users edit their submitted entries |
| Allow Multiple | Let users submit more than one entry |
| Show as Card | Display in card layout style |
| Max Attachment Size | Limit file upload sizes |
| Success URL | Redirect after successful submission |
| Success Message | Custom message after submission |

### 3) Make it a Standard Web Form (app-bundled)

Check "Is Standard" (visible in Developer Mode) to export the form as files:

```
my_app/
└── my_module/
    └── web_form/
        └── contact_us/
            ├── contact_us.json    # Web form metadata
            ├── contact_us.py      # Server-side customization
            └── contact_us.js      # Client-side customization
```

### 4) Add server-side customization

```python
# contact_us.py
import frappe

def get_context(context):
    """Add custom context variables to the web form."""
    context.categories = frappe.get_all("Support Category",
        filters={"enabled": 1},
        fields=["name", "label"],
        order_by="label asc"
    )

def validate(doc):
    """Custom validation before the document is saved."""
    if not doc.email:
        frappe.throw("Email address is required")

    # Prevent duplicate submissions
    existing = frappe.db.exists("Support Ticket", {"email": doc.email, "status": "Open"})
    if existing:
        frappe.throw("You already have an open ticket. Please wait for a response.")
```

### 5) Add client-side customization

```javascript
// contact_us.js
frappe.ready(function() {
    // Handle field changes
    frappe.web_form.on("field_change", function(field, value) {
        if (field === "category" && value === "Urgent") {
            frappe.web_form.set_df_property("description", "reqd", 1);
        }
    });

    // Custom validation
    frappe.web_form.validate = function() {
        let data = frappe.web_form.get_values();
        if (data.phone && !data.phone.match(/^\+?[0-9\-\s]+$/)) {
            frappe.msgprint("Please enter a valid phone number");
            return false;
        }
        return true;
    };

    // Custom after-save behavior
    frappe.web_form.after_save = function() {
        frappe.msgprint("Thank you for your submission!");
    };
});
```

### 6) Control permissions

- **Guest access**: Uncheck "Login Required" for fully public forms
- **Portal roles**: Assign portal roles to control which logged-in users see the form
- **User permissions**: Set explicit document-level permissions on the target DocType
- **Row-level access**: Use User Permission rules to restrict which records users can edit

### 7) Style the web form

Web forms use the website theme by default. For custom styling:

```html
<!-- Add custom CSS via Web Form → Custom CSS field -->
<style>
    .web-form-container { max-width: 600px; margin: 0 auto; }
    .web-form-container .form-group { margin-bottom: 1.5rem; }
    .web-form-container .btn-primary { background-color: #2490EF; }
</style>
```

## Verification

- [ ] Web form accessible at the correct URL (`/contact-us`)
- [ ] All fields render correctly
- [ ] Required field validation works
- [ ] Submission creates the correct DocType record
- [ ] Login requirement enforced (if configured)
- [ ] Edit and resubmit work (if configured)
- [ ] File uploads work within size limits
- [ ] Success message/redirect works after submission
- [ ] Custom Python validation runs on submit

## Failure modes / debugging

- **Form not accessible**: Check if published; verify URL slug
- **Permission denied on submit**: Check DocType permissions for Website User or Guest
- **Fields not showing**: Ensure fields are added to the Web Form (not just on the DocType)
- **Custom JS not loading**: Check browser console; ensure file path is correct
- **Validation not firing**: Verify `validate` function in Python file returns/throws correctly
- **Duplicate entries**: Check "Allow Multiple" setting; add custom duplicate detection

## Escalation

- For DocType schema → `frappe-doctype-development`
- For Frappe UI portal apps → `frappe-frontend-development`
- For API endpoint access → `frappe-api-development`

## References

- [references/web-forms.md](references/web-forms.md) — Web Form creation and customization

## Guardrails

- **Validate input server-side**: Never trust client validation; check in `validate()` Python method
- **Use captcha for public forms**: Enable reCAPTCHA for guest-accessible forms to prevent spam
- **Sanitize output**: Escape user-submitted data when displaying; use `frappe.utils.escape_html()`
- **Limit file uploads**: Set max file size and allowed types for attachment fields
- **Check rate limits**: Consider throttling form submissions from same IP

## Common Mistakes

| Mistake | Why It Fails | Fix |
|---------|--------------|-----|
| Missing DocType permissions | "Permission denied" on submit | Grant Create permission to Website User or Guest role |
| Not handling file uploads | Files don't attach to record | Configure Attach field properly; check upload limits |
| XSS vulnerabilities | Security risk | Escape user input in display; use `| e` filter in templates |
| Forgetting to publish form | 404 error | Check "Published" checkbox in Web Form |
| Client-only validation | Invalid data in database | Add `validate()` method in web form Python file |
| Not testing as guest user | Works for admin, fails for users | Test in incognito/logged out mode |
