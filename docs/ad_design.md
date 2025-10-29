# Automatic Differentiation Design

## Overview

The `src/ad/` module implements **symbolic differentiation** for GAMS NLP expressions. Given an optimization model, it computes:

- **Gradient**: ∇f(x) for the objective function
- **Constraint Jacobians**: J_g(x) and J_h(x) for inequality and equality constraints

All derivatives are computed symbolically and stored as AST expressions that can be evaluated at specific points.

## Why Symbolic Differentiation?

We chose symbolic differentiation over other AD approaches (like reverse-mode/adjoint AD) for several key reasons:

### 1. **Transparency and Debuggability**
- Derivatives are explicit AST expressions that can be inspected
- Users can see exactly what derivative was computed
- Easy to verify correctness by comparing with hand-derived formulas
- Facilitates debugging when derivatives seem incorrect

### 2. **Multiple Evaluation Points**
- Symbolic expressions can be evaluated at any point
- No need to re-run AD for different evaluation points
- Ideal for iterative optimization algorithms that query derivatives repeatedly

### 3. **Code Generation Friendly**
- Symbolic expressions can be directly translated to target languages (Python, Julia, C++)
- Enables efficient code generation for KKT conditions (Sprint 3)
- Can be optimized via algebraic simplification (future work)

### 4. **Natural Fit for Sparse Problems**
- Index-aware differentiation naturally produces sparse structure
- Easy to identify which derivatives are structurally zero
- Sparsity pattern available before evaluation

### 5. **Educational Value**
- Students and researchers can learn by inspecting symbolic derivatives
- Makes the "black box" of AD more transparent
- Aligns with mathematical notation (∂f/∂x)

### Trade-offs

**Advantages:**
- ✅ Transparent and inspectable
- ✅ Reusable across evaluation points
- ✅ Code generation friendly
- ✅ Natural sparsity handling
- ✅ Educational value

**Disadvantages:**
- ❌ Can produce large expression trees (no automatic simplification yet)
- ❌ May be slower than reverse-mode AD for functions with many inputs
- ❌ Memory usage grows with expression complexity

For our use case (NLP → MCP transformation with code generation), the advantages far outweigh the disadvantages.

## Architecture

### Module Structure

```
src/ad/
├── api.py                  # High-level public API
├── derivative_rules.py     # Core differentiation rules
├── evaluator.py           # Expression evaluation
├── gradient.py            # Objective gradient computation
├── constraint_jacobian.py # Constraint Jacobian computation
├── jacobian.py            # Jacobian data structures
├── index_mapping.py       # Variable/equation enumeration
├── sparsity.py            # Sparsity pattern analysis
├── validation.py          # Finite-difference validation
└── __init__.py            # Public exports
```

### Data Flow

```
GAMS File
    ↓
[Parser] → ModelIR (AST)
    ↓
[Normalize] → Normalized equations & bounds
    ↓
[Index Mapping] → Variable instances → Dense IDs
                   Equation instances → Dense IDs
    ↓
[Symbolic Differentiation]
    ├→ [Gradient] → ∇f(x)
    └→ [Jacobian] → J_g(x), J_h(x)
    ↓
[Code Generation] → Python/Julia/C++ (Sprint 3)
```

## Core Components

### 1. Symbolic Differentiation Engine

**File**: `src/ad/derivative_rules.py`

Implements standard calculus rules:

- **Constant Rule**: d(c)/dx = 0
- **Variable Rule**: d(x)/dx = 1, d(y)/dx = 0
- **Sum Rule**: d(f+g)/dx = df/dx + dg/dx
- **Product Rule**: d(fg)/dx = f(dg/dx) + g(df/dx)
- **Quotient Rule**: d(f/g)/dx = (g(df/dx) - f(dg/dx))/g²
- **Chain Rule**: d(f(g))/dx = f'(g) * dg/dx
- **Power Rule**: d(x^n)/dx = n*x^(n-1)
- **Exponential**: d(exp(x))/dx = exp(x)
- **Logarithm**: d(log(x))/dx = 1/x
- **Trigonometric**: d(sin(x))/dx = cos(x), etc.

**Key Feature**: Index-Aware Differentiation
- Distinguishes between x (scalar) and x(i) (indexed)
- Handles sum collapse: ∂(sum(i, x(i)))/∂x(i1) = 1
- Enables correct sparse Jacobian construction

