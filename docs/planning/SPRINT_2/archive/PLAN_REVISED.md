# Sprint 2: Differentiation Engine (AD) + Jacobians (REVISED)

**Duration:** 2 weeks (10 working days)  
**Goal:** Build gradients/Jacobians on the IR to support KKT stationarity and constraint Jacobians.

## Overview

Sprint 2 focuses on implementing automatic differentiation (AD) to compute:
- Objective function gradients: ∇f(x)
- Constraint Jacobians: J_g (inequalities), J_h (equalities)
- Support for indexed variables and aggregation operations (sum)
- Sparse Jacobian structures with symbolic AST expressions
- AST evaluation engine for finite-difference validation

## Changes from Original Plan

**Addressing Review Feedback:**

1. **abs() Policy:** Sprint 2 will **reject** `abs()` with a clear error message, consistent with PROJECT_PLAN.md. Smoothing/handling deferred to Sprint 4.
2. **Unary Operators:** Added explicit support for unary `+` and `-` operators on Day 2.
3. **AST Evaluator:** Added AST evaluator implementation on Day 2 (before FD validation needs it).
4. **Objective Expression:** Added explicit handling to locate objective expression from defining equation on Day 7.
5. **NumPy Dependency:** Added task to update `pyproject.toml` dependencies on Day 9.
6. **Bound Equations:** Explicitly included normalized bound equations in Jacobian tasks on Day 8.
7. **Schedule Rebalancing:** Extended sum/sparsity work to 2 days (Days 5-6) and added explicit debugging slack on Day 9.

## Success Metrics

- [ ] Reverse-mode AD correctly differentiates all v1 expression types (excluding abs)
- [ ] Unary +/- operators fully supported
- [ ] AST evaluator can plug concrete values for FD validation
- [ ] Jacobians match finite-difference validation within 1e-6 tolerance
- [ ] Supports indexed sums and multi-dimensional variables/equations
- [ ] Bound-derived equations included in Jacobian structure
- [ ] 60+ unit tests passing (30 derivative rules, 20 sparsity, 10 FD)
- [ ] All Sprint 1 examples produce correct gradients and Jacobians
- [ ] Dependencies documented and updated in pyproject.toml

---

## Day-by-Day Plan

### Day 1 (Monday): AD Foundation & Design

**Goals:**
- Design AD architecture and data structures
- Implement basic AD framework with simple operations

**Tasks:**
1. Create `src/ad/` directory structure
2. Design AD node classes and reverse-mode accumulation strategy
   - Plan for symbolic differentiation (AST → AST transformations)
   - Design `ADContext` to track variable dependencies
3. Implement derivative rules for constants and variable references
   - Constant: derivative is zero
   - Variable: derivative is 1 (or identity)
4. Write initial unit tests for AD framework
5. Document AD architecture and design decisions

**Deliverables:**
- `src/ad/__init__.py`
- `src/ad/ad_core.py` with `ADContext`, symbolic differentiation framework
- `src/ad/derivative_rules.py` (skeleton with const/var rules)
- `tests/ad/test_ad_core.py` with 5-8 basic tests
- `docs/ad_architecture.md` (design notes)

**Acceptance Criteria:**
- Can differentiate `f(x) = x` and `f(x) = c` (constant)
- AD framework outputs symbolic AST expressions as derivatives
- Tests verify derivative of identity and constant functions
- Clear architecture documented for team review

---

### Day 2 (Tuesday): Arithmetic Operations & AST Evaluator

**Goals:**
- Implement AD for basic arithmetic: +, -, *, /
- Add support for unary +/- operators
- Create AST evaluator for plugging in concrete values

**Tasks:**
1. Implement reverse-mode AD for `Binary` AST nodes (add, sub, mul, div)
   - Addition: ∂(a+b)/∂x = ∂a/∂x + ∂b/∂x
   - Subtraction: ∂(a-b)/∂x = ∂a/∂x - ∂b/∂x
   - Multiplication: ∂(a*b)/∂x = b*(∂a/∂x) + a*(∂b/∂x)
   - Division: ∂(a/b)/∂x = (b*(∂a/∂x) - a*(∂b/∂x))/b²
