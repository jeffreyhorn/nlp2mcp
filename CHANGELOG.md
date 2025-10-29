# Changelog

All notable changes to the nlp2mcp project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Sprint 2: Differentiation Engine (AD) + Jacobians

#### Day 1 (2025-10-28) - AD Foundation & Design

##### Added
- Created `src/ad/` module for automatic differentiation
- Implemented symbolic differentiation framework in `src/ad/ad_core.py`
- Added derivative rules for constants and variable references in `src/ad/derivative_rules.py`
- Created initial test suite in `tests/ad/test_ad_core.py`
- Added architecture documentation in `docs/ad_architecture.md`

##### Changed
- N/A

##### Fixed
- N/A

#### Day 2 (2025-10-28) - Arithmetic Operations & AST Evaluator

##### Added
- Implemented symbolic differentiation for Binary operations (+, -, *, /) in `src/ad/derivative_rules.py`
  - Addition and subtraction using sum/difference rules
  - Multiplication using product rule: d(a*b)/dx = b*(da/dx) + a*(db/dx)
  - Division using quotient rule: d(a/b)/dx = (b*(da/dx) - a*(db/dx))/b²
- Implemented symbolic differentiation for Unary operators (+, -)
- Created AST evaluator in `src/ad/evaluator.py`
  - Evaluate expressions with concrete variable/parameter values
  - Support for all v1 expression types (constants, variables, binary, unary, functions)
  - Handle indexed variables and parameters
- Implemented comprehensive NaN/Inf detection
  - Check for NaN in all arithmetic operations
  - Check for Inf in all operations
  - Domain violation checks (division by zero, log of negative, sqrt of negative)
  - Clear, actionable error messages with context
- Created `tests/ad/test_arithmetic.py` with 15 tests for differentiation
- Created `tests/ad/test_evaluator.py` with 19 tests for evaluation and safety
- Exported `evaluate` and `EvaluationError` from `src/ad/__init__.py`

##### Changed
- Updated `src/ad/derivative_rules.py` to include Binary and Unary in dispatcher

##### Fixed
- N/A

#### Day 3 (2025-10-28) - Power & Transcendental Functions

##### Added
- Implemented symbolic differentiation for power function in `src/ad/derivative_rules.py`
  - General formula: d(a^b)/dx = a^b * (b/a * da/dx + ln(a) * db/dx)
  - Optimized constant exponent case: d(a^n)/dx = n * a^(n-1) * da/dx
  - Supports power(base, exponent) function calls
- Implemented symbolic differentiation for exponential function
  - Formula: d(exp(a))/dx = exp(a) * da/dx
  - Chain rule support for composite expressions
- Implemented symbolic differentiation for logarithm function
  - Formula: d(log(a))/dx = (1/a) * da/dx
  - Chain rule support for composite expressions
- Implemented symbolic differentiation for square root function
  - Formula: d(sqrt(a))/dx = (1/(2*sqrt(a))) * da/dx
  - Chain rule support for composite expressions
- Created `tests/ad/test_transcendental.py` with 26 comprehensive tests
  - Power function tests (6 tests): constant exponent, constant base, both variables, negative exponent, fractional exponent, chain rule
  - Exponential tests (4 tests): variable, constant, different variable, chain rule
  - Logarithm tests (4 tests): variable, constant, different variable, chain rule
  - Square root tests (4 tests): variable, constant, different variable, chain rule
  - Error handling tests (5 tests): wrong argument counts, unsupported functions
- Added Call import to `src/ad/derivative_rules.py`
- Added `_diff_call`, `_diff_power`, `_diff_exp`, `_diff_log`, `_diff_sqrt` functions

##### Changed
- Updated dispatcher in `differentiate_expr` to route Call expressions to `_diff_call`
- Updated documentation comments to reflect Day 3 implementation

##### Fixed
- N/A

#### Day 4 (2025-10-28) - Trigonometric Functions & abs() Rejection

##### Added
- Implemented symbolic differentiation for trigonometric functions in `src/ad/derivative_rules.py`
  - Sine function: d(sin(a))/dx = cos(a) * da/dx
  - Cosine function: d(cos(a))/dx = -sin(a) * da/dx
  - Tangent function: d(tan(a))/dx = sec²(a) * da/dx = (1/cos²(a)) * da/dx
  - Full chain rule support for all trig functions
  - Documented tan domain limitations (poles at π/2 + nπ)
- Implemented abs() rejection with helpful, actionable error message
  - Clear explanation: "abs() is not differentiable everywhere (undefined at x=0)"
  - References planned smooth approximation feature
  - Mentions planned --smooth-abs flag for sqrt(x² + ε) approximation
  - Points to PROJECT_PLAN.md for details on smoothing techniques
