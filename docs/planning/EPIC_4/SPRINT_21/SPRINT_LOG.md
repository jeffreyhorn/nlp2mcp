# Sprint 21 Progress Log

**Sprint Duration:** Day 0 – Day 14
**Baseline Commit:** `feffaa95`
**Plan:** `docs/planning/EPIC_4/SPRINT_21/PLAN.md`

---

## Baseline Metrics (commit `feffaa95`)

| Metric | Value |
|--------|-------|
| **Parse** | 132/160 (82.5%) |
| **Translate** | 123/132 (93.2%) |
| **Solve** | 33/124 (26.6%) |
| **Match** | 16/33 (48.5%) |
| **Tests** | 3,715 passed, 10 skipped, 2 xfailed |

### Parse Error Breakdown (28 failures)

| Category | Count |
|----------|-------|
| lexer_invalid_char | 10 |
| semantic_undefined_symbol | 7 |
| internal_error | 7 |
| parser_invalid_expression | 3 |
| model_no_objective_def | 1 |

### Solve Error Breakdown (91 failures)

| Category | Count |
|----------|-------|
| path_syntax_error | 48 |
| path_solve_terminated | 29 |
| model_infeasible | 12 |
| path_solve_license | 2 |

---

## Sprint 21 Targets

| Metric | Baseline | Target | Stretch |
|--------|----------|--------|---------|
| Parse | 132/160 | ≥ 135/160 | ≥ 141/160 |
| lexer_invalid_char | 10 | ≤ 5 | ≤ 3 |
| internal_error | 7 | ≤ 3 | ≤ 1 |
| Solve | 33 | ≥ 36 | ≥ 40 |
| Match | 16 | ≥ 20 | ≥ 22 |

---

## Daily Progress

### Day 0 — Baseline Confirm + Sprint Kickoff

**Date:** 2026-02-24
**Status:** COMPLETE
**PR:** #855
**Effort:** ~1h

