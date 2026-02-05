# EPIC 4 Goals: Full GAMSLIB LP/NLP/QCP Coverage

**Timeline:** 16 weeks (8 sprints of 2 weeks each)
**Sprints:** 18-25
**Target Release:** v2.0.0
**Status:** Planning Phase

## Overview

Epic 4 focuses on achieving full pipeline success (parse, translate, solve) for all syntactically correct, feasible GAMSLIB models of type LP, NLP, and QCP. Building on the infrastructure and metrics established in Epic 3 (v1.1.0: 12/160 full pipeline at 7.5%), this epic systematically eliminates blockers at every pipeline stage to reach comprehensive coverage.

A key new capability is **GAMSLIB syntactic correctness validation** — models with syntax errors in the GAMSLIB source itself (e.g., mismatched parentheses in `camcge`) are identified, eliminated from the nlp2mcp test corpus, and reported to the GAMS team for correction. Similarly, models that are inherently infeasible or unbounded are flagged as they may be difficult or impossible to translate and solve as MCP.

The overarching goal: **every GAMSLIB LP, NLP, and QCP model that is syntactically correct and feasible should parse, translate, and solve with nlp2mcp, producing MCP solutions that match the original NLP solutions.** Where MCP solutions diverge from NLP solutions, we will consult the PATH authors (Michael Ferris, Steven Dirkse) for guidance on forcing matching solutions.

## Strategic Themes

1. **GAMSLIB Source Validation** — Identify and eliminate syntactically incorrect models; report issues to GAMS
2. **Parse Completion** — Achieve 100% parse rate on syntactically correct models
3. **Translation Completion** — Achieve 100% translate rate on all parsed models
4. **Solve Completion** — Achieve 100% solve rate on all translated models
5. **Solution Matching** — Verify MCP solutions match NLP solutions; consult PATH authors for discrepancies
6. **Infeasible/Unbounded Handling** — Identify and document models that cannot produce valid MCP solutions

---

## Goal Categories

### 1. GAMSLIB Syntactic Correctness Validation

**Priority:** HIGH
**Estimated Effort:** Sprint 18 (2 weeks)

#### Motivation
Some GAMSLIB models contain syntax errors in their source code (e.g., `camcge` has mismatched parentheses). These models have no hope of parsing, translating, or solving with nlp2mcp — or with GAMS itself. We need to identify these models, remove them from our test corpus, and notify the GAMS team so the GAMSLIB source can be corrected.

Additionally, some models are infeasible or unbounded (currently 2 models flagged as `model_infeasible`). These may produce undefined or degenerate KKT conditions and should be tracked separately.

#### Objectives

- **1.1 GAMS Compilation Test**
  - Run `gams <model>.gms action=c` on all 160 convex models to test GAMS compilation
  - Models that fail GAMS compilation have source-level syntax errors
  - Record compilation status (success/failure) and error messages in database
  - Create new database field: `gams_syntax.status` (valid, syntax_error, compilation_error)

- **1.2 Syntax Error Report Generation**
  - Generate a report listing all models with GAMS syntax errors
  - Include: model name, error message, line number, nature of error
  - Format suitable for submission to GAMS team (or GAMS issue tracker)
  - Create `data/gamslib/SYNTAX_ERROR_REPORT.md`

- **1.3 Corpus Reclassification**
  - Models with GAMS syntax errors: reclassify as `excluded_syntax_error`
  - Models that are infeasible: reclassify as `excluded_infeasible`
  - Models that are unbounded: reclassify as `excluded_unbounded`
  - Update all pipeline metrics to use the reduced "valid corpus" as denominator
  - Track exclusion reasons in database

- **1.4 Infeasible/Unbounded Detection**
  - Review the 2 currently-flagged `model_infeasible` models
  - Check GAMS solve status for unbounded indicators
  - Document which models are inherently infeasible or unbounded
  - Assess whether infeasible/unbounded models can produce meaningful MCP formulations

#### Success Criteria
- All 160 models tested for GAMS compilation
- Syntactically incorrect models identified and excluded from corpus
- Infeasible/unbounded models documented with rationale
- Pipeline metrics recalculated against valid corpus
- GAMS notification report generated

