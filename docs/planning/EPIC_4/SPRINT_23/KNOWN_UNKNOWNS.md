# Sprint 23 Known Unknowns

**Created:** 2026-03-17
**Sprint:** 23 (Prep Task 1)
**Status:** Initial — unknowns cataloged; verification pending during prep tasks
**Last Updated:** 2026-03-17

---

## Purpose

This document catalogs assumptions and unknowns for Sprint 23 (Solve Rate Push & Error Category Reduction). Each unknown has a priority, assumption, research questions, verification method, and risk assessment. The goal is to prevent late discoveries during implementation by surfacing uncertainties early.

**Process:** Sprint 22 Known Unknowns (30 entries) proved highly effective — KU-24 correctly predicted the model_infeasible cascade, and KU-27/KU-28 discoveries were proactively documented for Sprint 23 carryforward. This document follows the same pattern.

**Sprint 23 Targets:**
- Solve: 89 → ≥ 100
- Match: 47 → ≥ 55
- path_solve_terminated: 10 → ≤ 5
- model_infeasible: 12 → ≤ 8 (in-scope)
- path_syntax_error: 20 → ≤ 15
- Translate: ≥ 93% (≥ 145/156)
- Parse: ≥ 156/160 (maintain)
- Tests: ≥ 4,300

---

## Summary Table

