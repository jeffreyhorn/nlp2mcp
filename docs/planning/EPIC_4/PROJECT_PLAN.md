# EPIC 4 Project Plan (Full GAMSLIB LP/NLP/QCP Coverage)

This plan translates `GOALS.md` into sprint-ready guidance for Sprints 18–25 (two weeks each).

**Baseline (v1.1.0 / Epic 3 Final):** Parse 61/160 (38.1%), Translate 42/61 (68.9%), Solve 12/42 (28.6%), Full Pipeline 12/160 (7.5%)

---

# Sprint 18 (Weeks 1–2): Syntactic Validation, emit_gams.py Solve Fixes & Parse Quick Wins

**Goal:** Validate GAMSLIB source correctness to establish the true valid corpus. Fix the highest-priority emit_gams.py solve blockers (deferred from Sprint 17). Pick up low-effort parse quick wins.

## Components

### GAMSLIB Syntactic Correctness Validation (~10-12h)
- **GAMS Compilation Test Script (4-5h)**
  - Create `scripts/gamslib/test_syntax.py`
  - Run `gams <model>.gms action=c` on all 160 convex models
  - Capture compilation status, error messages, and line numbers
  - Record results in database with new `gams_syntax.status` field (valid, syntax_error, compilation_error)
  - **Deliverable:** `scripts/gamslib/test_syntax.py`

- **Syntax Error Report (2-3h)**
  - Generate `data/gamslib/SYNTAX_ERROR_REPORT.md`
  - Include: model name, error type, error message, line number
  - Format suitable for GAMS team notification
  - **Deliverable:** `data/gamslib/SYNTAX_ERROR_REPORT.md`

- **Corpus Reclassification (2h)**
  - Reclassify syntax-error models as `excluded_syntax_error`
  - Review 2 `model_infeasible` models — reclassify as `excluded_infeasible` if confirmed
  - Check for unbounded models — reclassify as `excluded_unbounded`
  - Recalculate all pipeline metrics against reduced valid corpus
  - **Deliverable:** Updated `gamslib_status.json` with valid corpus denominator

- **Infeasible/Unbounded Documentation (2h)**
  - Document which models are inherently infeasible or unbounded
  - Assess whether these can produce meaningful MCP formulations
  - Add notes to database entries
  - **Deliverable:** Documented exclusions with rationale

### emit_gams.py Solve Fixes — Part 1 (~10-12h)
- **Table Data Emission (4-5h)**
  - Fix emission of GAMS table data structures in MCP output
  - Handle multi-dimensional tables with proper formatting
  - Location: `src/emit/original_symbols.py`
  - Target: ~4 models unblocked
  - **Deliverable:** Table data emission fix with regression tests

- **Computed Parameter Assignments (4-5h)**
  - Fix emission of parameter assignments involving computed values
  - Handle expressions in parameter data definitions
  - Location: `src/emit/original_symbols.py`
  - Target: ~4 models unblocked
  - **Deliverable:** Computed parameter fix with regression tests

- **Pipeline Retest (2h)**
  - Run full pipeline on all valid corpus models
  - Record updated metrics and compare to v1.1.0 baseline
  - **Deliverable:** Updated metrics

### Parse Quick Win: Put Statement Format (~2h)
- **Put Statement `:width:decimals` Syntax (2h)**
  - Add support for format specifiers in put statements
  - Models affected: ps5_s_mn, ps10_s, ps10_s_mn, stdcge
  - Grammar extension in `src/gams/gams_grammar.lark`
  - **Deliverable:** Put statement format support with unit tests

## Deliverables
- `scripts/gamslib/test_syntax.py` — GAMS compilation test script
- `data/gamslib/SYNTAX_ERROR_REPORT.md` — Syntax error report for GAMS team
- Updated `gamslib_status.json` with `gams_syntax.status` and valid corpus
- emit_gams.py fixes for table data and computed parameter emission (~8 models)
- Put statement `:width:decimals` format support (~4 models)
- Updated pipeline metrics against valid corpus

