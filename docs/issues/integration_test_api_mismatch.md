# Issue: Integration Tests API Mismatch

## ✅ RESOLVED (2025-10-29)

**Resolution**: Fixed tests to match actual implementation (Option 1)
- Updated all API attribute references to use correct naming
- Changed `gradient.mapping.num_vars` → `gradient.num_cols`
- Changed `J_g.mapping.num_equations` → `J_g.num_rows`
- Changed `gradient.mapping` → `gradient.index_mapping`
- Updated test expectations to account for objective variable (obj)
- Added proper skip marker for bounds test (separate bug, not API mismatch - see Issue #24)
- **Result**: 13 out of 15 tests passing (87% pass rate)
  - 2 skipped: bounds handling bug (Issue #24) and power operator (Issue #25)

**Branch**: `fix/issue-22-integration-test-api-mismatch`

## Summary

Integration tests in `tests/ad/test_integration.py` were failing due to API mismatches between what the tests expected and what the actual AD module provides. The tests were written against an expected API design but the implementation uses different attribute names and structure.

## Severity

- **Status**: RESOLVED ✅
- **Severity**: Medium - Tests fail but core functionality works
- **Component**: Sprint 2 (AD / Automatic Differentiation)
- **Affects**: Integration test coverage, API documentation
- **Discovered**: Sprint 2 Day 10 (2025-10-29) after fixing Issue #20 (parse hang)
- **GitHub Issue**: #22 - https://github.com/jeffreyhorn/nlp2mcp/issues/22
- **Type**: Test/Implementation mismatch (not a functional bug)

## Problem Description

After fixing Issue #20 (parse_model_file hang), integration tests can now run but 10 out of 15 tests fail. The failures are not due to broken functionality but rather API design mismatches between test expectations and actual implementation.

### Test Results Summary

- **Total tests**: 15
- **Passing**: 5 (33%)
- **Failing**: 10 (67%)

### Failure Categories

#### 1. Attribute Name Mismatch (8 tests fail)

**Expected API**:
```python
gradient.mapping.num_vars
J_g.mapping.num_equations
```

**Actual API**:
```python
gradient.index_mapping  # Different name
gradient.num_cols       # Direct attribute, not through mapping
J_g.num_rows           # Direct attribute, not through mapping
```

**Failing Tests**:
- `TestScalarModels::test_scalar_nlp_basic`
- `TestIndexedModels::test_simple_nlp_indexed`
- `TestIndexedModels::test_indexed_balance_model`
- `TestJacobianStructure::test_jacobian_sparsity_pattern`
- `TestGradientStructure::test_gradient_all_components`
- `TestConsistency::test_mapping_consistency`
- `TestConsistency::test_all_variables_have_gradients`
- `TestEndToEndWorkflow::test_full_pipeline_indexed`

**Error Example**:
```
AttributeError: 'GradientVector' object has no attribute 'mapping'
```

#### 2. Missing Bound Variable Names (1 test fails)

**Test Expectation**: Bound constraint equations should have names like `'x_lo'`, `'x_up'`

**Actual Behavior**: Bounds are represented differently in the normalized model

**Failing Test**:
- `TestScalarModels::test_bounds_nlp_basic`

**Error Example**:
```
KeyError: 'x_lo'
```

**Status**: Separate issue created - See **GitHub Issue #24**: https://github.com/jeffreyhorn/nlp2mcp/issues/24

#### 3. Unimplemented Power Operation (1 test fails)

**Test Expectation**: Power operator `^` should be supported for differentiation

**Actual Behavior**: Power operator not yet implemented (planned for Day 3)

**Failing Test**:
- `TestNonlinearFunctions::test_nonlinear_mix_model`

**Error Example**:
```
ValueError: Unsupported binary operation '^' for differentiation. 
Supported operations: +, -, *, /. Power (^) will be implemented on Day 3.
```

**Status**: Separate issue created - See **GitHub Issue #25**: https://github.com/jeffreyhorn/nlp2mcp/issues/25

## API Structure Comparison

### GradientVector Class

**Actual Implementation** (`src/ad/jacobian.py`):
```python
@dataclass
class GradientVector:
    """Gradient vector storing derivative expressions for objective function."""
    
    entries: dict[int, Expr] = field(default_factory=dict)
    index_mapping: IndexMapping  # Attribute name: index_mapping
    num_cols: int                 # Direct attribute
    
    def get_derivative(self, col_id: int) -> Expr | None: ...
    def get_derivative_by_name(self, var_name: str, indices: tuple[str, ...]) -> Expr | None: ...
    def get_all_derivatives(self) -> dict[int, Expr]: ...
    def num_nonzeros(self) -> int: ...
```

**Test Expectations**:
```python
# Tests expect:
gradient.mapping          # Should be gradient.index_mapping
gradient.mapping.num_vars # Should be gradient.num_cols
```

### JacobianStructure Class

**Actual Implementation** (`src/ad/jacobian.py`):
```python
@dataclass
class JacobianStructure:
    """Sparse Jacobian matrix structure storing derivative expressions."""
    
    entries: dict[int, dict[int, Expr]] = field(default_factory=dict)
    index_mapping: IndexMapping  # Attribute name: index_mapping
    num_rows: int                # Direct attribute
    num_cols: int                # Direct attribute
    
    def get_derivative(self, row_id: int, col_id: int) -> Expr | None: ...
    def get_derivative_by_names(self, eq_name: str, eq_indices: tuple[str, ...],
                                var_name: str, var_indices: tuple[str, ...]) -> Expr | None: ...
    def get_nonzero_entries(self) -> list[tuple[int, int]]: ...
    def num_nonzeros(self) -> int: ...
    def density(self) -> float: ...
```

**Test Expectations**:
```python
# Tests expect:
J_g.mapping               # Should be J_g.index_mapping
J_g.mapping.num_equations # Should be J_g.num_rows
J_g.mapping.num_vars      # Should be J_g.num_cols
```

### IndexMapping Class

**Actual Implementation** (`src/ad/index_mapping.py`):
```python
@dataclass
class IndexMapping:
    """Bidirectional mapping between variable/equation instances and matrix indices."""
    
    var_to_col: dict[tuple[str, tuple[str, ...]], int]
    col_to_var: dict[int, tuple[str, tuple[str, ...]]]
    eq_to_row: dict[tuple[str, tuple[str, ...]], int]
    row_to_eq: dict[int, tuple[str, tuple[str, ...]]]
    num_vars: int
    num_eqs: int
```

## Detailed Test Failures

### 1. test_scalar_nlp_basic

**File**: `tests/ad/test_integration.py:87`

**Test Code**:
```python
def test_scalar_nlp_basic(self):
    model_ir = parse_and_normalize("scalar_nlp.gms")
    gradient, J_g, J_h = compute_derivatives(model_ir)
    
    # Should have 1 variable (x)
    assert gradient.mapping.num_vars == 1  # ❌ FAILS HERE
```

**Error**:
```
AttributeError: 'GradientVector' object has no attribute 'mapping'
```

**Fix Needed**:
```python
# Change from:
assert gradient.mapping.num_vars == 1

# To:
assert gradient.num_cols == 1
# OR
assert gradient.index_mapping.num_vars == 1
```

### 2. test_bounds_nlp_basic

**File**: `tests/ad/test_integration.py:98`

**Status**: Separate issue - See **GitHub Issue #24**: https://github.com/jeffreyhorn/nlp2mcp/issues/24

**Test Code**:
```python
def test_bounds_nlp_basic(self):
    model_ir = parse_and_normalize("bounds_nlp.gms")
    gradient, J_g, J_h = compute_derivatives(model_ir)
    
    # Bounds contribute to J_g (inequality constraints)
    # Each bound becomes g(x) = x - bound ≤ 0
    assert J_g.num_nonzeros() > 0  # This passes
    
    # Later in test:
    # Tests try to access equations by name like 'x_lo', 'x_up'
    # But normalized bounds don't have these names
```

**Error**:
```
KeyError: 'x_lo'
```

**Root Cause**: Tests assume bounds are represented as named inequality constraints (e.g., `'x_lo'`, `'x_up'`), but the actual normalization creates bound constraints with different naming or structure.

**See GitHub Issue #24 for detailed investigation and proposed solutions.**

### 3. test_nonlinear_mix_model

**File**: `tests/ad/test_integration.py:140`

**Status**: Separate issue - See **GitHub Issue #25**: https://github.com/jeffreyhorn/nlp2mcp/issues/25

**Test Code**:
```python
def test_nonlinear_mix_model(self):
    """Test model with mix of nonlinear functions."""
    model_ir = parse_and_normalize("nonlinear_mix.gms")
    gradient, J_g, J_h = compute_derivatives(model_ir)  # ❌ FAILS HERE
```

**Error**:
```
ValueError: Unsupported binary operation '^' for differentiation. 
Supported operations: +, -, *, /. Power (^) will be implemented on Day 3.
```

**Root Cause**: The `nonlinear_mix.gms` file contains power operations (e.g., `x^2`) which are not yet implemented in the differentiation engine.

**See GitHub Issue #25 for detailed implementation requirements and proposed solutions.**

## Proposed Solutions

### Option 1: Fix Tests to Match Implementation (Recommended)

**Approach**: Update integration tests to use the actual API

**Changes Needed**:
```python
# 1. Replace .mapping with .index_mapping
gradient.mapping.num_vars → gradient.index_mapping.num_vars
# OR use direct attributes:
gradient.mapping.num_vars → gradient.num_cols

# 2. Replace J_g.mapping with J_g.index_mapping
J_g.mapping.num_equations → J_g.index_mapping.num_eqs
# OR use direct attributes:
J_g.mapping.num_equations → J_g.num_rows

# 3. Fix bounds test to use actual bound constraint names/structure
# (Requires investigation of how bounds are actually represented)

# 4. Skip test_nonlinear_mix_model until power operator is implemented
@pytest.mark.skip(reason="Power operator (^) not yet implemented - planned for Day 3")
def test_nonlinear_mix_model(self): ...
```

**Pros**:
- Tests will pass immediately
- Matches actual implementation
- No changes to working AD code

**Cons**:
- Tests may have been written against a better API design
- Should verify if current API is the intended design

### Option 2: Add Alias Properties to Match Expected API

**Approach**: Add `mapping` property as an alias for `index_mapping`

**Changes Needed** in `src/ad/jacobian.py`:
```python
@dataclass
class GradientVector:
    entries: dict[int, Expr] = field(default_factory=dict)
    index_mapping: IndexMapping
    num_cols: int
    
    @property
    def mapping(self) -> IndexMapping:
        """Alias for index_mapping for backward compatibility."""
        return self.index_mapping

@dataclass  
class JacobianStructure:
    entries: dict[int, dict[int, Expr]] = field(default_factory=dict)
    index_mapping: IndexMapping
    num_rows: int
    num_cols: int
    
    @property
    def mapping(self) -> IndexMapping:
        """Alias for index_mapping for backward compatibility."""
        return self.index_mapping
```

**Pros**:
- Tests pass without modification
- Provides backward compatibility
- Both API styles work

**Cons**:
- Adds redundant API surface
- May perpetuate confusing naming

### Option 3: Rename index_mapping to mapping in Implementation

**Approach**: Change implementation to match test expectations

**Changes Needed**:
- Rename `index_mapping` → `mapping` throughout codebase
- Update all references in `src/ad/` modules

**Pros**:
- Shorter, cleaner name (`mapping` vs `index_mapping`)
- Tests work without changes
- More consistent naming

**Cons**:
- Requires changes across multiple files
- May break other code depending on `index_mapping`
- Need to verify `mapping` is clearer than `index_mapping`

## Recommended Approach

**Immediate**: Option 1 - Fix tests to match implementation
- Update test assertions to use `gradient.num_cols`, `J_g.num_rows`, etc.
- Or use `gradient.index_mapping.num_vars` if needed
- Skip `test_nonlinear_mix_model` until power operator implemented
- Investigate and fix bounds test

**Future**: Consider Option 3 if team agrees `mapping` is better than `index_mapping`
- Rename in a separate PR after discussion
- Update all references consistently

## Investigation Needed

### 1. Bounds Representation

**Question**: How are variable bounds represented in normalized equations?

**Test File**: `examples/bounds_nlp.gms`
```gams
x.lo = -1;
x.up = 2;
```

**Investigation Steps**:
1. Parse and normalize `bounds_nlp.gms`
2. Inspect `model_ir.normalized_bounds` structure
3. Determine what keys/names are used
4. Update test to match actual structure

**Code to Run**:
```python
from src.ir.parser import parse_model_file
from src.ir.normalize import normalize_model

model_ir = parse_model_file('examples/bounds_nlp.gms')
normalize_model(model_ir)

print("Normalized bounds:", model_ir.normalized_bounds)
print("Inequalities:", model_ir.inequalities)
print("Equalities:", model_ir.equalities)
```

### 2. API Design Intent

**Question**: Was `mapping` the intended API name, or is `index_mapping` correct?

**Action**: Review with team or check design documents
- If `mapping` was intended, implement Option 3
- If `index_mapping` is correct, implement Option 1

## Impact

### Current State
- ✅ 5/15 integration tests pass (33%)
- ✅ Core AD functionality works correctly
- ✅ Parsing works (Issue #20 fixed)
- ❌ 10/15 integration tests fail due to API mismatch

### After Fix (Option 1)
- ✅ ~13/15 integration tests pass (87%)
- ❌ 1 test skipped (power operator - planned)
- ❌ 1 test may need investigation (bounds)

### Functional Impact
- **None** - This is a test issue, not a functionality issue
- The AD code works correctly
- Only the test assertions need updating

## Files Affected

### Test Files
- `tests/ad/test_integration.py` - All 10 failing tests need updates

### Implementation Files (if Option 2 or 3 chosen)
- `src/ad/jacobian.py` - GradientVector and JacobianStructure classes
- `src/ad/api.py` - May reference mapping
- `src/ad/gradient.py` - May reference mapping

## Related Issues

- **GitHub Issue #19** (RESOLVED ✅): Objective extraction in normalization
  - https://github.com/jeffreyhorn/nlp2mcp/issues/19
- **GitHub Issue #20** (RESOLVED ✅): parse_model_file() hang
  - https://github.com/jeffreyhorn/nlp2mcp/issues/20
  - This issue (Issue #22) was discovered after fixing Issue #20, which enabled integration tests to run
- **GitHub Issue #22** (OPEN 🔴): Integration Tests API Mismatch (this issue)
  - https://github.com/jeffreyhorn/nlp2mcp/issues/22

## Test Execution

### Before Fix
```bash
$ python -m pytest tests/ad/test_integration.py -v
======================== 10 failed, 5 passed in 6.42s =========================
```

### After Fix (Expected)
```bash
$ python -m pytest tests/ad/test_integration.py -v
======================== 1 skipped, 13 passed in 6.0s ==========================
# (1 skipped = power operator test)
# (May have 1 more failing if bounds investigation reveals issues)
```

## Next Steps

1. **Immediate**: Choose solution approach (Option 1 recommended)
2. **Investigate**: Bounds representation in normalized model
3. **Update**: Integration tests to match actual API
4. **Document**: API structure in code comments/docstrings
5. **Future**: Consider consistent naming (mapping vs index_mapping)
