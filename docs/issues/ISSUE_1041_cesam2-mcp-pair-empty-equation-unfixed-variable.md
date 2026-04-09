# cesam2: MCP pair empty equation — associated variable not fixed

**GitHub Issue:** [#1041](https://github.com/jeffreyhorn/nlp2mcp/issues/1041)
**Status:** PARTIALLY FIXED
**Severity:** High — EXECERROR 486 aborts solve
**Date:** 2026-03-10
**Updated:** 2026-03-11
**Affected Models:** cesam2 (and potentially any model with conditioned stationarity equations)

---

## Problem Summary

After fixing Issue #1025 (loop body parameter emission), cesam2 compiles without $141 errors but fails at solve time with 486 MCP pair errors. Four stationarity equations (`stat_a`, `stat_err3`, `stat_tsam`, `stat_w3`) have domain conditions like `$(ii(i) and ii(j))` that exclude certain `(i,j)` pairs (specifically those involving `"Total"`). For excluded instances, the equation is empty, but the paired variable (e.g., `A(i,j)`) is not fixed to 0.

GAMS requires: if an MCP equation is empty for some instance, the paired variable must be fixed for that instance.

---

## Root Cause Analysis

Three distinct bugs were identified and fixed:

### Bug 1: Parser `index_list` in loop body (from Issue #1025)
The parser was incorrectly including `index_list` trees (e.g., `$NONZERO(ii,jj)`) as body statements in loop parsing. This caused parameters like `wbar3` to not be assigned.

### Bug 2: Domain matching for subset/alias in stationarity builder
`_add_indexed_jacobian_terms()` could not match constraint domains using dynamic subsets (e.g., `(ii, jj)`) against variable domains using parent sets (e.g., `(i, j)`). The stationarity builder wrapped these in unnecessary `Sum()` aggregations.

### Bug 3: Set assignment emission ordering (ROOT CAUSE of empty equations)
`NONZERO(ii,jj) = yes$(Abar0(ii,jj))` was emitted **before** `Abar0` was computed, making NONZERO empty at solve time. All constraint equations conditioned on NONZERO/icoeff/ival produced NONE instances.

The root cause was in `emit_interleaved_params_and_sets()` which only detected "set-blocked params" (params with LHS conditions on dynamic sets) but not "index-blocked params" (params referenced by set assignments whose expression keys use dynamic set names or aliases).

---

## Fixes Applied

### 1. `src/ir/parser.py` — Skip `index_list` in loop body
```python
elif child.data == "index_list":
    continue  # Not a body statement
```

### 2. `src/kkt/stationarity.py` — Subset/alias domain matching
Added `_match_subset_domain()` function that matches constraint domain indices to variable domain indices through subset/alias relationships, and `_rewrite_subset_to_superset()` to rewrite index names in expression trees.

### 3. `src/emit/emit_gams.py` — Equality multiplier `.fx` for dynamic subsets
Added section 3b that emits `.fx` statements for equality multipliers whose equation domain uses dynamic subsets:
```gams
nu_SAMCOEF.fx(i,j)$(not (ii(i) and jj(j))) = 0;
```

### 4. `src/emit/original_symbols.py` — Index-blocked param detection
Extended `emit_interleaved_params_and_sets()` to detect "index-blocked params" — parameters referenced by set assignments that are indexed by dynamic set names (including aliases). This ensures proper topological ordering:
1. `ii(i) = 1; ii("Total") = 0;`
2. SAM recomputation
3. `Abar0(ii,jj)` computation
4. `NONZERO(ii,jj) = yes$(Abar0(ii,jj));`
5. `icoeff(ii,acoeff) = yes$(NONZERO(ii,acoeff));`
6. `ival(ii,jj) = yes$(SAM0(ii,jj) and (not icoeff(ii,jj)));`

---

## Results

**Before**: $141 compilation error (never reached solve)

**After (Sprint 23)**: Compiles and reaches solver. 447 equations generated
(up from 167 NONE-affected). 66 unmatched free variables from `stat_tsam`
missing `nu_COLSUM(j)` and `nu_ROWSUM(i)` Jacobian contributions and from
empty diagonal equation instances.

---

## Sprint 24 Update

**Improved:** Empty equation detector (#1133 fix) reduced unmatched from 66 to 4.
The 62 previously unmatched variables from `stat_tsam` / COLSUM / ROWSUM
Jacobian issues were resolved by the static coefficient sparsity analysis
detecting empty equation instances and fixing their multipliers.

The remaining 4 unmatched variables are `ERR3(ACT,ACT)`, `ERR3(FAC,FAC)`,
`ERR3(ENT,ENT)`, and `ERR3(HOU,HOU)`. These are diagonal elements of
`err3(i,j)` where:
- `stat_err3(i,j)` references `err3(j,j)` (diagonal only)
- For diagonal instances like `(ACT,ACT)`, all terms guarded by
  dollar-conditions based on the runtime-computed sets `NONZERO`, `ICOEFF`,
  and `IVAL` evaluate to false because SAM matrices don't have
  self-referencing entries
- The empty equation detector can't prove these are empty because
  `NONZERO`, `ICOEFF`, `IVAL` have no static members at compile time
  (populated via runtime assignment like `NONZERO(ii,jj) = yes$(Abar0(ii,jj))`)

**NOT FIXED** — requires either:
1. Support for evaluating runtime-computed set conditions in the detector
2. Detecting that `err3(j,j)` (same-index-repeated) only contributes to
   equations where the corresponding diagonal condition is active
3. A GAMS-side runtime check that fixes variables for truly empty equations

---

## Files Modified

| File | Change |
|------|--------|
| `src/ir/parser.py` | Skip `index_list` in loop body extraction |
| `src/kkt/stationarity.py` | `_match_subset_domain()`, `_rewrite_subset_to_superset()`, domain matching |
| `src/emit/emit_gams.py` | Section 3b: equality multiplier `.fx` for dynamic subset domains |
| `src/emit/original_symbols.py` | Index-blocked param detection in `emit_interleaved_params_and_sets()` |

---

## Related Issues

- Issue #1025: cesam2 wbar3 loop body parameter unassigned (FIXED)
- Issue #1022: cesam2 $187 errors (FIXED)
- Issue #881: cesam missing dollar conditions
