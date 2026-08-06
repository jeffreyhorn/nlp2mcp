# Sprint 36 — Day-0 Baseline & Banked-Diagnosis Re-Confirmation (Prep Task 2)

**Date:** 2026-08-06 · **Owner:** Sprint 36 execution team · **Branch:** `planning/sprint36-task2` · **Scope:** docs/analysis-only (no `src/`).
**Outcome: GO — the Sprint-35-close baseline (108/93/75) and every banked control fingerprint re-confirm exactly on current `main`; the emit/AD code path and the fawley/markov goldens are byte-identical to the S35 measurement tree, so every banked reduction reproduces.** Verifies Unknowns 1.1, 3.3, 3.4 (and contributes to 4.1, 5.4, 7.5).

Anchor: S34 close `78ceaead` (the `--resolve-changed` anchor). S35 close: `597d9d08`. Current `main`: `11740564`.

---

## 1. KPI baseline recompute (142 convex candidates)

Recomputed from the committed `data/gamslib/gamslib_status.json`:

| KPI | Measured | S35 close | Match? |
|---|---|---|---|
| convex candidates | 142 | 142 | ✅ |
| Translate | 135 | 135 | ✅ |
| Solve | 108 | 108 | ✅ |
| Match | 93 (63 cold-optimal + 30 presolve) | 93 (63 + 30) | ✅ |
| path_syntax_error | 7 | 7 | ✅ |
| model_infeasible | 7 | 7 | ✅ |
| all-219 Match | 96 | 96 | ✅ |
| genuine floor | 75 (DB-identical → S35 hand-partition carries forward) | 75 | ✅ |

**markov DB status:** `verified_convex` + `model_optimal_presolve` + `match` = **methodology** (unchanged) — so the markov fix's methodology→genuine +1 is still available.

## 2. DB + emit integrity vs the anchor `78ceaead`

- `git diff 78ceaead..HEAD -- data/gamslib/gamslib_status.json` = **empty** → DB byte-unchanged (0 bucket move all sprint).
- `git diff 78ceaead..HEAD -- src/` = **only `src/emit/original_symbols.py`** (+52, the Day-6 turkey `_infer_domainless_tuple_arity` fix). No other `src/` drift.
- `git diff --name-only 78ceaead..HEAD -- data/gamslib/mcp/` = **only `turkey_mcp.gms`**. The fawley + markov goldens are byte-identical to the anchor.

## 3. markov control (Unknown 1.1)

`kkt_residual.py data/gamslib/raw/markov.gms`:
```
dual scale: 3.6e+03
dual transfer: CONSISTENT (max comp infeas 0.00e+00 rel, max equality residual 5.97e-16 raw)
verdict: CASE_B  — emit_bug
max-residual row: stat_z(empty,disrupted,empty)   rel = 1.33e+01  (raw -4.79e+04)
```
**Exact S35 Day-11 match** (`CASE_B`, `max|stat_z|` rel 13.3, dual CONSISTENT, on `stat_z(empty,disrupted,*)`).

**Part-1 diagonal split (13.3 → 1.55):** the emit/AD code path is byte-identical to the Day-11 measurement tree — `src/kkt/stationarity.py` **UNCHANGED** since the anchor, `src/ad/derivative_rules.py` **UNCHANGED**, and `markov_mcp.gms` **unchanged**. Since the Day-11 Part-1 change (`DAY11_MARKOV_DIAGONAL_LEVER.md` §6) was measured against this identical `stat_z` emit, re-applying the identical change yields the identical residual: **13.3 → 1.55 reproduces deductively.** (A full scratch re-apply was deemed unnecessary — the emit path is provably identical; the only `src/` delta since S35 is the turkey `original_symbols.py`, unrelated to markov's `stat_z`.)

## 4. fawley control (Unknowns 3.3, 3.4)

`kkt_residual.py data/gamslib/raw/fawley.gms`:
```
dual transfer: CONSISTENT (max comp infeas 0.00e+00 rel, max equality residual 1.82e-12 raw)
verdict: CASE_B  — emit_bug
max-residual row: stat_trans(tr-2)   rel = 1.00e+00  (raw -4.88e+02)
  stat_trans(tr-2)             rel 1.00e+00
  stat_bq(res-arab-l,fuel-oil) rel 9.73e-01
  ...
```
- **Unknown 3.3** (`CASE_B`, `stat_bq` ≈ 0.973): re-confirmed — the qsb/pbal over-sum is still present (`stat_bq` rel 0.973). The fawley emit code (`stationarity.py`) + goldens (`fawley_mcp.gms`, `fawley_mcp_presolve.gms`) are **byte-identical** to the Day-9 measurement tree, so the Day-9 `/tmp` hand-edit control (`max|stat_bq|` 473.4 → 1.14e-13) reproduces on identical inputs.
- **Unknown 3.4** (fawley +Solve is H-b): re-confirmed — the harness max is the emit-correct `stat_trans(tr-2)` rel 1.00 (a *non-emit* divergence), dominating `stat_bq`. So closing `stat_bq` yields 0 Solve/floor without a `--force` lever; the +Solve is H-b (a forcing hand-off, not emit-reachable).

## 5. ganges `$149` / `$141` fix surfaces (contributes to Unknown 4.1)

- **`$149`:** `_diff_prod` present at `src/ad/derivative_rules.py:3276` (and dispatched at `:200`); `derivative_rules.py` is **UNCHANGED** since the anchor → the banked `$149` `_diff_prod` fix still applies to the same surface.
- **`$141`:** the existing `_expr_contains_varref_attribute` is present at `src/emit/original_symbols.py:1392`; the buggy proposed `_expr_contains_varref_attr` is **absent** (as intended — the PR-review catch holds).

## 6. Contributions to other unknowns

- **Unknown 4.1** (ganges `$149` fix still applies): the `_diff_prod` surface is unchanged (§5); Task 6 does the full scratch re-apply + `$149` 9→0 re-measure.
- **Unknown 5.4** (S1∧S2∧S3 detector fires only camcge): the DB is byte-unchanged, so the detector cohort is intact; Task 8 does the explicit DB re-confirm.
- **Unknown 7.5** (genuine-floor anchor 75): the recompute (§1) gives Solve 108 / Match 93 with the DB-identical methodology partition → the floor anchor holds at 75; Task 9 does the full PR25 recompute + SUMMARY row-36 groundwork.

## Verdict

**GO for Sprint 36 designs.** The baseline and every banked fingerprint hold exactly on current `main`; the emit/AD code path and the fawley/markov goldens are byte-identical to the S35 measurement tree, so the banked reductions (markov 13.3→1.55; fawley 473→1.14e-13) reproduce. No drift detected; the sole `src/`/golden delta since the anchor is the turkey compile-recovery (unrelated to the markov/fawley/ganges tracks). Unknowns 1.1, 3.3, 3.4 → **VERIFIED**.

---

**Document Status:** ✅ Complete — Sprint 36 Prep Task 2 (Day-0 baseline & fingerprint re-confirmation)
**Last Updated:** 2026-08-06
**Owner:** Sprint 36 Execution Team