2. Implement AD for `Unary` operators (unary +, unary -)
   - Unary +: ∂(+a)/∂x = ∂a/∂x
   - Unary -: ∂(-a)/∂x = -∂a/∂x
3. Create `src/ad/evaluator.py` - AST evaluator
   - Evaluate expressions given variable and parameter values
   - Handle indexed variables/parameters using value dictionaries
   - Support all v1 expression types
4. Add division by zero domain checks
5. Write comprehensive tests for each operation
6. Write tests for AST evaluator

**Deliverables:**
- AD support for `Binary(+, -, *, /)` and `Unary(+, -)`
- `src/ad/evaluator.py` with `evaluate(expr, var_vals, param_vals)` function
- `tests/ad/test_arithmetic.py` with 12-15 tests
- `tests/ad/test_evaluator.py` with 10-12 tests
- Documentation of derivative formulas in code comments

**Acceptance Criteria:**
- Correctly differentiates: `x + y`, `x - y`, `x * y`, `x / y`, `-x`, `+x`
- Chain rule works: `∂/∂x [(x + y) * (x - y)]`
- Division by zero raises informative error
- AST evaluator correctly computes expression values
- Can evaluate indexed expressions: `x(i) + y(j)`
- All tests pass

**Note:** AST evaluator is needed before Day 9 FD validation, so implementing it early.

---

### Day 3 (Wednesday): Power & Exponential Functions

**Goals:**
- Implement AD for power, exp, log, sqrt functions

**Tasks:**
1. Implement derivative rule for `Call("power", base, exponent)` or `Binary("^", base, exp)`
   - General: ∂(a^b)/∂x = a^b * (b/a * ∂a/∂x + ln(a) * ∂b/∂x)
   - Special case b constant: ∂(a^n)/∂x = n*a^(n-1) * ∂a/∂x
   - Handle edge cases: negative bases with fractional exponents
2. Implement derivative rule for `Call("exp", x)`
   - ∂exp(a)/∂x = exp(a) * ∂a/∂x
3. Implement derivative rule for `Call("log", x)`
   - ∂log(a)/∂x = (1/a) * ∂a/∂x
   - Add domain check: a > 0
4. Implement derivative rule for `Call("sqrt", x)`
   - ∂sqrt(a)/∂x = (1/(2*sqrt(a))) * ∂a/∂x
   - Add domain check: a >= 0
5. Write tests including edge cases and domain violations
6. Test chain rule combinations

**Deliverables:**
- AD support for `power`/`^`, `exp`, `log`, `sqrt`
- Domain validation logic with helpful error messages
- `tests/ad/test_transcendental.py` with 12-15 tests

**Acceptance Criteria:**
- Correctly differentiates: `x^2`, `x^n`, `exp(x)`, `log(x)`, `sqrt(x)`
- Chain rule works: `exp(x^2)`, `log(x + 1)`, `sqrt(x*y)`
- Domain errors caught: `log(-1)`, `sqrt(-1)`
- Power edge cases handled correctly
- All tests pass

---

### Day 4 (Thursday): Trigonometric Functions & abs() Rejection

**Goals:**
- Implement AD for sin, cos, tan
- Add rejection handling for abs() with clear error
- Complete basic function coverage for v1

**Tasks:**
1. Implement derivative rules for `Call("sin", x)`, `Call("cos", x)`, `Call("tan", x)`
   - ∂sin(a)/∂x = cos(a) * ∂a/∂x
   - ∂cos(a)/∂x = -sin(a) * ∂a/∂x
   - ∂tan(a)/∂x = sec²(a) * ∂a/∂x = (1/cos²(a)) * ∂a/∂x
2. Handle tan domain issues (poles at π/2 + nπ) - document limitations
3. Implement `Call("abs", x)` detection and rejection
   - Raise clear error: "abs() is not differentiable; smoothing options available in Sprint 4"
   - Reference PROJECT_PLAN.md Sprint 4 for future support
4. Test chain rule with trig functions
5. Create comprehensive test suite for trig operations
6. Add tests verifying abs() rejection

**Deliverables:**
- AD support for `sin`, `cos`, `tan`
- `abs()` rejection with informative error message
- `tests/ad/test_trigonometric.py` with 10-12 tests
- `tests/ad/test_unsupported.py` with abs() rejection tests
- Complete coverage of all v1 differentiable functions

