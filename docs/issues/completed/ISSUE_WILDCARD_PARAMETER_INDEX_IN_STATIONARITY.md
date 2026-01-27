# Issue: Wildcard Parameter Index Incorrectly Emitted in Stationarity Equations

**Status:** Open  
**Category:** KKT Transformation / Stationarity Generation  
**Affected Models:** blend, and models with wildcard (*) parameter domains  
**Priority:** Medium  
**GitHub Issue:** [#575](https://github.com/jeffreyhorn/nlp2mcp/issues/575)

## Summary

When a parameter is declared with a wildcard domain (e.g., `compdat(*,alloy)`), the stationarity equation generation incorrectly emits the literal `"*"` as the index instead of resolving it to the actual element being accessed in the original equation.

## Reproduction

### Model: blend

**Original parameter declaration:**
```gams
Table compdat(*,alloy) 'composition data (pct and price)'
         a     b     c     d     e     f     g     h     i
lead    10    10    40    60    30    30    30    50    20
zinc    10    30    50    30    30    40    20    40    30
tin     80    60    10    10    40    30    50    10    50
price  4.1   4.3   5.8   6.0   7.6   7.5   7.3   6.9   7.3 ;
```

**Original objective equation:**
```gams
ac..  phi =e= sum(alloy, compdat("price",alloy)*v(alloy));
```

**Generated stationarity equation (stat_v in blend_mcp.gms line 71):**
```gams
stat_v(alloy).. compdat("*",alloy) + sum(elem, compdat("*",alloy) * nu_pc(elem)) + 1 * nu_mb =E= 0;
```

**GAMS Error:**
```
*** SOLVE aborted (3 Errors)
```
The `"*"` is not a valid element - it should be `"price"`.

**Expected stationarity equation:**
```gams
stat_v(alloy).. compdat("price",alloy) + sum(elem, compdat(elem,alloy) * nu_pc(elem)) + 1 * nu_mb =E= 0;
```

## Root Cause Analysis

The KKT transformation computes the gradient of the objective with respect to each variable. When the objective contains `compdat("price",alloy) * v(alloy)`:

1. The derivative of `compdat("price",alloy) * v(alloy)` with respect to `v(alloy)` is `compdat("price",alloy)`
2. However, when the parameter is declared with a wildcard domain `compdat(*,alloy)`, the differentiation or index replacement logic incorrectly substitutes `"*"` instead of preserving or inferring the actual index `"price"`

The issue likely occurs in:
- `src/ad/differentiation.py`: When differentiating expressions containing parameters with wildcard domains
- `src/kkt/stationarity.py`: When building stationarity equations and replacing indices

## Expected Behavior

When generating stationarity equations:
1. Parameters with wildcard domains should preserve their concrete indices from the original expression
2. `compdat("price",alloy)` should remain `compdat("price",alloy)` in the derivative
3. The wildcard `*` should never appear as an actual index in generated code

## Affected Models

| Model | Parameter | Wildcard Domain | Used Elements |
|-------|-----------|-----------------|---------------|
| blend | compdat(*,alloy) | First position | "price", elem |

Other models with wildcard parameter domains may also be affected.

## Proposed Fix

**Location:** `src/ad/differentiation.py` and/or `src/kkt/stationarity.py`

**Approach:**

1. When differentiating a ParamRef, preserve the concrete indices exactly as they appear
2. During index replacement in stationarity building, don't replace concrete element indices (like `"price"`) with set names or wildcards
3. Add validation to detect if `"*"` appears as an index in generated code (it should never happen)

**Key changes:**
1. Review `_replace_indices_in_expr()` to ensure it doesn't replace concrete indices that aren't set elements
2. Ensure differentiation preserves concrete indices in ParamRef nodes
3. Add a post-generation check to flag any `"*"` indices as errors

## Test Cases

```python
def test_wildcard_parameter_preserves_concrete_index():
    """Concrete parameter indices should be preserved in stationarity equations."""
    # Create model with compdat(*,alloy) and compdat("price",alloy) usage
    # Generate stationarity equation for v(alloy)
    # Assert that compdat("price",alloy) appears, NOT compdat("*",alloy)
    pass

def test_no_wildcard_in_generated_code():
    """Generated code should never contain '*' as an actual index."""
    # Generate MCP for blend model
    # Search for any ParamRef with "*" index
    # Assert none found
    pass
```

## Related Files

- `src/ad/differentiation.py`: Expression differentiation
- `src/kkt/stationarity.py`: Stationarity equation building
- `src/ir/ast.py`: ParamRef node handling

## Notes

This issue is distinct from:
- **ISSUE_KKT_INCORRECT_INDEX_REFERENCES.md** (completed): Set indices being incorrectly mapped
- **ISSUE_QUOTED_INDICES_IN_MODEL_STATEMENT.md**: Quoted indices in model statement

The wildcard `*` in GAMS parameter declarations means "any element from any set". It's a domain specification, not an actual element, and should never appear in generated equation code.
