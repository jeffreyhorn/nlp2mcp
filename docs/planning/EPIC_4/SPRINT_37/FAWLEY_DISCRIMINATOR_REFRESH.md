# fawley P4 — Emission-Path Location & Constraint-Index-Diagonal Discriminator (Prep Task 6)

**Date:** 2026-08-10 · **Branch:** `planning/sprint37-task6` · **Scope:** docs/analysis-only — a scratch `src/` predicate was implemented for control purposes and **reverted** (`src/kkt/stationarity.py` byte-identical to the anchor `78ceaead`).

**One line:** the emission path is **located** (the Day-4 blocker), the correctness fix is **control-verified in `src/`** (not a hand-edit) — and then Task 3's leak gate, on its **first production use, caught a real leak** that the Sprint-36 6-model cohort would have missed, including onto **`prolog`, a live *matching* model**. Two predicate refinements reduced the leak from 3 models to 2; it is **not yet leak-free**, so fawley stays deferred with a much sharper spec.

Reference: `SPRINT_36/DAY4_FAWLEY_DEFER.md` (the DEFER + "path ≠ assumed branch"), `FAWLEY_DISCRIMINATOR_DESIGN.md`, `DAY11_P5_CONSULTATION.md` §4. Phase-0 doc: `docs/issues/ISSUE_1111_fawley-constraint-index-diagonal.md`.

---

## 1. The emission path — LOCATED (Unknown 4.1)

Sprint 36 Day 4 established only what it is *not*: the partial-overlap branch (0 firings for `var=bq`). Instrumenting `_add_indexed_jacobian_terms` for `var_name == "bq"` gives the answer directly:

```
[BQ] DISJOINT branch: mult_domain=('cfq','l','s')  var_domain=('c','cf')  dual_binding=None
[BQ] DISJOINT branch: mult_domain=('cfq','m')      var_domain=('c','cf')  dual_binding=None
```

Both `qsb` and `pbal` take the **"truly disjoint by NAME"** branch (`src/kkt/stationarity.py:7069–7096`) and fall through to the `else: term = Sum(mult_domain, term)` fallback at **`:7096`**, because `_dual_binding_map` returns `None`.

**Why:** the branch tests domain overlap **by name** — `mult_domain_set.intersection(var_domain_set)` — and `cfq ∉ {c, cf}`, so `qsb(cfq,l,s)` looks independent of `bq(c,cf)`. But `cfq` is **declared as a subset of `cf`**:

```
Set cfq(cf)      →  model_ir.sets['cfq'].domain == ('cf',)
```

so it is *not* an independent iteration index — the per-cell derivative already collapsed to the diagonal, and summing over the whole domain over-counts. That is exactly the missing `$(sameas(cfq__, cf))`.

**The mechanism already exists elsewhere.** The scalar-constraint branch handles this precise shape via Issue #1393 (`_subset_alias_superset_index`, `:7251`) — and its comment names fawley explicitly (*"whether the summed parameter is declared over the subset (**fawley `pcr(cr)`**) or the parent (otpop `del(tt)`)"*). Two mis-hypotheses were tested and rejected before landing on the answer: the `:7120` uncontrolled-free-index branch (a `_subset_alias_superset_index` fallback there changed nothing — `sameas` count stayed 1), and the fresh-alias branch at `:6946` (that one mints `root__kktN`, markov's convention, not the AD layer's `cfq__`).

## 2. The predicate + the correctness control

**Conjunct 1 (orientation, rebuilt):** in the disjoint branch, a multiplier-domain index declared as a **single-parent subset** of a variable-domain index binds to it — emitted as `$(sameas(<mult_idx>, <var_idx>))` — instead of being summed independently.

**Result (scratch `src/`, fawley re-emit):**

| | baseline | with the predicate |
|---|---|---|
| `sameas` count in `stat_bq` | **1** (the pre-existing `mbal`) | **3** (`mbal` + `qsb` + `pbal`) ✔ |
| `kkt_residual.py fawley` | `stat_bq(res-arab-l,fuel-oil)` rel **9.73e-01** among the top rows | **`stat_bq` absent from the residual rows entirely** ✔ |
| harness max | `stat_trans(tr-2)` rel 1.00 | `stat_trans(tr-2)` rel 1.00 (unchanged — the H-b divergence) |

This reproduces the Day-9 hand-edit target (`473 → 1.14e-13`) **from a real `src/` change**, closing the correctness question.

## 3. The leak gate caught a real leak — twice (Unknown 4.2, leak axis)

