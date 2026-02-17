# Sprint 19 Log

**Sprint:** 19 (Epic 4)
**Start Date:** 2026-02-13
**Duration:** 14 working days + Day 0 setup
**Estimated Effort:** 43-53 hours (~3-4h/day effective capacity)
**Risk Level:** MEDIUM-HIGH

## Baseline Metrics (Verified Day 0)

| Metric | Baseline |
|--------|----------|
| Parse success | 61/159 (38.4%) |
| lexer_invalid_char | 72 |
| internal_error (pipeline) | 24 |
| Translate success | 48 |
| Solve success | 20 |
| Full pipeline match | 7 |
| path_syntax_error | 6 |
| Test count | 3,294 |

## Sprint Targets

| Metric | Baseline | Day 6 Target | Day 11 Target | Day 14 Target |
|--------|----------|-------------|--------------|--------------|
| Parse success | 61/159 (38.4%) | 75/159 (47.2%) | 87/159 (54.7%) | >=87/159 (>=55%) |
| lexer_invalid_char | 72 | <=59 | <=30 | <30 |
| internal_error (pipeline) | 24 | <=5 | <=3 | <=3 |
| Translate success | 48 | 52+ | 55+ | 55+ |
| Solve success | 20 | 23+ | 25+ | 25+ |
| Full pipeline match | 7 | 9+ | 10+ | 10+ |
| path_syntax_error | 6 | <=2 | <=2 | <=2 |
| Test count | 3,294 | 3,310+ | 3,340+ | 3,350+ |
| Regressions | 0 | 0 | 0 | 0 |

---

## Day 0 — Sprint Initialization

**Date:** 2026-02-13
**Time Spent:** ~0.5h

### Summary

Initialized Sprint 19 infrastructure. Verified all 10 prep task deliverables are present on `main`, confirmed test suite green (3,294 passed, 10 skipped, 1 xfailed in 38.86s), and created this SPRINT_LOG.md.

### Verification Results

**Prep Task Deliverables (10/10 confirmed):**
- `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md`
- `docs/planning/EPIC_4/SPRINT_19/INTERNAL_ERROR_ANALYSIS_PREP.md`
- `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md`
- `docs/planning/EPIC_4/SPRINT_19/ISSUE_670_DESIGN.md`
- `docs/planning/EPIC_4/SPRINT_19/DEFERRED_ITEMS_AUDIT.md`
- `docs/planning/EPIC_4/SPRINT_19/INDEX_OFFSET_DESIGN_OPTIONS.md`
- `docs/planning/EPIC_4/SPRINT_19/TABLE_PARSING_ANALYSIS.md`
- `docs/planning/EPIC_4/SPRINT_19/ISSUE_672_ANALYSIS.md`
- `docs/planning/EPIC_4/SPRINT_19/BASELINE_METRICS.md`
- `docs/planning/EPIC_4/SPRINT_19/PLAN.md`

**Test Suite:** 3,294 passed, 10 skipped, 1 xfailed (38.86s)

**Deviations from Expected State:** None. All deliverables present, all tests pass, baseline metrics match BASELINE_METRICS.md.

### Key Decisions
- Baseline confirmed at 61/159 (38.4%) parse rate, matching BASELINE_METRICS.md exactly
- No deviations from expected state; sprint ready to proceed on schedule

---

## Day 1 — Setup + Quick Wins + Checkpoint 0

**Date:** 2026-02-13
**Time Spent:** ~3h

### Summary

Verified baseline, updated error taxonomy with 5 new classification patterns (eliminating all 24 `internal_error` misclassifications), implemented Subcategory G grammar fixes (NUMBER STRING set elements + Table without domain), and confirmed zero regressions.

### Changes

**Grammar fixes (`src/gams/gams_grammar.lark`):**
- Added `NUMBER STRING -> set_element_with_desc` rule for numeric set elements with descriptions (ganges/gangesx/lop)
- Added `table_block` alternative without explicit domain for `Table ID STRING table_content+ SEMI` (weapons)

**Parser updates (`src/ir/parser.py`):**
- Updated `set_element_with_desc` handler for NUMBER STRING case
- Updated `_handle_table_block` to handle missing domain (infer wildcard `("*", "*")`)

**Error taxonomy (`scripts/gamslib/error_taxonomy.py`):**
- Added `VALIDATION_CIRCULAR_DEP` category (17th parse category)
- Added 5 new patterns to `categorize_parse_error()`:
  1. "has no objective function" → `model_no_objective_def` (12 models)
  2. "circular dependency" → `validation_circular_dep` (9 models)
  3. "expects N indices, got M" → `semantic_domain_error` (1 model)
  4. "not declared as a variable" → `semantic_undefined_symbol` (1 model)
  5. "unsupported expression type" → `parser_invalid_expression` (1 model)