## Acceptance Criteria
- **Syntactic Validation:** All 160 models tested for GAMS compilation
- **Corpus Defined:** Valid corpus established with excluded models documented
- **emit_gams.py:** Table data and computed parameter fixes merged with tests
- **Put Statement:** Format syntax supported, 4 target models unblocked
- **Metrics:** `path_syntax_error` count reduced by ≥6 from baseline (17)
- **Quality:** All existing 3204+ tests still pass; new fixes have regression tests

**Estimated Effort:** 22-26 hours
**Risk Level:** LOW-MEDIUM (emit_gams.py fixes are well-scoped; syntax validation is straightforward)

---

# Sprint 19 (Weeks 3–4): emit_gams.py Completion & Lexer Error Analysis

**Goal:** Complete all remaining emit_gams.py solve blockers. Perform deep analysis and subcategorization of all 74 lexer_invalid_char failures to create a prioritized parse fix roadmap.

## Components

### emit_gams.py Solve Fixes — Part 2 (~10-12h)
- **Subset Relationship Preservation (4-5h)**
  - Preserve set-subset relationships when emitting domain declarations
  - Ensure subset constraints maintained in MCP output
  - Location: `src/emit/original_symbols.py`
  - Target: ~3 models unblocked
  - **Deliverable:** Subset preservation fix with regression tests

- **Reserved Word Quoting (2-3h)**
  - Quote set elements that are GAMS reserved words
  - Handle context-dependent quoting requirements
  - Location: `src/emit/expr_to_gams.py`
  - Target: ~2 models unblocked
  - **Deliverable:** Reserved word quoting fix with regression tests

- **Remaining path_syntax_error Investigation (4h)**
  - Generate and examine MCP files for remaining failing models
  - Identify new emit patterns causing GAMS compilation failures
  - Fix additional patterns as discovered
  - Target: remaining ~4 models
  - **Deliverable:** Additional emit fixes; `path_syntax_error` count < 3

### Lexer Error Deep Analysis (~8-10h)
- **Full Subcategorization of 74 Failures (5-6h)**
  - Run all 74 `lexer_invalid_char` models with verbose lexer output
  - Group by specific character/pattern triggering the error
  - Create subcategory clusters with model counts:
    - Complex set data syntax (multi-dim assignments, compound operations)
    - Compile-time constants in ranges (`1*card(s)`)
    - Implicit assignment statements
    - Numeric context in parameter data
    - Other character-level rejections
  - **Deliverable:** `docs/planning/EPIC_4/SPRINT_19/LEXER_ANALYSIS.md`

- **Prioritized Fix Roadmap (2-3h)**
  - Rank subcategories by: model count, estimated effort, dependency chain
  - Identify which clusters can be fixed independently
  - Map clusters to Sprint 20 implementation plan
  - **Deliverable:** Prioritized lexer fix roadmap

- **Initial Complex Set Data Syntax Work (2h)**
  - Begin prototyping grammar changes for the largest cluster
  - Identify scope of grammar refactoring required
  - Assess regression risk
  - **Deliverable:** Prototype/spike for complex set data handling

### Pipeline Retest (~2h)
- Run full pipeline after emit_gams.py fixes complete
- Validate solve rate improvement
- Record updated metrics
- **Deliverable:** Updated metrics; expected solve rate ≥ 45%

## Deliverables
- emit_gams.py fixes for subset preservation, reserved words, and remaining patterns
- `docs/planning/EPIC_4/SPRINT_19/LEXER_ANALYSIS.md` — Full lexer error subcategorization
- Prioritized lexer fix roadmap for Sprints 20-22
- Initial complex set data syntax prototype
- Updated pipeline metrics

## Acceptance Criteria
- **emit_gams.py:** `path_syntax_error` count reduced to < 3
- **Solve Rate:** ≥ 45% of translated models solve correctly
- **Lexer Analysis:** All 74 failures subcategorized with model counts
- **Roadmap:** Clear sprint-level plan for addressing each subcategory
- **Quality:** All tests pass; no regressions in previously-solving models

**Estimated Effort:** 20-24 hours
**Risk Level:** LOW-MEDIUM (emit fixes are targeted; analysis is research-only)

---

# Sprint 20 (Weeks 5–6): Major Parse Push (lexer_invalid_char & internal_error)

