# Sprint 7 Preparation Task Prompts

**Purpose:** Ready-to-use prompts for executing Sprint 7 prep tasks (Tasks 2-10)  
**Created:** 2025-11-14  
**Sprint:** Sprint 7 (Epic 2 - Parser Enhancements & GAMSLib Expansion)

---

## Table of Contents

- [Task 2: Analyze GAMSLib Parser Failures](#task-2-analyze-gamslib-parser-failures)
- [Task 3: Research Preprocessor Directive Handling](#task-3-research-preprocessor-directive-handling)
- [Task 4: Research Multi-Dimensional Set Indexing](#task-4-research-multi-dimensional-set-indexing)
- [Task 5: Profile Test Suite Performance](#task-5-profile-test-suite-performance)
- [Task 6: Survey GAMS Syntax Features for Wave 2](#task-6-survey-gams-syntax-features-for-wave-2)
- [Task 7: Design Line Number Tracking for Warnings](#task-7-design-line-number-tracking-for-warnings)
- [Task 8: Set Up CI for GAMSLib Regression Tracking](#task-8-set-up-ci-for-gamslib-regression-tracking)
- [Task 9: Create Parser Test Fixture Strategy](#task-9-create-parser-test-fixture-strategy)
- [Task 10: Plan Sprint 7 Detailed Schedule](#task-10-plan-sprint-7-detailed-schedule)

---

## Task 2: Analyze GAMSLib Parser Failures

### Prompt

```
On a new branch, complete Task 2 from docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md (lines 155-295): Analyze GAMSLib Parser Failures.

OBJECTIVES:
1. Perform detailed analysis of all 9 GAMSLib parser failures
2. Categorize error types and identify high-impact features
3. Prioritize parser enhancements for Sprint 7
4. Verify Known Unknowns 1.3, 3.1

UNKNOWNS TO VERIFY:
- Unknown 1.3: Is 30% GAMSLib parse rate achievable in Sprint 7?
- Unknown 3.1: Is 30% parse rate achievable with planned parser enhancements?

DELIVERABLES:
1. Create `docs/planning/EPIC_2/SPRINT_7/GAMSLIB_FAILURE_ANALYSIS.md` with:
   - Detailed analysis of all 9 failed models
   - Error messages categorized by feature type
   - Feature impact matrix (8-12 features)
   - Recommended feature priority (Critical/High/Medium/Low)
   - Quick wins list (2-3 features, unlock ≥2 models, <6h effort)
   - Hard problems list (features to defer to Sprint 8+)

2. Update `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md`:
   - For Unknown 1.3 (lines 344-387):
     * Change status from "🔍 Status: INCOMPLETE" to "✅ Status: VERIFIED" or "❌ Status: WRONG"
     * Add "Verification Results" section with:
       - Verified by: Task 2 (GAMSLib Failure Analysis)
       - Date: [today's date]
       - Findings: [Summary of what you learned]
       - Evidence: Link to GAMSLIB_FAILURE_ANALYSIS.md
       - Decision: [What this means for Sprint 7]
   - For Unknown 3.1 (lines 803-856):
     * Same verification results format

3. Update `docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md`:
   - Task 2 status (line 158): Change "🔵 NOT STARTED" to "✅ COMPLETE"
   - Add "Changes:" section (line 278) with summary of findings
   - Add "Result:" section (line 282) with links to created documents
   - Check off all acceptance criteria (lines 287-293)

4. Update `CHANGELOG.md`:
   - Add new entry under "Sprint 7 Prep: Task 2 - GAMSLib Failure Analysis - [date]"
   - Include summary of findings, deliverables created, unknowns verified
   - Link to GAMSLIB_FAILURE_ANALYSIS.md

RESEARCH STEPS:
1. Extract all parser error messages for 9 failed models (circle, himmel16, hs62, mathopt1, maxmin, mhw4dx, mingamma, rbrock, trig)
2. Categorize failures by feature type (preprocessor, sets, parameters, expressions, statements)
3. Build feature impact matrix (feature | models blocked | complexity | effort | priority)
4. Identify quick wins vs hard problems
5. Create recommended feature priority aligned with 30% parse rate goal
6. Document findings in GAMSLIB_FAILURE_ANALYSIS.md
7. Update KNOWN_UNKNOWNS.md with verification results for Unknowns 1.3, 3.1
8. Update PREP_PLAN.md Task 2 status and acceptance criteria
9. Update CHANGELOG.md

QUALITY CHECKS:
- ALWAYS run these commands before committing if you write any Python code:
  1. `make typecheck`
  2. `make lint`
  3. `make format`
  4. `make test`
- Ensure all links to documents are valid
- Verify all acceptance criteria are checked off

ACCEPTANCE CRITERIA (must all be checked):
- [ ] All 9 failed models analyzed
- [ ] Error messages categorized by feature type
- [ ] Feature impact matrix complete with effort estimates
- [ ] Quick wins identified (unlock ≥2 models, <6h effort)
- [ ] Recommended priority aligns with 30% parse rate goal
- [ ] Cross-referenced with PROJECT_PLAN.md Sprint 7 features
- [ ] Unknowns 1.3, 3.1 verified and updated in KNOWN_UNKNOWNS.md

COMMIT MESSAGE FORMAT:
"Complete Sprint 7 Prep Task 2: GAMSLib Failure Analysis

- Analyzed 9 GAMSLib parser failures
- Created feature impact matrix with [N] features
- Identified [N] quick wins and [N] hard problems
- Verified Unknowns 1.3, 3.1
- Updated PREP_PLAN.md Task 2 to COMPLETE
- Updated CHANGELOG.md"

When finished, commit all changes and push the branch.
```

---

## Task 3: Research Preprocessor Directive Handling

### Prompt

```
On a new branch, complete Task 3 from docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md (lines 297-451): Research Preprocessor Directive Handling.

PREREQUISITES:
- Task 2 (GAMSLib Failure Analysis) must be complete

OBJECTIVES:
1. Research and design preprocessor directive handling strategy
2. Compare full preprocessing vs mock/skip approach
3. Create concrete implementation plan for Sprint 7
4. Verify Known Unknowns 1.1, 1.4, 1.11

UNKNOWNS TO VERIFY:
- Unknown 1.1: Should we implement full preprocessing or mock directive handling?
- Unknown 1.4: Does Lark grammar support needed for preprocessor directives?
- Unknown 1.11: Does preprocessor handling require include file resolution?

DELIVERABLES:
1. Create `docs/research/preprocessor_directives.md` with:
   - Survey of all GAMS preprocessor directives
   - Complexity analysis for each category
   - Mock handling approach design (grammar changes, transformer updates)
   - Grammar prototype for mock directive handling
   - Test cases for common directive patterns (≥3 GAMSLib failures tested)
   - Recommendation: Full vs Mock vs Hybrid approach
   - Pros/cons analysis
   - Implementation plan for Sprint 7 (effort estimate, risks)
   - Limitations and warnings documented

2. Grammar prototype (either):
   - Modify `src/gams/grammar.lark` with preprocessor rules, OR
   - Create `src/gams/grammar_preprocessor_mock.lark` as prototype

3. Update `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md`:
   - For Unknown 1.1 (lines 245-297):
     * Change status to "✅ Status: VERIFIED" or "❌ Status: WRONG"
     * Add "Verification Results" with findings, decision, links
   - For Unknown 1.4 (lines 402-442):
     * Same verification results format
   - For Unknown 1.11 (lines 706-747):
     * Same verification results format

4. Update `docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md`:
   - Task 3 status (line 300): "🔵 NOT STARTED" → "✅ COMPLETE"
   - Add "Changes:" section (line 433) with summary
   - Add "Result:" section (line 437) with document links
   - Check off all acceptance criteria (lines 443-450)

5. Update `CHANGELOG.md`:
   - Add entry: "Sprint 7 Prep: Task 3 - Preprocessor Directive Handling - [date]"
   - Summary of research findings and recommendation
   - Links to docs/research/preprocessor_directives.md
   - Unknowns verified

RESEARCH STEPS:
1. Survey all GAMS preprocessor directives ($if, $set, $include, $ontext, etc.)
2. Analyze complexity for each directive category
3. Design mock handling approach with grammar modifications
4. Prototype grammar changes (recognize and skip directives)
5. Test prototype on ≥3 GAMSLib failures
6. Evaluate hybrid approach (mock simple, fail on complex)
7. Document recommendation with pros/cons
8. Update KNOWN_UNKNOWNS.md with verification results
9. Update PREP_PLAN.md Task 3 status
10. Update CHANGELOG.md

QUALITY CHECKS:
- ALWAYS run before committing if you write Python code:
  1. `make typecheck`
  2. `make lint`
  3. `make format`
  4. `make test`
- If you modify grammar.lark, test that existing tests still pass
- Ensure all acceptance criteria checked

ACCEPTANCE CRITERIA (must all be checked):
- [ ] All GAMS preprocessor directives surveyed
- [ ] Complexity analysis complete for each category
- [ ] Mock handling approach designed with grammar changes
- [ ] Prototype tested on ≥3 GAMSLib failures
- [ ] Recommendation documented with pros/cons
- [ ] Implementation effort estimated (Critical/High priority for Sprint 7)
- [ ] Limitations and warnings documented
- [ ] Unknowns 1.1, 1.4, 1.11 verified and updated in KNOWN_UNKNOWNS.md

COMMIT MESSAGE FORMAT:
"Complete Sprint 7 Prep Task 3: Preprocessor Directive Research

- Surveyed GAMS preprocessor directives
- Designed [mock/full/hybrid] handling approach
- Tested prototype on [N] GAMSLib models
- Recommendation: [approach] for Sprint 7
- Verified Unknowns 1.1, 1.4, 1.11
- Updated PREP_PLAN.md Task 3 to COMPLETE
- Updated CHANGELOG.md"

When finished, commit all changes and push the branch.
```

---

## Task 4: Research Multi-Dimensional Set Indexing

### Prompt

```
On a new branch, complete Task 4 from docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md (lines 453-623): Research Multi-Dimensional Set Indexing.

PREREQUISITES:
- Task 2 (GAMSLib Failure Analysis) must be complete

OBJECTIVES:
1. Research multi-dimensional set indexing requirements
2. Design IR representation and normalization strategy
3. Create implementation plan for Sprint 7
4. Verify Known Unknowns 1.2, 1.6

UNKNOWNS TO VERIFY:
- Unknown 1.2: How should multi-dimensional indexing be represented in IR?
- Unknown 1.6: Does multi-dimensional indexing affect KKT derivative computation?

DELIVERABLES:
1. Create `docs/research/multidimensional_indexing.md` with:
   - Pattern survey (parameters, variables, sets with 2D, 3D indexing)
   - IR design for multi-dimensional symbols
   - Normalization strategy with examples
   - Derivative computation approach
   - Grammar modification proposal
   - Impact analysis (parser, IR, normalization, AD modules)
   - Implementation plan for Sprint 7 (effort estimate, risks)
   - Test cases (simple, nested, conditional indexing)

2. Update `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md`:
   - For Unknown 1.2 (lines 299-342):
     * Change status to "✅ Status: VERIFIED" or "❌ Status: WRONG"
     * Add "Verification Results" with IR design decision, examples, links
   - For Unknown 1.6 (lines 488-536):
     * Same verification results format

3. Update `docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md`:
   - Task 4 status (line 456): "🔵 NOT STARTED" → "✅ COMPLETE"
   - Add "Changes:" section (line 603) with summary
   - Add "Result:" section (line 607) with document links
   - Check off all acceptance criteria (lines 613-620)

4. Update `CHANGELOG.md`:
   - Add entry: "Sprint 7 Prep: Task 4 - Multi-Dimensional Indexing Research - [date]"
   - Summary of IR design and normalization strategy
   - Links to docs/research/multidimensional_indexing.md
   - Unknowns verified

RESEARCH STEPS:
1. Survey multi-dimensional indexing patterns from GAMSLib failures
2. Design IR representation (e.g., Variable(name="X", indices=["i", "j", "k"]))
3. Design normalization strategy with examples
4. Analyze derivative computation impact (index matching logic)
5. Draft grammar modifications for indexed_ref, index_list
6. Document impact on parser, IR, normalization, AD modules
7. Create test case examples
8. Update KNOWN_UNKNOWNS.md with verification results
9. Update PREP_PLAN.md Task 4 status
10. Update CHANGELOG.md

QUALITY CHECKS:
- ALWAYS run before committing if you write Python code:
  1. `make typecheck`
  2. `make lint`
  3. `make format`
  4. `make test`
- Ensure IR design is consistent with existing IR classes
- Verify all acceptance criteria checked

ACCEPTANCE CRITERIA (must all be checked):
- [ ] Multi-dimensional patterns surveyed (parameters, variables, sets)
- [ ] IR design handles ≥3 indices per symbol
- [ ] Normalization strategy preserves index semantics
- [ ] Derivative computation approach designed
- [ ] Grammar modifications drafted
- [ ] Implementation effort estimated (High priority for Sprint 7)
- [ ] Test cases identified (simple, nested, conditional)
- [ ] Unknowns 1.2, 1.6 verified and updated in KNOWN_UNKNOWNS.md

COMMIT MESSAGE FORMAT:
"Complete Sprint 7 Prep Task 4: Multi-Dimensional Indexing Research

- Designed IR for multi-dimensional symbols
- Created normalization strategy with examples
- Analyzed derivative computation impact
- Drafted grammar modifications
- Verified Unknowns 1.2, 1.6
- Updated PREP_PLAN.md Task 4 to COMPLETE
- Updated CHANGELOG.md"

When finished, commit all changes and push the branch.
```

---

## Task 5: Profile Test Suite Performance

### Prompt

```
On a new branch, complete Task 5 from docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md (lines 625-768): Profile Test Suite Performance.

OBJECTIVES:
1. Profile full test suite to identify slow tests
2. Categorize tests by type and speed
3. Create baseline for Sprint 7 test performance optimization
4. Verify Known Unknowns 2.1, 2.3, 2.4

UNKNOWNS TO VERIFY:
- Unknown 2.1: What is the distribution of test execution times?
- Unknown 2.3: Is PATH solver isolation needed for parallel test execution?
- Unknown 2.4: What is the overhead of pytest-xdist?

DELIVERABLES:
1. Create `docs/planning/EPIC_2/SPRINT_7/TEST_PERFORMANCE_BASELINE.md` with:
   - Full test suite profile (50+ slowest tests)
   - Test categorization by type (unit/integration/e2e/slow)
   - Test categorization by speed (with time distribution)
   - Parallelization blocker analysis
   - Speedup estimates for 4/8 workers
   - Recommended test marking strategy (@pytest.mark.slow, etc.)
   - Implementation plan for Sprint 7

2. Test profiling data files:
   - `test_profile.txt` (pytest --durations=50 output)
   - `test_times_sorted.txt` (sorted test times)

3. Update `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md`:
   - For Unknown 2.1 (lines 560-598):
     * Change status to "✅ Status: VERIFIED"
     * Add "Verification Results" with distribution data, links
   - For Unknown 2.3 (lines 654-693):
     * Change status to "✅ Status: VERIFIED" or "❌ Status: WRONG"
     * Add findings about PATH isolation requirements
   - For Unknown 2.4 (lines 695-735):
     * Change status to "✅ Status: VERIFIED"
     * Add overhead measurement and speedup estimates

4. Update `docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md`:
   - Task 5 status (line 628): "🔵 NOT STARTED" → "✅ COMPLETE"
   - Add "Changes:" section (line 748) with summary
   - Add "Result:" section (line 752) with document links
   - Check off all acceptance criteria (lines 758-764)

5. Update `CHANGELOG.md`:
   - Add entry: "Sprint 7 Prep: Task 5 - Test Suite Performance Profiling - [date]"
   - Summary of findings (slowest tests, speedup potential)
   - Links to TEST_PERFORMANCE_BASELINE.md
   - Unknowns verified

RESEARCH STEPS:
1. Run pytest with profiling: `pytest --durations=50 > test_profile.txt`
2. Extract and sort all test times: `pytest --durations=0 | grep -E "^[0-9]" | sort -rn > test_times_sorted.txt`
3. Categorize slow tests by type (validation, golden files, integration, unit)
4. Calculate time distribution (total time per category, avg time per test)
5. Identify parallelization blockers (file I/O, global state, subprocesses, solver calls)
6. Design test marking strategy (unit/integration/e2e/slow)
7. Estimate speedup for 4 workers and 8 workers
8. Document findings in TEST_PERFORMANCE_BASELINE.md
9. Update KNOWN_UNKNOWNS.md with verification results
10. Update PREP_PLAN.md Task 5 status
11. Update CHANGELOG.md

QUALITY CHECKS:
- ALWAYS run before committing if you write Python code:
  1. `make typecheck`
  2. `make lint`
  3. `make format`
  4. `make test`
- Verify profile data files exist and are readable
- Ensure all acceptance criteria checked

ACCEPTANCE CRITERIA (must all be checked):
- [ ] Full test suite profiled (--durations=50 minimum)
- [ ] Slowest tests identified (top 20 with times)
- [ ] Tests categorized by type (unit/integration/e2e/slow)
- [ ] Parallelization blockers documented
- [ ] Speedup estimates calculated
- [ ] Implementation plan for Sprint 7 created
- [ ] Unknowns 2.1, 2.3, 2.4 verified and updated in KNOWN_UNKNOWNS.md

COMMIT MESSAGE FORMAT:
"Complete Sprint 7 Prep Task 5: Test Suite Performance Profiling

- Profiled test suite ([N] tests, [X]s total)
- Identified [N] slow tests (>[Y]s each)
- Categorized tests by type and speed
- Estimated speedup: [X]x with [N] workers
- Verified Unknowns 2.1, 2.3, 2.4
- Updated PREP_PLAN.md Task 5 to COMPLETE
- Updated CHANGELOG.md"

When finished, commit all changes and push the branch.
```

---

## Task 6: Survey GAMS Syntax Features for Wave 2

### Prompt

```
On a new branch, complete Task 6 from docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md (lines 770-912): Survey GAMS Syntax Features for Wave 2.

PREREQUISITES:
- Task 2 (GAMSLib Failure Analysis) must be complete

OBJECTIVES:
1. Survey GAMS syntax features beyond Sprint 7 scope
2. Plan parser roadmap for Sprint 8+ 
3. Identify dependencies between features
4. Verify Known Unknowns 1.3, 1.9, 1.10

UNKNOWNS TO VERIFY:
- Unknown 1.3: Is 30% GAMSLib parse rate achievable in Sprint 7? (contributes to)
- Unknown 1.9: Should equation attributes (.l, .m) be supported in Sprint 7?
- Unknown 1.10: Should assignments and scalar declarations be supported in Sprint 7?

DELIVERABLES:
1. Create `docs/planning/EPIC_2/PARSER_ROADMAP.md` with:
   - Complete GAMS feature catalog (30-50 features across 5 categories)
   - GAMSLib usage analysis (which models use which features)
   - Feature dependency graph
   - Effort/impact estimates for top 20 features
   - ROI calculation (Impact / Effort) for each feature
   - Recommended roadmap for Sprints 8-10
   - Feature groupings by sprint (Wave 2, Wave 3, Wave 4)

2. Update `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md`:
   - For Unknown 1.3 (lines 344-387):
     * Add additional findings from roadmap analysis
     * Update verification results with roadmap insights
   - For Unknown 1.9 (lines 658-697):
     * Change status to "✅ Status: VERIFIED" or "❌ Status: WRONG"
     * Add decision on equation attributes for Sprint 7
   - For Unknown 1.10 (lines 699-738):
     * Change status to "✅ Status: VERIFIED" or "❌ Status: WRONG"
     * Add decision on assignments/scalars for Sprint 7

3. Update `docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md`:
   - Task 6 status (line 773): "🔵 NOT STARTED" → "✅ COMPLETE"
   - Add "Changes:" section (line 892) with summary
   - Add "Result:" section (line 896) with document links
   - Check off all acceptance criteria (lines 902-908)

4. Update `CHANGELOG.md`:
   - Add entry: "Sprint 7 Prep: Task 6 - GAMS Syntax Feature Survey - [date]"
   - Summary of roadmap (features for Sprints 8-10)
   - Links to PARSER_ROADMAP.md
   - Unknowns verified

RESEARCH STEPS:
1. Catalog GAMS syntax features (sets, parameters, variables, equations, expressions, statements)
2. Cross-reference with GAMSLib failures to identify feature frequency
3. Build dependency graph (which features require others)
4. Estimate effort (Low/Medium/High/Very High) and impact (models unlocked)
5. Calculate ROI for each feature
6. Group features into Sprint 8 (Wave 2), Sprint 9 (Wave 3), Sprint 10 (Wave 4)
7. Document in PARSER_ROADMAP.md
8. Update KNOWN_UNKNOWNS.md with verification results
9. Update PREP_PLAN.md Task 6 status
10. Update CHANGELOG.md

QUALITY CHECKS:
- ALWAYS run before committing if you write Python code:
  1. `make typecheck`
  2. `make lint`
  3. `make format`
  4. `make test`
- Cross-reference roadmap with PROJECT_PLAN.md Sprint 8-10 targets
- Ensure all acceptance criteria checked

ACCEPTANCE CRITERIA (must all be checked):
- [ ] GAMS features cataloged (≥30 features across 5 categories)
- [ ] GAMSLib usage analyzed (feature frequency in failed models)
- [ ] Dependency graph created
- [ ] Effort/impact estimated for top 20 features
- [ ] Roadmap drafted for Sprints 8-10
- [ ] Cross-referenced with PROJECT_PLAN.md targets
- [ ] Unknowns 1.3, 1.9, 1.10 verified and updated in KNOWN_UNKNOWNS.md

COMMIT MESSAGE FORMAT:
"Complete Sprint 7 Prep Task 6: GAMS Syntax Feature Survey

- Cataloged [N] GAMS features across 5 categories
- Created parser roadmap for Sprints 8-10
- Identified [N] Wave 2 features, [N] Wave 3, [N] Wave 4
- Analyzed feature dependencies
- Verified Unknowns 1.3, 1.9, 1.10
- Updated PREP_PLAN.md Task 6 to COMPLETE
- Updated CHANGELOG.md"

When finished, commit all changes and push the branch.
```

---

## Task 7: Design Line Number Tracking for Warnings

### Prompt

```
On a new branch, complete Task 7 from docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md (lines 914-1085): Design Line Number Tracking for Warnings.

OBJECTIVES:
1. Design approach to track line numbers through parser → IR → normalization → convexity pipeline
2. Enable warnings with line number citations
3. Verify Known Unknown 4.1

UNKNOWNS TO VERIFY:
- Unknown 4.1: Can line numbers be tracked through parser → IR → convexity pipeline?

DELIVERABLES:
1. Create `docs/design/line_number_tracking.md` with:
   - Parser metadata extraction (Lark line number support confirmed)
   - IR metadata structure design (Metadata dataclass with line, column, source_file)
   - Normalization metadata preservation strategy
   - Warning formatter updates (show line numbers in output)
   - Edge case handling (generated nodes, multi-line equations, includes)
   - Implementation plan for Sprint 7
   - Example code snippets showing design

2. Update `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md`:
   - For Unknown 4.1 (lines 905-953):
     * Change status to "✅ Status: VERIFIED" or "❌ Status: WRONG"
     * Add "Verification Results" with design approach, examples, links

3. Update `docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md`:
   - Task 7 status (line 917): "🔵 NOT STARTED" → "✅ COMPLETE"
   - Add "Changes:" section (line 1067) with summary
   - Add "Result:" section (line 1071) with document links
   - Check off all acceptance criteria (lines 1077-1083)

4. Update `CHANGELOG.md`:
   - Add entry: "Sprint 7 Prep: Task 7 - Line Number Tracking Design - [date]"
   - Summary of design approach
   - Links to docs/design/line_number_tracking.md
   - Unknown verified

RESEARCH STEPS:
1. Test Lark parser line number support (tree.meta.line, tree.meta.column)
2. Design IR Metadata structure (dataclass with line, column, source_file)
3. Design normalization preservation (ensure metadata passes through transformations)
4. Design convexity detection usage (access eq.meta.line in warnings)
5. Design warning formatter (format with line/column citations)
6. Handle edge cases (generated nodes, multi-line, includes)
7. Document design in line_number_tracking.md
8. Update KNOWN_UNKNOWNS.md with verification results
9. Update PREP_PLAN.md Task 7 status
10. Update CHANGELOG.md

QUALITY CHECKS:
- ALWAYS run before committing if you write Python code:
  1. `make typecheck`
  2. `make lint`
  3. `make format`
  4. `make test`
- Verify design is consistent with existing IR classes
- Ensure all acceptance criteria checked

ACCEPTANCE CRITERIA (must all be checked):
- [ ] Lark parser line number support confirmed
- [ ] IR metadata structure designed
- [ ] Normalization preservation strategy documented
- [ ] Warning formatter updates specified
- [ ] Edge cases identified and solutions proposed
- [ ] Implementation effort estimated (Medium priority for Sprint 7)
- [ ] Unknown 4.1 verified and updated in KNOWN_UNKNOWNS.md

COMMIT MESSAGE FORMAT:
"Complete Sprint 7 Prep Task 7: Line Number Tracking Design

- Designed IR metadata structure for line tracking
- Created normalization preservation strategy
- Specified warning formatter updates
- Identified and solved edge cases
- Verified Unknown 4.1
- Updated PREP_PLAN.md Task 7 to COMPLETE
- Updated CHANGELOG.md"

When finished, commit all changes and push the branch.
```

---

## Task 8: Set Up CI for GAMSLib Regression Tracking

### Prompt

```
On a new branch, complete Task 8 from docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md (lines 1087-1323): Set Up CI for GAMSLib Regression Tracking.

OBJECTIVES:
1. Design CI workflow for automated GAMSLib ingestion
2. Enable automated dashboard updates and parse rate regression detection
3. Verify Known Unknowns 3.2, 3.3, 5.1

UNKNOWNS TO VERIFY:
- Unknown 3.2: Should dashboard updates be auto-committed by CI?
- Unknown 3.3: What parse rate regression threshold should trigger CI failure?
- Unknown 5.1: Should CI run on every PR or only on parser changes?

DELIVERABLES:
1. Create `docs/ci/gamslib_regression_tracking.md` with:
   - CI trigger strategy (when to run, which files to watch)
   - CI job workflow design (steps, timeout handling)
   - Regression detection logic (threshold, baseline comparison)
   - Auto-commit strategy decision (pros/cons of each option)
   - Timeout handling approach (<10min limit)
   - Implementation plan

2. Create `.github/workflows/gamslib-regression.yml` (CI workflow draft):
   - Trigger configuration (PR paths, schedule)
   - Job steps (checkout, setup, run ingestion, check regression)
   - Artifact uploads
   - Failure handling

3. Create `scripts/check_parse_rate_regression.py`:
   - Read current parse rate from JSON report
   - Read baseline from main branch
   - Compare with threshold (>10% drop = fail)
   - Output results

4. Update `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md`:
   - For Unknown 3.2 (lines 858-893):
     * Change status to "✅ Status: VERIFIED"
     * Add decision on auto-commit strategy with rationale
   - For Unknown 3.3 (lines 895-931):
     * Change status to "✅ Status: VERIFIED"
     * Add threshold decision (e.g., >10% drop) with justification
   - For Unknown 5.1 (lines 1359-1407):
     * Change status to "✅ Status: VERIFIED"
     * Add trigger strategy decision with file patterns

5. Update `docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md`:
   - Task 8 status (line 1090): "🔵 NOT STARTED" → "✅ COMPLETE"
   - Add "Changes:" section (line 1303) with summary
   - Add "Result:" section (line 1307) with document links
   - Check off all acceptance criteria (lines 1313-1319)

6. Update `CHANGELOG.md`:
   - Add entry: "Sprint 7 Prep: Task 8 - CI GAMSLib Regression Tracking - [date]"
   - Summary of CI design and decisions
   - Links to docs/ci/gamslib_regression_tracking.md
   - Unknowns verified

RESEARCH STEPS:
1. Design CI trigger strategy (Option A: every PR, B: parser files only, C: scheduled + parser)
2. Design CI job workflow (YAML structure, steps, timeouts)
3. Design regression detection script (Python, read JSON, compare, threshold)
4. Evaluate auto-commit options (A: auto-commit, B: fail if not committed, C: post comment)
5. Handle timeout (cache GAMSLib, limit to top models, parallelize)
6. Document design in gamslib_regression_tracking.md
7. Create .github/workflows/gamslib-regression.yml draft
8. Create scripts/check_parse_rate_regression.py
9. Update KNOWN_UNKNOWNS.md with verification results
10. Update PREP_PLAN.md Task 8 status
11. Update CHANGELOG.md

QUALITY CHECKS:
- ALWAYS run before committing if you write Python code:
  1. `make typecheck`
  2. `make lint`
  3. `make format`
  4. `make test`
- Validate YAML syntax for workflow file
- Test regression script locally if possible
- Ensure all acceptance criteria checked

ACCEPTANCE CRITERIA (must all be checked):
- [ ] CI trigger strategy designed (when to run)
- [ ] CI job workflow drafted (.github/workflows)
- [ ] Regression detection script created
- [ ] Threshold defined (>10% drop = fail)
- [ ] Auto-commit strategy decided
- [ ] Timeout handling designed (<10min limit)
- [ ] Implementation effort estimated (Medium priority for Sprint 7)
- [ ] Unknowns 3.2, 3.3, 5.1 verified and updated in KNOWN_UNKNOWNS.md

COMMIT MESSAGE FORMAT:
"Complete Sprint 7 Prep Task 8: CI GAMSLib Regression Tracking

- Designed CI workflow with [trigger strategy]
- Created regression detection script
- Decided on [auto-commit strategy]
- Set regression threshold: [X]% drop
- Verified Unknowns 3.2, 3.3, 5.1
- Updated PREP_PLAN.md Task 8 to COMPLETE
- Updated CHANGELOG.md"

When finished, commit all changes and push the branch.
```

---

## Task 9: Create Parser Test Fixture Strategy

### Prompt

```
On a new branch, complete Task 9 from docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md (lines 1325-1531): Create Parser Test Fixture Strategy.

PREREQUISITES:
- Task 2 (GAMSLib Failure Analysis) must be complete
- Task 3 (Preprocessor Research) must be complete
- Task 4 (Multi-Dimensional Indexing) must be complete

OBJECTIVES:
1. Design test fixture strategy for new parser features
2. Ensure comprehensive coverage without test bloat
3. Use findings from Tasks 2, 3, 4 to identify test requirements

DELIVERABLES:
1. Create `docs/testing/PARSER_FIXTURE_STRATEGY.md` with:
   - Review of existing test fixtures
   - Fixture hierarchy design (tests/fixtures/preprocessor/, multidim/, advanced/)
   - Expected results format (YAML schema)
   - Test case generation approach (parametrized tests with pytest)
   - Fixture documentation template (README.md format)
   - Coverage matrix (features × test types: simple/nested/error)
   - Implementation checklist for Sprint 7

2. Create fixture directory structure (can be placeholder):
   - `tests/fixtures/preprocessor/README.md` (template)
   - `tests/fixtures/multidim/README.md` (template)
   - `tests/fixtures/advanced/README.md` (template)
   - Example `expected.yaml` schema

3. Update `docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md`:
   - Task 9 status (line 1328): "🔵 NOT STARTED" → "✅ COMPLETE"
   - Add "Changes:" section (line 1511) with summary
   - Add "Result:" section (line 1515) with document links
   - Check off all acceptance criteria (lines 1521-1528)

4. Update `CHANGELOG.md`:
   - Add entry: "Sprint 7 Prep: Task 9 - Parser Test Fixture Strategy - [date]"
   - Summary of fixture strategy
   - Links to docs/testing/PARSER_FIXTURE_STRATEGY.md
   - Coverage matrix highlights

RESEARCH STEPS:
1. Review existing fixtures (tests/fixtures/convexity/, tests/golden/, examples/)
2. Design fixture hierarchy based on Tasks 2, 3, 4 findings
3. Design expected results YAML format
4. Design parametrized test approach
5. Create fixture documentation template
6. Build coverage matrix (identify which features need which test types)
7. Create implementation checklist
8. Document strategy in PARSER_FIXTURE_STRATEGY.md
9. Create fixture directory templates
10. Update PREP_PLAN.md Task 9 status
11. Update CHANGELOG.md

QUALITY CHECKS:
- ALWAYS run before committing if you write Python code:
  1. `make typecheck`
  2. `make lint`
  3. `make format`
  4. `make test`
- Ensure fixture strategy aligns with findings from Tasks 2, 3, 4
- Verify all acceptance criteria checked

ACCEPTANCE CRITERIA (must all be checked):
- [ ] Fixture hierarchy designed (3+ directories for Sprint 7)
- [ ] Expected results format specified (YAML schema)
- [ ] Test case generation approach documented (parametrized)
- [ ] Fixture documentation template created
- [ ] Coverage matrix identifies gaps
- [ ] Cross-referenced with Tasks 2, 3, 4 (parser features)
- [ ] Implementation checklist for Sprint 7 created

COMMIT MESSAGE FORMAT:
"Complete Sprint 7 Prep Task 9: Parser Test Fixture Strategy

- Designed fixture hierarchy (preprocessor, multidim, advanced)
- Created expected results YAML schema
- Documented parametrized test approach
- Built coverage matrix with [N] features × [N] test types
- Created implementation checklist
- Updated PREP_PLAN.md Task 9 to COMPLETE
- Updated CHANGELOG.md"

When finished, commit all changes and push the branch.
```

---

## Task 10: Plan Sprint 7 Detailed Schedule

### Prompt

```
On a new branch, complete Task 10 from docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md (lines 1533-1749): Plan Sprint 7 Detailed Schedule.

PREREQUISITES:
- ALL Tasks 1-9 must be complete
- All Known Unknowns should be verified

OBJECTIVES:
1. Create detailed day-by-day Sprint 7 plan
2. Define checkpoints, deliverables, and acceptance criteria
3. Integrate all findings from prep tasks 1-9

DELIVERABLES:
1. Create `docs/planning/EPIC_2/SPRINT_7/PLAN.md` with:
   - Executive summary
   - Sprint 7 goals (4 major goals from prep findings)
   - Day-by-day breakdown (Days 0-10, 11 days total)
   - 5 checkpoints with acceptance criteria:
     * Checkpoint 0 (Day 0): Prep complete
     * Checkpoint 1 (Day 5): Parser enhancements, GAMSLib ≥30%
     * Checkpoint 2 (Day 7): Test suite <60s (fast), <120s (full)
     * Checkpoint 3 (Day 9): All features integrated, CI working
     * Checkpoint 4 (Day 10): Sprint complete, v0.7.0 released
   - Deliverables list for each day
   - Success criteria
   - Risk register with mitigations
   - Effort estimates (6-8h per day)
   - Cross-references to all prep task outputs

2. Update `docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md`:
   - Task 10 status (line 1536): "🔵 NOT STARTED" → "✅ COMPLETE"
   - Add "Changes:" section (line 1729) with summary
   - Add "Result:" section (line 1733) with link to PLAN.md
   - Check off all acceptance criteria (lines 1739-1746)

3. Update `CHANGELOG.md`:
   - Add entry: "Sprint 7 Prep: Task 10 - Detailed Sprint Plan - [date]"
   - Summary of sprint structure (11 days, 5 checkpoints)
   - Links to PLAN.md
   - Highlight critical path and dependencies

PLANNING STEPS:
1. Review all prep task outputs (Tasks 1-9)
2. Consolidate findings from KNOWN_UNKNOWNS.md (all verified unknowns)
3. Review recommendations from:
   - GAMSLIB_FAILURE_ANALYSIS.md (Task 2)
   - preprocessor_directives.md (Task 3)
   - multidimensional_indexing.md (Task 4)
   - TEST_PERFORMANCE_BASELINE.md (Task 5)
   - PARSER_ROADMAP.md (Task 6)
   - line_number_tracking.md (Task 7)
   - gamslib_regression_tracking.md (Task 8)
   - PARSER_FIXTURE_STRATEGY.md (Task 9)
4. Create day-by-day breakdown:
   - Day 0: Pre-sprint setup
   - Days 1-2: Preprocessor directive implementation
   - Days 3-4: Multi-dimensional indexing implementation
   - Day 5: GAMSLib retest (Checkpoint 1)
   - Days 6-7: Test optimization (Checkpoint 2)
   - Days 8-9: Convexity + CI (Checkpoint 3)
   - Day 10: Sprint review (Checkpoint 4)
5. Define acceptance criteria for each day
6. Estimate effort and identify risks
7. Cross-reference with PROJECT_PLAN.md, PRELIMINARY_PLAN.md
8. Document in PLAN.md
9. Update PREP_PLAN.md Task 10 status
10. Update CHANGELOG.md

QUALITY CHECKS:
- ALWAYS run before committing if you write Python code:
  1. `make typecheck`
  2. `make lint`
  3. `make format`
  4. `make test`
- Verify all cross-references to prep task outputs are valid
- Ensure plan aligns with PROJECT_PLAN.md Sprint 7 deliverables
- Confirm all acceptance criteria checked

ACCEPTANCE CRITERIA (must all be checked):
- [ ] PLAN.md created following Sprint 6 format
- [ ] 11 days (Days 0-10) with detailed tasks
- [ ] 5 checkpoints defined with acceptance criteria
- [ ] All 4 Sprint 7 goals addressed (parser, tests, convexity, CI)
- [ ] Effort estimates realistic (6-8h per day)
- [ ] Risk register complete with mitigations
- [ ] Cross-referenced with PROJECT_PLAN.md, PRELIMINARY_PLAN.md, Known Unknowns
- [ ] All prep tasks (1-9) integrated into plan

COMMIT MESSAGE FORMAT:
"Complete Sprint 7 Prep Task 10: Detailed Sprint Plan

- Created 11-day sprint plan (Days 0-10)
- Defined 5 checkpoints with acceptance criteria
- Integrated findings from all prep tasks (1-9)
- Estimated effort: [X]h total ([Y]-[Z]h per day)
- Identified [N] risks with mitigations
- Updated PREP_PLAN.md Task 10 to COMPLETE
- Updated CHANGELOG.md"

When finished, commit all changes and push the branch.
```

---

## Usage Notes

### Executing Tasks in Order

Tasks should generally be executed in order due to dependencies:

1. **Task 1** (Done): Create Known Unknowns List
2. **Task 2**: Analyze GAMSLib Failures (depends on Task 1)
3. **Tasks 3-4**: Can run in parallel after Task 2
4. **Task 5**: Can run in parallel with Tasks 2-4
5. **Task 6**: Depends on Task 2
6. **Task 7**: Can run in parallel with other tasks
7. **Task 8**: Can run in parallel with other tasks
8. **Task 9**: Depends on Tasks 2, 3, 4
9. **Task 10**: Depends on ALL tasks 1-9

### Branch Naming Convention

Use consistent branch names:
- `prep/sprint7-task2-gamslib-analysis`
- `prep/sprint7-task3-preprocessor-research`
- `prep/sprint7-task4-multidim-indexing`
- etc.

### Quality Gate Reminder

ALWAYS run before committing Python code:
```bash
make typecheck
make lint
make format
make test
```

### Cross-References

Each task references specific line numbers in PREP_PLAN.md. If the file is modified, update line numbers in these prompts accordingly.

### Unknown Verification Format

When updating KNOWN_UNKNOWNS.md, use this format:

```markdown
### Verification Results
✅ **Status:** VERIFIED  
**Verified by:** Task N ([Task Name])  
**Date:** YYYY-MM-DD

**Findings:**
- [Key finding 1]
- [Key finding 2]
- [Evidence/data]

**Evidence:**
- Link to [document created]
- Test results: [summary]

**Decision:** [What this means for Sprint 7]
```

Or if wrong:

```markdown
### Verification Results
❌ **Status:** WRONG - Assumption was incorrect  
**Verified by:** Task N ([Task Name])  
**Date:** YYYY-MM-DD

**Findings:**
- [What was wrong]
- [Corrected understanding]

**Corrected Assumption:**
[New assumption based on findings]

**Decision:** [How Sprint 7 plan changes]
```

---

**Created:** 2025-11-14  
**Sprint:** Sprint 7 (Epic 2)  
**Total Tasks:** 9 (Tasks 2-10)  
**Estimated Total Time:** 42-57 hours
