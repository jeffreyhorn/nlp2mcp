# Presolve-Record Remedy Design (P7)

**Sprint 39 Prep Task 8** · **Measured at:** `15fb4a78`, GAMS **54.2.1** · **Authored:** 2026-09-01

> **⚠ Two findings, and the headline one is that P7's framing does not hold.** *"One remedy covering all affected rows"* is not achievable, because the spurious match and the dangling references are **different defects that share one row**. Neither candidate remedy fixes both. **P7 needs two changes at one site, landed together** — stated here rather than discovered mid-sprint.
>
> **⚠ And the KPI fall is bigger than the plan says.** The plan anticipates Match 96 → 95. Measured: **three** figures move (Match, presolve-match, all-219). Two that were *feared* do **not** — see §4.

---

## 1. The population, re-derived (Unknown 7.1)

Task 2 measured these at `a8669ad6`. Re-derived here at `15fb4a78` because a figure is evidence only at the point of use.

| population | count | what it is |
|---|---|---|
| `presolve_required: true` | **48** | all-219 presolve rows |
| presolve goldens on disk | **40** | `data/gamslib/mcp/*_mcp_presolve.gms` |
| presolve ∧ match | **34** | the attribution scope |
| presolve ∧ match ∧ convex candidate | **31** | the KPI "presolve" line |
| **dangling `mcp_file_used`** | **14** | of the 48, the recorded path does not exist |

All five reproduce exactly. **`weapons` is still the only spurious match**: the attribution checker over all 34 reports **33 MCP-SOLVED, 1 EMBEDDED-ONLY**, and the one is `weapons` (`war/NLP MS-2` and nothing else).

The 14 dangling rows, named: `aircraft`, `apl1p`, `apl1pca`, `china`, `circle`, `imsl`, `lmp2`, `prodsp2`, `ps10_s_mn`, `ps5_s_mn`, `senstran`, `spatequ`, `trig`, **`weapons`**.

**⚠ P7's phrase "all 14 rows or none" conflates two populations.** The dangling set is **14**; the spurious set is **1**. Their intersection is `weapons` alone. Any remedy statement has to name which it means.

## 2. What weapons' record should say — measured, not assumed

The obvious replacement is "record the failure". **That is wrong, and measuring it is what showed so.**

Run cold from a scratch directory at `15fb4a78`:

| | value |
|---|---|
| `weapons_mcp.gms` (cold) | **MODEL STATUS 1 Optimal** |
| cold objective | **1700.397** |
| NLP reference | 1735.5696 |
| relative difference | **2.0266 %** (tolerance 0.2 %) |

So **weapons' cold MCP solves.** The presolve retry fired because `_cold_objective_mismatches_nlp` was satisfied — correctly. The retry's MCP then aborted, `nlp2mcp_obj_val = tetd.l` read back the embedded NLP's own 1735.5696, and the comparison matched itself.

**The correct record is therefore weapons' own cold result** — `model_optimal`, 1700.397, comparison **mismatch**. Not a failure, and not a new category.

**This matters for the remedy's shape.** The record-writing code already has the branch that produces exactly this: when a retry fails it restores `original_mcp_solve`. So the fix does not invent a category or a value — **it declines to overwrite.**

## 3. Remedy coverage, per row (Unknown 7.2)

**Where the record is written:** `scripts/gamslib/run_full_test.py:936`, the `if retry_result["status"] == "success":` branch, which sets `presolve_required` (`:949`), `mcp_file_used` (`:954`) and `outcome_category` (`:955`). Located by **symbol**, then the line numbers read back from the file — the Day-10 note's `~954` is right for one of the three and would have been the wrong insertion point.

### Remedy A — gate the retry-success branch on attribution

Extend the condition to *"the retry succeeded **and** the MCP produced its own `MODEL STATUS`"*. On failure, fall through to the existing `else`, which restores `original_mcp_solve`.

| corrects | rows |
|---|---|
| spurious match | **1 of 1** — `weapons` |
| dangling references | **1 of 14** — only `weapons`, and only as a side effect of its row reverting to the cold golden, which exists |

**A does not fix the other 13.** For those the retry genuinely succeeded; `mcp_file_used` faithfully records a *generated* artifact that was never adopted as a golden. Nothing about them is wrong except the field's meaning.

