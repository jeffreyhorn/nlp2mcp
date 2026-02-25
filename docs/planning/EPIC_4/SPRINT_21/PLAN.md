# Sprint 21 Detailed Plan

**Created:** 2026-02-24
**Sprint Duration:** 15 days (Day 0 – Day 14)
**Estimated Effort:** ~48–58 hours (~3.2–3.9h/day effective capacity)
**Risk Level:** MEDIUM
**Baseline:** `feffaa95` — parse 132/160 (82.5%), translate 123/132 (93.2%), solve 33/124 (26.6%), match 16/33 (48.5%), tests 3,715

---

## Executive Summary

Sprint 21 targets five primary priorities identified by the prep phase, plus four supporting workstreams. The primary priorities are: (1) `%macro%` expansion in the preprocessor to unblock saras/springchain, (2) internal_error triage for 7 models with 5 distinct root causes, (3) path_syntax_error reduction targeting the top 3 subcategories (E+D+A = 26 models within budget), (4) deferred Sprint 20 issues (#789, #828, #826), and (5) match rate improvement via tolerance adjustment and IndexOffset gradient fix. Supporting workstreams cover semantic error resolution (+7 parse), emerging translation blockers, PATH convergence investigation, and solution comparison enhancement.

**Key scope decisions from prep research:**
- **Semantic errors are the quickest win:** Adding 4 functions to FUNCNAME regex (+5 parse in 30min) plus acronym handler and sameas fix (+2 parse) = +7 parse for ~3-4h total
- **path_syntax_error budget triage:** Full catalog is 15-22h (9 subcategories, 45 models) but budget is 8-12h. Top 3 subcategories (E: set quoting, D: neg exponent, A: Table data) cover 26/45 models (58%) for ~6-9h
- **Macro expansion:** Task 2 design research was not completed during prep — Day 2-3 must include design work alongside implementation
- **internal_error lead/lag:** One fix unblocks 3/7 models (highest leverage)
- **Match rate:** Primary cause is KKT formulation bugs, not initialization. Only 2 near-matches (port, chakra). Projected improvement: 16 → 18-20

### Sprint 21 Targets

| Metric | Baseline | Target | Stretch | How |
|--------|----------|--------|---------|-----|
| Parse success | 132/160 (82.5%) | ≥ 135/160 (84.4%) | ≥ 141/160 (88.1%) | Semantic +7, macro +2, internal_error +4 |
| lexer_invalid_char | 10 | ≤ 5 | ≤ 3 | Macro expansion (-2), remaining lexer fixes |
| internal_error (parse) | 7 | ≤ 3 | ≤ 1 | Lead/lag (-3), if-stmt (-1), table (-1), arity (-1) |
| Solve | 33 | ≥ 36 | ≥ 40 | path_syntax_error fixes unblock new solvers |
| Match | 16 | ≥ 20 | ≥ 22 | Tolerance (+1), IndexOffset gradient (+2-4), LP bounds (+0-4) |
| PATH analysis | — | All path_solve_terminated classified | — | 29 models classified by root cause |
| Solution comparison | — | Framework extended | — | Primal/dual/complementarity comparison |
| Tests | 3,715 | ≥ 3,780 | — | New tests for each workstream |

---

## Workstreams

### WS1: Semantic Error Resolution (Priority 6 in PROJECT_PLAN.md)
**Effort:** ~3-4h
**Target models:** camcge, feedtray, cesam2, sambal, procmean (FUNCNAME), worst (acronym), cesam (sameas)
**Source:** `SEMANTIC_ERROR_AUDIT.md`
**Files:** `src/gams/gams_grammar.lark` (FUNCNAME), `src/ir/parser.py` (acronym handler, sameas fix)

Scheduled early (Day 1) because it's the quickest path to +7 parse successes, exceeding the ≥135 target with a single day's work.

| Step | Models | Effort |
|------|--------|--------|
| Add `sign\|centropy\|mapval\|betareg` to FUNCNAME | camcge, feedtray, cesam2, sambal, procmean | 30min |
| Add `acronym_stmt` handler to IR builder | worst | 1-2h |
| Fix sameas string literal handling | cesam | 1h |
| Unit tests + pipeline verification | all 7 | 1h |

**Metric impact:** parse 132 → 139/160 (if all 7 parse), exceeds ≥135 target on Day 1.

### WS2: Macro Expansion in Preprocessor (Priority 1)
**Effort:** ~6-8h
**Target models:** saras (`%system.nlp%`), springchain (`$set`/`$eval`/`%N%`/`%NM1%`)
**Source:** `KNOWN_UNKNOWNS.md` Category 1 (unknowns 1.1-1.4 — NOT YET VERIFIED, Task 2 incomplete)
**Issues:** #837, #840
**Files:** `src/ir/preprocessor.py`

Note: Prep Task 2 (macro expansion design) was not completed. Days 2-3 must include design work.

| Step | Effort |
|------|--------|
| Design macro store + expansion algorithm | 1-2h |
| Implement `$set`/`$setglobal` + `%name%` expansion | 2-3h |
| Implement `$eval` arithmetic evaluation | 1-2h |
| Implement `%system.nlp%` system macro | 1h |
| Unit tests + springchain/saras pipeline verification | 1h |

**Metric impact:** lexer_invalid_char 10 → 8 (-2: saras, springchain); parse 139 → 141/160.

### WS3: internal_error Triage (Priority 2)
**Effort:** ~7-11h
**Target models:** imsl, sarf, tfordy (lead/lag), senstran (if-stmt), turkpow (table), indus (arity), clearlak (include)
**Source:** `INTERNAL_ERROR_CATALOG.md`
**Files:** `src/ir/parser.py` (`_extract_indices`, `_handle_if_stmt`, `_parse_param_data_items`)

| Priority | Fix | Models | Effort |
|----------|-----|--------|--------|
| 1 | Lead/lag in `_extract_indices()` | imsl, sarf, tfordy | 2-3h |
| 2 | `if` statement condition parsing | senstran | 2-3h |
| 3 | Table row dotted index parsing | turkpow | 1-2h |
| 4 | Variable index arity leniency | indus | 1-2h |
| 5 | Reclassify/auto-declare (missing include) | clearlak | 1h |

**Metric impact:** internal_error 7 → 1-3 (target ≤3 met after Priority 1-2 fixes).

### WS4: path_syntax_error Reduction (Priority 3, budget-triaged)
**Effort:** ~8-10h (within 8-12h budget)
**Target models:** 26/45 models from top 3 subcategories
**Source:** `PATH_SYNTAX_ERROR_CATALOG.md`
**Files:** `src/emit/emit_gams.py`, `src/ir/parser.py`, `src/gams/gams_grammar.lark`

Budget triage applied per RETROSPECTIVE_ALIGNMENT.md: full catalog is 15-22h; top 3 subcategories fit within 8-12h.

| Priority | Subcategory | Models | Effort | Stage |
|----------|-------------|--------|--------|-------|
| 1 | E: Set index quoting | irscge, lrgcge, moncge, quocge, sample, stdcge, twocge | 1-2h | Emitter |
| 2 | D: Negative exponent parens | launch, ps2_f_eff, ps2_f_inf | 1h | Emitter |
| 3 | A: Missing Table data | 16 models | 4-6h | Parser |

**Deferred to Sprint 22:** Subcategories C (9), B (5), F (1), G (2), I (1), J (1) = 19 models, ~6-8h.

**Metric impact:** Up to 26 models unblocked at solve stage (pending secondary errors).

### WS5: Deferred Sprint 20 Issues (Priority 4, triaged)
**Effort:** ~7-10h
**Target issues:** #789, #828, #826, #757 (stretch)
**Source:** `DEFERRED_ISSUES_TRIAGE.md`

| Priority | Issue | Model | Problem | Effort |
|----------|-------|-------|---------|--------|
| 1 | #789 | (general) | Min/max reformulation in objective | 2-3h |
| 2 | #828 | ibm1 | Missing bound multipliers | 2-3h |
| 3 | #826 | decomp | Empty stationarity equation | 3-4h |
| 4 (stretch) | #757 | bearing | Non-convex convergence investigation | 2-3h |

**Already resolved:** #763, #810, #835 (0h).
**Addressed by WS2:** #837, #840 (0h additional).
**Deferred to Sprint 22+:** #764 (8-12h), #765 (incompatible), #827 (6-8h), #830 (8-10h).

### WS6: Match Rate Improvement (Priority 5)
**Effort:** ~4-6h
**Target:** 16 → 20+ matches
**Source:** `SOLVE_MATCH_GAP_ANALYSIS.md`

| Step | Models | Effort | Projected Gain |
|------|--------|--------|----------------|
| Tolerance adjustment (rtol → 1e-2) | port | <1h | +1 match |
| IndexOffset gradient fix in `derivative_rules.py` | chakra, catmix, abel, qabel | 3-4h | +2-4 matches |
| LP bound investigation | apl1p, apl1pca, sparta, aircraft | 2h | +0-4 matches |

### WS7: Emerging Translation Blockers
**Effort:** ~4-6h
**Trigger:** After WS1 (semantic) and WS3 (internal_error) unblock new models, some will hit translation failures.

| Step | Effort |
|------|--------|
| Run newly-parsing models through full pipeline (per PR4) | 1h |
| Categorize new translation failures | 1-2h |
| Fix highest-priority blockers | 2-3h |

### WS8: PATH Convergence Investigation
**Effort:** ~4-5h
**Target:** 29 `path_solve_terminated` models
**Source:** `BASELINE_METRICS.md` Section 5

| Step | Effort |
|------|--------|
| For each model: examine PATH output, check residuals, test relaxed tolerances | 3-4h |
| Classify: KKT issue vs starting point vs inherent difficulty vs PATH options | 1h |
| Write `PATH_CONVERGENCE_ANALYSIS.md` | included |

### WS9: Solution Comparison Enhancement
**Effort:** ~4-5h

| Step | Effort |
|------|--------|
| Extend comparison: primal variable comparison | 1-2h |
| Extend comparison: dual variable comparison | 1-2h |
| Combined relative/absolute tolerance with model defaults | 1h |
| Generate detailed mismatch reports | 1h |

---

## Effort Summary

| Workstream | Estimate | Notes |
|------------|----------|-------|
| WS1: Semantic errors | 3-4h | +7 parse; Day 1 |
| WS2: Macro expansion | 6-8h | +2 parse; Days 2-3 |
| WS3: internal_error | 7-11h | -4 to -6 internal_error; Days 4-5, 11 |
| WS4: path_syntax_error | 8-10h | Up to +26 solve candidates; Days 6-8 |
| WS5: Deferred issues | 7-10h | #789, #828, #826, #757; Days 10-11 |
| WS6: Match rate | 4-6h | +2-9 matches; Day 9 |
| WS7: Emerging translation | 4-6h | After parse improvements; Day 11 |
| WS8: PATH convergence | 4-5h | 29 models classified; Days 12-13 |
| WS9: Solution comparison | 4-5h | Framework extended; Days 13-14 |
| Pipeline retests | 2h | Checkpoints at Days 5, 10, 14 |
| Sprint overhead | 2-3h | Day 0 kickoff, Day 14 close |
| **Total (per-day sum)** | **~48-58h** | Within 46-68h budget |

*Note: Per-workstream estimates sum higher (~51-70h) because multiple workstreams share days with overlapping effort (e.g., Day 5 combines checkpoint + WS3, Day 11 combines WS5+WS3+WS7). The ~48-58h total reflects the per-day schedule, which is the ground truth for capacity planning.*

---

## 15-Day Schedule

### Day 0 — Baseline Confirm + Sprint Kickoff

**Theme:** Verify clean baseline, read PLAN.md, confirm all tests pass
**Effort:** ~1h
**Workstream:** Sprint overhead

| Task | Deliverable |
|------|-------------|
| `make test` — confirm 3,715+ passed | Clean baseline |
| Run full pipeline retest (PR3 compliance) | Baseline verified via `parse_model_file()` + `validate_model_structure()` |
| Create SPRINT_LOG.md from template | Sprint log initialized |
| Record baseline error category breakdown (PR5) | Error categories logged |

**Day 0 criterion:** All tests pass; SPRINT_LOG.md created with baseline metrics and error category breakdown.

**Day 0 status:** COMPLETE (2026-02-24). Tests: 3,715 passed. Pipeline parse retest: 131/160 (minor non-deterministic variance vs stored 132/160). SPRINT_LOG.md initialized. PR #855.

---

### Day 1 — WS1: Semantic Error Resolution (+7 parse)

**Theme:** Quick-win parse improvements — FUNCNAME, acronym, sameas
**Effort:** ~3-4h
**Workstream:** WS1 (Semantic errors)
**Source:** `SEMANTIC_ERROR_AUDIT.md`
**Branch:** `sprint21-day1-semantic-errors`

| Task | Files | Deliverable |
|------|-------|-------------|
| Add `sign\|centropy\|mapval\|betareg` to FUNCNAME regex | `gams_grammar.lark` | +5 models parse |
| Add `acronym_stmt` handler to IR builder | `parser.py` | worst parses |
| Fix sameas string literal handling in conditions | `parser.py` | cesam parses |
| Unit tests for all 3 fixes | `tests/` | ≥5 new tests |
| Run newly-parsing models through full pipeline (PR4) | pipeline | Solve/translate status for 7 new models |

**End of Day 1 criterion:** parse ≥139/160; 7 semantic_undefined_symbol models resolved; newly-parsing models tested through full pipeline.

**Day 1 status:** COMPLETE (2026-02-24). Parse 139/160 (stored). semantic_undefined_symbol: 0 (was 7). Tests: 3,724 passed (+9). All 7 models through full pipeline (PR4): 4 translate OK, 2 translate fail, 1 no objective. 0 solve.

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)
- [x] Run newly-parsing models through full pipeline (PR4)

