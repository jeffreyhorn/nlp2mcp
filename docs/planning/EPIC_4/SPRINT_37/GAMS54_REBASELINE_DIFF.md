# GAMS 54.2.1 Corpus Re-Baseline — Diff & Version Decision (Sprint 37 Day 9, P6)

**Date:** 2026-08-12 · **Branch:** `planning/sprint37-day9-p7-infra` · **Solver:** GAMS **54.2.1** (`d9889eb3`, DEX-DEG x86 64bit/macOS, demo) · **Scope:** the 142 convex candidates, `--only-solve`, **persisting**.

**DB snapshot before the run:** md5 `e997e4ead5b6c524aac732b919045a53` (`/tmp/db_before_v54.json`) — fully revertible.

**Verdict: ✅ RE-PIN TO v54. Zero Regressions.** Three models moved and **none is a bucket downgrade**. The headline is narrower than it first looks: `Match 93 → 94` is real, but **the genuine floor stays 76** — the model that appeared to add to it had already been counted since Sprint 30.

---

## 1. Result

| KPI | before | after | Δ |
|---|---|---|---|
| Solve | 108 | **108** | — |
| **Match** | 93 | **94** | **+1** |
|   cold-optimal match | 64 | 65 | +1 |
|   presolve match | 29 | 29 | — |
| **genuine floor** | 76 | **76** | **— (see §3)** |
| model_infeasible | 7 | 7 | — |
| `path_syntax_error` | 7 | **6** | −1 |
| `path_solve_license` | 9 | **10** | +1 |
| all-219 Match | 96 | **97** | +1 |

Run: 142/142 processed, 7 skipped, 371.6 s total (~2.6 s/model). Presolve retry recovered 43/47 from STATUS 5.

## 2. The three movers — classified, not lumped

Task 8 §3 requires a **three-way** classification, because a stale DB row and a v54 behaviour change look identical in a bucket diff. Each was traced to its cause:

| model | change | classification | evidence |
|---|---|---|---|
| **turkey** | `path_syntax_error` → `path_solve_license` | **stale-entry correction** | the `$161` compile-recovery landed **2026-08-03**; the row was solved **2026-06-20**. Predicted by Task 8 §1. Not a v54 effect, not a recovery. |
| **robert** | `model_optimal_presolve`+match → `model_optimal`+match | **stale-entry correction** | its cold emit changed in **Sprint 30** (`87f4bd3d`, "robert objective-gradient fix"), *after* the 2026-06-20 row, which was never re-solved. |
| **hhfair** | `model_optimal`+**mismatch** → `model_optimal_presolve`+**match** | **v54 effect** | emit **byte-identical** since 2026-06-20 (`git log` on both goldens is empty), so the solver is the only variable. |

**No Regression** under the rule's definition (a v54-attributable bucket downgrade — `model_optimal → model_infeasible`, or `match → mismatch`). hhfair's move is `mismatch → match`, an improvement.

## 3. Why the floor does **not** move to 77

The naive reading — cold-optimal match rose 64 → 65, so the floor rises 76 → 77 — is **wrong**, and worth recording because it is the reading a future automation would produce.

`SPRINT_32/BASELINE_METRICS.md` §3 gives the operational definition, and it has **three** conditions, not one:

> the **methodology** set = `outcome_category = model_optimal_presolve` **AND** `comparison_status = match` **whose cold MCP failed/mismatched** (the warm-start was *required*), **with the cold emit byte-identical to its pre-fix state**.
>
> The **genuine floor** = every other match: a cold match, **OR a match whose cold emit a real fix *changed*** (a genuine cross-term contribution, even if PATH still needs the presolve warm-start).

### robert was already genuine

The same document's floor provenance names it outright:

> Genuine, stable (floor) | **74** | … **+1** S29 (maxmin `-1` + catmix) **+1 S30 (robert cold obj-grad)** **+4** S31 …

So robert has counted toward the floor **since Sprint 30**, under the second limb — its cold emit was *changed by a real fix* — even though its DB row still read `model_optimal_presolve`. Today's re-solve makes the **DB agree with the hand-partition for the first time in five sprints**; it does not add a model. Counting it again would double-count.

The stale row had been *understating* robert's recorded status all along, which is exactly why the correction reads like a gain.

### hhfair is methodology, not genuine

Checked against all three conditions: `presolve` + `match` ✓, warm-start required (its cold MCP now mismatches) ✓, cold emit byte-identical with no fix having changed it ✓. That is the methodology set precisely. **+1 Match, +0 floor.**

