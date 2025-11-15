# Sprint 7 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 7 (Epic 2 - Parser Enhancements & GAMSLib Expansion)  
**Timeline:** Complete before Sprint 7 Day 1  
**Goal:** Address Sprint 6 parser limitations and prepare for 30%+ GAMSLib parse rate target

**Key Insight from Sprint 6:** Parser limitations were underestimated - 9/10 GAMSLib models failed on preprocessor directives. Systematic analysis of parser gaps and prioritization of high-impact features is critical for Sprint 7 success.

---

## Executive Summary

Sprint 6 achieved 10% GAMSLib parse rate (1/10 models) but revealed significant parser gaps. Sprint 7 aims to triple this to 30%+ by addressing:
1. **Priority 1 (Parser Gaps):** Preprocessor directives (`$if`, `$set`, `$include`) causing 9/10 failures
2. **Priority 2 (Advanced Features):** Multi-dimensional set indexing, table declarations, set operations
3. **Priority 3 (Performance):** Test suite optimization (107s → <60s for fast tests)
4. **Priority 4 (Quality):** Convexity refinements, CI automation, dashboard improvements

This prep plan focuses on research, analysis, and design tasks that must be completed before Sprint 7 Day 1 to ensure smooth execution and avoid parser complexity underestimation.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|------------------------|
| 1 | Create Sprint 7 Known Unknowns List | Critical | 4-6 hours | None | Proactive risk management |
| 2 | Analyze GAMSLib Parser Failures | Critical | 6-8 hours | Task 1 | Parser gap prioritization |
| 3 | Research Preprocessor Directive Handling | Critical | 8-10 hours | Task 2 | Preprocessor support design |
| 4 | Research Multi-Dimensional Set Indexing | High | 6-8 hours | Task 2 | Advanced GAMS features |
| 5 | Profile Test Suite Performance | High | 4-6 hours | None | Test optimization baseline |
| 6 | Survey GAMS Syntax Features for Wave 2 | High | 4-6 hours | Task 2 | Parser roadmap planning |
| 7 | Design Line Number Tracking for Warnings | Medium | 3-4 hours | None | Convexity UX improvements |
| 8 | Set Up CI for GAMSLib Regression Tracking | Medium | 4-5 hours | None | Automated dashboard updates |
| 9 | Create Parser Test Fixture Strategy | High | 3-4 hours | Tasks 2, 3, 4 ✅ | Test coverage planning |
| 10 | Plan Sprint 7 Detailed Schedule | Critical | 6-8 hours | All tasks | Sprint 7 execution planning |

**Total Estimated Time:** ~48-65 hours (~6-8 working days)

**Critical Path:** Tasks 1 → 2 → 3, 4 → 9 → 10 (must complete before Sprint 7)

---

## Task 1: Create Sprint 7 Known Unknowns List

**Status:** ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 4-6 hours  
**Deadline:** 1 week before Sprint 7 Day 1  
**Owner:** Sprint planning team  
**Dependencies:** None

### Objective

Create comprehensive `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md` documenting all assumptions, uncertainties, and research questions that could impact Sprint 7 execution.

### Why This Matters

Sprint 6 demonstrated that parser complexity was underestimated (only 10% parse rate vs expected higher baseline). Sprint 7 tackles even more complex parser features (preprocessor directives, multi-dimensional indexing) with many untested assumptions.

**Critical assumptions to validate:**
- Preprocessor directive handling approach (full vs mock)
- Multi-dimensional indexing impact on IR and normalization
- Test parallelization doesn't introduce race conditions
- GAMSLib models use parseable subset after adding new features
- Convexity warning line number tracking feasible with current parser

### Background

Sprint 4, 5, and 6 Known Unknowns processes successfully prevented late-stage surprises:
- Sprint 4: 23 unknowns, zero blocking issues
- Sprint 5: 22 unknowns, all resolved on schedule
- Sprint 6: 22 unknowns, enabled realistic scope setting

Sprint 7 adds complexity with parser internals modifications, requiring even more thorough unknown identification.

### What Needs to Be Done

**Create document with sections:**

1. **Parser Enhancement Unknowns** (10-12 unknowns expected)
   - Preprocessor directive handling strategy
   - Grammar modification scope and testing
   - Multi-dimensional indexing IR representation
   - Table declaration normalization
   - Set operation semantic handling
   - Backward compatibility risks

2. **Test Performance Unknowns** (4-6 unknowns expected)
   - Parallelization race conditions
   - Slow test identification methodology
   - Worker count optimization
   - CI timeout handling
   - Fixture isolation requirements

3. **GAMSLib Integration Unknowns** (3-5 unknowns expected)
   - Parse rate improvement predictability
   - CI job execution time
   - Dashboard update automation reliability
   - Regression detection false positives

4. **Convexity Refinement Unknowns** (3-4 unknowns expected)
   - Line number tracking parser overhead
   - Fine-grained suppression implementation complexity
   - Context-aware heuristics feasibility
   - Documentation link generation automation

5. **CI/CD Unknowns** (2-3 unknowns expected)
   - Auto-commit workflow security
   - Parse rate regression thresholds
   - CI job trigger specificity

**Changes:**

Created comprehensive 9-model failure analysis with 7-feature impact matrix. Key findings:
- Identified 2 critical features (preprocessor directives, set range syntax) that unlock 3 models = 30% parse rate
- Calculated precise ROI for each feature (preprocessor: 2.9%/hour, set range: 2.5%/hour)
- Categorized all failures into 3 main categories: preprocessor (2 models), set features (1 model), statement-level (6 models)
- Recommended 2-phase Sprint 7 implementation: Phase 1 (preprocessor 6-8h) + Phase 2 (set range 3-4h) = 9-12 hours total

**Result:**

Deliverable created: `docs/planning/EPIC_2/SPRINT_7/GAMSLIB_FAILURE_ANALYSIS.md` (550+ lines)
- Detailed analysis of all 9 models with error context and root causes
- Feature impact matrix with complexity, effort, priority, and unlock rate
- Quick wins vs hard problems categorization
- Sprint 7 implementation plan with concrete steps
- Verified Unknown 1.3: 30% parse rate achievable with 2 features
- Verified Unknown 3.1: Sprint 7 scope is sufficient for 30%+ goal

### Verification

```bash
# Document should exist
test -f docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md

# Should contain required sections
grep -q "Parser Enhancement" docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md
grep -q "Test Performance" docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md
grep -q "GAMSLib Integration" docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md
grep -q "Convexity Refinement" docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md

# Count unknowns (should be 22-30)
grep -c "^## Unknown" docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md`
- 22-30 unknowns documented across 5 categories
- Each unknown has: assumption, verification method, priority, owner
- Research time estimated for all Critical/High unknowns
- Cross-referenced with PROJECT_PLAN.md Sprint 7 deliverables

### Acceptance Criteria

- [x] Document created with 22+ unknowns across 5 categories
- [x] All unknowns have assumption, verification method, priority
- [x] All Critical unknowns have verification plan and timeline
- [x] Unknowns cover all Sprint 7 components (parser, tests, CI, convexity)
- [x] Template for updates defined
- [x] Research time estimated (28-36 hours total; exceeds initial 24-32 hour target)
- [x] Cross-referenced with PROJECT_PLAN.md and PRELIMINARY_PLAN.md

---

## Task 2: Analyze GAMSLib Parser Failures

**Status:** ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 6-8 hours  
**Deadline:** 1 week before Sprint 7 Day 1  
**Owner:** Development team (Parser specialist)  
**Dependencies:** Task 1 (Known Unknowns)  
**Unknowns Verified:** 1.3, 3.1

### Objective

Perform detailed analysis of all 9 GAMSLib parser failures to categorize error types, identify high-impact features, and prioritize parser enhancements for Sprint 7.

### Why This Matters

Sprint 6 established 10% baseline but treating all parser gaps equally wastes effort. Some features may unlock multiple models (high ROI), while others unlock only one model (low ROI). Strategic prioritization is critical to achieving 30%+ parse rate.

**Key questions:**
- Which features appear in most failed models?
- What's the minimal feature set to unlock 2-3 additional models?
- Are there easy wins (simple syntax) vs hard problems (complex semantics)?
- Which failures are caused by missing features vs bugs in existing parser?

### Background

From `docs/status/GAMSLIB_CONVERSION_STATUS.md`:
- 9/10 models failed with `UnexpectedCharacters`
- `circle.gms`: Failed on `$if not set size $set size 10` (preprocessor)
- `himmel16.gms`: Failed on `Set i 'indices for the 6 points' / 1*6 /;` (range syntax)
- Other models: Unknown specific causes

Need systematic analysis to understand failure distribution across:
- Preprocessor directives (`$if`, `$set`, `$include`, `$ontext`, etc.)
- Set features (ranges, tuples, indexed sets)
- Parameter features (tables, multi-dimensional indexing)
- Statement types (display, option, assignment)

### What Needs to Be Done

**Step 1: Extract all parser error messages**

For each of the 9 failed models:
1. Locate model file in GAMSLib cache
2. Run parser with verbose error output
3. Capture: error message, line number, problematic syntax
4. Document in `docs/planning/EPIC_2/SPRINT_7/GAMSLIB_FAILURE_ANALYSIS.md`

```bash
# For each failed model (wrapped in subshell to preserve working directory)
(
  if [ ! -d "data/gamslib" ]; then
    echo "Error: data/gamslib/ directory does not exist. Please check your path."
    exit 1
  fi
  cd data/gamslib/
  for model in circle himmel16 hs62 mathopt1 maxmin mhw4dx mingamma rbrock trig; do
    echo "=== $model ===" >> failures.txt
    # Change to repo root to ensure src.cli is importable, then run parser
    (cd ../.. && python -m src.cli data/gamslib/${model}.gms 2>&1 | grep -A20 "UnexpectedCharacters") >> failures.txt
  done
)
```

