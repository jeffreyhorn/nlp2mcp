# Sprint 3 Preparation Plan

**Purpose:** Implement all process improvements identified in Sprint 2 Retrospective before Sprint 3 begins  
**Timeline:** Complete before Sprint 3 Day 1  
**Goal:** Start Sprint 3 with improved processes, better tooling, and clearer architecture to avoid Sprint 2's integration issues

**Key Insight from Sprint 2:** Integration issues discovered on Day 9 could have been caught on Day 2-3 with better architecture documentation and early integration testing.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies |
|---|------|----------|-----------|--------------|
| 1 | Create Architecture Diagram | Critical | 3 hours | None |
| 2 | Create Parser Output Reference | Critical | 2 hours | None |
| 3 | Refactor Test Organization | High | 4 hours | None |
| 4 | Add API Contract Tests | High | 2 hours | Task 3 |
| 5 | Create Early Integration Smoke Test | Critical | 1 hour | None |
| 6 | Implement Test Pyramid Visualization | Medium | 3 hours | Task 3 |
| 7 | Add Integration Risk Sections to Sprint 3 Plan | Critical | 2 hours | Task 1, Task 2 |
| 8 | Establish Mid-Sprint Checkpoint Process | High | 1 hour | Task 1 |
| 9 | Add Complexity Estimation to Sprint 3 Plan | Medium | 2 hours | None |
| 10 | Create Known Unknowns List for Sprint 3 | High | 1 hour | Task 1, Task 2 |

**Total Estimated Time:** 21 hours (~2.5 working days)

---

## Task 1: Create Architecture Diagram

**Priority:** Critical  
**Estimated Time:** 3 hours  
**Deadline:** Before Sprint 3 Day 1  
**Owner:** Development team

### Objective
Create a visual diagram showing complete data flow from GAMS input to KKT output, with all key data structures and API boundaries clearly marked.

### Why This Matters
Sprint 2 Issues #22 and #24 were caused by misunderstanding how data flows between components. A clear architecture diagram would have prevented both.

### Deliverable
**File:** `docs/architecture/SYSTEM_ARCHITECTURE.md`

### Required Content

#### 1. High-Level Data Flow Diagram
Create a diagram (Mermaid, ASCII art, or image) showing:

```
GAMS File (.gms)
    ↓
[Parser] (Sprint 1)
    ↓
ParsedModel
    ↓
[Normalizer] (Sprint 1)
    ↓
ModelIR
    ├─→ equations: dict[str, EquationDef]
    ├─→ normalized_bounds: dict[str, BoundsDef]
    ├─→ inequalities: list[str]
    ├─→ sets: dict[str, SetDef]
    └─→ variables: dict[str, VariableDef]
    ↓
[Variable Instance Mapper] (Sprint 2)
    ↓
VariableInstanceMapping
    ├─→ instances: list[VarInstance]
    └─→ var_to_indices: dict[str, list[int]]
    ↓
[AD Engine] (Sprint 2)
    ↓
├─→ [Gradient Computer] → SparseGradient
│                           ├─→ num_cols (NOT mapping.num_vars!)
│                           ├─→ values: dict[int, Expr]
│                           └─→ mapping: VariableInstanceMapping
│
└─→ [Jacobian Computer] → SparseJacobian
                            ├─→ num_rows
                            ├─→ num_cols
                            ├─→ values: dict[tuple[int,int], Expr]
                            └─→ row_mapping, col_mapping
    ↓
[KKT Assembler] (Sprint 3 - PLANNED)
    ↓
KKTSystem
    ├─→ stationarity_eqs
    ├─→ complementarity_eqs
    └─→ multiplier_vars
    ↓
[GAMS Emitter] (Sprint 3 - PLANNED)
    ↓
MCP File (.gms)
```

#### 2. Critical API Boundaries

Document each module interface:

**ModelIR → AD Module:**
```python
# What AD expects from ModelIR
class ModelIR:
    equations: dict[str, EquationDef]        # Equality and inequality equations
    normalized_bounds: dict[str, BoundsDef]  # Variable bounds (NOT in equations!)
    inequalities: list[str]                  # Names of inequality equations
    # Note: Bounds are in BOTH normalized_bounds AND inequalities list
```

**SparseGradient API:**
```python
# Correct API (Sprint 2)
gradient.num_cols          # ✅ Correct
gradient.mapping.num_vars  # ❌ Wrong (Issue #22)
gradient.values[col_idx]   # Returns Expr
```

**SparseJacobian API:**
```python
# What KKT Assembler will need (Sprint 3)
jacobian.num_rows          # Number of constraint rows
jacobian.num_cols          # Number of variable columns
jacobian.values[(r,c)]     # Returns Expr at (row, col)
```

#### 3. Data Structure Contracts

For each key data structure, document:
- What fields exist
- What invariants must hold
- Where it's created
- Who consumes it

**Example:**
```markdown
### ModelIR (Created: Sprint 1 Normalizer, Consumed: Sprint 2 AD)

**Fields:**
- `equations: dict[str, EquationDef]` - Equality and inequality equations
- `normalized_bounds: dict[str, BoundsDef]` - Variable bounds
- `inequalities: list[str]` - Names of all inequality constraints

**Invariants:**
1. If `name` in `inequalities`, then either:
   - `name` in `equations` (regular inequality), OR
   - `name` in `normalized_bounds` (bound constraint)
2. Bound names follow pattern: `{var}_lo` or `{var}_up`

**Created by:** `normalize_model()` in `src/ir/normalize.py`
**Consumed by:**
- `compute_objective_gradient()` in `src/ad/gradient.py`
- `compute_constraint_jacobian()` in `src/ad/constraint_jacobian.py`

**Issue #24 Root Cause:** Constraint Jacobian code assumed all inequalities in `equations`, but bounds are in `normalized_bounds`.
```

### Implementation Steps

1. **Create directory structure:**
   ```bash
   mkdir -p docs/architecture
   ```

2. **Create main architecture document:**
   - File: `docs/architecture/SYSTEM_ARCHITECTURE.md`
   - Include high-level flow diagram
   - Document all module boundaries

3. **Create data structure reference:**
   - File: `docs/architecture/DATA_STRUCTURES.md`
   - Document all key IR types
   - Document invariants and contracts

4. **Add cross-references:**
   - Link from module docstrings to architecture docs
   - Link from Sprint 3 plan to architecture docs

### Acceptance Criteria

- [ ] Diagram shows complete GAMS → MCP flow
- [ ] All Sprint 1 and Sprint 2 components represented
- [ ] All API boundaries documented with correct attribute names
- [ ] Issue #22 and #24 root causes explained in context
- [ ] Sprint 3 KKT assembler inputs/outputs clearly specified
- [ ] Document reviewed and confirmed accurate

### Expected Outcome

When a developer starts Day 3 (KKT Assembler) in Sprint 3, they can:
1. Look at architecture diagram
2. See exactly what inputs they receive from Sprint 2
3. Know what outputs Sprint 3 needs to produce
4. Understand all data structure contracts without guessing

---

## Task 2: Create Parser Output Reference

**Priority:** Critical  
**Estimated Time:** 2 hours  
**Deadline:** Before Sprint 3 Day 1  
**Owner:** Development team

### Objective
Document how the parser represents every GAMS construct as AST nodes, so developers don't have to guess (Issue #25 root cause).

### Why This Matters
Issue #25 happened because we assumed `x^2` was parsed as `Call("power", ...)` when it was actually `Binary("^", ...)`. A reference would have prevented this.

### Deliverable
**File:** `docs/ir/parser_output_reference.md`

### Required Content

#### 1. Binary Operators

Document how each operator is represented:

```markdown
### Binary Operators

All binary operations are represented as `Binary(op, left, right)` nodes.

| GAMS Syntax | AST Representation | Example |
|-------------|-------------------|---------|
| `x + y` | `Binary("+", VarRef("x"), VarRef("y"))` | Addition |
| `x - y` | `Binary("-", VarRef("x"), VarRef("y"))` | Subtraction |
| `x * y` | `Binary("*", VarRef("x"), VarRef("y"))` | Multiplication |
| `x / y` | `Binary("/", VarRef("x"), VarRef("y"))` | Division |
| `x ^ 2` | `Binary("^", VarRef("x"), Const(2.0))` | **Power (NOT Call!)** |

**Important:** The power operator `^` is parsed as `Binary("^", ...)`, NOT as `Call("power", ...)`.
The AD engine converts `Binary("^", ...)` to `Call("power", ...)` internally for differentiation.
```

#### 2. Function Calls

```markdown
### Function Calls

All function calls are represented as `Call(func_name, args)` nodes.

| GAMS Syntax | AST Representation | Example |
|-------------|-------------------|---------|
| `exp(x)` | `Call("exp", (VarRef("x"),))` | Exponential |
| `log(x)` | `Call("log", (VarRef("x"),))` | Natural log |
| `sqrt(x)` | `Call("sqrt", (VarRef("x"),))` | Square root |
| `sin(x)` | `Call("sin", (VarRef("x"),))` | Sine |
| `cos(x)` | `Call("cos", (VarRef("x"),))` | Cosine |
| `power(x,y)` | `Call("power", (VarRef("x"), VarRef("y")))` | Explicit power |

**Note:** `power(x, 2)` and `x^2` are different at parse time but equivalent after AD processing.
```

