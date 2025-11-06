# Sprint 5 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 5 production hardening and release  
**Timeline:** Complete before Sprint 5 Day 1  
**Goal:** Address Sprint 4 learnings and prepare for production release

**Key Insight from Sprint 4:** Known Unknowns process achieved ⭐⭐⭐⭐⭐ rating - 23 unknowns identified, 10 resolved proactively, 13 on schedule, zero late surprises. Continue this success in Sprint 5.

---

## Executive Summary

Sprint 4 Retrospective identified production readiness as the primary focus for Sprint 5. The sprint will address:
1. **Priority 1 (Critical):** Fix min/max reformulation bug that causes PATH solver failures
2. **Priority 2 (Validation):** Complete PATH solver validation with available licensing
3. **Priority 3 (Production):** Hardening for large models, error recovery, memory optimization
4. **Priority 4 (Release):** PyPI packaging and release automation
5. **Priority 5 (Documentation):** Tutorial, FAQ, troubleshooting, API reference

This prep plan focuses on research and setup tasks that must be completed before Sprint 5 Day 1 to prevent blocking issues.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint 4 Issue Addressed |
|---|------|----------|-----------|--------------|--------------------------|
| 1 | ✅ Create Sprint 5 Known Unknowns List | Critical | 2-3 hours | None | Proactive unknown identification |
| 2 | Research Min/Max Reformulation Strategies | Critical | 4-6 hours | Task 1 | Strategy validation before implementation |
| 3 | Validate PATH Solver Environment | Critical | 2 hours | None | Ensure licensing and setup correct |
| 4 | Benchmark Current Performance Baselines | High | 3 hours | None | Establish pre-optimization baselines |
| 5 | Survey PyPI Packaging Best Practices | High | 3 hours | None | Modern Python packaging standards |
| 6 | Audit Current Documentation Gaps | High | 2 hours | None | Identify documentation priorities |
| 7 | Set Up Sphinx Documentation Environment | Medium | 2 hours | Task 6 | API reference infrastructure |
| 8 | Create Large Model Test Fixtures | Medium | 3 hours | None | Production hardening test data |
| 9 | Review Sprint 4 Retrospective Action Items | High | 1 hour | None | Ensure all followups captured |
| 10 | Plan Sprint 5 Scope and Schedule | Critical | 4 hours | All tasks | Sprint 5 planning |

**Total Estimated Time:** ~26-29 hours (~3-4 working days)

**Critical Path:** Tasks 1 → 2 → 10 (must complete before Sprint 5)

**Note:** Task 1 (Known Unknowns) is already ✅ **COMPLETED** as of November 5, 2025. Document available at `docs/planning/SPRINT_5/KNOWN_UNKNOWNS.md` with 22 unknowns identified.

---

## Task 1: Create Sprint 5 Known Unknowns List (COMPLETED)

**Status:** ✅ **COMPLETED** (November 5, 2025)  
**Priority:** Critical  
**Time Spent:** 3 hours  

### What Was Done

Created comprehensive `docs/planning/SPRINT_5/KNOWN_UNKNOWNS.md` with 22 unknowns across 5 categories.

**Statistics:**
- **Total Unknowns:** 22
- **By Priority:** 3 Critical, 8 High, 7 Medium, 4 Low
- **By Category:** Min/Max Fix (5), PATH Validation (4), Production Hardening (5), PyPI Packaging (4), Documentation (4)
- **Estimated Research Time:** 12-16 hours

**Categories:**
1. Min/Max Reformulation Fix (5 unknowns)
2. PATH Solver Validation (4 unknowns)
3. Production Hardening (5 unknowns)
4. PyPI Packaging (4 unknowns)
5. Documentation Polish (4 unknowns)

**Critical Unknowns:**
- Unknown 1.1: Does Strategy 2 (Direct Constraints) handle all objective-defining cases?
- Unknown 3.2: What memory limit is acceptable for 10,000+ equation models?
- Unknown 4.1: Does `pyproject.toml` build system work with current dependencies?

### Verification

Document available at: `docs/planning/SPRINT_5/KNOWN_UNKNOWNS.md`

**Acceptance Criteria:** ✅ All met
- [x] Document created with 22+ unknowns across 5 categories
- [x] All unknowns have assumption, verification method, priority
- [x] All Critical/High unknowns have verification plan
- [x] Unknowns cover all Sprint 5 priorities
- [x] Template for updates defined
- [x] Research time estimated (12-16 hours)

---

## Task 2: Research Min/Max Reformulation Strategies

**Priority:** Critical  
**Estimated Time:** 4-6 hours  
**Deadline:** 1 week before Sprint 5 Day 1  
**Owner:** Development team  
**Dependencies:** Task 1 (Known Unknowns)

### Objective

Validate the min/max reformulation strategies from `docs/research/minmax_objective_reformulation.md` and resolve all Critical/High unknowns in Category 1 before implementation.

### Why This Matters

Sprint 5 Priority 1 (days 1-2) depends entirely on having a validated fix for the min/max reformulation bug. Wrong approach = major refactoring during sprint.

Current situation:
- Research document proposes Strategy 2 (Direct Constraints) for objective-defining min/max
- 5 unknowns in Category 1 of KNOWN_UNKNOWNS.md must be verified
- No live testing of Strategy 2 implementation yet

### Background

**The Bug:** Min/max reformulation creates auxiliary variables and constraints, but their multipliers aren't included in stationarity equations, causing PATH solver failures.

**Proposed Fix (Strategy 2):** For min/max that defines objective variable, use direct constraints instead of auxiliary variables.
- Example: `minimize z` where `z = min(x,y)` → `minimize z` with `z ≤ x, z ≤ y`

**Research Questions (from KNOWN_UNKNOWNS.md Category 1):**

#### Unknown 1.1: Does Strategy 2 handle all objective-defining cases? (CRITICAL)
- Maximize with max: `maximize z` where `z = max(x,y)` → `z ≥ x, z ≥ y` ✓
- Minimize with max: `minimize z` where `z = max(x,y)` → ? (opposite sense)
- Maximize with min: `maximize z` where `z = min(x,y)` → ? (opposite sense)
- Chains: `obj = z1`, `z1 = z2`, `z2 = min(x,y)` → ?

#### Unknown 1.2: What happens when min/max is nested? (HIGH)
- `z = min(min(x,y), w)`
- `z = max(min(x,y), w)`
- Does detection work correctly?
- Does reformulation apply recursively?

#### Unknown 1.3: Can non-objective min/max still use auxiliary variables? (HIGH)
- Min/max in constraint: current approach should work
- But does new code path affect these cases?
- Need regression tests

#### Unknown 1.4: How to detect "objective-defining"? (HIGH)
- Is it just: variable appears on LHS of objdef equation?
- What about: `objdef.. obj =e= f(z)` where `aux.. z =e= min(x,y)`?
- Need precise definition

#### Unknown 1.5: Does PATH solve the reformulated MCP? (MEDIUM)
- Mathematical correctness doesn't guarantee convergence
- Need to actually run PATH solver
- Test all 5 test cases from research doc

### Implementation Steps

#### Step 1: Create Test GAMS Models (1 hour)

For each research question, create minimal GAMS NLP model:

```python
# tests/fixtures/minmax_test_models.py

def create_minimize_min_model(output_path: Path):
    """
    Test Case 1: minimize z where z = min(x,y)
    Expected: Convert to z ≤ x, z ≤ y
    """
    content = """
Variables x, y, z, obj;
x.lo = 0; x.up = 10;
y.lo = 0; y.up = 10;

Equations objdef, minconstraint;

objdef.. obj =e= z;
minconstraint.. z =e= min(x, y);

Model test /all/;
Solve test using NLP minimizing obj;
"""
    output_path.write_text(content)
    return output_path

def create_maximize_max_model(output_path: Path):
    """
    Test Case 2: maximize z where z = max(x,y)
    Expected: Convert to z ≥ x, z ≥ y
    """
    # Similar structure...

def create_minimize_max_model(output_path: Path):
    """
    Test Case 3: minimize z where z = max(x,y) (opposite sense)
    Expected: ???
    """
    # Need to determine correct reformulation

def create_nested_min_model(output_path: Path):
    """
    Test Case 4: z = min(min(x,y), w)
    Expected: Recursive handling?
    """
    # Test nested case

def create_constraint_min_model(output_path: Path):
    """
    Test Case 5: min/max in constraint (not objective)
    Expected: Existing auxiliary variable approach
    """
    # Regression test
```

#### Step 2: Manually Reformulate Each Case (2 hours)

For each test case:
1. Convert NLP to KKT system by hand
2. Identify correct MCP formulation
3. Document expected PATH solution
4. Verify mathematical correctness

