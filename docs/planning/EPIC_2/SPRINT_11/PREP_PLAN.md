# Sprint 11 Preparation Plan

**Purpose:** Prepare for aggressive simplification, CI regression guardrails, UX diagnostics, and maxmin.gms implementation  
**Timeline:** Complete before Sprint 11 Day 1  
**Goal:** Research and prototype key Sprint 11 features, establish process improvements, achieve 100% GAMSLIB Tier 1 parse rate

**Key Insight from Sprint 10:** Sprint 10 achieved 90% parse rate (9/10 models) 4 days ahead of schedule through comprehensive prep work, conservative planning, and front-loaded low-risk features. Sprint 11 will target the final Tier 1 model (maxmin.gms) while implementing aggressive simplification and CI guardrails.

---

## Executive Summary

Sprint 11 represents a significant technical expansion across three major workstreams:

1. **Aggressive Simplification (Core Feature):** Implement advanced algebraic transformations (factoring, fraction simplification, nested operations, division by multiplication, optional CSE) that extend beyond basic/advanced simplification to achieve ≥20% derivative term reduction.

2. **maxmin.gms Implementation (Parser Coverage):** Research and implement nested/subset indexing to unlock the final GAMSLIB Tier 1 model, achieving 100% parse rate on all 10 Tier 1 models.

3. **CI Regression Guardrails & UX (Infrastructure):** Add automated GAMSLib sampling, PATH smoke tests, performance thresholds, and deeper diagnostics mode to prevent regressions and improve developer experience.

4. **Process Improvements (Sprint 10 Retrospective):** Implement incremental documentation, refined effort estimation, and feature interaction testing processes.

This prep plan focuses on research, prototyping, and infrastructure setup to de-risk Sprint 11 execution.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|----------------------|
| 1 | Create Sprint 11 Known Unknowns List | Critical | 3 hours | None | Risk mitigation, all goals |
| 2 | Research maxmin.gms Nested/Subset Indexing | Critical | 6 hours | Task 1 | Parser coverage (100% Tier 1) |
| 3 | Design Aggressive Simplification Architecture | Critical | 5 hours | Task 1 | Core simplification feature |
| 4 | Research Common Subexpression Elimination (CSE) | High | 4 hours | Task 3 | Simplification enhancement |
| 5 | Prototype Factoring Algorithms | High | 5 hours | Task 3 | Simplification core |
| 6 | Survey CI Regression Frameworks | High | 3 hours | Task 1 | CI guardrails infrastructure |
| 7 | Design GAMSLib Sampling Strategy | High | 3 hours | Task 6 | CI automated testing |
| 8 | Research PATH Smoke Test Integration | Medium | 3 hours | Task 6 | CI solver validation |
| 9 | Design Diagnostics Mode Architecture | Medium | 4 hours | Task 1 | UX improvements |
| 10 | Establish Incremental Documentation Process | High | 2 hours | Task 1 | Process improvement |
| 11 | Create Feature Interaction Test Framework | Medium | 3 hours | Task 1 | Quality improvement |
| 12 | Plan Sprint 11 Detailed Schedule | Critical | 5 hours | Tasks 1-11 | Sprint execution plan |

**Total Estimated Time:** ~46 hours (~6 working days)

**Critical Path:** Tasks 1 → 2 → 3 → 5 → 12 (maxmin research + simplification design + detailed planning)

**Parallel Tracks:**
- Track A: Simplification (Tasks 3, 4, 5)
- Track B: CI/Infrastructure (Tasks 6, 7, 8)
- Track C: UX/Process (Tasks 9, 10, 11)
- Track D: Parser (Task 2)

---

## Task 1: Create Sprint 11 Known Unknowns List

**Status:** ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 3 hours  
**Deadline:** Before Sprint 11 Day 1  
**Owner:** Sprint planning  
**Dependencies:** None

### Objective

Create comprehensive list of assumptions and unknowns for Sprint 11's three major workstreams (aggressive simplification, maxmin.gms, CI/UX) to prevent late discoveries and enable proactive research.

### Why This Matters

Sprint 10 Retrospective identified prep work as a key success factor. Sprint 11 has significantly higher technical complexity:
- Aggressive simplification involves complex algebraic transformations with correctness risks
- maxmin.gms has complexity 9/10 (highest of any Tier 1 model)
- CI integration requires infrastructure knowledge

Documenting unknowns upfront enables targeted research and prototyping.

### Background

Sprint 10 achieved 90% parse rate through comprehensive prep analysis (11 tasks). Sprint 11 targets:
- Aggressive simplification with ≥20% derivative term reduction
- 100% Tier 1 parse rate (maxmin.gms 18% → 100%)
- CI guardrails preventing regressions
- Diagnostics mode for pipeline visibility

### What Needs to Be Done

**1. Document Aggressive Simplification Unknowns**
   - How to detect common factors across terms?
   - When does distribution over division improve vs. worsen expressions?
   - How to detect cancellation opportunities before applying transformations?
   - What heuristics prevent expression size explosion (>150% growth)?
   - How to handle associativity with mixed operations?
   - What's the optimal transformation ordering?
   - How to validate transformations (FD checks sufficient)?

**2. Document maxmin.gms / Nested Indexing Unknowns**
   - What is nested/subset indexing syntax in GAMS?
   - How are nested indices represented in AST?
   - How do nested domains affect equation generation?
   - What are edge cases (empty subsets, dynamic subsets)?
   - How to handle subset conditions in MCP generation?
   - Performance impact of nested indexing on large models?

**3. Document CI/Regression Guardrails Unknowns**
   - Which CI framework to use (GitHub Actions already used)?
   - How to sample GAMSLib models (random, stratified, fixed subset)?
   - What performance thresholds trigger alerts (time, memory)?
   - How to integrate PATH solver (licensing, timeout handling)?
   - How to store/compare regression baselines?
   - Alert mechanism (email, Slack, issue creation)?

**4. Document UX/Diagnostics Unknowns**
   - What granularity for stage-by-stage stats (per-pass, per-transformation)?
   - How to capture simplification decisions (logging, structured output)?
   - What metrics matter most (term count, operation count, depth, sparsity)?
   - Output format (JSON, YAML, text table)?
   - Performance impact of diagnostics (acceptable overhead)?

**5. Document Process Improvement Unknowns**
   - How to enforce "update docs after each PR" (pre-commit hooks, checklist)?
   - What format for incremental SPRINT_LOG updates?
   - How to track actual time spent (manual, automated)?
   - How to generate feature interaction tests (combinatorial explosion)?

### Changes

**File to Create:** `docs/planning/EPIC_2/SPRINT_11/KNOWN_UNKNOWNS.md`

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify document created
test -f docs/planning/EPIC_2/SPRINT_11/KNOWN_UNKNOWNS.md

# Verify minimum content (50+ unknowns across 5 categories)
wc -l docs/planning/EPIC_2/SPRINT_11/KNOWN_UNKNOWNS.md | awk '{if ($1 > 300) print "✅ Sufficient content"; else print "❌ Insufficient content"}'

