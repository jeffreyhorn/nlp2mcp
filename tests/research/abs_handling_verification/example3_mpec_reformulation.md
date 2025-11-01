# Example 3: MPEC Reformulation for Absolute Value

## Overview

This example explores the Mathematical Program with Equilibrium Constraints (MPEC) approach to reformulating `abs(x)` exactly without approximation.

## Mathematical Formulation

### Decomposition into Positive and Negative Parts

Any real number x can be decomposed as:
```
x = x⁺ - x⁻
```

where:
- x⁺ = max(x, 0) (positive part)
- x⁻ = max(-x, 0) (negative part)
- x⁺ ≥ 0, x⁻ ≥ 0
- x⁺ · x⁻ = 0 (complementarity: at most one is non-zero)

### Absolute Value Expression

```
|x| = x⁺ + x⁻
```

**Verification:**
- If x > 0: x⁺ = x, x⁻ = 0, so |x| = x + 0 = x ✓
- If x < 0: x⁺ = 0, x⁻ = -x, so |x| = 0 + (-x) = -x ✓
- If x = 0: x⁺ = 0, x⁻ = 0, so |x| = 0 + 0 = 0 ✓

### MCP Formulation

**Variables:**
```
x         (original variable, free)
y_abs     (result of |x|)
x_pos     (positive part, >= 0)
x_neg     (negative part, >= 0)
```

**Equations:**
```gams
* Decomposition: x = x_pos - x_neg
eq_decomp.. x =e= x_pos - x_neg;

* Absolute value: y_abs = x_pos + x_neg
eq_abs.. y_abs =e= x_pos + x_neg;

* Complementarity: x_pos ⊥ x_neg
* Implementation option 1: x_pos * x_neg = 0
eq_comp.. x_pos * x_neg =e= 0;

* Implementation option 2: MCP pairs
* x_pos.lambda_pos, x_neg.lambda_neg
* with additional constraints
```

## Worked Example: y = |x|, minimize y

### Problem Setup

```
minimize  y
subject to:
  y = |x|
  -5 <= x <= 5
```

### MPEC Reformulation

```gams
Variables
    x        "original variable"
    y_abs    "result of abs(x)"
    x_pos    "positive part"
    x_neg    "negative part";

Positive Variables x_pos, x_neg;

x.lo = -5;
x.up = 5;

Equations
    eq_decomp   "x = x_pos - x_neg"
    eq_abs      "y_abs = x_pos + x_neg"
    eq_comp     "complementarity";

eq_decomp.. x =e= x_pos - x_neg;
eq_abs.. y_abs =e= x_pos + x_neg;
eq_comp.. x_pos * x_neg =e= 0;

Model abs_mpec / eq_decomp, eq_abs, eq_comp /;
Solve abs_mpec minimizing y_abs using NLP;
```

### Expected Solution

Since we're minimizing y_abs = x_pos + x_neg and x = x_pos - x_neg:
- At optimum: y_abs should be minimized
- This occurs when x = 0 (then x_pos = x_neg = 0, y_abs = 0)

**Optimal solution:**
```
x* = 0
x_pos* = 0
x_neg* = 0
y_abs* = 0
```

### Verification of Solution

1. **Decomposition:** x = x_pos - x_neg = 0 - 0 = 0 ✓
2. **Absolute value:** y_abs = x_pos + x_neg = 0 + 0 = 0 = |0| ✓
3. **Complementarity:** x_pos · x_neg = 0 · 0 = 0 ✓
4. **Optimality:** y_abs = 0 is indeed minimum ✓

## Case Analysis

### Case 1: x = 3 (positive)

**Expected:**
```
x_pos = 3
x_neg = 0
y_abs = 3
```

**Verification:**
- Decomposition: 3 = 3 - 0 ✓
- Absolute value: 3 = 3 + 0 = |3| ✓
- Complementarity: 3 · 0 = 0 ✓

### Case 2: x = -2 (negative)

**Expected:**
```
x_pos = 0
x_neg = 2
y_abs = 2
```

**Verification:**
- Decomposition: -2 = 0 - 2 ✓
- Absolute value: 2 = 0 + 2 = |-2| ✓
- Complementarity: 0 · 2 = 0 ✓

### Case 3: x = 0 (at kink)

**Multiple valid solutions:**

Solution A:
```
x_pos = 0, x_neg = 0, y_abs = 0
```

Solution B:
```
x_pos = t, x_neg = t, y_abs = 2t  (for any t ≥ 0)
```

All satisfy:
- Decomposition: 0 = t - t ✓
- Absolute value: 2t = t + t ✓ (but should be 0!)
- Complementarity: t · t = 0 only if t = 0 ✓

So actually, complementarity forces t = 0, giving unique solution.

## Complementarity Implementation Options

### Option 1: Explicit Product Constraint

```gams
eq_comp.. x_pos * x_neg =e= 0;
```

**Issues:**
- Non-convex constraint
- Difficult for NLP solvers
- May fail to find feasible solution
- Not suitable for PATH (needs smooth reformulation)

### Option 2: MCP with Complementarity Pairs

```gams
Positive Variables lambda_pos, lambda_neg;

Equations
    stat_pos, stat_neg;

* For minimizing objective with abs(x):
* Stationarity conditions link multipliers

stat_pos.. lambda_pos =g= 0;
stat_neg.. lambda_neg =g= 0;

Model abs_mcp /
    eq_decomp,
    eq_abs,
    stat_pos.x_pos,
    stat_neg.x_neg
/;
```

