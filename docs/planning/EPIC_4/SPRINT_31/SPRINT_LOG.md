# Sprint 31 — Progress Log

**Sprint:** 31 (Head-Offset IR Plumbing, General-Alias AD #1111/#1112 & Dual-Consistent CGE — Sprint 30 carryforwards)
**Day-0 baseline (`BASELINE_METRICS.md`):** Parse 142 · Translate 135 · Solve 107 · Match 92 (genuine floor 70) · model_infeasible 7 · Tests 4,997 · anchor `ea4191dc`.

| Day | Priority / Work | Metric delta | Status |
|---|---|---|---|
| 0 | Kickoff + Day-0 traces (PR24) + tractability probes (P1 round-trip / P3 `/tmp` prototype / P5 hhfair control) | — (baseline confirmed) | 🔵 PENDING |
| 1 | P1 Phase 1: head-offset IR plumbing (`EquationDef.head_domain_offsets` field addition) | — (round-trip fixture green; goldens byte-stable) | 🔵 PENDING |
| 2 | P1 Phase 2: shared 3-site helper (heaviest day) | — (helper wired to comp_pr / dual-transfer / stat_x) | 🔵 PENDING |
| 3 | P1 mine close-or-REPLAN (cold-INFES-by-direction gate) | — (target: mine → MS 1, +1 Solve; REPLAN on a 4th site) | 🔵 PENDING |
| 4 | P2 offset-alias #1111/#1112 core (polygon): coupled objective + distance second-index | — (target: coupled fix lands, tightly gated) | 🔵 PENDING |
| 5 | P2 finish (shape8 enable, warm-match 0.780) + Checkpoint 1 | — (target: polygon genuine floor +1; REPLAN on gate leak) | 🔵 PENDING |
| 6 | P3 camcge dual-consistent Walras (start; `/tmp` prototype → src) | — (target: dual-consistent redefinition + S1∧S2∧S3 detector) | 🔵 PENDING |
| 7 | P3 camcge close-or-REPLAN (MS 1 @ 191.7346 + detector precision) | — (target: camcge → MS 1, +1 Solve; REPLAN to per-model-numéraire) | 🔵 PENDING |
| 8 | P4 sarf symbolic emit (start): 2-D gate + parametric `stat_task` | — (target: 2-D `_is_blowup_dynamic_subset_equation` + no set-name literals) | 🔵 PENDING |
| 9 | P4 sarf tractability gate (O(constraints)) + Checkpoint 2 | — (target: sarf → translate, +Translate; REPLAN on timeout) | 🔵 PENDING |
| 10 | P5 cold-convex obj-grad: CGE cluster `stat_xp` reduction (hhfair = Case-c) | — (target: irscge/lrgcge/moncge → Case-a, genuine floor; sign flip BANNED) | 🔵 PENDING |
| 11 | P6 rocket forcing → PATH-consultation input (`1/m` reformulation + continuation) | — (target: +1 Solve OR the finalized PATH-consultation input) | 🔵 PENDING |
| 12 | P7 infrastructure (shape8 + head-offset fixtures, genuine-floor tracking) + REPLAN-slack | — (target: property fixtures + PR25 re-baseline recompute) | 🔵 PENDING |
| 13 | Final retest (≥3 `PYTHONHASHSEED`) + closeout | — (target: Solve ≥109 / genuine floor ≥73 / determinism ✅) | 🔵 PENDING |

**Targets (`PROJECT_PLAN.md` §"Sprint 31"):** Solve 107 → ≥ 109 · Match maintain ≥ 92 / genuine floor 70 → ≥ 73 · model_infeasible 7 → ≤ 5 · Translate ≥ 135 (stretch +1 via #1385) · Tests ≥ 5,000 · determinism ✅.

**Honest KPI projection (`REPLAN_RISK_ASSESSMENT.md`):** Solve ≥ 109 (needs mine [P1] + camcge [P3]) is the most REPLAN-sensitive KPI (P3 has a per-model-numéraire fallback that still solves; P1 does not); the genuine-floor ramp ≥ 73 is conditional on P2 + P3 + P5 (not independent +1s; P5's emit-fixable gain is the CGE cluster, hhfair = Case-c).

---

## Sprint 31 — Final Summary (Day 13)

_(To be completed at closeout — final metrics table, per-priority summary, determinism verification, Sprint-32 carryforwards.)_