#### 3. Variables and Indexing

```markdown
### Variable References

| GAMS Syntax | AST Representation | Notes |
|-------------|-------------------|-------|
| `x` | `VarRef("x", ())` | Scalar variable (empty tuple) |
| `x(i)` | `VarRef("x", ("i",))` | Indexed by one set |
| `x(i,j)` | `VarRef("x", ("i", "j"))` | Indexed by two sets |

**Important:** Indices are symbolic at parse time. After normalization:
- Symbolic: `VarRef("x", ("i",))` where `i` is a set element variable
- Concrete: `VarRef("x", ("i1",))` where `i1` is a specific set member

**Issue #24 Context:** Bounds like `x.lo(i)` become entries in `normalized_bounds` with names like `x_lo`.
```

#### 4. Aggregations

```markdown
### Sum Operations

| GAMS Syntax | AST Representation | Notes |
|-------------|-------------------|-------|
| `sum(i, x(i))` | `Sum(index_vars=["i"], index_sets=["I"], body=VarRef("x", ("i",)))` | Basic sum |
| `sum((i,j), x(i,j))` | `Sum(index_vars=["i","j"], index_sets=["I","J"], body=...)` | Multi-dimensional |

**Differentiation Note:** `d/dx(i1) sum(i, f(i))` only the `i=i1` term contributes (index-aware, Sprint 2 Day 7.5).
```

#### 5. Constants and Parameters

```markdown
### Constants and Parameters

| GAMS Syntax | AST Representation | Notes |
|-------------|-------------------|-------|
| `3.14` | `Const(3.14)` | Numeric constant |
| `c` | `ParamRef("c", ())` | Scalar parameter |
| `c(i)` | `ParamRef("c", ("i",))` | Indexed parameter |
```

#### 6. Common Pitfalls

```markdown
### Common Pitfalls and Gotchas

1. **Power Operator Confusion (Issue #25)**
   - ❌ Wrong: Assuming `x^2` is `Call("power", ...)`
   - ✅ Right: Parser produces `Binary("^", ...)`, AD converts to `Call("power", ...)`

2. **Bounds Location (Issue #24)**
   - ❌ Wrong: Looking for bounds in `model_ir.equations`
   - ✅ Right: Bounds are in `model_ir.normalized_bounds`, names in `model_ir.inequalities`

3. **Index Tuples**
   - ❌ Wrong: `VarRef("x", "i")` (string instead of tuple)
   - ✅ Right: `VarRef("x", ("i",))` (tuple, even for single index)

4. **Empty vs. None Indices**
   - Scalar variable: `VarRef("x", ())` (empty tuple)
   - NOT: `VarRef("x", None)` or `VarRef("x")`
```

### Implementation Steps

1. **Create directory if needed:**
   ```bash
   mkdir -p docs/ir
   ```

2. **Examine parser output for all examples:**
   ```python
   # Run parser on each example, print AST
   for example in ["examples/simple_scalar.gms", "examples/nonlinear_mix.gms", ...]:
       model = parse_model_file(example)
       print(f"\n=== {example} ===")
       for eq_name, eq_def in model.equations.items():
           print(f"{eq_name}: {eq_def.expression}")
   ```

3. **Document all observed patterns:**
   - Create tables for each AST node type
   - Include examples from actual parsed files
   - Note any surprises or non-obvious representations

4. **Add quick reference card:**
   - One-page cheat sheet at top of document
   - Most common operations with AST patterns

### Acceptance Criteria

- [ ] All binary operators documented with examples
- [ ] All function calls documented with examples
- [ ] Variable and parameter indexing patterns documented
- [ ] Sum/aggregation patterns documented
- [ ] Common pitfalls section includes Issues #24 and #25
- [ ] Examples verified against actual parser output
- [ ] Quick reference card at top of document

### Expected Outcome

When implementing differentiation or code generation:
1. Developer sees GAMS syntax like `x^2`
2. Looks up in parser reference
3. Finds it's `Binary("^", ...)` not `Call("power", ...)`
4. Implements correctly on first try, no bugs

---

## Task 3: Refactor Test Organization

**Priority:** High  
**Estimated Time:** 4 hours  
**Deadline:** Before Sprint 3 Day 1  
**Owner:** Development team

### Objective
Reorganize test suite from flat structure into clear test pyramid: unit → integration → e2e → validation.

### Why This Matters
Current structure makes it hard to know where to add new tests and which tests to run for quick feedback vs. comprehensive validation.

### Current Structure (Sprint 2)
```
tests/
  ad/
    test_derivative_rules.py        (40 tests - unit)
    test_arithmetic.py              (33 tests - unit)
    test_gradient.py                (60 tests - mixed unit/integration)
    test_variable_mapping.py        (21 tests - unit)
    test_index_mapping.py           (18 tests - unit)
    test_constraint_jacobian.py     (15 tests - integration)
    test_index_aware_differentiation.py (18 tests - unit)
    test_finite_difference.py       (23 tests - validation)
    test_fd_integration.py          (10 tests - validation)
    test_numeric_edge_cases.py      (15 tests - unit)
    test_sparsity.py                (12 tests - unit)
    test_integration.py             (15 tests - e2e)
  gams/
    test_parser.py
  ir/
    test_normalize.py
```

**Problems:**
- All files at same level - can't tell what's fast vs. slow
- `test_gradient.py` mixes unit and integration tests
- Not clear which tests to run for quick feedback

### Target Structure (Sprint 3)

```
tests/
  unit/                              # Fast tests, no file I/O
    ad/
      test_derivative_rules.py       (40 tests)
      test_arithmetic.py             (33 tests)
      test_variable_mapping.py       (21 tests)
      test_index_mapping.py          (18 tests)
      test_index_aware_differentiation.py (18 tests)
      test_numeric_edge_cases.py     (15 tests)
      test_sparsity.py               (12 tests)
      test_gradient_unit.py          (extracted from test_gradient.py)
    gams/
      test_parser_unit.py
    ir/
      test_normalize_unit.py
  
  integration/                       # Cross-module tests, some file I/O
    ad/
      test_gradient_integration.py   (extracted from test_gradient.py)
      test_constraint_jacobian.py    (15 tests)
      test_gradient_jacobian_integration.py (new - gradient + jacobian together)
    gams_ir/
      test_parser_normalize_integration.py
  
  e2e/                               # Full pipeline tests
    test_gams_to_jacobian.py         (renamed from test_integration.py - 15 tests)
    test_bounds_handling_e2e.py      (new - Issue #24 regression)
    test_power_operator_e2e.py       (new - Issue #25 regression)
  
  validation/                        # Mathematical correctness checks (slower)
    test_finite_difference.py        (23 tests)
    test_fd_integration.py           (10 tests)
    test_numeric_accuracy.py         (new - FD validation for Sprint 3)
```

### Implementation Steps

#### Step 1: Create new directory structure
```bash
mkdir -p tests/unit/ad
mkdir -p tests/unit/gams
mkdir -p tests/unit/ir
mkdir -p tests/integration/ad
mkdir -p tests/integration/gams_ir
mkdir -p tests/e2e
mkdir -p tests/validation
```

#### Step 2: Move and categorize existing tests

**Unit tests (move to `tests/unit/ad/`):**
- `test_derivative_rules.py` → move as-is
- `test_arithmetic.py` → move as-is
- `test_variable_mapping.py` → move as-is
- `test_index_mapping.py` → move as-is
- `test_index_aware_differentiation.py` → move as-is
- `test_numeric_edge_cases.py` → move as-is
- `test_sparsity.py` → move as-is

**Integration tests (move to `tests/integration/ad/`):**
- `test_constraint_jacobian.py` → move as-is

**E2E tests (move to `tests/e2e/`):**
- `test_integration.py` → rename to `test_gams_to_jacobian.py`

**Validation tests (move to `tests/validation/`):**
- `test_finite_difference.py` → move as-is
- `test_fd_integration.py` → move as-is

#### Step 3: Split mixed test files

**Split `test_gradient.py` (60 tests):**

Extract to `tests/unit/ad/test_gradient_unit.py`:
- Tests that use synthetic ModelIR objects (no file parsing)
- Tests of pure gradient computation logic
- ~40 tests

Extract to `tests/integration/ad/test_gradient_integration.py`:
- Tests that parse example files
- Tests that combine gradient + variable mapping
- ~20 tests

#### Step 4: Add pytest markers

Add to `pyproject.toml`:
```toml
[tool.pytest.ini_options]
markers = [
    "unit: Fast unit tests with no I/O",
    "integration: Cross-module integration tests",
    "e2e: End-to-end pipeline tests",
    "validation: Mathematical validation tests (slower)",
]
```

Mark each test:
```python
# tests/unit/ad/test_derivative_rules.py
import pytest

@pytest.mark.unit
class TestDerivativeRules:
    ...
```

#### Step 5: Create test runner scripts

**`scripts/test_fast.sh`** (runs in <5 seconds):
```bash
#!/bin/bash
pytest tests/unit/ -v
```

