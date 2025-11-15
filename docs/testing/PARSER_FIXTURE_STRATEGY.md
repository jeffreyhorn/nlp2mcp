# Parser Test Fixture Strategy

**Created:** 2025-11-15  
**Sprint:** Sprint 7 Prep (Task 9)  
**Purpose:** Comprehensive test fixture strategy for parser features across Sprints 7-10  
**Owner:** Development team (Testing specialist)

---

## Executive Summary

This document defines a systematic test fixture strategy for new parser features being added in Sprints 7-10. The strategy builds on the successful convexity fixture pattern (YAML + parametrized tests) and extends it to cover:

1. **Preprocessor directives** (`$if`, `$set`, `$include`, etc.)
2. **Set range syntax** (`Set i / 1*6 /`)
3. **Multi-dimensional indexing** (`Parameter A(i,j)`, `Variable X(i,j,k)`)
4. **Advanced GAMS features** (table declarations, model/solve statements, etc.)

**Key Principles:**
- **Systematic coverage**: Every parser feature has positive, negative, and edge case tests
- **Minimal fixtures**: Each fixture tests ONE specific feature in isolation (<30 lines)
- **Expected results**: YAML files document expected parse outcomes for validation
- **Parametrized tests**: DRY principle - single test function validates all fixtures
- **Documentation**: README.md in each directory explains fixture purpose and usage

**Total Fixtures Planned:** 45-60 across 4 categories (Sprint 7: 34 fixtures)

---

## Table of Contents

