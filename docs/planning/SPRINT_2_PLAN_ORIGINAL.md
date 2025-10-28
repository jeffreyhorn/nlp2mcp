# Sprint 2: Differentiation Engine (AD) + Jacobians

**Duration:** 2 weeks (10 working days)  
**Goal:** Build gradients/Jacobians on the IR to support KKT stationarity and constraint Jacobians.

## Overview

Sprint 2 focuses on implementing automatic differentiation (AD) to compute:
- Objective function gradients: ∇f(x)
- Constraint Jacobians: J_g (inequalities), J_h (equalities)
- Support for indexed variables and aggregation operations (sum)
- Sparse Jacobian structures with symbolic AST expressions

## Success Metrics

- [ ] Reverse-mode AD correctly differentiates all v1 expression types
- [ ] Jacobians match finite-difference validation within 1e-6 tolerance
- [ ] Supports indexed sums and multi-dimensional variables/equations
- [ ] 60+ unit tests passing (30 derivative rules, 20 sparsity, 10 numeric FD)
- [ ] All Sprint 1 examples produce correct gradients and Jacobians

---

## Day-by-Day Plan

### Day 1 (Monday): AD Foundation & Design

**Goals:**
- Design AD architecture and data structures
- Implement basic AD framework with simple operations

**Tasks:**
1. Create `src/ad/` directory structure
2. Design AD node classes and reverse-mode accumulation strategy
3. Implement `ADContext` class for managing derivative computation
4. Implement derivative rules for constants and variable references
5. Write initial unit tests for AD framework

**Deliverables:**
- `src/ad/__init__.py`
- `src/ad/ad_core.py` with `ADContext`, `ADNode` base classes
- `src/ad/derivative_rules.py` (skeleton)
- `tests/ad/test_ad_core.py` with 5-10 basic tests

**Acceptance Criteria:**
- Can differentiate `f(x) = x` and `f(x) = c` (constant)
- AD context properly tracks computational graph
- Tests verify derivative of identity and constant functions

---

### Day 2 (Tuesday): Arithmetic Operations

**Goals:**
- Implement AD for basic arithmetic: +, -, *, /

**Tasks:**
1. Implement reverse-mode AD for `Binary` AST nodes (add, sub, mul, div)
2. Add derivative rules for arithmetic operations
3. Handle division by zero gracefully (domain checks)
4. Write comprehensive tests for each operation
5. Test chain rule through multiple operations

**Deliverables:**
- AD support for `BinaryOp(+, -, *, /)`
- `tests/ad/test_arithmetic.py` with 10-15 tests
- Documentation of derivative formulas in code comments

**Acceptance Criteria:**
- Correctly differentiates: `x + y`, `x - y`, `x * y`, `x / y`
- Chain rule works: `∂/∂x [(x + y) * (x - y)]`
- Division by zero raises informative error
- All tests pass with FD validation

---

### Day 3 (Wednesday): Power & Exponential Functions

**Goals:**
- Implement AD for power, exp, log functions

**Tasks:**
1. Implement derivative rule for `pow(base, exponent)`
   - Handle special cases: integer exponents, negative bases
2. Implement derivative rule for `exp(x)`
3. Implement derivative rule for `log(x)`
   - Add domain check: x > 0
4. Implement derivative rule for `sqrt(x)` (special case of pow)
5. Write tests including edge cases and domain violations

**Deliverables:**
- AD support for `pow`, `exp`, `log`, `sqrt`
- `tests/ad/test_transcendental.py` with 10-12 tests
- Domain validation logic with helpful error messages

**Acceptance Criteria:**
- Correctly differentiates: `x^2`, `x^n`, `exp(x)`, `log(x)`, `sqrt(x)`
- Chain rule works: `exp(x^2)`, `log(x + 1)`
- Domain errors caught: `log(-1)`, `sqrt(-1)`
- FD validation passes for all functions

---

### Day 4 (Thursday): Trigonometric Functions

**Goals:**
- Implement AD for sin, cos, tan
- Complete basic function coverage for v1

**Tasks:**
1. Implement derivative rules for `sin(x)`, `cos(x)`, `tan(x)`
2. Handle tan domain issues (poles at π/2 + nπ)
3. Test chain rule with trig functions
4. Create comprehensive test suite for trig operations
5. Document any numerical stability considerations

**Deliverables:**
- AD support for `sin`, `cos`, `tan`
- `tests/ad/test_trigonometric.py` with 8-10 tests
- Complete coverage of all v1 unary functions

