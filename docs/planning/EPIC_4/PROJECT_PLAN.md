# EPIC 4 Project Plan (Full GAMSLIB LP/NLP/QCP Coverage)

This plan translates `GOALS.md` into sprint-ready guidance for Sprints 18–25 (two weeks each, with Sprint 18 expanded to three weeks based on prep task findings).

**Baseline (v1.1.0 / Epic 3 Final):** Parse 61/160 (38.1%), Translate 42/61 (68.9%), Solve 12/42 (28.6%), Full Pipeline 12/160 (7.5%)

---

# Sprint 18 (Weeks 1–3): Syntactic Validation, emit_gams.py Solve Fixes, Parse Quick Wins & Lexer Analysis

**Goal:** Validate GAMSLIB source correctness. Fix all emit_gams.py solve blockers including MCP formulation bugs. Pick up parse quick wins. Complete lexer error analysis and create prioritized fix roadmap.

**Note:** Sprint 18 scope was expanded to ~56h across 14 working days (~3 weeks) by pulling items from Sprint 19 based on prep task findings that reduced original scope (zero syntax errors, zero table data issues).

## Components

### GAMSLIB Syntactic Correctness Validation (~4h)
- **GAMS Compilation Test Script (2.5h)**
  - Create `scripts/gamslib/test_syntax.py`
  - Run `gams <model>.gms action=c` on all 160 convex models
  - Record results in database with new `gams_syntax.status` field
  - **Deliverable:** `scripts/gamslib/test_syntax.py`

- **Schema Updates (1.5h)**
  - Add `gams_syntax` and `exclusion` fields to schema
  - Version bump to schema 2.1.0
  - **Deliverable:** Updated schema

### emit_gams.py Solve Fixes (~18h)
- **Set Element Quoting (2.5h)**
  - Quote set elements used as symbols in emitted GAMS code
  - Location: `src/emit/expr_to_gams.py`
  - Target: 6 models (ps2_f, ps2_f_eff, ps2_f_inf, ps2_f_s, ps2_s, pollut)
  - **Deliverable:** Set element quoting fix with regression tests

- **Computed Parameter Skip (2h)**
  - Skip computed parameter assignments (emit empty string)
  - Location: `src/emit/original_symbols.py` (orchestrated by emit_gams.py)
  - Target: 5 models (ajax, demo1, mathopt1, mexss, sample)
  - **Deliverable:** Computed parameter skip with regression tests

- **Bound Multiplier Dimension Fix (4h)**
  - Fix dimension handling for scalar variable bound multipliers
  - Location: `src/kkt/assemble.py`, `src/emit/model.py`
  - Target: 3-5 models (alkyl, bearing, + partial overlaps)
  - **Deliverable:** Bound multiplier fix with regression tests

- **Reserved Word Quoting (2.5h)**
  - Quote identifiers that are GAMS reserved words
  - Location: `src/emit/expr_to_gams.py`
  - Target: ~2 models
  - **Deliverable:** Reserved word quoting fix with regression tests

- **Subset Relationship Preservation (4h)**
  - Preserve set-subset relationships in emitted domain declarations
  - Location: `src/emit/emit_gams.py`, `src/emit/model.py`
  - Target: ~3 models
  - **Deliverable:** Subset preservation fix with regression tests

- **Remaining path_syntax_error Investigation (3h)**
  - Investigate and fix remaining syntax errors after initial fixes
  - Target: ~4 additional models
  - **Deliverable:** Additional emit fixes; documented intractable cases

### MCP Infeasibility Bug Fixes (~4h)
- **circle Model Fix (2.5h)**
  - Fix `uniform()` random data regeneration issue
  - Capture original random values for MCP context
  - **Deliverable:** circle achieves `model_optimal`

- **house Model Fix (1.5h)**
  - Fix constraint qualification or Lagrangian formulation issue
  - **Deliverable:** house achieves `model_optimal`

### Parse Quick Win: Put Statement Format (~2.5h)
- **Put Statement `:width:decimals` Syntax (2h)**
  - Add support for format specifiers in put statements
  - Models affected: ps5_s_mn, ps10_s, ps10_s_mn
  - Grammar extension in `src/gams/gams_grammar.lark`
  - **Deliverable:** Put statement format support with unit tests

- **Put Statement No-Semicolon Variant (0.5h)**
  - Handle `loop(j, put j.tl)` pattern for stdcge
  - **Deliverable:** stdcge parses successfully

