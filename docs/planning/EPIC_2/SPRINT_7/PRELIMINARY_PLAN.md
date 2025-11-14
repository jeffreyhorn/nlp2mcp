# Sprint 7 Preliminary Plan

**Sprint:** Epic 2 - Sprint 7: Parser Enhancements & GAMSLib Expansion  
**Version Target:** v0.7.0  
**Status:** 📋 DRAFT - Preliminary Planning  
**Created:** 2025-11-13 (Sprint 6 Day 10)  
**Based On:** Sprint 6 Retrospective insights and deferred unknowns

---

## Executive Summary

Sprint 7 focuses on addressing the primary bottleneck identified in Sprint 6: **parser limitations that restrict GAMSLib coverage**. The sprint will tackle deferred unknowns from Sprint 6 Known Unknowns (1.6, 1.7, 4.3) plus additional parser features needed to increase GAMSLib parse rate from 10% to 30%+.

**Primary Goal:** Increase GAMSLib parse rate to 30%+ by addressing parser gaps  
**Secondary Goals:** Test performance optimization, CI improvements, convexity refinements

---

## Sprint 6 Learnings Driving Sprint 7

From the Sprint 6 Retrospective:

### What Went Well (Continue)
- ✅ Comprehensive prep week with Known Unknowns analysis
- ✅ Incremental development with daily deliverables
- ✅ Test-driven approach (99.8% pass rate)
- ✅ Strong documentation culture

### What Needs Improvement (Address in Sprint 7)
- ⚠️ **Parser limitations underestimated:** Only 10% GAMSLib parse rate (9/10 models failed on preprocessor directives)
- ⚠️ **Test execution time:** 1217 tests take ~107 seconds (timeout risk)
- ⚠️ **Convexity scope:** Too conservative, needs fine-grained suppression
- ⚠️ **GAMSLib monitoring:** Manual dashboard updates, no regression tracking

---

## Sprint 7 Goals

### Goal 1: Parser Enhancements (Primary Focus)

**Target:** Increase GAMSLib parse rate from 10% (1/10) to 30%+ (≥3/10)

**Key Issues from Sprint 6:**
- 9/10 GAMSLib models failed with `UnexpectedCharacters` on preprocessor directives
- Missing support: `$if`, `$set`, `$include`, multi-dimensional set indexing

**Deliverables:**
1. **Preprocessor directive support** (or lightweight mock handling)
   - `$if`, `$set`, `$include` (most common directives)
   - Goal: Allow parser to skip or handle directives gracefully
   
2. **Multi-dimensional set indexing** (from Known Unknown deferred scope)
   - Support: `Set i, j; Parameter A(i,j);`
   - Required for most real-world GAMS models

3. **Advanced GAMS features** (from Known Unknown deferred scope)
   - Table declarations
   - Tuple syntax
   - Indexed set operations

**Acceptance Criteria:**
- ✅ GAMSLib parse rate ≥30% (≥3/10 Tier 1 models)
- ✅ All 3 feature areas implemented with tests
- ✅ Zero regressions on existing test suite
- ✅ Dashboard updated with new parse results

---

### Goal 2: Test Performance Optimization

**Target:** Reduce test execution time from ~107s to <60s (fast suite) / <120s (full suite)

**Approach:**
1. **Profile slow tests**
   - Identify validation tests with solver calls
   - Mark slow tests: `@pytest.mark.slow`

2. **Test parallelization**
   - Enable `pytest-xdist` for parallel execution
   - Target: 4-8 workers depending on CI environment

3. **CI optimization**
   - Fast tests in PR checks (<60s)
   - Full suite (including slow) on main branch only

**Acceptance Criteria:**
- ✅ Fast test suite completes in <60s
- ✅ Full test suite completes in <120s
- ✅ No flaky tests introduced by parallelization
- ✅ CI configuration updated

---

### Goal 3: Convexity Detection Refinements

**Target:** Reduce false positives and add fine-grained warning suppression

**From Sprint 6 Known Unknowns (deferred):**
- **1.6:** Exit codes for `--strict-convexity` mode (Low priority, consider for Sprint 7)
- **1.7:** Convexity warnings with line numbers (Medium priority, include)
- **4.3:** Per-equation warning suppression (Low priority, consider for Sprint 7)

**Deliverables:**
1. **Line number citations in warnings** (from Unknown 1.7)
   - Warning format: `W301 in equation 'circle_eq' (line 15)`
   - Include expression snippet for context

2. **Fine-grained warning suppression**
   - CLI: `--skip-convexity-codes W301,W303` (suppress specific codes)
   - Alternative to current all-or-nothing `--skip-convexity-check`

3. **Context-aware heuristics** (stretch goal)
   - Check variable bounds/domains before warning
   - Example: `sin(x)` with `x.lo=0, x.up=pi/2` is concave (no warning)

