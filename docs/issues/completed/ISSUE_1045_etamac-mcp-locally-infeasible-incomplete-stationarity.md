# etamac: MCP Locally Infeasible — Incomplete Stationarity for Lead/Lag Variables

**GitHub Issue:** [#1045](https://github.com/jeffreyhorn/nlp2mcp/issues/1045)
**Status:** Fixed
**Severity:** Medium — Model translates and solver runs, but PATH reports locally infeasible
**Date:** 2026-03-11
**Fixed:** 2026-03-11
**Affected Models:** etamac, himmel16 (also improved)

---

## Problem Summary

After fixing the structural MCP errors (#984 domain errors, #1043 unmatched equations), the etamac model now reaches the PATH solver but reports **Locally Infeasible** (model status 5, solver status 1). PATH runs 5,682 iterations but cannot converge. The largest infeasibility is at `stat_k('2010')` with a normal map residual of 15.362.

---

## Root Cause

The stationarity equation `stat_k(t)` is **incomplete** — it only captures the Jacobian contribution from `totalcap(t)` with respect to `k(t)`, but misses the contribution from `totalcap(t-1)` with respect to `k(t)` via the lead/lag offset `k(t+1)`.

### The Capital Accumulation Constraint

```gams
totalcap(t)$(ord(t) <= card(t) - 1).. k(t+1) =E= k(t) * spda ** nyper + kn(t+1);
```

This constraint creates two Jacobian entries for variable `k(t)`:
1. `∂totalcap(t)/∂k(t) = -spda^nyper` — from the `k(t)` term on the RHS
2. `∂totalcap(t-1)/∂k(t) = 1` — because `totalcap(t-1)` references `k((t-1)+1) = k(t)` on the LHS

### Why This Happened

The Jacobian computation pipeline had two gaps for lead/lag variable references:

1. **`_substitute_indices()` didn't handle IndexOffset nodes**: When substituting symbolic indices with concrete values (e.g., `t` → `"1990"`), the function only handled plain string indices. `IndexOffset` nodes like `IndexOffset("t", Const(1), False)` (representing `t+1`) passed through unchanged, so `k(t+1)` became `k(IndexOffset("t", Const(1), False))` instead of `k(IndexOffset("1990", Const(1), False))`.

2. **No resolution of IndexOffset to concrete domain elements**: Even after substitution, `k(IndexOffset("1990", 1))` couldn't match the variable column `k("1995")` because `IndexOffset != string`. The system needed to resolve IndexOffset to the actual domain element (e.g., look up "1990" in the time set, add 1 position, get "1995").

3. **Stationarity assembly used only one Jacobian pattern per constraint**: When multiple entries for the same constraint-variable pair had different index offset patterns (e.g., `totalcap(t)→k(t)` with offset 0 and `totalcap(t-1)→k(t)` with offset -1), only the first pattern was used.

---

## Fix Applied

Three-part fix across the Jacobian computation and stationarity assembly pipeline:

### Part 1: `_substitute_indices()` IndexOffset handling (`constraint_jacobian.py`)

Added `_sub_idx()` helper that handles both plain string indices and IndexOffset nodes:
- For `IndexOffset`, substitutes the `base` field while preserving `offset` and `circular` flags
- Example: `k(IndexOffset("t", 1))` with `t→"1990"` becomes `k(IndexOffset("1990", 1))`

### Part 2: `_resolve_index_offsets()` function (`constraint_jacobian.py`)

New function that walks expression trees and resolves IndexOffset nodes to concrete domain elements:
- Looks up the domain set for each VarRef/ParamRef
- Finds the base element's position in the domain
- Computes position + offset to get the target element
- Out-of-bounds offsets → `Const(0)` (GAMS convention)
- Supports circular wrapping for `++` operator
- Called after `_substitute_indices` in both equality and inequality Jacobian computation

### Part 3: Stationarity assembly offset sub-grouping (`stationarity.py`)

Modified `_add_indexed_jacobian_terms()` to sub-group Jacobian entries by index offset pattern:
- `_compute_index_offset_key()` — computes positional offset between equation and variable indices (only for same underlying domain sets)
- `_build_offset_multiplier()` — builds MultiplierRef with IndexOffset indices for shifted multipliers (e.g., `nu_totalcap(t-1)`)
- `_build_offset_guard()` — builds boundary guard conditions (e.g., `$(ord(t) > 1)` for lag terms)
- Each offset pattern gets its own multiplier term in the stationarity equation

### Part 4: MultiplierRef exclusion from lead/lag scan (`equations.py`)

Excluded `MultiplierRef` from the lead/lag restriction scan in `_has_lead_lag_refs()`. This prevents equation-level `$(ord(t) > 1)` conditions from being incorrectly applied to entire stationarity equations — the boundary guard is now on the individual offset term instead.

---

## Result After Fix

### etamac: Optimal

```
SOLVER STATUS     1 Normal Completion
MODEL STATUS      1 Optimal

FINAL STATISTICS
Inf-Norm of Complementarity . .  0.0000e+00 eqn: (stat_c('1990'))
Inf-Norm of Normal Map. . . . .  0.0000e+00 eqn: (stat_c('1990'))
Inf-Norm of Minimum Map . . . .  0.0000e+00 eqn: (stat_c('1990'))

251 row/cols, 625 non-zeros
2 iterations
```

### Corrected Stationarity Equation

```gams
stat_k(t).. (-spda^nyper) * nu_totalcap(t) + nu_totalcap(t-1)$(ord(t) > 1)
            + sum(tlast, (grow(tlast) + 1 - spda) * lam_tc(tlast)) - piL_k(t) =E= 0;
```

The `nu_totalcap(t-1)$(ord(t) > 1)` term is now correctly included with a boundary guard.

### himmel16: Also improved

The fix also corrected the himmel16 model (circular lead/lag via `++` operator). The objective value changed from ~0 (incorrect) to 0.385 (correct maximum hexagon area).

---

## Verification

- All 4,125 tests pass (10 skipped, 1 xfailed)
- Quality gate: typecheck, lint, format all pass
- Full pipeline regression: no outcome changes (66 success, 70 failure)
- etamac: model_infeasible → model_optimal

---

## Files Modified

- `src/ad/constraint_jacobian.py` — `_sub_idx()` helper, `_resolve_index_offsets()` function, calls in equality/inequality Jacobian computation
- `src/kkt/stationarity.py` — `_compute_index_offset_key()`, `_build_offset_multiplier()`, `_build_offset_guard()`, offset sub-grouping in `_add_indexed_jacobian_terms()`
- `src/emit/equations.py` — Excluded MultiplierRef from lead/lag restriction scan
- `tests/unit/ad/test_index_offset_ad.py` — 18 new tests (TestSubstituteIndicesIndexOffset, TestResolveIndexOffsets)
- `tests/e2e/test_gamslib_match.py` — Updated himmel16 reference value
- `data/gamslib/mcp/etamac_mcp.gms` — Regenerated with fix

---

## Related Issues

- #984 — etamac domain errors (division by zero, log(0)) — FIXED
- #1043 — etamac unmatched totalcap equations — FIXED (IndexOffset subset detection)
- #763 — AD propagation for lead/lag expressions — RESOLVED by this fix
