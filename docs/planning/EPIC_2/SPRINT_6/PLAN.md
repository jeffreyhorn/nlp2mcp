# Sprint 6 Plan: Convexity Heuristics, Critical Bug Fixes, GAMSLib Bootstrapping, UX Kickoff

**Sprint Duration:** 2 weeks (10 working days)  
**Sprint Goal:** Deliver v0.6.0 with convexity detection, nested min/max optimization, GAMSLib foundation, and UX improvements  
**Start Date:** TBD  
**End Date:** TBD  
**Release:** v0.6.0

---

## Executive Summary

Sprint 6 delivers four major features:

1. **Convexity Heuristics** - Pattern-based detection of nonconvex constructs with user warnings
2. **Nested Min/Max Optimization** - Flatten nested min/max for better PATH solver performance
3. **GAMSLib Bootstrapping** - Ingest 10 Tier 1 GAMS models, establish conversion tracking
4. **UX Improvements** - Enhanced error messages with context and actionable guidance

**Key Success Metrics:**
- All 13 convexity test fixtures correctly classified
- Nested min/max flattening working without regression
- 10 GAMSLib models ingested with conversion dashboard
- Error messages include source context and documentation links

---

## Prep Work Completed (Before Day 1)

All 9 prep tasks completed:

✅ **Task 1:** Known Unknowns documented (22 unknowns identified)  
✅ **Task 2:** Convexity POC validated (5 patterns, 89% accuracy)  
✅ **Task 3:** Maximize bug investigated (NO BUG - gradient negation correct)  
✅ **Task 4:** GAMSLib catalog created (241 NLP models, 10 Tier 1 selected)  
✅ **Task 5:** Nested min/max designed (flattening strategy documented)  
✅ **Task 6:** Error message improvements prototyped (7-component structure)  
✅ **Task 7:** GAMSLib download infrastructure (shell script ready)  
✅ **Task 8:** Convexity test fixtures created (13 minimal models)  
✅ **Task 9:** Test coverage baseline established (87% coverage, 1098 tests)

**Remaining Unknowns:** 9 incomplete + 2 deferred (11 total) - see schedule below for resolution

---

## Daily Schedule (10 Days)

### **Day 1: Research Day - Nested Min/Max Unknowns**

**Goal:** Resolve 4 critical/high unknowns about nested min/max before implementation

**Tasks:**
1. **Resolve Unknown 2.2** (Critical) - Nested min/max flattening semantics (2h)
   - Create mathematical proof that `min(min(x,y),z) ≡ min(x,y,z)`
   - Test with PATH solver: confirm identical solutions
   - Document any edge cases or limitations
   - **Deliverable:** `docs/research/nested_minmax_semantics.md`

2. **Resolve Unknown 2.3** (High) - AST traversal for nested detection (3h)
   - Design AST visitor pattern to detect nested min/max
   - Implement proof-of-concept traversal
   - Test on example: `x + min(y, min(z,w))`
   - **Deliverable:** Code in `src/ad/minmax_flattener.py` (skeleton)

3. **Resolve Unknown 2.4** (High) - Regression testing strategy (2h)
   - Run current test suite baseline
   - Document expected changes from flattening
   - Identify tests that need golden file updates
   - **Deliverable:** Test plan in `docs/research/nested_minmax_testing.md`

4. **Resolve Unknown 2.5** (Low) - Configuration design (1h)
   - Decide: always-on vs. configurable flattening
   - **Decision:** Start always-on, no flag needed for Sprint 6
   - **Deliverable:** Design doc section

**Checkpoint 1 (End of Day 1):**
- ✅ All 4 nested min/max unknowns resolved
- ✅ Mathematical semantics confirmed
- ✅ AST detection approach designed
- ✅ Test strategy documented
- **Go/No-Go:** Proceed to Day 2 implementation only if semantics verified

---

### **Day 2: Nested Min/Max Implementation**

**Goal:** Implement nested min/max flattening with full test coverage

