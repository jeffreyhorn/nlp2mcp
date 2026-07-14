# Sprint 32 — Reusable-Tooling Readiness Audit + Backlog Fix-Surface Analysis (Priorities 6 + 7)

**Task:** Sprint 32 Prep Task 10
**Date:** 2026-07-14
**Owner:** Development team
**Scope:** audit only — read-only tool runs (the `kkt_residual.py` cohort sweep + a `--resolve-changed --dry-run` + a structural corpus grep); no `src/` change.

---

## Executive summary

Sprint 32's diagnostic tooling is **reused, not rebuilt** — this audit confirms, from read-only runs, that each of the five carryforward tracks inherits a tool that already guards its shape, with only **one new tool-code extension** (the P5 Case-c classifier in the diagnostic harness `scripts/diagnostics/kkt_residual.py`, designed in Task 7 — not a `src/` emit/runtime change) and **two new test fixtures** (P7). The Priority-6 fill/absorb-slack work is scoped here so Day-1 P6 is not an open-ended search: (a) a corpus structural audit surfaces the offset-alias generalization candidates beyond polygon/ps2 (chiefly **cpack**, a circle-packing distance sibling); (b) the `kkt_residual.py` sweep re-triages the four residual `model_infeasible` members — **fawley is a clean fixable Case-b / second-index candidate** (a convex LP with a uniform transpose-column residual), **agreste** a candidate-with-caveat (a convex LP but a double-solve driver), and **cesam + lnts genuine Case-c** (bilinear SAM / bilinear-`step` optimal-control non-convexity) banked for Sprint 33. The `--resolve-changed --since-commit 4cbf8bff` gate reports **GO (0 changed) at Day 0** (clean baseline), so it is the ready regression gate for every P6/P1/P2/P3 emit change.

---

## §1. Per-track tooling-readiness audit

All six reusable tools are present and confirmed on `main` (two exercised this task — the KKT-residual harness sweep + the `--resolve-changed` dry-run; the other four confirmed present):

| Tool | Path | Confirmed |
|---|---|---|
| KKT-residual harness | `scripts/diagnostics/kkt_residual.py` | ✅ ran on 4 cohort models this task |
| `--resolve-changed` checkpoint | `scripts/gamslib/run_full_test.py` (`--resolve-changed --since-commit --dry-run`) | ✅ GO dry-run at `4cbf8bff` |
| Golden-staleness gate | `scripts/sprint_audit/check_golden_staleness.py` | ✅ present |
| Presolve-divergence detector | `scripts/diagnostics/check_presolve_divergence.py` (+ `presolve_divergence_allowlist.txt`) | ✅ present |
| `--force` solution-forcing scaffold | `src/cli.py` (`--force`) | ✅ present |
| AD cross-term property catalog | `tests/integration/emit/test_ad_crossterm_shapes.py` (shapes 1–11) | ✅ present |

| Track | Guarding tool | Minimal extension for Sprint 32 |
|---|---|---|
| **P1 mine** (bound-multiplier 4th site) | `kkt_residual.py` — the warm-residual→0 (Case-a) verdict at the bound-active `stat_x` rows; the `--resolve-changed` golden-diff on `mine_mcp_presolve.gms` | **A bound-multiplier residual assertion** (the harness already reports `stat_x` Case-b→a; the new coverage is the P7 property fixture, §4) — **no harness code change**. |
| **P2 sarf** (4-D `stat_task` sparsification) | The translate-budget timer (`run_full_test.py --only-parse`/emit timing) + the golden-staleness gate on `sarf_mcp.gms` | **No tool change** — the O(active=398) timing probe uses the existing translate path; the golden-staleness gate catches the new `sarf_mcp.gms` (no golden today — sarf is `translate_failure`, so the first emit *creates* the golden). |
| **P3 camcge** (`stat_mps` + Walras) | `kkt_residual.py` — the CASE_B `stat_mps` verdict + the dual-transfer flag; the S1∧S2∧S3 detector logic (Task 5) | **No harness code change** for step 1 (the general `nu_mps_fx` emit fix); the S1∧S2∧S3 CGE-degeneracy detector is a *Task-5-designed* check run at the `/tmp` prototype (analysis, not tool code). |
| **P4 rocket** (PATH-consultation) | The `--force` scaffold (homotopy/multistart/optfile levers + PATH optfile emit) | **No tool change** — the scaffold landed Sprint 30; P4 consumes it to package the ruled-out-lever survey. |
| **P5 hhfair/CGE** (Case-c formalization) | `kkt_residual.py` — the CASE_B + D1(obj-defining)∧D3(cold-spurious) reclassification | **The one new tool-code extension** (in the diagnostic harness `scripts/diagnostics/kkt_residual.py`, **not** `src/`): the **Case-c auto-classifier** (Task 7 design) — a post-verdict reclassification pass, no emit change. |