**`scripts/test_integration.sh`** (runs in <30 seconds):
```bash
#!/bin/bash
pytest tests/unit/ tests/integration/ -v
```

**`scripts/test_all.sh`** (full suite):
```bash
#!/bin/bash
pytest tests/ -v
```

#### Step 6: Update CI/CD

Update `.github/workflows/test.yml`:
```yaml
- name: Run fast tests
  run: pytest tests/unit/ -v
  
- name: Run integration tests
  run: pytest tests/integration/ -v
  
- name: Run e2e tests
  run: pytest tests/e2e/ -v
  
- name: Run validation tests
  run: pytest tests/validation/ -v
```

#### Step 7: Update documentation

Update `README.md`:
```markdown
## Running Tests

Fast feedback (5 seconds):
```bash
pytest tests/unit/
```

Include integration (30 seconds):
```bash
pytest tests/unit/ tests/integration/
```

Full suite including validation (2 minutes):
```bash
pytest tests/
```
```

### Acceptance Criteria

- [ ] All 386 tests moved to new structure
- [ ] All tests still pass after reorganization
- [ ] Pytest markers configured and applied
- [ ] Test runner scripts created and tested
- [ ] CI/CD updated to use new structure
- [ ] README updated with test running instructions
- [ ] `test_gradient.py` successfully split into unit + integration
- [ ] No duplicate test code between files

### Validation Steps

1. **Before reorganization:**
   ```bash
   pytest tests/ --collect-only | wc -l  # Count tests
   pytest tests/ -v                        # All should pass
   ```

2. **After reorganization:**
   ```bash
   pytest tests/ --collect-only | wc -l  # Should be same count
   pytest tests/ -v                        # All should still pass
   pytest tests/unit/ -v                   # Should be fast (<5s)
   ```

### Expected Outcome

Developers can:
1. Run `pytest tests/unit/` for instant feedback while coding
2. Run `pytest tests/integration/` before committing
3. CI runs full suite including validation
4. Clear where to add new tests based on type

---

## Task 4: Add API Contract Tests

**Priority:** High  
**Estimated Time:** 2 hours  
**Deadline:** Sprint 3 Day 2 (after test reorganization)  
**Owner:** Development team  
**Dependencies:** Task 3 (test organization)

### Objective
Create explicit contract tests that validate API boundaries between modules, catching Issues #22-style mismatches immediately.

### Why This Matters
Issue #22 happened because tests assumed `gradient.mapping.num_vars` existed when the correct API was `gradient.num_cols`. Contract tests would have caught this in CI.

### Deliverable
**File:** `tests/integration/test_api_contracts.py`

### Required Test Cases

#### 1. SparseGradient API Contract

```python
import pytest
from src.ad.gradient import compute_objective_gradient
from src.ir.parser import parse_model_file
from src.ir.normalize import normalize_model

@pytest.mark.integration
class TestSparseGradientContract:
    """Tests that validate SparseGradient API stays stable."""
    
    def test_sparse_gradient_has_num_cols(self):
        """SparseGradient must have num_cols attribute."""
        model = parse_model_file('examples/simple_scalar.gms')
        normalize_model(model)
        gradient = compute_objective_gradient(model)
        
        # API contract: gradient.num_cols must exist
        assert hasattr(gradient, 'num_cols')
        assert isinstance(gradient.num_cols, int)
        assert gradient.num_cols > 0
    
    def test_sparse_gradient_has_values(self):
        """SparseGradient must have values dict."""
        model = parse_model_file('examples/simple_scalar.gms')
        normalize_model(model)
        gradient = compute_objective_gradient(model)
        
        assert hasattr(gradient, 'values')
        assert isinstance(gradient.values, dict)
    
    def test_sparse_gradient_has_mapping(self):
        """SparseGradient must have mapping attribute."""
        model = parse_model_file('examples/simple_scalar.gms')
        normalize_model(model)
        gradient = compute_objective_gradient(model)
        
        assert hasattr(gradient, 'mapping')
        # mapping should be VariableInstanceMapping
        assert hasattr(gradient.mapping, 'instances')
    
    def test_num_cols_matches_mapping_length(self):
        """Regression test for Issue #22."""
        model = parse_model_file('examples/simple_scalar.gms')
        normalize_model(model)
        gradient = compute_objective_gradient(model)
        
        # These must be consistent
        assert gradient.num_cols == len(gradient.mapping.instances)
```

#### 2. SparseJacobian API Contract

```python
@pytest.mark.integration
class TestSparseJacobianContract:
    """Tests that validate SparseJacobian API stays stable."""
    
    def test_sparse_jacobian_has_dimensions(self):
        """SparseJacobian must have num_rows and num_cols."""
        model = parse_model_file('examples/bounds_nlp.gms')
        normalize_model(model)
        jacobian = compute_constraint_jacobian(model)
        
        assert hasattr(jacobian, 'num_rows')
        assert hasattr(jacobian, 'num_cols')
        assert isinstance(jacobian.num_rows, int)
        assert isinstance(jacobian.num_cols, int)
    
    def test_sparse_jacobian_has_values(self):
        """SparseJacobian values must be dict[(int,int), Expr]."""
        model = parse_model_file('examples/bounds_nlp.gms')
        normalize_model(model)
        jacobian = compute_constraint_jacobian(model)
        
        assert hasattr(jacobian, 'values')
        assert isinstance(jacobian.values, dict)
        # Keys should be (row, col) tuples
        for key in jacobian.values.keys():
            assert isinstance(key, tuple)
            assert len(key) == 2
```

#### 3. ModelIR API Contract

```python
@pytest.mark.integration
class TestModelIRContract:
    """Tests that validate ModelIR structure from Sprint 1."""
    
    def test_model_ir_has_required_fields(self):
        """ModelIR must have all expected fields."""
        model = parse_model_file('examples/bounds_nlp.gms')
        normalize_model(model)
        
        # Required fields from Sprint 1
        assert hasattr(model, 'equations')
        assert hasattr(model, 'normalized_bounds')
        assert hasattr(model, 'inequalities')
        assert hasattr(model, 'sets')
        assert hasattr(model, 'variables')
    
    def test_bounds_not_in_equations(self):
        """Regression test for Issue #24: bounds are separate."""
        model = parse_model_file('examples/bounds_nlp.gms')
        normalize_model(model)
        
        # Bounds should NOT be in equations dict
        for bound_name in model.normalized_bounds.keys():
            # Bound names like 'x_lo', 'x_up' should NOT be in equations
            if bound_name.endswith('_lo') or bound_name.endswith('_up'):
                assert bound_name not in model.equations, \
                    f"Bound {bound_name} should not be in equations dict"
    
    def test_bounds_in_inequalities_list(self):
        """Bounds should appear in inequalities list."""
        model = parse_model_file('examples/bounds_nlp.gms')
        normalize_model(model)
        
        # Every bound should be in inequalities list
        for bound_name in model.normalized_bounds.keys():
            assert bound_name in model.inequalities, \
                f"Bound {bound_name} should be in inequalities list"
```

#### 4. Differentiation API Contract

```python
@pytest.mark.unit
class TestDifferentiationAPIContract:
    """Tests for differentiate_expr API signature."""
    
    def test_differentiate_accepts_wrt_indices(self):
        """differentiate_expr must accept wrt_indices parameter."""
        from src.ad.derivative_rules import differentiate_expr
        from src.ir.ast_types import VarRef, Const
        
        expr = VarRef("x", ("i1",))
        
        # Should accept wrt_indices parameter (Sprint 2 Day 7.5)
        result = differentiate_expr(expr, "x", wrt_indices=("i1",))
        assert result == Const(1.0)
        
        # Should also work without wrt_indices (backward compat)
        result_compat = differentiate_expr(expr, "x")
        assert isinstance(result_compat, Const)
```

### Implementation Steps

1. **Create test file:**
   ```bash
   touch tests/integration/test_api_contracts.py
   ```

2. **Implement all contract test classes:**
   - SparseGradient contract
   - SparseJacobian contract
   - ModelIR contract
   - Differentiation API contract

3. **Run tests to verify they pass:**
   ```bash
   pytest tests/integration/test_api_contracts.py -v
   ```

4. **Add to CI as critical tests:**
   - These tests must pass before merging any PR
   - Fail fast if API contracts violated

### Acceptance Criteria

- [ ] SparseGradient contract tests implemented (4 tests)
- [ ] SparseJacobian contract tests implemented (2 tests)
- [ ] ModelIR contract tests implemented (3 tests)
- [ ] Differentiation API contract tests implemented (1 test)
- [ ] All tests pass
- [ ] Tests added to integration test suite
- [ ] CI configured to run these tests first (fail fast)

### Expected Outcome

When someone modifies an API:
1. Contract test fails immediately
2. CI catches it before code review
3. Developer sees clear message: "API contract violated: expected gradient.num_cols"
4. No more Issue #22-style bugs in production

---

## Task 5: Create Early Integration Smoke Test

**Priority:** Critical  
**Estimated Time:** 1 hour  
**Deadline:** Sprint 3 Day 2  
**Owner:** Development team

### Objective
Create a minimal end-to-end test that runs early (Day 2-3) to catch integration issues before they cascade.

