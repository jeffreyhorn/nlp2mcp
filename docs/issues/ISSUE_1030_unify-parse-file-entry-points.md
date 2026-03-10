# Unify parse_file and parse_model_file entry points

**GitHub Issue:** [#1030](https://github.com/jeffreyhorn/nlp2mcp/issues/1030)
**Status:** OPEN
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

## Root Cause

The two functions share preprocessing and Earley parsing but diverge at IR construction. `parse_file` stops after the parse tree, while `parse_model_file` continues through `_ModelBuilder.build()`. Errors in IR construction (e.g., `_process_index_list` missing `expr_fn`) are invisible to `parse_file` callers.

---

## Proposed Fix

Consolidate to a single entry point or clearly separate concerns:

1. **Option A**: Remove `parse_file`. Callers needing just the tree can call `parse_text(preprocess_gams_file(path))` directly.
2. **Option B**: Rename `parse_file` to `parse_tree` for clarity, ensure pipeline/test code uses `parse_model_file`.
3. **Option C**: Make `parse_model_file` canonical, `parse_file` becomes a thin wrapper.

---

## Affected Files

- `src/ir/parser.py` — both functions defined here (lines 392-423)
- `scripts/gamslib/batch_parse.py` — uses `parse_model_file`
- `src/cli.py` — check which entry point is used
- Tests — audit which entry point they use

---

## Discovery Context

Found during PR #1029 review: `imsl` had stale "success" parse status in `gamslib_status.json` because the old pipeline run recorded success, but `parse_model_file` actually fails with `offset_func requires an expr_fn`. The `srpchase` model had a similar issue caused by missing `expr_fn` in `_handle_conditional_assign_general` (fixed in PR #1029).
