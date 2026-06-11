# Priority 4/5/6 — Diagnosis-Heavy Track REPLAN Risk Assessment (PR16)

**Task:** Sprint 28 Prep Task 6 (design-only — the validations are *run* in-sprint, Day 0/1)
**Date:** 2026-06-11
**Method:** PR16 single-model hypothesis-validation — an env-guarded prototype / trace on one representative scenario per track, **zero `src/` diff**, deciding PROCEED (Sprint 28 implementation) vs REPLAN (Sprint 29 re-scope) on evidence **before** the sprint commits the combined budget.
**Instrument:** the KKT-residual harness (Task 4, `PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md`) + targeted code traces.
**Why:** Sprint 27 showed deep AD/CGE fixes routinely prove multi-bug — cclinpts was implemented and *reverted* (Day 6), kand's first hypothesis was proven *inert* (Day 5), camcge is a singular Jacobian that may be *inherent*. Committing ~28–46h to all three without a pre-sprint validation risks the "partial progress, rest deferred" drift the sprint is built to avoid.

---

## Track A — #1387 cclinpts (Priority 4): anchor fix *architectural* vs *local*

**Decision pivot (Unknown 4.1):** is the gradient→stationarity **re-symbolization anchor** fix architectural (touches all re-symbolization callers) or local (gateable to the pure-offset case)?

**Binding Sprint 27 Day-6 record:** the fix is **three coupled changes**, not one — (1) AD `_diff_sum` offset-enumeration (the `j+1` cross-terms; **done + residual-verified**, max|r| = 5e-8 at the NLP optimum), (2) the re-symbolization-anchor fix (the **revert blocker**: a pure-offset `δ=-1` term, having no reference to the column index, was anchored on the wrong element `s11` not `s10`, cancelling the diagonal → cclinpts *worse*), (3) a non-convex warm-start. The "sign-flip" framing is a **MISDIAGNOSIS** (the outer `(-1)` is the standard maximize negation, `src/ad/gradient.py:265`) — do **not** touch sign logic.

### Single-model validation design (PR16 — do not implement)

| Step | Action | Output |
|---|---|---|
| A1 | Re-run the Day-6 `_diff_sum` offset-enumeration prototype on current `main` (env-guarded, zero `src/` diff) | confirm the anchor blocker still reproduces (cclinpts byte-identical / worse) |
| A2 | **Trace the re-symbolization callers** — how many call sites would a correct anchor change touch? Can the anchor be selected from the *differentiated variable's own column index* in a gated branch, or is it chosen upstream of any per-term context (Unknown 4.1 Q1/Q2)? | a caller count + a gateable/not-gateable verdict |
| A3 | KKT-residual harness eliminated-KKT check (`objgrad_b(j) + b(j)^(-γ)*objgrad_fb(j) = 0`, max|r| <= 1e-6) on the prototype | re-confirm the cross-term shape (Case c expected: residual clean, cold PATH diverges → warm-start needed) |

### Recommendation: **PROCEED-with-condition**

