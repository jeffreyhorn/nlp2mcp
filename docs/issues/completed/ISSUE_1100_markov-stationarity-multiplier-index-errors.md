# markov: Stationarity Multiplier Index Errors ($148/$171)

**GitHub Issue:** [#1100](https://github.com/jeffreyhorn/nlp2mcp/issues/1100)
**Model:** markov (GAMSlib SEQ=186)
**Status:** FIXED
**Error Category:** Compilation — $148 Dimension different, $171 Domain violation
**Severity:** Medium — model translates but GAMS compilation fails (8 errors)
**Sprint:** 22 Day 12

---

## Problem Summary

After resolving the missing `pi` assignment issue (#914), the markov MCP still fails to compile due to incorrect multiplier indexing in the `stat_z` stationarity equation. The multiplier `nu_constr(s,i)` is referenced with varying incorrect index combinations.

---

## Error Details

### stat_z (line 105): 4 distinct index violations

```gams
stat_z(s,i,sp).. c(s,sp,i)
  + sum(spp, (1 - b * pi(s,i,s,i,spp)) * nu_constr(s,i))        -- OK
  + 2 * sum(spp, ((-1) * (b * pi(s,i,s,i,spp))) * nu_constr(s))  -- $148: missing i
  + sum(spp, ((-1) * (b * pi(s,i,s,i,spp))) * nu_constr(i))       -- $171,$148: missing s
  + sum(spp, ((-1) * (b * pi(s,i,s,i,spp))) * nu_constr)          -- $148: missing both
  + sum(spp, ((-1) * (b * pi(s,i,s,i,spp))) * nu_constr(i,s))     -- $171,$171: reversed
  - piL_z(s,i,sp) =E= 0;
```

1. **`nu_constr(s)` — $148**: Declared `(s,i)`, referenced with only `s`. Missing index `i`.
2. **`nu_constr(i)` — $171+$148**: Declared `(s,i)`, referenced with only `i`. Wrong domain + missing index.
3. **`nu_constr` — $148**: Declared `(s,i)`, referenced with 0 indices. Both indices missing.
4. **`nu_constr(i,s)` — $171+$171**: Declared `(s,i)`, referenced as `(i,s)`. Indices reversed.

### Cascading: 2 errors

- **$257 (line 141)**: Solve statement not checked
- **$141 (line 143)**: `pvcost.l` has no value

---

## Root Cause

Same root cause as #1099 (marco). The `_compute_index_offset_key()` function in `src/kkt/stationarity.py` used element-value string matching to determine dimension alignment between equation and variable domains. For markov, the sets `s`, `sp`, `spp` are aliases of each other and share all element labels, causing the element-value matching to produce incorrect or arbitrary dimension mappings.

Additionally, the multiplier reference construction for dimension-mismatch cases used `matched_var_dims` instead of the equation's own `mult_domain`, producing scalar or wrong-dimensional multiplier references.

---

## Fix Details

Fixed by the same changes as #1099:

**Files modified:**
- `src/kkt/stationarity.py`: Three changes:
  1. `_compute_index_offset_key()`: Domain/alias-based matching with two-pass approach (exact canonical match first, then root/parent match)
  2. Multiplier reference construction: Use `mult_domain` for dim-mismatch
  3. `_replace_matching_indices()`: Preserve fixed literals from independent sets

**Verification:**
- GAMS compilation: 0 errors (was 8)
- MODEL STATUS 1 (Optimal)
- MCP objective: 2571.794
- All 4209 tests pass, no regressions

---

## Impact

4 primary compilation errors in one equation. Model now compiles and solves successfully.
