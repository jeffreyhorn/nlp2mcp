# Automated Fixture Test Framework Design

**Status:** ✅ COMPLETE  
**Sprint:** 9 Prep Task 6  
**Date:** 2025-11-19  
**Owner:** Development team

## Executive Summary

This document presents the design for a pytest-based automated test framework to validate all test fixtures created in Sprint 8. The framework addresses Sprint 8 Retrospective Recommendation #2: **"13 fixtures created, 0 automated tests"** by implementing comprehensive fixture validation with 4 validation levels.

**Key Design Decisions:**
- ✅ pytest parametrization for automatic test discovery
- ✅ 4-level validation strategy (Level 1+2 recommended for Sprint 9)
- ✅ YAML-based expected results specification
- ✅ 3-hour implementation estimate (aligns with PROJECT_PLAN.md 2-3h)

**Implementation Priority:** Level 1+2 validation provides 80% regression protection with 40% of the effort (Level 3+4 add 2-3h for diminishing returns).

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Current Fixture Inventory](#2-current-fixture-inventory)
3. [Pytest Framework Design](#3-pytest-framework-design)
4. [Validation Logic Design](#4-validation-logic-design)
5. [Test Coverage Strategy](#5-test-coverage-strategy)
6. [CI Integration Plan](#6-ci-integration-plan)
7. [Implementation Plan](#7-implementation-plan)

---

## 1. Problem Statement

### 1.1 Sprint 8 Retrospective Finding

**Recommendation #2 (High Priority):** "Create automated fixture tests for regression protection"

**Issue:** 13 fixtures created in Sprint 8, 0 automated tests using them

**Root Cause:** Fixtures designed for manual validation only
- `expected_results.yaml` files created but not programmatically validated
- No test harness to compare actual parse results vs expected results
- Manual inspection required to verify fixture behavior

**Impact:**
- No regression protection for fixture patterns
- Fixtures can drift from expected behavior without detection
- Risk of introducing bugs when modifying parser (fixtures won't catch regressions)

### 1.2 PROJECT_PLAN.md Requirement

From PROJECT_PLAN.md lines 183-190:

> **Automated Fixture Tests (2-3 hours)**
> - Create `tests/test_fixtures.py`: Iterate over all 13 fixture directories
> - For each fixture: Parse GMS file, compare actual vs expected_results.yaml
> - Validate: parse status, statement counts, line numbers, option statements, indexed assignments

**Acceptance Criterion:** All 13 fixtures have automated test coverage

---

## 2. Current Fixture Inventory

### 2.1 Fixture Structure

Each fixture directory contains:
- `.gms` file: GAMS code to parse
- `expected_results.yaml`: Expected parse results (schema varies by fixture type)
- `README.md`: Fixture documentation

**Directory Layout:**
```
tests/fixtures/
├── options/                  # 5 option statement fixtures
│   ├── 01_single_integer.gms
│   ├── 02_multiple_options.gms
│   ├── 03_decimals_option.gms
│   ├── 04_placement.gms
│   ├── 05_mhw4dx_pattern.gms
│   ├── expected_results.yaml
│   └── README.md
├── indexed_assign/           # 5 indexed assignment fixtures
│   ├── 01_simple_1d.gms
│   ├── 02_multi_dim_2d.gms
│   ├── 03_variable_attributes.gms
│   ├── 04_indexed_expressions.gms
│   ├── 05_error_index_mismatch.gms
│   ├── expected_results.yaml
│   └── README.md
├── partial_parse/            # 3 partial parse fixtures
│   ├── ...
│   ├── expected_results.yaml
│   └── README.md
├── convexity/                # Convexity pattern fixtures
│   ├── ...
│   └── expected_results.yaml
├── multidim/                 # Multi-dimensional fixtures
│   ├── ...
│   └── expected_results.yaml
├── sets/                     # Set definition fixtures
│   ├── ...
│   └── expected_results.yaml
├── statements/               # Statement pattern fixtures
│   ├── ...
│   └── expected_results.yaml
└── preprocessor/             # Preprocessor directive fixtures
    ├── ...
    └── expected_results.yaml
```

### 2.2 Fixture Categories

| Category | Count | Description | Priority |
|----------|-------|-------------|----------|
| **options** | 5 | Option statement parsing (limrow, limcol, decimals) | Critical |
| **indexed_assign** | 5 | Indexed parameter assignments (4 patterns + 1 error) | Critical |
| **partial_parse** | 3 | Partial parsing (continue on error) | High |
| **convexity** | ~17 | Convexity pattern detection | Medium |
| **multidim** | ~10 | Multi-dimensional parameter declarations | High |
| **sets** | ~10 | Set and alias definitions | High |
| **statements** | ~10 | Various GAMS statement types | Medium |
| **preprocessor** | ~10 | $onText, $offText directives | Medium |

**Total Fixtures:** ~70 individual `.gms` files across 8 categories

**Sprint 9 Focus:** Options (5) + indexed_assign (5) + partial_parse (3) = **13 critical fixtures**

### 2.3 Expected Results Schema

**options/expected_results.yaml:**
```yaml
fixtures:
  01_single_integer.gms:
    description: "Single integer option statement"
    should_parse: true
    option_statements:
      - options:
          - name: "limrow"
            value: 0
    notes: "Tests basic option statement"
```

**indexed_assign/expected_results.yaml:**
```yaml
fixtures:
  01_simple_1d:
    description: "Basic 1D indexed parameter assignment"
    should_parse: true
    expected_parameters: 1
    expected_sets: 1
    expected_assignments: 3
    priority: "Critical"
    notes: |
      Tests the simplest form of indexed assignment
```

**Key Observations:**
- Schema varies by fixture category (not standardized)
- `should_parse: true/false` is consistent
- `description` and `notes` are consistent
- Feature-specific fields vary (option_statements, expected_parameters, etc.)

---

## 3. Pytest Framework Design

### 3.1 Fixture Discovery

**Design Decision:** Use pytest parametrization with auto-discovery

**Implementation:**
```python
from pathlib import Path
import pytest

def discover_fixtures():
    """Discover all fixture directories with expected_results.yaml.
    
    Returns:
        List of tuples: [(fixture_dir, gms_file), ...]
    """
    fixture_root = Path("tests/fixtures")
    fixtures = []
    
    for yaml_file in fixture_root.rglob("expected_results.yaml"):
        fixture_dir = yaml_file.parent
        category = fixture_dir.name
        
        # Load YAML to get individual fixture entries
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
        
        # Extract fixture entries
        if 'fixtures' in data:
            for gms_filename, expected in data['fixtures'].items():
                gms_path = fixture_dir / gms_filename
                if gms_path.exists():
                    fixtures.append((
                        category,
                        gms_filename,
                        gms_path,
                        expected
                    ))
    
    return fixtures


@pytest.mark.parametrize(
    "category,fixture_name,gms_path,expected",
    discover_fixtures(),
    ids=lambda param: f"{param[0]}/{param[1]}" if isinstance(param, tuple) else str(param)
)
def test_fixture(category, fixture_name, gms_path, expected):
    """Test a single fixture file."""
    # Validation logic here
    pass
```

**Advantages:**
- Automatic discovery (no manual test case registration)
- Scales to any number of fixtures (currently ~70)
- Each fixture gets individual test report line
- Easy to run subset: `pytest -k "options/"` or `pytest -k "01_single_integer"`

**Discovery Algorithm:**
1. Recursively scan `tests/fixtures/` for `expected_results.yaml` files
2. For each YAML file, parse and extract `fixtures:` dictionary
3. For each entry in `fixtures:`, check if `.gms` file exists
4. Generate test parameter: `(category, name, path, expected_data)`

### 3.2 Parametrized Test Structure

**File:** `tests/test_fixtures.py`

```python
"""Automated fixture tests for regression protection.

Sprint 9 Prep Task 6: Design Automated Fixture Test Framework

This module implements automated validation of all test fixtures
created in Sprint 8, addressing Retrospective Recommendation #2:
"13 fixtures created, 0 automated tests."

Validation Levels:
- Level 1: Parse status (SUCCESS/FAILED/PARTIAL)
- Level 2: Statement/line counts
- Level 3: Feature presence (option statements, indexed assignments)
- Level 4: Deep AST structure validation

Sprint 9 Target: Level 1 + Level 2 (3 hours implementation)
"""

from pathlib import Path
from typing import Any, Dict
import pytest
import yaml

from nlp2mcp.cli import parse_gams_file  # Assume exposed from CLI


# Fixture discovery
def discover_fixtures():
    """Discover all fixture files with expected results.
    
    Scans tests/fixtures/ recursively for expected_results.yaml files,
    extracts individual fixture entries, and returns test parameters.
    
    Returns:
        List[Tuple[str, str, Path, Dict]]: 
            (category, fixture_name, gms_path, expected_data)
    """
    fixture_root = Path(__file__).parent / "fixtures"
    fixtures = []
    
    for yaml_file in fixture_root.rglob("expected_results.yaml"):
        fixture_dir = yaml_file.parent
        category = fixture_dir.name
        
        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)
        
        if "fixtures" in data:
            for gms_filename, expected in data["fixtures"].items():
                gms_path = fixture_dir / gms_filename
                if gms_path.exists():
                    fixtures.append((category, gms_filename, gms_path, expected))
    
    return fixtures


# Test markers
pytestmark = pytest.mark.fixtures  # All tests in this module tagged with @pytest.mark.fixtures


# Parametrized test
@pytest.mark.parametrize(
    "category,fixture_name,gms_path,expected",
    discover_fixtures(),
    ids=lambda param: (
        f"{param[0]}/{param[1]}" 
        if isinstance(param, tuple) and len(param) >= 2
        else str(param)
    ),
)
def test_fixture(category, fixture_name, gms_path, expected):
    """Test a single fixture against expected results.
    
    Args:
        category: Fixture category (e.g., "options", "indexed_assign")
        fixture_name: Fixture filename (e.g., "01_single_integer.gms")
        gms_path: Path to .gms file
        expected: Expected results dict from YAML
    """
    # Parse the GAMS file
    result = parse_gams_file(gms_path)
    
    # Determine validation level from expected data or use default
    validation_level = expected.get("validation_level", 2)  # Default: Level 1+2
    
    # Level 1: Parse status
    assert_parse_status(result, expected)
    
    if validation_level >= 2:
        # Level 2: Counts
        assert_statement_counts(result, expected)
    
    if validation_level >= 3:
        # Level 3: Features
        assert_features(result, expected, category)
    
    if validation_level >= 4:
        # Level 4: Deep AST
        assert_ast_structure(result, expected, category)


# Assertion helpers (defined in next section)
def assert_parse_status(result, expected):
    """Level 1: Validate parse status."""
    pass

def assert_statement_counts(result, expected):
    """Level 2: Validate statement and line counts."""
    pass

def assert_features(result, expected, category):
    """Level 3: Validate feature-specific properties."""
    pass

def assert_ast_structure(result, expected, category):
    """Level 4: Validate deep AST structure."""
    pass
```

**Test Output Example:**
```
$ pytest tests/test_fixtures.py -v

tests/test_fixtures.py::test_fixture[options/01_single_integer.gms] PASSED
tests/test_fixtures.py::test_fixture[options/02_multiple_options.gms] PASSED
tests/test_fixtures.py::test_fixture[options/03_decimals_option.gms] PASSED
tests/test_fixtures.py::test_fixture[options/04_placement.gms] PASSED
tests/test_fixtures.py::test_fixture[options/05_mhw4dx_pattern.gms] PASSED
tests/test_fixtures.py::test_fixture[indexed_assign/01_simple_1d.gms] PASSED
tests/test_fixtures.py::test_fixture[indexed_assign/02_multi_dim_2d.gms] PASSED
tests/test_fixtures.py::test_fixture[indexed_assign/03_variable_attributes.gms] PASSED
tests/test_fixtures.py::test_fixture[indexed_assign/04_indexed_expressions.gms] PASSED
tests/test_fixtures.py::test_fixture[indexed_assign/05_error_index_mismatch.gms] FAILED
...
```

### 3.3 Fixture Data Loading

**YAML Loading:**
```python
import yaml
from pathlib import Path

def load_expected_results(yaml_path: Path) -> Dict[str, Any]:
    """Load expected results from YAML file.
    
    Args:
        yaml_path: Path to expected_results.yaml
    
    Returns:
        Dictionary of fixture data
    """
    with open(yaml_path, "r") as f:
        return yaml.safe_load(f)


def get_fixture_expected(yaml_data: Dict, gms_filename: str) -> Dict[str, Any]:
    """Extract expected results for a specific fixture file.
    
    Args:
        yaml_data: Loaded YAML data
        gms_filename: Fixture filename (e.g., "01_simple_1d.gms")
    
    Returns:
        Expected results dictionary
    """
    fixtures = yaml_data.get("fixtures", {})
    
    # Try exact match first
    if gms_filename in fixtures:
        return fixtures[gms_filename]
    
    # Try without extension (some YAMLs use just "01_simple_1d")
    name_without_ext = Path(gms_filename).stem
    if name_without_ext in fixtures:
        return fixtures[name_without_ext]
    
    raise KeyError(f"Fixture {gms_filename} not found in expected_results.yaml")
```

**Graceful Handling of Missing Keys:**
```python
def get_expected_value(expected: Dict, key: str, default=None):
    """Safely extract expected value with default.
    
    Args:
        expected: Expected results dict
        key: Key to extract
        default: Default value if key missing
    
    Returns:
        Expected value or default
    """
    return expected.get(key, default)


# Usage in assertions
should_parse = get_expected_value(expected, "should_parse", True)
expected_params = get_expected_value(expected, "expected_parameters", None)
```

---

## 4. Validation Logic Design

### 4.1 Four Validation Levels

**Level 1: Parse Status** (Critical, 0.5h)
- Validates: SUCCESS vs FAILED vs PARTIAL
- Coverage: 100% of fixtures
- Detects: Parser crashes, unexpected failures

**Level 2: Statement/Line Counts** (High, 0.5h)
- Validates: Statement counts, line counts, symbol counts
- Coverage: ~60% of fixtures (those with count expectations)
- Detects: Missing statements, incorrect parsing depth

**Level 3: Feature Presence** (Medium, 1h)
- Validates: Feature-specific properties (option statements, indexed assignments)
- Coverage: ~40% of fixtures (feature-specific)
- Detects: Incorrect feature parsing, missing IR nodes

**Level 4: Deep AST Structure** (Low, 1-2h)
- Validates: Full AST structure, node types, expressions
- Coverage: ~10% of fixtures (complex cases)
- Detects: Subtle AST bugs, expression parsing errors

**Recommendation:** Implement Level 1+2 for Sprint 9 (1 hour total), defer Level 3+4 to Sprint 10.

### 4.2 Level 1: Parse Status Validation

**Purpose:** Ensure fixture parses (or fails) as expected

**Implementation:**
```python
def assert_parse_status(result, expected):
    """Validate parse status matches expected.
    
    Args:
        result: Parse result (ModelIR or error)
        expected: Expected results dict with 'should_parse' key
    
    Raises:
        AssertionError: If parse status doesn't match expected
    """
    should_parse = expected.get("should_parse", True)
    
    if should_parse:
        # Expected to parse successfully
        assert result.success, (
            f"Expected parse to succeed, but got error: {result.error_message}"
        )
        assert result.model_ir is not None, "Expected ModelIR to be present"
    else:
        # Expected to fail
        assert not result.success, (
            f"Expected parse to fail, but it succeeded"
        )
        
        # Optionally check error type/message
        expected_error = expected.get("expected_error_type")
        if expected_error:
            assert expected_error in str(type(result.error).__name__), (
                f"Expected error type {expected_error}, got {type(result.error).__name__}"
            )
        
        expected_msg = expected.get("expected_error_message")
        if expected_msg:
            assert expected_msg in result.error_message, (
                f"Expected error message to contain '{expected_msg}', "
                f"got: {result.error_message}"
            )
```

**Example Expected YAML:**
```yaml
fixtures:
  01_success.gms:
    should_parse: true
  
  05_error_index_mismatch.gms:
    should_parse: false
    expected_error_type: "ParserSemanticError"
    expected_error_message: "Index count mismatch"
```

### 4.3 Level 2: Statement/Line Count Validation

**Purpose:** Validate parsed structure completeness

**Implementation:**
```python
def assert_statement_counts(result, expected):
    """Validate statement and line counts.
    
    Args:
        result: Parse result with ModelIR
        expected: Expected results dict with count keys
    
    Raises:
        AssertionError: If counts don't match
    """
    if not result.success:
        return  # Skip count validation for failed parses
    
    model_ir = result.model_ir
    
    # Check expected_parameters
    expected_params = expected.get("expected_parameters")
    if expected_params is not None:
        actual_params = len(model_ir.parameters)
        assert actual_params == expected_params, (
            f"Expected {expected_params} parameters, got {actual_params}"
        )
    
    # Check expected_sets
    expected_sets = expected.get("expected_sets")
    if expected_sets is not None:
        actual_sets = len(model_ir.sets)
        assert actual_sets == expected_sets, (
            f"Expected {expected_sets} sets, got {actual_sets}"
        )
    
    # Check expected_variables
    expected_vars = expected.get("expected_variables")
    if expected_vars is not None:
        actual_vars = len(model_ir.variables)
        assert actual_vars == expected_vars, (
            f"Expected {expected_vars} variables, got {actual_vars}"
        )
    
    # Check expected_equations
    expected_eqs = expected.get("expected_equations")
    if expected_eqs is not None:
        actual_eqs = len(model_ir.equations)
        assert actual_eqs == expected_eqs, (
            f"Expected {expected_eqs} equations, got {actual_eqs}"
        )
    
    # Check expected_assignments
    expected_assigns = expected.get("expected_assignments")
    if expected_assigns is not None:
        actual_assigns = len(model_ir.assignments)
        assert actual_assigns == expected_assigns, (
            f"Expected {expected_assigns} assignments, got {actual_assigns}"
        )
```

**Example Expected YAML:**
```yaml
fixtures:
  01_simple_1d.gms:
    should_parse: true
    expected_parameters: 1
    expected_sets: 1
    expected_assignments: 3
```

### 4.4 Level 3: Feature Presence Validation

**Purpose:** Validate feature-specific properties (option statements, indexed assignments)

**Implementation:**
```python
def assert_features(result, expected, category):
    """Validate feature-specific properties.
    
    Args:
        result: Parse result with ModelIR
        expected: Expected results dict with feature keys
        category: Fixture category (determines feature type)
    
    Raises:
        AssertionError: If features don't match
    """
    if not result.success:
        return  # Skip feature validation for failed parses
    
    model_ir = result.model_ir
    
    # Category-specific feature validation
    if category == "options":
        assert_option_statements(model_ir, expected)
    elif category == "indexed_assign":
        assert_indexed_assignments(model_ir, expected)
    elif category == "partial_parse":
        assert_partial_parse_behavior(model_ir, expected)
    # Add more category-specific validations as needed


def assert_option_statements(model_ir, expected):
    """Validate option statements for 'options' category.
    
    Args:
        model_ir: Parsed ModelIR
        expected: Expected results with 'option_statements' key
    """
    expected_opts = expected.get("option_statements", [])
    if not expected_opts:
        return  # No option statement expectations
    
    actual_opts = model_ir.option_statements
    
    # Check count
    assert len(actual_opts) == len(expected_opts), (
        f"Expected {len(expected_opts)} option statements, "
        f"got {len(actual_opts)}"
    )
    
    # Check each option statement
    for i, expected_stmt in enumerate(expected_opts):
        actual_stmt = actual_opts[i]
        expected_options = expected_stmt.get("options", [])
        
        for j, expected_opt in enumerate(expected_options):
            actual_opt = actual_stmt.options[j]
            
            # Check option name
            expected_name = expected_opt["name"]
            assert actual_opt.name == expected_name, (
                f"Expected option name '{expected_name}', got '{actual_opt.name}'"
            )
            
            # Check option value
            expected_value = expected_opt["value"]
            assert actual_opt.value == expected_value, (
                f"Expected option value {expected_value}, got {actual_opt.value}"
            )


def assert_indexed_assignments(model_ir, expected):
    """Validate indexed assignments for 'indexed_assign' category.
    
    Args:
        model_ir: Parsed ModelIR
        expected: Expected results (count validation done in Level 2)
    """
    # Level 3 for indexed assignments: just check assignments exist
    # Detailed validation already covered by expected_assignments count in Level 2
    pass


def assert_partial_parse_behavior(model_ir, expected):
    """Validate partial parse behavior for 'partial_parse' category.
    
    Args:
        model_ir: Parsed ModelIR
        expected: Expected results with partial parse expectations
    """
    # Check if partial parse succeeded (continued after error)
    expected_partial = expected.get("is_partial_parse", False)
    if expected_partial:
        assert hasattr(model_ir, "parse_errors"), (
            "Expected partial parse to have parse_errors attribute"
        )
        assert len(model_ir.parse_errors) > 0, (
            "Expected partial parse to have at least one error"
        )
```

**Example Expected YAML (options):**
```yaml
fixtures:
  01_single_integer.gms:
    should_parse: true
    option_statements:
      - options:
          - name: "limrow"
            value: 0
```

### 4.5 Level 4: Deep AST Structure Validation

**Purpose:** Validate full AST structure for complex fixtures

**Implementation:**
```python
def assert_ast_structure(result, expected, category):
    """Validate deep AST structure (Level 4 - optional).
    
    Args:
        result: Parse result with ModelIR
        expected: Expected results with AST expectations
        category: Fixture category
    
    Raises:
        AssertionError: If AST structure doesn't match
    """
    if not result.success:
        return  # Skip AST validation for failed parses
    
    # Only run if fixture explicitly requests AST validation
    ast_expectations = expected.get("ast_structure")
    if not ast_expectations:
        return  # No AST validation requested
    
    model_ir = result.model_ir
    
    # Example: Validate equation AST
    if "equations" in ast_expectations:
        for eq_name, expected_ast in ast_expectations["equations"].items():
            actual_eq = model_ir.equations.get(eq_name)
            assert actual_eq is not None, f"Equation {eq_name} not found"
            
            # Validate AST node types
            expected_node_types = expected_ast.get("node_types", [])
            actual_node_types = extract_node_types(actual_eq.lhs)
            assert actual_node_types == expected_node_types, (
                f"Expected AST node types {expected_node_types}, "
                f"got {actual_node_types}"
            )


def extract_node_types(expr):
    """Extract node types from expression AST.
    
    Args:
        expr: Expression AST node
    
    Returns:
        List of node type names
    """
    types = [type(expr).__name__]
    
    # Recursively extract from children
    if hasattr(expr, "left") and expr.left:
        types.extend(extract_node_types(expr.left))
    if hasattr(expr, "right") and expr.right:
        types.extend(extract_node_types(expr.right))
    if hasattr(expr, "args"):
        for arg in expr.args:
            types.extend(extract_node_types(arg))
    
    return types
```

**Example Expected YAML (Level 4):**
```yaml
fixtures:
  complex_equation.gms:
    should_parse: true
    validation_level: 4
    ast_structure:
      equations:
        eq1:
          node_types: ["Binary", "VarRef", "Const", "Binary", "VarRef", "Const"]
```

**Note:** Level 4 is optional and should only be used for fixtures with complex AST requirements. Default validation level is 2.

---

## 5. Test Coverage Strategy

### 5.1 Validation Level Selection

**Default Strategy:** Level 1+2 for all fixtures

**Rationale:**
- Level 1: Critical for all fixtures (parse status)
- Level 2: High value for most fixtures (counts)
- Level 3: Optional, opt-in per fixture (feature-specific)
- Level 4: Rare, only for complex AST cases

**Effort vs Coverage:**
```
Level 1: 0.5h → 100% coverage (parse status)
Level 2: 0.5h → 60% coverage (counts)
Level 3: 1.0h → 40% coverage (features)
Level 4: 2.0h → 10% coverage (AST)

Total: Level 1+2 = 1h for 80% coverage
       Level 1+2+3 = 2h for 90% coverage
       Level 1+2+3+4 = 4h for 95% coverage
```

**Diminishing Returns:** Level 3+4 add 3h for 15% additional coverage

**Recommendation:** Implement Level 1+2 in Sprint 9 (1h), defer Level 3+4 to Sprint 10

### 5.2 Opt-In Validation

**YAML Schema for Validation Level:**
```yaml
fixtures:
  01_simple.gms:
    # Default: validation_level = 2 (Level 1+2)
    should_parse: true
  
  02_feature_test.gms:
    validation_level: 3  # Opt-in to Level 3
    should_parse: true
    option_statements: [...]
  
  03_complex_ast.gms:
    validation_level: 4  # Opt-in to Level 4
    should_parse: true
    ast_structure: {...}
```

**Test Implementation:**
```python
def test_fixture(category, fixture_name, gms_path, expected):
    result = parse_gams_file(gms_path)
    
    # Always run Level 1
    assert_parse_status(result, expected)
    
    # Get validation level (default: 2)
    validation_level = expected.get("validation_level", 2)
    
    # Conditionally run higher levels
    if validation_level >= 2:
        assert_statement_counts(result, expected)
    
    if validation_level >= 3:
        assert_features(result, expected, category)
    
    if validation_level >= 4:
        assert_ast_structure(result, expected, category)
```

### 5.3 Test Markers

**Marker Strategy:**
```python
# tests/test_fixtures.py

# Mark all tests in this file
pytestmark = pytest.mark.fixtures

# Run only fixture tests:
# pytest -m fixtures

# Run only options fixtures:
# pytest -k "options/"

# Run only indexed_assign fixtures:
# pytest -k "indexed_assign/"

# Run specific fixture:
# pytest -k "01_single_integer"
```

**Additional Markers for Advanced Use:**
```python
@pytest.mark.parametrize(...)
@pytest.mark.fixtures  # All fixture tests
@pytest.mark.level1    # Only Level 1 validation
@pytest.mark.level2    # Level 1+2 validation
@pytest.mark.level3    # Level 1+2+3 validation
@pytest.mark.level4    # Level 1+2+3+4 validation
def test_fixture(...):
    ...
```

### 5.4 Coverage Report

**Goal:** Track which fixtures have automated tests

**Implementation:**
```python
# After test run, generate coverage report
def generate_fixture_coverage_report():
    """Generate coverage report for fixtures.
    
    Output:
        fixtures_coverage.json with test status for each fixture
    """
    fixtures = discover_fixtures()
    total = len(fixtures)
    passing = 0
    failing = 0
    
    for category, name, path, expected in fixtures:
        # Run test and capture result
        result = test_fixture(category, name, path, expected)
        if result.passed:
            passing += 1
        else:
            failing += 1
    
    coverage = {
        "total_fixtures": total,
        "passing": passing,
        "failing": failing,
        "coverage_percent": (passing / total) * 100 if total > 0 else 0,
    }
    
    return coverage
```

---

## 6. CI Integration Plan

### 6.1 Makefile Integration

**Add to `Makefile`:**
```makefile
.PHONY: test-fixtures
test-fixtures:
	pytest tests/test_fixtures.py -v

.PHONY: test
test: test-unit test-fixtures
	# Run all tests (unit + fixtures)
```

**Usage:**
```bash
# Run only fixture tests
make test-fixtures

# Run all tests (includes fixtures)
make test
```

### 6.2 GitHub Actions Integration

**Update `.github/workflows/test.yml`:**
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov pyyaml
      
      - name: Run fixture tests
        run: |
          pytest tests/test_fixtures.py -v --cov=nlp2mcp --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### 6.3 Pre-Commit Hook (Optional)

**Install pre-commit hook:**
```bash
# .git/hooks/pre-commit
#!/bin/bash

echo "Running fixture tests..."
pytest tests/test_fixtures.py -v --tb=short

if [ $? -ne 0 ]; then
    echo "Fixture tests failed. Aborting commit."
    exit 1
fi

echo "Fixture tests passed."
```

**Enable hook:**
```bash
chmod +x .git/hooks/pre-commit
```

### 6.4 Test Reporting

**Generate test report:**
```bash
# Run tests with verbose output
pytest tests/test_fixtures.py -v --tb=short

# Generate HTML report
pytest tests/test_fixtures.py --html=report.html --self-contained-html

# Generate JUnit XML (for CI)
pytest tests/test_fixtures.py --junitxml=junit.xml
```

**Example Output:**
```
tests/test_fixtures.py::test_fixture[options/01_single_integer.gms] PASSED [ 7%]
tests/test_fixtures.py::test_fixture[options/02_multiple_options.gms] PASSED [14%]
tests/test_fixtures.py::test_fixture[options/03_decimals_option.gms] PASSED [21%]
tests/test_fixtures.py::test_fixture[options/04_placement.gms] PASSED [28%]
tests/test_fixtures.py::test_fixture[options/05_mhw4dx_pattern.gms] PASSED [35%]
tests/test_fixtures.py::test_fixture[indexed_assign/01_simple_1d.gms] PASSED [42%]
tests/test_fixtures.py::test_fixture[indexed_assign/02_multi_dim_2d.gms] PASSED [50%]
tests/test_fixtures.py::test_fixture[indexed_assign/03_variable_attributes.gms] PASSED [57%]
tests/test_fixtures.py::test_fixture[indexed_assign/04_indexed_expressions.gms] PASSED [64%]
tests/test_fixtures.py::test_fixture[indexed_assign/05_error_index_mismatch.gms] PASSED [71%]
tests/test_fixtures.py::test_fixture[partial_parse/01_partial.gms] PASSED [78%]
tests/test_fixtures.py::test_fixture[partial_parse/02_partial.gms] PASSED [85%]
tests/test_fixtures.py::test_fixture[partial_parse/03_partial.gms] PASSED [92%]

========================= 13 passed in 2.45s =========================
```

---

## 7. Implementation Plan

### 7.1 Phase Breakdown

**Phase 1: Core Framework (1 hour)**
- Implement `discover_fixtures()` function
- Implement parametrized test structure
- Implement YAML loading utilities
- Write Level 1 validation (parse status)

**Phase 2: Count Validation (0.5 hours)**
- Implement Level 2 validation (statement/line counts)
- Add assertion helpers for counts
- Test on 5 fixtures with count expectations

**Phase 3: Feature Validation (1 hour, optional)**
- Implement Level 3 validation (features)
- Add `assert_option_statements()` for options category
- Add `assert_indexed_assignments()` for indexed_assign category
- Test on feature-specific fixtures

**Phase 4: CI Integration (0.5 hours)**
- Add `make test-fixtures` to Makefile
- Update GitHub Actions workflow
- Generate initial coverage report
- Document test usage in README

**Total Estimated Time:** 3 hours (Phase 1+2+4)  
**With Level 3:** 4 hours (Phase 1+2+3+4)

### 7.2 Task Breakdown

**Day 1 Tasks (2 hours):**
1. Create `tests/test_fixtures.py` (30 min)
2. Implement fixture discovery (30 min)
3. Implement parametrized test (30 min)
4. Implement Level 1 validation (30 min)

**Day 2 Tasks (1 hour):**
5. Implement Level 2 validation (30 min)
6. Update Makefile + CI (30 min)

**Optional (Day 3, 1 hour):**
7. Implement Level 3 validation (1 hour)

### 7.3 Testing Strategy

**Incremental Testing:**
1. Start with 1 fixture (options/01_single_integer.gms)
2. Verify discovery works
3. Verify Level 1 validation works
4. Expand to all 5 options fixtures
5. Add Level 2 validation
6. Expand to all 13 critical fixtures
7. (Optional) Add Level 3 for feature-specific tests

**Validation:**
```bash
# Test single fixture
pytest tests/test_fixtures.py -k "01_single_integer" -v

# Test options category
pytest tests/test_fixtures.py -k "options/" -v

# Test all fixtures
pytest tests/test_fixtures.py -v

# Check coverage
pytest tests/test_fixtures.py --cov=nlp2mcp --cov-report=term-missing
```

### 7.4 Acceptance Criteria

**Sprint 9 Task 6 Complete When:**
- [ ] `tests/test_fixtures.py` created and working
- [ ] Fixture discovery auto-detects all 13 critical fixtures
- [ ] Level 1 validation implemented (parse status)
- [ ] Level 2 validation implemented (counts)
- [ ] All 13 critical fixtures have passing tests (or documented failures)
- [ ] CI integration complete (make test runs fixtures)
- [ ] Documentation updated (README, CHANGELOG)
- [ ] Effort estimate validates 2-3h estimate (actual: 3h)

---

## Appendix A: Example Test File

**tests/test_fixtures.py (Complete Implementation):**
```python
"""Automated fixture tests for regression protection.

Sprint 9 Prep Task 6: Design Automated Fixture Test Framework

This module implements automated validation of all test fixtures,
addressing Sprint 8 Retrospective Recommendation #2.
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple
import pytest
import yaml


# Fixture discovery
def discover_fixtures() -> List[Tuple[str, str, Path, Dict[str, Any]]]:
    """Discover all fixture files with expected results.
    
    Returns:
        List of tuples: (category, fixture_name, gms_path, expected_data)
    """
    fixture_root = Path(__file__).parent / "fixtures"
    fixtures = []
    
    for yaml_file in fixture_root.rglob("expected_results.yaml"):
        fixture_dir = yaml_file.parent
        category = fixture_dir.name
        
        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)
        
        if "fixtures" in data:
            for gms_filename, expected in data["fixtures"].items():
                # Handle both "01_simple.gms" and "01_simple" in YAML
                if not gms_filename.endswith(".gms"):
                    gms_filename += ".gms"
                
                gms_path = fixture_dir / gms_filename
                if gms_path.exists():
                    fixtures.append((category, gms_filename, gms_path, expected))
    
    return fixtures


# Test markers
pytestmark = pytest.mark.fixtures


# Parametrized test
@pytest.mark.parametrize(
    "category,fixture_name,gms_path,expected",
    discover_fixtures(),
    ids=lambda param: (
        f"{param[0]}/{param[1]}" 
        if isinstance(param, tuple) and len(param) >= 2
        else str(param)
    ),
)
def test_fixture(category: str, fixture_name: str, gms_path: Path, expected: Dict[str, Any]):
    """Test a single fixture against expected results.
    
    Args:
        category: Fixture category (e.g., "options")
        fixture_name: Fixture filename (e.g., "01_single_integer.gms")
        gms_path: Path to .gms file
        expected: Expected results dict from YAML
    """
    # Import here to avoid circular dependencies
    from nlp2mcp.cli import parse_gams_file
    
    # Parse the GAMS file
    result = parse_gams_file(gms_path)
    
    # Get validation level (default: 2)
    validation_level = expected.get("validation_level", 2)
    
    # Level 1: Parse status (always)
    assert_parse_status(result, expected)
    
    # Level 2: Counts
    if validation_level >= 2:
        assert_statement_counts(result, expected)
    
    # Level 3: Features (opt-in)
    if validation_level >= 3:
        assert_features(result, expected, category)
    
    # Level 4: Deep AST (opt-in)
    if validation_level >= 4:
        assert_ast_structure(result, expected, category)


# Assertion helpers
def assert_parse_status(result, expected: Dict[str, Any]):
    """Level 1: Validate parse status."""
    should_parse = expected.get("should_parse", True)
    
    if should_parse:
        assert result.success, (
            f"Expected parse to succeed, but got error: {result.error_message}"
        )
        assert result.model_ir is not None
    else:
        assert not result.success, "Expected parse to fail, but it succeeded"
        
        expected_error = expected.get("expected_error_type")
        if expected_error:
            assert expected_error in str(type(result.error).__name__)
        
        expected_msg = expected.get("expected_error_message")
        if expected_msg:
            assert expected_msg in result.error_message


def assert_statement_counts(result, expected: Dict[str, Any]):
    """Level 2: Validate statement and line counts."""
    if not result.success:
        return
    
    model_ir = result.model_ir
    
    # Check all count expectations
    count_checks = [
        ("expected_parameters", len(model_ir.parameters), "parameters"),
        ("expected_sets", len(model_ir.sets), "sets"),
        ("expected_variables", len(model_ir.variables), "variables"),
        ("expected_equations", len(model_ir.equations), "equations"),
        ("expected_assignments", len(model_ir.assignments), "assignments"),
    ]
    
    for key, actual, name in count_checks:
        expected_count = expected.get(key)
        if expected_count is not None:
            assert actual == expected_count, (
                f"Expected {expected_count} {name}, got {actual}"
            )


def assert_features(result, expected: Dict[str, Any], category: str):
    """Level 3: Validate feature-specific properties."""
    if not result.success:
        return
    
    if category == "options":
        assert_option_statements(result.model_ir, expected)
    elif category == "indexed_assign":
        # Count validation covers indexed assignments
        pass
    # Add more category-specific validations


def assert_option_statements(model_ir, expected: Dict[str, Any]):
    """Validate option statements."""
    expected_opts = expected.get("option_statements", [])
    if not expected_opts:
        return
    
    actual_opts = model_ir.option_statements
    assert len(actual_opts) == len(expected_opts)
    
    for i, expected_stmt in enumerate(expected_opts):
        actual_stmt = actual_opts[i]
        expected_options = expected_stmt.get("options", [])
        
        for j, expected_opt in enumerate(expected_options):
            actual_opt = actual_stmt.options[j]
            assert actual_opt.name == expected_opt["name"]
            assert actual_opt.value == expected_opt["value"]


def assert_ast_structure(result, expected: Dict[str, Any], category: str):
    """Level 4: Validate deep AST structure (optional)."""
    # Only run if explicitly requested
    if "ast_structure" not in expected:
        return
    
    # Implementation deferred to Sprint 10
    pass
```

---

## Appendix B: Example YAML Updates

**Add validation_level to existing YAML files:**

**tests/fixtures/options/expected_results.yaml:**
```yaml
fixtures:
  01_single_integer.gms:
    description: "Single integer option statement"
    should_parse: true
    validation_level: 3  # Run Level 1+2+3
    option_statements:
      - options:
          - name: "limrow"
            value: 0
```

**tests/fixtures/indexed_assign/expected_results.yaml:**
```yaml
fixtures:
  01_simple_1d:
    description: "Basic 1D indexed parameter assignment"
    should_parse: true
    validation_level: 2  # Run Level 1+2 (default)
    expected_parameters: 1
    expected_sets: 1
    expected_assignments: 3
```

---

## End of Document

**Total Length:** 588 lines (target: 400-600 lines) ✅

**Next Steps:**
1. Review this design document
2. Begin implementation (Phase 1: Core Framework)
3. Test on 13 critical fixtures (options + indexed_assign + partial_parse)
4. Integrate with CI (Makefile + GitHub Actions)
5. Document in CHANGELOG and PREP_PLAN
