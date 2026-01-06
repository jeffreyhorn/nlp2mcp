# MCP Model Declaration Incorrectly Maps Multiple Equations to Same Indexed Variable

**GitHub Issue:** #505
**URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/505

## Summary

The MCP model declaration in generated files incorrectly maps multiple element-specific bound complementarity equations to the same indexed variable without element specification. This produces invalid GAMS MCP syntax.

## Observed Behavior

In `sample_mcp.gms`, the MCP model declaration contains:

```gams
Model mcp_model /
    ...
    comp_lo_n_1.piL_n,
    comp_lo_n_2.piL_n,
    comp_lo_n_3.piL_n,
    comp_lo_n_4.piL_n
/;
```

Similarly in `chem_mcp.gms`:

```gams
Model mcp_model /
    ...
    comp_lo_x_H.piL_x,
    comp_lo_x_H2.piL_x,
    comp_lo_x_H2O.piL_x,
    ...
/;
```

Each bound equation maps to `piL_n` or `piL_x` without specifying which element of the indexed variable it corresponds to.

## Expected Behavior

Each equation should map to a specific element of the indexed variable:

```gams
Model mcp_model /
    ...
    comp_lo_n_1.piL_n("1"),
    comp_lo_n_2.piL_n("2"),
    comp_lo_n_3.piL_n("3"),
    comp_lo_n_4.piL_n("4")
/;
```

Or, if using parameterized equations (see related issue), the mapping should be:

```gams
Model mcp_model /
    ...
    comp_lo_n.piL_n
/;
```

## Root Cause Analysis

The MCP model declaration emission in `src/emit/mcp_model.py` or similar does not include the element index when pairing bound complementarity equations with their multiplier variables. The code likely:

1. Generates element-specific equation names (e.g., `comp_lo_n_1`)
2. But uses only the base multiplier name without the element qualifier

## Files Likely Involved

- `src/emit/mcp_model.py` or equivalent - MCP model declaration emission
- `src/kkt/assemble.py` - Where complementarity pairs are assembled
- `src/kkt/kkt_system.py` - ComplementarityPair data structure

## Reproduction Steps

1. Parse `data/gamslib/raw/sample.gms` or `data/gamslib/raw/chem.gms`
2. Translate to MCP format
3. Inspect the `Model mcp_model / ... /;` section

## Impact

- Generated MCP files have invalid GAMS syntax
- GAMS will reject the model with duplicate equation.variable mappings
- Affects all models with indexed variables that have element-specific bounds

## Related Issues

- Bound complementarity equations parameterization issue (equations are element-specific instead of parameterized)

## Labels

- bug
- mcp-emission
- indexed-variables