**Acceptance Criteria:**
- Correctly differentiates: `sin(x)`, `cos(x)`, `tan(x)`
- Chain rule works: `sin(x^2)`, `cos(exp(x))`
- All v1 function derivatives validated
- ~30 derivative rule tests passing total

---

### Day 5 (Friday): Sum Aggregation & Indexing

**Goals:**
- Implement AD for `sum(i, expr)` constructs
- Handle indexed variable references

**Tasks:**
1. Design strategy for differentiating sum aggregations
   - Derivative of sum is sum of derivatives
2. Implement AD for `SumExpr` AST nodes
3. Handle index set iteration and variable instance mapping
4. Track sparsity: which variables appear in which sums
5. Write tests with indexed variables and nested sums

**Deliverables:**
- AD support for `SumExpr` nodes
- Index-aware derivative accumulation logic
- `tests/ad/test_sum_aggregation.py` with 8-10 tests

**Acceptance Criteria:**
- Correctly differentiates: `sum(i, x(i))`, `sum(i, x(i)^2)`
- Handles: `sum(i, sum(j, x(i) * y(j)))`
- Sparse derivative structure correctly tracks variable instances
- All tests pass

---

### Day 6 (Monday): Jacobian Structure & Sparsity

**Goals:**
- Build Jacobian matrix structure from equation derivatives
- Implement sparse storage and indexing

**Tasks:**
1. Create `src/ad/jacobian.py` module
2. Design `JacobianStructure` class for sparse storage
3. Implement equation indexing: map equation[index] → row number
4. Implement variable indexing: map variable[index] → column number
5. Build sparse map: `J[eq_row][var_col] = derivative_ast`
6. Write tests for Jacobian construction

**Deliverables:**
- `src/ad/jacobian.py` with `JacobianStructure` class
- Row/column index mapping utilities
- `tests/ad/test_jacobian_structure.py` with 10-12 tests

**Acceptance Criteria:**
- Can build Jacobian for scalar equations
- Can build Jacobian for indexed equations
- Sparse structure correctly identifies nonzero entries
- Deterministic ordering (sorted by set members)

---

### Day 7 (Tuesday): Objective Gradient Computation

**Goals:**
- Compute gradients of objective function
- Handle minimization vs. maximization

**Tasks:**
1. Implement `compute_objective_gradient()` function
2. Handle objective sense: max → multiply by -1
3. Create gradient vector indexed by all variable instances
4. Handle scalar vs. indexed objective variables
5. Write tests for objective gradients on Sprint 1 examples

**Deliverables:**
- `src/ad/gradient.py` with gradient computation
- Support for both `min` and `max` objectives
- `tests/ad/test_gradient.py` with 8-10 tests

**Acceptance Criteria:**
- Correct gradient for: `min x^2`, `max -x^2`
- Handles indexed objectives: `min sum(i, x(i)^2)`
- Gradient structure matches variable index map
- FD validation passes

---

### Day 8 (Wednesday): Constraint Jacobian Computation

**Goals:**
- Compute full Jacobians for equality and inequality constraints
- Integrate with normalized IR from Sprint 1

**Tasks:**
1. Implement `compute_constraint_jacobian()` function
2. Process all equality constraints (h(x) = 0) → J_h
3. Process all inequality constraints (g(x) ≤ 0) → J_g
4. Handle indexed constraints correctly
5. Ensure sparsity pattern is optimal (only nonzero entries)
6. Test on all Sprint 1 examples

**Deliverables:**
- Full Jacobian computation for constraint systems
- Integration tests with Sprint 1 IR
- `tests/ad/test_constraint_jacobian.py` with 10-12 tests

**Acceptance Criteria:**
- Correct Jacobians for all 5 Sprint 1 examples
- Sparsity pattern matches expected nonzero structure
- FD validation within 1e-6 tolerance
- Handles empty constraint sets gracefully

---

### Day 9 (Thursday): Numeric Validation & Testing

**Goals:**
- Comprehensive finite-difference validation
- Edge case testing and error handling

**Tasks:**
1. Implement finite-difference checker utility
2. Run FD validation on all derivative rules
3. Test numeric stability on boundary cases
   - Near-zero values, large values
   - Domain boundaries (log near 0, etc.)
4. Add tests for degenerate cases:
   - Constant expressions (zero derivatives)
   - Variables that don't appear in constraints
