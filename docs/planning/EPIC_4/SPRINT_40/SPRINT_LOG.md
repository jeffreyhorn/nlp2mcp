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
- **The fix** (`_diff_sum_repeated_binder`, run only after every existing attempt returned zero): place the binder at **every** position it occupies, **only when the `wrt` values there are equal**, then substitute it back. The result is the **whole** derivative: every distinct layout once, plus the summed remainder (PR #1779 review round 1).

| criterion | result |
|---|---|
| fail-before at the layer | `Sum((i), Const(0.0))` → `Const(1.0)` on the diagonal |
| **positive control** | the off-diagonal `('i1','i2')` stays **0**, as do the three-position and mixed-concrete variants |
| scalar variant | the emit **is the hand-derived row** (`2*tsam(i,j) + nu_diag$(diagonal)`); PATH **MS 1 at 0.333** = NLP 0.3333 |
| reproducer | `diagsum` and `nu_diagsum` present and paired, `nu_diagsum` on the diagonal only, no `1 =E= 0` |
| #1737 | shape (a) `dd(i,i)` moves from **silently dropped** to **refused**. Pinned; #1737 untouched |
| leak gate | `make check-goldens` **alone**: **200 in-scope, all clean**, rc 0 with `--fail-on-unverified` (17:55 → 18:12Z). **Byte-identical corpus-wide** |
| `check-index-repeats` | P1 0 / 3,370; P2 11 = baseline |
| mutation controls (throwaway worktrees) | revert → 12 of 13 fail · drop equal-values → the positive control fails · exact spelling → the case test fails · (after review round 1) drop the remainder / first layout only / no layout dedup → each fails its mixed-reference test |

- **A vacuous test caught by the controls.** The first case-insensitivity test, `tsam(i,I)`, passed with the fix **reverted**. `main` already handled that two-position form by accident: #1111's free-index conversion treats `I` as a distinct free index. It was replaced with a three-position `w(i,I,i)`, which `main` and the exact-spelling mutant both get wrong, and the accidental form is kept as a pin.
- **Where the measurement differed from the prediction:**
  - **The indexed reproducer's row is not the hand-derived one.** AD is now right (1 for every `j`), but the stationarity row aggregates the cross-instance multipliers wrongly (`2·nu_diagsum(i1)` at `(i1,i1)`).
  - **That is a pre-existing, independent defect, filed as #1778.** A reproducer with no repeated binder is byte-identical on an untouched `main` and **solves to a wrong 0.375** against an NLP of 0.3333. It is latent in the corpus: 0 goldens carry the shape, and the positive control matches.
  - Its `nu_e(i)$(ord(i) = k)` guard looks like the phantom-IndexOffset family (#1381/#1714): a hypothesis.
- **A pinned reachability claim became live, as its own message anticipated.**
  - `test_pattern_c_alias_offset_gate.py` asserted that a diagonal reference *never* reaches Pattern-C B-3. Now that the reference differentiates, B-3 is consulted and **declines** (`None`), so the test asserts "reached and declined" and is renamed.
  - ⚠ A mutant showed #1741's guard is **not** the only decliner for that fixture, so the test claims only "B-3 declines". `ISSUE_1741` is updated.
- **Out of scope, unchanged:** #1776 (the equal-count sibling).

### PR #1779 review round 1 (P7)

- **The helper returned a partial derivative for mixed references, and the review was right.** It returned the first layout's collapsed contribution and nothing else:
  - `sum(i, x(i,i) + x('i1','i1'))` gave **1, not 4**. `main` had given 3, so this was a regression in that shape;
  - `sum(i, w(i,i,'i1') + w('i1',i,i))` gave **1, not 2**.
- **Fixed:** every distinct layout counts once, plus the summed remainder (the caller's normal case), and the two parts are disjoint. Three value-checked regressions cover the two cases and a shared layout (no double count). **12 tests; 7 mutants, all caught.** The leak gate was re-run alone (below).
- **A pre-existing sibling, routed:** the #1086 loop before the helper returns its *first* non-zero attempt, so `sum(i, x(i,'i1') + x(i,i))` gives 1, not 2. That is unchanged from `main`, and filed as **#1780**: changing the loop needs its own Phase-0 gate.

### PR #1779 review round 2 (P7)

- **Layouts were keyed by spelling, but index matching is case-insensitive.** `sum(i, w(i,i,i) + w(i,I,i))` at `w('i1','i1','i1')` gave **4, not 2**. The two references made two keys, and each symbolic differentiation counted both.
  - The same input also left a coefficient `c(I)` **unsubstituted** in one layout.
- **Fixed:** the key uses the canonical binder spelling at the binder positions, and the original spellings of every reference sharing a key are **merged**, so substitution replaces `i` and `I` alike.
- **The regression** covers the plain case (2) and one with a coefficient under both spellings. The test's evaluator refuses an unsubstituted `c(i)` / `c(I)`, so the substitution cannot pass silently.
- **Mutants:** the previous revision fails it (4 ≠ 2); canonical keys without merged spellings fail it (`c(I)` left). **13 tests**; reverting the fix fails 12 of them. The leak gate was re-run alone (below).

### PR #1779 review round 3 (P7)

Two findings without threads, both confirmed at the AD level first:

- **Coefficient-only case variants.** Spellings came only from references to the differentiated variable, so `sum(i, c(I)*x(i,i))` left `c(I)`. In the two-layout case, one symbolic `c(I)` could not carry two bindings.
  - **Fixed:** `_binder_spellings` collects every spelling of the binder across the body and condition. A nested aggregation that re-binds the name is skipped; GAMS rejects that anyway (`$125`).
  - Now `c('i1')`, and `c('i1') + c('i2')` across two layouts.
- **Layout-specific conditions.** Every layout received the same symbolic `active(i)`.
  - **Fixed:** each layout's condition is substituted with **its own** binder value: `active('i1') + active('i2')`.
- **4 value-checked regressions; 16 tests; 3 new mutants, all caught.** The previous revision fails all three; a symbolic condition fails the condition test; reference-only spellings fail both coefficient tests.
- ⚠ **End-to-end, the condition is still lost one layer later, and this round does not fix that.** Two NLPs measured: a single layout with the binder in positions 3–4 (cond1), and the reviewer's two-layout case (cond2).
  - AD now returns `act('i1')` / `act('i2')` per instance.
  - The **stationarity** generalization then maps both back to `act(i)`, the variable's first domain position. So cond1's MCP still aborts (`e.nu_e` unmatched) and cond2's solves to **0.667 against 0.5**, **byte-identically before and after** this round.
  - Recorded on **#1778** as two more stationarity-layer reproducers, possibly the same root. Latent in the corpus.
  - The coefficient case solves correctly end to end (0.034 vs 0.0345), both before and after.

### PR #1779 review round 4 (P7)

- **The equal-values check compared raw strings, but `_indices_match` strips quotes and ignores case.** So `('i1','I1')` and `('i1',"'i1'")`, the same element in both coordinates, were treated as inconsistent, and `sum(i, x(i,i))` stayed at 0.
- **Fixed:** values are compared as `_indices_match` compares them, and the substitution keeps a spelling that passes the existing set-membership check (`x(i1,i1)`).
- **Regressions:** case- and quote-varied targets in both coordinate orders (4), plus varied off-diagonal controls (3). **23 tests.**
- **Mutants:** the previous revision and a raw-string comparison each fail the 4 varied tests; removing the check fails 7, including the off-diagonal controls.

### PR #1779 review round 5 (P7)

Two findings without threads, both reproduced first:

- **A body-level dollar condition hid the diagonal.** In `sum(i, x(i,i)$active(i))`, the loop produced `0$active('i1')`. `_is_structurally_zero` did not recognize a guarded zero, so the loop took it for a match and returned before #1755's fallback.
  - **Fixed in `_is_structurally_zero`** (`0$cond` is 0 whatever `cond` is), as suggested. Result: `1$active('i1')`.
  - ⚠ This touches every caller of `_is_structurally_zero` (5 sites, all in `derivative_rules.py`), not only #1755's. The leak gate below is therefore what decides that no golden moved.
- **A fully noncanonical target stayed at 0.** For `('I1','I1')` or `("'i1'","'i1'")`, no coordinate used the declared spelling, and membership is a raw lookup.
  - **Fixed:** `_declared_member_spelling` resolves the normalized target to the declared member through `resolve_set_members`, so the substitution writes `x(i1,i1)`.
- **Regressions:** fully noncanonical targets (2) with a nonlinear body, their off-diagonal controls (2), and the body condition, active and inactive. **28 tests.**
- **Mutants:** the previous revision fails all 3 new tests; no guarded-zero recognition fails the body-condition test; no declared-spelling lookup fails both noncanonical tests.

### PR #1779 review round 6 (P7)

Two findings without threads, both reproduced first:

- **A quotient body hid the diagonal.** `sum(i, x(i,i)/2)` gave 0, not 0.5. Each single-position attempt left `(2*0 - x*0)/2^2`, a quotient with a zero numerator, which the loop took for a match. The same happened with `x(i,i)/c(i)`.
  - **Fixed in `_is_structurally_zero`:** a quotient is zero when its numerator is (the denominator is non-zero wherever the expression is defined). This again reaches every caller, and the leak gate decides.
- **A quoted label spelled like the binder was counted.** With `Set i / i, i1, i2 /`, `sum(i, x(i,i) + x('i','i'))` at `x('i1','i1')` gave **2, not 1**. The parser keeps the label quoted (`"i"`), but index matching strips quotes, so the symbolic `(i,i)` target matched it.
  - **Fixed:** each layout is differentiated against a **fresh placeholder** for the binder, which no label in the expression can spell. The rest of the body is left intact.
- **Regressions:** both quotient forms, and the quoted label. **30 tests.** **Mutants:** the previous revision fails both; no quotient-zero recognition fails the quotient test; no fresh placeholder fails the quoted-label test.
- ⚠ **A cost regression, found by the leak gate and fixed.** The first gate run on this round was UNVERIFIED (198 of 200), with ferts and ganges timed out on a quiet machine.
  - Paired emits of ferts (`main` vs this branch, alternating order) were **byte-identical** but slower: 405 s vs 246 s, then 252 s vs 210 s.
  - `cProfile` attributed it: the helper runs on **1.39 M** calls in ferts (nearly every single-binder `_diff_sum`), and each call re-walked the body. That was **6.5%** of the profiled emit.
  - **Fixed:** an early return before any whole-expression walk when no reference repeats the binder, and the loop's already-computed reference list passed in instead of a second walk. The helper is now **1.6%**, and the emit is still byte-identical to the golden.
- ⚠ **Pre-existing and unchanged, recorded in the test:** a **target** element spelled like the binder (`x('i','i')` at `('i','i')`) cannot be told from the binder in the bare-string index representation. `main` returns the same wrong value, so this PR does not change it.

### PR #1779 review round 7 (P7)

- **A zero-valued nested sum hid the diagonal.** In `sum(i, x(i,i) + sum(k, c(k)))`, the inner sum's derivative `sum(k, 0)` was taken for a match, and the loop returned `0 + sum(k, 0)` instead of 1. The same happened with a nested variable sum, and with a sum-valued coefficient `sum(k, c(k)) * x(i,i)`.
- **Fixed in `_is_structurally_zero`:** a `Sum` whose body is structurally zero is zero over any domain. ⚠ **Not `Prod`:** a product over an empty domain is 1.
- **Regressions:** an independent inner sum, a nested variable sum, and a sum-valued coefficient. **33 tests.** The previous revision fails all 3.
- **Gate:** the first leak-gate run was **UNVERIFIED**, 196 of 200: ferts, ganges, gangesx and turkpow timed out, although the 1-min load was low at the start.
  - Paired emits (previous commit vs this one) were byte-identical, with **no cost regression**: turkpow 228 s vs 254 s, ferts 187 s vs 186 s. The 15-min load averages, 34 and 23, showed bursts of outside load that the 1-min check misses.
  - **The re-run waited for the 1- *and* 5-min averages to stay below 6 for 10 minutes. It was complete and clean** (23:44 → 00:10Z).
  - ⚠ **A vacuous assertion was caught by that control.** The coefficient test first checked only that `sum(k, c(k))` *appears*, and it passed on the previous revision, whose wrong output contains it multiplied by 0. It now asserts the coefficient multiplied by the diagonal's 1.

### PR #1779 review round 8 (P7)

- **The round-6 placeholder was fresh only within the expression.** Two collisions, both reproduced:
  - **A target label:** with `i = {i1, i2, i__binder1755}`, the target `w('i1','i1','i__binder1755')` matched the renamed `w(i,i,i)`, giving 1 instead of 0.
  - **Another set's member:** with `k = {i__binder1755}`, the inner `sum(k, x(k,k))` took the placeholder for a member of `k`, giving 2 instead of 1.
- **Fixed:** the placeholder is also reserved against the normalized target labels and against every set or alias name and declared member in the model. That runs only when a repeated-binder layout exists, so it stays off the common path.
- **Regressions:** both collisions. **35 tests.** The previous revision fails both; reserving target labels alone fails the member case, as the review predicted.

### PR #1779 review round 9 (P7): the shared collapse machinery, by owner decision

Two findings, both **pre-existing in the shared collapse path**: measured on `main`, the single-position collapse had both. The reviewer asked for human validation. **The owner chose to fix the shared machinery in this PR** (option 3 of 3 offered).

- **`card()` operands.** `_apply_index_substitution` turned `card(s)` into `card(i1)`, so the subset's cardinality became the parent's.
  - **Fixed:** a `card()` used as a **value** keeps its set operand. `ord()` and all other calls are still substituted.
  - ⚠ **Except inside an `IndexOffset`'s offset** (`card_operands=True`): there `card(t) - ord(t)` is a relative position, and `card` must follow `ord` onto the same set (#1178's behaviour).
  - The first version preserved `card` everywhere. The resolver caught otpop's `p(t + (card(t) - ord(t)))` becoming `p(tt + (card(t) - ord(tt)))`: the wrong element, and the cold match lost (`model_optimal` → `model_optimal_presolve`). With the offset exception, otpop's emit is **byte-identical** to its golden.
- **Dynamic-subset membership.** A collapsed contribution over a runtime-assigned subset (`ii(i) = yes$…`, no static members) dropped the restriction. AD resolves the binder to the parent's elements (#723), so `sum(ii, x(ii,ii))` gave an unguarded 1 at an excluded cell.
  - **Fixed:** `_diff_sum` attaches `ii(ii)` to the **body** as a dollar condition for every collapse path. The normal, non-collapsing case uses the original sum. Static subsets need no guard.
  - ⚠ The first version ANDed the guard into the sum's **condition**. The stationarity builder lifts that condition into the row and `.fx` guards and does not map the sum index inside an `and`, so srkandw's emit had an uncontrolled `sn` (`$149`). **The resolver caught it as BACKWARD (match → `path_syntax_error`).** On the body, srkandw solves to 2613 = NLP.
- **End-to-end, both measured with GAMS (NLP vs MCP):**
  - a runtime subset with a full-domain objective: NLP 1.0; `main` **0.000**; this branch **1.000**, and the row carries `1$(ii(i)) * nu_e`;
  - a `card(s)` coefficient: NLP 0.125; `main` **0.000**; this branch **0.125** with `nu_e = -0.25`.
  - ⚠ The objective alone does not discriminate the `card` fix: the model is symmetric, so the wrong coefficient (parent `card(i)` = 3) cancels from the primal. The test checks the **row** and `nu_e` (−0.1667 with 3), and fails with the fix reverted.
- **Corpus (examined, not refreshed blindly):** the leak gate showed **19 drifted goldens over 15 models**, all small guard additions. Each drifted model was regenerated and re-solved by the resolver (`--resolve-changed --min-scope 15`, throwaway worktree): **GO, 14 hold their bucket.**
  - The 15th, **abel**, moved mismatch → match. **That is a stale DB row, not this change:** the *committed* golden also solves to 225.195 = NLP today; the row was written 2026-04-21 at 158.15. **It is not booked as a fix.** A persisted run will correct it.
  - The 19 goldens are committed. `check-index-repeats` is unchanged.
- **Regressions:** `card` preserved (diagonal and single-position), `ord` still substituted, `card` inside an offset following `ord`, a dynamic subset active and inactive, a static subset unguarded, and two GAMS solves. **42 + 2 tests.**
- **Mutants:** reverting the `card` fix fails the `card` tests and the GAMS `nu_e` check; disabling the guard fails both subset tests and the GAMS solve; preserving `card` inside offsets fails the offset test.

### PR #1779 review round 10 (P7)

- **A runtime-subset guard lost its coordinate in stationarity.** With `Alias(i,j)`, `ii(i) = {i1}`, `jj(i) = {i2}` and objective `sum((ii,jj), sqr(x(ii,jj) - 1)) + sum((i,j), sqr(x(i,j)))`:
  - NLP **0.5**; this branch **1.000** (row guard `ii(i) and jj(i)`, never true, so the gradient at `(i1,i2)` was zeroed); `main` **1.250** (no guard at all).
- **Mechanism (instrumented):** the guard was written over the binder, so a collapse made it concrete. Stationarity's element-to-set map is right for the instance `(i1,i2)` (`i2 → j`), but a DIAGONAL instance put `i1` in both coordinates, and the generalized row took `jj('i1') → jj(i)`.
- **Fixed:** when every reference to the differentiated variable places the binder at ONE position, the guard is written over that position's **declared domain symbol** (`ii(i) and jj(j)`), which stationarity leaves alone. Otherwise, or if that symbol is a binder of the same sum, it stays on the binder.
  - The aliased model now solves to **0.500** = NLP, with row guard `ii(i) and jj(j)`.
- **The corpus had it:** round 9's committed cesam2 golden carried `$(ii(i) and ii(i))` on its objective term. It is now `$(ii(i) and ii(j))`; the leak gate's only drift, re-solved by the resolver: **GO**, match held.
- **Regression:** the aliased end-to-end solve (row guard and objective). A mutant that writes the guard on the binder again fails it.

### PR #1779 review round 11 (P7)

- **An enclosing sum captured the guard's coordinate.** In `sum(i, sum(ii, x(ii,i)))`, the inner guard was written over the declared coordinate `i`, which is also the OUTER binder. The outer collapse substituted it with the second coordinate: `ii('i2')` at `x('i1','i2')`, so 0 instead of 1.
- **Fixed:** `_diff_sum` keeps a stack of enclosing binders (`_ENCLOSING_BINDERS`), and the guard falls back to the binder when ANY enclosing sum binds its declared symbol. It then collapses to the right element first: `ii('i1')`, active, and `ii('i2')` at `(i2,i2)`, excluded. A separate channel is used, not `bound_indices`, which also drives alias matching.
- **Regressions:** nested against flat, active and excluded. The previous revision fails the active case; the excluded one cannot discriminate.
- **Leak gate:** clean, 200 goldens with 0 drift, so the fix changes no committed emit.
- **`test_positional_domain_sites.py`'s catalogue** pinned two sites by the function name `_diff_sum`. The body moved intact into `_diff_sum_impl` (`_diff_sum` is now the binder-stack wrapper), so the catalogue was repointed with the same anchors.
- ⚠ **End to end this shape is still wrong, for a pre-existing reason:** stationarity generalizes the row to `x(j,j)` (`main`: `2*x(j,j) =E= 0`, MCP 2.000; here 1.500; NLP 1.0). This is the same aliased-coordinate mapping family; added to **#1778**.

### PR #1779 review round 12 (P7)

- **A FREE index captured the guard, with no enclosing sum.** In `sum(ii, x(ii,i))` with a symbolic free `i` (the equation's own index), #1111's free-index recovery substituted the guard's declared `i` from the second coordinate: `ii('i2')` at `x('i1','i2')`, 0 instead of 1. Round 11's flat control used a literal second index, so it could not see this.
- **Fixed:** the declared symbol is used only if NOTHING else in the body uses that name. Every name in the body now counts as occupied, as do the enclosing binders; on any clash the guard stays on the binder. The round-10 aliased-coordinate solve still passes, because its body uses only binder names.
- **Regression:** a symbolic free index, active and excluded. The previous revision fails the active case.

### PR #1779 review round 13 (P7)

Three findings, each reproduced end to end against the NLP (`HEAD` = round 12):

| case | NLP | `HEAD` | fixed |
|---|---|---|---|
| initialized-then-pruned subset `Set s(i) / i1, i2 /; s(i) = yes$(ord(i) = 1);` | 1.0 | **2.000** | **1.000** |
| disjoint runtime subsets in a partial collapse, `sum((ii,jj), x(ii)*x(jj))` | 0.667 | **1.000** | **0.667** |
| the aliased case with a `card(j)` coefficient | 0.667 | 0.667, but one row branch carried `jj(i)` | 0.667, row `ii(i) and jj(j)` |

- **Runtime mutability:** declared members do not make a set static. A set is now guarded if it has no static members (#723) **or** it is the target of any execution-time set assignment (`model_ir.set_assignments`).
  - ⚠ Not done: widening member *resolution* for a reassigned set (to cover elements added at runtime). That changes instance enumeration corpus-wide and is a separate change.
- **Promotion requires a consistent binder position:** EVERY reference to the variable must hold the binder at exactly one position, and the same one. Otherwise the guard stays on the binder.
- **Occupancy follows the substitution rules:** `_capturable_names` skips a preserved `card()` operand, except inside an IndexOffset's offset.
- **Regressions:** the three end-to-end solves. Each mutant (no assignment check; a position union; occupancy counting `card` operands) fails exactly its own test.
- **Leak gate:** clean, 200 goldens with **0 drift**.

### PR #1779 review round 14 (P7)

Two findings without threads, both reproduced:

- **A quoted label occupied a coordinate.** The occupancy scan stripped quotes, but substitution matches names exactly and never rewrites the quoted label `"j"`. So `p('j')` marked the coordinate `j` as occupied, and the `jj` guard fell back to its binder. On the aliased model, `HEAD`'s row had a `jj(i)` branch.
  - **Fixed:** `_capturable_names` keeps quotes. The row is now `(2*(x(i,j) - p("j")))$(ii(i) and jj(j)) + 2*x(i,j)`.
  - ⚠ That MCP cannot be solved today, for a **separate pre-existing emitter defect, filed as #1781:** the data line is emitted `p(j) = 1;`, so the label is read as the alias (`$171`). Identical on `main`. The regression asserts the row only.
- **A renamed remaining binder captured a promoted guard.** In `sum((ii,k), x(ii)*p(k))` with `Alias(ii,k)`, `Alias(i,k__)` and `x(k__)`, the promoted guard is `ii(k__)`. `_partial_collapse_sum` renamed the surviving binder `k` to `k__`, capturing it (1 instead of 0 at `x('b')`).
  - **Fixed:** the rename also avoids every name the body or condition uses, so `k` becomes `k___`.
- **Regressions:** the quoted label (AD and emitted row) and the rename capture. The previous revision fails all 3; quote-stripping fails the two quoted tests; dropping the in-use check fails the rename test.

### PR #1779 review round 15 (P7)

Two findings, both checked as **values** with a test-side evaluator that expands `Sum`/`Prod` over the IR's sets:

| case | correct | previous revision | fixed |
|---|---|---|---|
| `prod((i,k), sum(ii, x(ii)))` at `x('a') = 2`, runtime `ii = {a}` (`= x(a)^4`) | 32 | **16** | **32** |
| round-14 fixture with `i = {a, k___}`, `sqr(x(ii))*p(k)` at `x('k___') = 3` | 12 | **8** | **12** |

- **An enclosing `Prod` captured the guard.** Only `Sum` binders were tracked. The product's logarithmic-derivative sum re-binds `i`, so the promoted `ii(i)` tested the product's iterate.
  - **Fixed:** `_diff_prod` is a thin wrapper pushing its binders onto `_ENCLOSING_BINDERS`, the same channel as `_diff_sum` (not `bound_indices`). The guard is now `ii('a')`.
- **A rename captured a concrete target label.** Round 14's rename avoided names in the body but not the target: `k` became `k___`, the label being differentiated, and the concrete `x(k___)` inside the surviving sum turned into the binder.
  - **Fixed:** the rename also reserves the normalized target labels, including IndexOffset bases (`k` → `k____`).
- **Regressions:** both, value-checked. The previous revision gives exactly the reviewer's 16 and 8.

### PR #1779 review round 16 (P7)

- **The rename could take an existing model set or alias name.** Adding `Set k____(i) / a /` to the round-15 fixture made `k` become `k____`. The emitter accepts an existing set as the renamed binder's alias, so the surviving sum iterated `{a}`: 6 instead of 12.
- **Fixed:** the rename also reserves every model set and alias name, case-insensitively (`k` → `k_____`). AD-generated aliases (`j__` …) are not in `model_ir` during AD, so this cannot reserve them.
- **Regressions:** a set collision and a (case-differing) alias collision, value-checked at 12. The previous revision fails both.
  - The test evaluator now resolves a generated binder by stripping ALL trailing underscores. Stripping one at a time stopped at the colliding set.

### PR #1779 review round 17 (P7)

- **The rename could take a parameter's name.** GAMS has one identifier namespace. With `Parameter k___(i)`, the surviving binder became `k___`, and the emitter declared `Alias(ii,k___)` over the parameter, so the MCP could not compile.
- **Fixed:** the rename reserves EVERY model identifier, case-insensitively: sets, aliases, parameters, variables, equations and declared models.
- **Regression:** a parameter-name collision, value-checked at 12. The previous revision fails it (its surviving sum binds `k___`).

### Checkpoint 1 (end of day): GO

Run in a throwaway worktree at `7db9aa4c` (the P7 landing), with the raw corpus copied in. The run launches GAMS with `cwd` at that root, and `tricp` writes `cp.eps` there. 18:31 → 18:55Z. **Nothing was persisted.**

- **Scope first: the resolver's own MODEL count.** `--resolve-changed --since-commit bd2af6e9 --dry-run --json` reports **12** changed-golden models: airsp2, egypt, glider, jbearing, minsurf, robot, shale, srpchase, tfordy, torsion, tricp, turkey. These are the goldens Day 3 committed. No empty-selection error, so no `--allow-empty`: the run certifies these 12.
- **`--resolve-changed --since-commit bd2af6e9 --min-scope 12`: GO, rc 0.** **All 12 held their bucket.** 0 `backward`, 0 `missing`, `= same` on every row.
- **Plus the licensed re-run of the 11 cohort models** (PR workflows are demo-only): `run_full_test.py --model <id>` for each.
  - **All 11 reproduce their committed rows exactly**, on outcome, verdict, attribution, `license_edition` and objective (4 dp).
  - No other row of the worktree DB changed.
  - Every row is `licensed`.

### Gate

`make typecheck && make format && make lint && make test`, run alone: typecheck, format and lint clean; **5,590 passed** at the first push and **5,593** after review round 1, **5,594** after round 2, **5,597** after round 3, **5,604** after round 4, **5,609** after round 5, **5,611** after round 6, **5,614** after round 7, **5,616** after round 8, **5,625** after round 9, **5,626** after round 10, **5,628** after round 11, **5,630** after round 12, **5,633** after round 13, **5,636** after round 14, **5,638** after round 15, **5,640** after round 16 and **5,641** after round 17, 10 skipped (the usual 10), 0 `test_path_solver` skips, no `225*` process dirs.
- `make check-goldens` (the leak gate) is complete and clean: 200 in-scope, byte-identical, at the landing and **re-run alone after review rounds 1 and 2**. ⚠ Round 2's first two runs were **UNVERIFIED**, 195 of 200 with 5 timeouts: external machine load reached a 15-min average ≈ 100, which my runs did not cause. `--fail-on-unverified` refused both, as P10c intends. The third run, started only after five consecutive quiet minutes (1-min load < 8), was **complete and clean** (18:03 → 18:33Z).
- `make check-index-repeats`: P1 0, P2 = baseline.
- `make check-doc-figures` is clean.
- `check_phase0_doc.py` PASS.

---

## Day 6 — 2026-10-24 · P7: #1755 finish · 3 h · + P4: turkpow, Class A · 7 h

**Branch:** `planning/sprint40-day6-turkpow` · **Base:** `3539f994` (PR #1779, 17 review rounds). The calendar runs about two days behind the plan's dates.

### P7: #1755 finish — landed (C2)

- **The three gates hold:**
  - the Phase-0 doc (`ISSUE_1755`, with layer and positive control);
  - an unqualified, uncontended leak-gate pass: complete and clean through every review round, the last one 0 drift;
  - **in `main`** at `3539f994`.
- **Determinism ×3** (`PYTHONHASHSEED` 0 / 1 / 42) on all **15** models whose goldens #1779's shared-machinery changes touched: **1 distinct hash each, byte-identical to the committed golden.**
  - turkpow, ganges and gangesx ran in a `main` worktree.
  - ⚠ The first run used the repo's working tree, and P4's edits landed mid-run. It was stopped and those three re-run against `main`, so every figure is `main`'s.

### P4: turkpow, Class A — #1782

- **Phase-0 gate first:** `819d7850` (`ISSUE_1782`; `check_phase0_doc.py` PASS).
- **Fail-before reproduced:** `Alias(t,v)`, `z(v,t)`, `e(t).. sum(v$s(t,v), c(v,t)*z(v,t))` emits `sum(t__kkt1, c(v,t__kkt1)*1$(s(t__kkt1,t__kkt1))*nu_e(v))`. MCP **0.045** vs NLP **0.0318**.
- **The positive control needed distinct LABELS, not just distinct sets.** My first control reused `t1*t3` for both sets, which reintroduced the element-to-set ambiguity: the emit was garbled and the MCP did not solve. With `v / v1*v3 /` it emits the hand-derived row and solves to 0.026 = NLP.
- **The layer, refined by measurement.** The pre-trace named the alias ChainMap layer. Instrumented, the `{'v': 't'}` remap is a CONSEQUENCE: two matchers pair the eq index with a variable position by **alias root**, and both take position 0 (`v`):
  - `_compute_index_offset_key`'s canonical pass, which leaves `t` "unmatched", hence `nu_e(v)`;
  - `_match_subset_domain`'s same-position preference, which returns `{t: v}`, hence the minted `t__kkt1` sum.
- **The fix:** an exact-name preference in each matcher. **Necessity measured:** the alias-layer change I tried first was not needed and is dropped; removing either matcher fix breaks the fixture.
- **Results:** the fixture emits `c(v,t)*1$(s(t,v))*nu_e(t)` and solves to **0.032** = NLP; the positive control is byte-identical.
  - **P2: 11 → 9.** turkpow's two minted repeats are gone; `--update-baseline` in the same commit.
- **Corpus:** 5 goldens over 3 models drifted (turkpow, sambal, qsambal); the resolver gives **GO, all held**.
  - ⚠ **The pre-trace's positive control was wrong.** sambal's "correct" minted emit had the same defect (`nu_cbal(i)` summed over `i__kkt1`). The new emit is the hand-derived `−1$(xb(i,j)) * nu_cbal(j)`.
  - sambal and qsambal keep their presolve match; their cold solves stay wrong for other reasons (1028 → 781, NLP 3.97).
- **Mutation controls:** `main` fails 4 tests; no offset-key pass, 3; no subset-domain preference, 4. The positive control passes in all.
- **Bounded, carried to Day 7: turkpow's third violation `vs(v,v)`** (`stat_ht`). There the eq index `t` has NO variable counterpart, and the canonical pass pairs it with its alias `v`. It needs a new discriminator, so it is not quick. It touches #1778's family: freej2 moves 0.375 → 0.360, NLP 0.3333, changed but not fixed. **#1778 stays open, tracked with it.**

### PR #1783 review round 1 (P4)

- **The declared-NAME preference was a heuristic, and the review found where it is wrong.** An equation index binds the variable position its REFERENCE occupies, which need not be the position with its name:
  - **reversed equal-arity domain**, `e(j,i).. x(j,i)` with `x(i,j)`: the name preference emitted `nu_e(j,i)`, with wrong multiplier values (−12 vs −16 at `(i1,i2)`). The objective cannot show it, because the primal is pinned;
  - **fixed coordinate**, `e(t).. z(t,'t1')` with `z(v,t)`: `t` binds position 0. The name preference broke it outright: the MCP did not solve, where `main` and the NLP give 14.0.
- **Fixed:** the binding is read from the equation body. `_eq_index_ref_binding` binds an equation index only where it occupies exactly ONE position across every reference to the variable. Both matchers use that binding first and otherwise fall back to `main`'s logic (canonical, root, same-position).
  - The #1782 fixture keeps its hand-derived row.
  - Fixed-coordinate and transposed-sum references solve to NLP (14.0, 0.0201).
  - The reversed domain is back to `nu_e(i,j)` with `nu_e(i1,i2) = −16`.
- **Mutation controls:** the name heuristic fails exactly the review's regressions (reversed, fixed coordinate, its solve, the multiplier values); `main` fails the original fixture.
- **Corpus:** one more golden drifted, **spatequ**, by one line: its multiplier declaration `nu_DX(r,c)` became `nu_DX(rr,c)`. In `DX(r,c).. sum(rr, X(rr,r,c))` the equation index `r` binds `X`'s position 1, declared `rr`, an alias of `r`. Same set, no other line changes, and the resolver holds the bucket. The P2 ratchet stays at 9.

### PR #1783 review round 2 (P4)

- **The review asked for a strict rule:** bind an equation index only at the SAME single position in EVERY reference. My first revision took the union, so a reference independent of the index (a fixed cell) could not veto the binding.
- **I first argued to keep the union, then measured a second shape. The second shape refuted it:**

  | version | `e(t).. z('t1',t) + z('t1','t1')` (NLP 8.75) | `e(t).. 2*z('t3',t) - z('t2','t4')` (NLP 7.5) |
  |---|---|---|
  | `main` | fails | fails |
  | union (round 1) | 8.750 ✓ | **37.75: a silent wrong answer** |
  | strict (round 2) | fails | fails |

  The union's success on the first shape was the offset grouping happening to line up. On the second, the fixed cell took the bound reference's coefficient.
- **Fixed as reviewed:** the strict rule. It never infers a binding from a reference that does not involve the index, and it matches `main` on both shapes, turning the silent wrong answer back into a visible failure.
- **Mixed bound + independent references are broken on every version** (the fixed cell needs `sum(t', coef·nu_e(t'))`). Both reproducers are on **#1778**, recorded as known failures, not asserted. The general fix goes with turkpow's `stat_ht` (Day 7).
- **Regression:** the binding unit test covers consistent (`{0: 1}`), mixed, inconsistent and repeated-in-one-reference cases.

### PR #1783 review round 3 (P4)

- **The binding was applied twice.** On `Alias(i,j,k)`, `z(i,j,k)`, `e(i,j).. z('a',i,j)` the dimension-mismatch branch already built `nu_e(j,k)`; `_match_subset_domain` derived the rename `{i: j, j: k}` from the same binding, and the term rewrite made it `nu_e(k,k)`. The MCP did not solve (NLP 156). `main` emits garbled offset terms there and also fails.
- **Fixed:** in `_match_subset_domain` the binding only suppresses a rename (it is accepted only when the bound position carries the mult index's own name) and never creates one. The emit is `nu_e(j,k)$(sameas(i,'a'))`, solving to 156.
- **Regressions:** an emitted-row unit test, a "never creates a rename" unit test, and a validation solve. Dropping the name check fails all three.
- **Corpus:** spatequ's round-1 re-spelling `nu_DX(rr,c)` is undone; its golden is byte-identical to `main` again (that rename came from the binding). The resolver holds the bucket. The other goldens and P2 = 9 are unchanged.

### Gate

`make typecheck && make format && make lint && make test`: typecheck, format and lint clean; **5,646 passed** at the first push, **5,652** after review round 1, **5,653** after round 2 and **5,656** after round 3, 10 skipped, no `225*` dirs.
- `make check-index-repeats`: P1 0 / 3,370; **P2 9 = baseline** (from 11).
- The leak gate is complete; every drifted golden was re-solved (GO).
- `check_phase0_doc.py` PASS.

## Day 7 — 2026-10-26 · P4: land turkpow, start egypt and shale · 5 h · + P8: the structural pins become behavioural · 5 h

**Branch:** `planning/sprint40-day7-classa` · **Base:** `500ffa1f` (PR #1783).

### P4: turkpow's `stat_ht` and shale: the Pattern C binder (#1782)

- **Phase-0 gate first:** `c33757ef`. It is a second gate section in `ISSUE_1782`, and `check_phase0_doc.py` passes.
- **The layer, measured.** `pr(t).. sum(mt, … sum(v$vs(t,v), ht(mt,v)))` is a **Pattern C** shape, and the gate fires (binder `v`, eq index `t`).
  - Day 6's carry-over guess, a "position whose value IS the eq index" discriminator in the matchers, is not the layer. An "absent from every reference" pass in `_compute_index_offset_key` left the row byte-identical, and was dropped.
  - The swap (`_apply_pattern_c_swap_to_term`) exchanged the binder with the **eq index**. That pair is right only under launch's naming, where the variable is declared over the eq index's name.
  - It fired only on an all-zero offset key, so a dimension-mismatch key `(999, 0)` never reached it.
- **The fix (`src/kkt/stationarity.py`; ⚠ parts 1–2 and the exchange itself are REPLACED in PR #1788 review round 2, see there):** the swap pairs the binder with **the variable position it occupies**, `_binder_var_position` (the same single position in every reference). It applies only when the eq index is absent from every reference to the variable (`_index_absent_from_var_refs`). Four parts, each necessary (measured by mutation):
  1. **A binder named like a variable position is renamed first,** to an alias of the same set that neither the variable nor the multiplier uses (an existing alias, else a fresh `__kkt` one). The eq index itself is not safe: the equal-arity path's eq→var rename would catch it.
  2. **A self-mapping for the renamed binder in the element map,** keeping the map's type. A `ParamRef` index absent from the map is sent to the declared domain's name, so turkpow's PARAMETER `vs(t,v)` turned `t__kkt1` back into `v`: `vs("t__kkt1","t__kkt1")`, quoted.
  3. **The gate admits a subset ↔ parent pair** (shale's `t(tf)` with binder `tf`) **and the related binder of a multi-index sum** (shale's `acap`: `sum((m,tf)$ts(t,tf), …)`, where the first binder `m` is unrelated). Both only on the binder-position terms, never through the legacy offset-0 swap that #1398 restricted (`binder_swap_only`).
  4. **The #1162 offset substitution is skipped where the swap applies.** The gate requires a body with no IndexOffset on the variable's sets, so the eq label's distance from the representative is the sum's iteration. Without the skip, shale's PARAMETER `ts(t,tf)` became `ts(tf+1,tf)`.
- ⚠ **Set-valued fixtures hid two of the four.** `vs` and `ts` are PARAMETERS in turkpow and shale. A `SetMembershipTest`'s symbols are rewritten by neither the declared-domain mapping nor the offset substitution, so my first fixtures passed while the corpus emit was wrong. Every fixture whose guard is a parameter in the source now uses a parameter.
- **Fixtures, each solved against its NLP optimum:**

  | shape | before | after | NLP |
  |---|---|---|---|
  | binder named like the variable's position, equal arity | no solve (`vs(t,t)`, `t` uncontrolled) | 7.680 | 7.68 |
  | turkpow `ht` (dim mismatch, subset `t(te)`, dynamic `mt`, PARAMETER `vs`) | `vs(v,v)` (simpler variant: 2.0 vs 1.536) | 0.0944 | 0.0944 |
  | turkpow `zh` (`sum(bp$bs(bp,b), zh(m,bp,t))`) | **558** (silent) | 112.264 | 112.264 |
  | shale `cpu` (subset ↔ parent) | **11.545** (silent) | 9.9375 | 9.9375 |
  | shale `acap` (related binder second) | **180** (silent) | 16.685 | 16.6848 |
  | shale `acap`, PARAMETER `ts`, `t` missing the first element | 25.618 (with the offset substitution) | 11.254 | 11.2545 |
  | **positive control:** launch shape (`h(t)`) | 7.680 | 7.680, byte-identical row | 7.68 |

- **Mutation controls:** on `main`, every new P4 test fails except the two launch-shape controls. Each part removed alone fails its own tests:
  - no binder rename: 4;
  - no absence gate: Day 6's `#1782` fixture (2), the `ao`/`zt` shape where the eq index IS in the reference;
  - no self-mapping: turkpow `ht`;
  - no related-binder admission: shale `cpu` and `acap`.
- **egypt is not this shape** (`tranc(rp,rp)`). Its two references hold the eq index at different positions (`trans(cf,rp,r) − trans(cf,r,rp)`), so the binder has no single position and the change leaves it byte-identical. It needs per-reference grouping (entries keyed by which variable position the eq label occupies, off-diagonal representatives). A 15-line fixture reproduces it. **Filed as #1787 with tfordy's `stat_v` (below) and carried to Day 8.**

- **P2: 9 → 6** (the plan's ≤ 6), with `--update-baseline` in this commit. turkpow's `vs(v,v)` and shale's `ts(tf,tf)` (golden + presolve) are gone. The remaining 6 are dinam's `ts2(te,te)`, egypt ×2 (#1787, Day 8), gussrisk, and nonsharp ×2 (a refused MINLP; regeneration cannot move it).
- **Corpus:** the leak gate is complete (200 in-scope, no timeouts). 6 goldens over 4 models drifted, and every one was re-solved by `--resolve-changed`:
  - **turkpow** `path_syntax_error` = same. `stat_ht` is the hand-derived `sum(t__kkt1, … vs(t__kkt1,v) … lam_pr(t__kkt1))`, and the `lam_db` terms of `stat_zh` / `stat_zt` are `sum(bp, bs(b,bp) * lam_db(bp,t))`. `nu_ao(t)` (Day 6) is untouched.
  - **shale** `model_infeasible` = same. The `cpu` coupling is restored to Task 10's hand-derived `sum(t$ts(t,tf), …)`. `acap`'s eight phantom `nu_acap(tf±k)$(ord(m) = k)` terms are one `sum(tfp, …)`. **Still MS 5, as Task 10 predicted** (necessary, not sufficient); the candidate underlying defect is routed as #1786.
  - **dinam** `path_syntax_error` = same. `stat_em`'s `ts(t,tep)` / `zmi(t,te)` and `stat_v(jd,te)`'s `ts2(te,te) * lam_cap(jd,te)` are now `sum(tep, ts2(tep,te) * lam_cap(jd,tep))`, the same Pattern C correction.
  - ⛔ **tfordy BACKWARD: `model_optimal_presolve` + match → `model_infeasible`. The resolver said NO-GO; the owner decided to land it, recorded and routed.**
    - The changed row is the CORRECT one. `ainvc(t).. phik(t) =e= sgm*sum(tp$avl(t,tp), sum(m, nu(m)*h(m,tp)))` gives `sum(tp, avl(tp,t)*nu_ainvc(tp))`; the old row was #1307's `sum(tp, avl(t,tp))*nu_ainvc(t)`.
    - **`main`'s tfordy emit is already Case B:** the KKT-residual harness gives `stat_w` rel 1.27 and `stat_v` rel 1.0 at the NLP point, identical on both versions. So the committed match rested on the presolve warm start, and the corrected row changes PATH's path.
    - The defect underneath is egypt's two-reference shape (`pfs`'s `v(s,k,t,te)` and `v(s,k,tp,t)`), plus a collapsed `yv(t,t,…)`. Both are routed as **#1787**, the Day 8 target.
    - tfordy is not in `floor_provenance.json`, so **the floor is unaffected. When a persisted run lands it, Match moves −1**; report it as exposed by a correct row, not as a regression of a sound match.
- **Gate:** `make typecheck && make format && make lint && make test`: clean; **5,676 passed** at the first push and **5,680** after review round 1, 10 skipped, no `225*` dirs. `make check-index-repeats`: P1 0 / 3,370, P2 6 = baseline. `check_phase0_doc.py` PASS.

### PR #1788 review round 1 (P4)

- **The binder ↔ position exchange corrupted a bound coefficient.** dinam's `mb(i,t).. es(i)*sum(tep$ts(t,tep), zmi(t,tep)*em(tep))` against `em(te)` arrives with the eq coordinate already its own summed index (`lam_mb(i,t)`), not spelled as the variable's position. Exchanging `tep` ↔ `te` turned the bound `zmi(t,te)` into `zmi(t,tep)` and kept a spurious `sum(tep, …)`. My first push shipped that in dinam's golden (path_syntax_error either way, so the resolver could not see it). On a fixture it is a silent wrong answer: MCP 11.779 vs NLP 10.5238.
  - **Fixed:** `_apply_binder_position_swap` reads how the multiplier spells the eq coordinate. Launch's form (the eq coordinate is spelled as the position) keeps the exchange. Otherwise the binder is substituted by the position and its outer sum dropped.
  - dinam's `stat_em` is now the hand-derived `sum((i,t), es(i)*zmi(t,te)*ts(t,te)*lam_mb(i,t))`. The fixture solves to 10.524.
- **The renamed binder could capture a coefficient's own sum binder.** With `Alias(t,v,w)` and `sum(w, a(w))` in the coefficient, the rename picked `w`, and the swap turned the inner `a(w)` into `a(v)` (MCP 1.600 vs NLP 1.2288).
  - **Fixed:** the rename also reserves every index name in the derivative, free or bound (`_index_names_in`). It picks `t__kkt1`, and the fixture solves to 1.229.
- **Regressions:** each case has an emitted-row unit test and a validation solve. Reverting either fix fails exactly its own test.
- **Corpus:** dinam drifted by −11 B and holds its bucket (resolver GO). The other in-scope goldens are clean. ferts, ganges and turkpow timed out under load (unverified); re-run alone with `--fail-on-unverified`, all three are clean, so the gate is complete.
- **CI: `PR19 emit solve validation` failed in its `Post Set up Python 3.12` step** after every real step had passed. `ubuntu-latest` rolled from 24.04 to 26.04, and setup-python's cache key includes the OS version, so the cache missed. This job never pip-installs, so `~/.cache/pip` did not exist and the post-job save errored. **Fixed:** `cache: "pip"` is removed from that workflow. The other three workflows with a pip cache (`ci`, `nightly`, `gamslib-regression`) do `pip install`, so they are not exposed.

### PR #1788 review round 2 (P4): no exchange at all

- **The exchange is unsound in launch's own form.** Once re-symbolised, the eq coordinate and the variable's coordinate are BOTH spelled as the position name, so a whole-term exchange moves row-bound factors with the multiplier:
  - a coefficient, `a(v)` → `a(t__kkt1)` (MCP 1.999 vs NLP 1.8655);
  - a nonlinear derivative factor, `2*h(v)` → `2*h(t__kkt1)` (13.617 vs 8.9208);
  - and, as it turned out, `main`'s launch swap too, for any non-unit coefficient (`a(v)` for `a(t)` under launch's naming). launch itself has unit coefficients, so its golden is unaffected.
  - Separately, the equation condition was attached after re-symbolisation, so its own binder `w` was not reserved, and `sum(w, a(w))` became `sum(w__, a(v))` (no solve).
- **Replaced by a rewrite BEFORE re-symbolisation**, where the two coordinates are still apart:
  - **the representative** is chosen so that its eq label at the pattern's eq position is not among the variable instance's labels;
  - **the symbolic binder** becomes the variable's position name, and **the eq label a placeholder eq coordinate `E*`.** `E*` is the binder's own name when that is free once it stands for the position (launch's `ss` and dinam's `tep` stay), else an unused alias of the eq index's set. The reserved names cover the variable's and multiplier's domains, the derivative's indices and the equation condition's;
  - **the equation condition's eq index** is renamed to `E*` before it is attached;
  - **finally (`_finish_binder_position_rewrite`) only the multiplier's eq index** is pointed at `E*`. If the standard path had made it a summed index pinned by `sameas` (the dimension-mismatch path's `sum((i,t)$sameas(t,te), …)`: dinam is that form too, not a "separate" one as round 1 thought), the index leaves its sum with its pin. `E*` is summed.
- **Regressions**, each an emitted-row unit test plus a validation solve:

  | fixture | before | after | NLP |
  |---|---|---|---|
  | row-bound coefficient | 1.999 | 1.865 | 1.8655 |
  | same, launch's naming (`main` wrong too) | 1.999 | 1.865 | 1.8655 |
  | row-bound nonlinear factor | 13.617 | 8.921 | 8.9208 |
  | equation condition with its own binder | no solve | 7.680 | 7.68 |
  | equation condition over the eq index | (2.924 without the rename) | 1.865 | 1.8655 |

  All 15 earlier fixtures still solve to their NLP optima, and the launch-shape row is byte-identical. Mutation: dropping the label placeholder fails 10 tests; the condition-name reservation, the condition rename and the `sameas`-pin removal each fail exactly their own.
- **Corpus:** the leak gate is complete (no timeouts). Only dinam and shale drift, and both are renames of the summed eq coordinate: shale's `tfp` → its existing alias `tp` of `t`, and dinam's `stat_em` / `stat_v` now use `tep` / `tp`. The resolver holds both (GO). turkpow, tfordy and launch are byte-identical. `make test`: **5,690 passed**.
- **Found on the way:** the emitter drops `a(t) = ord(t)/4;` when `a` is used only in an equation condition (`$141`, identical on `main`). The fixture uses literal data.

### PR #1788 review round 3 (P4)

- **The round-2 representative search dropped the default selector's collision checks** (#1086 / #1278: distinct variable labels, distinct equation labels). With `Alias(t,m,v)`, `h(m,v)` and `e(t).. sum((m,v)$s(t,v), sqr(h(m,v)))`, it could take `e(b)` / `h(a,a)`, and the element map sent both variable coordinates to `v`: `2*h(v,v)` (MCP 4.983 vs NLP 3.169). **Fixed:** it keeps both checks. The row is `2*h(m,v)`, solving to 3.169.
- **A binder over a SUBSET lent its name to the eq coordinate.** With `ss` of `s(i)` against `e(i)`, `sum(ss, … lam_e(ss))` dropped `e('c')` and the MCP did not solve.
  - **Fixed:** the binder's name is reused only when its set CONTAINS the eq index's (`_set_contains`: the same set or a subset ancestor). dinam's `tep` over `te` for `t(te)` still qualified. ⚠ *Narrowed to the SAME set in round 4.*
  - Otherwise an alias of the eq index's set is used (`i__kkt1`), and the fixture solves to 3.0 = NLP.
- **Regressions:** `MULTI_AXIS_ALIAS` and `SUBSET_BINDER`, each an emitted-row unit test plus a validation solve. Removing either fix fails exactly its own test. The fixture's weighted objective first hit #1785 (`c(v,v)` in the gradient), so it uses an unweighted one.
- **Corpus:** the leak gate is complete and clean: 200 in-scope, **0 drifted**, no timeouts, so no golden changes. `make test`: **5,694 passed**, no `225*` dirs.

### PR #1788 review round 4 (P4)

- **Reusing a PARENT-set binder as the eq coordinate changes the equation condition's meaning.** With dinam's shape and `mb(i,t)$(card(t) = 4)..`, the coordinate `tep` (over `te`, 5 elements) turned the guard into `card(tep) = 4`, false everywhere, so the multiplier contribution vanished and the MCP did not solve. `ord(t)` has the same problem, since it counts within the subset.
- **Fixed, both ways:**
  - the binder's name is reused only when it ranges over **exactly** the eq index's set. Round 3's `_set_contains` (which allowed a parent) is removed, so dinam's eq coordinate is now an alias of `t`;
  - the condition rename and the final rename both leave `card(...)` operands alone (`_rename_iterators_keeping_card`), so the guard stays `card(t) = 4`.
- **Regressions:** `PARENT_BINDER_CARD` (an emitted-row unit test plus a validation solve: no solve → 10.524 = NLP) and `PARENT_BINDER_ORD` (an emitted-row unit test; its solve happens to agree either way). Allowing the parent again fails 3 tests; not holding `card` fails exactly its own.
- **Corpus:** the leak gate is complete (no timeouts). Only dinam drifts (−5 B): `stat_em`'s eq coordinate is now `tp`, dinam's alias of `t`, in place of `tep`. The resolver holds it (GO). `make test`: **5,697 passed**, no `225*` dirs.

### PR #1788 review round 5 (P4)

- **No usable representative left neither rewrite active.** With labels shared across the variable's independent sets (`k / a /` beside `i / a, b /`), every entry fails the representative checks. The binder-only admission (round 0's later-binder / subset gate) had already consolidated the entries, so the row lost cross-equation contributions.
  - **Fixed:** for a binder-only pattern, the representative's existence is checked BEFORE consolidation (`_binder_rep_ok` over all entries). Without one, the admission is withdrawn and the pair keeps the pre-#1782 path, byte-identical to it.
  - That path is wrong here too, for the shared-label ambiguity, so the reproducer is recorded on #1778. A position-aware rename cannot fix it: a label shared across sets cannot be attributed to a coordinate.
- **The placeholder alias could take an existing identifier.** `Scalar t__kkt1` beside a minted `Alias(t, t__kkt1)` does not compile (`$195`, one GAMS namespace).
  - **Fixed in the shared `_get_or_create_fresh_alias`:** a minted name skips every set, alias, parameter, variable, equation, model and acronym name. That fixes every caller, not only this one. The fixture mints `t__kkt2` and solves to 7.68 = NLP.
- **Regressions:** `SHARED_LABELS` (the emit equals the same model with the binder-only admission switched off, plus a non-vacuity check that the admission fires) and `NAME_COLLISION` (an emitted-row unit test plus a validation solve). Removing either fix fails exactly its own test.
- **Corpus:** the leak gate drifted **0** goldens. ferts and ganges timed out under load (≈150); re-run alone with `--fail-on-unverified` both are clean, so all 200 are verified. `make test`: **5,700 passed**, no `225*` dirs.

### PR #1788 review round 6 (P4)

- **A direct reference beside the sum rejected the rewrite after consolidation.** In `e(t).. h('m1',t) + 0.5*sum((m,tf)$ts(t,tf), h(m,tf))`, the later-binder admission passed the representative check. Then `_pc_gate`'s whole-equation absence test failed on `h('m1',t)`, after the offsets had been consolidated, so the row lost the per-offset terms: it was no longer the pre-#1782 path.
  - **Fixed:** the pre-consolidation check for a binder-only admission also requires the rewrite's own preconditions on the whole equation: a binder position, and the eq index absent from every reference to the variable. Otherwise the admission is withdrawn.
- **Regressions:** the round-5 test, parametrized as `test_a_binder_only_admission_the_rewrite_cannot_serve_is_WITHDRAWN` (emit = admission-off path, plus non-vacuity), now covers `SHARED_LABELS`, `MIXED_SUBSET` (`x(t)` beside `sum(tf$ts(t,tf), x(tf))`) and `MIXED_LATER_BINDER`.
  - Removing the whole-equation check fails `MIXED_LATER_BINDER`.
  - ⚠ `MIXED_SUBSET` is byte-identical to the pre-#1782 path with or without the check, as measured, so it guards the property but does not discriminate the fix.
  - The pre-#1782 path is itself wrong for mixed direct + summed references: NLP 3.8221 / 12.8859, that path 85.953 / 28.0, identical on `main`. That is #1778's mixed-reference family.
- **Corpus:** the leak gate is complete and clean: 200 in-scope, **0 drifted**, no timeouts. `make test`: **5,702 passed**, no `225*` dirs.

### PR #1788 review round 7 (P4)

- **Independently named sums over the same variable coordinate.** In `e(t).. sum(v$vs(t,v), h(v)) + sum(w$vs(t,w), a(w)*h(w)) =g= 5 - ord(t)` the rewrite rebound only the first sum's `v`. The second guard's `w` stayed free, and the free-index wrap summed the whole derivative over it: `sum((t__kkt1,w), (vs(t__kkt1,v) + a(v)*vs(t__kkt1,w)) * lam_e(t__kkt1))`, MCP 5.440 vs NLP 4.0. `main` does not solve this model (`vs(t,t)`, `t` uncontrolled).
  - **Fixed by rebinding each sum within its own scope:** `_position_binders` collects every binder that carries the variable's coordinate, and requires each reference to the variable to hold an enclosing sum's binder at that position, and nowhere else in it. All of them map to the position name before re-symbolisation.
  - Any other shape (a reference outside such a sum, or the binder elsewhere in the reference) gets no rewrite, and its binder-only admission is withdrawn before consolidation, as in rounds 5–6.
  - The row is now `sum(w, (vs(w,v) + a(v)*vs(w,v)) * lam_e(w))`, solving to 4.0.
- **Regression:** `MIXED_BINDERS`, where only the second sum's binder is renamed: an emitted-row unit test plus a validation solve. Rebinding only the first binder fails it.
- ⚠ This finding came from the review's "previously missed" summary, with no comment thread, so the reply is a new inline comment at the flagged line.
- **Corpus:** the leak gate is complete and clean: 200 in-scope, **0 drifted**, no timeouts. `make test`: **5,704 passed**, no `225*` dirs.

### PR #1788 review round 8 (P4)

- **The combined rebinding crossed sum scopes.** In `e(t).. sum(v$vs(t,v), sum(w,a(w))*h(v)) + sum(w$vs(t,w), h(w))`, round 7's `{v, w} → v` map also rewrote the coefficient's own `sum(w, a(w))` to `sum(w, a(v))`: 4·a(v) in place of 10 (MCP 31.392 vs NLP 25.3884 with RHS `20*ord(t)`).
  - **Fixed:** both derivative rewrites use `_rename_free_indices`, which leaves a name alone inside any Sum/Prod that binds it. The row keeps `sum(w, a(w))` and solves to 25.388.
- **Regression:** `COEFFICIENT_SUM_MIXED_BINDERS` (`COEFFICIENT_SUM` combined with `MIXED_BINDERS`): an emitted-row unit test plus a validation solve. A scope-blind rename fails exactly that test.
- **Corpus:** the leak gate is complete and clean: 200 in-scope, **0 drifted**, no timeouts. `make test`: **5,706 passed**, no `225*` dirs.

### PR #1788 review round 9 (P4)

- **A nested binder that is a rename destination captured the renamed name.** `e(t).. sum(w$(vs(t,w) and sum(v, c(v,w)) > 20), h(w))` with `{w: v}` gave `sum(v, c(v,v))`, which activated the first row's term (15 → 24 > 20): MCP 86.976 vs NLP 14.3662.
  - **Fixed:** `_rename_free_indices` alpha-renames such a binder to a fresh alias of its set before applying the map (only in the rewriting pass: the name-collecting pass mints nothing). The row has `sum(t__kkt1, c(t__kkt1,v)) > 20`, and the fixture solves to 14.366.
- **`card()` in the derivative.**
  - For a SUBSET binder beside a full-set one (`sum(s$vs(t,s), card(s)*h(s))` with `sum(v$…, h(v))`), the subset sum contributes only where `s` holds, which a single representative cannot carry. **The binders at the pattern's position must now range over ONE set,** or the shape keeps the pre-#1782 path. It is byte-identical to it there, and `card(s)` is not rewritten.
  - **The derivative rewrite now holds `card()` operands too.** A rebound binder's operand becomes its SET (`card(w)` → `card(t)`), because leaving the alias name behind made it a free index that the free-index wrap summed over: `sum((t__kkt1,w), …)`.
- **Permuted variable positions** (`h(v,m)`, binder `m` at position 1): the multiplier is spelled `v`, a ROW coordinate, which the finishing step took for a summed index, so it moved the row-bound `h(v,m)` to the eq coordinate.
  - **Fixed:** only a name that is no row coordinate counts as "separate".
  - ⚠ The reviewer's exact fixture also lists the binders out of reference order (`(m,v)` against `h(v,m)`). The AD derivative is then itself wrong (#1776: positional binder pairing gives `h(b,a)*sameas(b,a)*sameas(a,b)`), so it solves on no version. The test pins only the stationarity property, and the reproducer is on #1776. With the binders in reference order the row is correct: 3.168 = NLP.
- **Regressions:** `CONDITION_SCOPE` (row + solve), `MIXED_SUBSET_BINDER_CARD` (keeps the pre-#1782 path, with a non-vacuity check that the same-set rule decides it), `CARD_SAME_SET` (row + solve) and `PERMUTED_POSITIONS` (row). Removing each of the four fixes fails exactly its own test.
- ⚠ **Process slip, recovered:** while measuring a pre-fix control I copied the pre-round source over `src/kkt/stationarity.py` and did not restore it, losing the uncommitted round-9 code. It was restored from the saved copy, the one later edit re-applied, and every function checked for before testing. From now on, controls are measured on a scratch copy, never in place without a verified restore.
- **Corpus:** the leak gate is complete and clean: 200 in-scope, **0 drifted**. `make test` first hit one load-timing failure, `test_performance_overhead_acceptable` (159% vs the 150% threshold; it times the metrics pipeline, which this PR does not touch). It passed 3/3 alone, and the full re-run gave **5,712 passed**, no `225*` dirs.

### PR #1788 review round 10 (P4)

- **`card()` operands counted as free indices.** With an alias-named equation domain (`pr(q)`, `Alias(t,q,w)`), `card(w)` became `card(t)`, and `_collect_free_indices` took the SET operand for an iterator and wrapped the term in `sum(t, …)`. **Fixed in `_collect_free_indices` itself:** a `card(...)` operand is never a free index. This is a general fix, since every `Call` argument used to be walked as an index.
- **Indexed `smax` / `smin` are `Call` nodes and bind their own index.** `{w: v}` captured `smax(v, c(v,w))` as `smax(v, c(v,v))` (no solve).
  - **Fixed:** `_reduction_call_parts` reads the parser's form (a prefix of set/alias names, an optional condition, the body).
  - `_rename_free_indices` scopes and alpha-renames it like a Sum, and `_collect_free_indices` binds its index.
  - The alpha-renamed binder also needs a self-mapping, or the PARAMETER `c`'s declared domain takes it back. So the self-maps now cover every set/alias name in the rewritten derivative. Solves to 14.366 = NLP.
- **Every row coordinate needs a self-mapping.** With `x(m,v,w)` and a three-axis aliased guard, the dimension-mismatch `alias_remap` sent `v` to `w`: `s(E*,m,w,w)`, no solve. **Fixed:** the self-maps cover every variable-domain name. Solves to 0.667 = NLP.
- **Regressions:** `CARD_ALIAS_EQ_DOMAIN` (row; its solve agrees either way), a direct `_collect_free_indices` unit test (`card` bound, `smax` binder bound, `ord` still free), `SMAX_CONDITION_SCOPE` (row + solve) and `THREE_AXIS_GUARD` (row + solve).
  - Mutation: the `card` rule fails its two tests, and the `smax` scoping fails its own.
  - ⚠ The two self-map extensions (row coordinates; derivative names) overlap on these fixtures: removing either alone leaves the tests green, and removing both fails `THREE_AXIS_GUARD` and `SMAX_CONDITION_SCOPE`.
- **Corpus:** the leak gate is complete and clean: 200 in-scope, **0 drifted**, no timeouts. The general `_collect_free_indices` change moves no golden. `make test`: **5,719 passed**, no `225*` dirs.

### Found and routed (not fixed in place)

- **#1787** (Day 8): a variable referenced twice, with the eq index at different positions, keeps one term (egypt `tranc(rp,rp)`, tfordy `stat_v`).
- **#1786** (shale's candidate underlying defect): a subset-defined equation SUMS over its bound subset index when another eq index has no variable counterpart. shale's `stat_z` has it on every subset balance. The 10-line reproducer is a silent wrong answer: MCP 9.03 vs NLP 3.69.
- **#1785:** the objective gradient re-symbolises `ord()` onto the wrong index, for an aliased 2-D variable (MCP 19 vs NLP 0) and for a subset (`ord(t)` → `ord(tf)`, 18.03 vs 17.25). Both are silent wrong answers on 6–7 line models.
- **#1784:** a lead/lag reference inside a sum over a 3-D variable's middle index gets phantom `$(ord(k) = n)` guards, and the MCP does not solve. This is §5's `oik3` fixture: its emit is defective on every version.
- #1784–#1786 are byte-identical on an untouched `main` worktree.

### P8: the structural pins become behavioural

- `_match_subset_domain`'s `if k in used_var_positions:` and both `_compute_index_offset_key` consume-once guards are now **behavioural** pins (`tests/unit/kkt/test_positional_domain_sites.py`). They use §5's 3-D aliased / subset inputs:
  - `_match_subset_domain`: `(ii,jj)` vs `(i,k,ip)` gives `{ii: i, jj: ip}` (guard off: `{ii: i, jj: i}`); alias-only `(ip,ipp)` vs `(i,k,ipp)` gives `{ip: i}` (guard off: `{ip: i, ipp: i}`);
  - `_compute_index_offset_key`: eq `('b','c')` against var `('a','k1','b')` gives `(1, 999, 1)` (guard off: `(2, 999, 999)`), the canonical pass on `(i,ip)` and the root pass on `(ii,jj)`. Each input leaves the OTHER pass's guard-off result unchanged, so the two rows cannot stand in for each other;
  - at emit level, `msd3`: `lam_c(i,ip)` (the MCP solves to the NLP optimum, 2.0) vs `lam_c(i,i)` with the guard off.
- **Positive control:** each pin rebuilds its function from its own source with only that guard neutralised and asserts the result changes. Separately, mutating the guard in `src/` (anchor text kept) fails exactly that guard's own pins.
- **The strength partition moves 5 / 11 → 8 / 8** (behavioural / structural), derived and asserted by identity as before.
- ⚠ **Proof scope for `_compute_index_offset_key`: function level.** Day 6's pass 0 (the reference binding) now binds an index before either pass runs whenever every reference holds it at one position. So §5's `oik3` emit no longer changes with either guard off. The passes and their guards are reached for indices without a reference binding.
