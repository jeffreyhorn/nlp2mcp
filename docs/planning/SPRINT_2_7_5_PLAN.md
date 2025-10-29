# Sprint 2 - Day 7.5: Index-Aware Differentiation Enhancement

**Duration:** 1 day (following Day 7 completion)  
**Goal:** Implement index-aware differentiation to properly distinguish between different instances of indexed variables (e.g., x(i1) vs x(i2)) in symbolic differentiation.

## Problem Statement

### Current Limitation

The existing symbolic differentiation implementation in `src/ad/derivative_rules.py` differentiates expressions with respect to variable **names** only, not specific variable **instances**. This causes all indexed variable instances to share the same symbolic derivative.

**Example of the Problem:**

```python
# Expression: sum(i, x(i))  where i ∈ {i1, i2, i3}
# Current behavior:
∂(sum(i, x(i)))/∂x → sum(i, 1)  # Same for ALL x instances

# Correct behavior should be:
∂(sum(i, x(i)))/∂x(i1) → 1  # Only the i1 term contributes
∂(sum(i, x(i)))/∂x(i2) → 1  # Only the i2 term contributes
∂(sum(i, x(i)))/∂x(i3) → 1  # Only the i3 term contributes
```

**Impact:**

- Gradients for indexed variables are incorrect (over-generalized)
- Jacobians will have incorrect sparsity patterns
- Derivatives don't properly capture which specific variable instances affect which equations
- Loss of precision in sparse derivative computation

### Root Cause

1. `differentiate_expr(expr, wrt_var)` signature only accepts variable name string
2. `_diff_varref()` compares variable names only: `expr.name == wrt_var`
3. No mechanism to distinguish VarRef("x", ("i1",)) from VarRef("x", ("i2",))

### Affected Code

- `src/ad/gradient.py`: Lines 185 and 244
- `src/ad/derivative_rules.py`: `differentiate_expr()` and `_diff_varref()`
- All differentiation call sites throughout the codebase

---

## Goals

1. **Extend differentiation API** to support index-aware variable matching
2. **Implement index matching logic** for VarRef nodes
3. **Maintain backward compatibility** with existing scalar variable differentiation
4. **Update all call sites** to use enhanced differentiation
5. **Validate correctness** with comprehensive tests

---

## Design Overview

### Proposed API Change

```python
# Current signature:
def differentiate_expr(expr: Expr, wrt_var: str) -> Expr:
    """Differentiate expression w.r.t. variable name."""
    ...

# New signature:
def differentiate_expr(
    expr: Expr,
    wrt_var: str,
    wrt_indices: tuple[str, ...] | None = None
) -> Expr:
    """
    Differentiate expression w.r.t. a specific variable instance.
    
    Args:
        expr: Expression to differentiate
        wrt_var: Variable name (e.g., "x")
        wrt_indices: Optional variable indices (e.g., ("i1",) or ("i1", "j2"))
                     If None, matches any variable with name wrt_var (backward compatible)
    
    Returns:
        Derivative expression
    """
    ...
```

### Index Matching Logic

The key change is in `_diff_varref()`:

```python
def _diff_varref(expr: VarRef, wrt_var: str, wrt_indices: tuple[str, ...] | None = None) -> Const:
    """
    Derivative of a variable reference with index-aware matching.
    
    Rules:
    1. Variable names must match: expr.name == wrt_var
    2. If wrt_indices is None: Match any indices (backward compatible, scalar variables)
    3. If wrt_indices is provided:
       - expr.indices must equal wrt_indices exactly
       - VarRef("x", ("i1",)) matches wrt_var="x", wrt_indices=("i1",)
       - VarRef("x", ("i2",)) does NOT match wrt_var="x", wrt_indices=("i1",)
    
    Returns:
        Const(1.0) if matches, Const(0.0) otherwise
    """
    # Name must match
    if expr.name != wrt_var:
        return Const(0.0)
    
    # Index matching
    if wrt_indices is None:
        # No indices specified: match any (backward compatible)
        return Const(1.0)
    
    # Indices specified: must match exactly
    if expr.indices == wrt_indices:
        return Const(1.0)
    else:
        return Const(0.0)
```

### Backward Compatibility

- Existing code calling `differentiate_expr(expr, "x")` continues to work unchanged
- Scalar variables (no indices) are unaffected
- Default `wrt_indices=None` matches current behavior

---

## Tasks

### Phase 1: Core Differentiation API Enhancement

**Task 1.1: Update differentiate_expr() signature**
- Modify `differentiate_expr()` in `src/ad/derivative_rules.py`
- Add `wrt_indices: tuple[str, ...] | None = None` parameter
- Update docstring with examples
- Thread `wrt_indices` through to all internal differentiation functions

