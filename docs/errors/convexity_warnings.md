# Convexity Warnings

This document describes the convexity warnings emitted by nlp2mcp when analyzing GAMS optimization models.

## Overview

nlp2mcp includes heuristic pattern matchers that detect common non-convex structures in optimization problems. These warnings are designed to help users identify potential issues that may cause solvers to find local optima instead of global optima, or may lead to convergence difficulties.

**Important Notes:**
- These are **heuristic warnings**, not definitive proofs of non-convexity
- Some convex problems may trigger warnings (false positives)
- Warnings can be suppressed with `--skip-convexity-check`
- All functionality remains available regardless of warnings

## Warning Categories

All convexity warnings use error codes in the format `W3xx`:
- `W301`: Nonlinear equality constraint
- `W302`: Trigonometric function
- `W303`: Bilinear term
- `W304`: Variable quotient (division by variable)
- `W305`: Odd power

---

## W301: Nonlinear Equality

### Description

Detects nonlinear equality constraints of the form `h(x) = 0` where `h(x)` is a nonlinear function.

### Mathematical Basis

Nonlinear equality constraints typically define non-convex feasible sets, even when the function `h(x)` itself might be convex.

**Example:**
- `x² + y² = 4` defines a circle (non-convex set)
- `x² + y² ≤ 4` defines a disk (convex set)

The equality constraint restricts solutions to the boundary of a level set, which is generally non-convex.

### When This Appears

```gams
Variables x, y;
Equations circle_eq;

circle_eq.. x**2 + y**2 =e= 4;  # Triggers W301
```

### False Positives

Linear equalities like `2*x + 3*y =e= 10` will not trigger this warning (they define convex sets).

### How to Fix

If your problem genuinely requires nonlinear equality:
1. **Verify solver choice**: Use solvers designed for non-convex problems (e.g., BARON, ANTIGONE)
2. **Consider reformulation**: Sometimes equalities can be relaxed to inequalities
3. **Multiple starting points**: Try different initial values to find global optima

If the warning is a false positive:
- Use `--skip-convexity-check` to suppress warnings
- The conversion will proceed normally

---

## W302: Trigonometric Function

### Description

Detects trigonometric functions (sin, cos, tan, arcsin, arccos, arctan) in objectives or constraints.

### Mathematical Basis

Trigonometric functions are neither globally convex nor concave. They are periodic and have multiple local extrema, making global optimization challenging.

### When This Appears

```gams
Variables x, y;
Equations trig_constraint;

trig_constraint.. sin(x) + cos(y) =l= 1;  # Triggers W302
```

### Examples

**Objective function:**
```gams
obj.. z =e= sin(x) * cos(y);  # Triggers W302 in objective
```

**Constraint:**
```gams
eq1.. x + sin(y) =l= 5;  # Triggers W302 in constraint
```

### How to Fix

1. **Verify necessity**: Ensure trigonometric functions are required for your problem
2. **Bounds on variables**: Tight bounds can help solvers by restricting to monotonic regions
3. **Solver selection**: Use global optimization solvers
4. **Linearization**: In some cases, trigonometric functions can be approximated with piecewise linear functions

---

## W303: Bilinear Term

### Description

Detects bilinear terms where two decision variables are multiplied together (e.g., `x * y`).

### Mathematical Basis

Bilinear terms `x * y` are non-convex. They create saddle-shaped surfaces with neither a unique minimum nor maximum.

**Note:** Products like `constant * variable` or `parameter * variable` are linear and will NOT trigger this warning.

### When This Appears

```gams
Variables x, y, z;
Equations bilinear_eq;

bilinear_eq.. x * y + z =e= 10;  # Triggers W303 (x*y is bilinear)
```

### False Positives

```gams
Parameters a;
a = 5;

eq1.. a * x + y =e= 10;  # No warning (a*x is linear)
eq2.. 3 * x * y =e= 10;  # Warning (constant * x * y still has x*y)
```

### How to Fix

**Option 1: McCormick Envelopes (Convex Relaxation)**

For bounded variables, bilinear terms can be relaxed:

```gams
# Original: x * y = w
# If x ∈ [xL, xU], y ∈ [yL, yU], introduce auxiliary variable w:

eq1.. w =g= xL*y + x*yL - xL*yL;
eq2.. w =g= xU*y + x*yU - xU*yU;
eq3.. w =l= xL*y + x*yU - xL*yU;
eq4.. w =l= xU*y + x*yL - xU*yL;
```

**Option 2: Global Solvers**

Use solvers with bilinear capabilities:
- BARON
- ANTIGONE  
- Couenne

**Option 3: Linearization (Special Cases)**

If one variable is binary, bilinear terms can be linearized.

---

## W304: Variable Quotient

### Description

Detects division operations where the denominator contains decision variables (e.g., `x / y`).

### Mathematical Basis

Rational functions with variable denominators are typically non-convex and may cause numerical issues:
1. Division by zero can occur if denominator approaches zero
2. The function `x/y` is neither convex nor concave

**Note:** Expressions like `x / constant` will NOT trigger this warning (they are linear).

### When This Appears

```gams
Variables x, y, z;
Equations quotient_eq;

quotient_eq.. x / y + z =e= 10;  # Triggers W304 (x/y is quotient)
```

