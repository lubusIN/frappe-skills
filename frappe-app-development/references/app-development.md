# App development (end-to-end)

## Typical app structure
- App modules live under `<app>/<app_module>/`.
- Keep domain logic in dedicated modules (e.g., `services/`, `utils/`, `api/`) instead of bloating DocType controllers.
- Use `doctype/<doctype_name>/` for DocType controllers, tests, and UI assets.

## Scaffolding workflow
- Create app with `bench new-app` and install on site.
- Create DocTypes in developer mode to export them into app files.
- Add form scripts and list/report scripts in the app for reusable UI behavior.

## Domain architecture patterns
- Keep DocType controllers thin; treat them as validation + orchestration.
- Move complex business logic into service modules (e.g., `your_app/services/billing.py`).
- Encapsulate integrations in `integrations/` or `connectors/` modules.
- Expose public APIs via a single `api.py` or `api/` package to control surface area.

## Background jobs
- Use background jobs for long-running tasks; avoid blocking request/submit handlers.
- Keep jobs idempotent and retry-safe; accept a job key and guard duplicate work.

## Event-driven patterns
- Prefer `doc_events` in hooks for cross-cutting behavior.
- Avoid deep override chains; keep event handlers small and delegate to services.

## Permissions and roles
- Define DocType permissions per role.
- Re-check permissions in RPC methods before acting on documents.

## API design
- Use REST endpoints for DocType CRUD; use RPC for workflows and custom actions.
- Validate user permissions and input payloads in all RPC methods.
- Return structured responses and handle errors consistently.

## Performance and scale
- Prefer `frappe.get_list` or Query Builder for efficient reads.
- Avoid N+1 queries by loading related data in bulk.
- Cache expensive reads when safe and invalidate on writes.

## Testing and CI
- Write unit tests for DocType logic and services.
- Add integration tests for workflows and API endpoints.
- Run tests in CI with a clean site and minimal fixtures.

## Packaging and release
- Commit exported DocType JSON and scripts to version control.
- Use patches for data changes and `bench migrate` on upgrade.
- Document breaking changes and provide migration notes.

## Production hardening
- Validate permissions at every boundary.
- Avoid direct SQL unless necessary; keep queries parameterized.
- Use background jobs for heavy tasks and set reasonable timeouts.

## Production-grade checklist
- **Security**: enforce permissions in server APIs; validate inputs; avoid unsafe SQL.
- **Reliability**: idempotent jobs, retries, clear error handling.
- **Observability**: structured logging, error capture, key events in logs.
- **Performance**: query builder, pagination, caching for hot paths.
- **Maintainability**: thin controllers, service modules, consistent API envelopes.
- **Upgrade safety**: use patches and keep schema changes versioned.

## Templates
- Service layer example: `/assets/mini-app-template/your_app/services/sample_service.py`
- Background job stub: `/assets/mini-app-template/your_app/background_jobs/sample_job.py`
- API response envelope example: `/assets/mini-app-template/your_app/api.py`
- Integration connector stub: `/assets/mini-app-template/your_app/integrations/sample_connector.py`
- Cache helper: `/assets/mini-app-template/your_app/utils/cache.py`
- Permission helper: `/assets/mini-app-template/your_app/utils/permissions.py`
- Error response helper: `/assets/mini-app-template/your_app/utils/errors.py`
- Logging helper: `/assets/mini-app-template/your_app/utils/logging.py`
- Validation helper: `/assets/mini-app-template/your_app/utils/validation.py`

Sources: Apps, Developer Mode, Background Jobs, Hooks, Permissions, REST/RPC API, Query Builder, Tests, Migrations (official docs)
