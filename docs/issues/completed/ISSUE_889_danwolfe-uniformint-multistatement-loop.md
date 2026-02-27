# danwolfe: `uniformInt` function and multi-statement loop lines

**GitHub Issue:** [#889](https://github.com/jeffreyhorn/nlp2mcp/issues/889)
**Model:** danwolfe (GAMSlib SEQ=79)
**Error category:** `lexer_invalid_char`
**Error message:** `Unexpected character: '1'` at line 77, column 22
**Status:** RESOLVED

## Description

The lexer fails on `uniformInt(1,card(i))` — the `uniformInt` function is not recognized. Additionally, the model has multiple statements on one line inside a `loop` block, separated by `;`.

## Resolution

Fixed via multiple changes:

1. **`uniformInt` added to FUNCNAME** in `src/gams/gams_grammar.lark` — placed before `uniform` to avoid prefix matching
2. **`while` statement support** added — grammar rule `while_stmt`, keyword `WHILE_K`, parser handler `_handle_while_stmt()`
3. **`display$condition` variants** added to grammar for conditional display statements
4. **`loop(k$kdem(k), ...)` variant** added — `loop_stmt_filtered` with indexed condition `ID "(" index_list ")"`
5. **`%solPrint.*` system macros** added to `SYSTEM_MACROS` in `src/ir/preprocessor.py`
6. **Case-insensitive macro expansion** — `expand_macros()` now uses `re.IGNORECASE` flag

The model now parses past the original `uniformInt` error and subsequent blockers. It still
fails at line 219 due to unsupported `handlecollect`/`handledelete` functions (GAMS
asynchronous grid computing features), which are outside the scope of this fix.

## Files Modified

| File | Changes |
|------|---------|
| `src/gams/gams_grammar.lark` | Added `uniformInt` to FUNCNAME, `while_stmt` rule, `display$` variants, indexed loop filter |
| `src/ir/parser.py` | Added `_handle_while_stmt()`, updated `_find_solve_in_loop_body()` |
| `src/ir/preprocessor.py` | Added `solPrint.*` system macros, case-insensitive macro expansion |
