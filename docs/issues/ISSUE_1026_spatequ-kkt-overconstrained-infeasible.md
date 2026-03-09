# spatequ: KKT System Overconstrained — Model Infeasible

**GitHub Issue:** [#1026](https://github.com/jeffreyhorn/nlp2mcp/issues/1026)
**Status:** OPEN
**Severity:** Medium — solve completes but model status 5 (Locally Infeasible)
**Date:** 2026-03-09
**Affected Models:** spatequ

---

## Problem Summary

After fixing Issue #1021 (empty equation execution errors), the spatequ model now translates and solves without execution errors, but the PATH solver reports Model Status 5 (Locally Infeasible). The KKT transformation produces an overconstrained system because it includes equations from the NLP model that are not part of the original hand-written MCP formulation.

---

## Error Details

```
**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      5 Locally Infeasible
```

Key infeasible equations:
```
stat_dint(Reg1,Com1)..  nu_DEMINT(Reg1,Com1) =E= 1 ; (LHS = 0, INFES = 1 ****)
stat_sint(Reg1,Com1)..  nu_SUPINT(Reg1,Com1) =E= -1 ; (LHS = 0, INFES = 1 ****)
stat_tc..  nu_TRANSCOST =E= -1 ; (LHS = 0, INFES = 1 ****)
```

These stationarity equations have constant RHS (no variable dependence), making them trivially infeasible unless the corresponding multipliers are set to specific non-zero values.

---

## Root Cause

The original spatequ.gms defines multiple models:
```gams
Model
   P2R3_Linear     / DEM, SUP, SDBAL, PDIF, TRANSCOST, SX, DX /
   P2R3_NonLinear  / P2R3_Linear, DEMINT, SUPINT, OBJECT /
   P2R3_MCP        / DEM, SUP, IN_OUT.P, DOM_TRAD.X /;
```

The hand-written MCP model (`P2R3_MCP`) uses only 4 equations: `DEM, SUP, IN_OUT, DOM_TRAD`. However, our tool's `model_equations` captures the LP model (`P2R3_Linear`) with 7 equations: `DEM, SUP, SDBAL, PDIF, TRANSCOST, SX, DX`. The KKT transformation then includes ALL of these plus their derivatives, creating stationarity equations for variables like `DINT`, `SINT`, `TC`, and `OBJ` that appear only in the integral/objective equations.

These "extra" stationarity equations (e.g., `stat_dint: nu_DEMINT = 1`) are constant — they have no variable dependence and cannot be satisfied by the solver. The original MCP model avoids this by using only the 4 core equations.

The underlying issue is that the parser captures `model_equations` from the first model declaration encountered, not from the model referenced by the last `solve` statement. When multiple models are declared, the wrong set of equations may be used.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/spatequ.gms -o /tmp/spatequ_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/spatequ_mcp.gms lo=0 o=/tmp/spatequ_mcp.lst

# Check model status:
grep 'MODEL STATUS' /tmp/spatequ_mcp.lst
# Expected: MODEL STATUS 5 Locally Infeasible

# Check infeasible stationarity equations:
grep 'INFES' /tmp/spatequ_mcp.lst | head -10
```

---

## Suggested Fix

### Approach A: Associate model_equations with solve statements (preferred)
When multiple `Model` and `Solve` statements exist, the parser should track which model is associated with which solve statement. The tool should use the `model_equations` from the model referenced by the selected solve statement, not the first model encountered.

For spatequ, the last solve uses `P2R3_MCP`, so `model_equations` should be `['DEM', 'SUP', 'IN_OUT', 'DOM_TRAD']`.

### Approach B: Detect and skip constant stationarity equations
After building the KKT system, detect stationarity equations that have constant LHS (no variable terms). These equations are trivially infeasible and indicate extra variables/equations that shouldn't be in the system. Exclude them and their associated variables.

**Effort estimate:** 4-8h for Approach A (requires parser refactoring for multi-model support)

---

## Files Likely Affected

| File | Change |
|------|--------|
| `src/ir/parser.py` | Track model_equations per model declaration and per solve statement |
| `src/ir/model_ir.py` | Store model → equations mapping |
| `src/kkt/partition.py` | Filter equalities/inequalities by selected model's equations |

---

## Related Issues

- Issue #1021: spatequ empty equation execution errors (FIXED — this issue is the residual)
