# Sprint 30 Known Unknowns

**Created:** 2026-07-04
**Status:** Active — Pre-Sprint 30
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 30 (Sprint 29 carryforwards — head-domain-offset emit architecture, non-convex convergence forcing, offset-alias AD, camcge → Epic 5 Walras transformation) before implementation begins

---

## Overview

This document identifies all assumptions and unknowns for the Sprint 30 implementation tracks **before** any `src/` change. It continues the Known-Unknowns methodology that has run since Epic 1 Sprint 4, sharpened by the Sprint 27 PR24 rule (prep records the *symptom + reproducer*; the fix surface is a Day-0-trace hypothesis, never trusted from the prep doc) and the Sprint 28 PR27 rule (the KKT-residual harness Case-(a/b/c) verdict is the standard verification instrument).

Sprint 30 is **implementation-bound, not diagnosis-bound** — the inverse of Sprint 29. Every core carryforward was *diagnosed* in Sprint 29 and then REPLAN'd precisely because the diagnosis proved the fix multi-site, intrinsic, or domain-specific. So the Sprint 30 unknowns are less "what is the bug?" and more "does the banked diagnosis convert to an in-budget fix, and does the minimal reproduction generalize?" — but PR24 still holds: the banked fix surface is a Day-0-trace hypothesis, not fact (Sprint 29 proved the Day-0 `$141` attribution wrong for hhfair — the real blocker was `$184`).

