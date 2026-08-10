# ISSUE #1111 — fawley `stat_bq`: constraint-index-diagonal over-count

> **Scope.** This doc addresses **#1111 only** (alias/subset-aware index matching). The Sprint-36/37 planning docs refer to the track as "fawley #1111/#1112" because it sits in that architectural family, but the defect fixed here is a *name-based* domain-overlap test missing a declared **subset** relationship — squarely #1111. **#1112** (dollar-condition propagation through the AD/stationarity pipeline) is *not* addressed: the `$(sameas(…))` guard is the fix's **mechanism**, not the broken machinery. No #1112 claim is made and no companion doc is implied.

**Status:** 🔶 DESIGN COMPLETE, **NOT LANDABLE YET** — correctness control-verified, but the full-corpus leak gate **FAILED** (see *Leak status*). Do not implement as-is.
**Sprint:** 37 (P4, 0-bucket / H-b) · **Prep:** Task 6 · **Issue:** #1111 (family: #1111/#1112)
**File:** `src/kkt/stationarity.py` — `_add_indexed_jacobian_terms`, the "truly disjoint by NAME" branch (`:7069–7096`)
**Design:** `docs/planning/EPIC_4/SPRINT_37/FAWLEY_DISCRIMINATOR_REFRESH.md`

## Problem

`stat_bq(c,cf)` sums its `qsb` and `pbal` multiplier terms over the **whole** constraint
domain — `sum((cfq__,l,s), …·nu_qsb(cfq__,l,s))` and `sum((cfq__,m), …·nu_pbal(cfq__,m))` —
even though their coefficients do not depend on `cfq__`. That is a pure over-count
(`max|stat_bq|` = 473.4, rel 0.973).

**Root cause (located this task).** `qsb(cfq,l,s)` / `pbal(cfq,m)` vs `bq(c,cf)`: the emitter
tests domain overlap **by name**, and `cfq ∉ {c, cf}`, so the pair is classified *"truly
disjoint by NAME"* and the whole multiplier domain is summed. But `cfq` is **declared as a
subset of `cf`** (`Set cfq(cf)`), so it is not an independent iteration index — the per-cell
derivative already collapsed to the diagonal. `_dual_binding_map` returns `None` here
(instrumented), so control falls to the `Sum(mult_domain, term)` fallback.

## Fix (design)

Make the disjoint branch **subset-aware**: a multiplier-domain index declared as a subset of a
variable-domain index binds to that index rather than being summed independently — emitted as a
`sameas` guard, mirroring the Issue #1393 handling already present on the *scalar*-constraint
branch (`:7251`, via `_subset_alias_superset_index`). The mechanism exists; it is simply absent
from this branch.

**Control-verified (Prep Task 6):** the scratch predicate produced exactly the Day-9 target form
— `stat_bq` went from **1** `sameas` (the pre-existing `mbal` one) to **3** (`mbal` + `qsb` +
`pbal`) — and `stat_bq` **dropped out of the KKT-residual top rows entirely** (baseline rel
0.973), leaving only the emit-correct `stat_trans(tr-2)`.

#### Leak status — the gate FAILED (measured, Prep Task 6)

`make leak-check MODEL=fawley` was run twice against the scratch predicate:

| predicate | verdict |
|---|---|
| conjunct 1 (subset-aware binding) alone | `LEAK: dinam, prolog, shale` |
| + conjunct 2 (coefficient independent of the summed index) | `LEAK: dinam, shale` (`prolog` excluded; `dinam` +190 → +40 B) |

**`prolog` is a live `model_optimal` + *match* model**, so conjunct 1 alone risked a Match
regression. All three leak models are **outside** the Sprint-36 6-model cohort — a cohort-only
check would have shown clean. The `shale` drift adds `$(sameas(t, tf))` to six `stat_z` sums;
whether that is a correction or a regression is unresolved.

**⇒ the predicate must be narrowed further before any `src/` commit.**

## Phase 0: Acceptance Gate

### Correctness