**Acceptance Criteria:**
- Correctly differentiates: `sin(x)`, `cos(x)`, `tan(x)`
- Chain rule works: `sin(x^2)`, `cos(exp(x))`
- `abs(x)` raises clear, actionable error
- All v1 function derivatives validated (except abs)
- ~35 derivative rule tests passing total

---

### Day 5 (Friday): Sum Aggregation & Indexing (Part 1)

**Goals:**
- Implement AD for `sum(i, expr)` constructs
- Handle indexed variable references
- Begin building index mapping infrastructure

**Tasks:**
1. Design strategy for differentiating sum aggregations
   - Mathematical rule: ∂/∂x sum(i, f(x,i)) = sum(i, ∂f(x,i)/∂x)
   - Derivative of sum is sum of derivatives (linearity)
2. Implement AD for `Sum` AST nodes
   - Process body expression differentiation
   - Preserve index sets in derivative expression
3. Handle indexed variable references in derivatives
   - `∂/∂x(i) VarRef(x, (i,))` → distinguish same variable different indices
4. Begin designing index instance mapping
   - Map variable[indices] → column identifiers
   - Map equation[indices] → row identifiers
5. Write tests with indexed variables and simple sums
6. Document indexing strategy

**Deliverables:**
- AD support for `Sum` expressions (basic cases)
- Index-aware derivative accumulation logic (partial)
- `tests/ad/test_sum_aggregation.py` with 6-8 tests
- Design document for index mapping strategy

**Acceptance Criteria:**
- Correctly differentiates: `sum(i, x(i))`, `sum(i, x(i)^2)`
- Handles constant sums: `sum(i, c*x(i))`
- Tests pass for basic indexed cases
- Index mapping strategy documented

**Note:** Extended to 2 days (Day 5-6) to provide debugging slack for complex indexing.

---

### Day 6 (Monday): Sum Aggregation & Indexing (Part 2)

**Goals:**
- Complete sum/indexing support with nested sums
- Finalize index mapping for sparse Jacobian structure
- Handle cross-product indexing

**Tasks:**
1. Implement nested sum differentiation
   - `sum(i, sum(j, expr))` cases
   - Track multiple index sets
2. Complete index instance mapping
   - Expand domain sets to concrete member tuples
   - Create bijection: (var_name, index_tuple) ↔ column_id
   - Create bijection: (eq_name, index_tuple) ↔ row_id
3. Handle sum over multiple indices: `sum((i,j), expr)`
4. Implement sparsity tracking
   - Track which variables appear in which expressions
   - Build dependency graph for Jacobian structure
5. Write comprehensive tests for complex indexing scenarios
6. Test cross-products and multi-dimensional indexing

**Deliverables:**
- Complete AD support for all `Sum` cases
- Full index mapping implementation
- Sparsity tracking infrastructure
- `tests/ad/test_sum_aggregation.py` with 12-15 tests total
- `tests/ad/test_index_mapping.py` with 8-10 tests

**Acceptance Criteria:**
- Correctly differentiates: `sum(i, sum(j, x(i)*y(j)))`
- Handles: `sum((i,j), x(i,j)^2)`
- Index mapping deterministic and reproducible
- Sparsity pattern correctly identifies variable dependencies
- All indexing tests pass

---

### Day 7 (Tuesday): Jacobian Structure & Objective Gradient

**Goals:**
- Build Jacobian matrix sparse structure
- Implement objective gradient computation
- Handle objective expression retrieval from IR

**Tasks:**
1. Create `src/ad/jacobian.py` module
2. Design `JacobianStructure` class for sparse storage
   - Store as dict: `J[row_id][col_id] = derivative_expr (AST)`
   - Maintain row/column index maps
3. Implement `compute_objective_gradient()` function
   - Locate objective expression from `ObjectiveIR`
   - If `ObjectiveIR.expr` is None, find defining equation for `objvar`
   - Handle case where objvar has a dedicated equation
4. Handle objective sense: max → multiply gradient by -1 (or negate objective)
5. Create gradient vector indexed by all variable instances
6. Handle scalar vs. indexed objective variables
7. Write tests for Jacobian structure construction
8. Write tests for objective gradients on Sprint 1 examples

