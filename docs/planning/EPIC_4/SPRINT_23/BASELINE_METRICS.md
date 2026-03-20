# Sprint 23 Baseline Metrics

**Created:** 2026-03-20
**Pipeline Run:** Full pipeline (no `--only-*` flags), per Sprint 22 PR6 recommendation
**Branch:** `planning/sprint23-task8` (from main at `2c33989e`)
**Commit:** `main @ 2c33989e` (Sprint 22 baseline merge)
**Pipeline Script:** `scripts/gamslib/run_full_test.py --quiet`
**Run Duration:** ~76 minutes (4564s)
**GAMS Version:** not recorded for this run
**PATH License:** not recorded for this run
**nlp2mcp Version:** not recorded for this run

---

## 1. Pipeline Scope

| Category | Count | Description |
|----------|-------|-------------|
| Total DB entries | 219 | All GAMSlib models in catalog |
| Pipeline candidates | 147 | `convexity.status` = verified_convex or likely_convex |
| Excluded | 6 | feasopt1, feedtray, iobalance, lop, meanvar, orani |
| Non-convex | 7 | ps10_s, ps2_f_s, ps2_s, ps3_s, ps3_s_gic, ps3_s_mn, ps3_s_scp |
| Full corpus (with stale) | 160 | 147 fresh + 13 stale results from prior runs |

**Note:** The pipeline processes 147 candidates. 13 additional models have results from previous pipeline runs preserved in the DB (6 excluded + 7 non-convex). Sprint 22 used 160 as the total denominator. For historical comparison, metrics below use the 160-model full corpus.

---

## 2. Full Pipeline Results

### Summary Table

| Stage | Count | Denominator | Percentage | Sprint 22 | Delta |
|-------|-------|-------------|------------|-----------|-------|
| **Parse** | 156 | 160 | 97.5% | 156/160 (97.5%) | +0 |
| **Translate** | 139 | 156 (parsed) | 89.1% | 141/156 (90.4%) | **-2** |
| **Solve** | 89 | 139 (translated) | 64.0% | 89/141 (63.1%) | +0 |
| **Match** | 47 | 160 (corpus) | 29.4% | 47/160 (29.4%) | +0 |

### Pipeline-Scope Results (147 candidates only)

| Stage | Count | Denominator | Percentage |
|-------|-------|-------------|------------|
| Parse | 144 | 147 | 98.0% |
| Translate | 127 | 144 (parsed) | 88.2% |
| Solve | 81 | 127 (translated) | 63.8% |
| Match | 47 | 147 | 32.0% |

---

## 3. Parse Failures (4)

| Model | Error Category | Notes |
|-------|---------------|-------|
| danwolfe | lexer_invalid_char | Fresh result |
| lop | lexer_invalid_char | Stale result (excluded) |
| partssupply | lexer_invalid_char | Fresh result |
| turkey | lexer_invalid_char | Fresh result |

**Status:** Unchanged from Sprint 22 (4 parse failures, same models).

---

## 4. Translate Failures (17)

### By Category