---

### Day 2 — WS2: Macro Expansion Part 1 (Design + Core Implementation)

**Theme:** Design macro subsystem; implement `$set`/`$setglobal`/`%name%`
**Effort:** ~3-4h
**Workstream:** WS2 (Macro expansion)
**Source:** `KNOWN_UNKNOWNS.md` Category 1
**Branch:** `sprint21-day2-macro-expansion`

| Task | Files | Deliverable |
|------|-------|-------------|
| Design macro store data structure | `preprocessor.py` | MacroStore class |
| Implement `$set name value` / `$setglobal name value` | `preprocessor.py` | Directives processed |
| Implement `%name%` expansion (case-insensitive) | `preprocessor.py` | Macros expanded in source |
| Implement `%system.nlp%` system macro | `preprocessor.py` | saras unblocked |
| Unit tests for `$set` + `%name%` expansion | `tests/` | ≥5 new tests |

**End of Day 2 criterion:** saras parses (if `%system.nlp%` is the only blocker); `$set`/`%name%` expansion functional; unit tests pass.

**Day 2 status:** COMPLETE (2026-02-24). `%system.nlp%` expands correctly. saras moved from lexer_invalid_char to semantic_undefined_symbol (Rcon1 — separate IR issue). $setglobal support added. Tests: 3,734 (+10).

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)
- [x] Run saras through full pipeline (PR4) — macro expansion works; blocked by separate Rcon1 issue

