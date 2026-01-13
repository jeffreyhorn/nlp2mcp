# Sprint 15 Detailed Plan

**Sprint:** 15  
**Duration:** 10 working days  
**Goal:** Build Pipeline Testing Infrastructure & Establish Initial Baseline  
**Status:** READY FOR EXECUTION

---

## Executive Summary

Sprint 15 builds on the JSON database infrastructure from Sprint 14 (219 models, 34 parsed, 32 translated) to create comprehensive automated testing infrastructure covering the full nlp2mcp pipeline (parse → translate → solve → compare).

### Key Deliverables

1. **test_parse.py** - Enhanced parse testing with refined error categorization (16 categories)
2. **test_translate.py** - Enhanced translation testing with error categorization (12 categories)
3. **test_solve.py** - MCP solve testing with PATH solver and solution comparison
4. **run_full_test.py** - Full pipeline orchestrator with filtering framework
5. **schema v2.1.0** - Database schema extended with solve and comparison objects
6. **Initial baseline metrics** - Performance and success rate documentation

### Prep Phase Summary

| Task | Status | Key Finding |
|------|--------|-------------|
| Task 1: Known Unknowns | ✅ Complete | 26 unknowns identified across 6 categories |
| Task 2: Batch Infrastructure | ✅ Complete | Extend existing scripts (save 12-16h effort) |
| Task 3: Solution Comparison | ✅ Complete | rtol=1e-6, atol=1e-8, objectives only |
| Task 4: Error Taxonomy | ✅ Complete | 44 outcome categories (16+12+16) |
| Task 5: PATH Solver | ✅ Complete | Validated, demo license until Jan 23, 2026 |
| Task 6: Schema Extensions | ✅ Complete | v2.1.0 backward compatible design |
| Task 7: Test Filtering | ✅ Complete | 14 MVP filters, AND logic |
| Task 8: Performance Measurement | ✅ Complete | perf_counter(), dual JSON/MD format |
| Task 9: Tolerance Research | ✅ Complete | Justified from 5 solvers + NumPy/CUTEst |
| Task 10: Detailed Schedule | ✅ Complete | This document |

### Critical Metrics from Prep Phase

| Metric | Value | Source |
|--------|-------|--------|
| Parse success rate (Sprint 14) | 21.3% (34/160) | batch_parse.py results |
| Translation success rate | 94.1% (32/34) | batch_translate.py results |
| Tolerance (rtol) | 1e-6 | Task 9 research |
| Tolerance (atol) | 1e-8 | Task 9 research |
| Error categories | 44 total | Task 4 taxonomy |
| MVP filter count | 14 | Task 7 requirements |
| GAMSLIB models with obj=0 | 7.5% (13/174) | Task 9 GAMSLIB analysis |

### Sprint 14 Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| gamslib_status.json v2.0.0 | ✅ Ready | 219 models, 34 parsed, 32 translated |
| batch_parse.py | ✅ Ready | Direct parser import, 6 error categories |
| batch_translate.py | ✅ Ready | Subprocess isolation, MCP output |
| db_manager.py | ✅ Ready | 8 subcommands, backup system |
| schema.json v2.0.0 | ✅ Ready | JSON Schema Draft-07 |
| PATH solver | ✅ Validated | GAMS 51.3.0, PATH 5.2.01 |

---

## 10-Day Schedule

### Phase 1: Foundation (Days 1-2)

#### Day 1: Schema Update and Migration

**Focus:** Update database schema to v2.1.0 and prepare infrastructure

| Task | Est. Time | Description |
|------|-----------|-------------|
| Review schema_v2.1.0_draft.json | 0.5h | Final review of prep task 6 output |
| Create schema.json v2.1.0 | 1h | Copy draft, update version, validate |
| Create schema migration script | 1.5h | Add new optional objects to existing models |
| Run migration on gamslib_status.json | 0.5h | Apply schema update |
| Validate all 219 entries | 0.5h | Ensure backward compatibility |
| Update db_manager.py for new objects | 1h | Add get/update support for new fields |