### Examples

**Triggers warning:**
```gams
eq1.. x / y =l= 5;           # W304: y is a variable
eq2.. (x + 1) / (y + 2) =e= 3;  # W304: denominator has variable
```

**No warning:**
```gams
Parameters p;
p = 5;

eq3.. x / p =e= 10;          # No warning: p is constant
eq4.. x / 3 =l= 7;           # No warning: 3 is constant
```

### How to Fix

**Option 1: Reformulation**

Multiply both sides by denominator (add nonnegativity constraints):

```gams
# Original: x / y = c
# Reformulated: x = c * y (assuming y > 0)

y.lo = 0.0001;  # Ensure y stays positive
eq_reformulated.. x =e= c * y;
```

**Option 2: Add Safeguards**

Bound denominator away from zero:

```gams
y.lo = 1e-6;  # Prevent division by zero
```

**Option 3: Global Solvers**

Use solvers capable of handling rational functions.

---

## W305: Odd Power

### Description

Detects odd integer powers of variables (x³, x⁵, x⁷, ...) excluding x¹.

### Mathematical Basis

Odd powers are neither globally convex nor concave:
- x³ is convex for x ≥ 0 but concave for x ≤ 0
- This makes global optimization difficult

**Note:** Even powers like x², x⁴ can be convex and will NOT trigger this warning. Linear terms x¹ also do not trigger warnings.

### When This Appears

```gams
Variables x, y;
Equations cubic_eq;

cubic_eq.. x**3 + y**2 =l= 100;  # Triggers W305 (x^3 is odd power)
```

### Examples

**Triggers warning:**
```gams
eq1.. x**3 =l= 50;              # W305: x^3 is odd power
eq2.. x**5 - y**4 =e= 0;        # W305: x^5 is odd power
eq3.. power(x, 3) =l= 10;       # W305: power(x,3) is odd power
eq4.. x**(-3) =g= 1;            # W305: x^-3 is negative odd power
```

**No warning:**
```gams
eq5.. x**2 =l= 100;             # No warning: x^2 is even (may be convex)
eq6.. x =e= 5;                  # No warning: x^1 is linear
eq7.. x**4 + y**2 =l= 50;       # No warning: both even powers
eq8.. x**(-1) =l= 10;           # No warning: x^-1 handled by W304
```

### How to Fix

**Option 1: Variable Bounds**

If you can bound x to be nonnegative or nonpositive, odd powers become monotonic:

```gams
x.lo = 0;  # Force x ≥ 0, making x^3 monotonic increasing
```

**Option 2: Solver Selection**

Use global optimization solvers:
- BARON (handles polynomial non-convexity)
- ANTIGONE
- SCIP

**Option 3: Reformulation with Auxiliary Variables**

For x³, introduce auxiliary variable w:

```gams
Variables w;
Equations aux_eq;

aux_eq.. w =e= x * x * x;  # May trigger W303 (bilinear)
```

Note: This doesn't eliminate non-convexity but may help some solvers.

---

## Suppressing Warnings

If you understand the non-convex nature of your problem and want to proceed without warnings:

```bash
nlp2mcp model.gms -o output.gms --skip-convexity-check
```

This will disable all convexity pattern detection.

---

## Understanding False Positives

### When Warnings May Be Incorrect

1. **Special Problem Structure**: Some problems have special structure that guarantees convexity despite individual non-convex terms

2. **Bounded Variables**: With tight bounds, non-convex functions may be monotonic over the feasible region

3. **Equality Constraints**: Sometimes nonlinear equalities are part of a convex problem (e.g., defining a convex manifold)

### What To Do

If you believe a warning is a false positive:
- Verify your problem is indeed convex using convexity analysis
- Use `--skip-convexity-check` to suppress warnings
- The tool will still convert your model correctly

---

## For Developers

### Error Code Registry

Error codes are defined in `src/utils/error_codes.py`. Each pattern has:
- Unique W3xx code
- Error level (Warning)
- Documentation anchor
- URL generation

### Pattern Matchers

Implemented in `src/diagnostics/convexity/patterns.py`:
- `NonlinearEqualityPattern` → W301
- `TrigonometricPattern` → W302
- `BilinearTermPattern` → W303
- `QuotientPattern` → W304
- `OddPowerPattern` → W305

### Adding New Patterns

To add a new convexity pattern:

1. Define error code in `src/utils/error_codes.py`
2. Create pattern matcher in `src/diagnostics/convexity/patterns.py`
3. Add pattern to CLI in `src/cli.py`
4. Document in this file with anchor link
5. Add tests in `tests/unit/diagnostics/test_convexity_patterns.py`

---

## References

- Boyd, S., & Vandenberghe, L. (2004). *Convex Optimization*. Cambridge University Press.
- Nocedal, J., & Wright, S. (2006). *Numerical Optimization*. Springer.
- POC validation: `scripts/poc_convexity_patterns.py` (100% accuracy on test fixtures)

---

## Feedback

If you encounter:
- Incorrect warnings (false positives)
- Missed patterns (false negatives)
- Suggestions for new patterns

Please open an issue at: https://github.com/jeffreyhorn/nlp2mcp/issues
