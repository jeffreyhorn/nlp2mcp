# cclinpts: MCP Execution Error — rPower Domain (x**y, x < 0)

**GitHub Issue:** [#982](https://github.com/jeffreyhorn/nlp2mcp/issues/982)
**Status:** FIXED
**Severity:** Medium — Model translates but PATH solver never runs (path_solve_terminated)
**Date:** 2026-03-03
**Fixed:** 2026-03-03
**Affected Models:** cclinpts

---

## Problem Summary

The cclinpts model parses and translates to MCP successfully, but GAMS aborts during equation generation with `rPower: FUNC DOMAIN: x**y, x < 0`. The error occurs because the stationarity equation contains `(1 - gamma) ** 2` with `gamma = 2`, evaluating as `(-1) ** 2`. GAMS's `rPower` rejects negative bases even for integer exponents. PATH never runs.

---

## Fix

Modified `src/emit/expr_to_gams.py` to emit `sqr(x)` instead of `x ** 2` when the exponent is exactly `Const(2.0)`. GAMS `sqr()` handles negative inputs correctly (computes `x*x`) unlike `x ** 2` via `rPower`.

**Result:** cclinpts now translates and solves (no more rPower domain error). The objective value differs from the original NLP (`diff=6.96`), likely converging to a different stationary point.

---

## Files Changed

- `src/emit/expr_to_gams.py` — Added `sqr(x)` conversion for `x ** 2` in Binary power handler
- `tests/unit/emit/test_expr_to_gams.py` — Updated 6 test expectations for `sqr()` output
- `tests/unit/emit/test_equations.py` — Updated 1 test expectation for `sqr()` output
