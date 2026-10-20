# Sprint 40: Sprint Log

**Weeks 45–46** *(project-relative, not ISO)* · **Days 0–13 = 2026-10-18 … 2026-10-31**
Plan: `PLAN.md` · prompts: `prompts/PLAN_PROMPTS.md`

---

## Day 0 — 2026-10-18 · baseline · 2 h · + P1: schema 3.1.0 and its writers · 8 h

**Branch:** `planning/sprint40-day0-schema` · **Measured at:** `cd5c6b7e` · `scripts/`, `tests/` and `data/` changed, so the quality gate was run (see *Gate*).

### Baseline, re-derived at execution time (close rule C6)

| quantity | value |
|---|---|
| convex candidates | 142 |
| Parse | 142 |
| Translate | **135** |
| Solve | **111** |
| Match | **95** (65 cold + 30 presolve) |
| model_infeasible | 7 |
| path_syntax_error | 6 |
| **`path_solve_terminated`** | **0** |
| path_solve_license | 11 |
| all-219 Match | 98 |
| **genuine floor** | **75** |

Derived by `scripts/sprint_audit/kpi_block.py` and `floor_tracker.py` at `cd5c6b7e`, not recalled. It reproduces the Sprint 39 close exactly.

**`git diff bd2af6e9 HEAD -- src/ data/gamslib/mcp/` is NOT empty, and what moved is named:** one file, `src/validation/gams_check.py`. It is PR #1760, which added `procDirPath=<tempdir>` to the GAMS compile check so a killed run cannot leave GAMS's process directory (and its license copy) in the working tree. It is **emit-neutral**: it changes a command-line argument to a syntax check, and `data/gamslib/mcp/` is unchanged.

**The three owner answers are fixed inputs** (`OWNER_DECISION_BRIEF.md`, committed at `b44344a2`). None was re-opened.

### P1: schema 3.1.0 — `license_edition`

Specification: `SCHEMA_3_1_0_DESIGN.md`.

- **`schema.json`:**
  - `license_edition` (`"licensed"` / `"demo"` / `null`) added to **both** `mcp_solve_result` and `convexity_result`;
  - `gams_version` added to `convexity_result`;
  - the top-level `_migration_summary_v3_1_0` declared;
  - the `description` set to "(v3.1.0)";
  - `additionalProperties: false` unchanged everywhere.
- **One parser:** `extract_license_edition` and `extract_solver_name`, beside `extract_gams_version` in `test_solve.py`, imported by `verify_convexity.py`. Nothing is copied.
  - Measured against real GAMS 54.2.1 listings before landing (synthetic models; only booleans printed, never a `USER:` line):

    | run | demo | licensed | solver |
    |---|---|---|---|
    | effective license, small NLP | — | ✓ | CONOPT |
    | demo license, small NLP (completes) | ✓ | — | CONOPT |
    | demo license, 1,500-row NLP (refused) | ✓ | — | none |

- **Writers.** The design's grep, re-run at HEAD, still closes the list.
  - **W1** `solve_mcp`: the result, plus `None` on the three early returns.
  - **W2** `update_model_solve_result` and **W3** `run_solve_stage`, both fixed-key-list writers, now name the field.
  - **W4** both `mark_cascade_not_tested` constructions write `None`.
  - **W5** the presolve restore: no change. It restores a `.copy()` of the cold record, which a test reproduces.
  - **W7** `migrate_catalog` copies the three flat fields only when present.
  - **W8** `update_catalog_entry` uses present-or-delete.
  - **W9** `verify_model`. It is now a thin wrapper:
    - the run (`_run_verification`) hands out its listing text at the single point it is read, inside the temp dir;
    - the wrapper classifies that text once, and stamps every result with a UTC `verification_date`, the pre-listing returns included;
    - the report envelope's date is UTC too.
  - **W11** `migrate_schema_v3.1.0.py` (below).
  - **W10** (`apply_convexity_results.py` and its corpus hold) is **not** in this PR. ⚠ The Day-0 prompt lists "all 11 writers", but `PLAN.md` schedules W10 as P3 work on Days 2–3, beside the licensed convexity run it applies. It is done there.
- **`db_manager.py`:** `init --empty` stamps **3.1.0**, and the catalog-init chain lists `migrate_schema_v3.1.0.py` after v3.0.0.
- **Migration, applied in this PR:** 3.0.0 → 3.1.0 added `mcp_solve.license_edition` ×150, `convexity.license_edition` ×219 and `convexity.gams_version` ×219, **all `null`**.
  - It validates against the real schema.
  - A second run refuses.
  - With the migration's own keys removed, the migrated DB is **identical** to the 3.0.0 one, with model key order preserved.
  - It was run with `--no-backup`, deliberately. The default backup name, `gamslib_status.json.bak-3.0.0`, is **not** matched by `.gitignore`'s `*.bak`, so it could be committed by accident. Git already holds the 3.0.0 DB.
- **`kpi_block.py` before and after the migration:** every figure is identical. The only difference is `db_dirty: false → true`, because the migrated DB was not yet committed.
- **Knock-on:** the GAMS launch in `verify_convexity` moved from `verify_model` to `_run_verification`. So `test_gams_procdir_invariant.py`'s pinned exemption (cwd = temp dir) moved with it, or the invariant would have reported it as stale.

### Tests

| file | covers |
|---|---|
| `tests/gamslib/test_schema_3_1_0.py` (new) | T8. **Positive control:** the new fields FAIL the 3.0.0 schema, read from `cd5c6b7e` with `git show`, and pass 3.1.0. `"unknown"` is rejected; an unknown key (`licence_edition`) is still rejected in both types; the top level accepts the summary and rejects an unknown block |
| `tests/gamslib/test_license_edition.py` (new) | T1–T4 and the W7–W9 part of T9: the parser (order, line-start anchoring, the licensee never returned), every writer, the cascade `None`s, the W5 restore, and the verifier's provenance and UTC dates |
| `tests/gamslib/test_migrate_schema_v3_1_0.py` (new) | T5: never overwrites, never guesses, refuses a non-3.0.0 start and a second run, `--dry-run` writes nothing. The **real** 3.0.0 DB migrates to a valid DB equal to it apart from the new keys. The §2 invariant holds on the **committed** DB |
| `tests/gamslib/test_migrate_schema_v3.py` | T6: the 2.2.1 rewind now strips v3.1.0's fields too. Otherwise it would start from a hybrid and still pass (design R4) |
| `tests/gamslib/test_db_manager.py` | T7: the chain lists v3.1.0 after v3.0.0. The `--empty` stamp is checked against the bumped `description` by the existing test |

**Each test was shown able to fail.**
- 10 mutants, each applied in a throwaway worktree or restored from a copy, never `git stash`:
  - W1, W2, W3, W4, W7 or W9 removed;
  - the parser's demo-first order swapped;
  - a parser that guesses `"demo"`;
  - the migration overwriting an existing value;
  - the migration guessing `"demo"`.
- Every mutant was caught.
- The invariant test fails on the unmigrated DB.

### Gate

`make typecheck && make format && make lint && make test`, run alone: typecheck, format and lint clean; **5,510 passed**, 10 skipped (the usual 10), 0 `test_path_solver` skips, and no `225*` process dirs created.

`make format`/`lint` cover only `src/` and `tests/`, so the changed `scripts/` files were also checked directly against `main`:
- the ruff counts are unchanged, except in `verify_convexity.py`, which gains 4 `UP045`. Those are the new dataclass fields, kept in the file's existing `Optional[...]` style, which the 7 findings already on `main` share;
- the new migration is ruff-, black- and mypy-clean.

---