### Parse Error Deep Analysis (~5.5h)
- **Full Subcategorization of 99 Parse Failures (4h)**
  - Run all 99 parse-stage failure models with verbose output
  - Group by error type (lexer_invalid_char, internal_error, semantic_undefined_symbol)
  - Create subcategory clusters with model counts
  - **Deliverable:** `LEXER_ERROR_ANALYSIS.md`

- **Prioritized Fix Roadmap (1.5h)**
  - Rank subcategories by model count and estimated effort
  - Map clusters to future sprint implementation
  - **Deliverable:** `FIX_ROADMAP.md`

### Initial Complex Set Data Syntax (~2h)
- **Pattern Investigation (1h)**
  - Identify complex set data syntax patterns
  - **Deliverable:** Pattern identification

- **Simple Case Implementation (1h)**
  - Implement grammar support for simple cases
  - **Deliverable:** Initial grammar additions

### Integration & Documentation (~7h)
- **Pipeline Retest (2.5h)**
  - Full pipeline on all 160 models
  - Record updated metrics
  - **Deliverable:** Updated `gamslib_status.json`

- **Documentation Updates (3h)**
  - Update GAMSLIB_STATUS.md, FAILURE_ANALYSIS.md
  - Update KNOWN_UNKNOWNS.md with resolved items
  - **Deliverable:** Updated documentation

- **Release Prep (1.5h)**
  - Version bump to v1.2.0
  - Create release notes and PR
  - **Deliverable:** v1.2.0 release

## Deliverables
- `scripts/gamslib/test_syntax.py` — GAMS compilation test script
- emit_gams.py fixes: set quoting, computed params, bound multipliers, reserved words, subsets (~20 models)
- MCP bug fixes for circle and house (2 models)
- Put statement format support (4 models)
- `LEXER_ERROR_ANALYSIS.md` — Comprehensive lexer error analysis
- `FIX_ROADMAP.md` — Prioritized fix roadmap for future sprints
- Initial complex set data syntax support
- v1.2.0 release

## Acceptance Criteria
- **Syntactic Validation:** All 160 models tested (expect 160/160 valid)
- **emit_gams.py:** All solve blockers fixed; `path_syntax_error` reduced to ≤2
- **MCP Fixes:** circle and house achieve `model_optimal`
- **Parse:** Put statement format supported, 4 models unblocked
- **Analysis:** Lexer errors fully subcategorized; fix roadmap created
- **Metrics:** Solve ≥22 models (up from 12); `model_infeasible` at 0
- **Quality:** All 3204+ tests pass; new fixes have regression tests

**Estimated Effort:** ~56 hours
**Risk Level:** MEDIUM (expanded scope but well-analyzed; MCP bugs may require investigation)

---

# Sprint 19 (Weeks 3–4): Major Parse Push (lexer_invalid_char & internal_error)

**Goal:** Major reduction in parse failures through systematic lexer and grammar fixes based on Sprint 18 analysis. Begin internal_error investigation. Design IndexOffset IR representation. Complete deferred Sprint 18 items.

**Note:** Sprint 19 now focuses on parse improvements, building on emit_gams.py fixes and initial lexer analysis completed in Sprint 18. It also covers remaining lexer error deep-dive work and items deferred from Sprint 18 due to architectural limitations discovered during that sprint.

## Components

### Sprint 18 Deferred Items (~17-21h)

These items were originally planned for Sprint 18 but were deferred when architectural limitations (cross-indexed sums, table parsing) were discovered. The sprint pivoted to focus on high-ROI emission fixes instead.

- **MCP Infeasibility Bug Fixes (3-4h)**
  - **circle Model Fix:** Fix `uniform()` random data regeneration issue; capture original random values for MCP context
  - **house Model Fix:** Fix constraint qualification or Lagrangian formulation issue
  - Target: Both models achieve `model_optimal`
  - **Deliverable:** MCP bug fixes with tests

- **Subset Relationship Preservation (4-5h)**
  - Preserve set-subset relationships in emitted domain declarations
  - Location: `src/emit/emit_gams.py`, `src/emit/model.py`
  - Target: ~3 models affected
  - **Deliverable:** Subset preservation fix with regression tests

- **Reserved Word Quoting (2-3h)**
  - Quote identifiers that are GAMS reserved words in emitted code
  - Location: `src/emit/expr_to_gams.py`
  - Target: ~2 models affected
  - **Deliverable:** Reserved word quoting fix with regression tests

