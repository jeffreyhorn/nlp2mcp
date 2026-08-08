# Sprint 36 — Day 4: fawley P3 constraint-index-diagonal — control + implementation attempt → DEFER (0 bucket, emission path ≠ design's assumed branch)

**Date:** 2026-08-08 · **Branch:** `planning/sprint36-day4-fawley-diag` · **Scope:** `/tmp` control + a reverted `src/` implementation attempt (`src/kkt/stationarity.py` byte-identical to `main`); no `src/` ships, no golden change.

**Outcome: DEFER fawley P3. The correctness target is confirmed (baseline `stat_bq` rel 0.973; the fawley golden is byte-identical to the anchor, so the Day-9 hand-edit `473→1.14e-13` reproduces). But an implementation attempt of the design's derivative-structure discriminator (Task 4 §2 — the `_collect_free_indices` absence test at the partial-overlap sum branch) did NOT fire on fawley's `qsb`/`pbal` terms: they emit via a DIFFERENT code path (0 partial-branch firings for `bq`), and the S35 Day-9 constraint-index-diagonal orientation predicate they would layer on is reverted/absent from `src/`. Locating that path + rebuilding the orientation predicate + adding the discriminator + FULL-CORPUS leak verification is a dedicated effort — not worth a 0-bucket (H-b) in-sprint slot that "must not displace P2/P4." Per the design's REPLAN exit, DEFER with a sharpened spec; the freed budget goes to P2 sarf / P4 ganges (the bucket tracks). Genuine floor stays 75.** Verifies Unknowns 3.1, 3.2 (the discriminator is disjoint from markov by construction; the leak-freedom axis is now moot — nothing ships).

Reference: `FAWLEY_DISCRIMINATOR_DESIGN.md` (Task 4) §2 (the discriminator), §5 (H-b, +Solve out of scope), §6 (REPLAN exit); `../SPRINT_35/FAWLEY_DIAGONAL_DESIGN.md` (the Day-9 `stat_bq` predicate + H-b); `CONSULTATION_BUNDLE.md` §3 (the +Solve `--force` survey). Code: `_add_indexed_jacobian_terms` (`src/kkt/stationarity.py`), `_collect_free_indices`.

---

## 1. The correctness target — confirmed

fawley (`model_infeasible`, `verified_convex`, H-b) — `kkt_residual.py data/gamslib/raw/fawley.gms`:
- **`stat_bq` rel 0.973** (residual 473.4) — the P3 target (the constraint-index-diagonal over-count).
- **`stat_trans(tr-2)` rel 1.00** (residual −488) — the harness max, the **emit-correct H-b residual** (out of P3 scope — the P5 `--force` survey, §5).

The emitted `stat_bq(c,cf)` has three multiplier terms summed over `cfq__`: the **mbal** term already carries `$(sameas(cfq__, cf))`, but the **qsb** (`nu_qsb(cfq__,l,s)`) and **pbal** (`nu_pbal(cfq__,m)`) terms do NOT — and their coefficients (`prop(c,s)·sum(m$…,char(c,m))·1$(bposs(cf,c))` and `-char(c,m)·1$(bposs(cf,c))`) do **not** depend on `cfq__`, so summing `nu_qsb`/`nu_pbal` over all `cfq__` is a pure over-count. `fawley_mcp_presolve.gms` is **byte-identical to the anchor `78ceaead`**, so the Day-9 hand-edit (add `$(sameas(cfq__,cf))` to qsb/pbal → `stat_bq 473→1.14e-13`) reproduces deductively. **The fix's correctness is not the blocker.**

## 2. The implementation attempt — the emission path is not the design's assumed branch

The design (Task 4 §2) specifies the discriminator as `summed_idx not in _collect_free_indices(deriv_coeff)`, "layered on the existing constraint-index-diagonal orientation check." I implemented exactly that at the **partial-overlap sum branch** (`_add_indexed_jacobian_terms`, the `extra_mult_indices` sum ~`:7106`) — the natural location for "a multiplier summed over an extra constraint index." Result:
- **The discriminator did not fire on fawley's `qsb`/`pbal`** — `stat_bq` re-emitted unchanged (still rel 0.973, still 1 `sameas` [the pre-existing mbal one]).
- **Instrumentation: 0 partial-branch firings for `var=bq`.** So fawley's `qsb`/`pbal` terms are **not** emitted via the partial-overlap branch — they take a different path (the dim-mismatch/offset-group path `:6236+` or the full-`mult_domain` sum `:7096`), where the S35 Day-9 orientation predicate (`_constraint_index_diagonal_guards`) used to live — but that predicate was **reverted** (S35 Day-9 DEFER) and is **absent** from current `src/`.