**Goal:** Major reduction in parse failures through systematic lexer and grammar fixes. Begin internal_error investigation. Design IndexOffset IR representation.

## Components

### lexer_invalid_char Fixes (~14-18h)
- **Complex Set Data Syntax (8-10h)**
  - Implement grammar changes for the largest subcategory (14+ models)
  - Handle multi-dimensional set assignments, compound set operations
  - May require restructuring data statement handling in grammar
  - Incremental changes with full regression testing after each
  - **Deliverable:** Complex set data syntax support

- **Compile-Time Constants in Ranges (3-4h)**
  - Support expressions like `1*card(s)` in set/parameter ranges
  - Grammar and possibly preprocessor changes
  - **Deliverable:** Compile-time range constant support

- **Remaining High-Priority Clusters (3-4h)**
  - Address next-highest subcategories from Sprint 19 analysis
  - Implicit assignment statements, numeric parameter contexts, etc.
  - **Deliverable:** Additional lexer fixes

### internal_error Investigation (~6-8h)
- **Error Classification (4-5h)**
  - Run all 23 `internal_error` models with debug parser output
  - Classify: grammar ambiguity, missing production, IR construction crash, transformer error
  - Identify common patterns and group by root cause
  - **Deliverable:** `docs/planning/EPIC_4/SPRINT_20/INTERNAL_ERROR_ANALYSIS.md`

- **Initial Fixes (2-3h)**
  - Fix the most common internal_error patterns
  - Focus on IR construction hardening and grammar disambiguation
  - Target: reduce from 23 to below 15
  - **Deliverable:** Initial internal_error fixes with tests

### IndexOffset IR Design (~4h)
- **IR Node Design (2h)**
  - Design `IndexOffset` node type for the IR
  - Handle lead (`t+1`), lag (`t-1`), circular (`t++1`, `t--1`)
  - Document integration points with parser, AD, KKT, and emit stages
  - **Deliverable:** IndexOffset design document

- **Parser Integration Spike (2h)**
  - Prototype parsing GAMS lead/lag syntax into IndexOffset nodes
  - Identify grammar changes needed
  - **Deliverable:** Parser spike for IndexOffset

### Pipeline Retest (~2h)
- Run full pipeline after parse fixes
- Validate parse rate improvement
- Track newly-parsed models entering translate/solve stages
- **Deliverable:** Updated metrics; expected parse rate ≥ 60% of valid corpus

## Deliverables
- Complex set data syntax support in grammar
- Compile-time range constant support
- Additional lexer fixes for high-priority subcategories
- `docs/planning/EPIC_4/SPRINT_20/INTERNAL_ERROR_ANALYSIS.md`
- Initial internal_error fixes
- IndexOffset IR design document and parser spike
- Updated pipeline metrics

## Acceptance Criteria
- **lexer_invalid_char:** Count reduced from 74 to below 30
- **internal_error (parse):** Count reduced from 23 to below 15
- **Parse Rate:** ≥ 60% of valid corpus
- **IndexOffset:** IR design documented; parser spike demonstrates feasibility
- **Quality:** All tests pass; golden file tests for 12 solving models unchanged

**Estimated Effort:** 26-32 hours
**Risk Level:** MEDIUM-HIGH (grammar refactoring for complex set data is the highest-risk item in Epic 4)

---

# Sprint 21 (Weeks 7–8): IndexOffset Implementation & Translation Improvements

**Goal:** Complete IndexOffset (lead/lag) support end-to-end. Address translation internal errors and objective extraction. Handle emerging translation blockers from improved parse rates.

## Components

### IndexOffset Implementation (~14-16h)
- **IR Node Implementation (3-4h)**
  - Implement `IndexOffset` node in IR based on Sprint 20 design
  - Handle positive/negative offsets and circular variants
  - Add IR validation and pretty-printing support
  - **Deliverable:** IndexOffset IR node with unit tests

- **Parser Integration (3-4h)**
  - Extend grammar to parse GAMS lead/lag syntax
  - Build IndexOffset nodes in transformer/visitor
  - Handle all syntactic variants: `t-1`, `t+1`, `t++1`, `t--1`
  - **Deliverable:** Parser support for lead/lag with unit tests