5. Performance testing on larger indexed models
6. Fix any discovered bugs

**Deliverables:**
- `tests/ad/test_finite_difference.py` with 10+ validation tests
- `src/ad/validation.py` with FD checker utilities
- Bug fixes and edge case handling

**Acceptance Criteria:**
- All derivative rules validated against FD
- Edge cases handled gracefully with clear errors
- No false positives/negatives in derivative computation
- Performance acceptable for 100+ variable/constraint models

---

### Day 10 (Friday): Integration, Documentation & Polish

**Goals:**
- Integrate AD with main codebase
- Complete documentation
- Final testing and cleanup

**Tasks:**
1. Create high-level API for external use:
   - `compute_derivatives(model_ir) → (gradient, jacobian_g, jacobian_h)`
2. Write integration tests using full NLP→AD pipeline
3. Add docstrings to all public functions and classes
4. Create `docs/ad_design.md` explaining AD architecture
5. Update main README with AD completion status
6. Code cleanup and refactoring
7. Final test suite run and validation

**Deliverables:**
- `src/ad/api.py` with clean public interface
- Complete docstrings and type hints
- `docs/ad_design.md` documentation
- Updated README
- All 60+ tests passing

**Acceptance Criteria:**
- Clean API for computing gradients and Jacobians from ModelIR
- All public functions documented
- Test coverage > 90%
- All Sprint 2 acceptance criteria met
- Ready for Sprint 3 (KKT synthesis)

---

## File Structure

```
src/ad/
├── __init__.py           # Public API exports
├── ad_core.py            # Core AD framework, ADContext, ADNode
├── derivative_rules.py   # Derivative rules for all operations
├── gradient.py           # Objective gradient computation
├── jacobian.py          # Jacobian structure and computation
├── validation.py        # Finite-difference validation utilities
└── api.py               # High-level public API

tests/ad/
├── test_ad_core.py
├── test_arithmetic.py
├── test_transcendental.py
├── test_trigonometric.py
├── test_sum_aggregation.py
├── test_jacobian_structure.py
├── test_gradient.py
├── test_constraint_jacobian.py
├── test_finite_difference.py
└── test_integration.py
```

---

## Testing Strategy

### Unit Tests (~30 derivative rule tests)
- Each operation tested independently
- Chain rule combinations
- Edge cases and domain boundaries

### Sparsity Tests (~20 tests)
- Jacobian structure correctness
- Index mapping verification
- Sparse vs. dense comparison

### Numeric Validation (~10 FD tests)
- Finite-difference agreement
- Random coefficient tests
- Tolerance checks (±1e-6)

### Integration Tests (~5 tests)
- Full NLP model → derivatives pipeline
- All Sprint 1 examples validated
- End-to-end workflow

---

## Dependencies

**From Sprint 1:**
- `ModelIR` with normalized equations and bounds
- Expression AST nodes (Const, VarRef, ParamRef, Binary, Unary, Sum)
- Symbol table with set/variable/equation metadata

**External Libraries:**
- `numpy` (for numeric validation and FD)
- `pytest` (testing framework)

**Optional:**
- `scipy.sparse` (if we want sparse matrix representation)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Complex indexing breaks AD | Comprehensive index mapping tests on Day 5-6 |
| Numeric instability | Domain checks, validation tests on Day 9 |
| Performance issues | Profile on Day 9, optimize hot paths |
| Incomplete test coverage | Daily test writing, coverage tracking |
| Integration issues with Sprint 1 | Integration tests starting Day 8 |

---

## Definition of Done

- [ ] All v1 functions have reverse-mode AD implementation
- [ ] Sum aggregation and indexing fully supported
- [ ] Jacobian sparsity structure correct for all test cases
- [ ] Objective gradient computation handles min/max
- [ ] 60+ unit tests passing with >90% coverage
- [ ] All 5 Sprint 1 examples produce validated gradients/Jacobians
- [ ] Finite-difference validation within 1e-6 for all examples
- [ ] Public API documented and ready for Sprint 3
- [ ] Code reviewed and merged to main

---

## Next Sprint Preview

**Sprint 3** will use the AD engine to:
- Assemble KKT stationarity conditions using ∇f and constraint Jacobians
- Generate Lagrange multiplier variables for each constraint
- Emit GAMS MCP code with complementarity pairs
- Create end-to-end NLP→MCP conversion pipeline

The derivatives computed in Sprint 2 are the foundation for the entire KKT system!
