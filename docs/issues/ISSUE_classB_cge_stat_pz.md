# Class-B CGE `stat_pz` coefficient discrepancy (irscge / lrgcge / moncge / stdcge / marco) — general-emit, NOT Walras

**GitHub:** (no number — local Sprint-30 Priority 7 general-emit backlog track)
**Status:** **Sprint 30 Priority 7 — PROCEED-conditional (general-emit coefficient fix; cold-robustness / genuine-floor, gated on one-fix-converts-several).** Established Sprint 29 Day 12 (harness trace); gate authored Sprint 30 Prep Task 5.
**Filed:** Sprint 30 Prep Task 5 (2026-07-05)

## Summary

A cluster of CGE models — **irscge, lrgcge, moncge** (`stat_pz` rel ≈ 1.0), **stdcge** (`stat_epsilon` rel ≈ 2.0), **marco** (`stat_w` rel ≈ 3.3) — carry a localizable Case-b stationarity residual on the output-price variable path. Sprint 29 Day 12 confirmed via the KKT-residual harness that this is a **general-emit coefficient/scaling discrepancy**, **NOT** the camcge (#1330) Walras-law structural singularity (Unknown 7.3). All the models already **match via the `--nlp-presolve` warm-start** (`model_optimal_presolve`); a fix is **cold-robustness** (raises the genuine floor), not headline +Match.

## Phase 0: Acceptance Gate

> **Sprint-30 disposition (Prep Task 5, 2026-07-05): PROCEED-conditional.** The residual is a **coefficient/scaling discrepancy** (the `pz` cross-terms are **present**, not dropped — Sprint 29 Day 12), and the models are **non-convex** (no cold-conversion available beyond the warm match). PROCEED to trace the coefficient; the payoff is genuine-floor (cold-robustness). **Gated on Unknown 7.1** — whether one general-emit coefficient fix converges the `stat_pz` residual across irscge/lrgcge/moncge/stdcge (several models, one fix) or the discrepancy is per-model. marco (`stat_w`) is a distinct, model-specific residual — separate.

### Hand-Derived KKT Shape

For the standard CGE closure, the output-price variable `pz(j)` is defined by a zero-profit / price row `eqpzs(j)` (activity price = unit cost). `pz(j)` appears in `eqpzs(j)` (coefficient depending on the value-added / intermediate structure) and in the market-clearing / income rows. Its stationarity:

```
stat_pz(j)..  ( Σ_over-rows-containing-pz(j)  COEFF · nu_<row> )  − piL_pz(j)  =E= 0
```

A residual of exactly **1.0** (irscge/lrgcge/moncge) is the fingerprint of a **missing unit-coefficient factor or a mis-scaled `COEFF`** on one of the `pz(j)` cross-terms — the terms are structurally present (dual-transfer CONSISTENT), so the discrepancy is in the *coefficient*, not a dropped multiplier. (`stdcge` `stat_epsilon` 2.0 and `marco` `stat_w` 3.3 are adjacent per-variable variants.)

### Expected Emit Pattern

Each model's `<model>_mcp.gms` `stat_pz(j)` (resp. `stat_epsilon` / `stat_w`) should carry the correctly-scaled coefficient on every `pz`-referencing Jacobian-transpose term, so the eliminated-KKT residual → 0 at the NLP optimum. The `pz` cross-terms are already emitted — the fix is a **coefficient correction in the general emit path**, not a new term. (Hypothesis — the actual builder `file:line` to be confirmed by the Day-0 trace.)

### Verification Methodology

```bash
for m in irscge lrgcge moncge stdcge marco; do
  .venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/$m.gms --json /tmp/phase0_$m.json 2>&1 | grep -iE "verdict|max-residual|dual transfer"
done
```

- **PROCEED (Case b, one-fix-several):** irscge/lrgcge/moncge all localize to the **same** `stat_pz` coefficient discrepancy (rel ≈ 1.0), dual transfer CONSISTENT → a single general-emit coefficient fix converges several. This is the confirmatory test for Unknown 7.1.
- **NOT Walras (Unknown 7.3):** cross-check the market-clearing block is **full-rank** (unlike camcge #1330's structural singularity — Sprint 29 Day 12 confirmed CASE_B + CONSISTENT, distinct from camcge's MS-4-at-iteration-0). The fix stays in nlp2mcp (general emit), it is **not** an Epic-5 CGE transformation.
- **REPLAN (per-model):** if the `stat_pz` coefficient differs per model (no shared general-emit surface) → the payoff drops to 1–2 models (the highest-residual), still worth the cold-robustness; not a Sprint-30 architectural REPLAN.
- Post-fix: cold `compare_objective_match` where the model is convex-enough to cold-solve; otherwise the residual → 0 (Case a) confirms emit-correctness even if the non-convex cold solve still needs the warm-start (genuine-floor, not +Match).

### PROCEED/REPLAN Signal

- **🟡 PROCEED-conditional — Sprint-30 P7 general-emit backlog.** PROCEED to trace the `stat_pz` coefficient discrepancy; the value is genuine-floor (cold-robustness across the cluster), not as-measured +Match (all already warm-match). Confirm one-fix-converts-several (Unknown 7.1) before counting the conversion.
- **Traced Fix-Surface (Day-0 hypothesis, PR24):** the general stationarity-emit coefficient path for the CGE output-price variable — the Jacobian-transpose coefficient on the `pz`-referencing cross-terms in `src/kkt/stationarity.py` / `src/ad/constraint_jacobian.py` (the terms are present; the coefficient/scaling is off). Trace command: the per-model harness loop above + `grep -E 'stat_pz|eqpzs|nu_' <model>_mcp.gms`. Evidence: `docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md` §4 Class B; the Sprint 29 Day-12 CHANGELOG entry (harness CASE_B, `stat_pz`≈1.0 / `stat_epsilon`≈2.0, dual transfer CONSISTENT, NOT Walras).

## Provenance

- Sprint 29 Day 12 — harness-traced the Class-B CGE cluster: CASE_B, `stat_pz`≈1.0 / `stat_epsilon`≈2.0, dual transfer CONSISTENT, **NOT** the camcge Walras family; the `pz` cross-terms are present (coefficient/scaling discrepancy), models non-convex → general-emit backlog.
- `docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md` §4 Class B (the CGE price/numéraire family, gated distinct from camcge #1330).