- **Differentiation Rules (4-5h)**
  - Implement derivative rules for IndexOffset expressions
  - Handle chain rule with shifted indices
  - Ensure KKT stationarity equations correctly reference offset indices
  - **Deliverable:** AD rules for IndexOffset with unit tests

- **Emit Support (3-4h)**
  - Generate correct GAMS lead/lag syntax in MCP output
  - Handle both `ord`-based and direct notations
  - Test against all 8 `unsup_index_offset` models
  - **Deliverable:** Emit support with integration tests

### Translation Internal Error Fixes (~6-8h)
- **Debug 5 Failing Models (3-4h)**
  - Run each model with verbose translation output
  - Identify root causes: missing derivative rules, IR gaps, KKT bugs
  - **Deliverable:** Root cause analysis for each model

- **Implement Fixes (3-4h)**
  - Fix identified root causes
  - Add regression tests for each fix
  - Target: `internal_error` (translate) count at 0
  - **Deliverable:** Translation fixes with tests

### Objective Extraction Enhancement (~4h)
- **Handle Implicit Objectives (2-3h)**
  - Improve handling of models without explicit `minimize`/`maximize`
  - Handle objective defined in constraint form
  - Address `model_no_objective_def` patterns
  - **Deliverable:** Objective extraction improvements

- **Emerging Blocker Capacity (1-2h)**
  - Address newly-discovered translation failures from improved parse
  - Track and triage as they appear
  - **Deliverable:** Fixes for emerging blockers

### Pipeline Retest (~2h)
- Run full pipeline after IndexOffset and translation fixes
- Track translation rate improvement and new solve-stage entries
- **Deliverable:** Updated metrics; expected translate rate ≥ 80%

## Deliverables
- Complete IndexOffset support (IR, parser, AD, emit) for all 8 affected models
- Translation `internal_error` fixes for 5 models
- Objective extraction enhancement for `model_no_objective_def` models
- Updated pipeline metrics

## Acceptance Criteria
- **IndexOffset:** All 8 `unsup_index_offset` models translate successfully
- **Translation Errors:** `internal_error` (translate) count at 0
- **Objective Extraction:** At least 3 of 5 `model_no_objective_def` models handled
- **Translation Rate:** ≥ 80% of parsed models translate
- **Quality:** All tests pass; IndexOffset has comprehensive unit and integration tests

**Estimated Effort:** 26-30 hours
**Risk Level:** MEDIUM (IndexOffset is a significant new IR feature; derivative rules require careful implementation)

---

# Sprint 22 (Weeks 9–10): Parse Completion & PATH Convergence Investigation

**Goal:** Push parse rate toward completion. Begin systematic investigation of PATH convergence failures. Enhance solution comparison framework.

## Components

### Parse Completion Push (~12-14h)
- **Remaining lexer_invalid_char Fixes (6-8h)**
  - Address remaining subcategories from Sprint 19 analysis
  - Handle long-tail patterns (1-2 models each)
  - Consider GAMS preprocessing for intractable patterns
  - Target: `lexer_invalid_char` below 10
  - **Deliverable:** Additional lexer/grammar fixes

- **Remaining internal_error Fixes (4-5h)**
  - Fix remaining internal_error patterns from Sprint 20 analysis
  - Grammar disambiguation and IR construction hardening
  - Target: `internal_error` (parse) below 5
  - **Deliverable:** Additional internal_error fixes

- **Semantic Error Resolution (2h)**
  - Resolve `semantic_undefined_symbol` (2 models)
  - Determine if these are GAMSLIB source issues or nlp2mcp bugs
  - If GAMSLIB issues: add to syntax error report; if bugs: fix
  - **Deliverable:** Semantic errors resolved or documented

### Emerging Translation Blockers (~4-6h)
- **Triage New Failures (2-3h)**
  - As parse rate improves, newly-parsed models enter translation
  - Identify and categorize new translation failures
  - Prioritize by model count and fix effort
  - **Deliverable:** Updated translation failure analysis

- **Fix High-Priority Blockers (2-3h)**
  - Address the most impactful new translation failures
  - May include new derivative rules, domain mismatches, etc.
  - **Deliverable:** Fixes for emerging translation blockers

