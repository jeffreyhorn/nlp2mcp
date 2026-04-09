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

## Fix (Sprint 24)

**Status: FIXED** — sambal and qsambal now solve MODEL STATUS 1 Optimal.

**Root Cause Detail:** Parameters `tb(i)` and `xb(i,j)` contain GAMS NA values
(`nan` in IR). The stationarity equation `stat_t(i)` has terms like
`tb(i) * ... / sqr(tb(i)) * 1$(tw(i))`. Even though `tw(h1) = 0` zeros out
the condition, GAMS evaluates `tb(i) = NA` first, producing NA propagation
through multiplication (`NA * 0 = NA`), and division by zero (`/ sqr(NA)`).

**Fix:** Added NA parameter cleanup in `emit_gams.py` before the solve
statement. For each parameter with NA values (`nan` in `pdef.values`),
emits `param(domain)$(mapval(param(domain)) = mapval(na)) = 1;`. Setting
NA entries to 1 (not 0) avoids both NA propagation AND division-by-zero
in denominators like `/ sqr(tb(i))`.

**Result:** sambal and qsambal both advance from path_solve_terminated
(EXECERROR=2) to model_optimal (MODEL STATUS 1 Optimal).

## Related Issues

- #862: Original sambal tracking issue (dollar condition + wrong index — both now fixed)
- #986: NA parameter in equation RHS (same class of issue)
