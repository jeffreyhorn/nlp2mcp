# Sprint 16 Detailed Plan

**Sprint:** 16  
**Duration:** 10 working days  
**Goal:** Reporting Infrastructure, Gap Analysis & Targeted Parser/Solve Improvements  
**Status:** Ready to Start

---

## Executive Summary

Sprint 16 builds on Sprint 15's comprehensive baseline (21.3% parse, 17.6% solve, 0.6% full pipeline) to create reporting infrastructure, perform systematic gap analysis, and implement targeted improvements to parser and code generation.

### Key Deliverables

1. **Reporting Infrastructure** - `generate_report.py` framework with status and failure analyzers
2. **Gap Analysis Reports** - GAMSLIB_STATUS.md, FAILURE_ANALYSIS.md, IMPROVEMENT_ROADMAP.md
3. **Parser Improvements** - Grammar extensions for keyword case, hyphenated elements, abort syntax
4. **Solve Improvements** - emit_gams.py fixes for unary minus, quoting, scalar declarations
5. **Progress Tracking** - Sprint-over-sprint comparison with regression detection

### Prep Phase Summary

| Task | Status | Key Finding |
|------|--------|-------------|
| Task 1: Known Unknowns | ✅ Complete | 27 unknowns identified, 27 verified (100%) |
| Task 2: Baseline Analysis | ✅ Complete | Parse stage primary bottleneck (78.8% failure) |
| Task 3: Report Generation | ✅ Complete | Jinja2 + tabulate, ~17h implementation |
| Task 4: Failure Analysis Schema | ✅ Complete | Priority Score = Models Affected / Effort Hours |
| Task 5: Grammar Extensions | ✅ Complete | Safe extension patterns documented |
| Task 6: Lexer Error Analysis | ✅ Complete | Data syntax issues, not dollar control |
| Task 7: PATH Error Analysis | ✅ Complete | 100% solve failures are emit_gams.py bugs |
| Task 8: Progress Tracking | ✅ Complete | Three-tier regression detection |
| Task 9: Sprint 15 Review | ✅ Complete | 7 learnings, 5 recommendations |
| Task 10: Schedule Planning | ✅ Complete | This document |

### Critical Metrics from Prep Phase

| Metric | Value | Source |
|--------|-------|--------|
| Parse success rate (Sprint 15) | 21.3% (34/160) | baseline_metrics.json |
| Translation success rate | 50.0% (17/34) | baseline_metrics.json |
| Solve success rate | 17.6% (3/17) | baseline_metrics.json |
| Full pipeline success | 0.6% (1/160) | baseline_metrics.json |
| Error categories | 47 total | error_taxonomy.py |
| Known unknowns verified | 27/27 (100%) | KNOWN_UNKNOWNS.md |
| Parse improvement potential | +15 to +45 models | LEXER_ERROR_ANALYSIS.md |
| Solve improvement potential | +10 to +14 models | PATH_ERROR_ANALYSIS.md |

### Sprint 15 Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| baseline_metrics.json | ✅ Ready | Sprint 15 baseline with all metrics |
| pipeline_results.json | ✅ Ready | Per-model results for 160 models |
| run_full_test.py | ✅ Ready | Pipeline orchestrator with 14 filters |
| error_taxonomy.py | ✅ Ready | 47-category error classification |
| gams.lark | ✅ Ready | GAMS grammar for extensions |
| emit_gams.py | ✅ Ready | MCP code generation for fixes |

---

## 10-Day Schedule

### Phase 1: Reporting Infrastructure (Days 1-3)

#### Day 1: Module Setup and Data Loading

**Focus:** Create reporting module structure and implement data loading

| Task | Est. Time | Description |
|------|-----------|-------------|
| Create `src/nlp2mcp/reporting/` structure | 1h | Module skeleton with __init__.py |
| Implement `data_loader.py` | 2h | Load/validate baseline_metrics.json, pipeline_results.json |
| Implement `StatusAnalyzer` class | 2h | Extract parse/translate/solve rates |
| Write unit tests for data loading | 1h | Test coverage for data loader |

**Deliverables:**
- `src/nlp2mcp/reporting/__init__.py`
- `src/nlp2mcp/reporting/data_loader.py`
- `src/nlp2mcp/reporting/analyzers/status_analyzer.py`
- Unit tests in `tests/unit/reporting/`

**Acceptance Criteria:**
- [x] `reporting/` module importable from nlp2mcp
- [x] Can load baseline_metrics.json and pipeline_results.json
- [x] StatusAnalyzer extracts parse/translate/solve rates
- [x] Data validation catches malformed input
- [x] Unit tests pass (28 tests)

