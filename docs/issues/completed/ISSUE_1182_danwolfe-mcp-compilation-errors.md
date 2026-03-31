# danwolfe: MCP Compilation Errors ($140/$126/$148/$149)

**GitHub Issue:** [#1182](https://github.com/jeffreyhorn/nlp2mcp/issues/1182)
**Status:** FIXED (compilation errors resolved; license limit for solve)
**Model:** danwolfe (GAMSlib, Dantzig-Wolfe decomposition)

## Fix

Three issues fixed:

1. **$140 Unknown symbol (kdem, bal, ebal, h)**: Parameters assigned inside loops but with no static values/expressions were skipped by Issue #917 logic. Added `_is_referenced_in_loops()` helper that checks if a parameter appears in any loop statement body tree. Parameters referenced in loops are now declared even without static data.

2. **Malformed `sum(sum, ...)`**: `_loop_tree_to_gams` emitted the `SUM_K` keyword token as the domain argument. Fixed by filtering to Tree children only, skipping leading keyword tokens.

3. **Missing dollar condition parens in sum domain**: `index_spec` with dollar condition (`i$(bal(k,i) > 0)`) had no handler in `_loop_tree_to_gams`. Added handler that emits `idx$(cond)` format.

**Result:** danwolfe now compiles cleanly (0 compilation errors). Solve blocked by demo license limit (model exceeds 1000 rows/columns for nonlinear types). All 4,358 tests pass.