`make leak-check MODEL=fawley` (Task 3's instrument, **first production use**):

| run | predicate | verdict |
|---|---|---|
| **v1** | conjunct 1 only | `LEAK: 3 unexpected model(s) drifted: dinam, prolog, shale` |
| **v2** | + conjunct 2 (the S36 discriminator: the coefficient must **not** depend on the summed index) | `LEAK: 2 unexpected model(s) drifted: dinam, shale` — `prolog` excluded, `dinam` drift shrank +190 → +40 B |

**Severity matters here, and it is not uniform:**

| model | DB status | risk of the drift |
|---|---|---|
| **prolog** | `model_optimal` + **match** | **HIGH — a live matching model.** v1 drifted it (+17 B); conjunct 2 excluded it. Landing v1 could have cost a Match. |
| dinam | `path_syntax_error`, not_tested | structurally-wrong emit change; no live match at risk |
| shale | `path_solve_license`, not_tested | same |

**What the shale drift actually is** (diffed): the predicate adds `$(sameas(t, tf))` to `stat_z(p,tf)`'s `sum((crs,t), a(crs,p)·nu_msu(crs,t))` and five sibling terms. Whether that is a *correction* (∂msu(crs,t)/∂z(p,tf) plausibly being nonzero only at `t = tf`) or a *regression* cannot be settled from a design task — and under the byte-identical discipline any unintended drift is a leak that must be resolved **before** landing, not argued away.

**This is the Sprint-36 lesson repeating, and being caught this time.** All three leak models — `dinam`, `prolog`, `shale` — are **outside** the 6-model cohort (cesam2/camcge/ps2_f_s/ps2_s/ps3_s_gic/polygon) that Sprint 36 relied on. A cohort-only check would have shown clean and shipped a Match-threatening change.

## 4. Mutual exclusion with the markov P1 change (Unknown 4.2, collision axis)

Disjoint **structurally, in both directions** — stronger than Task 4 alone established:

1. **Same if/elif chain, opposite branches.** This fix sits under `elif not _did_dim_mismatch_alias_fix:` (`:7060`); the markov `σ=sp` fix sits on the dim-mismatch/offset-group path — the path that **sets that very flag `True`** (`:6925`). A term that took markov's path cannot reach fawley's branch, and vice versa.
2. **fawley declares no aliases at all**, so markov's collision signature (an alias-canon match across ≥2 variable positions) is structurally unsatisfiable there (Task 4, measured: `domain_gate_pairs: []`).

Land order: markov → `make leak-check MODEL=markov` → fawley → `make leak-check MODEL=fawley`.

## 5. +Solve is H-b — a Sprint-38 consultation, not an emit fix (Unknown 4.4)

Re-confirmed this task: with `stat_bq` fully corrected, the harness max is still `stat_trans(tr-2)` rel **1.00** — an **emit-correct** divergence. fawley's MCP stays MS-5 (LP optimum 2899.25), and Sprint 36's `--force` survey was **NEGATIVE** (homotopy/multistart/optfile all MS-5). So this fix is **0 bucket by construction**; the +Solve needs a stronger continuation/reformulation, which is the Sprint-38 PATH-consultation question.

## 6. Disposition: still deferred, with a much sharper spec

**The correctness fix is ready; the gate is not passed.** Remaining work for the dedicated effort — all now precisely bounded:

1. Narrow conjunct 2 so `dinam` and `shale` stop drifting. The current test (`mult_idx ∉ _collect_free_indices(coefficient)`) is name-based and misses the AD layer's `__`-suffixed re-symbolization, which is likely why it under-fires. Candidate: compare on the **suffix-stripped canonical** name, and/or require the subset to be a *proper* single-parent subset of the specific var index the coefficient references.
2. Re-run `make leak-check MODEL=fawley` to the **unqualified** `LEAK GATE PASS`.
3. Land with the `shape_fawley_2d_second_index` fixture (§7) and 0-bucket KPIs asserted unchanged.

## 7. `shape_fawley_2d_second_index` fixture spec

- **Type:** fast, in-process (runs in `make test`); `pytest.skip` when `data/gamslib/raw/fawley.gms` is absent (CI lacks the raw corpus).
- **Asserts:** `stat_bq`'s `qsb` (`nu_qsb(cfq__,l,s)`) and `pbal` (`nu_pbal(cfq__,m)`) terms each carry `$(sameas(cfq__, cf))` — i.e. the `sameas` count in `stat_bq` is **3**, not 1.
- **Fail-before (measured, not assumed):** the committed golden has exactly **1** `sameas` in `stat_bq`, so the assertion fails today and passes after.

---

## 8. Known-Unknown dispositions

| Unknown | Verdict | Basis |
|---|---|---|
| **4.1** where the `qsb`/`pbal` emission path actually runs | ✅ VERIFIED | §1 — instrumented: the **"truly disjoint by NAME"** branch (`:7069–7096`), falling to `Sum(mult_domain, …)` at `:7096` with `dual_binding=None`, because `cfq ⊂ cf` is a *subset* relationship the name-based overlap test misses. Two competing hypotheses tested and rejected. |
| **4.2** the predicate can be rebuilt + co-exist with markov, full-corpus leak-clean | 🔶 PARTIAL — rebuild ✅, markov co-existence ✅, **leak-freedom ❌ REFUTED (twice)** | §2 the predicate is rebuilt and correctness-verified (`sameas` 1→3; `stat_bq` out of the residuals). §4 markov exclusion is structural in both directions. **But** §3: `make leak-check MODEL=fawley` reports `LEAK` on `dinam, prolog, shale` (v1) and `dinam, shale` (v2) — **not leak-free**, so it must not land. |
| **4.4** fawley's +Solve is H-b → a Sprint-38 consultation | ✅ VERIFIED | §5 — with `stat_bq` corrected the harness max is still the emit-correct `stat_trans(tr-2)` rel 1.00; MCP stays MS-5; the S36 `--force` survey was NEGATIVE. 0 bucket by construction. |

---

**Document Status:** ✅ Complete — Sprint 37 Prep Task 6 (fawley emission-path location + discriminator design; deferred, leak-freedom not yet achieved).
**Last Updated:** 2026-08-10 · **Owner:** Sprint 37 execution team
