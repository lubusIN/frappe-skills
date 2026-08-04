# Stage 1 — Audit

A fast surface scan to catch hygiene problems, structural debt, and frontend
inconsistencies before committing to a deep review. If an audit surfaces
critical issues, resolve them before proceeding to Stage 2.

---

## Code Hygiene

Scan for these categories of waste. Each one obscures intent, inflates
maintenance cost, or masks real bugs.

### Dead and duplicate code

- **Duplicate logic** — identical or near-identical blocks across modules.
  Extract shared behaviour into a single source of truth.
- **Dead code** — functions, classes, or branches that are never called.
  Remove them. Version control preserves history.
- **Unused imports and variables** — noise that clutters the namespace and
  confuses readers. Tools like Ruff catch these automatically.
- **Commented-out code** — either restore it or delete it. Comments should
  explain *why*, not preserve abandoned alternatives.

### Debug and temporary artifacts

- **Debug statements** — `print()`, `console.log()`, `debugger`, `breakpoint()`.
  These must never reach production. Search for them explicitly.
- **Temporary files** — scratch scripts, `.bak` files, editor swap files.
  They do not belong in the repository.
- **TODO/FIXME without tracking** — if the fix cannot happen now, create an
  issue. Untracked TODOs accumulate silently.

### Structural complexity

- **Stale tests** — tests that pass but no longer exercise the code they were
  written for. They provide false confidence.
- **Unnecessary wrappers** — functions that delegate to a single call without
  adding value. They obscure the actual operation.
- **Complexity hotspots** — functions with high cyclomatic complexity, deeply
  nested conditionals, or excessive branching. Flag anything over 10 branches
  for potential decomposition.
- **Oversized modules** — files that handle too many concerns. If a module
  requires scrolling through hundreds of lines to understand its purpose,
  it likely needs splitting.

---

## Frontend Review

Frappe applications should use consistent frontend patterns. The audit
checks for deviations from established standards.

### Component architecture

- **Prefer frappe-ui** — use the component library for standard interface
  elements (buttons, dialogs, forms, data tables). Avoid reimplementing
  components that already exist in the library.
- **Reusable components** — extract repeated UI patterns into shared components.
  If the same card layout appears in three views, it should be one component
  used three times.
- **Semantic tokens** — reference design tokens (colours, spacing, typography)
  through semantic names rather than raw values. This enables theming and
  ensures visual consistency.
- **Composition over inheritance** — build complex interfaces by composing
  small, focused components. Avoid deep component hierarchies that are
  difficult to reason about.

### Patterns to avoid

- **Plain HTML for interactive elements** — `<div onclick="...">` instead of
  proper framework components. This breaks accessibility and event handling.
- **Deeply nested DOM structures** — excessive nesting makes styling fragile
  and debugging painful. Flatten where possible.
- **Duplicated components** — two components that do nearly the same thing
  with minor variations. Consolidate and parameterise.
- **Hardcoded colour values** — `#3498db` sprinkled through templates instead
  of referencing theme variables.
- **Inline styling** — `style="margin-top: 12px"` in templates. Move styles
  to CSS classes or utility classes.

---

## Tailwind Review

When the project uses Tailwind CSS, audit for discipline in utility usage.

- **Duplicated class combinations** — the same sequence of utilities repeated
  across multiple elements. Extract into a component or use `@apply` in a
  stylesheet for genuinely shared patterns.
- **Repeated spacing utilities** — inconsistent spacing values (`p-3` in one
  place, `p-4` in another for visually identical spacing). Standardise on a
  spacing scale.
- **Oversized class strings** — elements with 15+ utility classes become
  unreadable. If a class string exceeds a comfortable line length, consider
  extraction.
- **Missing responsive variants** — components that look correct on desktop
  but break on smaller viewports. Verify responsive behaviour.

---

## Dark Mode Review

Theme compatibility is a first-class concern, not an afterthought.

- **Semantic colour tokens** — all colours should reference semantic tokens
  (e.g. `text-gray-900 dark:text-gray-100` or CSS custom properties) rather
  than fixed hex values. Hard-coded colours break under theme changes.
- **Focus states** — interactive elements must have visible focus indicators
  in both light and dark themes. Test keyboard navigation.
- **Hover states** — hover effects should maintain sufficient contrast against
  the current theme background.
- **Contrast ratios** — verify that text remains readable against its
  background in both themes. WCAG AA requires a minimum ratio of 4.5:1 for
  normal text.
- **No raw hex values in templates** — `bg-[#1a1a2e]` in Tailwind or
  `color: #333` in CSS defeats theming entirely. Use the design system.

---

## Observations

These patterns have been identified across projects and should be
checked proactively during audits.

- **Avoid overengineering** — do not introduce abstractions for problems
  that do not yet exist. Solve the current problem clearly.
- **Simplify abstractions** — if an abstraction layer adds indirection without
  adding value, remove it.
- **Remove temporary code** — scaffolding, prototype logic, and feature
  flags for shipped features should be cleaned up.
- **Minimise DOM complexity** — keep the rendered DOM as flat and shallow as
  practical. Deeply nested structures impair performance and debuggability.
- **Explicit type hints** — Python functions should have type annotations on
  parameters and return values. This aids both human readers and static analysis.
- **Translation wrappers** — all user-facing strings should use `_()` for
  internationalisation, even if the application currently targets a single
  language.
