# hs62: MCP Execution Error — Division by Zero in Pre-solve Calibration

**GitHub Issue:** [#985](https://github.com/jeffreyhorn/nlp2mcp/issues/985)
**Status:** OPEN
**Severity:** Medium — Model translates but PATH solver never runs (path_solve_terminated)
**Date:** 2026-03-03
**Affected Models:** hs62

---

## Problem Summary

The hs62 model (Hock-Schittkowski test problem #62) parses and translates to MCP successfully, but GAMS aborts with `division by zero (0)` at line 65 of the MCP file. The error occurs in a post-solve calibration expression `diff = (global - obj.l) / global` that is placed **before** the Solve statement. The scalar `global` is initialized to 0, causing division by zero. The stationarity equations themselves are not the problem. PATH never runs.

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

The error is at line 65 of the emitted MCP file, in a "Post-solve Calibration" block that appears **before** the Solve statement:

```gams
Scalars
    global /0/          ← initialized to 0
    solution /-26272.5145/
    diff /0/
;

x1.l = 1;  x2.l = 1;  x3.l = 1;

* Post-solve Calibration (variable .l references)
$onImplicitAssign
diff = (global - obj.l) / global;   ← line 65: division by zero (global = 0)
$offImplicitAssign

* Equations (stationarity, etc.) follow below...
* ... then Solve statement
```

The scalar `global` is declared with value 0. The expression `diff = (global - obj.l) / global` divides by `global` = 0, causing the execution error. This block is emitted from original model code that was intended to run **after** solving, but the emitter places it before the equations and Solve statement. The stationarity equations themselves evaluate correctly at the `.l` starting point.

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
