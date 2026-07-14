# Sprint 32 Detailed Schedule (Day 0 + Days 1–13)

**Created:** 2026-07-14
**Prep Task:** 11 (the final prep task — integrates Tasks 1–10)
**Budget:** 80–120 h over 14 days (Day 0 + Days 1–13) at ≤ 12 h/day (168 h cap); Risk **HIGH**.
**Day-0 anchor:** `4cbf8bff` (Sprint 31 close).

---

## 1. Sprint 32 Goal

Land the five Sprint-31 REPLAN'd Solve/Match carryforwards, each now carrying a **precisely-pinned root cause** (`SPRINT_31/SPRINT_RETROSPECTIVE.md` §4), not an open question. The two firm **+Solve** movers — **P1 mine head-offset 4th bound-complementarity site** and **P3 camcge `stat_mps` + dual-consistent Walras** — lead, front-loaded across Days 1–5 so a REPLAN surfaces by the **Day-5 checkpoint**, not Day 11 (the Sprint-31 lesson: the two Solve-side targets missed by exactly the REPLAN'd deep tracks). The IR foundation for P1 (`EquationDef.head_domain_offsets` + the Site-2 dual transfer) already landed in Sprint 31 — Sprint 32's P1 is the residual bound-multiplier fix, a **local presolve-transfer change**.

## 2. Acceptance Criteria (from `PROJECT_PLAN.md` §"Sprint 32")

- **Solve ≥ 109** (up from 107; +2 firm via mine [P1] + camcge [P3]); **model_infeasible ≤ 5** (down from 7).
- **Match maintain ≥ 92** as-measured; **genuine floor 74 → ≥ 75** (mine [P1] + camcge [P3] cold-matches convert; any P6 emit gain).
- **Translate ≥ 135 → +1 (136)** via #1385 sarf [P2]; **Parse 142** maintain.
- **Tests ≥ 5,080** (up from 5,074); **Determinism** byte-identical under ≥ 3 `PYTHONHASHSEED` (PR12).

## 3. Sequencing Constraints (from the prep-task outputs)

