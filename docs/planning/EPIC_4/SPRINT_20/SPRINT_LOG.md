# Sprint 20 Log

**Sprint Duration:** 15 days (Day 0 – Day 14)  
**Start Date:** 2026-02-19  
**Baseline Commit:** `dc390373c42528772d9d3c6fb558bf1e28927463`

---

## Baseline Metrics (Day 0)

**Test Suite:** 3,579 passed, 10 skipped, 2 xfailed

| Metric | Baseline | Target | Stretch |
|---|---|---|---|
| Parse success | 112/160 (70.0%) | ≥ 127/160 (≥ 79.4%) | ≥ 132/160 (≥ 82.5%) |
| lexer_invalid_char | 26 | ≤ 11 | ≤ 8 |
| model_no_objective_def | 14 | ≤ 4 | ≤ 1 |
| Translate success | 96/112 (85.7%) | ≥ 110/127 (≥ 86.6%) | — |
| Solve success | 27 | ≥ 30 | ≥ 33 |
| Full pipeline match | 10 | ≥ 15 | ≥ 18 |
| Tests | 3,579 | ≥ 3,650 | — |

---

## Workstream to Issue Mapping

### WS1: `.l` Initialization Emission
- **Issues:** #753 (circle), #757 (bearing)
- **Target models:** circle, abel, chakra, bearing, + 5 others with expression-based `.l`
- **Effort:** ~4h

### WS2: IndexOffset `to_gams_string()` Extensions
- **Target models:** sparta, tabora, otpop; mine, pindyck (cascading)
- **Effort:** ~3h

### WS3: Lexer Grammar Fixes
- **Target:** lexer_invalid_char ≤ 11 (from 26; −15 target)
- **Phase 1 (L+M+H):** camcge, ferts, tfordy, cesam, spatequ, senstran, worst, iobalance, lop
- **Phase 2 (A+E):** indus, mexls, paperco, sarf, turkey, turkpow, cesam2, gussrisk, trnspwl
- **Phase 3 (J+K):** mathopt3, dinam
- **Effort:** ~8–10h

### WS4: model_no_objective_def Preprocessor Fix
- **Target:** 13 models currently excluded by `$if set workSpace` preprocessor bug
- **Effort:** ~3h

### WS5: Pipeline Match — Tolerance + Inf Parameters
- **Part A:** Raise rtol 1e-6→1e-4 (chem, dispatch, hhmax, mhw4d, mhw4dx)
- **Part B:** codegen_numerical_error / ±Inf parameter handling (decomp, gastrans, gtm, ibm1)
- **Effort:** ~3–4h

### WS6: Golden-File Tests for Matching Models
- **Purpose:** Regression guard for the 10 (→ target 15) models achieving full pipeline match
- **Effort:** ~2h

---

## Daily Progress

### Day 0 — Baseline Confirm + Sprint Kickoff (2026-02-19)

**Status:** ✅ COMPLETE

**Activities:**
- Verified baseline: `make test` passed with 3,579 tests
- Created SPRINT_LOG.md with baseline metrics
- Verified KNOWN_UNKNOWNS.md is current (Unknowns 4.1, 5.x, 7.x already ✅ VERIFIED; Unknown 6.4 INCOMPLETE as expected)
- Mapped open GitHub issues to workstreams (documented above)

**Branch:** `sprint20-day0-kickoff`

**Deliverables:**
- ✅ `make test` passing (3,579 tests)
- ✅ `SPRINT_LOG.md` initialized with baseline metrics
- ✅ KNOWN_UNKNOWNS.md verified current

---

### Day 1 — WS1 `.l` Emission: IR + Parser (2026-02-19)

**Status:** ✅ COMPLETE
**PR:** #801 (merged)

**Activities:**
- Extended `VariableDef` with `l_expr`/`l_expr_map` for expression-based `.l` initialization
- Mutual exclusion semantics: setting numeric clears expression storage and vice versa
- Index preservation: `l_expr_map` keys use full `IndexOffset`/`SubsetIndex` objects
- 7 unit tests added

**Metrics:** Tests 3,586 (+7)

---

### Day 2 — WS1 `.l` Emission: Emitter + End-to-End (2026-02-19)

**Status:** ✅ COMPLETE
**PR:** #802 (merged)

**Activities:**
- Extended MCP emitter to emit `.l` initialization assignments
- End-to-end pipeline testing for circle, abel, chakra models

---

### Day 3 — WS2 IndexOffset `to_gams_string()` Extensions (2026-02-20)

**Status:** ✅ COMPLETE
**PR:** #805 (merged)

**Activities:**
- Extended `IndexOffset.to_gams_string()` for arithmetic offsets, function-call offsets
- Fixed sparta, tabora, otpop models

---

### Day 4 — WS3 Lexer Phase 1: Subcategories L, M, H (2026-02-20)

**Status:** ✅ COMPLETE
**PR:** #806 (merged)

