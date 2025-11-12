# KKT Theory for Maximize vs Minimize Objectives

**Date:** 2025-11-12  
**Purpose:** Mathematical foundation for fixing maximize bound multiplier bug  
**Reference:** Boyd & Vandenberghe, Convex Optimization (2004), Section 5.5.3

## Summary

The bound multiplier signs **DO NOT** change between minimize and maximize problems. Instead, the objective gradient term flips sign for maximize problems. The current code incorrectly uses the same signs for both cases.

## KKT Conditions for Minimization

**Standard form:**
```
minimize    f(x)
subject to  h_i(x) = 0         (i ∈ E, equality constraints)
            g_j(x) ≤ 0         (j ∈ I, inequality constraints)
            l_k ≤ x_k ≤ u_k    (k, variable bounds)
```

**KKT Stationarity (Lagrangian first-order condition):**
```
∇f(x*) + Σ_i ν_i ∇h_i(x*) + Σ_j λ_j ∇g_j(x*) - π^L + π^U = 0
```

Where:
- `∇f(x*)` = gradient of objective at optimal point
- `ν_i` = free multipliers for equality constraints
- `λ_j ≥ 0` = non-negative multipliers for inequality constraints
- `π^L ≥ 0` = non-negative multipliers for lower bounds (x ≥ l)
- `π^U ≥ 0` = non-negative multipliers for upper bounds (x ≤ u)

**Sign explanation for bounds:**
- Lower bound `x_k ≥ l_k` is equivalent to `-x_k + l_k ≤ 0`
  - Gradient w.r.t. x_k is `-1`
  - Contributes: `π^L_k · (-1) = -π^L_k` to stationarity
  - Hence: **subtract π^L**

- Upper bound `x_k ≤ u_k` is equivalent to `x_k - u_k ≤ 0`
  - Gradient w.r.t. x_k is `+1`
  - Contributes: `π^U_k · (+1) = +π^U_k` to stationarity
  - Hence: **add π^U**

## KKT Conditions for Maximization

**Standard form:**
```
maximize    f(x)
subject to  h_i(x) = 0
            g_j(x) ≤ 0
            l_k ≤ x_k ≤ u_k
```

**Key transformation:**
```
maximize f(x)  ≡  minimize -f(x)
```

**KKT Stationarity for maximize:**
```
-∇f(x*) + Σ_i ν_i ∇h_i(x*) + Σ_j λ_j ∇g_j(x*) - π^L + π^U = 0
```

Or equivalently, rearranging:
```
∇f(x*) = Σ_i ν_i ∇h_i(x*) + Σ_j λ_j ∇g_j(x*) - π^L + π^U
```

**Critical observation:**
- The objective gradient term changes sign: `∇f` becomes `-∇f`
- The bound multiplier signs **remain the same**: still `-π^L + π^U`
- Constraint multiplier terms remain the same

## Why Bound Signs Stay the Same

The bound constraints are **independent of objective sense**:
- Lower bound `x_k ≥ l_k` is the same constraint whether minimizing or maximizing
- Upper bound `x_k ≤ u_k` is the same constraint whether minimizing or maximizing
- The complementarity conditions remain the same:
  - `(x_k - l_k) · π^L_k = 0` (lower bound complementarity)
  - `(u_k - x_k) · π^U_k = 0` (upper bound complementarity)

Therefore, bound multiplier signs are **invariant** to objective sense.

## Current Bug Analysis

### Current Implementation (stationarity.py:409-418)

For **all objectives** (minimize and maximize):
```python
# Subtract π^L (lower bound multiplier, if exists)
key = (var_name, var_indices)
if key in kkt.multipliers_bounds_lo:
    piL_name = create_bound_lo_multiplier_name(var_name)
    expr = Binary("-", expr, MultiplierRef(piL_name, var_indices))

# Add π^U (upper bound multiplier, if exists)
if key in kkt.multipliers_bounds_up:
    piU_name = create_bound_up_multiplier_name(var_name)
    expr = Binary("+", expr, MultiplierRef(piU_name, var_indices))
```

This is **CORRECT for minimize**, but **INCORRECT for maximize**.

### What Happens for Maximize

The current code builds:
```
expr = ∇f + [constraint terms] - π^L + π^U
```

But for maximize, it should be:
```
expr = -∇f + [constraint terms] - π^L + π^U
```

The gradient term `∇f` needs to be negated for maximize objectives.

## Example: Simple Maximize with Upper Bound

**Problem:**
```
maximize    x
subject to  x ≤ 10
```

**Expected solution:** x* = 10 (push to upper bound)

**KKT stationarity at x* = 10:**
```
-∇f + π^U = 0
-1 + π^U = 0
π^U = 1  (active bound, complementarity satisfied)
```

**Current buggy code generates:**
```
1 + π^U = 0
π^U = -1  (WRONG! Multiplier should be non-negative)
```

This violates dual feasibility (π^U ≥ 0) and causes PATH solver to fail or find incorrect solutions.

## Correct Formulation

For maximize problems, the stationarity equation should be:

```python
# Build base expression (starts with gradient and constraint terms)
expr = ...

# For MAXIMIZE objectives, negate the gradient term
if kkt.model_ir.objective.sense == ObjSense.MAX:
    # Gradient term needs to flip sign for maximize
    # This is typically the first term in expr
    pass  # Will be handled by negating gradient earlier or entire equation

# Bound multiplier signs remain the same for both minimize and maximize
if key in kkt.multipliers_bounds_lo:
    piL_name = create_bound_lo_multiplier_name(var_name)
    expr = Binary("-", expr, MultiplierRef(piL_name, var_indices))

if key in kkt.multipliers_bounds_up:
    piU_name = create_bound_up_multiplier_name(var_name)
    expr = Binary("+", expr, MultiplierRef(piU_name, var_indices))
```

## References

1. Boyd, S., & Vandenberghe, L. (2004). *Convex Optimization*. Cambridge University Press.
   - Section 5.5.3: KKT conditions for inequality-constrained problems
   - Page 243: Stationarity condition

2. Nocedal, J., & Wright, S. J. (2006). *Numerical Optimization* (2nd ed.). Springer.
   - Chapter 12: Theory of Constrained Optimization
   - Section 12.1: KKT conditions

3. Bertsekas, D. P. (1999). *Nonlinear Programming* (2nd ed.). Athena Scientific.
   - Section 3.3: Necessary and Sufficient Conditions for Optimality

## Conclusion

The fix must ensure:
1. Objective gradient term is negated for maximize problems
2. Bound multiplier signs remain `-π^L + π^U` for both minimize and maximize
3. Constraint multiplier terms remain unchanged

This can be achieved by:
- Negating the gradient term when building the stationarity expression (before adding bounds)
- OR negating the entire objective expression early in the pipeline
- OR transforming maximize → minimize early in processing