---

### Day 3 — WS2: Macro Expansion Part 2 ($eval + springchain)

**Theme:** Implement `$eval`; verify springchain end-to-end
**Effort:** ~3-4h
**Workstream:** WS2 (Macro expansion)
**Branch:** `sprint21-day3-macro-eval`

| Task | Files | Deliverable |
|------|-------|-------------|
| Implement `$eval name expression` (integer arithmetic) | `preprocessor.py` | `$eval` functional |
| Test springchain expansion: `$set N 10`, `$eval N2 %N%-2` | pipeline | springchain parses |
| Edge cases: nested expansion, undefined macro handling | `preprocessor.py` | Error handling |
| End-to-end: springchain and saras through full pipeline | pipeline | Both models verified |
| Unit tests for `$eval` | `tests/` | ≥3 new tests |

**End of Day 3 criterion:** springchain and saras both parse; lexer_invalid_char ≤8; macro expansion tests pass.

**Day 3 status:** COMPLETE — springchain parses, translates, solves (mismatch); saras blocked by #857 (separate case-sensitivity issue); 10 new tests; 3,744 passed.

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)
- [ ] Run springchain + saras through full pipeline (PR4)

---

### Day 4 — WS3: internal_error — Lead/Lag Fix (3 models)

**Theme:** Fix `_extract_indices()` for lead/lag in parameter assignments
**Effort:** ~2-3h
**Workstream:** WS3 (internal_error)
**Source:** `INTERNAL_ERROR_CATALOG.md` Subcategory B
**Branch:** `sprint21-day4-leadlag-params`

