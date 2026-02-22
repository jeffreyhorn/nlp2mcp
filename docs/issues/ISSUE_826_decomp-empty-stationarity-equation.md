# Decomp MCP: GAMS Error — Empty Stationarity Equation for `lam` Variable

**GitHub Issue:** [#826](https://github.com/jeffreyhorn/nlp2mcp/issues/826)
**Status:** OPEN — Cannot fix; deep stationarity builder issue (domain/subset mapping limitation)
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

---

## Investigation Findings (2026-02-22)

### Deep Root Cause: Domain/Subset Index Mismatch in Stationarity Construction

The decomp model declares `Variable lam(ss)` over the full set `ss = /1*10/`, but the
equations `cbal`, `tbal`, `convex` are **scalar** and access `lam` only over the dynamic
subset `s(ss)` via `sum(s, ...)`. This creates a fundamental mismatch in the stationarity
builder.

**Detailed trace through the code:**

1. **No gradient term**: `lam` does not appear directly in the objective function, so
   `_build_indexed_gradient_term()` returns `Const(0.0)`.

2. **Jacobian terms fail to propagate**: The equations `cbal`, `tbal`, `convex` are scalar
   (no domain in their declaration). When `_add_indexed_jacobian_terms()` (lines 1382-1567)
   processes these equations:
   - `eq_indices` is empty (scalar constraint)
   - The code processes scalar constraints in the `else` branch
   - The derivative expression contains concrete element indices ("1", "2") from set `s`
   - The `element_to_set` mapping maps `"1" → "ss"` (from variable instances)
   - But parameters like `mcost(s)` are declared over `s`, not `ss`
   - `_replace_indices_in_expr()` cannot correctly map concrete indices back to
     symbolic set names when the parameter domain differs from the variable domain

3. **Result**: After simplification, the stationarity expression becomes `Const(0.0)`,
   producing empty equations `stat_lam(1).. 0 =E= 0` and `stat_lam(2).. 0 =E= 0`.

4. **No empty-equation filtering**: `src/emit/model.py` (function `emit_model_mcp`, lines
   128-151) does not check whether stationarity equations are empty before including them in
   MCP pairing. GAMS requires that MCP-paired empty equations correspond to fixed variables.

### Why This Cannot Be Simply Fixed

This is a structural limitation in how the stationarity builder handles the relationship
between variable domains and constraint access patterns:

- The code assumes a 1-to-1 mapping between variable domain indices and constraint domain
  indices, but decomp uses a **subset access pattern** (`sum(s, ... lam(s))` where `s ⊂ ss`)
- Fixing this requires either:
  1. **Per-instance stationarity equations**: Build separate scalar stationarity equations
     for each concrete element, avoiding the need for index replacement
  2. **Subset-aware index replacement**: Teach `_replace_indices_in_expr()` to recognize
     that element "1" in `mcost("1")` should map to subset `s`, not the parent set `ss`
  3. **Empty equation post-processing**: After building stationarity equations, detect empty
     ones and either fix the variable or exclude the pair from the MCP model

### Prerequisites Before Attempting Fix

1. **Empty equation post-processing (quickest mitigation, option 3 above)**: Add a
   post-build validation pass in `build_stationarity_equations()` that detects empty
   stationarity expressions and either fixes the associated variable (`.fx = 0`) or
   excludes the equation/variable pair from the MCP model statement in `emit_model.py`.

2. **Per-instance or subset-aware stationarity (proper fix, options 1 or 2 above)**:
   Requires refactoring the indexed stationarity builder to handle subset access patterns.
   This is a significant change affecting `_add_indexed_jacobian_terms()`,
   `_replace_indices_in_expr()`, and potentially `_build_element_to_set_mapping()`. Should
   be planned as a dedicated sprint task.

### Key Code Locations

| Function | File:Line | Issue |
|----------|-----------|-------|
| `_build_indexed_stationarity_expr()` | `stationarity.py:702-768` | Gradient + Jacobian assembly |
| `_add_indexed_jacobian_terms()` | `stationarity.py:1382-1567` | Scalar constraint branch fails for subset access |
| `_replace_indices_in_expr()` | `stationarity.py:923-1093` | Cannot map indices across different domain sets |
| MCP pairing | `emit/model.py:128-151` | No filtering of empty stationarity equations |
