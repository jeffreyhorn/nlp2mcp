# etamac: MCP Execution Error — Division by Zero + log(0) Singular

**GitHub Issue:** [#984](https://github.com/jeffreyhorn/nlp2mcp/issues/984)
**Status:** OPEN
**Severity:** Medium — Model translates but PATH solver never runs (path_solve_terminated)
**Date:** 2026-03-03
**Affected Models:** etamac

---

## Problem Summary

The etamac model (energy-technology-aggregate-climate model) parses and translates to MCP successfully, but GAMS aborts during equation generation with two types of errors: `division by zero (0)` in `stat_c` at line 199 and `log: FUNC SINGULAR: x = 0` at line 232. The consumption variable `c(t)` appears in `1/c(t)` gradient terms and `log(c(t))` terms. Despite `.l` initialization (`c.l(t) = c0 * l(t)`), if `c0` or `l(t)` is zero for any time period, evaluation errors occur. PATH never runs (20 execution errors total).

---

## Reproduction

```bash
python scripts/gamslib/run_full_test.py --model etamac --verbose
# Output: [SOLVE] FAILURE: path_solve_terminated

# Direct GAMS execution:
gams data/gamslib/mcp/etamac_mcp.gms lo=3
# Error at line 199: division by zero (0)
# Evaluation error(s) in equation "stat_c(1995)" through "stat_c(2040)"
# Error at line 232: log: FUNC SINGULAR: x = 0
# SOLVE from line 299 ABORTED, EXECERROR = 20
```

---

## Root Cause Analysis

The stationarity equation for `c(t)` contains:

```gams
stat_c(t).. ((-1) * (dfact(t) * 1 / c(t))) - nu_cc(t) - piL_c(t) =E= 0;
```

This is the gradient of `log(c(t))` from the utility function `util.. utility =E= sum(t, dfact(t) * log(c(t)))`. The derivative `d/dc log(c) = 1/c` evaluated at `c = 0` causes division by zero.

The `.l` initialization `c.l(t) = c0 * l(t)` depends on parameters `c0` and `l(t)`. If either is zero for some time periods (e.g., `l(t)` is a labor force that starts at zero), then `c.l(t) = 0`, triggering the domain error.

The model also has lower bounds `c.lo(t) = 3.2` (from `comp_lo_c(t).. c(t) - 3.2 =G= 0`), but `.l` initialization occurs before GAMS enforces bounds during equation generation.

---

## Suggested Fix

1. **Ensure `.l` respects `.lo`** — after setting `.l` values, add `c.l(t) = max(c.l(t), c.lo(t))` or equivalent to ensure `.l >= .lo` before equation generation. The emitter should emit `.l` assignments that respect declared lower bounds.
2. **Alternatively, initialize with `.lo` floor** — if `.l` would be zero, use `max(epsilon, c0 * l(t))` where `epsilon` is a small positive value.
3. **Add `option domlim = 100;`** as a workaround to allow PATH to attempt solving despite domain errors.

---

## Files

- MCP file: `data/gamslib/mcp/etamac_mcp.gms`
- Original GAMS model: `data/gamslib/gms/etamac.gms`
- Stationarity builder: `src/kkt/stationarity.py`
- Emitter `.l` initialization: `src/emit/emit_gams.py`
