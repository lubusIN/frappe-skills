---
name: code-review
description: >-
  Progressive code review for Frappe applications — three stages from quick
  audit to deep structural review to strict automated validation. Grounded
  in Frappe engineering principles and Lubus development standards across
  correctness, security, performance, and maintainability.
---

# Code Review

A progressive review system for Frappe applications. Three stages of increasing
depth, each designed to catch a different class of problem.

## Philosophy

Every review exists to protect four things, in this order of priority:

1. **Users** — their data, their trust, their experience
2. **Data integrity** — correctness of state across documents, ledgers, and linked records
3. **Future maintainers** — the developer who inherits this code in two years
4. **Application stability** — predictable behaviour under load, error, and edge conditions

Optimise for correctness first, then security, then maintainability, then
consistency, then predictability, then simplicity, then backward compatibility.

Root-cause fixes over workarounds. Every finding should explain *why* it
matters — what breaks, for whom, and under what conditions.

---

## Review Stages

### Stage 1 — Audit

A fast surface-level scan. The goal is to discover obvious hygiene problems
before investing time in a deep review.

What to look for:

- Duplicate logic, dead code, unused imports and variables
- Commented-out code, debug statements, temporary files
- Stale tests and unnecessary wrapper functions
- Complexity hotspots and oversized modules
- Frontend hygiene (frappe-ui usage, component reuse, DOM depth)
- Tailwind discipline (class duplication, extraction opportunities)
- Dark mode and theme compatibility

→ Full guidance: [references/audit.md](references/audit.md)

---

### Stage 2 — Code Review

A thorough structural review. Work through these ten dimensions in order —
the sequence reflects consequence severity, not time spent.

| Priority | Dimension | Core question |
|----------|-----------|---------------|
| 1 | Correctness | Does this produce the right result in every case? |
| 2 | Security | Can this be exploited or abused? |
| 3 | Performance | Will this remain fast at production scale? |
| 4 | Concurrency | Is this safe under parallel execution? |
| 5 | Readability | Can someone unfamiliar understand this quickly? |
| 6 | Architecture | Does this fit the system's structure and boundaries? |
| 7 | API design | Is this interface stable and backward-compatible? |
| 8 | Database integrity | Are schema changes, queries, and transactions safe? |
| 9 | Testing | Is this change adequately covered by tests? |
| 10 | Observability | Will operators know when this fails and why? |

Spend the most attention on the first two. Correctness and security problems
are the most expensive to fix after they ship.

→ Full guidance: [references/code-review.md](references/code-review.md)

---

### Stage 3 — Strict Validation

Run **only when explicitly requested**. This stage involves executing tooling
and running test suites — it is not part of the default review workflow.

What it covers:

- Static analysis (Ruff, pre-commit, Semgrep, pip-audit)
- Compatibility validation (Python, Node, Bench, Redis, MariaDB, Frappe versions)
- Infrastructure review (pyproject.toml, hooks.py, workflows, dependency ranges)
- Test execution (unit, integration, regression suites)

→ Full guidance: [references/automated-checks.md](references/automated-checks.md)

---

## Agent Behaviour

Follow these guidelines when executing a review:

1. **Target Working Tree:** Always restrict your review to the user's staged/unstaged git changes unless instructed otherwise. Do not scan the entire codebase.
2. **Default to Static Analysis:** For generic requests like "audit", "review", or "check", perform **Stage 1** or **Stage 2** on the modified files.
3. **Avoid Stage 3:** Never run automated tests or tools (Stage 3) unless explicitly requested (e.g., "run tests" or "strict validation").
4. **Offer Options:** If a request is ambiguous, ask the user to choose their desired depth: Audit, Code Review, Strict Validation, or a **Full Review (All Stages)**.
5. **Report:** Group findings by severity (critical, warning, suggestion) and propose concrete, actionable improvements.

If the user asks for "a review" without specifying a stage, default to offering
the choice. Do not assume the deepest level is always appropriate.

---

## Quick Reference

→ [references/review-checklist.md](references/review-checklist.md) — condensed
checklist for rapid scanning during reviews.

## References

- [references/audit.md](references/audit.md) — Stage 1 audit criteria
- [references/code-review.md](references/code-review.md) — Stage 2 review dimensions
- [references/automated-checks.md](references/automated-checks.md) — Stage 3 tooling and validation
- [references/review-checklist.md](references/review-checklist.md) — Quick-reference checklist
