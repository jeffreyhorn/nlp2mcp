# Sprint 36 — Day 0 Kickoff: Baseline + Fingerprint Re-Confirm + GO/NO-GO

**Date:** 2026-08-07 · **Branch:** `planning/sprint36-day0-kickoff` · **Scope:** docs/trace-only (re-confirmation on current `main`; no `src/`).

**Outcome: GO for Day 1.** The S35-close baseline reproduces exactly on current `main`; the code anchor holds (the only `src/` delta since `78ceaead` is the turkey compile-recovery, unrelated to the S36 tracks); every banked fingerprint re-confirms; all 30 unknowns are resolved with zero INCOMPLETE.

Anchor: DB / `--resolve-changed --since-commit` / banked-fingerprint = **`78ceaead`** (S34 close). S36 Day-0 code state = S35 close `597d9d08` (prep was docs-only). Ref: `PLAN.md` §4, §18; `DAY0_TRACE_NOTES.md` (Task 2).

---

## 1. Baseline (142 convex candidates) — reproduces exactly

Recomputed from the committed DB:

| KPI | Measured | Expected (S35 close) |
|---|---|---|
| convex candidates | 142 | 142 |
| Solve | **108** | 108 |
| Match | **93** (63 cold-optimal + 30 presolve) | 93 (63 + 30) |
| genuine floor | **75** | 75 |
| model_infeasible | 7 | 7 |
| path_syntax_error | 7 | 7 |
| all-219 Match | 96 | 96 |
| Translate / Parse | 135 / 142 | 135 / 142 |

**DB byte-unchanged since the anchor** (`git diff 78ceaead..HEAD -- data/gamslib/gamslib_status.json` = empty → 0 bucket move).

## 2. Code anchor — only the turkey delta

- `git diff 78ceaead..HEAD -- src/` = **only `src/emit/original_symbols.py` (+52)** — the Day-6 turkey `_infer_domainless_tuple_arity` compile-recovery. No other `src/` drift.
- `scripts/` delta = the presolve-divergence allowlist (+9: korcge, robustlp) + `kkt_residual.py` / `test_solve.py` harness (GAMS-54 bump). All unrelated to the markov/fawley/sarf/ganges emit paths.
- **`src/kkt/stationarity.py` UNCHANGED · `src/ad/derivative_rules.py` UNCHANGED** since the anchor → the markov `stat_z` residual and the ganges cascade reproduce **deductively** (identical emit path). `_diff_prod` present (`derivative_rules.py:3276`); `_expr_contains_varref_attribute` present (`original_symbols.py:1392`).

## 3. Banked fingerprints — re-confirmed

| track | fingerprint | Day-0 status |
|---|---|---|
| **markov** | `CASE_B` `max\|stat_z\|` rel 13.3; Part-1 diagonal split → 1.55 | ✅ deductive (stationarity.py + derivative_rules.py byte-unchanged since the Day-11 measurement tree) |
| **fawley** | the discriminator: fire only when the summed constraint index is ABSENT from the derivative coefficient (disjoint from markov) | ✅ design-stable (Task 4; emit path unchanged) |
| **sarf** | O(active) (369K `task` blow-up) | ✅ (Task 5; parser/emitter unchanged) |
| **ganges** | `$141`×15 / `$145` / `$149` cascade → `$66` → `rPower`; `_diff_prod:3276` unchanged | ✅ (Task 6; AD path byte-unchanged, `a8ff626c` banked) |
| **camcge** | S1∧S2∧S3 detector fires ONLY camcge (MS-4 @ omega 191.7346); siblings irscge/lrgcge/moncge/stdcge MS-1 + match | ✅ re-confirmed from the DB |
| **robustlp** | EXECERROR-84 "Matrix error - illegal level value"; NA multiplier `.L` | ✅ re-reproduced live (see §3.1) |

### 3.1 robustlp — re-reproduced + mechanism sharpened

Re-ran the (byte-unchanged) `robustlp_mcp_presolve.gms` under GAMS 54.2.1 demo: **`Matrix error - illegal level value`**, `Bound [min,max] = [NA, NA]`, `lam_socpqcpcons(1..7)` / `piL_y(1..7)` `.L = NA`. The abort reproduces.

**Mechanism sharpened (strengthens Task 9 §4, does not contradict it):** the equation listing also shows `stat_v(1,1).. (NA)*v(1,1) + …` — an NA *coefficient* on `v`. Tracing it: the emitted `stat_v(i,k).. nu_defv(i,k) + 2*v(i,k)*lam_socpqcpcons(i) =E= 0` has coefficient `2*lam_socpqcpcons(i)` on `v`, and since `lam_socpqcpcons.L = NA` (the multiplier warm-start level), that bilinear coefficient evaluates to `2·NA = NA`. **So the `(NA)*v` coefficient is DOWNSTREAM of the same NA `.L` root — not a separate NA param.** The single bounded P7 fix (NA-guard the presolve marginal→multiplier `.L` warm-start transfer, Task 9 §4) therefore clears **both** the "illegal level value" abort **and** the `(NA)*v` stat_v coefficient. The Task-9 root + de-allowlist plan stand, now with the propagation mechanism pinned (Day-10 P7).

## 4. PR25 tally — the markov +1 is real

markov: `model_optimal_presolve` + match, `verified_convex` → **in the 30-model presolve-match (methodology) partition**. So fixing markov's cold emit (P1) moves it *out* of methodology *into* the genuine floor — a **true +1** (75 → 76), not a double-count.

## 5. Known-Unknowns Day-0-blocker clearance

- **10/10 prep tasks COMPLETE.**
- **All 30 unknowns resolved — zero INCOMPLETE:** 28 ✅ VERIFIED; 6.1 ❌ WRONG → bounded Day-0 risk (no licensed >1000-row testbed; the re-baseline is demo-runnable, only turkey's +1 is license-gated → deferred); 6.2 🔍 BLOCKED → deferred (turkey solve).

## 6. GO / NO-GO

**⇒ GO for Sprint 36 Day 1.** Baseline exact; anchor clean; every fingerprint re-confirms; the one local +1-floor lever (markov) is ready to front-load Days 1–3 with its `σ=sp` REPLAN surfacing by Day-5 Checkpoint 1; no Day-0 blocker (the sole external dependency, turkey's testbed solve, is bounded + deferred). Standing BANs restated: **`modelstat` asserted before every objective read; `x.up=inf` BANNED (mine); the Case-c objective-gradient sign flip BANNED.**

Honest projection (`PLAN.md` §2): **genuine floor 75 or 76 (markov-contingent); Solve 108–110 (P4-bimodal); Translate 135 or 136 (sarf); robustlp de-allowlisted; turkey +1 testbed-deferred.**

---

**Document Status:** ✅ Complete — Sprint 36 Day 0 (kickoff + GO for Day 1)
**Last Updated:** 2026-08-07 · **Owner:** Sprint 36 Execution Team
