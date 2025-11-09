# Critical Finding: Strategy 1 May Not Be Needed

## Summary

After deep analysis, we've discovered that **Strategy 1 (Direct Objective Substitution) creates a mathematically inconsistent system**, while **the standard min/max reformulation (Strategy 2) should actually work correctly**.

## The Misconception

The research document claims that when min/max appears in objective-defining equations, the standard KKT reformulation creates an infeasible system. However, this claim appears to be **incorrect**.

## Mathematical Analysis

### Original Problem
```
minimize obj
subject to:
  obj = z
  z = min(x,y)
  1 ≤ x ≤ 10, 2 ≤ y ≤ 10
```

**Expected solution**: z* = 1, x* = 1, y* = 2

### After Standard Reformulation (No Strategy 1)
```
minimize obj
subject to:
  obj = z
  z = aux
  aux ≤ x  (with multiplier λ_x)
  aux ≤ y  (with multiplier λ_y)
  bounds...
```

### KKT Conditions at Solution
```
∂L/∂obj = 1 - ν_objdef = 0           → ν_objdef = 1
∂L/∂z = ν_objdef - ν_aux = 0         → ν_aux = 1
∂L/∂aux = ν_aux - λ_x - λ_y = 0      → λ_x + λ_y = 1
∂L/∂x = λ_x - π_x^L = 0              → π_x^L = λ_x
∂L/∂y = λ_y - π_y^L = 0              → π_y^L = λ_y
```

### Complementarity
- At solution: aux* = 1, x* = 1, y* = 2
- aux ≤ x: 1 ≤ 1 (ACTIVE) → λ_x ≥ 0, and (1-1) · λ_x = 0 ✓
- aux ≤ y: 1 ≤ 2 (SLACK) → λ_y = 0, and (2-1) · 0 = 0 ✓

### Solution
```
λ_x = 1, λ_y = 0
π_x^L = 1, π_y^L = 0
ν_objdef = 1, ν_aux = 1
```

**This is FEASIBLE and CORRECT!** ✓

## Why Strategy 1 Fails

Strategy 1 tries to create stationarity equations for BOTH `obj` and `aux`, leading to:

```
stat_obj: ∂obj/∂obj + ν_objdef = 0
```

But this creates contradictions:
- If ∂obj/∂obj = 0: leads to infeasibility (λ's sum to negative)
- If ∂obj/∂obj = 1: leads to original issue (if there was one)

The fundamental problem: **Strategy 1 over-constrains the system** by treating both the original objective variable and the auxiliary variable as primal variables with stationarity conditions.

## The Real Issue

Going back to check: what was the ACTUAL problem that Strategy 1 was supposed to solve?

Looking at the test output from earlier sessions, the error WITHOUT Strategy 1 was:
```
*** Unmatched free variables = 1
     obj
```

This suggests `obj` had no equation paired with it. But in our current implementation, `objdef` should be paired with `obj` in the MCP model...

**Hypothesis**: The original bug might have been in the MCP emission code, not in the mathematical formulation. The standard reformulation is mathematically sound, but there may have been an implementation bug in how the MCP pairs were generated.

## Recommendation

1. **Disable Strategy 1** entirely as it creates mathematical inconsistencies
2. **Test the standard reformulation** (Strategy 2) with PATH solver
3. If there are still issues, they're likely **implementation bugs** in:
   - How `objdef` equation is paired in the MCP model
   - How multipliers are created and referenced
   - Not fundamental mathematical problems

## Action Items

1. Add a flag to completely disable Strategy 1
2. Test standard reformulation on all 6 test cases
3. If issues remain, debug the MCP generation, not the mathematics
4. Consider removing Strategy 1 code entirely if standard reformulation works

## Conclusion

The non-differentiability of `min(x,y)` is NOT a problem because:
1. The reformulation replaces it with differentiable inequality constraints
2. The KKT conditions for the reformulated problem are well-defined
3. The solution to the reformulated MCP equals the solution to the original NLP

**Strategy 1 was based on a misconception and should likely be abandoned.**
