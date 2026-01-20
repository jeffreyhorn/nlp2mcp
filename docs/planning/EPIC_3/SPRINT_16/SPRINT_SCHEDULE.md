# Sprint 16 Detailed Schedule

**Created:** January 20, 2026  
**Purpose:** Day-by-day schedule for Sprint 16 execution  
**Related Task:** Sprint 16 Prep Task 10

---

## Executive Summary

Sprint 16 focuses on three priorities: Reporting Infrastructure, Gap Analysis, and Targeted Improvements. This schedule allocates 10 working days across these priorities based on prep task findings.

**Sprint Duration:** 10 days  
**Total Estimated Effort:** 26-34 hours  
**Primary Goal:** Build visibility into pipeline health and improve parse/solve rates

---

## Prep Task Synthesis

### Key Findings from Prep Phase

| Task | Key Finding | Sprint 16 Impact |
|------|-------------|------------------|
| Task 2 | Parse stage is primary bottleneck (78.8% failure) | Focus on parse improvements |
| Task 3 | Jinja2 + tabulate for reporting | 17h implementation estimate |
| Task 4 | Priority Score = Models / Effort | Clear prioritization framework |
| Task 6 | Dollar control already handled; grammar needs data syntax | Target keyword case, hyphenated elements |
| Task 7 | 100% solve failures are emit_gams.py bugs | Fix unary minus, quoting (9-15h) |
| Task 8 | Three-tier regression detection | CI integration ready |
| Task 9 | Defer translation to Sprint 17 | Reduces Sprint 16 scope |

### Unknowns Status

- **Total:** 27 unknowns
- **Verified:** 26 (96%)
- **Remaining:** 1 (9.3 - realistic model count, addressed below)

### Unknown 9.3 Resolution

**Question:** How many models can realistically be unblocked in Sprint 16?

**Answer (based on Task 6 + Task 7 analysis):**

| Priority | Target | Models | Effort | Confidence |
|----------|--------|--------|--------|------------|
| Parse P1 | Keyword case, hyphenated, abort | 15 | 1.5 days | High |
| Parse P2 | Tuple syntax, quoted descriptions | 19 | 2 days | Medium |
| Solve | Unary minus, quoting | 10-14 | 1.5 days | High |

**Sprint 16 Targets:**
- **Minimum:** +16 models parsing (+10% rate), solve 10+ models
- **Target:** +26 models parsing (+16% rate), solve 13+ models  
- **Stretch:** +45 models parsing (+28% rate), solve all 17 translated

---

## Day-by-Day Schedule

### Phase 1: Reporting Infrastructure (Days 1-3)

#### Day 1: Module Setup and Data Loading

| Task | Hours | Deliverable |
|------|-------|-------------|
| Set up `src/nlp2mcp/reporting/` structure | 1 | Module skeleton |
| Implement `data_loader.py` | 2 | Load/validate baseline_metrics.json |
| Implement `StatusAnalyzer` | 2 | Extract status metrics |
| Write unit tests | 1 | Test coverage for data loading |

**Day 1 Checkpoint:**
- [ ] `reporting/` module importable
- [ ] Can load baseline_metrics.json
- [ ] StatusAnalyzer extracts parse/translate/solve rates

#### Day 2: Analyzers and Templates

| Task | Hours | Deliverable |
|------|-------|-------------|
| Implement `FailureAnalyzer` | 2 | Error breakdown by category |
| Implement `ProgressAnalyzer` | 2 | Historical comparison logic |
| Create Jinja2 templates | 2 | status_report.md.j2, failure_report.md.j2 |

**Day 2 Checkpoint:**
- [ ] FailureAnalyzer groups errors correctly
- [ ] Templates render sample data
- [ ] Progress comparison logic works

#### Day 3: CLI and Integration

| Task | Hours | Deliverable |
|------|-------|-------------|
| Implement `MarkdownRenderer` | 1.5 | Render templates to files |
| Implement CLI (`generate_report.py`) | 1.5 | argparse with --format, --output |
| Integration testing | 1.5 | End-to-end report generation |
| Generate first reports | 0.5 | GAMSLIB_STATUS.md, FAILURE_ANALYSIS.md |

**Day 3 Checkpoint:**
- [ ] `python -m nlp2mcp.reporting.generate_report` works
- [ ] GAMSLIB_STATUS.md generated
- [ ] FAILURE_ANALYSIS.md generated
- [ ] All reporting tests pass

---

### Phase 2: Gap Analysis (Days 4-5)

#### Day 4: Parse and Translate Gap Analysis

| Task | Hours | Deliverable |
|------|-------|-------------|
| Generate detailed parse failure report | 1 | Parse error breakdown |
| Analyze lexer error subcategories | 2 | Prioritized fix list |
| Document translation failure patterns | 1 | Translation gap analysis |
| Create IMPROVEMENT_ROADMAP.md | 2 | Prioritized improvement list |