**Tests (`tests/gamslib/test_error_taxonomy.py`):**
- Updated category count assertions (16→17, 48→49)
- Added 5 new test cases for new patterns
- Added `VALIDATION_CIRCULAR_DEP` import

**Failure analyzer (`src/reporting/analyzers/failure_analyzer.py`):**
- Added `validation_circular_dep` effort hours (4.0h)

### Checkpoint 0 Assessment

| Criterion | Target | Actual | Met? |
|-----------|--------|--------|------|
| All tests pass | 3294+ | 3299 | YES |
| Pipeline matches baseline | verified | verified | YES |
| internal_error reclassified | 24 → ≤3 | 24 → 0 | YES (exceeded) |
| Subcategory G models parsing | 4 new | +1 new (+3 reclassified to lexer_invalid_char) | PARTIAL |
| Regressions | 0 | 0 | YES |

### Metrics Snapshot

| Metric | Baseline | Day 1 | Change |
|--------|----------|-------|--------|
| Parse success | 61/159 | 62/160 | +1 |
| lexer_invalid_char | 72 | 72 | 0 |
| internal_error | 24 | 0 | -24 |
| Translate success | 48 | 49 | +1 |
| Solve success | 20 | 20 | 0 |
| Test count | 3,294 | 3,299 | +5 |

### Notes
- The 4 Subcategory G models (ganges, gangesx, lop, weapons) all advance past their original set element description errors, but hit new unrelated lexer errors deeper in their files (tab characters, backslash, percent sign). The grammar fixes are working correctly.
- All 24 former `internal_error` models are now properly classified: 12 `model_no_objective_def`, 9 `validation_circular_dep`, 3 `semantic_undefined_symbol`, 1 `semantic_domain_error`, 1 `parser_invalid_expression`. This exceeds the Day 6 target of ≤5 and the Day 14 target of ≤3.

---

## Day 2 — Put Statement Format + Reserved Word Quoting

**Date:** 2026-02-16
**Time Spent:** ~3h

### PR Entries

- **PR #XXX** — Sprint 19 Day 2: Put Statement Format + Reserved Word Quoting
  - Grammar: Added `put_format` rule (`:width:decimals` specifiers) and `put_stmt_nosemi` variant
  - Emit: Added `GAMS_RESERVED_CONSTANTS` set; reserved words (inf, na, eps, etc.) quoted in `_quote_indices()` and `_sanitize_set_element()`
  - 6 models get past put format parse errors (apl1pca, prodsp2, ps5_s_mn, ps10_s, ps10_s_mn, stdcge)
  - ps2_f family (5 models) now emit correctly quoted reserved constants

### Decisions

- Reserved constant check takes priority over domain_vars context in `_quote_indices()` — a domain variable should never be named `inf`, `na`, etc.
- `eff` is NOT a GAMS reserved constant; it's a regular identifier that is correctly handled by existing heuristics

### Metrics Snapshot

| Metric | Baseline | Day 2 |
|--------|----------|-------|
| Parse success | 61/159 | 63/159 (database, pre-reparse) |
| lexer_invalid_char | 72 | 69 (database, pre-reparse) |
| internal_error | 24 | 2 |
| Test count | 3,294 | 3,386 |

---

## Day 3 — Special Values + Circle Model Fix

**Date:** 2026-02-16
**Time Spent:** ~3h

### Summary

Extended grammar to support GAMS special values (`na`, `inf`, `eps`, `undf`) in scalar data blocks and indexed parameter data. This unblocked 4 models: ship, tforss, ferts (all blocked on `na` in scalar data), and lands (blocked on `na` in indexed parameter data). Added deterministic random seed injection (`execseed`) for MCP files containing stochastic function calls (`uniform`, `normal`), fixing the non-deterministic behavior of the circle model MCP. The circle MCP is now deterministic but remains locally infeasible due to a deeper KKT formulation issue (separate from the randomness fix).

### Changes

- **Grammar:** Extended `scalar_data_item` rule to accept `SPECIAL_VALUE | MINUS SPECIAL_VALUE | PLUS SPECIAL_VALUE` (was `NUMBER` only)
- **Grammar:** Changed `param_data_scalar` rule from `data_indices NUMBER` to `data_indices param_data_value` for special value support
- **Parser:** Updated `_process_scalar_item()` to walk `scalar_data_item` children and handle SPECIAL_VALUE tokens via `_parse_table_value()`
- **Parser:** Updated `param_data_scalar` handler to use `_parse_param_data_value()` for Tree nodes
- **Emit:** Added `STOCHASTIC_FUNCTIONS` set, `_expr_contains_stochastic()`, and `has_stochastic_parameters()` in `original_symbols.py`
- **Emit:** Added `execseed = 12345;` injection in `emit_gams.py` before stochastic parameter assignments
- **Tests:** 18 new tests (8 scalar/param special values + 10 stochastic detection/execseed)

