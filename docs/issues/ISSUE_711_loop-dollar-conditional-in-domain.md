# Grammar: Dollar Conditional in Loop Domain

**GitHub Issue:** [#711](https://github.com/jeffreyhorn/nlp2mcp/issues/711)

**Issue:** The parser cannot handle dollar conditionals inside a `loop()` domain specification, e.g., `loop(r$(ord(r) > 1 and card(unvisit)), ...)`. The `$` after the loop index variable is not recognized in this context.

**Status:** Open
**Severity:** Medium — Loop domain filtering with `$` is a common GAMS pattern
**Discovered:** 2026-02-13 (Sprint 19, after Issue #706 fix advanced lop past its solve keyword typo)
**Affected Models:** lop (confirmed, line 176)

---

## Problem Summary

GAMS `loop()` statements can filter the loop domain using dollar conditionals:

```gams
loop(r$(condition), body);
```

This iterates over elements of set `r` where `condition` is true. Our grammar's `loop_stmt` rule does not support dollar conditionals in the loop domain.

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
Error: Parse error at line 176, column 7: Unexpected character: '$'
  loop(r$(ord(r) > 1 and card(unvisit)),
        ^
```

**Relevant GAMS code (lines 176-190):**
```gams
loop(root,
   from(root) = yes;
   unvisit(s) = yes;
   visit(s)   =  no;
   loop(r$(ord(r) > 1 and card(unvisit)),
      unvisit(from) =  no;
      visit(from)   = yes;
      to(unvisit) = sum(tree(root,from,unvisit), yes);
      loop(from,
         k(s2,s3)$l(root,from,s2,s3)  = yes;
         v(s2,r1)$lr(root,from,s2,r1) = yes;
```

The inner `loop(r$(ord(r) > 1 and card(unvisit)), ...)` uses `$` to filter the loop domain. Additionally, assignments inside the loop body use dollar conditionals (`k(s2,s3)$l(...)`) which are handled by Issue #705's `conditional_assign_general` fix.

---

## Root Cause

The `loop_stmt` rule in `src/gams/gams_grammar.lark` expects a simple loop domain:

```lark
loop_stmt: LOOP_K "(" ID "," exec_stmt+ ")" SEMI                      -> loop_stmt
         | LOOP_K "(" "(" id_list ")" "," exec_stmt+ ")" SEMI         -> loop_stmt_paren
         | LOOP_K "(" ID "$" "(" expr ")" "," exec_stmt+ ")" SEMI     -> loop_stmt_filtered
         | LOOP_K "(" "(" id_list ")" "$" "(" expr ")" "," exec_stmt+ ")" SEMI -> loop_stmt_paren_filtered
```

The `loop_stmt_filtered` rule expects `ID "$" "(" expr ")"` — a dollar sign followed by parenthesized expression. But the lop model uses `r$(ord(r) > 1 and card(unvisit))` where the dollar sign is immediately adjacent to the identifier (no space), and the condition includes function calls like `ord()` and `card()`.

The issue may be that the `$` is being lexed as part of the identifier `r$` rather than as a separate DOLLAR token, or that the condition expression `ord(r) > 1 and card(unvisit)` is not being parsed correctly in this context.

Looking more closely, the grammar uses `"$"` (string literal) rather than `DOLLAR` (terminal). With Earley parser, string literals in rules are handled differently. The actual issue needs investigation — it could be:

1. Lexer tokenization: `r$` being consumed as a single token
2. The `$` not matching because `DOLLAR` terminal takes priority over the string literal `"$"`
3. The expression grammar inside the filter not supporting `ord()`, `card()`, `and`

---

## Proposed Fix

1. Change `"$"` to `DOLLAR` in the `loop_stmt_filtered` and `loop_stmt_paren_filtered` rules for consistency with the `condition` rule.
2. Alternatively, use the `condition` rule (which already handles all dollar conditional forms) in the loop domain:

```lark
loop_stmt: LOOP_K "(" ID condition? "," exec_stmt+ ")" SEMI -> loop_stmt
```

This would unify loop domain filtering with the condition handling used in equations and assignments.

---

## Context

This issue was exposed by the Sprint 19 Issue #706 fix (solve keyword typo tolerance) which advanced lop past line 149. The lop model now parses its solve statement but fails when it reaches the nested `loop` with dollar-filtered domain at line 176.

The lop model also uses dollar conditionals on assignments inside the loop body (`k(s2,s3)$l(root,from,s2,s3) = yes;`), which are now supported by the `conditional_assign_general` grammar from Issue #705.
