# Sprint 17 Prep Plan

**Sprint:** 17 (Weeks 9-10)  
**Goal:** Translation/Solve Improvements, Final Assessment & Release v1.1.0  
**Created:** 2026-01-28  
**Status:** Planning

---

## Executive Summary

Sprint 17 is the final sprint of Epic 3, focused on addressing remaining translation and solve failures, completing final testing and documentation, and releasing v1.1.0. Building on Sprint 16's solid foundation (30% parse, 43.8% translate, 52.4% solve), this sprint targets the ambitious final goals: 70% parse, 60% translate, 80% solve, and 50% full pipeline success.

### Key Focus Areas
1. **Translation Improvements:** Address the 27 translation failures with focus on domain mismatches and unsupported functions
2. **Solve Improvements:** Analyze and fix remaining solve failures and mismatches
3. **Final Assessment:** Complete test runs with comprehensive comparison reporting
4. **Documentation & Release:** User guides, infrastructure docs, and v1.1.0 release

### Sprint 16 Baseline (Starting Point)
| Metric | Count | Rate | Target for Sprint 17 |
|--------|-------|------|---------------------|
| Parse Success | 48/160 | 30.0% | ≥70% (112 models) |
| Translate Success | 21/48 | 43.8% | ≥60% of parsed |
| Solve Success | 11/21 | 52.4% | ≥80% of translated |
| Full Pipeline | 5/160 | 3.1% | ≥50% (80 models) |

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Unknowns Verified |
|---|------|----------|-----------|--------------|-------------------|
| 1 | Create Sprint 17 Known Unknowns List | P0 | 2h | None | - |
| 2 | Detailed Error Analysis | P0 | 3h | Task 1 | 3.1*, 3.3, 4.1-4.5 |
| 3 | Translation Deep Dive | P1 | 3h | Task 2 | 1.1-1.7 |
| 4 | MCP Compilation Analysis | P1 | 2h | Task 2 | 2.1, 2.4 |
| 5 | Lexer/Parser Improvement Plan | P1 | 2h | Tasks 2, 3 | 3.1, 3.2, 3.4, 3.5* |
| 6 | Solve Failure Investigation Plan | P1 | 2h | Task 2 | 2.2, 2.3, 2.5 |
| 7 | Documentation Inventory | P2 | 1h | None | - |
| 8 | Release Checklist | P2 | 1h | Task 7 | 5.1-5.4 |
| 9 | Plan Sprint 17 Detailed Schedule | P0 | 2h | Tasks 1-8 | 3.5, 3.6 |

*Note: Unknown 3.1 is partially verified by Task 2 (initial extraction) and primarily verified by Task 5 (complete analysis). Unknown 3.5 is partially verified by Task 5 and finalized by Task 9.

**Total Estimated Prep Time:** 18 hours

---

## Prep Tasks

### Task 1: Create Sprint 17 Known Unknowns List

**Status:** COMPLETE  
**Priority:** P0 - Critical  
**Estimated Time:** 2 hours  
**Deadline:** Before Sprint 17 Day 1  
**Owner:** TBD  
**Dependencies:** None

#### Objective
Document all remaining uncertainties and unknowns that could affect Sprint 17 success.

#### Why This Matters
Sprint 17 has ambitious targets (70% parse, 60% translate, 80% solve). Understanding what we don't know helps us plan realistic tasks and allocate contingency time appropriately.

#### Background
Sprint 16 achieved significant improvements but revealed new questions:
- Why do some translated models fail MCP compilation?
- What causes the new `internal_error` cases?
- Which `lexer_invalid_char` subcategories are actually fixable?
- Why did translate rate drop while translate count increased?

See: [SPRINT_RETROSPECTIVE.md](../SPRINT_16/SPRINT_RETROSPECTIVE.md) § "What Could Be Improved"

#### What Needs to Be Done
1. Review Sprint 16 error categories and identify unknowns
2. Document technical uncertainties for each pipeline stage
3. List assumptions that need validation
4. Identify risks and their potential impact
5. Prioritize unknowns by impact on Sprint 17 goals

#### Changes
- Create `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md`

#### Result
A comprehensive list of unknowns categorized by:
- Parse stage uncertainties
- Translation stage uncertainties
- Solve stage uncertainties
- Infrastructure/tooling uncertainties