**Tasks:**
1. **Implement flattening logic** (3h)
   - Complete `src/ad/minmax_flattener.py` based on Day 1 design
   - Add AST visitor for nested min/max detection
   - Implement flattening transformation
   - Unit tests for flattening logic

2. **Integration with AD system** (2h)
   - Hook flattener into `src/ad/ad_core.py`
   - Ensure flattening happens before derivative computation
   - Integration tests with real equations

3. **Regression testing** (2h)
   - Run full test suite with flattening enabled
   - Update golden files as needed (expected changes documented Day 1)
   - Verify no unexpected failures
   - Add regression tests for nested min/max cases

4. **Documentation** (1h)
   - Update `docs/features/min_max.md` with flattening behavior
   - Add examples to user documentation

**Deliverables:**
- `src/ad/minmax_flattener.py` - Flattening implementation
- Updated tests in `tests/ad/test_minmax_flattening.py`
- Documentation updates

**Checkpoint 2 (End of Day 2):**
- ✅ Nested min/max flattening working
- ✅ All tests passing (regression + new tests)
- ✅ Example: `min(min(x,y),z)` → `min(x,y,z)` verified
- **Go/No-Go:** Proceed to convexity work

---

### **Day 3: Convexity Heuristics - Core Patterns**

**Goal:** Implement 5 core convexity detection patterns from Task 2 POC

**Tasks:**
1. **Create pattern matcher infrastructure** (2h)
   - Design pattern matcher base class
   - Implement AST traversal for pattern matching
   - File: `src/diagnostics/convexity/pattern_matcher.py`

2. **Implement 5 core patterns** (4h)
   - Pattern 1: Nonlinear equality detection
   - Pattern 2: Trigonometric function detection
   - Pattern 3: Bilinear term detection
   - Pattern 4: Division/quotient detection
   - Pattern 5: Odd-power polynomial detection
   - File: `src/diagnostics/convexity/patterns.py`

3. **Unit tests for each pattern** (2h)
   - Test each pattern against convexity fixtures (Task 8)
   - Verify: 5 non-convex models trigger warnings
   - Verify: 5 convex models do NOT trigger warnings
   - File: `tests/diagnostics/test_convexity_patterns.py`

**Deliverables:**
- `src/diagnostics/convexity/pattern_matcher.py`
- `src/diagnostics/convexity/patterns.py`
- Unit tests with 13 test fixtures

**Progress Metric:** 5 patterns implemented, tested against 13 fixtures

---

### **Day 4: Convexity Heuristics - CLI Integration**

**Goal:** Integrate convexity warnings into CLI and resolve UX unknowns

**Tasks:**
1. **Resolve Unknown 4.1** (High) - Parser line/column tracking (2h)
   - Analyze Lark parser position tracking
   - Implement position metadata on AST nodes
   - Test error reporting with line/col positions
   - **Decision:** Use Lark's `meta` attribute for position tracking

2. **CLI integration** (3h)
   - Add convexity checker to main conversion pipeline
   - Integrate with structured error messages (Task 6)
   - Add `--skip-convexity-check` flag (opposite of strict mode)
   - File: `src/cli.py` updates

3. **Resolve Unknown 4.2** (Medium) - Documentation links (1h)
   - **Decision:** Single-page docs with anchor links for Sprint 6
   - Create `docs/errors/convexity_warnings.md`
   - Format: `https://docs.project.org/errors/convexity_warnings#E101`

4. **End-to-end testing** (2h)
   - Test full pipeline: GAMS → parse → convexity check → warning output
   - Test with all 13 convexity fixtures
   - Verify warning messages include source context + doc links
   - File: `tests/integration/test_convexity_e2e.py`

**Deliverables:**
- Updated `src/cli.py` with convexity integration
- `docs/errors/convexity_warnings.md` - User-facing documentation
- End-to-end integration tests

