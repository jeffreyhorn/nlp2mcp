# weapons: Model Infeasible — Jacobian Condition Evaluation Failure

**GitHub Issue:** [#1057](https://github.com/jeffreyhorn/nlp2mcp/issues/1057)
**Status:** OPEN
**Severity:** High — model_infeasible (66 infeasible equations)
**Date:** 2026-03-11
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

The objective value is computed (1728.973) but does not match the NLP objective.

---

## Root Cause

In the original model:
```gams
Parameter tm(t) 'minimum number of weapons per target';
tm(t) = td("target",t);

minw(t)$tm(t).. sum(w$td(w,t), x(w,t)) =g= tm(t);
```

The equation `minw(t)` is conditioned on `$tm(t)` — it only exists for targets with a minimum weapon requirement. The parameter `tm` is computed from `td("target",t)`, which is a cross-reference into table data.

During Jacobian computation, `_enumerate_equation_instances()` tries to evaluate the condition `$tm(t)` for each value of `t`. Since `tm` has expression-based values (assigned via `tm(t) = td("target",t)`), the condition evaluator cannot determine which `t` values have nonzero `tm`. It falls back to "including instance by default," generating equation instances for **all** `t` values instead of only those where `tm(t) > 0`.

This produces extra stationarity terms and complementarity equations for targets that shouldn't have the `minw` constraint, making the KKT system inconsistent → infeasible.

Additionally, the `report` parameter warning ("declared without domain but used with indexed values") suggests the emitter may include post-solve reporting code that causes issues.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/weapons.gms -o /tmp/weapons_mcp.gms
gams /tmp/weapons_mcp.gms lo=2
# Compiles OK but: MODEL STATUS 5 Locally Infeasible, 66 INFEASIBLE
```

---

## Proposed Fix

The condition evaluator in `src/ad/constraint_jacobian.py` (`_evaluate_condition()` or `enumerate_equation_instances()`) needs to handle expression-based parameters. Options:

1. **Static evaluation:** Pre-evaluate `tm(t) = td("target",t)` by looking up `td` data statically and computing `tm` values before condition checking
2. **Expression-based parameter resolution:** When a parameter has expression values (`p_expr` / `p_expr_map`), attempt to resolve the expression using known data values
3. **Conservative skip:** When condition can't be evaluated, default to EXCLUDING the instance (opposite of current behavior), since the condition is there to restrict the equation domain

Option 1 is the most robust but requires general expression evaluation capability. Option 3 is simpler but risks excluding valid instances.

---

## Related

- This is a pre-existing issue on main; re-translation with current code exposes the bug
- Similar to condition evaluation failures in other models with expression-based parameters
- The `report` parameter warning may be a separate minor issue