**Step 2: Categorize failures by feature type**

Create taxonomy:
- **Preprocessor directives:** `$if`, `$set`, `$include`, `$ontext`/`$offtext`, `$call`, etc.
- **Set features:** Range syntax (`1*6`), tuples (`(i,j)`), indexed sets, set operations
- **Parameter features:** Table declarations, multi-dimensional indexing, data statements
- **Expression features:** Conditional expressions (`$(condition)`), special functions
- **Statement types:** Display, option, assignment, loop constructs

**Step 3: Build feature impact matrix**

| Feature | Models Blocked | Complexity | Est. Effort | Priority |
|---------|----------------|------------|-------------|----------|
| `$if`/`$set` | 5-7 | High | 8-12h | Critical |
| Range syntax `1*6` | 3-4 | Medium | 4-6h | High |
| Multi-dim indexing | 2-3 | High | 6-8h | High |
| Table declarations | 1-2 | Medium | 4-6h | Medium |
| ... | ... | ... | ... | ... |

**Step 4: Identify quick wins vs hard problems**

- **Quick wins:** Features with simple syntax, low semantic complexity, high model unlock count
- **Hard problems:** Features with complex semantics, deep IR changes, low model unlock count

**Step 5: Create recommended feature priority**

Based on:
1. Model unlock count (higher = better)
2. Implementation complexity (lower = better)
3. Foundation for future features (enabler features = higher priority)

**Changes:**

Created comprehensive 85-page research document analyzing GAMS preprocessor directive handling strategies. Key findings:
- Surveyed all 60+ GAMS dollar control options organized into 9 functional categories
- Analyzed GAMSLib test suite usage: only **3 directive types block parsing** (`$if not set`, `%macro%`, `$eolCom`)
- Only **2 models affected** (circle.gms, maxmin.gms) - all other failures are non-preprocessor issues
- Designed mock preprocessing approach requiring **no grammar changes** (preprocessing before parsing)
- Tested approach on 3 GAMSLib models: circle, maxmin, mhw4dx
- Compared 4 approaches: Full Preprocessor (40-60h), Mock (6-8h), Hybrid (12-15h), Skip (0h, insufficient)
- **Recommendation: Mock/skip approach** - achieves same +20% parse rate with 6-8h effort vs 40-60h for full preprocessing
- Documented implementation plan with 8 steps, unit test strategy, and quality checks
- Verified 3 Known Unknowns with concrete evidence and recommendations

**Result:**

Deliverable created: `docs/research/preprocessor_directives.md` (85 pages, 12 sections)
- **Section 1:** Background and current preprocessor status
- **Section 2:** Complete directive survey (60+ directives, usage frequency in GAMSLib)
- **Section 3:** Blocking analysis for circle.gms and maxmin.gms
- **Section 4:** Complexity analysis by category (Priority 1/2/3)
- **Section 5:** Mock handling approach design (3-function architecture, no grammar changes)
- **Section 6:** Grammar prototype decision (none needed - preprocessing removes directives)
- **Section 7:** Test results and expected preprocessing flow
- **Section 8:** Full vs Mock vs Hybrid comparison with effort/impact matrix
- **Section 9:** Detailed implementation plan for Sprint 7 (6-8 hours, 8 steps)
- **Section 10:** Limitations and warnings (command-line overrides, advanced conditionals, etc.)
- **Section 11:** Verification of Unknowns 1.1, 1.4, 1.11 with evidence and decisions
- **Section 12:** References and appendices (system constants, preprocessing examples)

Updated `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md`:
- **Unknown 1.1:** ✅ VERIFIED - Mock/skip approach is sufficient (6-8h vs 40-60h for full preprocessing)
- **Unknown 1.4:** ✅ VERIFIED - Preprocess before parsing, no grammar integration needed
- **Unknown 1.11:** ✅ VERIFIED - Include resolution NOT required (already implemented, orthogonal feature)

### Verification

```bash
# Analysis document should exist
test -f docs/planning/EPIC_2/SPRINT_7/GAMSLIB_FAILURE_ANALYSIS.md

# Should contain required sections
grep -q "Failure Summary" docs/planning/EPIC_2/SPRINT_7/GAMSLIB_FAILURE_ANALYSIS.md
grep -q "Feature Impact Matrix" docs/planning/EPIC_2/SPRINT_7/GAMSLIB_FAILURE_ANALYSIS.md
grep -q "Recommended Priority" docs/planning/EPIC_2/SPRINT_7/GAMSLIB_FAILURE_ANALYSIS.md

# Should analyze all 9 models
[ "$(grep -c "^### " docs/planning/EPIC_2/SPRINT_7/GAMSLIB_FAILURE_ANALYSIS.md)" -eq 9 ]
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_7/GAMSLIB_FAILURE_ANALYSIS.md`
- Feature impact matrix with 8-12 features analyzed
- Recommended feature priority (Critical/High/Medium/Low)
- Quick wins list (2-3 features that unlock most models for least effort)
- Hard problems list (features to defer to Sprint 8+)
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.3, 3.1

### Acceptance Criteria

- [x] All 9 failed models analyzed
- [x] Error messages categorized by feature type
- [x] Feature impact matrix complete with effort estimates
- [x] Quick wins identified (unlock ≥2 models, <6h effort)
- [x] Recommended priority aligns with 30% parse rate goal
- [x] Cross-referenced with PROJECT_PLAN.md Sprint 7 features
- [x] Unknowns 1.3, 3.1 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 3: Research Preprocessor Directive Handling

**Status:** ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 8-10 hours  
**Deadline:** 1 week before Sprint 7 Day 1  
**Owner:** Development team (Parser specialist)  
**Dependencies:** Task 2 (GAMSLib failure analysis) ✅  
**Unknowns Verified:** 1.1 ✅, 1.4 ✅, 1.11 ✅

### Objective

Research and design preprocessor directive handling strategy, comparing full preprocessing vs mock/skip approach, with concrete implementation plan for Sprint 7.

### Why This Matters

Preprocessor directives (`$if`, `$set`, `$include`) cause majority of GAMSLib failures. The handling strategy impacts:
- **Parser complexity:** Full preprocessing requires lexer/parser overhaul
- **Semantic correctness:** Mock handling may miss conditional code paths
- **Development time:** Full = weeks, Mock = days

Wrong choice could derail Sprint 7 or compromise correctness.

### Background

From Sprint 6 retrospective and GAMSLib analysis:
- Most failures due to `$if not set`, `$set`, `$include` directives
- Current parser treats `$` as unexpected character
- GAMS preprocessor is Turing-complete (supports macros, conditionals, file I/O)

**Two implementation approaches:**

**Option A: Full Preprocessing**
- Implement full GAMS preprocessor in Python
- Process directives before parsing
- Pros: Semantically correct, handles all directives
- Cons: Complex, weeks of work, out of scope for Sprint 7

**Option B: Mock/Skip Handling**
- Modify grammar to recognize and skip common directives
- Don't evaluate conditionals (assume true branch)
- Pros: Fast to implement, sufficient for many models
- Cons: May produce incorrect AST for complex conditional logic

### What Needs to Be Done

**Step 1: Survey GAMS preprocessor directives**

Catalog all GAMS preprocessor directives:
- Compile control: `$if`, `$ifI`, `$ifE`, `$else`, `$endif`
- Symbol definition: `$set`, `$setGlobal`, `$setLocal`, `$setEnv`
- File inclusion: `$include`, `$batInclude`, `$libInclude`
- Text blocks: `$ontext`, `$offtext`, `$comment`, `$onecho`, `$offecho`
- System calls: `$call`, `$echo`
- Options: `$onempty`, `$offempty`, `$on`/`$offOrder`

Identify which appear in GAMSLib failures.

**Step 2: Analyze directive complexity**

For each directive category:
- **Compile control:** Requires conditional AST construction
- **Symbol definition:** Requires symbol table with scoping
- **File inclusion:** Requires file system access and recursive parsing
- **Text blocks:** Requires lexer state management
- **System calls:** Requires subprocess execution (security risk)

Rank by complexity: Low (skip), Medium (mock), High (full preprocessing)

**Step 3: Prototype mock handling approach**

Design grammar modification to recognize and skip directives:

```lark
// Add to grammar
preprocessor_directive: "$" DIRECTIVE_NAME directive_args? NEWLINE
DIRECTIVE_NAME: "if" | "set" | "include" | "ontext" | "offtext" | ...
directive_args: /[^\n]+/

// In parser transformer
def preprocessor_directive(self, items):
    # Log directive seen, but don't process
    logger.debug(f"Skipping preprocessor directive: {items}")
    return None  # Omit from AST
```

Test on failed GAMSLib models:
- Does parser accept the file now?
- Does generated AST make sense?
- What breaks if we ignore conditionals?

**Step 4: Evaluate hybrid approach**

Consider hybrid: mock simple directives, fail on complex ones

- **Mock (safe):** `$set`, `$include` (if file exists), `$ontext`/`$offtext`
- **Fail (unsafe):** `$if`/`$else` (conditional logic), `$call` (side effects)
- Emit warning: "Preprocessor directive ignored, results may be incorrect"

**Step 5: Document recommendation**

Create `docs/research/preprocessor_directives.md`:
- Survey of directive types
- Complexity analysis
- Mock handling design (grammar changes, transformer updates)
- Test strategy
- Limitations and warnings
- Recommended approach for Sprint 7

**Changes:**

Completed comprehensive research on multi-dimensional indexing support in current IR implementation. Key findings:
- Surveyed 89 GAMS files across codebase: 71 use 1D indexing (96%), 7 use 2D indexing (4%), 0 use 3D+ indexing
- Analyzed current IR implementation in `src/ir/symbols.py`, `src/ir/ast.py`, `src/ad/index_mapping.py`
- **Discovered current IR already fully supports multi-dimensional indexing via tuple-based design**
- Verified normalization strategy preserves index semantics for nested sums (tested with test_simple_table.gms)
- Verified AD system handles multi-dim derivatives via tuple equality index matching
- Verified KKT module generates stationarity equations per instance correctly
- Identified parser blockers (set ranges `/ 1*6 /`, preprocessor directives `$if`) - not IR issues
- **Conclusion: 0 IR changes needed for Sprint 7** - current design supports arbitrary dimensions natively

