# Sprint 8 Test Fixture Strategy

**Sprint:** Epic 2 - Sprint 8 Prep  
**Created:** 2025-11-17  
**Purpose:** Define comprehensive test fixture strategy for Sprint 8 parser features

---

## Executive Summary

Sprint 8 will create **13 test fixtures** for three feature categories: option statements (5 fixtures), indexed assignments (5 fixtures), and partial parse metrics (3 fixtures). This strategy follows the proven Sprint 7 pattern (34 fixtures created) and ensures comprehensive test coverage for Sprint 8's parse rate target of 40-50%.

**Key Findings:**
- **Total Fixtures:** 13 (5 option + 5 indexed + 3 partial)
- **Sprint 7 Patterns:** Fully reusable (directory structure, YAML format, README templates)
- **Fixture Creation Effort:** ~4 hours (13 fixtures × ~18 min each)
- **Coverage:** 100% of Sprint 8 parser features
- **Backward Compatibility:** Yes (extends Sprint 7 YAML schema)

---

## Table of Contents

1. [Sprint 7 Pattern Review](#sprint-7-pattern-review)
2. [Option Statement Fixtures](#option-statement-fixtures-5-fixtures)
3. [Indexed Assignment Fixtures](#indexed-assignment-fixtures-5-fixtures)
4. [Partial Parse Metric Fixtures](#partial-parse-metric-fixtures-3-fixtures)
5. [expected_results.yaml Structure](#expected_resultsyaml-structure)
6. [README Templates](#readme-templates)
7. [Implementation Plan](#implementation-plan)

---

## Sprint 7 Pattern Review

### Sprint 7 Achievements

From Sprint 7 Day 9 CHANGELOG entry:
- **34 fixtures created** across 4 directories
- **Fixture breakdown:**
  - `tests/fixtures/preprocessor/` - 9 fixtures
  - `tests/fixtures/sets/` - 8 fixtures
  - `tests/fixtures/multidim/` - 8 fixtures
  - `tests/fixtures/statements/` - 9 fixtures
- **Pattern:** Directory per feature category, expected_results.yaml, README.md

### Reusable Patterns

**1. Directory Structure**
```
tests/fixtures/<feature_name>/
├── 01_<fixture_name>.gms
├── 02_<fixture_name>.gms
├── ...
├── expected_results.yaml
└── README.md
```

**2. YAML Structure** (from `tests/fixtures/statements/expected_results.yaml`):
```yaml
fixtures:
  <fixture_name>:
    description: "..."
    expected_status: "SUCCESS" | "FAILED"
    expected_equations: N
    expected_variables: N
    expected_error_type: "..." (if FAILED)
    priority: "Critical" | "High" | "Medium" | "Low"
    notes: "..."

summary:
  total_fixtures: N
  expected_success: M
  expected_failures: K
  coverage:
    - "Feature 1"
    - "Feature 2"
```

**3. README Template** (from `tests/fixtures/statements/README.md`):
- Purpose section
- Fixture structure explanation
- Coverage section
- Fixture list with descriptions
- Usage examples
- Expected results summary
- Status section with completion checkboxes

**Decision:** ✅ **Fully reuse Sprint 7 patterns** for Sprint 8 fixtures

---

## Option Statement Fixtures (5 Fixtures)

### Background

From Task 3 (Research Option Statement Syntax):
- **GAMS Syntax:** `option <name> = <value> [, <name> = <value>]*;`
- **Sprint 8 Scope:** Integer options (limrow, limcol, decimals)
- **Unlocks:** mhw4dx.gms (+10% parse rate)

### Fixture 1: Single Integer Option

**File:** `tests/fixtures/options/01_single_integer.gms`

**Purpose:** Test basic single option statement with integer value

**GAMS Code:**
```gams
Set i /1*5/;
Scalar x /10/;

option limrow = 0;

Variable obj;
Equation objdef;
objdef.. obj =e= x;

Model m /all/;
solve m using nlp minimizing obj;
```

**Expected Result:** ✅ SUCCESS
- Parses option statement
- Stores option in IR (name: "limrow", value: 0)
- No semantic effects (mock/skip approach)

---

### Fixture 2: Multiple Options in One Statement

**File:** `tests/fixtures/options/02_multiple_options.gms`

**Purpose:** Test comma-separated multiple options

**GAMS Code:**
```gams
Set i /1*5/;
Scalar x /10/;

option limrow = 0, limcol = 0;

Variable obj;
Equation objdef;
objdef.. obj =e= x;

Model m /all/;
solve m using nlp minimizing obj;
```

**Expected Result:** ✅ SUCCESS
- Parses both options
- Stores: [("limrow", 0), ("limcol", 0)]

---

### Fixture 3: decimals Option

**File:** `tests/fixtures/options/03_decimals_option.gms`

**Purpose:** Test decimals display option (different option type)

**GAMS Code:**
```gams
Set i /1*5/;
Parameter p(i) /1 1.123456789, 2 2.987654321/;

option decimals = 8;

Scalar result;
result = sum(i, p(i));

display result;
```

**Expected Result:** ✅ SUCCESS
- Parses decimals option
- Stores: ("decimals", 8)
- Display statement skipped (as in Sprint 7)

---

### Fixture 4: Options Placement (Before and After Declarations)

**File:** `tests/fixtures/options/04_placement.gms`

**Purpose:** Test option statements in different locations

**GAMS Code:**
```gams
option limrow = 0;

Set i /1*5/;
Scalar x /10/;

option decimals = 3;

Variable obj;
Equation objdef;
objdef.. obj =e= x;

option limcol = 0;

Model m /all/;
solve m using nlp minimizing obj;
```

**Expected Result:** ✅ SUCCESS
- Options parsed in any position
- Order doesn't matter for mock/skip approach

---

### Fixture 5: Option Statement from mhw4dx.gms (Real GAMSLib Example)

**File:** `tests/fixtures/options/05_mhw4dx_pattern.gms`

**Purpose:** Test exact pattern from mhw4dx.gms (ensures unlock)

**GAMS Code:** (Simplified excerpt from mhw4dx.gms)
```gams
Set i /1*10/;
Variable x(i), obj;
Equation objdef, cons(i);

objdef.. obj =e= sum(i, x(i));
cons(i).. x(i) =l= 10;

option limcol = 0, limrow = 0;

Model m /all/;
solve m using nlp minimizing obj;

option decimals = 8;

display x.l;
```

**Expected Result:** ✅ SUCCESS
- Parses all 3 option statements
- Validates mhw4dx.gms unlock scenario

---

### Option Fixtures Summary

| Fixture | Test Case | Priority | Expected |
|---------|-----------|----------|----------|
| 01 | Single integer option | Critical | SUCCESS |
| 02 | Multiple options (comma-separated) | Critical | SUCCESS |
| 03 | decimals option type | High | SUCCESS |
| 04 | Option placement flexibility | Medium | SUCCESS |
| 05 | mhw4dx.gms pattern (real-world) | Critical | SUCCESS |

**Coverage:** 100% of Sprint 8 option statement scope (integer options, multi-option syntax)

---

## Indexed Assignment Fixtures (5 Fixtures)

### Background

From Task 7 (Indexed Assignments Research):
- **4 GAMS Patterns Identified:**
  1. Simple 1D indexed assignment
  2. Multi-dimensional 2D/3D
  3. Variable attribute access (`.l`, `.m`)
  4. Indexed expressions on RHS
- **Unlocks:** mathopt1.gms + trig.gms (+20% parse rate)

### Fixture 1: Simple 1D Indexed Assignment

**File:** `tests/fixtures/indexed_assign/01_simple_1d.gms`

**Purpose:** Test basic 1D parameter indexed assignment

**GAMS Code:**
```gams
Set i /i1, i2, i3/;
Parameter p(i);

p('i1') = 10;
p('i2') = 20;
p('i3') = 30;

display p;
```

**Expected Result:** ✅ SUCCESS
- Parses indexed assignments
- Stores: p.values = {('i1',): 10.0, ('i2',): 20.0, ('i3',): 30.0}

---

### Fixture 2: Multi-Dimensional 2D Indexed Assignment

**File:** `tests/fixtures/indexed_assign/02_multi_dim_2d.gms`

**Purpose:** Test 2D parameter indexed assignment (mathopt1.gms pattern)

**GAMS Code:**
```gams
Set scenario /global, solver/;
Set metric /x1, x2/;
Parameter report(scenario, metric);

report('global','x1') = 1.0;
report('global','x2') = 1.0;
report('solver','x1') = 0.95;
report('solver','x2') = 1.02;

display report;
```

**Expected Result:** ✅ SUCCESS
- Parses 2D indexed assignments
- Stores: report.values = {('global', 'x1'): 1.0, ('solver', 'x2'): 1.02, ...}

---

### Fixture 3: Variable Attribute Access in Assignments

**File:** `tests/fixtures/indexed_assign/03_variable_attributes.gms`

**Purpose:** Test variable `.l` attribute access (trig.gms pattern)

**GAMS Code:**
```gams
Variable x1, x2;
Scalar diff1, diff2;

x1.l = 2.5;
x2.l = 3.7;

diff1 = 10.0 - x1.l;
diff2 = 5.0 - x2.l;

Equation objdef;
objdef.. x1 + x2 =e= 6;

Model m /all/;
solve m using nlp minimizing x1;
```

**Expected Result:** ✅ SUCCESS
- Parses `.l` attribute assignments (left-hand side)
- Parses `.l` attribute access in expressions (right-hand side)
- Stores: x1.level = 2.5, x2.level = 3.7

---

### Fixture 4: Indexed Expressions on RHS

**File:** `tests/fixtures/indexed_assign/04_indexed_expressions.gms`

**Purpose:** Test indexed parameter references in expressions (mathopt1.gms pattern)

**GAMS Code:**
```gams
Set metric /global, solver, diff/;
Parameter data(metric);

data('global') = 1.0;
data('solver') = 0.95;
data('diff') = data('global') - data('solver');

display data;
```

**Expected Result:** ✅ SUCCESS
- Parses indexed parameters in RHS expressions
- Evaluates: data('diff') = Sub(ParameterRef('data', ('global',)), ParameterRef('data', ('solver',)))

---

### Fixture 5: Error Handling - Index Count Mismatch

**File:** `tests/fixtures/indexed_assign/05_error_index_mismatch.gms`

**Purpose:** Test validation of index count matching parameter domain

**GAMS Code:**
```gams
Set i /i1, i2/;
Set j /j1, j2/;
Parameter p(i, j);

p('i1') = 10;  * ERROR: Parameter expects 2 indices, got 1
```

**Expected Result:** ❌ FAILED
- **Error Type:** ParserSemanticError
- **Error Message:** "Parameter 'p' expects 2 indices, got 1"
- **Purpose:** Validate index count validation logic

---

### Indexed Assignment Fixtures Summary

| Fixture | Test Case | Priority | Expected |
|---------|-----------|----------|----------|
| 01 | Simple 1D indexed assignment | High | SUCCESS |
| 02 | Multi-dimensional 2D | Critical | SUCCESS |
| 03 | Variable attributes (`.l`) | Critical | SUCCESS |
| 04 | Indexed expressions on RHS | Critical | SUCCESS |
| 05 | Error: Index count mismatch | Medium | FAILED (validation) |

**Coverage:** 100% of 4 GAMS indexed assignment patterns + error handling

---

## Partial Parse Metric Fixtures (3 Fixtures)

### Background

From PROJECT_PLAN.md Sprint 8:
- **Goal:** Partial parse metrics (e.g., "himmel16: 85% parsed, needs [i++1 indexing]")
- **Purpose:** Track incremental progress, identify missing features

### Fixture 1: Partial Parse with Unsupported Feature

**File:** `tests/fixtures/partial_parse/01_himmel16_pattern.gms`

**Purpose:** Test partial parse with lead/lag indexing error (himmel16.gms pattern)

**GAMS Code:**
```gams
Set i /i1*i5/;
Variable x(i), y(i), area(i);
Equation areadef(i);

* This equation will fail due to i++1 indexing
areadef(i).. area(i) =e= 0.5*(x(i)*y(i++1) - y(i)*x(i++1));

Model m /all/;
solve m using nlp minimizing area('i1');
```

**Expected Result:** ❌ FAILED (Partial Parse)
- **Parse Percentage:** ~80-92% (parsed declarations, failed at equation definition)
- **Statements Parsed:** Set, Variable declarations (3 statements)
- **Statements Failed:** Equation definition (1 statement)
- **Missing Feature:** "Lead/lag indexing (i++1)"
- **Error Location:** Line 6 (areadef equation)

---

### Fixture 2: Partial Parse with Function Calls

**File:** `tests/fixtures/partial_parse/02_circle_pattern.gms`

**Purpose:** Test partial parse with function call in assignment (circle.gms pattern)

**GAMS Code:**
```gams
Set i /i1*i10/;
Parameter x(i), y(i);

* These assignments will fail due to uniform() function calls
x(i) = uniform(1,10);
y(i) = uniform(1,10);

Scalar result;
result = sum(i, x(i) + y(i));
display result;
```

**Expected Result:** ❌ FAILED (Partial Parse)
- **Parse Percentage:** ~70-100% (parsed declarations, failed at assignments)
- **Statements Parsed:** Set, Parameter declarations (2 statements)
- **Statements Failed:** Assignments with function calls (2 statements)
- **Missing Feature:** "Function calls in assignments (uniform, normal, etc.)"
- **Error Location:** Line 5 (x(i) assignment)

---

### Fixture 3: Successful Complete Parse (Baseline)

**File:** `tests/fixtures/partial_parse/03_complete_success.gms`

**Purpose:** Test 100% parse success (baseline for partial metrics)

**GAMS Code:**
```gams
Set i /1*5/;
Parameter p(i) /1 10, 2 20, 3 30/;
Scalar x /5/;

Variable obj;
Equation objdef;
objdef.. obj =e= sum(i, p(i)) + x;

Model m /all/;
solve m using nlp minimizing obj;
```

**Expected Result:** ✅ SUCCESS (100% Parse)
- **Parse Percentage:** 100%
- **Statements Parsed:** 7/7
- **Statements Failed:** 0
- **Missing Features:** None
- **Purpose:** Validate that 100% parse is correctly reported

---

### Partial Parse Fixtures Summary

| Fixture | Partial Parse Scenario | Parse % | Missing Feature | Priority |
|---------|------------------------|---------|-----------------|----------|
| 01 | himmel16 pattern (i++1) | ~80% | Lead/lag indexing | High |
| 02 | circle pattern (function calls) | ~70% | Function calls in assignments | High |
| 03 | Complete success baseline | 100% | None | Medium |

**Coverage:** Partial parse metric calculation + missing feature extraction + 100% baseline

---

## expected_results.yaml Structure

### Sprint 8 Extensions

Building on Sprint 7 YAML schema, Sprint 8 adds:

```yaml
fixtures:
  <fixture_name>:
    description: "..."
    expected_status: "SUCCESS" | "FAILED" | "PARTIAL"  # NEW: PARTIAL status
    expected_equations: N
    expected_variables: N
    expected_error_type: "..." (if FAILED)
    priority: "Critical" | "High" | "Medium" | "Low"
    notes: "..."
    
    # NEW: Option statement fields
    option_statements:  # Optional, for option fixtures
      - name: "limrow"
        value: 0
      - name: "limcol"
        value: 0
    
    # NEW: Indexed assignment fields
    indexed_assignments:  # Optional, for indexed assignment fixtures
      - parameter: "report"
        indices: ["'global'", "'x1'"]
        value: 1.0
    
    # NEW: Variable attribute fields
    variable_attributes:  # Optional, for variable attribute fixtures
      - variable: "x1"
        attribute: "l"  # level
        value: 2.5
    
    # NEW: Partial parse fields
    parse_percentage: 85  # Optional, for partial parse fixtures
    statements_parsed: 6
    statements_total: 7
    missing_features:  # Optional, for partial parse fixtures
      - "Lead/lag indexing (i++1)"
      - "Function calls in assignments"
    error_location:  # Optional, for partial parse fixtures
      line: 6
      statement: "areadef(i).. area(i) =e= ..."

summary:
  total_fixtures: N
  expected_success: M
  expected_failures: K
  expected_partial: P  # NEW: Count of partial parse fixtures
  coverage:
    - "Feature 1"
    - "Feature 2"
```

### Backward Compatibility

**Existing Sprint 7 Fixtures:**
- All Sprint 7 YAML files remain valid (no required new fields)
- Sprint 7 tests continue to pass without modification

**Sprint 8 Fixtures:**
- Use new optional fields as needed
- Ingestion script checks for field presence before accessing

---

## README Templates

### Template 1: Option Statement Fixtures README

```markdown
# Option Statement Fixtures

This directory contains test fixtures for GAMS option statement features.

## Purpose

These fixtures test the parser's ability to handle option statements with integer values (Sprint 8 scope: limrow, limcol, decimals).

## Fixture Structure

Each fixture consists of:
- `*.gms` - Input GAMS file with specific option pattern
- `expected_results.yaml` - Expected parsing results

## Coverage

Target: 5 option fixtures covering:
- Single integer option (`option limrow = 0`)
- Multiple options in one statement (`option limrow = 0, limcol = 0`)
- decimals option type (`option decimals = 8`)
- Option placement flexibility (before/after declarations)
- Real-world pattern from mhw4dx.gms

## Fixture List

1. **01_single_integer.gms** - Single option with integer value
2. **02_multiple_options.gms** - Comma-separated multiple options
3. **03_decimals_option.gms** - decimals display option
4. **04_placement.gms** - Options in different locations
5. **05_mhw4dx_pattern.gms** - Real GAMSLib pattern

## Usage

```bash
# Parse all option fixtures
for f in tests/fixtures/options/*.gms; do 
    python -m src.cli parse "$f"
done
```

## Expected Results

- **Success:** 5/5 fixtures parse successfully
- **Expected failures:** 0/5

See `expected_results.yaml` for detailed expectations.

## Status

- **Created:** Sprint 8
- **Fixtures:** 5/5 ✓
- **Coverage:**
  - ✅ Single integer options
  - ✅ Multiple options (comma-separated)
  - ✅ decimals option type
  - ✅ Flexible placement
  - ✅ mhw4dx.gms pattern

## Notes

Option statements are implemented using mock/skip approach (store values, no semantic effects). Sprint 8 unlocks mhw4dx.gms (+10% parse rate).
```

---

### Template 2: Indexed Assignment Fixtures README

```markdown
# Indexed Assignment Fixtures

This directory contains test fixtures for GAMS indexed assignment features.

## Purpose

These fixtures test the parser's ability to handle indexed parameter assignments and variable attribute access (Sprint 8 scope: patterns 1-4 from Task 7 research).

## Fixture Structure

Each fixture consists of:
- `*.gms` - Input GAMS file with specific indexed assignment pattern
- `expected_results.yaml` - Expected parsing results

## Coverage

Target: 5 indexed assignment fixtures covering:
- Simple 1D indexed assignment (`p('i1') = 10`)
- Multi-dimensional 2D/3D (`report('global','x1') = 1.0`)
- Variable attribute access (`xdiff = x1.l`)
- Indexed expressions on RHS (`data('diff') = data('global') - data('solver')`)
- Error handling (index count mismatch)

## Fixture List

1. **01_simple_1d.gms** - Basic 1D indexed assignment
2. **02_multi_dim_2d.gms** - 2D indexed assignment (mathopt1 pattern)
3. **03_variable_attributes.gms** - Variable .l attribute access (trig pattern)
4. **04_indexed_expressions.gms** - Indexed params in expressions
5. **05_error_index_mismatch.gms** - Index count validation (expected to fail)

## Usage

```bash
# Parse all indexed assignment fixtures
for f in tests/fixtures/indexed_assign/*.gms; do 
    python -m src.cli parse "$f"
done
```

## Expected Results

- **Success:** 4/5 fixtures parse successfully
- **Expected failures:** 1/5 (fixture 05 - index count mismatch)

See `expected_results.yaml` for detailed expectations.

## Status

- **Created:** Sprint 8
- **Fixtures:** 5/5 ✓
- **Coverage:**
  - ✅ 1D indexed assignments
  - ✅ 2D multi-dimensional assignments
  - ✅ Variable attributes (.l)
  - ✅ Indexed expressions on RHS
  - ✅ Index validation error handling

## Notes

Indexed assignments unlock mathopt1.gms + trig.gms (+20% parse rate). Covers all 4 GAMS patterns identified in Task 7 research.
```

---

### Template 3: Partial Parse Fixtures README

```markdown
# Partial Parse Metric Fixtures

This directory contains test fixtures for partial parse metric calculation and missing feature extraction.

## Purpose

These fixtures test the parser's ability to calculate parse percentage and identify missing features for models that partially parse.

## Fixture Structure

Each fixture consists of:
- `*.gms` - Input GAMS file with known partial parse scenario
- `expected_results.yaml` - Expected parse percentage and missing features

## Coverage

Target: 3 partial parse fixtures covering:
- Partial parse with lead/lag indexing error (himmel16 pattern)
- Partial parse with function call error (circle pattern)
- Complete success baseline (100% parse)

## Fixture List

1. **01_himmel16_pattern.gms** - Partial parse ~80% (i++1 indexing missing)
2. **02_circle_pattern.gms** - Partial parse ~70% (function calls missing)
3. **03_complete_success.gms** - 100% parse baseline

## Usage

```bash
# Parse all partial parse fixtures with metrics
for f in tests/fixtures/partial_parse/*.gms; do 
    python -m src.cli parse "$f" --show-metrics
done
```

## Expected Results

- **100% Parse:** 1/3 (fixture 03)
- **Partial Parse:** 2/3 (fixtures 01, 02)

See `expected_results.yaml` for detailed expectations.

## Status

- **Created:** Sprint 8
- **Fixtures:** 3/3 ✓
- **Coverage:**
  - ✅ Partial parse with lead/lag indexing
  - ✅ Partial parse with function calls
  - ✅ 100% parse baseline

## Notes

Partial parse metrics enable tracking incremental progress toward 100% parse rate. Dashboard will display: "himmel16: 85% parsed, needs [i++1 indexing]".
```

---

## Implementation Plan

### Phase 1: Directory Creation (15 minutes)

```bash
# Create 3 new fixture directories
mkdir -p tests/fixtures/options
mkdir -p tests/fixtures/indexed_assign
mkdir -p tests/fixtures/partial_parse
```

---

### Phase 2: Option Fixtures (1 hour)

**Tasks:**
1. Create 5 `.gms` files (15 min)
2. Create `expected_results.yaml` (20 min)
3. Create `README.md` (15 min)
4. Verify YAML validity (10 min)

---

### Phase 3: Indexed Assignment Fixtures (1.5 hours)

**Tasks:**
1. Create 5 `.gms` files (20 min)
2. Create `expected_results.yaml` with new fields (30 min)
3. Create `README.md` (20 min)
4. Verify patterns match Task 7 research (20 min)

---

### Phase 4: Partial Parse Fixtures (45 minutes)

**Tasks:**
1. Create 3 `.gms` files (15 min)
2. Create `expected_results.yaml` with partial parse fields (15 min)
3. Create `README.md` (10 min)
4. Validate parse percentage calculation logic (5 min)

---

### Phase 5: Documentation & Verification (30 minutes)

**Tasks:**
1. Update this TEST_FIXTURE_STRATEGY.md (10 min)
2. Verify all cross-references (10 min)
3. Check backward compatibility with Sprint 7 (10 min)

---

### Total Effort Estimate

- Phase 1: 15 minutes
- Phase 2: 1 hour
- Phase 3: 1.5 hours
- Phase 4: 45 minutes
- Phase 5: 30 minutes
- **Total: ~4 hours** for fixture creation

**Note:** This estimate is for fixture **creation** during Sprint 8 Days 1-3, not for this prep task (which only designs the strategy).

---

## Summary

**Sprint 8 Test Fixtures:**
- **Total:** 13 fixtures (5 option + 5 indexed + 3 partial)
- **Expected Success:** 10/13 (77% success rate)
- **Expected Failures:** 1/13 (fixture: indexed_assign/05 - validation)
- **Expected Partial:** 2/13 (fixtures: partial_parse/01, partial_parse/02)

**Sprint 7 Pattern Reuse:**
- ✅ Directory structure: Fully reusable
- ✅ YAML format: Extends Sprint 7 schema (backward compatible)
- ✅ README template: Fully reusable

**Coverage:**
- ✅ Option statements: 100% (5 fixtures, 3 option types, placement flexibility)
- ✅ Indexed assignments: 100% (5 fixtures, 4 GAMS patterns + error handling)
- ✅ Partial parse metrics: 100% (3 fixtures, 2 partial scenarios + baseline)

**Fixture Creation Effort:** 3.5 hours during Sprint 8 implementation

**Backward Compatibility:** ✅ Yes (all Sprint 7 fixtures remain valid)
