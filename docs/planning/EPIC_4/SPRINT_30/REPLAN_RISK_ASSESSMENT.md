# Sprint 30 — Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (PR16)

**Task:** Sprint 30 Prep Task 6 (the risk/decision layer over the Task-3/4/7 designs — design-only; the empirical gates are *run* in-sprint, Day 0)
**Date:** 2026-07-06
**Method:** PR16 single-model hypothesis-validation — the Task-3/4/7 Day-0 `kkt_residual.py` trace + the prototype-then-revert probes already run (zero `src/` diff), converted here into an explicit PROCEED (Sprint 30 implementation) vs REPLAN (Sprint 31 / Epic 5 re-scope) signal **per track**, with the Sprint-31 exit + the budget reallocation pinned **before** the sprint commits the combined budget.
**Instrument:** the KKT-residual harness (`scripts/diagnostics/kkt_residual.py`, PR27) + the Task-3/4 cold-solve control experiments + the Epic-5 §5 open questions. The Task-5 Phase-0 gates already produced the Day-0 verdicts cited below; this task adds the risk/probability/reallocation layer the schedule (Task 10) consumes.
**Why:** Sprint 27–29 showed deep AD / non-convex / domain-specific fixes routinely prove multi-site (cclinpts reverted, mine 3-site Day-7), intrinsic (rocket non-convergence), or structural (camcge singular Jacobian). **All three Sprint-30 deep tracks were REPLAN'd *out of* Sprint 29 for exactly these reasons** — so the risk that they slip *again* (to Sprint 31 / Epic 5) is the single largest Sprint-30 schedule unknown. This assessment prices that risk.

> **Scope note — this is a fix-shape / firm-part question, not a Case-b-vs-Case-c discriminator.** Task 3 already established mine is harness-**Case b** (a confirmed emit bug, convex LP — no non-convexity escape), and Task 4 established rocket is intrinsic non-convergence (**Case c** — no emit fix). So the REPLAN question here is: *for each track, is the confirmed-scope fix a localizable single-sprint deliverable (PROCEED), or a distributed / PATH-internal / domain-specific re-derivation that hands to Sprint 31 (REPLAN)* — and, critically, **what firm part lands regardless** (robert / the forcing scaffold / the Class-B general-emit fix). The headline **Solve ≥ 109 depends on *both* mine (P1) and rocket (P2)** landing their +1 Solve — the single most REPLAN-sensitive KPI — while the genuine-floor lift is robust (robert / Class-B / offset-alias are cold-robustness, not the as-measured Solve).

---

## Track A — #1443 mine (Priority 1): the head-offset architecture is mine-only; robert is a decoupled genuine-floor fix

**Decision pivot (Unknowns 1.1, 1.2):** the banked Sprint-29 premise was "robert is the pure-constant-offset minimal reproduction of mine → one head-offset fix converts both." **Task 3 refuted it** (Unknown 1.1 = ❌ does NOT generalize): robert's real bug is an **objective-gradient boundary-term drop** in `stat_s` (same class as the Sprint-29 Day-3 #1447 maxmin objvar fix), while mine's firm bug is a **`comp_pr` `l+1`-head × `li(k)`/`lj(k)`-parameter-offset coupling** (a constraint-Jacobian re-derivation, `ISSUE_1443` Day-7). **Different bug classes, no shared code path.** The favourable consequence: Priority 1 **splits into two independent tracks**, which *de-risks and decouples* the robert genuine-floor gain and *isolates* mine as the one REPLAN-prone half. So there are two sub-decisions:

- **robert (genuine-floor +1) — not REPLAN-prone.** A LOW-risk, standalone, single-site objective-gradient fix, **cold-confirmed** at 11025.0 (= the NLP optimum) by the Task-3 control experiment (no warm-start; robert is a convex LP ⇒ a correct emit *must* cold-solve, so there is no Case-c escape and no REPLAN branch). ~2–4 h. **This is the firm part of Track A: it lands regardless of mine.**
- **mine (+1 Solve) — the REPLAN-prone head-offset architecture.** The REPLAN question is whether the coordinated 3-site index-map re-derivation (Unknown 1.2) fits the Priority-1 budget and drives mine's cold LCP to MS 1 — or whether each fixed site exposes the next (the Day-7 signature).