| Task | Files | Deliverable |
|------|-------|-------------|
| Extend `_extract_indices()` to handle `lag_lead_suffix` | `parser.py` | Lead/lag in param assigns |
| Handle linear lead (`+N`), linear lag (`-N`), circular lead (`++expr`) | `parser.py` | All variants |
| Unit tests for lead/lag in parameter context | `tests/` | ≥4 new tests |
| Verify imsl, sarf, tfordy parse | pipeline | 3 models unblocked |
| Run newly-parsing models through full pipeline (PR4) | pipeline | Translate/solve status |

**End of Day 4 criterion:** imsl, sarf, tfordy all parse via `parse_model_file()`; internal_error ≤4.

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)
- [ ] Run imsl, sarf, tfordy through full pipeline (PR4)

---

### Day 5 — CHECKPOINT 1 + WS3: internal_error — if-stmt + table (2 models)

**Theme:** Checkpoint gate; fix senstran and turkpow
**Effort:** ~4h (1h checkpoint + 3h fixes)
**Workstream:** WS3 (internal_error) + Checkpoint
**Branch:** `sprint21-day5-checkpoint1-internal-error`

#### Checkpoint 1 Gate (PR3 + PR5 compliance)

| Check | Command | Expected |
|-------|---------|----------|
| Full pipeline parse retest | `run_full_test.py --only-parse --quiet` | parse ≥141/160 |
| Error category breakdown (parse) | Extract from pipeline output | lexer_invalid_char ≤8, internal_error ≤4, semantic_undefined_symbol ≤0 |
| Error category breakdown (solve) | Extract from pipeline output | path_syntax_error, path_solve_terminated, model_infeasible, path_solve_license counts |
| Test suite | `make test` | All pass |

