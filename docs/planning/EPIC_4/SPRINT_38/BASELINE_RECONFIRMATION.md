# Sprint 38 Prep Task 2 — Baseline Re-Derivation & Carryforward Fingerprints

**Date:** 2026-08-17 · **Branch:** `planning/sprint38-task2` · **Measured at:** `84fbe43c` (main, Sprint-38 prep merge) · **Solver:** GAMS **54.2.1** · **Scope:** measurement only — `src/` untouched, DB restored byte-identical.

**Verdict: 🔶 PROCEED WITH TWO CORRECTIONS.** The KPI block re-derives **exactly** on every line, and the sarf and inventory fingerprints hold. Two things do **not** hold as banked, and both change what a later task must do:

1. **The ganges `$141` count does not reproduce** — banked 78, measured **15** (cold) / **49** (presolve). `$145`×3 and `$149`×9 reproduce *exactly* in both variants.
2. **The genuine floor's provenance chain credits three models that are outside the corpus the floor is reported over** — `ps2_f_s`, `ps2_s`, `ps3_s_gic` are `non_convex`, and were already so at the S32 anchor immediately after the S31 sprint that credited them.

Every figure below carries the SHA it was measured at, per the retrospective's banked-staleness remedy.

---

## 1. KPI block — re-derived, not re-read (`84fbe43c`)

Recomputed directly from `data/gamslib/gamslib_status.json` using `model_id` as the key (**not** `model_name`, which holds the description) and `mcp_solve.outcome_category` + `solution_comparison.comparison_status` as the fields.

| quantity | recorded | derived | |
|---|---|---|---|
| convex candidates | 142 | **142** | ✅ |
| Parse | 142 | **142** | ✅ |
| Translate | 135 | **135** | ✅ |
| Solve | 108 | **108** | ✅ |
| Match | 94 | **94** | ✅ |
|   cold-optimal | 65 | **65** | ✅ |
|   presolve | 29 | **29** | ✅ |
| model_infeasible | 7 | **7** | ✅ |
| path_syntax_error | 6 | **6** | ✅ |
| all-219 Match | 97 | **97** | ✅ |

**Every line reproduces.** Translate is derived from `nlp2mcp_translate.status == 'success'` over the 142 candidates (135 success / 7 failure).

## 2. The genuine floor — and a provenance defect

**Mechanical count: 65. Recorded floor: 76. Gap: 11.** The mechanical count is **confirmed** at `84fbe43c`. The 76 is **re-observed from the hand-partition, not validated** — §2.1 shows its provenance credits three out-of-corpus models, so the correct target may be 73. Both figures behave as expected in one respect: the floor is not DB-derivable.

The documented provenance chain (`SPRINT_32/BASELINE_METRICS.md` §3, extended):

```
S28 genuine 68  (otpop/chakra/chenery/kand/srkandw + the 6 non-methodology presolve matches)
  +1 S29  (maxmin -1 + catmix)
  +1 S30  (robert cold obj-grad)
  +4 S31  (polygon methodology→genuine + ps2_f_s/ps2_s/ps3_s_gic mismatch→genuine)
  = 74 at S32
  +1 S33  (P6 sample pruned-var .l-init)     = 75
  +1 S37  (P1 markov σ=sp)                   = 76
```

### 2.1 The defect: three credited models are outside the corpus

| model | convexity | in the 142? | credited |
|---|---|---|---|
| `ps2_f_s` | **non_convex** | ❌ **no** | S31, +1 |
| `ps2_s` | **non_convex** | ❌ **no** | S31, +1 |
| `ps3_s_gic` | **non_convex** | ❌ **no** | S31, +1 |

The genuine floor is a headline KPI reported **over the 142 convex candidates** (`reference_match_kpi_corpus_scope`). These three are `non_convex` and therefore outside it.

**They were not reclassified after the fact.** Checked at four anchors:

| anchor | date | `ps2_f_s` / `ps2_s` / `ps3_s_gic` |
|---|---|---|
| `4cbf8bff` (S32) | 2026-07-13 | non_convex ×3 |
| `750803b2` (S33 close) | 2026-07-17 | non_convex ×3 |
| `78ceaead` (S34 close) | 2026-07-22 | non_convex ×3 |
| `84fbe43c` (now) | 2026-08-17 | non_convex ×3 |

S31 closed 2026-07-13 — the same day as the S32 anchor. So they were **already `non_convex` when credited**.

### 2.2 What this means, stated without guessing

Two readings, and this task cannot choose between them:

- **(a) The floor is in-corpus only** ⇒ it has been **overstated by 3 since Sprint 31**, and the true in-corpus floor is **73**, not 76.
- **(b) The floor's scope legitimately differs from Solve/Match's scope** ⇒ the figure is right, but that scope difference **has never been written down anywhere**.