# Verify categories present
grep -q "Aggressive Simplification" docs/planning/EPIC_2/SPRINT_11/KNOWN_UNKNOWNS.md && echo "✅ Simplification unknowns"
grep -q "Nested.*Indexing\|maxmin" docs/planning/EPIC_2/SPRINT_11/KNOWN_UNKNOWNS.md && echo "✅ Parser unknowns"
grep -q "CI.*Regression\|Guardrails" docs/planning/EPIC_2/SPRINT_11/KNOWN_UNKNOWNS.md && echo "✅ CI unknowns"
```

### Deliverables

- `KNOWN_UNKNOWNS.md` with 50+ documented unknowns
- Unknowns categorized by workstream (Simplification, Parser, CI, UX, Process)
- Each unknown has: assumption, verification method, priority, risk assessment
- Verification plan for Critical/High priority unknowns (Day 0-2 timeline)

### Acceptance Criteria

- [x] Document created with 50+ unknowns across 5 categories
- [x] All unknowns have assumption, verification method, priority, and risk if wrong
- [x] All Critical/High unknowns have verification plan with timeline
- [x] Unknowns cover all Sprint 11 features and action items
- [x] Template for updates during sprint defined
- [x] Verification deadlines assigned (Day 0/1/2)

---

## Task 2: Research maxmin.gms Nested/Subset Indexing

**Status:** 🔵 NOT STARTED  
**Priority:** Critical  
**Estimated Time:** 6 hours  
**Deadline:** Before Sprint 11 Day 1  
**Owner:** Parser team  
**Dependencies:** Task 1 (Known Unknowns)  
**Unknowns Verified:** 2.1, 2.2, 2.3, 2.4

### Objective

Research GAMS nested/subset indexing semantics, analyze maxmin.gms blocker in detail, and design implementation approach for achieving 100% Tier 1 parse rate.

### Why This Matters

maxmin.gms is the final GAMSLIB Tier 1 model at 18% parse rate (complexity 9/10). Unlocking this model achieves 100% Tier 1 coverage, completing Epic 2's primary parser goal.

Sprint 10 deferred maxmin.gms due to high complexity and risk. Sprint 11 allocates dedicated research and 8-12 hours implementation time.

### Background

**Current Status:**
- Parse rate: 90% (9/10 models)
- maxmin.gms: 18% parsed (main blocker: nested/subset indexing)
- Complexity: 9/10 (highest of all Tier 1 models)

**From Sprint 10 Retrospective:**
> "Plan maxmin.gms Implementation - Dedicated research phase for nested/subset indexing. Prototype approach before full implementation. Budget: 8-12 hours for complexity 9/10 feature."

**Prior Analysis:**
- `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/` may contain maxmin analysis
- Nested indexing involves subset conditions in equation domains
- Example: `Equation balance(i) $(subset(i)).. ...` or similar

### What Needs to Be Done

**1. Analyze maxmin.gms in Detail (2 hours)**
   - Download maxmin.gms from GAMSLIB
   - Identify all instances of nested/subset indexing
   - Document syntax patterns used
   - Identify which lines fail to parse (vs. parse correctly)
   - Create minimal reproducible examples for each pattern

**2. Research GAMS Nested/Subset Indexing Semantics (2 hours)**
   - Read GAMS documentation on subset indexing
   - Research conditional set operations (`$` operator)
   - Understand dynamic vs. static subsets
   - Research nested index scoping rules
   - Find examples in GAMS forums/documentation
   - Document edge cases (empty subsets, complex conditions)

**3. Design AST Representation (1 hour)**
   - How to represent subset conditions in AST?
   - Does `Set` node need `condition` field?
   - How to represent `$` operator in equation domains?
   - How to handle nested indices in `IndexedExpr`?
   - Update AST node definitions if needed

**4. Design Implementation Approach (1 hour)**
   - Grammar changes needed (parser rules for `$` operator)
   - Semantic analyzer changes (subset condition evaluation)
   - IR representation (how `Parameter`/`Equation` store conditions)
   - MCP generation (how subset conditions affect equation instances)
   - Test strategy (unit tests, integration tests, maxmin.gms end-to-end)

**5. Prototype if Time Permits**
   - Create minimal grammar rule for subset syntax
   - Test parsing simple subset examples
   - Validate approach before full implementation

### Changes

**Files to Create/Update:**
- `docs/research/nested_subset_indexing_research.md` - Research findings
- `docs/planning/EPIC_2/SPRINT_11/maxmin_implementation_plan.md` - Implementation design
- `tests/synthetic/nested_subset_indexing.gms` - Minimal test case

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify research document created
test -f docs/research/nested_subset_indexing_research.md && echo "✅ Research doc created"

# Verify implementation plan created
test -f docs/planning/EPIC_2/SPRINT_11/maxmin_implementation_plan.md && echo "✅ Implementation plan created"

# Verify minimal test case created
test -f tests/synthetic/nested_subset_indexing.gms && echo "✅ Minimal test case created"

# Verify maxmin.gms downloaded
test -f data/gamslib_nlp/maxmin.gms && echo "✅ maxmin.gms available"
```

### Deliverables

- Research document with GAMS nested/subset indexing semantics
- Implementation plan with grammar, AST, semantic, IR, MCP changes
- Minimal reproducible test cases for each pattern
- Complexity and risk assessment
- Estimated implementation time (should be 8-12 hours based on research)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.1, 2.2, 2.3, 2.4

### Acceptance Criteria

- [ ] maxmin.gms analyzed with all nested/subset indexing patterns documented
- [ ] GAMS semantics researched and documented
- [ ] AST representation designed for subset conditions
- [ ] Implementation approach documented with step-by-step plan
- [ ] Minimal test cases created for each pattern
- [ ] Complexity assessment confirms 8-12 hour budget is reasonable
- [ ] Edge cases identified (empty subsets, complex conditions, nested levels)
- [ ] Unknowns 2.1, 2.2, 2.3, 2.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 3: Design Aggressive Simplification Architecture

**Status:** 🔵 NOT STARTED  
**Priority:** Critical  
**Estimated Time:** 5 hours  
**Deadline:** Before Sprint 11 Day 1  
**Owner:** Simplification team  
**Dependencies:** Task 1 (Known Unknowns)  
**Unknowns Verified:** 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 1.10, 1.11

### Objective

Design comprehensive architecture for aggressive simplification mode implementing distribution/factoring, fraction simplification, nested operations, and division by multiplication as specified in PROJECT_PLAN.md.

### Why This Matters

Aggressive simplification is Sprint 11's primary feature with goal of ≥20% derivative term reduction. Poor architecture risks:
- Correctness bugs (wrong algebraic transformations)
- Expression explosion (>150% size growth without benefit)
- Performance regression (>10% conversion time overhead)
- Maintenance burden (complex transformation interactions)

Upfront design prevents costly refactoring during sprint.

### Background

**From PROJECT_PLAN.md (lines 456-638):**
- 5 transformation categories with 15+ specific patterns
- 8-step transformation pipeline
- Heuristics: size limit (150%), depth limit, cancellation detection
- Validation: FD checks, PATH alignment, performance <10% overhead
- Target: ≥20% term reduction on ≥50% benchmark models

**Existing Simplification:**
- Basic: Constant folding, identity operations (already implemented)
- Advanced: Like-term combination, fraction cancellation (already implemented)
- Aggressive: NEW - factoring, fraction ops, nested ops, division transformations

### What Needs to Be Done

**1. Review Existing Simplification Code (1 hour)**
   - Read `src/ad/simplification.py` (or equivalent)
   - Understand current basic/advanced simplification passes
   - Identify extension points for aggressive transformations
   - Document current architecture (visitor pattern, passes, etc.)

**2. Design Transformation Pipeline (2 hours)**
   - Map 5 transformation categories to code modules
   - Define 8-step pipeline execution order (per PROJECT_PLAN.md line 570)
   - Design data structures for tracking transformations
   - Design metrics collection (`--simplification-stats`)
   - Define heuristic thresholds (size 150%, depth limits)
   - Design cancellation detection algorithm

**3. Design Individual Transformations (1.5 hours)**
   - **Distribution/Factoring:** Common factor detection, multi-term factoring
   - **Fraction Simplification:** Distribution over division, combining fractions, common denominator handling
   - **Nested Operations:** Associativity for constants, division chain simplification
   - **Division by Multiplication:** Constant extraction, variable extraction
   - Define pattern matching approach for each transformation
   - Define applicability conditions (when to apply vs. skip)

**4. Design Validation and Safety (0.5 hour)**
   - Finite difference validation after each transformation
   - Expression size tracking (reject if >150% growth)
   - Depth limit enforcement
   - Rollback mechanism if transformation worsens expression
   - Performance budgeting per transformation type

### Changes

