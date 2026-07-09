# Sprint 31 Detailed Schedule (Day 0 + Days 1–13)

**Task:** Sprint 31 Prep Task 10 (the terminal prep task — integrates Tasks 1–9)
**Date:** 2026-07-09
**Owner:** Sprint planning

---

## 1. Sprint 31 Goal

Land the Sprint-30 REPLAN'd Solve/Match carryforwards, each now carrying a Sprint-30 **control-verified recipe or precisely-pinned root cause** (`SPRINT_RETROSPECTIVE.md` §4). The deepest track — **P1 mine head-offset IR plumbing** — leads, because Sprint 30 Day 6 found it needs a **foundational IR change first** (the head-offset detail is not stored today), so the sprint plumbs it through parse → normalize → KKT and *then* builds the shared 3-site helper.

## 2. Acceptance Criteria (from `PROJECT_PLAN.md` §"Sprint 31")

- **Solve:** ≥ 109 (up from 107; +2 firm via mine [P1] + camcge [P3]; rocket [P6] a conditional +1)
- **Match:** maintain ≥ 92; **genuine floor 70 → ≥ 73** (polygon [P2] + hhfair/CGE [P5] convert warm/methodology matches to genuine)
- **model_infeasible:** ≤ 5 (−2 via mine + camcge)
- **Translate:** ≥ 135 (maintain; stretch +1 via #1385 sarf)
- **Parse:** ≥ 142 · **Tests:** ≥ 5,000 · **Determinism:** byte-identical under ≥ 3 `PYTHONHASHSEED` values

## 3. Sequencing Constraints (from the prep-task outputs)

- **P1 leads, contiguous:** Phase 1 (IR plumbing — a favorable field addition, Task 3) must land + its round-trip fixture must be green **before** Phase 2 (the shared 3-site helper). Days 1–3.
- **The genuine-floor ramp is conditional** (Task 7 / Sprint-30 §3): P2 + P3 + P5 are *not* independent +1s. **Solve ≥109 (mine + camcge) is the most REPLAN-sensitive KPI** — P3 has a per-model-numéraire fallback that still solves; P1 does not.
- **P5 is re-scoped by the Task-9 finding:** hhfair's `stat_u` already carries the correct log-derivative gradient → **hhfair leans genuine Case-c** (documented, no fix); the **emit-fixable P5 gain is the CGE cluster** (irscge/lrgcge/moncge `stat_xp`).
- **Day-0 tractability probes** (Task 10 §2) validate the three control-experiment tracks before the mid-sprint budget commits: P1 round-trip, P3 dual-consistent `/tmp` → MS-1, P5 hhfair ν_objective → Case-c confirm.
- **≤ 12 h/day**; the ~11 h heaviest day is the P1 Phase-1-finish + Phase-2 wiring (Day 2).

## 4. Day 0 — Kickoff + Day-0 Traces + Tractability Probes (≤ 6 h)

- Confirm Day-0 = Sprint 30 final (`BASELINE_METRICS.md`: **Solve 107 / Match 92 / genuine floor 70 / model_infeasible 7 / Translate 135 / Tests 4,997**). **Verify** `git diff ea4191dc..HEAD -- src/ scripts/` is empty before skipping the retest; if non-empty, run a fresh retest.
- **Day-0 traces (PR24)** — re-confirm each Phase-0 gate's `Traced Fix-Surface (Day-0)` `file:line` (`PHASE_0_ACCEPTANCE_GATES.md`): mine (`kkt_residual.py` CASE_B `stat_x(4,1,1)` 1.33 + the cold-INFES-by-direction histogram), polygon (CASE_B `stat_theta(i12)` 0.492), camcge (CASE_B + cold MS-4 singular), sarf (the 2-D gate + the emit-timing), hhfair (the inlined log-derivative `stat_u`), rocket (Case-c clean at the NLP point).
- **The three tractability probes (Task 10 §2):**
  - **P1 round-trip:** author + run `tests/fixtures/head_offset_ir_roundtrip.gms` — assert `head_domain_offsets[1] == IndexOffset('l', Const(1.0), False)` (the Phase-1 gate; must be green before the emit change).
  - **P3 dual-consistent `/tmp` prototype:** hand-edit `camcge_mcp.gms` with the dual-consistent redefinition → **reach MS-1 at omega 191.7346** before the `src/` change (check the dual side).
  - **P5 hhfair ν_objective control:** confirm the current `stat_u` log-derivative gradient is emit-correct → hhfair is **genuine Case-c** (documented; the sign flip stays BANNED); pivot P5 to the CGE cluster.
- **PR25 Day-0 tally:** restate genuine 70 / methodology 22; the genuine-floor → ≥ 73 conversion map (polygon P2 / hhfair-CGE P5 / mine P1). **Docs/trace-only (no `src/`).**

## 5. Day 1 — Priority 1 Phase 1: head-offset IR plumbing (~7 h)

- **The favorable foundational IR change (Task 3).** Add `EquationDef.head_domain_offsets` (a per-position `IndexOffset` tuple, mirroring `declaration_domain`) — the parser producer (`_domain_list_head_offsets` reusing `_process_index_expr`, replacing the bare `has_head_domain_offset` bool at `parser.py:3952`) + copy-through at the reconstructor sites (`sqr_reformulation.py:88/:108`, `complementarity.py:242`). `normalize` is a passthrough.
- **Phase-1 gate:** the round-trip fixture (Day-0) is green + the golden byte-diff shows **zero changes** (the field addition is inert until a consumer reads it — Unknown 1.4).
- **Verifies:** 1.1, 1.4. **PR (src/ir/, tests/). Est ~7 h.**

## 6. Day 2 — Priority 1 Phase 2: shared 3-site helper (heaviest day, ~11 h)

- **The shared head-offset index-map helper** parameterized by (head-offset δ on `l`, param offsets `li(k)`/`lj(k)` from the body), called **atomically** by the three sites: (1) `comp_pr` head-var emission, (2) the `--nlp-presolve` dual transfer (`_emit_nlp_presolve`, `emit_gams.py:1354`), (3) the landed `stat_x` cross-term (`_add_indexed_jacobian_terms`/`stat_x`, `stationarity.py:5767`). mine is a convex LP ⇒ the cold `x → 4e10` **is** the `comp_pr` LCP residual.
- **Verifies:** 1.2. **PR (emit-touching, atomic — a partial 3-site fix = no Solve gain). Est ~11 h (the P1 Phase-1-finish + Phase-2 wiring day).**

## 7. Day 3 — Priority 1: mine close-or-REPLAN (~6 h)

- **The cold-INFES-by-direction gate (Unknown 1.3):** re-solve mine cold; the shared helper must drive **all four k-directions (nw/ne/se/sw) → 0**, cold **MODEL STATUS 1** (from the ~4.07e10 baseline). **PROCEED** (+1 Solve, mine `model_infeasible → model_optimal`; +1 genuine floor if it cold-matches) if yes.
- **REPLAN exit (prior Medium):** a **4th bound-complementarity site** (`comp_lo_x`/`comp_up_x`) persisting after the `comp_pr` fix → file the **Sprint-32 head-offset-Phase-3 workstream**; the IR plumbing + helper still land (reusable foundation). Freed ~10–14 h → P5/P7 (Task 7 reallocation).
- **Verifies:** 1.3. **REPLAN exit explicit. PR. Est ~6 h.** *(P1 total ~24 h across Days 1–3.)*

## 8. Days 4–5 — Priority 2: offset-alias #1111/#1112 core (polygon) + Checkpoint 1 (~16 h)

- **The coupled fix, tightly gated (Task 4).** Land the **objective-successor half** (`_build_indexed_gradient_term`, `stationarity.py:2864` — the interior-representative selection) **and** the **distance-Jacobian second-index half** (`_add_indexed_jacobian_terms`, `stationarity.py:5767` — the new per-position complementary sum, inverted multiplier order + flipped `ord`) **together** — neither alone matches (objective-alone regresses polygon to MS-5). #1110 is orthogonal (single-scalar diagonal-vs-off-diagonal vs a whole position-keyed sum). himmel16 is a **non-convex scope guard** (no fix).
- **Completion gate:** drop `shape8_offset_alias_successor`'s `strict=True` xfail + polygon warm-matches 0.780 + the CGE multi-pattern GO list byte-stable.
- **Day 5 — Checkpoint 1:** `--resolve-changed --since-commit ea4191dc` re-solve of the changed-golden set + golden-staleness + the PR25 re-baseline recompute. NO-GO if any changed-golden model moved backward.
- **REPLAN exit (prior Medium):** the var-at-two-indices gate leaks into the CGE cohort → the **Sprint-32 #1111/#1112 AD-engine filing**; polygon's genuine-floor +1 becomes conditional.
- **Verifies:** 2.1, 2.2, 2.3, 2.4. **REPLAN exit explicit. PR (emit-touching). Est ~16 h (~8/day).**

## 9. Days 6–7 — Priority 3: camcge dual-consistent Walras transform (~15 h)

- **Land the src from the Day-0-proven `/tmp` prototype (Task 5; Epic 5).** Keep **every** market-clearing row (no orphaned dual) + a consumption-weighted numéraire (on `cles(i)`/`pd0(i)`) + **redefine the redundant market's dual via Walras' law** so the dual block is full-rank → MS-1. Guard with the **S1∧S2∧S3 degeneracy detector** (S3 cold-MCP-singular = the false-positive guard; pass-through default — never transform a well-posed model).
- **The empirical gate (Unknown 3.1/3.2):** **PROCEED** if transformed camcge reaches **MODEL STATUS 1 at omega 191.7346** (non-singular basis) **and** the detector flags only camcge across irscge/lrgcge/moncge/stdcge; **REPLAN to a per-model-numéraire declaration** (opt-in, still lands camcge's +1 Solve — the sole inherent Walras case) if the `/tmp` prototype can't reach MS-1 or the auto-heuristic false-flags.
- **Verifies:** 3.1, 3.2, 3.3, 3.4. **REPLAN exit explicit. PR (emit-touching). Est ~15 h (~7.5/day).**

## 10. Days 8–9 — Priority 4: #1385 sarf symbolic runtime-guard emit (~16 h)

- **The atomic symbolic-emit rebuild (Task 9).** Two coupled sites: (1) extend `_is_blowup_dynamic_subset_equation` (`index_mapping.py:402`, the `len(eq_domain) != 1` bail) from srpchase's 1-D to sarf's **2-D** dynamic-subset-condition shape (`tbal(g,t)$taskposs`, `equipb1(m,t)$equipposs`, `equipb2(n,t)$equipposs`); (2) a **new parametric `stat_task` emit** in `stationarity.py` differentiating each short-circuited body **once** in `(g,t,m,n)` — the banked 6-guarded-term derivation, `$taskposs`/`$equipposs` guards, **no set-name multiplier indices** (the Sprint-26 `nu_slack("srn")` failure). **Atomic** (re-emit + cross-terms together — a partial is an inconsistent MCP).
- **The tractability gate (Unknown 4.1/4.2/4.3):** the emit must be **O(constraints), not O(instances)** (1,152 Cartesian instances). Time `sarf_mcp.gms`; **PROCEED** (+Translate, sarf `translate_failure → translate`) if sub-budget; **REPLAN to Sprint 32** if the symbolic re-emit re-triggers the per-instance timeout.
- **Verifies:** 4.1, 4.2, 4.3. **REPLAN exit explicit. PR (emit-touching). Est ~16 h (~8/day).**

## 11. Day 10 — Priority 5: cold-convex obj-grad (CGE cluster) + Checkpoint 2 (~11 h)

- **The ν_objective reduction on the CGE cluster (Task 9 — the emit-fixable P5 target).** Route the objective gradient of the objective-defining-intermediate-variable through the defining-equation multiplier ν_objective (`src/ad/gradient.py` / `src/kkt/stationarity.py`) → convert the **CGE cluster** (irscge/lrgcge/moncge `stat_xp` rel ~0.06, convex) to **Case-a** (residual → 0). A single structural rule; orthogonal to the Day-5 case-normalization fix. **THE SIGN FLIP STAYS BANNED** (refuted 3×). **hhfair is documented genuine Case-c** (its `stat_u` is already emit-correct — no fix; the Day-0 probe confirmed).
- **The control gate (Unknown 5.1/5.2):** the reduction must reach the residual → 0 on the CGE cluster **before** the (high-blast-radius) obj-grad `src/` change; **REPLAN** to a documented Case-c finding for the family if it doesn't.
- **Day 10 — Checkpoint 2:** `--resolve-changed` re-solve + golden-staleness + PR25 tally.
- **Verifies:** 5.1, 5.2, 5.3, 5.4. **REPLAN exit explicit. PR (emit-touching). Est ~11 h.**

## 12. Day 11 — Priority 6: rocket forcing → PATH-consultation input (~9 h)

- **Exhaust the emittable levers (Task 9).** Re-confirm the emit residual is clean at the NLP point (Case-c) **before** forcing (PR27). Then try the **`1/m` / `1/ht²` division-by-variable reformulation** (an auxiliary `w(h)` with `w(h)·m(h) =e= X`, removing the division-by-variable from the ill-conditioned Jacobian) + scaled/relaxed continuation via the landed `--force` scaffold.
- **Disposition (Unknown 6.1/6.3, prior High):** **+1 Solve** if the reformulation converges rocket; else **finalize the PATH-consultation input** for the renumbered Sprint 32 (the scaffold + the concrete question are the de-risked hand-off) — rocket's +1 Solve is conditional.
- **Verifies:** 6.1, 6.2, 6.3. **PR (emit-touching if the reformulation lands, else docs). Est ~9 h.**

## 13. Day 12 — Priority 7 infrastructure + REPLAN-slack (~9 h)

- **P7 property fixtures:** confirm `shape8_offset_alias_successor` enabled (the P2 completion gate, once P2 landed) + add the **head-domain-offset fixture** (`head_offset_ir_roundtrip.gms`, guarding the P1 index-map). Recompute the **PR25 genuine-floor tracking** against the S31–S34 re-baselined Match KPIs (footnote ⁸ ramp S31 ≥ 73). Refresh the `--resolve-changed` checkpoint targets.
- **REPLAN-slack absorption:** whatever the mine [P1] / polygon [P2] / sarf [P4] / hhfair-CGE [P5] REPLANs freed re-allocates here per the Task-7 reallocation order (P5 → P7 → the +Translate/forcing tails).
- **Verifies:** 7.1, 7.2, 7.3. **PR. Est ~9 h.**

## 14. Day 13 — Final Retest + Closeout (~8 h)

- **Full pipeline retest** under ≥ 3 `PYTHONHASHSEED` values (PR12); recompute the DB (machine-portable paths) + the Sprint 30 → 31 metrics comparison; **PR25 genuine-vs-methodology re-baseline** recomputed (genuine floor → ≥ 73 target).
- **Closeout:** `SPRINT_LOG.md` final entry + top-table + per-priority summary; `SPRINT_RETROSPECTIVE.md` authored; Sprint-32 carryforwards filed (mine if REPLAN'd, the #1111/#1112 core if P2 REPLAN'd, sarf if P4 REPLAN'd, the per-model-numéraire fallback if P3 REPLAN'd, rocket PATH consultation, hhfair Case-c). **Est ~8 h.**

---

## 15. Budget Summary

| Day(s) | Work | Est (h) |
|---|---|---|
| 0 | Kickoff + Day-0 traces + tractability probes (P1 round-trip / P3 `/tmp` prototype / P5 hhfair control) | ~6 |
| 1 | P1 Phase 1: head-offset IR plumbing (field addition) | ~7 |
| 2 | P1 Phase 2: shared 3-site helper (heaviest day) | ~11 |
| 3 | P1 mine close-or-REPLAN (cold-INFES gate) | ~6 |
| 4–5 | P2 offset-alias #1111/#1112 core (polygon) + Checkpoint 1 | ~16 |
| 6–7 | P3 camcge dual-consistent Walras (REPLAN-gated) | ~15 |
| 8–9 | P4 #1385 sarf symbolic emit (REPLAN-gated) | ~16 |
| 10 | P5 cold-convex obj-grad (CGE cluster) + Checkpoint 2 | ~11 |
| 11 | P6 rocket forcing/PATH input | ~9 |
| 12 | P7 infrastructure + REPLAN-slack | ~9 |
| 13 | Final retest + closeout | ~8 |
| **Total** | | **~114 h** (mid; ~92 h if the deep tracks REPLAN early, ~134 h if all PROCEED) |

**Fits the 168 h cap** with ≥ 54 h slack at the mid-estimate; **no day > 12 h** (heaviest ~11 h on Day 2, the P1 Phase-1-finish + Phase-2 wiring). The lower bound assumes the REPLAN-prone tracks (P1 mine +1 Solve, P2/P5 genuine-floor lift) slip per Task 7; the **firm parts land regardless** — the IR plumbing + helper, the P2 second-index design, camcge (via the fallback), the sarf re-scoping finding, the CGE-cluster reduction, the rocket scaffold + PATH input, the P7 infra.

## 16. Phase 0 Coverage Audit (PR20 + PR24)

All six emit-touching tracks have a Phase-0 gate authored/refreshed in prep (Task 6): `PHASE_0_ACCEPTANCE_GATES.md` + the per-issue `## Phase 0` sections in `docs/issues/ISSUE_{1443,1143,1330,1385,1236,1462}_*.md` (all keep the 4 required `###` subsections). Each gate's `Traced Fix-Surface (Day-0)` line is re-confirmed Day 0 before any `src/` change; each cites `kkt_residual.py` (PR27) + carries a control-experiment-before-src rule (the sign flip is BANNED for P5).

## 17. Known Unknowns Status Snapshot

All **25** Sprint-31 prep unknowns are **✅ VERIFIED** after Tasks 1–9, **except Unknown 4.2** (the sarf O(constraints) *empirical* result), which is legitimately the in-sprint P4 Day-9 gate (its fix surface + tooling are pinned; only the fix-outcome timing remains). Three notable prep findings the schedule absorbs (no WRONG inversions this sprint, unlike Sprint 30's robert):
- **Task 3 (favorable):** the head offset is discarded at *parse*, so P1 Phase 1 is a **field addition, not a deep normalize rewrite** — de-risking the deepest track's foundation (Days 1).
- **Task 4 (2 PR24 corrections):** the offset-alias second-index drop is in `stationarity.py:5767` (`_add_indexed_jacobian_terms`), **not** `constraint_jacobian.py` as the banked surface named — the schedule points Day 4–5 at the corrected site.
- **Task 9 (P5 re-scope):** hhfair's `stat_u` is already emit-correct → **hhfair leans genuine Case-c** (documented Day 0/Day 10, no fix); the emit-fixable P5 gain is the **CGE cluster** — the schedule targets Day 10 P5 at irscge/lrgcge/moncge, not hhfair.

## 18. Risk Register + Mitigations

| Risk | Mitigation |
|---|---|
| Solve ≥ 109 misses (needs mine [P1] + camcge [P3]) | Honest projection (Task 7): the +2 Solve is REPLAN-sensitive; **P3 has a per-model-numéraire fallback that still solves** (P1 does not) — so P3 is the more robust Solve mover. |
| mine 3-site fix exposes a 4th bound-complementarity site (Day-3 cascade) | Explicit REPLAN mine → Sprint-32 head-offset-Phase-3; the IR plumbing + helper land regardless (reusable foundation). |
| P2 var-at-two-indices gate leaks into the CGE multi-pattern cohort | REPLAN to the Sprint-32 #1111/#1112 AD-engine filing; polygon's genuine-floor +1 becomes conditional. |
| P5 hhfair proves the *only* fixable target (CGE distinct) | The CGE cluster is the primary P5 gain; hhfair is already documented Case-c (Task 9) — the schedule does not depend on hhfair. |
| #1385 sarf symbolic re-emit re-triggers the translate-timeout | The O(constraints) tractability gate (Day 9); REPLAN to Sprint 32 if it re-enumerates. |
| Day over-pack (Sprint 27 Day-12 lesson) | No day > 12 h (heaviest ~11 h Day 2); Day 12 P7-infra/slack is absorptive, not a hard commitment. |

## 19. Related Documents

- `PROJECT_PLAN.md` §"Sprint 31" · `KNOWN_UNKNOWNS.md` · `BASELINE_METRICS.md` · `HEAD_OFFSET_IR_PLUMBING_DESIGN.md` · `OFFSET_ALIAS_JACOBIAN_DESIGN.md` · `CAMCGE_DUAL_CONSISTENT_DESIGN.md` · `PHASE_0_ACCEPTANCE_GATES.md` · `REPLAN_RISK_ASSESSMENT.md` · `TOOLING_READINESS_AUDIT.md` · `BACKLOG_FIX_SURFACE_ANALYSIS.md` · `prompts/PLAN_PROMPTS.md`
