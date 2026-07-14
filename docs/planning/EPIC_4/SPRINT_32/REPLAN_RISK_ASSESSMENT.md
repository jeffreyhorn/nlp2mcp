# Sprint 32 — Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (PR16)

**Task:** Sprint 32 Prep Task 9
**Date:** 2026-07-14
**Owner:** Sprint planning
**Scope:** docs/analysis only — consumes the Task-3/4/5 designs + the Task-8 Phase-0 gates; no `src/` change.

---

## Executive summary

Sprint 32's carryforwards are the five tracks Sprint 31's Day-13 closeout explicitly REPLAN'd *because* they proved deeper than projected — P1 a **4th** head-offset site *after* the IR foundation landed; P2 an **O(instances) 369K** blow-up, not O(constraints); P3 a **CASE_B `nu_mps_fx`** fixing-multiplier defect, not clean Walras; P4/P5 **intrinsic non-convexity**. This assessment applies the PR16 hypothesis-validation discipline to the **three deepest REPLAN-prone tracks** — **P1 (mine 4th-site bound-dual, deeper-IR risk)**, **P2 (sarf 4-D sparsification, timeout-re-trigger risk)**, **P3 (camcge Epic-5, dual-consistency risk)**: each gets a **single-model / control-experiment validation** (measurable by the Day-5 checkpoint), an **explicit Sprint-33 REPLAN exit**, and a **budget-reallocation target** if it stalls. (P4 rocket is a Task-6 packaged hand-off; P5 hhfair/CGE is a Task-7 documented-Case-c with **0 genuine floor** — neither is a deep implementation track, but both appear in the KPI projection.)

**The decisive mitigation (Sprint-31 §4 + the Sprint-30 §3 lesson):** each track now carries a **precisely-pinned root cause**, so Sprint 32 implements against specifications, not open questions — mine's residual is localized to the presolve bound-multiplier transfer (`src/emit/emit_gams.py:1548–1577`, `piL_x/piU_x = ±x.m` vs the residual `N`, Task 3); sarf's blow-up is the 369,024-instance 4-D `stat_task`, sparsifiable to **398 active** (Task 4); camcge is a **split** track — step 1 (`nu_mps_fx.l = -mps.m`, `mps.m = −209.861`) is a general emit fix that clears the CASE_B residual regardless, step 2 the Epic-5 dual-consistent Walras (Task 5). So REPLAN risk is **bounded**, and every REPLAN hands cleanly to a Sprint-33 filing rather than a dead end.

**The honest KPI projection (Sprint-30 §3 lesson 3, binding — re-confirmed by the Sprint-31 retro §3, where the genuine-floor ramp was carried entirely by ONE emit-changing track [polygon], not the projected three):** treat **Solve 107 → ≥ 109 as conditional on BOTH mine [P1] AND camcge [P3]** (the most REPLAN-sensitive KPI); treat **genuine floor 74 → ≥ 75 as conditional on mine/camcge COLD-matching or a P6 emit change — NOT on presolve-methodology reclassification** (P5 delivers 0 floor); treat **Translate +1 as conditional on sarf [P2]**. (See the "Honest KPI projection" section below.)

---

## Track P1 — mine Head-Offset 4th Bound-Complementarity Site (#1443)

**Bug class (pinned, Task 3):** Sprint 31 Days 1–2 landed the head-offset **IR foundation** — the `EquationDef.head_domain_offsets` field + the shared `head_offset_marginal_index_map` Site-2 `--nlp-presolve` dual transfer, both on `main` (16 guard tests green). The residual **4th site** is the presolve **bound-multiplier warm-start transfer** (`src/emit/emit_gams.py:1548–1577`): it sets `piL_x/piU_x = ±x.m` (the LP reduced cost), but at mine's degenerate-LP vertex `x.m ≠ N`, where `N` = the non-bound part of `stat_x` (`−obj_grad + Σ_k[lam_pr(k,l,i−li,j−lj)$c − lam_pr(k,l−1,i,j)$c]`), so `stat_x = N − (±x.m) ≠ 0`. The fix is **derivable by construction**: `piL_x = max(N,0)`, `piU_x = max(−N,0)` closes `stat_x = N − piL_x + piU_x = 0` exactly and respects the complementarity pairing.

**Single-model validation (PR16):**

| Step | Gate | Measurable by |
|---|---|---|
| V1 | The harness reproduces the Day-3 fingerprint (CASE_B, `stat_x(3,1,1)` rel 2.37 / raw −3.2e4, dual-transfer CONSISTENT, dual scale 1.35e4) — the residual localizes entirely to `stat_x` rows with the duals CONSISTENT (`lam_pr`/`pr.m` correct) | Day-0 (✅ done, Task 3) |
| V2 | The `N`-derivation transfer drives the **warm residual → 0** (Case-a, `modelstat` asserted — the `x.up=inf` measurement error is BANNED) → **presolve MS-1** (+1 Solve); **no 5th coupling** (a fresh `stat_x` residual after the `N`-derivation, or `sign(N)` contradicting the bound-active status) | **Day-5 checkpoint** |

