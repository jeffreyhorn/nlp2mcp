# camcge: Stationarity Equations Missing Subset Conditioning

**GitHub Issue:** [#871](https://github.com/jeffreyhorn/nlp2mcp/issues/871)
**Status:** PARTIALLY FIXED
**Severity:** High — Model compiles but PATH solver aborts with execution errors (division by zero)
**Date:** 2026-02-24
**Affected Models:** camcge
**Partial Fix:** 2026-02-25

---

## Problem Summary

The camcge MCP model compiles without syntax errors (after Issue #860 fixes), but the PATH
solver aborts with 5 execution errors due to division by zero in stationarity equations.
The root cause is that stationarity equations are generated over the full domain `i` (all 11
sectors) when the original constraint equations are only defined over a subset `it(i)` (9
traded sectors). Non-traded sectors (`services`, `publiques`) have zero-valued parameters
(`e0=0`, `m0=0`) that appear in denominators of the differentiated expressions.

---

## Partial Fix Applied (5 errors → 1 error)

### 1. DollarConditional subset detection (src/kkt/stationarity.py)

Extended `_find_variable_subset_condition()` to detect subset restrictions from
`DollarConditional` nodes. When a variable like `e(i)` is accessed as `(pe(i)*e(i))$it(i)`,
the `$it(i)` condition now propagates through the walk — the access is treated as restricted
to `it` rather than full-domain.

Added `dollar_subsets` parameter to `_walk_expr()` that maps domain indices to their
restricting subset when inside a DollarConditional. When `actual_lower == decl_lower` but
a dollar subset restriction exists, the access is recorded as a subset access.

### 2. DollarConditional handling in access condition detection (src/kkt/stationarity.py)

Extended `_collect_access_conditions()` to recognize `DollarConditional` as a condition-
guarding construct (similar to conditioned `Sum`/`Prod`). When a variable is found inside
a `DollarConditional` whose condition references relevant domain indices, the condition
is captured as a guarding condition.

### Results

The fix correctly detects and applies stationarity conditions for 7 variables:
- `e`, `m`, `pe`, `pm`, `pwe`, `pwm`, `tm` — all conditioned on `it(i)`

Execution errors reduced from **5 to 1**.

---

## Remaining Issue (1 execution error)

### `stat_pd(services)` — division by zero at line 456

The remaining error is NOT a subset conditioning issue. Variable `pd(i)` is genuinely
referenced in equations over the full domain (`absorption(i)`, `sales(i)`) so its
stationarity equation correctly covers all `i`.

The bug is a **Jacobian domain index propagation issue**: in the stationarity equation
`stat_pd(i)`, the Jacobian terms from `esupply(it)` contain `rhot(i)` instead of `rhot(it)`.
The equation `esupply(it)` uses `rhot(it)`, but when the derivative is wrapped in
`sum(it, ...)` for the stationarity equation, the parameter reference `rhot` incorrectly
uses the outer domain `i` instead of the inner sum index `it`.

This causes `rhot(services) - 1` in a denominator, and since `rhot(services) - 1 ≈ 0`
(or creates a degenerate expression), GAMS reports division by zero.

**This requires a separate fix** in the AD/Jacobian domain remapping system to properly
propagate the equation domain index into derivative expressions when they are wrapped
in stationarity sums.

---

## Related Issues

- **Issue #862** (sambal): Same class of issue — dollar condition from sum not propagated
- **Issue #764** (mexss): Accounting variable stationarity conditioning
- **Issue #826** (decomp): Empty stationarity equation from domain issues
- **NEW**: Jacobian domain index propagation bug (rhot(i) vs rhot(it) in stationarity sums)

---

## Progress (2026-04-01)

**$141 fix:** Added explicit zero assignments for parameters with all-zero values (e.g., `te(i) = 0;`). Issue #967's sparse zero skip caused these to be declared without any data/assignments. camcge now compiles cleanly (0 compilation errors).

**Remaining:** EXECERROR=4 at runtime (division by zero in stationarity equations). The earlier partial fix reduced exec errors from 5 to 1 by adding subset conditioning; this count may differ from the current run due to additional code changes since then (domain widening, etc.). The root cause remains the `rhot(i)` vs `rhot(it)` Jacobian domain index propagation issue documented above.
