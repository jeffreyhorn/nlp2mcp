# Automatic Differentiation Architecture

**Author:** nlp2mcp Development Team  
**Date:** 2025-10-28  
**Sprint:** Sprint 2, Day 1  
**Status:** Initial Design

---

## Overview

This document describes the symbolic automatic differentiation (AD) architecture for the nlp2mcp project. The AD engine computes derivatives of GAMS NLP expressions to support KKT condition generation.

## Design Decision: Symbolic vs. Reverse-Mode AD

### Why Symbolic Differentiation?

We chose **symbolic differentiation** (AST → AST transformations) over traditional **adjoint-style reverse-mode AD** for the following reasons:

#### 1. **Transparency and Inspectability**
- Derivative expressions remain as AST nodes
- Can be inspected, pretty-printed, and verified before evaluation
- Easier debugging: symbolic derivatives match mathematical expectations
- Example: `d(x*y)/dx` → `Binary("*", Const(1), VarRef("y"))` is clearly `y`

#### 2. **Code Generation Requirements**
- Need to emit GAMS MCP code directly from derivative expressions
- Symbolic ASTs can be converted to GAMS syntax without evaluation
- No need for numerical evaluation before code generation
- Supports our primary use case: generating KKT systems in GAMS

#### 3. **Jacobian Structure**
- KKT conditions require symbolic Jacobian entries, not just numerical values
- Each Jacobian entry `J[i,j]` is a symbolic expression in GAMS
- Symbolic approach naturally produces the required structure

#### 4. **Simplicity and Maintainability**
- Easier to understand and debug than adjoint computations
- Each derivative rule is self-contained and testable
- Clear mapping from mathematical rules to code

#### 5. **Problem Size**
- NLP models are typically small to medium (100s-1000s of variables)
- Expression tree size not a bottleneck for our use cases
- Simplicity and correctness prioritized over maximum efficiency

### Trade-offs

**Disadvantages of Symbolic Differentiation:**
- Can produce larger expression trees than strictly necessary
- May compute redundant sub-expressions
- No automatic common subexpression elimination (CSE)

**Why These Are Acceptable:**
- Expression simplification can be added later if needed
- GAMS compiler will optimize generated code
- Clarity and correctness more important than minimal expression size
- Problem sizes don't require aggressive optimization

### Comparison with Reverse-Mode AD

| Aspect | Symbolic Differentiation | Reverse-Mode AD |
|--------|-------------------------|-----------------|
| Output | AST expressions | Numerical gradients |
| Use case | Code generation | Numerical optimization |
| Memory | O(expression size) | O(n) for n variables |
| Complexity | Simple rules | Adjoint tape management |
| Debugging | Easy (symbolic) | Harder (numerical) |
| For KKT | Yes - Perfect fit | No - Extra conversion needed |

---

## Architecture Components

### 1. Core Module: `src/ad/ad_core.py`

**Main Function:**
```python
def differentiate(expr: Expr, wrt_var: str) -> Expr:
    """
    Compute symbolic derivative of expression w.r.t. variable.
    
    Returns: New AST representing d(expr)/d(wrt_var)
    """
```

**Design Principles:**
- Pure function: never modifies input AST
- Returns new AST nodes
- Delegates to derivative_rules for specific node types

### 2. Derivative Rules: `src/ad/derivative_rules.py`

**Pattern:**
Each AST node type has a dedicated differentiation function:

```python
def _diff_const(expr: Const, wrt_var: str) -> Expr:
    """d(c)/dx = 0"""
    return Const(0.0)

def _diff_varref(expr: VarRef, wrt_var: str) -> Expr:
    """d(x)/dx = 1, d(y)/dx = 0"""
    return Const(1.0) if expr.name == wrt_var else Const(0.0)
```

**Dispatcher:**
```python
def differentiate_expr(expr: Expr, wrt_var: str) -> Expr:
    if isinstance(expr, Const):
        return _diff_const(expr, wrt_var)
    elif isinstance(expr, VarRef):
        return _diff_varref(expr, wrt_var)
    # ... more rules
```

### 3. Public API: `src/ad/__init__.py`