---

### 2. Parse Stage: Eliminate lexer_invalid_char Errors

**Priority:** HIGH
**Estimated Effort:** Sprints 18-20 (6 weeks)

#### Motivation
The `lexer_invalid_char` category accounts for 74 of 99 parse failures (74.7%). These are models where the lexer encounters characters or token patterns it doesn't recognize. Systematic elimination of these errors is the highest-impact work for improving parse rates.

#### Objectives

- **2.1 Lexer Error Subcategorization**
  - Analyze all 74 `lexer_invalid_char` failures
  - Group by specific character/pattern that triggers the error
  - Identify clusters of models sharing the same lexer issue
  - Prioritize fixes by model count per cluster

- **2.2 Complex Set Data Syntax (14+ models)**
  - Handle advanced set data patterns that the current grammar rejects
  - Include: multi-dimensional set assignments, compound set operations
  - May require grammar refactoring for data statement handling
  - High effort but high model count

- **2.3 Put Statement Format Syntax (4 models)**
  - Add support for `:width:decimals` format specifiers in put statements
  - Models affected: ps5_s_mn, ps10_s, ps10_s_mn, stdcge
  - Low effort (~2h), well-defined syntax extension

- **2.4 Remaining Lexer Patterns**
  - Address remaining lexer_invalid_char subcategories
  - Compile-time constants in ranges (e.g., `1*card(s)`)
  - Implicit assignment statements
  - Other character-level lexer rejections identified in 2.1

#### Success Criteria
- `lexer_invalid_char` count reduced from 74 to <15
- Put statement format syntax fully supported
- Complex set data syntax handled for majority of affected models
- Parse rate on valid corpus exceeds 75%

---

### 3. Parse Stage: Resolve internal_error Failures

**Priority:** HIGH
**Estimated Effort:** Sprints 19-20 (4 weeks)

#### Motivation
The `internal_error` category at parse stage accounts for 23 failures. These are models that pass lexing but crash the parser — likely due to grammar productions that accept the tokens but produce malformed parse trees, or IR construction failures on valid parse trees.

#### Objectives

- **3.1 Internal Error Classification**
  - Run all 23 internal_error models with verbose/debug parser output
  - Classify errors: grammar ambiguity, missing production, IR construction, transformer crash
  - Identify common patterns across models

- **3.2 Grammar Ambiguity Resolution**
  - Fix grammar productions that create ambiguous parses
  - Add disambiguation rules or restructure productions
  - Ensure Lark parser handles all valid GAMS constructs

- **3.3 IR Construction Hardening**
  - Fix transformer/visitor crashes on valid parse trees
  - Add graceful handling for unexpected AST shapes
  - Ensure IR construction covers all grammar-valid inputs

- **3.4 Semantic Error Handling**
  - Address `semantic_undefined_symbol` errors (2 models)
  - Investigate whether these are GAMSLIB issues or nlp2mcp bugs
  - Improve error messages for semantic failures

#### Success Criteria
- `internal_error` (parse) count reduced from 23 to <5
- `semantic_undefined_symbol` resolved or documented as GAMSLIB issues
- Parser does not crash on any syntactically valid GAMS input

---

### 4. Translation Stage: IndexOffset Support

**Priority:** HIGH
**Estimated Effort:** Sprint 20-21 (4 weeks)

#### Motivation
The `unsup_index_offset` category blocks 8 models from translating. These models use GAMS lead/lag indexing (`t-1`, `t+1`, `t++1`, `t--1`) which requires IR-level support, derivative rules for shifted indices, and emit support for GAMS lead/lag syntax. This is the largest single translation blocker category.

#### Objectives

- **4.1 IR Support for IndexOffset**
  - Add `IndexOffset` node type to the IR
  - Handle positive offsets (lead: `t+1`) and negative offsets (lag: `t-1`)
  - Handle circular offsets (`t++1`, `t--1`)
  - Parse GAMS lead/lag syntax into IndexOffset nodes

