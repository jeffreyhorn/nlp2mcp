# Issue: Objective Expression Not Found After Model Normalization

## Summary

The `find_objective_expression()` function in `src/ad/gradient.py` fails to locate objective expressions after `normalize_model()` is called on the ModelIR. This prevents integration tests from running and blocks the full end-to-end NLP → AD pipeline workflow.

## Status

- **Severity**: High - Blocks integration testing and end-to-end workflows
- **Component**: Sprint 1 (Parser & IR)
- **Affects**: Sprint 2 integration tests
- **Discovered**: Sprint 2 Day 10 (2025-10-29)

## Problem Description

### What's Happening

When parsing GAMS models where the objective variable is defined by an equation (common pattern), the objective expression cannot be found after normalization:

```gams
Variables
    x
    obj ;

Equations
    objective ;

objective..
    obj =e= x;

Solve model using NLP minimizing obj ;
```

**Expected behavior:**
- `find_objective_expression()` should return the expression `x` (from the RHS of the objective equation)

**Actual behavior:**
- `find_objective_expression()` raises:
  ```
  ValueError: Objective variable 'obj' is not defined by any equation.
  ObjectiveIR.expr is None and no defining equation found.
  ```

### Root Cause Analysis

The issue occurs because:

1. **Parser creates ObjectiveIR with `expr=None`:**
   - When parsing `Solve model using NLP minimizing obj`, the parser sets `ObjectiveIR.objvar = "obj"` but `ObjectiveIR.expr = None`
   - The actual expression is in a separate equation: `objective.. obj =e= x`

2. **Normalization restructures equations:**
   - `normalize_model()` processes equations and converts them to canonical form
   - The relationship between the objective variable and its defining equation is lost or changed
   - The equation structure may change from `obj =e= x` to `obj - x =e= 0` or similar

3. **find_objective_expression() search fails:**
   - Function searches `model_ir.equations` for equations defining `objvar`
   - After normalization, the equation structure doesn't match the search pattern
   - Function looks for `SymbolRef(objvar)` on LHS or RHS but can't find it

### Code Location

**File:** `src/ad/gradient.py:79-142`

```python
def find_objective_expression(model_ir: ModelIR) -> Expr:
    """Find the objective function expression from ModelIR."""
    if model_ir.objective is None:
        raise ValueError("ModelIR has no objective defined")

    objective = model_ir.objective

    # Case 1: Explicit expression
    if objective.expr is not None:
        return objective.expr

    # Case 2: Find defining equation
    objvar = objective.objvar

    # Search through equations for one that defines objvar
    for _eq_name, eq_def in model_ir.equations.items():
        # Skip indexed equations (objective must be scalar)
        if eq_def.domain:
            continue

        # Check if this equation defines the objective variable
        lhs, rhs = eq_def.lhs_rhs

        # Check if lhs is the objvar (then use rhs as expression)
        if _is_symbol_ref(lhs, objvar):
            return rhs

        # Check if rhs is the objvar (then use lhs as expression)
        if _is_symbol_ref(rhs, objvar):
            return lhs

    # No defining equation found
    raise ValueError(
        f"Objective variable '{objvar}' is not defined by any equation. "
        f"ObjectiveIR.expr is None and no defining equation found. "
        f"Available equations: {list(model_ir.equations.keys())}"
    )
```

## Impact

### Affected Tests

All 15 integration tests in `tests/ad/test_integration.py` are currently **SKIPPED**:

1. **TestScalarModels** (2 tests):
   - `test_scalar_nlp_basic` - Tests scalar model with objective `obj =e= x`
   - `test_bounds_nlp_basic` - Tests scalar model with bounds

2. **TestIndexedModels** (2 tests):
   - `test_simple_nlp_indexed` - Tests indexed model with sum objective
   - `test_indexed_balance_model` - Tests indexed constraints

3. **TestNonlinearFunctions** (1 test):
   - `test_nonlinear_mix_model` - Tests exp, log, sqrt, trig functions

4. **TestJacobianStructure** (2 tests):
   - `test_jacobian_sparsity_pattern` - Tests sparse Jacobian structure
   - `test_jacobian_by_names` - Tests Jacobian querying by names

5. **TestGradientStructure** (2 tests):
   - `test_gradient_by_name` - Tests gradient querying by variable name
   - `test_gradient_all_components` - Tests all gradient components exist

6. **TestAPIErrorHandling** (2 tests):
   - `test_empty_model_error` - Tests error handling for empty models
   - `test_no_objective_error` - Tests error handling when objective missing