| ID | Category | Unknown | Priority | Assumption | Verification Deadline |
|----|----------|---------|----------|------------|-----------------------|
| KU-01 | path_solve_terminated | 10 models are mostly MCP pairing/execution errors, not PATH convergence | Critical | Yes — Sprint 21 Day 12 analysis confirmed pre-solver failures | Task 2 |
| KU-02 | path_solve_terminated | Fixing 5+ models is achievable in Sprint 23 timeframe | Critical | Yes — Sprint 22 WS2 fixed 5 in ~12h | Task 2 |
| KU-03 | path_solve_terminated | sambal/qsambal dollar-condition issues are fixable without #1112 | High | May require #1112 (dollar-condition propagation) first | Task 2 |
| KU-04 | path_solve_terminated | dyncge/twocge CGE models will solve after KKT fixes | High | CGE models may be structurally incompatible like orani | Task 2 |
| KU-05 | path_solve_terminated | Fixing path_solve_terminated won't cascade to model_infeasible | High | Some models may shift category when errors are resolved | Task 2 |
| KU-06 | model_infeasible | 12 in-scope models have fixable KKT formulation bugs | Critical | Most are KKT bugs, not inherent MCP incompatibilities | Task 3 |
| KU-07 | model_infeasible | Sprint 22 sameas guard pattern applies to additional models | High | pak, spatequ, sparta may share the #764 pattern | Task 3 |
| KU-08 | model_infeasible | model_infeasible influx from other fixes is manageable | Critical | Sprint 22 had net-zero (5 fixed, 5 entered); Sprint 23 budgets for influx | Task 3 |
| KU-09 | model_infeasible | chain/rocket local infeasibility is non-convexity, not KKT bug | Medium | Confirmed in Sprint 22 KU-09; PATH ran to completion | Task 3 |
| KU-10 | model_infeasible | markov multi-pattern Jacobian (#1110) is fixable in 3-4h | High | Single-representative derivative is the root cause | Task 3 |
| KU-11 | model_infeasible | prolog singular Jacobian (#1070) is a CES demand formulation issue | Medium | May require reformulation beyond simple KKT fix | Task 3 |
| KU-12 | Match Rate | Alias-aware differentiation can be implemented without regression | Critical | Sprint 22 naive fix regressed dispatch model; need iteration-context guard | Task 4 |
| KU-13 | Match Rate | Alias differentiation affects only alias-using models | High | Fix should be selective — no impact on non-alias models | Task 4 |
| KU-14 | Match Rate | Dollar-condition propagation requires changes to gradient only, not Jacobian | High | Conditions may need propagation through both AD layers | Task 5 |
| KU-15 | Match Rate | Dollar-condition and alias fixes are independent (no coupling) | High | Could share AD pipeline modifications; order matters | Tasks 4-5 |
| KU-16 | Match Rate | Non-convex multi-KKT divergence is irreducible (~12 models) | Medium | Sprint 22 KU-29 confirmed; match rate ceiling ~75-80% of solvers | Task 4 |
| KU-17 | Match Rate | Fixing KKT bugs in verified-convex models yields guaranteed matches | High | 7 verified-convex mismatches from Sprint 22 KU-11; convex ⟹ unique KKT | Task 4 |
| KU-18 | path_syntax_error | Subcategory G aliasing mechanism works for remaining 2 models | High | Sprint 22 KU-04 verified; detection needs enhancement | Task 6 |
| KU-19 | path_syntax_error | Subcategory B (5 models) have diverse root causes, not a common bug | High | Sprint 22 KU-03 refuted common-bug assumption; each model needs separate investigation | Task 6 |
| KU-20 | path_syntax_error | Fixing 5 path_syntax_error models won't inflate model_infeasible | High | Sprint 22 KU-24 confirmed 7-14 at-risk models; CGE subset highest | Task 6 |
| KU-21 | path_syntax_error | New subcategories (K, GUSS, hyphenated labels) from Sprint 22 are low-effort | Medium | Sprint 22 KU-19 found tricp needs new Subcat K; unclear effort | Task 6 |
| KU-22 | Translate Failures | Compilation error fixes are higher leverage than timeout fixes | High | Quick compilation fixes yield models that can immediately attempt solve | Task 7 |
| KU-23 | Translate Failures | Timeout models (#830 gastrans pattern) are architecturally intractable | Medium | Sprint 22 KU-22 confirmed gastrans needs architectural Jacobian changes | Task 7 |
| KU-24 | Translate Failures | 4 compilation fixes are sufficient to reach ≥ 145/156 translate target | High | Need exactly 4 of 15 failures fixed; depends on failure type distribution | Task 7 |
| KU-25 | Translate Failures | paperco (#953) and lmp2 (#952) loop-body issues share a common parser fix | Medium | Both involve loop body assignments not emitted; may share root cause | Task 7 |
| KU-26 | Match Rate | Multi-solve models (senstran, aircraft, sparta) are correctly classified as incomparable | Low | Sprint 22 KU-30 confirmed; pipeline skips comparison | N/A |

---

## Category 1: path_solve_terminated Reduction (5 unknowns)

### KU-01: 10 Remaining Models Are Mostly Pre-Solver Failures

**Priority:** Critical
**Assumption:** The 10 remaining path_solve_terminated models (dyncge, elec, etamac, fawley, gtm, maxmin, qsambal, rocket, sambal, twocge) fail before PATH runs, due to MCP pairing errors or execution errors, not genuine PATH convergence failures.

**Research Questions:**
1. How many of the 10 models have MCP pairing errors (wrong variable/equation count)?
2. How many have execution errors (division by zero, NA values, domain errors)?
3. Do any genuinely reach PATH and fail convergence (like the old chain/rocket pattern)?
4. Which models have existing GitHub issues with root cause analysis?
5. Has the Sprint 22 sameas guard refactor changed any of these models' error patterns?

**How to Verify:** Run MCP generation and attempt GAMS solve for each model. Classify error type from GAMS `.lst` output. Cross-reference with Sprint 21 PATH Convergence Analysis.

**Risk if Wrong:** If several models have genuine PATH convergence issues (not pre-solver errors), the ≤ 5 target requires PATH author consultation or reformulation — work that can't fit in Sprint 23's timeframe.

**Estimated Research Time:** 2h (part of Task 2 triage)
**Owner:** Task 2 (path_solve_terminated triage)
**Verification Results:** 🔍 Status: INCOMPLETE

---

### KU-02: Fixing 5+ Models Is Achievable in Sprint 23

**Priority:** Critical
**Assumption:** Sprint 22 WS2 fixed 5 path_solve_terminated models (fdesign, trussm, fawley, springchain, whouse) in ~12h. Sprint 23 can replicate this pace for 5+ additional models, reducing from 10 to ≤ 5.

**Research Questions:**
1. Were Sprint 22's WS2 fixes "low-hanging fruit" that won't repeat?
2. Are the remaining 10 models harder than the 5 already fixed?
3. What is the average fix effort per model based on Sprint 22 data?
4. Do any of the 10 require architectural changes (not just localized KKT/emitter fixes)?
5. Is the 8-12h budget for Priority 1 sufficient given the model difficulty?

**How to Verify:** Task 2 triage will classify each model's difficulty. Compare against Sprint 22 WS2 fix efforts to calibrate.

**Risk if Wrong:** If the remaining 10 are significantly harder (e.g., all require architectural AD changes), Sprint 23 may only fix 2-3, missing the ≤ 5 target. Contingency: deprioritize Priority 4/5 to allocate more time to Priority 1.

**Estimated Research Time:** 30min (review Sprint 22 WS2 effort data)
**Owner:** Task 2 (path_solve_terminated triage)
**Verification Results:** 🔍 Status: INCOMPLETE

---

### KU-03: sambal/qsambal Dollar-Condition Dependencies

**Priority:** High
**Assumption:** sambal (#862) and qsambal have domain conditioning issues that may require the dollar-condition propagation fix (#1112) from Priority 3 before they can be resolved. If true, these models can't be fixed early in the sprint.

**Research Questions:**
1. Does sambal's division-by-zero error (#862) stem from missing dollar conditions in stationarity equations?
2. Does qsambal share the same pattern as sambal (they are related models)?
3. Can the sambal/qsambal fix be applied independently of the full #1112 architectural change?
4. Would a targeted, model-specific dollar-condition fix work, or is the full propagation mechanism required?

**How to Verify:** Examine sambal's emitted MCP for missing `$` conditions on stationarity equations. Compare with the original NLP model's conditional structure.

**Risk if Wrong:** If sambal/qsambal require #1112, they must wait until Priority 3 is complete (mid-sprint). This delays 2 of the 5 needed path_solve_terminated reductions, compressing the schedule.

**Estimated Research Time:** 1h
**Owner:** Task 2 (path_solve_terminated triage)
**Verification Results:** 🔍 Status: INCOMPLETE

---

### KU-04: CGE Models (dyncge, twocge) May Be Structurally Incompatible

**Priority:** High
**Assumption:** dyncge and twocge are CGE (Computable General Equilibrium) models that may share orani's structural incompatibility with NLP→MCP conversion. Sprint 22 KU-23 confirmed orani is permanently unfixable.

**Research Questions:**
1. Are dyncge and twocge linearized percentage-change CGE models like orani?
2. Do they have high fixed-variable density (orani had 54 `_fx_` references)?
3. Are they currently path_solve_terminated for a different reason (pre-solver error) that masks incompatibility?
4. If incompatible, should they be reclassified to permanently excluded (like orani)?
5. Would fixing their current error reveal model_infeasible status?

**How to Verify:** Examine model structure for CGE characteristics. Check fixed-variable density. Run MCP generation and analyze error type.

**Risk if Wrong:** If dyncge/twocge are incompatible, the effective target pool for path_solve_terminated drops from 10 to 8, requiring 3 of 8 fixes (not 5 of 10) to reach ≤ 5. This is actually easier if we acknowledge the exclusions early.

**Estimated Research Time:** 1h
**Owner:** Task 2 (path_solve_terminated triage)
**Verification Results:** 🔍 Status: INCOMPLETE

---

### KU-05: path_solve_terminated → model_infeasible Cascade

**Priority:** High
**Assumption:** Fixing path_solve_terminated models' pre-solver errors may expose model_infeasible conditions for some models. Sprint 22 KU-24 confirmed this pattern: fixing syntax errors shifted 5 models into model_infeasible.

**Research Questions:**
1. How many of the 10 path_solve_terminated models are likely to shift to model_infeasible when their primary error is fixed?
2. Are the CGE models (dyncge, twocge) at highest risk of this cascade?
3. Does the model_infeasible ≤ 8 target account for influx from path_solve_terminated fixes?
4. Should Sprint 23 track gross fixes and influx separately (per PR7)?

**How to Verify:** After each path_solve_terminated fix, check if the model solves or shifts to model_infeasible. Track influx per PR7.

**Risk if Wrong:** If 3+ models cascade to model_infeasible, the ≤ 8 in-scope target becomes unreachable unless additional model_infeasible fixes compensate. The solve count (≥ 100) target may still be met if models shift to model_infeasible rather than solving.

**Estimated Research Time:** 30min
**Owner:** Tasks 2, 3 (cross-referenced)
**Verification Results:** 🔍 Status: INCOMPLETE

---

## Category 2: model_infeasible Reduction (6 unknowns)

### KU-06: 12 In-Scope Models Are Primarily KKT Formulation Bugs

**Priority:** Critical
**Assumption:** Most of the 12 in-scope model_infeasible models (bearing, chain, cpack, lnts, markov, mathopt3, pak, paperco, prolog, robustlp, sparta, spatequ) have KKT formulation bugs that can be fixed, rather than inherent MCP incompatibilities.

**Research Questions:**
1. How many have known KKT issues (existing GitHub issues with root cause)?
2. How many are structural infeasibility (PATH preprocessor detects infeasibility at MODEL STATUS 4)?
3. Are any similar to orani (inherently incompatible model class)?
4. What fraction of Sprint 22's model_infeasible fixes were KKT bugs vs. other causes?
5. Do any require missing IR/grammar features not yet implemented?

**How to Verify:** For each model, review existing issues (#1049, #1070, #1081, #1110, #1038). Run MCP generation and classify infeasibility source.

**Risk if Wrong:** If most are inherent incompatibilities (not KKT bugs), the ≤ 8 target requires reclassifying them as permanently excluded — changing the denominator, not fixing code. This would mask the real problem.

**Estimated Research Time:** 2h (part of Task 3 triage)
**Owner:** Task 3 (model_infeasible triage)
**Verification Results:** 🔍 Status: INCOMPLETE

---

### KU-07: Sprint 22 sameas Guard Pattern Extends to More Models

**Priority:** High
**Assumption:** The sameas guard refactor from Sprint 22 (PR #1076, fixing uimp/mexss) established a pattern for scalar-constraint multiplier terms. Additional model_infeasible models (pak, spatequ, sparta) may benefit from the same pattern or extensions of it.

**Research Questions:**
1. Does pak's incomplete stationarity (#1049) involve the same `_add_indexed_jacobian_terms()` code path?
2. Does spatequ's Jacobian domain mismatch (#1038) relate to the sameas guard logic?
3. Does sparta's KKT bug (#1081) share the scalar-constraint multiplier pattern?
4. Are there other stationarity.py code paths with similar single-entry restrictions?
5. Did the Sprint 22 sameas guard refactor create any new edge cases for these models?

**How to Verify:** Examine each model's PATH/GAMS error output. Compare error patterns with the uimp/mexss pattern that was fixed in Sprint 22.

**Risk if Wrong:** If these models have unrelated KKT bugs, we can't reuse Sprint 22 knowledge — each requires independent investigation, increasing effort from ~2h (pattern-based) to ~4h (from scratch) per model.

**Estimated Research Time:** 1.5h
**Owner:** Task 3 (model_infeasible triage)
**Verification Results:** 🔍 Status: INCOMPLETE

---

### KU-08: model_infeasible Influx Is Manageable

**Priority:** Critical
**Assumption:** Sprint 23's model_infeasible influx (from path_syntax_error and path_solve_terminated fixes) will be ≤ 3 models, keeping the net reduction achievable. Sprint 22 saw 5 models enter infeasible despite 5 being fixed (net zero).

**Research Questions:**
1. Sprint 22 had a 1:1 fix:influx ratio — is Sprint 23's ratio likely similar?
2. Which Priority 1 and Priority 4 fixes are most likely to cascade models into model_infeasible?
3. Does the ≤ 8 target account for both gross fixes and gross influx (per PR7)?
4. How many gross fixes are needed if influx is 2-3 models?
5. Should Sprint 23 budget extra model_infeasible fix capacity (per Sprint 22 retrospective recommendation)?

**How to Verify:** Track model_infeasible count at each checkpoint. Record gross fixes and influx separately per PR7.

**Risk if Wrong:** If influx exceeds 3, Sprint 23 needs ≥ 7 gross fixes (not just 4) to reach ≤ 8. This doubles the model_infeasible workload.

**Estimated Research Time:** 30min
**Owner:** Tasks 2, 3, 6 (cross-referenced)
**Verification Results:** 🔍 Status: INCOMPLETE

---

### KU-09: chain/rocket Are Genuinely Non-Convex Infeasibility

**Priority:** Medium
**Assumption:** chain and rocket are locally infeasible due to non-convexity, not KKT formulation bugs. Sprint 22 KU-09 confirmed they moved from path_solve_terminated to model_infeasible and PATH ran to Normal Completion.

**Research Questions:**
1. Are chain and rocket convex or non-convex NLPs?
2. Would warm-starting from NLP `.l` values change the outcome?
3. Are they candidates for permanent exclusion or re-investigation?

**How to Verify:** Already verified in Sprint 22 KU-09. Confirm classification is still accurate.

**Risk if Wrong:** Low — Sprint 22 analysis was thorough. If unexpectedly fixable, these are bonus solves.

**Estimated Research Time:** 15min (confirmation only)
**Owner:** Task 3 (model_infeasible triage)
**Verification Results:** 🔍 Status: INCOMPLETE — Sprint 22 KU-09 CONFIRMED (carryforward)

---

### KU-10: markov Multi-Pattern Jacobian Is Fixable

**Priority:** High
**Assumption:** markov's model_infeasible status (#1110) is caused by the stationarity builder using a single representative derivative for equations with multiple Jacobian patterns. The fix involves generating per-pattern stationarity equations.

**Research Questions:**
1. How many distinct Jacobian patterns does markov have per constraint?
2. Does the fix require changes to the AD engine, stationarity builder, or both?
3. Are there other models with the same multi-pattern Jacobian issue?
4. What is the regression risk of generating per-pattern stationarity?
5. Can the fix be scoped to 3-4h?

**How to Verify:** Examine markov's Jacobian structure. Count distinct derivative patterns per constraint. Design the per-pattern generation approach.

**Risk if Wrong:** If multi-pattern Jacobian generation requires deep AD engine changes, the fix could take 8-10h instead of 3-4h, consuming a significant portion of Priority 2 budget.

**Estimated Research Time:** 1.5h
**Owner:** Task 3 (model_infeasible triage)
**Verification Results:** 🔍 Status: INCOMPLETE

---

### KU-11: prolog CES Demand Singular Jacobian Is Addressable

**Priority:** Medium
**Assumption:** prolog's model_infeasible status (#1070) involves a singular Jacobian from CES (Constant Elasticity of Substitution) demand equations. This may require reformulation or improved starting points rather than a simple KKT fix.

**Research Questions:**
1. Is the singular Jacobian due to incorrect KKT assembly or inherent model structure?
2. Does prolog's CES formulation produce a degenerate Jacobian at the default starting point?
3. Would improved `.l` initialization resolve the singularity?
4. Is this related to the subcategory G set index reuse issue (Sprint 22 KU-04)?
5. Is prolog a candidate for permanent exclusion if the singularity is inherent?

**How to Verify:** Examine prolog's Jacobian at the default starting point. Check for zero rows/columns that indicate structural vs. numerical singularity.

**Risk if Wrong:** If the singularity is inherent (not a KKT bug), prolog cannot be fixed by code changes alone. It may require PATH author consultation or model reformulation — beyond Sprint 23 scope.

**Estimated Research Time:** 1h
**Owner:** Task 3 (model_infeasible triage)
**Verification Results:** 🔍 Status: INCOMPLETE

---

## Category 3: Match Rate Improvement (6 unknowns)

### KU-12: Alias-Aware Differentiation Without Regression

**Priority:** Critical
**Assumption:** The alias-aware differentiation fix (#1111) can be implemented with summation-context tracking that distinguishes "same variable via alias" from "independent iteration over same set," avoiding the regression that Sprint 22's naive fix caused in the dispatch model.

**Research Questions:**
1. How does the current AD engine track active iteration indices in Sum/Prod nodes?
2. What data structure is needed to pass bound iteration indices through `differentiate_expr()`?
3. How many models currently use aliases in differentiated expressions?
4. Does the dispatch model regression reproduce reliably for testing?
5. Can the fix be scoped to `_diff_varref()` only, or does it require broader changes?

**How to Verify:** Implement summation-context tracking. Test on qabel (known failure) and dispatch (known regression from naive fix). Run full pipeline to check for regressions.

**Risk if Wrong:** If summation-context tracking is insufficient (more complex than anticipated), the fix could take 6-8h instead of 3-4h. If it causes unanticipated regressions, the match rate could decrease rather than increase.

**Estimated Research Time:** 2h (part of Task 4 investigation)
**Owner:** Task 4 (alias differentiation investigation)
**Verification Results:** 🔍 Status: INCOMPLETE — Sprint 22 KU-27 (carryforward)

---

### KU-13: Alias Fix Selectivity

**Priority:** High
**Assumption:** The alias-aware differentiation fix will only activate for models that use aliased set indices in differentiated expressions. Models without aliases should produce identical output before and after the fix.

**Research Questions:**
1. How many of the 89 solving models use aliases?
2. How many of the 47 matching models use aliases?
3. Can the fix be guarded to skip entirely when no aliases are present?
4. What is the alias detection mechanism — compile-time (IR) or runtime (AD)?

**How to Verify:** Search for alias declarations in all model IR outputs. Count affected models. Implement guard and verify no-alias models are unchanged.

**Risk if Wrong:** If the fix is not selective (affects all models), regression testing scope expands to all 89 solving models, making verification much slower.

**Estimated Research Time:** 30min
**Owner:** Task 4 (alias differentiation investigation)
**Verification Results:** 🔍 Status: INCOMPLETE

---

### KU-14: Dollar-Condition Propagation Scope

**Priority:** High
**Assumption:** Dollar-condition propagation (#1112) primarily requires changes to the gradient computation (`src/ad/gradient.py`) to extract conditions from `DollarConditional` nodes and store them as metadata. The Jacobian may not need separate changes.

**Research Questions:**
1. Where are `DollarConditional` nodes encountered in the AD pipeline — gradient only, or also Jacobian?
2. Does the stationarity builder already have infrastructure for equation-level conditions?
3. Can condition extraction happen at gradient time and propagate naturally to Jacobian through existing code?
4. Are there models where the condition is on the Jacobian entry but not the gradient?
5. What data structure should `KKTSystem` use to store gradient conditions?

**How to Verify:** Trace `DollarConditional` handling through the AD pipeline. Examine stationarity builder for condition infrastructure. Design the propagation mechanism.

**Risk if Wrong:** If the Jacobian also needs explicit condition propagation, the fix doubles in scope (both `gradient.py` and `constraint_jacobian.py`), potentially 6-8h instead of 3-4h.

**Estimated Research Time:** 2h (part of Task 5 investigation)
**Owner:** Task 5 (dollar-condition investigation)
**Verification Results:** 🔍 Status: INCOMPLETE — Sprint 22 KU-28 (carryforward)

---

### KU-15: Independence of Alias and Dollar-Condition Fixes

**Priority:** High
**Assumption:** The alias-aware differentiation (#1111) and dollar-condition propagation (#1112) fixes are architecturally independent — they modify different parts of the AD pipeline and can be implemented and tested in any order.

**Research Questions:**
1. Do both fixes modify `_diff_varref()` or adjacent functions?
2. Could one fix's context-tracking mechanism subsume or conflict with the other's?
3. Is there a natural implementation order that reduces integration risk?
4. Do any models require both fixes to solve/match correctly?
5. Can both be tested independently before integration?

**How to Verify:** Map the code locations each fix modifies. Check for overlapping data structures or function signatures.

**Risk if Wrong:** If the fixes are coupled, they must be implemented together or in a specific order, complicating the sprint schedule. Integration bugs could require a third round of changes.

**Estimated Research Time:** 30min
**Owner:** Tasks 4, 5 (cross-referenced)
**Verification Results:** 🔍 Status: INCOMPLETE

---

### KU-16: Non-Convex Mismatch Population Is Irreducible

**Priority:** Medium
**Assumption:** Approximately 12 models that solve but don't match are non-convex NLPs where the MCP finds a different valid KKT point than the NLP solver. These are inherently non-matchable and represent a ceiling on match rate. Sprint 22 KU-29 confirmed this pattern.

**Research Questions:**
1. Has the list of non-convex mismatch models changed since Sprint 22?
2. Are any models currently classified as "non-convex mismatch" actually KKT bugs?
3. What is the maximum achievable match rate given this irreducible population?
4. Should these models be reclassified to a separate status (not counted in match targets)?

**How to Verify:** Review Sprint 22 Category B (multi-KKT-point) classification. Cross-check with full pipeline results.

**Risk if Wrong:** Low — this is well-established from Sprint 22. If some are actually fixable, they're bonus matches.

**Estimated Research Time:** 15min (confirmation)
**Owner:** Task 4 (match rate analysis)
**Verification Results:** 🔍 Status: INCOMPLETE — Sprint 22 KU-29 (carryforward)

---

### KU-17: Verified-Convex Mismatch Models Are Fixable

**Priority:** High
**Assumption:** The 7 verified-convex models that solve but don't match (from Sprint 22 KU-11 Category A analysis) have KKT formulation bugs. Fixing these bugs guarantees correct matches because convex NLPs have unique KKT points.

**Research Questions:**
1. Which 7 verified-convex models are mismatching?
2. Are the KKT bugs in the gradient, Jacobian, or stationarity assembly?
3. How many of these will be fixed by #1111 (alias) or #1112 (dollar-condition)?
4. Are any of these LP models that need the "LP KKT derivation pattern" fix identified in Sprint 22 KU-11?
5. What is the expected match improvement from fixing verified-convex models?

**How to Verify:** Review Sprint 22 divergence analysis. Identify which verified-convex models are affected by #1111 or #1112 vs. requiring independent fixes.

**Risk if Wrong:** If the KKT bugs in verified-convex models are deep architectural issues (not addressed by #1111/#1112), each requires individual investigation, consuming Priority 3 budget.

**Estimated Research Time:** 1h
**Owner:** Task 4 (alias differentiation investigation)
**Verification Results:** 🔍 Status: INCOMPLETE

---

## Category 4: path_syntax_error Residual (4 unknowns)

### KU-18: Subcategory G Aliasing Mechanism Is Sound

**Priority:** High
**Assumption:** The `resolve_index_conflicts()` mechanism in `expr_to_gams.py` correctly renames conflicting indices and updates references. Sprint 22 KU-04 verified this but identified two detection gaps: nested same-name reuse and case-insensitive collisions.

**Research Questions:**
1. Have the detection gaps (nested reuse, case-insensitive) been addressed since Sprint 22?
2. Which 2 specific subcategory G models need the enhanced detection?
3. Does the `__` suffix naming convention still avoid collisions with user-defined identifiers?
4. Can the fix be applied to just the 2 models, or does it require a general mechanism?
5. What is the regression risk of enhancing index conflict detection?

**How to Verify:** Run MCP generation for the 2 subcategory G models. Check for $409 (uncontrolled set) or $149 errors indicating index conflicts.

**Risk if Wrong:** Low — Sprint 22 verified the mechanism is sound. The remaining work is detection enhancement, estimated at 1-2h.

**Estimated Research Time:** 30min
**Owner:** Task 6 (path_syntax_error G+B triage)
**Verification Results:** 🔍 Status: INCOMPLETE — Sprint 22 KU-04 (carryforward)

---

### KU-19: Subcategory B Models Have Diverse Root Causes

**Priority:** High
**Assumption:** The 5 subcategory B models do NOT share a common emitter bug. Sprint 22 KU-03 explicitly refuted this assumption. Each model requires individual investigation and potentially different fix approaches.

**Research Questions:**
1. Which 5 models constitute the current subcategory B?
2. What specific GAMS error does each produce ($170, $141, $66, other)?
3. Are cesam/cesam2 (Sprint 22 KU-03's current Subcat B) still the primary B models?
4. Can any be grouped into sub-patterns for batch fixing?
5. What is the total effort to fix all 5 (individual fixes vs. one general fix)?

**How to Verify:** Run MCP generation for each subcategory B model. Capture and classify GAMS error output.

**Risk if Wrong:** If they unexpectedly share a common root cause, effort would be lower than estimated (good outcome). The risk is in the other direction — that individual investigation reveals even more diverse causes than expected.

**Estimated Research Time:** 1.5h
**Owner:** Task 6 (path_syntax_error G+B triage)
**Verification Results:** 🔍 Status: INCOMPLETE — Sprint 22 KU-03 (carryforward)

---

### KU-20: path_syntax_error → model_infeasible Cascade Risk

**Priority:** High
**Assumption:** Fixing 5 path_syntax_error models (Priority 4) may shift some into model_infeasible, repeating Sprint 22's net-zero pattern. Sprint 22 KU-24 predicted 7-14 at-risk models; 5 actually shifted.

**Research Questions:**
1. Which of the 7 G+B target models are at highest risk of cascading to model_infeasible?
2. Are any of the 7 CGE models (highest risk per Sprint 22 KU-24)?
3. Does the model_infeasible ≤ 8 target account for this influx?
4. Should Priority 4 fixes be scheduled before Priority 2 (so influx is known before model_infeasible work)?

**How to Verify:** After each path_syntax_error fix, run the model through the full pipeline to check for model_infeasible status.

**Risk if Wrong:** If 3+ of the 7 G+B models cascade to model_infeasible, the influx may push model_infeasible above 8 unless compensating fixes are applied.

**Estimated Research Time:** 30min
**Owner:** Task 6 (path_syntax_error G+B triage)
**Verification Results:** 🔍 Status: INCOMPLETE

---

### KU-21: New Sprint 22 Subcategories Are Low-Effort

**Priority:** Medium
**Assumption:** New subcategories discovered during Sprint 22 (K: smax/sum domain tuple mismatch for tricp; GUSS dict syntax; unquoted hyphenated labels for gtm) are relatively low effort (1-2h each) and some may be targetable in Sprint 23.

**Research Questions:**
1. How many models are affected by each new subcategory?
2. Is subcategory K (tricp, #1062) a single-model fix or does it generalize?
3. Are unquoted hyphenated labels (gtm) a preprocessor fix or grammar change?
4. Should Sprint 23 target any of these, or defer all to Sprint 24?

**How to Verify:** Review Sprint 22 catalog updates. Estimate effort for each new subcategory.

**Risk if Wrong:** If any new subcategory affects multiple models, it may be higher leverage than expected — an opportunity, not a risk.

**Estimated Research Time:** 30min
**Owner:** Task 6 (path_syntax_error G+B triage)
**Verification Results:** 🔍 Status: INCOMPLETE

---

## Category 5: Translate Failures (4 unknowns)

### KU-22: Compilation Errors Are Higher Leverage Than Timeouts

**Priority:** High
**Assumption:** Of the 15 translate failures, compilation errors (GAMS can't compile the MCP output) are faster to fix than timeouts (translation takes too long) and immediately enable models to attempt the solve stage.

**Research Questions:**
1. How many of the 15 are compilation errors vs. timeouts vs. internal errors?
2. What is the average fix time for compilation errors (based on Sprint 22 data)?
3. Do compilation error fixes typically yield solving models, or do they expose new errors?
4. Are there quick-win compilation fixes (e.g., missing parameter, wrong syntax) that can be done in ≤ 1h each?
5. Is the 2-3h budget for "Compilation Error Fixes" sufficient for 4+ models?

**How to Verify:** Run pipeline on all translate failures. Classify each as compilation error, timeout, or internal error.

**Risk if Wrong:** If most failures are timeouts (not compilation errors), the ≤ 11 target requires timeout investigation, which may be architecturally intractable per Sprint 22 KU-22.

**Estimated Research Time:** 1h (part of Task 7 catalog)
**Owner:** Task 7 (translate failures catalog)
**Verification Results:** 🔍 Status: INCOMPLETE

---

### KU-23: Timeout Models Are Architecturally Intractable

**Priority:** Medium
**Assumption:** Translate timeout models follow the gastrans pattern (Sprint 22 KU-22): they require architectural Jacobian changes (sparsity-aware computation or dynamic subset preservation) that are beyond Sprint 23 scope.

**Research Questions:**
1. Do all timeout models involve Jacobian computation, or do some timeout in other stages?
2. Is there a simple "increase timeout" fix for borderline cases?
3. Could recursion limit increases (currently 50,000) help any timeout models?
4. Are any timeout models close enough to the limit that optimization (not architecture) would suffice?

**How to Verify:** Profile timeout models to identify the bottleneck stage. Measure time vs. limit proximity.

**Risk if Wrong:** If some timeout models are fixable with simple optimizations, Sprint 23 could gain additional translate successes beyond the ≤ 11 target — an opportunity.

**Estimated Research Time:** 1h
**Owner:** Task 7 (translate failures catalog)
**Verification Results:** 🔍 Status: INCOMPLETE — Sprint 22 KU-22 (carryforward)

---

### KU-24: 4 Compilation Fixes Reach ≥ 145/156 Translate Target

**Priority:** High
**Assumption:** The translate rate target (≥ 145/156 = 93%) requires fixing 4 of the 15 translate failures (141 → 145). This is achievable if at least 4 of the compilation error models have straightforward fixes.

**Research Questions:**
1. Exactly how many of the 15 failures are compilation errors (fixable) vs. timeouts (likely intractable)?
2. Are there at least 4 compilation errors with known fixes or existing issues?
3. Do the 4 easiest compilation fixes have dependencies on other Sprint 23 work?
4. Will fixing compilation errors create models that then fail at solve (adding to path_syntax_error or path_solve_terminated)?
5. Are existing issues #952 (lmp2), #953 (paperco), #940 (mexls), #1062 (tricp) the best candidates?

**How to Verify:** Catalog all 15 failures. Identify the 4-5 easiest compilation error fixes. Verify they are independent of other Sprint 23 work.

**Risk if Wrong:** If fewer than 4 failures are compilation errors (most are timeouts), the ≥ 145/156 target requires fixing timeouts, which may be infeasible.

**Estimated Research Time:** 1h
**Owner:** Task 7 (translate failures catalog)
**Verification Results:** 🔍 Status: INCOMPLETE

---

### KU-25: paperco and lmp2 Loop-Body Issues Share Root Cause

**Priority:** Medium
**Assumption:** paperco (#953: loop body parameter assignment not emitted) and lmp2 (#952: empty dynamic subsets and loop body assignments not emitted) both involve the emitter failing to handle loop-body assignments. They may share a common root cause in `src/emit/emit_gams.py`.

**Research Questions:**
1. Do both issues involve the same emitter code path?
2. Is the problem in IR construction (loop body not parsed into IR) or emission (IR present but not emitted)?
3. Would fixing the common root cause resolve both models simultaneously?
4. Are there other models with loop-body assignment issues?

**How to Verify:** Compare the IR output for paperco and lmp2. Check if loop body assignments are present in the IR but missing from emitted GAMS.

**Risk if Wrong:** If the root causes are different, fixing one doesn't help the other. Low impact — they're separate 1-2h fixes either way.

**Estimated Research Time:** 30min
**Owner:** Task 7 (translate failures catalog)
**Verification Results:** 🔍 Status: INCOMPLETE

---

## Sprint 22 Carryforward (1 unknown)

### KU-26: Multi-Solve Incomparable Classification Is Stable

**Priority:** Low
**Assumption:** Models classified as "incomparable" in Sprint 22 (senstran, aircraft, sparta for multi-solve; apl1p, apl1pca for stochastic) remain correctly classified. The pipeline already skips comparison for these models (PR #1103).

**Research Questions:**
1. Has the list of incomparable models changed since Sprint 22?
2. Are any models incorrectly classified as incomparable that could actually match?
3. Does the incomparable classification affect Sprint 23 match rate targets?

**How to Verify:** Review pipeline skip list. Confirm no changes since Sprint 22 KU-30.

**Risk if Wrong:** Negligible — this is well-established and the pipeline handles it correctly.

**Estimated Research Time:** 10min (confirmation)
**Owner:** Task 8 (baseline metrics)
**Verification Results:** 🔍 Status: INCOMPLETE — Sprint 22 KU-30 (carryforward)

---

## Appendix A: Task-to-Unknown Mapping

This table maps each PREP_PLAN.md task to the unknowns it should verify during execution.

| Task | Unknowns to Verify | Verification Method |
|------|--------------------|--------------------|
| Task 1 (Known Unknowns) | — | This document |
| Task 2 (path_solve_terminated Triage) | KU-01, KU-02, KU-03, KU-04, KU-05 | Run MCP generation + solve for all 10 models; classify error types |
| Task 3 (model_infeasible Triage) | KU-06, KU-07, KU-08, KU-09, KU-10, KU-11 | Run MCP generation for all 12 models; classify infeasibility source |
| Task 4 (Alias Differentiation Investigation) | KU-12, KU-13, KU-15, KU-16, KU-17 | Trace AD pipeline; design summation-context tracking; count alias-using models |
| Task 5 (Dollar-Condition Investigation) | KU-14, KU-15 | Trace DollarConditional through AD pipeline; assess gradient vs Jacobian scope |
| Task 6 (path_syntax_error G+B Triage) | KU-18, KU-19, KU-20, KU-21 | Run MCP generation for 7 G+B models; classify error types per model |
| Task 7 (Translate Failures Catalog) | KU-22, KU-23, KU-24, KU-25 | Run pipeline on all translate failures; classify as compilation/timeout/internal |
| Task 8 (Full Pipeline Baseline) | KU-26 | Full pipeline run; confirm incomparable classifications; record baseline metrics |
| Task 9 (Retrospective Alignment) | (all remaining) | Verify Sprint 22 process recommendations are integrated |
| Task 10 (Detailed Schedule) | (synthesis) | Incorporate all verification results into sprint plan |

---

## Appendix B: Priority Distribution

| Priority | Count | Unknowns |
|----------|-------|----------|
| Critical | 5 | KU-01, KU-02, KU-06, KU-08, KU-12 |
| High | 14 | KU-03, KU-04, KU-05, KU-07, KU-10, KU-13, KU-14, KU-15, KU-17, KU-18, KU-19, KU-20, KU-22, KU-24 |
| Medium | 6 | KU-09, KU-11, KU-16, KU-21, KU-23, KU-25 |
| Low | 1 | KU-26 |

**All Critical unknowns have verification plans assigned to Tasks 2-4 (highest priority prep tasks). High unknowns are distributed across Tasks 2-7.**

---

## Appendix C: Verification Status Tracking

Use this template during Sprint 23 prep and execution to track verification results.

| ID | Verified? | Date | Result | Action Taken |
|----|-----------|------|--------|-------------|
| KU-01 | | | | |
| KU-02 | | | | |
| KU-03 | | | | |
| KU-04 | | | | |
| KU-05 | | | | |
| KU-06 | | | | |
| KU-07 | | | | |
| KU-08 | | | | |
| KU-09 | | | | |
| KU-10 | | | | |
| KU-11 | | | | |
| KU-12 | | | | |
| KU-13 | | | | |
| KU-14 | | | | |
| KU-15 | | | | |
| KU-16 | | | | |
| KU-17 | | | | |
| KU-18 | | | | |
| KU-19 | | | | |
| KU-20 | | | | |
| KU-21 | | | | |
| KU-22 | | | | |
| KU-23 | | | | |
| KU-24 | | | | |
| KU-25 | | | | |
| KU-26 | | | | |

---

## Appendix D: Cross-References

### Source Documents
- `docs/planning/EPIC_4/PROJECT_PLAN.md` (lines 629-740) — Sprint 23 scope
- `docs/planning/EPIC_4/SPRINT_22/SPRINT_RETROSPECTIVE.md` — Sprint 22 retrospective with Sprint 23 recommendations
- `docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md` — Sprint 22 Known Unknowns (KU-27–KU-30 carry forward)
- `docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md` — Sprint 23 preparation plan
- `docs/planning/EPIC_4/GOALS.md` — Epic 4 overarching goals

### Sprint 22 Carryforward KUs
- Sprint 22 KU-27 → Sprint 23 KU-12 (alias-aware differentiation)
- Sprint 22 KU-28 → Sprint 23 KU-14 (dollar-condition propagation)
- Sprint 22 KU-29 → Sprint 23 KU-16 (non-convex multi-KKT divergence)
- Sprint 22 KU-30 → Sprint 23 KU-26 (multi-solve incomparable)

### Key GitHub Issues (sprint-23 label)
- #1112: Dollar-condition propagation through AD/stationarity pipeline
- #1111: Alias-aware differentiation with summation-context tracking
- #1110: markov multi-pattern Jacobian
- #1091: Reclassify Category D models as Category B
- #1089: qabel regression
- #1081: sparta KKT bug
- #1070: prolog singular Jacobian
- #1062: tricp sparse edge-set conditioning
- #1061: tforss NA parameter propagation
- #1049: pak incomplete stationarity
- #1041: cesam2 empty equation
- #1038: spatequ Jacobian domain mismatch
- #986: lands NA values
- #983: elec division by zero
- #956: nonsharp compilation errors
- #953: paperco loop body parameter
- #952: lmp2 empty dynamic subsets
- #945: launch per-instance stationarity
- #940: mexls universal set
- #919: sroute empty stationarity
- #918: qdemo7 conditionally-absent variables
- #882: camcge subset bound complementarity
- #871: camcge stationarity subset conditioning
- #862: sambal domain conditioning

---

**Document Created:** 2026-03-17
**Total Unknowns:** 26 (across 5 categories + 1 carryforward)
**Sprint 22 Carryforward:** 4 KUs (KU-27→KU-12, KU-28→KU-14, KU-29→KU-16, KU-30→KU-26)
**Next Steps:** Verify unknowns during prep Tasks 2-8; update Appendix C with results
