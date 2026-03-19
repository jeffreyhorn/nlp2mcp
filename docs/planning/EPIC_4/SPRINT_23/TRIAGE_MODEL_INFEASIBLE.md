# Triage: model_infeasible Models (12)

**Date:** 2026-03-19
**Branch:** `planning/sprint23-task3`
**Prep Task:** 3 (from PREP_PLAN.md)

## Executive Summary

All 12 in-scope model_infeasible models were analyzed by running MCP generation, examining GAMS solve output, and reviewing existing GitHub issues. Key findings:

- **All 12 models parse, translate, and generate MCP files successfully.** Failures occur at GAMS solve time.
- **2 models have MCP pairing errors** (bearing, pak) — GAMS aborts before PATH runs due to unmatched equation/variable pairs. These are Category A (KKT formulation bugs).
- **5 models have diagnosed KKT formulation bugs** with existing GitHub issues (markov #1110, spatequ #1038, pak #1049, paperco #953, sparta #1081). These are the highest-leverage fix targets.
- **5 models are PATH convergence failures** on non-convex problems (chain, cpack, lnts, mathopt3, robustlp) — structurally correct MCP but PATH cannot find the KKT point from default initialization. These require warm-start infrastructure or are candidates for deferral.
- **0 models are inherently incompatible** (unlike orani in the permanent exclusion list).
- **Recommendation:** Target 5-6 models in Sprint 23, reducing model_infeasible from 12 to 6-7 (gross fixes; influx tracking per PR7).

## Root Cause Classification

| Model | Type | Category | Error | Issue(s) | Fix Effort | Sprint 23? |
|-------|------|----------|-------|----------|-----------|-----------|
| markov | LP | A | Single representative derivative for multi-pattern Jacobian | #1110 | 3-4h | Yes |
| spatequ | LP | A | Jacobian domain mismatch in stationarity equations | #1038 | 3-4h | Yes (needs #1026) |
| pak | LP | A | MCP pairing: unmatched `comp_conl.lam_conl`; incomplete stationarity for `s(t)` | #1049 | 3-4h | Yes |
| bearing | NLP | A | MCP pairing: 2 unmatched equations + 8 unused variables | #757 | 3-5h | Maybe |
| paperco | LP | D | Parameter `pp(p)` assigned inside loop body not emitted | #953 | 3-4h | Yes |
| sparta | LP | A | KKT bug in bal4 formulation; also multi-solve (#1080) | #1081 | 2-3h | Maybe |
| robustlp | LP | B | Locally Infeasible (residual 3.6e-04); diagonal parameter fix applied but PATH convergence remains | #1105 (closed) | 2-3h | Maybe |
| prolog | NLP | B | CES singular Jacobian; fractional exponents create numerical singularity | #1070 | 3-4h | Uncertain |
| mathopt3 | NLP | B | Locally Infeasible; correct formulation, bad starting point (residual 197) | (none) | 2-3h | Deferred |
| chain | NLP | B | Locally Infeasible; non-convex catenary, nearly converges (residual 0.11) | (none) | 2-3h | Deferred |
| cpack | QCP | B | Locally Infeasible; non-convex circle packing, possible self-pair issue | (none) | 2-3h | Deferred |
| lnts | NLP | B | Locally Infeasible; 100 zero rows at initial point, many `.fx` boundary conditions | (none) | 3-4h | Deferred |

### Category Distribution

| Category | Count | Models |
|----------|-------|--------|
| A: KKT formulation bug | 5 | markov, spatequ, pak, bearing, sparta |
| B: PATH convergence / non-convex | 6 | robustlp, prolog, mathopt3, chain, cpack, lnts |
| C: Inherent MCP incompatibility | 0 | (none) |
| D: Missing feature | 1 | paperco |

---

## Per-Model Analysis

### markov (Category A: KKT Formulation Bug)

**Type:** LP | **GAMS Size:** 2 vars, 3 eqs | **MCP Instantiated:** 329 vars, 329 eqs
**Error:** Locally Infeasible (MODEL STATUS 5), 21,727 iterations, residual 0.249
**Root Cause:** The stationarity builder picks a single representative (diagonal) Jacobian entry and applies its derivative to ALL constraint-variable pairings. For `constr(sp,j)` involving `z(sp,j,spp)`, the diagonal entry has derivative `1 - b*pi(...)` but off-diagonal entries should be `-b*pi(...)` only. The extra `+1` term is incorrectly added to every `nu_constr` coefficient.

**Issue:** #1110 (open) — well-diagnosed with specific code-level root cause
**Dependencies:** Changes to `_add_indexed_jacobian_terms()` in `src/kkt/stationarity.py`
**Fix Effort:** 3-4h
**Fix Approach:** Generate per-pattern stationarity equations instead of using a single representative. For each unique derivative pattern, emit a separate `sameas`-guarded term with the correct derivative expression.

---

### spatequ (Category A: KKT Formulation Bug)

**Type:** LP | **GAMS Size:** 8 vars, 14 eqs | **MCP Instantiated:** 125 vars, 131 eqs
**Error:** Locally Infeasible (MODEL STATUS 5), 1,305 iterations, residual 260.0, 82 infeasible equations
**Root Cause:** When a variable with domain `(r,c)` appears inside a `sum()` over a different index in an equation with domain `(r,c)`, the Jacobian derivative is incorrectly emitted as a sum over all equation instances. The KKT assembly's sum index binding fails to correctly map equation domain indices to the variable's domain indices when they have different dimensionality (3D variable `X(r,rr,c)` vs 2D equations).

**Issue:** #1038 (open) — well-diagnosed; depends on #1026 (model equation selection for MCP solves)
**Dependencies:** #1026 must be fixed first; changes to `src/kkt/assemble.py`, `src/ad/constraint_jacobian.py`
**Fix Effort:** 3-4h (after #1026)
**Fix Approach:** Fix the sum index binding in the Jacobian assembly to correctly track which indices are equation-domain vs. sum-iteration indices.

---

### pak (Category A: KKT Formulation Bug)

**Type:** LP | **GAMS Size:** 11 vars, 15 eqs | **MCP Instantiated:** 770 eqs, 777 vars
**Error:** GAMS solve aborted — unmatched MCP pair `comp_conl.lam_conl`; warnings about multiple defining equations for `ti` and `gnp`
**Root Cause:** Incomplete stationarity for variable `s(t)`. Constraints involving `s` with lead/lag expressions are missing Jacobian entries. The terminal period `t='1985'` suggests missing transversality condition terms.

**Issue:** #1049 (open) — diagnosed; involves lead/lag handling in Jacobian computation
**Dependencies:** Changes to `src/ad/constraint_jacobian.py`, `src/kkt/stationarity.py`
**Fix Effort:** 3-4h
**Fix Approach:** Ensure lead/lag variable references in constraint bodies generate correct Jacobian entries for the shifted time period. Add transversality condition handling for terminal periods.

---

### bearing (Category A: KKT Formulation Bug)

**Type:** NLP | **GAMS Size:** 14 vars, 13 eqs | **MCP Instantiated:** 44 eqs, 42 vars
**Error:** GAMS solve aborted — 2 unmatched equations (`comp_radius.lam_radius`, `pumping_energy.nu_pumping_energy`), 8 unused variables
**Root Cause:** MCP pairing mismatch. The equation/variable count is 44 vs 42, indicating 2 equations are generated without corresponding paired variables (or vice versa). The issue doc (#757) attributes this to extreme coefficient scaling (1e-6 to 1e8) and missing `.scale` emission, but the MCP pairing abort is a more fundamental structural issue that must be resolved before scaling matters.

**Issue:** #757 (open) — partially diagnosed; pairing mismatch takes precedence over scaling
**Dependencies:** None (localized MCP pairing fix)
**Fix Effort:** 3-5h (uncertain — need to investigate which equations/variables are unmatched)
**Fix Approach:** Identify which equations/variables are generating unmatched pairs. Fix the KKT builder to ensure every equation has a corresponding variable and vice versa. After pairing is fixed, address scaling (`.scale` emission) if PATH still fails.

---

### paperco (Category D: Missing Feature)

**Type:** LP | **GAMS Size:** 8 vars, 5 eqs | **MCP Instantiated:** 59 vars, 59 eqs
**Error:** Locally Infeasible (MODEL STATUS 5), 1,675 iterations, residual 0.865
**Root Cause:** Parameter `pp(p)` is assigned inside a `loop(scenario, ...)` body in the original model. The IR parser stores loop bodies as raw AST but does not extract individual parameter assignment statements, so the assignment never reaches the emitter. The MCP output declares `pp(p)` with no values.

**Issue:** #953 (open) — well-diagnosed; shares root cause with lmp2 (#952)
**Dependencies:** Changes to `src/ir/parser.py` (`_handle_loop_stmt()`)
**Fix Effort:** 3-4h
**Fix Approach:** Enhance loop body extraction in the IR parser to walk and extract parameter assignment statements. For paperco, use a representative scenario value from the loop body data.

---

### sparta (Category A: KKT Formulation Bug)

**Type:** LP | **GAMS Size:** 3 vars, 5 eqs | **MCP Instantiated:** 111 vars, 111 eqs
**Error:** Locally Infeasible (MODEL STATUS 5), 435 iterations, residual 5.01
**Root Cause:** KKT derivation bug specific to the bal4 constraint structure. The model has 4 LP formulations solved sequentially; nlp2mcp captures the last one (sparta4/bal4).

**Issue:** #1081 (open) — less detail than other issues
**Dependencies:** Also a multi-solve model (#1080) — even if KKT bug is fixed, NLP reference comparison may not be valid
**Fix Effort:** 2-3h
**Fix Approach:** Debug the bal4 constraint's KKT derivation. Since it's an LP, the KKT should be straightforward linear complementarity. The multi-solve nature means comparison validation requires special handling.

---

### robustlp (Category B: PATH Convergence)

**Type:** LP | **GAMS Size:** 6 vars, 7 eqs | **MCP Instantiated:** 89 vars, 89 eqs
**Error:** Locally Infeasible (MODEL STATUS 5), 4,285 iterations, residual 3.62e-04
**Root Cause:** The diagonal parameter expansion bug (#1105) was already fixed. The remaining issue is PATH convergence — residual is very small (3.62e-04), suggesting the MCP is nearly feasible. This is likely a warm-start initialization issue rather than a KKT formulation bug.

**Issue:** #1105 (closed — parameter expansion fix applied)
**Dependencies:** None; may benefit from warm-start infrastructure
**Fix Effort:** 2-3h
**Fix Approach:** With residual at 3.6e-04, the KKT formulation is likely correct. Options: (1) improve `.l` initialization, (2) adjust PATH tolerances, (3) investigate if the remaining infeasibility is due to a secondary formulation issue. Since it's an LP, the MCP should have a unique solution — the near-convergence is encouraging.

---

### prolog (Category B: PATH Convergence / Singular Jacobian)

**Type:** NLP | **GAMS Size:** 6 vars, 9 eqs | **MCP Instantiated:** 67 vars, 69 eqs
**Error:** Locally Infeasible (MODEL STATUS 5), 8,060 iterations, residual 0.94
**Root Cause:** CES demand functions produce fractional exponents (`y(h)**(epsi-1)`, `p(gp)**-(1+eta)`) in KKT stationarity equations that create singular Jacobian entries near variable bounds. PATH cannot converge due to extreme Jacobian entries. This may be a numerical conditioning issue rather than a code bug.

**Issue:** #1070 (open) — well-analyzed; identified as CES singularity
**Dependencies:** May require PATH parameter tuning or model reformulation
**Fix Effort:** 3-4h (uncertain)
**Fix Approach:** Options: (1) clamp variables away from singularity boundaries, (2) reformulate CES terms to avoid fractional exponents in stationarity, (3) warm-start from NLP solution. The CES singularity is a structural property of the model class, making this a borderline Category B/C issue.

---

### mathopt3 (Category B: PATH Convergence)

**Type:** NLP | **GAMS Size:** 7 vars, 8 eqs | **MCP Instantiated:** 14 vars, 14 eqs
**Error:** Locally Infeasible (MODEL STATUS 5), 732 iterations, residual 197.4
**Root Cause:** Hard nonlinear KKT system with trigonometric terms (sin, cos, sqr). The MCP formulation is structurally correct — proper multiplier terms, correct complementarity pairing. The failure is purely a starting point issue: default initialization is far from the global minimum.

**Dependencies:** Warm-start infrastructure
**Fix Effort:** 2-3h (with warm-start)
**Fix Approach:** Seed MCP variable initialization from the NLP solution. The model is small (14x14 MCP) so warm-start should be effective.

---

### chain (Category B: PATH Convergence)

**Type:** NLP | **GAMS Size:** 3 vars, 3 eqs | **MCP Instantiated:** 156 vars, 157 eqs
**Error:** Locally Infeasible (MODEL STATUS 5), 282 iterations, residual 0.11
**Root Cause:** COPS catenary benchmark. Non-convex NLP with `.fx` boundary conditions. PATH nearly converges (residual 0.11) but stalls on the `length_eqn`. The MCP formulation appears structurally correct — this is a starting point / nonconvexity issue, not a KKT bug.

**Dependencies:** Warm-start infrastructure
**Fix Effort:** 2-3h
**Fix Approach:** Warm-start from NLP solution. The near-convergence (0.11 residual) suggests the KKT system is solvable from a better starting point.

---

### cpack (Category B: PATH Convergence)

**Type:** QCP | **GAMS Size:** 3 vars, 2 eqs | **MCP Instantiated:** 63 vars, 63 eqs
**Error:** Locally Infeasible (MODEL STATUS 5), 324 iterations, residual 0.022
**Root Cause:** Non-convex circle packing problem. PATH gets very close (residual 0.022) but cannot fully satisfy complementarity. Possible self-pair issue in `comp_nooverlap(i1,i1)` — the `ij(i,j)` set condition `ord(i) < ord(j)` may not be fully enforced in equation conditions.

**Dependencies:** Verify set conditioning; warm-start infrastructure
**Fix Effort:** 2-3h
**Fix Approach:** (1) Verify `ij(i,j)` set conditioning is correctly reflected in `comp_nooverlap`, (2) warm-start from NLP solution. The very small residual is encouraging.

---

### lnts (Category B: PATH Convergence)

**Type:** NLP | **GAMS Size:** 4 vars, 4 eqs | **MCP Instantiated:** 567 eqs, 673 vars
**Error:** Locally Infeasible (MODEL STATUS 5), 18,686 iterations, residual 1.71
**Root Cause:** Particle steering optimal control (COPS benchmark) with many boundary conditions (7 `_fx_` equations, 106 fixed columns). 100 of 567 equations evaluate to zero at the default starting point, creating a degenerate initial Jacobian where PATH has no gradient information. The eq/var dimension mismatch (567 vs 673) suggests extra variables being generated.

**Dependencies:** Investigation of `.fx` handling and variable generation
**Fix Effort:** 3-4h
**Fix Approach:** (1) Investigate whether `.fx_` equations are over-constraining the system, (2) check for spurious variable generation causing the 567/673 mismatch, (3) warm-start from NLP solution to avoid zero-row problem.

---

## Fix Priority Ranking

Models ranked by fix leverage (benefit vs. effort), considering diagnosed root causes and dependencies.

### Tier 1: Diagnosed KKT Bugs (fix in Sprint 23)

| Priority | Model | Effort | Category | Notes |
|----------|-------|--------|----------|-------|
| 1 | **markov** | 3-4h | A | Well-diagnosed (#1110); multi-pattern Jacobian fix in stationarity.py |
| 2 | **pak** | 3-4h | A | Well-diagnosed (#1049); lead/lag Jacobian entries |
| 3 | **paperco** | 3-4h | D | Well-diagnosed (#953); loop body parameter extraction |
| 4 | **sparta** | 2-3h | A | #1081; LP model, should be straightforward KKT |
| 5 | **spatequ** | 3-4h | A | Well-diagnosed (#1038); depends on #1026 |

**Tier 1 total:** 14-19h for 5 models

### Tier 2: Investigate Mid-Sprint

| Priority | Model | Effort | Category | Notes |
|----------|-------|--------|----------|-------|
| 6 | **bearing** | 3-5h | A | MCP pairing mismatch; need to identify unmatched pairs |
| 7 | **robustlp** | 2-3h | B | Near-feasible (residual 3.6e-04); may just need initialization |

**Tier 2 total:** 5-8h for 2 models

### Tier 3: Deferred (requires warm-start infrastructure)

| Priority | Model | Effort | Category | Notes |
|----------|-------|--------|----------|-------|
| 8 | **prolog** | 3-4h | B | CES singularity; may be structural |
| 9 | **chain** | 2-3h | B | Nearly converges; warm-start should solve |
| 10 | **cpack** | 2-3h | B | Nearly converges; verify set conditions first |
| 11 | **mathopt3** | 2-3h | B | Correct formulation; needs warm-start |
| 12 | **lnts** | 3-4h | B | Many zero rows; needs investigation |

**Tier 3 total:** 12-17h for 5 models

---

## Recommendation for Sprint 23

### Target: Fix 5 models (Tier 1), reducing gross model_infeasible by 5

**Rationale:**
- Tier 1 has 5 models with well-diagnosed KKT bugs and existing GitHub issues providing clear fix directions
- Total effort: 14-19h, fitting within the Priority 2 budget
- All 5 are LP or LP-like models where KKT is linear complementarity — fixes should be reliable
- markov (#1110) and spatequ (#1038) have the most detailed root cause analysis
- paperco (#953) shares a root cause with lmp2 (#952), giving bonus coverage

**Gross vs. Net Tracking (PR7):**
- Gross fixes: 5 (from Tier 1)
- Expected influx from path_solve_terminated fixes: 2-3 models (per KU-05 cascade assessment)
- Net reduction: 2-3 models (from 12 to 9-10)
- To reach ≤ 8 target: need 4+ gross fixes, or reduce influx, or add Tier 2 models

**Permanent Exclusion Candidates:** None recommended. All 12 models have identifiable fix paths (KKT bugs or warm-start). No model shows the inherent structural incompatibility pattern seen in orani/feasopt1/iobalance.

### Schedule Suggestion

| Day | Models | Work |
|-----|--------|------|
| 2-3 | markov, pak | Multi-pattern Jacobian fix; lead/lag Jacobian entries |
| 4-5 | paperco, sparta | Loop body extraction; bal4 KKT debug |
| 6-7 | spatequ | Jacobian domain mismatch (after #1026) |
| 8+ | bearing, robustlp | Investigation; MCP pairing fix; initialization |

---

## MCP Generation Summary

All 12 models parse, translate, and generate MCP files successfully. The failures occur at GAMS solve time.

| Model | MCP Lines | Nonconvex Warnings | Generation Issues |
|-------|-----------|-------------------|-------------------|
| bearing | 317 | 15 | None |
| chain | 232 | 2 | None |
| cpack | 181 | 0 | None |
| lnts | 256 | 8 | None |
| markov | 180 | 0 | None |
| mathopt3 | 175 | 1 | Skipped param 'report' |
| pak | 306 | 0 | Skipped param 'rep' |
| paperco | 222 | 0 | None |
| prolog | 307 | 2 | Skipped params 'pi', 'yp' |
| robustlp | 138 | 1 | None |
| sparta | 253 | 0 | Skipped param 'rep' |
| spatequ | 267 | 6 | None |

## Solve Summary

| Model | Solver Status | Model Status | Iterations | Residual | Infeasible Rows |
|-------|--------------|-------------|-----------|----------|----------------|
| bearing | Aborted | N/A | N/A | N/A | Pairing error |
| chain | 1 Normal | 5 Locally Infeasible | 282 | 0.11 | 151 |
| cpack | 1 Normal | 5 Locally Infeasible | 324 | 0.022 | 5 |
| lnts | 1 Normal | 5 Locally Infeasible | 18,686 | 1.71 | 449 |
| markov | 1 Normal | 5 Locally Infeasible | 21,727 | 0.249 | 121 |
| mathopt3 | 1 Normal | 5 Locally Infeasible | 732 | 197.4 | 13 |
| pak | Aborted | N/A | N/A | N/A | Pairing error |
| paperco | 1 Normal | 5 Locally Infeasible | 1,675 | 0.865 | 6 |
| prolog | 1 Normal | 5 Locally Infeasible | 8,060 | 0.94 | 40 |
| robustlp | 1 Normal | 5 Locally Infeasible | 4,285 | 3.62e-04 | 12 |
| sparta | 1 Normal | 5 Locally Infeasible | 435 | 5.01 | 20 |
| spatequ | 1 Normal | 5 Locally Infeasible | 1,305 | 260.0 | 82 |
