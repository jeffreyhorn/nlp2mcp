# Sprint 40 Schema 3.1.0 — `license_edition` Design (Prep Task 5)

**Measured at:** `a8bff1d8` (`main`) · **Date:** 2026-10-14 · **Status:** design only — **P1 implements it; nothing here is implemented yet.**

**License hygiene:** the listing lines quoted below are GAMS's generic header, solver and demo-refusal lines from **synthetic** probes. No licensee, license-ID or node text appears here, and the test fixtures this design specifies are hand-written (§9).

**Bottom line.** The writer list **closes**, with **three additions** beyond the prep plan's list, all found by grep:

1. **`run_full_test.py::mark_cascade_not_tested`** builds `mcp_solve` twice (L680, L695).
2. **`db_manager.py update`** writes any nested field by hand.
3. **`schema.json`'s own `description`** carries `(v3.0.0)`, which `test_db_manager.py` reads as the canonical version.

The **P3 convexity application writer** does not exist and is designed in §6, with the corpus hold built in. The positive control holds: a row carrying the new fields **fails** the current schema and **passes** a draft 3.1.0 schema, which **still rejects** an unknown key (§10).

---

## 1. The contract today

```bash
python3 -c "import json;s=json.load(open('data/gamslib/schema.json'));d=s['definitions'];[print(k,'additionalProperties=',d[k].get('additionalProperties'),'gams_version' in d[k]['properties']) for k in ('mcp_solve_result','convexity_result')]"
# mcp_solve_result additionalProperties= False True
# convexity_result additionalProperties= False False
```

- The top level is also `additionalProperties: false`. Its properties include one `_migration_summary*` block per migration (`_migration_summary`, `_v2_2_1`, `_v3_0_0`).
- `schema_version` is checked by **pattern only** (`^\d+\.\d+\.\d+$`).
- The committed DB has **219 models**, **150 `mcp_solve` objects** (119 `success` · 24 `failure` · 7 `not_tested`) and **219 `convexity` objects**. None carries `license_edition` or `convexity.gams_version`.
- `convexity_result` already defines `solver`, but **0 rows carry it**: nothing writes it.

## 2. Field definitions

| field | in | type | values | meaning |
|---|---|---|---|---|
| `license_edition` | `mcp_solve_result` **and** `convexity_result` | `["string","null"]` | `"licensed"` · `"demo"` · `null` | the edition **of the GAMS run that produced this record**, classified from that run's own listing |
| `gams_version` | `convexity_result` (new; `mcp_solve_result` already has it) | `["string","null"]` | e.g. `"54.2.1"` | the GAMS version from the listing header |

**Null semantics: `null` means *unrecorded*, never a guess.**
- **Existing rows get `null`.** A pre-license row's edition is *unknown*, not `"demo"`. Most corpus rows were small enough to solve on either edition, so "demo" would be a positive claim nobody measured.
- **A writer records `null` whenever it did not classify a listing:** GAMS was not found, a timeout, no listing produced, or a listing matching neither pattern (§4).
- **The enum has no `"unknown"`:** `null` already means that, and a third word would invite guessing (rejected by the schema, §10).
- **Never back-filled by hand.** `db_manager.py update <id> mcp_solve.license_edition demo` would pass validation (§3, writer W6), so the rule is procedural. A row's edition changes only when the run that produced the row is re-run.

**Invariant P1 should test:** after migration and after any pipeline run, **every** `mcp_solve` and `convexity` object carries `license_edition` (present, possibly `null`). It is **non-null exactly when a listing was classified.** A cascade `not_tested` row carries `null`, because no GAMS ran.

## 3. The closed writer list (derived by grep)

**Commands** (run at `a8bff1d8`; `--include` quoted, because zsh globs it otherwise):

```bash
# (a) subscript writes into the two objects
grep -rnE "\[[\"'](mcp_solve|convexity)[\"']\]\s*(=|\[)|setdefault\([\"'](mcp_solve|convexity)[\"']" scripts/ src/ '--include=*.py'
# (b) aliases bound to either object (each read to see whether it mutates)
grep -rnE "=\s*\w+(\.get\(|\[)[\"'](mcp_solve|convexity)[\"']" scripts/ src/ '--include=*.py'
# (c) every schema-version literal, any quoting
grep -rn "3\.0\.0" scripts/ src/ tests/ data/gamslib/schema.json Makefile .github
grep -rn '"3\.0\.0"' scripts/ tests/          # the prep plan's count: 9 hits, re-confirmed
# (d) every gams_version writer
grep -rn "gams_version" scripts/gamslib/*.py | grep -v "migrate_"
```

