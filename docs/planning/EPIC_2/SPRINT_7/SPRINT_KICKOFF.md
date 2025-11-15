# Sprint 7 Kickoff Summary

**Date:** November 15, 2025  
**Sprint:** Sprint 7 - Parser Enhancements & GAMSLib Expansion  
**Duration:** 11 days (Days 0-10)  
**Target Release:** v0.7.0

---

## Sprint 7 Overview

### Vision
Transform the NLP2MCP parser from 10% GAMSLib support to 30%+ by implementing high-ROI features while achieving <60s test suite performance and enhanced convexity UX.

### Four Primary Goals

| Goal | Baseline | Target | Success Metric |
|------|----------|--------|----------------|
| **1. GAMSLib Parse Rate** | 10% (1/10) | 30% minimum (3/10)<br>40% target (4/10) | `make ingest-gamslib` |
| **2. Fast Test Suite** | 208s | <60s fast suite<br><120s full suite | `pytest -m "not slow" -n 4` |
| **3. Convexity UX** | No line numbers | 100% warnings show location | Manual inspection |
| **4. CI Automation** | Manual updates | Automated regression detection | CI workflow active |

---

## Key Preparation Completed

### Prep Tasks (✅ All 9 Complete)
1. ✅ **Task 1:** Created 25 Known Unknowns (100% verified)
2. ✅ **Task 2:** Analyzed GAMSLib failures - identified 2 critical features
3. ✅ **Task 3:** Designed preprocessor directive handling
4. ✅ **Task 4:** Researched multi-dimensional indexing (already works!)
5. ✅ **Task 5:** Profiled test suite (1.3% tests = 66.7% time)
6. ✅ **Task 6:** Surveyed GAMS syntax for Wave 2
7. ✅ **Task 7:** Designed line number tracking
8. ✅ **Task 8:** Designed GAMSLib regression CI
9. ✅ **Task 9:** Created parser fixture strategy (34 fixtures planned)

### Design Documents Ready
- `docs/research/preprocessor_directives.md` - Mock/skip approach
- `docs/research/multidimensional_indexing.md` - Already supported!
- `docs/research/line_number_tracking.md` - SourceLocation dataclass
- `docs/research/gamslib_regression_tracking.md` - CI automation design
- `docs/testing/PARSER_FIXTURE_STRATEGY.md` - 34 fixtures across 4 categories

---

## Week-by-Week Plan

### Week 1: Parser Enhancements (Days 1-5, Checkpoint 1)
**Focus:** Implement preprocessor directives and set range syntax

- **Day 1:** Preprocessor core functions (extract, expand, strip)
- **Day 2:** Complete preprocessor integration + start set ranges
- **Day 3:** Complete set range syntax (all 4 types)
- **Day 4:** Integration testing + quick wins (multiple scalars, models keyword)
- **Day 5:** GAMSLib retest + create 17 fixtures (**Checkpoint 1:** 30%+ parse rate)

**Goal:** Achieve 30% parse rate (3/10 models minimum, 50% target with quick wins)

### Week 2: Test Performance (Days 6-7, Checkpoint 2)
**Focus:** Enable pytest-xdist and optimize test suite

- **Day 6:** Install pytest-xdist, fix isolation issues, stress test
- **Day 7:** Benchmark workers, mark slow tests, configure CI (**Checkpoint 2:** <60s/<120s)

**Goal:** Achieve fast <60s, full <120s test suite performance

### Week 3: Convexity UX + CI + Release (Days 8-10, Checkpoints 3 & 4)
**Focus:** Line numbers, fixtures, CI automation, release

- **Day 8:** Line number tracking + 8 multidim fixtures
- **Day 9:** GAMSLib regression CI + 9 statement fixtures (**Checkpoint 3:** All features)
- **Day 10:** Final QA, documentation, release (**Checkpoint 4:** v0.7.0)

**Goal:** 100% warnings show line numbers, CI automated, v0.7.0 released

---

## Five Checkpoints

| Checkpoint | Day | Objective | Key Criteria |
|------------|-----|-----------|--------------|
| **0** | Day 0 | Prep Complete | All 9 prep tasks done, 25 unknowns verified |
| **1** | Day 5 | Parser Enhanced | Parse rate ≥30%, 17 fixtures created |
| **2** | Day 7 | Test Optimized | Fast <60s, Full <120s |
| **3** | Day 9 | Features Integrated | 34 fixtures, line numbers, CI active |
| **4** | Day 10 | Sprint Complete | v0.7.0 released, all 4 goals met |