**Files to Create:**
- `docs/planning/EPIC_2/SPRINT_11/aggressive_simplification_architecture.md` - Architecture doc
- `docs/planning/EPIC_2/SPRINT_11/transformation_catalog.md` - Transformation patterns with examples

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify architecture document created
test -f docs/planning/EPIC_2/SPRINT_11/aggressive_simplification_architecture.md && echo "✅ Architecture doc created"

# Verify transformation catalog created
test -f docs/planning/EPIC_2/SPRINT_11/transformation_catalog.md && echo "✅ Transformation catalog created"

# Verify key sections present
grep -q "8-step pipeline\|Transformation.*Pipeline" docs/planning/EPIC_2/SPRINT_11/aggressive_simplification_architecture.md && echo "✅ Pipeline documented"
grep -q "Heuristics\|Safety" docs/planning/EPIC_2/SPRINT_11/aggressive_simplification_architecture.md && echo "✅ Safety mechanisms documented"
```

### Deliverables

- Architecture document with transformation pipeline design
- Transformation catalog with 15+ patterns, applicability conditions, examples
- Data structure designs for tracking transformations and metrics
- Heuristic thresholds documented with rationale
- Validation strategy (FD checks, size limits, performance budgets)
- Extension points in existing code identified
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 1.10, 1.11

### Acceptance Criteria

- [ ] Architecture document covers all 5 transformation categories from PROJECT_PLAN.md
- [ ] 8-step transformation pipeline designed with execution order justified
- [ ] Each transformation has pattern, applicability conditions, example
- [ ] Heuristics documented: size limit (150%), depth limit, cancellation detection
- [ ] Validation strategy defined: FD checks, PATH alignment, performance <10%
- [ ] Metrics collection designed for `--simplification-stats`
- [ ] Extension points in existing code identified
- [ ] Rollback/safety mechanisms designed to prevent expression explosion
- [ ] Unknowns 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 1.10, 1.11 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 4: Research Common Subexpression Elimination (CSE)

**Status:** 🔵 NOT STARTED  
**Priority:** High  
**Estimated Time:** 4 hours  
**Deadline:** Before Sprint 11 Day 1  
**Owner:** Simplification team  
**Dependencies:** Task 3 (Simplification Architecture)  
**Unknowns Verified:** 1.9

### Objective

Research CSE algorithms, design integration with aggressive simplification, and determine scope for Sprint 11 (opt-in via `--cse` flag vs. automatic).

### Why This Matters

CSE is listed as optional in PROJECT_PLAN.md but can provide significant benefits:
- Reduces redundant computation for expensive functions (exp, log, trig)
- Can reduce derivative terms through shared subexpression handling
- Complements factoring (exposes additional factoring opportunities)

However, CSE has trade-offs:
- Increases variable count (introduces temporaries)
- Complicates code generation (need to emit temporary definitions)
- Only beneficial if subexpression reused ≥2 times

Research needed to determine if Sprint 11 scope or defer to Sprint 12.

### Background

**From PROJECT_PLAN.md (line 565):**
> "CSE (Optional, if enabled) - final pass for repeated subexpressions"

**From PROJECT_PLAN.md (line 554):**
> "Explicit CSE (optional, controlled by flag): Pattern: Replace repeated subexpressions with temporary variables. Trade-off: Increases variable count; only beneficial if subexpression reused ≥2 times. Note: May be deferred to later sprint or made opt-in via --cse flag."

**Prior Work:**
- No existing CSE implementation
- Simplification currently handles duplicates via like-term combination, not explicit temporaries

### What Needs to Be Done

**1. Research CSE Algorithms (2 hours)**
   - Classic CSE algorithms (hash-based, tree traversal)
   - Cost models (when CSE improves vs. worsens performance)
   - Reuse threshold (≥2, ≥3, cost-based?)
   - Handling of function calls vs. binary ops
   - Integration with existing compiler passes

**2. Survey CSE in Similar Tools (1 hour)**
   - Compiler optimizers (LLVM, GCC)
   - Symbolic math tools (SymPy, Mathematica)
   - Automatic differentiation tools
   - Document best practices and pitfalls

**3. Design Integration Approach (1 hour)**
   - Where in 8-step pipeline does CSE fit? (Step 8 per PROJECT_PLAN.md)
   - How to detect repeated subexpressions? (AST hashing, equality checks)
   - How to generate temporary variable names? (`cse_tmp_1`, etc.)
   - How to emit temporaries in GAMS code? (separate `Variables` block)
   - How to update derivatives after CSE? (chain rule through temporaries)
   - Flag design: `--cse`, `--cse-threshold=N`, `--cse-min-cost=X`?

**4. Scope Decision for Sprint 11**
   - Implement full CSE in Sprint 11? (risky, significant scope)
   - Implement basic CSE (function calls only) in Sprint 11?
   - Defer to Sprint 12 and focus on other transformations?
   - Document recommendation with rationale

### Changes

**Files to Create:**
- `docs/research/cse_research.md` - CSE algorithm research
- `docs/planning/EPIC_2/SPRINT_11/cse_integration_design.md` - Integration design (if Sprint 11 scope)

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify research document created
test -f docs/research/cse_research.md && echo "✅ CSE research doc created"

# Verify scope decision documented
grep -q "Sprint 11 Scope Decision\|Recommendation" docs/research/cse_research.md && echo "✅ Scope decision documented"

# If Sprint 11 scope, verify integration design
if grep -q "Sprint 11.*Scope.*Yes\|Implement.*Sprint 11" docs/research/cse_research.md; then
  test -f docs/planning/EPIC_2/SPRINT_11/cse_integration_design.md && echo "✅ Integration design created"
fi
```

### Deliverables

- CSE research document with algorithms, cost models, best practices
- Scope recommendation for Sprint 11 with rationale
- If Sprint 11 scope: Integration design with implementation plan
- If deferred: Justification and Sprint 12 proposal
- Updated KNOWN_UNKNOWNS.md with verification results for Unknown 1.9

### Acceptance Criteria

- [ ] CSE algorithms researched (hash-based, tree traversal, cost models)
- [ ] Reuse threshold analyzed (≥2 vs. ≥3 vs. cost-based)
- [ ] Integration approach designed (where in pipeline, how to handle temporaries)
- [ ] Scope decision made: Sprint 11 full/basic/deferred with clear rationale
- [ ] If Sprint 11: Integration design complete with implementation plan
- [ ] If deferred: Sprint 12 proposal documented
- [ ] Unknown 1.9 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 5: Prototype Factoring Algorithms

**Status:** 🔵 NOT STARTED  
**Priority:** High  
**Estimated Time:** 5 hours  
**Deadline:** Before Sprint 11 Day 1  
**Owner:** Simplification team  
**Dependencies:** Task 3 (Simplification Architecture)  
**Unknowns Verified:** 1.1, 1.7

### Objective

Prototype distribution cancellation (`x*y + x*z → x*(y + z)`) and multi-term factoring algorithms to validate approach and identify implementation challenges before Sprint 11.

### Why This Matters

Factoring is the core of aggressive simplification (Category 1 in PROJECT_PLAN.md). Prototyping de-risks Sprint 11 by:
- Validating common factor detection algorithm
- Testing pattern matching approach
- Identifying edge cases (negative factors, fractional coefficients)
- Measuring performance impact
- Confirming ≥20% term reduction is achievable

### Background

**From PROJECT_PLAN.md (lines 465-486):**
- Distribution cancellation: `x*y + x*z → x*(y + z)`
- Multi-term factoring: `a*c + a*d + b*c + b*d → (a + b)*(c + d)`
- Reduces multiplication operations, exposes structure

**Example from PROJECT_PLAN.md:**
```
Before: grad_x = 2*exp(x)*sin(y) + 2*exp(x)*cos(y)
After:  grad_x = 2*exp(x)*(sin(y) + cos(y))
Operations: 4 multiplications, 1 addition → 2 multiplications, 1 addition (50% reduction)
```

**Challenges:**
- Detecting common factors across terms (AST equality)
- Handling non-commutative operations (careful reordering)
- Deciding when factoring improves expression (heuristics)

### What Needs to Be Done