**Example for Test Case 1:**

Original NLP:
```
minimize obj
s.t. obj = z
     z = min(x, y)
     0 ≤ x ≤ 10
     0 ≤ y ≤ 10
```

Strategy 2 reformulation:
```
minimize obj
s.t. obj = z
     z ≤ x
     z ≤ y
     0 ≤ x ≤ 10
     0 ≤ y ≤ 10
```

KKT conditions:
```
Stationarity (obj): 1 + ν_objdef = 0
Stationarity (z):   -ν_objdef + λ1 + λ2 = 0  (from z ≤ x, z ≤ y)
Stationarity (x):   -λ1 + πL_x - πU_x = 0
Stationarity (y):   -λ2 + πL_y - πU_y = 0

Complementarity: λ1 ⊥ (z - x), λ2 ⊥ (z - y), etc.
```

Expected solution: `z = x = y = 0` (minimize z pushes it to zero, constraints force x,y ≥ z)

#### Step 3: Test with PATH Solver (2 hours)

For each test case:
1. Manually create reformulated GAMS MCP
2. Solve with PATH
3. Verify solution matches expected
4. Document any issues

```bash
# Test each case
cd tests/fixtures/minmax_manual_reformulation/

# Test Case 1
gams minimize_min_manual_mcp.gms
# Expected: Optimal solution found
# Solution: z ≈ 0, x ≈ 0, y ≈ 0

# Test Case 2
gams maximize_max_manual_mcp.gms
# Expected: Optimal solution found
# Solution: z ≈ 10, x ≈ 10, y ≈ 10

# Test Case 3
gams minimize_max_manual_mcp.gms
# Expected: ??? (need to determine correct behavior)
```

#### Step 4: Document Findings (1 hour)

Update `docs/research/minmax_objective_reformulation.md` with:

**Section: Validation Results**

```markdown
## Validation Results (Pre-Sprint 5)

### Test Case 1: minimize z where z = min(x,y)
**Status:** ✅ VALIDATED
**Strategy:** Direct constraints (z ≤ x, z ≤ y)
**PATH Result:** Optimal solution, z = x = y = 0
**Conclusion:** Strategy 2 works as expected

### Test Case 2: maximize z where z = max(x,y)
**Status:** ✅ VALIDATED
**Strategy:** Direct constraints (z ≥ x, z ≥ y)
**PATH Result:** Optimal solution, z = x = y = 10
**Conclusion:** Symmetric case works

### Test Case 3: minimize z where z = max(x,y) (opposite sense)
**Status:** [VALIDATED / ISSUE FOUND]
**Strategy:** [Document correct approach]
**PATH Result:** [Document outcome]
**Conclusion:** [Document findings]

[Similar for remaining test cases]
```

#### Step 5: Update Known Unknowns (30 min)

Mark all Category 1 unknowns as resolved in `docs/planning/SPRINT_5/KNOWN_UNKNOWNS.md`:

```markdown
## Unknown 1.1: Does Strategy 2 handle all objective-defining cases?

**Status:** ✅ VERIFIED (Pre-Sprint 5)

**Findings:**
- minimize/min: ✅ Works (z ≤ x, z ≤ y)
- maximize/max: ✅ Works (z ≥ x, z ≥ y)
- minimize/max: ✅ Works [document approach]
- maximize/min: ✅ Works [document approach]
- Chains: ✅ Works [document approach]

**Implementation Ready:** Yes, proceed with Strategy 2
```

### Deliverable

**Files Created/Updated:**
- `tests/fixtures/minmax_test_models.py` - Test case generators
- `tests/fixtures/minmax_manual_reformulation/*.gms` - Manual MCP files for validation
- `docs/research/minmax_objective_reformulation.md` - Validation results section
- `docs/planning/SPRINT_5/KNOWN_UNKNOWNS.md` - Category 1 unknowns marked resolved

**Documentation:**
- All 5 test cases validated with PATH solver
- Correct reformulation strategy documented for each case
- Any edge cases or limitations identified
- Implementation ready for Sprint 5 Day 1

### Acceptance Criteria

- [ ] All 5 test cases from research doc created as GAMS models
- [ ] Manual MCP reformulation created for each test case
- [ ] PATH solver successfully solves all test cases (or failures documented)
- [ ] All Category 1 unknowns in KNOWN_UNKNOWNS.md marked as verified
- [ ] Validation results documented in research doc
- [ ] Any surprises or edge cases documented
- [ ] Implementation approach confirmed for Sprint 5 Day 1

### Expected Outcome

**Sprint 5 Day 1 morning:**
- Developer implements min/max reformulation fix
- References validated Strategy 2 from research doc
- All test cases already proven to work with PATH
- No surprises or mathematical issues during implementation
- **Result:** 1-2 day implementation with high confidence, no emergency debugging

---

## Task 3: Validate PATH Solver Environment

**Priority:** Critical  
**Estimated Time:** 2 hours  
**Deadline:** 1 week before Sprint 5 Day 1  
**Owner:** Development team

### Objective

Verify PATH solver environment is correctly configured with licensing and ready for validation testing in Sprint 5 Priority 2.

### Why This Matters

Sprint 5 Priority 2 (day 3) requires running full PATH solver validation suite. Licensing issues discovered on Day 3 would block sprint progress.

Sprint 4 Prep notes: "PATH solver tests exist but marked xfail due to golden file infeasibility issues."

### Current Status (from Sprint 4)

**Test Framework:** ✅ EXISTS
- File: `tests/validation/test_path_solver.py`
- Tests: 6 total (5 solve validation + 1 availability check)
- Status: 1 passed, 5 xfailed (due to golden file modeling issues)

**PATH Environment:** ✅ INSTALLED
- GAMS Version: 51.3.0
- PATH Solver: 5.2.01
- License: Demo license (sufficient for test problems)
- Location: `/Library/Frameworks/GAMS.framework/Versions/51/Resources/`

**Known Issues:**
- 5 golden MCP files produce Model Status 4 (Infeasible)
- Root cause: Sign error in stationarity equations (lam_balance forced negative but declared Positive)
- Tests marked `@pytest.mark.xfail` until golden files corrected

### Implementation Steps

#### Step 1: Verify PATH Availability (15 min)

```bash
# Check GAMS installation
which gams
gams --version
# Expected: GAMS 51.3.0 or higher

# Check PATH solver
gams << EOF
\$ontext
Test PATH solver availability
\$offtext
Variables x; x.l = 0; x.lo = -inf; x.up = inf;
Equations dummy; dummy.. x =e= 0;
Model test /all/;
option mcp=path;
Solve test using mcp;
Display x.l;
EOF

# Expected: PATH solver runs, x.l = 0
```

#### Step 2: Run PATH Availability Test (10 min)

```bash
# Run availability test
pytest tests/validation/test_path_solver.py::TestPATHSolverValidation::test_path_available -v

# Expected: PASSED
```

If test fails:
- Check GAMS_PATH environment variable
- Verify GAMS license
- Check PATH solver license status

#### Step 3: Document Current Test Status (30 min)

Create summary of PATH test status:

```markdown
# PATH Solver Validation Status (Pre-Sprint 5)

## Environment
- **GAMS Version:** 51.3.0
- **PATH Solver:** 5.2.01
- **License:** Demo (sufficient for nlp2mcp test suite)
- **Location:** `/Library/Frameworks/GAMS.framework/Versions/51/Resources/`
- **Status:** ✅ Installed and accessible

## Test Suite Status

### tests/validation/test_path_solver.py
- **Total Tests:** 6
- **Passing:** 1 (test_path_available)
- **Xfailed:** 5 (golden file infeasibility issues)

#### Xfailed Tests (Expected Failures)
1. `test_simple_nlp_solves` - Model Status 4 (Infeasible)
2. `test_bounds_nlp_solves` - Model Status 4 (Infeasible)
3. `test_indexed_balance_solves` - Model Status 4 (Infeasible)
4. `test_nonlinear_mix_solves` - Model Status 4 (Infeasible)
5. `test_scalar_nlp_solves` - Model Status 4 (Infeasible)

**Root Cause:** Golden MCP files have sign error in stationarity equations:
```gams
stat_x(i).. a(i) + 1 * lam_balance(i) =E= 0;
```
Forces `lam_balance(i) = -a(i)` (negative when a(i) > 0), but `lam_balance` declared as `Positive Variable`.

**Resolution Plan:** Sprint 5 Priority 2 will regenerate golden files with corrected formulation.

## Action Items for Sprint 5 Priority 2
1. Regenerate all 5 golden MCP files with correct KKT formulation
2. Remove `@pytest.mark.xfail` decorators
3. Verify all tests pass
4. Document any remaining issues
```

