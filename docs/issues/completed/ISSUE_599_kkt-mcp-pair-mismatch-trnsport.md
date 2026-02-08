# KKT MCP Pair Mismatch: trnsport Model

**Status:** Open  
**Priority:** High  
**Component:** KKT System / MCP Generation  
**Model:** trnsport (GAMSLIB)  
**GitHub Issue:** #599

---

## Summary

The trnsport model fails to solve with GAMS Error "MCP pair has unmatched equation". The stationarity equations and constraint multipliers are not correctly paired in the MCP model declaration.

## Error Message

```
**** MCP pair comp_supply.lam_supply has unmatched equation
     comp_supply(seattle)

**** MCP pair comp_supply.lam_supply has unmatched equation
     comp_supply(san-diego)
```

## Root Cause Analysis

The MCP model pairs `comp_supply.lam_supply` but the dimensions don't match:
- `comp_supply(i)` is indexed over set `i` (seattle, san-diego)
- `lam_supply(i)` is indexed over set `i` (seattle, san-diego)

However, the variable `lam_supply` is not appearing in the `comp_supply` equation at all. Looking at the generated equation:

```gams
comp_supply(i).. ((-1) * sum(j, x(i,j))) =G= 0;
```

The issue is that the stationarity equation for `x(i,j)` is:

```gams
stat_x(i,j).. c(i,j) + sum(i__, 0 * lam_supply(i__)) + sum(j__, (-1) * lam_demand(j__)) =E= 0;
```

Notice that `lam_supply` has coefficient 0, meaning the constraint Jacobian entry is zero. This suggests the original constraint `supply(i).. sum(j, x(i,j)) =l= a(i);` is not correctly contributing to the stationarity conditions.

### Detailed Investigation

The original trnsport model has:
```gams
supply(i).. sum(j, x(i,j)) =l= a(i);  * Supply limit constraint
demand(j).. sum(i, x(i,j)) =g= b(j);  * Demand satisfaction constraint
```

For the stationarity equation ∂L/∂x(i,j) = 0:
- The coefficient of `lam_supply(i)` should be the partial derivative of `supply(i)` w.r.t. `x(i,j)` = 1 (only when i matches)
- The coefficient of `lam_demand(j)` should be the partial derivative of `demand(j)` w.r.t. `x(i,j)` = 1 (only when j matches)

The generated code shows:
- `sum(i__, 0 * lam_supply(i__))` - coefficient is 0 (WRONG - should be 1 for matching i)
- `sum(j__, (-1) * lam_demand(j__))` - coefficient is -1 for all j (WRONG - should be 1 for matching j only)

The bug is in how the Jacobian is computed for indexed constraints.

## Steps to Reproduce

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/trnsport.gms -o /tmp/trnsport_mcp.gms

# Run GAMS
gams /tmp/trnsport_mcp.gms lo=3
```

## Expected Behavior

The stationarity equation should be:
```gams
stat_x(i,j).. c(i,j) + lam_supply(i) - lam_demand(j) =E= 0;
```

Where:
- `lam_supply(i)` has coefficient +1 (for inequality ≤, multiplier is positive when constraint is active)
- `lam_demand(j)` has coefficient -1 (for inequality ≥, multiplier is negative in standard form)

## Actual Behavior

The stationarity equation incorrectly sums over ALL constraint indices instead of selecting the matching index:
```gams
stat_x(i,j).. c(i,j) + sum(i__, 0 * lam_supply(i__)) + sum(j__, (-1) * lam_demand(j__)) =E= 0;
```

## Files Involved

- `src/kkt/stationarity.py` - Stationarity equation generation
- `src/kkt/jacobian.py` - Jacobian computation for indexed constraints
- `src/ad/derivative_rules.py` - Automatic differentiation

## Suggested Fix

The Jacobian computation for indexed constraints needs to correctly identify which constraint index corresponds to which variable index. For `supply(i)` and `x(i,j)`:
- Only `supply(i)` (matching the first index of x) should contribute
- The coefficient should be ∂supply(i)/∂x(i,j) = 1 (since `supply(i) = sum(j, x(i,j))`)

The sum/differentiation logic needs to handle the index matching correctly.

## Related Issues

- This may be related to how indexed sums are differentiated
- The same pattern likely affects other models with indexed inequality constraints

---

## GitHub Issue

**Issue #:** 599  
**URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/599
