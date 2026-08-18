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

**Note:** All Priority-1–6 fixes carry forward from Sprint 27 with a documented Phase-0 diagnosis already in their `docs/issues/ISSUE_*.md` files — Sprint 28 starts from a known fix-surface for most, **except where Sprint 27 proved the prep-doc surface wrong** (see Process Recommendation §"PR24"). The single highest-leverage Solve workstream is **#1224 + #1388**: both are AD/KKT cross-term defects with a hand-derived target shape already recorded (+1 Solve each, firm). The PATH-author-consultation / solution-forcing / release work that previously occupied Sprint 28 moves to **Sprint 30** (and Sprints 31/32) — see the renumbered sections below.

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
- **Solve:** ≥ 110 models solve (stretch; up from 105). +4 firm/conditional is backed by the named carryforwards — #1224 mine [+1 firm] + #1388 camshape [+1 firm] + #1393+#1335 otpop [+1 firm] + camcge [+1 conditional] — taking Solve to 109; the +5th to reach 110 is a stretch requiring one additional recovery (TBD at Day 0). cclinpts (#1387) and kand (#1390) already solve (`model_optimal`, currently mismatching), so they contribute Match, not Solve.
- **Match:** ≥ 65 models match (up from 62; +3 — #1393+#1335 otpop [+1] + #1387 cclinpts [+1] + #1390 kand [+1]; #1224/#1388 contribute Solve and Match-conditional)
- **path_syntax_error:** maintain ≤ 8 (no Sprint 28 carryforward targets this bucket directly — otpop/camshape/mine are `model_infeasible`, so their recoveries reduce `model_infeasible`, not `path_syntax_error`; the Solve/Match gains come from the model_infeasible and mismatch buckets)
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

# Sprint 29 (Weeks 23–24): Sprint 28 Carryforward — Presolve/Warm-Start Robustness, Cold-Convex MCP Convergence & AD Cross-Term Cleanup

**Goal:** Land the Sprint 28 Solve/Match carryforwards that the Day-13 retest and Task-6 gates deferred — the head-domain-offset MCP infeasibility (#1443 mine), the presolve `_fx_`-multiplier warm-start + non-convex convergence (#1462 rocket), and the translation-timeout Option-1 cross-term re-emit (#1385) — and attack the **cold-convex robustness** gap the Sprint 28 retrospective surfaced: the ~24 non-convex models (otpop/cclinpts/camshape + the methodology-recovered cohort) that match ONLY via the `--nlp-presolve` warm-start, whose cold MCP is non-convex-infeasible. Produce the Epic 5 scoping observation for the inherent CGE Walras-law degeneracy (#1330 camcge). Then clear the highest-leverage AD/KKT cross-term backlog beyond the retrospective (#1447 maxmin, the objective-mismatch cohort #1332/#1247/#1239/#1236, and the offset-alias gradient architecture #1112/#1111/#1146/#1143). Wire the Sprint-28 retrospective process recommendations (checkpoint re-solve of the changed-golden set; re-baseline after any pipeline-methodology change) into the pipeline tooling. (See `SPRINT_28/SPRINT_RETROSPECTIVE.md` §"Sprint 29 Recommendations / Carryforwards" + §"What We'd Do Differently" for per-priority and per-process-rec rationale.)

**Note:** The five retrospective carryforwards (Priorities 1–5) are the core; Priorities 6–8 pull additional open backlog issues beyond the retrospective to fill the 14-day budget, grouped by the same AD/KKT cross-term and presolve bug classes so the Sprint 28 diagnostic tooling (KKT-residual harness, presolve-divergence detector, golden-staleness gate) is reused rather than rebuilt. The PATH-author-consultation / solution-forcing / quality / release work that previously occupied Sprints 30–32 moves to **Sprints 38–40** — see the renumbered sections below (the new **Sprint 30** below is the Sprint-29-carryforward sprint).

## Components

### Priority 1: #1443 mine — Head-Domain-Offset MCP Infeasibility (~10–16h)  [retrospective carryforward]
- Re-scoped from #1224 (whose `stat_x` parameter-valued-offset inversion landed in Sprint 28). mine is a convex LP whose corrected MCP still cold-solves to MS 5 (`x → 4e10` despite `x.up=1`, 49 INFES across `comp_pr`/`comp_lo_x`/`comp_up_x`/`stat_x`). Two coupled defects: (a) the `pr(k,l+1,i,j)` **head-domain-offset** dual-transfer should read `pr.m` at `l+1` (the presolve warm-start mis-aligns the multiplier), and (b) a deeper cold-infeasible complementarity/bound coupling.
- **Phase 0 acceptance gate (PR20/PR24):** `kkt_residual.py data/gamslib/raw/mine.gms` to localize the max-residual row at the NLP KKT point; confirm whether it is the head-offset dual-transfer (Case b) or a cold non-convex coupling (Case c) BEFORE any src change.
- **Deliverable:** mine → MODEL STATUS 1 (or a documented Case-c REPLAN with the localized row); #1443 closed or re-scoped. +1 Solve (firm if Case b).

### Priority 2: #1462 rocket — Presolve `_fx_`-Multiplier Warm-Start + Non-Convex Convergence (~8–14h)  [retrospective carryforward]
- Sprint 28 Day-13 localized the root cause: the `_fx_` equation multipliers (`nu_<var>_fx_<idx>`) are NOT warm-started in the presolve emit, so `stat_v('h0')` has a nonzero residual at the warm start and PATH diverges (non-convex) → MS 5. Injecting `nu_*_fx_h0.l = <var>.m('h0')` moves the objective to 1.016 (near NLP 1.0128) but MS 5 persists — necessary but not sufficient.
- **Fix:** add the general `_fx_`-multiplier warm-start (`nu_<var>_fx_<idx>.l = <var>.m(<idx>)`, mirroring the existing `piL_/piU_` warm-starts) in `src/emit/emit_gams.py`; then harness-investigate the residual non-convex convergence (the bound-complementarity `piL/piU` activation at `h0` introduced by the #1449 Layer-4 unfix).
- **Phase 0 acceptance gate (PR20/PR27):** `kkt_residual.py` on rocket post-warm-start — residual → 0 at `h0`; PATH solve to MS 1/2 at 1.0128.
- **Deliverable:** the general `_fx_`-multiplier warm-start lands (sprint-wide presolve robustness, not rocket-only); rocket → match OR a documented non-convex-convergence Case-c finding; #1462 closed or re-scoped. +1 Solve / +1 Match (recovers the Sprint-28 stale-baseline model).

### Priority 3: #1385 — Translation-Timeout Option-1 Short-Circuit Cross-Terms (~10–16h)  [retrospective carryforward]
- The translate-time short-circuit landed Sprint 27; the runtime-guard equation-body re-emit + the `J_gᵀ·lam` cross-terms are still deferred (a re-emit without cross-terms = an inconsistent MCP, so they land together). Target models: the `translate_timeout` cohort Option-1 was meant to recover (#1228 iswnm, #1185 mexls, #932 nebrazil, sarf), partially overlapping the slow-emit set.
- **Phase 0 acceptance gate (PR20):** hand-derive the runtime-guarded `stat_*` cross-terms for one srpchase-class target; verify the re-emit body shape against the Lagrangian + the regenerated golden byte-stability.
- **Deliverable:** the runtime-guard re-emit + `J_gᵀ·lam` cross-terms land; ≥1 translation-timeout model recovers to translate (+Translate) OR a re-scoped Phase-0 filing; #1385 closed or re-scoped.

### Priority 4: Cold-Convex Robustness — Non-Convex Models that Match Only Warm-Started (~12–18h)  [retrospective carryforward, NEW track]
- The Sprint 28 retrospective surfaced that otpop/cclinpts/camshape and the ~24 methodology-recovered models match ONLY via the `--nlp-presolve` warm-start (the Day-9 presolve-retry broadening); their COLD MCP is non-convex-infeasible. Track cold robustness as its own workstream: classify each model's cold failure (a genuine emit bug surfaced only cold vs inherent non-convexity), and fix the cold-emit bugs. **First concrete target: #1447 maxmin** — `stat_mindist` missing the objective-variable cross-term (Case b, harness-localized) — the cold emit is wrong, not just non-convex.
- **Phase 0 acceptance gate (PR20/PR27):** run `kkt_residual.py` across the ~24 cohort to partition Case-b (cold emit bug → fixable) from Case-c (inherent non-convexity → forcing-strategy territory, hand off to the renumbered Sprint 30 solution-forcing work); fix the Case-b cold-emit bugs (#1447 first).
- **Deliverable:** the cold/warm partition documented; ≥2 Case-b cold-emit bugs fixed (#1447 maxmin + ≥1 more); the Case-c residue scoped for Sprint 30 forcing strategies.

### Priority 5: camcge → Epic 5 Scoping Observation (#1330) (~6–10h)  [retrospective carryforward]
- Sprint 28 Day-11 Task-6 gate confirmed camcge's MCP is structurally singular (CGE Walras-law degeneracy — `equil(i)` goods + `lmequil(lc)` labor market-clearing linearly dependent given budget balance, no price numéraire). A general nlp2mcp emit fix does not exist; this needs a CGE-domain structural transformation (a single redundant-row drop + numéraire fix preserving the economic solution) = Epic 5 scope. The CGE cohort (#1354 camcge, #1355 cesam2, #1317/#1331/#1251 twocge) shares the class.
- **Deliverable:** `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` (or an Epic 5 observation issue) documenting the Walras-redundancy + numéraire-selection transformation, the affected CGE cohort, and a proposed approach; #1330 moved to Epic 5. NO Sprint-29 `src/` budget on camcge.

### Priority 6 (additional backlog): Objective-Mismatch Cohort — Harness-Classify + Fix Case-b (~12–18h)
- Beyond the retrospective: the cluster of `model_optimal`-but-mismatching models the KKT-residual harness can now triage mechanically — **#1332 quocge** (25.683 vs 25.5085), **#1247 prolog** (−73.5 vs −0.0), **#1239 sambal/qsambal** (1028 vs 3.97), **#1236 hhfair** (54.9 vs 87.2). Run the Case-(a/b/c) verdict per model; fix the Case-b emit bugs (each → +1 Match).
- **Phase 0 acceptance gate (PR20/PR27):** `kkt_residual.py` verdict per model BEFORE any src change; only PROCEED on a localizable Case-b row.
- **Deliverable:** ≥2 of the cohort fixed to match (Case-b emit bugs); Case-c residue re-scoped. +2 Match (contingent on the Case-b verdicts).

### Priority 7 (additional backlog): Offset-Alias Gradient + Dollar-Condition AD Architecture (~12–18h)
- Beyond the retrospective: the recurring offset-alias gradient defect class — **#1146 himmel16** (cyclic offset-alias gradient, 43% mismatch), **#1143 polygon** (offset-alias gradient, 100% mismatch) — plus the underlying AD-engine gaps **#1112** (dollar-condition propagation through the AD/stationarity pipeline) and **#1111** (alias-aware differentiation with summation-context tracking). These are the architecture behind several Sprint 24–28 cross-term defects; the AD cross-term property tests (Sprint 28 Priority 10) guard the fix.
- **Phase 0 acceptance gate (PR20):** add a property-test fixture reproducing the himmel16/polygon offset-alias gradient shape (extends the Sprint 28 `test_ad_crossterm_shapes.py` catalog); hand-derive the correct gradient before the AD change.
- **Deliverable:** himmel16 + polygon offset-alias gradients corrected (or a re-scoped architectural filing for #1111/#1112 if the fix proves a deeper AD-engine redesign); +1–2 Match.

### Priority 8 (Infrastructure): Checkpoint Re-Solve + Post-Methodology Re-Baseline (~6–10h)
- **Sprint 28 retrospective "What We'd Do Differently" #4 + #5:** (a) golden-stability (byte-identical re-emit) does NOT catch a broken *solve* — the rocket #1462 stale baseline hid behind passing golden checks until the Day-13 retest; wire a "**re-solve the changed-golden set**" step into the Day-5/Day-10 checkpoints (the `changed_emit_artifacts.py` golden diff is the exact at-risk list). (b) a pipeline-methodology change (the Day-9 presolve-retry broadening) silently lifted Match +24 beyond the genuine gains; add a **re-baseline** step so the headline delta stays attributable after any retry/comparison-logic change.
- **Components:** extend `scripts/sprint_audit/` (or the checkpoint flow) with a `--resolve-changed` mode that re-solves only the changed-golden models; a re-baseline note in the PR25 projection-discipline template.
- **Deliverable:** the checkpoint re-solve + re-baseline tooling/process; CONTRIBUTING.md / Phase-0 template note.

### Pipeline Retest (~4h)
- Full pipeline at each checkpoint (Day 5 + Day 10) and final (Day 13) per PR6; final retest under ≥ 3 `PYTHONHASHSEED` values (PR12). Use the new Priority-8 checkpoint re-solve so a broken solve surfaces mid-sprint, not at Day 13 (the Sprint 28 rocket lesson).
- **Deliverable:** updated `gamslib_status.json` (machine-portable paths) + Sprint 27→28→29 metrics comparison; determinism verified.

## Deliverables
- #1443 mine head-domain-offset MCP fix — mine solves, OR a Case-c REPLAN with the localized row (Priority 1)
- #1462 rocket general `_fx_`-multiplier warm-start (presolve robustness) + non-convex investigation — rocket matches OR a documented Case-c finding (Priority 2)
- #1385 translation-timeout Option-1 runtime-guard re-emit + `J_gᵀ·lam` cross-terms (Priority 3)
- Cold-convex robustness partition + ≥2 Case-b cold-emit fixes (#1447 maxmin first) (Priority 4)
- `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` — camcge #1330 → Epic 5 (Priority 5)
- Objective-mismatch cohort: ≥2 of #1332/#1247/#1239/#1236 matched (Priority 6)
- Offset-alias gradient fixes (#1146 himmel16 + #1143 polygon) + AD-engine #1111/#1112 scoping (Priority 7)
- Checkpoint re-solve + post-methodology re-baseline tooling/process (Priority 8)
- Updated pipeline metrics + Sprint 29 SPRINT_LOG.md + SPRINT_RETROSPECTIVE.md

## Acceptance Criteria
- **Solve:** ≥ 109 models solve (up from Sprint 28's 107; +2 firm via #1443 mine [+1] + #1462 rocket [+1]; cold-convex Case-b fixes are Match-not-Solve unless they recover a `model_infeasible` model)
- **Match:** maintain ≥ 92 models (the Sprint 28 baseline = 92/142 = **64.8% Full Pipeline Match**, the re-baselined Rolling-KPIs target ≥ 64% — footnote ⁸); **stretch ≥ 96 models** (+4 genuine via #1462 rocket [+1] + #1447 maxmin [+1] + objective-mismatch cohort [+2]); the genuine-gain figure tracked separately per PR25
- **model_infeasible:** ≤ 5 (down from 7; −2 via mine #1443 + rocket #1462 recoveries)
- **path_syntax_error:** maintain ≤ 8
- **path_solve_terminated:** maintain ≤ 5
- **Translate:** ≥ 135/142 (maintain; stretch +1 via #1385 timeout recovery)
- **Parse:** ≥ 142/142 (maintain)
- **Tests:** ≥ 4,960 (up from ~4,935; the new cross-term property fixtures + warm-start regression tests add coverage)
- **Determinism:** byte-identical pipeline output under ≥ 3 `PYTHONHASHSEED` values (PR12)
- **Epic 5 scoping:** camcge #1330 CGE-degeneracy scoping doc filed; #1330 moved to Epic 5
- **Process:** checkpoint re-solve of the changed-golden set wired into Day-5/Day-10; PR25 re-baseline step codified
- **Quality:** all quality gates pass; all fixes have regression tests; emit-touching PRs pass the golden-staleness check (PR26) + the presolve-divergence detector (Sprint 28 Priority 10)

**Estimated Effort:** 96–134 hours over a 14-day sprint (Day 0 + Days 1–13). At ≤ 12 hours/day this fits within the 168-hour budget (14 × 12 = 168) with slack. Per-priority budgets: P1 #1443 [10–16h] + P2 #1462 [8–14h] + P3 #1385 [10–16h] + P4 cold-convex robustness [12–18h] + P5 camcge Epic-5 scoping [6–10h] + P6 objective-mismatch cohort [12–18h] + P7 offset-alias gradient AD [12–18h] + P8 checkpoint re-solve infra [6–10h] + pipeline retest [4h] = 80–124h work-item total, plus ~6–10h prep tasks (Phase-0 gates for the diagnosis-heavy tracks). The lower bound assumes the diagnosis-heavy, REPLAN-prone tracks (P1 #1443 cold-coupling, P2 #1462 non-convex convergence, P7 AD-engine #1111/#1112) partially slip to Sprint 30; the upper bound assumes all 8 priorities ship. The KKT-residual harness, presolve-divergence detector, and golden-staleness gate (all built Sprint 28) are reused throughout, so the diagnosis cost is lower than Sprint 28's. Heaviest day budget: a ~11h day mid-sprint (P4 cold-convex partition across the ~24 cohort + the #1447 maxmin fix verification).
**Risk Level:** HIGH — five of the eight priorities are AD/KKT/presolve carryforwards or backlog with diagnosis-heavy, REPLAN-prone tails (the Sprint 24–28 pattern: deep AD/non-convex fixes routinely prove multi-bug). The primary mitigations are (a) the Sprint-28 KKT-residual harness making Case-(a/b/c) classification mechanical, so each track has an early PROCEED/REPLAN gate, (b) the PR24 Day-0-traced-fix-surface rule, and (c) explicit Case-c REPLAN exits on #1443/#1462/#1447 and the cohort priorities. The cold-convex robustness track (P4) is intentionally diagnosis-first (partition before fixing) so its non-convex residue hands cleanly to the renumbered Sprint 30 solution-forcing work rather than over-running Sprint 29.

---

# Sprint 30 (Weeks 25–26): Sprint 29 Carryforward — Head-Domain-Offset Emit Architecture, Non-Convex Forcing & Offset-Alias AD

**Goal:** Land the Sprint 29 Solve/Match carryforwards the Day-13 retest REPLAN'd — the **head-domain-offset emit architecture** (the coordinated `comp_pr`/`lam_pr`/`stat_x` + bound index-map re-derivation that converts **mine** [+1 Solve] *and* **robert** [genuine-floor], with robert as the minimal pure-constant-offset reproduction and mine as the full `l+1 × li(k)/lj(k)` multi-site case), the **rocket #1462 non-convex forcing** (trust-region / homotopy / multi-start — the `_fx_` warm-start already landed Sprint 29, the residual is intrinsic non-convergence), the **hhfair #1236 widened-VARIABLE presolve fix** (the `$184` #1449-conflict for a live nonlinear-stationarity variable `n`, the prerequisite to the CES-mismatch verdict), the **#1385 symbolic runtime-guard cross-term emit** (sarf reference target; cross-terms already hand-derived + banked Sprint 29), and the **offset-alias cross-terms #1111/#1112** (polygon successor-offset — reverted Sprint 29 Day 5 as coupled with the distance-Jacobian — plus himmel16). Implement the **camcge #1330 → Epic 5** Walras transformation (drop-one-redundant-row + fix-one-numéraire per `EPIC_5/CGE_DEGENERACY_SCOPING.md`), and clear the adjacent general-emit backlog the Sprint 29 harness sweep surfaced (the Class-B CGE `stat_pz` coefficient discrepancy — confirmed **NOT** Walras). (See `SPRINT_29/SPRINT_RETROSPECTIVE.md` §"Sprint-30 carryforwards" for per-priority rationale.)

**Note:** The six retrospective carryforwards (Priorities 1–6) are the core; Priorities 7–8 pull the adjacent general-emit backlog + the infrastructure the Sprint 29 retrospective recommends (property-test catalog extension for the new head-offset/offset-alias cross-term shapes; a Sprint-30 re-baseline of the stale Rolling-KPIs Match targets; a solution-forcing harness scaffold that feeds the renumbered Sprint 39 PATH-consultation work). The Sprint 29 diagnostic tooling (KKT-residual harness, presolve-divergence detector, golden-staleness gate, `--resolve-changed` checkpoint re-solve) is reused throughout rather than rebuilt. The PATH-author-consultation / quality / release work that previously occupied Sprints 34–36 moves to **Sprints 38–40** — see the renumbered sections below (the new **Sprint 31** below is the Sprint-30-carryforward sprint).

## Components

### Priority 1: Head-Domain-Offset Emit Architecture (#1443 mine + robert) (~14–20h)  [retrospective carryforward]
- Sprint 29 Day-7 REPLAN'd #1443: mine's cold MS-5 is not a single-site emit bug but a **coordinated re-derivation of the head-domain-offset index map across three emit sites** — (1) `comp_pr` emission, (2) the `--nlp-presolve` dual transfer (`src/emit/emit_gams.py` `_emit_nlp_presolve`), (3) the `stat_x` cross-term — plus the cold-start LCP consistency. Sprint 29 Day-12 found **robert** is a second instance of the same class: `sb(r,tt+1)`'s head-offset defining statement means `x(p,tt)`'s cross-term must be `sum(r, a(r,p)*nu_sb(r,tt+1))` but the emit produces `nu_sb(r,tt)` (the head offset is not inverted onto the multiplier index). robert is the **simpler pure-constant-offset sub-case** (no `li(k)`/`lj(k)` parameter offset); a correct head-domain-offset cross-term emit converts **both** mine (Solve) **and** robert (genuine-floor).
- **Phase 0 acceptance gate (PR20/PR24):** hand-derive the head-offset-inverted cross-term for robert (minimal reproduction) first; verify `kkt_residual.py` residual → 0 on robert, then mine, before the multi-site src change.
- **Deliverable:** the head-domain-offset cross-term + dual-transfer index-map lands; **mine → MODEL STATUS 1** (+1 Solve) and **robert cold-matches** (genuine-floor +1); #1443 closed.

### Priority 2: rocket #1462 — Non-Convex Convergence Forcing (~10–16h)  [retrospective carryforward]
- The general `_fx_`-multiplier warm-start landed Sprint 29 Day 1 (sprint-wide presolve robustness); Sprint 29 Day 2 confirmed the residual MS-5 is **intrinsic non-convex convergence**, not an emit/warm-start defect. This needs a **solution-forcing** strategy: trust-region damping, a homotopy/continuation path from a relaxed problem, or multi-start from perturbed warm-starts.
- **Phase 0 acceptance gate (PR27):** confirm (again) via `kkt_residual.py` that the emit residual is clean at the NLP point (Case-c); then prototype one forcing lever and measure MODEL STATUS progression toward MS 1/2 at 1.0128.
- **Deliverable:** rocket → match via a documented forcing strategy (+1 Solve / +1 Match) OR a documented "needs a solver-side option beyond nlp2mcp" finding that seeds the Sprint-38 PATH consultation; the forcing scaffold is reusable for the cold-convex Case-c residue.

### Priority 3: hhfair #1236 — Widened-VARIABLE Presolve Fix (~10–16h)  [retrospective carryforward]
- Sprint 29 Day 8 REPLAN'd hhfair: the compile blocker's first error is `$184` (the #1449 widened-symbol conflict for the **variable** `n`, source `n(t)` vs MCP-widened `n(tl)`), not the Day-0-attributed `$141`; the `__pw`-companion fix doesn't transfer because `n` is a live nonlinear-stationarity coefficient, and `--gdx` does not bypass it (the presolve `$include` supplies the symbol declarations). Generalize the #1449 widened-symbol handling to the widened-**variable** case so the residual MCP compiles; then read the CES-mismatch Case-b/Case-c verdict.
- **Phase 0 acceptance gate (PR20/PR27):** the `$184` clears (residual MCP compiles); `kkt_residual.py` returns a verdict; PROCEED to the CES/product `stat_*` fix only on a localizable Case-b row.
- **Deliverable:** the widened-VARIABLE presolve fix lands (general emit robustness, not hhfair-only); hhfair → match (+1 Match, the last live objective-mismatch-cohort target) OR a documented Case-c non-convexity finding; #1236 closed or re-scoped.

### Priority 4: #1385 — Symbolic Runtime-Guard Cross-Term Emit (~10–16h)  [retrospective carryforward]
- Sprint 29 Day 9 hand-derived + banked the runtime-guarded `stat_*` `J_gᵀ·lam` cross-terms for the short-circuited constraints (the re-emit body + cross-terms land atomically). **sarf** is the reference target (smallest tractable skipped-constraint instance count). Implement the symbolic-instance re-emit so the cross-terms materialize.
- **Phase 0 acceptance gate (PR20):** verify the re-emitted `stat_*` bodies against the banked hand-derivation; no quoted-set-name multiplier indices; the regenerated golden is byte-stable.
- **Deliverable:** the runtime-guard re-emit + `J_gᵀ·lam` cross-terms land; ≥1 translation-timeout model (sarf) recovers to translate (+Translate) OR a re-scoped Phase-0 filing; #1385 closed or re-scoped.

### Priority 5: Offset-Alias Cross-Terms #1111/#1112 (polygon + himmel16) (~12–18h)  [retrospective carryforward]
- Sprint 29 Day 5 reverted the polygon successor-offset cross-term (it was coupled with the distance-Jacobian and the localized fix regressed the pair). File the AD-engine issue (#1111 alias-aware differentiation / #1112 dollar-condition propagation) and land the offset-alias gradient correction with the property-test fixture guarding it. himmel16 (`stat_area`, cyclic `i++1`) is the second Class-A target.
- **Phase 0 acceptance gate (PR20):** the offset-alias property-test fixture (extends `test_ad_crossterm_shapes.py`) reproduces the polygon/himmel16 shape; hand-derive the correct offset-image cross-term before the AD change; confirm the fix doesn't regress the distance-Jacobian coupling.
- **Deliverable:** polygon + himmel16 offset-alias gradients corrected (cold-match, genuine-floor) OR a re-scoped #1111/#1112 architectural filing if the fix proves a deeper AD-engine redesign; +genuine-floor Match.

### Priority 6: camcge #1330 → Epic 5 Walras Transformation (~10–16h)  [retrospective carryforward / Epic 5]
- Implement the CGE-domain structural preprocessing transformation scoped in `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md`: detect the Walras-law rank-deficiency, **drop one redundant market-clearing row** + **fix one price numéraire** (per-model row/numéraire selection), verifying the transformed MCP reaches MODEL STATUS 1 at camcge's NLP optimum (191.7346) without perturbing the economic solution. Guard so a non-degenerate model is never silently altered.
- **Phase 0 acceptance gate (PR20/PR27):** confirm the §3 paper argument empirically on camcge (drop-`lmequil` + fix-`cpi=1` → MS 1 at 191.7346) before generalizing; verify the degeneracy-detection heuristic does not falsely flag a well-posed model.
- **Deliverable:** the Walras drop-row + fix-numéraire transformation lands (or a documented "needs a per-model numéraire declaration" finding); **camcge → MODEL STATUS 1** (+1 Solve) OR the transformation is proven and the residual is a per-model numéraire-selection open item; #1330 resolved or Epic-5-scoped with the empirical result.

### Priority 7 (adjacent backlog): Class-B CGE `stat_pz` Coefficient Discrepancy + Cold-Convex Residue (~10–16h)
- Sprint 29 Day 12 confirmed the Class-B CGE `stat_pz` residual (irscge/lrgcge/moncge/stdcge/marco) is a **general-emit coefficient discrepancy, NOT the Walras singularity** — a distinct, localizable cross-term/coefficient bug the harness can trace. Fix the general-emit defect (converts several Class-B cold-convex models to cold-match). Then finalize the cold-convex Case-b/Case-c partition disposition for the remaining warm-start-only cohort (the Sprint 29 Task-3 survey's residue).
- **Phase 0 acceptance gate (PR27):** `kkt_residual.py` per Class-B model to localize the `stat_pz` coefficient row before the emit change.
- **Deliverable:** the Class-B `stat_pz` general-emit fix lands; ≥2 Class-B CGE models cold-match (genuine-floor); the cold-convex Case-c residue documented for Sprint 39 forcing.

### Priority 8 (Infrastructure): Property-Test Catalog Extension + Re-Baseline + Forcing Scaffold (~6–10h)
- **Sprint 29 retrospective infrastructure recommendations:** (a) extend the AD cross-term property-test catalog (`test_ad_crossterm_shapes.py`) with the **head-domain-offset** and **offset-alias successor** shapes so the P1/P5 fixes are permanently guarded; (b) apply the **PR25 re-baseline** to the stale Rolling-KPIs Match targets (the renumbered S35–S37 ≥45/48/52% lines predate the Sprint-28 methodology lift — re-baseline to the ≥64% line per footnote ⁸); (c) scaffold a **solution-forcing harness** (trust-region / homotopy / multi-start entry point) from the rocket P2 work so the Sprint-38 PATH-consultation sprint inherits a tested lever set rather than starting cold.
- **Deliverable:** the two new property-test fixtures; the re-baselined Rolling-KPIs Match targets for S35–S37; the forcing-harness scaffold + a CONTRIBUTING/Phase-0 note.

### Pipeline Retest (~4h)
- Full pipeline at each checkpoint (Day 5 + Day 10) and final (Day 13) per PR6, using the Sprint 29 `--resolve-changed` checkpoint re-solve so a broken solve surfaces mid-sprint; final retest under ≥ 3 `PYTHONHASHSEED` values (PR12).
- **Deliverable:** updated `gamslib_status.json` (machine-portable paths) + Sprint 29→30 metrics comparison; determinism verified; PR25 genuine-vs-methodology re-baseline recomputed.

## Deliverables
- Head-domain-offset emit-architecture fix — mine solves (+1 Solve) + robert cold-matches (Priority 1)
- rocket #1462 non-convex forcing — rocket matches via a forcing strategy OR a documented solver-side finding (Priority 2)
- hhfair #1236 widened-VARIABLE presolve fix — hhfair matches OR a Case-c finding (Priority 3)
- #1385 runtime-guard `J_gᵀ·lam` cross-term emit — sarf recovers to translate (Priority 4)
- Offset-alias cross-terms (#1111/#1112) — polygon + himmel16 cold-match OR a re-scoped AD-engine filing (Priority 5)
- camcge #1330 Walras drop-row + fix-numéraire transformation — camcge solves OR the transformation proven (Priority 6)
- Class-B CGE `stat_pz` general-emit fix + cold-convex residue disposition (Priority 7)
- Property-test catalog extension + Rolling-KPIs re-baseline + solution-forcing scaffold (Priority 8)
- Updated pipeline metrics + Sprint 30 SPRINT_LOG.md + SPRINT_RETROSPECTIVE.md

## Acceptance Criteria
- **Solve:** ≥ 109 models solve (up from Sprint 29's 107; +2 firm via mine [+1, Priority 1] + rocket [+1, Priority 2]; camcge is a conditional +1 on the Epic-5 transformation)
- **Match:** maintain ≥ 92 as-measured; **genuine floor 69 → ≥ 72** (robert [P1] + hhfair [P3, if Case b] + polygon/himmel16 [P5] + Class-B CGE [P7] convert warm/methodology matches into genuine cold matches); genuine-gain figure tracked per PR25
- **model_infeasible:** ≤ 5 (down from 7; −2 via mine [#1443] + rocket [#1462] recoveries; −1 more if camcge lands)
- **path_syntax_error:** maintain ≤ 8
- **path_solve_terminated:** maintain ≤ 5
- **Translate:** ≥ 135/142 (maintain; stretch +1 via #1385 sarf recovery)
- **Parse:** ≥ 142/142 (maintain)
- **Tests:** ≥ 4,990 (up from 4,971; the head-offset + offset-alias property fixtures + warm-start/forcing regression tests add coverage)
- **Determinism:** byte-identical pipeline output under ≥ 3 `PYTHONHASHSEED` values (PR12)
- **Epic 5:** the camcge Walras drop-row + fix-numéraire transformation lands or is empirically proven; #1330 resolved or Epic-5-scoped with the result
- **Process:** the Rolling-KPIs Match targets for S35–S37 re-baselined off the ≥64% line (footnote ⁸); the head-offset/offset-alias property fixtures guard P1/P5
- **Quality:** all quality gates pass; all fixes have regression tests; emit-touching PRs pass the golden-staleness check (PR26) + the presolve-divergence detector + the `--resolve-changed` checkpoint re-solve

**Estimated Effort:** 92–142 hours over a 14-day sprint (Day 0 + Days 1–13). At ≤ 12 hours/day this fits within the 168-hour budget (14 × 12 = 168) with slack. Per-priority budgets: P1 head-offset architecture [14–20h] + P2 rocket forcing [10–16h] + P3 hhfair widened-VARIABLE [10–16h] + P4 #1385 cross-terms [10–16h] + P5 offset-alias AD [12–18h] + P6 camcge Walras transform [10–16h] + P7 Class-B CGE + cold-convex residue [10–16h] + P8 infrastructure [6–10h] + pipeline retest [4h] = 86–132h work-item total, plus ~6–10h prep tasks (Phase-0 gates for the diagnosis-heavy tracks). The lower bound assumes the deepest tracks (P1 multi-site head-offset re-derivation, P2 non-convex forcing, P6 Epic-5 transformation) partially slip to Sprint 31; the upper bound assumes all 8 priorities ship. The Sprint 29 KKT-residual harness, presolve-divergence detector, golden-staleness gate, and `--resolve-changed` checkpoint re-solve are reused throughout, so the diagnosis cost is lower than a from-scratch sprint. Heaviest day budget: a ~11h day mid-sprint (the P1 multi-site head-offset re-derivation + the robert/mine dual verification).
**Risk Level:** HIGH — the core carryforwards are the tracks Sprint 29 explicitly REPLAN'd *because* they proved multi-site or intrinsic (P1 head-offset architecture, P2 rocket non-convex forcing, P6 CGE Walras transformation), so the sprint front-loads the hardest work. The primary mitigations are (a) the Sprint-29 KKT-residual harness making the Case-(a/b/c) PROCEED/REPLAN gate mechanical, (b) **robert as the minimal head-offset reproduction** de-risking P1 (a correct robert fix generalizes to mine), (c) the Epic-5 scoping doc's paper-verified transformation de-risking P6, and (d) the P2 forcing scaffold explicitly feeding the Sprint-38 PATH consultation so an intrinsic-non-convergence finding is a clean hand-off, not a dead end. The offset-alias track (P5) carries the residual #1111/#1112 architectural-redesign risk with a Case-c REPLAN exit to Sprint 31.

---

# Sprint 31 (Weeks 27–28): Sprint 30 Carryforward — Head-Offset IR Plumbing, General-Alias AD (#1111/#1112) & Dual-Consistent CGE

**Goal:** Land the Sprint 30 Solve/Match carryforwards the Day-13 closeout REPLAN'd — each now carries a *de-risked, control-verified* recipe rather than an open question (`SPRINT_30/SPRINT_RETROSPECTIVE.md` §4). The core is the **mine head-domain-offset architecture** (#1443), which Sprint 30 Day 6 found needs a **foundational IR change first** (the head-offset position+amount is not stored today — only a `has_head_domain_offset` bool), so this sprint plumbs the head-offset detail through parse → normalize → KKT and *then* builds the shared 3-site index-map helper; the **offset-alias general-alias core #1111/#1112** (polygon — Sprint 30 Day 7 control-verified the exact 4-term fix at warm-match 0.780, and Day 8 implemented+verified the objective-successor half; the remaining **distance-Jacobian second-index** is the general-alias core that must land coupled); the **camcge #1330 dual-consistent Walras transform** (Sprint 30 Day 11 found the design's drop-row is primal-correct but breaks the MCP *dual* — the price-pin gives the correct omega 191.735, so the fix is a dual-consistent multiplier redefinition, not the naive row-drop); the **#1385 sarf symbolic-emit workstream** (the atomic runtime-guard cross-term emit is the Sprint-26-failed architecture, rebuilt as a dedicated builder-pipeline-aware path with the banked `stat_task` derivation); the **cold-convex obj-grad residue** (hhfair `stat_u` / CGE `stat_xp` — the objective-defining-intermediate-variable family whose sign-flip fix was *control-refuted* Sprint 30, so it needs a non-sign-flip treatment); and **rocket #1462 non-convex forcing** advancing to the PATH-consultation input (the scaffold landed Sprint 30; the concrete PATH question is banked). (See `SPRINT_30/SPRINT_RETROSPECTIVE.md` §4 + the per-track ISSUE docs for the banked recipes.)

**Note:** The six Sprint-30 REPLAN carryforwards (Priorities 1–6) are the core; Priority 7 pulls the deferred property-test fixtures (the head-offset + polygon successor shapes, now unblockable once P1/P2 land) + the genuine-floor KPI tracking. The Sprint 28–30 diagnostic tooling (KKT-residual harness, presolve-divergence detector, golden-staleness gate, `--resolve-changed` checkpoint re-solve, the `--force` solution-forcing scaffold) is reused throughout rather than rebuilt. The PATH-author-consultation / quality / release work that previously occupied Sprints 34–36 moves to **Sprints 38–40** — see the renumbered sections below.

## Components

### Priority 1: mine Head-Offset IR Plumbing + Shared 3-Site Helper (#1443) (~18–24h)  [retrospective carryforward]
- Sprint 30 Day 6 REPLAN'd #1443: the cold LCP breaks (~4.07e10 across all four k-directions), and the shared index-map helper the design calls for **cannot be built without first plumbing the head-offset detail through the IR** — `pr.has_head_domain_offset` is a bare `bool`, and after normalization `pr.domain = (k,l,i,j)` with the `l+1` head lost. **Phase 1:** store the head-offset position+amount on `EquationDef` through parse → normalize → KKT (a foundational IR change; blast-radius-guard against the emit core). **Phase 2:** the single head-offset index-map helper parameterized by (head-offset δ on `l`, param offsets `li(k)`/`lj(k)`) called by all three sites — (1) `comp_pr` emission, (2) the `--nlp-presolve` dual transfer, (3) the landed `stat_x` cross-term — applied atomically.
- **Phase 0 acceptance gate (PR20/PR24):** verify the plumbed head-offset detail round-trips (unit tests) before the emit change; then the cold-INFES-by-direction histogram drives the multi-site fix (`kkt_residual.py` residual → 0 warm, then cold MS 1).
- **Deliverable:** the head-offset IR plumbing + shared 3-site helper land; **mine → MODEL STATUS 1** (+1 Solve); #1443 closed (or a documented deeper-architecture REPLAN if a 4th site surfaces).

### Priority 2: Offset-Alias General-Alias Core #1111/#1112 (polygon) (~14–20h)  [retrospective carryforward]
- Sprint 30 Day 7 control-verified polygon's **4-term coupled fix** (warm-match 0.780 ≈ NLP 0.7797); Day 8 implemented + verified the **objective-successor half** (interior-representative selection in `_build_indexed_gradient_term`) but reverted it — it can't ship without the coupled **distance-Jacobian second-index cross-term**, which is the **#1111/#1112 general-alias core** (a variable at two index-positions of a 2-index constraint; the Jacobian already computes the second-index entries but `_add_indexed_jacobian_terms` drops them — the Issue #1110 multi-pattern correction is diagonal-vs-off-diagonal topology, not var-at-two-indices). Land both halves together, tightly gated. himmel16 is documented **non-convex** (Sprint 30 Day 7 refuted its sign fix — no emit fix converts it).
- **Phase 0 acceptance gate (PR20):** enable `shape8_offset_alias_successor` (drop the strict-xfail) as the completion gate; the control-verified 4-term recipe is banked in `ISSUE_1143` Day-7/8 blocks; confirm no regression to the CGE multi-pattern cohort (`--resolve-changed` GO).
- **Deliverable:** polygon's coupled offset-alias fix lands (warm-match, genuine-floor +1); the `#1110`/`#1111`/`#1112` second-index cross-term generalizes; **#1111/#1112 resolved (the general-alias core), with #1143 closing as the polygon instance** — OR a re-scoped AD-engine filing if the tight gate proves infeasible.

### Priority 3: camcge #1330 → Dual-Consistent Walras Transform (~12–18h)  [retrospective carryforward / Epic 5]
- Sprint 30 Day 11 refined the Epic-5 transform: the premise holds (NLP optimum `p=pd0`), and **pinning the price ray reaches the correct allocation (omega 191.735)** — but the design's **drop-one-market-clearing-row breaks the MCP dual** (every market-clearing multiplier is a needed price/wage in the stationarity; dropping a row orphans it → omega 299, MS-4). The fix is a **dual-consistent multiplier redefinition** (express the dropped market's dual via Walras' law so it stays available in the stationarity), gated by the S1∧S2∧S3 degeneracy detector (pass-through default).
- **Phase 0 acceptance gate (PR20/PR27):** the price-pin recipe (fix `p('services')=pd0` → omega 191.735, MS-4) is the banked starting point (`ISSUE_1330` + `CAMCGE_WALRAS_TRANSFORM_DESIGN.md` Day-11); prototype the dual-consistent redefinition on `/tmp` to MS 1 before the src change; verify the detector flags only camcge across irscge/lrgcge/moncge/stdcge.
- **Deliverable:** the dual-consistent Walras transform lands — **camcge → MODEL STATUS 1** (+1 Solve) — OR a documented per-model-numéraire-declaration fallback; #1330 resolved or Epic-5-scoped with the dual-consistent result.

### Priority 4: #1385 sarf — Symbolic Runtime-Guard Cross-Term Emit Workstream (~14–20h)  [retrospective carryforward]
- Sprint 30 Day 9 REPLAN'd #1385 as a **dedicated builder-pipeline-aware symbolic-emit workstream** (the atomic fix is the Sprint-26-Day-4-failed architecture — the `nu_slack("srn")` set-name-literal bug). Rebuild it: (1) extend `_is_blowup_dynamic_subset_equation` from srpchase's 1-D to sarf's **2-D** dynamic-subset shape (`tbal(g,t)$taskposs`, `equipb1/equipb2`); (2) a **new symbolic cross-term emit** in `src/kkt/stationarity.py` differentiating each short-circuited body **once parametrically** in `(g,t,m,n)` — the banked 6-guarded-term `stat_task` derivation, no set-name multiplier indices; the re-emit + cross-terms land atomically.
- **Phase 0 acceptance gate (PR20):** the emit must be **O(constraints), not O(instances)** (sarf's 1,152 Cartesian instances) — time `sarf_mcp.gms` against the translate budget; verify the re-emitted `stat_task` against the banked hand-derivation; regenerated golden byte-stable.
- **Deliverable:** the symbolic runtime-guard re-emit + `J_gᵀ·lam` cross-terms land; **sarf recovers to translate** (+Translate) OR a documented re-scoping if the parametric emit re-triggers the timeout; #1385 closed or re-scoped.

### Priority 5: Cold-Convex Obj-Grad Residue (hhfair `stat_u` / CGE `stat_xp`) (~10–16h)  [retrospective carryforward]
- Sprint 30 identified a recurring **objective-defining-intermediate-variable** residue: a variable appearing only in the objective *defining equation* (`obj =e= prod(x**a)`) and also market-cleared leaves a `stat_*` residual (hhfair `stat_u` rel 2.0; irscge/lrgcge/moncge `stat_xp` rel ~0.06 after the Day-5 case-normalization fix). The obvious inlined-obj-grad **sign-flip fix was control-refuted three times** (hhfair Days 4/6, himmel16 Day 7) — flipping makes hhfair *worse* (72→22). The correct treatment is the objective-gradient reduction through the defining-equation multiplier (ν_objective), not a sign flip — diagnose the exact reduction on hhfair (the cleanest instance), then verify it converts the CGE cluster to Case-a (residual → 0).
- **Phase 0 acceptance gate (PR27):** a control experiment (like Sprint 30's) must show the candidate treatment reaches the NLP optimum on hhfair **before** the (high-blast-radius) objective-gradient src change; abort to a documented non-convexity finding if hhfair proves genuinely Case-c.
- **Deliverable:** the objective-defining-intermediate-variable obj-grad treatment lands (hhfair +1 Match + irscge/lrgcge/moncge → Case-a, genuine-floor) OR a documented Case-c non-convexity finding for the family.

### Priority 6: rocket #1462 — Non-Convex Forcing → PATH-Consultation Input (~8–12h)  [retrospective carryforward]
- The `--force {homotopy,multistart,optfile}` solution-forcing scaffold landed Sprint 30 (Days 2–3); no emittable-GAMS lever converges rocket (intrinsic non-convergence; INFES 477 → 382 best but never crosses). Exhaust the remaining emittable levers (reformulation of the `1/ht²`,`1/m²` division-by-variable Jacobian; scaled/relaxed continuation schedules) and **author the concrete PATH-consultation question** that feeds the renumbered Sprint 39 consultation (`NONCONVEX_FORCING_SURVEY.md` §4 has the draft scope).
- **Phase 0 acceptance gate (PR27):** re-confirm the emit residual is clean at the NLP point (Case-c) before any forcing attempt.
- **Deliverable:** rocket → match via a documented forcing/reformulation strategy (+1 Solve) OR the finalized PATH-consultation input for Sprint 39; #1462 advanced or handed off.

### Priority 7 (Infrastructure): Property-Test Catalog Completion + Genuine-Floor Tracking (~6–10h)
- Complete the AD cross-term property catalog the Sprint-30 REPLANs deferred: **enable `shape8_offset_alias_successor`** (the polygon completion gate, once P2 lands) + add the **head-domain-offset fixture** (once P1's IR plumbing lands, guarding the mine index-map). Recompute the PR25 **genuine-floor tracking** against the S31–S36 re-baselined Match KPIs (footnote ⁸ ramp S31 ≥73 → …). Refresh the `--resolve-changed` checkpoint targets for the newly-touched emit sites.
- **Deliverable:** the two enabled/added property fixtures; the recomputed genuine-floor tracking; the checkpoint target list refreshed.

### Pipeline Retest (~4h)
- Full pipeline at each checkpoint (Day 5 + Day 10) and final (Day 13) per PR6, using the `--resolve-changed` checkpoint re-solve; final retest under ≥ 3 `PYTHONHASHSEED` values (PR12).
- **Deliverable:** updated `gamslib_status.json` (machine-portable paths) + Sprint 30→31 metrics comparison; determinism verified; PR25 genuine-vs-methodology re-baseline recomputed.

## Deliverables
- mine head-offset IR plumbing + shared 3-site helper — mine solves (+1 Solve) (Priority 1)
- Offset-alias general-alias core #1111/#1112 — polygon coupled fix lands (genuine-floor) (Priority 2)
- camcge #1330 dual-consistent Walras transform — camcge solves OR a per-model-numéraire fallback (Priority 3)
- #1385 sarf symbolic runtime-guard cross-term emit — sarf recovers to translate (Priority 4)
- Cold-convex obj-grad residue treatment — hhfair + CGE cluster Case-a OR a Case-c finding (Priority 5)
- rocket #1462 forcing → the finalized PATH-consultation input for Sprint 39 (Priority 6)
- Property-test catalog completion (shape8 + head-offset fixtures) + genuine-floor tracking (Priority 7)
- Updated pipeline metrics + Sprint 31 SPRINT_LOG.md + SPRINT_RETROSPECTIVE.md

## Acceptance Criteria
- **Solve:** ≥ 109 models solve (up from Sprint 30's 107; +2 firm via mine [+1, Priority 1] + camcge [+1, Priority 3, the dual-consistent Walras]; rocket [Priority 6] a conditional +1)
- **Match:** maintain ≥ 92 as-measured; **genuine floor 70 → ≥ 73** (polygon [P2] + hhfair/Class-B obj-grad [P5] convert the Sprint-30-REPLAN'd warm/methodology matches into genuine cold matches); genuine-gain figure tracked per PR25
- **model_infeasible:** ≤ 5 (down from 7; −2 via mine [#1443] + camcge [#1330] recoveries)
- **path_syntax_error:** maintain ≤ 8
- **path_solve_terminated:** maintain ≤ 5
- **Translate:** ≥ 135/142 (maintain; stretch +1 via #1385 sarf recovery)
- **Parse:** ≥ 142/142 (maintain)
- **Tests:** ≥ 5,000 (up from 4,997; the head-offset + enabled offset-alias property fixtures + the dual-consistent-Walras / symbolic-emit regression tests add coverage)
- **Determinism:** byte-identical pipeline output under ≥ 3 `PYTHONHASHSEED` values (PR12)
- **Epic 5:** the camcge dual-consistent Walras transform lands or is empirically proven with the per-model-numéraire fallback; #1330 resolved or Epic-5-scoped with the dual-consistent result
- **Process:** the genuine-floor ramp (S31 ≥73) tracked against the re-baselined ≥64% Match line (footnote ⁸); the head-offset/offset-alias property fixtures guard P1/P2
- **Quality:** all quality gates pass; all fixes have regression tests; emit-touching PRs pass the golden-staleness check (PR26) + the presolve-divergence detector + the `--resolve-changed` checkpoint re-solve

**Estimated Effort:** 92–134 hours over a 14-day sprint (Day 0 + Days 1–13). At ≤ 12 hours/day this fits within the 168-hour budget (14 × 12 = 168) with slack. Per-priority budgets: P1 mine head-offset IR plumbing + helper [18–24h] + P2 offset-alias #1111/#1112 core [14–20h] + P3 camcge dual-consistent Walras [12–18h] + P4 #1385 sarf symbolic emit [14–20h] + P5 cold-convex obj-grad residue [10–16h] + P6 rocket forcing/PATH input [8–12h] + P7 infrastructure [6–10h] + pipeline retest [4h] = 86–124h work-item total, plus ~6–10h prep tasks (Phase-0 gates for the diagnosis-heavy tracks). The lower bound assumes the deepest tracks (P1 foundational IR plumbing, P4 symbolic-emit rebuild) partially slip to Sprint 32; the upper bound assumes all 7 priorities ship. The Sprint 28–30 diagnostic tooling (KKT-residual harness, presolve-divergence detector, golden-staleness gate, `--resolve-changed` checkpoint re-solve, `--force` scaffold) is reused throughout, so the diagnosis cost is lower than a from-scratch sprint — and every carryforward inherits a Sprint-30 control-verified recipe. Heaviest day budget: a ~11h day mid-sprint (the P1 head-offset IR plumbing Phase 1 + Phase 2 helper wiring).
**Risk Level:** HIGH — the carryforwards are the tracks Sprint 30 explicitly REPLAN'd *because* they proved to need foundational work (P1 IR plumbing), the general-alias AD core (P2 #1111/#1112), a dual-side transform (P3 camcge), a failed-architecture rebuild (P4 #1385), or a refuted-hypothesis re-diagnosis (P5 obj-grad). The decisive mitigation is that **each track now carries a Sprint-30 *control-verified* recipe or a *precisely-pinned* root cause** (polygon's 4-term fix warm-matches; camcge's price-pin gives omega 191.735; hhfair's sign-flip is refuted so the reduction is the target; sarf's `stat_task` is hand-derived) — so Sprint 31 implements against specifications, not open questions. Additional mitigations: (a) the KKT-residual harness Case-(a/b/c) PROCEED/REPLAN gate; (b) the PR24 control-experiment-before-implement rule (which refuted five hypotheses in Sprint 30 before any bad ship); (c) explicit REPLAN exits on P1 (a 4th head-offset site), P4 (timeout re-trigger), and P5 (genuine Case-c) that hand cleanly to a later sprint.

---

# Sprint 32 (Weeks 29–30): Sprint 31 Carryforward — mine Head-Offset 4th Site, sarf 4-D Stationarity, camcge Dual-Consistent Walras (Epic 5), rocket PATH-Consultation & Case-c Documentation

**Goal:** Land the Sprint 31 Solve/Match carryforwards the Day-13 closeout REPLAN'd — each carries a *precisely-pinned root cause* rather than an open question (`SPRINT_31/SPRINT_RETROSPECTIVE.md` §4). The core is the **mine head-offset 4th bound-complementarity site** (#1443 — Sprint 31 landed the head-offset IR foundation `EquationDef.head_domain_offsets` + the Site-2 dual transfer, but Day 3 found a residual 4th site: the LP bound-duals warm-started into `piU_x` don't satisfy the emitted `stat_x` at bound-active rows); the **sarf 4-D `task`-variable stationarity sparsification** (#1385 — Sprint 31 Day 8 found the 2-D constraint gate fires but sarf still times out on the **369,024-instance** 4-D `task(g,t,mn,mn)` `stat_task` enumeration, not the 1,152 constraints); the **camcge dual-consistent Walras / CASE_B `stat_mps`** (#1330 → Epic 5 — Sprint 31 Days 6–7 re-diagnosed camcge as CASE_B, the `nu_mps_fx` fixing-multiplier defect, NOT the clean Walras singular-Jacobian case); the **rocket PATH-consultation forcing input** (#1462 — Sprint 31 exhausted the division-by-variable reformulation; the intrinsic non-convergence is now a *ruled-out-lever* question for the renumbered Sprint 39 consultation); and the **hhfair + CGE-cluster Case-c documentation** (#1236 — Sprint 31 Day 10 control-refuted the ν_objective reduction, documenting the objective-defining-intermediate-variable family as genuine non-convex Case-c). (See `SPRINT_31/SPRINT_RETROSPECTIVE.md` §4 + the per-track ISSUE docs for the banked diagnoses.)

**Note:** The five Sprint-31 REPLAN carryforwards (Priorities 1–5) are the core; Priority 6 pulls the adjacent offset-alias / symbolic-emit backlog + residual failure-cohort re-triage, and Priority 7 the infrastructure (property-catalog extension for the head-offset 4th-site + sarf 4-D shapes, genuine-floor KPI tracking, Epic-4-SUMMARY groundwork) to fill the 14-day budget. The S28–31 diagnostic tooling (KKT-residual harness, presolve-divergence detector, golden-staleness gate, `--resolve-changed` checkpoint re-solve, the `--force` solution-forcing scaffold) is reused throughout rather than rebuilt. The PATH-author-consultation / quality / release work occupies the renumbered **Sprints 38–40** — see the sections below.

## Components

### Priority 1: mine #1443 — Head-Offset 4th Bound-Complementarity Site (~14–20h)  [retrospective carryforward]
- Sprint 31 Days 1–2 landed the head-offset IR foundation (the Phase-1 `EquationDef.head_domain_offsets` field + the shared `head_offset_marginal_index_map` Site-2 `--nlp-presolve` dual transfer, both on `main`), but Day 3 REPLAN'd: mine stays `model_infeasible` via a **residual 4th bound-complementarity / `stat_x` reconciliation** — the LP reduced costs `x.m` warm-started into `piU_x` don't satisfy the emitted `stat_x` at bound-active rows (a degenerate-LP bound-dual ambiguity coupled with the head-offset cross-term). Derive a **stationarity-consistent bound-multiplier** (rather than the `x.m` transfer) so the emitted `stat_x` balances at bound-active rows.
- **Phase 0 acceptance gate (PR24/PR27):** the `kkt_residual.py` CASE_B `stat_x` localization at bound-active rows is the banked starting point (`ISSUE_1443` Day-3 block); the cold-INFES-by-direction histogram drives the fix; prototype the bound-multiplier derivation to warm-residual → 0, then cold MS 1, before the emit change.
- **Deliverable:** mine → **MODEL STATUS 1** (+1 Solve, +1 genuine floor if it cold-matches); #1443 closed — OR a documented deeper-IR-architecture REPLAN if the bound-dual reconciliation surfaces a 5th coupling.

### Priority 2: sarf #1385 — 4-D `task`-Variable Stationarity Sparsification (~14–20h)  [retrospective carryforward]
- Sprint 31 Day 8 found the 2-D dynamic-subset constraint gate (`_is_blowup_2d_condition_equation`) fires on `tbal`/`equipb1`/`equipb2` but sarf **still times out** — the dominant blow-up is the **369,024-instance** 4-D `task(g,t,mn,mn)` variable's `stat_task` enumeration (16·24·31·31), not the 1,152 constraint instances. Sparsify the 4-D `task` stationarity to the `$taskposs`-active subset (369K → the active entries) via a builder-pipeline-aware symbolic `stat_task` emit — the banked hand-derivation, no set-name-literal multiplier indices.
- **Phase 0 acceptance gate (PR20):** the emit must be **O(active-instances), not O(Cartesian-instances)** — time `sarf_mcp.gms` against the translate budget; verify the re-emitted `stat_task` against the banked derivation; regenerated golden byte-stable; the 2-D constraint gate (built + reverted S31) re-lands coupled with the 4-D sparsification.
- **Deliverable:** the 4-D `task` sparsification + 2-D gate land; **sarf recovers to translate** (+1 Translate) OR a documented re-scoping if the parametric emit re-triggers the timeout; #1385 closed or re-scoped.

### Priority 3: camcge #1330 → Dual-Consistent Walras / CASE_B `stat_mps` (~12–18h)  [retrospective carryforward / Epic 5]
- Sprint 31 Days 6–7 re-diagnosed camcge as **CASE_B** (harness `stat_mps` rel 1.05 / raw −210, dual-transfer CONSISTENT) — a **`nu_mps_fx` fixing-multiplier transfer/stationarity defect** (`mps` is a fixed variable), a *different bug class* than the Walras singular-Jacobian the Epic-5 transform targets. **First** resolve the `stat_mps`/`nu_mps_fx` Case-B residual (re-diagnose via the harness), **then** the dual-consistent numéraire (the price-pin reaches the correct omega 191.735, MS-4; the fix is a Walras-consistent multiplier redefinition, not a naive row-drop). This is Epic-5-domain CGE work.
- **Phase 0 acceptance gate (PR20/PR27):** prototype the `stat_mps` fix + the dual-consistent redefinition on `/tmp` to MS 1 before any `src/` change; verify the degeneracy detector flags only camcge across irscge/lrgcge/moncge/stdcge.
- **Deliverable:** the `stat_mps` fix + dual-consistent Walras transform land — **camcge → MODEL STATUS 1** (+1 Solve) as an Epic-5 deliverable — OR a documented per-model-numéraire-declaration fallback; #1330 resolved or Epic-5-scoped with the CASE_B + dual-consistent result.

### Priority 4: rocket #1462 — PATH-Consultation Forcing Input (~8–12h)  [retrospective carryforward]
- Sprint 31 Day 11 **exhausted the last emittable lever** (the division-by-variable reformulation — MS-5 cold/warm/continuation): rocket's non-convergence is intrinsic to the discretized optimal-control MCP structure, not the `1/ht²`,`1/m²` Jacobian conditioning. Finalize + package the **concrete PATH-consultation input** (the reformulation now a *ruled-out* candidate in `BACKLOG_FIX_SURFACE_ANALYSIS.md` §3, sharpening the question toward the intrinsic structure) for the renumbered **Sprint 39** consultation; try any remaining emittable lever the packaging surfaces.
- **Phase 0 acceptance gate (PR27):** re-confirm the emit residual is clean at the NLP point (Case-c) before any forcing attempt (keeps rocket a forcing problem, not a latent emit bug).
- **Deliverable:** the finalized, packaged PATH-consultation input for Sprint 39 (rocket's concrete question set + the ruled-out-lever survey) OR +1 Solve if a lever crosses; #1462 handed off.

### Priority 5: hhfair + CGE Cluster #1236 — Case-c Formalization (~6–10h)  [retrospective carryforward]
- Sprint 31 Day 10 **control-refuted** the ν_objective reduction (inert on the CGE cluster; the sign flip stayed BANNED) and documented hhfair + irscge/lrgcge/moncge as **genuine non-convex Case-c** (the objective-defining-intermediate-variable family: a variable appearing only in `obj =e= prod(x**a)` and also market-cleared; the cold solve sits at a spurious local KKT point, the match reachable only via the presolve warm-start). Formalize the finding: extend the `kkt_residual.py` Case-c classifier to auto-flag the family, close the ISSUE as documented-non-convex, and hand the models to the Sprint 39 forcing/PATH work (no emit fix expected).
- **Phase 0 acceptance gate (PR27):** any candidate treatment must reach the NLP optimum in a `/tmp` control before a `src/` change — the sign flip is banned (refuted 4× across S30–S31); default to the documented Case-c finding.
- **Deliverable:** the Case-c finding formalized (harness auto-classification + `ISSUE_1236` closure as documented-non-convex); the family handed to the Sprint 39 forcing/PATH consultation.

### Priority 6: Adjacent Backlog + Deferred Cross-Terms (~10–16h)
- Pull adjacent open backlog that reuses the S28–31 tooling: **generalize the #1111/#1112 offset-alias second-index-transpose core beyond polygon/ps2** (audit other 2-index-transpose models for cold-emit corrections, genuine-floor); the srpchase/sarf symbolic-emit family follow-ons; **re-triage the residual `model_infeasible` cohort** (agreste/cesam/fawley/lnts) + `path_syntax_error` members via the KKT-residual harness. Each candidate gated by a `--resolve-changed` GO (no changed-golden regression).
- **Deliverable:** ≥ 1 additional model recovered (Solve/Match/Translate) OR the cohort re-triaged with banked harness diagnoses for Sprint 34.

### Priority 7 (Infrastructure): Property-Catalog + Genuine-Floor Tracking + Checkpoint Refresh (~6–10h)
- Extend the AD cross-term property catalog with the **mine head-offset 4th-site** + **sarf 4-D `task`** shapes (once P1/P2 land, guarding the new emit paths); recompute the PR25 **genuine-floor tracking** against the S32–S36 re-baselined Match KPIs (footnote ⁸ ramp S32 ≥75); refresh the `--resolve-changed` checkpoint targets for the newly-touched emit sites; begin the Epic-4 `SUMMARY.md` sprint-by-sprint groundwork (S30-retro §5 front-loading recommendation).
- **Deliverable:** the property fixtures; the recomputed genuine-floor tracking; the refreshed checkpoint target list; the Epic-4-SUMMARY skeleton.

### Pipeline Retest (~4h)
- Full pipeline at each checkpoint (Day 5 + Day 10) and final (Day 13) per PR6, using the `--resolve-changed` checkpoint re-solve; final retest under ≥ 3 `PYTHONHASHSEED` values (PR12).
- **Deliverable:** updated `gamslib_status.json` (machine-portable paths) + Sprint 31→32 metrics comparison; determinism verified; PR25 genuine-vs-methodology re-baseline recomputed.

## Deliverables
- mine #1443 head-offset 4th-site fix — mine solves (+1 Solve) OR a deeper-IR-architecture REPLAN (Priority 1)
- sarf #1385 4-D `task`-variable stationarity sparsification — sarf recovers to translate (+1 Translate) (Priority 2)
- camcge #1330 dual-consistent Walras + `stat_mps` — camcge solves OR a per-model-numéraire fallback, Epic-5-scoped (Priority 3)
- rocket #1462 finalized PATH-consultation input for Sprint 39 (Priority 4)
- hhfair + CGE cluster #1236 Case-c formalized (harness auto-classification + ISSUE closure) (Priority 5)
- Adjacent backlog recoveries / failure-cohort re-triage (Priority 6)
- Property-catalog completion (head-offset 4th-site + sarf 4-D fixtures) + genuine-floor tracking + checkpoint refresh (Priority 7)
- Updated pipeline metrics + Sprint 32 SPRINT_LOG.md + SPRINT_RETROSPECTIVE.md

## Acceptance Criteria
- **Solve:** ≥ 109 models solve (up from Sprint 31's 107; +2 firm via mine [+1, Priority 1] + camcge [+1, Priority 3, the Epic-5 dual-consistent Walras]; rocket [Priority 4] is deferred to the PATH consultation)
- **Match:** maintain ≥ 92 as-measured; **genuine floor 74 → ≥ 75** (mine [P1] + camcge [P3] cold-matches convert to genuine cold matches); genuine-gain figure tracked per PR25
- **model_infeasible:** ≤ 5 (down from 7; −2 via mine [#1443] + camcge [#1330] recoveries)
- **path_syntax_error:** maintain ≤ 8
- **path_solve_terminated:** maintain ≤ 5
- **Translate:** ≥ 135/142 (maintain; **+1 via #1385 sarf** 4-D sparsification)
- **Parse:** ≥ 142/142 (maintain)
- **Tests:** ≥ 5,080 (up from 5,074; the head-offset 4th-site + sarf 4-D + CGE Case-c-classifier regression tests add coverage)
- **Determinism:** byte-identical pipeline output under ≥ 3 `PYTHONHASHSEED` values (PR12)
- **Epic 5:** the camcge `stat_mps` + dual-consistent Walras transform lands or is empirically proven with the per-model-numéraire fallback; #1330 resolved or Epic-5-scoped with the CASE_B + dual-consistent result
- **Process:** the genuine-floor ramp (S32 ≥75) tracked against the re-baselined ≥64% Match line (footnote ⁸); the head-offset 4th-site / sarf 4-D property fixtures guard P1/P2; hhfair + the CGE cluster formally closed as documented Case-c
- **Quality:** all quality gates pass; all fixes have regression tests; emit-touching PRs pass the golden-staleness check (PR26) + the presolve-divergence detector + the `--resolve-changed` checkpoint re-solve

**Estimated Effort:** 80–120 hours over a 14-day sprint (Day 0 + Days 1–13). At ≤ 12 hours/day this fits within the 168-hour budget (14 × 12 = 168) with slack. Per-priority budgets: P1 mine 4th-site [14–20h] + P2 sarf 4-D stationarity [14–20h] + P3 camcge dual-consistent Walras [12–18h] + P4 rocket PATH input [8–12h] + P5 hhfair/CGE Case-c [6–10h] + P6 adjacent backlog [10–16h] + P7 infrastructure [6–10h] + pipeline retest [4h] = 74–110h work-item total, plus ~6–10h prep tasks (Phase-0 gates for the diagnosis-heavy tracks). The lower bound assumes the deepest tracks (P1 4th-site bound-dual reconciliation, P3 Epic-5 camcge) partially slip to Sprint 33 (the new Sprint-32 carryforward sprint); the upper bound assumes all 7 priorities ship. The S28–31 diagnostic tooling (KKT-residual harness, presolve-divergence detector, golden-staleness gate, `--resolve-changed` checkpoint re-solve, `--force` scaffold) is reused throughout, so the diagnosis cost is lower than a from-scratch sprint — and every carryforward inherits a Sprint-31 precisely-pinned root cause. Heaviest day budget: a ~11h day mid-sprint (the P1 bound-multiplier re-derivation + the P2 4-D sparsification verification).
**Risk Level:** HIGH — the carryforwards are the tracks Sprint 31 explicitly REPLAN'd *because* they proved deeper than projected (P1 a 4th head-offset site after the IR foundation landed; P2 an O(instances) 369K blow-up, not O(constraints); P3 a CASE_B `nu_mps_fx` fixing-multiplier defect, not clean Walras; P4/P5 intrinsic non-convexity). The decisive mitigation is that **each track carries a Sprint-31 precisely-pinned root cause** (mine's bound-complementarity localization; sarf's 369K finding; camcge's `stat_mps` CASE_B verdict; rocket's exhausted-lever survey; the CGE-cluster Case-c control) — so Sprint 32 implements against specifications, not open questions. Additional mitigations: (a) the KKT-residual harness Case-(a/b/c) PROCEED/REPLAN gate; (b) the PR24/PR27 control-experiment-before-implement rule (which refuted five hypotheses in Sprint 31 before any bad ship); (c) explicit REPLAN exits on P1 (deeper IR architecture), P2 (timeout re-trigger), and P3 (Epic-5 deferral) that hand cleanly to Sprint 33. **camcge is Epic-5-scoped; hhfair + the CGE cluster are documented Case-c (no emit fix converts them).**

---

# Sprint 33 (Weeks 31–32): Sprint 32 Carryforward — mine Head-Offset Cross-Term Architecture, sarf Symbolic-Emit Subsystem, #1111/#1112 Second-Index Generalization, camcge Walras (Epic 5) & rocket/Case-c PATH Forcing

**Goal:** Land the Sprint 32 REPLAN'd carryforwards — each carries a **control-confirmed, precisely-pinned root cause** from the Sprint-32 `/tmp`/harness controls, not an open question (`SPRINT_32/SPRINT_RETROSPECTIVE.md` §4). The three deepest are now from-scratch AD/emit workstreams that Sprint 32 de-risked to a specification: the **mine head-offset bound-active cross-term architecture** (#1443 — Sprint 32 Day 1 confirmed the `N`-derivation closes `stat_x` by construction but yields a *wrong-sign* residual at **6 bound-active rows** requiring an infeasible negative bound multiplier ⇒ the emitted `stat_x` head-offset **cross-term** is inconsistent at bound-active rows, not a warm-start-value fix); the **sarf symbolic parametric `stat_task` emit subsystem** (#1385 — Sprint 32 Day 6 profiled the timeout to `compute_constraint_jacobian` and confirmed the 2-D constraint gate is *necessary but insufficient*: the 369,024 `task(g,t,mn,mn)` columns enumerate via the scalar `acost3` + the variable path, so the fix must eliminate the 369K-column materialization *everywhere* + emit one symbolic guarded `stat_task(g,t,m,n)$taskposs(g,t)` + `task.fx` with parametric cross-terms); and the **#1111/#1112 second-index generalization** (fawley — Sprint 32 Day 11 confirmed `stat_bq`'s qsb/pbal cross-terms miss the `$(sameas(cfq__,cf))` second-index restriction the mbal term has; the `/tmp` patch closes `max|stat_bq|` **473 → 18 [96%]** but a secondary residual + the MS-5 LP-convergence remain — the core's second-index gate must extend from the variable's-first-index to the variable's-second-index-summed shape). Plus the **camcge dual-consistent Walras numéraire** (#1330 → Epic 5 — step 1 landed S32; step 2's numéraire reaches omega 191.7346 but MS-4 residual Walras rank-deficiency) and the **rocket + hhfair/CGE Case-c PATH forcing** (#1462/#1236 — the finalized PATH-consultation input is packaged; the Case-c family is documented, forcing-only). (See `SPRINT_32/SPRINT_RETROSPECTIVE.md` §4 + the per-track banked write-ups: `MINE_5TH_COUPLING_REPLAN.md`, `SARF_TRANSLATE_REPLAN.md`, `P6_BACKLOG_RETRIAGE.md`, `CAMCGE_WALRAS_REPLAN.md`, `ROCKET_PATH_CONSULTATION_INPUT.md`.)

**Note:** The five Sprint-32 REPLAN carryforwards (Priorities 1–5) are the core; Priority 6 pulls the residual failure-cohort re-triage (agreste double-`solve` scope, cesam/lnts Case-c) + adjacent emit backlog, and Priority 7 the infrastructure (property fixtures for the P1/P2/P3 emit paths *once they land*, genuine-floor tracking re-baselined to 74, Epic-4-`SUMMARY` continuation) to fill the 14-day budget. The S28–32 diagnostic tooling (KKT-residual harness incl. the new `case_c_objdef` classifier, presolve-divergence detector, golden-staleness gate, `--resolve-changed` checkpoint re-solve, the `--force` solution-forcing scaffold) is reused throughout rather than rebuilt. The deeper PATH-author back-and-forth / quality / release work occupies the renumbered **Sprints 38–40** — see the sections below; rocket's finalized consultation input (P5) feeds the Sprint-38 consultation.

## Components

### Priority 1: mine #1443 — Head-Offset Bound-Active Cross-Term Architecture (~18–24h)  [Sprint-32 carryforward]
- Sprint 32 Day 1's `/tmp` control refuted the banked bound-multiplier `N`-derivation: it closes `stat_x` **by construction** (direct body 0.000) but the MCP solves to **MS-5 @ 22058** (≠ the NLP optimum 17500) — at **6 bound-active rows** (`x(1,3,{1,2,3})`, `x(3,1,2)`, `x(3,2,1)`, `x(4,1,1)`) the residual `N` carries the sign of the *opposite* bound, requiring an infeasible **negative** bound multiplier, while `N = 0` at every interior row. So the defect is a **wrong-sign residual in the emitted `stat_x` head-offset cross-term** at bound-active rows (`sum(k, lam_pr(k,l,i−li,j−lj)$c − lam_pr(k,l−1,i,j)$c)`), not a warm-start value. Re-derive the head-offset `stat_x` cross-term so it vanishes consistently at bound-active rows (a deeper AD/emit change on the S31 IR foundation).
- **Phase 0 acceptance gate (PR24/PR27):** the corrected cross-term must drive the warm residual → 0 **at the bound-active rows** (no wrong-sign `N`) in a `/tmp` control **before** the `src/` change; assert `modelstat` (the `x.up=inf` experiment is BANNED); then presolve MS-1. Banked: `SPRINT_32/MINE_5TH_COUPLING_REPLAN.md` + the S31 IR foundation.
- **Deliverable:** mine → **MODEL STATUS 1** (+1 Solve, +1 genuine floor if it cold-matches); #1443 closed — OR a documented further-architecture REPLAN if the corrected cross-term surfaces a deeper coupling.

### Priority 2: sarf #1385 — Symbolic Parametric `stat_task` Emit Subsystem (~20–28h)  [Sprint-32 carryforward]
- Sprint 32 Day 6 profiled the timeout to **`compute_constraint_jacobian` (>120s)** and confirmed the extended 2-D constraint gate (`_is_blowup_2d_condition_equation`, fires sarf-only) is **necessary but insufficient** — with the gate active the Jacobian still times out because the **369,024 `task(g,t,mn,mn)` columns** enumerate via the scalar `acost3` (`sum((g,t,m,n)$taskposs(g,t), oc·task)`, untouched by the constraint gate) + the variable-instance path. Build the **symbolic parametric emit subsystem**: eliminate the 369K-column materialization in the constraint Jacobian, the variable enumeration, AND the variable stationarity, replaced by **one symbolic guarded `stat_task(g,t,m,n)$taskposs(g,t)`** (the banked 7-term derivation) + `task.fx$(not active)=0`, with the `J_gᵀ·lam` cross-terms differentiated **once parametrically** (not per-instance), no set-name-literal multiplier indices.
- **Phase 0 acceptance gate (PR20):** the re-emit must be **O(active = 398), not O(369K)** — time `sarf_mcp.gms` against the translate budget (target seconds, srpchase's 1-D analogue 6.56s); verify `stat_task` against the banked derivation (grep-scan clean of set-name literals); the gate + parametric cross-terms + `task.fx` land atomically; new golden byte-stable. Banked: `SPRINT_32/SARF_TRANSLATE_REPLAN.md` + the working 2-D detector (the "necessary" half).
- **Deliverable:** sarf recovers to **translate** (+1 Translate) OR a documented re-scoping if the parametric emit re-triggers the timeout; #1385 closed or re-scoped.

### Priority 3: fawley #1111/#1112 — Second-Index Cross-Term Generalization (~12–18h)  [Sprint-32 carryforward]
- Sprint 32 Day 11 found + control-confirmed fawley's genuine CASE_B (`stat_bq(*,fuel-oil)` rel 0.973): `bq(c,cf)` appears in `qsb(cfq,l,s)`/`pbal(cfq,m)` as the #1111/#1112 second-index-transpose shape, but `stat_bq` applies the `$(sameas(cfq__,cf))` second-index restriction to the **mbal** cross-term and **not** the **qsb/pbal** terms (over-summing over all `cfq__`). The `/tmp` sameas patch closes `max|stat_bq|` **473 → 18 (96%)** but a secondary residual (18.47) + the MS-5 LP-convergence remain. Extend the landed #1111/#1112 core's second-index gate from the *variable's-first-index = equation-index* shape (mbal) to the *variable's-second-index-summed* shape (qsb/pbal); close the residual + confirm the LP convergence.
- **Phase 0 acceptance gate (PR24/PR27):** the extended gate must drive `max|stat_bq| → 0` (not just 96%) in a `/tmp` control and reach MS-1 at the LP optimum (2899.25) **before** the `src/` change; `--resolve-changed --since-commit 4cbf8bff` GO (no polygon/ps2 regression — the core already covers those). Banked: `SPRINT_32/P6_BACKLOG_RETRIAGE.md`.
- **Deliverable:** fawley → **translate + solve** (+1 Solve, +1 genuine floor if it cold-matches) OR a documented re-scoping if the second-index generalization leaks; #1356/#1111/#1112 advanced.

### Priority 4: camcge #1330 → Dual-Consistent Walras Numéraire (~10–16h)  [Sprint-32 carryforward / Epic 5]
- Sprint 32 landed step 1 (the scalar-`fx` `nu_mps_fx` transfer → `stat_mps` Case-a). Day 5 confirmed step 2 (the consumption-weighted numéraire) reaches **omega 191.7346 (correct allocation)** but stays **MS-4** — a residual Walras rank-deficiency on the accounting identities (`gdp`/`depreq`/`hhsaveq`/`gruse`), deeper than a numéraire selection. Implement the **per-model-numéraire-declaration + dual-consistent Walras redefinition** (Epic-5-domain CGE work): keep every market-clearing row, redefine the redundant market's dual via Walras' law so the reduced system is full-rank while the dual stays available.
- **Phase 0 acceptance gate (PR27):** the full transform must reach **MS-1 at omega 191.7346** (`modelstat` asserted) in a `/tmp` prototype **before** any `src/` change; the S1∧S2∧S3 detector flags only camcge across irscge/lrgcge/moncge/stdcge. Banked: `SPRINT_32/CAMCGE_WALRAS_REPLAN.md` + `EPIC_5/CGE_DEGENERACY_SCOPING.md`.
- **Deliverable:** camcge → **MODEL STATUS 1** (+1 Solve) as an Epic-5 deliverable — OR a documented per-model-numéraire-declaration finding if the `/tmp` prototype stays MS-4; #1330 resolved or Epic-5-scoped.

### Priority 5: rocket #1462 + hhfair/CGE #1236 — PATH-Consultation Submission & Case-c Forcing (~8–12h)  [Sprint-32 carryforward]
- Sprint 32 finalized rocket's PATH-consultation input (Case-c boundary re-confirmed; `--force` scaffold emits; every emittable lever ruled out) and closed the hhfair + CGE cluster as documented Case-c (auto-classified `case_c_objdef`). **Submit** the packaged rocket consultation input to the Sprint-38 PATH-author consultation, and **exercise the `--force` scaffold** (homotopy / multistart / optfile) on rocket + the hhfair/CGE Case-c family — the presolve-recovered non-convex models whose only remaining avenue is forcing/reformulation.
- **Phase 0 acceptance gate (PR27):** re-confirm each model's residual is clean at the NLP point (Case-c) before any forcing (keeps them forcing problems, not latent emit bugs); the sign flip stays BANNED for the Case-c family.
- **Deliverable:** the rocket consultation input submitted (feeds Sprint 39); any `--force` lever that crosses recovers a model (+Solve) OR the forcing survey is banked for the PATH consultation; #1462 handed to Sprint 39, #1236 forcing-explored.

### Priority 6: Failure-Cohort Re-Triage + Adjacent Backlog (~8–14h)
- Re-triage the residual failure cohort with the harness: **agreste** (Sprint-32 CASE_B `stat_sales` rel 2.0, a candidate Case-b — but a double-`solve` scenario driver: verify scope before any fix), **cesam** (bilinear SAM, likely Case-c) + **lnts** (bilinear-`step` optimal-control, Case-c) re-confirm; residual `path_syntax_error` members. Pull any adjacent emit backlog the P1/P2/P3 fixes unlock (the srpchase/sarf symbolic-emit family follow-ons). Each candidate gated by a `--resolve-changed` GO.
- **Deliverable:** ≥ 1 additional model recovered (Solve/Match/Translate) OR the cohort re-triaged with banked harness diagnoses.

### Priority 7 (Infrastructure): Property Fixtures + Genuine-Floor Tracking + Checkpoint (~6–10h)
- Add the AD cross-term property fixtures the Sprint-32 P1/P2 REPLANs deferred — **shape12** (head-offset bound-active cross-term, once P1 lands) + **shape13** (sarf symbolic `stat_task`, once P2 lands) + a **fawley second-index** fixture (once P3 lands) — guarding the new emit paths (fail-before/pass-after). Recompute the PR25 **genuine-floor tracking** against the re-baselined ramp (S33 anchor **74**; footnote ⁸); refresh the `--resolve-changed` checkpoint targets for the newly-touched emit sites; continue the Epic-4 `SUMMARY.md` sprint-by-sprint groundwork.
- **Deliverable:** the property fixtures for the tracks that landed; the recomputed genuine-floor tracking; the refreshed checkpoint target list; the Epic-4-SUMMARY continuation.

### Pipeline Retest (~4h)
- Full pipeline at each checkpoint (Day 5 + Day 10) and final (Day 13) per PR6, using the `--resolve-changed` checkpoint re-solve; final retest under ≥ 3 `PYTHONHASHSEED` values (PR12).
- **Deliverable:** updated `gamslib_status.json` (machine-portable paths) + the Sprint 32→33 metrics comparison; determinism verified; PR25 genuine-vs-methodology re-baseline recomputed.

## Deliverables
- mine #1443 head-offset bound-active cross-term fix — mine solves (+1 Solve) OR a documented further-architecture REPLAN (Priority 1)
- sarf #1385 symbolic parametric `stat_task` emit subsystem — sarf recovers to translate (+1 Translate) OR a documented re-scoping (Priority 2)
- fawley #1111/#1112 second-index generalization — fawley solves (+1 Solve) OR a documented gate-leak re-scoping (Priority 3)
- camcge #1330 dual-consistent Walras numéraire — camcge solves OR a per-model-numéraire Epic-5 finding (Priority 4)
- rocket #1462 consultation input submitted (feeds Sprint 39) + hhfair/CGE #1236 Case-c forcing explored (Priority 5)
- Failure-cohort re-triage recoveries / banked diagnoses (Priority 6)
- Property fixtures for the landed emit paths + genuine-floor tracking + checkpoint refresh + Epic-4-SUMMARY continuation (Priority 7)
- Updated pipeline metrics + Sprint 33 SPRINT_LOG.md + SPRINT_RETROSPECTIVE.md

## Acceptance Criteria
- **Solve:** ≥ 108 models solve (up from Sprint 32's 107; +1 firm via any one of mine [P1] / fawley [P3] / camcge [P4], each carrying a Sprint-32 control-confirmed diagnosis; **stretch ≥ 109 if two of the three land, ≥ 110 if all three land**); the +Solve tracks are REPLAN-prone from-scratch AD/emit work
- **Match:** maintain ≥ 92 as-measured; **genuine floor 74 → ≥ 75** (mine [P1] / fawley [P3] cold-matches convert to genuine cold matches); genuine-gain figure tracked per PR25
- **model_infeasible:** ≤ 7 (maintain; −1 per mine [#1443] / camcge [#1330] / fawley recovery)
- **path_syntax_error:** maintain ≤ 8
- **path_solve_terminated:** maintain ≤ 5
- **Translate:** ≥ 135/142 (maintain; **+1 via #1385 sarf** symbolic emit)
- **Parse:** ≥ 142/142 (maintain)
- **Tests:** ≥ 5,085 (up from Sprint 32; the head-offset cross-term + sarf symbolic + fawley second-index regression fixtures add coverage)
- **Determinism:** byte-identical pipeline output under ≥ 3 `PYTHONHASHSEED` values (PR12)
- **Epic 5:** the camcge dual-consistent Walras numéraire lands or is empirically proven with the per-model-numéraire fallback; #1330 resolved or Epic-5-scoped
- **Process:** the genuine-floor ramp anchor re-baselines to **74** at S33 open (footnote ⁸); the head-offset / sarf / fawley property fixtures guard P1/P2/P3; the rocket consultation input is submitted to the Sprint-38 PATH consultation
- **Quality:** all quality gates pass; all fixes have regression tests; emit-touching PRs pass the golden-staleness check (PR26) + the presolve-divergence detector + the `--resolve-changed` checkpoint re-solve

**Estimated Effort:** 86–126 hours over a 14-day sprint (Day 0 + Days 1–13). At ≤ 12 hours/day this fits within the 168-hour budget (14 × 12 = 168) with slack. Per-priority budgets: P1 mine cross-term architecture [18–24h] + P2 sarf symbolic-emit subsystem [20–28h] + P3 fawley #1111/#1112 generalization [12–18h] + P4 camcge Walras numéraire [10–16h] + P5 rocket/Case-c forcing [8–12h] + P6 failure-cohort re-triage [8–14h] + P7 infrastructure [6–10h] + pipeline retest [4h] = 86–126h work-item total. The lower bound assumes the deepest from-scratch tracks (P1 cross-term architecture, P2 symbolic-emit subsystem) partially slip; the upper bound assumes all 7 priorities ship. The S28–32 diagnostic tooling is reused throughout, and every carryforward inherits a **Sprint-32 control-confirmed diagnosis** (not just a pinned location), so the diagnosis cost is lower than a from-scratch sprint. Heaviest day budget: a ~11h day mid-sprint (the P1 cross-term re-derivation + the P2 symbolic-emit verification).
**Risk Level:** HIGH — the three deepest tracks (P1 mine head-offset cross-term architecture, P2 sarf symbolic-emit subsystem, P3 fawley #1111/#1112 second-index generalization) are **from-scratch AD/emit workstreams** the Sprint-32 controls proved are deeper than a bounded change: P1 the cross-term is inconsistent at bound-active rows (not a warm-start value), P2 the 369K-column materialization must be eliminated everywhere (not just the constraint gate), P3 the second-index gate must generalize to a new shape (the "#1111/#1112 gate leaks" risk, confirmed). The decisive mitigation is that **each track carries a Sprint-32 control-confirmed diagnosis** (mine's 6-bound-active-row wrong-sign `N`; sarf's `acost3`-plus-variable-path enumeration; fawley's qsb/pbal `sameas` gap, 473→18) — so Sprint 33 implements against a specification, not an open question. Additional mitigations: (a) the KKT-residual harness Case-(a/b/c) PROCEED/REPLAN gate; (b) the PR24/PR27 control-experiment-before-implement rule (which refuted five hypotheses in Sprint 32 before any bad ship — zero broken code shipped); (c) explicit REPLAN exits on P1 (further architecture), P2 (timeout re-trigger), P3 (gate-leak re-scope), P4 (Epic-5 deferral) that hand cleanly forward. **camcge is Epic-5-scoped; hhfair + the CGE cluster are documented Case-c (no emit fix converts them — forcing/PATH only).**

---

# Sprint 34 (Weeks 33–34): Sprint 33 Carryforward — mine Head-Offset Dual Subsystem, sarf Symbolic-Emit Subsystem, fawley Second-Index Correction, the Max-Convention Bound-Transfer Track, camcge Walras (Epic 5) & rocket PATH Submission

**Goal:** Land the Sprint 33 REPLAN'd/deferred carryforwards — each carries a **Sprint-33 control-confirmed diagnosis** (`SPRINT_33/SPRINT_RETROSPECTIVE.md` §4 + `SPRINT_33/SPRINT_34_CARRYFORWARDS.md`), not an open question. Sprint 33 closed with one genuine bucket move (P6 sample: +1 Solve / +1 Match / +1 genuine floor → **108 / 93 / 75**); its three deepest emit tracks each REPLAN'd/deferred after a `/tmp`/harness control refuted the banked premise **before any bad ship** — so they carry precise, de-risked specifications. The core: the **mine head-offset dual subsystem** (#1443 — S33 Day 2 proved H1 head-label re-keying is *value-invariant* [22→22 nonzero rows]; the residual is a deeper head-offset dual-architecture mismatch — the head-placed precedence dual not mapping to `stat_x` at the `c`-boundary, 22-row breadth, `x.m=0` degeneracy); the **sarf symbolic-emit subsystem** (#1385 — the 369K-column `task` materialization needs a from-scratch symbolic/parametric emit MODE, since the active 398 = `taskposs∧tech` is not statically enumerable); the **fawley second-index correction** (#1111/#1112 — the qsb/pbal `sameas` gap is genuine [473→18.468 control-proven] but the fix surface is a constraint-index diagonal in the ~1400-line general emit function, and fawley's +Solve is **H-b** [non-emit MS-5 divergence → forcing]); and the **NEW max-convention bound-transfer-sign track** (the `piL_*/piU_*` warm-start transfers are gated on min-convention `.m>0`/`.m<0` and skip correctly-signed multipliers for MAXIMIZE solves — surfaced in both fawley and mine). Plus the **camcge dual-consistent Walras** (#1330 → Epic 5) and the **rocket PATH-consultation submission** (#1462 → the Sprint-38 consultation). (See `SPRINT_33/SPRINT_34_CARRYFORWARDS.md` + the per-track control docs: `DAY2_MINE_REPLAN.md`, `DAY6_SARF_ASSESSMENT.md`, `DAY4_FAWLEY_CONTROL.md`, `CAMCGE_WALRAS_DESIGN.md`, `ROCKET_CASEC_FORCING_PLAN.md`.)

**Note:** The four emit tracks (Priorities 1–4) are the core; Priority 5 combines the camcge Epic-5 work + the rocket consultation submission; Priority 6 pulls the banked failure-cohort (ganges/gangesx `$141/$145/$149`, agreste scope-verify); Priority 7 the infrastructure. The S28–33 diagnostic tooling (KKT-residual harness incl. `case_c_objdef`, presolve-divergence detector, golden-staleness gate, `--resolve-changed` checkpoint, `--force` scaffold) + the S33 P6 sample pruned-var `.l`-init fixture pattern are reused throughout. The full PATH-author consultation / quality / release work occupies the renumbered **Sprints 38–40**; rocket's finalized input (Priority 5) feeds the Sprint-38 consultation.

## Components

### Priority 1: mine #1443 — Head-Offset Dual Subsystem (~18–24h)  [Sprint-33 carryforward]
- S33 Day 2's `/tmp` control **refuted H1** (head-label multiplier re-keying): it is **value-invariant** — the `l+1`-shifted transfer (`lam_pr.l(k,l,i,j) = abs(pr.m(k,l+1,i,j))`) already stores the head-label dual at the body label, so re-keying the `stat_x` cross-term reads the same value (baseline 22 nonzero residual rows = H1's 22, row-for-row). No emit-consistent change closes the `c`-boundary: at `stat_x(3,1,1)`, x is bound-active with NLP reduced cost `x.m=0`, the cross-term is structurally correct (−16000), and closing needs +16000 that neither a keying change (banned sign flip) nor a bound multiplier (`x.m=0`) can supply. The residual is a **head-offset dual-architecture mismatch** (the head-placed precedence dual `pr.m(k,l+1)` doesn't map to the `stat_x` boundary stationarity; 22-row breadth). Design a dedicated head-offset dual subsystem: reconcile how head-placed constraint duals enter `stat_x` at the boundary (an emit reformulation on the S31 `head_domain_offsets` IR, not a keying tweak).
- **Phase 0 acceptance gate (PR24/PR27):** the reformulation must drive the warm residual `N → 0` at **all** bound-active rows AND unchanged (0) at interior rows in a `/tmp` control **before** the `src/` change; assert `modelstat` (`x.up=inf` BANNED); then presolve MS-1 @ 17500. Banked: `SPRINT_33/DAY2_MINE_REPLAN.md` + `DAY1_PROGRESS_NOTES.md` (the validated residual decomposition) + `MINE_CROSSTERM_DESIGN.md`.
- **Deliverable:** mine → **MODEL STATUS 1** (+1 Solve, +1 genuine floor if it cold-matches); #1443 closed — OR a documented deeper-architecture REPLAN.

### Priority 2: sarf #1385 — Symbolic-Emit Subsystem (~20–28h)  [Sprint-33 carryforward]
- S33 Day 6 assessed the blow-up as per-column differentiation of `task(g,t,mn,mn)`'s **369,024 columns** at three sites (S1 `acost3` scalar body-diff, S2 `enumerate_variable_instances` Cartesian, S3 variable stationarity). The active subset (`taskposs ∧ tech` = 398) is **not statically enumerable** (`taskposs` is runtime-computed from data), so the fix requires a from-scratch **symbolic/parametric emit MODE** for `task`: stop enumerating its columns, emit one guarded `stat_task(g,t,m,n)$taskposs(g,t)` (the banked 7-term derivation) + `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0`, and let GAMS instantiate the 398 live rows (head guard + `task.fx` + MCP matching). Atomic across S1/S2/S3 (no safe partial — the short-circuited constraints enumerate zero Jacobian entries, so every `stat_*` cross-term must come from the parametric path).
- **Phase 0 acceptance gate (PR20):** the re-emit must be **O(active = 398), not O(369K)** — time `sarf_mcp.gms` (target seconds, srpchase's 1-D analogue ~2.9s; the failure is >75s); verify `stat_task` against the banked 7-term derivation (grep-scan clean of set-name-literal indices); atomic landing; byte-stable golden; determinism ×3. Banked: `SPRINT_33/DAY6_SARF_ASSESSMENT.md` + `SARF_EMIT_SUBSYSTEM_DESIGN.md`.
- **Deliverable:** sarf recovers to **translate** (+1 Translate) OR a documented re-scoping if the parametric emit re-triggers the timeout; #1385 closed or re-scoped.

### Priority 3: fawley #1111/#1112 — Second-Index Correction + Forcing (~12–18h)  [Sprint-33 carryforward]
- S33 Day 4 control-confirmed the qsb/pbal `sameas` over-sum is real (`max|stat_bq|` 473 → 18.468 with `$(sameas(cfq__,cf))` added), but the fix surface is a **constraint-index diagonal** in `_add_indexed_jacobian_terms` (~1400-line general emit function, a dozen `sameas` paths) — distinct from the 1-D polygon core. Critically, fawley's +Solve is **H-b**: sameas + all bound-transfer signs fixed drives the warm residual → 0 **but the MCP still solves MS-5** (@ 4399.557, LP optimum 2899.25) — a non-emit LP divergence. Land the genuine sameas cross-term correction (a correctness fix, guarded by a fawley 2-D second-index fixture); fawley's +Solve hands to the forcing survey (the divergence is structural at fawley's scale).
- **Phase 0 acceptance gate (PR24/PR27):** the generalization must drive `max|stat_bq| → 0` (not 96%) in a `/tmp` control; `--resolve-changed --since-commit <S33-close>` GO — **no mbal-term change** and no 1-D polygon/ps2 regression (the correction is on the same 2-D path). Banked: `SPRINT_33/DAY4_FAWLEY_CONTROL.md` + `DAY5_FAWLEY_CLOSE.md` + `FAWLEY_SECOND_INDEX_DESIGN.md`.
- **Deliverable:** the genuine sameas correction ships (+1 genuine floor if fawley cold-matches) + a fawley second-index fixture; fawley's +Solve handed to forcing OR recovered if the forcing lever crosses; #1111/#1112 advanced.

### Priority 4: Max-Convention Bound-Transfer-Sign Track (~10–16h)  [NEW — Sprint-33 discovery]
- S33 Day 4 discovered the `piL_*/piU_*` warm-start transfers are gated on min-convention `.m > 0` / `.m < 0`; for a **MAXIMIZE** solve they skip correctly-signed bound multipliers — surfaced in both fawley (`bq.m < 0` at a lower bound → the residual-18.468 cell) and mine (`x.m > 0` upper-bound multipliers). A sign-robust transfer (`= abs(.m)` at the active bound) closes the warm residual. Scope the fix generally, regression-test across the MAXIMIZE-model cohort, and **check whether it is a +Solve lever** on any max model whose MCP divergence is warm-residual-driven (not structural like fawley's H-b).
- **Phase 0 acceptance gate (PR24/PR27):** a `/tmp` control confirms the sign-robust transfer closes the warm residual per model; `--resolve-changed` GO (no regression to the presolve-match cohort — the transfer only fires at active bounds). Banked: `SPRINT_33/DAY4_FAWLEY_CONTROL.md` §5.
- **Deliverable:** the sign-robust bound-transfer fix lands (a general emit-correctness improvement) + any +Solve it unlocks on the max-model cohort; OR a documented finding if it recovers no bucket.

### Priority 5: camcge Walras (Epic 5) + rocket PATH Submission (~10–16h)  [Sprint-33 carryforward]
- **camcge #1330 → Epic 5:** step 1 (the scalar-`fx` `nu_mps_fx` transfer) landed S32; step 2 (the dual-consistent Walras numéraire) reaches omega 191.7346 but MS-4 (residual Walras rank-deficiency). Prototype the full dual-consistent redefinition (keep every market-clearing row + the consumption-weighted numéraire + redefine the redundant market's dual via Walras' law) to MS-1 in a `/tmp` control (the Epic-5 gate); the S1∧S2∧S3 detector must flag only camcge. Banked: `CAMCGE_WALRAS_DESIGN.md` + `EPIC_5/CGE_DEGENERACY_SCOPING.md`.
- **rocket #1462 → the Sprint-38 consultation:** the FINALIZED PATH-consultation input is submission-ready; **submit** it (the concrete question + the ruled-out-lever survey + the reproducible case + the `--force` scaffold) to the Sprint-38 PATH-author consultation. Banked: `ROCKET_CASEC_FORCING_PLAN.md` + `SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`.
- **Deliverable:** camcge → MS-1 as an Epic-5 deliverable OR the per-model-numéraire Epic-5 finding; the rocket consultation input submitted to Sprint 39.

### Priority 6: Banked Failure-Cohort Re-Triage (~8–14h)
- **ganges/gangesx** `path_syntax_error` — a **different** root than the S33 sample fix (`$141/$145/$149` on bound-clamp `x$(not(...))=0` + parameter-assignment lines; their `.l`-init referenced vars are declared, so the S33 sample pruned-var fix doesn't touch them). Diagnose the shared translate-syntax root; a single fix may recover both. **agreste** — the CASE_B `stat_sales` rel 2.0 needs a harness scope-verify (a single-model-solved-twice scenario driver; genuine factor-of-2 dropped-gradient vs driver artifact). Each `--resolve-changed`-gated.
- **Deliverable:** ≥ 1 additional model recovered (Solve/Match/Translate) OR the cohort re-triaged with banked diagnoses.

### Priority 7 (Infrastructure): Property Fixtures + Genuine-Floor Tracking + Checkpoint (~6–10h)
- Add the AD cross-term property fixtures for the tracks that land — **shape12** (head-offset, once P1 lands) + **shape13** (sarf symbolic, once P2 lands) + a **fawley 2-D second-index** fixture (once P3 lands) — fail-before/pass-after, following the S33 P6 `test_sample_pruned_var_l_init.py` pattern. Recompute the PR25 **genuine-floor tracking** (S34 anchor **75**); refresh the `--resolve-changed` checkpoint targets; continue the Epic-4 `SUMMARY.md` groundwork (row 34).
- **Deliverable:** the property fixtures for the landed tracks; the recomputed genuine-floor tracking (anchor 75); the refreshed checkpoint list; the Epic-4-SUMMARY continuation.

### Pipeline Retest (~4h)
- Full pipeline at each checkpoint (Day 5 + Day 10) and final (Day 13) via the `--resolve-changed` checkpoint re-solve; final retest under ≥ 3 `PYTHONHASHSEED` (PR12).
- **Deliverable:** updated `gamslib_status.json` + the Sprint 33→34 metrics comparison; determinism verified; PR25 re-baseline recomputed.

## Deliverables
- mine #1443 head-offset dual subsystem — mine solves (+1 Solve) OR a documented deeper-architecture REPLAN (Priority 1)
- sarf #1385 symbolic-emit subsystem — sarf recovers to translate (+1 Translate) OR a documented re-scoping (Priority 2)
- fawley #1111/#1112 second-index correction — the genuine sameas fix ships + fixture; +Solve to forcing (H-b) OR recovered (Priority 3)
- The max-convention bound-transfer-sign fix + any +Solve it unlocks (Priority 4)
- camcge #1330 dual-consistent Walras (Epic 5) + the rocket #1462 consultation input submitted to Sprint 39 (Priority 5)
- Banked failure-cohort recoveries / diagnoses (ganges/gangesx, agreste) (Priority 6)
- Property fixtures for the landed emit paths + genuine-floor tracking (anchor 75) + checkpoint refresh + Epic-4-SUMMARY continuation (Priority 7)
- Updated pipeline metrics + Sprint 34 SPRINT_LOG.md + SPRINT_RETROSPECTIVE.md

## Acceptance Criteria
- **Solve:** ≥ 108 (maintain the S33 gain; +1 firm via any of mine [P1] / fawley-forcing [P3] / the bound-transfer track [P4] / camcge [P5-Epic5] / ganges·gangesx [P6]; **stretch ≥ 110** if two land)
- **Match:** maintain ≥ 93 as-measured; **genuine floor 75 → ≥ 76** if mine [P1] / fawley [P3] cold-match
- **Translate:** ≥ 135/142 (maintain; **+1 → 136 via #1385 sarf** if the symbolic-emit subsystem lands)
- **Parse:** ≥ 142/142 (maintain)
- **model_infeasible:** ≤ 7 (maintain; −1 per recovery)
- **path_syntax_error:** ≤ 7 (maintain; −1 per ganges/gangesx recovery)
- **Tests:** ≥ 5,035 (up from S33; the head-offset / sarf / fawley / bound-transfer regression fixtures add coverage)
- **Determinism:** byte-identical under ≥ 3 `PYTHONHASHSEED` (PR12)
- **Epic 5:** the camcge dual-consistent Walras lands to MS-1 OR is empirically scoped with the per-model-numéraire fallback; #1330 resolved or Epic-5-scoped
- **Process:** the genuine-floor ramp anchor re-baselines to **75** at S34 open; the head-offset / sarf / fawley / bound-transfer property fixtures guard the landed tracks; the rocket consultation input is submitted to the Sprint-38 PATH consultation
- **Quality:** all quality gates pass; all fixes have regression tests; emit-touching PRs pass the golden-staleness check (PR26) + the presolve-divergence detector + the `--resolve-changed` checkpoint

**Estimated Effort:** 88–130 hours over a 14-day sprint (Day 0 + Days 1–13). At ≤ 12 hours/day this fits within the 168-hour budget (14 × 12 = 168) with slack. Per-priority budgets: P1 mine head-offset dual [18–24h] + P2 sarf symbolic-emit [20–28h] + P3 fawley second-index + forcing [12–18h] + P4 bound-transfer-sign track [10–16h] + P5 camcge Epic-5 + rocket submission [10–16h] + P6 banked cohort [8–14h] + P7 infrastructure [6–10h] + pipeline retest [4h] = 88–130h work-item total. The lower bound assumes the deepest tracks (P1 head-offset dual, P2 symbolic-emit) partially slip; the upper bound assumes all land. Every carryforward inherits a **Sprint-33 control-confirmed diagnosis** (a de-risked specification, not an open question), and the S28–33 tooling is reused, so the diagnosis cost is low. Heaviest day budget: a ~11h day mid-sprint (the P1 dual-subsystem re-derivation + the P2 symbolic-emit verification).
**Risk Level:** HIGH — P1 (mine head-offset dual) and P2 (sarf symbolic-emit) are the two deepest from-scratch AD/emit workstreams, twice-carried (S32→S33→S34); Sprint 33 refuted the banked mine premise (H1 value-invariant) and Option-B-deferred the sarf rebuild, so both are genuine architectural work, not bounded changes. The decisive mitigation is that **each carries a Sprint-33 control-confirmed diagnosis** (mine's value-invariance proof + the 22-row dual-architecture characterization; sarf's three-site symbolic-emit spec; fawley's H-b finding + the sameas fix surface; the bound-transfer-sign root) — so Sprint 34 implements against specifications. Additional mitigations: (a) the KKT-residual harness Case-(a/b/c) PROCEED/REPLAN gate; (b) the PR24/PR27 control-experiment-before-implement rule (which refuted every S33 deep-track premise before any bad ship — zero broken code); (c) explicit REPLAN exits on P1 (deeper architecture), P2 (timeout re-trigger), P3 (gate-leak / H-b forcing hand-off), P5 (Epic-5 deferral). **camcge is Epic-5-scoped; the fawley +Solve is a forcing hand-off (H-b, non-emit divergence); rocket is a consultation submission (no emit fix).**

---

# Sprint 35 (Weeks 35–36): Sprint 34 Carryforward — mine Head-Offset Dual Subsystem, sarf Symbolic-Emit Subsystem, fawley Constraint-Index-Diagonal Correction, ganges/gangesx Multi-Root Recovery, camcge Walras (Epic 5) & rocket PATH Submission

**Goal:** Land the Sprint 34 REPLAN'd/deferred/banked carryforwards — each carries a **Sprint-34 control-confirmed diagnosis** (`SPRINT_34/SPRINT_RETROSPECTIVE.md` §4 + `SPRINT_34/SPRINT_35_CARRYFORWARDS.md`), not an open question. Sprint 34 was a **full modal-flat close** (0 bucket moves — Solve 108 / Match 93 / genuine floor 75 held), exactly the Task-9 projection: every deep emit track REPLAN'd/deferred after a `/tmp`/harness/compile control refuted or de-risked the premise **before any bad ship** (zero broken code), and the one `src/` landing (P4 sense-aware bound-transfer) was a general warm-start-correctness fix with no +Solve. So each track carries a precise, de-risked specification. The core: the **mine head-offset dual subsystem** (#1443 — S34 Day 1's cold-MS-1 control refuted H_dual: the head-offset dual boundary is `x.m=0`-degenerate, needing a dual-architecture rethink, not a single-site fix); the **sarf symbolic-emit subsystem** (#1385 — the 369K-column `task` materialization needs a from-scratch symbolic/parametric emit MODE, a corpus-wide re-architecture of the foundational `enumerate_variable_instances`); the **fawley constraint-index-diagonal correction** (#1111/#1112 — the qsb/pbal `sameas` gap is genuine [473→18.468 control-proven] in the ~1430-line `_add_indexed_jacobian_terms`, and fawley's +Solve is **H-b** [non-emit MS-5 divergence → forcing]); and the **ganges/gangesx multi-root recovery** (S34 Day 11 corrected the prep's single-root hypothesis — three independent roots: the `$141` `.l`-calibration NaN-cleanup [fix verified + banked], the `$145` universal-set cleanup, and the deep **`$149` CES/LES `prod()` product-rule stationarity uncontrolled-index AD bug** that gates six models; plus turkey's `$161` set-emit root). Plus the **camcge dual-consistent Walras** (#1330 → Epic 5) and the **rocket PATH-consultation submission** (#1462 → the now-Sprint-38 consultation). (See `SPRINT_34/SPRINT_35_CARRYFORWARDS.md` + the per-track control docs: `SPRINT_34/DAY1_PROGRESS_NOTES.md`, `DAY6_PROGRESS_NOTES.md`, `DAY5_PROGRESS_NOTES.md`, `DAY11_PROGRESS_NOTES.md`, `DAY10_PROGRESS_NOTES.md`.)

**Note:** The four emit tracks (Priorities 1–4) are the core; Priority 5 combines the camcge Epic-5 work + the rocket consultation submission; Priority 6 the residual failure-cohort + banked follow-ons; Priority 7 the infrastructure. The S28–34 diagnostic tooling (KKT-residual harness incl. `case_c_objdef`, presolve-divergence detector, golden-staleness gate, `--resolve-changed` checkpoint, `--force` scaffold) + the S33 P6 `test_sample_pruned_var_l_init.py` fixture pattern + the S34 P4 `test_p4_maximize_bound_transfer_sense_aware` fixture are reused throughout. The full PATH-author consultation / quality / release work occupies the renumbered **Sprints 38–40**; rocket's finalized input (Priority 5) feeds the Sprint-38 consultation. The S34 P4 max-convention bound-transfer-sign fix **shipped** (sense-aware `abs(var.m)`, no +Solve) — not a carryforward.

## Components

### Priority 1: mine #1443 — Head-Offset Dual Subsystem (~18–24h)  [Sprint-34 carryforward]
- S34 Day 1's cold-MS-1 `/tmp` control **refuted H_dual**: mine's head-offset dual boundary is **`x.m=0`-degenerate** — at the bound-active `stat_x` rows the cross-term is structurally correct and closing the residual needs a contribution that neither a keying change (banned sign flip) nor a bound multiplier (`x.m=0`) can supply. The residual is a **head-offset dual-architecture mismatch** (the head-placed precedence dual doesn't map to the `stat_x` boundary stationarity; 22-row breadth). Design a dedicated head-offset dual subsystem: reconcile how head-placed constraint duals enter `stat_x` at the boundary (an emit reformulation on the S31 `head_domain_offsets` IR, not a keying tweak).
- **Phase 0 acceptance gate (PR24/PR27):** the reformulation must drive the warm residual → 0 at **all** bound-active rows AND unchanged (0) at interior rows in a `/tmp` control **before** the `src/` change; assert `modelstat` (the `x.up=inf` measurement error stays **BANNED**); then cold/presolve MS-1. Banked: `SPRINT_34/DAY1_PROGRESS_NOTES.md` + `SPRINT_33/MINE_CROSSTERM_DESIGN.md`.
- **Deliverable:** mine → **MODEL STATUS 1** (+1 Solve, +1 genuine floor if it cold-matches); #1443 closed — OR a documented deeper-architecture REPLAN.

### Priority 2: sarf #1385 — Symbolic-Emit Subsystem (~20–28h)  [Sprint-34 carryforward]
- S34 Day 6 re-confirmed the blow-up at three sites (S1 `acost3` scalar body-diff, S2 `enumerate_variable_instances` materializing the **369,024** `task` columns, S3 per-column `stat_task`). `enumerate_variable_instances` is **foundational** (builds the `col_to_var` index the whole Jacobian→gradient→stationarity flow iterates for all 142 models), so making `task` symbolic is a **coordinated corpus-wide re-architecture** (a new parametric cross-term path), atomic across S1/S2/S3. The active subset (`taskposs ∧ tech` = 398) is not statically enumerable (`taskposs` runtime-computed) → emit one guarded `stat_task(g,t,m,n)$taskposs` + `task.fx(...)$(not (...)) = 0` and let GAMS instantiate the live rows.
- **Phase 0 acceptance gate (PR20):** the re-emit must be **O(active = 398), not O(369K)** — time `sarf_mcp.gms` (target seconds; the failure is >75s); verify `stat_task` against the banked 7-term derivation; atomic landing; byte-stable golden; determinism ×3; a full-corpus `--resolve-changed` regression harness. Banked: `SPRINT_34/DAY6_PROGRESS_NOTES.md` + `SPRINT_33/SARF_EMIT_SUBSYSTEM_DESIGN.md`.
- **Deliverable:** sarf recovers to **translate** (+1 Translate) OR a documented re-scoping if the parametric emit re-triggers the timeout; #1385 closed or re-scoped.

### Priority 3: fawley #1111/#1112 — Constraint-Index-Diagonal Correction + Forcing (~12–18h)  [Sprint-34 carryforward]
- S34 Day 5 re-confirmed the qsb/pbal `sameas` over-sum is real (`max|stat_bq|` 473 → 18.468 with `$(sameas(cfq__,cf))` added), but the fix surface is a **constraint-index diagonal** in `_add_indexed_jacobian_terms` (~1430-line general emit function, a dozen `sameas` paths, shared with mbal/cesam2/camcge/ps2). fawley's +Solve is **H-b**: sameas + all bound-transfers → warm residual ~0 **but the MCP still solves MS-5** (@ 4399.557, LP optimum 2899.25) — a non-emit divergence. Land the genuine sameas cross-term correction (a correctness fix, guarded by a fawley 2-D second-index fixture + a 2-D-cohort regression harness); fawley's +Solve hands to the forcing survey.
- **Phase 0 acceptance gate (PR24/PR27):** the generalization must drive `max|stat_bq| → 0` (not 96%) in a `/tmp` control; `--resolve-changed --since-commit <S34-close>` GO — **no mbal-term change** and no 1-D polygon/ps2 regression. Banked: `SPRINT_34/DAY5_PROGRESS_NOTES.md` + `SPRINT_33/FAWLEY_SECOND_INDEX_DESIGN.md`.
- **Deliverable:** the genuine sameas correction ships (+1 genuine floor if fawley cold-matches) + a fawley second-index fixture; fawley's +Solve handed to forcing OR recovered if the forcing lever crosses; #1111/#1112 advanced.

### Priority 4: ganges/gangesx Multi-Root Recovery (~14–20h)  [Sprint-34 carryforward]
- S34 Day 11 **corrected the prep's single-root hypothesis**: the ganges/gangesx `path_syntax_error` is **three independent roots**, and no model recovers from the `$141` fix alone. (a) **`$141`** — the Issue-#1322 NaN-cleanup self-referential guard over `.l`-calibration params (`adst=dst.l/…`), whose assignment is presolve-gated: the **fix is written + verified** (skip `.l`-attribute-referencing params in `emit_post_assignment_na_cleanup` via a `_param_assignment_references_varref_attr` helper — removes all 15 `$141`), **banked** (reverted because it recovered 0 bucket alone and its slow-emit CGE goldens are un-regenerable in the CI budget). (b) **`$145`** — a universal-set (`*`) domain NaN-cleanup gap (`series(*,years)`). (c) **`$149`** — the deep blocker: an **uncontrolled index in the stationarity emit** (ganges `stat_pc`'s CES/LES `prod(j, (pc(j)/pc00(j))**ac(j,r))` derivative w.r.t. `pc(i)` leaves a free `j`), a **deep AD-core product-rule bug** gating ganges/gangesx/dinam/indus/turkpow/clearlak. Re-apply the banked `$141` fix, add the `$145` universal-set skip, and fix the `$149` product-rule stationarity emit; the effort can afford the slow ganges/gangesx golden regen. turkey's distinct `$161` dotted-tuple set-declaration root is a separate, smaller item.
- **Phase 0 acceptance gate (PR24/PR27):** each fix `--resolve-changed`-gated; the `$149` product-rule fix verified against a hand-derived `stat_pc` cross-term in a `/tmp` control before `src/`; the slow-emit CGE goldens regenerated (nightly budget) + determinism ×3. Banked: `SPRINT_34/DAY11_PROGRESS_NOTES.md`.
- **Deliverable:** ganges/gangesx recover to model_optimal + match (+2 Solve/Match, +2 genuine floor if they cold-match; −2 path_syntax_error) OR a documented residual blocker; the `$149` product-rule AD bug fixed generally (also unblocks the `$149` half of dinam/indus/turkpow/clearlak).

### Priority 5: camcge Walras (Epic 5) + rocket PATH Submission (~10–16h)  [Sprint-34 carryforward]
- **camcge #1330 → Epic 5:** step 1 (the scalar-`fx` `nu_mps_fx` transfer) landed S32; the S1∧S2∧S3 degeneracy detector is confirmed (fires only camcge: cold MS-4 @ omega 191.7346; the four CGE siblings cold MS-1). Prototype the full dual-consistent Walras redefinition (keep every market-clearing row + the consumption-weighted numéraire + redefine the redundant market's dual via Walras' law) to MS-1 in a `/tmp` control (the Epic-5 gate); the banked price-pin variant reaches the correct primal but stays MS-4, so MS-1 is genuinely hard. Banked: `SPRINT_33/CAMCGE_WALRAS_DESIGN.md` + `EPIC_5/CGE_DEGENERACY_SCOPING.md`.
- **rocket #1462 → the Sprint-38 consultation:** the FINALIZED PATH-consultation input is submission-ready; **submit** it (the concrete question + the ruled-out-lever survey + the reproducible case + the `--force` scaffold) to the Sprint-38 PATH-author consultation. The Case-c sign flip stays **BANNED**. Banked: `SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`.
- **Deliverable:** camcge → MS-1 as an Epic-5 deliverable OR the per-model-numéraire Epic-5 finding; the rocket consultation input submitted to Sprint 39.

### Priority 6: Residual Failure-Cohort + Banked Follow-Ons (~8–14h)
- The residual `path_syntax_error` cohort per-model roots (dinam/indus `$140`+`$149`; turkpow/clearlak `$149`+`$171`; turkey `$161`) — each characterized S34 Day 11; verify per-model (the multi-root discipline). The P4 `$149` product-rule fix unblocks the `$149` half of dinam/indus/turkpow/clearlak; the residual `$140` (pruned-var `.l`-init — the S33 sample shape), `$171`, and `$161` are per-model. The Case-c family (cesam/lnts/hhfair/CGE-cluster — `case_c_objdef`, `nu_obj = ±1`, the sign flip **BANNED**) stays documented non-convex (forcing, not emit; residuals clean at the NLP point).
- **Deliverable:** ≥ 1 additional model recovered OR the residual cohort re-triaged with banked diagnoses.

### Priority 7 (Infrastructure): Property Fixtures + Genuine-Floor Tracking + Checkpoint (~6–10h)
- Add the AD cross-term property fixtures for the tracks that land — **shape12** (head-offset, once P1 lands) + **shape13** (sarf symbolic, once P2 lands) + a **fawley 2-D second-index** fixture (once P3 lands) + a **ganges recovery** raw-emit fixture (once P4 lands, following the `test_sample_pruned_var_l_init.py` skip-if-absent pattern) — fail-before/pass-after. Recompute the PR25 **genuine-floor tracking** (S35 anchor **75** → ≥ 76 if mine/fawley/ganges cold-match); refresh the `--resolve-changed` checkpoint targets; continue the Epic-4 `SUMMARY.md` groundwork (row 35).
- **Deliverable:** the property fixtures for the landed tracks; the recomputed genuine-floor tracking (anchor 75); the refreshed checkpoint list; the Epic-4-SUMMARY continuation.

### Pipeline Retest (~4h)
- Full pipeline at each checkpoint (Day 5 + Day 10) and final (Day 13) via the `--resolve-changed` checkpoint re-solve; final retest under ≥ 3 `PYTHONHASHSEED` (PR12).
- **Deliverable:** updated `gamslib_status.json` + the Sprint 34→35 metrics comparison; determinism verified; PR25 re-baseline recomputed.

## Deliverables
- mine #1443 head-offset dual subsystem — mine solves (+1 Solve) OR a documented deeper-architecture REPLAN (Priority 1)
- sarf #1385 symbolic-emit subsystem — sarf recovers to translate (+1 Translate) OR a documented re-scoping (Priority 2)
- fawley #1111/#1112 constraint-index-diagonal correction — the genuine sameas fix ships + fixture; +Solve to forcing (H-b) OR recovered (Priority 3)
- ganges/gangesx multi-root recovery — the `$141`/`$145`/`$149` fixes land (+2 Solve/Match/floor if they cold-match) + the `$149` product-rule AD bug fixed generally (Priority 4)
- camcge #1330 dual-consistent Walras (Epic 5) + the rocket #1462 consultation input submitted to Sprint 39 (Priority 5)
- Residual failure-cohort recoveries / diagnoses (Priority 6)
- Property fixtures for the landed emit paths + genuine-floor tracking (anchor 75) + checkpoint refresh + Epic-4-SUMMARY continuation (Priority 7)
- Updated pipeline metrics + Sprint 35 SPRINT_LOG.md + SPRINT_RETROSPECTIVE.md

## Acceptance Criteria
- **Solve:** ≥ 108 (maintain the S34 close; +1–4 firm via mine [P1] / fawley-forcing [P3] / ganges·gangesx [P4] / camcge [P5-Epic5]; **stretch ≥ 112** if the ganges pair + one deep track land)
- **Match:** maintain ≥ 93 as-measured; **genuine floor 75 → ≥ 76** (up to ≥ 78 if mine [P1] / fawley [P3] / ganges·gangesx [P4] cold-match)
- **Translate:** ≥ 135/142 (maintain; **+1 → 136 via #1385 sarf** if the symbolic-emit subsystem lands)
- **Parse:** ≥ 142/142 (maintain)
- **model_infeasible:** ≤ 7 (maintain; −1 per recovery)
- **path_syntax_error:** ≤ 7 (maintain; **−2 → 5 via ganges/gangesx** recovery)
- **Tests:** ≥ 5,037 (up from S34; the head-offset / sarf / fawley / ganges regression fixtures add coverage)
- **Determinism:** byte-identical under ≥ 3 `PYTHONHASHSEED` (PR12)
- **Epic 5:** the camcge dual-consistent Walras lands to MS-1 OR is empirically scoped with the per-model-numéraire fallback; #1330 resolved or Epic-5-scoped
- **Process:** the genuine-floor ramp anchor holds at **75** at S35 open; the head-offset / sarf / fawley / ganges property fixtures guard the landed tracks; the rocket consultation input is submitted to the Sprint-38 PATH consultation
- **Quality:** all quality gates pass; all fixes have regression tests; emit-touching PRs pass the golden-staleness check (PR26) + the presolve-divergence detector + the `--resolve-changed` checkpoint

**Estimated Effort:** 92–134 hours over a 14-day sprint (Day 0 + Days 1–13). At ≤ 12 hours/day this fits within the 168-hour budget (14 × 12 = 168) with slack. Per-priority budgets: P1 mine head-offset dual [18–24h] + P2 sarf symbolic-emit [20–28h] + P3 fawley constraint-index-diagonal + forcing [12–18h] + P4 ganges/gangesx multi-root recovery [14–20h] + P5 camcge Epic-5 + rocket submission [10–16h] + P6 residual cohort [8–14h] + P7 infrastructure [6–10h] + pipeline retest [4h] = 92–134h work-item total. The lower bound assumes the deepest tracks (P1 head-offset dual, P2 symbolic-emit, the P4 `$149` product-rule AD bug) partially slip; the upper bound assumes all land. Every carryforward inherits a **Sprint-34 control-confirmed diagnosis** (a de-risked specification — the P4 `$141` fix is already written + verified), and the S28–34 tooling is reused, so the diagnosis cost is low. Heaviest day budget: a ~11h day mid-sprint (the P1 dual-subsystem re-derivation + the P2 symbolic-emit verification).
**Risk Level:** HIGH — P1 (mine head-offset dual), P2 (sarf symbolic-emit), and the P4 `$149` CES/LES product-rule stationarity AD bug are deep from-scratch AD/emit workstreams; mine is thrice-carried (S32→S33→S34→S35) and sarf twice-carried, both genuine architectural work. The decisive mitigation is that **each carries a Sprint-34 control-confirmed diagnosis** (mine's `x.m=0`-degeneracy proof; sarf's three-site symbolic-emit spec; fawley's H-b finding + the sameas fix surface; ganges's three-root characterization + the already-verified `$141` fix). Additional mitigations: (a) the KKT-residual harness Case-(a/b/c) PROCEED/REPLAN gate; (b) the PR24/PR27 control-experiment-before-implement rule (which refuted or de-risked every S34 deep-track premise before any bad ship — zero broken code); (c) explicit REPLAN exits on P1 (deeper architecture), P2 (timeout re-trigger), P3 (gate-leak / H-b forcing hand-off), P4 (the `$149` AD bug depth), P5 (Epic-5 deferral). **camcge is Epic-5-scoped; the fawley +Solve is a forcing hand-off (H-b); rocket is a consultation submission (no emit fix).**

---

# Sprint 36 (Weeks 37–38): Sprint 35 Carryforward — markov Diagonal-Kronecker +1-Floor Lever, sarf Symbolic-Emit Subsystem, fawley Constraint-Index-Diagonal Correction, ganges/gangesx Multi-Root Recovery, the rocket/mine Consultation Trio, camcge Walras (Epic 5) & the GAMS-54 Re-Baseline

**Goal:** Land the Sprint 35 REPLAN'd/deferred/banked carryforwards — each carries a **Sprint-35 control-confirmed diagnosis** (`SPRINT_35/SPRINT_RETROSPECTIVE.md` §5 + `SPRINT_35/SPRINT_36_CARRYFORWARDS.md`), not an open question. Sprint 35 was a **modal-flat close** (0 bucket moves — Solve 108 / Match 93 / genuine floor 75 held; the third consecutive modal-flat), exactly the honest bimodal projection's flat branch: every deep emit track REPLAN'd/deferred/banked after a `/tmp`/harness/compile control refuted or de-risked the premise **before any bad ship** (zero broken code). The sprint's genuine discovery is the **markov diagonal-Kronecker +1-floor lever** — the strongest local upside, half-de-risked by a leak-gated landing attempt. The core: the **markov `stat_z` diagonal-Kronecker correction** (a control-confirmed `CASE_B` cold-emit bug — `max|stat_z|` rel 13.3 — that makes a `verified_convex` model a *methodology* match; the two-part fix flips it methodology→genuine, floor 75→76, fully local); the **sarf symbolic-emit subsystem** (#1385 — the 369K-column `task` materialization needs a from-scratch symbolic/parametric emit MODE, a corpus-wide re-architecture of the foundational `enumerate_variable_instances`); the **fawley constraint-index-diagonal correction** (#1111/#1112 — the qsb/pbal `sameas` gap is genuine [control-verified `max|stat_bq|` 473→1.14e-13] but the general predicate leaks onto markov #1110, needing a derivative-structure discriminator; fawley's +Solve is **H-b** → a `--force` survey); and the **ganges/gangesx multi-root recovery** (a ≥5-blocker cascade — `$141`/`$145`/`$149` fixed → `$66` cold → `rPower` presolve; the `$149` `_diff_prod` fix verified+banked). Plus the **rocket/mine consultation trio** (rocket PATH submission #1462 + mine primal-degenerate-LP question #1443), the **camcge dual-consistent Walras** (#1330 → Epic 5), the **turkey v54 testbed re-solve** (the +1 pending the licensed testbed), and the **GAMS-54 corpus re-baseline** (the v53→v54 transition's first infra task). (See `SPRINT_35/SPRINT_36_CARRYFORWARDS.md` + the per-track control docs: `DAY11_MARKOV_DIAGONAL_LEVER.md`, `DAY9_P3_FAWLEY_CONTROL_DEFER.md`, `DAY3_P4_BANK_CARRYFORWARD.md`, `SPRINT_36/CONSULTATION_BUNDLE.md`, `FOLLOWUPS_GAMS54_TRANSITION.md`.)

**Note:** The four emit tracks (Priorities 1–4) are the core; Priority 5 combines the rocket/mine consultation submissions + the camcge Epic-5 work; Priority 6 the turkey testbed re-solve + the residual multi-root cohort; Priority 7 the infrastructure (led by the GAMS-54 re-baseline). The S28–35 diagnostic tooling (KKT-residual harness incl. `case_c_objdef`, presolve-divergence detector, golden-staleness gate, `--resolve-changed` checkpoint, `--force` scaffold) + the turkey `_infer_domainless_tuple_arity` unit-test pattern are reused throughout. The full PATH-author consultation / quality / release work occupies the renumbered **Sprints 38–40**; rocket's finalized input (Priority 5) feeds the Sprint-38 consultation. The Sprint-35 markov leak-gated attempt already verified Part 1 of the fix (the diagonal split, residual 13.3→1.55) — not a from-scratch start.

## Components

### Priority 1: markov — Diagonal-Kronecker +1-Floor Lever (~14–20h)  [Sprint-35 carryforward]
- Sprint 35 Day 11 discovered + control-confirmed a **`CASE_B` cold-emit bug** in markov's `stat_z` (`kkt_residual.py` = `CASE_B`, `max|stat_z|` rel 13.3): markov is a `verified_convex` **methodology** match (presolve-rescued) because its cold emit is wrong. A correct cold emit ⇒ `CASE_A` ⇒ cold `model_optimal` ⇒ genuine match ⇒ **genuine floor 75→76 (+1)**, fully **local** (tiny model — no testbed gate). The archaeology proved the correct `#1110` split was **never emitted** (the `slow` test red from birth). The fix is **two-part**: (1) the **diagonal-Kronecker split** — the diagonal is its own single-key offset group `(0,0,999)`, so #1110's within-group split can't fire; emit the determined diagonal entry as a direct `(1 − b·pi(s,i,s,i,sp))·nu_constr(s,i)` (Part 1 is **implemented + verified**, residual 13.3→1.55); (2) the **off-diagonal `σ=sp` enumeration** — the multiplier index is an independent variable index (`σ=sp`, the var's 3rd) the offset machinery can't represent (→ 44 spurious groups), the deeper rewrite.
- **Phase 0 acceptance gate (PR24/PR27):** the fix must drive `kkt_residual.py markov` → `CASE_A` (rel < tol) — the tiny model makes each iteration cheap; leak-freedom via golden-staleness (only markov drifts; the 2-D cohort cesam2/camcge/ps2/ps3/polygon byte-identical — the fawley Day-9 leak precedent); a cold re-solve confirming `model_optimal`; the `slow` test `test_markov_stationarity_has_correction_term` flips red→green (its `slow`/`xfail` disposition decided with the fix). Banked: `SPRINT_35/DAY11_MARKOV_DIAGONAL_LEVER.md` (§6 has Part 1 implemented + the two-part spec).
- **Deliverable:** markov → cold `model_optimal` + genuine match (**+1 genuine floor, methodology→genuine**); the `#1110` multi-pattern machinery repaired (diagonal split + `σ=sp` enumeration) — OR a documented residual blocker on Part 2.

### Priority 2: sarf #1385 — Symbolic-Emit Subsystem (~20–28h)  [Sprint-35 carryforward]
- S35 carried the blow-up at three sites (S1 `acost3` scalar body-diff, S2 `enumerate_variable_instances` materializing the **369,024** `task` columns, S3 per-column `stat_task`). `enumerate_variable_instances` is **foundational** (builds the `col_to_var` index the whole Jacobian→gradient→stationarity flow iterates for all 142 models), so making `task` symbolic is a **coordinated corpus-wide re-architecture** (a new parametric cross-term path), atomic across S1/S2/S3. The active subset (`taskposs ∧ tech` = 398) is not statically enumerable (`taskposs` runtime-computed) → emit one guarded `stat_task(g,t,m,n)$taskposs` + `task.fx(...)$(not (...)) = 0` and let GAMS instantiate the live rows.
- **Phase 0 acceptance gate (PR20):** the re-emit must be **O(active = 398), not O(369K)** — time `sarf_mcp.gms` (the measured baseline is >303s and non-terminating); verify `stat_task` against the banked 7-term derivation; atomic landing; byte-stable golden; determinism ×3; a full-corpus `--resolve-changed` regression harness; no set-name-literal indices. Banked: `SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md` + `PHASE_0_ACCEPTANCE_GATES.md`.
- **Deliverable:** sarf recovers to **translate** (+1 Translate) OR a documented re-scoping if the parametric emit re-triggers the timeout; #1385 closed or re-scoped.

### Priority 3: fawley #1111/#1112 — Constraint-Index-Diagonal Correction (derivative-structure discriminator) + Forcing (~12–18h)  [Sprint-35 carryforward]
- S35 Day 9 **control-verified** the qsb/pbal `sameas` correction drives `max|stat_bq|` **473.4→1.14e-13**, but the general `src/` predicate **leaked onto markov #1110** (the shared ~1430-line `_add_indexed_jacobian_terms`) → reverted. The fix needs a **derivative-structure discriminator** (not a surface-pattern predicate) to separate fawley's constraint-index-diagonal from the #1110 multi-pattern off-diagonal. fawley's +Solve is **H-b**: the MCP solves MS-5 @ 4399.557 (LP optimum 2899.25) — a non-emit `stat_trans(tr-2)` divergence — even with `stat_bq` closed → a `--force`/continuation survey.
- **Phase 0 acceptance gate (PR24/PR27):** the discriminator drives `max|stat_bq| → 0` in a `/tmp` control; `--resolve-changed --since-commit <S35-close>` GO with golden-staleness clean — **markov #1110 + the 2-D cohort (cesam2/camcge/ps2/ps3/polygon) byte-identical**; lands with the `shape_fawley_2d_second_index` fixture. Banked: `SPRINT_35/DAY9_P3_FAWLEY_CONTROL_DEFER.md` + `FAWLEY_DIAGONAL_DESIGN.md`.
- **Deliverable:** the genuine sameas correction ships (+1 genuine floor if fawley cold-matches — H-b, so contingent) + a fawley second-index fixture; fawley's +Solve handed to the `--force` survey OR recovered if a forcing lever crosses; #1111/#1112 advanced.

### Priority 4: ganges/gangesx Multi-Root Recovery (~16–22h)  [Sprint-35 carryforward]
- S35 Day 3 found the ganges/gangesx `path_syntax_error` a **≥5-blocker cascade**: `$141`/`$145`/`$149` fixed → **`$66`** (cold — presolve-gated `.l`-calibration params `adst`/`aid`/`deltax` unassigned-but-referenced-in-stationarity) → **`rPower`** (the presolve `$onMultiR` `$include` re-runs `ganges0`, which aborts `x**y, x=0, y<0` — the embedded-NLP-diverges class; raw ganges NLP solves fine standalone MS2). The **`$149` `_diff_prod` fix** (rebind the collapsed prod-dummy → the original wrt index in the cross-index CES/LES case) is **verified + banked** (ganges `$149` 9→0; lmp2/camcge byte-identical). Re-apply it — **use the existing `_expr_contains_varref_attribute` for the `$141` helper** (the proposed `_expr_contains_varref_attr` is buggy, a PR-review catch) + the `$145` universal-set skip — and tackle `$66`/`rPower`; the effort can afford the slow ganges/gangesx CGE golden regen.
- **Phase 0 acceptance gate (PR24/PR27):** each fix `--resolve-changed`-gated; the slow-emit CGE goldens regenerated (nightly budget) + determinism ×3. Banked: `SPRINT_35/DAY3_P4_BANK_CARRYFORWARD.md` + `GANGES_RECOVERY_DESIGN.md` + `GANGES_149_PRODUCT_RULE_ANALYSIS.md`.
- **Deliverable:** ganges/gangesx recover to model_optimal + match (+2 Solve/Match, +2 genuine floor if they cold-match; −2 path_syntax_error) OR a documented residual blocker on `$66`/`rPower`; the `$149` product-rule fix (also unblocks the `$149` half of dinam/indus/turkpow/clearlak).

### Priority 5: rocket/mine Consultation Trio + camcge Walras (Epic 5) (~10–16h)  [Sprint-35 carryforward]
- **rocket #1462 → PATH consultation:** the FINALIZED, renumbered input is submission-ready; **submit** it (the concrete question + the ruled-out-lever survey + the reproducible case + the `--force` scaffold) to the PATH authors, feeding the Sprint-38 consultation. The recommended option-set plugs into `--force homotopy` (μ-continuation + `mcp_model.optfile = 1`). The Case-c sign flip stays **BANNED**. Banked: `SPRINT_36/CONSULTATION_BUNDLE.md` §1.
- **mine #1443 → primal-degenerate-LP question:** pose the primal-degenerate-LP question — *how does a warm KKT point of a primal-degenerate LP reconcile into an MCP when the degenerate boundary is not emit-reachable?* The whole keying/pairing space is **value-invariant** (S34 proved H_dual value-invariant); the only non-invariant lever is an LP-side reformulation (out of emit scope). `x.up=inf` stays **BANNED**. Banked: `SPRINT_36/CONSULTATION_BUNDLE.md` §2 + `SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md`.
- **camcge #1330 → Epic 5:** the S1∧S2∧S3 degeneracy detector fires only camcge (cold MS-4 @ omega 191.7346; the four CGE siblings cold MS-1). Prototype the full dual-consistent Walras redefinition to MS-1 in a `/tmp` control (the Epic-5 gate); the banked price-pin variant reaches the correct primal but stays MS-4. Banked: `SPRINT_35/DAY8_P5_CAMCGE_SPRINT36.md`.
- **Deliverable:** the rocket consultation submitted (feeds Sprint 39) + the mine primal-degenerate-LP question posed; camcge → MS-1 as an Epic-5 deliverable OR the per-model-numéraire Epic-5 finding.

### Priority 6: turkey Testbed Re-Solve + Residual Multi-Root Cohort (~8–12h)  [Sprint-35 carryforward]
- **turkey +1 (testbed):** the Day-6 compile-recovery is real (Checkpoint 2 + the S35-close retest confirmed turkey now reaches PATH; `path_syntax_error → path_solve_license`), blocked only by the 1000-row demo limit (turkey MCP 3,866 rows). Re-solve under a **licensed GAMS 54 testbed** to realize the +1 Solve/Match. Banked: `SPRINT_35/DAY6_P6_TURKEY_AND_TESTFIX.md`.
- **residual cohort:** turkpow (a ragged fixed-width `Table mdatat` parse bug) / clearlak (uninitialized dynamic/computed sets) / dinam / indus — heavily multi-root (6/9 root codes each); per-model dedicated efforts (the `$149` `_diff_prod` fix unblocks their `$149` half). Banked: `SPRINT_35/DAY7_P6_TURKPOW_CLEARLAK.md`.
- **Deliverable:** turkey's +1 realized on the testbed OR the testbed step re-documented; ≥ 1 residual model recovered OR the cohort re-triaged with banked diagnoses.

### Priority 7 (Infrastructure): GAMS-54 Corpus Re-Baseline + robustlp NA Fix + Property Fixtures + Genuine-Floor Tracking (~10–14h)
- **GAMS-54 corpus re-baseline (the v53→v54 transition's first infra task):** the 108/93/75 baseline + the committed DB were built under GAMS 53; CI + local now validate under 54.2.1 (the S35 Day-6 license-expiry cascade). Re-solve the corpus under 54 in the licensed testbed and diff buckets vs the v53-built DB; decide the canonical validation version (pin the DB to 54 or keep 53 where a license solves); re-check the 5 OBJ-GAP models (agreste/cesam/chain/fawley/rocket); confirm the PR19 Tier-0/1 canaries stay green under 54. Banked: `SPRINT_35/FOLLOWUPS_GAMS54_TRANSITION.md`.
- **robustlp NA coefficients:** eliminate the NA matrix coeffs GAMS 54 rejects (#1322 class) in the emit, then **de-allowlist** robustlp from `presolve_divergence_allowlist.txt`.
- **Property fixtures + tracking:** add the **markov diagonal-Kronecker** fixture (once P1 lands) + the **fawley 2-D second-index** fixture (once P3 lands), fail-before/pass-after; decide the markov `slow`-test disposition *with* the P1 fix; recompute the PR25 **genuine-floor tracking** (S36 anchor **75** → ≥ 76 if markov/fawley/ganges cold-match); refresh the `--resolve-changed` checkpoint targets; continue the Epic-4 `SUMMARY.md` groundwork (row 36).
- **Deliverable:** the GAMS-54 re-baseline decision + the DB re-solve diff; the robustlp NA fix (de-allowlisted); the property fixtures for the landed tracks; the recomputed genuine-floor tracking (anchor 75); the Epic-4-SUMMARY continuation.

### Pipeline Retest (~4h)
- Full pipeline at each checkpoint (Day 5 + Day 10) and final (Day 13) via the `--resolve-changed` checkpoint re-solve; final retest under ≥ 3 `PYTHONHASHSEED` (PR12).
- **Deliverable:** updated `gamslib_status.json` + the Sprint 35→36 metrics comparison; determinism verified; PR25 re-baseline recomputed.

## Deliverables
- markov diagonal-Kronecker correction — markov cold-matches (+1 genuine floor, methodology→genuine) OR a documented Part-2 (`σ=sp`) blocker (Priority 1)
- sarf #1385 symbolic-emit subsystem — sarf recovers to translate (+1 Translate) OR a documented re-scoping (Priority 2)
- fawley #1111/#1112 constraint-index-diagonal correction (derivative-structure discriminator) — the genuine fix ships + fixture; +Solve to the `--force` survey (H-b) (Priority 3)
- ganges/gangesx multi-root recovery — the `$141`/`$145`/`$149` fixes + `$66`/`rPower` (+2 Solve/Match/floor if they cold-match) OR a documented residual blocker (Priority 4)
- rocket #1462 consultation submitted (feeds Sprint 39) + mine #1443 primal-degenerate-LP question posed + camcge #1330 dual-consistent Walras (Epic 5) (Priority 5)
- turkey testbed +1 + residual multi-root cohort recoveries / diagnoses (Priority 6)
- GAMS-54 corpus re-baseline + robustlp NA fix + property fixtures + genuine-floor tracking (anchor 75) + Epic-4-SUMMARY continuation (Priority 7)
- Updated pipeline metrics + Sprint 36 SPRINT_LOG.md + SPRINT_RETROSPECTIVE.md

## Acceptance Criteria
- **Solve:** ≥ 108 (maintain the S35 close; +1–4 firm via markov [P1] / fawley-forcing [P3] / ganges·gangesx [P4] / turkey [P6-testbed]; **stretch ≥ 112** if the ganges pair + markov land)
- **Match:** maintain ≥ 93 as-measured; **genuine floor 75 → ≥ 76** via markov [P1] (the strongest, fully-local lever; up to ≥ 78 if fawley [P3] / ganges·gangesx [P4] also cold-match)
- **Translate:** ≥ 135/142 (maintain; **+1 → 136 via #1385 sarf** if the symbolic-emit subsystem lands)
- **Parse:** ≥ 142/142 (maintain)
- **model_infeasible:** ≤ 7 (maintain; −1 per recovery)
- **path_syntax_error:** ≤ 7 (maintain; **−2 → 5 via ganges/gangesx** recovery)
- **Tests:** ≥ 5,037 (up from S35; the markov / fawley / ganges regression fixtures add coverage)
- **Determinism:** byte-identical under ≥ 3 `PYTHONHASHSEED` (PR12)
- **GAMS-54 re-baseline:** the v53→v54 corpus re-solve diff completed + the canonical validation version decided; robustlp de-allowlisted
- **Epic 5:** the camcge dual-consistent Walras lands to MS-1 OR is empirically scoped with the per-model-numéraire fallback; #1330 resolved or Epic-5-scoped
- **Process:** the genuine-floor ramp anchor holds at **75** at S36 open; the markov / fawley / ganges property fixtures guard the landed tracks; the rocket consultation input is submitted to the Sprint-38 PATH consultation
- **Quality:** all quality gates pass; all fixes have regression tests; emit-touching PRs pass the golden-staleness check (PR26) + the presolve-divergence detector + the `--resolve-changed` checkpoint

**Estimated Effort:** 94–134 hours over a 14-day sprint (Day 0 + Days 1–13). At ≤ 12 hours/day this fits within the 168-hour budget (14 × 12 = 168) with slack. Per-priority budgets: P1 markov diagonal-Kronecker [14–20h] + P2 sarf symbolic-emit [20–28h] + P3 fawley constraint-index-diagonal + forcing [12–18h] + P4 ganges/gangesx multi-root recovery [16–22h] + P5 rocket/mine consultation + camcge Epic-5 [10–16h] + P6 turkey testbed + residual cohort [8–12h] + P7 GAMS-54 re-baseline + infrastructure [10–14h] + pipeline retest [4h] = 94–134h work-item total. The lower bound assumes the deepest tracks (the markov P1 `σ=sp` enumeration, P2 symbolic-emit, the P4 `$66`/`rPower` blockers) partially slip; the upper bound assumes all land. Every carryforward inherits a **Sprint-35 control-confirmed diagnosis** (markov's `CASE_B` + the Part-1-verified split; fawley's control + the leak finding; ganges's ≥5-blocker characterization + the verified `$149` fix), and the S28–35 tooling is reused, so the diagnosis cost is low. Heaviest day budget: a ~11h day mid-sprint (the markov P1 `σ=sp` rewrite + the P2 symbolic-emit verification).
**Risk Level:** HIGH — P1 (markov `σ=sp` off-diagonal enumeration) and P2 (sarf symbolic-emit) are deep shared-machinery / AD workstreams; the markov and fawley fixes both touch the high-blast-radius `_add_indexed_jacobian_terms` (the fawley Day-9 leak-onto-markov is the direct precedent), and sarf is thrice-carried. The decisive mitigation is that **each carries a Sprint-35 control-confirmed diagnosis** (markov's `CASE_B` + the Part-1-verified diagonal split; fawley's control + the derivative-structure-discriminator requirement; ganges's ≥5-blocker map + the verified `$149` fix; the GAMS-54 axis scoped). Additional mitigations: (a) the KKT-residual harness Case-(a/b/c) PROCEED/REPLAN gate; (b) the PR24/PR27 control-experiment-before-implement rule (which de-risked every S35 deep-track premise before any bad ship — zero broken code); (c) explicit REPLAN exits on P1 (Part-2 `σ=sp` depth / cohort leak), P2 (timeout re-trigger), P3 (gate-leak / H-b forcing hand-off), P4 (`$66`/`rPower` depth), P5 (Epic-5 deferral / consultation timeline). **camcge is Epic-5-scoped; the fawley +Solve is a forcing hand-off (H-b); rocket/mine are consultation submissions (no emit fix); turkey's +1 is testbed-gated.**

---

# Sprint 37 (Weeks 39–40): Sprint 36 Carryforward — markov σ=sp +1-Floor Lever, ganges/gangesx ≥5-Blocker Recovery, the rocket/mine/camcge Consultation & Epic-5 Cycle, fawley & sarf, turkey Testbed + GAMS-54 v54 Re-Baseline

**Goal:** Land the Sprint 36 banked/deferred carryforwards — each carries a **Sprint-36 EMPIRICALLY-REPRODUCED diagnosis** (`SPRINT_36/SPRINT_37_CARRYFORWARDS.md` + `SPRINT_36/SPRINT_RETROSPECTIVE.md` §5), a *sharper* hand-off than a prep bank: every blocker was reproduced live in-`src/`, so this sprint inherits **proven components + a single precise blocker each**, not a rewrite-from-scratch. Sprint 36 closed **FLAT** (Solve 108 / Match 93 / genuine floor 75 / Translate 135 — the projection's 75 branch; the four deep tracks all control-first-banked with zero broken code; one `src/` landing — P7 robustlp NA-guard de-allowlist). The sprint's headline lever is **markov Part-2 `σ=sp`** — the +1-floor lever whose **emission is already PROVEN in `src/`** (Mechanism C drove `CASE_B` rel 13.3 → `CASE_A` rel 2.8e-16 and the cold MCP solved to the reference **2401.577 + match**, floor 75→76) — blocked only on a **derivative-structure discriminator verified full-corpus** (the domain-only gate leaks onto cesam/ferts/sroute; the 6-model cohort proved incomplete). The core: **markov `σ=sp` discriminator** (P1, the +1-floor lever, fully local); the **ganges/gangesx ≥5-blocker recovery** (P2 — `$141`/`$145`/`$149` VERIFIED working, blocked on `$66` cold + `rPower` the #1378/#1424 embedded-NLP-divergence deep class); the **rocket/mine/camcge consultation & Epic-5 cycle** (P3); **fawley** (P4 — 0-bucket H-b, emission-path relocate + the `--force` +Solve); **sarf** (P5 — the 20–28h atomic re-arch, +1 Translate lowest-leverage); the **turkey testbed +1 + the full GAMS-54 v54 re-baseline** (P6, licensed-testbed-gated); and the **full-corpus leak-verification harness + property fixtures + genuine-floor tracking** (P7 infra, the Sprint-36 retrospective's top process lesson).

**Note:** Priority order follows `SPRINT_36/SPRINT_RETROSPECTIVE.md` §5 — **markov first** (the strongest, fully-local, emission-proven +1 lever), then ganges (+2 bimodal) and the consultation cycle; fawley/sarf are lowest-priority (0-bucket / lowest-leverage); turkey and the full v54 re-baseline are gated on a **licensed >1000-row GAMS-54 testbed** (none exists — local + CI both demo). The S28–36 tooling is reused; markov/P4/fawley inherit *proven* `src/` components (the reverted Day-2 markov prototype, the verified ganges cascade fixes in git `a8ff626c` + the `_diff_prod` §5 patch, the confirmed fawley `stat_bq` control). The **full-corpus (163-golden) leak gate is now mandatory** for every shared-`_add_indexed_jacobian_terms` change (the P1/P4 lesson).

## Components

### Priority 1: markov `σ=sp` — Derivative-Structure Discriminator +1-Floor Lever (~16–22h)  [Sprint-36 carryforward]
- **Emission PROVEN (Sprint 36 Day 2):** Mechanism C (reconciliation (a): Kronecker `nu_constr(s,i)` + `−b·sum(j, pi(s,i,sp,j,sp)·nu_constr(sp,j))`, suppressing the 45 spurious offset groups) drove markov `CASE_B` rel 13.3 → `CASE_A` rel 2.8e-16 and the **cold** MCP solved to the reference **2401.577 + match** (methodology→genuine, **floor 75→76**). The *sole* blocker: the domain-only signature gate **leaks full-corpus** (cesam/ferts/sroute) — a leak-free gate needs a **derivative-structure discriminator** that fires only on the genuine param-coupled `σ=sp` (`−b·pi(s,i,σ,τ,sp)`, a parameter coupling the constraint index to the variable's independent index) and excludes conditional-constant (sroute `1$(darc(ip,ipp))`) and variable-bilinear (cesam) derivatives.
- **Phase 0 acceptance gate (PR24/PR27) + the mandatory full-corpus leak gate:** the discriminator drives `kkt_residual.py markov` → `CASE_A` + cold `model_optimal` + match (2401.577); **`check_golden_staleness.py` full-corpus (163 goldens) shows ONLY markov drifts** — NOT the 6-model cohort (which missed all three Day-2 leaks); the fast `shape_markov_diagonal_kronecker` fixture + the sharpened `test_markov_stationarity_has_correction_term` land with the fix. `docs/issues/ISSUE_<N>_*.md` Phase-0 doc authored BEFORE the `src/` commit. Banked: `SPRINT_36/DAY2_MARKOV_OFFDIAG_CONTROL.md`, `DAY3_MARKOV_BANK.md`, `MARKOV_OFFDIAGONAL_DESIGN.md`.
- **Deliverable:** markov → cold `model_optimal` + genuine match (**+1 genuine floor, methodology→genuine, 75→76**) with the leak-free discriminator — OR a documented residual on the discriminator's generality.

### Priority 2: ganges/gangesx ≥5-Blocker Recovery (~18–24h)  [Sprint-36 carryforward]
- **Fixes VERIFIED (Sprint 36 Day 8):** `$141`/`$145` (corrected helper `_expr_contains_varref_attribute`) + `$149` (`_diff_prod` §5 patch) drive the cold compile's `$141`/`$145`/`$149` → 0 (git `a8ff626c` + `SPRINT_35/DAY3_P4_BANK_CARRYFORWARD.md` §5). Both terminals **reproduced**: `$66` ×17 (cold — presolve-gated calibration params unassigned-but-referenced in stationarity; the `ac(i+2,r)` match-correctness risk) + `rPower` (presolve — the `.l`-based power calibrations `k(i)**(-rhos(i))` re-run non-idempotently under the `$onMultiR` `$include` → `x**y, x=0, y<0` at generation; the **#1378/#1424 embedded-NLP-divergence deep class**). Recovery is **atomic** — a partial = 0 bucket + golden churn.
- **Phase 0 acceptance gate:** per-model (ganges AND gangesx) emit → compile → count `$NNN` (assert 0) → solve cold AND presolve (`modelstat` asserted) → bucket → match; each fix `--resolve-changed`-gated; the 335s slow-emit goldens on a nightly regen slot + determinism ×3. Banked: `SPRINT_36/DAY8_P4_GANGES_BANK.md`, `GANGES_RECOVERY_SEQUENCING.md`.
- **Deliverable:** ganges/gangesx recover to model_optimal + match (**+2 Solve/Match/floor**, −2 path_syntax_error) OR a documented residual on `$66`/`rPower` (the deep divergence class); the general `$149` fix also unblocks the `$149` half of dinam/indus/turkpow/clearlak.

### Priority 3: rocket/mine Consultation + camcge Walras (Epic 5) (~12–16h)  [Sprint-36 carryforward]
- **rocket #1462:** ⚠ **CORRECTED in Sprint-37 Prep Task 9 — the input was NOT submitted.** It has been "FINALIZED, ready to submit" since 2026-07-15 and slipped S33 → S34 → S35 → S36 with the bundle's one *action* checkbox still unchecked; issue #1462's only comment is the Sprint-28 bisect, and no send or reply record exists anywhere. So **no reply can have arrived**, and the first action is to **send** (scheduled S37 **Day 0**, `SPRINT_37/PLAN.md` §4). Then **integrate the PATH authors' reply** (the recommended option-set / continuation schedule plugs into `--force homotopy`); +1 Solve contingent on the send, then the reply. The Case-c sign flip stays **BANNED**. Banked: `SPRINT_36/DAY11_P5_CONSULTATION.md` §1, `CONSULTATION_BUNDLE.md` §1.
- **mine #1443:** the primal-degenerate-LP question is posed; the only non-invariant lever is an LP-side reformulation (out of emit scope). **0 bucket.** `x.up=inf` stays **BANNED**. Banked: `DAY11_P5_CONSULTATION.md` §2.
- **camcge #1330 → Epic 5:** Sprint-36 confirmed MS-4 with a **numéraire alone insufficient** (fixes the price-scaling ray, not the row-redundancy nullspace — the two-nullspaces diagnosis). Prototype the **full three-part dual-consistent Walras redefinition** (numéraire + the **Walras-law dual redefinition**, the row-redundancy fix) to MS-1 in a demo `/tmp` control (641 rows, demo-reachable); expected MS-4 → the **per-model-numéraire Epic-5 declaration** (`../EPIC_5/CGE_DEGENERACY_SCOPING.md`). Banked: `DAY11_P5_CONSULTATION.md` §3.
- **Deliverable:** the rocket reply integrated (+1 contingent) + the mine question tracked; camcge → MS-1 as an Epic-5 deliverable OR the per-model-numéraire Epic-5 finding.

### Priority 4: fawley #1111/#1112 — Constraint-Index-Diagonal (0-bucket) + Forcing (~14–18h)  [Sprint-36 carryforward]
- **Correctness confirmed (Sprint 36 Day 4):** the `stat_bq` `sameas` correction drives `max|stat_bq|` 473→1.14e-13 (hand-edit, reproduces on byte-identical goldens). But the Day-4 implementation revealed the `qsb`/`pbal` terms emit via a path **≠** the design's partial-overlap branch, and the S35 constraint-index-diagonal orientation predicate is reverted/absent → **locate the emission path + rebuild the orientation predicate + layer the discriminator + verify full-corpus** (the same full-corpus discipline as P1). fawley's +Solve is **H-b** — the Sprint-36 `--force` survey was NEGATIVE (homotopy/multistart/optfile all MS-5) → a **stronger continuation / reformulation** question for the Sprint-38 PATH consultation, not the current scaffold.
- **Phase 0 acceptance gate:** the discriminator drives `max|stat_bq| → 0`; **full-corpus golden-staleness — only fawley drifts** (markov + the 2-D cohort byte-identical); the `shape_fawley_2d_second_index` fixture lands with the fix. Banked: `SPRINT_36/DAY4_FAWLEY_DEFER.md`, `FAWLEY_DISCRIMINATOR_DESIGN.md`.
- **Deliverable:** the fawley `stat_bq` correction ships (0 bucket — H-b) + the second-index fixture; the +Solve handed to the Sprint-38 consultation; #1111/#1112 advanced.

### Priority 5: sarf #1385 — Symbolic-Emit Subsystem (~20–28h)  [Sprint-36 carryforward]
- Sprint-36 re-confirmed the blow-up non-terminating (>100s cap; O(369,024) `task` columns). A **20–28h atomic re-architecture** of the `enumerate_variable_instances` → column-index → Jacobian → gradient → stationarity flow (6 call sites, 142 models); the O(active=398) guarded emit is validated but the re-arch has **no bounded control** (the timing needs the full re-arch) and is **not landable without the full-corpus regression harness** (P7) first.
- **Phase 0 acceptance gate (PR20):** the re-emit is **O(active=398), not O(369K)** — `sarf_mcp.gms` completes in single-digit seconds; `stat_task` matches the banked 7-term derivation; atomic; byte-stable golden; determinism ×3; the full-corpus `--resolve-changed` regression harness. Banked: `SPRINT_36/DAY6_SARF_BANK.md`, `SARF_DESIGN_REFRESH.md`.
- **Deliverable:** sarf recovers to **translate** (+1 Translate → 136) OR a documented re-scoping if the parametric emit re-triggers the timeout; #1385 closed or re-scoped.

### Priority 6: turkey Testbed +1 + Full GAMS-54 v54 Re-Baseline (~10–14h)  [Sprint-36 carryforward]
- **The licence-gated cohort (10 models) — reframed 2026-08-18 (owner):** turkey is **not a special case**. **Ten models carry the identical block** — `egypt`, `ferts`, `glider`, `robot`, `shale`, `sroute`, `srpchase`, `tabora`, `tfordy`, `turkey` — **7 % of the 142 convex candidates**. All are `path_solve_license`, all `not_tested`, and **all have `solver_version: None`**: they are rejected at **generation** by the GAMS demo **1000-row nonlinear** limit, so PATH is never invoked. **All ten have committed goldens**, so the emit is verified and only the *solve* is blocked — one licence problem, not ten model problems. **Ceiling: Solve 108 → 118**, and **one licence unlocks all ten as a batch** (a single `--only-solve` pass). **Classification `licence-gated`, applied uniformly:** excluded from KPI projections (the phantom-upside failure mode turkey alone showed across S35–S37), **but not written off** — capacity is being actively pursued with Dirkse/Ferris, the same recipients as the P3 consultation, so the two conversations can be one. **A reduced instance cannot substitute** for any member: the KPI requires the model itself to solve and match. Full treatment: `docs/planning/EPIC_4/SPRINT_38/CAMCGE_EPIC5_HANDOFF.md` §4.
- **full GAMS-54 v54 re-baseline (demo-runnable):** re-solve the **142 candidates** under GAMS 54 demo (the solving set is demo-solvable — the baseline is demo-built) and diff buckets vs the v53(51.3.0) DB; re-check the 5 OBJ-GAP models (agreste/cesam/chain/fawley/rocket); produce `GAMS54_REBASELINE_DIFF.md`. **Decision: re-pin the DB to v54 only on confirmed zero bucket regressions**, else keep v53 (Sprint 36 kept v53 pending this full re-solve; P7 already restored robustlp's v54 solvability). Banked: `GAMS54_TESTBED_PLAN.md` §4.
- **residual multi-root cohort:** turkpow (ragged `Table mdatat`) / clearlak (dynamic sets) / dinam / indus — the general `$149` fix (P2) unblocks their `$149` half; per-model dedicated efforts otherwise.
- **Deliverable:** turkey's +1 realized on the testbed OR re-documented as license-gated; the full v54 re-baseline diff + the canonical-version decision; ≥1 residual model recovered OR re-triaged.

### Priority 7 (Infrastructure): Full-Corpus Leak Harness + Property Fixtures + Genuine-Floor Tracking + Phase-0 Enforcement (~12–16h)
- **Full-corpus leak-verification harness (the Sprint-36 top process lesson):** the 6-model cohort is NOT the risk set (it missed all three markov Day-2 leaks). Ship a **`check_golden_staleness.py` full-corpus (163-golden) mode as a required gate** for any `src/{ad,kkt,emit}` PR touching `_add_indexed_jacobian_terms` (a CI job + a `make` target), with the slow-emit CGE/dynamic models on a nightly budget. This is the mandatory leak gate for P1/P4.
- **Phase-0-doc enforcement:** a lint/CI check that any `src/{ad,kkt,emit}`-touching PR has a `docs/issues/ISSUE_<N>_*.md` with the `## Phase 0: Acceptance Gate` (4 `###` subsections) — the Sprint-36 P7 lesson (the robustlp doc was needed under review, not before).
- **Property fixtures + tracking:** land the `shape_markov_diagonal_kronecker` (with P1) + `shape_fawley_2d_second_index` (with P4) fixtures, fail-before/pass-after; recompute the PR25 **genuine-floor tracking** (S37 anchor 75 → ≥76 if markov lands); continue the Epic-4 `SUMMARY.md` groundwork (row 37).
- **Deliverable:** the full-corpus leak-harness gate + the Phase-0-doc CI check + the property fixtures for the landed tracks + the recomputed genuine-floor tracking + the Epic-4-SUMMARY continuation.

### Pipeline Retest (~4h)
- Full pipeline at each checkpoint (Day 5 + Day 10) and final (Day 13) via the `--resolve-changed` checkpoint re-solve; final retest under ≥ 3 `PYTHONHASHSEED` (PR12).
- **Deliverable:** updated `gamslib_status.json` + the Sprint 36→37 metrics comparison; determinism verified; PR25 re-baseline recomputed.

## Deliverables
- markov `σ=sp` derivative-structure discriminator — markov cold-matches (+1 genuine floor, methodology→genuine, 75→76) OR a documented discriminator-generality residual (Priority 1)
- ganges/gangesx ≥5-blocker recovery — the verified `$141`/`$145`/`$149` fixes + `$66`/`rPower` (+2 Solve/Match/floor if they cold-match) OR a documented residual (Priority 2)
- rocket #1462 reply integrated + mine #1443 question tracked + camcge #1330 Walras (Epic 5) (Priority 3)
- fawley #1111/#1112 constraint-index-diagonal (0-bucket, H-b) + second-index fixture; +Solve → Sprint-38 consultation (Priority 4)
- sarf #1385 symbolic-emit subsystem — sarf recovers to translate (+1 Translate) OR a documented re-scoping (Priority 5)
- turkey testbed +1 + the full GAMS-54 v54 re-baseline diff + version decision + residual cohort (Priority 6)
- full-corpus leak-harness gate + Phase-0-doc CI check + property fixtures + genuine-floor tracking (anchor 75) + Epic-4-SUMMARY continuation (Priority 7)
- Updated pipeline metrics + Sprint 37 SPRINT_LOG.md + SPRINT_RETROSPECTIVE.md

## Acceptance Criteria
- **Solve:** ≥ 108 (maintain the S36 close; +2 firm via ganges·gangesx [P2] / +1 via turkey [P6-testbed]; **stretch ≥ 111** if the ganges pair + turkey land)
- **Match:** maintain ≥ 93 as-measured; **genuine floor 75 → ≥ 76** via markov [P1] (the strongest, fully-local, emission-proven lever; up to ≥ 78 if ganges·gangesx [P2] also cold-match)
- **Translate:** ≥ 135/142 (maintain; **+1 → 136 via #1385 sarf** if the symbolic-emit subsystem lands)
- **Parse:** ≥ 142/142 (maintain)
- **model_infeasible:** ≤ 7 (maintain; −1 per recovery)
- **path_syntax_error:** ≤ 7 (maintain; **−2 → 5 via ganges/gangesx** recovery)
- **Determinism:** byte-identical under ≥ 3 `PYTHONHASHSEED` (PR12)
- **Full-corpus leak gate:** the 163-golden staleness gate is a required CI check for `_add_indexed_jacobian_terms`-touching PRs; markov [P1] and fawley [P4] both pass it (only their own model drifts)
- **GAMS-54 re-baseline:** the full v54 corpus re-solve diff completed + the canonical version decided (re-pin to v54 only on zero regressions)
- **Epic 5:** the camcge dual-consistent Walras lands to MS-1 OR is scoped with the per-model-numéraire fallback; #1330 resolved or Epic-5-scoped
- **Process:** the genuine-floor ramp anchor holds at **75** at S37 open; the Phase-0-doc CI check is enforced; every landed track has a property fixture
- **Quality:** all quality gates pass; all fixes have regression tests; emit-touching PRs pass the full-corpus golden-staleness + presolve-divergence + `--resolve-changed` checkpoint

**Estimated Effort:** 106–142 hours over a 14-day sprint (Day 0 + Days 1–13). At ≤ 12 hours/day this fits within the 168-hour budget (14 × 12 = 168) with slack. Per-priority budgets: P1 markov `σ=sp` discriminator [16–22h] + P2 ganges/gangesx recovery [18–24h] + P3 rocket/mine consultation + camcge Epic-5 [12–16h] + P4 fawley constraint-index-diagonal + forcing [14–18h] + P5 sarf symbolic-emit [20–28h] + P6 turkey testbed + full v54 re-baseline [10–14h] + P7 leak-harness + fixtures + tracking [12–16h] + pipeline retest [4h] = 106–142h work-item total. The lower bound assumes the deepest tracks (the P1 discriminator generality, the P2 `$66`/`rPower` blockers, the P5 atomic re-arch) partially slip; the upper bound assumes all land. Every carryforward inherits a **Sprint-36 empirically-reproduced diagnosis with proven components** (markov's proven emission + the full-corpus leak finding; ganges's verified cascade fixes + the reproduced `rPower`; fawley's confirmed control + the emission-path finding), so the diagnosis cost is near-zero. Heaviest day budget: a ~11h day mid-sprint (the P1 discriminator + full-corpus verify + the P5 symbolic-emit verification).
**Risk Level:** HIGH — P1 (markov `σ=sp` discriminator) and P4 (fawley) both touch the high-blast-radius shared `_add_indexed_jacobian_terms`, and P2 (ganges `rPower`) + P5 (sarf) are deep AD / re-architecture workstreams. The decisive mitigation is that **each carries a Sprint-36 empirically-reproduced diagnosis with PROVEN components** (unlike a prep bank): markov's *emission is proven* (CASE_A + cold-match 2401.577), so only the discriminator remains; ganges's `$141`/`$145`/`$149` are *verified working*, so only `$66`/`rPower` remain; fawley's `stat_bq` control is *confirmed*, so only the emission-path relocate remains. Additional mitigations: (a) the **mandatory full-corpus (163-golden) leak gate** for every shared-function change (the Sprint-36 P1/P4 lesson — the 6-model cohort missed 3 leaks); (b) the KKT-residual harness Case-(a/b/c) PROCEED/REPLAN gate; (c) the PR24/PR27 control-experiment-before-implement rule (zero broken code across S30–S36); (d) the Phase-0-doc-before-`src/` rule (P7); (e) explicit REPLAN exits on P1 (discriminator generality / cohort leak), P2 (`$66`/`rPower` depth), P4 (gate-leak / H-b forcing hand-off), P5 (timeout re-trigger), P6 (testbed license). **camcge is Epic-5-scoped; fawley's +Solve is a Sprint-38 forcing hand-off (H-b); turkey's +1 + the full v54 re-baseline are licensed-testbed-gated.**

---

# Sprint 38 (Weeks 41–42): Sprint 37 Carryforward — ganges `$149` Rebind Predicate, sarf O(active) Re-Architecture, the Consultation Ownership Decision, Presolve-Golden Coverage & the Measurement-Integrity Infrastructure

**Goal:** Land the Sprint 37 carryforwards — each carries a **Sprint-37 MEASURED disposition** (`SPRINT_37/SPRINT_38_CARRYFORWARDS.md` + `SPRINT_37/SPRINT_RETROSPECTIVE.md` §7), the sharpest hand-off yet: every deferred track was refuted or bounded by a *measurement*, not a judgement call. Sprint 37 closed with the **genuine floor advancing 75 → 76** — the first advance since Sprint 33, ending four consecutive modal-flat closes — via the markov `σ=sp` discriminator, plus a second correctness landing (fawley, 0 bucket) and four P7 infrastructure gates. **This sprint is deliberately NOT floor-targeted:** the honest position is that **no carryforward can move the floor** (ganges is 0-bucket, sarf is +1 Translate, turkey is license-gated, camcge is Epic-5), so the sprint's value is **one Translate gain, one blocked-track unblock, a coverage-asymmetry fix, and the measurement-integrity infrastructure the S37 retrospective identified as the recurring defect source**. The core: the **ganges `$149` rebind predicate re-scope** (P1 — all four cascade fixes VERIFIED working, blocked only by a `prolog` over-fire); the **sarf O(active) atomic re-architecture** (P2 — the sole viable lever, with the cheap alternative measured dead at ~5% against ~66× needed); the **consultation ownership decision** (P3 — send it or strike it, after three sprints unsent); the **36 presolve goldens** (P4 — the 153-cold/17-presolve coverage asymmetry, adopted deliberately); **camcge Epic-5 scoping + turkey testbed** (P5); the **measurement-integrity infrastructure** (P6 — the retrospective's three process recommendations, each a defect source this sprint); **Phase-0 backfill for long-open issues** (P7 — `$66`/#1289 has been un-implementable since Sprint 25); and a **general emit-backlog sweep** (P8).

**Note:** Priority order follows `SPRINT_37/SPRINT_RETROSPECTIVE.md` §7 and `SPRINT_38_CARRYFORWARDS.md` §1 — **ganges first** (the only track whose blocker is a single named predicate), then sarf (the sprint's largest single cost and only KPI mover). **P3 is a decision, not an engineering task**, and is scheduled Day 0 precisely because it has slipped three sprints on the *absence of an owner*, not on effort. **P6 is elevated above the usual infrastructure slot** because the S37 retrospective found the same failure mode — verifying a component while asserting a system property — in six separate places, two of them expensive. The S28–37 tooling is reused; ganges and sarf inherit *verified* components (the four cascade fixes; the profile + the refuted memoization). **The full-corpus (163-golden) leak gate remains mandatory** for every shared-`_add_indexed_jacobian_terms` change, and is now a required status check.

## Components

### Priority 1: ganges/gangesx — the `$149` Rebind Predicate Re-Scope (~18–24h)  [Sprint-37 carryforward]
- **Cascade VERIFIED (Sprint 37 Day 4):** all four fixes work on **both** models, run per-model and never inferred — `$141`/`$145`/`$149` go **78/3/9 → 0/0/0**, `rPower` (`FUNC DOMAIN: x**y, x=0,y<0`) is **gone**, `gams rc` **2 → 0**, EXECERROR cleared. `src/` was reverted; the tree is byte-identical to `main`.
- **The sole blocker is one predicate:** the **`$149` rebind drifts `prolog`**, a live `model_optimal` + match model, so the full-corpus leak gate refuses the cascade. Reverting *only* `$149` (keeping `$141`/`$145` + the `rPower` gate) returns `rc=2` with 9 × `$149` — **`$149` is load-bearing and there is no leak-free subset.** Re-scope the **rebind predicate**, not the fix: **#1668** records two directions — rebind parameter indices consistently, or restrict the trigger to a genuinely-free `prod` bound (**direction 2 is closer to the original intent**).
- **Bucket is 0 — the prep-era "+2 or 0" was refuted on Sprint 37 Days 4–5.** The **6th blocker** (embedded `ganges0` **MS-5 Locally Infeasible @ −386785.5017** against raw standalone **MS-2 @ 6395.5444**, matching the banked figure to the decimal) is untouched and `mcp_model` stays **MS-4**. A fully clean cascade buys `path_syntax_error → model_infeasible` — a **lateral** move (pse 6 → 4, **mi 7 → 9**). **Solve stays 108, Match stays 94.** A genuine +2 additionally requires the #1378/#1424 embedded-NLP-divergence class, **not scoped here**.
- **Phase 0 acceptance gate:** per-model (ganges AND gangesx) emit → compile → count `$NNN` (assert 0) → solve cold AND presolve (`modelstat` asserted) → bucket; **`make check-goldens` full-corpus shows ONLY ganges/gangesx drift — `prolog` byte-identical** (the gate that refused Sprint 37); the 335s slow-emit goldens on a nightly regen slot + determinism ×3. Banked: `SPRINT_37/DAY4_GANGES_CONTROL.md`, `ISSUE_1667`, GitHub #1667/#1668.
- **Deliverable:** the cascade lands leak-free (ganges/gangesx `path_syntax_error → model_infeasible`, **0 bucket, −2 pse / +2 mi**) OR a documented residual on the rebind predicate; the general `$149` fix also unblocks the `$149` half of dinam/indus/turkpow/clearlak.

### Priority 2: sarf #1385 — the O(active) Atomic Re-Architecture (~20–28h)  [Sprint-37 carryforward]
- **The profile relocated the bottleneck (Sprint 37 Day 7):** the banked design blamed "369K columns"; the measurement says **the columns are cheap and differentiating each one is not**. `compute_constraint_jacobian` is **137 s of a 180 s cap**, with ~**762 K** top-level `differentiate_expr` calls against the **398** columns that matter (`_diff_sum` 104.5 s, `_is_concrete_instance_of` 59.0 s, `simplify` 49.7 s).
- **The cheap fix is measured dead — do NOT re-attempt it.** Memoizing `resolve_set_members` inside `_is_concrete_instance_of` (5.8 M invocations) worked exactly as intended — `resolve_set_members` left the top-14, `_is_concrete_instance_of` 59.0 → 39.7 s — and bought **~5 % throughput** (761,897 → 802,108 differentiations). sarf needs `>330 s → single-digit seconds` ≈ **66×**; the **927×** ratio between declared (369,024) and active (398) columns is the only headroom. Recorded in `ISSUE_1385`.
- **Atomic by construction:** the 2-D constraint gate + the S1/S2/S3 short-circuit + the parametric `stat_task` + `task.fx` land as **one unit** — a partial landing leaves multipliers with no stationarity coupling, i.e. an inconsistent MCP, and is explicitly a REPLAN rather than progress. Three sites re-located on current `main`: **S1 `constraint_jacobian.py:78`**, **S2 `index_mapping.py:634`**, **S3 `stationarity.py`**, plus **six** corpus-safety call sites that must be provably unperturbed.
- **Two gate peculiarities (do not rediscover):** sarf has **no golden**, so `make leak-check MODEL=sarf` reports `NO-OP` and fails for a non-correctness reason — the real gate is **`make check-goldens` (zero drift ×163) plus sarf newly producing a golden (163 → 164)**. And **sarf cannot be its own fixture**, because at 369,024 columns the fail-before state does not terminate.
- **Phase 0 acceptance gate (PR20) — timing threshold REVISED 2026-08-18 (owner decision):** the re-emit is **O(active=398), not O(369K)** — `sarf_mcp.gms` **completes and produces a byte-stable golden, wall-clock ≤ 300 s on a nightly slot** (**revised from "single-digit seconds"**: Prep Task 5 measured the O(active) projection at **~141 s** — 1,183 rows × 398 cols at 3,343 diff/s — so the original threshold was unreachable without also gating the 1,183 rows, scope not in the 20–28 h estimate. The KPI is **+1 Translate**, which requires only that sarf *complete*); `stat_task` matches the banked 7-term derivation with **symbolic** multiplier indices (`grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` empty); byte-stable golden; determinism ×3. Banked: `SPRINT_37/DAY6_FAWLEY_LANDING.md` §1–4 (Day 7 sections), `ISSUE_1385`, `SARF_REARCH_REFRESH.md`.
- **Deliverable:** sarf recovers to **translate** (**+1 Translate → 136**, the sprint's only KPI mover) OR a documented re-scoping if the parametric emit re-triggers the timeout; #1385 closed or re-scoped.

### Priority 3: The Consultation Ownership Decision — Send It or Strike It (~4–6h)  [Sprint-37 carryforward; **Day 0**]
- **Not an engineering task, and that is the point.** The rocket/mine consultation bundle has been **FINALIZED since 2026-07-15** and has now slipped **S33 → S34 → S35 → S36 → S37** with its one *action* checkbox unchecked. Sprint 37 Day 0 established why it is not executable by an execution agent: **the bundle names no recipient, address, or channel.**
- **The decision, scheduled Day 0:** a **human names a recipient and channel and the bundle is sent**, OR the item is **struck from the plan** and rocket's +1 is reclassified as unreachable-without-consultation. Carrying it a fourth time without an owner converts a task into a permanent fixture and quietly inflates every sprint's projected upside.
- **What it would buy if sent:** rocket **+1 Solve contingent** on a recommended option-set / continuation schedule. **fawley's +Solve is the same class** — the Sprint-36 `--force` survey was NEGATIVE (homotopy/multistart/optfile all leave MS-5), so it needs a stronger continuation or reformulation, i.e. the same consultation. **mine is 0 bucket** (the only non-invariant lever is an LP-side reformulation, out of emit scope); `x.up=inf` stays **BANNED**.
- **Deliverable:** the consultation **sent with a named recipient and a tracking record**, OR a written strike decision reclassifying rocket/fawley's +Solve as consultation-gated and removing it from sprint projections; `../SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` closed out either way.

### Priority 4: The 36 Presolve Goldens — Close the Coverage Asymmetry (~10–14h)  [Sprint-37 carryforward]
- **The asymmetry:** the golden corpus is **153 cold vs 17 presolve**, so the presolve emit path is far less covered than the cold path — while `model_optimal_presolve` accounts for **29 of the 94 matches**.
- **The 36 exist already.** Sprint 37 Day 9's full re-solve regenerated them (17 → 53); they were swept into a commit by `git add -A`, caught in review, and **removed**. They are plausibly the *fix* for the asymmetry.
- **Adopt them deliberately, never as a solve-run side effect.** Generating references and committing them in one unreviewed step would expand what `check-goldens` sweeps (170 → 206) using references produced by that very run — **a self-certifying reference set, which is how a gate stops being a gate.** Each of the 36 must be reviewed against its model's expected presolve emit before adoption, and the leak-gate runtime impact re-measured (the sweep is already the sprint's slowest gate at 3 workers).
- **Phase 0 acceptance gate:** each adopted golden is byte-stable + deterministic ×3; `make check-goldens` passes at the new scope with **0 timeouts**; `--min-scope` is raised from 170 to the new in-scope count so a silent narrowing still fails loudly.
- **Deliverable:** the 36 presolve goldens adopted with per-model review (**scope 163 → ~199**) + `--min-scope` raised + the runtime re-measured, OR a documented subset with the exclusions justified.

### Priority 5: camcge Epic-5 Scoping + the Licence-Gated Cohort (~10–14h)  [Sprint-37 carryforward]
- **camcge #1330 → Epic 5:** Sprint 37 Day 10's `/tmp` control under GAMS 54.2.1 **reproduced every predicted figure** — emit 19 s, **641 single equations / 641 variables**, embedded NLP **MS-2 @ omega 191.7346**, `mcp_model` **MS-4 Infeasible**. The MCP is MS-4 against a *correct* NLP optimum: structural Walras rank-deficiency, **not an emit defect**. The three-part dual-consistent Walras redefinition has been refuted across 3+ sprints (price-pin → MS-4, single-dual-pin → MS-4, drop-row → corrupt @ omega 299) and **must not be re-run here**; the **drop-row half remains BANNED** (primal-correct, breaks the MCP dual). Produce the **Epic-5 handoff**: the per-model-numéraire declaration + the two-nullspaces diagnosis in `../EPIC_5/CGE_DEGENERACY_SCOPING.md`, so Epic 5 starts from the refutations rather than repeating them.
- **turkey +1 (licensed testbed):** the `$161` compile-recovery landed S35 and Day 9 corrected its stale row to `path_solve_license`. The MCP is **3,866 rows** against the GAMS **demo 1000-row nonlinear limit** — local solve-verification is impossible. Procure a licensed environment and re-solve; **+1 Solve / +1 Match if it converges**, otherwise re-document as license-gated.
- **residual multi-root cohort:** turkpow (ragged `Table mdatat`) / clearlak (dynamic sets) / dinam / indus — P1's general `$149` fix unblocks their `$149` half; per-model dedicated efforts otherwise.
- **Deliverable:** the camcge Epic-5 handoff (refutations + per-model-numéraire fallback, #1330 Epic-5-scoped) + the **10-model licence-gated cohort** classified uniformly, excluded from projections with its **+10 Solve ceiling** recorded + ≥1 residual model re-triaged.

### Priority 6 (Infrastructure): Measurement Integrity — the S37 Retrospective's Three Recurring Defects (~14–18h)
- **6a. Derive figures at execution time; stop quoting them** (retrospective §3 / rec 1). Sprint 37's Day-8 prompt sweep corrected 6 stale figures and was **re-staled by Day 9's own re-baseline within 24 hours**; the defect then recurred *inside the closeout*, twice (the S36-close partition written as the mid-sprint 64/29, and the refuted "+2 or 0" carried into `SPRINT_LOG.md` §7). Convert the day-prompt and sprint-doc templates from **quoted figures to derived ones** — a `scripts/sprint_audit/` helper that emits the current KPI block on demand — and require any figure that *must* be quoted to **carry the commit it was measured at**.
- **6b. Assert every gate's SCOPE, not just its verdict** (retrospective §2 / rec 2). A check that silently narrows passes while the property is false — a **false-negative generator, worse than no check**. `--min-scope N` asserted on *discovery* is the working template. Two known narrowing modes remain unguarded: **`--resolve-changed` selects by git diff** (uncommitted goldens are invisible — this produced a false GO in Sprint 37), and **`make leak-check MODEL=<id>` reports `NO-OP`** for a model with no golden (which is how sarf's gate fails for a non-correctness reason). Give both an asserted scope and a non-zero exit on an empty selection.
- **6c. Floor provenance must travel with the floor** (retrospective §4 / rec 3). A mechanical `Match − (presolve ∧ match)` count yields **65** against the recorded **76**, because the *"cold emit byte-identical to pre-fix"* qualifier lives only in the hand-partition. Ship a **provenance-carrying floor tracker** — a per-model partition file with the reason each model counts — so the figure is reproducible rather than hand-maintained, and so any future automation cannot silently emit 65 and look authoritative.
- **6d. Re-anchor the DB checkpoint.** `--resolve-changed --since-commit 78ceaead` has anchored on the S34 close since Sprint 34, but **the DB changed in Sprint 37** (Day 3 markov, Day 9 v54). Re-anchor to the **S37 close** so the checkpoint measures this sprint's drift rather than four sprints of accumulated intent.
- **Deliverable:** the derived-figure helper + the two gate-scope assertions + the provenance-carrying floor tracker + the re-anchored checkpoint, each with a test that fails before and passes after.

### Priority 7: Phase-0 Backfill for Long-Open Issues (~8–10h)
- **`$66` is Issue #1289, open since Sprint 25 with NO `## Phase 0: Acceptance Gate` section** — so it was **never implementable** under CONTRIBUTING §392–447, cascade or not. Sprint 37 authored a gate for it on Day 5; sarf's #1385 had the same gap. Both were discovered only when a sprint tried to *budget* them.
- **Sweep the open backlog for the same defect** now that `check_phase0_doc.py` exists: any issue a future sprint might schedule needs its Phase-0 section **before** it is budgeted, not during. Report the count and backfill the top candidates.
- **Deliverable:** a Phase-0 compliance report over the open backlog + backfilled gates for the top candidates; `$66`/#1289 confirmed implementable or explicitly closed as out-of-scope.

### Priority 8: General Emit-Backlog Sweep (~12–16h)
- With no floor-moving lever scoped (see Goal), use the remaining budget on the **adjacent general-emit backlog** rather than inflating the deep tracks: the `$149`-half unblocks from P1 (dinam/indus/turkpow/clearlak), the residual `path_solve_terminated` cohort, and any `model_infeasible` model whose root cause is a *bounded* emit defect rather than a structural one.
- **Selection rule (pre-registered, to prevent scope drift):** a model enters this sweep only if it has a **reproduced fingerprint** and a **named fix surface**; anything requiring a new diagnosis is banked, not started. This is the S30–S37 control-first discipline applied to the backlog.
- **Deliverable:** ≥2 backlog models recovered or re-triaged with reproduced fingerprints; any new deep class banked with a bounded next step.

### Pipeline Retest (~4h)
- Full pipeline at each checkpoint (Day 5 + Day 10) and final (Day 13) via the `--resolve-changed` checkpoint re-solve (**re-anchored per P6d**); final retest under ≥ 3 `PYTHONHASHSEED` (PR12).
- **Deliverable:** updated `gamslib_status.json` + the Sprint 37→38 metrics comparison; determinism verified; the PR25 genuine-floor partition recomputed **from the provenance file** (P6c).

## Deliverables
- ganges/gangesx `$149` rebind-predicate re-scope — the cascade lands leak-free (0 bucket, −2 path_syntax_error / +2 model_infeasible) OR a documented residual (Priority 1)
- sarf #1385 O(active) atomic re-architecture — sarf recovers to translate (**+1 Translate → 136**) OR a documented re-scoping (Priority 2)
- The consultation **sent with a named recipient**, OR a written strike decision removing rocket/fawley's +Solve from sprint projections (Priority 3)
- The 36 presolve goldens adopted with per-model review (scope 163 → ~199) + `--min-scope` raised + runtime re-measured (Priority 4)
- camcge Epic-5 handoff (refutations + per-model numéraire, #1330 scoped) + the **10-model licence-gated cohort** uniformly classified, +10 Solve ceiling recorded (Priority 5)
- Measurement-integrity infrastructure: derived-figure helper + two gate-scope assertions + provenance-carrying floor tracker + re-anchored DB checkpoint (Priority 6)
- Phase-0 compliance report over the open backlog + backfilled gates; `$66`/#1289 resolved either way (Priority 7)
- ≥2 emit-backlog models recovered or re-triaged with reproduced fingerprints (Priority 8)
- Updated pipeline metrics + Sprint 38 SPRINT_LOG.md + SPRINT_RETROSPECTIVE.md + **SPRINT_39_CARRYFORWARDS.md**

## Acceptance Criteria
- **Solve:** ≥ 108 (maintain the S37 close; **no carryforward is scoped to raise it** — the **10-model licence-gated cohort** [P5] needs licence capacity and rocket's +1 is consultation-gated [P3]. The cohort's **+10 ceiling (108 → 118) is explicitly NOT a Sprint-38 projection**; it becomes reachable only when a larger licence exists)
- **Match:** ≥ 94 (maintain the S37 close as-measured)
- **Genuine floor:** **maintain ≥ 73** — **re-baselined 2026-08-18 (owner decision): the baseline is 73, not 76.** Prep Tasks 2–3 established that the floor's provenance credits **three `non_convex`, out-of-corpus models** (`ps2_f_s`/`ps2_s`/`ps3_s_gic`), so the in-corpus figure is **76 − 3 = 73**; the S31–S37 series was overstated by 3. Explicitly **not** a growth target this sprint; ganges is 0-bucket, and any advance would come from an unbudgeted P8 lever. The figure must be recomputed **from the provenance file** (P6c, `baseline.count = 73`), never a mechanical DB count. **P6c owns re-baselining the downstream reports** (KPI column, footnote ⁸, `SUMMARY.md` row 37)
- **Translate:** ≥ 135/142 (**+1 → 136 via #1385 sarf** if the O(active) re-arch lands — the sprint's only KPI mover)
- **Parse:** ≥ 142/142 (maintain)
- **model_infeasible:** ≤ 7, **or ≤ 9 if the ganges cascade lands** — an increase here is a **lateral move from path_syntax_error, not a regression**, and must be reported as such
- **path_syntax_error:** ≤ 6 (**−2 → 4 via the ganges cascade**)
- **Determinism:** byte-identical under ≥ 3 `PYTHONHASHSEED` (PR12)
- **Leak gate:** `make check-goldens` clean at the **new** scope (~199 after P4) with 0 timeouts; ganges/gangesx [P1] pass it with `prolog` byte-identical
- **Consultation:** **sent with a named recipient, or struck** — "carried forward" is not an acceptable outcome for a fourth sprint (P3)
- **Measurement integrity:** the two gate-scope assertions fail loudly on an empty/narrowed selection; the floor is reproducible from the provenance file; the DB checkpoint is re-anchored to the S37 close
- **Epic 5:** the camcge handoff records the refuted variants so Epic 5 does not repeat them; #1330 Epic-5-scoped
- **Quality:** all quality gates pass; all fixes have regression tests; emit-touching PRs carry a Phase-0 doc **before** the `src/` commit and pass the full-corpus golden-staleness + `--resolve-changed` checkpoint

**Estimated Effort:** 100–134 hours over a 14-day sprint (Day 0 + Days 1–13). At ≤ 12 hours/day this fits within the 168-hour budget (14 × 12 = 168) with substantial slack. Per-priority budgets: P1 ganges rebind predicate [18–24h] + P2 sarf O(active) re-arch [20–28h] + P3 consultation ownership decision [4–6h] + P4 presolve-golden adoption [10–14h] + P5 camcge Epic-5 + turkey testbed [10–14h] + P6 measurement-integrity infrastructure [14–18h] + P7 Phase-0 backfill [8–10h] + P8 emit-backlog sweep [12–16h] + pipeline retest [4h] = 100–134h work-item total. The lower bound assumes P2's atomic re-arch slips (its REPLAN is explicit and cheap) and P8 is trimmed; the upper bound assumes all land. **P8 is the deliberate schedule filler** — with no floor lever available it absorbs slack without inflating the deep tracks, and its pre-registered selection rule prevents it becoming an open-ended diagnosis sprint. Heaviest day budget: a ~11h day mid-sprint (the P2 atomic re-arch verification + the P4 golden review). Both deep tracks inherit **measured** dispositions (ganges's verified cascade + named predicate; sarf's profile + refuted memoization), so diagnosis cost is near-zero.

**Risk Level:** MEDIUM-HIGH — lower than Sprint 37 despite comparable scope, because **no track needs a new diagnosis** and **the sprint is not floor-targeted**, removing the pressure that produced Sprint 36's reverted landing attempt. P2 (sarf) is the dominant risk: a 20–28h atomic re-architecture across three materialization sites and six call sites, where a partial landing is an inconsistent MCP rather than partial progress — its REPLAN exit is therefore explicit and must be taken early rather than nursed. P1 (ganges) touches the shared rebind path that already drifted `prolog` once. P4 changes what the leak gate sweeps, which is the gate the other priorities depend on — it is scheduled *after* P1's gate run for that reason. Mitigations: (a) the **mandatory full-corpus (163→~199-golden) leak gate**, now a required status check; (b) the KKT-residual harness PROCEED/REPLAN gate; (c) the PR24/PR27 control-experiment-before-implement rule (**zero broken code across S30–S37**); (d) the Phase-0-doc-before-`src/` CI gate (P7 extends its coverage to the backlog); (e) explicit REPLAN exits on P1 (predicate leak), P2 (timeout re-trigger / atomicity), P4 (runtime or review burden), P5 (testbed license). **camcge is Epic-5-scoped; rocket/fawley's +Solve is consultation-gated and must not be counted in projections until P3 resolves; turkey's +1 is licensed-testbed-gated.**

---
# Sprint 39 (Weeks 43–44): PATH Author Consultation & Solution Forcing

**Goal:** Prepare and submit PATH author consultation document. Implement solution forcing strategies. Address remaining solve and translate failures across all pipeline stages.

**Note:** Case studies from Sprint 22; consultation submission now in Sprint 39. The rocket PATH-consultation input finalized S32 and submitted from the Sprint-37 carryforward sprint feeds this consultation; the deep emit carryforwards (markov diagonal-Kronecker, sarf symbolic-emit, fawley constraint-index-diagonal, ganges/gangesx multi-root, camcge Walras / Epic 5) are addressed first in the new **Sprint 37** and its **Sprint 38** carryforward — see the inserted sections above.

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
  - Target: translate rate ≥ 95% of parsed models (matches Sprint 39 Acceptance Criteria below; Sprint 40 steps up to ≥ 97%)
  - **Deliverable:** Final translation fixes

- **Final Solve Fixes (2h)**
  - Address any remaining solvable `path_syntax_error` or `path_solve_terminated` models
  - Apply solution forcing strategies to divergent models
  - Target: solve rate ≥ 81% of translated models, stretch ≥ 82% (matches Sprint 39 Acceptance Criteria below; a modest +1pp bump on Sprint 31's ≥ 81% baseline if forcing strategies recover 1–2 divergent models)
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
- **Parse Rate:** ≥ 100% of pipeline scope (maintain from Sprint 31)
- **Translate Rate:** ≥ 95% of parsed models (maintain from Sprint 31; the step-up to ≥ 97% happens in Sprint 40 per Rolling KPIs)
- **Solve Rate:** ≥ 81% of translated models (maintain Sprint 31's ≥ 81% baseline; modest stretch to ≥ 82% via forcing strategies recovering 1–2 divergent models; Sprint 40 / Sprint 41 continue the ramp to ≥ 83% / ≥ 85% per Rolling KPIs)
- **Full Pipeline Match:** ≥ 45% of pipeline scope — **legacy inherited target, superseded:** this predates the Sprint-28 presolve-retry methodology lift; **Sprint 30 Priority 8** re-baselined the Rolling-KPIs Match targets (now the S39–S41 columns) to the ≥ 64% line (footnote ⁸, Sprint 30 Day 12 / 2026-07-08), so this ≥ 45% figure is superseded by that ≥ 64% target
- **Quality:** All tests pass; all fixes have regression tests

**Estimated Effort:** 22-28 hours
**Risk Level:** MEDIUM (PATH author response timeline is uncertain; solution forcing may have limited effectiveness for some model classes)

---

# Sprint 40 (Weeks 45–46): Quality, Performance & PATH Feedback Integration

**Goal:** Stabilize performance benchmarks. Incorporate any PATH author feedback. Final comprehensive pipeline run. Begin documentation finalization.

**Note:** PATH consultation submitted in Sprint 39; feedback integration now in Sprint 40.

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
- **Deliverable:** Updated metrics; expected full pipeline match ≥ 48% (matches Sprint 40 Acceptance Criteria below; up from Sprint 39's ≥ 45%)

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
- **Final Translate Rate:** ≥ 97% of parsed models (up from Sprint 39's ≥ 95%)
- **Final Solve Rate:** ≥ 83% of translated models (up from Sprint 39's ≥ 81%)
- **Full Pipeline Match:** ≥ 48% of pipeline scope (up from Sprint 39's ≥ 45%)
- **Documentation:** Remaining failures documented; Epic 4 summary drafted
- **Quality:** All quality gates pass

**Estimated Effort:** 22-30 hours
**Risk Level:** LOW-MEDIUM (mostly consolidation; PATH feedback timing uncertain)

---

# Sprint 41 (Weeks 47–48): v2.0.0 Release & Epic 5 Planning

**Goal:** Complete Epic 4 with v2.0.0 release. Finalize all documentation. Plan Epic 5 based on remaining failures and new opportunities.

**Note:** Performance benchmarks and PATH feedback integration completed in Sprint 40; Sprint 41 focuses on release and forward planning.

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
  - Review REMAINING_FAILURES.md from Sprint 40
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
  - Outline Sprint 42-45 high-level scope
  - **Deliverable:** Draft Epic 5 PROJECT_PLAN.md

### Sprint Retrospective (~2h)
- **Epic 4 Retrospective (2h)**
  - Document what worked well across Sprints 18-40
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
- **Final Parse Rate:** ≥ 100% of pipeline scope (confirmed from Sprint 40)
- **Final Translate Rate:** ≥ 97% of parsed models (confirmed from Sprint 40)
- **Final Solve Rate:** ≥ 85% of translated models (up from Sprint 40's ≥ 83%)
- **Full Pipeline Match:** ≥ 52% of pipeline scope (up from Sprint 40's ≥ 48%)
- **Epic 5 Ready:** Draft project plan created; backlog prioritized
- **Quality:** All quality gates pass on final release

**Estimated Effort:** 22-28 hours
**Risk Level:** LOW (release mechanics and documentation; Epic 5 planning is exploratory)

---

## Rolling KPIs & Tracking

### Sprint-Level KPIs

| Metric | S18 | S19 | S20 | S21 (actual) | S22 (actual) | S23 (actual) | S24 (actual) | S25 (actual) | S26 (actual) | S27 | S28 | S29 | S30 | S31 | S32 | S33 | S34 | S35 | S36 | S37 | S38 | S39 | S40 | S41 |
|--------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----| ----- |-----|-----|-----|
| Valid Corpus Defined | ✓ | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| lexer_invalid_char | ~95 | <50 | 10 | **3** | **4** | **0**³ | **0** | **0** | **0** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| internal_error (parse) | ~23 | <15 | 7 | **0** | **0** | **0** | **0** | **0** | **0** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| path_syntax_error | ≤2 | ≤2 | 48 | **41** | **20** | **23** | **11**⁴ | **12**⁶ | **17**⁷ | ≤6 (−11 via #1398 + #1381 + carryforward) | maintain ≤8 | maintain ≤8 | maintain ≤8 | maintain ≤8 | maintain ≤8 | maintain ≤8 | maintain ≤7 | maintain ≤7 (stretch ≤5 via ganges/gangesx) | maintain ≤7 (stretch ≤5 via ganges/gangesx) | maintain ≤7 (stretch ≤5 via ganges/gangesx) | maintain ≤6 (−2 → 4 via the ganges cascade — those 2 move to model_infeasible, a lateral move) | ≤6 | ≤5 | maintain ≤5 |
| path_solve_terminated | 11 | 11 | 29 | **12** (29/29 classified) | **10** | **12** | **10** | **5** | **5** | maintain ≤5 | maintain ≤5 | maintain ≤5 | maintain ≤5 | maintain ≤5 | maintain ≤5 | maintain ≤5 | maintain ≤5 | maintain ≤5 | maintain ≤5 | maintain ≤5 | maintain ≤5 | maintain ≤5 | ≤4 | ≤3 |
| model_infeasible | 0 | 0 | 12 | **15** | **12**² | **11** | **8**⁵ | **4** | **4** | ≤3 | ≤5 | ≤5 | ≤5 | ≤5 | ≤5 (stretch ≤3 via mine + camcge) | ≤7 (maintain; −1 per mine + camcge + fawley) | ≤7 (maintain) | ≤7 (maintain; −1 per recovery) | ≤7 (maintain; −1 per recovery) | ≤7 (maintain; −1 per recovery) | ≤7 (maintain; **+2 → 9 if the ganges cascade lands** — lateral from path_syntax_error, NOT a regression) | ≤4 | ≤3 | maintain ≤3 |
| Parse Rate (pipeline scope) | ~41% | ≥55% | 82.5% | **98.1%** (154/157) | **97.5%** (156/160) | **100.0%** (147/147)³ | **100.0%** (143/143)⁴ | **100.0%** (142/142)⁶ | **100.0%** (142/142)⁷ | ≥100% | ≥100% | ≥100% | ≥100% | ≥100% | ≥100% | ≥100% | ≥100% | ≥100% | ≥100% | ≥100% | ≥100% | ≥100% | ≥100% | ≥100% |
| Translate Rate (of parsed) | ~69% | ~72% | 90.9% | **89.0%** (137/154) | **90.4%** (141/156) | **95.2%** (140/147) | **94.4%** (135/143)⁴ | **93.7%** (133/142)⁶ | **94.4%** (134/142)⁷ | ≥95% (+1 via #1385) | ≥95% | ≥95% | maintain ≥95% (stretch +1 via #1385) | maintain ≥95% (stretch +1 via #1385) | maintain ≥95% (stretch +1 via #1385 sarf) | maintain ≥95% (stretch +1→96% via #1385 sarf) | maintain ≥95% (stretch +1→96% via #1385 sarf) | maintain ≥95% (stretch +1→96% via #1385 sarf) | maintain ≥95% (stretch +1→96% via #1385 sarf) | maintain ≥95% (stretch +1→96% via #1385 sarf) | maintain ≥95% (stretch +1→96% via #1385 sarf O(active) re-arch) | maintain ≥95% (stretch ≥96% via forcing) | ≥97% | ≥97% |
| Solve Rate (of translated) | ≥52% | ≥52% | 27.5% | **47.4%** (65/137) | **63.1%** (89/141) | **61.4%** (86/140) | **73.3%** (99/135) | **78.2%** (104/133) | **76.9%** (103/134)⁷ | ≥82% | ≥81% | ≥81% | ≥81% (stretch +2 via mine + rocket) | ≥81% (stretch +2 via mine + camcge) | ≥81% (stretch +2 via mine + camcge) | ≥81% (stretch +2 via mine + fawley + camcge) | maintain ≥81% (stretch +1 via mine/fawley-forcing/bound-transfer) | maintain ≥81% (stretch +1–4 via mine/fawley-forcing/ganges/camcge) | maintain ≥81% (stretch +1–4 via markov/fawley/ganges/turkey) | maintain ≥81% (stretch +1–4 via markov/fawley/ganges/turkey) | maintain ≥81% (stretch +1 via turkey on a licensed testbed) | maintain ≥81% (stretch ≥82% via forcing) | ≥83% | ≥85% |
| Full Pipeline Match (pipeline scope) | ~14% | ≥20% | 10.0% | **19.1%** (30/157) | **29.4%** (47/160) | **33.3%** (49/147)³ | **37.8%** (54/143)⁴ | **42.3%** (60/142)⁶ | **41.5%** (59/142)⁷ | ≥46% | ≥45% | ≥64%⁸ | ≥64%⁸ (genuine floor 69→**70 actual**) | ≥64%⁸ (genuine floor 70→≥73) | ≥64%⁸ (genuine floor 74→≥75; **74 actual**) | ≥64%⁸ ᴿ (genuine floor 74→≥75) | ≥64%⁸ ᴿ (genuine floor 75→≥76) | ≥64%⁸ ᴿ (genuine floor 75→**75 actual**) | ≥64%⁸ ᴿ (genuine floor 75→**75 actual**; markov emission proven+banked, P7 robustlp shipped) | ≥64%⁸ ᴿ (genuine floor 75→**76 actual** via markov `σ=sp`) | ≥64%⁸ ᴿ (genuine floor **maintain ≥73** — **re-baselined from 76 on 2026-08-18**, the provenance credited 3 out-of-corpus `non_convex` models; no emit lever is scoped to move it — ganges is 0-bucket) | ≥64%⁸ ᴿ (genuine floor maintain ≥73 — re-baselined 2026-08-18) | ≥64%⁸ ᴿ (genuine floor →≥74 — re-baselined 2026-08-18) | ≥64%⁸ ᴿ (genuine floor →≥75 — re-baselined 2026-08-18) |

² Sprint 22 `model_infeasible` is 15 total; 12 in-scope after excluding 3 permanently infeasible models (feasopt1, iobalance, orani). A 4th model (meanvar) was declared excluded on Day 7 but later achieved model_optimal, so only 3 remain in the infeasible count. S23–S41 targets are in-scope counts.

³ Sprint 23 pipeline scope changed from 160 to 147 models (13 MIP/other models excluded). Parse and match percentages are relative to the 147-run scope, so excluded models are not counted in that denominator. The `lexer_invalid_char` count dropping to 0 in Sprint 23 primarily reflects parse fixes on models that remained in scope, rather than all lexer failures being removed by scope exclusion.

⁴ Sprint 24 pipeline scope narrowed from 147 to 143 models via schema v2.2.1 exclusions (2 multi-solve driver scripts `decomp`/`danwolfe` excluded by the validator gate introduced in PR #1265, plus 2 others moved out of the in-scope convex-continuous set). S24 metrics are reported on the 143-scope. The S24 `path_syntax_error` value of 11 is from the Day 13 Addendum re-retest under doubled pipeline timeouts (PR #1274 bumped translate 300s→600s / solve 60s→120s / compile-check 30s→60s); the pre-bump Day 13 retest saw 6 path_syntax_error, but the doubled-timeout re-retest translated 5 previously-timing-out models whose MCPs all hit path_syntax_error at PATH compile, yielding a net 1:1 influx. Translate = 135/143 is the post-bump value; pre-bump was 130/143.

⁵ Sprint 24 `model_infeasible` baseline was 14 (triage-scope count from PLAN.md; the narrower 147-pipeline-scope baseline was 11). Δ = −6 net (6 gross fixes: cesam2, qabel, abel, stdcge, lrgcge, moncge recovered; 0 gross influx).

⁶ Sprint 25 pipeline scope narrowed from 143 to 142 models via a runtime convexity reclassification of one model (visible by the Day 11 retest). Per `BASELINE_METRICS.md` §5 this is treated as a runtime filter rather than a scope edit (similar to the multi-solve gate handling of `danwolfe`/`decomp`); identifying the specific model is a Sprint 26 prep item (see Sprint 25 retrospective PR18). The S25 `path_syntax_error` value of 12 is bucket churn — 3 baseline syntax-error models resolved (mathopt4, saras, ferts) and 4 added: 3 transfers from `path_solve_terminated`/`model_infeasible` (camcge, cesam2, fawley) where Sprint 25 unblocked their translates and surfaced fresh PATH compile errors, plus 1 regression from solving (otpop, baseline `solve_success` → `path_syntax_error`). The S25 Translate Rate of 93.7% (133/142) is −2 net vs S24: the Day 12 #1270 multi-solve gate moved saras from `path_syntax_error` to `translate_internal_error` (intentional, same net failure status), plus the 1-model scope shift. S25 Match Rate of 42.3% includes 3 newly-matching models from previously-failing buckets (gtm, korcge, robustlp) and 3 from previously-mismatching. Error-influx accounting (PR10 re-calibrated): alias-AD 0% (within 30% budget), emitter recovery 71% / 5 influx ÷ 7 fixes (within 80–100% budget). 4/8 acceptance criteria reached STRETCH; 1 GO miss on Translate (−2); 1 NO-GO on `path_syntax_error` (+1, bucket churn). 6/8 criteria met overall (Parse, Solve, Match, path_solve_terminated, model_infeasible, Tests).

⁷ Sprint 26 pipeline scope unchanged at 142 (verified Sprint 26 prep Task 2 — abel reclassification carries forward, no new scope movement). The S26 Translate Rate of 94.4% (134/142) is **+1 net vs S25 final** (133 → 134) — srpchase recovered translation under Day 13's faster runner (274.2s per `gamslib_status.json` `translate_time_seconds` vs Sprint 25's 846s under SIGALRM 900s profile); 3 additional Day 0 machine-variance churn-out models (clearlak, ganges, turkpow) also returned to translating successfully and cascaded to path_syntax_error per Sprint 25 final state. The S26 `path_syntax_error` value of 17 (Day 0 9 → Day 13 17, +8) is **bucket churn + Phase A regressions** (the two contributions overlap on turkpow): 3 machine-variance translate churn-backs (clearlak / ganges / turkpow returning from Day 0 translate_timeout to Sprint 25's path_syntax_error baseline) + 1 chronic srpchase translate recovery (Day 13 faster runner unblocked srpchase's chronic Sprint 25 translate_timeout at 274.2s; surfaces path_syntax_error post-translate) — **turkpow's translate-recovery surfaced an additional Phase A `stat_zt(m,v,b,t)` syntax regression on top of its pre-Sprint-26 syntax error**, so it has mixed metric-bucket attribution; 4 Phase A gate side-effects driving the bucket transition (qdemo7 [compare_match → path_syntax_error] + egypt + ferts + shale [path_solve_license → path_syntax_error] — `i↔j` swap on Sums whose body multipliers were already correctly alias-indexed, filed as Sprint 27 #1398). The widened #1398 affected-models known-bug surface (15 models per PR #1399 review) is broader than the 4 models that drove a metric-bucket transition. The S26 Solve Rate of 76.9% (103/134) is **−1 net vs S25 final** (104 → 103, qdemo7 regression). The S26 Match Rate of 41.5% (59/142) is **−1 net** (qdemo7 same root cause). model_infeasible held at 4 (third consecutive sprint with zero gross influx — S24 / S25 / S26). Sprint 26 absorbed **4 close-and-refile architectural reclassifications + 1 in-place carryforward** without sprint cancellation: Phase B → Sprint 27 #1381 (Day 3), Priority 4 Option 1 short-circuit → #1385 (Day 4), Priority 3 kand → #1390 (Day 7), Priority 5 #1334 → #1393 + #1335 in-place reopen (Day 9). Plus PR19 pre-merge solve-time validation CI extension shipped Day 11 (PR #1396). Error-influx accounting (PR10): alias-AD 400% / 4 influx ÷ 1 fix (Phase A consolidated launch emit, PR #1379) — above 30% budget. The 3 machine-variance translate churn-backs (clearlak / ganges / turkpow) are runner-speed effects reverting to the Sprint 25 baseline state, not Sprint 26 fixes. Widened #1398 known-bug surface is 15 models (1500% if measured against the widened surface). Same failure-mode shape PR19 was designed to prevent, just at a broader emit-affected surface than PR19's initial target list (canaries + Pattern C targets); PR19 target-list widening is a Sprint 27 follow-up. **5/8 acceptance criteria met (1 STRETCH on Translate; Parse + path_solve_terminated + model_infeasible + Tests are the other 4 met); 3 MISS with mixed attribution — Solve −1 and Match −1 both single-root-caused by Phase A gate side-effect (qdemo7 regression, #1398); path_syntax_error +8 is partially #1398 (4 Phase A side-effects) PLUS 4 translate recoveries (3 machine-variance churn-backs + srpchase chronic recovery) cascading from translate_timeout to path_syntax_error.** New process recommendations from Sprint 26 retrospective: PR20 (Phase 0 acceptance gate — hand-derived KKT before src/ implementation), PR21 (prep-task end-to-end emit verification), PR22 (Day-0 / mid-sprint script auto-generating the Day 12 PR14 review list), PR23 (CI-workflow PR self-review checklist).

⁸ The new Sprint 29 Full Pipeline Match target (≥64%) is **re-baselined** on the Sprint 28 Day-13 retest actual (92/142 = 64.8%), which the Day-9 presolve-retry-on-cold-mismatch broadening (`_cold_objective_mismatches_nlp`) lifted well above the pre-Sprint-28 ≥45% target line — a methodology lift, not a genuine-gain lift (only +7 of the +30 Match are cross-term fixes; see `SPRINT_28/SPRINT_RETROSPECTIVE.md` §"What We'd Do Differently" #5). The renumbered S39–S41 Full Pipeline Match targets (≥45% / ≥48% / ≥52%) were **inherited from the pre-methodology-lift baseline and stale**. **ᴿ RE-BASELINED (Sprint 30 Day 12, 2026-07-08 — the Priority-8 PR25 re-baseline):** the S31–S41 as-measured Full Pipeline Match targets are now the **≥64% line** (maintain the Sprint-28 methodology-lifted floor), and the **genuine-floor count** (per PR25, the cold/cross-term matches excluding the presolve-retry methodology) is the real ramp: **S30 actual 70** (robert +1; the polygon/hhfair/Class-B genuine-floor gains REPLAN'd to the new Sprint 31) → **S31 ≥73** (the Sprint-30-carryforward sprint lands them) → **S32 actual 74** (the Sprint-31-carryforward sprint's mine + camcge genuine-floor movers all REPLAN'd; a flat-KPI close) → **S33 actual 75** (the Sprint-32-carryforward sprint landed +1 via the P6 sample pruned-var `.l`-init fix — Solve 108 / Match 93 / genuine floor 75) → **S34 actual 75** (the Sprint-33-carryforward sprint's mine/fawley genuine-floor movers all REPLAN'd/deferred — a full modal-flat close, ≥76 missed; the one `src/` landing [P4 sense-aware bound-transfer] is warm-start-only → 0 floor) → **S35 actual 75** (the Sprint-34-carryforward sprint's mine/fawley/ganges genuine-floor movers all REPLAN'd/deferred/banked — the third consecutive modal-flat close, ≥76 missed; turkey's +1 is testbed-gated, and the markov diagonal-Kronecker +1 lever was discovered but banked) → **S36 actual 75** (the Sprint-35-carryforward sprint closed FLAT — markov's emission proven in-`src/` [Mechanism C: `CASE_A` + cold-match 2401.577] but banked as a dedicated full-corpus derivative-structure-discriminator effort [the domain-only gate leaks onto cesam/ferts/sroute]; fawley/sarf/ganges all control-first-banked; one `src/` landing [P7 robustlp NA-guard de-allowlist — a v54-robustness win, not a bucket] — the **fourth consecutive modal-flat** close, ≥76 missed) → **S37 actual 76** (the Sprint-36-carryforward sprint **LANDED the ≥76 step** via the markov `σ=sp` derivative-structure discriminator — the first genuine-floor advance since S33, ending four consecutive modal-flat closes; ganges did **not** cold-match and was re-scoped to 0-bucket) → **S38 maintain ≥73** (the Sprint-37-carryforward sprint scopes **no emit lever that can move the floor** — ganges is 0-bucket [lateral `path_syntax_error → model_infeasible`], sarf is +1 Translate, turkey is license-gated, and camcge is Epic-5; the floor moves only if the P8 backlog sweep surfaces an unbudgeted lever) → S39 maintain ≥73 → S40 ≥74 → **S41 ≥75** as the deeper follow-ons settle. **⚠ The forward targets S38–S41 were re-baselined down by 3 on 2026-08-18** (owner decision): the floor's provenance credited three `non_convex`, out-of-corpus models, so the in-corpus figure is 76 − 3 = **73**. **The S31–S37 *actuals* in this footnote and in the table above are NOT yet restated** — P6c owns that, together with `SUMMARY.md` row 37 and the provenance tracker that will enforce the figure. **⚠ The genuine floor cannot be derived from the DB** — a mechanical `Match − (presolve ∧ match)` count yields **65** against the recorded **76**, because the *"cold emit byte-identical to pre-fix"* qualifier lives only in the hand-partition (S37 Day-9 finding); any floor-tracking automation must carry per-model provenance. The ≥52%/≥48%/≥45% figures are superseded. The Sprint 30 Full Pipeline Match target (≥64%) already sat on the re-baselined line.

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
| Stacked blockers in models | HIGH | HIGH | 20-36 | Track blockers removed, not just models unblocked |
| MCP-NLP solution divergence | HIGH | MEDIUM | 25-38 | PATH author consultation; multiple forcing strategies |
| PATH author availability | MEDIUM | MEDIUM | 38-39 | Self-contained case studies; batch questions; literature fallback |
| Diminishing returns on parse | MEDIUM | MEDIUM | 22-37 | Subcategorize before implementing; preprocessing fallback |
| IndexOffset complexity | MEDIUM | MEDIUM | 20-21, 26-36 | Design first (S20), implement second (S21); spike validates feasibility; S26 #1224 ParamRef IndexOffset deferred until architectural extension scoped; S27 Priority 6 lands the translate; S28 Priority 1 lands the parameter-valued-offset KKT cross-term; S29 Priority 1 diagnoses the head-domain-offset MCP (#1443 mine, REPLAN'd multi-site); S30 Priority 1 REPLAN'd the head-domain-offset architecture (found it needs foundational IR plumbing); S31 Priority 1 plumbed the head-offset detail through the IR + landed the Site-2 dual-transfer helper (IR foundation on `main`) but REPLAN'd mine — a residual 4th bound-complementarity site (`stat_x` at bound-active rows); S32 Priority 1 targeted that 4th site but REPLAN'd — the control showed the bound-multiplier `N`-derivation closes `stat_x` by construction yet yields a wrong-sign residual at 6 bound-active rows; **S33 Priority 1 targets the head-offset bound-active cross-term architecture (the 5th coupling, mine +1 Solve)** |
| Infeasible MCP formulations | MEDIUM | LOW-MEDIUM | 24-38 | PATH consultation; document as inherent limitations |
| Alias-AD architectural drift | HIGH | HIGH | 24-36 | Day 5 hypothesis-validation methodology (PR16) applied PRE-Sprint-0 from S26 onward; pre-merge solve-time validation (PR19) for emit-affecting changes; **PR20 Phase 0 acceptance gate (hand-derived KKT before src/ implementation) added in S27** after S26 carryforward identified 4 reclassifications + 1 in-place hand-derived-KKT-review catch; **S28 added the KKT-residual harness + golden-staleness + presolve-divergence guards**, reused in S29–S30 (S30 adds head-offset + offset-alias property-test fixtures; **S31 lands the #1111/#1112 general-alias core [polygon] + enables the head-offset/offset-alias property fixtures**) |

---

## Dependencies & Prerequisites

### External Dependencies
- GAMS software installed locally (with valid license)
- PATH solver available (version 5.2+)
- Internet access for GAMS team communication
- PATH author availability (Michael Ferris, Steven Dirkse) — needed by Sprint 39

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
- Sprint 29 depends on Sprint 28 (the Sprint 28 Solve/Match carryforwards filed in the S28 retrospective — #1443 mine, #1462 rocket, #1385, cold-convex robustness, #1330 camcge — plus the S28 diagnostic tooling: KKT-residual harness, presolve-divergence detector, golden-staleness gate)
- Sprint 30 depends on Sprint 29 (the Sprint 29 REPLAN'd Solve/Match carryforwards — #1443 head-domain-offset architecture [mine + robert], #1462 rocket non-convex forcing, #1236 hhfair widened-VARIABLE, #1385 cross-terms, #1111/#1112 offset-alias, camcge #1330 Epic-5 transformation — plus the S29 diagnostic tooling: KKT-residual harness, presolve-divergence detector, golden-staleness gate, `--resolve-changed` checkpoint re-solve)
- Sprint 31 depends on Sprint 30 (the Sprint 30 REPLAN'd Solve/Match carryforwards — #1443 mine head-offset IR plumbing, #1111/#1112 offset-alias general-alias core [polygon], camcge #1330 dual-consistent Walras, #1385 sarf symbolic-emit, the cold-convex obj-grad residue, #1462 rocket forcing — plus the S28–30 diagnostic tooling + the `--force` scaffold)
- Sprint 32 depends on Sprint 31 (the Sprint 31 REPLAN'd Solve/Match carryforwards — #1443 mine head-offset 4th bound-complementarity site [IR foundation on main], #1385 sarf 4-D `task`-var stationarity gate, camcge #1330 → Epic 5 dual-consistent Walras / CASE_B `stat_mps`, #1462 rocket PATH-consultation forcing, #1236 hhfair + CGE cluster documented Case-c — plus the S28–31 diagnostic tooling + the `--force` scaffold)
- Sprint 33 depends on Sprint 32 (the Sprint 32 REPLAN'd Solve/Match carryforwards, each control-confirmed — #1443 mine head-offset bound-active cross-term architecture [the 6-bound-active-row wrong-sign `N` diagnosis], #1385 sarf symbolic parametric `stat_task` emit subsystem [the 369K-column `acost3`+variable-path enumeration], fawley #1111/#1112 second-index generalization [`max|stat_bq|` 473→18], camcge #1330 → Epic 5 dual-consistent Walras numéraire [omega 191.7346 but MS-4], #1462 rocket PATH-consultation input finalized + #1236 hhfair/CGE documented Case-c — plus the S28–32 diagnostic tooling incl. the new `case_c_objdef` classifier + the `--force` scaffold)
- Sprint 34 depends on Sprint 33 (the Sprint 33 REPLAN'd/deferred carryforwards, each control-confirmed — mine head-offset dual [H1 value-invariant], sarf symbolic-emit subsystem, fawley sameas + the max-convention bound-transfer track, camcge Walras → Epic 5, the rocket PATH-consultation input — plus the S28–33 diagnostic tooling + the S33 P6 sample `.l`-init fixture pattern)
- Sprint 35 depends on Sprint 34 (the Sprint 34 REPLAN'd/deferred/banked carryforwards, each control-confirmed — mine head-offset dual [H_dual refuted, `x.m=0`-degenerate], sarf symbolic-emit subsystem, fawley constraint-index-diagonal sameas correction, ganges/gangesx multi-root recovery [the verified-and-banked `$141` fix + the deep `$149` CES/LES product-rule AD bug], camcge Walras → Epic 5, the rocket PATH-consultation input — plus the S28–34 diagnostic tooling + the S33 P6 `.l`-init fixture pattern + the S34 P4 bound-transfer fixture)
- Sprint 36 depends on Sprint 35 (the Sprint 35 REPLAN'd/deferred/banked carryforwards, each control-confirmed — the markov diagonal-Kronecker +1-floor lever [Part-1 diagonal split verified, residual 13.3→1.55], sarf symbolic-emit subsystem, fawley constraint-index-diagonal [control-verified 473→1.14e-13, needs a derivative-structure discriminator], ganges/gangesx ≥5-blocker recovery [the verified-and-banked `$149` `_diff_prod` fix], the rocket/mine consultation trio, camcge Walras → Epic 5, the turkey testbed +1, the GAMS-54 re-baseline — plus the S28–35 diagnostic tooling + the turkey `_infer_domainless_tuple_arity` unit-test pattern)
- Sprint 37 depends on Sprint 36 (the Sprint 36 banked/deferred carryforwards, each empirically-reproduced with proven `src/` components — markov's proven emission [`CASE_A` + cold-match 2401.577] + the full-corpus leak finding, the verified `$141`/`$145`/`$149` ganges cascade fixes, the confirmed fawley `stat_bq` control, the sarf/consultation/testbed banks — plus the S28–36 diagnostic tooling + the mandatory full-corpus [163-golden] leak-verification harness)
- Sprint 38 depends on Sprint 37 (the Sprint 37 carryforwards, each with a MEASURED disposition — the VERIFIED ganges cascade blocked on the single `$149` rebind predicate [#1668], sarf's profile + the refuted ~5% memoization [#1385], the unsent consultation bundle, the 36 regenerated presolve goldens, and the camcge/turkey banks — plus the S28–37 diagnostic tooling and the four S37 P7 gates [required golden-staleness + `--min-scope`, the Phase-0 CI gate, the 3-worker leak gate, per-row `gams_version`])
- Sprint 39 depends on Sprint 22 (case studies feed consultation document) and Sprint 38 (the consultation ownership decision — P3 either sends the bundle or strikes it; the finalized rocket input was submitted from S38 + carryforward stabilization + the solution-forcing scaffold establish the baseline for PATH consultation work)
- Sprint 40 depends on Sprint 39 (PATH feedback integration, performance benchmarks)
- Sprint 41 depends on Sprint 40 (release preparation based on final metrics)

---

## Changelog

- **2026-08-13:** Inserted new **Sprint 38** (Weeks 41–42): Sprint 37 Carryforward — ganges `$149` Rebind Predicate, sarf O(active) Re-Architecture, the Consultation Ownership Decision, Presolve-Golden Coverage & the Measurement-Integrity Infrastructure. Based on `SPRINT_37/SPRINT_RETROSPECTIVE.md` §7 ("Recommendations for Sprint 38") + `SPRINT_37/SPRINT_38_CARRYFORWARDS.md` (Sprint 37 closed with the **genuine floor advancing 75 → 76** — the first advance since S33, ending four consecutive modal-flat closes — via the markov `σ=sp` discriminator [P1] plus the fawley constraint-index-diagonal landing [P4, 0 bucket] and four P7 infrastructure gates; final Solve 108 / Match 94 [65 cold + 29 presolve] / floor 76 / Translate 135 / mi 7 / pse 6 / all-219 97, corpus re-pinned to GAMS 54.2.1): P1 the ganges `$149` rebind-predicate re-scope [all four cascade fixes VERIFIED working; blocked solely by a `prolog` over-fire; **0 bucket** — the prep-era "+2 or 0" was refuted on S37 Days 4–5, since the 6th blocker leaves a clean cascade a lateral `path_syntax_error → model_infeasible` move], P2 sarf #1385 O(active) atomic re-architecture [the profile relocated the bottleneck to per-column differentiation — 137s of a 180s cap — and the cheap memoization was measured dead at ~5% against ~66× needed; **+1 Translate, the sprint's only KPI mover**], P3 the consultation ownership decision [**send it or strike it** — finalized since 2026-07-15 and unsent across S33–S37 because the bundle names no recipient; not an engineering task], P4 the 36 presolve goldens [the 153-cold/17-presolve coverage asymmetry, adopted deliberately with per-model review — scope 163 → ~199], P5 camcge Epic-5 handoff + turkey licensed-testbed re-solve, P6 the **measurement-integrity infrastructure** [the retrospective's three recurring defects: derive figures at execution time; assert every gate's SCOPE not just its verdict; floor provenance must travel with the floor — plus re-anchoring the DB checkpoint off the four-sprint-old `78ceaead`], P7 Phase-0 backfill over the open backlog [`$66`/#1289 has been un-implementable since S25 for want of a Phase-0 section], P8 a general emit-backlog sweep with a pre-registered selection rule. **Deliberately NOT floor-targeted** — no carryforward can move the floor, and saying so prevents the pressure that produced Sprint 36's reverted landing attempt. 14-day sprint at ≤12h/day = 168h cap; estimated effort 100–134h. Cascaded existing sprints forward: old S38 (PATH Author Consultation & Solution Forcing) → new **S39** (Weeks 43–44); old S39 (Quality+Performance+PATH Feedback Integration) → new **S40** (Weeks 45–46); old S40 (v2.0.0 Release + Epic 5 Planning) → new **S41** (Weeks 47–48). Inserted a new **S38** Rolling-KPIs column (maintain-the-S37-line targets, with `model_infeasible` explicitly allowed to rise to ≤9 as a **lateral** ganges move rather than a regression) + relabelled the old S38/S39/S40 columns S39/S40/S41, and annotated the **S37** Full Pipeline Match cell with its actual (**76**). Updated the pre-entry body cross-references (all `Sprint 38`/`Sprint 39`/`Sprint 40` in the S18–S37 bodies → `Sprint 39`/`Sprint 40`/`Sprint 41`), the Epic-5 outline scope (`Sprint 40-43` → `Sprint 42-45`, which the token shift would otherwise have collided with the renumbered release sprint), the Epic-4 retrospective span (`Sprints 18-39` → `Sprints 18-40`), the risk-table PATH-author window (37-38 → 38-39), the Sprint-to-Sprint Dependencies (**new** `Sprint 38 depends on Sprint 37`; `S39 depends on 22+37` → `22+38`), and footnote ⁸ (the genuine-floor ramp: **S37 actual 76** — the ≥76 step LANDED → **S38 maintain ≥76** [no emit lever scoped to move it] → S39 maintain ≥76 → S40 ≥77 → S41 ≥78, plus the standing warning that the floor **cannot be derived from the DB**: a mechanical count yields 65 against the recorded 76). The `## Changelog` history entries were left frozen.
- **2026-08-09:** Inserted new **Sprint 37** (Weeks 39–40): Sprint 36 Carryforward — markov `σ=sp` +1-Floor Lever, ganges/gangesx ≥5-Blocker Recovery, the rocket/mine/camcge Consultation & Epic-5 Cycle, fawley & sarf, turkey Testbed + GAMS-54 v54 Re-Baseline. Based on `SPRINT_36/SPRINT_RETROSPECTIVE.md` §5 + `SPRINT_36/SPRINT_37_CARRYFORWARDS.md` (Sprint 36 closed **FLAT, 0 bucket moves** — Solve 108 / Match 93 / genuine floor 75 / Translate 135, the **fourth consecutive** modal-flat; the four deep tracks all control-first-banked with PROVEN components, one `src/` landing [P7 robustlp NA-guard de-allowlist — a v54-robustness win, not a bucket]): P1 markov `σ=sp` derivative-structure discriminator [the +1-floor lever; **emission PROVEN** in-`src/` — `CASE_A` + cold-match 2401.577 — blocked only on a **full-corpus-verified** discriminator, the 6-model cohort missed the cesam/ferts/sroute leaks], P2 ganges/gangesx ≥5-blocker recovery [`$141`/`$145`/`$149` VERIFIED working; `$66` cold + `rPower` the #1378/#1424 embedded-NLP-divergence deep class], P3 the rocket #1462 reply + mine #1443 question + camcge #1330 Walras → Epic 5 [MS-4, numéraire-insufficient], P4 fawley #1111/#1112 [correctness confirmed; emission-path relocate + the `--force` survey NEGATIVE → 0 bucket], P5 sarf #1385 symbolic-emit [20–28h atomic re-arch], P6 turkey testbed +1 + the full GAMS-54 v54 re-baseline [licensed-testbed-gated], P7 the **full-corpus (163-golden) leak-verification harness** [the S36 top process lesson] + Phase-0-doc CI enforcement + property fixtures + genuine-floor tracking. 14-day sprint at ≤12h/day = 168h cap; estimated effort 106–142h. Cascaded existing sprints forward: old S37 (PATH Author Consultation & Solution Forcing) → new **S39** (Weeks 41–42); old S39 (Quality+Performance+PATH Feedback Integration) → new **S40** (Weeks 43–44); old S40 (v2.0.0 Release + Epic 5 Planning) → new **S41** (Weeks 45–46). Inserted a new **S37** Rolling-KPIs column (carryforward targets continuing S36's markov floor 75→≥76 line) + relabelled the old S37/S39/S40 columns S39/S40/S41 + a new S41 column, and annotated the **S36** Full Pipeline Match cell with its actual (**75**; markov emission proven+banked, P7 robustlp shipped). Updated the pre-entry body cross-references (all `Sprint 37`/`Sprints 37–39`/`Sprint-37 consultation` in the S18–S36 bodies → `Sprint 39`/`Sprints 38–40`/`Sprint-38`), the risk-table sprint-range references (Stacked blockers 20-35→20-36, MCP-NLP divergence 25-37→25-38, PATH author availability 36-37→37-38, Diminishing returns 22-36→22-37, IndexOffset 26-35→26-36, Infeasible MCP 24-37→24-38, Alias-AD drift 24-35→24-36), the External Dependencies "PATH author availability" Sprint 37 → 38, the Sprint-to-Sprint Dependencies (**new** `Sprint 37 depends on Sprint 36`; old `S37 depends on 22+36` → `S39 depends on 22+37`; `S39 dep S37`→`S40 dep S39`; `S40 dep S39`→`S41 dep S40`), and footnote ⁸ (the genuine-floor ramp: **S36 actual 75** [fourth consecutive modal-flat, markov emission proven but banked as a dedicated full-corpus-discriminator effort, ≥76 missed; one `src/` landing P7 robustlp] → new **S37 →≥76** via the markov `σ=sp` discriminator → S39 maintain ≥76 → S40 ≥77 → S41 ≥78; the renumbered S39–S41 stale targets; the as-measured ≥64% line S31–S41). The `## Changelog` history entries were left frozen. Footnote ² updated S23–S40 → S23–S41.

- **2026-08-05:** Inserted new **Sprint 36** (Weeks 37–38): Sprint 35 Carryforward — markov Diagonal-Kronecker +1-Floor Lever, sarf Symbolic-Emit Subsystem, fawley Constraint-Index-Diagonal Correction, ganges/gangesx Multi-Root Recovery, the rocket/mine Consultation Trio, camcge Walras (Epic 5) & the GAMS-54 Re-Baseline. Based on `SPRINT_35/SPRINT_RETROSPECTIVE.md` §5 + `SPRINT_35/SPRINT_36_CARRYFORWARDS.md` (Sprint 35 closed **modal-flat, 0 bucket moves** — Solve 108 / Match 93 / genuine floor 75, the third consecutive modal-flat; every deep track REPLAN'd/deferred/banked, one `src/` landing [P6 turkey `$161` compile-recovery, testbed-gated]): P1 **NEW** markov `stat_z` diagonal-Kronecker +1-floor lever [a control-confirmed `CASE_B` cold-emit bug making a `verified_convex` model a *methodology* match; the two-part fix flips it methodology→genuine, floor 75→76, fully local; Part-1 diagonal split verified 13.3→1.55, Part-2 the `σ=sp` off-diagonal enumeration], P2 #1385 sarf symbolic-emit subsystem [369K `task` columns], P3 #1111/#1112 fawley constraint-index-diagonal [control-verified 473→1.14e-13 but the general predicate leaks onto markov #1110 → needs a derivative-structure discriminator; +Solve H-b → `--force` survey], P4 ganges/gangesx ≥5-blocker cascade recovery [`$141`/`$145`/`$149` → `$66` cold → `rPower` presolve; the `$149` `_diff_prod` fix verified+banked], P5 the rocket #1462 PATH submission + mine #1443 primal-degenerate-LP question + camcge #1330 → Epic 5, P6 turkey v54 testbed re-solve + the residual multi-root cohort (turkpow/clearlak/dinam/indus), P7 the GAMS-54 corpus re-baseline (the v53→v54 transition's first infra task) + robustlp NA fix + property fixtures. 14-day sprint at ≤12h/day = 168h cap; estimated effort 94–134h. Cascaded existing sprints forward: old S36 (PATH Author Consultation & Solution Forcing) → new **S37** (Weeks 39–40); old S37 (Quality+Performance+PATH Feedback Integration) → new **S39** (Weeks 41–42); old S39 (v2.0.0 Release + Epic 5 Planning) → new **S40** (Weeks 43–44). Inserted a new **S36** Rolling-KPIs column (carryforward targets: Solve maintain ≥81% stretch +1–4 via markov/fawley/ganges/turkey, Full Pipeline Match ≥64%⁸ genuine floor 75→≥76 via markov, path_syntax_error maintain ≤7 stretch ≤5 via ganges/gangesx, model_infeasible ≤7, path_solve_terminated maintain ≤5, Translate maintain ≥95% stretch +1→96% via #1385 sarf) + relabelled the old S36/S37/S39 columns S37/S39/S40 + a new S40 column, and annotated the S35 Full Pipeline Match cell with its actual (**75**). Updated sprint dependencies (new S36 depends on S35 carryforwards + the S28–35 tooling + the turkey unit-test pattern; old-S36-now-S37 PATH-consultation dep re-pointed to the new S36; S39 dep on S37; S40 dep on S39), the inline consultation/step-up cross-references inside the renamed S37/S39/S40 bodies (the PATH-consultation Note 36→37; the acceptance-criteria "up from Sprint 36's" → "Sprint 37's"/"Sprint 39's"; the S40 release-criteria Parse/Translate "confirmed from Sprint 37" → **Sprint 39**; the ramp "Sprint 37/38"→"Sprint 39/39"; "Sprint 39-42"→"39-43"; "Sprints 18-38"→"18-39"; "REMAINING_FAILURES.md from Sprint 37"→"38"), the risk table sprint-range references (Stacked blockers 20-34→20-35, MCP-NLP solution divergence 25-36→25-37, PATH author availability 35-36→36-37, Diminishing returns 22-35→22-36, IndexOffset 26-34→26-35, Infeasible MCP formulations 24-36→24-37, Alias-AD architectural drift 24-34→24-35), the External Dependencies "PATH author availability" Sprint 36 → 37, the forward PATH-consultation / quality / release references inside the *earlier* S29–S35 bodies ("the renumbered Sprint 36 / Sprint-36 consultation → **Sprint 37**"; the Sprint-36 forcing/PATH hand-offs → **37**; "moves to / occupies the renumbered **Sprints 36–38**" → **Sprints 37–39**), and footnote ⁸ (the genuine-floor ramp: **S35 actual 75** [third consecutive modal-flat, ≥76 missed; turkey +1 testbed-gated, markov +1 lever discovered but banked] → new **S36 →≥76** via markov [the strongest, fully-local] → S37 maintain ≥76 → S39 ≥77 → S40 ≥78; the renumbered stale ≥45/48/52% targets → S37–S40; the as-measured ≥64% line S31–S40). The `## Changelog` history entries were left frozen (renumbering applied only to the pre-Changelog body). Footnote ² updated S23–S39 → S23–S40.

- **2026-07-22:** Inserted new **Sprint 35** (Weeks 35–36): Sprint 34 Carryforward — mine Head-Offset Dual Subsystem, sarf Symbolic-Emit Subsystem, fawley Constraint-Index-Diagonal Correction, ganges/gangesx Multi-Root Recovery, camcge Walras (Epic 5) & rocket PATH Submission. Based on `SPRINT_33/SPRINT_RETROSPECTIVE.md` §4 + `SPRINT_34/SPRINT_35_CARRYFORWARDS.md` (Sprint 34 closed **full modal-flat, 0 bucket moves** — Solve 108 / Match 93 / genuine floor 75, exactly the Task-9 projection; every deep track REPLAN'd/deferred, the one `src/` landing [P4 sense-aware bound-transfer] a warm-start-correctness fix with no +Solve): P1 #1443 mine head-offset dual [H_dual refuted S34 Day 1 — `x.m=0`-degenerate boundary], P2 #1385 sarf from-scratch symbolic/parametric emit mode [369K `task` columns; `enumerate_variable_instances` foundational → corpus-wide re-architecture], P3 #1111/#1112 fawley constraint-index-diagonal sameas correction [473→18.468; +Solve is **H-b** → forcing], P4 **NEW** ganges/gangesx multi-root recovery [S34 Day 11 corrected the prep's single-root hypothesis → three independent roots: the verified-and-banked `$141` `.l`-calibration NaN-cleanup fix + the `$145` universal-set gap + the deep **`$149` CES/LES `prod()` product-rule stationarity AD bug** gating six models; turkey `$161`], P5 camcge #1330 → Epic 5 + the rocket #1462 consultation submission, P6 residual failure-cohort + banked follow-ons + P7 infrastructure. 14-day sprint at ≤12h/day = 168h cap; estimated effort 92–134h. Cascaded existing sprints forward: old S35 (PATH Author Consultation & Solution Forcing) → new **S36** (Weeks 37–38); old S36 (Quality+Performance+PATH Feedback Integration) → new **S37** (Weeks 39–40); old S37 (v2.0.0 Release + Epic 5 Planning) → new **S39** (Weeks 41–42). Inserted a new **S35** Rolling-KPIs column (carryforward targets: Solve maintain ≥81% stretch +1–4 via mine/fawley-forcing/ganges/camcge, Full Pipeline Match ≥64%⁸ genuine floor 75→≥76, path_syntax_error maintain ≤7 stretch ≤5 via ganges/gangesx, model_infeasible ≤7, path_solve_terminated maintain ≤5, Translate maintain ≥95% stretch +1→96% via #1385 sarf) + relabelled the old S35/S36/S37 columns S36/S37/S39 + a new S39 column. Updated sprint dependencies (new S35 depends on S34 carryforwards + the S28–34 tooling + the S33 P6 `.l`-init + S34 P4 bound-transfer fixtures; old-S35-now-S36 PATH-consultation dep re-pointed to the new S35; S37 dep on S36; S39 dep on S37), the inline consultation/step-up cross-references inside the renamed S36/S37/S39 bodies (the PATH-consultation Note 35→36; the acceptance-criteria "up from Sprint 35's" → "Sprint 36's"/"Sprint 37's"; the S39 release-criteria Parse/Translate "confirmed from Sprint 35" → **Sprint 37** [corrects a pre-existing off-by-one: the release sprint confirms from its immediately prior quality/performance sprint, not from the consultation sprint]; the ramp "Sprint 36/37"→"Sprint 37/38"; "Sprint 37-41"→"38-42"; "Sprints 18-35"→"18-38"; "REMAINING_FAILURES.md from Sprint 35"→"37"), the risk table sprint-range references (Stacked blockers 20-33→20-34, MCP-NLP solution divergence 25-35→25-36, PATH author availability 34-35→35-36, Diminishing returns 22-34→22-35, IndexOffset 26-33→26-34, Infeasible MCP formulations 24-35→24-36, Alias-AD architectural drift 24-33→24-34), the External Dependencies "PATH author availability" Sprint 35 → 36, the forward PATH-consultation / quality / release references inside the *earlier* S29–S34 bodies ("the renumbered Sprint 35 / Sprint-35 consultation → **Sprint 36**"; the Sprint-35 forcing/PATH hand-offs → **36**; "moves to / occupies the renumbered **Sprints 35–37**" → **Sprints 36–38**), and footnote ⁸ (the genuine-floor ramp: **S34 actual 75** [full modal-flat, ≥76 missed] → new **S35 →≥76** → S36 maintain ≥76 → S37 ≥77 → S39 ≥78; the renumbered stale ≥45/48/52% targets → S36–S39; the as-measured ≥64% line S31–S39). The `## Changelog` history entries were left frozen (renumbering applied only to the pre-Changelog body). Footnote ² updated S23–S37 → S23–S39.
- **2026-07-17:** Inserted new **Sprint 34** (Weeks 33–34): Sprint 33 Carryforward — mine Head-Offset Dual Subsystem, sarf Symbolic-Emit Subsystem, fawley Second-Index Correction, the Max-Convention Bound-Transfer Track, camcge Walras (Epic 5) & rocket PATH Submission. Based on `SPRINT_33/SPRINT_RETROSPECTIVE.md` §4 + `SPRINT_33/SPRINT_34_CARRYFORWARDS.md` (six control-confirmed carryforwards: P1 #1443 mine head-offset dual [H1 head-label re-keying proven *value-invariant* S33 Day 2 — 22→22 nonzero rows], P2 #1385 sarf from-scratch symbolic/parametric emit mode [369K `task` columns; active 398 not statically enumerable], P3 #1111/#1112 fawley constraint-index-diagonal sameas correction [473→18.468; +Solve is **H-b**, non-emit MS-5 divergence → forcing], P4 the **NEW** max-convention bound-transfer-sign track [shared mine/fawley], P5 camcge #1330 → Epic 5 + the rocket #1462 consultation submission, P6 banked ganges/gangesx `$141/$145/$149` + agreste scope-verify) + P7 infrastructure. 14-day sprint at ≤12h/day = 168h cap; estimated effort 88–130h. Cascaded existing sprints forward: old S34 (PATH Author Consultation & Solution Forcing) → new **S35** (Weeks 35–36); old S35 (Quality+Performance+PATH Feedback Integration) → new **S36** (Weeks 37–38); old S36 (v2.0.0 Release + Epic 5 Planning) → new **S37** (Weeks 39–40). Inserted a new **S34** Rolling-KPIs column (carryforward targets: Solve maintain ≥81% stretch +1 via mine/fawley-forcing/bound-transfer, Full Pipeline Match ≥64%⁸ genuine floor 75→≥76, path_syntax_error maintain ≤7, model_infeasible ≤7, Translate maintain ≥95% stretch +1→96% via #1385 sarf) + relabelled the old S34/S35/S36 columns S35/S36/S37 + annotated the S33 cells with actuals (Solve 108 / Match 93 / genuine floor 75). Updated sprint dependencies (new S34 depends on S33 carryforwards + the S28–33 tooling; old-S34-now-S35 PATH-consultation dep re-pointed to the new S34; S36 dep on S35; S37 dep on S36), the inline consultation/forward cross-references in the S29–S33 bodies (the PATH-consultation sprint 34→35; the quality/release 35/36→36/37; "renumbered Sprints 34–36"→"35–37"; the S34–S36 stale-target refs→S35–S37), the External Dependencies "PATH author availability" Sprint 34 → 35, and footnote ⁸ (the genuine-floor ramp: **S33 actual 75** → S34 ≥76 → S35 maintain ≥75 → S36 ≥77 → S37 ≥78; the renumbered stale ≥45/48/52% targets → S35–S37). The `## Changelog` history entries were left frozen (renumbering applied only to the pre-Changelog body). Footnote ² updated S23–S36 → S23–S37.
- **2026-07-15:** Inserted new Sprint 33 (Sprint 32 Carryforward — mine Head-Offset Cross-Term Architecture, sarf Symbolic-Emit Subsystem, #1111/#1112 Second-Index Generalization, camcge Walras [Epic 5] & rocket/Case-c PATH Forcing) based on `SPRINT_32/SPRINT_RETROSPECTIVE.md` §4 (Priorities 1–5 = the five Sprint-32 REPLAN carryforwards: #1443 mine head-offset bound-active cross-term architecture [the control-confirmed 6-bound-active-row wrong-sign `N`, not a warm-start value], #1385 sarf symbolic parametric `stat_task` emit subsystem [the 369,024-column `acost3`+variable-path enumeration the 2-D constraint gate doesn't cover], fawley #1111/#1112 second-index generalization [`max|stat_bq|` 473→18, 96%], camcge #1330 → Epic 5 dual-consistent Walras numéraire [step 1 scalar-`fx` landed S32; step 2 reaches omega 191.7346 but MS-4], #1462 rocket PATH-consultation input finalized + #1236 hhfair/CGE documented Case-c [`case_c_objdef`, ISSUE_1236 closed]) + Priority 6 pulling the residual failure-cohort re-triage (agreste double-`solve` Case-b, cesam/lnts Case-c) + adjacent emit backlog + Priority 7 infrastructure (property fixtures for the P1/P2/P3 emit paths once they land, genuine-floor tracking re-baselined to 74, Epic-4-`SUMMARY` continuation). Each carryforward inherits a Sprint-32 **control-confirmed** diagnosis (not just a pinned location — the fix's sign and sufficiency are confirmed). 14-day sprint at ≤12h/day = 168h budget cap; estimated effort 86–126h total (incl. ~4h retest). Cascaded existing sprints forward: old S33 (PATH Author Consultation & Solution Forcing) → new S34 (Weeks 33–34); old S34 (Quality+Performance+PATH Feedback Integration) → new S35 (Weeks 35–36); old S35 (v2.0.0 Release + Epic 5 Planning) → new S36 (Weeks 37–38). Added S36 column to Rolling KPIs + inserted new S33 column with carryforward targets (Solve Rate ≥81% stretch +2 via mine + fawley + camcge, Full Pipeline Match ≥64%⁸ genuine floor 74→≥75, path_syntax_error maintain ≤8, path_solve_terminated maintain ≤5, model_infeasible ≤7 maintain, Translate Rate maintain ≥95% stretch +1→96% via #1385 sarf) + annotated the S32 Match cell with its actual (**74**). Updated sprint dependencies (new S33 depends on S32 carryforwards + the S28–32 diagnostic tooling incl. the new `case_c_objdef` classifier + the `--force` scaffold; old-S33-now-S34 PATH-consultation dep re-pointed from S32 to the new S33; S35 dep on S34; S36 dep on S35), the risk table sprint-range references (Stacked blockers 20-32→20-33, MCP-NLP solution divergence 25-34→25-35, PATH author availability 33-34→34-35, Diminishing returns 22-33→22-34, IndexOffset 26-32→26-33 + the S33 head-offset-cross-term clause, Infeasible MCP formulations 24-34→24-35, Alias-AD architectural drift 24-32→24-33), External Dependencies "PATH author availability" Sprint 33 → 34, and the inline cross-references inside the renamed S34/S35/S36 bodies ("Sprint 36-40"→"37-41"/"Sprints 18-34"→"18-35"/"Sprints 33–35"→"34–36"/"Sprints 32–34"→"32–35"/"Sprints 31–33"→"31–34"). The `## Changelog` history entries were left frozen (renumbering applied only to the pre-Changelog body). Footnote ⁸ updated (renumbered S34–S36 targets flagged stale; the S31–S36 as-measured line; the genuine-floor ramp corrected to **S32 actual 74** [mine + camcge REPLAN'd — a flat-KPI close] → new **S33 ≥75** → S34 maintain ≥75 → S35 ≥77 → S36 ≥78). Footnote ² updated S23–S35 → S23–S36.
- **2026-07-13:** Inserted new Sprint 32 (Sprint 31 Carryforward — mine Head-Offset 4th Site, sarf 4-D Stationarity, camcge Dual-Consistent Walras [Epic 5], rocket PATH-Consultation & Case-c Documentation) based on `SPRINT_31/SPRINT_RETROSPECTIVE.md` §4 (Priorities 1–5 = the five Sprint-31 REPLAN carryforwards: #1443 mine head-offset 4th bound-complementarity site [the IR foundation `EquationDef.head_domain_offsets` + Site-2 dual transfer landed S31], #1385 sarf 4-D `task(g,t,mn,mn)` `stat_task` sparsification [the 369,024-instance blow-up, not the 1,152 constraints], camcge #1330 → Epic 5 dual-consistent Walras + the CASE_B `nu_mps_fx` `stat_mps` defect, #1462 rocket PATH-consultation forcing input [division-by-variable reformulation exhausted], #1236 hhfair + CGE-cluster documented genuine Case-c [ν_objective reduction control-refuted, sign flip banned]) + Priority 6 pulling adjacent offset-alias/symbolic-emit backlog + residual failure-cohort re-triage + Priority 7 infrastructure (property-catalog extension for the head-offset 4th-site + sarf 4-D shapes, genuine-floor KPI tracking, Epic-4-SUMMARY groundwork). Each carryforward inherits a Sprint-31 precisely-pinned root cause (mine's bound-complementarity localization; sarf's 369K finding; camcge's `stat_mps` CASE_B verdict; rocket's exhausted-lever survey; the CGE Case-c control). 14-day sprint at ≤12h/day = 168h budget cap; estimated effort 80–120h total (74–110h work-items + ~6–10h prep). Cascaded existing sprints forward: old S32 (PATH Author Consultation & Solution Forcing) → new S33 (Weeks 31–32); old S33 (Quality+Performance+PATH Feedback Integration) → new S34 (Weeks 33–34); old S34 (v2.0.0 Release + Epic 5 Planning) → new S35 (Weeks 35–36). Added S35 column to Rolling KPIs + inserted new S32 column with carryforward targets (Solve Rate ≥81% stretch +2 via mine + camcge, Full Pipeline Match ≥64%⁸ genuine floor 74→≥75, path_syntax_error maintain ≤8, path_solve_terminated maintain ≤5, model_infeasible ≤5 stretch ≤3, Translate Rate ≥95% stretch +1 via #1385 sarf). Updated sprint dependencies (new S32 depends on S31 carryforwards + the S28–31 diagnostic tooling + the `--force` scaffold; old-S32-now-S33 dep on S22 case studies + S32 stabilization; S34 dep on S33; S35 dep on S34), the Sprint-30/31 bodies' forward references (renumbered-Sprint-32 PATH-consultation → Sprint 33; "moves to Sprints 32–34" → "Sprints 33–35"; the rocket/Case-c "→ Sprint 32" hand-offs → Sprint 33), risk table sprint-range references (Stacked blockers 20-31→20-32, MCP-NLP solution divergence 25-33→25-34, PATH author availability 32-33→33-34, Diminishing returns 22-32→22-33, IndexOffset 26-31→26-32, Infeasible MCP formulations 24-33→24-34, Alias-AD architectural drift 24-31→24-32), External Dependencies "PATH author availability" Sprint 32 → 33, and the inline cross-references inside the renamed S33/S34/S35 bodies ("Sprint 32-36"→"33-37"/"Sprint 35-39"→"36-40"/"Sprints 18-33"→"18-34"/Acceptance-Criteria "up from Sprint 32/33"). Footnote ⁸ updated (renumbered S33–S35 targets flagged stale; the genuine-floor ramp gets the new S32 lands ≥75 → S33 maintain ≥75 → S34 ≥77 → S35 ≥78). Footnote ² updated S23–S34 → S23–S35.
- **2026-07-08:** Inserted new Sprint 31 (Sprint 30 Carryforward — Head-Offset IR Plumbing, General-Alias AD #1111/#1112 & Dual-Consistent CGE) based on `SPRINT_30/SPRINT_RETROSPECTIVE.md` §4 (Priorities 1–6 = the six Sprint-30 REPLAN carryforwards: #1443 mine head-offset IR plumbing → shared 3-site helper, #1111/#1112 offset-alias general-alias core [polygon; himmel16 documented non-convex], camcge #1330 dual-consistent Walras transform [the Day-11 finding: the drop-row is primal-correct but breaks the MCP dual], #1385 sarf symbolic runtime-guard cross-term emit workstream, the cold-convex obj-grad residue [hhfair `stat_u` / CGE `stat_xp` — the sign-flip was control-refuted], #1462 rocket forcing → PATH-consultation input) + Priority 7 pulling the deferred property-test fixtures (head-offset + polygon successor shapes) + genuine-floor tracking. Each carryforward inherits a Sprint-30 control-verified recipe / precisely-pinned root cause (polygon's 4-term fix warm-matches 0.780; camcge's price-pin gives omega 191.735; hhfair's sign-flip is refuted; sarf's `stat_task` is hand-derived). 14-day sprint at ≤12h/day = 168h budget cap; estimated effort 92–134h total (86–124h work-items + ~6–10h prep). Cascaded existing sprints forward: old S31 (PATH Author Consultation & Solution Forcing) → new S32 (Weeks 29–30); old S32 (Quality+Performance+PATH Feedback Integration) → new S33 (Weeks 31–32); old S33 (v2.0.0 Release + Epic 5 Planning) → new S34 (Weeks 33–34). Added S34 column to Rolling KPIs + inserted new S31 column with carryforward targets (Solve Rate ≥81% stretch +2 via mine + camcge, Full Pipeline Match ≥64%⁸ genuine floor 70→≥73, path_syntax_error maintain ≤8, path_solve_terminated maintain ≤5, model_infeasible ≤5, Translate Rate ≥95% stretch +1 via #1385). Updated sprint dependencies (new S31 depends on S30 carryforwards + the S28–30 diagnostic tooling + the `--force` scaffold; old-S31-now-S32 dep on S22 case studies + S31 stabilization; S33 dep on S32; S34 dep on S33), the Sprint-30 body's forward references (renumbered-Sprint-31 PATH-consultation → Sprint 32; "moves to Sprints 31–33" → "Sprints 32–34"), External Dependencies "PATH author availability" Sprint 31 → 32, and the inline cross-references inside the renamed S32/S33/S34 bodies (Acceptance-Criteria/ramp/"up from"/"Sprint 34-38"→"35-39"/"Sprints 18-32"→"18-33"/"REMAINING_FAILURES.md from Sprint 32"→"33"). Footnote ⁸ updated (renumbered S32–S34 targets flagged stale; the genuine-floor ramp gets the new S31 lands ≥73 → S32 maintain ≥73 → S33 ≥75 → S34 ≥78). Footnote ² updated S23–S33 → S23–S34.
- **2026-07-04:** Inserted new Sprint 30 (Sprint 29 Carryforward — Head-Domain-Offset Emit Architecture, Non-Convex Forcing & Offset-Alias AD) based on `SPRINT_29/SPRINT_RETROSPECTIVE.md` §"Sprint-30 carryforwards" (Priorities 1–6 = the six retrospective carryforwards: head-domain-offset emit architecture #1443 [mine +1 Solve + robert genuine-floor], #1462 rocket non-convex forcing, #1236 hhfair widened-VARIABLE presolve fix, #1385 symbolic runtime-guard cross-term emit [sarf], offset-alias cross-terms #1111/#1112 [polygon + himmel16], camcge #1330 → Epic 5 Walras drop-row + fix-numéraire transformation) + Priorities 7–8 pulling the adjacent general-emit backlog (Class-B CGE `stat_pz` coefficient discrepancy — confirmed NOT Walras — + cold-convex residue) and the S29-retrospective infrastructure (property-test catalog extension for head-offset/offset-alias shapes, Rolling-KPIs Match re-baseline, solution-forcing scaffold). 14-day sprint at ≤12h/day = 168h budget cap; estimated effort 92–142h total (86–132h work-items + ~6–10h prep) (upper bound assumes all 8 priorities ship; lower bound assumes the deepest tracks — P1 multi-site head-offset, P2 non-convex forcing, P6 Epic-5 transformation — partially slip to Sprint 31). Cascaded existing sprints forward: old S30 (PATH Author Consultation & Solution Forcing) → new S31 (Weeks 27–28); old S31 (Quality+Performance+PATH Feedback Integration) → new S32 (Weeks 29–30); old S32 (v2.0.0 Release + Epic 5 Planning) → new S33 (Weeks 31–32). Added S33 column to Rolling KPIs + inserted new S30 column with carryforward targets (Solve Rate ≥81% stretch +2 via mine + rocket, Full Pipeline Match ≥64%⁸ genuine floor 69→≥72, path_syntax_error maintain ≤8, model_infeasible ≤5, Translate Rate ≥95% stretch +1 via #1385). Updated sprint dependencies (new S30 depends on S29 carryforwards + diagnostic tooling; old-S30-now-S31 dep on S22 case studies retained + dep on S30 carryforward stabilization + solution-forcing scaffold), risk table sprint-range references (Stacked blockers 20-29→20-30, MCP-NLP solution divergence 25-31→25-32, PATH author availability 30-31→31-32, Diminishing returns 22-30→22-31, IndexOffset 26-29→26-30 + S30 head-offset-architecture note, Infeasible MCP formulations 24-31→24-32, Alias-AD architectural drift 24-29→24-30 + S30 property-fixtures note), External Dependencies "PATH author availability" Sprint 30 → 31, and inline "Sprint 33-37"→"Sprint 34-38" + "Sprints 18-31"→"Sprints 18-32" references inside the renamed Sprint 33 body (plus the S31/S32 self/cross-references remapped). Footnote ⁸ updated (renumbered S31–S33 targets flagged stale; new S30 ≥64% sits on the re-baselined line). Footnote ² updated S23–S32 → S23–S33 targets are in-scope counts.

- **2026-06-22:** Inserted new Sprint 29 (Sprint 28 Carryforward — Presolve/Warm-Start Robustness, Cold-Convex MCP Convergence & AD Cross-Term Cleanup) based on `SPRINT_28/SPRINT_RETROSPECTIVE.md` §"Sprint 29 Recommendations / Carryforwards" (Priorities 1–5 = the five retrospective carryforwards: #1443 mine head-domain-offset MCP infeasibility, #1462 rocket presolve `_fx_`-multiplier warm-start + non-convex convergence, #1385 translation-timeout Option-1 cross-terms, cold-convex robustness for the ~24 warm-start-only models, camcge #1330 → Epic 5 CGE-degeneracy scoping) + Priorities 6–8 pulling additional open backlog beyond the retrospective to fill the 14-day budget (P6 objective-mismatch cohort #1332/#1247/#1239/#1236, P7 offset-alias gradient + dollar-condition AD architecture #1146/#1143/#1112/#1111, P8 checkpoint re-solve + post-methodology re-baseline tooling from the S28 retrospective "What We'd Do Differently" #4/#5). 14-day sprint at ≤12h/day = 168h budget cap; estimated effort 96–134h total (80–124h work-items + ~6–10h prep) (upper bound assumes all 8 priorities ship; lower bound assumes the diagnosis-heavy REPLAN-prone tracks — #1443 cold-coupling, #1462 non-convex convergence, P7 AD-engine #1111/#1112 — partially slip to Sprint 30). Cascaded existing sprints forward: old S29 (PATH Author Consultation & Solution Forcing) → new S30 (Weeks 25–26); old S30 (Quality+Performance+PATH Feedback Integration) → new S31 (Weeks 27–28); old S31 (v2.0.0 Release + Epic 5 Planning) → new S32 (Weeks 29–30). Added S32 column to Rolling KPIs + inserted new S29 column with carryforward targets (Solve Rate ≥81%, Full Pipeline Match ≥64% re-baselined per new footnote ⁸, path_syntax_error maintain ≤8, model_infeasible ≤5, Translate Rate ≥95%). Updated sprint dependencies (new S29 depends on S28 carryforwards + diagnostic tooling; old-S29-now-S30 dep on S22 case studies retained + dep on S29 carryforward stabilization), risk table sprint-range references (Stacked blockers 20-28→20-29, MCP-NLP solution divergence 25-30→25-31, PATH author availability 29-30→30-31, Diminishing returns 22-29→22-30, IndexOffset 26-28→26-29, Infeasible MCP formulations 24-30→24-31, Alias-AD architectural drift 24-28→24-29), External Dependencies "PATH author availability" Sprint 29 → 30, and inline "Sprint 32-36"→"Sprint 33-37" + "Sprints 18-30"→"Sprints 18-31" references inside the renamed Sprint 32 body. Added footnote ⁸ (Full Pipeline Match re-baseline on the S28 Day-13 92/142 actual; the renumbered S30–S32 ≥45/48/52% targets flagged stale). Footnote ² updated S23–S31 → S23–S32 targets are in-scope counts.

- **2026-06-09:** Inserted new Sprint 28 (Sprint 27 Carryforward — KKT Cross-Term Correctness, AD Architectural Fixes & Diagnostic/CI Tooling) based on `SPRINT_27/SPRINT_RETROSPECTIVE.md` §"Sprint 28 Recommendations" (Priorities 1–6: #1224 parameter-valued-offset KKT cross-term, #1388 camshape `stat_r`, #1393+#1335 otpop scalar-eq Sum-collapse, #1387 cclinpts three-coupled-change, #1390 kand re-diagnosis, camcge CGE degeneracy) + Priority 7 Sprint-27 lower-priority cleanups (#1374 `.l` shape, #1400 `message`-field leak, #1385 cross-terms) + Priorities 8–10 infrastructure (golden-staleness CI check, KKT-residual verification harness, embedded-NLP-divergence detector + AD cross-term property tests) + Sprint 27 retrospective process recs PR24 (Day-0 traced fix-surface) + PR25 (projection discipline). 14-day sprint at ≤12h/day = 168h budget cap; estimated effort 98–144h total (101–149h work-items + ~5–8h prep) (upper bound assumes all 10 priorities ship; lower bound assumes Priorities 4–6 — #1387/#1390/camcge, the diagnosis-heavy REPLAN-prone tracks — partially slip to Sprint 29). Cascaded existing sprints forward: old S28 (PATH Author Consultation & Solution Forcing) → new S29 (Weeks 23–24); old S29 (Quality+Performance+PATH Feedback Integration) → new S30 (Weeks 25–26); old S30 (v2.0.0 Release + Epic 5 Planning) → new S31 (Weeks 27–28). Added S31 column to Rolling KPIs + inserted new S28 column with carryforward targets (Solve ≥81%, Match ≥45%, path_syntax_error maintain ≤8, model_infeasible ≤5, Translate ≥95%). Updated sprint dependencies (S28 now depends on S27 alias-AD baseline + the filed Sprint-28 carryforwards; S29 dep on S22 case studies retained + new dep on S28 carryforward stabilization), risk table sprint-range references (Stacked blockers 20-27→20-28, MCP-NLP solution divergence 25-29→25-30, PATH author availability 28-29→29-30, Diminishing returns 22-28→22-29, IndexOffset 26-27→26-28, Infeasible MCP formulations 24-29→24-30, Alias-AD architectural drift 24-27→24-28), and inline "Sprint 31-35"→"Sprint 32-36" + "Sprints 18-29"→"Sprints 18-30" references inside the renamed Sprint 31 body. Footnote ² updated S23–S30 → S23–S31 targets are in-scope counts.

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