The arithmetic is consistent with either. Reading (a) needs 8 in-corpus presolve-genuine models (65 + 8 = 73); reading (b) needs 11 (65 + 11 = 76, of which 3 are out-of-corpus, leaving 8 in-corpus — the *same* 8). **The two readings differ only in whether the 3 out-of-corpus models are counted**, which is a definitional question, not a measurement one.

**This is Unknown 6.2's whole premise, arriving earlier than expected.** Task 3 must resolve it *before* designing the provenance file, because a tracker that reproduces "76" and a tracker that reproduces "73" are different artifacts, and the wrong one silently entrenches the error.

### 2.3 Per-model provenance draft (input to Task 3)

Attributable from the documented chain, all verified present in the DB at `84fbe43c`:

| model | limb | provenance | in 142? |
|---|---|---|---|
| otpop, chakra, chenery, kand, srkandw | cold | S28 named genuine | ✅ |
| maxmin, catmix | presolve-genuine | S29 (+1) | ✅ |
| robert | cold *(was presolve-genuine until S37 Day 9)* | S30 cold obj-grad | ✅ |
| polygon | presolve-genuine | S31 methodology→genuine | ✅ |
| ps2_f_s, ps2_s, ps3_s_gic | presolve-genuine | S31 mismatch→genuine | ❌ **out of corpus** |
| sample | cold | S33 P6 pruned-var `.l`-init | ✅ |
| markov | cold | S37 P1 `σ=sp` | ✅ |

**14 of the 76 are attributable by name.** The remaining ~62 come from the unnamed "S28 genuine 68" block and have **no per-model record anywhere** — which is precisely why the floor cannot be audited today. Task 3 must either reconstruct them or accept the block as an opaque baseline and say so.

## 3. ganges cascade fingerprint — ❌ the banked baseline does not reproduce (the `rc=0` claim is untested)

**`src/` is byte-identical to the S37 close (`8cffec29`)** — `git diff 8cffec29..HEAD -- src/` is empty, so the cascade is **not** on `main`, as expected.

`prolog` — the model the `$149` rebind drifts — is **`model_optimal` + match**, confirmed. It is the leak target Task 4 must keep byte-identical.

### 3.1 Measured error signatures (occurrence counts, both models)

| run | `$141` | `$145` | `$149` | rc |
|---|---|---|---|---|
| **banked** (S37 Day 4, presolve) | **78** | 3 | 9 | 2 |
| cold compile, ganges | **15** | **3** ✅ | **9** ✅ | 2 ✅ |
| cold compile, gangesx | **15** | **3** ✅ | **9** ✅ | 2 ✅ |
| presolve emit, ganges | **49** | **3** ✅ | **9** ✅ | 2 ✅ |

`$145`×3 and `$149`×9 reproduce **exactly, in both variants, on both models**. `$141` reproduces in **neither** variant.

The presolve run also shows `$140`×63, `$318`×47, `$300`, `$282`, `$257`, `$184` — error classes the banked figure does not mention at all.

### 3.2 Two measurement notes worth carrying

- **The banked figure came from the presolve run, not a cold compile.** `DAY4_GANGES_CONTROL.md` §1 states it explicitly: *"The first presolve run failed with the cascade's first root."* **The Task-2 prompt asked for a cold compile** — that instruction was wrong, and it is mine. Both variants were measured here so the comparison is complete either way.
- **`grep -c` counts lines, not occurrences.** The first pass reported `$145=1` because three occurrences share one line. All counts above use `grep -o … | wc -l`. A line count would have understated two of the three classes.

### 3.3 A plausible cause, not a confirmed one

`stationarity.py` gained **+53 lines between the Day-4 measurement (`7789d9cf`) and now** — the Day-6 fawley landing, which touches the same emit surface and landed *after* the ganges figure was banked. That is a plausible cause for a changed `$141` count and it is **not established**. Determining it is Task 4's job, not this one's.

### 3.4 What was NOT tested

**The cascade was not re-applied.** Unknown 1.1's core question — do the four fixes still take both models to `rc=0`? — is **untested here**; re-applying the banked patch is a scratch-branch exercise that Task 4 owns. What this task establishes is the *baseline that patch starts from*, and that baseline has drifted in one of three counts.

**Unknown 1.1 is therefore recorded 🔍 INCOMPLETE, not ❌ WRONG.** Marking it WRONG would assert that the cascade *fails* to reach `rc=0` — a claim no measurement here supports. The refuted item is the banked fingerprint, not the cascade's behaviour. (This distinction was caught in PR review; the original status overstated the evidence, which is the same verify-a-component / assert-a-property error the sprint keeps surfacing.)

## 4. sarf sites — ✅ intact

