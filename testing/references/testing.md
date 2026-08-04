# Testing (expanded)

## Running tests
- Install dev dependencies: `bench setup requirements --dev`.
- Run all tests: `bench --site <site> run-tests`.
- Run tests for an app: `bench --site <site> run-tests --app <app_name>`.
- Run tests for a module: `bench --site <site> run-tests --module <module_path>`.
- Run tests for a DocType: `bench --site <site> run-tests --doctype "DocType"`.

## Test types
- **Unit tests**: focus on DocType controller logic and utility functions.
- **Integration tests**: validate workflows, permissions, and API calls.
- **UI tests**: use Cypress for end-to-end flows.

## Test structure
- Tests must start with `test_` and be Python files.
- DocType tests live in `doctype/<doctype_name>/test_<doctype_name>.py`.
- Module tests live in `<app>/<module>/tests/`.

## Writing tests
- Use `frappe.get_doc` to construct test documents.
- Use `self.assertRaises` or `frappe.throw` assertions for validation errors.
- Keep tests deterministic: no network, no random data without seeding.
- Use minimal fixtures and create test data in setup.

## Fixtures and test data
- Use fixtures for metadata required by tests.
- Use test records with clear naming to avoid collisions.

## Database isolation
- Tests run inside transactions; keep tests idempotent.
- Avoid shared state between tests; clean up test data when needed.

## Permissions testing
- Use `frappe.set_user` to test role-based access.
- Assert permission errors for restricted actions.

## UI testing (Cypress)
- Run UI tests: `bench --site <site> run-ui-tests <app>`.
- Headless UI tests: `bench --site <site> run-ui-tests <app> --headless`.

## CI considerations
- Run tests against a fresh site and database.
- Seed only required fixtures for speed.
- Keep test suite runtime small and parallelize if possible.

Sources: Testing, Unit Testing, UI Testing (official docs)