7. **TestConsistency** (2 tests):
   - `test_mapping_consistency` - Tests index mapping consistency
   - `test_all_variables_have_gradients` - Tests gradient completeness

8. **TestEndToEndWorkflow** (2 tests):
   - `test_complete_workflow_scalar` - End-to-end scalar model test
   - `test_complete_workflow_indexed` - End-to-end indexed model test

### Example Files Affected

All example GAMS files use the objective-defined-by-equation pattern:

- `examples/scalar_nlp.gms`
- `examples/bounds_nlp.gms`
- `examples/simple_nlp.gms`
- `examples/indexed_balance.gms`
- `examples/nonlinear_mix.gms`

## Reproduction Steps

1. **Create a simple GAMS model:**
   ```gams
   Variables x, obj;
   Equations objective;
   objective.. obj =e= x;
   Model test /all/;
   Solve test using NLP minimizing obj;
   ```

2. **Parse and normalize:**
   ```python
   from src.ir.parser import parse_model_file
   from src.ir.normalize import normalize_model
   from src.ad.gradient import find_objective_expression
   
   model_ir = parse_model_file("examples/scalar_nlp.gms")
   normalize_model(model_ir)  # Modifies model_ir in place
   
   # This will fail:
   obj_expr = find_objective_expression(model_ir)
   ```

3. **Observe error:**
   ```
   ValueError: Objective variable 'obj' is not defined by any equation.
   ObjectiveIR.expr is None and no defining equation found.
   Available equations: ['objective', 'stationarity']
   ```

## Investigation Needed

### Questions to Answer

1. **What does `normalize_model()` do to equation structure?**
   - How are equations transformed?
   - Where do normalized equations go (model_ir.equalities, model_ir.inequalities)?
   - Does it preserve the original equations dict?

2. **Where should we look for the objective equation?**
   - Original `model_ir.equations`?
   - Normalized `model_ir.equalities`?
   - Somewhere else?

3. **How should equation structure be matched?**
   - Current code looks for `SymbolRef(objvar)` on LHS or RHS
   - After normalization: `obj - x =e= 0`, does this still match?
   - Do we need to handle `BinaryOp('-', SymbolRef('obj'), ...)`?

4. **Should ObjectiveIR.expr be populated during parsing?**
   - Alternative approach: Parser could extract expression immediately
   - Pro: Avoids post-normalization search
   - Con: Requires more complex parsing logic

### Files to Examine

- `src/ir/normalize.py` - Understand normalization transformation
- `src/ir/model_ir.py` - Check ModelIR structure after normalization
- `src/ir/parser.py` - See how ObjectiveIR is created
- `src/ad/gradient.py` - Current search implementation

## Proposed Solutions

### Option 1: Fix find_objective_expression() to Search Normalized Structures

**Approach:** Update the search logic to look in the right places after normalization.

**Changes needed:**
```python
def find_objective_expression(model_ir: ModelIR) -> Expr:
    # ... existing code ...
    
    # Case 2: Find defining equation
    objvar = objective.objvar
    
    # Search in normalized equations (equalities + inequalities)
    all_equations = [
        *model_ir.equalities,
        *model_ir.inequalities,
    ]
    
    for eq_def in all_equations:
        # Skip indexed equations
        if eq_def.domain:
            continue
        
        # Check normalized form: could be "obj - expr =e= 0"
        if _equation_defines_variable(eq_def, objvar):
            return _extract_expression(eq_def, objvar)
    
    # Fallback: search original equations dict if still exists
    # ...
```

**Pros:**
- Minimal changes to existing code
- Works with current parsing approach

**Cons:**
- Need to understand all normalization transformations
- May be fragile if normalization changes

### Option 2: Populate ObjectiveIR.expr During Parsing

**Approach:** Have the parser extract the objective expression immediately when it encounters the defining equation.

**Changes needed in `src/ir/parser.py`:**
```python
# When processing equations, check if equation defines objective variable
if self.objective and self.objective.objvar:
    objvar = self.objective.objvar
    if equation_defines_variable(eq_def, objvar):
        # Extract expression and populate ObjectiveIR.expr
        self.objective.expr = extract_expression(eq_def, objvar)
```

**Pros:**
- Avoids post-normalization search entirely
- More robust to normalization changes
- Clearer separation of concerns

**Cons:**
- Requires parser to understand equation structure
- More complex parsing logic
- May need to handle forward references (equation before objective variable declared)

### Option 3: Preserve Original Equation Mapping

**Approach:** Keep a reference to original equations before normalization.

