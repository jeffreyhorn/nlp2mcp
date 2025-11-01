# Example 4: Nested Max and Flattening

## Problem Statement

How should nested max expressions like `max(max(x, y), z)` be reformulated for MCP?

## Mathematical Foundation

### Associativity of Max

The max function is associative:
```
max(max(x, y), z) = max(x, y, z)
max(x, max(y, z)) = max(x, y, z)
```

**Proof:**

For any ordering of x, y, z, both sides yield the same result.

**Case 1:** x ≥ y ≥ z
```
max(max(x, y), z) = max(x, z) = x
max(x, y, z) = x
```

**Case 2:** y ≥ x ≥ z
```
max(max(x, y), z) = max(y, z) = y
max(x, y, z) = y
```

**Case 3:** z ≥ x ≥ y
```
max(max(x, y), z) = max(x, z) = z
max(x, y, z) = z
```

All cases: nested and flattened forms are equivalent ✓

## Two Reformulation Approaches

### Approach A: Direct Reformulation (Nested)

Reformulate each max separately, maintaining nesting structure.

**Example:** `result = max(max(x, y), z)`

```gams
* Inner max: aux1 = max(x, y)
Variables aux1_max;
Positive Variables lambda_aux1_x, lambda_aux1_y;

Equations
    stat_aux1,
    comp_aux1_x, comp_aux1_y;

stat_aux1.. 1 - lambda_aux1_x - lambda_aux1_y =e= 0;
comp_aux1_x.. x - aux1_max =l= 0;
comp_aux1_y.. y - aux1_max =l= 0;

* Outer max: result = max(aux1, z)
Variables result_max;
Positive Variables lambda_result_aux1, lambda_result_z;

Equations
    stat_result,
    comp_result_aux1, comp_result_z;

stat_result.. 1 - lambda_result_aux1 - lambda_result_z =e= 0;
comp_result_aux1.. aux1_max - result_max =l= 0;
comp_result_z.. z - result_max =l= 0;

Model nested_max /
    stat_aux1, comp_aux1_x.lambda_aux1_x, comp_aux1_y.lambda_aux1_y,
    stat_result, comp_result_aux1.lambda_result_aux1, comp_result_z.lambda_result_z
/;
```

**Counts:**
- Variables: 6 (aux1_max, result_max, λ₁, λ₂, λ₃, λ₄)
- Equations: 6 (2 stationarity + 4 complementarity)

### Approach B: Flattening (Recommended)

Flatten nested max to single multi-argument max.

**Example:** `result = max(max(x, y), z)` → `result = max(x, y, z)`

```gams
* Flattened: result = max(x, y, z)
Variables result_max;
Positive Variables lambda_x, lambda_y, lambda_z;

Equations
    stat_result,
    comp_max_x, comp_max_y, comp_max_z;

stat_result.. 1 - lambda_x - lambda_y - lambda_z =e= 0;
comp_max_x.. x - result_max =l= 0;
comp_max_y.. y - result_max =l= 0;
comp_max_z.. z - result_max =l= 0;

Model flattened_max /
    stat_result,
    comp_max_x.lambda_x,
    comp_max_y.lambda_y,
    comp_max_z.lambda_z
/;
```

**Counts:**
- Variables: 4 (result_max, λ_x, λ_y, λ_z)
- Equations: 4 (1 stationarity + 3 complementarity)

### Comparison

| Aspect | Nested (A) | Flattened (B) |
|--------|-----------|---------------|
| **Variables** | 6 | 4 |
| **Equations** | 6 | 4 |
| **Auxiliary vars** | 2 (aux1, result) | 1 (result) |
| **Complexity** | Higher | Lower |
| **Clarity** | Lower | Higher |
| **Correctness** | ✓ | ✓ |

**Recommendation:** Use flattening (Approach B)

## Flattening Algorithm

### Recursive Flattening Function

```python
def is_max_call(expr):
    """Type-checking function: returns True if expr is a max() function call."""
    return isinstance(expr, FunctionCall) and expr.name == 'max'

def flatten_max(expr):
    """
    Recursively flatten nested max calls.
    
    Example:
        max(max(x, y), z) -> [x, y, z]
        max(x, max(y, max(z, w))) -> [x, y, z, w]
    
    Args:
        expr: Expression to flatten
        
    Returns:
        List of flattened arguments
    """
    if not is_max_call(expr):
        # Base case: not a max call, return as-is
        return [expr]
    
    # Recursive case: flatten all arguments
    flattened_args = []
    for arg in expr.arguments:
        if is_max_call(arg):
            # Recursively flatten nested max
            flattened_args.extend(flatten_max(arg))
        else:
            # Regular argument, add to list
            flattened_args.append(arg)
    
    return flattened_args
```

### Example Execution

**Input:** `max(max(x, y), max(z, w))`

**Execution trace:**

```
flatten_max(max(max(x, y), max(z, w)))
├─ arg1 = max(x, y) is max_call ✓
│  └─ flatten_max(max(x, y))
│     ├─ arg1 = x, not max_call
│     │  └─ return [x]
│     └─ arg2 = y, not max_call
│        └─ return [y]
│     Result: [x, y]
│
└─ arg2 = max(z, w) is max_call ✓
   └─ flatten_max(max(z, w))
      ├─ arg1 = z, not max_call
      │  └─ return [z]
      └─ arg2 = w, not max_call
         └─ return [w]
      Result: [z, w]

Final result: [x, y] + [z, w] = [x, y, z, w]
```