- **4.2 Differentiation Rules for IndexOffset**
  - Implement derivative rules for expressions containing shifted indices
  - Handle chain rule with index offsets
  - Ensure KKT stationarity equations correctly incorporate offset indices

- **4.3 Emit Support for Lead/Lag**
  - Generate correct GAMS syntax for lead/lag in MCP output
  - Handle both `ord`-based and direct lead/lag notations
  - Test against all 8 affected models

#### Success Criteria
- All 8 `unsup_index_offset` models translate successfully
- Lead/lag indexing works for both positive and negative offsets
- Generated MCP files compile and solve correctly with PATH

---

### 5. Translation Stage: Remaining Blockers

**Priority:** MEDIUM-HIGH
**Estimated Effort:** Sprints 21-22 (4 weeks)

#### Motivation
Beyond IndexOffset, there are additional translation failures including `internal_error` (translate) at 5 models and various other categories. As parse improvements bring more models into the translation stage, new translation blockers will be discovered.

#### Objectives

- **5.1 Translation Internal Error Investigation**
  - Debug the 5 `internal_error` (translate) models
  - Identify root causes: missing derivative rules, IR construction gaps, KKT generation bugs
  - Fix or document each failure

- **5.2 Derivative Rule Expansion**
  - Implement missing derivative rules identified during Sprint 17:
    - `gamma`/`loggamma` function derivatives
    - `smin` smooth approximation
    - Additional trigonometric/hyperbolic derivatives as needed
  - Planned but unexecuted Sprint 17 quick wins

- **5.3 Objective Extraction Enhancement**
  - Improve handling of models without explicit `minimize`/`maximize` statements
  - Handle models with objective defined in constraint form
  - Address `model_no_objective_def` patterns

- **5.4 New Translation Blockers (from Parse Improvements)**
  - As parse rate improves, newly-parsed models will reveal new translation issues
  - Allocate capacity for emerging translation blockers
  - Track and prioritize dynamically

#### Success Criteria
- Translation `internal_error` count reduced from 5 to 0
- All planned derivative rules implemented
- Translation rate on parsed models exceeds 85%

---

### 6. Solve Stage: Fix emit_gams.py Blockers

**Priority:** HIGH
**Estimated Effort:** Sprints 18-19 (4 weeks)

#### Motivation
The `path_syntax_error` category accounts for 17 solve failures. These are models that translate successfully but produce MCP files that GAMS cannot compile due to code generation bugs in emit_gams.py. This was the highest-priority deferred work from Sprint 17.

#### Objectives

- **6.1 Table Data Emission (~4 models)**
  - Fix emission of GAMS table data structures in MCP output
  - Handle multi-dimensional tables with proper formatting
  - Location: `src/emit/original_symbols.py`

- **6.2 Computed Parameter Assignments (~4 models)**
  - Fix emission of parameter assignments that involve computed values
  - Handle expressions in parameter data definitions
  - Location: `src/emit/original_symbols.py`

- **6.3 Subset Relationship Preservation (~3 models)**
  - Preserve set-subset relationships when emitting domain declarations
  - Ensure subset constraints are maintained in MCP output
  - Location: `src/emit/original_symbols.py`

- **6.4 Reserved Word Quoting (~2 models)**
  - Quote set elements that are GAMS reserved words
  - Handle context-dependent quoting requirements
  - Location: `src/emit/expr_to_gams.py`

- **6.5 Other path_syntax_error Patterns (~4 models)**
  - Investigate remaining path_syntax_error models
  - Fix additional emit patterns as discovered
  - Various emit modules

#### Success Criteria
- `path_syntax_error` count reduced from 17 to <3
- Solve rate on translated models exceeds 50%
- All emit fixes include regression tests

---

### 7. Solve Stage: PATH Convergence and Solution Matching

**Priority:** HIGH
**Estimated Effort:** Sprints 22-24 (6 weeks)

#### Motivation
The `path_solve_terminated` category accounts for 11 models where PATH fails to converge. Additionally, as more models reach the solve stage, solution matching (MCP vs NLP objective values) becomes critical. Some MCP formulations may produce different solutions than the original NLP — these cases require consultation with the PATH authors (Michael Ferris, Steven Dirkse).

