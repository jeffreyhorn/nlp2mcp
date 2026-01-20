# Sprint 15 Deliverables and Learnings Review

**Created:** January 20, 2026  
**Purpose:** Consolidate learnings from Sprint 15 to inform Sprint 16 approach  
**Related Task:** Sprint 16 Prep Task 9

---

## Executive Summary

Sprint 15 was a 10-day sprint that established comprehensive pipeline testing infrastructure for GAMSLIB models. It delivered the full parse → translate → solve → compare pipeline with PATH solver integration, establishing baseline metrics that guide Sprint 16 improvements.

**Key Outcome:** 1/160 models (0.6%) achieve full pipeline success, with clear blockers identified at each stage.

---

## Sprint 15 Deliverables Summary

### 1. Pipeline Testing Infrastructure

| Deliverable | Description | Location |
|-------------|-------------|----------|
| `run_full_test.py` | Pipeline orchestrator with 14 MVP filter arguments | `scripts/gamslib/` |
| `test_solve.py` | MCP solve testing with PATH solver integration | `scripts/gamslib/` |
| `error_taxonomy.py` | 47 outcome categories (16 parse + 13 translate + 16 solve + 2 generic) | `scripts/gamslib/` |
| `baseline_metrics.json` | Machine-readable baseline metrics | `data/gamslib/` |
| Schema v2.1.0 | Added `mcp_solve` and `solution_comparison` objects | `data/gamslib/schema.json` |

### 2. Documentation

| Document | Description | Location |
|----------|-------------|----------|
| `SPRINT_BASELINE.md` | Human-readable baseline with analysis | `docs/planning/EPIC_3/SPRINT_15/` |
| `GAMSLIB_TESTING.md` | Comprehensive testing guide | `docs/guides/` |
| `GAMSLIB_CONVERSION_STATUS.md` | Updated status dashboard | `docs/status/` |

### 3. Baseline Metrics Established

| Stage | Attempted | Success | Rate |
|-------|-----------|---------|------|
| Parse | 160 | 34 | 21.3% |
| Translate | 34 | 17 | 50.0% |
| Solve | 17 | 3 | 17.6% |
| Compare | 3 | 1 match | 33.3% |
| **Full Pipeline** | **160** | **1** | **0.6%** |

### 4. Error Taxonomy

**47 error categories** established across pipeline stages:
- Parse: 16 categories (dominated by `lexer_invalid_char`: 109 models, 86.5%)
- Translate: 13 categories (top: `model_no_objective_def`: 5, `diff_unsupported_func`: 5)
- Solve: 16 categories (100% are `path_syntax_error`: 14 models)
- Generic: 2 categories

### 5. New Tests Added

| Area | Tests Added |
|------|-------------|
| error_taxonomy | 92 |
| batch_parse | 14 |
| batch_translate | 18 |
| test_solve | 72 |
| **Total** | **196** |

---

## Key Learnings

### Learning 1: Cascade Failures Dominate Pipeline Success

**Observation:** Only 0.6% of models (1/160) complete the full pipeline. This is because failures cascade - a parse failure prevents all downstream stages.

**Impact Analysis:**
- 126 models (78.8%) fail at parse → cannot translate, solve, or compare
- 17 models fail at translate → cannot solve or compare
- 14 models fail at solve → cannot compare

**Implication for Sprint 16:** Fixing parse-stage blockers has the highest leverage. Each model unblocked at parse enables potential success in all downstream stages.

### Learning 2: Single Error Category Dominates Parse Failures

**Observation:** `lexer_invalid_char` accounts for 86.5% of parse failures (109/126 models).

**Root Cause Analysis (from Sprint 16 prep):**
- NOT dollar control (already handled by `%ignore` pattern)
- Actual causes: hyphenated set elements, tuple expansion syntax, keyword case variations

**Implication for Sprint 16:** Focused effort on extending grammar for GAMS data syntax could unblock 50-80 models.

