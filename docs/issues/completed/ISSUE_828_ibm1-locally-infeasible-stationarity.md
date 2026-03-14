# IBM1 MCP: Locally Infeasible — Stationarity Equations Have Nonzero Constants

**GitHub Issue:** [#828](https://github.com/jeffreyhorn/nlp2mcp/issues/828)
**Status:** RESOLVED — Root cause was table column misalignment (ISSUE_1074 / PR #1079)
**Severity:** High — MCP generates and compiles, but PATH solver reports locally infeasible
**Date:** 2026-02-22
**Resolved:** 2026-03-14
**Affected Models:** ibm1

---

## Problem Summary

The ibm1 model (`data/gamslib/raw/ibm1.gms`) generates an MCP file that compiles in GAMS,
but PATH reports locally infeasible (MODEL STATUS 5):

```
**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      5 Locally Infeasible
```

The stationarity equations for the `x(s)` variables (material usage) have nonzero constant
terms that make the system unsatisfiable:

```gams
stat_x(bin-1)..  nu_yield - 0.7*nu_ebal(aluminum) - 0.02*nu_ebal(silicon)
  - 0.15*nu_ebal(iron) - 0.03*nu_ebal(copper) - 0.02*nu_ebal(manganese)
  - 0.02*nu_ebal(magnesium) =E= -0.03 ;   (LHS = 0, INFES = 0.03)

stat_x(bin-2)..  [similar] =E= -0.08 ;   (LHS = 0, INFES = 0.08)
stat_x(bin-3)..  [similar] =E= -0.17 ;   (LHS = 0, INFES = 0.17)
```

Previously this model failed with `codegen_numerical_error` due to `+Inf` parameter values.
The Inf handling fix (Sprint 20 Day 10) resolved that blocker, revealing this infeasibility.

---

## Resolution

**Root Cause:** Table column misalignment in the `sup` parameter table (ISSUE_1074).

The ibm1 model uses a GAMS table `sup(s,*)` with columns `inventory`, `min-use`, and `cost`.
The table parser's range-based column matching used the next column's start position as the
range boundary, which caused values in sparse rows (where some columns are blank) to be
assigned to the wrong column. Specifically, `cost` values were being mapped to `min-use` and
vice versa, corrupting the parameter data fed into the KKT system.

The fix (PR #1079) replaced range-based column matching with **gap-midpoint matching**: column
boundaries are defined at the midpoint of the whitespace gap between adjacent header text
spans (`(prev_right_edge + this_start) / 2`). This correctly handles sparse rows where some
columns are blank.

**After the fix:**
- ibm1 generates a correct MCP file
- PATH solver reports MODEL STATUS 1 (Optimal)
- Objective value: 287.105 (matches NLP reference 287.1357 within solver tolerance)
- Stationarity equations have correct cost constants balanced by bound multiplier terms

**Fix PR:** [#1079](https://github.com/jeffreyhorn/nlp2mcp/pull/1079)
**Related Issue:** [#1074](https://github.com/jeffreyhorn/nlp2mcp/issues/1074) (table column misalignment)

---

## Original Investigation Findings (2026-02-22)

The original investigation focused on bound multiplier infrastructure, which turned out to be
working correctly. The actual problem was upstream: corrupted parameter values from table
column misalignment meant the wrong numeric constants appeared in stationarity equations.

### Key Lesson

When stationarity equations show unexpected constants, verify that the upstream parameter
values (from table parsing) are correct before investigating the KKT infrastructure itself.
