# IBM1 MCP: Locally Infeasible — Stationarity Equations Have Nonzero Constants

**GitHub Issue:** [#828](https://github.com/jeffreyhorn/nlp2mcp/issues/828)
**Status:** OPEN — Cannot fix; requires investigation of bound multiplier inclusion in stationarity
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

---

## Investigation Findings (2026-02-22)

### Bound Multiplier Infrastructure Analysis

The KKT bound multiplier system was investigated in detail. The infrastructure correctly
handles several scenarios:

**What works correctly:**
- **Positive Variables**: `lo = 0.0` → creates uniform `piL_x` with variable's domain
- **Infinite bound filtering**: `+Inf`/`-Inf` bounds are skipped at partition time
  (`partition.py`, lines 120-157), preventing meaningless multiplier generation
- **Uniform bounds**: Single indexed multiplier `piL_x(i)` added to `stat_x(i)` via
  `Binary("-", expr, MultiplierRef(piL_name, domain))` (stationarity.py lines 757-767)
- **Non-uniform bounds**: Per-instance scalar multipliers `piL_x_i1` added to per-instance
  stationarity equations (stationarity.py lines 559-579, 1577-1623)

**How bounds from parameter assignments are handled:**
- `x.up(s) = sup(s,"inventory")` → parsed into `var_def.up_map` with per-instance values
- `_process_indexed_bounds()` (partition.py lines 165-235) consolidates:
  - If all values identical and no scalar bound → uniform bound with `()` key
  - Otherwise → non-uniform bounds with per-instance keys `(var_name, (idx,))`
- Infinite values in `up_map` are tracked in `skipped_infinite` and excluded from bound multiplier creation

### The ibm1 Specific Problem

In ibm1, `x(s)` is declared as `Positive Variable` (lo=0) with upper bounds set via:
```gams
x.up(s) = sup(s,"inventory");
```

The `sup` table contains `+Inf` for some materials (aluminum, etc.) and finite values for
others (bin-1 through bin-5). This creates a **non-uniform bounds** scenario:

1. **Lower bound**: Uniform `lo = 0.0` → should create `piL_x(s)` multiplier
2. **Upper bound**: Non-uniform — mix of `+Inf` (skipped) and finite values → should create
   per-instance `piU_x_bin1`, `piU_x_bin2`, etc. for the finite bounds only

### Likely Failure Point

The stationarity equations show cost constants (`-0.03`, `-0.08`, `-0.17`) on the RHS but
**no bound multiplier terms** to balance them. This suggests one of:

1. **Bound multipliers not created**: The partition/complementarity code may not be
   generating `piL_x` or `piU_x` multipliers at all. This could happen if:
   - It's possible that the parameter-assigned bounds (`x.up(s) = sup(s,"inventory")`) are
     not being resolved to numeric values at IR time (stored as expressions rather than
     evaluated)
   - The `up_map` entries are expression objects rather than floats, causing
     `_process_indexed_bounds()` to skip them

2. **Bound multipliers created but not included in stationarity**: The stationarity builder
   may be looking for uniform bounds (key `(var_name, ())`) but finding non-uniform ones
   (keyed per-instance), or vice versa. The `_has_nonuniform_bounds()` detection
   (stationarity.py lines 451-484) must agree with how multipliers were created.

3. **Interaction with indexed stationarity construction**: If `x(s)` has non-uniform upper
   bounds, it should get per-instance stationarity equations (`stat_x_bin1`, etc.), but if
   the lower bound is uniform, there may be a conflict in whether to use indexed or
   per-instance stationarity construction.

### What Must Be Done Before Attempting Fix

1. **Reproduce and inspect the generated MCP file**: Run the pipeline on ibm1 and examine
   the generated GAMS file to verify:
   - Whether `piL_x` and/or `piU_x` variables are declared
   - Whether complementarity equations `comp_lo_x` and `comp_up_x` exist
   - Whether `stat_x` contains bound multiplier terms

2. **Debug bound resolution**: Check if `x.up(s) = sup(s,"inventory")` results in numeric
   values in `var_def.up_map` or if they remain as unresolved expressions. The partition
   code expects numeric values for bound classification.

3. **Test uniform vs non-uniform detection**: Verify that `_has_nonuniform_bounds()` returns
   the correct value for `x` given its mixed bound scenario (uniform lo=0, non-uniform up
   with some infinite entries skipped).

4. **Consider the mixed-bounds case**: When lo is uniform but up is non-uniform (or absent
   for some indices), the stationarity builder must handle both types correctly in the same
   equation. This edge case may not be fully supported.

### Key Code Locations

| Function | File:Line | Issue |
|----------|-----------|-------|
| `_process_indexed_bounds()` | `partition.py:165-235` | How parameter-assigned bounds are consolidated |
| `_create_bound_lo_multipliers()` | `assemble.py:280-357` | Multiplier creation for lower bounds |
| `_create_bound_up_multipliers()` | `assemble.py:358-436` | Multiplier creation for upper bounds |
| `_has_nonuniform_bounds()` | `stationarity.py:451-484` | Uniform vs non-uniform detection |
| `_build_indexed_stationarity_expr()` | `stationarity.py:702-768` | Bound multiplier terms in stationarity |
| `_build_stationarity_expr()` | `stationarity.py:1577-1623` | Per-instance bound multiplier lookup |
