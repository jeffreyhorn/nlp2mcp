# Sprint 38 Day 10 — Checkpoint 2 + P5 + P8: the spurious-match investigation

**Date:** 2026-08-22 · **Branch:** `planning/sprint38-day10-checkpoint2-p5` · **Measured at:** `643a2dab` · **Toolchain:** GAMS **54.2.1** / PATH **5.2.01** · **Scope:** one new script + its tests + docs. **No `src/` change. No DB change.**

**Verdict: ✅ Checkpoint 2 GO (22/22) · P8 finding — EXACTLY ONE spurious match (`weapons`), of 33 checked · P5 — #1330 re-confirmed Epic-5, and the cohort survey re-triaged with one issue found still LIVE.**

**The blast radius, stated plainly because it will be misread otherwise:** up to **30** presolve matches were in question (Match 95 = 65 cold + 30 presolve). **Exactly 1 is spurious.** **Cold matches are unaffected** — there is no warm start to read back — so **the genuine floor of 73 is not at risk either way.**

---

## 1. Checkpoint 2 — GO, and this time the selection was not empty

Run through the **re-anchored** checkpoint (`--since-commit 8cffec29`, P6d), which selects the 22 goldens adopted on Day 8.

```
[resolve-changed] re-solving 22 changed-golden model(s) since 8cffec29:
  catmix, cpack, etamac, harker, hhfair, himmel16, irscge, like, lrgcge, marco,
  mathopt1, mathopt4, maxmin, mingamma, moncge, paperco, qsambal, sambal,
  stdcge, tforss, twocge, worst
...
GO: all 22 changed-golden model(s) held their bucket
```

All 22 read `model_optimal_presolve` + `match` → `model_optimal_presolve` + `match` = **same**. Exit 0.

**Contrast with Checkpoint 1** (Day 5), which had to be run with `--allow-empty` because the re-anchor had not yet happened and the selection was empty. P6d's re-anchor is what makes this checkpoint assert anything at all: against the stale anchor the diff would again have been empty, and Day 4's P6b assertion would have refused the run.

**Figures derived, not quoted** (`scripts/sprint_audit/kpi_block.py`, at `643a2dab`):

| quantity | value |
|---|---|
| convex candidates | 142 · Parse 142 · Translate **135** |
| Solve | **109** |
| Match | **95** (cold-optimal **65** + presolve **30**) |
| model_infeasible 7 · path_syntax_error 6 · path_solve_terminated 3 · license-gated 10 | |
| all-219 Match | **98** |

Genuine floor **73**, from `floor_tracker.py` (baseline 73 + 0 recorded movements) — *not* the DB's mechanical 65.

---

## 2. P8 — the discriminator, and why it is not a grep

### 2.1 The hypothesis

A `--nlp-presolve` emit warm-starts by running the original model inside the generated file, then reads the objective back **after** the MCP solve:

```gams
$include "data/gamslib/raw/<model>.gms"   * solves the NLP, sets <objvar>.l
Solve mcp_model using MCP;                 * if this ABORTS, .l is untouched
nlp2mcp_obj_val = <objvar>.l;              * still the NLP's own answer
```

If the MCP aborts, **both sides of the comparison come from the NLP** and it matches itself.

The recorded *status* is wrong the same way, and for a reason worth naming: `parse_gams_listing` (`scripts/gamslib/test_solve.py`) deliberately takes the **last** `MODEL STATUS` in the file "to handle multiple solves". On a presolve listing whose MCP aborted, the last one is the embedded NLP's.

### 2.2 The discriminator — positional attribution

**Every status line in a GAMS listing belongs to the solve summary above it.** So the question is not *"does the listing contain a MODEL STATUS"* but *"is there a summary whose `TYPE` is `MCP`, and did it report one"*:

```
               S O L V E      S U M M A R Y

     MODEL   mcp_model
     TYPE    MCP
     SOLVER  PATH                FROM LINE  1124

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal
```

