# Stationarity Equations Contain Zero Gradients for Indexed Variables

**GitHub Issue:** #504
**URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/504

## Summary

The MCP emitter generates stationarity equations with `sum(h, 0)` expressions instead of actual partial derivatives when processing indexed variables. This results in incorrect KKT conditions.

## Observed Behavior

In generated MCP files like `sample_mcp.gms`, the stationarity equations contain expressions that evaluate to zero:

```gams
stat_n(h).. sum(h, 0) + (-sum(h, 0)) * nu_cbalr + sum(j, sum(h, 0) * lam_vbal(j)) + sum(j, sum(h, 0) * lam_vbalr(j)) - piL_n(h) =E= 0;
stat_nr(h).. sum(h, 0) + (-sum(h, 0)) * nu_cbalr + sum(j, sum(h, 0) * lam_vbal(j)) + sum(j, sum(h, 0) * lam_vbalr(j)) =E= 0;
```

The `sum(h, 0)` terms all evaluate to 0, which means the gradient contributions are missing.

## Expected Behavior

The stationarity equations should contain the actual partial derivatives of the Lagrangian with respect to the primal variables. For example:

```gams
stat_n(h)..  data(h,"cost")
              + data(h,"cost") * nu_cbalr
              + sum(j, k1(h,j) / sqr(n(h)) * lam_vbal(j))
              - piL_n(h) =E= 0;
stat_nr(h)..  data(h,"cost") / sqr(nr(h)) * nu_cbalr
              - sum(j, k1(h,j) * lam_vbalr(j)) =E= 0;
```

## Root Cause Analysis

The issue likely originates in the gradient/Jacobian computation phase when:
1. Computing partial derivatives of constraint expressions with respect to indexed variables
2. The derivative computation may not be correctly handling the index relationship between the constraint domain and the variable domain

## Files Likely Involved

- `src/ad/` - Automatic differentiation for gradient computation
- `src/kkt/assemble.py` - KKT system assembly
- `src/emit/equations.py` - Equation definition emission

## Reproduction Steps

1. Parse `data/gamslib/raw/sample.gms`
2. Translate to MCP format: `python -m src.cli data/gamslib/raw/sample.gms -o output.gms`
3. Inspect the `stat_n` and `stat_nr` equations in the output

## Impact

- Generated MCP files have incorrect KKT conditions
- Solving the MCP will not produce correct solutions
- Affects models with indexed variables that have constraints involving those variables

## Labels

- bug
- kkt-system
- gradient-computation
