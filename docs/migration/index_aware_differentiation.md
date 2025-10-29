# Migration Guide: Index-Aware Differentiation

This guide helps you understand and transition to the index-aware differentiation feature introduced in Sprint 2 Day 7.5.

## Overview

The differentiation engine now properly distinguishes between **scalar variables** and **indexed variable instances**. This ensures correct sparse Jacobian construction for optimization models with indexed variables.

## What Changed

### Previous Behavior (Before Sprint 2 Day 7.5)

The differentiation engine treated all variables with the same name as equivalent, regardless of their indices. This led to incorrect derivatives for indexed variables.

**Example Problem:**
```python
# Objective: sum(i, x(i)^2) where i ∈ {i1, i2}
# Previous (WRONG): All x instances shared the same symbolic derivative
# ∂f/∂x(i1) = sum(i, 2*x(i))  # WRONG: includes all terms
# ∂f/∂x(i2) = sum(i, 2*x(i))  # WRONG: same as above
```

### New Behavior (After Sprint 2 Day 7.5)

The differentiation engine now distinguishes between different variable instances based on their **exact index tuple**.

**Correct Behavior:**
```python
# Objective: sum(i, x(i)^2) where i ∈ {i1, i2}
# Correct (NOW): Each instance gets its own derivative
# ∂f/∂x(i1) = 2*x(i1)  # CORRECT: only i1 term
# ∂f/∂x(i2) = 2*x(i2)  # CORRECT: only i2 term
```

## Key Semantics

The new system follows these differentiation rules:

| Expression | Differentiation w.r.t. | Result | Explanation |
|------------|------------------------|--------|-------------|
| `x` | `d/dx` (scalar) | `1` | Scalar matches scalar |
| `x(i)` | `d/dx` (scalar) | `0` | Indexed doesn't match scalar |
| `x` | `d/dx(i)` (indexed) | `0` | Scalar doesn't match indexed |
| `x(i)` | `d/dx(i)` (indexed) | `1` | Exact index match |
| `x(j)` | `d/dx(i)` (indexed) | `0` | Index mismatch |

**Key principle:** A variable matches only if both the **name** and **indices** match exactly.

## API Changes

### Function Signature

The `differentiate_expr()` function now accepts an optional `wrt_indices` parameter:

```python
def differentiate_expr(
    expr: Expr,
    wrt_var: str,
    wrt_indices: tuple[str, ...] | None = None
) -> Expr:
    """
    Differentiate expression with respect to a variable instance.
    
    Args:
        expr: Expression to differentiate
        wrt_var: Variable name (e.g., "x")
        wrt_indices: Optional index tuple (e.g., ("i1",) or ("i1", "j2"))
                     - None: differentiate w.r.t. scalar variable
                     - Provided: differentiate w.r.t. indexed variable
    """
```

### Breaking Changes

**None.** The default parameter value (`wrt_indices=None`) ensures backward compatibility.

## Migration Steps

### Step 1: Understand Your Use Case

**Do you have indexed variables?**
- **No:** No changes needed. Your code continues to work unchanged.
- **Yes:** Read on to understand how to use index-aware differentiation.

### Step 2: Update Gradient/Jacobian Computation

The `compute_objective_gradient()` and Jacobian computation functions have been updated internally to use index-aware differentiation. **No changes are required in your code.**