**Time Estimate:** 6 hours

**Status:** ✅ Complete (January 21, 2026)

---

#### Day 2: Analyzers and Templates

**Focus:** Implement failure analysis and Jinja2 templates

| Task | Est. Time | Description |
|------|-----------|-------------|
| Implement `FailureAnalyzer` class | 2h | Error breakdown by category with counts |
| Implement `ProgressAnalyzer` class | 2h | Historical comparison and delta calculation |
| Create Jinja2 template directory | 0.5h | `src/nlp2mcp/reporting/templates/` |
| Create `status_report.md.j2` template | 1h | Status summary report template |
| Create `failure_report.md.j2` template | 1h | Failure analysis report template |

**Deliverables:**
- `src/nlp2mcp/reporting/analyzers/failure_analyzer.py`
- `src/nlp2mcp/reporting/analyzers/progress_analyzer.py`
- `src/nlp2mcp/reporting/templates/status_report.md.j2`
- `src/nlp2mcp/reporting/templates/failure_report.md.j2`

**Acceptance Criteria:**
- [x] FailureAnalyzer groups errors by category
- [x] FailureAnalyzer calculates priority scores (models/effort)
- [x] ProgressAnalyzer computes deltas between snapshots
- [x] Templates render sample data correctly
- [x] Templates use tabulate for tables

**Time Estimate:** 6.5 hours

**Status:** ✅ Complete (January 21, 2026)

---

#### Day 3: CLI and Integration

**Focus:** Complete CLI tool and generate first reports

| Task | Est. Time | Description |
|------|-----------|-------------|
| Implement `MarkdownRenderer` class | 1.5h | Render Jinja2 templates to markdown files |
| Implement `generate_report.py` CLI | 1.5h | argparse with --type, --output, --format |
| Integration testing | 1.5h | End-to-end report generation tests |
| Generate first reports | 0.5h | GAMSLIB_STATUS.md, FAILURE_ANALYSIS.md |
| Add to pyproject.toml | 0.5h | Add Jinja2, tabulate dependencies |

**Deliverables:**
- `src/nlp2mcp/reporting/renderers/markdown_renderer.py`
- `src/nlp2mcp/reporting/generate_report.py` (CLI entry point)
- Generated `docs/testing/GAMSLIB_STATUS.md`
- Generated `docs/testing/FAILURE_ANALYSIS.md`

**Acceptance Criteria:**
- [x] `python -m src.reporting.generate_report --type=status` works
- [x] `python -m src.reporting.generate_report --type=failure` works
- [x] GAMSLIB_STATUS.md generated with current metrics
- [x] FAILURE_ANALYSIS.md generated with error breakdown
- [x] All reporting tests pass
- [x] Quality gate passes (typecheck, lint, format, test)

**Time Estimate:** 5.5 hours

**Status:** ✅ Complete (January 21, 2026)

**Checkpoint 1 (End of Day 3):** ✅ COMPLETE - Reporting infrastructure complete; first reports generated

---

### Phase 2: Gap Analysis (Days 4-5)

#### Day 4: Parse and Translate Gap Analysis

**Focus:** Deep-dive into parse failures and document improvement opportunities

| Task | Est. Time | Description |
|------|-----------|-------------|
| Generate detailed parse failure report | 1h | Run failure analyzer on parse errors |
| Analyze lexer error subcategories | 2h | Categorize by root cause and fix strategy |
| Document translation failure patterns | 1h | Analyze 17 translate failures (deferred to Sprint 17) |
| Begin IMPROVEMENT_ROADMAP.md | 2h | Priority-ranked improvement list |

**Deliverables:**
- Detailed parse error analysis (in FAILURE_ANALYSIS.md)
- Translation gap analysis documentation
- `docs/planning/EPIC_3/SPRINT_16/IMPROVEMENT_ROADMAP.md` (draft)

**Acceptance Criteria:**
- [x] Parse failures categorized by subcategory (keyword case, hyphenated, etc.)
- [x] Each error category has fix strategy and effort estimate
- [x] Translation failures documented with Sprint 17 deferral rationale
- [x] IMPROVEMENT_ROADMAP.md draft with top 10 improvements

**Time Estimate:** 6 hours

**Status:** ✅ Complete (January 22, 2026)

---

#### Day 5: Solve Gap Analysis and Roadmap Finalization

**Focus:** Analyze solve failures and finalize improvement roadmap