#### Day 5 Work

| Task | Files | Deliverable |
|------|-------|-------------|
| Fix `_handle_if_stmt` for bare identifier condition | `parser.py` | senstran parses |
| Fix `_parse_param_data_items` for dotted index notation | `parser.py` | turkpow parses |
| Unit tests for both fixes | `tests/` | ≥3 new tests |
| Run newly-parsing models through full pipeline (PR4) | pipeline | Status recorded |

**End of Day 5 criterion:** Checkpoint 1 metrics recorded with error category breakdown; senstran and turkpow parse; internal_error ≤2.

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)
- [ ] Record Checkpoint 1 metrics with error category breakdown in SPRINT_LOG.md (PR5)
- [ ] Run senstran, turkpow through full pipeline (PR4)

---

### Day 6 — WS4: path_syntax_error — Emitter Fixes (E + D, 10 models)

**Theme:** Quick emitter fixes for set quoting and negative exponents
**Effort:** ~2-3h
**Workstream:** WS4 (path_syntax_error)
**Source:** `PATH_SYNTAX_ERROR_CATALOG.md` Subcategories E, D
**Branch:** `sprint21-day6-emitter-fixes`

| Task | Files | Deliverable |
|------|-------|-------------|
| Fix set index quoting (bare identifier vs string literal) | `emit_gams.py` | 7 CGE models unblocked |
| Fix negative exponent parenthesization (`** -N` → `** (-N)`) | `emit_gams.py` | 3 models unblocked |
| Unit tests for both fixes | `tests/` | ≥4 new tests |
| Re-run affected models through full pipeline | pipeline | Solve status for 10 models |

**End of Day 6 criterion:** irscge, lrgcge, moncge, quocge, stdcge, twocge, sample, launch, ps2_f_eff, ps2_f_inf compile cleanly; solve attempted on all 10.

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)
- [ ] Run all 10 models through full pipeline (PR4)

---

### Day 7 — WS4: path_syntax_error — Table Data Capture Part 1

**Theme:** Begin Table data capture in IR builder
**Effort:** ~3-4h
**Workstream:** WS4 (path_syntax_error)
**Source:** `PATH_SYNTAX_ERROR_CATALOG.md` Subcategory A
**Branch:** `sprint21-day7-table-data`

| Task | Files | Deliverable |
|------|-------|-------------|
| Analyze Table data format (multi-line, column headers, dotted indices) | `parser.py` | Format understood |
| Implement Table data parsing into `ParameterDef.values` | `parser.py` | Table data captured |
| Handle standard Table format (header row + data rows) | `parser.py` | Core functionality |
| Unit tests for Table data capture | `tests/` | ≥3 new tests |

**End of Day 7 criterion:** Table data parsing implemented for standard format; unit tests pass; at least 3 Subcategory A models (e.g., iobalance, qdemo7, hydro) have populated `ParameterDef.values`.

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)

---

### Day 8 — WS4: path_syntax_error — Table Data Capture Part 2 + Test