**Issues:**
- Requires embedding abs() reformulation in broader optimization context
- Complex to set up stationarity conditions correctly
- Not standalone reformulation

### Option 3: SOS1 (Special Ordered Set)

```gams
SOS1 Variable sos_abs;
sos_abs.. x_pos, x_neg;
```

Some solvers support SOS1 (at most one variable non-zero), which directly encodes complementarity.

**Issues:**
- Not supported by all solvers
- PATH doesn't directly support SOS1
- Requires MILP solver or special SOS-capable solver

## Complexity Analysis

For a single abs() reformulation:

| Approach | Variables Added | Equations Added | Complementarity Conditions |
|----------|-----------------|-----------------|----------------------------|
| **Smooth approximation** | 0 | 0 | 0 |
| **MPEC** | +2 (x_pos, x_neg) | +2 (decomp, abs) | +1 (x_pos ⊥ x_neg) |

For n occurrences of abs():

| Approach | Total Variables | Total Equations | Complementarity Conditions |
|----------|------------------|------------------|----------------------------|
| **Smooth approximation** | 0 | 0 | 0 |
| **MPEC** | +2n | +2n | +n |

### Scaling Example

Model with 10 abs() occurrences:

**Smooth approximation:**
- No additional structure needed
- Just replace abs(x) with sqrt(x^2 + eps) in place

**MPEC:**
- Add 20 variables (10 x_pos, 10 x_neg)
- Add 20 equations (10 decomposition, 10 abs definition)
- Add 10 complementarity conditions

This significantly increases problem size and complexity.

## PATH Solver Compatibility

PATH is designed for smooth MCPs. The complementarity condition x_pos ⊥ x_neg is non-smooth.

### Reformulation for PATH

The condition x_pos ⊥ x_neg means:
```
x_pos ≥ 0, x_neg ≥ 0
x_pos · x_neg = 0
```

In MCP form:
```
F₁(x_pos) = some_expression_1 ⊥ x_pos ≥ 0
F₂(x_neg) = some_expression_2 ⊥ x_neg ≥ 0
```

But we need F₁ and F₂ such that the solution enforces x_pos · x_neg = 0.

**Challenge:** Without an optimization objective, there's no natural choice for F₁ and F₂ that enforces this.

**Conclusion:** MPEC reformulation of abs() is not naturally compatible with PATH solver for general MCP formulations.

## When MPEC Might Be Useful

### Scenario 1: Mixed-Integer Problems

If using a MILP solver, can introduce binary variable:
```
Variables
    x, y_abs, x_pos, x_neg;
Binary Variable b;

Equations
    decomp, abs_def,
    logic1, logic2;

decomp.. x =e= x_pos - x_neg;
abs_def.. y_abs =e= x_pos + x_neg;

* b = 1 ⟹ x >= 0 ⟹ x_neg = 0
* b = 0 ⟹ x < 0 ⟹ x_pos = 0
logic1.. x_pos =l= M * b;
logic2.. x_neg =l= M * (1 - b);
```

This exactly enforces complementarity, but requires MILP solver.

### Scenario 2: Small Problems

For problems with 1-2 abs() occurrences and local NLP solver (e.g., CONOPT), the product constraint x_pos · x_neg = 0 might be handled.

**But:** Not reliable or scalable.

## Comparison with Smooth Approximation

| Aspect | MPEC | Smooth Approximation |
|--------|------|----------------------|
| **Exactness** | Exact | Approximate (error ≈ √ε) |
| **Variables** | +2 per abs() | 0 |
| **Equations** | +2 per abs() | 0 |
| **Complementarity** | +1 per abs() | 0 |
| **Solver compatibility** | Poor (non-convex) | Excellent (smooth) |
| **Scalability** | Poor | Excellent |
| **Implementation complexity** | High | Low |
| **Numerical stability** | Moderate | Good |

## Recommendation

**For nlp2mcp project:**

❌ **Do NOT implement MPEC reformulation for abs()** because:

1. **Complexity:** Adds 2 variables and 2-3 equations per abs()
2. **Non-convexity:** Product constraint is non-convex
3. **Solver incompatibility:** PATH doesn't naturally handle this
4. **Scaling issues:** Becomes unwieldy with multiple abs()
5. **Implementation burden:** Much more complex than smoothing

✅ **Use smooth approximation instead** because:

1. **Simplicity:** No additional variables or equations
2. **Smoothness:** Compatible with PATH solver
3. **Accuracy:** Error is negligible (< 0.001) for most applications
4. **Scalability:** No overhead regardless of number of abs()
5. **Implementation ease:** Simple expression replacement

### Future Consideration

If there is strong user demand for exact abs() handling:

1. Provide as optional advanced feature (`--exact-abs` flag)
2. Require MILP-capable solver
3. Document limitations and performance implications
4. Recommend smooth approximation as default

## Conclusion

While MPEC reformulation of abs() is theoretically interesting and exact, it is **not practical for the nlp2mcp tool**. The smooth approximation approach is superior in all practical aspects:

- ✅ Simpler implementation
- ✅ Better solver compatibility
- ✅ Better scaling properties
- ✅ Adequate accuracy for real applications
- ✅ No additional variables or constraints

The MPEC approach should be considered only as a future enhancement for specialized use cases requiring exact reformulation with MILP solvers.