**Deliverables:**
- `src/ad/jacobian.py` with `JacobianStructure` class
- `src/ad/gradient.py` with objective gradient computation
- Objective expression retrieval logic
- `tests/ad/test_jacobian_structure.py` with 8-10 tests
- `tests/ad/test_gradient.py` with 10-12 tests

**Acceptance Criteria:**
- Can build sparse Jacobian structure for scalar equations
- Correct gradient for: `min x^2`, `max -x^2`
- Handles indexed objectives: `min sum(i, x(i)^2)`
- Successfully retrieves objective expression from IR (handles both explicit expr and objvar equation)
- Gradient structure matches variable index map
- Deterministic row/column ordering (sorted)

---

### Day 8 (Wednesday): Constraint Jacobian Computation

**Goals:**
- Compute full Jacobians for equality and inequality constraints
- Include normalized bound equations
- Integrate with normalized IR from Sprint 1

**Tasks:**
1. Implement `compute_constraint_jacobian()` function
2. Process all equality constraints (h(x) = 0) → J_h
   - Iterate through `ModelIR.equalities`
   - Differentiate each equation w.r.t. all variables
3. Process all inequality constraints (g(x) ≤ 0) → J_g
   - Iterate through `ModelIR.inequalities`
   - Handle normalized form from Sprint 1
4. **Include bound-derived equations**
   - Process `ModelIR.normalized_bounds` (from normalize.py:49)
   - Add bound constraint rows to appropriate Jacobian (J_g for inequalities)
   - Ensure bound equations: `x - lo >= 0` and `up - x >= 0` enter Jacobian
5. Handle indexed constraints correctly
   - Expand each indexed equation to multiple rows
6. Ensure sparsity pattern is optimal (only nonzero entries)
7. Test on all Sprint 1 examples
8. Verify bound equations appear in Jacobian

**Deliverables:**
- Full Jacobian computation for constraint systems
- Bound equation handling in Jacobian
- Integration tests with Sprint 1 IR
- `tests/ad/test_constraint_jacobian.py` with 12-15 tests
- `tests/ad/test_bound_jacobian.py` with 6-8 tests

**Acceptance Criteria:**
- Correct Jacobians for all 5 Sprint 1 examples
- Bound-derived rows appear in J_g with correct derivatives
- Sparsity pattern matches expected nonzero structure
- Handles empty constraint sets gracefully
- Indexed constraints properly expanded to rows
- All tests pass

---

### Day 9 (Thursday): Numeric Validation, Testing & Dependencies

**Goals:**
- Comprehensive finite-difference validation
- Edge case testing and error handling
- Update dependencies in pyproject.toml

**Tasks:**
1. Implement finite-difference checker utility
   - Use AST evaluator from Day 2
   - Compute numerical derivatives: f'(x) ≈ (f(x+h) - f(x-h))/(2h)
   - Compare AD results with FD results
2. Run FD validation on all derivative rules
3. Test numeric stability on boundary cases
   - Near-zero values, large values
   - Domain boundaries (log near 0, sqrt near 0, etc.)
4. Add tests for degenerate cases:
   - Constant expressions (zero derivatives)
   - Variables that don't appear in constraints
   - Empty sums
5. **Update `pyproject.toml` dependencies**
   - Add `numpy` for FD validation and numeric operations
   - Document version requirements
   - Consider pure-Python fallback strategy (document if not implemented)
6. Performance testing on larger indexed models
   - Test with 100+ variables and constraints
   - Profile hot paths if needed
7. Debugging slack: fix any discovered bugs from Days 5-8
8. Address any FD mismatches or indexing issues

**Deliverables:**
- `tests/ad/test_finite_difference.py` with 12-15 validation tests
- `src/ad/validation.py` with FD checker utilities
- Updated `pyproject.toml` with numpy dependency
- Bug fixes and edge case handling
- Performance profiling results (documented)

**Acceptance Criteria:**
- All derivative rules validated against FD within 1e-6 tolerance
- Edge cases handled gracefully with clear errors
- No false positives/negatives in derivative computation
- Performance acceptable for 100+ variable/constraint models
- Dependencies documented and updated
- All discovered bugs fixed
- ~55 tests passing

---

### Day 10 (Friday): Integration, Documentation & Polish