#### Verification
- [x] All error categories from Sprint 16 reviewed
- [x] Each unknown has estimated impact documented
- [x] Unknowns prioritized for investigation

#### Deliverables
- `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md`

#### Acceptance Criteria
- [x] Document covers all pipeline stages
- [x] Each unknown has clear description and potential impact
- [x] Unknowns linked to specific error categories where applicable
- [x] Task-to-Unknown mapping table created
- [x] 27 unknowns documented (target 22-30)
- [x] Priority distribution: 4 Critical (15%), 8 High (30%), 12 Medium (44%), 3 Low (11%)

---

### Task 2: Detailed Error Analysis

**Status:** COMPLETE  
**Priority:** P0 - Critical  
**Estimated Time:** 3 hours  
**Deadline:** Before Sprint 17 Day 2  
**Owner:** TBD  
**Dependencies:** Task 1  
**Unknowns Verified:** 3.3, 4.1, 4.2, 4.3, 4.4, 4.5  
**Unknowns Partially Verified:** 3.1 (initial extraction; primary verification in Task 5)

#### Objective
Analyze remaining error categories to understand patterns and fix complexity.

#### Why This Matters
Sprint 16 revealed error category shifts. Understanding the exact nature of remaining errors enables targeted fixes rather than trial-and-error approaches.

#### Background
Sprint 16 error distribution:
- `lexer_invalid_char`: 97 models (largest blocker)
- `path_syntax_error`: 8 models (MCP compilation)
- Translation failures: 27 models (various categories)
- Solve mismatches: 10 models

See: [SPRINT_RETROSPECTIVE.md](../SPRINT_16/SPRINT_RETROSPECTIVE.md) § "Priority 1: Continue Lexer/Parser Improvements"

#### What Needs to Be Done
1. Extract sample error messages for each category
2. Identify patterns across models within categories
3. Estimate fix complexity (trivial/moderate/complex)
4. Map errors to specific code locations
5. Document findings in analysis report

#### Changes
- Create `docs/planning/EPIC_3/SPRINT_17/ERROR_ANALYSIS.md`

#### Result
For each error category:
- Representative examples
- Pattern analysis
- Fix complexity estimate
- Recommended approach

#### Verification
- [x] All major error categories analyzed
- [x] Sample errors extracted for each category
- [x] Complexity estimates provided
- [x] Patterns identified and documented
- [x] Unknowns 3.1, 3.3, 4.1, 4.2, 4.3, 4.4, 4.5 verified and updated in KNOWN_UNKNOWNS.md

#### Deliverables
- `docs/planning/EPIC_3/SPRINT_17/ERROR_ANALYSIS.md`
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1, 3.3, 4.1, 4.2, 4.3, 4.4, 4.5

#### Acceptance Criteria
- [x] At least 3 sample errors per major category
- [x] Complexity rated as: trivial (<1h), moderate (1-4h), complex (>4h)
- [x] Clear patterns identified for categories with 5+ models
- [x] Unknowns 3.1, 3.3, 4.1, 4.2, 4.3, 4.4, 4.5 verified and updated in KNOWN_UNKNOWNS.md

---

### Task 3: Translation Deep Dive

**Status:** COMPLETE  
**Priority:** P1 - High  
**Estimated Time:** 3 hours  
**Deadline:** Before Sprint 17 Day 3  
**Owner:** TBD  
**Dependencies:** Task 2  
**Unknowns Verified:** 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7

#### Objective
Categorize and prioritize the 27 translation failures for targeted fixes.

#### Why This Matters
Translation is the middle bottleneck. Fixing translation issues has multiplicative impact: each new model that translates becomes a candidate for solve success.

#### Background
Translation failure categories from Sprint 16:
- `model_domain_mismatch`: 6 models (index domain issues)
- `diff_unsupported_func`: 6 models (missing derivative rules)
- `model_no_objective_def`: 5 models (objective handling)
- Other categories: 10 models

See: [SPRINT_RETROSPECTIVE.md](../SPRINT_16/SPRINT_RETROSPECTIVE.md) § "Priority 3: Address Translation Blockers"