**Conclusion:** no blocking tool gap. The only tool-code change is the P5 classifier (in the diagnostic harness `scripts/diagnostics/kkt_residual.py`, not `src/`; no emit change); everything else is a reuse + the two P7 fixtures (§4).

---

## §2. P6 offset-alias generalization candidate list (Unknown 6.1)

The Sprint-31 #1111/#1112 second-index-transpose core (`_var_at_two_indices_complement` / `_build_complement_index_sum`, `stationarity.py`) landed for **polygon + ps2_f_s + ps2_s + ps3_s_gic**. A structural corpus grep for the var-at-two-indices distance/norm shape (`sqr(x(i)−x(j))` / `sum(j, …(i)…(j))`) surfaces the adjacent-candidate set:

| Candidate | Shape | Prior (genuine-floor gain?) |
|---|---|---|
| **cpack** | circle-packing pairwise distance `sqr(x(i)−x(j))+sqr(y(i)−y(j))` — the **direct polygon sibling** | **Highest** — the same single-constraint second-index transpose the core targets |
| **ps3_s_scp / ps5_s_mn / ps10_s_mn** | ps-family siblings of the landed ps2/ps3 | Medium — same generator family; likely already-correct or a small delta |
| **partssupply** | 2-index coupling; needs the cold-emit check to confirm the transpose shape | Medium |
| **maxcut** | quadratic 2-index; may be a different (symmetric-matrix) shape | Low–Medium |
| irscge / lrgcge / moncge / camcge | CGE 2-index — but these are the **P5 Case-c family** (non-convex, 0 floor) | Excluded (Case-c) |
| himmel16 | documented non-convex (S30 Day 7) | Excluded |

**`--resolve-changed` GO gate (Unknown 6.3):** each candidate's Day-1 cold-emit diff must (a) change the cold `*_mcp.gms` (a real cross-term correction, not a no-op) and (b) pass `run_full_test.py --resolve-changed --since-commit 4cbf8bff` with **no changed golden moving backward** across the 92 matches / 107 solves. **The per-candidate emit-diff + GO check is Day-1 P6 work** (this task seeds the list; it does not run the 219-model emit sweep). If the core is polygon/ps2-specific (no candidate corrected), P6 falls back to the §3 failure-cohort re-triage — **fawley** is the strongest fallback +Solve.

---

## §3. P6 failure-cohort re-triage (Unknown 6.2)

`kkt_residual.py` sweep on the four residual `model_infeasible` members (`--tol 0.001`, dual-transfer CONSISTENT on all four):