- **Lexer Error Deep Analysis (5-6h)**
  - Full subcategorization of remaining parse failures
  - Run all parse-stage failure models with verbose output
  - Group by error type and create subcategory clusters
  - **Deliverable:** `LEXER_ERROR_ANALYSIS.md` with error categories and fix priorities

- **Put Statement Format Support (2.5h)**
  - Add support for `:width:decimals` format specifiers in put statements
  - Grammar extension in `src/gams/gams_grammar.lark`
  - Handle `loop(j, put j.tl)` pattern (no-semicolon variant)
  - Target: 4 models (ps5_s_mn, ps10_s, ps10_s_mn, stdcge)
  - **Deliverable:** Put statement format support with unit tests

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
  - Address next-highest subcategories from Sprint 18 analysis
  - Implicit assignment statements, numeric parameter contexts, etc.
  - **Deliverable:** Additional lexer fixes

### internal_error Investigation (~6-8h)
- **Error Classification (4-5h)**
  - Run all 23 `internal_error` models with debug parser output
  - Classify: grammar ambiguity, missing production, IR construction crash, transformer error
  - Identify common patterns and group by root cause
  - **Deliverable:** `docs/planning/EPIC_4/SPRINT_19/INTERNAL_ERROR_ANALYSIS.md`

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
- **Deliverable:** Updated metrics; expected parse rate ≥ 55% of valid corpus

## Deliverables
- **Sprint 18 Deferred Items:**
  - MCP bug fixes for circle and house models
  - Subset relationship preservation fix
  - Reserved word quoting fix
  - `LEXER_ERROR_ANALYSIS.md` with error categories
  - Put statement format support (4 models)
- **Parse Improvements:**
  - Complex set data syntax support in grammar
  - Compile-time range constant support
  - Additional lexer fixes for high-priority subcategories
  - `docs/planning/EPIC_4/SPRINT_19/INTERNAL_ERROR_ANALYSIS.md`
  - Initial internal_error fixes
  - IndexOffset IR design document and parser spike
- Updated pipeline metrics

## Acceptance Criteria
- **Sprint 18 Deferred:** circle and house achieve `model_optimal`; put statement models parse
- **lexer_invalid_char:** Count reduced from ~95 to below 50
- **internal_error (parse):** Count reduced from 23 to below 15
- **Parse Rate:** ≥ 55% of valid corpus
- **IndexOffset:** IR design documented; parser spike demonstrates feasibility
- **Quality:** All tests pass; golden file tests for solving models unchanged

**Estimated Effort:** 43-55 hours (original 26-32h + 17-23h deferred items)
**Risk Level:** MEDIUM-HIGH (grammar refactoring for complex set data is the highest-risk item in Epic 4)

---

# Sprint 20 (Weeks 5–6): IndexOffset Implementation & Translation Improvements

**Goal:** Complete IndexOffset (lead/lag) support end-to-end based on Sprint 19 design. Address translation internal errors and objective extraction. Handle emerging translation blockers from improved parse rates.

**Note:** IndexOffset design from Sprint 19; implementation now in Sprint 20.

## Components

### IndexOffset Implementation (~14-16h)
- **IR Node Implementation (3-4h)**
  - Implement `IndexOffset` node in IR based on Sprint 19 design
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
- **Deliverable:** Updated metrics; expected translate rate ≥ 75%

## Deliverables
- Complete IndexOffset support (IR, parser, AD, emit) for all 8 affected models
- Translation `internal_error` fixes for 5 models
- Objective extraction enhancement for `model_no_objective_def` models
- Updated pipeline metrics

## Acceptance Criteria
- **IndexOffset:** All 8 `unsup_index_offset` models translate successfully
- **Translation Errors:** `internal_error` (translate) count at 0
- **Objective Extraction:** At least 3 of 5 `model_no_objective_def` models handled
- **Translation Rate:** ≥ 75% of parsed models translate
- **Quality:** All tests pass; IndexOffset has comprehensive unit and integration tests

**Estimated Effort:** 26-30 hours
**Risk Level:** MEDIUM (IndexOffset is a significant new IR feature; derivative rules require careful implementation)

---

# Sprint 21 (Weeks 7–8): Parse Completion & PATH Convergence Investigation

**Goal:** Push parse rate toward completion. Begin systematic investigation of PATH convergence failures. Enhance solution comparison framework.

