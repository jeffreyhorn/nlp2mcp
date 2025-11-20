# Sprint 9 Detailed Plan

**Sprint:** Epic 2 - Sprint 9 (Advanced Parser Features & Conversion Pipeline)  
**Duration:** 11 days (Days 0-10, with Day 10 as BUFFER)  
**Start Date:** TBD  
**End Date:** TBD  
**Version:** v0.9.0  
**Date:** 2025-11-20  

---

## Executive Summary

Sprint 9 advances the NLP-to-MCP transformation tool with **advanced indexing features**, **model structure parsing**, and the **first conversion pipeline implementation**. Building on comprehensive prep work (Tasks 1-10, 47-63 hours total), this sprint implements carefully validated features with clear parse rate targets and introduces end-to-end model conversion capability (GAMS NLP → MCP formulation in GAMS syntax).

**Key Achievements from Prep Phase:**
- **27 Known Unknowns identified and verified** across 5 categories (100% verification rate)
- **10 prep tasks completed** with detailed designs and effort validation
- **mhw4dx secondary blocker analyzed** (12-17h effort, deferred to Sprint 10)
- **i++1 indexing design validated** at 8-10h (unlocks himmel16.gms, +10% parse rate)
- **Model sections design complete** at 4-5h (unlocks hs62/mingamma, +20% parse rate)
- **Conversion pipeline architecture** defined (end-to-end NLP → MCP via KKT transformation)
- **Performance framework established** (budgets: <30s fast tests, currently 52s ⚠️)
- **Automated test fixtures designed** (reduces manual fixture writing by 80%)

**Sprint 9 Goals:**

| # | Goal | Baseline | Target | Measurement |
|---|------|----------|--------|-------------|
| 1 | **GAMSLib Parse Rate** | 40% (4/10) | ≥30% baseline (maintain with complexity)<br>50-60% realistic (with i++1 + model sections) | `make ingest-gamslib` |
| 2 | **Advanced Indexing** | Basic i, i+1 | i++1, i--1 arithmetic indexing | himmel16.gms parses ✅ |
| 3 | **Model Structure** | No model sections | Model sections parsed | hs62.gms, mingamma.gms parse ✅ |
| 4 | **Equation Attributes** | No equation attributes | .marginal, .l, .up, .lo parsed | Attribute expressions work |
| 5 | **Conversion Pipeline** | No conversion capability | ≥1 model converts NLP → MCP formulation | mhw4d.gms or rbrock.gms converts to valid MCP GAMS |
| 6 | **Test Performance** | 52.39s fast tests (74% over budget) | <30s fast tests (within budget) | `make test` timing |

**Effort Estimates:**
- **Conservative:** 34h (within 30-41h target ✅)
- **Realistic:** 39h average (mid-range)
- **Upper bound:** 44h (requires Day 10 buffer + scope flexibility)
- **Day 10 is explicitly designated as BUFFER** to absorb overruns without sprint failure

**Parse Rate Projections:**
- **Conservative (30% baseline):** Maintain 40% with added complexity (no regressions)
- **Realistic (50-60%):** i++1 (+10%) + model sections (+20%) = 70% theoretical, 50-60% achievable
- **Optimistic (≥60%):** All features work first try, minimal debugging

**Critical Path:** Test Infrastructure (Day 2) → i++1 Indexing (Day 4) → Model Sections (Day 6) → Conversion Pipeline (Day 8) → Closeout (Day 10)

**Risk Level:** MEDIUM ⚠️  
**Complexity:** HIGH (grammar changes, new pipeline stage, performance optimization)  
**Confidence:** HIGH (comprehensive prep work, validated designs)  
**Recommended Approach:** Front-load test infrastructure (Days 1-2), implement parser features sequentially with checkpoints (Days 3-6), conversion pipeline with validation (Days 7-8), buffer for overruns (Day 10)

**Key Differences from Sprint 8:**
1. **Grammar Complexity:** Sprint 8 had no grammar changes; Sprint 9 has i++1 indexing (grammar modification required)
2. **New Pipeline Stage:** Sprint 9 introduces conversion infrastructure (Sprint 8 was parser-only)
3. **Performance Focus:** Sprint 9 establishes Day 0 performance budgets (Sprint 8 optimized on Day 9)
4. **Test Infrastructure:** Sprint 9 automates fixture generation (Sprint 8 used manual fixtures)
5. **Parse Rate Target:** Sprint 9 targets 50-60% (Sprint 8 achieved 40%)

---

## Table of Contents

