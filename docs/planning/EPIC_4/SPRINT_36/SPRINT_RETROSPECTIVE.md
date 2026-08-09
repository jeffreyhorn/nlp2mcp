# Sprint 36 — Retrospective

**Close:** 2026-08-09 · **Result:** FLAT (108/93/75/135), the projection's 75 branch · **Shipped:** P7 robustlp (1 `src/` landing) · **Banked:** markov / P4 ganges / fawley / sarf (4 deep tracks).

---

## 1. What the sprint produced (beyond the flat KPIs)

The headline is flat, but the sprint's *firm product* is real:
1. **One shipped robustness landing — P7 robustlp.** A general emit fix (NA-guard the presolve marginal→multiplier `.L` warm-start), Phase-0 gated, that restores robustlp's GAMS-54 solvability and removes an allowlisted divergence. Under review it *grew* better: the reviewer caught an NA `_fx_` fix-dual gap, closed with byte-identical non-fx goldens.
2. **Four empirically-sharpened banks.** Unlike a prep-only bank, every S36 bank *reproduced its blocker live* — so Sprint 37 inherits proven components + a single precise blocker each, not a "substantial rewrite" from scratch.
3. **The rocket/mine submissions + the camcge/fawley experiment results** — the consultation cycle is teed up for Sprint 37 with empirical hand-offs.
4. **Zero broken code across 13 days** — `src/kkt/stationarity.py` / `derivative_rules.py` byte-identical to the anchor throughout; DB byte-unchanged.

## 2. What worked

- **Control-first, front-loaded.** The schedule front-loaded markov (the one local bucket lever) so its REPLAN surfaced on **Day 2**, not Day 12 — freeing the whole back half. Every emit-touching gate ran a `/tmp` control *before* `src/`; the only shipped `src/` (P7) had a full-green gate.
- **"Reproduce, don't trust the doc."** This paid off repeatedly: Day-0 traced robustlp's `(NA)*v` to the same `.L` root; Day-2 markov's leak surfaced *full-corpus* (cesam/ferts/sroute — the 6-model cohort missed all three); Day-8 ganges's cascade fixes were *verified working* and `rPower` *reproduced* as the deep class; Day-11 fawley's `--force` NEGATIVE and camcge's numéraire-insufficiency were *measured*. Prep characterizations were right in direction but the live runs sharpened (and twice corrected) them.
- **Banking over shipping risk.** markov's emission works but its gate leaks; ganges's fixes work but rPower is a deep class; fawley/sarf are 0-bucket/lowest-leverage. Every one banked rather than ship a fragile shared-function change for uncertain/zero gain — the S30–S36 pattern, held.

## 3. Key technical findings

- **markov (the +1 lever):** the emission is *solved* (CASE_A + cold-match 2401.577); the blocker is a **derivative-structure discriminator** — a domain-only gate can't tell markov's param-coupled `σ=sp` from cesam's variable-bilinear or sroute's conditional-constant structures. **Leak-verification must be full-corpus (163), not the 6-model cohort** — the single biggest process lesson (the prep's cohort was incomplete).
- **P4 ganges:** `$141`/`$145`/`$149` verified; `rPower` is the #1378/#1424 embedded-NLP-divergence class (the `.l`-power calibrations re-run non-idempotently under the presolve `$onMultiR` `$include`). Recovery is atomic — a partial churns goldens for 0 bucket.
- **robustlp (shipped):** the GAMS-54 EXECERROR-84 was an NA *multiplier level* (not an NA Jacobian coefficient — the allowlist's characterization was imprecise), propagating into the `(NA)*v` bilinear coefficients; one `.L → 0` reset clears both.

## 4. Process lessons (for Sprint 37 prep)

1. **Full-corpus leak verification is mandatory for any shared-`_add_indexed_jacobian_terms` change.** The 6-model cohort is *not* the risk set (it missed 3 markov leaks). Bake the 163-golden staleness into every such control.
2. **A "leak-free by construction" design claim is a hypothesis, not a fact** — markov's Mechanism C was argued leak-free and leaked. Test it.
3. **Distinguish "emission proven" from "landable."** markov and P4 both have *proven* components but un-landable-in-budget blockers; the sharpened bank (proven emission + one precise blocker) is a far better hand-off than a prep bank.
4. **Emit-touching PRs need the Phase-0 issue doc up front** (CONTRIBUTING.md) — P7 needed it added under review; author it before the `src/` commit next time.

## 5. Carryforward priority (Sprint 37)

**markov Part-2 first** (the +1-floor lever, fully local, emission proven — the highest-probability real bucket move once the discriminator lands, full-corpus-verified). Then **P4 ganges** (+2 bimodal, atomic) and the **consultation cycle** (rocket reply, mine, camcge Epic-5). **sarf/fawley** stay lowest-priority (lowest-leverage / 0-bucket). **turkey** and the **full v54 re-baseline** are gated on a licensed testbed. Detail: `SPRINT_37_CARRYFORWARDS.md`.

---

**Document Status:** ✅ Complete — Sprint 36 retrospective.
**Last Updated:** 2026-08-09 · **Owner:** Sprint 36 Execution Team