| Model | Solve type | Verdict | Max-residual row | Re-triage |
|---|---|---|---|---|
| **fawley** | LP (convex) | CASE_B | `stat_bq(*,fuel-oil)` rel **0.973** (uniform across the whole `fuel-oil` column) | **Fixable Case-b / P6 second-index candidate** — the highest-confidence cohort +Solve. `bq(c,cfq)` is summed over `cfq` in `cbal` and over `c` in `qsb`/`pbal`; the uniform transpose-column residual is a clean single-dropped-cross-term on a **convex LP**. |
| **agreste** | LP (convex), **double-solve** | CASE_B | `stat_sales(sugar-cane)` rel **2.00** | **Candidate fixable Case-b with a scope caveat** — rel exactly 2.0 on a convex LP (a factor-of-2 / dropped `stat_sales` gradient term) is a genuine emit bug, BUT agreste has **two `solve … maximizing yfarm using lp`** statements (a scenario driver) — verify scope (cf. the danwolfe/decomp/saras multi-solve allowlist) before committing a fix. |
| **cesam** | NLP+MCP+NLP (multi-solve driver) | CASE_B | `stat_tsam(GIN,GRE)` rel **1.02** (dispersed across the `GRE` column) | **Genuine Case-c (bilinear SAM) / out-of-scope driver** — `TSAM(ii,jj) =e= A(ii,jj)·(X(jj)+ERR1(jj))` is bilinear (cross-entropy SAM balancing); the dispersed near-1.0 column residual is the bilinear non-convexity, and cesam already embeds its own `solve … using mcp` (line 595). Banked Case-c for Sprint 33; likely out of scope. |
| **lnts** | NLP | CASE_B | `stat_step` rel **9.66** (interior `stat_y` near tol ~0.008) | **Genuine Case-c (rocket-family)** — `tf =e= step·nh` and `y(c,h+1) = y(c,h) + 0.5·step·(…)` make `step` multiply every dynamics row (a brachistochrone minimum-time optimal-control model); the `stat_step` boundary residual with a near-tolerance interior is the same bilinear-coupling Case-c signature as rocket. Banked for the Sprint-33 forcing/PATH work. |

**Net:** **2 candidate Case-b +Solve** (fawley clean; agreste scope-caveated) + **2 genuine Case-c** (cesam bilinear-SAM, lnts bilinear-`step`) banked for Sprint 33. fawley is the strongest single P6 +Solve, and it overlaps the §2 second-index family — so P6's offset-alias and cohort tracks converge on the second-index cross-term as the highest-leverage fix surface.

---

## §4. P7 infrastructure groundwork (Unknowns 7.1, 7.3)