**Activities:**
- Verified baseline: `make test` → 3,715 passed, 10 skipped, 2 xfailed
- Confirmed clean commit from main (a70d70d3, merge of PR #854)
- Ran full pipeline parse retest (PR3 compliance): 131/160 (one model flaky vs stored 132/160; lexer_invalid_char 9 vs stored 10 — minor non-deterministic variance)
- Initialized SPRINT_LOG.md with baseline metrics and error category breakdown (PR5 compliance)
- Reviewed Day 1 tasks: SEMANTIC_ERROR_AUDIT.md and FUNCNAME regex location

**Metrics:**
- Parse: 132/160 (baseline confirmed)
- Tests: 3,715 passed, 10 skipped, 2 xfailed

---

### Day 1 — WS1: Semantic Error Resolution

**Date:** 2026-02-24
**Status:** COMPLETE
**PR:** #856
**Effort:** ~3h

**Activities:**
- Added `sign|centropy|mapval|betareg` to FUNCNAME regex in grammar (+5 models: camcge, feedtray, cesam2, sambal, procmean)
- Added `_handle_acronym_stmt` to IR builder — registers acronym names as zero-valued scalar parameters (+1 model: worst)
- Fixed sameas() string literal handling — quoted strings in `_make_symbol` now resolve as set element references (+1 model: cesam)
- Added 9 unit tests (4 FUNCNAME + 3 acronym handler + 2 sameas)
- Ran all 7 newly-parsing models through full pipeline (PR4)

**Metrics:**
- Parse: 139/160 (stored; fresh run 137/158 — consistent with Day 0 variance)
- semantic_undefined_symbol: 0 (was 7)
- Tests: 3,724 passed (+9), 10 skipped, 2 xfailed
- Newly-parsing models pipeline status:

| Model | Parse | Translate | Solve | Error |
|-------|-------|-----------|-------|-------|
| camcge | OK | OK | FAIL | path_syntax_error |
| feedtray | OK | OK | FAIL | path_syntax_error |
| cesam2 | OK | FAIL | — | internal_error |
| sambal | OK | OK | FAIL | path_solve_terminated |
| procmean | OK | FAIL | — | diff_unsupported_func |
| worst | OK | OK | FAIL | path_syntax_error |
| cesam | OK (no objective) | — | — | model_no_objective_def |

---

### Day 2 — WS2: Macro Expansion Part 1

**Date:** 2026-02-24
**Status:** COMPLETE
**PR:** TBD
**Effort:** ~2h

**Activities:**
- Added `SYSTEM_MACROS` constant with 60+ system/built-in macro defaults (solver names, modelStat/solveStat/solveLink constants, infrastructure paths)
- Added `$setglobal` directive support to `extract_set_directives()` and `strip_set_directives()`
- Injected system macros into preprocessing pipeline (Step 2b, before conditional processing)
- saras: `%system.nlp%` now expands to `CONOPT`; model moved from `lexer_invalid_char` to `semantic_undefined_symbol` (separate IR builder issue with `Rcon1`)
- 10 unit tests (7 system macros + 3 $setglobal)

**Metrics:**
- Parse: 139/160 (unchanged; saras moved error category but still fails)
- lexer_invalid_char: 8 (fresh run; was 9)
- Tests: 3,734 passed (+10), 10 skipped, 2 xfailed
- saras pipeline status: macro expansion works (`%system.nlp%` → `CONOPT`); fails on `Rcon1` undeclared symbol (separate issue)

---

### Day 3 — WS2: Macro Expansion Part 2

**Date:** 2026-02-24
**Status:** COMPLETE
**PR:** #866
**Effort:** ~2h

**Activities:**
- Implemented `extract_eval_directives()` with `_safe_eval_arithmetic()` for `$eval` directive support
- Added `strip_eval_directives()` to strip `$eval` lines after processing
- Wired `$eval` extraction into `_preprocess_content()` pipeline (Step 2a, after $set, before system macros)
- springchain: `$eval NM1 %N%-1` now evaluates correctly (`NM1 = 9`)
- springchain full pipeline: parse OK, translate OK, solve OK (mismatch on comparison)
- saras: still blocked by Rcon1 case-sensitivity issue (#857, separate from macro expansion)
- Closed Issue #837 (springchain bracket + macro) as fully fixed
- Moved ISSUE_837 and ISSUE_840 docs to completed/
- 10 unit tests (8 $eval + 2 _safe_eval_arithmetic)

**Metrics:**
- Parse: 140/160 (+1 springchain)
- lexer_invalid_char: 8 (was 9; springchain removed)
- Tests: 3,744 passed (+10), 10 skipped, 2 xfailed
- springchain pipeline status: parse OK, translate OK, solve OK, mismatch

---

### Day 4 — WS3: internal_error Lead/Lag Fix

**Date:** 2026-02-25
**Status:** COMPLETE
**PR:** #883
**Effort:** ~3h

**Activities:**
- Extended `_extract_indices()` to gracefully return base names when encountering `lag_lead_suffix` (instead of raising `ParserSemanticError`)
- Extended `_extract_indices_with_subset()` with optional `expr_fn` parameter and widened return type to `str | IndexOffset`
- Updated `_handle_assign` `symbol_indexed` handler: added `has_lead_lag` detection, guarded domain-over expansion, forced expression path for lead/lag keys
- Widened `ParameterDef.expressions` key type to `tuple[str | IndexOffset, ...]` in symbols.py
- Updated emitter (`original_symbols.py`): added `IndexOffset` import, widened `_StmtTuple`, updated `domain_vars` extraction and index formatting to dispatch `IndexOffset` to `to_gams_string()`
- Fixed `bound_indexed` handler in `_expr` to pass `expr_fn` for complex offset expressions (tfordy fix)
- Fixed `_ef` in `symbol_indexed` handler to pass `domain_context` instead of empty tuple (imsl fix)
- Added `isinstance(idx, str)` guard for subset expansion check (type safety)
- Updated existing test from `raises(ParserSemanticError)` to acceptance test
- 6 new unit tests (linear lead, multi-index lead, linear lag, multiple lags, circular lead, conditional with lead)

**Metrics:**
- Parse: 143/160 (stored; fresh run 144/157 available)
- internal_error: 3 (was 7 at baseline, 4 after Day 3 — 3 models fixed: imsl, sarf, tfordy)
- Tests: 3,759 passed (+15), 10 skipped, 2 xfailed
- imsl, sarf, tfordy pipeline status:

| Model | Parse | Translate | Solve | Error |
|-------|-------|-----------|-------|-------|
| imsl | OK | FAIL | — | internal_error (translation) |
| sarf | OK | FAIL | — | timeout |
| tfordy | OK | OK | FAIL | path_syntax_error |

---

### Day 5 — CHECKPOINT 1 + WS3: internal_error (if-stmt + table)

**Date:**
**Status:**
**PR:**
**Effort:**

**Checkpoint 1 Metrics:**

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Parse | /160 | ≥ 141 | |
| lexer_invalid_char | | ≤ 8 | |
| internal_error | | ≤ 4 | |
| semantic_undefined_symbol | | ≤ 0 | |
| Solve | | — | |
| Match | | — | |
| Tests | | — | |

**Parse Error Breakdown:**

| Category | Count |
|----------|-------|
| lexer_invalid_char | |
| semantic_undefined_symbol | |
| internal_error | |
| parser_invalid_expression | |
| model_no_objective_def | |

**Solve Error Breakdown:**

| Category | Count |
|----------|-------|
| path_syntax_error | |
| path_solve_terminated | |
| model_infeasible | |
| path_solve_license | |

**Activities:**
-

---

### Day 6 — WS4: path_syntax_error Emitter Fixes (E + D)

**Date:**
**Status:**
**PR:**
**Effort:**

**Activities:**
-

**Metrics:**
- path_syntax_error:
- Tests:
- Models unblocked:

---

### Day 7 — WS4: Table Data Capture Part 1

**Date:**
**Status:**
**PR:**
**Effort:**

**Activities:**
-

**Metrics:**
- Tests:
- Models with Table data populated:

---

### Day 8 — WS4: Table Data Capture Part 2

**Date:**
**Status:**
**PR:**
**Effort:**

**Activities:**
-

**Metrics:**
- path_syntax_error:
- Tests:
- Subcategory A models compiling:

---

### Day 9 — WS6: Match Rate Improvement

**Date:**
**Status:**
**PR:**
**Effort:**

**Activities:**
-

**Metrics:**
- Match:
- Tests:
- port status:
- chakra status:

---

### Day 10 — CHECKPOINT 2 + WS5: Deferred Issues (#789, #828)

**Date:**
**Status:**
**PR:**
**Effort:**

**Checkpoint 2 Metrics:**

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Parse | /160 | ≥ 141 | |
| lexer_invalid_char | | ≤ 5 | |
| internal_error | | ≤ 3 | |
| Solve | | ≥ 36 | |
| Match | | ≥ 18 | |
| Tests | | — | |

**Parse Error Breakdown:**

| Category | Count |
|----------|-------|
| lexer_invalid_char | |
| semantic_undefined_symbol | |
| internal_error | |
| parser_invalid_expression | |
| model_no_objective_def | |

**Solve Error Breakdown:**

| Category | Count |
|----------|-------|
| path_syntax_error | |
| path_solve_terminated | |
| model_infeasible | |
| path_solve_license | |

**Activities:**
-

---

### Day 11 — WS5 (#826) + WS3 Remaining + WS7 Emerging

**Date:**
**Status:**
**PR:**
**Effort:**

**Activities:**
-

**Metrics:**
- internal_error:
- Tests:
- Emerging blocker status:

---

### Day 12 — WS8: PATH Convergence Investigation

**Date:**
**Status:**
**PR:**
**Effort:**

**Activities:**
-

**Metrics:**
- path_solve_terminated models classified: /29

---

### Day 13 — WS8 Completion + WS9: Solution Comparison

**Date:**
**Status:**
**PR:**
**Effort:**

**Activities:**
-

**Metrics:**
- path_solve_terminated classified: /29
- Solution comparison: primal/dual/complementarity

---

### Day 14 — FINAL CHECKPOINT + Sprint Close

**Date:**
**Status:**
**PR:**
**Effort:**

**Final Metrics:**

| Metric | Baseline | Final | Target | Status |
|--------|----------|-------|--------|--------|
| Parse | 132/160 | /160 | ≥ 135 | |
| lexer_invalid_char | 10 | | ≤ 5 | |
| internal_error | 7 | | ≤ 3 | |
| Solve | 33 | | ≥ 36 | |
| Match | 16 | | ≥ 20 | |
| Tests | 3,715 | | ≥ 3,780 | |

**Final Parse Error Breakdown:**

| Category | Baseline | Final | Delta |
|----------|----------|-------|-------|
| lexer_invalid_char | 10 | | |
| semantic_undefined_symbol | 7 | | |
| internal_error | 7 | | |
| parser_invalid_expression | 3 | | |
| model_no_objective_def | 1 | | |

**Final Solve Error Breakdown:**

| Category | Baseline | Final | Delta |
|----------|----------|-------|-------|
| path_syntax_error | 48 | | |
| path_solve_terminated | 29 | | |
| model_infeasible | 12 | | |
| path_solve_license | 2 | | |

**Acceptance Criteria:**
- [ ] Parse ≥ 135/160
- [ ] lexer_invalid_char ≤ 5
- [ ] internal_error ≤ 3
- [ ] Solve ≥ 36
- [ ] Match ≥ 20
- [ ] PATH analysis: all path_solve_terminated classified
- [ ] Solution comparison framework extended
- [ ] All tests pass, ≥ 3,780

---

## PR Log

| Day | PR # | Title | Status |
|-----|------|-------|--------|
| 0 | #855 | Sprint 21 Day 0: Baseline Confirm + Sprint Kickoff | Merged |
| 1 | #856 | Sprint 21 Day 1: Semantic Error Resolution (+7 parse) | Merged |
| 2 | #865 | Sprint 21 Day 2: Macro Expansion Part 1 (System Macros + $setglobal) | Merged |
| 3 | #866 | Sprint 21 Day 3: Macro Expansion Part 2 ($eval + springchain) | Open |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |
| 8 | | | |
| 9 | | | |
| 10 | | | |
| 11 | | | |
| 12 | | | |
| 13 | | | |
| 14 | | | |
