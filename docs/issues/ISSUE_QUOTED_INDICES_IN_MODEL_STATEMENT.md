# Issue: Quoted Indices in MCP Model Statement Pairings

**Status:** Open  
**Category:** Code Generation / MCP Model Statement  
**Affected Models:** chem, ps2_f_inf, and models with indexed bound multipliers  
**Priority:** High  
**GitHub Issue:** [#574](https://github.com/jeffreyhorn/nlp2mcp/issues/574)

## Summary

When generating MCP model statements, the code emitter produces bound multiplier pairings with quoted indices like `piL_x("H")`. GAMS does not accept quoted indices in model statement equation-variable pairings, causing compilation errors.

## Reproduction

### Example 1: chem model

**Generated code (lines 127-137 of chem_mcp.gms):**
```gams
Model mcp_model /
    stat_x.x,
    stat_xb.xb,
    cdef.nu_cdef,
    edef.energy,
    xdef.nu_xdef,
    comp_lo_x_H.piL_x("H"),
    comp_lo_x_H2.piL_x("H2"),
    comp_lo_x_H2O.piL_x("H2O"),
    ...
/;
```

**GAMS Errors:**
```
*** Error   2 in chem_mcp.gms
    Identifier expected
*** Error 924 in chem_mcp.gms
    Equation and variable list in model statement expect | as separator
```

### Example 2: ps2_f_inf model

**Generated code (line 111 of ps2_f_inf_mcp.gms):**
```gams
Model mcp_model /
    ...
    comp_lo_x_inf.piL_x("inf")
/;
```

**Same GAMS Errors:** Error 2, Error 924

## Root Cause Analysis

The MCP model statement generation creates element-specific complementarity pairings for bound constraints. When a variable like `x(c)` has lower bounds for each element (H, H2, H2O, etc.):

1. The code generates element-specific complementarity equations: `comp_lo_x_H`, `comp_lo_x_H2`, etc.
2. It pairs them with the bound multiplier using a quoted index: `piL_x("H")`

However, GAMS model statements don't support the syntax `variable("element")`. The variable reference in a model pairing must be either:
- A scalar variable: `equation.variable`
- An indexed variable without element specification: `equation.variable` (when both have matching domains)

## Expected Behavior

For indexed bound multipliers, the model statement should either:

### Option A: Use indexed complementarity equations with matching domains
```gams
Equations
    comp_lo_x(c)  "Lower bound complementarity for x"
;

comp_lo_x(c).. x(c) - lo(c) =G= 0;

Model mcp_model /
    ...
    comp_lo_x.piL_x
/;
```

### Option B: Use element-specific scalar multipliers
```gams
Variables
    piL_x_H, piL_x_H2, piL_x_H2O, ...
;

Model mcp_model /
    ...
    comp_lo_x_H.piL_x_H,
    comp_lo_x_H2.piL_x_H2,
    ...
/;
```

Option A is preferred as it's cleaner and scales better.

## Affected Models

| Model | Element Count | Bound Type |
|-------|--------------|------------|
| chem | 10 elements (H, H2, H2O, N, N2, NH, NO, O, O2, OH) | Lower bounds |
| ps2_f_inf | 1 element (inf) | Lower bounds |

Other models with indexed variables that have finite bounds may also be affected.

## Proposed Fix

**Location:** `src/emit/emit_gams.py` (model statement generation)

**Approach:**

1. When generating bound complementarity pairings, check if the multiplier is indexed
2. If indexed, generate a single indexed complementarity equation instead of element-specific equations
3. Pair the indexed equation with the indexed multiplier in the model statement

**Key changes:**
1. Modify `emit_complementarity_equations()` to generate indexed equations for indexed bound multipliers
2. Modify `emit_model_statement()` to use `equation.variable` syntax (without element indices)

## Test Cases

```python
def test_indexed_bound_multiplier_model_statement():
    """Model statement should not have quoted indices in variable references."""
    # Generate MCP for chem model
    # Check that model statement contains:
    #   comp_lo_x.piL_x  (indexed)
    # NOT:
    #   comp_lo_x_H.piL_x("H")
    pass

def test_model_statement_compiles():
    """Generated MCP model should compile without GAMS errors."""
    # Generate MCP for chem model
    # Run GAMS compilation
    # Assert no Error 2 or Error 924
    pass
```

## Related Files

- `src/emit/emit_gams.py`: Model statement and complementarity equation generation
- `src/kkt/complementarity.py`: Complementarity pair definition
- `src/emit/equations.py`: Equation emission

## Notes

This issue is distinct from:
- **ISSUE_KKT_INCORRECT_INDEX_REFERENCES.md** (completed): Wrong indices in equations themselves
- **ISSUE_DOUBLE_QUOTED_STRING_INDICES.md** (completed): Double-escaping of quotes in equation bodies
- **ISSUE_KKT_INDEX_REUSE_IN_SUM.md** (completed): Same index in equation domain and sum

The pattern here is specifically about the MCP model statement syntax, not the equation definitions.
