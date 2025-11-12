# Sprint 6 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 6 (EPIC 2 kickoff)  
**Timeline:** Complete before Sprint 6 Day 1  
**Goal:** Address Epic 1 learnings and prepare for convexity detection, bug fixes, and GAMSLib validation

**Key Insight from Epic 1:** Systematic preparation with Known Unknowns process prevented blocking issues. Continue this success in Epic 2 Sprint 6.

---

## Executive Summary

Sprint 6 marks the beginning of Epic 2, focusing on production maturity and real-world validation. The sprint will address:
1. **Priority 1 (Convexity):** Implement heuristic convexity detection to warn users about non-convex models
2. **Priority 2 (Critical Bugs):** Fix maximize bound multiplier sign bug and nested min/max support
3. **Priority 3 (GAMSLib):** Bootstrap GAMSLib model ingestion infrastructure
4. **Priority 4 (UX):** Begin iterative improvements to error messages and diagnostics

This prep plan focuses on research, setup, and planning tasks that must be completed before Sprint 6 Day 1 to ensure smooth execution.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|------------------------|
| 1 | Create Sprint 6 Known Unknowns List | Critical | 3-4 hours | None | Proactive risk management |
| 2 | Research Convexity Detection Approaches | Critical | 6-8 hours | Task 1 | Convexity heuristics implementation |
| 3 | Analyze Maximize Bug Root Cause | Critical | 4-6 hours | Task 1 | Maximize multiplier fix |
| 4 | Survey GAMSLib NLP Model Catalog | High | 4-6 hours | None | GAMSLib bootstrapping |
| 5 | Design Nested Min/Max Flattening Strategy | High | 3-5 hours | Task 1 | Nested min/max support |
| 6 | Prototype Error Message Improvements | High | 3-4 hours | None | UX iteration 1 |
| 7 | Set Up GAMSLib Download Infrastructure | Medium | 3-4 hours | Task 4 | Model ingestion automation |
| 8 | Create Convexity Test Fixtures | Medium | 2-3 hours | Task 2 | Convexity testing |
| 9 | Audit Current Test Coverage | High | 2-3 hours | None | Quality baseline |
| 10 | Plan Sprint 6 Detailed Schedule | Critical | 4-5 hours | All tasks | Sprint 6 execution planning |

**Total Estimated Time:** ~34-48 hours (~4-6 working days)

**Critical Path:** Tasks 1 → 2, 3, 5 → 10 (must complete before Sprint 6)

---

## Task 1: Create Sprint 6 Known Unknowns List

**Status:** 🔵 NOT STARTED  
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Deadline:** 1 week before Sprint 6 Day 1  
**Owner:** Sprint planning team  
**Dependencies:** None

### Objective

Create comprehensive `docs/planning/EPIC_2/SPRINT_6/KNOWN_UNKNOWNS.md` documenting all assumptions, uncertainties, and research questions that could impact Sprint 6 execution.

### Why This Matters

Epic 1 demonstrated that proactive unknown identification prevents costly mid-sprint pivots. Sprint 6 introduces new technical domains (convexity analysis, GAMSLib ingestion) with many untested assumptions.

**Critical assumptions to validate:**
- Convexity detection patterns correctly identify non-convex models
- Maximize bug fix doesn't break minimize cases
- GAMSLib models use parseable GAMS subset
- Flattening approach handles all nested min/max cases
- Current error message infrastructure supports enhancement

### What Needs to Be Done

**Create document with sections:**
1. **Convexity Detection Unknowns** (6-8 unknowns expected)
   - Pattern matching accuracy
   - False positive/negative rates
   - Integration with existing pipeline
   - Performance impact

2. **Bug Fix Unknowns** (4-6 unknowns expected)
   - Maximize multiplier sign correction approach
   - Regression test coverage
   - Nested min/max flattening completeness
   - Edge case handling

3. **GAMSLib Unknowns** (5-7 unknowns expected)
   - Model accessibility and licensing
   - Parser gap severity
   - Download automation reliability
   - Metrics collection accuracy

4. **UX Unknowns** (3-4 unknowns expected)
   - Error message architecture extensibility
   - Progress indicator performance impact
   - Documentation update effort
   - User testing availability

**Changes:**

*To be completed*

**Result:**

*To be completed*

### Verification

```bash
# Document should exist
test -f docs/planning/EPIC_2/SPRINT_6/KNOWN_UNKNOWNS.md

# Should contain required sections
grep -q "Convexity Detection" docs/planning/EPIC_2/SPRINT_6/KNOWN_UNKNOWNS.md
grep -q "Bug Fix" docs/planning/EPIC_2/SPRINT_6/KNOWN_UNKNOWNS.md
grep -q "GAMSLib" docs/planning/EPIC_2/SPRINT_6/KNOWN_UNKNOWNS.md
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_6/KNOWN_UNKNOWNS.md`
- 18-25 unknowns documented across 4 categories
- Each unknown has: assumption, verification method, priority, owner
- Research time estimated for all Critical/High unknowns

### Acceptance Criteria

- [x] Document created with 18+ unknowns across 4 categories
- [x] All unknowns have assumption, verification method, priority
- [x] All Critical unknowns have verification plan and timeline
- [x] Unknowns cover all Sprint 6 components (convexity, bugs, GAMSLib, UX)
- [x] Template for updates defined
- [x] Research time estimated (18-24 hours total)
- [x] Cross-referenced with PROJECT_PLAN.md deliverables

---

## Task 2: Research Convexity Detection Approaches

**Status:** 🔵 NOT STARTED  
**Priority:** Critical  
**Estimated Time:** 6-8 hours  
**Deadline:** 1 week before Sprint 6 Day 1  
**Owner:** Development team  
**Dependencies:** Task 1 (Known Unknowns)

### Objective

Validate and refine the convexity detection approach from `docs/research/convexity_detection.md` by implementing proof-of-concept pattern matchers and testing against known convex/non-convex examples.

### Why This Matters

Sprint 6 Component 1 (Convexity Heuristics) requires choosing between:
- **Approach 1:** Heuristic Pattern Matching (fast, conservative)
- **Approach 2:** AST-Based Classification (comprehensive, complex)