| site | location | verified |
|---|---|---|
| **S1** | `constraint_jacobian.py:78` | ✅ `enumerate_variable_instances(var_def, model_ir)` |
| **S2** | `index_mapping.py:634` | ✅ `enumerate_variable_instances(var_def, model_ir)` |
| **S3** | `stationarity.py` | ✅ present (file is +311 since the S34 anchor) |

**Six corpus-safety call sites, all located:**

`index_mapping.py:634` · `constraint_jacobian.py:78` · `gradient.py:287` · `gradient.py:453` · `complementarity.py:367` · `complementarity.py:512`

**Drift since the S34 anchor `78ceaead`:** `index_mapping.py`, `constraint_jacobian.py`, `gradient.py`, `complementarity.py` are all **byte-unchanged**. Only `stationarity.py` moved (+311: markov +259, fawley +54, less deletions) — and its site survived, exactly as Sprint 37 recorded.

**Blow-up confirmed non-terminating:** sarf emit was still running at a **100 s cap** and was killed. Not profiled — Task 5 owns that.

**Gate peculiarity confirmed:** no `data/gamslib/mcp/sarf_mcp.gms` exists, so `make leak-check MODEL=sarf` reports `NO-OP` and fails for a non-correctness reason, as the design records.

## 5. Golden / gate inventory — ✅ all confirmed

| quantity | expected | measured |
|---|---|---|
| discovered goldens | 170 | **170** ✅ |
| allowlisted | 7 | **7** ✅ |
| in-scope | 163 | **163** ✅ |
| presolve goldens | 17 | **17** ✅ |
| `--min-scope` | 170 | **170** ✅ |
| `MAX_WORKERS` | 3 | **3** ✅ |

## 6. The 36 presolve goldens — ✅ fully reproducible

A clean `--only-solve` run **from `/tmp/task2_scratch`** regenerated exactly **36** presolve goldens (17 → **53**; discovered 170 → **206**), matching the Sprint-37 Day-9 figures precisely. Run time 607.8 s (inflated by concurrent ganges compiles; S37 measured 445 s unloaded).

**The 36 models:**

```
aircraft  apl1p     apl1pca   catmix    china     circle
cpack     etamac    harker    hhfair    himmel16  imsl
irscge    like      lmp2      lrgcge    marco     mathopt1
mathopt4  maxmin    mine      mingamma  moncge    paperco
prodsp2   ps10_s_mn ps5_s_mn  qsambal   sambal    senstran
spatequ   stdcge    tforss    trig      weapons   worst
```

**Zero bucket moves** — the re-solve changed no `outcome_category` and no `comparison_status` for any of the 219 models. The DB delta was metadata only.

**The scratch-directory mitigation works.** Sprint 37 Day 9's `git add -A` after an in-repo re-solve swept 20 runtime artifacts including `decis.lic`. Running from `/tmp/task2_scratch` produced **zero** repo-root artifacts, verified by `git status` before restoring.

**Tree restored to pristine:** DB `git checkout`'d back to md5 `2ed0a42ba6861fd5837399ae88646d76`, the 36 untracked goldens `git clean`'d, scratch directory removed. Working tree: 0 uncommitted.

## 7. Reproduction

```bash
# KPI block
.venv/bin/python -c "import json; d=json.load(open('data/gamslib/gamslib_status.json')); ..."   # §1

# ganges/gangesx cold + presolve (SLOW: 325s / 243s emit)
# NOTE: the CLI writes directly to the output path and does NOT create parent
# directories — create them first or the command fails on a clean machine.
mkdir -p /tmp/w /tmp/w2
.venv/bin/python -m src.cli data/gamslib/raw/ganges.gms -o /tmp/w/ganges_mcp.gms
.venv/bin/python -m src.cli data/gamslib/raw/ganges.gms --nlp-presolve -o /tmp/w2/ganges_mcp.gms
( cd /tmp/w && gams ganges_mcp.gms lo=0 o=ganges.lst )
grep -o '\$[0-9]\{3\}' /tmp/w/ganges.lst | sort | uniq -c | sort -rn   # occurrences, NOT grep -c

# the 36 presolve goldens — ALWAYS from a scratch directory, NEVER git add -A after
mkdir -p /tmp/task2_scratch && cd /tmp/task2_scratch
PATH=/Library/Frameworks/GAMS.framework/Versions/54/Resources:$PATH \
  <repo>/.venv/bin/python <repo>/scripts/gamslib/run_full_test.py --only-solve --quiet
cd <repo> && git checkout -- data/gamslib/gamslib_status.json && git clean -fq data/gamslib/mcp/
```

---

**Document Status:** ✅ Complete — Sprint 38 Prep Task 2. KPI block and sarf/inventory fingerprints verified; **two corrections raised** (the ganges `$141` count; the floor's out-of-corpus provenance).
**Last Updated:** 2026-08-17 · **Owner:** Sprint 38 execution team