### Why This Matters
Sprint 2 integration issues weren't discovered until Day 9. An early smoke test would have caught them on Day 2-3.

### Deliverable
**File:** `tests/e2e/test_smoke.py`

### Implementation

```python
"""
Early integration smoke test.

This test should be run as soon as basic components are implemented
to catch integration issues early.

Run this on:
- Sprint 3 Day 2 (after KKT assembler basics)
- Sprint 3 Day 3 (after GAMS emitter basics)
- Any time a major API change is made

If this test fails, stop and fix integration before continuing.
"""

import pytest
from src.ir.parser import parse_model_file
from src.ir.normalize import normalize_model
from src.ad.gradient import compute_objective_gradient
from src.ad.constraint_jacobian import compute_constraint_jacobian

@pytest.mark.e2e
class TestEarlyIntegrationSmoke:
    """
    Minimal smoke test to catch integration issues early.
    
    This is NOT comprehensive - it just checks that the pipeline
    doesn't crash and produces reasonable outputs.
    """
    
    def test_minimal_scalar_nlp_pipeline(self):
        """
        Smoke test: Parse → Normalize → Gradient → Jacobian.
        
        Uses simplest possible example to minimize variables.
        If this fails, integration is broken.
        """
        # Step 1: Parse
        model = parse_model_file('examples/simple_scalar.gms')
        assert model is not None, "Parser failed"
        
        # Step 2: Normalize
        normalize_model(model)
        assert hasattr(model, 'equations'), "Normalizer didn't create equations"
        assert hasattr(model, 'normalized_bounds'), "Normalizer didn't create bounds"
        
        # Step 3: Gradient
        gradient = compute_objective_gradient(model)
        assert gradient is not None, "Gradient computation failed"
        assert hasattr(gradient, 'num_cols'), "Gradient missing num_cols (Issue #22?)"
        assert gradient.num_cols > 0, "Gradient has no columns"
        
        # Step 4: Jacobian
        jacobian = compute_constraint_jacobian(model)
        assert jacobian is not None, "Jacobian computation failed"
        assert hasattr(jacobian, 'num_rows'), "Jacobian missing num_rows"
        assert hasattr(jacobian, 'num_cols'), "Jacobian missing num_cols"
        
        # Sanity checks
        assert gradient.num_cols == jacobian.num_cols, \
            "Gradient and Jacobian have different column counts"
    
    def test_indexed_nlp_pipeline(self):
        """
        Smoke test with indexed variables.
        
        Catches index-aware differentiation issues early.
        """
        model = parse_model_file('examples/indexed_sum.gms')
        normalize_model(model)
        
        gradient = compute_objective_gradient(model)
        jacobian = compute_constraint_jacobian(model)
        
        # Basic sanity
        assert gradient.num_cols > 1, "Should have multiple variables"
        assert jacobian.num_rows > 0, "Should have constraints"
        assert gradient.num_cols == jacobian.num_cols
    
    def test_bounds_handling_pipeline(self):
        """
        Smoke test for bounds handling (Issue #24 regression).
        
        This would have caught Issue #24 on Day 2 instead of Day 9.
        """
        model = parse_model_file('examples/bounds_nlp.gms')
        normalize_model(model)
        
        # Check bounds are normalized
        assert len(model.normalized_bounds) > 0, "Should have bounds"
        
        # This should NOT crash with KeyError
        try:
            jacobian = compute_constraint_jacobian(model)
        except KeyError as e:
            pytest.fail(f"Issue #24 regression: KeyError {e} when processing bounds")
        
        assert jacobian is not None
        assert jacobian.num_rows > 0
    
    def test_power_operator_pipeline(self):
        """
        Smoke test for power operator (Issue #25 regression).
        
        This would have caught Issue #25 early.
        """
        model = parse_model_file('examples/nonlinear_mix.gms')
        normalize_model(model)
        
        # This should NOT raise ValueError for unsupported operator
        try:
            gradient = compute_objective_gradient(model)
            jacobian = compute_constraint_jacobian(model)
        except ValueError as e:
            if "Unsupported binary operation" in str(e):
                pytest.fail(f"Issue #25 regression: Power operator not supported")
            raise
        
        assert gradient is not None
        assert jacobian is not None


@pytest.mark.e2e
class TestSprint3KKTSmoke:
    """
    Smoke tests for Sprint 3 KKT assembler.
    
    Add these tests on Sprint 3 Day 2-3 as KKT assembler is built.
    """
    
    @pytest.mark.skip(reason="Implement on Sprint 3 Day 2")
    def test_kkt_assembler_smoke(self):
        """
        Smoke test: Parse → Normalize → Gradient → Jacobian → KKT.
        
        Implement this on Sprint 3 Day 2 after basic KKT assembler exists.
        """
        from src.kkt.assemble import assemble_kkt_system  # Add in Sprint 3
        
        model = parse_model_file('examples/simple_scalar.gms')
        normalize_model(model)
        gradient = compute_objective_gradient(model)
        jacobian = compute_constraint_jacobian(model)
        
        # KKT assembly should not crash
        kkt = assemble_kkt_system(model, gradient, jacobian)
        assert kkt is not None
        assert hasattr(kkt, 'stationarity_eqs')
        assert hasattr(kkt, 'complementarity_eqs')
    
    @pytest.mark.skip(reason="Implement on Sprint 3 Day 3")
    def test_gams_emitter_smoke(self):
        """
        Smoke test: Full pipeline → GAMS MCP output.
        
        Implement this on Sprint 3 Day 3 after basic GAMS emitter exists.
        """
        from src.kkt.assemble import assemble_kkt_system
        from src.emit.emit_gams import emit_gams_mcp
        
        model = parse_model_file('examples/simple_scalar.gms')
        normalize_model(model)
        gradient = compute_objective_gradient(model)
        jacobian = compute_constraint_jacobian(model)
        kkt = assemble_kkt_system(model, gradient, jacobian)
        
        # GAMS emission should not crash
        gams_code = emit_gams_mcp(kkt)
        assert gams_code is not None
        assert len(gams_code) > 0
        assert 'Model' in gams_code  # Basic sanity
```

### When to Run This Test

**Sprint 3 Timeline:**

- **Day 1:** Test skeleton exists, Sprint 2 tests all pass
- **Day 2 (KKT Assembler Day):**
  - Run `test_minimal_scalar_nlp_pipeline()` after basic assembler
  - If fails → stop, fix integration, then continue
  - Add `test_kkt_assembler_smoke()` and verify
- **Day 3 (GAMS Emitter Day):**
  - Run full smoke suite
  - Add `test_gams_emitter_smoke()` and verify
- **Every day after:** Run smoke suite in CI

### Implementation Steps

1. **Create test file:**
   ```bash
   touch tests/e2e/test_smoke.py
   ```

2. **Implement Sprint 2 smoke tests:**
   - All 4 tests in `TestEarlyIntegrationSmoke`

3. **Add Sprint 3 placeholders:**
   - Skipped tests for KKT and GAMS emitter
   - Unskip and implement on Sprint 3 Days 2-3

4. **Add to CI:**
   ```yaml
   # Run smoke tests first (fail fast)
   - name: Early integration smoke test
     run: pytest tests/e2e/test_smoke.py -v
   ```

### Acceptance Criteria

- [ ] 4 Sprint 2 smoke tests implemented
- [ ] All tests pass
- [ ] 2 Sprint 3 placeholder tests added (skipped)
- [ ] Test added to CI pipeline (runs first)
- [ ] Documentation added explaining when to run

### Expected Outcome

**Sprint 3 Day 2:**
- Developer implements basic KKT assembler
- Runs smoke test
- Test catches integration issue immediately
- Developer fixes before moving to next component
- **Result:** Issues caught in hours, not days

---

## Task 6: Implement Test Pyramid Visualization

**Priority:** Medium  
**Estimated Time:** 3 hours  
**Deadline:** Sprint 3 Day 1  
**Owner:** Development team  
**Dependencies:** Task 3 (test reorganization)

### Objective
Create visualization showing test coverage breakdown by type (unit/integration/e2e/validation) for each module.

### Why This Matters
Makes it clear where test coverage is comprehensive vs. sparse, helping identify gaps.

### Deliverable
**Script:** `scripts/test_pyramid.py`  
**Output:** `docs/testing/TEST_PYRAMID.md` (auto-generated)

### Implementation