So the design's §2 named the *discriminator predicate* correctly but assumed it drops into an existing orientation check at a known branch; in reality the orientation predicate must be **rebuilt** at the (yet-unlocated) `qsb`/`pbal` emission path, then the discriminator layered on, then verified full-corpus. That is the substantial part — not a one-line predicate addition.

## 3. Why DEFER (not push on)

| factor | reading |
|---|---|
| KPI value | **0 bucket** — fawley is H-b (`stat_trans` rel 1.00 dominates; MCP stays MS-5 @ 4399.557 vs LP opt 2899.25 even with `stat_bq` closed). The +Solve is the P5 `--force` survey, not a `stat_bq` fix (§5). |
| Implementation cost | locate the `qsb`/`pbal` path + rebuild the S35 orientation predicate + add the discriminator + **full-corpus** leak verify (163 goldens — the markov Day-2 lesson: the 6-model cohort misses leaks) — a dedicated effort. |
| Risk | a shared-function (`_add_indexed_jacobian_terms`) change — the exact class that leaked on markov Day 2 (cesam/ferts/sroute); for **0 bucket**, the risk/reward is poor. |
| Schedule | P3 "must not displace P2/P4" (`PLAN.md` §3) — the bucket tracks. |
| Design | explicitly sanctions defer ("0 in-sprint bucket is the expected P3 outcome; the value is the shipped correctness fix + the fixture"). |

**DEFER** is the disciplined, honest call — consistent with the design, the schedule, and the project's control-first / zero-broken-code ethos (the S30–S35 pattern).

## 4. The sharpened bank (for a dedicated P3 effort)

1. **Correctness target (established):** add `$(sameas(cfq__, cf))` to `stat_bq`'s `qsb` + `pbal` terms → `stat_bq 473→1.14e-13` (Day-9, reproduces on byte-identical goldens).
2. **Discriminator (specified):** `summed_idx absent from _collect_free_indices(coefficient)` — a derivative-structure test, disjoint from markov (markov's coefficient always carries the summed index via `pi`; the markov track is banked anyway). Confirmed disjoint (Task 4 §3).
3. **The real blocker (Day-4 finding):** the `qsb`/`pbal` terms do NOT use the partial-overlap branch; the dedicated effort must (a) locate their actual emission path (`:6236+` dim-mismatch or `:7096` full-sum), (b) rebuild the constraint-index-diagonal orientation predicate there (S35 Day-9, reverted), (c) layer the discriminator, (d) verify **full-corpus** leak-freedom (only fawley drifts), (e) land the `shape_fawley_2d_second_index` fixture with it.
4. **Bucket:** 0 in-sprint even when landed (H-b); the +Solve is the P5 `--force` survey.

## 5. Budget + KPI

The freed P3 (Day-4) budget → **P2 sarf (Days 6–7) / P4 ganges (Days 8–9)** — the actual bucket tracks. **Genuine floor stays 75** (fawley is 0 bucket regardless). `src/kkt/stationarity.py` byte-identical to the anchor; fawley re-emits to its committed golden (`CASE_B`, no drift); DB byte-unchanged.

## 6. Go / No-Go

**DEFER — clean.** Zero broken code (`src/` reverted, byte-identical; no golden churn). The control-first discipline held: the correctness target was confirmed and the emission-path blocker surfaced via a genuine implementation attempt — *before* shipping a risky 0-bucket shared-function change. `modelstat`-assert / `x.up=inf`-BAN / Case-c-BAN disciplines all held. The correctness fix + fixture carry to a dedicated P3 effort with §4 as the implementer-ready spec.

---

**Document Status:** ✅ Complete — Sprint 36 Day 4 (fawley P3 constraint-index-diagonal; DEFER — 0 bucket, emission path ≠ design's assumed branch)
**Last Updated:** 2026-08-08 · **Owner:** Sprint 36 Execution Team
