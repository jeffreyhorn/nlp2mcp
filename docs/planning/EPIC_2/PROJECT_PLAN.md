# EPIC 2 Project Plan (v1.0 Track)

This plan translates `GOALS_REVISED.md` into sprint-ready guidance for Sprints 6–10 (two weeks each).

---

# Sprint 6 (Weeks 1–2): Convexity Heuristics, Critical Bug Fixes, GAMSLib Bootstrapping, UX Kickoff

**Goal:** Ship actionable convexity heuristics, close high-severity reformulation bugs, stand up GAMSLib ingestion + dashboards, and begin iterative UX improvements.

## Components
- **Convexity Heuristic Pass**
  - Implement pattern-based nonconvex detectors (nonlinear equalities, trig, bilinear, quotients, odd powers).
  - CLI flags: `--strict-convexity` (fail on warning) and default warning mode.
  - Documentation section covering when to trust MCP vs stick with NLP.
- **Critical Bug Fixes**
  - ~~Adjust KKT stationarity for maximize-sense bound multipliers.~~ **REMOVED** - No bug exists (verified 2025-11-12)
  - Implement nested min/max flattening (Option A) plus regression tests & PATH validation.
- **GAMSLib Bootstrapping**
  - Script to download/refresh target NLP models, run nightly ingestion.
  - Initial `CONVERSION_STATUS.md` with parse results and error buckets.
  - Baseline KPI: ≥10 models ingested; ≥10 % parse success.
- **UX Improvements (Iteration 1)**
  - Enhance parser/convexity error copy with line/column context and doc links.
  - Add sprint demo checklist for UX increments.

## Deliverables
- Convexity heuristic module + CLI flags + docs.
- ~~Fixed maximize multiplier~~ + nested min/max flattening with tests.
- `scripts/download_gamslib_nlp.sh`, ingestion cron, and conversion dashboard.

**Note:** Maximize multiplier bug fix removed from scope - verified no bug exists (see `SPRINT_6/TASK3_CORRECTED_ANALYSIS.md`).
- Updated error messaging + documentation describing new warnings.
- Release tag `v0.6.0`.

## Acceptance Criteria
- Heuristic warnings trigger on curated nonconvex samples and stay silent on convex baselines.
- Maximize/minimize regression suite fully green; nested min/max research cases convert and solve in PATH.
- GAMSLib ingestion runs nightly; dashboard lists ≥10 models with parse status.
- UX checklist for sprint shows completed error-messaging improvements.

---

# Sprint 7 (Weeks 3–4): Parser Enhancements Wave 1, Optional Convexity AST Pass, UX Iteration, KPI Tracking ✅ COMPLETE

**Goal:** Raise parser coverage to ≥20 %, experiment with AST-based convexity analysis if time allows, integrate KPIs/dashboards, and continue UX upgrades.

**Status:** ✅ **COMPLETE** - Completed 2025-11-16, v0.7.0 released  
**Actual Results:**
- ✅ Parse Rate: 20% achieved (2/10 GAMSLib models)
- ✅ Test Performance: 7.1x speedup (208s → 29.23s fast suite)
- ✅ Convexity UX: 100% warnings show line numbers
- ✅ CI Automation: Regression detection active
- ✅ Quality: 1287 tests passing, all checks passing

## Components
- **Parser Enhancements (Wave 1)**
  - Prioritize syntax gaps revealed by Sprint 6 telemetry (e.g., `.l/.m`, assignment statements, simple dollar conditions).
  - Update normalization + IR to support new constructs.
- **Convexity AST Analysis (Optional)**
  - Compose expression-class tracking for `--analyze-convexity` flag (CONSTANT/AFFINE/CONVEX/CONCAVE/UNKNOWN).
  - Emit detailed reports citing problematic equations.
- **Telemetry & KPIs**
  - Automate dashboard updates; KPI: ≥20 % of tracked GAMSLib models parse, ≥15 % convert.
  - Introduce PATH smoke target for simple models (if licensing available).
- **UX Improvements (Iteration 2)**
  - Add lightweight progress indicators (stage-level timers) and refine error guidance for newly supported syntax.

## Deliverables
- Parser support for top-priority GAMSLib features + regression tests.
- (If implemented) AST-based convexity analysis doc + CLI flag.
- Updated conversion dashboard with parse/convert metrics + PATH smoke stats.
- Progress indicator implementation + improved error copy.
- Release tag `v0.7.0`.

