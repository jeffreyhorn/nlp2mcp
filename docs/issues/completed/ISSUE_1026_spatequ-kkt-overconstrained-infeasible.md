# spatequ: KKT System Overconstrained — Model Infeasible

**GitHub Issue:** [#1026](https://github.com/jeffreyhorn/nlp2mcp/issues/1026)
**Status:** FIXED
**Severity:** Medium — solve completes but model status 5 (Locally Infeasible)
**Date:** 2026-03-09
**Fixed:** 2026-03-10
**Affected Models:** spatequ

---

## Problem Summary

After fixing Issue #1021 (empty equation execution errors), the spatequ model now translates and solves without execution errors, but the PATH solver reports Model Status 5 (Locally Infeasible). The KKT transformation uses the wrong model's equations because the parser sets `model_name` from the last solve statement, which is `solve P2R3_MCP using mcp` — an MCP solve with no objective.

---

## Root Cause

The spatequ.gms file has multiple solve statements:
```gams
solve P2R3_Linear    using  lp minimizing TC;
solve P2R3_LinearLog using nlp minimizing TC;
solve P2R3_NonLinear using nlp maximizing OBJ;
solve P2R3_MCP using mcp;
```

Two problems:

1. **MCP solve overwrites model_name**: The parser always set `model_name` from the last solve, even for MCP/CNS solves. Since our tool converts NLP→MCP, the MCP solve is irrelevant — we should use the last NLP solve's model (`P2R3_NonLinear`).

2. **Model references not expanded**: `P2R3_NonLinear / P2R3_Linear, DEMINT, SUPINT, OBJECT /` references another model (`P2R3_Linear`) in its equation list. GAMS expands this to include P2R3_Linear's equations, but `get_solved_model_equations()` returned the raw list including the unexpanded model reference.

---

## Fix Applied

### Change 1: Skip model_name update for MCP/CNS solves (`src/ir/parser.py`)

When `_handle_solve()` encounters an MCP/CNS solve (detected by `MCP_CNS_SOLVER` token) and there's already an NLP objective from a prior solve, the parser now preserves the previous NLP model name instead of overwriting it. This ensures the KKT pipeline uses the NLP formulation's equations.

### Change 2: Resolve model references in equation lists (`src/ir/model_ir.py`)

Added `_resolve_model_refs()` to `ModelIR` that recursively expands model references in equation lists. When `get_solved_model_equations()` returns a list containing a model name (e.g., `P2R3_Linear`), it is expanded to that model's equation list from `model_equation_map`.

For spatequ, `P2R3_NonLinear / P2R3_Linear, DEMINT, SUPINT, OBJECT /` is now resolved to:
`['DEM', 'SUP', 'SDBAL', 'PDIF', 'TRANSCOST', 'SX', 'DX', 'DEMINT', 'SUPINT', 'OBJECT']`

### Result

The generated MCP now uses the correct NLP model (`P2R3_NonLinear`) with all 10 equations. The model still reports Status 5 due to a separate Jacobian domain mismatch issue (see Issue #1038), but the equation scoping is now correct.

---

## Files Changed

| File | Change |
|------|--------|
| `src/ir/parser.py` | `_handle_solve()`: detect MCP/CNS solve, skip model_name update when NLP objective exists |
| `src/ir/model_ir.py` | `get_solved_model_equations()`: resolve model references; added `_resolve_model_refs()` helper |

---

## Quality Gate

- 4048 passed, 10 skipped, 1 xfailed
- typecheck: clean
- lint: clean
- format: clean

---

## Related Issues

- Issue #1021: spatequ empty equation execution errors (FIXED — prerequisite)
- Issue #1038: spatequ Jacobian domain mismatch in stationarity equations (OPEN — blocking remaining infeasibility)
