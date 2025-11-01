# Example 1: Simple max(x,y) Reformulation

## Problem Statement

Reformulate `z = max(x, y)` for use in a Mixed Complementarity Problem (MCP).

## Mathematical Development

### Step 1: Optimization Formulation

The max function can be expressed as an optimization problem:

```
maximize  z
subject to:
  x - z ≤ 0  (z must be ≥ x)
  y - z ≤ 0  (z must be ≥ y)
```

At optimum: z* = max(x, y)

Introduce Lagrange multipliers λ_x ≥ 0 and λ_y ≥ 0:

```
maximize  z
subject to:
  x - z ≤ 0
  y - z ≤ 0
  
with complementarity:
  (x - z) ⊥ λ_x, λ_x ≥ 0
  (y - z) ⊥ λ_y, λ_y ≥ 0
```

### Step 2: KKT Conditions

Form the Lagrangian (for maximization problem):
```
L(z, λ_x, λ_y) = z + λ_x(x - z) + λ_y(y - z)
```

**Stationarity** (∇L = 0):
```
∂L/∂z = 1 - λ_x - λ_y = 0
```

Therefore: **λ_x + λ_y = 1**

**Primal Feasibility**:
```
x - z ≤ 0
y - z ≤ 0
```

**Dual Feasibility**:
```
λ_x ≥ 0
λ_y ≥ 0
```

**Complementarity**:
```
λ_x(x - z) = 0
λ_y(y - z) = 0
```

### Step 3: MCP Formulation

The complete MCP system in GAMS notation:

```gams
Variables
    x, y, z_max;

Positive Variables
    lambda_x, lambda_y;

Equations
    stat_x, stat_y, stat_z,
    comp_max_x, comp_max_y;

* Stationarity conditions
stat_x.. lambda_x =e= 0;
stat_y.. lambda_y =e= 0;
stat_z.. 1 - lambda_x - lambda_y =e= 0;

* Complementarity constraints
comp_max_x.. x - z_max =l= 0;
comp_max_y.. y - z_max =l= 0;

* Model with complementarity pairs
Model max_model /
    stat_x, stat_y, stat_z,
    comp_max_x.lambda_x,
    comp_max_y.lambda_y
/;
```

**Key Points:**
- Constraints use `=l=` (less than or equal) for max
- Stationarity for z: `1 - lambda_x - lambda_y =e= 0`
- Complementarity pairs: `constraint.multiplier`

## Worked Examples

### Example A: max(3, 5)

**Given:** x = 3, y = 5

**Expected:** z = 5, λ_x = 0, λ_y = 1

**Verification:**

1. **Primal feasibility:**
   - x - z = 3 - 5 = -2 ≤ 0 ✓
   - y - z = 5 - 5 = 0 ≤ 0 ✓

2. **Dual feasibility:**
   - λ_x = 0 ≥ 0 ✓
   - λ_y = 1 ≥ 0 ✓

3. **Complementarity:**
   - λ_x(x - z) = 0 × (-2) = 0 ✓
   - λ_y(y - z) = 1 × 0 = 0 ✓

4. **Stationarity:**
   - λ_x + λ_y = 0 + 1 = 1 ✓

**Conclusion:** z = 5 = max(3, 5) ✓

### Example B: max(7, 2)

**Given:** x = 7, y = 2

**Expected:** z = 7, λ_x = 1, λ_y = 0

**Verification:**

1. **Primal feasibility:**
   - x - z = 7 - 7 = 0 ≤ 0 ✓
   - y - z = 2 - 7 = -5 ≤ 0 ✓

2. **Dual feasibility:**
   - λ_x = 1 ≥ 0 ✓
   - λ_y = 0 ≥ 0 ✓

3. **Complementarity:**
   - λ_x(x - z) = 1 × 0 = 0 ✓
   - λ_y(y - z) = 0 × (-5) = 0 ✓

4. **Stationarity:**
   - λ_x + λ_y = 1 + 0 = 1 ✓

**Conclusion:** z = 7 = max(7, 2) ✓

### Example C: max(4, 4)

**Given:** x = 4, y = 4

