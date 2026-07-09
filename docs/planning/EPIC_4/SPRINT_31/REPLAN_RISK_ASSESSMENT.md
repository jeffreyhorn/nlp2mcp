# Sprint 31 — Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (PR16)

**Task:** Sprint 31 Prep Task 7
**Date:** 2026-07-09
**Owner:** Sprint planning
**Scope:** docs/analysis only — consumes the Task-3/4/5 designs + the Task-6 Phase-0 gates; no `src/` change.

---

## Executive summary

Sprint 31's carryforwards are the tracks Sprint 30 explicitly REPLAN'd *because* they proved to need foundational (P1 IR plumbing), general-alias-AD (P2 #1111/#1112), failed-architecture-rebuild (P4 #1385), or refuted-hypothesis-re-diagnosis (P5 obj-grad) work. This assessment applies the PR16 hypothesis-validation discipline to the **four deepest REPLAN-prone tracks (P1, P2, P4, P5)**: each gets a **single-model / control-experiment validation** (measurable by the Day-5 checkpoint), an **explicit Sprint-32 REPLAN exit**, and a **budget-reallocation target** if it stalls. (P3 camcge + P6 rocket are also REPLAN-prone but are gated by Task 6 + designed by Task 5 / the Sprint-30 forcing survey; they appear in the KPI projection.)

**The decisive mitigation (Sprint-30 §3 lesson):** each track now carries a **control-verified recipe or a precisely-pinned root cause** — polygon's 4-term fix warm-matches 0.780 (Task 4 re-confirmed on the current tree); the head offset is a favorable field-addition, not a normalize rewrite (Task 3); camcge's price-pin gives omega 191.735 and the dual-flaw is pinned (Task 5); hhfair's sign flip is *refuted* so the ν_objective reduction is the named target (Task 6 gate). Sprint 31 implements against specifications, not open questions — so REPLAN risk is **bounded**, and every REPLAN hands cleanly to a Sprint-32 filing rather than a dead end.

**The honest KPI projection (Sprint-30 §3 lesson 3, binding):** treat the genuine-floor ramp (→ ≥73) as **conditional** on the #1111/#1112 core [P2] + the dual-consistent CGE [P3] + the obj-grad reduction [P5], **NOT as independent +1s**. **Solve ≥109 (needs mine [P1] + camcge [P3]) is the most REPLAN-sensitive KPI.** (See the "Honest KPI projection" section below.)

---

## Track P1 — mine head-offset IR plumbing + shared 3-site helper (#1443)

**Bug class (pinned, Task 3):** the head offset is discarded at *parse* (`_domain_list_has_offset` → bool), not normalize; the fix is a **field addition** on `EquationDef` (`head_domain_offsets`) + copy-through at ~3 reconstructor sites — a favorable foundation. Phase 2 is the coordinated 3-site `comp_pr` head×parameter-offset index-map helper (the Sprint-30 Day-7 REPLAN cause).

**Single-model validation (PR16):**

| Step | Gate | Measurable by |
|---|---|---|
| V1 | The round-trip unit reproduction (`tests/fixtures/head_offset_ir_roundtrip.gms`) is **green** — `head_domain_offsets[1] == IndexOffset('l', Const(1.0), False)` — before any emit change | **Day 1** (Phase 1) |
| V2 | The shared 3-site helper drives the cold-INFES histogram → **all four k-directions (nw/ne/se/sw) → 0**, cold **MS-1**; **no 4th emit site** (`comp_lo_x`/`comp_up_x` bound-complementarity) surfaces | **Day-5 checkpoint** |

**REPLAN exit:** a **4th site** (bound-complementarity residual persisting after the `comp_pr` fix, or the Day-7 `ne`/`se`/`sw` cascade re-appearing) → a **Sprint-32 head-offset-Phase-3 workstream** (a deeper bound-complementarity architecture change). The IR plumbing + the shared helper **still land as reusable foundation** (they are correct regardless).

**Budget reallocation on REPLAN:** mine's remaining ~10–14h (of the 18–24h) → **P5** (the obj-grad reduction, the firmest remaining genuine-floor lever) + **P7** (the property-fixture catalog + genuine-floor tracking). mine's +1 Solve becomes conditional.

**Prior of REPLAN: Medium.** Lower than Sprint 30's "Medium-High" — the IR-plumbing blocker that forced the Day-6 REPLAN is now *designed away* (favorable field addition), so the residual risk is only the 4th-site question, which the Day-5 histogram resolves early.

---

## Track P2 — offset-alias general-alias core #1111/#1112 (polygon, #1143)

**Bug class (re-confirmed, Task 4):** the distance-Jacobian **second-index** cross-term is dropped in `_add_indexed_jacobian_terms` (`stationarity.py:5767`); the restoration is a new per-position complementary sum, coupled with the (reverted-but-verified) objective-successor half. The #1110 multi-pattern correction is orthogonal (single-scalar diagonal-vs-off-diagonal vs a whole position-keyed sum).

**Single-model validation (PR16):**

| Step | Gate | Measurable by |
|---|---|---|
| V1 | The 4-term recipe **re-confirmed** on the current tree (✅ done, Task 4 — CASE_B, `stat_theta(i12)` rel 0.492, CONSISTENT) | Day-0 (done) |
| V2 | The coupled fix (objective + distance second-index) **gates tightly to var-at-two-indices** — `shape8_offset_alias_successor` enabled + polygon warm-matches 0.780 + the **CGE multi-pattern GO list byte-stable** (`--resolve-changed`, no regression) | **Day-5 checkpoint** |

**REPLAN exit:** the var-at-two-indices gate **leaks** into the CGE multi-pattern cohort (a byte-golden regresses) → the full **#1111/#1112 alias-aware-differentiation AD-engine core = a Sprint-32 filing**. The banked 4-term recipe + the working objective half + the Task-4 second-index design make that filing a de-risked hand-off.

**Budget reallocation on REPLAN:** polygon's remaining ~8–14h (of the 14–20h) → **P5** + **P7**. **polygon's genuine-floor +1 becomes conditional** (it does not move the as-measured Match 92).

**Prior of REPLAN: Medium.** The recipe is control-verified and the #1110 orthogonality is confirmed, but the tight-gate-vs-general-core boundary is the exact risk Sprint 30 Day 8 hit (the objective half reverted because it can't ship alone).

---

## Track P4 — sarf symbolic runtime-guard cross-term emit (#1385)

**Bug class:** a dedicated builder-pipeline-aware symbolic-emit rebuild of the Sprint-26-Day-4-failed architecture (the `nu_slack("srn")` set-name-literal bug) — extend `_is_blowup_dynamic_subset_equation` from 1-D to sarf's 2-D dynamic-subset shape + a new parametric `stat_task` cross-term emit. **Fix surface pinned by Task 9.**

**Single-model validation (PR16):**

| Step | Gate | Measurable by |
|---|---|---|
| V1 | The symbolic re-emit is **O(constraints), not O(instances)** — `sarf_mcp.gms` translates **well under the >180s Option-1 timeout** (sarf has 1,152 Cartesian instances) | Day-0 timing probe (Task 9) |
| V2 | The re-emitted `stat_task` matches the **banked 6-guarded-term hand-derivation** with **no set-name-literal multiplier indices**; the re-emit + cross-terms land **atomically**; golden byte-stable | mid-sprint |

**REPLAN exit:** the parametric re-emit **re-triggers the translate timeout** (O(instances) after all) → **re-scope the parametric emit** (a documented re-scoping); +Translate deferred. sarf stays `translate_failure`.

**Budget reallocation on REPLAN:** sarf's remaining ~10–16h (of the 14–20h) → **P5** + **P7** (the +Translate stretch is the lowest-priority target — it does not move Solve/Match).

**Prior of REPLAN: Medium-High.** This is a *failed-architecture rebuild* — the Sprint-26 attempt failed on exactly the set-name-literal + combinatorial-blowup axes this gate guards. The O(constraints) tractability gate (V1) resolves the dominant risk early.

---

## Track P5 — cold-convex obj-grad residue (hhfair `stat_u` / CGE `stat_xp`, #1236)

**Bug class:** an objective-defining-intermediate-variable residue; the fix is the objective-gradient reduction **through the defining-equation multiplier (ν_objective)** — **NOT the sign flip**, which was control-refuted **three times** in Sprint 30 (hhfair 72.147 → 22.144, worse). **Fix surface pinned by Task 9.**

**Single-model validation (PR16 — control-experiment-before-implement):**

| Step | Gate | Measurable by |
|---|---|---|
| V1 | The **ν_objective reduction reaches the NLP optimum on hhfair** (the cleanest instance, `stat_u` rel 2.0) in a `/tmp` control experiment **before** the objective-gradient `src/` change. **The sign flip is BANNED.** | **Day-0 control experiment** (Task 9) |
| V2 | The same reduction converts the CGE cluster (irscge/lrgcge/moncge `stat_xp` rel ~0.06 after the Day-5 case-normalization fix) to **Case-a** (residual → 0) | mid-sprint |

**REPLAN exit:** the ν_objective reduction does **not** reach the NLP optimum on hhfair → hhfair is **genuine Case-c non-convexity** → a **documented non-convexity finding** for the objective-defining-intermediate-variable family; **no `src/` change** (the control experiment prevents a bad ship — exactly what killed the sign flip 3× in Sprint 30).

**Budget reallocation on REPLAN:** P5's remaining ~6–12h (of the 10–16h) → **P7** (property fixtures + genuine-floor tracking) + the +Translate/forcing tails. hhfair's +1 Match and the CGE-cluster genuine-floor gains are lost.

**Prior of REPLAN: Medium.** The sign flip is refuted (the wrong path is closed), and the ν_objective reduction is the named correct-treatment hypothesis — but it is not yet control-verified (unlike polygon's 4-term recipe), so hhfair could still prove genuinely Case-c. The V1 control experiment resolves this Day-0.

---

## Budget-at-Risk tally (feeds Task 10's schedule lower bound + fallback ordering)

| Track | Priority | Budget at risk | At-risk condition | Firm part (lands regardless) | Prior of REPLAN |
|---|---|---|---|---|---|
| **P1 mine (#1443)** | 1 [18–24h] | ~10–14h (mine's +1 Solve) | a 4th bound-complementarity site / the Day-7 cascade persists | **the IR plumbing + the shared 3-site helper** (reusable foundation) | **Medium** — the IR blocker is designed away; only the 4th-site question remains |
| **P2 polygon (#1143)** | 2 [14–20h] | ~8–14h (polygon's genuine-floor +1) | the var-at-two-indices gate leaks into the CGE multi-pattern cohort | **the second-index design + the working objective half** (the Sprint-32 #1111/#1112 filing) | **Medium** — recipe control-verified; the tight-gate boundary is the risk |
| **P4 sarf (#1385)** | 4 [14–20h] | ~10–16h (the +Translate stretch) | the parametric re-emit re-triggers the timeout (O(instances)) | **the re-scoping finding** (a documented builder-pipeline constraint) | **Medium-High** — a failed-architecture rebuild; V1 O(constraints) gate resolves it early |
| **P5 hhfair/CGE (#1236)** | 5 [10–16h] | ~6–12h (hhfair +1 Match + CGE genuine floor) | the ν_objective reduction is genuine Case-c (non-convex) | **the documented non-convexity finding** (closes the family) | **Medium** — sign flip refuted; reduction not yet control-verified |
| **Combined** | 1,2,4,5 | Solve ≥109 (P1) + genuine floor ≥73 (P2+P5) | — | all IR/design/finding artifacts land; each REPLAN → a Sprint-32 filing | **Task 10 lower bound: assume P1's +1 Solve + the P2/P5 genuine-floor lift may slip; every firm part lands** |

---

## Honest KPI projection (which KPI survives each single-track REPLAN)

**Solve 107 → ≥ 109** rests on **mine [P1] + camcge [P3]** (rocket [P6] is a conditional third → the Sprint-32 PATH-consultation input on the evidence). This is the **most REPLAN-sensitive KPI**:

- **P1 REPLAN (4th site):** Solve ≥109 misses by 1 (camcge alone → 108) unless rocket [P6] converts. mine's +1 becomes a Sprint-32 carry.
- **P3 REPLAN (per-model-numéraire fallback):** camcge still lands via the fallback (declaration), so Solve holds — **P3 is the more robust of the two Solve movers** (it has a fallback that still solves; P1 does not).
- **Both P1 + P3 firm ⇒ Solve 109.** This is the target line, and it is exactly the "needs both" fragility the Sprint-30 retro warned about.

**Match maintain ≥ 92 / genuine floor 70 → ≥ 73** is **conditional, not independent +1s** (Sprint-30 §3 lesson 3):

- The genuine-floor +3 needs **polygon [P2] +1 + hhfair [P5] +1 + the CGE cluster [P5] +1–3** (mine [P1] contributes a conditional +1 if it also cold-matches). himmel16 is **not** a contributor (non-convex).
- **P2 REPLAN (gate leaks):** −1 genuine floor (polygon), and the #1111/#1112 core defers to Sprint 32.
- **P5 REPLAN (Case-c):** −1 to −4 genuine floor (hhfair + the CGE cluster) — the **largest single-track genuine-floor exposure**.
- **As-measured Match ≥92** holds under any single REPLAN (the floor is the Sprint-30 92; hhfair [P5] mismatch→match + rocket [P6] are the only as-measured +Match movers, both conditional).

**Budget-reallocation order (feeds Task 10):** on any deep-track REPLAN, reallocate to (1) **P5** (the firmest remaining genuine-floor lever, if not itself REPLAN'd), (2) **P7** (property fixtures + genuine-floor tracking — always lands, durable leverage), (3) the +Translate [P4] / forcing [P6] tails. The Task-10 schedule **lower bound assumes P1's +1 Solve + the P2/P5 genuine-floor lift slip**; the upper bound assumes all four deep tracks ship.

---

## Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_31/REPLAN_RISK_ASSESSMENT.md && echo present
# Each deep track has a validation + a REPLAN exit + a reallocation target:
grep -cE "REPLAN exit:|Budget reallocation|Single-model validation" docs/planning/EPIC_4/SPRINT_31/REPLAN_RISK_ASSESSMENT.md
# The four deepest tracks are covered:
grep -oE "Track P[1245]" docs/planning/EPIC_4/SPRINT_31/REPLAN_RISK_ASSESSMENT.md | sort -u
# The honest KPI projection ties Solve/genuine-floor to specific tracks:
grep -qE "Solve.*≥ ?109|genuine floor.*≥ ?73" docs/planning/EPIC_4/SPRINT_31/REPLAN_RISK_ASSESSMENT.md && echo "KPI projection present"
```