### Learning 3: PATH Solver Integration Works Reliably

**Observation:** PATH solver integration via GAMS subprocess proved robust. Solve timing is consistent (mean: 172.7ms, stddev: 7.1ms).

**What Worked Well:**
- `.lst` file parsing for status extraction
- Combined tolerance formula for objective comparison (rtol=1e-6, atol=1e-8)
- Decision tree for compare outcomes (7 outcomes)

**Implication for Sprint 16:** Solve infrastructure is stable; improvements should focus on upstream stages.

### Learning 4: MCP Code Generation Has Systematic Issues

**Observation:** 100% of solve failures (14/14 models) are `path_syntax_error` - GAMS compilation errors in generated MCP files.

**Root Cause Analysis (from Sprint 16 prep Task 7):**
- Unary minus formatting: `-(expr)` should be `(-1)*(expr)` (10 models)
- Set element quoting inconsistencies (3 models)
- Scalar declaration issues (1 model)

**Implication for Sprint 16:** Fixing `src/emit/emit_gams.py` could improve solve rate from 17.6% to 76-100%.

### Learning 5: Filter Framework Enables Efficient Debugging

**Observation:** The 14 MVP filter arguments in `run_full_test.py` proved invaluable for targeted testing.

**Most Useful Filters:**
- `--only-failing` - Re-run only failed models
- `--type LP|NLP|QCP` - Focus on specific model types
- `--parse-success` / `--translate-success` - Stage-specific filtering
- `--verbose` / `--json` - Output format control

**Implication for Sprint 16:** Build on this pattern for reporting infrastructure.

### Learning 6: Timing Statistics Require Scope Clarity

**Observation:** Initial confusion about timing statistics scope (all models vs. successful only).

**Resolution:** Timing statistics are computed only for successful models at each stage:
- Parse timing: 34 successful models
- Translate timing: 17 successful models
- Solve timing: 3 successful models

**Implication for Sprint 16:** Document timing scope clearly in generated reports.

### Learning 7: Translation Success Rate Higher Than Expected

**Observation:** 50% translation success rate (17/34) is better than anticipated.

**Analysis:** Models that successfully parse tend to have simpler structures that also translate well. The harder models (complex syntax) fail earlier at parse.

**Implication for Sprint 16:** As more models pass parse stage, translation failures may increase proportionally.

---

## What Worked Well

1. **Comprehensive prep phase (10 tasks)** - Eliminated implementation surprises
2. **PATH solver integration** - Smooth setup with GAMS 51.3.0
3. **Error taxonomy design** - 47 categories provide precise debugging
4. **Filter framework** - 14 MVP filters enable flexible testing
5. **Cascade failure handling** - Clear propagation through pipeline stages
6. **Machine-readable output** - JSON baseline enables automated comparison
7. **Daily checkpoints** - Steady progress with clear milestones

## What Was Challenging

1. **Parse rate reality check** - Initial expectations of 30%+ were too optimistic
2. **Timing scope ambiguity** - Needed clarification mid-sprint
3. **Error categorization granularity** - Balancing detail vs. actionability
4. **Solution tolerance tuning** - Finding right rtol/atol for objective comparison

## What Would Be Done Differently

1. **Earlier error analysis** - Understanding lexer errors deeply before Sprint 15 would have informed expectations
2. **Smaller error categories initially** - Could have started with fewer categories and expanded
3. **More incremental testing** - Running full pipeline more frequently during development

---

## Recommendations for Sprint 16

### Recommendation 1: Prioritize Parse Stage Improvements

**Rationale:** Parse stage has 78.8% failure rate; fixing it unblocks all downstream stages.

**Specific Targets:**
- Keyword case handling (`Free Variable`) - 9 models, low effort
- Hyphenated set elements with numbers - 3+ models, low effort
- Tuple expansion syntax `(a,b).c` - 12 models, medium effort
- Numeric context in parameter data - 11 models, medium effort