**REPLAN exit (Sprint 33):** a **5th coupling** (the warm residual does not close, or the derived bound-multiplier contradicts the complementarity sign) → a **Sprint-33 deeper head-offset bound-complementarity architecture workstream**. The **de-risked hand-off**: the `MINE_BOUND_MULTIPLIER_DESIGN.md` localization + the residual `N` characterization + the S31 IR foundation (already on `main`, correct regardless) make that filing a specification, not an open question. mine's +1 Solve becomes a Sprint-33 carry.

**Budget reallocation on REPLAN:** mine's remaining ~8–14h (of the 14–20h) → **P6** (generalize the #1111/#1112 offset-alias second-index-transpose core beyond polygon/ps2 — the firmest remaining **genuine-floor** lever, an emit-changing fix) + **P7** (property fixtures + genuine-floor tracking). mine's +1 Solve + its conditional +1 genuine floor become conditional.

**Prior of REPLAN: Medium.** Lower than a from-scratch track — the IR blocker that forced the Sprint-31 Day-3 REPLAN is *landed*, and the fix is derivable by construction (`piL_x = max(N,0)`). The residual risk is the 5th-coupling question, which the Day-5 warm-residual→0 check resolves early. But mine is a **degenerate LP** — the bound-dual ambiguity is exactly the class that has surfaced fresh couplings before, so this is not a low prior.

---

## Track P2 — sarf 4-D `task`-Variable Stationarity Sparsification (#1385)

