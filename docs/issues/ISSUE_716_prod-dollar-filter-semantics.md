# Parser: prod(i$cond, body) Dollar-Filter Folded as Multiplication Corrupts Semantics

**GitHub Issue:** [#716](https://github.com/jeffreyhorn/nlp2mcp/issues/716)
**Status:** Open
**Severity:** High — Produces mathematically incorrect results for prod with filtered domains
**Discovered:** 2026-02-13 (PR #712 review, Copilot comment)
**Affected Models:** weapons (confirmed), any model using `prod` with dollar-filtered domains

---

## Problem Summary

The parser's `_handle_aggregation` method (in `src/ir/parser.py`) folds dollar-conditional filters into the aggregation body as multiplication for both `Sum` and `Prod`:

```python
# Apply condition by multiplying: sum(i$cond, expr) => sum(i, cond * expr)
if condition_expr is not None:
    body = Binary("*", condition_expr, body)
```

For `Sum`, this is mathematically correct: excluded elements contribute `0 * body = 0` to the sum.

For `Prod`, this is **mathematically wrong**: `prod(w$cond, body)` should give the product over elements where `cond != 0` (excluded elements contribute the multiplicative identity **1**). But `prod(w, cond * body)` makes elements where `cond=0` contribute `0` to the product, **zeroing the entire result**.

---

## Reproduction

**GAMS input (weapons model, line 63):**
```gams
probe(t)..  prob(t) =e= 1 - prod(w$td(w,t), (1-td(w,t))**x(w,t));
```

**Current IR:**
```python
Prod(("w",), Binary("*", ParamRef("td", ("w", "t")), Binary("**", ...)))
```

**Emitted GAMS (incorrect):**
```gams
prod(w, td(w,t) * (1 - td(w,t)) ** x(w,t))
```

When `td(w,t) = 0` for some `w`, the multiplication makes that element contribute `0` to the product, zeroing the entire result.

**Correct emission should be:**
```gams
prod(w$td(w,t), (1 - td(w,t)) ** x(w,t))
```

This preserves the exclusion semantics — elements where `td(w,t) = 0` are skipped entirely (contributing the multiplicative identity 1).

---

## Root Cause

The `_handle_aggregation` method in `src/ir/parser.py` (around line 3614) applies the same condition-folding logic to both `Sum` and `Prod`:

```python
if condition_expr is not None:
    body = Binary("*", condition_expr, body)
```

The `Prod` AST node (in `src/ir/ast.py`) has no `condition` field — only `index_sets` and `body`. The condition is lost after being multiplied into the body.

---

## Proposed Fix

Either:
1. Add an optional `condition: Expr | None` field to `Prod` (and optionally `Sum`) in `src/ir/ast.py`, and update `_handle_aggregation` to store the condition separately for `Prod`
2. Or wrap the body in a `DollarConditional` node instead of multiplying, so `expr_to_gams` can emit `prod(w$cond, body)`

Both approaches require updates to:
- `src/ir/ast.py` — AST node definition
- `src/ir/parser.py` — `_handle_aggregation` method
- `src/emit/expr_to_gams.py` — emission logic for `Prod` (and potentially `Sum`)
- `src/ad/evaluator.py` — evaluation logic
- `src/emit/equations.py` — equation handling

---

## Context

This issue was identified during PR #712 code review (Copilot comment on `data/gamslib/mcp/weapons_mcp.gms`). The `prod` emission code added in Issue #709 correctly translates `Prod` nodes to GAMS syntax, but the underlying IR representation of dollar-filtered `prod` is mathematically incorrect due to the condition-folding in the parser.
