# Emit: Missing stat_r.r Pairing in MCP Model Declaration (cpack.gms)

**Status:** Open  
**Priority:** High  
**Affects:** cpack.gms (circle packing from GAMSLIB)  
**GitHub Issue:** [#623](https://github.com/jeffreyhorn/nlp2mcp/issues/623)

---

## Summary

The MCP model declaration for cpack.gms omits the pairing for the primal variable `r`: the stationarity equation `stat_r` is defined, but there is no `stat_r.r` entry in `Model mcp_model / ... /;`. This leaves variable `r` unpaired and equation `stat_r` unused, making the MCP formulation incomplete/incorrect.

## Symptoms

- **Model:** cpack.gms
- **Parse:** SUCCESS
- **Translate:** SUCCESS (generates MCP file)
- **Solve:** FAILS (MCP formulation incomplete - variable `r` not paired)

## Root Cause

The MCP model pairing generator is not including all stationarity equations in the model declaration. Specifically, when collecting equation-variable pairs for the model statement, `stat_r.r` is being omitted.

**Problem Code in Generated MCP:**
```gams
Equations
    stat_r       * Stationarity for r - DEFINED
    stat_x(i)
    stat_y(i)
    ...
;

stat_r..  [equation body] =E= 0;   * Equation IS generated

Model mcp_model /
    stat_x.x,
    stat_y.y,
    ...
    * MISSING: stat_r.r   <-- BUG: pairing not included
/;
```

**Correct Code Should Be:**
```gams
Model mcp_model /
    stat_r.r,    * Add this pairing
    stat_x.x,
    stat_y.y,
    ...
/;
```

## Analysis

The cpack.gms model is a circle packing optimization problem where:
- `r` is a scalar primal variable (the radius to maximize)
- `x(i)` and `y(i)` are indexed position variables
- The stationarity equation `stat_r` is correctly generated for `r`
- However, the `stat_r.r` pairing is missing from the MCP model declaration

This indicates a bug in the model declaration emission logic where scalar (non-indexed) variable pairings may be handled differently than indexed pairings.

## Proposed Solution

In the MCP model declaration emission:
1. Ensure all primal variables (both indexed and scalar) have their stationarity equation pairings included
2. Check for consistent handling of scalar vs. indexed variables in the pairing generator
3. Verify the equation-variable pairing collection includes all defined stationarity equations

**Likely Code Locations:**
- `src/emit/emit_gams.py` - MCP model declaration emission
- `src/kkt/kkt_system.py` - KKT system assembly and pairing collection
- `src/kkt/stationarity.py` - Stationarity equation generation

## Reproduction Steps

```bash
# 1. Parse and translate cpack.gms (from repo root)
python -m src.cli data/gamslib/raw/cpack.gms -o /tmp/cpack_mcp.gms

# 2. Examine the generated MCP file
grep -A 20 "Model mcp_model" /tmp/cpack_mcp.gms

# 3. Verify stat_r.r is missing from the model statement
# The equation stat_r will be defined but not paired in the model
```

## Impact

- MCP formulation is mathematically incomplete
- cpack.gms cannot be solved as an MCP because variable `r` has no complementarity pairing
- May affect other models with scalar primal variables

## Testing

1. Unit test: Verify scalar variable pairings are included in model declaration
2. Integration test: cpack.gms compiles and solves successfully after fix
3. Regression test: Models with indexed variables still work correctly

## Related Issues

- GitHub #621 - Alias ordering in cpack.gms
- GitHub #624 - Same issue pattern in circle.gms

## References

- `data/gamslib/mcp/cpack_mcp.gms` - Generated MCP file showing the bug
- `data/gamslib/raw/cpack.gms` - Original GAMS model
- `src/emit/emit_gams.py` - Model declaration emission code
- PR #619 review comment identifying this issue

---

**Created:** 2026-02-03  
**Sprint:** Sprint 17