**Expected:** z = 4, λ_x + λ_y = 1 (any valid combination)

**One valid solution:** z = 4, λ_x = 0.5, λ_y = 0.5

**Verification:**

1. **Primal feasibility:**
   - x - z = 4 - 4 = 0 ≤ 0 ✓
   - y - z = 4 - 4 = 0 ≤ 0 ✓

2. **Dual feasibility:**
   - λ_x = 0.5 ≥ 0 ✓
   - λ_y = 0.5 ≥ 0 ✓

3. **Complementarity:**
   - λ_x(x - z) = 0.5 × 0 = 0 ✓
   - λ_y(y - z) = 0.5 × 0 = 0 ✓

4. **Stationarity:**
   - λ_x + λ_y = 0.5 + 0.5 = 1 ✓

**Conclusion:** z = 4 = max(4, 4) ✓

**Note:** Other valid solutions exist, e.g., (λ_x = 0, λ_y = 1) or (λ_x = 1, λ_y = 0)

## Comparison with Min

| Aspect | min(x,y) | max(x,y) |
|--------|----------|----------|
| **Constraint form** | x - z ≥ 0 | x - z ≤ 0 |
| **GAMS operator** | `=g=` | `=l=` |
| **Interpretation** | z ≤ x, z ≤ y | z ≥ x, z ≥ y |
| **Stationarity** | -1 + λ_x + λ_y = 0 | 1 - λ_x - λ_y = 0 |
| **Multiplier sum** | λ_x + λ_y = 1 | λ_x + λ_y = 1 |
| **Active constraint** | Smallest arg | Largest arg |

**Key insight:** The only difference is the inequality direction (≥ vs ≤)

## Common Mistakes to Avoid

### ❌ Mistake 1: Wrong constraint direction
```gams
* WRONG: Using =g= (greater than) for max
comp_max_x.. x - z_max =g= 0;  # INCORRECT!
```

**Correct:**
```gams
comp_max_x.. x - z_max =l= 0;  # CORRECT
```

### ❌ Mistake 2: Wrong stationarity sign
```gams
* WRONG: Negating stationarity for max
stat_z.. -1 - lambda_x - lambda_y =e= 0;  # INCORRECT!
```

**Correct:**
```gams
stat_z.. 1 - lambda_x - lambda_y =e= 0;  # CORRECT
```

### ❌ Mistake 3: Confusing max with min formulation
Max and min have different constraint directions. Don't copy-paste min code for max!

## Implementation Guidance

### Pseudocode for Max Reformulation

```python
def reformulate_max(args: list[Expr], context: str) -> tuple[str, list[Constraint]]:
    """
    Reformulate max(args) as MCP constraints.
    
    Returns:
        aux_var_name: Name of auxiliary variable z representing max result
        constraints: List of complementarity constraints
    """
    aux_name = f"aux_max_{context}"
    constraints = []
    
    for i, arg in enumerate(args):
        # For max: arg - aux <= 0  (i.e., aux >= arg)
        constraint = Constraint(
            lhs=BinaryOp('-', arg, VarRef(aux_name)),
            rhs=Constant(0),
            operator='<=',
            multiplier=f"lambda_{aux_name}_{i}"
        )
        constraints.append(constraint)
    
    # Stationarity: 1 - sum(lambda_i) = 0
    lambda_sum = sum(VarRef(f"lambda_{aux_name}_{i}") for i in range(len(args)))
    stationarity = Equation(
        lhs=BinaryOp('-', Constant(1), lambda_sum),
        rhs=Constant(0)
    )
    
    return aux_name, constraints, stationarity
```

## Summary

The max(x,y) reformulation for MCP:

1. **Creates auxiliary variable** z_max
2. **Adds constraints** x - z ≤ 0, y - z ≤ 0
3. **Introduces multipliers** λ_x, λ_y ≥ 0
4. **Enforces complementarity** (x - z) ⊥ λ_x, (y - z) ⊥ λ_y
5. **Ensures stationarity** λ_x + λ_y = 1

The reformulation is **dual to min** with the key difference being constraint inequality direction (≤ vs ≥).
