# cesam2: MCP pair empty equation — associated variable not fixed

**GitHub Issue:** [#1041](https://github.com/jeffreyhorn/nlp2mcp/issues/1041)
**Status:** OPEN
**Severity:** High — EXECERROR 486 aborts solve
**Date:** 2026-03-10
**Affected Models:** cesam2 (and potentially any model with conditioned stationarity equations)

---

## Problem Summary

After fixing Issue #1025 (loop body parameter emission), cesam2 compiles without $141 errors but fails at solve time with 486 MCP pair errors. Four stationarity equations (`stat_a`, `stat_err3`, `stat_tsam`, `stat_w3`) have domain conditions like `$(ii(i) and ii(j))` that exclude certain `(i,j)` pairs (specifically those involving `"Total"`). For excluded instances, the equation is empty, but the paired variable (e.g., `A(i,j)`) is not fixed to 0.

GAMS requires: if an MCP equation is empty for some instance, the paired variable must be fixed for that instance.

---

## Error Details

```
**** MCP pair stat_a.A has empty equation but associated variable is NOT fixed       (81 instances)
**** MCP pair stat_err3.ERR3 has empty equation but associated variable is NOT fixed  (81 instances)
**** MCP pair stat_tsam.TSAM has empty equation but associated variable is NOT fixed  (81 instances)
**** MCP pair stat_w3.W3 has empty equation but associated variable is NOT fixed      (243 instances)
**** SOLVE from line 367 ABORTED, EXECERROR = 486
```

---

## Root Cause

The cesam2 model has:
- Set `i` with 10 members including `"Total"`
- Dynamic subset `ii(i) = yes; ii("Total") = no;` — excludes `"Total"`
- Variables `A(i,j)`, `ERR3(i,j)`, `TSAM(i,j)`, `W3(i,j,jwt)` declared over full `(i,j)` domain
- Equations with conditions like `$(NONZERO(ii,jj))`, `$(IVAL(ii,jj))`, `$(ICOEFF(ii,jj))`

The KKT stationarity equations inherit these conditions:
```gams
stat_a(i,j)$(ii(i) and ii(j)).. sum((ii,jj), ...) =E= 0;
stat_w3(i,j,jwt)$(ii(i) and ii(j) and jwt3(jwt)).. sum((ii,jj), ...) =E= 0;
```

For `(i,j)` pairs where the condition is false (e.g., `i="Total"` or `j="Total"`), the equation is empty. But the MCP model declaration pairs these equations with variables over the full domain:
```gams
Model mcp_model /
    stat_a.a,
    stat_w3.w3,
    ...
/;
```

GAMS requires that for every `(i,j)` instance where `stat_a` is empty, `A(i,j)` must be `.fx`'d. Currently the emitter does not generate these fix statements.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/cesam2.gms -o /tmp/cesam2_mcp.gms --skip-convexity-check
gams /tmp/cesam2_mcp.gms lo=0 o=/tmp/cesam2_mcp.lst

# Check MCP pair errors:
grep "MCP pair" /tmp/cesam2_mcp.lst | sort | uniq -c
# Expected: 486 total errors across 4 equation types

# Check stationarity conditions:
grep "stat_a\|stat_w3\|stat_err3\|stat_tsam" /tmp/cesam2_mcp.gms | grep '\$'
```

---

## Suggested Fix

When a stationarity equation has a domain condition (dollar condition), emit `.fx` statements for the paired variable on instances where the condition is false:

```gams
* Fix variables for instances where stationarity equation is inactive
a.fx(i,j)$(not (ii(i) and ii(j))) = 0;
err3.fx(i,j)$(not (ii(i) and ii(j))) = 0;
tsam.fx(i,j)$(not (ii(i) and ii(j))) = 0;
w3.fx(i,j,jwt)$(not (ii(i) and ii(j) and jwt3(jwt))) = 0;
```

This pattern already exists in the emitter for inequality multipliers (`lam_*.fx(...)$(cond) = 0`). It needs to be extended to primal variables paired with conditioned stationarity equations.

### Implementation

1. In `src/kkt/assemble.py` or `src/emit/emit_gams.py`: when building the MCP model, detect stationarity equations with conditions.
2. For each conditioned stationarity equation, emit a `.fx` statement for the paired variable with the negated condition.
3. The condition can be extracted from the `EquationDef.condition` field or from the stationarity equation's dollar condition.

---

## Files Likely Affected

| File | Change |
|------|--------|
| `src/emit/emit_gams.py` | Emit `.fx` statements for variables paired with conditioned stationarity equations |
| `src/kkt/assemble.py` | Propagate stationarity conditions to the KKT system metadata |

---

## Related Issues

- Issue #1025: cesam2 wbar3 loop body parameter unassigned (FIXED)
- Issue #1022: cesam2 $187 errors (FIXED)
- Issue #881: cesam missing dollar conditions
