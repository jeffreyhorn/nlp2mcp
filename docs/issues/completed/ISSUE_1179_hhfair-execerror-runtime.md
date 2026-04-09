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

The stationarity equations involve CES utility function derivatives with expressions like `(th - l(t) - n(t)) ** ((-1) * a2)` and `c(t) ** ((-1) * a2)`. Variable initialization exists for `a`, `c`, `l`, `m`, and `u`, but NOT for `n` (and several other variables remain at their default initial values).

The key structural detail is that `stat_m(tl)` iterates over `tl = {0,1,2,3}` including `tl=0`, which is NOT in subset `t`. At `tl=0`:
- `n(tl)` was domain-widened from `n(t)` to `n(tl)` — at `tl=0`, `n('0')` has no data (default 0)
- `nu_timemoney(tl)` at `tl=0` is declared over `tl` and fixed to 0 for out-of-subset instances, so it is defined but zero

A plausible hypothesis is that EXECERROR arises from a domain/undefined-instance issue when evaluating equations at `tl=0`. However, in the checked-in generated model, the only `tl`-indexed unconditioned stationarity equation `stat_m(tl)` is linear, contains no divisions or powers, and `n(tl)` appears only in a simple product term. This suggests the precise EXECERROR trigger is still unknown. The next step is to inspect the GAMS listing/log to identify the exact equation/subexpression that raises EXECERROR.

## Fix (Sprint 24)

**Status: FIXED** — hhfair now solves MODEL STATUS 1 Optimal.

**Root Cause:** Variable `n(t)` was domain-widened to `n(tl)` by the emitter,
but the stationarity equation `stat_n(t)` stayed over subset `t`. This left
`n(0)` as an unmatched free variable in the MCP (0 ∈ tl but 0 ∉ t).

**Fix:** In emit_gams.py section 1c, added domain-widened variable fixing.
When a variable's domain is widened (e.g., `n(t)` → `n(tl)`), the emitter
now emits `n.fx(tl)$(not (t(tl))) = 0;` to fix out-of-subset instances.
This is applied to all widened variables not already handled by
stationarity_conditions.

**Result:** hhfair advances from path_solve_terminated (EXECERROR=1) to
model_optimal (MODEL STATUS 1). MCP obj=54.885 vs NLP obj=87.159
(objective mismatch — separate issue).