#### Step 4: Test on Different Model Sizes (30 min)

Create test models of various sizes to verify licensing:

```bash
# Small model (10 vars, 5 constraints) - should work with demo license
python -c "
from tests.benchmarks.test_performance import TestPerformanceBenchmarks
from pathlib import Path
test = TestPerformanceBenchmarks()
model = test._generate_model(Path('/tmp'), 'small', 10, 5)
print(f'Created: {model}')
"

# Convert and solve
nlp2mcp /tmp/small_model.gms -o /tmp/small_mcp.gms
gams /tmp/small_mcp.gms

# Expected: PATH solves successfully

# Medium model (100 vars, 50 constraints) - verify demo license sufficient
# [Similar test]

# Large model (1000 vars, 500 constraints) - may hit demo license limit
# [Document if demo license insufficient]
```

#### Step 5: Document License Limitations (15 min)

```markdown
## GAMS Demo License Limitations

**Tested Model Sizes:**
- ✅ 10 variables, 5 constraints - Works
- ✅ 100 variables, 50 constraints - Works
- ⚠️ 1000 variables, 500 constraints - [Document result]
- ❌ 10,000 variables, 5,000 constraints - Demo limit exceeded

**Demo License Limits:**
- Maximum variables: [Document]
- Maximum equations: [Document]
- Sufficient for nlp2mcp test suite: [Yes/No]

**If Full License Needed:**
- Contact: GAMS support
- Use case: Open source optimization tool testing
- Alternative: Skip large model tests in CI
```

### Deliverable

**File:** `docs/testing/PATH_SOLVER_STATUS.md`

**Contents:**
- PATH solver environment details
- Current test suite status
- Known issues with golden files
- License limitations
- Action items for Sprint 5 Priority 2

### Acceptance Criteria

- [x] GAMS and PATH verified installed and accessible
- [x] PATH availability test passes
- [x] Current test status documented (3 pass, 1 xfail in minmax)
- [x] Golden file issues documented (resolved - tests now passing)
- [x] License limitations tested and documented
- [x] PATH_SOLVER_STATUS.md created with all details
- [x] No blockers for Sprint 5 Priority 2

**Note:** Test suite status differs from Sprint 4 notes. Currently 3 tests passing in test_path_solver.py (test_path_available, test_solve_simple_nlp_mcp, test_solve_indexed_balance_mcp). The 5 xfailed tests mentioned in Sprint 4 notes appear to have been resolved. Only 1 xfail remains in test_path_solver_minmax.py (expected due to known min/max bug).

### Expected Outcome

**Sprint 5 Day 3 morning:**
- Developer starts PATH validation work
- No licensing surprises
- Environment already verified
- Clear understanding of golden file issues
- Can immediately start regenerating correct MCP files
- **Result:** 1 day validation work proceeds smoothly, no environment debugging

---

## Task 4: Benchmark Current Performance Baselines

**Priority:** High  
**Estimated Time:** 3 hours  
**Deadline:** Before Sprint 5 Day 1  
**Owner:** Development team

### Objective

Establish performance and memory baselines before Sprint 5 Priority 3 optimization work. Need quantitative metrics to measure improvement.

### Why This Matters

Sprint 5 Priority 3 (days 4-6) includes large model testing and memory optimization. Without baselines:
- Can't measure optimization improvements
- Can't identify performance regressions
- Can't set reasonable targets

### Current Status

Sprint 4 Prep created benchmark suite:
- File: `tests/benchmarks/test_performance.py`
- 7 benchmarks: small/medium/large parsing, differentiation scalability, memory usage, end-to-end, sparsity exploitation
- Status: Tests exist, baselines not formally documented

### Implementation Steps

#### Step 1: Run Full Benchmark Suite (1 hour)

```bash
# Run all benchmarks with pytest-benchmark
pytest tests/benchmarks/test_performance.py -v --benchmark-only --benchmark-autosave

# Generate benchmark report
pytest tests/benchmarks/test_performance.py --benchmark-only --benchmark-json=/tmp/baseline.json

# View results
cat /tmp/baseline.json | jq '.benchmarks[] | {name: .name, mean: .stats.mean, stddev: .stats.stddev}'
```

#### Step 2: Document Baseline Metrics (1 hour)

Create formal baseline document:

```markdown
# Performance Baselines (Pre-Sprint 5)

**Date:** [Date]
**System:** [OS, CPU, RAM]
**Python:** [Version]
**Dependencies:** [Key versions: numpy, lark, etc.]

## Parsing Performance

| Model Size | Variables | Constraints | Parse Time (mean) | Std Dev |
|------------|-----------|-------------|-------------------|---------|
| Small      | 10        | 5           | 0.045s            | 0.002s  |
| Medium     | 100       | 50          | 0.312s            | 0.008s  |
| Large      | 1,000     | 500         | 3.145s            | 0.125s  |

**Scalability:** 10x variables = ~70x parse time (sub-quadratic ✓)

## Differentiation Performance

| Model Size | Gradient Time | Jacobian Time | Total |
|------------|---------------|---------------|-------|
| Small      | 0.012s        | 0.028s        | 0.040s |
| Medium     | 0.145s        | 0.523s        | 0.668s |

**Scalability:** 10x variables = 16.7x time (sub-quadratic ✓)

## Memory Usage

| Model Size | Variables | Constraints | Peak Memory |
|------------|-----------|-------------|-------------|
| Small      | 10        | 5           | 8.2 MB      |
| Medium     | 100       | 50          | 24.7 MB     |
| Large      | 1,000     | 500         | 78.5 MB     |

**Target:** < 100 MB for 1,000 variables ✓

## End-to-End Performance

| Model Size | Total Time | Throughput |
|------------|------------|------------|
| Medium     | 1.234s     | 81 vars/sec |

## Sparsity Exploitation

| Model Type | Jacobian Time | Speedup (vs dense) |
|------------|---------------|---------------------|
| Sparse (2% density) | 0.052s | 1.0x (baseline) |
| Dense (100% density) | 0.875s | 16.8x slower |

**Conclusion:** Sparsity exploitation working well

## Baseline Summary

**Strengths:**
- Sub-quadratic scaling in parsing and differentiation ✓
- Memory usage reasonable for 1,000 var models ✓
- Sparsity exploitation effective ✓

**Optimization Targets for Sprint 5:**
- Parse time: Improve large model parsing (currently 3.1s for 1K vars)
- Memory: Test 10,000 variable models (current limit unknown)
- Differentiation: Profile for hotspots (0.67s for 100 vars)

**Sprint 5 Goals:**
- Large model (10,000 vars): Parse < 30s, Memory < 500 MB
- Medium model optimization: End-to-end < 1.0s (currently 1.234s)
```

#### Step 3: Identify Optimization Targets (30 min)

Profile current implementation to find hotspots:

```python
# Profile parsing
python -m cProfile -o parse.prof -m nlp2mcp tests/fixtures/large_model.gms -o /tmp/out.gms

# Analyze
python -c "
import pstats
p = pstats.Stats('parse.prof')
p.sort_stats('cumulative')
p.print_stats(20)
"

# Expected hotspots:
# - GAMS parsing (lark)
# - Expression tree traversal
# - Dictionary lookups
# - String formatting in emission
```

Document top 5 hotspots for Sprint 5 optimization focus.

#### Step 4: Set Sprint 5 Targets (30 min)

Based on baselines and Sprint 5 Priority 3 goals:

```markdown
## Sprint 5 Optimization Targets

### Large Model Performance (10,000 variables, 5,000 constraints)

**Current:** Unknown (not tested)
**Target:**
- Parse: < 30 seconds
- Differentiation: < 60 seconds
- Total end-to-end: < 120 seconds
- Memory: < 500 MB peak

**Rationale:** 2x larger than 1,000 var model, allow 4x time (sub-quadratic)

### Medium Model Optimization (100 variables, 50 constraints)

**Current:** 1.234s end-to-end
**Target:** < 1.0s end-to-end (20% improvement)

**Focus areas:**
1. Parsing: 0.312s → < 0.25s (optimize lark grammar)
2. Differentiation: 0.668s → < 0.55s (cache subexpressions)
3. Emission: Remaining time → < 0.20s (optimize string ops)

### Memory Optimization

**Current:** 78.5 MB for 1,000 vars
**Target:** < 400 MB for 10,000 vars (5x model size, allow 5x memory)

**Focus areas:**
- Sparse matrix representations
- AST node memory footprint
- String interning for repeated names
```

### Deliverable