1. [Background and Motivation](#background-and-motivation)
2. [Fixture Hierarchy Design](#fixture-hierarchy-design)
3. [Expected Results Format](#expected-results-format)
4. [Test Case Generation Approach](#test-case-generation-approach)
5. [Fixture Documentation Template](#fixture-documentation-template)
6. [Coverage Matrix](#coverage-matrix)
7. [Sprint 7 Implementation Checklist](#sprint-7-implementation-checklist)
8. [Sprint 8-10 Roadmap](#sprint-8-10-roadmap)

---

## 1. Background and Motivation

### 1.1 Current Test Fixture Landscape

**Existing fixtures (Sprint 6):**
- ✅ `tests/fixtures/convexity/` - 18 models testing convexity patterns
  - Well-documented with README.md
  - YAML expected results (`expected_results.yaml`)
  - Parametrized tests in `test_convexity_patterns.py`
  - **Model:** Successful pattern to replicate
  
- ✅ `tests/fixtures/gamslib/` - 10 GAMSLib models for benchmarking
  - Real-world models (not minimal test fixtures)
  - Used for integration testing and parse rate tracking
  
- ✅ `tests/golden/` - End-to-end golden file tests
  - Full conversion pipeline validation
  - Not organized by feature

**Gaps for Sprint 7:**
- ❌ No systematic preprocessor directive tests
- ❌ No set range syntax tests
- ❌ No multi-dimensional indexing tests
- ❌ No advanced GAMS feature tests (model/solve, table, option, etc.)

### 1.2 Research Findings from Tasks 2-4

**Task 2: GAMSLib Failure Analysis**
- Identified 7 feature categories blocking parse rate
- Prioritized features by ROI: preprocessor (2.9%/hour), set range (2.5%/hour)
- 9 models analyzed with specific failure patterns

**Task 3: Preprocessor Directive Research**
- 60+ GAMS directives surveyed
- Only 3 types block parsing: `$if not set`, `%macro%`, `$eolCom`
- Mock/skip approach recommended (6-8 hour effort)

**Task 4: Multi-Dimensional Indexing Research**
- Current IR already supports multi-dim (tuple-based design)
- No IR changes needed, only grammar updates
- 96% of models use 1D indexing, 4% use 2D

**Implication:** Test fixtures should focus on **high-impact features** with **minimal complexity**.

### 1.3 Testing Goals

**Sprint 7 Goals:**
1. **Comprehensive coverage**: Every new parser feature has ≥3 test cases (positive, negative, edge)
2. **Fast execution**: All parser tests run in <5 seconds
3. **Easy maintenance**: Adding new fixtures requires <10 minutes
4. **Clear documentation**: Developers can understand fixture purpose without code inspection
5. **Integration ready**: Fixtures can be used in unit, integration, and E2E tests

**Quality Metrics:**
- **Parser feature coverage:** 100% of Sprint 7 features tested
- **Test execution time:** <5s for all parser unit tests
- **Fixture clarity:** Every fixture has expected result documented
- **Maintenance burden:** <10% test code churn per sprint

---

## 2. Fixture Hierarchy Design

### 2.1 Proposed Directory Structure

```
tests/fixtures/
├── convexity/                  # Existing - Sprint 6 convexity patterns
│   ├── README.md
│   ├── expected_results.yaml
│   └── *.gms (18 models)
│
├── preprocessor/               # NEW - Sprint 7
│   ├── README.md
│   ├── expected_results.yaml
│   ├── simple_set.gms          # $set directive
│   ├── simple_if.gms           # $if not set
│   ├── if_else.gms             # $if/$else branches
│   ├── macro_expansion.gms     # %variable% expansion
│   ├── nested_if.gms           # Nested conditionals
│   ├── eolcom.gms              # $eolCom directive
│   ├── include_basic.gms       # $include (already works)
│   ├── ontext_offtext.gms      # $onText/$offText (already works)
│   └── combined.gms            # Multiple directives
│
├── sets/                       # NEW - Sprint 7
│   ├── README.md
│   ├── expected_results.yaml
│   ├── range_numeric.gms       # Set i / 1*6 /
│   ├── range_alpha.gms         # Set s / s1*s10 /
│   ├── range_prefix.gms        # Set i / p1*p100 /
│   ├── range_with_macro.gms    # Set i / 1*%n% /
│   ├── explicit_elements.gms   # Set i / i1, i2, i3 /
│   ├── indexed_set.gms         # Set active(i)
│   ├── multi_dim_set.gms       # Set pairs(i,j)
│   └── set_tuple.gms           # Set ij(i,j)
│
├── multidim/                   # NEW - Sprint 7
│   ├── README.md
│   ├── expected_results.yaml
│   ├── parameter_2d.gms        # Parameter A(i,j)
│   ├── parameter_3d.gms        # Parameter B(i,j,k)
│   ├── variable_2d.gms         # Variable X(i,j)
│   ├── variable_3d.gms         # Variable Y(i,j,k)
│   ├── nested_sum_2d.gms       # sum((i,j), ...)
│   ├── nested_sum_3d.gms       # sum((i,j,k), ...)
│   ├── equation_2d.gms         # Equation eq(i,j)
│   └── mixed_dimensions.gms    # A(i,j) * X(j,k)
│
├── statements/                 # NEW - Sprint 7/8
│   ├── README.md
│   ├── expected_results.yaml
│   ├── model_declaration.gms   # Model mymodel / all /
│   ├── solve_basic.gms         # solve mymodel using mcp
│   ├── solve_with_objective.gms # solve m using nlp minimizing obj
│   ├── option_statement.gms    # option limrow = 0
│   ├── display_statement.gms   # display x.l, y.l
│   ├── scalar_assignment.gms   # scalar pi / 3.14159 /
│   ├── multiple_scalars.gms    # Scalars a, b, c
│   └── assignment_indexed.gms  # A(i) = B(i) + 1
│
├── tables/                     # NEW - Sprint 8
│   ├── README.md
│   ├── expected_results.yaml
│   ├── table_2d.gms            # Table data(i,j)
│   ├── table_with_headers.gms  # Table with row/col headers
│   └── table_sparse.gms        # Sparse table data
│
├── advanced/                   # NEW - Sprint 9-10
│   ├── README.md
│   ├── expected_results.yaml
│   ├── conditional_expr.gms    # expr$(condition)
│   ├── set_operations.gms      # union, intersect, card()
│   ├── variable_attributes.gms # x.l, x.m, x.lo, x.up
│   ├── equation_attributes.gms # eq.range, eq.slack
│   ├── loop_statement.gms      # loop(i, ...)
│   └── special_functions.gms   # ord(), card(), smax(), smin()
│
├── gamslib/                    # Existing - Real-world benchmarks
│   └── ... (10 models)
│
├── large_models/               # Existing - Performance tests
│   └── ... (3 models)
│
├── minmax_research/            # Existing - Research fixtures
│   └── ...
│
└── maximize_debug/             # Existing - Debug fixtures
    └── ...
```

### 2.2 Naming Conventions

**Fixture files:**
- Lowercase with underscores: `simple_set.gms`, `parameter_2d.gms`
- Descriptive names indicating feature tested
- Prefix with complexity: `simple_`, `nested_`, `complex_`

**Directory names:**
- Singular nouns: `preprocessor/`, `multidim/`, `statements/`
- Feature-focused, not syntax-focused

**Expected results:**
- Always named `expected_results.yaml` (consistent with convexity pattern)

### 2.3 Fixture Organization Principles

1. **One feature per fixture**: Each .gms file tests ONE specific parser feature
2. **Minimal size**: Fixtures should be <30 lines (easier to understand and debug)
3. **Self-documenting**: File name + header comment explain what's being tested
4. **Isolated**: No dependencies between fixtures (can run in any order)
5. **Progressive complexity**: `simple_*.gms` → `nested_*.gms` → `complex_*.gms`

---

## 3. Expected Results Format

### 3.1 YAML Schema Design

Building on the convexity pattern, extend YAML schema to support parser validation:

```yaml
# tests/fixtures/preprocessor/expected_results.yaml

# Fixture: simple_set.gms
simple_set:
  should_parse: true
  symbols_defined:
    - name: "size"
      type: "scalar"
      value: 10
  preprocessor_actions:
    - directive: "$set"
      variable: "size"
      value: "10"
  warnings: []
  notes: "Basic $set directive - should define scalar 'size' with value 10"

# Fixture: simple_if.gms
simple_if:
  should_parse: true
  symbols_defined:
    - name: "size"
      type: "scalar"
      value: 10
  preprocessor_actions:
    - directive: "$if not set"
      variable: "size"
      action: "set_default"
      value: "10"
  warnings:
    - "Preprocessor directive mocked - assuming default value"
  notes: "$if not set should define 'size' if not already defined"

# Fixture: nested_if.gms
nested_if:
  should_parse: false  # May not implement full conditional logic in Sprint 7
  expected_error: "Nested $if directives not supported"
  warnings:
    - "Complex preprocessor logic may require manual review"
  notes: "Nested conditionals are out of scope for Sprint 7 mock approach"

# Fixture: macro_expansion.gms
macro_expansion:
  should_parse: true
  symbols_defined:
    - name: "n"
      type: "scalar"
      value: 100
    - name: "i"
      type: "set"
      elements: ["1", "2", "3", "100"]  # ... (1-100, expanded from / 1*%n% /)
  preprocessor_actions:
    - directive: "$set"
      variable: "n"
      value: "100"
    - directive: "%macro%"
      macro: "n"
      expanded_value: "100"
  warnings: []
  notes: "Macro expansion in set range syntax"
```

### 3.2 Schema Fields

**Top-level keys:**
- `should_parse` (boolean): Should the parser succeed?
- `symbols_defined` (list): Symbols expected in IR after parsing
- `preprocessor_actions` (list): Preprocessor directives and their effects
- `expected_error` (string, optional): Expected error message if `should_parse: false`
- `warnings` (list): Expected warnings to be issued
- `notes` (string): Human-readable explanation

**`symbols_defined` schema:**
```yaml
- name: "variable_name"       # Symbol identifier
  type: "scalar|set|parameter|variable|equation"
  value: 42                   # Optional - expected value
  domain: ["i", "j"]          # Optional - for indexed symbols
  elements: ["e1", "e2"]      # Optional - for sets
```

**`preprocessor_actions` schema:**
```yaml
- directive: "$set|$if|%macro%|..."
  variable: "var_name"        # Variable affected
  action: "set_default|expand|skip"
  value: "10"                 # Value assigned or expanded
```

### 3.3 Multi-Dimensional Indexing Schema

```yaml
# tests/fixtures/multidim/expected_results.yaml

parameter_2d:
  should_parse: true
  symbols_defined:
    - name: "A"
      type: "parameter"
      dimensions: 2
      domain: ["i", "j"]
  notes: "2D parameter declaration: Parameter A(i,j)"

nested_sum_2d:
  should_parse: true
  symbols_defined:
    - name: "eq1"
      type: "equation"
      domain: []  # Scalar equation
      expression_structure:
        - type: "sum"
          indices: ["i"]
          nested:
            - type: "sum"
              indices: ["j"]
              expr: "A(i,j) * X(i,j)"
  notes: "Nested sum: sum(i, sum(j, A(i,j) * X(i,j)))"
```

### 3.4 Set Range Syntax Schema

```yaml
# tests/fixtures/sets/expected_results.yaml

range_numeric:
  should_parse: true
  symbols_defined:
    - name: "i"
      type: "set"
      elements: ["1", "2", "3", "4", "5", "6"]
      range_syntax: "1*6"
  notes: "Numeric range: Set i / 1*6 / expands to 6 elements"

range_alpha:
  should_parse: true
  symbols_defined:
    - name: "s"
      type: "set"
      elements: ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10"]
      range_syntax: "s1*s10"
  notes: "Alphabetic range: Set s / s1*s10 / expands to 10 elements"
```

---

## 4. Test Case Generation Approach

### 4.1 Parametrized Test Pattern

Following the convexity pattern, use `pytest.mark.parametrize` for DRY tests:

```python
# tests/unit/parser/test_preprocessor.py

import pytest
import yaml
from pathlib import Path
from src.ir.parser import parse_model_file

pytestmark = pytest.mark.unit

FIXTURE_DIR = Path("tests/fixtures/preprocessor")

@pytest.fixture
def expected_results():
    """Load expected results from YAML."""
    with open(FIXTURE_DIR / "expected_results.yaml") as f:
        return yaml.safe_load(f)

@pytest.mark.parametrize("fixture_name", [
    "simple_set",
    "simple_if",
    "if_else",
    "macro_expansion",
    "eolcom",
    "include_basic",
    "ontext_offtext",
    "combined",
])
def test_preprocessor_parsing(fixture_name, expected_results):
    """Test preprocessor directive fixtures."""
    fixture_file = FIXTURE_DIR / f"{fixture_name}.gms"
    expected = expected_results[fixture_name]
    
    # Test parsing
    if expected["should_parse"]:
        model = parse_model_file(fixture_file)
        assert model is not None, f"{fixture_name} should parse successfully"
        
        # Validate symbols defined
        for symbol_spec in expected.get("symbols_defined", []):
            symbol = model.get_symbol(symbol_spec["name"])
            assert symbol is not None, f"Symbol '{symbol_spec['name']}' not found"
            assert symbol.type == symbol_spec["type"], \
                f"Symbol '{symbol_spec['name']}' has wrong type"
    else:
        with pytest.raises(Exception) as exc_info:
            parse_model_file(fixture_file)
        if "expected_error" in expected:
            assert expected["expected_error"] in str(exc_info.value)

@pytest.mark.parametrize("fixture_name,expected_count", [
    ("simple_set", 0),      # No warnings
    ("simple_if", 1),       # 1 warning about mocked directive
    ("macro_expansion", 0), # No warnings
])
def test_preprocessor_warnings(fixture_name, expected_count, expected_results):
    """Test preprocessor warning generation."""
    fixture_file = FIXTURE_DIR / f"{fixture_name}.gms"
    expected = expected_results[fixture_name]
    
    model = parse_model_file(fixture_file)
    warnings = model.get_warnings()
    
    assert len(warnings) == expected_count, \
        f"{fixture_name}: Expected {expected_count} warnings, got {len(warnings)}"
    
    # Validate warning messages if specified
    for expected_warning in expected.get("warnings", []):
        assert any(expected_warning in str(w) for w in warnings), \
            f"Expected warning '{expected_warning}' not found"
```

### 4.2 Multi-Dimensional Indexing Tests

```python
# tests/unit/parser/test_multidim.py

import pytest
from pathlib import Path
from src.ir.parser import parse_model_file

FIXTURE_DIR = Path("tests/fixtures/multidim")

@pytest.mark.parametrize("fixture_name,expected_dims", [
    ("parameter_2d", 2),
    ("parameter_3d", 3),
    ("variable_2d", 2),
    ("variable_3d", 3),
])
def test_multidim_dimensions(fixture_name, expected_dims):
    """Test multi-dimensional symbol parsing."""
    fixture_file = FIXTURE_DIR / f"{fixture_name}.gms"
    model = parse_model_file(fixture_file)
    
    # Find the multi-dimensional symbol
    # (implementation depends on IR API)
    symbols = model.get_symbols()
    multidim_symbol = next(s for s in symbols if len(s.domain) == expected_dims)
    
    assert len(multidim_symbol.domain) == expected_dims, \
        f"Expected {expected_dims} dimensions"

@pytest.mark.parametrize("fixture_name", [
    "nested_sum_2d",
    "nested_sum_3d",
])
def test_nested_sum_parsing(fixture_name):
    """Test nested sum expression parsing."""
    fixture_file = FIXTURE_DIR / f"{fixture_name}.gms"
    model = parse_model_file(fixture_file)
    
    # Should parse without errors
    assert model is not None
    
    # Should have at least one equation with nested sum
    equations = model.get_equations()
    assert len(equations) > 0
```

### 4.3 Set Range Syntax Tests

```python
# tests/unit/parser/test_sets.py

import pytest
from pathlib import Path
from src.ir.parser import parse_model_file

FIXTURE_DIR = Path("tests/fixtures/sets")

@pytest.mark.parametrize("fixture_name,expected_elements", [
    ("range_numeric", ["1", "2", "3", "4", "5", "6"]),
    ("range_alpha", [f"s{i}" for i in range(1, 11)]),
    ("range_prefix", [f"p{i}" for i in range(1, 101)]),
])
def test_set_range_expansion(fixture_name, expected_elements):
    """Test set range syntax expansion."""
    fixture_file = FIXTURE_DIR / f"{fixture_name}.gms"
    model = parse_model_file(fixture_file)
    
    # Get the set symbol
    sets = model.get_sets()
    assert len(sets) == 1
    
    # Validate elements
    actual_elements = sets[0].elements
    assert actual_elements == expected_elements, \
        f"Range expansion mismatch: expected {expected_elements}, got {actual_elements}"
```

### 4.4 Test Organization

**Unit tests:**
- `tests/unit/parser/test_preprocessor.py` - Preprocessor directive tests
- `tests/unit/parser/test_sets.py` - Set range syntax tests
- `tests/unit/parser/test_multidim.py` - Multi-dimensional indexing tests
- `tests/unit/parser/test_statements.py` - Statement-level features (model, solve, option)

**Integration tests:**
- `tests/integration/test_parser_e2e.py` - Full parse → IR → normalize pipeline

**Performance tests:**
- `tests/benchmarks/test_parser_performance.py` - Parse time for all fixtures (<5s total)

---

## 5. Fixture Documentation Template

### 5.1 README.md Template

Each fixture directory must have a README.md following this template:

```markdown
# [Feature Name] Test Fixtures

**Purpose:** Test fixtures for [feature description]  
**Created:** [Date]  
**Sprint:** Sprint [N]  
**Total Fixtures:** [N] fixtures ([X] positive, [Y] negative, [Z] edge cases)

## Overview

This directory contains minimal GAMS models designed to test [feature name] parsing. Each fixture is carefully constructed to represent a specific [feature] pattern or edge case.

## Test Fixture Catalog

### Positive Tests (Should Parse Successfully)

| Fixture | Description | Key Feature | Expected Result |
|---------|-------------|-------------|-----------------|
| `simple_*.gms` | [Description] | [Feature] | PASS, [N] symbols defined |
| ... | ... | ... | ... |

### Negative Tests (Should Fail Gracefully)

| Fixture | Description | Key Feature | Expected Result |
|---------|-------------|-------------|-----------------|
| `invalid_*.gms` | [Description] | [Feature] | FAIL, clear error message |
| ... | ... | ... | ... |

### Edge Cases (Boundary Conditions)

| Fixture | Description | Key Feature | Expected Result |
|---------|-------------|-------------|-----------------|
| `edge_*.gms` | [Description] | [Feature] | [Specific behavior] |
| ... | ... | ... | ... |

## Expected Results

All expected results are documented in `expected_results.yaml`. See that file for:
- Parse success/failure expectations
- Symbol definitions expected
- Warning messages expected
- Preprocessor actions expected

## Usage

### Unit Testing

```python
from src.ir.parser import parse_model_file

# Test positive case
model = parse_model_file("tests/fixtures/[feature]/simple_*.gms")
assert model is not None

# Test negative case
with pytest.raises(ParseError):
    parse_model_file("tests/fixtures/[feature]/invalid_*.gms")
```

### Batch Testing

```bash
# Run all [feature] tests
pytest tests/unit/parser/test_[feature].py -v

# Run specific fixture
pytest tests/unit/parser/test_[feature].py::test_[feature]_parsing[simple_*] -v
```

## Validation

All fixtures have been verified to:
- ✅ Contain <30 lines (minimal examples)
- ✅ Test ONE specific feature in isolation
- ✅ Have expected results documented in YAML
- ✅ Include header comment explaining purpose

## Feature Coverage

This directory tests the following [feature] capabilities:

1. **[Capability 1]** - [Description]
   - Fixtures: `simple_*.gms`, `complex_*.gms`
   
2. **[Capability 2]** - [Description]
   - Fixtures: `nested_*.gms`
   
3. **[Capability 3]** - [Description]
   - Fixtures: `edge_*.gms`

## Sprint [N] Testing Goals

1. **Baseline Parsing**: All positive fixtures parse successfully (100% pass rate)
2. **Error Handling**: All negative fixtures produce clear error messages
3. **Edge Case Coverage**: Consistent behavior on boundary conditions
4. **Performance**: Parse all [N] fixtures in <2 seconds

## File Manifest

```
tests/fixtures/[feature]/
├── README.md                 # This file
├── expected_results.yaml     # Expected parse outcomes
├── simple_*.gms              # Basic feature tests
├── nested_*.gms              # Complex nested tests
├── edge_*.gms                # Edge case tests
└── invalid_*.gms             # Negative tests
```

## References

- Task [N]: [Feature] Research
- `docs/research/[feature].md`
- Sprint [N] PREP_PLAN.md (Task [M])

## Version History

- **[Date]**: Initial fixture set ([N] fixtures)
  - [X] positive tests
  - [Y] negative tests
  - [Z] edge cases
```

### 5.2 Fixture Header Comment Template

Each .gms fixture file should start with a header comment:

```gams
* ============================================================================
* Fixture: [fixture_name].gms
* Purpose: Test [specific feature being tested]
* Expected: [PASS/FAIL] - [brief description of expected outcome]
* Sprint: Sprint [N]
* Category: [positive/negative/edge]
* ============================================================================
*
* This fixture tests [detailed description].
*
* Key Feature: [feature name]
* Expected Symbols: [list of symbols that should be defined]
* Expected Warnings: [N] warning(s) about [...]
*
* References:
*   - Task [N]: [Feature] Research
*   - docs/research/[feature].md
* ============================================================================

[GAMS code here - minimal, focused on ONE feature]
```

---

## 6. Coverage Matrix

### 6.1 Sprint 7 Parser Feature Coverage

| Feature Category | Feature | Fixtures | Positive | Negative | Edge | Total | Priority |
|------------------|---------|----------|----------|----------|------|-------|----------|
| **Preprocessor** | `$set` directive | simple_set | 1 | 0 | 0 | 1 | Critical |
| | `$if not set` | simple_if, nested_if | 1 | 1 | 1 | 3 | Critical |
| | `$if`/`$else` | if_else | 1 | 0 | 1 | 2 | High |
| | `%macro%` expansion | macro_expansion, range_with_macro | 2 | 0 | 1 | 3 | Critical |
| | `$eolCom` | eolcom | 1 | 0 | 0 | 1 | Medium |
| | Combined | combined | 0 | 0 | 1 | 1 | Medium |
| **Set Range** | Numeric range | range_numeric | 1 | 0 | 0 | 1 | Critical |
| | Alpha range | range_alpha | 1 | 0 | 0 | 1 | High |
| | Prefix range | range_prefix | 1 | 0 | 0 | 1 | High |
| | With macro | range_with_macro | 1 | 0 | 1 | 2 | High |
| **Multi-Dim** | 2D parameter | parameter_2d | 1 | 0 | 0 | 1 | High |
| | 3D parameter | parameter_3d | 1 | 0 | 1 | 2 | Medium |
| | 2D variable | variable_2d | 1 | 0 | 0 | 1 | High |
| | 3D variable | variable_3d | 1 | 0 | 1 | 2 | Medium |
| | Nested sum 2D | nested_sum_2d | 1 | 0 | 1 | 2 | High |
| | Nested sum 3D | nested_sum_3d | 1 | 0 | 1 | 2 | Medium |
| | 2D equation | equation_2d | 1 | 0 | 0 | 1 | High |
| | Mixed dims | mixed_dimensions | 0 | 0 | 1 | 1 | Medium |
| **Statements** | Model declaration | model_declaration | 1 | 1 | 0 | 2 | Critical |
| | Solve basic | solve_basic | 1 | 1 | 0 | 2 | Critical |
| | Solve w/ obj | solve_with_objective | 1 | 0 | 1 | 2 | High |
| | Option | option_statement | 1 | 0 | 0 | 1 | High |
| | Display | display_statement | 1 | 0 | 0 | 1 | Medium |
| | Scalar assign | scalar_assignment | 1 | 0 | 0 | 1 | High |
| | Multiple scalars | multiple_scalars | 1 | 0 | 1 | 2 | Critical |
| | Indexed assign | assignment_indexed | 1 | 0 | 1 | 2 | Medium |
| **TOTAL** | | | **24** | **3** | **13** | **40** | |

**Summary:**
- **Total test cases:** 40 (Sprint 7 only)
- **Total fixture files:** 34 (9 preprocessor + 8 sets + 8 multidim + 9 statements)
- **Positive tests:** 25 (61%)
- **Negative tests:** 3 (7%)
- **Edge cases:** 13 (32%)
- **Critical priority:** 10 features
- **High priority:** 16 features
- **Medium priority:** 15 features

**Note:** Some features require multiple test types (positive + negative + edge), so the total number of test cases (41) exceeds the number of fixture files (35). Each fixture file typically contains one test type.

### 6.2 Coverage Gaps Identified

**Sprint 7 gaps (deferred to Sprint 8-10):**
- ❌ Table declarations (Sprint 8)
- ❌ Conditional expressions `$(...)` (Sprint 9)
- ❌ Set operations (union, intersect, card) (Sprint 9)
- ❌ Variable attributes (.l, .m, .lo, .up) (Sprint 9)
- ❌ Equation attributes (.range, .slack) (Sprint 9)
- ❌ Loop statements (Sprint 9)
- ❌ Special functions (ord, card, smax, smin) (Sprint 10)

### 6.3 Test Execution Time Estimates

Based on convexity fixture timing (~0.3s for 18 fixtures):

| Category | Fixtures | Estimated Time |
|----------|----------|----------------|
| Preprocessor | 9 | ~0.5s |
| Set Range | 8 | ~0.5s |
| Multi-Dim | 8 | ~0.5s |
| Statements | 9 | ~0.5s |
| **TOTAL** | **34** | **~2.0s** |

**Target:** <5s for all Sprint 7 parser unit tests ✅

---

## 7. Sprint 7 Implementation Checklist

### 7.1 Directory Setup (Day 1)

- [ ] Create `tests/fixtures/preprocessor/` directory
- [ ] Create `tests/fixtures/sets/` directory
- [ ] Create `tests/fixtures/multidim/` directory
- [ ] Create `tests/fixtures/statements/` directory
- [ ] Create `tests/unit/parser/` directory (if not exists)

### 7.2 Preprocessor Fixtures (Day 1-2)

- [ ] Create `preprocessor/README.md` from template
- [ ] Create `preprocessor/expected_results.yaml`
- [ ] Create 9 fixture files:
  - [ ] `simple_set.gms` (Critical)
  - [ ] `simple_if.gms` (Critical)
  - [ ] `if_else.gms` (High)
  - [ ] `macro_expansion.gms` (Critical)
  - [ ] `nested_if.gms` (High)
  - [ ] `eolcom.gms` (Medium)
  - [ ] `include_basic.gms` (Medium - validation)
  - [ ] `ontext_offtext.gms` (Medium - validation)
  - [ ] `combined.gms` (Medium)
- [ ] Create `test_preprocessor.py` with parametrized tests
- [ ] Verify all tests pass (or fail as expected)

### 7.3 Set Range Fixtures (Day 2)

- [ ] Create `sets/README.md` from template
- [ ] Create `sets/expected_results.yaml`
- [ ] Create 8 fixture files:
  - [ ] `range_numeric.gms` (Critical)
  - [ ] `range_alpha.gms` (High)
  - [ ] `range_prefix.gms` (High)
  - [ ] `range_with_macro.gms` (High)
  - [ ] `explicit_elements.gms` (Medium - validation)
  - [ ] `indexed_set.gms` (Medium)
  - [ ] `multi_dim_set.gms` (Medium)
  - [ ] `set_tuple.gms` (Medium)
- [ ] Create `test_sets.py` with parametrized tests
- [ ] Verify all tests pass (or fail as expected)

### 7.4 Multi-Dimensional Fixtures (Day 3)

- [ ] Create `multidim/README.md` from template
- [ ] Create `multidim/expected_results.yaml`
- [ ] Create 8 fixture files:
  - [ ] `parameter_2d.gms` (High)
  - [ ] `parameter_3d.gms` (Medium)
  - [ ] `variable_2d.gms` (High)
  - [ ] `variable_3d.gms` (Medium)
  - [ ] `nested_sum_2d.gms` (High)
  - [ ] `nested_sum_3d.gms` (Medium)
  - [ ] `equation_2d.gms` (High)
  - [ ] `mixed_dimensions.gms` (Medium)
- [ ] Create `test_multidim.py` with parametrized tests
- [ ] Verify all tests pass (or fail as expected)

### 7.5 Statement Fixtures (Day 4)

- [ ] Create `statements/README.md` from template
- [ ] Create `statements/expected_results.yaml`
- [ ] Create 9 fixture files:
  - [ ] `model_declaration.gms` (Critical)
  - [ ] `solve_basic.gms` (Critical)
  - [ ] `solve_with_objective.gms` (High)
  - [ ] `option_statement.gms` (High)
  - [ ] `display_statement.gms` (Medium)
  - [ ] `scalar_assignment.gms` (High)
  - [ ] `multiple_scalars.gms` (Critical)
  - [ ] `assignment_indexed.gms` (Medium)
- [ ] Create `test_statements.py` with parametrized tests
- [ ] Verify all tests pass (or fail as expected)

### 7.6 Integration and Documentation (Day 5)

- [ ] Update `conftest.py` with fixture loading helpers
- [ ] Create integration test combining all features
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Verify execution time <5s for parser unit tests
- [ ] Update this document with actual results
- [ ] Cross-reference with PREP_PLAN.md Task 9

### 7.7 Acceptance Criteria

- [ ] All 34+ fixtures created and documented
- [ ] All fixtures have header comments
- [ ] All fixtures have expected results in YAML
- [ ] All 4 README.md files created
- [ ] Parametrized tests cover all fixtures
- [ ] Test execution time <5s
- [ ] 100% coverage of Sprint 7 parser features
- [ ] Zero test failures (positive fixtures parse, negative fixtures fail gracefully)

---

## 8. Sprint 8-10 Roadmap

### 8.1 Sprint 8 Additions (Wave 2)

**New directories:**
- `tests/fixtures/tables/` - Table declaration syntax
- `tests/fixtures/indexed_assign/` - Indexed assignment statements

**Estimated fixtures:** 15-20
**Estimated effort:** 4-6 hours

### 8.2 Sprint 9 Additions (Wave 3)

**New directories:**
- `tests/fixtures/conditional/` - Conditional expressions `$(condition)`
- `tests/fixtures/set_ops/` - Set operations (union, intersect, card)
- `tests/fixtures/attributes/` - Variable and equation attributes

**Estimated fixtures:** 20-25
**Estimated effort:** 6-8 hours

### 8.3 Sprint 10 Additions (Wave 4)

**New directories:**
- `tests/fixtures/loops/` - Loop statements
- `tests/fixtures/special_funcs/` - Special functions (ord, card, smax, smin)
- `tests/fixtures/file_io/` - File I/O statements

**Estimated fixtures:** 15-20
**Estimated effort:** 4-6 hours

### 8.4 Long-Term Maintenance

**Quarterly review:**
- Add fixtures for newly discovered edge cases
- Update expected results if parser behavior changes
- Archive obsolete fixtures (mark as deprecated)

**Fixture lifecycle:**
- Fixtures remain in place indefinitely (regression safety)
- Deprecated fixtures moved to `tests/fixtures/deprecated/`
- New features always get fixtures before implementation

---

## Appendix A: Example Fixtures

### A.1 Preprocessor Example: simple_set.gms

```gams
* ============================================================================
* Fixture: simple_set.gms
* Purpose: Test basic $set directive
* Expected: PASS - defines scalar 'size' with value 10
* Sprint: Sprint 7
* Category: positive
* ============================================================================
*
* This fixture tests the simplest preprocessor directive: $set.
* The directive should define a scalar variable 'size' = 10.
*
* Key Feature: $set directive
* Expected Symbols: size (scalar, value=10)
* Expected Warnings: 0
*
* References:
*   - Task 3: Preprocessor Directive Research
*   - docs/research/preprocessor_directives.md
* ============================================================================

$set size 10

Set i / p1*p%size% /;
Scalar n / %size% /;
```

### A.2 Set Range Example: range_numeric.gms

```gams
* ============================================================================
* Fixture: range_numeric.gms
* Purpose: Test numeric set range syntax
* Expected: PASS - expands to 6 elements (1, 2, 3, 4, 5, 6)
* Sprint: Sprint 7
* Category: positive
* ============================================================================
*
* This fixture tests set range syntax with numeric elements.
* The range 1*6 should expand to 6 elements.
*
* Key Feature: Set range syntax (numeric)
* Expected Symbols: i (set, 6 elements)
* Expected Warnings: 0
*
* References:
*   - Task 2: GAMSLib Failure Analysis (himmel16.gms)
*   - docs/planning/EPIC_2/SPRINT_7/GAMSLIB_FAILURE_ANALYSIS.md
* ============================================================================

Set i 'indices for the 6 points' / 1*6 /;
Display i;
```

### A.3 Multi-Dim Example: parameter_2d.gms

```gams
* ============================================================================
* Fixture: parameter_2d.gms
* Purpose: Test 2D parameter declaration
* Expected: PASS - parameter A indexed by (i,j)
* Sprint: Sprint 7
* Category: positive
* ============================================================================
*
* This fixture tests multi-dimensional parameter indexing.
* Parameter A should have domain (i, j).
*
* Key Feature: 2D parameter indexing
* Expected Symbols: A (parameter, 2D, domain=[i,j])
* Expected Warnings: 0
*
* References:
*   - Task 4: Multi-Dimensional Indexing Research
*   - docs/research/multidimensional_indexing.md
* ============================================================================

Set i / i1*i3 /;
Set j / j1*j2 /;
Parameter A(i,j);
A(i,j) = ord(i) + ord(j);
Display A;
```

---

## Appendix B: YAML Schema Reference

### B.1 Complete YAML Schema

```yaml
# Fixture name (key)
fixture_name:
  # Required fields
  should_parse: true|false                # Should parser succeed?
  
  # Optional fields
  symbols_defined:                        # List of expected symbols
    - name: "symbol_name"                 # Symbol identifier (required)
      type: "scalar|set|parameter|variable|equation"  # Type (required)
      value: 42                           # Value (optional)
      dimensions: 2                       # For multi-dim symbols (optional)
      domain: ["i", "j"]                  # Index sets (optional)
      elements: ["e1", "e2"]              # For sets (optional)
      range_syntax: "1*10"                # For range sets (optional)
  
  preprocessor_actions:                   # List of preprocessor operations
    - directive: "$set|$if|%macro%"       # Directive type (required)
      variable: "var_name"                # Variable affected (required)
      action: "set_default|expand|skip"   # Action taken (optional)
      value: "10"                         # Value (optional)
  
  expression_structure:                   # For complex expressions (optional)
    - type: "sum|product|power"           # Expression type
      indices: ["i", "j"]                 # Index variables
      nested:                             # Nested expressions
        - type: "binop"
          op: "*"
          left: "A(i,j)"
          right: "X(i,j)"
  
  expected_error: "Error message"         # If should_parse: false (optional)
  
  warnings:                               # List of expected warnings (optional)
    - "Warning message 1"
    - "Warning message 2"
  
  notes: "Human-readable explanation"     # Documentation (optional)
```

### B.2 Symbol Types

- `scalar` - Scalar variable (0-dimensional)
- `set` - Set declaration
- `parameter` - Parameter (data)
- `variable` - Decision variable
- `equation` - Constraint or equation

### B.3 Preprocessor Directives

- `$set` - Define compile-time variable
- `$if` - Conditional compilation
- `$if not set` - Define default if not already set
- `%macro%` - Macro expansion

### B.4 Expression Types

- `sum` - Summation expression
- `product` - Product expression
- `power` - Exponentiation
- `binop` - Binary operation (+, -, *, /)
- `unop` - Unary operation (-, +)

---

## Appendix C: References

### Research Documents
- `docs/planning/EPIC_2/SPRINT_7/GAMSLIB_FAILURE_ANALYSIS.md` (Task 2)
- `docs/research/preprocessor_directives.md` (Task 3)
- `docs/research/multidimensional_indexing.md` (Task 4)
- `docs/planning/EPIC_2/PARSER_ROADMAP.md` (Task 6)

### Test Patterns
- `tests/fixtures/convexity/` - Successful pattern to replicate
- `tests/fixtures/convexity/expected_results.yaml` - YAML schema example
- `tests/unit/diagnostics/test_convexity_patterns.py` - Parametrized test example

### Sprint Planning
- `docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md` (Task 9)
- `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md`

### Project Documentation
- `PROJECT_PLAN.md` - Sprint 7-10 goals
- `PRELIMINARY_PLAN.md` - Sprint 7 task breakdown

---

**End of Document**
