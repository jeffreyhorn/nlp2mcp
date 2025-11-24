# Synthetic Test Framework

**Purpose:** Validate individual parser features in isolation using minimal GAMS test files.

**Created:** 2025-11-24  
**Sprint:** Sprint 10 Prep Phase (Task 9)  
**Owner:** Development Team

---

## Why Synthetic Tests?

### The Problem

**Sprint 9 Lesson:** Cannot validate feature implementations work correctly when testing with complex GAMSLIB models.

**Example:**
- Implemented i++1 indexing in Sprint 9
- himmel16.gms still fails to parse
- **Question:** Does i++1 work, or is there a bug?
- **Answer:** Unknown - secondary blocker (level bounds) prevents testing

### The Solution

**Synthetic Tests:** Minimal GAMS files that test ONE feature in isolation.

**Benefits:**
1. **Clear Validation:** If synthetic test passes, feature definitely works
2. **Bug Detection:** If synthetic test fails, feature implementation has bugs
3. **Fast Feedback:** Tests run in <1 second
4. **No Dependencies:** Each test is self-contained
5. **Automated:** Run via pytest, integrate with CI

---

##  Synthetic Test Principles

### 1. MINIMAL

Tests should be as small as possible while still exercising the feature.

**Guidelines:**
- Typically 5-15 lines of GAMS code
- Only include declarations needed for the feature
- No extra complexity or "nice-to-have" elements
- Remove anything not essential to the test

**Example (i++1 indexing):**
```gams
* Minimal test for i++1 indexing
Set i /i1*i3/;
Variable x(i);
Equation test(i);
test(i).. x(i) =e= x(i++1);
```

**Not Minimal (too much):**
```gams
* Too complex
Set i /i1*i10/;
Set j /j1*j5/;
Parameter p(i);
Variable x(i), y(j), z;
Equation test1(i), test2(j), test3;
test1(i).. x(i) =e= x(i++1) + p(i);  * Extra complexity
test2(j).. y(j) =l= 10;              * Unnecessary
test3.. z =e= sum(i, x(i));          * Unnecessary
```

### 2. ISOLATED

Tests should validate ONE feature only, with no dependencies on other features.

**Guidelines:**
- Test a single feature per file
- Avoid interactions between multiple features
- No complex GAMS constructs unless testing them
- If feature needs setup, use simplest possible setup

**Example (function calls):**
```gams
* Isolated test for function calls in parameters
Parameter p;
p = uniform(1,10);  * Test only function call syntax
```

**Not Isolated (multiple features):**
```gams
* Tests multiple features at once
Set i /i1*i3/;
Parameter p(i);
Variable x(i);
Equation eq(i);
p(i) = uniform(1,10);        * Function calls
eq(i).. x(i) =e= x(i++1);    * i++1 indexing
Model test /eq/;             * Model sections
Solve test using nlp;        * Solve statements
```

### 3. VALIDATING

Tests must have clear pass/fail criteria that directly indicate feature correctness.

**Guidelines:**
- Pass = Feature works correctly
- Fail = Feature has bugs (not "feature not implemented yet")
- Expected result documented in test file
- Can be automatically verified

**Test States:**
- ✅ **PASSING:** Feature implemented and working
- ❌ **FAILING:** Feature has bugs (unexpected parse error, wrong IR, etc.)
- ⏭️  **SKIP:** Feature not yet implemented (expected to fail, marked with `pytest.mark.skip`)

**Example:**
```gams
* Synthetic Test: Function Calls in Parameters
* Expected: PARSE SUCCESS
* Validates: Parser can handle function call syntax in parameter assignments
*
* Pass Criteria:
* - Parser succeeds without errors
* - IR contains parameter 'p' with FunctionCall AST node
* - FunctionCall has func='uniform', args=[1, 10]
*
* Fail Criteria:
* - Parse error
* - IR missing parameter
* - IR has wrong AST node type
```

### 4. AUTOMATABLE

Tests must run automatically via pytest with clear success/failure reporting.

**Guidelines:**
- pytest-compatible
- Fast execution (<1 second per test)
- Parametrized for multiple features
- Clear assertion messages