#### What Needs to Be Done
1. Group all 27 translation failures by root cause
2. Identify which require AD changes vs emit changes
3. Prioritize by impact (models affected) and effort
4. Create fix plan with estimated hours per category
5. Identify quick wins (high impact, low effort)

#### Changes
- Create `docs/planning/EPIC_3/SPRINT_17/TRANSLATION_ANALYSIS.md`

#### Result
A prioritized list of translation issues with:
- Root cause analysis
- Code location (AD vs emit)
- Fix complexity
- Expected model impact

#### Verification
- [x] All 27 failures categorized
- [x] Root causes identified
- [x] Fix locations determined (AD/emit/other)
- [x] Priority ranking established
- [x] Unknowns 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7 verified and updated in KNOWN_UNKNOWNS.md

#### Deliverables
- `docs/planning/EPIC_3/SPRINT_17/TRANSLATION_ANALYSIS.md`
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7

#### Acceptance Criteria
- [x] All 27 failures accounted for
- [x] At least top 5 issues have detailed analysis
- [x] Quick wins clearly identified
- [x] Unknowns 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7 verified and updated in KNOWN_UNKNOWNS.md

---

### Task 4: MCP Compilation Analysis

**Status:** COMPLETE  
**Priority:** P1 - High  
**Estimated Time:** 2 hours  
**Deadline:** Before Sprint 17 Day 3  
**Owner:** TBD  
**Dependencies:** Task 2  
**Unknowns Verified:** 2.1, 2.4

#### Objective
Investigate the 8 `path_syntax_error` models to understand MCP compilation failures.

#### Why This Matters
These 8 models successfully translate but fail MCP compilation - they're "almost there." Fixing these path syntax errors directly adds to solve success.

#### Background
Path syntax errors occur when generated MCP code has invalid GAMS syntax. Sprint 16 fixed some patterns but 8 remain.

See: [SPRINT_RETROSPECTIVE.md](../SPRINT_16/SPRINT_RETROSPECTIVE.md) § "Priority 2: Fix Remaining Path Syntax Errors"

#### What Needs to Be Done
1. Generate MCP files for all 8 affected models
2. Compile each manually with GAMS
3. Document exact error locations and messages
4. Identify patterns in emit_gams.py causing issues
5. Propose fixes

#### Changes
- Create `docs/planning/EPIC_3/SPRINT_17/MCP_COMPILATION_ANALYSIS.md`

#### Result
For each of 8 models:
- Generated MCP file location
- Exact GAMS error message
- Line/column of error
- Root cause in emit_gams.py

#### Verification
- [x] All 8 models analyzed
- [x] MCP files generated and saved
- [x] GAMS errors captured
- [x] Root causes in emit_gams.py identified
- [x] Unknown 2.1 verified and updated in KNOWN_UNKNOWNS.md
- [x] Unknown 2.4 deferred to Task 6 and updated in KNOWN_UNKNOWNS.md

#### Deliverables
- `docs/planning/EPIC_3/SPRINT_17/MCP_COMPILATION_ANALYSIS.md`
- Generated MCP files for affected models (if useful for debugging)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknown 2.1 and deferral note for 2.4

#### Acceptance Criteria
- All 8 path_syntax_error models analyzed
- Error patterns documented
- emit_gams.py locations identified
- [x] Unknown 2.1 verified in KNOWN_UNKNOWNS.md
- [x] Unknown 2.4 deferred to Task 6 in KNOWN_UNKNOWNS.md

---

### Task 5: Lexer/Parser Improvement Plan

**Status:** Not Started  
**Priority:** P1 - High  
**Estimated Time:** 2 hours  
**Deadline:** Before Sprint 17 Day 4  
**Owner:** TBD  
**Dependencies:** Tasks 2, 3  
**Unknowns Verified:** 3.1 (primary), 3.2, 3.4  
**Unknowns Partially Verified:** 3.5 (initial assessment; finalized in Task 9)

#### Objective
Create a prioritized plan for addressing remaining `lexer_invalid_char` errors (97 models).

#### Why This Matters
Lexer/parser errors are the largest blocker. Even partial success here significantly increases the model pool available for translation and solve.

