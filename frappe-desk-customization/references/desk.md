# Desk UI and Scripting

## Overview
- Desk is the admin UI for System Users.
- It renders Form, List, Report, Tree, Calendar, Kanban, Dashboard, and Workspace views from DocType metadata.
- Scripts can be app-level (version controlled) or Client Scripts (per-site).

## Workspaces
- Workspaces organize modules, shortcuts, charts, and links for navigation.
- Customize Workspace layout to highlight key DocTypes and reports.

## Views
- **List View**: filters, sorting, indicators, bulk actions.
- **Form View**: DocType form builder and custom scripts.
- **Report View**: reports from builder, SQL, or Python.
- **Tree, Kanban, Calendar**: specialized views for hierarchical, status, or time-based data.

## Form Scripts
- Use `frappe.ui.form.on(doctype, {...})` to hook form events.
- Common events: `setup`, `onload`, `refresh`, `validate`, `before_save`, `after_save`.
- Use `frm.add_custom_button`, `frm.set_query`, `frm.toggle_display`, `frm.toggle_enable`.
- Use `frm.set_value`, `frm.get_value`, `frm.get_field`, `frm.set_df_property`.
- Use fieldname handlers (`fieldname(frm) {}`) to handle field changes.

## List View Scripts
- Use `frappe.listview_settings["DocType"]` to customize list actions and indicators.
- Add bulk actions and list badges via `get_indicator`.

## Report Scripts
- Use `frappe.query_reports` to add filters and client-side formatting.
- Use `onload` and custom filter logic for dynamic reports.

## Dashboard and Links
- Use Dashboard metadata to show related DocTypes.
- Use Links and Cards for quick access in Desk.

## Permissions
- Use permissions to control visibility of Desk items.

## Best Practices
- Prefer app-level scripts for reusable logic.
- Keep scripts lightweight and defer heavy work to server-side RPC methods.

## Examples (app-level scripts)
- Form Script: `/assets/mini-app-template/your_app/doctype/sample_doc/sample_doc.js`
- List View: `/assets/mini-app-template/your_app/list_view/sample_doc_list.js`
- Query Report: `/assets/mini-app-template/your_app/report/sample_report/sample_report.js`

Sources: Form Scripts, Client Script, List View, Query Report, Dashboard, Desk UI (official docs)

References:
- [Desk UI](https://frappe.io/framework/desk-ui)