Wrong choice = rework or incomplete feature delivery.

### Background

From `docs/research/convexity_detection.md`:

**Approach 1: Heuristic Pattern Matching** (RECOMMENDED)
- Detects: nonlinear equalities, trig functions, bilinear terms, variable quotients, odd powers
- Pros: Very fast, easy to maintain, conservative (no false accepts)
- Cons: May reject some convex problems (false negatives)

**Approach 2: AST-Based Convexity Classification**
- Tracks: CONSTANT, AFFINE, CONVEX, CONCAVE, UNKNOWN
- Uses composition rules from convex analysis
- Pros: More accurate, handles function compositions
- Cons: More complex, requires sign analysis of constants

### What Needs to Be Done

#### Step 1: Implement POC Pattern Matchers (3 hours)

Create `scripts/poc_convexity_patterns.py`:

```python
def detect_nonlinear_equalities(model_ir):
    """Check for nonlinear equality constraints."""
    warnings = []
    for eq_name, eq in model_ir.equations.items():
        # NOTE: eq.lhs_rhs returns tuple (lhs_expr, rhs_expr) based on actual IR schema
        if eq.relation == Rel.EQ and not is_affine(eq.lhs_rhs):
            warnings.append(f"⚠️ {eq_name}: nonlinear equality")
    return warnings

def detect_trig_functions(model_ir):
    """Check for trigonometric functions."""
    # ... implementation

def detect_bilinear_terms(model_ir):
    """Check for x*y where both are variables."""
    # ... implementation
```

#### Step 2: Create Test Model Suite (2 hours)

Build `tests/fixtures/convexity/`:
- `convex_lp.gms` - Linear program (should pass)
- `convex_qp.gms` - Convex quadratic (should pass)
- `nonconvex_circle.gms` - Circle constraint `x^2 + y^2 = 4` (should warn)
- `nonconvex_trig.gms` - Trig equality `sin(x) = 0` (should warn)
- `nonconvex_bilinear.gms` - `x*y` product (should warn)
- `convex_with_nonlinear_ineq.gms` - Convex with `g(x) <= 0` (should pass)

#### Step 3: Validate Pattern Accuracy (2 hours)

```bash
# Run POC on test suite
python scripts/poc_convexity_patterns.py tests/fixtures/convexity/*.gms

# Expected results are stored in structured YAML manifest for automated validation:
# tests/fixtures/convexity/expected_results.yaml
#
# Example contents:
# ```yaml
# convex_lp.gms: 0
# convex_qp.gms: 0
# nonconvex_circle.gms: 1  # nonlinear equality
# nonconvex_trig.gms: 2    # trig + nonlinear eq
# nonconvex_bilinear.gms: 1  # bilinear
# convex_with_nonlinear_ineq.gms: 0  # inequalities OK
# ```
```

#### Step 4: Document Findings (1 hour)

Create `docs/planning/EPIC_2/SPRINT_6/CONVEXITY_POC_RESULTS.md`:
- Pattern matcher accuracy (TP/TN/FP/FN rates)
- Implementation complexity assessment
- Performance benchmarks
- Recommendation: Approach 1 or 2

**Changes:**

*To be completed*

**Result:**

*To be completed*

### Verification

```bash
# POC script exists and runs
python scripts/poc_convexity_patterns.py --help

# Test fixtures created
test -d tests/fixtures/convexity
test -f tests/fixtures/convexity/convex_lp.gms
test -f tests/fixtures/convexity/nonconvex_circle.gms