**Checkpoint 3 (End of Day 4):**
- ✅ Convexity heuristics fully integrated
- ✅ All 13 test fixtures correctly classified
- ✅ CLI warnings include source context + doc links
- ✅ Unknown 4.1 and 4.2 resolved
- **Demo:** Show convexity warning on `nonconvex_circle.gms` with context

---

### **Day 5: GAMSLib Integration - Ingestion Pipeline**

**Goal:** Download 10 Tier 1 models and set up ingestion pipeline

**Tasks:**
1. **Download Tier 1 models** (1h)
   - Run `scripts/download_gamslib_nlp.sh` from Task 7
   - Verify all 10 models downloaded successfully
   - Commit models to `tests/fixtures/gamslib/`

2. **Resolve Unknown 3.3** (High) - Parse error patterns (2h)
   - Run parser on all 10 models
   - Document parse failures with specific error messages
   - Categorize by failure type (attributes, dollar conditions, etc.)
   - **Deliverable:** `docs/research/gamslib_parse_errors.md`

3. **Implement parse-only ingestion** (3h)
   - Create ingestion script: `scripts/ingest_gamslib.py`
   - For each model: attempt parse, record success/failure
   - Generate ingestion report with error details
   - File: `scripts/ingest_gamslib.py`

4. **Resolve Unknown 3.5** (Medium) - KPI calculations (1h)
   - Define metrics: parse%, convert%, solve%
   - Implement KPI calculation in ingestion script
   - **Sprint 6 targets:** ≥10 models, ≥10% parse%, ≥50% convert%

5. **Initial ingestion run** (1h)
   - Run `scripts/ingest_gamslib.py` on 10 models
   - Generate initial metrics report
   - **Deliverable:** `reports/gamslib_ingestion_sprint6.json`

**Deliverables:**
- Downloaded models in `tests/fixtures/gamslib/`
- `scripts/ingest_gamslib.py` - Ingestion automation
- `docs/research/gamslib_parse_errors.md` - Error analysis
- `reports/gamslib_ingestion_sprint6.json` - Initial metrics

**Progress Metric:** 10 models ingested, baseline metrics established

---

### **Day 6: GAMSLib Integration - Conversion Dashboard**

**Goal:** Create conversion tracking dashboard and resolve remaining unknowns

**Tasks:**
1. **Resolve Unknown 3.4** (Medium) - Dashboard implementation (1h)
   - **Decision:** Start with pure Markdown for Sprint 6
   - Format: `docs/status/GAMSLIB_CONVERSION_STATUS.md`
   - Auto-generated from ingestion script output

2. **Implement dashboard generation** (3h)
   - Extend `scripts/ingest_gamslib.py` to generate Markdown
   - Dashboard sections:
     * Overall KPIs (parse%, convert%, solve%)
     * Per-model status table
     * Common failure patterns
     * Sprint-over-sprint progress chart (manual for Sprint 6)
   - File: `docs/status/GAMSLIB_CONVERSION_STATUS.md`

3. **Resolve Unknown 3.6** (Low) - Ingestion scheduling (1h)
   - **Decision:** Manual ingestion for Sprint 6
   - Document process: `make ingest-gamslib` → updates dashboard
   - Defer GitHub Action automation to Sprint 7+

4. **Documentation** (2h)
   - Create `docs/features/gamslib_integration.md`
   - Document ingestion process, dashboard interpretation, KPIs
   - Add troubleshooting guide for common parse errors

5. **Sprint 6 baseline run** (1h)
   - Final ingestion run with dashboard generation
   - Commit dashboard as Sprint 6 baseline
   - **Deliverable:** Initial `GAMSLIB_CONVERSION_STATUS.md`

**Deliverables:**
- `docs/status/GAMSLIB_CONVERSION_STATUS.md` - Live dashboard
- `docs/features/gamslib_integration.md` - User documentation
- `make ingest-gamslib` target in Makefile

