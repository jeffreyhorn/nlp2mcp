# hs62: MCP Execution Error — Division by Zero (log derivative)

**GitHub Issue:** [#985](https://github.com/jeffreyhorn/nlp2mcp/issues/985)
**Status:** OPEN
**Severity:** Medium — Model translates but PATH solver never runs (path_solve_terminated)
**Date:** 2026-03-03
**Affected Models:** hs62

---

## Problem Summary

The hs62 model (Hock-Schittkowski test problem #62) parses and translates to MCP successfully, but GAMS aborts during equation generation with `division by zero (0)` at line 65. The stationarity equations contain `1 / (ratio_expression)` gradient terms from `log(ratio)` in the objective. The `.l` initialization sets `x1.l = x2.l = x3.l = 1`, which causes a denominator to evaluate to zero. PATH never runs.

---

## Reproduction

```bash
python scripts/gamslib/run_full_test.py --model hs62 --verbose
# Output: [SOLVE] FAILURE: path_solve_terminated

# Direct GAMS execution:
gams data/gamslib/mcp/hs62_mcp.gms lo=3
# Error at line 65: division by zero (0)
# SOLVE from line 126 ABORTED
```

---

## Root Cause Analysis

The stationarity equation `stat_x1` contains:

```gams
stat_x1.. (-8204.37) * 1 / ((x1 + x2 + x3 + 0.03) / (0.09 * x1 + x2 + x3 + 0.03))
    * (0.09 * x1 + x2 + x3 + 0.03 - (x1 + x2 + x3 + 0.03) * 0.09)
    / (0.09 * x1 + x2 + x3 + 0.03) ** 2 + ... =E= 0;
```

This is the derivative of `log((x1+x2+x3+0.03) / (0.09*x1+x2+x3+0.03))`. The derivative of `log(u/v)` = `(v*u' - u*v') / (u*v)`. The numerator factor `(0.09*x1+x2+x3+0.03 - (x1+x2+x3+0.03)*0.09)` simplifies to `(1-0.09)*(x2+x3+0.03) - 0` which is nonzero, but the denominator `(0.09*x1+x2+x3+0.03)^2` evaluates correctly at `x1=x2=x3=1`.

However, there is also a division error at line 65, which is in the "Post-solve Calibration" section:

```gams
diff = (global - obj.l) / global;
```

If `global = 0`, this causes division by zero. The issue is that `obj.l` is referenced before the solve, and `global` may be a parameter that is zero or uninitialized.

---

## Suggested Fix

1. **Move post-solve calibration after the Solve statement** — the `diff = (global - obj.l) / global` line should only execute after PATH solves the model, not before.
2. **Guard the calibration** with `$if` or check if `global` is nonzero.
3. **Investigate whether the emitter places `.l`-referencing code in the correct position** relative to the Solve statement.

---

## Files

- MCP file: `data/gamslib/mcp/hs62_mcp.gms`
- Original GAMS model: `data/gamslib/gms/hs62.gms`
- Emitter: `src/emit/emit_gams.py`
