# Example 4: Nested Min Functions

## Problem: Nested Min

```gams
Variables x, y, z, w, obj;

Equations objdef, minconstraint;

objdef.. obj =e= w;
minconstraint.. w =e= min(min(x, y), z);

Model nlp_model /all/;
Solve nlp_model using NLP minimizing obj;
```

---

## Approach 1: Direct Nested Reformulation

### Step 1: Inner min
```
Let t = min(x, y)

Reformulate:
  t <= x  with (x - t) ⊥ lambda_t_x >= 0
  t <= y  with (y - t) ⊥ lambda_t_y >= 0
```

### Step 2: Outer min
```
Let w = min(t, z)

Reformulate:
  w <= t  with (t - w) ⊥ lambda_w_t >= 0
  w <= z  with (z - w) ⊥ lambda_w_z >= 0
```

### MCP Formulation

```gams
Variables x, y, z, t, w, obj;
Positive Variables 
    lambda_t_x, lambda_t_y,    * Multipliers for inner min
    lambda_w_t, lambda_w_z;    * Multipliers for outer min

Equations
    stat_x, stat_y, stat_z, stat_t, stat_w,
    comp_t_x, comp_t_y,
    comp_w_t, comp_w_z,
    objdef;

* Stationarity for x
stat_x.. -lambda_t_x =e= 0;

* Stationarity for y
stat_y.. -lambda_t_y =e= 0;

* Stationarity for z
stat_z.. -lambda_w_z =e= 0;

* Stationarity for t (intermediate variable)
stat_t.. lambda_t_x + lambda_t_y - lambda_w_t =e= 0;

* Stationarity for w
stat_w.. 1 - lambda_w_t - lambda_w_z =e= 0;

* Complementarity for inner min (t = min(x,y))
comp_t_x.. x - t =g= 0;
comp_t_y.. y - t =g= 0;

* Complementarity for outer min (w = min(t,z))
comp_w_t.. t - w =g= 0;
comp_w_z.. z - w =g= 0;

objdef.. obj =e= w;

Model mcp_model / 
    stat_x.x, stat_y.y, stat_z.z,
    stat_t.t, stat_w.w,
    comp_t_x.lambda_t_x, comp_t_y.lambda_t_y,
    comp_w_t.lambda_w_t, comp_w_z.lambda_w_z,
    objdef.obj /;
```

**Variables:** x, y, z, t, w, obj (6 total)
**Multipliers:** 4 (lambda_t_x, lambda_t_y, lambda_w_t, lambda_w_z)
**Total equations:** 5 stationarity + 4 complementarity + 1 obj = 10

---

## Approach 2: Flattening (Recommended)

### Observation
```
min(min(x, y), z) = min(x, y, z)
```

Nested min can be flattened to single min with all arguments.

### Flattened Reformulation

```gams
Variables x, y, z, w, obj;
Positive Variables lambda_x, lambda_y, lambda_z;

Equations
    stat_x, stat_y, stat_z, stat_w,
    comp_w_x, comp_w_y, comp_w_z,
    objdef;

* Stationarity
stat_x.. -lambda_x =e= 0;
stat_y.. -lambda_y =e= 0;
stat_z.. -lambda_z =e= 0;
stat_w.. 1 - lambda_x - lambda_y - lambda_z =e= 0;

* Complementarity (w = min(x, y, z))
comp_w_x.. x - w =g= 0;
comp_w_y.. y - w =g= 0;
comp_w_z.. z - w =g= 0;

objdef.. obj =e= w;

Model mcp_model / 
    stat_x.x, stat_y.y, stat_z.z, stat_w.w,
    comp_w_x.lambda_x, comp_w_y.lambda_y, comp_w_z.lambda_z,
    objdef.obj /;
```

**Variables:** x, y, z, w, obj (5 total)
**Multipliers:** 3 (lambda_x, lambda_y, lambda_z)
**Total equations:** 4 stationarity + 3 complementarity + 1 obj = 8

### Comparison

| Approach | Variables | Equations | Complexity |
|----------|-----------|-----------|------------|
| Nested   | 6 + 4 mult = 10 | 10 | High |
| Flattened | 5 + 3 mult = 8 | 8 | Low |

**Winner:** Flattening is simpler, more efficient, and mathematically equivalent.

---

## General Flattening Algorithm

### Pattern Recognition

**Nested min patterns that can be flattened:**
```
min(min(a, b), c)           → min(a, b, c)
min(a, min(b, c))           → min(a, b, c)
min(min(a, b), min(c, d))   → min(a, b, c, d)
min(a, min(b, min(c, d)))   → min(a, b, c, d)
```

### Algorithm