#### Background
Sprint 16 made substantial progress on lexer issues. Remaining categories:
- Complex set data syntax (largest subcategory)
- Numeric context in parameter data
- Operator context issues
- Hyphenated identifier patterns (some remain)

See: [SPRINT_RETROSPECTIVE.md](../SPRINT_16/SPRINT_RETROSPECTIVE.md) § "Priority 1: Continue Lexer/Parser Improvements"
See: [PROJECT_PLAN.md](../PROJECT_PLAN.md) § "Sprint 17"

#### What Needs to Be Done
1. Categorize 97 lexer failures by subcategory
2. Estimate fixability of each subcategory
3. Identify patterns that can be addressed with lexer changes
4. Identify patterns requiring deeper parser changes
5. Create prioritized fix plan (targeting +15-25 models)

#### Changes
- Create `docs/planning/EPIC_3/SPRINT_17/LEXER_IMPROVEMENT_PLAN.md`

#### Result
A prioritized plan targeting:
- Quick wins (1-2h fixes, multiple models)
- Medium effort (2-4h fixes, good model count)
- Complex changes (4h+, assessed for ROI)

#### Verification
- [ ] All 97 failures reviewed
- [ ] Subcategories identified with counts
- [ ] Fixability assessed for each
- [ ] Plan targets +15-25 models
- [ ] Unknowns 3.1, 3.2, 3.4, 3.5 verified and updated in KNOWN_UNKNOWNS.md

#### Deliverables
- `docs/planning/EPIC_3/SPRINT_17/LEXER_IMPROVEMENT_PLAN.md`
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1, 3.2, 3.4, 3.5

#### Acceptance Criteria
- All lexer failures categorized
- Clear priority ranking
- Realistic +15-25 model target plan
- [ ] Unknowns 3.1, 3.2, 3.4, 3.5 verified and updated in KNOWN_UNKNOWNS.md

---

### Task 6: Solve Failure Investigation Plan

**Status:** Not Started  
**Priority:** P1 - High  
**Estimated Time:** 2 hours  
**Deadline:** Before Sprint 17 Day 4  
**Owner:** TBD  
**Dependencies:** Task 2  
**Unknowns Verified:** 2.2, 2.3, 2.5

#### Objective
Plan investigation and fixes for solve failures and mismatches.

#### Why This Matters
Sprint 17 targets 80% solve success (currently 52.4%). Understanding solve failures enables targeted improvements to reach this goal.

#### Background
Solve failure categories to investigate:
- PATH solver configuration issues
- Initial point problems
- Scaling/conditioning problems
- Numerical tolerance mismatches
- Actual nlp2mcp bugs

See: [PROJECT_PLAN.md](../PROJECT_PLAN.md) § "Sprint 17 - Solve Improvements"

#### What Needs to Be Done
1. Categorize all solve failures by root cause
2. Identify PATH solver configuration opportunities
3. Assess initial point handling improvements
4. Evaluate tolerance adjustment options
5. Create investigation and fix plan

#### Changes
- Create `docs/planning/EPIC_3/SPRINT_17/SOLVE_INVESTIGATION_PLAN.md`

#### Result
A plan covering:
- Failure categories with counts
- Investigation priorities
- Potential fixes to try
- Expected impact per fix

#### Verification
- [ ] All solve failures categorized
- [ ] Root causes identified
- [ ] Fix options evaluated
- [ ] Impact estimates provided
- [ ] Unknowns 2.2, 2.3, 2.5 verified and updated in KNOWN_UNKNOWNS.md

#### Deliverables
- `docs/planning/EPIC_3/SPRINT_17/SOLVE_INVESTIGATION_PLAN.md`
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.2, 2.3, 2.5

#### Acceptance Criteria
- All 10 solve mismatches analyzed
- Fix options prioritized by impact/effort
- Clear plan for reaching 80% target
- [ ] Unknowns 2.2, 2.3, 2.5 verified and updated in KNOWN_UNKNOWNS.md

---

### Task 7: Documentation Inventory

**Status:** Not Started  
**Priority:** P2 - Medium  
**Estimated Time:** 1 hour  
**Deadline:** Before Sprint 17 Day 5  
**Owner:** TBD  
**Dependencies:** None  
**Unknowns Verified:** -

