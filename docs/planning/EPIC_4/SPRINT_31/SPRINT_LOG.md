# Sprint 31 — Progress Log

**Sprint:** 31 (Head-Offset IR Plumbing, General-Alias AD #1111/#1112 & Dual-Consistent CGE — Sprint 30 carryforwards)
**Day-0 baseline (`BASELINE_METRICS.md`):** Parse 142 · Translate 135 · Solve 107 · Match 92 (genuine floor 70) · model_infeasible 7 · Tests 4,997 · anchor `ea4191dc`.

| Day | Priority / Work | Metric delta | Status |
|---|---|---|---|
| 0 | Kickoff + Day-0 traces (PR24) + tractability probes (P1 round-trip / P3 `/tmp` prototype / P5 hhfair control) | — (baseline confirmed: Parse 142 · Translate 135 · Solve 107 · Match 92 · genuine 70; `DAY0_TRACES.md`) | ✅ DONE |
| 1 | P1 Phase 1: head-offset IR plumbing (`EquationDef.head_domain_offsets` field addition) | — (round-trip fixture green; 5 head-offset models byte-identical to goldens — field inert) | ✅ DONE |
| 2 | P1 Phase 2: shared 3-site helper (heaviest day) | — (helper `head_offset_marginal_index_map` wired to Site 2 dual-transfer; Sites 1/3 verified already-correct; blast radius 0) | ✅ DONE (WIP: Day-3 4th-site gate) |
| 3 | P1 mine close-or-REPLAN (cold-INFES-by-direction gate) | — (target: mine → MS-1, +1 Solve; REPLAN on a 4th site) | 🔵 PENDING |
| 4 | P2 offset-alias #1111/#1112 core (polygon): coupled objective + distance second-index | — (target: coupled fix lands, tightly gated) | 🔵 PENDING |
| 5 | P2 finish (shape8 enable, warm-match 0.780) + Checkpoint 1 | — (target: polygon genuine floor +1; REPLAN on gate leak) | 🔵 PENDING |
| 6 | P3 camcge dual-consistent Walras (start; `/tmp` prototype → src) | — (target: dual-consistent redefinition + S1∧S2∧S3 detector) | 🔵 PENDING |
| 7 | P3 camcge close-or-REPLAN (MS-1 @ 191.7346 + detector precision) | — (target: camcge → MS-1, +1 Solve; REPLAN to per-model-numéraire) | 🔵 PENDING |
| 8 | P4 sarf symbolic emit (start): 2-D gate + parametric `stat_task` | — (target: 2-D `_is_blowup_dynamic_subset_equation` + no set-name literals) | 🔵 PENDING |
| 9 | P4 sarf tractability gate (O(constraints)) + Checkpoint 2 | — (target: sarf → translate, +Translate; REPLAN on timeout) | 🔵 PENDING |
| 10 | P5 cold-convex obj-grad: CGE cluster `stat_xp` reduction (hhfair = Case-c) | — (target: irscge/lrgcge/moncge → Case-a, genuine floor; sign flip BANNED) | 🔵 PENDING |
| 11 | P6 rocket forcing → PATH-consultation input (`1/m` reformulation + continuation) | — (target: +1 Solve OR the finalized PATH-consultation input) | 🔵 PENDING |
| 12 | P7 infrastructure (shape8 + head-offset fixtures, genuine-floor tracking) + REPLAN-slack | — (target: property fixtures + PR25 re-baseline recompute) | 🔵 PENDING |
| 13 | Final retest (≥3 `PYTHONHASHSEED`) + closeout | — (target: Solve ≥109 / genuine floor ≥73 / determinism ✅) | 🔵 PENDING |

**Targets (`PROJECT_PLAN.md` §"Sprint 31"):** Solve 107 → ≥ 109 · Match maintain ≥ 92 / genuine floor 70 → ≥ 73 · model_infeasible 7 → ≤ 5 · Translate ≥ 135 (stretch +1 via #1385) · Tests ≥ 5,000 · determinism ✅.

**Honest KPI projection (`REPLAN_RISK_ASSESSMENT.md`):** Solve ≥ 109 (needs mine [P1] + camcge [P3]) is the most REPLAN-sensitive KPI (P3 has a per-model-numéraire fallback that still solves; P1 does not); the genuine-floor ramp ≥ 73 is conditional on P2 + P3 + P5 (not independent +1s; P5's emit-fixable gain is the CGE cluster, hhfair = Case-c).

---

## Day 2 — P1 Phase 2: shared head-offset index-map helper + Site-2 dual transfer (2026-07-10)

**Branch** `planning/sprint31-day2-headoffset-helper`. Emit-touching. **A decisive re-diagnosis overturned the plan's "3 identical maps" premise.**

**Empirical proof chain (GAMS available this session):**
1. **Cold mine MCP = MS-5** (`stat_x` Normal-Map inf-norm 4.07e10; `lam_pr` goes negative) — the baseline infeasibility.
2. **The emit (`comp_pr` Site 1 + `stat_x` Site 3) is ALREADY CORRECT.** Warm-starting the emitted MCP from the NLP optimum with the head-**shifted** dual transfer `lam_pr(k,l,i,j) = |pr.m(k,l+1,i,j)|` reaches **MS-1, profit 17500**; a direct LP solve of mine.gms is also **17500**. So the NLP KKT point is an exact LCP solution of the current emit — Sites 1 & 3 do not need changing (the plan assumed all 3 sites needed a coordinated fix).
3. **Site 2 (the `--nlp-presolve` dual transfer) was reading the wrong instance.** The NLP labels the equation instance — and stores `pr.m` — at the **shifted head label** `(k,l+1,i,j)` (confirmed: `pr.m` dumps at l ∈ {2,3,4}, e.g. `pr.m(se,4,1,1) = −7500`), while `lam_pr` is paired at the base `(k,l,i,j)`; the transfer read `pr.m(k,l,i,j)`.  **FIXED** via the new shared helper `head_offset_marginal_index_map` (`emit_gams.py`), which reads `head_domain_offsets` (Phase-1 field) and shifts the read to `pr.m(k,l+1,i,j)`.
4. **The "4th site" (Day-3 gate).** Even with the shifted transfer, mine's presolve MCP is **still MS-5 (22058)** until the `x.fx(l,i,j)$(not d(l,i,j)) = 0` fixing is relaxed. Isolation: shifted-transfer + `x.up=inf` for all (non-`d` left free, bound via `comp_up_x`) → **MS-1 17500**; shifted-transfer + `x.up(d)=inf` only (non-`d` kept fixed) → **MS-5 22058**. So hard-fixing the inactive non-`d` instances to 0 makes the LCP infeasible even from the exact NLP KKT warm point. This is the bound-complementarity 4th site the design §6 flagged → **Day 3 close-or-REPLAN.**

**Landed (Day 2):** the shared helper + Site-2 wiring; 5 unit + 3 integration tests (committed fixture `head_offset_ir_roundtrip.gms` is the always-run guard). **Blast radius zero** — all 13 committed `*_mcp_presolve.gms` goldens + all cold goldens byte-identical (Site 2 is presolve-only; only mine's uncommitted presolve emit changes). Quality gate green. **mine still `model_infeasible` — the +1 Solve is the Day-3 gate (relax/scope the non-`d` fixing, or REPLAN to Sprint-32 per §6).**

## Sprint 31 — Final Summary (Day 13)

_(To be completed at closeout — final metrics table, per-priority summary, determinism verification, Sprint-32 carryforwards.)_