**Deliverables:**
- `data/gamslib/schema.json` v2.1.0
- `scripts/gamslib/migrate_schema_v2.1.0.py`
- Updated `data/gamslib/gamslib_status.json`
- Updated `db_manager.py` with new object support

**Acceptance Criteria:**
- [ ] Schema v2.1.0 validates all existing entries
- [ ] New objects (mcp_solve_result, solution_comparison_result) can be added
- [ ] db_manager.py update works with new nested fields
- [ ] Backup created before migration

**Time Estimate:** 5 hours

#### Day 2: Error Taxonomy Integration

**Focus:** Implement error categorization functions from Task 4 taxonomy

| Task | Est. Time | Description |
|------|-----------|-------------|
| Create error_taxonomy.py module | 2h | Categorization functions with regex patterns |
| Integrate parse error detection | 1h | 16 parse error categories |
| Integrate translate error detection | 1h | 12 translation error categories |
| Add solve outcome categorization | 1h | 16 solve outcome categories |
| Write unit tests for taxonomy | 1h | Test pattern matching |

**Deliverables:**
- `scripts/gamslib/error_taxonomy.py`
- Unit tests for error categorization
- Integration with existing batch scripts

**Acceptance Criteria:**
- [ ] All 44 outcome categories implemented
- [ ] Regex patterns detect errors correctly
- [ ] Backward compatible with Sprint 14 categories
- [ ] Unit tests pass (20+ test cases)

**Time Estimate:** 6 hours

**Checkpoint 1 (End of Day 2):** Schema updated, error taxonomy functional

---

### Phase 2: Parse Testing Enhancement (Days 3-4)

#### Day 3: Enhance batch_parse.py

**Focus:** Add filtering and refined error categorization to parse testing

| Task | Est. Time | Description |
|------|-----------|-------------|
| Add filter flags to batch_parse.py | 2h | --only-failing, --error-category, --type |
| Integrate error_taxonomy.py | 1h | Replace simple categorization |
| Add model statistics extraction | 1h | Variables, equations from IR |
| Add timing improvements | 0.5h | perf_counter, record all times |
| Update database with refined categories | 0.5h | Use new error_category enum |
| Test on subset of models | 1h | 10-20 models for validation |

**Deliverables:**
- Enhanced `batch_parse.py` with filters
- Model statistics in database
- Refined error categories applied

**Acceptance Criteria:**
- [ ] `--only-failing` filter works correctly
- [ ] `--error-category=syntax_error` filters by category
- [ ] `--type=NLP` filters by model type
- [ ] Model statistics (var_count, eq_count) recorded
- [ ] All 16 parse error categories can be assigned

**Time Estimate:** 6 hours

#### Day 4: Enhance batch_translate.py

**Focus:** Add filtering and error categorization to translation testing

| Task | Est. Time | Description |
|------|-----------|-------------|
| Add filter flags to batch_translate.py | 1.5h | --parse-success, --translate-failure |
| Integrate error_taxonomy.py | 1h | 12 translation error categories |
| Add MCP file validation | 1h | Basic syntax check with GAMS action=c |
| Add timing improvements | 0.5h | perf_counter, subprocess timing |
| Update database with results | 0.5h | Use new error categories |
| Run on all 34 parsed models | 0.5h | Full translation test |

**Deliverables:**
- Enhanced `batch_translate.py` with filters
- Translation error categorization
- MCP validation capability

**Acceptance Criteria:**
- [ ] `--parse-success` only processes parsed models
- [ ] All 12 translation error categories can be assigned
- [ ] MCP files validated (optional, via --validate flag)
- [ ] Translation timing recorded accurately

**Time Estimate:** 5 hours

**Checkpoint 2 (End of Day 4):** Parse and translate testing enhanced with filtering

---

### Phase 3: Solve Testing (Days 5-7)

#### Day 5: Create test_solve.py Core