**Note:** IndexOffset implementation completed in Sprint 20; Sprint 21 focuses on parse completion and solve investigation.

## Components

### Parse Completion Push (~12-14h)
- **Remaining lexer_invalid_char Fixes (6-8h)**
  - Address remaining subcategories from Sprint 18 analysis
  - Handle long-tail patterns (1-2 models each)
  - Consider GAMS preprocessing for intractable patterns
  - Target: `lexer_invalid_char` below 15
  - **Deliverable:** Additional lexer/grammar fixes

- **Remaining internal_error Fixes (4-5h)**
  - Fix remaining internal_error patterns from Sprint 19 analysis
  - Grammar disambiguation and IR construction hardening
  - Target: `internal_error` (parse) below 8
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
  - **Deliverable:** `docs/planning/EPIC_4/SPRINT_21/PATH_CONVERGENCE_ANALYSIS.md`

- **Solution Comparison Enhancement (4-5h)**
  - Extend comparison beyond objective value matching
  - Add: primal variable comparison, dual variable comparison, complementarity residuals
  - Implement combined relative/absolute tolerance with model-appropriate defaults
  - Generate detailed mismatch reports
  - **Deliverable:** Enhanced solution comparison framework with tests

### Pipeline Retest (~2h)
- Full pipeline run with updated parse and translation fixes
- Record parse, translate, and solve metrics
- **Deliverable:** Updated metrics; expected parse rate ≥ 75% of valid corpus

## Deliverables
- Additional parse fixes pushing `lexer_invalid_char` below 15
- `internal_error` (parse) below 8
- Fixes for emerging translation blockers
- `docs/planning/EPIC_4/SPRINT_21/PATH_CONVERGENCE_ANALYSIS.md`
- Enhanced solution comparison framework
- Updated pipeline metrics

## Acceptance Criteria
- **Parse Rate:** ≥ 75% of valid corpus
- **lexer_invalid_char:** Count below 15
- **internal_error (parse):** Count below 8
- **PATH Analysis:** All 11 `path_solve_terminated` models classified by root cause
- **Solution Comparison:** Framework extended with primal/dual/complementarity comparison
- **Quality:** All tests pass; no regressions

**Estimated Effort:** 26-32 hours
**Risk Level:** MEDIUM (diminishing returns on parse fixes; PATH investigation may reveal fundamental issues)

---

# Sprint 22 (Weeks 9–10): Solve Improvements & Solution Matching

**Goal:** Fix KKT bugs and PATH configuration issues identified in Sprint 21. Improve starting point initialization. Begin MCP-NLP solution divergence analysis.

**Note:** PATH convergence analysis from Sprint 21; fixes now in Sprint 22.

## Components

### KKT Correctness Fixes (~8-10h)
- **Fix Formulation Bugs (6-8h)**
  - For models classified as "KKT correctness issue" in Sprint 21:
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

### Parse Completion Final Push (~4h)
- **Long-Tail Parse Fixes (2-3h)**
  - Address remaining parse failures with tractable fixes
  - Target: parse rate ≥ 85%
  - **Deliverable:** Additional parse fixes

- **Document Intractable Cases (1-2h)**
  - Document models requiring GAMS preprocessing or major grammar work
  - Add to Epic 5 backlog
  - **Deliverable:** Intractable cases documentation

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
- **Solve Rate:** ≥ 55% of translated models solve correctly
- **Solution Analysis:** All solving models assessed for NLP/MCP match
- **Case Studies:** At least 3 divergence cases documented for consultation
- **Parse Rate:** ≥ 85% of valid corpus
- **Quality:** All tests pass; KKT fixes have comprehensive tests

**Estimated Effort:** 24-30 hours
**Risk Level:** MEDIUM-HIGH (KKT bugs may be subtle; solution divergence analysis may reveal fundamental issues requiring PATH author input)

---

# Sprint 23 (Weeks 11–12): PATH Author Consultation & Solution Forcing

**Goal:** Prepare and submit PATH author consultation document. Implement solution forcing strategies. Address remaining solve and translate failures across all pipeline stages.

**Note:** Case studies from Sprint 22; consultation submission now in Sprint 23.

## Components

### PATH Author Consultation (~8-10h)
- **Consultation Document (5-6h)**
  - Compile all case studies from Sprint 22
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
  - Target: solve rate ≥ 65% of translated models
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
- **Solve Rate:** ≥ 65% of translated models
- **Full Pipeline:** ≥ 55% of valid corpus
- **Quality:** All tests pass; all fixes have regression tests