**Before (you don't need to change this):**
```python
# This still works and now produces correct results
gradient = compute_objective_gradient(model_ir)
```

**After (automatic, handled internally):**
```python
# The function now calls differentiate_expr with indices:
for var_name, indices in variable_instances:
    derivative = differentiate_expr(obj_expr, var_name, indices)
```

### Step 3: Direct API Usage (Advanced)

If you're calling `differentiate_expr()` directly, you may want to use the new parameter:

**Example: Differentiating w.r.t. Scalar Variable**
```python
from src.ir.ast import VarRef, Const
from src.ad.derivative_rules import differentiate_expr

# Scalar variable
expr = VarRef("x")
result = differentiate_expr(expr, "x")  # wrt_indices=None (default)
# result = Const(1.0)

# Indexed variable, differentiate w.r.t. scalar
expr = VarRef("x", ("i1",))
result = differentiate_expr(expr, "x")  # wrt_indices=None
# result = Const(0.0)  # indexed doesn't match scalar
```

**Example: Differentiating w.r.t. Indexed Variable**
```python
# Indexed variable, exact match
expr = VarRef("x", ("i1",))
result = differentiate_expr(expr, "x", ("i1",))  # wrt_indices=("i1",)
# result = Const(1.0)  # exact match

# Indexed variable, mismatch
expr = VarRef("x", ("i2",))
result = differentiate_expr(expr, "x", ("i1",))  # wrt_indices=("i1",)
# result = Const(0.0)  # index mismatch
```

## Examples

### Example 1: Quadratic Objective with Indexed Variables

**GAMS Model:**
```gams
Set i /i1, i2, i3/;
Variable x(i);
Variable obj;

Equation obj_def;
obj_def.. obj =e= sum(i, x(i) * x(i));
```

**Gradient Computation:**
```python
# Internal computation (automatic):
# For each instance:
#   ∂f/∂x(i1) = differentiate_expr(sum(i, x(i)^2), "x", ("i1",))
#              = 2*x(i1)  # sum collapses to i1 term only
#
#   ∂f/∂x(i2) = differentiate_expr(sum(i, x(i)^2), "x", ("i2",))
#              = 2*x(i2)  # sum collapses to i2 term only
#
#   ∂f/∂x(i3) = differentiate_expr(sum(i, x(i)^2), "x", ("i3",))
#              = 2*x(i3)  # sum collapses to i3 term only
```

### Example 2: Mixed Scalar and Indexed Variables

**GAMS Model:**
```gams
Set i /i1, i2/;
Variable x(i);
Variable y;
Variable obj;

Equation obj_def;
obj_def.. obj =e= sum(i, x(i)) + y * y;
```

**Gradient Computation:**
```python
# ∂f/∂x(i1) = 1 (from sum term where i=i1)
# ∂f/∂x(i2) = 1 (from sum term where i=i2)
# ∂f/∂y = 2*y (from y^2 term)
```

### Example 3: Multi-Dimensional Indices

**GAMS Model:**
```gams
Set i /i1, i2/;
Set j /j1, j2/;
Variable x(i, j);
Variable obj;

Equation obj_def;
obj_def.. obj =e= sum((i,j), x(i,j) * x(i,j));
```

**Gradient Computation:**
```python
# For each (i, j) combination:
#   ∂f/∂x(i1,j1) = 2*x(i1,j1)
#   ∂f/∂x(i1,j2) = 2*x(i1,j2)
#   ∂f/∂x(i2,j1) = 2*x(i2,j1)
#   ∂f/∂x(i2,j2) = 2*x(i2,j2)
```

## Sum Collapse Behavior

A special optimization occurs when differentiating sums:

**Mathematical Rule:**
```
∂(sum(i, f(x(i))))/∂x(i1) = sum(i, ∂f(x(i))/∂x(i1))
                           = sum(i, [result if i=i1 else 0])
                           = result[i→i1]
```

**Example:**
```python
# Differentiating sum(i, x(i)^2) w.r.t. x(i1)
# Previous (Day 1-7.4): Returns Sum(i, 2*x(i))  # WRONG
# Current (Day 7.5+):  Returns 2*x(i1)          # CORRECT (collapsed)
```

The sum collapses because only the term where `i=i1` contributes a non-zero derivative.

## Common Pitfalls

### Pitfall 1: Mixing Scalar and Indexed References

**Problem:**
```python
# If you have both scalar x and indexed x(i), they are DIFFERENT variables
expr1 = VarRef("x")        # scalar x
expr2 = VarRef("x", ("i1",))  # indexed x(i1)

# These produce different results:
differentiate_expr(expr1, "x")        # = 1 (matches)
differentiate_expr(expr2, "x")        # = 0 (doesn't match)
differentiate_expr(expr1, "x", ("i1",))  # = 0 (doesn't match)
differentiate_expr(expr2, "x", ("i1",))  # = 1 (matches)
```

**Solution:** Be consistent. Use either scalar OR indexed variables, not both for the same base name.

### Pitfall 2: Forgetting Index Tuple

**Problem:**
```python
# If you want to differentiate w.r.t. x(i1), you MUST provide indices
result = differentiate_expr(expr, "x")  # This is w.r.t. scalar x, not x(i1)!
```

**Solution:**
```python
# Correct: specify indices for indexed differentiation
result = differentiate_expr(expr, "x", ("i1",))
```

### Pitfall 3: Index Naming Conventions

**Problem:**
The sum collapse heuristic relies on naming patterns: "i1", "i2" are instances of "i".

```python
# These work with sum collapse:
sum(i, x(i)) differentiated w.r.t. x(i1)  # ✓ "i1" matches "i"
sum(j, x(j)) differentiated w.r.t. x(j2)  # ✓ "j2" matches "j"

# These don't trigger sum collapse:
sum(i, x(i)) differentiated w.r.t. x(a1)  # ✗ "a1" doesn't match "i"
```

**Solution:** Use consistent naming: symbolic indices like "i", "j", concrete indices like "i1", "i2", "j1", "j2".

## Backward Compatibility

### Guaranteed Compatibility

1. **Default Parameter:** `wrt_indices=None` is the default, preserving original behavior for scalar-only models.

2. **Scalar Variables:** If your model has no indexed variables, all behavior is unchanged.

3. **API Signature:** No existing function signatures changed. Only an optional parameter was added.

### What Changed

1. **Semantics:** `d/dx x(i)` now correctly returns 0 (was incorrectly 1 before).

2. **Sum Differentiation:** Sums now collapse when appropriate, producing more efficient expressions.

3. **Gradient Computation:** Now computes correct sparse derivatives for indexed variables.

## Testing

All existing tests continue to pass. New tests were added:

- **36 new tests** in `tests/ad/test_index_aware_diff.py`
- **Updated tests** in `test_gradient.py` to verify correct collapse behavior
- **312 total tests** now passing

## FAQ

**Q: Do I need to change my code?**

A: No, if you're using high-level functions like `compute_objective_gradient()`. They handle index-aware differentiation automatically.

**Q: When should I use `wrt_indices`?**

A: Only if you're calling `differentiate_expr()` directly and need to differentiate w.r.t. a specific indexed variable instance.

**Q: What if I have both scalar x and indexed x(i)?**

A: Don't do this. They're treated as different variables. Choose one form consistently.

**Q: Why does d/dx x(i) = 0?**

A: Because `d/dx` means "differentiate w.r.t. scalar x" (no indices). The indexed variable `x(i)` is different from scalar `x`, so the derivative is 0.

**Q: How do I differentiate w.r.t. x(i1) instead?**

A: Use `differentiate_expr(expr, "x", ("i1",))` to specify indices.

**Q: Will sum collapse always work?**

A: The collapse heuristic works for standard naming conventions (i, i1, i2, j, j1, j2, etc.). It may not work for unusual naming patterns.

**Q: What if my indexed variable has multiple indices?**

A: Fully supported. Use tuples: `wrt_indices=("i1", "j2")` for `x(i1, j2)`.

## References

- **Implementation:** `src/ad/derivative_rules.py`
- **Tests:** `tests/ad/test_index_aware_diff.py`
- **Planning Document:** `docs/planning/SPRINT_2_7_5_PLAN.md`
- **Architecture:** `docs/ad_architecture.md`

## Contact

For questions or issues, please file an issue in the project repository.