#### Objectives

- **7.1 PATH Convergence Investigation**
  - Analyze all `path_solve_terminated` models
  - Classify: KKT correctness issue, starting point problem, inherent difficulty, PATH options
  - For KKT bugs: fix the formulation
  - For starting point issues: improve initialization strategy
  - For PATH options: tune iteration limits, tolerances, crash methods

- **7.2 Solution Comparison Framework Enhancement**
  - Extend solution comparison beyond objective value matching
  - Compare: primal variables, dual variables (multipliers), complementarity residuals
  - Implement relative/absolute tolerance combination with model-appropriate defaults
  - Generate detailed mismatch reports

- **7.3 MCP-NLP Solution Divergence Analysis**
  - Identify models where MCP solution exists but differs from NLP solution
  - Classify divergences: multiple optima, numerical precision, formulation error
  - Document cases requiring PATH author consultation

- **7.4 PATH Author Consultation Preparation**
  - Prepare detailed case studies for models with solution mismatches
  - Include: original NLP formulation, MCP formulation, both solutions, discrepancy analysis
  - Format for review by Michael Ferris and Steven Dirkse
  - Create `docs/research/PATH_CONSULTATION.md` with findings and questions

- **7.5 Solution Forcing Strategies**
  - Based on PATH author guidance, implement strategies to force MCP solutions to match NLP solutions
  - Options may include: tighter tolerances, starting point from NLP solution, reformulation techniques
  - Document which strategies work for which model classes

#### Success Criteria
- `path_solve_terminated` count reduced by 50%+
- Solution comparison framework captures all divergence types
- PATH consultation document prepared with specific cases
- At least initial response from PATH authors incorporated

---

### 8. Performance, Quality & Release

**Priority:** MEDIUM
**Estimated Effort:** Sprint 25 (2 weeks)

#### Motivation
The final sprint consolidates all improvements, ensures quality, stabilizes performance benchmarks, and prepares the v2.0.0 release.

#### Objectives

- **8.1 Performance Benchmark Stabilization**
  - Replace absolute wall-clock thresholds with regression detection
  - Use statistical approach (median of N runs) to reduce CI flakiness
  - Add warm-up runs for cold-start variance reduction
  - Sprint 17 recommendation carried forward

- **8.2 Comprehensive Pipeline Retest**
  - Run full pipeline on all valid corpus models
  - Generate final metrics and comparison to Epic 3 baseline
  - Document all remaining failures with root cause analysis

- **8.3 Documentation and Reporting**
  - Update all auto-generated reports (GAMSLIB_STATUS.md, FAILURE_ANALYSIS.md)
  - Create Epic 4 SUMMARY.md with full sprint-by-sprint history
  - Update README.md with Epic 4 results
  - Create v2.0.0 release notes

- **8.4 v2.0.0 Release**
  - Version bump and release preparation
  - Final quality gate verification
  - Tag and GitHub release

#### Success Criteria
- Performance benchmarks do not produce flaky CI failures
- All pipeline metrics documented and compared to Epic 3 baseline
- v2.0.0 released with comprehensive documentation
- Clear path forward documented for any remaining failures

---

## Sprint Breakdown

### Sprint 18 (Weeks 1-2): Syntactic Validation & emit_gams.py Fixes
- Run GAMS compilation test on all 160 models
- Classify and exclude syntactically incorrect models
- Document infeasible/unbounded models
- Begin emit_gams.py path_syntax_error fixes (table data, computed params)
- Put statement format syntax (~2h quick win)

**Deliverables:**
- `data/gamslib/SYNTAX_ERROR_REPORT.md`
- Database updated with `gams_syntax.status` field
- Recalculated pipeline metrics against valid corpus
- emit_gams.py fixes for ~8 models
- Put statement format support in grammar

### Sprint 19 (Weeks 3-4): emit_gams.py Completion & Parse Analysis
- Complete remaining emit_gams.py fixes (subset preservation, reserved words)
- Deep analysis of all 74 lexer_invalid_char failures
- Subcategorize and prioritize lexer fixes
- Begin complex set data syntax work

