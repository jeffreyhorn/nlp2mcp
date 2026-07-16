# Sprint 33 — Reusable-Tooling Readiness Audit + Backlog Fix-Surface Analysis (Priorities 6 + 7)

**Task:** Sprint 33 Prep Task 10
**Date:** 2026-07-16
**Owner:** Development team
**Scope:** audit only — read-only tool runs (a `--resolve-changed --dry-run` at the S32-close anchor, a source-scope grep of the P6 cohort, a DB `outcome_category` sweep, and a property-catalog inventory); no `src/` change.

---

## Executive summary

Sprint 33's diagnostic tooling is **reused, not rebuilt** — and this sprint it is a **pure** reuse: the one Sprint-32 tool-code extension (the P5 `case_c_objdef` classifier) **landed on `main`**, so Sprint 33 adds **zero new diagnostic-tool code** and only **three P7 test fixtures** (shape12/shape13 + a fawley 2-D second-index fixture, each gated on P1/P2/P3 landing). All six reusable tools are confirmed present, and the checkpoint gate is ready: `run_full_test.py --resolve-changed --since-commit ee51ed9e --dry-run` reports **GO (no emit goldens changed)** at Day 0 (`ee51ed9e` confirmed an ancestor of `main`). The Priority-6 fill/absorb-slack work is pre-scoped so Day-6+ P6 is a plan, not a cold survey: (a) the **offset-alias generalization is exhausted** (S32 Day-11 re-triage found cpack et al. already solve, CASE_A no-op — fawley, the one genuine second-index bug, was **promoted to P3**), so P6 is the **failure-cohort re-triage**; (b) the cohort splits cleanly — **agreste is a double-`solve` scope caveat** (two `solve … using lp` at lines 294/298 — verify scope BEFORE treating the CASE_B `stat_sales` as an emit bug), **cesam + lnts are genuine Case-c** (bilinear SAM / bilinear-`step` optimal control, confirmed from source), and a **distinct 8-member `path_syntax_error` cohort** (all convex/likely-convex — clearlak/dinam/ganges/gangesx/indus/sample/turkey/turkpow) is a translate-*syntax* fix-surface separate from the emit-correctness bugs. Every P6 candidate is `--resolve-changed`-gated. No blocking tool gap.

---

## §1. Per-track tooling-readiness audit (Unknown 6.1 tooling-layer)

All six reusable tools confirmed present on `main` (two exercised this task — the `--resolve-changed` dry-run + the DB/source sweep; the other four confirmed present):

| Tool | Path | Confirmed |
|---|---|---|
| KKT-residual harness (incl. `case_c_objdef`) | `scripts/diagnostics/kkt_residual.py` | ✅ present; `reclassify_objdef_case_c` landed (S32) |
| `--resolve-changed` checkpoint | `scripts/gamslib/run_full_test.py` (`--resolve-changed --since-commit --dry-run`) | ✅ **GO dry-run at `ee51ed9e`** this task |
| Golden-staleness gate | `scripts/sprint_audit/check_golden_staleness.py` | ✅ present |
| Presolve-divergence detector | `scripts/diagnostics/check_presolve_divergence.py` | ✅ present |
| `--force` solution-forcing scaffold | `src/cli.py` (`--force`) | ✅ present |
| AD cross-term property catalog | `tests/integration/emit/test_ad_crossterm_shapes.py` (shapes 1–11) | ✅ present |

| Track | Guarding tool | New tool code for Sprint 33 |
|---|---|---|
| **P1 mine** (head-offset bound-active cross-term) | `kkt_residual.py` — the warm-residual→0 (Case-a) verdict at the 6 bound-active `stat_x` rows; `--resolve-changed` golden-diff on `mine_mcp_presolve.gms` | **None** — the harness already reports the `stat_x` Case-b/Case-a verdict + the CONSISTENT dual flag; the new coverage is the **P7 shape12 fixture** (§4). |
| **P2 sarf** (three-site symbolic `stat_task` emit) | The translate-budget timer (`run_full_test.py` emit timing) + the golden-staleness gate on `sarf_mcp.gms` | **None** — the O(active=398) timing probe uses the existing translate path; sarf has **no golden today** (`translate_failure`), so the first emit *creates* `sarf_mcp.gms` (caught by the golden-staleness gate, §4). New coverage = the **P7 shape13 fixture**. |
| **P3 fawley** (second-index `sameas`-guard generalization) | `kkt_residual.py` — the CASE_B `stat_bq` verdict + <code>max&#124;stat_bq&#124;</code> residual; `--resolve-changed` on `fawley_mcp_presolve.gms` | **None** — the harness scores the H-a/H-b split (residual→0 vs MS-5); new coverage = the **P7 fawley 2-D second-index fixture** (§4). |
| **P4 camcge** (Epic-5 dual-consistent Walras) | `kkt_residual.py` (CASE_B `stat_mps` + dual flag) + the S1∧S2∧S3 detector logic (Task 6, analysis) | **None** — Epic-5-deferred; step 1 landed S32. The `case_c_objdef`/degeneracy logic is analysis at the `/tmp` prototype, not tool code. |
| **P5 rocket/Case-c** (forcing survey) | `kkt_residual.py` (`case_c_objdef`) + the `--force` scaffold (homotopy/multistart/optfile) | **None** — the `case_c_objdef` classifier **landed S32**; P5 consumes it + the scaffold. |

