# Sprint 34 — Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (PR16)

**Task:** Sprint 34 Prep Task 9
**Date:** 2026-07-19
**Owner:** Sprint planning
**Day-0 code anchor:** `750803b2` (S33 close)
**Scope:** docs/analysis only — consumes the Task-3/4/5/6 designs + the Task-8 `PHASE_0_ACCEPTANCE_GATES.md`; no `src/` change.

---

## Executive summary

Sprint 34's carryforwards are the Sprint-33 REPLAN'd/deferred tracks, each now carrying a **control-confirmed characterization** but an **un-built (and, for P1/P3, harder-than-a-keying-tweak)** fix: P1 the mine head-offset dual subsystem (H1 proven **value-invariant**), P2 the sarf three-site 369K enumeration, P3 the fawley constraint-index-diagonal `sameas` gap (+Solve is **H-b**), P4 the **NEW** max-convention bound-transfer-sign gap, P5 the camcge Walras rank-deficiency (Epic-5) + rocket Case-c (Sprint-35). This assessment applies the PR16 hypothesis-validation discipline to the **four from-scratch/new tracks** — **P1 (mine dual subsystem)**, **P2 (sarf symbolic emit mode)**, **P3 (fawley second-index + forcing)**, **P4 (max-convention bound-transfer, NEW)**: each gets a **single-model / control-experiment validation** (measurable by the Day-5 checkpoint), an **explicit REPLAN exit**, and a **budget-reallocation target** if it stalls. (P5 camcge is Epic-5-deferred + rocket is a Sprint-35 hand-off with **0 genuine floor** — neither is a firm in-sprint mover, but both appear in the projection.)

**The two things that are different this sprint (and both raise the risk, not lower it):**
1. **P1 is at an even higher prior than Sprint 33 carried.** Sprint 33 entered mine on H1 (head-label re-keying) — which its Day-2 control then proved **value-invariant** (re-keying leaves the warm residual byte-identical). So mine enters Sprint 34 on a **THIRD hypothesis (H_dual — a *structural* complementarity-pairing change)** whose `/tmp` control has not run, and — critically — the gate itself is **reframed to the cold MCP reaching MS-1** (not the warm residual `N→0`, which no keying/pairing change can move). A cold-solve gate on a **degenerate LP with `x.m=0` at the boundary** is a materially harder bar than a warm-residual check.
2. **P3's +Solve is now confirmed NOT in-sprint.** Sprint 33 framed P3 as an unresolved H-a/H-b; Task 5's Day-4 control **confirmed H-b** (sameas + all bound-transfer signs → warm `max|stat_bq| ~0` but the MCP still solves MS-5 @ 4399.557). So fawley's +Solve hands to the P5 forcing survey (a priori unpromising, like rocket), and — the correction to S33's framing — **under H-b fawley does not cold-match, so its genuine-floor +1 is contingent on forcing, not a firm in-sprint P3 gain.**