**Deliverables:**
- `path_syntax_error` count reduced to <3
- Lexer error subcategorization report
- Initial complex set data syntax fixes
- Updated pipeline metrics

### Sprint 20 (Weeks 5-6): Parse Improvements (lexer_invalid_char & internal_error)
- Major push on lexer_invalid_char elimination
- Internal error investigation and fixes
- Grammar refactoring for complex data syntax
- IndexOffset IR design and initial implementation

**Deliverables:**
- `lexer_invalid_char` count below 30
- `internal_error` (parse) count below 10
- IndexOffset IR node type defined
- Parse rate exceeds 60% of valid corpus

### Sprint 21 (Weeks 7-8): IndexOffset & Translation Improvements
- Complete IndexOffset implementation (IR, derivatives, emit)
- Address translation internal errors
- Implement missing derivative rules (gamma, smin, etc.)
- Objective extraction enhancement

**Deliverables:**
- IndexOffset support complete for all 8 affected models
- Translation `internal_error` count at 0
- New derivative rules implemented with tests
- Translation rate exceeds 80%

### Sprint 22 (Weeks 9-10): Parse Completion & Solve Investigation
- Final push on remaining parse failures
- Address newly-discovered translation blockers from improved parse
- Begin PATH convergence investigation
- Solution comparison framework enhancement

**Deliverables:**
- Parse rate exceeds 85% of valid corpus
- Remaining parse failures documented with root causes
- PATH convergence analysis for all `path_solve_terminated` models
- Enhanced solution comparison framework

### Sprint 23 (Weeks 11-12): Solve Improvements & Solution Matching
- Fix KKT bugs identified in PATH convergence analysis
- Improve starting point initialization
- Tune PATH solver options for difficult models
- Begin MCP-NLP solution divergence analysis

**Deliverables:**
- `path_solve_terminated` count reduced by 50%+
- Starting point initialization improvements
- PATH options tuning guide
- Initial solution divergence report

### Sprint 24 (Weeks 13-14): PATH Consultation & Solution Forcing
- Prepare PATH author consultation document
- Submit cases to Ferris/Dirkse for review
- Implement solution forcing strategies based on guidance
- Address remaining solve failures

**Deliverables:**
- `docs/research/PATH_CONSULTATION.md`
- Solution forcing strategies implemented
- Solve rate exceeds 70% of translated models
- Remaining failures documented

### Sprint 25 (Weeks 15-16): Quality, Performance & v2.0.0 Release
- Performance benchmark stabilization (regression-based, not absolute)
- Final comprehensive pipeline retest
- Documentation finalization
- v2.0.0 release

**Deliverables:**
- Stable, non-flaky performance benchmarks
- Final pipeline metrics and comparison report
- Epic 4 SUMMARY.md
- v2.0.0 release (tag + GitHub release + release notes)

---

## Success Metrics

### Quantitative

- **Valid Corpus:** Syntactically correct, feasible models identified (expected: ~150 of 160)
- **Parse Success:** ≥95% of valid corpus parses successfully
- **Translation Success:** ≥90% of parsed models translate successfully
- **Solve Success:** ≥80% of translated models solve correctly
- **Solution Match:** ≥90% of solved models produce matching NLP/MCP solutions
- **Full Pipeline:** ≥70% of valid corpus completes full pipeline
- **Improvement:** From 7.5% (Epic 3) to ≥70% full pipeline success

### Qualitative

- **Syntactically Incorrect Models:** Identified, reported to GAMS, excluded from metrics
- **Infeasible/Unbounded Models:** Documented with rationale for exclusion
- **PATH Author Consultation:** Cases prepared and submitted; initial guidance incorporated
- **Solution Forcing:** Strategies documented for models with divergent solutions
- **Reproducible:** All results reproducible with deterministic pipeline configuration
- **Actionable:** Remaining failures documented with clear root causes and next steps

---

## File Structure

