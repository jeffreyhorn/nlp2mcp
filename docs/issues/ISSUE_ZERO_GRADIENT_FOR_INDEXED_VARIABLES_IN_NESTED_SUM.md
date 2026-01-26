# Issue: Zero Gradient for Indexed Variables in Nested Sums

**Status:** Open  
**Category:** KKT Transformation / Gradient Computation  
**Affected Models:** apl1p, and models with indexed variables in nested sums  
**Priority:** High  
**GitHub Issue:** [#576](https://github.com/jeffreyhorn/nlp2mcp/issues/576)

## Summary

When an indexed variable appears inside nested sums in the objective function (e.g., `sum(g, sum(dl, f(g,dl)*y(g,dl)))`), the gradient computation incorrectly produces zero for all instances of that variable. This results in empty stationarity equations that cause GAMS execution errors.

## Reproduction

### Model: apl1p

**Original objective expression:**
```gams
Variables
   y(g,dl) 'operation level'

objdef.. profit =e= sum(g, sum(dl, f(g,dl)*y(g,dl))) - ... ;
```

**Generated stationarity equation (stat_y in apl1p_mcp.gms line 102):**
```gams
stat_y(g,dl).. sum(g__, 0) + sum(g__, sum(dl__, 0)) + sum(dl__, 0) + sum(g__, 0 * lam_cmin(g__)) + sum(g__, 0 * lam_cmax(g__)) + sum(g__, sum(dl__, 0) * lam_omax(g__)) + sum(dl__, ((-1) * sum(g__, 0)) * lam_demand(dl__)) =E= 0;
```

**GAMS Error:**
```
**** MCP pair stat_y.y has empty equation but associated variable is NOT fixed
**** SOLVE aborted, EXECERROR = 6
```

**Expected stationarity equation:**
```gams
stat_y(g,dl).. f(g,dl) + lam_omax(g) + (-1) * lam_demand(dl) =E= 0;
```

The gradient of the objective term `sum(g, sum(dl, f(g,dl)*y(g,dl)))` with respect to `y(g,dl)` should be `f(g,dl)`, not zero.

## Root Cause Analysis

The gradient computation for `sum(g, sum(dl, f(g,dl)*y(g,dl)))` with respect to `y(g,dl)`:

1. **Expected behavior:** 
   - ∂/∂y(g,dl) [sum(g', sum(dl', f(g',dl')*y(g',dl')))] = f(g,dl) when g'=g and dl'=dl, else 0
   - The result is simply `f(g,dl)` for the matching indices

2. **Actual behavior:**
   - The differentiation returns 0 for all components
   - This suggests the index matching between the sum indices and the variable indices is failing

The issue likely occurs in:
- `src/ad/differentiation.py`: When differentiating through nested Sum expressions
- The logic that determines if a VarRef inside a Sum matches the differentiation target

## Expected Behavior

When computing the gradient of a sum expression with respect to an indexed variable:
1. If the variable appears inside the sum, the derivative should be the coefficient (here `f(g,dl)`)
2. The sum structure should be collapsed when the indices match the variable's domain
3. Non-zero gradients should be correctly propagated through nested sums

## Affected Models

| Model | Variable | Sum Structure | Expected Gradient |
|-------|----------|---------------|-------------------|
| apl1p | y(g,dl) | sum(g, sum(dl, f*y)) | f(g,dl) |

Other models with multi-indexed variables inside nested sums may also be affected.

## Proposed Fix

**Location:** `src/ad/differentiation.py`

**Approach:**

1. Review the differentiation logic for Sum expressions
2. Ensure that when differentiating `sum(i, expr)` w.r.t. `x(i)`:
   - The derivative of `expr` is computed
   - If `expr` contains `x(i)` and we're differentiating for a specific instance, the sum collapses appropriately
3. For nested sums, the logic should recursively apply correctly

**Key investigation areas:**
1. How does `differentiate(Sum(...), wrt_var, wrt_indices)` handle the case when `wrt_indices` matches the sum indices?
2. Is the index matching working correctly for multi-dimensional cases?
3. Is there special handling needed when the sum indices exactly match the variable indices?

## Test Cases

```python
def test_gradient_nested_sum_indexed_variable():
    """Gradient through nested sum should produce non-zero result."""
    # Create expression: sum(i, sum(j, a(i,j) * x(i,j)))
    # Compute gradient w.r.t. x(i,j)
    # Assert result is a(i,j), not 0
    pass

def test_stationarity_not_all_zeros():
    """Stationarity equation should not be all zeros for active variables."""
    # Generate MCP for apl1p
    # Check stat_y equation
    # Assert at least one non-zero term exists
    pass
```

## Related Files

- `src/ad/differentiation.py`: Core differentiation logic
- `src/ad/gradient.py`: Gradient vector computation
- `src/kkt/stationarity.py`: Stationarity equation assembly

## Notes

This is a critical issue because:
1. It produces mathematically incorrect KKT conditions
2. The resulting MCP is unsolvable (empty equations paired with free variables)
3. It affects any model with indexed variables in the objective inside sums

The error message "MCP pair stat_y.y has empty equation but associated variable is NOT fixed" is GAMS detecting that the stationarity equation has no non-trivial content, which violates MCP requirements.