**1. Implement Distribution Cancellation Prototype (2 hours)**
   - Create function `factor_common_terms(expr: BinaryOp) -> BinaryOp`
   - Detect common factors in sum terms (AST equality checks)
   - Extract common factor, create factored expression
   - Test on examples from PROJECT_PLAN.md
   - Test edge cases: negative factors, constant factors, function call factors

**2. Implement Multi-Term Factoring Prototype (2 hours)**
   - Create function `factor_multi_terms(expr: BinaryOp) -> BinaryOp`
   - Detect common factors across term pairs
   - Group terms by common factors
   - Recursively apply factoring
   - Test on `a*c + a*d + b*c + b*d` example
   - Test edge cases: partial factorability, nested sums

**3. Measure Performance and Effectiveness (1 hour)**
   - Run prototype on benchmark expressions
   - Measure term count reduction (target ≥20%)
   - Measure execution time (should be <1ms per expression)
   - Identify bottlenecks (AST equality checks, pattern matching)
   - Document findings and recommendations

### Changes

**Files to Create:**
- `prototypes/aggressive_simplification/factoring_prototype.py` - Prototype code
- `prototypes/aggressive_simplification/test_factoring.py` - Test cases
- `docs/planning/EPIC_2/SPRINT_11/factoring_prototype_results.md` - Results and findings

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify prototype created
test -f prototypes/aggressive_simplification/factoring_prototype.py && echo "✅ Prototype created"

# Verify test cases created
test -f prototypes/aggressive_simplification/test_factoring.py && echo "✅ Test cases created"

# Run prototype tests
cd prototypes/aggressive_simplification && python test_factoring.py && echo "✅ Tests pass"

# Verify results documented
test -f docs/planning/EPIC_2/SPRINT_11/factoring_prototype_results.md && echo "✅ Results documented"
```

### Deliverables

- Working prototype for distribution cancellation
- Working prototype for multi-term factoring
- Test suite with examples from PROJECT_PLAN.md and edge cases
- Performance measurements (execution time, term count reduction)
- Results document with findings, recommendations, identified challenges
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.7

### Acceptance Criteria

- [ ] Distribution cancellation prototype working on PROJECT_PLAN.md examples
- [ ] Multi-term factoring prototype working on `a*c + a*d + b*c + b*d`
- [ ] Test suite covers edge cases (negatives, constants, nested sums)
- [ ] Performance measured: <1ms per expression, ≥20% term reduction on examples
- [ ] Results documented with recommendations for Sprint 11 implementation
- [ ] Challenges identified (AST equality, pattern matching, heuristics)
- [ ] Unknowns 1.1, 1.7 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 6: Survey CI Regression Frameworks

**Status:** 🔵 NOT STARTED  
**Priority:** High  
**Estimated Time:** 3 hours  
**Deadline:** Before Sprint 11 Day 1  
**Owner:** Infrastructure team  
**Dependencies:** Task 1 (Known Unknowns)  
**Unknowns Verified:** 3.3, 3.4

### Objective

Survey CI frameworks and tools for implementing regression guardrails with GAMSLib sampling, PATH smoke tests, and performance thresholds.

### Why This Matters

Sprint 11 introduces CI regression guardrails to prevent regressions as codebase grows. Without automated checks:
- Parse rate could regress (models that worked start failing)
- Performance could degrade (conversion time increases)
- PATH solver compatibility could break (MCP generation changes)

CI guardrails catch these issues before merge, preventing costly rollbacks.

### Background

**From PROJECT_PLAN.md (line 447):**
> "CI Regression Guardrails: Add automated GAMSLib sampling to CI (parse/convert), PATH smoke tests (where licensing permits), performance thresholds with alerting."

**Current CI:**
- GitHub Actions for testing (`pytest`, linting, type checking)
- No GAMSLib sampling
- No PATH integration
- No performance tracking

**Sprint 11 Acceptance Criteria:**
> "CI guardrails run on every PR/nightly and block regressions per thresholds."

### What Needs to Be Done

**1. Survey CI Tools and Frameworks (1 hour)**
   - GitHub Actions features (matrix builds, caching, artifacts)
   - Performance tracking tools (pytest-benchmark, time command, custom)
   - Baseline storage (git-lfs, artifacts, separate repo)
   - Alert mechanisms (GitHub Actions annotations, Slack, email)
   - Parallelization (matrix builds, concurrent jobs)

**2. Research GAMSLib Testing Approaches (1 hour)**
   - How to select models for CI (all 10 Tier 1, random sample, stratified)
   - How often to run (every PR, nightly, weekly)
   - What to test (parse only, parse+convert, parse+convert+solve)
   - How to handle flaky tests (retries, tolerance)
   - How to update baselines (manual approval, automatic on main)

**3. Research PATH Integration (0.5 hour)**
   - PATH licensing for CI (is it allowed?)
   - PATH installation in CI environment (apt, conda, manual)
   - PATH timeout handling (kill after 30s, 60s)
   - PATH result validation (solution check, KKT check)

**4. Design Performance Tracking (0.5 hour)**
   - What metrics to track (parse time, convert time, memory, term count)
   - What thresholds to use (20% regression, 50% regression, absolute time)
   - How to store baselines (JSON files, artifacts)
   - How to visualize trends (dashboard, plots, text report)

### Changes

**Files to Create:**
- `docs/planning/EPIC_2/SPRINT_11/ci_regression_framework_survey.md` - Survey results

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify survey document created
test -f docs/planning/EPIC_2/SPRINT_11/ci_regression_framework_survey.md && echo "✅ Survey doc created"

# Verify key sections present
grep -q "GitHub Actions\|CI Framework" docs/planning/EPIC_2/SPRINT_11/ci_regression_framework_survey.md && echo "✅ CI framework surveyed"
grep -q "GAMSLib.*Sampling\|Model Selection" docs/planning/EPIC_2/SPRINT_11/ci_regression_framework_survey.md && echo "✅ GAMSLib approach surveyed"
grep -q "PATH.*Integration\|Solver" docs/planning/EPIC_2/SPRINT_11/ci_regression_framework_survey.md && echo "✅ PATH integration surveyed"
grep -q "Performance.*Tracking\|Metrics" docs/planning/EPIC_2/SPRINT_11/ci_regression_framework_survey.md && echo "✅ Performance tracking surveyed"
```

### Deliverables

- CI framework survey with tool recommendations
- GAMSLib sampling strategy (which models, how often)
- PATH integration approach (licensing, installation, validation)
- Performance tracking design (metrics, thresholds, storage)
- Recommended CI workflow structure
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.3, 3.4

### Acceptance Criteria

- [ ] GitHub Actions capabilities surveyed (matrix, caching, artifacts, alerts)
- [ ] GAMSLib sampling strategy designed (model selection, frequency, test scope)
- [ ] PATH integration approach defined (licensing clarified, installation method)
- [ ] Performance tracking designed (metrics, thresholds, baseline storage)
- [ ] Recommended CI workflow structure documented
- [ ] Estimated CI runtime calculated (should be <10 minutes per PR)
- [ ] Unknowns 3.3, 3.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 7: Design GAMSLib Sampling Strategy

**Status:** 🔵 NOT STARTED  
**Priority:** High  
**Estimated Time:** 3 hours  
**Deadline:** Before Sprint 11 Day 1  
**Owner:** Infrastructure team  
**Dependencies:** Task 6 (CI Framework Survey)  
**Unknowns Verified:** 3.1

### Objective

Design detailed GAMSLib sampling strategy for CI regression testing: which models, how often, what to test, pass/fail criteria.

### Why This Matters

Automated GAMSLib sampling prevents parse rate regressions. Without strategy:
- Too many models = CI too slow (>10 min)
- Too few models = regressions slip through
- Wrong models = false positives or false negatives
- No strategy = arbitrary, unreliable testing

Well-designed sampling balances coverage, speed, and reliability.

### Background

**Current Testing:**
- Manual testing of Tier 1 models via `scripts/measure_parse_rate.py`
- No automated CI testing of GAMSLIB models
- Parse rate: 90% (9/10 Tier 1 models)

