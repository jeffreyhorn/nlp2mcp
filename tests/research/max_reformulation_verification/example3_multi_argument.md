# Example 3: Multi-Argument Max Reformulation

## Problem Statement

Reformulate `z = max(x₁, x₂, ..., xₙ)` for n ≥ 3 arguments in MCP.

## General Formulation

For `z = max(x₁, x₂, ..., xₙ)`:

### Optimization Form

```
maximize  z
subject to:
  x₁ - z ≤ 0
  x₂ - z ≤ 0
  ...
  xₙ - z ≤ 0
```

### KKT Conditions

**Lagrangian:**
```
L = z + Σᵢ λᵢ(xᵢ - z)
  = z + λ₁(x₁ - z) + λ₂(x₂ - z) + ... + λₙ(xₙ - z)
```

**Stationarity:**
```
∂L/∂z = 1 - Σᵢ λᵢ = 0

Therefore: Σᵢ λᵢ = 1
```

**Complementarity:**
```
For each i: λᵢ(xᵢ - z) = 0, λᵢ ≥ 0
```

**Interpretation:**
- Exactly one xᵢ will equal z (the maximum)
- That λᵢ will be 1, all others will be 0
- Unless multiple arguments are equal to the max (then Σλᵢ = 1 still holds)

### MCP Form (n arguments)

```gams
Variables z_max;
Positive Variables lambda_max_1, lambda_max_2, ..., lambda_max_n;

Equations
    stat_z,
    comp_max_1, comp_max_2, ..., comp_max_n;

* Stationarity
stat_z.. 1 - lambda_max_1 - lambda_max_2 - ... - lambda_max_n =e= 0;

* Complementarity constraints
comp_max_1.. x_1 - z_max =l= 0;
comp_max_2.. x_2 - z_max =l= 0;
...
comp_max_n.. x_n - z_max =l= 0;

Model max_model /
    stat_z,
    comp_max_1.lambda_max_1,
    comp_max_2.lambda_max_2,
    ...
    comp_max_n.lambda_max_n
/;
```

## Scaling Analysis

| Number of Args (n) | Variables | Equations | Complementarity Pairs |
|--------------------|-----------|-----------|----------------------|
| 2 | 3 (z, λ₁, λ₂) | 3 | 2 |
| 3 | 4 (z, λ₁, λ₂, λ₃) | 4 | 3 |
| 4 | 5 (z, λ₁, λ₂, λ₃, λ₄) | 5 | 4 |
| n | n+1 | n+1 | n |

**Scaling:** Linear in n

## Example: max(x, y, z) - Three Arguments

### Problem Setup

```
z_max = max(x, y, z)
```

### Full MCP Formulation

```gams
Variables z_max;
Positive Variables lambda_x, lambda_y, lambda_z;

Equations
    stat_z_max,
    comp_max_x, comp_max_y, comp_max_z;

* Stationarity: sum of multipliers = 1
stat_z_max.. 1 - lambda_x - lambda_y - lambda_z =e= 0;

* Complementarity constraints: each arg <= z_max
comp_max_x.. x - z_max =l= 0;
comp_max_y.. y - z_max =l= 0;
comp_max_z.. z - z_max =l= 0;

Model max3_model /
    stat_z_max,
    comp_max_x.lambda_x,
    comp_max_y.lambda_y,
    comp_max_z.lambda_z
/;
```

### Worked Example: max(3, 7, 5)

**Given:** x = 3, y = 7, z = 5

**Expected:** z_max = 7, λ_x = 0, λ_y = 1, λ_z = 0

**Verification:**

1. **Primal feasibility:**
   - x - z_max = 3 - 7 = -4 ≤ 0 ✓
   - y - z_max = 7 - 7 = 0 ≤ 0 ✓
   - z - z_max = 5 - 7 = -2 ≤ 0 ✓

2. **Dual feasibility:**
   - λ_x = 0 ≥ 0 ✓
   - λ_y = 1 ≥ 0 ✓
   - λ_z = 0 ≥ 0 ✓

3. **Complementarity:**
   - λ_x(x - z_max) = 0 × (-4) = 0 ✓
   - λ_y(y - z_max) = 1 × 0 = 0 ✓
   - λ_z(z - z_max) = 0 × (-2) = 0 ✓

4. **Stationarity:**
   - λ_x + λ_y + λ_z = 0 + 1 + 0 = 1 ✓

**Conclusion:** z_max = 7 = max(3, 7, 5) ✓

### Edge Case: All Equal - max(4, 4, 4)

**Given:** x = 4, y = 4, z = 4

**Expected:** z_max = 4, λ_x + λ_y + λ_z = 1

**One valid solution:** z_max = 4, λ_x = 1/3, λ_y = 1/3, λ_z = 1/3

**Verification:**

1. **Primal feasibility:**
   - x - z_max = 4 - 4 = 0 ≤ 0 ✓
   - y - z_max = 4 - 4 = 0 ≤ 0 ✓
   - z - z_max = 4 - 4 = 0 ≤ 0 ✓

