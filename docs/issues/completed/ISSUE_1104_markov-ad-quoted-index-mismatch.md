# markov: Objective Mismatch — AD Quoted-Index Literal + Stationarity Index Lifting

**GitHub Issue:** [#1104](https://github.com/jeffreyhorn/nlp2mcp/issues/1104)
**Status:** FIXED (both primary and secondary issues resolved)
**Model:** markov (GAMSlib SEQ=82)
**Error category:** `objective_mismatch` (was 170.2 absolute difference)
**NLP objective:** 2401.577

## Description

The markov model (Strategic Petroleum Reserve) is a verified-convex LP that translates and solves to MODEL STATUS 1 (Optimal), but the MCP objective was 170 higher than the NLP reference. Two issues contributed:

1. **Primary (FIXED):** The `equil` inequality constraint was entirely missing from the generated MCP due to an AD differentiation bug involving quoted string literals in variable indices.
2. **Secondary (FIXED):** The `constr` equation's contribution to `stat_z` had incorrect index lifting in the dimension-mismatch path. The parameter `pi(s,i,sp,j,spp)` had its constraint-domain indices collapsed to variable-domain names.

## Primary Fix: AD Quoted-Index Normalization

**Root cause:** The `equil` constraint uses `z(s,"disrupted",spp)` where `"disrupted"` (with embedded quotes) is a VarRef index. When the AD system enumerates variable instances via set members, it uses the unquoted form `'disrupted'`. The exact tuple comparison in `_diff_varref()` failed, making the entire inequality Jacobian empty.

**Fix applied:** Added `_strip_quotes()` and `_indices_match()` helper functions in `src/ad/derivative_rules.py`. The `_indices_match()` function normalizes string indices by stripping surrounding quotes and comparing case-insensitively before checking equality.

**File changed:** `src/ad/derivative_rules.py`
- Added `_strip_quotes(s)`: strips surrounding single/double quotes from a string
- Added `_indices_match(a, b)`: compares index tuples with quote normalization
- Changed `_diff_varref()` line 274 from `expr.indices == wrt_indices` to `_indices_match(expr.indices, wrt_indices)`

## Secondary Fix: Dimension-Mismatch Alias Collision in Stationarity

**Root cause:** When `constr(sp,j)` (2D) contributes to `stat_z(s,i,sp)` (3D), this is a dimension-mismatch case. The constraint-domain indices `sp` and `j` are aliases of variable-domain indices `s` and `i`. The `_match_subset_domain()` function returned a rename map `{sp→s, j→i}`, and `_rewrite_subset_to_superset()` blindly renamed ALL occurrences of `sp` and `j` in the expression — including the constraint-domain names inside `pi(s,i,sp,j,spp)` which represent independent iteration variables, not the variable's indices. This produced `pi(s,i,s,i,spp)` instead of the correct form.

**Fix applied:** Added dimension-mismatch-aware handling in `src/kkt/stationarity.py`:

1. **Detection**: After `_match_subset_domain()` returns an alias-only rename map for a dimension-mismatch case, check whether any renamed mult_domain index appears as a FREE index in the derivative expression. If yes, the standard rename would corrupt the derivative.

2. **Fresh alias generation**: For colliding indices, create fresh aliases (e.g., `s__kkt1` as `Alias(s, s__kkt1)`) via the new `_get_or_create_fresh_alias()` helper. This avoids GAMS variable shadowing in `sum()` expressions.

3. **Alias fix for unmatched positions**: Parameters with `prefer_declared_domain=True` may have alias-domain names (e.g., `spp`) at positions that should map to the variable domain. These are renamed to the correct variable domain name (e.g., `spp → sp`).

4. **Sum wrapping**: Independent constraint-domain indices are wrapped in a `Sum()` node.

**Files changed:** `src/kkt/stationarity.py`
- Added `_get_or_create_fresh_alias()` helper (~line 1895)
- Modified `_add_indexed_jacobian_terms()` dimension-mismatch branch (~lines 2790-2880)
- Added `AliasDef` import

**Before fix:**
```gams
stat_z(s,i,sp).. c(s,sp,i) + sum(spp, (1 - b * pi(s,i,s,i,spp)) * nu_constr(s,i))
                 + (ord(sp) - ord(s)) * lam_equil(s,sp) - piL_z(s,i,sp) =E= 0;
```

**After fix:**
```gams
stat_z(s,i,sp).. c(s,sp,i) + sum((s__kkt1,j), (1 - b * pi(s,i,s__kkt1,j,sp)) * nu_constr(s__kkt1,j))
                 + (ord(sp) - ord(s)) * lam_equil(s,sp) - piL_z(s,i,sp) =E= 0;
```

## Verification

- Quality gate: 4,209 tests pass, typecheck/lint/format clean
- `stat_z` equation has correct `pi(s,i,s__kkt1,j,sp)` indices (was `pi(s,i,s,i,spp)`)
- `equil` constraint present with correct `lam_equil(s,sp)` direct term (no incorrect sum)
- Fresh alias `Alias(s, s__kkt1)` properly declared in generated MCP

## Related Issues

- #1099 (marco): Similar quoted-literal index issue in stationarity, fixed for parameter refs but not AD
- #914 (markov): Previous issue was uninitialized `pi` parameter (RESOLVED)
