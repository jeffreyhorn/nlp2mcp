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
- **path_solve_terminated:** Count reduced by ≥ 50% (from 11 to ≤ 5)
- **Solve Rate:** ≥ 55% of translated models solve correctly
- **Solution Analysis:** All solving models assessed for NLP/MCP match
- **Case Studies:** At least 3 divergence cases documented for consultation
- **Parse Rate:** ≥ 85% of valid corpus
- **Quality:** All tests pass; KKT fixes have comprehensive tests

**Estimated Effort:** 24-30 hours
**Risk Level:** MEDIUM-HIGH (KKT bugs may be subtle; solution divergence analysis may reveal fundamental issues requiring PATH author input)

---

# Sprint 23 (Weeks 11–12): Solve Rate Push & Error Category Reduction

**Goal:** Push solve success from 89 to ≥ 100 and match from 47 to ≥ 55 by addressing the five priority areas identified in the Sprint 22 retrospective: path_solve_terminated, model_infeasible, match rate, path_syntax_error residual, and translate failures. Maintain parse rate. Apply Sprint 22 process recommendations: use full pipeline for all definitive metrics (PR6), track model_infeasible gross fixes and gross influx separately (PR7), and use absolute counts alongside percentages for parse success (PR8). See `SPRINT_RETROSPECTIVE.md` §New Recommendations for Sprint 23 for details.

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
  - 20 models remain from Sprint 22
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
  - Target: reduce from 15 to ≤ 10
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
- **Translate:** ≥ 145/156 (93%, up from 90.4%)
- **Parse:** ≥ 156/160 (maintain 97.5%)
- **Tests:** ≥ 4,300 (up from 4,209)
- **Quality:** All tests pass; all fixes have regression tests

**Estimated Effort:** 32-44 hours
**Risk Level:** MEDIUM (path_solve_terminated and model_infeasible fixes may reveal deeper architectural issues; alias differentiation is a significant AD change; match rate improvement depends on correct root cause identification)

---

# Sprint 24 (Weeks 13–14): PATH Author Consultation & Solution Forcing

**Goal:** Prepare and submit PATH author consultation document. Implement solution forcing strategies. Address remaining solve and translate failures across all pipeline stages.

**Note:** Case studies from Sprint 22; consultation submission now in Sprint 24.

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
  - Target: parse rate ≥ 98% of valid corpus
  - **Deliverable:** Final parse fixes

- **Final Translation Fixes (2-3h)**
  - Address remaining translation blockers
  - Handle newly-discovered patterns from late-arriving parsed models
  - Target: translate rate ≥ 95% of parsed models
  - **Deliverable:** Final translation fixes

- **Final Solve Fixes (2h)**
  - Address any remaining solvable `path_syntax_error` or `path_solve_terminated` models
  - Apply solution forcing strategies to divergent models
  - Target: solve rate ≥ 75% of translated models
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
- **Parse Rate:** ≥ 98% of valid corpus
- **Translate Rate:** ≥ 95% of parsed models
- **Solve Rate:** ≥ 75% of translated models
- **Full Pipeline Match:** ≥ 40% of valid corpus
- **Quality:** All tests pass; all fixes have regression tests

**Estimated Effort:** 22-28 hours
**Risk Level:** MEDIUM (PATH author response timeline is uncertain; solution forcing may have limited effectiveness for some model classes)

---

# Sprint 25 (Weeks 15–16): Quality, Performance & PATH Feedback Integration

**Goal:** Stabilize performance benchmarks. Incorporate any PATH author feedback. Final comprehensive pipeline run. Begin documentation finalization.

**Note:** PATH consultation submitted in Sprint 24; feedback integration now in Sprint 25.

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
- **Deliverable:** Updated metrics; expected full pipeline match ≥ 50%

## Deliverables
- Regression-based performance benchmarks (replacing absolute thresholds)
- PATH author feedback integration
- Final pipeline metrics and comparison report
- `docs/planning/EPIC_4/REMAINING_FAILURES.md` — Remaining failures with roadmap
- Draft Epic 4 SUMMARY.md
- Updated GAMSLIB_STATUS.md, FAILURE_ANALYSIS.md

## Acceptance Criteria
- **Performance Benchmarks:** No flaky CI failures from benchmark tests
- **Final Parse Rate:** ≥ 98% of valid corpus
- **Final Translate Rate:** ≥ 95% of parsed models
- **Final Solve Rate:** ≥ 75% of translated models
- **Full Pipeline Match:** ≥ 50% of valid corpus
- **Documentation:** Remaining failures documented; Epic 4 summary drafted
- **Quality:** All quality gates pass

**Estimated Effort:** 22-30 hours
**Risk Level:** LOW-MEDIUM (mostly consolidation; PATH feedback timing uncertain)

---

# Sprint 26 (Weeks 17–18): v2.0.0 Release & Epic 5 Planning

**Goal:** Complete Epic 4 with v2.0.0 release. Finalize all documentation. Plan Epic 5 based on remaining failures and new opportunities.

**Note:** Performance benchmarks and PATH feedback integration completed in Sprint 25; Sprint 26 focuses on release and forward planning.

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
  - Review REMAINING_FAILURES.md from Sprint 25
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
  - Outline Sprint 27-31 high-level scope
  - **Deliverable:** Draft Epic 5 PROJECT_PLAN.md

### Sprint Retrospective (~2h)
- **Epic 4 Retrospective (2h)**
  - Document what worked well across Sprints 18-26
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
- **Final Parse Rate:** ≥ 98% of valid corpus (confirmed from Sprint 25)
- **Final Translate Rate:** ≥ 95% of parsed models (confirmed from Sprint 25)
- **Final Solve Rate:** ≥ 80% of translated models (confirmed from Sprint 25)
- **Full Pipeline Match:** ≥ 50% of valid corpus (confirmed from Sprint 25)
- **Epic 5 Ready:** Draft project plan created; backlog prioritized
- **Quality:** All quality gates pass on final release

