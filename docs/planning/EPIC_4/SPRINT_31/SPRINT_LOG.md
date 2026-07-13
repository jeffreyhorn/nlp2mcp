# Sprint 31 — Progress Log

**Sprint:** 31 (Head-Offset IR Plumbing, General-Alias AD #1111/#1112 & Dual-Consistent CGE — Sprint 30 carryforwards)
**Day-0 baseline (`BASELINE_METRICS.md`):** Parse 142 · Translate 135 · Solve 107 · Match 92 (genuine floor 70) · model_infeasible 7 · Tests 4,997 · anchor `ea4191dc`.

| Day | Priority / Work | Metric delta | Status |
|---|---|---|---|
| 0 | Kickoff + Day-0 traces (PR24) + tractability probes (P1 round-trip / P3 `/tmp` prototype / P5 hhfair control) | — (baseline confirmed: Parse 142 · Translate 135 · Solve 107 · Match 92 · genuine 70; `DAY0_TRACES.md`) | ✅ DONE |
| 1 | P1 Phase 1: head-offset IR plumbing (`EquationDef.head_domain_offsets` field addition) | — (round-trip fixture green; 5 head-offset models byte-identical to goldens — field inert) | ✅ DONE |
| 2 | P1 Phase 2: shared 3-site helper (heaviest day) | — (helper `head_offset_marginal_index_map` wired to Site 2 dual-transfer, correct + landed but not sufficient; blast radius 0. ⚠️ the Day-2 "Sites 1/3 already-correct / MS-1 17500" claim was a measurement error — corrected Day 3) | ✅ DONE (code); ⚠️ diagnosis corrected Day 3 |
| 3 | P1 mine close-or-REPLAN (cold-INFES-by-direction gate) | **0 (REPLAN → Sprint 32 — 4th bound-complementarity site confirmed; foundation landed Days 1–2)** | 🔴 REPLAN |
| 4 | P2 offset-alias #1111/#1112 core (polygon): coupled objective + distance second-index | **polygon → MATCH 0.780 (genuine floor +1); +cpack/himmel16/ps2×2/ps3 correct KKT completions, all still solve** | ✅ DONE |
| 5 | P2 finish (shape8 enable, warm-match 0.780) + Checkpoint 1 | **Checkpoint 1 GO: +3 as-measured Match (ps2_f_s/ps2_s/ps3_s_gic mismatch→match), genuine floor 70→74, Match 92→95 — both targets already met** | ✅ DONE |
| 6 | P3 camcge dual-consistent Walras (start; `/tmp` prototype → src) | **0 (REPLAN → Epic 5 — `/tmp` prototype stayed MS-4; harness re-diagnosed CASE_B stat_mps, not clean Walras)** | 🔴 REPLAN |
| 7 | P3 camcge close-or-REPLAN (MS-1 @ 191.7346 + detector precision) | **0 (REPLAN confirmed → Epic 5; cohort precision verified: irscge/lrgcge/moncge/stdcge all Optimal → only camcge would flag)** | 🔴 REPLAN |
| 8 | P4 sarf symbolic emit (start): 2-D gate + parametric `stat_task` | **0 (REPLAN → Sprint 32 — 2-D gate built + fires, but the dominant blow-up is the 369K-instance 4-D `task` var stationarity, not the 1,152 constraints)** | 🔴 REPLAN |
| 9 | P4 sarf tractability gate (O(constraints)) + Checkpoint 2 | **sarf tractability gate FAILED (Day-8 REPLAN confirmed — O(instances) 369K); Checkpoint 2 GO (P2 gains stable: Match 95, genuine floor 74)** | ✅ DONE |
| 10 | P5 cold-convex obj-grad: CGE cluster `stat_xp` reduction (hhfair = Case-c) | **0 (REPLAN → Case-c — control refuted: reduction INERT, CGE cluster non-convex like hhfair; sign flip stayed BANNED)** | 🔴 REPLAN |
| 11 | P6 rocket forcing → PATH-consultation input (`1/m` reformulation + continuation) | **0 Solve (REPLAN → Sprint 32) — reformulation exhausted (MS-5 cold/warm/continuation); PATH-consultation input finalized** | 🔴 REPLAN (deliverable landed) |
| 12 | P7 infrastructure (shape8 + head-offset fixtures, genuine-floor tracking) + REPLAN-slack | — (property fixtures confirmed green ×35; PR25 genuine floor FINALIZED = **74**, P2 sole gain; REPLAN-slack = no additional emit gains) | ✅ DONE |
| 13 | Final retest (≥3 `PYTHONHASHSEED`) + closeout | — (target: Solve ≥109 / genuine floor ≥73 / determinism ✅) | 🔵 PENDING |

**Targets (`PROJECT_PLAN.md` §"Sprint 31"):** Solve 107 → ≥ 109 · Match maintain ≥ 92 / genuine floor 70 → ≥ 73 · model_infeasible 7 → ≤ 5 · Translate ≥ 135 (stretch +1 via #1385) · Tests ≥ 5,000 · determinism ✅.

**Honest KPI projection (`REPLAN_RISK_ASSESSMENT.md`):** Solve ≥ 109 (needs mine [P1] + camcge [P3]) is the most REPLAN-sensitive KPI (P3 has a per-model-numéraire fallback that still solves; P1 does not); the genuine-floor ramp ≥ 73 is conditional on P2 + P3 + P5 (not independent +1s; P5's emit-fixable gain is the CGE cluster, hhfair = Case-c).

---

## Day 2 — P1 Phase 2: shared head-offset index-map helper + Site-2 dual transfer (2026-07-10)

> **⚠️ SUPERSEDED IN PART BY DAY 3 (see the Day 3 section below).** Items 2 and 4 of the proof chain below are a **MEASUREMENT ERROR**: the "reaches MS-1, profit 17500" results came from experiments that set `x.up=inf` (relaxing the non-`d` `x.fx` fixing), which produces **34 "Unmatched variable not free or fixed" errors** — the MCP solve never executed and the reported 17500/MS-1 was the **embedded `$include` LP**, not the MCP. Freeing non-`d` is structurally invalid, so it is NOT an available fix, and the emit is NOT proven correct. The KKT-residual harness (reading the shifted transfer) still reports **CASE_B emit_bug** (`stat_x` rel 2.37 at the NLP optimum). What stands: item 1 (cold MS-5), item 3 (the Site-2 shift is objectively correct and landed), and that mine stays `model_infeasible` → **REPLAN to Sprint 32**. The strikethrough claims in items 2/4 are retained for the audit trail only.

**Branch** `planning/sprint31-day2-headoffset-helper`. Emit-touching.

**Empirical proof chain (GAMS available this session) — ⚠️ items 2 & 4 corrected Day 3:**
1. **Cold mine MCP = MS-5** (`stat_x` Normal-Map inf-norm 4.07e10; `lam_pr` goes negative) — the baseline infeasibility. ✅ stands.
2. ~~**The emit (`comp_pr` Site 1 + `stat_x` Site 3) is ALREADY CORRECT** — warm-starting reaches MS-1, profit 17500.~~ **❌ WRONG (Day-3): measurement error — the 17500/MS-1 was the embedded LP; `x.up=inf` produced 34 unmatched-variable errors, the MCP never solved. The emit is NOT proven correct (harness still CASE_B, `stat_x` rel 2.37).** _(The direct LP solve of mine.gms being 17500 is true and unrelated.)_
3. **Site 2 (the `--nlp-presolve` dual transfer) was reading the wrong instance.** The NLP labels the equation instance — and stores `pr.m` — at the **shifted head label** `(k,l+1,i,j)` (confirmed: `pr.m` dumps at l ∈ {2,3,4}, e.g. `pr.m(se,4,1,1) = −7500`), while `lam_pr` is paired at the base `(k,l,i,j)`; the transfer read `pr.m(k,l,i,j)`.  **FIXED** via the new shared helper `head_offset_marginal_index_map` (`emit_gams.py`), which reads `head_domain_offsets` (Phase-1 field) and shifts the read to `pr.m(k,l+1,i,j)`. ✅ stands (objectively correct, landed) — but **not sufficient**.
4. ~~**The "4th site":** shifted-transfer + `x.up=inf` (non-`d` free) → MS-1 17500; keeping non-`d` fixed → MS-5.~~ **❌ WRONG (Day-3): the "MS-1 17500" was again the embedded LP — freeing non-`d` via `x.up=inf` is structurally invalid (34 unmatched-variable errors), not a fix. The real 4th site is a `stat_x` ⊥ bound-complementarity residual that persists with the emitted (valid) non-`d` fixing.** What stands: mine's presolve MCP is **MS-5 (22058)** even with the shifted transfer → the residual 4th bound-complementarity site → **Day 3 REPLAN to Sprint 32.**

**Landed (Day 2):** the shared helper + Site-2 wiring; 5 unit + 3 integration tests (committed fixture `head_offset_ir_roundtrip.gms` is the always-run guard). **Blast radius zero** — all 13 committed `*_mcp_presolve.gms` goldens + all cold goldens byte-identical (Site 2 is presolve-only; only mine's uncommitted presolve emit changes). Quality gate green. **mine still `model_infeasible`.** _(The Day-2 "relax/scope the non-`d` fixing" idea proved a dead end on Day 3 — freeing non-`d` via `x.up=inf` is structurally invalid (unmatched variables), so it is NOT the next step. The Day-3 outcome is **REPLAN → Sprint 32**: the real 4th site is a `stat_x` ⊥ bound-complementarity residual with the emitted, valid non-`d` fixing — see the Day 3 section.)_

## Day 3 — P1 mine close-or-REPLAN → **REPLAN to Sprint 32** (2026-07-10)

**Branch** `planning/sprint31-day3-mine-close`. Docs/decision-only (no `src/` — the REPLAN means no mine fix lands; the IR plumbing + Site-2 helper already landed Days 1–2).

**Decision: REPLAN mine → Sprint 32.** The PROCEED criterion (cold MS-1, all four k-directions → 0) is NOT met; a residual **4th bound-complementarity site** is confirmed — exactly the design §6 REPLAN exit.

**Rigorous Day-3 re-verification (GAMS):**
- **Cold MCP MS-5** (`stat_x`/`lam_pr` → 4.07e10); **presolve MCP MS-5** (omega 22058) even with the merged Site-2 head-shifted transfer.
- **KKT-residual harness — CASE_B emit_bug** with the shifted transfer (verified via `extract_dual_transfer` that the harness reads `lam_pr.l(k,l,i,j)=abs(pr.m(k,l+1,i,j))`): `stat_x(3,1,1)` rel **2.37** / raw **3.2e4**, dual-transfer CONSISTENT. So **even with the correct head-shifted duals the stationarity does not balance at the NLP optimum** — the `piL_x`/`piU_x` bound multipliers satisfying `comp_lo_x`/`comp_up_x` don't reconcile with `stat_x` given the head-offset cross-terms (the 4th site).

**⚠️ Day-2 measurement-error correction (integrity).** The Day-2 record ("emit already correct; warm-solves to MS-1 17500") was WRONG: those experiments set `x.up=inf` to relax the non-`d` `x.fx` fixing, which produces **34 "Unmatched variable not free or fixed" errors** (a variable paired with a vacuous conditioned `stat_x` MUST be fixed for MCP matching). The MCP solve never executed; the reported "17500/MS-1" was the **embedded `$include` LP**, not the MCP. Freeing non-`d` is structurally invalid → not an available fix. The Site-2 shift is still objectively correct (NLP stores `pr.m` at the `l+1` head label: `pr.m(se,4,1,1)=−7500` is the dual of the base-`l=3` constraint) and a genuine improvement — just **not sufficient**. Corrected in `ISSUE_1443` (top block) and the CHANGELOG.

**Landed this sprint (P1, reusable, merged):** Phase-1 IR field `EquationDef.head_domain_offsets` (Day 1, PR #1526); the shared `head_offset_marginal_index_map` helper + Site-2 head-shifted dual transfer (Day 2, PR #1527). **Metric: mine stays `model_infeasible` (0 Solve/Match change).** Sprint-32 carryforward = the bound-complementarity / stat_x reconciliation (stationarity-consistent bound-multiplier derivation vs the `x.m` reduced-cost transfer). robert inherits the same 4th-site risk. **Freed ~10–14 h → P5 (CGE cluster) / P7** per Task 7.

## Day 5 — P2 finish + Checkpoint 1 (2026-07-11)

**Branch** `planning/sprint31-day5-checkpoint1`. Docs/measurement-only (the P2 completion gate — shape8 un-xfailed + polygon warm-match 0.780 + CGE byte-stable — all landed Day 4, PR #1529; no `src/` this day).

**Checkpoint 1 `--resolve-changed --since-commit ea4191dc` — GO.** 6 changed goldens re-solved + bucket-diffed vs the committed DB; none moved backward. **3 forward:**
- polygon / cpack / himmel16 — held `model_optimal_presolve / match`.
- **ps2_f_s / ps2_s / ps3_s_gic — `model_optimal / mismatch` → `model_optimal_presolve / match` (✅ forward).** The distance second-index half generalized: these pooling models' packing-style constraints put a variable at both indices, so the missing second-index transpose sum was exactly their KKT defect. Verified ps2_f_s presolve MCP → MS-1, `nlp2mcp_obj_val = 0.861` = NLP ref.

**PR25 re-baseline recompute (`BASELINE_METRICS.md` §Checkpoint 1):** genuine floor **70 → 74** (polygon methodology→genuine +1; ps2×3 new genuine +3); methodology **22 → 21**; **as-measured Match 92 → 95** (74 + 21 = 95 ✓). **Both sprint targets already met at Day 5** — genuine floor ≥ 73 (74) and Match ≥ 92 (95). The DB is not persisted at a checkpoint (the tool restores it on exit); the gains land in the DB at the Day-13 final retest.

**Golden-staleness:** clean (goldens on `main` current). **No REPLAN** — the var-at-two-indices gate did not leak (CGE cohort byte-stable).

## Day 6 — P3 camcge dual-consistent Walras → **REPLAN to Epic 5** (2026-07-11)

**Branch** `planning/sprint31-day6-camcge`. The Phase-0 gate (`/tmp` prototype must reach MS-1 at omega 191.7346 BEFORE src) was **NOT met** → REPLAN; no `src/` landed.

**The Day-0-flagged substantive experiment (GAMS):**
- **Baseline** camcge presolve MCP: omega **191.7346, MS-4 Infeasible** (as banked).
- **Numéraire re-pairing** (`numeraire.. sum(i$cles(i), cles(i)*p(i)) =e= sum(i$cles(i), cles(i)*pd0(i))` + `nu_numeraire` + `cles(i)*nu_numeraire` in `stat_p`, `numeraire ⊥ nu_numeraire`, all market-clearing rows kept — the design's "try first"): omega 191.7346, **still MS-4**.
- **Single-dual pin** (`nu_equil.fx('services')` to warm value): **still MS-4** → the dual redundancy is **deeper than a single Walras relation** (design §5 REPLAN trigger).
- **KKT-residual harness: CASE_B — emit_bug.** `stat_mps` rel **1.05** / raw −210 (+ `stat_tm`/`stat_pwm` residues); dual-transfer CONSISTENT (closure residual 4.8e-10). `mps.fx=.09305` (FIXED), so `stat_mps` carries the fixing multiplier `nu_mps_fx` — the residual is a **fixing-multiplier transfer/stationarity defect**, a *different bug class* from the Walras dual-singularity.

**Decision: REPLAN → Epic 5, with a corrected diagnosis.** The design's premise ("warm-start IS a valid KKT point; failure is only the singular Jacobian") is **refuted** — camcge has a genuine **CASE_B `stat_mps`/`nu_mps_fx` emit residual**, so the dual-consistent Walras transform addresses the wrong defect. The Epic-5 item is re-scoped: FIRST resolve the `stat_mps` Case-B residual, THEN the dual-consistent numéraire. camcge stays `model_infeasible`; +1 Solve deferred. **The S1∧S2∧S3 detector was NOT built** (no src). **Sprint targets already met** (Day-5: Match 95 ≥ 92, genuine floor 74 ≥ 73) — only the Solve ≥ 109 stretch (mine [P1 REPLAN'd] + camcge) is missed, the most REPLAN-sensitive KPI (Task 7). All experiments on `/tmp` (reverted); docs/decision-only.

## Day 7 — P3 camcge close-or-REPLAN → **REPLAN confirmed → Epic 5** + cohort precision (2026-07-12)

**Branch** `planning/sprint31-day7-camcge-close`. Docs/measurement-only (P3 REPLAN'd Day 6; this day confirms the close decision + verifies the detector cohort precision). No `src/`.

**PROCEED criterion NOT met (confirmed).** camcge does not reach MS-1: Day 6's numéraire re-pairing and single-dual pin both stayed MS-4, and the harness re-diagnosed CASE_B (`stat_mps`). Critically, the Day-6 **single-dual pin** (`nu_equil.fx('services')` = warm value) staying MS-4 **rules out the explicit Walras redefinition too** — that redefinition just pins `nu_equil(n*)` to its Walras value, which is exactly what the warm-value pin does. So no numéraire/Walras variant (auto composite, single-good, per-model declaration, or explicit dual redefinition) reaches MS-1. **The per-model-numéraire alternative also does NOT land camcge** — the defect is the CASE_B `stat_mps` residual, not the numéraire/dual-singularity.

**Detector cohort precision — VERIFIED (S3 is decisive).** The well-posed CGE cohort all cold-solve **MODEL STATUS 1 Optimal** → their cold MCP is NOT Walras-singular at iter 0 → they **fail S3** → pass-through:
| Model | cold MCP | S3 (singular @ iter 0)? |
|---|---|---|
| irscge | MS-1 Optimal | no → pass-through |
| lrgcge | MS-1 Optimal | no → pass-through |
| moncge | MS-1 Optimal | no → pass-through |
| stdcge | MS-1 Optimal | no → pass-through |
| **camcge** | **MS-4** | **yes → would flag (sole case)** |

So **only camcge** is the (would-be) Walras case — confirming the design's scope claim and that a per-model-numéraire declaration would not spuriously apply to any other CGE model. The S1∧S2∧S3 detector was NOT built (no src — REPLAN); this cohort test is the de-risking evidence for the Epic-5 hand-off.

**Decision: REPLAN → Epic 5 CONFIRMED, with the corrected CASE_B scope** (resolve `stat_mps`/`nu_mps_fx` first, then the numéraire). camcge stays `model_infeasible`; +1 Solve deferred. **P3 track closed.** Freed budget → P5 (CGE cluster `stat_xp`) / P7 per Task 7. **Sprint targets already met** (Match 95 ≥ 92, genuine floor 74 ≥ 73); the Solve ≥ 109 stretch (mine + camcge, both REPLAN'd) is the only miss. All experiments on `/tmp` (reverted).

## Day 8 — P4 sarf symbolic emit → **REPLAN to Sprint 32** (enlarged scope) (2026-07-12)

**Branch** `planning/sprint31-day8-sarf`. Docs/decision-only (the 2-D gate was built for measurement and REVERTED — it neither makes sarf translate nor can land). No `src/`.

**A Day-8 finding enlarges the scope.** Built the 2-D gate extension `_is_blowup_2d_condition_equation` (sarf's shape: 2-D regular eq_domain + a 2-D dynamic-subset-condition — `tbal(g,t)$taskposs(g,t)`, `equipb1(m,t)$equipposs(m,t)`, `equipb2(n,t)$equipposs(n,t)` — with 0 static members + a 2-D-summing body). It **fires tightly** on `tbal`/`equipb1`/`equipb2` (verified) and short-circuits their AD enumeration (warnings confirm) — **but sarf STILL times out.**
- **The dominant blow-up is the 4-D `task(g,t,mn,mn)` variable: 16·24·31·31 = 369,024 instances** (the next-largest variable is `xcrop` at 48), so `stat_task` is enumerated 369K times regardless of the constraint short-circuit.
- **So the design's fix-surface (2-D constraint gate + parametric cross-term) is necessary but INSUFFICIENT** — the design scoped the blow-up as the 1,152 constraint instances (tbal 384 / equipb1 648 / equipb2 120), but the real cost is the 369K-instance `task`-variable stationarity. The parametric emit must ALSO sparsify `stat_task` to the `$taskposs(g,t)`-active subset (the banked `stat_task(g,t,m,n)$taskposs(g,t)` shape IS parametric, but the current per-instance emit enumerates all 369K before guarding).

**Decision: REPLAN → Sprint 32, with an enlarged scope.** The full fix is parametric stationarity emit for a 369K-instance 4-D variable + the parametric constraint cross-terms, landed atomically — strictly larger than the already-4×-failed Sprint-26 symbolic-emit. Gate reverted (measurement-only). sarf stays `translate_timeout`; +Translate deferred. **Sprint targets already met** (Match 95, genuine floor 74 at Day 5); P4 was a +Translate stretch. This is the 5th REPLAN of this track — the enlarged scope (369K var blow-up) is the new banked finding for the dedicated Sprint-32/Epic workstream.

## Day 9 — P4 sarf tractability gate + Checkpoint 2 (2026-07-12)

**Branch** `planning/sprint31-day9-checkpoint2`. Docs/measurement-only (no `src/`; the DB is not persisted at a checkpoint — the tool restores it on exit).

**P4 sarf tractability gate — FAILED (REPLAN confirmed Day 8).** The gate requires the emit to be **O(constraints), not O(instances)**. Day 8 established it is O(instances): even with the 2-D constraint gate short-circuiting `tbal`/`equipb1`/`equipb2`, the 4-D `task(g,t,mn,mn)` variable's `stat_task` enumerates **369,024** instances → the >2-min timeout persists. So the tractability gate is not met → **REPLAN → Sprint 32** (enlarged scope: parametric stationarity emit for the 369K-instance variable). sarf stays `translate_timeout`; no +Translate.

**Checkpoint 2 (`--resolve-changed --since-commit ea4191dc`) — GO.** The changed-golden set is unchanged since Checkpoint 1 (Days 6–8 were REPLANs / docs-only, no golden changes), so the 6 P2 models re-solve identically:
- polygon / cpack / himmel16 — held `model_optimal_presolve / match`.
- ps2_f_s / ps2_s / ps3_s_gic — `model_optimal / mismatch` → `model_optimal_presolve / match` (✅ forward).
- **GO: all 6 held their bucket** — the P2 gains are **stable** (no regression introduced by the Day 6–8 REPLAN work).

**Golden-staleness:** clean. **PR25 tally — unchanged from Checkpoint 1:** genuine floor **74**, methodology **21**, as-measured **Match 95** (no new golden changes since Day 5). **Both sprint targets remain met** (Match ≥ 92, genuine floor ≥ 73). The +3 Match gains land in the DB at the Day-13 final retest.

## Day 10 — P5 cold-convex obj-grad (CGE cluster) → **REPLAN to Case-c** (2026-07-12)

**Branch** `planning/sprint31-day10-objgrad`. The control gate (the ν_objective reduction must reach residual→0 in a `/tmp` control BEFORE any `src/`) **FAILED** → REPLAN; no `src/` landed. **The sign flip stayed BANNED** (tested only as a control, never shipped).

**The `/tmp` control (GAMS) refutes the reduction:**
- **irscge cold-mismatches:** cold `UU = 25.5085` vs the presolve match **26.0914** (the harness's CASE_B, `stat_xp(BRD)` rel 0.064). So the P5 target (methodology → genuine cold match) exists.
- **The ν_objective reduction is INERT.** `UU` appears ONLY in `obj.. UU =e= prod(i, Xp(i)**alpha(i))` → nu_obj = ±1, so the reduction reduces to the sign choice. Flipping `stat_xp`'s objective-gradient sign leaves the cold primal at the **identical 25.5085** — it does NOT move toward the match.
- **The whole cluster is uniformly the same:** irscge / lrgcge / moncge all cold `25.5085`, sign flip inert both ways. They are **non-convex model classes** (irscge = *Scale Economy* / increasing returns, lrgcge = *Large-Country*, moncge = *Monopoly* CGE) → 25.5085 is a genuine non-global local optimum; the match is only reachable via the presolve warm-start.

**Decision: REPLAN — the CGE cluster is genuine Case-c (like hhfair).** The design's "CGE cluster is convex, one ν_objective reduction → several cold" hypothesis is REFUTED by the control — exactly the hhfair Case-c pattern (Sprint-30 Day-6 sign-fix refutation). The 3 CGE models stay methodology (match via presolve, not cold); hhfair stays genuine Case-c. **P5 delivers 0 genuine floor** — the floor stays **74** (P2's gain). No high-blast-radius obj-grad change shipped on a refuted hypothesis (the PR24/PR27 control discipline working as intended — the same lesson as hhfair Day-6). **Sprint targets remain met** (Match 95 ≥ 92, genuine floor 74 ≥ 73). All experiments on `/tmp` (reverted); docs/decision-only.

## Day 11 — P6 rocket forcing → PATH-consultation input (2026-07-12)

**Branch** `planning/sprint31-day11-rocket`. Docs/decision-only (no `src/` — the reformulation is a model-level change that does not converge, so nothing lands; the `--force` scaffold already landed Sprint 30). All experiments on `/tmp`.

**Gate: residual clean at the NLP point (Case-c) — PASS.** The harness reports CASE_B `stat_ht(h0)` rel 1.00, but per ISSUE_1462 the residual at the h0/h50 **boundary** rows (moving with the warm-start value, `nu_*_fx=0` → `stat_step`; `=var.m` → `stat_ht(h0)`) is the non-convex **Case-c boundary** signature, not a cleanable emit bug — rocket stays a forcing problem.

**The LAST untried emittable lever — the division-by-variable reformulation — is EXHAUSTED.** Reformulated rocket to remove ALL division-by-variable from the initial Jacobian: `gf(h)` → `g(h)*sqr(ht(h)) =e= g_0*sqr(h_0)` (removes 1/ht²); a free acceleration `a(h)` with `accel(h).. (a(h)+g(h))*m(h) =e= T(h)−D(h)` replacing `(T−D−m·g)/m` in `v_eqn` (removes 1/m). The reformulated NLP solves to the same optimum (**1.0128**), but its MCP is:
- **MS-5 Locally Infeasible cold** (nh=10),
- **MS-5 warm-started from the NLP optimum** (presolve),
- **MS-5 across every mu-continuation step** (`--force homotopy`).

(The nh=50 reformulated MCP exceeds the demo-license nonlinear-row limit — the auxiliary `a(h)` + bilinear `accel` push it past 1000 rows — so the comparison ran at nh=10, where the ORIGINAL rocket MCP is also MS-5, a fair baseline.)

**So rocket's non-convergence is intrinsic to the discretized optimal-control MCP structure, NOT the division-by-variable Jacobian conditioning.** Combined with the exhausted PATH-option survey (INFES 477 → 382, Sprint-30 Task 4) and continuation/multistart (all MS-5, Sprint-30 Day 3), **NO emittable lever converges rocket.**

**Decision: REPLAN → Sprint 32; the finalized PATH-consultation input is the deliverable.** The reformulation is now a *ruled-out* candidate in the `BACKLOG §3` PATH-consultation question, sharpening it toward the intrinsic structure. The `--force` scaffold (Sprint 30) + this finalized question are the de-risked hand-off. rocket stays `model_infeasible`; +1 Solve deferred. **Sprint targets remain met** (Match 95 ≥ 92, genuine floor 74 ≥ 73). This was the last live +Solve/+Match attempt.

## Day 12 — P7 infrastructure + REPLAN-slack (2026-07-13)

**Branch** `planning/sprint31-day12-infra`. Docs-only (all P7 fixtures already landed Days 0–4; no new `src/` or fixtures — nothing to gate).

**Property fixtures confirmed present + guarded + GREEN (35 passed).** The P7 cross-term/head-offset property suite is in place:
- `shape8_offset_alias_successor.gms` — xfail **removed** (Day 5, warm-match 0.780); guarded by `test_ad_crossterm_shapes.py::test_shape8`.
- `shape10_distance_second_index.gms` + `shape11_second_index_indexed_condition.gms` — the P2 #1111/#1112 second-index-transpose regression fixtures; guarded by `test_ad_crossterm_shapes.py`.
- `head_offset_ir_roundtrip.gms` — the Phase-1 `head_domain_offsets` round-trip anchor; guarded by `test_head_domain_offsets.py` + `test_head_offset_presolve_transfer.py` + `test_head_offset_marginal_map.py` (Site-2 shifted read).
- `test_count_additive_terms.py` — the interior-representative selection unit guard (8 tests).
- Full P7 suite: **35 passed** (`pytest test_ad_crossterm_shapes test_head_domain_offsets test_head_offset_presolve_transfer test_head_offset_marginal_map test_count_additive_terms`).

**PR25 genuine-floor tracking FINALIZED** (`BASELINE_METRICS.md` Day-12 section): **genuine floor = 74** (S30 70 + P2's +4), methodology 21, as-measured Match 95. **P2 is the sole genuine-floor contributor** — the projected P5 ramp component (+1 to +4 from the CGE cluster) did NOT land (control refuted it as genuine Case-c non-convexity, Day 10), and P1's +0-to-+1 mine gain REPLAN'd (Day 3). This is the Sprint-30-retro §3 conditionality warning realized: the genuine-floor ramp is NOT independent +1s — it was carried entirely by the one convex-fixable track. **Footnote-⁸ ramp: S30 70 → S31 74 (S31 ≥ 73 MET, +1 headroom).**

**REPLAN-slack outcome: no additional emit gains.** The Task-7 reallocation order (P5 → P7 → +Translate/forcing tails) freed slack from the mine/polygon/sarf/hhfair-CGE/rocket REPLANs, but every deep track that REPLAN'd did so because its fix premise was refuted (measurement error, Case-c non-convexity, O(instances) blow-up, intrinsic non-convergence) — there was no *correct-but-unshipped* emit fix to absorb. The freed slack went to hardening the P7 property suite and de-risking the S32 carryforwards (PATH-consultation question sharpened, ISSUE files updated). **P2 remains the sole net gain; both sprint targets stay met (Match 95 ≥ 92, genuine floor 74 ≥ 73).**

**`--resolve-changed` checkpoint targets (Day-13 retest):** the 6 P2-touched goldens (polygon, cpack, himmel16, ps2_f_s, ps2_s, ps3_s_gic) against anchor `ea4191dc` — GO iff no changed golden moves backward. No other track landed `src/`, so the changed-golden set is exactly the P2 set.

## Sprint 31 — Final Summary (Day 13)

_(To be completed at closeout — final metrics table, per-priority summary, determinism verification, Sprint-32 carryforwards.)_