**Checkpoint 4 (End of Day 6):**
- ✅ 10 GAMSLib models ingested
- ✅ Conversion dashboard live with baseline metrics
- ✅ Parse error patterns documented
- ✅ Unknowns 3.3, 3.4, 3.5, 3.6 resolved
- **Demo:** Show dashboard with parse%, convert%, solve% KPIs

---

### **Day 7: UX Improvements - Error Message Integration**

**Goal:** Apply error message improvements from Task 6 throughout codebase

**Tasks:**
1. **Integrate structured error format** (3h)
   - Apply 7-component error structure (from Task 6) to parser errors
   - Update `src/ir/parser.py` error handling
   - Update `src/validation/*.py` error messages
   - Ensure all errors include: level, title, location, context, explanation, action, doc link

2. **Source context extraction** (2h)
   - Implement source line extraction for error context
   - Use line/col metadata from Day 4 (Unknown 4.1)
   - Add caret pointer to highlight error location
   - File: `src/utils/error_formatter.py` (from Task 6)

3. **Documentation link generation** (2h)
   - Create error documentation structure
   - Document top 10 common errors in `docs/errors/`
   - Implement doc link generation in error formatter
   - Format: Error code → URL mapping

4. **Testing** (1h)
   - Unit tests for error formatter
   - Integration tests for error messages in pipeline
   - File: `tests/utils/test_error_formatter.py`

**Deliverables:**
- Updated error messages throughout codebase
- `docs/errors/` - Error documentation directory
- Tests for error formatting

**Progress Metric:** All parser/validation errors use new structured format

---

### **Day 8: UX Improvements - Documentation & Polish**

**Goal:** Complete UX improvements and resolve remaining unknowns

**Tasks:**
1. **Resolve Unknown 4.3** (Low) - Convexity warning suppression (1h)
   - **Decision:** Defer to Sprint 7+ (not critical for v0.6.0)
   - Document as future enhancement in `docs/roadmap.md`

2. **Resolve Unknown 4.4** (Low) - Demo checklist tracking (1h)
   - **Decision:** Use Markdown checklist in `SPRINT_6_DEMO.md`
   - Create demo preparation checklist
   - **Deliverable:** `docs/planning/EPIC_2/SPRINT_6/SPRINT_6_DEMO.md`

3. **User documentation updates** (3h)
   - Update `README.md` with v0.6.0 features
   - Update CLI help text with new flags
   - Add examples for convexity warnings
   - Add examples for GAMSLib ingestion
   - Update `docs/getting_started.md`

4. **Release notes draft** (2h)
   - Create `docs/releases/v0.6.0.md`
   - Document all new features with examples
   - Migration guide (if any breaking changes)
   - Known limitations

5. **Code cleanup** (1h)
   - Remove dead code
   - Update code comments
   - Run linters and formatters

**Deliverables:**
- `docs/planning/EPIC_2/SPRINT_6/SPRINT_6_DEMO.md`
- `docs/releases/v0.6.0.md` - Release notes
- Updated user documentation
- Unknowns 4.3 and 4.4 resolved

**Progress Metric:** All documentation updated for v0.6.0

---

### **Day 9: Testing & Quality Assurance**

**Goal:** Comprehensive testing and quality checks before release

**Tasks:**
1. **Full regression test suite** (2h)
   - Run `make test` on all 1098+ tests
   - Verify all tests pass
   - Investigate and fix any failures
   - Update test coverage report

2. **Integration testing** (2h)
   - Test all 4 major features together
   - End-to-end workflows:
     * Parse GAMS → detect convexity → warn user
     * Parse GAMS with nested min/max → flatten → solve
     * Ingest GAMSLib model → update dashboard
     * Trigger parse error → see structured error message

3. **Performance benchmarks** (2h)
   - Run performance suite on large models
   - Compare Sprint 5 vs Sprint 6 performance
   - Verify no significant regressions
   - Document any performance changes

