# Sprint 35 — Retrospective

**Theme:** Quality, performance & PATH-feedback integration. **Anchor:** S34 close `78ceaead`. **Close:** Day 13. **Result: modal-FLAT** — Solve 108 / Match 93 / genuine floor 75 / Translate 135 (all maintained; 0 bucket move; the honest bimodal projection's flat branch; `≥112` a-priori refuted).

---

## 1. What landed

- **The projection called it.** Prep projected a **bimodal** outcome (flat 108/93/75 or upside 110/95/77) gated on P4 (ganges/gangesx) proceeding, and warned `≥112` was refuted. P4 banked Day 3 as a ≥5-blocker cascade, so the **flat branch landed exactly** on every axis. No surprise, no broken code.
- **One `src/` landing:** turkey `$161` compile-recovery (Day 6) — a domain-less 2-D-set arity-inference fix. It works (Checkpoint 2 + Day-13 retest: turkey now compiles clean and reaches PATH; `path_syntax_error → path_solve_license`), but its +1 Solve/Match is **testbed-gated** by the 1000-row GAMS demo limit (turkey's MCP is 3,866 rows).
- **Two verified-but-banked fixes** (control-confirmed, reverted for risk/scope): the Day-9 fawley constraint-index-diagonal control (`max|stat_bq|` 473.4→1.14e-13) and the Day-11 markov diagonal-Kronecker split (residual 13.3→1.55).
- **One genuine discovery:** the Day-11 **markov +1-floor lever** — a control-confirmed `CASE_B` cold-emit bug that makes a `verified_convex` model a *methodology* match; fixing it flips markov methodology→genuine (floor 75→76), fully local (no testbed gate). Half-de-risked by a leak-gated landing attempt.

## 2. What held (the disciplines)

- **Control-first REPLAN (PR24/PR27) held for the fifth+ sprint.** Every deep track was refuted or banked on control evidence *before* any bad ship: P1 mine (value-invariant), P2 sarf (369K re-arch), P3 fawley (leaks onto markov), P4 ganges (≥5-blocker), P5 camcge (Epic-5). **Zero broken code shipped.** The KKT-residual harness + `/tmp` controls remain the workhorse.
- **The leak-gate works both ways.** Day 9: a fawley shared-function change *leaked onto markov* → reverted. Day 11: the markov fix attempt was reverted when it (a) didn't reach CASE_A and (b) couldn't even be cohort-validated (cohort emits are minutes-scale). The `_add_indexed_jacobian_terms` shared machinery is the recurring high-blast-radius surface — and the discipline correctly gated both attempts.
- **Every PR obeyed the workflow:** docs-only PRs skipped the quality gate; the one src/ landing (turkey, PR #1620) ran the full gate; every PR-review thread was replied to individually (incl. declining two false-positive Markdown-lint suggestions with rationale, and accepting real catches — a broken relative path, non-rendering wiki-links, an internally-inconsistent formula).

## 3. What we learned (new this sprint)

- **A hidden red `slow` test can conceal a real bucket lever.** `test_markov_stationarity_has_correction_term` had been red **since March 2026**, excluded from `make test` by `pytest.mark.slow`. It surfaced only because a Day-9 KKT run filtered on the test name. It encodes a *correct* assertion the emit never satisfied → the markov +1-floor lever. **Action:** the Sprint-36 markov fix decides the `slow`/`xfail` disposition; more broadly, `slow`-marked correctness tests deserve a periodic visible run.
- **The GAMS demo license is a hard 1000-row solve ceiling (v53 and v54).** It makes local solve-verification of large MCPs impossible — turkey's +1 is real but unrealizable without a licensed testbed. This is now a structural constraint on what "landing a bucket" can mean locally.
- **The v53→v54 transition adds a version axis to the baseline.** GAMS 53's demo license expired mid-sprint; CI + local moved to 54.2.1. The 108/93/75 baseline was built under 53. The close reports the v53 KPIs as-is and opens a v54 corpus re-baseline as the first Sprint-36 infra task (emit-level gates are version-independent and stayed valid).
- **markov's bug is a two-part shape defect**, not the single split the test docstring implied: (1) the diagonal Kronecker `1` is summed over the enumeration dummy (the direct fix, verified), and (2) the off-diagonal multiplier index is an *independent* variable index (`σ=sp`) the offset machinery can't represent (the deeper rewrite). The attempt turned an aspirational docstring into a rigorous, pinned spec.

## 4. Honest framing

This is the **third consecutive modal-flat sprint** (S33's +1 was the last genuine bucket move; S34 flat; S35 flat). The genuine-floor ramp is **75 → 75 → 75** across S33–S35 — the aspirational S32→S35 `≥78` ramp did **not** realize. The Sprint-30/31 §3 lesson holds: the floor advances *only* via emit-changing cold-matches, and none landed. The sprint's value is **de-risking + verified diagnoses**, not bucket motion — and, uniquely this sprint, **a newly-discovered, half-de-risked +1 lever (markov)** that is the strongest concrete upside carried into Sprint 36.

## 5. Carried into Sprint 36

The one live, local upside is **markov (+1 floor)** — fully diagnosed, part-1 fix verified, part-2 (`σ=sp` enumeration) pinned. Second is **turkey (+1)**, testbed-gated. Both, plus the consultation trio (rocket/mine/fawley), sarf, the ganges recovery bundle, and the GAMS-54 re-baseline, are specified in `SPRINT_36_CARRYFORWARDS.md`. camcge → Epic 5.

---

**Document Status:** ✅ Sprint 35 retrospective (Day 13 close)
**Last Updated:** 2026-08-04
**Owner:** Sprint 35 Execution Team