**The decisive mitigation + the S33 precedent that beats the modal outcome.** Each track carries a control-confirmed characterization (mine's 22-row `c`-boundary + `d\c`-ring residual with the cross-term proven correct; sarf's 369K→398-active three-site sparsification; fawley's constraint-index-diagonal 473→18.468; the bound-transfer sign gate at `src/emit/emit_gams.py:1590`/`:1603`), so REPLAN risk is **bounded and hands cleanly forward**. And — the binding lesson from the Sprint-33 retro §3 — **the modal outcome for the deep tracks is flat-KPI, but the P6 failure-cohort is a genuine bucket source: S33's Task-9 projection was borne out (all three deep tracks moved no bucket) yet P6 (the sample pruned-var `.l`-init fix) delivered the +1 Solve / +1 Match / +1 floor.** So the honest Sprint-34 projection is: the deep tracks likely REPLAN/hand-off, and **P6 (ganges/gangesx `$141/$145/$149`) is the designated best-remaining-shot** for an actual bucket move.

**The honest KPI projection (Sprint-33 retro §3, binding):** treat **Solve 108 → +1 (109) as conditional on P1 mine [cold-MS-1] OR P4 bound-transfer [agreste, contingent] OR P6 [ganges/gangesx]** — NOT P3 (its +Solve is a P5 forcing hand-off, a priori unpromising), NOT camcge (Epic-5), NOT sarf (Translate); treat **genuine floor 75 → +1 (76) as conditional on P1 OR P3 [contingent on forcing] OR P6 COLD-matching** — the firmest is **P6** (the S33 precedent); treat **Translate 135 → +1 (136) as conditional on P2 sarf** alone. **Solve ≥ 110 is a stretch** needing multiple movers to land — a priori unlikely. The modal outcome is **flat-KPI**, beaten (if at all) by the **P6 failure-cohort** — exactly the S33 shape.

---

## Track P1 — mine Head-Offset Dual Subsystem (#1443)

**Bug class (pinned, Task 3 — the banked premise TWICE-refuted):** Sprint 31 landed the head-offset **IR foundation** (`EquationDef.head_domain_offsets`, on `main`). Sprint 32 Day 1 refuted the `N`-derivation (MS-5 @ 22058, wrong-sign `N`). Sprint 33 Task 3 proved the emitted `stat_x` cross-term is **algebraically correct** (`_try_build_param_offset_crossterm`, `src/kkt/stationarity.py:5712`), and Sprint 33 Day 2's control then proved **H1 head-label re-keying is value-invariant** (22→22 nonzero rows, `d_N=d_Nh1` row-for-row — re-keying reads the same value the transfer already stores). The residual is a **head-offset dual-architecture mismatch**: the head-placed precedence dual `pr.m(k,l+1,i,j)` enters `stat_x` with opposite orientation at the `c`-boundary (22 rows), and `x.m=0` (degenerate) leaves no bound multiplier to reconcile it. Sprint 34 enters on **H_dual** — anchor the dual's *complementarity* to the head-side variable (a structural pairing change).

**Single-model validation (PR16):**

| Step | Gate | Measurable by |
|---|---|---|
| V1 | The harness reproduces the Day-0 fingerprint (CASE_B, `stat_x(3,1,1)` rel 2.37, dual CONSISTENT) — re-confirmed live (Task 3); H1 value-invariance holds | Day-0 (✅ done, Task 3) |
| V2 | The **H_dual** structural prototype drives the **cold** MCP to **MODEL STATUS 1 at profit 17500** (`modelstat=1` asserted; `x.up=inf` BANNED), with the 22 boundary rows closing **in the cold solution** + interior rows unperturbed, and srpchase no-regression. **NB — the gate is the cold solve, NOT warm `N→0`** (keying-invariant) | **Day-5 checkpoint** |

**REPLAN exit (H3′):** H_dual cannot drive the **cold** MCP to MS-1 @ 17500 without perturbing interior rows or regressing srpchase → the boundary is a genuine dual-degeneracy the emit cannot deterministically reconcile → hand off a deeper head-offset dual architecture (or a PATH-consultation question — an LP whose warm KKT point is not MCP-reconcilable) to a later sprint; mine stays `model_infeasible`. The **de-risked hand-off**: `MINE_DUAL_SUBSYSTEM_DESIGN.md` + the S31 IR foundation (on `main`).

**Budget reallocation on REPLAN:** mine's remaining ~14–18h (of the 18–24h) → **P6** (the ganges/gangesx `$141/$145/$149` cohort — the designated best-remaining-shot for a bucket move) + **P7** (property fixtures + genuine-floor tracking + Epic-4 `SUMMARY`).

**Prior of REPLAN: High (higher than S33).** The banked premise is now **twice-refuted** (S32 `N`-derivation + S33 H1 value-invariance), and mine enters on a **third** hypothesis (H_dual) whose `/tmp` control has not run — against a **reframed cold-MS-1 gate** that is a harder bar than a warm-residual check on a degenerate LP. The Day-5 cold-solve check resolves it early (why P1 is front-loaded), but the honest prior is High.

---

## Track P2 — sarf Three-Site Symbolic Parametric `stat_task` Emit (#1385)

**Bug class (pinned, Task 4):** the 369,024-instance `task(g,t,mn,mn)` Cartesian (16·24·31·31) enumerates at **three** sites — S1 `acost3` body-differentiation (`src/ad/constraint_jacobian.py`), S2 variable-column enumeration (`src/ad/index_mapping.py`), S3 variable stationarity (`src/kkt/stationarity.py`). The fix eliminates all three and emits **one** symbolic guarded `stat_task(g,t,m,n)$taskposs(g,t)` (the 7-term derivation, Task-4-verified term-for-term against the live source) + `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0` over the **398 active** instances — a **927× reduction**. The blow-up was re-confirmed live (Task 4: **> 116s** still in `compute_constraint_jacobian`).

**Single-model validation (PR16):**

| Step | Gate | Measurable by |
|---|---|---|
| V1 | The symbolic re-emit is **O(active = 398), not O(369,024)** — `sarf_mcp.gms` translates in **seconds** (srpchase's 1-D analogue ~2.9s), well under the current > 116s — the dominant risk, resolved **before** any downstream emit work | **Day-0/early timing probe** |
| V2 | The re-emitted `stat_task` matches the 7-term derivation with **no set-name-literal multiplier indices** (`grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` = empty); the 2-D gate + the S1/S2/S3 parametric emit + `task.fx` land **atomically**; golden byte-stable + deterministic ×3; `--resolve-changed --since-commit 750803b2` GO (sarf only) | mid-sprint |

**REPLAN exit:** the parametric re-emit **re-triggers the translate timeout** (a 4th enumeration site) → **re-scope** (a documented builder-pipeline constraint); +Translate deferred; sarf stays `translate_failure`. De-risked hand-off: `SARF_EMIT_MODE_DESIGN.md` + the timing evidence.

**Budget reallocation on REPLAN:** sarf's remaining ~9–20h (of the 20–28h) → **P6** + **P7**. +Translate is the **lowest-leverage KPI** (moves neither Solve nor Match).

**Prior of REPLAN: Medium-High.** A *failed-architecture rebuild* (the 4×-failed Sprint-26 path); the "necessary but insufficient" finding proved the blow-up hides at multiple sites, so "eliminate it everywhere" carries genuine miss-a-site risk. The V1 O(active) timing probe resolves the dominant risk **Day-0**, capping the prior below "High."

---

## Track P3 — fawley Second-Index Correction + Forcing (#1111/#1112)

**Bug class (pinned, Task 5 — a SPLIT outcome, H-b CONFIRMED):** `stat_bq`'s qsb/pbal cross-terms miss the `$(sameas(cfq__,cf))` restriction the mbal term has (an over-sum); the fix surface is the **constraint-index diagonal** in the general `sameas`-guard path (`_build_sameas_guard`/`_get_or_create_fresh_alias` in `_add_indexed_jacobian_terms`, `src/kkt/stationarity.py:5861`), **NOT** the 1-D polygon core (`_var_at_two_indices_complement`, `src/kkt/stationarity.py:7291` — `bq` is 2-D). **Task-5's Day-4 control CONFIRMED H-b** (no longer an open H-a/H-b): sameas + all bound-transfer signs → warm `max|stat_bq| ~0` but the MCP still solves **MS-5 @ 4399.557** (LP opt 2899.25) — a non-emit LP-convergence divergence. So the correction ships as a **genuine cross-term fix** (correctness) but fawley's **+Solve hands to the P5 forcing survey**, and — the correction to S33 — **under H-b fawley does not cold-match, so its genuine-floor +1 is contingent on forcing**, not a firm in-sprint P3 gain.

**Single-model validation (PR16):**

| Step | Gate | Measurable by |
|---|---|---|
| V1 | Re-confirm the live fingerprint (CASE_B `stat_bq(res-arab-l,fuel-oil)` 0.973 raw 473, dual CONSISTENT) + the constraint-index-diagonal control (`max|stat_bq|` 473 → 18.468; the residual-18.468 is the P4 cc-dist bound-transfer cell) | Day-0 (✅ done, Task 5) |
| V2 | The constraint-index-diagonal correction fires on **every** qsb/pbal `cfq` with **no mbal-term change** and **no 1-D-core regression**; `--resolve-changed --since-commit 750803b2` GO (polygon/ps2 the 1-D core untouched). **`max|stat_bq| → 0` needs P3 + P4 together.** The +Solve is the P5 forcing survey's (H-b); the genuine-floor +1 is contingent on forcing landing the solve | **Day-5 checkpoint** |

**REPLAN exit:** the generalization **leaks onto the mbal / variable-index-diagonal shape or regresses the 1-D polygon core** (a correctness risk — the emit fix cannot ship) → REPLAN. (There is **no H-a/H-b branch** — H-b is confirmed; fawley moves no in-sprint bucket, its +Solve is the P5 forcing survey's.)

**Budget reallocation on REPLAN:** fawley's remaining ~6–12h (of the 12–18h) → **P6** + **P7**. The genuine emit-correctness fix ships regardless (a cold-emit change), so P3 is **partly de-risked** — but note its genuine-floor +1 is **contingent on forcing** (not a firm in-sprint gain).

**Prior of REPLAN (correctness-REPLAN): Medium.** The no-regression is structurally favorable (polygon/ps2 use the *different* 1-D core; the only real risk is perturbing the same-path mbal). But **the +Solve is a forcing hand-off (H-b confirmed) — a priori unpromising, not an in-sprint mover**, and the genuine-floor +1 is contingent on that forcing. So P3 lands a correctness fix (firm), but its **bucket contribution is contingent on forcing, effectively deferred**.

---

## Track P4 — Max-Convention Bound-Transfer-Sign Track (#NEW)

**Bug class (pinned, Task 6):** the `piL_*/piU_*` warm-start transfers at `src/emit/emit_gams.py:1590` (`piL`: `…and var.m > 0`) + `:1603` (`piU`: `…and var.m < 0`) encode the MINIMIZE sign convention; for a **MAXIMIZE** solve they skip the correctly-signed multiplier (fawley `bq.m=-18.468` at a lower bound; mine's 3 upper-bound `x.m>0` rows). The fix is the sign-robust `= abs(var.m)` at the active bound (Option B sense-aware, `ObjSense.MAX`-conditioned, so MINIMIZE stays byte-identical). **The honest finding (Task 6):** the MAXIMIZE `model_infeasible` cohort ({fawley, mine, camcge, rocket, agreste}) is **otherwise-attributed** — fawley H-b, mine P1 (`x.m=0` at the boundary), camcge Epic-5, rocket Case-c — so the realistic +Solve target reduces to **agreste** (P6-entangled). P4's firm value is the **general warm-start-correctness fix**; the +Solve is **contingent/uncertain**.

**Single-model validation (PR16):**

| Step | Gate | Measurable by |
|---|---|---|
| V1 | The sign-robust `= abs(var.m)` closes the fawley cc-dist warm cell (proven, Day-4) + the mine 3 upper-bound rows; the min-convention gates re-confirmed at `src/emit/emit_gams.py:1590`/`:1603` | Day-0 (✅ done, Task 6) |
| V2 | Option B sense-aware; the transfer fires **only** at active bounds (no over-transfer); `--resolve-changed --since-commit 750803b2` GO over the ~20 MAXIMIZE presolve-match models (the regression-risk set). **The +Solve survey (primarily agreste):** does the sign-robust transfer close the warm residual AND reach MS-1 (warm-residual-driven → +Solve) vs stay MS-5 (structural)? | **Day-5 checkpoint** |

**REPLAN / documented-finding exit:** no candidate is warm-residual-driven (the a-priori-likely outcome) → the sign-robust transfer ships as a **general warm-start-correctness fix** with **no +Solve** (a documented finding, not a correctness REPLAN); OR the change over-transfers / regresses the MAXIMIZE presolve cohort (`--resolve-changed` NO-GO) → re-scope (Option B is the mitigation).

**Budget reallocation on REPLAN:** P4's ~10–16h — the correctness fix itself is low-risk (lands regardless); only the +Solve is at risk (~contingent), and its documented-finding outcome *is* the deliverable. Freed budget (if the correction is quick) → the agreste +Solve survey or P6/P7.

**Prior of REPLAN: Low (correctness) / Medium-High (+Solve miss).** The freshest, least-refuted track — but "least-refuted" is not "most-likely-to-move-a-bucket": the +Solve is Medium-High-at-risk because the MAXIMIZE `model_infeasible` cohort is otherwise-attributed. The realistic outcome is a **general-correctness fix with no +Solve** (a documented finding); a +Solve requires agreste (P6-entangled) to be warm-residual-driven.

---

## P5 dispositions (non-firm KPI movers, in the projection for completeness)

**P5-camcge — Dual-Consistent Walras Numéraire (#1330 → Epic 5): Epic-5-deferred (expected).** Step 1 (`nu_mps_fx` → `stat_mps` Case-a) landed on `main` (S32). The full dual-consistent redefinition's `/tmp`-to-MS-1 prototype is the **Epic-5 gate** (the banked price-pin variant reaches omega 191.7346 but MS-4; 3+ sprints of MS-4 variants). **camcge stays `model_infeasible` in Sprint 34** — not an in-sprint Solve mover. The S1∧S2∧S3 detector (flags only camcge) + the numéraire recipe are the de-risked Epic-5 hand-off.

**P5-rocket — Case-c Forcing (#1462): Sprint-35 hand-off, 0 genuine floor.** rocket's FINALIZED PATH-consultation input hands to the **Sprint-35** consultation (renumbered from the pre-insertion Sprint 34); its `--force` survey is exhausted (all MS-5). **P5 delivers 0 genuine floor** (documented Case-c; the sign flip BANNED 4×). The realistic modal outcome is **banked Case-c / a Sprint-35 conditional**; the value is the clean hand-off.

---

## Budget-at-Risk tally (feeds Task 10's schedule lower bound + fallback ordering)

| Track | Priority | Budget at risk | At-risk condition | Firm part (lands regardless) | Prior of REPLAN |
|---|---|---|---|---|---|
| **P1 mine (#1443)** | 1 [18–24h] | ~14–18h (mine's +1 Solve + conditional +1 floor) | a **deeper dual-architecture gap** (H3′) — H_dual can't reach **cold MS-1** without perturbing interior/regressing srpchase | `MINE_DUAL_SUBSYSTEM_DESIGN.md` + the S31 IR foundation (on `main`) → a de-risked filing | **High** (twice-refuted; a third hypothesis vs a harder cold-solve gate) |
| **P2 sarf (#1385)** | 2 [20–28h] | ~9–20h (the +Translate stretch) | the parametric re-emit **re-triggers the timeout** (a 4th enumeration site) | the three-site O(active) design + the re-scoping finding | **Medium-High** — a failed-architecture rebuild; V1 timing probe Day-0 |
| **P3 fawley (#1111/#1112)** | 3 [12–18h] | the +Solve (**forcing-dependent**, a priori unpromising) + the contingent +1 floor | the generalization **leaks onto mbal / regresses the 1-D core** (correctness-REPLAN) | **the genuine constraint-index-diagonal correction ships** (correctness, a cold-emit change) | **Medium** (correctness-REPLAN) / **the +Solve is a P5 forcing hand-off (not in-sprint)** |
| **P4 bound-transfer (NEW)** | 4 [10–16h] | the +Solve (**contingent** — agreste only, P6-entangled) | no MAXIMIZE candidate is warm-residual-driven (the a-priori outcome) | **the general warm-start-correctness fix ships** (Option B sense-aware) | **Low** (correctness) / **Medium-High** (the +Solve miss) |
| **P5 camcge (#1330) + rocket (#1462)** | 5 [Epic-5 / Sprint-35] | N/A in-sprint | camcge `/tmp` stays MS-4; rocket survey exhausted | step-1 on `main` + the detector + recipe (camcge); the FINALIZED input (rocket) | **N/A** — camcge Epic-5-deferred; rocket → Sprint-35; **0 floor** |
| **Combined** | 1,2,3,4,6 | Solve +1 (P1 **or** P4-agreste **or** P6); floor +1 (P1/P3-forcing/P6 cold-match); Translate +1 (P2) | — | all design/finding artifacts + camcge step-1 (on `main`) | **Task-10 lower bound: assume all deep-track KPI gains slip; the firm parts + the P6 shot land** |

---

## Honest KPI projection (which KPI survives each single-track REPLAN)

**Solve 108 → +1 (109)** rests on the in-sprint Solve mover set `{mine [P1, cold-MS-1], bound-transfer [P4, agreste — contingent], ganges/gangesx [P6]}` — plus fawley-via-forcing [P3→P5 `--force`, a priori unpromising]. **NOT** camcge (Epic-5), **NOT** sarf (Translate):

- **P1 REPLAN (H3′):** Solve +1 rests on P4-agreste or P6; if both slip, Solve holds at 108.
- **P4 all-structural (the a-priori outcome):** Solve +1 rests on P1 or P6.
- **The firmest Solve shot is P6** (the ganges/gangesx cohort — the S33 sample precedent: the failure-cohort *is* a genuine bucket source). P1 is High-prior; P4's +Solve is contingent on agreste; P3's is a forcing hand-off.
- **Solve ≥ 110 (stretch)** needs multiple movers to land — a priori unlikely; do not promise it.
- **model_infeasible ≤ 6 / path_syntax_error ≤ 6** track Solve one-for-one; if all slip, they hold at 7/7.

**Match maintain ≥ 93 / genuine floor 75 → +1 (76)** is **conditional, not independent +1s** (Sprint-33 retro §3 — the ramp advances only via an *emit-changing / recovered* track):

- The genuine-floor +1 needs **P1 [H_dual cold-match] OR P3 [the genuine cross-term correction — but its floor credit is contingent on forcing under H-b] OR P6 [ganges/gangesx cold-match if recovered]**. **P6 is the firmest** (the S33 sample precedent — a genuine cold-emit recovery). P3's floor is contingent on forcing (H-b, so fawley doesn't cold-match unaided). P1 is High-prior.
- **P5 (camcge + rocket) delivers 0 genuine floor** (documented Case-c / Epic-5; the sign flip BANNED).
- **P4 delivers 0 floor directly** (a warm-start-correctness fix; any floor gain routes through a +Solve, which is contingent).
- **As-measured Match ≥ 93** holds under any single REPLAN (the floor is the S33 93; the only in-sprint +Match movers are the P1/P6 recoveries, both conditional).

**Translate ≥ 135 → +1 (136)** rests solely on **P2 sarf**; a P2 REPLAN maintains 135. The lowest-leverage KPI.

**The modal outcome is flat-KPI (Solve 108 / Translate 135 / Match 93 / genuine floor 75) — beaten, if at all, by the P6 failure-cohort.** With P1 at a High prior on a third hypothesis against a harder cold-solve gate, P2's gain the lowest-leverage bucket, **P3's +Solve confirmed a forcing hand-off (not in-sprint)**, P4's +Solve contingent on an otherwise-attributed cohort, P5 Epic-5/Sprint-35, the *expected* result is that no **deep-track** bucket moves. **But — the binding S33 lesson — the P6 failure-cohort (ganges/gangesx `$141/$145/$149`) is a genuine bucket source (S33's sample proved it), and is the designated best-remaining-shot for an actual +Solve / +floor.** The sprint's firm product is the de-risking (five control-confirmed dispositions, the Epic-5 camcge scope, the Sprint-35 rocket hand-off); the most-likely *single* gain, if any, is **P6**.

---

## Front-load ordering recommendation

Order the sprint so **every deep-track REPLAN surfaces by the Day-5 checkpoint** — the S33 front-load worked exactly as designed (mine Day 2, fawley Day 4/5, sarf Day 6 all REPLAN'd/deferred by the checkpoint, freeing the back half for the P6 sample win):

1. **Day 0–1: P2 sarf V1 timing probe** — the cheapest, earliest verdict in the sprint (a Day-0 O(active) probe); run it first/in parallel. If the three-site re-emit still times out, re-scope immediately and reallocate.
2. **Day 1–5: P1 mine** (highest prior, deepest architecture). Run the H_dual `/tmp` structural prototype → the **cold-MS-1** gate. An early H3′ REPLAN frees ~14–18h into P6/P7 with the sprint remaining.
3. **Day 1–5: P4 bound-transfer** (the freshest lever — run the agreste +Solve survey early). Its correctness fix lands regardless; the +Solve disposition (warm-residual-driven vs all-structural) is known by Day 5.
4. **Day 2–5: P3 fawley** — the constraint-index-diagonal correction + the no-regression gate; the correction ships for correctness (H-b confirmed → +Solve is the P5 forcing survey's, not gated here).
5. **Day 1–3 (parallel, low-cost): P5-camcge Epic-5 gate** (`/tmp` full-redefinition to *confirm the deferral*, expected MS-4) + the **P5-rocket Sprint-35 submission**.
6. **Day 5+ (back half): P6** (the ganges/gangesx `$141/$145/$149` cohort + agreste — **the designated best-remaining-shot**) + **P7** (property fixtures for whichever P1–P4 emit paths landed + genuine-floor re-baseline + Epic-4 `SUMMARY`).

**Rationale:** P1, P2, P4 carry the highest REPLAN priors *and* the earliest-resolving controls (P2 a Day-0 timing probe, P1 a Day-5 cold-solve check, P4 a Day-5 survey), so front-loading them converts the sprint's dominant risk into a Day-5 fork. Either the movers land (P6/P7 are the stretch) or they REPLAN early (P6/P7 absorb the freed budget as the primary work) — and **P6 is where the S33 precedent says the actual bucket move most likely comes from.**

---

## Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_34/REPLAN_RISK_ASSESSMENT.md && echo present
# Each track has a validation + a REPLAN exit + a reallocation target:
grep -cE "REPLAN exit|Budget reallocation|Single-model validation" docs/planning/EPIC_4/SPRINT_34/REPLAN_RISK_ASSESSMENT.md
# The four from-scratch/new tracks are covered:
grep -oE "Track P[1234]" docs/planning/EPIC_4/SPRINT_34/REPLAN_RISK_ASSESSMENT.md | sort -u
# The honest KPI projection + the modal flat-KPI outcome + the P6 bucket source + the front-load:
grep -qiE "modal outcome is flat-KPI" docs/planning/EPIC_4/SPRINT_34/REPLAN_RISK_ASSESSMENT.md && echo "flat-KPI modal present"
grep -qiE "P6 .*(designated|best-remaining-shot|genuine bucket source)" docs/planning/EPIC_4/SPRINT_34/REPLAN_RISK_ASSESSMENT.md && echo "P6 bucket source present"
grep -qiE "front-load ordering" docs/planning/EPIC_4/SPRINT_34/REPLAN_RISK_ASSESSMENT.md && echo "front-load ordering present"
```

---
**Document Status:** ✅ Complete — Sprint 34 Prep Task 9 (docs-only)
**Last Updated:** 2026-07-19 · **Owner:** Sprint planning