**File:** `docs/benchmarks/PERFORMANCE_BASELINES.md`

**Contents:**
- Complete benchmark results (all 7 benchmarks)
- System configuration
- Baseline metrics table
- Scalability analysis
- Optimization targets for Sprint 5
- Profiling hotspots identified

### Acceptance Criteria

- [x] All 7 benchmarks run and results documented
- [x] Baseline metrics captured for small/medium/large models
- [x] Scalability verified (sub-quadratic)
- [x] Memory usage documented (skipped benchmark, documented estimates)
- [x] Sparsity exploitation verified
- [x] Top 5 performance hotspots identified
- [x] Sprint 5 optimization targets defined
- [x] PERFORMANCE_BASELINES.md created

### Expected Outcome

**Sprint 5 Day 4 morning:**
- Developer starts optimization work
- Has clear baseline metrics (e.g., 1.234s for medium model)
- Has quantitative targets (< 1.0s for medium model)
- Knows where to focus (parsing: 0.312s, differentiation: 0.668s)
- Can measure improvements objectively
- **Result:** Data-driven optimization, avoid premature optimization, clear success criteria

---

## Task 5: Survey PyPI Packaging Best Practices

**Priority:** High  
**Estimated Time:** 3 hours  
**Deadline:** Before Sprint 5 Day 1  
**Owner:** Development team

### Objective

Research modern Python packaging standards and prepare for Sprint 5 Priority 4 (PyPI packaging and release).

### Why This Matters

Sprint 5 Priority 4 (days 7-8) will create production PyPI package. Python packaging landscape has evolved significantly:
- `setup.py` → `pyproject.toml` (PEP 517/518)
- `setuptools` vs `hatchling` vs `poetry` vs `pdm`
- Build backends, editable installs, lockfiles
- Modern best practices (2025)

Need to research upfront to avoid mid-sprint rewrites.

### Current Status

Project uses `pyproject.toml` with basic configuration:
- Build system: setuptools
- CLI entry point: `nlp2mcp`
- Dependencies specified
- No lockfile, no publishing workflow

### Research Questions (from KNOWN_UNKNOWNS.md Category 4)

#### Unknown 4.1: Does `pyproject.toml` build system work with current dependencies? (CRITICAL)
- Can we build wheel: `python -m build`?
- Do dependencies install correctly?
- Any conflicts or missing specifications?

#### Unknown 4.2: Should we use `setuptools`, `hatchling`, `poetry`, or `pdm`? (HIGH)
- Modern recommendation for libraries?
- Pros/cons of each?
- Migration effort if switching?

#### Unknown 4.3: How to manage dev vs prod dependencies? (HIGH)
- `[project.optional-dependencies]`?
- Separate `requirements-dev.txt`?
- Lock files for reproducibility?

#### Unknown 4.4: What's the modern GitHub Actions workflow for PyPI publishing? (MEDIUM)
- Trusted publisher (OIDC) vs API token?
- TestPyPI testing flow?
- Automated version bumping?

### Implementation Steps

#### Step 1: Test Current Build System (30 min)

```bash
# Test current pyproject.toml
python -m build

# Expected: Successful wheel creation or errors to fix

# Test installation from wheel
pip install dist/nlp2mcp-*.whl

# Test CLI entry point
nlp2mcp --version

# Expected: CLI works or errors to fix
```

Document any issues found.

#### Step 2: Research Build Backends (1 hour)

Compare modern options:

| Build Backend | Pros | Cons | Use Case |
|---------------|------|------|----------|
| **setuptools** | - Standard, widely used<br>- Good compatibility | - Verbose config<br>- Legacy cruft | Safe default choice |
| **hatchling** | - Modern, clean<br>- Fast builds<br>- Good defaults | - Newer, less mature<br>- Plugin ecosystem smaller | Modern projects, speed matters |
| **poetry** | - All-in-one (build + deps)<br>- Lock files built-in | - Opinionated<br>- Non-standard commands<br>- Migration effort | Full project management |
| **pdm** | - PEP 582 support<br>- Fast resolver | - Less adoption<br>- Learning curve | Experimental projects |

**Recommendation for nlp2mcp:**
- Current: setuptools (working)
- Consider: hatchling (modern, minimal migration)
- Avoid: poetry/pdm (overkill for library)

#### Step 3: Review Dependency Management (30 min)

**Current approach:**
```toml
[project]
dependencies = [
    "lark>=1.0.0",
    "numpy>=1.20.0",
    # ...
]
```

**Modern best practice:**
```toml
[project]
dependencies = [
    "lark>=1.1.0,<2.0",  # Upper bound for stability
    "numpy>=1.20.0,<2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "mypy>=1.0",
    "ruff>=0.1.0",
]
test = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
]
docs = [
    "sphinx>=6.0",
    "sphinx-rtd-theme>=1.0",
]
```

**Lock files:**
- For applications: Use `requirements.txt` or `poetry.lock`
- For libraries: No lock file (users control versions)
- nlp2mcp is both CLI tool and library → Use `requirements-dev.txt` for dev reproducibility

#### Step 4: Survey PyPI Publishing Workflows (1 hour)

Research modern GitHub Actions publishing:

**Option A: Trusted Publisher (OIDC) - Modern, secure**
```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # OIDC token
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Build
        run: |
          pip install build
          python -m build
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        # No API token needed - uses OIDC
```

**Option B: API Token - Traditional**
- Requires storing PyPI API token in GitHub secrets
- More manual setup
- Still secure but less automated

**Recommendation:** Use Trusted Publisher (modern standard as of 2025)

#### Step 5: Document Packaging Plan (30 min)

Create packaging preparation document:

```markdown
# PyPI Packaging Plan (Pre-Sprint 5)

## Current Status
- **Build system:** setuptools (via pyproject.toml)
- **Entry point:** nlp2mcp CLI ✅
- **Dependencies:** Specified in pyproject.toml
- **Tests:** pytest suite (972 tests passing)
- **Documentation:** README.md, USER_GUIDE.md, API docs pending

## Sprint 5 Priority 4 Implementation Plan

### Phase 1: Validate Current Build (Day 7 Morning)
- [ ] Run `python -m build` - verify successful
- [ ] Test wheel installation in clean venv
- [ ] Test CLI entry point
- [ ] Fix any build errors found

### Phase 2: Enhance pyproject.toml (Day 7 Afternoon)
- [ ] Add complete metadata (classifiers, keywords, project URLs)
- [ ] Add upper bounds to dependencies (e.g., `lark>=1.1,<2.0`)
- [ ] Organize optional dependencies (dev, test, docs)
- [ ] Add README.md as long_description

### Phase 3: Release Automation (Day 8 Morning)
- [ ] Create GitHub Actions publish workflow (OIDC)
- [ ] Set up PyPI trusted publisher
- [ ] Test publish to TestPyPI
- [ ] Document release process

### Phase 4: Testing and Release (Day 8 Afternoon)
- [ ] Test installation from TestPyPI
- [ ] Test on Python 3.10, 3.11, 3.12
- [ ] Test on macOS (current), Linux, Windows (CI)
- [ ] Publish v0.4.0 to PyPI
- [ ] Update README with `pip install nlp2mcp`

## Build Backend Decision
**Choice:** Keep setuptools
**Rationale:**
- Currently working
- Industry standard
- Good compatibility
- Migration to hatchling possible later if needed

## Dependency Management
**Choice:** Add upper bounds, optional-dependencies groups
**Rationale:**
- Stability: upper bounds prevent breaking changes
- Organization: separate dev/test/docs dependencies
- Best practice: optional-dependencies standard in pyproject.toml

## Publishing Strategy
**Choice:** GitHub Actions with OIDC trusted publisher
**Rationale:**
- Modern standard (2025)
- No secrets management
- Automated on release creation
- Secure and auditable
```

### Deliverable

**File:** `docs/release/PYPI_PACKAGING_PLAN.md`

**Contents:**
- Current build system status
- Build backend comparison and decision
- Dependency management strategy
- Publishing workflow design
- Sprint 5 Priority 4 implementation steps
- Testing checklist

### Acceptance Criteria

- [x] Current build tested (`python -m build` works or issues documented)
- [x] Build backend options researched and decision documented
- [x] Dependency management strategy defined
- [x] Publishing workflow researched (OIDC vs API token)
- [x] Sprint 5 implementation plan created
- [x] All 4 Category 4 unknowns addressed
- [x] PYPI_PACKAGING_PLAN.md created

### Expected Outcome

**Sprint 5 Day 7 morning:**
- Developer starts PyPI packaging work
- Has clear plan (validate, enhance, automate, test)
- Knows which build system to use (setuptools)
- Has GitHub Actions workflow template ready (OIDC)
- No surprises about dependency conflicts or build issues
- **Result:** 1-2 day packaging work completes smoothly, production release ready

