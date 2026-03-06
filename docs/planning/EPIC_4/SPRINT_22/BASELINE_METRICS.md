# Sprint 22 Baseline Metrics

**Date:** 2026-03-06
**Branch:** `main` @ `53ac5979` (PR #996 merge commit)
**Pipeline:** `run_full_test.py --quiet` (convex models only)
**Test Suite:** `make test`
**nlp2mcp Version:** 1.1.0 (from `pyproject.toml`; note `src/__init__.py` still reports `__version__ = "0.6.0"` at this commit)
**GAMS Version:** 51.3.0
**PATH Solver License:** Demo (300 variables/constraints)

---

## 1. Pipeline Summary

| Stage | Success | Attempted | Rate | Failures | Cascade Skipped |
|-------|---------|-----------|------|----------|-----------------|
| Parse | 154 | 157 | 98.1% | 3 | — |
| Translate | 136 | 154 | 88.3% | 18 | 3 |
| Solve | 65 | 136 | 47.8% | 71 | 21 |
| Match | 30 | 65 | 46.2% | 35 | 92 |

**Full pipeline success (parse → match):** 30/157 (19.1%)

**Total pipeline time:** 3636.9s (~61 min), average 23.16s/model

---

## 2. Parse Stage (154/157)

### Error Breakdown

| Category | Count | Models |
|----------|-------|--------|
| lexer_invalid_char | 3 | danwolfe, partssupply, turkey |

### Timing

| Metric | Value |
|--------|-------|
| Mean | 9.90s |
| Median | 1.79s |
| P90 | 15.45s |

### Notes

- **lop** (lexer_invalid_char in previous runs) is excluded from this pipeline run because its convexity status is not `verified_convex` or `likely_convex`. It still fails to parse but is not counted in the 157-model test set.
- See KU-14 investigation below for root cause analysis of all 3 failures.

---

## 3. Translate Stage (136/154)

### Error Breakdown

| Category | Count | Models |
|----------|-------|--------|
| timeout | 12 | clearlak, dinam, egypt, ferts, ganges, gangesx, iswnm, nebrazil, sarf, srpchase, tricp, turkpow |
| internal_error | 6 | gastrans, maxmin, mexls, mlbeta, mlgamma, robustlp |

### Internal Error Root Causes

| Model | Root Cause |
|-------|-----------|
| gastrans | `signpower()` differentiation requires `--smooth-abs` flag |
| maxmin | `smin()` argument count mismatch (3 vs expected 2) |
| mexls | Universal set `'*'` not found in ModelIR |
| mlbeta | `loggamma()` differentiation requires digamma/psi function |
| mlgamma | `loggamma()` differentiation requires digamma/psi function |
| robustlp | `gamma()` differentiation requires digamma/psi function |

### Timing

| Metric | Value |
|--------|-------|
| Mean | 12.78s |
| Median | 4.23s |
| P90 | 47.89s |

### Delta from Sprint 21 Final

- Sprint 21 final: 137/154 (89.0%) — timeout: 11, internal_error: 6
- Sprint 22 baseline: 136/154 (88.3%) — timeout: 12, internal_error: 6
- **Regression:** tricp moved from translate success → timeout (+1 timeout)

---

## 4. Solve Stage (65/136)

### Error Breakdown

| Category | Count | Models |
|----------|-------|--------|
| path_syntax_error | 40 | agreste, ampl, camcge, camshape, cesam, cesam2, china, decomp, dyncge, glider, gtm, gussrisk, harker, imsl, indus, kand, korcge, launch, lmp2, marco, markov, nemhaus, nonsharp, paklive, paperco, pdi, prolog, ps10_s_mn, ps5_s_mn, qsambal, ramsey, robert, sambal, saras, shale, spatequ, srkandw, tabora, trnspwl, worst |
| model_infeasible | 15 | bearing, chain, cpack, feasopt1, ibm1, iobalance, lnts, mathopt3, meanvar, mexss, orani, rocket, twocge, uimp, whouse |
| path_solve_terminated | 12 | elec, etamac, fawley, fdesign, hhfair, lands, otpop, pak, pindyck, springchain, tforss, trussm |
| path_solve_license | 4 | prodsp2, robot, sroute, tfordy |

### path_syntax_error Subcategory Breakdown (40 models)

Based on PATH_SYNTAX_ERROR_STATUS.md (Task 2) with current adjustments:

| Subcategory | Count | Models | GAMS Error |
|-------------|-------|--------|------------|
| A: Missing data | 15 | agreste, camcge, camshape, china, decomp, indus, lmp2, markov, paperco, ps5_s_mn, ps10_s_mn, qsambal, ramsey, sambal, saras | $141/$66/$140 |
| B: Domain violation | 2 | cesam, cesam2 | $170 |
| C: Uncontrolled set | 10 | ampl, dyncge, glider, harker, korcge, paklive, robert, shale, tabora, trnspwl | $149 |
| G: Set index reuse | 4 | kand, prolog, spatequ, srkandw | $125 |
| I: Unreferenced var | 2 | nemhaus, worst | $483 |
| J: Dimension mismatch | 2 | launch, pdi | $70 |
| New patterns | 5 | gussrisk ($161), gtm ($120/$340), imsl ($116), marco ($172), nonsharp ($187) | Various |

Note: imsl was classified as "New pattern" in Task 2 and is counted only under the "New patterns" subcategory here.

### Timing

| Metric | Value |
|--------|-------|
| Mean | 0.80s |
| Median | 0.66s |
| P90 | 1.28s |

### Delta from Sprint 21 Final

- Sprint 21 final: 65/137 (47.4%) — path_syntax_error: 41
- Sprint 22 baseline: 65/136 (47.8%) — path_syntax_error: 40
- **Changes:**
  - tricp: was path_syntax_error → now translate timeout (removed from solve stage)
  - mingamma: was path_syntax_error → now translate internal_error (removed from solve stage)
  - feedtray: convexity excluded, not in test set
  - Net solve success unchanged at 65

---

## 5. Match Stage (30/65)

### Matched Models (30)

ajax, alkyl, blend, chem, demo1, dispatch, hhmax, himmel11, house, hs62, mathopt2, mathopt4, mhw4d, mhw4dx, pollut, port, procmean, prodmix, ps2_f, ps2_f_eff, ps2_f_inf, ps3_f, quocge, rbrock, sample, ship, solveopt, splcge, trnsport, wall

### Mismatched Models (35)

All mismatches are `compare_objective_mismatch` — the MCP solves successfully but produces a different objective value than the original NLP.

| Model | NLP Obj | MCP Obj | Rel Diff |
|-------|---------|---------|----------|
| abel | 225.19 | 2557.43 | 91.2% |
| aircraft | 1566.04 | 7332.50 | 78.6% |
| apl1p | 24515.65 | 23700.15 | 3.3% |
| apl1pca | 15902.49 | 23700.15 | 32.9% |
| catmix | -0.05 | 0.00 | 100.0% |
| cclinpts | -3.00 | -9.96 | 69.9% |
| chakra | 179.13 | 177.87 | 0.7% |
| chenery | 1058.92 | 839.77 | 20.7% |
| circle | 4.57 | 4.07 | 11.0% |
| himmel16 | 0.68 | 0.00 | 100.0% |
| hydro | 4366944.16 | 4975400.49 | 12.2% |
| irscge | 26.09 | 25.51 | 2.2% |
| jobt | 21343.06 | 81000.00 | 73.7% |
| least | 14085.14 | 21027.50 | 33.0% |
| like | -1138.41 | -1218.44 | 6.6% |
| lrgcge | 25.77 | 25.51 | 1.0% |
| mathopt1 | 1.00 | 0.00 | 100.0% |
| mine | 17500.00 | 29000.00 | 39.7% |
| moncge | 25.98 | 25.51 | 1.8% |
| polygon | 0.78 | 0.00 | 100.0% |
| process | 2410.83 | 1161.34 | 51.8% |
| ps10_s | 0.53 | 0.39 | 27.4% |
| ps2_f_s | 0.87 | 0.86 | 0.5% |
| ps2_s | 0.87 | 0.86 | 0.5% |
| ps3_s | 1.16 | 1.06 | 9.1% |
| ps3_s_gic | 1.16 | 1.06 | 9.1% |
| ps3_s_mn | 1.05 | 1.03 | 2.2% |
| ps3_s_scp | -0.61 | -0.62 | 2.3% |
| qabel | 46965.04 | 668024.80 | 93.0% |
| qdemo7 | 1589042.39 | 0.00 | 100.0% |
| senstran | 163.98 | 153.68 | 6.3% |
| sparta | 3466.38 | 4959.35 | 30.1% |
| stdcge | 26.09 | 25.51 | 2.2% |
| trig | 0.00 | 0.23 | 100.0% |
| weapons | 1735.57 | 1361.56 | 21.5% |

---

## 6. Test Suite

```
make test
```

| Metric | Value |
|--------|-------|
| Passed | 3,957 |
| Skipped | 10 |
| Xfailed | 1 |
| Failed | 0 |

Matches Sprint 21 final exactly.

---

## 7. KU-14 Verification: 3 lexer_invalid_char Models

**Status:** VERIFIED — all 3 are non-trivial grammar features, not Sprint 22 scope.

| Model | Issue | Root Cause | Effort |
|-------|-------|-----------|--------|
| danwolfe | Parenthesized expression in data block | Grammar doesn't support `);` as data terminator after parenthesized groups | 1-2h |
| partssupply | Model composition with `+` operator | Grammar doesn't support `Model m /eq1, eq2/ + /eq3/;` syntax (#892) | 1-2h |
| turkey | Parenthesized table column groups | Grammar doesn't support `Table t(i, j) / (col1,col2).row1 val /` syntax (#896) | 1-2h |

**Note:** lop (Issue #890, multi-dimensional subset declaration) is the 4th lexer_invalid_char model in the full database but is excluded from the 157-model pipeline test set (convexity status: excluded).

---

## 8. KU-15 Verification: Parse Rate Stability

**Status:** VERIFIED — parse rate is stable at 154/157 (98.1%).

Sprint 21 final: 154/157 (98.1%)
Sprint 22 baseline: 154/157 (98.1%)

No regression. The same 3 models fail (danwolfe, partssupply, turkey) with the same error category (lexer_invalid_char).

---

## 9. Sprint 22 Targets vs Baseline

| Metric | Sprint 22 Baseline | Sprint 22 Target | Gap |
|--------|-------------------|------------------|-----|
| path_syntax_error | 40 | ≤ 30 | -10 models needed |
| Solve success | 65 | ≥ 75 | +10 models needed |
| Match | 30 | ≥ 35 | +5 models needed |
| Tests | 3,957 | No regressions | Maintain |

### path_syntax_error Fix Priorities (from PATH_SYNTAX_ERROR_FIX_DESIGN.md)

| Subcategory | Models | Estimated Effort | Sprint 22 Priority |
|-------------|--------|------------------|--------------------|
| A: Missing data | 15 | 4-6h | **P0 — highest leverage** |
| C: Uncontrolled set | 10 | 3-5h | P1 |
| G: Set index reuse | 4 | 1-2h | P1 |
| B: Domain violation | 2 | 1-2h | P1 |
| New patterns | 5 | 4-7h | P2 |
| I, J, Other | 4 | 2-3h | P2 |

Fixing Subcategory A alone (15 models) would reduce path_syntax_error to ≤ 25, exceeding the ≤ 30 target.
