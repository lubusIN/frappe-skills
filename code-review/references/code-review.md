# Stage 2 — Code Review

A deep structural review across ten dimensions. Work through them in order —
the sequence reflects how expensive each class of defect is to fix after it
ships. Spend the most attention on correctness and security; those two
categories account for the majority of critical production incidents.

For every finding, explain *why* it matters: what breaks, for whom, and under
what conditions.

---

## 1. Correctness

Correctness takes precedence over convenience, performance, or elegance. A
fast but wrong function is worse than a slow but correct one.

### Questions to ask for every change

- **What breaks?** — identify the failure mode. Silent data corruption is
  the most dangerous class of bug because it compounds over time.
- **Who is affected?** — a bug in a utility function may cascade across
  hundreds of callers. Scope the blast radius.
- **Can recovery occur?** — if this fails, is the system in a state that
  allows retry or correction? Or is data permanently lost?
- **Is existing behaviour preserved?** — long-standing behaviour that callers
  depend on is a contract, even if it was never formally documented.

### What to review

**Invariants and assertions** — business rules that must always hold true
(e.g. debit equals credit, stock cannot go negative) should be enforced
explicitly with assertions or validation. Assertions are for internal
invariants the code guarantees — not for user-facing validation.

**Transaction boundaries** — a stray `frappe.db.commit()` mid-transaction
terminates the transaction and exposes partial state. Every commit must be
intentional and justified. The same applies to `db.rollback()` — it can
silently discard valid work if placed incorrectly.

**Silent failures** — functions that swallow exceptions, return `None`
instead of raising, or log errors but continue processing. These hide
real problems and make debugging extremely difficult.

**Edge cases** — empty inputs, `None` values, zero-length lists, boundary
values (first/last item, max integer, empty string). Most production bugs
live at the edges, not in the happy path.

**Type mismatches** — a comparison between a string and a `datetime`, or a
string and an integer, will silently produce wrong results. Cast explicitly
at the boundary using `cint()`, `flt()`, `getdate()`, or similar converters.

**Mutable default arguments** — `def process(items=[])` shares a single
list object across every call. Use `None` as the default and create a new
container inside the function body.

**List mutation during iteration** — removing or adding items to a collection
while iterating over it either raises `RuntimeError` or silently skips
elements. Iterate over a copy, use `reversed()`, or build a new collection.

**Return shape consistency** — before indexing a result, verify whether it
can be `None`, an empty list, or a list of `None` values. Watch for confusion
between `as_dict=1` (returns list of dicts) and scalar returns.

**Implicit assumptions** — code that assumes a document exists, a field has
a value, or a linked record is in a particular state. These assumptions
should be validated, not trusted.

**Backward compatibility** — changing the semantics of a function that
callers have depended on for a long time is a breaking change, even when
the function signature remains identical. Treat established behaviour as
an implicit API contract.

### Patterns to avoid

- Partial commits — `frappe.db.commit()` inside loops or conditional branches
- Validation bypasses — saving or submitting documents without running
  the full validation chain
- Hidden side effects — functions that modify global state, write to the
  database, or send notifications without making that obvious in their name
  or signature

---

## 2. Security

Preventing a vulnerability is far less expensive than remediating one. Review
security-sensitive code (authentication, authorisation, permissions, user
management, data access) with heightened scrutiny.

### SQL and injection

- **Never construct SQL through string concatenation or f-strings.** Use the
  query builder (`frappe.qb`) or the ORM. If raw SQL is truly unavoidable,
  use parameter substitution: `frappe.db.sql("... WHERE name = %s", (name,))`.
- **Prefer `frappe.qb` over raw SQL entirely.** Beyond injection risk, raw
  SQL ties code to a specific database dialect and complicates future
  database portability.
- **Type confusion at ORM boundaries** — Frappe accepts complex types, so a
  parameter expected to be a string can arrive as a filter operator list
  (e.g. `{"key": ["!=", ""]}`). This can bypass equality checks on secrets
  or tokens. Validate input types with explicit `isinstance()` checks at
  every trust boundary.