### Decisions

- Used `execseed = 12345;` (GAMS execution-time statement) rather than `option seed = 12345;` (option statement) for random seed control
- Circle MCP infeasibility is a KKT formulation issue, not a randomness issue — the execseed fix makes it deterministic but doesn't resolve the infeasibility. Deeper KKT fix deferred.
- Catalog said 3 grammar-fixable models (ferts, gussrisk, lands), but actual diagnostics revealed 4 models blocked on special values (ship, tforss, ferts, lands) while gussrisk is blocked on GUSS syntax (compound set data + scenario solve extension)

### PR Entries

- PR: Sprint 19 Day 3: Special Values Grammar + Circle Model Deterministic Fix

### Metrics Snapshot

| Metric | Baseline | Day 3 |
|--------|----------|-------|
| Parse success | 61/159 | 65/159 (+4: ship, tforss, ferts, lands past grammar stage) |
| lexer_invalid_char | 72 | 68 (-4) |
| internal_error | 24 | 24 |
| Test count | 3,294 | 3,413 (+119 cumulative from Day 0) |

---

## Day 4 — ISSUE_672: MCP Case Sensitivity Fix

**Date:** 2026-02-16
**Time Spent:** ~2h

### Summary
Fixed ISSUE_672: VarRef names normalized to lowercase at parse time in `src/ir/parser.py`
(3 locations). Resolves case sensitivity mismatch between `CaseInsensitiveDict.keys()`
(lowercase) and VarRef node names (original case), which caused all stationarity derivatives
to return zero for mixed-case models (alkyl, bearing).

### Changes
- `src/ir/parser.py`: Added `.lower()` normalization at all 3 VarRef creation points
- `tests/unit/ad/test_mixed_case_differentiation.py`: 13 new unit + integration tests

### PR Entries

