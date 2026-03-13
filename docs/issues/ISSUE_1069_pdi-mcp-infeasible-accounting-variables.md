# pdi: MCP Structurally Infeasible — Accounting Variable Stationarity

**GitHub Issue:** [#1069](https://github.com/jeffreyhorn/nlp2mcp/issues/1069)
**Model:** pdi (SEQ=140) — Price-Directed Decomposition
**Type:** LP
**Category:** KKT construction bug (accounting variable stationarity)

---

## Summary

The pdi model is structurally infeasible (model_status=4, 0 iterations) because accounting/intermediate variables (`holding`, `production`, `transport`, `revenue`) get trivial stationarity equations of the form `1 + nu_xxx =E= 0`, which force the free multiplier to a constant. This is the same pattern as issue #764.

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/pdi.gms -o data/gamslib/mcp/pdi_mcp.gms
cd /tmp && gams /path/to/data/gamslib/mcp/pdi_mcp.gms lo=2 o=pdi.lst
# Expected: MODEL STATUS 4 (Infeasible), 0 iterations
```

## Model Structure

- **Sets**: `p` (plants), `d` (distribution centers), `m` (months), `c` (commodities)
- **Objective**: Maximize `profit`
- **Decision variables**: `x(p,d,m)` (transport), `pn(p,m)` (normal production), `po(p,m)` (overtime production), `s(d,m)` (sales), `h(d,m)` (inventory), `dm(d,m)` (demand)
- **Accounting variables**: `profit`, `revenue`, `production`, `transport`, `holding`
- **Accounting equations**:
  - `ar.. revenue =E= sum(...)`
  - `at.. transport =E= sum(...)`
  - `ap.. production =E= sum(...)`
  - `ah.. holding =E= sum(...)`
  - `apr.. profit =E= revenue - transport - production - holding + 10`

## Root Cause

The accounting variables (`revenue`, `transport`, `production`, `holding`) appear in the objective chain only through their defining equations. The KKT builder generates stationarity equations for each:

```gams
stat_holding..    1 + nu_ah =E= 0;
stat_production.. 1 + nu_ap =E= 0;
stat_transport..  1 + nu_at =E= 0;
stat_revenue..   -1 + nu_ar =E= 0;
```

These equations force `nu_ah = -1`, `nu_ap = -1`, `nu_at = -1`, `nu_ar = 1`. Combined with the MCP complementarity structure (free multipliers paired with equality constraints), this creates a structurally infeasible system — the multiplier values are over-determined.

The correct approach is to either:
1. Substitute accounting variables out before generating KKT conditions (inline `revenue = sum(...)` etc. into the `profit` equation), or
2. Propagate the objective gradient chain through accounting equations so that stationarity equations for decision variables include the contribution of these accounting definitions.

This is the same accounting variable pattern documented in issue #764.

## PATH Solver Output

```
MODEL STATUS      4 Infeasible
0 iterations (structural infeasibility detected at preprocessing)
```

65 total INFES markers in the solution report.

## Fix Approach

Same fix as #764: implement accounting variable elimination or gradient chain propagation to handle intermediate variables that appear only as bookkeeping quantities in the objective chain.

## Files

- `data/gamslib/raw/pdi.gms` — original LP model
- `data/gamslib/mcp/pdi_mcp.gms` — generated MCP
- Key equations: `stat_holding`, `stat_production`, `stat_transport`, `stat_revenue`