**Result:**

Deliverable created: `docs/research/multidimensional_indexing.md` (comprehensive research document)
- **Section 1:** Background and current status (10% parse rate, 2 models with 2D indexing)
- **Section 2:** Pattern survey (frequency analysis: 96% 1D, 4% 2D, 0% 3D+)
- **Section 3:** Current IR design (tuple-based domains `domain: tuple[str, ...]` support arbitrary dimensions)
- **Section 4:** Normalization strategy (nested sum expansion with index binding)
- **Section 5:** Derivative computation (tuple equality for index matching `idx == var_indices`)
- **Section 6:** Grammar analysis (multi-dim syntax already supported)
- **Section 7:** Impact analysis - **0 changes needed** across all modules (Parser, IR, Normalization, AD, KKT)
- **Section 8:** Test cases (simple 2D, nested sum, conditional domain, 3D stress test)
- **Section 9:** Implementation plan - **0 hours effort** (no changes required)
- **Section 10:** Conclusion and recommendations

Updated `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md`:
- **Unknown 1.2:** ✅ VERIFIED - Current IR fully supports multi-dim with zero refactoring needed
  - Tuple-based design (`domain: tuple[str, ...]`) handles 1D/2D/3D/ND natively
  - Cross-product enumeration in AD system works for arbitrary dimensions
  - Working test: test_simple_table.gms with 2D parameter
- **Unknown 1.6:** ✅ VERIFIED - KKT stationarity generation already handles multi-dim correctly
  - Iterates over `enumerate_variable_instances()` which supports arbitrary dimensions
  - Generates `stat_X(i,j)` for each instance via cross-product
  - Gradient computation uses tuple equality for index matching

### Verification

```bash
# Research document should exist
test -f docs/research/preprocessor_directives.md

# Should contain required sections
grep -q "Directive Survey" docs/research/preprocessor_directives.md
grep -q "Complexity Analysis" docs/research/preprocessor_directives.md
grep -q "Mock Handling Design" docs/research/preprocessor_directives.md
grep -q "Recommendation" docs/research/preprocessor_directives.md

# Prototype should exist
test -f src/gams/grammar_preprocessor_mock.lark || \
  grep -q "preprocessor_directive" src/gams/grammar.lark
```

### Deliverables

- `docs/research/preprocessor_directives.md` (research document)
- Grammar prototype for mock directive handling
- Test cases for common directive patterns
- Recommendation: Full vs Mock vs Hybrid approach
- Implementation plan for Sprint 7 (effort estimate, risks)
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.1, 1.4, 1.11

### Acceptance Criteria

- [x] All GAMS preprocessor directives surveyed
- [x] Complexity analysis complete for each category
- [x] Mock handling approach designed with grammar changes
- [x] Prototype tested on ≥3 GAMSLib failures
- [x] Recommendation documented with pros/cons
- [x] Implementation effort estimated (Critical/High priority for Sprint 7)
- [x] Limitations and warnings documented
- [x] Unknowns 1.1, 1.4, 1.11 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 4: Research Multi-Dimensional Set Indexing

**Status:** ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 6-8 hours  
**Deadline:** 1 week before Sprint 7 Day 1  
**Owner:** Development team  
**Dependencies:** Task 2 (GAMSLib failure analysis) ✅  
**Unknowns Verified:** 1.2 ✅, 1.6 ✅

### Objective

Research multi-dimensional set indexing requirements, design IR representation and normalization strategy, and create implementation plan for Sprint 7.

### Why This Matters

Multi-dimensional indexing is fundamental to real-world GAMS models but currently unsupported. Required for expressions like:

```gams
Set i, j;
Parameter A(i,j), B(i,j,k);
Variable X(i,j);
Equation eq(i);
eq(i).. sum(j, A(i,j) * X(i,j)) =e= 0;
```

Without this, most practical models fail to parse. GAMSLib analysis (Task 2) will quantify impact.

### Background

Current parser supports:
- Single-dimensional indexing: `Variable X(i);`
- Simple summations: `sum(i, expr)`

Current parser does NOT support:
- Multi-dimensional parameters: `Parameter A(i,j);`
- Multi-dimensional variables: `Variable X(i,j,k);`
- Multi-dimensional sets: `Set ij(i,j);`
- Nested indexing in expressions: `A(i,j) + B(j,k)`

This impacts IR, normalization, and KKT derivative computation.

### What Needs to Be Done

**Step 1: Survey multi-dimensional indexing patterns**

From GAMSLib failures and literature, identify:
1. Parameter indexing: `A(i,j,k)`
2. Variable indexing: `X(i,j)`
3. Set tuples: `Set ij(i,j);`
4. Conditional indexing: `A(i,j)$(i.val < j.val)`
5. Index mapping: `sum((i,j), ...)`

Prioritize by frequency in GAMSLib.

**Step 2: Design IR representation**

Current IR stores:
```python
Variable(name="X", indices=["i"])
```

Proposed IR:
```python
Variable(name="X", indices=["i", "j", "k"])  # Multiple indices
Index(name="i", set_name="I")  # Link to set
IndexedRef(symbol="A", indices=["i", "j"])  # Reference with indices
```

Must support:
- Multiple indices per symbol
- Index order preservation
- Set membership validation

**Step 3: Design normalization strategy**

How to normalize multi-dimensional expressions:

Example:
```gams
eq(i).. sum(j, A(i,j) * X(i,j)) =e= 0;
```

Normalized IR:
```python
Equation(
  name="eq",
  indices=["i"],
  expr=Sum(
    index="j",
    expr=BinaryOp(
      op="*",
      left=IndexedRef(symbol="A", indices=["i", "j"]),
      right=IndexedRef(symbol="X", indices=["i", "j"])
    )
  )
)
```

**Step 4: Identify derivative computation impacts**

How does multi-dimensional indexing affect AD?

Derivative of `A(i,j) * X(i,j)` w.r.t. `X(k,l)`:
- If `(i,j) == (k,l)`: `A(i,j)`
- Otherwise: `0`

Need index matching logic in AD module.

**Step 5: Create grammar modifications**

Update grammar to support:
```lark
indexed_ref: ID "(" index_list ")"
index_list: ID ("," ID)*
```

**Step 6: Document design**

Create `docs/research/multidimensional_indexing.md`:
- Pattern survey
- IR design
- Normalization strategy
- Derivative computation approach
- Grammar modifications
- Test strategy

**Changes:**

1. Created `docs/planning/EPIC_2/SPRINT_7/TEST_PERFORMANCE_BASELINE.md` (comprehensive 400+ line analysis)
2. Generated profiling data files:
   - `test_profile.txt` - Full pytest --durations=50 output
   - `test_times_sorted.txt` - All test times sorted by duration
3. Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 2.1, 2.3, 2.4

**Result:**

✅ **Profiling Complete - Sprint 7 Optimization Highly Achievable**

**Key Findings:**
- **Total execution time:** 208.41s (full suite), 176.90s (core tests)
- **Pareto confirmed:** Top 4 tests (1.3%) = 66.7% of execution time
- **Test distribution:**
  - Production tests: 4 tests, 94.08s (53.2%)
  - Benchmark tests: 6 tests, 39.86s (22.5%)
  - Integration tests: 45 tests, 24.76s (14.0%)
  - PATH solver tests: 15 tests, 4.18s (2.4% - not a bottleneck)
- **Parallelization potential:** 95%+ of tests can be parallelized safely
- **Expected speedup:** 3.4x (4 workers) to 6.0x (8 workers)
- **Sprint 7 goal (<60s):** HIGH achievability with pytest-xdist

**Unknowns Verified:**
- ✅ **Unknown 2.1:** Pareto principle confirmed (1.3% of tests = 67% of time)
- ✅ **Unknown 2.3:** PATH solver tests are isolated and only 2.4% of time
- ✅ **Unknown 2.4:** pytest-xdist overhead estimated at 15-25% (reasonable)

### Verification

```bash
# Research document should exist
test -f docs/research/multidimensional_indexing.md

# Should contain required sections
grep -q "Pattern Survey" docs/research/multidimensional_indexing.md
grep -q "IR Design" docs/research/multidimensional_indexing.md
grep -q "Normalization Strategy" docs/research/multidimensional_indexing.md
grep -q "Grammar Modifications" docs/research/multidimensional_indexing.md
```

### Deliverables

- `docs/research/multidimensional_indexing.md` (research document)
- IR design for multi-dimensional symbols
- Normalization strategy with examples
- Grammar modification proposal
- Impact analysis (parser, IR, normalization, AD)
- Implementation plan for Sprint 7 (effort estimate, risks)
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.2, 1.6

### Acceptance Criteria

- [x] Multi-dimensional patterns surveyed (parameters, variables, sets)
- [x] IR design handles ≥3 indices per symbol
- [x] Normalization strategy preserves index semantics
- [x] Derivative computation approach designed
- [x] Grammar modifications drafted
- [x] Implementation effort estimated (High priority for Sprint 7)
- [x] Test cases identified (simple, nested, conditional)
- [x] Unknowns 1.2, 1.6 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 5: Profile Test Suite Performance

**Status:** ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 4-6 hours  
**Actual Time:** ~5 hours  
**Completed:** 2025-11-14  
**Owner:** Development team (Testing specialist)  
**Dependencies:** None  
**Unknowns Verified:** 2.1 ✅, 2.3 ✅, 2.4 ✅

### Objective

Profile full test suite to identify slow tests, categorize by type, and create baseline for Sprint 7 test performance optimization.

