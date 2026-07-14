# Sprint 32 — Progress Log

**Sprint:** 32 (mine Head-Offset 4th Site, sarf 4-D Stationarity, camcge Dual-Consistent Walras [Epic 5], rocket PATH-Consultation & Case-c Documentation — Sprint 31 carryforwards)
**Day-0 baseline (`BASELINE_METRICS.md`):** Parse 142 · Translate 135 · Solve 107 · Match 92 (genuine floor 74) · model_infeasible 7 · Tests 5,074 · all-219 Match 95 · anchor `4cbf8bff`.

> **Skeleton — filled per day during the sprint.** Each row's Metric delta + Status is updated at the end of that day; the closeout table + per-priority summary land Day 13.

| Day | Priority / Work | Metric delta | Status |
|---|---|---|---|
| 0 | Kickoff + Day-0 traces (PR24) + tractability probes (P1 warm-residual→0 / P3 step-1 `mps.m` / P2 O(active) sizing) | — (baseline confirmed: Parse 142 · Translate 135 · Solve 107 · Match 92 · genuine 74; `src/`+`scripts/` diff vs `4cbf8bff` EMPTY; 4 harness fingerprints re-confirmed exactly, duals CONSISTENT; sarf 369,024→398; `DAY0_TRACES.md`) | ✅ DONE |
| 1 | P1 mine bound-multiplier `/tmp` control (PR24/PR27) → **5th coupling confirmed** | **0 (REPLAN → Sprint 33 — the `N`-derivation closes `stat_x` by construction but PATH MS-5 @ 22058; 6 bound-active rows carry wrong-sign `N` → infeasible negative multiplier; interior emit correct)** | 🔴 REPLAN |
| 2 | ~~P1 mine warm→cold verification~~ → **freed by Day-1 REPLAN** → pull P6 forward (Task 9 reallocation) | — | ⏭️ REALLOCATED |
| 3 | ~~P1 mine close-or-REPLAN~~ → **REPLAN fired Day 1** (front-loading worked — surfaced early) | — | ⏭️ REALLOCATED |
| 4 | P3 camcge `stat_mps` (step 1 `nu_mps_fx.l=-mps.m`) + Walras (step 2) start | — | 🔵 PENDING |
| 5 | **P3 camcge close-or-REPLAN** (MS-1 @ 191.7346 + detector) **+ Checkpoint 1** | — (target +1 Solve; else step 1 lands, numéraire → Epic 5) | 🔵 PENDING |
| 6 | P2 sarf 4-D `task` sparsification start (2-D gate + parametric `stat_task`) | — | 🔵 PENDING |
| 7 | P2 sarf tractability gate (O(active=398) not O(369K)) | — (target +1 Translate; else REPLAN → Sprint 33 re-scoping) | 🔵 PENDING |
| 8 | P2 sarf close + golden byte-stable | — | 🔵 PENDING |
| 9 | P4 rocket PATH-consultation input (Case-c re-confirm + finalize) | — (deliverable: packaged input; +1 Solve only if a lever crosses) | 🔵 PENDING |
| 10 | P5 hhfair + CGE Case-c classifier (harness extension) **+ Checkpoint 2** | — (0 genuine floor; `ISSUE_1236` documented-non-convex) | 🔵 PENDING |
| 11 | P6 adjacent backlog (cpack offset-alias + fawley Case-b) + REPLAN-slack | — (target ≥ 1 model recovered OR cohort re-triaged) | 🔵 PENDING |
| 12 | P7 infrastructure (shape12/shape13 fixtures + genuine-floor tracking + Epic-4-SUMMARY) + REPLAN-slack | — | 🔵 PENDING |
| 13 | Final retest (≥ 3 `PYTHONHASHSEED`) + closeout | — | 🔵 PENDING |

