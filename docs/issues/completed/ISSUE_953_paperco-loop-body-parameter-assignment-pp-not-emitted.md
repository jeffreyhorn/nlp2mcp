# paperco: Loop Body Parameter Assignment `pp(p)` Not Emitted

**GitHub Issue:** [#953](https://github.com/jeffreyhorn/nlp2mcp/issues/953)
**Status:** FIXED (resolved by existing `emit_pre_solve_param_assignments`)
**Model:** paperco (GAMSlib)

## Fix

The $66 compilation error was resolved by the existing `emit_pre_solve_param_assignments` function in `src/emit/original_symbols.py`, which extracts pre-solve parameter assignments from solve-containing loops. It emits `pp(p) = ppdat('scenario-1', p)` as a separate `Parameter pp(p);` declaration with assignment before the MCP solve.

Note: `_collect_loop_referenced_params` (PR #1183) does NOT apply here because it explicitly skips loops containing solve statements. The fix is entirely from the pre-solve assignment extraction path.

**Result:** paperco compiles and solves to MODEL STATUS 1 Optimal (verified 2026-03-31). Objective mismatch with reference is expected — the original model runs 3 scenarios and the reference uses the last iteration; the MCP captures scenario-1 values.

No additional code changes needed.