### Why This Matters

Sprint 6 test suite takes ~107 seconds for 1217 tests. Sprint 7 goal is <60s for fast tests, <120s for full suite. Without profiling data, optimization is guesswork.

**Key questions:**
- Which tests take >1 second?
- Are slow tests due to solver calls, file I/O, or computation?
- Can tests be parallelized safely?
- Which tests should be marked `@pytest.mark.slow`?

### Background

From Sprint 6:
- 1217 tests total
- Execution time: ~107 seconds (~88ms average per test)
- Some tests likely much slower (solver validation, golden files)
- No current profiling or slow test marking

From Sprint 6 retrospective:
- "Test execution time needs optimization (~107s for full suite)"
- "Profile slowest tests (likely validation tests with solver calls)"
- "Mark slow tests with `@pytest.mark.slow`"

### What Needs to Be Done

**Step 1: Run pytest with profiling**

```bash
# Profile full test suite
pytest --durations=50 > test_profile.txt

# Categorize test times
pytest --durations=0 | grep -E "^[0-9]" | sort -rn > test_times_sorted.txt
```

**Step 2: Categorize slow tests by type**

Group tests into categories:
- **Validation tests:** Tests calling GAMS/PATH solvers (likely slowest)
- **Golden file tests:** End-to-end tests comparing output files
- **Integration tests:** Cross-module tests
- **Unit tests:** Isolated component tests

For each category:
- Count of tests
- Total time
- Average time per test
- Slowest test

**Step 3: Identify parallelization blockers**

Analyze tests for:
- File I/O to shared locations (race condition risk)
- Global state mutations (test isolation issues)
- Subprocess calls (may need serialization)
- Solver calls (may have licensing limits)

**Step 4: Create test categorization strategy**

Design marking strategy:
```python
@pytest.mark.unit       # Fast, isolated (<100ms)
@pytest.mark.integration # Medium, cross-module (100ms-1s)
@pytest.mark.e2e        # Slower, end-to-end (1s-5s)
@pytest.mark.slow       # Slowest, solver calls (>5s)
```

**Step 5: Estimate parallelization speedup**

Calculate theoretical speedup:
- If 90% of time in 10% of tests: High speedup potential
- If evenly distributed: Low speedup potential

Estimate speedup for 4 workers, 8 workers.

**Step 6: Document findings**

Create `docs/planning/EPIC_2/SPRINT_7/TEST_PERFORMANCE_BASELINE.md`:
- Full test suite profile (50 slowest tests)
- Test categorization by type
- Parallelization blocker analysis
- Recommended marking strategy
- Speedup estimates
- Implementation plan for Sprint 7

**Changes:**

1. Created `docs/planning/EPIC_2/PARSER_ROADMAP.md` (comprehensive parser feature catalog and roadmap)
2. Cataloged **52 GAMS syntax features** across 5 categories:
   - Preprocessing & Macros: 7 features
   - Set Features: 9 features
   - Parameter & Data Features: 8 features
   - Variable & Equation Features: 10 features
   - Statement & Control Features: 18 features
3. Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.3, 1.9, 1.10

**Result:**

✅ **Complete Parser Roadmap for Sprints 8-10**

**Feature Catalog:**
- 52 GAMS features cataloged and analyzed
- Current support status documented (21 features already supported ✅)
- 31 features identified for future implementation

**GAMSLib Usage Analysis:**
- Cross-referenced 9 failed models with feature requirements
- No single feature dominates (steady progress across categories needed)
- Feature frequency: Preprocessor (22%), Model declaration (22%), Set range (11%), etc.

**ROI Rankings:**
- **Tier 1 (Excellent ROI >4.0):** Models keyword (10.0), Multiple scalars (6.7), Model declaration (4.0)
- **Tier 2 (Good ROI 2.0-4.0):** Variable attributes (3.3), Preprocessor (2.5), Set range (2.5), Option statements (2.5), Solve with objective (2.0)
- **Tier 3 (Moderate ROI 1.0-2.0):** Indexed assignments (1.7), Indexed sets (1.7)
- **Tier 4 (Low ROI <1.0):** Display, loops, file I/O, etc.

**Sprint Roadmaps:**
- **Sprint 8 (Wave 2):** 6 features, 19-28 hours, 60-70% parse rate (ROI: 1.7-2.4% per hour)
- **Sprint 9 (Wave 3):** 7 features, 35-46 hours, 80% parse rate (ROI: 0.3-0.6% per hour)
- **Sprint 10 (Wave 4):** 10 features, 36-52 hours, 90% parse rate (ROI: 0.2-0.3% per hour)
- **Total:** 90-126 hours to achieve 90% parse rate

**Dependency Graph:**
- No blocking circular dependencies
- Features mostly independent (can parallelize)
- Preprocessor features are foundational (many models use them)

**Unknowns Verified:**
- ✅ **Unknown 1.3:** Enhanced with roadmap insights - Sprint 7 target (30-40%) is conservative, clear path to 90% by Sprint 10
- ✅ **Unknown 1.9:** Equation attributes can be deferred to Sprint 9 (not blocking any models)
- ✅ **Unknown 1.10:** Assignments already supported for Sprint 7, enhance with indexed assignments in Sprint 8

### Verification

```bash
# Baseline document should exist
test -f docs/planning/EPIC_2/SPRINT_7/TEST_PERFORMANCE_BASELINE.md

# Should contain required sections
grep -q "Test Profile" docs/planning/EPIC_2/SPRINT_7/TEST_PERFORMANCE_BASELINE.md
grep -q "Categorization" docs/planning/EPIC_2/SPRINT_7/TEST_PERFORMANCE_BASELINE.md
grep -q "Parallelization" docs/planning/EPIC_2/SPRINT_7/TEST_PERFORMANCE_BASELINE.md
grep -q "Speedup Estimates" docs/planning/EPIC_2/SPRINT_7/TEST_PERFORMANCE_BASELINE.md

# Profile data should exist
test -f test_profile.txt
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_7/TEST_PERFORMANCE_BASELINE.md`
- Test profiling data (50+ slowest tests)
- Test categorization by type (unit/integration/e2e/slow)
- Parallelization blocker analysis
- Speedup estimates for 4/8 workers
- Recommended test marking strategy
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 2.1, 2.3, 2.4

### Acceptance Criteria

- [x] Full test suite profiled (--durations=50 minimum) ✅
- [x] Slowest tests identified (top 20 with times) ✅ Top 50 identified
- [x] Tests categorized by type (unit/integration/e2e/slow) ✅ 8 categories
- [x] Parallelization blockers documented ✅ 95%+ parallelizable
- [x] Speedup estimates calculated ✅ 3.4x-6.0x expected
- [x] Implementation plan for Sprint 7 created ✅ 4-phase plan, 11-16h effort
- [x] Unknowns 2.1, 2.3, 2.4 verified and updated in KNOWN_UNKNOWNS.md ✅

---

## Task 6: Survey GAMS Syntax Features for Wave 2

**Status:** ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 4-6 hours  
**Actual Time:** ~5 hours  
**Completed:** 2025-11-14  
**Owner:** Development team (Parser specialist)  
**Dependencies:** Task 2 (GAMSLib failure analysis)  
**Unknowns Verified:** 1.3 ✅ (enhanced), 1.9 ✅, 1.10 ✅

### Objective

Survey GAMS syntax features beyond Sprint 7 scope to plan parser roadmap for Sprint 8+ and identify dependencies between features.

### Why This Matters

Sprint 7 focuses on preprocessor directives and multi-dimensional indexing (Wave 1). But GAMSLib models likely use many more features. Understanding the full landscape helps:
- Sequence features correctly (foundation features before dependent features)
- Estimate total parser work (Sprint 8, 9, 10 scoping)
- Identify diminishing returns (when to stop parser expansion)

### Background

From PROJECT_PLAN.md Sprint 8:
- "Multi-dimensional sets, equation attributes, conditional expressions, selected display/option statements"
- Target: ≥50% parse rate

Need to catalog all missing GAMS features and prioritize for Sprints 8-10.

### What Needs to Be Done

**Step 1: Catalog GAMS syntax features**

Survey GAMS documentation and GAMSLib models for:

**Set features:**
- Range syntax: `Set i /1*10/`
- Tuples: `Set ij(i,j)`
- Indexed sets: `Set active(i)`
- Set operations: `union`, `intersect`, `card`

**Parameter features:**
- Table declarations: `Table A(i,j) ...`
- Data statements: `Parameter A(i) /1 5, 2 10/`
- Conditional assignment: `A(i)$(i.val > 5) = ...`

**Variable/Equation features:**
- Attributes: `.l`, `.m`, `.lo`, `.up`
- Equation types: `=n=` (nonlinear), `=x=` (external)
- Equation attributes: `.range`, `.slack`

**Expression features:**
- Conditionals: `expr$(condition)`
- Special functions: `card()`, `ord()`, `smax()`, `smin()`
- Set membership: `i in Set`

**Statement features:**
- Assignments: `scalar x; x = 5;`
- Loops: `loop(i, ...)`
- Display: `display x;`
- Options: `option limrow = 0;`

**Step 2: Cross-reference with GAMSLib failures**

For each feature, identify:
- How many GAMSLib models use it?
- Is it a blocker for parsing or just for full semantics?
- Is it used in objective/constraints (critical) or just setup (less critical)?

**Step 3: Create dependency graph**

Some features depend on others:
- Conditional expressions depend on set membership
- Equation attributes depend on equation parsing
- Table declarations depend on multi-dimensional indexing

Build dependency graph to sequence features correctly.

**Step 4: Estimate effort and impact**

For each feature:
- **Effort:** Low (<4h), Medium (4-8h), High (8-16h), Very High (>16h)
- **Impact:** Number of models unlocked
- **ROI:** Impact / Effort

**Step 5: Create roadmap**

