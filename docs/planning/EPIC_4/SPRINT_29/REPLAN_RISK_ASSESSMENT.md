# Sprint 29 — Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (PR16)

**Task:** Sprint 29 Prep Task 5 (design-only — the validations are *run* in-sprint, Day 0/1)
**Date:** 2026-06-26
**Method:** PR16 single-model hypothesis-validation — a Day-0 `kkt_residual.py` trace + an optional env-guarded prototype-then-revert probe on one representative scenario per track, **zero `src/` diff**, deciding PROCEED (Sprint 29 implementation) vs REPLAN (Sprint 30 / Epic 5 re-scope) on evidence **before** the sprint commits the combined budget.
**Instrument:** the KKT-residual harness (`scripts/diagnostics/kkt_residual.py`) + targeted code traces. The Task-4 Phase-0 gates already produced the Day-0 harness verdicts cited below.
**Why:** Sprint 27–28 showed deep AD/non-convex/presolve fixes routinely prove multi-bug — cclinpts was implemented and *reverted*, kand's first hypothesis was proven *inert*, camcge is an inherent singular Jacobian. The three tracks here are the Sprint-29 successors with the same REPLAN-prone tails: each carries a Task-4 gate that **explicitly deferred its PROCEED/REPLAN decision to this task**.

> **Scope note.** Two of the three tracks are already harness-**Case b** (mine, the offset-alias pair); rocket is Case b on `stat_step` but non-convex. So the REPLAN question here is **not** the usual Case-b-vs-Case-c emit-bug discriminator — it is the **fix-shape** question: is the confirmed emit bug a *localizable single-site* fix that fits the per-priority budget (PROCEED), or a *distributed / architectural* re-derivation that should hand to Sprint 30 / Epic 5 (REPLAN)?

---

## Track A — #1443 mine (Priority 1): single-site head-offset fix vs distributed multi-site re-derivation

**Decision pivot (Unknown 1.1):** does mine's cold MS-5 localize to the **head-offset dual-transfer** (one fix surface → PROCEED), or is it **distributed across `comp_*`/bound rows** (a multi-site head-domain-offset re-derivation that exceeds the ~10–16h Priority-1 budget → Sprint-30 REPLAN)? **mine is a convex LP** (Unknown 1.3 — monotone LCP, no spurious local optima), so there is **no Case-c "non-convexity" escape**: cold infeasibility *is* an emit bug. The REPLAN question is therefore **budget/architecture, not Case-b-vs-Case-c**.

**Binding Sprint 28 Day-4 record:** the `stat_x` cross-term *formula* landed and is correct against `comp_pr`'s body, but the cold MCP is still MS-5 (`x → 4e10`) with **49 INFES spread across `comp_pr`, `comp_lo_x`, `comp_up_x`, `stat_x`, `def`** — not localized to stationarity. The Day-4 time-boxed probe found **no single `lam_pr` sign×alignment variant zeroes the residual** (best 1.6e4); with the principled `l+1` alignment, **22 of 30 `stat_x` cells** remain systemic ("round" multiples of ~500 = mis-aligned dual contributions). The fix is a **coordinated re-derivation of the head-offset index map across three emit sites** — (1) `comp_pr` emission, (2) the `--nlp-presolve` dual transfer (`src/emit/emit_gams.py` `_emit_nlp_presolve`, ~line 1281, `lam_<eq>.l = abs(<eq>.m)`), (3) the (landed) `stat_x` cross-term — **plus** the cold-start LCP consistency. The Day-4 verdict (on that day's remaining ~2h probe budget): *not a confident fix in the time available* — and for Sprint 29 the PROCEED test is whether the coordinated 3-site re-derivation fits the **~10–16h Priority-1 budget** (the figure used throughout this assessment).

### Single-model validation design (PR16 — Day-0, zero `src/` diff)

