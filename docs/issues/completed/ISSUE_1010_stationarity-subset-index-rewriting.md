# Stationarity gradient: rewrite subset indices to controlled domain with membership guard

**GitHub Issue:** [#1010](https://github.com/jeffreyhorn/nlp2mcp/issues/1010)
**Status:** FIXED
**Model:** robert (GAMSlib) and similar subset-index patterns
**Component:** `src/kkt/stationarity.py` — `_build_indexed_stationarity_expr()`
**Related PR:** #1006 (Copilot review comments on lines 920 and 105)

## Description

When a variable is declared over a superset (e.g., `x(p,tt)`) but the objective references it via a subset index (e.g., `x(p,t)` where `t(tt)`), the gradient term contains the subset index `t` which is uncontrolled in the stationarity equation `stat_x(p,tt)`.

The previous fix (PR #1006 / Issue #949) wrapped the gradient in `Sum(t, ...)`, producing:

```gams
stat_x(p,tt)$(t(tt)).. sum(t, (-1) * c(p,t)) + ... =E= 0;
```

This made the gradient term **constant across all `tt`** — `sum(t, c(p,t))` evaluated to the same value regardless of which `tt` element the stationarity equation was instantiated for.

## Fix Applied

Instead of an unconditional Sum or direct index rewriting (which causes GAMS $171 domain violations when the parameter is declared over the subset), the fix wraps in `sum(t$(sameas(t,tt)), ...)`:

```gams
stat_x(p,tt)$(t(tt)).. sum(t$(sameas(t, tt)), ((-1) * c(p,t))) + ... =E= 0;
```

The `sameas(t,tt)` condition selects only the `t` element matching the current `tt`, preserving per-element gradient semantics while keeping `c(p,t)` in its declared domain.

### Why direct rewriting doesn't work

The original issue doc proposed replacing `c(p,t)` with `c(p,tt)`. This fails because `c` is declared over `(p,t)` and GAMS performs static domain checking — `c(p,tt)` is a $171 domain violation since `tt` is not a subset of `t`.

### Implementation

1. **`_find_superset_in_domain()`** — New helper that checks if an uncontrolled index is a subset of any variable domain index, following `SetDef.domain` and alias resolution.

2. **`_rewrite_subset_to_superset()`** — Added but ultimately not used for the primary fix (retained for potential future use with domain-relaxed parameters).

3. **`_build_indexed_stationarity_expr()`** — Modified to wrap gradient in `Sum((idx,), expr, condition=Call("sameas", (SymbolRef(idx), SymbolRef(superset))))` when a subset→superset mapping exists. Falls back to unconditional Sum wrapping when no mapping exists.

4. **Test updated** — `test_subset_index_in_gradient_rewritten_to_superset` now asserts the presence of `Sum(t$(sameas(t,tt)), ...)` instead of `Sum(t, ...)`.

### Verification

- robert: Compiles and solves OPTIMAL (Solver Status 1, Model Status 1)
- dyncge, korcge, paklive, tabora: No regressions (same pre-existing errors)
- All 3961 tests pass

## Related Issues

- #949 — Original uncontrolled set index issue (GAMS Error $149)
- PR #1006 — Previous Sum-wrapping fix with Copilot review identifying this improvement