Group features into:
- **Sprint 7 (Wave 1):** Preprocessor, multi-dim indexing (already planned)
- **Sprint 8 (Wave 2):** Top 5 ROI features from analysis
- **Sprint 9 (Wave 3):** Next 5 ROI features
- **Sprint 10 (Wave 4):** Remaining features or diminishing returns

**Step 6: Document survey**

Create `docs/planning/EPIC_2/PARSER_ROADMAP.md`:
- Complete feature catalog
- GAMSLib usage analysis
- Dependency graph
- Effort/impact estimates
- Recommended roadmap for Sprints 7-10

**Changes:**

Created comprehensive line number tracking design with complete implementation plan:

1. **Created `docs/design/line_number_tracking.md`** (350+ lines)
   - Confirmed Lark metadata support (tree.meta.line, tree.meta.column)
   - Designed SourceLocation dataclass (line, column, end_line, end_column, source_file)
   - Designed IR node updates (EquationDef, VariableDef, ParameterDef with loc field)
   - Designed parser metadata extraction (_extract_location helper)
   - Designed normalization preservation (inherit parent location)
   - Designed convexity detection usage (pass eq.loc to warnings)
   - Designed warning formatter updates (display "file.gms:line:column")
   - Handled 6 edge cases (generated nodes, multi-line, includes, macros, expressions, indexed equations)
   - Created 5-phase implementation plan (3-4 hours total)
   - Designed testing strategy (7 unit tests + 1 integration test)

2. **Updated `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md`**
   - Verified Unknown 4.1 (Can line numbers be tracked through pipeline?)
   - Status: ✅ VERIFIED - fully feasible with Lark metadata
   - Added comprehensive verification results with design decisions
   - Documented implementation effort (3-4 hours)
   - Documented testing strategy and edge cases

**Result:**

Deliverable created: `docs/design/line_number_tracking.md`
- Complete design for line number tracking through parser → IR → normalization → convexity pipeline
- SourceLocation dataclass with line, column, file tracking
- Parser integration plan using Lark tree.meta
- Normalization preservation strategy (inherit parent location)
- Warning format: "W301 in equation 'circle_eq' (file.gms:15:8): message"
- All edge cases handled (generated nodes, multi-line, includes)
- Implementation effort: 3-4 hours for Sprint 7
- Testing: 7 unit tests + 1 E2E integration test

Verified Unknown 4.1:
- ✅ Lark provides full metadata support (line, column, end_line, end_column)
- ✅ Performance impact negligible (<1% overhead)
- ✅ Normalization preservation straightforward
- ✅ Line number tracking fully feasible and ready for Sprint 7

### Verification

```bash
# Roadmap document should exist
test -f docs/planning/EPIC_2/PARSER_ROADMAP.md

# Should contain required sections
grep -q "Feature Catalog" docs/planning/EPIC_2/PARSER_ROADMAP.md
grep -q "Dependency Graph" docs/planning/EPIC_2/PARSER_ROADMAP.md
grep -q "Roadmap" docs/planning/EPIC_2/PARSER_ROADMAP.md
```

### Deliverables

- `docs/planning/EPIC_2/PARSER_ROADMAP.md`
- Complete GAMS feature catalog (30-50 features)
- GAMSLib usage analysis (which models use which features)
- Feature dependency graph
- Effort/impact estimates for top 20 features
- Recommended roadmap for Sprints 8-10
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.3, 1.9, 1.10

### Acceptance Criteria

- [x] GAMS features cataloged (≥30 features across 5 categories) ✅ 52 features across 5 categories
- [x] GAMSLib usage analyzed (feature frequency in failed models) ✅ Cross-referenced 9 models
- [x] Dependency graph created ✅ No blocking circular dependencies
- [x] Effort/impact estimated for top 20 features ✅ All 52 features analyzed with ROI rankings
- [x] Roadmap drafted for Sprints 8-10 ✅ Wave 2 (Sprint 8), Wave 3 (Sprint 9), Wave 4 (Sprint 10)
- [x] Cross-referenced with PROJECT_PLAN.md targets ✅ Aligns with Sprint 8-10 parse rate goals
- [x] Unknowns 1.3, 1.9, 1.10 verified and updated in KNOWN_UNKNOWNS.md ✅

---

## Task 7: Design Line Number Tracking for Warnings

**Status:** ✅ COMPLETE  
**Priority:** Medium  
**Estimated Time:** 3-4 hours  
**Deadline:** Before Sprint 7 Day 1  
**Owner:** Development team  
**Dependencies:** None  
**Unknowns Verified:** 4.1

### Objective

Design approach to track line numbers through parser → IR → normalization → convexity detection pipeline, enabling warnings with line number citations.

### Why This Matters

From Sprint 6 Known Unknowns (deferred Unknown 1.7):
- Current convexity warnings don't cite line numbers
- Users can't easily locate problematic equations
- UX improvement: "W301 in equation 'circle_eq' (line 15)"

From Sprint 6 retrospective action items:
- "Add line numbers to convexity warnings"
- Medium priority for Sprint 7

### Background

Current warning format:
```
W301: Nonlinear equality constraint detected
   Equation: circle_eq
   Docs: https://...
```

Desired format:
```
W301: Nonlinear equality constraint detected
   Equation: circle_eq (line 15)
   Expression: x**2 + y**2 =e= 4
   Docs: https://...
```

Requires tracking line numbers from parse tree through IR transformations.

### What Needs to Be Done

**Step 1: Survey Lark parser line number support**

Lark provides meta information:
```python
from lark import Tree
tree.meta.line  # Line number
tree.meta.column  # Column number
```

Test: Can we access line numbers in transformer?

**Step 2: Design IR metadata**

Add metadata to IR nodes:
```python
@dataclass
class Equation:
    name: str
    expr: Expr
    eq_type: str
    indices: List[str]
    meta: Optional[Metadata] = None  # NEW

@dataclass
class Metadata:
    line: int
    column: int
    source_file: str
```

**Step 3: Track through normalization**

Normalization transforms IR. Must preserve metadata:
```python
def normalize_equation(eq: Equation) -> Equation:
    new_expr = normalize_expr(eq.expr)
    return Equation(
        name=eq.name,
        expr=new_expr,
        eq_type=eq.eq_type,
        indices=eq.indices,
        meta=eq.meta  # Preserve metadata
    )
```

**Step 4: Use in convexity detection**

```python
def detect_nonlinear_equality(eq: Equation) -> List[Warning]:
    if eq.eq_type == "=e=" and is_nonlinear(eq.expr):
        return [Warning(
            code="W301",
            equation=eq.name,
            line=eq.meta.line if eq.meta else None,  # Use line number
            column=eq.meta.column if eq.meta else None
        )]
    return []
```

**Step 5: Format warning output**

Update warning formatter to include line/column:
```python
def format_warning(warning: Warning) -> str:
    location = f" (line {warning.line})" if warning.line else ""
    return f"{warning.code}: {warning.message}\n" \
           f"   Equation: {warning.equation}{location}\n"
```

**Step 6: Handle edge cases**

- IR nodes created during normalization (no source location)
- Multi-line equations (which line to cite?)
- Included files (how to show file path?)

**Step 7: Document design**

Create `docs/design/line_number_tracking.md`:
- Parser metadata extraction
- IR metadata design
- Normalization metadata preservation
- Convexity detection usage
- Warning formatter updates
- Edge case handling

**Changes:**

Created comprehensive CI regression tracking design with 3 deliverables. Key achievements:

**1. CI Design Document (`docs/ci/gamslib_regression_tracking.md`):**
- 85-page comprehensive design covering all aspects of CI automation
- 13 sections: Executive Summary, Background, Current Process Analysis, CI Trigger Strategy, Workflow Design, Regression Logic, Auto-Commit Strategy, Timeout/Performance, Security, Implementation Plan, Testing Strategy, Known Unknowns Verification, Future Enhancements
- Detailed comparison of 3 trigger strategies → Hybrid approach (path filter + weekly scheduled)
- Security analysis: auto-commit vs manual commit → Manual commit recommended
- Regression threshold analysis: absolute vs relative → 10% relative threshold recommended
- 5-phase implementation plan with time estimates (4-5 hours total)
- Performance optimization: <5 minutes CI time using cached models
- Security considerations: minimal permissions, no write access needed

**2. Regression Detection Script (`scripts/check_parse_rate_regression.py`):**
- Full implementation with error handling (not stub)
- Reads current parse rate from JSON report
- Reads baseline from git branch (via `git show`)
- Calculates relative drop: `(baseline - current) / baseline`
- Exits 1 if drop >10% (configurable via `--threshold`)
- Handles edge cases: 0% baseline, improvement, unchanged
- Detailed regression report output with recommendations
- CLI arguments: `--current`, `--baseline`, `--baseline-file`, `--threshold`
- 250+ lines with comprehensive error handling

**3. CI Workflow YAML (`.github/workflows/gamslib-regression.yml`):**
- Hybrid trigger: path filter (parser files) + weekly schedule (Sunday 00:00 UTC)
- Minimal permissions: `contents: read`, `pull-requests: read`
- 10-minute timeout (2x expected time)
- Full history checkout for baseline comparison
- GAMSLib caching (skip download if already present)
- Regression check with configurable threshold
- Artifact upload (always, even on failure)
- Dashboard commit check (fails CI if not committed)
- Manual trigger support (`workflow_dispatch`)

**4. Verified 3 Known Unknowns in `KNOWN_UNKNOWNS.md`:**
- **Unknown 3.2:** Auto-commit vs manual → Manual commit recommended (security)
- **Unknown 3.3:** Regression threshold → 10% relative threshold recommended
- **Unknown 5.1:** Trigger strategy → Hybrid (path filter + weekly scheduled)

**Result:**

Deliverables created: `docs/ci/gamslib_regression_tracking.md` (comprehensive CI design), `scripts/check_parse_rate_regression.py` (regression detection script), `.github/workflows/gamslib-regression.yml` (CI workflow)