```
docs/planning/EPIC_4/
  ├── GOALS.md                    # This document
  ├── SUMMARY.md                  # Epic summary (created during execution)
  ├── SPRINT_18/                  # Sprint 18 planning and logs
  │   ├── SPRINT_SCHEDULE.md
  │   ├── SPRINT_LOG.md
  │   ├── SPRINT_RETROSPECTIVE.md
  │   └── PREP_PLAN.md
  ├── SPRINT_19/ ... SPRINT_25/   # Similar structure per sprint

data/gamslib/
  ├── gamslib_status.json         # Updated with new fields
  ├── SYNTAX_ERROR_REPORT.md      # GAMS syntax error report
  ├── GAMSLIB_STATUS.md           # Updated auto-generated report
  └── progress_history.json       # Historical metrics extended

docs/research/
  └── PATH_CONSULTATION.md        # Cases for PATH author review

scripts/gamslib/
  ├── test_syntax.py              # GAMS compilation test script
  └── (existing scripts enhanced)
```

---

## Risks & Mitigation

### Risk 1: GAMSLIB Models with Stacked Blockers
**Impact:** HIGH
**Probability:** HIGH

Many models have 2+ independent blocking issues. Fixing one issue reveals the next.

**Mitigation:**
- Track "blockers removed" alongside "models unblocked" (Sprint 17 lesson)
- Expect diminishing returns as easy fixes are exhausted
- Prioritize by blocker frequency, not model count

### Risk 2: MCP-NLP Solution Divergence
**Impact:** HIGH
**Probability:** MEDIUM

Some MCP formulations may produce valid but different solutions from the NLP formulation, especially for models with multiple optima or degenerate solutions.

**Mitigation:**
- Build robust solution comparison with appropriate tolerances
- Prepare detailed case studies for PATH author consultation
- Plan for iterative guidance from Ferris/Dirkse (may require multiple rounds)

### Risk 3: PATH Author Availability
**Impact:** MEDIUM
**Probability:** MEDIUM

Ferris and Dirkse may have limited availability for consultation.

**Mitigation:**
- Prepare clear, self-contained case studies that minimize back-and-forth
- Batch questions rather than individual queries
- Have fallback strategies (literature review, empirical experimentation)

### Risk 4: Grammar Refactoring Scope
**Impact:** MEDIUM
**Probability:** HIGH

Complex set data syntax (14+ models) may require significant grammar restructuring that risks regressions in currently-passing models.

**Mitigation:**
- Comprehensive grammar regression test suite (currently 3204 tests)
- Incremental changes with full test runs after each modification
- Golden file tests for all 12 currently-solving models

### Risk 5: Diminishing Returns on Parse Fixes
**Impact:** MEDIUM
**Probability:** MEDIUM

The remaining 74 lexer errors may be long-tail issues with 1-2 models each, making individual fixes less impactful.

**Mitigation:**
- Thorough subcategorization (Goal 2.1) before implementation
- Focus on clusters, not individual models
- Accept that some models may require GAMS preprocessing

### Risk 6: Infeasible MCP Formulations
**Impact:** MEDIUM
**Probability:** LOW-MEDIUM

Some KKT reformulations may be inherently infeasible even when the original NLP is feasible (e.g., due to constraint qualification failures).

**Mitigation:**
- Include in PATH author consultation
- Document models where MCP formulation is provably infeasible
- Research constraint qualification conditions

---

## Dependencies

### External Dependencies
- GAMS software installed locally (with valid license)
- PATH solver available (version 5.2+)
- Internet access for GAMS team communication
- PATH author availability (Michael Ferris, Steven Dirkse) for consultation

### Internal Dependencies
- Epic 3 deliverables: GAMSLIB testing infrastructure, pipeline scripts, reporting tools
- v1.1.0 as stable baseline (219 models cataloged, 160 verified convex)
- Error taxonomy (47 categories) for consistent failure tracking
- Quality gate infrastructure (typecheck, lint, format, 3204+ tests)

---

## Deferred Work Inventory (from Epic 3)

The following items were identified in Sprint 16/17 retrospectives and Epic 3 summary as deferred to future work. All are incorporated into Epic 4 goals above.

### From Sprint 17 Retrospective

