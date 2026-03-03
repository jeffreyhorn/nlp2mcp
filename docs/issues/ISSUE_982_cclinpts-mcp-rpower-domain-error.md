# cclinpts: MCP Execution Error — rPower Domain (x**y, x < 0)

**GitHub Issue:** [#982](https://github.com/jeffreyhorn/nlp2mcp/issues/982)
**Status:** OPEN
**Severity:** Medium — Model translates but PATH solver never runs (path_solve_terminated)
**Date:** 2026-03-03
**Affected Models:** cclinpts

---

## Problem Summary

The cclinpts model parses and translates to MCP successfully, but GAMS aborts during equation generation with `rPower: FUNC DOMAIN: x**y, x < 0`. The error occurs in the `stat_b` stationarity equations at line 124 of the MCP file. PATH never runs.

---

## Reproduction

```bash
python scripts/gamslib/run_full_test.py --model cclinpts --verbose
# Output: [SOLVE] FAILURE: path_solve_terminated

# Direct GAMS execution:
gams data/gamslib/mcp/cclinpts_mcp.gms lo=3
# Error: rPower: FUNC DOMAIN: x**y, x < 0
# Evaluation error(s) in equation "stat_b(s1)" through "stat_b(s30)"
```

---

## Root Cause Analysis

The stationarity equation `stat_b(j)` contains a power expression derived from the KKT gradient:

```gams
stat_b(j).. ((-1) * ((1 - gamma) * b(j) ** (1 - gamma) * (1 - gamma) / b(j) / (1 - gamma) ** 2)) * nu_FBCalc(j) + ... =E= 0;
```

The model declares `gamma = 2` (Scalar). With `gamma = 2`, `(1 - gamma) = -1`. The subexpression `(1 - gamma) ** 2` evaluates as `(-1) ** 2`. GAMS uses `rPower` for the `**` operator, which requires a non-negative base for real-valued exponentiation. Even though `(-1)^2 = 1` is mathematically well-defined, GAMS's `rPower` rejects the negative base `-1` and raises `FUNC DOMAIN: x**y, x < 0`.

The variable `b.l` is initialized to 5.0, and `b(j) ** (1 - gamma)` = `5^(-1)` = 0.2 is fine. The problem is specifically the `(1 - gamma) ** 2` subexpression where the base `(1 - gamma) = -1` is negative.

---

## Suggested Fix

1. **Simplify the gradient expression** — the entire expression `(1 - gamma) * b^(1-gamma) * (1-gamma) / b / (1-gamma)^2` simplifies algebraically to `b^(-gamma)` = `1/b^gamma`, which avoids raising a negative base to any power. The AD/emitter should apply this simplification.
2. **Use `sqr()` instead of `** 2`** — GAMS `sqr(x)` handles negative inputs correctly unlike `x ** 2` via `rPower`.
3. **Add `option domlim = 100;`** as a workaround to allow GAMS to continue past domain errors.

---

## Files

- MCP file: `data/gamslib/mcp/cclinpts_mcp.gms`
- Original GAMS model: `data/gamslib/gms/cclinpts.gms`
- Stationarity builder: `src/kkt/stationarity.py`
- Expression emitter: `src/emit/expr_to_gams.py`