**Day 4 Checkpoint:**
- [ ] Parse failures categorized with fix strategies
- [ ] Translation failures documented (for Sprint 17)
- [ ] IMPROVEMENT_ROADMAP.md with priority scores

#### Day 5: Solve Gap Analysis and Roadmap Finalization

| Task | Hours | Deliverable |
|------|-------|-------------|
| Analyze solve failure patterns in detail | 1.5 | emit_gams.py fix requirements |
| Finalize IMPROVEMENT_ROADMAP.md | 1.5 | Complete priority list |
| Create implementation tickets | 1 | Specific fix tasks defined |
| Review with Phase 3 dependencies | 1 | Handoff to implementation |

**Day 5 Checkpoint:**
- [ ] All gap analysis complete
- [ ] IMPROVEMENT_ROADMAP.md finalized
- [ ] Implementation tasks defined for Days 6-8

---

### Phase 3: Targeted Improvements (Days 6-8)

#### Day 6: Parse Improvements - Priority 1 (Low Effort)

| Task | Hours | Deliverable |
|------|-------|-------------|
| Fix keyword case handling (`Free Variable`) | 2 | Grammar update |
| Fix hyphenated set elements with numbers | 2 | Extend SET_ELEMENT_ID |
| Fix abort statement syntax | 1 | Add abort_stmt rule |
| Run regression tests | 1 | No existing parse regressions |

**Target:** +15 models parsing (9 keyword + 3 hyphenated + 3 abort)

**Day 6 Checkpoint:**
- [ ] Keyword case models parsing
- [ ] Hyphenated element models parsing
- [ ] Abort syntax models parsing
- [ ] All existing tests still pass

#### Day 7: Parse Improvements - Priority 2 (Medium Effort)

| Task | Hours | Deliverable |
|------|-------|-------------|
| Add tuple expansion syntax | 3 | `(a,b).c` support |
| Fix quoted set descriptions | 2 | Inline description handling |
| Test with affected models | 1 | Verify 19 additional models |

**Target:** +19 models parsing (12 tuple + 7 quoted)

**Day 7 Checkpoint:**
- [ ] Tuple expansion models parsing
- [ ] Quoted description models parsing
- [ ] Total parse improvement measured

#### Day 8: Solve Improvements (emit_gams.py Fixes)

| Task | Hours | Deliverable |
|------|-------|-------------|
| Fix unary minus formatting | 3 | `-(expr)` → `(-1)*(expr)` |
| Fix set element quoting | 2 | Consistent quoting in output |
| Fix scalar declaration | 0.5 | Edge case fix |
| Test all translated models | 0.5 | Verify 10-14 additional solves |

**Target:** Solve rate from 17.6% to 76-100%

**Day 8 Checkpoint:**
- [ ] Unary minus models now solve
- [ ] Quoting issues resolved
- [ ] Solve rate significantly improved

---

### Phase 4: Retest and Documentation (Days 9-10)

#### Day 9: Full Pipeline Retest

| Task | Hours | Deliverable |
|------|-------|-------------|
| Run full pipeline on all 160 models | 1 | Updated pipeline_results.json |
| Generate comparison report | 1 | Sprint 15 vs Sprint 16 delta |
| Analyze unexpected results | 2 | Debug any regressions |
| Create new baseline snapshot | 1 | sprint16_20260XXX in progress_history.json |

**Day 9 Checkpoint:**
- [ ] Full pipeline run complete
- [ ] New metrics captured
- [ ] Comparison report generated
- [ ] Any regressions identified and addressed

#### Day 10: Documentation and Retrospective

| Task | Hours | Deliverable |
|------|-------|-------------|
| Update GAMSLIB_STATUS.md | 1 | Current status summary |
| Update SPRINT_BASELINE.md | 1 | Sprint 16 baseline |
| Write Sprint 16 retrospective | 1.5 | What worked, what didn't |
| Plan Sprint 17 prep tasks | 1 | Next sprint priorities |
| Final commit and review | 0.5 | Sprint complete |

**Day 10 Checkpoint:**
- [ ] All documentation updated
- [ ] Retrospective complete
- [ ] Sprint 17 prep tasks identified
- [ ] Sprint 16 officially complete

---

## Dependencies and Critical Path

### Dependency Diagram

```
Day 1-3: Reporting ──────────────────────────────────────────────┐
    │                                                            │
    ▼                                                            ▼
Day 4-5: Gap Analysis ──────► IMPROVEMENT_ROADMAP.md ──────► Day 9: Retest
    │                                                            ▲
    ▼                                                            │
Day 6-8: Improvements ───────────────────────────────────────────┘
```

### Critical Path

1. **Days 1-3:** Reporting Infrastructure (MUST complete before Day 4)
2. **Day 4-5:** Gap Analysis (MUST complete before Day 6)
3. **Days 6-8:** Improvements (parallel tracks possible)
4. **Day 9:** Retest (depends on all improvements complete)
5. **Day 10:** Documentation (depends on retest)