**Example (pytest):**
```python
@pytest.mark.parametrize("test_file,should_parse,feature", [
    ("i_plusplus_indexing.gms", True, "i++1 indexing"),
    ("function_calls.gms", False, "function calls"),  # Not yet implemented
])
def test_synthetic_feature(test_file, should_parse, feature):
    """Test that {feature} works in isolation."""
    file_path = SYNTHETIC_DIR / test_file
    
    if should_parse:
        result = parse_model_file(str(file_path))
        assert result is not None, f"{feature} should parse successfully"
    else:
        # Feature not implemented, skip test
        pytest.skip(f"{feature} not yet implemented")
```

---

## Test Template

Use this template for all synthetic test files:

```gams
$title Synthetic Test: [FEATURE NAME]
$onText
Synthetic Test for [FEATURE NAME]

Purpose:
Validate [feature description] works in isolation.

Feature:
[What GAMS feature is being tested]

Expected Result:
[PARSE SUCCESS / PARSE FAILURE / specific behavior]

Pass Criteria:
- [Criterion 1]
- [Criterion 2]
- [...]

Fail Criteria:
- [What indicates the feature is broken]

Minimal Example:
[Explanation of why this is minimal]

Dependencies:
[List any other features this test depends on, should be minimal]

Sprint:
[Sprint when feature was/will be implemented]

$offText

* ===== TEST CODE BELOW =====

[Minimal GAMS code that tests the feature]

* ===== END TEST CODE =====

* Verification Notes:
* [Any additional notes for test verification]
```

---

## Test File Specifications

### Sprint 9 Features (Should Pass)

#### 1. i++1 Lead/Lag Indexing

**File:** `i_plusplus_indexing.gms`

**Feature:** Lead/lag indexing with i++1 and i--1 syntax

**Minimal Test:**
```gams
Set i /i1*i3/;
Variable x(i);
Equation test(i);
test(i).. x(i) =e= x(i++1);
```

**Expected:** PARSE SUCCESS  
**Pass Criteria:**
- Parser succeeds
- IR contains equation with lead indexing
- i++1 correctly represents next element

**Sprint:** 9 (Implemented)

---

#### 2. Equation Attributes

**File:** `equation_attributes.gms`

**Feature:** Equation attributes (.l, .m) for accessing dual variables

**Minimal Test:**
```gams
Variable x;
Equation obj;
obj.. x =e= 0;
Parameter dual;
dual = obj.m;
```

**Expected:** PARSE SUCCESS  
**Pass Criteria:**
- Parser succeeds
- IR contains attribute access on equation
- .m attribute correctly parsed

**Sprint:** 9 (Implemented)

---

#### 3. Model Sections

**File:** `model_sections.gms`

**Feature:** Model declaration and solve statements

**Minimal Test:**
```gams
Variable x;
Equation obj;
obj.. x =e= 0;
Model test /obj/;
Solve test using nlp;
```

**Expected:** PARSE SUCCESS  
**Pass Criteria:**
- Parser succeeds
- IR contains model declaration
- Solve statement parsed correctly

**Sprint:** 9 (Implemented)

---

### Sprint 10 Features (Initially Fail, Then Pass)

#### 4. Function Calls in Parameters

**File:** `function_calls_parameters.gms`

**Feature:** Function call syntax in parameter assignments

**Minimal Test:**
```gams
Parameter p;
p = uniform(1,10);
```

**Expected:** PARSE SUCCESS (after Sprint 10 implementation)  
**Pass Criteria:**
- Parser succeeds
- IR contains parameter with FunctionCall AST node
- Function name 'uniform' and args [1, 10] captured

**Sprint:** 10 (To be implemented)

---

#### 5. Aggregation Functions in Parameters

**File:** `aggregation_functions.gms`

**Feature:** Aggregation functions (smin, smax) in parameter assignments

**Minimal Test:**
```gams
Set i /i1*i3/;
Parameter x(i) /i1 1, i2 2, i3 3/;
Parameter xmin;
xmin = smin(i, x(i));
```

**Expected:** PARSE SUCCESS (after Sprint 10 implementation)  
**Pass Criteria:**
- Parser succeeds
- IR contains aggregation function call
- smin with set and expression arguments

**Sprint:** 10 (To be implemented)

---

#### 6. Nested Function Calls

**File:** `nested_function_calls.gms`

**Feature:** Nested function calls in expressions

**Minimal Test:**
```gams
Parameter p;
p = sqrt(sqr(5));
```

**Expected:** PARSE SUCCESS (after Sprint 10 implementation)  
**Pass Criteria:**
- Parser succeeds
- IR contains nested Call nodes
- Outer sqrt contains inner sqr