**Acceptance Criteria:**
- ✅ Line numbers included in all convexity warnings
- ✅ Code-specific suppression flag implemented
- ✅ Tests cover suppression behavior
- ✅ Documentation updated (docs/errors/README.md)

---

### Goal 4: GAMSLib CI Integration

**Target:** Automated dashboard updates and parse rate regression detection

**Issues from Sprint 6:**
- Manual `make ingest-gamslib` run required
- Dashboard not auto-updated
- No alerting if parse rate drops

**Deliverables:**
1. **CI job for GAMSLib ingestion**
   - Trigger: Changes to `src/gams/parser.py` or grammar files
   - Output: Updated dashboard and JSON report
   - Duration limit: 5 minutes

2. **Regression detection**
   - Compare parse rate to previous run
   - Fail CI if parse rate drops >10%
   - Store historical parse rates (trend analysis)

3. **Automated dashboard commit**
   - Auto-commit dashboard updates on successful run
   - Or: Fail CI with dashboard diff if changes not committed

**Acceptance Criteria:**
- ✅ CI job runs on parser changes
- ✅ Dashboard auto-updates or CI fails with diff
- ✅ Parse rate regressions detected and block merge
- ✅ Historical trend data tracked

---

## Preliminary Task Breakdown

### Week 1: Parser Enhancements (Days 1-5)

**Day 1: Preprocessor Directives**
- Research approach: Mock handling vs full preprocessing
- Implement `$if`, `$set`, `$include` support
- Add 20+ tests for directive handling
- **Checkpoint 1:** Parser handles preprocessor directives

**Day 2: Multi-Dimensional Set Indexing**
- Implement indexed set declarations
- Support parameter/variable indexing over multiple sets
- Add 30+ tests for multi-dimensional indexing
- **Checkpoint 2:** Multi-dimensional sets work

**Day 3: Advanced GAMS Features**
- Table declarations
- Tuple syntax
- Indexed set operations
- Add 20+ tests for advanced features

**Day 4: GAMSLib Retest & Validation**
- Re-run ingestion on all 10 Tier 1 models
- Target: ≥3 models parse successfully (30%+ rate)
- Debug any new parser issues
- **Checkpoint 3:** GAMSLib parse rate ≥30%

**Day 5: Parser Integration Testing**
- End-to-end tests with new parser features
- Regression testing (ensure 0 regressions)
- Performance benchmarks (ensure <10% slowdown)

---

### Week 2: Optimization & Quality (Days 6-10)

**Day 6: Test Performance Profiling**
- Profile full test suite to identify slow tests
- Mark slow tests with `@pytest.mark.slow`
- Configure pytest-xdist for parallelization
- **Checkpoint 4:** Test suite profiled

**Day 7: Test Parallelization**
- Enable parallel test execution
- Fix any race conditions or flaky tests
- Validate: Fast suite <60s, full suite <120s
- Update CI configuration

**Day 8: Convexity Refinements**
- Add line numbers to convexity warnings
- Implement `--skip-convexity-codes` flag
- Add tests for selective suppression
- Update error documentation

**Day 9: GAMSLib CI Integration**
- Create CI job for automated ingestion
- Implement regression detection logic
- Test auto-commit workflow
- **Checkpoint 5:** CI integration complete

**Day 10: Sprint Review & Release Prep**
- Final testing and QA
- Update documentation (CHANGELOG, README)
- Version bump to v0.7.0
- Sprint retrospective
- Tag release

---

## Estimated Metrics

### Parser Enhancement Targets
| Metric | Sprint 6 | Sprint 7 Target | Change |
|--------|----------|-----------------|--------|
| GAMSLib Parse Rate | 10% (1/10) | 30%+ (≥3/10) | +200% |
| Preprocessor Support | 0% | 80% (basic) | New feature |
| Multi-dim Indexing | 0% | 100% | New feature |

### Test Performance Targets
| Metric | Sprint 6 | Sprint 7 Target | Improvement |
|--------|----------|-----------------|-------------|
| Fast Test Suite | N/A | <60s | New |
| Full Test Suite | ~107s | <120s | -12% time |
| Parallelization | None | 4-8 workers | New |

### Quality Targets
| Metric | Target |
|--------|--------|
| Test Pass Rate | ≥99.8% (maintain Sprint 6 level) |
| Code Coverage | ≥88% (maintain Sprint 6 level) |
| Zero Regressions | ✅ All existing tests pass |
| Performance | <10% slowdown on benchmarks |

---

## Risks & Mitigations

### Risk 1: Parser Complexity Underestimated
**Impact:** High - May not reach 30% parse rate  
**Probability:** Medium  
**Mitigation:**
- Start with Known Unknowns prep task (1 week before sprint)
- Prioritize most impactful features first (preprocessor > indexing > advanced)
- Have fallback: Aim for 20%+ if 30% is too aggressive