**Task 1.2: Update _diff_varref() with index matching**
- Implement index comparison logic
- Handle `wrt_indices=None` case (backward compatible)
- Handle exact index match case
- Handle index mismatch case (return 0)

**Task 1.3: Update _diff_symbolref() with index matching**
- SymbolRef doesn't have indices, so behavior unchanged
- Update signature for consistency: `_diff_symbolref(expr, wrt_var, wrt_indices=None)`
- Document that SymbolRef always ignores wrt_indices

**Task 1.4: Thread wrt_indices through derivative rules**
- Update all `_diff_*()` function signatures to accept `wrt_indices`
- Pass `wrt_indices` to recursive `differentiate_expr()` calls
- Update: `_diff_binary()`, `_diff_unary()`, `_diff_call()`, `_diff_sum()`
- Ensure chain rule propagates indices correctly

### Phase 2: Update Gradient Computation

**Task 2.1: Update compute_objective_gradient()**
- Change line 185 from:
  ```python
  derivative = differentiate_expr(obj_expr, var_name)
  ```
  To:
  ```python
  derivative = differentiate_expr(obj_expr, var_name, indices)
  ```
- Now each variable instance gets its own specific derivative

**Task 2.2: Update compute_gradient_for_expression()**
- Change line 244 similarly
- Pass indices to differentiation call

### Phase 3: Update Sum Differentiation (Special Case)

**Task 3.1: Review _diff_sum() implementation**
- Sum differentiation is special: d/dx(sum(i, f(i))) = sum(i, df(i)/dx)
- When differentiating w.r.t. x(i1), the sum still ranges over all i
- But the body derivative should recognize when index variables match
- This may require sum index variable tracking

**Task 3.2: Implement sum index awareness**
- Track which index variables are bound by enclosing sums
- When matching VarRef("x", ("i",)), check if "i" is a sum index variable
- If "i" is a sum index: derivative is 1 within that sum's scope
- If "i" is a concrete index: match exactly against wrt_indices

### Phase 4: Testing

**Task 4.1: Add unit tests for index-aware VarRef differentiation**
- Test exact index match: `d/dx(i1) VarRef("x", ("i1",))` → 1
- Test index mismatch: `d/dx(i1) VarRef("x", ("i2",))` → 0
- Test no indices (backward compat): `d/dx VarRef("x")` → 1
- Test multi-dimensional: `d/dx(i1,j2) VarRef("x", ("i1","j2"))` → 1

**Task 4.2: Add tests for sum with index-aware differentiation**
- Test `d/dx(i1) sum(i, x(i))` → 1 (only i1 term contributes)
- Test `d/dx(i2) sum(i, x(i))` → 1 (only i2 term contributes)
- Test `d/dx sum(i, x(i))` (no indices) → sum(i, 1) (all terms)

**Task 4.3: Add gradient computation tests**
- Test objective: `min sum(i, x(i)^2)` with i={i1,i2}
- Verify gradient: ∂f/∂x(i1) = 2*x(i1), ∂f/∂x(i2) = 2*x(i2)
- Not: ∂f/∂x(i1) = sum(i, 2*x(i)) (current incorrect behavior)

**Task 4.4: Update existing tests**
- Review all tests in `tests/ad/test_gradient.py`
- Fix test expectations to match correct behavior
- Update test_mixed_scalar_and_indexed expectations

### Phase 5: Documentation

**Task 5.1: Update derivative_rules.py docstrings**
- Document new `wrt_indices` parameter
- Add examples showing index-aware matching
- Explain backward compatibility

**Task 5.2: Update gradient.py docstrings**
- Remove "Index-Aware Differentiation (Limitation)" section
- Add "Index-Aware Differentiation (Implemented)" section
- Document how to use indices in differentiation

**Task 5.3: Update CHANGELOG.md**
- Document breaking change (signature extension)
- Document new functionality
- Provide migration guide (though default parameter makes it backward compatible)

**Task 5.4: Create migration guide**
- Document in `docs/migration/index_aware_differentiation.md`
- Show before/after code examples
- Explain when to use wrt_indices parameter

---

## Deliverables

1. **Updated `src/ad/derivative_rules.py`**
   - Extended `differentiate_expr()` signature with `wrt_indices` parameter
   - Index-aware `_diff_varref()` implementation
   - All derivative rules threaded with `wrt_indices`

2. **Updated `src/ad/gradient.py`**
   - `compute_objective_gradient()` uses index-aware differentiation
   - `compute_gradient_for_expression()` uses index-aware differentiation
   - Removed TODO comments, replaced with implementation

3. **New test suite additions**
   - `tests/ad/test_index_aware_differentiation.py` (15-20 tests)
   - Updated `tests/ad/test_gradient.py` expectations

4. **Documentation**
   - Updated docstrings throughout
   - Migration guide
   - CHANGELOG entry