---

## Task 6: Audit Current Documentation Gaps

**Priority:** High  
**Estimated Time:** 2 hours  
**Deadline:** Before Sprint 5 Day 1  
**Owner:** Documentation team

### Objective

Identify documentation gaps and prioritize for Sprint 5 Priority 5 (Documentation Polish).

### Why This Matters

Sprint 5 Priority 5 (days 9-10) will create:
- Tutorial for beginners
- FAQ section
- Troubleshooting guide
- API reference

Need to audit existing docs to avoid duplication and identify gaps.

### Current Documentation (from codebase)

#### Existing Files
- **README.md** - Project overview, installation, quick start, sprint progress
- **USER_GUIDE.md** - User-facing guide (assumed exists)
- **docs/planning/** - Sprint plans, retrospectives, known unknowns
- **docs/research/** - Min/max reformulation research
- **docs/testing/** - Edge case matrix (Sprint 4)
- **docs/architecture/** - (Check if exists)
- **docs/development/** - Error messages guide (Sprint 4)

#### Missing or Incomplete
- **TUTORIAL.md** - Step-by-step beginner guide (NOT EXISTS)
- **FAQ.md** - Common questions (NOT EXISTS)
- **TROUBLESHOOTING.md** - Error reference (mentioned in Sprint 4, check status)
- **API Reference** - Auto-generated from docstrings (NOT EXISTS)
- **CONTRIBUTING.md** - Contribution guide (check if exists)
- **CHANGELOG.md** - Exists, but verify up to date

### Implementation Steps

#### Step 1: Inventory Existing Documentation (30 min)

```bash
# List all documentation files
find docs -name "*.md" | sort

# Check key user-facing docs
ls -lh README.md USER_GUIDE.md CONTRIBUTING.md CHANGELOG.md

# Check docstring coverage
grep -r "def " src/ | wc -l  # Total functions
grep -r '"""' src/ | wc -l   # Total docstrings
# Estimate coverage ratio
```

Create inventory:

```markdown
# Documentation Inventory (Pre-Sprint 5)

## User-Facing Documentation

| Document | Status | Completeness | Last Updated | Needs Update |
|----------|--------|--------------|--------------|--------------|
| README.md | ✅ Exists | 90% | 2025-11-05 | Minor (post-release) |
| USER_GUIDE.md | ? | ? | ? | Audit needed |
| CHANGELOG.md | ✅ Exists | Current | 2025-11-05 | No |
| TUTORIAL.md | ❌ Missing | 0% | N/A | **CREATE (Priority 5)** |
| FAQ.md | ❌ Missing | 0% | N/A | **CREATE (Priority 5)** |
| TROUBLESHOOTING.md | ? | ? | ? | Audit needed |

## Developer Documentation

| Document | Status | Completeness | Last Updated | Needs Update |
|----------|--------|--------------|--------------|--------------|
| CONTRIBUTING.md | ? | ? | ? | Audit needed |
| docs/architecture/OVERVIEW.md | ? | ? | ? | Audit needed |
| docs/development/ERROR_MESSAGES.md | ✅ Exists | 100% | Sprint 4 | No |
| docs/testing/EDGE_CASE_MATRIX.md | ✅ Exists | 100% | Sprint 4 | No |

## API Reference

| Component | Docstring Coverage | Status |
|-----------|-------------------|--------|
| src/ir/ | ?% | Audit needed |
| src/ad/ | ?% | Audit needed |
| src/kkt/ | ?% | Audit needed |
| src/emit/ | ?% | Audit needed |
| src/cli.py | ?% | Audit needed |

**Overall API Coverage:** ?% (Target for Sprint 5: 90%+)
```

#### Step 2: Identify User Pain Points (30 min)

Review Sprint 4 retrospective and imagine common user questions:

**Installation:**
- "How do I install nlp2mcp?" → README has this, but is it clear?
- "What Python version do I need?" → Check if documented
- "Do I need GAMS installed?" → Clarify (only for solve validation)

**Getting Started:**
- "How do I convert my first NLP?" → Need step-by-step TUTORIAL
- "What GAMS features are supported?" → Should be in FAQ
- "Can I see example input/output?" → Need more examples

**Troubleshooting:**
- "I get 'Variable x not found' - what does this mean?" → Need error reference
- "My model fails to convert - how do I debug?" → Need diagnostic procedure
- "PATH solver says infeasible - is my MCP wrong?" → Need MCP debugging guide

**Advanced Usage:**
- "How do I handle large models?" → Need performance tips in FAQ
- "Can I use this in automated pipeline?" → Need API usage examples
- "How do I contribute?" → Need CONTRIBUTING.md

#### Step 3: Prioritize Documentation Tasks (30 min)

Create prioritized list for Sprint 5 Priority 5:

```markdown
# Sprint 5 Priority 5 Documentation Tasks

## Must Have (Day 9)
1. **TUTORIAL.md** - Step-by-step beginner guide
   - Estimated time: 3-4 hours
   - Audience: New users, no MCP background
   - Content: Installation → First conversion → Understanding output → Next steps

2. **FAQ.md** - 20+ common questions
   - Estimated time: 2-3 hours
   - Audience: All users
   - Content: 
     - What is nlp2mcp?
     - What NLP formats supported?
     - What solvers can use MCP output?
     - Performance expectations
     - Troubleshooting quick hits

3. **Enhance TROUBLESHOOTING.md** - Error reference
   - Estimated time: 2 hours
   - Audience: Users encountering errors
   - Content:
     - Common error messages and fixes
     - Diagnostic procedures
     - When to file bug report

## Should Have (Day 10)
4. **API Reference (Sphinx)** - Auto-generated docs
   - Estimated time: 3-4 hours (setup + docstring improvements)
   - Audience: Advanced users, integrators
   - Content:
     - Set up Sphinx
     - Improve docstring coverage to 90%+
     - Generate HTML API docs
     - Host on Read the Docs or GitHub Pages

5. **CONTRIBUTING.md** - Contribution guide
   - Estimated time: 1-2 hours
   - Audience: Potential contributors
   - Content:
     - How to set up dev environment
     - How to run tests
     - Code style guidelines
     - PR process

## Nice to Have (If time permits)
6. **ARCHITECTURE.md** - System architecture overview
7. **EXAMPLES.md** - Gallery of example conversions
8. **PERFORMANCE.md** - Performance tuning guide
```

#### Step 4: Create Documentation Style Guide (30 min)

Ensure consistency across new docs:

```markdown
# Documentation Style Guide

## Tone
- Friendly but professional
- Active voice ("Convert your model" not "Models can be converted")
- Clear and concise
- Avoid jargon (or define when necessary)

## Structure
- Start with "What" and "Why" before "How"
- Use concrete examples
- Include expected output
- Link to related documentation

## Formatting
- Use markdown consistently
- Code blocks with language tags: ```python, ```gams, ```bash
- Use tables for comparisons
- Use callouts for warnings/notes: **Note:**, **Warning:**

## Examples
- Always show complete, runnable examples
- Include both input and expected output
- Use realistic but simple models
- Explain what the example demonstrates

## Cross-References
- Link to related docs
- Keep links relative for portability
- Update all cross-references when moving docs
```

### Deliverable

**File:** `docs/planning/SPRINT_5/DOCUMENTATION_AUDIT.md`

**Contents:**
- Inventory of existing documentation
- Identified gaps
- Prioritized task list for Sprint 5 Priority 5
- Time estimates for each task
- Documentation style guide

### Acceptance Criteria

- [x] All existing documentation inventoried
- [x] Completeness of each doc assessed
- [x] User pain points identified (10+ scenarios)
- [x] Documentation tasks prioritized (must/should/nice to have)
- [x] Time estimates provided for each task
- [x] Style guide created for consistency
- [x] DOCUMENTATION_AUDIT.md created

### Expected Outcome

**Sprint 5 Day 9 morning:**
- Developer starts documentation work
- Has clear priorities (TUTORIAL, FAQ, TROUBLESHOOTING)
- Knows estimated time for each task
- Has style guide for consistency
- No duplication of existing docs
- **Result:** 2 days of documentation work is well-organized and completes all must-haves

---

## Task 7: Set Up Sphinx Documentation Environment

**Priority:** Medium  
**Estimated Time:** 2 hours  
**Deadline:** Before Sprint 5 Day 9  
**Owner:** Documentation team  
**Dependencies:** Task 6 (Documentation audit)

### Objective

Set up Sphinx for auto-generating API reference documentation from docstrings.

### Why This Matters

Sprint 5 Priority 5.4 includes creating API reference documentation. Sphinx setup can be time-consuming if done during sprint. Set up infrastructure early.

### Implementation Steps

#### Step 1: Install Sphinx and Extensions (20 min)

```bash
# Install Sphinx and common extensions
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints

# Add to pyproject.toml optional dependencies
[project.optional-dependencies]
docs = [
    "sphinx>=7.0",
    "sphinx-rtd-theme>=1.0",
    "sphinx-autodoc-typehints>=1.0",
]

# Install dev dependencies
pip install -e ".[docs]"
```

#### Step 2: Install Sphinx and Extensions (20 min)

```bash
# Create docs directory (if not exists)
mkdir -p docs/api

# Run sphinx-quickstart
cd docs/api
sphinx-quickstart

# Prompts:
# > Separate source and build directories? y
# > Project name: nlp2mcp
# > Author name: [Your name]
# > Project release: 0.4.0
# > Project language: en
```

#### Step 3: Configure Sphinx (40 min)

Edit `docs/api/source/conf.py`:

```python
# docs/api/source/conf.py

import os
import sys
sys.path.insert(0, os.path.abspath('../../..'))  # Point to src/

project = 'nlp2mcp'
copyright = '2025, nlp2mcp contributors'
author = 'nlp2mcp contributors'
release = '0.4.0'

# Extensions
extensions = [
    'sphinx.ext.autodoc',        # Auto-generate from docstrings
    'sphinx.ext.napoleon',       # Support Google/NumPy docstring styles
    'sphinx.ext.viewcode',       # Add source code links
    'sphinx.ext.intersphinx',    # Link to other projects (e.g., Python docs)
    'sphinx_autodoc_typehints',  # Better type hint rendering
]

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

# Napoleon settings (for Google-style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = True

# Theme
html_theme = 'sphinx_rtd_theme'

# Intersphinx mapping (link to Python docs)
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
}
```

#### Step 4: Create API Documentation Structure (30 min)

```bash
# Create API reference pages
cat > docs/api/source/api.rst << 'EOF'
API Reference
=============

.. toctree::
   :maxdepth: 2

   api/ir
   api/ad
   api/kkt
   api/emit
   api/cli

EOF

# Create module pages
mkdir -p docs/api/source/api

cat > docs/api/source/api/ir.rst << 'EOF'
IR Module
=========

.. automodule:: src.ir.model
   :members:

.. automodule:: src.ir.parser
   :members:

.. automodule:: src.ir.normalize
   :members:
EOF

# Similar for other modules...
```

#### Step 5: Test Documentation Build (10 min)

```bash
# Build HTML docs
cd docs/api
make html

# Expected: Successful build with some warnings about missing docstrings

# View docs
open build/html/index.html

# Verify:
# - Index page loads
# - API reference page exists
# - Modules are documented
# - Type hints are rendered
```

### Deliverable

**Files Created:**
- `docs/api/source/conf.py` - Sphinx configuration
- `docs/api/source/index.rst` - Documentation homepage
- `docs/api/source/api.rst` - API reference index
- `docs/api/source/api/*.rst` - Per-module documentation
- `docs/api/Makefile` - Build commands

**Documentation:**
- Build instructions in README or docs/development/
- Style guide for docstrings (Google style)

### Acceptance Criteria

- [x] Sphinx installed with required extensions
- [x] Sphinx project initialized in `docs/api/`
- [x] Configuration complete (autodoc, napoleon, theme)
- [x] API reference structure created (ir, ad, kkt, emit, cli)
- [x] Documentation builds successfully (`make html`)
- [x] HTML output viewable and correctly formatted
- [x] Build instructions documented

### Expected Outcome

**Sprint 5 Day 9-10:**
- Developer working on API documentation
- Sphinx already configured and working
- Can focus on improving docstrings, not setup
- Can see live preview of documentation
- **Result:** API reference completion is straightforward, no tool setup delays

---

## Task 8: Create Large Model Test Fixtures

**Priority:** Medium  
**Estimated Time:** 3 hours  
**Deadline:** Before Sprint 5 Day 4  
**Owner:** Development team

### Objective

Create large model test fixtures for Sprint 5 Priority 3 production hardening (large model testing, memory optimization).

### Why This Matters

Sprint 5 Priority 3.2 includes testing with 1,000+ and 10,000+ variable models. These models need to be generated and validated before hardening work begins.

Current benchmark suite has model generators, but not validated for correctness or realism.

### Implementation Steps

#### Step 1: Create Model Generator Script (1 hour)

```python
# tests/fixtures/generate_large_models.py

"""
Generate large test models for production hardening.

Models are realistic (not just random), with typical optimization structures:
- Resource allocation problems
- Network flow problems
- Production planning problems
"""

from pathlib import Path
from typing import Literal

def generate_resource_allocation(
    output_path: Path,
    num_resources: int,
    num_tasks: int,
) -> Path:
    """
    Generate resource allocation NLP.

    minimize sum over tasks: cost(task, resource_allocation)
    s.t. sum over tasks: resource_usage(task, r) <= available(r) for each resource
         resource_allocation(task) >= 0

    This is a realistic structure for production optimization problems.
    """
    content = [f"* Resource Allocation Problem: {num_tasks} tasks, {num_resources} resources\n\n"]

    # Sets
    content.append(f"Sets\n")
    content.append(f"    tasks /task1*task{num_tasks}/\n")
    content.append(f"    resources /res1*res{num_resources}/\n")
    content.append(f";\n\n")

    # Parameters
    content.append("Parameters\n")
    content.append("    capacity(resources) / ")
    content.append(", ".join([f"res{i} {100 + i*10}" for i in range(1, num_resources+1)]))
    content.append(" /\n")
    content.append("    usage(tasks, resources) / ")
    # Sparse usage matrix (each task uses ~3 resources)
    usage_pairs = []
    for t in range(1, num_tasks+1):
        for r in range(1, min(4, num_resources+1)):
            usage_pairs.append(f"task{t}.res{r} {1 + (t+r) % 3}")
    content.append(", ".join(usage_pairs))
    content.append(" /\n")
    content.append(";\n\n")

    # Variables
    content.append("Variables\n")
    content.append("    x(tasks) allocation amount\n")
    content.append("    obj objective value\n")
    content.append(";\n\n")

    content.append("Positive Variable x;\n\n")

    # Equations
    content.append("Equations\n")
    content.append("    objdef objective definition\n")
    content.append("    capacity_constraint(resources) capacity limits\n")
    content.append(";\n\n")

    # Objective: sum over tasks of quadratic cost
    content.append("objdef.. obj =e= sum(tasks, x(tasks)*x(tasks)) + sum(tasks, 10*x(tasks));\n\n")

    # Constraints: resource capacity
    content.append("capacity_constraint(resources)..\n")
    content.append("    sum(tasks, usage(tasks, resources) * x(tasks)) =l= capacity(resources);\n\n")

    # Model
    content.append("Model resource_allocation /all/;\n")
    content.append("Solve resource_allocation using NLP minimizing obj;\n")

    output_path.write_text(''.join(content))
    return output_path


def generate_network_flow(
    output_path: Path,
    num_nodes: int,
    num_arcs: int,
) -> Path:
    """
    Generate network flow optimization.

    minimize sum over arcs: cost(arc) * flow(arc)^2
    s.t. flow_balance(node): inflow - outflow = supply(node)
         flow(arc) >= 0

    Realistic structure for logistics/transport problems.
    """
    content = [f"* Network Flow Problem: {num_nodes} nodes, {num_arcs} arcs\n\n"]

    # Sets
    content.append("Sets\n")
    content.append(f"    nodes /n1*n{num_nodes}/\n")
    content.append(f"    arcs /a1*a{num_arcs}/\n")
    content.append(";\n\n")

    # Parameters (simplified - each arc connects sequential nodes)
    content.append("Parameters\n")
    content.append("    supply(nodes) /")
    supply = [f"n{i} {10 if i == 1 else (-10 if i == num_nodes else 0)}" 
              for i in range(1, num_nodes+1)]
    content.append(", ".join(supply))
    content.append("/\n")
    content.append("    cost(arcs) /")
    costs = [f"a{i} {1 + i % 5}" for i in range(1, num_arcs+1)]
    content.append(", ".join(costs))
    content.append("/\n")
    content.append(";\n\n")

    # Variables
    content.append("Variables\n")
    content.append("    flow(arcs) flow on arcs\n")
    content.append("    obj objective value\n")
    content.append(";\n\n")

    content.append("Positive Variable flow;\n\n")

    # Equations (simplified for demonstration)
    content.append("Equations\n")
    content.append("    objdef\n")
    content.append(";\n\n")

    content.append("objdef.. obj =e= sum(arcs, cost(arcs)*flow(arcs)*flow(arcs));\n\n")

    # Model
    content.append("Model network_flow /all/;\n")
    content.append("Solve network_flow using NLP minimizing obj;\n")

    output_path.write_text(''.join(content))
    return output_path


def generate_all_test_models():
    """Generate all large model test fixtures."""
    fixtures_dir = Path(__file__).parent / "large_models"
    fixtures_dir.mkdir(exist_ok=True)

    models = [
        # Medium models (baseline)
        ("resource_allocation_medium.gms", "resource_allocation", 
         {"num_resources": 20, "num_tasks": 100}),
        
        # Large models (1,000 scale)
        ("resource_allocation_large.gms", "resource_allocation",
         {"num_resources": 50, "num_tasks": 1000}),
        ("network_flow_large.gms", "network_flow",
         {"num_nodes": 500, "num_arcs": 1000}),
        
        # Very large models (10,000 scale)
        ("resource_allocation_xlarge.gms", "resource_allocation",
         {"num_resources": 100, "num_tasks": 10000}),
        ("network_flow_xlarge.gms", "network_flow",
         {"num_nodes": 5000, "num_arcs": 10000}),
    ]

    for filename, generator_name, kwargs in models:
        output_path = fixtures_dir / filename
        if generator_name == "resource_allocation":
            generate_resource_allocation(output_path, **kwargs)
        elif generator_name == "network_flow":
            generate_network_flow(output_path, **kwargs)
        print(f"Generated: {output_path}")

    return fixtures_dir


if __name__ == "__main__":
    fixtures_dir = generate_all_test_models()
    print(f"\nAll large model fixtures generated in: {fixtures_dir}")
    print("\nTo test:")
    print(f"  nlp2mcp {fixtures_dir}/resource_allocation_medium.gms -o /tmp/out.gms")
```

#### Step 2: Generate and Validate Models (1 hour)

```bash
# Generate all test models
python tests/fixtures/generate_large_models.py

# Validate medium model (should convert successfully)
nlp2mcp tests/fixtures/large_models/resource_allocation_medium.gms -o /tmp/medium_mcp.gms

# Time conversion
time nlp2mcp tests/fixtures/large_models/resource_allocation_large.gms -o /tmp/large_mcp.gms
# Expected: < 10 seconds (if longer, note as optimization target)

# Check memory usage
/usr/bin/time -l nlp2mcp tests/fixtures/large_models/resource_allocation_xlarge.gms -o /tmp/xlarge_mcp.gms
# Note peak memory usage

# Verify GAMS syntax
gams /tmp/medium_mcp.gms --compile-only
# Expected: Compilation succeeds (or document errors)
```

#### Step 3: Create Test Suite for Large Models (1 hour)

```python
# tests/production/test_large_models.py

"""
Production hardening tests for large models.

Tests that nlp2mcp can handle realistic large-scale problems.
"""

import pytest
from pathlib import Path
import subprocess
import time
import tracemalloc

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "large_models"

class TestLargeModelHandling:
    """Test nlp2mcp handles large models correctly."""

    def test_medium_model_converts(self):
        """Test: 100-variable model converts successfully."""
        model = FIXTURES_DIR / "resource_allocation_medium.gms"
        output = Path("/tmp/test_medium_mcp.gms")

        result = subprocess.run(
            ['nlp2mcp', str(model), '-o', str(output)],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, f"Conversion failed: {result.stderr}"
        assert output.exists()
        assert output.stat().st_size > 0

    @pytest.mark.slow
    def test_large_model_converts(self):
        """Test: 1,000-variable model converts in reasonable time."""
        model = FIXTURES_DIR / "resource_allocation_large.gms"
        output = Path("/tmp/test_large_mcp.gms")

        start = time.time()
        result = subprocess.run(
            ['nlp2mcp', str(model), '-o', str(output)],
            capture_output=True,
            text=True,
            timeout=120
        )
        elapsed = time.time() - start

        assert result.returncode == 0
        assert elapsed < 30, f"Conversion too slow: {elapsed:.1f}s"

    @pytest.mark.slow
    def test_xlarge_model_memory_usage(self):
        """Test: 10,000-variable model uses acceptable memory."""
        model = FIXTURES_DIR / "resource_allocation_xlarge.gms"
        output = Path("/tmp/test_xlarge_mcp.gms")

        tracemalloc.start()

        result = subprocess.run(
            ['nlp2mcp', str(model), '-o', str(output)],
            capture_output=True,
            text=True,
            timeout=300
        )

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak / 1024 / 1024

        assert result.returncode == 0, f"Conversion failed: {result.stderr}"
        assert peak_mb < 500, f"Memory usage too high: {peak_mb:.1f} MB"

        print(f"\n10K variable model: {peak_mb:.1f} MB peak memory")
```

### Deliverable

**Files Created:**
- `tests/fixtures/generate_large_models.py` - Model generators
- `tests/fixtures/large_models/*.gms` - 3 test models (250, 500, 1K variables)
- `tests/production/test_large_models.py` - Large model test suite

**Documentation:**
- README in `tests/fixtures/large_models/` explaining each model with performance baselines

**Regeneration (2025-11-06):**
- Updated to leverage newly added asterisk notation support
- Increased model sizes from (10, 50, 100) to (250, 500, 1K) variables
- Added comprehensive performance baselines

### Acceptance Criteria

- [x] Model generator script created with resource allocation model type
- [x] 3 test models generated (250 vars, 500 vars, 1K vars) - updated 2025-11-06
- [x] Models use asterisk notation for sets (e.g., `i /i1*i1000/`)
- [x] Models use long comma-separated parameter lists
- [x] 250-var model validated (converts successfully in ~5.1s)
- [x] 500-var model conversion timed (baseline: ~13.5s)
- [x] 1K-var model conversion timed (baseline: ~45.9s)
- [x] Performance metrics documented in README with scaling analysis
- [x] Test suite created with 4 large model tests
- [x] README documenting test models and performance baselines
- [x] All tests passing with appropriate timeouts

### Expected Outcome

**Sprint 5 Day 4 morning:**
- Developer starts production hardening work
- Has ready-to-use large model test fixtures
- Has baseline performance metrics (time, memory)
- Can immediately test optimizations
- **Result:** No delays creating test data, focus on actual hardening work

---

## Task 9: Review Sprint 4 Retrospective Action Items

**Priority:** High  
**Estimated Time:** 1 hour  
**Deadline:** Before Sprint 5 Day 1  
**Owner:** Sprint planning

### Objective

Review Sprint 4 Retrospective to ensure all action items and recommendations are captured in Sprint 5 planning.

### Why This Matters

Sprint 4 Retrospective identified improvements and issues to address. Need to verify Sprint 5 priorities align with those recommendations.

### Implementation Steps

#### Step 1: Review Sprint 4 Retrospective (20 min)

Read `docs/planning/SPRINT_4/RETROSPECTIVE.md` and extract:
- Action items
- Technical debt identified
- Recommendations
- Known issues to fix

#### Step 2: Map to Sprint 5 Priorities (20 min)

Create mapping:

| Sprint 4 Recommendation | Sprint 5 Priority | Day | Status |
|-------------------------|-------------------|-----|--------|
| Fix min/max reformulation bug | Priority 1 | Days 1-2 | ✅ Planned |
| Complete PATH validation | Priority 2 | Day 3 | ✅ Planned |
| Large model testing | Priority 3.2 | Days 4-6 | ✅ Planned |
| Memory optimization | Priority 3.3 | Days 4-6 | ✅ Planned |
| Error recovery | Priority 3.1 | Days 4-6 | ✅ Planned |
| PyPI packaging | Priority 4 | Days 7-8 | ✅ Planned |
| Tutorial creation | Priority 5.1 | Days 9-10 | ✅ Planned |
| FAQ creation | Priority 5.2 | Days 9-10 | ✅ Planned |

#### Step 3: Identify Any Gaps (10 min)

Check if any recommendations not captured in Sprint 5:
- Scan retrospective for "should do", "consider", "recommended"
- Verify all technical debt items addressed or documented
- Check if any "What Could Have Gone Better" items need action

#### Step 4: Update Sprint 5 Plan if Needed (10 min)

If gaps found:
- Add to Sprint 5 priorities (or defer to Sprint 6 with justification)
- Update PLAN.md with additional tasks
- Adjust time estimates if needed

### Deliverable

**File:** `docs/planning/SPRINT_5/RETROSPECTIVE_ALIGNMENT.md`

**Contents:**
- Mapping of Sprint 4 recommendations to Sprint 5 tasks
- Confirmation all critical items addressed
- Deferred items with justification
- Any additional tasks identified

### Acceptance Criteria

- [x] Sprint 4 Retrospective reviewed completely
- [x] All action items mapped to Sprint 5 priorities
- [x] Any gaps identified and addressed
- [x] Deferred items documented with justification
- [x] RETROSPECTIVE_ALIGNMENT.md created

### Expected Outcome

Confidence that Sprint 5 addresses all learnings from Sprint 4, no overlooked action items.

---

## Task 10: Plan Sprint 5 Scope and Schedule

**Priority:** Critical  
**Estimated Time:** 4 hours  
**Deadline:** Before Sprint 5 Day 1  
**Owner:** Sprint planning  
**Dependencies:** All prep tasks

### Objective

Create detailed Sprint 5 plan incorporating all prep work and known unknowns research.

### Why This Matters

Comprehensive plan prevents mid-sprint surprises and ensures all priorities complete in 10 days.

### Deliverable

**File:** `docs/planning/SPRINT_5/PLAN.md`

### Required Sections

1. **Sprint Goals** (from PROJECT_PLAN.md Sprint 5)
2. **Day-by-Day Plan** (Days 1-10)
3. **Integration Risks** (per day)
4. **Complexity Estimates** (per day)
5. **Known Unknowns Reference** (link to KNOWN_UNKNOWNS.md)
6. **Checkpoint Schedule** (Days 3, 6, 8)
7. **Acceptance Criteria** (per priority)
8. **Contingency Plans** (if tasks run over)

### Tentative Schedule

**Priority 1: Fix Min/Max Bug (Days 1-2)**
- Day 1: Implement Strategy 2 (Direct Constraints) for objective-defining min/max
- Day 2: Add test cases, verify PATH solutions, update documentation

**Priority 2: PATH Validation (Day 3)**
- Regenerate golden MCP files with correct formulation
- Run full PATH validation suite
- Document any issues found
- **Checkpoint 1: End of Day 3**

**Priority 3: Production Hardening (Days 4-6)**
- Day 4: Large model testing (1K, 10K variables), identify bottlenecks
- Day 5: Memory optimization, error recovery improvements
- Day 6: Edge case testing, numerical robustness
- **Checkpoint 2: End of Day 6**

**Priority 4: PyPI Packaging (Days 7-8)**
- Day 7: Validate build, enhance pyproject.toml, test wheel
- Day 8: Release automation, TestPyPI publish, final release
- **Checkpoint 3: End of Day 8**

**Priority 5: Documentation (Days 9-10)**
- Day 9: TUTORIAL.md, FAQ.md, TROUBLESHOOTING.md
- Day 10: API reference (Sphinx), polish, final review

### Lessons Applied from Sprint 4

1. ✅ Known unknowns created proactively (Task 1)
2. ✅ Critical unknowns researched before sprint (Task 2)
3. ✅ Validation environment verified (Task 3)
4. ✅ Performance baselines established (Task 4)
5. ✅ Packaging strategy researched (Task 5)
6. ✅ Documentation gaps identified (Task 6)
7. ✅ Infrastructure setup complete (Tasks 7-8)
8. ✅ Retrospective action items confirmed (Task 9)

### Acceptance Criteria

- [ ] Plan created with all required sections
- [ ] All 10 days have detailed tasks
- [ ] All days have integration risks documented
- [ ] All days have complexity estimates
- [ ] Known unknowns list referenced
- [ ] Checkpoint schedule defined (Days 3, 6, 8)
- [ ] Acceptance criteria for each priority documented
- [ ] Contingency plans for delays documented

### Expected Outcome

**Sprint 5 Day 1 morning:**
- Team has comprehensive 10-day plan
- All unknowns researched
- All infrastructure ready
- Clear acceptance criteria
- **Result:** Sprint 5 executes smoothly, all priorities complete, production release ready

---

## Summary and Critical Path

### Critical Path (Must Complete Before Sprint 5 Day 1)

1. ✅ **Task 1: Known Unknowns** (COMPLETE - Nov 5)
2. **Task 2: Research Min/Max Strategies** (4-6 hours) - CRITICAL
3. **Task 3: Validate PATH Environment** (2 hours) - CRITICAL
4. **Task 10: Plan Sprint 5** (4 hours) - CRITICAL

**Total Critical Path Time:** ~10-12 hours (1.5-2 working days)

### High Priority (Should Complete Before Sprint 5)

4. **Task 4: Performance Baselines** (3 hours)
5. **Task 5: PyPI Packaging Survey** (3 hours)
6. **Task 6: Documentation Audit** (2 hours)
9. **Task 9: Review Retrospective** (1 hour)

**Total High Priority Time:** ~9 hours (1 working day)

### Medium Priority (Nice to Have, or Complete by Mid-Sprint)

7. **Task 7: Sphinx Setup** (2 hours) - Can do by Day 9
8. **Task 8: Large Model Fixtures** (3 hours) - Can do by Day 4

**Total Medium Priority Time:** ~5 hours

### Overall Prep Time: 26-29 hours (~3-4 working days)

---

## Prep Week Schedule

Suggested schedule for completing prep tasks:

**Day -4 (Monday):**
- ✅ Task 1: Known Unknowns (COMPLETE)
- Task 9: Review Sprint 4 Retrospective (1 hour)
- Task 6: Documentation Audit (2 hours)

**Day -3 (Tuesday):**
- Task 2: Research Min/Max Strategies (4-6 hours) - CRITICAL
- Task 3: Validate PATH Environment (2 hours)

**Day -2 (Wednesday):**
- Task 4: Performance Baselines (3 hours)
- Task 5: PyPI Packaging Survey (3 hours)

**Day -1 (Thursday):**
- Task 7: Sphinx Setup (2 hours)
- Task 8: Large Model Fixtures (3 hours)
- Task 10: Plan Sprint 5 (4 hours)

**Day 0 (Friday):**
- Buffer day for any overruns
- Final review of all prep work
- Team readiness check

**Sprint 5 Day 1 (Monday):** 🚀 Sprint begins with all prep complete

---

## Success Criteria for Prep Phase

- [x] ✅ Known Unknowns document created (22 unknowns, 5 categories)
- [ ] All Critical unknowns researched and resolved
- [ ] PATH solver environment validated and ready
- [ ] Performance baselines documented
- [ ] PyPI packaging strategy defined
- [ ] Documentation gaps identified and prioritized
- [ ] Sphinx environment ready for API docs
- [ ] Large model test fixtures generated
- [ ] Sprint 4 retrospective action items confirmed
- [ ] Sprint 5 PLAN.md completed with 10-day schedule

**Overall Goal:** No blockers, no surprises, high-confidence sprint start

---

## Notes and Risks

### Key Differences from Sprint 4 Prep

1. **Known Unknowns already done** (Task 1 ✅) - Saves 2-3 hours
2. **Min/max bug research is critical** - Could reveal unexpected complexity
3. **PATH validation is critical** - Must work for production release
4. **PyPI packaging is new** - Need to learn modern standards
5. **Documentation is major focus** - 2 full days in sprint

### Potential Risks

1. **Risk:** Min/max research reveals Strategy 2 doesn't work for all cases
   - **Mitigation:** Task 2 includes testing all edge cases
   - **Contingency:** Have Strategy 3 (general fix) ready as backup

2. **Risk:** PATH validation finds fundamental MCP formulation issues
   - **Mitigation:** Task 3 validates environment early
   - **Contingency:** Allocate extra day to Priority 2 if needed

3. **Risk:** PyPI packaging has unexpected dependency conflicts
   - **Mitigation:** Task 5 includes build testing before sprint
   - **Contingency:** Use TestPyPI first, delay prod release if needed

4. **Risk:** Documentation takes longer than 2 days
   - **Mitigation:** Task 6 prioritizes must-have vs nice-to-have
   - **Contingency:** TUTORIAL and FAQ are must-have, API docs can be post-release

### Sprint 5 Success Definition

**Minimum Success (B Grade):**
- ✅ Min/max bug fixed and tested
- ✅ PATH validation passing
- ✅ Package on PyPI
- ✅ TUTORIAL.md exists

**Target Success (A Grade):**
- ✅ All 5 priorities complete
- ✅ Large model testing done
- ✅ Full documentation suite
- ✅ Zero critical bugs

**Exceptional Success (A+ Grade):**
- ✅ All of above
- ✅ Performance optimizations exceed targets
- ✅ API documentation on Read the Docs
- ✅ User testimonials/case studies

---

**END OF SPRINT 5 PREP PLAN**
