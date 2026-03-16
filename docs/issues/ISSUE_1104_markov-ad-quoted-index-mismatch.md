# markov: Objective Mismatch — AD Quoted-Index Literal Causes Missing Inequality Constraint

**GitHub Issue:** [#1104](https://github.com/jeffreyhorn/nlp2mcp/issues/1104)
**Status:** PARTIALLY FIXED
**Model:** markov (GAMSlib SEQ=82)
**Error category:** `objective_mismatch`
**MCP objective:** 2571.794 (unchanged — blocked by secondary issue)
**NLP objective:** 2401.577
**Absolute difference:** 170.2

## Description

The markov model (Strategic Petroleum Reserve) is a verified-convex LP that translates and solves to MODEL STATUS 1 (Optimal), but the MCP objective is 170 higher than the NLP reference. Two issues contribute:

1. **Primary (FIXED):** The `equil` inequality constraint was entirely missing from the generated MCP due to an AD differentiation bug involving quoted string literals in variable indices.
2. **Secondary (REMAINING):** The `constr` equation's contribution to `stat_z` has incorrect index lifting in the dimension-mismatch path. The parameter `pi(s,i,sp,j,spp)` gets its constraint-domain indices `(sp,j)` collapsed to variable-domain names `(s,i)`, producing `pi(s,i,s,i,spp)` instead of correctly summing over independent constraint domain indices.

## Primary Fix: AD Quoted-Index Normalization

**Root cause:** The `equil` constraint uses `z(s,"disrupted",spp)` where `"disrupted"` (with embedded quotes) is a VarRef index. When the AD system enumerates variable instances via set members, it uses the unquoted form `'disrupted'`. The exact tuple comparison in `_diff_varref()` failed, making the entire inequality Jacobian empty.

**Fix applied:** Added `_strip_quotes()` and `_indices_match()` helper functions in `src/ad/derivative_rules.py`. The `_indices_match()` function normalizes string indices by stripping surrounding quotes and comparing case-insensitively before checking equality.

**File changed:** `src/ad/derivative_rules.py`
- Added `_strip_quotes(s)`: strips surrounding single/double quotes from a string
- Added `_indices_match(a, b)`: compares index tuples with quote normalization
- Changed `_diff_varref()` line 274 from `expr.indices == wrt_indices` to `_indices_match(expr.indices, wrt_indices)`

**Verification:** After fix, `grep -c 'lam_equil' /tmp/markov_mcp.gms` returns 5 (was 0 before). The `equil` constraint and its complementarity pair are now present in the MCP.

## Secondary Issue: Stationarity Index Lifting for `constr` (REMAINING)

The `constr(sp,j)` equation sums over `z(s,i,sp)` via `pi(s,i,sp,j,spp)`. Variable `z` has domain `('s','i','sp')` (3D) while `constr` has domain `('sp','j')` (2D). This is a dimension-mismatch case in `_add_indexed_jacobian_terms()`.

The problem: `sp` is an alias of `s`, and `j` is an alias of `i`. When `_replace_indices_in_expr` maps concrete element values back to domain names, elements from constraint-domain positions get mapped to variable-domain names (since they share the same alias root). This produces `pi(s,i,s,i,spp)` instead of the correct form that sums over independent constraint indices.

**Correct stationarity for `stat_z(s,i,sp)`:**
```gams
stat_z(s,i,sp).. c(s,sp,i) + nu_constr(s,i) + sum((sp2,j), -b * pi(s,i,sp2,j,sp) * nu_constr(sp2,j))
                 + (ord(sp) - ord(s)) * lam_equil(s,sp) - piL_z(s,i,sp) =E= 0;
```

**Current (incorrect) output:**
```gams
stat_z(s,i,sp).. c(s,sp,i) + sum(spp, (1 - b * pi(s,i,s,i,spp)) * nu_constr(s,i))
                 + (ord(sp) - ord(s)) * lam_equil(s,sp) - piL_z(s,i,sp) =E= 0;
```

**Why this blocks progress:** Even with `equil` now present, the incorrect `constr` stationarity dominates the solution, so the MCP objective remains at 2571.794.

**Root cause location:** `src/kkt/stationarity.py`, dimension-mismatch branch of `_add_indexed_jacobian_terms()` (lines ~2634-2680). The `constraint_element_to_set` mapping maps elements from aliased constraint-domain sets back to the variable domain names when they share the same alias root. A fix would need to distinguish "this element is from the constraint-domain position `sp`" from "this element is from the variable-domain position `s`" even when `sp` and `s` resolve to the same root set.

## What Must Be Done Before Attempting Another Fix

1. The secondary stationarity index lifting issue requires redesigning how `_replace_indices_in_expr` handles element-to-set mapping when constraint and variable domains contain aliased sets that resolve to the same root. The current approach of mapping concrete elements to set names is fundamentally ambiguous when multiple domain positions use aliased sets.

2. A possible approach: instead of mapping elements to set names, map element *positions* to domain names. For example, the element at position 0 of `pi(s,i,sp,j,spp)` maps to the 1st Jacobian variable-domain name, position 1 to the 2nd, etc. This would require tracking positional information through the differentiation and index replacement pipeline.

3. Estimated effort: 3-5h. This is a deep change in the stationarity builder's dimension-mismatch path.

## Related Issues

- #1099 (marco): Similar quoted-literal index issue in stationarity, fixed for parameter refs but not AD
- #914 (markov): Previous issue was uninitialized `pi` parameter (RESOLVED)