**Estimated Effort:** 22-28 hours
**Risk Level:** MEDIUM (PATH author response timeline is uncertain; solution forcing may have limited effectiveness for some model classes)

---

# Sprint 24 (Weeks 13–14): Quality, Performance & PATH Feedback Integration

**Goal:** Stabilize performance benchmarks. Incorporate any PATH author feedback. Final comprehensive pipeline run. Begin documentation finalization.

**Note:** PATH consultation submitted in Sprint 23; feedback integration now in Sprint 24.

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

### Documentation Foundation (~6-8h)
- **Epic 4 Summary Draft (3-4h)**
  - Begin `docs/planning/EPIC_4/SUMMARY.md` with sprint-by-sprint history
  - Include cumulative metrics table and progression
  - Document key learnings and technical decisions
  - **Deliverable:** Draft Epic 4 SUMMARY.md

- **Report Updates (3-4h)**
  - Regenerate `GAMSLIB_STATUS.md` and `FAILURE_ANALYSIS.md`
  - Update `progress_history.json` with metrics
  - **Deliverable:** Updated reports

### Pipeline Retest (~2h)
- Full pipeline run with PATH feedback integration
- Record final metrics
- **Deliverable:** Updated metrics; expected full pipeline ≥ 65%

## Deliverables
- Regression-based performance benchmarks (replacing absolute thresholds)
- PATH author feedback integration
- Final pipeline metrics and comparison report
- `docs/planning/EPIC_4/REMAINING_FAILURES.md` — Remaining failures with roadmap
- Draft Epic 4 SUMMARY.md
- Updated GAMSLIB_STATUS.md, FAILURE_ANALYSIS.md

## Acceptance Criteria
- **Performance Benchmarks:** No flaky CI failures from benchmark tests
- **Final Parse Rate:** ≥ 92% of valid corpus
- **Final Translate Rate:** ≥ 88% of parsed models
- **Final Solve Rate:** ≥ 75% of translated models
- **Full Pipeline:** ≥ 65% of valid corpus
- **Documentation:** Remaining failures documented; Epic 4 summary drafted
- **Quality:** All quality gates pass

**Estimated Effort:** 22-30 hours
**Risk Level:** LOW-MEDIUM (mostly consolidation; PATH feedback timing uncertain)

---

# Sprint 25 (Weeks 15–16): v2.0.0 Release & Epic 5 Planning

**Goal:** Complete Epic 4 with v2.0.0 release. Finalize all documentation. Plan Epic 5 based on remaining failures and new opportunities.

**Note:** Performance benchmarks and PATH feedback integration completed in Sprint 24; Sprint 25 focuses on release and forward planning.

## Components

### Documentation Finalization (~8-10h)
- **Epic 4 Summary Completion (3-4h)**
  - Finalize `docs/planning/EPIC_4/SUMMARY.md` with sprint-by-sprint history
  - Include cumulative metrics table and progression charts
  - Document key learnings and technical decisions
  - Add recommendations for Epic 5
  - **Deliverable:** Complete Epic 4 SUMMARY.md

- **README and User Documentation (2-3h)**
  - Update README.md with Epic 4 results and capabilities
  - Update user-facing documentation with new features
  - Add examples for new functionality (IndexOffset, etc.)
  - **Deliverable:** Updated README and user docs

- **Architecture Documentation (2-3h)**
  - Document architecture changes from Epic 4
  - Update IR documentation with IndexOffset
  - Document solution forcing strategies
  - **Deliverable:** Updated architecture docs

### v2.0.0 Release (~6-8h)
- **Release Notes (2-3h)**
  - Create comprehensive v2.0.0 release notes
  - Highlight major improvements: parse rate, solve rate, new features
  - Document breaking changes (if any)
  - **Deliverable:** v2.0.0 release notes

- **Version Bump and Quality Gate (2h)**
  - Version bump in pyproject.toml to 2.0.0
  - Full quality gate verification (typecheck, lint, format, test)
  - Ensure all CI checks pass
  - **Deliverable:** Quality-verified codebase

- **Release Mechanics (2-3h)**
  - Update CHANGELOG.md with all Epic 4 changes
  - Create release commit and tag
  - Publish GitHub release with artifacts
  - **Deliverable:** v2.0.0 released

