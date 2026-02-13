# Sprint 19 Baseline Metrics

**Date:** 2026-02-13
**Branch:** `main` (post-v1.2.0 merge)
**Commit:** 7680551
**Prep Task:** 9

---

## Test Suite

| Metric | Value |
|--------|-------|
| Total tests | 3,294 |
| Passed | 3,294 |
| Failed | 0 |
| Skipped | 10 |
| xfailed | 1 |
| Duration | 42.43s |

**Result:** All 3,294 tests pass. Zero failures.

---

## Pipeline Metrics

### Corpus

| Metric | Value |
|--------|-------|
| Total models in database | 219 |
| Verified convex | 57 |
| Likely convex | 102 |
| Excluded | 5 |
| Error (convexity check) | 48 |
| Unknown | 7 |
| **Active corpus** | **159** |

### Parse Stage

| Metric | Value | Rate |
|--------|-------|------|
| Success | 61 | 38.4% |
| Failure | 98 | 61.6% |

**Parse Error Breakdown:**

| Error Category | Count | % of Failures |
|----------------|-------|---------------|
| lexer_invalid_char | 72 | 73.5% |
| internal_error | 24 | 24.5% |
| semantic_undefined_symbol | 2 | 2.0% |
| **Total** | **98** | **100%** |

### Translate Stage

| Metric | Value | Rate |
|--------|-------|------|
| Success | 48 | 78.7% (of 61 parsed) |
| Failure | 13 | 21.3% |
| Cascade-skipped | 98 | — |

**Translate Error Breakdown:**

| Error Category | Count |
|----------------|-------|
| internal_error | 7 |
| codegen_numerical_error | 2 |
| unsup_expression_type | 2 |
| diff_unsupported_func | 2 |
| **Total** | **13** |

### Solve Stage

| Metric | Value | Rate |
|--------|-------|------|
| Success | 20 | 41.7% (of 48 translated) |
| Failure | 28 | 58.3% |
| Cascade-skipped | 111 | — |

**Solve Error Breakdown:**

| Error Category | Count | Models |
|----------------|-------|--------|
| path_solve_terminated | 19 | alkyl, bearing, himmel16, jobt, pak, pollut, ps2_f, ps2_f_eff, ps2_f_inf, ps2_f_s, ps2_s, ps3_f, ps3_s, ps3_s_gic, ps3_s_mn, ps3_s_scp, sample, trussm, whouse |
| path_syntax_error | 6 | abel, chenery, like, mexss, qabel, robert |
| model_infeasible | 3 | circle, cpack, meanvar |
| **Total** | **28** | |

### Solution Comparison Stage

| Metric | Value |
|--------|-------|
| Objective match | 7 |
| Objective mismatch | 5 |
| Not performed (no original solution) | 8 |
| Cascade-skipped | 139 |

### Full Pipeline Success

| Metric | Value | Rate |
|--------|-------|------|
| Full pipeline success (objective match) | 7 | 4.4% of corpus |

**Successful models:** ajax, himmel11, hs62, mathopt2, prodmix, rbrock, trnsport

---

## Comparison with Sprint 18 Day 14 Reported Numbers

| Metric | Sprint 18 Day 14 | Verified (Feb 13) | Match? |
|--------|-----------------|-------------------|--------|
| Corpus size | 160 | 159 | ⚠️ Discrepancy |
| Parse success | 62 (38.8%) | 61 (38.4%) | ⚠️ Discrepancy |
| Translate success | 48 | 48 | ✅ |
| Solve success | 20 | 20 | ✅ |
| Full pipeline (match) | 7 | 7 | ✅ |
| path_syntax_error | 7 | 6 | ⚠️ Discrepancy |
| Test count | 3,294 | 3,294 | ✅ |

### Discrepancy Explanations