**Targets (`PROJECT_PLAN.md` §"Sprint 32"):** Solve 107 → ≥ 109 · Match maintain ≥ 92 / genuine floor 74 → ≥ 75 · model_infeasible 7 → ≤ 5 · Translate ≥ 135 (+1 via #1385 sarf) · Tests ≥ 5,080 · determinism ✅ ×3.

**Honest KPI projection (`REPLAN_RISK_ASSESSMENT.md`):** Solve ≥ 109 needs BOTH mine [P1] AND camcge [P3] (the 2-element mover set; rocket [P4] a conditional third) — the most REPLAN-sensitive KPI; genuine floor ≥ 75 is conditional on mine/camcge **cold-matching** or a P6 emit change, NOT presolve-methodology (P5 = 0 floor); Translate +1 is conditional on sarf [P2]. Reallocation order on any REPLAN: P6 → P7 → the rocket [P4] forcing tail.

---

## Day 0 — Kickoff + Day-0 Traces + Tractability Probes (2026-07-14)

**Branch** `planning/sprint32-day0-kickoff`. Trace-only (no `src/`); see `DAY0_TRACES.md`.

- **Baseline holds:** `git diff 4cbf8bff..HEAD -- src/ scripts/` **EMPTY** → no retest needed; DB recompute = 142 candidates / 107 solved (Sprint-31-final headline reproduced).
- **Day-0 fix-surface traces re-confirmed exactly** (`kkt_residual.py`, duals CONSISTENT throughout): mine CASE_B `stat_x(3,1,1)` rel **2.37** (−3.20e4); camcge CASE_B `stat_mps` raw **−210** (⇒ `mps.m ≈ −209.861`); rocket CASE_B boundary `stat_ht(h0)` 1.00 / `stat_step` 0.50 / `stat_ht(h50)` 0.44 with interior near tol (Case-c); hhfair CASE_B `stat_u(1)` rel **2.00** (D1, `nu_obj=±1`).
- **Tractability probes:** (P1) mine warm-residual pre-fix fingerprint re-confirmed — the `N`-derivation `/tmp` is the Day-1 pre-`src/` control; (P3) camcge step-1 `−210`/`mps.m` re-confirmed — the dual-consistent-Walras `/tmp`-to-MS-1 (191.7346) is the Day-4 pre-`src/` control; (P2) sarf sizing re-confirmed **369,024 Cartesian → 398 active** (927×), the O(1 symbolic equation) fix.
- **PR25 tally:** genuine 74 / methodology 21; → ≥ 75 needs mine/camcge cold-match or a P6 emit gain (P5 = 0 floor).
- **Disposition: GO for Day 1** (the mine bound-multiplier emit at `src/emit/emit_gams.py:1548–1577`, gated on the `/tmp` warm-residual→0 control).

## Day 1 — P1 mine bound-multiplier `/tmp` control → 5th coupling REPLAN (2026-07-14)

**Branch** `planning/sprint32-day1-mine-boundmult`. Control-only (**no `src/`** — the fix was refuted before src). See `MINE_5TH_COUPLING_REPLAN.md`.

The PR24/PR27 Day-1 `/tmp` control (hand-edited `mine_mcp_presolve.gms`, GAMS 53; embedded NLP MS-1 @ 17500) refuted the banked `N`-derivation:
- **`stat_x` body = 0.000 by construction** (`piL_x=max(N,0)`, `piU_x=max(−N,0)` — the formula is correct).
- **But the MCP solve → MS-5 Locally Infeasible @ 22058** (≠ NLP 17500) — the S31 Day-2/3 signature.
- **6 complementarity violations:** `piL_x>0` off the lower bound at `x(1,3,{1,2,3})`, `piU_x>0` off the upper bound at `x(3,1,2)/x(3,2,1)/x(4,1,1)` — the sign-split multiplier is nonzero at rows whose `x` is at the *opposite* bound.
- **0 interior rows with `N≠0`** — the interior emit is correct; the residual is exclusively at bound-active rows with the **wrong sign** (would need an infeasible negative multiplier).

**Diagnosis:** the emitted `stat_x` head-offset **cross-term** is inconsistent at bound-active rows — the design's own explicit 5th-coupling REPLAN trigger. No warm-start bound-multiplier value can fix it; the fix is a deeper head-offset cross-term emit change → **Sprint 33**. **REPLAN; no `src/` change** (the 6th consecutive control-first REPLAN, S30–S32). mine stays `model_infeasible`; Solve ≥ 109 now rests on **camcge [P3] alone** (+ a possible P6 cpack/fawley convert). P1 Days 1–3 budget → **P6 + P7** (Task 9); the Day-2/3 mine slots pull P6 forward.

_(Per-day entries appended below as the sprint runs.)_
