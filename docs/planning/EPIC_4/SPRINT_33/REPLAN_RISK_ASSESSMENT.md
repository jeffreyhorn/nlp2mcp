# Sprint 33 — Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (PR16)

**Task:** Sprint 33 Prep Task 9
**Date:** 2026-07-16
**Owner:** Sprint planning
**Scope:** docs/analysis only — consumes the Task-3/4/5 designs + the Task-8 `PHASE_0_ACCEPTANCE_GATES.md`; no `src/` change.

---

## Executive summary

Sprint 33's carryforwards are the five tracks Sprint 32 REPLAN'd *because a control refuted the banked premise before any bad ship* — P1 the mine `N`-derivation (closes `stat_x` by construction but MS-5 @ 22058, wrong-sign `N` at 6 bound-active rows); P2 the sarf 369K enumeration (the 2-D gate fires but the columns enumerate elsewhere); P3 the fawley qsb/pbal `sameas` gap (the patch closes 96% but the MCP still diverges); P4 the camcge Walras rank-deficiency (step-1 + numéraire reaches omega 191.7346 but MS-4); P5 the rocket/Case-c non-convexity. This assessment applies the PR16 hypothesis-validation discipline to the **three deepest from-scratch tracks** — **P1 (mine head-offset bound-active cross-term architecture)**, **P2 (sarf three-site symbolic `stat_task` emit)**, **P3 (fawley second-index `sameas`-guard generalization)**: each gets a **single-model / control-experiment validation** (measurable by the Day-5 checkpoint), an **explicit Sprint-33 REPLAN exit**, and a **budget-reallocation target** if it stalls. (P4 camcge is a Task-6 Epic-5 deferral; P5 rocket/Case-c is a Task-7 conditional hand-off + forcing survey with **0 genuine floor** — neither is a firm in-sprint KPI mover, but both appear in the projection.)

**The one thing that is different this sprint (and it raises the risk, not lowers it):** in Sprint 32 the banked premises were refuted *in-sprint* by the Day-1/Day-5 controls. In Sprint 33 **P1's banked premise was already refuted during prep** — Task 3's from-scratch ∂-derivation proved the emitted `stat_x` cross-term is *algebraically correct*, so the Sprint-32 "the cross-term is inconsistent at bound-active rows / re-derive it" framing is **dead on arrival**. mine enters Sprint 33 not on a pinned root cause but on a **fresh hypothesis (H1 head-label multiplier-keying)** whose own `/tmp` control has not yet run. That is a materially higher REPLAN prior than the Sprint-32 framing carried, and the honest projection below treats it as such.

**The decisive mitigation (unchanged from S32):** each track still carries a **control-confirmed characterization** — mine's residual is localized to 6 bound-active `c`-boundary rows with the duals CONSISTENT and the cross-term proven correct (so the fix is a *multiplier-keying* reconciliation, not a term re-derivation, Task 3); sarf's blow-up is the 369,024-instance enumeration at **three** sites, sparsifiable to **398 active** (Task 4); fawley's residual is the qsb/pbal `sameas`-guard gap on the **2-D** indexed cross-term path, 96%-closed by the banked `/tmp` patch (Task 5). So REPLAN risk is **bounded and hands cleanly forward**, but — with P1's first hypothesis already spent and P3's +Solve gated behind an unresolved H-a/H-b — the **modal outcome is flat-KPI** (the Sprint-32 retro §3 lesson, now with one *fewer* firm mover than Sprint 32 had at the same point).

**The honest KPI projection (Sprint-32 retro §3, binding — "when every KPI mover is REPLAN-prone and the sprint is 'implement against a banked root cause,' a flat-KPI outcome is the modal result; the value is the de-risking, not the bucket"):** treat **Solve 107 → +1 as conditional on P1 mine OR P3 fawley** landing an emit fix that reaches MS-1 (P4 camcge is **Epic-5-deferred**, not an in-sprint Solve mover; P5 rocket is a **Sprint-34** conditional) — the **two** in-sprint Solve movers are both from-scratch and both REPLAN-prone; treat **genuine floor 74 → +1 as conditional on P1 OR P3 COLD-matching an emit change — NOT on presolve-methodology reclassification** (P5 delivers 0 floor); treat **Translate 135 → +1 as conditional on P2 sarf** alone. **Solve ≥ 110 is a stretch** that needs both in-sprint Solve movers to land *and* rocket [P4-adjacent] or camcge [Epic-5] to convert — a priori unlikely. (See "Honest KPI projection" below.)