**Conclusion:** **zero new diagnostic-tool code for Sprint 33** — a pure reuse (the S32 `case_c_objdef` extension is now on `main`). The only new test artifacts are the three P7 fixtures (§4). No blocking tool gap.

---

## §2. P6 failure-cohort re-triage (Unknowns 6.1, 6.2)

**Context: the offset-alias generalization is exhausted.** The Sprint-31 #1111/#1112 1-D second-index-transpose core landed for polygon + ps2/ps3; the Sprint-32 Day-11 structural-candidate re-triage found the adjacent set (**cpack** et al.) **already solves** (CASE_A — the landed core covers it, a no-op), and the one genuine remaining second-index bug (**fawley**, the 2-D `qsb`/`pbal` `sameas` gap) was **promoted to a headline track (P3)**. So Sprint 33's P6 is **not** an offset-alias candidate sweep — it is the residual-`model_infeasible` / failure-cohort re-triage below.

**The `model_infeasible` cohort (source-scope + banked-harness re-confirm):**

| Model | Solve scope | Verdict | Signature (confirmed this task) | Re-triage |
|---|---|---|---|---|
| **agreste** | LP (convex), **double-`solve`** | CASE_B (scope-caveated) | **two** `solve agreste maximizing yfarm using lp` (lines 294 + 298) — a scenario driver; the CASE_B `stat_sales` rel 2.0 may be a double-solve scope artifact, not an emit bug | **Verify scope BEFORE any fix** (the multi-solve-gate lesson — cf. danwolfe/decomp/saras). If the single-solve scope holds CASE_B, it is a factor-of-2 dropped-gradient Case-b (+Solve candidate); if it is a driver artifact, **bank** (not a fixable emit bug). `--resolve-changed`-gated. |
| **cesam** | NLP + **embedded MCP** + NLP (3 solves) | Case-c (bilinear SAM) | `TSAM(ii,jj) =e= A(ii,jj)*(X(jj)+ERR1(jj))` (bilinear, line 362) + the cross-entropy `log` objective; embeds its own `solve m_SAMENTROP using mcp` (line 595) | **Genuine Case-c / out-of-scope driver** — the bilinear SAM balancing is the non-convexity; banked (joins the forcing cohort, not the emit-fix cohort). |
| **lnts** | NLP (single solve) | Case-c (bilinear-`step`) | `tf =e= step*nh` (line 57) + `y(c,h+1) =e= y(c,h) + 0.5*step*(…)` (lines 59/61/63) — `step` multiplies every dynamics row (brachistochrone min-time optimal control) | **Genuine Case-c (rocket-family)** — the bilinear-`step` coupling is the same signature as rocket; banked for the P5 forcing/PATH work. |

