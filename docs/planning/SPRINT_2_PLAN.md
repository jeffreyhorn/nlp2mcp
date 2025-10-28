# Sprint 2: Differentiation Engine (AD) + Jacobians (FINAL)

**Duration:** 2 weeks (10 working days)  
**Goal:** Build gradients/Jacobians on the IR to support KKT stationarity and constraint Jacobians.

## Overview

Sprint 2 focuses on implementing symbolic automatic differentiation (AD) to compute:
- Objective function gradients: ∇f(x)
- Constraint Jacobians: J_g (inequalities), J_h (equalities)
- Support for indexed variables and aggregation operations (sum)
- Sparse Jacobian structures with symbolic AST expressions
- AST evaluation engine for finite-difference validation
- NaN/Inf detection and safety checks

**Differentiation Strategy:** This sprint implements **symbolic differentiation** (AST → AST transformations), not traditional reverse-mode adjoint AD. Each derivative operation transforms one AST into another AST representing the derivative expression.

## Changes from Revised Plan

**Addressing Final Review Feedback:**

1. **Differentiation approach clarified:** Updated terminology throughout to use "symbolic differentiation" rather than "reverse-mode AD" to match implementation intent.
2. **Finite-difference seed points:** Added Day 9 sub-task to define deterministic FD seed points with reproducible random seeding strategy.
3. **Alias resolution:** Extended Day 6 indexing work to explicitly handle `ModelIR.aliases` and alias universes for proper Jacobian enumeration.
4. **NaN/Inf detection:** Added Day 2 task to implement safety checks in evaluator, with additional validation on Day 9.

## Success Metrics

- [ ] Symbolic differentiation correctly differentiates all v1 expression types (excluding abs)
- [ ] Unary +/- operators fully supported
- [ ] AST evaluator can plug concrete values for FD validation
- [ ] NaN/Inf detection with actionable error messages
- [ ] Jacobians match finite-difference validation within 1e-6 tolerance
- [ ] Supports indexed sums and multi-dimensional variables/equations
- [ ] Alias resolution correctly handles aliased sets in index mapping
- [ ] Bound-derived equations included in Jacobian structure
- [ ] 60+ unit tests passing (30 derivative rules, 20 sparsity, 10 FD)
- [ ] All Sprint 1 examples produce correct gradients and Jacobians
- [ ] Dependencies documented and updated in pyproject.toml

---

## Day-by-Day Plan

### Day 1 (Monday): AD Foundation & Design

**Goals:**
- Design symbolic differentiation architecture and data structures
- Implement basic AD framework with simple operations

**Tasks:**
1. Create `src/ad/` directory structure
2. Design symbolic differentiation strategy (AST → AST transformations)
   - Document why symbolic approach chosen over adjoint-style reverse-mode
   - Plan for differentiating one AST node type at a time
   - Design `differentiate(expr, wrt_var)` → returns new AST
3. Implement derivative rules for constants and variable references
   - Constant: derivative is `Const(0)`
   - Variable x w.r.t. x: derivative is `Const(1)`
   - Variable y w.r.t. x: derivative is `Const(0)`
4. Write initial unit tests for AD framework
5. Document AD architecture and design decisions

**Deliverables:**
- `src/ad/__init__.py`
- `src/ad/ad_core.py` with symbolic differentiation framework
- `src/ad/derivative_rules.py` (skeleton with const/var rules)
- `tests/ad/test_ad_core.py` with 5-8 basic tests
- `docs/ad_architecture.md` (design notes explaining symbolic approach)

**Acceptance Criteria:**
- Can differentiate `f(x) = x` and `f(x) = c` (constant)
- Symbolic differentiation outputs AST expressions
- Tests verify derivative of identity and constant functions
- Clear architecture documented explaining symbolic vs. adjoint approach
- Documentation updates prepared for PROJECT_PLAN.md reference

---