- **PROCEED to Sprint 28** if A2 shows the anchor fix is **gateable to the offset case** (local — anchors on the differentiated variable's column index without changing non-offset re-symbolization). All three coupled changes land together (a partial fix = no Match gain).
- **REPLAN to Sprint 29** if A2 shows the anchor is chosen **upstream of per-term context / touches all callers** (architectural).
- **Deciding signal:** the A2 caller trace — local vs architectural anchor selection.
- **Budget at risk:** ~12–18h (Priority 4).
- **Sprint 29 re-scope path:** file a re-scoped Phase-0 successor targeting the re-symbolization **architecture** (all callers) as its own workstream, separate from the per-model cclinpts AD-enumeration + warm-start (which can land independently once the anchor is sound).

---

## Track B — #1390 kand (Priority 5): localizable row vs LP-recourse architecture

**Decision pivot (Unknown 5.1):** does the 195.0-vs-2613.0 gap localize to a specific stationarity/complementarity row (PROCEED), or is it LP first-stage/recourse-coupling architecture (REPLAN)? **The phantom-term collapse is proven inert (Sprint 27 Day 5) and is explicitly OUT OF SCOPE.**

### Single-model validation design (PR16 — Day-0 trace plan)

| Step | Action | Output |
|---|---|---|
| B0 | **NLP-reference check (Unknown 5.3):** standalone kand NLP solve; confirm `2613.0` deterministically; check global-vs-local (multiple optima?) | a reliable warm-start target (or a corrected reference) |
| B1 | **Dual-transfer consistency self-check (Unknown 5.2):** harness loads the NLP `dembalx` marginals into the `tree(nn,n)`-conditioned `lam_dembalx`; verify the *constraint* rows ≈ 0 **first** | trust (or `dual_transfer_inconsistent`) before any verdict |
| B2 | **Case-(b/c) localization (Unknown 5.1):** run the harness at the NLP KKT point | the max-residual row + verdict |

**Verdict interpretation:** **Case b** (a `stat`/`comp` row exceeds tol — e.g. `bal(j,t,n)`/`x` stationarity or the `t-1`↔`t+1` lag duality) ⇒ a **localizable** emit row → PROCEED. **Case c** (all residuals ≈ 0 but cold PATH lands at 195.0) ⇒ the gap is **non-convexity / LP first-stage-recourse coupling**, not an emit bug → REPLAN.

### Recommendation: **diagnosis-first / conditional (lean REPLAN-aware)**

- **PROCEED to a Sprint 28 fix** only if B2 reports **Case b** with a concrete localizable row (the Traced Fix-Surface).
- **REPLAN to Sprint 29** if B2 reports **Case c** (LP-recourse-coupling architecture).
- **Deciding signal:** the harness Case-(b/c) verdict (gated on B1 passing).
- **Budget at risk:** ~8–14h (Priority 5).
- **Sprint 29 re-scope path:** a re-scoped Phase-0 filing targeting the LP first-stage/recourse duality (architectural — needs the harness + a deeper structural trace, not a per-term fix).
- **Prior-evidence note:** the first hypothesis (phantom-term re-symbolization) was already disproven by a full env-guarded prototype (solution-inert); this raises the prior probability of Case c, so the budget lower bound should assume kand may slip.

---

## Track C — camcge (Priority 6): Walras-law fix vs inherent degeneracy

**Decision pivot (Unknown 6.1):** is the singular Jacobian a fixable **Walras-law redundancy** (price-numéraire / redundant-row drop that preserves the economic solution → PROCEED), or **inherent CGE degeneracy** (formulation change → Epic 5 observation, REPLAN)?

**Binding Sprint 27 record:** camcge translates `action=c`-clean and the **KKT system is structurally correct** — the warm-start is a valid KKT point (all primal + stationarity equations ≈ 0 at machine precision, e.g. `gdp_check ≈ -4.83e-10`). The infeasibility is **PATH numerical convergence at a singular/ill-conditioned Jacobian, not an emit/AD bug** (`ISSUE_1330` round-3). **Day-0 bucket is `model_infeasible` (Unknown 6.2 — confirmed from the committed DB).**

### Single-model validation design (PR16 — do not implement)

| Step | Action | Output |
|---|---|---|
| C1 | Read the camcge PATH listing's **basis-singularity / dependency report** | which row(s) are flagged dependent |
| C2 | **Jacobian rank check** at the NLP point | confirm a single redundant row (Walras' law) vs higher-dimensional degeneracy |
| C3 | Prototype a **price-numéraire normalization** (or redundant-row drop); check MODEL STATUS + economic-solution match | does a clean fix yield MS 1 *and* preserve the economic solution? |
| C4 | Check generality on korcge / quocge | camcge-specific vs a general CGE issue |

### Recommendation: **conditional (harness expected Case c)**

- **PROCEED to a Sprint 28 PATH-side / numéraire fix** if C2 confirms a **single redundant row** and C3's numéraire fix yields MS 1 while **preserving the economic solution** (the Traced Fix-Surface is that lever).
- **REPLAN to an Epic 5 observation task** ("inherent CGE degeneracy needs a formulation change") if C2 shows higher-dimensional degeneracy or C3's fix changes the solution.
- **Deciding signal:** the singular-row identity (C1/C2) + whether the numéraire fix preserves the economic solution (C3).
- **Budget at risk:** ~8–14h (Priority 6); camcge's +1 Solve is **conditional**.
- **Sprint 29 / Epic 5 re-scope path:** document the degeneracy as an Epic 5 formulation-level observation (CGE models are classically singular at the Walras-law row) if no numéraire fix preserves the solution.

---

## Budget-at-Risk Tally (feeds Task 10's schedule lower bound)

| Track | Priority | Budget | At-risk condition | Prior probability of REPLAN |
|---|---|---|---|---|
| #1387 cclinpts | 4 | ~12–18h | anchor fix is architectural (all callers) | Medium — the Day-6 revert blocker is real, but the anchor *may* be gateable |
| #1390 kand | 5 | ~8–14h | gap is LP-recourse-coupling (Case c) | Medium-High — first hypothesis already proven inert |
| camcge | 6 | ~8–14h | inherent degeneracy / numéraire changes solution | Medium-High — Sprint 27 already found it PATH-side, not emit |
| **Combined** | 4–6 | **~28–46h** | — | **Task 10 lower-bound schedule should assume all three may partially slip** |

The Task 10 schedule's **lower bound** assumes Priorities 4–6 partially slip to Sprint 29; the **upper bound** assumes all three PROCEED and land. The firm Sprint 28 gains (Solve +3 from mine/camshape/otpop, Match +3 from otpop/cclinpts/kand — though cclinpts Match is itself Track A) do **not** depend on Tracks A–C resolving PROCEED, except cclinpts's +1 Match (Track A) and kand's +1 Match (Track B), which are the at-risk Match contributions.

## Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_28/PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md && echo present
grep -Ei 'PROCEED|REPLAN' docs/planning/EPIC_4/SPRINT_28/PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md
grep -Ei 'cclinpts|#1387|kand|#1390|camcge' docs/planning/EPIC_4/SPRINT_28/PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md | head
```