```python
#!/usr/bin/env python3
"""
Generate test pyramid visualization.

Shows breakdown of tests by type for each module.
"""

import subprocess
import re
from collections import defaultdict
from pathlib import Path

def count_tests_by_marker(path: Path, marker: str) -> int:
    """Count tests with specific marker in path."""
    result = subprocess.run(
        ['pytest', str(path), '-m', marker, '--collect-only', '-q'],
        capture_output=True,
        text=True
    )
    # Parse output like "15 tests collected"
    match = re.search(r'(\d+) tests? collected', result.stdout)
    return int(match.group(1)) if match else 0

def count_total_tests(path: Path) -> int:
    """Count all tests in path."""
    result = subprocess.run(
        ['pytest', str(path), '--collect-only', '-q'],
        capture_output=True,
        text=True
    )
    match = re.search(r'(\d+) tests? collected', result.stdout)
    return int(match.group(1)) if match else 0

def generate_pyramid():
    """Generate test pyramid visualization."""
    
    modules = {
        'AD (Differentiation)': 'tests/unit/ad',
        'GAMS Parser': 'tests/unit/gams',
        'IR': 'tests/unit/ir',
        'Integration (AD)': 'tests/integration/ad',
        'Integration (GAMS-IR)': 'tests/integration/gams_ir',
        'End-to-End': 'tests/e2e',
        'Validation': 'tests/validation',
    }
    
    results = {}
    for name, path in modules.items():
        path_obj = Path(path)
        if not path_obj.exists():
            continue
        
        results[name] = {
            'unit': count_tests_by_marker(path_obj, 'unit'),
            'integration': count_tests_by_marker(path_obj, 'integration'),
            'e2e': count_tests_by_marker(path_obj, 'e2e'),
            'validation': count_tests_by_marker(path_obj, 'validation'),
            'total': count_total_tests(path_obj),
        }
    
    # Generate markdown
    md = []
    md.append("# Test Pyramid Visualization")
    md.append("")
    md.append("*Auto-generated by `scripts/test_pyramid.py`*")
    md.append("")
    md.append("## Overview")
    md.append("")
    md.append("```")
    md.append("        /\\")
    md.append("       /  \\  Validation (slowest, mathematical correctness)")
    md.append("      /    \\")
    md.append("     /------\\")
    md.append("    /        \\  E2E (slow, full pipeline)")
    md.append("   /----------\\")
    md.append("  /            \\  Integration (medium, cross-module)")
    md.append(" /--------------\\")
    md.append("/________________\\  Unit (fast, isolated)")
    md.append("```")
    md.append("")
    md.append("## Test Counts by Module")
    md.append("")
    md.append("| Module | Unit | Integration | E2E | Validation | Total |")
    md.append("|--------|------|-------------|-----|------------|-------|")
    
    totals = defaultdict(int)
    for name, counts in results.items():
        md.append(f"| {name} | {counts['unit']} | {counts['integration']} | "
                  f"{counts['e2e']} | {counts['validation']} | {counts['total']} |")
        for key in ['unit', 'integration', 'e2e', 'validation', 'total']:
            totals[key] += counts[key]
    
    md.append(f"| **TOTAL** | **{totals['unit']}** | **{totals['integration']}** | "
              f"**{totals['e2e']}** | **{totals['validation']}** | **{totals['total']}** |")
    md.append("")
    
    # Add pyramid visualization
    md.append("## Pyramid Balance")
    md.append("")
    md.append("Ideal test pyramid: Many unit tests, fewer integration, even fewer e2e.")
    md.append("")
    md.append(f"- Unit: {totals['unit']} ({100*totals['unit']//totals['total']}%)")
    md.append(f"- Integration: {totals['integration']} ({100*totals['integration']//totals['total']}%)")
    md.append(f"- E2E: {totals['e2e']} ({100*totals['e2e']//totals['total']}%)")
    md.append(f"- Validation: {totals['validation']} ({100*totals['validation']//totals['total']}%)")
    md.append("")
    
    # Check balance
    if totals['unit'] < totals['integration']:
        md.append("⚠️ **Warning:** More integration than unit tests. Add more unit tests.")
    elif totals['unit'] > 2 * totals['integration']:
        md.append("✅ **Good:** Healthy test pyramid with strong unit test base.")
    
    md.append("")
    md.append("## Test Execution Speed")
    md.append("")
    md.append("Expected execution times:")
    md.append(f"- Unit only: ~{totals['unit'] * 0.01:.1f}s (fast feedback)")
    md.append(f"- Unit + Integration: ~{(totals['unit'] + totals['integration']) * 0.05:.1f}s (pre-commit)")
    md.append(f"- Full suite: ~{totals['total'] * 0.3:.1f}s (CI)")
    
    return '\n'.join(md)

if __name__ == '__main__':
    markdown = generate_pyramid()
    
    output_path = Path('docs/testing/TEST_PYRAMID.md')
    output_path.parent.mkdir(exist_ok=True, parents=True)
    output_path.write_text(markdown)
    
    print(f"Test pyramid generated: {output_path}")
    print()
    print(markdown)
```

### Usage

```bash
# Generate pyramid
python scripts/test_pyramid.py

# Output will be in docs/testing/TEST_PYRAMID.md
```

### Example Output

```markdown
# Test Pyramid Visualization

## Test Counts by Module

| Module | Unit | Integration | E2E | Validation | Total |
|--------|------|-------------|-----|------------|-------|
| AD (Differentiation) | 157 | 0 | 0 | 0 | 157 |
| Integration (AD) | 0 | 35 | 0 | 0 | 35 |
| End-to-End | 0 | 0 | 18 | 0 | 18 |
| Validation | 0 | 0 | 0 | 33 | 33 |
| **TOTAL** | **157** | **35** | **18** | **33** | **243** |

## Pyramid Balance

- Unit: 157 (64%)
- Integration: 35 (14%)
- E2E: 18 (7%)
- Validation: 33 (14%)

✅ **Good:** Healthy test pyramid with strong unit test base.
```

### Implementation Steps

1. **Create script:**
   ```bash
   mkdir -p scripts
   touch scripts/test_pyramid.py
   chmod +x scripts/test_pyramid.py
   ```

2. **Implement pyramid generator** (code above)

3. **Test script:**
   ```bash
   python scripts/test_pyramid.py
   ```

4. **Add to CI:**
   ```yaml
   - name: Generate test pyramid
     run: python scripts/test_pyramid.py
   
   - name: Upload pyramid artifact
     uses: actions/upload-artifact@v2
     with:
       name: test-pyramid
       path: docs/testing/TEST_PYRAMID.md
   ```

5. **Add to README:**
   ```markdown
   ## Test Coverage
   
   See [Test Pyramid](docs/testing/TEST_PYRAMID.md) for test breakdown.
   ```

### Acceptance Criteria

- [ ] Script implemented and executable
- [ ] Generates TEST_PYRAMID.md correctly
- [ ] Shows counts by module and type
- [ ] Calculates percentages
- [ ] Warns if pyramid inverted
- [ ] Estimates execution times
- [ ] Added to CI pipeline
- [ ] README links to pyramid

### Expected Outcome

When reviewing test coverage:
1. Run `python scripts/test_pyramid.py`
2. See clear breakdown of test types
3. Identify gaps (e.g., "AD has 157 unit tests but only 2 integration tests")
4. Make informed decisions about where to add tests

---

## Task 7: Add Integration Risk Sections to Sprint 3 Plan

**Priority:** Critical  
**Estimated Time:** 2 hours  
**Deadline:** Before Sprint 3 Day 1  
**Owner:** Sprint planning  
**Dependencies:** Task 1 (architecture diagram), Task 2 (parser reference)

### Objective
Review Sprint 3 plan and add "Integration Risks" section to each day's plan, explicitly noting dependencies and assumptions.

### Why This Matters
Sprint 2 Day 7 didn't consider Sprint 1's bounds storage design, causing Issue #24. Explicit integration risks make dependencies visible and testable.

### Process

For each day in Sprint 3 plan, add a section:

```markdown
### Integration Risks for Day N

**Sprint 1 Dependencies:**
- Assumption: [What we assume about Sprint 1 components]
- Risk: [What could go wrong]
- Mitigation: [How to test early]

**Sprint 2 Dependencies:**
- Assumption: [What we assume about Sprint 2 components]
- Risk: [What could go wrong]
- Mitigation: [How to test early]

**Within-Sprint Dependencies:**
- Assumption: [What we assume about earlier Sprint 3 days]
- Risk: [What could go wrong]
- Mitigation: [How to test]
```

### Example: Sprint 3 Day 3 (KKT Assembler)

```markdown
## Day 3: KKT Assembler

### Goals
- Partition constraints into equality/inequality
- Create multiplier variables for each constraint row
- Build stationarity equation: ∇f + J_g^T λ + J_h^T ν - π^L + π^U
- Build complementarity equations

### Integration Risks for Day 3

**Sprint 1 Dependencies:**

