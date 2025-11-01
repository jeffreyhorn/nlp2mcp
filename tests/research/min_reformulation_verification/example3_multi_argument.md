# Example 3: Multi-Argument Min

## Problem: Three Arguments

```gams
Variables x, y, z, w, obj;

Equations objdef, minconstraint;

objdef.. obj =e= w;
minconstraint.. w =e= min(x, y, z);

Model nlp_model /all/;
x.lo = 0; y.lo = 0; z.lo = 0;
Solve nlp_model using NLP minimizing obj;
```

**Expected Solution:**
- x = 0, y = 0, z = 0, w = 0
- All at lower bounds

---

## MCP Reformulation

```gams
Variables x, y, z, w_min, obj;
Positive Variables lambda_x, lambda_y, lambda_z;

Equations
    stat_x, stat_y, stat_z, stat_w,
    comp_min_x, comp_min_y, comp_min_z,
    objdef;

* Stationarity conditions
stat_x.. -lambda_x =e= 0;
stat_y.. -lambda_y =e= 0;
stat_z.. -lambda_z =e= 0;
stat_w.. 1 - lambda_x - lambda_y - lambda_z =e= 0;

* Complementarity constraints (w_min <= each argument)
comp_min_x.. x - w_min =g= 0;
comp_min_y.. y - w_min =g= 0;
comp_min_z.. z - w_min =g= 0;

objdef.. obj =e= w_min;

Model mcp_model / 
    stat_x.x,
    stat_y.y,
    stat_z.z,
    stat_w.w_min,
    comp_min_x.lambda_x,
    comp_min_y.lambda_y,
    comp_min_z.lambda_z,
    objdef.obj /;

x.lo = 0; y.lo = 0; z.lo = 0;

Solve mcp_model using MCP;
```

---

## General Pattern for N Arguments

For `w = min(x1, x2, ..., xN)`:

### Variables
- Auxiliary: `w_min`
- Multipliers: `lambda_1, lambda_2, ..., lambda_N` (all positive)

### Equations

**Stationarity for each xi:**
```
∂L/∂xi + ... - lambda_i = 0
```

**Stationarity for w_min:**
```
∂obj/∂w_min - Σ(lambda_i) = 0

For minimizing w_min:
  1 - lambda_1 - lambda_2 - ... - lambda_N = 0
  
Therefore: Σ(lambda_i) = 1
```

**Complementarity constraints:**
```
xi - w_min >= 0  ⊥  lambda_i >= 0    for each i
```

### Key Properties

1. **Sum of multipliers:** `Σ(lambda_i) = 1`
2. **At least one active:** At optimum, at least one `xi = w_min`
3. **Active multipliers:** If `xi = w_min`, then `lambda_i > 0` is allowed
4. **Inactive multipliers:** If `xi > w_min`, then `lambda_i = 0` (complementarity)

---

## Example with Specific Values

### Problem
```
minimize w
subject to: w = min(4, 2, 6, 3)
```

### Expected Solution
- w = 2 (the minimum)
- lambda_2 > 0 (active constraint)
- lambda_1 = lambda_3 = lambda_4 = 0 (slack)

### Verification

**Stationarity:**
```
1 - lambda_1 - lambda_2 - lambda_3 - lambda_4 = 0
1 - 0 - lambda_2 - 0 - 0 = 0
lambda_2 = 1 ✓
```

**Complementarity:**
```
4 - 2 = 2 > 0  ⊥  lambda_1 = 0  →  2*0 = 0 ✓
2 - 2 = 0 = 0  ⊥  lambda_2 = 1  →  0*1 = 0 ✓
6 - 2 = 4 > 0  ⊥  lambda_3 = 0  →  4*0 = 0 ✓
3 - 2 = 1 > 0  ⊥  lambda_4 = 0  →  1*0 = 0 ✓
```

All conditions satisfied ✓

---

## Efficiency Note

For N arguments:
- **Variables added:** 1 auxiliary + N multipliers = N+1 variables
- **Constraints added:** 1 stationarity + N complementarities = N+1 equations

**Scaling:**
- 2 arguments: 3 variables, 3 equations
- 3 arguments: 4 variables, 4 equations
- 10 arguments: 11 variables, 11 equations

The reformulation scales linearly with the number of arguments, which is acceptable.

---

## Implementation Pseudocode

```python
def reformulate_min(min_expr, context):
    """
    Reformulate min(arg1, arg2, ..., argN) for MCP.
    
    Args:
        min_expr: AST node for min() call
        context: Equation/expression context for naming
    
    Returns:
        aux_var: Name of auxiliary variable
        constraints: List of complementarity constraints
        multipliers: List of multiplier variables
    """
    args = min_expr.arguments
    n = len(args)
    
    # Generate names
    aux_var = f"w_min_{context}"
    multipliers = [f"lambda_min_{context}_{i}" for i in range(n)]
    
    # Create inequality constraints: arg_i - aux_var >= 0
    constraints = []
    for i, arg in enumerate(args):
        constraint = {
            'lhs': subtract(arg, VarRef(aux_var)),
            'relation': '>=',
            'rhs': Constant(0),
            'multiplier': multipliers[i]
        }
        constraints.append(constraint)
    
    # Create stationarity for aux_var
    # gradient - sum(multipliers) = 0
    stationarity = {
        'lhs': gradient_term(aux_var),
        'rhs': sum(VarRef(m) for m in multipliers)
    }
    
    return {
        'aux_var': aux_var,
        'constraints': constraints,
        'stationarity': stationarity,
        'multipliers': multipliers
    }
```
