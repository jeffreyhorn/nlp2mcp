# Bound Complementarity Equations Are Element-Specific Instead of Parameterized

**GitHub Issue:** #506
**URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/506

## Summary

Bound complementarity equations for indexed variables are generated with hardcoded element references instead of being parameterized over the index set. This creates multiple nearly-identical equations when a single parameterized equation would be correct.

## Observed Behavior

In `sample_mcp.gms`, the bound complementarity equations are:

```gams
comp_lo_n_1(h).. n("1") - 100 =G= 0;
comp_lo_n_2(h).. n("2") - 100 =G= 0;
comp_lo_n_3(h).. n("3") - 100 =G= 0;
comp_lo_n_4(h).. n("4") - 100 =G= 0;
```

Similarly in `chem_mcp.gms`:

```gams
comp_lo_x_H(c).. x(H) - 0.001 =G= 0;
comp_lo_x_H2(c).. x("H2") - 0.001 =G= 0;
...
```

Each equation has a domain `(h)` or `(c)` but references a specific element (`n("1")`, `x("H2")`) rather than using the domain index.

## Expected Behavior

A single parameterized equation should cover all elements:

```gams
comp_lo_n(h).. n(h) - 100 =G= 0;
```

Or for chem:

```gams
comp_lo_x(c).. x(c) - 0.001 =G= 0;
```

This properly uses the index variable to create one equation instance per set element.

## Root Cause Analysis

The bound complementarity generation in `src/kkt/assemble.py` appears to:

1. Iterate over each element of an indexed variable's bounds
2. Create a separate equation for each element with a hardcoded element reference
3. Incorrectly include the full domain in the equation declaration

The correct approach would be to:
1. Recognize when a bound applies uniformly to all elements of an indexed variable
2. Generate a single parameterized equation using the index variable

## Files Likely Involved

- `src/kkt/assemble.py` - `_create_bound_lo_multipliers` and `_create_bound_up_multipliers` functions
- `src/kkt/naming.py` - Equation naming for bound complementarity
- `src/emit/equations.py` - Equation definition emission

## Reproduction Steps

1. Parse a model with indexed variables that have uniform bounds (e.g., `sample.gms`)
2. Translate to MCP format
3. Inspect the `comp_lo_*` equations in the output

## Impact

- Generated files are larger than necessary (N equations instead of 1)
- Combined with the MCP declaration issue, creates invalid GAMS syntax
- May cause confusion when reading generated code

## Related Issues

- MCP model declaration indexed variable mapping issue

## Design Considerations

If bounds are element-specific (different values for different elements), the current approach of separate equations may be correct, but the equation should NOT include the domain, and the MCP declaration needs to map to specific elements. Example:

```gams
* For element-specific bounds:
comp_lo_n_1.. n("1") - 100 =G= 0;
comp_lo_n_2.. n("2") - 200 =G= 0;  * Different bound value

Model mcp_model /
    comp_lo_n_1.piL_n("1"),
    comp_lo_n_2.piL_n("2")
/;
```

## Labels

- bug
- kkt-system
- bound-handling
- indexed-variables