**Changes needed:**
```python
# In normalize_model():
model_ir.original_equations = dict(model_ir.equations)  # Preserve original

# In find_objective_expression():
# Search original_equations if normalized search fails
if hasattr(model_ir, 'original_equations'):
    for eq_name, eq_def in model_ir.original_equations.items():
        # ... search logic ...
```

**Pros:**
- Backwards compatible
- Simple fallback mechanism

**Cons:**
- Increases memory usage (duplicate equations)
- Doesn't address root cause
- Band-aid solution

### Option 4: Store Objective Expression Reference in Normalization

**Approach:** Have `normalize_model()` explicitly track and preserve objective expressions.

**Changes needed:**
```python
def normalize_model(model_ir: ModelIR):
    # Before normalization, extract objective expression if needed
    if model_ir.objective and not model_ir.objective.expr:
        objvar = model_ir.objective.objvar
        obj_expr = _find_and_extract_objective(model_ir.equations, objvar)
        model_ir.objective.expr = obj_expr
    
    # Continue with normalization...
```

**Pros:**
- Fixes issue at normalization time
- Objective expression always available post-normalization
- Clean separation of concerns

**Cons:**
- Couples normalization to objective handling
- May complicate normalization logic

## Recommended Solution

**Option 4** (Store Objective Expression Reference in Normalization) is recommended because:

1. **Fixes the root cause**: Ensures ObjectiveIR.expr is populated before equations are restructured
2. **Minimal impact**: Single change point in normalize_model()
3. **Robust**: Works regardless of how normalization transforms equations
4. **Clear semantics**: After normalization, ObjectiveIR.expr is guaranteed to be set

## Implementation Plan

1. **Add helper function to normalize.py:**
   ```python
   def _extract_objective_expression(equations: dict, objvar: str) -> Expr:
       """Extract objective expression from equations before normalization."""
       # Search logic (similar to current find_objective_expression)
       # ...
   ```

2. **Update normalize_model():**
   ```python
   def normalize_model(model_ir: ModelIR) -> None:
       # Extract objective expression BEFORE normalization
       if model_ir.objective and not model_ir.objective.expr:
           objvar = model_ir.objective.objvar
           model_ir.objective.expr = _extract_objective_expression(
               model_ir.equations, objvar
           )
       
       # Continue with existing normalization logic...
   ```

3. **Add tests:**
   - Test that objective is found before normalization
   - Test that ObjectiveIR.expr is populated after normalize_model()
   - Test with scalar and indexed objectives

4. **Enable integration tests:**
   - Remove `pytestmark` skip from `tests/ad/test_integration.py`
   - Verify all 15 tests pass

## Testing

### Unit Tests to Add

**File:** `tests/ir/test_normalize.py`

```python
def test_normalize_extracts_objective_expression():
    """Test that normalize_model() populates ObjectiveIR.expr."""
    model_ir = parse_model_file("examples/scalar_nlp.gms")
    
    # Before normalization: expr is None
    assert model_ir.objective.expr is None
    
    # After normalization: expr should be populated
    normalize_model(model_ir)
    assert model_ir.objective.expr is not None
    
    # Expression should be the RHS of objective equation
    # objective.. obj =e= x  -->  expr = VarRef('x')
    assert isinstance(model_ir.objective.expr, VarRef)
    assert model_ir.objective.expr.name == 'x'
```

### Integration Tests to Enable

Once fixed, remove skip marker from `tests/ad/test_integration.py` and verify:

- All 15 integration tests pass
- Full pipeline works: parse → normalize → compute_derivatives
- No timeouts or errors

## References

- **Original issue location**: `tests/ad/test_integration.py` (all tests skipped)
- **Error source**: `src/ad/gradient.py:79-142` (find_objective_expression)
- **Related code**: `src/ir/normalize.py` (normalization logic)
- **Example files**: `examples/*.gms` (all use objective-defined-by-equation pattern)
- **CHANGELOG entry**: Day 10 notes (2025-10-29)

## Additional Notes

- This is a **Sprint 1 issue** discovered during Sprint 2 integration testing
- The AD functionality itself (Sprint 2) works correctly when given a proper ModelIR
- This blocks end-to-end testing but doesn't affect Sprint 2 core deliverables
- Issue should be fixed before Sprint 3 (KKT synthesis) to enable full pipeline testing

## Related Issues

None yet - this is the first documented instance of this problem.

## Labels

- `bug`
- `sprint-1`
- `parser`
- `normalization`
- `priority: high`
- `blocked: integration-tests`