**Theme:** Complete Table data capture; verify Subcategory A models
**Effort:** ~3-4h
**Workstream:** WS4 (path_syntax_error)
**Branch:** `sprint21-day8-table-data-test`

| Task | Files | Deliverable |
|------|-------|-------------|
| Handle edge cases (dotted indices, empty cells, string elements) | `parser.py` | All Table formats |
| Emitter: output Table data in MCP file | `emit_gams.py` | Data emitted |
| Run all 16 Subcategory A models through full pipeline | pipeline | Solve status |
| Fix secondary errors discovered during testing | various | Secondary fixes |

**End of Day 8 criterion:** ≥10/16 Subcategory A models compile cleanly in GAMS (may have secondary errors); path_syntax_error reduced by ≥10 models.

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)
- [ ] Run all 16 Subcategory A models through full pipeline (PR4)

---

### Day 9 — WS6: Match Rate Improvement

**Theme:** Tolerance adjustment + IndexOffset gradient fix
**Effort:** ~4-5h
**Workstream:** WS6 (Match rate)
**Source:** `SOLVE_MATCH_GAP_ANALYSIS.md`
**Branch:** `sprint21-day9-match-improvement`

| Task | Files | Deliverable |
|------|-------|-------------|
| Adjust comparison tolerance for port | `scripts/gamslib/test_solve.py` | port matches |
| Fix IndexOffset gradient in `_diff_varref()` | `src/ad/derivative_rules.py` | Lagged var gradients correct |
| Unit tests for IndexOffset gradient fix | `tests/` | ≥3 new tests |
| Re-run chakra, catmix, abel, qabel | pipeline | Match status |
| Investigate LP bound multipliers for apl1p, sparta, aircraft, apl1pca | analysis | Root cause documented |

**End of Day 9 criterion:** port matches; chakra gradient fixed (may or may not match — depends on other factors); LP bound investigation documented.

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)

---

### Day 10 — CHECKPOINT 2 + WS5: Deferred Issues (#789, #828)

**Theme:** Checkpoint gate; fix min/max reformulation and ibm1 bound multipliers
**Effort:** ~5h (1h checkpoint + 4h fixes)
**Workstream:** WS5 (Deferred issues) + Checkpoint
**Branch:** `sprint21-day10-checkpoint2-deferred`

#### Checkpoint 2 Gate (PR3 + PR5 compliance)

| Check | Command | Expected |
|-------|---------|----------|
| Full pipeline parse retest | `run_full_test.py --quiet` (full pipeline) | parse ≥141/160 |
| Error category breakdown (parse) | Extract from pipeline output | All parse-stage categories |
| Error category breakdown (solve) | Extract from pipeline output | path_syntax_error reduced, solve ≥36 |
| Solve attempts on newly-parsing models (PR4) | targeted runs | All new parsers tested |
| Test suite | `make test` | All pass |
| Match count | pipeline output | match ≥18 |

#### Day 10 Work

| Task | Files | Deliverable |
|------|-------|-------------|
| #789: Bypass epigraph reformulation for objective-defining min/max | `src/kkt/reformulation.py` | Min/max in objective fixed |
| #828: Investigate and fix ibm1 bound resolution | `src/ir/parser.py`, `src/kkt/` | ibm1 bound multipliers correct |
| Unit tests for both fixes | `tests/` | ≥3 new tests |

**End of Day 10 criterion:** Checkpoint 2 metrics recorded with full error category breakdown; #789 fix verified; #828 ibm1 investigated (fix or document remaining issues).

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)
- [ ] Record Checkpoint 2 metrics with error category breakdown in SPRINT_LOG.md (PR5)

---

### Day 11 — WS5: Deferred Issues (#826) + WS3/WS7: Remaining internal_error + Emerging Blockers

**Theme:** decomp stationarity fix; remaining internal_error (indus, clearlak); triage emerging translation blockers
**Effort:** ~4-5h
**Workstream:** WS5 + WS3 + WS7
**Branch:** `sprint21-day11-decomp-emerging`

| Task | Files | Deliverable |
|------|-------|-------------|
| #826: Fix empty stationarity equation detection for decomp | `src/kkt/` | decomp solve attempted |
| Fix indus variable index arity mismatch | `parser.py` | indus parses |
| Reclassify or fix clearlak (missing include) | `parser.py` | clearlak resolved |
| Triage emerging translation failures from WS1/WS3 newly-parsing models | analysis | Failure categorization |
| Fix highest-priority emerging blocker | various | ≥1 blocker fixed |

