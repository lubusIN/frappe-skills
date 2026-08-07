# Stage 3 — Strict Validation

Automated checks and tooling-driven validation. This stage is **not part of the
default review workflow** — run it only when explicitly requested or when the
change touches infrastructure, dependencies, or cross-version compatibility.

---

## Static Analysis

### Ruff

Run Ruff for both linting and formatting. It replaces flake8, isort, pycodestyle,
and black in a single tool.

```bash
# Lint with auto-fix
ruff check --fix .

# Format
ruff format .

# Check without modifying (CI mode)
ruff check .
ruff format --check .
```

Ensure the project's `pyproject.toml` has a `[tool.ruff]` section with
appropriate rule selections. At minimum, enable:

- `E` / `W` — pycodestyle errors and warnings
- `F` — pyflakes
- `I` — isort
- `UP` — pyupgrade
- `B` — flake8-bugbear
- `SIM` — flake8-simplify

### Pre-commit

Verify that `.pre-commit-config.yaml` exists and includes hooks for:

- Ruff (linting and formatting)
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON validation
- Merge conflict markers

Run the full suite:

```bash
pre-commit run --all-files
```

### Semgrep

Use Semgrep for security-focused pattern matching. Key rules to enforce:

- No string-interpolated SQL (`f"SELECT ... {variable}"`)
- No `eval()` or `exec()` calls outside sanctioned modules
- No `allow_guest=True` without explicit justification
- No secrets in source code

```bash
semgrep --config auto .
```

> **IMPORTANT FOR AI:** If `semgrep` is not installed in the local environment, DO NOT skip this scan. You must pause the review and explicitly ask the user to install it (e.g., `pip install semgrep`) before proceeding.

### pip-audit

Scan Python dependencies for known vulnerabilities:

```bash
pip-audit
```

> **IMPORTANT FOR AI:** `pip-audit` scans the entire Bench virtual environment. You must **IGNORE** any vulnerabilities found in global Frappe dependencies (like `cryptography`, `aiohttp`, etc.). **Do not** recommend upgrading packages in the Bench environment. Only flag vulnerabilities if they belong to dependencies explicitly defined in the current app's `pyproject.toml` or `requirements.txt`.

---

## Compatibility Matrix

Frappe applications must work across a range of infrastructure versions.
Validate explicitly when a change touches dependencies, system calls, or
version-specific APIs.

### Python

- Verify the `requires-python` field in `pyproject.toml`
- Check for syntax or stdlib APIs that are version-specific (e.g.
  `match` statements require 3.10+, `tomllib` requires 3.11+)
- Run tests against the minimum supported Python version

### Bench

- Confirm compatibility with the Bench version in use
- Check for deprecated Bench CLI commands or changed options
- Verify that `bench setup` commands still work as documented

### Redis

- Frappe uses Redis for caching, queuing, and realtime updates
- Verify that Redis commands used are available in the minimum
  supported Redis version
- Check for deprecated commands or changed behaviour across versions

### MariaDB

- Validate that SQL syntax works on the minimum supported MariaDB version
- Check for version-specific features (JSON functions, window functions,
  CTEs) and verify the floor version supports them
- Ensure `ALTER TABLE` statements are compatible and will not lock
  large tables for extended periods

### Frappe Version

- Verify that APIs used are available in the target Frappe version
- Check for deprecated APIs that will be removed in the next major version
- Validate that hook signatures match the expected format for the
  target version

---

## Infrastructure Checks

### pyproject.toml

- All metadata fields present (name, version, description, requires-python)
- Dependency ranges use compatible release specifiers (`~=` or `>=,<`)
  rather than exact pins where appropriate
- No stale or unused dependencies listed
- Build system configuration is correct

### hooks.py

- All registered hooks reference existing functions
- No hooks pointing to deleted or renamed modules
- Scheduler events have appropriate frequencies
- DocType event hooks follow the expected signature

### Workflows

- CI workflow files (`.github/workflows/`) are syntactically valid
- Test jobs run against the correct matrix of versions
- Deployment workflows have appropriate environment protections
- No hardcoded secrets in workflow files (use repository secrets)

### Dependency Definitions

- `pyproject.toml` is the single source of truth for all Python
  dependencies and build configuration
- Legacy `requirements.txt` and `setup.py` files should not exist — flag
  them for removal if present
- `required_apps` in `hooks.py` should not list `frappe` — it is the
  core runtime and always implicitly available. Frappe version constraints
  belong in `pyproject.toml` under `[tool.bench.frappe-dependencies]`
- Frontend dependencies in `package.json` are up to date
- No conflicting version constraints between direct and transitive
  dependencies
- Lock files (`package-lock.json`, `yarn.lock`) are committed and current

---

## Test Execution

Run the full test suite and verify results before approving.

### Unit tests

```bash
bench --site <site> run-tests --app <app>
```

All unit tests must pass. Newly failing tests indicate a regression.

### Integration tests

```bash
bench --site <site> run-tests --app <app> --module <app>.tests
```

Integration tests verify cross-document and cross-module behaviour.
Failures here often indicate broken assumptions about data state.

### Regression tests

Every bug fix should include a regression test that:

1. Reproduces the original failure
2. Verifies the fix resolves it
3. Remains part of the suite permanently

If a bug fix PR does not include a regression test, flag it. The fix
may be correct today but nothing prevents the bug from returning.