**The `path_syntax_error` cohort (a distinct P6 fix-surface, DB sweep this task):** **8 convex/likely-convex** models whose *emitted* MCP fails at the PATH **compile** stage (`outcome_category: path_syntax_error`, "Parse error: compilation_error") — **clearlak**, **dinam**, **ganges**, **gangesx**, **indus**, **sample**, **turkey**, **turkpow**. These are **not** Case-c (all convex) and **not** Case-b emit-correctness bugs — they are a **translate-syntax** defect (the emit produces a GAMS construct PATH won't compile), likely sharing a small common root across the large sectoral/agricultural models. **Bonus P6 back-half candidate:** a single translate-syntax fix could recover several at once; each `--resolve-changed`-gated + a golden-staleness check on the new goldens. (Caveat: several — ganges/indus/turkey/dinam — are large sectoral models; scope the shared syntax root before committing.)

**Net P6 fix-surface:** agreste (scope-verify → conditional +Solve) + the `path_syntax_error` 8-cohort (a shared translate-syntax root, bonus back-half) — **each `--resolve-changed`-gated**; cesam + lnts **bank as Case-c**.

---

## §3. P6 adjacent unlock — the sarf/srpchase symbolic-emit family (Unknown 6.3)

The P2 sarf three-site symbolic `stat_task$taskposs` subsystem generalizes to any model sharing the **active-subset dynamic-guard emit shape** (`$taskposs`-style `subset(i,j) ∧ tech(m,n)` restriction over a Cartesian product). **srpchase** is the confirmed 1-D analogue (it already translates — ~2.9s current runner / 6.56s S32 runner — and is the P2 O(active) timing reference), so it is **not** itself an unlock; the unlock is any *currently-failing* model with the same 2-D+ dynamic-subset blow-up.

**Plan (Day-6+ after P2 lands, not this docs task):** scan the `translate_failure` cohort for the sarf `$taskposs`-active shape (a Cartesian product guarded by a dynamic subset intersection); for each match, re-emit with the P2 subsystem and gate on `run_full_test.py --resolve-changed --since-commit ee51ed9e` GO + a byte-stable new golden. **Prior: Low–Medium** — the shape is specific (few models carry a 369K-scale dynamic-subset product), so the realistic outcome is 0–1 follow-ons; any unlock is bonus back-half scope, not a firm KPI. If none matches, the P2 subsystem is sarf-specific (acceptable — re-scoped, documented).

---

## §4. P7 infrastructure groundwork (Unknowns 7.1, 7.3)

**Property-catalog fixtures (Unknown 7.1).** The catalog `tests/integration/emit/test_ad_crossterm_shapes.py` holds **shapes 1–11** (shape10 `distance_second_index` + shape11 `second_index_indexed_condition` = the **1-D** polygon #1111/#1112 family). Three fixtures to add — each **fail-before / pass-after**, authored against the Day-0 emit and landing **only once** the corresponding fix lands (the Sprint-28 property-catalog lesson: a fixture that passes on the old emit guards nothing):

- **shape12 — head-offset bound-active cross-term** (guards P1): a minimal `EquationDef.head_domain_offsets` model whose `--nlp-presolve` emit keys `comp_pr`/`lam_pr` + the `stat_x` cross-term to the **head label `(k,l+1,i,j)`** (the H1 multiplier-keying); assert `stat_x` closes (`N → 0`) at a bound-active row and is unchanged at an interior row. **Fail-before:** the Day-0 emit leaves the wrong-sign `N` at the bound-active row. Lands once P1 lands (H1).
- **shape13 — sarf symbolic `stat_task`** (guards P2): a minimal 2-D dynamic-subset model; assert the emitted `stat_task$taskposs` is the symbolic guarded form (O(active), the banked 7-term shape, **no set-name-literal multiplier indices**) + `task.fx$(not active) = 0`. **Fail-before:** the Day-0 emit either times out (369K enumeration) or emits set-name literals. Lands once P2 lands.
- **fawley 2-D second-index** (guards P3 — a **new** shape, distinct from the 1-D shape10/11): a minimal model with a variable's-**second-index-summed** cross-term (`bq(c,cf)` in `qsb(cfq,l,s)`/`pbal(cfq,m)`); assert the `$(sameas(cfq__,cf))` restriction fires on **every** second-index `cfq` (covering the qsb/pbal shape, not just mbal). **Fail-before:** the Day-0 emit over-sums (the 96%-residual). Lands once P3 lands (H-a or the genuine cross-term correction under H-b).

All three are **property-based** (the cross-term shape), not model-specific, and extend the shapes-1–11 catalog cleanly.

**Genuine-floor-tracking recompute (Unknown 7.2 cross-check — Task 2).** The genuine floor **re-baselines to 74** at Sprint-33 Day 0 (Sprint 32 closed flat at 74; the S32 footnote-⁸ ≥75 projection was missed — the honest anchor is 74, per `BASELINE_METRICS.md`). Any Sprint-33 floor +1 is conditional on P1 [H1 cold-match] **or** P3 [the genuine cross-term correction, which lands even under H-b] (Task 9); P5 delivers **0** floor. The 142-convex-corpus vs all-219 scope (all-219 Match 95) carries through the recompute; the recompute runs at Sprint-33 close after any emit lands.

**Checkpoint coverage (Unknown 7.3 cross-check).** `--resolve-changed --since-commit ee51ed9e --dry-run` = **GO (0 changed)** at Day 0 (this task); the gate selects a model the moment its `_mcp*.gms` golden changes, so the Day-5/Day-10 checkpoints re-solve exactly the touched set (mine `_mcp_presolve.gms`, fawley `_mcp_presolve.gms`, any P6 candidate). **The sarf nuance persists:** sarf has **no golden today** (`translate_failure`), so the P2 emit *creates* `sarf_mcp.gms` — its first appearance is caught by the **golden-staleness gate** (a new golden), not by `--resolve-changed` (which diffs *existing* goldens). Anchor **`ee51ed9e`** (the Day-0 code anchor; distinct from `4cbf8bff`, the DB byte-anchor).

**Epic-4 `SUMMARY.md` row-33 continuation (Unknown 7.3).** The skeleton (one row per Sprint 18–36) is on `main`; the Sprint-33 row is `| 33 | 31–32 | PATH author consultation & solution forcing | (planned) | — | — |`. **Two continuation items at Sprint-33 close (a Day-12 task, mirroring Sprint 32's):** (1) **reconcile the theme cell** — "PATH author consultation & solution forcing" is **Sprint 34's** theme (the renumbered PATH-consultation sprint); Sprint 33's theme is "Sprint 32 REPLAN'd carryforwards (mine/sarf/fawley/camcge/rocket)"; (2) **fill the cells** in the rows-28–32 format — {Theme / Headline KPIs (Solve/Match/floor at close) / Firm landing(s) / REPLAN'd → carryforward}. The row backfill is a Day-12 continuation, scheduled in the Task-11 plan (not this docs-only prep).

---

## §5. Known-Unknowns dispositions

| # | Unknown | Disposition |
|---|---|---|
| 6.1 | Is agreste genuinely CASE_B or a double-`solve` scope artifact? | ✅ VERIFIED — agreste has **two** `solve agreste maximizing yfarm using lp` (lines 294 + 298), a scenario driver. The CASE_B `stat_sales` rel 2.0 **must be scope-verified BEFORE any fix** (the multi-solve-gate lesson); if the single-solve scope holds CASE_B it is a factor-of-2 dropped-gradient Case-b (+Solve candidate), else banked as a driver artifact. `--resolve-changed`-gated. |
| 6.2 | Are cesam and lnts confirmed Case-c (non-convex, forcing-only)? | ✅ VERIFIED — **cesam** = bilinear SAM (`TSAM =e= A·(X+ERR1)`, line 362) + embedded MCP (line 595) → Case-c; **lnts** = bilinear-`step` (`tf =e= step·nh` + `0.5·step·(…)`, lines 57/59) → Case-c (rocket-family). Both bank to the forcing cohort, not the emit-fix cohort. No emit defect masquerading as non-convexity. |
| 6.3 | Do the P1/P2/P3 fixes unlock adjacent backlog (the srpchase/sarf symbolic-emit family)? | ✅ VERIFIED (plan) — the P2 subsystem generalizes to any `$taskposs`-active dynamic-subset-product shape; srpchase is the *reference* (already translates), not an unlock. The Day-6+ plan scans the `translate_failure` cohort for the same shape, each `--resolve-changed`-gated. **Prior Low–Medium** (0–1 follow-ons); bonus back-half, not a firm KPI. |
| 7.1 | Do the shape12/shape13/fawley property fixtures fail-before/pass-after only once P1/P2/P3 land? | ✅ VERIFIED (design) — shape12 (head-offset bound-active, guards P1), shape13 (sarf symbolic `stat_task`, guards P2), and a **new** fawley 2-D second-index fixture (guards P3, distinct from the 1-D shape10/11) each fail on the Day-0 emit and pass only after the fix; property-based; extend the shapes-1–11 catalog. Land only once P1/P2/P3 land. |
| 7.3 | What is the Epic-4 `SUMMARY.md` row-33 continuation scope? | ✅ VERIFIED — row 33 (`(planned)`) needs (1) a **theme reconciliation** ("PATH author consultation" is Sprint 34's theme; Sprint 33 = "S32 REPLAN'd carryforwards") + (2) the cells filled in the rows-28–32 format {Theme / KPIs / Firm landing(s) / REPLAN'd → carryforward}. A Day-12 close continuation (mirroring S32), scheduled in Task 11. |

**Decision: no blocking tool gap for Sprint 33 — a pure tool reuse** (the S32 `case_c_objdef` extension is on `main`; zero new diagnostic-tool code) + the three P7 fixtures. **P6 fix-surface:** agreste (scope-verify → conditional +Solve) + the 8-member `path_syntax_error` translate-syntax cohort (bonus back-half, shared root) — each `--resolve-changed`-gated; cesam/lnts bank as Case-c; the sarf/srpchase symbolic-emit unlock is a Low–Medium Day-6+ scan. **P7:** the three fail-before/pass-after fixtures (gated on P1/P2/P3), the genuine-floor recompute (anchor 74), and the SUMMARY row-33 Day-12 continuation.

---

**Document Created:** 2026-07-16
**Owner:** Sprint 33 Planning Team
**Evidence:** the `run_full_test.py --resolve-changed --since-commit ee51ed9e --dry-run` GO output (+ `git merge-base --is-ancestor ee51ed9e HEAD`), the source-scope grep of agreste/cesam/lnts (`solve` counts + the bilinear signatures above), the DB `outcome_category` sweep (the 8-member `path_syntax_error` cohort with convexity), and the `test_ad_crossterm_shapes.py` shape-1–11 inventory. The raw model `.gms` under `data/gamslib/raw/` are fetched via `gamslib <name>` and are **not** checked into the repo (per the corpus convention); this audit ran against the local raw corpus.
