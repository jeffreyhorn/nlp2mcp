# Grammar: Tuple Domain Dollar Condition Outside Parentheses (lop)

**GitHub Issue:** [#718](https://github.com/jeffreyhorn/nlp2mcp/issues/718)
**Status:** Open
**Severity:** Medium — Blocks parsing of models using `sum((i,j)$cond, expr)` syntax
**Discovered:** 2026-02-13 (Sprint 19, after Issue #715 fix advanced lop past abort statement)
**Affected Models:** lop (line 252 after preprocessing)

---

## Problem Summary

The grammar does not support dollar conditions on tuple domains when the `$` appears outside the tuple parentheses: `sum((s1,s2)$cond, expr)`. Only `sum((s1,s2$cond), expr)` (dollar inside the parens) is supported. GAMS accepts both forms, and the outside-parens form is common in GAMSLib models.

---

## Reproduction

**Model:** `lop` (`data/gamslib/raw/lop.gms`)

**Command to reproduce:**
```bash
source .venv/bin/activate
python -m src.cli data/gamslib/raw/lop.gms -o /tmp/lop_mcp.gms --diagnostics
```

**Error output:**
```
ParseError: Error: Parse error at line 254, column 1: Unexpected character: 'M'
  Model lopdt / deffreqlop, dtlimit, defobjdtlop /;
  ^
```

The actual failure is at line 252 (preprocessed): `defobjdtlop.. obj =e= sum((s1,s2)$od(s1,s2), dt(s1,s2));` — the parser cannot handle the tuple domain dollar condition and enters a bad state, causing the next `Model` statement to fail.

**Minimal reproduction:**
```bash
source .venv/bin/activate
python -c "
from src.ir.parser import parse_text
text = '''
Sets s1 /a/ ; Sets s2 /b/ ;
Parameter od(s1,s2); Parameter dt(s1,s2);
Variables obj;
Equations eq1;
eq1.. obj =e= sum((s1,s2)\\\$od(s1,s2), dt(s1,s2));
'''
parse_text(text)
"
```

**Error:** `ParseError: Unexpected end of file. Expected one of: COMMA`

**Working alternative** (dollar inside parens):
```gams
eq1.. obj =e= sum((s1,s2$od(s1,s2)), dt(s1,s2));
```

---

## Root Cause

The `sum_domain` and `index_spec` rules in `src/gams/gams_grammar.lark`:

```lark
sum_expr: SUM_K "(" sum_domain "," expr ")"
sum_domain: index_spec
          | "(" index_spec ")"  -> tuple_domain

index_spec: index_list (DOLLAR expr)?
          | index_list DOLLAR "[" expr "]"
```

The `tuple_domain` rule wraps `index_spec` in parentheses: `"(" index_spec ")"`. The `index_spec` rule supports `index_list$expr` (dollar condition inside the parens). But there is no rule for a dollar condition OUTSIDE the tuple parens.

When parsing `sum((s1,s2)$od(s1,s2), dt(s1,s2))`:
- `sum(` — opening of sum
- `(s1,s2)` — parsed as tuple_domain (closing paren consumed)
- `$od(s1,s2)` — now outside the tuple, dollar condition has no matching rule
- The Earley parser cannot continue and the parse fails

## Proposed Fix

Add a variant to `sum_domain` that supports a dollar condition after the tuple:

```lark
sum_domain: index_spec
          | "(" index_spec ")" (DOLLAR expr)?        -> tuple_domain
          | "(" index_spec ")" DOLLAR "[" expr "]"    -> tuple_domain
```

Or add a separate rule:
```lark
sum_domain: index_spec
          | "(" index_spec ")"                        -> tuple_domain
          | "(" index_spec ")" DOLLAR expr            -> tuple_domain_cond
          | "(" index_spec ")" DOLLAR "[" expr "]"    -> tuple_domain_cond
```

The parser's `_ModelBuilder` would need a handler for the new `tuple_domain_cond` tree if a new alias is used, or would work automatically if the existing `tuple_domain` rule is extended.

**Note:** The `prod` expression uses the same `sum_domain` rule, so the fix would also apply to `prod((i,j)$cond, expr)`.

---

## GAMS Reference

From lop.gms (line 257 original, line 252 preprocessed):
```gams
defobjdtlop.. obj =e= sum((s1,s2)$od(s1,s2), dt(s1,s2));
```

This is standard GAMS syntax where the dollar condition filters the tuple domain `(s1,s2)` by the parameter `od(s1,s2)`.
