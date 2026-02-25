# Sambal: KKT Stationarity Domain Conditioning + Wrong Index Reference

**GitHub Issue:** [#862](https://github.com/jeffreyhorn/nlp2mcp/issues/862)
**Status:** PARTIALLY RESOLVED
**Severity:** Medium — Model translates but PATH solver aborts (path_solve_terminated)
**Date:** 2026-02-24
**Partially Resolved:** 2026-02-24
**Affected Models:** sambal

---

## Problem Summary

The sambal model parses and translates to MCP, but the PATH solver aborts with 15 execution
errors. Two distinct KKT/stationarity builder bugs are present: (1) stationarity equations
are not conditioned on the original equation's domain filter, causing division by zero, and
(2) an incorrect index reference (`x(i,i)` instead of `x(i,j)`) in the stationarity
equation.

---

## Resolution

### Bug 2 (Wrong Index Reference): FIXED

The `x(i,i)` bug was caused by `_build_element_to_set_mapping` losing position information
when the same element appears at multiple positions of a variable with aliased domains.

For sambal, `x(i,j)` where `j` aliases `i` means instance `x("h1","h1")` maps both
positions to set `i` (first-wins in the dict), losing the `j` mapping for position 1.

**Fix:** In `_replace_matching_indices`, when the mapped set from `element_to_set` differs
from the `declared_domain` target at a given position AND they share the same alias root,
use the declared domain's set name to preserve positional semantics. This is guarded to
only apply in the gradient path (plain dict), not the Jacobian path (ChainMap with
position-specific overrides).

**Result:** `stat_x(i,j)` now correctly references `x(i,j)` instead of `x(i,i)`.

### Bug 1 (Dollar Condition Not Propagated): NOT FIXED

The stationarity equation `stat_x(i,j)` is not conditioned on `$xw(i,j)`, which was the
dollar condition inside `sum((i,j)$xw(i,j), ...)` in the objective. This causes:
- Division by zero for `(i,j)` pairs where `xb(i,j) = 0` (line 85)
- 13 empty MCP pair warnings for unconditioned instances

**Root cause:** The AD differentiation collapses the sum and loses the dollar condition.
The stationarity builder has no mechanism to detect and propagate conditions from
collapsed sum expressions in the objective to the generated stationarity equations.

**What must be done before fixing Bug 1:**
1. During AD sum collapse (`_diff_sum` in `derivative_rules.py`), detect and preserve
   the sum's dollar condition
2. Propagate the preserved condition back through `_build_indexed_gradient_term` to
   `build_stationarity_equations`
3. Apply the condition to the stationarity equation and fix variables for excluded instances
4. This is an architectural enhancement affecting the AD → stationarity pipeline

**Effort estimate:** ~4-6h for Bug 1

---

## Files Changed

| File | Change |
|------|--------|
| `src/kkt/stationarity.py` | Fixed alias-aware index replacement in `_replace_matching_indices` (Bug 2) |

---

## Related Issues

- **Issue #764** (mexss): Similar accounting variable / stationarity conditioning issue
- **Issue #826** (decomp): Related empty stationarity equation issue