## Acceptance Criteria
- Telemetry shows ≥20 % parse success across selected GAMSLib set; dashboard auto-updates per run.
- Newly supported syntax passes unit/integration tests; previously working models unaffected.
- If AST analysis shipped, sample report matches designed expectations.
- Progress indicators reflected in CLI output; UX checklist ticked for sprint.

---

# Sprint 8 (Weeks 5–6): Parser Maturity & Developer Experience (Hybrid Strategy) ✅ COMPLETE

**Goal:** Incremental parse rate improvement (20% → 25%) with enhanced developer UX through parser error line numbers and improved diagnostics. Conservative, achievable targets based on Sprint 7 retrospective.

**Status:** ✅ **COMPLETE** - Completed 2025-11-18, v0.8.0 ready for release  
**Actual Results:**
- ✅ Parse Rate: 40% achieved (4/10 GAMSLib models) - **EXCEEDED target by 60%** (40% vs 25% target)
- ✅ Parser Features: Option statements + Indexed assignments fully implemented
- ✅ Error UX: 100% of parse errors show line numbers, 5 enhancement rules active
- ✅ Partial Metrics: Dashboard shows parse progress percentages with 4-level color coding
- ✅ Test Suite: 1349 tests passing (5x faster: 120s → 24s)
- ✅ Documentation: Comprehensive retrospective with Sprint 9 recommendations

**Strategy:** 60% Parser Maturity + 40% Infrastructure/UX (Sprint 7 Retrospective recommendation)

## Components

### Parser Enhancements (60% effort, ~15-20 hours)
- **Option Statements (High Priority)**
  - Implement `option` statement parsing (`option limrow = 0;`, `option limcol = 0;`)
  - Unlocks: mhw4dx.gms and other models using basic options
  - Effort: 6-8 hours
  - Risk: Low (grammar extension, semantic handling straightforward)
  
- **Per-Model Feature Analysis**
  - Create feature dependency matrix for all 10 GAMSLib models
  - Identify models closest to parsing (1-2 features away)
  - Prioritize features that unlock multiple models
  - Effort: 3-4 hours
  - Deliverable: `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md`

- **One Additional High-ROI Feature** (choose based on analysis)
  - Either: Simple indexed assignments (if unlocks 2+ models)
  - Or: Function call syntax improvements (if unlocks 2+ models)
  - Effort: 6-8 hours
  - Risk: Medium (grammar changes required)

### Infrastructure & UX Improvements (40% effort, ~10-15 hours)
- **Parser Error Line Numbers (High Priority)**
  - Extend SourceLocation tracking to parser errors (builds on Sprint 7 work)
  - Show precise file/line/column for all parse errors
  - Effort: 4-6 hours
  - Risk: Very Low (infrastructure exists from convexity line numbers)
  
- **Partial Parse Metrics**
  - Track percentage of statements parsed per model (not just binary pass/fail)
  - Update dashboard to show "80% parsed" for partially-supported models
  - Effort: 3-4 hours
  - Deliverable: Enhanced `docs/status/GAMSLIB_CONVERSION_STATUS.md`
  
- **Improved Error Messages**
  - Enhance parser error messages with actionable suggestions
  - Add "did you mean?" hints for common mistakes
  - Effort: 3-5 hours

## Deliverables
- Option statement support with regression tests
- One additional parser feature (indexed assignments OR function calls)
- Parser error line numbers for all parse errors
- Per-model feature dependency matrix
- Partial parse metrics in dashboard
- Improved error messages with suggestions
- Release tag `v0.8.0`

## Acceptance Criteria - All Met ✅
- ✅ **Parse Rate:** ≥25% (2.5/10 models) - **ACHIEVED 40%** (exceeded by 60%)
- ✅ **Parser Errors:** 100% of parse errors show file/line/column (matches convexity UX)
- ✅ **Feature Matrix:** All 10 models analyzed with feature dependencies documented
- ✅ **Partial Metrics:** Dashboard shows statement-level parse success (e.g., "himmel16: 42% parsed")
- ✅ **Quality:** All existing tests pass (1349 passed), new features have comprehensive test coverage
- ✅ **UX Validation:** Error messages tested with real-world models, 5 enhancement rules active

**Estimated Effort:** 25-35 hours (Sprint 7 Retrospective recommendation)  
**Actual Effort:** ~35 hours (within estimate)  
**Risk Level:** LOW (focuses on proven patterns from Sprint 7)

---

# Sprint 9 (Weeks 7–8): Advanced Parser Features & Conversion Pipeline

**Goal:** Implement advanced parser features requiring grammar changes and begin conversion pipeline work. Builds on Sprint 8's foundation with higher-complexity features.

