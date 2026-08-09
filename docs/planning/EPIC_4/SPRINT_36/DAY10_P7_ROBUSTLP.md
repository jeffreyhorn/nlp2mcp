# Sprint 36 — Day 10: P7 robustlp NA-guard de-allowlist (the sprint's first `src/` landing) + Checkpoint 2

**Date:** 2026-08-08 · **Branch:** `planning/sprint36-day10-p7-infra` · **Scope:** emit-touching (`src/emit/emit_gams.py` + harness + allowlist + 17 presolve goldens); the sprint's first shipped `src/`.

**Outcome: P7 LANDS — robustlp de-allowlisted via a general emit-robustness fix. NA-guarding the presolve marginal→multiplier `.L` warm-start transfer (the #1322 idiom, in `_emit_nlp_presolve`) clears the GAMS-54 EXECERROR-84 ("illegal level value"): robustlp presolve now solves MODEL STATUS 1 Optimal (was aborting), and robustlp is removed from `presolve_divergence_allowlist.txt`. The fix is a proven no-op for finite marginals — the 17 drifted presolve goldens changed PURELY additively (0 removals; all 256 additions are the guard block), 0 cold goldens, and the full quality gate passes (typecheck / format / lint / `make test` 5040 passed). A harness interaction (the NA-guard resets matched `_MULT_RE`) was fixed in `kkt_residual.py` (`extract_dual_transfer` now skips them). Determinism ×3 {0,1,42} ✓. NOT a new bucket — robustlp was already `model_optimal_presolve` + match in the v53 DB; this RESTORES its v54 solvability (which GAMS-54's stricter generation broke) + clears the WARN. KPIs stay 108/93/75.** Resolves Unknown 7.3.

Reference: `FIXTURE_AND_HARNESS_CATALOG.md` §4 (the bounded fix spec), `DAY0_KICKOFF.md` §3.1 (the root: NA multiplier `.L` level, propagating into `(NA)*v`).

---

## 1. The fix (Task 9 §4 + the Day-0 mechanism)

The GAMS-54 EXECERROR-84 root (Day 0 §3.1): the presolve emit transfers a source marginal into a multiplier `.L` (`lam_socpqcpcons.l(i) = abs(socpqcpcons.m(i))`, `piL_y.l(i)$(…) = y.m(i)`). When the NLP solver returns **no** marginal for a row/bound, `.m` is NA → the multiplier `.L` becomes NA, which GAMS-54 rejects at generation ("illegal level value") — and that NA also propagates into any bilinear stationarity coefficient built from the multiplier (`(NA)*v` in `stat_v`, from `2*v*lam_socpqcpcons`).

**Fix (`src/emit/emit_gams.py`, `_emit_nlp_presolve`):** collect every multiplier that receives a warm-start level (the nu / lam / piL / piU transfers), then after the transfers emit one reset block using the #1322 idiom:
```gams
* Reset any NA/UNDF warm-start multiplier levels to 0 (#1322)
<mult>.l<dom>$(NOT (<mult>.l<dom> > -inf and <mult>.l<dom> < inf)) = 0;
```
A single NA `.L` → 0 clears **both** the "illegal level value" abort **and** the downstream `(NA)*v` coefficient (Day 0 §3.1). This is NOT `emit_post_assignment_na_cleanup` (which only guards indexed-param division assignments, and never sees the multiplier `.L` warm-start).

## 2. Verification

| gate | result |
|---|---|
| robustlp presolve compile (GAMS 54.2.1) | **EXECERROR-84 gone (0)**; MODEL STATUS 1 **Optimal** (was ABORTED) |
| golden drift (full corpus, 163) | **17 presolve goldens** drift; **0 cold**; 0 emit-failures |
| drift shape | **purely additive** — 0 removals, all 256 additions are the guard block (proven no solve-logic change) |
| no-op property | `$(NOT (x > -inf and x < inf))` is false for every finite `x` → the guard never fires for finite marginals; the 16 non-robustlp models' solves are invariant by construction |
| quality gate | typecheck ✓ · format ✓ · lint ✓ · `make test` **5040 passed**, 10 skipped, 1 xfailed |
| determinism ×3 {0,1,42} | robustlp + ps2_s md5-identical across seeds ✓ |

## 3. The harness interaction (fixed)

`make test` first failed 2 kkt_residual tests: the NA-guard resets (`nu_X.l$(NOT…)=0;`) matched `_MULT_RE`, so `extract_dual_transfer` mis-captured them as dual transfers (a `lam_` line without `abs(`; an un-flipped `nu_` line). Fixed in `scripts/diagnostics/kkt_residual.py`: a `_NA_GUARD_RE` + a skip in `extract_dual_transfer` (the reset is not a transfer). All 109 harness tests pass; `extract_multiplier_names` is unaffected (it dedupes names). This is exactly what the full-test gate exists to catch.

## 4. KPI framing (honest — not a new bucket)

robustlp is `verified_convex` and **already** `model_optimal_presolve` + match in the DB (`gams_version` 51.3.0 — GAMS 51/53 *tolerated* the NA levels). GAMS-54's stricter matrix generation broke it (→ the allowlist, S35 Day 6). This fix **restores robustlp's v54 solvability** and clears the WARN — it does **not** add a Solve/Match bucket. **KPIs stay 108/93/75.** The value: a real emit-robustness improvement (any presolve model's marginal could be NA) + one fewer allowlisted divergence + the v53→v54 gap closed for robustlp.

## 5. Checkpoint 2

- **Golden-staleness:** clean after regen (the 17 refreshed).
- **PR25 re-baseline:** Solve 108 / Match 93 (63 + 30) / floor 75 — unchanged.
- **`--resolve-changed --since-commit 78ceaead`** (committed state): re-solves the 17 refreshed presolve goldens + turkey → GO (no unchanged golden regressed; robustlp holds `model_optimal_presolve`; turkey `path_solve_license` testbed-gated).
- **Allowlist:** robustlp removed; korcge remains (#1439, a different EXECERROR-5 class).

## 6. Go / No-Go

**GO — P7 landed.** The sprint's first shipped `src/`: a general, deterministic, no-op-for-finite NA-guard that de-allowlists robustlp and restores its v54 solvability, with a full-green quality gate and a purely-additive golden regen. Zero regression (proven + `--resolve-changed` GO). `modelstat`-assert / `x.up=inf`-BAN / Case-c-BAN disciplines held.

**Sprint status:** the four deep tracks all banked/deferred (flat KPIs); P7 is the shipped robustness win. Remaining: P5 consultation (Day 11) + the async GAMS-54 re-baseline; turkey +1 testbed-deferred.

---

**Document Status:** ✅ Complete — Sprint 36 Day 10 (P7 robustlp NA-guard de-allowlist; landed, KPIs 108/93/75, robustlp v54-solvable + de-allowlisted)
**Last Updated:** 2026-08-08 · **Owner:** Sprint 36 Execution Team