### Day 2 (Tuesday): Arithmetic Operations, AST Evaluator & Safety

**Goals:**
- Implement AD for basic arithmetic: +, -, *, /
- Add support for unary +/- operators
- Create AST evaluator for plugging in concrete values
- Implement NaN/Inf detection and safety checks

**Tasks:**
1. Implement symbolic differentiation for `Binary` AST nodes (add, sub, mul, div)
   - Addition: d(a+b)/dx = da/dx + db/dx
   - Subtraction: d(a-b)/dx = da/dx - db/dx
   - Multiplication: d(a*b)/dx = b*(da/dx) + a*(db/dx) (product rule)
   - Division: d(a/b)/dx = (b*(da/dx) - a*(db/dx))/b² (quotient rule)
2. Implement symbolic differentiation for `Unary` operators (unary +, unary -)
   - Unary +: d(+a)/dx = da/dx
   - Unary -: d(-a)/dx = -da/dx
3. Create `src/ad/evaluator.py` - AST evaluator
   - Evaluate expressions given variable and parameter values
   - Handle indexed variables/parameters using value dictionaries
   - Support all v1 expression types
   - **Implement NaN/Inf detection:**
     - Check for NaN/Inf in all arithmetic operations
     - Raise clear errors: "NaN detected in expression evaluation at [location]"
     - Check domain violations: division by zero, log of negative, etc.
4. Add division by zero domain checks
5. Write comprehensive tests for each operation
6. Write tests for AST evaluator including NaN/Inf cases

**Deliverables:**
- Symbolic differentiation for `Binary(+, -, *, /)` and `Unary(+, -)`
- `src/ad/evaluator.py` with `evaluate(expr, var_vals, param_vals)` function
- NaN/Inf detection and error reporting
- `tests/ad/test_arithmetic.py` with 12-15 tests
- `tests/ad/test_evaluator.py` with 12-15 tests (including NaN/Inf cases)
- Documentation of derivative formulas in code comments

**Acceptance Criteria:**
- Correctly differentiates: `x + y`, `x - y`, `x * y`, `x / y`, `-x`, `+x`
- Chain rule works: `d/dx [(x + y) * (x - y)]`
- Division by zero raises informative error
- AST evaluator correctly computes expression values
- Can evaluate indexed expressions: `x(i) + y(j)`
- NaN/Inf detected and reported with actionable errors
- All tests pass

**Note:** AST evaluator and safety checks implemented early before FD validation needs them.

---

### Day 3 (Wednesday): Power & Exponential Functions

**Goals:**
- Implement symbolic differentiation for power, exp, log, sqrt functions

**Tasks:**
1. Implement derivative rule for `Call("power", base, exp)` or `Binary("^", base, exp)`
   - General case: d(a^b)/dx = a^b * (b/a * da/dx + ln(a) * db/dx)
   - Constant exponent optimization: d(a^n)/dx = n*a^(n-1) * da/dx
   - Handle edge cases: negative bases with fractional exponents
2. Implement derivative rule for `Call("exp", x)`
   - d(exp(a))/dx = exp(a) * da/dx
3. Implement derivative rule for `Call("log", x)`
   - d(log(a))/dx = (1/a) * da/dx
   - Add domain check: a > 0
4. Implement derivative rule for `Call("sqrt", x)`
   - d(sqrt(a))/dx = (1/(2*sqrt(a))) * da/dx
   - Add domain check: a >= 0
5. Write tests including edge cases and domain violations
6. Test chain rule combinations

**Deliverables:**
- Symbolic differentiation for `power`/`^`, `exp`, `log`, `sqrt`
- Domain validation logic with helpful error messages
- `tests/ad/test_transcendental.py` with 12-15 tests