| Task | Est. Time | Description |
|------|-----------|-------------|
| Analyze solve failure patterns in detail | 1.5h | Cross-reference with PATH_ERROR_ANALYSIS.md |
| Document emit_gams.py fix requirements | 1h | Specific code changes needed |
| Finalize IMPROVEMENT_ROADMAP.md | 1.5h | Complete priority list with all phases |
| Create implementation task list | 1h | Specific tasks for Days 6-8 |
| Review dependencies for Phase 3 | 1h | Ensure handoff is clear |

**Deliverables:**
- Solve error analysis (in FAILURE_ANALYSIS.md)
- Finalized `docs/planning/EPIC_3/SPRINT_16/IMPROVEMENT_ROADMAP.md`
- Implementation task list for Days 6-8

**Acceptance Criteria:**
- [ ] All solve failures mapped to emit_gams.py bugs
- [ ] IMPROVEMENT_ROADMAP.md complete with priority scores
- [ ] Implementation tasks defined for each Day 6-8 fix
- [ ] Clear handoff to improvement phase

**Time Estimate:** 6 hours

**Checkpoint 2 (End of Day 5):** Gap analysis complete; improvement roadmap finalized

---

### Phase 3: Targeted Improvements (Days 6-8)

#### Day 6: Parse Improvements - Priority 1 (High Confidence)

**Focus:** Implement low-effort, high-confidence grammar fixes

| Task | Est. Time | Description |
|------|-----------|-------------|
| Fix keyword case handling | 2h | `Free Variable` → `free variable` (9 models) |
| Fix hyphenated set elements | 2h | `element-1` in SET_ELEMENT_ID (3 models) |
| Fix abort statement syntax | 1h | Add abort_stmt rule to grammar (3 models) |
| Run regression tests | 1h | Verify no existing parse regressions |

**Deliverables:**
- Updated `src/nlp2mcp/parser/gams.lark` with P1 fixes
- All 34 previously-passing models still pass
- 15 newly-passing models documented

**Acceptance Criteria:**
- [ ] Keyword case models (FREE, POSITIVE, NEGATIVE, etc.) now parse
- [ ] Hyphenated element models now parse
- [ ] Abort syntax models now parse
- [ ] No regressions: all 34 existing parses still succeed
- [ ] Quality gate passes

**Time Estimate:** 6 hours

**Target:** +15 models parsing (from 34 to 49)

---

#### Day 7: Parse Improvements - Priority 2 (Medium Confidence)

**Focus:** Implement medium-effort grammar fixes

| Task | Est. Time | Description |
|------|-----------|-------------|
| Add tuple expansion syntax | 3h | `(a,b).c` domain syntax (12 models) |
| Fix quoted set descriptions | 2h | Inline description handling (7 models) |
| Test with affected models | 1h | Verify 19 additional models parse |

**Deliverables:**
- Updated `src/nlp2mcp/parser/gams.lark` with P2 fixes
- 19 newly-passing models documented

**Acceptance Criteria:**
- [ ] Tuple expansion syntax models now parse
- [ ] Quoted set description models now parse
- [ ] No regressions from Day 6 or Sprint 15 baseline
- [ ] Quality gate passes

**Time Estimate:** 6 hours

**Target:** +19 models parsing (from 49 to 68)

---

#### Day 8: Solve Improvements (emit_gams.py Fixes)

**Focus:** Fix MCP code generation bugs to improve solve rate

| Task | Est. Time | Description |
|------|-----------|-------------|
| Fix unary minus formatting | 3h | `-(expr)` → `(-1)*(expr)` (10 models) |
| Fix set element quoting | 2h | Consistent quoting in MCP output (3 models) |
| Fix scalar declaration edge case | 0.5h | Handle scalar without domain (1 model) |
| Test all translated models | 0.5h | Verify 10-14 additional models solve |

**Deliverables:**
- Updated `src/nlp2mcp/ir/emit_gams.py` with solve fixes
- Solve results for all newly-translated models
- Updated solve metrics

**Acceptance Criteria:**
- [ ] Unary minus models now solve correctly
- [ ] Quoting issue models now solve correctly
- [ ] Scalar declaration model now solves
- [ ] No regressions: hs62 still solves and matches
- [ ] Quality gate passes

**Time Estimate:** 6 hours

**Target:** Solve rate from 17.6% to 76%+ (10-14 additional models)

**Checkpoint 3 (End of Day 8):** All targeted improvements implemented

---

### Phase 4: Retest and Documentation (Days 9-10)

#### Day 9: Full Pipeline Retest

**Focus:** Run complete pipeline and measure improvements