**Expected Impact:** +20-30% parse rate (from 21.3% to 41-51%)

### Recommendation 2: Fix MCP Code Generation Bugs

**Rationale:** 100% of solve failures are code generation bugs in `emit_gams.py`.

**Specific Fixes:**
- Unary minus formatting - 10 models
- Set element quoting - 3 models
- Scalar declaration - 1 model

**Expected Impact:** Solve rate from 17.6% to 76-100%

### Recommendation 3: Leverage Error Taxonomy for Gap Analysis

**Rationale:** 47-category taxonomy enables precise targeting of improvements.

**Approach:**
- Generate failure analysis report grouping by error category
- Calculate models affected × fix effort for prioritization
- Track improvements against baseline

### Recommendation 4: Build on Filter Framework for Reporting

**Rationale:** Filter framework in `run_full_test.py` is battle-tested.

**Implementation:**
- Use similar patterns in `generate_report.py`
- Reuse data loading and filtering logic
- Add Jinja2 templates for Markdown/JSON output

### Recommendation 5: Defer Translation Improvements to Sprint 17

**Rationale:** Translation failures are diverse (6 categories) and require significant effort.

**Sprint 16 Focus:**
- Parse improvements (highest leverage)
- Solve/emit fixes (quick wins)
- Reporting infrastructure

**Sprint 17 Focus:**
- `model_no_objective_def` handling
- `diff_unsupported_func` (new derivative rules)
- `unsup_index_offset` (index arithmetic)

---

## Technical Debt Identified

### TD-1: Translate Success Rate Discrepancy

**Issue:** Sprint 14 reported 94.1% translate success (32/34), but Sprint 15 reported 50% (17/34).

**Explanation:** Sprint 15 introduced stricter validation with 47-category taxonomy. 15 models reclassified from "success" to specific error categories.

**Recommendation:** Document this explicitly in reporting to avoid confusion.

### TD-2: Path Syntax Error Naming

**Issue:** `path_syntax_error` name is misleading - suggests PATH solver issue, but actually means GAMS compilation error.

**Recommendation:** Consider renaming to `gams_compilation_error` or `mcp_syntax_error` for clarity.

### TD-3: Missing Model Type Analysis

**Issue:** Parse success varies by model type (NLP: 27.7%, LP: 8.8%, QCP: 33.3%) but root causes not fully analyzed.

**Recommendation:** Investigate why LP models have lower parse rate than NLP.

---

## Appendix: Sprint 15 Timeline

| Day | Focus | Key Outcome |
|-----|-------|-------------|
| Day 0 | Setup | Verified Sprint 14 deliverables, PATH solver availability |
| Day 1 | Schema | Updated to v2.1.0 with mcp_solve and solution_comparison |
| Day 2 | Taxonomy | Created error_taxonomy.py with 47 categories |
| Day 3 | Parse | Enhanced batch_parse.py with filter flags |
| Day 4 | Translate | Enhanced batch_translate.py, validated 17/34 success |
| Day 5 | Solve core | Created test_solve.py with PATH invocation |
| Day 6 | Comparison | Implemented objectives_match() and compare_solutions() |
| Day 7 | Solve complete | Ran on 17 MCPs: 3 success, 14 path_syntax_error |
| Day 8 | Orchestrator | Created run_full_test.py with 14 filters |
| Day 9 | Integration | Full pipeline on 160 models |
| Day 10 | Baseline | Created baseline_metrics.json, SPRINT_BASELINE.md |

---

## References

- [SPRINT_BASELINE.md](../SPRINT_15/SPRINT_BASELINE.md) - Detailed baseline metrics
- [GAMSLIB_TESTING.md](../../../guides/GAMSLIB_TESTING.md) - Testing guide
- [baseline_metrics.json](../../../../data/gamslib/baseline_metrics.json) - Machine-readable baseline
- [Epic 3 Summary](../SUMMARY.md) - Sprint 13-15 overview
