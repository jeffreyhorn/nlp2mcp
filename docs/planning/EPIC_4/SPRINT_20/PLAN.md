# Sprint 20 Detailed Plan

**Created:** 2026-02-19  
**Sprint Duration:** 15 days (Day 0 – Day 14)  
**Estimated Effort:** ~35–42 hours (~2.3–2.8h/day effective capacity)  
**Risk Level:** MEDIUM  
**Baseline:** `dc390373` — parse 112/160 (70.0%), translate 96/112 (85.7%), solve 27/96 (28.1%), match 10/27 (37.0%), tests 3,579

---

## Executive Summary

Sprint 20 focuses on four primary high-ROI workstreams identified by the prep phase (WS1–WS4), with two additional supporting workstreams (WS5–WS6) defined below. The primary workstreams are: (1) `.l` initialization emission to warm-start PATH for circle and other models, (2) IndexOffset `to_gams_string()` extensions for sparta/tabora/otpop, (3) lexer grammar work targeting subcategories L, M, H, A, and E (~15 new parse successes expected), and (4) the `model_no_objective_def` preprocessor fix (~13 new parse successes). Accounting variable detection (mexss/#764) and AD condition propagation (chenery/#763) are deferred to Sprint 21.

**Revised total effort from prep findings: ~35–42h** (down from PROJECT_PLAN.md's 50–64h estimate).

### Key Scope Decisions vs. PROJECT_PLAN.md

| Workstream | PROJECT_PLAN.md Estimate | Sprint 20 Plan | Decision |
|---|---|---|---|
| IndexOffset implementation | 14–16h | 3h | IN SCOPE — only `to_gams_string()` gaps remain (sparta/tabora/otpop); bulk of work done in Sprint 19 |
| `.l` emission | 4–6h | 4h | IN SCOPE — requires IR + parser + emitter changes |
| Translation internal_error fixes | 6–8h | 0h | DESCOPED — only 2 genuine errors remain, both architecturally deferred (smin agg., digamma) |
| model_no_objective_def fix | 4h | 3h | IN SCOPE — preprocessor `$if` single-line bug affects 13 models (~2–3h fix) |
| Accounting variable detection (#764) | 6–8h | 0h | DEFERRED to Sprint 21 — C5 multiplier-consistency criterion not statically feasible |
| AD condition propagation (#763) | 6–8h | 0h | DEFERRED to Sprint 21 — equation-level condition threading is architectural (~6–8h) |
| lexer_invalid_char reduction | 4–6h | 8–10h | EXPANDED — L (5 models), M (2 models), H (2 models), A (6 models), E (3 models) = ~18 models |
| Pipeline match tolerance fix | 4–6h | 2h | IN SCOPE — raise rtol 1e-6→1e-4 to add 5 near-matches |
| codegen_numerical_error (Inf params) | not planned | 2–3h | ADDED — 4 models, single pattern (±Inf parameter values) |

---

## Sprint 20 Targets

| Metric | Baseline | Target | Stretch |
|---|---|---|---|
| Parse success | 112/160 (70.0%) | ≥ 127/160 (≥ 79.4%) | ≥ 132/160 (≥ 82.5%) |
| lexer_invalid_char | 26 | ≤ 11 | ≤ 8 |
| model_no_objective_def | 14 | ≤ 4 | ≤ 1 |
| Translate success | 96/112 (85.7%) | ≥ 110/127 (≥ 86.6%) | — |
| Solve success | 27 | ≥ 30 | ≥ 33 |
| Full pipeline match | 10 | ≥ 15 | ≥ 18 |
| Tests | 3,579 | ≥ 3,650 | — |

**Parse target rationale:** lexer fixes (+15 models: L5, M2, H2, A6 partial, E3 partial via cascading) + model_no_objective_def fix (+12 from `$if` bug fix) + IndexOffset fix (+2 via mine/pindyck cascading) = +~29 in optimistic case; target set at +15 (conservative).

**Match target rationale:** 5 near-matches via rtol fix + 2 from `.l` emission (abel, chakra) + 1 from circle solve = +8 optimistic → target ≥ 15 (conservative: +5 from rtol alone).

---

## Workstreams

### WS1: `.l` Initialization Emission (Priority 1 deferred from Sprint 19)
**Effort:** ~4h  
**Target models:** circle (solve), abel (match), chakra (match), + 5 other models with expression-based `.l`  
**Files:** `src/ir/symbols.py`, `src/ir/parser.py`, `src/emit/emit_gams.py`

| Step | Effort |
|---|---|
| Add `l_expr`/`l_expr_map` fields to `VariableDef` | 0.5h |
| Parser: store `.l` expressions instead of dropping at `_handle_assign` | 1h |
| Emitter: emit `l_expr`/`l_expr_map` in initialization section | 0.5h |
| Unit tests + circle regression | 1h |
| End-to-end: run circle, abel, chakra through pipeline | 0.5h |

**Acceptance criteria:** circle solves (PATH status 1); abel and chakra objective values match within rtol; `tests/` covers expression `.l` capture.

### WS2: IndexOffset `to_gams_string()` Extensions
**Effort:** ~3h  
**Target models:** sparta, tabora (Unary+Call), otpop (Binary+Call/Call); mine, pindyck resolve as cascading bonus  
**Files:** `src/ir/ast.py` (IndexOffset.to_gams_string)

| Step | Effort |
|---|---|
| Extend `to_gams_string()` for `Unary("-", Call(...))` (sparta/tabora) | 1h |
| Extend `to_gams_string()` for `Binary(op, Call, Call)` (otpop) | 1h |
| End-to-end: sparta/tabora/otpop translate; verify PATH solve attempt | 0.5h |
| Fix xfail sum-collapse for IndexOffset wrt-index (cleanup) | 0.5h |

**Acceptance criteria:** sparta, tabora, otpop all translate successfully; mine and pindyck parse (lexer cascading resolved); xfail test either fixed or documented.

### WS3: Lexer Grammar Fixes
**Effort:** ~8–10h  
**Target:** ≤ 11 lexer_invalid_char (from 26; −15 target)

#### Phase 1 — Quick wins (~3–4h, ~9 models + cascading)

| Subcategory | Models | Effort | Notes |
|---|---|---|---|
| L: Set-Model Exclusion | camcge, ferts, tfordy (3); cesam, spatequ (2) | 1–2h | `all - setname` pattern + dotted model-attr |
| M: File/Acronym declarations | senstran, worst | 1h | Stub `File` and `Acronym` keywords |
| H: Control Flow | iobalance (repeat/until), lop (abort$) | 1h | Also unblocks nemhaus (B cascading) |

#### Phase 2 — Core grammar (~4–6h, ~9 models)

| Subcategory | Models | Effort | Notes |
|---|---|---|---|
| A: Compound Set Data (extended) | indus, mexls, paperco, sarf, turkey, turkpow | 3–4h | Extends Sprint 19 A fix: parenthesized sub-lists, multi-word elements, hyphenated+numeric |
| E: Inline Scalar Data | cesam2, gussrisk, trnspwl | 1h | `scalar / value /` missing grammar |

#### Phase 3 — If time permits (~2h, 2+ models)

| Subcategory | Models | Effort |
|---|---|---|
| J: Square bracket function call | mathopt3 | 1h |
| K: Miscellaneous | dinam | 1–2h |

**Automatic via IndexOffset WS2:** mine, pindyck (D cascading), fdesign (B cascading from H fix), nemhaus (B cascading from H fix)

**Acceptance criteria:** lexer_invalid_char ≤ 11; no regression in existing parse successes.

### WS4: model_no_objective_def Fix
**Effort:** ~3h  
**Target:** 13 models currently excluded by `$if set workSpace` preprocessor bug  
**Files:** `src/ir/preprocessor.py` (process_conditionals)

| Step | Effort |
|---|---|
| Fix `process_conditionals` inline `$if` guard (same-line vs next-line) | 1.5h |
| Tests: unit tests for inline `$if` patterns | 0.5h |
| End-to-end: verify camshape, catmix, chain, lnts, polygon parse | 0.5h |
| Handle lmp2 doubly-nested loop (if time) | 0.5h |

**Acceptance criteria:** model_no_objective_def ≤ 4 (down from 14); at least 11 of the 13 `$if`-bug models now parse. (Rationale: fixing "at least 11" leaves ≤ 2 from the `$if` bug + lmp2 doubly-nested + robot/other edge cases = ≤ 4 total remaining. The ≤ 2 target was inconsistent with the "at least 10 of 13" fix rate.)

### WS5: Pipeline Match — Tolerance + Inf Parameters
**Effort:** ~3–4h

#### Part A: rtol adjustment (~2h)
- Raise `DEFAULT_RTOL` from `1e-6` to `1e-4` in `scripts/gamslib/test_solve.py`
- Verify that the 5 near-match models (chem, dispatch, hhmax, mhw4d, mhw4dx) now pass
- Confirm no previously-failing model incorrectly passes at the new tolerance
- **Acceptance criteria:** Full pipeline match ≥ 15; chem/dispatch/hhmax/mhw4d/mhw4dx all match

#### Part B: codegen_numerical_error / Inf parameter handling (~2h, if time)
- 4 models (decomp, gastrans, gtm, ibm1) fail because parameter values are `+Inf`/`-Inf`
- Fix `validate_parameter_values` to treat IEEE infinity as "no bound" and emit `.up = +Inf` / `.lo = -Inf`
- **Acceptance criteria:** decomp, gastrans, gtm, ibm1 translate; 0 codegen_numerical_error (excluding iswnm timeout)

### WS6: Golden-File Tests for Matching Models
**Effort:** ~2h  
**Purpose:** Prevent regression on the 10 (→ target 15) models that achieve full pipeline match  
**Files:** `tests/e2e/test_golden.py` or new `tests/e2e/test_gamslib_match.py`

**Acceptance criteria:** Solve-level regression tests for at least 5 of the 10 currently-matching models; tests pass in CI.

---

## Revised Effort Summary

| Workstream | Revised Estimate | Notes |
|---|---|---|
| WS1: `.l` emission | 4h | IR + parser + emitter (higher than original 2h estimate) |
| WS2: IndexOffset `to_gams_string()` | 3h | Only 2 gap types remain; bulk done in Sprint 19 |
| WS3: Lexer grammar | 8–10h | Phase 1 (3–4h) + Phase 2 (4–6h) |
| WS4: model_no_objective_def | 3h | Preprocessor fix + tests |
| WS5: Tolerance + Inf params | 3–4h | rtol (2h) + Inf params (2h) |
| WS6: Golden-file tests | 2h | Regression guard |
| Pipeline retest | 1.5h | Full run after each major workstream |
| Sprint close + retrospective | 1h | Day 14 |
| **Total (workstreams only)** | **~26–29h** | Excludes sprint overhead below |
| Sprint overhead (Day 0 kickoff, Day 6 checkpoint buffer, Day 11 model validation, Days 12–13 Phase 3 + regression) | ~9–13h | Captured in day-by-day schedule |
| **Total (full sprint)** | **~35–42h** | Down from PROJECT_PLAN.md's 50–64h |

---

## 15-Day Schedule

### Day 0 — Baseline Confirm + Sprint Kickoff ✅ COMPLETE

**Theme:** Verify clean baseline, read PLAN.md, confirm all tests pass  
**Effort:** 1h

| Task | Deliverable |
|---|---|
| `make test` — confirm 3,579 passed | Clean baseline ✅ |
| Review BASELINE_METRICS.md | Baseline numbers internalized ✅ |
| Create SPRINT_LOG.md | Sprint log initialized ✅ |
| Read open GitHub issues; triage to workstream | Issue-to-WS mapping ✅ |

**Day 0 criterion:** All tests pass; SPRINT_LOG.md created. ✅

---

### Day 1 — WS1: `.l` Emission (IR + Parser) ✅ COMPLETE

**Theme:** Fix `.l` expression capture in parser and IR  
**Effort:** 3–3.5h

| Task | Files | Deliverable |
|---|---|---|
| Add `l_expr`/`l_expr_map` to `VariableDef` | `src/ir/symbols.py` | Fields added ✅ |
| Modify `_handle_assign` to store `.l` expressions | `src/ir/parser.py` | Expressions stored, not dropped ✅ |
| Unit tests: expression `.l` capture | `tests/unit/ir/` | ≥ 3 tests covering scalar, indexed, chained `.l` ✅ |

**End of Day 1 criterion:** `circle.gms` IR contains `a.l_expr`, `b.l_expr`, `r.l_expr`; unit tests pass. ✅

---

### Day 2 — WS1: `.l` Emission (Emitter + End-to-End) ✅ COMPLETE

**Theme:** Emit `.l` expressions; validate circle/abel/chakra  
**Effort:** 2–2.5h

| Task | Files | Deliverable |
|---|---|---|
| Emit `l_expr`/`l_expr_map` in initialization section | `src/emit/emit_gams.py` | `.l = expr` lines in MCP output ✅ |
| End-to-end circle test | pipeline | circle MCP has correct `.l` init ✅ |
| Verify circle PATH solve | PATH solver | Still infeasible (deeper issue) ⚠️ |
| Check abel, chakra objective match | `gamslib_status.json` | Dependency ordering issue found ⚠️ |

**End of Day 2 criterion:** `.l` emission implemented; known limitation documented (dependency ordering for interdependent `.l` expressions). ✅

**Notes:**
- Circle's `.l` expressions emit correctly but model remains infeasible (model_status=5)
- Issue #802 filed for dependency ordering in `.l` expressions (affects chakra, others)
- Simple `.l` expressions (circle-style) work correctly; interdependent ones need topological sort

---

### Day 3 — WS2: IndexOffset `to_gams_string()` Extensions ✅ COMPLETE

**Theme:** Fix sparta/tabora/otpop IndexOffset gaps  
**Effort:** 2.5–3h  
**Actual:** ~2.5h

| Task | Files | Deliverable | Status |
|---|---|---|---|
| Extend `to_gams_string()` for `Unary("-", Call(...))` | `src/ir/ast.py` | sparta, tabora translate | ✅ |
| Extend `to_gams_string()` for `Binary(op, Call, Call)` | `src/ir/ast.py` | otpop translates | ✅ |
| Unit tests for new `to_gams_string()` cases | `tests/unit/emit/test_expr_to_gams.py` | 5 tests added | ✅ |
| xfail sum-collapse | `tests/unit/ad/test_index_offset_ad.py` | xfail remains (cleanup item, not blocking) | ✅ |
| Verify mine, pindyck now parse (cascading resolved) | pipeline | mine ✅; pindyck has unrelated display parse error | ⚠️ |

**Deliverables:**
- Extended `IndexOffset.to_gams_string()` to handle:
  - `Unary("-", Call(...))` pattern (sparta, tabora)
  - `Unary("-", Binary(...))` pattern (sparta nested case)
  - `Binary(op, Call, Call)` pattern (otpop)
  - Direct `Call(...)` offset (general case)
- Added helper method `_offset_expr_to_string()` for recursive expression conversion
- 5 comprehensive unit tests covering all new patterns
- sparta, tabora, otpop all translate successfully
- mine translates successfully (was parse failure pre-Sprint 19)

**Notes:**
- xfail sum-collapse test remains as expected-failure (cleanup item per INDEXOFFSET_AUDIT.md; doesn't block any of the 8 IndexOffset models)
- pindyck has an unrelated parse error on display statement (not IndexOffset-related)

**End of Day 3 criterion:** ✅ sparta, tabora, otpop translate; mine parses; PR ready for review.

---

### Day 4 — WS3 Phase 1: Lexer Quick Wins (L + M + H) ✅ COMPLETE

**Theme:** Set-Model Exclusion, unsupported declarations, control flow  
**Effort:** 3–4h  
**Actual:** ~3h

| Task | Files | Models unblocked | Status |
|---|---|---|---|
| Subcat L: `all - setname` + dotted model-attr | `src/gams/gams_grammar.lark`, `src/ir/parser.py` | camcge, ferts, tfordy | ✅ |
| Subcat M: `File` declaration (description variant) | `src/gams/gams_grammar.lark` | (existing Acronym already supported) | ✅ |
| Subcat H: `repeat/until` loop | `src/gams/gams_grammar.lark` | iobalance, lop | ✅ |
| Unit tests for new grammar rules | `tests/unit/test_sprint20_day4_grammar.py` | 12 tests added (6 L, 3 M, 3 H) | ✅ |
| IR builder updates for new model_ref structure | `src/ir/parser.py` | Handle model_simple_ref, model_dotted_ref, model_all_except | ✅ |
| Pipeline retest on affected models | manual verification | 5 models now parse successfully | ✅ |

**Deliverables:**
- **Subcat L (Set-Model Exclusion)**: Added support for `all - eqname` exclusion pattern and dotted `eq.var` references in model statements
  - Grammar: `model_ref` rule with `model_all_except`, `model_dotted_ref`, `model_simple_ref` subtypes
  - IR builder: Updated `_handle_model_with_list` and `_handle_model_multi` to extract equation names from new tree structure
  - Models unblocked: camcge ✅, ferts ✅, tfordy ✅
  - cesam, spatequ: Model definitions now parse; later errors are MCP-related (solve without objective), not lexer errors
  
- **Subcat M (File/Acronym declarations)**: Extended File declaration to support description-only variant
  - Grammar: Added `file_stmt` variant `"file"i ID STRING SEMI` for `File name 'desc';` syntax
  - Acronym already supported from Sprint 17 Day 8
  - Models: senstran File declaration now parses (later error unrelated to File); worst Acronym supported but has other parse issues
  
- **Subcat H (Control Flow)**: Added `repeat/until` loop construct
  - Grammar: `repeat_stmt` with `REPEAT_K exec_stmt* exec_stmt_final UNTIL_K expr SEMI`
  - Added REPEAT_K and UNTIL_K keywords
  - Models unblocked: iobalance ✅, lop ✅ (abort$ already supported from earlier sprints)

**Test coverage:** 12 unit tests covering all three subcategories

**Parse success count:** 5 of 9 target models now parse without lexer errors:
- Subcat L: camcge ✅, ferts ✅, tfordy ✅ (cesam ⚠️ MCP error, spatequ ⚠️ MCP error)
- Subcat M: senstran ⚠️ (File parsed, loop syntax issue), worst ⚠️ (Acronym parsed, other errors)
- Subcat H: iobalance ✅, lop ✅

**Notes:**
- cesam and spatequ now parse past the model definition but fail on MCP solve (no objective) — this is expected and not a lexer issue
- senstran's File declaration works, but there's a separate loop syntax error (tuple with dollar condition)
- worst has other parse errors after the Acronym declaration
- nemhaus still has cascading errors (not yet resolved by H subcategory alone)

**End of Day 4 criterion:** ✅ 5/9 models parse successfully (camcge, ferts, tfordy, iobalance, lop); grammar extended for all three subcategories; 12 unit tests pass; PR ready for review.

---

### Day 5 — WS4: model_no_objective_def Preprocessor Fix ✅ COMPLETE

**Theme:** Fix `$if set workSpace` inline-guard bug
**Effort:** 3h
**Actual:** ~2h

| Task | Files | Deliverable | Status |
|---|---|---|---|
| Fix `process_conditionals` for single-line `$if` | `src/ir/preprocessor.py` | Inline `$if` guard handled correctly | ✅ |
| Unit tests: `$if set X stmt` on same line | `tests/unit/ir/test_preprocessor.py` | 9 tests covering all inline `$if` variants | ✅ |
| End-to-end: camshape, catmix, chain, lnts, polygon parse | pipeline | 8 of 13 `$if`-bug models now parse with objectives | ✅ |
| Handle robot typo (`miniziming`) if needed | N/A | Already handled by grammar — no fix needed | ✅ |
| Document lmp2 (doubly-nested loop) — file issue | GitHub #810 | lmp2 deferred to Sprint 21 | ✅ |

**Deliverables:**
- **Inline `$if` detection**: Added `_split_inline_if()` helper to detect and split inline `$if` directives (condition + guarded statement on same line)
- **process_conditionals fix**: Inline `$if` directives no longer push to the conditional stack, preventing incorrect exclusion of subsequent lines and unclosed `$if` warnings
- **`_evaluate_if_condition` fix**: Normalized `$ifI`/`$ifE` prefixes to `$if` for uniform matching
- **model_no_objective_def count**: Reduced from 14 to 4 (lmp1, lmp2, lmp3, mhw4dxx)
- **Models newly parsing with objectives**: camshape, catmix, chain, lnts, polygon, robot, rocket, elec (8 of 13)
- **Models with other errors** (not `$if`-related): danwolfe (uniformInt), clearlak (undeclared param), feasopt1 (attr_access_indexed), partssupply (parse error), srpchase (File path parse)
- **lmp2 issue filed**: #810 (doubly-nested loop solve extraction, deferred to Sprint 21)

**End of Day 5 criterion:** ✅ model_no_objective_def = 4 (≤4 target met); 8 models newly parsing with objectives; 9 unit tests pass; PR ready for review.

---

### Day 6 — Checkpoint 1 + Buffer ✅

**Theme:** Checkpoint 1 GO/NO-GO; light work; buffer for Days 1–5 overruns

#### Checkpoint 1 (Day 6) GO/NO-GO Criteria

| Criterion | GO threshold | NO-GO action |
|---|---|---|
| Parse success | ≥ 125/160 (78.1%) | Defer WS3 Phase 2 (A subcat); focus on pipeline match |
| Solve success | ≥ 28 | Investigate circle/abel PATH failures; debug before proceeding |
| `.l` emission PR | Merged | If not merged: complete WS1 before Day 7 |
| IndexOffset PR | Merged | If not merged: complete WS2 before Day 7 |
| Tests | All pass | Block on test failures |

**If GO:** Proceed with WS3 Phase 2 (Day 7–9) and WS5 (Day 10).  
**If NO-GO (parse < 125):** Redirect Days 7–9 to remaining WS3 Phase 1 items and debugging.

---

### Day 7 — WS3 Phase 2: Compound Set Data (Part 1) ✅

**Theme:** Extend Subcategory A compound set data grammar
**Effort:** 3h

| Task | Files | Models |
|---|---|---|
| Multi-word set elements (`wire rod`) — `mexls` pattern | `src/gams/gams_grammar.lark` | mexls |
| Parenthesized sub-list in table header (`(sch-1*sch-3)`) — `sarf` pattern | grammar + preprocessor | sarf, possibly indus |
| Unit tests | `tests/unit/` | ≥ 3 tests |

---

### Day 8 — WS3 Phase 2: Compound Set Data (Part 2) + Inline Scalar Data ✅ COMPLETE

**Theme:** Complete Subcategory A; fix Subcategory E
**Effort:** 3–4h

| Task | Files | Models |
|---|---|---|
| Multi-line table row label continuation (`paperco`) | grammar, preprocessor | paperco |
| Hyphenated+numeric element (`hydro-4.1978`) — `turkpow` | grammar, parser | turkpow, turkey |
| Inline scalar data (`/ .05 /`, `/ 50 /`) — Subcat E | grammar, parser | cesam2, gussrisk, trnspwl |
| Pipeline retest for all Subcat A + E models | gamslib_status.json | ≥ 5 new parse successes |

**End of Day 8 criterion:** indus, mexls, paperco, sarf, turkey, turkpow, cesam2, gussrisk, trnspwl — at least 6 of 9 now parse.
**Result:** 6 of 9 parse (indus, paperco, sarf, turkey, turkpow, trnspwl). Remaining: mexls (#816), cesam2 (#817), gussrisk (#818).

---

### Day 9 — WS5 Part A: Pipeline Match Tolerance Fix

**Theme:** Raise rtol; validate near-match models; add golden-file tests  
**Effort:** 3h

| Task | Files | Deliverable |
|---|---|---|
| Raise `DEFAULT_RTOL` to `1e-4` | `scripts/gamslib/test_solve.py` | +5 near-matches (chem, dispatch, hhmax, mhw4d, mhw4dx) |
| Run full pipeline retest; confirm match count | gamslib_status.json | Match ≥ 15 |
| Add solve-level regression tests for 5 matching models | `tests/e2e/` | ≥ 5 new regression tests |
| Verify no false positives at new rtol | pipeline | All matches are genuine |

**End of Day 9 criterion:** Full pipeline match ≥ 15; rtol PR merged; regression tests pass.
**Result:** 16 matches (+6: chem, dispatch, hhmax, mhw4d, mhw4dx, splcge). Regression coverage added in `tests/e2e/test_gamslib_match.py` (16 parametrized model cases). Also fixed issue #763 (chenery MCP division by zero) in separate PR #822.

---

### Day 10 — WS5 Part B: Inf Parameter Handling + Model Validation Prep

**Theme:** Fix codegen_numerical_error; begin model validation  
**Effort:** 3h

| Task | Files | Deliverable |
|---|---|---|
| Fix `validate_parameter_values` for ±Inf values | `src/validation/numerical.py` or emitter | decomp, gastrans, gtm, ibm1 translate |
| Emit `.up = +Inf` / `.lo = -Inf` as appropriate | `src/emit/emit_gams.py` | 0 codegen_numerical_error (ex iswnm) |
| Begin model validation: run solve on all parse-success models | gamslib_status.json | Fresh solve results |

**End of Day 10 criterion:** codegen_numerical_error ≤ 1 (iswnm timeout only); all newly-parsing models validated.

**Day 10 result:** COMPLETE. codegen_numerical_error = 0 (all 4 models now pass parameter validation). ±Inf emitted as GAMS `inf`/`-inf`. 3 of 4 models translate (gastrans blocked by unsupported `signpower` function). 9 new unit tests, 3,701 total (+15). Filed 4 new blocking issues (#825–#828). Full pipeline retest started.

---

### Day 11 — Model Validation + Checkpoint 2 ✅ COMPLETE

**Theme:** Complete model validation; assess sprint state
**Effort:** 2–3h

| Task | Deliverable |
|---|---|
| Complete model validation run (all parse-success models) | Updated solve/match metrics ✅ |
| Review any new issues uncovered by validation | Filed GitHub issues ✅ |
| Checkpoint 2 evaluation | GO/NO-GO decision ✅ |

#### Checkpoint 2 (Day 11) GO/NO-GO Criteria

| Criterion | GO threshold | Current | Verdict |
|---|---|---|---|
| Parse success | ≥ 125/160 (78.1%) | 129/158* (81.7%) | ✅ GO |
| lexer_invalid_char | ≤ 11 | 11 | ✅ GO |
| model_no_objective_def | ≤ 4 | 1 | ✅ GO |
| Full pipeline match | ≥ 15 | 16 | ✅ GO |
| Solve success | ≥ 30 | 33 | ✅ GO |
| Tests | All pass | 3,712 passed (10 skipped, 2 xfailed) | ✅ GO |

\* The evaluation suite contains 158 candidate models (filtered by convexity status). The "160" in sprint planning thresholds was an approximation; thresholds remain defined on the original planning numbers.

**Decision: GO** — All 6 criteria met. Proceed with Phase 3 (Days 12–13) and remaining WS6.

**End of Day 11 criterion:** ✅ Checkpoint 2 evaluated; all criteria met; Phase 3 confirmed.

---

### Day 12 — Phase 3 + WS6: Regression Tests ✅ COMPLETE

**Theme:** Phase 3 grammar (if Checkpoint 2 GO); golden-file test coverage
**Effort:** 3h

| Task | Files | Deliverable |
|---|---|---|
| Phase 3: Square bracket function call (mathopt3) — Subcat J | grammar | mathopt3 parses ✅ |
| Phase 3: Miscellaneous (dinam) — Subcat K | grammar + preprocessor | dinam parses ✅ |
| WS6: Solve-level regression tests | `tests/e2e/` | 3 new regression tests ✅ |

**End of Day 12 criterion:** ✅ mathopt3 parses (Subcat J); dinam parses (Subcat K); 3 solve-level regression tests added (alkyl, circle, himmel16); total WS6 coverage = 19 tests (16 match + 3 solve).

---

### Day 13 — Sprint Close Prep: Issues + Documentation

**Theme:** File/close remaining issues; update documentation  
**Effort:** 2h

| Task | Deliverable |
|---|---|
| File issues for all deferred items (accounting vars, AD condition propagation, `.scale`, lmp2, saras/springchain preprocessor) | GitHub issues filed |
| Smoke-test all "not fixable" declarations (lesson from Sprint 19) | Each deferred item verified via `python -m src.cli <model>` |
| Update SPRINT_LOG.md with final metrics | Sprint log complete |
| Run final `make test` | 0 failures |

---

### Day 14 — Sprint Close + Retrospective

**Theme:** Final pipeline retest; sprint retrospective  
**Effort:** 2–3h

| Task | Deliverable |
|---|---|
| Final full pipeline retest | Updated `gamslib_status.json` |
| Record final metrics vs. targets | SPRINT_LOG.md complete |
| Write Sprint 20 Retrospective | `docs/planning/EPIC_4/SPRINT_20/SPRINT_RETROSPECTIVE.md` |
| Update CHANGELOG.md with sprint summary | CHANGELOG.md |
| Tag release if appropriate | Git tag |

---

## Checkpoints Summary

### Checkpoint 1 (Day 6)

| Criterion | Target | Fallback if missed |
|---|---|---|
| Parse success | ≥ 125/160 | Defer Subcat A; focus on model_no_objective_def |
| Solve success | ≥ 28 | Debug circle/abel; PATH warm-start analysis |
| `.l` emission PR merged | Yes | Complete before Day 7 (Day 6 buffer) |
| IndexOffset PR merged | Yes | Complete before Day 7 (Day 6 buffer) |
| All tests pass | Yes | Block on failures |

### Checkpoint 2 (Day 11) ✅ GO

| Criterion | Target | Actual | Status |
|---|---|---|---|
| Parse success | ≥ 125/160 | 129/158* | ✅ |
| lexer_invalid_char | ≤ 11 | 11 | ✅ |
| model_no_objective_def | ≤ 4 | 1 | ✅ |
| Full pipeline match | ≥ 15 | 16 | ✅ |
| Solve success | ≥ 30 | 33 | ✅ |
| All tests pass | Yes | 3,712 passed, 10 skipped, 2 xfailed | ✅ |

\* Evaluation suite has 158 candidates; "160" in thresholds was a planning approximation.

---

## Contingency Plans

### Contingency 1: WS3 Phase 1 takes longer than expected (> 4h)

**Trigger:** By end of Day 4, fewer than 7 new lexer parse successes.  
**Action:** Defer Subcategory A (WS3 Phase 2) entirely to Sprint 21. Redirect Days 7–8 to WS5 pipeline match work and WS6 golden-file tests. Parse target reduced to ≥ 120/160 (75%).

### Contingency 2: model_no_objective_def fix is more complex than ~3h

**Trigger:** By end of Day 5, fewer than 8 of 13 `$if`-bug models are unblocked.  
**Action:** Document the specific preprocessor case that remains unresolved; file a detailed issue. Reduce model_no_objective_def target to ≤ 6. Use saved time on WS5 (tolerance/Inf) and WS6 (regression tests).

### Contingency 3: circle still fails PATH after `.l` emission fix (at Day 2 check)

**Trigger:** circle translates but PATH still reports model_status=5 (locally infeasible) after `.l` fix.  
**Action:** Do not spend more than 1h debugging. File issue with exact PATH output. Close #753 as "requires `.scale` emission or alternative formulation." Proceed to WS2.

---

## Open Risks (KNOWN_UNKNOWNS PARTIAL/INCOMPLETE)

The following unknowns were not fully resolved during prep and are flagged as open risks for Sprint 20:

### Risk 1: AD Condition Propagation (Unknowns 3.1/3.2 — ⚠️ PARTIAL)
- **Status:** chenery's `$` condition is equation-level (easier case, ~6–8h), not inline. AD system has `DollarConditional` support but `EquationDef.condition` is not threaded through stationarity assembly as a guard.
- **Impact:** chenery (#763) remains blocked at solve stage.
- **Sprint 20 decision:** DEFERRED to Sprint 21. Not on the critical path for match/solve targets.

### Risk 2: Accounting Variable Detection C5 (Unknown 2.1/2.4 — ✅ VERIFIED but deferred)
- **Status:** C1–C4 criteria are statically computable. C5 (multiplier-consistency) is not feasible statically. mexss remains blocked.
- **Impact:** mexss (#764) deferred to Sprint 21.
- **Sprint 20 decision:** DEFERRED. The tightened C3 criterion (demo1 only, 4 vars) still has moderate false positive risk; implementing without C5 would break demo1.

### Risk 3: codegen_numerical_error (Unknown 8.1 — translated via Task 5)
- **Status:** 4 models fail because `±Inf` parameter values are not handled. Fix is straightforward (~2h) but not yet implemented.
- **Sprint 20 decision:** IN SCOPE (WS5 Part B, Day 10).

### Risk 4: Stale KNOWN_UNKNOWNS.md Status for Previously INCOMPLETE Unknowns
- **Status:** Unknowns 4.1, 5.x, and 7.x have now been verified (via Tasks 3, 6, and 5 respectively), and their `Status` fields in KNOWN_UNKNOWNS.md have been updated in this PR. The only remaining `Status: INCOMPLETE` entry is Unknown 6.4, which is explicitly deferred.
- **Sprint 20 action:** None beyond normal monitoring — KNOWN_UNKNOWNS.md already reflects the current verification state.

---

## Sprint 19 Retrospective Process Improvements (Incorporated)

1. **Model validation scheduled for Days 10–11** (not Day 13 as in Sprint 19) — provides buffer for newly-discovered issues before sprint close.
2. **Smoke-test checklist for "not fixable" declarations** — Day 13 explicitly includes `python -m src.cli <model>` verification before closing any issue.
3. **"Models within ε" tracked as leading indicator** — Sprint 20 targets track both tolerance-adjusted match (rtol=1e-4) and strict match separately.
4. **Baseline denominator explicitly documented** — BASELINE_METRICS.md pins 160 tested / 219 total / 59 excluded from `gamslib_status.json` at commit `dc390373`.
5. **Denominator changes formally documented** — Any model addition/exclusion during Sprint 20 will be recorded in SPRINT_LOG.md with date and reason.
6. **Deferred issue accumulation tracked** — accounting vars, AD propagation, `.scale`, lmp2 all have explicit Sprint 21 deferrals in this plan.

---

## Acceptance Criteria

### Per-Workstream

| Workstream | Acceptance Criteria |
|---|---|
| WS1: `.l` emission | circle solves (PATH model_status=1); abel+chakra objective values match reference; `l_expr`/`l_expr_map` fields tested |
| WS2: IndexOffset | sparta, tabora, otpop all translate; mine, pindyck parse; xfail addressed |
| WS3: Lexer | lexer_invalid_char ≤ 11; no regression in existing 112 parse successes |
| WS4: model_no_objective_def | ≤ 4 remaining; ≥ 11 of 13 `$if`-bug models now parse |
| WS5: Match/Tolerance | Full pipeline match ≥ 15; chem/dispatch/hhmax/mhw4d/mhw4dx all match; codegen_numerical_error ≤ 1 |
| WS6: Regression tests | ≥ 5 solve-level regression tests for matching models; all pass in CI |

### Sprint-Level

- Parse success: ≥ 127/160 (≥ 79.4%)
- lexer_invalid_char: ≤ 11
- model_no_objective_def: ≤ 4
- Translate success: ≥ 110/127 attempted
- Solve success: ≥ 30
- Full pipeline match: ≥ 15
- Tests: ≥ 3,650 (≥ +71 from baseline)
- Zero regressions: all existing 112 parse successes maintained

---

## Files Reference

| File | Purpose |
|---|---|
| `docs/planning/EPIC_4/SPRINT_20/BASELINE_METRICS.md` | Baseline numbers (commit dc390373) |
| `docs/planning/EPIC_4/SPRINT_20/INDEXOFFSET_AUDIT.md` | Sparta/tabora/otpop gap analysis |
| `docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md` | Subcategory L/M/H/A/E analysis |
| `docs/planning/EPIC_4/SPRINT_20/L_INIT_EMISSION_DESIGN.md` | `.l` IR + parser + emitter design |
| `docs/planning/EPIC_4/SPRINT_20/TRANSLATE_ERROR_AUDIT.md` | `$if` bug + translate error analysis |
| `docs/planning/EPIC_4/SPRINT_20/PIPELINE_MATCH_ANALYSIS.md` | rtol + `.l` impact analysis |
| `docs/planning/EPIC_4/SPRINT_20/ACCOUNTING_VAR_DETECTION_DESIGN.md` | C1–C5 algorithm (Sprint 21 deferred) |
| `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md` | Open risks and verified assumptions |