5. **Validation**
   - All existing 267 tests still pass
   - New tests demonstrate correct index-aware behavior
   - Gradient computation produces correct sparse derivatives

---

## Acceptance Criteria

### Functional Requirements

1. **Index-aware VarRef matching works correctly**
   - ✅ `d/dx(i1) VarRef("x", ("i1",))` returns Const(1.0)
   - ✅ `d/dx(i1) VarRef("x", ("i2",))` returns Const(0.0)
   - ✅ `d/dx VarRef("x", ("i1",))` returns Const(1.0) (backward compat)

2. **Sum differentiation is index-aware**
   - ✅ `d/dx(i1) sum(i, x(i))` returns Const(1.0), not sum(i, 1)
   - ✅ Each sum term contributes only when its index matches

3. **Gradient computation uses index-aware differentiation**
   - ✅ Each variable instance gets its own derivative
   - ✅ Sparse Jacobian patterns are correct
   - ✅ No over-generalization of derivatives

4. **Backward compatibility maintained**
   - ✅ Existing calls without `wrt_indices` work unchanged
   - ✅ Scalar variables unaffected
   - ✅ All existing tests pass

### Quality Requirements

5. **Test coverage**
   - ✅ 15-20 new tests for index-aware differentiation
   - ✅ Updated expectations in existing tests
   - ✅ All 280+ tests passing

6. **Documentation**
   - ✅ All docstrings updated with examples
   - ✅ CHANGELOG documents changes
   - ✅ Migration guide available

7. **Code quality**
   - ✅ mypy type checking passes
   - ✅ ruff linting passes
   - ✅ No performance regression

### Mathematical Correctness

8. **Example validation: sum(i, x(i)) where i ∈ {i1, i2}**
   ```
   ∂(sum(i, x(i)))/∂x(i1) = 1  ✅ (only i1 contributes)
   ∂(sum(i, x(i)))/∂x(i2) = 1  ✅ (only i2 contributes)
   ```

9. **Example validation: sum(i, x(i)^2) where i ∈ {i1, i2}**
   ```
   ∂(sum(i, x(i)^2))/∂x(i1) = 2*x(i1)  ✅ (not sum(i, 2*x(i)))
   ∂(sum(i, x(i)^2))/∂x(i2) = 2*x(i2)  ✅ (not sum(i, 2*x(i)))
   ```

10. **Example validation: nested sums**
    ```
    Expression: sum(i, sum(j, x(i,j)^2))
    ∂f/∂x(i1,j1) = 2*x(i1,j1)  ✅ (not sum(i, sum(j, 2*x(i,j))))
    ```

---

## Implementation Notes

### Edge Cases to Handle

1. **Sum with symbolic indices**
   - `sum(i, x(i))` when differentiating w.r.t. `x` with no indices
   - Should maintain current behavior: sum(i, 1) for backward compatibility

2. **Nested sums with same index name**
   - `sum(i, sum(i, x(i)))` (should be flagged as error? or inner i shadows outer?)
   - Document behavior clearly

3. **Mixed indexed and scalar variables**
   - Expression with both VarRef("y") and VarRef("x", ("i",))
   - Ensure both are handled correctly

4. **Empty index tuples**
   - VarRef("x", ()) vs VarRef("x") 
   - Should be treated identically

### Testing Strategy

1. **Unit tests** for core differentiation logic
2. **Integration tests** for gradient computation
3. **Regression tests** to ensure backward compatibility
4. **Mathematical validation tests** with known correct answers

### Performance Considerations

- Index comparison is O(k) where k = number of indices (typically 1-3)
- Minimal performance impact expected
- Profile if needed, optimize if necessary

---

## Timeline Estimate

- **Phase 1 (Core API):** 3 hours
- **Phase 2 (Gradient update):** 1 hour  
- **Phase 3 (Sum special case):** 2 hours
- **Phase 4 (Testing):** 2 hours
- **Phase 5 (Documentation):** 1 hour

**Total: ~1 full working day**

---

## Success Metrics

- All 280+ tests passing (including new tests)
- Correct sparse derivatives demonstrated in tests
- Zero performance regression
- Clean documentation of new feature
- No breaking changes for existing code (backward compatible)

---

## Future Work (Out of Scope)

- **Symbolic index expressions**: Differentiating w.r.t. `x(i+1)` or `x(f(i))`
- **Index aliasing**: Handling when `i` and `j` represent the same set
- **Partial index matching**: Matching `x(i,j)` when differentiating w.r.t. `x(i,_)`
- **Automatic index simplification**: Recognizing when sum can be eliminated

These features can be added in future sprints if needed.

---

## References

- Current implementation: `src/ad/derivative_rules.py`
- Current limitations documented in: `src/ad/gradient.py` (module docstring)
- Related: Day 5 Sum differentiation, Day 6 Index mapping
