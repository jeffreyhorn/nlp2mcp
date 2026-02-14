# Parser: prod(i$cond, body) Dollar-Filter Folded as Multiplication Corrupts Semantics

**GitHub Issue:** [#716](https://github.com/jeffreyhorn/nlp2mcp/issues/716)
**Status:** Fixed
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

---

## Fix Applied

**Approach:** Added an optional `condition: Expr | None = None` field to both `Sum` and `Prod` AST nodes, and updated all consumers to preserve the condition through transformations.

**Files modified:**

1. **`src/ir/ast.py`** — Added `condition: Expr | None = None` field to both `Sum` and `Prod` dataclasses. Updated `children()` to yield condition, updated `__repr__` to show condition.

2. **`src/ir/parser.py`** — Changed `_handle_aggregation` to store condition separately instead of folding as `Binary("*", cond, body)`. Now passes condition directly to `Sum`/`Prod` constructors. Also updated `_contains_function_call` and `_contains_variable_reference` to recurse into condition.

3. **`src/emit/expr_to_gams.py`** — Added `_agg_domain_str()` helper to format `idx$cond` domain strings. Updated `Sum` and `Prod` emission to use 3-field destructuring and emit dollar-filter syntax. Updated alias collection and conflict resolution to handle condition.

4. **`src/ad/derivative_rules.py`** — Updated `_apply_index_substitution`, `_diff_sum`, `_partial_collapse_sum`, and `_diff_prod` to preserve condition through differentiation.

5. **`src/ad/ad_core.py`** — Updated `simplify()` and `simplify_advanced()` to simplify and preserve condition.

6. **`src/kkt/stationarity.py`** — Updated `_replace_indices_in_expr` to process condition.

7. **`src/kkt/reformulation.py`** — Updated `_replace_min_max_call` to process condition.

8. **`src/ad/constraint_jacobian.py`** — Updated `_substitute_indices` to process condition.

9. **`src/ir/transformations/cse_advanced.py`** — Updated `_expression_key` and `_replace_subexpression` to handle condition.

10. **`src/ir/simplification_pipeline.py`** — Updated `_expression_size` to include condition size.

11. **`src/ad/sparsity.py`** — Updated `_collect_variables` to recurse into condition.

12. **`src/ir/metrics.py`** — Updated `count_operations` to include condition operations.

13. **`src/ad/minmax_flattener.py`** — Updated `visit_sum` to transform and preserve condition.

**Verification:**
- Weapons MCP output now correctly emits `prod(w$td(w,t), (1 - td(w,t)) ** x(w,t))` instead of `prod(w, td(w,t) * (1 - td(w,t)) ** x(w,t))`
- Quality gate: typecheck ✓, lint ✓, format ✓, 3308 tests pass ✓
