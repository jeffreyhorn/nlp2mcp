# Grammar: abort$condition with Display Items (No String Message) (lop)

**GitHub Issue:** [#715](https://github.com/jeffreyhorn/nlp2mcp/issues/715)
**Status:** Fixed
**Severity:** Medium — Blocks parsing of models using abort$cond with identifier display lists
**Discovered:** 2026-02-13 (Sprint 19, after Issue #711 fix advanced lop past nested loop)
**Fixed:** 2026-02-13 (Sprint 19)
**Affected Models:** lop (line 207)

---

## Problem Summary

The `abort` statement grammar supported `abort$condition 'message', display_items` (with a STRING message) and `abort$condition` (bare), but did not support `abort$condition display_items` where the display items are identifiers without a preceding string message. This caused lop to fail parsing at line 207.

---

## Root Cause

The `abort_base` rule in `src/gams/gams_grammar.lark` had no variant for `abort$condition display_items` without a STRING. When parsing `abort$card(error02) error02;`, the Earley parser's greedy `expr` rule consumed both `card(error02)` and `error02` as a single expression, leaving the parser unable to parse the subsequent `Set` statement.

---

## Fix

Grammar changes in `src/gams/gams_grammar.lark`:

1. **Added `abort_cond_plain_display` variant**: `"abort"i DOLLAR abort_cond_atom display_item (","? display_item)*` — handles `abort$cond items` where the condition is a single atom (function call, indexed reference, or bare identifier).

2. **Added `abort_cond_atom` rule**: A restricted condition expression (`func_call | ID "(" id_list ")" | ID`) that prevents the Earley parser from greedily consuming display items as part of the condition expression. Without delimiters (`()` or `[]`), the condition must be a single atom so the parser knows where it ends.

3. **Added `abort_cond_paren_display` and `abort_cond_square_display` variants**: For completeness, also support `abort$(expr) display_items` and `abort$[expr] display_items` without a STRING message.

No parser.py changes needed — abort statements are execution statements that the model builder silently skips.

Also removed unused `pytest` import from `tests/edge_cases/test_edge_cases.py` (leftover from Issue #714 test update).

---

## Verification

- Minimal reproduction `abort$card(error02) error02; Set ll(s) 'test';` now parses correctly
- Parse tree shows `abort_cond_plain_display` with `abort_cond_atom(func_call(card, error02))` and display item `error02`
- lop model advances past line 207 to line 252 (separate issue: tuple domain `$` condition in sum expression, not related to #715)
- Quality gate: 3312 tests pass, typecheck/lint/format clean
