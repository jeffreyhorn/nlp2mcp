# solveopt: Domain Violation ($171) in Stationarity Equation — Index Mismatch

**GitHub Issue:** [#1053](https://github.com/jeffreyhorn/nlp2mcp/issues/1053)
**Status:** OPEN
**Severity:** High — path_syntax_error, model fails to compile
**Date:** 2026-03-11
**Affected Models:** solveopt

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

The stationarity equation builder computes the Jacobian of equation `e2(j)` w.r.t. variable `x2(i)` and produces a term `nu_e2(...)`. When the equation domain `(j)` is a subset of the variable domain `(i)`, the multiplier index should use `j` (or the conditioned intersection), not `i`.

**Original GAMS model:**
```gams
Set i /i1*i5/, j(i) /i2,i4/;
Variable x2(i);
e2(j).. x2(j) =E= 20;
```

The stationarity for `x2` w.r.t. `e2(j)` should produce `nu_e2(j)` indexed over the equation's domain, or equivalently `nu_e2(i)$(j(i))`. Since the entire stationarity equation is already conditioned on `j(i)`, the reference `nu_e2(i)` would work if GAMS didn't enforce strict domain checking. However, GAMS does enforce domain checking, so the emitter must use `nu_e2(j)` — but the index name `j` is also the set name, creating a conflict.

**Correct form should be one of:**
```gams
stat_x2(j).. nu_e2(j) + piU_x2(j) =E= 0;
```
or with explicit domain mapping using the `j(i)` condition.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/solveopt.gms -o /tmp/solveopt_mcp.gms
gams /tmp/solveopt_mcp.gms lo=2
# Error $171 at stat_x2 equation
```

---

## Proposed Fix

The stationarity equation builder needs to handle the case where the equation's domain is a strict subset of the variable's domain. When emitting `nu_eqname(indices)`, the indices must be valid for the multiplier's declared domain. Options:

1. **Use equation domain indices directly:** Change `stat_x2` domain from `(i)` to `(j)`, matching the equation domain
2. **Emit domain-compatible indices:** Keep `stat_x2(i)$(j(i))` but reference `nu_e2(i)` with explicit GAMS domain relaxation
3. **Remap indices:** When the stationarity domain is `i` but the multiplier domain is `j(i)`, substitute index references appropriately

---

## Related

- This is a pre-existing issue on main (not caused by Sprint 22 Day 5 changes)
- solveopt previously solved with old MCP files from Sprint 20; re-translation with current code exposes this bug
