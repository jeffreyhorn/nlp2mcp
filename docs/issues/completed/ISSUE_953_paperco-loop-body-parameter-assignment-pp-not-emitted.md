# paperco: Loop Body Parameter Assignment `pp(p)` Not Emitted

**GitHub Issue:** [#953](https://github.com/jeffreyhorn/nlp2mcp/issues/953)
**Status:** FIXED (resolved by PRs #1183 and prior loop emission improvements)
**Model:** paperco (GAMSlib)

## Fix

The $66 compilation error was resolved by two prior fixes:

1. **PR #1183** (`_collect_loop_referenced_params`): Parameters referenced in loop body trees are now declared even without static data. `pp(p)` is now included in the Parameters block.

2. **`emit_pre_solve_param_assignments`**: Extracts pre-solve parameter assignments from loop bodies. `pp(p) = ppdat('scenario-1', p)` is correctly emitted from the first iteration's assignment.

**Result:** paperco compiles and solves to MODEL STATUS 1 Optimal. Objective mismatch is expected — the original model runs 3 scenarios and the reference uses the last; the MCP captures scenario-1 values.

No additional code changes needed.