---

## Track P1 — mine Head-Offset Bound-Active Cross-Term Architecture (#1443)

**Bug class (pinned, Task 3 — the banked premise REFUTED):** Sprint 31 landed the head-offset **IR foundation** (`EquationDef.head_domain_offsets` + the Site-2 dual transfer, on `main`). Sprint 32 Day 1's control then refuted the `N`-derivation (closes `stat_x` by construction but MS-5 @ 22058 — an infeasible *negative* bound multiplier at 6 bound-active rows). **Sprint 33's Task 3 went one step further and refuted the Sprint-32 re-framing itself:** a from-scratch ∂-derivation + a source trace of `_try_build_param_offset_crossterm` (`src/kkt/stationarity.py:5712`) proved the emitted `stat_x` cross-term is **algebraically correct**. The residual `N` at the 6 bound-active `c`-boundary rows (`x(1,3,{1,2,3})`, `x(3,1,2)`, `x(3,2,1)`, `x(4,1,1)`) is therefore **not** a wrong cross-term — it is a **multiplier-keying** gap: the duals couple through shared boundary multipliers (e.g. `stat_x(3,1,2)` and `stat_x(4,1,1)` via `lam_pr(ne,3,1,1)`), so the closure must re-key `comp_pr`/`lam_pr` + the cross-term to the **head label `(k,l+1,i,j)`** (where the NLP stores `pr.m`) via the currently-unused `head_domain_offsets` IR (**H1**), or reconcile the `d\c`-ring (**H2**) — not correct a term sign.

**Single-model validation (PR16):**

| Step | Gate | Measurable by |
|---|---|---|
| V1 | The harness reproduces the Day-0 fingerprint (CASE_B, `stat_x(3,1,1)` rel 2.37, dual-transfer CONSISTENT) **and** Task 3's finding holds — the cross-term is correct, the residual is the 6 bound-active rows only, interior at 0 | Day-0 (✅ done, Task 3) |
| V2 | The **H1** head-label re-keying drives the **warm residual `N → 0` at ALL 6 bound-active rows AND unchanged (0) at every interior row** (`modelstat` asserted — the `x.up=inf` measurement error is BANNED) → presolve **MS-1 at profit 17500** (+1 Solve); **no deeper coupling** (a fresh `stat_x` residual after re-keying, or `sign(N)` still contradicting the bound-active status) | **Day-5 checkpoint** |

**REPLAN exit (H3, Sprint 33):** H1 (and the H2 `d\c`-ring reconciliation) cannot drive `N → 0` without perturbing interior rows or regressing srpchase → the residual is a **deeper head-offset dual-architecture gap** → hand off a dedicated head-offset dual subsystem to a later sprint; mine stays `model_infeasible`. The **de-risked hand-off**: `MINE_CROSSTERM_DESIGN.md` (the cross-term-correct finding + the multiplier-coupling characterization) + the S31 IR foundation (on `main`, correct regardless) make that filing a specification, not an open question.

**Budget reallocation on REPLAN:** mine's remaining ~14–18h (of the 14–20h — H1 is a prototype-first track, so most budget is at risk until V2 passes) → **P6** (the residual failure-cohort re-triage — agreste double-`solve` scope, cesam/lnts Case-c — plus any P3 fawley cold-match follow-on, the firmest remaining **genuine-floor** levers) + **P7** (property fixtures + genuine-floor tracking + the Epic-4 `SUMMARY` continuation). mine's +1 Solve + its conditional +1 genuine floor become a Sprint-34+ carry.