**Focus:** Build solve testing infrastructure with PATH solver

| Task | Est. Time | Description |
|------|-----------|-------------|
| Create test_solve.py skeleton | 1h | argparse, logging, database integration |
| Implement PATH solver invocation | 2h | Subprocess with timeout, .lst parsing |
| Implement status code extraction | 1h | SOLVER STATUS, MODEL STATUS from .lst |
| Implement objective extraction | 1h | Parse objective value from .lst |
| Add database update for solve results | 1h | mcp_solve_result object |

**Deliverables:**
- `scripts/gamslib/test_solve.py` (basic solve functionality)
- PATH solver integration working
- Solve results in database

**Acceptance Criteria:**
- [ ] Can solve MCP file with PATH solver
- [ ] Extracts solver status and model status
- [ ] Extracts objective value (or handles MCP case)
- [ ] Updates database with mcp_solve_result
- [ ] 60-second timeout implemented

**Time Estimate:** 6 hours

#### Day 6: Solution Comparison Implementation

**Focus:** Implement objective comparison with tolerance

| Task | Est. Time | Description |
|------|-----------|-------------|
| Implement tolerance comparison | 1.5h | Combined formula, edge cases |
| Create comparison decision tree | 1.5h | 7 outcomes from Task 3 |
| Handle NLP objective retrieval | 1h | From convexity_verification |
| Implement solution_comparison_result | 1h | Database storage |
| Add CLI tolerance arguments | 0.5h | --rtol, --atol |
| Test on translated models | 0.5h | Run on 5-10 MCPs |

**Deliverables:**
- Solution comparison logic in test_solve.py
- Tolerance-based matching
- Comparison results in database

**Acceptance Criteria:**
- [ ] `objectives_match()` function works correctly
- [ ] Handles objective=0 edge case (uses atol)
- [ ] Handles very large objectives (uses rtol)
- [ ] Comparison result stored with tolerances used
- [ ] Decision tree produces correct outcome categories

**Time Estimate:** 6 hours

#### Day 7: Solve Testing Complete

**Focus:** Run solve testing on all translated models, handle edge cases

| Task | Est. Time | Description |
|------|-----------|-------------|
| Add error handling for edge cases | 1.5h | NaN, Inf, missing NLP objective |
| Add solve outcome categorization | 1h | 16 solve categories from taxonomy |
| Run solve test on all 32 MCPs | 1h | Full solve batch |
| Analyze results and fix issues | 1.5h | Debug any failures |
| Generate solve summary report | 0.5h | Success rate, mismatches |
| Update documentation | 0.5h | test_solve.py usage |

**Deliverables:**
- Complete test_solve.py with all features
- Solve results for all 32 translated models
- Solve summary report

**Acceptance Criteria:**
- [ ] All 32 MCP files attempted
- [ ] Solve outcome categories assigned correctly
- [ ] Solution comparison performed for successful solves
- [ ] Mismatches flagged for investigation
- [ ] Summary report generated

**Time Estimate:** 6 hours

**Checkpoint 3 (End of Day 7):** Solve testing functional with solution comparison

---

### Phase 4: Pipeline Integration (Days 8-9)

#### Day 8: Create run_full_test.py

**Focus:** Build pipeline orchestrator with filtering

| Task | Est. Time | Description |
|------|-----------|-------------|
| Create run_full_test.py skeleton | 1h | argparse with filter arguments |
| Implement filter logic | 2h | AND combination, conflict detection |
| Implement stage orchestration | 1.5h | Parse → Translate → Solve → Compare |
| Add cascade failure handling | 1h | Mark downstream as not_tested |
| Add progress reporting | 0.5h | Per-stage progress |
| Test with subset of models | 0.5h | 5-10 models end-to-end |

**Deliverables:**
- `scripts/gamslib/run_full_test.py` (core orchestration)
- Filter framework implemented
- Cascade handling working