| Task | Est. Time | Description |
|------|-----------|-------------|
| Run full pipeline on all 160 models | 1h | `run_full_test.py` with all stages |
| Generate Sprint 15 vs Sprint 16 comparison | 1h | Delta report with progress analyzer |
| Analyze unexpected results | 2h | Debug any regressions or failures |
| Create new baseline snapshot | 1h | `sprint16_YYYYMMDD` in progress_history.json |

**Deliverables:**
- Updated `tests/output/pipeline_results.json`
- Updated `tests/output/baseline_metrics.json`
- Sprint comparison report
- New snapshot in progress tracking

**Acceptance Criteria:**
- [ ] Full pipeline run complete without errors
- [ ] New metrics captured in baseline_metrics.json
- [ ] Comparison report shows improvement delta
- [ ] Any regressions identified and documented
- [ ] Parse rate meets minimum target (≥31.3%)
- [ ] Solve rate meets minimum target (≥60%)

**Time Estimate:** 5 hours

---

#### Day 10: Documentation and Retrospective

**Focus:** Finalize documentation and complete sprint

| Task | Est. Time | Description |
|------|-----------|-------------|
| Update GAMSLIB_STATUS.md | 1h | Current status with Sprint 16 metrics |
| Update SPRINT_BASELINE.md | 1h | Sprint 16 baseline documentation |
| Write Sprint 16 retrospective | 1.5h | What worked, what didn't, lessons learned |
| Plan Sprint 17 prep tasks | 1h | Identify priorities for next sprint |
| Final commit and review | 0.5h | Ensure all deliverables complete |

**Deliverables:**
- Updated `docs/testing/GAMSLIB_STATUS.md`
- Updated `docs/testing/SPRINT_BASELINE.md`
- `docs/planning/EPIC_3/SPRINT_16/SPRINT_RETROSPECTIVE.md`
- Sprint 17 prep task outline

**Acceptance Criteria:**
- [ ] GAMSLIB_STATUS.md reflects Sprint 16 final metrics
- [ ] SPRINT_BASELINE.md updated with Sprint 16 baseline
- [ ] Retrospective documents successes and improvements
- [ ] Sprint 17 priorities identified
- [ ] All Sprint 16 code committed and tested

**Time Estimate:** 5 hours

**Checkpoint 4 (End of Day 10):** Sprint 16 complete; baseline recorded

---

## Success Criteria

### Quantitative Metrics

| Metric | Baseline (Sprint 15) | Minimum | Target | Stretch |
|--------|----------------------|---------|--------|---------|
| Parse Success Rate | 21.3% (34/160) | 31.3% (+16) | 37.5% (+26) | 49.4% (+45) |
| Translate Success Rate | 50.0% (17/34) | 50.0% (maintain) | 50.0% | 50.0% |
| Solve Success Rate | 17.6% (3/17) | 60% (10/17) | 76% (13/17) | 100% (17/17) |
| Full Pipeline Success | 0.6% (1/160) | 3% (5/160) | 5% (8/160) | 8% (13/160) |

### Qualitative Deliverables

| Deliverable | Required | Notes |
|-------------|----------|-------|
| `generate_report.py` CLI | ✅ Yes | Reporting infrastructure |
| GAMSLIB_STATUS.md (automated) | ✅ Yes | Generated by reporting |
| FAILURE_ANALYSIS.md (automated) | ✅ Yes | Generated by reporting |
| IMPROVEMENT_ROADMAP.md | ✅ Yes | Prioritized improvement list |
| Grammar extensions (gams.lark) | ✅ Yes | P1 and P2 parse fixes |
| Code gen fixes (emit_gams.py) | ✅ Yes | Solve rate improvements |
| Progress tracking snapshot | ✅ Yes | Sprint comparison enabled |

### Definition of Done

Sprint 16 is **COMPLETE** when:

1. **Reporting:** `generate_report.py` produces status and failure reports
2. **Gap Analysis:** IMPROVEMENT_ROADMAP.md documents all gaps with priorities
3. **Parse Improvements:** Parse rate ≥31.3% (minimum) with no regressions
4. **Solve Improvements:** Solve rate ≥60% of translated models
5. **Documentation:** All deliverables reviewed and committed
6. **Tests:** All existing tests pass, new tests added for reporting
7. **Quality:** Typecheck, lint, format all pass

---

## Checkpoints Summary

