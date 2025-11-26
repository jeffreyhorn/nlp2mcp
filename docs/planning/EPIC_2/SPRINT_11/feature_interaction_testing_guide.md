# Feature Interaction Testing Guide

**Date:** 2025-11-26  
**Purpose:** Framework for testing feature combinations to catch interaction bugs  
**Sprint:** 11 Prep Task 11

---

## Why Feature Interaction Testing?

### Problem: Features Work Alone, Fail Together

Individual features may pass unit tests but interact poorly:
- **Simplification + function calls:** May simplify function arguments incorrectly
- **Nested indexing + variable bounds:** Index extraction may fail with complex nesting
- **Comma-separated declarations + inline values:** Parsing ambiguity
- **Diagnostics mode + simplification:** May not capture all transformation details

### Solution: Systematic Interaction Testing

Test high-risk feature combinations incrementally to detect interaction bugs before they reach production.

---

## Feature Inventory

### Sprint 9 Features
1. **i++1 Indexing:** Offset indexing patterns (`i++1`, `i-1`)
2. **Model Sections:** Model block parsing and validation
3. **Equation Attributes:** Equation attribute access (`.l`, `.m`, `.lo`, `.up`)
4. **Conversion Pipeline:** GAMS → IR → MCP transformation
5. **Fixture Validation:** Automated test fixture generation

### Sprint 10 Features
6. **Variable Bound Literals:** Indexed variable bound assignments (`x.lo(i) = value`)
7. **Comma-Separated Scalars:** Multiple scalar declarations (`Scalar a /5/, b /10/`)
8. **Function Calls (Parse-Only):** Mathematical and aggregation functions

### Sprint 11 Features (Planned)
9. **maxmin.gms Support:** TBD (complex min/max operations)
10. **Simplification Improvements:** Advanced expression simplification
11. **Diagnostics Mode:** `--diagnostic` flag for pipeline visibility

---

## High-Risk Feature Pairs

### Risk Assessment Matrix

| Feature Pair | Risk Level | Reason | Priority |
|--------------|------------|--------|----------|
| Function Calls + Nested Indexing | HIGH | Both involve complex expression parsing | P0 |
| Variable Bounds + Nested Indexing | HIGH | Index extraction from attribute access | P0 |
| Function Calls + Simplification | MEDIUM | Simplification may alter function arguments | P1 |
| Comma-Separated + Inline Values | MEDIUM | Parsing ambiguity with complex expressions | P1 |
| Diagnostics + Simplification | MEDIUM | Must capture transformation details | P1 |
| i++1 Indexing + Function Calls | LOW | Orthogonal features (index vs. expression) | P2 |
| Model Sections + Any Feature | LOW | Structural feature, low interaction risk | P3 |

**Risk Levels:**
- **HIGH:** Features share AST manipulation or semantic analysis code
- **MEDIUM:** Features may affect same data structures or output
- **LOW:** Features are orthogonal (operate on different parts of system)

**Priority:**
- **P0:** Test in Sprint 11 (before feature implementation)
- **P1:** Test in Sprint 11 (after basic features stable)
- **P2:** Test in Sprint 12 (lower urgency)
- **P3:** Test as needed (minimal interaction expected)

---

## Test Organization

### Directory Structure

```
tests/
├── integration/
│   └── test_feature_interactions.py      # Main interaction test file
├── synthetic/
│   └── combined_features/                # Synthetic test models
│       ├── README.md                     # Documentation
│       ├── functions_with_nested_indexing.gms
│       ├── bounds_with_nested_indexing.gms
│       ├── functions_with_simplification.gms
│       ├── comma_separated_complex.gms
│       └── diagnostics_with_simplification.gms
```

### Test File Naming Conventions

**Integration Tests:** `test_feature_interactions.py`
- Class per feature pair: `TestFunctionCallsWithNestedIndexing`
- Method per scenario: `test_sqrt_with_double_nested_indices`

**Synthetic Models:** `{feature1}_with_{feature2}.gms`
- Descriptive names showing feature combination
- README.md documents rationale and expected behavior

---

## Test Structure

### Integration Test Template