### A caveat for anyone automating this

A mechanical count of `all-219 Match − (presolve ∧ match)` yields **64 → 65**, nowhere near the recorded 76. It drops the *"cold emit byte-identical to pre-fix"* qualifier, so it misclassifies every presolve match that a real fix earned as methodology. **The genuine floor cannot be derived from the DB alone** — it is a hand-partition with per-model provenance. Any future "floor tracking" automation must carry that provenance or it will silently emit 65 and look authoritative.

## 4. Version decision

**RE-PIN the corpus baseline to GAMS 54.2.1.** The rule is *"re-pin only if the diff contains zero Regressions"*, and it does:

- 1 v54 effect, and it is an **improvement** (hhfair `mismatch → match`).
- 2 stale-entry corrections, both **predicted or explicable** and neither attributable to v54.
- No model lost a bucket, no match became a mismatch.

Task 8 §2's risk set (`agreste`, `cesam`, `chain`, `fawley`, `rocket`) is unchanged, as it forecast. The set was **corrected to 8 on Day 5** (adding `ps2_f_s`, `ps2_s`, `ps3_s_gic`); all eight are unchanged here.

## 5. An unmet requirement — `solver_version` is still null

Day 9's prompt required: *"While re-baselining, populate `solver_version` (currently `null` for all 219 rows)."*

**It is still `null` for all 219 rows.** `run_full_test.py` does not record it, so populating it needs a runner change, not a re-baseline flag. This is the second sprint to identify the gap (Task 8 §3) and the second to leave it open.

The consequence is unchanged and now demonstrated: **this whole document existed only because the question "did v54 change anything?" could not be answered by querying the DB.** It took a 372-second re-solve plus per-model `git log` archaeology to classify three rows. With `solver_version` recorded, turkey and robert would have been identifiable as pre-v54 rows immediately, and the two stale-entry corrections would not have needed tracing.

**Recommendation:** make it a P7 follow-up with a concrete surface — `run_full_test.py`'s solve-result writer — rather than a re-baseline instruction, since the re-baseline is not where the field gets set.

## 6. A process failure this run exposed

**`git add -A` after a GAMS run in the repo root committed 20 runtime artifacts** — `MINOS.SPC`, `MODEL.{COR,ERR,FLN,INP,MAP,OBJ,SCR,SO2,SOG,SOL,SPA,STG,STO,TIM}`, `decis.lic`, `decism.opt`, `listA1.csv`, `repdat.put`, `solution_lic.csv`. Two are materially bad: **`decis.lic` is license material**, and `MODEL.SOL` carries a third-party copyright header (*"D E C I S Copyright (c) 1989–2007 by Dr. Gerd Infanger"*). PR review caught 4 of the 20.

**It also swept in 36 unintended presolve goldens** (17 → 53), written by the presolve retry. That is not a cosmetic problem: it would have expanded the golden corpus 170 → 206 and **changed what `check-goldens` sweeps**, using references generated in this very run rather than reviewed ones — a self-certifying reference set.

All 56 removed from the PR; the 20 artifacts are now in `.gitignore` so a solve run from the project directory cannot repeat it.

**Two process notes worth carrying:**

1. **The re-baseline must be run from a scratch directory**, or `git add -A` must never follow it. GAMS writes solver scratch files to `cwd`, and `cwd` here is the repo root.
2. **The 36 presolve goldens are arguably the *fix* for the Day-4 coverage asymmetry** (153 cold vs 17 presolve). But adopting them must be a deliberate, reviewed change — generating references and committing them in the same unreviewed step is how a gate stops being a gate.

## 7. Reproduction

```bash
cp data/gamslib/gamslib_status.json /tmp/db_before_v54.json   # md5 e997e4ea…
PATH=/Library/Frameworks/GAMS.framework/Versions/54/Resources:$PATH \
  .venv/bin/python scripts/gamslib/run_full_test.py --only-solve --quiet
```

Per-model diff: compare `outcome_category` and `comparison_status` across the snapshot and the live DB; classify each mover by (a) its prior `solve_date` against the landing dates of any emit fix, and (b) `git log --since=<solve_date>` on its goldens.

---

**Document Status:** ✅ Complete — Sprint 37 Day 9 P6 (re-baseline diff; **RE-PIN to v54**, zero Regressions, floor unchanged at 76).
**Last Updated:** 2026-08-12 · **Owner:** Sprint 37 execution team
