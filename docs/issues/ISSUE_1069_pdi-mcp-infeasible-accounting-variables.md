# pdi: MCP Structurally Infeasible — Accounting Variable Stationarity

**GitHub Issue:** [#1069](https://github.com/jeffreyhorn/nlp2mcp/issues/1069)
**Model:** pdi (SEQ=140) — Price-Directed Decomposition
**Type:** LP
**Category:** KKT construction bug (accounting variable stationarity)

---

## Summary

The pdi model is structurally infeasible (model_status=4, 0 iterations) because accounting/intermediate variables (`holding`, `production`, `transport`, `revenue`) get trivial stationarity equations of the form `1 + nu_xxx =E= 0`, which force the free multiplier to a constant. This is the same pattern as issue #764 (mexss).

## Resolution: Duplicate of #764 — Cannot Fix Yet

This issue is a duplicate of [#764](https://github.com/jeffreyhorn/nlp2mcp/issues/764) (mexss accounting variables). The root cause and required fix are identical.

### Why This Cannot Be Fixed Now

The accounting variable elimination was explicitly deferred in Sprint 20 after thorough analysis (see `docs/planning/EPIC_4/SPRINT_20/ACCOUNTING_VAR_DETECTION_DESIGN.md`). The design identified 5 detection criteria (C1-C5):

- **C1-C4** (static analysis): Computable but produce **false positives** — incorrectly classifying variables in models like `demo1`, `himmel11`, `house` as accounting variables
- **C5** (multiplier consistency): Requires runtime dependency graph analysis — not feasible from static analysis alone

The `sameas` guard bug in `src/kkt/stationarity.py:2446-2473` (using only the first Jacobian entry for scalar equations that sum over multiple variable instances) is a contributing factor but not sufficient to fix the full accounting variable pattern.

### What Must Be Done Before Fixing

1. Implement C5 multiplier-consistency checking with a constraint dependency graph
2. Fix the `sameas` guard to handle multi-entry Jacobian patterns for scalar equations
3. Validate against known false-positive models (demo1, himmel11, house)

## Model Structure

- **Sets**: `p` (plants), `d` (distribution centers), `m` (months), `c` (commodities)
- **Objective**: Maximize `profit`
- **Accounting equations**:
  - `ar.. revenue =E= sum(...)`
  - `at.. transport =E= sum(...)`
  - `ap.. production =E= sum(...)`
  - `ah.. holding =E= sum(...)`
  - `apr.. profit =E= revenue - transport - production - holding + 10`

## Trivial Stationarity Equations

```gams
stat_holding..    1 + nu_ah =E= 0;
stat_production.. 1 + nu_ap =E= 0;
stat_transport..  1 + nu_at =E= 0;
stat_revenue..   -1 + nu_ar =E= 0;
```

## Files

- `data/gamslib/raw/pdi.gms` — original LP model
- `data/gamslib/mcp/pdi_mcp.gms` — generated MCP
- `docs/issues/ISSUE_764_mexss-mcp-locally-infeasible-accounting-variables.md` — parent issue
