# Research: min(x,y) Reformulation for MCP

## Executive Summary

This document analyzes how `z = min(x,y)` should be reformulated for Mixed Complementarity Problems (MCP) to be solved with PATH solver.

**Key Finding:** The epigraph reformulation using complementarity conditions is the standard and correct approach for MCP.

---

## Mathematical Background

### The Problem

The function `z = min(x, y)` is **non-smooth** (non-differentiable) at the point `x = y`. This creates problems for:
- Gradient-based optimization
- KKT condition formulation
- Standard NLP solvers

### Why Reformulation is Needed

In an NLP problem like:
```
minimize f(z)
subject to: z = min(x, y)
```

We cannot directly differentiate `z = min(x,y)` to form KKT conditions. We need a smooth reformulation that:
1. Preserves the mathematical equivalence
2. Can be expressed as complementarity conditions
3. Works with PATH solver

---

## Standard MCP Reformulation: Epigraph Form

### Core Idea

The epigraph of `min(x,y)` is the set of points `(x,y,z)` where `z >= min(x,y)`. At the minimum, `z = min(x,y)`.

### Reformulation

**Original:**
```
z = min(x, y)
```

**Reformulated:**
```
z <= x    (constraint 1)
z <= y    (constraint 2)

with complementarity:
  (z - x) ⊥ λ_x    where λ_x >= 0
  (z - y) ⊥ λ_y    where λ_y >= 0
```

**Meaning:**
- `⊥` means "perpendicular" or "complementary": `(z-x) * λ_x = 0`
- At least one constraint must be tight (active)
- The complementarity ensures `z` equals the minimum

### Why This Works

**Case 1: x < y**
- `z = x` (the minimum)
- Constraint 1 is tight: `z - x = 0` → `λ_x` can be > 0 (active)
- Constraint 2 has slack: `z - y < 0` → `λ_y = 0` (inactive)
- Complementarity satisfied: `(z-x)*λ_x = 0*λ_x = 0` ✓
- Complementarity satisfied: `(z-y)*λ_y = (negative)*0 = 0` ✓

**Case 2: y < x**
- `z = y` (the minimum)
- Constraint 2 is tight: `z - y = 0` → `λ_y` can be > 0 (active)
- Constraint 1 has slack: `z - x < 0` → `λ_x = 0` (inactive)
- Complementarity satisfied ✓

**Case 3: x = y**
- `z = x = y` (both equal)
- Both constraints tight: `z - x = 0` and `z - y = 0`
- Both `λ_x` and `λ_y` can be > 0
- The sum `λ_x + λ_y` carries the gradient information
- Complementarity satisfied ✓

---

## Complete MCP Formulation Example

### Original NLP Problem

```gams
Variables x, y, z, obj;
x.lo = 0; y.lo = 0;

Equations objdef, minconstraint;

objdef.. obj =e= z;
minconstraint.. z =e= min(x, y);

Model nlp_model /all/;
Solve nlp_model using NLP minimizing obj;
```

### Reformulated as MCP

```gams
Variables x, y, z_min, obj;
Positive Variables lambda_min_x, lambda_min_y;

Equations
    stationarity_x,     * KKT for x
    stationarity_y,     * KKT for y
    stationarity_z,     * KKT for z_min
    stationarity_obj,   * KKT for obj
    comp_min_x,         * Complementarity for z <= x
    comp_min_y,         * Complementarity for z <= y
    objdef;             * Objective definition

* Stationarity conditions (gradient = 0)
stationarity_x.. lambda_min_x =e= 0;
stationarity_y.. lambda_min_y =e= 0;
stationarity_z.. -1 + lambda_min_x + lambda_min_y =e= 0;
stationarity_obj.. 1 =e= 0;  * (This would be adjusted for real objective)

* Complementarity constraints (z - x <= 0, z - y <= 0)
comp_min_x.. z_min - x =l= 0;
comp_min_y.. z_min - y =l= 0;

* Original objective definition
objdef.. obj =e= z_min;

Model mcp_model / 
    stationarity_x.x,
    stationarity_y.y, 
    stationarity_z.z_min,
    stationarity_obj.obj,
    comp_min_x.lambda_min_x,
    comp_min_y.lambda_min_y,
    objdef.obj /;

Solve mcp_model using MCP;
```

