# Issue: himmel16 Translation Bugs - Constraint RHS and Stationarity Indexing

**Status**: FIXED
**GitHub Issue**: #649 (https://github.com/jeffreyhorn/nlp2mcp/issues/649)
**Model**: `himmel16.gms`
**Component**: Converter / KKT Transformation

## Fix Status

| Bug | Status | Fixed In |
|-----|--------|----------|
| Invalid .fx bound names (nested parens) | FIXED | Commit 494d31c (P3 fix) |
| Constraint RHS missing | FIXED | Sprint 18 - complementarity.py fix |
| Stationarity equation indexing | FIXED | This commit - stationarity.py fix |

## Summary

The `himmel16` model translation had three bugs, all now fixed:

1. **Invalid .fx bound names**: Nested parentheses in bound names - **FIXED** (P3 fix)
2. **Inequality constraint missing RHS and sign flip**: The `maxdist` constraint loses its RHS constant and has incorrect sign - **FIXED** (Sprint 18)
3. **Stationarity equation indexing bug**: The partial derivatives use `(x(i) - x(i))` instead of `(x(i) - x(j))` - **FIXED** (This commit)

## Original Model Context

The `himmel16.gms` model contains an inequality constraint:
```gams
maxdist(i,j)$(ord(i) < ord(j)).. sqr(x(i)-x(j)) + sqr(y(i)-y(j)) =l= 1;
```

This constrains the maximum distance between points to be at most 1.

---

## Bug 1: Constraint RHS Missing - FIXED (Sprint 18)

### Problem
The complementarity builder was only using `eq_def.lhs_rhs[0]` (the LHS) to build the complementarity equation, ignoring the RHS constant.

### Fix
Changed to properly build the normalized form `LHS - RHS` before negating in `src/kkt/complementarity.py`.

---

## Bug 2: Stationarity Equation Indexing - FIXED

### Problem
The stationarity equations used `(x(i) - x(i))` instead of `(x(i) - x(j))`:

```gams
* Before (WRONG):
stat_x(i).. ... + sum(j, 2 * (x(i) - x(i)) * lam_maxdist(i,j)) =E= 0;

* After (CORRECT):
stat_x(i).. ... + sum(j, 2 * (x(i) - x(j)) * lam_maxdist(i,j)) =E= 0;
```

### Root Cause

The Jacobian is computed element-by-element correctly:
- `d(maxdist(1,2))/d(x(1)) = 2 * (x(1) - x(2))` - Correct!

The bug was in `_replace_indices_in_expr` in `src/kkt/stationarity.py`. When converting element-specific indices to set indices, the `element_to_set` mapping didn't distinguish between:
1. The element corresponding to the variable's index (should become `i`)
2. The element corresponding to the constraint's other index (should become `j`)

Both elements mapped to `i` because they came from the same underlying set.

### Fix Details

**File**: `src/kkt/stationarity.py`

1. **Added `_build_constraint_element_mapping()` function**: Creates a constraint-specific element-to-set mapping that uses the constraint's indices and domain to map elements to their correct position.

```python
def _build_constraint_element_mapping(
    base_element_to_set: dict[str, str],
    constraint_indices: tuple[str, ...],
    constraint_domain: tuple[str, ...],
) -> ChainMap[str, str]:
    """Build constraint-specific element-to-set mapping (returned as a ChainMap overlay).
    
    For maxdist(1,2) with domain (i,j):
      "1" -> "i" (position 0)
      "2" -> "j" (position 1)
    
    This ensures x(1) - x(2) becomes x(i) - x(j), not x(i) - x(i).
    """
```

2. **Modified `_add_indexed_jacobian_terms()`**: Now builds constraint-specific mappings for each constraint before replacing indices in derivatives.

3. **Added `prefer_declared_domain` parameter to `_replace_matching_indices()`**: This parameter controls whether to prefer the declared domain (for parameters, Issue #572) or the element_to_set mapping (for variables, Issue #649).
   - For `ParamRef`: `prefer_declared_domain=True` - parameter domain is authoritative
   - For `VarRef`: `prefer_declared_domain=False` - constraint position mapping is used

### Technical Details

When processing a constraint like `maxdist(i,j)` with instance `maxdist(1,2)`:
1. The constraint's `eq_indices = ('1', '2')` and `mult_domain = ('i', 'j')`
2. `_build_constraint_element_mapping()` creates: `{'1': 'i', '2': 'j', ...}`
3. When replacing indices in `2 * (x(1) - x(2))`:
   - `x(1)` → `x(i)` (element '1' at position 0 → 'i')
   - `x(2)` → `x(j)` (element '2' at position 1 → 'j')

This correctly preserves the constraint's domain structure in the stationarity equation.

---

## Verification

After the fix:
```gams
stat_x(i).. ((-1) * (0.5 * y(i))) + ((-1) * (0.5 * y(i))) * nu_areadef(i) + 0 * nu_obj2 + 1 * nu_x_fx_1 + 0 * nu_y_fx_1 + 0 * nu_y_fx_2 + sum(j, 2 * (x(i) - x(j)) * lam_maxdist(i,j)) =E= 0;

stat_y(i).. ((-1) * (0.5 * ((-1) * x(i)))) + ((-1) * (0.5 * ((-1) * x(i)))) * nu_areadef(i) + 0 * nu_obj2 + 0 * nu_x_fx_1 + 1 * nu_y_fx_1 + 0 * nu_y_fx_2 + sum(j, 2 * (y(i) - y(j)) * lam_maxdist(i,j)) =E= 0;
```

The stationarity equations now correctly reference `x(i) - x(j)` and `y(i) - y(j)`.

## Testing

All quality checks pass:
- `make typecheck` - SUCCESS
- `make lint` - SUCCESS  
- `make format` - SUCCESS
- `make test` - SUCCESS (3258 passed)

The fix also preserves the parameter domain disambiguation behavior tested in Issue #572.

## Affected Components

- `src/kkt/stationarity.py` - Main fix location
  - `_build_constraint_element_mapping()` - New function
  - `_add_indexed_jacobian_terms()` - Uses constraint-specific mapping
  - `_replace_matching_indices()` - Added `prefer_declared_domain` parameter