**Prior of REPLAN: High.** This is the sprint's highest-prior track, and it is *higher* than the Sprint-32 framing carried. The Sprint-32 assessment rated mine "Medium — IR blocker landed, fix derivable by construction." That "derivable by construction" premise is now **twice refuted** (the `N`-derivation in S32 Day 1, the cross-term re-derivation in S33 Task 3). mine is a **degenerate LP** whose bound-dual ambiguity is exactly the class that has surfaced fresh couplings twice; H1 is a plausible but *unproven* third hypothesis whose `/tmp` control has not run. The Day-5 warm-residual→0 check resolves it early — which is why P1 is front-loaded — but the honest prior is High.

---

## Track P2 — sarf Three-Site Symbolic Parametric `stat_task` Emit (#1385)

**Bug class (pinned, Task 4):** Sprint 32 Day 6 profiled the timeout to `compute_constraint_jacobian` (> 75s) and confirmed the 2-D constraint gate (`_is_blowup_2d_condition_equation`, reverted from `main`) is **necessary but insufficient** — the 369,024-instance `task(g,t,mn,mn)` Cartesian product (16·24·31·31) enumerates at **three** sites: S1 the `acost3` body-differentiation (`src/ad/constraint_jacobian.py`), S2 the variable-column enumeration (`src/ad/index_mapping.py`), S3 the variable stationarity (`src/kkt/stationarity.py`). The fix eliminates the 369K materialization at **all three** sites and emits **one** symbolic guarded `stat_task(g,t,m,n)$taskposs(g,t)` (the banked 7-term derivation, Task-4-verified term-for-term) + `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0` over the **398 active** `taskposs(g,t) ∧ tech(g,m,n)` instances — a **927× reduction**.

**Single-model validation (PR16):**