### Whitelisted methods

- Every `@frappe.whitelist()` method is a public API endpoint. Audit each
  one for type validation, permission checks, and rate limiting.
- Verify that the method does not accept arbitrary method paths, class names,
  or code strings from the client.
- Check whether the method should be restricted to specific roles rather
  than being accessible to all logged-in users.

### Guest access

- `allow_guest=True` exposes a method to unauthenticated users. This is
  rarely appropriate and never a shortcut around proper authentication.
- When guest access is genuinely required (public forms, webhooks),
  verify that the method does not read or write sensitive data and that
  it has appropriate rate limiting.

### Path traversal

- If user input is used to construct a file path, verify that traversal
  sequences (`../`, `/../../`) cannot escape the intended directory.
- Prefer the File doctype API for file operations rather than constructing
  paths manually.


### Execution safety

- Never use `eval()` or `exec()` directly. If dynamic evaluation is
  required, use `safe_eval`/`safe_exec` and understand their limitations.
- Sandboxed execution (RestrictedPython) is not reliably escape-proof.
  Treat it as a mitigation, not a guarantee.
- Prefer allowlists over blocklists for any filtering or access control
  mechanism. Blocklists are inherently bypassable.

---

## 3. Performance

Treat slow code as a correctness problem. A request that blocks a worker
for 30 seconds is not merely inconvenient — it degrades the entire
application's throughput and responsiveness.

### Budgets

Establish expectations for response times and enforce them during review:

- Common read operations: under 100ms
- General reads: under 1 second
- Write operations: under 5 seconds
- Maximum tolerable: 10 seconds (anything beyond this should be a
  background job)

A slow synchronous request blocks a Gunicorn worker. Under load, this
leads to worker exhaustion and cascading failures.

### What to review

**N+1 queries** — loading a list of documents, then fetching a related
record for each one in a loop. This is the single most common performance
problem in Frappe applications. Fetch all related data in a single query
using joins or `frappe.get_all` with appropriate fields.

**Repeated calculations** — the same value computed multiple times within
a request. Cache intermediate results in a local variable or use
`@request_cache` for values that are stable within a single request.

**Expensive operations inside loops** — `frappe.get_doc()`, `get_value()`,
or any database call inside a loop. Move the query outside the loop and
operate on the result set.

**Unnecessary rendering** — rebuilding an entire page or component when
only a small section changed. On the frontend, ensure reactive updates
are scoped to the affected elements.

**Unbounded scans** — queries without `LIMIT`, date range filters, or
other bounds that could scan an entire table. On production data with
millions of rows, this causes timeouts and lock contention.

**Missing indexes** — any `WHERE` clause, `JOIN` condition, or `ORDER BY`
on a column that is not indexed. Indexes must be declared in code
(DocType field definitions or explicit migration patches) — indexes
applied manually in the database are lost during site migrations.

**Redundant document loading** — calling `frappe.get_doc()` multiple
times for the same document within a request. Load once and pass the
reference.

### Preferred approaches

- Aggregate in SQL rather than in Python — `SUM()`, `COUNT()`, `GROUP BY`
  are faster than fetching rows and accumulating in a loop
- Use `@redis_cache` for values that change infrequently and are
  expensive to compute
- Defer expensive work to background jobs (`frappe.enqueue`)
- Use indexed lookups exclusively for filtered queries

---

## 4. Concurrency

Concurrency bugs are invisible in development and during manual testing.
They surface under production load and are extremely difficult to reproduce.

### What to review

**Race conditions** — check-then-act patterns where the state can change
between the check and the action. Classic example: checking whether a
name exists, then creating a record — another request can create it in
between. Use database-level `UNIQUE` constraints instead.

**Shared mutable state** — global variables, module-level dicts, or
cached objects that multiple requests can modify simultaneously. In
Frappe's Gunicorn deployment, each worker is a separate process, but
within a worker, async operations or background threads can still
create contention.

