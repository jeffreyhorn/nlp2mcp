# Issue: himmel16 Translation Bugs - Constraint RHS and Stationarity Indexing

**Status**: PARTIALLY FIXED (Sprint 18)
**GitHub Issue**: #649 (https://github.com/jeffreyhorn/nlp2mcp/issues/649)
**Model**: `himmel16.gms`
**Component**: Converter / KKT Transformation

## Fix Status

| Bug | Status | Fixed In |
|-----|--------|----------|
| Invalid .fx bound names (nested parens) | FIXED | Commit 494d31c (P3 fix) |
| Constraint RHS missing | FIXED | This sprint - complementarity.py fix |
| Stationarity equation indexing | OPEN | Needs deeper investigation |

## Summary

The `himmel16` model translation has two critical bugs:

1. **Inequality constraint missing RHS and sign flip**: The `maxdist` constraint loses its RHS constant and has incorrect sign - **FIXED**
2. **Stationarity equation indexing bug**: The partial derivatives use `(x(i) - x(i))` instead of `(x(i) - x(j))` - **OPEN**

## Original Model Context

The `himmel16.gms` model contains an inequality constraint:
```gams
maxdist(i,j)$(ord(i) < ord(j)).. sqr(x(i)-x(j)) + sqr(y(i)-y(j)) =l= 1;
```

This constrains the maximum distance between points to be at most 1.

---

## Bug 1: Constraint RHS Missing - FIXED

### Problem
The complementarity builder was only using `eq_def.lhs_rhs[0]` (the LHS) to build the complementarity equation, ignoring the RHS constant.

### Original Behavior
```gams
comp_maxdist(i,j).. ((-1) * (sqr(x(i) - x(j)) + sqr(y(i) - y(j)))) =G= 0;
```

### Expected Behavior
```gams
comp_maxdist(i,j).. -(sqr(x(i) - x(j)) + sqr(y(i) - y(j)) - 1) =G= 0;
```
Which simplifies to: `1 - sqr(x(i) - x(j)) - sqr(y(i) - y(j)) >= 0`

### Root Cause
In `src/kkt/complementarity.py`, the code was:
```python
g_expr = eq_def.lhs_rhs[0]  # Only took LHS, ignored RHS
F_lam = Unary("-", g_expr)  # Negated just the LHS
```

### Fix
Changed to properly build the normalized form `LHS - RHS` before negating:
```python
lhs_expr, rhs_expr = eq_def.lhs_rhs

# Build normalized form: LHS - RHS
if isinstance(rhs_expr, Const) and rhs_expr.value == 0.0:
    normalized_expr = lhs_expr
else:
    normalized_expr = Binary("-", lhs_expr, rhs_expr)

if eq_def.relation == Rel.LE:
    # (LHS - RHS) <= 0 becomes -(LHS - RHS) >= 0
    F_lam = Unary("-", normalized_expr)
    negated = True
```

---

## Bug 2: Stationarity Equation Indexing - OPEN

### Problem
The stationarity equations use `(x(i) - x(i))` instead of `(x(i) - x(j))`:

```gams
* Actual (WRONG):
stat_x(i).. ... + sum(j, 2 * (x(i) - x(i)) * lam_maxdist(i,j)) =E= 0;

* Expected:
stat_x(i).. ... + sum(j, 2 * (x(i) - x(j)) * lam_maxdist(i,j)) =E= 0;
```

### Root Cause Analysis

The Jacobian is computed element-by-element correctly. For example:
- `d(maxdist(1,2))/d(x(1)) = 2 * (x(1) - x(2))` - Correct!

The bug is in `_replace_indices_in_expr` in `src/kkt/stationarity.py`. When converting element-specific indices to set indices:
1. Element `"1"` maps to set `"i"`
2. Element `"2"` also maps to set `"i"`

So `x(1) - x(2)` becomes `x(i) - x(i)` instead of `x(i) - x(j)`.

### Technical Details

The `element_to_set` mapping doesn't distinguish between:
1. The element that corresponds to the stationarity variable index (should become `i`)
2. Other elements from the same set in the constraint (should become `j` from `maxdist(i,j)`)

### Required Fix

To properly fix this, the stationarity builder needs to:
1. Track the relationship between variable indices and constraint indices
2. When building Jacobian terms for `stat_x(i)`:
   - The variable's index (`x(1)` for `stat_x(1)`) should become `x(i)`
   - Other indices from the constraint (`x(2)` from `maxdist(1,2)`) should become `x(j)`
3. This requires preserving the constraint's domain structure when replacing indices

### Complexity

This is a non-trivial fix because:
- The current approach processes derivatives element-by-element
- Index replacement is done without knowledge of which elements belong together
- Multi-indexed constraints (like `maxdist(i,j)`) need special handling where different elements from the same underlying set map to different domain indices

### Workaround

For models like himmel16, per-instance stationarity equations could be generated instead of indexed equations. This would avoid the index replacement issue but would produce verbose output.

---

## Affected Components

- `src/kkt/complementarity.py` - Bug 1 fix applied
- `src/kkt/stationarity.py` - Bug 2 location, needs fix
- `_replace_indices_in_expr` - Core function needing enhancement
- `_build_element_to_set_mapping` - Needs constraint-aware variant

## Priority

High - Bug 2 produces mathematically incorrect MCP formulations for models with multi-indexed constraints where both indices come from the same underlying set (via aliases).