- Added `_diff_sin`, `_diff_cos`, `_diff_tan` functions
- Created `tests/ad/test_trigonometric.py` with 12 comprehensive tests
  - 4 sin tests: variable, constant, different variable, chain rule
  - 4 cos tests: variable, constant, different variable, chain rule
  - 4 tan tests: variable, constant, different variable, chain rule
  - 3 error handling tests for wrong argument counts
- Created `tests/ad/test_unsupported.py` with 9 tests
  - 6 abs() rejection tests verifying error message quality
  - 2 tests for other unsupported functions with clear messages
  - Validates references to planned features, smooth-abs flag, PROJECT_PLAN.md

##### Changed
- Updated `_diff_call` dispatcher to route sin, cos, tan, and abs
- Enhanced error messages for unsupported functions to list all supported functions
- Error messages now explicitly mention abs() is intentionally excluded

##### Fixed
- N/A

#### Day 5 (2025-10-28) - Sum Aggregation & Indexing (Part 1)

##### Added
- Implemented symbolic differentiation for Sum aggregations in `src/ad/derivative_rules.py`
  - Mathematical rule (linearity): d/dx sum(i, f(x,i)) = sum(i, df(x,i)/dx)
  - Derivative of sum is sum of derivatives
  - Sum structure preserved in derivative AST
  - Basic index-aware differentiation (same base variable name)
- Added `_diff_sum` function with comprehensive documentation
  - Differentiates body expression
  - Wraps result in new Sum with same index variables
  - Handles single and multiple indices: sum(i, ...) and sum((i,j), ...)
  - Supports nested sums: sum(i, sum(j, ...))
- Added Sum import to `src/ad/derivative_rules.py`
- Updated dispatcher in `differentiate_expr` to route Sum expressions
- Created `tests/ad/test_sum_aggregation.py` with 14 comprehensive tests
  - 4 basic sum tests: indexed variable, constant, parameter, different variable
  - 3 arithmetic tests: product with parameter, addition, power
  - 2 multiple indices tests: two indices, product with indexed parameter
  - 2 nested sum tests: simple nested, nested with constant
  - 2 complex expression tests: exp, log
  - All tests verify Sum structure preservation and correct body differentiation
- Documented index matching strategy in docstrings
  - Day 5: Basic matching on variable base name
  - Day 6: Full index-aware matching (distinguishing x(i) from x(j))

##### Changed
- Updated Day 5+ placeholder section header to "Day 5: Sum Aggregations"
- Updated test_ad_core.py's test_sum_not_yet_supported (now Sum is supported)

##### Fixed
- N/A

#### Day 6 (2025-10-28) - Sum Aggregation, Indexing & Alias Resolution (Part 2)

##### Added
- Created `src/ad/index_mapping.py` module for index instance mapping
  - `IndexMapping` class: Bijective mapping between variable/equation instances and dense IDs
  - `build_index_mapping()`: Constructs complete mapping for all variables and equations
  - `enumerate_variable_instances()`: Enumerates all instances of indexed variables
  - `enumerate_equation_instances()`: Enumerates all instances of indexed equations
  - Deterministic ordering: Sorted by name and indices for reproducibility
  - Support for scalar, single-index, and multi-index variables/equations
- Implemented comprehensive alias resolution system
  - `resolve_set_members()`: Resolves set or alias names to concrete members
  - Handles simple aliases (alias to direct set)
  - Handles chained aliases (alias to alias to set)
  - Supports universe constraints (AliasDef.universe)
  - Circular alias detection with clear error messages
  - Intersection logic for universe-constrained aliases
- Created `src/ad/sparsity.py` module for sparsity tracking
  - `SparsityPattern` class: Tracks nonzero entries in Jacobian
  - `find_variables_in_expr()`: Finds all variable names in expression AST
  - `analyze_expression_sparsity()`: Maps expression to column IDs
  - Row/column dependency queries
  - Density computation for sparsity analysis
  - Support for indexed variables in sparsity pattern
- Added index instance mapping with cross-product enumeration
  - Variables: (var_name, index_tuple) → column_id
  - Equations: (eq_name, index_tuple) → row_id
  - Reverse mappings: col_id → (var_name, index_tuple)
  - Handles multi-dimensional indexing: x(i,j,k)
- Created `tests/ad/test_index_mapping.py` with 19 comprehensive tests
  - Set member resolution tests (2 tests)
  - Variable enumeration tests (5 tests): scalar, single-index, two-index, three-index, empty set error
  - Equation enumeration tests (3 tests)
  - Complete index mapping tests (9 tests): empty model, scalar variables, indexed variables, mixed, bijective mapping, deterministic ordering
- Created `tests/ad/test_alias_resolution.py` with 17 comprehensive tests
  - Basic alias resolution (3 tests)
  - Chained aliases (4 tests): two-level, three-level, circular detection, self-referential
  - Universe constraints (5 tests): basic constraint, disjoint universe, superset, chained with universe, universe not found
  - Variables with aliases (3 tests)
  - Complete mapping with aliases (2 tests)