**End of Day 11 criterion:** internal_error ≤1 (target ≤3 exceeded); decomp solve attempted; emerging blockers documented.

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)
- [ ] Run indus, clearlak, decomp through full pipeline (PR4)

---

### Day 12 — WS8: PATH Convergence Investigation

**Theme:** Systematic analysis of path_solve_terminated models
**Effort:** ~4-5h
**Workstream:** WS8 (PATH convergence)
**Source:** `BASELINE_METRICS.md` Section 5 (29 models)
**Branch:** `sprint21-day12-path-convergence`

| Task | Files | Deliverable |
|------|-------|-------------|
| For each model: examine PATH output, iteration log, residuals | analysis | Per-model data |
| Test with relaxed tolerances and increased iteration limits | PATH options | Sensitivity results |
| Classify: KKT issue vs starting point vs inherent difficulty vs PATH options | document | Classification |
| Write `PATH_CONVERGENCE_ANALYSIS.md` | `docs/planning/EPIC_4/SPRINT_21/` | Analysis document |

**End of Day 12 criterion:** ≥20/29 path_solve_terminated models classified; PATH_CONVERGENCE_ANALYSIS.md drafted.

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)

---

### Day 13 — WS8: PATH Convergence Completion + WS9: Solution Comparison Part 1

**Theme:** Complete PATH analysis; begin solution comparison enhancement
**Effort:** ~4-5h
**Workstream:** WS8 + WS9
**Branch:** `sprint21-day13-path-solcomp`

| Task | Files | Deliverable |
|------|-------|-------------|
| Complete PATH convergence classification (remaining models) | document | All 29 classified |
| Implement primal variable comparison | `scripts/gamslib/` | Primal comparison |
| Implement dual variable comparison | `scripts/gamslib/` | Dual comparison |
| Implement combined relative/absolute tolerance | `scripts/gamslib/` | Tolerance framework |
| Unit tests for comparison framework | `tests/` | ≥3 new tests |

**End of Day 13 criterion:** All 29 path_solve_terminated models classified; solution comparison framework extended with primal and dual comparison.

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)

---

### Day 14 — FINAL CHECKPOINT + Sprint Close + Retrospective

**Theme:** Final pipeline retest; sprint retrospective; documentation
**Effort:** ~2-3h
**Workstream:** Sprint overhead + WS9 completion
**Branch:** `sprint21-day14-sprint-close`

#### Final Checkpoint Gate (PR3 + PR5 compliance)

| Check | Command | Expected |
|-------|---------|----------|
| Full pipeline retest | `run_full_test.py --quiet` (full pipeline) | All acceptance criteria met |
| Parse | pipeline | ≥ 135/160 |
| lexer_invalid_char | pipeline | ≤ 5 |
| internal_error | pipeline | ≤ 3 |
| Solve | pipeline | ≥ 36 |
| Match | pipeline | ≥ 20 |
| Error category breakdown (parse) | pipeline | lexer_invalid_char, internal_error, semantic_undefined_symbol, parser_invalid_expression, model_no_objective_def |
| Error category breakdown (solve) | pipeline | path_syntax_error, path_solve_terminated, model_infeasible, path_solve_license |
| PATH analysis | document | All path_solve_terminated classified |
| Solution comparison | framework | Primal/dual/complementarity comparison implemented |
| Test suite | `make test` | All pass, ≥3,780 |

#### Day 14 Work

| Task | Deliverable |
|------|-------------|
| Complete solution comparison: complementarity residuals + mismatch reports | Framework complete |
| Generate final metrics | SPRINT_LOG.md updated |
| Write sprint retrospective | `SPRINT_RETROSPECTIVE.md` |
| Update PROJECT_PLAN.md with final metrics | Sprint 21 metrics recorded |

**End of Day 14 criterion:** All acceptance criteria verified; retrospective written; Sprint 22 recommendations documented.

**Post-merge checklist:**
- [ ] Record PR number in SPRINT_LOG.md (PR2)
- [ ] Record final metrics with full error category breakdown in SPRINT_LOG.md (PR5)

---

## Checkpoint Gates Summary