**Sprint 30 Scope** (`docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 30 (Weeks 25–26)"):
1. **Head-domain-offset emit architecture** (#1443 mine + robert) — the coordinated `comp_pr` / dual-transfer / `stat_x` index-map re-derivation; robert (pure constant offset) is the minimal reproduction, mine (`l+1 × li(k)/lj(k)`) the full case (+1 Solve mine, genuine-floor robert)
2. **rocket #1462** — non-convex convergence forcing (trust-region / homotopy / multi-start); the `_fx_` warm-start already landed Sprint 29 (+1 Solve / +1 Match)
3. **hhfair #1236** — widened-VARIABLE presolve fix (the `$184` #1449 conflict for a live nonlinear-stationarity variable) (+Match)
4. **#1385** — symbolic runtime-guard cross-term emit (sarf); cross-terms already hand-derived + banked Sprint 29 (+Translate)
5. **Offset-alias cross-terms** (#1146/#1143/#1112/#1111) — polygon + himmel16; the Sprint-29 Day-5 revert coupling (+Match)
6. **camcge #1330 → Epic 5** — Walras drop-row + fix-numéraire transformation; paper-verified Sprint 29 (Epic 5 hand-off + potential +Solve)
7. **Class-B CGE `stat_pz`** — general-emit coefficient discrepancy (confirmed NOT Walras, Sprint 29 Day 12) + the cold-convex Case-c residue disposition (+Match / documentation)
8. **Infrastructure** — property-test catalog extension (head-offset + offset-alias shapes) + the genuine-floor re-baseline + the solution-forcing harness scaffold

**Reference:** `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 30" (Priorities 1–8 + Acceptance Criteria + Estimated Effort 92–142h + Risk HIGH); prep tasks: `docs/planning/EPIC_4/SPRINT_30/PREP_PLAN.md`. (No separate `PRELIMINARY_PLAN.md` exists for Sprint 30 — the PROJECT_PLAN §"Sprint 30" entry + this PREP_PLAN are the planning source.)

**Lessons from Sprint 29** (`docs/planning/EPIC_4/SPRINT_29/SPRINT_RETROSPECTIVE.md`):
- §"Sprint-30 carryforwards" — the six REPLAN'd tracks below carry a *banked* Sprint-29 diagnosis (the SPRINT_LOG per-day entries), so Sprint 30 implements rather than re-diagnoses; but each banked surface is re-framed here as a Day-0 hypothesis (PR24).
- **The hhfair `$141` → `$184` correction** — the Sprint-29 Day-0 fix-surface attribution (`$141`) was wrong; the real blocker surfaced Day 8 (`$184` widened-VARIABLE). → Every Category-3 unknown treats the fix surface as unverified until the Day-0 trace, and the tooling-readiness audit (Task 8) trusts the harness's *actual* output, not the assumed one.
- **The genuine-floor / methodology split** — the Sprint-29 headline Match (92) sits above a genuine floor of 69 (the +23 is the Sprint-28 methodology lift). → Category 8's re-baseline unknown keeps the genuine floor 69 → ≥ 72 target measurable.
- **REPLAN discipline (PR16)** — Sprint 29 REPLAN'd mine (Days 6–7), rocket (Day 2), and camcge (Day 11) with explicit exits; Sprint 30's three deep tracks (P1 multi-site, P2 forcing, P6 Epic-5) carry the same PROCEED/REPLAN framing (Category 1/2/6 Criticals → Task 6).

**Deferred unknowns carried from Sprint 29:** all 28 Sprint 29 prep unknowns were VERIFIED (`docs/planning/EPIC_4/SPRINT_29/KNOWN_UNKNOWNS.md` §"Next Steps"). Three Sprint-29 unknowns **INVERTED** and became the direct parents of Sprint-30 categories: **Unknown 1.1** (mine is distributed multi-site, not single-site → the Sprint-30 head-offset architecture, Category 1), **Unknown 2.2** (rocket is intrinsic non-convergence, not a `_fx_` Case-b → the Sprint-30 forcing survey, Category 2), and **Unknown 5.1** (the CGE cohort has *distinct* degeneracies → camcge is the sole inherent Walras case, Category 6; the Class-B `stat_pz` cluster is a *separate* general-emit bug, Category 7). The Sprint 30 unknowns are net-new, derived from the six carryforwards + the two backlog priorities + the infrastructure track.

---

## How to Use This Document

### Before Sprint 30 Day 1
1. Research and verify all **Critical** and **High** priority unknowns during prep Tasks 2–10 (see §"Appendix: Task-to-Unknown Mapping").
2. Create minimal test cases / run the `kkt_residual.py` trace for validation.
3. Document findings in each "Verification Results" section.
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED (with evidence) or ❌ WRONG (with correction and new assumption).

### During Sprint 30
1. Review daily during standup — especially unknowns marked 🔍 INCOMPLETE.
2. Add newly discovered unknowns (template below).
3. Update with implementation findings.
4. Move resolved items to "Confirmed Knowledge" post-sprint.

### Priority Definitions
- **Critical:** Wrong assumption derails a priority or forces a mid-sprint REPLAN (>8 hours of churn / a lost target).
- **High:** Wrong assumption causes significant rework (4–8 hours) or a scope reduction.
- **Medium:** Wrong assumption causes minor issues (2–4 hours).
- **Low:** Wrong assumption has minimal impact (<2 hours).

---

## Summary Statistics

**Total Unknowns:** 25

**By Priority:**
- Critical: 6 (the REPLAN-prone deep tracks + the robert→mine generalization + the camcge detection-heuristic false-positive risk)
- High: 10 (unknowns requiring upfront research before their priority's Day-0 trace)
- Medium: 7 (resolvable during the relevant prep task)
- Low: 2 (nice-to-know / low impact)

**By Category:**
- Category 1 (head-domain-offset emit architecture — #1443 mine + robert): 4 unknowns
- Category 2 (rocket #1462 — non-convex convergence forcing): 3 unknowns
- Category 3 (hhfair #1236 — widened-VARIABLE presolve fix): 3 unknowns
- Category 4 (#1385 — symbolic runtime-guard cross-term emit): 2 unknowns
- Category 5 (offset-alias cross-terms #1111/#1112): 3 unknowns
- Category 6 (camcge #1330 → Epic 5 Walras transformation): 3 unknowns
- Category 7 (Class-B CGE `stat_pz` + cold-convex residue): 3 unknowns
- Category 8 (property-test catalog + re-baseline + forcing scaffold): 4 unknowns

**Estimated Research Time:** 28–36 hours (the per-unknown estimates below sum to ~36h, but many unknowns are verified in parallel within a single prep task — see §"Appendix: Task-to-Unknown Mapping". The authoritative scheduling budget is the per-task total in `docs/planning/EPIC_4/SPRINT_30/PREP_PLAN.md`: 34–48h across Tasks 1–10.)

---

## Table of Contents

1. [Category 1: Head-Domain-Offset Emit Architecture (#1443 mine + robert)](#category-1-head-domain-offset-emit-architecture-1443-mine--robert)
2. [Category 2: rocket #1462 — Non-Convex Convergence Forcing](#category-2-rocket-1462--non-convex-convergence-forcing)
3. [Category 3: hhfair #1236 — Widened-VARIABLE Presolve Fix](#category-3-hhfair-1236--widened-variable-presolve-fix)
4. [Category 4: #1385 — Symbolic Runtime-Guard Cross-Term Emit](#category-4-1385--symbolic-runtime-guard-cross-term-emit)
5. [Category 5: Offset-Alias Cross-Terms #1111/#1112 (polygon + himmel16)](#category-5-offset-alias-cross-terms-11111112-polygon--himmel16)
6. [Category 6: camcge #1330 → Epic 5 Walras Transformation](#category-6-camcge-1330--epic-5-walras-transformation)
7. [Category 7: Class-B CGE `stat_pz` Coefficient Discrepancy + Cold-Convex Residue](#category-7-class-b-cge-stat_pz-coefficient-discrepancy--cold-convex-residue)
8. [Category 8: Property-Test Catalog Extension + Re-Baseline + Forcing Scaffold](#category-8-property-test-catalog-extension--re-baseline--forcing-scaffold)
9. [Template for New Unknowns](#template-for-new-unknowns)
10. [Next Steps](#next-steps)
11. [Appendix: Task-to-Unknown Mapping](#appendix-task-to-unknown-mapping)

---

# Category 1: Head-Domain-Offset Emit Architecture (#1443 mine + robert)

## Unknown 1.1: Does a correct robert (constant-offset) head-offset fix generalize to mine (parameter-offset)?

### Priority
**Critical** — robert is the P1 minimal reproduction; if a correct robert fix does NOT generalize to mine, P1 is not "one fix, two models" but a robert-then-separate-mine multi-site slip, and the mine +1 Solve is at risk.

### Assumption
robert's head-domain-offset bug (`sb(r,tt+1)` with a *pure constant* `+1` offset — the `x(p,tt)` cross-term must be `sum(r, a(r,p)*nu_sb(r,tt+1))` but the emit produces `nu_sb(r,tt)`) is the **same class** as mine's, only simpler: mine adds the `li(k)`/`lj(k)` *parameter* offsets on top of the `l+1` head offset. So a head-offset cross-term + dual-transfer index map that fixes robert **generalizes** to mine by composing the parameter offset into the constant-offset design (the `sum(k, lam_pr(k,l,i-li(k),j-lj(k)) - lam_pr(k,l-1,i,j))` shape the landed `stat_x` already uses).

### Research Questions
1. Is robert's head-offset structurally the constant-offset special case of mine's `l+1 × li(k)/lj(k)` coupling (no parameter offset)?
2. Does a shared code path handle both (constant offset = parameter offset with `li=lj=0`), or does mine require a distinct parameter-offset branch?
3. Sprint 29 Day 7 found hand-fixing mine's dual transfer cleared only the `nw` direction (`li=lj=0`) and left `ne/se/sw` at ~1e10 — is that the *parameter-offset composition* gap the robert design closes, or a separate `comp_pr` re-derivation?
4. Does robert reach MODEL STATUS 1 with the designed fix (confirming robert is a faithful minimal reproduction), and if so does the same emit logic drive mine's cold LCP to MS 1?

### How to Verify
Hand-derive robert's head-offset cross-term + dual-transfer index map; confirm the eliminated-KKT residual → 0 at robert's NLP optimum; then show mine's `li(k)`/`lj(k)` case is the constant-offset design with the parameter offset composed in:
```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/robert.gms
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/mine.gms
# Expect: robert design generalizes → one shared head-offset code path → P1 = one fix, two models
#         does NOT generalize → mine is a separate multi-site fix → re-size P1, robert still lands
```

### Risk if Wrong
- **Does not generalize:** P1 splits — robert (genuine-floor) lands, mine (+1 Solve) REPLANs to a Sprint-31 head-offset-architecture workstream; -1 Solve vs the Sprint-30 target. The robert-minimal-reproduction de-risking evaporates for mine.
- **Mis-scoped as generalizing when it is not:** the schedule under-budgets mine and discovers the split mid-sprint (the exact churn PR16 prevents).

### Estimated Research Time
2.5 hours (Task 3 — hand-derivation of robert + the robert→mine generalization argument on paper)

### Owner
Development team (AD/KKT specialist)

### Verification Results
❌ **Status:** WRONG — does NOT generalize (different bug classes); favourable re-scope
**Verified by:** Task 3 (Head-Offset Architecture Design + robert Minimal Reproduction)
**Date:** 2026-07-05
**Findings:** The banked premise (robert = pure-constant-offset minimal reproduction of mine; one head-offset fix converts both) is **refuted**. Cold-solve control experiments on `robert_mcp.gms`: patching **only** `stat_x` to `nu_sb(r,tt+1)` (the banked "fix") leaves robert at the spurious **6741.67**; patching **only** `stat_s`'s objective gradient (drop-in `−res-value(r)` boundary term at `tt=4`, guard `storage-c(r)` to `t(tt)`) makes robert cold-solve to **11025.0 = NLP optimum (MATCH)**. So robert's real bug is an **objective-gradient boundary-term drop** (same class as Sprint-29 #1447 maxmin), NOT the head-offset cross-term — and it is a **different class** from mine's firm `comp_pr` `l+1`-head × `li(k)`/`lj(k)`-parameter-offset coupling (`ISSUE_1443` Day-7). robert's `stat_x` cross-term `nu_sb(r,tt)` is already correct under the emit's base-labeling.
**Evidence:** `docs/planning/EPIC_4/SPRINT_30/HEAD_OFFSET_ARCHITECTURE_DESIGN.md` §0–§2 + §Appendix (the two cold-solve control experiments).
**Decision:** **Priority 1 splits into two independent tracks** — robert (genuine-floor +1, LOW-risk standalone objective-gradient fix, ~2–4 h, decoupled) and mine (+1 Solve, HIGH-risk multi-site `comp_pr` re-derivation, ~10–16 h, REPLAN-prone). Removing the false coupling de-risks the robert gain and isolates mine. Fed to Task 5 (gate refresh: record robert as objective-gradient, head-offset architecture as mine-only) + Task 6 (REPLAN mine only) + Task 10 (schedule robert early + standalone).

**Task 6 (2026-07-06) — risk/decision layer:** **robert = firm PROCEED** (genuine-floor +1, no REPLAN branch — convex LP, cold-confirmed 11025). **mine = PROCEED-conditional, prior of REPLAN Medium-High** — PROCEED the coordinated 3-site `comp_pr` fix if the cold-INFES stays dominated by `comp_pr`/`pr` (no 4th bound-row site) and the shared index-map drives the cold LCP to MS 1 within the ~10–16 h estimate / ~14–20 h P1 ceiling; **REPLAN mine (not robert)** to a Sprint-31 head-offset-architecture workstream if a 4th site surfaces or the Day-7 `ne`/`se`/`sw` cascade persists. **Reallocation on mine REPLAN:** freed ~10–16 h → genuine-floor Class-B CGE `stat_pz` (P7) + offset-alias himmel16/polygon (P5). robert lands regardless. See `REPLAN_RISK_ASSESSMENT.md` Track A.

---

## Unknown 1.2: Is the coordinated 3-site index-map re-derivation an ≤ 14–20h fix, or does each fixed site expose the next?

### Priority
**Critical** — sizes the P1 budget; a "each fixed site exposes the next" outcome is a deeper architectural slip (→ Sprint-31 REPLAN).

### Assumption
mine's fix is a **coordinated re-derivation across exactly three emit sites** — (1) `comp_pr` emission, (2) the `--nlp-presolve` dual transfer (`src/emit/emit_gams.py` `_emit_nlp_presolve`), and (3) the (landed) `stat_x` cross-term — that lands together within the 14–20h P1 budget, not an open-ended cascade where each corrected site reveals a new mis-alignment.

### Research Questions
1. Are the three sites the *complete* set, or does the cold LCP surface a fourth (a bound-complementarity `comp_lo_x`/`comp_up_x` coupling)?
2. Can the three sites share one head-offset index-map helper, or does each need bespoke logic?
3. Sprint 29 Day 7 hand-fixed Site 2 (dual transfer) and evaluated at the NLP optimum — did that isolate Sites 1+3 as the remaining work, or expose new coupling?
4. What is the realistic hour estimate for the coordinated 3-site change + its blast-radius regen?

### How to Verify
Trace the three emit sites; prototype the Site-2 fix (env-guarded, zero `src/`) and evaluate mine at `iterlim=0` from the NLP optimum; measure which INFES rows remain:
```bash
# Which sites remain after the Site-2 dual-transfer prototype (the Sprint-29 Day-7 experiment)?
grep -n "_emit_nlp_presolve\|comp_pr\|stat_x" src/emit/emit_gams.py src/kkt/stationarity.py | head
```

### Risk if Wrong
- **Cascade (each site exposes the next):** P1 overruns → REPLAN mine to Sprint 31; the freed budget re-allocates to the Class-B CGE / offset-alias genuine-floor work (Task 6 reallocation).

### Estimated Research Time
2.5 hours (Task 3 — the 3-site trace + the Site-2 prototype re-run from the Sprint-29 Day-7 experiment)

### Owner
Development team (AD/KKT specialist)

### Verification Results
✅ **Status:** VERIFIED — mine-only (robert is not a 3-site problem)
**Verified by:** Task 3 (Head-Offset Architecture Design)
**Date:** 2026-07-05
**Findings:** The 3-site coordination (`comp_pr` / `_emit_nlp_presolve` / `stat_x`) applies **only to mine** — robert needs no site coordination (its bug is a single objective-gradient site; cold-confirmed at 11025 with the `stat_s` fix alone, Unknown 1.1). For mine the 3-site budget stands as the firm `ISSUE_1443` Day-7 finding: fixing Site 2 alone (dual transfer → `pr.m(k,l+1,i,j)`) clears only the `nw` direction (`li=lj=0`), leaving `ne`/`se`/`sw` at ~1e10 `comp_pr` infeasibility — so each site can expose the next (the head-offset × parameter-offset coupling is the un-budgeted risk). Design recommends a single shared head-offset index-map helper all three sites call.
**Evidence:** `HEAD_OFFSET_ARCHITECTURE_DESIGN.md` §3 (three-site table with `file:line`); `ISSUE_1443` Day-7.
**Decision:** mine ~10–16 h with a REPLAN-if-cascade exit (Task 6); robert is NOT counted in the 3-site budget (separate ~2–4 h objective-gradient fix).

**Task 6 (2026-07-06) — risk/decision layer:** the 3-site coordination is the mine REPLAN pivot. **PROCEED** if the shared head-offset index-map helper (all three sites) drives the cold LCP to MS 1 atomically within budget; **REPLAN mine to Sprint 31** if A2's cold-INFES histogram shows a 4th site (`comp_lo_x`/`comp_up_x`/bound coupling) or A3 shows each fixed site exposes the next (the Day-7 signature). Sprint-31 exit = "the head-domain-offset emit architecture as one workstream (a single δ + `li(k)`/`lj(k)` index-map helper with cold-LCP consistency)." Prior of REPLAN Medium-High. See `REPLAN_RISK_ASSESSMENT.md` Track A (steps A2/A3).

**Task 5 (2026-07-05):** the #1443 gate was refreshed to this disposition (mine-only 3-site `comp_pr` re-derivation; PROCEED, REPLAN-if-cascade).

---

## Unknown 1.3: Does the head-offset fix alone leave the cold LCP feasible (mine's `x → 4e10` resolved)?

### Priority
**High** — a residual bound-complementarity coupling after the head-offset fix would mean mine needs a *second* fix (bounds), extending P1.

### Assumption
mine's cold failure (MS 5, `x → 4e10` despite `x.up=1`, 49 INFES) is driven *entirely* by the head-offset mis-alignment in `comp_pr`, so a correct head-offset emit drives the cold LCP to MS 1 with no residual bound-complementarity coupling — mine is a convex LP (a monotone LCP), so a correct emit MUST cold-solve (no warm-start escape, Sprint 29 Unknown 1.3).

### Research Questions
1. After the head-offset fix, do the `comp_lo_x`/`comp_up_x` bound-complementarity rows clear, or does a residual remain?
2. Is the `x → 4e10` blowup purely the `comp_pr` LCP residual (Sprint 29 Day 6 finding), fully resolved by the head-offset fix?
3. Does mine reach MS 1 *cold* (not just warm-started from the NLP optimum), confirming the convex-LP expectation?

### How to Verify
After the Task-3 head-offset design, evaluate mine's corrected cold emit and confirm the LCP residual → 0 and MS 1:
```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/mine.gms
# Expect: residual → 0 at the head-offset fix, cold MS 1 (convex LP, no warm-start needed)
```

### Risk if Wrong
- **Residual bound coupling:** P1 needs a second (bounds) fix → +2–4h; if the coupling is deep, mine REPLANs with robert still landing.

### Estimated Research Time
2 hours (Task 3 — the cold-LCP-consistency check after the head-offset design)

### Owner
Development team (AD/KKT specialist)

### Verification Results
✅ **Status:** VERIFIED — robert cold-LCP feasible after the objective-gradient fix; mine hypothesis firm
**Verified by:** Task 3 (Head-Offset Architecture Design)
**Date:** 2026-07-05
**Findings:** **robert ✅ CONFIRMED** — after the `stat_s` objective-gradient fix, robert's cold MCP solves to MS 1 at 11025.0, a clean convex-LP cold solve with **no warm-start** and no residual bound coupling. **mine (hypothesis, firm):** the head-offset `comp_pr` fix must drive the `comp_pr` LCP residual (the `x → 4e10`) to 0; mine is a convex LP (monotone LCP) so there is no Case-c escape — a residual after the 3-site fix is a remaining emit/index-map bug (still Case-b), not non-convexity.
**Evidence:** `HEAD_OFFSET_ARCHITECTURE_DESIGN.md` §1.4 (robert cold 11025) + §4; `ISSUE_1443` (mine convex-LP / `x → 4e10` = comp_pr LCP residual).
**Decision:** robert's cold LCP is fully consistent once the objective gradient is fixed (no bound-coupling second fix). mine's cold-LCP consistency is the PROCEED criterion for the 3-site fix (Task 6).

**Task 5 (2026-07-05):** the #1443 gate records the cold-LCP-consistency criterion (convex LP, no Case-c; the `comp_pr` fix must clear `x → 4e10`).

---

## Unknown 1.4: Is robert's `nu_sb(r,tt+1)` the correct dual-transfer cross-term, with the harness residual → 0 at the NLP optimum?

### Priority
**High** — robert is the minimal reproduction that anchors the whole P1 design; if the hand-derived cross-term is wrong, the design starts from a false premise.

### Assumption
robert's `x(p,tt)` stationarity cross-term is `sum(r, a(r,p)*nu_sb(r,tt+1))` (the head offset inverts the multiplier index to `tt+1`), and the `--nlp-presolve` dual transfer must read `sb.m` at the `tt+1` head-offset position; at robert's NLP optimum the eliminated-KKT residual → 0 with this cross-term, confirming it is correct.

### Research Questions
1. Does the eliminated-KKT residual → 0 at robert's NLP optimum with the `nu_sb(r,tt+1)` cross-term (emit correct) vs ≠ 0 (cross-term wrong)?
2. Does `kkt_residual.py`'s dual-transfer self-check report CONSISTENT for robert's `nu_sb` head-offset multiplier?
3. Is robert's Day-0 bucket `model_optimal_presolve`-match (genuine-floor candidate), confirming a correct cold emit converts a warm-only match to a genuine cold match (+genuine floor)?

### How to Verify
```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/robert.gms
# Expect: the current emit localizes to a CASE_B stat_x residual (the nu_sb(r,tt) bug);
#         substituting the hand-derived nu_sb(r,tt+1) drives the residual → 0 (CASE_A, emit
#         correct) at the NLP optimum; dual transfer CONSISTENT
```

### Risk if Wrong
- **Cross-term wrong:** the P1 design is built on a false minimal reproduction → the whole track's hand-derivation is invalid; re-derive before any `src/` change (PR24 catches this at the gate).

### Estimated Research Time
2.5 hours (Task 3 — robert hand-derivation + harness residual check; Task 8 confirms the harness handles the `nu_sb` head-offset multiplier)

### Owner
Development team (AD/KKT specialist)

### Verification Results
❌ **Status:** WRONG — `nu_sb(r,tt+1)` is NOT robert's fix; the emitted `nu_sb(r,tt)` is already correct
**Verified by:** Task 3 (Head-Offset Architecture Design)
**Date:** 2026-07-05
**Findings:** The hand-derived `sum(r, a(r,p)*nu_sb(r,tt+1))` cross-term is **not** robert's fix. Control experiment: patching robert's cold `stat_x` from `nu_sb(r,tt)` to `nu_sb(r,tt+1)` leaves the cold MCP at the spurious **6741.67** (unchanged) — because under the emit's **base-labeling** of `sb(r,tt)$(ord(tt)<=card-1)`, the equation body references `x(p,tt)` at the base index, so `∂sb(r,tt)/∂x(p,tt)=a(r,p)` and the emitted `nu_sb(r,tt)` index is **already correct**. robert's cold-match (11025) / residual → 0 is achieved by the **`stat_s` objective-gradient boundary-term fix** instead (drop-in `−res-value(r)` at `tt=4` + guard `storage-c(r)` to `t(tt)`) — see Unknown 1.1. The harness localized to `stat_x` only because its same-index dual transfer (`nu_sb.l=sb.m`, NLP marginals stored at the head label) shifts `nu_sb` and corrupts the `stat_x` residual rows (a transfer artifact, not a formula bug).
**Evidence:** `HEAD_OFFSET_ARCHITECTURE_DESIGN.md` §1.2–1.5 + §Appendix (the `stat_x`-only patch → 6741.67; the harness-artifact explanation).
**Decision:** do NOT touch robert's `stat_x`; the objective-gradient `stat_s` fix is the whole robert fix (Unknown 1.1). This also invalidates the banked `ISSUE_1443` Day-12 robert diagnosis (a PR24 correction — recorded for the Task-5 gate refresh).

**Task 8 (2026-07-06) — tooling-readiness layer (the harness handles the `nu_sb` head-offset multiplier).** Actual harness runs: **robert** dual transfer **CONSISTENT** (verdict CASE_B, top `stat_x(high,3)` rel 7.20); **mine** dual transfer **CONSISTENT** (verdict CASE_B, top `stat_x(4,1,1)` rel 1.33). So the harness loads the head-offset `nu_sb`/`lam_pr` multipliers with **no mis-transfer / no false-inconsistency** — the self-check is trustworthy. **But** the top per-row residual on base-normalized head-offset equations is a **same-index-transfer artifact** (robert's `stat_x` top row; the operative bug is `stat_s` — this Unknown's finding), so per-row *localization* must be corroborated with the **cold-solve control experiment** (Task 3's method). Optional non-blocking ≤ 1 h harness extension (head-label warm-start `nu_<eq>.l(idx)=<eq>.m(head(idx))`). See `TOOLING_READINESS_AUDIT.md` Tool 1.

---

# Category 2: rocket #1462 — Non-Convex Convergence Forcing

## Unknown 2.1: Which forcing lever moves rocket's residual MS-5 toward MS 1/2 at 1.0128?

### Priority
**Critical** — decides whether P2 yields a Solve at all; rocket is intrinsic non-convergence (Sprint 29 Day 2), so the whole priority hinges on a forcing lever working.

### Assumption
One of {trust-region damping, homotopy/continuation from a relaxed problem, multi-start from perturbed warm-starts} moves rocket's MS-5 (which the landed `_fx_` warm-start left at objective 1.016 after 1.137 → 1.016, MS 5 persisting) toward MS 1/2 at the NLP optimum 1.0128 — the residual is a *convergence* problem, not an emit problem, so a solution-forcing strategy (not a further emit fix) is the lever.

### Research Questions
1. Which of the three lever families produces the largest MODEL STATUS improvement on rocket's presolve MCP?
2. Does the `_fx_` warm-start (already landed) plus one forcing lever reach MS 1/2, or does rocket resist all in-GAMS levers?
3. Is the lever a continuation-parameter loop, a bound-relaxation schedule, or a `.l`-perturbation multi-start?
4. What objective does the best lever reach vs the NLP reference 1.0128?

### How to Verify
Prototype-probe the most promising lever on rocket's presolve MCP (env-guarded, zero `src/`); measure the MODEL STATUS progression:
```bash
# Apply the chosen lever to rocket's presolve MCP; solve; read MS + objective
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/rocket.gms
# Expect: a lever drives MS 5 → MS 1/2 at ~1.0128 → PROCEED
#         no in-GAMS lever moves it → PATH-option Sprint-31 hand-off (2.2)
```

### Risk if Wrong
- **No lever moves rocket:** P2 yields no Solve in Sprint 30; the forcing scaffold (P8) still lands + the PATH-option question becomes the Sprint-31 PATH-consultation hand-off (2.2). -1 Solve vs target.

### Estimated Research Time
2.5 hours (Task 4 — the forcing-lever survey + the rocket prototype-probe)

### Owner
Development team (numerics / solver-interface)

### Verification Results
⚠️ **Status:** VERIFIED — no PATH-option configuration (via optfile) forces rocket (intrinsic non-convergence confirmed)
**Verified by:** Task 4 (Non-Convex Forcing Strategy Survey)
**Date:** 2026-07-05
**Findings:** Prototype-probed the tunable forcing levers on rocket's presolve MCP (env-guarded `path.opt` + `mcp_model.optfile=1`, zero `src/`). Baseline: MCP MS 5, **477 INFES**, 0 eval errors (embedded NLP MS 2). Across `proximal_perturbation` ∈ {1e-2, 1e-1, 1.0, 1e2} (trust-region/Levenberg-Marquardt Jacobian regularization), `crash_method pnewton`, `merit_function normal`, and combined strong configs, rocket **stays MS 5** — best (`merit_function normal` + `proximal_perturbation 1e-2`) reduces INFES 477 → **382** but never converges. rocket is the Goddard rocket (division-by-variable `1/ht²`,`1/m²` initial Jacobian) — intrinsic non-convergence, confirming ISSUE_1462 Day-2.
**Evidence:** `docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md` §1–§2 + §Appendix.
**Decision:** no tunable PATH-option configuration (via optfile) crosses; the PATH-option tuning (INFES 477 → 382) is the concrete **Sprint-31 PATH-consultation hand-off** (2.2). Sprint-30 P2 = the emitted-GAMS forcing scaffold (homotopy/multi-start), not a firm rocket +1 Solve.

**Task 6 (2026-07-06) — risk/decision layer:** **PROCEED-to-scaffold (firm P8)** — build the `--force <strategy>` driver + MODEL-STATUS reporter; it lands regardless. **rocket's +1 Solve = REPLAN to the Sprint-31 PATH consultation** (prior of REPLAN High — no PATH-option config converges even from the NLP optimum). One PROCEED-flip: if a scaffold *homotopy/multi-start* strategy (the emittable-GAMS levers the Task-4 probe did not exhaustively drive) reaches MS 1/2 at 1.0128, rocket's +1 Solve lands in Sprint 30 (low prior — the NLP-optimum warm-start already fails). **Reallocation on rocket REPLAN:** the scaffold lands; freed tuning budget → scaffold hardening + Priority 3 hhfair (#1236). See `REPLAN_RISK_ASSESSMENT.md` Track B.

---

## Unknown 2.2: Is a forcing lever expressible in emitted GAMS, or does it require a PATH solver option?

### Priority
**High** — sets the nlp2mcp/PATH boundary; a PATH-option-only lever is a clean Sprint-31 hand-off, not a dead end, but changes P2's Sprint-30 deliverable.

### Assumption
At least one effective forcing lever is expressible **inside nlp2mcp's emitted GAMS** (a continuation parameter, a bound-relaxation schedule, or a `.l` perturbation loop), so P2 can land a Sprint-30 emit change; the levers that need a PATH solver option (merit-function / trust-region / crash tuning) are scoped as the Sprint-31 PATH-consultation question.

### Research Questions
1. Which levers are pure emitted-GAMS constructs vs which need a `option` / PATH control file directive?
2. Does the in-GAMS lever set include the one that actually moves rocket (2.1), or is the effective lever PATH-side?
3. What is the exact Sprint-31 PATH-consultation scope (the levers deferred to the PATH author)?

### How to Verify
For each lever, classify emittable-GAMS vs PATH-option; cross-check against the 2.1 probe result:
```bash
# Record per-lever: mechanism, emittable-GAMS? / PATH-option?, effect on rocket
grep -rn "option\|control file\|\.optfile" docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md 2>/dev/null | head
```

### Risk if Wrong
- **Effective lever is PATH-only:** P2's Sprint-30 deliverable becomes the scaffold + the PATH hand-off, not a Solve; the schedule must know this at Day 0 (Task 6 REPLAN framing).

### Estimated Research Time
1.5 hours (Task 4 — the nlp2mcp/PATH boundary classification)

### Owner
Development team (numerics / solver-interface)

### Verification Results
✅ **Status:** VERIFIED — the effective levers are PATH options; the emittable-GAMS levers are the P8 scaffold
**Verified by:** Task 4 (Non-Convex Forcing Strategy Survey)
**Date:** 2026-07-05
**Findings:** The three *tunable* levers (trust-region = `proximal_perturbation`, `crash_method`, `merit_function`) are **PATH options** (delivered via an `optfile` — nlp2mcp can emit the optfile, but the tuning is PATH-internal). The two *structural* levers (homotopy/continuation, multi-start) are **emittable GAMS** (a driver loop around `Solve mcp_model using MCP;`). On the evidence (2.1), even the strongest PATH-option config does not converge rocket → the convergence question is PATH-solver-internals.
**Evidence:** `NONCONVEX_FORCING_SURVEY.md` §1 (the lever/boundary table) + §4.
**Decision:** **Sprint-31 PATH-author consultation** for the PATH-option tuning (the scoped question: which option set/regularization schedule/reformulation converges the division-by-variable optimal-control MCP); the emitted-GAMS homotopy/multi-start scaffold is the **Sprint-30 P8** deliverable + entry point (feeds Unknown 8.3 / Task 8).

**Task 5 (2026-07-05):** the #1462 gate was refreshed — PROCEED to the P8 forcing scaffold; PATH-option tuning → Sprint-31 consultation.

**Task 6 (2026-07-06) — risk/decision layer:** the emittable-GAMS/PATH boundary is the rocket REPLAN pivot. Since the effective (tunable) levers are PATH-side and none converge, **rocket's +1 Solve REPLANs to the Sprint-31 PATH-author consultation**; the emittable-GAMS homotopy/multi-start levers are the firm **Sprint-30 P8 scaffold**. Sprint-31 exit = the scoped PATH-option/regularization/reformulation question for the division-by-variable optimal-control MCP. See `REPLAN_RISK_ASSESSMENT.md` Track B.

---

## Unknown 2.3: Does the chosen forcing lever recover any cold-convex Case-c residue (shared payoff)?

### Priority
**Medium** — a bonus; the lever's primary target is rocket, but a shared payoff on the Case-c cohort would lift additional models.

### Assumption
The forcing lever chosen for rocket also moves at least one cold-convex Case-c cohort model (from the Sprint-29 `docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md`) toward a solve, because both share the "correct emit, non-convex cold-convergence failure" signature.

### Research Questions
1. Which Case-c cohort models share rocket's non-convergence signature?
2. Does the chosen lever move any of them toward MS 1/2?
3. Is the shared payoff worth a Sprint-30 pass, or a Sprint-31 forcing-sprint item?

### How to Verify
Apply the chosen lever to 2–3 Case-c cohort models; measure MODEL STATUS:
```bash
# From COLD_CONVEX_COHORT_SURVEY.md §"Case c", pick 2-3 models; apply the lever; read MS
```

### Risk if Wrong
- **No shared payoff:** no loss (rocket still the primary target); the Case-c residue stays documented for Sprint 31 (Unknown 7.2).

### Estimated Research Time
1 hour (Task 4 — the cold-convex Case-c shared-payoff check)

### Owner
Development team (numerics / solver-interface)

### Verification Results
✅ **Status:** VERIFIED — no shared payoff (the Case-c cohort already warm-matches)
**Verified by:** Task 4 (Non-Convex Forcing Strategy Survey)
**Date:** 2026-07-05
**Findings:** The 4 cold-convex Case-c cohort models (`COLD_CONVEX_COHORT_SURVEY.md` §3 — **bearing, launch, mathopt3, robustlp**) are emit-correct (residual ≤ 8e-6) and **already warm-match** (`model_optimal_presolve` + `compare_objective_match` in the Day-0 DB) — they need **no forcing**. rocket (`model_infeasible`) is the **sole** genuinely-non-converging model (its NLP-optimum warm-start still fails — the distinguishing intrinsic-non-convergence signature the 4 do not share). A rocket forcing lever therefore has no additional cohort to lift.
**Evidence:** `NONCONVEX_FORCING_SURVEY.md` §3 (per-model bucket table); DB `data/gamslib/gamslib_status.json`.
**Decision:** no shared-payoff bonus; rocket forcing is a standalone (Sprint-31) target. Feeds Unknown 7.2 (residue disposition = the 4 already-matching + rocket-alone).

---

# Category 3: hhfair #1236 — Widened-VARIABLE Presolve Fix

## Unknown 3.1: Does generalizing the #1449 widened-symbol handling from the parameter case to the variable case clear the `$184`?

### Priority
**Critical** — the residual MCP must compile before the CES verdict (3.2) is even readable; the `$184` is the gate to the whole priority.

### Assumption
hhfair's `$184` (Sprint 29 Day 8 — a live nonlinear-stationarity variable `n(t)` widened to `n(tl)` under `--nlp-presolve`) is the *variable* analogue of the #1449 widened-*parameter* `$184` conflict, so extending the #1449 handling from parameters to variables clears the compile error — the fix surface is the #1449 widened-symbol path, not the Day-0-attributed `$141`.

### Research Questions
1. Is the `$184` root cause the widened-VARIABLE `n(t)→n(tl)` under `$onMulti`, exactly analogous to the #1449 widened-parameter case?
2. Does the #1449 code path already have a variable branch, or does it hard-assume parameters?
3. Does clearing the `$184` require the same domain-restriction logic (`tl→t`) the #1449 parameter fix used?
4. Is `n` a *live nonlinear-stationarity coefficient* (so its emit cannot be dropped, only domain-corrected)?

### How to Verify
Reproduce the `$184`; inspect the #1449 widened-symbol handling for a variable branch:
```bash
# Reproduce the hhfair $184 (Sprint 29 Day 8)
grep -rn "184\|widened\|\$onMulti" docs/issues/ISSUE_1236_*.md docs/issues/finished/ISSUE_1449_*.md 2>/dev/null | head
```

### Risk if Wrong
- **Not the #1449 variable analogue:** the fix surface is elsewhere → re-trace (PR24); hhfair's compile stays broken and the +Match is at risk.

### Estimated Research Time
2 hours (Task 5 — the Phase-0 gate refresh corrects the hhfair blocker from `$141` to `$184`)

### Owner
Development team (emit specialist)

### Verification Results
✅ **Status:** VERIFIED — Phase-0 gate refreshed (PROCEED via the #1449 widened-VARIABLE fix)
**Verified by:** Task 5 (Phase 0 Acceptance Gate refresh)
**Date:** 2026-07-05
**Findings:** The #1236 gate now records the Sprint-30 disposition: the compile blocker is the **`$184`** #1449 widened-symbol conflict for the VARIABLE `n` (source `n(t)` vs MCP-widened `n(tl)`), **not** the Day-0-attributed `$141`. PROCEED to generalize the #1449 widened-symbol handling from the parameter case to the variable case so the residual MCP compiles.
**Evidence:** `docs/issues/ISSUE_1236_hhfair-objective-mismatch.md` §"Phase 0: Acceptance Gate" (Sprint-30 refresh note); Sprint 29 Day 8 `$184` finding.
**Decision:** PROCEED; the fix-surface (the #1449 widened-symbol path, variable branch) is a Day-0 hypothesis (PR24) to re-trace in-sprint; verified via `kkt_residual.py data/gamslib/raw/hhfair.gms` after the compile clears.

---

## Unknown 3.2: After the `$184` clears, is hhfair's CES/product mismatch a localizable Case-b row or an inherent non-convexity?

### Priority
**High** — determines whether hhfair yields a Sprint-30 +Match (Case-b) or defers to Sprint-31 forcing (Case-c).

### Assumption
Once the `$184` compile error clears, hhfair's residual objective mismatch is a **localizable Case-b `stat_*` row** (a CES/product-form cross-term the harness pins), not an inherent non-convexity — so hhfair yields a Sprint-30 +Match.

### Research Questions
1. Does the harness return Case-b (localizable row) or Case-c (distributed / non-convex) once hhfair compiles?
2. Is the mismatch a CES aggregator cross-term or a product-form derivative?
3. Does the localized row match a known cross-term shape (reusing a prior fix), or is it novel?

### How to Verify
After the `$184` fix, run the harness on hhfair:
```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/hhfair.gms
# Expect: CASE_B + a localizable stat_* row → +Match; CASE_C → Sprint-31 forcing
```

### Risk if Wrong
- **Case-c (inherent):** hhfair yields no Sprint-30 +Match → defers to Sprint 31; the `$184` fix still lands (a Translate/compile improvement).

### Estimated Research Time
1.5 hours (Task 5 — the post-compile CES verdict in the hhfair gate)

### Owner
Development team (AD/emit specialist)

### Verification Results
✅ **Status:** VERIFIED — gate encodes the post-compile CES verdict branch
**Verified by:** Task 5 (Phase 0 Acceptance Gate refresh)
**Date:** 2026-07-05
**Findings:** The #1236 gate records: after the `$184` clears, read the CES/product objective-mismatch verdict — PROCEED if it localizes to a Case-b `stat_*` row (+1 Match), REPLAN to Sprint 31 if the post-compile mismatch is an inherent non-convexity (Case-c). The verdict is unreadable until the compile fix lands.
**Evidence:** `ISSUE_1236` §"Phase 0" Sprint-30 refresh; `kkt_residual.py` as the discriminator.
**Decision:** conditional — PROCEED-if-Case-b / REPLAN-to-Sprint-31-if-Case-c, decided in-sprint after the `$184` compile fix.

---

## Unknown 3.3: Does the widened-VARIABLE fix regress the #1449 widened-parameter presolve models?

### Priority
**Medium** — a blast-radius question; extending the #1449 path to variables must not break the parameter case it already handles.

### Assumption
Extending the #1449 widened-symbol handling to variables is *additive* — it fires only on the widened-VARIABLE shape (a live-stationarity variable widened under `$onMulti`) and leaves the existing widened-parameter presolve models (the #1449 cohort) byte-identical.

### Research Questions
1. Which presolve models exercise the #1449 widened-parameter path today (the blast-radius set)?
2. Does the variable extension share the parameter branch or add a disjoint one?
3. After the fix, are the #1449 parameter-cohort goldens byte-stable + solve-stable?

### How to Verify
Enumerate the #1449 cohort; regen + re-solve after the fix:
```bash
# Regen all presolve goldens; expect the #1449 parameter cohort byte-stable, only hhfair changed
grep -rln "widened\|1449" data/gamslib/mcp/*_mcp_presolve.gms 2>/dev/null | head
```

### Risk if Wrong
- **Regression:** the variable extension breaks the parameter case → tighten the gate; caught by the presolve-golden byte-check + `--resolve-changed` before merge.

### Estimated Research Time
1 hour (Task 9 — the blast-radius enumeration in the backlog fix-surface analysis)

### Owner
Development team (emit specialist)

### Verification Results
✅ **Status:** VERIFIED — the #1449 widened-parameter presolve cohort is 4 models; the variable extension is a disjoint additive path
**Verified by:** Task 9 (Backlog Fix-Surface Analysis)
**Date:** 2026-07-06
**Findings:** The #1449 widened-**parameter** presolve cohort = **4 models** — `cclinpts`, `chain`, `otpop`, `rocket` (the `*_mcp_presolve.gms` carrying the `#1449` marker). hhfair's blocker is the **`$184`** #1449 conflict for a **VARIABLE** `n` (source `n(t)` vs MCP-widened `n(tl)`); the parameter `__pw`-companion fix does **not** transfer (`n` is a live nonlinear-stat coefficient, not a value-copy), so the fix is a **new companion-*variable* + value-coupling path**, disjoint from and additive to the widened-parameter `__pw` branch. So the extension fires only on the widened-VARIABLE shape and leaves the 4 widened-parameter goldens untouched.
**Evidence:** `grep -lE "#1449" data/gamslib/mcp/*_mcp_presolve.gms` → cclinpts/chain/otpop/rocket; `docs/issues/ISSUE_1236_*.md` Day-8 (the `$184` widened-VARIABLE root cause); `BACKLOG_FIX_SURFACE_ANALYSIS.md` Part D.
**Decision:** blast-radius-safe as an additive path — the Day-0 check is a byte-scan of the 4 #1449 presolve goldens (0 diff) + `--resolve-changed` GO after the fix; only hhfair's golden changes. Feeds Task 6 (hhfair PROCEED via the widened-VARIABLE fix, then the CES/product Case-b verdict).

---

# Category 4: #1385 — Symbolic Runtime-Guard Cross-Term Emit

## Unknown 4.1: Do the Sprint-29-banked hand-derived cross-terms materialize atomically with the runtime-guarded re-emit for sarf?

### Priority
**High** — #1385 is the +Translate target; the banked cross-terms must land *with* the runtime-guarded equation-body re-emit, or the MCP is inconsistent.

### Assumption
The Sprint-29-banked hand-derived `J_gᵀ·lam` cross-terms materialize **atomically** with the runtime-guarded equation-body re-emit for **sarf** (the reference target) — the re-emit and the cross-terms are one coupled change (a re-emit without cross-terms = an inconsistent MCP, a cross-term without re-emit = a dangling multiplier), with no quoted-set-name multiplier indices.

### Research Questions
1. Where do the runtime-guard equation-body re-emit and the `J_gᵀ·lam` cross-terms materialize (`src/kkt/stationarity.py` + `src/ad/index_mapping.py`)?
2. Do the emitted multiplier indices avoid quoted set names (the Sprint-29-noted failure mode)?
3. Does the sarf MCP compile clean with the coupled change (action=c, 0 errors)?
4. Is the banked hand-derivation still correct against the current main emit?

### How to Verify
Pin the emit site; emit sarf's MCP with the coupled change; check for quoted-set indices + compile:
```bash
grep -rn "runtime.guard\|J_g\|cross.term" docs/issues/ISSUE_1385_*.md | head
# Emit sarf_mcp.gms; grep for quoted-set multiplier indices; compile-check
```

### Risk if Wrong
- **Not atomic / quoted indices:** the sarf MCP is inconsistent or won't compile → the +Translate is lost; re-derive the coupling before emitting.

### Estimated Research Time
1.5 hours (Task 9 — the #1385 sarf emit-site pin in the backlog fix-surface analysis)

### Owner
Development team (AD/emit specialist)

### Verification Results
✅ **Status:** VERIFIED — gate refreshed (PROCEED to the atomic runtime-guard re-emit for sarf)
**Verified by:** Task 5 (Phase 0 Acceptance Gate refresh)
**Date:** 2026-07-05
**Findings:** The #1385 gate records the Sprint-30 disposition: land the runtime-guarded equation-body re-emit **atomically** with the banked `J_gᵀ·lam` cross-terms for **sarf** (a re-emit without cross-terms = an inconsistent MCP), with **no quoted-set-name multiplier indices** (the Sprint-26-Day-4 failure mode) and no re-introduction of the translate-timeout.
**Evidence:** `docs/issues/ISSUE_1385_*.md` §"Phase 0" Sprint-30 refresh (sarf reference target; cross-terms hand-derived + banked).
**Decision:** PROCEED; fix-surface (Day-0 hypothesis) = `src/kkt/stationarity.py` + `src/ad/index_mapping.py`, pinned by Task 9; REPLAN to Sprint 31 if the symbolic re-emit re-triggers the combinatorial blow-up.

**Task 9 (2026-07-06) — emit-site pinned (two coupled sites).** `BACKLOG_FIX_SURFACE_ANALYSIS.md` Part A pins: (1) **`src/ad/index_mapping.py`** — extend `_is_blowup_dynamic_subset_equation` / `enumerate_equation_instances` from the srpchase **1-D** shape (`len(eq_domain)!=1` bails) to sarf's **2-D** dynamic-subset constraints (`tbal(g,t)$taskposs`, `equipb1(m,t)$equipposs`, `equipb2(n,t)$equipposs`); (2) **`src/kkt/stationarity.py`** — a **new symbolic runtime-guard cross-term emit path** that differentiates each short-circuited constraint body parametrically in `(g,t,m,n)` (the equations enumerate **zero** instances, so the `J_gᵀ·lam` cross-terms can't be assembled per-instance) and injects the banked 6-guarded-term `stat_task(g,t,m,n)` derivation with `$taskposs`/`$equipposs` guards and **no set-name multiplier indices**. Atomic (re-emit + cross-terms together). Feeds Unknown 4.2 (the emit must be O(constraints), not O(instances)).

---

## Unknown 4.2: Is sarf's skipped-constraint instance count tractable at emit time, or does the symbolic re-emit re-introduce the translate-timeout?

### Priority
**Medium** — the Option-1 short-circuit exists *because* sarf's instance enumeration blew up the translate time; the symbolic re-emit must not re-introduce it.

### Assumption
sarf's skipped-constraint instance count is tractable at emit time, so the symbolic runtime-guarded re-emit (which materializes the previously-short-circuited cross-terms) does **not** re-introduce the translate-timeout that Option-1 was created to avoid.

### Research Questions
1. How many constraint instances does sarf's runtime-guarded re-emit materialize?
2. Is the symbolic re-emit `O(instances)` or does it re-trigger the combinatorial blow-up Option-1 short-circuited?
3. What is sarf's translate wall-clock with the re-emit vs the short-circuit?

### How to Verify
Translate sarf with the symbolic re-emit; measure wall-clock:
```bash
# Time sarf translation with the runtime-guarded re-emit; compare to the Option-1 short-circuit baseline
```

### Risk if Wrong
- **Timeout re-introduced:** the symbolic re-emit is non-viable at scale → the +Translate defers; the short-circuit stays.

### Estimated Research Time
1 hour (Task 9 — the sarf instance-count tractability check)

### Owner
Development team (AD/emit specialist)

### Verification Results
⚠️ **Status:** SCOPED (Task 9) — the instance counts are pinned; tractability hinges on the symbolic re-emit being O(constraints), the Day-0 timing gate
**Verified by:** Task 9 (Backlog Fix-Surface Analysis)
**Date:** 2026-07-06
**Findings:** sarf's three blow-up constraints materialize **tbal 384 + equipb1 648 + equipb2 120 = 1,152** instances (the `taskposs`/`equipposs` conditions are computed from `treq`/`tech` data → zero concrete members at compile time → the full Cartesian is what blows up `differentiate_expr` >200 s, `ISSUE_1385` Day-9). The symbolic runtime-guard re-emit must **NOT** re-enumerate these per-instance — it differentiates each constraint body **once** parametrically in `(g,t,m,n)` and emits a single runtime-guarded row, so the emit-time cost is **O(constraints), not O(instances)**. The cross-term *derivation* is tractable (banked, 6 guarded terms); the open risk is purely the *implementation* keeping the emit O(constraints).
**Evidence:** `docs/issues/ISSUE_1385_*.md` §PROCEED/REPLAN (the 384/648/120 instance counts + the blow-up diagnosis); `BACKLOG_FIX_SURFACE_ANALYSIS.md` Part A.
**Decision:** the Day-0 tractability gate = time `sarf_mcp.gms` emit; **PROCEED** if it emits under the translate budget, **REPLAN to Sprint 31** if the symbolic re-emit re-triggers the per-instance enumeration (the timeout). The +Translate is conditional on this gate.

---

# Category 5: Offset-Alias Cross-Terms #1111/#1112 (polygon + himmel16)

## Unknown 5.1: Was the Sprint-29 Day-5 revert caused by the offset-image cross-term being coupled with the distance-Jacobian?

### Priority
**High** — the coupling determines whether a coordinated fix is possible or whether both pieces must land together; a mis-understood revert cause repeats the regression.

### Assumption
The Sprint-29 Day-5 revert of the offset-alias fix was caused by the offset-image cross-term being **coupled** with the distance-Jacobian (fixing one without the other regressed polygon/himmel16), so a **coordinated** fix that lands both together avoids the regression.

### Research Questions
1. What exactly regressed at the Day-5 revert (which models, which residual)?
2. Is the offset-image cross-term computationally coupled with the distance-Jacobian (both reference the same offset image)?
3. Does a coordinated fix (both together) drive polygon/himmel16 to +Match without the regression?
4. What is the cyclic/successor-offset shape (`i++1` / `ord(j)=ord(i)+1`) the fix must gate to?

### How to Verify
Review the Day-5 revert record; design the coordinated fix; check the property-test shape:
```bash
grep -rn "Day-5\|revert\|distance.Jacobian\|offset.image" docs/issues/ISSUE_1146_*.md docs/issues/ISSUE_1143_*.md docs/planning/EPIC_4/SPRINT_29/BACKLOG_FIX_SURFACE_ANALYSIS.md 2>/dev/null | head
```

### Risk if Wrong
- **Not the coupling:** the real revert cause is elsewhere → the coordinated fix regresses again; re-diagnose before re-attempting (PR24).

### Estimated Research Time
1.5 hours (Task 9 — the Day-5 revert root-cause + coordinated-fix hypothesis)

### Owner
Development team (AD specialist)

### Verification Results
✅ **Status:** VERIFIED — the coupling is confirmed (polygon: objective-gradient cross-term × distance-Jacobian symmetry); the coordinated fix lands both together
**Verified by:** Task 9 (Backlog Fix-Surface Analysis)
**Date:** 2026-07-06
**Findings:** The Day-5 revert was **polygon** specifically: the Day-4 representative-selection fix made polygon's **objective gradient** correct (`stat_theta`/`stat_r` gained the predecessor offset-image cross-term) but the Day-5 Checkpoint re-solve caught **`match` (0.7797) → `mismatch` (spurious 0.0 optimum)**. Root cause = a **SECOND, independent bug**: the `distance(i,j)` **constraint-Jacobian symmetry** — `stat_r` sums only the `ord(j)>ord(i)` first-index direction, dropping the symmetric second-index `r(j)` term (the "Multi-pattern Jacobian: skipping correction for distance/r" warning). With the objective gradient complete but the distance-Jacobian one-sided, the KKT admits a degenerate `area=0` solution. **So the coupling is confirmed** — neither piece alone matches: (a) the objective-gradient cross-term alone regressed to 0.0 (the revert); (b) the distance-Jacobian alone leaves the dropped cross-term. **himmel16 is a DISTINCT shape** (its cyclic cross-term is structurally *present*; the 2.0 residual is a numeric/objvar-gradient-sign defect, not a dropped term) — the two models share the code path, not the exact defect.
**Evidence:** `docs/issues/ISSUE_1143_*.md` §"REVERTED — Sprint 29 Day 5" (the match→mismatch + the distance-Jacobian symmetry); `docs/issues/ISSUE_1146_*.md` §"NOT a missing-term bug"; `BACKLOG_FIX_SURFACE_ANALYSIS.md` Part B.
**Decision:** land the coordinated fix — polygon = the successor-offset objective cross-term (`derivative_rules.py` `_diff_varref` / the `_partial_collapse_sum` non-circular-offset branch, preserved in `shape8` xfail) **+** the `distance(i,j)` second-index symmetry (`constraint_jacobian.py` multi-pattern correction); gate tightly to the cyclic/successor shape (Unknown 5.2). REPLAN to Sprint 31 if it needs the #1111/#1112 core.

---

## Unknown 5.2: Does the localized polygon/himmel16 fix stay gateable to the offset-alias shape, or does it require the #1111/#1112 AD core?

### Priority
**High** — a localized-vs-architectural decision; if the fix needs the #1111 alias-aware-differentiation / #1112 dollar-condition-propagation core, it is a Sprint-31 architectural filing, not a Sprint-30 fix.

### Assumption
The polygon/himmel16 offset-alias fix stays **gateable** to the cyclic/successor-offset shape (a localized cross-term correction), so it lands in Sprint 30 without the #1111 (alias-aware differentiation) / #1112 (dollar-condition propagation) AD-engine core — those remain a Sprint-31 architectural item.

### Research Questions
1. Can the fix be gated tightly to the cyclic/successor shape, or does correctness require the general alias-aware differentiation (#1111)?
2. Does the dollar-condition propagation (#1112) affect polygon/himmel16, or only the broader cohort?
3. Where is the localized-vs-architectural boundary (the REPLAN trigger)?

### How to Verify
Assess the gate tightness; check whether polygon/himmel16 need the #1111/#1112 core:
```bash
grep -rn "1111\|1112\|alias.aware\|dollar.condition" docs/issues/ISSUE_1146_*.md docs/issues/ISSUE_1143_*.md 2>/dev/null | head
```

### Risk if Wrong
- **Needs the AD core:** polygon/himmel16 defer to Sprint 31 (the #1111/#1112 architectural workstream); no Sprint-30 +Match from P5.

### Estimated Research Time
1.5 hours (Task 5 gate + Task 9 — the localized-vs-architectural boundary)

### Owner
Development team (AD specialist)

### Verification Results
✅ **Status:** VERIFIED — gates refreshed with the localized-vs-architectural boundary
**Verified by:** Task 5 (Phase 0 Acceptance Gate refresh)
**Date:** 2026-07-05
**Findings:** The #1146/#1143 gates record the Sprint-30 disposition: PROCEED to a **coordinated** offset-alias fix (the offset-image cross-term landed **together with** the distance-Jacobian — the Sprint-29 Day-5 revert proved they are coupled), gated tightly to the cyclic/successor-offset shape. This is cold-robustness / genuine-floor (both already match warm), not +Match.
**Evidence:** `docs/issues/ISSUE_1146_*.md` + `ISSUE_1143_*.md` §"Phase 0" Sprint-30 refresh notes.
**Decision:** PROCEED if a tight gate makes it correct; **REPLAN to Sprint 31** (the #1111 alias-aware-differentiation / #1112 dollar-condition-propagation AD-engine core) if the localized fix needs the general architecture. The architectural-REPLAN boundary is the Task-6 assessment input.

**Task 9 (2026-07-06) — the boundary pinned per shape.** `BACKLOG_FIX_SURFACE_ANALYSIS.md` Part B refines: the two models share the code path but have **distinct** defects, each with its own localized surface — **polygon** = successor-offset objective cross-term (`_diff_varref` / the `_partial_collapse_sum` non-circular-offset branch) **+** distance-Jacobian second-index symmetry (`constraint_jacobian.py`); **himmel16** = the cyclic `i++1` cross-term is *present*, so its fix is the objvar-gradient-**sign** reconciliation in the `_diff_varref(circular=True)` branch + the dual-transfer sign. Both lean **localized** (single-row integer-residual signatures, gateable to the cyclic/successor shape). **REPLAN to Sprint 31** (#1111/#1112 AD core) only if a tight shape-gate can't make either correct without threading general alias differentiation. The #1111/#1112 footprint is small (3 issues: #1146/#1143/#1162) → Sprint-31 candidate, not an Epic-5 necessity. Flagged for the Task-6 REPLAN assessment.

---

## Unknown 5.3: Does a coordinated polygon/himmel16 fix stay blast-radius-safe (no regression on the other offset-alias models)?

### Priority
**Medium** — a blast-radius question; the coordinated fix must not regress the models that already emit the offset-alias shape correctly.

### Assumption
The coordinated offset-alias fix, gated to the cyclic/successor-offset shape, is blast-radius-limited to polygon + himmel16 (and any model with the identical shape), leaving the rest of the corpus byte-identical.

### Research Questions
1. Which corpus models emit the cyclic/successor-offset shape (the potential blast radius)?
2. Does the gate fire only on the polygon/himmel16 shape, or on adjacent shapes too?
3. After the fix, are the non-target models byte-stable + solve-stable?

### How to Verify
Enumerate the offset-alias shape across the corpus; regen + re-solve:
```bash
# Grep the corpus for the cyclic/successor-offset shape; regen goldens; verify byte-stability
```

### Risk if Wrong
- **Wider blast radius:** the fix perturbs adjacent models → tighten the gate; caught by the golden byte-check + `--resolve-changed`.

### Estimated Research Time
1 hour (Task 9 — the offset-alias blast-radius enumeration + property-test fixture plan)

### Owner
Development team (AD specialist)

### Verification Results
✅ **Status:** VERIFIED — blast-radius-safe as two shape-gated fixes; guarded by the property catalog + `--resolve-changed`
**Verified by:** Task 9 (Backlog Fix-Surface Analysis)
**Date:** 2026-07-06
**Findings:** Each fix is gated to its own offset shape — polygon's successor `ord(j)=ord(i)+1` (+ the `distance` symmetry) and himmel16's circular `i++1` — so the blast radius is limited to models emitting the identical shape. The property-test catalog already guards these: `shape7_offset_alias_cyclic` (himmel16, passing structural guard) and `shape8_offset_alias_successor` (polygon, xfail-strict — flips to passing when the coordinated fix lands). The Day-0 blast-radius check is a full-corpus golden byte-scan + `--resolve-changed` GO after the fix (expect only polygon/himmel16 goldens change); the `shape8` xfail flipping to pass is the regression signal that the fix is complete + correctly scoped.
**Evidence:** `tests/integration/emit/test_ad_crossterm_shapes.py` (shape7 pass / shape8 xfail-strict — Task 8 re-confirmed 7 passed, 1 xfailed); `BACKLOG_FIX_SURFACE_ANALYSIS.md` Part B + Part E.
**Decision:** blast-radius-safe with the shape gate; the property fixtures (`shape7`/`shape8`) + the golden byte-scan + `--resolve-changed` are the Day-0 guards. Enabling `shape8` (drop `@pytest.mark.xfail`) is the completion gate for the coordinated fix.

---

# Category 6: camcge #1330 → Epic 5 Walras Transformation

## Unknown 6.1: Does the paper-verified drop-`lmequil` + fix-`cpi=1` transformation reach MODEL STATUS 1 at 191.7346 empirically?

### Priority
**Critical** — the transformation is proven on paper only (`CGE_DEGENERACY_SCOPING.md` §3); if the empirical GAMS run does not reach MS 1 at the NLP optimum, the Epic-5 P6 premise is invalid.

> **Shorthand note (governs all of Category 6):** "`cpi=1`" is a **generic placeholder** for a fixed price numéraire — **camcge has no literal `cpi` variable** (Task 7 grounding). The concrete camcge instantiation is a base-consumption-weighted composite-price index on the existing `p(i)`/`pd0(i)`: `sum(i$cles(i), cles(i)*p(i)) =e= sum(i$cles(i), cles(i)*pd0(i))` (`CAMCGE_WALRAS_TRANSFORM_DESIGN.md` §3.2). Read every "fix-`cpi=1`" below as this concrete numéraire.

### Assumption
The Walras transformation (drop **one** redundant market-clearing row *instance* — a single `lmequil(lc_drop)`, since Walras' law gives rank deficiency exactly 1, not the whole `lc` family — + fix a price numéraire — `cpi=1` shorthand, see the note above) empirically drives camcge's MCP to MODEL STATUS 1 at the NLP optimum 191.7346 — reproducing the paper-verified solution-preservation argument in a real GAMS solve.

### Research Questions
1. Does the drop-`lmequil` + fix-`cpi=1` MCP reach MS 1 (not MS 4-at-iteration-0, the current structural-singularity signature)?
2. Does it converge to 191.7346 (the camcge NLP optimum), confirming solution preservation?
3. Is the PATH basis non-singular after the transformation (the rank deficiency removed)?

### How to Verify
Run the transformed camcge MCP in GAMS; check MS + objective:
```bash
# Emit camcge with lmequil dropped + cpi fixed; solve; expect MS 1 at 191.7346
grep -rn "191.7346\|lmequil\|cpi\|numéraire\|numeraire" docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md | head
```

### Risk if Wrong
- **Does not reach MS 1:** the transformation is incomplete → P6 REPLANs to a deeper Epic-5 diagnosis; the Class-B general-emit work (P7) absorbs the freed budget.

### Estimated Research Time
1.5 hours (Task 7 — the empirical-confirmation experiment scope; run at P6 Day-0)

### Owner
Development team (CGE / Epic-5)

### Verification Results
✅ **Status:** VERIFIED — gate refreshed to PROCEED via the Epic-5 Walras transformation
**Verified by:** Task 5 (Phase 0 Acceptance Gate refresh)
**Date:** 2026-07-05
**Findings:** The #1330 gate records the Sprint-30 P6 disposition: PROCEED to the Epic-5 CGE-domain preprocessing transformation (drop the redundant `lmequil` row + fix a price numéraire `cpi=1`), solution-preserving on paper and reproducing camcge's NLP optimum 191.7346. The empirical confirmation (drop-`lmequil` + fix-`cpi=1` → MODEL STATUS 1 at 191.7346) is the P6 Day-0 gate.
**Evidence:** `docs/issues/ISSUE_1330_*.md` §"Phase 0" Sprint-30 refresh; `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md`.
**Decision:** PROCEED to the transformation; the detection-heuristic + numéraire-selection design is Prep Task 7; REPLAN to a per-model-numéraire-declaration Epic-5 item if the heuristic proves unreliable (Unknown 6.2).

**Task 6 (2026-07-06) — risk/decision layer:** the empirical MS-1 result (C1) is the first camcge gate, run at P6 Day-0. **PROCEED** the Epic-5 Walras transform if C1 reaches **MS 1 at 191.7346** *and* the detection heuristic is clean (6.2); **REPLAN** to deeper Epic-5 diagnosis if C1 does not reach MS 1 (the transform premise invalid) — the Class-B `stat_pz` general-emit fix (P7) then absorbs the freed budget. Prior of the empirical gate holding: high (the paper solution-preservation argument is solid). See `REPLAN_RISK_ASSESSMENT.md` Track C (step C1).

**Task 7 (2026-07-06) — the empirical experiment scoped.** The P6 Day-0 run is fully specified in `CAMCGE_WALRAS_TRANSFORM_DESIGN.md` §4.1: emit `camcge_ps.gms` (`--nlp-presolve`), drop **one** `lmequil(lc_drop)` instance (a single labor category — Walras' law ⇒ rank deficiency exactly 1, **not** the whole `lc` family) + its paired multiplier/comp rows, add `numeraire.. sum(i$cles(i), cles(i)*p(i)) =e= sum(i$cles(i), cles(i)*pd0(i));`, solve cold → **expect MS 1 at omega 191.7346, non-singular PATH basis** (was MS-4-at-iter-0). **Grounding refinement:** camcge has **no `cpi` variable** and `er` is a fixed `Scalar` (=.21, a partial anchor for *traded* prices only), so the scoping-doc "fix-`cpi=1`" is instantiated as the consumption-weighted composite-price index above (a CPI=1 normalization on the existing `p(i)`/`pd0(i)`). Solution-preserving on paper (§3.2: quantities are invariant along the price ray, so the numéraire is a base-year normalization — λ=1 only if the unscaled equilibrium already satisfies it — not a perturbation ⇒ omega 191.7346). **Status → VERIFIED** (the empirical experiment is designed + scoped; the MS-1 GAMS confirmation is the P6 Day-0 gate). Evidence: `CAMCGE_WALRAS_TRANSFORM_DESIGN.md` §1/§3.2/§4.1.

---

## Unknown 6.2: Is there a degeneracy-detection heuristic that does NOT false-flag a well-posed model?

### Priority
**Critical** — silently transforming a non-degenerate model (dropping a user row / fixing a price) would corrupt a correct problem; the false-positive guard is a correctness requirement, not an optimization.

### Assumption
A robust degeneracy-detection heuristic exists (a rank check on the market-clearing block, or the PATH basis-singularity report, or a model-structure signature) that recognises a Walras-degenerate model **without** false-flagging a well-posed one — so the transformation applies only to detected-degenerate models and passes well-posed models through untouched.

### Research Questions
1. What signal reliably distinguishes a Walras-degenerate model (camcge) from a well-posed CGE (the cohort)?
2. Does the heuristic have false positives on any corpus model (would it corrupt a correct problem)?
3. Is the detection a preprocessing-time rank check, a solver-report parse, or a structural signature?
4. What is the false-positive guard (the conservative default = pass through untouched)?

### How to Verify
Design the heuristic; run it across the CGE cohort; check for false positives:
```bash
# Apply the detection heuristic to camcge + irscge/lrgcge/moncge/stdcge; expect only camcge flagged
```

### Risk if Wrong
- **False positives:** a well-posed model is silently transformed → corrupted output; the guard must default to pass-through. This is the P6 correctness gate — REPLAN to a per-model *declaration* (opt-in) if the heuristic is unreliable.

### Estimated Research Time
1.5 hours (Task 7 — the detection-heuristic + false-positive-guard design; Task 6 assesses its reliability for the REPLAN decision)

### Owner
Development team (CGE / Epic-5)

### Verification Results
⚠️ **Status:** RISK-ASSESSED (Task 6) — the auto-heuristic is the REPLAN pivot; the per-model-declaration fallback makes it non-blocking. The heuristic *design* (the market-clearing-block rank check / PATH basis-singularity report / structural signature + the false-positive guard) is Prep Task 7.
**Verified by:** Task 6 (REPLAN-Prone Track Risk Assessment) — the risk/decision layer over the Task-7 design
**Date:** 2026-07-06
**Findings:** The detection-heuristic reliability is the **correctness gate** for the *automatic* Walras transform: silently dropping a user row / fixing a price on a well-posed model would corrupt a correct problem. Because **camcge is the sole inherent Walras case in the corpus** (Sprint-29 Unknown 5.1 inverted — the "CGE cohort" #1354/#1355/#1317/#1331/#1251 are distinct ordinary emit bugs, and the Class-B `stat_pz` cluster is a separate general-emit discrepancy), a robust automatic detector is a *stretch*, not a blocker: the fallback is a **per-model numéraire + redundant-row declaration (opt-in)**, which lands camcge's +1 Solve without an auto-detector.
**Evidence:** `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` §2 (camcge sole case) + §5 Q2 (the open detection question); `docs/planning/EPIC_4/SPRINT_30/REPLAN_RISK_ASSESSMENT.md` Track C (step C3).
**Decision:** **PROCEED-conditional** — PROCEED the automatic transform if the Task-7 heuristic flags camcge with **zero false positives** across the CGE cohort (camcge + irscge/lrgcge/moncge/stdcge, step C3); **REPLAN to the per-model-declaration Epic-5 item (opt-in)** if it false-flags a well-posed model or the numéraire proves per-model (Unknown 6.3). Prior of REPLAN-to-declaration: Medium (the likeliest outcome is PROCEED-with-declaration — the +1 Solve lands via opt-in, the auto-detector is deferred to a later Epic-5 iteration). **Reallocation on REPLAN:** freed auto-heuristic budget → the Class-B `stat_pz` general-emit fix (P7).

**Task 7 (2026-07-06) — the detection heuristic + false-positive guard designed.** `CAMCGE_WALRAS_TRANSFORM_DESIGN.md` §2 specifies a **conjunction of three signals** with a **pass-through default**: **S1** market-clearing-block rank deficiency (`equil(i)` + `lmequil(lc)` Jacobian rank < #rows, the primary signal), **S2** the singular-solve signature (MS-4-at-iter-0 + `kkt_residual.py` residual-clean + PATH basis-singularity), **S3** the CGE structural precondition (≥ 2 market-clearing rows + a budget-balance identity + price homogeneity, no existing numéraire). **Transform only if S1 ∧ S2 ∧ S3; else PASS THROUGH untouched.** The residual-clean sub-check inside S2 separates an *inherent structural* singularity (transform) from an *emit bug* (`CASE_B` → general emit path, NOT the transform), and a well-posed CGE that already fixes a numéraire has a full-rank block (S1 fails) → never transformed. The false-positive validation = the §4.2 cohort sweep (expect only camcge flagged). **Reliability caveat:** S1's rank-by-tolerance is the fragile piece → the auto-tier is PROCEED-conditional with the per-model-declaration fallback (6.3). **Status → VERIFIED** (design complete; the cohort false-positive sweep is the P6 Day-0 empirical validation). Evidence: `CAMCGE_WALRAS_TRANSFORM_DESIGN.md` §2 + §4.2.

---

## Unknown 6.3: Is the redundant-row + numéraire selection a single automatic rule or a per-model declaration?

### Priority
**Medium** — determines whether P6 ships an automatic transformation or a per-model opt-in; the fallback (declaration) is viable either way.

### Assumption
The redundant-row + numéraire selection follows a single automatic rule (a SAM-largest-sector rule, a CPI aggregate, or a structural redundancy detector) that reproduces camcge's 191.7346, rather than requiring a per-model hand declaration.

### Research Questions
1. Is there a principled rule for which market-clearing row to drop + which price to fix?
2. Does the rule generalise beyond camcge, or is camcge the sole case (making a per-model declaration acceptable)?
3. Does the automatic rule reproduce 191.7346 on paper?

### How to Verify
Design the selection rule; verify it picks camcge's `lmequil`/`cpi`:
```bash
# Check the rule selects lmequil (drop) + cpi (fix) for camcge and reproduces 191.7346
```

### Risk if Wrong
- **No automatic rule:** P6 ships a per-model declaration (opt-in) instead of auto-detection — acceptable if camcge is the sole case (Unknown 6.2 cohort check).

### Estimated Research Time
1 hour (Task 7 — the redundant-row + numéraire-selection rule design)

### Owner
Development team (CGE / Epic-5)

### Verification Results
✅ **Status:** VERIFIED — a per-model rule with a declaration fallback; the *argument* is generic, the *instantiation* is per-model
**Verified by:** Task 7 (camcge → Epic 5 Walras Transformation Design)
**Date:** 2026-07-06
**Findings:** `CAMCGE_WALRAS_TRANSFORM_DESIGN.md` §3 designs a two-tier rule. **Drop-row:** **one** factor-market row instance `lmequil(lc_drop)` (a single labor category — Walras' law ⇒ rank deficiency exactly 1, so drop one *row*, **not** the whole `lc` family; the other `lmequil` instances + all `equil(i)` stay enforced; the dropped market clears automatically at the solution). **Numéraire:** a **base-consumption-weighted composite-price index** pinned to its calibrated level — `sum(i$cles(i), cles(i)*p(i)) =e= sum(i$cles(i), cles(i)*pd0(i))` — instantiated on camcge's existing `p(i)`/`pd0(i)` (**grounding refinement: camcge has no `cpi` variable**, so the scoping-doc "fix-`cpi=1`" becomes this CPI=1 normalization on `p(i)`; a single good's price `p('numéraire-good')=pd0` is the fallback). By homogeneity of degree 0, quantities are invariant along the price ray, so the numéraire is a base-year normalization (λ=1 only if the unscaled equilibrium already satisfies it), a *selection* not a *perturbation* → quantities unchanged → `omega = prod(i$cles(i), cd(i)**cles(i))` = **191.7346** on paper. The general argument (Walras redundancy + price homogeneity) is generic to closed CGE models, but *which* row is redundant + *which* price is the numéraire is **per-model** (closure + SAM dependent).
**Evidence:** `CAMCGE_WALRAS_TRANSFORM_DESIGN.md` §3.1/§3.2/§3.3; `data/gamslib/raw/camcge.gms` (`lmequil` line 339, `p.l(i)=pd0(i)` line 401, `cles(i)`, `obj/omega` line 395, `er` Scalar); `CGE_DEGENERACY_SCOPING.md` §3.
**Decision:** ship the **automatic tier** (heuristic-driven `lmequil` drop + consumption-weighted numéraire) with a **per-model declaration fallback (opt-in)** — acceptable because camcge is the sole inherent Walras case (6.2). The declaration tier is the Task-6 REPLAN target if the automatic detection (6.2) proves unreliable; it lands camcge's +1 Solve regardless.

---

# Category 7: Class-B CGE `stat_pz` Coefficient Discrepancy + Cold-Convex Residue

## Unknown 7.1: Is the Class-B CGE `stat_pz` residual a single general-emit coefficient discrepancy that one fix converts across several models?

### Priority
**High** — a single general-emit fix converting several Class-B CGE models (irscge/lrgcge/moncge/stdcge/marco) is high-leverage for the genuine floor.

### Assumption
The Class-B CGE `stat_pz` residual (irscge/lrgcge/moncge/stdcge/marco) is a **single general-emit coefficient discrepancy** the harness localizes to the `stat_pz` row — so one fix in the general emit path converts several models to +Match, not five per-model fixes.

### Research Questions
1. Does the harness localize the same `stat_pz` coefficient-discrepancy row across the Class-B cluster?
2. Is the discrepancy a shared general-emit bug (one fix, several models) or per-model?
3. What is the exact coefficient the emit drops/mis-weights in `stat_pz`?
4. Which models share the identical shape (the conversion count)?

### How to Verify
Run the harness across the Class-B cluster; compare the `stat_pz` rows:
```bash
for m in irscge lrgcge moncge stdcge marco; do .venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/$m.gms 2>&1 | grep -iE "stat_pz|max_residual_row"; done
# Expect: the same stat_pz coefficient discrepancy across the cluster → one general-emit fix
```

### Risk if Wrong
- **Per-model, not shared:** the conversion count drops to 1–2 → lower genuine-floor gain; still worth the highest-residual model.

### Estimated Research Time
1.5 hours (Task 9 — the Class-B `stat_pz` patch-site trace)

### Owner
Development team (AD/emit specialist)

### Verification Results
✅ **Status:** VERIFIED — Class-B `stat_pz` gate authored (PROCEED-conditional)
**Verified by:** Task 5 (Phase 0 Acceptance Gate — new gate)
**Date:** 2026-07-05
**Findings:** Authored `docs/issues/ISSUE_classB_cge_stat_pz.md`: the Class-B cluster (irscge/lrgcge/moncge `stat_pz` rel ≈ 1.0, stdcge `stat_epsilon` 2.0, marco `stat_w` 3.3) is a **general-emit coefficient/scaling discrepancy** (the `pz` cross-terms are present, not dropped; dual transfer CONSISTENT). The gate's confirmatory test for one-fix-converts-several: irscge/lrgcge/moncge all localize to the same `stat_pz` coefficient.
**Evidence:** `ISSUE_classB_cge_stat_pz.md` §"Phase 0" (4 subsections); `COLD_CONVEX_COHORT_SURVEY.md` §4 Class B; Sprint 29 Day 12.
**Decision:** PROCEED-conditional — the payoff is genuine-floor (cold-robustness; all already warm-match, non-convex), gated on whether one general-emit coefficient fix converges the cluster (else per-model, 1–2 models). Fix-surface (Day-0 hypothesis) = the CGE output-price Jacobian-transpose coefficient in `src/kkt/`.

**Task 9 (2026-07-06) — fresh Day-0 harness re-confirms one-fix-several.** Ran `kkt_residual.py` on the cluster: **irscge** `stat_pz(MLK)` rel **1.00**, **lrgcge** `stat_pz(MLK)` rel **1.00**, **moncge** `stat_pz(BRD)` rel **1.00** — all **CASE_B**, all **dual transfer CONSISTENT**. The **identical relative residual (exactly 1.0)** across the three is the missing-unit-coefficient fingerprint → **one general-emit coefficient fix converts all three** (strong one-fix-several evidence). CASE_B (not the MS-4-at-iter-0 singular signature) confirms **NOT Walras** (Unknown 7.3) — full-rank market-clearing, stays in nlp2mcp general emit. Pinned fix-surface: the Jacobian-transpose coefficient on the `pz`-referencing cross-terms in `src/kkt/stationarity.py` / `src/ad/constraint_jacobian.py` (terms present, coefficient off by a unit factor). stdcge (`stat_epsilon` 2.0) is a probable same-path variant; marco (`stat_w` 3.3) is model-specific/separate. See `BACKLOG_FIX_SURFACE_ANALYSIS.md` Part C.

---

## Unknown 7.2: What is the disposition of the remaining cold-convex Case-c residue — Sprint-31 forcing or documented inherent non-convexity?

### Priority
**Medium** — a scoping decision; the Case-c residue either feeds the Sprint-31 forcing sprint or is documented as inherent (no further work).

### Assumption
The cold-convex Case-c residue (the cohort models from the Sprint-29 survey that neither the Sprint-29 fixes nor the Sprint-30 forcing lever recover) is a small, enumerable set whose disposition is either the Sprint-31 forcing sprint (if the P2 lever shows promise, Unknown 2.3) or a documented inherent-non-convexity list (no further nlp2mcp work).

### Research Questions
1. Which cohort models remain Case-c after the Sprint-30 forcing lever (2.3)?
2. Is the residue small enough to document as inherent, or large enough to warrant a Sprint-31 forcing sprint?
3. Does any residue model have a non-forcing path (an emit fix missed in the survey)?

### How to Verify
Enumerate the post-forcing Case-c residue; classify each:
```bash
# From COLD_CONVEX_COHORT_SURVEY.md §"Case c" minus the 2.3 recoveries; classify Sprint-31 vs documented
```

### Risk if Wrong
- **Larger residue than expected:** more Sprint-31 forcing scope; documented at Sprint-30 close either way (no lost target).

### Estimated Research Time
1 hour (Task 4 shared-payoff check + Task 9 residue enumeration)

### Owner
Development team (numerics)

### Verification Results
✅ **Status:** VERIFIED — the residue is rocket-alone; the 4 Case-c models already warm-match (no action)
**Verified by:** Task 4 (Non-Convex Forcing Strategy Survey)
**Date:** 2026-07-05
**Findings:** The cold-convex Case-c residue = {bearing, launch, mathopt3, robustlp} — all **emit-correct and already warm-matching** (`model_optimal_presolve` + `compare_objective_match`, residual ≤ 8e-6; `COLD_CONVEX_COHORT_SURVEY.md` §3) → **no action, documented inherent-non-convexity-that-warm-matches**. rocket (`model_infeasible`) is the **sole** genuinely-non-converging model, and no PATH-option configuration (via optfile) forces it (Unknown 2.1). So there is **no Sprint-30 forcing cohort** — the residue is rocket-alone.
**Evidence:** `NONCONVEX_FORCING_SURVEY.md` §3; DB buckets.
**Decision:** the 4 Case-c models need no forcing (documented); **rocket is the Sprint-31 PATH-consultation target** (2.2). No Sprint-30/Sprint-31 forcing *sprint* is warranted — a single-model (rocket) PATH-consultation suffices.

---

## Unknown 7.3: Is the Class-B CGE `stat_pz` discrepancy truly NOT Walras (distinct from the camcge Category-6 transformation)?

### Priority
**High** — if the Class-B `stat_pz` were actually a Walras degeneracy, it would fold into P6 (Epic 5), not P7 (general emit); the Sprint-29 Day-12 "NOT Walras" finding is the premise for P7 being an nlp2mcp fix.

### Assumption
The Class-B CGE `stat_pz` discrepancy is a **general-emit coefficient bug**, genuinely distinct from the camcge Walras degeneracy (Sprint 29 Day 12 confirmed NOT Walras via the harness + Jacobian rank check) — so it stays an nlp2mcp fix (P7), not an Epic-5 transformation (P6).

### Research Questions
1. Does the Class-B cluster have a full-rank market-clearing block (NOT Walras-degenerate), unlike camcge?
2. Is the `stat_pz` residual an emit coefficient discrepancy (fixable in nlp2mcp), not a structural singularity?
3. Does the Sprint-29 Day-12 harness/Jacobian evidence hold on re-check?

### How to Verify
Re-confirm the Sprint-29 Day-12 finding (harness Case + Jacobian rank):
```bash
for m in irscge lrgcge moncge stdcge; do .venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/$m.gms 2>&1 | grep -iE "verdict|CASE"; done
# Expect: Case-b general-emit (NOT the camcge structural-singularity signature)
```

### Risk if Wrong
- **Actually Walras:** the Class-B cluster folds into P6 (Epic 5) → P7 loses its nlp2mcp target; the Category-6 transformation scope widens.

### Estimated Research Time
1 hour (Task 5 gate — the Class-B `stat_pz` gate confirms NOT-Walras)

### Owner
Development team (AD/emit specialist)

### Verification Results
✅ **Status:** VERIFIED — gate confirms NOT Walras (distinct from camcge Category-6)
**Verified by:** Task 5 (Phase 0 Acceptance Gate — new gate)
**Date:** 2026-07-05
**Findings:** The Class-B `stat_pz` gate records the NOT-Walras discriminator: harness **CASE_B** + dual transfer **CONSISTENT** across the cluster (Sprint 29 Day 12), with a full-rank market-clearing block — distinct from camcge (#1330)'s structural singularity (MS-4-at-iteration-0). So the Class-B residual is an **nlp2mcp general-emit** coefficient bug (Priority 7), NOT an Epic-5 CGE transformation (Priority 6).
**Evidence:** `docs/issues/ISSUE_classB_cge_stat_pz.md` §"Phase 0" (the NOT-Walras verification bullet); `ISSUE_1330` Sprint-30 refresh (explicitly distinguishes the two).
**Decision:** the Class-B cluster stays in nlp2mcp (P7 general emit); it does not fold into the camcge Walras transformation (P6). Re-confirm the Day-12 harness/Jacobian evidence in-sprint (Day-0).

---

# Category 8: Property-Test Catalog Extension + Re-Baseline + Forcing Scaffold

## Unknown 8.1: Does the head-domain-offset shape need a new property-test fixture, and can the existing offset-alias `shape8` xfail be enabled?

### Priority
**Medium** — the property-test catalog must guard the new Sprint-30 cross-term shapes; a gap means the head-offset fix ships without a regression guard, and the already-present offset-alias xfail must flip to passing when its fix lands.

### Assumption
The `test_ad_crossterm_shapes.py` catalog already has **8** fixtures (`shape1`–`shape8`), including `shape7_offset_alias_cyclic` and `shape8_offset_alias_successor` (Category 5; `test_shape8_offset_alias_successor` is currently **xfail**). So the **head-domain-offset** shape (Category 1) is the one genuinely-missing fixture P8 adds, while the offset-alias work **enables the existing `shape8` (and `shape7`) xfail** once the fix lands — the catalog is structurally extensible (no refactor needed to add the head-offset fixture).

### Research Questions
1. Do any of the existing 8 fixtures cover the head-domain-offset shape (the offset-alias-successor shape is already `shape8`, xfail)?
2. Is `test_ad_crossterm_shapes.py` + `tests/fixtures/crossterm_shapes/` extensible by adding the one head-offset fixture, or does it need a structural change?
3. What is the minimal synthetic fixture for the head-offset shape, and does enabling the `shape8` (and `shape7`) offset-alias xfail just require removing the `@pytest.mark.xfail` once the fix lands?

### How to Verify
Review the existing fixtures (expect `shape1`–`shape8`, `shape8` xfail); confirm only the head-offset shape is absent + addable:
```bash
ls tests/fixtures/crossterm_shapes/
grep -nE "def test_shape|xfail" tests/integration/emit/test_ad_crossterm_shapes.py
```

### Risk if Wrong
- **Head-offset already covered / not extensible:** either no new fixture is needed or a small refactor is — low impact. If `shape8`/`shape7` cannot be enabled by simply dropping the xfail, the offset-alias fix is incomplete (feeds Unknown 5.2).

### Estimated Research Time
1 hour (Task 8 — the property-catalog extensibility audit)

### Owner
Development team (Tooling)

### Verification Results
✅ **Status:** VERIFIED — head-offset shape is the one missing fixture (a clean one-file add); `shape8`/`shape7` offset-alias fixtures already exist (`shape8` xfail-strict)
**Verified by:** Task 8 (Reusable-Tooling Readiness Audit)
**Date:** 2026-07-06
**Findings:** `tests/fixtures/crossterm_shapes/` has **8** fixtures (`shape1`–`shape8`); `pytest tests/integration/emit/test_ad_crossterm_shapes.py` = **7 passed, 1 xfailed**. `shape8_offset_alias_successor` is **xfail-strict** (`#1143/#1447: reverted; pending coupled distance-Jacobian fix (Sprint 30)`); `shape7_offset_alias_cyclic` **passes** as a structural-decomposition guard for the himmel16 `i++1` cyclic shape (#1146; its `2.0` numeric residual defect is noted as not assertable without a GAMS residual eval). None of `shape1`–`shape8` covers the **head-domain-offset** `nu_sb`/`lam_pr` cross-term (shape8 is the distinct Category-5 *offset-alias* successor), so the head-offset shape is the **one genuinely-missing fixture** P8 adds. The catalog is **structurally extensible** — a new fixture is a `.gms` drop + a `def test_shape9_...` using the existing `_emit`/`_stat_row` helpers (no refactor); enabling `shape8` is a one-line drop of `@pytest.mark.xfail` once the offset-alias fix lands.
**Evidence:** `ls tests/fixtures/crossterm_shapes/` (shape1–8); `pytest tests/integration/emit/test_ad_crossterm_shapes.py -q` → 7 passed, 1 xfailed; `test_ad_crossterm_shapes.py:104-134` (shape8 xfail-strict; shape7 passing); `TOOLING_READINESS_AUDIT.md` Tool 4.
**Decision:** no structural blocker — P8 adds the one head-offset fixture; `shape8` (and any residual `shape7` numeric assertion) flips to passing by removing the xfail when the #1143 offset-alias fix lands (feeds Unknown 5.2). No Day-0 extension.

---

## Unknown 8.2: Is Day-0 = Sprint 29 final (no `src/` drift), and does the genuine floor 69 carry forward correctly?

### Priority
**High** — the whole Sprint-30 target set (Solve ≥ 109, genuine floor 69 → ≥ 72) is measured against this baseline; a wrong Day-0 baseline mis-attributes every delta.

### Assumption
Sprint 30 Day 0 equals the Sprint 29 final state (no `src/`/`scripts/` drift since the Sprint 29 close, so no fresh ~4h retest is needed), the committed DB recomputes to the canonical Solve 107 / Match 92 / model_infeasible 7 / Translate 135, and the genuine floor 69 carries forward so the genuine-floor → ≥ 72 target is measured on real cold-match transitions.

### Research Questions
1. Is `git diff <S29-close-SHA>..HEAD -- src/ scripts/` empty (only planning docs landed)?
2. Does the committed DB recompute to Solve 107 / Match 92 / model_infeasible 7 (canonical 142 scope)?
3. Does the genuine-floor-69 split carry forward with the genuine-floor → ≥ 72 conversion map (robert / hhfair / polygon-himmel16 / Class-B CGE)?

### How to Verify
```bash
# Use the OLDEST match (| tail -1) — later prep commits quote "SPRINT 29 CLOSED", so `-1` (newest)
# would resolve to a docs-only review-fix commit, not the true close.
S29=$(git log --grep='SPRINT 29 CLOSED' --format=%H | tail -1)
git diff --quiet "$S29"..HEAD -- src/ scripts/ && echo "no drift → Day 0 = Sprint 29 final, reuse the committed DB, no fresh retest" || git diff --stat "$S29"..HEAD -- src/ scripts/
# Pass (exit 0 + "no drift") → Day-0 baseline holds; any output from --stat → drift, fresh retest needed
```

### Risk if Wrong
- **`src/` drift:** a fresh ~4h retest is required before Day 0; the baseline shifts and the targets re-anchor.

### Estimated Research Time
1 hour (Task 2 — the Day-0 baseline assertion + genuine-floor carry-forward)

### Owner
Sprint planning

### Verification Results
✅ **Status:** VERIFIED
**Verified by:** Task 2 (Day-0 Baseline + Genuine-Floor Re-Baseline)
**Date:** 2026-07-05
**Findings:** `git diff 68b5b4a7..HEAD -- src/ scripts/` is **empty** — no `src/`/`scripts/` drift since the true Sprint 29 close (`68b5b4a7`, "SPRINT 29 CLOSED", 2026-07-01); every commit since is docs-only (PRs #1489, #1490). The committed DB recomputes over the canonical 142-model scope (`get_candidate_models` = `convexity.status ∈ {verified_convex, likely_convex}`) to exactly **Parse 142 · Translate 135 · Solve 107 · Match 92 · Mismatch 9 · model_infeasible 7** — the Sprint 29 final headline. The genuine floor **69** carries forward (Sprint 28 genuine 68 +1 from Sprint 29's maxmin/catmix reclassification; methodology ~23), with the genuine-floor → ≥ 72 conversion map documented (robert P1 / polygon-himmel16 P5 / Class-B CGE P7 / hhfair P3). **Bonus finding:** the committed DB is byte-unchanged since the *Sprint 28* close (`2717d542`) — because Sprint 29 netted no bucket change (all headline movers REPLAN'd; the firm deliverables were genuine-floor/cold-correctness, Match-neutral) — so the Sprint-28-close DB *is* the Sprint-29-final DB.
**Evidence:** `docs/planning/EPIC_4/SPRINT_30/BASELINE_METRICS.md` §0–§3 (git-diff drift check, canonical recompute, per-target bucket table).
**Decision:** **reuse the committed DB — no fresh ~4 h retest.** Day-0 = Sprint 29 final. ⚠️ **Latent-snippet finding** (recorded in `BASELINE_METRICS.md` §0 for Task 8/Task 10): the `git log --grep='SPRINT 29 CLOSED' -1` auto-derive now resolves to a docs-only PR-#1490 review-fix commit (`7a2d30e3`), not the true close (`68b5b4a7`), because prep commit bodies quote the phrase — drift *result* is identical (all-docs in between) but the reported SHA is misleading; use the pinned SHA or `git log --grep='SPRINT 29 CLOSED' --format=%H | tail -1` (oldest match).
**Day-0-bucket contribution to other unknowns:** confirmed each Sprint-30 target is still in its gating bucket at Day 0 — **mine** + **rocket** + **camcge** `model_infeasible` (feeds 1.1 / 2.1 / 6.1); **hhfair** `model_optimal` + **mismatch** 72.147 vs 87.159 (feeds 3.1); **robert** `model_optimal_presolve` + match 11025.0 (P1 genuine-floor candidate); **sarf** `translate_failure` (feeds 4.1); **polygon**/**himmel16** + the Class-B cluster `model_optimal_presolve` + match (methodology). Their *fix-surface* aspects remain to be verified by Tasks 3/4/5.

---

## Unknown 8.3: Does the solution-forcing harness scaffold provide a stable entry point the Sprint-31 PATH-consultation sprint inherits?

### Priority
**Low** — a forward-looking infrastructure question; a rough scaffold is still usable by Sprint 31, just less polished.

### Assumption
The solution-forcing harness scaffold built in P8 (from the P2 forcing lever, Category 2) provides a stable, documented entry point that the renumbered **Sprint 31** (PATH-author consultation + forcing) inherits — so the forcing work compounds across sprints rather than being rebuilt.

### Research Questions
1. What is the minimal stable interface for the forcing scaffold (a lever-injection hook + a MODEL STATUS reporter)?
2. Does the Sprint-31 PATH-consultation work plug into it, or need a different shape?
3. Is the scaffold documented enough to hand off?

### How to Verify
Sketch the scaffold interface against the Sprint-31 PATH-consultation scope:
```bash
grep -rn "Sprint 31\|PATH consultation\|forcing scaffold" docs/planning/EPIC_4/PROJECT_PLAN.md | head
```

### Risk if Wrong
- **Unstable interface:** Sprint 31 reworks the scaffold — minor rework, not a lost target.

### Estimated Research Time
0.5 hours (Task 8 — the forcing-scaffold entry-point sketch)

### Owner
Development team (Tooling)

### Verification Results
✅ **Status:** VERIFIED — the stable entry point is a lever-injection hook + a MODEL-STATUS reporter around the MCP solve
**Verified by:** Task 8 (Reusable-Tooling Readiness Audit) — building on the Task-4 forcing survey
**Date:** 2026-07-06
**Findings:** The Task-4 `NONCONVEX_FORCING_SURVEY.md` §4 already defined the P8 scaffold's stable interface: a `--force <strategy>` emit mode (or driver template) that wraps `Solve mcp_model using MCP;` in one of {homotopy/continuation loop, multi-start `.l`-perturbation loop, emitted PATH `optfile`} + a **MODEL-STATUS reporter**. The **minimal stable hook** Sprint 31 inherits = the lever-injection point around the MCP solve + the status reporter; the **strategy is a parameter**, so the Sprint-31 PATH-consultation work (a `proximal_perturbation`/`merit_function` schedule via the emitted optfile) plugs into the *same* hook without reshaping it. Sprint 30 P8 builds + validates this scaffold on rocket (it *runs* the levers, per Task 4); Sprint 31 adds strategies. No new tooling audit gap — this is a design-forward confirmation that the P8 entry point is stable enough to hand off.
**Evidence:** `NONCONVEX_FORCING_SURVEY.md` §4 (the P8 scaffold entry point + the Sprint-31 hand-off scope); `REPLAN_RISK_ASSESSMENT.md` Track B (rocket PROCEED-to-scaffold); `TOOLING_READINESS_AUDIT.md` (forcing-scaffold row).
**Decision:** the scaffold interface (lever-injection hook + MODEL-STATUS reporter, strategy-as-parameter) is stable and documented for the Sprint-31 PATH-consultation inheritance; no rework expected. Feeds Task 10 (schedule the P8 scaffold build).

---

## Unknown 8.4: Is the Sprint-29-built `--resolve-changed` + PR25 re-baseline discipline the standing Day-0 baseline mechanism (no rebuild)?

### Priority
**Low** — a reuse-confirmation; the tooling exists, this only confirms it applies unchanged to Sprint 30.

### Assumption
The Sprint-29 Priority-8 deliverables (`--resolve-changed` checkpoint re-solve + the PR25 re-baseline step) are the **standing** Day-0 baseline + checkpoint mechanism for Sprint 30 — reused unchanged, not rebuilt — so the Task-2 baseline and the Day-5/Day-10 checkpoints inherit them directly.

### Research Questions
1. Is `--resolve-changed` present on `main` and functional for the Sprint-30 changed-golden set?
2. Does the PR25 re-baseline step apply to the genuine-floor-69 → ≥ 72 measurement unchanged?
3. Are the checkpoint inputs (`changed_emit_artifacts.py --since-commit`) still the correct at-risk-list source?

### How to Verify
```bash
grep -rn "resolve-changed\|resolve_changed" scripts/ | head
test -f scripts/sprint_audit/changed_emit_artifacts.py && echo "changed-artifact diff present"
```

### Risk if Wrong
- **Tooling drift:** a small fix before Day 0 — minimal impact.

### Estimated Research Time
0.5 hours (Task 8 — the `--resolve-changed` / re-baseline reuse confirmation)

### Owner
Development team (Tooling)

### Verification Results
✅ **Status:** VERIFIED — `--resolve-changed` present on `main`, covers the Sprint-30 changed-golden set unchanged
**Verified by:** Task 8 (Reusable-Tooling Readiness Audit)
**Date:** 2026-07-06
**Findings:** `run_full_test.py --resolve-changed --since-commit <SHA>` is present on `main` (Sprint-29 Priority 8). It defines `_GOLDEN_SUFFIXES = ("_mcp_presolve.gms", "_mcp.gms")` (longest-first) and `_changed_golden_model_ids(since_commit)` git-diffs `<SHA>..HEAD` for changed goldens of **either** suffix — so the changed-golden set surfaces **both** the Sprint-30 **widened-VARIABLE presolve** regen (hhfair `_mcp_presolve.gms`, P3) **and** the **head-offset cold** regen (mine/robert `_mcp.gms`, P1); `run_resolve_changed` re-solves each and diffs its bucket vs the committed DB, exiting **NO-GO** on any backward move. `changed_emit_artifacts.py --since-commit <Day-0 SHA> --format json/markdown` is the same at-risk list for the Day-5/Day-10 checkpoint. The PR25 re-baseline step applies unchanged to the genuine-floor-69 → ≥ 72 measurement (a post-methodology re-measure, tool-independent).
**Evidence:** `scripts/gamslib/run_full_test.py:1043-1229` (`--resolve-changed`, `_GOLDEN_SUFFIXES`, `_changed_golden_model_ids`, `run_resolve_changed`); `scripts/sprint_audit/changed_emit_artifacts.py` present; `TOOLING_READINESS_AUDIT.md` Tool 3.
**Decision:** reuse unchanged — no rebuild. The Task-2 baseline + the Day-5/Day-10 checkpoints inherit `--resolve-changed` directly; it covers both Sprint-30 golden kinds.

---

## Template for New Unknowns

```markdown
## Unknown X.Y: [Title / Question]

### Priority
**[Critical/High/Medium/Low]** - [Brief reason]

### Assumption
[The assumption being made]

### Research Questions
1. [Question 1]
2. [Question 2]
...

### How to Verify
[Test cases, experiments, or analysis to validate the assumption]

### Risk if Wrong
[Impact on the sprint if the assumption is incorrect]

### Estimated Research Time
[Hours] ([brief description of research activities])

### Owner
[Team/Person responsible]

### Verification Results
🔍 **Status:** INCOMPLETE
```

---

## Next Steps

> **⏳ PREP PHASE IN PROGRESS (Task 1 complete, 2026-07-04).** All **25** prep-time unknowns are authored and currently **🔍 INCOMPLETE**; they are verified during prep Tasks 2–10 (see §"Appendix: Task-to-Unknown Mapping"). This is the Task-1 deliverable — the risk-identification foundation for the rest of the Sprint 30 prep. As each downstream task lands, its unknowns move 🔍 INCOMPLETE → ✅ VERIFIED (or ❌ WRONG with a correction), and this note is updated. Sprint 30 is **GO for Day 0** once all Critical + High unknowns are VERIFIED (Task 10).

**Before Sprint 30 Day 1:**
1. Review all Critical and High priority unknowns (16 total: 6 Critical + 10 High).
2. Execute verification tests for the top unknowns via prep Tasks 2–10 (see §"Appendix: Task-to-Unknown Mapping").
3. Update this document with findings (🔍 INCOMPLETE → ✅ VERIFIED or ❌ WRONG).
4. Adjust Sprint 30 scope (PROJECT_PLAN.md or PLAN.md) if major assumptions are wrong — specifically, any of Unknowns 1.1, 1.2, 2.1, 3.1, 6.1, 6.2 returning WRONG triggers a Priority re-plan / REPLAN-to-Sprint-31 decision during prep (Task 6).
5. Share findings with the team during sprint planning (Task 10).

**During Sprint 30:**
1. Reference this document daily (especially Critical / High unknowns).
2. Add newly discovered unknowns using the template above.
3. Update verification results as features are implemented.
4. Move resolved items to "Confirmed Knowledge" post-sprint.

---

## Appendix: Task-to-Unknown Mapping

This table shows which Sprint 30 prep tasks verify which unknowns. Prep Task 10 (Plan Sprint 30 Detailed Schedule) integrates all verified unknowns into the 14-day execution schedule.

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Day-0 Baseline + Genuine-Floor Re-Baseline | 8.2 | Confirms Day-0 = Sprint 29 final (no `src/` drift) + the committed-DB canonical tally + the genuine-floor-69 carry-forward (8.2); the per-target "still in its bucket at Day 0?" check contributes to 1.1 / 2.1 / 3.1 / 6.1 |
| Task 3: Head-Offset Architecture Design + robert Minimal Reproduction | 1.1, 1.2, 1.3, 1.4 | Hand-derives robert's head-offset cross-term + dual-transfer index map with residual → 0 (1.4); designs the 3-site coordination (1.2); validates the robert → mine generalization (1.1); resolves the cold-LCP-consistency question (1.3) |
| Task 4: Non-Convex Forcing Strategy Survey | 2.1, 2.2, 2.3, 7.2 | Surveys the forcing levers + prototype-probes rocket (2.1), sets the nlp2mcp/PATH boundary (2.2), checks the cold-convex Case-c shared payoff (2.3), and enumerates the post-forcing Case-c residue (7.2, with Task 9) |
| Task 5: Refresh + Author Phase 0 Acceptance Gates | 1.2, 1.3, 2.2, 3.1, 3.2, 4.1, 5.2, 6.1, 7.1, 7.3 | Each gate frames its fix-surface as a Day-0 hypothesis (PR24) + cites `kkt_residual.py` (PR27): the head-offset gate (1.2, 1.3), the rocket-forcing exit (2.2), the hhfair `$184` correction + CES verdict (3.1, 3.2), the #1385 sarf gate (4.1), the offset-alias localized-vs-architectural gate (5.2), the camcge Walras gate (6.1), and the new Class-B `stat_pz` gate (7.1, 7.3 NOT-Walras) |
| Task 6: Diagnosis-Heavy / REPLAN-Prone Risk Assessment (PR16) | 1.1, 1.2, 2.1, 2.2, 6.1, 6.2 | The three REPLAN-prone deep tracks — mine multi-site (1.1, 1.2), rocket forcing (2.1, 2.2), camcge Epic-5 (6.1, 6.2) — each get a PROCEED/REPLAN signal + Sprint-31 exit + budget reallocation |
| Task 7: camcge → Epic 5 Walras Transformation Design | 6.1, 6.2, 6.3 | Designs the empirical-confirmation experiment (6.1), the degeneracy-detection heuristic + false-positive guard (6.2), and the redundant-row + numéraire-selection rule (6.3) |
| Task 8: Reusable-Tooling Readiness Audit | 1.4, 8.1, 8.3, 8.4 | Validates the harness dual-transfer on robert's `nu_sb` head-offset multiplier (1.4), audits the property-catalog extensibility for the new shapes (8.1), sketches the forcing-scaffold entry point (8.3), and confirms the `--resolve-changed` + re-baseline reuse (8.4) |
| Task 9: Backlog Fix-Surface Analysis | 3.3, 4.1, 4.2, 5.1, 5.2, 5.3, 7.1 | The #1385 sarf emit-site + instance-count (4.1, 4.2), the offset-alias Day-5 revert coupling + coordinated fix + blast radius + property fixtures (5.1, 5.2, 5.3), the hhfair widened-VARIABLE blast radius (3.3), and the Class-B `stat_pz` patch-site (7.1) |
| Task 10: Plan Sprint 30 Detailed Schedule | (integrates all) | Sprint 30 14-day schedule + day-by-day prompts; absorbs the PROCEED/REPLAN decisions from Tasks 5/6, the head-offset design from Task 3, the forcing survey from Task 4, and the infra designs from Tasks 7/8 |

**Cross-cutting unknowns** (verified across multiple prep tasks):

- **Unknown 1.1** (robert → mine generalization) — Task 3 validates it on paper (the head-offset design), Task 6 makes the PROCEED/REPLAN decision (mine one-fix vs robert-then-mine split), and Task 2 confirms mine is still `model_infeasible` + robert genuine-floor at Day 0.
- **Unknown 1.2** (3-site budget) — Task 3 traces the sites + prototypes Site 2, Task 5 gates the fix-surface, and Task 6 makes the budget/REPLAN call.
- **Unknown 2.1 / 2.2** (rocket forcing lever + PATH boundary) — Task 4 surveys + probes, Task 5 gates the exit, Task 6 makes the PROCEED (in-GAMS lever) vs Sprint-31 (PATH-option) decision.
- **Unknown 6.1 / 6.2** (camcge empirical + detection heuristic) — Task 7 designs both, Task 5 gates the transformation, Task 6 judges the detection reliability for the PROCEED/REPLAN decision.
- **Unknown 7.1 / 7.3** (Class-B `stat_pz` shared fix + NOT-Walras) — Task 9 traces the patch site, Task 5 authors the gate confirming NOT-Walras (distinct from the Category-6 camcge transformation).
- **Unknown 8.2** (Day-0 baseline + genuine floor) — Task 2 establishes it, and every Sprint-30 target delta is measured against it.

**Coverage:** All 25 Sprint 30 prep-time unknowns are assigned to at least one prep task. Each Critical and High-priority unknown is assigned to the task that will act on its findings (e.g., Task 6 verifies the diagnosis-heavy Category 1/2/6 Criticals AND its findings drive Task 10's schedule allocation + the Sprint 31 REPLAN exits).

**Carryforward from Sprint 29** (now informing Sprint 30 prep):
- All 28 Sprint 29 prep unknowns were VERIFIED (see `docs/planning/EPIC_4/SPRINT_29/KNOWN_UNKNOWNS.md` §"Next Steps"). Three INVERTED and became the parents of Sprint-30 categories: Sprint-29 Unknown 1.1 (mine distributed multi-site → Category 1), Unknown 2.2 (rocket intrinsic non-convergence → Category 2), and Unknown 5.1 (CGE cohort distinct degeneracies → camcge sole Walras case Category 6 + Class-B `stat_pz` separate general-emit Category 7). The Sprint 30 unknowns are net-new, derived from the six carryforwards + the two backlog priorities + the infrastructure track.

---

**Document Created:** 2026-07-04
**Last Updated:** 2026-07-04
**Total Unknowns:** 25
**Owner:** Sprint 30 Planning Team
**Review Frequency:** Daily during Sprint 30