**⚠ `TYPE MCP` alone is NOT sufficient, and writing the reproduction command is what exposed it.** Two raw corpus sources — **`cesam.gms` and `spatequ.gms`** — solve an MCP of their own, and a presolve emit `$include`s the raw source, so their listings carry a `TYPE MCP` summary that is **not ours**. Reading it as ours would reinstate this very bug one level up.

Neither is in today's 33 (`spatequ` is a presolve row but `mismatch`; `cesam` is not a presolve row at all), so **the measured result is unaffected** — but the check keys on the **model name** as well:

- **All 39 committed presolve goldens name the model `mcp_model`** — `grep -o "^Model [A-Za-z_0-9]*" | sort | uniq -c` → `39 Model mcp_model`.
- A `TYPE MCP` summary under any *other* model name is counted as **foreign** and surfaced, never as evidence our MCP ran.

Re-running the 33 retained listings under the tightened rule reproduces **32 / 1 exactly**, with **zero** foreign summaries encountered.

**Deliberately NOT keyed on `EXECERROR`,** per the Day-9 instruction. `check_presolve_divergence.py`'s first branch treats *any* execution error as an **embedded-NLP** divergence — which is exactly how weapons, whose embedded NLP solved perfectly, got reported against the wrong side. An abort tells you *something* failed, not *which model*.

Shipped as `scripts/sprint_audit/check_mcp_solve_attribution.py`.

### 2.3 The result — 1 of 33