### Parallel Opportunities

- Day 6-7 parse improvements can run in parallel if team splits
- Day 8 solve improvements independent of Day 7 parse work
- Documentation prep can start on Day 9 afternoon

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

| Deliverable | Status | Notes |
|-------------|--------|-------|
| GAMSLIB_STATUS.md (automated) | Required | Generated by reporting infrastructure |
| FAILURE_ANALYSIS.md (automated) | Required | Error breakdown with recommendations |
| IMPROVEMENT_ROADMAP.md | Required | Prioritized improvement list |
| Progress tracking (progress_history.json) | Required | Sprint comparison enabled |
| Regression detection | Required | CI-ready with --fail-on-regression |

### Definition of Done

Sprint 16 is **COMPLETE** when:

1. **Reporting:** `generate_report.py` produces GAMSLIB_STATUS.md and FAILURE_ANALYSIS.md
2. **Gap Analysis:** IMPROVEMENT_ROADMAP.md documents all gaps with priorities
3. **Parse Improvements:** Parse rate ≥31.3% (minimum) with no regressions
4. **Solve Improvements:** Solve rate ≥60% of translated models
5. **Documentation:** All deliverables reviewed and committed
6. **Tests:** All existing tests pass, new tests added for reporting

---

## Risk Mitigation

### Risk 1: Grammar Changes Break Existing Parses

**Probability:** Medium  
**Impact:** High  
**Mitigation:**
- Run full regression test after each grammar change
- Use `%ignore` patterns (lowest risk) where possible
- Keep grammar changes minimal and targeted
- Have rollback plan for each change

### Risk 2: Reporting Infrastructure Takes Longer Than Estimated

**Probability:** Medium  
**Impact:** Medium  
**Mitigation:**
- Day 3 is buffer for integration issues
- Can defer JSON renderer to Sprint 17 if needed
- Minimum viable: Markdown reports only
- Use existing `tabulate` for quick table generation

### Risk 3: emit_gams.py Fixes Have Side Effects

**Probability:** Low  
**Impact:** High  
**Mitigation:**
- Test on all 17 translated models before/after
- Keep hs62 (only full success) as golden test
- Make fixes minimal and focused
- Have comparison tests for objective values

### Risk 4: Improvements Don't Meet Minimum Targets

**Probability:** Low  
**Impact:** Medium  
**Mitigation:**
- Day 6 P1 improvements are high-confidence (+15 models)
- Day 8 solve fixes are well-understood (+10 models)
- Even P1 alone meets minimum parse target
- Focus on high-confidence fixes first

---

## Resource Allocation

### Effort Summary

| Phase | Days | Hours | % of Sprint |
|-------|------|-------|-------------|
| Reporting Infrastructure | 1-3 | 17 | 50% |
| Gap Analysis | 4-5 | 11 | 32% |
| Targeted Improvements | 6-8 | 17.5 | 52% |
| Retest and Documentation | 9-10 | 9 | 26% |
| **Total** | 10 | **54.5** | - |

**Note:** Some overlap expected; actual hours ~30-35.

### Tools and Dependencies

| Tool | Purpose | Status |
|------|---------|--------|
| Jinja2 | Template rendering | Add to pyproject.toml |
| tabulate | Table formatting | Add to pyproject.toml |
| pytest | Test coverage | Already installed |
| GAMS 51.3.0 | Model compilation | Verified |
| PATH 5.2.01 | MCP solving | Verified |

---

## Daily Standup Questions

For each day, answer:

1. **What was completed yesterday?**
2. **What is planned for today?**
3. **Are there any blockers?**
4. **Are we on track for phase checkpoint?**

---

## Appendix: Prep Task Deliverables Reference

| Task | Deliverable | Key Insight |
|------|-------------|-------------|
| 1 | KNOWN_UNKNOWNS.md | 27 unknowns, 26 verified |
| 2 | BASELINE_ANALYSIS.md | Parse bottleneck (78.8% failure) |
| 3 | REPORT_DESIGN.md | Jinja2 + tabulate, 17h estimate |
| 4 | FAILURE_REPORT_SCHEMA.md | Priority = Models / Effort |
| 5 | GRAMMAR_EXTENSION_GUIDE.md | Safe extension patterns |
| 6 | LEXER_ERROR_ANALYSIS.md | Data syntax, not dollar control |
| 7 | PATH_ERROR_ANALYSIS.md | emit_gams.py bugs, 100% fixable |
| 8 | (in REPORT_DESIGN.md) | Progress tracking schema |
| 9 | SPRINT_15_REVIEW.md | 7 learnings, 5 recommendations |
| 10 | SPRINT_SCHEDULE.md | This document |

---

*Schedule created: January 20, 2026*  
*Ready for Sprint 16 Day 1*
