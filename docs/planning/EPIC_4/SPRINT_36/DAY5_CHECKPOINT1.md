# Sprint 36 — Day 5: Checkpoint 1 (markov + fawley verdict; no-regression GO)

**Date:** 2026-08-08 · **Branch:** `planning/sprint36-day5-checkpoint1` · **Scope:** docs-only (checkpoint gates + verdicts); no `src/`, no golden change in this PR. (The one golden changed *since the anchor* is `turkey_mcp.gms`, from the S35 Day-6 turkey landing — pre-existing, outside this PR; §1.)

**Outcome: Checkpoint 1 = GO. Both front-loaded emit tracks resolved with ZERO `src/` shipped (markov P1 banked Day 3; fawley P3 deferred Day 4), so every no-regression gate is trivially green: the PR25 re-baseline is exactly the S35-close 108/93 (63+30)/75, the golden-staleness over markov + fawley + the 2-D cohort is clean (0 drift), the presolve-divergence allowlist is unchanged (korcge + robustlp), and `--resolve-changed --since-commit 78ceaead` finds only turkey changed (testbed-gated — no unchanged golden can regress since `src/` is byte-identical to the anchor). Genuine floor stays 75 (the honest projection's 75 branch). Freed budget → P2 sarf (Days 6–7) + P4 ganges (Days 8–9), the actual bucket tracks.** Verifies the no-regression invariant + the markov/fawley dispositions.

Reference: `DAY2_MARKOV_OFFDIAG_CONTROL.md` + `DAY3_MARKOV_BANK.md` (markov bank), `DAY4_FAWLEY_DEFER.md` (fawley defer), `PLAN.md` §9 (Checkpoint 1), §2 (projection).

---

## 1. Checkpoint gates (all GREEN)

| gate | result |
|---|---|
| **Anchor integrity** (`git diff 78ceaead..HEAD -- src/`) | only `original_symbols.py` +52 (the S35 turkey delta); `stationarity.py` / `derivative_rules.py` byte-identical → Days 1–4 shipped **0 `src/`** |
| **DB byte-unchanged** (`git diff 78ceaead..HEAD -- data/gamslib/gamslib_status.json`) | empty → 0 bucket move |
| **PR25 re-baseline** (142 candidates) | **Solve 108 / Match 93 (63 cold + 30 presolve) / genuine floor 75** — exactly the S35-close baseline |
| **Golden-staleness** (markov, fawley, cesam2, camcge, ps2_f_s, ps2_s, ps3_s_gic, polygon → 13 goldens) | **all clean, 0 drift** |
| **Presolve-divergence allowlist** | korcge + robustlp (unchanged — no NEW divergence) |
| **`--resolve-changed --since-commit 78ceaead`** | only `turkey_mcp.gms` changed (>1000-row testbed-gated); no unchanged golden can regress (`src/` byte-identical) |

**NO-GO condition** (any *unchanged* golden moved backward `match→mismatch` / `model_optimal→model_infeasible` / presolve-match→abort): **not triggered** — nothing shipped, nothing drifted.

## 2. Track verdicts

- **P1 markov — BANKED (Day 3), floor flat 75.** Day 1 proved the `CASE_A` cold emit → cold match (2401.577) — the +1 payoff is real. Day 2's Mechanism C control proved the emission reaches `CASE_A` + cold-match in `src/`, but the domain-only signature gate leaks full-corpus (cesam/ferts/sroute). Day 3 banked the whole lever (a leak-free gate needs a derivative-structure discriminator = dedicated effort). **The markov +1 (75→76) did NOT land** — floor stays 75. Bank carries a *proven emission* + a single precisely-scoped blocker.
- **P3 fawley — DEFERRED (Day 4), 0 bucket.** The correctness target is confirmed (`stat_bq` 0.973 → the Day-9 `473→1.14e-13` hand-edit reproduces on byte-identical goldens), but the `qsb`/`pbal` emission path ≠ the design's assumed partial-overlap branch, and fawley is H-b (0 bucket regardless; the +Solve is the P5 `--force` survey). Deferred with a sharpened spec.

## 3. Freed-budget reallocation

Both front-loaded tracks (markov Days 1–3, fawley Day 4) resolved to de-risked banks with **0 `src/`** — well under their nominal budgets. The reallocation (`PLAN.md` §9):
- **Days 6–7 → P2 sarf** (the 369K symbolic-emit re-arch; +1 Translate).
- **Days 8–9 → P4 ganges** (the ≥5-blocker cascade; +2 Solve/Match or 0 — the bimodal bucket gate).
- These are the sprint's **actual bucket tracks** — any KPI movement this sprint comes from here (markov/fawley were the emit-correctness tracks, now banked/deferred).

## 4. KPI + Go/No-Go

**Checkpoint 1 = GO.** Genuine floor **75** (the projection's 75 branch — markov +1 banked, fawley 0-bucket); Solve 108 / Match 93 / Translate 135 unchanged; DB byte-unchanged; `src/` byte-identical to the anchor across Days 1–4. Zero broken code; the control-first discipline held on both front-loaded tracks (payoffs de-risked, blockers surfaced + scoped, nothing risky shipped). The sprint proceeds to P2/P4.

**Honest projection forward (`PLAN.md` §2):** floor stays 75 (markov contingency resolved to the 75 branch); Solve 108–110 (P4 ganges bimodal); Translate 135 or 136 (P2 sarf); robustlp de-allowlist (P7, Day 10); turkey +1 testbed-deferred.

---

**Document Status:** ✅ Complete — Sprint 36 Day 5 (Checkpoint 1; no-regression GO, floor flat 75, budget → P2/P4)
**Last Updated:** 2026-08-08 · **Owner:** Sprint 36 Execution Team
