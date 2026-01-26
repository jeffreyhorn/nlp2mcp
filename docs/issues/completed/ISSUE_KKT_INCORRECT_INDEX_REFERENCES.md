# Issue: KKT Transformation Generates Incorrect Index References

**Status:** Open  
**Category:** KKT Transformation / Code Generation  
**Affected Models:** chem, prodmix, blend, apl1p, dispatch (5+ models)  
**Priority:** High  
**GitHub Issue:** [#572](https://github.com/jeffreyhorn/nlp2mcp/issues/572)

## Summary

The KKT transformation generates equations with incorrect index references in several ways:
1. Using literal strings (`"elem"`, `"shop"`) instead of set index variables (`elem`, `shop`)
2. Using the same index twice (`a(c,c)`) when different indices are needed (`a(i,c)`)
3. Dimension mismatches where parameters are referenced with wrong number of indices

These cause GAMS Errors 170 (domain violation for element), 171 (domain violation for set), and 148 (dimension mismatch).

## Reproduction

### Example 1: Literal String Instead of Index Variable

**Model:** `data/gamslib/mcp/prodmix_mcp.gms`

**Generated code (line 68):**
```gams
stat_mix(desk).. ((-1) * price("desk")) + sum(shop, labor("shop","desk") * lam_cap("shop")) =E= 0;
```

**GAMS Error:**
```
*** Error 170: Domain violation for element
```

**Issue:** `labor("shop","desk")` uses literal strings instead of index variables.

**Expected:**
```gams
stat_mix(desk).. ((-1) * price(desk)) + sum(shop, labor(shop,desk) * lam_cap(shop)) =E= 0;
```

### Example 2: Same Index Used Twice

**Model:** `data/gamslib/mcp/chem_mcp.gms`

**Generated code (line 86):**
```gams
stat_x(c).. gplus(c) + log(x(c) / xb) + ... + sum(i, a(c,c) * nu_cdef(i)) + ... =E= 0;
```

**GAMS Error:**
```
*** Error 171: Domain violation for set
```

**Issue:** `a(c,c)` uses `c` for both indices when the parameter `a` is indexed by `(i,c)`.

**Expected:**
```gams
stat_x(c).. ... + sum(i, a(i,c) * nu_cdef(i)) + ... =E= 0;
```

### Example 3: Dimension Mismatch

**Model:** `data/gamslib/mcp/blend_mcp.gms`

**Generated code (line 71):**
```gams
stat_v(alloy).. compdat(""price"","alloy") + sum(elem, compdat("elem","alloy") * nu_pc("elem")) + 1 * nu_mb =E= 0;
```

**GAMS Errors:**
```
*** Error 148: Dimension different
*** Error 170: Domain violation for element
```

**Issues:** 
- Double-quoted `""price""` (separate issue)
- Literal string `"elem"` instead of index variable `elem`

## Root Cause Analysis

The KKT transformation computes gradients symbolically. When a constraint involves indexed parameters:

1. **Gradient computation** may not properly track which indices are "free" (to be summed) vs "fixed" (from the stationarity variable)
2. **Index substitution** may incorrectly use literal names instead of index variables
3. **Index mapping** between the original constraint indices and the stationarity equation indices is incorrect

### Likely Code Locations

- `src/kkt/stationarity.py`: When building stationarity equations, indices from the Lagrangian terms are not correctly mapped
- `src/ir/differentiation.py` or similar: When computing gradients, index references may be incorrectly captured

## Affected Models

| Model | Errors | Primary Pattern |
|-------|--------|-----------------|
| chem | 171 | `a(c,c)` instead of `a(i,c)` |
| prodmix | 170 (7+) | `labor("shop","desk")` literals |
| blend | 148, 170 | `compdat("elem",...)` literals |
| apl1p | 170 | Similar index issues |
| dispatch | 170 | Similar index issues |

## Proposed Fix

**Location:** `src/kkt/stationarity.py` and related gradient computation

**Approach:**

1. **Track index context**: When generating stationarity equations, maintain a mapping of:
   - The primal variable's indices (these become the equation's domain)
   - The constraint indices (these should appear correctly in gradient terms)

2. **Substitute correctly**: When a gradient term includes a parameterized reference like `a(i,c)`:
   - If `c` is the stationarity variable's index → keep as `c` (domain variable)
   - If `i` is a summation index → keep as `i` (will be summed over)
   - Never substitute with literal strings

3. **Validate index references**: After generating equations, validate that:
   - No quoted strings appear where index variables should be
   - Parameter references match their declared dimensions

## Test Cases

```python
def test_stationarity_correct_index_references():
    """Stationarity equations should use index variables, not literal strings."""
    # Parse model with indexed parameters
    # Generate KKT system
    # Check that all ParamRef indices are either:
    #   - Domain variables (single lowercase letters)
    #   - Or valid set elements (quoted strings)
    # NOT literal set names like "shop" or "elem"
    pass

def test_stationarity_parameter_dimensions():
    """Parameter references should match declared dimensions."""
    # For each ParamRef in generated equations
    # Verify index count matches parameter declaration
    pass
```

## Related Files

- `src/kkt/stationarity.py`: Stationarity equation generation
- `src/kkt/builder.py`: KKT system construction  
- `src/ir/differentiation.py`: Gradient computation (if exists)
- `src/emit/equations.py`: Equation emission

## Notes

This issue is related to but distinct from:
- **ISSUE_KKT_INDEX_REUSE_IN_SUM.md**: Same index used in equation domain AND sum (Error 125)
- **ISSUE_DOUBLE_QUOTED_STRING_INDICES.md**: Double-escaping of quotes (Error 409)

All three issues stem from the same area (KKT index handling) but have different manifestations and require different fixes.

The fundamental problem is that the KKT transformation needs a proper index tracking system that:
1. Distinguishes between set names, set elements, and index variables
2. Correctly propagates indices through gradient computation
3. Properly substitutes indices when building stationarity equations
