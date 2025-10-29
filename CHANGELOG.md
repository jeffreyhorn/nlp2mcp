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
