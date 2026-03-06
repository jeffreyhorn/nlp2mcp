# model_infeasible Triage (Sprint 22 Prep Task 4)

**Created:** 2026-03-06
**Sprint:** 22 (Prep Task 4)
**Status:** Complete — ready for Sprint 22 fix design (Task 7)
**Data Source:** `data/gamslib/gamslib_status.json` working-tree version (12 models committed as `model_infeasible` + 3 additional from local pipeline reruns: ibm1 reclassified from `model_optimal`, twocge from `path_syntax_error`, feasopt1 newly classified). Committed version has 12; working-tree has 15. All 15 were verified by direct GAMS execution.
**Error verification:** GAMS v53 using on-disk MCP files

---

## 1. Executive Summary

The model_infeasible category contains **15 models** (12 in committed `gamslib_status.json` + 3 from local pipeline reruns — see Data Source), all with SOLVER STATUS 1 (Normal Completion). PATH completed its algorithm in every case — the infeasibility is in the MCP system itself, not a solver failure.

Sprint 22 targets model_infeasible **≤ 12** (−3 models). Analysis shows the 15 models break into four classification categories:

| Category | Count | Models | Fixable? |
|----------|-------|--------|----------|
| **A: KKT construction bug** | 4 | ibm1, mexss, uimp, whouse | YES — fix in KKT builder/emitter |
| **B: Nonconvex NLP / starting point** | 5 | bearing, chain, cpack, mathopt3, rocket | MAYBE — warm-start or formulation fixes |
| **C: Model type incompatible** | 4 | feasopt1, iobalance, meanvar, orani | NO — fundamental MCP limitations |
| **D: CGE / complex structure** | 2 | lnts, twocge | MAYBE — requires deeper investigation |

**Sprint 22 target is achievable:** Fixing the 4 Category A models (ibm1, mexss, uimp, whouse) meets the −3 target with margin. These have clear, documented KKT construction bugs.

### Sub-status Breakdown

Based on direct GAMS v53 execution of all 15 on-disk MCP files:

| MODEL STATUS | Count | Meaning | Models |
|-------------|-------|---------|--------|
| **4 (Infeasible)** | 3 | Structural infeasibility detected at preprocessing | ibm1*, uimp, whouse |
| **5 (Locally Infeasible)** | 12 | PATH converged but could not satisfy complementarity | all others |

*ibm1 is `model_optimal` in committed `gamslib_status.json` but `model_infeasible` when re-run with current on-disk MCP file.

---

## 2. Per-Model Classification

### Category A: KKT Construction Bug (4 models)

These models have identifiable bugs in the KKT stationarity equations, bound multiplier handling, or equation conditioning. Fixing the bug should make the MCP feasible.

#### whouse — Incorrect equation conditioning breaks stationarity

**MODEL STATUS:** 4 (Infeasible — detected at preprocessing)
**PATH output:** `Force Row Zero Infeasible stat_sell('q-1')`
**Iterations:** 0 (preprocessing detection)
**Issue doc:** None

**Root cause:** The stock balance equation `sb(t)` is incorrectly conditioned on `ord(t) > 1` in the MCP, causing `nu_sb('q-1')` to be fixed at 0. In the original model, `sb` is defined for ALL `t` — GAMS handles `stock(t-1)` at `t='q-1'` by using the default value 0. With `nu_sb('q-1') = 0`, the stationarity equation `stat_sell('q-1')` becomes `-price('q-1') - piL_sell('q-1') = 0`, requiring `piL_sell = -10` — impossible since `piL_sell >= 0`.

**Fix:** Remove the `$(ord(t) > 1)` condition from `sb` in the MCP, or correctly handle lag references (`stock(t-1)`) at the first time period. This is a translator/emitter bug in how lag expressions are conditioned.
**Effort:** 1-2h
**Priority:** HIGH — simplest LP model (45 lines GAMS), ideal diagnostic baseline

