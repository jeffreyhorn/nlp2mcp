# Example 1: Simple Min Problem

## Original NLP Formulation

```gams
Variables x, y, z, obj;
x.lo = 0; y.lo = 0;

Equations objdef, minconstraint;

objdef.. obj =e= z;
minconstraint.. z =e= min(x, y);

Model nlp_model /all/;
Solve nlp_model using NLP minimizing obj;
```

**Problem:** 
- Minimize z
- Subject to: z = min(x, y)
- x >= 0, y >= 0

**Expected Solution:**
- x = 0, y = 0, z = 0 (all at lower bounds)
- Objective value = 0

---

## MCP Reformulation (Conceptual)

### Step 1: Replace min with auxiliary variable

```
z_min = min(x, y)

becomes:

z_min <= x    ... (inequality 1)
z_min <= y    ... (inequality 2)

with complementarity:
  (z_min - x) ⊥ λ_x, λ_x >= 0
  (z_min - y) ⊥ λ_y, λ_y >= 0
```

### Step 2: KKT Conditions

**Original Lagrangian:**
```
L = z + μ_x*(-x) + μ_y*(-y) + ν*(z - min(x,y))
```

**After reformulation:**
```
L = z_min + μ_x*(-x) + μ_y*(-y) + λ_x*(z_min-x) + λ_y*(z_min-y)
```

**Stationarity Conditions:**
```
∂L/∂x = 0:      -μ_x - λ_x = 0  →  λ_x = -μ_x
∂L/∂y = 0:      -μ_y - λ_y = 0  →  λ_y = -μ_y
∂L/∂z_min = 0:   1 + λ_x + λ_y = 0
```

**Complementarity Conditions:**
```
x >= 0  ⊥  μ_x >= 0        (bound on x)
y >= 0  ⊥  μ_y >= 0        (bound on y)
z_min - x <= 0  ⊥  λ_x >= 0    (min constraint 1)
z_min - y <= 0  ⊥  λ_y >= 0    (min constraint 2)
```

### Step 3: MCP Formulation

```gams
Variables x, y, z_min, obj;
Positive Variables lambda_x, lambda_y;  * Multipliers for min constraints

Equations
    stat_x,          * Stationarity for x
    stat_y,          * Stationarity for y  
    stat_z,          * Stationarity for z_min
    comp_min_x,      * z_min <= x
    comp_min_y,      * z_min <= y
    objdef;          * Objective definition

* Stationarity conditions
stat_x.. -lambda_x =e= 0;        * ∂L/∂x = -λ_x = 0 (since x at bound)
stat_y.. -lambda_y =e= 0;        * ∂L/∂y = -λ_y = 0 (since y at bound)
stat_z.. 1 + lambda_x + lambda_y =e= 0;  * ∂L/∂z_min = 1 + λ_x + λ_y = 0

* Complementarity constraints
comp_min_x.. z_min - x =l= 0;    * Paired with lambda_x
comp_min_y.. z_min - y =l= 0;    * Paired with lambda_y

* Objective
objdef.. obj =e= z_min;

Model mcp_model / 
    stat_x.x,
    stat_y.y,
    stat_z.z_min,
    comp_min_x.lambda_x,
    comp_min_y.lambda_y,
    objdef.obj /;

x.lo = 0;
y.lo = 0;

Solve mcp_model using MCP;
```

---

## Solution Analysis

### At Solution (x=0, y=0, z_min=0)

**Check complementarity conditions:**

1. **Bound on x:**
   - x = 0 (at bound)
   - Can have μ_x > 0 (active)
   - Complementarity: 0 * μ_x = 0 ✓

2. **Bound on y:**
   - y = 0 (at bound)  
   - Can have μ_y > 0 (active)
   - Complementarity: 0 * μ_y = 0 ✓

3. **Min constraint 1 (z_min <= x):**
   - z_min - x = 0 - 0 = 0 (tight)
   - Can have λ_x > 0 (active)
   - Complementarity: 0 * λ_x = 0 ✓

4. **Min constraint 2 (z_min <= y):**
   - z_min - y = 0 - 0 = 0 (tight)
   - Can have λ_y > 0 (active)
   - Complementarity: 0 * λ_y = 0 ✓

**Check stationarity:**

From stat_z: `1 + λ_x + λ_y = 0`
Therefore: `λ_x + λ_y = -1`

Since both λ_x and λ_y must be >= 0, and they sum to -1...
**Wait, this is wrong!** This would require λ_x + λ_y < 0, but they must be positive.

### Correcting the Formulation

The issue is we're minimizing z_min, so the objective gradient ∂obj/∂z_min = +1.

But in the stationarity condition, we need:
```
∂obj/∂z_min + (multiplier terms) = 0
1 - λ_x - λ_y = 0  (note the minus signs!)
```

Wait, let me reconsider the complementarity direction...

The constraints are `z_min <= x` and `z_min <= y`, which can be written as:
```
x - z_min >= 0
y - z_min >= 0
```

With multipliers:
```
(x - z_min) ⊥ λ_x, λ_x >= 0
(y - z_min) ⊥ λ_y, λ_y >= 0
```

Now stationarity for z_min:
```
∂obj/∂z_min + ∂(complementarity)/∂z_min = 0
1 + (-λ_x) + (-λ_y) = 0
1 = λ_x + λ_y
```

This makes sense! At optimum:
- λ_x + λ_y = 1
- Both λ_x, λ_y >= 0
- At least one is positive (enforces the min)

---

## Corrected MCP Formulation

```gams
Variables x, y, z_min, obj;
Positive Variables lambda_x, lambda_y;

Equations
    stat_x, stat_y, stat_z,
    comp_min_x, comp_min_y,
    objdef;

* Stationarity
stat_x.. -lambda_x =e= 0;        
stat_y.. -lambda_y =e= 0;        
stat_z.. 1 - lambda_x - lambda_y =e= 0;  * CORRECTED

* Complementarity (write as g(z) >= 0)
comp_min_x.. x - z_min =g= 0;    * CORRECTED direction
comp_min_y.. y - z_min =g= 0;    * CORRECTED direction

objdef.. obj =e= z_min;

Model mcp_model / 
    stat_x.x,
    stat_y.y,
    stat_z.z_min,
    comp_min_x.lambda_x,
    comp_min_y.lambda_y,
    objdef.obj /;

x.lo = 0;
y.lo = 0;

Solve mcp_model using MCP;
```

**At solution (x=0, y=0, z_min=0):**
- λ_x + λ_y = 1 (from stationarity)
- Both constraints tight: x - z_min = 0, y - z_min = 0
- Multiple solutions possible: (λ_x=1, λ_y=0), (λ_x=0, λ_y=1), (λ_x=0.5, λ_y=0.5), etc.
- All satisfy complementarity ✓

---

## Key Insights

1. **Constraint Direction Matters:**
   - Write as `x - z_min >= 0` (or `x >= z_min`)
   - Not `z_min - x <= 0`
   - Direction affects sign in stationarity condition

2. **Multiplier Sum Property:**
   - At optimal: λ_x + λ_y = |gradient of objective w.r.t. z_min|
   - For minimizing z_min: λ_x + λ_y = 1

3. **Degeneracy at x = y:**
   - When x = y, both constraints are tight
   - Multiple multiplier values satisfy KKT
   - PATH solver will find one valid solution

4. **Bound Constraints:**
   - x.lo = 0 and y.lo = 0 are separate complementarities
   - Handled automatically by GAMS/PATH
   - Don't need explicit stationarity terms for these
