# IBM1 MCP: Locally Infeasible — Stationarity Equations Have Nonzero Constants

**GitHub Issue:** [#828](https://github.com/jeffreyhorn/nlp2mcp/issues/828)
**Status:** OPEN
**Severity:** High — MCP generates and compiles, but PATH solver reports locally infeasible
**Date:** 2026-02-22
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

The `-0.03`, `-0.08`, `-0.17` constants on the RHS correspond to the material costs from
the objective function. These should be offset by bound multiplier terms, but the bound
multipliers appear to be missing or incorrectly handled.

Previously this model failed with `codegen_numerical_error` due to `+Inf` parameter values.
The Inf handling fix (Sprint 20 Day 10) resolved that blocker, revealing this infeasibility.

---

## Reproduction

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/ibm1.gms -o /tmp/ibm1_mcp.gms

# Run GAMS
gams /tmp/ibm1_mcp.gms lo=2

# Expected output:
# **** SOLVER STATUS     1 Normal Completion
# **** MODEL STATUS      5 Locally Infeasible
```

---

## Root Cause

The ibm1 model is a blending LP where:
- `x(s)` = amount of each scrap material used (Positive Variable, bounded above by supply)
- The objective minimizes total cost: `min sum(s, cost(s) * x(s))`
- Constraints: element balance (`ebal`), yield (`yield`), bounds from supply inventory

The stationarity equations `stat_x(s)` should be:

```
∂L/∂x(s) = cost(s) + ν_yield + Σ_e comp(e,s) * ν_ebal(e) - π_lo(s) + π_up(s) = 0
```

The constants `-0.03`, `-0.08`, `-0.17` are the `cost(s)` values from the objective gradient.
These should be balanced by bound multipliers `π_lo` and `π_up`, but these multipliers
appear to be missing from the stationarity equations.

**Possible causes:**
1. Upper bound multipliers (`π_up`) for the supply constraints are not being generated
   because the `+Inf` inventory values (e.g., `aluminum.inventory = inf`) mean those bounds
   are correctly skipped — but the finite bounds for `bin-1` through `bin-5` should still
   generate bound multipliers
2. The bound multiplier generation logic may not correctly handle variable bounds that come
   from parameter assignments (`x.up(s) = sup(s,"inventory")`) rather than direct `.up` values
3. Lower bound multipliers (`π_lo`) for Positive Variables should exist but may not appear

---

## Suggested Fix

1. **Verify bound multiplier generation** for `x(s)`:
   - Check if `piL_x` and `piU_x` multipliers exist in the KKT system
   - Verify they appear in `stat_x` stationarity equations
   - If missing, trace why they were excluded (infinite bound detection, etc.)

2. **Check Positive Variable handling**:
   - `x(s)` is declared as `Positive Variable` with `.lo = 0`
   - The lower bound should generate a `piL_x(s)` multiplier
   - Verify this multiplier appears in the stationarity equation

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/kkt/stationarity.py` | How bound multiplier terms are added to stationarity |
| `src/kkt/complementarity.py` | How bound multipliers are generated |
| `src/kkt/partition.py` | How variable bounds are extracted and classified |
| `src/emit/emit_gams.py` | How bound multiplier declarations are emitted |
| `data/gamslib/raw/ibm1.gms` | Original model with blending structure |