```python
def flatten_min(expr):
    """
    Recursively flatten nested min() calls.
    
    Returns list of all non-min arguments.
    """
    if expr.type != 'Call' or expr.func_name != 'min':
        return [expr]
    
    flattened_args = []
    for arg in expr.arguments:
        if is_min_call(arg):
            # Recursively flatten nested min
            flattened_args.extend(flatten_min(arg))
        else:
            # Regular argument
            flattened_args.append(arg)
    
    return flattened_args

def reformulate_nested_min(expr, context):
    """
    Reformulate potentially nested min for MCP.
    
    Step 1: Flatten all nested min calls
    Step 2: Apply standard multi-argument reformulation
    """
    # Flatten
    all_args = flatten_min(expr)
    
    # Create synthetic min with flattened args
    flattened_min = MinCall(arguments=all_args)
    
    # Apply standard reformulation
    return reformulate_min(flattened_min, context)
```

### Example Execution

**Input:**
```python
expr = min(min(x, y), z)
```

**Step 1: Flatten**
```python
flatten_min(expr) = [x, y, z]
```

**Step 2: Reformulate**
```python
reformulate_min(min(x, y, z), "eq1")
→ Creates: w_min_eq1, lambda_min_eq1_0, lambda_min_eq1_1, lambda_min_eq1_2
→ Constraints: x >= w, y >= w, z >= w with complementarity
```

---

## Complex Nested Example

### Problem
```
w = min(min(x, min(y, z)), min(a, b))
```

### Flattening Process

**Step 1:** Identify innermost min
```
min(y, z) → temp1
Expression becomes: min(min(x, temp1), min(a, b))
```

**Step 2:** Flatten recursively
```
min(x, temp1) → [x, y, z]
min(a, b) → [a, b]
Outer min → [x, y, z, a, b]
```

**Result:**
```
w = min(x, y, z, a, b)
```

### Reformulation
```gams
Variables x, y, z, a, b, w, obj;
Positive Variables lambda_x, lambda_y, lambda_z, lambda_a, lambda_b;

Equations
    stat_x, stat_y, stat_z, stat_a, stat_b, stat_w,
    comp_w_x, comp_w_y, comp_w_z, comp_w_a, comp_w_b,
    objdef;

* Stationarity (one for each variable)
stat_x.. -lambda_x =e= 0;
stat_y.. -lambda_y =e= 0;
stat_z.. -lambda_z =e= 0;
stat_a.. -lambda_a =e= 0;
stat_b.. -lambda_b =e= 0;
stat_w.. 1 - lambda_x - lambda_y - lambda_z - lambda_a - lambda_b =e= 0;

* Complementarity
comp_w_x.. x - w =g= 0;
comp_w_y.. y - w =g= 0;
comp_w_z.. z - w =g= 0;
comp_w_a.. a - w =g= 0;
comp_w_b.. b - w =g= 0;

objdef.. obj =e= w;
```

**Efficiency:** 5 arguments → 6 variables + 6 equations (linear scaling)

---

## Implementation Recommendations

### Priority 1: Implement Flattening
```python
# Preprocessing step before reformulation
def preprocess_min_expressions(ast):
    """
    Find all min() calls in AST and flatten them.
    """
    for node in ast.walk():
        if node.type == 'Call' and node.func_name == 'min':
            # Flatten recursively
            flattened_args = flatten_min(node)
            # Replace node with flattened version
            node.arguments = flattened_args
```

### Priority 2: Direct Reformulation
```python
# After flattening, reformulate as multi-argument min
def reformulate_all_min(ast):
    """
    Reformulate all min() calls to MCP form.
    """
    for node in ast.walk():
        if node.type == 'Call' and node.func_name == 'min':
            # Already flattened, just reformulate
            reformulation = reformulate_min(node, context)
            # Add to MCP model
            add_reformulation(reformulation)
```

### Error Handling

**Case 1: Deeply nested min**
```python
# Before: min(min(min(min(x, y), z), a), b)
# After flattening: min(x, y, z, a, b)
# Warning: "Flattened deeply nested min (depth=4) to 5 arguments"
```

**Case 2: Mixed with max**
```python
# min(max(x, y), z)
# Cannot flatten (different operators)
# Must use nested reformulation or reject
# Recommendation: Reject for MVP, document as limitation
```

---

## Conclusion

**Recommendation for nlp2mcp:**
1. ✅ Implement flattening for nested min
2. ✅ Use single multi-argument reformulation
3. ❌ Don't implement direct nested reformulation (overly complex)
4. ⚠️ Document limitation: Cannot handle min/max mixing

**Benefits of flattening:**
- Simpler implementation
- Fewer variables and equations
- Better solver performance
- Mathematically equivalent
- Easier to debug