**Sprint:** 10 (To be implemented)

---

#### 7. Variable Level Bounds

**File:** `variable_level_bounds.gms`

**Feature:** Variable level (.l) assignments with indexed variables

**Minimal Test:**
```gams
Set i /i1*i2/;
Variable x(i);
x.l('i1') = 1;
x.l('i2') = 2;
```

**Expected:** PARSE SUCCESS (after Sprint 10 fix)  
**Pass Criteria:**
- Parser succeeds
- IR contains level bounds for specific indices
- No "conflicting level bound" error

**Sprint:** 10 (Bug fix)

---

#### 8. Mixed Variable Bounds

**File:** `mixed_variable_bounds.gms`

**Feature:** Mixed bound types (.fx, .l, .lo, .up) on same variable with different indices

**Minimal Test:**
```gams
Set i /i1*i3/;
Variable x(i);
x.fx('i1') = 0;
x.l('i2') = 0.5;
x.lo('i3') = 0;
x.up('i3') = 1;
```

**Expected:** PARSE SUCCESS (after Sprint 10 fix)  
**Pass Criteria:**
- Parser succeeds
- Different bound types on different indices allowed
- No spurious conflicts

**Sprint:** 10 (Bug fix)

---

#### 9. Comma-Separated Variable Declarations

**File:** `comma_separated_variables.gms`

**Feature:** Comma-separated declarations for variables

**Minimal Test:**
```gams
Variable x, y, z;
```

**Expected:** PARSE SUCCESS (already works per Task 6)  
**Pass Criteria:**
- Parser succeeds
- IR contains 3 separate variables
- All declared correctly

**Sprint:** 10 (Already implemented)

---

#### 10. Comma-Separated Scalars with Inline Values

**File:** `comma_separated_scalars.gms`

**Feature:** Comma-separated scalar declarations with mixed inline values

**Minimal Test:**
```gams
Scalar x1 /1.0/, x2, x3 /3.0/;
```

**Expected:** PARSE SUCCESS (after Sprint 10 implementation)  
**Pass Criteria:**
- Parser succeeds
- IR contains 3 scalars
- x1=1.0, x2=undefined, x3=3.0

**Sprint:** 10 (To be implemented)

---

#### 11. abort$ in If-Blocks

**File:** `abort_in_if_blocks.gms`

**Feature:** Conditional abort statements inside if-block bodies

**Minimal Test:**
```gams
Scalar x /5/;
if(x > 0,
    abort$[x > 10] "Value too large";
);
```

**Expected:** PARSE SUCCESS (already works per Task 5)  
**Pass Criteria:**
- Parser succeeds
- IR contains if-block with abort statement
- Condition correctly parsed

**Sprint:** 9/10 (Already implemented)

---

### Deferred Features (Sprint 11+)

#### 12. Nested/Subset Indexing

**File:** `nested_subset_indexing.gms`

**Feature:** Subset domain restrictions in equation declarations

**Minimal Test:**
```gams
Set i /i1*i3/;
Set low(i,i);
Alias (i,j);
low(i,j) = ord(i) > ord(j);
Equation test(low(i,j));
test(low(i,j)).. 1 =e= 1;
```

**Expected:** PARSE FAILURE (deferred to Sprint 11)  
**Status:** NOT IMPLEMENTED (High complexity, deferred)

**Sprint:** 11+ (Deferred per Task 8)

---

## Directory Structure

```
tests/synthetic/
├── README.md                           # This file
├── test_synthetic.py                   # Pytest runner
│
├── Sprint 9 Features (Should Pass)
├── i_plusplus_indexing.gms            # Lead/lag indexing
├── equation_attributes.gms            # Equation .l/.m attributes
├── model_sections.gms                 # Model and solve statements
│
├── Sprint 10 Features (Initially Fail)
├── function_calls_parameters.gms      # Function calls in parameters
├── aggregation_functions.gms          # smin/smax in parameters
├── nested_function_calls.gms          # Nested function calls
├── variable_level_bounds.gms          # Variable .l assignments
├── mixed_variable_bounds.gms          # Mixed bound types
├── comma_separated_variables.gms      # Comma-separated variables
├── comma_separated_scalars.gms        # Comma-separated scalars with values
├── abort_in_if_blocks.gms             # abort$ in if-blocks
│
└── Deferred Features (Sprint 11+)
    └── nested_subset_indexing.gms     # Subset domain restrictions
```