Assumption 1: `model_ir.equations` contains all equality and regular inequality constraints
- **Risk:** Some inequalities might be stored elsewhere (like bounds were in Issue #24)
- **Mitigation:** On Day 3 morning, run diagnostic:
  ```python
  print("Equations:", model_ir.equations.keys())
  print("Inequalities:", model_ir.inequalities)
  print("Bounds:", model_ir.normalized_bounds.keys())
  # Verify: every inequality is either in equations OR bounds
  ```

Assumption 2: `model_ir.normalized_bounds` contains bounds with names like `x_lo`, `x_up`
- **Risk:** Naming convention might be different
- **Mitigation:** Check parser reference doc (Task 2), verify with examples

**Sprint 2 Dependencies:**

Assumption 1: `SparseJacobian` has `.num_rows`, `.num_cols`, `.values` attributes
- **Risk:** API might be different (like Issue #22)
- **Mitigation:** Run API contract tests (Task 4) before starting Day 3

Assumption 2: Jacobian values are symbolic Expr AST nodes, not numeric values
- **Risk:** Might need to handle both symbolic and numeric
- **Mitigation:** Check one jacobian.values entry:
  ```python
  sample_entry = next(iter(jacobian.values.values()))
  print(f"Type: {type(sample_entry)}")  # Should be Expr
  ```

Assumption 3: Jacobian columns match gradient columns (same variable ordering)
- **Risk:** Gradient and Jacobian might use different variable orderings
- **Mitigation:** Verify:
  ```python
  assert gradient.num_cols == jacobian.num_cols
  assert gradient.mapping == jacobian.col_mapping
  ```

**Within-Sprint Dependencies:**

Assumption 1: We can represent stationarity as symbolic Expr AST
- **Risk:** Might need new AST node types for Jacobian transpose operations
- **Mitigation:** On Day 2, design KKT IR structure; confirm AST is sufficient

**Early Integration Test:**
On Day 3 afternoon, run:
```python
def test_kkt_basic_integration():
    model = parse_model_file('examples/simple_scalar.gms')
    normalize_model(model)
    gradient = compute_objective_gradient(model)
    jacobian = compute_constraint_jacobian(model)
    
    # This should not crash
    kkt = assemble_kkt_system(model, gradient, jacobian)
    assert kkt is not None
```

If this fails, STOP and fix integration before continuing to Day 4.
```

### Implementation Steps

1. **Read Sprint 3 plan:**
   ```bash
   # Assuming SPRINT_3_PLAN.md exists or needs to be created
   ```

2. **For each day (Days 1-10):**
   - Identify what Sprint 1 components it uses
   - Identify what Sprint 2 components it uses
   - Identify what earlier Sprint 3 days it depends on
   - Document assumptions about each
   - Note what could go wrong
   - Define early test to mitigate

3. **Use architecture diagram (Task 1):**
   - Reference diagram to find dependencies
   - Example: "See architecture diagram: KKT Assembler receives SparseJacobian from Sprint 2"

4. **Use parser reference (Task 2):**
   - Reference for any assumptions about AST structure
   - Example: "Per parser reference, bounds are in normalized_bounds, not equations"

5. **Add integration test checkpoints:**
   - For each day with high integration risk, define test to run that afternoon
   - Tests should be in `test_smoke.py` (Task 5)

### Template for Each Day

```markdown
### Integration Risks for Day N

**Complexity: [Simple/Medium/Complex]**

**Sprint 1 Dependencies:**
- Uses: [List specific Sprint 1 components]
- Assumptions:
  1. [Explicit assumption with reference to architecture doc]
  2. [Another assumption]
- Mitigation: [Early test or verification]

**Sprint 2 Dependencies:**
- Uses: [List specific Sprint 2 components]
- Assumptions:
  1. [Explicit assumption with reference to API contracts]
  2. [Another assumption]
- Mitigation: [API contract test or early integration test]

**Within-Sprint Dependencies:**
- Uses: [List earlier Sprint 3 days]
- Assumptions: [What we assume about those days' outputs]
- Mitigation: [How to verify]

**Early Integration Checkpoint:**
- When: [Day N afternoon / Day N+1 morning]
- Test: [Specific test name from test_smoke.py]
- Criteria: [What must pass to proceed]
```

### Deliverable

**Updated:** `docs/planning/SPRINT_3_PLAN.md` with integration risks for all days

### Acceptance Criteria

- [ ] All 10 days in Sprint 3 plan have Integration Risks section
- [ ] Each section lists Sprint 1, Sprint 2, and within-sprint dependencies
- [ ] Each assumption references architecture diagram or parser reference
- [ ] Each high-risk day has early integration checkpoint defined
- [ ] Mitigations are specific and testable
- [ ] Document reviewed for completeness

### Expected Outcome

**Sprint 3 Day 3 morning:**
- Developer reads Day 3 plan
- Sees integration risks clearly listed
- Runs specified diagnostic/verification
- Catches integration issue before writing code
- Saves 1-2 days of debugging

---

## Task 8: Establish Mid-Sprint Checkpoint Process

**Priority:** High  
**Estimated Time:** 1 hour  
**Deadline:** Before Sprint 3 Day 1  
**Owner:** Sprint lead  
**Dependencies:** Task 1 (architecture diagram)

### Objective
Define formal architectural review checkpoints at Days 3, 6, and 8 of Sprint 3.

### Why This Matters
Sprint 2 had no cross-module reviews until Day 9 integration testing. Checkpoints on Days 3, 6, 8 would have caught issues earlier.

### Deliverable
**Document:** `docs/process/CHECKPOINT_PROCESS.md`

### Implementation

```markdown
# Sprint Checkpoint Process

## Purpose

Prevent late-stage integration issues by reviewing architectural fit at key milestones during the sprint.

## Sprint 3 Checkpoints

### Checkpoint 1: Day 3 (KKT Assembler Complete)

**When:** End of Day 3, before starting Day 4  
**Duration:** 30 minutes  
**Format:** Async document review or synchronous meeting

**Review Questions:**
1. Does KKT assembler correctly consume Sprint 2 outputs (gradient, Jacobian)?
2. Are all API assumptions validated? (Run API contract tests)
3. Does stationarity equation construction match mathematical definition?
4. Are multiplier variables created for all constraint rows?
5. Do complementarity equations handle bounds correctly?

**Artifacts to Review:**
- `src/kkt/assemble.py` implementation
- Test results from `test_smoke.py::test_kkt_assembler_smoke`
- Any integration issues discovered

**Acceptance Criteria:**
- ✅ Smoke test passes
- ✅ API contract tests pass
- ✅ KKT equations match mathematical formulation (refer to Sprint 3 plan)
- ✅ No assumptions about Sprint 1/2 data structures are unvalidated

**If Checkpoint Fails:**
- STOP Day 4 work
- Fix integration issues
- Re-run checkpoint review
- Only proceed when all criteria pass

---

### Checkpoint 2: Day 6 (GAMS Emitter Basics Complete)

**When:** End of Day 6, before starting Day 7  
**Duration:** 30 minutes

**Review Questions:**
1. Does GAMS emitter correctly consume KKT system from Day 3?
2. Does generated GAMS code compile? (Run GAMS syntax check if available)
3. Are equation names unique and valid GAMS identifiers?
4. Are complementarity pairings correct in Model declaration?
5. Do emitted equations match KKT system semantics?

**Artifacts to Review:**
- `src/emit/emit_gams.py` implementation
- Generated GAMS code from examples
- Test results from `test_smoke.py::test_gams_emitter_smoke`
- Golden file comparisons (if available)

**Acceptance Criteria:**
- ✅ Smoke test passes
- ✅ Generated GAMS code compiles (or syntax validates)
- ✅ Stationarity equations have correct structure
- ✅ Complementarity equations properly paired
- ✅ No naming collisions in generated code

**If Checkpoint Fails:**
- STOP Day 7 work
- Fix code generation issues
- Re-run checkpoint review
- Only proceed when all criteria pass

---

### Checkpoint 3: Day 8 (Integration Testing Complete)

**When:** End of Day 8, before starting Day 9 (polish/docs)  
**Duration:** 60 minutes (more comprehensive)

**Review Questions:**
1. Do all integration tests pass?
2. Are all acceptance criteria from Sprint 3 plan met?
3. Do generated MCPs solve correctly? (If PATH available)
4. Are there any known issues or limitations to document?
5. Is test coverage comprehensive?

**Artifacts to Review:**
- Full test suite results (all 400+ tests)
- Integration test results (`tests/integration/`, `tests/e2e/`)
- Test pyramid visualization (run `scripts/test_pyramid.py`)
- Golden file comparisons for all examples
- Any GAMS/PATH run results (if available)

**Acceptance Criteria:**
- ✅ All tests pass (100%)
- ✅ All Sprint 3 deliverables complete
- ✅ Test pyramid shows healthy distribution
- ✅ Generated MCPs compile in GAMS
- ✅ No unresolved integration issues
- ✅ Documentation plan for Day 9-10 clear

**If Checkpoint Fails:**
- Day 9-10 may need to focus on fixing issues instead of polish
- Escalate if major blockers discovered this late
- Document known issues/limitations
- Decide: fix now or defer to Sprint 4?

---

## Checkpoint Review Format

### Async Review (Recommended for solo development)

1. **Developer creates checkpoint document:**
   ```markdown
   # Checkpoint N Review - [Date]
   
   ## Review Questions
   [Answer each question above]
   
   ## Test Results
   [Paste relevant test outputs]
   
   ## Issues Discovered
   [List any problems found]
   
   ## Acceptance Criteria
   - [ ] Criterion 1
   - [ ] Criterion 2
   ...
   ```

2. **Self-review:**
   - Answer all questions honestly
   - Run all specified tests
   - Check all acceptance criteria
   - Document issues

3. **Decision:**
   - If all criteria pass → proceed to next phase
   - If any fail → stop, fix, re-review

### Synchronous Review (For team development)

1. **Pre-meeting:** Developer prepares checkpoint document
2. **Meeting:** Team reviews together (30-60 min)
3. **Output:** Go/no-go decision + action items
4. **Follow-up:** Fix issues before next phase

---

## Benefits

1. **Early issue detection:** Catch problems on Day 3, not Day 9
2. **Clear go/no-go points:** Don't proceed with broken foundations
3. **Reduced rework:** Fix integration before building on top
4. **Better planning:** Know status at key milestones
5. **Quality assurance:** Built-in review gates

---

## Sprint 2 Retrospective Context

In Sprint 2, we had:
- ❌ No architectural checkpoints
- ❌ Integration testing only on Day 9
- ❌ Issues discovered 5-7 days after introduced

Result: Issues #22, #24, #25 found late

With checkpoints, we would have:
- ✅ Caught API mismatch (Issue #22) on Day 4 checkpoint
- ✅ Caught bounds handling (Issue #24) on Day 7 checkpoint
- ✅ Caught power operator (Issue #25) on Day 2 smoke test

**Estimated time saved:** 1-2 days per sprint
```

### Implementation Steps

1. **Create process document:**
   ```bash
   mkdir -p docs/process
   touch docs/process/CHECKPOINT_PROCESS.md
   ```

2. **Add to Sprint 3 plan:**
   - Reference checkpoints in Sprint 3 plan
   - Add reminders on Days 3, 6, 8

3. **Create checkpoint templates:**
   ```bash
   mkdir -p docs/checkpoints
   touch docs/checkpoints/CHECKPOINT_TEMPLATE.md
   ```

4. **Add to calendar/reminders:**
   - Set reminder for end of Day 3
   - Set reminder for end of Day 6
   - Set reminder for end of Day 8

### Acceptance Criteria

- [ ] Checkpoint process document created
- [ ] 3 checkpoints defined with clear criteria
- [ ] Checkpoint templates created
- [ ] Sprint 3 plan references checkpoints
- [ ] Reminders set for checkpoint days

### Expected Outcome

**Sprint 3 Day 3 afternoon:**
- Developer completes KKT assembler
- Runs Checkpoint 1 review
- Discovers gradient/Jacobian API mismatch
- Fixes immediately (1 hour)
- Proceeds to Day 4 with clean foundation
- **Saved:** 1-2 days of debugging later

---

## Task 9: Add Complexity Estimation to Sprint 3 Plan

**Priority:** Medium  
**Estimated Time:** 2 hours  
**Deadline:** Before Sprint 3 Day 1  
**Owner:** Sprint planning

### Objective
Add complexity estimates (Simple/Medium/Complex) to each day in Sprint 3 plan to identify where buffer time might be needed.

### Why This Matters
Sprint 2's Day 7.5 (index-aware differentiation) was unplanned because complexity was underestimated. Explicit estimates help allocate buffer time.

### Process

For each day in Sprint 3, add:

```markdown
### Day N: [Task Name]

**Complexity: [Simple / Medium / Complex]**

**Complexity Rationale:**
- [Why this complexity level]
- [Similar past work or new territory]
- [Known unknowns that could increase complexity]

**Estimated Time:** [Hours]  
**Buffer Time:** [0 hours / 2 hours / 4 hours]

**Complexity Risk Factors:**
- [ ] New territory (no similar past work)
- [ ] Multiple external dependencies
- [ ] Unclear requirements
- [ ] Complex algorithm/math
- [ ] Extensive testing needed

**If Complexity Exceeds Estimate:**
- Trigger: [What indicates we're over estimate]
- Response: [Add Day N.5 or defer scope]
```

### Complexity Definitions

**Simple:**
- Well-understood problem
- Similar to past work
- Clear implementation path
- Few dependencies
- Estimated time: 4-6 hours
- Buffer: 0 hours
- Example: Day 10 Documentation (similar to Sprint 2 Day 10)

**Medium:**
- Some unknowns, but clear approach
- Builds on existing patterns
- Moderate dependencies
- Some new concepts
- Estimated time: 6-8 hours
- Buffer: 2 hours
- Example: Day 3 KKT Assembler (new, but straightforward math)

**Complex:**
- New territory
- Unclear best approach
- Many dependencies
- Novel algorithms
- High integration risk
- Estimated time: 8-10 hours
- Buffer: 4 hours (may need Day N.5)
- Example: Day 7.5 from Sprint 2 (index-aware differentiation)

### Example: Sprint 3 Days with Estimates

```markdown
## Day 1: KKT System IR Design

**Complexity: Simple**

**Complexity Rationale:**
- Similar to Sprint 2 IR design (SparseGradient, SparseJacobian)
- Well-defined mathematical structure (stationarity, complementarity)
- No external dependencies (pure design work)

**Estimated Time:** 5 hours  
**Buffer Time:** 0 hours

**Complexity Risk Factors:**
- [ ] New territory
- [ ] Multiple external dependencies
- [ ] Unclear requirements
- [ ] Complex algorithm/math
- [ ] Extensive testing needed

None checked → Simple

---

## Day 3: KKT Assembler Implementation

**Complexity: Medium**

**Complexity Rationale:**
- Moderate dependencies (Sprint 1 ModelIR, Sprint 2 Jacobians)
- Mathematical structure is clear (KKT conditions well-defined)
- Implementation path straightforward, but integration risk exists
- Similar to Sprint 2 gradient/Jacobian assembly

**Estimated Time:** 7 hours  
**Buffer Time:** 2 hours (total 9 hours available)

**Complexity Risk Factors:**
- [ ] New territory (first time assembling KKT, but concept is clear)
- [X] Multiple external dependencies (ModelIR, Gradient, Jacobian)
- [ ] Unclear requirements
- [ ] Complex algorithm/math
- [X] Extensive testing needed (integration with Sprint 1 & 2)

2 checked → Medium

**If Complexity Exceeds Estimate:**
- Trigger: Not done by end of Day 3 (9 hours)
- Response: Add Day 3.5 for integration bug fixing

---

## Day 5: GAMS Emitter - Equation Generation

**Complexity: Complex**

**Complexity Rationale:**
- New territory (first time generating GAMS code)
- Many edge cases (naming collisions, syntax quirks, escaping)
- Unclear how to handle all GAMS syntax rules
- String templating can be brittle
- High risk of GAMS compilation errors

**Estimated Time:** 8 hours  
**Buffer Time:** 4 hours (total 12 hours available, may need Day 5.5)

**Complexity Risk Factors:**
- [X] New territory (never generated GAMS code before)
- [X] Multiple external dependencies (GAMS syntax rules, KKT system)
- [X] Unclear requirements (don't know all GAMS edge cases yet)
- [ ] Complex algorithm/math
- [X] Extensive testing needed (need GAMS compiler to validate)

4 checked → Complex

**If Complexity Exceeds Estimate:**
- Trigger: Generated code doesn't compile, or more than 3 edge cases discovered
- Response: Add Day 5.5 for GAMS edge case handling

---

## Day 7.5: [Contingency - Buffer Day]

**Reserved for complexity overruns from Days 5-7.**

If no overruns, use for:
- Additional testing
- Performance optimization
- Documentation improvements
```

### Implementation Steps

1. **Review Sprint 3 plan days 1-10**

2. **For each day:**
   - Assess complexity based on factors above
   - Assign Simple/Medium/Complex
   - Write rationale
   - Estimate time + buffer
   - Check risk factors
   - Define overflow trigger and response

3. **Add contingency days:**
   - Day 7.5: Buffer for Days 5-7 (complex days)
   - Day 9.5: Buffer for Days 8-9 if needed

4. **Calculate total time:**
   - Sum base estimates + buffers
   - Ensure fits in sprint timeline
   - Adjust if over

### Acceptance Criteria

- [ ] All 10 days have complexity rating
- [ ] All ratings have rationale
- [ ] All days have time estimate + buffer
- [ ] Risk factors identified for each
- [ ] Overflow responses defined
- [ ] Contingency days allocated
- [ ] Total time fits sprint

### Expected Outcome

**Sprint 3 Day 5:**
- Plan says "Complex, may need Day 5.5"
- Developer hits 3rd GAMS edge case
- Recognizes complexity exceeding estimate
- Adds Day 5.5 proactively (not reactively)
- **Result:** Stays on schedule, no surprises

---

## Task 10: Create Known Unknowns List for Sprint 3

**Priority:** High  
**Estimated Time:** 1 hour  
**Deadline:** Before Sprint 3 Day 1  
**Owner:** Sprint planning  
**Dependencies:** Task 1 (architecture), Task 2 (parser reference)

### Objective
Create explicit list of assumptions and unknowns for Sprint 3, making risks visible and testable.

### Why This Matters
Sprint 2 assumed power was represented as `Call("power", ...)` when it was actually `Binary("^", ...)`. Listing this as "known unknown" would have prompted investigation before coding.

### Deliverable
**Section in:** `docs/planning/SPRINT_3_PLAN.md`

### Implementation

Add section at top of Sprint 3 plan:

```markdown
# Sprint 3: KKT Synthesis + GAMS MCP Codegen

## Known Unknowns and Assumptions

This section lists assumptions we're making and things we don't know yet.
Each should be investigated before or during relevant day.

### Sprint 1 / Sprint 2 Integration

| Unknown | Assumption | Test/Verify | Priority | Day |
|---------|-----------|-------------|----------|-----|
| How are bounds stored in ModelIR? | In `normalized_bounds` dict, names in `inequalities` list | Check parser reference, verify with `bounds_nlp.gms` example | Critical | Day 1 |
| What's the API for SparseJacobian? | Has `.num_rows`, `.num_cols`, `.values` | Run API contract tests | Critical | Day 1 |
| Do gradient and Jacobian use same variable ordering? | Yes, both use VariableInstanceMapping | Verify in smoke test | High | Day 2 |
| Are Jacobian values symbolic or numeric? | Symbolic (Expr AST nodes) | Check one entry: `type(jacobian.values[(0,0)])` | High | Day 2 |

### GAMS Syntax and Semantics

| Unknown | Assumption | Test/Verify | Priority | Day |
|---------|-----------|-------------|----------|-----|
| What are valid GAMS identifier names? | Alphanumeric + underscore, start with letter | Read GAMS docs, test examples | High | Day 4 |
| How to emit complementarity equations? | Use `=G=` plus Model declaration pairing | Check GAMS MCP docs, test small example | Critical | Day 5 |
| Can we use same identifier for equation and variable? | No, need separate namespaces | Test in GAMS | Medium | Day 5 |
| How to handle INF bounds in GAMS? | Skip or emit as large number? | Check GAMS docs | Medium | Day 6 |
| What's the syntax for equation indexing? | `eq(i).. expr(i) =E= 0;` | Verify with GAMS examples | High | Day 6 |

### KKT System Construction

| Unknown | Assumption | Test/Verify | Priority | Day |
|---------|-----------|-------------|----------|-----|
| How to represent Jacobian transpose in AST? | Sum over rows, or new AST node? | Design decision on Day 1 | High | Day 1 |
| Do we need separate multipliers for each indexed constraint? | Yes, one per row instance | Mathematical correctness check | Critical | Day 2 |
| How to pair complementarity variables? | Match order: Fx.x, Flam.lam, etc. | Check PATH MCP docs | Critical | Day 3 |
| What sign convention for complementarity? | F(x) ⊥ x, both ≥ 0 | Verify with KKT theory | Critical | Day 3 |

### Code Generation

| Unknown | Assumption | Test/Verify | Priority | Day |
|---------|-----------|-------------|----------|-----|
| How to avoid variable/equation name collisions? | Prefix with context: `lam_c1`, `nu_e1` | Test with example, verify uniqueness | High | Day 4 |
| Do we need to declare all sets? | Yes, need set declarations for indices | Check GAMS requirements | High | Day 5 |
| How to emit parameter values? | Not needed for MCP (only structure)? | Verify with GAMS | Medium | Day 6 |
| Can GAMS handle large expressions? | Might need line breaking | Test with complex example | Low | Day 7 |

### End-to-End Integration

| Unknown | Assumption | Test/Verify | Priority | Day |
|---------|-----------|-------------|----------|-----|
| Will generated MCP compile? | Should if syntax correct | Run GAMS compiler (if available) | Critical | Day 8 |
| Will generated MCP solve? | Depends on math correctness + PATH | Run PATH (if available), or manual check | High | Day 8 |
| Are there edge cases we haven't considered? | Probably | Comprehensive test suite on Day 9 | High | Day 9 |

---

## How to Use This List

**Before Each Day:**
1. Review "Known Unknowns" for that day
2. Investigate and verify assumptions FIRST
3. Update table with findings
4. If assumption wrong, adjust plan

**Example Workflow - Day 3:**

1. Morning: Review unknowns for Day 3
2. See: "How to pair complementarity variables?"
3. Read PATH MCP documentation
4. Find: Variables paired in Model declaration: `/ Fx.x, Flam.lam /`
5. Update table: Assumption confirmed ✅
6. Proceed with implementation using correct syntax

**If Assumption Wrong:**

1. Mark in table: ❌ Assumption incorrect
2. Document actual finding
3. Assess impact on plan
4. Adjust implementation approach
5. Consider if Day N.5 needed

---

## Updating This List

As sprint progresses:
- ✅ Mark confirmed assumptions
- ❌ Mark incorrect assumptions (document correct answer)
- Add newly discovered unknowns
- Remove resolved items (move to "Confirmed Knowledge" section)
```

### Implementation Steps

1. **Brainstorm unknowns:**
   - Review Sprint 3 plan
   - For each day, ask "What don't we know?"
   - Check architecture diagram for interface assumptions
   - Check parser reference for any gaps

2. **Categorize unknowns:**
   - Group by topic (Integration, GAMS, KKT, etc.)
   - Prioritize (Critical/High/Medium/Low)
   - Assign to day when it needs to be resolved

3. **Define verification method:**
   - For each unknown, specify how to verify
   - Make it concrete and testable

4. **Add to Sprint 3 plan:**
   - Place at top of plan (high visibility)
   - Reference from relevant days

5. **Review during checkpoints:**
   - Checkpoint 1 (Day 3): Review integration unknowns
   - Checkpoint 2 (Day 6): Review GAMS unknowns
   - Checkpoint 3 (Day 8): Review e2e unknowns

### Example "Known Unknown" Lifecycle

**Day 1 Morning:**
```markdown
| How are bounds stored? | In `normalized_bounds`? | Check parser ref | Critical | Day 1 |
```

**Day 1 Investigation:**
- Check `docs/ir/parser_output_reference.md` (Task 2)
- Check `docs/architecture/SYSTEM_ARCHITECTURE.md` (Task 1)
- Run diagnostic:
  ```python
  model = parse_model_file('examples/bounds_nlp.gms')
  print(model.normalized_bounds)  # Confirmed: bounds are here
  print(model.inequalities)       # Confirmed: bound names in list
  ```

**Day 1 Afternoon:**
```markdown
| How are bounds stored? | ✅ In `normalized_bounds` dict, names in `inequalities` | Verified with bounds_nlp.gms | Critical | Day 1 |
```

### Acceptance Criteria

- [ ] List created with 20+ known unknowns
- [ ] Unknowns categorized by topic
- [ ] Each has assumption, verification method, priority, day
- [ ] Critical unknowns identified for early verification
- [ ] Added to top of Sprint 3 plan
- [ ] Process for updating list defined

### Expected Outcome

**Sprint 3 Day 5 morning:**
- Developer reviews Day 5 unknowns
- Sees: "What are valid GAMS identifier names?"
- Reads GAMS docs before coding
- Learns: Can't start with number, can't use keywords
- Implements name sanitization correctly first try
- **Avoided:** Bug where generated code uses invalid identifier

---

## Summary: Prep Task Execution Order

To minimize dependencies, execute in this order:

1. **Task 1: Create Architecture Diagram** (3 hours)
   - Foundation for other tasks
   - No dependencies

2. **Task 2: Create Parser Output Reference** (2 hours)
   - Foundation for unknowns list
   - No dependencies

3. **Task 3: Refactor Test Organization** (4 hours)
   - Required for Tasks 4 and 6
   - No dependencies

4. **Task 4: Add API Contract Tests** (2 hours)
   - Depends on Task 3
   - Quick after reorganization

5. **Task 5: Create Early Integration Smoke Test** (1 hour)
   - Can be done anytime
   - No dependencies

6. **Task 6: Implement Test Pyramid Visualization** (3 hours)
   - Depends on Task 3
   - Good to see coverage breakdown

7. **Task 10: Create Known Unknowns List** (1 hour)
   - Depends on Tasks 1 and 2
   - Needed for Tasks 7 and 9

8. **Task 9: Add Complexity Estimation** (2 hours)
   - Depends on Task 10 (unknowns inform complexity)
   - No other dependencies

9. **Task 7: Add Integration Risk Sections** (2 hours)
   - Depends on Tasks 1, 2, 10
   - Uses architecture, parser ref, and unknowns

10. **Task 8: Establish Checkpoint Process** (1 hour)
    - Depends on Task 1
    - Final process setup

**Total: 21 hours (~2.5 working days)**

---

## Prep Completion Checklist

Before Sprint 3 Day 1, verify:

- [ ] Architecture diagram created and reviewed
- [ ] Parser output reference complete
- [ ] Test suite reorganized (all tests still pass)
- [ ] API contract tests added and passing
- [ ] Early integration smoke test created
- [ ] Test pyramid script working
- [ ] Known unknowns list created
- [ ] Complexity estimates added to plan
- [ ] Integration risks added to all days
- [ ] Checkpoint process documented
- [ ] All prep artifacts reviewed for quality

**When all checked: Sprint 3 is ready to begin with minimal integration risk.**

---

## Expected Benefits for Sprint 3

With all prep tasks complete:

1. **Faster integration:** Issues caught in hours, not days
2. **Fewer surprises:** Known unknowns listed and investigated early
3. **Better estimates:** Complexity ratings help allocate time
4. **Clearer testing:** Pyramid shows where to add tests
5. **Stronger contracts:** API mismatches caught by CI
6. **Systematic reviews:** Checkpoints prevent late-stage issues

**Estimated time savings in Sprint 3: 2-3 days**  
**Prep time investment: 2.5 days**

**Net benefit: Break even in Sprint 3, significant savings in Sprints 4-5**