**Acceptance Criteria:**
- Correctly differentiates: `x^2`, `x^n`, `exp(x)`, `log(x)`, `sqrt(x)`
- Chain rule works: `exp(x^2)`, `log(x + 1)`, `sqrt(x*y)`
- Domain errors caught: `log(-1)`, `sqrt(-1)`
- Power edge cases handled correctly
- Constant exponent optimization generates simpler ASTs
- All tests pass

---

### Day 4 (Thursday): Trigonometric Functions & abs() Rejection

**Goals:**
- Implement symbolic differentiation for sin, cos, tan
- Add rejection handling for abs() with clear error
- Complete basic function coverage for v1

**Tasks:**
1. Implement derivative rules for `Call("sin", x)`, `Call("cos", x)`, `Call("tan", x)`
   - d(sin(a))/dx = cos(a) * da/dx
   - d(cos(a))/dx = -sin(a) * da/dx
   - d(tan(a))/dx = sec²(a) * da/dx = (1/cos²(a)) * da/dx
2. Handle tan domain issues (poles at π/2 + nπ)
   - Document limitations in docstrings
   - Add domain warning (optional runtime check)
3. Implement `Call("abs", x)` detection and rejection
   - Raise clear error: "abs() is not differentiable everywhere; use smoothing options in Sprint 4 (--smooth-abs flag)"
   - Reference PROJECT_PLAN.md Sprint 4 for future support
   - Include link to documentation about smooth approximations
4. Test chain rule with trig functions
5. Create comprehensive test suite for trig operations
6. Add tests verifying abs() rejection with helpful message

**Deliverables:**
- Symbolic differentiation for `sin`, `cos`, `tan`
- `abs()` rejection with informative, actionable error message
- `tests/ad/test_trigonometric.py` with 10-12 tests
- `tests/ad/test_unsupported.py` with abs() rejection tests (4-6 tests)
- Complete coverage of all v1 differentiable functions

**Acceptance Criteria:**
- Correctly differentiates: `sin(x)`, `cos(x)`, `tan(x)`
- Chain rule works: `sin(x^2)`, `cos(exp(x))`
- `abs(x)` raises clear, actionable error referencing Sprint 4
- Error message includes helpful guidance on future support
- All v1 function derivatives validated (except abs)
- ~35 derivative rule tests passing total

---

### Day 5 (Friday): Sum Aggregation & Indexing (Part 1)

**Goals:**
- Implement symbolic differentiation for `sum(i, expr)` constructs
- Handle indexed variable references
- Begin building index mapping infrastructure

**Tasks:**
1. Design strategy for differentiating sum aggregations
   - Mathematical rule: d/dx sum(i, f(x,i)) = sum(i, df(x,i)/dx)
   - Derivative of sum is sum of derivatives (linearity)
   - Preserve `Sum` AST structure in derivative
2. Implement symbolic differentiation for `Sum` AST nodes
   - Differentiate body expression
   - Wrap result in new `Sum` with same index sets
   - Handle empty sums (derivative is zero)
3. Handle indexed variable references in derivatives
   - d/dx(i) VarRef(x, (i,)) → Const(1) when indices match
   - d/dx(i) VarRef(x, (j,)) → Const(0) when indices differ
   - d/dx(i) VarRef(y, (i,)) → Const(0) for different variable
4. Begin designing index instance mapping
   - Map variable[indices] → column identifiers
   - Map equation[indices] → row identifiers
   - Plan for deterministic ordering (sorted)
5. Write tests with indexed variables and simple sums
6. Document indexing strategy and index matching rules

**Deliverables:**
- Symbolic differentiation for `Sum` expressions (basic cases)
- Index-aware derivative logic (partial implementation)
- `tests/ad/test_sum_aggregation.py` with 6-8 tests
- Design document for index mapping strategy (initial)

**Acceptance Criteria:**
- Correctly differentiates: `sum(i, x(i))`, `sum(i, x(i)^2)`
- Handles constant sums: `sum(i, c*x(i))`
- Index matching works: distinguishes x(i) from x(j)
- Tests pass for basic indexed cases
- Index mapping strategy documented