**Strategy:** Advanced features + conversion infrastructure (deferred from original Sprint 8) + Test infrastructure improvements (Sprint 8 retrospective recommendations)

**Sprint 8 Retrospective Integration:** Incorporates 5 high/medium priority recommendations to strengthen test infrastructure and prevent issues identified in Sprint 8.

## Components

### High Priority: Test Infrastructure Improvements (~5-6 hours)
**NEW - Sprint 8 Retrospective Recommendations:**

- **Secondary Blocker Analysis for mhw4dx.gms (2-3 hours)**
  - Manual inspection of mhw4dx.gms lines 37-63 to identify ALL blockers
  - Parse with current parser, capture ALL errors (not just first)
  - Document: "Primary blocker: option statements ✅. Secondary blocker: [TBD]"
  - Update GAMSLIB_FEATURE_MATRIX.md with complete findings
  - **Impact:** Prevents underestimation of unlock requirements (Sprint 8 lesson)
  - **Rationale:** Sprint 8 assumed option statements alone would unlock mhw4dx.gms, but secondary blockers exist

- **Automated Fixture Tests (2-3 hours)**
  - Create `tests/test_fixtures.py`: Iterate over all 13 fixture directories
  - For each fixture: Parse GMS file, compare actual vs expected_results.yaml
  - Validate: parse status, statement counts, line numbers, option statements, indexed assignments
  - **Impact:** Regression protection for all documented test patterns
  - **Addresses:** Sprint 8 gap - "13 fixtures created, 0 automated tests"

- **Fixture Validation Script (1 hour)**
  - Create `scripts/validate_fixtures.py` for pre-commit validation
  - Input: GMS file + expected_results.yaml
  - Output: Report discrepancies (line numbers, statement counts, feature counts)
  - **Impact:** Prevents PR review issues like PR #254 (5 review comments on incorrect counts)
  - **Use:** Run before creating fixture PRs to ensure accuracy

### Advanced Parser Features (~15-20 hours)
- **Advanced Indexing (i++1, i--1)**
  - Implement lead/lag indexing operators
  - Unlocks: himmel16.gms and models with sequential indexing
  - Effort: 8-10 hours
  - Risk: Medium-High (requires grammar changes, semantic complexity)
  
- **Model Sections (mx syntax)**
  - Support multi-line model declarations with `/` syntax
  - Unlocks: hs62.gms, mingamma.gms
  - Effort: 5-6 hours
  - Risk: Medium (grammar extension)
  
- **Equation Attributes (.l/.m)**
  - Parse and store equation attributes where semantically relevant
  - Foundation for conversion pipeline
  - Effort: 4-6 hours

### Conversion & Performance Instrumentation (~10-15 hours)
- **Dashboard Expansion**
  - Track parse/convert/solve rates (extend existing dashboard)
  - KPI: Monitor conversion rate on successfully parsed models
  - Effort: 3-4 hours
  
- **Conversion Pipeline Foundation**
  - Begin conversion infrastructure for successfully parsed models
  - Focus on simple models (mhw4d, rbrock) as initial targets
  - Effort: 6-8 hours
  - Risk: Medium (new pipeline stage)
  
- **Performance Baseline & Budget**
  - Establish benchmark harness for parse/convert times
  - Document baseline performance for regression tracking
  - **NEW:** Establish test suite performance budgets (Sprint 8 recommendation):
    - Fast tests (`make test`): <30s (currently 24s ✅)
    - Full suite (`make test-all`): <5min baseline
  - Add test timing to CI/CD reports
  - **Sprint 8 Lesson:** Set up performance budget on Day 0 for all-day benefits
  - Effort: 3-4 hours + 1 hour (performance budget) = 4-5 hours

## Deliverables

**Test Infrastructure (NEW):**
- Secondary blocker analysis for mhw4dx.gms (GAMSLIB_FEATURE_MATRIX.md update)
- Automated fixture test suite (`tests/test_fixtures.py`)
- Fixture validation script (`scripts/validate_fixtures.py`)
- Test suite performance budget documentation

**Parser Features (Original):**
- Advanced indexing support (i++1, i--1)
- Model sections support (mx syntax)
- Equation attributes parsing (.l/.m)

**Conversion & Performance (Original + Enhanced):**
- Expanded dashboard with conversion tracking
- Conversion pipeline foundation
- Performance baseline documentation + performance budgets

**Release:**
- Release tag `v0.9.0` (bumped from v0.8.1 due to test infrastructure additions)

## Acceptance Criteria

