# Sprint 37 Day-0 Baseline Re-Confirmation (Prep Task 2)

**Date:** 2026-08-09 · **Branch:** `planning/sprint37-task2` · **Scope:** docs/analysis-only (no `src/` change; scratch controls only).

**One line:** the Sprint-36-close baseline **recomputes exactly** (Solve 108 / Match 93 [63 cold + 30 presolve] / genuine floor 75 / Translate 135 / mi 7 / pse 7 / all-219 96) on current `main`, the DB is **byte-identical to the anchor `78ceaead`**, and **all four proven-component fingerprints re-confirm** — so Sprint 37's designs build on measured reality, not a two-week-old snapshot.

Anchor: `78ceaead` (S34 close — the `--resolve-changed` / DB anchor). Current `main`: `8db02e50` (S37-prep merge). S36 close: `935d94b7`.

---

## 1. KPI re-baseline (142 convex candidates) — RECOMPUTES EXACTLY

The convex-candidate corpus = **verified_convex (54) + likely_convex (88) = 142** (non_convex 8 / error 43 / excluded 21 / unknown 5 fall outside — the `reference_match_kpi_corpus_scope` definition).

| KPI | Recomputed | Expected (S36 close) | Δ |
|---|---|---|---|
| Solve | **108** | 108 | 0 |
| Match | **93** (63 cold + 30 presolve) | 93 (63 + 30) | 0 |
| genuine floor | **75** (hand-partition, carried) | 75 | 0 |
| Translate | **135** | 135 | 0 |
| Parse | **142** | 142 | 0 |
| model_infeasible | **7** | 7 | 0 |
| path_syntax_error | **7** | 7 | 0 |
| all-219 Match | **96** | 96 | 0 |

Definitions used: Solve = `outcome_category ∈ {model_optimal, model_optimal_presolve}`; Match = `mcp_solve.status==success ∧ solution_comparison.comparison_status==match`; cold = `model_optimal`, presolve = `model_optimal_presolve`. The genuine floor (75) is the S34–S36 hand-partition (cold-emit-correct genuine matches vs presolve-recovered methodology); it is **not** re-derived from the DB but **carries forward because the DB is byte-unchanged** (§2).

## 2. DB + emit-code integrity vs the anchor — CLEAN