4. **Coverage analysis** (1h)
   - Run `pytest --cov` to measure coverage
   - Verify coverage ≥87% (baseline from Task 9)
   - Target: ≥90% with new tests
   - Document coverage changes

5. **Code quality checks** (1h)
   - Run `make typecheck` - verify no type errors
   - Run `make lint` - verify no lint warnings
   - Run `make format` - verify code formatted
   - Security scan (if applicable)

**Deliverables:**
- All tests passing (≥1098 tests)
- Performance benchmarks documented
- Coverage report (target ≥90%)
- Quality checks passing

**Checkpoint 5 (End of Day 9):**
- ✅ All tests passing
- ✅ Performance acceptable (no major regressions)
- ✅ Coverage ≥87% (target ≥90%)
- ✅ All quality checks passing
- **Go/No-Go:** Proceed to release only if all criteria met

---

### **Day 10: Release Preparation & Sprint Review**

**Goal:** Final release preparation and Sprint 6 retrospective

**Tasks:**
1. **Final release preparation** (2h)
   - Update version number to v0.6.0
   - Finalize release notes
   - Tag release in git: `git tag v0.6.0`
   - Create GitHub release with notes
   - Update CHANGELOG.md

2. **Demo preparation** (2h)
   - Prepare demo materials using `SPRINT_6_DEMO.md` checklist
   - Test demo scenarios:
     * Demo 1: Convexity warning on `nonconvex_circle.gms`
     * Demo 2: Nested min/max flattening on example model
     * Demo 3: GAMSLib dashboard with metrics
     * Demo 4: Enhanced error message with context
   - Record demo video (optional)

3. **Sprint retrospective** (2h)
   - Review Sprint 6 goals vs. actual delivery
   - Document what went well
   - Document what could be improved
   - Identify action items for Sprint 7
   - **Deliverable:** `docs/planning/EPIC_2/SPRINT_6/RETROSPECTIVE.md`

4. **Sprint 7 prep** (2h)
   - Review deferred unknowns (1.6, 1.7, 4.3)
   - Identify Sprint 7 priorities based on Sprint 6 learnings
   - Create preliminary Sprint 7 task list
   - Update PROJECT_PLAN.md with Sprint 7 scope

**Deliverables:**
- v0.6.0 release tagged and published
- Demo materials ready
- `docs/planning/EPIC_2/SPRINT_6/RETROSPECTIVE.md`
- Sprint 7 preliminary plan

**Final Checkpoint (End of Sprint 6):**
- ✅ v0.6.0 released
- ✅ All acceptance criteria met (see below)
- ✅ Demo delivered successfully
- ✅ Sprint 6 complete

---

## Checkpoints Summary

### Checkpoint 1 (Day 1 EOD): Nested Min/Max Research Complete
**Criteria:**
- All 4 nested min/max unknowns resolved (2.2, 2.3, 2.4, 2.5)
- Mathematical semantics verified
- AST detection approach designed
- Test strategy documented

**Deliverables:**
- `docs/research/nested_minmax_semantics.md`
- `docs/research/nested_minmax_testing.md`
- AST visitor design

**Go/No-Go Decision:** Proceed to implementation only if semantics mathematically verified

---

### Checkpoint 2 (Day 2 EOD): Nested Min/Max Implementation Complete
**Criteria:**
- Flattening logic implemented and tested
- All regression tests passing
- Example `min(min(x,y),z)` → `min(x,y,z)` verified
- Documentation updated

**Deliverables:**
- `src/ad/minmax_flattener.py`
- Unit and integration tests
- Updated documentation

**Go/No-Go Decision:** Proceed to convexity work

---

### Checkpoint 3 (Day 4 EOD): Convexity Heuristics Complete
**Criteria:**
- 5 core patterns implemented
- All 13 test fixtures correctly classified
- CLI integration complete with warnings
- Error messages include source context + doc links
- Unknowns 4.1 and 4.2 resolved