- **Front-load the two firm +Solve movers (P1 mine Days 1–3 + P3 camcge Days 4–5)** so both close-or-REPLAN gates fire by the **Day-5 checkpoint** (Task 9: Solve ≥ 109 is the most REPLAN-sensitive KPI — it needs BOTH).
- **The genuine-floor ramp is conditional** (Task 9 / Sprint-30 §3 / Sprint-31 §3): genuine floor ≥ 75 advances only via an **emit-changing** track (mine/camcge cold-match, or the P6 #1111/#1112 generalization), **NOT** via presolve-methodology reclassification — **P5 delivers 0 floor** (documented Case-c).
- **camcge [P3] is a split track:** step 1 (`nu_mps_fx.l = -mps.m`) is a general emit fix that lands regardless; step 2 (the Epic-5 Walras) is `/tmp`-prototype-gated.
- **Reallocation order on any REPLAN (Task 9):** P6 (offset-alias generalization + failure-cohort) → P7 (property fixtures + genuine-floor tracking) → the rocket [P4] forcing tail.

## 4. Day 0 — Kickoff + Day-0 Traces + Tractability Probes (≤ 6 h)

- Confirm Day-0 = Sprint 31 final (`BASELINE_METRICS.md`: **Solve 107 / Match 92 / genuine floor 74 / model_infeasible 7 / Translate 135 / Tests 5,074**). **Verify** `git diff 4cbf8bff..HEAD -- src/ scripts/` is empty before skipping the retest; if non-empty, run a fresh retest.
- **Day-0 traces (PR24)** — re-confirm each Phase-0 gate's `Traced Fix-Surface (Day-0)` `file:line` (`PHASE_0_ACCEPTANCE_GATES.md`): mine (`kkt_residual.py` CASE_B `stat_x(3,1,1)` rel 2.37, duals CONSISTENT), camcge (CASE_B `stat_mps` `mps.m = −209.861`), sarf (the 2-D gate + the 369K-vs-398-active timing), rocket (Case-c clean at the NLP point — boundary `stat_ht`/`stat_step`), hhfair (D1 `stat_u` rel 2.0, `nu_obj=±1`).
- **The three tractability probes (Task 10 §1 / the Task-9 single-model validations):**
  - **P1 warm-residual→0 `/tmp` prototype:** apply the `N`-derivation (`piL_x = max(N,0)`, `piU_x = max(−N,0)`) to a scratch `mine_mcp_presolve.gms` → the harness reports **Case-a** at the bound-active `stat_x` rows (`modelstat` asserted) **before** the `src/` change.
  - **P3 dual-consistent `/tmp` prototype:** hand-edit `camcge_mcp.gms` with step 1 (`nu_mps_fx.l = -mps.m`) + the dual-consistent Walras redefinition → reach **MS-1 at omega 191.7346** (check the dual side) before the `src/` change.
  - **P2 sarf O(active) timing probe:** confirm the sparsified `stat_task$taskposs` emits **398 active**, not 369,024 Cartesian — time the translate (target seconds, cf. srpchase's 1-D 6.56 s; the failure is > 180 s).
- **PR25 Day-0 tally:** restate genuine 74 / methodology 21; the genuine-floor → ≥ 75 conversion map (mine [P1] + camcge [P3] cold-match; P6 cpack/fawley emit gain). **Docs/trace-only (no `src/`).**

## 5. Day 1 — Priority 1: mine bound-multiplier emit (start) (~6 h)

- **The stationarity-consistent bound-multiplier derivation (Task 3).** Replace the presolve bound-multiplier transfer (`src/emit/emit_gams.py:1548–1577`, currently `piL_x/piU_x = ±x.m`, the LP reduced cost) with the **residual-`N` derivation** `piL_x = max(N,0)`, `piU_x = max(−N,0)` (where `N` = the non-bound part of `stat_x` after the `lam_pr` transfer) — closing `stat_x = N − piL_x + piU_x = 0` at bound-active rows. **Gate the `N`-derivation to the head-offset-coupled case** (or `--resolve-changed`-verify) so the non-mine presolve cohort stays byte-stable.
- **Phase-0 gate:** `docs/issues/ISSUE_1443_*.md` §P1 (the Day-0 `/tmp` warm-residual→0 must be Case-a before src). **Emit-touching PR (WIP if incomplete). Est ~6 h.**

## 6. Day 2 — Priority 1: mine warm→cold verification (~6 h)

- **The warm-residual→0 gate (Unknown 1.1).** Re-run `kkt_residual.py mine.gms` after the `N`-derivation transfer → **warm residual → 0 (Case-a**, `modelstat` asserted). Then the **presolve solve → MS-1** (+1 Solve; +1 genuine floor if it cold-matches). Confirm the S31 head-offset foundation regression guard stays green (16 tests: `test_head_domain_offsets.py` + `test_head_offset_presolve_transfer.py` + `test_head_offset_marginal_map.py`) and the non-mine presolve goldens byte-stable (`--resolve-changed`).
- **Verifies:** 1.1. **Emit-touching PR. Est ~6 h.**

## 7. Day 3 — Priority 1: mine close-or-REPLAN (~5 h)

- **The 5th-coupling gate (Unknown 1.2).** **PROCEED** (mine `model_infeasible → model_optimal`, +1 Solve; +1 genuine floor if cold-match) if the warm residual closes with no fresh residual. **REPLAN (prior Medium)** if a **5th coupling** surfaces — a fresh `stat_x` residual persists at the NLP optimum, or `sign(N)` contradicts the bound-active status → file a **Sprint-33 deeper head-offset bound-complementarity architecture**; the bound-multiplier design + the S31 IR foundation hand off cleanly. Freed ~8–14 h → **P6 + P7** (Task 9 reallocation).
- **Verifies:** 1.2. **REPLAN exit explicit. PR. Est ~5 h.** *(P1 total ~17 h across Days 1–3.)*

## 8. Days 4–5 — Priority 3: camcge `stat_mps` + dual-consistent Walras + Checkpoint 1 (~15 h)

- **Day 4 — step 1 (general emit fix) + step 2 (Walras src from the Day-0 `/tmp` prototype) (~7.5 h).** Step 1: extend the #1462 fixed-variable-marginal transfer block (`src/emit/emit_gams.py`) to emit `nu_mps_fx.l = -mps.m` (sign per the multiplier's stationarity role; `mps.m = −209.861`) → `stat_mps` **Case-a**. Step 2 (Epic 5): keep every market-clearing row + the consumption-weighted numéraire + redefine the redundant market's dual via Walras' law; guard with the **S1∧S2∧S3 degeneracy detector** (S3 cold-MCP-singular = the false-positive guard; pass-through default).
- **Day 5 — camcge close-or-REPLAN + Checkpoint 1 (~7.5 h).** **The empirical gate (Unknown 3.1/3.2): PROCEED** if the transformed camcge reaches **MS-1 at omega 191.7346** (non-singular basis) **and** the detector flags only camcge across irscge/lrgcge/moncge/stdcge (+1 Solve); **REPLAN** (step 1 still lands as a cleaner CASE_B → Case-a general emit fix; the numéraire → a per-model-numéraire-declaration **Epic-5** item — camcge stays `model_infeasible` in S32; freed step-2 ~6–12 h → **P6 + P7**) if the `/tmp` prototype can't reach MS-1 or the detector false-flags.
- **Checkpoint 1 (Day 5):** `--resolve-changed --since-commit 4cbf8bff` re-solve of the changed-golden set (bucket-diff vs the committed DB) + golden-staleness + the PR25 re-baseline recompute. **NO-GO** if any changed-golden model moved backward (`match→mismatch`, `model_optimal→model_infeasible`, presolve-match→abort). **Both firm +Solve movers (mine + camcge) have now fired their PROCEED/REPLAN gates.**
- **Verifies:** 3.1, 3.2, 3.3, 3.4. **REPLAN exit explicit. PR (emit-touching). Est ~15 h (~7.5/day).**

## 9. Days 6–8 — Priority 2: sarf 4-D `task` stationarity sparsification (~17 h)

- **The atomic O(active) symbolic re-emit (Task 4).** Two coupled sites, landed **atomically** (a partial = an inconsistent MCP): (1) extend `_is_blowup_dynamic_subset_equation` (`src/ad/index_mapping.py`) from srpchase's 1-D to sarf's **2-D** dynamic-subset shape (`tbal(g,t)$taskposs`, `equipb1/equipb2`); (2) a **new parametric `stat_task` emit** in `src/kkt/stationarity.py` — one symbolic guarded `stat_task(g,t,m,n)$taskposs(g,t)` (the banked 7-guarded-term derivation) + `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0`, **no set-name-literal multiplier indices** (the Sprint-26 `nu_slack("srn")` failure, commit `243fe578`; scan `grep -En 'nu_[[:alnum:]_]+\("' sarf_mcp.gms` = empty).
- **The tractability gate (Unknown 2.1, Day 7).** The re-emit must be **O(active = 398), not O(369,024)** — time `sarf_mcp.gms` (target seconds, well under the > 180 s Option-1 timeout). **PROCEED** (sarf `translate_failure → translate`, +1 Translate) if sub-budget; **REPLAN to Sprint 33** (a documented parametric-emit re-scoping; freed ~8–16 h → P6 + P7) if it re-triggers the timeout.
- **Day 8 close:** golden byte-stable (sarf's *new* `sarf_mcp.gms` golden — caught by the golden-staleness gate, since `--resolve-changed` diffs existing goldens); `--resolve-changed` GO.
- **Verifies:** 2.1, 2.2, 2.3, 2.4. **REPLAN exit explicit. PR (emit-touching). Est ~17 h (~5.5/day).**

## 10. Day 9 — Priority 4: rocket PATH-consultation input (~9 h)

- **Re-confirm + finalize the packaged hand-off (Task 6).** Re-confirm the emit residual is **clean at the NLP point (Case-c boundary signature** — `stat_ht(h0)`/`stat_step`/`stat_ht(h50)` move with the warm-start value, interior near tolerance**) before** any forcing (PR27). Confirm no untried emittable lever crosses (PATH options 477→382, μ-continuation / multistart / the division-by-variable reformulation all MS-5 in prep).
- **Disposition (Unknown 4.1, prior — hand-off):** **finalize the PATH-consultation input** for the renumbered Sprint 33 (`ROCKET_PATH_CONSULTATION_INPUT.md` — the concrete question + the ruled-out-lever survey + the `--force` scaffold); **+1 Solve only if** a lever unexpectedly crosses. rocket's +1 Solve is a conditional Sprint-33 hand-off.
- **Verifies:** 4.1, 4.2, 4.3. **PR (docs, unless a lever lands emit). Est ~9 h.**

## 11. Day 10 — Priority 5: hhfair + CGE Case-c classifier + Checkpoint 2 (~8 h)

- **The `kkt_residual.py` Case-c auto-classifier extension (Task 7 — no emit fix).** Add a post-verdict reclassification pass: CASE_B + **D1** (the max-residual `stat_<var>`'s `<var>` is the objective-defining intermediate variable, `obj =e= f(<var>)`, `nu_obj=±1`) ∧ **D3** (cold-start MCP reaches a spurious KKT point) → `case_c (objective-defining-intermediate-variable non-convexity)`. **THE SIGN FLIP STAYS BANNED** (control-refuted 4×). Re-confirm all four members Case-c (hhfair `stat_u` rel 2.0; irscge/lrgcge/moncge `stat_xp` rel ~0.06); close `ISSUE_1236` as documented-non-convex (methodology, **0 genuine floor**).
- **Checkpoint 2 (Day 10):** `--resolve-changed` re-solve + golden-staleness + the PR25 tally.
- **Verifies:** 5.1, 5.2, 5.3, 5.4. **PR (diagnostic-harness `scripts/diagnostics/kkt_residual.py`, not `src/` emit). Est ~8 h.**

## 12. Day 11 — Priority 6: adjacent backlog (offset-alias + failure-cohort) + REPLAN-slack (~11 h)

- **P6 offset-alias generalization (Task 10 §2).** Emit-diff the highest-prior #1111/#1112 second-index-transpose candidates beyond polygon/ps2 — **cpack** (circle-packing distance sibling) first, then ps3_s_scp/ps5_s_mn/ps10_s_mn/partssupply — via the landed general-alias core; land any that (a) change the cold emit (a real correction) and (b) pass the `--resolve-changed --since-commit 4cbf8bff` **GO** gate (no changed golden moves backward across the 92 matches / 107 solves).
- **P6 failure-cohort (Task 10 §3).** **fawley** is the strongest cohort +Solve (convex LP, uniform `stat_bq(*,fuel-oil)` rel 0.973 — a clean second-index Case-b); attempt it if the offset-alias core generalizes. agreste is candidate-Case-b but scope-caveated (double-`solve` driver — verify scope first); cesam/lnts stay banked Case-c.
- **REPLAN-slack absorption:** whatever the mine [P1] / camcge [P3] / sarf [P2] REPLANs freed re-allocates here first (Task 9 order: P6 → P7 → rocket tail).
- **Deliverable:** ≥ 1 additional model recovered (Solve/Match/genuine floor) OR the cohort re-triaged with banked diagnoses. **Verifies:** 6.1, 6.2, 6.3. **PR (emit-touching if a candidate lands, else docs). Est ~11 h.**

## 13. Day 12 — Priority 7 infrastructure + REPLAN-slack (~8 h)

- **P7 property fixtures (Unknown 7.1):** add **shape12** (head-offset 4th-site bound-multiplier — guards the P1 emit, once P1 landed) + **shape13** (sarf 4-D `task` sparsification — guards the P2 emit, once P2 landed) to `tests/integration/emit/test_ad_crossterm_shapes.py` (fail-before/pass-after).
- **Genuine-floor tracking + checkpoint refresh (Unknowns 7.2/7.3):** recompute the PR25 **genuine-floor tracking** against the S32–S35 footnote-⁸ ramp (S32 ≥ 75); refresh the `--resolve-changed` checkpoint targets for the newly-touched emit sites; begin the **Epic-4 `SUMMARY.md` skeleton** (S30-retro §5 front-loading — one row per Sprint 18–35).
- **REPLAN-slack:** absorb residual freed budget per the Task-9 reallocation order.
- **Verifies:** 7.1, 7.2, 7.3. **PR (tests/ + docs). Est ~8 h.**

## 14. Day 13 — Final Retest + Closeout (~8 h)

- **Full pipeline retest** under ≥ 3 `PYTHONHASHSEED` values (PR12); recompute the DB (machine-portable paths) + the Sprint 31 → 32 metrics comparison; **PR25 genuine-vs-methodology re-baseline** recomputed (genuine floor → ≥ 75 target).
- **Closeout:** `SPRINT_LOG.md` final entry + top-table + per-priority summary; `SPRINT_RETROSPECTIVE.md` authored; Sprint-33 carryforwards filed (mine if REPLAN'd → deeper head-offset architecture, the camcge numéraire if P3 step-2 REPLAN'd → Epic 5, sarf if P2 REPLAN'd → re-scoping, rocket PATH-consultation input, cesam/lnts Case-c, any un-landed P6 candidate). **Est ~8 h.**

---

## 15. Budget Summary

| Day(s) | Track | Est (h) |
|---|---|---|
| 0 | Kickoff + Day-0 traces + 3 tractability probes | ~6 |
| 1–3 | **P1 mine bound-multiplier 4th site** (close-or-REPLAN Day 3) | ~17 |
| 4–5 | **P3 camcge `stat_mps` + Walras** (close-or-REPLAN + Checkpoint 1 Day 5) | ~15 |
| 6–8 | P2 sarf 4-D `task` sparsification (tractability gate Day 7) | ~17 |
| 9 | P4 rocket PATH-consultation input | ~9 |
| 10 | P5 hhfair/CGE Case-c classifier + Checkpoint 2 | ~8 |
| 11 | P6 adjacent backlog (cpack/fawley) + REPLAN-slack | ~11 |
| 12 | P7 infrastructure (shape12/shape13 + tracking + SUMMARY) + REPLAN-slack | ~8 |
| 13 | Final retest (≥ 3 seeds) + closeout | ~8 |
| **Total** | | **~99 h** (mid; ~80 h if the deep tracks REPLAN early, ~120 h if all PROCEED) |

**Fits the 168 h cap** with ≥ 48 h slack at the mid-estimate; **no day > 12 h** (heaviest ~11 h on Day 11, the P6 offset-alias + failure-cohort + REPLAN-slack day). The lower bound assumes the REPLAN-prone tracks (P1 mine +1 Solve, P3 camcge step-2 +1 Solve, P2 sarf +Translate) slip per Task 9; the **firm parts land regardless** — the mine bound-multiplier design, camcge step-1 (the general `nu_mps_fx` emit fix), the sarf O(active) sparsification design (or its re-scoping finding), the rocket scaffold + PATH input, the P5 harness Case-c classifier, the P7 infra.

## 16. Phase 0 Coverage Audit (PR20 + PR24 + PR27)

The three emit-touching tracks (P1 mine, P2 sarf, P3 camcge) each have a PROCEED/REPLAN gate in `PHASE_0_ACCEPTANCE_GATES.md` + the per-issue `## Phase 0` section in `docs/issues/ISSUE_{1443,1385,1330}_*.md`. Each gate's `Traced Fix-Surface (Day-0)` is re-confirmed Day 0 before any `src/` change; each cites `kkt_residual.py` (PR27) + a control-before-`src/` rule (P1 warm-residual→0; P3 `/tmp`-to-MS-1; P2 O(active) timing). P4 rocket is a docs hand-off (no emit); P5's only tool change is the diagnostic classifier (no emit); P6 candidates each pass the `--resolve-changed` GO gate before landing. **`modelstat` is asserted before every objective read; `x.up=inf` is BANNED.**

## 17. Known Unknowns Status Snapshot

All 25 prep unknowns are ✅ VERIFIED (Tasks 1–10): the P1 bound-multiplier + 5th-coupling (1.1/1.2), the sarf O(active) sparsification (2.1–2.4), the camcge split-track (3.1–3.4), the rocket Case-c scope (4.1–4.3), the hhfair/CGE Case-c classifier (5.1–5.4), the P6 offset-alias/cohort (6.1–6.3), the P7 infra (7.1–7.3). The in-sprint gates that remain are the **execution** of each track's PROCEED/REPLAN gate (Days 3/5/7), not open prep unknowns.

## 18. Risk Register + Mitigations

| Risk | Mitigation |
|---|---|
| Solve ≥ 109 misses (needs BOTH mine [P1] + camcge [P3]) | Honest projection (Task 9): the +2 Solve is the most REPLAN-sensitive KPI; both are front-loaded Days 1–5 so a REPLAN surfaces at Checkpoint 1, and the freed budget reallocates to P6 (cpack/fawley — a possible replacement +Solve). |
| mine bound-multiplier surfaces a 5th coupling (degenerate-LP) | Explicit REPLAN mine → Sprint-33 deeper head-offset architecture (Day 3); the bound-multiplier design + the S31 IR foundation hand off cleanly. |
| camcge Walras step-2 stays MS-4 (Epic-5 dual rank-deficiency) | Step 1 (`nu_mps_fx`, the general emit fix) lands regardless (cleaner CASE_B → Case-a); the numéraire → a per-model Epic-5 fallback; the `/tmp`-to-MS-1 prototype gates before any src. |
| sarf symbolic re-emit re-triggers the translate timeout | The O(active=398) tractability gate (Day 7) resolves it early; REPLAN → a documented re-scoping; +Translate deferred. |
| genuine floor ≥ 75 counted from presolve-methodology | Task 9 / Sprint-31 §3: the floor advances only via an emit change (mine/camcge cold-match or P6 #1111/#1112); P5 is explicitly 0 floor. |
| a P6 emit change regresses the 92-match / 107-solve guard | Each P6 candidate passes the `--resolve-changed` GO gate before landing (NO-GO → revert, no net loss). |

## 19. Related Documents

- `PROJECT_PLAN.md` §"Sprint 32" · `KNOWN_UNKNOWNS.md` · `BASELINE_METRICS.md` · `MINE_BOUND_MULTIPLIER_DESIGN.md` · `SARF_STAT_TASK_SPARSIFICATION_DESIGN.md` · `CAMCGE_STAT_MPS_WALRAS_DESIGN.md` · `ROCKET_PATH_CONSULTATION_INPUT.md` · `CASE_C_CLASSIFIER_DESIGN.md` · `PHASE_0_ACCEPTANCE_GATES.md` · `REPLAN_RISK_ASSESSMENT.md` · `TOOLING_AND_BACKLOG_ANALYSIS.md` · `prompts/PLAN_PROMPTS.md`

---

**Document Created:** 2026-07-14
**Owner:** Sprint 32 Planning Team
**Status:** Sprint 32 is **GO for Day 0** — all 11 prep tasks complete; the schedule front-loads the two firm +Solve movers (mine + camcge) so a REPLAN surfaces by the Day-5 checkpoint.