```python
\"\"\"Feature interaction tests.

Tests combinations of features to detect interaction bugs.
Organized by feature pair with risk-based prioritization.
\"\"\"

import pytest
from src.ir.parser import parse_model_file
from src.ir.ast import Call, BinaryOp

pytestmark = pytest.mark.integration


class TestHighRiskInteractions:
    \"\"\"HIGH risk feature pairs (P0 - test before Sprint 11 implementation).\"\"\"

    class TestFunctionCallsWithNestedIndexing:
        \"\"\"Function calls + nested indexing interaction.
        
        Risk: Both involve complex expression parsing, may interfere.
        Example: sqrt(data(i,subset(j))) - nested index inside function arg.
        \"\"\"

        def test_function_with_single_nested_index(self, tmp_path):
            \"\"\"Test function call with single level of index nesting.\"\"\"
            # Test implementation
            pass

        def test_function_with_double_nested_index(self, tmp_path):
            \"\"\"Test function call with double-nested indices.\"\"\"
            # Test implementation
            pass

    class TestVariableBoundsWithNestedIndexing:
        \"\"\"Variable bounds + nested indexing interaction.
        
        Risk: Index extraction from attribute access may fail with nesting.
        Example: x.lo(subset(i)) = value - nested index in bound assignment.
        \"\"\"

        def test_bounds_with_nested_index(self, tmp_path):
            \"\"\"Test variable bound with nested index extraction.\"\"\"
            # Test implementation
            pass


class TestMediumRiskInteractions:
    \"\"\"MEDIUM risk feature pairs (P1 - test after basic features stable).\"\"\"

    class TestFunctionCallsWithSimplification:
        \"\"\"Function calls + simplification interaction.
        
        Risk: Simplification may alter function arguments incorrectly.
        Example: sqrt(2*x + 2*y) → sqrt(2*(x+y)) should preserve Call node.
        \"\"\"

        def test_simplification_preserves_function_call(self, tmp_path):
            \"\"\"Test that simplification doesn't break function calls.\"\"\"
            # Test implementation
            pass


class TestLowRiskInteractions:
    \"\"\"LOW risk feature pairs (P2/P3 - test as needed).\"\"\"

    # Optional: Add low-risk tests if time permits
    pass
```

### Synthetic Model Template

```gams
$ontext
Feature Interaction Test: Function Calls + Nested Indexing

Purpose: Test that function calls work correctly with nested index expressions
Risk Level: HIGH
Expected Behavior: Function should accept nested index without parse error

Sprint: 11 Prep
Date: 2025-11-26
$offtext

Sets
    i / i1*i3 /
    j / j1*j2 /
    subset(i) / i1, i3 /;

Parameters
    data(i,j)
    result(i);

* Populate data
data(i,j) = ord(i) * ord(j);

* HIGH RISK: Function call with nested indexing
* Pattern: sqrt(data(subset(i), j))
result(i) = sqrt(data(subset(i), 'j1'));

Display result;
```

---

## Test Implementation Strategy

### Phase 1: High-Risk Pairs (Sprint 11)

**Estimated Time:** 3 hours

1. **Function Calls + Nested Indexing** (1h)
   - Single-nested: `sqrt(data(subset(i)))`
   - Double-nested: `exp(values(outer(inner(k))))`
   - Test: Parse succeeds, Call node structure correct

2. **Variable Bounds + Nested Indexing** (1h)
   - Nested bound: `x.lo(subset(i)) = 0`
   - Complex nesting: `y.up(filter(data(j) > threshold)) = 100`
   - Test: Index extraction works, bounds applied correctly

3. **Function Calls + Simplification** (1h)
   - Simplifiable args: `sqrt(2*x + 2*y)` → `sqrt(2*(x+y))`
   - Nested calls: `exp(log(x*y))` → may simplify to `x*y` (future)
   - Test: Call nodes preserved, arguments simplified

### Phase 2: Medium-Risk Pairs (Sprint 11/12)

**Estimated Time:** 2 hours

4. **Comma-Separated + Complex Expressions** (0.5h)
   - Inline calculations: `Scalar a /(2+3)/, b /sqrt(25)/`
   - Test: Parsing disambiguates commas vs. expression operators

5. **Diagnostics + Simplification** (1h)
   - Capture transformations: `--diagnostic` shows each simplification step
   - Test: All transformations logged, metrics accurate

6. **Other Medium-Risk** (0.5h)
   - Add as needed based on Sprint 11 features

### Phase 3: Low-Risk Pairs (Sprint 12+)

**Test only if interactions suspected based on bug reports or code changes.**

---

## When to Run Interaction Tests

### During Development (Continuous)

**Trigger:** After implementing any new feature
- Run interaction tests for all pairs involving the new feature
- Example: After implementing `maxmin.gms` support, run tests for:
  - maxmin + simplification
  - maxmin + function calls
  - maxmin + nested indexing

### Before PR Merge (Gate)

**Requirement:** All interaction tests passing
- Part of CI pipeline: `make test` includes interaction tests
- Reviewer verifies interaction tests exist for new features
- Block merge if new feature lacks interaction tests

### After Each Sprint (Validation)

**Checkpoint:** Sprint retrospective includes interaction test review
- Measure: % feature pairs with interaction tests
- Target: 100% HIGH-risk pairs, 80% MEDIUM-risk pairs tested
- Action: Add missing tests to next sprint backlog