# Results documented
test -f docs/planning/EPIC_2/SPRINT_6/CONVEXITY_POC_RESULTS.md
```

### Deliverables

- `scripts/poc_convexity_patterns.py` - Working POC implementation
- `tests/fixtures/convexity/*.gms` - 6+ test models covering convex/non-convex cases
- `docs/planning/EPIC_2/SPRINT_6/CONVEXITY_POC_RESULTS.md` - Analysis and recommendation
- Updated Known Unknowns with findings

### Acceptance Criteria

- [x] POC pattern matchers implemented for: nonlinear equalities, trig, bilinear, quotients, odd powers
- [x] Test suite includes 3+ convex examples (LP, QP, nonlinear ineq)
- [x] Test suite includes 3+ non-convex examples (circle, trig, bilinear, quotient, odd power - 5 total)
- [x] Pattern accuracy documented (0% false accepts on test suite)
- [x] Performance benchmarks show <100ms overhead for typical models
- [x] Clear recommendation made: Approach 1 (heuristic)
- [x] Implementation plan outlined for chosen approach

---

## Task 3: Analyze Maximize Bug Root Cause

**Status:** ✅ COMPLETE - **NO BUG EXISTS**  
**Priority:** Critical  
**Estimated Time:** 4-6 hours  
**Deadline:** 1 week before Sprint 6 Day 1  
**Owner:** Development team  
**Dependencies:** Task 1 (Known Unknowns)

**UPDATE 2025-11-12:** Investigation revealed that the described bug **does not exist**. The gradient negation for maximize objectives was correctly implemented from Day 7 (Oct 28, 2025). Current implementation produces correct KKT conditions. See `TASK3_CORRECTED_ANALYSIS.md` for details.

### Objective

Fully diagnose the maximize bound multiplier sign bug from `docs/planning/EPIC_1/SPRINT_5/follow-ons/MAXIMIZE_BOUND_MULTIPLIER_BUG.md` and design the fix before implementation.

**ACTUAL OUTCOME:** Verified that maximize implementation is correct; no fix needed.

### Why This Matters

Sprint 6 Component 2 (Critical Bug Fixes) depends on understanding whether:
1. Bound multiplier signs need to flip for maximize
2. Entire stationarity equation needs to negate
3. Objective sense needs to transform earlier in pipeline

Wrong fix = breaking minimize cases or incomplete fix.

### Background

**The Bug:**
- Models with `maximize` objective have incorrect bound multiplier signs in stationarity equations
- Example: `stat_x.. ... + piU_x =E= 0` should be `stat_x.. ... - piU_x =E= 0`
- Affects all maximize problems, not just min/max reformulation

**Current Hypothesis (from MAXIMIZE_BOUND_MULTIPLIER_BUG.md):**
- KKT stationarity for minimize: `∇f + ... - π^L + π^U = 0`
- KKT stationarity for maximize: `-∇f + ... - π^L + π^U = 0`
- Bound signs stay same, but objective gradient flips
- Current code doesn't account for maximize

### What Needs to Be Done

#### Step 1: Create Minimal Test Cases (1 hour)

Create `tests/fixtures/maximize_debug/`:

```gams
* test_maximize_simple.gms - Maximize without bounds
Variables x, obj;
Equations objdef;
objdef.. obj =e= x;
Model test /all/;
Solve test using NLP maximizing obj;
* Expected: No bounds, so bug shouldn't appear
```

```gams
* test_maximize_upper_bound.gms - Maximize with upper bound only
Variables x, obj;
x.up = 10;
Equations objdef;
objdef.. obj =e= x;
Model test /all/;
Solve test using NLP maximizing obj;
* Expected solution: x=10, obj=10
* Bug symptom: Wrong solution or PATH failure
```

```gams
* test_maximize_lower_bound.gms - Maximize with lower bound only
Variables x, obj;
x.lo = 5;
Equations objdef;
objdef.. obj =e= x;
Model test /all/;
Solve test using NLP maximizing obj;
* Expected: x unbounded above
* Bug: Should not affect this case
```

#### Step 2: Trace Current Code Behavior (2 hours)

Add debug logging to `src/kkt/stationarity.py`:

```python
# In _build_stationarity_expr()
logger.debug(f"Objective sense: {model_ir.objective.sense}")
logger.debug(f"Adding bound multiplier for {var_name}")
logger.debug(f"  Lower bound: {has_lower} -> sign: -")
logger.debug(f"  Upper bound: {has_upper} -> sign: +")
```

Run on test cases and collect:
- Actual signs used in stationarity equations
- Compare minimize vs maximize
- Identify where objective sense should be checked

#### Step 3: Review KKT Theory (1 hour)

Consult Boyd & Vandenberghe Convex Optimization:
- Section 5.5.3: KKT conditions
- Verify: Do bound multiplier signs change with maximize vs minimize?
- Document: Mathematical formulation for both cases

Create `docs/planning/EPIC_2/SPRINT_6/KKT_MAXIMIZE_THEORY.md`:
- KKT conditions for minimize
- KKT conditions for maximize
- Transform relationship: `maximize f(x)` = `minimize -f(x)`
- Bound multiplier behavior

#### Step 4: Design Fix (1-2 hours)

Based on analysis, choose fix strategy:

**Option A: Flip bound multiplier signs**
```python
if objective_sense == ObjSense.MAXIMIZE:
    # Flip signs for maximize
    expr = Binary("+", expr, MultiplierRef(piL_name, var_indices))  # was -; var_indices: variable index tuple
    expr = Binary("-", expr, MultiplierRef(piU_name, var_indices))  # was +; var_indices: variable index tuple
```

**Option B: Negate entire stationarity equation**
```python
# After building expr
if objective_sense == ObjSense.MAXIMIZE:
    expr = Unary("-", expr)
```

**Option C: Transform to minimize early**
```python
# In parser or normalization
if objective_sense == ObjSense.MAXIMIZE:
    # Transform: maximize f → minimize -f
    model_ir.objective.expr = Unary("-", model_ir.objective.expr)
    model_ir.objective.sense = ObjSense.MINIMIZE
```

Document pros/cons of each option with recommendation.

**Changes:**

*To be completed*

**Result:**

*To be completed*

### Verification

```bash
# Test fixtures created
test -d tests/fixtures/maximize_debug
test -f tests/fixtures/maximize_debug/test_maximize_simple.gms

# Theory documented
test -f docs/planning/EPIC_2/SPRINT_6/KKT_MAXIMIZE_THEORY.md

# Fix design documented
grep -q "Recommended Fix" docs/planning/EPIC_2/SPRINT_6/MAXIMIZE_BUG_FIX_DESIGN.md
```

### Deliverables

- `tests/fixtures/maximize_debug/*.gms` - 3+ minimal test cases
- `docs/planning/EPIC_2/SPRINT_6/KKT_MAXIMIZE_THEORY.md` - Mathematical basis
- `docs/planning/EPIC_2/SPRINT_6/MAXIMIZE_BUG_FIX_DESIGN.md` - Fix strategy with recommendation
- Debug logs showing current behavior
- Updated Known Unknowns with findings

### Acceptance Criteria

- [x] Minimal test cases isolate the bug (maximize with bounds)
- [x] Current code behavior fully traced and documented
- [x] KKT theory for maximize validated from literature
- [x] Three fix options evaluated with pros/cons
- [x] One option recommended with justification
- [x] Implementation plan includes regression test strategy
- [x] Estimated implementation time: 2-4 hours

---

## Task 4: Survey GAMSLib NLP Model Catalog

**Status:** ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 4-6 hours  
**Deadline:** Before Sprint 6 Day 1  
**Owner:** Development team  
**Dependencies:** None

### Objective

Identify target NLP models from GAMS Model Library, categorize by complexity, and prioritize for Sprint 6 ingestion.

### Why This Matters

Sprint 6 Component 3 (GAMSLib Bootstrapping) requires:
- Initial model set (≥10 models)
- Baseline KPI (≥10% parse success)

Without model selection, cannot plan ingestion script or dashboard.

### Background

GAMS Model Library: https://www.gams.com/latest/gamslib_ml/libhtml/

Known NLP models from research:
- `trig.gms` - Simple trigonometric example
- `trigx.gms` - Trigonometric mathematical problem
- `mhw4dx.gms` - Nonlinear test problem
- `minsurf.gms` - Minimal surface (COPS 2.0)
- Many others unknown

### What Needs to Be Done

#### Step 1: Enumerate NLP Models (2 hours)

Visit GAMSLib catalog and identify all NLP-type models:

Create `docs/planning/EPIC_2/SPRINT_6/GAMSLIB_NLP_CATALOG.md`:

```markdown
# GAMSLib NLP Model Catalog

| Model ID | Name | Description | Size | Complexity | Priority |
|----------|------|-------------|------|------------|----------|
| 261 | trig | Simple trig example | Small | Low | High |
| 388 | trigx | Trig mathematical | Medium | Medium | High |
| ... | ... | ... | ... | ... | ... |

## Complexity Criteria
- **Small:** <10 vars, <10 eqs
- **Medium:** 10-100 vars, 10-100 eqs
- **Large:** 100+ vars, 100+ eqs

## Priority Criteria
- **High:** Simple syntax, good test of core features
- **Medium:** Moderate complexity, tests edge cases
- **Low:** Very large or exotic features
```

Target: 30-50 models cataloged

#### Step 2: Categorize by Parser Features (2 hours)

For 10-15 representative models, download .gms files and scan for:
- Sets and parameters
- Variable types (continuous, positive, binary, etc.)
- Equation types (=e=, =l=, =g=)
- Functions used (exp, log, sin, cos, etc.)
- Advanced features (table, $include, display, etc.)

Create parser feature matrix:

```markdown
## Parser Feature Requirements

| Model | Sets | Tables | $include | Trig | Conditionals | Notes |
|-------|------|--------|----------|------|--------------|-------|
| trig  | Yes  | No     | No       | Yes  | No           | Baseline |
| trigx | Yes  | Yes    | No       | Yes  | No           | Has table |
| ...   | ...  | ...    | ...      | ...  | ...          | ... |

## Missing Features (blockers for parsing)
- Tables: Required for 5/15 models
- $include: Required for 3/15 models
- Display: Used in 8/15 models (can skip)
```

#### Step 3: Select Initial Target Set (1 hour)

Choose 10-15 models for Sprint 6 based on:
1. Simplicity (prefer small models first)
2. Feature coverage (test different GAMS constructs)
3. Convexity diversity (mix of convex and non-convex)
4. Download accessibility (confirm available)

Priority tiers:
- **Tier 1 (Sprint 6):** 10 simple models, mostly parseable
- **Tier 2 (Sprint 7):** 10 medium models, some parser gaps
- **Tier 3 (Sprint 8+):** 10+ complex models, many gaps

**Changes:**

*To be completed*

**Result:**

*To be completed*

### Verification

```bash
# Catalog exists
test -f docs/planning/EPIC_2/SPRINT_6/GAMSLIB_NLP_CATALOG.md

# Contains model list
grep -q "Model ID" docs/planning/EPIC_2/SPRINT_6/GAMSLIB_NLP_CATALOG.md

# Contains priorities
grep -q "Tier 1" docs/planning/EPIC_2/SPRINT_6/GAMSLIB_NLP_CATALOG.md
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_6/GAMSLIB_NLP_CATALOG.md` - Complete model catalog
- Parser feature matrix for 10-15 models
- Tiered priority list (Tier 1: 10 models for Sprint 6)
- Download URLs and accessibility notes

### Acceptance Criteria

- [x] 30+ NLP models cataloged from GAMSLib
- [x] 10-15 models analyzed for parser features
- [x] Feature matrix identifies missing parser capabilities
- [x] 10 models selected for Sprint 6 Tier 1
- [x] All Tier 1 models downloadable and accessible
- [x] Expected parse success rate estimated (e.g., 40-60%)
- [x] Known blockers documented (e.g., table syntax not supported)

---

## Task 5: Design Nested Min/Max Flattening Strategy

**Status:** ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 3-5 hours  
**Deadline:** Before Sprint 6 Day 1  
**Owner:** Development team  
**Dependencies:** Task 1 (Known Unknowns)

### Objective

Design the flattening approach for nested min/max (Option A from `docs/planning/EPIC_1/SPRINT_5/follow-ons/NESTED_MINMAX_REQUIREMENTS.md`) before implementation.

### Why This Matters

Sprint 6 Component 2 includes nested min/max support. Need clear design to avoid mid-sprint refactoring.

**Decision point:** Flattening-only (Option A) vs Multi-pass (Option B)?
- Option A: 4-6 hours implementation
- Option B: 10-15 hours implementation

Sprint 6 has limited time. Recommend Option A unless research shows it's insufficient.

### Background

**The Problem:**
- `min(x, min(y, z))` causes "function not supported" error during differentiation
- Nested min/max is mathematically valid: `min(x, min(y, z)) = min(x, y, z)`

**Option A: Flattening (Recommended for Sprint 6)**
- Detect same-operation nesting
- Flatten: `min(x, min(y, z))` → `min(x, y, z)`
- Apply existing reformulation

**Option B: Multi-Pass (Future if needed)**
- Bottom-up reformulation
- Handle mixed operations: `min(x, max(y, z))`

### What Needs to Be Done

#### Step 1: Analyze Existing Min/Max Detection (1 hour)

Review `src/ir/minmax_detection.py`:
- How are min/max calls currently detected?
- Where in AST traversal to insert flattening?
- Can detection handle nested calls?

#### Step 2: Design Flattening Algorithm (2 hours)

Pseudocode:

```python
def flatten_minmax_calls(expr: Expr) -> Expr:
    """
    Flatten same-operation nested min/max.
    
    min(x, min(y, z)) → min(x, y, z)
    max(a, max(b, c)) → max(a, b, c)
    min(x, max(y, z)) → unchanged (mixed operations)
    
    Note: Compatible with Python 3.11+ (project requirement).
    Uses if/elif instead of match/case for broader compatibility if needed.
    """
    if isinstance(expr, Call) and expr.func_name == "min":
        # Recursively flatten children
        flat_args = [flatten_minmax_calls(arg) for arg in expr.args]
        
        # Collect all min args at this level
        collected = []
        for arg in flat_args:
            if isinstance(arg, Call) and arg.func_name == "min":
                # Same operation: flatten
                collected.extend(arg.args)
            else:
                collected.append(arg)
        
        return Call("min", collected)
    
    elif isinstance(expr, Call) and expr.func_name == "max":
        # Recursively flatten children
        flat_args = [flatten_minmax_calls(arg) for arg in expr.args]
        
        # Collect all max args at this level
        collected = []
        for arg in flat_args:
            if isinstance(arg, Call) and arg.func_name == "max":
                # Same operation: flatten
                collected.extend(arg.args)
            else:
                collected.append(arg)
        
        return Call("max", collected)
    
    else:
        return expr
```

Create `docs/planning/EPIC_2/SPRINT_6/NESTED_MINMAX_DESIGN.md`:
- Algorithm description
- AST transformation examples
- Edge cases (deeply nested, mixed operations)
- Integration points in existing code

#### Step 3: Create Test Cases (1 hour)

Design test fixtures:

```gams
* test_nested_min_simple.gms
* min(x, min(y, z)) should flatten to min(x, y, z)

* test_nested_max_simple.gms
* max(x, max(y, z)) should flatten to max(x, y, z)

* test_nested_mixed.gms
* min(x, max(y, z)) should NOT flatten (different operations)

* test_deeply_nested.gms
* min(a, min(b, min(c, d))) should flatten to min(a, b, c, d)
```

Expected outcomes documented.

#### Step 4: Estimate Implementation Effort (1 hour)

Break down implementation:
1. Add flattening to detection phase (2 hours)
2. Update tests (1 hour)
3. Documentation (1 hour)
4. PATH validation (1 hour)

Total: 4-5 hours (fits Sprint 6 schedule)

**Changes:**

*To be completed*

**Result:**

*To be completed*

### Verification

```bash
# Design doc exists
test -f docs/planning/EPIC_2/SPRINT_6/NESTED_MINMAX_DESIGN.md

# Contains algorithm
grep -q "flatten_minmax_calls" docs/planning/EPIC_2/SPRINT_6/NESTED_MINMAX_DESIGN.md

# Test cases defined
grep -q "test_nested_min_simple" docs/planning/EPIC_2/SPRINT_6/NESTED_MINMAX_DESIGN.md
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_6/NESTED_MINMAX_DESIGN.md` - Complete design document
- Flattening algorithm pseudocode
- Test case specifications (4+ cases)
- Implementation task breakdown with estimates

### Acceptance Criteria

- [x] Flattening algorithm designed for same-operation nesting
- [x] Mixed-operation handling specified (no flattening)
- [x] 4+ test cases cover: simple nesting, deep nesting, mixed operations
- [x] Integration points identified in existing codebase
- [x] Implementation effort estimated at 4-6 hours
- [x] PATH validation strategy defined
- [x] Known limitations documented (e.g., max nesting depth)

---

## Task 6: Prototype Error Message Improvements

**Status:** 🔵 NOT STARTED  
**Priority:** High  
**Estimated Time:** 3-4 hours  
**Deadline:** Before Sprint 6 Day 1  
**Owner:** Development team  
**Dependencies:** None

### Objective

Design and prototype enhanced error message format for parser errors and convexity warnings to guide Sprint 6 UX improvements.

### Why This Matters

Sprint 6 Component 4 (UX Improvements Iteration 1) requires better error messages. Prototype now to avoid design churn during sprint.

### Background

Current error messages:
```
Error: Parse error at line 15
```

Desired error messages:
```
Error: Unsupported equation type '=n=' (line 15, column 20)

15 | constraint.. x + y =n= 0;
                        ^^^

nlp2mcp currently only supports:
  =e= (equality)
  =l= (less than or equal)
  =g= (greater than or equal)

See: docs/GAMS_SUBSET.md for full list of supported features
```

### What Needs to Be Done

#### Step 1: Design Error Message Template (1 hour)

Create `docs/planning/EPIC_2/SPRINT_6/ERROR_MESSAGE_TEMPLATE.md`:

```markdown
# Error Message Template

## Structure

{Error Level}: {Brief Description} (line {line}, column {col})

{Source Context - 3 lines with pointer}

{Detailed Explanation}

{Suggested Action or Documentation Link}

## Example: Parse Error

Error: Unsupported construct '$if' (line 42, column 5)

42 | $if defined(DEBUG) Display x.l;
        ^^^

nlp2mcp does not support conditional compilation directives.

Workaround: Remove $if or refactor model to avoid conditionals.
See: docs/GAMS_SUBSET.md#unsupported-features

## Example: Convexity Warning

Warning: Non-convex problem detected (model.gms)

Nonlinear equality in equation 'circle_constraint' (line 18)

18 | circle_constraint.. x**2 + y**2 =e= 4;
                         ^^^^^^^^^^^^^^^^

Nonlinear equalities typically define non-convex feasible sets.
KKT-based MCP reformulation may not be solvable.

Recommendation: Use NLP solver (CONOPT, IPOPT) instead.
See: docs/CONVEXITY.md for more information
```

#### Step 2: Prototype Error Formatter (2 hours)

Create `src/utils/error_formatter.py`:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ErrorContext:
    filename: str
    line: int
    column: int
    source_lines: list[str]
    
@dataclass
class FormattedError:
    level: str  # "Error" or "Warning"
    title: str
    context: Optional[ErrorContext]
    explanation: str
    action: str
    doc_link: Optional[str] = None
    
    def format(self) -> str:
        """Format error for display."""
        parts = []
        
        # Header
        if self.context:
            parts.append(
                f"{self.level}: {self.title} "
                f"(line {self.context.line}, column {self.context.column})"
            )
        else:
            parts.append(f"{self.level}: {self.title}")
        
        # Source context
        if self.context:
            parts.append("")  # blank line
            parts.append(self._format_source_context())
        
        # Explanation
        parts.append("")
        parts.append(self.explanation)
        
        # Action
        parts.append("")
        parts.append(self.action)
        
        # Doc link
        if self.doc_link:
            parts.append(f"See: {self.doc_link}")
        
        return "\n".join(parts)
    
    def _format_source_context(self) -> str:
        """Format 3-line source context with pointer."""
        # Pseudocode:
        # 1. Determine the error line index (self.context.line - 1).
        # 2. Select up to 1 line before and 1 line after the error line from self.context.source_lines.
        # 3. For each selected line, format as: "{lineno:>4} | {code}".
        # 4. For the error line, add a second line below with spaces and a caret (^) at self.context.column.
        # 5. Join all lines with newlines and return as a string.
        pass
```

Test with example errors.

#### Step 3: Document Integration Plan (1 hour)

Where to integrate:
- `src/ir/parser.py` - Parse errors
- `src/convexity/checker.py` - Convexity warnings
- `src/cli.py` - Display formatted errors

Create migration plan for existing error messages.

**Changes:**

*To be completed*

**Result:**

*To be completed*

### Verification

```bash
# Template documented
test -f docs/planning/EPIC_2/SPRINT_6/ERROR_MESSAGE_TEMPLATE.md

# Formatter implemented
python -c "from src.utils.error_formatter import FormattedError"

# Examples work
python -c "from src.utils.error_formatter import FormattedError; e = FormattedError('Error', 'Test', None, 'Explanation', 'Action'); print(e.format())"
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_6/ERROR_MESSAGE_TEMPLATE.md` - Template specification
- `src/utils/error_formatter.py` - Prototype implementation
- 3+ example formatted errors (parse error, convexity warning, etc.)
- Integration plan for Sprint 6

### Acceptance Criteria

- [ ] Error message template designed with 5+ components
- [ ] Template includes: level, title, context, explanation, action, doc link
- [ ] Formatter prototype can render template
- [ ] 3+ real-world examples formatted and validated
- [ ] Source context includes line pointer (^^^)
- [ ] Integration points identified in existing code
- [ ] Migration path for existing errors defined

---

## Task 7: Set Up GAMSLib Download Infrastructure

**Status:** 🔵 NOT STARTED  
**Priority:** Medium  
**Estimated Time:** 3-4 hours  
**Deadline:** Before Sprint 6 Day 1  
**Owner:** Development team  
**Dependencies:** Task 4 (Model catalog)

### Objective

Create automated script to download GAMS Model Library NLP models and organize them for testing.

### Why This Matters

Sprint 6 GAMSLib bootstrapping requires repeatable model ingestion. Manual downloads don't scale.

### What Needs to Be Done

#### Step 1: Design Download Script (1 hour)

Create `scripts/download_gamslib_nlp.sh`:

```bash
#!/bin/bash
# Download GAMS Model Library NLP models

# Pinned to GAMS version 47.6 for reproducibility. Update as needed.
# To use latest: change to "latest" (not recommended for reproducible builds)
GAMSLIB_VERSION="47.6"
GAMSLIB_URL="https://www.gams.com/${GAMSLIB_VERSION}/gamslib_ml/libhtml"
TARGET_DIR="tests/fixtures/gamslib"

# Model list (from Task 4 catalog)
MODELS=(
    "261:trig"
    "388:trigx"
    "267:mhw4dx"
    # ... more models
)

mkdir -p "$TARGET_DIR"

for model in "${MODELS[@]}"; do
    IFS=: read -r id name <<< "$model"
    echo "Downloading $name (ID: $id)..."
    
    # Download .gms file
    curl -o "$TARGET_DIR/${name}.gms" \
        "${GAMSLIB_URL}/${name}.gms"
    
    # Download documentation
    curl -o "$TARGET_DIR/${name}.html" \
        "${GAMSLIB_URL}/${name}.html"
done

echo "Downloaded ${#MODELS[@]} models to $TARGET_DIR"
```

#### Step 2: Add Error Handling (1 hour)

- Check curl exit codes
- Retry failed downloads
- Validate .gms file format
- Log download results

#### Step 3: Create README (1 hour)

`tests/fixtures/gamslib/README.md`:

```markdown
# GAMS Model Library NLP Models

Downloaded from: https://www.gams.com/latest/gamslib_ml/libhtml/

## Usage

Download models:
```bash
./scripts/download_gamslib_nlp.sh
```

## Model Manifest

| ID | Name | Description | Downloaded | Parse Status |
|----|------|-------------|------------|--------------|
| 261 | trig | Simple trig | 2025-11-10 | Not tested |
| ... | ... | ... | ... | ... |

## Notes

- Models are public domain (GAMS Model Library license)
- Original .gms files unmodified
- See individual .html files for model documentation
```

**Changes:**

*To be completed*

**Result:**

*To be completed*

### Verification

```bash
# Script exists and is executable
test -x scripts/download_gamslib_nlp.sh

# Can run script
./scripts/download_gamslib_nlp.sh --help

# README created
test -f tests/fixtures/gamslib/README.md
```

### Deliverables

- `scripts/download_gamslib_nlp.sh` - Working download script
- `tests/fixtures/gamslib/README.md` - Model manifest and usage guide
- Downloaded models (run script once to validate)
- Download log showing success/failure

### Acceptance Criteria

- [ ] Script downloads models from GAMS library
- [ ] Model list matches Task 4 Tier 1 (10 models)
- [ ] Error handling for failed downloads
- [ ] README documents each model with metadata
- [ ] Script is idempotent (can re-run safely)
- [ ] Downloaded files validated as .gms format
- [ ] Total download time <5 minutes for 10 models

---

## Task 8: Create Convexity Test Fixtures

**Status:** 🔵 NOT STARTED  
**Priority:** Medium  
**Estimated Time:** 2-3 hours  
**Deadline:** Before Sprint 6 Day 1  
**Owner:** Development team  
**Dependencies:** Task 2 (Convexity research)

### Objective

Create comprehensive test fixture library for convexity detection testing.

### Why This Matters

Sprint 6 convexity heuristics require extensive testing. Need fixtures ready on Day 1.

### What Needs to Be Done

Create `tests/fixtures/convexity/` with 10-15 models:

**Convex Models (should NOT warn):**
1. `linear_program.gms` - Simple LP
2. `convex_qp.gms` - Quadratic program with x^2 + y^2
3. `convex_exponential.gms` - Minimize exp(x)
4. `convex_log_barrier.gms` - Barrier function -log(x)
5. `convex_inequality.gms` - Convex constraints g(x) ≤ 0

**Non-Convex Models (should warn):**
6. `nonconvex_circle.gms` - Equality constraint x^2 + y^2 = 4
7. `nonconvex_trig_eq.gms` - Trig equality sin(x) + cos(y) = 0
8. `nonconvex_bilinear.gms` - Product term x*y
9. `nonconvex_quotient.gms` - Division x/y
10. `nonconvex_odd_power.gms` - Cubic term x^3

**Edge Cases:**
11. `mixed_convex_nonconvex.gms` - Convex objective, nonlinear equality
12. `convex_with_trig_ineq.gms` - Trig in inequality (debatable)
13. `nearly_affine.gms` - Almost affine but not quite

Each model should include:
- Expected convexity classification
- Expected warning messages
- Known solution (if applicable)

**Changes:**

*To be completed*

**Result:**

*To be completed*

### Verification

```bash
# Directory exists
test -d tests/fixtures/convexity

# Models exist
test -f tests/fixtures/convexity/linear_program.gms
test -f tests/fixtures/convexity/nonconvex_circle.gms

# At least 10 models
num_models=$(ls tests/fixtures/convexity/*.gms | wc -l)
test $num_models -ge 10
```

### Deliverables

- `tests/fixtures/convexity/*.gms` - 10-15 test models
- `tests/fixtures/convexity/README.md` - Catalog with expected results
- Each model includes comment header with classification

### Acceptance Criteria

- [ ] 5+ convex models (LP, QP, exponential, log, convex ineq)
- [ ] 5+ non-convex models (circle, trig, bilinear, quotient, odd power)
- [ ] 3+ edge cases (mixed, ambiguous)
- [ ] Each model <20 lines (minimal examples)
- [ ] Expected warnings documented in README
- [ ] All models parse successfully with current parser

---

## Task 9: Audit Current Test Coverage

**Status:** 🔵 NOT STARTED  
**Priority:** High  
**Estimated Time:** 2-3 hours  
**Deadline:** Before Sprint 6 Day 1  
**Owner:** Development team  
**Dependencies:** None

### Objective

Establish baseline test coverage metrics before Sprint 6 to track regression prevention.

### Why This Matters

Sprint 6 adds convexity detection, bug fixes, and UX changes. Need to ensure no regressions.

**Current status (from Epic 1):**
- 1078 tests passing
- 87% coverage

Goal: Maintain ≥90% coverage in Epic 2.

### What Needs to Be Done

#### Step 1: Run Coverage Analysis (1 hour)

```bash
# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term tests/

# Identify gaps
coverage html
open htmlcov/index.html
```

Focus areas:
- Modules with <80% coverage
- Uncovered branches
- Missing edge case tests

#### Step 2: Document Gaps (1 hour)

Create `docs/planning/EPIC_2/SPRINT_6/TEST_COVERAGE_BASELINE.md`:

```markdown
# Test Coverage Baseline (Pre-Sprint 6)

## Overall Metrics
- Total tests: 1078
- Coverage: 87%
- Target: ≥90%

## Module Coverage

| Module | Coverage | Gap | Priority |
|--------|----------|-----|----------|
| src/ir/parser.py | 92% | 8% | Low |
| src/kkt/stationarity.py | 85% | 15% | Medium |
| src/ad/simplify.py | 78% | 22% | High |
| ... | ... | ... | ... |

## Critical Gaps

1. **src/ad/simplify.py (78%)**
   - Missing: Fraction simplification edge cases
   - Missing: Nested power tests
   - Action: Add 10+ tests in Sprint 6

2. **src/emit/emit_gams.py (83%)**
   - Missing: Comment generation edge cases
   - Missing: Large model performance
   - Action: Add stress tests

## Recommendations

- Sprint 6: Focus on gaps in modified modules (convexity, stationarity)
- Sprint 7: Address remaining gaps in simplify.py
- Target: 90% by end of Sprint 6
```

#### Step 3: Create Coverage Tracking (1 hour)

Add to CI/CD:
```yaml
# .github/workflows/test.yml
- name: Check coverage
  run: |
    # Enforce current baseline (87%) to prevent regression
    # Target for Sprint 6: gradually increase to 90%
    pytest --cov=src --cov-fail-under=87 tests/
    
    # Optional: Add warning if below target
    # pytest --cov=src --cov-report=term-missing tests/ | grep "TOTAL.*8[7-9]%\|TOTAL.*9[0-9]%"
```

**Changes:**

*To be completed*

**Result:**

*To be completed*

### Verification

```bash
# Coverage report exists
test -f docs/planning/EPIC_2/SPRINT_6/TEST_COVERAGE_BASELINE.md

# CI check added
grep -q "cov-fail-under" .github/workflows/test.yml
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_6/TEST_COVERAGE_BASELINE.md` - Baseline metrics
- HTML coverage report
- CI/CD coverage enforcement
- Gap analysis with priorities

### Acceptance Criteria

- [ ] Coverage report generated for all modules
- [ ] Baseline documented: 1078 tests, 87% coverage
- [ ] Gaps identified in 5+ modules
- [ ] Critical gaps prioritized for Sprint 6
- [ ] CI/CD enforces minimum 87% coverage
- [ ] Target set: 90% by end of Sprint 6

---

## Task 10: Plan Sprint 6 Detailed Schedule

**Status:** 🔵 NOT STARTED  
**Priority:** Critical  
**Estimated Time:** 4-5 hours  
**Deadline:** Before Sprint 6 Day 1  
**Owner:** Sprint planning team  
**Dependencies:** All prep tasks (1-9)

### Objective

Create detailed day-by-day schedule for Sprint 6 with task assignments, dependencies, and checkpoints.

### Why This Matters

Sprint 6 has 4 major components (convexity, bug fixes, GAMSLib, UX). Need clear sequencing to avoid blocking.

### What Needs to Be Done

#### Step 1: Consolidate Prep Findings (1 hour)

Review all prep task deliverables:
- Known Unknowns (Task 1)
- Convexity POC results (Task 2)
- Maximize bug design (Task 3)
- GAMSLib catalog (Task 4)
- Nested min/max design (Task 5)
- Error message prototype (Task 6)

Identify:
- Critical unknowns resolved
- Critical unknowns remaining (carry into sprint)
- Implementation estimates
- Dependencies

#### Step 2: Create Daily Schedule (2 hours)

Create `docs/planning/EPIC_2/SPRINT_6/PLAN.md`:

```markdown
# Sprint 6 Plan: Convexity Heuristics, Critical Bug Fixes, GAMSLib Bootstrapping, UX Kickoff

**Duration:** 2 weeks (10 working days)
**Goal:** Deliver v0.6.0 with convexity detection, bug fixes, and GAMSLib foundation

## Day 1-2: Convexity Heuristics (Foundation)
- Implement pattern matchers (nonlinear eq, trig, bilinear)
- Add CLI flags (--strict-convexity)
- Unit tests for each pattern
- Checkpoint 1: Patterns detect all non-convex test cases

## Day 3-4: Bug Fixes (Maximize + Nested Min/Max)
- Fix maximize bound multiplier signs
- Implement nested min/max flattening
- Regression tests for both fixes
- PATH validation
- Checkpoint 2: All tests pass, PATH solves test cases

## Day 5-6: GAMSLib Bootstrapping
- Run download script for Tier 1 models
- Create conversion status dashboard
- Implement parse-only ingestion
- Collect baseline metrics
- Checkpoint 3: 10 models ingested, dashboard live

## Day 7-8: Convexity Integration + UX
- Integrate convexity warnings into CLI
- Apply error message improvements
- Documentation updates
- User-facing polish

## Day 9-10: Testing, Documentation, Release
- Full regression suite
- Performance benchmarks
- Documentation review
- Release v0.6.0
```

#### Step 3: Define Checkpoints (1 hour)

Three checkpoints:
1. **Checkpoint 1 (Day 2):** Convexity patterns working
2. **Checkpoint 2 (Day 4):** Bug fixes complete
3. **Checkpoint 3 (Day 6):** GAMSLib ingestion live

Each checkpoint:
- Acceptance criteria
- Demo artifacts
- Go/no-go decision

#### Step 4: Risk Mitigation (1 hour)

Identify risks and mitigations:

**Risk 1:** Convexity patterns have high false positive rate
- **Mitigation:** Tune patterns based on test results, start conservative

**Risk 2:** Maximize fix breaks minimize cases
- **Mitigation:** Extensive regression testing, fix only bound logic

**Risk 3:** GAMSLib models have unexpected syntax
- **Mitigation:** Start with simple models, document blockers for Sprint 7

**Changes:**

*To be completed*

**Result:**

*To be completed*

### Verification

```bash
# Plan exists
test -f docs/planning/EPIC_2/SPRINT_6/PLAN.md

# Contains daily schedule
grep -q "Day 1-2" docs/planning/EPIC_2/SPRINT_6/PLAN.md

# Contains checkpoints
grep -q "Checkpoint 1" docs/planning/EPIC_2/SPRINT_6/PLAN.md
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_6/PLAN.md` - Detailed sprint plan
- Daily task breakdown (10 days)
- 3 checkpoint definitions with criteria
- Risk register with mitigations
- Acceptance criteria for v0.6.0 release

### Acceptance Criteria

- [ ] Daily schedule covers all 10 days
- [ ] Each day has 4-8 hours of planned work
- [ ] Dependencies clearly marked (e.g., bug fixes don't block GAMSLib)
- [ ] 3 checkpoints defined with demo criteria
- [ ] Risk register includes ≥3 risks with mitigations
- [ ] Release criteria for v0.6.0 documented
- [ ] Plan reviewed and approved by team

---

## Summary and Critical Path

### Critical Path

```
Task 1 (Known Unknowns)
  ↓
Task 2 (Convexity Research) ──┐
Task 3 (Maximize Bug)        ──┼── Task 10 (Sprint Plan)
Task 5 (Nested Min/Max)      ──┘
```

**Parallel tracks:**
- Track 1: Convexity (Tasks 1, 2, 8)
- Track 2: Bug fixes (Tasks 1, 3, 5)
- Track 3: GAMSLib (Tasks 4, 7)
- Track 4: UX (Task 6)

All converge into Task 10 (Sprint Plan).

### Success Criteria for Prep Phase

Sprint 6 prep is complete when:
- [ ] All 10 tasks status = ✅ COMPLETED
- [ ] Known Unknowns document has 18+ unknowns
- [ ] All Critical unknowns have verification plans
- [ ] Convexity approach validated (Approach 1 recommended)
- [ ] Bug fix designs approved (maximize + nested min/max)
- [ ] 10 GAMSLib models cataloged and downloaded
- [ ] Sprint 6 PLAN.md reviewed and approved
- [ ] All prep deliverables in docs/planning/EPIC_2/SPRINT_6/

### Next Steps After Prep

1. **Sprint 6 Kickoff Meeting**
   - Review PLAN.md
   - Assign daily tasks
   - Confirm checkpoint dates

2. **Day 1 Activities**
   - Create feature branches
   - Set up checkpoint tracking
   - Begin Task 1.1 (Convexity pattern matchers)

3. **Daily Standups**
   - Review progress against PLAN.md
   - Surface blockers from Known Unknowns
   - Adjust schedule if needed

---

## Appendix: Document Cross-References

### Key Documents
- **Epic 2 Goals:** `docs/planning/EPIC_2/GOALS.md`
- **Epic 2 Project Plan:** `docs/planning/EPIC_2/PROJECT_PLAN.md`
- **Sprint 6 Plan:** `docs/planning/EPIC_2/SPRINT_6/PLAN.md` (created in Task 10)
- **Known Unknowns:** `docs/planning/EPIC_2/SPRINT_6/KNOWN_UNKNOWNS.md` (created in Task 1)

### Related Research
- **Convexity Detection:** `docs/research/convexity_detection.md`
- **Maximize Bug:** `docs/planning/EPIC_1/SPRINT_5/follow-ons/MAXIMIZE_BOUND_MULTIPLIER_BUG.md`
- **Nested Min/Max:** `docs/planning/EPIC_1/SPRINT_5/follow-ons/NESTED_MINMAX_REQUIREMENTS.md`

### Epic 1 References
- **Sprint 4 Prep:** `docs/planning/EPIC_1/SPRINT_4/PREP_PLAN.md`
- **Sprint 5 Prep:** `docs/planning/EPIC_1/SPRINT_5/PREP_PLAN.md`
- **Epic 1 Summary:** `docs/planning/EPIC_1/SUMMARY.md`
