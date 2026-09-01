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

| figure | before | after |
|---|---|---|
| **Match** | 96 | **95** |
| **presolve-match** | 31 | **30** |
| **all-219 Match** | 99 | **98** |
| Solve | 111 | **111 — unchanged** |
| cold-optimal match | 65 | **65 — unchanged** |
| `path_solve_terminated` | 0 | **0 — unchanged** |
| dangling rows | 14 | **13** (A alone) / **0** (A + B) |

**Two feared collisions do not happen, and both are worth stating because the plan does not rule them out.**

1. **`path_solve_terminated` stays 0.** Sprint 39 pre-registers it as an acceptance criterion where *a return to non-zero is a REGRESSION, not churn*. Recording weapons as a failure would have set it to 1 and collided head-on. It does not, **because the correct record is the cold solve, not a failure.** An earlier draft of this analysis assumed a failure record and reported `Solve 111 → 110` and `path_solve_terminated 0 → 1`; measuring the cold solve refuted both.
2. **Solve stays 111** — weapons does solve. Only the *comparison* was untrue.

**The floor cannot change, structurally.** `floor_tracker.compute_floor(provenance)` takes only the provenance dict — it never reads the DB. So this is not "the floor should be unaffected"; it is unaffected by construction.

### Gates and consumers, checked one by one

| consumer | effect |
|---|---|
| `scripts/sprint_audit/kpi_block.py` | reports the new figures — intended |
| `scripts/sprint_audit/floor_tracker.py` | **none** — reads provenance, not the DB |
| `scripts/sprint_audit/check_doc_figures.py` | ⚠ the `dangling mcp_file_used rows` fact goes 14 → 0 and `Match` 96 → 95. The check then flags any **changed** doc line still citing the old figures — correct behaviour, but the docs must move in the same PR |
| `tests/unit/sprint_audit/test_check_doc_figures.py` | **none.** Its `TRUTHS` are *pinned* fixtures, deliberately not derived ("deriving them here would re-implement the thing under test"), and no test asserts derived == pinned |
| `tests/gamslib/test_run_full_test_path_relative.py` | ⚠ Sprint 27 #1400 requires a **repo-relative** path when one is written. A null must be an explicit allowed case, not an accident |
| CI workflows | **none assert Match monotonicity.** `check_parse_rate_regression.py` reads only `parse_rate_percent`, `convert_rate_percent`, `avg_time_ms` from a report JSON — there is no Match analogue and no DB read. `ci.yml` touches `gamslib_status.json` only as a **cache key** |

**⚠ The one real gate interaction is `--resolve-changed`.** `_bucket_severity` = `compare_rank × 10 + outcome_rank`. weapons today is `match` + `model_optimal_presolve` ⇒ **22**; corrected it is `mismatch` + `model_optimal` ⇒ **12**. A drop is classified `backward`, and `backward` is the checkpoint's **only NO-GO**.

It does not fire *for this change*, because the checkpoint selects models whose **emit golden changed** and P7 changes no golden. But the mechanism matters in the other direction: **if the DB is corrected without Remedy A, a later re-solve records the spurious match again, and the checkpoint reads that as `forward` (12 → 22) — an improvement.** The gate would applaud the regression. That is the sharpest argument for A.

## 5. The KPI-fall wording, pre-written

To be used verbatim, so the fall is never reported as a bare number.

> **Match 96 → 95 is a CORRECTION, not a regression.** `weapons` was recorded as a presolve match, but its MCP never solved: the `--nlp-presolve` emit warm-starts by solving the original model inside the generated file, so when the MCP aborted, `nlp2mcp_obj_val = tetd.l` read back the embedded NLP's own answer (1735.5696) and the comparison matched itself. Its true cold result is `model_optimal` @ **1700.397**, a **2.03 %** divergence from the NLP — a **mismatch**. The overstatement dates from Sprint 38 Day 9, was reported at the time, and is corrected here. **Match 95 is the first figure in this series that is true.** Solve (111), the cold-optimal partition (65) and the genuine floor (73) are unaffected; presolve-match moves 31 → 30 and all-219 Match 99 → 98 for the same single reason.

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
- **It does not decide the `mcp_file_used` replacement value.** `null` is the plan's suggestion and is consistent with the field's name; an alternative — rename to `mcp_file_generated` and keep the path — preserves information a debugger may want. Both close the dangling count; they differ in what is lost. **Owner's call, flagged rather than taken.**
- **It does not re-check the remaining rows for spuriousness** — the 13 other than `weapons`. All are `MCP-SOLVED` per §1, so their records are true; only the field's meaning is at issue.

---

**Document Status:** ✅ Complete — Sprint 39 Prep Task 8
**Last Updated:** 2026-09-01