**Goals:**
- Integrate AD with main codebase
- Complete documentation
- Final testing and cleanup

**Tasks:**
1. Create high-level API for external use:
   - `compute_derivatives(model_ir) → (gradient, jacobian_g, jacobian_h)`
   - Clean interface hiding internal complexity
2. Write integration tests using full NLP→AD pipeline
   - Load GAMS file → parse → normalize → compute derivatives
   - End-to-end tests on all Sprint 1 examples
3. Add comprehensive docstrings to all public functions and classes
   - Include mathematical formulas
   - Document assumptions and limitations
   - Add usage examples
4. Create/update documentation:
   - `docs/ad_design.md` explaining AD architecture and algorithms
   - Document index mapping strategy
   - Document derivative rules reference
   - Add FD validation methodology
5. Update main README with Sprint 2 completion status
6. Code cleanup and refactoring
   - Remove dead code
   - Improve naming consistency
   - Add type hints throughout
7. Final test suite run and validation
8. Code review preparation

**Deliverables:**
- `src/ad/api.py` with clean public interface
- Complete docstrings and type hints throughout `src/ad/`
- `docs/ad_design.md` comprehensive documentation
- `docs/derivative_rules.md` reference guide
- Updated README.md
- All 60+ tests passing
- Code ready for review and merge

**Acceptance Criteria:**
- Clean API: `gradient, J_g, J_h = compute_derivatives(model_ir)`
- All public functions documented with docstrings
- Mathematical formulas documented for all derivative rules
- Test coverage > 90%
- All Sprint 2 acceptance criteria met:
  - ✅ All v1 functions differentiated (except abs - rejected)
  - ✅ Unary operators supported
  - ✅ AST evaluator working
  - ✅ Jacobians validated with FD
  - ✅ Indexed sums/variables supported
  - ✅ Bound equations in Jacobians
  - ✅ 60+ tests passing
  - ✅ Dependencies updated
- Ready for Sprint 3 (KKT synthesis)

---

## File Structure

```
src/ad/
├── __init__.py           # Public API exports
├── ad_core.py            # Core AD framework, ADContext
├── derivative_rules.py   # Derivative rules for all operations
├── evaluator.py          # AST evaluator for plugging concrete values
├── gradient.py           # Objective gradient computation
├── jacobian.py          # Jacobian structure and computation
├── validation.py        # Finite-difference validation utilities
└── api.py               # High-level public API

tests/ad/
├── test_ad_core.py              # Core framework tests
├── test_arithmetic.py           # Binary +,-,*,/ and Unary +,- tests
├── test_evaluator.py            # AST evaluator tests
├── test_transcendental.py       # Power, exp, log, sqrt tests
├── test_trigonometric.py        # Sin, cos, tan tests
├── test_unsupported.py          # abs() rejection tests
├── test_sum_aggregation.py      # Sum and indexing tests
├── test_index_mapping.py        # Index mapping tests
├── test_jacobian_structure.py   # Jacobian structure tests
├── test_gradient.py             # Objective gradient tests
├── test_constraint_jacobian.py  # Constraint Jacobian tests
├── test_bound_jacobian.py       # Bound equation Jacobian tests
├── test_finite_difference.py    # FD validation tests
└── test_integration.py          # End-to-end integration tests

docs/
├── ad_design.md          # AD architecture and design
├── ad_architecture.md    # Initial design notes (Day 1)
└── derivative_rules.md   # Derivative formulas reference
```

---

## Testing Strategy

### Unit Tests (~35 derivative rule tests)
- Each operation tested independently
- Unary operators (+, -)
- Binary operators (+, -, *, /)
- Functions (exp, log, sqrt, sin, cos, tan, power)
- abs() rejection
- Chain rule combinations
- Edge cases and domain boundaries

### Indexing & Sum Tests (~15 tests)
- Basic sums
- Nested sums
- Multi-index sums
- Index mapping correctness

### Sparsity & Structure Tests (~10 tests)
- Jacobian structure correctness
- Index mapping verification
- Sparse vs. dense comparison
- Row/column ordering

### Numeric Validation (~12 FD tests)
- Finite-difference agreement
- Random coefficient tests
- Tolerance checks (±1e-6)
- Boundary value testing

