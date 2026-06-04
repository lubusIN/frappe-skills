# Server Scripts

## Overview
Server Scripts allow you to dynamically define Python scripts that execute on the server on document events or as custom API endpoints—without writing app code. They are useful for site-specific automation without custom app deployment.

**Note**: Server Scripts are disabled by default on shared benches (v15+) for security. Enable with:
```bash
bench --site <site> set-config server_script_enabled true
```

## Creating a Server Script
1. Ensure `server_script_enabled` is `true` in `site_config.json`.
2. Ensure your role is System Manager.
3. Type "New Server Script" in the awesomebar.
4. Set the script type (Document Event / API).
5. Set the document type and event name, or method name, plus the script.

## Script Types

### Document Events
- Before Insert, After Insert
- Before Validate, Before Save, After Save
- Before Submit, After Submit
- Before Cancel, After Cancel
- Before Delete, After Delete
- Before Save (Submitted Document), After Save (Submitted Document)
- Before Print

### API Scripts
- Create custom API endpoints on the fly.
- Endpoints are prefixed with `/api/method/<method_name>`.
- Enable guest access with the "Allow Guest" checkbox.
- IP-based rate limiting available.

## Security
Server Scripts use the RestrictedPython library to limit available methods. See the Script API for allowed methods.

## Examples

### Change value before save
Script Type: Before Save
```python
if "test" in doc.description:
    doc.status = 'Closed'
```

### Custom validation
Script Type: Before Save
```python
if "validate" in doc.description:
    raise frappe.ValidationError
```

### Auto-create ToDo
Script Type: After Save
```python
if doc.allocated_to:
    frappe.get_doc(dict(
        doctype = 'ToDo',
        owner = doc.allocated_to,
        description = doc.subject
    )).insert()
```

### API Script
Script Type: API, Method Name: `test_method`
```python
frappe.response['message'] = "hello"
```
Request: `/api/method/test_method`

### Internal Library (v13+)
Use `frappe.flags` to share data between scripts:
```python
# Script 1
frappe.flags.my_key = 'my value'

# Script 2
my_key = run_script('script_1').get('my_key')
```

## When to Use
- **Server Scripts**: Site-specific automation without custom apps.
- **App-level controllers/hooks**: Reusable behavior bundled with an app.

Sources: Server Script, Script API (official docs)