**Bug class (pinned, Task 4):** Sprint 31 Day 8 found the 2-D constraint gate fires but sarf still times out (>180s) on the **369,024-instance** 4-D `task(g,t,mn,mn)` `stat_task` enumeration — the full Cartesian product, not the **1,152 constraints** or the **398 active** `taskposs(g,t) ∧ tech(g,m,n)` instances. The fix: emit **one** symbolic guarded `stat_task(g,t,m,n)$taskposs(g,t)` equation (the banked 7-term hand-derivation) + `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0`. Sites: `src/ad/index_mapping.py` (extend `_is_blowup_dynamic_subset_equation` from 1-D to sarf's 2-D dynamic-subset shape) + `src/kkt/stationarity.py`.

**Single-model validation (PR16):**

| Step | Gate | Measurable by |
|---|---|---|
| V1 | The symbolic re-emit is **O(active = 398), not O(369,024)** — `sarf_mcp.gms` translates in **seconds** (srpchase's 1-D analogue is 6.56s), well under the >180s Option-1 timeout | **Day-0 timing probe** (Task 9 designed; in-sprint measured) |
| V2 | The re-emitted `stat_task` matches the **banked 7-guarded-term hand-derivation** with **no set-name-literal multiplier indices** (the Sprint-26 `nu_slack("srn")` failure, commit `243fe578`; grep scan `nu_[[:alnum:]_]+\("` = empty); the 2-D gate + the 4-D sparsification + the `J_gᵀ·lam` cross-terms + `task.fx` land **atomically**; golden byte-stable; `--resolve-changed` GO (sarf only) | mid-sprint |

**REPLAN exit (Sprint 33):** the parametric re-emit **re-triggers the translate timeout** (O(instances) after all) → **re-scope the parametric emit** (a documented builder-pipeline constraint); +Translate deferred; sarf stays `translate_failure`. The **de-risked hand-off**: the `SARF_STAT_TASK_SPARSIFICATION_DESIGN.md` O(active) sparsification design + the timing evidence make the re-scoping a documented finding, not a dead end.

**Budget reallocation on REPLAN:** sarf's remaining ~8–16h (of the 14–20h) → **P6** + **P7**. The +Translate stretch is the **lowest-priority KPI** — it moves neither Solve nor Match.

**Prior of REPLAN: Medium-High.** This is a *failed-architecture rebuild* — the Sprint-26 Day-4 attempt failed on exactly the set-name-literal + combinatorial-blow-up axes this gate guards, and sarf's 369K enumeration is the worst-case instance of that axis. The V1 O(active) timing probe resolves the dominant risk **Day 0** (before any downstream emit work), which is what caps the prior below "High."

---

## Track P3 — camcge `stat_mps` + Dual-Consistent Walras (#1330 → Epic 5)

**Bug class (pinned, Task 5 — a SPLIT track):** Sprint 31 Days 6–7 re-diagnosed camcge as **CASE_B** (the `nu_mps_fx` fixing-multiplier defect), *not* the clean Walras singular-Jacobian case. **Step 1 (a general nlp2mcp emit fix):** the #1462 "transfer fixed-variable marginals to `_fx_` multipliers" block (`src/emit/emit_gams.py`) misses `nu_mps_fx`; the CASE_B `stat_mps` residual is `mps.m = −209.861` (≈ the −210 gradient), so `nu_mps_fx.l = -mps.m` (sign per the multiplier's stationarity role) clears it. **Step 2 (the Epic-5 dual-consistency):** the redundant market-clearing row's Walras singularity — keep every market-clearing row + a consumption-weighted numéraire + redefine the redundant dual via Walras' law → **omega 191.7346**.

**Single-model validation (PR16 — control-experiment-before-implement):**

| Step | Gate | Measurable by |
|---|---|---|
| V1 (step 1) | `nu_mps_fx.l = -mps.m` → `kkt_residual.py camcge.gms` `stat_mps` → **Case-a** (the CASE_B residual clears; a general emit fix, low risk) | Day-0/early |
| V2 (step 2) | The **`/tmp` prototype** of step 1 + the dual-consistent Walras reaches **MS-1 at omega 191.7346** (`modelstat` asserted) **before** the Walras `src/` change; the **S1∧S2∧S3 detector flags only camcge** across irscge/lrgcge/moncge/stdcge (S3 = cold-MCP-singular-at-iter-0, the false-positive guard) | mid-sprint |

**REPLAN exit (Sprint 33 / Epic 5):** the `/tmp` prototype (step 1 + step 2) stays **MS-4** (the Walras rank-deficiency is deeper than a numéraire selection) → **step 1 lands anyway** (a cleaner CASE_B → Case-a general emit fix, benefiting any fixed-scalar model), the numéraire falls to a **per-model-numéraire-declaration Epic-5 item**; camcge stays `model_infeasible` in Sprint 32 and its +1 Solve defers to Epic 5. The **de-risked hand-off**: step 1 (the general emit fix) + the `/tmp` dual diagnosis pin the Epic-5 scope precisely.

**Budget reallocation on REPLAN:** camcge's remaining ~6–12h (of the 12–18h) → **P6** + **P7**. **Step 1 lands regardless** (a cleaner emit + a resolved CASE_B), so P3 is **partly de-risked** — only the Solve +1 (which needs the Walras convergence) is at risk, not the emit-correctness fix.

**Prior of REPLAN: Medium.** Step 1 is a near-certain general emit fix (`mps.m = −209.861` measured, matches the −210 residual). The real risk is **step 2** — the Epic-5 Walras dual-consistency is a redefinition not yet `/tmp`-verified to MS-1; the V2 `/tmp` prototype resolves it *before* any Walras `src/` change. Step-1 firmness is what caps this at Medium rather than Medium-High.

---

## Budget-at-Risk tally (feeds Task 10's schedule lower bound + fallback ordering)

| Track | Priority | Budget at risk | At-risk condition | Firm part (lands regardless) | Prior of REPLAN |
|---|---|---|---|---|---|
| **P1 mine (#1443)** | 1 [14–20h] | ~8–14h (mine's +1 Solve + conditional +1 floor) | a **5th coupling** — the warm residual won't close under the `N`-derivation | **the bound-multiplier design + the S31 IR foundation** (on `main`) → a de-risked Sprint-33 filing | **Medium** — IR blocker landed, fix derivable; the degenerate-LP 5th-coupling question remains |
| **P2 sarf (#1385)** | 2 [14–20h] | ~8–16h (the +Translate stretch) | the parametric re-emit **re-triggers the timeout** (O(instances) after all) | **the O(active) sparsification design + the re-scoping finding** (a documented builder-pipeline constraint) | **Medium-High** — a failed-architecture rebuild; V1 O(active) timing probe resolves it Day-0 |
| **P3 camcge (#1330)** | 3 [12–18h] | ~6–12h (camcge's +1 Solve — **step 2 only**) | the `/tmp` prototype stays **MS-4** (Walras rank-deficiency deeper than a numéraire) | **step 1 `nu_mps_fx.l=-mps.m`** (a general emit fix, clears CASE_B) + the `/tmp` dual diagnosis → Epic-5 scope | **Medium** — step 1 near-certain; step 2 Epic-5 dual-consistency is the risk, V2 `/tmp` resolves it pre-src |
| **Combined** | 1,2,3 | Solve ≥109 (P1 + P3) + genuine floor ≥75 (P1/P3 cold-match + P6) | — | all design/finding artifacts + camcge step-1 emit fix + the P5 Case-c classifier land | **Task-10 lower bound: assume mine's + camcge's Solve +2 and the genuine-floor lift may slip; every firm part lands** |

---

## Honest KPI projection (which KPI survives each single-track REPLAN)

**Solve 107 → ≥ 109** rests on **mine [P1] + camcge [P3]** (rocket [P4] is a conditional third → the Sprint-33 PATH-consultation input on the evidence). Since the mover set `{mine, camcge}` has exactly two elements, **≥ 109 needs BOTH** — the **most REPLAN-sensitive KPI**:

- **P1 REPLAN (5th site):** Solve ≥ 109 misses by 1 (camcge alone → 108) unless rocket [P4] converts. mine's +1 becomes a Sprint-33 carry.
- **P3 REPLAN (step-2 Epic-5 deferral):** step 1 lands (a cleaner emit), but camcge stays `model_infeasible` in Sprint 32 → Solve 108 (mine alone) unless rocket converts. Note the per-model-numéraire fallback is an **Epic-5 item that does not land in Sprint 32**, so camcge's +1 Solve is genuinely at risk here (unlike the Sprint-31 framing, which assumed a fallback that still solves in-sprint).
- **Both P1 + P3 firm ⇒ Solve 109.** This is the target line, and it is exactly the "needs both" fragility the Sprint-30 retro warned about.
- **model_infeasible ≤ 5** (down from 7) tracks Solve one-for-one: −2 needs both mine + camcge to recover; each single REPLAN gives −1 (≤ 6).

**Match maintain ≥ 92 / genuine floor 74 → ≥ 75** is **conditional, not independent +1s** (Sprint-30 §3 lesson 3, re-confirmed by the Sprint-31 retro §3 — the ramp advanced only via an **emit-changing** track [polygon], never via presolve-methodology reclassification):

- The genuine-floor +1 needs **mine [P1] OR camcge [P3] to COLD-match** (a genuine emit change — not merely presolve-solve, which is methodology) **or a P6 emit change** (the #1111/#1112 offset-alias generalization beyond polygon/ps2). +2 (→ 76) needs both cold-matches.
- **P5 (hhfair + CGE cluster) delivers 0 genuine floor** — documented Case-c (the ν_objective reduction control-refuted, the sign flip BANNED 4×); it is a methodology closure, **not** a floor contributor. This is the Sprint-31-retro §3 lesson applied: do not count P5 toward the ramp.
- **P1 REPLAN:** −1 conditional genuine floor (mine's cold-match) — but mine's floor +1 was already conditional on cold-matching, not just solving.
- **P3 REPLAN (step 2):** −1 conditional genuine floor (camcge's cold-match); step 1's cleaner emit does not by itself add a floor match.
- **As-measured Match ≥ 92** holds under any single REPLAN (the floor is the Sprint-31 92; mine/camcge recoveries and rocket [P4] are the only as-measured +Match movers, all conditional).

**Translate ≥ 135 → +1 (136)** rests solely on **sarf [P2]**; a P2 REPLAN maintains 135 (no regression). It is the lowest-leverage KPI (moves neither Solve nor Match).

**Budget-reallocation order (feeds Task 10):** on any deep-track REPLAN, reallocate to (1) **P6** (the adjacent backlog — chiefly the #1111/#1112 offset-alias second-index-transpose generalization beyond polygon/ps2, the firmest remaining **emit-changing genuine-floor** lever, plus the `model_infeasible` cohort re-triage), (2) **P7** (property fixtures + genuine-floor tracking + checkpoint refresh — always lands, durable leverage), (3) the rocket [P4] forcing tail. The Task-10 schedule **lower bound assumes mine's + camcge's Solve +2 and the genuine-floor lift slip**; the upper bound assumes all three deep tracks ship. Every firm part lands regardless: the mine bound-multiplier design, the sarf O(active) sparsification design, camcge's step-1 general emit fix, and the P5 harness Case-c classifier.

---

## Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_32/REPLAN_RISK_ASSESSMENT.md && echo present
# Each deep track has a validation + a REPLAN exit + a reallocation target:
grep -cE "REPLAN exit|Budget reallocation|Single-model validation" docs/planning/EPIC_4/SPRINT_32/REPLAN_RISK_ASSESSMENT.md
# The three deepest tracks are covered:
grep -oE "Track P[123]" docs/planning/EPIC_4/SPRINT_32/REPLAN_RISK_ASSESSMENT.md | sort -u
# The honest KPI projection ties Solve/genuine-floor to specific tracks:
grep -qE "Solve.*≥ ?109|genuine floor.*≥ ?75" docs/planning/EPIC_4/SPRINT_32/REPLAN_RISK_ASSESSMENT.md && echo "KPI projection present"
```
