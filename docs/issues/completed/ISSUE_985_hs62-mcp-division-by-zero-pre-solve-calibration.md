# hs62: MCP Execution Error — Division by Zero in Pre-solve Calibration

**GitHub Issue:** [#985](https://github.com/jeffreyhorn/nlp2mcp/issues/985)
**Status:** FIXED
**Severity:** Medium — Model translates but PATH solver never runs (path_solve_terminated)
**Date:** 2026-03-03
**Fixed:** 2026-03-03
**Affected Models:** hs62

---

## Problem Summary

The hs62 model (Hock-Schittkowski test problem #62) parses and translates to MCP successfully, but GAMS aborts with `division by zero (0)` at line 65 of the MCP file. The error occurs in a post-solve calibration expression `diff = (global - obj.l) / global` that is placed **before** the Solve statement. The scalar `global` is initialized to 0, causing division by zero. The stationarity equations themselves are not the problem. PATH never runs.

---

## Fix

Disabled emission of post-solve calibration code (parameter assignments that reference variable `.l` values) in `src/emit/emit_gams.py`. The problematic expression `diff = (global - obj.l) / global` is no longer generated in the MCP file. These NLP reporting assignments may divide by zero and are not needed for MCP correctness or objective extraction.

**Result:** hs62 now translates and solves successfully without triggering division by zero (full pipeline success).

---

## Files Changed

- `src/emit/emit_gams.py` — Removed post-solve calibration emission
