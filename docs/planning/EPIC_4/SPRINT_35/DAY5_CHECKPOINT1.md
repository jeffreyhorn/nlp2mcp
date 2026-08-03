# Sprint 35 — Day 5: Checkpoint 1 (P4 close-or-REPLAN) — GO, no regression; P4 REPLAN'd (banked)

**Day:** 5 (Priority 4 — close-or-REPLAN + Checkpoint 1) · **Date:** 2026-08-03 · **Owner:** Sprint 35 execution
**Day-0 code anchor:** `78ceaead` (S34 close) · **Branch:** `planning/sprint35-day5-p4-close-checkpoint` (docs-only)
**Verdict: ✅ Checkpoint 1 GO — zero regression. P4 REPLAN'd (banked at Day 3).** The sprint's only live REPLAN gate has fired; the outcome resolves to the bimodal projection's **flat** branch (108/93/75). P4's freed budget → P6/P7.

---

## 1. Checkpoint 1 gates (Phase-0 §2 cross-cutting)

| Gate | Result |
|---|---|
| `--resolve-changed --since-commit 78ceaead` (bucket-diff vs committed DB) | ✅ **GO** — "no emit goldens changed since 78ceaead" (0 changed) |
| `src/`/`scripts/` drift since `78ceaead` (`git diff --stat`) | ✅ **empty** — zero drift → golden-staleness (PR26) + presolve-divergence are **clean by construction** (identical `src/` ⇒ identical emit ⇒ identical goldens ⇒ identical divergence) |
| DB byte-unchanged since S33 close `750803b2` | ✅ **unchanged** (md5 `6166acab90dcaff8789255f8ada83c54`) — the committed tally is authoritative |
| PR25 re-baseline (142 corpus) | ✅ **== Day-0 baseline** (below) |

**NO-GO condition** (any *unchanged* golden moved backward: `match→mismatch`, `model_optimal→model_infeasible`, presolve-match→abort): **not triggered** — the P4 arc (Days 1–3) shipped **zero** `src/`/DB/golden changes (all banked, docs-only), so no golden could move.

## 2. Tally (142 candidate corpus) — flat vs Day 0

| KPI | Day 0 | Day 5 | Δ |
|---|---|---|---|
| Parse | 142 | 142 | 0 |
| Translate | 135 | 135 | 0 |
| Solve | 108 (64 cold + 44 presolve) | 108 (64 + 44) | 0 |
| Match (142) | 93 | 93 | 0 |
| all-219 Match | 96 | 96 | 0 |
| model_infeasible | 7 | 7 | 0 |
| path_syntax_error | 7 | 7 | 0 |
| genuine floor (PR25) | 75 | 75 | 0 |

`model_infeasible (7)`: agreste, camcge, cesam, fawley, lnts, mine, rocket.
`path_syntax_error (7)`: clearlak, dinam, **ganges**, **gangesx**, indus, turkey, turkpow — ganges/gangesx unchanged (P4 banked, no bucket move).

## 3. P4 verdict: REPLAN'd (banked)

**P4 is REPLAN'd** — banked at Day 3 (`DAY3_P4_BANK_CARRYFORWARD.md`). ganges/gangesx are a **≥5-blocker cascade** (`$141`/`$145`/`$149` fixed → `$66` cold → `rPower` presolve `$onMultiR` divergence), recovering on neither path. Per "no bucket → no `src/`", the whole three-root fix was reverted; the **`$149` fix is verified correct + surgical** and banked with its patch for the Sprint-36 dedicated ganges recovery. This is the honest bimodal outcome (Task 11): with P4 as the sole live bucket lever, its REPLAN resolves the sprint to the **flat** branch — Solve 108 / Match 93 / floor 75 hold unless P6 recovers a residual-cohort model.

## 4. Freed-budget reallocation

P4's **14–20 h** (the in-sprint bucket work) reallocates to:
- **P6 (Days 6–7) — the residual failure-cohort**, now the sprint's **remaining bucket hope** (the second bucket source per Task 11): turkey `$161`, dinam/indus `$140`+`$149`, turkpow `$149`+`$171`, clearlak `$149`+**`$352`** (the Day-0-flagged catalog correction). Multi-root discipline + per-model verify + `--resolve-changed` GO on any landing.
- **P7 (Day 10)** — infrastructure/fixtures + the PR25 floor tracking + SUMMARY row 35.

The retrospective-budget slack is now even larger (P4's design was spent in prep *and* its in-sprint attempt fast-failed at Day 3), so the back half can afford a thorough P6 push.

## 5. Next

**Day 6 — Priority 6 (residual failure-cohort, part 1):** turkey `$161` (dotted-tuple set) + dinam/indus (`$140`+`$149`). Per-model, never inferred; `--resolve-changed` GO before any landing; `modelstat` asserted. A flat P6 is acceptable — P6 is the *second* bucket source, not the headline.

---

**Document Status:** ✅ Complete — Sprint 35 Day 5 (Checkpoint 1: GO, P4 REPLAN'd)
**Last Updated:** 2026-08-03
**Owner:** Sprint 35 Execution Team