**Locking** — `SELECT ... FOR UPDATE` on an unindexed column will
escalate to a table lock. Verify that locked queries target indexed
columns. Avoid holding locks across slow operations (network calls,
file I/O).

**Uniqueness constraints** — enforce uniqueness at the database level,
not in application code. Application-level uniqueness checks are
inherently racy.

**Transactional integrity** — operations that must succeed or fail as
a unit should be within a single transaction. Verify that nothing
commits or rolls back in the middle of such a unit.

### Preferred approaches

- Database constraints over application-level checks
- Stateless designs over shared mutable state
- Idempotent operations that are safe to retry
- Pessimistic locking only when optimistic approaches are insufficient

---

## 5. Readability

Code is read far more often than it is written. Optimise for the reader,
not the author.

### What to review

**Oversized functions** — functions that handle multiple responsibilities
or span hundreds of lines. Break them into focused units with clear names.

**Excessive nesting** — multiple levels of `if`/`for`/`try` nesting. Use
guard clauses to handle error conditions early and keep the main path
at a shallow indentation level.

**Unnecessary abstractions** — layers of indirection that add complexity
without adding flexibility. If a function is only called from one place
and its name restates what the code does, it may not need to exist.

**Duplicated logic** — the same algorithm implemented in two places. When
the logic needs to change, one copy will be missed. Extract into a shared
function.

**Naming consistency** — follow the conventions already established in the
codebase. If existing code uses `get_active_users()`, do not introduce
`fetch_enabled_user_list()` for the same concept.

**Dead code** — commented-out blocks, unreachable branches, and unused
variables. They add noise and confuse readers about what the code actually
does.

### Preferred approaches

- Guard clauses to reduce nesting
- Predictable, explicit code over clever shortcuts
- Type annotations as documentation — a function signature with types
  communicates intent more reliably than a docstring that may drift
- Small functions with descriptive names over large functions with
  inline comments

---

## 6. Architecture

Architectural concerns are about whether the change fits the system's
existing structure and principles, not just whether it works in isolation.

### What to review

**Component boundaries** — does this change respect the separation between
modules, apps, and layers? A DocType controller should not directly import
from another app's internal module.

**Coupling** — how many other components does this change depend on, and
how many depend on it? High coupling makes future changes expensive and
increases the blast radius of bugs.

**Extension points** — Frappe applications are designed to be extended
through hooks, overrides, and custom scripts. Verify that the change
preserves these extension mechanisms rather than bypassing them.

**Hook-based integration** — prefer `hooks.py` for cross-app integration
over direct function calls. Hooks allow downstream apps to participate
without tight coupling.

### Patterns to avoid

- **Monkey-patching** — replacing framework methods or class attributes at
  runtime. This is fragile, invisible to other maintainers, and breaks
  when the framework changes.
- **Copy-paste divergence** — copying a function from the framework or
  another app and modifying it locally. When the original is updated,
  the copy falls behind. Use hooks, overrides, or contribute the
  improvement upstream.
- **Implicit dependencies** — relying on import side effects, module-level
  execution, or specific import order. Make dependencies explicit.

---

## 7. API Design

Every public method, whitelisted function, and DocType controller action is
an API surface. Changes to these are expensive to reverse.

### What to review

**Backward compatibility** — existing callers, integrations, and scripts
depend on current behaviour. Changing a return type, renaming a parameter,
or removing a field is a breaking change that affects downstream consumers.

**Parameter ordering** — new parameters should be appended to the end of
the signature as keyword-only arguments with sensible defaults. This
preserves compatibility for callers using positional arguments.

**Migration safety** — adding a mandatory field to an existing DocType
without a patch to populate it on existing records will cause validation
failures site-wide. Schema evolution must include data migration.

**Deprecation discipline** — when retiring an API, provide a deprecation
period with clear warnings, document the replacement, and maintain the
old path for at least one major version cycle.