**Note:** Extended to 2 days (Day 5-6) to provide debugging slack for complex indexing.

---

### Day 6 (Monday): Sum Aggregation, Indexing & Alias Resolution (Part 2)

**Goals:**
- Complete sum/indexing support with nested sums
- Finalize index mapping for sparse Jacobian structure
- Handle alias resolution and universe expansion
- Handle cross-product indexing

**Tasks:**
1. Implement nested sum differentiation
   - `sum(i, sum(j, expr))` cases
   - Track multiple index sets correctly
2. Complete index instance mapping
   - **Expand domain sets to concrete member tuples**
   - Use `ModelIR.sets[set_name].members` for enumeration
   - **Handle alias resolution:**
     - Check `ModelIR.aliases` for alias definitions
     - If domain uses alias, resolve to target set
     - Respect `AliasDef.universe` when specified
     - Use alias target's members for enumeration
   - Create bijection: (var_name, index_tuple) ↔ column_id
   - Create bijection: (eq_name, index_tuple) ↔ row_id
   - Ensure deterministic ordering: sort by set members
3. Handle sum over multiple indices: `sum((i,j), expr)`
4. Implement sparsity tracking
   - Track which variables appear in which expressions
   - Build dependency graph for Jacobian structure
5. Write comprehensive tests for complex indexing scenarios
   - Test cross-products and multi-dimensional indexing
   - **Test alias scenarios:**
     - Variables/equations using aliased sets
     - Verify member enumeration through aliases
     - Test universe constraints on aliases
6. Document alias resolution strategy

**Deliverables:**
- Complete symbolic differentiation for all `Sum` cases
- Full index mapping implementation with alias resolution
- Sparsity tracking infrastructure
- `tests/ad/test_sum_aggregation.py` with 12-15 tests total
- `tests/ad/test_index_mapping.py` with 10-12 tests (including alias tests)
- `tests/ad/test_alias_resolution.py` with 6-8 tests

**Acceptance Criteria:**
- Correctly differentiates: `sum(i, sum(j, x(i)*y(j)))`
- Handles: `sum((i,j), x(i,j)^2)`
- Index mapping deterministic and reproducible
- **Alias resolution works correctly:**
  - Aliases map to correct target set members
  - Universe constraints respected
  - Tests verify aliased domains enumerate properly
- Sparsity pattern correctly identifies variable dependencies
- All indexing and alias tests pass

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
   - Maintain row/column index maps (from Day 6)
   - Support queries: get_derivative(eq_instance, var_instance)
3. Implement `compute_objective_gradient()` function in `src/ad/gradient.py`
   - Locate objective expression from `ObjectiveIR`:
     - If `ObjectiveIR.expr` is not None, use it directly
     - If `ObjectiveIR.expr` is None, find defining equation:
       - Look for equation defining `ObjectiveIR.objvar`
       - Extract expression from that equation's LHS or RHS
       - Handle error if no defining equation found
   - Differentiate objective expression w.r.t. all variables
   - Handle objective sense: 
     - `min`: use gradient as-is
     - `max`: negate gradient (or negate objective before differentiating)
4. Create gradient vector indexed by all variable instances
5. Handle scalar vs. indexed objective variables
6. Write tests for Jacobian structure construction
7. Write tests for objective gradients on Sprint 1 examples
   - Test both explicit expr and objvar-equation cases

**Deliverables:**
- `src/ad/jacobian.py` with `JacobianStructure` class
- `src/ad/gradient.py` with objective gradient computation
- Objective expression retrieval logic (handles None case)
- `tests/ad/test_jacobian_structure.py` with 8-10 tests
- `tests/ad/test_gradient.py` with 12-15 tests