- Sprint 19 Day 4: ISSUE_672 — MCP Case Sensitivity Fix (PR #756)

### Metrics Snapshot

| Metric | Baseline | Day 4 |
|--------|----------|-------|
| Parse success | 61/159 | 61/159 (unchanged) |
| lexer_invalid_char | 72 | 72 (unchanged) |
| internal_error | 24 | 24 (unchanged) |
| Test count | 3,294 | 3,479 (+185 cumulative from Day 0; +13 this day) |

---

## Day 5 — ISSUE_670: Cross-Indexed Sums (Part 1)

**Date:** 2026-02-17
**Time Spent:** ~3h

### Summary
Implemented `_collect_free_indices()` utility in `src/kkt/stationarity.py` and integrated
it into `_add_indexed_jacobian_terms()`. After the existing domain-based sum wrapping,
any remaining free indices in the derivative expression (not in var_domain ∪ mult_domain)
are now wrapped in a Sum node, avoiding GAMS Error 149 ("Uncontrolled set entered as constant").

abel model now generates without Error 149 — GAMS parsing succeeds.

### Changes
- `src/kkt/stationarity.py`: Added `_collect_free_indices()` + integration in `_add_indexed_jacobian_terms()`
- `tests/unit/kkt/test_collect_free_indices.py`: 37 unit tests (initial 19 + 18 added during PR review rounds covering MultiplierRef, SetMembershipTest/SymbolRef, mixed-case binding, and IndexOffset lead/lag expressions)

### PR Entries

- Sprint 19 Day 5: ISSUE_670 — Cross-Indexed Sums Part 1 (PR #758)

### Metrics Snapshot

| Metric | Baseline | Day 5 |
|--------|----------|-------|
| Parse success | 61/159 | 61/159 (unchanged) |
| lexer_invalid_char | 72 | 72 (unchanged) |
| internal_error | 24 | 24 (unchanged) |
| Test count | 3,294 | 3,516 (+222 cumulative; +37 this day) |

---

## Day 6 — ISSUE_670: Cross-Indexed Sums (Part 2) + Checkpoint 1

**Date:**
**Time Spent:**

### PR Entries

_(To be filled during Day 6)_

### Checkpoint 1 Assessment

| Criterion | Target | Actual | Met? |
|-----------|--------|--------|------|
| New models parsing | >=13 | | |
| internal_error reclassified | 24 -> 3 | | |
| ISSUE_672 fixed | alkyl/bearing | | |
| ISSUE_670 on abel | validated | | |
| circle model | model_optimal | | |
| path_syntax_error | <=2 | | |
| Regressions | 0 | | |
| Parse rate | 47%+ | | |

**Go/No-Go Decision:**

### Metrics Snapshot

| Metric | Baseline | Day 6 |
|--------|----------|-------|
| Parse success | 61/159 | |
| lexer_invalid_char | 72 | |
| internal_error | 24 | |
| Translate success | 48 | |
| Solve success | 20 | |
| Full pipeline match | 7 | |
| Test count | 3,294 | |

---

## Day 7 — ISSUE_670 Wrap-up + House Model Investigation

**Date:**
**Time Spent:**

### PR Entries

_(To be filled during Day 7)_

### Metrics Snapshot

| Metric | Baseline | Day 7 |
|--------|----------|-------|
| Parse success | 61/159 | |
| lexer_invalid_char | 72 | |
| internal_error | 24 | |
| Test count | 3,294 | |

---

## Day 8 — Tuple/Compound Set Data Grammar (Part 1)

**Date:**
**Time Spent:**

### PR Entries

_(To be filled during Day 8)_

### Metrics Snapshot

| Metric | Baseline | Day 8 |
|--------|----------|-------|
| Parse success | 61/159 | |
| lexer_invalid_char | 72 | |
| internal_error | 24 | |
| Test count | 3,294 | |

---

## Day 9 — Tuple/Compound Set Data (Part 2) + Model/Solve Issues

**Date:**
**Time Spent:**

### PR Entries

_(To be filled during Day 9)_

### Metrics Snapshot

| Metric | Baseline | Day 9 |
|--------|----------|-------|
| Parse success | 61/159 | |
| lexer_invalid_char | 72 | |
| internal_error | 24 | |
| Test count | 3,294 | |

---

## Day 10 — Table Parsing (ISSUE_392/399) + Subset Verification

**Date:**
**Time Spent:**

### PR Entries

_(To be filled during Day 10)_

### Metrics Snapshot

| Metric | Baseline | Day 10 |
|--------|----------|--------|
| Parse success | 61/159 | |
| lexer_invalid_char | 72 | |
| internal_error | 24 | |
| Test count | 3,294 | |

---

## Day 11 — Declaration/Syntax Gaps + Checkpoint 2

**Date:**
**Time Spent:**

### PR Entries

_(To be filled during Day 11)_

### Checkpoint 2 Assessment

| Criterion | Target | Actual | Met? |
|-----------|--------|--------|------|
| Parse rate | >=55% | | |
| lexer_invalid_char | <30 | | |
| internal_error | <15 | | |
| FIX_ROADMAP P1-P3 | complete | | |
| ISSUE_672 | resolved | | |
| circle + house | confirmed | | |
| Regressions | 0 | | |

**Go/No-Go Decision:**

### Metrics Snapshot

| Metric | Baseline | Day 11 |
|--------|----------|--------|
| Parse success | 61/159 | |
| lexer_invalid_char | 72 | |
| internal_error | 24 | |
| Translate success | 48 | |
| Solve success | 20 | |
| Full pipeline match | 7 | |
| Test count | 3,294 | |

---

## Day 12 — IndexOffset AD Integration (Part 1)

**Date:**
**Time Spent:**

### PR Entries

_(To be filled during Day 12)_

### Metrics Snapshot

| Metric | Baseline | Day 12 |
|--------|----------|--------|
| Parse success | 61/159 | |
| lexer_invalid_char | 72 | |
| internal_error | 24 | |
| Test count | 3,294 | |

---

## Day 13 — IndexOffset Validation + Lead/Lag Grammar

**Date:**
**Time Spent:**

### PR Entries

_(To be filled during Day 13)_

### Metrics Snapshot

| Metric | Baseline | Day 13 |
|--------|----------|--------|
| Parse success | 61/159 | |
| lexer_invalid_char | 72 | |
| internal_error | 24 | |
| Test count | 3,294 | |

---

## Day 14 — Final Pipeline Retest + Documentation + Sprint Close

**Date:**
**Time Spent:**

### PR Entries

_(To be filled during Day 14)_

### Final Metrics

| Metric | Baseline | Final | Change |
|--------|----------|-------|--------|
| Parse success | 61/159 (38.4%) | | |
| lexer_invalid_char | 72 | | |
| internal_error (pipeline) | 24 | | |
| Translate success | 48 | | |
| Solve success | 20 | | |
| Full pipeline match | 7 | | |
| path_syntax_error | 6 | | |
| Test count | 3,294 | | |
| Regressions | 0 | | |

### Final Acceptance Criteria

| Criterion | Target | Actual | Met? |
|-----------|--------|--------|------|
| lexer_invalid_char | <30 | | |
| internal_error (parse) | <15 | | |
| Parse rate | >=55% | | |
| IndexOffset AD | complete | | |
| FIX_ROADMAP P1-P3 | resolved | | |
| Zero regressions | yes | | |
| circle + house solve | yes | | |
| Put statement models parse | yes | | |

### Retrospective

_(To be filled on Day 14)_

---

## Sprint Summary

_(To be filled on sprint completion)_
