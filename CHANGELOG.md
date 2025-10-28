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