**Design Decisions:**
1. **Trigger strategy:** Hybrid (path filter + weekly scheduled) - reduces runs by ~80%, saves ~8 hours CI time/year
2. **Regression threshold:** 10% relative drop - industry standard, adapts to baseline
3. **Auto-commit:** Manual commit required - more secure, maintains PR review process
4. **Timeout:** 10 minutes - 2x expected time, fast enough for PR feedback
5. **Permissions:** Minimal (`contents: read`) - principle of least privilege
6. **Baseline comparison:** Use `git show main:reports/...` - no extra files needed

**Edge Cases Handled:**
- Baseline = 0% (cannot regress from zero)
- Parse rate improves (pass CI with success message)
- Parse rate unchanged (pass CI silently)
- Small drop <10% (pass CI, minor variation acceptable)
- Dashboard not committed (fail CI with helpful message)
- Git command failures (exit 2 with error details)

**Security Considerations:**
- No write permissions needed (read-only)
- No auto-commit (prevents bot from pushing malicious code)
- Token security: uses built-in `GITHUB_TOKEN` (scoped to repo)
- Output validation: dashboard is generated data (no code injection)
- Minimal attack surface: parser is read-only, no subprocess execution

**Implementation Effort:** 4-5 hours actual (matches estimate)

**Unknowns Verified:**
- **3.2:** Manual commit is safer and recommended (no write permissions, maintains transparency)
- **3.3:** 10% relative threshold is appropriate (industry standard, adapts to scale)
- **5.1:** Hybrid trigger is optimal (efficiency + safety net)

**Future Enhancements Identified:**
1. Historical trend tracking (Sprint 8)
2. Conversion/solve rate tracking (Sprint 9)
3. Performance benchmarking (Sprint 10)
4. Full GAMSLib suite nightly (Sprint 11)

### Verification

```bash
# Design document should exist
test -f docs/design/line_number_tracking.md

# Should contain required sections
grep -q "Parser Metadata" docs/design/line_number_tracking.md
grep -q "IR Metadata" docs/design/line_number_tracking.md
grep -q "Normalization" docs/design/line_number_tracking.md
```

### Deliverables

- `docs/design/line_number_tracking.md` (design document)
- IR metadata structure design
- Normalization metadata preservation strategy
- Warning formatter updates
- Edge case handling approach
- Implementation plan for Sprint 7
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknown 4.1

### Acceptance Criteria

- [x] Lark parser line number support confirmed ✅
- [x] IR metadata structure designed ✅
- [x] Normalization preservation strategy documented ✅
- [x] Warning formatter updates specified ✅
- [x] Edge cases identified and solutions proposed ✅
- [x] Implementation effort estimated (Medium priority for Sprint 7) ✅ 3-4 hours
- [x] Unknown 4.1 verified and updated in KNOWN_UNKNOWNS.md ✅

---

## Task 8: Set Up CI for GAMSLib Regression Tracking

**Status:** ✅ COMPLETE  
**Priority:** Medium  
**Estimated Time:** 4-5 hours  
**Actual Time:** ~5 hours  
**Deadline:** Before Sprint 7 Day 1  
**Owner:** DevOps/Development team  
**Dependencies:** None  
**Unknowns Verified:** 3.2 ✅, 3.3 ✅, 5.1 ✅

### Objective

Design CI workflow for automated GAMSLib ingestion, dashboard updates, and parse rate regression detection.

### Why This Matters

From Sprint 6 retrospective:
- "GAMSLib dashboard updates currently manual (need CI automation)"
- "No regression tracking (can't detect if parse rate drops)"

Manual process risks:
- Forgetting to re-run after parser changes
- No continuous monitoring of benchmark progress
- Silent regressions (parse rate drops unnoticed)

### Background

Current process:
1. Developer runs `make ingest-gamslib` manually
2. Dashboard `docs/status/GAMSLIB_CONVERSION_STATUS.md` generated
3. Developer commits dashboard (or forgets)
4. No alerting if parse rate decreases

Desired process:
1. PR modifies parser code
2. CI automatically runs GAMSLib ingestion
3. Dashboard auto-updated (or CI fails if not committed)
4. CI fails if parse rate drops >10% (regression detection)

### What Needs to Be Done

**Step 1: Design CI trigger strategy**

Options:
- **Option A:** Run on every PR (thorough but slow)
- **Option B:** Run only on parser-related file changes
- **Option C:** Run on schedule (nightly) + parser changes

Recommended: Option B (parser changes) + Option C (weekly scheduled run)

Trigger files:
- `src/gams/grammar.lark`
- `src/gams/parser.py`
- `src/ir/*.py` (if parser depends on IR)

**Step 2: Design CI job workflow**

```yaml
name: GAMSLib Regression Check

on:
  pull_request:
    paths:
      - 'src/gams/grammar.lark'
      - 'src/gams/parser.py'
      - 'src/ir/*.py'
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  gamslib-ingestion:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -e .
      
      - name: Run GAMSLib ingestion
        run: make ingest-gamslib
      
      - name: Check for dashboard changes
        run: |
          if git diff --quiet docs/status/GAMSLIB_CONVERSION_STATUS.md; then
            echo "No dashboard changes detected - skipping parse rate check"
          else
            echo "Dashboard changes detected - checking parse rate..."
          fi
      
      - name: Detect parse rate regression
        run: python scripts/check_parse_rate_regression.py
      
      - name: Upload dashboard artifact
        uses: actions/upload-artifact@v3
        with:
          name: gamslib-dashboard
          path: docs/status/GAMSLIB_CONVERSION_STATUS.md
```

**Step 3: Design regression detection script**

Create `scripts/check_parse_rate_regression.py`:
```python
# Note: This is a design example. Helper functions like read_parse_rate() and 
# read_parse_rate_from_main() need to be implemented with proper error handling.

import sys
import json
from pathlib import Path

def read_parse_rate(json_path: str) -> float:
    """
    Read parse rate from GAMSLib ingestion JSON report.
    
    Args:
        json_path: Path to JSON report file
        
    Returns:
        Parse rate as float (e.g., 30.0 for 30%)
        
    Raises:
        FileNotFoundError: If JSON file doesn't exist
        json.JSONDecodeError: If JSON is malformed
        KeyError: If expected parse_rate field is missing
    """
    # TODO: Implement with error handling
    pass

def read_parse_rate_from_main() -> float:
    """
    Read baseline parse rate from main branch.
    
    Fetches the latest JSON report from main branch using git show.
    
    Returns:
        Baseline parse rate as float (e.g., 10.0 for 10%)
        
    Raises:
        subprocess.CalledProcessError: If git command fails
        FileNotFoundError: If baseline file doesn't exist on main
        json.JSONDecodeError: If baseline JSON is malformed
        KeyError: If expected parse_rate field is missing
    """
    # TODO: Implement using subprocess.run(['git', 'show', 'main:reports/...'])
    pass

def check_regression():
    # Read current parse rate from JSON report
    current_rate = read_parse_rate("reports/gamslib_ingestion_sprint7.json")
    
    # Read baseline from main branch
    baseline_rate = read_parse_rate_from_main()
    
    # Check for regression (>10% drop)
    if current_rate < baseline_rate * 0.9:
        print(f"REGRESSION: Parse rate dropped from {baseline_rate}% to {current_rate}%")
        sys.exit(1)
    else:
        print(f"OK: Parse rate {current_rate}% (baseline {baseline_rate}%)")
```

**Step 4: Design auto-commit strategy**

Options:
- **Option A:** CI auto-commits dashboard changes (requires write permission)
- **Option B:** CI fails if dashboard not committed (developer commits manually)
- **Option C:** CI posts comment with dashboard diff (no auto-commit)

Recommended: Option B (fail if not committed) for security/transparency

**Step 5: Handle CI timeout**

GAMSLib ingestion should complete in <5 minutes. If timeout:
- Cache downloaded GAMSLib models
- Limit to top 10-20 models (not full suite)
- Parallelize ingestion

**Step 6: Document CI design**

Create `docs/ci/gamslib_regression_tracking.md`:
- Trigger strategy
- CI job workflow
- Regression detection logic
- Auto-commit strategy
- Timeout handling
- Implementation plan

**Changes:**

*To be completed*

**Result:**

*To be completed*

### Verification

```bash
# CI design document should exist
test -f docs/ci/gamslib_regression_tracking.md

# Regression script should exist (can be stub)
test -f scripts/check_parse_rate_regression.py

# CI workflow should exist (can be draft)
test -f .github/workflows/gamslib-regression.yml || \
  grep -q "gamslib" docs/ci/gamslib_regression_tracking.md
```

### Deliverables

- `docs/ci/gamslib_regression_tracking.md` (design document)
- `.github/workflows/gamslib-regression.yml` (CI workflow draft)
- `scripts/check_parse_rate_regression.py` (regression detection script)
- Trigger strategy (files to watch)
- Auto-commit strategy decision
- Timeout handling approach
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 3.2, 3.3, 5.1

### Acceptance Criteria

- [x] CI trigger strategy designed (when to run)
- [x] CI job workflow drafted (.github/workflows)
- [x] Regression detection script created
- [x] Threshold defined (>10% drop = fail)
- [x] Auto-commit strategy decided
- [x] Timeout handling designed (<10min limit)
- [x] Implementation effort estimated (Medium priority for Sprint 7)
- [x] Unknowns 3.2, 3.3, 5.1 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 9: Create Parser Test Fixture Strategy

**Status:** ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 3-4 hours  
**Actual Time:** ~3 hours  
**Completed:** 2025-11-15  
**Owner:** Development team (Testing specialist)  
**Dependencies:** Tasks 2, 3, 4 (parser research) ✅  
**Unknowns Verified:** Uses findings from Tasks 2, 3, 4 to design comprehensive test coverage