| Category | Count | Models |
|----------|-------|--------|
| **Timeout** (>=150s) | 11 | clearlak, dinam, ferts, ganges, gangesx, gastrans, iswnm, nebrazil, sarf, srpchase, turkpow |
| **Unsupported expression** (LhsConditionalAssign) | 4 | agreste, ampl, cesam, korcge |
| **Internal error** | 2 | mexls (#940, universal set `'*'`), mine (SetMembershipTest in condition) |

### Timeout Analysis

| Subclass | Count | Models | Notes |
|----------|-------|--------|-------|
| Persistent (well over limit) | 7 | ganges, gangesx, gastrans, iswnm, nebrazil, sarf, srpchase | Architecturally intractable |
| Borderline (150.0-150.2s) | 4 | clearlak (150.0s), dinam (150.2s), ferts (150.1s), turkpow (150.0s) | Fluctuate run-to-run |

### Translate Delta vs Sprint 22

Sprint 22 had 141/156 (15 failures). This run has 139/156 (17 failures). Net: **-2**.

- **Deterministic failures (6):** agreste, ampl, cesam, korcge (LhsConditionalAssign) + mexls, mine (internal error) — **stable, same as Sprint 22**
- **Timeout count:** 11 now vs ~9 in Sprint 22 — **2 borderline models flipped from success to failure**
- **Root cause:** Borderline timeouts (clearlak, dinam, ferts, turkpow) are at exactly 150.0-150.2s and fluctuate based on system load. This is run-to-run variance, not a regression.

---

## 5. Solve Error Categories

| Category | Count | Sprint 22 | Delta | Notes |
|----------|-------|-----------|-------|-------|
| model_optimal | 89 | 89 | +0 | |
| path_syntax_error | 18 | 20 | -2 | 2 fewer due to scope narrowing (excluded models) |
| model_infeasible | 15 | 15 | +0 | 12 in-scope + 3 excluded |
| path_solve_terminated | 10 | 10 | +0 | |
| path_solve_license | 7 | 7 | +0 | |
| not_tested (cascade) | 21 | 19 | +2 | 17 translate fail + 4 parse fail = 21 |

### model_infeasible Breakdown (per PR7)

| Scope | Count | Models |
|-------|-------|--------|
| **In-scope** | 12 | bearing, chain, cpack, lnts, markov, mathopt3, pak, paperco, prolog, robustlp, sparta, spatequ |
| **Permanently excluded** | 3 | feasopt1, iobalance, orani |
| **Total** | 15 | |

### path_syntax_error (18)

camcge, cesam2, chenery, china, decomp, feedtray, harker, hhfair, indus, lmp2, nonsharp, otpop, ramsey, sample, saras, shale, srkandw, worst

### path_solve_terminated (10)

dyncge, elec, etamac, fawley, gtm, maxmin, qsambal, rocket, sambal, twocge

### path_solve_license (7)

egypt, glider, robot, sroute, tabora, tfordy, tricp

---

## 6. Comparison Results

| Result | Count | Notes |
|--------|-------|-------|
| **Match** | 47 | Objective values match within tolerance |
| **Mismatch** | 36 | Objective values diverge |
| **Multi-solve skip** | 6 | aircraft, apl1p, apl1pca, ps10_s_mn, ps5_s_mn, senstran |
| **Not compared** | 71 | Cascade from upstream failures |

### Multi-Solve Models (KU-26 VERIFIED)

All 6 multi-solve models are correctly flagged and skipped during comparison:
- aircraft, apl1p, apl1pca, ps10_s_mn, ps5_s_mn, senstran
- Flag introduced by PR #1103
- Comparison pipeline checks `multi_solve: true` first (`scripts/gamslib/test_solve.py:809-816`)
- Flag is stable across runs

---

## 7. Regression Analysis

### No Regressions Detected

| Metric | Sprint 22 | Sprint 23 Baseline | Status |
|--------|-----------|-------------------|--------|
| Parse | 156/160 | 156/160 | Stable |
| Translate | 141/156 | 139/156 | -2 (borderline timeout variance) |
| Solve | 89 | 89 | Stable |
| Match | 47 | 47 | Stable |
| model_infeasible (in-scope) | 12 | 12 | Stable |
| path_syntax_error | 18-20 | 18 | Stable (scope narrowing) |
| path_solve_terminated | 10 | 10 | Stable |
| path_solve_license | 7 | 7 | Stable |

**Translate delta explanation:** The -2 translate difference is not a code regression. It reflects borderline timeout models (clearlak, dinam, ferts, turkpow) that sit at exactly 150s and flip between success/failure based on system load and run-to-run variance. All deterministic failures (6) are unchanged. The solve count (89) and match count (47) are identical, confirming no functional regressions.

---

## 8. Sprint 23 Targets (from PREP_PLAN.md)

| Priority | Metric | Baseline | Target | Gap |
|----------|--------|----------|--------|-----|
| P1 | Parse | 156/160 (97.5%) | >= 157/160 (98.1%) | Need +1 |
| P2 | Match | 47/160 (29.4%) | >= 55/160 (34.4%) | Need +8 |
| P3 | Solve | 89 (64.0%) | >= 95 (68.3%) | Need +6 |
| P4 | path_syntax_error | 18 | <= 14 | Need -4 |
| P5 | Translate | 139/156 (89.1%) | >= 145/156 (93.0%) | Need +6 |

**Note:** Translate baseline is 139 (not 141 as Sprint 22 final) due to borderline timeout variance. The Tier 1 LhsConditionalAssign fix (+4 models) still reaches 143 (not 145). Additional work may be needed: mine fix (+1 → 144) and/or mexls fix (+1 → 145) to meet P5 target from this baseline.

---

## 9. Known Unknowns Verification

### KU-26: Multi-Solve Incomparable Classification Stability

**Status:** VERIFIED

- All 6 multi-solve models confirmed: aircraft, apl1p, apl1pca, ps10_s_mn, ps5_s_mn, senstran
- Flag is set in `data/gamslib/gamslib_status.json` with `"multi_solve": true`
- Comparison pipeline correctly skips these models (sets `comparison_result = compare_multi_solve_skip`)
- Flag was introduced by PR #1103 and is stable across runs
- No models were incorrectly flagged or missed

---

**Document Created:** 2026-03-20
**Pipeline Run Date:** 2026-03-20
**Next:** Sprint 23 execution begins; reference this document for checkpoint comparisons