### Remedy B — re-specify `mcp_file_used` (null unless a committed golden exists) + back-fill

| corrects | rows |
|---|---|
| dangling references | **14 of 14** |
| spurious match | **0 of 1** — `weapons` would still read `model_optimal_presolve` + match |

**B is a code change *and* a back-fill, not a back-fill alone.** `run_full_test.py:954` rewrites the field on every successful retry, so a back-filled null is overwritten the next time the model is re-solved.

### ❌ The assumption behind 7.2 is wrong

Unknown 7.2 assumes *"one of two remedies covers the whole population"*. **Neither does.** They address different defects:

- the **spurious match** is a *truth* defect — the row asserts something untrue;
- the **dangling reference** is a *specification* defect — the field records a real thing under a name that implies a different thing.

`weapons` sits in both only because a spurious retry also happens to leave a dangling path behind.

**⚠ And A is a prerequisite for B's durability on the weapons row.** B alone back-fills `weapons`'s path to null while leaving the match; the next pipeline run re-solves it, the retry "succeeds" again, and both defects return. **A must land, or B is transient where it matters most.**

**Recommendation: land A and B together as one change at one site.** That is still systemic — two rules, one insertion point, one PR — but it must be *described* as two rules, because "all 14 rows or none" is true of B and false of A.

## 4. What actually moves (Unknown 7.3)

Simulated by rewriting weapons' row to its cold result and re-running `kpi_block.compute_kpis`:

| KPI-block row | before | after |
|---|---|---|
| **Match** | 96 | **95** |
| &nbsp;&nbsp;**cold-optimal** | 65 | **65 — unchanged** |
| &nbsp;&nbsp;**presolve** | 31 | **30** |
| **all-219 Match** | 99 | **98** |
| **Solve** | 111 | **111 — unchanged** |
| **`path_solve_terminated`** | 0 | **0 — unchanged** |

*Row names and order are `kpi_block.py`'s own, so this table cross-references the block a reader meets in a report. `presolve` and `cold-optimal` are the indented sub-rows of `Match`; where the prose below says "presolve-match" it means this `presolve` row.*

Not a KPI-block row, but moved by the same change: **dangling `mcp_file_used`** 14 → **13** under Remedy A alone, → **0** under A + B.

**Two feared collisions do not happen, and both are worth stating because the plan does not rule them out.**

1. **`path_solve_terminated` stays 0.** Sprint 39 pre-registers it as an acceptance criterion where *a return to non-zero is a REGRESSION, not churn*. Recording weapons as a failure would have set it to 1 and collided head-on. It does not, **because the correct record is the cold solve, not a failure.** An earlier draft of this analysis assumed a failure record and reported `Solve 111 → 110` and `path_solve_terminated 0 → 1`; measuring the cold solve refuted both.
2. **Solve stays 111** — weapons does solve. Only the *comparison* was untrue.

**The floor cannot change, structurally.** `floor_tracker.compute_floor(provenance)` takes only the provenance dict — it never reads the DB. So this is not "the floor should be unaffected"; it is unaffected by construction.

### Gates and consumers, checked one by one

