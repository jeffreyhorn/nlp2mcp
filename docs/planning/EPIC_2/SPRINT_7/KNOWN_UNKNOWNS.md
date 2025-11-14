# Sprint 7 Known Unknowns

**Created:** November 14, 2025  
**Status:** Active - Pre-Sprint 7  
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 7 parser enhancements, test performance optimization, convexity refinements, and CI/CD improvements

---

## Overview

This document identifies all assumptions and unknowns for Sprint 7 features **before** implementation begins. This proactive approach continues the highly successful methodology from Sprint 4, 5, and 6 that prevented late-stage surprises.

**Sprint 7 Scope:**
1. Parser Enhancements (Wave 1) - Preprocessor directives, multi-dimensional indexing, priority syntax gaps
2. Test Performance Optimization - Profiling, parallelization, CI optimization
3. Convexity Refinements - Line number tracking, fine-grained suppression
4. CI/CD Improvements - Automated GAMSLib dashboard updates, regression detection

**Reference:** See `docs/planning/EPIC_2/PROJECT_PLAN.md` lines 45-92 for complete Sprint 7 deliverables and acceptance criteria.

**Lessons from Previous Sprints:** The Known Unknowns process achieved excellent results:
- Sprint 4: 23 unknowns, zero blocking issues
- Sprint 5: 22 unknowns, all resolved on schedule  
- Sprint 6: 22 unknowns, enabled realistic scope setting (10% GAMSLib parse rate baseline)

**Sprint 6 Key Learning:** Parser complexity was underestimated - only 10% parse rate achieved (1 out of 10 models parsed successfully) due to preprocessor directive gaps. Sprint 7 requires even more thorough analysis of parser internals and GAMSLib syntax requirements.

---

## How to Use This Document

### Before Sprint 7 Day 1
1. Research and verify all **Critical** and **High** priority unknowns
2. Create minimal test cases for validation
3. Document findings in "Verification Results" sections
4. Update status: 🔍 INCOMPLETE -> [x] COMPLETE or ❌ WRONG (with correction)

### During Sprint 7
1. Review daily during standup
2. Add newly discovered unknowns
3. Update with implementation findings
4. Move resolved items to "Confirmed Knowledge"

### Priority Definitions
- **Critical:** Wrong assumption will break core functionality or require major refactoring (>8 hours)
- **High:** Wrong assumption will cause significant rework (4-8 hours)
- **Medium:** Wrong assumption will cause minor issues (2-4 hours)
- **Low:** Wrong assumption has minimal impact (<2 hours)

---

## Summary Statistics

**Total Unknowns:** 25  
**By Priority:**
- Critical: 6 (unknowns that could derail sprint or prevent 30% parse rate goal)
- High: 10 (unknowns requiring upfront research)
- Medium: 6 (unknowns that can be resolved during implementation)
- Low: 3 (nice-to-know, low impact)

**By Category:**
- Category 1 (Parser Enhancements): 11 unknowns
- Category 2 (Test Performance): 6 unknowns
- Category 3 (GAMSLib Integration): 4 unknowns
- Category 4 (Convexity Refinements): 3 unknowns
- Category 5 (CI/CD): 1 unknown

**Estimated Research Time:** 28-36 hours (exceeds 24-32 hour target; spread across prep phase)

---

## Table of Contents

