# Sambal: KKT Stationarity Domain Conditioning + Wrong Index Reference

**GitHub Issue:** [#862](https://github.com/jeffreyhorn/nlp2mcp/issues/862)
**Status:** PARTIALLY RESOLVED — Bug 2 fixed, Bug 1 requires architectural AD changes
**Severity:** Medium — Model translates but execution errors abort solve (division by zero)
**Date:** 2026-02-24
**Partially Resolved:** 2026-02-24
**Last Updated:** 2026-03-17
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

### Investigated Fix Approach (2026-03-17)

Analysis confirmed that the AD engine already computes the correct gradient with the dollar
condition embedded as `DollarConditional(1, SetMembershipTest("xw", (i,j)))` multiplied
into the gradient expression. The issue is that `_find_variable_access_condition()` in
`src/kkt/stationarity.py` only scans **constraint equation bodies** for conditions, not the
**objective gradient**. The condition from the objective sum is embedded in the gradient
expression but never extracted to become an equation-level guard.

**Concrete fix path:**
1. Add `_extract_gradient_conditions()` to `src/ad/gradient.py` to scan computed gradients
   for embedded `DollarConditional` nodes
2. Store extracted conditions in `KKTSystem.gradient_conditions: dict[str, Expr | None]`
3. Modify `_find_variable_access_condition()` in `src/kkt/stationarity.py` to also check
   gradient conditions from the objective
4. The existing infrastructure for applying conditions at the equation level already works

**Why not fixed now:** The change spans 3 files (`src/ad/gradient.py`, `src/kkt/kkt_system.py`,
`src/kkt/stationarity.py`) and requires careful testing to ensure no regressions in the
condition-detection pipeline for other models.

---

## Files Changed

| File | Change |
|------|--------|
| `src/kkt/stationarity.py` | Fixed alias-aware index replacement in `_replace_matching_indices` (Bug 2) |

---

## Related Issues

- **Issue #764** (mexss): Similar accounting variable / stationarity conditioning issue
- **Issue #826** (decomp): Related empty stationarity equation issue

---

## Status (2026-04-01)

**Bug 1 (dollar condition) IS now fixed.** The `extract_gradient_conditions` infrastructure was already implemented in a prior sprint and the condition `$(xw(i,j))` is correctly applied to `stat_x(i,j)`.

**New blocker: NA values in stationarity equations.** `stat_t(h1)` has "RHS value NA" — some parameter used in the stationarity equation for `t` has NA values. Additionally, `cbal` equations show infeasibilities. The EXECERROR=2 is from the NA values, not the missing dollar condition.

This is a separate issue from the original Bug 1 — it's related to Issue #986 (NA parameter handling in equations).
