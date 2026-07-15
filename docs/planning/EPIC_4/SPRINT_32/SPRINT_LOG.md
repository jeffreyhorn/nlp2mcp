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
| 4 | P3 camcge **step 1 landed** — scalar-`fx` marginal transfer (`nu_mps_fx.l = mps.m`, DIRECT — sign corrected by control) | **`stat_mps` CASE_B rel 1.05 → Case-a** (dropped from top residuals; camcge max now `stat_tm(biens-int)` 0.076); all 17 presolve goldens clean; general emit fix (`emit_gams.py`) | ✅ DONE (step 1) |
| 5 | **P3 camcge step 2 REPLAN** (dual-consistent Walras) **+ Checkpoint 1 GO** | **0 Solve (REPLAN → Epic 5 — step 1 + numéraire reaches omega 191.7346 [correct] but MS-4; residual Walras singularity on the accounting identities; re-scoped hypothesis refuted). Step 1 landed (general emit fix). Checkpoint 1 GO (no golden regressed).** | 🔴 REPLAN (step 1 landed) |
| 6 | **P2 sarf REPLAN** (2-D gate necessary but insufficient — tractability gate front-loaded) | **0 Translate (REPLAN → Sprint 33 — the 2-D constraint gate fires sarf-only but `compute_constraint_jacobian` still times out; the 369K `task` columns enumerate via `acost3` + the variable path; the full fix is a from-scratch symbolic parametric emit). No src (gate reverted).** | 🔴 REPLAN |
| 7 | ~~P2 sarf tractability gate~~ → **gate fired Day 6** (front-loaded; surfaced early) | — | ⏭️ REALLOCATED |
| 8 | ~~P2 sarf close~~ → **freed by Day-6 REPLAN** → P6/P7 (Task 9) | — | ⏭️ REALLOCATED |
| 9 | **P4 rocket PATH-consultation input FINALIZED** (Case-c re-confirm + scaffold emits) | **Case-c boundary signature re-confirmed (`stat_ht(h0)` 1.00 / `stat_step` 0.497 / `stat_ht(h50)` 0.438, interior near tol, duals CONSISTENT); `--force homotopy` scaffold emits; no lever crosses. Deliverable packaged for Sprint 33; +1 Solve conditional on the consultation.** | ✅ DONE (hand-off) |
| 10 | **P5 hhfair + CGE Case-c classifier LANDED** (harness extension) **+ Checkpoint 2 GO** | **`kkt_residual.py` `reclassify_objdef_case_c` (D1∧D3 → `case_c_objdef`); all four members auto-flag (hhfair `stat_u` 2.0, irscge/lrgcge/moncge `stat_xp` 0.04–0.07), camcge `stat_tm` guard stays `case_b`; `ISSUE_1236` CLOSED. 0 genuine floor (methodology); sign flip BANNED. Checkpoint 2 GO. Tests +7.** | ✅ DONE |
| 11 | **P6 adjacent backlog RE-TRIAGED** (cpack no-op / fawley 96%-diagnosed) + REPLAN-slack | **0 KPI (cohort re-triaged — §2 offset-alias candidates already solve + cpack CASE_A [no-op]; fawley CASE_B qsb/pbal `sameas` gap control-confirmed [`stat_bq` 473→18, 96%] but incomplete + MCP diverges MS-5 → Sprint-33 hand-off). No src.** | 🟡 RE-TRIAGED |
| 12 | **P7 infrastructure DONE** (fixtures right-sized + genuine-floor recompute + Epic-4-SUMMARY skeleton) | **shape12/shape13 deferred with P1/P2 (REPLAN'd — nothing to guard); what landed [camcge scalar-`fx`, Case-c classifier] already tested; genuine floor `74` recomputed (S32 ≥75 MISSED); checkpoint anchor `4cbf8bff` stands (GO); `SUMMARY.md` skeleton begun. No src.** | ✅ DONE |
| 13 | Final retest (≥ 3 `PYTHONHASHSEED`) + closeout | **Parse 142 · Translate 135 · Solve 107 · Match 92 (142-corpus, maintained) · genuine floor 74 · model_infeasible 7 · Tests 5,085 (+11) · determinism ✅ ×3 {0,1,42} — SPRINT 32 CLOSED.** No headline gain (all movers REPLAN'd); 2 genuine landings (camcge step-1 emit fix, Case-c classifier) + 5 banked S33/Epic-5 diagnoses. DB byte-unchanged since `4cbf8bff`. | ✅ DONE |

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

## Day 4 — P3 camcge step 1: scalar-`fx` marginal transfer (general emit fix) (2026-07-14)

**Branch** `planning/sprint32-day4-camcge`. Emit-touching (`src/emit/emit_gams.py`). See `CAMCGE_STAT_MPS_WALRAS_DESIGN.md` §2 (sign-corrected).

**Root cause (IR probe):** camcge fixes the scalar `mps.fx = .09305`; a scalar fix lives in `var_def.fx` with an **empty index tuple** and an empty `fx_map`, so the `#1462 _emit_presolve_fx_warmstart` loop — which iterated only `fx_map.items()` — **skipped it**, leaving `nu_mps_fx` at 0 and `stat_mps` at CASE_B rel 1.05.

**`/tmp` control (PR24/PR27, before src) — corrected the design's sign:** the emitted `stat_mps` body is **+209.86** at the warm point (the harness's −210 is its sign-corrected variant). `nu_mps_fx = -mps.m` (the design's proposal) → **+419.72 (worse)**; `nu_mps_fx = mps.m` (DIRECT, = −209.861) → **−3.9e-4 ≈ 0 (Case-a)**. So the fix is the **same direct `= var.m`** as the existing `l`-transfers.

**Fix (src):** extended `_emit_presolve_fx_warmstart` to iterate **both** `fx_map` (per-element) **and** the scalar `.fx` (empty-index) fixing; the scalar marginal emits as `var.m` (no parens). Now emits `nu_gdtot_fx.l = gdtot.m; nu_mps_fx.l = mps.m; nu_fsav_fx.l = fsav.m;` for camcge's three scalar fixes. **(PR #1553 review):** extended the companion `_emit_presolve_fx_unfix` symmetrically — a scalar-fixed var (`mps.fx` from the `$include`) must be unfixed (`mps.lo/up` restored) so its paired `_fx_` equation does the fixing (the #1449 over-determined/unmatched mode otherwise); now emits `gdtot.lo/up`, `mps.lo/up`, `fsav.lo/up`. Added scalar warm-start + unfix unit tests.

**Result:** harness camcge — **`stat_mps` dropped out of the CASE_B top residuals** (rel 1.05 → Case-a); max residual now `stat_tm(biens-int)` rel 0.076 (the secondary rows = step-2 Walras territory, as the design predicted). **Blast radius:** all 17 committed presolve goldens **clean** (golden-staleness) + all plain goldens clean — camcge is the only affected model (no committed presolve golden). A **general nlp2mcp emit-correctness fix** (any scalar-`.fx`-in-stationarity model benefits). **Step 2 (dual-consistent Walras → MS-1 @ 191.7346) is Day 5.**

## Day 5 — P3 camcge step 2 REPLAN (dual-consistent Walras → Epic 5) + Checkpoint 1 (2026-07-14)

**Branch** `planning/sprint32-day5-camcge-walras`. Control-only (**no step-2 `src/`** — refuted before src). See `CAMCGE_WALRAS_REPLAN.md`.

The PR24/PR27 `/tmp` control tested the re-scoped hypothesis — **`stat_mps`-fixed-first (step 1, on main) + the consumption-weighted numéraire → MS-1**:
- Built `numeraire.. sum(i$cles(i), cles(i)*(p(i)−pd0(i))) =E= 0;` + `nu_numeraire` + the `cles(i)·nu_numeraire` cross-term in `stat_p`, every market row kept.
- **Result: omega = 191.7346 (correct allocation) but MODEL STATUS 4** — the residual Walras singularity on the accounting identities (`gdp`/`depreq` 131.96, `hhsaveq` 97.26, `gruse` 43.97). **Primal-correct / basis-singular.**

**The re-scoped hypothesis is refuted** — fixing `stat_mps` first does not let the numéraire reach MS-1 (consistent with 3 sprints of prep; the Walras rank-deficiency is deeper than a numéraire selection). The dual-consistent redefinition is genuinely deeper Epic-5 MCP research (the design's own words). **REPLAN step 2 → Epic 5; no step-2 `src/`** (7th consecutive control-first REPLAN, S30–S32). **Step 1 landed** (PR #1553 — the general scalar-`fx` emit fix). camcge stays `model_infeasible`.

**Checkpoint 1: GO** — `--resolve-changed --since-commit 4cbf8bff` = no golden changed (step 1 changed only `src/`); golden-staleness clean; no changed-golden model moved backward. PR25 unchanged (genuine floor 74 / methodology 21).

**Both firm +Solve movers have now REPLAN'd** (mine Day 1, camcge Day 5) — the Task-9 honest projection realized. **Solve stays 107** unless P6 (cpack/fawley) converts; **genuine floor ≥ 75 now rests entirely on a P6 emit change**. Freed step-2 + Days-2/3 mine budget → **P6 + P7**.

## Day 6 — P2 sarf REPLAN (2-D gate necessary but insufficient → Sprint 33) (2026-07-14)

**Branch** `planning/sprint32-day6-sarf`. Control/probe-only (**no `src/`** — the insufficient gate was reverted). See `SARF_TRANSLATE_REPLAN.md`.

A profiling probe + a bounded implementation attempt (the Day-7 tractability gate, front-loaded):
- **Profiled the blow-up:** parse 11.3s, then **`compute_constraint_jacobian` TIMEOUT >120s** — the runtime-computed 2-D dynamic sets `taskposs`/`equipposs` are un-evaluable at compile time → the constraint enumeration falls back to the full Cartesian × the 369K `task(g,t,mn,mn)` columns.
- **Implemented + tested the 2-D gate** (`_is_blowup_2d_condition_equation`): fires correctly for `sarf:tbal/equipb1/equipb2` and **no other** sampled model (well-scoped). **But `compute_constraint_jacobian` STILL times out >90s** — the 369K `task` columns enumerate via `acost3` (`sum((g,t,m,n)$taskposs(g,t), oc·task)`, a scalar eq the gate doesn't touch) + the variable path. **The design's own "necessary but insufficient" confirmed empirically.**

**The real fix** — stop materializing the 369K `task` columns everywhere + emit one symbolic guarded `stat_task$taskposs` + `task.fx` with parametric cross-terms — is a **from-scratch symbolic-emit subsystem** (the current builder works from enumerated entries). The design's re-scoping REPLAN exit. **REPLAN → Sprint 33; no `src/`** (gate reverted; 8th consecutive control/probe-first REPLAN). sarf stays `translate_timeout`; **Translate maintains 135** (+1 deferred — the lowest-leverage KPI).

**ALL THREE deep tracks have now REPLAN'd** (mine Solve Day 1, camcge Solve Day 5, sarf Translate Day 6). **Solve 107 / Translate 135 / genuine floor 74 all hold at Day-0.** Any Sprint-32 KPI gain now rests **entirely on P6** (cpack/fawley). Freed P2 + mine/camcge budget → **P6 + P7**. De-risked hand-off: the profiled locus + the working sarf-only 2-D detector (the "necessary" half, banked).

## Day 9 — P4 rocket PATH-consultation input FINALIZED (2026-07-15)

**Branch** `planning/sprint32-day9-rocket`. Docs/hand-off only (no `src/`). See `ROCKET_PATH_CONSULTATION_INPUT.md` (Status → FINALIZED).

- **Case-c re-confirmed (PR27, before any forcing):** `kkt_residual.py rocket.gms` → CASE_B concentrated on the boundary rows `stat_ht(h0)` rel **1.00** / `stat_step` **0.497** / `stat_ht(h50)` **0.438**, interior near tolerance (`stat_v(h0)` 0.038, `stat_m(h0)` 0.014), dual-transfer CONSISTENT (closure 1.53e-10) — matches Day-0. The residual is clean at the NLP point ⇒ a **forcing** problem, not a latent emit bug.
- **The `--force homotopy` scaffold still emits** (`--nlp-presolve --force homotopy` → the `proximal_perturbation` μ-continuation driver + `mcp_model.optfile = 1`) — the hand-off mechanism the consultation's recommended option-set plugs into.
- **No emittable lever crosses** (the banked survey stands: PATH options 477→382 / μ-continuation / multistart / the division-by-variable reformulation all MS-5; the reformulation-exhaustion finding sharpens the question to the intrinsic discretized-optimal-control structure).
- **Deliverable: the finalized PATH-consultation input packaged for Sprint 33** (the concrete question + the ruled-out-lever survey + the `--force` scaffold). rocket stays `model_infeasible`; **+1 Solve is a conditional Sprint-33 hand-off, not a Sprint-32 gain** — as the schedule anticipated (P4 is a hand-off track, not a KPI mover). No `src/` change.

## Day 10 — P5 hhfair + CGE Case-c classifier LANDED + Checkpoint 2 (2026-07-15)

**Branch** `planning/sprint32-day10-casec`. Diagnostic-harness change (`scripts/diagnostics/kkt_residual.py` — **not** `src/` emit). See `CASE_C_CLASSIFIER_DESIGN.md`.

Landed the **`kkt_residual.py` Case-c auto-classifier** (`reclassify_objdef_case_c`): a post-verdict pass reclassifying a CASE_B → **`case_c_objdef`** when **D1** (the max-residual `stat_<var>`'s `<var>` is the objective-defining intermediate variable — in `obj =e= f(<var>)`, with its own defining equation, so `nu_obj=±1`) ∧ **D3** (the cold-start MCP reaches a *spurious* optimum — cold objective ≠ the presolve match). D2 (dual-CONSISTENT) is implied by the case_b branch. Implemented via `cold_start_result` (now returns the cold objective) + `_presolve_match_objective` (the match) + `_cold_is_spurious` (the objective comparison, rtol 2e-3) + the structural `_is_objdef_intermediate_var` (D1).

- **All four family members auto-flag `case_c_objdef`:** hhfair `stat_u(1)` rel 2.00 (cold 72.147 ≠ match 87.159), irscge `stat_xp(BRD)` 0.064, lrgcge `stat_xp(BRD)` 0.045, moncge `stat_xp(MLK)` 0.066.
- **False-positive guard holds:** camcge (`stat_tm`, a non-objective-defining variable) correctly stays `case_b` — D1 gates before the match solve, so a genuine emit residual is never mislabeled.
- **`ISSUE_1236` CLOSED** as documented-non-convex (auto-classified). **THE SIGN FLIP STAYS BANNED** (refuted 4× S30–S31). P5 delivers **0 genuine floor** (methodology — presolve-recovered); the family hands to the Sprint-33 forcing/PATH work like rocket.
- **Checkpoint 2: GO** (`--resolve-changed --since-commit 4cbf8bff` = no emit golden changed — the classifier is diagnostic tooling, not the emit path). **Tests +7** (the P5 classifier unit tests: `_var_from_stat_label`, `_cold_is_spurious`, `_is_objdef_intermediate_var`, the D1∧D3 reclassification + guards). No `src/` emit change.

## Day 11 — P6 adjacent-backlog RE-TRIAGED (offset-alias no-op / fawley 96%-diagnosed) (2026-07-15)

**Branch** `planning/sprint32-day11-backlog`. Probe/re-triage only (**no `src/`**). See `P6_BACKLOG_RETRIAGE.md`.

- **Offset-alias generalization (§2) — no gain:** the Task-10 structural candidates already solve and are emit-correct — **cpack** is **CASE_A** (residual 1.4e-17, the landed core already covers its distance shape); ps5_s_mn/ps10_s_mn/partssupply already `success`; ps3_s_scp non_convex. Structural shape ≠ a dropped cross-term → no genuine-floor gain.
- **Failure-cohort (§3) — fawley 96%-diagnosed, not a clean +Solve:** fawley (`solve=failure`, LP 2899.25) CASE_B `stat_bq(*,fuel-oil)` rel 0.973. **Root cause found + control-confirmed:** `bq(c,cf)` in `qsb(cfq,l,s)`/`pbal(cfq,m)` is the #1111/#1112 second-index-transpose shape, but `stat_bq` applies `$(sameas(cfq__, cf))` to the **mbal** cross-term and **not** to the **qsb/pbal** terms (they over-sum over all `cfq__`). The `/tmp` sameas patch closes `max|stat_bq|` **473 → 18 (96%)** — BUT a residual 18.47 remains AND the MCP still diverges (MS-5 @ 5739, not the LP 2899). A deeper AD-core generalization + LP-convergence issue (the Task-9 "#1111/#1112 gate leaks" REPLAN, confirmed) → **Sprint-33 hand-off**. agreste (double-`solve` driver) + cesam/lnts (Case-c) stay banked.
- **No `src/` change** (offset-alias no-op; fawley fix incomplete + high-blast-radius). **No headline KPI gain** — Solve 107 / Translate 135 / genuine floor 74 hold at Day-0. Freed budget → **P7** (Day 12). The de-risked fawley diagnosis (the qsb/pbal `sameas` gap, 96%-confirmed) is the banked Sprint-33 deliverable.

## Day 12 — P7 infrastructure (fixtures right-sized · genuine-floor recompute · Epic-4-SUMMARY skeleton) (2026-07-15)

**Branch** `planning/sprint32-day12-infra`. Docs-only (no `src/`; no new fixtures). See `P7_INFRASTRUCTURE.md` + `docs/planning/EPIC_4/SUMMARY.md`.

- **Property fixtures right-sized:** shape12 (head-offset 4th-site) + shape13 (sarf 4-D) were contingent on P1/P2 landing — **both REPLAN'd**, so the emit paths they'd guard don't exist → **NOT added** (deferred with P1/P2 to Sprint 33; catalog stays shapes 1–11). What DID land is already guarded: camcge scalar-`fx` transfer (`test_presolve_fx_warmstart.py`, Day 4) + the Case-c classifier (`TestObjdefCaseCClassifier`, 9 tests, Day 10).
- **Genuine-floor tracking recomputed** (142-corpus, DB byte-unchanged since `4cbf8bff`): Parse 142 · Translate 135 · Solve 107 · Match 92 · **genuine floor 74** · model_infeasible 7. **The footnote-⁸ S32 ≥ 75 step is MISSED** (floor holds at 74 — no genuine cold-match landed; mine/camcge REPLAN'd, camcge step-1 doesn't cold-match, P6 re-triaged). The ramp re-baselines to the honest 74 anchor for S33.
- **Checkpoint refresh:** `--resolve-changed --since-commit 4cbf8bff --dry-run` = **GO (0 changed)** — the only emit landing (camcge step-1) changed no committed golden; anchor stands, no new target.
- **Epic-4 `SUMMARY.md` skeleton begun** — one row per Sprint 18–35 (headline KPI + firm landing + REPLAN'd carryforwards), seeded from the closed-sprint record; to fill at Epic-4 close.
- **REPLAN-slack absorbed:** the freed mine/camcge/sarf/P6 budget flowed to P7 (this infra + the banked-diagnosis write-ups). No `src/` change.

## Day 13 — Final Retest + Closeout — SPRINT 32 CLOSED (2026-07-15)

**Branch** `planning/sprint32-day13-close`. Docs/retest-only (no `src/`). See `SPRINT_RETROSPECTIVE.md`.

- **Determinism ✅ ×3:** camcge presolve (the emit change), hhfair presolve, polygon plain — all byte-identical across `PYTHONHASHSEED` {0,1,42}.
- **DB byte-unchanged since `4cbf8bff`** (`git diff 4cbf8bff..HEAD -- data/gamslib/gamslib_status.json data/gamslib/mcp/` empty) — no bucket moved, so no re-solve/persist. The only emit change (camcge step-1 `emit_gams.py`) changed no committed golden.
- **Final (142-corpus):** Parse 142 · Translate 135 · **Solve 107** · **Match 92** (maintained) · **genuine floor 74** · model_infeasible 7 · **Tests 5,085** (+11: 2 scalar-`fx` + 9 Case-c classifier).

### Per-priority summary

| P | Track | Outcome |
|---|---|---|
| P1 | mine 4th bound-complementarity site (#1443) | 🔴 REPLAN → Sprint 33 (5th coupling: wrong-sign `N` at 6 bound-active rows; MS-5 @ 22058; the `N`-derivation control-refuted, no src) |
| P3 | camcge `stat_mps` + Walras (#1330) | ✅ step 1 landed (scalar-`fx` general emit fix, `stat_mps` → Case-a) · 🔴 step 2 REPLAN → Epic 5 (numéraire → omega 191.7346 but MS-4; Walras rank-deficiency deeper) |
| P2 | sarf 4-D `task` sparsification (#1385) | 🔴 REPLAN → Sprint 33 (2-D constraint gate necessary but insufficient — 369K `task` columns via `acost3` + variable path; from-scratch symbolic-emit subsystem needed) |
| P4 | rocket PATH-consultation (#1462) | ✅ FINALIZED hand-off (Case-c re-confirmed; `--force` scaffold emits; no lever crosses; +1 Solve conditional on the Sprint-33 consultation) |
| P5 | hhfair + CGE Case-c (#1236) | ✅ classifier landed (`case_c_objdef`, D1∧D3; all four members auto-flag; camcge guard holds); ISSUE_1236 CLOSED; 0 floor (methodology); sign flip BANNED |
| P6 | adjacent backlog | 🟡 re-triaged (offset-alias candidates already solve/CASE_A; fawley qsb/pbal `sameas` gap control-confirmed 473→18 [96%] but incomplete + MCP diverges → Sprint 33) |
| P7 | infrastructure | ✅ fixtures right-sized (shape12/13 deferred with P1/P2); genuine-floor 74 recomputed; Epic-4 `SUMMARY.md` skeleton |

### Targets vs actual (`PROJECT_PLAN.md` §"Sprint 32")

| Target | Result |
|---|---|
| Solve ≥ 109 | ✗ **107** (both firm movers mine+camcge REPLAN'd — the Task-9-flagged "needs BOTH" fragility) |
| Match maintain ≥ 92 | ✅ 92 |
| genuine floor ≥ 75 | ✗ **74** (no genuine cold-match landed; ramp re-baselines to 74) |
| model_infeasible ≤ 5 | ✗ 7 |
| Translate +1 (136) | ✗ 135 (sarf REPLAN'd) |
| Tests ≥ 5,080 | ✅ 5,085 |
| Determinism ✅ ×3 | ✅ |

**No headline KPI gain** — exactly the Task-9 honest projection (every mover REPLAN-prone). **Realized value:** 2 genuine landings (camcge step-1 scalar-`fx` emit-correctness fix; the P5 Case-c auto-classifier + ISSUE_1236 closure) + 5 control-confirmed, de-risked banked diagnoses for Sprint 33/Epic 5 (mine 5th-coupling, camcge Walras/Epic-5, sarf symbolic-emit, fawley qsb/pbal sameas, rocket PATH-consultation), with **zero broken code shipped** — the control-first (PR24/PR27) discipline held on every deep track.

**SPRINT 32 CLOSED.** Anchors: S32 close = this Day-13 branch (`planning/sprint32-day13-close`); S31 close `4cbf8bff`.
