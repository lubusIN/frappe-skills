```markdown
# Controller Lifecycle Hooks Reference

## Overview
Controllers are Python classes that handle document lifecycle events. Each DocType can have a controller that extends `frappe.model.document.Document`.

## Controller Structure

```python
# my_app/doctype/my_doc/my_doc.py
import frappe
from frappe import _
from frappe.model.document import Document

class MyDoc(Document):
    def validate(self):
        """Called during save, before database write."""
        pass
    
    def before_save(self):
        """Called after validate, before database write."""
        pass
    
    def after_insert(self):
        """Called after first save (insert only)."""
        pass
```

## Lifecycle Hook Order

### On Insert (New Document)
```
1. __init__
2. before_insert
3. validate
4. before_save
5. before_naming (if autoname)
6. autoname
7. [Database INSERT]
8. after_insert
9. after_save
10. on_change
```

### On Update (Existing Document)
```
1. __init__
2. validate
3. before_save
4. [Database UPDATE]
5. on_update
6. after_save
7. on_change
```

### On Submit (Submittable DocTypes)
```
1. validate
2. before_save
3. before_submit
4. [Database UPDATE - docstatus=1]
5. on_submit
6. after_save
7. on_change
```

### On Cancel
```
1. before_cancel
2. [Database UPDATE - docstatus=2]
3. on_cancel
4. on_change
```

### On Delete
```
1. before_delete (v16+) / on_trash
2. [Database DELETE]
3. after_delete
```

## Hook Reference

### Validation Hooks

#### validate
Called on every save. Use for data validation and lightweight normalization.

```python
def validate(self):
    if self.end_date and self.start_date:
        if self.end_date < self.start_date:
            frappe.throw(_("End Date cannot be before Start Date"))
    
    # Normalize data
    if self.email:
        self.email = self.email.lower().strip()
```

**Best Practices:**
- Keep lightweight - runs on every save
- Raise `frappe.throw()` for validation errors
- Don't make external API calls
- Don't create/modify other documents

#### before_validate
Called before `validate`. Use for pre-validation setup.

```python
def before_validate(self):
    # Set computed fields that validation depends on
    self.total = sum(item.amount for item in self.items)
```

### Save Hooks

#### before_save
Called after validation, before database write. Use for final data normalization.

```python
def before_save(self):
    self.full_name = f"{self.first_name} {self.last_name}".strip()
    self.modified_by_script = True
```

#### after_save
Called after database write. Use for post-save actions that need the saved state.

```python
def after_save(self):
    # Update related documents
    if self.has_value_changed("status"):
        self.update_related_records()
    
    # Clear caches
    frappe.cache().delete_key(f"my_doc:{self.name}")
```

### Insert/Creation Hooks

#### before_insert
Called only on new document creation, before any validation.

```python
def before_insert(self):
    # Set defaults that depend on other field values
    if not self.assigned_to:
        self.assigned_to = self.get_default_assignee()
```

#### after_insert
Called only after first save. Use for post-creation side effects.

```python
def after_insert(self):
    # Create related documents
    self.create_initial_task()
    
    # Send notifications
    frappe.publish_realtime("new_document", {
        "doctype": self.doctype,
        "name": self.name
    })
```

### Update Hooks

#### on_update
Called after save of existing document (not on insert).

```python
def on_update(self):
    # Sync with external systems
    if self.has_value_changed("status"):
        self.sync_to_external_system()
```

### Submit/Cancel Hooks (Submittable DocTypes)

#### before_submit
Called before docstatus changes to 1.

```python
def before_submit(self):
    # Final validation before locking
    if not self.items:
        frappe.throw(_("Cannot submit without items"))
    
    # Set submission timestamp
    self.submitted_at = frappe.utils.now()
```

#### on_submit
Called after docstatus changes to 1.

```python
def on_submit(self):
    # Create downstream documents
    self.create_invoice()
    
    # Update stock
    self.update_stock_ledger()
```

#### before_cancel
Called before docstatus changes to 2.

```python
def before_cancel(self):
    # Check if cancellation is allowed
    if self.has_linked_invoices():
        frappe.throw(_("Cancel linked invoices first"))
```

#### on_cancel
Called after docstatus changes to 2.

```python
def on_cancel(self):
    # Reverse downstream effects
    self.reverse_stock_entries()
    self.cancel_linked_documents()
```

### Update After Submit

#### before_update_after_submit
For fields with `allow_on_submit = 1`.

```python
def before_update_after_submit(self):
    # Validate changes to submitted document
    if self.has_value_changed("critical_field"):
        frappe.throw(_("Cannot change critical field after submit"))
```

#### on_update_after_submit
Called after update to submitted document.

```python
def on_update_after_submit(self):
    # Handle allowed post-submit changes
    self.recalculate_totals()
```

### Delete Hooks

#### on_trash
Called before document deletion.

```python
def on_trash(self):
    # Clean up related records
    frappe.delete_doc("Comment", {"reference_doctype": self.doctype, "reference_name": self.name})
    
    # Clear files
    self.delete_attachments()
```

#### after_delete
Called after document deletion.

```python
def after_delete(self):
    # Clear caches
    frappe.cache().delete_key(f"my_doc_list")
```

### Change Detection Hook

#### on_change
Called whenever document state changes (save, submit, cancel).

```python
def on_change(self):
    # Audit logging
    if self.has_value_changed("status"):
        self.log_status_change()
```

## Utility Methods

### has_value_changed
Check if a field changed during this save.

```python
def on_update(self):
    if self.has_value_changed("status"):
        old_status = self.get_doc_before_save().status
        new_status = self.status
        frappe.log(f"Status changed: {old_status} → {new_status}")
```

### get_doc_before_save
Access the document state before current changes.

```python
def validate(self):
    old_doc = self.get_doc_before_save()
    if old_doc and old_doc.submitted:
        frappe.throw(_("Cannot modify submitted document"))
```

### db_set
Update single field without triggering hooks.

```python
def after_save(self):
    # Update counter without triggering another save
    self.db_set("view_count", self.view_count + 1)
```

### run_method
Call a method if it exists.

```python
def after_save(self):
    self.run_method("custom_after_save")  # Calls if defined
```

## Best Practices

### Keep Controllers Thin
```python
# ❌ Bad: Business logic in controller
def on_submit(self):
    # 50 lines of invoice creation logic...

# ✅ Good: Delegate to service layer
def on_submit(self):
    from my_app.services.invoicing import create_invoice_from_order
    create_invoice_from_order(self)
```

### Use Appropriate Hooks
| Task | Recommended Hook |
|------|------------------|
| Data validation | `validate` |
| Computed fields | `before_save` |
| Send notifications | `after_insert`, `after_save` |
| Create related docs | `after_insert`, `on_submit` |
| External sync | `on_update`, `on_submit` |
| Cleanup on delete | `on_trash` |

### Avoid Common Mistakes
```python
# ❌ Don't: Create documents in validate (may not save)
def validate(self):
    frappe.get_doc({"doctype": "Log"}).insert()

# ✅ Do: Create in after_save
def after_save(self):
    frappe.get_doc({"doctype": "Log"}).insert()

# ❌ Don't: Long operations in hooks
def on_submit(self):
    sync_to_100_external_systems()  # Blocks request

# ✅ Do: Background jobs for long operations
def on_submit(self):
    frappe.enqueue("my_app.jobs.sync_external", doc_name=self.name)
```

Sources: Controller Methods, Document API, Lifecycle Hooks (official docs)
```