2. **Dual feasibility:**
   - λ_x = 1/3 ≥ 0 ✓
   - λ_y = 1/3 ≥ 0 ✓
   - λ_z = 1/3 ≥ 0 ✓

3. **Complementarity:**
   - All products are 0 ✓

4. **Stationarity:**
   - 1/3 + 1/3 + 1/3 = 1 ✓

**Note:** Other valid solutions include (1, 0, 0), (0, 1, 0), (0, 0, 1), or any convex combination.

## Example: max(w, x, y, z) - Four Arguments

### Problem Setup

```
result = max(w, x, y, z)
```

### MCP Formulation

```gams
Variables z_max;
Positive Variables lambda_w, lambda_x, lambda_y, lambda_z;

Equations
    stat_z_max,
    comp_max_w, comp_max_x, comp_max_y, comp_max_z;

stat_z_max.. 1 - lambda_w - lambda_x - lambda_y - lambda_z =e= 0;

comp_max_w.. w - z_max =l= 0;
comp_max_x.. x - z_max =l= 0;
comp_max_y.. y - z_max =l= 0;
comp_max_z.. z - z_max =l= 0;

Model max4_model /
    stat_z_max,
    comp_max_w.lambda_w,
    comp_max_x.lambda_x,
    comp_max_y.lambda_y,
    comp_max_z.lambda_z
/;
```

### Worked Example: max(2, 9, 5, 9)

**Given:** w = 2, x = 9, y = 5, z = 9

**Expected:** z_max = 9, λ_w = 0, λ_x + λ_z = 1, λ_y = 0

**One valid solution:** z_max = 9, λ_w = 0, λ_x = 0.5, λ_y = 0, λ_z = 0.5

**Verification:**

1. **Primal feasibility:**
   - w - z_max = 2 - 9 = -7 ≤ 0 ✓
   - x - z_max = 9 - 9 = 0 ≤ 0 ✓
   - y - z_max = 5 - 9 = -4 ≤ 0 ✓
   - z - z_max = 9 - 9 = 0 ≤ 0 ✓

2. **Dual feasibility:**
   - All λ ≥ 0 ✓

3. **Complementarity:**
   - All products are 0 ✓

4. **Stationarity:**
   - 0 + 0.5 + 0 + 0.5 = 1 ✓

**Conclusion:** z_max = 9 = max(2, 9, 5, 9) ✓

**Note:** Multiple maxima (x and z both equal 9) lead to non-unique λ values, but Σλ = 1 always holds.

## Implementation Pseudocode

```python
def reformulate_max(args: list[Expr], context: str) -> tuple[str, list[Constraint]]:
    """
    Reformulate max(arg1, arg2, ..., argn) as MCP constraints.
    
    Args:
        args: List of n argument expressions
        context: Unique context string for naming
        
    Returns:
        aux_var: Name of auxiliary variable representing max result
        constraints: List of n complementarity constraints
        stationarity: Stationarity equation (sum of lambdas = 1)
    """
    n = len(args)
    aux_var = f"aux_max_{context}"
    constraints = []
    lambda_vars = []
    
    # Create n complementarity constraints
    for i, arg in enumerate(args):
        lambda_name = f"lambda_{aux_var}_{i}"
        lambda_vars.append(lambda_name)
        
        # arg - aux <= 0  (i.e., aux >= arg)
        constraint = Constraint(
            lhs=BinaryOp('-', arg, VarRef(aux_var)),
            rhs=Constant(0),
            operator='<=',
            multiplier=lambda_name
        )
        constraints.append(constraint)
    
    # Stationarity: 1 - sum(lambda_i) = 0
    lambda_sum = sum(VarRef(lam) for lam in lambda_vars)
    stationarity = Equation(
        lhs=BinaryOp('-', Constant(1), lambda_sum),
        rhs=Constant(0)
    )
    
    return aux_var, constraints, stationarity
```

## Complexity Analysis

### Time Complexity
- **Reformulation:** O(n) - linear in number of arguments
- **PATH solver:** O(n) per iteration for this subproblem

### Space Complexity
- **Variables:** O(n) - need n+1 variables total
- **Constraints:** O(n) - need n complementarity constraints

### Comparison with Pairwise Chaining

**Alternative:** max(x, y, z) = max(max(x, y), z)

This requires:
- First max: 3 variables (z1, λ1, λ2)
- Second max: 3 variables (z2, λ3, λ4)
- Total: 6 variables, 6 equations

**Direct multi-argument:**
- 4 variables (z, λ_x, λ_y, λ_z)
- 4 equations

**Conclusion:** Direct multi-argument is more efficient than pairwise chaining.

## Summary

Multi-argument max reformulation:

1. **Scales linearly** with number of arguments
2. **Follows same pattern** as 2-argument max
3. **More efficient** than pairwise chaining
4. **Stationarity condition** always: Σλᵢ = 1
5. **Each argument** gets its own complementarity constraint

The reformulation is straightforward to implement and maintains O(n) complexity.
