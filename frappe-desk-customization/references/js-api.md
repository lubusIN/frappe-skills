# JavaScript API (comprehensive)

## Core globals
- `frappe` is the global namespace for client APIs.
- `frappe.ui` contains UI helpers like dialogs and form utilities.
- `frappe.session` has user/session context.

## Form API
- Use `frappe.ui.form.on(doctype, { ... })` to register form hooks.
- Common hooks: `setup`, `onload`, `refresh`, `validate`, `before_save`, `after_save`.
- Use `frm.set_value`, `frm.get_value`, `frm.get_field`.
- Use `frm.toggle_display`, `frm.toggle_enable`, `frm.set_df_property`.
- Use `frm.add_custom_button` for custom actions.
- Use `frm.set_query` to filter Link field options.

## Field events
- Use fieldname handlers (`fieldname(frm) {}`) to handle field changes.

## Dialogs and prompts
- Use `frappe.ui.Dialog` for modal inputs.
- Use `dialog.get_values()` and `dialog.set_values()`.
- Use `frappe.prompt` for quick input dialogs.

## Client calls
- Use `frappe.call` to call whitelisted server methods.
- Use `frappe.xcall` for Promise-based calls.

## UI feedback
- Use `frappe.msgprint` for messages.
- Use `frappe.show_alert` for transient notifications.
- Use `frappe.confirm` for confirmations.

## List View
- Customize with `frappe.listview_settings["DocType"]`.
- Use `get_indicator` for colored status indicators and badges.

## Report API
- Customize Query Reports with `frappe.query_reports`.
- Use `onload` and custom filter logic for dynamic reports.

## Router and navigation
- Use `frappe.set_route` to navigate.
- Use `frappe.route_options` to pass filters.

## Realtime
- Use `frappe.realtime.on` for realtime events.

## Utilities
- Use `frappe.utils` for date/time formatting and helpers.

## Permissions and session
- Use `frappe.user.has_role` for client role checks.
- Use `frappe.session.user` for current user.

## Examples (app-level scripts)
- Form Script: `/assets/mini-app-template/your_app/doctype/sample_doc/sample_doc.js`
- List View: `/assets/mini-app-template/your_app/list_view/sample_doc_list.js`
- Query Report: `/assets/mini-app-template/your_app/report/sample_report/sample_report.js`

Sources: Form Scripts, Client Script, Dialog, List View, Query Report, Realtime, JS API (official docs)