- Created `tests/ad/test_sparsity.py` with 33 comprehensive tests
  - Finding variables in expressions (17 tests): constants, variables, indexed variables, symbols, parameters, binary ops, unary ops, function calls, sums, nested sums, complex expressions
  - Expression sparsity analysis (6 tests)
  - Sparsity pattern data structure (10 tests): empty pattern, adding dependencies, density calculation, row/column queries

##### Changed
- N/A

##### Fixed
- N/A

#### Day 7 (2025-10-28) - Jacobian Structure & Objective Gradient

##### Added
- Created `src/ad/jacobian.py` module for sparse Jacobian storage
  - `JacobianStructure` class: Sparse dict-based storage for derivative expressions
  - Storage format: J[row_id][col_id] = derivative_expr (AST)
  - `set_derivative()` and `get_derivative()` for entry management
  - `get_derivative_by_names()`: Query using equation/variable names
  - `get_row()` and `get_col()`: Retrieve all nonzero entries in row/column
  - `get_nonzero_entries()`: List all (row, col) pairs with derivatives
  - `num_nonzeros()` and `density()`: Sparsity metrics
  - Integration with IndexMapping from Day 6
- Created `GradientVector` class for objective gradient storage
  - Dict-based storage: col_id → derivative_expr
  - `set_derivative()` and `get_derivative()` for component management
  - `get_derivative_by_name()`: Query using variable names
  - `get_all_derivatives()`: Retrieve all gradient components
  - `num_nonzeros()`: Count nonzero gradient entries
- Created `src/ad/gradient.py` module for objective gradient computation
  - `find_objective_expression()`: Retrieve objective from ModelIR
    - Handles explicit ObjectiveIR.expr
    - Handles None case by finding defining equation
    - Searches for equation defining ObjectiveIR.objvar
    - Extracts expression from equation LHS or RHS
    - Clear error if no objective expression found
  - `compute_objective_gradient()`: Compute ∇f for objective function
    - Differentiates objective w.r.t. all variables
    - Handles ObjSense.MIN (use gradient as-is)
    - Handles ObjSense.MAX (negate gradient: max f = min -f)
    - Works with scalar and indexed variables
    - Returns GradientVector with all components
  - `compute_gradient_for_expression()`: Gradient of arbitrary expression
    - Useful for constraint gradients or sub-expressions
    - Optional negation flag
- Created `tests/ad/test_jacobian_structure.py` with 24 comprehensive tests
  - JacobianStructure basics (5 tests): empty, set/get, multiple entries, overwrite
  - Row/column queries (4 tests): get_row, get_col, empty row/col
  - Sparsity tracking (5 tests): nonzero entries, density, empty, fully dense
  - Integration with IndexMapping (3 tests): query by names, not found, error handling
  - GradientVector basics (5 tests): empty, set/get, multiple components, get_all
  - GradientVector with IndexMapping (2 tests): query by name, error handling
- Created `tests/ad/test_gradient.py` with 17 comprehensive tests
  - Finding objective expression (6 tests): explicit expr, objvar-defined LHS/RHS, no objective, objvar not defined, ignores indexed equations
  - Gradient minimization (4 tests): scalar quadratic, two variables, constant, linear
  - Gradient maximization (2 tests): max linear (negated), max two variables
  - Indexed variables (2 tests): indexed objective, mixed scalar/indexed
  - Gradient for expression (2 tests): simple expression, with negation
  - Objective from defining equation (1 test): complete flow

##### Changed
- N/A

##### Fixed
- N/A

---

## [0.1.0] - Sprint 1 Complete

### Added
- GAMS parser with Lark grammar for NLP subset
- Intermediate representation (IR) with normalized constraints
- Support for indexed variables and equations
- Expression AST with all v1 operations
- Comprehensive test coverage for parser and IR
- Example GAMS models

### Components
- `src/gams/` - GAMS grammar and parsing utilities
- `src/ir/` - Intermediate representation (ast.py, model_ir.py, normalize.py, parser.py, symbols.py)
- `tests/gams/` - Parser tests
- `tests/ir/` - IR and normalization tests
- `examples/` - Example GAMS NLP models

---

## Project Milestones

- **v0.1.0** (Sprint 1): ✅ Parser and IR - COMPLETE
- **v0.2.0** (Sprint 2): 🔄 Automatic differentiation - IN PROGRESS
- **v0.3.0** (Sprint 3): 📋 KKT synthesis and MCP code generation
- **v0.4.0** (Sprint 4): 📋 Extended features and robustness
- **v1.0.0** (Sprint 5): 📋 Production-ready with docs and PyPI release
