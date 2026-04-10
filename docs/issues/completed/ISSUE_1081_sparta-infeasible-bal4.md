# sparta: MCP Locally Infeasible for bal4 Formulation (KKT Bug)

**GitHub Issue:** [#1081](https://github.com/jeffreyhorn/nlp2mcp/issues/1081)
**Status:** FIXED
**Severity:** Medium — was locally infeasible (now resolved)
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

Before fix (historical):
```bash
python -m src.cli data/gamslib/raw/sparta.gms -o /tmp/sparta_mcp.gms
gams /tmp/sparta_mcp.gms lo=2
# **** MODEL STATUS      5 Locally Infeasible
```

After fix (Sprint 24):
```bash
# **** MODEL STATUS      1 Optimal
# nlp2mcp_obj_val = 3466.380 (matches NLP)
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

Resolved by accumulated Sprint 24 fixes; no single isolated root cause
was identified. The infeasibility was likely caused by one or more of:
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

## FIXED (Sprint 24)

Resolved by accumulated Sprint 24 fixes (multiplier dimension fix PR #1246,
empty equation detector PR #1240, ord() handler improvements, stationarity
condition fixes).

**Result:** sparta compiles and solves to MODEL STATUS 1 Optimal.
MCP obj=3466.380, NLP obj=3466.38 — **exact match**.

No code changes needed — the infeasibility was caused by bugs in the KKT
system that were fixed by other Sprint 24 issues.

## Files

| File | Relevance |
|------|-----------|
| `data/gamslib/raw/sparta.gms` | Original model with 4 formulations |