**Schema evolution pitfalls** — changing a field's type (e.g. Data to Link)
requires a migration patch. Adding a new mandatory field requires a
default value or a data patch. Renaming a field breaks all existing
references (server scripts, print formats, custom reports).

### Patterns to avoid

- Breaking changes without a migration path
- Monkey-patching framework methods to alter API behaviour
- Implicit behaviour changes that are invisible to callers (changing
  the semantics of a return value without changing the signature)

---

## 8. Database Integrity

Database changes are among the hardest to reverse in production. Review
them with extra care.

### What to review

**Migrations and patches** — every schema change needs a corresponding
migration. Patches must be idempotent — safe to run multiple times
without causing errors or duplicate modifications.

**Patch ordering** — patches run in the order they appear in `patches.txt`.
Verify that dependencies between patches are reflected in their ordering.

**Indexing** — indexes must be declared in code (as DocType field properties
or in explicit patches), not applied manually to the database. Manual
indexes are lost when a site is migrated or restored from backup.

**Transactions** — operations that must be atomic should be within a single
transaction. Watch for `frappe.db.commit()` in unexpected places —
each commit ends the current transaction and starts a new one.

**Constraints** — rely on database-level constraints (UNIQUE, NOT NULL,
foreign keys where available) rather than application-level checks. The
database is the last line of defence against invalid data.

### Preferred patterns

- `frappe.get_single_value()` / `frappe.db.set_single_value()` for reading
  and writing Singles (Settings doctypes). These are optimised and cached.
- `frappe.qb` for constructing queries — type-safe, database-agnostic,
  and immune to SQL injection.
- Parameterised queries (`%s` placeholders) when raw SQL is unavoidable.

### Patterns to avoid

- String-interpolated SQL of any kind
- `db.delete()` or `set_value()` where the filter could be `None` or
  empty — this affects every row in the table
- Unsafe filter construction that allows operator injection
- `frappe.db.commit()` inside loops

---

## 9. Testing

Code without tests is a liability. Tests are not overhead — they are the
mechanism that allows future changes to be made with confidence.

### What to review

**Regression coverage** — every bug fix should include a test that
reproduces the original failure and verifies the fix. Without this,
nothing prevents the bug from returning.

**Migration coverage** — patches that modify data should have tests
verifying both the forward migration and the expected end state.

**Fixtures** — test data should be created through fixtures or setup
methods, not assumed to exist in the database. Tests must be independent
of each other and of execution order.

**Deterministic behaviour** — tests that depend on wall clock time,
random values, or external services are flaky by design. Use
`freeze_time` for time-dependent logic, seed random generators, and
mock external service calls.

### Expectations

- Tests pass consistently across runs
- New features have corresponding test coverage
- Bug fixes include regression tests
- Tests clean up after themselves (no test pollution)
- No reliance on test execution order

---

## 10. Observability

When something fails in production, the quality of error messages and
logging determines how quickly the problem is diagnosed and resolved.

### What to review

**Logging quality** — log messages should include enough context to be
useful without reading the source code. Include identifiers (document
name, user, transaction ID) and the operation that failed.

**Exception handling** — preserve the exception chain with
`raise NewError(...) from original_error`. Catching and re-raising
without `from` destroys the original traceback.

**Error message specificity** — a good error message answers three
questions:
1. What happened? (the symptom)
2. Who was affected? (the user, document, or record)
3. What changed? (the operation that triggered the failure)

**Log levels** — use appropriate severity levels. Not every exception
is `ERROR` — expected conditions (user input validation failures,
permission denials) are `WARNING` or `INFO`. Reserve `ERROR` and
`CRITICAL` for genuinely unexpected failures.

**Traceback attribution** — ensure that exceptions surface to a level
where they can be observed. Exceptions caught in a broad `except` block
and logged at `DEBUG` level are effectively invisible.

### Patterns to avoid

- Bare `except:` clauses that swallow all exceptions
- Logging sensitive data (passwords, tokens, personal information)
- Error messages that say "An error occurred" without specifics
- Catching exceptions only to re-raise the same exception without
  additional context