Every model recorded `model_optimal_presolve` **+ match** was re-emitted and re-run (33 rows; the KPI's 30 plus the 3 `non_convex` ones outside the 142 candidates).

```
Checked 33 model(s) recorded model_optimal_presolve + match.
  our MCP solved (MS-1/MS-2)          : 32
  our MCP ran but FAILED              : 0
  ONLY an embedded solve reported     : 1
  could not be determined             : 0

SPURIOUS MATCHES — the recorded objective is the embedded solve's own value:
  weapons
```

**Attribution is kept separate from success, and the label does not assert a solve kind.** A `MODEL STATUS` proves the status is *ours*, not that the solve worked — an MCP returning MS-4 leaves the warm-started `.l` values in place exactly as an abort does, so it is reported as **`MCP-FAILED`**, never as solved. And the spurious verdict is **`EMBEDDED-ONLY`** rather than "NLP-only" because the population is not all NLP: `marco`/`paperco`/`tforss` are **LP**, `cpack`/`qsambal` **QCP**, `maxmin` **DNLP**, `robustlp` mixed. The solve *kind* is carried on the summary; the verdict names only provenance.

**Three indeterminate verdicts are kept distinct from the spurious one** — `MCP-NO-STATUS` (our block exists but reported nothing), `NO-SOLVE` (no recognised solve at all) and `ERROR`. Folding them into "spurious" would report *"the embedded model solved and ours did not"* when **nothing** solved — a fabricated finding of exactly the kind this script exists to catch. They exit **1**; a spurious match exits **0**, because it is a finding, not a failure of the check.

**weapons** — one summary in the whole listing (`war` / NLP / CONOPT, MS-2 @ 1735.5696); the MCP aborted:

```
**** MCP pair comp_minw.lam_minw has unmatched equation
**** SOLVE from line 238 ABORTED, EXECERROR = 1
```

The DB records `model_optimal_presolve`, MS-**2** "Locally Optimal", objective 1735.5696, `iterations: 11` — **every one of those is the NLP's**, including the iteration count, read off `ITERATION COUNT, LIMIT 11` in the NLP's own summary.

**32 of 33 genuinely solved.** The parser handled the awkward cases without special-casing: `harker` has 4 NLP solves before its MCP, `mathopt4` has 4, `robustlp` mixes LP/LP/QCP, `marco`/`paperco`/`tforss` are LPs reporting MS-1.

### 2.4 Two independent DB-side corroborations

Neither was used as the discriminator — both were derived afterwards and agree with it.

| signal | weapons | the other 32 |
|---|---|---|
| `mcp_model_status` | **2** ("Locally Optimal") | **1** ("Optimal") on all 32 |
| `solver_version` | **null** — PATH never ran, so no version to extract | `5.2.01` on 30 of 32 |

**The `solver_version` signal alone would have been wrong**, which is why it is a corroboration and not the test: `ps2_f_s`, `ps2_s`, `ps3_s_gic` also carry `null` (older solves, predating version extraction) yet all three genuinely solved with MS-1. **MS-2 on an MCP is the sharper tell** — PATH reports MS-1 for a solved complementarity problem; MS-2 is a CONOPT status — and it picks out weapons uniquely across all 33.

### 2.5 What this means for the KPI — reported, not corrected

**Per the Day-10 instruction, nothing was changed: no DB edit, no re-classification.**

| | recorded | if weapons is reclassified |
|---|---|---|
| Match (142 candidates) | **95** | 94 |
| &nbsp;&nbsp;cold-optimal | 65 | **65 — unchanged** |
| &nbsp;&nbsp;presolve | 30 | 29 |
| **genuine floor** | **73** | **73 — unchanged** |

**The Match KPI is overstated by exactly 1.** The floor is untouched: weapons was never a floor entry, and `floor_provenance.json` carries zero entries, so `floor_tracker.py` reports 73 either way. This is the second time in two days that P6c's separation of the floor from the DB has kept a defect out of the headline number.

**The remedy is systemic, not per-model.** The pipeline should refuse to record an MCP outcome it cannot attribute to an MCP solve — the check now exists as a function (`mcp_produced_status`) and can be wired into `run_pipeline`. **That is a change to how results are recorded and belongs to the owner, not to Day 10.**

---

## 3. The second measurement — `mcp_file_used` dangles for 14 of 47

Same population, same question: **how much of the presolve record describes artifacts that no longer exist?**

`mcp_file_used` records the presolve artifact the solve *generated* (`run_full_test.py:954`), not a committed golden — so it points at a non-existent path for every model that solved via presolve without an adopted golden.

| `comparison_status` | dangling | what they are |
|---|---|---|
| `mismatch` | **7** | china, circle, imsl, lmp2, prodsp2, spatequ, trig |
| `skipped` | **6** | aircraft, apl1p, apl1pca, ps10_s_mn, ps5_s_mn, senstran |
| `match` | **1** | **weapons** |
| **total** | **14 of 47** | |

**7 + 6 = 13 is exactly Day 8's Tier 2** — the cohort deliberately *not* adopted, because pinning an emit that demonstrably fails to reproduce its NLP solution would make the leak gate certify a wrong answer. Their dangling pointers are the direct consequence of that decision and are **not** a defect to fix model-by-model.

**The 14th is weapons, and the two measurements meet there.** It is the *only* dangling row that is also a `match` — reached independently, from opposite directions: one asks "did the MCP solve?", the other "does the recorded artifact exist?". Both single out the same model.

**Not fixed here, per instruction — a systemic remedy covers all 14 or none.** The two candidate shapes: record `None` when the generated artifact is transient, or adopt Tier 2 (rejected on Day 8, for reasons that still hold).

---

## 4. P5 — #1330 confirmed Epic-5, and the cohort survey re-triaged

> **Doc-name correction:** the Day-10 prompt cites `../CAMCGE_EPIC5_HANDOFF.md`. **No such file exists and none should be written** — prep Task 8 found `EPIC_5/CGE_DEGENERACY_SCOPING.md` already carried every substantive item, and a second document would duplicate ~90 % of it. That is the doc used below.

### 4.1 #1330 — re-confirmed by measurement, not quotation

`B1–B4` were **not** re-run (banned; B1 in particular is *primal-correct* and breaks the MCP dual silently). What was re-measured is the **baseline state**, on the current toolchain:

| | scoping doc (2026-08-18) | **measured today** |
|---|---|---|
| emit | compiles clean | ✅ clean, **0 × `$141`** |
| size | 641 single equations / 641 variables | ✅ **641 / 641** |
| `mcp_model` | MS-4 Infeasible | ✅ **MS-4 Infeasible** (solver status 1) |

**#1330 remains Epic-5-scoped.** The emit is structurally correct and compiles; the MCP is infeasible at iteration 0 against a *correct* NLP optimum. That is the **two-nullspaces** rank-deficiency — a price-scaling ray *and* a row-redundancy nullspace — and closing one without the other leaves the system singular, which is precisely why B2/B3 (numéraire alone, single-dual-pin) both returned MS-4.

### 4.2 Re-triage — the cohort survey's backlog column is stale, but not uniformly

§2 of the scoping doc lists 5 "nlp2mcp backlog" rows. **All 7 cohort issues are still OPEN on GitHub, while 3 of the 4 models now solve and match.** A match is *not* a discharge, so each was re-triaged **against its own fingerprint** rather than inferred from the KPI.

| issue | model | fingerprint checked | verdict |
|---|---|---|---|
| **#1354** camcge `$141` `nu_ieq(i±N)` | camcge | compile + named refs | **DISCHARGED** — compiles clean, `nu_ieq`/`nu_actp` carry **no offsets** |
| **#1355** cesam2 `$141` `nu_COLSUM(i±N)` | cesam2 | compile + named refs | **DISCHARGED** — clean, `nu_COLSUM` no offsets; cesam2 `model_optimal` + match |
| **#1331** twocge empty MCP pair | twocge | EXECERROR=8 / "empty equation" | **DISCHARGED** — fixed Day 9; today's listing: MCP **MS-1**, no pairing error |
| **#1251** twocge empty trade eqs (`r=rr`) | twocge | same fingerprint | **DISCHARGED** — duplicate class of #1331 |
| **#1317** twocge `stat_tz`/`stat_tx` mis-emit | twocge | the emitted rows | ⚠ **STILL LIVE — see 4.3** |
| #1070 prolog CES singular | prolog | DB state | resolved in effect (`model_optimal` + match) |

**Four discharged, one live.** The re-triage narrows the scoping doc's §2 conclusion further: the CGE cohort is now **camcge #1330 (Epic 5) + twocge #1317 (nlp2mcp emit)** — everything else is gone.

### 4.3 ⚠ #1317 is live, and twocge matches anyway

**This is the day's second instance of a green number sitting on top of a real defect.** The reported shape reproduces verbatim in today's emit:

```
stat_tz(j,r).. ... + (((-1) * (pq(j,r)   * mu(j+1,r) / sqr(pq(j,r)  ))) * nu_eqXg(j+1,r))$(...)
stat_tm(i,r).. ... + (((-1) * (pq(i+1,r) * mu(i+1,r) / sqr(pq(i+1,r)))) * nu_eqXg(i+1,r))$(...)
```

`stat_tm` shifts `pq`; **`stat_tz` does not** — two structurally identical equations, emitted differently.

**Hand-derived, and it confirms the report.** `eqXg(i,r).. Xg(i,r) =e= mu(i,r)*(Td(r) + sum(j,Tz(j,r)) + sum(j,Tm(j,r)) - Sg(r))/pq(i,r)` gives `∂/∂Tz(j,r) = -mu(i,r)/pq(i,r)`, so `stat_tz(j,r)` should carry `Σ_i -mu(i,r)/pq(i,r)·nu_eqXg(i,r)`. The emitted off-diagonal term reduces to `-mu(j±1,r)/pq(j,r)` — **the wrong denominator**.

**Why twocge still matches — measured, not assumed.** Set `i` has **2 members** (`BRD`, `MLK`), so the guarded `±1` window (`$(ord(j) <= card(j)-1)`, `$(ord(j) > 1)`) happens to enumerate the *whole* set: the structure is accidentally complete and only the coefficient is wrong. At the MCP solution the two prices are **0.9755 vs 0.9746** (JPN) and **0.9784 vs 0.9782** (USA) — so the bad denominator perturbs that term by **≈ 0.09 %**, against a match tolerance of **0.2 % relative**.

**The defect is masked, not absent, and the margin is thin (0.09 % against 0.2 %).** Two consequences worth stating:

- twocge's Day-9 bucket move rests on an emit with a known-wrong coefficient in `stat_tz`. The Day-9 result stands — the MCP genuinely solved (§2.3 confirms MS-1) and the objective genuinely matched — but the comparison is an **objective** comparison and would not detect a wrong **dual**. Same shape as B1's standing warning.
- The masking is a property of *this model's data* (2 goods, near-equal prices), not of the fix. A wider set or a larger price spread would surface it.

**#1317 has no `docs/issues/` file and no Phase-0 gate** — it is one of the ungated Tier-1 issues P7's Task-10 rule deliberately left unscheduled. **Recommend gating it and scheduling it ahead of the remaining P8 shortlist**: it is the only known-live *numerical* mis-emit on a model already counted in the KPI.

---

## 5. Reproduction

```bash
# §1 — Checkpoint 2, at the re-anchored commit
.venv/bin/python scripts/gamslib/run_full_test.py --resolve-changed --since-commit 8cffec29
.venv/bin/python scripts/sprint_audit/kpi_block.py
.venv/bin/python scripts/sprint_audit/floor_tracker.py

# §2 — the discriminator over every presolve+match row (33)
.venv/bin/python scripts/sprint_audit/check_mcp_solve_attribution.py \
    --workdir /tmp/d10/sweep --json /tmp/d10/attribution.json

# why the check keys on the model NAME, not just TYPE
for f in data/gamslib/mcp/*_mcp_presolve.gms; do grep -o "^Model [A-Za-z_0-9]*" $f; done | sort | uniq -c
grep -Ril 'using[[:space:]]\+mcp' data/gamslib/raw/    # → cesam.gms, spatequ.gms (NOT ours)

# §4 — camcge baseline, WITHOUT re-running any banned variant.
# `src.cli` writes with `Path.write_text` and does NOT create the output parent,
# so the directories must exist first or the emit fails before it starts.
mkdir -p /tmp/d10/emit /tmp/d10/lst
.venv/bin/python -m src.cli data/gamslib/raw/camcge.gms -o /tmp/d10/emit/camcge_mcp.gms
gams /tmp/d10/emit/camcge_mcp.gms o=/tmp/d10/lst/camcge.lst lo=2 ScrDir=$(mktemp -d)
grep -E "SINGLE EQUATIONS|MODEL STATUS" /tmp/d10/lst/camcge.lst

# §4.3 — #1317's fingerprint. The §2 sweep already wrote twocge's presolve emit
# into ITS workdir, so read it from there rather than /tmp/d10/emit (which the
# sweep never populates).
grep -o 'stat_tz(j,r)\.\..*;' /tmp/d10/sweep/twocge_mcp_presolve.gms
```

> **GAMS is run with `cwd` at the repo root** — the emitted `$include "data/gamslib/raw/<id>.gms"` is repo-relative — **but always with `ScrDir` pointing outside the tree**. Sprint 37 Day 9 swept GAMS scratch files into a commit; `ScrDir` is what prevents it. Because the child's `cwd` is the repo root, `--workdir` is **resolved to an absolute path** before use; a relative one would have the child write where the parent never looks.
>
> **A nonzero GAMS exit code is recorded but never acted on.** `weapons` — the entire finding — exits **3** (`USER ERROR(S) ENCOUNTERED`) *because* its MCP aborted. Treating a nonzero rc as an untrustworthy listing would discard the only spurious match in the corpus.

---

## 6. Gate scope — what was run, and what deliberately was not

`*.py` changed ⇒ the full quality gate applies.

| gate | result |
|---|---|
| `make typecheck` | ✅ no issues, 99 source files |
| `make format` / `make lint` | ✅ clean — **plus explicit `black` + `ruff` on the new script**, since the Makefile targets cover only `src/` and `tests/` |
| `make test` | ✅ **5098 passed, 10 skipped** (see below) |
| full-corpus leak gate | **deliberately NOT run** |

**Why no leak gate:** the PR touches no `src/` file and no golden, so the emit cannot have moved and a 185-model sweep would assert nothing about this diff. Stating the reason rather than the omission — a silently skipped gate is the failure mode P6b exists to catch.

> **⚠ The command originally cited here could not have established that claim** (caught at review). `git diff --stat HEAD -- src/ data/` compares the **working tree** against `HEAD`, so it is empty the moment the work is committed — *including* when `HEAD` itself changed those paths. It would have printed the reassuring answer no matter what the PR did. The check has to run against the merge-base:
>
> ```bash
> BASE=$(git merge-base origin/main HEAD)
> git diff --stat "$BASE"..HEAD -- src/ data/   # empty — verified
> git diff --name-only "$BASE"..HEAD            # 5 files: 1 script, 1 test, 3 docs
> ```
>
> Re-checked properly: **the conclusion holds** — the PR's five files are one script, its tests, and three documents. But the evidence for it was worthless, which is the more useful half of the correction.

**One flaky failure, re-run in full rather than in isolation.** The first `make test` reported `1 failed, 5084 passed` — `test_metrics_integration.py::TestMetricsWithSimplificationPipeline::test_performance_overhead_acceptable`. It is a **wall-clock ratio** test (`time.perf_counter()` over 100 pipeline runs) executed under `-n auto`, it touches nothing in this diff, and it is **the same test that flaked on Day 9**. Re-run of the whole suite: **5085 passed**.

**A skip-count discrepancy chased down rather than waved through** (review round). After the review fixes the suite read `5085 passed, 13 skipped` where the previous run read `5085 passed, 10 skipped` — collection had risen by exactly the 3 tests added, so **3 tests that previously passed appeared to have stopped running**. A gate going green while tests quietly stop executing is the same failure mode this PR is about, so it was measured, not assumed:

- `tests/unit` alone → **3725 passed, 0 skipped**: all 9 attribution tests run.
- the parent commit → **5085 passed, 10 skipped** (baseline).
- a clean full run with `-rs` → **5088 passed, 10 skipped** = baseline + the 3 new tests, exactly as expected.

**The 13-skip reading did not reproduce**, and every one of the 10 skips is a pre-existing `pytest.skip` for an unimplemented feature (nested subset indexing, Sprint-10/11 items, a memory-usage test disabled in CI). None is in this diff.

**It recurred once more in review round 2 and again did not survive a re-run** — that round reported `1 failed, 5095 passed, 12 skipped`, the failure being `test_gams_check.py::test_validate_simple_nlp_golden` (**the Day-7 flake**, a GAMS-invoking validation test, distinct from the Day-9 one). Clean re-run: **5098 passed, 10 skipped, exit 0** — exactly 5088 + the 10 tests added in round 2, with the same 10 pre-existing skips enumerated by `-rs`.

**The pattern is worth naming rather than re-diagnosing each time:** this suite has two known wall-clock/subprocess flakes (`test_performance_overhead_acceptable`, `test_validate_simple_nlp_golden`) and its skip count drifts by a few under `-n auto`. **The count is only trustworthy from a run with nothing else competing for the machine**, and the check that settles it is `-rs` — a skip list that names every skip beats any arithmetic on the totals.

> **A process note, since it cost time.** The baseline was first measured with `git stash` running *concurrently* with another full-suite run over the same tree — the two interfere, and the concurrent run's numbers were meaningless. Re-measured serially. **Do not stash the working tree while another job is reading it.**

---

**Document Status:** ✅ Complete — Sprint 38 Day 10. **Checkpoint 2 GO (22/22, non-empty selection).** **P8: exactly 1 spurious match of 33 — `weapons`; Match 95 is overstated by 1; cold matches and the genuine floor of 73 are unaffected. Reported, not corrected.** **`mcp_file_used` dangles for 14 of 47 — 13 are exactly Day 8's Tier 2, the 14th is weapons.** **P5: #1330 re-confirmed Epic-5 (641/641, MS-4, 0 × `$141`); cohort re-triaged — #1354/#1355/#1331/#1251 discharged at their fingerprints, #1070 resolved in effect, and ⚠ #1317 found STILL LIVE with a wrong `pq` denominator in `stat_tz`, masked by a 0.09 % price spread against a 0.2 % tolerance.**
**Last Updated:** 2026-08-22 · **Owner:** Sprint 38 execution team
