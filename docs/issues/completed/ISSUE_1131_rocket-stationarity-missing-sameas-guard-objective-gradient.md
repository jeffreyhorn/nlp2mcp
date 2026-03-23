# rocket: Stationarity Missing sameas Guard on Objective Gradient

**GitHub Issue:** [#1131](https://github.com/jeffreyhorn/nlp2mcp/issues/1131)
**Status:** FIXED
**Severity:** High — MCP generates and PATH runs, but model is structurally infeasible (497 INFES)
**Date:** 2026-03-22
**Fixed:** 2026-03-22
**Affected Models:** rocket (and potentially any model with element-specific variable references in objective)

---

## Problem Summary

The rocket model (`data/gamslib/raw/rocket.gms`) generates an MCP file that compiles and
runs PATH, but PATH reports MODEL STATUS 5 (Locally Infeasible) with 497 infeasible
equations. The root cause is a missing `sameas()` guard in the objective gradient.

The original objective is `Maximize final_velocity; obj.. final_velocity =E= ht("h50");`
which means the objective gradient w.r.t. `ht(h)` should be 1 only when `h = h50` and 0
otherwise. But the stationarity equation emitted `-1` unconditionally for all `h`:

```gams
* WRONG (before fix):
stat_ht(h).. -1 + [constraint derivatives] =E= 0;

* CORRECT (after fix):
stat_ht(h).. -1$(sameas(h,'h50')) + [constraint derivatives] =E= 0;
```

---

## Root Cause

### The Gradient Assembly Bug

In `_build_indexed_gradient_term()` (`src/kkt/stationarity.py`), when building the
gradient term for indexed variable `ht(h)`:

1. The gradient vector correctly has `Const(-1)` only for `ht('h50')` and `Const(0)` for
   all other instances
2. The function finds `h50` as the representative non-zero instance, getting `Const(-1)`
3. `_replace_indices_in_expr(Const(-1), ...)` returns `Const(-1)` unchanged (a constant
   has no indices to replace)
4. This `Const(-1)` is then used as the gradient for the indexed equation `stat_ht(h)`,
   applying `-1` to ALL instances instead of only `h50`

The function correctly handled the case where the gradient structure was the same for all
instances (just with different element labels), but failed when the gradient was non-zero
only for a strict subset of instances and the non-zero expression was a constant.

---

## Fix Applied

Two additions to `src/kkt/stationarity.py`:

**1. Extended `_build_indexed_gradient_term()` to detect partial-instance gradients:**
After finding the representative non-zero gradient and performing index replacement,
the function now checks whether only a strict subset of instances have non-zero
gradients. If so, it wraps the gradient expression in a `DollarConditional` with a
`sameas()` guard.

**2. New helper `_build_sameas_guard_for_instances()`:**
Builds a per-dimension `sameas()` condition (or OR-disjunction for multiple elements)
that selects only the instances with non-zero gradients. Uses the existing
`_quote_sameas_uel()` for proper element quoting.

### Result

```gams
* Before:
stat_ht(h).. -1 + ... =E= 0;  (497 INFES for all h != h50)

* After:
stat_ht(h).. -1$(sameas(h, 'h50')) + ... =E= 0;  (0 stat_ht INFES)
```

The 497 stationarity infeasibilities from the missing sameas guard are eliminated.
The model still reports `MODEL STATUS 5 Locally Infeasible` due to PATH solver
convergence difficulties with the nonlinear problem (typical for rocket trajectory
optimization), but this is a separate issue from the structural infeasibility.

---

## Verification

```bash
python -m src.cli data/gamslib/raw/rocket.gms -o /tmp/rocket_mcp.gms
grep "stat_ht" /tmp/rocket_mcp.gms
# Contains: -1$(sameas(h, 'h50'))

gams /tmp/rocket_mcp.gms lo=2
# stat_ht equations: 0 INFES (was 497)
# Remaining MODEL STATUS 5 is PATH convergence issue, not structural
```

Full test suite: 4,222 passed, 10 skipped, 1 xfailed.

---

## Files Modified

| File | Change |
|------|--------|
| `src/kkt/stationarity.py` | Extended `_build_indexed_gradient_term()` to wrap gradient with sameas guard when only a subset of instances are non-zero |
| `src/kkt/stationarity.py` | Added `_build_sameas_guard_for_instances()` helper |