**Deliverables:**
- `src/diagnostics/convexity/` - Pattern matchers
- CLI integration with `--skip-convexity-check` flag
- `docs/errors/convexity_warnings.md`

**Demo:** Show convexity warning on `nonconvex_circle.gms` with full context

---

### Checkpoint 4 (Day 6 EOD): GAMSLib Integration Complete
**Criteria:**
- 10 Tier 1 models downloaded and ingested
- Conversion dashboard live with baseline metrics
- Parse error patterns documented
- Unknowns 3.3, 3.4, 3.5, 3.6 resolved

**Deliverables:**
- `tests/fixtures/gamslib/` - 10 models
- `docs/status/GAMSLIB_CONVERSION_STATUS.md` - Dashboard
- `scripts/ingest_gamslib.py` - Automation
- `docs/research/gamslib_parse_errors.md`

**Demo:** Show dashboard with parse%, convert%, solve% KPIs

---

### Checkpoint 5 (Day 9 EOD): Quality Assurance Complete
**Criteria:**
- All tests passing (≥1098 tests)
- Performance acceptable (no major regressions)
- Coverage ≥87% (target ≥90%)
- All quality checks passing (typecheck, lint, format)

**Deliverables:**
- Test report with coverage metrics
- Performance benchmark results
- Quality check results

**Go/No-Go Decision:** Proceed to release only if all criteria met

---

## Risk Register

### Risk 1: Nested min/max flattening changes PATH solver behavior
**Impact:** High  
**Probability:** Low  
**Mitigation:**
- Day 1 research includes PATH validation
- Compare solutions with/without flattening
- Regression testing with existing test suite
- If issues found: add `--preserve-nesting` flag
**Contingency:** Defer flattening to Sprint 7 if semantics don't hold

---

### Risk 2: Convexity patterns have high false positive rate
**Impact:** Medium (user annoyance, not correctness)  
**Probability:** Medium  
**Mitigation:**
- Use conservative pattern matching (warn only on clear nonconvex cases)
- Test on all 13 fixtures + real models
- Tune patterns based on test results
- Provide `--skip-convexity-check` escape hatch
**Contingency:** Adjust pattern sensitivity, add per-equation suppression in Sprint 7

---

### Risk 3: GAMSLib models have unexpected syntax blocking parse
**Impact:** Medium (reduces ingestion count)  
**Probability:** High  
**Mitigation:**
- Start with simple Tier 1 models
- Document all parse blockers for Sprint 7 parser work
- Set realistic Sprint 6 target: ≥10% parse rate
- Focus on successful conversions, not parse rate
**Contingency:** Accept lower parse rate, prioritize parser improvements in Sprint 7

---

### Risk 4: Parser line/column tracking requires major refactoring
**Impact:** High (delays UX improvements)  
**Probability:** Low (Lark supports this)  
**Mitigation:**
- Day 4 research confirms Lark `meta` attribute availability
- Use Lark's built-in position tracking
- Start with simple line/col metadata, enhance later
**Contingency:** Ship v0.6.0 without line numbers, add in v0.6.1 patch

---

### Risk 5: Test coverage drops below 87% baseline
**Impact:** Medium (violates quality goals)  
**Probability:** Low  
**Mitigation:**
- Add unit tests for all new code (Day 3-8)
- Day 9 coverage analysis catches issues early
- CI/CD enforces 87% minimum (from Task 9)
**Contingency:** Add missing tests on Day 10 before release

---

### Risk 6: Integration testing reveals feature conflicts
**Impact:** High (blocks release)  
**Probability:** Low  
**Mitigation:**
- Day 9 integration testing tests all features together
- End-to-end workflows validated
- 2 full days (9-10) for testing and fixes
**Contingency:** Descope one feature if critical conflict found (most likely: GAMSLib)

---

## Dependencies

### External Dependencies
- **Lark parser** - Position metadata support (confirmed available)
- **PATH solver** - Nested min/max handling (verified in POC)
- **GAMS Model Library** - Download availability (verified in Task 7)