**Sprint 11 Goal:**
- Automated CI sampling to detect parse rate regressions
- Run on every PR and nightly
- Block regressions (parse rate drops, previously passing models fail)

### What Needs to Be Done

**1. Define Model Selection Strategy (1 hour)**
   - **Fixed Subset Approach:**
     - Always test all 10 Tier 1 models (comprehensive, reliable)
     - Pros: 100% Tier 1 coverage, catches all regressions
     - Cons: ~30-60 seconds runtime
   - **Stratified Random Sampling:**
     - Sample N models per complexity tier (balanced coverage)
     - Pros: Faster if Tier 2/3 added
     - Cons: May miss specific model regressions
   - **Representative Subset:**
     - Select 3-5 "canary" models covering diverse features
     - Pros: Fast (<10s), catches most regressions
     - Cons: Lower coverage
   - **Recommendation:** Start with fixed subset (all 10 Tier 1), add stratified when Tier 2+ added

**2. Define Test Frequency (0.5 hour)**
   - **Every PR:** Catches regressions before merge (recommended)
   - **Nightly:** Slower feedback, cheaper CI (supplement)
   - **Weekly:** Too slow, regressions pile up (not recommended)
   - **Recommendation:** Every PR for Tier 1, nightly for Tier 2+ when added

**3. Define Test Scope (0.5 hour)**
   - **Parse only:** Fast, catches parse regressions
   - **Parse + convert:** Catches conversion regressions
   - **Parse + convert + solve:** Catches MCP generation bugs (requires PATH)
   - **Recommendation:** Parse + convert on every PR, parse + solve nightly (if PATH available)

**4. Define Pass/Fail Criteria (1 hour)**
   - **Parse rate threshold:** Must maintain ≥90% (allow ±0% regression)
   - **Individual model failures:** Any previously passing model fails = fail CI
   - **Performance thresholds:** Parse time >20% slower = warn, >50% slower = fail
   - **Baseline updates:** On main merge, update baselines automatically
   - **Flaky test handling:** Retry once on failure, require 2 consecutive failures to fail CI

### Changes

**Files to Create:**
- `docs/planning/EPIC_2/SPRINT_11/gamslib_sampling_strategy.md` - Detailed strategy

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify strategy document created
test -f docs/planning/EPIC_2/SPRINT_11/gamslib_sampling_strategy.md && echo "✅ Strategy doc created"

# Verify key sections present
grep -q "Model Selection\|Fixed Subset\|Stratified" docs/planning/EPIC_2/SPRINT_11/gamslib_sampling_strategy.md && echo "✅ Model selection defined"
grep -q "Test Frequency\|Every PR\|Nightly" docs/planning/EPIC_2/SPRINT_11/gamslib_sampling_strategy.md && echo "✅ Test frequency defined"
grep -q "Pass.*Fail.*Criteria\|Threshold" docs/planning/EPIC_2/SPRINT_11/gamslib_sampling_strategy.md && echo "✅ Pass/fail criteria defined"
```

### Deliverables

- GAMSLib sampling strategy document
- Model selection approach (fixed subset of 10 Tier 1 recommended)
- Test frequency (every PR recommended)
- Test scope (parse + convert recommended, solve nightly if PATH available)
- Pass/fail criteria (≥90% parse rate, no model regressions, <20% performance regression)
- Baseline update process
- Updated KNOWN_UNKNOWNS.md with verification results for Unknown 3.1

### Acceptance Criteria

- [ ] Model selection strategy defined with rationale
- [ ] Test frequency defined (every PR, nightly, or both)
- [ ] Test scope defined (parse, convert, solve combinations)
- [ ] Pass/fail criteria defined with specific thresholds
- [ ] Baseline update process defined
- [ ] Flaky test handling approach defined
- [ ] Estimated CI runtime calculated (should be <2 minutes for 10 models)
- [ ] Unknown 3.1 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 8: Research PATH Smoke Test Integration

**Status:** 🔵 NOT STARTED  
**Priority:** Medium  
**Estimated Time:** 3 hours  
**Deadline:** Before Sprint 11 Day 1  
**Owner:** Infrastructure team  
**Dependencies:** Task 6 (CI Framework Survey)  
**Unknowns Verified:** 3.2

### Objective

Research how to integrate PATH solver into CI for smoke tests validating MCP generation correctness.

### Why This Matters

PATH smoke tests catch MCP generation bugs that parse/convert checks miss:
- Incorrect complementarity pairs (variables and equations mismatched)
- Infeasible formulations (over/under-constrained systems)
- Numerical issues (poor scaling, unbounded variables)

PATH validation ensures generated MCP is not just syntactically correct but also solvable.

### Background

**Current Testing:**
- No PATH testing in CI
- Manual PATH testing via `scripts/validate_with_path.py`
- Some PATH integration tests in `tests/validation/test_path_solver.py`

**Sprint 11 Goal:**
> "PATH smoke tests (where licensing permits)"

**Challenge:**
- PATH licensing may restrict CI use
- PATH installation in CI environment may be complex
- Timeout handling needed (some models may not converge)

### What Needs to Be Done

**1. Research PATH Licensing for CI (1 hour)**
   - Review PATH license terms (academic, commercial)
   - Check if CI use is permitted (GitHub Actions = cloud compute)
   - Contact PATH maintainers if licensing unclear
   - Identify alternatives if PATH not permitted (KNITRO, IPOPT with complementarity)
   - **Decision:** If PATH not permitted, defer PATH smoke tests to Sprint 12 or use alternative

**2. Research PATH Installation in CI (1 hour)**
   - Check if PATH available via apt, conda, pip
   - Research manual installation (download binary, set environment variables)
   - Test PATH installation in local GitHub Actions workflow
   - Estimate installation time (should be <1 minute)
   - Document installation steps

**3. Design Smoke Test Approach (1 hour)**
   - Which models to test? (Subset of Tier 1 with known solutions)
   - What to validate? (Solve status, solution values, KKT check)
   - How to handle timeouts? (Kill after 30-60 seconds)
   - How to handle solve failures? (Not all models guaranteed to converge)
   - Pass/fail criteria (models that previously solved must still solve)
   - Baseline storage (expected solve status, objective value tolerance)

### Changes

**Files to Create:**
- `docs/planning/EPIC_2/SPRINT_11/path_smoke_test_research.md` - Research findings and recommendations

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify research document created
test -f docs/planning/EPIC_2/SPRINT_11/path_smoke_test_research.md && echo "✅ Research doc created"

# Verify licensing research done
grep -q "Licensing\|License.*PATH" docs/planning/EPIC_2/SPRINT_11/path_smoke_test_research.md && echo "✅ Licensing researched"

# Verify installation research done
grep -q "Installation\|Install.*PATH" docs/planning/EPIC_2/SPRINT_11/path_smoke_test_research.md && echo "✅ Installation researched"

# Verify recommendation present
grep -q "Recommendation\|Sprint 11 Scope" docs/planning/EPIC_2/SPRINT_11/path_smoke_test_research.md && echo "✅ Recommendation documented"
```

### Deliverables

- PATH licensing research with CI use clarification
- PATH installation instructions for GitHub Actions
- Smoke test design (model selection, validation criteria, timeout handling)
- Recommendation: Sprint 11 scope or defer to Sprint 12
- Updated KNOWN_UNKNOWNS.md with verification results for Unknown 3.2

### Acceptance Criteria

- [ ] PATH licensing for CI clarified (permitted, restricted, or unclear)
- [ ] PATH installation approach documented (apt, conda, manual)
- [ ] Smoke test design complete (models, validation, timeouts, pass/fail criteria)
- [ ] Recommendation made: Sprint 11 full/basic/deferred with rationale
- [ ] If Sprint 11: Implementation plan outlined
- [ ] If deferred: Alternative validation approach proposed
- [ ] Unknown 3.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 9: Design Diagnostics Mode Architecture