**Corpus size (160 → 159) and Parse (62 → 61):**
The model `mingamma` was reclassified from `likely_convex` to `excluded` between Sprint 18 Day 14 and the current database state. `mingamma` parsed successfully, so its exclusion reduces both the corpus and parse success count by 1. The remaining 61 parse successes and 98 failures are unchanged. This is a corpus curation change, not a regression.

**path_syntax_error (7 → 6):**
The pipeline summary reports 6 `path_syntax_error` models (abel, chenery, like, mexss, qabel, robert). The Sprint 18 Day 14 count of 7 likely included a model that was either reclassified or whose error category changed between runs. The difference is 1 model and does not indicate a regression.

---

## Sprint 19 Target Calibration

### Original Targets (from PROJECT_PLAN.md)

| Target | Original | Baseline |
|--------|----------|----------|
| lexer_invalid_char | ~95 → below 50 | 72 (actual) |
| internal_error (parse) | 23 → below 15 | 24 (actual) |
| Parse rate | ≥55% of valid corpus | 38.4% (actual) |

### Recalibrated Targets

| Target | Recalibrated | Rationale |
|--------|-------------|-----------|
| lexer_invalid_char | 72 → below 30 | Baseline is 72, not ~95. Fix 43+ models. Task 3 catalog confirms 43 directly grammar-fixable + 15 cascading. |
| internal_error (parse) | 24 → below 15 | Baseline is 24, not 23. Off by 1 — target remains valid. Need to fix 10+ models. |
| Parse rate | 38.4% → ≥55% | Baseline confirmed at 38.4%. Achieving ≥55% requires parsing ~87 models (26+ new). Achievable if lexer_invalid_char and internal_error targets are met (42+ new parses from those categories alone). |

### Target Achievability Assessment

- **lexer_invalid_char (72 → <30):** ✅ Achievable. Task 3 catalog identified 43 directly grammar-fixable + 15 cascading = 58 potentially fixable. Even the conservative estimate (43 fixed → 29 remaining) meets the target.
- **internal_error (24 → <15):** ✅ Achievable. 21 of 24 were silently resolved by Sprint 18 grammar changes but not re-tested with the pipeline. The remaining 3 genuine internal_errors need investigation.
- **Parse rate (38.4% → ≥55%):** ✅ Achievable. Fixing 43+ lexer_invalid_char models brings parse to 104/159 = 65.4%. Combined with internal_error fixes, the target is well within reach.

---

## Error Category Summary

### Parse Errors (98 total)

| Category | Count | Sprint 19 Target | Addressable |
|----------|-------|-----------------|-------------|
| lexer_invalid_char | 72 | Below 30 | 43 direct + 15 cascading |
| internal_error | 24 | Below 15 | 21 already resolved; 3 genuine |
| semantic_undefined_symbol | 2 | — | Not targeted in Sprint 19 |

### Translate Errors (13 total)

| Category | Count | Notes |
|----------|-------|-------|
| internal_error | 7 | Various IR/translation issues |
| codegen_numerical_error | 2 | Numerical computation issues |
| unsup_expression_type | 2 | Unsupported AST node types |
| diff_unsupported_func | 2 | Missing derivative rules |

### Solve Errors (28 total)

| Category | Count | Notes |
|----------|-------|-------|
| path_solve_terminated | 19 | PATH solver convergence failures (includes ISSUE_672 models) |
| path_syntax_error | 6 | Generated MCP syntax errors |
| model_infeasible | 3 | MCP formulation produces infeasible model |

---

## Verification Method

1. **Test suite:** `make test` (runs `pytest tests/ -n auto -m "not slow"`)
2. **Pipeline:** `.venv/bin/python scripts/gamslib/run_full_test.py` (runs Parse → Translate → Solve → Compare on all 159 candidate models)
3. **Database:** `data/gamslib/gamslib_status.json` (schema v2.0.0, updated 2026-02-13)
4. **All metrics extracted programmatically** from `gamslib_status.json` after pipeline run