### PATH Convergence Investigation (~8-10h)
- **Systematic Analysis of 11 Models (4-5h)**
  - For each `path_solve_terminated` model:
    - Examine PATH solver output and iteration log
    - Check complementarity residuals at termination
    - Test with relaxed tolerances and increased iteration limits
  - Classify: KKT correctness issue, starting point, inherent difficulty, PATH options
  - **Deliverable:** `docs/planning/EPIC_4/SPRINT_22/PATH_CONVERGENCE_ANALYSIS.md`

- **Solution Comparison Enhancement (4-5h)**
  - Extend comparison beyond objective value matching
  - Add: primal variable comparison, dual variable comparison, complementarity residuals
  - Implement combined relative/absolute tolerance with model-appropriate defaults
  - Generate detailed mismatch reports
  - **Deliverable:** Enhanced solution comparison framework with tests

### Pipeline Retest (~2h)
- Full pipeline run with updated parse and translation fixes
- Record parse, translate, and solve metrics
- **Deliverable:** Updated metrics; expected parse rate ≥ 85% of valid corpus

## Deliverables
- Additional parse fixes pushing `lexer_invalid_char` below 10
- `internal_error` (parse) below 5
- Fixes for emerging translation blockers
- `docs/planning/EPIC_4/SPRINT_22/PATH_CONVERGENCE_ANALYSIS.md`
- Enhanced solution comparison framework
- Updated pipeline metrics

## Acceptance Criteria
- **Parse Rate:** ≥ 85% of valid corpus
- **lexer_invalid_char:** Count below 10
- **internal_error (parse):** Count below 5
- **PATH Analysis:** All 11 `path_solve_terminated` models classified by root cause
- **Solution Comparison:** Framework extended with primal/dual/complementarity comparison
- **Quality:** All tests pass; no regressions

**Estimated Effort:** 26-32 hours
**Risk Level:** MEDIUM (diminishing returns on parse fixes; PATH investigation may reveal fundamental issues)

---

# Sprint 23 (Weeks 11–12): Solve Improvements & Solution Matching

**Goal:** Fix KKT bugs and PATH configuration issues identified in Sprint 22. Improve starting point initialization. Begin MCP-NLP solution divergence analysis.

## Components

### KKT Correctness Fixes (~8-10h)
- **Fix Formulation Bugs (6-8h)**
  - For models classified as "KKT correctness issue" in Sprint 22:
    - Identify the specific KKT formulation error
    - Fix stationarity, complementarity, or feasibility conditions
    - Verify fix produces correct MCP that PATH can solve
  - Each fix includes regression tests
  - **Deliverable:** KKT fixes for convergence-failing models

- **Starting Point Improvements (2-3h)**
  - For models classified as "starting point problem":
    - Implement warm-start from NLP solution values
    - Add configurable starting point strategies
    - Test alternative initialization approaches
  - **Deliverable:** Starting point initialization improvements

### PATH Solver Tuning (~4-6h)
- **Options Tuning (3-4h)**
  - For models classified as "PATH options":
    - Experiment with iteration limits, convergence tolerances
    - Test different crash methods and preprocessing options
    - Document model-specific PATH configurations that work
  - **Deliverable:** PATH options tuning guide

- **Tolerance Adjustments (1-2h)**
  - Review solution comparison tolerances across all solving models
  - Adjust per-model tolerances where needed
  - Document tolerance rationale
  - **Deliverable:** Updated tolerance configuration

### MCP-NLP Solution Divergence Analysis (~6-8h)
- **Identify Divergent Models (3-4h)**
  - For all models that solve: compare MCP solution to NLP solution
  - Identify models where solutions differ beyond tolerance
  - Classify: multiple optima, numerical precision, formulation error
  - **Deliverable:** Solution divergence report

- **Case Study Preparation (3-4h)**
  - Select 3-5 most interesting divergence cases
  - Document: original NLP, MCP formulation, both solutions, analysis
  - Begin formatting for PATH author review
  - **Deliverable:** Draft case studies for PATH consultation

### Pipeline Retest (~2h)
- Full pipeline run after KKT and PATH fixes
- Record solve metrics improvement
- **Deliverable:** Updated metrics; expected `path_solve_terminated` reduced by 50%+