**Exports:**
- `differentiate(expr, wrt_var)` - Main entry point
- `simplify(expr)` - Future optimization (placeholder)

---

## Implementation Schedule (Sprint 2)

### Day 1 ✅ (Today)
- [x] Constants: `d(c)/dx = 0`
- [x] Variables: `d(x)/dx = 1`, `d(y)/dx = 0`
- [x] Parameters: `d(param)/dx = 0`
- [x] 16 tests passing

### Day 2 (Next)
- [ ] Binary operations: `+`, `-`, `*`, `/`
- [ ] Unary operations: `+x`, `-x`
- [ ] Product rule: `d(f*g)/dx = f*(dg/dx) + g*(df/dx)`
- [ ] Quotient rule: `d(f/g)/dx = (g*df - f*dg)/g²`

### Day 3
- [ ] Power: `d(x^n)/dx = n*x^(n-1)`
- [ ] Exponential: `d(exp(x))/dx = exp(x)`
- [ ] Logarithm: `d(log(x))/dx = 1/x`
- [ ] Square root: `d(sqrt(x))/dx = 1/(2*sqrt(x))`

### Day 4
- [ ] Trigonometric: `sin`, `cos`, `tan`
- [ ] abs() rejection with clear error

### Days 5-6
- [ ] Sum aggregation: `d(sum(i, f))/dx = sum(i, df/dx)`
- [ ] Index-aware differentiation
- [ ] Alias resolution

### Days 7-8
- [ ] Jacobian structure
- [ ] Gradient computation
- [ ] Objective expression handling

### Day 9
- [ ] Finite-difference validation
- [ ] NaN/Inf detection

### Day 10
- [ ] Integration and documentation

---

## Mathematical Foundation

### Basic Rules (Day 1 ✅)

1. **Constant Rule**
   ```
   d(c)/dx = 0
   ```

2. **Variable Rule**
   ```
   d(x)/dx = 1
   d(y)/dx = 0  (for y ≠ x)
   ```

3. **Parameter Rule**
   ```
   d(param)/dx = 0  (parameters are constant w.r.t. variables)
   ```

### Chain Rule (Days 2-4)

For composite functions `f(g(x))`:
```
d(f(g(x)))/dx = f'(g(x)) * g'(x)
```

Implementation:
```python
def _diff_call(expr: Call, wrt_var: str) -> Expr:
    # Differentiate outer function
    outer_deriv = _derivative_of_function(expr.func, expr.args)
    
    # Differentiate inner argument
    inner_deriv = differentiate(expr.args[0], wrt_var)
    
    # Apply chain rule: multiply
    return Binary("*", outer_deriv, inner_deriv)
```

### Linearity (Day 5)

For sum aggregations:
```
d(sum(i, f(x,i)))/dx = sum(i, df(x,i)/dx)
```

Derivative commutes with summation.

---

## Index-Aware Differentiation (Days 5-6)

### Challenge

Distinguish between:
- `d(x(i))/d(x(i))` = 1 (same instance)
- `d(x(i))/d(x(j))` = 0 (different instances, i ≠ j)

### Approach

For Day 1, we use simple name matching:
```python
# Current (Day 1)
VarRef("x", ("i",)) w.r.t. "x" → Const(1.0)
```

For Days 5-6, we'll implement full index matching:
```python
# Future (Days 5-6)
def _matches_indices(ref_indices, wrt_indices):
    """Check if indices represent same variable instance"""
    # Will implement Kronecker delta logic
```

This will be crucial for sparse Jacobian generation.

---

## Testing Strategy

### Unit Tests (Day 1: 16 tests ✅)

**Test Classes:**
1. `TestConstantDifferentiation` (3 tests)
   - Positive constant
   - Zero
   - Negative constant

2. `TestVariableReferenceDifferentiation` (5 tests)
   - Same variable
   - Different variable
   - Indexed variables
   - Multi-indexed variables

3. `TestSymbolReferenceDifferentiation` (2 tests)
   - Same symbol
   - Different symbol

4. `TestParameterReferenceDifferentiation` (3 tests)
   - Scalar parameter
   - Indexed parameter
   - Multi-indexed parameter

5. `TestUnsupportedExpressions` (1 test)
   - Helpful error for unimplemented types

