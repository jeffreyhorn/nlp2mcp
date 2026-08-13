# Sprint 37 Day 10 — Checkpoint 2 + P3 camcge + the `solver_version` gap closed

**Date:** 2026-08-13 · **Branch:** `planning/sprint37-day10-checkpoint2` · **Scope:** `scripts/` + DB + schema. No `src/` change.

**Verdict: ✅ GO.** Checkpoint 2 passes on all three components. The day's substantive finding is that **`solver_version` was never going to populate** — the extractor's regex has never matched — which explains why two sprints of "populate `solver_version`" instructions failed. Both that and the deeper provenance gap are now closed.

---

## 1. Checkpoint 2 — three components, all pass

| # | component | result |
|---|---|---|
| a | `make check-goldens` | ✅ **163 checked, all clean**, 0 timeouts (at the new default of 3 workers) |
| b | `--resolve-changed --since-commit 78ceaead` | ✅ **GO** — all 19 changed-golden models held their bucket, every one `= same` |
| c | PR25 tally | ✅ Solve **108** · Match **94** (65 cold + 29 presolve) · genuine floor **76** |

**No NO-GO condition met.** Notably, turkey now reads `path_solve_license → path_solve_license  = same` — its stale-entry correction persisted on Day 9 and is now stable rather than a pending shift.

## 2. The `solver_version` gap — a broken *read*, not a missing *write*

Day 9 and Task 8 both recorded *"populate `solver_version` (currently `null` for all 219 rows)"* as a re-baseline instruction. **That instruction could never have worked.**

`extract_path_version` (`scripts/gamslib/test_solve.py:330`) searched for:

```
PATH Version: 5.2.01          <- what the docstring CLAIMED GAMS emits
```

GAMS actually emits:

```
Path 5.2.01 (Mon Jul 13 19:47:36 2026)     <- different case, and no "Version:"
```

The regex has **never matched**, which is why every row was null. Two sprints of re-baseline instructions assumed a missing write; the defect was a failed extraction, and the docstring documented a format that isn't produced — which is presumably how it survived review.

**Fixed:** the matcher now accepts both spellings (`re.IGNORECASE` on the legacy form, plus the actual `^Path <ver> (`). Verified against a real listing: `extract_path_version → '5.2.01'`. **The docstring was rewritten too** — leaving it asserting a format the code does not parse would re-create the exact trap that caused this bug, and PR review caught that I had fixed the implementation while leaving the docstring stale.

## 3. The deeper gap — `solver_version` would not have answered the question anyway

Task 8's actual need was *"no per-row provenance for **which GAMS version** produced a result"*. But:

- **`mcp_solve.solver_version`** records the **PATH solver** version (`5.2.01`).
- **top-level `gams_version`** records `51.3.0` and is described as *"the GAMS version used to **source** the models"* — a corpus-provenance field, not a per-solve one, and unrelated to which version solved a row.

So even a working extractor would have left the v53-vs-v54 question open.

**Added `mcp_solve.gams_version`** — extracted from the listing header (`GAMS 54.2.1  d9889eb3 …`), captured alongside the PATH version, forwarded through both writers, and documented in `schema.json` (`additionalProperties` was already permitted, so the addition is schema-legal).

Verified end-to-end on a real solve:

```
markov  solver_version: '5.2.01'   gams_version: '54.2.1'
```

Then populated corpus-wide by a full `--only-solve` (445 s):

| | count |
|---|---|
| rows with a solve outcome | 143 |
| **rows carrying `gams_version`** | **135** — all `54.2.1` |
| rows carrying `solver_version` | 114 |

**The 8 rows without provenance are explained, not missing:** `abel`, `ps10_s`, `ps2_f_s`, `ps2_s`, `ps3_s`, `ps3_s_gic`, `ps3_s_mn`, `ps3_s_scp` are all **`non_convex`** — outside the candidate corpus, so `--only-solve` never re-ran them. Provenance is complete for every row the re-solve touched. (`solver_version` < `gams_version` because a row can reach a listing header without reaching a PATH solve — e.g. a license refusal.)

**What this retires:** Day 9's re-baseline diff existed *only* because "did v54 change anything?" could not be answered by querying the DB — it took a 372-second re-solve plus per-model `git log` archaeology to classify three moved rows. The next version transition is now a query.

## 4. KPIs unchanged by the re-solve

**Solve 108 · Match 94 (65 cold + 29 presolve) · genuine floor 76** — identical to Day 9's post-re-baseline state. The full re-solve was run to populate provenance, not to move buckets, and it moved none.

## 5. P3 camcge — the Epic-5 gate confirmed, exactly as predicted

The `/tmp` Walras control (GAMS 54.2.1):

| quantity | measured | Task 9's prediction |
|---|---|---|
| emit time | **19 s** | ~18 s ✓ |
| model size | **641 single equations / 641 variables** | 641, demo-reachable ✓ |
| embedded NLP | **MS-2 Locally Optimal @ omega 191.7346** | MS-2 @ 191.7346 ✓ |
| `mcp_model` | **MS-4 Infeasible** | MS-4 ✓ |

Every figure reproduces. The MCP is MS-4 against a correct NLP optimum — the structural Walras rank-deficiency, not an emit defect.

**The three-part dual-consistent Walras redefinition was deliberately NOT attempted.** Price-pin → MS-4, single-dual-pin → MS-4, drop-row → corrupt @ omega 299; 3+ sprints of variants have all stayed MS-4. Running it here would re-run a refuted experiment. **The drop-row half remains BANNED** (primal-correct but breaks the MCP dual).

⇒ **camcge stays an Epic-5 deliverable**, with the per-model-numéraire fallback confirmed. **0 bucket for Sprint 37.**

## 6. Two prompt items already resolved

- **The v54 decision** was made on **Day 9** — the corpus is re-pinned to GAMS 54.2.1 with zero Regressions (`GAMS54_REBASELINE_DIFF.md`). Not re-litigated here.
- **The sarf budget fork** is **closed**, resolved on Day 7 on measured grounds.

## 7. A process note carried from Day 9

Day 9's `git add -A` after a GAMS run swept 20 runtime artifacts (including `decis.lic`) and 36 unintended presolve goldens into a commit. Today's full re-solve regenerated the same 36 presolve goldens; they were **deleted rather than staged**, and the artifacts did not reappear because they are now `.gitignore`d. The staged change is six files — the DB, the schema, the two writers, this note and the CHANGELOG — and **no** runtime artifact or regenerated golden among them.

---

**Document Status:** ✅ Complete — Sprint 37 Day 10 (Checkpoint 2 GO; provenance gap closed; camcge → Epic 5).
**Last Updated:** 2026-08-13 · **Owner:** Sprint 37 execution team
