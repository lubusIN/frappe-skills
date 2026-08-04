Your App - Mini App Template

Purpose
- Provide a minimal, opinionated pattern for building production-grade Frappe apps.

Key patterns
- Service layer: place business logic in `services/` (see `sample_service.py`). Keep API handlers thin.
- Error handling: use `utils/errors.py` to return consistent error codes for API consumers.
- Logging: use `utils/logging.py` to capture messages and tracebacks.
- Validation & permissions: use `utils/validation.py` and `utils/permissions.py` from API handlers or services.
- Integrations: wrap external calls and map errors to `ERROR_CODES` (see `integrations/sample_connector.py`).

Files of interest
- `api.py` — small whitelisted handlers; delegates to services and returns `ok`/`error` payloads.
- `services/sample_service.py` — service layer used by `api.py` for creating documents.
- `utils/` — helpers for caching, validation, permissions, logging, and errors.
- `doctype/` — example DocType and client-side script demonstrating UI hooks.
- `report/`, `list_view/`, `background_jobs/` — practical examples for common app features.

Recommendations for production readiness
- Add tests for `services/` and `integrations/`.
- Centralize configuration values (API URLs, timeouts) in site config or environment variables.
- Use `frappe.enqueue` for long-running tasks and instrument metrics where necessary.
- Prefer explicit exception handling in API handlers to map to `ERROR_CODES`.
- Document hooks and override points in `hooks.py` for maintainers.

Try it
- Copy this template folder into a new app and update `app_name` and module paths.
- Run a small smoke test creating a `Sample Doc` via the create API or the UI.

If you'd like, I can:
- Add unit tests for `sample_service.py` and `sample_connector.py`.
- Add a minimal `requirements.txt` listing third-party dependencies like `requests`.
