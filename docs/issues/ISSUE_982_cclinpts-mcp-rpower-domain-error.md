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

The `b(j) ** (1 - gamma)` term raises `b(j)` to a non-integer power. When `gamma > 1`, the exponent `(1 - gamma)` is negative. The variable `b.l` is initialized to 5.0, which should be valid. However, the gradient expression `b(j) ** (1 - gamma)` with `gamma` likely > 1 and a possible negative intermediate creates the domain error.

The `.l` initialization exists (`b.l("s1") = 5.0` etc.) but may not be sufficient if the expression requires `b > 0` strictly and intermediate evaluation produces negative values, or if `gamma` makes the expression `x^y` with `x < 0`.

---

## Suggested Fix

1. **Investigate the actual value of `gamma`** in the original model — if `gamma > 1`, then `1 - gamma < 0` and `b(j)^(1-gamma)` requires `b(j) > 0` strictly. The `.l` values of 5.0 should work, so the issue may be in how the gradient is simplified/evaluated.
2. **Add `option domlim = 100;`** to allow GAMS to continue past domain errors — PATH may still converge if evaluation errors are transient.
3. **Simplify the gradient expression** — the `b(j) ** (1 - gamma) * (1 - gamma) / b(j)` can be rewritten as `(1 - gamma) * b(j) ** (-gamma)` which may have better numerical behavior.

---

## Files

- MCP file: `data/gamslib/mcp/cclinpts_mcp.gms`
- Original GAMS model: `data/gamslib/gms/cclinpts.gms`
- Stationarity builder: `src/kkt/stationarity.py`
- Expression emitter: `src/emit/expr_to_gams.py`