## Deliverables
- KKT correctness fixes for convergence-failing models
- Starting point initialization improvements
- PATH options tuning guide
- Solution divergence analysis report
- Draft case studies for PATH author consultation
- Updated pipeline metrics

## Acceptance Criteria
- **path_solve_terminated:** Count reduced by ≥ 50% (from 11 to ≤ 5)
- **Solve Rate:** ≥ 60% of translated models solve correctly
- **Solution Analysis:** All solving models assessed for NLP/MCP match
- **Case Studies:** At least 3 divergence cases documented for consultation
- **Quality:** All tests pass; KKT fixes have comprehensive tests

**Estimated Effort:** 20-26 hours
**Risk Level:** MEDIUM-HIGH (KKT bugs may be subtle; solution divergence analysis may reveal fundamental issues requiring PATH author input)

---

# Sprint 24 (Weeks 13–14): PATH Author Consultation & Solution Forcing

**Goal:** Prepare and submit PATH author consultation document. Implement solution forcing strategies. Address remaining solve and translate failures across all pipeline stages.

## Components

### PATH Author Consultation (~8-10h)
- **Consultation Document (5-6h)**
  - Compile all case studies from Sprint 23
  - Write clear problem descriptions with mathematical formulations
  - Include: original NLP, KKT conditions, MCP formulation, solution comparison
  - Add specific questions about forcing solution agreement
  - Create `docs/research/PATH_CONSULTATION.md`
  - **Deliverable:** `docs/research/PATH_CONSULTATION.md`

- **Submit and Follow Up (2-3h)**
  - Send document to Michael Ferris and Steven Dirkse
  - Provide reproducible test cases (model files, scripts)
  - Track questions and responses
  - **Deliverable:** Consultation submitted; tracking document created

### Solution Forcing Strategies (~6-8h)
- **Implement Known Strategies (4-5h)**
  - Based on literature and any early PATH author feedback:
    - Warm-start MCP from NLP solution
    - Tighter PATH tolerances for specific model classes
    - Reformulation techniques (scaling, variable substitution)
  - Test each strategy across divergent models
  - **Deliverable:** Solution forcing implementations with tests

- **Document Strategy Effectiveness (2-3h)**
  - Record which strategies work for which model classes
  - Create decision tree for selecting forcing strategy
  - Note models that remain divergent despite all strategies
  - **Deliverable:** Strategy effectiveness documentation

### Remaining Pipeline Fixes (~6-8h)
- **Final Parse Fixes (2-3h)**
  - Address any remaining parse failures that are fixable
  - Implement GAMS preprocessing for intractable patterns if needed
  - Target: parse rate ≥ 90% of valid corpus
  - **Deliverable:** Final parse fixes

- **Final Translation Fixes (2-3h)**
  - Address remaining translation blockers
  - Handle newly-discovered patterns from late-arriving parsed models
  - Target: translate rate ≥ 85% of parsed models
  - **Deliverable:** Final translation fixes

- **Final Solve Fixes (2h)**
  - Address any remaining solvable `path_syntax_error` or `path_solve_terminated` models
  - Apply solution forcing strategies to divergent models
  - Target: solve rate ≥ 70% of translated models
  - **Deliverable:** Final solve fixes

### Pipeline Retest (~2h)
- Full pipeline run — comprehensive status check
- Record metrics for all stages
- Compare to Sprint 18 starting point and v1.1.0 baseline
- **Deliverable:** Comprehensive metrics comparison report

## Deliverables
- `docs/research/PATH_CONSULTATION.md` — PATH author consultation document
- Solution forcing strategy implementations and documentation
- Final parse, translate, and solve fixes
- Comprehensive pipeline metrics comparison

## Acceptance Criteria
- **PATH Consultation:** Document submitted to Ferris/Dirkse with reproducible cases
- **Solution Forcing:** At least 2 strategies implemented and tested
- **Parse Rate:** ≥ 90% of valid corpus
- **Translate Rate:** ≥ 85% of parsed models
- **Solve Rate:** ≥ 70% of translated models
- **Full Pipeline:** ≥ 60% of valid corpus
- **Quality:** All tests pass; all fixes have regression tests

