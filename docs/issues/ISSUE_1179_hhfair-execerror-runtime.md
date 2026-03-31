# hhfair: Runtime EXECERROR During Model Generation

**GitHub Issue:** [#1179](https://github.com/jeffreyhorn/nlp2mcp/issues/1179)
**Model:** hhfair (GAMSlib SEQ=128, "Household Optimization for Fair Wages")
**Error category:** `path_syntax_error` (EXECERROR at runtime, solve aborted)
**Previous blocker:** $171 domain violation (fixed in PR #1176 via domain widening)

## Description

The hhfair model compiles cleanly after the $171 fix (zero compilation errors), but GAMS aborts the solve with EXECERROR=1 during model generation. This is a runtime error (likely division by zero or domain error) that occurs between the `execError = 0` statement and the solve.

## Set Hierarchy

- `tl = {0, 1, 2, 3}` — long time horizon
- `t(tl) = {1, 2, 3}` — optimizing horizon (subset)
- `tt(t) = {3}` — terminal year

## Reproduction

```bash
python -m src.cli data/gamslib/raw/hhfair.gms -o /tmp/hhfair_mcp.gms --skip-convexity-check
(cd /tmp && gams hhfair_mcp.gms lo=2)
# SOLVE ABORTED, EXECERROR = 1
```

## Root Cause

The stationarity equations involve complex expressions with powers and divisions (utility function derivatives like `c(t) ** ((-1) * a2)`). When evaluated at the default initial point (variables initialized to 0 or 1), these may produce division by zero or domain errors.

The `execError = 0` at line 46 clears pre-existing errors, but new errors are generated during equation evaluation at lines 46-261.

## Investigation (2026-03-30)

The stationarity equations involve CES utility function derivatives with expressions like `(th - l(t) - n(t)) ** ((-1) * a2)` and `c(t) ** ((-1) * a2)`. Variable initialization exists for `a`, `c`, `l`, `m` but NOT for `n`.

The key issue: `stat_m(tl)` iterates over `tl = {0,1,2,3}` including `tl=0` which is NOT in subset `t`. At `tl=0`:
- `n(tl)` was domain-widened from `n(t)` to `n(tl)` — at `tl=0`, `n('0')` has no data (default 0)
- `nu_timemoney(tl)` at `tl=0` is declared over `tl` and fixed to 0 for out-of-subset instances, so it is defined but zero
- The EXECERROR likely comes from evaluating the unguarded terms in the equation body at `tl=0` — while dollar-conditioned terms are zeroed out, unconditioned terms (like `n(tl) * nu_timemoney(tl)`) are still evaluated and may reference widened variables with incompatible initial values

The EXECERROR is a consequence of domain widening: the equation iterates over `tl` (superset) and while dollar-conditioned terms correctly zero out at `tl=0`, unconditioned terms in the stationarity body may produce runtime errors when widened variables have default-zero values that cause domain issues in other parts of the expression.

## Fix Approach

1. Restrict the stationarity equation domain so it is only generated where data are valid, e.g., add a `$(t(tl))` condition on the equation definition so `tl=0` is excluded entirely
2. Alternatively, fix the paired variable/multiplier at out-of-subset elements, e.g., `m.fx(tl)$(not t(tl)) = 0;` (`.fx` is a variable attribute, not an equation attribute)
3. May need to initialize widened variables at out-of-subset elements to safe values to avoid domain violations during evaluation