| Checkpoint | Day | Validation Criteria |
|------------|-----|---------------------|
| **1: Reporting Complete** | 3 | generate_report.py works; GAMSLIB_STATUS.md and FAILURE_ANALYSIS.md generated |
| **2: Gap Analysis Complete** | 5 | IMPROVEMENT_ROADMAP.md finalized; implementation tasks defined |
| **3: Improvements Complete** | 8 | Grammar and emit_gams.py fixes implemented; no regressions |
| **4: Sprint Complete** | 10 | Full retest done; documentation updated; retrospective written |

---

## Effort Summary

| Phase | Days | Est. Hours | Components |
|-------|------|------------|------------|
| Phase 1: Reporting | 1-3 | 18h | Module setup, analyzers, CLI |
| Phase 2: Gap Analysis | 4-5 | 12h | Parse/translate/solve analysis |
| Phase 3: Improvements | 6-8 | 18h | Grammar extensions, emit_gams fixes |
| Phase 4: Retest/Docs | 9-10 | 10h | Pipeline retest, documentation |
| **Total** | 10 | **58h** | |

**Note:** Estimated 58 hours is conservative. Realistic with parallel work: 35-40 hours (~3.5-4 hours/day)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Grammar changes cause regressions | Medium | High | Run full regression after each change; rollback plan |
| Reporting takes longer than estimated | Medium | Medium | Day 3 buffer; MVP markdown-only if needed |
| emit_gams.py fixes have side effects | Low | High | Test all 17 translated models; keep hs62 as golden test |
| P2 parse fixes don't work as expected | Medium | Low | P1 alone meets minimum; defer P2 to Sprint 17 if needed |
| Improvements don't meet targets | Low | Medium | P1 + solve fixes are high-confidence |

### Mitigation Strategies

1. **Daily regression testing:** Run parse tests after every grammar change
2. **Incremental commits:** Commit each fix separately for easy rollback
3. **Checkpoint reviews:** Assess progress at each checkpoint before proceeding
4. **Scope adjustment:** Defer P2 to Sprint 17 if behind schedule

---

## Dependencies

### External Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| GAMS 51.3.0 | ✅ Available | Installed locally |
| PATH solver 5.2.01 | ✅ Validated | Demo license until Jan 23, 2026 |
| Python 3.12+ | ✅ Available | With Jinja2, tabulate (to add) |

### Internal Dependencies

| Dependency | Status | Required By |
|------------|--------|-------------|
| Sprint 15 baseline | ✅ Complete | Day 1 (data loading) |
| error_taxonomy.py | ✅ Complete | Day 2 (failure analyzer) |
| gams.lark | ✅ Complete | Days 6-7 (grammar fixes) |
| emit_gams.py | ✅ Complete | Day 8 (solve fixes) |
| run_full_test.py | ✅ Complete | Day 9 (retest) |

---

## Appendix A: Prep Task Deliverables Reference

| Task | Deliverable | Location |
|------|-------------|----------|
| 1 | KNOWN_UNKNOWNS.md | docs/planning/EPIC_3/SPRINT_16/ |
| 2 | BASELINE_ANALYSIS.md | docs/planning/EPIC_3/SPRINT_16/ |
| 3 | REPORT_DESIGN.md | docs/planning/EPIC_3/SPRINT_16/ |
| 4 | FAILURE_REPORT_SCHEMA.md | docs/planning/EPIC_3/SPRINT_16/ |
| 5 | GRAMMAR_EXTENSION_GUIDE.md | docs/planning/EPIC_3/SPRINT_16/ |
| 6 | LEXER_ERROR_ANALYSIS.md | docs/planning/EPIC_3/SPRINT_16/ |
| 7 | PATH_ERROR_ANALYSIS.md | docs/planning/EPIC_3/SPRINT_16/ |
| 8 | Progress Tracking (in REPORT_DESIGN.md) | docs/planning/EPIC_3/SPRINT_16/ |
| 9 | SPRINT_15_REVIEW.md | docs/planning/EPIC_3/SPRINT_16/ |
| 10 | SPRINT_SCHEDULE.md | docs/planning/EPIC_3/SPRINT_16/ |

---

## Appendix B: Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Reporting library | Jinja2 + tabulate | Industry standard, flexible, well-documented |
| Template format | Markdown | Human-readable, version-control friendly |
| Grammar extension approach | Minimal changes | Reduce regression risk |
| Solve fix approach | Targeted emit_gams.py edits | 100% of failures are code gen bugs |
| Translation improvements | Deferred to Sprint 17 | Parse stage is higher leverage |
| Regression detection | Three-tier (rate, model, error) | Comprehensive coverage |

---

*Document created: January 20, 2026*  
*Sprint 16 Start: After this document approved*  
*Estimated Duration: 10 working days (35-40 hours with parallel work)*