| Item | Priority | Goal Reference | Models Affected |
|------|----------|----------------|-----------------|
| emit_gams.py solve blockers (table data, computed params, subset relationships) | P1 | Goal 6 | 17 (path_syntax_error) |
| IndexOffset support (lead/lag indexing) | P2 | Goal 4 | 8 (unsup_index_offset) |
| Parse internal_error investigation | P3 | Goal 3 | 23 |
| PATH convergence investigation | P4 | Goal 7 | 11 (path_solve_terminated) |
| Put statement format syntax | P5 | Goal 2.3 | 4 |
| Remaining grammar gaps (compile-time constants, complex set data, implicit assignments) | P6 | Goals 2.2, 2.4 | 14+ |
| Performance benchmark stabilization | P7 | Goal 8.1 | N/A (CI reliability) |

### From Sprint 16 Retrospective

| Item | Priority | Goal Reference | Models Affected |
|------|----------|----------------|-----------------|
| Complex set data syntax (largest parse subcategory) | P1 | Goal 2.2 | 14+ |
| Numeric context in parameter data | P2 | Goal 2.4 | ~5 |
| Translation blockers: model_domain_mismatch | P3 | Goal 5 | 6 |
| Translation blockers: diff_unsupported_func | P3 | Goal 5.2 | 6 |
| Translation blockers: model_no_objective_def | P3 | Goal 5.3 | 5 |

### Planned but Unexecuted Sprint 17 Work

| Item | Priority | Goal Reference | Notes |
|------|----------|----------------|-------|
| gamma/loggamma derivative rules | P2 | Goal 5.2 | Superseded by KKT root cause fixes |
| smin smooth approximation | P2 | Goal 5.2 | Superseded by KKT root cause fixes |
| Objective extraction enhancement | P3 | Goal 5.3 | Deferred in favor of deeper KKT work |

---

## Future Work (Post-Epic 4)

### Epic 5 Candidates

1. **Extended Model Type Support**
   - DNLP (Discontinuous NLP) models — requires subdifferential handling
   - MPSGE (General Equilibrium) models — specialized structure
   - CNS (Constrained Nonlinear Systems) — direct MCP without optimization

2. **Non-GAMSLIB Test Sources**
   - CUTEst test problem collection
   - Netlib LP test problems
   - User-submitted models from community
   - Industry partner test cases

3. **CI Integration for GAMSLIB Testing**
   - Automated nightly pipeline runs (requires GAMS license in CI)
   - Regression detection with alerts
   - Automated database updates and report generation

4. **Model Transformation Preprocessing**
   - Automatic model simplification before parsing
   - Macro expansion and include resolution
   - Handle common unsupported patterns via preprocessing

5. **Performance Optimization**
   - Parallel batch processing for pipeline stages
   - Profile and optimize bottlenecks on large models
   - Incremental pipeline (only re-run changed stages)

6. **MCP Solution Quality Metrics**
   - Complementarity residual analysis
   - Solution sensitivity and stability metrics
   - Comparison with commercial MCP solvers

---

## References

### Internal Documents
- `docs/planning/EPIC_3/GOALS.md` — Epic 3 goals (predecessor)
- `docs/planning/EPIC_3/SUMMARY.md` — Epic 3 summary with final metrics
- `docs/planning/EPIC_3/SPRINT_16/SPRINT_RETROSPECTIVE.md` — Sprint 16 retrospective
- `docs/planning/EPIC_3/SPRINT_17/SPRINT_RETROSPECTIVE.md` — Sprint 17 retrospective
- `docs/planning/EPIC_3/SPRINT_16/IMPROVEMENT_ROADMAP.md` — Prioritized improvement roadmap
- `docs/releases/v1.1.0.md` — v1.1.0 release notes (Epic 3 baseline)
- `docs/GAMS_SUBSET.md` — Supported GAMS syntax

### External Resources
- GAMS Model Library: https://www.gams.com/latest/gamslib_ml/libhtml/
- GAMS Documentation: https://www.gams.com/latest/docs/
- PATH Solver Manual: https://www.gams.com/latest/docs/S_PATH.html
- PATH Authors: Michael Ferris (UW-Madison), Steven Dirkse (GAMS)

---

## Changelog

- **2026-02-05:** Initial EPIC_4 goals document created