**Status:** 🔵 NOT STARTED  
**Priority:** Medium  
**Estimated Time:** 4 hours  
**Deadline:** Before Sprint 11 Day 1  
**Owner:** UX team  
**Dependencies:** Task 1 (Known Unknowns)  
**Unknowns Verified:** 4.1, 4.2

### Objective

Design architecture for `--diagnostic` mode showing stage-by-stage stats, pipeline decisions, and simplification summaries.

### Why This Matters

Diagnostics mode improves developer UX by providing visibility into conversion pipeline:
- Which stage is slow? (parse, semantic, simplification, conversion, MCP generation)
- Why did simplification reduce term count by only 5% (expected 20%)?
- Which transformations applied vs. skipped?
- Where are bottlenecks in large models?

Good diagnostics enable debugging, performance tuning, and user confidence.

### Background

**From PROJECT_PLAN.md (line 449):**
> "Introduce deeper diagnostics mode (`--diagnostic`) showing stage-by-stage stats, pipeline decisions, and simplification summaries."

**Current Diagnostics:**
- Basic error messages
- No stage-by-stage stats
- No simplification visibility
- No performance profiling

**Sprint 11 Acceptance Criteria:**
> "Diagnostics mode validated on representative models; UX checklist updated."

### What Needs to Be Done

**1. Define Diagnostic Output Structure (1.5 hours)**
   - What stages to report? (parse, semantic, simplification passes, conversion, MCP gen)
   - What metrics per stage? (time, memory, input/output size, transformation count)
   - What format? (JSON, YAML, text table, structured log)
   - Example output for simple NLP model
   - Verbosity levels (summary, detailed, debug)

**2. Design Simplification Diagnostics (1.5 hours)**
   - What to report per transformation? (attempted, applied, skipped, reason)
   - Term count before/after each pass
   - Operation count reduction
   - Expression depth changes
   - Heuristic triggers (size limit hit, depth limit hit, cancellation detected)
   - Example output for aggressive simplification

**3. Design Performance Profiling (0.5 hour)**
   - How to measure stage times? (Python `time.perf_counter`, profiler)
   - How to measure memory? (tracemalloc, psutil)
   - Overhead acceptable? (<5% performance impact)
   - Profiling granularity (per-stage, per-function, per-transformation)

**4. Design Output Mechanism (0.5 hour)**
   - Stdout with pretty formatting (default)
   - File output `--diagnostic-output=stats.json`
   - Structured logging (JSON lines for machine parsing)
   - Dashboard integration (future Sprint 12 work)

### Changes

**Files to Create:**
- `docs/planning/EPIC_2/SPRINT_11/diagnostics_mode_architecture.md` - Architecture doc
- `docs/planning/EPIC_2/SPRINT_11/diagnostics_output_examples.md` - Example outputs

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify architecture document created
test -f docs/planning/EPIC_2/SPRINT_11/diagnostics_mode_architecture.md && echo "✅ Architecture doc created"

# Verify example outputs created
test -f docs/planning/EPIC_2/SPRINT_11/diagnostics_output_examples.md && echo "✅ Example outputs created"

# Verify key sections present
grep -q "Stage.*Stats\|Pipeline" docs/planning/EPIC_2/SPRINT_11/diagnostics_mode_architecture.md && echo "✅ Stage stats designed"
grep -q "Simplification.*Diagnostics" docs/planning/EPIC_2/SPRINT_11/diagnostics_mode_architecture.md && echo "✅ Simplification diagnostics designed"
```

### Deliverables

- Diagnostics mode architecture document
- Example diagnostic outputs for simple and complex models
- Stage-by-stage metrics defined (time, memory, size, transformation count)
- Simplification diagnostics design (per-transformation reporting)
- Output format specification (JSON, text, YAML)
- Performance overhead assessment (<5% target)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.1, 4.2

### Acceptance Criteria

- [ ] Diagnostic output structure defined with stages, metrics, format
- [ ] Simplification diagnostics designed (transformations attempted/applied/skipped)
- [ ] Performance profiling approach defined (time, memory measurements)
- [ ] Example outputs created for simple and complex models
- [ ] Output mechanism designed (stdout, file, structured logging)
- [ ] Performance overhead estimated (<5% acceptable)
- [ ] Verbosity levels defined (summary, detailed, debug)
- [ ] Unknowns 4.1, 4.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 10: Establish Incremental Documentation Process

**Status:** 🔵 NOT STARTED  
**Priority:** High  
**Estimated Time:** 2 hours  
**Deadline:** Before Sprint 11 Day 1  
**Owner:** Process improvement  
**Dependencies:** Task 1 (Known Unknowns)  
**Unknowns Verified:** 5.1, 5.2

### Objective

Design and document incremental documentation process per Sprint 10 Retrospective Action Item #3: update SPRINT_LOG.md after each PR merge, not at end of sprint.

### Why This Matters

**From Sprint 10 Retrospective (lines 238-245):**
> "Incremental Documentation Process (Process Improvement)
> - Update SPRINT_LOG.md after each PR merge (not end of sprint)
> - Document decisions and lessons immediately
> - Add 'update docs' to PR checklist template
> - Create incremental documentation workflow guide"

Sprint 10 concentrated documentation on Day 10, increasing end-of-sprint workload. Incremental approach:
- Reduces Day 10 burden
- Captures decisions while fresh
- Enables real-time progress tracking
- Improves sprint transparency

### Background

**Sprint 10 Experience:**
- SPRINT_LOG.md and RETROSPECTIVE.md created on Day 10
- ~2 hours documentation time at end of sprint
- Some details forgotten or reconstructed from git history
- Worked well but could be improved

**Sprint 11 Opportunity:**
- Implement incremental process from Day 1
- Test process improvements for future sprints
- Reduce end-of-sprint documentation burden

### What Needs to Be Done

**1. Design SPRINT_LOG.md Template (0.5 hour)**
   - Section structure (daily progress, feature implementation, metrics)
   - Incremental update format (append-only vs. section updates)
   - Required content per PR (what was done, why, results, metrics)
   - Example entry for typical PR

**2. Design PR Checklist Integration (0.5 hour)**
   - Add "Update SPRINT_LOG.md" to PR template checklist
   - Add "Document key decisions" to PR template
   - Add link to SPRINT_LOG template in PR template
   - Enforce via PR review (reviewer checks docs updated)

**3. Create Documentation Workflow Guide (0.5 hour)**
   - When to update: immediately after PR merge
   - What to document: feature changes, decisions, metrics, blockers
   - How to update: append to daily section, update metrics table
   - Examples of good vs. bad documentation
   - Time estimate: 5-10 minutes per PR

**4. Create Pre-populated SPRINT_LOG.md (0.5 hour)**
   - Sprint 11 header and metadata
   - Daily sections for Days 1-10 (pre-populated with dates)
   - Metrics tables (parse rate progression, test counts)
   - Placeholder sections for features, decisions, retrospective items

### Changes

**Files to Create:**
- `docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md` - Pre-populated log
- `docs/planning/EPIC_2/SPRINT_11/incremental_documentation_guide.md` - Workflow guide
- `.github/pull_request_template.md` - Updated PR template (or create if doesn't exist)

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify SPRINT_LOG.md pre-populated
test -f docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md && echo "✅ SPRINT_LOG.md created"
grep -q "Day 1\|Day 2\|Day 3" docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md && echo "✅ Daily sections present"

# Verify workflow guide created
test -f docs/planning/EPIC_2/SPRINT_11/incremental_documentation_guide.md && echo "✅ Workflow guide created"

# Verify PR template updated (if exists) or created
if [ -f .github/pull_request_template.md ]; then
  grep -q "SPRINT_LOG\|Update.*documentation" .github/pull_request_template.md && echo "✅ PR template updated"
else
  echo "⚠️  PR template doesn't exist, create in Sprint 11"
fi
```

### Deliverables

- Pre-populated SPRINT_LOG.md with daily sections for Sprint 11
- Incremental documentation workflow guide
- Updated PR template with documentation checklist items
- Example documentation entries (good and bad)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 5.1, 5.2

