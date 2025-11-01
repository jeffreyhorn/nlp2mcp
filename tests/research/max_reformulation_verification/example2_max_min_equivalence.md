# Example 2: Max-Min Equivalence Verification

## Mathematical Duality

The fundamental relationship between max and min:

```
max(x, y) = -min(-x, -y)
```

This example verifies this equivalence both mathematically and in MCP reformulation.

## Proof of Equivalence

### Forward Direction: max(x,y) = -min(-x,-y)

**Case 1:** x > y

Left side:
```
max(x, y) = x
```

Right side:
```
-min(-x, -y) = -min(-x, -y)
Since -x < -y (because x > y), we have min(-x, -y) = -x
Therefore: -min(-x, -y) = -(-x) = x
```

Both sides equal x ✓

**Case 2:** y > x

Left side:
```
max(x, y) = y
```

Right side:
```
-min(-x, -y) = -min(-x, -y)
Since -y < -x (because y > x), we have min(-x, -y) = -y
Therefore: -min(-x, -y) = -(-y) = y
```

Both sides equal y ✓

**Case 3:** x = y

Left side:
```
max(x, y) = x = y
```

Right side:
```
-min(-x, -y) = -min(-x, -x) = -(-x) = x = y
```

Both sides equal x = y ✓

## Numerical Verification

### Test 1: max(3, 5) vs -min(-3, -5)

**Direct max:**
```
max(3, 5) = 5
```

**Via min:**
```
-min(-3, -5) = -min(-3, -5)
              = -(-5)  [since -5 < -3]
              = 5
```

**Result:** 5 = 5 ✓

### Test 2: max(7, 2) vs -min(-7, -2)

**Direct max:**
```
max(7, 2) = 7
```

**Via min:**
```
-min(-7, -2) = -min(-7, -2)
              = -(-7)  [since -7 < -2]
              = 7
```

**Result:** 7 = 7 ✓

### Test 3: max(-3, -8) vs -min(3, 8)

**Direct max:**
```
max(-3, -8) = -3
```

**Via min:**
```
-min(-(-3), -(-8)) = -min(3, 8)
                    = -(3)  [since 3 < 8]
                    = -3
```

**Result:** -3 = -3 ✓

## MCP Reformulation Comparison

### Option A: Direct Max Reformulation

```gams
Variables z_max;
Positive Variables lambda_max_x, lambda_max_y;

Equations
    stat_z_max,
    comp_max_x, comp_max_y;

* Stationarity
stat_z_max.. 1 - lambda_max_x - lambda_max_y =e= 0;

* Complementarity constraints (x - z <= 0, y - z <= 0)
comp_max_x.. x - z_max =l= 0;
comp_max_y.. y - z_max =l= 0;

Model max_direct /
    stat_z_max,
    comp_max_x.lambda_max_x,
    comp_max_y.lambda_max_y
/;
```

**Variable count:** 3 (z_max, lambda_max_x, lambda_max_y)  
**Equation count:** 3 (1 stationarity + 2 complementarity)

### Option B: Max via -Min(-x,-y)

```gams
* First negate the arguments
Parameters neg_x, neg_y;
neg_x = -x;
neg_y = -y;

* Apply min reformulation
Variables z_min;
Positive Variables lambda_min_x, lambda_min_y;

Equations
    stat_z_min,
    comp_min_x, comp_min_y;

* Stationarity for min
stat_z_min.. -1 + lambda_min_x + lambda_min_y =e= 0;

* Complementarity constraints (neg_x - z_min >= 0, neg_y - z_min >= 0)
comp_min_x.. neg_x - z_min =g= 0;
comp_min_y.. neg_y - z_min =g= 0;

* Final result: negate z_min
Variables z_max;
Equation define_max;
define_max.. z_max =e= -z_min;

Model max_via_min /
    stat_z_min,
    comp_min_x.lambda_min_x,
    comp_min_y.lambda_min_y,
    define_max
/;
```

**Variable count:** 4 (z_min, z_max, lambda_min_x, lambda_min_y)  
**Equation count:** 4 (1 min stationarity + 2 min complementarity + 1 definition)