### Epic 5 Planning (~6-8h)
- **Backlog Prioritization (2-3h)**
  - Review REMAINING_FAILURES.md from Sprint 24
  - Prioritize remaining parse/translate/solve issues
  - Identify quick wins vs. major undertakings
  - **Deliverable:** Prioritized Epic 5 backlog

- **New Feature Opportunities (2-3h)**
  - Identify new features enabled by Epic 4 progress
  - Consider: additional model types, performance optimization, tooling
  - Gather any user feedback
  - **Deliverable:** Epic 5 opportunity analysis

- **Epic 5 Project Plan Draft (2-3h)**
  - Create initial `docs/planning/EPIC_5/PROJECT_PLAN.md`
  - Define Epic 5 goals and success criteria
  - Outline Sprint 26-30 high-level scope
  - **Deliverable:** Draft Epic 5 PROJECT_PLAN.md

### Sprint Retrospective (~2h)
- **Epic 4 Retrospective (2h)**
  - Document what worked well across Sprints 18-25
  - Identify process improvements for Epic 5
  - Celebrate achievements
  - **Deliverable:** Epic 4 retrospective document

## Deliverables
- Complete `docs/planning/EPIC_4/SUMMARY.md`
- Updated README.md and user documentation
- Updated architecture documentation
- v2.0.0 release notes, CHANGELOG, tag, and GitHub release
- Prioritized Epic 5 backlog
- Draft `docs/planning/EPIC_5/PROJECT_PLAN.md`
- Epic 4 retrospective

## Acceptance Criteria
- **Release:** v2.0.0 tagged, pushed, and GitHub release published
- **Documentation:** All Epic 4 documentation complete and reviewed
- **Final Parse Rate:** ≥ 95% of valid corpus (confirmed from Sprint 24)
- **Final Translate Rate:** ≥ 90% of parsed models (confirmed from Sprint 24)
- **Final Solve Rate:** ≥ 80% of translated models (confirmed from Sprint 24)
- **Full Pipeline:** ≥ 70% of valid corpus (confirmed from Sprint 24)
- **Epic 5 Ready:** Draft project plan created; backlog prioritized
- **Quality:** All quality gates pass on final release

**Estimated Effort:** 22-28 hours
**Risk Level:** LOW (release mechanics and documentation; Epic 5 planning is exploratory)

---

## Rolling KPIs & Tracking

### Sprint-Level KPIs

| Metric | S18 | S19 | S20 | S21 | S22 | S23 | S24 | S25 |
|--------|-----|-----|-----|-----|-----|-----|-----|-----|
| Valid Corpus Defined | ✓ | — | — | — | — | — | — | — |
| lexer_invalid_char | ~95 | <50 | <40 | <15 | <10 | <8 | <5 | <5 |
| internal_error (parse) | ~23 | <15 | <10 | <8 | <5 | <5 | <3 | <3 |
| path_syntax_error | ≤2 | ≤2 | ≤2 | ≤2 | ≤2 | ≤2 | ≤2 | ≤2 |
| path_solve_terminated | 11 | 11 | 11 | classified | ≤5 | ≤3 | ≤3 | ≤3 |
| model_infeasible | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Parse Rate (valid corpus) | ~41% | ≥55% | ≥65% | ≥75% | ≥85% | ≥90% | ≥92% | ≥95% |
| Translate Rate (of parsed) | ~69% | ~72% | ≥75% | ≥80% | ≥82% | ≥85% | ≥88% | ≥90% |
| Solve Rate (of translated) | ≥52% | ≥52% | ≥52% | ≥50% | ≥55% | ≥65% | ≥75% | ≥80% |
| Full Pipeline (valid corpus) | ~14% | ≥20% | ≥30% | ≥40% | ≥50% | ≥55% | ≥65% | ≥70% |

**Note:** Sprint 18 expanded to include emit_gams.py fixes, MCP bug fixes, and lexer analysis (previously Sprint 19 content). All subsequent sprints shifted forward accordingly.

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

- **2026-02-06:** Reorganized sprints 18-25 after Sprint 18 scope expansion
  - Sprint 18 expanded to ~56h by pulling Sprint 19 items (emit_gams.py completion, lexer analysis, fix roadmap)
  - Content cascaded forward: S19←S20, S20←S21, S21←S22, S22←S23, S23←S24, S24←S25
  - Sprint 25 now includes Epic 5 planning as new content
  - Updated KPIs to reflect accelerated progress in Sprint 18
- **2026-02-05:** Initial EPIC_4 project plan created