**Activities:**
- Fixed lexer issues for subcategories L (camcge, ferts, tfordy), M (cesam, spatequ, senstran), H (worst, iobalance, lop)
- Created issue docs for blocking models (#807, #808, #809)
- lexer_invalid_char reduced from 26 to 21

---

### Day 5 — WS4 model_no_objective_def Preprocessor Fix (2026-02-20)

**Status:** ✅ COMPLETE
**PR:** #811 (merged)

**Activities:**
- Fixed `$if set workSpace` inline guard preprocessor bug
- model_no_objective_def reduced from 14 to 4
- Created issue #810 (nested loop solve extraction — deferred)

**Additional PRs merged:**
- #812: Fixed issues #807 (MCP/CNS solve w/o objective), #808 (loop tuple dollar condition), #809 (errorf in FUNCNAME); added errorf derivative & evaluator support
- #813: Fixed issue #810 (recursive solve extraction from doubly-nested loops); model_no_objective_def reduced from 4 to 1

---

### Day 6 — Checkpoint 1 + Buffer (2026-02-20)

**Status:** ✅ COMPLETE
**PR:** #814

**Activities:**
- Ran full pipeline retest (160 models)
- Evaluated Checkpoint 1 GO/NO-GO criteria
- Triaged open GitHub issues from Days 3-5

### Day 7 — WS3 Phase 2: Compound Set Data Part 1 (2026-02-20)

**Status:** ✅ COMPLETE
**PR:** TBD

**Activities:**
- Extended `table_row_label` to support deep dotted labels with parenthesized sub-lists (e.g., `wheat.bullock.standard.(heavy,january)`)
- Added multi-word set element grammar rule (`SET_ELEMENT_ID SET_ELEMENT_ID STRING` → `set_multiword_with_desc`)
- Added numeric-prefix tuple support: grammar rules for `NUMBER.ID`, `NUMBER.STRING`, `NUMBER.(list)` in set data
- Added preprocessor fix: quote numeric prefixes in `N.word` and `N.(` patterns to prevent FLOAT tokenization
- sarf and indus now pass grammar/lexer stage (blocked by downstream internal_error: lead/lag, variable index)
- mexls passes multi-word and numeric-dot stages (blocked by downstream `yes$(...)` syntax)
- 7 unit tests added

**Metrics:** Tests 3,642 (+7), lexer_invalid_char 19 (−2 from Day 6)

---

## Checkpoints

### Checkpoint 1 (Day 6)

**GO/NO-GO Criteria:**
- Parse success ≥ 125/160 (78.1%)
- Solve success ≥ 28
- `.l` emission PR merged
- IndexOffset PR merged
- All tests pass

**Evaluation:**

| Criterion | GO threshold | Current | Verdict |
|---|---|---|---|
| Parse success | ≥ 125/160 (78.1%) | 123/160 (77.8%) | **NO-GO** (-2) |
| Solve success | ≥ 28 | 29 | **GO** |
| `.l` emission PR | Merged | ✅ #801, #802 | **GO** |
| IndexOffset PR | Merged | ✅ #805 | **GO** |
| Tests | All pass | ✅ 3,635 passed | **GO** |

**Decision: NO-GO** — Parse 2 short of 125 threshold. Contingency 1 NOT triggered (parse ≥ 120).

**Action:** Per PLAN.md, redirect Days 7–9 to remaining WS3 Phase 1 items and debugging to close the 2-model parse gap.

**Full Pipeline Metrics (Day 6):**

| Metric | Baseline | Day 6 | Delta |
|---|---|---|---|
| Parse success | 112/160 (70.0%) | 123/160 (77.8%) | +11 |
| lexer_invalid_char | 26 | 21 | -5 |
| model_no_objective_def | 14 | 1 | -13 |
| Translate success | 96/112 (85.7%) | 109/123 (88.6%) | +13 |
| Solve success | 27 | 29 | +2 |
| Full pipeline match | 10 | 10 | 0 |
| Tests | 3,579 | 3,635 | +56 |

**Parse error breakdown:**
- lexer_invalid_char: 21
- semantic_undefined_symbol: 8
- internal_error: 3
- parser_invalid_expression: 2
- model_no_objective_def: 1

**Solve error breakdown:**
- path_syntax_error: 45
- path_solve_terminated: 22
- model_infeasible: 12
- path_solve_license: 1

**Status:** EVALUATED — NO-GO (parse)

---

### Checkpoint 2 (Day 11)

**GO/NO-GO Criteria:**
- Parse success ≥ 125/160 (78.1%)
- lexer_invalid_char ≤ 11
- model_no_objective_def ≤ 4
- Full pipeline match ≥ 15
- Solve success ≥ 30
- All tests pass

**Status:** PENDING

---

## Sprint Close (Day 14)

**Final Metrics:** TBD

**Sprint 20 Retrospective:** TBD

---

## Notes

- Sprint 20 Prep Phase completed: 10 tasks merged to main via PRs #790–#799
- All planning documents on main: PLAN.md, PLAN_PROMPTS.md, BASELINE_METRICS.md, KNOWN_UNKNOWNS.md, PREP_PLAN.md
- Key deferrals to Sprint 21: accounting variable detection (#764), AD condition propagation (#763)

### Day 6 Issue Triage

Open GitHub issues reviewed at Checkpoint 1:

| Issue | Summary | Stage | Sprint Action |
|---|---|---|---|
| #532 | Store Objective Variable Name | Enhancement | Deferred (long-standing) |
| #757 | Bearing MCP locally infeasible | Solve | Deferred to Sprint 21 |
| #763 | Chenery MCP division by zero (del parameter) | Solve | Deferred to Sprint 21 |
| #764 | Mexss MCP locally infeasible (accounting vars) | Solve | Deferred to Sprint 21 |
| #765 | Orani MCP locally infeasible (fixed exogenous vars) | Solve | Deferred to Sprint 21 |
| #789 | Min/max in objective produces infeasible MCP | Solve | Deferred to Sprint 21 |
| #803 | Circle MCP remains infeasible | Solve | WS5 candidate (Day 10) |

All open issues are solve/match-stage; none block the parse gap that caused Checkpoint 1 NO-GO. The parse gap (123 → 125) is driven by `lexer_invalid_char` (21 remaining) and needs WS3 Phase 1 completion.