---

## Adding New Interaction Tests

### Step-by-Step Process

**1. Identify Feature Pair**
```python
# New feature: "Aggressive Simplification"
# Existing feature: "Function Calls"
# Risk assessment: MEDIUM (may over-simplify function arguments)
```

**2. Create Synthetic Model**
```bash
# Create test file
touch tests/synthetic/combined_features/aggressive_simpl_with_functions.gms

# Document rationale in file header
$ontext
Feature Interaction: Aggressive Simplification + Function Calls
Risk: May incorrectly simplify function arguments
Expected: Function calls preserved, args simplified conservatively
$offtext
```

**3. Write Integration Test**
```python
class TestAggressiveSimplificationWithFunctions:
    \"\"\"Aggressive simplification + function calls interaction.\"\"\"

    def test_preserves_function_structure(self, tmp_path):
        \"\"\"Test that aggressive simplification doesn't break functions.\"\"\"
        test_file = tmp_path / "test.gms"
        test_file.write_text(\"\"\"
        Parameter result;
        result = sqrt(2*x*x + 2*y*y);  # May simplify to sqrt(2*(x^2 + y^2))
        \"\"\")
        
        model = parse_model_file(test_file)
        
        # Verify Call node preserved
        assert isinstance(model.params["result"].expressions[()], Call)
        assert model.params["result"].expressions[()].func == "sqrt"
        
        # Verify argument simplified (if simplification enabled)
        # But Call structure intact
```

**4. Update Test Count**
- Add to interaction test suite
- Update this guide with new test case
- Document in PR description

**5. Run Quality Checks**
```bash
make typecheck && make lint && make format && make test
```

---

## Measuring Interaction Test Coverage

### Coverage Metrics

**Formula:**
```
Interaction Coverage = (Pairs Tested / High-Risk Pairs) * 100%

Where:
- Pairs Tested = # of HIGH-risk pairs with ≥1 interaction test
- High-Risk Pairs = All pairs with risk level = HIGH
```

**Sprint 11 Target:**
- HIGH-risk pairs: 100% coverage (all 3 pairs tested)
- MEDIUM-risk pairs: 60% coverage (3 of 5 pairs tested)
- LOW-risk pairs: Optional (test if bugs found)

### Coverage Tracking

**Method 1: Manual Count**
```bash
# Count interaction test classes
grep -c "class Test.*With" tests/integration/test_feature_interactions.py

# Expected: ≥3 for Sprint 11 (3 HIGH-risk pairs)
```

**Method 2: Test Markers**
```python
@pytest.mark.interaction
@pytest.mark.risk_high
class TestFunctionCallsWithNestedIndexing:
    pass

# Run: pytest -m "interaction and risk_high" --collect-only
# Count: Should match # of HIGH-risk pairs
```

---

## Common Interaction Patterns

### Pattern 1: Shared AST Manipulation

**Risk:** Two features modify same AST nodes → conflicts

**Example:** Simplification + Function Calls
- Simplification traverses AST to combine terms
- Function Calls introduce `Call` nodes in AST
- **Risk:** Simplification may incorrectly transform Call arguments

**Test Strategy:**
- Verify Call nodes preserved after simplification
- Check argument expressions simplified correctly
- Ensure function structure intact

### Pattern 2: Sequential Processing

**Risk:** Feature B depends on Feature A's output → ordering matters

**Example:** Parsing + Semantic Analysis + Simplification
- Parser creates AST
- Semantic analysis validates and enriches AST
- Simplification transforms expressions
- **Risk:** Simplification may invalidate semantic analysis results

**Test Strategy:**
- Test pipeline with multiple features enabled
- Verify intermediate states valid
- Check final output correct

### Pattern 3: Overlapping Syntax

**Risk:** Two features use similar syntax → parsing ambiguity

**Example:** Comma-Separated Declarations + Function Call Arguments
- `Scalar a, b;` uses commas for separation
- `smin(i, expr)` uses commas for function arguments
- **Risk:** Parser may misinterpret commas in complex expressions

**Test Strategy:**
- Test edge cases with nested commas
- Verify parser disambiguates correctly
- Check error messages clear

---

## Troubleshooting Interaction Bugs

### Debugging Workflow

**Step 1: Isolate the Interaction**
```python
# Test Feature A alone
def test_feature_a_alone():
    # Should pass

# Test Feature B alone
def test_feature_b_alone():
    # Should pass

# Test A + B together
def test_feature_a_with_b():
    # Fails - interaction bug confirmed
```

**Step 2: Identify the Failure Point**
```python
# Add intermediate assertions
model = parse_model_file(test_file)
assert model.parsed_successfully  # Parser OK?

analyzed = semantic_analyze(model)
assert analyzed.valid  # Semantic analysis OK?

simplified = simplify(analyzed)
assert simplified.correct  # Simplification OK?
```

