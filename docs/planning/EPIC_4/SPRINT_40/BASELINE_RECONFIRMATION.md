# Sprint 40 Baseline Reconfirmation (Prep Task 2)

**Measured at:** `366e91f3` (`main`, the merge of PR #1746) · **Date:** 2026-10-13 · **Toolchain:** GAMS 54.2.1

Every figure below was produced by a tool at that commit, not copied from the Sprint 39 close documents. Later tasks **cite this file** for both license-gated populations rather than re-typing members (S39 retrospective §7.2: a count catches an omission; only an identity catches a swap).

---

## 1. Anchor diff — did anything move since the Sprint 39 close?

```
$ git diff --stat bd2af6e9 HEAD -- data/ src/ tests/ scripts/
(empty — 0 files)
```

**Nothing substantive moved** between the Sprint 39 close (`bd2af6e9`) and `366e91f3` in `data/`, `src/`, `tests/` or `scripts/` (the last included because the baseline figures are produced by tools under `scripts/gamslib` and `scripts/sprint_audit`). Every file changed since the close is under `docs/` or is `CHANGELOG.md` (`git diff --name-only bd2af6e9 HEAD`). So a figure that differs from the close is a measurement or recall discrepancy, never a code change.

## 2. KPIs and the genuine floor (verbatim tool output)

Unchanged stdout+stderr of each command, captured by running it in a throwaway worktree checked out at **`366e91f3`** (both tools stamp the commit they ran at). Both exited 0.

`$ .venv/bin/python scripts/sprint_audit/kpi_block.py` — verbatim (it emits Markdown; reproduced as-is, not reflowed):

**KPI block — derived at `366e91f3`**

| quantity | value |
|---|---|
| convex candidates | **142** |
| Parse | **142** |
| Translate | **135** |
| Solve | **111** |
| Match | **95** |
| &nbsp;&nbsp;cold-optimal | **65** |
| &nbsp;&nbsp;presolve | **30** |
| model_infeasible | **7** |
| path_syntax_error | **6** |
| path_solve_terminated | **0** |
| path_solve_license | **11** |
| all-219 Match | **98** |

*Genuine floor: NOT derivable from the DB. The mechanical `Match − (presolve ∧ match)` count is **65**, which is **not** the floor — read it from the provenance file (P6c).*

`$ .venv/bin/python scripts/sprint_audit/floor_tracker.py` — verbatim, default output (4 lines):

```
Genuine floor: 75   (derived at 366e91f3)
  = baseline 73 (as of S37-close) + 2 recorded movement(s)
    + elec [presolve-match-genuine] S38 — cold emit changed at 82b91c94 (+3/-3): stationarity equations corrected — always-false ut(i,i) diagonal guard replaced by ut(i,j__), spurious outer sum removed. Was path_solve_terminated (solver_version: None, aborting before PATH); now model_optimal_presolve + match. Cold emit reaches MS-1 @ 244.624 vs NLP 243.8128, so the match arrives via the presolve warm start.
    + twocge [presolve-match-genuine] S38 — cold emit changed at 204f35ac (+10/-0): two nu_*.fx guard lines fixing multipliers for MCP-excluded instances. Was path_solve_terminated (solver_version: None, aborting before PATH); now model_optimal_presolve + match. Cold emit reaches MS-1 @ 55.508 vs NLP 56.7778, so the match arrives via the presolve warm start.
```

`$ .venv/bin/python scripts/sprint_audit/floor_tracker.py --show-mechanical` — verbatim. The DB mechanical-count line is printed **only** with `--show-mechanical` (`floor_tracker.py`: `mech` is computed only `if args.show_mechanical`), so the default run above omits nothing; this run is included so a future comparison has the mechanical figure from the tool itself:

```
Genuine floor: 75   (derived at 366e91f3)
  = baseline 73 (as of S37-close) + 2 recorded movement(s)
    + elec [presolve-match-genuine] S38 — cold emit changed at 82b91c94 (+3/-3): stationarity equations corrected — always-false ut(i,i) diagonal guard replaced by ut(i,j__), spurious outer sum removed. Was path_solve_terminated (solver_version: None, aborting before PATH); now model_optimal_presolve + match. Cold emit reaches MS-1 @ 244.624 vs NLP 243.8128, so the match arrives via the presolve warm start.
    + twocge [presolve-match-genuine] S38 — cold emit changed at 204f35ac (+10/-0): two nu_*.fx guard lines fixing multipliers for MCP-excluded instances. Was path_solve_terminated (solver_version: None, aborting before PATH); now model_optimal_presolve + match. Cold emit reaches MS-1 @ 55.508 vs NLP 56.7778, so the match arrives via the presolve warm start.
  DB mechanical count: 65  <-- NOT the floor. The 'cold emit byte-identical to pre-fix' qualifier is not in the DB.
```

## 3. The two license-gated populations — by identity, with their predicates

### 3.1 MCP-gated cohort — `mcp_solve.outcome_category == "path_solve_license"` → **11**

| model | `gamslib_type` | convexity status |
|---|---|---|
| `egypt` | LP | verified_convex |
| `ferts` | LP | verified_convex |
| `glider` | NLP | likely_convex |
| `robot` | NLP | likely_convex |
| `shale` | LP | verified_convex |
| `sroute` | LP | verified_convex |
| `srpchase` | LP | verified_convex |
| `tabora` | LP | verified_convex |
| `tfordy` | LP | verified_convex |
| `tricp` | QCP | likely_convex |
| `turkey` | NLP | likely_convex |

All 11 are inside the 142-candidate corpus.

### 3.2 NLP-gated set — `convexity.error == "Model exceeds demo license limits"` → **10**

| model | `gamslib_type` (DB) | DB convexity status | in scope? |
|---|---|---|---|
| `airsp` | LP | error | yes |
| `airsp2` | LP | error | yes |
| `andean` | **MIP** | excluded (`minlp_out_of_scope`) | **no — MIP, excluded, never relaxed** |
| `emfl` | QCP | error | yes |
| `indus89` | LP | error | yes |
| `jbearing` | NLP | error | yes |
| `minsurf` | NLP | error | yes |
| `msm` | LP | error | yes |
| `phosdis` | LP | error | yes |
| `torsion` | NLP | error | yes |

**Nine in scope.** None of the ten rows carries an `nlp2mcp_parse` key — they have never been run through the pipeline.

## 4. The nine in-scope NLP-gated models — type and license-free pipeline state (Unknown 3.1)

Type from the raw source's `solve … using` statements (comments and `$onText` blocks stripped); multi-solve status from the pipeline's own classifier, `src/validation/driver.py::scan_multi_solve_driver`, on the parsed IR (the S24 `multi_solve_driver_out_of_scope` gate); parse via `src.ir.parser.parse_model_file`; translate via `python -m src.cli <raw> -o <scratch>` under the pipeline's **600 s** translate timeout. All runs license-free, outputs in a scratch directory (deleted).

| model | source `using` (solves) | multi-solve driver | parse | translate |
|---|---|---|---|---|
| `airsp` | lp ×3 (`alloch`, `allocs` ×2) | no | ✅ 4.5 s | ⏱ **TIMEOUT** (600 s) |
| `airsp2` | lp ×6 (`fixed` ×4, `expval`, `deteq`) | no | ✅ 3.4 s | ✅ 4.8 s |
| `emfl` | qcp ×1 | — | ❌ L36 col 46: `%` in `n1*n%new%` (compile-time `%new%` variable) | ❌ (parse) |
| `indus89` | lp ×1 | — | ❌ L128 col 11: `Singleton Set` | ❌ (parse) |
| `jbearing` | nlp ×1 | no | ✅ 0.7 s | ✅ 74.2 s |
| `minsurf` | nlp ×1 | no | ✅ 0.9 s | ✅ 23.5 s |
| `msm` | lp ×5 (`msm` ×5) | no | ✅ 3.4 s | ⏱ **TIMEOUT** (600 s) |
| `phosdis` | lp ×1 | — | ❌ L609 col 10: `for(iter = 1 to 7, …)` loop syntax | ❌ (parse) |
| `torsion` | nlp ×2 (`torsion`, `torsionx`) | no | ✅ 0.6 s | ✅ 15.4 s |

**Summary: 9/9 in scope by type · 6/9 parse · 4/9 translate** (`airsp2`, `jbearing`, `minsurf`, `torsion`) · 2 translate timeouts (`airsp`, `msm`) · 3 parse failures (`emfl`, `indus89`, `phosdis`). The pipeline's classifier marks **none** of the six parsed models a multi-solve driver, despite several having more than one `solve` statement (`airsp2` ×6, `msm` ×5, `airsp` ×3, `torsion` ×2). **`airsp`/`airsp2` are not near-duplicates:** `airsp2` is the DECIS stochastic variant (297 vs 170 lines, 355 differing lines) and is assessed separately. The three parse failures are unclassified for multi-solve status.

## 5. MCP-gated cohort sizes — generated dimensions (contribution to Unknown 2.1)

Each committed golden `data/gamslib/mcp/<id>_mcp.gms` run in a scratch directory with `iterlim=0`; `SINGLE EQUATIONS` / `SINGLE VARIABLES` read from the listing's `MODEL STATISTICS`. Run under the **demo** license file (`license=` → the system-directory copy — task stays license-free) **and** under the effective license: **identical figures for all 11**, and the demo refused all 11 (consistent with every one being license-gated).

| model | single equations | single variables | recalled figure | verdict |
|---|---|---|---|---|
| `egypt` | 3,447 | 3,537 | "~3,470 equations" (#927) | ❌ recalled figure was approximate — **3,447** |
| `ferts` | 5,702 | 5,702 | — | measured |
| `glider` | 1,531 | 1,637 | — | measured |
| `robot` | 1,688 | 1,694 | — | measured |
| `shale` | 1,956 | 1,956 | — | measured |
| `sroute` | 1,531 | 1,540 | — | measured |
| `srpchase` | 4,005 | 4,005 | — | measured |
| `tabora` | 1,894 | 1,924 | — | measured |
| `tfordy` | 3,155 | 3,157 | — | measured |
| `tricp` | 1,255 | 1,400 | 1,255 rows | ✅ reproduces |
| `turkey` | 3,866 | 3,753 | 3,866 rows | ✅ reproduces |

Largest: `ferts` (5,702), `srpchase` (4,005), `turkey` (3,866) — input to Task 12's nightly-slot sizing alongside Task 7's wall-clock.

## 6. P2 index-repeat ratchet (contribution to Unknown 4.1)

```
$ make check-index-repeats
Index-repeat properties: 193 golden(s), 3109 equation head(s).
  P1 OK: 0 violation(s) in 3109 head(s)
  P2: 9 violation(s) across 6 model(s); baseline 9
PASS
```

Per model, from `scripts/sprint_audit/index_repeat_p2_baseline.json`: **turkpow ×3**, nonsharp ×2, dinam ×1, egypt ×1, gussrisk ×1, shale ×1 — **9**, matching `../SPRINT_39/P2_VIOLATION_TRIAGE.md`.

## 7. Leak gate and test suite

Both run **alone** — started only after checking no other `pytest`, `src.cli`, GAMS batch or gate was running, and run one after the other, never together.

```
$ make check-goldens            (18:20:55 → 18:32:19, rc=0)
Golden staleness: checked 186 in-scope golden(s) (7 allowlisted, 3 workers).
  All in-scope goldens clean.

$ make test                     (18:32:27 → 18:38:17, rc=0)
==== 5444 passed, 10 skipped, 1 xfailed, 108 warnings in 348.42s (0:05:48) =====
```

`make test` is run **explicitly**, even though this task changes no `*.py` file and its quality gate is N/A — the S39 close's test count is a close figure like any other, and the gate's waiver is not a reason to re-quote it.

## 8. Verdict per figure

| figure | S39 close (`bd2af6e9`) | re-derived (`366e91f3`) | verdict |
|---|---|---|---|
| Solve | 111 | 111 | ✅ |
| Match (cold + presolve) | 95 (65 + 30) | 95 (65 + 30) | ✅ |
| Translate | 135 | 135 | ✅ |
| Parse | 142/142 | 142 | ✅ |
| Genuine floor (provenance file) | 75 | 75 | ✅ |
| `path_solve_terminated` | 0 | 0 | ✅ |
| model_infeasible | 7 | 7 | ✅ |
| path_syntax_error | 6 | 6 | ✅ |
| `path_solve_license` | 11 | 11 (named in §3.1) | ✅ |
| all-219 Match | 98 | 98 | ✅ |
| P2 ratchet | 9 = baseline 9 | 9 = baseline 9 (turkpow ×3) | ✅ |
| NLP-gated set | 10 (9 in scope) | 10 (9 in scope; named in §3.2) | ✅ |
| egypt size | "~3,470 equations" | 3,447 eqs / 3,537 vars | ❌ approximate recall → corrected |
| tricp / turkey sizes | 1,255 / 3,866 | 1,255 / 3,866 | ✅ |
| NLP-gated pipeline state | assumed "most parse" | 6/9 parse, 4/9 translate | 🔶 → Unknown 3.1 |
| Leak-gate scope | 186 in-scope (7 allowlisted) | 186 in-scope (7 allowlisted), all clean | ✅ |
| `make test` | 5,444 passed, 10 skipped | 5,444 passed, 10 skipped, 1 xfailed | ✅ |

### Differences, routed

- **egypt's size** (§5): the recalled "~3,470" was an approximation; the measured 3,447 / 3,537 replaces it everywhere a size is quoted. → Task 7 (cohort scheduling) and Unknown 2.1.
- **NLP-gated pipeline state** (§4): only **4 of 9** reach a translated MCP today. → **Task 6** (the corpus-entry decision is about models that can actually run: the brief should show how many would enter under each option, and that 5 need work first), **Task 7** (dry-run only the 4 translating ones end to end; record the 2 timeouts and 3 parse failures as-is), and **Sprint 40 P3** (the three parse failures are grammar work — `%new%` compile-time variables, `Singleton Set`, `for … to …` loops — and the two timeouts are translate-performance work whose cause is **not yet diagnosed** — not assumed to be the sarf class).
