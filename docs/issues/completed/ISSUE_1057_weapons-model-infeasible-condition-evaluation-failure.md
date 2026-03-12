# weapons: Model Infeasible — Jacobian Condition Evaluation Failure

**GitHub Issue:** [#1057](https://github.com/jeffreyhorn/nlp2mcp/issues/1057)
**Status:** FIXED
**Severity:** High — model_infeasible (66 infeasible equations)
**Date:** 2026-03-11
**Fixed:** 2026-03-12
**Affected Models:** weapons

---

## Problem Summary

The weapons model translates and compiles successfully but PATH reports Model Status 5 (Locally Infeasible) with 66 infeasible equations. The root cause is that the Jacobian computation fails to evaluate dollar conditions involving expression-based parameters, leading to incorrect or extra equation instances being included.

---

## Error Details

Translation warnings:
```
UserWarning: Failed to evaluate condition for minw('20',):
  Failed to evaluate condition ParamRef(tm(t)) with indices ('20',):
  Parameter 'tm' has expression-based values that cannot be evaluated statically
  for indices ('20',). Including instance by default.
```

PATH solver result:
```
**** MODEL STATUS      5 Locally Infeasible
REPORT SUMMARY: 66 INFEASIBLE (INFES)
```

---

## Root Cause

In the original model:
```gams
Parameter tm(t) 'minimum number of weapons per target';
tm(t) = td("target",t);

minw(t)$tm(t).. sum(w$td(w,t), x(w,t)) =g= tm(t);
```

The equation `minw(t)` is conditioned on `$tm(t)` — it only exists for targets with a minimum weapon requirement. The parameter `tm` is computed from `td("target",t)`, which is a cross-reference into table data.

The condition evaluator in `condition_eval.py` could not evaluate `tm(t)` because `tm` had expression-based values (no static data). It fell back to "including instance by default," generating equation instances for **all** `t` values instead of only those where `tm(t) > 0`.

---

## Fix

**File:** `src/ir/condition_eval.py` — `_eval_expr()` ParamRef handler (~line 130)

When a parameter has expression-based values and the static lookup fails, the evaluator now attempts to recursively evaluate the expression body. For `tm(t) = td("target",t)`, it:
1. Finds the matching expression `(('t',), ParamRef(td("target",t)))`
2. Builds an index map `{"t": concrete_value}`
3. Recursively evaluates `ParamRef(td("target",t))` → looks up `td("target", concrete_value)` in static data

This correctly resolves `tm("1")` = 30.0, `tm("2")` = 0.0, etc., so the `$tm(t)` condition properly filters equation instances.

---

## Verification

- **Before fix:** MODEL STATUS 5 (Locally Infeasible), 66 infeasible equations
- **After fix:** MODEL STATUS 1 (Optimal), 0 infeasible equations
- **Quality gate:** 4141 tests pass, typecheck/lint/format clean

---

## Related

- #720 Expression-based parameter evaluation (original limitation this fix extends)
- #877 Condition evaluation fallback behavior