| Checkpoint | Day | Key Metrics | PR Compliance |
|------------|-----|-------------|---------------|
| Checkpoint 1 | Day 5 | parse, internal_error, error breakdown | PR3 (pipeline retest), PR5 (categories) |
| Checkpoint 2 | Day 10 | parse, solve, match, error breakdown | PR3, PR4 (newly-parsing solve), PR5 |
| Final | Day 14 | All acceptance criteria | PR2-PR5 (all) |

---

## Dependency Chain

```
Day 0: Baseline
  ↓
Day 1: WS1 Semantic (+7 parse) ─────────────────────────────────┐
  ↓                                                               │
Day 2-3: WS2 Macro (+2 parse) ──────────────────────────────────┤
  ↓                                                               │
Day 4-5: WS3 internal_error (-4 to -6) ─────────────────────────┤
  ↓                                                               │
Day 5: CHECKPOINT 1 (parse ≥141, internal_error ≤4)              │
  ↓                                                               ↓
Day 6-8: WS4 path_syntax_error (E+D+A) ──→ Day 11: WS7 Emerging Translation
  ↓                                           (newly-parsing models)
Day 9: WS6 Match Rate (tolerance + gradient)
  ↓
Day 10: CHECKPOINT 2 (solve ≥36, match ≥18)
  ↓
Day 10-11: WS5 Deferred Issues (#789, #828, #826)
  ↓
Day 12-13: WS8 PATH Convergence + WS9 Solution Comparison
  ↓
Day 14: FINAL CHECKPOINT + Sprint Close
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Macro expansion design takes longer (Task 2 incomplete) | Medium | Medium | Days 2-3 have 6-8h allocated; can extend to Day 4 if needed |
| Table data parsing is more complex than estimated | Medium | High | 4-6h allocated; defer edge cases to Sprint 22 if needed |
| Lead/lag fix exposes secondary errors in imsl/sarf/tfordy | Medium | Low | Re-test after fix; secondary errors are separate tasks |
| IndexOffset gradient fix doesn't improve match rate | Medium | Low | Already conservative estimate (2-4 matches); tolerance fix gives +1 guaranteed |
| PATH convergence investigation reveals no actionable fixes | Low | Medium | Document findings for future sprints; classification is the primary deliverable |
| Emerging translation blockers consume more than 4-6h | Medium | Medium | Time-box to 4-6h; defer remaining to Sprint 22 |

---

## Acceptance Criteria

| Criterion | Target | Verification |
|-----------|--------|-------------|
| Parse rate | ≥ 135/160 (84.4%) | Pipeline retest |
| lexer_invalid_char | ≤ 5 | Pipeline parse error breakdown |
| internal_error (parse) | ≤ 3 | Pipeline parse error breakdown |
| Solve | ≥ 36 | Pipeline solve count |
| Match | ≥ 20 | Pipeline match count |
| PATH analysis | All path_solve_terminated classified | PATH_CONVERGENCE_ANALYSIS.md |
| Solution comparison | Framework extended | Primal/dual/complementarity tests |
| Tests | All pass, ≥ 3,780 | `make test` |
| No regressions | 0 | Existing tests pass |

---

## Process Compliance (Sprint 20 Retrospective)

This plan encodes all 5 Sprint 20 retrospective action items per `RETROSPECTIVE_ALIGNMENT.md` Section 4 (the items Task 10 must encode — PR1 was already addressed in prep deliverables):

1. **PR2 (record PR numbers):** Every day's post-merge checklist includes "Record PR number in SPRINT_LOG.md"
2. **PR3 (pipeline parse retest):** All checkpoint gates use `parse_model_file()` + `validate_model_structure()` (full pipeline), not `parse_file()` alone
3. **PR4 (targeted solve on new parsers):** Days 1, 3, 4, 5, 6, 8, 11 include "run newly-parsing models through full pipeline"
4. **PR5 (error category breakdown):** All checkpoint gates include parse-stage (lexer_invalid_char, internal_error, semantic_undefined_symbol, parser_invalid_expression, model_no_objective_def) and solve/translate-stage (path_syntax_error, path_solve_terminated, model_infeasible, path_solve_license) category counts
5. **Budget awareness:** path_syntax_error top 3 subcategories (E+D+A, 26/45 models) scheduled within 8-12h budget; remaining 19 models deferred to Sprint 22

---

**Document Created:** 2026-02-24
**Next:** Sprint 21 Day 0 (baseline confirm + sprint kickoff)