### Objective

Design test fixture strategy for new parser features (preprocessor, multi-dimensional indexing), ensuring comprehensive coverage without test bloat.

### Why This Matters

Sprint 7 adds complex parser features. Without systematic test fixture design:
- Tests duplicate effort (same patterns tested multiple times)
- Edge cases missed (untested combinations)
- Test maintenance burden (hard to update)
- Unclear coverage (which features are tested?)

Need structured approach to test fixtures.

### Background

From Sprint 6:
- 1217 tests total
- Convexity tests used `tests/fixtures/convexity/` with 18 models + README
- Good model: Organized fixtures with expected results documented

Sprint 7 will add:
- Preprocessor directive tests
- Multi-dimensional indexing tests
- Advanced GAMS feature tests

Need unified strategy across all parser features.

### What Needs to Be Done

**Step 1: Review existing test fixtures**

Catalog current fixtures:
- `tests/fixtures/convexity/` - 18 models, expected results in YAML
- `tests/golden/` - End-to-end golden files
- `examples/` - Example models (not systematic tests)

Identify patterns:
- Fixture organization (by feature)
- Expected results documentation (YAML, README)
- Positive vs negative tests

**Step 2: Design fixture hierarchy**

Proposed structure:
```
tests/fixtures/
  convexity/           # Existing
  preprocessor/        # NEW Sprint 7
    simple_set.gms     # $set directive
    conditional.gms    # $if/$else
    include.gms        # $include
    text_block.gms     # $ontext/$offtext
    expected.yaml      # Expected parse results
    README.md          # Fixture documentation
  multidim/            # NEW Sprint 7
    parameter_2d.gms   # Parameter A(i,j)
    variable_3d.gms    # Variable X(i,j,k)
    nested_sum.gms     # sum((i,j), ...)
    expected.yaml
    README.md
  advanced/            # NEW Sprint 7 (Wave 2 prep)
    table_decl.gms
    set_range.gms
    expected.yaml
    README.md
```

**Step 3: Design expected results format**

Use YAML for expected results:
```yaml
# tests/fixtures/preprocessor/expected.yaml
simple_set:
  should_parse: true
  symbols_defined:
    - name: size
      type: scalar
      value: 10
  warnings: []

conditional:
  should_parse: true
  branches_taken:
    - if: true
    - else: false
  warnings:
    - "Preprocessor directive ignored, assuming true branch"
```

**Step 4: Design test case generation**

Use parametrized tests:
```python
import pytest
import yaml

@pytest.fixture
def preprocessor_fixtures():
    with open("tests/fixtures/preprocessor/expected.yaml") as f:
        return yaml.safe_load(f)

@pytest.mark.parametrize("fixture_name", [
    "simple_set",
    "conditional",
    "include",
    "text_block"
])
def test_preprocessor_parsing(fixture_name, preprocessor_fixtures):
    model_path = f"tests/fixtures/preprocessor/{fixture_name}.gms"
    expected = preprocessor_fixtures[fixture_name]
    
    # Test parsing
    result = parse_file(model_path)
    assert result.success == expected["should_parse"]
    
    # Test symbols
    if expected["should_parse"]:
        for symbol in expected["symbols_defined"]:
            assert symbol["name"] in result.symbols
```

**Step 5: Design fixture documentation**

Each fixture directory needs README.md:
- Purpose of fixtures
- How to add new fixtures
- How to update expected results
- Cross-references to features tested

**Step 6: Identify coverage gaps**

From Tasks 2, 3, 4 research, identify:
- Which parser features need fixtures?
- How many test cases per feature?
- Which combinations need testing?

Create coverage matrix:
| Feature | Simple | Nested | Error | Total |
|---------|--------|--------|-------|-------|
| Preprocessor $set | ✅ | - | ✅ | 2 |
| Preprocessor $if | ✅ | ✅ | ✅ | 3 |
| Multi-dim param | ✅ | ✅ | ✅ | 3 |
| ... | ... | ... | ... | ... |

**Step 7: Document strategy**

Create `docs/testing/PARSER_FIXTURE_STRATEGY.md`:
- Fixture hierarchy
- Expected results format
- Test case generation approach
- Fixture documentation requirements
- Coverage matrix
- Implementation checklist for Sprint 7

**Changes:**

Created comprehensive parser test fixture strategy with complete implementation plan:

1. **Created `docs/testing/PARSER_FIXTURE_STRATEGY.md`** (comprehensive 1000+ line strategy document)
   - Designed 4-directory hierarchy (preprocessor, sets, multidim, statements)
   - Extended YAML schema from convexity pattern to support parser features
   - Designed parametrized test approach following successful convexity pattern
   - Created README.md and fixture header comment templates
   - Built coverage matrix for 41 Sprint 7 fixtures across 4 categories
   - Created detailed 7-phase implementation checklist for Sprint 7
   - Documented Sprint 8-10 roadmap (60+ total fixtures planned)
   - Included complete YAML schema reference and 3 example fixtures

2. **Fixture Hierarchy Design:**
   - `tests/fixtures/preprocessor/` - 9 fixtures (Critical/High priority)
   - `tests/fixtures/sets/` - 8 fixtures (Critical/High priority)
   - `tests/fixtures/multidim/` - 8 fixtures (High/Medium priority)
   - `tests/fixtures/statements/` - 9 fixtures (Critical/High/Medium priority)
   - **Total:** 34 fixture files, 40 test cases (24 positive, 3 negative, 13 edge cases)

3. **Expected Results Format:**
   - Extended YAML schema with parser-specific fields:
     - `symbols_defined` - List of expected IR symbols
     - `preprocessor_actions` - Directive processing expectations
     - `expression_structure` - Complex expression validation
   - Documented complete schema in Appendix B
   - Provided example YAML files for all 4 categories

4. **Test Case Generation:**
   - Parametrized test pattern using `@pytest.mark.parametrize`
   - 4 test files: `test_preprocessor.py`, `test_sets.py`, `test_multidim.py`, `test_statements.py`
   - DRY principle - single test function validates all fixtures per category
   - Expected execution time: <2s for all 35 fixtures (<5s target ✅)

5. **Documentation Templates:**
   - README.md template with 9 sections (overview, catalog, usage, validation, etc.)
   - Fixture header comment template with purpose, expected outcome, references
   - File manifest template
   - Version history template

6. **Coverage Matrix:**
   - Mapped 26 parser features across 4 categories
   - Identified coverage for Sprint 7 (34 fixture files, 40 test cases), Sprint 8 (15-20), Sprint 9 (20-25), Sprint 10 (15-20)
   - Prioritized fixtures: 7 Critical, 14 High, 13 Medium
   - Identified gaps deferred to Sprints 8-10 (tables, conditionals, loops, etc.)

7. **Implementation Checklist:**
   - 7-phase plan: Directory setup → Preprocessor → Sets → MultiDim → Statements → Integration → Validation
   - Detailed tasks for each phase with checkboxes
   - Cross-referenced with Tasks 2, 3, 4 (parser research)
   - Acceptance criteria: 35+ fixtures, <5s execution, 100% feature coverage

**Result:**

Deliverable created: `docs/testing/PARSER_FIXTURE_STRATEGY.md` (comprehensive test fixture strategy)

**Strategy Summary:**
- **Fixture hierarchy:** 4 directories, 34 fixture files (40 test cases) for Sprint 7, 60+ total planned (Sprints 7-10)
- **YAML schema:** Extended from convexity pattern with parser-specific fields
- **Test pattern:** Parametrized tests following proven convexity approach
- **Documentation:** README + header templates ensure maintainability
- **Coverage:** 100% of Sprint 7 parser features (preprocessor, sets, multidim, statements)
- **Execution time:** <2s estimated (well under <5s target)
- **Implementation effort:** 3-4 hours for Sprint 7 fixture creation

**Key Design Decisions:**
1. **Reuse convexity pattern:** YAML + parametrized tests proven successful
2. **Minimal fixtures:** <30 lines each, ONE feature per file
3. **4-directory hierarchy:** Organized by feature category (not syntax)
4. **Progressive complexity:** simple_ → nested_ → complex_ naming
5. **Documentation-first:** README + header comments required for all fixtures
6. **Roadmap planning:** Sprints 8-10 fixtures identified (tables, conditionals, loops)

**Cross-References:**
- Task 2: GAMSLib Failure Analysis (feature priorities)
- Task 3: Preprocessor Directive Research (9 fixtures planned)
- Task 4: Multi-Dimensional Indexing Research (9 fixtures planned)
- Task 6: Parser Roadmap (Sprint 8-10 fixture planning)
- Convexity pattern: `tests/fixtures/convexity/` (template to replicate)

### Verification

```bash
# Strategy document should exist
test -f docs/testing/PARSER_FIXTURE_STRATEGY.md

# Should contain required sections
grep -q "Fixture Hierarchy" docs/testing/PARSER_FIXTURE_STRATEGY.md
grep -q "Expected Results Format" docs/testing/PARSER_FIXTURE_STRATEGY.md
grep -q "Coverage Matrix" docs/testing/PARSER_FIXTURE_STRATEGY.md
```

### Deliverables

- `docs/testing/PARSER_FIXTURE_STRATEGY.md`
- Fixture hierarchy design
- Expected results format (YAML schema)
- Test case generation approach (parametrized tests)
- Fixture documentation template (README.md)
- Coverage matrix (features × test types)
- Implementation checklist for Sprint 7

### Acceptance Criteria

- [x] Fixture hierarchy designed (3+ directories for Sprint 7) ✅ 4 directories designed
- [x] Expected results format specified (YAML schema) ✅ Complete schema in Appendix B
- [x] Test case generation approach documented (parametrized) ✅ Following convexity pattern
- [x] Fixture documentation template created ✅ README + header templates
- [x] Coverage matrix identifies gaps ✅ 34 fixture files (40 test cases), gaps identified for Sprint 8-10
- [x] Cross-referenced with Tasks 2, 3, 4 (parser features) ✅ All research integrated
- [x] Implementation checklist for Sprint 7 created ✅ 7-phase checklist with detailed tasks

