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

## Fix Approach

1. Check which stationarity equation triggers the EXECERROR (add `option execErr = 0;` or `$onError` directives)
2. Investigate if variable initialization (`.l` values) prevents division by zero
3. May need to add better initial point or guards against zero denominators in the emitted MCP