**Estimated Effort:** 22-28 hours
**Risk Level:** LOW (release mechanics and documentation; Epic 5 planning is exploratory)

---

## Rolling KPIs & Tracking

### Sprint-Level KPIs

| Metric | S18 | S19 | S20 | S21 (actual) | S22 (actual) | S23 | S24 | S25 | S26 |
|--------|-----|-----|-----|--------------|--------------|-----|-----|-----|-----|
| Valid Corpus Defined | ✓ | — | — | — | — | — | — | — | — |
| lexer_invalid_char | ~95 | <50 | 10 | **3** | **4** | <8 | <5 | <5 | <5 |
| internal_error (parse) | ~23 | <15 | 7 | **0** | **0** | <5 | <3 | <3 | <3 |
| path_syntax_error | ≤2 | ≤2 | 48 | **41** | **20** | ≤15 | ≤10 | ≤5 | ≤5 |
| path_solve_terminated | 11 | 11 | 29 | **12** (29/29 classified) | **10** | ≤5 | ≤3 | ≤3 | ≤3 |
| model_infeasible | 0 | 0 | 12 | **15** | **12**² | ≤8 | ≤5 | ≤5 | ≤5 |
| Parse Rate (valid corpus) | ~41% | ≥55% | 82.5% | **98.1%** (154/157) | **97.5%** (156/160) | ≥97.5% | ≥98% | ≥98% | ≥98% |
| Translate Rate (of parsed) | ~69% | ~72% | 90.9% | **89.0%** (137/154) | **90.4%** (141/156) | ≥93% | ≥95% | ≥95% | ≥95% |
| Solve Rate (of translated) | ≥52% | ≥52% | 27.5% | **47.4%** (65/137) | **63.1%** (89/141) | ≥70% | ≥75% | ≥75% | ≥80% |
| Full Pipeline Match (valid corpus) | ~14% | ≥20% | 10.0% | **19.1%** (30/157) | **29.4%** (47/160) | ≥34% | ≥40% | ≥50% | ≥50% |

² Sprint 22 `model_infeasible` is 15 total; 12 in-scope after excluding 3 permanently infeasible models (feasopt1, iobalance, orani). A 4th model (meanvar) was declared excluded on Day 7 but later achieved model_optimal, so only 3 remain in the infeasible count. S23–S26 targets are in-scope counts.

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
| Stacked blockers in models | HIGH | HIGH | 20-25 | Track blockers removed, not just models unblocked |
| MCP-NLP solution divergence | HIGH | MEDIUM | 24-26 | PATH author consultation; multiple forcing strategies |
| PATH author availability | MEDIUM | MEDIUM | 25-26 | Self-contained case studies; batch questions; literature fallback |
| Diminishing returns on parse | MEDIUM | MEDIUM | 22-25 | Subcategorize before implementing; preprocessing fallback |
| IndexOffset complexity | MEDIUM | MEDIUM | 20-21 | Design first (S20), implement second (S21); spike validates feasibility |
| Infeasible MCP formulations | MEDIUM | LOW-MEDIUM | 23-26 | PATH consultation; document as inherent limitations |

---

## Dependencies & Prerequisites

### External Dependencies
- GAMS software installed locally (with valid license)
- PATH solver available (version 5.2+)
- Internet access for GAMS team communication
- PATH author availability (Michael Ferris, Steven Dirkse) — needed by Sprint 25

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
- Sprint 24 depends on Sprint 22 (case studies feed consultation document)
- Sprint 25 depends on Sprint 24 (PATH feedback integration)
- Sprint 26 depends on Sprint 25 (performance benchmarks and documentation)

---

## Changelog

- **2026-03-17:** Replaced Sprint 23 content with Sprint 22 retrospective recommendations (5 priorities: path_solve_terminated, model_infeasible, match rate, path_syntax_error residual, translate failures). Cascaded old S23→S24, S24→S25, S25→S26. Added S26 column to Rolling KPIs. Updated sprint dependencies.
- **2026-03-17:** Sprint 22 final metrics recorded (6/8 targets met, 3 exceeded stretch: solve 89, match 47, path_syntax_error 20). Updated Rolling KPIs with Sprint 22 actuals and revised S23–S25 targets. 24 issues labeled `sprint-23` for Sprint 23 backlog.
- **2026-02-06:** Reorganized sprints 18-25 after Sprint 18 scope expansion
  - Sprint 18 expanded to ~56h by pulling Sprint 19 items (emit_gams.py completion, lexer analysis, fix roadmap)
  - Content cascaded forward: S19←S20, S20←S21, S21←S22, S22←S23, S23←S24, S24←S25
  - Sprint 25 now includes Epic 5 planning as new content
  - Updated KPIs to reflect accelerated progress in Sprint 18
- **2026-03-04:** Sprint 21 final metrics recorded (all 8 acceptance criteria met: parse 154/157, solve 65, match 30, tests 3,957). Deferred to Sprint 22: #764 accounting vars, #765 CGE model type, #827 domain violations, #830 Jacobian timeout, remaining path_syntax_error subcategories (C/B/G/F/I/J)
- **2026-02-18:** Added Sprint 19 deferred items to Sprint 20 (Priorities 1–5 from Sprint 19 retrospective: `.l` initialization emission, accounting variable detection, AD condition propagation, remaining lexer_invalid_char taxonomy, full pipeline match rate, plus smoke-test process recommendation)
- **2026-02-05:** Initial EPIC_4 project plan created
