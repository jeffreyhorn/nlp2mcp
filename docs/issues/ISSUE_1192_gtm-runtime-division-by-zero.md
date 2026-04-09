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

## Root Cause (Initial Hypothesis — Superseded)

~~The supply function involves `supa(i) * s(i) ** supb(i)` where negative
exponents cause division by zero.~~ This was the initial hypothesis. The
confirmed root cause is in the "Root Cause Detail" section below: three
regions have `supc(i) = 0`, making the `log((supc-s)/supc)` supply function
and its derivative `supb/(supc-s)` undefined.

## Reproduction

```bash
python -m src.cli data/gamslib/raw/gtm.gms -o /tmp/gtm_mcp.gms --skip-convexity-check
(cd /tmp && gams gtm_mcp.gms lo=2)
# SOLVE ABORTED, EXECERROR = 3
```

## Investigation (Sprint 24)

**Status: NOT FIXED** — requires model-specific initialization or expression guards.

### Root Cause Detail

For three supply regions (mexico, alberta-bc, atlantic), `supc(i) = 0` because
`sdat(i, "limit")` is not defined and `supc(i)$(supc(i) = inf) = 100` doesn't
trigger. This makes the supply function `supa*s - supb*log((supc-s)/supc)`
and its derivative `supb/(supc - s)` undefined at the initial point `s = 0`.

The original NLP avoids this because `s.up(i) = 0.99 * supc(i) = 0` forces
`s(i) = 0`, and GAMS skips equation evaluation for fixed variables. But the
MCP stationarity equations evaluate at all domain instances, including those
with degenerate supply functions.

### Approaches Tried

1. **`option domlim = 100`**: Only controls solver-level domain violations,
   not equation-generation-time errors. GAMS still aborts with EXECERROR=3.

2. **`execError = 0` before solve**: Clears the counter but GAMS regenerates
   errors during equation listing for the Solve statement.

3. **`model.domlim = 100`**: Same as option-level, doesn't prevent abort.

### What Would Fix It

1. **Emit `$onUndf` directive**: Would need to be emitted as a GAMS directive
   (starting with `$`) BEFORE the equation definitions, not as a GAMS statement.
   This requires changes to the emitter's directive handling.

2. **Model-specific variable initialization**: Add `s.l(i) = sdat(i,"ref-q1")`
   which provides feasible starting values. Requires the emitter to detect
   supply parameters and emit appropriate initialization.

3. **Conditional stationarity**: Add `$(supc(i) > 0)` condition on `stat_s(i)`
   to skip zero-capacity regions. Requires parameter-value-aware conditioning
   in the stationarity builder.

4. **General expression guards**: Use GAMS conditional-term syntax such as
   `(1/(supc-s))$(supc > 0)`. This is a general solution but requires
   significant emitter/IR changes.

## Related Issues

- #827: Original compilation errors (now fixed)