#### Objective
Inventory existing documentation and identify gaps for v1.1.0 release.

#### Why This Matters
Sprint 17 includes user documentation as a major deliverable. Understanding what exists and what's missing enables efficient documentation work.

#### Background
Sprint 17 documentation deliverables:
- `docs/guides/GAMSLIB_TESTING.md` - User guide for GAMSLIB testing
- Infrastructure documentation updates
- Release notes

See: [PROJECT_PLAN.md](../PROJECT_PLAN.md) § "Sprint 17 - Documentation & Release"

#### What Needs to Be Done
1. List all existing documentation files
2. Assess completeness and accuracy
3. Identify gaps requiring new documentation
4. Prioritize documentation tasks
5. Estimate effort for each doc task

#### Changes
- Create `docs/planning/EPIC_3/SPRINT_17/DOCUMENTATION_PLAN.md`

#### Result
A documentation plan with:
- Existing docs inventory
- Gap analysis
- Prioritized doc tasks
- Effort estimates

#### Verification
- [ ] All docs directories scanned
- [ ] Gaps identified
- [ ] Priority ranking established
- [ ] Effort estimates provided

#### Deliverables
- `docs/planning/EPIC_3/SPRINT_17/DOCUMENTATION_PLAN.md`

#### Acceptance Criteria
- Complete inventory of existing docs
- Clear gap identification
- Actionable documentation task list

---

### Task 8: Release Checklist

**Status:** Not Started  
**Priority:** P2 - Medium  
**Estimated Time:** 1 hour  
**Deadline:** Before Sprint 17 Day 5  
**Owner:** TBD  
**Dependencies:** Task 7  
**Unknowns Verified:** 5.1, 5.2, 5.3, 5.4

#### Objective
Create comprehensive checklist for v1.1.0 release.

#### Why This Matters
Sprint 17 culminates in the v1.1.0 release. A thorough checklist ensures nothing is missed and the release is professional and complete.

#### Background
Release requirements from PROJECT_PLAN.md:
- Update CHANGELOG
- Update version to v1.1.0
- Create release notes
- Tag release
- Ensure all tests passing
- Documentation complete

See: [PROJECT_PLAN.md](../PROJECT_PLAN.md) § "Sprint 17 - Release Preparation"

#### What Needs to Be Done
1. List all release artifacts
2. Define quality gates for release
3. Create step-by-step release process
4. Identify release blockers to monitor
5. Plan release communication

#### Changes
- Create `docs/planning/EPIC_3/SPRINT_17/RELEASE_CHECKLIST.md`

#### Result
A comprehensive checklist covering:
- Pre-release verification steps
- Artifact preparation
- Release execution steps
- Post-release verification

#### Verification
- [ ] All release artifacts listed
- [ ] Quality gates defined
- [ ] Step-by-step process documented
- [ ] Blockers identified
- [ ] Unknowns 5.1, 5.2, 5.3, 5.4 verified and updated in KNOWN_UNKNOWNS.md

#### Deliverables
- `docs/planning/EPIC_3/SPRINT_17/RELEASE_CHECKLIST.md`
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 5.1, 5.2, 5.3, 5.4

#### Acceptance Criteria
- Checklist covers all release aspects
- Quality gates clearly defined
- Process is repeatable
- [ ] Unknowns 5.1, 5.2, 5.3, 5.4 verified and updated in KNOWN_UNKNOWNS.md

---

### Task 9: Plan Sprint 17 Detailed Schedule

**Status:** Not Started  
**Priority:** P0 - Critical  
**Estimated Time:** 2 hours  
**Deadline:** Before Sprint 17 Day 1  
**Owner:** TBD  
**Dependencies:** Tasks 1-8  
**Unknowns Verified:** 3.5 (finalized), 3.6

#### Objective
Create detailed day-by-day schedule for Sprint 17 based on prep findings.

#### Why This Matters
Sprint 17 is ambitious with 26-34 hours of planned work. A detailed schedule ensures efficient execution and proper prioritization.

#### Background
Sprint 17 components from PROJECT_PLAN.md:
- Translation Improvements (~8-10h)
- Solve Improvements (~6-8h)
- Final Assessment (~6-8h)
- Documentation & Release (~6-8h)