1. [Category 1: Parser Enhancements](#category-1-parser-enhancements)
2. [Category 2: Test Performance](#category-2-test-performance)
3. [Category 3: GAMSLib Integration](#category-3-gamslib-integration)
4. [Category 4: Convexity Refinements](#category-4-convexity-refinements)
5. [Category 5: CI/CD](#category-5-cicd)

---

# Category 1: Parser Enhancements

## Unknown 1.1: Should we implement full preprocessing or mock directive handling?

### Priority
**Critical** - Affects 9/10 failed GAMSLib models, core to 30% parse rate goal

### Assumption
Mock/skip handling of preprocessor directives (`$if`, `$set`, `$include`) is sufficient to parse most GAMSLib models without implementing full GAMS preprocessing.

### Research Questions
1. Can we parse models by recognizing and skipping directives without evaluating them?
2. What happens if we ignore `$if` conditionals - do we parse both branches or assume true branch?
3. Can we handle `$include` by attempting to parse the included file if it exists?
4. Are there preprocessor directives that MUST be evaluated for semantic correctness?
5. How many GAMSLib failures are due to directives vs other missing syntax features?

### How to Verify

**Test Case 1: Simple $set directive**
```gams
$set size 10
Set i /1*%size%/;
```
Expected: Parser recognizes `$set` and either skips it or stores value for macro expansion

**Test Case 2: Conditional $if**
```gams
$if not set size $set size 10
Set i /1*10/;
```
Expected: Parser skips `$if` line or assumes condition is true

**Test Case 3: File inclusion**
```gams
$include data.gms
```
Expected: Parser attempts to load and parse data.gms or skips directive with warning

**Test Case 4: Nested conditionals**
```gams
$if set debug
  $set verbose 1
$endif
```
Expected: Parser handles nested directives or fails gracefully

### Risk if Wrong
- **Mock approach insufficient:** May need full preprocessing, requiring 2-3 weeks of additional work
- **Semantic incorrectness:** Skipping directives may produce wrong AST (e.g., missing conditional code)
- **30% parse rate unachievable:** If directives are pervasive and complex

### Estimated Research Time
8-10 hours (implement prototype, test on 9 failed models, analyze results)

### Owner
Development team (Parser specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.2: Can multi-dimensional indexing be represented in current IR without major refactoring?

### Priority
**Critical** - Required for most real-world GAMS models

### Assumption
Current IR can be extended to support multi-dimensional indexing (e.g., `A(i,j,k)`) by changing `Variable(indices=["i"])` to `Variable(indices=["i", "j", "k"])` without breaking normalization or AD.

### Research Questions
1. Does AD module handle multi-dimensional derivatives correctly (partial w.r.t. X(i,j))?
2. Can normalization preserve index semantics when transforming expressions?
3. Do we need index matching logic: ∂A(i,j)/∂X(k,l) = 0 if (i,j) ≠ (k,l)?
4. How does `sum((i,j), A(i,j) * X(i,j))` translate to IR?
5. Are there edge cases with mixed index dimensions: `A(i,j) + B(i)` - valid or error?

### How to Verify

**Test Case 1: 2D parameter**
```gams
Parameter A(i,j);
A(i,j) = i.val + j.val;
```
Expected: IR stores `Parameter(name="A", indices=["i", "j"])`

**Test Case 2: 3D variable in equation**
```gams
Variable X(i,j,k);
Equation eq(i);
eq(i).. sum((j,k), X(i,j,k)) =e= 0;
```
Expected: IR correctly represents nested summation with 3D variable

**Test Case 3: Derivative computation**
```gams
Variable X(i,j);
Equation eq(i);
eq(i).. sum(j, X(i,j)**2) =e= 1;
```
Expected: Derivative ∂eq(i)/∂X(k,l) correctly computed as 2*X(i,j) if (i,j)==(k,l), else 0

### Risk if Wrong
- **Major IR refactoring:** May need to redesign symbol table, expression trees, derivative computation
- **Normalization breaks:** Index semantics lost during transformations
- **Timeline impact:** Could add 1-2 weeks if current approach doesn't scale

### Estimated Research Time
6-8 hours (prototype IR changes, test normalization, check AD module)

### Owner
Development team (IR and AD specialists)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.3: What's the minimum GAMS syntax needed to unlock 2-3 additional GAMSLib models?

### Priority
**High** - Determines feature prioritization for 30% parse rate

### Assumption
Adding 3-4 high-impact syntax features (preprocessor, multi-dim indexing, set ranges, table declarations) will unlock 2-3 additional GAMSLib models, achieving 30% parse rate (3/10 models).

### Research Questions
1. Which models fail on which specific syntax features?
2. Is there a "long tail" where each model needs unique syntax, or do features cluster?
3. Can we achieve 30% by fixing top 3 features, or need 5-6 features?
4. Are there dependencies: e.g., table declarations require multi-dim indexing?
5. What's the ROI curve: effort vs models unlocked?

### How to Verify

**Step 1: Categorize failures**
Analyze all 9 failed models:
- circle.gms → preprocessor (`$if not set`)
- himmel16.gms → set range syntax (`/ 1*6 /`)
- hs62.gms → ?
- mathopt1.gms → ?
- maxmin.gms → ?
- mhw4dx.gms → ?
- mingamma.gms → ?
- rbrock.gms → ?
- trig.gms → ?

**Step 2: Build feature matrix**
| Feature | Models Blocked | Effort | ROI |
|---------|----------------|--------|-----|
| Preprocessor directives | ? | High | ? |
| Set range syntax | ? | Medium | ? |
| Multi-dim indexing | ? | High | ? |
| Table declarations | ? | Medium | ? |

**Step 3: Calculate minimum feature set**
What's the smallest set of features that unlocks ≥3 models?

### Risk if Wrong
- **Overestimate:** Implement 4 features but only unlock 1 model (wasted effort)
- **Underestimate:** Need 6+ features, Sprint 7 scope too small
- **Wrong features:** Prioritize low-ROI features, miss high-ROI ones

### Estimated Research Time
4-6 hours (analyze all failures, categorize by feature, calculate ROI)

### Owner
Development team (Parser specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.4: Does Lark grammar support preprocessor directives or need custom lexer?

### Priority
**High** - Technical feasibility of mock directive approach

### Assumption
Lark grammar can be extended with rules to recognize preprocessor directives without requiring custom lexer modifications.

### Research Questions
1. Can Lark terminals match `$if`, `$set`, etc. as special tokens?
2. Do we need lexer callbacks to skip directive lines?
3. Can grammar rules handle directive arguments: `$set name value`?
4. How to handle multi-line directives: `$ontext ... $offtext`?
5. Does directive recognition interfere with other `$` usage in GAMS?

### How to Verify

**Test Case 1: Add directive terminals**
```lark
DIRECTIVE: "$" ("if"|"set"|"include"|"ontext"|"offtext"|...)
preprocessor_directive: DIRECTIVE /[^\n]*/
```
Expected: Parser recognizes but doesn't fail on directives

**Test Case 2: Multi-line text block**
```gams
$ontext
This is a comment block
that spans multiple lines
$offtext
```
Expected: Lexer skips entire block

**Test Case 3: Inline directive**
```gams
Set i /1*10/;  $set size 10
```
Expected: Parser handles directive mid-line or errors gracefully

### Risk if Wrong
- **Grammar limitations:** May need to drop down to custom lexer (complex, error-prone)
- **Parser conflicts:** Directive syntax may conflict with existing grammar rules
- **Timeline impact:** Custom lexer adds 1-2 weeks

### Estimated Research Time
3-4 hours (prototype grammar changes, test with Lark, check for conflicts)

### Owner
Development team (Parser specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.5: Can we support set range syntax `/ 1*10 /` without breaking existing set declarations?

### Priority
**High** - Appears in multiple GAMSLib models

### Assumption
Set range syntax `Set i / 1*10 /;` can be added to grammar without conflicting with explicit element lists `Set i / el1, el2, el3 /;`.

### Research Questions
1. Can grammar distinguish `1*10` (range) from `el1, el2` (explicit elements)?
2. Is `*` operator ambiguous with multiplication in expressions?
3. How to handle mixed syntax: `Set i / 1*5, extra, 10*15 /;`?
4. Does range syntax extend to sets over sets: `Set ij(i,j) / 1*10.1*10 /;`?
5. Do we need to evaluate ranges at parse time or defer to normalization?

### How to Verify

**Test Case 1: Simple range**
```gams
Set i / 1*10 /;
```
Expected: Parser recognizes as range, stores bounds [1, 10]

**Test Case 2: Multiple ranges**
```gams
Set i / 1*5, 10*15, 20*25 /;
```
Expected: Parser handles multiple range segments

**Test Case 3: Mixed range and explicit**
```gams
Set i / 1*10, special, 20*30 /;
```
Expected: Parser distinguishes range from explicit element "special"

**Test Case 4: Ambiguity check**
```gams
Set i / 2*3 /;  # Is this range [2,3] or element "2*3"?
```
Expected: Grammar rules correctly interpret as range

### Risk if Wrong
- **Grammar ambiguity:** Parser may misinterpret ranges as expressions
- **Regression:** Existing set declarations may break
- **Limited utility:** Range syntax alone may not unlock many models

### Estimated Research Time
3-4 hours (grammar prototype, test on GAMSLib models with ranges)

### Owner
Development team (Parser specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.6: How does multi-dimensional indexing affect KKT stationarity equation generation?

### Priority
**High** - Core correctness of generated MCP

### Assumption
Stationarity equations for multi-dimensional variables `X(i,j)` can be generated by iterating over all index combinations without requiring major changes to KKT module.

### Research Questions
1. Does `build_stationarity_equations()` already handle multi-dim through index product?
2. Do we generate `stat_X(i,j)` or separate equations for each (i,j) pair?
3. How does gradient computation handle ∂F/∂X(i,j) with multiple indices?
4. Are there sparsity implications: large index sets → many stationarity equations?
5. Do bounds apply per-index: `X.lo(i,j) = 0` or globally: `X.lo = 0`?

### How to Verify

**Test Case 1: 2D variable stationarity**
```gams
Variable X(i,j);
Objective obj.. z =e= sum((i,j), X(i,j)**2);
```
Expected: Stationarity equation `stat_X(i,j).. 2*X(i,j) =e= 0` for all (i,j)

**Test Case 2: Indexed bounds**
```gams
Variable X(i,j);
X.lo(i,j) = i.val;
X.up(i,j) = j.val;
```
Expected: Complementarity pairs per (i,j): `mu_lo_X(i,j) complements X(i,j) - X.lo(i,j)`

**Test Case 3: Sparsity check**
```gams
Set i / 1*100 /, j / 1*100 /;
Variable X(i,j);  # 10,000 variables
```
Expected: Performance acceptable, no memory issues

### Risk if Wrong
- **Incorrect MCP:** Stationarity equations may be wrong, solutions invalid
- **Scalability:** Large index sets may cause performance problems
- **IR mismatch:** KKT module expectations may not match multi-dim IR

### Estimated Research Time
4-6 hours (trace through KKT module, test with multi-dim examples, validate output)

### Owner
Development team (KKT specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.7: Can table declarations be parsed as structured data or need special handling?

### Priority
**Medium** - May be needed for some GAMSLib models

### Assumption
Table declarations can be parsed as a special statement type and stored in IR, deferring semantic handling (parameter initialization) to later sprints.

### Research Questions
1. What's the syntax for table declarations: rows, columns, data layout?
2. Can we parse table structure without evaluating data (lazy parsing)?
3. Do tables require multi-dimensional indexing support?
4. Are tables syntactic sugar for parameter initialization, or do they have unique semantics?
5. How common are tables in GAMSLib models?

### How to Verify

**Test Case 1: Simple table**
```gams
Table data(i,j)
        j1  j2  j3
i1      1   2   3
i2      4   5   6
```
Expected: Parser recognizes table structure, stores in IR (even if not fully processed)

**Test Case 2: Table with headers**
```gams
Table A(i,j) "Distance matrix"
         NYC  LA   CHI
NYC       0  2800  800
LA     2800     0 2000
```
Expected: Parser handles string descriptions and data layout

### Risk if Wrong
- **Parsing fails:** Table syntax may be complex, blocking some models
- **Semantic coupling:** Tables may require parameter initialization logic (not planned for Sprint 7)
- **Low priority:** If tables are rare, effort may be wasted

### Estimated Research Time
2-3 hours (survey GAMSLib for table usage, design grammar rules)

### Owner
Development team (Parser specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.8: Are there backward compatibility risks with parser grammar changes?

### Priority
**Medium** - Regression prevention

### Assumption
Adding new grammar rules for preprocessor directives, multi-dimensional indexing, and set ranges won't break parsing of models that currently work.

### Research Questions
1. Do new terminals/rules conflict with existing grammar?
2. Will Lark parser performance degrade with more complex grammar?
3. Are there ambiguous cases where old and new syntax overlap?
4. Do we need grammar versioning or feature flags?
5. How to test for regressions: run all 1217 tests after grammar changes?

### How to Verify

**Test: Run existing test suite**
```bash
# After grammar changes
pytest tests/ -v
# Expected: All 1217 tests still pass (0 regressions)
```

**Test: Parse all examples/**
```bash
for model in examples/*.gms; do
  python -m src.cli $model -o /tmp/output.gms || echo "REGRESSION: $model"
done
# Expected: All existing examples still parse
```

### Risk if Wrong
- **Regressions:** Working models break, user trust damaged
- **Performance degradation:** Parser becomes slower (Sprint 6: ~5ms, acceptable up to ~10ms)
- **Hidden bugs:** Regressions not caught by tests, found in production

### Estimated Research Time
2-3 hours (analyze grammar, run comprehensive regression tests)

### Owner
Development team (QA specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.9: Can we defer equation attributes (`.l`, `.m`, `.lo`, `.up`) to Sprint 8?

### Priority
**Low** - Scope management

### Assumption
Equation attributes (e.g., `eq.l`, `eq.m` for level and marginal) are not needed for Sprint 7's 30% parse rate goal and can be deferred to Sprint 8 Wave 2.

### Research Questions
1. Do any of the 9 failed GAMSLib models use equation attributes?
2. Are attributes required for parsing or only for semantics (solve statements)?
3. Can parser skip attributes with warning, or must it support them?
4. Is there overlap between variable attributes (`.lo`, `.up`) and equation attributes?
5. What's the implementation effort: grammar only, or full semantic support?

### How to Verify

**Survey GAMSLib models:**
```bash
grep -r "\.l\|\.m\|\.lo\|\.up" data/gamslib/*.gms | grep -v "^$"
```
Expected: Count occurrences, determine if blocking any of the 9 failed models

**Test: Parser tolerance**
```gams
Equation eq;
eq.. x + y =e= 10;
eq.l = 5;  # Level attribute
```
Expected: Determine if this causes parse failure or can be ignored

### Risk if Wrong
- **Underestimate:** Attributes block models, preventing 30% parse rate
- **Scope creep:** Adding attributes mid-sprint if needed

### Estimated Research Time
1-2 hours (grep search, test parser behavior)

### Owner
Development team (Parser specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.10: Do we need assignment statement support (`scalar x; x = 5;`) for GAMSLib parsing?

### Priority
**Medium** - Potential parser gap

### Assumption
Assignment statements outside equations (e.g., `x = 5;` for scalars/parameters) are not critical for Sprint 7 parse rate and can be deferred.

### Research Questions
1. How common are assignment statements in GAMSLib models?
2. Can parser skip assignments or must it process them for correct semantics?
3. Are assignments used for data initialization (low priority) or control flow (higher priority)?
4. What's the syntax: `x = expr;` or more complex forms?
5. Do assignments interact with preprocessor directives (`$set`)?

### How to Verify

**Survey GAMSLib:**
```bash
# Look for assignment patterns
grep -E "^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*" data/gamslib/*.gms | head -20
```
Expected: Determine frequency and context

**Test: Parser behavior**
```gams
Scalar x;
x = 10;
```
Expected: Parse succeeds or fails with clear error

### Risk if Wrong
- **Underestimate:** Assignments block models
- **Complexity:** Assignment semantics may be more complex than assumed

### Estimated Research Time
2-3 hours (survey, test parsing, assess priority)

### Owner
Development team (Parser specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.11: Can we implement `$include` by attempting to parse included files?

### Priority
**Medium** - Preprocessor directive handling detail

### Assumption
`$include` directives can be handled by attempting to locate and parse the included file, falling back to skipping if file not found.

### Research Questions
1. Do GAMSLib models use relative paths, absolute paths, or GAMS library paths?
2. Can we resolve included file paths from the working directory?
3. Should we recursively parse included files or just skip the directive?
4. What if included file has parse errors - fail entire parse or warn and continue?
5. Do included files use preprocessor directives themselves (nested includes)?

### How to Verify

**Test Case 1: Relative include**
```gams
$include data/params.gms
```
Expected: Parser attempts to load `data/params.gms` from model directory

**Test Case 2: Missing include**
```gams
$include nonexistent.gms
```
Expected: Parser warns but continues (or fails with clear message)

**Test Case 3: Recursive include**
```gams
# main.gms
$include a.gms
# a.gms
$include b.gms
```
Expected: Parser handles nested includes or detects cycles

### Risk if Wrong
- **Path resolution errors:** Can't find included files, parse fails
- **Infinite loops:** Circular includes cause parser to hang
- **Security:** Arbitrary file inclusion may be a security risk

### Estimated Research Time
3-4 hours (implement prototype, test on GAMSLib models with includes)

### Owner
Development team (Parser specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 2: Test Performance

## Unknown 2.1: Which tests account for the majority of execution time?

### Priority
**High** - Determines optimization strategy

### Assumption
A small fraction of tests (e.g., 10-20% of tests) account for the majority (80%+) of execution time, following the Pareto principle.

### Research Questions
1. What percentage of tests take >1 second?
2. Are slow tests concentrated in specific modules (validation, integration, E2E)?
3. Is slowness due to solver calls, file I/O, or computation?
4. Can slow tests be optimized (e.g., smaller test models) or must they be marked `@pytest.mark.slow`?
5. What's the speedup potential: 107s → ? seconds if slow tests are parallelized or deferred?

### How to Verify

**Profile test suite:**
```bash
pytest --durations=50
```
Expected: Identify top 50 slowest tests, categorize by type and time

**Analyze results:**
- How many tests >5s? (likely validation tests with PATH solver)
- How many tests 1-5s? (likely E2E tests with golden files)
- How many tests <100ms? (likely unit tests)

**Calculate Pareto:**
If top 20% of tests account for 80%+ of time, optimization is straightforward

### Risk if Wrong
- **Uniform distribution:** All tests equally slow, no easy optimizations
- **Slow tests necessary:** Solver validation cannot be sped up, must be deferred
- **Measurement error:** Profiling overhead skews results

### Estimated Research Time
2-3 hours (run profiling, analyze results, categorize tests)

### Owner
Development team (Testing specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.2: Can pytest-xdist parallelize tests without race conditions?

### Priority
**High** - Core to test performance goal

### Assumption
pytest-xdist can run tests in parallel (4-8 workers) without introducing race conditions from shared file system access or global state.

### Research Questions
1. Do tests use shared temporary directories that could cause conflicts?
2. Are there tests with global state mutations (e.g., environment variables)?
3. Can solver calls (PATH) handle concurrent execution?
4. Does pytest-xdist provide per-worker isolation (separate tmp dirs)?
5. What's the optimal worker count: 4, 8, or auto-detect based on CPU cores?

### How to Verify

**Test: Run with parallelization**
```bash
pytest -n 4 tests/unit/
pytest -n 8 tests/integration/
```
Expected: All tests pass, no flaky failures

**Test: Stress test**
```bash
for i in {1..10}; do
  pytest -n 8 tests/ || echo "FAILURE on iteration $i"
done
```
Expected: 0 failures across 10 runs (no race conditions)

**Benchmark speedup:**
```bash
time pytest tests/  # Baseline
time pytest -n 4 tests/  # 4 workers
time pytest -n 8 tests/  # 8 workers
```
Expected: ~3-4x speedup with 4 workers, ~6-7x with 8 workers

### Risk if Wrong
- **Flaky tests:** Race conditions cause intermittent failures, CI unreliable
- **Wrong results:** Tests pass in parallel but actually have bugs
- **No speedup:** Overhead from parallelization negates benefits

### Estimated Research Time
3-4 hours (install pytest-xdist, run tests, analyze for flakiness, benchmark)

### Owner
Development team (Testing specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.3: Can validation tests with PATH solver be marked slow and run separately?

### Priority
**High** - Fast test suite goal

### Assumption
Validation tests that call PATH solver can be marked `@pytest.mark.slow` and excluded from fast test runs (`pytest -m "not slow"`) without sacrificing coverage.

### Research Questions
1. How many tests call PATH solver?
2. What percentage of total test time do PATH tests account for?
3. Can PATH tests be run in CI only (not local development)?
4. Are there critical PATH tests that must run in fast suite?
5. Does PATH licensing limit concurrent executions?

### How to Verify

**Count PATH tests:**
```bash
grep -r "PATH\|path_solver\|validate.*solve" tests/ --include="*.py" | wc -l
```
Expected: Identify how many tests use solver

**Profile PATH tests:**
```bash
pytest tests/validation/ --durations=0
```
Expected: Measure time contribution of PATH tests

**Test exclusion:**
```bash
# Mark PATH tests
pytest -m "slow" tests/  # Run only slow tests
pytest -m "not slow" tests/  # Run fast tests
```
Expected: Fast suite <60s, slow suite can be >60s

### Risk if Wrong
- **Too many slow tests:** Fast suite still too slow
- **Critical tests excluded:** Coverage gaps in fast suite
- **PATH required:** Solver validation cannot be deferred

### Estimated Research Time
2-3 hours (identify PATH tests, measure time, test marking strategy)

### Owner
Development team (Testing specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.4: What's the performance overhead of pytest-xdist?

### Priority
**Medium** - Speedup calculation

### Assumption
pytest-xdist overhead (process spawning, result collection) is <10% of total test time, so 4 workers yield ~3.6x speedup (not perfect 4x).

### Research Questions
1. How much overhead does worker spawning add?
2. Does overhead increase with worker count (8 workers > 4 workers overhead)?
3. Are there tests that cannot be parallelized (e.g., due to test order dependencies)?
4. What's the speedup curve: 2 workers, 4 workers, 8 workers, 16 workers?
5. Is there a point of diminishing returns (too many workers)?

### How to Verify

**Benchmark worker count:**
```bash
for workers in 1 2 4 8 16; do
  echo "=== $workers workers ==="
  time pytest -n $workers tests/unit/
done
```
Expected: Plot speedup curve, identify optimal worker count

**Measure overhead:**
- Serial time: 107s
- Parallel time (4 workers): ~30s
- Ideal speedup: 107/4 = 26.75s
- Actual speedup: 30s
- Overhead: (30 - 26.75) / 30 = 10.8%

### Risk if Wrong
- **High overhead:** Parallelization doesn't achieve expected speedup
- **Diminishing returns:** 8 workers no better than 4 workers
- **Negative speedup:** Overhead exceeds benefits (unlikely but possible)

### Estimated Research Time
2-3 hours (benchmark multiple worker counts, analyze results)

### Owner
Development team (Testing specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.5: Can CI timeout be extended or do we need faster tests?

### Priority
**Medium** - CI configuration

### Assumption
CI jobs have sufficient timeout (10-15 minutes) to run full test suite even if optimization goals aren't met.

### Research Questions
1. What's the current CI timeout for test jobs?
2. Can timeout be extended to 20-30 minutes if needed?
3. Is there a cost implication for longer CI jobs?
4. Do we run tests in CI differently than locally (e.g., more verbose output)?
5. Can we use CI caching to speed up dependency installation?

### How to Verify

**Check CI configuration:**
```yaml
# .github/workflows/*.yml
jobs:
  test:
    timeout-minutes: ?
```
Expected: Determine current timeout

**Test CI timing:**
Run CI job and measure actual execution time (install deps, run tests, upload artifacts)

**Benchmark with caching:**
Enable pip cache, pytest cache - measure speedup

### Risk if Wrong
- **Timeout too short:** CI jobs fail, blocking PRs
- **Timeout too long:** CI takes forever, slows development
- **Cost issues:** Long CI jobs may have billing implications

### Estimated Research Time
1-2 hours (review CI config, test timing, check documentation)

### Owner
DevOps/Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.6: Are there test isolation issues that prevent parallelization?

### Priority
**Medium** - Parallelization blocker

### Assumption
Tests are well-isolated (no shared mutable state, each test cleans up after itself) and can run in parallel without conflicts.

### Research Questions
1. Do tests use `pytest.fixture(scope="module")` or `scope="session"` that could cause issues?
2. Are there tests that modify global singletons or environment variables?
3. Do tests create files in predictable locations (e.g., `/tmp/test_output.gms`) without unique names?
4. Are there test order dependencies (Test B assumes Test A ran first)?
5. Do tests mock global objects (e.g., `sys.stdout`) that could conflict across workers?

### How to Verify

**Review test code:**
```bash
# Check for shared state
grep -r "scope=.*session\|scope=.*module" tests/
grep -r "os.environ\|sys.stdout" tests/
grep -r "open.*\/tmp\/" tests/
```
Expected: Identify potential isolation issues

**Test randomization:**
```bash
pytest --random-order tests/
```
Expected: Tests pass regardless of order (no dependencies)

**Test parallelization stress:**
```bash
# Run in parallel 20 times
for i in {1..20}; do
  pytest -n 8 tests/ --tb=short || echo "FAIL: iteration $i"
done
```
Expected: 0 failures (no race conditions or isolation issues)

### Risk if Wrong
- **Flaky tests:** Intermittent failures from isolation issues
- **Cannot parallelize:** Must fix isolation before enabling pytest-xdist
- **False positives:** Tests pass locally but fail in CI

### Estimated Research Time
3-4 hours (code review, test randomization, stress testing)

### Owner
Development team (Testing specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 3: GAMSLib Integration

## Unknown 3.1: Is 30% parse rate achievable with Sprint 7 scope?

### Priority
**Critical** - Core sprint goal

### Assumption
Implementing 3-4 parser features (preprocessor, multi-dim indexing, set ranges) will unlock ≥2 additional GAMSLib models, achieving 30% parse rate (3/10 models).

### Research Questions
1. Have we correctly identified which features block which models?
2. Are there hidden dependencies (Feature A requires Feature B)?
3. Is there a "long tail" where each model needs unique features?
4. Can we achieve 30% or is 20% more realistic?
5. Should we expand to 15-20 models for more stable percentage?

### How to Verify

**After Task 2 (Failure Analysis):**
Review `docs/planning/EPIC_2/SPRINT_7/GAMSLIB_FAILURE_ANALYSIS.md` and determine:
- Which features unlock how many models
- Minimum feature set for 30% (3/10 models)
- Whether 30% is realistic or optimistic

**During Sprint 7:**
After each parser feature is implemented, re-run ingestion:
```bash
make ingest-gamslib
# Check parse rate improvement
```
Expected: Incremental progress toward 30%

### Risk if Wrong
- **Overestimate:** Implement features but only reach 20% (2/10 models)
- **Underestimate:** Could have reached 40% with same effort
- **Goal mismatch:** 30% is wrong target, should be models parsed not percentage

### Estimated Research Time
Depends on Task 2 (Failure Analysis) - 2-3 hours to assess feasibility

### Owner
Sprint planning team

### Verification Results
🔍 **Status:** INCOMPLETE (pending Task 2)

---

## Unknown 3.2: Can dashboard updates be automated without security risks?

### Priority
**Medium** - CI automation

### Assumption
CI can auto-commit dashboard updates to the repository without compromising security (e.g., no arbitrary code execution from JSON reports).

### Research Questions
1. Is auto-commit safe: does it require write access to repo?
2. Can we use GitHub Actions `secrets.GITHUB_TOKEN` safely?
3. Should we auto-commit or require manual PR review of dashboard changes?
4. What if dashboard shows regression - auto-commit bad data?
5. Are there authentication/permission issues with CI committing?

### How to Verify

**Test CI auto-commit:**
```yaml
- name: Commit dashboard
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git add docs/status/GAMSLIB_CONVERSION_STATUS.md
    git commit -m "Update GAMSLib dashboard [skip ci]" || echo "No changes"
    git push
```
Expected: CI successfully commits changes (or fails with clear error)

**Security review:**
- Does JSON report parsing have injection risks?
- Can malicious model cause bad dashboard data?
- Is `[skip ci]` needed to prevent infinite loops?

### Risk if Wrong
- **Security vulnerability:** Arbitrary code execution or repo compromise
- **Infinite loops:** CI triggers itself repeatedly
- **Bad commits:** Regression data committed automatically

### Estimated Research Time
3-4 hours (design workflow, test security, implement safeguards)

### Owner
DevOps/Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.3: What's the right parse rate regression threshold?

### Priority
**Medium** - CI regression detection

### Assumption
A >10% drop in parse rate (e.g., 30% → 27%) indicates a regression worth failing CI.

### Research Questions
1. Is 10% too sensitive (false positives from random variation)?
2. Should threshold be absolute (e.g., -1 model) or relative (e.g., -10%)?
3. What if parse rate improves unexpectedly - is that a "regression" (test bug)?
4. Should threshold depend on baseline: 10% → 9% is -10% relative but only -1% absolute?
5. Can we track trend over time instead of single-commit changes?

### How to Verify

**Simulate regressions:**
- Baseline: 30% (3/10 models)
- Regression: 20% (2/10 models) - should trigger alert
- Small change: 30% → 27% (still 3/10, maybe one model got harder to parse) - should not trigger

**Calculate thresholds:**
| Baseline | 10% relative | 10% absolute | 1 model absolute |
|----------|--------------|--------------|------------------|
| 10% (1/10) | 9% | 0% | 0% (0/10) |
| 30% (3/10) | 27% | 20% | 20% (2/10) |
| 50% (5/10) | 45% | 40% | 40% (4/10) |

**Recommendation:** Use absolute model count: -1 model = regression (simpler, clearer)

### Risk if Wrong
- **Too sensitive:** False positives, CI fails on noise
- **Too lenient:** Real regressions not caught
- **Wrong metric:** Percentage vs absolute count confusion

### Estimated Research Time
2-3 hours (analyze thresholds, test scenarios, define policy)

### Owner
Sprint planning team / DevOps

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.4: Should we expand GAMSLib test set beyond 10 models?

### Priority
**Low** - Scope question for Sprint 8+

### Assumption
10 Tier 1 GAMSLib models are sufficient for Sprint 7 baseline; expanding to 20-30 models can wait until Sprint 8.

### Research Questions
1. Is 10 models statistically significant or too small?
2. Do we risk overfitting parser to these 10 models?
3. Would 20 models give more stable parse rate percentage?
4. Is there a cost to expanding: CI time, storage, maintenance?
5. Should we prioritize diverse models (different syntax features) or similar models (same feature depth)?

### How to Verify

**Analyze 10 model diversity:**
- Do all 10 models use similar GAMS features?
- Are they all small/large, simple/complex, or mixed?
- Would adding 10 more models reveal new parser gaps?

**Cost-benefit:**
- Adding 10 models: +1-2 minutes CI time
- Benefit: More robust parse rate tracking
- Cost: More failure analysis, more maintenance

### Risk if Wrong
- **Too small:** 10 models not representative, parse rate misleading
- **Overfitting:** Parser works on these 10 but fails on others
- **Premature optimization:** Expanding too early wastes effort

### Estimated Research Time
1-2 hours (analyze model diversity, assess expansion benefits)

### Owner
Sprint planning team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 4: Convexity Refinements

## Unknown 4.1: Can we extract line numbers from Lark parse tree without performance impact?

### Priority
**High** - Convexity warning UX improvement

### Assumption
Lark parse tree provides `.meta.line` and `.meta.column` attributes that can be extracted and propagated through IR transformations without significant performance overhead.

### Research Questions
1. Does Lark parser store line numbers for all AST nodes?
2. What's the performance cost of storing metadata in every IR node?
3. Do normalization transformations preserve line number metadata?
4. Can we handle equations created during transformations (no source line)?
5. What if equation spans multiple lines - which line to report?

### How to Verify

**Test Case 1: Extract line numbers**
```python
from lark import Lark
tree = parser.parse(gams_code)
for node in tree.iter_subtrees():
    if hasattr(node, 'meta'):
        print(f"Line {node.meta.line}: {node.data}")
```
Expected: All nodes have `.meta.line` attribute

**Test Case 2: Benchmark overhead**
```bash
# Without metadata
time pytest tests/unit/gams/test_parser.py

# With metadata (store in IR)
# Modify IR to include metadata
time pytest tests/unit/gams/test_parser.py
```
Expected: Overhead <5% (acceptable)

**Test Case 3: Multi-line equations**
```gams
eq.. x + y
     + z =e= 10;
```
Expected: Report line of equation name (`eq..`) or first line of expression

### Risk if Wrong
- **No line numbers:** Lark doesn't provide metadata, feature unimplementable
- **Performance hit:** 10-20% overhead, unacceptable
- **Metadata lost:** Normalization drops line numbers, warnings don't cite lines

### Estimated Research Time
3-4 hours (test Lark metadata, benchmark, design IR changes)

### Owner
Development team (Parser/IR specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.2: Should fine-grained suppression use CLI flags or config file?

### Priority
**Medium** - UX design decision

### Assumption
CLI flags (e.g., `--skip-convexity-codes W301,W303`) are more user-friendly than config files for suppressing specific convexity warnings.

### Research Questions
1. Is CLI flag sufficient or do users need per-model configuration?
2. Should we support both CLI and config file (precedence rules)?
3. How to validate warning codes: error on typo (`--skip-convexity-codes W999`) or warn?
4. Can users suppress all warnings of a type globally or need per-equation control?
5. What's the syntax: comma-separated (`W301,W303`) or repeatable flag (`--skip W301 --skip W303`)?

### How to Verify

**Test Case 1: CLI flag**
```bash
nlp2mcp model.gms --skip-convexity-codes W301,W303
```
Expected: W301 and W303 warnings suppressed, W302/W304/W305 still shown

**Test Case 2: Config file**
```toml
# .nlp2mcp.toml
[convexity]
skip_codes = ["W301", "W303"]
```
Expected: Same behavior as CLI flag

**Test Case 3: Precedence**
```bash
nlp2mcp model.gms --skip-convexity-codes W301  # CLI
# .nlp2mcp.toml has skip_codes = ["W303"]
```
Expected: Both W301 and W303 suppressed (union of CLI and config)

### Risk if Wrong
- **Poor UX:** Users confused by suppression mechanism
- **Inconsistency:** CLI and config file behavior differ
- **Scope creep:** Per-equation suppression needed, much more complex

### Estimated Research Time
2-3 hours (design options, implement prototype, gather feedback)

### Owner
Development team (UX/CLI specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.3: Can we implement context-aware convexity heuristics in Sprint 7?

### Priority
**Low** - Stretch goal

### Assumption
Context-aware heuristics (e.g., checking variable bounds to determine if `sin(x)` is convex/concave on restricted domain) are too complex for Sprint 7 and should be deferred to Sprint 8+.

### Research Questions
1. How much effort to check bounds in convexity detector?
2. Would context-awareness significantly reduce false positives?
3. Are there simple cases we could handle (e.g., `x.lo = 0; x.up = pi/2; sin(x)` is concave)?
4. What about complex cases (bounds depend on other variables)?
5. Is the ROI worth it: effort vs false positive reduction?

### How to Verify

**Estimate effort:**
- Parse bounds from IR
- Check if bounds restrict function to convex/concave domain
- Update heuristic to skip warning if domain is safe
Estimated: 4-8 hours

**Estimate benefit:**
- Survey convexity test fixtures: how many have restricted domains?
- Calculate false positive reduction: ?%

**Decision:**
If benefit is high (>30% false positive reduction) and effort is low (<8 hours), include in Sprint 7
Otherwise, defer to Sprint 8

### Risk if Wrong
- **Premature optimization:** Spend effort on low-impact feature
- **Scope creep:** Sprint 7 timeline at risk
- **Wrong assumption:** Context-awareness is harder than expected

### Estimated Research Time
2-3 hours (survey fixtures, estimate effort, calculate ROI)

### Owner
Sprint planning team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 5: CI/CD

## Unknown 5.1: Should CI job run on every PR or only parser-related changes?

### Priority
**Medium** - CI efficiency

### Assumption
GAMSLib ingestion CI job should run only when parser-related files change (grammar, parser, IR) to avoid unnecessary runs on documentation/test changes.

### Research Questions
1. What files trigger CI: grammar.lark, parser.py, ir/*.py, normalization/*.py?
2. Should we also run on schedule (weekly) regardless of changes?
3. What if parser change doesn't affect GAMSLib (e.g., bug fix in variable naming)?
4. Can we use GitHub Actions `paths` filter effectively?
5. What's the cost of running on every PR vs selective runs?

### How to Verify

**Test path filter:**
```yaml
on:
  pull_request:
    paths:
      - 'src/gams/grammar.lark'
      - 'src/gams/parser.py'
      - 'src/ir/**'
      - 'src/normalize/**'
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
```
Expected: CI runs on parser changes, skips on documentation changes

**Cost analysis:**
- Every PR: ~100 PRs/year × 5 min = 8.3 hours CI time
- Selective: ~30 parser PRs/year × 5 min = 2.5 hours CI time
- Savings: 5.8 hours/year (minimal cost impact but cleaner CI logs)

### Risk if Wrong
- **Too selective:** Miss regressions from unexpected changes
- **Too broad:** CI runs unnecessarily, slower PR feedback
- **Missed runs:** Path filter misconfigured, parser changes skip CI

### Estimated Research Time
1-2 hours (configure path filter, test trigger conditions)

### Owner
DevOps/Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Confirmed Knowledge (From Sprint 6 and Earlier)

### Parser
- ✅ Lark parser handles GAMS subset efficiently (~5ms for small models)
- ✅ Grammar modifications don't break existing tests if carefully designed
- ✅ Parser can handle 1000+ line models without performance issues

### Testing
- ✅ pytest framework scales to 1217 tests without issues
- ✅ Test markers (`@pytest.mark.unit`, `@pytest.mark.integration`) work well
- ✅ Golden file tests catch regressions effectively

### GAMSLib
- ✅ 10 Tier 1 models provide good baseline for sprint-to-sprint tracking
- ✅ Dashboard JSON format is stable and machine-readable
- ✅ Ingestion script (`make ingest-gamslib`) is reliable

### Convexity
- ✅ Pattern-based heuristics detect nonconvex cases with acceptable false positive rate
- ✅ Warning format (W3xx codes) is clear and user-friendly
- ✅ Documentation links in warnings improve UX

---

## Template for New Unknowns

When adding unknowns during Sprint 7:

```markdown
## Unknown X.Y: [Question/Assumption]

### Priority
**[Critical/High/Medium/Low]** - [One-line impact]

### Assumption
[State the assumption being made]

### Research Questions
1. [Question 1]
2. [Question 2]
...

### How to Verify
[Test cases, experiments, analysis to validate assumption]

### Risk if Wrong
[Impact if assumption is incorrect]

### Estimated Research Time
[Hours] ([brief description of research activities])

### Owner
[Team/Person responsible]

### Verification Results
🔍 **Status:** INCOMPLETE
```

---

## Next Steps

**Before Sprint 7 Day 1:**
1. Review all Critical and High priority unknowns (16 total)
2. Execute verification tests for top unknowns
3. Update this document with findings
4. Adjust Sprint 7 scope if major assumptions are wrong
5. Share findings with team during sprint planning

**During Sprint 7:**
1. Reference this document daily
2. Add newly discovered unknowns
3. Update verification results as features are implemented
4. Move resolved items to "Confirmed Knowledge"

---

**Document Status:** 🔵 DRAFT - Pre-Sprint 7  
**Last Updated:** November 14, 2025  
**Owner:** Sprint 7 Planning Team  
**Review Frequency:** Daily during Sprint 7