### 2. Index Mapping

**File**: `src/ad/index_mapping.py`

Maps symbolic variable/equation instances to dense integer IDs:

```python
# Variables:
x       → col_id = 0
y       → col_id = 1
z(i1)   → col_id = 2
z(i2)   → col_id = 3
z(i3)   → col_id = 4

# Equations:
balance(i1)  → row_id = 0
balance(i2)  → row_id = 1
balance(i3)  → row_id = 2
```

**Features**:
- Deterministic ordering (sorted by name and indices)
- Handles set aliases and universe constraints
- Detects circular aliases
- Enumerates cross-product of multi-dimensional indices

### 3. Gradient Computation

**File**: `src/ad/gradient.py`

Computes ∇f(x) = [∂f/∂x₁, ∂f/∂x₂, ..., ∂f/∂xₙ]

**Algorithm**:
1. Find objective expression (explicit or from defining equation)
2. Enumerate all variable instances
3. Differentiate objective w.r.t. each variable
4. Handle ObjSense.MAX by negating gradient (max f = min -f)
5. Store results in GradientVector

**Sparsity**: In principle, objective may depend on all variables, so gradient is typically dense.

### 4. Constraint Jacobian Computation

**File**: `src/ad/constraint_jacobian.py`

Computes constraint Jacobians:
- **J_h**: Equality constraints h(x) = 0
- **J_g**: Inequality constraints g(x) ≤ 0

**Algorithm**:
1. Normalize constraints to canonical form (lhs - rhs REL 0)
2. Enumerate equation instances
3. For each constraint and variable, compute ∂constraint/∂variable
4. Store non-zero derivatives in sparse structure
5. Include bound-derived equations in J_g

**Sparsity**: Most constraints depend on few variables, so Jacobians are typically sparse.

### 5. AST Evaluator

**File**: `src/ad/evaluator.py`

Evaluates symbolic expressions at concrete points:

**Features**:
- Evaluates all AST node types
- Handles indexed variables and parameters
- Detects NaN/Inf and domain violations
- Raises clear errors with context

**Usage**:
```python
from src.ad.evaluator import evaluate
from src.ir.ast import Binary, Call, VarRef, Const

# Symbolic expression: x^2 + y
expr = Binary(
    op="+",
    left=Call(func="power", args=(VarRef(name="x"), Const(value=2.0))),
    right=VarRef(name="y")
)

# Evaluate at point
var_values = {("x", ()): 3.0, ("y", ()): 5.0}
result = evaluate(expr, var_values, {})
# result = 14.0 (3² + 5)
```

### 6. Finite-Difference Validation

**File**: `src/ad/validation.py`

Validates symbolic derivatives against numerical finite-difference:

**Method**: Central difference
```
f'(x) ≈ (f(x+h) - f(x-h))/(2h)
```

**Features**:
- Deterministic test point generation (seed=42)
- Respects variable bounds
- Avoids domain boundaries (log, sqrt)
- Tolerance: 1e-6

**Usage**: Primarily for testing, not production

## Supported Operations

### Arithmetic Operations ✅
- Addition: `a + b`
- Subtraction: `a - b`
- Multiplication: `a * b`
- Division: `a / b`

### Unary Operations ✅
- Unary plus: `+a`
- Unary minus: `-a`

### Mathematical Functions ✅
- Power: `power(base, exponent)`
- Exponential: `exp(x)`
- Logarithm: `log(x)` (natural log)
- Square root: `sqrt(x)`

### Trigonometric Functions ✅
- Sine: `sin(x)`
- Cosine: `cos(x)`
- Tangent: `tan(x)`

### Aggregations ✅
- Sum: `sum(i, expr(i))`

### Not Supported ❌
- **abs()**: Rejected as non-differentiable at x=0
  - Alternative: Use smooth approximations (future work)
  - Planned: `--smooth-abs` flag to replace abs(x) with sqrt(x² + ε)

## Index-Aware Differentiation

A key innovation in our implementation is **index-aware differentiation**, which correctly handles indexed variables.

### The Problem

Consider:
```
f(x) = sum(i, x(i)²)
```

What is ∂f/∂x(i1)?

**Naive approach** (wrong):
```
∂f/∂x = sum(i, 2*x(i))  # Wrong! This is the same for all x instances
```