| Step | Gate | Measurable by |
|---|---|---|
| V1 | The symbolic re-emit is **O(active = 398), not O(369,024)** — `sarf_mcp.gms` translates in **seconds** (srpchase's 1-D analogue is ~2.9s on the current runner / 6.56s on the slower Sprint-32 runner), well under the current > 75s timeout — the dominant risk, resolved **before** any downstream emit work | **Day-0/early timing probe** |
| V2 | The re-emitted `stat_task` matches the banked 7-term derivation with **no set-name-literal multiplier indices** (the Sprint-26 `nu_slack("srn")` failure, commit `243fe578`; `grep -E 'nu_[[:alnum:]_]+\("\|lam_[[:alnum:]_]+\("' sarf_mcp.gms` = empty); the 2-D gate + the S1/S2/S3 parametric emit + the `task.fx` fixing land **atomically** (a re-emit without cross-terms = an inconsistent MCP); golden byte-stable + deterministic ×3 `PYTHONHASHSEED`; `--resolve-changed --since-commit ee51ed9e` GO (sarf only) | mid-sprint |

**REPLAN exit (Sprint 33):** the parametric re-emit **re-triggers the translate timeout** (O(instances) after all — a fourth enumeration site, or a builder-pipeline materialization the three-site fix misses) → **re-scope the parametric emit** (a documented builder-pipeline constraint); +Translate deferred; sarf stays `translate_failure`. The **de-risked hand-off**: `SARF_EMIT_SUBSYSTEM_DESIGN.md`'s three-site O(active) design + the timing evidence make the re-scoping a documented finding, not a dead end.

**Budget reallocation on REPLAN:** sarf's remaining ~8–16h (of the 14–20h) → **P6** + **P7**. The +Translate stretch is the **lowest-leverage KPI** — it moves neither Solve nor Match.

**Prior of REPLAN: Medium-High.** This is a *failed-architecture rebuild* — the Sprint-26 Day-4 attempt failed on exactly the set-name-literal + combinatorial-blow-up axes this design guards, and sarf's 369K enumeration is the worst-case instance of that axis; the Sprint-32 "necessary but insufficient" finding proved the blow-up hides at *multiple* sites, so "eliminate it everywhere" carries genuine miss-a-site risk. The V1 O(active) timing probe resolves the dominant risk **Day 0** (before any downstream emit work), which caps the prior below "High."

---

## Track P3 — fawley Second-Index `sameas`-Guard Generalization (#1111/#1112)

**Bug class (pinned, Task 5 — a SPLIT outcome by construction):** Sprint 32 Day 11 confirmed `stat_bq`'s qsb/pbal cross-terms miss the `$(sameas(cfq__,cf))` second-index restriction the mbal term has (an over-sum); the `/tmp` `sameas` patch closes `max|stat_bq|` **473 → 18 [96%]** but a residual 18.47 remains **and** the MCP still diverges (MS-5 @ 5739). Task 5 refined the fix surface: the general indexed cross-term `sameas`-guard path (`_build_sameas_guard`@`stationarity.py:4623` / `_get_or_create_fresh_alias`@4496 in `_add_indexed_jacobian_terms`), **NOT** the 1-D polygon core (`_var_at_two_indices_complement`@7291 — `bq` is 2-D). The split: **H-a** — the residual 18.47 is a second-column gate-leak that the full generalization closes → `max|stat_bq| → 0` → MS-1 @ 2899.25 (+1 Solve, +1 genuine floor if cold-match); **H-b** — the residual is a non-emit LP-convergence issue (MS-5 @ 5739 separable from the emit) → the emit fix ships as a **genuine cross-term correction** but fawley's +Solve hands to the P5 forcing survey.

**Single-model validation (PR16):**

| Step | Gate | Measurable by |
|---|---|---|
| V1 | Re-confirm the Day-11 control (`max\|stat_bq\|` 473 → 18, 96%) and **localize the residual 18.47 by column** — the H-a/H-b discriminator | Day-0/early |
| V2 | The full generalization (every second-index `cfq` gets the `$(sameas(cfq__,cf))` restriction, covering qsb/pbal) drives **`max\|stat_bq\| → 0`** (not 96%) at the warm point (`modelstat` asserted). **H-a:** presolve → **MS-1 @ 2899.25** (+1 Solve). **H-b:** `max\|stat_bq\| → 0` yet MS-5 → emit ships genuine, +Solve → P5. **No regression:** `--resolve-changed --since-commit ee51ed9e` GO (polygon/ps2 the 1-D core untouched; **no mbal-term change** — Unknown 3.3 structurally favorable) | **Day-5 checkpoint** |

**REPLAN exit (Sprint 33):** the generalization **leaks onto the mbal / first-index shape or regresses the 1-D polygon core** (a correctness risk — the emit fix cannot ship) → REPLAN, fawley stays `model_infeasible`, the design is re-scoped. (The H-b outcome — emit closes but MCP diverges — is **not** a REPLAN: the genuine cross-term correction still ships and lifts the genuine floor; only the +Solve defers to forcing.) The **de-risked hand-off**: `FAWLEY_SECOND_INDEX_DESIGN.md`'s fix-surface refinement + the H-a/H-b discriminator make either outcome a documented finding.

**Budget reallocation on REPLAN:** fawley's remaining ~6–12h (of the 12–18h) → **P6** + **P7**. Under H-b the emit-correctness fix lands regardless (a genuine cross-term correction), so P3 is **partly de-risked** — only the +Solve (which needs H-a) is fully at risk.

**Prior of REPLAN (correctness-REPLAN): Medium.** The no-regression is structurally favorable (Unknown 3.3: polygon/ps2 use the *different* 1-D core; the only real risk is perturbing the same-path mbal/first-index `sameas`). But the **+Solve is Medium-High at risk**: H-a is unproven, and the banked evidence is discouraging — the 96%-patch left the MCP diverging (MS-5 @ 5739), which is the exact H-b signature; if the residual 18.47 is non-emit LP-convergence, the emit fix ships genuine (a floor lever) but **no +Solve**. So P3's *correctness* REPLAN is Medium, its *+Solve* miss is Medium-High.

---

## P4 / P5 dispositions (non-firm KPI movers, in the projection for completeness)

**P4 — camcge Dual-Consistent Walras Numéraire (#1330 → Epic 5): Epic-5-deferred (the expected disposition).** Step 1 (the scalar-`fx` `nu_mps_fx` transfer → `stat_mps` Case-a) landed on `main` (S32, PR #1553). Step 2 (the dual-consistent Walras numéraire) is genuinely deeper MCP research: the banked step-1 + numéraire prototype reaches **omega 191.7346 (correct primal) but MS-4** (residual Walras rank-deficiency on gdp/depreq/hhsaveq/gruse). Given the banked evidence (price-pin MS-4, single-dual-pin MS-4, 3+ sprints of MS-4 variants), the **`/tmp` full-redefinition prototype reaching MS-1 is the Epic-5 gate**, not an in-sprint landing. **camcge stays `model_infeasible` in Sprint 33** — it is **not** an in-sprint Solve mover; its +1 Solve defers to Epic 5. The S1∧S2∧S3 detector (flags only camcge across irscge/lrgcge/moncge/stdcge) + the working numéraire recipe are the de-risked Epic-5 hand-off (`CAMCGE_WALRAS_DESIGN.md`).

**P5 — rocket + hhfair/CGE Case-c Forcing (#1462 / #1236): conditional hand-off + survey, 0 genuine floor.** rocket's PATH-consultation input is FINALIZED (S32); Sprint 33 **submits** it to the Sprint-34 consultation (rocket's survey is *exhausted* — homotopy/multistart/optfile all MS-5 — so its +1 Solve is a **Sprint-34** conditional, not an in-sprint gain). The `--force {homotopy,multistart,optfile}` survey across hhfair + irscge/lrgcge/moncge is exercised, but every candidate is a non-convex model at a spurious local optimum (`case_c_objdef`, `nu_obj=±1`, the sign flip **BANNED** — control-refuted 4×): a lever crossing to the global optimum is a priori unpromising. **P5 delivers 0 genuine floor** (documented Case-c, not a floor contributor — the Sprint-32 retro §3 lesson applied: do not count P5 toward the ramp). The realistic modal outcome is **banked Case-c** (no bucket move); the value is the clean Sprint-34 hand-off (`ROCKET_CASEC_FORCING_PLAN.md`).

---

## Budget-at-Risk tally (feeds Task 10's schedule lower bound + fallback ordering)

| Track | Priority | Budget at risk | At-risk condition | Firm part (lands regardless) | Prior of REPLAN |
|---|---|---|---|---|---|
| **P1 mine (#1443)** | 1 [14–20h] | ~14–18h (mine's +1 Solve + conditional +1 floor) | a **deeper coupling** (H3) — H1 head-label re-keying won't close `N` at the 6 rows without perturbing interior | **the cross-term-correct finding + the multiplier-coupling characterization + the S31 IR foundation** (on `main`) → a de-risked Sprint-34 filing | **High** — the banked premise was twice-refuted (S32 Day-1 + S33 Task-3); H1 is an unproven third hypothesis |
| **P2 sarf (#1385)** | 2 [14–20h] | ~8–16h (the +Translate stretch) | the parametric re-emit **re-triggers the timeout** (a 4th enumeration site / builder-pipeline materialization) | **the three-site O(active) design + the re-scoping finding** (a documented builder-pipeline constraint) | **Medium-High** — a failed-architecture rebuild; V1 O(active) timing probe resolves it Day-0 |
| **P3 fawley (#1111/#1112)** | 3 [12–18h] | ~6–12h (fawley's +1 Solve — **H-a only**; the genuine emit fix lands under H-b) | the generalization **leaks onto mbal / regresses the 1-D core** (correctness-REPLAN); OR H-b (emit closes but MS-5) | **the fix-surface refinement + the H-a/H-b discriminator**; under H-b the **genuine cross-term correction ships** (a floor lever) | **Medium** (correctness-REPLAN) / **Medium-High** (the +Solve miss under H-b) |
| **P4 camcge (#1330)** | 4 [10–16h] | N/A in-sprint (Epic-5-deferred) | the `/tmp` full-redefinition stays **MS-4** (Walras deeper than the dual redefinition) | **step 1 on `main`** + the S1∧S2∧S3 detector + the numéraire recipe → Epic-5 scope | **Epic-5-deferred (expected)** — MS-1 is the Epic-5 gate, not in-sprint |
| **P5 rocket/Case-c (#1462/#1236)** | 5 [8–12h] | N/A in-sprint (rocket → Sprint-34; hhfair/CGE forcing conditional) | rocket survey exhausted; hhfair/CGE lever crossing a priori unpromising | **the FINALIZED consultation input** + the `--force` survey → Sprint-34 hand-off | **N/A** — no emit fix; **0 genuine floor**; sign flip BANNED |
| **Combined** | 1,2,3 | Solve +1 (P1 **or** P3-H-a) + genuine floor +1 (P1/P3 cold-match) + Translate +1 (P2) | — | all design/finding artifacts + camcge step-1 (on `main`) + the P5 Case-c survey land | **Task-10 lower bound: assume all three deep-track KPI gains slip; every firm part lands** |

---

## Honest KPI projection (which KPI survives each single-track REPLAN)

**Solve 107 → +1 (108)** rests on **P1 mine OR P3 fawley** landing an emit fix that reaches MS-1 in-sprint. **P4 camcge is Epic-5-deferred** (not an in-sprint Solve mover — this is the key difference from the Sprint-32 framing, which still counted camcge in-sprint); **P5 rocket is a Sprint-34 conditional**. So the in-sprint Solve mover set is exactly `{mine [P1], fawley [P3-H-a]}` — two elements, both from-scratch and both REPLAN-prone:

- **P1 REPLAN (H3 deeper coupling):** Solve +1 rests on fawley alone (P3-H-a); if P3 is H-b or REPLANs, Solve holds at 107.
- **P3 H-b or REPLAN:** Solve +1 rests on mine alone (P1-H1); the genuine emit fix under H-b lifts the *floor* but not *Solve*.
- **Solve ≥ 108 needs at least one of {P1-H1, P3-H-a} to land.** Given P1 High-prior and P3 +Solve Medium-High-at-risk, this is a genuine coin-flip, not a firm mover.
- **Solve ≥ 110 (stretch)** needs **both** in-sprint movers to land **and** camcge [Epic-5] or rocket [Sprint-34] to convert out-of-band — a priori unlikely; do not promise it.
- **model_infeasible ≤ 6** (down from 7) tracks Solve one-for-one: each landed mover gives −1; if both slip, it holds at 7.

**Match maintain ≥ 92 / genuine floor 74 → +1 (75)** is **conditional, not independent +1s** (Sprint-32 retro §3 — the ramp advanced only via an *emit-changing* track, never via presolve-methodology reclassification):

- The genuine-floor +1 needs **P1 [H1 cold-match] OR P3 [the genuine cross-term correction — which lands even under H-b]**. P3 is the **firmer** floor lever here: under H-b the emit fix still ships as a genuine cross-term correction (a cold-emit change), so it can lift the floor *even without* the +Solve. +2 (→ 76) needs both P1 and P3 cold-matches.
- **P5 (rocket + hhfair/CGE) delivers 0 genuine floor** — documented Case-c (the ν_objective reduction control-refuted, the sign flip BANNED 4×); it is a methodology/hand-off closure, **not** a floor contributor.
- **camcge step 1 (on `main`) adds no floor** — it converted `stat_mps` to Case-a but camcge stays `model_infeasible` (no match).
- **As-measured Match ≥ 92** holds under any single REPLAN (the floor is the S32 92; mine/fawley recoveries are the only as-measured in-sprint +Match movers, both conditional; all-219 Match holds at 95).

**Translate ≥ 135 → +1 (136)** rests solely on **P2 sarf**; a P2 REPLAN maintains 135 (no regression). It is the lowest-leverage KPI (moves neither Solve nor Match).

**The modal outcome is flat-KPI (Solve 107 / Translate 135 / Match 92 / genuine floor 74).** With P1 at a High prior on an unproven third hypothesis, P2's gain the lowest-leverage bucket, P3's +Solve gated behind an unresolved H-a/H-b, P4 Epic-5-deferred, and P5 zero-floor, the *expected* result is that no headline bucket moves — exactly the Sprint-32 realization, and with **one fewer firm mover** than Sprint 32 carried (camcge is now Epic-5-out-of-sprint, where S32 still counted it). The most-likely *single* gain, if any, is **genuine floor +1 via P3's genuine cross-term correction** (the one lever that lands even under its adverse hypothesis H-b). **The sprint's real product is the de-risking** — the control-confirmed root causes, the Epic-5 camcge scope, and the Sprint-34 rocket hand-off — not a bucket.

---

## Front-load ordering recommendation

Order the sprint so **every deep-track REPLAN surfaces by the Day-5 checkpoint**, not Day 11 — the Sprint-32 front-load worked exactly as designed (mine Day 1 + camcge Day 5 both REPLAN'd by Day 5, freeing the back half for P6/P7):

1. **Day 0–1: P1 mine** (highest prior, deepest architecture). Run the H1 `/tmp` head-label re-keying control **first** — it is the single most REPLAN-prone track, and its V2 warm-residual→0 check is a clean Day-1 verdict. An early H3 REPLAN frees ~14–18h into P6/P7 with the whole sprint remaining.
2. **Day 0–2: P2 sarf** (V1 is a **Day-0 timing probe** — the cheapest, earliest verdict in the sprint; run it in parallel with P1). If the three-site O(active) re-emit still times out, re-scope immediately and reallocate.
3. **Day 2–5: P3 fawley** (the H-a/H-b discriminator localizes the residual 18.47 by column early; the genuine emit fix can land even under H-b). Its no-regression control (`--resolve-changed` GO) gates the src change.
4. **Day 1–3 (parallel, low-cost): P4 camcge Epic-5 gate** — run the `/tmp` full-redefinition prototype to *confirm the deferral* (expected MS-4); if by some chance it reaches MS-1, promote it. Otherwise it is a documented Epic-5 hand-off.
5. **Day 5+ (back half): P5 rocket/Case-c** submission + the `--force` survey, then **P6** (freed-budget failure-cohort re-triage) + **P7** (property fixtures for whichever P1/P2/P3 emit paths landed + genuine-floor re-baseline + Epic-4 `SUMMARY`).

**Rationale:** P1 and P2 carry the highest REPLAN priors *and* the earliest-resolving controls (P1 a Day-1 warm-residual check, P2 a Day-0 timing probe), so front-loading them converts the sprint's dominant risk into a Day-5 fork: either the movers land (and P6/P7 are the stretch) or they REPLAN early (and P6/P7 absorb the freed budget as the primary work). Either way the back half is productive — the flat-KPI modal outcome still ships the de-risking + P6/P7 durable leverage.

---

## Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_33/REPLAN_RISK_ASSESSMENT.md && echo present
# Each deep track has a validation + a REPLAN exit + a reallocation target:
grep -cE "REPLAN exit|Budget reallocation|Single-model validation" docs/planning/EPIC_4/SPRINT_33/REPLAN_RISK_ASSESSMENT.md
# The three deepest tracks are covered:
grep -oE "Track P[123]" docs/planning/EPIC_4/SPRINT_33/REPLAN_RISK_ASSESSMENT.md | sort -u
# The honest KPI projection + the modal flat-KPI outcome + the front-load ordering:
grep -qiE "modal outcome is flat-KPI" docs/planning/EPIC_4/SPRINT_33/REPLAN_RISK_ASSESSMENT.md && echo "flat-KPI modal present"
grep -qiE "front-load ordering" docs/planning/EPIC_4/SPRINT_33/REPLAN_RISK_ASSESSMENT.md && echo "front-load ordering present"
```