**Acceptance Criteria:**
- [ ] `--model=trnsport` runs single model through pipeline
- [ ] `--only-parse` runs parse stage only
- [ ] `--only-failing` re-runs failed models
- [ ] Filter conflicts detected and reported
- [ ] Cascade failures mark downstream stages correctly

**Time Estimate:** 6.5 hours

#### Day 9: Pipeline Integration and Summary

**Focus:** Complete pipeline runner with summary statistics

| Task | Est. Time | Description |
|------|-----------|-------------|
| Add summary generation | 1.5h | Per-stage stats, error breakdown |
| Add output formats | 1h | Table, JSON, quiet modes |
| Add --dry-run mode | 0.5h | Preview without execution |
| Run full pipeline on all models | 1h | Complete test run |
| Fix integration issues | 1.5h | Debug and resolve |
| Document run_full_test.py | 0.5h | Usage examples |

**Deliverables:**
- Complete run_full_test.py with all features
- Full pipeline run results
- Summary statistics

**Acceptance Criteria:**
- [ ] Full pipeline runs on all 160 verified/likely_convex models
- [ ] Summary shows parse/translate/solve/compare stats
- [ ] --dry-run previews filter results
- [ ] --verbose shows detailed progress
- [ ] --json outputs machine-readable results

**Time Estimate:** 6 hours

**Checkpoint 4 (End of Day 9):** Full pipeline operational with filtering

---

### Phase 5: Baseline and Documentation (Day 10)

#### Day 10: Establish Baseline and Complete Sprint

**Focus:** Record baseline metrics and finalize documentation

| Task | Est. Time | Description |
|------|-----------|-------------|
| Generate baseline metrics | 1h | Per-stage success rates, timing stats |
| Create baseline_metrics.json | 1h | Machine-readable baseline |
| Create SPRINT_BASELINE.md | 1h | Human-readable documentation |
| Update GAMSLIB_STATUS.md | 0.5h | Current status summary |
| Create/update GAMSLIB_TESTING.md | 1h | Testing guide documentation |
| Sprint retrospective preparation | 0.5h | Notes for summary |

**Deliverables:**
- `data/gamslib/baseline_metrics.json`
- `docs/planning/EPIC_3/SPRINT_15/SPRINT_BASELINE.md`
- Updated status documentation
- `docs/guides/GAMSLIB_TESTING.md`

**Acceptance Criteria:**
- [ ] Baseline metrics recorded for all stages
- [ ] Timing statistics documented (mean, median, p90)
- [ ] Success rates documented
- [ ] Error distribution documented
- [ ] Testing guide complete with examples

**Time Estimate:** 5 hours

**Checkpoint 5 (End of Day 10):** Baseline recorded, sprint complete

---

## Checkpoints Summary

| Checkpoint | Day | Validation Criteria |
|------------|-----|---------------------|
| **1: Schema & Taxonomy** | 2 | Schema v2.1.0 validates all entries; 44 error categories implemented |
| **2: Parse & Translate** | 4 | Filters working; refined error categories applied; statistics recorded |
| **3: Solve Testing** | 7 | PATH solver working; solution comparison functional; all MCPs tested |
| **4: Pipeline Integration** | 9 | Full pipeline runs; filters work; cascade handling correct |
| **5: Sprint Complete** | 10 | Baseline recorded; documentation complete; all tests passing |

---

## Effort Summary

| Phase | Days | Est. Hours | Components |
|-------|------|------------|------------|
| Phase 1: Foundation | 1-2 | 11h | Schema v2.1.0, error taxonomy |
| Phase 2: Parse/Translate | 3-4 | 11h | Enhanced batch scripts |
| Phase 3: Solve Testing | 5-7 | 18h | test_solve.py, comparison |
| Phase 4: Pipeline | 8-9 | 12.5h | run_full_test.py, filters |
| Phase 5: Baseline | 10 | 5h | Metrics, documentation |
| **Total** | 10 | **57.5h** | |