`python scripts/diagnostics/kkt_residual.py data/gamslib/raw/fawley.gms` must show **no
`stat_bq` row** among the reported residuals (baseline: `stat_bq(res-arab-l,fuel-oil)` rel
**9.73e-01** and siblings). The verdict **remains `CASE_B`** — that is expected and not a
failure: the harness max is the *emit-correct* `stat_trans(tr-2)` rel 1.00, an H-b divergence
outside this issue's scope.

### Leak-freedom (full corpus — MANDATORY)

`make leak-check MODEL=fawley` must print the **unqualified** `LEAK GATE PASS` (a `PARTIAL`
verdict fails — it means the sweep was narrowed). This asserts that of all 163 in-scope goldens
**only** `fawley_mcp.gms` / `fawley_mcp_presolve.gms` drift; **markov** and the 2-D cohort must
be byte-identical (the Sprint-35 fawley→markov leak precedent). Any `LEAK:` or `NO-OP:` line
fails. Do **not** clear drift with `make regen-goldens` — that launders a leak into the goldens.

### Bucket / KPI (expected: none)

fawley is **H-b**: even with `stat_bq` fully closed the MCP stays MS-5 (LP optimum 2899.25),
and the Sprint-36 `--force` survey was **NEGATIVE** (homotopy/multistart/optfile all MS-5). So
this fix must be landed as a **0-bucket correctness improvement** — Solve/Match/genuine floor
must all be **unchanged** (108/93/75), and the DB must not move. Claiming a bucket gain here
would be wrong; the +Solve is a Sprint-38 PATH-consultation question.

### Regression guard

`shape_fawley_2d_second_index` (fast, in-process) must **fail before** and **pass after**,
asserting `stat_bq`'s `qsb` and `pbal` terms each carry `$(sameas(cfq__, cf))` — i.e. the
`sameas` count in `stat_bq` is **3**, not 1. It must `pytest.skip` when
`data/gamslib/raw/fawley.gms` is absent (CI lacks the raw corpus). Full quality gate
(`make typecheck && make format && make lint && make test`) green.

## Mutual exclusion with the markov P1 change (both touch `_add_indexed_jacobian_terms`)

Structurally disjoint, in **both** directions:

1. This fix sits under `elif not _did_dim_mismatch_alias_fix:` (`:7060`); the markov `σ=sp` fix
   sits on the dim-mismatch/offset-group path, which is exactly the path that **sets that flag
   `True`** (`:6925`). They are alternative branches of the *same* if/elif chain — a term that
   took markov's path cannot reach this one.
2. fawley declares **no aliases at all**, so markov's conjunct-(1) collision signature is
   structurally unsatisfiable there (Prep Task 4, measured).

Recommended land order: markov (P1) → `make leak-check MODEL=markov` → fawley (P4) →
`make leak-check MODEL=fawley`.

## REPLAN exit

The first two rungs of this ladder have **already been tried and both leaked** (see *Leak
status*): conjunct 1 alone, and conjunct 1 + the `_collect_free_indices` absence test from the
Sprint-36 design. The next refinement to try is that conjunct-2 test's **name matching**: it
compares the raw `mult_domain` index name, which misses the AD layer's `__`-suffixed
re-symbolization (`cfq` vs `cfq__`), so it likely under-fires on `dinam`/`shale`. Compare on the
suffix-stripped canonical name, and/or require the subset's parent to be the *specific* var-domain
index the coefficient actually references.

If that still leaks, **re-defer**. fawley is 0-bucket, so it must never be shipped at the cost of
a shared-function regression — and `prolog` (a live match) is in the blast radius.

## References

- `docs/planning/EPIC_4/SPRINT_36/DAY4_FAWLEY_DEFER.md` — the correctness target + the "path ≠ assumed branch" finding
- `docs/planning/EPIC_4/SPRINT_36/FAWLEY_DISCRIMINATOR_DESIGN.md` — the original discriminator spec
- `docs/planning/EPIC_4/SPRINT_36/DAY11_P5_CONSULTATION.md` §4 — the `--force` survey (NEGATIVE)
- `docs/planning/EPIC_4/SPRINT_37/LEAK_HARNESS_DESIGN.md` — the `make leak-check` gate