**Key Points:**
1. Auxiliary variable `z_min` replaces `z`
2. Multipliers `lambda_min_x` and `lambda_min_y` are positive variables
3. Stationarity conditions capture gradient information
4. Complementarity pairs: `(comp_min_x, lambda_min_x)` and `(comp_min_y, lambda_min_y)`

---

## Multi-Argument Case: min(x, y, z)

### Reformulation

**Original:**
```
w = min(x, y, z)
```

**Reformulated:**
```
w <= x    with (w - x) ⊥ λ_x, λ_x >= 0
w <= y    with (w - y) ⊥ λ_y, λ_y >= 0
w <= z    with (w - z) ⊥ λ_z, λ_z >= 0
```

**General Pattern:**
For `w = min(x1, x2, ..., xn)`:
- Create n constraints: `w <= xi` for each i
- Create n complementarity pairs: `(w - xi) ⊥ λ_i`
- All multipliers `λ_i >= 0`

**At solution:**
- At least one constraint must be tight
- The tightest constraint(s) have active multipliers
- All slack constraints have zero multipliers

---

## Nested Min: min(min(x,y), z)

### Two Approaches

**Approach 1: Nested Reformulation**
```
Let w1 = min(x, y)
Let w2 = min(w1, z)

Reformulate each separately:
  w1 <= x  with (w1-x) ⊥ λ1_x
  w1 <= y  with (w1-y) ⊥ λ1_y
  w2 <= w1 with (w2-w1) ⊥ λ2_w1
  w2 <= z  with (w2-z) ⊥ λ2_z
```

**Approach 2: Flattening (Simpler)**
```
Recognize that min(min(x,y), z) = min(x, y, z)

Flatten to single min with 3 arguments:
  w <= x  with (w-x) ⊥ λ_x
  w <= y  with (w-y) ⊥ λ_y
  w <= z  with (w-z) ⊥ λ_z
```

**Recommendation:** Use Approach 2 (flattening) as it:
- Results in fewer variables
- Is simpler to implement
- Is mathematically equivalent
- Is easier for PATH solver

---

## Alternative: Smooth Approximation

### LogSumExp Smoothing

```
min(x, y) ≈ -(1/α) * log(exp(-α*x) + exp(-α*y))
```

**Properties:**
- Smooth (differentiable everywhere)
- Converges to true min as α → ∞
- Can use standard NLP solvers

**Tradeoffs:**
- **Pros:** No reformulation needed, works with standard NLP
- **Cons:** 
  - Approximation error (not exact)
  - Numerical issues for large α
  - Slower convergence
  - Requires tuning α

**When to Use:**
- Prototyping/quick solutions
- When exact min not critical
- When MCP reformulation too complex

**For nlp2mcp:**
- Primary approach should be MCP reformulation (exact)
- Could offer `--smooth-min <alpha>` flag as option

---

## Comparison with Literature

### Standard References

1. **Ferris & Pang (1997)** - "Engineering and Economic Applications of Complementarity Problems"
   - Confirms epigraph reformulation
   - Used in economic equilibrium models

2. **Luo, Pang & Ralph (1996)** - "Mathematical Programs with Equilibrium Constraints (MPEC)"
   - Discusses smooth vs. non-smooth reformulations
   - Covers min/max in MPEC context

3. **GAMS/PATH Documentation**
   - PATH solver designed for MCP
   - Handles complementarity pairs naturally
   - Standard approach in GAMS community

### Industry Practice

The epigraph reformulation with complementarity is the **standard** approach for:
- Economic equilibrium models
- Bilevel optimization
- Game theory applications
- Engineering design with discrete choices

---

## Verification Tests

### Test 1: Simple Two-Argument Min

**Problem:**
```
minimize z
subject to: z = min(3, 5)
```