**Note:** Estimated 57.5 hours exceeds PROJECT_PLAN.md estimate of 26-33 hours. However, this includes:
- Infrastructure reuse savings not yet credited (~12-16h from Task 2)
- Buffer for unexpected issues
- Documentation time

**Realistic estimate with reuse:** 41-46 hours (~4-4.5 hours/day)

---

## Deliverables Checklist

From PROJECT_PLAN.md Sprint 15:

- [ ] `scripts/gamslib/test_parse.py` - Parse testing with error classification
  - Implementation: Enhance existing batch_parse.py
- [ ] `scripts/gamslib/test_translate.py` - Translation testing
  - Implementation: Enhance existing batch_translate.py
- [ ] `scripts/gamslib/test_solve.py` - Solve testing with solution comparison
  - Implementation: New script, reuse verify_convexity.py patterns
- [ ] `scripts/gamslib/run_full_test.py` - Full pipeline orchestration
  - Implementation: New script with filter framework
- [ ] Updated `data/gamslib/gamslib_status.json` with initial test results
  - Implementation: Schema v2.1.0 with all new objects
- [ ] Initial baseline metrics documented
  - Implementation: JSON + Markdown format

---

## Acceptance Criteria

From PROJECT_PLAN.md Sprint 15:

- [ ] **Parse Testing:** Can test all verified convex models and record results
- [ ] **Translation Testing:** Can translate parsed models and record results
- [ ] **Solve Testing:** Can solve translated MCPs and compare solutions
- [ ] **Pipeline Runner:** Full pipeline runs without manual intervention
- [ ] **Database Updated:** All test results recorded in gamslib_status.json
- [ ] **Error Classification:** Parse and translation errors categorized
- [ ] **Baseline Recorded:** Initial metrics available for comparison
- [ ] **Quality:** All scripts have error handling and logging

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| PATH solver integration issues | Low | High | Already validated in Task 5; fallback to GAMS error codes |
| Solution comparison edge cases | Medium | Medium | Thorough research in Task 3/9; extensive edge case handling |
| Error taxonomy incomplete | Low | Low | Can add categories during sprint; taxonomy is extensible |
| Schema migration issues | Low | Medium | Backward compatible design; test before migration |
| Filter logic complexity | Medium | Low | MVP filter set defined; defer advanced filters |
| Pipeline timing exceeds estimates | Medium | Low | Built-in buffer; can defer documentation to Day 11 |
| MCP files fail to solve | Medium | Medium | Expected based on Sprint 14 results; document failures |

### Mitigation Strategies

1. **Daily progress check:** Review checkpoint criteria at end of each day
2. **Early integration:** Test end-to-end pipeline by Day 7 (not Day 9)
3. **Incremental commits:** Commit working code daily
4. **Documentation in parallel:** Document as features are completed
5. **Scope adjustment:** If behind, prioritize core functionality over filters

---

## Resource Allocation

### By Component

| Component | Hours | Percentage |
|-----------|-------|------------|
| Schema & Infrastructure | 11h | 19% |
| Parse Testing | 6h | 10% |
| Translation Testing | 5h | 9% |
| Solve Testing | 18h | 31% |
| Pipeline Orchestration | 12.5h | 22% |
| Baseline & Documentation | 5h | 9% |

### By Activity Type

| Activity | Hours | Percentage |
|----------|-------|------------|
| Implementation | 40h | 70% |
| Testing | 10h | 17% |
| Documentation | 7.5h | 13% |

---

## Dependencies

### External Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| GAMS 51.3.0 | ✅ Available | Installed locally |
| PATH solver 5.2.01 | ✅ Validated | Demo license until Jan 23, 2026 |
| Python 3.12+ | ✅ Available | With jsonschema, requests |

### Internal Dependencies

| Dependency | Status | Required By |
|------------|--------|-------------|
| Sprint 14 database | ✅ Complete | Day 1 (migration) |
| Sprint 14 batch scripts | ✅ Complete | Day 3-4 (enhancement) |
| Schema v2.1.0 draft | ✅ Complete | Day 1 (finalization) |
| Error taxonomy | ✅ Designed | Day 2 (implementation) |
| Tolerance values | ✅ Researched | Day 6 (comparison) |

