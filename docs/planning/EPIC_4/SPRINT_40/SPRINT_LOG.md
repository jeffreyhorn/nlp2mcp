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
