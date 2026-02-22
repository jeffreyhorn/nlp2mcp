# Decomp MCP: GAMS Error — Empty Stationarity Equation for `lam` Variable

**GitHub Issue:** [#826](https://github.com/jeffreyhorn/nlp2mcp/issues/826)
**Status:** OPEN
**Severity:** High — MCP generates but GAMS reports compile error (EXECERROR = 2)
**Date:** 2026-02-22
**Affected Models:** decomp

---

## Problem Summary

The decomp model (`data/gamslib/raw/decomp.gms`) generates an MCP file, but GAMS reports:

```
**** MCP pair stat_lam.lam has empty equation but associated variable is NOT fixed
     lam(1)
**** MCP pair stat_lam.lam has empty equation but associated variable is NOT fixed
     lam(2)
**** SOLVE from line 179 ABORTED, EXECERROR = 2
```

The stationarity equation `stat_lam` for the multiplier variable `lam(i)` is completely empty
(no terms), but the variable `lam` is not fixed. GAMS requires that if an MCP-paired equation
is empty, the associated variable must be fixed.

Previously this model failed with `codegen_numerical_error` due to `+Inf` parameter value
in the `rep` table. The Inf handling fix (Sprint 20 Day 10) resolved that blocker, revealing
this deeper issue.

---

## Reproduction

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/decomp.gms -o /tmp/decomp_mcp.gms

# Run GAMS
gams /tmp/decomp_mcp.gms lo=2

# Expected output:
# **** MCP pair stat_lam.lam has empty equation but associated variable is NOT fixed
# **** SOLVE from line 179 ABORTED, EXECERROR = 2
```

---

## Root Cause

The decomp model uses Benders decomposition with a variable `lam(i)` that represents the
multiplier for the convexity constraint. In the KKT transformation:

1. `lam(i)` is a primal variable that gets a stationarity equation `stat_lam(i)`
2. The stationarity equation should contain the gradient of the Lagrangian w.r.t. `lam(i)`
3. If `lam` does not appear in any constraint (or all its derivative terms simplify to zero),
   the stationarity equation becomes empty (`stat_lam.. NONE`)
4. GAMS requires that empty MCP-paired equations correspond to fixed variables

The generated MCP file shows:

```gams
---- stat_lam  =E=

                NONE
```

This means either:
- The variable `lam` is not referenced in any equation (unlikely if it's in the model)
- All Jacobian terms for `lam` simplified to zero during stationarity equation construction
- The variable was detected as unreferenced but not excluded from the MCP model

---

## Suggested Fix

**Option A: Detect and fix empty stationarity equations**

After building stationarity equations, check for any that are empty (zero expression).
For such variables, either:
- Fix the variable to zero (`.fx = 0`) and exclude from the MCP pairing
- Exclude the variable/equation pair from the MCP model entirely

**Option B: Improve unreferenced variable detection**

The `referenced_variables` set in `KKTSystem` should catch variables that don't appear in
any equation. If `lam` is not referenced, it should be excluded by the emitter.

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/kkt/stationarity.py` | `build_stationarity_equations()` — why `stat_lam` is empty |
| `src/emit/emit_gams.py` | Unreferenced variable filtering |
| `src/emit/model.py` | MCP model statement construction |
| `data/gamslib/raw/decomp.gms` | Original model structure |
