# markov: Stationarity Multiplier Index Errors ($148/$171)

**GitHub Issue:** [#1100](https://github.com/jeffreyhorn/nlp2mcp/issues/1100)
**Model:** markov (GAMSlib SEQ=186)
**Status:** OPEN
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

All 5 `sum(spp, ...)` terms should have `nu_constr(s,i)` since the multiplier for `constr(sp,j)` in the context of `stat_z(s,i,sp)` should be indexed by the stationarity equation's own free indices `(s,i)`.

### Cascading: 2 errors

- **$257 (line 141)**: Solve statement not checked
- **$141 (line 143)**: `pvcost.l` has no value

---

## Root Cause

The original equation `constr(sp,j)` has domain `(sp,j)`:

```gams
constr(sp,j).. sum(spp, z(sp,j,spp)) - b * sum((s,i,spp), pi(s,i,sp,j,spp) * z(s,i,spp)) =E= beta;
```

The Jacobian of `constr` w.r.t. `z(s,i,sp)` involves the term `pi(s,i,sp,j,spp)`. When building the stationarity equation for `z`, the multiplier `nu_constr` should be indexed by the constraint's free indices `(sp,j)` mapped through the Jacobian relationship to the stationarity domain `(s,i,sp)`.

The stationarity builder appears to be incorrectly decomposing the multi-dimensional index mapping, producing partial or reversed index tuples for the multiplier reference.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/markov.gms -o /tmp/markov_mcp.gms --skip-convexity-check
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/markov_mcp.gms lo=2 o=/tmp/markov_mcp.lst
grep '^\*\*\*\*' /tmp/markov_mcp.lst
```

---

## Original GAMS Context

```gams
Sets s   /s1*s2/
     i   /i1*i3/
     sp  /s1*s2/   (alias of s)
     j   /i1*i3/   (alias of i)
     spp /s1*s2/   (alias of s)

Variables z(s,i,sp)

Equations constr(sp,j)
constr(sp,j).. sum(spp, z(sp,j,spp)) - b * sum((s,i,spp), pi(s,i,sp,j,spp) * z(s,i,spp)) =E= beta;
```

The constraint has domain `(sp,j)` and the variable `z` has domain `(s,i,sp)`. The Jacobian involves a complex multi-index relationship through the `pi` parameter.

---

## Suggested Fix

1. Investigate how `_add_indexed_jacobian_terms()` handles the case where the constraint domain `(sp,j)` doesn't directly overlap with the variable domain `(s,i,sp)` but is connected through a sum expression
2. The multiplier `nu_constr` appearing in `stat_z(s,i,sp)` should be consistently indexed — likely as `nu_constr(sp,j)` with appropriate sum wrapping, or as `nu_constr(s,i)` if the constraint-variable mapping is 1:1 through aliases

---

## Impact

4 primary compilation errors in one equation. Model cannot compile or solve.
