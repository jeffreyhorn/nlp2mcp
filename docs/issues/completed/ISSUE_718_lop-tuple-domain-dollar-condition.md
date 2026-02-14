# Grammar: Tuple Domain Dollar Condition Outside Parentheses (lop)

**GitHub Issue:** [#718](https://github.com/jeffreyhorn/nlp2mcp/issues/718)
**Status:** Fixed
**Severity:** Medium — Blocks parsing of models using `sum((i,j)$cond, expr)` syntax
**Discovered:** 2026-02-13 (Sprint 19, after Issue #715 fix advanced lop past abort statement)
**Fixed:** 2026-02-13
**Affected Models:** lop (line 252 after preprocessing)

---

## Problem Summary

The grammar does not support dollar conditions on tuple domains when the `$` appears outside the tuple parentheses: `sum((s1,s2)$cond, expr)`. Only `sum((s1,s2$cond), expr)` (dollar inside the parens) is supported. GAMS accepts both forms, and the outside-parens form is common in GAMSLib models.

---

## Reproduction

**Model:** `lop` (`data/gamslib/raw/lop.gms`)

**Minimal reproduction:**
```gams
eq1.. obj =e= sum((s1,s2)$od(s1,s2), dt(s1,s2));
```

**Error:** `ParseError: Unexpected end of file. Expected one of: COMMA`

---

## Root Cause

The `sum_domain` rule in `src/gams/gams_grammar.lark` had no variant for a dollar condition OUTSIDE the tuple parentheses:

```lark
sum_domain: index_spec
          | "(" index_spec ")"  -> tuple_domain
```

When parsing `sum((s1,s2)$od(s1,s2), ...)`:
- `(s1,s2)` is consumed as `tuple_domain` (closing paren consumed)
- `$od(s1,s2)` has no matching rule outside the tuple

---

## Fix

### 1. Grammar (`src/gams/gams_grammar.lark`)

Added `tuple_domain_cond` rule variants to `sum_domain`:

```lark
sum_domain: index_spec
          | "(" index_spec ")"                        -> tuple_domain
          | "(" index_spec ")" DOLLAR expr            -> tuple_domain_cond
          | "(" index_spec ")" DOLLAR "[" expr "]"    -> tuple_domain_cond
```

This applies to both `sum` and `prod` since both use `sum_domain`.

### 2. Parser (`src/ir/parser.py`)

Updated `_handle_aggregation` to handle the new `tuple_domain_cond` tree node:

- Extract `index_spec` from `children[0]` and condition expression from `children[2]`
- Introduced `condition_node` variable to track the source AST node for condition re-evaluation in `body_domain`, fixing an IndexError that occurred when the condition came from `tuple_domain_cond` (different child index than `index_spec` internal conditions)

### Results

- Minimal reproduction `sum((s1,s2)$od(s1,s2), dt(s1,s2))` parses and builds correctly
- lop model advances from line 252 to line 336 (new separate issue with description string)
- All quality gates pass (typecheck, lint, format, 3315 tests)
