# REST API and RPC (expanded)

## REST API (resource endpoints)
- REST endpoints follow `/api/resource/<DocType>` for CRUD on DocTypes.
- Common operations: list, read by name, insert, update, delete.

## REST API v2
- v2 uses `/api/v2/document/<DocType>` and returns a standardized response structure.

## RPC API (whitelisted methods)
- Use `frappe.whitelist` on Python functions to expose RPC endpoints.
- Call RPC methods via `/api/method/<python.path>`.

## Authentication
- Token auth: `Authorization: token <api_key>:<api_secret>`.
- Basic auth: `Authorization: Basic <base64(api_key:api_secret)>`.
- OAuth2: `Authorization: Bearer <access_token>` when configured.

## Permissions
- REST endpoints enforce DocType permissions based on the authenticated user.
- RPC methods should check permissions explicitly when operating on documents.

## Filters and pagination
- Use query parameters for filtering and pagination (`fields`, `filters`, `limit_start`, `limit_page_length`).
- Prefer explicit fields for performance and smaller responses.

## Error handling
- Handle Frappe error responses consistently; surface `message`, `exc`, and `traceback` as needed.

## Best practices
- Prefer REST endpoints for DocType CRUD.
- Use RPC for workflows or custom operations that do not map to a DocType resource.
- Validate payloads server-side in RPC methods.

Sources: REST API, REST API v2, RPC API, Token Based Authentication (official docs)
