# Version compatibility notes

## Frappe v16+
- `extend_doctype_class` is available as a safer alternative to full controller overrides.

## Frappe v15+
- REST API v2 is available under `/api/v2/` routes.

## Frappe v11.0.3+
- Token-based authentication for REST API is supported.

## Guidance
- When targeting multiple versions, prefer hooks and APIs that exist across versions.
- If a feature is version-gated, add a clear fallback path or guard in code.

Sources: Hooks (v16), REST API v2 (v15), Token Based Authentication (v11.0.3) (official docs)