## Day 1 — 2026-10-19 · P1: CI, the ledger and the corpus readers · 10 h · + P10c · 2 h

**Branch:** `planning/sprint40-day1-ci` · **Base:** `81ab8e46` · `scripts/`, `tests/`, `data/`, `.github/` and the `Makefile` changed, so the quality gate was run (see *Gate*).

**Owner action, done and verified before the work** (2026-10-18): the `gams-licensed` environment exists. Its custom branch policy is `branch:main` only, it has **no** required-reviewer rule, and `GAMS_ACCESS_CODE` is an **environment** secret. The repository-level secrets are still only the older `PYPI_API_TOKEN`.

### CI: the licensed tier (`CI_LICENSE_DESIGN.md` §3)

- **New `.github/workflows/licensed-solve.yml`:**
  - triggers on `push` to `main`, `schedule` and `workflow_dispatch`, and **nothing else**: no PR trigger of any kind, never `pull_request_target`;
  - runs in `environment: gams-licensed`;
  - installs GAMS with the same pinned installer and SHA-256 guard;
  - activates the license with `gamsgetkey … || exit 1`, after checking the binary exists;
  - masks the access code and every license line.
- **What it prints:** an **edition check** (`--require licensed`) and **licensed solves** of the targets, as a summary only. Listings stay on the runner. **Nothing is uploaded.**
- **Scan gate:**
  - **positive control:** the scan must hit the license file itself;
  - it then scans the one thing the job reports, the summary, and fails closed on a scan error.
  - The `rc` logic was exercised under `bash -e`: hit 0, clean 1, missing file 2.
- **`always()` cleanup:** removes the license, the pattern file and the outputs.
- **Targets** (`.github/licensed-solve-targets.txt`): the 11 MCP-gated models **by identity**, solved from their committed cold goldens (none has an `$include`). The 9 NLP-gated models join once P3 gives them goldens.
- **`scripts/ci/run_licensed_solves.py`, run locally against all 11** (licensed, about 44 s): **all 11 `edition=licensed`**, and the summary carries no header text. Its cold outcomes match Prep Task 7:
  - egypt, glider, robot, shale, tricp and turkey: MS 5;
  - sroute: MS 4;
  - ferts and tabora: rc 3;
  - srpchase and tfordy: MS 1.

  These are measurements and are not gated here; P2 owns them.
- **The real activation test is the first run on `main` after merge.** It goes in Day 2's log.

### CI: the PR side (`CI_LICENSE_DESIGN.md` §6)

- **Both GAMS-installing PR workflows** (`pr19-emit-solve-validation.yml`, `presolve-divergence.yml`):
  - the step is renamed *"Install GAMS (demo edition)"*, with the SHA-256 guard kept;
  - **all three raw `gams audit lo=2` prints are replaced** by `scripts/ci/gams_edition.py --require demo`.
- **`gams_edition.py`:** runs a tiny probe with **all** output (stdout, stderr, listing, process dir) captured in a temp dir, classifies it with the one shared parser, and prints only `edition=…` and the version. It is stdlib-only, because PR19 never `pip install`s. Measured locally:

  | case | output | rc |
  |---|---|---|
  | effective license, `--require licensed` | `edition=licensed` | 0 |
  | demo license | `edition=demo` | 0 |
  | demo license, `--require licensed` | mismatch | 1 |
  | no GAMS | `edition=unknown` | 2 |

  `--require demo` in the PR workflows means **every PR run now proves the license never reached it**.
- **`run_pr19_solves.py` detects the demo refusal.** It reports the model as **`skipped: over the demo ceiling`**, with a `::notice::` and ⏭ in the PR comment. That covers the six Pattern-C cohort targets, which used to fail as if they were emit failures. `passed` stays false, so a **hard-tier** canary that ever outgrew the demo would still fail its tier.
- **This PR touches both workflows**, so their runs on it are the Phase-0 gate's **same-repo negative control**: `edition=demo` and the ⏭ skips. `licensed-solve.yml` has no PR trigger, so a PR cannot even request its environment. The refusal of a non-`main` ref was verified in the throwaway repository (§4).

### P1 Phase-0 gate: the > 1,000-row probe, local half

| edition | 1,500-row NLP |
|---|---|
| licensed | rc 0, **MODEL STATUS 2 Locally Optimal**, SOLVER STATUS 1 |
| demo | rc 7, **refused** (the demo-ceiling line); no SOLVE SUMMARY |

### Decision 1's ledger (`data/floor_provenance.json`, `floor_tracker.py`)

- **The definition is amended in the file's `_README`:**
  - a license-unlocked **cold** match is not genuine;
  - presolve-only matches stay under the existing rule;
  - the fail-before sub-rule applies;
  - no model may be both counted and in the ledger.
- **New `license_unlocked` list (empty) and its schema.** `floor_tracker.py` reports **"Genuine floor: 75 (+0 license-unlocked, not counted)"**.
- **The ledger is deliberately outside `compute_floor`.** The doc-figure "floor" fact keeps reading 75.
- **Validation:** limb must be `license-unlocked-cold-match`; never also an `entries` item; no duplicates; audit fields required.
- **First unit tests for the tracker:** `tests/unit/sprint_audit/test_floor_tracker.py`.

### Decision 2's readers

- **New `data/corpus_admissions.json`**, empty, with its rule and schema.
- **`kpi_block.py --corpus current|continuity`:** `continuity` drops the admitted ids, through `compute_kpis(exclude=…)`. Every block now states its corpus. Today both report **142**.
- **`check_doc_figures.py` is corpus-aware, before Day 3's first admission:**
  - a bare figure is checked against **continuity**;
  - Solve, Match and Translate accept `N/D` and are matched to the corpus whose denominator is `D` (corpus size, parsed count, translated count);
  - a `D` matching neither corpus is a finding.
  - Tests cover all five cases from the brief, plus a forced-admission test proving the bare figure follows continuity.
  - ⚠ There is no `Parse` fact in the registry, so Parse is not covered. Adding one would start checking every "Parse N" in the docs, so it was left out deliberately.

### The danwolfe / decomp check (Prep Task 6 side finding)

`kpi_block` (142) and `batch_parse.get_candidate_models` (140) differ by **exactly `{danwolfe, decomp}`**: convex LPs whose `pipeline_status` is `skipped` (`multi_solve_driver_out_of_scope`). They parse and never translate.

**Resolved by the prompt's second option: the reason is stated in the code**, at both readers, and **pinned by identity** in `test_kpi_corpus.py`.

⚠ **Owner question, not decided here.** PROJECT_PLAN footnote 4 says these two were *excluded* in Sprint 24, but the computed 142 has always *included* them. Re-basing to 140 would move every headline rate mid-series, which close rule C4 exists to prevent happening implicitly. It is recorded for the owner.

### P10c: the leak gate fails on timeouts (`PROCESS_AND_SMALL_ITEMS.md` §10c)

- **`check_golden_staleness.py --fail-on-unverified`** returns **3** when any golden timed out. It prints "covered N of M … NOT a pass".
- **`make check-goldens`** derives `--min-scope` from `git ls-files`, exactly as CI does, and passes both flags.
- **CI's plain call stays soft**, which a test pins.
- **Tests:** a faked timeout gives rc 3 with the flag and rc 0 without it, and **`--min-scope` alone passes a contended run** (the reason the flag exists). A further test checks that the Makefile recipe carries both flags.

### Tests, and their controls

- **New:**
  - `tests/unit/sprint_audit/test_floor_tracker.py`;
  - `tests/unit/sprint_audit/test_kpi_corpus.py`;
  - `tests/unit/test_ci_license_scripts.py`. Every CI-script test asserts that **no `USER:` text** reaches what the script prints or writes, using a synthetic licensee.