**Parse Rate & Features (Original):**
- **Parse Rate:** ≥30% (3/10 models) - Original Sprint 8 target, achievable with advanced features
- **Advanced Features:** i++1 indexing and model sections working with comprehensive tests
- **Conversion Pipeline:** At least 1 model (mhw4d or rbrock) successfully converts end-to-end
- **Dashboard:** Tracks parse/convert/solve rates automatically
- **Quality:** All existing tests pass, advanced features have edge case coverage

**Test Infrastructure (NEW - Sprint 8 Retrospective):**
- **Secondary Blocker Analysis:** mhw4dx.gms blockers fully documented in GAMSLIB_FEATURE_MATRIX.md ✅
- **Automated Fixtures:** All 13 fixtures have automated tests in `tests/test_fixtures.py` ✅
- **Fixture Validation:** `scripts/validate_fixtures.py` prevents manual counting errors ✅
- **Performance Budget:** Test suite budgets established and documented (<30s fast, <5min full) ✅

## Sprint 8 Retrospective Lessons Applied

1. **✅ Address Test Infrastructure Gaps Early:** Fix fixture testing gap before it becomes technical debt
2. **✅ Performance Budget on Day 0:** Establish budgets early (Sprint 8 lesson: benefits all days)
3. **✅ Complete Secondary Blocker Analysis:** Prevent underestimation (mhw4dx.gms lesson learned)
4. **✅ Fixture Validation Automation:** Prevent PR review cycles on manual counting errors
5. **✅ Regression Protection:** Automated fixture tests protect documented behavior

**Estimated Effort:** 30-41 hours (25-35h original + 5-6h test infrastructure)  
**Risk Level:** MEDIUM (complex grammar changes, new pipeline stage, offset by test infrastructure improvements)

---

# Sprint 10 (Weeks 9–10): Complete GAMSLIB Tier 1 Parse Coverage & Comma-Separated Declarations

**Goal:** Achieve 100% parse rate on Tier 1 GAMSLIB models (10/10) through comprehensive dependency analysis and targeted feature implementation. Add support for comma-separated VARIABLE, PARAMETER, and EQUATION declarations.

**Strategy:** Deep dependency analysis first, then implement only the features required to unlock all remaining blocked models. Focus on understanding complete blocker chains before any implementation work.

## Components

### Phase 1: Comprehensive Dependency Analysis (~6-9 hours)
**Critical Foundation - Sprint 9 Retrospective Priority #1:**

- **Full Dependency Chain Analysis (6-9 hours)**
  - Analyze each blocked model line-by-line to identify ALL blockers (primary, secondary, tertiary)
  - For each model: circle.gms, himmel16.gms, maxmin.gms, mingamma.gms
  - Parse with current parser, capture complete error cascade
  - Document blockers in priority order with effort estimates
  - Create synthetic test cases for each identified feature
  - **Deliverable:** `docs/planning/EPIC_2/SPRINT_10/BLOCKER_ANALYSIS.md`
  - **Sprint 9 Lesson:** Features implemented ≠ models unlocked without complete blocker analysis
  - **Validation:** Each model must have full blocker chain documented before implementation starts

### Phase 2: Comma-Separated Declarations (~4-6 hours)
**Quick Win - Common GAMS Pattern:**

- **Comma-Separated Declaration Support**
  - Support multiple declarations in single statement:
    - `Variable x1, x2, x3;` (currently requires separate lines)
    - `Parameter a, b, c;`
    - `Equation eq1, eq2, eq3;`
  - Grammar extension + parser updates
  - Comprehensive test coverage for all declaration types
  - **Effort:** 4-6 hours
  - **Risk:** Low (straightforward grammar extension)
  - **Impact:** Common GAMS pattern, improves compatibility

### Phase 3: Targeted Feature Implementation (~20-26 hours)
**Based on Phase 1 Analysis - Implement Only Required Features:**

- **Function Calls in Parameter Assignments (6-8 hours)**
  - Support `uniform(1,10)`, `smin(i, x(i))`, etc.
  - Unlocks: circle.gms (primary blocker)
  - Risk: Medium (AST changes for parameter initialization)

- **Level Bound Conflict Resolution (2-3 hours)**
  - Handle multiple `.l` assignments to same variable
  - Unlocks: himmel16.gms (secondary blocker - i++1 already implemented)
  - Risk: Low (semantic validation improvement)

- **Nested/Subset Indexing in Domains (10-12 hours)**
  - Support `defdist(low(n,nn))..` where low is 2D subset
  - Unlocks: maxmin.gms (primary blocker)
  - Risk: High (complex indexing semantics)