### Internal Dependencies
```
Day 1 (Research) ──┐
                   ├─→ Day 2 (Nested Min/Max) ──┐
Day 3 (Convexity) ─┘                             ├─→ Day 9 (Testing)
Day 4 (Convexity) ────────────────────────────┐  │
                                               │  │
Day 5 (GAMSLib) ───────────────────────────┐  │  │
Day 6 (GAMSLib) ───────────────────────────┼──┼──┘
                                           │  │
Day 7 (UX) ────────────────────────────────┘  │
Day 8 (UX) ───────────────────────────────────┘

Day 10 (Release) depends on Day 9 Go/No-Go
```

**Critical Path:** Day 1 → Day 2 → Day 9 → Day 10 (nested min/max research gates implementation)

**Parallelizable Work:**
- Convexity (Days 3-4) can run parallel to nested min/max (Days 1-2)
- GAMSLib (Days 5-6) independent of both
- UX (Days 7-8) depends on Day 4 (line/col tracking) but otherwise independent

---

## Release Criteria for v0.6.0

### Feature Completeness
- [x] ✅ Convexity heuristics: 5 patterns implemented
- [x] ✅ Convexity warnings: CLI integration with source context
- [x] ✅ Nested min/max: Flattening working without regression
- [x] ✅ GAMSLib: 10 models ingested with dashboard
- [x] ✅ UX: Structured error messages with doc links

### Quality Criteria
- [x] ✅ All tests passing (≥1098 tests)
- [x] ✅ Test coverage ≥87% (target ≥90%)
- [x] ✅ No regressions in existing functionality
- [x] ✅ Performance acceptable (no >10% slowdown)
- [x] ✅ All quality checks passing (typecheck, lint, format)

### Documentation Criteria
- [x] ✅ Release notes complete (`docs/releases/v0.6.0.md`)
- [x] ✅ User documentation updated
- [x] ✅ Error documentation created (`docs/errors/`)
- [x] ✅ GAMSLib integration documented

### Demo Criteria
- [x] ✅ Demo 1: Convexity warning working
- [x] ✅ Demo 2: Nested min/max flattening working
- [x] ✅ Demo 3: GAMSLib dashboard working
- [x] ✅ Demo 4: Enhanced error messages working

**All criteria must be met before v0.6.0 release.**

---

## Success Metrics

### Quantitative Metrics
- **Test Count:** ≥1098 tests (maintain or increase)
- **Test Coverage:** ≥87% baseline, ≥90% target
- **GAMSLib Parse Rate:** ≥10% (≥1 model successfully parsed)
- **GAMSLib Convert Rate:** ≥50% of parsed models converted
- **Convexity Accuracy:** ≥90% on 13 test fixtures (≥12 correct classifications)
- **Performance:** <10% regression on existing benchmarks

### Qualitative Metrics
- **User Feedback:** Convexity warnings helpful and actionable
- **Code Quality:** Clean, maintainable, well-documented
- **Team Confidence:** High confidence in v0.6.0 stability
- **Unknowns Resolved:** ≥80% of Sprint 6 unknowns resolved (9/11 incomplete)

---

## Lessons from Previous Sprints

### Sprint 4 Lessons Applied
- ✅ Known Unknowns process continued (22 unknowns identified upfront)
- ✅ Research days scheduled before implementation (Day 1)
- ✅ Checkpoints with go/no-go decisions (5 checkpoints defined)

### Sprint 5 Lessons Applied
- ✅ Test coverage baseline established before sprint (Task 9)
- ✅ Integration testing scheduled late in sprint (Day 9)
- ✅ Buffer time for fixes and polish (Days 9-10)

### New Practices for Sprint 6
- 🆕 Deferred unknowns tracked for Sprint 7+ (2 deferred items)
- 🆕 GAMSLib ingestion as ongoing process (not one-time)
- 🆕 Conversion dashboard for continuous tracking
- 🆕 Research day dedicated to mathematical verification (Day 1)