**Property-catalog fixtures (Unknown 7.1).** The catalog `tests/integration/emit/test_ad_crossterm_shapes.py` holds shapes 1–11 (shape10 `distance_second_index` + shape11 `second_index_indexed_condition` = the polygon #1111/#1112 family). Two fixtures to add **once P1/P2 land** (fail-before / pass-after guards):

- **shape12 — head-offset 4th-site bound-multiplier** (mine): a minimal `EquationDef.head_domain_offsets` model whose `--nlp-presolve` emit sets `piL_x/piU_x` from the stationarity residual `N` (not `x.m`); assert `stat_x` closes at a bound-active row. Guards the P1 emit.
- **shape13 — sarf 4-D `task` sparsification**: a minimal 2-D dynamic-subset model; assert the emitted `stat_task$taskposs` is the symbolic guarded form (O(active), no set-name-literal indices). Guards the P2 emit.

**Genuine-floor-tracking recompute (Unknown 7.2 — cross-checked with Task 2).** The footnote-⁸ ramp (S31 74 → **S32 ≥ 75** → S33 maintain ≥ 75 → S34 ≥ 77 → S35 ≥ 78) is set; the genuine floor 74 reproduces as the Day-0 anchor (Task 2 / `BASELINE_METRICS.md`). The S32 ≥ 75 step is conditional on mine [P1] + camcge [P3] cold-matching (per Task 9), plus any P6 §2/§3 genuine-floor gain (fawley/cpack). The 142-corpus vs all-219 scope carries through the recompute.

**Checkpoint coverage (Unknown 7.3).** `run_full_test.py --resolve-changed --since-commit 4cbf8bff --dry-run` reports **`GO: no emit goldens changed since 4cbf8bff`** — 0 selected at Day 0 (clean baseline; `4cbf8bff` confirmed an ancestor of `main`, the S31-close SHA). The gate selects a model the moment its emit golden changes, so the Day-5/Day-10 checkpoints re-solve exactly the touched set (mine `_mcp_presolve.gms`, camcge `_mcp.gms`, any P6 candidate). **Note:** sarf has **no golden today** (`translate_failure`), so the P2 emit *creates* `sarf_mcp.gms` — its first appearance is caught by the golden-staleness gate (a new golden), not by `--resolve-changed` (which diffs *existing* goldens); this is the one checkpoint-coverage nuance for Sprint 32.

**Epic-4 `SUMMARY.md` skeleton (P7 groundwork, S30-retro §5 front-loading).** A sprint-by-sprint history stub to seed during Sprint 32: one row per Sprint 18–35 with {headline KPI deltas, the firm landed track, the REPLAN'd tracks + their carryforward filing}; anchored on the closed-sprint record (S27 Match 62→ … → S31 Match 92 / genuine floor 74). Deliverable is the skeleton, not the full history (that is the Epic-4-close task).

---

## §5. Known-Unknowns dispositions

| # | Unknown | Disposition |
|---|---|---|
| 6.1 | Does the #1111/#1112 core generalize beyond polygon/ps2? | ✅ VERIFIED (candidate list) — the structural audit surfaces **cpack** (circle-packing distance sibling, highest prior) + ps3_s_scp/ps5_s_mn/ps10_s_mn/partssupply; the CGE cluster + himmel16 are excluded (Case-c / non-convex). The per-candidate cold-emit diff + GO check is Day-1 P6 work; if none corrects, §3 fawley is the fallback. |
| 6.2 | Do any `model_infeasible` cohort members re-triage to a fixable Case-b? | ✅ VERIFIED (harness sweep) — **fawley** = clean fixable Case-b (convex LP, uniform transpose-column `stat_bq(*,fuel-oil)` rel 0.973); **agreste** = candidate Case-b with a double-solve scope caveat (rel 2.0 on a convex LP); **cesam** = Case-c (bilinear SAM) / driver; **lnts** = Case-c (bilinear `step` optimal-control, rocket-family). 2 candidate +Solve + 2 banked Case-c. |
| 6.3 | Does any P6 candidate pass the `--resolve-changed` GO gate? | ✅ VERIFIED (gate ready) — `--resolve-changed --since-commit 4cbf8bff --dry-run` = GO (0 changed at Day 0); the gate is the Day-1 per-candidate blast-radius check (no changed golden moves backward across 92 matches / 107 solves). |
| 7.1 | Do the new property fixtures guard P1/P2? | ✅ VERIFIED (design) — shape12 (head-offset 4th-site) + shape13 (sarf 4-D `task`) extend the shapes-1–11 catalog; fail-before/pass-after, added once P1/P2 land. |
| 7.3 | Do the `--resolve-changed` targets cover the newly-touched emit sites? | ✅ VERIFIED — the gate selects mine/camcge goldens on emit change (GO at Day 0); the one nuance is sarf's *new* golden (caught by the golden-staleness gate, since `--resolve-changed` diffs existing goldens). Anchor `4cbf8bff`. |

**Decision: no blocking tool gap for Sprint 32.** The tooling is reuse + the single P5 classifier extension + the two P7 fixtures. P6 has a scoped fix-surface: the §2 offset-alias candidates (cpack-led) and the §3 fawley Case-b converge on the second-index cross-term; cesam/lnts bank as Case-c for Sprint 33.

---

**Document Created:** 2026-07-14
**Owner:** Sprint 32 Planning Team
**Evidence:** the `kkt_residual.py` sweep on agreste/cesam/fawley/lnts (verdicts + max-residual rows above), the `run_full_test.py --resolve-changed --since-commit 4cbf8bff --dry-run` GO output, the structural corpus grep (polygon-family distance shape), and the `test_ad_crossterm_shapes.py` shape-1–11 catalog. The raw model `.gms` under `data/gamslib/raw/` are fetched via `gamslib <name>` and are **not** checked into the repo (per the corpus convention); the harness runs against the local raw corpus.