**Writers: each must change, or is confirmed not to need to.**

| # | site | what it does | change for 3.1.0 |
|---|---|---|---|
| W1 | `scripts/gamslib/test_solve.py::solve_mcp` (L1089; result dict L1390–1405) | runs GAMS, parses the listing, builds the result | add `"license_edition": extract_license_edition(lst_content)` beside `gams_version` (L1313/L1395); add `"license_edition": None` to the **three early returns** (no GAMS L1154, timeout L1198, no listing L1213) |
| W2 | `test_solve.py::update_model_solve_result` (L1449; write L1459) | **rebuilds `mcp_solve` from a fixed key list**, the standalone `--compare` path | add `"license_edition": solve_result.get("license_edition")`. ⚠ This is the Sprint 39 "second writer" that silently dropped `mcp_attribution` (its own comment, L1475). A field missing here vanishes on that path |
| W3 | `scripts/gamslib/run_full_test.py::run_solve_stage` (`solve_entry` L554–583; write L609) | the pipeline's `mcp_solve` record, fixed key list | add `"license_edition": result.get("license_edition")` beside the `gams_version` passthrough (L559) |
| W4 | `run_full_test.py::mark_cascade_not_tested` (L680, L695) | builds `{"status":"not_tested","solve_date":…}` after a parse/translate failure | add `"license_edition": None` to both, for the §2 invariant. *Not in the prep plan's list* |
| W5 | `run_full_test.py` presolve retry (L947 copy; L1005–1017 sub-writes; L1040 restore) | copies the cold `mcp_solve`, re-solves via W3, restores the copy on a failed retry | **no change.** W3 writes the retry's edition and the restore carries the cold run's, so each record keeps the edition of the run that produced it. One presolve listing holds both the embedded NLP and our MCP solve, but it is **one** GAMS run with one edition |
| W6 | `scripts/gamslib/db_manager.py::cmd_update` (L842; `set_nested_value` L752) | sets **any** dotted field (`mcp_solve.license_edition`), validates the model first | **no code change**, since it validates against whatever schema is current. It is a hand-writer, so the §2 no-back-fill rule covers it. *Not in the prep plan's list* |
| W7 | `scripts/gamslib/migrate_catalog.py::transform_entry` (`convexity` built L156–181) | builds the DB's nested `convexity` from `catalog.json`'s flat fields, copying each optional field **only if present** | copy flat `license_edition`, `gams_version`, `convexity_solver` → `convexity.license_edition` / `.gams_version` / `.solver` when present. ⚠ It **regenerates a whole new DB** (default `--output` is `gamslib_status.json`, models plus `convexity` only, **no pipeline stages**). It is **not** an apply-to-live-DB path; §6 is that path |
| W8 | `scripts/gamslib/verify_convexity.py::update_catalog_entry` (L515) | writes flat fields into `catalog.json` (`--update-catalog`) | write the three new flat fields with the same present-or-delete pattern it uses for `solver_status`, so W7 can carry them |
| W9 | `verify_convexity.py::verify_model` + `VerificationResult` (L90, L316) | runs GAMS in a `TemporaryDirectory` that is **deleted on return**; `to_dict()` is `--output` | read the edition, version and **solver name** from `lst_content` **inside** the `with` block (§5); add three fields to `VerificationResult` |
| W10 | **new:** P3 application writer (§6) | verifier `--output` JSON → `gamslib_status.json` `convexity` | design in §6 |
| W11 | **new:** `scripts/gamslib/migrate_schema_v3.1.0.py` (§7) | additive migration | spec in §7 |