#### ibm1 — Missing bound multiplier terms in stationarity

**Note:** Committed `gamslib_status.json` shows ibm1 as `model_optimal`. Local pipeline rerun with current MCP file produces `model_infeasible` (MODEL STATUS 4). The committed result reflects an older MCP file; the current on-disk MCP file was re-generated after Sprint 21 changes.

**MODEL STATUS:** 4 (Infeasible — detected at preprocessing)
**PATH output:** `Inequality: infeasible 1.5000e+03 0.0000e+00 1.0000e+20` (bounds conflict)
**Iterations:** 0 (preprocessing detection)
**Issue doc:** #828 (`docs/issues/ISSUE_828_ibm1-locally-infeasible-stationarity.md`)

**Root cause:** Stationarity equations `stat_x(s)` have nonzero constant terms (`-0.03`, `-0.08`, `-0.17`) from objective gradient coefficients that should be balanced by bound multiplier terms (`piL_x`, `piU_x`). These multiplier terms are missing. The issue is in how parameter-assigned bounds (`x.up(s) = sup(s,"inventory")`) interact with the bound multiplier generation: the mixed uniform/non-uniform bounds case (uniform `lo=0`, non-uniform `up` with some infinite entries) is not handled correctly.
**Fix:** Fix bound multiplier generation for the mixed uniform/non-uniform case in `partition.py` and `stationarity.py`.
**Effort:** 2-3h
**Priority:** HIGH — well-documented root cause in Issue #828

#### uimp — Duplicate row / structural infeasibility

**MODEL STATUS:** 4 (Infeasible — detected at preprocessing)
**PATH output:** `DuplicateRow Upper Infinite Value stat_z(summer,nuts)` (structural infeasibility)
**Iterations:** 0 (preprocessing detection)
**Issue doc:** None

**Root cause:** The original model has two solve statements (`lp max revenue`, then `lp max profit`) using the same model but different objectives. The MCP translator merges or incorrectly handles the multi-solve pattern, producing duplicate rows or stationarity equations derived from the wrong objective. The `stat_z` equation references `summer,nuts` — domain indices from the production variables, suggesting the stationarity is being generated for the wrong model/objective combination.
**Fix:** Correct multi-solve handling — derive KKT from the last (or correct) solve statement, not a merged model.
**Effort:** 2-3h (depends on multi-solve infrastructure)
**Priority:** MEDIUM — multi-solve is a broader pattern (also affects iobalance, meanvar)

#### mexss — Incorrect `sameas` guard restricts multiplier terms to single instance

**MODEL STATUS:** 5 (Locally Infeasible)
**PATH output:** Residual 1.0, stuck on `stat_phipsi` (171 iterations, 3 restarts)
**Issue doc:** #764 (`docs/issues/ISSUE_764_mexss-mcp-locally-infeasible-accounting-variables.md`)

**Root cause:** The `sameas` guard in `_add_indexed_jacobian_terms()` in `src/kkt/stationarity.py` incorrectly restricts scalar-constraint multiplier terms to a single variable instance. For example, the scalar equation `alam` sums over `e(cf,i)` for ALL 5 valid `(cf,i)` combinations, but the guard uses `entries[0]` (only `('steel','ahmsa')`) to build the `sameas` condition, ignoring the other 4 valid instances. This produces stationarity equations that are too restrictive — multiplier terms contribute to only one instance when they should contribute to all valid instances.