**Expected Solution:**
- `z = 3`
- `λ_x > 0` (constraint `z <= 3` is active)
- `λ_y = 0` (constraint `z <= 5` has slack)

### Test 2: Three-Argument Min

**Problem:**
```
minimize w
subject to: w = min(4, 2, 6)
```

**Expected Solution:**
- `w = 2`
- `λ_y > 0` (active)
- `λ_x = 0`, `λ_z = 0` (slack)

### Test 3: Min in Objective

**Problem:**
```
minimize x + y + min(x, y)
subject to: x >= 1, y >= 1
```

**Expected Solution:**
- Both x and y should equal 1 (boundary)
- `min(x,y) = 1`
- Objective value = 1 + 1 + 1 = 3

---

## Implementation Recommendations

### For nlp2mcp Tool

1. **Detection Phase:**
   - Scan AST for `min()` function calls
   - Record location and arguments

2. **Reformulation Phase:**
   - Create auxiliary variable for each `min()` expression
   - Generate inequality constraints (`z <= xi` for each argument)
   - Create positive multiplier variables (`λ_i`)

3. **KKT Assembly Phase:**
   - Add stationarity conditions for auxiliary variables
   - Add complementarity pairs to MCP model
   - Update references to use auxiliary variables

4. **Naming Convention:**
   ```
   Original: z = min(x, y) in equation eq5
   Auxiliary var: z_min_eq5
   Multipliers: lambda_min_eq5_x, lambda_min_eq5_y
   ```

5. **Edge Cases to Handle:**
   - `min()` with constants: `min(x, 5)` → still reformulate
   - `min()` in nested expressions: `x + min(y, z)`
   - Multiple `min()` in same equation

### Error Handling

1. **Single-argument min:**
   ```
   min(x) → Warning: "min() with single argument is identity"
   → Replace with x directly
   ```

2. **No arguments:**
   ```
   min() → Error: "min() requires at least one argument"
   ```

3. **Non-numeric arguments:**
   ```
   min(set_element) → Error: "min() arguments must be numeric"
   ```

---

## Conclusions

### Key Findings

1. ✅ **Epigraph reformulation is correct** for MCP
2. ✅ **Works for multi-argument min** (n >= 2 arguments)
3. ✅ **Nested min should be flattened** for simplicity
4. ✅ **Smooth approximation is alternative** but not preferred
5. ✅ **Standard in literature** and industry practice

### Recommendations for Sprint 4

**Priority 1: Basic Implementation**
- Implement epigraph reformulation for 2-argument `min(x, y)`
- Generate auxiliary variables and constraints
- Add complementarity pairs to MCP formulation

**Priority 2: Extensions**
- Support multi-argument `min(x1, x2, ..., xn)`
- Flatten nested `min()` expressions

**Priority 3: Optional Features**
- Add `--smooth-min <alpha>` flag for smooth approximation
- Provide warnings for degenerate cases

**Not Needed for MVP:**
- Nested min without flattening (overly complex)
- Automatic α tuning for smooth approximation

### Mathematical Correctness

The epigraph reformulation is:
- ✅ **Mathematically equivalent** to original
- ✅ **Preserves optimality** (KKT conditions satisfied)
- ✅ **Compatible with PATH** solver
- ✅ **Standard approach** in complementarity literature

---

## References

1. Ferris, M. C., & Pang, J. S. (1997). Engineering and economic applications of complementarity problems. *SIAM Review*, 39(4), 669-713.

2. Luo, Z. Q., Pang, J. S., & Ralph, D. (1996). *Mathematical programs with equilibrium constraints*. Cambridge University Press.

3. Dirkse, S. P., & Ferris, M. C. (1995). The PATH solver: A non-monotone stabilization scheme for mixed complementarity problems. *Optimization Methods and Software*, 5(2), 123-156.

4. GAMS Documentation. (2024). MCP Model Type. https://www.gams.com/latest/docs/UG_ModelSolve.html#UG_ModelSolve_ModelTypes_MCP

5. Cottle, R. W., Pang, J. S., & Stone, R. E. (2009). *The linear complementarity problem*. SIAM.
