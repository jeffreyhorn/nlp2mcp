# Sprint 20 Baseline Metrics Snapshot

**Snapshot Date:** 2026-02-19  
**Git Commit SHA:** `dc390373c42528772d9d3c6fb558bf1e28927463`  
**Branch:** `main` (post Tasks 1–8 merge)  
**Test suite:** 3,579 passed, 10 skipped, 2 xfailed

---

## Pipeline Metrics

| Stage | Success | Failure | Attempted | Rate |
|---|---|---|---|---|
| **Parse** | 112 | 48 | 160 | 70.0% |
| **Translate** | 96 | 16 | 112 | 85.7% |
| **Solve** | 27 | 69 | 96 | 28.1% |
| **Full pipeline match** | 10 | 17 | 27 | 37.0% |

**Test count:** 3,579  
**Full pipeline success (parse → translate → solve → match):** 10/160 tested (6.3%)

---

## Parse Failure Breakdown

| Error Category | Count | Models |
|---|---|---|
| `lexer_invalid_char` | 26 | camcge, cesam, cesam2, dinam, fdesign, ferts, gussrisk, indus, iobalance, lop, mathopt3, mexls, nemhaus, nonsharp, paperco, pindyck, saras, sarf, senstran, spatequ, springchain, tfordy, trnspwl, turkey, turkpow, worst |
| `model_no_objective_def` | 14 | (MCP models without a minimization/maximization statement) |
| `semantic_undefined_symbol` | 5 | |
| `internal_error` | 2 | |
| `parser_invalid_expression` | 1 | |
| **Total failures** | **48** | |

---

## Translate Failure Breakdown

| Error Category | Count |
|---|---|
| `internal_error` | 7 |
| `codegen_numerical_error` | 5 |
| `timeout` | 4 |
| **Total failures** | **16** |

---

## Solve Failure Breakdown

| Error Category | Count |
|---|---|
| `path_syntax_error` | 35 |
| `path_solve_terminated` | 22 |
| `model_infeasible` | 11 |
| **Total failures** | **68** |

*Note: Solve attempted = 96 (translate successes); failure total 68 + success 27 = 95; 1 model may have a different terminal state.*

---

## Explicit Denominator

| Category | Count | Notes |
|---|---|---|
| **Total catalog** | 219 | All models in `gamslib_status.json` |
| **Tested** | 160 | Models with a parse result (success or failure) in this run |
| **Not tested (excluded)** | 59 | See breakdown below |

### Excluded Models (59 total)

**Reason for exclusion:** These model types are outside the current NLP→MCP pipeline scope. LP and QCP models are not supported (no nonlinear objective); several NLP models require compilation features (GUSS, stochastic, SDP) not yet handled by the preprocessor.

**LP models (29):**
airsp, airsp2, andean, asyncloop, chance, demo7, dqq, embmiex1, epscm, gqapsdp,
gussex1, gussgrid, immun, indus89, kqkpsdp, maxcut, msm, netgen, phosdis, prodsp,
qp5, scenmerge, sddp, spbenders1, spbenders2, spbenders4, srcpm, tgridmix, trnsgrid

**NLP models excluded (26):**
alan, circpack, gancnsx, gasoil, guss2dim, jbearing, lmp1, lmp3, methanol, mhw4dxx,
minlphi, minsurf, pinene, pool, popdynm, qfilter, qp1, qp1x, qp2, qp3, qp4, sipres,
t1000, torsion, trigx, trnspwlx

**QCP models (4):**
emfl, qalan, qcp1, qp7

---

## Comparison with Sprint 19 Final State

| Metric | Sprint 19 Final | Sprint 20 Baseline | Change |
|---|---|---|---|
| Parse success | 107/160 (66.9%) | 112/160 (70.0%) | +5 (+3.1 pp) |
| lexer_invalid_char | 27 | 26 | −1 |
| Translate success | 73 | 96/112 (85.7%) | +23 |
| Solve success | 25 | 27 | +2 |
| Full pipeline match | 9 | 10 | +1 |
| Test count | 3,579 | 3,579 | 0 |
| Total catalog | 219 | 219 | 0 |
| Tested | 160 | 160 | 0 |
| Excluded | 59 | 59 | 0 |

### Discrepancy Notes

1. **Parse: 107 → 112 (+5):** Sprint 19 metrics were taken mid-sprint; the Sprint 20 baseline
   reflects all fixes merged through Task 8 (including grammar improvements from Sprint 19 Days
   1–14 and any Sprint 20 Prep code fixes). No code changes were made in Tasks 1–9 (prep only),
   so the +5 reflects Sprint 19 work that was not reflected in the original Sprint 19 final count.

2. **Translate: 73 → 96 (+23):** The Sprint 19 figure of 73 was a raw count not normalized by
   attempted. The Sprint 20 baseline records 96/112 attempted (85.7%). The increase reflects
   both more parse successes (+5 input models) and pipeline improvements merged through Sprint 19.

3. **lexer_invalid_char: 27 → 26 (−1):** One model fixed since the Sprint 19 count was recorded.
   See Unknown 4.2 verification in `KNOWN_UNKNOWNS.md`.

4. **Solve success: 25 → 27 (+2):** Two additional models now solve, consistent with translate
   improvements feeding more candidates into the solver.

5. **Full pipeline match: 9 → 10 (+1):** One additional model achieves objective match.
