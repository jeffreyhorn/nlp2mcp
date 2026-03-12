# solveopt: Domain Violation ($171) in Stationarity Equation — Index Mismatch

**GitHub Issue:** [#1053](https://github.com/jeffreyhorn/nlp2mcp/issues/1053)
**Status:** FIXED
**Severity:** High — path_syntax_error, model fails to compile
**Date:** 2026-03-11
**Affected Models:** solveopt (also fixes tforss #1055 domain violation)

---

## Problem Summary

The solveopt model's generated MCP file contains a domain violation in the stationarity equation for `x2`. The equation `stat_x2(i)$(j(i))` references `nu_e2(i)`, but `nu_e2` is declared over domain `j` (a strict subset of `i`). GAMS reports error $171 (Domain violation for set).

---

## Error Details

GAMS compilation error:
```
stat_x2(i)$(j(i)).. nu_e2(i) + piU_x2(i) =E= 0;
                             $171
**** 171  Domain violation for set
```

The variable `nu_e2` is the multiplier for equation `e2(j)`, so it has domain `(j)`. The stationarity equation `stat_x2(i)$(j(i))` is conditioned on `j(i)`, meaning it only activates for `i` elements in `j`. However, the reference `nu_e2(i)` uses index `i` where `j` is expected — this is a domain violation because `i` is the parent set of `j`.

---

## Root Cause

The stationarity equation builder's `_match_subset_domain()` correctly detects that the equation domain `(j)` is a subset of the variable domain `(i)` and rewrites `MultiplierRef("nu_e2", ("j",))` to `MultiplierRef("nu_e2", ("i",))`. However, the multiplier variable `nu_e2` remains declared over `(j)` in the KKT system. GAMS enforces compile-time domain checking, so `nu_e2(i)` is invalid when `nu_e2` is declared over `j`.

---

## Fix

**Approach:** Multiplier domain widening — when the subset rename rewrites multiplier indices from subset to parent set, also widen the multiplier's declared domain to match.

**Files modified:**

1. **`src/kkt/kkt_system.py`**: Added `multiplier_domain_widenings` field to `KKTSystem` to track which multipliers had their domain widened (maps mult_name → (original_domain, widened_domain)).

2. **`src/kkt/stationarity.py`** (in `_add_indexed_jacobian_terms`): After `_rewrite_subset_to_superset()` rewrites the term's indices, also widen the multiplier's declared domain in the `multipliers` dict and record the widening on the KKT system.

3. **`src/emit/emit_gams.py`**: Added section 3c to generate fix statements for widened multipliers. For each widened multiplier, emits `mult.fx(widened_domain)$(not (subset(parent))) = 0;` to fix instances outside the original subset.

**Result:**
- `nu_e2` declared over `(i)` instead of `(j)`
- `nu_e2.fx(i)$(not (j(i))) = 0;` fixes instances outside `j`
- GAMS compiles and solves: MODEL STATUS 1 (Optimal), objective = 6.000 (matches NLP)

**Tests added:**
- Unit test: `test_rewrite_multiplierref_indices` in `test_stationarity_subset_domain.py`
- Integration test: `test_solveopt_multiplier_declared_over_parent_set` in `test_fx_complementarity.py`

---

## Verification

```bash
python -m src.cli data/gamslib/raw/solveopt.gms -o /tmp/solveopt_mcp.gms
gams /tmp/solveopt_mcp.gms lo=2
# SOLVER STATUS 1 Normal Completion
# MODEL STATUS 1 Optimal
# nlp2mcp_obj_val = 6.000 (matches NLP)
```
