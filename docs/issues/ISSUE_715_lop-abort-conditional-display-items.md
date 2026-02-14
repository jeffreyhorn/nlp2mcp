# Grammar: abort$condition with Display Items (No String Message) (lop)

**GitHub Issue:** [#715](https://github.com/jeffreyhorn/nlp2mcp/issues/715)
**Status:** Open
**Severity:** Medium — Blocks parsing of models using abort$cond with identifier display lists
**Discovered:** 2026-02-13 (Sprint 19, after Issue #711 fix advanced lop past nested loop)
**Affected Models:** lop (line 207)

---

## Problem Summary

The `abort` statement grammar supports `abort$condition 'message', display_items` (with a STRING message) and `abort$condition` (bare), but does not support `abort$condition display_items` where the display items are identifiers without a preceding string message. This causes lop to fail parsing at line 207.

---

## Reproduction

**Model:** `lop` (`data/gamslib/raw/lop.gms`)

**Command to reproduce:**
```bash
source .venv/bin/activate
python -c "from src.ir.parser import parse_model_file; parse_model_file('data/gamslib/raw/lop.gms')"
```

**Error output:**
```
ParseError: Error: Parse error at line 208, column 1: Unexpected character: 'S'
  Set ll(s,s) 'station pair represening a line';
  ^
```

The actual failure is at line 207, but the error manifests at line 208 because the parser consumes `error02` (the display item) into the abort condition expression, then fails to parse the next `Set` statement.

**Minimal reproduction:**
```bash
python -c "
from src.ir.parser import parse_text
text = '''Set s /s1*s5/;
Parameter error02(s);
abort\\\$card(error02) error02;
Set ll(s) 'test';'''
parse_text(text)
"
```

**Error:** Same "Unexpected character: 'S'" at the `Set` line.

**Relevant GAMS code (line 207):**
```gams
abort$card(error02) error02;
```

This aborts if `card(error02) > 0` and displays the contents of `error02`. No string message is provided — just the identifier to display.

---

## Root Cause

The `abort_base` rule in `src/gams/gams_grammar.lark` (lines 549-557) has these variants:

```lark
abort_base: "abort"i DOLLAR "[" expr "]" STRING ("," display_item)*  -> abort_cond_square_msg
          | "abort"i DOLLAR "[" expr "]"                              -> abort_cond_square
          | "abort"i DOLLAR "(" expr ")" STRING ("," display_item)*   -> abort_cond_paren_msg
          | "abort"i DOLLAR "(" expr ")"                              -> abort_cond_paren
          | "abort"i DOLLAR expr STRING ("," display_item)*           -> abort_cond_plain_msg
          | "abort"i DOLLAR expr                                      -> abort_cond_plain
          | "abort"i STRING ("," display_item)*                       -> abort_msg
          | "abort"i                                                  -> abort_plain
```

The `abort_cond_plain_msg` variant requires `STRING` after the condition expression. The `abort_cond_plain` variant has no display items. There is no variant for `abort$condition display_items` without a STRING.

When parsing `abort$card(error02) error02;`:
- The parser tries `abort_cond_plain_msg` but `error02` is not a STRING
- Falls back to `abort_cond_plain`: `abort$expr` → consumes `card(error02) error02` as the entire expression (since the Earley parser can interpret `func_call identifier` as a valid expression continuation)
- The `;` terminates the abort statement, but the parse tree is malformed
- The subsequent `Set` statement cannot be parsed

---

## Proposed Fix

Add variants to `abort_base` that support display items without a string message:

```lark
abort_base: ...existing variants...
          | "abort"i DOLLAR "(" expr ")" ("," display_item)*   -> abort_cond_paren_display
          | "abort"i DOLLAR "[" expr "]" ("," display_item)*   -> abort_cond_square_display
```

For the bare `$expr` form (without parens/brackets), this is harder because `abort$cond item1, item2` is ambiguous — the parser cannot distinguish where the condition ends and display items begin. The parenthesized/bracketed forms avoid this ambiguity.

However, GAMS accepts `abort$card(error02) error02;` where `card(error02)` is a complete expression (function call). One approach is to use the `condition` rule which already handles `DOLLAR "(" expr ")"` and `DOLLAR expr` forms.

Alternative: Change `abort_cond_plain` to accept optional comma-separated display items:
```lark
          | "abort"i DOLLAR expr ("," display_item)*  -> abort_cond_plain
```

This works because `error02` after a space is ambiguous as expression continuation, but with a comma separator it would be clear. In the lop case, `abort$card(error02) error02;` has no comma, so the display item approach might not directly solve it. The condition may need to be parenthesized/bracketed using the `condition` rule.

Further investigation needed on whether GAMS requires the condition to be a single function call / identifier in the bare `$expr` form, or if any expression is valid.

---

## Context

This issue was exposed by the Issue #711 fix (nested loop support) which advanced lop past line 176. The lop model now parses its nested loop structure but fails at the `abort$card(error02) error02;` statement.
