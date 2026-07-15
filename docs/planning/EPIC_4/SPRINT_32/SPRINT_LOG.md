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

_(Per-day entries appended below as the sprint runs.)_