**Step 3: Inspect AST/IR**
```python
# Print AST structure
print(model.params["x"].expressions[()])
# Expected: Call(func='sqrt', args=[...])
# Actual: BinaryOp(...) - Call node lost!

# Identify where Call node disappeared
```

**Step 4: Fix and Validate**
```python
# Fix the interaction bug
# Re-run interaction test
assert test_passes()

# Re-run individual feature tests
assert feature_a_test_passes()
assert feature_b_test_passes()

# No regressions
```

---

## Examples

### Example 1: Function Calls + Nested Indexing (HIGH Risk)

**Synthetic Model:** `tests/synthetic/combined_features/functions_with_nested_indexing.gms`

```gams
Sets
    i / i1*i5 /
    subset(i) / i1, i3, i5 /;

Parameters
    data(i)
    result;

data(i) = ord(i) * 2;

* Function call with nested index
result = sqrt(data(subset(i)));  # HIGH RISK: nested index in function arg
```

**Integration Test:**

```python
def test_function_with_nested_index(tmp_path):
    \"\"\"Test function call accepts nested index expression.\"\"\"
    test_file = tmp_path / "test.gms"
    test_file.write_text(\"\"\"
    Sets i /i1*i3/, subset(i) /i1,i3/;
    Parameters data(i), result;
    data(i) = ord(i);
    result = sqrt(data(subset(i)));
    \"\"\")
    
    model = parse_model_file(test_file)
    
    # Verify parse succeeded
    assert "result" in model.params
    
    # Verify Call node structure
    expr = model.params["result"].expressions[()]
    assert isinstance(expr, Call)
    assert expr.func == "sqrt"
    
    # Verify nested index preserved in argument
    arg = expr.args[0]
    # arg should be IndexedAccess(data, subset(i))
    assert hasattr(arg, 'indices')  # Nested indexing preserved
```

### Example 2: Variable Bounds + Nested Indexing (HIGH Risk)

**Synthetic Model:** `tests/synthetic/combined_features/bounds_with_nested_indexing.gms`

```gams
Sets
    i / i1*i5 /
    active(i) / i1, i3 /;

Variables
    x(i);

* Variable bound with nested index
x.lo(active(i)) = 0;    # HIGH RISK: nested index in bound
x.up(active(i)) = 100;
```

**Integration Test:**

```python
def test_bounds_with_nested_index(tmp_path):
    \"\"\"Test variable bound assignment with nested index.\"\"\"
    test_file = tmp_path / "test.gms"
    test_file.write_text(\"\"\"
    Sets i /i1*i3/, active(i) /i1,i3/;
    Variables x(i);
    x.lo(active(i)) = 0;
    x.up(active(i)) = 100;
    \"\"\")
    
    model = parse_model_file(test_file)
    
    # Verify bounds set correctly for active subset
    assert "x" in model.variables
    
    # Check bound structure includes nested index info
    var = model.variables["x"]
    assert hasattr(var, 'lower_bounds')
    assert hasattr(var, 'upper_bounds')
    
    # Verify nested index extracted correctly
    # (implementation details depend on bound storage)
```

---

## Success Criteria

**Sprint 11 Goals:**

1. ✅ **HIGH-risk pairs tested:** 3/3 (100%)
   - Function Calls + Nested Indexing
   - Variable Bounds + Nested Indexing
   - Function Calls + Simplification

2. ✅ **MEDIUM-risk pairs tested:** 3/5 (60%)
   - Comma-Separated + Complex Expressions
   - Diagnostics + Simplification
   - One additional based on Sprint 11 features

3. ✅ **Framework established:**
   - `test_feature_interactions.py` with class structure
   - `tests/synthetic/combined_features/` directory
   - This guide documenting strategy and examples

4. ✅ **CI integration:**
   - Interaction tests run in `make test`
   - PR checklist includes interaction tests
   - Reviewer validation required

**Measure at Sprint 11 Retrospective:**
- Interaction bugs found: Target 0 (proactive testing prevents)
- Test runtime: Target <5 seconds total (no performance impact)
- Coverage: Target 100% HIGH-risk pairs, 60% MEDIUM-risk pairs

---

## References

- Sprint 10 Retrospective: Action Item (Feature Interaction Testing)
- KNOWN_UNKNOWNS.md: Unknown 5.3 (Feature Interaction Test Coverage)
- Sprint 9 Features: i++1, Model Sections, Equation Attributes
- Sprint 10 Features: Variable Bounds, Comma-Separated Scalars, Function Calls
- Sprint 11 Features: maxmin.gms, Simplification, Diagnostics Mode
