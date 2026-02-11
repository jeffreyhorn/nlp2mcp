# Mathopt1: Report Parameter Dimension Mismatch

**GitHub Issue:** [#675](https://github.com/jeffreyhorn/nlp2mcp/issues/675)

**Issue:** The mathopt1 model declares a parameter without explicit domain, but uses it with 2 indices. The parser interprets it as a scalar, causing Error 148/116.

**Status:** FIXED  
**Severity:** Medium - Model fails to compile  
**Affected Models:** mathopt1  
**Date:** 2026-02-10  
**Fixed:** 2026-02-11

---

## Problem Summary

GAMS allows declaring parameters without explicit domains and using them with any indices:
```gams
Parameter report 'solution summary report';
report('x1','global') = 1;
```

The current parser interprets `Parameter report;` as a scalar, but the assignments use it as 2-dimensional.

GAMS Errors:
- Error 116: Label is unknown
- Error 148: Dimension different - The symbol is referenced with more/less indices as declared

---

## Solution

**Implemented Option 2: Skip Report Parameters**

Report parameters (post-solve) typically reference `.l` values (solution levels) and aren't needed for MCP translation. The fix skips emitting these parameters entirely.

### Changes Made

In `src/emit/original_symbols.py`:

1. **`emit_original_parameters()`**: Added check to skip parameters with empty domain but indexed values or expressions. These are "dynamically typed" report parameters that GAMS allows but can't be properly emitted to MCP.

2. **`emit_computed_parameter_assignments()`**: Updated skip logic to handle parameters with empty domain but indexed expressions, even if they have some indexed values.

### Why This Works

The `report` parameter in mathopt1.gms:
- Is declared without domain: `Parameter report;`
- Has indexed values: `report('x1','global') = 1`
- Has indexed expressions: `report('x1','diff') = report('x1','global') - report('x1','solver')`
- References solution values: `report('x1','solver') = x1.l`

Since:
1. The `.l` assignments can't be captured (they're post-solve)
2. The expressions reference those uncaptured values
3. The parameter can't be properly declared without a domain

The safest approach is to skip emitting such parameters entirely. They're not needed for the MCP optimization problem - they're only for post-solve reporting.

---

## Verification

```bash
# Translate the model
nlp2mcp data/gamslib/raw/mathopt1.gms -o data/gamslib/mcp/mathopt1_mcp.gms

# Run GAMS - now compiles and solves successfully
cd data/gamslib/mcp && gams mathopt1_mcp.gms lo=2

# Model status: Optimal
```

---

## Original Analysis

### GAMS Dynamic Parameter Behavior

GAMS allows parameters without explicit domains. The dimension is inferred from usage:
- `Parameter p;` → scalar if used as `p = 5;`
- `Parameter p;` → indexed if used as `p(i,j) = 5;`

### Why Full Domain Inference Wasn't Chosen

Option 1 (inferring domain from assignments) would require:
1. Tracking all indexed assignments
2. Creating anonymous sets for the inferred indices
3. Handling the case where some assignments reference `.l` values

This is complex and the benefit is limited since report parameters aren't needed for MCP.

---

## References

- GAMS Parameter Syntax Documentation
- Sprint 18 Day 6 fix