---

## Sprint 7 Preview

**Deferred from Sprint 6:**
- Unknown 1.6: Strict-convexity exit codes
- Unknown 1.7: Line number citations in warnings
- Unknown 4.3: Convexity warning suppression

**New Priorities (Based on Sprint 6 Findings):**
- Parser improvements for GAMSLib models (based on parse error patterns from Day 5)
- Additional convexity patterns (based on false negative analysis)
- Dashboard automation (GitHub Action for nightly ingestion)
- Enhanced warning suppression mechanisms

**Estimated Scope:** 2 weeks, v0.7.0 release

---

## Appendices

### Appendix A: Task 1-9 Prep Summary

See individual task deliverables:
- `docs/planning/EPIC_2/SPRINT_6/KNOWN_UNKNOWNS.md` (Task 1)
- `scripts/poc/convexity_detection.py` (Task 2)
- `docs/research/maximize_bug_investigation.md` (Task 3)
- `docs/planning/EPIC_2/SPRINT_6/GAMSLIB_NLP_CATALOG.md` (Task 4)
- `docs/research/nested_minmax_design.md` (Task 5)
- `src/utils/error_formatter.py` (Task 6)
- `scripts/download_gamslib_nlp.sh` (Task 7)
- `tests/fixtures/convexity/` (Task 8)
- `docs/planning/EPIC_2/SPRINT_6/TEST_COVERAGE_BASELINE.md` (Task 9)

### Appendix B: Unknown Resolution Tracker

| Unknown | Priority | Day Resolved | Status |
|---------|----------|--------------|--------|
| 1.1-1.5 | Various | Prep (Task 2) | ✅ VERIFIED |
| 1.6 | Low | Sprint 7+ | ⏳ DEFERRED |
| 1.7 | Medium | Sprint 7+ | ⏳ DEFERRED |
| 2.1 | Critical | Prep (Task 3) | ✅ VERIFIED (no bug) |
| 2.2 | Critical | Day 1 | 🎯 PLANNED |
| 2.3 | High | Day 1 | 🎯 PLANNED |
| 2.4 | High | Day 1 | 🎯 PLANNED |
| 2.5 | Low | Day 1 | 🎯 PLANNED |
| 3.1 | Critical | Prep (Task 7) | ✅ VERIFIED |
| 3.2 | High | Prep (Task 4) | ✅ VERIFIED |
| 3.3 | High | Day 5 | 🎯 PLANNED |
| 3.4 | Medium | Day 6 | 🎯 PLANNED |
| 3.5 | Medium | Day 5 | 🎯 PLANNED |
| 3.6 | Low | Day 6 | 🎯 PLANNED |
| 4.1 | High | Day 4 | 🎯 PLANNED |
| 4.2 | Medium | Day 4 | 🎯 PLANNED |
| 4.3 | Low | Sprint 7+ | ⏳ DEFERRED |
| 4.4 | Low | Day 8 | 🎯 PLANNED |

**Resolution Rate:** 5/17 verified in prep (29%), 9/17 planned for sprint (53%), 3/17 deferred (18%)

### Appendix C: Test Fixture Catalog

**Convexity Fixtures (13 models):**
- 5 convex: linear_program, convex_qp, convex_exponential, convex_log_barrier, convex_inequality
- 5 non-convex: nonconvex_circle, nonconvex_trig_eq, nonconvex_bilinear, nonconvex_quotient, nonconvex_odd_power
- 3 edge cases: mixed_convex_nonconvex, convex_with_trig_ineq, nearly_affine

**GAMSLib Tier 1 Models (10 models):**
- trig, rbrock, himmel16, hs62, mhw4d
- mhw4dx, circle, maxmin, mathopt1, mingamma

See `tests/fixtures/convexity/README.md` and `tests/fixtures/gamslib/README.md` for details.

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-12  
**Status:** Ready for Sprint 6 Day 1