- **Extended:** `test_check_doc_figures.py` (two corpora) and `test_gate_scope_assertions.py` (P10c).
- **9 mutants, each applied in a throwaway worktree:**
  - the ledger counted in the floor;
  - the ledger accepting any limb;
  - the continuity exclusion removed;
  - `N/D` resolution removed;
  - bare figures checked against current;
  - `--fail-on-unverified` returning 0;
  - PR19 refusal detection off;
  - `gams_edition` echoing the listing;
  - the licensed-edition gate removed.
- **All 9 are caught.** Two were not caught on the first run, and both were fixed:
  - the bare-figure mutant passed, because the live test runs with no admissions, where the two corpora agree. A forced-admission test now catches it;
  - the first `gams_edition` mutant was malformed and leaked nothing, so it proved nothing. It was replaced by one that prints the listing.
- **Knock-on:** the procdir invariant now covers the two new GAMS launchers (`gams_edition.classify`, `run_licensed_solves.solve_one`), and both pass it.

### PR #1762 review round 1

- **Stale listings:** `run_licensed_solves.py` **and** `run_pr19_solves.py` (the same defect, found by sweeping for it) now delete the model's listing before GAMS starts. A reused `--out` / persisted `--scratch-base` can no longer have an OLD listing classified as this run's result.
- **`--fix --fail-on-unverified`** returned 0 when one golden was refreshed and another timed out. The strict check now guards **every** success path of the plain sweep.
- **`kpi_block.py --format line`** writes Solve/Match/Translate as `N/D` when a corpus is named. Otherwise a correct `--corpus current` line would be checked as continuity and flagged after the first admission.
- **Each fix has a revert control, all caught.** The first PR19 stale-listing test was **vacuous**: a missing GAMS returns before the listing is read, so it stayed green with the fix reverted. It now uses the real hazard, GAMS running without writing a listing.

### Gate

`make typecheck && make format && make lint && make test`, run alone: typecheck, format and lint clean; **5,551 passed**, 10 skipped (the usual 10), 0 `test_path_solver` skips, no `225*` process dirs created. That was at a load average of about 35 at start, rising to about 134 by the end, with no timeouts.

The changed `scripts/` files were also checked directly against `main`:
- ruff counts are unchanged;
- black only touched lines this PR changed;
- the two new CI scripts are ruff-, black- and mypy-clean. One unused import, found by that check, was removed.

---

## Owner decision — 2026-10-19 · the KPI corpus is re-based 142 → 140

**Branch:** `planning/sprint40-rebase-140` · **Measured at:** `135d1037`

**Decision (owner, 2026-10-19):** re-base the headline corpus from **142 to 140**, removing **`danwolfe`** and **`decomp`**.

**Why the question existed** (Prep Task 6 side finding, Day 1):
- `kpi_block.py` selected the corpus by convexity alone, so it counted both models.
- `batch_parse.get_candidate_models` honoured their `pipeline_status: skipped` (`multi_solve_driver_out_of_scope`), so it selected 140.
- `run_full_test.get_candidate_models` did **not** honour the skip. So the pipeline kept re-running both models, and translation refused them every time, writing two permanent translate failures into the DB.
- PROJECT_PLAN footnote 4 described them as excluded since Sprint 24; the computed series never excluded them.

**What changed:**
- **One corpus rule, three readers.** A candidate is convex **and** not `pipeline_status: skipped`. `kpi_block.compute_kpis`, `batch_parse.get_candidate_models` and `run_full_test.get_candidate_models` all apply it, and `floor_tracker`'s advisory mechanical count does too.
- **`tests/unit/sprint_audit/test_kpi_corpus.py`** pins all three readers to **one identical 140-model set**, a set rather than a count. Both models are named, and the test asserts they are excluded by the skip, not by convexity. Removing the skip from any one reader fails it (3 mutants, all caught).
- **PROJECT_PLAN:**
  - new Rolling-KPIs **footnote ⁹**, marked on the S40 Parse, Translate and Match cells;
  - **footnote 4 corrected**;
  - the Sprint 40 acceptance criteria restated on 140;
  - P3's ceiling becomes "at most 149".
- **`SPRINT_40/PLAN.md`:** close rule C4 and the acceptance table now say 140. **`PLAN_PROMPTS.md`:** Day 5 now says 140. Records of past findings, such as Task 6 and Day 1, are left as written.

**Effect, measured at `135d1037`.** No count moved; only the denominators did.

| | 142 (before) | 140 (after) |
|---|---|---|
| Parse | 142/142 · 100.0% | 140/140 · 100.0% |
| Translate | 135/142 · 95.1% | **135/140 · 96.4%** |
| Solve | 111/135 · 82.2% | 111/135 · 82.2% |
| Match | 95/142 · 66.9% | **95/140 · 67.9%** |
| genuine floor | 75 | 75 (neither model ever matched) |

⚠ **The Translate and Match rate rises are a RE-BASE, not progress.** Across this boundary, compare counts, not rates. That is what footnote ⁹ is for.

**Decision 2's continuity series is this 140.** No NLP-gated model had been admitted when the re-base landed, so continuity and current are both 140 today.

---

## Day 2 — 2026-10-20 · RT: the license-neutrality gate · 3 h · + P2: batch preparation · 5 h · + P3: licensed convexity · 2 h

**Branch:** `planning/sprint40-day2-neutrality` · **Base:** `94fe8271` (the corpus is 140 since the re-base, PROJECT_PLAN ⁹).

### P1's gate, the licensed half: recorded as the Day 1 prompt requires

- **`licensed-solve.yml`'s first runs on `main` both succeeded.** `39294915808` ran at `135d1037` and `39327845244` at `94fe8271`. In each:
  - the license activated from `GAMS_ACCESS_CODE` on a **GitHub-hosted** runner, which was the open question behind the CI design;
  - the edition check read `edition=licensed`;
  - **all 11 targets ran licensed**;
  - the scan gate's positive control **hit**, and the summary carried **no license text**;
  - the license was removed;
  - **0 `USER:` lines appeared in the published log.**
- **The negative control** was PR #1762's own demo-only runs:
  - PR19 printed `edition=demo` twice, and showed **⏭ skipped: over the demo ceiling** with a `::notice::` for exactly the six over-ceiling cohort models;
  - presolve-divergence printed `edition=demo` and checked 40 models;
  - 0 `USER:` lines in either log.
- **P1's Phase-0 gate is complete.**

### RT: the first licensed full run, close rule C8

- **The run:** `run_full_test.py`, all 140 candidates, in a throwaway worktree at `94fe8271` with the raw corpus copied in. 2026-10-19T21:36 → 22:55Z, **79 min**, rc 0, 140 processed, 0 skipped. **The load average stayed ≈ 3 throughout, so load-induced timeouts are not a factor.** It was never persisted.
  - ⚠ The first launch was **void** and is recorded as such. The raw corpus was copied into `raw/raw/`, so all 140 models were skipped as "file not found". It was fixed, smoke-tested on one model, and relaunched.