**Estimated Effort:** 22-28 hours
**Risk Level:** MEDIUM (PATH author response timeline is uncertain; solution forcing may have limited effectiveness for some model classes)

---

# Sprint 25 (Weeks 15–16): Quality, Performance & v2.0.0 Release

**Goal:** Stabilize performance benchmarks. Incorporate any PATH author feedback. Final comprehensive pipeline run. Documentation finalization and v2.0.0 release.

## Components

### Performance Benchmark Stabilization (~6-8h)
- **Regression-Based Benchmarks (4-5h)**
  - Replace absolute wall-clock thresholds with regression detection
  - Implement: run N times, use median, compare to stored baseline
  - Add warm-up runs to reduce cold-start variance
  - Update `tests/benchmarks/test_performance.py`
  - **Deliverable:** Regression-based performance benchmarks

- **Benchmark Configuration (2-3h)**
  - Store baseline timing data in version-controlled file
  - Create script to update baseline after intentional performance changes
  - Document benchmark methodology
  - **Deliverable:** Benchmark configuration and documentation

### PATH Author Feedback Integration (~4-6h)
- **Process Responses (2-3h)**
  - Incorporate any feedback received from Ferris/Dirkse
  - Implement recommended solution forcing techniques
  - Update divergent models with new strategies
  - **Deliverable:** PATH feedback implementation

- **Update Consultation Document (2-3h)**
  - Add PATH author responses and recommendations
  - Document resolved vs. unresolved cases
  - Note any follow-up needed for Epic 5
  - **Deliverable:** Updated `docs/research/PATH_CONSULTATION.md`

### Final Pipeline Run & Assessment (~4-6h)
- **Comprehensive Retest (2-3h)**
  - Full pipeline on all valid corpus models
  - Record final metrics for every stage
  - Generate comparison: v1.1.0 baseline → Sprint 18 → final
  - **Deliverable:** Final pipeline results

- **Remaining Failure Documentation (2-3h)**
  - For every model that still fails: document root cause and category
  - Classify remaining failures as: fixable (Epic 5), inherent limitation, GAMSLIB issue
  - Create improvement roadmap for Epic 5
  - **Deliverable:** `docs/planning/EPIC_4/REMAINING_FAILURES.md`

### Documentation & Release (~8-10h)
- **Epic 4 Summary (3-4h)**
  - Create `docs/planning/EPIC_4/SUMMARY.md` with sprint-by-sprint history
  - Include cumulative metrics table and progression charts
  - Document key learnings and technical decisions
  - **Deliverable:** Epic 4 SUMMARY.md

- **Report Updates (2h)**
  - Regenerate `GAMSLIB_STATUS.md` and `FAILURE_ANALYSIS.md`
  - Update `progress_history.json` with final metrics
  - Update README.md with Epic 4 results
  - **Deliverable:** Updated reports and README

- **v2.0.0 Release (3-4h)**
  - Create v2.0.0 release notes
  - Update CHANGELOG.md
  - Version bump in pyproject.toml
  - Quality gate verification (typecheck, lint, format, test)
  - Create release commit, tag, and GitHub release
  - **Deliverable:** v2.0.0 release (tag + GitHub release)

## Deliverables
- Regression-based performance benchmarks (replacing absolute thresholds)
- PATH author feedback integration
- Final pipeline metrics and comparison report
- `docs/planning/EPIC_4/REMAINING_FAILURES.md` — Remaining failures with roadmap
- `docs/planning/EPIC_4/SUMMARY.md` — Epic summary
- Updated GAMSLIB_STATUS.md, FAILURE_ANALYSIS.md, README.md
- v2.0.0 release notes, CHANGELOG, tag, and GitHub release

## Acceptance Criteria
- **Performance Benchmarks:** No flaky CI failures from benchmark tests
- **Final Parse Rate:** ≥ 95% of valid corpus
- **Final Translate Rate:** ≥ 90% of parsed models
- **Final Solve Rate:** ≥ 80% of translated models
- **Full Pipeline:** ≥ 70% of valid corpus
- **Documentation:** Epic 4 summary, remaining failures, and release notes complete
- **Release:** v2.0.0 tagged, pushed, and GitHub release published
- **Quality:** All quality gates pass on final release

