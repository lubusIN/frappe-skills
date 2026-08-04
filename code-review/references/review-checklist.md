# Review Checklist

A condensed reference for use during reviews. Check the items relevant to
your current review stage.

---

## Stage 1 — Audit

### Code hygiene
- [ ] No duplicate logic across modules
- [ ] No dead code (unreachable branches, uncalled functions)
- [ ] No unused imports or variables
- [ ] No commented-out code blocks
- [ ] No debug statements (`print`, `console.log`, `debugger`, `breakpoint`)
- [ ] No temporary or scratch files in the repository
- [ ] No untracked TODOs/FIXMEs (create issues instead)

### Complexity
- [ ] No functions exceeding 10 branches of cyclomatic complexity
- [ ] No oversized modules handling too many concerns
- [ ] No unnecessary wrapper functions

### Frontend
- [ ] frappe-ui components used for standard interface elements
- [ ] Repeated UI patterns extracted into shared components
- [ ] Semantic tokens used instead of hardcoded values
- [ ] No plain HTML for interactive elements
- [ ] No deeply nested DOM structures
- [ ] No inline styling in templates

### Tailwind
- [ ] No duplicated utility class combinations
- [ ] Consistent spacing scale across elements
- [ ] Class strings remain readable (consider extraction if 15+ utilities)

### Dark mode
- [ ] All colours reference semantic tokens
- [ ] Focus indicators visible in both themes
- [ ] Hover effects maintain contrast in both themes
- [ ] Text meets WCAG AA contrast ratio (4.5:1 minimum)
- [ ] No raw hex values in templates or stylesheets

---

## Stage 2 — Code Review

### Correctness
- [ ] Invariants are explicitly enforced
- [ ] Transaction boundaries are correct (no stray commits or rollbacks)
- [ ] Edge cases handled (empty inputs, None values, boundary conditions)
- [ ] No mutable default arguments
- [ ] No list/dict mutation during iteration
- [ ] Return shapes are consistent and documented
- [ ] Backward compatibility preserved

### Security
- [ ] No string-interpolated SQL (use `frappe.qb` or parameterised queries)
- [ ] `@frappe.whitelist` methods validate input types at entry
- [ ] `allow_guest=True` justified and minimally scoped
- [ ] No `eval`/`exec` usage
- [ ] Secrets stored in password fields, never in plain text
- [ ] No user input injected into DOM without escaping
- [ ] File paths validated against traversal attacks

### Performance
- [ ] No database calls inside loops (N+1 query pattern)
- [ ] Unbounded scans are bounded or paginated
- [ ] Missing indexes flagged for filtered/joined columns
- [ ] Expensive operations deferred to background jobs where appropriate
- [ ] Read operations target < 1s, write operations target < 5s

### Concurrency
- [ ] No check-then-act patterns without locking
- [ ] Shared mutable state protected or eliminated
- [ ] Uniqueness constraints enforced at database level

### Readability
- [ ] Functions are focused and reasonably sized
- [ ] Nesting depth is shallow (guard clauses used)
- [ ] Naming is consistent with existing codebase conventions
- [ ] Type annotations present on function signatures

### Architecture
- [ ] Component boundaries respected
- [ ] No monkey-patching of framework internals
- [ ] Hook-based integration preferred over direct modification

### API design
- [ ] No breaking changes to existing interfaces
- [ ] New parameters added as keyword arguments with defaults
- [ ] Deprecations communicated clearly

### Database integrity
- [ ] Migrations and patches are idempotent
- [ ] Indexes committed in code (not applied ad-hoc)
- [ ] No `db.delete` or `set_value` with empty/None filters
- [ ] `get_single_value`/`set_single_value` used for Singles

### Testing
- [ ] Bug fixes include regression tests
- [ ] Tests are deterministic (no reliance on execution order or wall clock)
- [ ] Test data cleaned up properly

### Observability
- [ ] Errors include context (what happened, who was affected, what changed)
- [ ] Exception chains preserved (`raise ... from e`)
- [ ] Log levels appropriate (not everything is `ERROR`)

---

## Stage 3 — Strict Validation

### Static analysis
- [ ] Ruff passes with no errors
- [ ] Pre-commit hooks pass on all files
- [ ] Semgrep reports no security findings
- [ ] pip-audit shows no HIGH/CRITICAL vulnerabilities

### Compatibility
- [ ] `requires-python` in pyproject.toml is correct
- [ ] Node version compatibility verified
- [ ] MariaDB syntax compatible with minimum supported version
- [ ] Frappe APIs used are available in target version
- [ ] Redis commands available in minimum supported version

### Infrastructure
- [ ] pyproject.toml metadata and dependencies correct
- [ ] hooks.py references existing functions
- [ ] CI workflows syntactically valid and version matrix correct

### Tests
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Regression tests present for bug fixes