**Output:** `max(x, y, z, w)`

## Worked Example: max(max(3, 5), 2)

### Direct Evaluation

```
max(max(3, 5), 2) = max(5, 2) = 5
```

### Nested Reformulation

**Inner max:** aux1 = max(3, 5) = 5
- λ₃ = 0, λ₅ = 1

**Outer max:** result = max(aux1, 2) = max(5, 2) = 5
- λ_aux1 = 1, λ₂ = 0

**Result:** 5 ✓

### Flattened Reformulation

**Flattened:** result = max(3, 5, 2) = 5
- λ₃ = 0, λ₅ = 1, λ₂ = 0

**Result:** 5 ✓

**Both approaches give correct answer, but flattened is simpler.**

## Complex Nesting Example

### Three Levels: max(x, max(y, max(z, w)))

**Flattening process:**

```
Original: max(x, max(y, max(z, w)))

Step 1: Identify innermost max
    max(z, w) -> cannot be flattened further

Step 2: Flatten middle level
    max(y, max(z, w)) -> [y, z, w]

Step 3: Flatten outer level
    max(x, [y, z, w]) -> [x, y, z, w]

Result: max(x, y, z, w)
```

**Comparison:**

| Approach | Variables | Equations |
|----------|-----------|-----------|
| **Nested (3 levels)** | 9 | 9 |
| **Flattened** | 5 | 5 |

**Efficiency gain:** ~45% reduction

## Mixed Nesting: max(max(x, y), z, max(w, v))

**Input:** `max(max(x, y), z, max(w, v))`

**Flattening:**

```
flatten_max(max(max(x, y), z, max(w, v)))
├─ arg1 = max(x, y) is max_call
│  └─ flatten -> [x, y]
├─ arg2 = z, not max_call
│  └─ add [z]
└─ arg3 = max(w, v) is max_call
   └─ flatten -> [w, v]

Result: [x, y, z, w, v]
```

**Output:** `max(x, y, z, w, v)`

## Edge Cases

### Constant Arguments in Nested Max

**Example:** `max(max(x, 5), 10)`

**Flattened:** `max(x, 5, 10)`

```gams
Variables result_max;
Positive Variables lambda_x, lambda_c5, lambda_c10;

Equations
    stat_result,
    comp_max_x, comp_max_5, comp_max_10;

stat_result.. 1 - lambda_x - lambda_c5 - lambda_c10 =e= 0;
comp_max_x.. x - result_max =l= 0;
comp_max_5.. 5 - result_max =l= 0;
comp_max_10.. 10 - result_max =l= 0;
```

**If x < 10:** result = 10, λ_c10 = 1, others = 0

### Single Argument After Flattening

**Example:** `max(max(x))` (degenerate)

**Flattened:** `max(x)`

This could be optimized away entirely to just `x`, but for consistency, treat as:

```gams
Variables result_max;
Positive Variable lambda_x;

Equation
    stat_result,
    comp_max_x;

stat_result.. 1 - lambda_x =e= 0;  # Forces lambda_x = 1
comp_max_x.. x - result_max =l= 0;
```

**Optimization opportunity:** Detect single-argument max and replace with identity.

## Implementation Strategy

### Preprocessing Step

Before reformulation, flatten all nested max:

```python
def preprocess_expression(expr):
    """Preprocess expression tree, flattening nested max."""
    if is_max_call(expr):
        # Flatten this max call
        flattened_args = flatten_max(expr)
        # Recursively preprocess each argument
        processed_args = [preprocess_expression(arg) for arg in flattened_args]
        # Return new max with flattened, processed arguments
        return FunctionCall('max', processed_args)
    elif isinstance(expr, BinaryOp):
        # Recurse on binary operators
        left = preprocess_expression(expr.left)
        right = preprocess_expression(expr.right)
        return BinaryOp(expr.op, left, right)
    else:
        # Leaf node, return as-is
        return expr
```

### Reformulation Step

After flattening, reformulate the simplified max:

```python
def reformulate_max_expression(expr, context):
    """Reformulate max expression (assumed already flattened)."""
    if not is_max_call(expr):
        # Not a max, no reformulation needed
        return expr, []
    
    # All arguments are now at the same level (flattened)
    args = expr.arguments
    aux_var, constraints, stationarity = reformulate_max(args, context)
    
    return VarRef(aux_var), constraints + [stationarity]
```

## Benefits of Flattening

1. ✅ **Fewer variables** - eliminates intermediate auxiliary variables
2. ✅ **Fewer equations** - reduces MCP system size
3. ✅ **Simpler code** - cleaner generated GAMS
4. ✅ **Better performance** - PATH solver has smaller problem
5. ✅ **Mathematically equivalent** - no loss of correctness
6. ✅ **Easier debugging** - simpler constraint structure

## Summary

For nested max expressions:

1. **Always flatten** before reformulation
2. **Use recursive algorithm** to handle arbitrary nesting
3. **Treat constants same as variables** in flattened form
4. **Optimize single-argument** max to identity (optional)
5. **Preprocess entire expression tree** to catch all nested max

Flattening provides significant efficiency gains with no downside, making it the clear choice for implementation.