---

## Task 10: Plan Sprint 7 Detailed Schedule

**Status:** 🔵 NOT STARTED  
**Priority:** Critical  
**Estimated Time:** 6-8 hours  
**Deadline:** Before Sprint 7 Day 1  
**Owner:** Sprint planning team  
**Dependencies:** All tasks (1-9)  
**Unknowns Verified:** Integrates all verified unknowns from Tasks 1-9 into detailed sprint plan

### Objective

Create detailed day-by-day Sprint 7 plan (`docs/planning/EPIC_2/SPRINT_7/PLAN.md`) with tasks, checkpoints, deliverables, and acceptance criteria.

### Why This Matters

Sprint 6 demonstrated that detailed daily plans with checkpoints prevent scope creep and ensure steady progress. Sprint 7 has more complexity (parser internals) requiring even more careful planning.

**Goals for Sprint 7 plan:**
- 11-day structure (Days 0-10) like Sprint 6
- 5 checkpoints to validate progress
- Clear acceptance criteria for each day
- Realistic effort estimates based on prep research

### Background

From Sprint 6 retrospective:
- "Day-by-day plan kept sprint on track"
- "Clear checkpoints validated progress"
- "Prep week tasks eliminated ambiguity"

Sprint 7 has 4 major goals:
1. Parser enhancements (30% GAMSLib parse rate)
2. Test performance (<60s fast suite)
3. Convexity refinements (line numbers, fine-grained suppression)
4. CI integration (automated dashboard)

Must sequence tasks correctly:
- Parser features before GAMSLib retest
- Test profiling before parallelization
- Research before implementation

### What Needs to Be Done

**Step 1: Review all prep task results**

Consolidate findings from Tasks 1-9:
- Known unknowns (Task 1)
- GAMSLib failure analysis (Task 2)
- Preprocessor directive design (Task 3)
- Multi-dimensional indexing design (Task 4)
- Test performance baseline (Task 5)
- Parser roadmap (Task 6)
- Line number tracking design (Task 7)
- CI design (Task 8)
- Test fixture strategy (Task 9)

**Step 2: Create day-by-day breakdown**

Proposed Sprint 7 schedule (11 days):

**Week 1: Parser Enhancements**
- Day 0: Pre-sprint setup, final prep review
- Day 1: Preprocessor directive implementation (mock approach)
- Day 2: Multi-dimensional set indexing (IR + grammar)
- Day 3: Multi-dimensional set indexing (normalization + AD)
- Day 4: Advanced GAMS features (table declarations, set ranges)
- Day 5: GAMSLib retest and parser validation
- **Checkpoint 1 (Day 5 EOD):** GAMSLib parse rate ≥30%

**Week 2: Optimization & Quality**
- Day 6: Test profiling and marking (slow tests)
- Day 7: Test parallelization (pytest-xdist)
- Day 8: Convexity refinements (line numbers, fine-grained suppression)
- Day 9: CI integration (GAMSLib regression tracking)
- **Checkpoint 2 (Day 9 EOD):** All quality metrics met
- Day 10: Sprint review, retrospective, release prep

**Step 3: Define checkpoints**

5 checkpoints:
1. **Checkpoint 0 (Day 0):** Prep tasks complete, Known Unknowns reviewed
2. **Checkpoint 1 (Day 5):** Parser enhancements complete, GAMSLib ≥30%
3. **Checkpoint 2 (Day 7):** Test suite <60s (fast), <120s (full)
4. **Checkpoint 3 (Day 9):** All features integrated, CI working
5. **Checkpoint 4 (Day 10):** Sprint 7 complete, v0.7.0 released

**Step 4: Define acceptance criteria**

For each day:
- Specific deliverables (files created/modified)
- Test coverage (new tests added)
- Quality checks (all passing)
- Integration validation (features work together)

Example (Day 1):
- [ ] Grammar updated to recognize preprocessor directives
- [ ] Transformer skips or mocks directives
- [ ] 10+ tests for common directive patterns
- [ ] All existing tests still pass (zero regressions)
- [ ] At least 1 additional GAMSLib model parses

**Step 5: Estimate effort and risk**

For each day:
- Estimated hours (6-8h per day)
- Risk level (Low/Medium/High)
- Mitigation strategy if high risk

**Step 6: Cross-reference with PROJECT_PLAN.md**

Ensure Sprint 7 plan aligns with:
- PROJECT_PLAN.md Sprint 7 components
- PRELIMINARY_PLAN.md goals
- Known Unknowns verification tasks

**Step 7: Create PLAN.md document**

Following Sprint 6 PLAN.md format:
- Executive summary
- Sprint goals
- Day-by-day breakdown (Days 0-10)
- Checkpoints with acceptance criteria
- Deliverables list
- Success criteria
- Risk register

**Changes:**

*To be completed*

**Result:**

*To be completed*

### Verification

```bash
# Sprint 7 PLAN.md should exist
test -f docs/planning/EPIC_2/SPRINT_7/PLAN.md

# Should contain required sections
grep -q "Day 0:" docs/planning/EPIC_2/SPRINT_7/PLAN.md
grep -q "Day 10:" docs/planning/EPIC_2/SPRINT_7/PLAN.md
grep -q "Checkpoint" docs/planning/EPIC_2/SPRINT_7/PLAN.md

# Should have 11 days (Days 0-10)
[ "$(grep -c "^### Day [0-9]" docs/planning/EPIC_2/SPRINT_7/PLAN.md)" -eq 11 ]

# Cross-references should exist
grep -q "PROJECT_PLAN.md" docs/planning/EPIC_2/SPRINT_7/PLAN.md
grep -q "KNOWN_UNKNOWNS.md" docs/planning/EPIC_2/SPRINT_7/PLAN.md
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_7/PLAN.md` (detailed sprint plan)
- Day-by-day breakdown (Days 0-10)
- 5 checkpoints with acceptance criteria
- Deliverables list for each day
- Risk register with mitigation strategies
- Effort estimates (hours per day)
- Cross-references to all prep task outputs

### Acceptance Criteria

- [ ] PLAN.md created following Sprint 6 format
- [ ] 11 days (Days 0-10) with detailed tasks
- [ ] 5 checkpoints defined with acceptance criteria
- [ ] All 4 Sprint 7 goals addressed (parser, tests, convexity, CI)
- [ ] Effort estimates realistic (6-8h per day)
- [ ] Risk register complete with mitigations
- [ ] Cross-referenced with PROJECT_PLAN.md, PRELIMINARY_PLAN.md, Known Unknowns
- [ ] All prep tasks (1-9) integrated into plan

---

## Summary

### Success Criteria

Sprint 7 prep is successful if:

1. ✅ **Known Unknowns documented** (22-30 unknowns across 5 categories)
2. ✅ **GAMSLib failures analyzed** (9 models categorized, feature priority established)
3. ✅ **Preprocessor directive approach designed** (mock vs full decision made)
4. ✅ **Multi-dimensional indexing designed** (IR, normalization, AD impacts understood)
5. ✅ **Test suite profiled** (slowest tests identified, speedup estimates calculated)
6. ✅ **Parser roadmap created** (features for Sprints 8-10 prioritized)
7. ✅ **Line number tracking designed** (convexity warning UX improvement ready)
8. ✅ **CI regression tracking designed** (automated dashboard updates planned)
9. ✅ **Test fixture strategy created** (comprehensive coverage planned)
10. ✅ **Sprint 7 PLAN.md created** (detailed day-by-day schedule ready)

**Total Prep Time:** ~48-65 hours (~6-8 working days)

**Critical Path Dependencies:**
- Tasks 1 → 2 → 3, 4 → 9 → 10
- Must complete Tasks 1, 2, 3, 4, 10 before Sprint 7 Day 1 (Critical priority)
- Tasks 5, 6, 7, 8, 9 can overlap with early Sprint 7 days if needed

**Ready to Begin Sprint 7 When:**
- All Critical priority tasks complete (1, 2, 3, 10)
- All High priority tasks complete (4, 5, 6, 9)
- Medium priority tasks at least designed (7, 8)
- Sprint 7 PLAN.md reviewed and approved

---

## Appendix: Document Cross-References

### Sprint 7 Scope
- **PROJECT_PLAN.md:** Lines 45-92 (Sprint 7 components, deliverables, acceptance criteria)
- **PRELIMINARY_PLAN.md:** Full document (goals, task breakdown, risk analysis)

### Sprint 6 Learnings
- **RETROSPECTIVE.md:** "What Could Be Improved" section (parser limitations, test performance)
- **KNOWN_UNKNOWNS.md:** Deferred unknowns (1.6, 1.7, 4.3)

### Epic 2 Goals
- **GOALS.md:** Production maturity, real-world validation, GAMSLib benchmarking

### Research Documents
- `docs/research/preprocessor_directives.md` (to be created in Task 3)
- `docs/research/multidimensional_indexing.md` (to be created in Task 4)

### Testing Documents
- **SPRINT_6_QA_REPORT.md:** Test suite baseline (1217 tests, 99.8% pass rate)
- `docs/testing/PARSER_FIXTURE_STRATEGY.md` (to be created in Task 9)

### CI/CD
- `docs/ci/gamslib_regression_tracking.md` (to be created in Task 8)

### GAMSLib Baseline
- **GAMSLIB_CONVERSION_STATUS.md:** Sprint 6 baseline (10% parse rate, 9 failures)
- `reports/gamslib_ingestion_sprint6.json`: Raw ingestion data

---

**Prep Plan Status:** 🔵 READY TO BEGIN  
**Created:** 2025-11-14  
**Owner:** Sprint 7 Planning Team  
**Review By:** Before Sprint 7 Day 1