| consumer | effect |
|---|---|
| `scripts/sprint_audit/kpi_block.py` | reports the new figures — intended |
| `scripts/sprint_audit/floor_tracker.py` | **none** — reads provenance, not the DB |
| `scripts/sprint_audit/check_doc_figures.py` | ⚠ **`Match` 96 → 95**, so the check flags any **changed** doc line citing 96 — correct behaviour, but the docs must move in the same PR. ⚠⚠ **The `dangling mcp_file_used rows` fact does NOT go 14 → 0** under the decided remedy — that prediction assumed the `null` option. See §9: left un-updated the fact reports **0 for the wrong reason**, and updated it reports **14, unchanged**. |
| `tests/unit/sprint_audit/test_check_doc_figures.py` | ⚠ **NOT "none" once the fact is RENAMED** (PR #1738 review). The original reasoning covered the *number* changing, not the *name*: `TRUTHS` are pinned fixtures, so 14 → any value breaks nothing. But `check_doc_figures.py:661` is `if fact.name not in truths: continue`, and `TRUTHS` hard-codes the key `"dangling mcp_file_used rows"`. Rename the fact without the fixture and **the new fact is silently skipped in every test while the old key sits inert** — coverage lost with the suite still green. See §9 obligation 3. |
| `tests/gamslib/test_run_full_test_path_relative.py` | ⚠ Sprint 27 #1400 requires a **repo-relative** path when one is written. A null must be an explicit allowed case, not an accident |
| CI workflows | **none assert Match monotonicity.** `check_parse_rate_regression.py` reads only `parse_rate_percent`, `convert_rate_percent`, `avg_time_ms` from a report JSON — there is no Match analogue and no DB read. `ci.yml` touches `gamslib_status.json` only as a **cache key** |

**⚠ The one real gate interaction is `--resolve-changed`.** `_bucket_severity` = `compare_rank × 10 + outcome_rank`. weapons today is `match` + `model_optimal_presolve` ⇒ **22**; corrected it is `mismatch` + `model_optimal` ⇒ **12**. A drop is classified `backward`, and `backward` is the checkpoint's **only NO-GO**.

It does not fire *for this change*, because the checkpoint selects models whose **emit golden changed** and P7 changes no golden. But the mechanism matters in the other direction: **if the DB is corrected without Remedy A, a later re-solve records the spurious match again, and the checkpoint reads that as `forward` (12 → 22) — an improvement.** The gate would applaud the regression. That is the sharpest argument for A.

## 5. The KPI-fall wording, pre-written

To be used verbatim, so the fall is never reported as a bare number.

> **Match 96 → 95 is a CORRECTION, not a regression.** `weapons` was recorded as a **presolve** match, but the presolve retry's MCP produced no `MODEL STATUS` of its own. A `--nlp-presolve` emit warm-starts by solving the original model inside the generated file, so when that MCP solve aborted, `nlp2mcp_obj_val = tetd.l` still held the embedded NLP's own answer (1735.5696) and the comparison matched itself. **This is not "weapons cannot be solved as an MCP"** — its **cold** emit solves, to `model_optimal` @ **1700.397**, which is a **2.03 %** divergence from the NLP and therefore a **mismatch**. That cold result is the true record. The overstatement dates from Sprint 38 Day 9, was reported at the time, and is corrected here. **Match 95 is the first figure in this series that is true.** Solve (111), cold-optimal (65) and the genuine floor (73) are unaffected; presolve-match moves 31 → 30 and all-219 Match 99 → 98 for the same single reason.

**Three rules this wording follows**, each from a Sprint-38 close finding: the reason is in the **same sentence** as the number; the figures that did **not** move are named, so the reader is not left inferring a wider fall; and the direction is stated as a property of the *record*, not of the work.

## 6. The presolve-golden adoption rule (draft for CONTRIBUTING)

> **Adopting a `_mcp_presolve.gms` golden.** All four must hold. Record each in the PR.
>
> 1. `scripts/sprint_audit/check_mcp_solve_attribution.py --models <id>` reports **`MCP-SOLVED`**. `EMBEDDED-ONLY` and `MCP-NO-STATUS` are both refusals.
> 2. `scripts/diagnostics/check_presolve_divergence.py --model <id>` passes.
> 3. The DB's `mcp_solve.mcp_file_used` references **the golden being adopted**.
> 4. **The emit actually executes.** Run it and read a `MODEL STATUS` produced by *our* `mcp_model`.
>
> **Why (4) is separate from (1)–(3).** `weapons` passed structure, DB, NA-guard and determinism review and was adopted — and its emit did not run. *A golden can pass every static check and still not execute.* The reviewer who caught it did so by running the file, which no checklist item had asked for. (Sprint 38 Day 9.)
>
> **⚠ Do not key the check on `EXECERROR`.** It conflates MCP-side and NLP-side aborts, which is how `weapons` was first reported against the wrong half of its listing. The attribution tool's method is deliberately **positional** — it locates the solve summary that is `TYPE MCP` *for our emitted model name* and asks whether that summary carries a `MODEL STATUS`. Preserve that; a global grep cannot answer the question.

## 7. Regression-test specification

**The property:** *a solve whose MCP produced no status of its own must not be recordable as a match.*

**Fixture** — corpus-free, so it runs in the unit suite: a minimal presolve-shaped listing with **one** solve summary, `TYPE NLP`, carrying `MODEL STATUS 2`, and no `mcp_model`/`TYPE MCP` summary. This is weapons' shape reduced to its discriminating feature.

**Assertions:**

1. Attribution over that listing returns **`EMBEDDED-ONLY`**.
2. Driving the record-writing path with a retry whose listing has that shape leaves `outcome_category` **not** `model_optimal_presolve`, and `solution_comparison.objective_match` **not** `true`.
3. **The negative control:** the same fixture *plus* a second summary — `mcp_model` / `TYPE MCP` / `MODEL STATUS 1` — is recorded as a presolve match normally. Without this, a test that rejects everything passes.
4. **Mutation requirement:** revert the gate and assertion 2 must fail. A green test here proves nothing on its own — this suite has already shipped three tests that passed against a reverted fix.

**Placement:** beside `tests/unit/sprint_audit/test_mcp_solve_attribution.py` for (1) and (3); the record-writing assertion (2) belongs with the `run_full_test` tests, since that is where the branch lives.

## 8. What this design does not do

- **It does not correct the DB.** That is P7 execution. The wording in §5 is written so the correction is reportable the day it lands.
- **~~It does not decide the `mcp_file_used` replacement value.~~ ✅ DECIDED by the owner, 2026-09-10: RENAME the field to `mcp_file_generated` and KEEP the path.** The debugger-useful information is preserved, and the field's name then matches what the pipeline actually knows — that it *generated* a file, not that the file is still present. ⚠ **This doc's original framing — "both close the dangling count" — was wrong, and §9 records the consequence.** Keeping the path means the count does **not** close; it stays at **14**. What changes is that those rows stop being a *defect*.
- **It does not re-check the remaining rows for spuriousness** — the 13 other than `weapons`. All are `MCP-SOLVED` per §1, so their records are true; only the field's meaning is at issue.

## 9. The decided field rename, and the silent-zero trap it sets for P7

**Decision (owner, 2026-09-10): rename `mcp_solve.mcp_file_used` → `mcp_solve.mcp_file_generated`, keeping the recorded path.**

### What the rename fixes

The *specification* defect named in §4. The pipeline writes this field at emit time and knows exactly one thing: that it **generated** that file. It does not know, then or later, whether the file is still on disk — the presolve artifacts are working files, and 14 of the 48 have since been cleaned up. `mcp_file_used` asserts a present-tense fact the writer was never in a position to assert; `mcp_file_generated` asserts the past-tense fact it actually observed. **A non-existent path then stops being an anomaly and becomes the expected steady state.**

### ⚠ What it does NOT do — three live docs say otherwise

`PLAN.md` §3 (risk table), this doc's §7 consumer table, and `KNOWN_UNKNOWNS.md` §7.3 all predict `check_doc_figures.py`'s `dangling mcp_file_used rows` fact going **14 → 0**. **That prediction was written for the `null` option and does not survive the decided one.** Keeping the path keeps the count. All three are corrected in the same PR as this section.

### ⚠⚠ THE TRAP: the predicted number and the broken number are the same number

`_dangling_presolve_rows` reads the key by name:

```python
if (f := (m.get("mcp_solve") or {}).get("mcp_file_used"))
```

Measured against the live DB, simulating the rename with paths kept:

| state | fact reports |
|---|---|
| today | **14** |
| after the rename, checker **left as-is** (reads `mcp_file_used`) | **0** |
| after the rename, checker **updated** (reads `mcp_file_generated`) | **14** |

So a P7 that renames the DB key and forgets the checker sees the fact fall to **0** — **exactly the number three planning documents predicted** — while the derivation has in fact gone blind, summing over a key that no longer exists. The prediction would appear confirmed by the very defect it should have caught.

This is the *silent scope narrowing* class already on record (S37's leak gate sweeping 3 goldens instead of 163): **a derived truth that reports 0 because it is looking at nothing is worse than no check**, because every correct citation of 14 would then be flagged as contradicting it.

### P7's obligations, therefore

*Six, not the five this section first listed — the schema contract was missing (PR #1738 review).*

1. **Update `_dangling_presolve_rows` to the new key IN THE SAME COMMIT as the DB migration.** Not the same PR — the same commit. A commit where the DB has moved and the checker has not is a commit whose figures lie.
2. **Assert the fact still derives 14 afterwards.** A positive control: the count must be *unchanged*, and a 0 is the failure signal, not the success signal. This inverts the usual reading, so state it at the assertion.
3. **Rename the fact, its `source` string, AND the pinned test fixture — together.** `dangling mcp_file_used rows` describes a defect that no longer exists; the population is still worth deriving (docs cite it), but as *"presolve rows whose generated file is no longer on disk"*.
   - ⚠ **Two of its three patterns key on the word `dangling`, not three** (PR #1738 review — an earlier revision of this line said three). Patterns 1–2 are the forward and reverse `dangling` forms; **pattern 3 is `all\s+N\s+(?:presolve-record\s+)?rows`, which never mentions `dangling`** and must survive the rename untouched. Editing it because a list said "three" would silently drop the "all 14 rows" citation form.
   - ⚠ **`tests/unit/sprint_audit/test_check_doc_figures.py` must move in the same commit.** `check_doc_figures.py:661` is `if fact.name not in truths: continue`, and the test's `TRUTHS` hard-codes `"dangling mcp_file_used rows": 14`. Rename `FACTS` alone and the new fact is **skipped in every test** — no failure, no coverage. The consumer table's original "none" for this file reasoned about the pinned *value*, which is safe, and missed the *key*, which is not.
4. **The Sprint 27 #1400 repo-relative requirement still applies unchanged.** `tests/gamslib/test_run_full_test_path_relative.py` exists because an absolute path leaked into this field. The decided remedy still writes a path, so — unlike the `null` option, which needed a new "null is allowed" case — that test's property is untouched. Only the key it names moves.
5. **`run_full_test.py:954` is the sole writer.** Renaming the DB key without it means the next pipeline run silently re-introduces `mcp_file_used` alongside `mcp_file_generated`, and the DB carries both.
6. **⚠⚠ `data/gamslib/schema.json` IS THE HARD ONE — it breaks P7's own gate** (PR #1738 review; this obligation was missing from the first revision of §9). `definitions.mcp_solve_result` sets **`additionalProperties: false`** and lists `mcp_file_used` among its properties, so a renamed key is an *unexpected property*.

   Measured by deep-copying the live DB, renaming the key and validating:

   | state | schema errors |
   |---|---|
   | today | **0** |
   | rename, `schema.json` unchanged | **48** — `Additional properties are not allowed ('mcp_file_generated' was unexpected)` |
   | rename, `schema.json` updated too | **0** |

   **48, not 14** — every row carrying the field, not only the dangling ones.

   **Why this is worse than a failed check:** `scripts/sprint_audit/check_mcp_solve_attribution.py:832-834` validates the whole DB and `raise InputError(schema_error)` on failure. That tool is **§6's adoption-rule item 1** and Remedy A's gate. So P7 would break the instrument it needs to verify itself with — and the failure surfaces as a refusal to run, not as a diagnosis of the rename.

   **⚠ AND IT MAY NOT REPRODUCE ON YOUR MACHINE.** `jsonschema` is **not** a declared dependency (absent from `requirements.txt` and `pyproject.toml`), and `_validate_against_schema` is documented as a **no-op** when the import fails. So on a machine without it the migration looks clean and breaks wherever the library *is* installed. Same shape as the silent-zero trap in this section: **the local signal and the true signal differ.** Verify with `jsonschema` present, and say in the PR that you did.

   **Also update the property's `description`.** It currently reads *"Relative path to the MCP file that was **solved**"* — a stronger version of the same present/past-tense defect the rename exists to fix, and demonstrably false for `weapons`, whose MCP never solved. `"...that was generated"` is what the writer actually knows.

### Why this is not §5's KPI correction

Independent of it. §5's `Match 96 → 95` is a **record correction** about `weapons`; this rename is a **field respecification** about all 48 presolve rows. They land together in P7 only because §4 showed one row (`weapons`) sits in both populations. Neither number depends on the other, and the KPI wording in §5 stands verbatim.

---

**Document Status:** ✅ Complete — Sprint 39 Prep Task 8
**Last Updated:** 2026-09-01