- **The diff,** against the committed DB, on outcome, objective (rel 1e-6), verdict, parse and translate: **198 models outside the two populations, 1 moved.**

  | model | before | after | cause |
  |---|---|---|---|
  | `iswnm` | translate **timeout** (600 s, recorded 2026-06-20) | translate **success** in 62 s → `path_syntax_error` | **a stale row, not the license** |

  - Translation is pure Python and never calls GAMS.
  - The committed row predated the AD speed-ups since Sprint 28, and was never re-run.
  - The new MCP fails to compile with **identical errors under both editions** (`$140`, `$141`, `$257`; no refusal), measured by compiling it licensed and demo.
  - ⚠ When a persisted run lands it, report it as a **stale-row correction** (Translate +1, `path_syntax_error` +1, issue #931), **not** as a fix.
- **Editions:** every one of the **136** solved rows from this run carries `licensed`. The 4 `null` rows (`mexls`, `nebrazil`, `saras`, `sarf`) are cascade `not_tested` rows: translation failed, no GAMS ran, so there is nothing to classify. That is writer W4, correct by design.
- **C8 holds. Unknown 1.5 is CLOSED:** the license changes no outcome outside the size-refused populations.

### P2: batch preparation

- **Byte identity:** `check_golden_staleness.py --models <the 11> --fail-on-unverified` re-emitted all 11 cohort models at HEAD: **11 checked, 0 drifted, 0 failed, 0 unverified.** Every committed golden is current, so the batch measures the committed emits.
- **turkey's pre-fix golden is pinned for Decision 1's fail-before sub-rule:**
  - turkey's golden last changed at **`95ba01ea`** (Sprint 35 Day 6, "turkey $161 compile-recovery"), which is a one-line diff;
  - the pre-fix golden is `95ba01ea^:data/gamslib/mcp/turkey_mcp.gms` (sha256 `ad6d57d21c0e4ba6…`); the current one is `70aaddac99c91a8f…`;
  - there is no committed turkey presolve golden;
  - the licensed run of the pre-fix golden is Day 3's.
- **The batch:** one `run_full_test.py --model <id>` per model, in a throwaway worktree at `94fe8271` (`/tmp/p2/wt`). 23:16 → 23:28Z, **11.5 min**, rc 0 for all 11.
  - ⚠ **Deviation:** the prompt says "tonight's nightly slot". The slot was sized to be unattended and uncontended, and the machine was idle (load ≈ 4), so it ran then.
  - **Every row carries `license_edition: licensed`** and its attribution.
  - **All 11 buckets reproduce RT exactly:**
    - `tfordy` and `turkey`: `model_optimal_presolve` + **match**, `MCP-SOLVED`;
    - `glider` (presolve) and `srpchase` (cold): solve, **mismatch**;
    - `egypt`, `robot`, `shale`, `sroute` and `tricp`: `model_infeasible`, `MCP-FAILED`;
    - `ferts` and `tabora`: `path_solve_terminated`, `NO-SOLVE`.
  - It generated **8 `<id>_mcp_presolve.gms`** files, one for each model that took the presolve retry. Day 3 decides what to persist.
  - ⚠ **`tricp` writes `cp.eps` into the working directory** (its source plots). Run from the repo root, it leaves an untracked file. One more reason never to `git add -A` after a pipeline run.

### P3: licensed convexity (output-only)

- **The run:** `verify_convexity.py --model <id> --timeout 600 --output <scratch>` for the 9 in-scope NLP-gated models. `andean` is MIP: excluded, never relaxed. The working tree stayed clean (no `catalog.json` or DB write).
- **All 9 classify convex: 5 `verified_convex`** (airsp, airsp2, indus89, msm, phosdis) **and 4 `likely_convex`** (emfl, jbearing, minsurf, torsion). This matches Prep Task 7.
  - Every result carries W9's new provenance: `licensed`, the solver actually used, `54.2.1`, and a per-result UTC `verification_date`.
  - ⚠ **`airsp2` classifies from a `DECISM` solve**, not the CPLEX LP that was requested. This is the multi-solve reference question (`PLAN.md` §3 P3) to settle before its comparison enters a headline.
- **W10, `scripts/gamslib/apply_convexity_results.py`:**
  - `--db` is required, with no default;
  - `convexity` is **replaced, not merged**;
  - non-nullable fields are omitted when `None`, so a successful result writes no `error: null`;
  - `license_edition` and `gams_version` are always written;
  - each result's own `verification_date` is copied verbatim, and a result without one is **refused**;
  - **the corpus hold:** a model entering the convex set is refused unless it is `--admit`-ted **and recorded in `data/corpus_admissions.json`**. The record is required so that `kpi_block --corpus continuity` can drop it; without it, continuity would grow silently anyway;
  - an `--admit` that admits nothing is refused;
  - MINLP/MIP and unknown ids are refused;
  - every problem is reported in one run, and nothing is written on refusal;
  - it validates before writing and backs up to the git-ignored `data/gamslib/archive/`.
- **On the real report, against a scratch DB:**
  - with no `--admit`, it **refuses all 9**;
  - with `--admit` but no record, it **refuses**;
  - with both, it applies and validates, and the summary says "the candidate corpus moves by +9: report both denominators (C4)";
  - afterwards `kpi_block --corpus current` reports **149** candidates and `--corpus continuity` **140**. The committed DB was untouched.
- **Tests: `tests/gamslib/test_apply_convexity_results.py` (12), with 6 mutants, all caught.** The first run let three survive, because three tests were **vacuous**: each was refused by a *different* guard than the one it claimed to test. Each now isolates its guard:
  - the hold: the model is recorded but not admitted;
  - the MIP refusal: `andean` admitted and recorded, asserted on the planner's own message;
  - the missing date: asserted on the refusal itself, because a `null` date would also fail schema validation.

### PR #1764 review round 1 (W10)

- **`verification_date` must be RFC 3339.** It uses the attribution inspector's shape regex plus a range check. jsonschema does not enforce `format` here, so `--validate` alone would have written a malformed stamp that the inspector then rejects.
- **One admissions reader.** W10 now reads the ledger with `kpi_block.load_admissions`. Its first version **filtered out** malformed entries, so it could admit from a ledger the continuity reader then rejects. This is the same class of defect as the 142/140 reader split.
- **Entry requires `license_edition == "licensed"`**, because Decision 2 admits by the licensed verifier's classification. Updates to models already inside are not restricted.
- **The summary reports CANDIDATE movement** (convex and not skipped, as `kpi_block` counts). A skipped `danwolfe` changing status is no longer reported as leaving the corpus. The hold stays on the convex-set transition, so it still applies to skipped models.
- **22 tests. 10 mutants (the 6 from before plus one per fix), all caught.**

### PR #1764 review round 2 (W10)

- **The write is atomic.** W10 now persists through `db_manager.save_database` (a same-directory temp file, then a rename). The old `write_text` truncated the live DB first, so a disk-full or interrupted write could leave partial JSON, and `--no-backup` removes the only recovery. A test simulates a half-written document followed by a write error: the live DB is untouched and still parseable.
- **The tests use a deterministic fixture DB**, independent of the committed one. Day 3's admission of `torsion` would otherwise have made the "entering without `--admit`" test pass for the wrong reason, and the admitted case fail on an unused `--admit`. Every starting state is now explicit, and a test checks that the fixture is itself schema-valid.
- **24 tests. 11 mutants, all caught**, including a non-atomic in-place write.

### Gate

`make typecheck && make format && make lint && make test`, run alone: typecheck, format and lint clean; **5,567 passed** at the first push, then **5,577** after review round 1, and **5,579** after round 2, 10 skipped (the usual 10), 0 `test_path_solver` skips, no `225*` process dirs. `make check-doc-figures` is clean.

⚠ **A false positive found and worked around, not fixed.** The fact *"presolve rows whose generated file is absent"* includes the pattern `all N rows`, which reads ANY "all *N* rows …" sentence as that count. It flagged this log's edition sentence. The sentence was reworded. Narrowing the pattern is a checker change with its own tests, so it is left for a separate PR.

---

## Day 3 — 2026-10-21 · P2: batch results, attribution and residuals · 6 h · + P3: admission by rule · 4 h

**Branch:** `planning/sprint40-day3-cohort` · **Base:** `a428f909`.

### P2: the batch, persisted (the C3 pin)

- **The batch commit is `f1771435`.** It holds the 11 cohort rows and the 8 `<id>_mcp_presolve.gms` emits from Day 2's batch (throwaway worktree at `94fe8271`).
  - The results DB is byte-unchanged between `94fe8271` and `a428f909` (`git diff --quiet`). The batch DB differs from `main` only in those 11 rows and `updated_date`, so the rows were ported verbatim, not re-run.
  - **All 8 presolve emits are persisted**, including the 5 whose retry did not solve. That follows the committed convention: 6 such files are already committed for rows that do not reference them (agreste, cesam, fawley, korcge, otpop, rocket).
- **C3, the pre-written wording, with the figures from `kpi_block.py` at `f1771435`:**

  > **Cohort result — license-unlocked, not recovered** (batch at `f1771435`): of the 11 MCP-gated models, `4` solve and `2` match; `path_solve_license` → `0`. None of these is a fix: the emits are byte-identical to their committed goldens; only the ability to run them changed.

  - The 4 that solve are `glider`, `srpchase`, `tfordy` and `turkey`, and the 2 that match are `tfordy` and `turkey`. On the 140-model corpus, Solve moves 111 → 115 and Match 95 → 97, all from the cohort.
  - turkey's floor credit (below) is for its **Sprint 35** fix, under the fail-before sub-rule. It does not make the Sprint 40 move a fix, and it is booked separately (C5).
- **C1: `path_solve_terminated` is 2, and both are cohort rows: `ferts` and `tabora`.** That is a **first-measurement influx**, as Task 7 predicted, not a regression. Over every row outside the two populations it stays **0**.

### P2: per-model verdict, attribution and residual

Every model has a comparison verdict, an attribution, and either a KKT-residual verdict or a recorded harness failure. Attribution comes from two sources:
- **row:** the pipeline's own `mcp_attribution`, which classifies the solve the row claims;
- **standalone:** `check_mcp_solve_attribution.py` over all 11 (`--workdir` scratch, licensed). It always classifies the **presolve** emit.

`kkt_residual.py` ran on the 9 non-matches. Both runs were in the throwaway worktree: each launches GAMS with `cwd` at the project root, and `tricp` writes `cp.eps` there.

| model | outcome | verdict | row attribution | standalone (presolve emit) | KKT residual | route (Day 4) |
|---|---|---|---|---|---|---|
| `tfordy` | `model_optimal_presolve` | **match** | `MCP-SOLVED` | `MCP-SOLVED` (antala/LP, antalb/LP, then mcp_model MS 1) | — (match) | — |
| `turkey` | `model_optimal_presolve` | **match** | `MCP-SOLVED` | `MCP-SOLVED` (turkeyn/NLP, turkeyl/LP, then mcp_model MS 1) | — (match) | — |
| `glider` | `model_optimal_presolve` | mismatch | `MCP-SOLVED` | `MCP-SOLVED` | **`case_b`**, worst `stat_cl(h0)`, rel 2.0 | R-B-glider |
| `srpchase` | `model_optimal` (cold) | mismatch | `MCP-SOLVED` | `NO-SOLVE` (the presolve emit does not compile) | harness failed: `$140` ×2 | R-PRE-140 |
| `egypt` | `model_infeasible` | `not_tested` | `MCP-FAILED` | `NO-SOLVE` | harness failed: `$140` ×2 | P4 + R-PRE-140 |
| `shale` | `model_infeasible` | `not_tested` | `MCP-FAILED` | `NO-SOLVE` | harness failed: `$148` ×2 | P4 |
| `robot` | `model_infeasible` | `not_tested` | `MCP-FAILED` | `MCP-FAILED` (MS 5) | **`case_b`**, worst `stat_step`, rel 10.1 | R-B-robot → P5 |
| `sroute` | `model_infeasible` | `not_tested` | `MCP-FAILED` | `MCP-FAILED` (MS 4) | **`case_b`**, worst `stat_x(portland,chicago,boston)`, rel 1.0 | R-B-sroute |
| `tricp` | `model_infeasible` | `not_tested` | `MCP-FAILED` | `MCP-FAILED` (MS 5) | **`case_b`**, worst `stat_x(n1,k0)`, rel 1.69 | R-B-tricp |
| `ferts` | `path_solve_terminated` | `not_tested` | `NO-SOLVE` | `EMBEDDED-ONLY` (stat2/LP MS 1) | harness failed: `EXECERROR = 46` | R-EXEC |
| `tabora` | `path_solve_terminated` | `not_tested` | `NO-SOLVE` | `EMBEDDED-ONLY` (tabora/LP MS 1) | harness failed: `EXECERROR = 36` | R-EXEC |

- **Both claimed matches are `MCP-SOLVED` in both sources,** so both are booked. Neither is the `weapons` shape.
- **Every row reproduces Task 7's dry run** (`COHORT_DRY_RUN.md`), at `79eeccff` then and `94fe8271` now:
  - the 4 `case_b` verdicts;
  - the 5 harness failures and their listing errors;
  - 6 harness failures were expected, because Task 7 also counted `jbearing`, which is P3's (Day 4).
- **Measured, not routed.** Day 4 opens the routing notes.

### P2: the floor (C5)

- **No license-unlocked COLD match, so the ledger stays empty.** The only cold solve, `srpchase`, mismatches.
- **`tfordy` is methodology: not counted, and not in the ledger.** Its match is presolve-only, and no emit fix is identified for it. Its golden last changed at `e0be4fb1` (Sprint 26, a pipeline-retest regeneration). The fail-before sub-rule applies only to a model whose emit a named fix changed. Without one, there is no pre-fix golden to run.
- **`turkey`: the fail-before sub-rule holds, so it is credited fix-driven genuine. Floor 75 → 76.**
  - **The fix:** `95ba01ea` (Sprint 35 Day 6, a one-line golden diff) quotes the domain-less 2-D set `ao` per component, ending `$161` ×6. turkey was `path_solve_license` under the demo, so its match could never be measured.
  - **Fail-before:** the pre-fix golden `95ba01ea^:data/gamslib/mcp/turkey_mcp.gms` (sha256 `ad6d57d21c0e4ba6…`, pinned on Day 2), run **licensed**, fails to compile: `$161` ×6, then the `$257`/`$141` cascade. **It does not match.**
  - That is decisive for the presolve emit as well. A compile error stops the whole file, and the presolve emit carries the same MCP body after its `$include`.
  - **The current cold golden** (licensed) reaches **MS 5 @ -5.473** against an NLP of 29078.2106. The match therefore arrives through the presolve warm start: the `presolve-match-genuine` limb, the same shape as `elec` and `twocge` in Sprint 38.
  - **Recorded** as an `entries` item in `data/floor_provenance.json`, with `expected_floor` 76. `floor_tracker.py`: **"Genuine floor: 76 (+0 license-unlocked, not counted)"**.
  - ⚠ The PLAN's REPLAN row for turkey covers only the case where the pre-fix golden **matches**. This is the other branch, read directly from the owner's sub-rule (`OWNER_DECISION_BRIEF.md` §Decision 1, answered at `b44344a2`): *"credited as fix-driven genuine only if its pre-fix golden, run under the license, does not match."*
- **`test_floor_tracker.py` no longer pins the committed figure.** It read the committed file and asserted 75. One test also put `turkey` in the ledger, which the "never both" rule would now reject for the wrong reason. The behavioural tests build on a deterministic in-test fixture: baseline 73 plus 2 entries, 75. The committed file gets a self-consistency test instead, because `expected_floor` already pins its number. This is the same fragility as PR #1764's round 2.

### P3: admission by rule (Decision 2 = A)

- **Precondition met:** Day 1's corpus-aware `check_doc_figures.py` is on `main` (PR #1762, `135d1037`).
- **The 9 are recorded by identity** in `data/corpus_admissions.json`, one entry each with its classification and the Day 2 verifier run as evidence. W10 was then applied for real (`191ed91f`): `apply_convexity_results.py --input <Day 2's report> --db data/gamslib/gamslib_status.json --admit <the 9> --validate`.
  - Validation passed, and the summary read "the candidate corpus moves by +9 / -0: report both denominators (close rule C4)".
  - **5 `verified_convex`:** airsp, airsp2, indus89, msm, phosdis. **4 `likely_convex`:** emfl, jbearing, minsurf, torsion.
  - `andean` is MIP: excluded, never relaxed.
- **Both denominators derive mechanically from `kpi_block.py` at `191ed91f`:** `--corpus current` **149** candidates, and `--corpus continuity` **140**. At admission the Solve and Match figures were the same on both (115 and 97), because no admitted model had a pipeline row yet.
- **The multi-solve reference question, recorded (`PLAN.md` §3 P3).** The verifier classifies a model from its **last** solve. For a multi-solve model that may not be the solve the comparison should use. `airsp2` is the visible case: it classifies from a `DECISM` solve, not the requested CPLEX LP.

  | model | solve statements | shape |
  |---|---|---|
  | `airsp` | 3 | `alloch`, then `allocs` twice (LP) |
  | `airsp2` | 6 | `fixed`, `expval`, `deteq`, `fixed` … (LP; one solved by DECISM) |
  | `msm` | 5 | `msm` five times (LP) |
  | `phosdis` | 1, **in a loop** | `loop(ss$(count < 4), … solve route …)` with `solveOpt = replace` |
  | `torsion` | 2 | `torsion`, then `torsionx` (a second formulation, NLP) |

  - ⚠ **`torsion` is a fifth case**, which the PLAN's list of four omits. It solves two **different models**, so "the NLP objective" has two candidates.
  - Each is admitted by rule anyway, because Decision 2 is on classification. **Every comparison among these five stays out of the headline until the reference question is settled.**

### P3: the pipeline for the admitted models

- **The run:** `run_full_test.py --model <id>`, one model at a time, in a throwaway worktree at the admission commit `191ed91f`. 02:59 → 03:22Z, **22.5 min**, rc 0 for all 9, load ≈ 3–6. It started only after Day 3's residual runs had finished, so nothing contended with the 600 s translate budget.
  - The worktree DB differed from the branch only in these 9 rows. The rows and the 6 goldens the run generated are persisted in `570d1c1b`.
  - The goldens are `airsp2_mcp`, `airsp2_mcp_presolve`, `jbearing_mcp`, `minsurf_mcp`, `torsion_mcp` and `torsion_mcp_presolve`. None contains license text.
- **All 9 reproduce Task 7:**

  | model | parse | translate | outcome | verdict | attribution |
  |---|---|---|---|---|---|
  | `airsp2` | ✓ | ✓ 2.5 s | `model_optimal_presolve` | **match** @ 1037.246 | `MCP-SOLVED` |
  | `torsion` | ✓ | ✓ 14.8 s | `model_optimal_presolve` | **match** @ -0.4175 | `MCP-SOLVED` |
  | `jbearing` | ✓ | ✓ 37.8 s | `path_syntax_error` | `not_tested` | `NO-SOLVE` |
  | `minsurf` | ✓ | ✓ 13.0 s | `path_solve_terminated` | `not_tested` | `NO-SOLVE` |
  | `airsp` | ✓ | **timeout** (600 s) | — | `not_tested` | — |
  | `msm` | ✓ | **timeout** (600 s) | — | `not_tested` | — |
  | `emfl` | ✗ `lexer_invalid_char` | — | — | `not_tested` | — |
  | `indus89` | ✗ `lexer_invalid_char` | — | — | `not_tested` | — |
  | `phosdis` | ✗ `lexer_invalid_char` | — | — | `not_tested` | — |

  - **Both matches are presolve-only and both models are multi-solve** (above). Under C5 they are methodology: not counted, and not in the ledger. Under the reference question, **neither enters the headline** until it is settled.
  - **C1:** `minsurf` at `path_solve_terminated` is an **NLP-gated first measurement**, as Task 7 predicted. It is reported by identity, not as a regression.
- **The two denominators, from `kpi_block.py` at `570d1c1b`:**

  | quantity | continuity (140) | current (149) |
  |---|---|---|
  | Parse | 140 | 146 |
  | Translate | 135 | 139 |
  | Solve | 115 | 117 |
  | Match | 97 | 99 |
  | `path_solve_terminated` | 2 | 3 |
  | `path_syntax_error` | 6 | 7 |

  - The scope additions add **+2 Solve and +2 Match on `current` only**, and both are the multi-solve presolve matches. **None is booked as a recovery (C4).**
  - The expanded-scope headline sentence is Day 5's. The corpus record is Day 4's.
- **Routing is Day 4's:** R-JB-171 (jbearing), R-EXEC and R-B-minsurf (minsurf), parse (emfl, indus89, phosdis) and translate performance (airsp, msm).

### What the persisted rows broke, and why each change is not a loosening

The first `make test` on this branch failed 6 tests. Each one had pinned **the state before Day 3**, not a property.

- **`check-index-repeats`, P2 (a CI gate): 2 "new" violations, both already-baselined defects in a new file.**
  - `egypt_mcp_presolve: tranc(rp,rp)` and `shale_mcp_presolve: ts(tf,tf)` are the **same** Class-A guards the baseline already holds for `egypt_mcp` and `shale_mcp`. The presolve emit carries the same MCP body after its `$include`, so committing it adds a second copy of a known defect, not a new one.
  - The baseline grows **9 → 11** (`--update-baseline`, both entries named). P1 is still 0 over 3,370 heads.
  - **P4 owns both** (Class-A `tranc(rp,rp)` and `ts(tf,tf)`, `PLAN.md` §3). One fix removes each defect from both emits, and the baseline then shrinks by 2 per model.
- **`test_kpi_corpus.py` (4) and `test_check_doc_figures.py` (1)** asserted *"no admissions yet, so both corpora are 140"*. That was Day 1's state, which Day 3 ends by design. They now state the invariant instead:
  - **continuity stays 140** (the re-based base series);
  - **current = 140 + the admissions recorded in `data/corpus_admissions.json`**;
  - the three corpus readers still select one **identical** set. That set is now the current corpus, and continuity is that set minus the admissions.
  - The scratch-admission tests admit one more model **on top of** the committed admissions. Derived, not counted, so the next admission does not break them for the wrong reason.
- **`test_floor_tracker.py`:** see the floor section above.

**Controls.**
- Dropping turkey's entry while `expected_floor` stays 76 fails the floor self-consistency test.
- Dropping one admission from `data/corpus_admissions.json`, while its row stays convex in the DB, fails all 5 rewritten corpus tests. That is the silent growth they guard against.

### Gate

`make typecheck && make format && make lint && make test`, run alone: typecheck, format and lint clean; **5,580 passed**, 10 skipped (the usual 10), 0 `test_path_solver` skips, no `225*` process dirs. `make check-index-repeats` passes: P1 0 / 3,370, P2 11 = baseline. `make check-doc-figures` is clean.

---

## Day 4 — 2026-10-22 · P2: route every non-match · 5 h · + P3: pipeline results and the corpus record · 5 h

**Branch:** `planning/sprint40-day4-routing` · **Base:** `de0a7186`. Measured and routed; **nothing fixed in place** (P10's rule).

### P2: the routing notes, opened

Each note reproduces its fingerprint (licensed GAMS 54.2.1, committed goldens at `de0a7186`), names a fix surface or the first step to find one, and is opened as a GitHub issue with an issue document under `docs/issues/`.

| route | models | issue | fingerprint → surface |
|---|---|---|---|
| **R-PRE-140** | egypt, srpchase | **#1766** | The presolve dual-transfer block initializes `.l` for multipliers **the MCP never declares** (`lam_landb`, `lam_waterb`; `nu_slack`, `lam_demand`). The `$140` is a symptom: **both models' source equations are dropped upstream**, by two different defects (next rows). |
| ↳ egypt's drop | egypt | **#1776** (new) | **AD, traced:** `_diff_sum`'s partial-match branches are gated on `len(wrt) > len(binders)` and `<`. Equal counts, as in `sum((c,z)…, xcrop(r,c)…)`, fall through to an assumed positional correspondence, so the derivative is 0. `landb` and `waterb` vanish, and **`labbal` silently loses its `xcrop` terms.** 10-line reproducer. A sibling of #1755, so P7 is the natural owner. |
| ↳ srpchase's drop | srpchase | **#1385** (comment) | The #1385 dynamic-subset short-circuit skips `slack` and `demand` entirely. **Without `demand`, the cold MCP "solves" at objective 0** against an NLP of 0.4001. P6's surface; srpchase is its minimal fail-before. |
| **R-EXEC** | ferts, tabora (+ minsurf, P3) | **#1767** | **The execution-error lines, captured this time, sanitized.** ferts: 36× `comp_mb.lam_mb` *empty equation, variable NOT fixed* (`EXECERROR = 36`). tabora: 36× `comp_lb.lam_lb` (`36`). minsurf: 4× `v_fx_<corner>.nu_v_fx_<corner>` *unmatched equation* (`4`). Data-empty inequality instances need their multiplier fixed (the #1041 class); minsurf's corners are a separate shape. |
| **R-B-glider** | glider | **#1768** | `case_b`, `stat_cl(h0)` at relative **2.000**, i.e. raw 258.4 against a **global** dual scale of 129.2 (the largest transferred multiplier). *Hypothesis, pending a per-row derivative trace:* a doubled or sign-flipped `h0` term. The ratio alone does not establish that. `stat_step` is second (0.38); glider is P5's candidate. |
| **R-B-sroute** | sroute | **#919** (re-measured) | The 307 empty-equation errors are gone; it is now MS 4 and `case_b`. Its worst row `stat_x(portland,chicago,boston)` has relative residual **1.000**: raw 260 against a **global** dual scale of 260, so it does **not** show the whole gradient is missing. The golden already carries `lam_nb` (`nb` is `=g=`). Leads, hypotheses until traced: the emitted objective coefficient is `darc(i,ip)` where `cd` gives `darc(ip,ipp)`, and the row has one `lam_nb(i,ip)` where the incoming (`nb(i,ipp)`) and outgoing (`nb(i,ip)`) contributions give two. First step: trace the objective coefficient and both `lam_nb` terms against a hand derivative. |
| **R-B-tricp** | tricp | **#933** (re-scoped and retitled) | ⚠ **The 6.15e6 equality residual was checked first, as the note required. It is a real primal defect:** the source's `eq1(e(i,j))` is violated at the transferred NLP point in **42 of 54** instances (max 6.154e6 at `eq1(n7,n9)`; `defobj` 4.5e-13). The emitted `eq1` reads faithful, so the suspect is the transferred point (`eq1` is declared `(n,n)`, the repeated-domain class). The harness counts equality residuals as informational, which is why it said "consistent". **The `case_b` verdict is not the whole story.** |
| **R-B-robot** | robot | **#1769** → **P5** | `case_b` at **`stat_step`** (rel 10.13), the same row as lnts. A confirmed member of P5's class. |
| **P4** | egypt, shale | (P4) | Class-A `tranc(rp,rp)` / `ts(tf,tf)`, unchanged. ⚠ **egypt also has #1776's AD cause.** Re-measure it after P7 before attributing anything to P4. |

- **`ISSUE_933`'s re-scope is committed.** The doc's re-scope was already in Prep Task 7 (`ddccb2c1`). What was missing was the GitHub side, done today: retitled, plus the re-scope comment with the `eq1` finding. The doc carries a new *Current Status (2026-10-20)*.
- **Corrected before commit (the verification discipline).** The first draft of #1766 and of the #1755 comment said egypt's drop "matches `_sum_should_collapse`'s positional pairing".
  - **Instrumenting it refuted that.** `_sum_should_collapse` returns False for the failing two-binder sum **and** for the working one-binder sum, so it is not where they diverge.
  - The trace then located `_diff_sum`'s `>` / `<` gates, and the mechanism was filed as its own issue, **#1776**.
  - #1766, the #1755 comment and the #927 comment were corrected in place. #1770's classification as "the repeated-index family" is marked as a hypothesis, because the builder has not been traced.

### P2: sweep of the changed set

Every live doc that named a cohort or admitted model's bucket was checked. Sprint logs, CHANGELOG entries and completed issues are history and were left alone.

- **`ISSUE_927` (egypt "demo license limit"):** superseded. **Closed by owner decision** (2026-10-20, as not planned), and the doc moved to `docs/issues/completed/`.
- **`ISSUE_928`, `ISSUE_1290` (ferts 63-character identifiers):** **no longer reproduce.** The golden compiles with 0 errors; the only ≥ 64-character tokens are in `*` comments, and the identifiers are hash-truncated. **Closed by owner decision** (2026-10-20, as completed), and both docs moved to `docs/issues/completed/`.
- **`ISSUE_1385`:** the srpchase wrong-answer measurement, added.
- **`ISSUE_1755`:** egypt recorded as a related sibling (#1776), **not** an instance. Its "latent in the corpus" scope line stands.
- **`data/gamslib/convexity_report.md`:** its 2026-01-01 "License Limit Errors" list is marked superseded by the Day 2/3 licensed verification.
- **No other live doc** (guides, schema docs, PROJECT_PLAN's current sections) quotes a cohort model's old bucket. PROJECT_PLAN's Sprint 40 section dates its list "as recorded at the S39 close", which is correct as written.

### P3: results for the admitted models, and their routes

- **Reaching an MCP (4):**
  - `airsp2` and `torsion` **match via presolve**, both `MCP-SOLVED`; both are multi-solve, so they stay out of the headline;
  - `jbearing` → **#1770** (R-JB-171);
  - `minsurf` → **#1767** (R-EXEC) + **#1771** (R-B-minsurf).
- **`jbearing`'s `$171`:** the stationarity body writes **`v(nx+1,nx)` and `v(nx,nx)`** where `v(nx+1,ny)` and `v(nx,ny)` are meant, so position 2 takes position 1's index. `check-index-repeats` P1 checks heads only, so it cannot see this.
- **`minsurf`:** `kkt_residual.py` re-run, **`case_b`, `stat_v(x39,y6)` rel 40.18**, reproducing Task 7. Its `stat_v` wraps its terms in `sum((i,j), … 1$(nx(i) and ny(j)))` although no term depends on `i`/`j`; jbearing shares the construction. Recorded as a lead, not a diagnosis.
- **Reaching none (5), routed:**
  - parse: `emfl` → **#1772** (**inline-guarded `$eval` does not define `%new%`**: `$if not set N $eval new …` is missed, so `%new%` reaches the lexer; standalone `$eval` is already implemented); `indus89` → **#1773** (`Singleton Set`); `phosdis` → **#1774** (`for(s = a to b, …)`, with its solve inside the loop);
  - translate: `airsp`, `msm` → **#1775** (600 s, uncontended).
- **The corpus record:** `docs/planning/EPIC_4/SPRINT_40/CORPUS_RECORD.md`. Both denominators come from `kpi_block.py --corpus` at `de0a7186`:
  - **continuity 140:** Solve 115, Match 97;
  - **current 149:** Solve 117/139, Match 99/149;
  - plus the admitted 9 by identity, with outcome and route.
  
  It is the source for Day 5's C4 sentence.

### Counts

- **Unrouted non-match fingerprints: 0.**
- **Issues opened: 11** (#1766–#1776). **Existing issues updated: 7** (#919, #933, #1385, #1755, #927, #928, #1290).
- **Closed by owner decision:** #927, #928 and #1290. Their docs moved to `docs/issues/completed/`.

### Gate

**No `src/` or `tests/` change** (the stable-scope waiver). The changes are docs, issue documents and one generated-report note. `git diff main...HEAD --name-only | grep -c '\.py$'` is 0 at the final commit. `make check-doc-figures` is clean.

---

## Day 5 — 2026-10-23 · P3: the expanded-scope sentence · 1 h · + P7: #1755, the diagonal defect · 7 h · + Checkpoint 1 · 2 h

**Branch:** `planning/sprint40-day5-diagonal` · **Base:** `abc82d30`.

### P3: the expanded-scope sentence (close rule C4)

> **At `abc82d30`, on the 140-candidate continuity corpus (re-based from 142 on 2026-10-19), Solve is 115/135 and Match 97/140; on the expanded scope of 149 (140 + 9 admitted by rule, Decision 2), Solve is 117/139 and Match 99/149. The +2 and +2 are scope additions, not recoveries.**

- Both figures come from `kpi_block.py --corpus continuity|current` at `abc82d30` (`CORPUS_RECORD.md` is the per-model record).
- **The Rolling-KPIs footnote is ¹⁰** (`PROJECT_PLAN.md`), in the S23–S25 form ("pipeline scope changed from X to Y", with rates stated relative to the new scope). It marks the S40 Translate, Solve and Match cells, and it says explicitly that the current corpus's **rates are not comparable** with the series: Match falls to 66.4% on 149, although no model regressed.

### P7: #1755, the diagonal-reference defect

- **Phase-0 gate first:** `a9f13e5d` (`ISSUE_1755` § *Phase 0: Acceptance Gate*; `check_phase0_doc.py` PASS). The `src/` landing is the following commit.
- **The layer was re-located by a call trace, before writing the gate.** Prep named `_sum_should_collapse`'s `len(...) != len(...)` early return.
  - Traced: it does return False here, but making it return True would only reach the full-collapse branch, whose `zip(..., strict=True)` cannot pair 1 binder with 2 positions.
  - **The derivative is lost in `_diff_sum`'s single-binder partial-match loop,** which symbolizes **one position per attempt** (`('i','i1')`, then `('i1','i')`) and so never matches `tsam(i,i)`.
  - Sprint 39 recorded three of four gates naming the wrong layer; this one was checked before the code was written.
- **The fix** (`_diff_sum_repeated_binder`, run only after every existing attempt returned zero): place the binder at **every** position it occupies, **only when the `wrt` values there are equal**, then substitute it back.

| criterion | result |
|---|---|
| fail-before at the layer | `Sum((i), Const(0.0))` → `Const(1.0)` on the diagonal |
| **positive control** | the off-diagonal `('i1','i2')` stays **0**, as do the three-position and mixed-concrete variants |
| scalar variant | the emit **is the hand-derived row** (`2*tsam(i,j) + nu_diag$(diagonal)`); PATH **MS 1 at 0.333** = NLP 0.3333 |
| reproducer | `diagsum` and `nu_diagsum` present and paired, `nu_diagsum` on the diagonal only, no `1 =E= 0` |
| #1737 | shape (a) `dd(i,i)` moves from **silently dropped** to **refused**. Pinned; #1737 untouched |
| leak gate | `make check-goldens` **alone**: **200 in-scope, all clean**, rc 0 with `--fail-on-unverified` (17:55 → 18:12Z). **Byte-identical corpus-wide** |
| `check-index-repeats` | P1 0 / 3,370; P2 11 = baseline |
| mutation controls (throwaway worktrees) | revert → 8 of 9 fail · drop equal-values → the positive control fails · exact spelling → the case test fails |

- **A vacuous test caught by the controls.** The first case-insensitivity test, `tsam(i,I)`, passed with the fix **reverted**. `main` already handled that two-position form by accident: #1111's free-index conversion treats `I` as a distinct free index. It was replaced with a three-position `w(i,I,i)`, which `main` and the exact-spelling mutant both get wrong, and the accidental form is kept as a pin.
- **Where the measurement differed from the prediction:**
  - **The indexed reproducer's row is not the hand-derived one.** AD is now right (1 for every `j`), but the stationarity row aggregates the cross-instance multipliers wrongly (`2·nu_diagsum(i1)` at `(i1,i1)`).
  - **That is a pre-existing, independent defect, filed as #1778.** A reproducer with no repeated binder is byte-identical on an untouched `main` and **solves to a wrong 0.375** against an NLP of 0.3333. It is latent in the corpus: 0 goldens carry the shape, and the positive control matches.
  - Its `nu_e(i)$(ord(i) = k)` guard looks like the phantom-IndexOffset family (#1381/#1714): a hypothesis.
- **A pinned reachability claim became live, as its own message anticipated.**
  - `test_pattern_c_alias_offset_gate.py` asserted that a diagonal reference *never* reaches Pattern-C B-3. Now that the reference differentiates, B-3 is consulted and **declines** (`None`), so the test asserts "reached and declined" and is renamed.
  - ⚠ A mutant showed #1741's guard is **not** the only decliner for that fixture, so the test claims only "B-3 declines". `ISSUE_1741` is updated.
- **Out of scope, unchanged:** #1776 (the equal-count sibling).

### Checkpoint 1 (end of day): GO

Run in a throwaway worktree at `7db9aa4c` (the P7 landing), with the raw corpus copied in. The run launches GAMS with `cwd` at that root, and `tricp` writes `cp.eps` there. 18:31 → 18:55Z. **Nothing was persisted.**

- **Scope first: the resolver's own MODEL count.** `--resolve-changed --since-commit bd2af6e9 --dry-run --json` reports **12** changed-golden models: airsp2, egypt, glider, jbearing, minsurf, robot, shale, srpchase, tfordy, torsion, tricp, turkey. These are the goldens Day 3 committed. No empty-selection error, so no `--allow-empty`: the run certifies these 12.
- **`--resolve-changed --since-commit bd2af6e9 --min-scope 12`: GO, rc 0.** **All 12 held their bucket.** 0 `backward`, 0 `missing`, `= same` on every row.
- **Plus the licensed re-run of the 11 cohort models** (PR workflows are demo-only): `run_full_test.py --model <id>` for each.
  - **All 11 reproduce their committed rows exactly**, on outcome, verdict, attribution, `license_edition` and objective (4 dp).
  - No other row of the worktree DB changed.
  - Every row is `licensed`.

### Gate

`make typecheck && make format && make lint && make test`, run alone: typecheck, format and lint clean; **5,590 passed**, 10 skipped (the usual 10), 0 `test_path_solver` skips, no `225*` process dirs.
- `make check-goldens` (the leak gate) is complete and clean, as above.
- `make check-index-repeats`: P1 0, P2 = baseline.
- `make check-doc-figures` is clean.
- `check_phase0_doc.py` PASS.
