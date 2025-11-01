# Example 2: Min with Constant Values

## Problem Setup

```gams
* Find the minimum of two constants
Variables z, obj;

Equations objdef, minconstraint;

objdef.. obj =e= z;
minconstraint.. z =e= min(3, 5);

Model nlp_model /all/;
Solve nlp_model using NLP minimizing obj;
```

**Expected Solution:**
- z = 3 (the minimum of 3 and 5)
- Objective = 3

---

## MCP Reformulation

When min has constant arguments, we can still use the same reformulation pattern.

```gams
Variables z_min, obj;
Positive Variables lambda_3, lambda_5;

Equations
    stat_z,
    comp_min_3,      * z_min <= 3
    comp_min_5,      * z_min <= 5
    objdef;

* Stationarity for z_min
stat_z.. 1 - lambda_3 - lambda_5 =e= 0;

* Complementarity constraints
comp_min_3.. 3 - z_min =g= 0;    * Slack when z_min < 3
comp_min_5.. 5 - z_min =g= 0;    * Slack when z_min < 5

objdef.. obj =e= z_min;

Model mcp_model / 
    stat_z.z_min,
    comp_min_3.lambda_3,
    comp_min_5.lambda_5,
    objdef.obj /;

Solve mcp_model using MCP;
```

---

## Solution Analysis

### At Solution: z_min = 3

**Complementarity Check:**

1. **Constraint comp_min_3:**
   - 3 - z_min = 3 - 3 = 0 (tight)
   - lambda_3 can be > 0 (active)
   - Complementarity: 0 * lambda_3 = 0 ✓

2. **Constraint comp_min_5:**
   - 5 - z_min = 5 - 3 = 2 > 0 (slack)
   - lambda_5 must be 0 (inactive)
   - Complementarity: 2 * 0 = 0 ✓

**Stationarity Check:**
```
1 - lambda_3 - lambda_5 = 0
1 - lambda_3 - 0 = 0
lambda_3 = 1 ✓
```

**Summary:**
- z_min = 3 ✓
- lambda_3 = 1 (tight constraint)
- lambda_5 = 0 (slack constraint)
- All KKT conditions satisfied ✓

---

## Generalization: Min with Variables and Constants

```gams
* Problem: z = min(x, 5, y)
* where x and y are variables

Variables x, y, z_min, obj;
Positive Variables lambda_x, lambda_const, lambda_y;

Equations
    stat_x, stat_y, stat_z,
    comp_min_x, comp_min_const, comp_min_y,
    objdef;

stat_x.. -lambda_x =e= 0;        * Stationarity for x
stat_y.. -lambda_y =e= 0;        * Stationarity for y  
stat_z.. 1 - lambda_x - lambda_const - lambda_y =e= 0;

comp_min_x.. x - z_min =g= 0;
comp_min_const.. 5 - z_min =g= 0;    * Constant treated same as variable
comp_min_y.. y - z_min =g= 0;

objdef.. obj =e= z_min;
```

**Key Point:** Constants in min() are treated the same as variables in the reformulation. The complementarity conditions handle which constraint is active.

---

## Edge Case: Single Argument

```gams
* z = min(x)  (only one argument)
```

**Reformulation:**
```
z_min <= x
(x - z_min) ⊥ λ_x >= 0

Stationarity: 1 - λ_x = 0  →  λ_x = 1
Constraint: x - z_min >= 0

At solution: z_min = x (tight), λ_x = 1
```

**Conclusion:** Single-argument min is just the identity function. The reformulation works but is unnecessary. **Optimization:** Detect single-argument min and replace with the argument directly.

---

## Implementation Notes

### Constant Handling

When reformulating `min(expr1, expr2, ..., exprN)`:
1. Each argument can be a variable, constant, or expression
2. Create one inequality constraint per argument: `arg_i - z_min >= 0`
3. Create one multiplier per constraint: `λ_i >= 0`
4. Stationarity condition: `gradient_obj - Σλ_i = 0`

### Variable Naming for Constants

For `z = min(x, 5, y)`:
- Auxiliary variable: `z_min`
- Multipliers: `lambda_min_1` (for x), `lambda_min_2` (for constant 5), `lambda_min_3` (for y)

OR more descriptively:
- Multipliers: `lambda_min_x`, `lambda_min_const_5`, `lambda_min_y`

Recommendation: Use descriptive names when possible, fallback to numbered when name collision might occur.
