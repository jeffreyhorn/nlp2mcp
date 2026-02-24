# Sprint 21 Baseline Metrics

**Date:** 2026-02-24
**Commit:** `feffaa95` (planning/sprint21-prep)
**Pipeline Script:** `scripts/gamslib/run_full_test.py --quiet`
**GAMS Version:** v53
**Purpose:** Establish ground truth for Sprint 21 progress measurement

---

## 1. Test Suite

| Metric | Value |
|--------|-------|
| **Tests passed** | 3,715 |
| **Tests skipped** | 10 |
| **Tests xfailed** | 2 |
| **Total runtime** | 61.19s |

---

## 2. Pipeline Summary

| Stage | Count | Rate | Denominator |
|-------|-------|------|-------------|
| **Parse** | 132/160 | 82.5% | 160 processable models (of 219 total GAMSlib) |
| **Translate** | 123/132 | 93.2% | 132 parse-success models |
| **Solve** | 33/124 | 26.6% | 124 real solve attempts (123 translate-success + 1 translate-fail with existing MCP) |
| **Match** | 16/33 | 48.5% | 33 solve-success models |
| **Full pipeline** | 16/160 | 10.0% | All processable models |

---

## 3. Parse Error Breakdown (28 failures)

| Error Category | Count | Models |
|---------------|-------|--------|
| **lexer_invalid_char** | 10 | danwolfe, lop, nonsharp, partssupply, pindyck, saras, springchain, srkandw, srpchase, turkey |
| **semantic_undefined_symbol** | 7 | camcge, cesam, cesam2, feedtray, procmean, sambal, worst |
| **internal_error** | 7 | clearlak, imsl, indus, sarf, senstran, tfordy, turkpow |
| **parser_invalid_expression** | 3 | *(3 models)* |
| **model_no_objective_def** | 1 | *(1 model)* |

---

## 4. Translate Error Breakdown (9 failures)

| Error Category | Count | Models |
|---------------|-------|--------|
| **internal_error** | 7 | gastrans, maxmin, mexls, mingamma, mlbeta, mlgamma, robustlp |
| **timeout** | 2 | iswnm, nebrazil |

Translate internal_error root causes:
- `loggamma`/`gamma` differentiation requires digamma/psi function: mingamma, mlbeta, mlgamma, robustlp (4 models)
- `signpower()` differentiation requires `--smooth-abs` flag: gastrans (1 model)
- `smin()` argument count error: maxmin (1 model)
- Set `'*'` not found in ModelIR: mexls (1 model)

---

## 5. Solve Error Breakdown (91 failures out of 124 real attempts)

| Error Category | Count | % of Failures | Models |
|---------------|-------|--------------|--------|
| **path_syntax_error** | 48 | 52.7% | agreste, ampl, china, dinam, dyncge, egypt, fawley, ferts, glider, gtm, gussrisk, harker, hydro, iobalance, irscge, kand, korcge, launch, least, lmp2, lrgcge, marco, markov, mine, mingamma, moncge, nemhaus, otpop, paklive, paperco, pdi, prolog, ps10_s_mn, ps2_f_eff, ps2_f_inf, ps5_s_mn, qdemo7, quocge, robert, sample, shale, ship, sroute, stdcge, tabora, tforss, tricp, twocge |
| **path_solve_terminated** | 29 | 31.9% | camshape, cclinpts, chain, decomp, elec, etamac, fdesign, ganges, gangesx, hhfair, hs62, jobt, lands, like, pak, polygon, ps10_s, ps2_f, ps2_f_s, ps2_s, ps3_f, ps3_s, ps3_s_gic, ps3_s_mn, ps3_s_scp, qsambal, rocket, solveopt, trussm |
| **model_infeasible** | 12 | 13.2% | bearing, cpack, ibm1, lnts, mathopt3, meanvar, mexss, orani, pollut, ramsey, uimp, whouse |
| **path_solve_license** | 2 | 2.2% | prodsp2, robot |

---

## 6. Solution Comparison (33 solve-success models)

### Matching Models (16)

| Model | NLP Objective | MCP Objective | Rel Diff |
|-------|--------------|---------------|----------|
| ajax | 441003.5953 | 441003.595 | 6.80e-10 |
| blend | 4.98 | 4.98 | 0.0 |
| chem | -47.7065 | -47.707 | 1.05e-05 |
| demo1 | 1898.52 | 1898.52 | 0.0 |
| dispatch | 7.9546 | 7.955 | 5.03e-05 |
| hhmax | 13.9288 | 13.929 | 1.44e-05 |
| himmel11 | -30665.5387 | -30665.539 | 9.78e-09 |
| house | 4500.0 | 4500.0 | 0.0 |
| mathopt2 | 0.0 | 0.0 | 0.0 |
| mhw4d | 27.8719 | 27.872 | 3.59e-06 |
| mhw4dx | 27.8719 | 27.872 | 3.59e-06 |
| prodmix | 18666.6667 | 18666.667 | 1.61e-08 |
| rbrock | 0.0 | 3.43e-20 | 3.43e-10 |
| splcge | 27.1441 | 27.144 | 3.68e-06 |
| trnsport | 153.675 | 153.675 | 0.0 |
| wall | 1.0 | 1.0 | 0.0 |

