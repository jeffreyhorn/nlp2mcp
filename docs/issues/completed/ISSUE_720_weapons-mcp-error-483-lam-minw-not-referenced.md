# MCP: GAMS Error 483 — Multiplier lam_minw Not Referenced in Equations (weapons)

**GitHub Issue:** [#720](https://github.com/jeffreyhorn/nlp2mcp/issues/720)
**Status:** Fixed
**Severity:** High — Generated MCP code fails GAMS compilation; model cannot be solved
**Discovered:** 2026-02-13 (Sprint 19, after Issue #713 fix corrected table data)
**Fixed:** 2026-02-13
**Affected Models:** weapons

---

## Problem Summary

The weapons model generated MCP code with multiplier `lam_minw` declared and mapped but never appearing in any equation body, causing GAMS Error 483. Two root causes:

1. **AD: Dollar condition dropped on sum collapse** — When differentiating `sum(w$td(w,t), x(w,t))` w.r.t. `x(w,t)`, the sum collapses to yield the body derivative, but the dollar condition `$td(w,t)` was discarded. Result was `1` instead of `1$td(w,t)`.

2. **Condition evaluator: Expression-based parameters treated as zero** — The equation `minw(t)$tm(t)` has condition `tm(t)` where `tm` is defined via an expression (`tm(t) = td("target",t)`), not static values. The condition evaluator returned `0.0` for all instances, causing all `minw` instances to be excluded from the Jacobian.

---

## Fix

### 1. AD: Preserve dollar condition on sum collapse (`src/ad/derivative_rules.py`)

When a conditioned sum collapses (the summation index is matched and eliminated), multiply the derivative result by the substituted condition (via `Binary("*", result, subst_cond)`) instead of wrapping it in a `DollarConditional`, to avoid GAMS structural exclusion issues. Fixed in three code paths:

- **`_sum_should_collapse` path**: Full collapse (sum indices == wrt_indices)
- **`_partial_index_match` path**: Partial match (wrt_indices has more indices than sum)
- **`_partial_collapse_sum` path**: When remaining sum indices are empty after matching

### 2. Condition evaluator: Raise for expression-based parameters (`src/ir/condition_eval.py`)

When a parameter lookup fails because values are empty but `param.expressions` is non-empty, raise `ConditionEvaluationError` instead of returning `0.0`. The existing catch handler in `enumerate_equation_instances` includes the instance by default when evaluation fails.

### 3. Stationarity: Handle DollarConditional in index replacement (`src/kkt/stationarity.py`)

Added `DollarConditional` case to `_replace_indices_in_expr` match statement so concrete indices in the condition are properly replaced with symbolic set indices.

### Results

- `lam_minw(t)` now appears in stationarity equations multiplied by condition `td(w,t)`
- Generated stat_x: `... + td(w,t) * lam_maxw(w) + ((-1) * td(w,t)) * lam_minw(t) =E= 0`
- All quality gates pass (typecheck, lint, format, 3315 tests)