**Estimated Effort:** 22-30 hours
**Risk Level:** LOW (mostly consolidation, documentation, and release mechanics)

---

## Rolling KPIs & Tracking

### Sprint-Level KPIs

| Metric | S18 | S19 | S20 | S21 | S22 | S23 | S24 | S25 |
|--------|-----|-----|-----|-----|-----|-----|-----|-----|
| Valid Corpus Defined | ✓ | — | — | — | — | — | — | — |
| lexer_invalid_char | ~70 | ~65 | <30 | <25 | <10 | <10 | <5 | <5 |
| internal_error (parse) | ~23 | ~23 | <15 | <10 | <5 | <5 | <3 | <3 |
| path_syntax_error | <11 | <3 | <3 | <3 | <3 | <3 | <2 | <2 |
| path_solve_terminated | 11 | 11 | 11 | 11 | classified | ≤5 | ≤3 | ≤3 |
| Parse Rate (valid corpus) | ~42% | ~42% | ≥60% | ≥70% | ≥85% | ≥85% | ≥90% | ≥95% |
| Translate Rate (of parsed) | ~69% | ~69% | ~72% | ≥80% | ≥82% | ≥85% | ≥85% | ≥90% |
| Solve Rate (of translated) | ~40% | ≥45% | ≥45% | ≥48% | ≥50% | ≥60% | ≥70% | ≥80% |
| Full Pipeline (valid corpus) | ~12% | ~14% | ≥20% | ≥30% | ≥40% | ≥50% | ≥60% | ≥70% |

### Dashboard Updates
- `data/gamslib/GAMSLIB_STATUS.md` — Updated after each pipeline retest
- `data/gamslib/progress_history.json` — Updated after each sprint
- Reports regenerated via `scripts/gamslib/generate_report.py`

---

## Risk Mitigation Summary

| Risk | Impact | Probability | Sprints Affected | Mitigation |
|------|--------|-------------|------------------|------------|
| Grammar refactoring regressions | HIGH | HIGH | 20, 22 | 3204+ test suite; golden files for 12 solving models; incremental changes |
| Stacked blockers in models | HIGH | HIGH | 20-24 | Track blockers removed, not just models unblocked |
| MCP-NLP solution divergence | HIGH | MEDIUM | 23-25 | PATH author consultation; multiple forcing strategies |
| PATH author availability | MEDIUM | MEDIUM | 24-25 | Self-contained case studies; batch questions; literature fallback |
| Diminishing returns on parse | MEDIUM | MEDIUM | 22-24 | Subcategorize before implementing; preprocessing fallback |
| IndexOffset complexity | MEDIUM | MEDIUM | 20-21 | Design first (S20), implement second (S21); spike validates feasibility |
| Infeasible MCP formulations | MEDIUM | LOW-MEDIUM | 23-25 | PATH consultation; document as inherent limitations |

---

## Dependencies & Prerequisites

### External Dependencies
- GAMS software installed locally (with valid license)
- PATH solver available (version 5.2+)
- Internet access for GAMS team communication
- PATH author availability (Michael Ferris, Steven Dirkse) — needed by Sprint 24

### Internal Dependencies
- Epic 3 deliverables: GAMSLIB infrastructure, pipeline scripts, reporting tools
- v1.1.0 as stable baseline (219 models cataloged, 160 verified convex, 12 solving)
- Error taxonomy (47 categories) for consistent failure tracking
- Quality gate infrastructure (typecheck, lint, format, 3204+ tests)

### Sprint-to-Sprint Dependencies
- Sprint 19 depends on Sprint 18 (emit_gams.py completion builds on Part 1)
- Sprint 20 depends on Sprint 19 (lexer analysis informs parse fix priorities)
- Sprint 21 depends on Sprint 20 (IndexOffset design feeds implementation)
- Sprint 23 depends on Sprint 22 (PATH analysis feeds KKT fixes)
- Sprint 24 depends on Sprint 23 (case studies feed consultation document)
- Sprint 25 depends on Sprint 24 (PATH feedback integration)

---

## Changelog

- **2026-02-05:** Initial EPIC_4 project plan created
