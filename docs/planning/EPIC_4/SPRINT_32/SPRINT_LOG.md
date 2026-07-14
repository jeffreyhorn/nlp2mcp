# Sprint 32 — Progress Log

**Sprint:** 32 (mine Head-Offset 4th Site, sarf 4-D Stationarity, camcge Dual-Consistent Walras [Epic 5], rocket PATH-Consultation & Case-c Documentation — Sprint 31 carryforwards)
**Day-0 baseline (`BASELINE_METRICS.md`):** Parse 142 · Translate 135 · Solve 107 · Match 92 (genuine floor 74) · model_infeasible 7 · Tests 5,074 · all-219 Match 95 · anchor `4cbf8bff`.

> **Skeleton — filled per day during the sprint.** Each row's Metric delta + Status is updated at the end of that day; the closeout table + per-priority summary land Day 13.

| Day | Priority / Work | Metric delta | Status |
|---|---|---|---|
| 0 | Kickoff + Day-0 traces (PR24) + tractability probes (P1 warm-residual→0 `/tmp` / P3 `/tmp`-to-MS-1 / P2 O(active) timing) | — (baseline to confirm) | 🔵 PENDING |
| 1 | P1 mine bound-multiplier emit start (`emit_gams.py:1548–1577`, `piL_x/piU_x` from residual `N`) | — | 🔵 PENDING |
| 2 | P1 mine warm→cold verification (warm residual → 0 Case-a → presolve MS-1) | — | 🔵 PENDING |
| 3 | **P1 mine close-or-REPLAN** (5th-coupling gate) | — (target +1 Solve / +1 floor if cold-match; else REPLAN → Sprint 33) | 🔵 PENDING |
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

## Day N — <title> (YYYY-MM-DD)

_(Per-day entries appended here as the sprint runs.)_