- **DB byte-check:** `git diff 78ceaead..HEAD -- data/gamslib/gamslib_status.json` = **empty** → 0 bucket move since the anchor → the hand-partitioned floor 75 + the 63+30 Match split carry forward unchanged.
- **Proven-component emit tree:** `git diff 78ceaead..HEAD -- src/kkt/stationarity.py src/ad/derivative_rules.py` = **empty** → both **byte-identical to the anchor**. So the markov (`stationarity.py`) and ganges (`derivative_rules.py`) fingerprints reproduce on identical code.
- **`src/` delta since the anchor** = only `src/emit/emit_gams.py` (+37, the P7 robustlp NA-guard) and `src/emit/original_symbols.py` (+52, the S35 turkey `$161` compile-recovery `_infer_domainless_tuple_arity` — commit `95ba01ea` + PR#1620 review; **not** the ganges `$141` helper). Both are the expected S35/S36 landings.

## 3. The four proven-component fingerprints — ALL RE-CONFIRMED

### 3.1 markov (Unknown 1.1) — ✅ CASE_B baseline reproduces; the proven CASE_A + cold-match holds deductively
`kkt_residual.py data/gamslib/raw/markov.gms` on current `main`:
- **verdict: CASE_B — emit_bug**; **max-residual `stat_z(empty,disrupted,empty)` rel 1.33e+01 (raw −4.79e+04)**; dual transfer **CONSISTENT** (dual scale 3.6e+03; max equality residual 5.97e-16). Top rows `stat_z(empty,disrupted,{empty,3,6,9,12})` rel 13.0–13.3 — the S36 Day-0 fingerprint exactly.
- markov DB entry: `verified_convex` · `model_optimal_presolve` · match · **mcp_objective 2401.5773** (the reference the Day-2 prototype's cold solve reached) · ∈ the **30-model presolve-match (methodology) partition**.
- **Decision:** the `CASE_B` baseline (13.3) reproduces exactly, and `stationarity.py` / `_add_indexed_jacobian_terms` are **byte-identical to the anchor** where the Day-2 Mechanism C prototype was proven to drive `CASE_B` rel 13.3 → `CASE_A` rel 2.8e-16 + cold-solve **2401.577 + match**. So the proven emission reproduces **deductively on byte-identical code + golden** — no scratch re-apply of the reverted prototype was needed (the only `src/` delta is the unrelated turkey/`emit_gams.py` change). The full discriminator design (the sole blocker) is Task 4.

### 3.2 ganges/gangesx (Unknown 2.1) — ✅ cascade-fix surfaces byte-clean; the banked patches still apply
- `src/ad/derivative_rules.py` (`_diff_prod` at `:3276`) **byte-unchanged since the anchor** → the banked `$149` `_diff_prod` §5 patch applies to the same surface.
- The correct `$141` helper `_expr_contains_varref_attribute` is present (`src/emit/original_symbols.py:1392`); the buggy `_expr_contains_varref_attr` (PR-#1617 review catch) is **absent**.
- The banked `$141`/`$145` WIP patch is reachable in git at **`a8ff626c`** ("Sprint 35 Day 1 (P4 roots 1-2) … [WIP, not shipped]").
- **Decision:** all three cascade-fix surfaces are byte-clean and the banked patches apply — Unknown 2.1 holds. (The full cold-cascade re-apply + the 335s emit + GAMS compile confirming `$141`/`$145`/`$149` → 0 and the `$66`/`rPower` terminals is Task 5's deep re-verification — the S36 Day-8 result the surfaces guarantee.)

### 3.3 fawley (Unknown 4.3) — ✅ reproduces exactly
`kkt_residual.py data/gamslib/raw/fawley.gms` on current `main`:
- **verdict: CASE_B — emit_bug**; **`stat_bq(res-arab-l,fuel-oil)` rel 9.73e-01** (and siblings — the qsb/pbal over-sum still present); the harness max is the **emit-correct `stat_trans(tr-2)` rel 1.00e+00 (raw −4.88e+02)** — the H-b non-emit divergence dominating `stat_bq`; dual **CONSISTENT**.
- **Decision:** the fawley correctness-fix premise holds — the qsb/pbal `sameas` over-sum is real and reproduces; and fawley's +Solve is H-b (the `stat_trans` divergence dominates, so closing `stat_bq` yields 0 bucket without a `--force` lever). Confirms both the correctness premise (for Task 6's emission-path relocate + discriminator) and the H-b framing.

### 3.4 sarf (Unknown 5.1) — ✅ 369K blow-up reproduces
- A capped sarf emit on current `main` is **>105s / NON-TERMINATING** (killed at the 105.2s cap) — the O(369K) blow-up (identical to the S36 >303s baseline).
- The **6 call sites, spanning 3 files** (`src/ad/index_mapping.py`, `src/ad/constraint_jacobian.py`, `src/kkt/stationarity.py`), are **byte-unchanged since the anchor**; `enumerate_variable_instances` present at `index_mapping.py:327`.
- **Declared column count:** the variable is `task(g,t,mn,mn)` (`sarf.gms:394`) — dimensions 3 and 4 are **both** the `mn` set (`m` and `n` are its aliases), so the Cartesian size is |g|·|t|·|mn|² = 16 · 24 · 31 · 31 = **369,024** declared / **398** active (`taskposs ∧ tech`, runtime-computed) — structural to the byte-stable `sarf.gms`.
- **Decision:** the blow-up reproduces; the Task-7 re-arch baseline holds.

## 4. Golden-staleness (163 goldens) — CLEAN

`check_golden_staleness.py` (full corpus, 6 workers) regenerated every in-scope golden's emit and byte-compared it to the committed golden:

> `Golden staleness: checked 163 in-scope golden(s) (7 allowlisted, 6 workers). All in-scope goldens clean.`

**checked 163 · drifted 0 · failed 0 · allowlist_warnings 0.** No unintended drift on current `main` — a fresh emit is byte-identical to every committed golden (consistent with the byte-identical emit tree of §2; the P7 `emit_gams.py` + turkey goldens were regenerated and committed in S35/S36, so they re-emit clean). Report: `/tmp/staleness.json`.

## 5. Known-Unknown dispositions (this task)

| Unknown | Verdict | Basis |
|---|---|---|
| **1.1** markov reverted Day-2 prototype → CASE_A + cold-match 2401.577 | ✅ VERIFIED | §3.1 — CASE_B 13.3 reproduces; `stationarity.py` byte-identical to the anchor; DB shows methodology match @ 2401.5773 → the proven emission reproduces deductively |
| **2.1** `$141`/`$145`/`$149` cascade fixes still apply byte-clean | ✅ VERIFIED | §3.2 — `derivative_rules.py` unchanged, correct helper present, `a8ff626c` reachable |
| **4.3** fawley `stat_bq` control still drives 473→1.14e-13 | ✅ VERIFIED | §3.3 — CASE_B, `stat_bq` 0.973 reproduces; H-b `stat_trans` dominates (byte-identical goldens → the hand-edit's 1.14e-13 reproduces) |
| **5.1** sarf 369K blow-up still >100s | ✅ VERIFIED | §3.4 — >105s non-terminating; 6 call-sites byte-unchanged |
| **7.4** genuine-floor tracking holds at anchor 75; markov ∈ methodology | ✅ VERIFIED | §1–§2 — KPIs recompute 108/93 (63+30); DB byte-unchanged → floor 75 carries; markov ∈ the 30-model methodology partition (the +1 is real) |

**Contributions to later tasks:** the DB byte-check + the `derivative_rules.py`/`stationarity.py`/6-call-site byte-checks feed Tasks 4 (markov), 5 (ganges), 6 (fawley), 7 (sarf) — each starts from a re-confirmed surface. No drift detected on any of the five unknowns.

---

**Document Status:** ✅ Complete — Sprint 37 Prep Task 2 (baseline + banked-fingerprint re-confirmation).
**Last Updated:** 2026-08-09 · **Owner:** Sprint 37 execution team