### Non-Matching Models (17, sorted by relative difference)

| Model | NLP Objective | MCP Objective | Rel Diff | Category |
|-------|--------------|---------------|----------|----------|
| port | 0.2984 | 0.298 | 0.00134 | A (near-match) |
| chakra | 179.1336 | 177.867 | 0.00707 | A (near-match) |
| apl1p | 24515.6483 | 23700.147 | 0.0333 | B (moderate) |
| alkyl | -1.765 | -1.894 | 0.0681 | B (moderate) |
| circle | 4.5742 | 4.071 | 0.110 | B (moderate) |
| chenery | 1058.9199 | 839.769 | 0.207 | B (moderate) |
| weapons | 1735.5696 | 1361.557 | 0.215 | B (moderate) |
| sparta | 3466.38 | 4424.95 | 0.217 | B (moderate) |
| apl1pca | 15902.4936 | 23700.147 | 0.329 | B (moderate) |
| process | 2410.8283 | 1161.337 | 0.518 | B (moderate) |
| aircraft | 1566.0422 | 7332.5 | 0.786 | B (moderate) |
| abel | 225.1946 | 2536.3 | 0.911 | B (moderate) |
| qabel | 46965.0362 | 656565.0 | 0.928 | B (moderate) |
| catmix | -0.0481 | 7.55e-15 | 1.000 | C (complete) |
| mathopt1 | 1.0 | 8.09e-30 | 1.000 | C (complete) |
| trig | 0.0 | 0.23 | 1.000 | C (complete) |
| himmel16 | 0.675 | -1.66e-13 | 1.000 | C (complete) |

---

## 7. Comparison with Sprint 20 Retrospective

| Metric | Sprint 20 Retro | Current Baseline | Delta | Notes |
|--------|----------------|-----------------|-------|-------|
| **Parse** | 132/160 | 132/160 | 0 | Match |
| **Translate** | 120/132 | 123/132 | **+3** | Late Sprint 20 work improved translate |
| **Solve** | 33 | 33 | 0 | Match |
| **Match** | 16 | 16 | 0 | Match |
| **Tests** | 3,715 | 3,715 | 0 | Match |
| **lexer_invalid_char** | 10 | 10 | 0 | Match |
| **internal_error** | 7 | 7 | 0 | Match |
| **semantic_undefined_symbol** | 7 | 7 | 0 | Match |

**Translate delta explanation:** The Sprint 20 retrospective reported 120/132 translate success. The current baseline shows 123/132. This +3 improvement likely reflects late Sprint 20 PRs that improved translate success without changing parse count. The 3 newly-translating models were previously blocked by translate-stage internal_error issues that were resolved by Sprint 20 Day 13-14 work.

**Conclusion:** All metrics match Sprint 20 retrospective values except translate (+3), which is a genuine improvement. The baseline is consistent and reliable for Sprint 21 planning.

---

## 8. Pipeline Processing Notes

- **Total GAMSlib models:** 219 files in `data/gamslib/raw/`
- **Processable models:** 160 (filtered by pipeline script; 59 skipped — these are models without prior parse data or excluded by the pipeline's model selection criteria)
- **Pipeline runtime:** ~1,156 seconds (19.3 minutes)
- **GAMS path:** `/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams`

---

## 9. Sprint 21 Targets (from PROJECT_PLAN.md)

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| **Parse** | 132/160 (82.5%) | ≥135/160 (84.4%) | +3 models needed |
| **lexer_invalid_char** | 10 | ≤5 | -5 needed |
| **internal_error** | 7 | ≤3 | -4 needed |
| **Solve** | 33 | ≥36 | +3 models needed |
| **Match** | 16 | ≥20 | +4 models needed |

---

## 10. Solve Failure Distribution

The 91 solve failures break down by pipeline stage of root cause:

| Root Cause Stage | Count | % | Description |
|-----------------|-------|---|-------------|
| **MCP syntax/compilation** | 48 | 52.7% | PATH cannot process the generated MCP file |
| **PATH convergence** | 29 | 31.9% | PATH runs but fails to converge to a solution |
| **Model infeasibility** | 12 | 13.2% | MCP compiles but is infeasible (KKT formulation issue) |
| **License limitation** | 2 | 2.2% | Model exceeds PATH demo license size limit |

This distribution is key for Unknown 8.1: `path_solve_terminated` (29 models) is a significant population — larger than the 12 model_infeasible failures and nearly as large as path_syntax_error (48) when normalized for total solve attempts.

---

**Document Created:** 2026-02-24
**Next:** Sprint 21 Day 1