### Acceptance Criteria

- [ ] SPRINT_LOG.md pre-populated with Days 1-10 sections
- [ ] Workflow guide created with when/what/how to document
- [ ] PR template updated with "Update SPRINT_LOG.md" checklist item
- [ ] Example documentation entries provided (1 good, 1 bad with explanation)
- [ ] Time estimate documented: 5-10 minutes per PR
- [ ] Enforcement mechanism defined (PR reviewer checks)
- [ ] Unknowns 5.1, 5.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 11: Create Feature Interaction Test Framework

**Status:** 🔵 NOT STARTED  
**Priority:** Medium  
**Estimated Time:** 3 hours  
**Deadline:** Before Sprint 11 Day 1  
**Owner:** QA / Testing  
**Dependencies:** Task 1 (Known Unknowns)  
**Unknowns Verified:** 5.3

### Objective

Design framework for testing feature interactions per Sprint 10 Retrospective Action Item #5: test combinations incrementally, create synthetic tests combining multiple features.

### Why This Matters

**From Sprint 10 Retrospective (lines 251-256):**
> "Feature Interaction Testing (Quality Improvement)
> - Test feature combinations incrementally (after each PR, not end of sprint)
> - Create synthetic tests that combine multiple features
> - Add 'integration test' step to PR checklist
> - Validate no regressions when features interact"

Features may work individually but interact poorly:
- Simplification + nested indexing may create invalid expressions
- Aggressive factoring + CSE may interfere
- Diagnostics mode may not capture simplified expressions correctly

Interaction testing catches these issues early.

### Background

**Sprint 10 Experience:**
- Integration testing done on Day 7 (after all features complete)
- Could have tested combinations earlier
- No systematic framework for interaction testing

**Sprint 11 Complexity:**
- 3 major workstreams (simplification, parser, CI/UX)
- Multiple transformation types in simplification
- Interactions possible: simplification + nested indexing, simplification + diagnostics

### What Needs to Be Done

**1. Identify Potential Feature Interactions (1 hour)**
   - Simplification + nested indexing (do simplified expressions handle nested indices?)
   - Factoring + CSE (do they interfere or complement?)
   - Simplification + diagnostics (does diagnostics capture transformation decisions?)
   - Aggressive simplification + basic/advanced simplification (does pipeline work?)
   - New features + existing Sprint 9/10 features (regressions?)

**2. Design Interaction Test Framework (1 hour)**
   - Test organization: `tests/integration/test_feature_interactions.py`
   - Test naming: `test_simplification_with_nested_indexing`
   - Test structure: setup feature A, setup feature B, exercise together, validate
   - Synthetic test files combining features: `tests/synthetic/combined_features/*.gms`
   - When to run: after each PR adds a feature, run all interaction tests

**3. Create Initial Interaction Tests (1 hour)**
   - Create 3-5 interaction test cases
   - Example: Simplification + function calls (Sprint 10 feature)
   - Example: Simplification + comma-separated scalars (Sprint 10 feature)
   - Example: Simplification + nested indexing (Sprint 11 feature, placeholder test)
   - Document test rationale and expected behavior

### Changes

**Files to Create:**
- `tests/integration/test_feature_interactions.py` - Interaction test suite (initial)
- `tests/synthetic/combined_features/` - Directory for synthetic combination tests
- `tests/synthetic/combined_features/simplification_with_functions.gms` - Example
- `docs/planning/EPIC_2/SPRINT_11/feature_interaction_testing_guide.md` - Guide

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify interaction test suite created
test -f tests/integration/test_feature_interactions.py && echo "✅ Interaction test suite created"

# Verify synthetic tests directory created
test -d tests/synthetic/combined_features && echo "✅ Combined features directory created"

# Verify at least one synthetic test created
test -f tests/synthetic/combined_features/simplification_with_functions.gms && echo "✅ Example synthetic test created"

# Verify guide created
test -f docs/planning/EPIC_2/SPRINT_11/feature_interaction_testing_guide.md && echo "✅ Testing guide created"

# Run initial tests
pytest tests/integration/test_feature_interactions.py -v && echo "✅ Initial tests pass"
```

### Deliverables

- Feature interaction test suite with 3-5 initial tests
- Synthetic test directory for combined feature tests
- At least 1 example synthetic test (simplification + functions)
- Feature interaction testing guide
- PR checklist item: "Run interaction tests if feature added"
- Updated KNOWN_UNKNOWNS.md with verification results for Unknown 5.3

### Acceptance Criteria

- [ ] Potential feature interactions identified (≥5 interactions documented)
- [ ] Interaction test framework designed (organization, naming, structure)
- [ ] Initial test suite created with 3-5 tests
- [ ] Synthetic test directory created with ≥1 example test
- [ ] Testing guide created with when/how to write interaction tests
- [ ] Tests pass on current codebase
- [ ] PR checklist item added for interaction testing
- [ ] Unknown 5.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 12: Plan Sprint 11 Detailed Schedule

**Status:** 🔵 NOT STARTED  
**Priority:** Critical  
**Estimated Time:** 5 hours  
**Deadline:** Before Sprint 11 Day 1  
**Owner:** Sprint planning  
**Dependencies:** Tasks 1-11 (all prep tasks)  
**Unknowns Verified:** 6.1, 7.1

### Objective

Create detailed day-by-day Sprint 11 schedule based on prep findings, incorporating aggressive simplification, maxmin.gms, CI guardrails, UX improvements, and process improvements.

### Why This Matters

Sprint 11 has the highest scope of any sprint to date:
- 3 major workstreams (simplification, parser, infrastructure)
- 6 action items from Sprint 10 Retrospective
- Multiple dependencies between tasks

Detailed schedule with effort estimates, dependencies, and checkpoints prevents:
- Scope creep (trying to do too much)
- Schedule slips (missing dependencies)
- Burnout (overcommitment)
- Surprises (late-discovered blockers)

### Background

**Sprint 10 Success:**
- 10-day schedule with daily deliverables
- Mid-sprint checkpoint on Day 5
- Goal achieved Day 6 (4 days ahead)
- Prep phase enabled accurate scheduling

**Sprint 11 Scope:**
- Aggressive simplification (5 transformation categories)
- maxmin.gms implementation (8-12 hours budgeted)
- CI guardrails (GAMSLib sampling, PATH smoke tests, performance)
- Diagnostics mode
- Process improvements (incremental docs, interaction tests)

**Sprint 11 Acceptance Criteria:**
- ≥20% derivative term reduction on ≥50% models
- 100% Tier 1 parse rate (maxmin.gms 18% → 100%)
- CI guardrails running on every PR
- Diagnostics mode validated

### What Needs to Be Done

**1. Synthesize Prep Task Findings (1 hour)**
   - Review all prep task deliverables (Tasks 1-11)
   - Extract effort estimates, complexity assessments, risks
   - Identify dependencies between features
   - Document any scope reductions (e.g., defer CSE if research recommends)

**2. Define Sprint 11 Phases (1 hour)**
   - Phase 1: maxmin.gms research + initial implementation (Days 1-3)
   - Phase 2: Aggressive simplification core (factoring, fractions) (Days 3-5)
   - Phase 3: Aggressive simplification advanced (nested ops, division transformations) (Days 5-7)
   - Phase 4: CI guardrails implementation (Days 6-8)
   - Phase 5: Diagnostics mode + integration testing (Days 8-9)
   - Phase 6: Final validation + retrospective (Day 10)

**3. Allocate Features to Days (2 hours)**
   - Day 1: maxmin.gms research (verify nested/subset indexing approach)
   - Day 2: maxmin.gms implementation part 1 (grammar, AST)
   - Day 3: maxmin.gms implementation part 2 (semantic, IR) + checkpoint (should achieve 100% Tier 1)
   - Day 4: Aggressive simplification architecture + factoring (distribution cancellation)
   - Day 5: Aggressive simplification fraction ops + checkpoint (verify term reduction)
   - Day 6: Aggressive simplification nested ops + division transformations
   - Day 7: CI guardrails (GAMSLib sampling workflow)
   - Day 8: CI guardrails (performance thresholds) + diagnostics mode
   - Day 9: Integration testing + final validation
   - Day 10: Documentation + retrospective

**4. Define Checkpoints and Risks (1 hour)**
   - Day 3 checkpoint: maxmin.gms passing (100% Tier 1 achieved)
   - Day 5 checkpoint: ≥20% term reduction demonstrated on 3+ models
   - Day 7 checkpoint: CI workflow running (even if not all features complete)
   - Risks: maxmin.gms complexity 9/10 (may take >12 hours), CSE scope creep, PATH licensing

**5. Document Detailed Schedule (1 hour per day = 10 hours, but parallelize with outline)**
   - Create PLAN.md structure (like Sprint 10)
   - Daily sections with goals, tasks, deliverables, acceptance criteria
   - Effort estimates per task
   - Dependencies and blockers per task
   - Update incremental documentation process integration

### Changes

**Files to Create:**
- `docs/planning/EPIC_2/SPRINT_11/PLAN.md` - Detailed day-by-day schedule

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify PLAN.md created
test -f docs/planning/EPIC_2/SPRINT_11/PLAN.md && echo "✅ PLAN.md created"

# Verify daily sections present
for day in {1..10}; do
  grep -q "Day $day:" docs/planning/EPIC_2/SPRINT_11/PLAN.md && echo "✅ Day $day section present"
done

# Verify checkpoints documented
grep -q "Checkpoint" docs/planning/EPIC_2/SPRINT_11/PLAN.md && echo "✅ Checkpoints documented"

# Verify acceptance criteria present
grep -q "Acceptance Criteria" docs/planning/EPIC_2/SPRINT_11/PLAN.md && echo "✅ Acceptance criteria present"
```