**Version stamps** (the `"3.0.0"` literals: 9 hits in `scripts/`+`tests/`, matching the prep plan's count):

| site | class | change |
|---|---|---|
| `db_manager.py:292` `cmd_init --empty` | **initializer** | → `"3.1.0"`; update the "stays correct" comment (L338) to name 3.1.0 (§8) |
| `db_manager.py:349` catalog-init chain message | **initializer** (prose chain) | append `migrate_schema_v3.1.0.py` after `migrate_schema_v3.0.0.py` (§8) |
| `migrate_schema_v3.0.0.py:58` `TO_VERSION` | historical migration | **no change.** See reader R3 for its `--validate` behaviour on a 3.1.0 DB |
| `tests/gamslib/test_migrate_schema_v3.py:78,99,156,242` | test | no change to the literals; the **pop list** must grow (T6) |
| `tests/gamslib/test_db_manager.py:761,773,791` | test (`updated_date` regressions) | none; the version is incidental there |
| **`data/gamslib/schema.json:5` `description` "(v3.0.0)"** | **canonical-version source** (found by the any-quoting grep, not the 9-hit one) | → "(v3.1.0)". ⚠ `test_db_manager.py:641` reads the canonical version **from this string** and checks `--empty`'s stamp against it, so it must move **in the same commit** as `db_manager.py:292` |

**Readers and classifiers, not writers** (confirmed by reading each alias hit):
- `db_manager.py:624/659` (`cmd_get` display) — display only; showing the edition there is optional.
- `scripts/sprint_audit/check_mcp_solve_attribution.py` — an **inspector**. It classifies listings and writes an `attribution.json` **report**, never the DB. `mcp_attribution` / `mcp_completed_own_solve` are **constructed in `test_solve.py`**. Its own version check is pattern-only, so 3.1.0 passes.
- **No other `sprint_audit/` tool writes DB fields:** `floor_tracker.py`, `kpi_block.py` and `check_doc_figures.py` only read, via `.get()`.
- `batch_parse.py` / `batch_translate.py` write `nlp2mcp_parse` / `nlp2mcp_translate` only.
- `check_presolve_divergence.py:157` reads `convexity`.
- `migrate_schema_v2.2.0.py:162` / `v3.0.0.py:74` are historical migrations.
- `test_error_recovery.py` writes its own synthetic `2.0.0` DBs.

**Strict-reader survey** (an extra key or the version bump): **no reader breaks.**
- No reader keeps its own key allow-list, `extra='forbid'` model, `**row` constructor on these objects, exact-key assertion, or exact-version comparison. Only `schema.json` enforces the field set, so it must change in the same commit as the first writer.
- Things that behave differently:

| # | where | what changes |
|---|---|---|
| R1 | the jsonschema validators: `db_manager.py validate` / `init` / `update` and `check_mcp_solve_attribution.py:600` | reject the new fields until `schema.json` changes |
| R2 | `test_db_manager.py:641` | reads the `description` version |
| R3 | `migrate_schema_v3.0.0.py --validate` | validate-only runs only when `current == "3.0.0"`, so on a 3.1.0 DB it now refuses ("Expected 2.2.1"). One-shot tool, not in CI; the 3.1.0 script's `--validate` replaces it |
| R4 | `test_migrate_schema_v3.py:202–243` | rewinds the **committed** DB to 2.2.1 |

- **R4 in detail:** once the committed DB is 3.1.0, the rewind would keep `license_edition`, `convexity.gams_version` and `_migration_summary_v3_1_0`. The test would then start from the old/new *hybrid* its own docstring forbids, and still pass. **T6 fixes this.**

## 4. Parser extension: one parser, shared by both stages

**Where:** beside `extract_gams_version` in `scripts/gamslib/test_solve.py` (L393). Both stages import from there, and **no second copy is made** in `verify_convexity.py`. That follows the module's own precedent: the attribution regexes are *"reused rather than re-implemented"* (L56). `scripts/` is a namespace package (no `__init__.py`), so `verify_convexity.py` adds the same `sys.path.insert(0, PROJECT_ROOT)` that `test_solve.py` uses (L50–51) before `from scripts.gamslib.test_solve import …`.

```python
# Task 3 (LICENSE_PROBE.md §3): generic GAMS text only. The licensed USER: line
# names the licensee, so it is matched by PREFIX via a negative lookahead and
# NEVER captured, returned, logged or stored.
_DEMO_EDITION = re.compile(r"^(?:\*{4} The model exceeds the demo license limits\b|USER: GAMS Demo,)", re.M)
_LICENSED_EDITION = re.compile(r"^USER: (?!GAMS Demo,)", re.M)

def extract_license_edition(lst_content: str) -> str | None:
    """'demo' | 'licensed' | None (neither marker: unknown, never guessed)."""
    if _DEMO_EDITION.search(lst_content):
        return "demo"
    if _LICENSED_EDITION.search(lst_content):
        return "licensed"
    return None

# Solver actually used, from the SOLVE SUMMARY ("     SOLVER  CONOPT   FROM LINE  3").
# Read, never inferred from the option passed: Task 3 found QCP runs CONOPT by
# default whatever NLP= says. Last match wins; a refused listing has none -> None.
_SOLVER_LINE = re.compile(r"^\s+SOLVER\s+(\S+)\s+FROM LINE\b", re.M)

def extract_solver_name(lst_content: str) -> str | None: ...
```

**Order matters:** demo is tested first. A refused demo run has no `USER:` line, and a completed demo run's `USER: GAMS Demo,` line must not satisfy the licensed pattern; the lookahead also excludes it.

**Measured on synthetic probes today** (licensed run; demo via `license=` pointed at the system-directory demo file; nothing displaced):

| probe | header line | `SOLVER` line | classified |
|---|---|---|---|
| 5-row NLP, effective license | `GAMS 54.2.1 …` | `SOLVER  CONOPT …` | `licensed` |
| 1,500-row NLP, demo (**refused**) | `GAMS 54.2.1 …` **present** | **absent** | `demo` |
| 5-row NLP, demo (completed) | `GAMS 54.2.1 …` | `SOLVER  CONOPT …` | `demo` |

**So a refused row records `gams_version` and `license_edition: "demo"`, but no solver.** That is the record the 11 + 9 gated models carry today, and the one P2/P3 must show moving.

## 5. `verify_convexity.py`: capturing provenance before the directory is deleted

`verify_model` writes `output.lst` inside `tempfile.TemporaryDirectory()` (L351). The directory is removed when the `with` block exits, and every `return` is inside it. Its `--output` JSON is `VerificationResult.to_dict()` (`asdict`), which today has numeric `solver_status` but **no solver name and no edition**.

**Change:**
1. **Add to `VerificationResult`:** `license_edition: Optional[str] = None`, `gams_version: Optional[str] = None`, `solver: Optional[str] = None`. They have defaults, so the existing positional constructions stay valid, and `to_dict()` carries them into `--output` automatically.
2. **Capture once, directly after `lst_content` is read (L425), before any branch:** `prov = dict(license_edition=extract_license_edition(lst_content), gams_version=extract_gams_version(lst_content), solver=extract_solver_name(lst_content))`. Pass `**prov` to **every** `VerificationResult` built after that point:
   - the demo-refusal return (L428): `demo`, version, solver `None`;
   - the `error_type` return;
   - the no-solve-summary return;
   - `classify_result` (give it a `provenance` parameter).
3. **Returns before the listing is read stay `None`** (§2: no listing classified): `EXCLUDED` (no GAMS run), `FileNotFoundError`, `TimeoutExpired`, `returncode == 2`, and no listing.

**These fields reach `convexity_result` only through W10 (§6)** or the catalog route (W8 → W7). Adding them to `VerificationResult` alone changes nothing in the DB.

## 6. The P3 application writer (W10): verifier output → `gamslib_status.json`

**Today no command applies `verify_convexity.py`'s results to the live DB.** `--update-catalog` writes `catalog.json`. `migrate_catalog.py` rebuilds an entire DB from the catalog, which would wipe every pipeline stage, so it cannot be used on the live DB. P3 needs a real application step, and **that step is where Unknown 3.3's corpus hold has to live**: `kpi_block.py:45` and `floor_tracker.py:42` derive the candidate corpus from `convexity.status ∈ {verified_convex, likely_convex}`, so a write *is* a corpus change.

**Proposed:** `scripts/gamslib/apply_convexity_results.py`

```
apply_convexity_results.py --input <verify_convexity --output JSON> --db <path>
                           [--admit <model_id> ...] [--dry-run] [--validate]
```

- **`--db` is required and has no default:** applying results to the committed DB has to be a deliberate choice.
- **Mapping, per result:**
  - `convexity_status` → `status`;
  - `verification_date`;
  - `solver_status`, `model_status`, `objective_value`, `solve_time_seconds`, `timed_out`;
  - `error_message` → `error`;
  - `license_edition`, `gams_version`, `solver`.
- **Schema-correct omission.** `solver`, `solver_status`, `model_status` and `objective_value` are **non-nullable** in `convexity_result` (`integer` / `number` / `string`), so they are **omitted** when `None`, never written as `null`. This mirrors `update_catalog_entry`'s present-or-delete pattern. `license_edition` and `gams_version` are nullable and **always written**, per §2's invariant.
- **Replace, don't merge:** the model's whole `convexity` object is rebuilt from the result. Merging would let fields from an older run survive under a new run's provenance.
- **The corpus hold (built in):** if the model's **current** status is outside `CONVEX_STATUSES` and the **new** one is inside, the writer **refuses** unless the id is listed in `--admit`. The `--admit` list is the owner's corpus-entry decision (Task 6), passed in explicitly. A refusal is a non-zero exit naming the models; it never silently skips. Status changes that **leave** the corpus, or stay outside it, are applied and **listed** in the run's summary, because they also move the 142.
- **Unknown ids, and models whose type is outside LP/NLP/QCP: refuse.** MINLP/MIP stays excluded and is never relaxed.
- **Then:** refresh the top-level `updated_date`, validate (same `None` vs `[]` distinction as `migrate_schema_v3.0.0.validate`), write only if valid, and keep a backup.

**Tests:** see T9.

## 7. `migrate_schema_v3.1.0.py`

This mirrors `migrate_schema_v3.0.0.py`'s structure: the `FROM`/`TO` refusal, a validate-only mode, the `None` ≠ `[]` validation result, a backup and `--dry-run`.

- **`FROM_VERSION = "3.0.0"`, `TO_VERSION = "3.1.0"`.** It refuses any other starting version, so it can't be run twice: re-running would add nothing and still bump the version.
- **Additive transform (idempotent):**
  - every `mcp_solve` dict gets `license_edition: None` **if absent**;
  - every `convexity` dict gets `license_edition: None` and `gams_version: None` **if absent**;
  - an existing value is **never overwritten**;
  - new keys are appended, so the existing key order stays byte-stable.
  - Expected footprint at `a8bff1d8`: **150** `mcp_solve` + **219** `convexity` objects.
- **Not added:** `convexity.solver`. It is non-nullable and nothing records it, so it stays **absent** until W10 writes a real value.
- **`schema_version` → `"3.1.0"` and `updated_date` → now (UTC ISO 8601),** exactly as `migrate_schema_v3.0.0.py` does (L150–157). `schema.json` defines it as the *"timestamp of last modification"*, and leaving it stale was a PR #1740 finding.
- **`_migration_summary_v3_1_0`:** `{to_version, added: {"mcp_solve.license_edition": n, "convexity.license_edition": n, "convexity.gams_version": n}}`. ⚠ The top level is `additionalProperties: false`, so **`schema.json` must declare this block** (§8), or the migrated DB fails validation (measured, §10).
- **Chain position:** after `migrate_schema_v3.0.0.py`.

## 8. `schema.json` and `db_manager.py` changes

**`schema.json` (same commit as the first writer):**
1. Add `license_edition` (`{"type":["string","null"], "enum":["licensed","demo",null]}`) to **both** `mcp_solve_result` and `convexity_result`.
2. Add `gams_version` (`["string","null"]`) to `convexity_result`.
3. Add `_migration_summary_v3_1_0` (`object`) to the top-level `properties`.
4. Change `description` "(v3.0.0)" → "(v3.1.0)".
5. **Keep `additionalProperties: false`** everywhere.

**`db_manager.py`:**
1. **`cmd_init --empty`:** stamp `"3.1.0"` (L292), and update the L338 comment from *"still stamps 3.0.0, and that stays correct"* to name 3.1.0. The reasoning is unchanged: an empty DB has no rows for any migration to have missed.
2. **Catalog-init warning chain** (L349 list): append `"migrate_schema_v3.1.0.py"` after `"migrate_schema_v3.0.0.py"`.
3. **Optional:** show `license_edition` in `cmd_get` (L624/L659).
4. **Leave alone:** `validate_model_entry`'s `"0.0.0"` placeholder (pattern-only, L821).

## 9. Test list

**Fixtures are synthetic and non-identifying:** hand-written listing snippets built around the generic lines of §4. A licensed fixture uses a made-up `USER: Example Licensee` line. The demo `USER:` fixture is written as `USER: GAMS Demo, for EULA and demo limitations see` with the license-ID tail **left off**. **Never** paste a real `.lst` license header.

| # | file | asserts |
|---|---|---|
| T1 | `tests/gamslib/test_test_solve.py` | `extract_license_edition`: refusal line → `demo`; `USER: GAMS Demo,` → `demo`; synthetic licensed `USER:` → `licensed`; neither → `None`; a listing holding **both** a licensed `USER:` and a refusal line → `demo` (order). `extract_solver_name`: `CONOPT` / `PATH`; refused listing → `None`; last match wins |
| T2 | same | `solve_mcp` (mocked subprocess writing a synthetic listing) carries `license_edition`; the **three early returns** carry `None` |
| T3 | same | `update_model_solve_result` **persists** `license_edition` (W2: the fixed-key-list regression, as for `mcp_attribution`) |
| T4 | `tests/gamslib/test_run_full_test_path_relative.py` or a new `test_run_full_test_license_edition.py` | `run_solve_stage` persists it (W3); both `mark_cascade_not_tested` branches write `None` (W4); the presolve restore keeps the **cold** run's edition (W5) |
| T5 | `tests/gamslib/test_migrate_schema_v3_1_0.py` (new, beside `test_migrate_schema_v3.py`) | additive: every object gains the keys as `None`; an **existing value is not overwritten**; `schema_version == "3.1.0"`; **`updated_date` is refreshed** (regression assertion); `_migration_summary_v3_1_0` counts; refuses a non-3.0.0 start **and a second run**; `--dry-run` writes nothing; output **validates against the real `schema.json`** |
| T6 | `tests/gamslib/test_migrate_schema_v3.py` | `_POST_MIGRATION_FIELDS` and the rewind gain `mcp_solve.license_edition`, `convexity.license_edition`, `convexity.gams_version` and a `pop("_migration_summary_v3_1_0")`, so the 2.2.1 rewind stays a genuine 2.2.1 shape (R4) |
| T7 | `tests/gamslib/test_db_manager.py` | `--empty` stamps 3.1.0 and `test_empty_init_stamps_the_canonical_version` passes against the bumped `description`; the catalog-init chain lists `migrate_schema_v3.1.0.py` after v3.0.0; `update … mcp_solve.license_edition licensed` validates, while `… license_edition unknown` is **rejected** |
| T8 | schema tests (in T5's file, or `tests/gamslib/test_schema_3_1_0.py`) | both types **accept** `licensed` / `demo` / `null`; **reject** `"unknown"`; **still reject an unknown key** (e.g. `licence_edition`) in **both** types; the top level accepts `_migration_summary_v3_1_0` and still rejects an unknown top-level key |
| T9 | `tests/gamslib/test_verify_convexity.py` + new `test_apply_convexity_results.py` | `verify_model` (mocked run, synthetic listings): the refusal return carries `demo`, version and `solver None`; the classified return carries all three; pre-listing returns carry `None`; `to_dict()` includes them. **W10:** the mapping; non-nullable fields **omitted** when `None`; replace-not-merge; **the hold refuses** a model entering `CONVEX_STATUSES` without `--admit` and **applies** it with `--admit`; MINLP/MIP and unknown ids refused; `updated_date` refreshed; output validates. **W7/W8:** `update_catalog_entry` writes and clears the three flat fields; `migrate_catalog` copies them into `convexity` only when present |

## 10. Positive control: "an un-migrated field fails validation"

A copy of a real row (`abel`) was given `mcp_solve.license_edition`, `convexity.license_edition` and `convexity.gams_version`, then validated with `Draft7Validator` in memory. Nothing was written.

| schema | result |
|---|---|
| **current 3.0.0** | **fails:** `Additional properties are not allowed ('license_edition' was unexpected)` (`mcp_solve`) and `('gams_version', 'license_edition' were unexpected)` (`convexity`) |
| **draft 3.1.0** (§8 items 1–3) | **passes** with `licensed`, `demo` and `null` |
| draft 3.1.0, `license_edition: "unknown"` | fails (`'unknown' is not one of ['licensed', 'demo', None]`) |
| draft 3.1.0, unknown key `licence_edition` in `mcp_solve` / `bogus` in `convexity` | **fails**: `additionalProperties: false` still bites |
| `_migration_summary_v3_1_0` at the top level | passes the draft; **fails the current schema**, which is why §8 item 3 is needed |

So the claim is demonstrated, not assumed, and the draft does not loosen the contract.

## 11. Order of work for P1

1. `schema.json` (§8) **together with** the `db_manager.py` stamp and chain, plus T7 and T8.
2. The parser (§4) plus T1.
3. W1–W4, plus T2–T4.
4. The migration (§7) plus T5 and T6, then **run it on the committed DB** (`--dry-run --validate` first).
5. W8/W9/W7, plus their part of T9.
6. W10 with its hold, plus the rest of T9, **before** any P3 licensed convexity run is applied.

**Steps 1 and 3 must not be split across commits:** a writer emitting the field before the schema allows it fails validation mid-batch. Unknown 1.4's second risk.
