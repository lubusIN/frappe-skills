# Hooks and extension points

## hooks.py basics
- Every app can define `hooks.py` to register events, overrides, and assets.
- Hooks are discovered by Frappe at runtime and merged across installed apps.

## Extending DocTypes and controllers
- `override_doctype_class` replaces a DocType controller class (use sparingly).
- `extend_doctype_class` (v16+) extends a controller without full replacement; prefer this when available.

## Events
- Use `doc_events` to attach handlers to DocType lifecycle events (`before_save`, `validate`, `on_submit`, etc.).

## Scheduled tasks
- Use scheduler events in `hooks.py` to run periodic jobs.

## Client-side extensions
- Attach form scripts via `doctype_js` and `doctype_list_js` hooks.

## Server-side overrides
- Use `override_whitelisted_methods` to replace RPC methods from another app when needed.

Sources: Hooks, Scheduler (official docs)