### Deliverables

- Sprint 11 PLAN.md with 10 daily sections
- Each day has: goals, tasks, deliverables, effort estimates, acceptance criteria
- 3 checkpoints defined (Days 3, 5, 7)
- Risk mitigation strategies documented
- Total effort estimate (should be 20-30 hours based on Sprint 10 velocity)
- Dependencies and critical path identified
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 6.1, 7.1 (stretch goals)

### Acceptance Criteria

- [ ] PLAN.md created with 10 daily sections (Days 1-10)
- [ ] Each day has goals, tasks, deliverables, effort estimates, acceptance criteria
- [ ] Checkpoints defined on Days 3, 5, 7 with pass/fail criteria
- [ ] Total effort estimate calculated (20-30 hours target based on Sprint 10)
- [ ] Dependencies and critical path documented
- [ ] Risk mitigation strategies for maxmin.gms, CSE, PATH licensing
- [ ] Scope reductions documented if any (based on prep findings)
- [ ] Incremental documentation process integrated into daily tasks
- [ ] Unknowns 6.1, 7.1 verified and updated in KNOWN_UNKNOWNS.md (stretch goal research during scheduling)

---

## Summary

### Total Prep Effort

**Estimated:** 46 hours (~6 working days)

**Breakdown by Priority:**
- Critical (4 tasks): 19 hours (Tasks 1, 2, 3, 12)
- High (5 tasks): 20 hours (Tasks 4, 5, 6, 7, 10)
- Medium (3 tasks): 7 hours (Tasks 8, 9, 11)

### Critical Path

**Tasks 1 → 2 → 3 → 5 → 12** (23 hours)
1. Known Unknowns (3h) - Identify risks and research needs
2. maxmin.gms Research (6h) - Nested/subset indexing approach
3. Simplification Architecture (5h) - Design transformation pipeline
4. Factoring Prototype (5h) - Validate core transformation
5. Detailed Schedule (5h) - Plan Sprint 11 execution

**Why This Path:**
- Known Unknowns informs all other research
- maxmin.gms is highest priority (100% Tier 1 goal)
- Simplification architecture needed before prototyping
- Factoring prototype validates simplification approach
- Detailed schedule synthesizes all prep findings

### Success Criteria

Sprint 11 prep is complete when:
- [x] All 12 tasks completed and verified
- [x] Known Unknowns document created with 50+ documented unknowns
- [x] maxmin.gms implementation approach validated (8-12 hour estimate confirmed)
- [x] Aggressive simplification architecture designed and prototyped
- [x] CI regression framework selected and designed
- [x] Incremental documentation process established
- [x] Sprint 11 PLAN.md created with detailed day-by-day schedule
- [x] All Critical/High priority unknowns have verification plans
- [x] Scope reductions documented if needed (e.g., defer CSE)

### Prep Completion Checklist

Before Sprint 11 Day 1, verify:
- [ ] All 12 prep tasks marked complete
- [ ] All deliverables created and verified
- [ ] PLAN.md reviewed and approved
- [ ] Known unknowns reviewed, Critical/High items verified
- [ ] Team aligned on Sprint 11 scope and schedule
- [ ] Process improvements ready (incremental docs, interaction tests)
- [ ] CI infrastructure ready or implementation plan clear

---

## Appendix: Cross-References

### Sprint 11 Goals

**Source:** `docs/planning/EPIC_2/PROJECT_PLAN.md` (lines 438-705)

**Core Goals:**
1. Deliver `--simplification aggressive` with ≥20% derivative term reduction
2. Integrate CI regression guardrails (GAMSLib sampling, PATH smoke tests, performance)
3. Expand diagnostics features (`--diagnostic` mode)
4. Achieve 100% GAMSLIB Tier 1 parse rate (maxmin.gms)

**Action Items from Sprint 10 Retrospective:**
1. maxmin.gms implementation (parser coverage)
2. Effort estimation refinement (process improvement)
3. Incremental documentation (process improvement)
4. GAMSLIB Tier 2 exploration (future planning, stretch goal)
5. Feature interaction testing (quality improvement)
6. Nested function calls (parser coverage, stretch goal)

### Related Documents

**Research:**
- `docs/research/` - Research findings to be created during prep
- Prior sprint research on simplification (if any)

**Prior Sprints:**
- `docs/planning/EPIC_2/SPRINT_10/RETROSPECTIVE.md` - Sprint 10 lessons learned
- `docs/planning/EPIC_2/SPRINT_10/PLAN.md` - Sprint 10 schedule format
- `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/` - Model blocker analysis

**Testing:**
- `tests/synthetic/` - Synthetic test framework
- `tests/integration/` - Integration test suite

**Epic Goals:**
- `docs/planning/EPIC_2/GOALS.md` - Epic 2 objectives
- 100% GAMSLIB Tier 1 parse rate
- Production-ready conversion pipeline

### Prep Task Dependencies Graph

```
Task 1 (Known Unknowns) [3h]
  ├─> Task 2 (maxmin Research) [6h]
  ├─> Task 3 (Simplification Architecture) [5h]
  │     ├─> Task 4 (CSE Research) [4h]
  │     └─> Task 5 (Factoring Prototype) [5h]
  ├─> Task 6 (CI Framework Survey) [3h]
  │     ├─> Task 7 (GAMSLib Sampling) [3h]
  │     └─> Task 8 (PATH Integration) [3h]
  ├─> Task 9 (Diagnostics Architecture) [4h]
  ├─> Task 10 (Incremental Docs Process) [2h]
  └─> Task 11 (Interaction Testing) [3h]

All tasks ─> Task 12 (Detailed Schedule) [5h]
```

**Parallelization Opportunities:**
- Track A (Simplification): Tasks 3, 4, 5 (can run in parallel with other tracks)
- Track B (CI/Infrastructure): Tasks 6, 7, 8
- Track C (UX/Process): Tasks 9, 10, 11
- Track D (Parser): Task 2

Tasks 3-11 can run in parallel after Task 1 completes.

---

**Prep Plan Created:** [Date TBD]  
**Target Sprint 11 Start:** [Date TBD]  
**Estimated Prep Duration:** 6 working days (46 hours)
