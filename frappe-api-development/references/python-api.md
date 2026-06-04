# Python API

## Document API
- Use `frappe.get_doc(doctype, name)` to fetch an existing document.
- Use `frappe.get_doc({"doctype": ..., ...})` to create a new document in memory.
- Use `doc.insert()` to insert and `doc.save()` to update; both run validations.
- Use `doc.submit()` / `doc.cancel()` for submittable workflows.
- Use `doc.get("fieldname")` and `doc.set("fieldname", value)` for field access.
- Use `doc.append("child_table_field", row_dict)` to add child rows.
- `doc.docstatus` for workflow status (0=Draft, 1=Submitted, 2=Cancelled).
- `doc.modified`, `doc.owner`, `doc.creation` for audit metadata.

### Direct DB Writes (use sparingly)
- `doc.db_set("field", value)` updates a single field in DB.
- `doc.db_update()` writes the document without full validation.

### Validation Patterns
- Put lightweight validation in `validate`.
- Use `before_save` for pre-save normalization.
- Use `after_insert` for post-create side effects.

## Database API
- Use `frappe.get_list` / `frappe.get_all` for DocType queries with permissions.
- Use `frappe.get_value` / `frappe.db.get_value` for simple reads.
- Use `frappe.get_cached_doc` for cached reads of Documents.
- Use `frappe.db.set_value` for targeted updates when appropriate.
- Use `frappe.db.sql` with parameterized queries for raw SQL.
- Use `frappe.db.commit()` and `frappe.db.rollback()` in controlled contexts.
- Avoid manual commits inside request handlers unless you know the implications.

## Query Builder
- Use `frappe.qb.DocType("DocType")` to start a query.
- Use `frappe.qb.from_(DocType).select(...)` to build queries.
- Use `.where(...)` for filters and `.orderby(...)` for sorting.
- Use `.limit()` and `.offset()` for pagination.
- Use `.left_join()` / `.join()` with `on()` for joins.
- Use `frappe.query_builder.functions as fn` for aggregations (`Count`, `Sum`, `Avg`).
- Use `.groupby(...)` with aggregate functions.
- Use `.run(as_dict=True)` to fetch results as dictionaries.
- Prefer Query Builder over raw SQL for safety and readability.

## Permissions and User Context
- Use `frappe.has_permission` to check DocType permissions.
- Use `frappe.get_roles` to inspect user roles.
- Use `frappe.session.user` for the current user.
- Use `frappe.set_user` only in controlled system tasks.

## Files and Attachments
- Use `frappe.get_doc("File", name)` for file metadata.
- Use `frappe.utils.file_manager` helpers for file operations.

## Email and Notifications
- Use `frappe.sendmail` for outbound email.
- Use `frappe.publish_realtime` for realtime UI events.

## Background Jobs
- Use `frappe.enqueue` for background jobs.
- Keep jobs idempotent and include `timeout` and `queue`.

## Scheduling
- Use Scheduler Events and `hooks.py` to run scheduled jobs.

## Caching
- Use `frappe.cache()` for key-value caching.

## Requests and Integrations
- Use `frappe.integrations.utils` helpers when available.
- Prefer centralized connector modules for external APIs.

## Printing and PDF
- Use print utilities for generating PDFs from print formats.

## Reports and Dashboards
- Use Query Reports with `execute(filters)` in Python.
- Use Report and Dashboard DocTypes for standard reporting metadata.

## Fixtures and Data Migration
- Use fixtures to ship metadata from apps.
- Use patches for data migrations and upgrades.

## Utility Functions
- Use `frappe.utils` for date/time, file, string, and JSON helpers.
- Common helpers: `getdate`, `get_datetime`, `add_days`, `add_months`, `nowdate`, `now_datetime`.
- Common type helpers: `cint`, `flt`, `cstr`.
- Use `frappe.as_json` and `frappe.parse_json` for serialization.
- Use `frappe.utils.password` or encryption helpers when storing secrets.
- Use `frappe.local.site` and `frappe.local` context for current site/session info.

## Error Handling
- Use `frappe.throw` for validation errors.
- Use `frappe.msgprint` for user-visible messages.

## Whitelisted Methods (RPC)
- Use `@frappe.whitelist` to expose Python functions to RPC.

Sources: Document API, Database API, Query Builder, File Manager, Email, Realtime, Background Jobs, Permissions, Utilities, Scheduler, Reports, Fixtures, Controller Methods (official docs)