### Comparison Table

| Aspect | Direct Max | Via -Min(-x,-y) |
|--------|------------|-----------------|
| **Variables** | 3 | 4 |
| **Equations** | 3 | 4 |
| **Negations** | 0 | 3 (2 args + 1 result) |
| **Clarity** | High | Lower |
| **Efficiency** | Better | Worse |
| **Correctness** | ✓ | ✓ (but more complex) |

## Why Direct Max is Preferred

### Reason 1: Fewer Variables and Equations

Direct max uses n+1 variables and equations, while max-via-min uses 2n+2.

### Reason 2: Fewer Operations

Direct max avoids:
- Negating input arguments
- Negating final result
- Extra auxiliary variable for z_min

### Reason 3: Clearer Generated Code

**Direct max output:**
```gams
comp_max_x.. x - z_max =l= 0;
```

**Via min output:**
```gams
neg_x = -x;
comp_min_x.. neg_x - z_min =g= 0;
z_max = -z_min;
```

### Reason 4: Symmetric to Min Implementation

Having separate implementations for min and max maintains code clarity:
```python
def reformulate_min(args): ...  # Uses =g= constraints
def reformulate_max(args): ...  # Uses =l= constraints
```

Rather than:
```python
def reformulate_min(args): ...
def reformulate_max(args):
    # Negate, call min, negate again
    return -reformulate_min([-arg for arg in args])
```

## Mathematical Verification in MCP Context

### Verifying λ Multipliers

For max(x, y) where x = 3, y = 5:

**Direct Max:**
```
z_max = 5
λ_max_x = 0 (x < z, constraint not binding)
λ_max_y = 1 (y = z, constraint binding)
λ_max_x + λ_max_y = 1 ✓
```

**Via -Min(-x,-y):**
```
neg_x = -3, neg_y = -5
z_min = -5 (since min(-3, -5) = -5)
λ_min_x = 0 (neg_x > z_min, constraint not binding)
λ_min_y = 1 (neg_y = z_min, constraint binding)
z_max = -z_min = -(-5) = 5 ✓
```

The multiplier patterns match, confirming equivalence.

## Implementation Recommendation

**Use direct max reformulation (Option A)** because:

1. ✅ **Simpler:** Fewer variables and equations
2. ✅ **Faster:** No extra negation operations
3. ✅ **Clearer:** Generated GAMS code is more readable
4. ✅ **Maintainable:** Symmetric to min implementation
5. ✅ **Efficient:** Better for PATH solver

The max-via-min equivalence is mathematically correct but computationally inefficient.

## Pseudocode for Both Approaches

### Option A: Direct Max (Recommended)

```python
def reformulate_max(args, context):
    """Direct max reformulation."""
    aux_name = f"aux_max_{context}"
    constraints = []
    
    for i, arg in enumerate(args):
        # arg - aux <= 0  (i.e., aux >= arg)
        constraints.append(Constraint(
            lhs=BinaryOp('-', arg, VarRef(aux_name)),
            operator='<=',
            multiplier=f"lambda_{aux_name}_{i}"
        ))
    
    return aux_name, constraints
```

### Option B: Max via Min (Not Recommended)

```python
def reformulate_max_via_min(args, context):
    """Max via -min(-args) - less efficient."""
    # Negate all arguments
    neg_args = [UnaryOp('-', arg) for arg in args]
    
    # Call min reformulation
    min_name, constraints = reformulate_min(neg_args, context + "_negmin")
    
    # Negate result
    max_name = f"aux_max_{context}"
    definition = Equation(
        lhs=VarRef(max_name),
        rhs=UnaryOp('-', VarRef(min_name))
    )
    
    return max_name, constraints + [definition]
```

## Summary

While `max(x,y) = -min(-x,-y)` is mathematically correct and provides useful theoretical insight into the duality between max and min, **direct implementation of max is strongly preferred** for:

- Computational efficiency
- Code clarity  
- Fewer auxiliary variables
- Simpler MCP formulation
- Better maintainability

The equivalence verification confirms our understanding of the max-min duality but guides us toward implementing max directly rather than via min.
