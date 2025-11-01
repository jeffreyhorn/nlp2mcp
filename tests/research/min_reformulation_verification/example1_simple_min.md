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

x >= z_min    ... (inequality 1)
y >= z_min    ... (inequality 2)

with complementarity:
  (x - z_min) ⊥ λ_x, λ_x >= 0
  (y - z_min) ⊥ λ_y, λ_y >= 0
```

### Step 2: KKT Conditions

**Original Lagrangian:**
```
L = z + μ_x*(-x) + μ_y*(-y) + ν*(z - min(x,y))
```

**After reformulation:**
```
L = z_min + μ_x*(-x) + μ_y*(-y) + λ_x*(x-z_min) + λ_y*(y-z_min)
```

**Stationarity Conditions:**
```
∂L/∂x = 0:      -μ_x + λ_x = 0  →  λ_x = μ_x
∂L/∂y = 0:      -μ_y + λ_y = 0  →  λ_y = μ_y
∂L/∂z_min = 0:   1 - λ_x - λ_y = 0
```

**Complementarity Conditions:**
```
x >= 0  ⊥  μ_x >= 0        (bound on x)
y >= 0  ⊥  μ_y >= 0        (bound on y)
x - z_min >= 0  ⊥  λ_x >= 0    (min constraint 1)
y - z_min >= 0  ⊥  λ_y >= 0    (min constraint 2)
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
stat_x.. lambda_x =e= 0;         * ∂L/∂x = -μ_x + λ_x = 0 (x at bound, μ_x = 0)
stat_y.. lambda_y =e= 0;         * ∂L/∂y = -μ_y + λ_y = 0 (y at bound, μ_y = 0)
stat_z.. 1 - lambda_x - lambda_y =e= 0;  * ∂L/∂z_min = 1 - λ_x - λ_y = 0

* Complementarity constraints (write as g(z) >= 0)
comp_min_x.. x - z_min =g= 0;    * Paired with lambda_x
comp_min_y.. y - z_min =g= 0;    * Paired with lambda_y

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
   - Bound handled automatically by GAMS (x.lo = 0)

2. **Bound on y:**
   - y = 0 (at bound)
   - Bound handled automatically by GAMS (y.lo = 0)

3. **Min constraint 1 (x >= z_min):**
   - x - z_min = 0 - 0 = 0 (tight)
   - Can have λ_x > 0 (active)
   - Complementarity: 0 * λ_x = 0 ✓

4. **Min constraint 2 (y >= z_min):**
   - y - z_min = 0 - 0 = 0 (tight)
   - Can have λ_y > 0 (active)
   - Complementarity: 0 * λ_y = 0 ✓

**Check stationarity:**

From stat_z: `1 - λ_x - λ_y = 0`
Therefore: `λ_x + λ_y = 1`

This makes sense! At optimum:
- λ_x + λ_y = 1 ✓
- Both λ_x, λ_y >= 0 ✓
- Both constraints are tight (degenerate case since x = y)
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