---

## Running Tests

### Run All Synthetic Tests

```bash
pytest tests/synthetic/test_synthetic.py -v
```

### Run Specific Feature Test

```bash
pytest tests/synthetic/test_synthetic.py::test_synthetic_feature[i_plusplus_indexing.gms] -v
```

### Run Only Passing Tests

```bash
pytest tests/synthetic/test_synthetic.py -v -m "not skip"
```

### Expected Results

**Sprint 9 Features:** Should PASS (features already implemented)
```
✓ i_plusplus_indexing.gms
✓ equation_attributes.gms
✓ model_sections.gms
```

**Sprint 10 Features:** PASS after Day 6 implementation
```
✓ function_calls_parameters.gms        (Day 6 - IMPLEMENTED)
✓ aggregation_functions.gms            (Day 6 - IMPLEMENTED)
⏭ nested_function_calls.gms            (deferred - not implemented)
⏭ variable_level_bounds.gms            (deferred - not implemented)
⏭ mixed_variable_bounds.gms            (deferred - not implemented)
✓ comma_separated_variables.gms        (already works)
✓ comma_separated_scalars.gms          (Day 3 - IMPLEMENTED)
✓ abort_in_if_blocks.gms               (Sprint 9 - already works)
```

**Deferred Features:** SKIP (not planned for Sprint 10)
```
⏭ nested_subset_indexing.gms           (deferred to Sprint 11)
```

---

## How to Add New Tests

### Step 1: Create Test File

Create `tests/synthetic/your_feature.gms` using the template above.

### Step 2: Keep It Minimal

- Only include declarations needed for the feature
- Test ONE feature, not multiple
- Use simplest possible GAMS constructs

### Step 3: Document Expected Behavior

In the test file header:
- What feature is being tested
- Expected parse result
- Pass/fail criteria
- Why this is minimal

### Step 4: Add to Pytest

Update `test_synthetic.py`:
```python
@pytest.mark.parametrize("test_file,should_parse,feature", [
    # ... existing tests ...
    ("your_feature.gms", False, "your feature name"),
])
```

### Step 5: Run Test

```bash
pytest tests/synthetic/test_synthetic.py::test_synthetic_feature[your_feature.gms] -v
```

Should skip if feature not implemented, pass after implementation.

---

## Maintenance

### After Implementing a Feature

1. Update test expectation in `test_synthetic.py`:
   - Change `should_parse` from `False` to `True`
   - Remove `pytest.skip()` if present

2. Run test to verify:
   ```bash
   pytest tests/synthetic/test_synthetic.py::test_synthetic_feature[feature_name.gms] -v
   ```

3. Test should now PASS

### If Test Fails After Implementation

1. **Feature has bugs** - Fix the implementation
2. **Test is wrong** - Fix the test (rare, tests should be simple)
3. **Test has secondary dependency** - Simplify test to remove dependency

---

## Best Practices

### DO

✅ Keep tests minimal (5-15 lines)  
✅ Test one feature per file  
✅ Use clear, descriptive file names  
✅ Document expected behavior in test file  
✅ Make tests fast (<1 second)  
✅ Use pytest parametrization  
✅ Update tests after implementing features  

### DON'T

❌ Don't test multiple features in one file  
❌ Don't add unnecessary complexity  
❌ Don't depend on other unimplemented features  
❌ Don't use real-world complex models  
❌ Don't skip documentation in test files  
❌ Don't forget to update pytest after implementing  

---

## Benefits Summary

1. **Feature Validation:** Know immediately if a feature works
2. **Bug Detection:** Isolate bugs to specific features
3. **Fast Feedback:** Tests run in <1 second
4. **CI Integration:** Automated testing in CI pipeline
5. **Documentation:** Tests serve as feature examples
6. **Confidence:** Prove features work before integration
7. **Debugging:** Easier to debug minimal tests than complex models

---

## References

- Sprint 9 Retrospective: Feature validation challenges
- Sprint 10 PROJECT_PLAN.md: Phase 5 - Synthetic Test Suite
- Sprint 10 PREP_PLAN.md: Task 9 - Design Synthetic Test Framework
- KNOWN_UNKNOWNS.md: Unknown 10.7.1 (Synthetic Test Design)

---

**Created:** 2025-11-24  
**Version:** 1.0  
**Author:** Development Team  
**Sprint:** Sprint 10 Prep Phase (Task 9)