**Binding Task-3 record:** the three sites are (1) `comp_pr` head-var emission (cold `mine_mcp.gms:106`; gate `src/kkt/stationarity.py:5750`), (2) the `--nlp-presolve` dual transfer (`src/emit/emit_gams.py:1281`, `lam_pr.l = abs(pr.m)`), (3) the landed `stat_x` cross-term (`src/kkt/stationarity.py:5562-5570`, #1224). The Day-7 experiment fixed **Site 2 alone** (dual transfer → `pr.m(k,l+1,i,j)`), evaluated at the NLP optimum, and **cleared only the `nw` direction** (`li=lj=0`), leaving **`ne`/`se`/`sw`** (parameter offsets active) at **~1e10 `comp_pr` infeasibility**. So the head×parameter-offset coupling is real and Site 2 does not close it — the design requires a **single shared head-offset index-map helper** all three sites call, applied atomically (a partial fix = no Solve gain). mine is a convex LP (monotone LCP) ⇒ no Case-c escape ⇒ the cold `x → 4e10` *is* the `comp_pr` LCP residual, and a correct 3-site emit must drive it to 0.

### Single-model validation design (PR16 — Day-0, zero `src/` diff)

| Step | Action | Output |
|---|---|---|
| A0 | **robert (firm):** `kkt_residual.py data/gamslib/raw/robert.gms` + the Task-3 `stat_s`-patch cold-solve control (already: cold **11025.0 = MATCH**) | robert's objective-gradient fix is cold-confirmed; land it early + standalone |
| A1 | **mine:** `kkt_residual.py data/gamslib/raw/mine.gms` — re-read the Case-b verdict + max-residual row + dual-transfer self-check (already: **Case b**, transfer consistent) | confirms the confirmed-emit-bug scope (not non-convexity) |
| A2 | **Cold-INFES cross-check:** generate `mine_mcp.gms`, solve cold, map INFES by row prefix — dominated by `comp_pr`/`pr` (the Day-7 coupling) vs spread across `comp_lo_x`/`comp_up_x`/bound rows (a 4th site) | an INFES-by-row-type histogram (is the site set complete?) |
| A3 | **3-site coherence probe (env-guarded, revert):** apply the shared `l+1`/`±li(k)`/`±lj(k)` index map at all three sites simultaneously, warm-start from the NLP optimum, and measure whether the cold LCP reaches MS 1 (or the residual drops monotonically) | does a *coordinated* fix converge, or does each site expose the next? |

### Recommendation: **robert PROCEED (firm) · mine conditional — lean REPLAN-aware**

- **robert: PROCEED unconditionally (firm genuine-floor +1).** Cold-confirmed at 11025; convex LP ⇒ no non-convexity risk; a single objective-gradient site (`src/ad/gradient.py` `find_objective_expression` / `src/kkt/stationarity.py`), the #1447 family — **not** the head-offset builder. Schedule it early and standalone (Task 10); it does not wait on, or share code with, the mine architecture. No REPLAN branch.
- **mine: PROCEED to the coordinated 3-site `comp_pr` fix** if A2 shows the INFES is **dominated by `comp_pr`/`pr` rows** (the site set is complete — no 4th bound-row site) *and* A3's shared index-map drives the cold LCP to MS 1 within the **~10–16 h design estimate (Task 3) inside the ~14–20 h Priority-1 budget ceiling**. The fix lands atomically across the three sites.
- **mine: REPLAN (mine only, NOT robert) to a Sprint-31 head-offset-architecture workstream** if A2 shows the INFES is **distributed onto a 4th site** (`comp_lo_x`/`comp_up_x`/bound coupling) *or* A3 shows each fixed site exposes the next (the Day-7 cascade persists) *or* the cold-LCP coupling does not close within the budget. **robert still lands** (the genuine-floor +1 is unaffected — the split is precisely what protects it).
- **Deciding signal:** A2's INFES-by-row histogram (site-set completeness) + A3's coordinated-fix convergence (cold LCP → MS 1, or the Day-7 cascade).
- **Sprint-31 exit scope (mine):** "the head-domain-offset emit architecture — a single `comp_pr`/`lam_pr`/`stat_x`/bound index-map helper parameterized by (head-offset δ, parameter offsets `li(k)`/`lj(k)`), applied identically at all emit sites, with cold-LCP consistency for the `l+1 × li/lj` coupling." Still Case b (a confirmed emit bug), just larger than one Priority slot.
- **Budget at risk:** ~10–16 h (mine's whole +1 Solve is conditional). **Firm part: robert (~2–4 h, genuine-floor +1) lands regardless.**
- **Prior-probability of REPLAN (mine): Medium-High.** The Day-7 evidence (Site 2 clears only `nw`; `ne`/`se`/`sw` at ~1e10; the head×parameter-offset coupling is un-budgeted) raises the prior of the distributed/architectural outcome. The Task-10 lower bound should assume mine's +1 Solve may slip to Sprint 31; robert's genuine-floor +1 is firm.

---

## Track B — #1462 rocket (Priority 2): the forcing scaffold is firm; rocket's +1 Solve is a Sprint-31 PATH-consultation hand-off

**Decision pivot (Unknowns 2.1, 2.2):** does an nlp2mcp-emittable forcing lever move rocket's residual MS-5 (the landed `_fx_` warm-start left it at objective 1.016, MS 5 persisting) toward MS 1/2 at the NLP optimum 1.0128 (**PROCEED** — a Sprint-30 Solve) — or is the effective lever a **PATH solver option** whose tuning is PATH-internal (**REPLAN** — a Sprint-31 PATH-author consultation, with the P8 forcing scaffold as the firm Sprint-30 deliverable)? rocket is non-convex (Goddard rocket: division-by-variable `1/ht²`,`1/m²` initial Jacobian) ⇒ the Case-c "intrinsic non-convergence" exit is live.

**Binding Task-4 record:** the Task-4 prototype-probe emitted rocket's presolve MCP (carrying the Day-1 `_fx_` warm-start) and applied the tunable levers via an env-guarded transient `path.opt` + `mcp_model.optfile=1` (zero `src/`). Baseline: MCP **MS 5, 477 INFES, 0 eval errors** (embedded NLP MS 2). Across `proximal_perturbation` ∈ {1e-2, 1e-1, 1.0, 1e2} (trust-region / Levenberg-Marquardt Jacobian regularization), `crash_method pnewton`, `merit_function normal`, and combined strong configs, rocket **stays MS 5**; the best config (`merit_function normal` + `proximal_perturbation 1e-2`) reduces INFES **477 → 382** (~20 %) but **never converges**. The three *tunable* levers are **PATH options** (emittable optfile, but PATH-internal tuning); the two *structural* levers (homotopy/continuation, multi-start) are **emittable GAMS** — the P8 scaffold. **No Case-c shared payoff:** the 4 Case-c cohort models (bearing/launch/mathopt3/robustlp) are emit-correct and **already warm-match** (`compare_objective_match`, residual ≤ 8e-6) — rocket is the **sole** genuinely-non-converging model, so a forcing lever has no additional cohort to lift.

### Single-model validation design (PR16 — Day-0, zero `src/` diff)

| Step | Action | Output |
|---|---|---|
| B1 | `kkt_residual.py data/gamslib/raw/rocket.gms` — read verdict (Case c / intrinsic non-convergence, ISSUE_1462 Day-2) | confirms the residual is convergence, not an emit bug |
| B2 | **PATH-option lever sweep (env-guarded `path.opt` + `optfile=1`, revert):** `proximal_perturbation` {1e-2,1e-1,1.0,1e2}, `crash_method pnewton`, `merit_function normal`, combined — re-solve, read MS + INFES | **done (Task 4):** all MS 5; best INFES 477 → 382; no config reaches MS 1/2 or 1.0128 |
| B3 | **Emittable-GAMS lever check:** classify homotopy/continuation + multi-start as the P8 scaffold; confirm the tunable levers are PATH-side (the nlp2mcp/PATH boundary, Unknown 2.2) | the scaffold is the firm deliverable; the tuning is PATH-internal → Sprint-31 |

### Recommendation: **PROCEED-to-scaffold (firm P8) · rocket +1 Solve → Sprint-31 (deferred, on the evidence)**

- **PROCEED to the P8 emitted-GAMS forcing scaffold (firm).** Build the `--force <strategy>` driver (homotopy/continuation loop + multi-start `.l`-perturbation loop + optional emitted PATH `optfile`) as the P8 entry point; validate its plumbing on rocket (it *runs* the levers) + a MODEL-STATUS reporter. **This scaffold is the firm Sprint-30 P2/P8 deliverable — it lands regardless of whether rocket converges.**
- **rocket's +1 Solve: REPLAN to the Sprint-31 PATH-author consultation.** On the Task-4 evidence, **no tunable PATH-option configuration forces rocket** — even warm-started from the NLP optimum it stays MS 5. So rocket's +1 Solve is **NOT firm for Sprint 30**; it is conditional on the Sprint-31 PATH consultation (or a reformulation of the division-by-variable optimal-control MCP). The honest projection: the scaffold lands; rocket's solve does not.
- **The one PROCEED-flip condition:** if, during the P8 scaffold validation, a *homotopy/continuation* or *multi-start* schedule (an emittable-GAMS lever the Task-4 probe did **not** exhaustively drive — the multi-start `.l`-perturbation probe was inconclusive) drives rocket to MS 1/2 at ~1.0128, then rocket's +1 Solve lands in Sprint 30. The prior is low (warm-starting from the NLP optimum itself already fails ⇒ random restarts are a priori unpromising), but the scaffold makes the check nearly free.
- **Deciding signal:** whether any scaffold strategy (homotopy/multi-start) reaches MS 1/2 at 1.0128; else the PATH-option INFES-477→382 stall is the Sprint-31 hand-off.
- **Sprint-31 exit scope (rocket):** "rocket's MCP is MS 5 with `EXIT — other error` at an ill-conditioned initial Jacobian (`1/ht²`,`1/m²`); `proximal_perturbation`/`merit_function`/`crash_method` move INFES 477 → 382 but do not converge from the NLP-optimum warm-start. Which PATH option set / regularization schedule / reformulation forces convergence?" — the concrete PATH-consultation question.
- **Budget at risk:** rocket's +1 Solve (conditional). **Firm part: the P8 forcing scaffold + the PATH-consultation hand-off land regardless.**
- **Prior-probability of REPLAN (rocket +1 Solve): High.** The warm-start is known-necessary-but-insufficient, non-convexity is confirmed, and no PATH-option config converges. The Task-10 lower bound should assume rocket's +1 Solve slips to Sprint 31; the scaffold is the firm deliverable.

---

## Track C — #1330 camcge (Priority 6, Epic 5): the Walras transform is paper-verified; the empirical MS-1 + the detection-heuristic reliability are the two gates

**Decision pivot (Unknowns 6.1, 6.2):** the Epic-5 Walras transformation (drop the redundant market-clearing row `lmequil` + fix a price numéraire `cpi=1`) is **solution-preserving on paper** (`CGE_DEGENERACY_SCOPING.md` §3: Walras redundancy ⇒ the dropped row is free; price homogeneity ⇒ the numéraire fix is a selection, not a perturbation) and reproduces camcge's NLP optimum 191.7346. Two things must hold to PROCEED in Sprint 30: **(6.1)** the transform **empirically** reaches MODEL STATUS 1 at 191.7346 in a real GAMS solve (not the current MS-4-at-iteration-0 singular-Jacobian signature), and **(6.2)** the degeneracy-**detection heuristic** reliably recognises camcge **without false-flagging a well-posed model** (silently dropping a user row / fixing a price on a non-degenerate model would corrupt a correct problem — a correctness gate, not an optimization).

**Binding Task-5 / Epic-5 record:** the #1330 gate (Task-5-refreshed) records PROCEED to the Epic-5 CGE-domain preprocessing transformation; the emitted KKT system is **structurally correct at the NLP optimum** (`gdp_check ≈ -4.83e-10`), so this is an inherent CGE rank-deficiency, **not** a localizable emit bug. camcge is the **sole** inherent Walras case in the corpus (Sprint-29 Unknown 5.1 inverted: the "CGE cohort" #1354/#1355/#1317/#1331/#1251 are *distinct ordinary emit bugs*, and the Class-B `stat_pz` cluster is a *separate general-emit* discrepancy — Category 7, confirmed NOT Walras). The three Epic-5 §5 open questions block implementation: (Q1) numéraire-selection rule, (Q2) the detection heuristic that must not false-positive, (Q3) the empirical confirmation.

### Single-model validation design (PR16 — Day-0, run at P6 Day-0)

| Step | Action | Output |
|---|---|---|
| C1 | **Empirical (6.1):** emit camcge with `lmequil` dropped + `cpi=1` fixed; solve cold; read MS + objective | expect **MS 1 at 191.7346** (the transform reproduces the NLP optimum) vs MS-4-at-iter-0 |
| C2 | **PATH basis check:** confirm the basis is non-singular after the transform (the rank deficiency removed) | the singular-Jacobian signature is gone |
| C3 | **Detection heuristic (6.2):** run the degeneracy detector (a market-clearing-block rank check / PATH basis-singularity report / structural signature) across camcge + irscge/lrgcge/moncge/stdcge; count false positives | expect **only camcge flagged**; any well-posed CGE flagged = a false positive |

### Recommendation: **PROCEED-conditional (empirical + heuristic gates) · REPLAN to a per-model declaration if the heuristic is unreliable**

- **PROCEED to the Epic-5 Walras transformation** if C1 reaches **MS 1 at 191.7346** (the paper argument confirmed in GAMS) *and* C3's detection heuristic flags camcge with **zero false positives** across the CGE cohort. The transform lands as a CGE-domain preprocessing layer invoked only for detected-degenerate models.
- **REPLAN to a per-model-numéraire-declaration Epic-5 item (opt-in)** if C3's heuristic **false-flags a well-posed model** (the correctness gate fails) *or* the redundant-row / numéraire selection proves **per-model** (no robust automatic rule, Unknown 6.3). The fallback — a per-model opt-in declaration of the numéraire + redundant row — is **viable and acceptable because camcge is the sole inherent case** (Sprint-29 Unknown 5.1): a single hand-declaration ships the camcge +1 Solve without an auto-detector, deferring the general heuristic to a later Epic-5 iteration. If C1 itself does not reach MS 1, the transform premise is invalid → deeper Epic-5 diagnosis, and the Class-B general-emit work (P7) absorbs the freed budget.
- **Deciding signal:** C1's MS/objective (empirical solution-preservation) + C3's false-positive count (heuristic reliability).
- **Sprint-31 / Epic-5 exit scope:** "a per-model numéraire + redundant-row *declaration* (opt-in), deferring the automatic degeneracy detector + numéraire-selection rule to a later Epic-5 iteration" — the correctness-safe fallback that still lands camcge's +1 Solve.
- **Budget at risk:** camcge's +1 Solve via the *automatic* transform. **Firm part: the Class-B `stat_pz` general-emit fix (P7) — a distinct track, unaffected by camcge — lands regardless; and the per-model-declaration fallback still lands camcge if the auto-heuristic is the only thing that fails.**
- **Prior-probability of REPLAN (auto-heuristic → per-model declaration): Medium.** The paper argument is solid and camcge-being-sole makes the false-positive surface small, but a *robust automatic* detector that never corrupts a well-posed model is the unproven piece (Unknown 6.2 is the correctness gate). The likeliest outcome is PROCEED-with-declaration (the +1 Solve lands via opt-in; the auto-detector is a stretch).

---

## Budget-at-Risk Tally (feeds Task 10's schedule lower bound + fallback ordering)

| Track | Priority | Budget at risk | At-risk condition | Firm part (lands regardless) | Prior probability of REPLAN |
|---|---|---|---|---|---|
| **#1443 mine** | 1 | ~10–16 h (mine's whole +1 Solve is conditional) | INFES distributed onto a 4th site / the Day-7 head×parameter-offset cascade persists (architectural) | **robert** (~2–4 h, genuine-floor +1, cold-confirmed 11025 — decoupled) | **Medium-High** — Day-7: Site 2 clears only `nw`; `ne`/`se`/`sw` ~1e10 |
| **#1462 rocket** | 2 | rocket's +1 Solve (conditional) | no emittable-GAMS lever converges; the tuning is PATH-internal | **the P8 forcing scaffold** + the PATH-consultation hand-off | **High** — no PATH-option config converges even from the NLP optimum |
| **#1330 camcge** | 6 (Epic 5) | camcge's +1 Solve via the *automatic* transform | the detection heuristic false-flags a well-posed model / numéraire is per-model | **the Class-B `stat_pz` general-emit fix (P7)** + the per-model-declaration fallback (still lands camcge) | **Medium** — paper argument solid; the robust auto-detector is the unproven piece |
| **Combined** | 1, 2, 6 | mine + rocket +1 Solve (the two Solve-target movers) | — | robert + the forcing scaffold + the Class-B fix + the camcge declaration-fallback | **Task 10 lower bound: assume mine + rocket's +1 Solve slip; every firm part lands** |

**Reallocation plan per REPLAN:**

- **#1443 mine REPLAN** (→ Sprint-31 head-offset architecture): the freed ~10–16 h pre-allocates to the **genuine-floor cohort** — additional **Class-B CGE `stat_pz`** general-emit conversions (P7) and the **offset-alias** himmel16/polygon cold-robustness (P5, #1146/#1143). Both are lower-risk shared-fix-class backlogs that absorb budget as genuine-floor lift. robert lands regardless.
- **#1462 rocket REPLAN** (→ Sprint-31 PATH consultation): the P8 forcing scaffold (firm) still lands; the freed rocket-specific tuning budget pre-allocates to **the scaffold's homotopy/multi-start strategies** (hardening the entry point) + **Priority 3 hhfair (#1236)** — the `$184` widened-VARIABLE +Match target.
- **#1330 camcge REPLAN** (→ per-model declaration / deeper Epic-5): the freed auto-heuristic budget pre-allocates to the **Class-B `stat_pz` general-emit fix (P7)** — the distinct, higher-confidence CGE general-emit track (a coefficient discrepancy across irscge/lrgcge/moncge, one fix several models). The per-model-declaration fallback still lands camcge's +1 Solve.

**The Task-10 schedule's lower bound** assumes Priorities 1 (mine) and 2 (rocket) slip their +1 Solve to Sprint 31 — so **Solve ≥ 109 is the most REPLAN-sensitive KPI** (it needs *both* mine and rocket) and the schedule must front-load them with their Day-0 gates (A2/A3, B2/B3) as the early decision points, and pre-commit the reallocation to the genuine-floor Class-B / offset-alias work. The **firm parts land regardless** (robert genuine-floor +1, the forcing scaffold, the Class-B general-emit fix, the camcge declaration-fallback), so the **genuine-floor lift is robust** even under a triple-REPLAN. The **upper bound** assumes all three PROCEED (mine + rocket + camcge auto-transform).

## Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_30/REPLAN_RISK_ASSESSMENT.md && echo present
grep -cE 'PROCEED|REPLAN' docs/planning/EPIC_4/SPRINT_30/REPLAN_RISK_ASSESSMENT.md
grep -qiE '#1443|mine|robert' docs/planning/EPIC_4/SPRINT_30/REPLAN_RISK_ASSESSMENT.md \
  && grep -qiE '#1462|rocket' docs/planning/EPIC_4/SPRINT_30/REPLAN_RISK_ASSESSMENT.md \
  && grep -qiE '#1330|camcge' docs/planning/EPIC_4/SPRINT_30/REPLAN_RISK_ASSESSMENT.md \
  && echo "3 tracks present"
grep -qiE 'Sprint 31|Sprint-31' docs/planning/EPIC_4/SPRINT_30/REPLAN_RISK_ASSESSMENT.md \
  && grep -qiE 'realloc|freed budget|budget-at-risk|Budget-at-Risk' docs/planning/EPIC_4/SPRINT_30/REPLAN_RISK_ASSESSMENT.md \
  && echo "exits + reallocation present"
```
