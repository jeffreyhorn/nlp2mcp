# Session Summary: Min/Max Reformulation Debug Session

**Date**: 2025-11-07  
**Status**: Solution identified but implementation incomplete

## Problem

Min/max reformulation for objective-defining equations creates infeasible MCP systems with PATH solver.

## Root Cause Found

The issue is a **sign mismatch** between:
1. The Jacobian computation (uses normalized equations)
2. The complementarity equation emission (uses un-normalized equations)

### Example

For `z = min(x, y)` reformulated as `z = aux_min` with constraints:

**Current broken flow**:
1. Create constraint: `aux_min - x <= 0` (Rel.LE)
2. Jacobian computes: ∂(aux_min - x)/∂aux_min = +1
3. Complementarity negates: -(aux_min - x) >= 0, i.e., x - aux_min >= 0 ✓
4. Stationarity: 1 + λ = 0 ✗ (should be 1 - λ = 0)

**Working manual MCP** (verified with PATH):
```gams
stat_aux_min.. 1 - lam_x - lam_y =E= 0;   // Negative lambda terms!
comp_x.. x - aux_min =G= 0;
comp_y.. y - aux_min =G= 0;
```

## Solution Direction

Need to ensure Jacobian derivative ∂g/∂aux_min = -1 (not +1) for correct stationarity signs.

### Attempted Approaches

1. ✗ Create `x - aux_min >= 0` → Normalization flips it back
2. ✗ Create `aux_min - x >= 0` → Wrong direction after complementarity
3. ✗ Handle Rel.GE differently in complementarity → Still wrong Jacobian signs

###  Correct Approach (Not Yet Implemented)

The Jacobian computation must use the **POST-complementarity** form of the constraint, not the pre-negation form.

OR: The stationarity assembly must account for the negation that happens in complementarity.

Specifically:
- If constraint is g(x) <= 0, complementarity creates -g(x) >= 0
- Jacobian should compute ∂(-g)/∂x = -∂g/∂x
- OR stationarity should use -J^T λ for negated constraints

## Files Modified

1. `src/kkt/reformulation.py` - Changed constraint creation (multiple iterations)
2. `src/kkt/complementarity.py` - Added Rel.GE handling
3. `docs/planning/SPRINT_5/*` - Extensive documentation

## Next Steps

1. **Option A**: Make Jacobian use complementarity form (post-negation)
   - Modify `src/ad/constraint_jacobian.py` to account for complementarity negation
   - Complex but mathematically correct

2. **Option B**: Make stationarity negate J^T terms for LE constraints
   - Modify `src/kkt/stationarity.py` to negate Jacobian terms from LE inequalities
   - Simpler implementation

3. **Option C**: Create constraints in "pre-negated" form
   - For min: create `-(x - aux_min) <= 0` explicitly as a Unary node
   - Jacobian sees the negation and computes correctly
   - Complementarity still negates, double negative cancels out
   - **Recommended approach**: Cleanest and most explicit

## Test Results

- Manual MCP with correct signs: ✓ WORKS (x=1, y=2, z=1)
- Generated MCP with current code: ✗ FAILS (wrong solution or infeasible)

## Key Insight

The mathematical formulation is correct. The implementation bug is purely about sign handling in the transformation pipeline:

```
Reformulation → Normalization → Jacobian → Complementarity → Stationarity
```

The negation in Complementarity must be reflected in either Jacobian or Stationarity computation.
