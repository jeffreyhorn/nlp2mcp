# cesam2: GAMS Error 141 — wbar3 parameter unassigned (loop body assignment not emitted)

**GitHub Issue:** [#1025](https://github.com/jeffreyhorn/nlp2mcp/issues/1025)
**Status:** FIXED
**Severity:** High — compilation error blocks solve
**Date:** 2026-03-09
**Fixed:** 2026-03-10
**Affected Models:** cesam2

---

## Problem Summary

The parameter `wbar3(i,j,jwt)` was declared and referenced in equations and `.l` assignments, but its values were never emitted. The parameter is assigned inside a `loop((ii,jj)$NONZERO(ii,jj), ...)` block in the original model, and the IR's `LoopStatement` body assignments were not being emitted.

GAMS Error $141: "Symbol declared but no values have been assigned."

---

## Fix Applied

### Approach: Re-emit loop statements from raw parse trees (Option A)

1. **Store raw Lark parse tree** in `LoopStatement.raw_node` (`src/ir/symbols.py`, `src/ir/parser.py`). This preserves the complete original loop structure for faithful re-emission.

2. **Tree-to-GAMS serializer** (`_loop_tree_to_gams()` in `src/emit/original_symbols.py`). Recursively walks the Lark parse tree and reconstructs valid GAMS syntax, handling `assign`, `conditional_assign_general`, `symbol_indexed`, `func_call`, `binop`, `condition`, and loop header variants (paren, filtered, indexed).

3. **Emit loop statements** in the MCP output (`emit_loop_statements()` in `src/emit/original_symbols.py`, called from `emit_gams_mcp()` in `src/emit/emit_gams.py`). Loops are emitted after computed parameter assignments and before variable declarations.

4. **Skip loops with solve statements** (`_loop_contains_solve()`). Loops that contain iterative solve procedures (e.g., dispatch model) are not re-emitted, as they are the original model's solve process, not parameter initialization.

### Result

- `wbar3`, `vbar3`, and `sigmay3` are now correctly assigned in the emitted loop
- The $141 error is eliminated
- The dispatch model (which has a loop with solve) is not affected

---

## Files Changed

| File | Change |
|------|--------|
| `src/ir/symbols.py` | Added `raw_node` field to `LoopStatement` |
| `src/ir/parser.py` | Store raw node in `LoopStatement` for both loop and while handlers |
| `src/emit/original_symbols.py` | Added `_loop_tree_to_gams()`, `_emit_loop_node()`, `_loop_contains_solve()`, `emit_loop_statements()` |
| `src/emit/emit_gams.py` | Import and call `emit_loop_statements()` after computed parameter assignments |

---

## Quality Gate

- 4048 passed, 10 skipped, 1 xfailed
- typecheck: clean
- lint: clean
- format: clean

---

## Related Issues

- Issue #1022: cesam2 $187 errors (FIXED — alias of dynamic subset used as domain)
- Issue #881: cesam missing dollar conditions (sibling model)
