# GAMS-54 v54 Re-Baseline Plan + turkey Testbed Procurement (Prep Task 8)

**Date:** 2026-08-10 · **Branch:** `planning/sprint37-task8` · **Scope:** docs/analysis-only — measurements under GAMS 54.2.1; the DB was snapshotted, mutated by a scoped re-solve, and **restored byte-identical** (md5 `6166acab…` before and after). No `src/` change.

**One line:** turkey is **definitively license-gated** (measured: 3,866 rows, the exact demo refusal, and a *clean* compile — the +1 is real but unrealizable), the v54 risk set shows **zero regressions** (all 5 OBJ-GAP models identical under v54, chain's objectives byte-identical), and a full re-baseline is a **~30-minute** operation — plus one thing no bank carried: **turkey's DB entry is stale by seven weeks and one landed fix.**

Reference: `SPRINT_36/GAMS54_TESTBED_PLAN.md` §3–§4, `SPRINT_35/FOLLOWUPS_GAMS54_TRANSITION.md`.

---

## 1. turkey testbed procurement — NO licensed environment exists (Unknown 6.1)

Checked every candidate path:

| candidate | finding |
|---|---|
| local GAMS 51 | `GAMS_Demo, for EULA and demo limitations see …` |
| local GAMS 53 | `GAMS_Demo, …` |
| **local GAMS 54.2.1** | `GAMS_Demo, …` (the version the project now uses) |
| CI secrets | only `PYPI_API_TOKEN` — **no GAMS license secret**; the workflows install the public demo installer |

**No licensed >1000-row GAMS-54 environment is available locally or in CI, and none is procurable from within the repo.** Acquiring one is a purchasing decision outside the sprint's control.

### turkey's block, measured precisely

Compiling the committed `turkey_mcp.gms` under GAMS 54.2.1:

```
BLOCKS OF EQUATIONS  89     SINGLE EQUATIONS   3,866
BLOCKS OF VARIABLES  89     SINGLE VARIABLES   3,753
**** The model exceeds the demo license limits for nonlinear models of more than 1000 rows or columns
**** Terminated due to a licensing error
```

**3,866 single equations — exactly the banked figure, now measured rather than cited.** Critically, the compile is otherwise **clean: zero `$NNN` errors**. So the S35 Day-6 `$161` compile-recovery genuinely worked, and **the license is the *only* remaining blocker** — turkey's +1 Solve/Match is real and would be realized immediately on a licensed run.

**Verdict: turkey's +1 stays deferred, license-gated.** Not a technical blocker, not something more prep effort can move.

### A stale-DB finding no bank carried

turkey's DB entry records:

```
outcome: path_syntax_error   solve_date: 2026-06-20   error: "Parse error: compilation_error"
```

But the measured state today is a **clean compile blocked only by the license** (`path_solve_license` in the project taxonomy). The S35 `$161` fix landed **2026-08-03** — seven weeks *after* that solve date. The entry was never refreshed because `--resolve-changed` **deliberately never persists** its mutation (`run_full_test.py:1267` — "Snapshot the working DB so the checkpoint never persists"), so the S36 Day-13 checkpoint confirmed `path_solve_license` without writing it.

**Consequence for the re-baseline:** a *persisting* re-solve will move turkey `path_syntax_error → path_solve_license`, i.e. **`path_syntax_error` 7 → 6** — with **no change to Solve or Match**. That is a **stale-entry correction, not a v54 effect**, and §3's decision rule must classify it as such or it will look like a spurious v54-induced change.

## 2. The v54 risk set shows ZERO regressions (Unknown 6.3)

Sprint 36 named the 5 OBJ-GAP models (`agreste`, `cesam`, `chain`, `fawley`, `rocket`) as the v54-strictness risk set. Re-solved all five under **GAMS 54.2.1** (DB snapshotted → run → restored byte-identical):

| model | v53 (DB) | **v54 (measured)** | Δ |
|---|---|---|---|
| agreste | `model_infeasible` | `model_infeasible` | — |
| cesam | `model_infeasible` | `model_infeasible` | — |
| **chain** | `model_optimal_presolve`, mismatch, nlp 5.0723 / mcp 5.1199 | `model_optimal_presolve`, mismatch, **nlp 5.0723 / mcp 5.1199** | — (objectives **byte-identical**) |
| fawley | `model_infeasible` | `model_infeasible` | — |
| rocket | `model_infeasible` | `model_infeasible` | — |

**Zero bucket changes, and not even a numerical drift on chain.** The models most likely to move under v54's stricter behaviour do not move at all — materially de-risking the re-pin decision.

**Measured cost** (the same run): agreste 0.85 s · chain 10.5 s · fawley 12.7 s · rocket 31.9 s ⇒ ~12 s/model average. **A full 142-candidate re-baseline is therefore a ~30-minute operation** — well within a sprint day, not the blocker the bank implied.

## 3. The v54 re-baseline procedure + decision rule (Unknown 6.2)

### Procedure

1. **Snapshot** the DB (`cp data/gamslib/gamslib_status.json` + record md5) — the re-baseline is the *one* operation that legitimately persists, so an explicit restore point is mandatory.
2. **Re-solve** the 142 convex candidates under GAMS 54 demo:
   `PATH=/Library/Frameworks/GAMS.framework/Versions/54/Resources:$PATH scripts/gamslib/run_full_test.py --only-solve` (scoped to the convex corpus). ~30 min.
3. **Diff buckets** against the v53 DB snapshot, per model, into **`GAMS54_REBASELINE_DIFF.md`**.
4. **Re-check** the OBJ-GAP models explicitly (§2 gives the expected answer: no change). ⚠ **The set is 8, not 5** — corrected at Sprint 37 Checkpoint 1 (Day 5). Beyond the five named in §2 (`agreste`, `cesam`, `chain`, `fawley`, `rocket`), the detector also reports **`ps2_f_s`, `ps2_s`, `ps3_s_gic`**. Their goldens changed in `ac391bb6` — Sprint 36 Day 10's own robustlp NA-guard landing — so S36 closed reporting the *pre-landing* count. All three still `model_optimal_presolve` + match (no bucket harm), but the re-baseline must re-check all **8**; the three additions are exactly the 2-D cohort members.
5. **Apply the decision rule** below; either commit the re-pinned DB or restore the snapshot.

### Classifying a "regression" (the rule)

The re-pin decision needs three categories, not two — §1 shows why:

| class | definition | effect on the decision |
|---|---|---|
| **Regression** | a **bucket downgrade** attributable to v54 — e.g. `model_optimal → model_infeasible`, or a `match → mismatch` | **blocks** the re-pin |
| **Neutral churn** | objective jitter within tolerance, or a lateral move that is not a downgrade | does **not** block; record in the diff |
| **Stale-entry correction** | the v53 row predates a landed fix, so the change reflects *our* code, not v54 — **turkey is exactly this** (`path_syntax_error → path_solve_license`) | does **not** block; must be **called out separately** so it is not miscounted as a v54 effect |

**Rule: re-pin the DB to v54 only if the diff contains zero Regressions.** Neutral churn and stale-entry corrections are recorded and explained, not treated as blockers.

### A gap worth fixing while re-baselining

The DB records **`"solver_version": null` for all 219 models** — there is no per-row provenance for which GAMS version produced a result. That is why the v53/v54 question can only be answered by re-running rather than by querying. **Recommendation:** have the re-baseline populate `solver_version` (GAMS 54.2.1) so future version transitions are a DB query, not a 30-minute re-solve.

## 4. Residual multi-root cohort

`turkpow` / `clearlak` / `dinam` / `indus` — all still `path_syntax_error`, unchanged. The P2 general `$149` `_diff_prod` fix (Task 5, verified working) removes their `$149` blocker, but each carries other roots (turkpow ragged `Table mdatat`; clearlak dynamic/computed sets; dinam & indus `$140`+`$149`), so `$149` removal is **necessary-not-sufficient**. No bounded per-model tail effort is identified for this sprint. **Cross-reference:** Task 6 measured `dinam` as one of the models the fawley predicate leaks onto — so dinam is touched by two open tracks and should not be worked in isolation.

## 5. P6 go / no-go

| item | verdict |
|---|---|
| **turkey +1** | **NO-GO — license-gated.** The fix works and the compile is clean; only a licensed >1000-row environment is missing, and none is procurable from the repo. |
| **v54 re-baseline** | **GO — cheap and low-risk.** ~30 min; the named risk set shows zero change. |
| **re-pin to v54** | **Decide from the diff** (§3). The evidence so far points to zero regressions, but the full 142-model diff is the gate. |
| **residual cohort** | **No in-sprint effort.** `$149` is necessary-not-sufficient; dinam overlaps the open fawley track. |

---

## 6. Known-Unknown dispositions

| Unknown | Verdict | Basis |
|---|---|---|
| **6.1** a licensed >1000-row GAMS-54 testbed is procurable | ❌ **WRONG (refuted)** — no such environment exists or is procurable | §1 — all three local installs are `GAMS_Demo`; CI holds only `PYPI_API_TOKEN` and installs the public demo. turkey measured at **3,866 single equations** with the exact demo refusal, and its compile is otherwise **clean (0 `$NNN`)** ⇒ the +1 is real but purely license-blocked. **Bonus:** turkey's DB row is stale (2026-06-20, pre-dating the 2026-08-03 `$161` fix) because `--resolve-changed` never persists; a persisting re-solve moves `path_syntax_error` 7 → 6 with no Solve/Match change. |
| **6.2** the full v54 demo re-baseline shows zero bucket regressions | 🔶 **DESIGN-VERIFIED** — procedure + decision rule specified; the full 142-model diff is the gate | §3 — procedure defined (snapshot → re-solve → diff → decide), with a **three-way** classification (Regression / neutral churn / **stale-entry correction**) because turkey's stale row would otherwise be miscounted as a v54 effect. Cost measured at **~12 s/model ⇒ ~30 min** for 142. Not upgraded to VERIFIED: only 5 of 142 models were actually re-solved here. |
| **6.3** which of the 5 OBJ-GAP models shift buckets under v54 | ✅ **VERIFIED — none** | §2 — all five re-solved under GAMS 54.2.1: identical buckets, and chain's objectives **byte-identical** (5.0723 / 5.1199). DB snapshotted and restored byte-identical (md5 unchanged). Residual cohort re-confirmed unchanged; `$149` necessary-not-sufficient. |

---

**Document Status:** ✅ Complete — Sprint 37 Prep Task 8 (v54 re-baseline plan + turkey testbed verdict).
**Last Updated:** 2026-08-10 · **Owner:** Sprint 37 execution team