---

## Appendix A: Prep Task Cross-References

| Prep Task | Primary Output | Used In Sprint 15 |
|-----------|----------------|-------------------|
| Task 1: Known Unknowns | KNOWN_UNKNOWNS.md | Risk assessment |
| Task 2: Batch Infrastructure | batch_infrastructure_assessment.md | Days 3-4 enhancements |
| Task 3: Solution Comparison | solution_comparison_research.md | Day 6 comparison |
| Task 4: Error Taxonomy | error_taxonomy.md | Day 2 implementation |
| Task 5: PATH Solver | path_solver_integration.md | Day 5 solve testing |
| Task 6: Schema Extensions | schema_v2.1.0_draft.json | Day 1 migration |
| Task 7: Test Filtering | test_filtering_requirements.md | Day 8 pipeline |
| Task 8: Performance | performance_measurement.md | Day 10 baseline |
| Task 9: Tolerance | numerical_tolerance_research.md | Day 6 comparison |

---

## Appendix B: Unknown Resolution Status

All 26 unknowns verified during prep phase:

### Category 1: Parse Testing Infrastructure (5 unknowns)
- 1.1: ✅ Extend batch_parse.py (not replace)
- 1.2: ✅ Subcategorize syntax_error (77% of failures)
- 1.3: ✅ Binary pass/fail for parse status
- 1.4: ✅ Extract model statistics from IR
- 1.5: ✅ 16 refined parse error categories

### Category 2: Translation Testing Infrastructure (4 unknowns)
- 2.1: ✅ Extend batch_translate.py (not replace)
- 2.2: ✅ GAMS action=c for syntax validation
- 2.3: ✅ 12 translation error categories
- 2.4: ✅ MCP file output location established

### Category 3: MCP Solve Testing (7 unknowns)
- 3.1: ✅ rtol=1e-6, atol=1e-8 tolerance values
- 3.2: ✅ 7-outcome decision tree for status handling
- 3.3: ✅ Compare objectives only (not primal variables)
- 3.4: ✅ Objective-only comparison for Sprint 15
- 3.5: ✅ 16 solve outcome categories
- 3.6: ✅ PATH solver validated and configured
- 3.7: ✅ .lst file extraction patterns validated

### Category 4: Database Schema Extensions (4 unknowns)
- 4.1: ✅ 14-field mcp_solve_result object
- 4.2: ✅ 16-field solution_comparison_result object
- 4.3: ✅ Schema version 2.1.0 (minor, backward compatible)
- 4.4: ✅ Enum extension backward compatible

### Category 5: Pipeline Orchestration & Filtering (3 unknowns)
- 5.1: ✅ 14 MVP filters defined
- 5.2: ✅ Cascade failure handling with not_tested status
- 5.3: ✅ Summary statistics design complete

### Category 6: Performance & Baseline Metrics (3 unknowns)
- 6.1: ✅ Use time.perf_counter() for timing
- 6.2: ✅ Dual JSON/Markdown baseline format
- 6.3: ✅ Statistical analysis approach defined

---

## Appendix C: Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Tolerance formula | `|a-b| <= atol + rtol*max(|a|,|b|)` | Industry standard (NumPy) |
| rtol value | 1e-6 | Matches PATH, CPLEX, GUROBI |
| atol value | 1e-8 | Handles objective=0 (7.5% of models) |
| Schema version | 2.1.0 (minor) | Backward compatible |
| Filter logic | AND combination | Multiple filters all must match |
| Timing function | time.perf_counter() | Highest resolution, monotonic |
| Baseline format | JSON + Markdown | Machine + human readable |
| Error categories | 44 total (16+12+16) | Detailed analysis capability |

---

*Document created: January 13, 2026*  
*Sprint 15 Start: After this document approved*  
*Estimated Duration: 10 working days (41-46 hours with reuse)*