**Acceptance Criteria:**
- Can build sparse Jacobian structure for scalar equations
- Correct gradient for: `min x^2`, `max -x^2`
- Handles indexed objectives: `min sum(i, x(i)^2)`
- **Successfully retrieves objective expression from IR:**
  - Handles explicit `ObjectiveIR.expr`
  - Handles None case by finding defining equation
  - Clear error if no objective expression found
- Gradient structure matches variable index map
- Deterministic row/column ordering (sorted)
- All tests pass

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
   - Use normalized form: equation AST is already (lhs - rhs)
3. Process all inequality constraints (g(x) ≤ 0) → J_g
   - Iterate through `ModelIR.inequalities`
   - Handle normalized form from Sprint 1
4. **Include bound-derived equations** (critical for KKT)
   - Process `ModelIR.normalized_bounds` (from normalize.py)
   - These are additional inequality constraints from variable bounds
   - Bound equations have form:
     - Lower bound: `x(i) - lo(i) >= 0` (normalized to `-(x(i) - lo(i)) <= 0`)
     - Upper bound: `up(i) - x(i) >= 0` (normalized to `-(up(i) - x(i)) <= 0`)
   - Add bound constraint rows to J_g
   - Derivatives are simple: d(x(i) - lo)/dx(i) = 1, etc.
5. Handle indexed constraints correctly
   - Expand each indexed equation to multiple rows
   - Use index mapping from Day 6
6. Ensure sparsity pattern is optimal (only nonzero entries)
7. Test on all Sprint 1 examples
8. Verify bound equations appear in Jacobian with correct structure

**Deliverables:**
- Full Jacobian computation for constraint systems
- Bound equation handling in Jacobian
- Integration tests with Sprint 1 IR
- `tests/ad/test_constraint_jacobian.py` with 12-15 tests
- `tests/ad/test_bound_jacobian.py` with 8-10 tests

**Acceptance Criteria:**
- Correct Jacobians for all 5 Sprint 1 examples
- **Bound-derived rows appear in J_g with correct derivatives**
- Sparsity pattern matches expected nonzero structure
- Handles empty constraint sets gracefully
- Indexed constraints properly expanded to rows
- Bound equations have correct simple structure (derivative = 1 or -1)
- All tests pass

---

### Day 9 (Thursday): Numeric Validation, Testing & Dependencies

**Goals:**
- Comprehensive finite-difference validation
- Edge case testing and error handling
- Update dependencies in pyproject.toml
- Implement deterministic FD seed strategy

**Tasks:**
1. **Define deterministic FD seed points strategy**
   - Create utility to generate reproducible test points
   - Use fixed random seed for repeatability: `np.random.seed(42)`
   - Generate seed points based on variable bounds:
     - If bounded: sample within bounds
     - If unbounded: use reasonable range (e.g., [-10, 10])
   - Store seed generation in `src/ad/validation.py`
   - Document seeding strategy for future reference
2. Implement finite-difference checker utility
   - Use AST evaluator from Day 2
   - Compute numerical derivatives: f'(x) ≈ (f(x+h) - f(x-h))/(2h)
   - Use step size h = 1e-6 for FD
   - Compare symbolic differentiation results (evaluated) with FD results
3. Run FD validation on all derivative rules
   - Test each operation type independently
   - Use deterministic seed points from step 1
4. Test numeric stability on boundary cases
   - Near-zero values, large values
   - Domain boundaries (log near 0, sqrt near 0, etc.)
   - **Verify NaN/Inf detection from Day 2:**
     - Test that NaN/Inf are caught and reported
     - Verify error messages are actionable
5. Add tests for degenerate cases:
   - Constant expressions (zero derivatives)
   - Variables that don't appear in constraints
   - Empty sums
6. **Update `pyproject.toml` dependencies**
   - Add `numpy` >= 1.24.0 (for FD validation and numeric operations)
   - Document version requirements and rationale
   - Update README if needed