**Correct approach** (index-aware):
```
∂f/∂x(i1) = 2*x(i1)  # Only the i1 term contributes
∂f/∂x(i2) = 2*x(i2)  # Only the i2 term contributes
```

### Implementation

The differentiation engine accepts an optional `wrt_indices` parameter:

```python
# Scalar differentiation (backward compatible)
differentiate_expr(expr, "x")  # d/dx

# Index-aware differentiation
differentiate_expr(expr, "x", ("i1",))  # d/dx(i1)
```

### Semantics

| Expression | d/dx | d/dx(i1) |
|------------|------|----------|
| x          | 1    | 0        |
| x(i1)      | 0    | 1        |
| x(i2)      | 0    | 0        |

### Sum Collapse

When differentiating a sum with respect to a specific index instance:

```python
expr = sum(i, x(i))
d_expr_dx_i1 = differentiate_expr(expr, "x", ("i1",))
# Result: 1 (not sum(i, ...))
```

This is mathematically correct because:
```
∂(sum(i, x(i)))/∂x(i1) = sum(i, ∂x(i)/∂x(i1))
                       = sum(i, [1 if i=i1 else 0])
                       = 1
```

## Error Handling

### Domain Violations

The evaluator detects and reports domain violations:

```python
log(-1)    # EvaluationError: log domain error
sqrt(-1)   # EvaluationError: sqrt domain error
1/0        # EvaluationError: Division by zero
```

### Missing Values

Clear errors when variables/parameters are missing:

```python
# EvaluationError: Missing value for variable x
```

### Unsupported Operations

Differentiation raises errors for unsupported functions:

```python
abs(x)  # ValueError: abs() is not differentiable everywhere
```

## Future Enhancements

### Sprint 3: Code Generation
- Generate Python/Julia/C++ code from symbolic expressions
- Optimize generated code for performance
- Handle KKT condition generation

### Sprint 4+: Algebraic Simplification
- Implement expression simplification rules
- Constant folding: `0 + x → x`, `1 * x → x`
- Algebraic identities: `x - x → 0`, `x / x → 1`
- Common subexpression elimination

### Sprint 4+: Advanced Features
- Second-order derivatives (Hessian)
- Smooth approximations for abs()
- Support for more functions (asin, acos, atan, etc.)
- Automatic sparsity detection and exploitation

## Testing Strategy

### Unit Tests
- Test each derivative rule independently
- Verify chain rule, product rule, quotient rule
- Test edge cases (zero, negative, boundary values)

### Finite-Difference Validation
- Validate all derivative rules against numerical FD
- Deterministic test points (seed=42)
- Tolerance: 1e-6

### Integration Tests
- Full pipeline: parse → normalize → differentiate
- Test on realistic NLP models
- Verify sparsity patterns

### Coverage
- Goal: >90% code coverage
- Focus on core differentiation and evaluation logic

## Performance Considerations

### Time Complexity
- Differentiation: O(n) where n = expression tree size
- Evaluation: O(n) where n = expression tree size
- Gradient: O(m × n) where m = variables, n = expression size
- Jacobian: O(p × m × n) where p = equations, m = variables, n = expression size

### Space Complexity
- Each derivative creates a new AST
- No automatic simplification yet
- Can lead to expression explosion for complex models
- Future work: Implement simplification to reduce memory

### Optimization Opportunities
1. **Algebraic Simplification**: Reduce expression tree size
2. **Common Subexpression Elimination**: Reuse repeated subexpressions
3. **Lazy Evaluation**: Only compute derivatives when needed
4. **Caching**: Cache derivative results for repeated queries

## References

- Griewank & Walther (2008): "Evaluating Derivatives: Principles and Techniques of Algorithmic Differentiation"
- Nocedal & Wright (2006): "Numerical Optimization" (Chapter on derivative computation)
- GAMS Documentation: Derivative computation in solvers
- Symbolics.jl: Symbolic mathematics in Julia (inspiration for design)

## See Also

- [Derivative Rules Reference](derivative_rules.md) - Mathematical formulas for all rules
- [API Documentation](../src/ad/api.py) - High-level usage guide
- [Sprint 2 Plan](planning/SPRINT_2_PLAN.md) - Development schedule and acceptance criteria
