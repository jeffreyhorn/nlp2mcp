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