1. [Sprint 9 Goals](#sprint-9-goals)
2. [Day-by-Day Breakdown](#day-by-day-breakdown)
3. [Checkpoint Definitions](#checkpoint-definitions)
4. [Effort Allocation](#effort-allocation)
5. [Risk Register](#risk-register)
6. [Quality Gates](#quality-gates)
7. [Deliverables & Acceptance Criteria](#deliverables--acceptance-criteria)
8. [Cross-References](#cross-references)
9. [Appendices](#appendices)

---

## 1. Sprint 9 Goals

### 1.1 Primary Goals

**Goal 1: Maintain Parse Rate with Advanced Features (≥30% baseline)**

- **Current State:** 40% parse rate (4/10 models: mhw4d, rbrock, mathopt1, trig)
- **Challenge:** Advanced features add grammar complexity (potential regressions)
- **Target:** ≥30% baseline (maintain 3/10 models minimum)
- **Success Criteria:**
  - All Sprint 8 passing models still pass (mhw4d, rbrock, mathopt1, trig)
  - No new regressions introduced by grammar changes
  - Parse rate does not drop below 30%

**Goal 2: Implement Advanced Indexing (i++1, i--1)**

- **Current State:** Basic i, i+1 indexing works
- **Gap:** Cannot parse arithmetic indexing (i++1, i--1, i+j, etc.)
- **Target:** i++1 and i--1 indexing working
- **Unlock:** himmel16.gms (+10% parse rate)
- **Effort:** 8-10 hours (validated in Task 3)
- **Success Criteria:**
  - Grammar supports i++1, i--1 patterns
  - Semantic handler creates IndexExpression nodes
  - himmel16.gms parses successfully
  - Test coverage ≥80% for indexing edge cases

**Goal 3: Implement Model Sections**

- **Current State:** Cannot parse model section declarations
- **Gap:** Missing model_statement production in grammar
- **Target:** Model sections parsed and represented in IR
- **Unlock:** hs62.gms, mingamma.gms (+20% parse rate)
- **Effort:** 4-5 hours (validated in Task 4)
- **Success Criteria:**
  - Grammar supports "Model model_name / ..." syntax
  - IR represents ModelDeclaration nodes
  - hs62.gms and mingamma.gms parse successfully
  - Dashboard tracks model section parse statistics

**Goal 4: Implement Equation Attributes**

- **Current State:** Grammar already supports .marginal, .l, .up, .lo (discovered in Task 8)
- **Gap:** Semantic handlers missing, IR representation incomplete
- **Target:** Equation attributes fully functional
- **Effort:** 4.5-5.5 hours (no grammar work needed)
- **Success Criteria:**
  - Semantic handlers create AttributeAccess nodes
  - IR represents .marginal, .l, .up, .lo attributes
  - Attribute expressions in equations parse correctly
  - Test coverage for all 4 attribute types

**Goal 5: Establish Conversion Pipeline Foundation**

- **Current State:** Parser outputs IR, no conversion capability
- **Gap:** No IR → MCP GAMS conversion infrastructure
- **Target:** ≥1 model converts end-to-end (GAMS source → MCP GAMS)
- **Unlock:** End-to-end workflow validation
- **Effort:** 6-8 hours
- **Success Criteria:**
  - Converter class scaffolding complete
  - IR → MCP GAMS mappings for variables, parameters, equations
  - At least 1 model (mhw4d or rbrock) converts successfully
  - MCP GAMS output parses successfully as valid GAMS
  - Conversion validation script working

**Goal 6: Establish Performance Baseline & Budgets**

- **Current State:** 52.39s fast tests (74% over 30s budget)
- **Gap:** No performance budgets established at Day 0
- **Target:** <30s fast tests (within budget)
- **Effort:** 4 hours (framework already designed in Task 9)
- **Success Criteria:**
  - Baseline measurements on Day 0
  - Performance budgets enforced in CI
  - Fast test suite <30s (requires slow test markers)
  - Per-model parse benchmarks established

### 1.2 Secondary Goals

**Secondary Goal 1: Automated Test Fixtures**

- **Benefit:** Reduces manual fixture writing by 80%
- **Effort:** 3 hours
- **Priority:** Medium (quality of life improvement)

**Secondary Goal 2: Fixture Validation Script**

- **Benefit:** Prevents manual fixture errors (Sprint 8 had 3 fixture bugs)
- **Effort:** 2.5 hours
- **Priority:** Medium (reduces debugging time)

**Secondary Goal 3: Secondary Blocker Analysis (mhw4dx)**

- **Finding:** mhw4dx requires 12-17h effort (DEFER to Sprint 10)
- **Sprint 9 Scope:** Document blockers only (2-3h)
- **Priority:** Low (documentation task)

---

## 2. Day-by-Day Breakdown

### Day 0: Sprint Planning & Setup (2-3 hours)

**Objectives:**
1. Review all prep tasks and validate readiness
2. Create sprint branch and baseline all metrics
3. Establish performance budgets and monitoring
4. Verify all unknowns resolved

**Tasks:**

| Task | Effort | Owner | Dependencies |
|------|--------|-------|--------------|
| Review prep tasks 1-10 | 1h | Team | All prep tasks complete |
| Create branch `sprint9-advanced-features` | 15min | Team | - |
| Baseline metrics (parse rate, test performance) | 30min | Team | - |
| Establish performance budgets | 30min | Team | Task 9 complete |
| Verify KNOWN_UNKNOWNS.md (27 unknowns verified) | 15min | Team | Task 1 complete |
| Day 0 standup & planning | 30min | Team | - |

**Quality Gates:**
- ✅ All prep tasks 1-10 marked complete in PREP_PLAN.md
- ✅ All 27 unknowns verified in KNOWN_UNKNOWNS.md
- ✅ Branch created and CI passing
- ✅ Baseline measurements recorded (parse rate: 40%, fast tests: 52.39s)
- ✅ Performance budgets documented in `docs/performance/baselines/budgets.json`

**Deliverables:**
- Sprint 9 branch created
- Baseline measurements in `docs/performance/baselines/sprint9_day0.json`
- Performance budget definitions

**Total Effort:** 2.5-3h

---

### Day 1: Test Infrastructure - Part 1 (4-5 hours)

**Objectives:**
1. Document mhw4dx secondary blockers (defer to Sprint 10)
2. Implement automated test fixture generation framework
3. Begin performance optimization (identify slow tests)

**Tasks:**

| Task | Effort | Owner | Dependencies |
|------|--------|-------|--------------|
| Analyze mhw4dx secondary blockers | 2-3h | Team | Task 2 research complete |
| Document blocker findings in BLOCKERS.md | 30min | Team | Analysis complete |
| Implement fixture generation framework | 1-2h | Team | Task 6 design complete |
| Write tests for fixture generator | 30min | Team | Framework implemented |
| Identify slow tests (pytest --durations=20) | 30min | Team | Baseline established |

**Quality Gates:**
- ✅ mhw4dx blockers documented with effort estimate (12-17h)
- ✅ Decision documented: DEFER mhw4dx to Sprint 10
- ✅ Fixture generator creates valid IR for basic cases
- ✅ Fixture generator tests pass
- ✅ Slow test list identified (≥10 tests >1s each)
- ✅ All quality checks pass: `make typecheck && make lint && make format && make test`

**Deliverables:**
- `docs/blockers/mhw4dx_analysis.md` (secondary blocker documentation)
- `tests/fixtures/generate_fixtures.py` (automated fixture generation framework)
- `tests/test_fixture_generator.py` (fixture generator tests)
- Slow test list in performance notes

**Dependencies:**
- Day 0 baseline complete
- Task 2 (mhw4dx research) complete
- Task 6 (fixture framework design) complete

**Total Effort:** 4-5h

---

### Day 2: Test Infrastructure - Part 2 (1-2 hours) → CHECKPOINT 1

**Objectives:**
1. Implement fixture validation script
2. Establish performance baseline and apply slow test markers
3. Achieve Checkpoint 1: Test infrastructure complete

**Tasks:**

| Task | Effort | Owner | Dependencies |
|------|--------|-------|--------------|
| Implement fixture validation script | 1h | Team | Task 7 design complete |
| Apply @pytest.mark.slow to identified slow tests | 30min | Team | Slow test list from Day 1 |
| Re-baseline fast test performance | 15min | Team | Slow markers applied |
| Validate <30s fast test budget achieved | 15min | Team | Re-baseline complete |

**Quality Gates:**
- ✅ Fixture validation script catches all 5 test fixture error types
- ✅ Fast test suite <30s (within budget) after slow markers applied
- ✅ All quality checks pass: `make typecheck && make lint && make format && make test`
- ✅ **CHECKPOINT 1 PASSED** (see Checkpoint Definitions section)

**Deliverables:**
- `scripts/validate_fixtures.py` (fixture validation script)
- Updated `pyproject.toml` with slow test markers
- `docs/performance/baselines/sprint9_day2.json` (performance baseline after optimization)

**Dependencies:**
- Day 1 fixture generator complete
- Task 7 (validation script design) complete
- Slow test list identified

**Total Effort:** 1-2h

**Checkpoint 1 Decision:**
- **GO:** Test infrastructure complete, performance budget achieved → Proceed to Day 3
- **NO-GO:** Performance budget not achieved → Spend Day 3 debugging, use Day 10 buffer

---

### Day 3: Advanced Indexing - Part 1 (4-5 hours)

**Objectives:**
1. Implement i++1, i--1 grammar changes
2. Implement semantic handlers for arithmetic indexing
3. Create IR representation for IndexExpression nodes

**Tasks:**

| Task | Effort | Owner | Dependencies |
|------|--------|-------|--------------|
| Update GAMS grammar (i++1, i--1 patterns) | 1-1.5h | Team | Task 3 design complete |
| Implement semantic handler for arithmetic indexing | 2-2.5h | Team | Grammar updated |
| Create IR IndexExpression nodes | 1h | Team | Semantic handler working |
| Write unit tests for i++1, i--1 indexing | 1h | Team | IR representation complete |

**Quality Gates:**
- ✅ Grammar parses "i++1", "i--1", "i+j", "i-j" patterns
- ✅ Semantic handler creates IndexExpression(base="i", offset=BinaryOp("+", 1))
- ✅ IR correctly represents arithmetic indexing
- ✅ Unit tests cover edge cases (i++10, i--5, i+j+k)
- ✅ All quality checks pass: `make typecheck && make lint && make format && make test`

**Deliverables:**
- Updated `src/grammar/gams.lark` (arithmetic indexing grammar)
- Updated `src/ir/semantic_handler.py` (indexing semantic handler)
- Updated `src/ir/nodes.py` (IndexExpression node type)
- Unit tests in `tests/test_indexing.py`

**Dependencies:**
- Checkpoint 1 passed
- Task 3 (i++1 design) complete

**Total Effort:** 4-5h

---

### Day 4: Advanced Indexing - Part 2 (4-5 hours) → CHECKPOINT 2

**Objectives:**
1. Validate i++1 indexing with himmel16.gms
2. Test advanced indexing edge cases
3. Achieve Checkpoint 2: i++1 working, himmel16 parses

**Tasks:**

| Task | Effort | Owner | Dependencies |
|------|--------|-------|--------------|
| Parse himmel16.gms (validate i++1 indexing) | 1h | Team | Day 3 implementation complete |
| Debug himmel16.gms parse failures (if any) | 1-2h | Team | Initial parse attempted |
| Write comprehensive indexing tests | 1-1.5h | Team | himmel16 parsing |
| Update dashboard with indexing statistics | 1h | Team | Tests passing |

**Quality Gates:**
- ✅ himmel16.gms parses successfully (unlocked by i++1)
- ✅ Parse rate ≥50% (4/10 → 5/10 with himmel16)
- ✅ Indexing test coverage ≥80%
- ✅ All quality checks pass: `make typecheck && make lint && make format && make test`
- ✅ **CHECKPOINT 2 PASSED** (see Checkpoint Definitions section)

**Deliverables:**
- himmel16.gms parsing successfully
- Comprehensive indexing test suite
- Updated dashboard with indexing metrics

**Dependencies:**
- Day 3 indexing implementation complete
- himmel16.gms available in GAMSLib subset

**Total Effort:** 4-5h

**Checkpoint 2 Decision:**
- **GO:** himmel16 parses, parse rate ≥50% → Proceed to Day 5
- **NO-GO:** himmel16 fails, indexing bugs → Spend Day 5 debugging, use Day 10 buffer

---

### Day 5: Model Sections (5-6 hours)

**Objectives:**
1. Implement model section grammar production
2. Implement semantic handlers for model declarations
3. Create IR representation for ModelDeclaration nodes
4. Validate with hs62.gms

**Tasks:**

| Task | Effort | Owner | Dependencies |
|------|--------|-------|--------------|
| Update GAMS grammar (model section production) | 1h | Team | Task 4 design complete |
| Implement semantic handler for model sections | 2-2.5h | Team | Grammar updated |
| Create IR ModelDeclaration nodes | 1h | Team | Semantic handler working |
| Parse hs62.gms (validate model sections) | 1h | Team | IR representation complete |
| Debug hs62.gms failures (if any) | 0.5-1h | Team | Initial parse attempted |
| Write model section tests | 1h | Team | hs62 parsing |

**Quality Gates:**
- ✅ Grammar parses "Model model_name / eq1, eq2, var1 /" syntax
- ✅ Semantic handler creates ModelDeclaration nodes
- ✅ IR correctly represents model structure
- ✅ hs62.gms parses successfully (unlocked by model sections)
- ✅ Parse rate ≥60% (5/10 → 6/10 with hs62)
- ✅ All quality checks pass: `make typecheck && make lint && make format && make test`

**Deliverables:**
- Updated `src/grammar/gams.lark` (model section grammar)
- Updated `src/ir/semantic_handler.py` (model section handler)
- Updated `src/ir/nodes.py` (ModelDeclaration node type)
- hs62.gms parsing successfully
- Model section test suite

**Dependencies:**
- Checkpoint 2 passed
- Task 4 (model sections design) complete

**Total Effort:** 5-6h

---

### Day 6: Equation Attributes (4-6 hours) → CHECKPOINT 3

**Objectives:**
1. Implement semantic handlers for equation attributes (.marginal, .l, .up, .lo)
2. Create IR representation for AttributeAccess nodes
3. Validate with mingamma.gms
4. Achieve Checkpoint 3: All parser features complete

**Tasks:**

| Task | Effort | Owner | Dependencies |
|------|--------|-------|--------------|
| Implement semantic handler for eq attributes | 2-3h | Team | Task 8 design complete |
| Create IR AttributeAccess nodes | 1h | Team | Semantic handler working |
| Parse mingamma.gms (validate attributes) | 1h | Team | IR representation complete |
| Debug mingamma.gms failures (if any) | 0.5-1h | Team | Initial parse attempted |
| Write attribute access tests | 1-1.5h | Team | mingamma parsing |
| Update dashboard with attribute statistics | 30min | Team | Tests passing |

**Quality Gates:**
- ✅ Semantic handler creates AttributeAccess(variable="eq1", attribute="marginal")
- ✅ IR correctly represents all 4 attribute types (.marginal, .l, .up, .lo)
- ✅ mingamma.gms parses successfully (unlocked by attributes)
- ✅ Parse rate ≥60% (6/10 → 6-7/10 with mingamma + potentially others)
- ✅ All quality checks pass: `make typecheck && make lint && make format && make test`
- ✅ **CHECKPOINT 3 PASSED** (see Checkpoint Definitions section)

**Deliverables:**
- Updated `src/ir/semantic_handler.py` (attribute semantic handler)
- Updated `src/ir/nodes.py` (AttributeAccess node type)
- mingamma.gms parsing successfully
- Equation attribute test suite
- Updated dashboard

**Dependencies:**
- Day 5 model sections complete
- Task 8 (equation attributes design) complete
- Grammar already supports attributes (no grammar work)

**Total Effort:** 4-6h

**Checkpoint 3 Decision:**
- **GO:** All parser features working, parse rate ≥60% → Proceed to Day 7
- **NO-GO:** Parser features incomplete → Spend Day 7 debugging, defer conversion to Day 10

---

### Day 7: Conversion Pipeline - Part 1 (4-5 hours)

**Objectives:**
1. Implement converter class scaffolding
2. Implement IR → MCP GAMS mappings for variables, parameters
3. Implement IR → MCP GAMS mappings for equations

**Tasks:**

| Task | Effort | Owner | Dependencies |
|------|--------|-------|--------------|
| Implement Converter class scaffolding | 1h | Team | Task 5 design complete |
| Implement variable IR → MCP mappings | 1-1.5h | Team | Scaffolding complete |
| Implement parameter IR → MCP mappings | 1-1.5h | Team | Variables working |
| Implement equation IR → MCP mappings | 1-2h | Team | Parameters working |
| Write converter unit tests | 1h | Team | Mappings implemented |

**Quality Gates:**
- ✅ Converter class instantiates and accepts IR as input
- ✅ Variables convert to MCP GAMS format
- ✅ Parameters convert to MCP GAMS format
- ✅ Equations convert to MCP GAMS format
- ✅ Unit tests cover all IR node types
- ✅ All quality checks pass: `make typecheck && make lint && make format && make test`

**Deliverables:**
- `src/converter/converter.py` (Converter class)
- `src/converter/mappings.py` (IR → MCP mappings)
- Unit tests in `tests/converter/test_converter.py`

**Dependencies:**
- Checkpoint 3 passed
- Task 5 (conversion pipeline design) complete

**Total Effort:** 4-5h

---

### Day 8: Conversion Pipeline - Part 2 (2-3 hours) → CHECKPOINT 4

**Objectives:**
1. Convert at least 1 model end-to-end (GAMS NLP → MCP GAMS)
2. Validate MCP GAMS output parses successfully
3. Implement conversion validation script
4. Achieve Checkpoint 4: 1 model converts

**Tasks:**

| Task | Effort | Owner | Dependencies |
|------|--------|-------|--------------|
| Convert mhw4d.gms or rbrock.gms end-to-end | 1h | Team | Day 7 converter complete |
| Debug conversion failures (if any) | 0.5-1h | Team | Initial conversion attempted |
| Implement conversion validation script | 1h | Team | Conversion working |
| Validate MCP GAMS output parses as valid GAMS | 30min | Team | Validation script working |

**Quality Gates:**
- ✅ At least 1 model converts successfully (mhw4d or rbrock)
- ✅ MCP GAMS output parses successfully as valid GAMS
- ✅ Conversion validation script working
- ✅ All quality checks pass: `make typecheck && make lint && make format && make test`
- ✅ **CHECKPOINT 4 PASSED** (see Checkpoint Definitions section)

**Deliverables:**
- mhw4d.gms or rbrock.gms converted to MCP GAMS format
- `scripts/validate_conversion.py` (conversion validation script)
- MCP GAMS output validated (parses successfully)

**Dependencies:**
- Day 7 converter implementation complete
- GAMS parser available for validation

**Total Effort:** 2-3h

**Checkpoint 4 Decision:**
- **GO:** 1 model converts, validation works → Proceed to Day 9
- **NO-GO:** Conversion failures → Spend Day 9 debugging, use Day 10 buffer

---

### Day 9: Dashboard & Performance Instrumentation (4-5 hours)

**Objectives:**
1. Expand dashboard with Sprint 9 metrics
2. Implement performance budget enforcement in CI
3. Document all Sprint 9 achievements

**Tasks:**

| Task | Effort | Owner | Dependencies |
|------|--------|-------|--------------|
| Add indexing metrics to dashboard | 1-1.5h | Team | i++1 feature complete |
| Add model section metrics to dashboard | 1h | Team | Model sections complete |
| Add conversion metrics to dashboard | 1-1.5h | Team | Conversion pipeline working |
| Implement CI performance budget checks | 1-2h | Team | Task 9 design complete |
| Update performance documentation | 30min | Team | Budgets enforced |

**Quality Gates:**
- ✅ Dashboard shows i++1 indexing statistics
- ✅ Dashboard shows model section statistics
- ✅ Dashboard shows conversion success rate
- ✅ CI fails if fast tests >30s
- ✅ CI warns if fast tests >27s (90% budget)
- ✅ All quality checks pass: `make typecheck && make lint && make format && make test`

**Deliverables:**
- Updated `scripts/dashboard.py` (Sprint 9 metrics)
- Updated `.github/workflows/performance-check.yml` (budget enforcement)
- `docs/performance/BUDGET_ENFORCEMENT.md` (documentation)

**Dependencies:**
- Checkpoint 4 passed
- All Sprint 9 features complete
- Task 9 (performance framework) complete

**Total Effort:** 4-5h

---

### Day 10: Documentation, PR, & Sprint Closeout (2-3 hours) - BUFFER DAY

**Objectives:**
1. Complete all documentation updates
2. Create Sprint 9 PR with comprehensive summary
3. Run final quality checks and sprint retrospective
4. **Absorb any overruns from Days 1-9**

**Tasks:**

| Task | Effort | Owner | Dependencies |
|------|--------|-------|--------------|
| Update CHANGELOG.md with Sprint 9 summary | 1h | Team | All features complete |
| Write Sprint 9 retrospective notes | 30min | Team | Sprint complete |
| Create Sprint 9 PR | 30min | Team | All commits ready |
| Final quality gate validation | 30min | Team | PR created |
| Sprint closeout meeting | 30min | Team | - |

**Quality Gates:**
- ✅ All Sprint 9 acceptance criteria met (see Deliverables section)
- ✅ All 4 checkpoints passed
- ✅ Parse rate ≥30% baseline (realistic: 50-60%)
- ✅ At least 1 model converts end-to-end
- ✅ Fast test suite <30s
- ✅ All quality checks pass: `make typecheck && make lint && make format && make test`
- ✅ PR ready for review

**Deliverables:**
- Updated `CHANGELOG.md` (Sprint 9 summary)
- Sprint 9 PR created
- Retrospective notes in `docs/planning/EPIC_2/SPRINT_9/RETROSPECTIVE.md`

**Dependencies:**
- Days 1-9 complete (or absorb overruns)

**Total Effort:** 2-3h (or more if absorbing overruns)

**Buffer Usage:**
- **Scenario 1:** All days on schedule → Use Day 10 for polish and documentation
- **Scenario 2:** 1-2 day overrun → Day 10 absorbs, sprint still completes on time
- **Scenario 3:** 3+ day overrun → Reduce scope (defer conversion or attributes), still deliver core features

---

## 3. Checkpoint Definitions

Sprint 9 has **4 checkpoints** with clear go/no-go criteria. Each checkpoint validates critical dependencies before proceeding.

### Checkpoint 1: Test Infrastructure Complete (Day 2 End)

**Success Criteria:**
1. ✅ mhw4dx secondary blockers documented (decision: defer to Sprint 10)
2. ✅ Automated fixture generator working (creates valid IR)
3. ✅ Fixture validation script working (catches 5 error types)
4. ✅ Fast test suite <30s (performance budget achieved)
5. ✅ Slow test markers applied to ≥10 tests

**Go/No-Go Decision:**
- **GO:** All 5 criteria met → Proceed to Day 3 (i++1 indexing)
- **NO-GO:** Performance budget not achieved → Spend Day 3 optimizing tests, use Day 10 buffer

**Rationale:** Test infrastructure must be solid before adding parser complexity. Performance budget critical for fast feedback throughout sprint.

**Risk if Skipped:** Slow tests bog down development, fixture bugs waste debugging time.

---

### Checkpoint 2: i++1 Indexing Working (Day 4 End)

**Success Criteria:**
1. ✅ Grammar supports i++1, i--1 patterns
2. ✅ Semantic handler creates IndexExpression nodes correctly
3. ✅ IR representation complete and tested
4. ✅ himmel16.gms parses successfully (validates i++1)
5. ✅ Parse rate ≥50% (4/10 → 5/10 with himmel16)
6. ✅ Indexing test coverage ≥80%

**Go/No-Go Decision:**
- **GO:** All 6 criteria met → Proceed to Day 5 (model sections)
- **NO-GO:** himmel16 fails to parse → Spend Day 5 debugging indexing, defer model sections to Day 6, use Day 10 buffer

**Rationale:** i++1 indexing is foundational for himmel16 and other models. Must work before adding more features.

**Risk if Skipped:** Compound bugs between indexing and model sections, harder debugging.

---

### Checkpoint 3: All Parser Features Complete (Day 6 End)

**Success Criteria:**
1. ✅ Model sections fully implemented (grammar + semantic + IR)
2. ✅ hs62.gms parses successfully (validates model sections)
3. ✅ Equation attributes fully implemented (semantic + IR only, grammar already exists)
4. ✅ mingamma.gms parses successfully (validates attributes)
5. ✅ Parse rate ≥60% (6-7/10 models)
6. ✅ All parser features tested with ≥80% coverage

**Go/No-Go Decision:**
- **GO:** All 6 criteria met → Proceed to Day 7 (conversion pipeline)
- **NO-GO:** Parser features incomplete → Spend Day 7 finishing parser, defer conversion to Day 8-9, accept reduced conversion scope

**Rationale:** Parser must be complete before conversion. Conversion depends on stable IR.

**Risk if Skipped:** Conversion failures due to incomplete IR, wasted effort.

**Contingency:** If parser features take longer, defer conversion to Day 8-9 or accept "conversion pipeline scaffolding only" as Sprint 9 deliverable.

---

### Checkpoint 4: Conversion Pipeline Working (Day 8 End)

**Success Criteria:**
1. ✅ Converter class scaffolding complete
2. ✅ IR → MCP GAMS mappings for variables, parameters, equations
3. ✅ At least 1 model converts successfully (mhw4d or rbrock)
4. ✅ MCP GAMS output parses successfully as valid GAMS
5. ✅ Conversion validation script working

**Go/No-Go Decision:**
- **GO:** All 5 criteria met → Proceed to Day 9 (dashboard + performance)
- **NO-GO:** Conversion fails → Spend Day 9 debugging, document known gaps, accept "partial conversion" as Sprint 9 deliverable

**Rationale:** Conversion pipeline is Sprint 9's stretch goal. Core parser features (Goals 2-4) are higher priority.

**Risk if Skipped:** No end-to-end validation, harder to catch IR gaps.

**Contingency:** If conversion takes longer, document what works and what doesn't, defer full conversion to Sprint 10.

---

## 4. Effort Allocation

### 4.1 Total Effort Breakdown

| Component | Conservative | Realistic | Upper Bound | Notes |
|-----------|--------------|-----------|-------------|-------|
| **Day 0: Sprint Planning** | 2h | 2.5h | 3h | Review, baseline, setup |
| **Days 1-2: Test Infrastructure** | 5h | 6h | 7h | Fixtures, validation, performance |
| **Days 3-4: i++1 Indexing** | 8h | 9h | 10h | Grammar, semantic, IR, tests |
| **Days 5-6: Model Sections + Attributes** | 9h | 10.5h | 12h | Two features in parallel |
| **Days 7-8: Conversion Pipeline** | 6h | 7h | 8h | Converter, mappings, validation |
| **Day 9: Dashboard + Performance** | 4h | 4.5h | 5h | Metrics, CI integration |
| **Day 10: Documentation + Closeout** | 2h | 2.5h | 3h | CHANGELOG, PR, retrospective |
| **TOTAL** | **36h** | **42h** | **48h** | Target: 30-41h |

**Effort Analysis:**
- **Conservative (36h):** Exceeds 30-41h target by 1h, but within acceptable margin
- **Realistic (42h):** Exceeds target by 1h, requires Day 10 buffer + efficient execution
- **Upper Bound (48h):** Requires Day 10 buffer + scope reduction (defer conversion or attributes)

**Conclusion:** Sprint 9 effort estimates are **tight but achievable** with:
1. Efficient execution (minimize debugging)
2. Day 10 buffer usage (2-3h available)
3. Scope flexibility (defer conversion if parser takes longer)

### 4.2 Effort by Feature Area

| Feature Area | Effort | % of Total | Priority | Risk |
|--------------|--------|------------|----------|------|
| **Test Infrastructure** | 5-7h | 14-16% | High | Low (well-defined) |
| **i++1 Indexing** | 8-10h | 19-24% | Critical | Medium (grammar changes) |
| **Model Sections** | 5-6h | 12-14% | High | Low (straightforward) |
| **Equation Attributes** | 4-6h | 10-14% | Medium | Low (no grammar work) |
| **Conversion Pipeline** | 6-8h | 14-19% | Medium | Medium (new infrastructure) |
| **Dashboard + Performance** | 4-5h | 10-12% | Medium | Low (incremental) |
| **Planning + Documentation** | 4-6h | 10-14% | Low | Low (routine) |

### 4.3 Critical Path Analysis

**Critical Path:** Test Infrastructure → i++1 Indexing → Model Sections → Conversion Pipeline → Closeout

**Critical Path Effort:** 18-24h (Conservative: 18h, Realistic: 21h, Upper: 24h)

**Non-Critical Path:** Equation attributes can be parallelized with model sections (Day 6)

**Buffer Availability:**
- Total sprint capacity: 11 days × 3h/day = 33h capacity
- Critical path: 18-24h
- Buffer: 9-15h available for non-critical tasks and overruns

**Conclusion:** Critical path fits comfortably in sprint duration. Day 10 provides additional 2-3h buffer.

---

## 5. Risk Register

Sprint 9 has **7 identified risks** with mitigation strategies and contingency plans.

### Risk 1: i++1 Indexing More Complex Than Expected (8-10h → 12-15h)

**Likelihood:** Medium  
**Impact:** High (blocks himmel16, delays downstream tasks)  
**Current Estimate:** 8-10h (from Task 3)

**Mitigation:**
- Task 3 already validated grammar changes with prototype
- Semantic handler design already complete
- Unit tests defined in advance

**Contingency:**
- Use Day 10 buffer (2-3h additional time)
- Defer equation attributes to Sprint 10 if needed
- Accept 50% parse rate instead of 60% if model sections also delayed

**Trigger:** Day 4 checkpoint fails (himmel16 doesn't parse)

---

### Risk 2: Conversion Pipeline Blocked by IR Gaps

**Likelihood:** Medium  
**Impact:** Medium (conversion is stretch goal, not critical)  
**Current Estimate:** 6-8h

**Mitigation:**
- Task 5 already identified IR coverage (variables, parameters, equations supported)
- Start with simplest models (mhw4d, rbrock)
- Document missing KKT transformation patterns instead of fixing in Sprint 9

**Contingency:**
- Accept "partial conversion" as Sprint 9 deliverable (e.g., KKT equations generated but not all complementarity conditions)
- Document IR gaps and missing transformation patterns for Sprint 10
- Defer full NLP→MCP conversion to Sprint 10

**Trigger:** Day 8 checkpoint fails (no model converts to valid MCP GAMS)

---

### Risk 3: Performance Budget Not Achievable (<30s fast tests)

**Likelihood:** Low  
**Impact:** Medium (slows development, but not blocking)  
**Current State:** 52.39s (74% over budget)

**Mitigation:**
- Slow test markers already identified in Task 9
- Hypothesis: Re-apply markers from Sprint 8 → 24s (within budget)
- Performance framework already designed

**Contingency:**
- Spend extra time on Day 2 identifying slow tests
- Use Day 10 buffer for optimization
- Accept 40s budget if 30s infeasible (still better than 52s)

**Trigger:** Day 2 checkpoint fails (fast tests still >30s after markers)

---

### Risk 4: Parse Rate Drops Below 30% Baseline (Regressions)

**Likelihood:** Low  
**Impact:** High (violates Goal 1)  
**Current State:** 40% (4/10 models)

**Mitigation:**
- Comprehensive test coverage before grammar changes
- Incremental testing (test after each grammar change)
- Checkpoint 2 validates no regressions (himmel16 + existing 4 models)

**Contingency:**
- Debug regressions immediately (halt feature work)
- Use Day 10 buffer for regression fixes
- Revert grammar changes if unfixable

**Trigger:** Any existing passing model (mhw4d, rbrock, mathopt1, trig) starts failing

---

### Risk 5: Model Sections or Equation Attributes Take Longer Than Expected

**Likelihood:** Low  
**Impact:** Low (can defer one feature)  
**Current Estimate:** Model sections 5-6h, Attributes 4-6h

**Mitigation:**
- Both features well-researched in Tasks 4 and 8
- Equation attributes require no grammar changes (lower risk)
- Model sections straightforward (single grammar production)

**Contingency:**
- Defer equation attributes to Sprint 10 if needed
- Accept 60% parse rate without mingamma (model sections more important)
- Use Day 10 buffer

**Trigger:** Day 6 checkpoint fails (hs62 or mingamma don't parse)

---

### Risk 6: Fixture Validation Script Catches Existing Bugs

**Likelihood:** Medium  
**Impact:** Low (good to find bugs, but requires extra time)

**Mitigation:**
- Budget 1h for fixing fixture bugs found by validation script
- Validation script is quality improvement (not blocking)

**Contingency:**
- Document bugs for later fixing
- Accept some manual fixture validation if script too strict

**Trigger:** Validation script reports ≥5 fixture bugs

---

### Risk 7: Day 10 Buffer Insufficient (3+ Day Overrun)

**Likelihood:** Low  
**Impact:** High (sprint timeline extends or scope reduces)

**Mitigation:**
- Conservative estimates already account for debugging time
- 4 checkpoints provide early warning of delays
- Scope flexibility (conversion and attributes are deferrable)

**Contingency:**
- **Option 1:** Extend sprint to Day 11-12 (acceptable for complex sprint)
- **Option 2:** Reduce scope (defer conversion to Sprint 10)
- **Option 3:** Reduce scope (defer equation attributes to Sprint 10)
- **Option 4:** Accept 50% parse rate instead of 60%

**Trigger:** 3+ checkpoints fail or require rework

---

## 6. Quality Gates

### 6.1 Continuous Quality Gates (All Days)

These gates must pass **every day** before committing:

| Gate | Command | Acceptance | Notes |
|------|---------|------------|-------|
| **Type Checking** | `make typecheck` | Zero type errors | mypy strict mode |
| **Linting** | `make lint` | Zero lint errors | ruff with custom rules |
| **Code Formatting** | `make format` | Zero format changes | black + ruff |
| **Fast Tests** | `make test` | All tests pass, <30s | After Day 2 budget enforcement |
| **Test Coverage** | `pytest --cov` | ≥80% coverage on new code | Tracked per feature |

**Enforcement:** CI blocks merge if any gate fails.

### 6.2 Feature-Specific Quality Gates

#### Day 0 Quality Gates

- ✅ All prep tasks 1-10 marked complete in PREP_PLAN.md
- ✅ All 27 unknowns verified in KNOWN_UNKNOWNS.md
- ✅ Branch created and CI passing
- ✅ Baseline measurements recorded

#### Day 2 Quality Gates (Checkpoint 1)

- ✅ mhw4dx blockers documented (decision: defer)
- ✅ Fixture generator creates valid IR
- ✅ Fixture validation script catches 5 error types
- ✅ Fast test suite <30s (budget achieved)

#### Day 4 Quality Gates (Checkpoint 2)

- ✅ himmel16.gms parses successfully
- ✅ Parse rate ≥50% (5/10 models)
- ✅ Indexing test coverage ≥80%

#### Day 6 Quality Gates (Checkpoint 3)

- ✅ hs62.gms parses successfully
- ✅ mingamma.gms parses successfully
- ✅ Parse rate ≥60% (6-7/10 models)
- ✅ All parser features tested ≥80% coverage

#### Day 8 Quality Gates (Checkpoint 4)

- ✅ At least 1 model converts (mhw4d or rbrock)
- ✅ MCP GAMS validates against schema
- ✅ Conversion validation script working

#### Day 10 Quality Gates (Sprint Complete)

- ✅ All Sprint 9 acceptance criteria met
- ✅ All 4 checkpoints passed
- ✅ Parse rate ≥30% baseline (realistic: 50-60%)
- ✅ PR ready for review

---

## 7. Deliverables & Acceptance Criteria

### 7.1 Sprint 9 Deliverables

#### Parser Features

1. **i++1 Indexing**
   - Updated `src/grammar/gams.lark` (arithmetic indexing grammar)
   - Updated `src/ir/semantic_handler.py` (indexing handler)
   - Updated `src/ir/nodes.py` (IndexExpression node)
   - himmel16.gms parsing successfully
   - Unit tests with ≥80% coverage

2. **Model Sections**
   - Updated `src/grammar/gams.lark` (model section production)
   - Updated `src/ir/semantic_handler.py` (model section handler)
   - Updated `src/ir/nodes.py` (ModelDeclaration node)
   - hs62.gms parsing successfully
   - Unit tests with ≥80% coverage

3. **Equation Attributes**
   - Updated `src/ir/semantic_handler.py` (attribute handler)
   - Updated `src/ir/nodes.py` (AttributeAccess node)
   - mingamma.gms parsing successfully
   - Unit tests for .marginal, .l, .up, .lo

#### Test Infrastructure

4. **Automated Fixture Generation**
   - `tests/fixtures/generate_fixtures.py` (fixture generator)
   - `tests/test_fixture_generator.py` (generator tests)

5. **Fixture Validation Script**
   - `scripts/validate_fixtures.py` (validation script)
   - Catches 5 fixture error types

6. **Performance Baseline**
   - `docs/performance/baselines/sprint9_day0.json` (baseline)
   - `docs/performance/baselines/budgets.json` (budget definitions)
   - Fast test suite <30s

#### Conversion Pipeline

7. **Converter Infrastructure**
   - `src/converter/converter.py` (Converter class)
   - `src/converter/mappings.py` (IR → MCP GAMS mappings)
   - `scripts/validate_conversion.py` (validation script)
   - At least 1 model converts (mhw4d or rbrock) to valid MCP GAMS

#### Dashboard & Performance

8. **Updated Dashboard**
   - Indexing statistics
   - Model section statistics
   - Conversion success rate
   - Performance metrics

9. **CI Performance Checks**
   - `.github/workflows/performance-check.yml` (budget enforcement)
   - Fails if fast tests >30s
   - Warns if fast tests >27s

#### Documentation

10. **Blocker Documentation**
    - `docs/blockers/mhw4dx_analysis.md` (secondary blocker analysis)

11. **Updated CHANGELOG.md**
    - Sprint 9 summary with all achievements

12. **Sprint 9 Retrospective**
    - `docs/planning/EPIC_2/SPRINT_9/RETROSPECTIVE.md`

### 7.2 Acceptance Criteria (from PROJECT_PLAN.md)

**All criteria must be met for Sprint 9 to be considered complete:**

- ✅ **AC1:** Parse rate ≥30% baseline (maintain with advanced features)
- ✅ **AC2:** i++1 and i--1 indexing working (himmel16.gms parses)
- ✅ **AC3:** Model sections implemented (hs62.gms parses)
- ✅ **AC4:** Equation attributes implemented (mingamma.gms parses)
- ✅ **AC5:** At least 1 model converts end-to-end (GAMS NLP → MCP GAMS)
- ✅ **AC6:** MCP GAMS output parses successfully as valid GAMS
- ✅ **AC7:** Automated fixture generation working
- ✅ **AC8:** Fixture validation script working
- ✅ **AC9:** Performance baseline established (<30s fast tests)
- ✅ **AC10:** Dashboard updated with Sprint 9 metrics
- ✅ **AC11:** All quality checks pass (typecheck, lint, format, test)
- ✅ **AC12:** Documentation complete (CHANGELOG, retrospective)

**Success Threshold:** 10/12 criteria met (83%) = Sprint 9 SUCCESS

**Failure Threshold:** <8/12 criteria met (<67%) = Sprint 9 requires re-planning

---

## 8. Cross-References

### 8.1 Prep Tasks → Sprint Days Mapping

| Prep Task | Sprint Days | Deliverables | Notes |
|-----------|-------------|--------------|-------|
| **Task 1: Unknowns** | Day 0 | Verified all 27 unknowns | Prerequisite for sprint start |
| **Task 2: mhw4dx** | Day 1 | BLOCKERS.md documentation | Defer to Sprint 10 (12-17h) |
| **Task 3: i++1 Indexing** | Days 3-4 | Grammar, semantic, IR, tests | Unlocks himmel16.gms |
| **Task 4: Model Sections** | Day 5 | Grammar, semantic, IR, tests | Unlocks hs62.gms |
| **Task 5: Conversion** | Days 7-8 | Converter, mappings, validation | End-to-end GAMS NLP → MCP GAMS |
| **Task 6: Fixtures** | Day 1 | Fixture generator | Reduces manual fixture work |
| **Task 7: Validation** | Day 2 | Validation script | Catches fixture bugs |
| **Task 8: Attributes** | Day 6 | Semantic handler, IR, tests | Unlocks mingamma.gms |
| **Task 9: Performance** | Days 0, 2, 9 | Baseline, budgets, CI | <30s fast tests |
| **Task 10: Planning** | Day 0 | This document (PLAN.md) | Master execution plan |

### 8.2 Features → Models Unlocked Mapping

| Feature | Models Unlocked | Parse Rate Impact | Effort |
|---------|-----------------|-------------------|--------|
| **i++1 Indexing** | himmel16.gms | +10% (4/10 → 5/10) | 8-10h |
| **Model Sections** | hs62.gms | +10% (5/10 → 6/10) | 5-6h |
| **Equation Attributes** | mingamma.gms (potentially) | +10% (6/10 → 7/10) | 4-6h |
| **All Features Combined** | himmel16, hs62, mingamma | +30% (4/10 → 7/10 theoretical) | 17-22h |

**Realistic Parse Rate:** 50-60% (5-6/10 models) accounting for overlapping dependencies

### 8.3 Dependencies Graph

```
Day 0 (Baseline)
    ↓
Day 1 (Fixtures + mhw4dx)
    ↓
Day 2 (Validation + Performance) → CHECKPOINT 1
    ↓
Day 3 (i++1 Part 1)
    ↓
Day 4 (i++1 Part 2) → CHECKPOINT 2
    ↓
Day 5 (Model Sections)
    ↓
Day 6 (Equation Attributes) → CHECKPOINT 3
    ↓
Day 7 (Conversion Part 1)
    ↓
Day 8 (Conversion Part 2) → CHECKPOINT 4
    ↓
Day 9 (Dashboard + Performance)
    ↓
Day 10 (Documentation + Closeout)
```

**Critical Path:** Days 0 → 2 → 4 → 6 → 8 → 10 (all checkpoints must pass)

---

## 9. Appendices

### Appendix A: Sprint 9 vs Sprint 8 Comparison

| Aspect | Sprint 8 | Sprint 9 | Change |
|--------|----------|----------|--------|
| **Duration** | 11 days (Days 0-10) | 11 days (Days 0-10) | Same |
| **Effort** | 30-41h (average 35.5h) | 36-48h (average 42h) | +18% effort |
| **Parse Rate Target** | 40% (4/10) | 50-60% (5-6/10) | +25-50% improvement |
| **Grammar Changes** | None (only semantic) | Yes (i++1 indexing) | Higher risk |
| **New Pipeline Stage** | No | Yes (conversion) | New infrastructure |
| **Performance Focus** | Day 9 optimization | Day 0 budgets | Earlier optimization |
| **Test Infrastructure** | Manual fixtures | Automated fixtures | Quality improvement |
| **Checkpoints** | 4 | 4 | Same |
| **Complexity** | Medium | High | More complex |
| **Risk Level** | Low | Medium | Higher risk |

**Key Insight:** Sprint 9 is more complex than Sprint 8 due to grammar changes and new conversion pipeline. However, comprehensive prep work (47-63h vs Sprint 8's ~30h) provides higher confidence.

### Appendix B: Lessons from Sprint 8

**Lesson 1: Performance Budget Should Be Day 0, Not Day 9**
- Sprint 8 optimized tests on Day 9 (120s → 24s)
- Sprint 9 establishes budgets on Day 0
- **Applied:** Day 0 and Day 2 tasks include performance baseline and budget enforcement

**Lesson 2: Automated Fixtures Reduce Manual Errors**
- Sprint 8 had 3 fixture bugs that wasted debugging time
- Sprint 9 implements automated fixture generation (Day 1)
- **Applied:** Fixture validation script (Day 2) catches errors early

**Lesson 3: Checkpoints Provide Early Warning**
- Sprint 8's 4 checkpoints all passed on schedule
- Checkpoints caught 2 issues early (option statement scope, indexed assignment edge case)
- **Applied:** Sprint 9 maintains 4 checkpoint structure

**Lesson 4: Buffer Day (Day 10) Absorbs Overruns**
- Sprint 8 used Day 10 for polish and documentation
- Day 10 provides flexibility for scope adjustments
- **Applied:** Sprint 9 designates Day 10 as BUFFER

**Lesson 5: Comprehensive Prep Reduces Sprint Risk**
- Sprint 8 had 27 unknowns, all verified in prep
- Zero blocking issues discovered during sprint
- **Applied:** Sprint 9 has 27 unknowns verified, 10 prep tasks completed (47-63h total)

### Appendix C: Sprint 9 Quality Gate Checklist

**Use this checklist to validate Sprint 9 completion:**

#### Day 0 Gates
- [ ] All prep tasks 1-10 marked complete
- [ ] All 27 unknowns verified
- [ ] Branch created, CI passing
- [ ] Baseline measurements recorded

#### Day 2 Gates (Checkpoint 1)
- [ ] mhw4dx blockers documented
- [ ] Fixture generator working
- [ ] Fixture validation script working
- [ ] Fast tests <30s

#### Day 4 Gates (Checkpoint 2)
- [ ] himmel16.gms parses
- [ ] Parse rate ≥50%
- [ ] Indexing test coverage ≥80%

#### Day 6 Gates (Checkpoint 3)
- [ ] hs62.gms parses
- [ ] mingamma.gms parses
- [ ] Parse rate ≥60%

#### Day 8 Gates (Checkpoint 4)
- [ ] 1 model converts to MCP GAMS
- [ ] MCP GAMS output parses successfully
- [ ] Conversion validation script working

#### Day 10 Gates (Sprint Complete)
- [ ] All acceptance criteria met (10/12 minimum)
- [ ] All 4 checkpoints passed
- [ ] Parse rate ≥30% baseline
- [ ] PR ready for review

### Appendix D: Unknown Verification Summary

All 27 unknowns identified in Task 1 have been verified across Tasks 2-9:

| Unknown | Category | Verified By | Decision |
|---------|----------|-------------|----------|
| 9.1.1 | i++1 Indexing | Task 3 | 8-10h effort, unlocks himmel16 |
| 9.1.2 | i++1 Grammar | Task 3 | Grammar changes required |
| 9.2.1 | Model Sections | Task 4 | 4-5h effort, unlocks hs62/mingamma |
| 9.2.2 | Model Semantics | Task 4 | IR ModelDeclaration node |
| 9.3.1 | Fixture Framework | Task 6 | 3h implementation |
| 9.3.2 | Fixture Validation | Task 7 | 2.5h validation script |
| 9.4.1 | Performance Metrics | Task 9 | 3 critical metrics selected |
| 9.4.2 | Budget Enforcement | Task 9 | Tiered enforcement strategy |
| 9.5.1 | Effort Allocation | Task 10 | 36-48h validated |
| 9.5.2 | Checkpoint Strategy | Task 10 | 4 checkpoints sufficient |
| ... | ... | ... | ... (17 more unknowns) |

**Full details in `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md`**

---

## End of Sprint 9 Plan

**Total Document Length:** ~1,950 lines  
**Preparation Effort:** 47-63 hours (Tasks 1-10)  
**Execution Effort:** 36-48 hours (Days 0-10)  
**Total Sprint 9 Effort:** 83-111 hours (prep + execution)

**Next Steps:**
1. Review this plan with stakeholders
2. Validate effort estimates against team capacity
3. Approve plan and proceed to Sprint 9 Day 0
4. Use this plan as daily reference throughout sprint

**Questions or Concerns:** Contact sprint team or refer to PREP_PLAN.md for detailed task breakdowns.
