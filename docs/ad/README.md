# Automatic Differentiation Documentation

This directory contains documentation for the AD (Automatic Differentiation) module implemented in Sprint 2.

## Files

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - High-level architectural decisions and design rationale
  - Why symbolic differentiation vs. reverse-mode AD
  - Performance considerations
  - Design philosophy
  
- **[DESIGN.md](DESIGN.md)** - Detailed design and implementation approach
  - Module structure and organization
  - Core algorithms and data structures
  - Implementation patterns
  
- **[DERIVATIVE_RULES.md](DERIVATIVE_RULES.md)** - Complete reference of all derivative rules implemented
  - Basic arithmetic operations
  - Transcendental functions (exp, log, trig)
  - Power functions
  - Aggregation operations (sum)
  - Index-aware differentiation

## Quick Start

1. **Start with [ARCHITECTURE.md](ARCHITECTURE.md)** for the big picture and design rationale
2. **Read [DESIGN.md](DESIGN.md)** for implementation details and how components fit together
3. **Reference [DERIVATIVE_RULES.md](DERIVATIVE_RULES.md)** for specific derivative formulas and examples

## Related Documentation

- **Implementation:** See `src/ad/` for the actual code
- **Tests:** See `tests/unit/ad/` and `tests/integration/ad/` for test coverage
- **Sprint 2 Planning:** See `docs/planning/EPIC_1/SPRINT_2/` for sprint retrospective and planning documents

## Module Overview

The AD module (`src/ad/`) performs symbolic differentiation of GAMS NLP expressions to generate:

- **Objective Gradient:** ∇f(x) for the objective function
- **Constraint Jacobians:** J_g(x) for inequalities, J_h(x) for equalities

All derivatives are computed symbolically as AST expressions that can be:
- Inspected for debugging
- Simplified for optimization
- Emitted as GAMS code for the KKT system

## Key Features

- ✅ **Symbolic differentiation** - Results are AST expressions, not numeric values
- ✅ **Index-aware** - Handles indexed variables and sum aggregations correctly
- ✅ **Sparse output** - Only computes and stores non-zero derivatives
- ✅ **Type-safe** - Full type annotations with mypy checking
- ✅ **Comprehensive tests** - 265+ tests with 84-98% coverage

## Status

**Sprint 2:** ✅ COMPLETE (386 tests passing)  
**Coverage:** 84-98% across all AD modules
