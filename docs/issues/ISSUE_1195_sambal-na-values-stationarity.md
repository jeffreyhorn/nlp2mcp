# sambal: NA Values in Stationarity Equations (RHS value NA)

**GitHub Issue:** [#1195](https://github.com/jeffreyhorn/nlp2mcp/issues/1195)
**Model:** sambal (GAMSlib SEQ=341)
**Error category:** `gams_error` (EXECERROR=2, solve aborted)
**Previous blockers:** Wrong index reference (fixed), dollar condition not propagated (fixed)
**Severity:** High — compiles cleanly but solve aborted

## Description

After fixing the dollar condition propagation (Bug 1 in #862, via `extract_gradient_conditions` infrastructure in `src/ad/gradient.py` and `src/kkt/assemble.py`) and the wrong index reference (Bug 2), sambal compiles cleanly but GAMS aborts with EXECERROR=2 due to "RHS value NA" in stationarity equations.

## Errors

```
**** RHS value NA in equation below is illegal
     stat_t(h1)

**** RHS value NA in equation below is illegal
     stat_t(h2)   (or similar)
```

Additionally, `cbal` equations show infeasibilities at the initial point.

## Root Cause

The `t` variable's stationarity equation `stat_t` references parameters that contain GAMS `NA` (Not Available) values. When these NA values propagate into the stationarity expression, the equation RHS becomes NA which GAMS rejects.

This is related to Issue #986 (NA parameter handling in equations) — the emitter needs to detect parameters with NA values and either filter them out or add `$(param <> na)` conditions.

## Reproduction

```bash
python -m src.cli data/gamslib/raw/sambal.gms -o /tmp/sambal_mcp.gms --skip-convexity-check
(cd /tmp && gams sambal_mcp.gms lo=2)
# SOLVE ABORTED, EXECERROR = 2
# "RHS value NA in equation below is illegal" on stat_t
```

## Fix Approach

1. Identify which parameter(s) in the `stat_t` stationarity expression contain NA values
2. Add `$(param <> na)` guards on terms that reference NA-containing parameters
3. Or filter out NA-valued parameter entries during emission

## Related Issues

- #862: Original sambal tracking issue (dollar condition + wrong index — both now fixed)
- #986: NA parameter in equation RHS (same class of issue)
