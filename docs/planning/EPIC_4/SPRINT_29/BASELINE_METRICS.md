# Sprint 29 Day-0 Baseline Metrics + Bucket Provenance + Re-Baseline Discipline

**Task:** Sprint 29 Prep Task 2 (PR15 bucket provenance + PR17 scope freeze + PR25 projection discipline + the Sprint-28 §5 post-methodology re-baseline)
**Date:** 2026-06-24
**Baseline source:** The committed Sprint 28 Day-13 final pipeline DB (`data/gamslib/gamslib_status.json`, last written by the Day-13 closeout, merged in PR #1463 `803a259a`). Reused per the Task-2 "reuse the committed final DB if `main` is unchanged" guidance — **verified applicable:** `git diff 803a259a..HEAD -- src/ scripts/` is **empty** (only Sprint 29 planning docs landed since the Sprint 28 close, PR #1465), so no pipeline-affecting change has occurred. **Sprint 29 Day 0 = Sprint 28 final;** no fresh ~4 h retest required. The DB has **0 absolute-path leaks** (`grep -c /Users/ … = 0`; the #1400 relativization holds).

---

## 1. Day-0 Headline Counts (142-model GAMSlib corpus)

Authoritative figures from the Sprint 28 Day-13 deterministic retest (`SPRINT_28/SPRINT_LOG.md` §"Day 13" + `SPRINT_28/SPRINT_RETROSPECTIVE.md` header). Byte-identical across `PYTHONHASHSEED` 0/1/42.

| Metric | Sprint 29 Day 0 | Sprint 29 Target | Gap |
|---|---|---|---|
| Parse | **142** / 142 | ≥ 142 | met |
| Translate | **135** / 142 | ≥ 135 | met (maintain) |
| Solve (`model_optimal[_presolve]`) | **107** / 142 | ≥ 109 (firm) | −2 |
| Match | **92** / 142 | maintain ≥ 92 / stretch ≥ 96 | met / −4 to stretch |
| Mismatch | **9** | — | (solved-but-diverging, `compare_objective_mismatch`) |
| path_syntax_error | **8** | maintain ≤ 8 | met |
| path_solve_terminated | **4** | maintain ≤ 5 | met |
| model_infeasible | **7** | ≤ 5 | −2 |
| Tests | **~4,935** | ≥ 4,960 | −25 |

Of the 107 solved models, 92 match their NLP reference, 9 mismatch (`compare_objective_mismatch`), and 6 are uncompared (`compare_multi_solve_skip` — no single-solve NLP reference).

> **Scope note.** A naive recompute over every translate-success row in the raw DB returns 115 solve / 92 match / 17 mismatch — it includes 8 out-of-scope models (non-NLP/QCP corpus). The authoritative figures above are the committed Day-13 retest **summary** (142-model pipeline scope): Solve 107, Match 92. The raw DB is used below only to confirm per-model buckets, which match the committed bucket lists exactly.

### Failure-bucket membership (frozen Day-0 reference)

From the Day-13 retest DB (cross-checked against `SPRINT_28/SPRINT_LOG.md`):

- **Translate failures (7):** `danwolfe`, `decomp`, `iswnm`, `mexls`, `nebrazil`, `saras`, `sarf`.
- **model_infeasible (7):** `agreste`, `camcge`, `cesam`, `fawley`, `lnts`, **`mine`**, **`rocket`**.
- **path_syntax_error (8):** `clearlak`, `dinam`, `ganges`, `gangesx`, `indus`, `sample`, `turkey`, `turkpow`.
- **path_solve_license (9):** `egypt`, `ferts`, `glider`, `robot`, `shale`, `sroute`, `srpchase`, `tabora`, `tfordy`.
- **path_solve_terminated (4):** `dyncge`, `elec`, `tricp`, `twocge`.
- **mismatch (9, 142-scope):** `chain`, `china`, `circle`, **`hhfair`**, `imsl`, `lmp2`, `prodsp2`, `spatequ`, `trig`. *(A raw recompute over all translate-success rows returns 17, but `abel` + the 7 `ps*` models — ps10_s/ps2_f_s/ps2_s/ps3_s/ps3_s_gic/ps3_s_mn/ps3_s_scp — are the 8 out-of-scope models excluded from the 142-model pipeline, the same 8 that make the raw Solve 115 vs the canonical 107.)*

The Sprint 29 target models are highlighted: **mine** + **rocket** (model_infeasible), **hhfair** (the only objective-mismatch-cohort member still mismatching — see §3).

---

## 2. Re-Baseline: Genuine vs Methodology Match Split (Sprint-28 §5)

The Sprint 28 headline Match jumped 62 → 92 (+30), but the decomposition (`SPRINT_28/SPRINT_LOG.md` §"Day 13" PR25 tally) is **+7 genuine + ~24 methodology − 1 stale-baseline**. Sprint 29's targets must therefore be set against the **genuine** baseline, not the methodology-inflated 92.

| Component | Count | Models |
|---|---|---|
| **Genuine, stable** (the re-baseline floor) | **68** | the 62 cold matches (which include the genuine cross-term fixes otpop/chakra/chenery/kand/srkandw that now solve **cold**) + the 6 non-methodology presolve matches (camshape, cclinpts + the pre-existing bearing/launch/mathopt3/robustlp) — 62 + 6 = 68 |
| **Methodology-recovered** (Day-9 presolve-retry-on-cold-mismatch broadening, `_cold_objective_mismatches_nlp`) | **~24** | catmix, himmel16, weapons, harker, polygon, sambal, markov, worst, irscge, lrgcge, moncge, stdcge, like, robert, mathopt1, mathopt4, mingamma, paperco, qsambal, marco, etamac, cpack, maxmin, tforss |
| **As-measured total** | **92** | — |

**Operational definition** of the methodology set: a model with `mcp_solve.outcome_category = model_optimal_presolve` AND `comparison_status = match` whose **cold** MCP failed/mismatched (the warm-start was *required*), and whose cold emit is byte-identical to its pre-Day-9 state (22 of the 24). These models were *always emit-correct*; the broadened retry now warm-start-*validates* them — so they are not a repeatable cross-term gain.

**Re-baseline rule (PR25 extension, for Task 8 to codify):** after any pipeline-methodology change (a retry-trigger or comparison-logic change), recompute this split and record the new genuine floor. The headline Match delta must be reported as **genuine** (cross-term-fix transitions) separately from **methodology** (validation of already-correct emits). Sprint 29's genuine target floor is **68**; its as-measured maintain target is **92**.

---

## 3. Per-Failing-Model Bucket Provenance — Sprint 29 Targets

Per-model trajectory: Sprint 28 final (= Sprint 29 Day-0) bucket + the gating issue + the **PR25 projection label** (genuine bucket-to-success vs methodology/bucket-forward / already-banked).

| Model / Track | S29 Day-0 bucket | Gating issue | Projected delta | PR25 label |
|---|---|---|---|---|
| **mine** (P1) | `model_infeasible` | #1443 head-domain-offset MCP infeasibility | +1 Solve (firm if Case b) | **genuine** (model_infeasible → model_optimal) |
| **rocket** (P2) | `model_infeasible` | #1462 `nu_*_fx_h0` warm-start + non-convex | +1 Solve / +1 Match (Case-b residual) | **genuine** (model_infeasible → match) |
| **#1385 timeout cohort** (P3) | `translate_failure` (iswnm/mexls/nebrazil/sarf) | #1385 runtime-guard cross-terms | +Translate (≥1) | **genuine** (translate_failure → translate) |
| **maxmin** (P4 lead) | `model_optimal_presolve` + **match** | #1447 `stat_mindist` cold-emit Case-b | 0 net (already matches warm); the genuine win is **cold robustness** | **methodology-already-banked**; the Case-b fix removes the warm-start dependency, not +Match |
| **cold-convex cohort** (P4) | `model_optimal_presolve` + match (the ~24) | cold-emit Case-b vs inherent non-convex (Task 3) | 0 net Match; cold-robustness only | **methodology-already-banked** |
| **camcge** (P5) | `model_infeasible` | #1330 CGE Walras degeneracy → Epic 5 | 0 (Epic-5 hand-off, no `src/`) | **bucket-forward / out-of-scope** (stays infeasible) |
| **quocge** (P6 #1332) | `model_optimal` + **match** (25.683 ≈ 25.6834) | — | **already matches** (was 25.683 vs 25.5085 in the stale PROJECT_PLAN; now matches) | **already-banked — REMOVE from P6 projection** |
| **prolog** (P6 #1247) | `model_optimal` + **match** (−6.25e-13 ≈ −0.0) | — | **already matches** | **already-banked — REMOVE from P6 projection** |
| **sambal / qsambal** (P6 #1239) | `model_optimal_presolve` + **match** (3.9682) | — | **already matches (warm)** (was 1028 vs 3.97 stale) | **methodology-already-banked — REMOVE from P6 projection** |
| **hhfair** (P6 #1236) | `model_optimal` + **mismatch** (72.147 vs 87.159) | #1236 objective mismatch | +1 Match (firm if Case b) | **genuine** (mismatch → match) — the only live P6 target |
| **himmel16 / polygon** (P7 #1146/#1143) | `model_optimal_presolve` + **match** | #1146/#1143 offset-alias gradient (cold) | 0 net Match (already match warm); cold-robustness | **methodology-already-banked**; the cold gradient fix is robustness + a Case-b for #1111/#1112 |

### Key scope findings (the PR25 discipline catching stale projections)

1. **Priority 6 has shrunk to one live target.** The PROJECT_PLAN listed `#1332/#1247/#1239/#1236` as a "+2 Match" cohort using **stale pre-Sprint-28 objective values** (quocge 25.683 vs 25.5085; sambal 1028 vs 3.97). On the current Day-0 DB, **quocge, prolog, sambal, and qsambal all match** — only **hhfair (#1236)** still mismatches. Priority 6's genuine remaining gain is therefore **≤ +1 Match (hhfair)**, not +2. The freed P6 budget should pre-allocate to Priority 4 cold-robustness or Priority 7 (per the Task-5 REPLAN reallocation).
2. **Priorities 4 and 7 overlap and are mostly Match-neutral.** maxmin, himmel16, and polygon all already **match via the warm-start** — their Sprint-29 fixes (#1447 `stat_mindist`; #1146/#1143 offset-alias gradient) are **cold-robustness** wins (removing the warm-start dependency), *not* +Match. They are genuine emit-correctness improvements but do **not** move the headline Match number unless a fix also recovers a *cold-only* model. This must be reflected in the schedule (Task 10): Priorities 4/6/7 contribute mostly to the *genuine-vs-methodology re-baseline* (converting methodology matches into genuine ones), not to the as-measured Match target.
3. **The firm Solve gains (mine #1443, rocket #1462) remain the only headline-moving genuine Match/Solve transitions** — both currently `model_infeasible`. Solve ≥ 109 = 107 + mine + rocket (firm if Case b; REPLAN-gated per Task 5).

### PR25 Projection Tally (genuine bucket-to-success only)

- **Solve (107 → target ≥ 109):** genuine = mine +1 (#1443) + rocket +1 (#1462) → **109** (firm if both Case b; REPLAN to Sprint 30 if Case c). No other priority moves Solve (the cold-convex/cohort fixes are Match-side or already-solved).
- **Match (92 as-measured → maintain ≥ 92 / stretch ≥ 96):** genuine new transitions = rocket +1 (#1462) + hhfair +1 (#1236, if Case b) → **94** firm-ish; the cold-robustness fixes (#1447 maxmin, #1146/#1143) convert ~3 methodology matches into genuine ones (raising the *genuine floor* 68 → ~71) without moving the as-measured 92. Stretch ≥ 96 requires ≥ 2 more cold-only recoveries from the Task-3 cold-convex Case-b partition.
- **model_infeasible (7 → ≤ 5):** −2 via mine + rocket recoveries (firm if Case b). camcge stays infeasible (Epic 5).
- **Bucket-forward / out-of-scope (no target credit):** camcge (#1330 → Epic 5); the already-banked P6 matches (quocge/prolog/sambal/qsambal); the methodology-already-banked P4/P7 warm-matches.

---

## 4. Scope Freeze (PR17)

- **In-target (genuine, headline-moving):** mine (#1443, +1 Solve), rocket (#1462, +1 Solve/+1 Match), hhfair (#1236, +1 Match conditional), the #1385 timeout cohort (+Translate conditional), any cold-only recoveries from the Task-3 cold-convex Case-b partition (+Match stretch).
- **In-target (genuine emit-correctness, re-baseline only):** the cold-robustness fixes — #1447 maxmin, #1146 himmel16, #1143 polygon — convert methodology matches into genuine ones (raise the genuine floor) without moving the as-measured 92.
- **Out-of-scope / Sprint-30-deferred (REPLAN exits):** camcge (#1330 → Epic 5, no `src/`); any Case-c models from the Task-3 partition (inherent non-convexity → Sprint 30 forcing strategies); the #1443/#1462/#1146-1112 architectural REPLAN exits (Task 5).
- **Committed regression-guard sets:** the 92 matching models + the 107 solving models (the Day-13 retest sets) — any Sprint-29 emit change must re-solve the changed-golden subset (Task 8) and not regress these.

---

**Document Created:** 2026-06-24
**Owner:** Sprint 29 Planning Team
**Authoritative scheduling budget:** the per-task totals in `docs/planning/EPIC_4/SPRINT_29/PREP_PLAN.md` (35–48 h across Tasks 1–10).