---

## Risk Register (7 Risks Identified - Overall: LOW)

### Critical Risks
1. **Flaky Tests with pytest-xdist** (Medium) - Mitigation: 10-run stress test on Day 6
2. **Preprocessor Edge Cases** (Low) - Mitigation: Mock/skip approach, not full implementation

### High Risks
3. **Test Speedup <2.9x** (Low) - Mitigation: Conservative 72s target acceptable
4. **GAMSLib Parse Rate <30%** (Low) - Mitigation: 2 critical features unlock 3 models

### Medium/Low Risks
5-7. Minor risks with documented mitigations

---

## Effort Estimates

### By Day (All 6-8 hours per day)
- **Days 0-4:** Parser setup and implementation (30.5-40h cumulative)
- **Days 5-7:** GAMSLib testing and performance (48.5-64h cumulative)
- **Days 8-10:** Convexity, CI, and release (66.5-88h cumulative)

**Total:** 66.5-88 hours (matches 11-day × 6-8h/day budget)

### By Feature Area
- Parser Enhancements: 9-12 hours
- Test Performance: 12-16 hours
- Convexity UX: 3-4 hours
- CI Automation: 4-5 hours
- Test Fixtures: 7-8 hours

---

## Development Environment Status

### ✅ Completed (Day 0)
- [x] Python 3.12.8, pip 24.3.1
- [x] pytest-xdist installed (3.8.0)
- [x] All prep tasks verified complete
- [x] All 25 Known Unknowns verified
- [x] All design documents reviewed

### ✅ Fixture Directories Created
```
tests/fixtures/
├── preprocessor/     (9 fixtures - Day 5)
├── sets/             (8 fixtures - Day 5)
├── multidim/         (8 fixtures - Day 8)
└── statements/       (9 fixtures - Day 9)
```

Each directory includes:
- README.md with purpose and coverage
- expected_results.yaml template

---

## Daily Workflow

### Each Day:
1. **Start:** Read day prompt from `PLAN_PROMPTS.md`
2. **During:** Complete tasks, run quality checks frequently
3. **End:**
   - Run final quality checks (typecheck, lint, format, test)
   - Update PLAN.md completion status
   - Check off day in README.md
   - Log progress to CHANGELOG.md
   - Create PR with `gh pr create`
   - Request Copilot review
   - Address review comments
   - Merge when approved

### Quality Checks (Required before commits with code changes):
```bash
make typecheck  # Must pass
make lint       # Must pass
make format     # Apply formatting
make test       # All tests must pass
```

Skip quality checks for documentation-only commits.

---

## Success Indicators

### Checkpoint 1 (Day 5)
- ✅ 30%+ parse rate (3/10 models minimum)
- ✅ circle.gms, maxmin.gms, himmel16.gms parsing
- ✅ 17 parser fixtures created

### Checkpoint 2 (Day 7)
- ✅ Fast test suite <60s
- ✅ Full test suite <120s
- ✅ CI test time <5 minutes

### Checkpoint 3 (Day 9)
- ✅ All 34 fixtures created
- ✅ 100% warnings show line numbers
- ✅ CI automation active

### Checkpoint 4 (Day 10)
- ✅ All 4 sprint goals achieved
- ✅ v0.7.0 released
- ✅ Retrospective complete

---

## Notes for Execution

### From Codex Reviews:
- Day 6 has adequate buffer (3.5-5h) for debugging flaky tests
- Worker count benchmarking moved to Day 7 to reduce Day 6 pressure
- All effort estimates normalized to 6-8h per day
- Checkpoint 2 explicitly requires both <60s fast AND <120s full suite

### Critical Path:
Days 1-5 (Parser enhancements) are the critical path. Days 6-10 can absorb minor delays without affecting release.

### Contingency:
- 0-24% buffer built into estimates
- Quick wins on Day 4 are now REQUIRED to ensure 50% target
- Conservative 72s test suite acceptable if 60s proves challenging

---

## Sprint 7 is Ready to Execute!

All prerequisites met, design documents complete, fixture structure in place.

**Next Step:** Begin Day 1 using `docs/planning/EPIC_2/SPRINT_7/prompts/PLAN_PROMPTS.md`
