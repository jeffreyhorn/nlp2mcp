# sparta: MCP Locally Infeasible for bal4 Formulation (KKT Bug)

**GitHub Issue:** [#1081](https://github.com/jeffreyhorn/nlp2mcp/issues/1081)
**Status:** OPEN
**Severity:** Medium — MCP generates but PATH reports locally infeasible
**Date:** 2026-03-14
**Affected Models:** sparta

---

## Problem Summary

The sparta model generates an MCP that is MODEL STATUS 5 (Locally Infeasible) for the bal4
formulation. The regenerated MCP (after Day 7-8 fixes) still shows infeasibility, indicating
a KKT derivation bug specific to the bal4 constraint structure.

Note: sparta is also a multi-solve model (#1080), so even if fixed, the NLP reference
comparison may not be valid.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/sparta.gms -o /tmp/sparta_mcp.gms
gams /tmp/sparta_mcp.gms lo=2
# **** SOLVER STATUS     1 Normal Completion
# **** MODEL STATUS      5 Locally Infeasible
```

---

## Context

sparta is a military manpower planning model (Wagner) with 4 LP formulations solved
sequentially:

```gams
solve sparta1 using lp minimizing z;  // bal1 equations
solve sparta2 using lp minimizing z;  // bal2 equations
solve sparta3 using lp minimizing z;  // bal3 equations
solve sparta4 using lp minimizing z;  // bal4 equations
```

The nlp2mcp pipeline captures the last formulation (sparta4, using equations bal4). All
four formulations share the same variables and objective but use different constraint
structures (bal1 through bal4 — stock vs. flow formulations).

---

## Root Cause

Not yet determined. The infeasibility suggests one of:
1. Incorrect KKT conditions for the bal4 constraint structure
2. Missing or incorrect domain conditioning on stationarity equations
3. Lead/lag reference handling specific to the bal4 formulation

---

## Suggested Fix

1. Examine the bal4 equation structure in `data/gamslib/raw/sparta.gms`
2. Compare generated MCP stationarity equations to hand-derived KKT
3. Inspect the listing file (`/tmp/sparta_mcp.lst`) for infeasibility diagnostics
4. Identify which stationarity or complementarity equation is unsatisfiable

---

## Analysis

From Sprint 22 Day 9 Category A divergence investigation. Full analysis in
`docs/planning/EPIC_4/SPRINT_22/CATEGORY_A_DIVERGENCE_ANALYSIS.md`.

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `data/gamslib/raw/sparta.gms` | Original model with 4 formulations |
| `data/gamslib/mcp/sparta_mcp.gms` | Generated MCP (stale — regenerate) |
| `src/kkt/stationarity.py` | KKT equation generation |
| `src/emit/equations.py` | Equation emission with domain conditions |