See: [PROJECT_PLAN.md](../PROJECT_PLAN.md) § "Sprint 17"

#### What Needs to Be Done
1. Review all prep task findings
2. Prioritize Sprint 17 work based on discoveries
3. Allocate tasks to sprint days
4. Identify dependencies and sequencing
5. Build in contingency for unknowns
6. Create SPRINT_LOG.md template

#### Changes
- Create `docs/planning/EPIC_3/SPRINT_17/SPRINT_LOG.md` (template)

#### Result
A detailed schedule with:
- Day-by-day task allocation
- Clear deliverables per day
- Dependencies mapped
- Contingency buffers

#### Verification
- [ ] All Sprint 17 work items scheduled
- [ ] Dependencies respected
- [ ] Total hours realistic (26-34h)
- [ ] Contingency included
- [ ] Unknowns 3.5, 3.6 verified and updated in KNOWN_UNKNOWNS.md

#### Deliverables
- `docs/planning/EPIC_3/SPRINT_17/SPRINT_LOG.md` (template with day plan)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.5, 3.6

#### Acceptance Criteria
- 10-day schedule complete
- Daily deliverables defined
- Schedule accounts for prep findings
- Release day clearly identified
- [ ] Unknowns 3.5, 3.6 verified and updated in KNOWN_UNKNOWNS.md

---

## Cross-References

### Source Documents
- [PROJECT_PLAN.md](../PROJECT_PLAN.md) - Sprint 17 section (lines 455-576)
- [SPRINT_RETROSPECTIVE.md](../SPRINT_16/SPRINT_RETROSPECTIVE.md) - Recommendations (lines 222-299)
- [SPRINT_LOG.md](../SPRINT_16/SPRINT_LOG.md) - Sprint 16 results
- [SPRINT_BASELINE.md](../../testing/SPRINT_BASELINE.md) - Sprint 16 baseline metrics
- [KNOWN_UNKNOWNS.md](KNOWN_UNKNOWNS.md) - Sprint 17 Known Unknowns

### Related Research
- [GAMSLIB_STATUS.md](../../testing/GAMSLIB_STATUS.md) - Current model status
- [baseline_metrics.json](../../testing/gamslib/baseline_metrics.json) - Quantitative baseline

### Infrastructure
- [scripts/testing/](../../../scripts/testing/) - Test scripts
- [src/reporting/](../../../src/reporting/) - Reporting module

---

## Risk Assessment

### High Risk
- **Ambitious targets:** 70% parse (currently 30%) requires +64 models
- **Lexer complexity:** Some `lexer_invalid_char` patterns may be unfixable without major refactor

### Medium Risk  
- **Translation diversity:** 27 failures across multiple categories may require many small fixes
- **Solve mysteries:** Some solve failures may have unclear root causes

### Low Risk
- **Documentation:** Well-understood deliverable, mainly execution
- **Release process:** Standard process, low complexity

### Mitigation Strategies
1. Start with error analysis to identify quick wins
2. Set intermediate checkpoints to assess progress
3. Be prepared to adjust targets based on prep findings
4. Prioritize high-impact, low-effort fixes

---

## Success Criteria for Prep Phase

### Required Before Sprint Start
- [x] Known Unknowns document complete
- [ ] Error analysis complete
- [ ] Translation failures categorized
- [ ] MCP compilation issues documented
- [ ] Lexer improvement plan ready
- [ ] Solve investigation plan ready
- [ ] Documentation inventory complete
- [ ] Release checklist created
- [ ] Detailed schedule in SPRINT_LOG.md

### Quality Gates
- All prep documents reviewed
- No blocking unknowns without mitigation plan
- Realistic targets based on analysis
- Clear day-by-day execution plan

---

## Notes

### Sprint 16 Lessons Learned
1. Systematic testing with clear metrics works well
2. Error categorization enables targeted fixes
3. Daily progress tracking maintains momentum
4. Rate vs absolute count metrics can diverge - track both
5. Quality gate discipline prevents regressions

### Sprint 17 Focus
1. Translation and solve are highest leverage now
2. Lexer/parser still important but diminishing returns expected
3. Documentation and release are non-negotiable deliverables
4. Final assessment must be comprehensive for Epic 3 closure