### Risk 2: Test Parallelization Introduces Flakiness
**Impact:** Medium - CI unreliable  
**Probability:** Medium  
**Mitigation:**
- Thorough testing of parallel execution locally first
- Use isolation (tmp directories per worker)
- Have fallback: Run slow tests sequentially if needed

### Risk 3: GAMSLib CI Job Too Slow
**Impact:** Low - CI takes too long  
**Probability:** Medium  
**Mitigation:**
- Set 5-minute timeout
- Cache GAMSLib downloads
- Run only on parser-related changes (not all PRs)

### Risk 4: Scope Creep from Convexity Refinements
**Impact:** Low - Minor delay  
**Probability:** Low  
**Mitigation:**
- Timebox convexity work to Day 8 only
- Line numbers are MVP, context-aware heuristics are stretch goal
- Can defer to Sprint 8 if needed

---

## Success Criteria

Sprint 7 is successful if:

1. ✅ **GAMSLib parse rate ≥30%** (≥3/10 models parse)
2. ✅ **Fast test suite <60s** (full suite <120s)
3. ✅ **CI monitors GAMSLib regressions** automatically
4. ✅ **Zero regressions** from Sprint 6
5. ✅ **All quality checks pass** (typecheck, lint, format, test)
6. ✅ **v0.7.0 released** on schedule

**Nice-to-Have (Stretch Goals):**
- GAMSLib parse rate ≥40% (4/10 models)
- Context-aware convexity heuristics implemented
- Historical parse rate trend dashboard

---

## Dependencies on Sprint 6

This plan assumes Sprint 6 deliverables are complete:
- ✅ Convexity detection with 5 warning codes (W301-W305)
- ✅ Error code registry with 17 codes
- ✅ GAMSLib ingestion pipeline (`make ingest-gamslib`)
- ✅ Conversion dashboard infrastructure
- ✅ Test suite at 1217 tests with 99.8% pass rate

---

## Next Steps (Before Sprint 7 Day 1)

### Prep Week Tasks (1 week before sprint)

1. **Known Unknowns Analysis** (4-6 hours)
   - Create `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md`
   - Research preprocessor directive handling approaches
   - Investigate multi-dimensional indexing in GAMS syntax
   - Estimate test parallelization complexity

2. **Parser Gap Analysis** (3-4 hours)
   - Analyze all 9 failed GAMSLib models
   - Categorize failures by missing feature
   - Prioritize features by impact (which unlocks most models)

3. **Test Profiling** (2-3 hours)
   - Run profiler on current test suite
   - Identify top 10 slowest tests
   - Estimate speedup from parallelization

4. **Detailed Schedule** (3-4 hours)
   - Create full `docs/planning/EPIC_2/SPRINT_7/PLAN.md`
   - Define daily tasks and checkpoints
   - Set acceptance criteria for each deliverable

**Total Prep Time:** ~12-17 hours (1.5-2 days)

---

## Open Questions for Sprint 7 Planning

1. **Preprocessor Handling Approach:**
   - Option A: Full preprocessing (more robust, more complex)
   - Option B: Mock/skip directives (faster to implement, less accurate)
   - **Recommendation:** Start with Option B, upgrade to A if needed

2. **Test Parallelization Strategy:**
   - How many workers? (4, 8, or auto-detect?)
   - Which tests should remain sequential? (likely validation tests with solver)
   - **Recommendation:** Start with 4 workers, profile and adjust

3. **GAMSLib CI Trigger:**
   - On every PR? (thorough but slow)
   - Only on parser changes? (faster but might miss issues)
   - **Recommendation:** Parser changes + weekly scheduled run

4. **Version Numbering:**
   - Is v0.7.0 appropriate for parser enhancements?
   - Or minor version: v0.6.1?
   - **Recommendation:** v0.7.0 (parser changes are significant new features)

---

## Notes

This is a **preliminary plan** created during Sprint 6 Day 10. A detailed plan will be created during Sprint 7 prep week with:
- Full Known Unknowns analysis
- Day-by-day task breakdown
- Detailed acceptance criteria for each deliverable
- Test count targets
- Checkpoint definitions

**References:**
- Sprint 6 Retrospective: `docs/planning/EPIC_2/SPRINT_6/RETROSPECTIVE.md`
- Sprint 6 Known Unknowns (deferred items): `docs/planning/EPIC_2/SPRINT_6/KNOWN_UNKNOWNS.md`
- Project Plan: `docs/planning/EPIC_2/PROJECT_PLAN.md`

---

**Created By:** Sprint 6 team  
**Review Status:** Pending review by Full Team  
**Next Review:** Sprint 7 prep week kickoff
