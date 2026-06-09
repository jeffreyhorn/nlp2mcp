# EPIC 4 Project Plan (Full GAMSLIB LP/NLP/QCP Coverage)

This plan translates `GOALS.md` into sprint-ready guidance for Sprints 18–26 (two weeks each, with Sprint 18 expanded to three weeks based on prep task findings).

**Baseline (v1.1.0 / Epic 3 Final):** Parse 61/160 (38.1%), Translate 42/61 (68.9%), Solve 12/42 (28.6%), Full Pipeline Match 12/160 (7.5%)

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

**Estimated Effort:** 43-53 hours (original 26-32h + 17-21h deferred items)
**Risk Level:** MEDIUM-HIGH (grammar refactoring for complex set data is the highest-risk item in Epic 4)

---

# Sprint 20 (Weeks 5–6): IndexOffset Implementation & Translation Improvements

**Goal:** Complete end-to-end IndexOffset (lead/lag) support (parser → IR → AD → emit), building on the Sprint 19 design and existing partial implementation. Address translation internal errors and objective extraction. Handle emerging translation blockers from improved parse rates. Address deferred Sprint 19 solver blockers (#753, #757, #763, #764, #765).

**Note:** IndexOffset design and initial AD integration landed in Sprint 19; Sprint 20 focuses on wiring it through the full pipeline (emit support, remaining parser/IR gaps), closing end-to-end test coverage, and adding regression tests.

## Sprint 19 Deferred Items

*These items were identified during Sprint 19 as the highest-leverage remaining solver blockers but require architectural work beyond that sprint's scope.*

### Priority 1: Variable Initialization Emission — `.l` assignments (~4-6h)
- **Target:** circle (#753), bearing (#757), and other models that solve but produce PATH model status 5 (locally infeasible).
- **Root Cause:** MCP translator doesn't emit variable level initializations from `.l` assignments in the original model. PATH is highly sensitive to starting points.
- **Fix:** Emit `.l` initialization statements from the IR in the prolog of the generated MCP file. The IR already parses these assignments; it's primarily an emitter gap.
- **Expected Impact:** +2–4 models solving. Low-to-medium effort.
- **Deliverable:** `.l` initialization emission with regression tests

### Priority 2: Accounting Variable Detection (#764 mexss) (~6-8h)
- **Target:** mexss and similar models with auxiliary/identity variables.
- **Root Cause:** Accounting variables (e.g., `xmarket = sum(p, x(p))`) should not get stationarity equations — they are definitional identities. Generating stationarity for them produces an over-constrained MCP.
- **Fix:** Detect variables that appear only on the LHS of equality constraints with no objective contribution (pure identities) and exclude them from the stationarity system.
- **Expected Impact:** +1–3 models solving. Medium effort, requires design work first.
- **Deliverable:** Accounting variable detection with tests

### Priority 3: AD Condition Propagation (#763 chenery) (~6-8h)
- **Target:** chenery and models with conditional denominators.
- **Root Cause:** The chenery model uses `$` conditions to guard denominators in equations (e.g., `x / del(i)` where `del(i) = 0` for some `i`). The AD system produces derivatives without these guards, causing GAMS EXECERROR = 1 (division by zero).
- **Fix:** Propagate the enclosing `$` condition through derivative expressions, or detect division-by-parameter patterns and add guards automatically.
- **Expected Impact:** +1 model solving. Medium-to-high effort (AD condition propagation is architectural).
- **Deliverable:** AD condition propagation design + initial implementation

### Priority 4: Remaining lexer_invalid_char Models (~4-6h)
- **Target:** Further reduce from 27 toward 0.
- **Background:** With Subcategories A/B/F/I addressed in Sprint 19, the remaining 27 lexer failures likely fall into new subcategories. A fresh taxonomy pass should identify the next highest-leverage grammar additions.
- **Expected Impact:** +10–15 models parsing. Medium effort.
- **Deliverable:** Updated lexer error taxonomy; grammar fixes for highest-priority subcategories

### Priority 5: Full Pipeline Match Rate (~4-6h)
- **Target:** 10+ full pipeline matches (Sprint 19 final: 9).
- **Background:** The gap between solve success (25) and full pipeline match (9) suggests many solved models produce different objective values than the reference. Investigate whether `.l` initialization, scaling, or other initialization issues are the cause, and whether solution comparison tolerances need adjustment.
- **Deliverable:** Root cause analysis; tolerance or initialization fixes for divergent models

### Process: Pipeline Smoke Test Before Declaring Issues "Not Fixable"
- Before closing any issue as "not fixable in sprint," run a 30-second CLI smoke test to confirm current status.
- This prevents false negatives (e.g., #671 in Sprint 19 was already resolved but incorrectly assessed as blocked).
- **Deliverable:** Checklist item in sprint close process

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

# Sprint 21 (Weeks 7–8): Macro Expansion, Error Triage & Solve Quality

**Goal:** Implement preprocessor macro expansion, triage internal_error models, reduce path_syntax_error failures, close deferred Sprint 20 issues, investigate PATH convergence, and enhance solution comparison. Push match rate from 16 toward 20+.

**Note:** Sprint 20 final metrics (baseline for Sprint 21): parse 132/160 (82.5%), translate 120/132 (90.9%), solve 33/120 (27.5%), match 16/33 (48.5%), tests 3,715.

## Components

### Priority 1: `%macro%` Expansion in Preprocessor (~4–8h)
- **Target models:** saras (`%system.nlp%`), springchain (`$set`/`$eval`/`%N%`/`%NM1%`), and other models using compile-time macros
- The preprocessor currently strips `$set`/`$eval` directives without executing them
- Implement a macro store + `%name%` expansion to unblock at least 2 `lexer_invalid_char` models
- System macros (~1–2h); `$eval` support (~4–6h)
- **Issues:** #837, #840
- **Deliverable:** Preprocessor macro expansion with tests

### Priority 2: internal_error Triage — 7 Models (~6–10h)
- **Target models:** clearlak, imsl, indus, sarf, senstran, tfordy, turkpow
- These models now parse the grammar but hit IR builder errors (table row index mismatches, lead/lag syntax, undefined references)
- Each likely requires a targeted parser fix (1–2h per model, varying complexity)
- **Deliverable:** IR builder fixes; updated pipeline metrics

### Priority 3: Solve Quality — path_syntax_error (~8–12h)
- **Target:** Reduce the 45 models failing with `path_syntax_error`
- These translate but produce MCP files that PATH cannot process
- Root causes include: malformed equation names, domain mismatches, stationarity system issues
- Systematic triage (similar to Sprint 20 lexer error catalog) to identify highest-leverage fixes
- **Deliverable:** path_syntax_error triage document; targeted fixes

### Priority 4: Deferred Sprint 20 Issues — 13 Issues (~8–12h)
| Issue | Model | Problem |
|---|---|---|
| #763 | chenery | AD condition propagation |
| #764 | mexss | Accounting variable stationarity |
| #765 | orani | CGE model type incompatible |
| #757 | bearing | Non-convex initialization |
| #810 | lmp2 | Solve in doubly-nested loop |
| #826 | decomp | Empty stationarity equation |
| #827 | gtm | Domain violations from zero-fill |
| #828 | ibm1 | Missing bound multipliers |
| #830 | gastrans | Jacobian timeout (dynamic subset) |
| #835 | bearing | .scale emission (partially done) |
| #837 | springchain | Bracket expr + macro expansion |
| #840 | saras | `%system.nlp%` system macro |
| #789 | — | Min/max in objective equations |

### Priority 5: Full Pipeline Match Rate Improvement (~4–6h)
- **Target:** 16 → 20+ matches
- The gap between solve success (33) and match (16) indicates 17 models solve but produce different objectives
- Investigate whether initialization, scaling, domain handling, or solver settings are the cause
- Models close to matching (e.g., port at rel_diff 1.3e-3) may need targeted fixes
- **Deliverable:** Match gap analysis; targeted fixes for near-match models

### Semantic Error Resolution (~2h)
- Resolve `semantic_undefined_symbol` (7 models)
- Determine if these are GAMSLIB source issues or nlp2mcp bugs
- If GAMSLIB issues: add to syntax error report; if bugs: fix
- **Deliverable:** Semantic errors resolved or documented

### Emerging Translation Blockers (~4–6h)
- As parse rate improves, newly-parsed models enter translation
- Identify and categorize new translation failures (2–3h)
- Fix highest-priority blockers — may include new derivative rules, domain mismatches, etc. (2–3h)
- **Deliverable:** Updated translation failure analysis; fixes for emerging blockers

### PATH Convergence Investigation (~8–10h)
- **Systematic Analysis of path_solve_terminated Models (4–5h)**
  - For each `path_solve_terminated` model:
    - Examine PATH solver output and iteration log
    - Check complementarity residuals at termination
    - Test with relaxed tolerances and increased iteration limits
  - Classify: KKT correctness issue, starting point, inherent difficulty, PATH options
  - **Deliverable:** `docs/planning/EPIC_4/SPRINT_21/PATH_CONVERGENCE_ANALYSIS.md`

- **Solution Comparison Enhancement (4–5h)**
  - Extend comparison beyond objective value matching
  - Add: primal variable comparison, dual variable comparison, complementarity residuals
  - Implement combined relative/absolute tolerance with model-appropriate defaults
  - Generate detailed mismatch reports
  - **Deliverable:** Enhanced solution comparison framework with tests

### Pipeline Retest (~2h)
- Full pipeline run after each priority block
- Record parse, translate, solve, and match metrics
- **Deliverable:** Updated metrics tracking

## Process Recommendations (from Sprint 20 Retrospective)
1. **Standardize pipeline denominator.** Use 160 (parse-attempted) as the canonical reference, not 158 (convexity-filtered). Document any exclusions explicitly.
2. **Record PR numbers immediately after merge.** Avoid leaving "PR: TBD" in sprint logs; record the PR number in the same commit as the day's work.
3. **Verify parse claims end-to-end.** Always use `parse_file()` (not partial grammar checks) before claiming a model parses. The pipeline retest is the ground truth.
4. **Run targeted solve on newly-parsing models.** Don't wait for checkpoints to discover solve issues. A quick `--only-solve` run after each parse-improvement PR provides earlier feedback.
5. **Track error category migration.** As lexer errors decrease, models shift to later-stage failures (`internal_error`, `semantic_undefined_symbol`). Track these transitions to prevent surprise backlogs.

## Deliverables
- Preprocessor macro expansion (`$set`/`$eval`/`%name%`)
- IR builder fixes for 7 internal_error models
- path_syntax_error triage and targeted fixes
- Progress on deferred Sprint 20 issues
- Match rate improvement (16 → 20+)
- Semantic errors resolved or documented
- Updated translation failure analysis; fixes for emerging blockers
- `docs/planning/EPIC_4/SPRINT_21/PATH_CONVERGENCE_ANALYSIS.md`
- Enhanced solution comparison framework with tests
- Updated pipeline metrics

## Acceptance Criteria
- **Parse Rate:** ≥ 135/160 (84.4%)
- **lexer_invalid_char:** ≤ 5 (down from 10)
- **internal_error (parse):** ≤ 3 (down from 7)
- **Solve:** ≥ 36 (up from 33)
- **Match:** ≥ 20 (up from 16)
- **PATH Analysis:** All `path_solve_terminated` models classified by root cause
- **Solution Comparison:** Framework extended with primal/dual/complementarity comparison
- **Quality:** All tests pass; no regressions

**Estimated Effort:** 46–68 hours
**Risk Level:** MEDIUM (macro expansion is a new subsystem; path_syntax_error triage may reveal deep translation issues; PATH investigation may reveal fundamental issues)

---

# Sprint 22 (Weeks 9–10): Solve Improvements & Solution Matching

**Goal:** Fix KKT bugs and PATH configuration issues identified in Sprint 21. Improve starting point initialization. Begin MCP-NLP solution divergence analysis. Address deferred Sprint 21 items.

**Note:** PATH convergence analysis from Sprint 21; fixes now in Sprint 22.

## Sprint 21 Deferred Items

*Items triaged during Sprint 21 prep and explicitly deferred due to budget, architectural complexity, or model class limitations.*

### Deferred Issues (4 issues, ~22-30h)

| Issue | Model | Problem | Est. Effort | Why Deferred |
|-------|-------|---------|-------------|-------------|
| #764 | mexss | Accounting variable stationarity — `sameas` guard in `_add_indexed_jacobian_terms()` incorrectly restricts scalar-constraint multiplier terms | 8-12h | Architectural refactor of KKT assembly guard logic; too large for Sprint 21 deferred issues budget |
| #765 | orani | CGE model type incompatible — linearized percentage-change model with exogenously fixed variables; stationarity equations structurally inconsistent | Detection/warning | Fundamental model class incompatibility with NLP→MCP conversion; needs model class detection rather than a fix |
| #827 | gtm | Domain violations from zero-fill — requires domain-aware zero-filling in parser + topological sort for computed parameters in emitter | 6-8h | High effort; partially addressed by Sprint 21 WS4 Subcategory B emitter work but parser-side fix is independent |
| #830 | gastrans | Jacobian timeout from dynamic subsets — dynamic subset fallback in `src/ad/index_mapping.py` causes combinatorial explosion | 8-10h | Requires dynamic subset member preservation + Jacobian sparsity infrastructure |

**Source:** `docs/planning/EPIC_4/SPRINT_21/DEFERRED_ISSUES_TRIAGE.md`

### Deferred path_syntax_error Subcategories (19 models, ~6-8h)

Sprint 21 WS4 triaged the top 3 subcategories (E+D+A, 26/48 models) within the 8-12h budget. The remaining 6 subcategories are deferred:

| Subcategory | Root Cause | Models | Est. Effort | Stage |
|-------------|-----------|--------|-------------|-------|
| C | Uncontrolled set in stationarity equations | 9 | 3-5h | Translator (KKT generation) |
| B | Domain violation in emitted parameter data | 5 | 2-3h | Emitter (data formatting) |
| G | Set index reuse conflict in sum | 2 | 1-2h | Translator (sum domain handling) |
| F | GAMS built-in function name collision | 1 | 1h | Translator (identifier naming) |
| I | MCP variable not referenced in equations | 1 | 1h | Translator (MCP model statement) |
| J | Equation-variable dimension mismatch | 1 | 1h | Translator (equation-variable pairing) |

Additionally, 3 models (dinam, ferts, tricp) entered path_syntax_error after the Sprint 21 catalog was created and are not yet subcategorized.

**Source:** `docs/planning/EPIC_4/SPRINT_21/PATH_SYNTAX_ERROR_CATALOG.md`

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
- **path_solve_terminated:** Count reduced by ≥ 50% (from 12 to ≤ 5)
- **Solve Rate:** ≥ 55% of translated models solve correctly
- **Solution Analysis:** All solving models assessed for NLP/MCP match
- **Case Studies:** At least 3 divergence cases documented for consultation
- **Parse Rate:** ≥ 85% of valid corpus
- **Quality:** All tests pass; KKT fixes have comprehensive tests

**Estimated Effort:** 24-30 hours
**Risk Level:** MEDIUM-HIGH (KKT bugs may be subtle; solution divergence analysis may reveal fundamental issues requiring PATH author input)

---

# Sprint 23 (Weeks 11–12): Solve Rate Push & Error Category Reduction

**Goal:** Push solve success from 89 to ≥ 100 and match from 47 to ≥ 55 by addressing the five priority areas identified in the Sprint 22 retrospective: path_solve_terminated, model_infeasible, match rate, path_syntax_error residual, and translate failures. Maintain parse rate. Apply Sprint 22 process recommendations: use full pipeline for all definitive metrics (PR6), track model_infeasible gross fixes and gross influx separately (PR7), and use absolute counts alongside percentages for parse success (PR8). See `SPRINT_22/SPRINT_RETROSPECTIVE.md` §New Recommendations for Sprint 23 for details.

**Note:** Sprint 22 retrospective identified 24 issues labeled `sprint-23`. Priorities derived from Sprint 22 error category analysis and the suggested targets table.

## Sprint 22 Deferred Items

*Items carried forward from Sprint 22 retrospective recommendations.*

### Deferred path_syntax_error Subcategories G+B (from Sprint 22 WS1)
- Subcategories G (set index reuse, 2 models) and B (domain violations, 5 models) were planned for Sprint 22 Days 2-3 but redirected to WS2/WS3
- Key issues: #956 (nonsharp compilation errors), #1041 (cesam2 empty equation), #882/#871 (camcge subset conditioning)

### path_solve_terminated Residual (from Sprint 22 WS2)
- Sprint 22 reduced from 12 to 10 but missed the ≤ 5 target
- Most remaining models have MCP pairing or execution errors, not PATH convergence issues

## Components

### Priority 1: path_solve_terminated Reduction (~8-12h)
- **MCP Pairing & Execution Fixes (6-8h)**
  - 10 models remain: dyncge, elec, etamac, fawley, gtm, maxmin, qsambal, rocket, sambal, twocge
  - Most have MCP pairing or execution errors, not PATH convergence issues
  - Key issues: #862 (sambal domain conditioning), #983 (elec division by zero), #986 (lands NA values)
  - Triage each model, classify root cause, fix highest-leverage issues
  - Target: reduce from 10 to ≤ 5
  - **Deliverable:** MCP fixes with regression tests; updated triage document

- **Convergence Investigation for Remaining Models (2-4h)**
  - For models that genuinely fail PATH convergence: investigate starting points, scaling, reformulation
  - Document models requiring PATH author consultation
  - **Deliverable:** Convergence analysis for residual models

### Priority 2: model_infeasible Reduction (~8-10h)
- **KKT Bug Fixes (6-8h)**
  - 12 in-scope models: bearing, chain, cpack, lnts, markov, mathopt3, pak, paperco, prolog, robustlp, sparta, spatequ
  - Key issues: #1049 (pak incomplete stationarity), #1070 (prolog singular Jacobian), #1081 (sparta KKT bug), #1110 (markov multi-pattern Jacobian)
  - Each fix includes regression tests
  - Target: reduce from 12 to ≤ 8
  - **Deliverable:** KKT fixes with tests; track gross fixes and gross influx per PR7

- **Infeasibility Root Cause Classification (2h)**
  - Classify remaining infeasible models as: KKT formulation bug, inherent MCP incompatibility, or structural issue
  - Document permanently infeasible models separately from fixable ones
  - **Deliverable:** Updated infeasibility classification

### Priority 3: Match Rate Improvement (~6-8h)
- **Alias-Aware Differentiation (3-4h)**
  - Key architectural issue: #1111 (alias-aware differentiation)
  - Fix derivative computation for aliased set references
  - **Deliverable:** Alias differentiation fix with tests

- **Dollar-Condition Propagation (3-4h)**
  - Key architectural issue: #1112 (dollar-condition propagation in AD)
  - Propagate enclosing dollar conditions through derivative expressions
  - Test across divergent models where condition guards affect solution
  - **Deliverable:** Dollar-condition propagation fix with tests

### Priority 4: path_syntax_error Residual (~4-6h)
- **Deferred Subcategories G+B (3-4h)**
  - 20 path_syntax_error models remain overall from Sprint 22; this workstream targets the 7-model G+B subset
  - Fix set index reuse (subcategory G, 2 models) and domain violations (subcategory B, 5 models)
  - Key issues: #956 (nonsharp compilation errors), #1041 (cesam2 empty equation), #882/#871 (camcge subset conditioning)
  - Target: reduce from 20 to ≤ 15
  - **Deliverable:** Emitter and translator fixes with tests

- **New Subcategory Triage (1-2h)**
  - Categorize any models that entered path_syntax_error during Sprint 22 but aren't yet classified
  - File issues for Sprint 24 backlog
  - **Deliverable:** Updated path_syntax_error catalog

### Priority 5: Translate Failures (~4-6h)
- **Compilation Error Fixes (2-3h)**
  - 15 translate failures remain (mix of compilation errors and timeout issues)
  - Fix highest-leverage compilation errors first
  - Target: reduce from 15 to ≤ 11 (consistent with acceptance criterion ≥ 145/156)
  - **Deliverable:** Translation fixes with tests

- **Timeout Investigation (2-3h)**
  - Profile remaining timeout models to identify bottlenecks (deep recursion, large models, specific grammar patterns)
  - Apply targeted fixes where feasible; increase timeout or document as intractable where not
  - **Deliverable:** Timeout analysis; fixes or documentation for each

### Pipeline Retest (~2h)
- Full pipeline run at each checkpoint and final (per PR6)
- Record metrics for all stages using full pipeline (not `--only-solve`)
- Track model_infeasible gross fixes and gross influx separately (per PR7)
- Use absolute counts alongside percentages for parse success (per PR8)
- **Deliverable:** Updated `gamslib_status.json`; comprehensive metrics report

## Deliverables
- MCP pairing/execution fixes for path_solve_terminated models
- KKT bug fixes for model_infeasible models with infeasibility classification
- Alias-aware differentiation and dollar-condition propagation fixes
- path_syntax_error subcategory G+B fixes and updated catalog
- Translation compilation error fixes and timeout analysis
- Updated pipeline metrics with full pipeline at all checkpoints

## Acceptance Criteria
- **Solve:** ≥ 100 models solve (up from 89)
- **Match:** ≥ 55 models match (up from 47)
- **path_solve_terminated:** ≤ 5 (down from 10)
- **model_infeasible:** ≤ 8 in-scope (down from 12)
- **path_syntax_error:** ≤ 15 (down from 20)
- **Translate:** ≥ 93% of parsed models (≥ 145/156 assuming 156 parsed; up from 90.4%)
- **Parse:** ≥ 156/160 (maintain 97.5%)
- **Tests:** ≥ 4,300 (up from 4,209)
- **Quality:** All tests pass; all fixes have regression tests

**Estimated Effort:** 32-44 hours
**Risk Level:** MEDIUM (path_solve_terminated and model_infeasible fixes may reveal deeper architectural issues; alias differentiation is a significant AD change; match rate improvement depends on correct root cause identification)

---

# Sprint 24 (Weeks 13–14): Alias Differentiation & Error Category Reduction

**Goal:** Address the single largest blocker (alias-aware differentiation #1111 family, ~20 models) and reduce error categories. Push solve from 86 to ≥ 95, match from 49 to ≥ 55. Apply Sprint 23 process recommendations by setting targets against actual pipeline scope, budgeting for error category influx, and prioritizing the highest-leverage architectural fix in Days 1-5. (See `SPRINT_23/SPRINT_RETROSPECTIVE.md` §New Recommendations PR9–PR11 for details.)

**Note:** Sprint 23 retrospective identified 20 issues labeled `sprint-24`. Alias differentiation is Priority 1 (highest leverage for both solve and match improvements).

## Components

### Priority 1: Alias-Aware Differentiation (#1111 Family) (~14-18h)
- **Summation-Context Tracking (8-10h)**
  - Thread summation context through `_diff_varref`/`_partial_collapse_sum`
  - Alias-to-root-set resolution in Jacobian construction
  - 12 open issues affecting ~20 models
  - Key architectural work: distinguish alias indices from domain indices in derivative computation
  - **Deliverable:** Alias differentiation fix with comprehensive tests

- **Regression Validation (4-6h)**
  - Verify all 49 currently-matching models still match
  - Test across all 12 alias-differentiation issues
  - **Deliverable:** Regression suite; updated MCP output files

- **Impact Assessment (2h)**
  - Track which models move from mismatch → match, infeasible → optimal, etc.
  - Document models that improve but don't fully resolve
  - **Deliverable:** Impact assessment document

### Priority 2: path_syntax_error Reduction (23 → ≤ 15) (~6-8h)
- **Compilation Error Fixes (4-6h)**
  - 23 models with compilation errors (5 influx from Sprint 23 translate recovery)
  - Categories: uncontrolled set references, invalid index expressions, empty equation bodies
  - Subset-superset domain and condition scope issues
  - **Deliverable:** Emitter and stationarity fixes with tests

- **Triage New Influx Models (2h)**
  - Classify the 5 newly-translating models that entered path_syntax_error
  - File issues and prioritize fixes
  - **Deliverable:** Updated path_syntax_error catalog

### Priority 3: model_infeasible Reduction (11 → ≤ 8) (~6-8h)
- **Jacobian Accuracy Fixes (4-6h)**
  - 11 in-scope models
  - Key issues: #1199 (bearing), #1177 (chenery), #1195 (sambal NA), #1192 (gtm div/zero)
  - Many overlap with Priority 1 (alias differentiation improves Jacobian accuracy)
  - **Deliverable:** KKT fixes with tests; track gross fixes/influx per PR7

- **Infeasibility Classification (2h)**
  - Update classification for remaining infeasible models
  - **Deliverable:** Updated infeasibility classification

### Priority 4: Translation Timeout & Internal Error (~4-6h)
- **Timeout Optimization (3-4h)**
  - 6 models still timeout at 300s (lop, mexls are largest)
  - Investigate sparse Jacobian, incremental computation approaches
  - **Deliverable:** Timeout analysis; fixes where feasible

- **Internal Error Triage (1-2h)**
  - 1 model with internal error during translation
  - **Deliverable:** Root cause and fix or documentation

### Pipeline Retest (~2h)
- Full pipeline at each checkpoint and final (per PR6)
- Track model_infeasible gross fixes and influx (per PR7)
- Use absolute counts and percentages (per PR8)
- Set targets against 147-model pipeline scope (per PR9)
- **Deliverable:** Updated `gamslib_status.json`; comprehensive metrics report

## Deliverables
- Alias-aware differentiation implementation with tests
- path_syntax_error compilation fixes and updated catalog
- model_infeasible Jacobian accuracy fixes with classification
- Translation timeout/error fixes
- Updated pipeline metrics with full pipeline at all checkpoints

## Acceptance Criteria
- **Solve:** ≥ 95 models solve (up from 86)
- **Match:** ≥ 55 models match (up from 49)
- **path_syntax_error:** ≤ 15 (down from 23)
- **path_solve_terminated:** ≤ 10 (down from 12)
- **model_infeasible:** ≤ 8 in-scope (down from 11)
- **Translate:** ≥ 97% of parsed models (≥ 143/147; up from 95.2%)
- **Parse:** ≥ 147/147 (maintain 100%)
- **Tests:** ≥ 4,400 (up from 4,364)
- **Quality:** All tests pass; all fixes have regression tests

**Estimated Effort:** 32-42 hours
**Risk Level:** MEDIUM (alias differentiation is a significant AD architectural change; error influx from translate recovery may offset solve gains)

---

# Sprint 25 (Weeks 15–16): Alias Differentiation Carryforward & Emitter Backlog

**Goal:** Land the alias-aware differentiation fix (carryforward from Sprint 24's Priority 1 workstream) and clear the emitter / stationarity bug backlog surfaced by the Day 13 review round. Push Match from 54 to ≥ 62 and Solve from 99 to ≥ 105. Apply Sprint 24 process recommendations: start the highest-leverage architectural fix on Day 1 and defend the reserved time (PR11 reinforcement); budget 80–100% influx for previously-timeout-excluded translate recoveries (PR13); run byte-stability regression tests across multiple `PYTHONHASHSEED` values (PR12); run a mid-sprint "read the generated MCP" review pass (PR14); freeze pipeline scope before Day 0 (PR15). (See `SPRINT_24/SPRINT_RETROSPECTIVE.md` §Sprint 25 Recommendations and §New Recommendations PR12–PR15 for details.)

**Note:** Sprint 24 retrospective identified 18+ issues labeled `sprint-25`. Alias-AD (#1138–#1147, #1150) is Priority 1 (highest leverage for Match); emitter backlog (#1275–#1281, #1283) is Priority 2 and the leverage point for the 5 "recovered translates that don't solve" from the Day 13 Addendum.

## Components

### Priority 1: Alias-Aware Differentiation Carryforward (#1138–#1147, #1150) (~24-32h)
- **Architectural Fix Completion (16-22h)**
  - Complete the summation-context / alias-match work started in Sprint 24
  - 11 open issues affecting ~20 models (CGE family, PS-family, cclinpts, polygon, himmel16, catmix, camshape, kand, launch, qabel/abel, meanvar, plus #1150 sum-index collapse)
  - Sprint 24 alias-AD KUs (KU-01..KU-08 in `SPRINT_24/KNOWN_UNKNOWNS.md`) capture the prep-phase classification and design context; `SPRINT_24/ANALYSIS_ALIAS_DIFFERENTIATION.md` and `SPRINT_24/DESIGN_ALIAS_DIFFERENTIATION_V2.md` document the Pattern A/B/C/D rollout. The Sprint 24 end-of-sprint KU that carries directly into Priority 1 is KU-32 (sameas guard runtime validation) — now tracked as Sprint 25 Unknown 1.5.
  - **Deliverable:** Alias-AD fix with comprehensive tests; dispatch canary + 54-model golden-file regression
- **Per-Pattern Validation (6-8h)**
  - Verify Pattern A (CGE, quadratic): 6 models
  - Verify Pattern C (offset-alias): polygon, himmel16, cclinpts (tied to #1143, #1145, #1146)
  - Verify Patterns B/D edge cases: kand (#1141), launch (#1142)
  - **Deliverable:** Per-pattern verification report; updated MCP output files
- **Impact Assessment (2h)**
  - Track movements: mismatch → match, infeasible → optimal, path_syntax_error → match
  - Document models that improve but don't fully resolve
  - **Deliverable:** Impact assessment; updated `gamslib_status.json`

### Priority 2: Emitter / Stationarity Bug Backlog (#1275–#1281, #1283) (~12-18h)
- **Fix #1283 First — Non-Deterministic Table Parsing (3-5h)**
  - Root-cause the non-determinism in multi-row-label tables like `(v1,v2,v3).col`
  - May have been confounding #1177 chenery investigation throughout Sprint 24
  - Add `PYTHONHASHSEED` variation test across 10 seeds (PR12)
  - **Deliverable:** Deterministic parser; byte-stability regression test
- **Emitter Bugs (7-10h total, parallelizable)**
  - **#1275** — presolve `$include` absolute paths → repo-relative emission (2-3h)
  - **#1276** — fawley duplicate `.fx` emission → emitter dedup (1-2h)
  - **#1280** — mathopt4 unquoted UELs with dots → unconditional single-quoting (1-2h)
  - **#1281** — lmp2 duplicate `Parameter` declarations → declared-symbol dedup (2-3h)
  - **Deliverable:** 4 emitter fixes with regression tests
- **Stationarity / KKT Bugs (2-3h, alias-AD adjacent)**
  - **#1277** — twocge `stat_tz` mixed offsets → may be subsumed by Priority 1 alias-AD
  - **#1278** — twocge `ord(r) <> ord(r)` tautology → index-substitution fix
  - **#1279** — robustlp `defobj(i)` scalar-equation widening → equation-domain inference guard
  - **Deliverable:** 3 stationarity fixes; chenery / twocge / robustlp verified solve-or-mismatch stable

### Priority 3: Multi-Solve Gate Extension (#1270) (~2-3h)
- **Extend Detector for saras-Style Top-Level `eq.m` Reads**
  - Approach A (cross-reference): flag `eq.m` reads whose receiving parameter later appears in another model's constraint body
  - Add saras + post-solve-reporting fixtures to detector test matrix
  - Regression guard: `ibm1`, `partssupply` continue translating
  - **Deliverable:** Updated `src/validation/driver.py`; saras flagged as driver

### Priority 4: Dispatcher Refactor (#1271) (~4-6h)
- **Collapse `_loop_tree_to_gams` and `_loop_tree_to_gams_subst_dispatch`**
  - Single parameterized dispatcher with optional `token_subst_map`
  - Byte-diff regression across all currently-solving MCPs
  - Eliminates the recurring "handler in one but not the other" bug class
  - **Deliverable:** Unified dispatcher; parity regression tests

### Priority 5: Translation Timeout — Algorithmic (#1169, #1185, #1192) (~4-6h)
- **Profile and Optimize Remaining 5 Timeouts (lower priority)**
  - `iswnm`, `mexls`, `nebrazil`, `sarf`, `srpchase` still time out at 600s
  - KU-19 / KU-20 in `SPRINT_24/KNOWN_UNKNOWNS.md` suggest profiling + sparse Jacobian
  - Day 13 Addendum showed that translate recovery alone is low-leverage for Match; prioritize only after Priorities 1 and 2 land
  - **Deliverable:** Profiling notes for each of the 5; at least one algorithmic fix landed if tractable

### Pipeline Retest (~2h)
- Full pipeline at each checkpoint and final (per PR6)
- Run 3× with different `PYTHONHASHSEED` values to verify #1283 fix (PR12)
- Track model_infeasible gross fixes and influx (per PR7)
- Use absolute counts and percentages (per PR8)
- Freeze scope before Day 0; no mid-sprint exclusions (PR15)
- Mid-sprint "read the generated MCP" review pass on 5–10 randomly-sampled models (PR14)
- **Deliverable:** Updated `gamslib_status.json`; comprehensive metrics report

## Deliverables
- Alias-aware differentiation fix (carryforward) with comprehensive tests
- 7 emitter / stationarity bug fixes (#1275–#1281)
- Non-deterministic parser fix (#1283) with byte-stability regression test
- Multi-solve gate extension for saras-style patterns (#1270)
- Unified loop-tree dispatcher (#1271)
- Profiling notes + optional algorithmic fix for at least 1 of 5 hard timeouts
- Updated pipeline metrics with full pipeline at all checkpoints, run under multiple hash seeds

## Acceptance Criteria
- **Solve:** ≥ 105 models solve (up from 99; +6 via alias AD)
- **Match:** ≥ 62 models match (up from 54; +8 via alias AD)
- **path_syntax_error:** ≤ 8 (down from 11; −3 via emitter fixes #1275–#1281)
- **path_solve_terminated:** ≤ 8 (down from 10)
- **model_infeasible:** ≤ 5 in-scope (down from 8; −3 via alias AD recovery)
- **Translate:** ≥ 96% of parsed models (≥ 137/143; up from 94.4%)
- **Parse:** ≥ 143/143 (maintain 100%)
- **Tests:** ≥ 4,550 (up from 4,522)
- **Determinism:** Full pipeline produces byte-identical output under at least 3 different `PYTHONHASHSEED` values (PR12 guard)
- **Quality:** All tests pass; all fixes have regression tests

**Estimated Effort:** 48-65 hours
**Risk Level:** MEDIUM-HIGH (alias-AD is the third sprint attempting this architectural change; the failure mode is drift into Sprint 24's outcome — "partial progress, rest deferred." PR11 defense of the Day-1–12 block is critical. Emitter backlog is additive and partially parallelizable so low risk; the #1283 non-determinism fix has uncertain scope until root-caused.)

---

# Sprint 26 (Weeks 17–18): Pattern C Generalization, Pattern A Reclassification & Sprint 25 Carryforward

**Goal:** Generalize the Pattern C launch-shape gate (#1306 narrowing) to handle plain-alias enumeration and `sameas`-decomposed SAM-block aliases, unblocking the four Sprint 25 Day-13 carryforward issues (#1354 camcge, #1355 cesam2, #1356 fawley, #1357 otpop) and removing the #1306 `xfail`. Reclassify the original Pattern A cohort per the Day 7 sweep. Re-verify Phase E carryforwards under the post-Sprint-25 emit pipeline. Land the Option 1 short-circuit for the 5 hard translation timeouts. Address the two open AD residuals (#1334, #1335) from the Day 11 fix-in-place series. Apply Sprint 25 process recommendations PR16–PR19 (and reaffirm PR14). Push Match from 60 to ≥ 64 and Solve from 104 to ≥ 108. (See `SPRINT_25/SPRINT_RETROSPECTIVE.md` §"Sprint 26 Recommendations" and §"What We'd Do Differently" for the per-priority and per-process-rec rationale.)

**Note:** Sprint 25 retrospective identified 23 issues labeled `sprint-26` (4 net-new from Day 13 + 19 carryforward including #1224 mine ParamRef IndexOffset; #1358 was filed and closed as duplicate of pre-existing #1224). Pattern C gate generalization is Priority 1 — the single highest-leverage workstream (4 path_syntax_error → solve = +4 Solve, +3–4 Match per the retrospective's targets table). Pattern A cohort reclassification (Priority 2) is groundwork for genuine Sprint 27 fixes; doesn't add net Match itself but is required so Sprint 27 doesn't replay the Day 5 hypothesis-validation-too-late mistake.

## Components

### Priority 1: Pattern C Gate Generalization (#1354, #1355, #1356, #1357, #1306, #1307) (~12-18h)
- **Generalize the Pattern C gate** (`src/kkt/stationarity.py`) to detect plain-alias enumeration (no `$cond` filter required) and `sameas`-decomposed SAM-block aliases. KU-33 captures the discovery: at least 4 CGE/SAM-balance models exhibit phantom `nu_<eq>(i±N)` enumeration on stationarity equations whose source bodies have no alias-conditional guard.
- **Pre-Sprint-0 hypothesis validation (PR16):** before committing the 12–18h budget, validate the "plain-alias variant of Pattern C" hypothesis on 2–3 representative models (e.g. camcge + cesam2 + fawley) using the Day 5 methodology — trace capture under `SPRINT25_DAY2_DEBUG=1` + emitted-artifact byte comparison against formal symbolic derivative. If the hypothesis is disproved on any of the three, replan the priority before Day 0.
- **Remove the #1306 `xfail`** — the original launch fix needs the proper sum-over-equation-domain rewrite (`sum(ss$ge(s,ss), -nu_dweight(ss))` instead of the over-counting per-offset enumeration). Bug #2 (#1307) lands in the same fix.
- **Pre-merge solve-time validation (PR19):** the structural emit change must pass a full PATH solve on each target model BEFORE merge — not just unit + compile-only. Sprint 25 #1308 passed unit + `action=c` validation but produced locally-infeasible MCPs at full solve.
- **Deliverable:** Generalized Pattern C gate with regression tests on camcge/cesam2/fawley/otpop; #1306 xfail removed; #1307 closed; estimated impact +3 to +5 path_syntax_error → solve.

### Priority 2: Pattern A Cohort Reclassification (#1138, #1139, #1140, #1142, #1145, #1150) (~4-6h)
- **Per `SPRINT_25/DAY7_COHORT_SWEEP.md` §"Classification Table":** the original Pattern A cohort is NOT actually Pattern A. Each issue needs reclassification to its true bug shape:
  - #1138 → Pattern C plain-alias variant (likely subsumed by Priority 1)
  - #1139 → AD-correct, pipeline-excluded (close with note)
  - #1140 → AD-correct multi-solve dynamics (separate investigation)
  - #1142 → Pattern C Bug #2 (#1307; subsumed by Priority 1)
  - #1145 → offset-handling/condition-guard bug (file new)
  - #1150 → split: qabel = Pattern C massive-enumeration variant; abel = AD-correct/solver noise
- **Action per issue:** close original with forward link to either an existing tracker or a new genuinely-classified issue.
- **Note:** #1311 (qabel/abel u-quadratic AD subset-domain bug) was identified during Sprint 25 Day 8 reassessment and CLOSED during Sprint 25 — that bug is fixed.
- **Deliverable:** 6 cohort issues closed/reclassified with `sprint-27`-labeled successors filed as needed; updated `SPRINT_25/AUDIT_ALIAS_AD_CARRYFORWARD.md` with the Day 7 classification.

### Priority 3: Pattern E Carryforward Re-Verification (#1141, #1144, #1147) (~4-6h)
- Phase E (Pattern E routing) was cancelled per the literal Checkpoint 2 NO-GO routing during Sprint 25. The three open Pattern E issues remain unresolved and may have shifted bucket via the Sprint 25 fix-in-place series #1338..#1352. Re-verify each before scoping fix work.
- **Deliverable:** Per-issue re-verification under the post-Sprint-25 emit pipeline; either fix or rescope (file new issues if shape changed; close with reclassification note if subsumed).

### Priority 4: Translation Timeout — Option 1 Short-Circuit (#885, #931, #932, #1185, #1228, #1224) (~4-6h)
- **5 hard timeouts** (`iswnm`, `mexls`, `nebrazil`, `sarf`, `srpchase`) plus the `mine` `internal_error` (#1224, ParamRef-valued IndexOffset). Per Sprint 25 Prep Task 8 (`SPRINT_25/PROFILE_HARD_TIMEOUTS.md`), all 5 timeouts share the `SetMembershipTest` / `enumerate_equation_instances` Cartesian-explosion pattern.
- **Implement Option 1 short-circuit** in `src/ad/index_mapping.py::enumerate_equation_instances` (with supporting behavior in `resolve_set_members` and the static `SetMembershipTest` failure path in `src/ir/condition_eval.py`). Should unblock at least srpchase and possibly iswnm.
- **Defer #1224 (mine ParamRef IndexOffset)** to a separate effort — the IndexOffset offset-as-Expr extension is a larger architectural change.
- **Deliverable:** Option 1 short-circuit landed with regression tests; srpchase translates; iswnm + nebrazil + sarf + mexls re-profiled to confirm whether they cross the budget after the fix.

### Priority 5: AD Residuals from Sprint 25 Day 11 Fix-In-Place Series (#1334, #1335) (~8-14h)
- **#1334:** `_add_jacobian_transpose_terms_scalar` (`src/kkt/stationarity.py:5279–5310`) wraps Jacobian terms in spurious `Sum(("t__",), ...)` when ParamRef domain is a strict subset of equation domain. Confirmed on otpop. Likely subsumes #1357.
- **#1335:** Missing `dzdef/dp` cross-term in `stat_p` when `zdef` references `p` via time-reversal-indexed offset. otpop residual after #1334 partial fix.
- Both target the `_replace_indices_in_expr` + `_add_jacobian_transpose_terms_scalar` pair in `src/kkt/stationarity.py`.
- **Pre-merge solve-time validation (PR19):** same as Priority 1 — full PATH solve on otpop BEFORE merge.
- **Deliverable:** Two AD fixes with unit + integration regression tests; otpop NLP-warm-started MCP converges to `pi ≈ 4217.80` (matches NLP).

### Process Recommendations from Sprint 25 (~8-12h)
- **PR16 — Pre-Sprint-0 hypothesis validation (already applied to Priority 1; document the methodology as a reusable prep task)** — codify in `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` as Task N: "Hypothesis validation for any multi-issue workstream sharing a single hypothesized root cause. Trace capture + emitted-artifact byte comparison against formal derivative on 2–3 representative models. Budget 1–2 prep days." (~2h)
- **PR17 — Bucket provenance column on `BASELINE_METRICS.md`** — add per-failing-model "Sprint 25 bucket → Sprint 26 bucket" provenance so net deltas don't hide composition changes. The Sprint 25 Day 14 SPRINT_LOG entry already does this informally — formalize it for Sprint 26. (~2-3h)
- **PR18 — Identify the Sprint 25 scope-shifted model** — run `git diff` between Sprint 25 Day 0 baseline `gamslib_status.json` and Day 14 final to identify which model's convexity status changed and document the reason in `BASELINE_METRICS.md` §5. (~1-2h)
- **PR19 — Pre-merge solve-time validation for structural emit changes** — extend CI to run a fast-suite `make test` PLUS a 30s PATH solve on a configurable target list when emit-affecting `.py` files change (any file under `src/emit/` or `src/kkt/stationarity.py`). PR #1308 (Pattern C gate that produced locally-infeasible MCP at solve time despite passing compile-only) would have been caught earlier. (~4-8h)
- **PR14 reaffirmation** (process, no code) — every PR that touches `src/emit/*.py` should have at least one regenerated `.gms` artifact from an affected model in the diff, and reviewers should read the relevant section. PR #1349 (clobbered `.l` overrides on clearlak) would have been caught at original merge with a 5-minute manual read. Add to `CONTRIBUTING.md` as a hard rule for emit-touching PRs. (~0h: process change only)
- **Deliverable:** PREP_PLAN.md with PR16 codified; updated BASELINE_METRICS.md with bucket provenance + scope-shift documentation; CI extension for emit-change solve-time validation; CONTRIBUTING.md updated.

### Pipeline Retest (~3h)
- Full pipeline at each checkpoint and final (per PR6)
- Run 3× with different `PYTHONHASHSEED` values (PR12 guard)
- Track model_infeasible gross fixes and influx (PR7)
- Use absolute counts and percentages (PR8)
- Freeze scope before Day 0; no mid-sprint exclusions (PR15)
- Mid-sprint "read the generated MCP" review pass on the 4 Pattern C target models (PR14 reaffirmation)
- **Deliverable:** Updated `gamslib_status.json` with bucket-provenance baseline; comprehensive metrics report.

## Deliverables
- Generalized Pattern C gate in `src/kkt/stationarity.py` with regression tests on camcge/cesam2/fawley/otpop and removed #1306 `xfail`
- 6 Pattern A cohort issues (#1138, #1139, #1140, #1142, #1145, #1150) closed/reclassified per Day 7 sweep with successor issues filed
- 3 Pattern E carryforward issues (#1141, #1144, #1147) re-verified and either fixed or rescoped
- Option 1 short-circuit landed in `src/ad/index_mapping.py::enumerate_equation_instances` (translates srpchase; possibly iswnm)
- AD fixes for #1334 + #1335 with regression tests on otpop
- New `BASELINE_METRICS.md` with bucket-provenance column (PR17) + scope-shift documentation (PR18)
- CI extension for pre-merge solve-time validation on emit-affecting changes (PR19)
- `CONTRIBUTING.md` rule for emit-PR `.gms` artifact diffs (PR14 reaffirmation)
- `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` codifying PR16 hypothesis-validation methodology
- Updated pipeline metrics with full pipeline at all checkpoints, run under multiple hash seeds

## Acceptance Criteria
- **Solve:** ≥ 108 models solve (up from 104; +4 via Pattern C generalization)
- **Match:** ≥ 64 models match (up from 60; +4 via combined Pattern C + #1334/#1335 AD fixes)
- **path_syntax_error:** ≤ 6 (down from 12; −6 via Pattern C removing camcge/cesam2/fawley/otpop)
- **path_solve_terminated:** maintain ≤ 5 (Sprint 25 floor)
- **model_infeasible:** maintain ≤ 4 (most carryforwards need investigative work)
- **Translate:** ≥ 135/142 (95%; +2 via Option 1 short-circuit unblocking srpchase + 1 of {iswnm, mexls, nebrazil, sarf})
- **Parse:** ≥ 142/142 (maintain 100%)
- **Tests:** ≥ 4,750 (up from 4,735)
- **Determinism:** Full pipeline produces byte-identical output under at least 3 different `PYTHONHASHSEED` values (PR12 guard)
- **Process recommendations:** PR16 codified; PR17 bucket provenance landed; PR18 scope-shifted model identified + documented; PR19 CI extension landed; PR14 reaffirmation added to CONTRIBUTING.md
- **Quality:** All quality gates pass; all fixes have regression tests; emit-touching PRs include regenerated `.gms` diffs

**Estimated Effort:** 50–75 hours over a 14-day sprint (Day 0 + Days 1–13). At ≤12 hours/day this fits within a 168-hour budget with substantial slack — the slack absorbs (a) unexpected Day 5 pivot work if the Priority 1 hypothesis validation disproves the gate-generalization premise, (b) Pattern A reclassification turning up a genuinely-fixable subset, and (c) the Option 1 short-circuit timing into iswnm/nebrazil profiling work.
**Risk Level:** MEDIUM — Pattern C gate generalization is the third sprint touching this code path (after Sprint 24's launch attempt and Sprint 25's narrow gate). Failure mode is the same drift seen in Sprints 24/25 alias-AD work: partial progress, rest deferred. Day 5 methodology applied PRE-Sprint-0 (PR16) is the primary mitigation. PR19 pre-merge solve-time validation specifically targets the structural-emit-change failure mode that bit Sprint 25's #1308 launch fix at solve time despite passing unit + compile-only validation.

---

# Sprint 27 (Weeks 19–20): Sprint 26 Carryforward — Pattern C Phase B + Phase A Gate Tightening + AD Architectural Redesigns

**Goal:** Land the four Sprint 26 close-and-refile architectural reclassifications (#1381 Pattern C Phase B, #1385 Option 1 short-circuit, #1390 kand AD architecture, #1393 scalar-eq Sum-collapse) + tighten the Phase A Pattern C gate predicate that regressed 15 non-target models in Sprint 26 (#1398). Address the comp_up subset/superset workstream (#1356 fawley + #1357 otpop), launch PATH-numerics divergence (#1378), in-place scalar-equation cross-term carryforward (#1335), mine ParamRef IndexOffset (#1224), and Day 6 close-and-refile carryforwards (#1387 cclinpts, #1388 camshape). Apply Sprint 26 retrospective process recommendations PR20 (Phase 0 acceptance gate) + PR21 (prep-task end-to-end emit verification) + PR22 (Day-0 mid-sprint script) + PR23 (CI-workflow PR checklist). Fix the pre-existing pipeline absolute-path leak (#1400). Push Match from 59 to ≥ 66 and Solve from 103 to ≥ 111. (See `SPRINT_26/SPRINT_RETROSPECTIVE.md` §"Sprint 27 Recommendations" and §"What We'd Do Differently" for per-priority and per-process-rec rationale.)

**Note:** Sprint 26 retrospective identified **14 issues labeled `sprint-27`** = 2 net-new from Day 13 (#1398 Phase A gate side-effect discovery + #1400 pipeline absolute-path leak) + 7 net-new from Sprint 26 reclassifications + close-and-refile across Days 1–9 (#1378 launch PATH numerics + #1381 Pattern C Phase B + #1385 Option 1 short-circuit + #1387 cclinpts + #1388 camshape + #1390 kand AD-architecture + #1393 scalar-eq Sum-collapse) + 1 reopened in-place Day 13 (#1335 per Day 9 intent) + 4 pre-existing carryforward (#1224 mine ParamRef IndexOffset + #1356 fawley comp_up + #1357 otpop comp_up + #1374 emit duplicate-init bugs). The Phase A gate tightening (#1398) is the single highest-leverage workstream — qdemo7 was matching at Day 0 before #1398 regressed it (+1 firm Solve and +1 firm Match recovery) AND PR19 target-list widening will cover the other 14 affected models against future regressions.

## Components

### Priority 1: Phase A Gate Predicate Tightening (#1398) (~10-14h)
- **Phase A's `_find_pattern_c_alias_sum` gate predicate fires too broadly** on Sums whose body multipliers are already correctly alias-indexed (no over-counting to consolidate). The Sprint 26 Day 1 PR #1379 consolidated zero-offset builder rewrite (launch fix) introduced 15 regression-affected models surfaced by PR #1399 review.
- **Affected models (15):** qdemo7 (compare_match → path_syntax_error), egypt + ferts + shale (path_solve_license → path_syntax_error), sambal + qsambal + harker + tfordy + dinam + ganges + gangesx + sroute (mismatch/license/other → mostly path_syntax_error or wrong-but-compiling emit), fawley (already in #1356 scope), srpchase + turkpow (compounded with translate recoveries).
- **Phase 0 acceptance gate (per Sprint 26 retrospective PR20):** hand-derive expected KKT shape on **8 anchor models** before committing any `src/kkt/stationarity.py` gate-predicate change: launch (Phase A's original target — verify byte-stability) + qdemo7 (`stat_xcrop(c)`) + ferts (`stat_z(p,i)`) + sambal (`stat_x(i,j)` cbal-derivative) + ganges (`stat_pls(r)`) + sroute (`stat_<network>`) + turkpow (`stat_zt(m,v,b,t)` — distinct inner-sum-of-bs-conditioned-products shape) + dinam (`comp_mb(i,t)` differentiate-vs-current-eq-index + `stat_ka(te)` row-multiplier-collapse — 2 distinct shapes). Verify prototype's regenerated `*_mcp.gms` matches byte-for-byte against the hand-derived form on each anchor.
- **PR19 target-list widening:** add launch (`tier=1` — currently NOT in PR19) + qdemo7 + ferts + sambal + ganges + sroute + turkpow + dinam to `.github/path-solve-ci-targets.txt` so similar gate-overreach catches surface at PR-review time.
- **Deliverable:** Tightened Phase A gate predicate that fires only on the launch-shape Pattern C case; 15 #1398-affected models verified clean (qdemo7 returns to compare_match; egypt/ferts/shale return to path_solve_license; sambal/qsambal/harker/tfordy/dinam/ganges/gangesx/sroute/turkpow return to their Day 0 baseline bucket); launch byte-stable vs Sprint 26 final emit; PR19 target list widened.

### Priority 2: Pattern C Phase B Redesign (#1381) (~10-16h)
- **Build the consolidated multiplier term explicitly from the source Sum's body structure** (positions preserved), intercepting BEFORE element-to-set substitution. Per Sprint 26 Day 3 reclassification: Phase A's swap-based approach is launch-shape-specific and doesn't generalize to plain-alias bodies (camcge/cesam2) because element-to-set substitution collapses the alias name before the swap fires.
- **Phase 0 acceptance gate (per Sprint 26 retrospective PR20):** hand-derived KKT shape on `nu_ieq` cross-term for camcge (per #1381 issue body). Verify prototype's regenerated `camcge_mcp.gms` matches byte-for-byte against the hand-derived form.
- **Deliverable:** Pattern C Phase B redesign landed; camcge + cesam2 unblocked from path_syntax_error to compare_match; #1381 closed.

### Priority 3: AD Architectural Redesigns (#1390, #1385, #1393) (~30-48h combined)

Three Sprint 26 reclassifications targeting different AD pipeline subsystems. **All three require Phase 0 acceptance gates BEFORE any src/ commits per Sprint 26 retrospective PR20.**

- **#1390 (kand) per-instance enumeration architecture redesign for tree-predicate-aliased Sums (~10-16h)** — The cross-term enumeration step in `_compute_equality_jacobian` / `_compute_inequality_jacobian` (`src/ad/constraint_jacobian.py:903` / `:1027`) iterates over each static `n`-element as a wrt-candidate, producing one cross-term per element-substitution; for kand this generates 22 phantom-offset `lam_dembalx(j,t+1,n+k)` terms instead of a single predicate-guarded Sum. Phase 0: hand-derived KKT for `stat_y(j,t,n)` cross-term.
- **#1385 (Option 1 short-circuit) (~10-16h)** — Symbolic-instance handling in downstream AD/emit pipeline OR alternative short-circuit shape compatible with concrete indices. The Sprint 26 Day 4 attempt produced syntactically-correct emit + GREEN quality gates but broken multiplier references downstream because `_build_symbolic_instance_placeholder` returned the set name as the index. Phase 0: end-to-end emit verification on srpchase. Unblocks iswnm/mexls/nebrazil/sarf translates.
- **#1393 + #1335 (scalar-eq Sum-collapse from #1334) (~10-16h combined)** — `_sum_should_collapse` (`src/ad/derivative_rules.py:2556`) + `_is_concrete_instance_of` (`:2607`) symbolic-superset-of-subset-iter collapse. #1335 has 3 competing approaches documented per Day 9 SPRINT_LOG (extend `_expand_sums_with_unresolved_offsets` + fix downstream re-symbolization; resolve `card-ord` symbolically without expansion; hybrid post-AD collapse to symbolic-Sum). Phase 0: hand-derived KKT for `stat_x(tt)` / `stat_p(tt)` on otpop.
- **Deliverable:** Three AD-architecture redesigns landed with byte-stable regression tests on Tier 0/1 + Pattern C target sets; #1390 kand cross-term reduces from 22 to 1; #1385 srpchase translates cleanly; #1393 + #1335 otpop solves with `pi ≈ 4217.80` matching NLP.

### Priority 4: launch PATH-Numerics Investigation (#1378) (~6-12h)
- **Phase A's mathematically-correct KKT diverges PATH residuals vs Day 0's over-counted-but-tractable form.** Sprint 25 #1351 emitted a different multiplier system (per-row weighted; same primal but different multipliers) that PATH found a numerical fix for; Phase A's mathematically-correct emit produces a different system that PATH stalls on (MODEL STATUS 5 Locally Infeasible, 6194 iterations, `defvt` residual ~3.2e+04).
- **Investigates:** PATH initial-point tuning, preprocessing options (`--nlp-presolve`), NLP-warm-start (use NLP solution as MCP starting point), sign/scaling refinement in `_apply_pattern_c_swap_to_term`. Numerical-conditioning problem, not a correctness regression.
- **Deliverable:** launch MODEL STATUS 1 (or model_optimal_presolve recovery) with matching solution; #1378 closed.

### Priority 5: comp_up Subset/Superset Workstream (#1356 fawley + #1357 otpop) (~8-12h)
- Both fawley (#1356) and otpop (#1357) exhibit `$171` domain violations in `comp_up_x(tt)$(t(tt) and xb(tt) < inf)..` and `piU_x.fx(tt)$(...)` (same shape). Per Sprint 26 Task 4 PATTERN_A_RECLASSIFICATION_PLAN, the fix is a **"comp_up subset/superset domain widening"** workstream in `src/kkt/complementarity.py` + `src/emit/emit_gams.py`.
- **Phase 0 acceptance gates need to be authored** — current `docs/issues/ISSUE_1356_*.md` and `ISSUE_1357_*.md` files don't have formal Phase 0 sections. Sprint 27 prep should author them before src/ implementation.
- **Deliverable:** fawley + otpop unblocked from path_syntax_error; #1356 + #1357 closed.

### Priority 6: #1224 mine ParamRef IndexOffset (~6-10h)
- `src/ad/index_mapping.py` UserWarning on `IndexOffset(ParamRef)`. Sprint 26 Task 6 deferred per "architectural extension orthogonal to Option 1 short-circuit". Can address standalone or bundle with Priority 3 #1385 work (both touch the AD index_mapping subsystem).
- **Deliverable:** mine translates from translate_internal_error to translate_success; MCP solve outcome documented (may still hit path_syntax_error or other downstream issues — Solve gain is conditional per Sprint 26 retrospective Solve target rationale).

### Priority 7: Day 6 Close-and-Refile Carryforwards (#1387 cclinpts + #1388 camshape) (~6-12h)
- **#1387 cclinpts:** condition-guard/sign bug producing ~70% rel_diff (post-Pattern-A reclassification per Sprint 26 Day 6). Phase 0 acceptance gate needs to be authored — `docs/issues/ISSUE_1387_*.md` only has investigation pointers, no formal Phase 0.
- **#1388 camshape:** MCP solves to Locally Infeasible (post-Pattern-E reclassification per Sprint 26 Day 6). `docs/issues/ISSUE_1388_*.md` has an investigation pointer mentioning "hand-derived KKT for camshape" but no formal Phase 0 acceptance-gate section.
- **Deliverable:** Both issues either fixed or scoped with formal Phase 0 + Sprint 28 carryforward filing if intractable in Sprint 27 budget.

### Priority 8: Pipeline Absolute-Path Leak Fix (#1400) (~2-4h)
- **Correction (per Sprint 27 PR #1402 review):** the original filing referenced a non-existent file `scripts/gamslib/solve_mcp.py` and incorrectly attributed a second leak source to `warnings.formatwarning`. Verified facts: (a) the `mcp_file_used` field is assigned at `scripts/gamslib/run_full_test.py:899` (`model["mcp_solve"]["mcp_file_used"] = str(presolve_path)` where `presolve_path` is `PROJECT_ROOT`-anchored), not in a `solve_mcp.py` module; (b) there is no `warnings` module usage anywhere in `scripts/gamslib/` (`grep -lE "warnings\." scripts/gamslib/*.py` returns nothing); (c) `solve_mcp()` is a function at `scripts/gamslib/test_solve.py:911` that calls `subprocess.run(..., capture_output=True)` but discards stdout/stderr (no `result = ...` capture) — the error message stored in the status dict is synthesized from parsed `.lst` content via `parse_gams_listing(...)`, so subprocess stderr is NOT a leak channel either.
- **Confirmed leak source:** `scripts/gamslib/run_full_test.py:899` `mcp_file_used` assignment. Fix to repo-relative paths against `PROJECT_ROOT` (or basename only — file is always at `data/gamslib/mcp/<model>_mcp_presolve.gms` per Sprint 25 #1345/#1346/#1347 cwd convention).
- **Audit-driven approach for additional leak sources:** Priority 8 implementation must run `grep -oE "\"[^\"]+\": \"/[^\"]+\"" data/gamslib/gamslib_status.json | sort -u` against a recent pipeline-run JSON to identify any other absolute-path fields. Note: the key match uses `"[^"]+"` (any non-quote string) rather than `"[a-z_]+"` because the JSON contains keys with digits like `_migration_summary_v2_2_1`; a narrower regex could silently miss leak fields. If `mcp_file_used` is the only leak, Priority 8 effort is at the low end of 2–4h.
- **Deliverable:** Pipeline no longer leaks developer-local absolute paths into `gamslib_status.json`; next pipeline retest produces byte-identical JSON across different developer machines (modulo wall-time fields).

### Priority 9: Emit Duplicate-Init Bugs (#1374) — observation-style (~2-4h investigation; defer fix to Sprint 28 if Sprint 27 budget is consumed)
- Sweep regenerated `*_mcp.gms` artifacts for duplicate `var.l(idx) = val` assignments (e.g., the Sprint 26 Day 13 finding on ganges `taum.l('cap-good')` after the generic `taum.l(i)` init). Pattern matches Sprint 25 #1349 clearlak finding.
- **Deliverable:** corpus-wide audit; targeted fix in `src/emit/` for the most common shapes; defer remaining shapes to Sprint 28 if Sprint 27 budget tight.

### Process Recommendations from Sprint 26 Retrospective (~8-12h)
- **PR20 — Phase 0 acceptance gate codification (~2-3h):** Add Phase 0 sections to `docs/issues/ISSUE_1356_*.md`, `ISSUE_1357_*.md`, `ISSUE_1387_*.md`, `ISSUE_1388_*.md` (currently missing per Sprint 26 retrospective Acknowledgments inventory). Codify Phase 0 methodology in CONTRIBUTING.md as a hard rule for any issue whose Phase 1 design touches `src/ad/`, `src/kkt/`, or `src/emit/`.
- **PR21 — Prep-task end-to-end emit verification (~2-3h):** Add to Sprint 27 PREP_PLAN.md a sub-task per workstream for empirical end-to-end correctness verification (translate one concrete target model with a prototype patch + verify GAMS compile-clean + KKT body shape against hand-derived Lagrangian). Codify as a reusable prep-task template.
- **PR22 — Day-0 / mid-sprint script (~2-3h):** Build `scripts/sprint_audit/changed_emit_artifacts.py` that scans `git log --since=<sprint-start>` for emit-affecting `data/gamslib/mcp/*.gms` changes (broad glob covers `*_mcp.gms` + `*_mcp_presolve.gms`) and auto-generates the PR14 review list + retest comparison surface. Avoids prompt-staleness on mid-sprint reclassifications (Sprint 26 Day 12 PLAN_PROMPTS.md staleness was the trigger).
- **PR23 — CI-workflow PR self-review checklist (~2-3h):** Add to CONTRIBUTING.md §"CI Workflow PR Checklist" covering input validation, pagination, fork tolerance, schema validation, error handling, marker uniqueness, logging visibility. Sprint 26 PR #1396 (PR19 CI extension) needed 11 rounds of Copilot review; a pre-merge self-review against this checklist would have compressed that to ~3-4 rounds.
- **Deliverable:** 4 Phase 0 sections authored on backlog issues; updated CONTRIBUTING.md with Phase 0 rule + CI-workflow PR checklist; new prep-task template; new script.

### Pipeline Retest (~3h)
- Full pipeline at each checkpoint (Day 5 + Day 10) and final (Day 13) per PR6
- Run final retest under multiple `PYTHONHASHSEED` values (PR12 byte-stability guard)
- Track model_infeasible gross fixes and influx (PR7); use absolute counts and percentages (PR8); freeze scope before Day 0 (PR15)
- Mid-sprint "read the regenerated MCP" review pass (PR14 reaffirmation) on emit-affected artifacts per PR22 auto-generated list
- **Deliverable:** Updated `gamslib_status.json` with bucket-provenance baseline; comprehensive metrics report comparing Sprint 26 final → Sprint 27 final.

## Deliverables
- Tightened Phase A Pattern C gate predicate in `src/kkt/stationarity.py` with regression tests on 8 anchor models (#1398)
- Pattern C Phase B redesign landed; camcge + cesam2 unblocked (#1381)
- Three AD architectural redesigns: kand per-instance enumeration redesign (#1390), Option 1 short-circuit redesign (#1385), scalar-eq Sum-collapse (#1393 + #1335)
- launch PATH-numerics fix or NLP-warm-start solution (#1378)
- comp_up subset/superset domain widening for fawley + otpop (#1356 + #1357)
- mine ParamRef IndexOffset support in `src/ad/index_mapping.py` (#1224)
- Day 6 close-and-refile fixes for cclinpts + camshape (#1387 + #1388) or formal Phase 0 + Sprint 28 carryforward filing
- Pipeline absolute-path leak fix in `scripts/gamslib/run_full_test.py:899` (`mcp_file_used` assignment; the original filing's reference to a `scripts/gamslib/solve_mcp.py` file was incorrect — no such file exists) (#1400)
- Emit duplicate-init bug investigation + targeted fixes (#1374)
- PR19 target-list widening to cover all 15 #1398-affected models + launch
- 4 Phase 0 acceptance-gate sections authored on backlog issues (#1356, #1357, #1387, #1388) per PR20
- Updated CONTRIBUTING.md with PR20 Phase 0 rule + PR23 CI-workflow PR checklist
- New `scripts/sprint_audit/changed_emit_artifacts.py` per PR22
- Updated Sprint 27 PREP_PLAN.md with PR21 end-to-end emit verification prep-task template
- Updated pipeline metrics + Sprint 27 SPRINT_LOG.md + SPRINT_RETROSPECTIVE.md

## Acceptance Criteria
- **Solve:** ≥ 111 models solve (up from 103; +6 firm + 2 conditional per Sprint 26 retrospective Sprint 27 target rationale — firm: #1381 camcge/cesam2 [+2] + #1398 qdemo7 recovery [+1] + #1357 otpop [+1] + #1356 fawley [+1] + #1388 camshape [+1]; conditional: #1385 [+1 conditional on iswnm/mexls/nebrazil/sarf subsequently solving] + #1224 [+1 conditional on mine subsequently solving cleanly])
- **Match:** ≥ 66 models match (up from 59; +7 via #1381 [+2] + #1398 qdemo7 [+1] + #1357 [+1] + #1356 [+1] + #1378 launch mismatch→match [+1] + #1390 kand mismatch→match [+1])
- **path_syntax_error:** ≤ 6 (down from 17; −11 via #1398 fixing up to 9 currently-affected models + #1381 fixing camcge/cesam2 + #1357 fixing otpop, well above the 11 needed; #1356 fawley single-counted with #1398)
- **path_solve_terminated:** maintain ≤ 5 (Sprint 26 floor)
- **model_infeasible:** ≤ 3 (down from 4; −1 via camshape #1388 fix)
- **Translate:** ≥ 135/142 (up from 134/142; +1 via #1385 unblocking iswnm/mexls/nebrazil/sarf OR #1224 unblocking mine)
- **Parse:** ≥ 142/142 (maintain 100%)
- **Tests:** ≥ 4,750 (up from 4,737)
- **Determinism:** Full pipeline produces byte-identical output under at least 3 different `PYTHONHASHSEED` values (PR12 guard)
- **Process recommendations:** PR20 Phase 0 acceptance gate codified + 4 backlog issues' Phase 0 sections authored; PR21 prep-task template codified; PR22 mid-sprint script landed; PR23 CI-workflow PR checklist added to CONTRIBUTING.md
- **PR19 widening:** target list widened to cover all 15 #1398-affected models + launch
- **Quality:** All quality gates pass; all fixes have regression tests; emit-touching PRs include regenerated `.gms` diffs (PR14 reaffirmation)

**Estimated Effort:** 97–157 hours over a 14-day sprint (Day 0 + Days 1–13). At ≤ 12 hours/day this fits within a 168-hour budget (14 × 12 = 168) with substantial slack at the lower bound. Per-priority budgets: P1 #1398 [10–14h] + P2 #1381 [10–16h] + P3 AD redesigns [30–48h combined] + P4 #1378 [6–12h] + P5 #1356/#1357 [8–12h] + P6 #1224 [6–10h] + P7 #1387/#1388 [6–12h] + P8 #1400 [2–4h] + P9 #1374 [2–4h] + process recs PR20–23 [8–12h] + pipeline retest [3h] = 91–147h estimated work-item total, plus ~6–10h prep tasks (totals 97–157h). The range upper bound assumes all 9 priorities + 4 process recs ship; the lower bound assumes Priorities 7–9 + some process recs slip to Sprint 28. Heaviest day budget: Day 4 (~10h: P1 #1398 fix-surface validation + parallel P5 comp_up prep). Slack absorbs (a) Day 5 hypothesis-validation pivot work for any Priority 3 AD redesign, (b) #1335's 3-approaches-to-evaluate uncertainty, (c) PR review iteration overhead for the emit-affecting PRs.
**Risk Level:** HIGH — Sprint 27 carries 4 architectural-redesign tracks from Sprint 26 reclassifications (Priorities 1, 3 × 3 sub-priorities) + 4 carryforward issues (Priorities 5, 6, 7 × 2 sub-priorities) + the Sprint 26 emit-regression cleanup (Priority 1 #1398). Failure mode is the same drift seen across Sprints 24/25/26 alias-AD work: partial progress on the AD pipeline subsystems, rest deferred to Sprint 28. The Phase 0 acceptance gate (PR20) is the primary mitigation — each Priority 3 sub-priority must pass Phase 0 (hand-derived KKT shape verified byte-stable on a concrete target) BEFORE committing src/ implementation effort. Sprint 26's Day 9 PR #1394 review hand-derived-KKT catch (#1335 rolled back after green quality gates) is the canonical case showing Phase 0 catches regressions that unit tests + integration tests miss.

---

# Sprint 28 (Weeks 21–22): Sprint 27 Carryforward — KKT Cross-Term Correctness, AD Architectural Fixes & Diagnostic/CI Tooling

**Goal:** Land the Sprint 27 Solve/Match carryforwards — the AD/KKT cross-term and architectural fixes deferred from the alias-AD workstream (#1224, #1388, #1393+#1335, #1387, #1390, camcge) — and build the diagnostic + CI tooling the Sprint 27 retrospective recommended (golden-staleness CI check, KKT-residual verification harness, embedded-NLP-divergence detector, AD cross-term property tests) so the bug classes that recurred across Sprints 24–27 are caught systematically rather than re-diagnosed by hand each sprint. Finish the Sprint 27 lower-priority cleanups (#1374 `.l` shape, #1400 `message`-field leak, #1385 runtime-guard cross-terms). Push Solve from 105 to ≥ 110 and Match from 62 to ≥ 65. (See `SPRINT_27/SPRINT_RETROSPECTIVE.md` §"Sprint 28 Recommendations" + §"What We'd Do Differently" for per-priority and per-process-rec rationale.)

**Note:** All Priority-1–6 fixes carry forward from Sprint 27 with a documented Phase-0 diagnosis already in their `docs/issues/ISSUE_*.md` files — Sprint 28 starts from a known fix-surface for most, **except where Sprint 27 proved the prep-doc surface wrong** (see Process Recommendation §"PR24"). The single highest-leverage Solve workstream is **#1224 + #1388**: both are AD/KKT cross-term defects with a hand-derived target shape already recorded (+1 Solve each, firm). The PATH-author-consultation / solution-forcing / release work that previously occupied Sprint 28 moves to **Sprint 29** (and Sprints 30/31) — see the renumbered sections below.

## Components

### Priority 1: #1224 mine — Parameter-Valued-Offset KKT Cross-Term Inversion (~10–14h)
- **mine now translates (Sprint 27 #1224) but is `model_infeasible`** because the `stat_x` cross-term from the `pr` constraint does not **invert** the parameter-valued offset: the emit produces `sum(k, lam_pr(k,l,i,j))` where the correct stationarity is `sum(k, lam_pr(k, l, i-li(k), j-lj(k))) - sum(k, lam_pr(k, l-1, i, j))`. The translate fix (Sprint 27, `src/ir/ast.py` emit render) is the prerequisite; this is the AD/Jacobian cross-term inversion the #1224 prep named (`src/ad/constraint_jacobian.py` / `src/ad/derivative_rules.py:2793`).
- **Phase 0 acceptance gate (PR20):** hand-derive `stat_x(l,i,j)` for mine including the inverse-offset `lam_pr` term + the `l-1` term; verify the regenerated `mine_mcp.gms` matches byte-for-byte and the NLP KKT point satisfies the emitted `stat_x` (residual ≈ 0 via the Priority-9 KKT-residual harness).
- **Deliverable:** mine → MODEL STATUS 1 with matching solution (or a documented residual proving the cross-term is now correct); #1224 closed. +1 Solve (firm), +1 Match (conditional on the solve matching the NLP optimum).

### Priority 2: #1388 camshape — Case-(b) `stat_r` Stationarity-Emit Divergence (~6–10h)
- **Sprint 27 Day 11 §4.6 discriminator classified camshape Case (b)** (non-inert emit bug, NOT non-convexity): from a verified-complete NLP-KKT warm-start the MCP returns MODEL STATUS 5 with `stat_r(i1)` INFES ≈ 396. The subset-corruption co-bug (#1424) already landed in Sprint 27; this is the remaining `stat_r` cross-term defect.
- **Phase 0 acceptance gate (PR20):** per-term hand-derivation of `stat_r(i)` (interior + edge `lam_convex_edge*` cross-terms) vs the emit at `src/kkt/stationarity.py:1835` (`_build_indexed_stationarity_expr`) — pin the missing/mis-signed balancing term; verify with the KKT-residual harness (NLP KKT point residual ≈ 0 post-fix).
- **Deliverable:** camshape → MODEL STATUS 1 (area ≈ 4.2841); #1388 closed. +1 Solve (firm).

### Priority 3: #1393 + #1335 otpop — Scalar-Eq Sum-Collapse + `card(t)-ord(t)` Offset Evaluator (~12–16h combined)
- **Now confirmed two distinct fixes** (Sprint 27 Day 0 proved #1393's Approach C inert). **#1393:** the over-counted `sum(t__, del(t__)…·nu_kdef)` cross-term in `stat_x(tt)`/`stat_p(tt)` must collapse — redirected to the **`stationarity.py` symbolic-collapse path** (where `t→t__` aliasing occurs), NOT `_is_concrete_instance_of`. **#1335:** the missing `nu_zdef` cross-term needs a `_try_eval_offset` extension that resolves symbolic-base `IndexOffset`s with `card(t)-ord(t)` arithmetic without Sum expansion (Approach B).
- **Phase 0 acceptance gate (PR20):** hand-derived `stat_x('tt-elem')` + `stat_p('1990')` KKT vs the regenerated `otpop_mcp.gms`; PATH solve to `cost ≈ 4217.80` (NLP optimum).
- **Deliverable:** otpop unblocked from `model_infeasible` → solve + match; #1393 + #1335 closed. +1 Solve, +1 Match (firm).

### Priority 4: #1387 cclinpts — Three Coupled AD Changes (~12–18h)
- Per the Sprint 27 Day-6 binding diagnosis, cclinpts needs **three coupled changes**: (1) the AD objective-gradient **offset-enumeration** in `_diff_sum` (the missing j+1 cross-terms; the per-instance math was residual-verified to 5e-8); (2) a **gradient→stationarity re-symbolization anchor fix** so a pure-offset term anchors on the differentiated variable's own column index (not an arbitrary element); (3) a **non-convex warm-start** (PATH cold-converges to a spurious degenerate KKT point `b≈const`). The "sign-flip" framing from the original filing is a **misdiagnosis** (the `(-1)` is the standard maximize negation — do NOT touch sign logic).
- **Phase 0 acceptance gate (PR20):** the eliminated-KKT residual check at the NLP optimum (`objgrad_b(j) + b(j)^(−γ)·objgrad_fb(j) = 0`, max|r| ≤ 1e-6) on the regenerated emit; high-blast-radius AD change → full-corpus byte-stability + re-solve verification required.
- **Deliverable:** cclinpts → MODEL STATUS 1 with `rel_diff < 1%`; #1387 closed. +1 Match (firm, contingent on all three changes landing together — REPLAN to Sprint 29 if the re-symbolization anchor fix proves architectural).

### Priority 5: #1390 kand — Re-Diagnose the True Mismatch Source (~8–14h)
- Sprint 27 **proved the phantom-term collapse is inert** (collapsing the 22 `lam_dembalx` terms is solution-equivalent; MCP stays `cost = 195.0` ≠ NLP `2613.0`). The real defect is elsewhere. **Re-diagnosis surfaces (per Sprint 27 Day 5):** the `bal(j,t,n)`/`x` stationarity, the `t-1`↔`t+1` lag duality, or the LP first-stage/recourse coupling.
- **Phase 0 acceptance gate (PR20):** a fresh Day-0 trace (per PR24) to localize the 195-vs-2613 gap to a specific stationarity/complementarity row via the KKT-residual harness, BEFORE any src change; the phantom-term re-symbolization is explicitly out of scope (proven inert).
- **Deliverable:** root cause localized + fixed (→ +1 Match) OR a re-scoped Phase-0 filing if the gap is a deeper LP-recourse-coupling architectural issue (→ Sprint 29 with the new diagnosis). Diagnosis-first: REPLAN-friendly.

### Priority 6: camcge — Singular-Jacobian CGE Degeneracy (~8–14h)
- camcge translates `action=c`-clean (Pattern C Phase B emit is correct) but the MCP is `model_infeasible` from a **singular-Jacobian CGE degeneracy** — distinct from Pattern C. Investigate: a redundant market-clearing / Walras-law row (one equation is linearly dependent), variable normalization (a price numéraire fix), or a PATH preprocessing/scaling option.
- **Phase 0 acceptance gate (PR20):** identify the singular row(s) via the PATH listing's basis-singularity report + a Jacobian rank check at the NLP point; verify the proposed fix (numéraire fix / redundant-row drop) preserves the economic solution.
- **Deliverable:** camcge → MODEL STATUS 1 OR a documented "inherent CGE degeneracy needs formulation change" finding (→ observation task / Epic 5). +1 Solve (conditional).

### Priority 7: Sprint 27 Lower-Priority Cleanups (~8–12h)
- **#1374 `.l` denominator/override dedup (robot)** — the second duplicate-init shape (robot's `rho.l('h0') = 4.5;` emitted by both the denominator-init block and the `fx_to_l_override`). Dedup at emit time; regenerate robot; KU follow-through.
- **#1400 `message`-field captured-warning path relativization** — the second absolute-path leak (captured warning text containing `…/src/…py:NNN`). Relativize paths in the warning-capture path so `gamslib_status.json` is fully machine-portable (the Sprint 27 #1400 fix covered `mcp_file_used` only).
- **#1385 runtime-guard cross-terms** — the deferred srpchase cross-term emit (`J_gᵀ·lam`) coupled with the runtime-guard equation-body re-emit (`src/kkt/stationarity.py`); must land together (re-emit without cross-terms = inconsistent MCP).
- **Deliverable:** #1374 fully closed; #1400 fully closed; #1385 cross-terms landed or re-scoped.

### Priority 8 (Infrastructure): Golden-Staleness Sweep + CI Check (~8–12h)
- **Sprint 27 retrospective "What We'd Do Differently #3":** several `*_mcp.gms` / `*_mcp_presolve.gms` goldens (cesam/fawley/korcge/dinam) silently drifted from current emit, surfacing as noise in unrelated PRs (Days 9/10/13). Build a check that regenerates every translating model's golden and fails if it differs from the committed artifact (modulo a documented allowlist of known-failing/non-deterministic models).
- **Components:** `scripts/sprint_audit/check_golden_staleness.py` (regenerate → diff → report); a CI job (`.github/workflows/`) running it on PRs that touch `src/{ad,kkt,emit,ir}/`; a `make regen-goldens` target to refresh in bulk.
- **Deliverable:** golden-staleness check + CI integration; a one-time corpus refresh commit clearing the existing drift (cesam/fawley/korcge/dinam/…); CONTRIBUTING.md note.

### Priority 9 (Infrastructure): KKT-Residual Verification Harness (~10–14h)
- **Sprint 27 retrospective "What Went Well #2":** the GDX warm-from-good-optimum experiment (solve NLP → unload solution → load into the MCP → check whether the NLP KKT point satisfies the emitted stationarity) became the standard tool for distinguishing an **emit bug** (Case b — residual ≠ 0 at the NLP KKT point) from **non-convexity** (Case c — residual ≈ 0 but PATH diverges). Formalize it as reusable tooling — it directly supports Priorities 1, 2, 5.
- **Components:** `scripts/diagnostics/kkt_residual.py` — given a model, solve the NLP (or load a provided GDX), warm-start the MCP from that solution + transferred duals, and report per-row stationarity/complementarity residuals + a Case-(a/b/c) verdict; integrate into the PR20 Phase-0 "Verification Methodology" template as a standard command.
- **Deliverable:** the KKT-residual harness + docs; PR20 template updated to reference it; applied to ≥ 3 carryforward models (mine/camshape/kand) as its first consumers.

### Priority 10 (Infrastructure): Embedded-NLP-Divergence Detector + AD Cross-Term Property Tests (~12–16h)
- **Sprint 27 retrospective "What Went Well #2":** the "**embedded NLP pre-solve diverges from standalone**" bug class (the `$include` re-running source statements under `$onMultiR`) drove two of the sprint's wins (#1378 launch double-applied param; #1424 camshape subset corruption). Build a detector + a structural test class so this is caught automatically.
- **Components:** (a) `scripts/diagnostics/check_presolve_divergence.py` — for each `--nlp-presolve` model, compare the embedded NLP objective to the standalone NLP objective and flag divergence (would have caught #1378 + #1424 at translate time); (b) AD cross-term **property tests** — generate small synthetic models with a known hand-derived KKT (offset sums, alias sums, parameter-valued offsets) and assert the emit's stationarity cross-terms match, systematically guarding the #1224/#1388/#1390 cross-term defect class.
- **Deliverable:** presolve-divergence detector (CI-runnable on presolve models) + ≥ 6 AD cross-term property tests covering the recurring shapes; both wired into CI.

### Pipeline Retest (~4h)
- Full pipeline at each checkpoint (Day 5 + Day 10) and final (Day 13) per PR6; run the final retest under ≥ 3 `PYTHONHASHSEED` values (PR12 determinism guard).
- Use the PR22 audit script (`changed_emit_artifacts.py --since-commit <Day-0 SHA>`) for the retest comparison surface; the new golden-staleness check (Priority 8) replaces the ad-hoc "measure, don't sweep" reconciliation from Sprint 27.
- **Deliverable:** updated `gamslib_status.json` (machine-portable paths) + Sprint 26→27→28 metrics comparison; determinism verified.

## Process Recommendations from Sprint 27

Derived from `SPRINT_27/SPRINT_RETROSPECTIVE.md` §"What We'd Do Differently". (PR20–PR23 from Sprint 26 are already delivered and remain in force; these extend them.)

- **PR24 — Day-0 fix-surface trace (~2–3h to codify):** prep-doc `file:line` fix surfaces were **wrong 4× in Sprint 27** (Days 0/6/11/12 — the real surfaces were `stationarity.py`, `src/ir/ast.py`, the emit restore pass, NOT the AD sites the prep named). Codify in CONTRIBUTING.md / the Phase-0 template a hard rule: **prep records the symptom + reproducer only; the fix surface is established by a Day-0 trace, never trusted from the prep doc.** Phase-0 PROCEED requires citing the *traced* surface.
- **PR25 — Projection discipline (bucket-forward vs genuine gain) (~1–2h to codify):** the Day-0 "+6 firm Match" over-counted because it assumed `path_syntax_error → model_infeasible` **bucket-forward** moves (fawley/otpop/camcge) were Solve/Match gains. Codify: Solve/Match projections must label each delta as a genuine bucket-to-success transition vs a forward move within the failure set; only the former counts toward the target.
- **PR26 — Golden-staleness CI check (Priority 8 above):** the recurring silent golden drift gets a CI gate (delivered as Priority 8).
- **PR27 — KKT-residual harness as a standard Phase-0 tool (Priority 9 above):** the Case-(a/b/c) discriminator is mechanized and referenced from the Phase-0 "Verification Methodology" template (delivered as Priority 9).
- **Deliverable:** CONTRIBUTING.md updated with PR24 + PR25 rules; the Phase-0 template references PR24 (traced surface) + PR27 (KKT-residual harness).

## Deliverables
- #1224 parameter-valued-offset KKT cross-term inversion (`src/ad/`) — mine solves (Priority 1)
- #1388 camshape `stat_r` cross-term fix (`src/kkt/stationarity.py`) — camshape solves (Priority 2)
- #1393 + #1335 otpop scalar-eq Sum-collapse + `card(t)-ord(t)` evaluator — otpop solves + matches (Priority 3)
- #1387 cclinpts three coupled AD changes — cclinpts matches, OR re-scoped Phase-0 filing (Priority 4)
- #1390 kand root-cause localization + fix OR re-scoped Phase-0 filing (Priority 5)
- camcge singular-Jacobian fix OR documented inherent-degeneracy finding (Priority 6)
- Sprint 27 lower-priority cleanups: #1374 `.l` shape, #1400 `message`-field leak, #1385 cross-terms (Priority 7)
- `scripts/sprint_audit/check_golden_staleness.py` + CI job + `make regen-goldens` + one-time corpus refresh (Priority 8)
- `scripts/diagnostics/kkt_residual.py` KKT-residual verification harness + Phase-0 template integration (Priority 9)
- `scripts/diagnostics/check_presolve_divergence.py` + ≥ 6 AD cross-term property tests, both CI-wired (Priority 10)
- CONTRIBUTING.md updated with PR24 (Day-0 traced fix-surface) + PR25 (projection discipline) rules
- Updated pipeline metrics + Sprint 28 SPRINT_LOG.md + SPRINT_RETROSPECTIVE.md

## Acceptance Criteria
- **Solve:** ≥ 110 models solve (up from 105; +5 firm/conditional — #1224 [+1 firm] + #1388 [+1 firm] + #1393+#1335 otpop [+1 firm] + camcge [+1 conditional] + #1390 kand-as-solve [n/a, Match] — net +5 with cclinpts/kand contributing Match not Solve)
- **Match:** ≥ 65 models match (up from 62; +3 — #1393+#1335 otpop [+1] + #1387 cclinpts [+1] + #1390 kand [+1]; #1224/#1388 contribute Solve and Match-conditional)
- **path_syntax_error:** ≤ 6 (down from 8; the carryforward fixes drain otpop and reduce the bucket)
- **path_solve_terminated:** maintain ≤ 5
- **model_infeasible:** ≤ 5 (down from 8; −3 via camshape/otpop/mine recoveries; camcge conditional)
- **Translate:** ≥ 135/142 (maintain; mine already counted in Sprint 27)
- **Parse:** ≥ 142/142 (maintain)
- **Tests:** ≥ 4,800 (up from 4,779; the property tests + harness tests add coverage)
- **Determinism:** byte-identical pipeline output under ≥ 3 `PYTHONHASHSEED` values (PR12)
- **Tooling (Infrastructure):** golden-staleness CI check live + existing drift cleared; KKT-residual harness landed + referenced in the Phase-0 template; presolve-divergence detector + AD cross-term property tests CI-wired
- **Process recommendations:** PR24 (Day-0 traced fix-surface) + PR25 (projection discipline) codified in CONTRIBUTING.md
- **Quality:** all quality gates pass; all fixes have regression tests; emit-touching PRs include regenerated `.gms` diffs (PR14) and pass the new golden-staleness check (PR26)

**Estimated Effort:** 98–144 hours over a 14-day sprint (Day 0 + Days 1–13). At ≤ 12 hours/day this fits within the 168-hour budget (14 × 12 = 168) with slack. Per-priority budgets: P1 #1224 [10–14h] + P2 #1388 [6–10h] + P3 #1393+#1335 [12–16h] + P4 #1387 [12–18h] + P5 #1390 [8–14h] + P6 camcge [8–14h] + P7 cleanups [8–12h] + P8 golden-staleness CI [8–12h] + P9 KKT-residual harness [10–14h] + P10 divergence detector + property tests [12–16h] + process recs PR24/25 [3–5h] + pipeline retest [4h] = 101–149h work-item total, plus ~5–8h prep tasks (Phase-0 gates for the 6 carryforwards). The lower bound assumes Priorities 4–6 (#1387/#1390/camcge — the three diagnosis-heavy, REPLAN-prone tracks) partially slip to Sprint 29; the upper bound assumes all 10 priorities ship. The diagnostic tooling (P9 KKT-residual harness) is intentionally front-loaded (Days 1–3) so it accelerates the carryforward diagnoses (P1/P2/P5) that follow. Heaviest day budget: a ~11h day mid-sprint (P4 #1387's three-coupled-change verification + full-corpus byte-stability re-solve).
**Risk Level:** HIGH — six of the ten priorities are AD/KKT-architecture carryforwards from the Sprint 24–27 alias-AD workstream, three of which (#1387, #1390, camcge) are diagnosis-heavy and REPLAN-prone (Sprint 27's pattern: deep AD fixes routinely prove multi-bug). The primary mitigations are (a) front-loading the KKT-residual harness (P9) so Case-(a/b/c) classification is mechanical, (b) the PR24 Day-0-traced-fix-surface rule (Sprint 27 proved the prep surfaces wrong 4×), and (c) generous REPLAN paths — #1387/#1390/camcge each have an explicit "re-scope to Sprint 29 with a Phase-0 filing" exit. The infrastructure priorities (P8–P10) are lower-risk and provide durable leverage against the recurring bug classes even if the hardest carryforwards slip.

---

# Sprint 29 (Weeks 23–24): PATH Author Consultation & Solution Forcing

**Goal:** Prepare and submit PATH author consultation document. Implement solution forcing strategies. Address remaining solve and translate failures across all pipeline stages.

**Note:** Case studies from Sprint 22; consultation submission now in Sprint 29.

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
  - Target: maintain 100% parse rate of pipeline scope
  - **Deliverable:** Final parse fixes

- **Final Translation Fixes (2-3h)**
  - Address remaining translation blockers
  - Handle newly-discovered patterns from late-arriving parsed models
  - Target: translate rate ≥ 95% of parsed models (matches Sprint 29 Acceptance Criteria below; Sprint 30 steps up to ≥ 97%)
  - **Deliverable:** Final translation fixes

- **Final Solve Fixes (2h)**
  - Address any remaining solvable `path_syntax_error` or `path_solve_terminated` models
  - Apply solution forcing strategies to divergent models
  - Target: solve rate ≥ 82% of translated models (matches Sprint 29 Acceptance Criteria below; modest +1pp bump on Sprint 28's ≥ 82% baseline if forcing strategies recover 1–2 divergent models)
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
- **Parse Rate:** ≥ 100% of pipeline scope (maintain from Sprint 28)
- **Translate Rate:** ≥ 95% of parsed models (maintain from Sprint 28; S30 steps up to ≥ 97% per Rolling KPIs)
- **Solve Rate:** ≥ 82% of translated models (maintain Sprint 28's ≥ 82% baseline; modest stretch via forcing strategies recovering 1–2 divergent models; S30/S31 continue the ramp to ≥ 83% / ≥ 85%)
- **Full Pipeline Match:** ≥ 46% of pipeline scope (maintain from Sprint 28)
- **Quality:** All tests pass; all fixes have regression tests

**Estimated Effort:** 22-28 hours
**Risk Level:** MEDIUM (PATH author response timeline is uncertain; solution forcing may have limited effectiveness for some model classes)

---

# Sprint 30 (Weeks 25–26): Quality, Performance & PATH Feedback Integration

**Goal:** Stabilize performance benchmarks. Incorporate any PATH author feedback. Final comprehensive pipeline run. Begin documentation finalization.

**Note:** PATH consultation submitted in Sprint 29; feedback integration now in Sprint 30.

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
- **Deliverable:** Updated metrics; expected full pipeline match ≥ 48% (matches Sprint 30 Acceptance Criteria below; up from Sprint 29's ≥ 46%)

## Deliverables
- Regression-based performance benchmarks (replacing absolute thresholds)
- PATH author feedback integration
- Final pipeline metrics and comparison report
- `docs/planning/EPIC_4/REMAINING_FAILURES.md` — Remaining failures with roadmap
- Draft Epic 4 SUMMARY.md
- Updated GAMSLIB_STATUS.md, FAILURE_ANALYSIS.md

## Acceptance Criteria
- **Performance Benchmarks:** No flaky CI failures from benchmark tests
- **Final Parse Rate:** ≥ 100% of pipeline scope (maintain)
- **Final Translate Rate:** ≥ 97% of parsed models (up from Sprint 29's ≥ 95%)
- **Final Solve Rate:** ≥ 83% of translated models (up from Sprint 29's ≥ 82%)
- **Full Pipeline Match:** ≥ 48% of pipeline scope (up from Sprint 29's ≥ 46%)
- **Documentation:** Remaining failures documented; Epic 4 summary drafted
- **Quality:** All quality gates pass

**Estimated Effort:** 22-30 hours
**Risk Level:** LOW-MEDIUM (mostly consolidation; PATH feedback timing uncertain)

---

# Sprint 31 (Weeks 27–28): v2.0.0 Release & Epic 5 Planning

**Goal:** Complete Epic 4 with v2.0.0 release. Finalize all documentation. Plan Epic 5 based on remaining failures and new opportunities.

**Note:** Performance benchmarks and PATH feedback integration completed in Sprint 30; Sprint 31 focuses on release and forward planning.

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
  - Review REMAINING_FAILURES.md from Sprint 30
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
  - Outline Sprint 32-36 high-level scope
  - **Deliverable:** Draft Epic 5 PROJECT_PLAN.md

### Sprint Retrospective (~2h)
- **Epic 4 Retrospective (2h)**
  - Document what worked well across Sprints 18-30
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
- **Final Parse Rate:** ≥ 100% of pipeline scope (confirmed from Sprint 30)
- **Final Translate Rate:** ≥ 97% of parsed models (confirmed from Sprint 30)
- **Final Solve Rate:** ≥ 85% of translated models (up from Sprint 30's ≥ 83%)
- **Full Pipeline Match:** ≥ 52% of pipeline scope (up from Sprint 30's ≥ 48%)
- **Epic 5 Ready:** Draft project plan created; backlog prioritized
- **Quality:** All quality gates pass on final release

**Estimated Effort:** 22-28 hours
**Risk Level:** LOW (release mechanics and documentation; Epic 5 planning is exploratory)

---

## Rolling KPIs & Tracking

### Sprint-Level KPIs

| Metric | S18 | S19 | S20 | S21 (actual) | S22 (actual) | S23 (actual) | S24 (actual) | S25 (actual) | S26 | S27 | S28 | S29 | S30 | S31 |
|--------|-----|-----|-----|--------------|--------------|--------------|--------------|--------------|-----|-----|-----|-----|-----|-----|
| Valid Corpus Defined | ✓ | — | — | — | — | — | — | — | — | — | — | — | — | — |
| lexer_invalid_char | ~95 | <50 | 10 | **3** | **4** | **0**³ | **0** | **0** | **0** | 0 | 0 | 0 | 0 | 0 |
| internal_error (parse) | ~23 | <15 | 7 | **0** | **0** | **0** | **0** | **0** | **0** | 0 | 0 | 0 | 0 | 0 |
| path_syntax_error | ≤2 | ≤2 | 48 | **41** | **20** | **23** | **11**⁴ | **12**⁶ | **17**⁷ | ≤6 (−11 via #1398 + #1381 + carryforward) | ≤6 | maintain ≤6 | ≤5 | maintain ≤5 |
| path_solve_terminated | 11 | 11 | 29 | **12** (29/29 classified) | **10** | **12** | **10** | **5** | **5** | maintain ≤5 | maintain ≤5 | maintain ≤5 | ≤4 | ≤3 |
| model_infeasible | 0 | 0 | 12 | **15** | **12**² | **11** | **8**⁵ | **4** | **4** | ≤3 | ≤5 | maintain ≤3 | maintain ≤4 | maintain ≤4 |
| Parse Rate (pipeline scope) | ~41% | ≥55% | 82.5% | **98.1%** (154/157) | **97.5%** (156/160) | **100.0%** (147/147)³ | **100.0%** (143/143)⁴ | **100.0%** (142/142)⁶ | **100.0%** (142/142)⁷ | ≥100% | ≥100% | ≥100% | ≥100% | ≥100% |
| Translate Rate (of parsed) | ~69% | ~72% | 90.9% | **89.0%** (137/154) | **90.4%** (141/156) | **95.2%** (140/147) | **94.4%** (135/143)⁴ | **93.7%** (133/142)⁶ | **94.4%** (134/142)⁷ | ≥95% (+1 via #1385) | ≥95% | maintain ≥95% (stretch ≥96% via forcing) | ≥97% | ≥97% |
| Solve Rate (of translated) | ≥52% | ≥52% | 27.5% | **47.4%** (65/137) | **63.1%** (89/141) | **61.4%** (86/140) | **73.3%** (99/135) | **78.2%** (104/133) | **76.9%** (103/134)⁷ | ≥82% | ≥81% | maintain ≥82% (stretch +1pp via forcing) | ≥83% | ≥85% |
| Full Pipeline Match (pipeline scope) | ~14% | ≥20% | 10.0% | **19.1%** (30/157) | **29.4%** (47/160) | **33.3%** (49/147)³ | **37.8%** (54/143)⁴ | **42.3%** (60/142)⁶ | **41.5%** (59/142)⁷ | ≥46% | ≥45% | maintain ≥46% | ≥48% | ≥52% |

² Sprint 22 `model_infeasible` is 15 total; 12 in-scope after excluding 3 permanently infeasible models (feasopt1, iobalance, orani). A 4th model (meanvar) was declared excluded on Day 7 but later achieved model_optimal, so only 3 remain in the infeasible count. S23–S31 targets are in-scope counts.

³ Sprint 23 pipeline scope changed from 160 to 147 models (13 MIP/other models excluded). Parse and match percentages are relative to the 147-run scope, so excluded models are not counted in that denominator. The `lexer_invalid_char` count dropping to 0 in Sprint 23 primarily reflects parse fixes on models that remained in scope, rather than all lexer failures being removed by scope exclusion.

⁴ Sprint 24 pipeline scope narrowed from 147 to 143 models via schema v2.2.1 exclusions (2 multi-solve driver scripts `decomp`/`danwolfe` excluded by the validator gate introduced in PR #1265, plus 2 others moved out of the in-scope convex-continuous set). S24 metrics are reported on the 143-scope. The S24 `path_syntax_error` value of 11 is from the Day 13 Addendum re-retest under doubled pipeline timeouts (PR #1274 bumped translate 300s→600s / solve 60s→120s / compile-check 30s→60s); the pre-bump Day 13 retest saw 6 path_syntax_error, but the doubled-timeout re-retest translated 5 previously-timing-out models whose MCPs all hit path_syntax_error at PATH compile, yielding a net 1:1 influx. Translate = 135/143 is the post-bump value; pre-bump was 130/143.

⁵ Sprint 24 `model_infeasible` baseline was 14 (triage-scope count from PLAN.md; the narrower 147-pipeline-scope baseline was 11). Δ = −6 net (6 gross fixes: cesam2, qabel, abel, stdcge, lrgcge, moncge recovered; 0 gross influx).

⁶ Sprint 25 pipeline scope narrowed from 143 to 142 models via a runtime convexity reclassification of one model (visible by the Day 11 retest). Per `BASELINE_METRICS.md` §5 this is treated as a runtime filter rather than a scope edit (similar to the multi-solve gate handling of `danwolfe`/`decomp`); identifying the specific model is a Sprint 26 prep item (see Sprint 25 retrospective PR18). The S25 `path_syntax_error` value of 12 is bucket churn — 3 baseline syntax-error models resolved (mathopt4, saras, ferts) and 4 added: 3 transfers from `path_solve_terminated`/`model_infeasible` (camcge, cesam2, fawley) where Sprint 25 unblocked their translates and surfaced fresh PATH compile errors, plus 1 regression from solving (otpop, baseline `solve_success` → `path_syntax_error`). The S25 Translate Rate of 93.7% (133/142) is −2 net vs S24: the Day 12 #1270 multi-solve gate moved saras from `path_syntax_error` to `translate_internal_error` (intentional, same net failure status), plus the 1-model scope shift. S25 Match Rate of 42.3% includes 3 newly-matching models from previously-failing buckets (gtm, korcge, robustlp) and 3 from previously-mismatching. Error-influx accounting (PR10 re-calibrated): alias-AD 0% (within 30% budget), emitter recovery 71% / 5 influx ÷ 7 fixes (within 80–100% budget). 4/8 acceptance criteria reached STRETCH; 1 GO miss on Translate (−2); 1 NO-GO on `path_syntax_error` (+1, bucket churn). 6/8 criteria met overall (Parse, Solve, Match, path_solve_terminated, model_infeasible, Tests).

⁷ Sprint 26 pipeline scope unchanged at 142 (verified Sprint 26 prep Task 2 — abel reclassification carries forward, no new scope movement). The S26 Translate Rate of 94.4% (134/142) is **+1 net vs S25 final** (133 → 134) — srpchase recovered translation under Day 13's faster runner (274.2s per `gamslib_status.json` `translate_time_seconds` vs Sprint 25's 846s under SIGALRM 900s profile); 3 additional Day 0 machine-variance churn-out models (clearlak, ganges, turkpow) also returned to translating successfully and cascaded to path_syntax_error per Sprint 25 final state. The S26 `path_syntax_error` value of 17 (Day 0 9 → Day 13 17, +8) is **bucket churn + Phase A regressions** (the two contributions overlap on turkpow): 3 machine-variance translate churn-backs (clearlak / ganges / turkpow returning from Day 0 translate_timeout to Sprint 25's path_syntax_error baseline) + 1 chronic srpchase translate recovery (Day 13 faster runner unblocked srpchase's chronic Sprint 25 translate_timeout at 274.2s; surfaces path_syntax_error post-translate) — **turkpow's translate-recovery surfaced an additional Phase A `stat_zt(m,v,b,t)` syntax regression on top of its pre-Sprint-26 syntax error**, so it has mixed metric-bucket attribution; 4 Phase A gate side-effects driving the bucket transition (qdemo7 [compare_match → path_syntax_error] + egypt + ferts + shale [path_solve_license → path_syntax_error] — `i↔j` swap on Sums whose body multipliers were already correctly alias-indexed, filed as Sprint 27 #1398). The widened #1398 affected-models known-bug surface (15 models per PR #1399 review) is broader than the 4 models that drove a metric-bucket transition. The S26 Solve Rate of 76.9% (103/134) is **−1 net vs S25 final** (104 → 103, qdemo7 regression). The S26 Match Rate of 41.5% (59/142) is **−1 net** (qdemo7 same root cause). model_infeasible held at 4 (third consecutive sprint with zero gross influx — S24 / S25 / S26). Sprint 26 absorbed **4 close-and-refile architectural reclassifications + 1 in-place carryforward** without sprint cancellation: Phase B → Sprint 27 #1381 (Day 3), Priority 4 Option 1 short-circuit → #1385 (Day 4), Priority 3 kand → #1390 (Day 7), Priority 5 #1334 → #1393 + #1335 in-place reopen (Day 9). Plus PR19 pre-merge solve-time validation CI extension shipped Day 11 (PR #1396). Error-influx accounting (PR10): alias-AD 400% / 4 influx ÷ 1 fix (Phase A consolidated launch emit, PR #1379) — above 30% budget. The 3 machine-variance translate churn-backs (clearlak / ganges / turkpow) are runner-speed effects reverting to the Sprint 25 baseline state, not Sprint 26 fixes. Widened #1398 known-bug surface is 15 models (1500% if measured against the widened surface). Same failure-mode shape PR19 was designed to prevent, just at a broader emit-affected surface than PR19's initial target list (canaries + Pattern C targets); PR19 target-list widening is a Sprint 27 follow-up. **5/8 acceptance criteria met (1 STRETCH on Translate; Parse + path_solve_terminated + model_infeasible + Tests are the other 4 met); 3 MISS with mixed attribution — Solve −1 and Match −1 both single-root-caused by Phase A gate side-effect (qdemo7 regression, #1398); path_syntax_error +8 is partially #1398 (4 Phase A side-effects) PLUS 4 translate recoveries (3 machine-variance churn-backs + srpchase chronic recovery) cascading from translate_timeout to path_syntax_error.** New process recommendations from Sprint 26 retrospective: PR20 (Phase 0 acceptance gate — hand-derived KKT before src/ implementation), PR21 (prep-task end-to-end emit verification), PR22 (Day-0 / mid-sprint script auto-generating the Day 12 PR14 review list), PR23 (CI-workflow PR self-review checklist).

**Note:** Sprint 18 expanded to include emit_gams.py fixes, MCP bug fixes, and lexer analysis (previously Sprint 19 content). All subsequent sprints shifted forward accordingly.

### Dashboard Updates
- `data/gamslib/GAMSLIB_STATUS.md` — Updated after each pipeline retest
- `data/gamslib/progress_history.json` — Updated after each sprint
- Reports regenerated via `scripts/gamslib/generate_report.py`

---

## Risk Mitigation Summary

| Risk | Impact | Probability | Sprints Affected | Mitigation |
|------|--------|-------------|------------------|------------|
| Grammar refactoring regressions | HIGH | HIGH | 20, 22 | 4,200+ test suite; golden files for 12 solving models; incremental changes |
| Stacked blockers in models | HIGH | HIGH | 20-28 | Track blockers removed, not just models unblocked |
| MCP-NLP solution divergence | HIGH | MEDIUM | 25-30 | PATH author consultation; multiple forcing strategies |
| PATH author availability | MEDIUM | MEDIUM | 29-30 | Self-contained case studies; batch questions; literature fallback |
| Diminishing returns on parse | MEDIUM | MEDIUM | 22-29 | Subcategorize before implementing; preprocessing fallback |
| IndexOffset complexity | MEDIUM | MEDIUM | 20-21, 26-28 | Design first (S20), implement second (S21); spike validates feasibility; S26 #1224 ParamRef IndexOffset deferred until architectural extension scoped; S27 Priority 6 lands the translate; S28 Priority 1 lands the parameter-valued-offset KKT cross-term |
| Infeasible MCP formulations | MEDIUM | LOW-MEDIUM | 24-30 | PATH consultation; document as inherent limitations |
| Alias-AD architectural drift | HIGH | HIGH | 24-28 | Day 5 hypothesis-validation methodology (PR16) applied PRE-Sprint-0 from S26 onward; pre-merge solve-time validation (PR19) for emit-affecting changes; **PR20 Phase 0 acceptance gate (hand-derived KKT before src/ implementation) added in S27** after S26 carryforward identified 4 reclassifications + 1 in-place hand-derived-KKT-review catch |

---

## Dependencies & Prerequisites

### External Dependencies
- GAMS software installed locally (with valid license)
- PATH solver available (version 5.2+)
- Internet access for GAMS team communication
- PATH author availability (Michael Ferris, Steven Dirkse) — needed by Sprint 29

### Internal Dependencies
- Epic 3 deliverables: GAMSLIB infrastructure, pipeline scripts, reporting tools
- v1.1.0 as stable baseline (219 models cataloged, 160 verified convex, 12 solving)
- Error taxonomy (47 categories) for consistent failure tracking
- Quality gate infrastructure (typecheck, lint, format, 3204+ tests)

### Sprint-to-Sprint Dependencies
- Sprint 19 depends on Sprint 18 (emit_gams.py completion builds on Part 1)
- Sprint 20 depends on Sprint 19 (lexer analysis informs parse fix priorities)
- Sprint 21 depends on Sprint 20 (IndexOffset design feeds implementation)
- Sprint 23 depends on Sprint 22 (error category analysis feeds targeted fixes)
- Sprint 24 depends on Sprint 23 (alias differentiation priorities from retrospective)
- Sprint 25 depends on Sprint 24 (alias differentiation carryforward + emitter backlog from S24 retrospective)
- Sprint 26 depends on Sprint 25 (Pattern C narrowing #1306 + Day 7 cohort sweep + KU-33/34/35/36 end-of-sprint discoveries from S25 retrospective)
- Sprint 27 depends on Sprint 26 (Pattern C Phase B + Phase A gate tightening + AD architectural redesigns + comp_up subset/superset workstream from S26 retrospective; 14 issues labeled `sprint-27`)
- Sprint 28 depends on Sprint 27 (the alias-AD baseline + the Sprint 28 carryforwards filed in S27: #1224 KKT cross-term, #1388, #1393+#1335, #1387, #1390, camcge — all with a Phase-0 diagnosis already recorded)
- Sprint 29 depends on Sprint 22 (case studies feed consultation document) and Sprint 28 (carryforward stabilization establishes the baseline for PATH consultation work)
- Sprint 30 depends on Sprint 29 (PATH feedback integration, performance benchmarks)
- Sprint 31 depends on Sprint 30 (release preparation based on final metrics)

---

## Changelog

- **2026-06-09:** Inserted new Sprint 28 (Sprint 27 Carryforward — KKT Cross-Term Correctness, AD Architectural Fixes & Diagnostic/CI Tooling) based on `SPRINT_27/SPRINT_RETROSPECTIVE.md` §"Sprint 28 Recommendations" (Priorities 1–6: #1224 parameter-valued-offset KKT cross-term, #1388 camshape `stat_r`, #1393+#1335 otpop scalar-eq Sum-collapse, #1387 cclinpts three-coupled-change, #1390 kand re-diagnosis, camcge CGE degeneracy) + Priority 7 Sprint-27 lower-priority cleanups (#1374 `.l` shape, #1400 `message`-field leak, #1385 cross-terms) + Priorities 8–10 infrastructure (golden-staleness CI check, KKT-residual verification harness, embedded-NLP-divergence detector + AD cross-term property tests) + Sprint 27 retrospective process recs PR24 (Day-0 traced fix-surface) + PR25 (projection discipline). 14-day sprint at ≤12h/day = 168h budget cap; estimated effort 98–144h total (101–149h work-items + ~5–8h prep) (upper bound assumes all 10 priorities ship; lower bound assumes Priorities 4–6 — #1387/#1390/camcge, the diagnosis-heavy REPLAN-prone tracks — partially slip to Sprint 29). Cascaded existing sprints forward: old S28 (PATH Author Consultation & Solution Forcing) → new S29 (Weeks 23–24); old S29 (Quality+Performance+PATH Feedback Integration) → new S30 (Weeks 25–26); old S30 (v2.0.0 Release + Epic 5 Planning) → new S31 (Weeks 27–28). Added S31 column to Rolling KPIs + inserted new S28 column with carryforward targets (Solve ≥81%, Match ≥45%, path_syntax_error ≤6, model_infeasible ≤5, Translate ≥95%). Updated sprint dependencies (S28 now depends on S27 alias-AD baseline + the filed Sprint-28 carryforwards; S29 dep on S22 case studies retained + new dep on S28 carryforward stabilization), risk table sprint-range references (Stacked blockers 20-27→20-28, MCP-NLP solution divergence 25-29→25-30, PATH author availability 28-29→29-30, Diminishing returns 22-28→22-29, IndexOffset 26-27→26-28, Infeasible MCP formulations 24-29→24-30, Alias-AD architectural drift 24-27→24-28), and inline "Sprint 31-35"→"Sprint 32-36" + "Sprints 18-29"→"Sprints 18-30" references inside the renamed Sprint 31 body. Footnote ² updated S23–S30 → S23–S31 targets are in-scope counts.

- **2026-05-26:** Inserted new Sprint 27 (Sprint 26 Carryforward — Pattern C Phase B + Phase A Gate Tightening + AD Architectural Redesigns) based on `SPRINT_26/SPRINT_RETROSPECTIVE.md` §"Sprint 27 Recommendations" (Priorities 1–6: Pattern C Phase B redesign #1381, AD architectural redesigns #1390/#1385/#1393, #1335 scalar-eq cross-term reopen, launch PATH-numerics #1378, comp_up subset/superset #1356/#1357, mine ParamRef IndexOffset #1224) + new priorities for Sprint 26 carryforward additions (#1398 Phase A gate side-effect, #1387 cclinpts + #1388 camshape, #1400 pipeline absolute-path leak, #1374 emit duplicate-init) + Sprint 26 retrospective process recs PR20 (Phase 0 acceptance gate) + PR21 (prep-task end-to-end emit verification) + PR22 (Day-0 mid-sprint script) + PR23 (CI-workflow PR self-review checklist). 14-day sprint at ≤12h/day = 168h budget cap; estimated effort 97–157h total (91–147h work-items + 6–10h prep tasks) (range upper bound assumes all 9 priorities + 4 process recs ship; lower bound assumes Priorities 7–9 + some process recs slip to Sprint 28). Cascaded existing sprints forward: old S27 (PATH Author Consultation & Solution Forcing) → new S28 (Weeks 21–22); old S28 (Quality+Performance+PATH Feedback Integration) → new S29 (Weeks 23–24); old S29 (v2.0.0 Release + Epic 5 Planning) → new S30 (Weeks 25–26). Added S30 column to Rolling KPIs + inserted new S28 column with PATH Consultation maintain targets. Updated sprint dependencies (Sprint 27 now depends on Sprint 26 for the 14 sprint-27-labeled issues; Sprint 28 dep on Sprint 22 case studies retained + new dep on Sprint 27 carryforward stabilization), risk table sprint-range references (Stacked blockers 20-26→20-27, MCP-NLP solution divergence 25-28→25-29, PATH author availability 27-28→28-29, IndexOffset 20-21,26→20-21,26-27, Infeasible MCP formulations 24-28→24-29, Alias-AD architectural drift HIGH/MEDIUM→HIGH/HIGH with PR20 Phase 0 acceptance-gate mitigation note), External Dependencies "PATH author availability" Sprint 28 → 29, and inline "Sprint 30-34" + "Sprints 18-28" references inside the renamed Sprint 30 body. Footnote ² updated S23–S29 → S23–S30 targets are in-scope counts.
- **2026-05-14:** Sprint 26 final metrics recorded (5/8 acceptance criteria met, 1 STRETCH on Translate +4 STRETCH ≥132 = 134/142). 3 MISS with **mixed attribution**: Solve (−1) and Match (−1) both single-root-caused by Phase A's Pattern C gate predicate firing too broadly on Sums whose body multipliers are already correctly alias-indexed (qdemo7 regression — filed as Sprint 27 #1398); path_syntax_error (+8) is **partially #1398** (4 Phase A side-effects: qdemo7/egypt/ferts/shale) **PLUS 4 translate recoveries cascading** from `translate_timeout` to `path_syntax_error` (clearlak/ganges/turkpow machine-variance churn-backs + srpchase chronic recovery via Day 13 faster runner). Updated Rolling KPIs row with S26 actuals + footnote ⁷ documenting the metric movement, the bucket-provenance analysis (4 Phase A side-effects + 3 machine-variance translate churn-backs + 1 chronic srpchase translate recovery), and the PR10 re-calibrated error-influx outcome (alias-AD 400% / 4 influx ÷ 1 fix [Phase A consolidated launch emit, PR #1379], above 30% budget; widened #1398 known-bug surface is 15 models at 1500% if measured against the widened surface — same failure-mode shape PR19 was designed to prevent, just at a broader emit-affected surface than PR19's initial target list). Sprint 26 absorbed 4 close-and-refile reclassifications + 1 in-place carryforward without sprint cancellation: Phase B → Sprint 27 #1381 (Day 3), Priority 4 Option 1 short-circuit → #1385 (Day 4), Priority 3 kand → #1390 (Day 7), Priority 5 #1334 → #1393 + #1335 in-place reopen (Day 9); plus PR19 CI extension shipped Day 11 (PR #1396 merged). New process recommendations from Sprint 26 retrospective: PR20 (Phase 0 acceptance gate — hand-derived KKT before src/ implementation effort), PR21 (prep-task end-to-end emit verification), PR22 (Day-0 / mid-sprint script auto-generating the Day 12 PR14 review list), PR23 (CI-workflow PR self-review checklist). **14 issues labeled `sprint-27` for Sprint 27 backlog** = 2 net-new from Day 13 (#1398 Phase A gate side-effect discovery + #1400 pipeline absolute-path leak in `gamslib_status.json`, surfaced by PR #1399 review) + 7 net-new from Sprint 26 reclassifications + close-and-refile across Days 1–9 (#1378 launch PATH numerics Day 1 + #1381 Pattern C Phase B Day 3 + #1385 Option 1 short-circuit Day 4 + #1387 cclinpts Day 6 + #1388 camshape Day 6 + #1390 kand AD-architecture Day 7 + #1393 scalar-eq Sum-collapse from #1334 Day 9) + 1 reopened in-place Day 13 (#1335 per Day 9 intent) + 4 pre-existing carryforward with sprint-26 label moved to sprint-27 Day 13 (#1224 mine ParamRef IndexOffset + #1356 fawley comp_up + #1357 otpop comp_up + #1374 emit duplicate-init bugs).
- **2026-05-06:** Inserted new Sprint 26 (Pattern C Generalization, Pattern A Reclassification & Sprint 25 Carryforward) based on Sprint 25 retrospective §"Sprint 26 Recommendations" (Priorities 1–5: Pattern C gate generalization #1354/#1355/#1356/#1357 + #1306/#1307; Pattern A cohort reclassification #1138/#1139/#1140/#1142/#1145/#1150; Pattern E re-verification #1141/#1144/#1147; translation timeout Option 1 short-circuit; AD residuals #1334/#1335) + §"What We'd Do Differently" (process recs PR16 hypothesis-validation pre-Sprint-0, PR17 bucket provenance, PR18 scope-shift identification, PR19 pre-merge solve-time validation, PR14 reaffirmation). 14-day sprint at ≤12h/day budget = 50–75h estimated effort. Cascaded existing sprints forward: old S26 (PATH Author Consultation) → new S27 (Weeks 19–20); old S27 (Quality+Performance+PATH Feedback) → new S28 (Weeks 21–22); old S28 (v2.0.0 Release + Epic 5 Planning) → new S29 (Weeks 23–24). Added S29 column to Rolling KPIs + new S27 column with PATH-consultation maintenance targets. Updated sprint dependencies, risk table sprint-range references (alias-AD architectural drift risk added explicitly), External Dependencies "PATH author availability" Sprint 27 → 28, and inline "Sprint 29-33" + "Sprints 18-28" references inside the renamed S29 body. Footnote ² updated to S23–S29 targets are in-scope counts.
- **2026-05-05:** Sprint 25 final metrics recorded (6/8 acceptance criteria met, 4/8 reaching STRETCH: Solve 104, Match 60, model_infeasible 4, path_solve_terminated 5). Updated Rolling KPIs row with S25 actuals + footnote ⁶ documenting the 1-model scope shift (143→142), the +1 path_syntax_error bucket churn (3 transfers + 1 regression — otpop), and the PR10 re-calibrated error-influx outcome (alias-AD 0% / emitter 71%, both within budget). Revised S26–S28 targets reflecting the Sprint 25 finishing state (path_syntax_error ≤6 / Match ≥45% / Solve Rate ≥81% for Sprint 26). 23 issues labeled `sprint-26` for Sprint 26 backlog (5 issues filed during Sprint 25 Day 13 — 1 closed as duplicate of pre-existing #1224 → 4 net-new open + 19 carryforward).
- **2026-04-19:** Inserted new Sprint 25 (Alias Differentiation Carryforward & Emitter Backlog) based on Sprint 24 retrospective. Cascaded old S25→S26, S26→S27, S27→S28. Added S28 column to Rolling KPIs. Shifted sprint weeks (old S25 Weeks 15–16 → new S26 Weeks 17–18; old S26 → S27 Weeks 19–20; old S27 → S28 Weeks 21–22). Updated sprint dependencies, acceptance criteria, and cross-references. S25 targets from Sprint 24 retrospective §Suggested Sprint 25 Targets; components from §Sprint 25 Recommendations Priority 1–5.
- **2026-04-03:** Inserted new Sprint 24 (Alias Differentiation & Error Category Reduction) based on Sprint 23 retrospective. Cascaded old S24→S25, S25→S26, S26→S27. Added S27 column to Rolling KPIs. Updated sprint dependencies, acceptance criteria, and risk table sprint references. S24 targets from Sprint 23 retrospective recommendations.
- **2026-03-17:** Replaced Sprint 23 content with Sprint 22 retrospective recommendations (5 priorities: path_solve_terminated, model_infeasible, match rate, path_syntax_error residual, translate failures). Cascaded old S23→S24, S24→S25, S25→S26. Added S26 column to Rolling KPIs. Updated sprint dependencies.
- **2026-03-17:** Sprint 22 final metrics recorded (6/8 targets met, 3 exceeded stretch: solve 89, match 47, path_syntax_error 20). Updated Rolling KPIs with Sprint 22 actuals and revised S23–S26 targets. 24 issues labeled `sprint-23` for Sprint 23 backlog.
- **2026-02-06:** Reorganized sprints 18-25 after Sprint 18 scope expansion
  - Sprint 18 expanded to ~56h by pulling Sprint 19 items (emit_gams.py completion, lexer analysis, fix roadmap)
  - Content cascaded forward: S19←S20, S20←S21, S21←S22, S22←S23, S23←S24, S24←S25
  - Sprint 25 now includes Epic 5 planning as new content
  - Updated KPIs to reflect accelerated progress in Sprint 18
- **2026-03-04:** Sprint 21 final metrics recorded (all 8 acceptance criteria met: parse 154/157, solve 65, match 30, tests 3,957). Deferred to Sprint 22: #764 accounting vars, #765 CGE model type, #827 domain violations, #830 Jacobian timeout, remaining path_syntax_error subcategories (C/B/G/F/I/J)
- **2026-02-18:** Added Sprint 19 deferred items to Sprint 20 (Priorities 1–5 from Sprint 19 retrospective: `.l` initialization emission, accounting variable detection, AD condition propagation, remaining lexer_invalid_char taxonomy, full pipeline match rate, plus smoke-test process recommendation)
- **2026-02-05:** Initial EPIC_4 project plan created
