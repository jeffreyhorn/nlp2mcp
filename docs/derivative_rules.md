# Derivative Rules Reference

This document provides a comprehensive reference of all derivative rules implemented in the symbolic differentiation engine.

## Table of Contents

1. [Basic Rules](#basic-rules)
2. [Arithmetic Operations](#arithmetic-operations)
3. [Power Functions](#power-functions)
4. [Exponential and Logarithmic](#exponential-and-logarithmic)
5. [Trigonometric Functions](#trigonometric-functions)
6. [Aggregation Operations](#aggregation-operations)
7. [Index-Aware Differentiation](#index-aware-differentiation)

## Basic Rules

### Constant Rule

**Expression:** `c` (where c is a constant)

**Derivative:**
```
∂c/∂x = 0
```

**Examples:**
- `∂(5)/∂x = 0`
- `∂(3.14)/∂x = 0`

### Variable Rule

**Expression:** `x`

**Derivative:**
```
∂x/∂x = 1
∂x/∂y = 0  (if x ≠ y)
```

**Examples:**
- `∂x/∂x = 1`
- `∂y/∂x = 0`

## Arithmetic Operations

### Addition Rule

**Expression:** `f(x) + g(x)`

**Derivative:**
```
∂/∂x [f(x) + g(x)] = ∂f/∂x + ∂g/∂x
```

**Example:**
```
f(x) = x² + 3x
∂f/∂x = ∂(x²)/∂x + ∂(3x)/∂x = 2x + 3
```

### Subtraction Rule

**Expression:** `f(x) - g(x)`

**Derivative:**
```
∂/∂x [f(x) - g(x)] = ∂f/∂x - ∂g/∂x
```

**Example:**
```
f(x) = x² - 5x
∂f/∂x = ∂(x²)/∂x - ∂(5x)/∂x = 2x - 5
```

### Product Rule

**Expression:** `f(x) · g(x)`

**Derivative:**
```
∂/∂x [f(x) · g(x)] = f(x) · ∂g/∂x + g(x) · ∂f/∂x
```

**Example:**
```
f(x) = x² · sin(x)
∂f/∂x = x² · cos(x) + sin(x) · 2x
      = x² · cos(x) + 2x · sin(x)
```

### Quotient Rule

**Expression:** `f(x) / g(x)`

**Derivative:**
```
∂/∂x [f(x)/g(x)] = [g(x) · ∂f/∂x - f(x) · ∂g/∂x] / [g(x)]²
```

**Example:**
```
f(x) = x² / (x + 1)
∂f/∂x = [(x + 1) · 2x - x² · 1] / (x + 1)²
      = [2x² + 2x - x²] / (x + 1)²
      = [x² + 2x] / (x + 1)²
```

### Negation Rule

**Expression:** `-f(x)`

**Derivative:**
```
∂/∂x [-f(x)] = -∂f/∂x
```

**Example:**
```
f(x) = -x²
∂f/∂x = -2x
```

## Power Functions

### Power Rule (Constant Exponent)

**Expression:** `x^n` (where n is a constant)

**Derivative:**
```
∂/∂x [x^n] = n · x^(n-1)
```

**Examples:**
```
∂(x²)/∂x = 2x
∂(x³)/∂x = 3x²
∂(x^0.5)/∂x = 0.5 · x^(-0.5) = 1/(2√x)
```

### General Power Rule

**Expression:** `f(x)^n` (where n is a constant)

**Derivative:**
```
∂/∂x [f(x)^n] = n · f(x)^(n-1) · ∂f/∂x
```

**Example:**
```
f(x) = (x² + 1)³
∂f/∂x = 3 · (x² + 1)² · 2x
      = 6x · (x² + 1)²
```

### Exponential Power Rule

**Expression:** `f(x)^g(x)` (both base and exponent are functions)

**Derivative:**
```
∂/∂x [f(x)^g(x)] = f(x)^g(x) · [g(x) · ∂f/∂x / f(x) + ln(f(x)) · ∂g/∂x]
```

**Example:**
```
f(x) = x^x
∂f/∂x = x^x · [x · 1/x + ln(x) · 1]
      = x^x · [1 + ln(x)]
```

## Exponential and Logarithmic

### Exponential Function (base e)

**Expression:** `exp(f(x))` or `e^f(x)`

**Derivative:**
```
∂/∂x [exp(f(x))] = exp(f(x)) · ∂f/∂x
```

**Examples:**
```
∂(exp(x))/∂x = exp(x)
∂(exp(2x))/∂x = exp(2x) · 2 = 2 · exp(2x)
∂(exp(x²))/∂x = exp(x²) · 2x
```

### Natural Logarithm

**Expression:** `log(f(x))` or `ln(f(x))`

**Derivative:**
```
∂/∂x [log(f(x))] = (1/f(x)) · ∂f/∂x
```

**Examples:**
```
∂(log(x))/∂x = 1/x
∂(log(x²))/∂x = (1/x²) · 2x = 2/x
∂(log(x + 1))/∂x = 1/(x + 1)
```

### Square Root

**Expression:** `sqrt(f(x))` or `√f(x)`

**Derivative:**
```
∂/∂x [sqrt(f(x))] = (1/(2·sqrt(f(x)))) · ∂f/∂x
```

**Examples:**
```
∂(sqrt(x))/∂x = 1/(2√x)
∂(sqrt(x² + 1))/∂x = (1/(2√(x² + 1))) · 2x
                   = x/√(x² + 1)
```

## Trigonometric Functions

### Sine Function

**Expression:** `sin(f(x))`

**Derivative:**
```
∂/∂x [sin(f(x))] = cos(f(x)) · ∂f/∂x
```

**Examples:**
```
∂(sin(x))/∂x = cos(x)
∂(sin(2x))/∂x = cos(2x) · 2 = 2 · cos(2x)
∂(sin(x²))/∂x = cos(x²) · 2x
```

### Cosine Function

**Expression:** `cos(f(x))`

**Derivative:**
```
∂/∂x [cos(f(x))] = -sin(f(x)) · ∂f/∂x
```

**Examples:**
```
∂(cos(x))/∂x = -sin(x)
∂(cos(3x))/∂x = -sin(3x) · 3 = -3 · sin(3x)
∂(cos(x²))/∂x = -sin(x²) · 2x
```

### Tangent Function

**Expression:** `tan(f(x))`

**Derivative:**
```
∂/∂x [tan(f(x))] = sec²(f(x)) · ∂f/∂x
                 = (1/cos²(f(x))) · ∂f/∂x
```

**Examples:**
```
∂(tan(x))/∂x = sec²(x) = 1/cos²(x)
∂(tan(2x))/∂x = sec²(2x) · 2 = 2/cos²(2x)
```

### Arcsine Function

**Expression:** `arcsin(f(x))`

**Derivative:**
```
∂/∂x [arcsin(f(x))] = (1/√(1 - f(x)²)) · ∂f/∂x
```

**Example:**
```
∂(arcsin(x))/∂x = 1/√(1 - x²)
```

### Arccosine Function

**Expression:** `arccos(f(x))`

**Derivative:**
```
∂/∂x [arccos(f(x))] = -(1/√(1 - f(x)²)) · ∂f/∂x
```

**Example:**
```
∂(arccos(x))/∂x = -1/√(1 - x²)
```

### Arctangent Function

**Expression:** `arctan(f(x))`

**Derivative:**
```
∂/∂x [arctan(f(x))] = (1/(1 + f(x)²)) · ∂f/∂x
```

**Example:**
```
∂(arctan(x))/∂x = 1/(1 + x²)
```

## Aggregation Operations

### Sum Rule

**Expression:** `Σᵢ f(xᵢ)` (sum over index i)

**Derivative with respect to scalar variable y:**
```
∂/∂y [Σᵢ f(xᵢ, y)] = Σᵢ [∂f(xᵢ, y)/∂y]
```

**Derivative with respect to indexed variable x(j):**
```
∂/∂x(j) [Σᵢ f(xᵢ)] = ∂f(x(j))/∂x(j)
```

**Example:**
```
f = Σᵢ xᵢ²

∂f/∂x(j) = ∂/∂x(j) [Σᵢ xᵢ²]
         = ∂(x(j)²)/∂x(j)    (only the j-th term contributes)
         = 2·x(j)
```

### Product in Sum

**Expression:** `Σᵢ [a(i) · x(i)]` (weighted sum)

**Derivative with respect to x(j):**
```
∂/∂x(j) [Σᵢ a(i)·x(i)] = a(j)
```

**Example:**
```
f = Σᵢ cᵢ·xᵢ    (linear combination)

∂f/∂x(j) = cⱼ
```

## Index-Aware Differentiation

The symbolic differentiation engine distinguishes between scalar and indexed variables:

### Scalar vs Indexed Variables

**Scalar variable:** `x` (no indices)
```
∂x/∂x = 1
```

**Indexed variable:** `x(i)` (has indices)
```
∂x(i)/∂x(j) = δᵢⱼ    (Kronecker delta: 1 if i=j, 0 otherwise)
```

### Summation with Index Matching

When differentiating a sum, only terms where indices match contribute:

**Expression:** `Σᵢ f(x(i), y)`

**Derivative with respect to x(j):**
```
∂/∂x(j) [Σᵢ f(x(i), y)] = ∂f(x(j), y)/∂x(j)
```

Only the term where `i = j` contributes to the derivative.

### Example: Quadratic Objective

**GAMS Model:**
```gams
Variable x(i);
Equation obj_def;

obj_def.. obj =e= sum(i, sqr(x(i)));
```

**Symbolic Derivative:**
```
∂obj/∂x(j) = ∂/∂x(j) [Σᵢ x(i)²]
           = 2·x(j)
```

**Implementation:**
The engine recognizes that:
1. `x` is an indexed variable (has set `i`)
2. When differentiating with respect to `x(j)`, only the `j`-th term contributes
3. The result is `2·x(j)`, not `Σᵢ 2·x(i)`

### Example: Constraint Jacobian

**GAMS Model:**
```gams
Variable x(i);
Equation constraint(i);

constraint(i).. x(i) * x(i) =l= 1;
```

**Jacobian Entry:**
```
∂constraint(i)/∂x(j) = ∂[x(i)²]/∂x(j)
                     = 2·x(i)  if i = j
                     = 0       if i ≠ j
```

This creates a sparse diagonal Jacobian structure.

## Chain Rule

The chain rule is fundamental to all composite function differentiation:

**General Form:**
```
∂/∂x [f(g(x))] = f'(g(x)) · g'(x)
```

All the rules above for composed functions (power, exponential, trigonometric, etc.) are applications of the chain rule.

## Implementation Notes

### Simplification

After applying derivative rules, the engine simplifies expressions:

1. **Arithmetic simplification:**
   - `0 + x → x`
   - `x + 0 → x`
   - `0 · x → 0`
   - `1 · x → x`
   - `x · 1 → x`

2. **Power simplification:**
   - `x^0 → 1`
   - `x^1 → x`
   - `0^n → 0` (for n > 0)
   - `1^n → 1`

3. **Constant folding:**
   - `2 + 3 → 5`
   - `4 · 5 → 20`

### Evaluation

Symbolic derivatives can be evaluated at specific points:

```python
from src.ad import differentiate, evaluate
from src.ir.ast import Binary, VarRef, Const

# Symbolic differentiation
expr = Binary(op='+', left=VarRef('x'), right=Const(2))  # x + 2
deriv = differentiate(expr, 'x')  # Result: Const(1)

# Evaluation
result = evaluate(deriv, {'x': 5.0})  # Result: 1.0
```

## References

- Griewank, A., & Walther, A. (2008). *Evaluating Derivatives: Principles and Techniques of Algorithmic Differentiation*. SIAM.
- Nocedal, J., & Wright, S. J. (2006). *Numerical Optimization* (2nd ed.). Springer.

## See Also

- [AD Design Document](ad_design.md) - Architecture and implementation details
- [AD Module Documentation](../src/ad/README.md) - API reference
- [Test Suite](../tests/ad/) - Examples and validation tests
