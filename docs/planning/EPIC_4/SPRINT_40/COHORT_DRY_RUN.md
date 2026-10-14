# Sprint 40 License-Gated Cohorts Dry Run (Prep Task 7)

**Measured at:** 79eeccff013027c036a7abc2e6a2fde79028ec20 (the `head_sha` of **all 53** retained invocations, every site and phase: 25 `solve_mcp`/`batch`, 9 `verify_model`/`convexity`, 11 `kkt_residual`/`residual`, 5 `solve_mcp`/`residual`, 3 `attribution`/`attribution`; none `null`. It descends from Task 6's answers commit `b44344a2`.)

**Date:** 2026-10-14 · **Toolchain:** GAMS 54.2.1, **every invocation classified `licensed`** from its own retained listing · **Branch descends from** `b44344a2` ✅

**License hygiene:** this document records **edition classes, solver names, invocation ids and SHAs only**, plus GAMS's generic error lines from emitted models. No license-file content, licensee, license-ID or node text. Every retained listing, the worktree and the attribution tool's work directory were removed by an `EXIT` trap (log: `CLEANED (worktree, retention dir, attr dir removed)`), and the sanitized output directory was scanned clean before use.

---

## Summary

- **MCP-gated (11):**
  - **all 11 re-emit byte-identical** to their goldens, and all translate within the 600 s limit (slowest `ferts`, 167 s);
  - **all 11 reach a GAMS listing.**
  - **2 match**, both only via the presolve warm start: `tfordy`, `turkey`.
  - **9 do not:** 5 infeasible (`egypt`, `robot`, `shale`, `tricp` MS 5; `sroute` MS 4), 2 terminated before PATH reported (`ferts`, `tabora`), 2 solved without matching (`srpchase`, `glider`).
- **NLP-gated (9 in scope):** **all 9 classify convex** under the licensed verifier: **5 `verified_convex`** (the five LPs) and **4 `likely_convex`** (`emfl`, `jbearing`, `minsurf`, `torsion`).
  - **2 match** (`airsp2`, `torsion`), both via the presolve warm start.
  - **2 do not:** `jbearing` (cold emit does not compile) and `minsurf` (cold MCP aborts).
  - **5 never reach an MCP:** `airsp` and `msm` time out at translate (600 s); `emfl`, `indus89` and `phosdis` fail to parse. These are the same five Task 2 found.
- **Residuals:** **11 non-matches** had an MCP and were run through `kkt_residual.py`.
  - **5 verdicts, all `case_b` (emit bug):** `glider`, `minsurf`, `robot`, `sroute`, `tricp`.
  - **6 harness failures**, so no verdict: the `--nlp-presolve` residual emit either does not compile (`egypt`, `srpchase` `$140`; `shale` `$148`; `jbearing` `$171`) or aborts in execution (`ferts` `EXECERROR = 46`, `tabora` `= 36`).
- **Every non-match has a route; unrouted fingerprints: 0.** Six routes are new routing notes (below), because no fix surface is named yet. Under P10's selection rule (a reproduced fingerprint **and** a named fix surface), **only `egypt` and `shale` (P4) qualify today**; the rest are banked for P2 diagnosis.
- **`ISSUE_933` (tricp) no longer reproduces:** the current golden compiles (**0** error markers in its own listing) and reaches PATH. The issue is re-scoped, not closed: tricp is now `case_b`.
- **Attribution at size (Unknown 2.3):** `turkey` → `MCP-SOLVED` (the positional parse finds our `mcp_model` among three summaries); `weapons` (positive control) → `EMBEDDED-ONLY`, correctly not counted; `egypt` → indeterminate, because its presolve emit does not compile.
- **What P2 would book**, as license-unlocked, not recovered:
  - in-corpus **+2 Match** (`tfordy`, `turkey`) and **+4 Solve** (those two, plus `srpchase` and `glider`, which solve without matching);
  - `path_solve_license` 11 → 0.
  - **All four matches are presolve-only.** **Zero license-unlocked *cold* matches**, so Decision 1's ledger receives nothing from this run. The floor booking of the presolve matches follows the existing rule, plus the fail-before sub-rule for `turkey` (S35 `$161` fix); that is P2's to apply.

## Results

| model | population | provenance (stage·edition·solver·invocation id·head_sha) | golden | translate s | solve s | wall s (convexity + pipeline) | outcome | NLP obj | MCP obj | abs diff | rel diff | comparison | attribution | residual | route |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `egypt` | MCP-gated ⚑ | `mcp`·licensed·PATH·`egypt_mcp.1792010020379437000.12764`·`79eeccff` | identical | 49.0 | 3.3 | 156 | `model_infeasible (MS 5)` | 4134175.7019 |  |  |  | not_tested | `MCP-FAILED` / own=True | none (harness failed, rc 1) | **P4** (Class-A `tranc(rp,rp)`); presolve emit `$140`×2 → **R-PRE-140** |
| `ferts` | MCP-gated ⚑ | `mcp`·licensed·—·`ferts_mcp.1792010252212377000.12939`·`79eeccff` | identical | 167.1 | 0.9 | 184 | `path_solve_terminated` | 58793.8227 |  |  |  | not_tested | `NO-SOLVE` / own=False | none (harness failed, rc 1) | **R-EXEC** (cold MCP aborts before PATH reports; presolve residual `EXECERROR = 46`) |
| `glider` | MCP-gated | `mcp`·licensed·PATH·`glider_mcp_presolve.1792010272308953000.13342`·`79eeccff`<br>`residual`·licensed·PATH·`glider_mcp_presolve_residual.1792012254090367000.15822`·`79eeccff` | identical | 4.4 | 2.0 | 21 | `model_optimal_presolve (MS 1)` | 1282.3997 | 1286.9774 | 4.57770000000005 | 0.0035569389174977353 | mismatch | `MCP-SOLVED` / own=True | `case_b` | **R-B-glider** |
| `robot` | MCP-gated | `mcp`·licensed·PATH·`robot_mcp.1792010281137925000.13402`·`79eeccff`<br>`residual`·licensed·PATH·`robot_mcp_presolve_residual.1792012416158223000.16190`·`79eeccff` | identical | 4.4 | 11.6 | 29 | `model_infeasible (MS 5)` | 9.1469 |  |  |  | not_tested | `MCP-FAILED` / own=True | `case_b` | **R-B-robot** (Task 8's baseline) |
| `shale` | MCP-gated ⚑ | `mcp`·licensed·PATH·`shale_mcp.1792010337526235000.13517`·`79eeccff` | identical | 19.5 | 2.3 | 56 | `model_infeasible (MS 5)` | 9354.8644 |  |  |  | not_tested | `MCP-FAILED` / own=True | none (harness failed, rc 1) | **P4** (Class-A `ts(tf,tf)`); presolve emit `$148`×2 |
| `sroute` | MCP-gated ⚑ | `mcp`·licensed·PATH·`sroute_mcp.1792010376410182000.13615`·`79eeccff`<br>`residual`·licensed·PATH·`sroute_mcp_presolve_residual.1792012465219068000.16330`·`79eeccff` | identical | 14.9 | 0.7 | 17 | `model_infeasible (MS 4)` | 6468.0 |  |  |  | not_tested | `MCP-FAILED` / own=True | `case_b` | **R-B-sroute** |
| `srpchase` | MCP-gated ⚑ | `mcp`·licensed·PATH·`srpchase_mcp.1792010380835010000.13653`·`79eeccff` | identical | 2.1 | 0.8 | 7 | `model_optimal (MS 1)` | 0.4001 | 0.0 | 0.4001 | 1.0 | mismatch | `MCP-SOLVED` / own=True | none (harness failed, rc 1) | **R-PRE-140** (shared with egypt); cold solve lands at objective 0 |
| `tabora` | MCP-gated | `mcp`·licensed·—·`tabora_mcp.1792010428197657000.13688`·`79eeccff` | identical | 40.9 | 0.7 | 45 | `path_solve_terminated` | 8471.9573 |  |  |  | not_tested | `NO-SOLVE` / own=False | none (harness failed, rc 1) | **R-EXEC** (cold MCP aborts before PATH reports; presolve residual `EXECERROR = 36`) |
| `tfordy` | MCP-gated ⚑ | `mcp`·licensed·PATH·`tfordy_mcp_presolve.1792010482616279000.13772`·`79eeccff` | identical | 22.8 | 3.2 | 57 | `model_optimal_presolve (MS 1)` | 102.0362 | 102.0362 | 0.0 | 0.0 | match | `MCP-SOLVED` / own=True | — | — (match) · floor booking → P2 under Decision 1 |
| `tricp` | MCP-gated ⚑ | `mcp`·licensed·PATH·`tricp_mcp.1792010491449649000.13853`·`79eeccff`<br>`residual`·licensed·PATH·`tricp_mcp_presolve_residual.1792012532295823000.16469`·`79eeccff` | identical | 3.7 | 3.5 | 17 | `model_infeasible (MS 5)` | 3838.2686 |  |  |  | not_tested | `MCP-FAILED` / own=True | `case_b` | **ISSUE_933** re-scoped (compile errors gone; now `case_b`) |
| `turkey` | MCP-gated | `mcp`·licensed·PATH·`turkey_mcp_presolve.1792010669432388000.13899`·`79eeccff` | identical | 55.1 | 6.2 | 174 | `model_optimal_presolve (MS 1)` | 29078.2106 | 29078.2106 | 0.0 | 0.0 | match | `MCP-SOLVED` / own=True | — | — (match) · floor booking → P2 under Decision 1 (fail-before sub-rule applies: S35 `$161` fix) |
| `airsp` | NLP-gated | `convexity`·licensed·CPLEX·`airsp.1792010677828466000.14089`·`79eeccff` | — | 600.0 (timeout) | — | 1 + 603 | `translate timeout` | 1566.0422 |  |  |  | not_tested | — | — | **P3** translate timeout |
| `airsp2` | NLP-gated | `convexity`·licensed·DECISM·`airsp2.1792010678997510000.14120`·`79eeccff`<br>`mcp`·licensed·PATH·`airsp2_mcp_presolve.1792011312939381000.14803`·`79eeccff` | — | 3.1 | 4.3 | 5 + 15 | `model_optimal_presolve (MS 1)` | 1037.246 | 1037.246 | 0.0 | 0.0 | match | `MCP-SOLVED` / own=True | — | — (match) · admitted by Decision 2's rule → P3 / W10 |
| `emfl` | NLP-gated | `convexity`·licensed·CONOPT·`emfl.1792010683545639000.14198`·`79eeccff` | — | — | — | 7 + 1 | `parse failure` | 46.8675 |  |  |  | not_tested | — | — | **P3** grammar (parse) |
| `indus89` | NLP-gated | `convexity`·licensed·CPLEX·`indus89.1792010690475831000.14225`·`79eeccff` | — | — | — | 1 + 2 | `parse failure` | 114873.6556 |  |  |  | not_tested | — | — | **P3** grammar (parse) |
| `jbearing` | NLP-gated | `convexity`·licensed·CONOPT·`jbearing.1792010691954261000.14237`·`79eeccff`<br>`mcp`·licensed·—·`jbearing_mcp.1792011367481278000.14924`·`79eeccff` | — | 45.5 | 0.7 | 1 + 48 | `path_syntax_error` | -0.1548 |  |  |  | not_tested | `NO-SOLVE` / own=False | none (harness failed, rc 1) | **R-JB-171** |
| `minsurf` | NLP-gated | `convexity`·licensed·CONOPT·`minsurf.1792010693117708000.14250`·`79eeccff`<br>`mcp`·licensed·—·`minsurf_mcp.1792011383515301000.14971`·`79eeccff`<br>`residual`·licensed·PATH·`minsurf_mcp_presolve_residual.1792012326181194000.15967`·`79eeccff` | — | 13.8 | 33.3 | 1 + 48 | `path_solve_terminated` | 2.5195 |  |  |  | not_tested | `NO-SOLVE` / own=False | `case_b` | **R-EXEC** (cold) + **R-B-minsurf** |
| `msm` | NLP-gated | `convexity`·licensed·CPLEX·`msm.1792010694146384000.14262`·`79eeccff` | — | 600.1 (timeout) | — | 2 + 603 | `translate timeout` | 3957.98 |  |  |  | not_tested | — | — | **P3** translate timeout |
| `phosdis` | NLP-gated | `convexity`·licensed·CPLEX·`phosdis.1792010696174159000.14280`·`79eeccff` | — | — | — | 3 + 1 | `parse failure` | 959033.0 |  |  |  | not_tested | — | — | **P3** grammar (parse) |
| `torsion` | NLP-gated | `convexity`·licensed·CONOPT·`torsion.1792010698480728000.14298`·`79eeccff`<br>`mcp`·licensed·PATH·`torsion_mcp_presolve.1792012069318452000.15555`·`79eeccff` | — | 18.8 | 8.4 | 1 + 56 | `model_optimal_presolve (MS 1)` | -0.4175 | -0.4175 | 0.0 | 0.0 | match | `MCP-SOLVED` / own=True | — | — (match) · admitted by Decision 2's rule → P3 / W10 |

**Columns:**
- **Provenance:** one tuple per GAMS invocation that produced a recorded value, as stage · edition · solver · invocation id · `head_sha`. Each tuple is associated with **exactly one** retained invocation by the artifact's per-stage rule (site + phase + input file, and a match on status, objective and `mcp_attribution`). `—` as solver means the listing has no `SOLVE` summary, because the run stopped before PATH reported.
- **Golden:** a HEAD re-emit `cmp`'d against the committed golden.
- **Wall:** the verifier run (NLP-gated only) plus the full `run_full_test.py --model` pipeline run.
- **⚑:** carries a repeated-symbol declared domain (Sprint 39 Unknown 6.2).
- **NLP obj:** the reference objective (`solution_comparison.nlp_objective`, or the convexity objective where comparison was `not_tested`).
- **Abs / rel diff:** blank where no MCP objective exists.

## Convexity — the nine NLP-gated models, licensed (Unknown 3.2)

`verify_convexity.py --model <id> --timeout 600 --output <scratch>.json`, **output-only**: `catalog.json` was unchanged afterwards (empty `git status` in the worktree), and **no `gamslib_status.json` was written**. Edition and solver come from each run's **own** retained listing.

| model | type | licensed classification | model status | objective (NLP reference) | solver(s) actually used, from its own listing | SOLVE summaries | wall s |
|---|---|---|---|---|---|---|---|
| `airsp` | LP | `verified_convex` | 1 | 1566.0422 | CPLEX | 3 | 1 |
| `airsp2` | LP | `verified_convex` | 1 | 1037.246 | CPLEX, DECISM | 6 | 5 |
| `emfl` | QCP | `likely_convex` | 2 | 46.8675 | CONOPT | 1 | 7 |
| `indus89` | LP | `verified_convex` | 1 | 114873.6556 | CPLEX | 1 | 1 |
| `jbearing` | NLP | `likely_convex` | 2 | -0.1548 | CONOPT | 1 | 1 |
| `minsurf` | NLP | `likely_convex` | 2 | 2.5195 | CONOPT | 1 | 1 |
| `msm` | LP | `verified_convex` | 1 | 3957.98 | CPLEX | 5 | 2 |
| `phosdis` | LP | `verified_convex` | 1 | 959033.0 | CPLEX | 7 | 3 |
| `torsion` | NLP | `likely_convex` | 2 | -0.4175 | CONOPT | 1 | 1 |

- **All nine classify convex: 5 `verified_convex` and 4 `likely_convex`.**
  - Under Task 6 Decision 2 (admit by rule), all nine are admitted. P3 applies them through W10's `--admit`.
  - **Five of the nine cannot yet reach an MCP** (see Results).
- **Every convexity solve finished in at most 7 s**, far inside the verifier's 60 s default. Only the demo refusal had kept these models out.
- ⚠ **Four are multi-solve** (`airsp` 3, `airsp2` 6, `msm` 5, `phosdis` 7 `SOLVE` summaries), and the verifier classifies from the listing's **last** status.
  - **`airsp2`'s classification and objective come from a `DECISM` (stochastic decomposition) solve**, not from the CPLEX LP solve `verify_convexity.py` requests with `LP=CPLEX`. The model selects its own solver for later solves.
  - **Routed to P3:** before W10 applies these, decide whether a multi-solve model's last solve is the right reference (cf. the multi-solve driver gate behind `PROJECT_PLAN.md` footnote ⁴).
- **`emfl` (QCP) ran CONOPT**, as Task 3 predicted: CONOPT is this install's default QCP solver.

## Routing — every non-match

None is fixed here; P10's rule applies. These are **routing notes**, opened as issue documents by P2 once a fix surface is named:

| route | models | fingerprint (reproduced in this run) | first step |
|---|---|---|---|
| **P4** | `egypt`, `shale` | cold MCP `model_infeasible` (MS 5); the **presolve** emit does not compile (`egypt` `$140` ×2, `shale` `$148` ×2, each with a cascading `$257`) | the known Class-A references (`tranc(rp,rp)`, `ts(tf,tf)`); P4 now has a real solve to verify a fix against |
| **R-PRE-140** | `egypt`, `srpchase` | presolve emit: `$140 Unknown symbol` ×2 + `$257`; `srpchase`'s cold MCP solves (MS 1) **at objective 0** vs NLP 0.4001 (rel diff 1.0), its retry was rejected (`NO-SOLVE`) and the cold record kept | identify the unknown symbol in the presolve emit; one defect may explain both |
| **R-EXEC** | `ferts`, `tabora`, `minsurf` | the cold MCP **aborts before PATH reports** (`no_solve_summary`; `ferts`/`tabora` within 1 s, `minsurf` after 33 s); the presolve residual aborts with `EXECERROR = 46` (`ferts`) / `36` (`tabora`) | capture the execution-error line. Not retained in sanitized form this run; a P2 re-run under the retention patch records it |
| **R-JB-171** | `jbearing` | cold MCP `path_syntax_error` (does not compile); presolve emit `$171 Domain violation for set` + `$257` | locate the domain-violating reference |
| **R-B-*** (one per model) | `glider`, `minsurf`, `robot`, `sroute`, `tricp` | `kkt_residual.py` **`case_b`** (emit bug), dual transfer consistent; worst stationarity row: `glider` `stat_cl(h0)` rel 2.0 · `minsurf` `stat_v(x39,y6)` rel 40.2 · `robot` `stat_step` rel 10.1 · `sroute` `stat_x(portland,chicago,boston)` rel 1.0 · `tricp` `stat_x(n1,k0)` rel 1.69 (the same value at every `n`) | trace the named stationarity row's terms. ⚠ `tricp`'s dual-transfer report has max equality residual **6.15e6** while marked consistent; check that first |
| **P3** | `airsp`, `msm` (translate timeout, 600 s); `emfl`, `indus89`, `phosdis` (parse failure) | unchanged from Task 2 | P3 grammar / translate-performance items |

**Counts:**
- **Unrouted fingerprints: 0.**
- **Meeting P10's rule today** (reproduced **and** a named fix surface): **2** (`egypt`, `shale`, via P4).
- **Banked for P2 diagnosis:** the remaining 9 non-match models with an MCP.
- **No residual verdict, because the harness itself fails on the presolve emit:** 6 (`egypt`, `ferts`, `jbearing`, `shale`, `srpchase`, `tabora`). `kkt_residual.py` evaluates the `--nlp-presolve` emit, so a presolve-emit defect blocks the verdict.

**Repeated-domain cross-tab** (Sprint 39 Unknown 6.2): the 7 flagged members were non-matches 6 of 7 times (`tfordy` matched); the 4 unflagged were non-matches 3 of 4 times (`turkey` matched). **The flag is not predictive at this size.**

## `ISSUE_933` (tricp) — triaged against a real compile (Unknown 2.4)

- **The issue's last recorded state** (2026-04-01): **10 compile errors** in the generated MCP: `$148` ×2 (`stat_r(n)` referencing `(n,n)` multipliers), `$149` ×6 (uncontrolled `i` in `stat_sln`/`stat_slp` conditions and `.fx` lines), and `$141`/`$257` cascading. *(Its title and opening sections still describe the older Sprint 21 translation timeout.)*
- **Now:**
  - the current golden is byte-identical to a HEAD re-emit;
  - it translates in 3.7 s;
  - its own retained listing has **0** compile-error markers;
  - PATH runs: `model_infeasible` (MS 5), retry also MS 5, `kkt_residual.py` `case_b` (`stat_x(n,k0)`).
- **Verdict: the compile errors no longer reproduce. Re-scope, don't close.** `tricp` is a solvable-but-wrong emit (R-B-tricp). The issue document is updated accordingly.

## Wall-clock (for Task 12's nightly sizing)

| phase | total | notes |
|---|---|---|
| MCP-gated batch (11 × `run_full_test.py --model`) | **763 s** | max `ferts` 184 s, `egypt` 156 s, `turkey` 174 s |
| NLP-gated convexity (9) | 22 s | max 7 s |
| NLP-gated pipeline (9) | 1,377 s | **1,206 s is two translate timeouts** (`airsp`, `msm`, 603 s each) |
| residuals (11) | 467 s | max `ferts` 138 s, `minsurf` 100 s |
| attribution exercise (3) | 106 s | `turkey`, `egypt`, `weapons` |

The **whole cohort pipeline, both populations, takes 2,162 s (~36 min)** including the two timeouts, or ~16 min without them. That fits a nightly slot comfortably. Solves capped at 120 s (`reslim`) never hit the cap: the longest cold solve was `minsurf`'s 33 s abort.

## Procedure and provenance

- **Worktree:** `git worktree add --detach <tmp> main` at `79eeccff`, which descends from `b44344a2`. Git-ignored raw sources copied in. The **retention patch** was applied from `artifacts/RETENTION_PATCH.md`, verbatim: tool blobs unchanged since `912d005c`. It reported exactly the four wrapped sites, plus one non-GAMS `subprocess.run` left in each of `kkt_residual.py` (gdxdump) and `check_mcp_solve_attribution.py` (the `src.cli` emit).
- **No fifth GAMS site is reachable:** `batch_translate.py::validate_mcp_file` (an `action=c` compile) is called only from `batch_translate.py`'s own CLI, never from `translate_single_model`; `src/validation/gams_check.py` is not imported by `src/cli.py`. **No `gams` was invoked directly.**
- **Phases:** `batch` (11 MCP-gated, then the 9 convex NLP-gated, the latter in the worktree's DB copy only), `convexity` (9), `residual` (every non-match with an MCP), `attribution` (`--workdir` inside the trap).
- **Two smoke runs on `trnsport` preceded the measurement**, to test the driver itself. They found two driver bugs (wall-clock capture; a missing `--json` path). Both ran at the same `79eeccff` and were discarded with their worktrees, and no Results value comes from them.
- **Associations:** every stage of every row matched **exactly one** retained invocation (1 candidate, 1 match), asserted by the generator that wrote the Results table.
- **Committed state:** `git diff main...HEAD -- scripts/ src/ data/` is empty. The patch, the worktree DB edits and the re-emits lived only in the worktree.
- **Not re-run:** `--only-solve` behaviour (Unknown 2.1 Q5) is answered from the code. With `nlp2mcp_translate.status == "success"` it solves the existing MCP without re-translating, whatever `solver_version` holds.