| Step | Action | Output |
|---|---|---|
| A1 | `kkt_residual.py data/gamslib/raw/mine.gms` — read the verdict + max-residual row + dual-transfer self-check (already Day-0: **Case b**, `stat_x('4','1','1')` rel 1.33, transfer **consistent**) | confirms a localizable stationarity row, not a bound-row residual |
| A2 | **Cold-INFES cross-check:** generate `mine_mcp.gms`, solve cold, and map the 49 INFES rows by prefix — are they dominated by `stat_x` (single-site, PROCEED) or spread across `comp_pr`/`comp_lo_x`/`comp_up_x` (distributed, REPLAN)? | an INFES-by-row-type histogram |
| A3 | **3-site coherence probe (env-guarded, revert):** apply the `l+1`/`±li`/`±lj` index map at all three sites simultaneously, warm-start, and measure whether the cold LCP reaches MS-1 (or the residual drops monotonically) | does a *coordinated* fix converge, or does each site expose the next? |

### Recommendation: **conditional — lean REPLAN-aware**

- **PROCEED to a Sprint 29 fix** if A2 shows the INFES is **dominated by `stat_x`/`pr` rows** *and* A3's coordinated 3-site map drives the cold LCP to MS-1 within the ~10–16h budget. The fix lands atomically across the three sites (a partial fix = no Solve gain).
- **REPLAN to Sprint 30** if A2 shows the INFES is **distributed across `comp_*`/bound rows** *or* A3 shows each site fixed only exposes the next (architectural head-domain-offset re-derivation). File a re-scoped Phase-0 successor targeting the **head-domain-offset emit architecture** (the `comp_pr`/`lam_pr`/`stat_x`/bound index-map as one workstream) — still Case b, just bigger than one sprint-day.
- **Deciding signal:** A2's INFES-row histogram + A3's coordinated-fix convergence.
- **Budget at risk:** ~10–16h (Priority 1); the **firm +1 Solve** is conditional on PROCEED.
- **Prior-probability note:** the Day-4 evidence (49 INFES across 5 row types; 22/30 `stat_x` systemic; no single-tweak fix) raises the prior of the **distributed/architectural** outcome → the Task-10 lower bound should assume mine may slip to Sprint 30.

---

## Track B — #1462 rocket (Priority 2): localizable `piL/piU`-at-`h0` fix vs intrinsic non-convergence

**Decision pivot (Unknown 2.2):** after the `_fx_`-multiplier warm-start, is the residual MS-5 the **localizable `piL/piU`-at-`h0` bound-complementarity** introduced by the #1449 Layer-4 unfix (Case b → PROCEED), or **intrinsic non-convex convergence** that the warm-start cannot fix (Case c → Sprint-30 forcing)? Unlike mine, **rocket is non-convex**, so the Case-c exit is *live*.

