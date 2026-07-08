# Sprint 30 — Retrospective

**Sprint:** 30 (Head-Domain-Offset Emit Architecture, Non-Convex Forcing & Offset-Alias AD — Sprint 29 carryforwards)
**Closed:** 2026-07-08 (Day 13)
**Final metrics (142 corpus):** Parse 142 · Translate 135 · **Solve 107** · **Match 92** (genuine floor **70**) · model_infeasible 7 · determinism ✅ ×3 {0,1,42} · Tests 4997 green.

---

## 1. Outcome vs targets

| KPI | Day-0 | Target | Final | Met? |
|---|---|---|---|---|
| Solve | 107 | ≥109 | 107 | ❌ (both +1s — mine, rocket — REPLAN'd) |
| Match | 92 | ≥92 | 92 | ✅ |
| genuine floor | 69 | ≥72 | 70 | ❌ (+1 robert; rest REPLAN'd/refuted) |
| model_infeasible | 7 | ≤5 | 7 | ❌ (−2 was mine+rocket) |
| Determinism / Tests | — | ✅ | ✅ / 4997 | ✅ |

**The Match ≥92 floor held; the Solve ≥109 and genuine-floor ≥72 stretches missed — exactly along the REPLAN-risk lines the Task-6 assessment drew.** Solve ≥109 required *both* mine and rocket, both rated High-risk / REPLAN-prone up front; both REPLAN'd. The genuine-floor lift was the "robust" deliverable on paper, but three of its four contributors (polygon P5, hhfair/Class-B obj-grad P7) hit a REPLAN boundary or a control-refutation, leaving robert as the sole +1.

## 2. What landed (firm)

- **robert (P1a)** — objective-gradient boundary-term fix; cold-matches 11025.0. +1 genuine floor. The one clean, decoupled, low-risk win — and it was correctly split out from mine early (the Task-3 "robert does NOT generalize to mine" inversion).
- **hhfair `$184` (P3)** — the #1449 widened-VARIABLE companion-variable emit architecture; general robustness (any widened variable under presolve). Unblocked hhfair's compile.
- **Class-B `stat_pz` (P7)** — the presolve dual-transfer **case-normalization** fix. General emit robustness: mixed-case equation duals were silently skipped in the warm-start for *every* model, not just the CGE cluster.
- **P8 infrastructure** — the `--force` solution-forcing scaffold (Sprint-31 PATH-consultation entry point), the PR25 KPI re-baseline, the AD cross-term property catalog.

## 3. What we'd do differently / key lessons

1. **PR24 discipline paid for itself repeatedly — banked fix-surfaces are hypotheses, and control experiments beat harness residuals.** Five banked diagnoses were *refuted* before any high-blast-radius `src/` change: the objective-gradient sign fix (hhfair `stat_u`, irscge `stat_xp`, himmel16 `stat_area` — all three control-inert or worse), the Class-B `stat_pz` "coefficient bug" (the real bug was case-normalization), and the camcge Walras drop-row (primal-correct but breaks the MCP dual). **Recommendation for Sprint 31: keep the control-experiment-before-implement gate; the single-point harness residual is systematically misleading for non-convex / objective-defining-intermediate-variable shapes.**

2. **"Solution-preserving on paper" ≠ "correct in the MCP" — always check the dual side.** The camcge Walras transform was paper-verified for the *primal* but orphans a needed price/wage multiplier in the stationarity (the dual side the paper analysis omitted). Any structural transform that drops/adds rows must be verified against the KKT dual, not just the primal solution set.

3. **REPLAN-prone estimates were accurate — the Task-6 risk assessment predicted the outcome.** mine (High), rocket (High), camcge (Medium) all REPLAN'd; polygon surfaced a *new* REPLAN boundary (the #1111/#1112 general-alias core). The honest projection ("Solve ≥109 is the most REPLAN-sensitive KPI; the genuine-floor lift is robust") was half-right: the Solve miss was expected, but the genuine-floor lift proved *less* robust than projected because two of its contributors were entangled with non-convexity / general-alias-differentiation. **Sprint-31 planning should treat the genuine-floor ramp (→≥73/75/78) as conditional on the #1111/#1112 core + the dual-consistent CGE work, not as independent +1s.**

4. **Control experiments turn "REPLAN with a shrug" into "REPLAN with a recipe."** Every deferred track carries a *de-risked* hand-off: polygon has a control-verified 4-term fix + a working objective-half implementation; camcge has the price-pin recipe (omega 191.735) + the pinned dual-flaw; sarf has the banked `stat_task` derivation; mine has the cold-INFES characterization. Sprint 31 inherits specifications, not open questions.

5. **A 14-day sprint (Day 0 + Days 1–13) with 5 REPLANs still shipped 3 firm general-robustness fixes + the infra.** The REPLANs were not wasted days — each produced a precise diagnosis that advances the Sprint-31 work. But the sprint would have benefited from **front-loading the tractability probes** (e.g. the mine IR-plumbing blocker and the polygon #1111/#1112 boundary were discoverable Day-0 with a deeper structural read, which would have re-allocated the Days 6–8 budget toward the firm floor gains earlier).

## 4. Sprint-31 carryforwards

See the SPRINT_LOG Day-13 "Sprint-31 carryforwards (filed)" table: **mine** (IR head-offset plumbing → shared 3-site helper), **rocket** (PATH consultation), **polygon+himmel16** (#1111/#1112 general-alias core), **sarf** (symbolic-emit workstream), **camcge** (dual-consistent Walras), and the **cold-convex obj-grad residue** (hhfair `stat_u` / CGE `stat_xp` — the objective-defining-intermediate-variable family). Each has a banked recipe/diagnosis in its ISSUE doc.

---

**SPRINT 30 CLOSED.**