- **abort$ in If-Block Bodies (2-3 hours)**
  - Allow `abort$(condition)` statements inside if-blocks
  - Unlocks: mingamma.gms (primary blocker - equation attributes already implemented)
  - Risk: Low (grammar extension)

### Phase 4: Mid-Sprint Validation Checkpoint (Day 5)
**NEW - Sprint 9 Retrospective Recommendation:**

- **Impact Validation at Sprint Midpoint**
  - Re-run parser on all 10 models
  - Verify parse rate increase matches projections
  - If parse rate hasn't improved, investigate and pivot
  - **Sprint 9 Lesson:** Features complete by Day 5, but 0% impact discovered only on Day 10
  - **Time Budget:** 1-2 hours
  - **Decision Point:** Continue with remaining features OR investigate why unlocks aren't happening

### Phase 5: Synthetic Test Suite (~3-4 hours)
**Quality Assurance - Sprint 9 Retrospective Recommendation:**

- **Isolated Feature Tests**
  - Create minimal GAMS files testing each feature in isolation
  - Validate: i++1 indexing works correctly (can't tell with himmel16.gms failures)
  - Validate: Equation attributes work correctly (mingamma.gms had different blocker)
  - Validate: Model sections work correctly (hs62.gms now parses)
  - Validate: New features (function calls, nested indexing, abort$, comma-separated)
  - **Impact:** Distinguish feature bugs from secondary blockers
  - **Sprint 9 Lesson:** Can't validate i++1 implementation without synthetic test

## Deliverables

**Analysis & Planning:**
- Complete blocker analysis document (`BLOCKER_ANALYSIS.md`) with full dependency chains
- Synthetic test suite for all Sprint 9 and Sprint 10 features

**Parser Features:**
- Comma-separated VARIABLE, PARAMETER, EQUATION declarations
- Function calls in parameter assignments
- Level bound conflict resolution
- Nested/subset indexing in equation domains
- abort$ statements in if-block bodies

**Validation & Metrics:**
- Mid-sprint checkpoint report (Day 5)
- Updated GAMSLIB_CONVERSION_STATUS.md showing 100% parse rate
- Parse rate dashboard showing 10/10 models

**Release:**
- Release tag `v0.10.0`

## Acceptance Criteria

**Primary Goal:**
- **Parse Rate:** 100% (10/10 Tier 1 GAMSLIB models) - All models parse successfully
- **Quality:** All 10 models have complete blocker analysis documented BEFORE implementation
- **Mid-Sprint Checkpoint:** Parse rate progress validated on Day 5; pivot if needed

**Feature Validation:**
- **Comma-Separated Declarations:** Works for Variable, Parameter, Equation statements
- **Function Calls:** Parameter assignments support function call expressions
- **Level Bounds:** Multiple `.l` assignments handled without conflicts
- **Nested Indexing:** Subset domains like `low(n,nn)` parse correctly
- **abort$ in If-Blocks:** Conditional abort statements allowed in if-block bodies

**Testing & Documentation:**
- **Synthetic Tests:** Each feature has isolated test case proving it works
- **Regression:** All existing tests pass (1400+ tests expected)
- **Documentation:** BLOCKER_ANALYSIS.md explains complete dependency chains for all 4 blocked models

**Sprint 9 Retrospective Lessons Applied:**
1. ✅ Complete dependency analysis BEFORE any implementation
2. ✅ Synthetic test cases for feature validation
3. ✅ Mid-sprint checkpoint at Day 5 to validate impact
4. ✅ Document full blocker chains, not just primary errors

## Risk Mitigation

**High Risk: Nested/Subset Indexing (10-12 hours)**
- Mitigation: Complete analysis in Phase 1 to understand exact requirements
- Fallback: If too complex, defer to Sprint 11 and target 90% parse rate (9/10 models)

**Medium Risk: Feature Interactions**
- Mitigation: Synthetic test suite validates each feature in isolation
- Mitigation: Mid-sprint checkpoint catches interaction issues early

**Low Risk: Time Estimation**
- Total Estimated Effort: 32-46 hours
- Sprint Capacity: ~40 hours (2 weeks)
- Buffer: Phase 1 analysis may reveal simpler/faster solutions

## Success Metrics

- **Before Sprint 10:** 60% parse rate (6/10 models)
  - _Assumes Sprint 9 successfully unlocks 2 additional models (himmel16.gms and hs62.gms); actual parse rate may be lower if these are not achieved._
- **After Sprint 10:** 100% parse rate (10/10 models) - **40 percentage point increase**
- **Models Unlocked:** circle, himmel16, maxmin, mingamma (4 new models)
- **Conversion Rate:** Target ≥50% of parseable models (5/10 minimum)

---

# Sprint 11 (Weeks 11–12): Aggressive Simplification, Regression Guardrails, UX Diagnostics

**Goal:** Deliver `--simplification aggressive` informed by telemetry, integrate CI regression hooks (GAMSLib sampling, PATH smoke, performance alerts), and expand diagnostics features.

## Components
- **Aggressive Simplification & CSE**
  - Implement advanced algebraic identities, rational simplification, optional CSE, and simplification metrics (`--simplification-stats`).
  - Ensure FD validation + PATH results align with baseline; integrate with benchmarks.
- **CI Regression Guardrails**
  - Add automated GAMSLib sampling to CI (parse/convert), PATH smoke tests (where licensing permits), performance thresholds with alerting.
- **UX Improvements (Iteration 4)**
  - Introduce deeper diagnostics mode (`--diagnostic`) showing stage-by-stage stats, pipeline decisions, and simplification summaries.

## Aggressive Simplification Specifications

The aggressive simplification mode (`--simplification aggressive`) extends beyond basic and advanced simplification with additional transformations that may increase expression size in intermediate steps but enable further optimizations through factoring, cancellation, and algebraic restructuring.

### Building on Existing Simplification Levels

**Basic Simplification** (already implemented):
- Constant folding: `2 + 3 → 5`
- Identity operations: `x * 1 → x`, `x + 0 → x`, `x * 0 → 0`
- Negation simplification: `-(-x) → x`
- Power simplification: `x^1 → x`, `x^0 → 1`

**Advanced Simplification** (already implemented):
- Algebraic combination of like terms: `2*x + 3*x → 5*x`
- Cancellation in fractions: `(x * y) / x → y`
- Power law application: `x^a * x^b → x^(a+b)`
- Nested negation: `-(a - b) → b - a`

**Aggressive Simplification** (new transformations):

### 1. Distribution and Factoring

**Distribution Cancellation** (factoring common terms):
- **Pattern:** `x*y + x*z → x*(y + z)`
- **Rationale:** Reduces multiplication operations and exposes common structure
- **Example:**
  ```
  Before: grad_x = 2*exp(x)*sin(y) + 2*exp(x)*cos(y)
  After:  grad_x = 2*exp(x)*(sin(y) + cos(y))
  ```

**Coefficient Factoring** (already done via different mechanism, but documented here):
- **Pattern:** `2*x + 3*x → (2 + 3)*x → 5*x`
- **Note:** Currently achieved through like-term combination in advanced simplification
- **Maintains:** No change needed; existing mechanism is sufficient

**Multi-term Factoring:**
- **Pattern:** `a*c + a*d + b*c + b*d → (a + b)*(c + d)`
- **Rationale:** Exposes multiplicative structure across multiple terms
- **Complexity:** Requires common factor detection across term pairs

### 2. Fraction Simplification

**Distribution Over Division** (expansion):
- **Pattern:** `(a + b) / c → a/c + b/c`
- **Rationale:** May increase size temporarily but can enable cancellation
- **Use case:** When `a/c` or `b/c` can simplify further
- **Example:**
  ```
  Before: (x*y + x*z) / x
  After:  (x*y)/x + (x*z)/x → y + z
  ```
- **Trade-off:** Can make expressions larger; apply only if cancellation detected

**Combining Fractions** (same denominator):
- **Pattern:** `a/c + b/c → (a + b)/c`
- **Rationale:** Reduces division operations and consolidates structure
- **Example:**
  ```
  Before: x/y + z/y
  After:  (x + z)/y
  ```

**Common Denominator Handling:**
- **Pattern:** `a/b + c/d → (a*d + c*b)/(b*d)`
- **Rationale:** Enables further simplification when numerators combine
- **Complexity:** Can significantly increase expression size; use cautiously
- **Heuristic:** Only apply if resulting numerator simplifies by ≥20%

### 3. Nested Operations

**Associativity for Constants:**
- **Pattern:** `(x * c1) * c2 → x * (c1 * c2)`
- **Rationale:** Constant folding opportunity; reduces operation count
- **Example:**
  ```
  Before: (x * 2) * 3
  After:  x * 6
  ```

**Division Chain Simplification:**
- **Pattern:** `(x / c1) / c2 → x / (c1 * c2)`
- **Rationale:** Consolidates multiple divisions into one
- **Example:**
  ```
  Before: (x / 2) / 3
  After:  x / 6
  ```

**Multiplication-Division Reordering:**
- **Pattern:** `(x * y) / z → x * (y / z)` (if `y/z` simplifies)
- **Rationale:** Expose cancellation opportunities through reordering

### 4. Division by Multiplication

**Extracting Constants from Denominator:**
- **Pattern:** `x / (y * c) → (x / c) / y`
- **Alternative:** `x / (y * c) → (x / y) / c`
- **Rationale:** Simplify constant division first, or enable variable cancellation
- **Example:**
  ```
  Before: (6*x) / (y * 2)
  After:  (6*x / 2) / y → (3*x) / y
  ```

**Variable Extraction:**
- **Pattern:** `x / (y * z) → (x / y) / z` (if `x` and `y` have common factors)
- **Use case:** When extracting enables cancellation
- **Example:**
  ```
  Before: (x*a) / (x*b)
  After:  ((x*a) / x) / b → a / b
  ```

### 5. Common Subexpression Elimination (CSE)

**Explicit CSE** (optional, controlled by flag):
- **Pattern:** Replace repeated subexpressions with temporary variables
- **Example:**
  ```
  Before: grad_x = exp(x)*sin(y) + exp(x)*cos(y)
  After:  t1 = exp(x)
          grad_x = t1*sin(y) + t1*cos(y)
  ```
- **Rationale:** Reduces computation when subexpression is expensive (e.g., `exp`, `log`)
- **Trade-off:** Increases variable count; only beneficial if subexpression reused ≥2 times
- **Note:** May be deferred to later sprint or made opt-in via `--cse` flag

### Implementation Strategy

**Transformation Ordering:**
1. **Constant folding and identity operations** (Basic)
2. **Like-term combination** (Advanced)
3. **Associativity for constants** (Aggressive) - enables more constant folding
4. **Fraction combining** (Aggressive) - consolidate before factoring
5. **Distribution cancellation** (Aggressive) - factor common terms
6. **Division simplification** (Aggressive) - extract constants, enable cancellation
7. **Multi-term factoring** (Aggressive) - expose multiplicative structure
8. **CSE** (Optional, if enabled) - final pass for repeated subexpressions

**Heuristics and Safeguards:**
- **Size increase limit:** Reject transformation if expression grows >150% without subsequent simplification
- **Depth limit:** Avoid transformations that increase nesting depth beyond reasonable bounds
- **Cancellation detection:** Prioritize transformations that enable immediate cancellation
- **Metrics tracking:** Report term count, operation count, depth before/after with `--simplification-stats`

**Validation Requirements:**
- **Finite difference validation:** All transformations must pass FD correctness checks
- **PATH solver alignment:** Results must match baseline within numerical tolerance
- **Performance regression:** Simplification overhead must be <10% of total conversion time
- **Benchmark target:** Achieve ≥20% derivative term count reduction on ≥50% of benchmark models

### Example: Full Aggressive Simplification Pipeline

**Input Expression:**
```
grad_f = 2*x*exp(y) + 3*x*exp(y) + (a + b)/c + a/c
```

**Step-by-step Transformation:**
1. **Like-term combination:** `2*x*exp(y) + 3*x*exp(y) → 5*x*exp(y)`
   ```
   grad_f = 5*x*exp(y) + (a + b)/c + a/c
   ```

2. **Distribution over division:** `(a + b)/c → a/c + b/c`
   ```
   grad_f = 5*x*exp(y) + a/c + b/c + a/c
   ```

3. **Like-term combination (fractions):** `a/c + a/c → 2*a/c`
   ```
   grad_f = 5*x*exp(y) + 2*a/c + b/c
   ```

4. **Combining fractions:** `2*a/c + b/c → (2*a + b)/c`
   ```
   grad_f = 5*x*exp(y) + (2*a + b)/c
   ```

**Final Result:**
```
grad_f = 5*x*exp(y) + (2*a + b)/c
```

**Metrics:**
- **Before:** 8 operations (4 multiplications, 2 additions, 2 divisions)
- **After:** 5 operations (2 multiplications, 2 additions, 1 division)
- **Reduction:** 37.5% fewer operations

## Deliverables

### Core Sprint 11 Features
- Simplification engine updates + documentation + examples.
- CI workflows covering GAMSLib sampling, PATH smoke subset, performance guardrails.
- Diagnostics mode implementation and supporting docs.
- Release tag `v0.9.0`.

### High Priority Action Items from Sprint 10 Retrospective

**1. maxmin.gms Implementation (Parser Coverage)**
- Dedicated research phase for nested/subset indexing semantics
- Prototype approach before full implementation
- Budget: 8-12 hours for complexity 9/10 feature
- Target: maxmin.gms 18% → 100% (final GAMSLIB Tier 1 model)
- Goal: Achieve 100% parse rate on all 10 GAMSLIB Tier 1 models

**2. Effort Estimation Refinement (Process Improvement)**
- Calibrate estimation based on Sprint 10 actuals (~18-20h vs. 20-31h budgeted)
- Use Sprint 10 velocity as baseline (3 features in 6 days)
- Track actual time spent in Sprint 11 for better future data
- Update estimation templates with refined coefficients

**3. Incremental Documentation Process (Process Improvement)**
- Update SPRINT_LOG.md after each PR merge (not end of sprint)
- Document decisions and lessons learned immediately
- Add "update docs" to PR checklist template
- Create incremental documentation workflow guide

### Medium Priority Action Items from Sprint 10 Retrospective

**4. GAMSLIB Tier 2 Models Exploration (Future Planning)**
- Research next set of models beyond Tier 1
- Identify new blockers and complexity levels
- Prioritize models for Sprint 11-12
- Create Tier 2 feature dependency matrix

**5. Feature Interaction Testing (Quality Improvement)**
- Test feature combinations incrementally (after each PR, not end of sprint)
- Create synthetic tests that combine multiple features
- Add "integration test" step to PR checklist
- Validate no regressions when features interact

**6. Nested Function Call Support (Parser Coverage)**
- Remaining blocker for circle.gms (3 lines) to reach 100%
- Low priority but achieves complete circle.gms coverage
- Estimate: 2-3 hours (low complexity)
- Example: `exp(log(x))`, `sqrt(power(a, 2))`

## Acceptance Criteria
- Simplification reduces derivative term count ≥20 % on at least half of benchmark models while keeping correctness checks green.
- CI guardrails run on every PR/nightly and block regressions per thresholds.
- Diagnostics mode validated on representative models; UX checklist updated.

### High Priority Action Items
- maxmin.gms achieves 100% parse rate (nested/subset indexing implemented and tested)
- 100% parse rate achieved on all 10 GAMSLIB Tier 1 models
- Sprint 11 effort estimation refined and documented using Sprint 10 actuals
- Incremental documentation process established, documented, and followed throughout sprint

### Medium Priority Action Items (Stretch Goals)
- GAMSLIB Tier 2 models researched with blocker analysis and prioritization complete
- Feature interaction tests added to synthetic test suite with ≥3 combination tests
- Nested function calls implemented (circle.gms → 100%)

---

# Sprint 12 (Weeks 13–14): Final UX Polish, Documentation Wrap, Release Readiness, v1.0.0

**Goal:** Complete diagnostics/progress UI, finalize documentation (advanced usage, GAMSLib handbook, tutorials), close outstanding bugs, and ship v1.0.0 meeting all KPIs.

## Components
- **UX & Diagnostics Finalization**
  - Polish progress indicators, diagnostics, and stats dashboards.
  - Ensure CLI outputs are consistent, localized, and documented.
- **Documentation Enhancements**
  - Expand `docs/ADVANCED_USAGE.md`, `docs/GAMSLIB_EXAMPLES.md`, API reference, and produce video scripts/walkthroughs.
  - Update release notes, changelog, and adoption guides.
- **Release Readiness & QA**
  - Ensure KPIs met (≥80 % parse, ≥60 % convert, ≥40 % solve; ≥90 % code coverage).
  - Run full regression suite, performance benchmarks, and PATH validations.
  - Finalize CI dashboards and release checklist execution.

## Deliverables
- Polished UX features (diagnostics/progress/stats) with final documentation.
- Complete documentation set (advanced usage, GAMSLib examples, API reference, video guides).
- Release notes, CHANGELOG entries, and v1.0.0 tag/sign-off artifacts.

## Acceptance Criteria
- KPIs satisfied and recorded; release checklist completed with approvals.
- Documentation covers all new capabilities and references dashboards/metrics.
- No P0/P1 bugs open; regression and performance suites green.
- PATH/GAMSLib dashboards confirm targets; v1.0.0 artifacts published.

---

## Rolling KPIs & Dashboards
- Sprint-level KPIs (parse/convert/solve, UX increments, coverage) reviewed at each retro.
- Dashboards (conversion status, performance, CI guardrails) must update automatically at least nightly.

---