**Binding Sprint 28 Day-13 record:** the `_fx_`-at-`h0` warm-start (`nu_*_fx_h0.l = <var>.m('h0')`) is **necessary but not sufficient** — it moves the objective **1.137 → 1.016** but **MS-5 persists**. Day-0 harness: **Case b**, `max_residual_row = stat_step`, rel **0.497**, transfer consistent. The hypothesized mechanism (#1462): the Layer-4 unfix relaxes `v/ht/m('h0')` bounds, so `v('h0')=0` sits at the *relaxed* lower bound → a degenerate bound-complementarity activation.

### Single-model validation design (PR16 — Day-0, zero `src/` diff)

| Step | Action | Output |
|---|---|---|
| B1 | `kkt_residual.py data/gamslib/raw/rocket.gms` — read verdict + max-residual row (Day-0: **Case b**, `stat_step` 0.497) | localizable stationarity residual confirmed |
| B2 | **Complete the `_fx_` warm-start probe (env-guarded):** inject `nu_<var>_fx_h0.l = <var>.m('h0')` for **all** of ht/v/m, re-solve, read MODEL STATUS + objective | does a *complete* warm-start (vs the partial Day-13 one) clear MS-5, or does it persist? |
| B3 | **Degenerate-bound suppression probe (env-guarded, revert):** emit rocket presolve with the Layer-4 unfix suppressed for elements whose fixed value equals the relaxed bound (`v('h0')=0`); solve; check MS + `piL_v('h0')`/`comp_lo_v('h0')` residuals | does suppressing the degenerate unfix clear MS-5 (Case b) or not (Case c)? |

### Recommendation: **conditional — lean REPLAN-aware**

- **PROCEED to a Sprint 29 fix** if B3's degenerate-bound suppression (or a `piL/piU`-at-`h0` transfer correction) drives rocket to MS-1 with `compare_objective_match`. The general `_fx_`-multiplier warm-start lands regardless (sprint-wide presolve robustness).
- **REPLAN to Sprint 30 forcing** if, after a **complete** `_fx_` warm-start (B2) **and** the bound-complementarity fix (B3), MS-5 persists with a clean residual → the remaining gap is **intrinsic non-convex convergence** (trust-region / homotopy / multi-start), not an emit bug.
- **Deciding signal:** whether B2+B3 (complete warm-start + degenerate-bound fix) reach MS-1, or MS-5 persists with clean residuals.
- **Budget at risk:** ~8–14h (Priority 2). **The general `_fx_` warm-start (presolve robustness) lands either way; only rocket's +1 Solve/+1 Match is at risk.** **Hard constraint:** the warm-start must not regress the Layer-4-unfix presolve set (`grep -l "#1449 (Layer 4)" data/gamslib/mcp/*_mcp_presolve.gms 2>/dev/null || true`) or the full presolve golden set.
- **Prior-probability note:** the warm-start being known-necessary-but-insufficient + rocket's non-convexity raises the prior of the **Case-c (intrinsic)** outcome → Task-10 lower bound should assume rocket's match may slip; the presolve-robustness deliverable is the firm part.

---

## Track C — #1111/#1112 offset-alias (Priority 7): localized cross-term vs alias-aware-AD redesign

**Decision pivot (Unknown 7.2):** is the himmel16/polygon offset-alias gradient defect a **localized AD cross-term correction** (property-test-guardable → PROCEED), or does it require the **#1111 alias-aware-differentiation / #1112 dollar-condition-propagation redesign** (architectural → Sprint-30 / Epic-5 REPLAN)?

**Binding Day-0 record (Task 3/4):** both models **already match warm** and are harness-**Case b** on a *single* `stat_*` row — himmel16 `stat_area` rel **2.000** (the GAMS circular-lead operator `i++1` — successor that wraps at the set boundary, per `himmel16.gms`; intermediate-var `nu_areadef - nu_obj2` cross-term), polygon `stat_theta` rel **0.492** (`ord(j)=ord(i)+1` successor, offset-image cross-term). The **integer residual (2.0)** on himmel16 is the fingerprint of a *missing unit-coefficient cross-term* — a localizable signature. Both route through the same code: `src/ad/derivative_rules.py` (`_partial_collapse_sum`, `_diff_varref` with `circular=True`) + `src/kkt/stationarity.py` (`_replace_indices_in_expr`). **The fix is Match-neutral cold-robustness** (both already match warm), so this track lifts the *genuine floor*, not the headline Match.

### Single-model validation design (PR16 — Day-0, prototype-then-revert)

| Step | Action | Output |
|---|---|---|
| C1 | `kkt_residual.py` on himmel16 + polygon — confirm the single-row Case-b residual (Day-0: 2.000 / 0.492) | both localizable to one `stat_*` row |
| C2 | **Localized-fix prototype (env-guarded, revert):** correct the offset-alias cross-term in `_partial_collapse_sum`/`_diff_varref` *for the cyclic/successor shape only*; re-emit himmel16+polygon; does the residual → 0 **without** touching the alias-aware-differentiation core (#1111) or dollar-condition propagation (#1112)? | a gateable/not-gateable verdict |
| C3 | **Blast-radius scan:** byte-diff the full corpus + run the AD cross-term property-test catalog (`tests/integration/emit/test_ad_crossterm_shapes.py`) against the prototype | how many models/fixtures the localized fix touches |

### Recommendation: **PROCEED-with-condition** (lean PROCEED — localizable signature)

- **PROCEED to a Sprint 29 fix** if C2's localized cross-term correction fixes himmel16+polygon (residual → 0, cold match) **without** modifying the #1111 alias-aware-differentiation core or requiring #1112 dollar-condition propagation, **and** C3 shows a contained blast radius. **Requires a new property-test fixture** for the offset-alias shape (Unknown 7.3 — not yet in the shapes-1–6 catalog).
- **REPLAN to Sprint 30 / Epic 5** if C2 shows the correction must thread through the **alias-aware-differentiation core (#1111)** or **dollar-condition propagation (#1112)** — i.e. it cannot be gated to the cyclic/successor shape without changing general alias differentiation. File the AD-engine architecture track.
- **Deciding signal:** C2's gateable-vs-core verdict + C3's blast radius.
- **Budget at risk:** ~12–18h (Priority 7); the gain is **genuine-floor (cold-robustness), not headline Match** — so a REPLAN here costs *genuine-floor lift*, not the as-measured Match target.
- **#1111/#1112 scope (Unknown 7.4):** the architectural backstop currently has a **small, contained footprint** — 3 open issues trace to #1111 (**#1146 himmel16, #1143 polygon, #1162**), and #1112 (dollar-condition propagation) backs the conditioned-sum cases (e.g. sambal/qsambal #1239's `$xw(i,j)`). It is a **Sprint-30 candidate, not an Epic-5 necessity**, and is scoped *only if* the localized fix (C2) fails. The integer-residual signature makes PROCEED the more likely outcome.

---

## Budget-at-Risk Tally (feeds Task 10's schedule lower bound)

| Track | Priority | Budget | At-risk condition | Firm part (lands either way) | Prior probability of REPLAN |
|---|---|---|---|---|---|
| #1443 mine | 1 | ~10–16h | INFES distributed / multi-site head-offset re-derivation (architectural) | — (the whole +1 Solve is conditional) | **Medium-High** — Day-4: 49 INFES/5 row types, 22/30 stat_x systemic, no single-tweak fix |
| #1462 rocket | 2 | ~8–14h | intrinsic non-convex convergence after complete warm-start + bound fix | **the general `_fx_` warm-start (presolve robustness)** | **Medium-High** — warm-start known-necessary-but-insufficient + non-convex |
| #1111/#1112 offset-alias | 7 | ~12–18h | fix must thread the alias-aware-AD core / dollar-condition propagation | a property-test fixture + the diagnosis | **Low-Medium** — integer-residual single-row signature leans localizable |
| **Combined** | 1, 2, 7 | **~30–48h** | — | rocket presolve robustness + the P7 diagnosis/fixture | **Task 10 lower-bound schedule should assume mine + rocket's *match/solve* may slip; their firm parts and P7 land** |

**Reallocation plan per REPLAN:**
- **#1443 mine REPLAN** → the freed ~10–16h pre-allocates to the **cold-convex Case-b cohort (Priority 4)** — the Task-3 survey found 21 Case-b models (a deep, low-risk, shared-fix-class backlog) that absorb budget productively as genuine-floor lift.
- **#1462 rocket REPLAN** → the warm-start (firm) still lands; the freed rocket-specific ~4–8h pre-allocates to **Priority 6 hhfair (#1236)** — the only live objective-mismatch +Match target (gated on its residual-emit compile fix).
- **#1111/#1112 offset-alias REPLAN** → the freed ~12–18h pre-allocates to the **objective-mismatch cohort (Priority 6)** + additional **cold-convex Case-b (Priority 4)** genuine-floor conversions; the AD-engine architecture track is filed for Sprint 30.

The Task-10 schedule's **lower bound** assumes Priorities 1/2 *match/solve* slip to Sprint 30 (firm parts: rocket presolve robustness + the P7 fix/diagnosis land); the **upper bound** assumes all three PROCEED. The headline **Solve ≥ 109** depends on **both** mine and rocket PROCEEDing — so the Solve target is the most REPLAN-sensitive KPI; the **Match ≥ 92 maintain** is robust (the cold-convex/offset-alias work is genuine-floor, not as-measured Match).

## Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_29/REPLAN_RISK_ASSESSMENT.md && echo present
grep -Ei 'PROCEED|REPLAN' docs/planning/EPIC_4/SPRINT_29/REPLAN_RISK_ASSESSMENT.md | head
grep -Ei '#1443|mine|#1462|rocket|#1111|#1112|offset-alias' docs/planning/EPIC_4/SPRINT_29/REPLAN_RISK_ASSESSMENT.md | head
```
