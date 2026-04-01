# gtm: Runtime Division by Zero in Stationarity Equations

**GitHub Issue:** [#1192](https://github.com/jeffreyhorn/nlp2mcp/issues/1192)
**Model:** gtm (GAMSlib SEQ=127, "Gas Trade Model")
**Error category:** `gams_error` (EXECERROR=3, solve aborted)
**Previous blocker:** $170/$141 compilation errors (fixed by accumulated prior fixes)
**Severity:** High — compiles cleanly but solve aborted

## Description

After resolving all 28 compilation errors, gtm compiles cleanly but GAMS aborts with EXECERROR=3 during model generation. Three `stat_s` stationarity equations produce division by zero, and multiple `stat_d`/`stat_x` equations show infeasibilities.

## Errors

```
**** Exec Error at line 155: division by zero (0)
**** Evaluation error(s) in equation "stat_s(mexico)"
**** Evaluation error(s) in equation "stat_s(alberta-bc)"
**** Evaluation error(s) in equation "stat_s(atlantic)"
```

Additionally, `stat_d` and `stat_x` equations show infeasibilities (nonzero RHS at the initial point).

## Root Cause

The supply function in gtm involves expressions like `supa(i) * s(i) ** supb(i)` where `supb` contains negative exponents. When `s(i)` is at its initial value (likely 0 or 1), the derivative `d/ds(supa * s^supb) = supa * supb * s^(supb-1)` can produce division by zero if `supb - 1 < 0` and `s = 0`.

The stationarity equation `stat_s(i)` contains these derivative terms. At the default initial point, the evaluation fails for regions where the supply function parameters create a singularity.

## Reproduction

```bash
python -m src.cli data/gamslib/raw/gtm.gms -o /tmp/gtm_mcp.gms --skip-convexity-check
(cd /tmp && gams gtm_mcp.gms lo=2)
# SOLVE ABORTED, EXECERROR = 3
```

## Fix Approach

1. Check if better variable initialization (`.l` values) avoids the singularity
2. May need to add guards against zero denominators in the emitted stationarity expressions
3. Related to the general problem of division-by-zero in nonlinear KKT conditions at default initial points

## Related Issues

- #827: Original compilation errors (now fixed)