Note: The initial analysis suspected accounting variable stationarity (`stat_phieps: -1 = 0`) as the root cause, but investigation showed those equations ARE individually satisfiable. The real problem is the `sameas` guard on indexed variable stationarity equations.
**Fix:** Refactor the `sameas` guard to handle multi-entry Jacobian patterns — use subset conditions (`$(cf(c))`) when entries match a named subset, or `or`-disjunction of `sameas` calls for arbitrary entries.
**Effort:** 3-4h (non-trivial refactor; see Issue #764 investigation section)
**Priority:** MEDIUM — fix has broader applicability beyond mexss

### Category B: Nonconvex NLP / Starting Point (5 models)

PATH ran to completion but could not find a feasible complementarity solution. The MCP formulation appears structurally correct; the issue is non-convexity making the KKT system hard to solve from the default starting point.

#### bearing — Strongly nonconvex engineering design

**MODEL STATUS:** 5 (Locally Infeasible)
**PATH output:** Residual 1.85e+04, 189 iterations, 3 restarts
**Issue doc:** #757 (`docs/issues/ISSUE_757_bearing-mcp-locally-infeasible.md`)

**Root cause:** Hydrostatic thrust bearing design (NLP, SEQ=202). Strongly nonconvex with bilinear/trilinear terms and 8 nonlinear equalities. The original model uses variable `.scale` directives which are not emitted in the MCP. PATH cannot converge from the current initialization.
**Fixable?** Unlikely without `.scale` emission or NLP warm-start infrastructure. Low priority.

#### chain — COPS benchmark catenary with fixed boundary

**MODEL STATUS:** 5 (Locally Infeasible)
**PATH output:** Residual 0.42, 336 iterations, 3 restarts. Nearly converged — stuck on `length_eqn`.
**Issue doc:** None (was Category F in Sprint 21 PATH_CONVERGENCE_ANALYSIS)

**Root cause:** COPS benchmark discretized catenary chain (NLP, SEQ=231). 2 `.fx` boundary conditions create `_fx_` equations. PATH gets very close to convergence (residual 0.42) but stalls on the length constraint. May be a starting point issue or a subtle `_fx_` boundary condition handling problem.
**Fixable?** MAYBE — close to convergence; warm-start from NLP solution might work. Also investigate `_fx_` handling.

#### cpack — Non-convex circle packing

**MODEL STATUS:** 5 (Locally Infeasible)
**PATH output:** Residual 0.022, 83 iterations, 3 restarts. Stuck on `comp_nooverlap(i1,i1)`.
**Issue doc:** None

**Root cause:** Circle packing (QCP, SEQ=387). Non-convex maximization with quadratic no-overlap constraints. The `comp_nooverlap(i1,i1)` self-reference suggests a possible self-pair issue similar to elec (Task 3). Alternatively, the symmetry of circle packing creates many equivalent KKT points, making PATH convergence difficult.
**Fixable?** MAYBE — investigate self-pair issue in no-overlap constraints. Low priority.

#### mathopt3 — Hard nonlinear KKT system

**MODEL STATUS:** 5 (Locally Infeasible)
**PATH output:** Residual 197, 394 iterations, 3 restarts. 58.67% dense Jacobian.
**Issue doc:** None

**Root cause:** MathOptimizer test problem (NLP, SEQ=257). 6 variables, 4 equalities, 3 inequalities with `sin`, `cos`, `sqr` terms creating a highly nonlinear KKT system. The MCP formulation appears structurally correct — stationarity equations have proper multiplier terms, no missing bound multipliers. Initial values (`x1=10, x2=-10, ...`) are far from the KKT point.
**Fixable?** MAYBE — formulation is correct; needs warm-start from NLP solution. Low priority.

#### rocket — COPS benchmark optimal control

**MODEL STATUS:** 5 (Locally Infeasible)
**PATH output:** Residual 1.12, 77 iterations, 3 restarts. 22 zero columns, 26 zero rows.
**Issue doc:** None (was Category F in Sprint 21 PATH_CONVERGENCE_ANALYSIS)

**Root cause:** Goddard Rocket (NLP, SEQ=238). COPS benchmark optimal control with 4 `.fx` boundary conditions and nonlinear dynamics. 971 rows/cols. The 22 zero columns and 26 zero rows suggest structural sparsity issues — possibly from `_fx_` boundary conditions creating degenerate equation rows.
**Fixable?** MAYBE — large model with complex dynamics. Warm-start might help. Low priority.

### Category C: Model Type Incompatible (4 models)

These models cannot be correctly converted to MCP due to fundamental structural incompatibilities with the NLP→MCP transformation.

#### feasopt1 — Intentionally infeasible LP

**MODEL STATUS:** 5 (Locally Infeasible)
**PATH output:** Residual 58.1, 103 iterations. Multipliers blew up to 1.74e+12.
**Issue doc:** None

**Root cause:** The feasopt1 model (LP, SEQ=314) is **intentionally infeasible** — it demonstrates GAMS's FeasOpt feature for relaxing infeasible constraints. The demand is multiplied by 1.2× (`b(j) = 1.2 * b(j)`), making total demand (1080) exceed total supply (950) by 130 units. No KKT point exists because the primal constraints are contradictory. FeasOpt is a solver-specific feature that cannot be replicated in MCP.
**Fixable?** NO — model is designed to be infeasible. Should be permanently excluded.

#### iobalance — Multi-model comparison problem

**MODEL STATUS:** 5 (Locally Infeasible)
**PATH output:** Residual 339, 79 iterations. Large Jacobian entries (4.21e+07).
**Issue doc:** None

**Root cause:** IO coefficient updating (NLP, SEQ=378). Uses 7 solve statements across 5+ different model definitions (NLP entropy, LP MAD/Linf, QCP SD/RSD). The MCP translator merges equations from ALL sub-models into one system, creating a structurally invalid combined MCP where different variable sets and objectives conflict.
**Fixable?** NO — multi-model merge is fundamentally incompatible with single-MCP translation. Would require per-solve-statement MCP generation.

#### meanvar — Multi-model portfolio optimization with parametric `.fx`

**MODEL STATUS:** 5 (Locally Infeasible)
**PATH output:** Residual 0.86, 161 iterations. Stuck on budget/vbal equations.
**Issue doc:** None

**Root cause:** Financial portfolio optimization (NLP, SEQ=112). Uses 6 solve statements across 3 different models (`var1`, `var2`, `sharpe`), with `.fx` assignments in loops to create parametric efficient frontier traces. The MCP merges equations from incompatible model definitions.
**Fixable?** NO — same multi-model merge issue as iobalance.

#### orani — Linearized percentage-change CGE model

**MODEL STATUS:** 5 (Locally Infeasible)
**PATH output:** Residual 1.88, 63 iterations. Stuck on `phi_fx`/`t_fx_clothing`.
**Issue doc:** #765 (`docs/issues/ISSUE_765_orani-mcp-locally-infeasible-fixed-variables-exogenous.md`)

**Root cause:** Linearized percentage-change CGE model (LP, SEQ=40) where variables represent percentage changes from equilibrium, not level values. 9+ variable groups are fixed as exogenous policy parameters. Stationarity equations for fixed exogenous variables reduce to unsatisfiable constants. Even after excluding fixed variables, the non-fixed variable stationarity equations are cascadingly infeasible due to the linearized model structure.
**Fixable?** NO — structurally incompatible with NLP→MCP conversion. Model class detection + warning is the correct approach.

### Category D: CGE / Complex Structure — Needs Investigation (2 models)

These models may have fixable KKT issues or may be structurally incompatible. Deeper investigation is needed.

#### lnts — COPS benchmark with many fixed boundary conditions

**MODEL STATUS:** 5 (Locally Infeasible)
**PATH output:** Residual 2.63, 85 iterations. 100 zero rows at initial point.
**Issue doc:** None

**Root cause:** Particle steering optimal control (NLP, SEQ=237). 4 `.fx` boundary conditions create 7 `_fx_` equations with 29 `_fx_` references in the MCP. 106 fixed columns (out of 567 total). The 100 zero rows at the initial point suggest many stationarity equations evaluate to 0 at the default starting point, providing no gradient information to PATH.
**Fixable?** UNCERTAIN — the high number of `_fx_` equations and zero rows suggests either a KKT construction issue with fixed boundary conditions or a starting point problem. Investigation needed.

#### twocge — Full CGE model with stationarity gradient issue

**MODEL STATUS:** 5 (Locally Infeasible)
**PATH output:** Residual 1.61, 169 iterations. Stuck on `eqM(MLK,JPN)`/`stat_epsilon`.
**Issue doc:** #970 (`docs/issues/ISSUE_970_twocge-mcp-locally-infeasible.md`)

**Root cause:** Two-country CGE model (NLP, SEQ=278). The stationarity equation for `UU(r)` requires `nu_eqUU(r) = 1` (from objective `SW = sum(r, UU(r))`), but PATH converges with `nu_eqUU = 0`. The `eqUU` equations also show large infeasibility (25.5, 30.0). Two `.fx` assignments for numeraire variables. Unlike orani (linearized CGE), this is a full nonlinear CGE with CES/CET/Armington structure.
**Fixable?** UNCERTAIN — may be a starting point issue (warm-start from NLP), a stationarity construction issue (objective gradient), or genuine non-convexity in the CGE equilibrium conditions.

---

## 3. Sprint 22 Fix Candidates

Sprint 22 target: model_infeasible **≤ 12** (need to fix **≥ 3** models from 15)

| Priority | Fix | Models | Effort | Cumulative Fixed | Rationale |
|----------|-----|--------|--------|-----------------|-----------|
| 1 | Fix equation conditioning for lag references | whouse | 1-2h | 1 | Simplest LP; clear translator bug |
| 2 | Fix mixed uniform/non-uniform bound multipliers | ibm1 | 2-3h | 2 | Well-documented in Issue #828 |
| 3 | Fix multi-solve objective selection | uimp | 2-3h | 3 | **Meets −3 target** |
| 4 | Refactor `sameas` guard for multi-entry Jacobian | mexss | 3-4h | 4 | Broader applicability (Issue #764) |

**Total estimated effort: 8-12h** (for all 4 Category A models)

### Recommended Sprint 22 Approach

**Minimum viable (−3 models, hitting ≤12 target):**
- Fix whouse (1-2h) + ibm1 (2-3h) + uimp (2-3h) = 3 models, 5-8h

**Recommended scope (−4 models):**
- Add mexss `sameas` guard refactor (3-4h) = 4 models, 8-12h

**Stretch investigation:**
- Investigate lnts `_fx_` boundary condition handling — may reveal broader fix for chain/rocket too
- Investigate twocge warm-start — tests whether CGE models benefit from NLP solution seeding

---

## 4. Models Excluded from Sprint 22 Scope

### Permanently excluded (4 models — model type incompatible)

| Model | Reason | Recommendation |
|-------|--------|---------------|
| feasopt1 | Intentionally infeasible LP (FeasOpt demo) | Add to "expected infeasible" list; exclude from metrics |
| iobalance | Multi-model merge (7 solves, 5+ models) | Requires per-solve MCP generation infrastructure |
| meanvar | Multi-model with parametric `.fx` loops | Same as iobalance |
| orani | Linearized percentage-change CGE | Add model class detection + warning (Issue #765) |

### Deferred to later sprints (5 models — nonconvex/starting point)

| Model | Reason | Potential Fix |
|-------|--------|--------------|
| bearing | Strongly nonconvex NLP + missing `.scale` | `.scale` emission; NLP warm-start |
| chain | COPS catenary, nearly converges | NLP warm-start; investigate `_fx_` |
| cpack | Non-convex QCP circle packing | Investigate self-pair issue |
| mathopt3 | Hard nonlinear KKT, correct formulation | NLP warm-start |
| rocket | COPS optimal control, zero rows/cols | NLP warm-start; investigate `_fx_` |

### Needs investigation (2 models)

| Model | Reason | Next Step |
|-------|--------|-----------|
| lnts | Many `_fx_` equations, 100 zero rows | Examine `_fx_` construction for boundary conditions |
| twocge | CGE with stationarity gradient issue | Test NLP warm-start; check objective gradient |

---

## 5. Movement Analysis

### How model_infeasible grew from 12 to 15

Sprint 21 code improvements allowed more models to reach the solve stage, where 3 new models were classified as model_infeasible:

| Model | Previous Status | How It Entered |
|-------|----------------|----------------|
| chain | path_solve_terminated (Cat F) | Sprint 21 reclassified from "PATH terminated" to "locally infeasible" |
| rocket | path_solve_terminated (Cat F) | Same as chain — reclassified per KU-09 |
| cpack | (newly translating) | Sprint 21 translation improvements enabled first MCP generation |

The remaining 12 models were already model_infeasible at Sprint 21 baseline.

---

## 6. KU Verification Summary

### KU-23: #765 (orani) Is Fundamentally Unfixable

**Status:** CONFIRMED

orani is a linearized percentage-change CGE model — structurally incompatible with NLP→MCP conversion. Issue #765 investigation (2026-02-22) demonstrated:
1. Excluding fixed variables from stationarity creates MCP count mismatch (13 unmatched variables)
2. Even after fixing count mismatch, non-fixed variable stationarity equations are cascadingly infeasible
3. The model's variables represent percentage changes, not level values — a fundamentally different problem class

**Other CGE-like models in model_infeasible:** twocge is a full nonlinear CGE (different structure from orani's linearized form). twocge may be fixable via warm-start; orani is not.

**Fixed-variable analysis:** orani has 54 `_fx_` references in its MCP (highest of all 15 models), consistent with >50% exogenous fixed variables. No other model_infeasible model has comparable fixed-variable density — iobalance and meanvar are multi-model issues, not fixed-variable issues.

**Recommendation:** Add model class detection heuristic (>30% fixed variables + all linear equations → warning) rather than attempting MCP conversion. Exclude orani from model_infeasible metrics.

### KU-24: path_syntax_error Fixes May Shift Models to model_infeasible

**Status:** CONFIRMED — estimated 7-14 models at risk

Of 43 current path_syntax_error models:
- **6 true CGE models** (camcge, cesam, cesam2, dyncge, korcge, saras) — HIGH risk based on twocge/orani precedent
- **3 borderline CGE/SAM** (prolog, qsambal, sambal) — HIGH risk
- **24 NLP models** — MODERATE risk (~18.8% base infeasibility rate from current pipeline)
- **10 LP/QCP models** — LOW risk

**Estimated shift:** 7-14 models could move from path_syntax_error → model_infeasible when syntax errors are fixed. The largest single risk cluster is the 6 CGE models (estimated 3-4 infeasible).

**Impact on Sprint 22 target:** If 7-14 new models enter model_infeasible, the ≤12 target becomes impossible without also fixing new entrants. Sprint 22 should:
1. Track model_infeasible count after each path_syntax_error fix batch
2. Prioritize Category A KKT fixes (whouse, ibm1, uimp, mexss) early to build buffer
3. Adjust target if CGE model influx exceeds projections

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| whouse fix harder than estimated | Low | Low | Simplest LP; clear root cause |
| ibm1 mixed-bounds fix has edge cases | Medium | Medium | Test on all models with mixed bounds; regression on currently-solving |
| uimp multi-solve fix introduces complexity | Medium | Medium | Scope fix to "use last solve" heuristic |
| mexss `sameas` refactor breaks other models | Medium | High | Extensive regression testing on all 65 currently-solving models |
| path_syntax_error fixes flood model_infeasible | High | High | Track count; adjust target; fix Category A first |
| Category B models not improvable with warm-start | Medium | Low | Only affects stretch goals, not target |

---

## 8. Per-Model Summary Table

| Model | Category | MODEL STATUS | Residual | Iterations | Fix Priority | Root Cause | Effort |
|-------|----------|-------------|----------|------------|-------------|------------|--------|
| bearing | B (nonconvex) | 5 | 1.85e+04 | 189 | Deferred | Nonconvex NLP + missing `.scale` | — |
| chain | B (nonconvex) | 5 | 0.42 | 336 | Deferred | COPS catenary, nearly converges | — |
| cpack | B (nonconvex) | 5 | 0.022 | 83 | Deferred | Non-convex QCP circle packing | — |
| feasopt1 | C (incompatible) | 5 | 58.1 | 103 | Excluded | Intentionally infeasible LP | — |
| ibm1 | A (KKT bug) | 4 | 1.0e+20 | 0 | 2 | Missing bound multiplier terms | 2-3h |
| iobalance | C (incompatible) | 5 | 339 | 79 | Excluded | Multi-model merge (7 solves) | — |
| lnts | D (investigate) | 5 | 2.63 | 85 | Investigate | Many `_fx_`, 100 zero rows | TBD |
| mathopt3 | B (nonconvex) | 5 | 197 | 394 | Deferred | Hard nonlinear, correct formulation | — |
| meanvar | C (incompatible) | 5 | 0.86 | 161 | Excluded | Multi-model with parametric `.fx` | — |
| mexss | A (KKT bug) | 5 | 1.0 | 171 | 4 | `sameas` guard restricts to 1 instance | 3-4h |
| orani | C (incompatible) | 5 | 1.88 | 63 | Excluded | Linearized CGE, exogenous fixed vars | — |
| rocket | B (nonconvex) | 5 | 1.12 | 77 | Deferred | COPS optimal control, zero rows | — |
| twocge | D (investigate) | 5 | 1.61 | 169 | Investigate | CGE stationarity gradient | TBD |
| uimp | A (KKT bug) | 4 | 1.0e+20 | 0 | 3 | Multi-solve objective selection | 2-3h |
| whouse | A (KKT bug) | 4 | 1.0e+20 | 0 | 1 | Equation conditioning for lag refs | 1-2h |

---

## 9. Cross-References to Existing Issue Documents

| Model | Issue | Status | Notes |
|-------|-------|--------|-------|
| bearing | #757 | Open | Nonconvex; needs `.scale` emission |
| ibm1 | #828 | Open | Mixed uniform/non-uniform bounds |
| mexss | #764 | Open | `sameas` guard for indexed Jacobian |
| orani | #765 | Open | Linearized CGE — not fixable |
| twocge | #970 | Open | Stationarity gradient / warm-start |

**Models without issue documents:** chain, cpack, feasopt1, iobalance, lnts, mathopt3, meanvar, rocket, uimp, whouse (10 models — create issues during Sprint 22 execution as needed)

---

## 10. Notes

- **GAMS version:** Pipeline data from `gamslib_status.json` uses GAMS 51.3.0. Manual error classification (GAMS execution of MCP files) used GAMS v53. Error types are consistent across both versions.
- **Committed vs working-tree discrepancy:** The committed `gamslib_status.json` has 12 `model_infeasible` models. The working-tree version (uncommitted local pipeline reruns) has 15, adding ibm1 (was `model_optimal`), twocge (was `path_syntax_error`), and feasopt1 (was unclassified). The discrepancy arises because Sprint 21 code improvements changed the MCP output for these models, but the status JSON was not re-committed. All 15 were verified by direct GAMS v53 execution of on-disk MCP files.
- **MODEL STATUS 4 vs 5:** STATUS 4 (Infeasible) means PATH detected structural infeasibility at preprocessing before running any iterations. STATUS 5 (Locally Infeasible) means PATH ran its algorithm but converged to a point with nonzero residual. STATUS 4 models (ibm1, uimp, whouse) are more likely to have clear KKT construction bugs.
- **Multi-model limitation:** 3 of 15 models (feasopt1, iobalance, meanvar) have multiple solve statements with different model definitions. The current pipeline generates one MCP per `.gms` file from the first or merged model. Per-solve-statement MCP generation would be a significant infrastructure change.