6. `TestDifferentiationInvariance` (2 tests)
   - Original expressions not modified

### Future Testing (Days 2-9)

- **Day 2:** Arithmetic operations (12-15 tests)
- **Day 3:** Transcendental functions (12-15 tests)
- **Day 4:** Trigonometric functions (10-12 tests)
- **Days 5-6:** Sum and indexing (18 tests)
- **Days 7-8:** Jacobian structure (18-25 tests)
- **Day 9:** Finite-difference validation (12-15 tests)

**Total Target:** 63+ tests

---

## Error Handling

### Unsupported Operations

For unimplemented derivatives, we raise `TypeError` with helpful messages:

```python
raise TypeError(
    f"Differentiation not yet implemented for {type(expr).__name__}. "
    f"This will be added in subsequent days of Sprint 2."
)
```

This ensures:
- Clear feedback during development
- Gradual implementation across 10 days
- Easy identification of missing features

### Future Error Handling (Days 2-9)

- **Domain errors:** `log(x)` for x ≤ 0
- **Division by zero:** `x/0`
- **NaN/Inf detection:** Arithmetic overflow
- **abs() rejection:** Non-differentiable function

---

## Integration Points

### With Sprint 1 IR

The AD module consumes AST nodes from Sprint 1:
```python
from src.ir.ast import Expr, Const, VarRef, Binary, Call, Sum
```

All AST types are immutable (`@dataclass(frozen=True)`), ensuring:
- Thread safety
- No side effects during differentiation
- Cacheable results (future optimization)

### With Sprint 3 KKT Synthesis

Sprint 3 will use differentiated expressions to build:
- **Stationarity conditions:** `∇f + J_g^T λ + J_h^T ν = 0`
- **Jacobian matrices:** `J_g[i,j] = d(g_i)/d(x_j)` (as symbolic AST)
- **GAMS code generation:** Convert derivative ASTs to GAMS syntax

---

## Performance Considerations

### Current (Day 1)

- Simple operations: O(1)
- No recursion yet (only leaf nodes)

### Future (Days 2-6)

- Recursive differentiation: O(tree depth)
- No memoization (yet)
- Potentially redundant computations

### Optimization Opportunities (Post-Sprint 2)

1. **Constant Folding**
   ```python
   Binary("+", Const(2), Const(3)) → Const(5)
   ```

2. **Algebraic Simplification**
   ```python
   Binary("*", expr, Const(0)) → Const(0)
   Binary("+", expr, Const(0)) → expr
   ```

3. **Common Subexpression Elimination (CSE)**
   - Detect repeated sub-expressions
   - Compute once, reuse

4. **Memoization**
   - Cache `differentiate(expr, var)` results
   - Avoid redundant differentiation

**Decision:** Defer optimization to Sprint 4 or later. Focus on correctness first.

---

## References

### Mathematical Background

- **Calculus:** Standard derivative rules (power, product, quotient, chain)
- **Automatic Differentiation:** Griewank & Walther (2008)
- **Symbolic Computation:** Computer algebra systems (Mathematica, SymPy)

### Implementation Inspiration

- **SymPy:** Python symbolic mathematics
- **JAX:** Differentiable programming (uses reverse-mode, but concepts apply)
- **PyTorch Autograd:** Computational graphs (different approach, but instructive)

### Project-Specific

- Sprint 1 IR documentation: `src/ir/ast.py`
- Sprint 2 Plan: `docs/planning/SPRINT_2_PLAN.md`
- Project Plan: `docs/planning/PROJECT_PLAN.md`

---

## Conclusion

The symbolic differentiation architecture provides a clean, understandable, and maintainable foundation for computing derivatives in nlp2mcp. By producing symbolic AST expressions as derivatives, we perfectly match the requirements for KKT synthesis and GAMS code generation.

**Day 1 Status:** ✅ **COMPLETE**
- 16 tests passing
- Basic derivative rules implemented
- Foundation ready for Day 2 arithmetic operations

**Next Steps (Day 2):**
- Implement binary operation differentiation
- Add unary operator support
- Create AST evaluator for testing
- Implement NaN/Inf detection
