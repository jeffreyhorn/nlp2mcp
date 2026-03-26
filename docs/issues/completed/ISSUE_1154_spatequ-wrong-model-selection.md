# spatequ: Wrong Model/Objective Selection for KKT Conversion

**GitHub Issue:** [#1154](https://github.com/jeffreyhorn/nlp2mcp/issues/1154)
**Status:** FIXED
**Severity:** High — produces incorrect KKT system, model infeasible (MODEL STATUS 5)
**Date:** 2026-03-25
**Affected Models:** spatequ (and potentially any GAMS file with multiple model/solve statements)

---

## Problem Summary

The spatequ GAMS file defines four models and four solve statements:

```gams
Model
   P2R3_Linear     / DEM, SUP, SDBAL, PDIF, TRANSCOST, SX, DX /
   P2R3_LinearLog  / DEMLOG, SUPLOG, SDBAL, PDIF, TRANSCOST, SX, DX /
   P2R3_NonLinear  / P2R3_Linear, DEMINT, SUPINT, OBJECT /
   P2R3_MCP        / DEM, SUP, IN_OUT.P, DOM_TRAD.X /;

solve P2R3_Linear    using  lp minimizing TC;
solve P2R3_LinearLog using nlp minimizing TC;
solve P2R3_NonLinear using nlp maximizing OBJ;
solve P2R3_MCP using mcp;
```

The nlp2mcp tool should convert `P2R3_Linear` (the first LP solve) to an MCP. Instead, it:
1. **Correctly** selects the model equations from `P2R3_Linear`: `DEM, SUP, SDBAL, PDIF, TRANSCOST, SX, DX`
2. **Incorrectly** selects the objective from `P2R3_NonLinear`: `maximize OBJ` (should be `minimize TC`)

This causes the KKT system to include stationarity terms from equations NOT in the LP model (e.g., `nu_DEMINT`, `nu_SUPINT` appear in `stat_p` and `stat_dint`), making the system overconstrained and infeasible.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/spatequ.gms -o /tmp/spatequ_mcp.gms --skip-convexity-check
gams /tmp/spatequ_mcp.gms lo=2
```

**Result:** MODEL STATUS 5 (Locally Infeasible), 0 compilation errors.

**Diagnostic:**
```python
from src.ir.parser import parse_model_file
model = parse_model_file('data/gamslib/raw/spatequ.gms')
print('Model equations:', list(model.model_equations))
# Output: ['DEM', 'SUP', 'SDBAL', 'PDIF', 'TRANSCOST', 'SX', 'DX']  ← correct
print('Objective:', model.objective)
# Output: ObjectiveIR(sense=MAX, objvar='OBJ', expr=None)  ← WRONG, should be MIN TC
```

**Evidence in MCP output:**
```gams
stat_dint(r,c).. -1 + nu_DEMINT(r,c) =E= 0;
stat_sint(r,c).. 1 + nu_SUPINT(r,c) =E= 0;
```
`DEMINT` and `SUPINT` are from `P2R3_NonLinear`, not `P2R3_Linear`.

---

## Expected Behavior

The tool should select the FIRST non-MCP solve statement (or the solve that matches the model equations) and use its objective:
- Model: `P2R3_Linear`
- Objective: `minimize TC`
- Equations: `DEM, SUP, SDBAL, PDIF, TRANSCOST, SX, DX`

The stationarity should NOT reference multipliers for equations outside the model.

---

## Root Cause

The parser's `_handle_solve()` method processes all solve statements sequentially and the last one that sets the objective wins. The model equations are correctly extracted from the LP model, but the objective is overwritten by later solve statements.

**Affected files:**
- `src/ir/parser.py` — `_handle_solve()` method (~line 3496)
- Potentially `src/kkt/assemble.py` — should filter constraints to only those in `model_equations`

---

## Fix Approach

Two complementary fixes needed:

1. **Parser**: When multiple solve statements exist, the parser should associate the objective with the specific model being converted (the first LP/NLP solve, not later MCP solves). Consider storing solve info per-model or preferring the first non-MCP solve.

2. **KKT Assembly**: The stationarity builder should only include constraints that are in `model.model_equations`, ignoring equations defined but not in the selected model. This is a safety net even if the parser fix is correct.

**Effort estimate:** 2-3 hours

---

## Fix Applied

Two changes:

1. **`src/ir/parser.py` — `_handle_solve()`**: Store per-model objectives in `_solve_objectives` dict alongside the existing last-wins behavior. This preserves all solve info for later reconciliation.

2. **`src/ir/normalize.py` — `normalize_model()`**: Added reconciliation at the start. When the current model's equation list references another model by name (e.g., `P2R3_NonLinear / P2R3_Linear, DEMINT, SUPINT, OBJECT /`), detect that it's a superset and switch to the referenced sub-model if that sub-model has a stored objective. This correctly selects `P2R3_Linear` with `minimize TC` for spatequ.

**Result:** spatequ MCP now uses only the 7 LP model equations (DEM, SUP, SDBAL, PDIF, TRANSCOST, SX, DX) with `minimize TC`. The stationarity equations no longer reference `nu_DEMINT` or `nu_SUPINT`.

**Note:** spatequ still shows MODEL STATUS 5 (infeasible) due to a separate issue with incomplete Jacobian entries for `p(r,c)` inside `sum(cc, BetaD(r,c,cc)*p(r,c))` — the alias `cc` vs `c` differentiation is not fully handled.

---

## Related Issues
- [#1038](https://github.com/jeffreyhorn/nlp2mcp/issues/1038) — spatequ Jacobian domain mismatch (partially fixed in PR #1153)
- [#1026](https://github.com/jeffreyhorn/nlp2mcp/issues/1026) — model equation selection (closed, but objective selection still wrong)