7. Performance testing on larger indexed models
   - Test with 100+ variables and constraints
   - Profile hot paths if needed (document, don't optimize yet)
8. Debugging slack: fix any discovered bugs from Days 5-8
9. Address any FD mismatches or indexing issues

**Deliverables:**
- Deterministic FD seed point generation strategy and implementation
- `tests/ad/test_finite_difference.py` with 12-15 validation tests
- `src/ad/validation.py` with FD checker utilities and seed generation
- Updated `pyproject.toml` with numpy dependency
- Bug fixes and edge case handling
- Performance profiling results (documented)
- NaN/Inf detection validation tests

**Acceptance Criteria:**
- **Deterministic FD seed points defined and documented**
- All derivative rules validated against FD within 1e-6 tolerance
- FD tests are reproducible (same seed → same results)
- Edge cases handled gracefully with clear errors
- NaN/Inf detection working and tested
- No false positives/negatives in derivative computation
- Performance acceptable for 100+ variable/constraint models
- Dependencies documented and updated
- All discovered bugs fixed
- ~60 tests passing

---

### Day 10 (Friday): Integration, Documentation & Polish

**Goals:**
- Integrate AD with main codebase
- Complete documentation
- Final testing and cleanup
- Update PROJECT_PLAN.md references

**Tasks:**
1. Create high-level API for external use:
   - `compute_derivatives(model_ir) → (gradient, jacobian_g, jacobian_h)`
   - Clean interface hiding internal complexity
   - Handle all edge cases gracefully
2. Write integration tests using full NLP→AD pipeline
   - Load GAMS file → parse → normalize → compute derivatives
   - End-to-end tests on all Sprint 1 examples
3. Add comprehensive docstrings to all public functions and classes
   - Include mathematical formulas
   - Document assumptions and limitations
   - Add usage examples
   - Clarify symbolic differentiation approach
4. Create/update documentation:
   - `docs/ad_design.md` explaining symbolic differentiation architecture
   - Clarify why symbolic approach chosen vs. adjoint reverse-mode
   - Document index mapping strategy and alias resolution
   - Document derivative rules reference with formulas
   - Add FD validation methodology and seeding strategy
   - Document NaN/Inf detection approach
5. **Update PROJECT_PLAN.md references:**
   - Change "reverse-mode AD" to "symbolic differentiation"
   - Update Sprint 2 description to match implementation
   - Ensure consistency across all planning docs
6. Update main README with Sprint 2 completion status
7. Code cleanup and refactoring
   - Remove dead code
   - Improve naming consistency
   - Add type hints throughout
8. Final test suite run and validation
   - Run full test suite
   - Verify 60+ tests passing
   - Check coverage > 90%
9. Code review preparation
   - Clean up commit history if needed
   - Prepare PR description

**Deliverables:**
- `src/ad/api.py` with clean public interface
- Complete docstrings and type hints throughout `src/ad/`
- `docs/ad_design.md` comprehensive documentation
- `docs/derivative_rules.md` reference guide
- Updated PROJECT_PLAN.md (terminology consistency)
- Updated README.md
- All 60+ tests passing
- Code ready for review and merge

**Acceptance Criteria:**
- Clean API: `gradient, J_g, J_h = compute_derivatives(model_ir)`
- All public functions documented with docstrings
- Mathematical formulas documented for all derivative rules
- Symbolic differentiation approach clearly explained
- PROJECT_PLAN.md updated for consistency
- Test coverage > 90%
- All Sprint 2 acceptance criteria met:
  - ✅ All v1 functions differentiated (except abs - rejected)
  - ✅ Unary operators supported
  - ✅ AST evaluator working
  - ✅ NaN/Inf detection implemented
  - ✅ Jacobians validated with FD
  - ✅ Indexed sums/variables supported
  - ✅ Alias resolution working
  - ✅ Bound equations in Jacobians
  - ✅ 60+ tests passing
  - ✅ Dependencies updated
  - ✅ Deterministic FD seeding
- Ready for Sprint 3 (KKT synthesis)

---

## File Structure

```
src/ad/
├── __init__.py           # Public API exports
├── ad_core.py            # Core symbolic differentiation framework
├── derivative_rules.py   # Derivative rules for all operations
├── evaluator.py          # AST evaluator with NaN/Inf detection
├── gradient.py           # Objective gradient computation
├── jacobian.py          # Jacobian structure and computation
├── validation.py        # FD validation and seed generation utilities
└── api.py               # High-level public API

tests/ad/
├── test_ad_core.py              # Core framework tests
├── test_arithmetic.py           # Binary +,-,*,/ and Unary +,- tests
├── test_evaluator.py            # AST evaluator tests (inc. NaN/Inf)
├── test_transcendental.py       # Power, exp, log, sqrt tests
├── test_trigonometric.py        # Sin, cos, tan tests
├── test_unsupported.py          # abs() rejection tests
├── test_sum_aggregation.py      # Sum and indexing tests
├── test_index_mapping.py        # Index mapping tests
├── test_alias_resolution.py     # Alias handling tests
├── test_jacobian_structure.py   # Jacobian structure tests
├── test_gradient.py             # Objective gradient tests
├── test_constraint_jacobian.py  # Constraint Jacobian tests
├── test_bound_jacobian.py       # Bound equation Jacobian tests
├── test_finite_difference.py    # FD validation tests
└── test_integration.py          # End-to-end integration tests

docs/
├── ad_design.md          # Symbolic differentiation architecture
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

### Indexing & Sum Tests (~18 tests)
- Basic sums
- Nested sums
- Multi-index sums
- Index mapping correctness
- Alias resolution tests

### Sparsity & Structure Tests (~10 tests)
- Jacobian structure correctness
- Index mapping verification
- Sparse vs. dense comparison
- Row/column ordering

### Numeric Validation (~12 FD tests)
- Finite-difference agreement
- Deterministic seed points
- Tolerance checks (±1e-6)
- Boundary value testing
- NaN/Inf detection

### Integration Tests (~8 tests)
- Full NLP model → derivatives pipeline
- All Sprint 1 examples validated
- Bound equation handling
- End-to-end workflow

**Total: 63 tests**

---

## Dependencies

**From Sprint 1:**
- `ModelIR` with normalized equations and bounds
- Expression AST nodes (Const, VarRef, ParamRef, Binary, Unary, Sum, Call)
- Symbol table with set/variable/equation metadata
- `SetDef` with members list for enumeration
- `AliasDef` with target and universe for alias resolution
- `NormalizedEquation` from normalize.py
- `ObjectiveIR` with sense and objvar (expr may be None)

**External Libraries (to be added to pyproject.toml):**
- `numpy` >= 1.24.0 (for numeric validation and FD)
  - Used in finite-difference validation
  - Used for numeric operations in evaluator
  - Provides reproducible random seeding
  - Required dependency (not optional)
- `pytest` >= 7.4.4 (already present, for testing)

**Future/Optional:**
- `scipy.sparse` (future optimization, not Sprint 2)

---

## Risk Mitigation

| Risk | Mitigation | Status |
|------|------------|--------|
| Complex indexing breaks AD | Two-day allocation (Days 5-6) with comprehensive tests | Addressed |
| Alias resolution forgotten | Explicit Day 6 tasks for alias handling | Final review fix |
| Numeric instability | Domain checks, NaN/Inf detection, validation on Day 9 | Enhanced |
| Performance issues | Profile on Day 9, defer optimization if needed | Original plan |
| Incomplete test coverage | Daily test writing, 63-test target with coverage tracking | Enhanced |
| Integration issues | Integration tests throughout, especially Days 8-10 | Original plan |
| abs() confusion | Clear rejection error with Sprint 4 reference | Addressed |
| Unary operator oversight | Explicit Day 2 task for unary +/- | Addressed |
| Missing AST evaluator | Implemented early on Day 2 with safety checks | Enhanced |
| Objective expr not found | Explicit task to locate from defining equation | Addressed |
| Dependency documentation | Update pyproject.toml on Day 9, document requirements | Addressed |
| Bound equations missed | Explicit inclusion in Day 8 tasks and tests | Addressed |
| Schedule too tight | Extended sum/indexing to 2 days, debugging slack Day 9 | Addressed |
| FD tests flaky | Deterministic seed points with fixed random seed | Final review fix |
| NaN/Inf propagation | Safety task on Day 2, validation on Day 9 | Final review fix |
| Symbolic vs adjoint confusion | Clarified throughout, update PROJECT_PLAN.md on Day 10 | Final review fix |

---

## Definition of Done

- [ ] All v1 functions have symbolic differentiation implementation
- [ ] Unary +/- operators supported
- [ ] abs() rejected with clear, informative error message
- [ ] AST evaluator implemented and tested
- [ ] NaN/Inf detection implemented with actionable errors
- [ ] Sum aggregation and indexing fully supported
- [ ] Nested sums and multi-dimensional indexing working
- [ ] Alias resolution correctly handles aliased sets and universes
- [ ] Jacobian sparsity structure correct for all test cases
- [ ] Objective gradient computation handles min/max
- [ ] Objective expression successfully retrieved from IR (handles None case)
- [ ] Normalized bound equations included in Jacobian
- [ ] Deterministic FD seed point strategy implemented
- [ ] 63 unit tests passing with >90% coverage
- [ ] All 5 Sprint 1 examples produce validated gradients/Jacobians
- [ ] Finite-difference validation within 1e-6 for all examples
- [ ] Dependencies updated in pyproject.toml
- [ ] PROJECT_PLAN.md updated for terminology consistency
- [ ] Public API documented and ready for Sprint 3
- [ ] Code reviewed and merged to main

---

## Next Sprint Preview

**Sprint 3** will use the symbolic differentiation engine to:
- Assemble KKT stationarity conditions using ∇f and constraint Jacobians (J_g, J_h)
- Generate Lagrange multiplier variables (λ, ν) for each constraint row
- Handle bound multipliers (π^L, π^U) using bound equation Jacobians
- Emit GAMS MCP code with complementarity pairs
- Create end-to-end NLP→MCP conversion pipeline

The symbolic derivatives computed in Sprint 2 are the foundation for the entire KKT system!

---

## Summary of Final Revisions

### Addressing Final Review (SPRINT_2_PLAN_FINAL_REVIEW.md):

1. ✅ **Differentiation approach clarified throughout:**
   - Changed "reverse-mode AD" to "symbolic differentiation"
   - Day 1 explains symbolic approach vs. adjoint
   - Day 10 includes updating PROJECT_PLAN.md for consistency

2. ✅ **Deterministic FD seed points:**
   - Day 9 task to define reproducible random seed strategy
   - Fixed seed (42) for repeatability
   - Documented in validation.py
   - FD tests now reproducible

3. ✅ **Alias resolution explicitly handled:**
   - Day 6 extended with alias resolution tasks
   - Use ModelIR.aliases and AliasDef.universe
   - Dedicated test file: test_alias_resolution.py
   - Ensures Jacobian enumeration respects aliases

4. ✅ **NaN/Inf detection scheduled:**
   - Day 2 implements safety checks in evaluator
   - Day 9 validates NaN/Inf detection
   - Actionable error messages
   - Satisfies reproducibility requirements

### All Previous Revisions Still Addressed:
- abs() rejection (Sprint 4 deferred)
- Unary operators (Day 2)
- AST evaluator (Day 2)
- Objective expression handling (Day 7)
- NumPy dependency (Day 9)
- Bound equations (Day 8)
- Schedule rebalanced (Days 5-6, Day 9 slack)