### Integration Tests (~8 tests)
- Full NLP model → derivatives pipeline
- All Sprint 1 examples validated
- Bound equation handling
- End-to-end workflow

**Total: 60+ tests**

---

## Dependencies

**From Sprint 1:**
- `ModelIR` with normalized equations and bounds
- Expression AST nodes (Const, VarRef, ParamRef, Binary, Unary, Sum, Call)
- Symbol table with set/variable/equation metadata
- `NormalizedEquation` from normalize.py
- `ObjectiveIR` with sense and objvar (expr may be None)

**External Libraries (to be added to pyproject.toml):**
- `numpy` >= 1.24.0 (for numeric validation and FD)
  - Used in finite-difference validation
  - Used for numeric operations in evaluator
  - Document as required dependency
- `pytest` >= 7.4.4 (already present, for testing)

**Optional:**
- `scipy.sparse` (future optimization, not Sprint 2)

---

## Risk Mitigation

| Risk | Mitigation | Status |
|------|------------|--------|
| Complex indexing breaks AD | Two-day allocation (Days 5-6) with comprehensive tests | Addressed in revision |
| Numeric instability | Domain checks, validation tests on Day 9 | Original plan |
| Performance issues | Profile on Day 9, defer optimization if needed | Original plan |
| Incomplete test coverage | Daily test writing, 60+ target with coverage tracking | Original plan |
| Integration issues with Sprint 1 | Integration tests throughout, especially Days 8-10 | Original plan |
| abs() confusion | Clear rejection error message with Sprint 4 reference | Added in revision |
| Unary operator oversight | Explicit Day 2 task for unary +/- | Added in revision |
| Missing AST evaluator | Implemented early on Day 2, before FD needs it | Added in revision |
| Objective expression not found | Explicit task to locate from defining equation | Added in revision |
| Dependency documentation | Update pyproject.toml on Day 9, document requirements | Added in revision |
| Bound equations missed | Explicit inclusion in Day 8 tasks and tests | Added in revision |
| Schedule too tight | Extended sum/indexing to 2 days, debugging slack on Day 9 | Added in revision |

---

## Definition of Done

- [ ] All v1 functions have reverse-mode AD implementation (exp, log, sqrt, sin, cos, tan, power, arithmetic)
- [ ] Unary +/- operators supported
- [ ] abs() rejected with clear, informative error message
- [ ] AST evaluator implemented and tested
- [ ] Sum aggregation and indexing fully supported
- [ ] Nested sums and multi-dimensional indexing working
- [ ] Jacobian sparsity structure correct for all test cases
- [ ] Objective gradient computation handles min/max
- [ ] Objective expression successfully retrieved from IR (handles None case)
- [ ] Normalized bound equations included in Jacobian
- [ ] 60+ unit tests passing with >90% coverage
- [ ] All 5 Sprint 1 examples produce validated gradients/Jacobians
- [ ] Finite-difference validation within 1e-6 for all examples
- [ ] Dependencies updated in pyproject.toml
- [ ] Public API documented and ready for Sprint 3
- [ ] Code reviewed and merged to main

---

## Next Sprint Preview

**Sprint 3** will use the AD engine to:
- Assemble KKT stationarity conditions using ∇f and constraint Jacobians (J_g, J_h)
- Generate Lagrange multiplier variables (λ, ν) for each constraint row
- Handle bound multipliers (π^L, π^U) using bound equation Jacobians
- Emit GAMS MCP code with complementarity pairs
- Create end-to-end NLP→MCP conversion pipeline

The derivatives computed in Sprint 2 are the foundation for the entire KKT system!

---

## Summary of Revisions

1. ✅ **abs() policy clarified**: Reject with clear error, defer to Sprint 4
2. ✅ **Unary operators added**: Explicit Day 2 tasks for unary +/-
3. ✅ **AST evaluator added**: Day 2 implementation before FD validation
4. ✅ **Objective expression handling**: Day 7 task to locate from IR/equation
5. ✅ **Dependencies updated**: Day 9 task to update pyproject.toml with numpy
6. ✅ **Bound equations included**: Day 8 explicit tasks and tests
7. ✅ **Schedule rebalanced**: Sum/indexing extended to 2 days (5-6), Day 9 has debugging slack
8. ✅ **All review feedback addressed**: See risk mitigation table
