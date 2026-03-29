# Unify parse_file and parse_model_file entry points

**GitHub Issue:** [#1030](https://github.com/jeffreyhorn/nlp2mcp/issues/1030)
**Status:** FIXED
**Severity:** Medium — causes stale/misleading status entries
**Date:** 2026-03-10
**Affected Models:** imsl (stale success status), potentially others

---

## Problem Summary

`src/ir/parser.py` has two parsing entry points that can get out of sync:

- `parse_file(path)` returns a raw `Tree` (lexing/parsing only)
- `parse_model_file(path)` returns `ModelIR` (preprocessing + parsing + IR building)

The pipeline uses `parse_model_file`, which exercises the full IR builder. A model can "parse" via `parse_file` while failing via `parse_model_file` due to IR builder errors, leading to stale status entries.

---

## Fix

Applied **Option B** from the proposed fixes: renamed `parse_file` to `parse_tree` for clarity.

Changes:
1. **`src/ir/parser.py`**: Renamed `parse_file()` to `parse_tree()` with updated docstring that points users to `parse_model_file()` for full ModelIR. Added a `parse_file()` wrapper that delegates to `parse_tree()` to preserve existing `parse_file` metadata while maintaining backward compatibility.
2. **`tests/e2e/test_integration.py`**: Updated import and all calls to use `parse_tree`.
3. **`tests/unit/gams/test_parser.py`**: Updated call to use `parse_tree`.
4. **`tests/research/table_verification/debug_token_positions.py`**: Updated import and call.
5. **`tests/research/table_verification/debug_ast.py`**: Updated import and call.

The new name `parse_tree` makes the API self-documenting:
- `parse_text(source)` → Tree (from string)
- `parse_tree(path)` → Tree (from file)
- `parse_model_text(source)` → ModelIR (from string)
- `parse_model_file(path)` → ModelIR (from file)
