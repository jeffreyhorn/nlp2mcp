# Sprint 31 — Retrospective

**Sprint:** 31 (Head-Offset IR Plumbing, General-Alias AD #1111/#1112 & Dual-Consistent CGE — Sprint 30 carryforwards)
**Closed:** 2026-07-13 (Day 13)
**Final metrics (142 corpus):** Parse 142 · Translate 135 · **Solve 107** · **Match 92** (genuine floor **74**) · model_infeasible 7 · determinism ✅ ×3 `PYTHONHASHSEED` {0,1,42} · Tests 5,074 passed (green). **All-219 Match tally 95** (+3 non-candidate ps2/ps3).

---

## 1. Outcome vs targets

| KPI | Day-0 | Target | Final | Met? |
|---|---|---|---|---|
| Solve | 107 | ≥ 109 | 107 | ❌ (both +1s — mine [P1], camcge [P3] — REPLAN'd) |
| Match (142-corpus) | 92 | maintain ≥ 92 | 92 | ✅ |
| genuine floor | 70 | ≥ 73 | **74** | ✅ (P2 delivered +4) |
| model_infeasible | 7 | ≤ 5 | 7 | ❌ (−2 was mine/camcge/rocket) |
| Translate | 135 | ≥ 135 (stretch 136) | 135 | ✅ / stretch ❌ (sarf #1385 REPLAN'd) |
| Determinism / Tests | — | ✅ / ≥ 5,000 | ✅ ×3 / 5,074 | ✅ |

**Both *stated* targets — Match maintain ≥ 92 and genuine floor ≥ 73 — were MET, and the genuine floor over-delivered (74 vs the ≥ 73 step) on a single track (P2).** The two Solve-side stretches (Solve ≥ 109, model_infeasible ≤ 5) missed by exactly 2 — the REPLAN'd deep tracks mine [P1], camcge [P3], and rocket [P6], all rated High/REPLAN-prone up front. No regression: every 142-corpus bucket is ≥ its Day-0 value.

## 2. What landed (firm)

- **P2 offset-alias #1111/#1112 (polygon core)** — the sole genuine emit track, and it over-delivered. The general-alias **second-index-transpose** cross-term (`_var_at_two_indices_complement` + `_build_complement_index_sum`, with the diagonal-exclusion + inverted-multiplier + flipped-`ord` machinery) is **not polygon-specific**: it converted polygon (methodology→genuine cold emit) **and** ps2_f_s / ps2_s / ps3_s_gic (live mismatch → genuine match). **+4 genuine floor** (70 → 74), **+3 all-219 matches** (92 → 95). Coupled with the interior-representative objective-gradient selection (`_count_additive_terms`).
- **P1 head-offset IR foundation (Days 1–2, #1443)** — `EquationDef.head_domain_offsets` (Phase-1 IR field, per-position offset tuple) + the shared `head_offset_marginal_index_map` Site-2 dual-transfer helper. The *track* REPLAN'd (Day 3), but the IR plumbing landed on main and is the de-risked foundation for the Sprint-32 mine 4th-site work.
- **P7 infrastructure (Day 12)** — the shape8/shape10/shape11 + head-offset property fixtures (35 tests green), the `--resolve-changed` checkpoint discipline, and the finalized PR25 genuine-floor tracking.

## 3. What we'd do differently / key lessons

1. **The PR24/PR27 control-first discipline caught FIVE wrong fix premises before shipping — this was the sprint's defining pattern.** Every deep track that REPLAN'd did so because a control experiment or the KKT-residual harness *refuted its design premise* before any high-blast-radius `src/` change: P1 mine (measurement error — the "MS-1 17500" was the embedded LP, not the MCP; `x.up=inf` produced 34 unmatched-variable errors), P3 camcge (CASE_B `stat_mps`, not clean Walras dual-singularity), P4 sarf (the blow-up is the 369K-instance 4-D `task` var, not the 1,152 constraints), P5 CGE-cluster+hhfair (the ν_objective reduction is inert; genuine Case-c non-convexity), P6 rocket (division-by-variable reformulation exhausted; intrinsic non-convergence). **Keep the gate — for non-convex / objective-defining-intermediate-variable shapes the single-point harness residual and the banked fix-surface are systematically misleading.**

2. **The Day-2/3 measurement error is the cautionary tale of the sprint.** The Day-2 record claimed mine's emit "warm-solves to MS-1 17500" — but relaxing `x.up=inf` produced 34 "Unmatched variable not free or fixed" errors, so the MCP *never solved*; the 17500 was the embedded `$include` LP. Caught Day 3 by explicitly checking `mcp_model.modelstat` and the harness (CASE_B `stat_x` 2.37). **Lesson: never read an objective off a solve without first asserting the model actually solved (modelstat), especially when a bound-relaxation experiment could have silently produced an unmatched-variable model.**

3. **The genuine-floor ramp was carried entirely by ONE track — exactly the Sprint-30-retro §3 conditionality warning realized.** The projection treated the ramp as polygon [P2] + hhfair/CGE [P5] + mine [P1], "not as independent +1s." In the event, P5's CGE cluster was control-refuted as genuine Case-c (0 delta) and P1 REPLAN'd (0 delta), so **P2 alone** carried 70 → 74. The floor is 74, not the nominal 77 headroom. **Sprint-32 planning should assume the genuine-floor ramp advances only via tracks whose fix genuinely changes the emit (the #1111/#1112 family), not via presolve-methodology reclassification.**

4. **The headline Match KPI and the genuine floor measure different populations — state which one you mean.** The 142-corpus Match KPI (`verified_convex + likely_convex`) stayed **92** because the P2 gains land on **non-candidate `non_convex` models** (ps2/ps3) plus an already-matching candidate (polygon). The +3 shows only in the all-219 tally (95) and the genuine floor (74). The Day-5/Day-12 "as-measured Match 95" phrasing conflated the two; the Day-13 recompute pins it: **corpus KPI 92 (maintained), all-219 tally 95, genuine floor 74.** **Lesson: every Match number must carry its scope (142-corpus vs all-219).**

5. **Control experiments turn "REPLAN with a shrug" into "REPLAN with a recipe" — Sprint 32 inherits specifications, not open questions.** mine has the cold-INFES-by-direction characterization + the 4th bound-complementarity site; sarf has the O(instances) 369K finding (needs a 4-D `task`-var gate, not O(constraints)); camcge has the CASE_B `stat_mps` diagnosis (→ Epic 5); rocket has the finalized PATH-consultation question with the division-by-variable reformulation now a *ruled-out* candidate; the CGE cluster + hhfair are documented genuine Case-c. Each is a de-risked hand-off.

## 4. Sprint-32 carryforwards

See the SPRINT_LOG Day-13 "Sprint-32 carryforwards" table: **mine** (#1443, P1 — 4th bound-complementarity site; head-offset IR foundation on main), **sarf** (#1385, P4 — 4-D `task`-var stationarity gate, not O(constraints)), **camcge** (#1330, P3 → Epic 5 — dual-consistent Walras / CASE_B `stat_mps`), **rocket** (#1462, P6 — PATH-consultation on intrinsic discretized-optimal-control non-convergence; `--force` scaffold + finalized question), and **hhfair + the CGE cluster** (#1236, P5 — documented genuine Case-c, non-convex, presolve warm-start required). Each has a banked recipe/diagnosis in its ISSUE doc.

---

**SPRINT 31 CLOSED.**
