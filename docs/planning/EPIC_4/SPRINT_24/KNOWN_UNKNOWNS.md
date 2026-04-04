# Sprint 24 Known Unknowns

**Created:** 2026-04-03
**Sprint:** 24 (Prep Task 1)
**Status:** Initial — all unknowns pending verification
**Last Updated:** 2026-04-03

---

## Purpose

This document catalogs assumptions and unknowns for Sprint 24 (Alias Differentiation & Error Category Reduction). Each unknown has a priority, assumption, research questions, verification method, and risk assessment. The goal is to prevent late discoveries during implementation by surfacing uncertainties early.

**Process:** Sprint 23 Known Unknowns (32 entries) proved effective — KU-27 (subset-superset domain) led to a high-impact fix, and KU-31 (LP fast path limitations) proved accurate. Sprint 24's alias differentiation work is architecturally complex and requires thorough risk identification.

**Sprint 24 Targets (147-model pipeline scope per PR9):**
- Parse: ≥ 147/147 (maintain 100%)
- Translate: ≥ 143/147 (97%)
- Solve: ≥ 95
- Match: ≥ 55
- path_syntax_error: ≤ 15
- path_solve_terminated: ≤ 10
- model_infeasible: ≤ 8
- Tests: ≥ 4,400

---

## How to Use This Document

| Priority | Definition | Verification Deadline |
|----------|------------|----------------------|
| **Critical** | Blocks sprint success if wrong; must verify Day 0-1 | Task 2-3 (before implementation) |
| **High** | Significant impact on effort/outcome; verify Day 2-3 | Task 4-7 (during triage) |
| **Medium** | Moderate impact; may require mid-sprint adjustment | Day 5-7 (Checkpoint 1) |
| **Low** | Minor impact; document for awareness | Day 10+ (Checkpoint 2) |

---

## Summary Statistics

- **Total Unknowns:** 26
- **Priority Distribution:** 7 Critical (27%), 10 High (38%), 7 Medium (27%), 2 Low (8%)
- **Estimated Total Research Time:** 21-29 hours
- **Categories:** 4 major + 1 cross-cutting + 1 carryforward

---

## Summary Table

| ID | Category | Unknown | Priority | Verification Deadline |
|----|----------|---------|----------|-----------------------|
| KU-01 | Alias Differentiation | Summation-context threading scope | Critical | Task 2 |
| KU-02 | Alias Differentiation | Single vs. multi-pattern root cause | Critical | Task 2 |
| KU-03 | Alias Differentiation | Regression risk for 49 matching models | Critical | Task 2-3 |
| KU-04 | Alias Differentiation | Offset-alias interaction complexity | High | Task 2 |
| KU-05 | Alias Differentiation | sameas guard generation correctness | High | Task 3 |
| KU-06 | Alias Differentiation | Incremental vs. big-bang rollout | High | Task 3 |
| KU-07 | Alias Differentiation | CGE model alias patterns | Medium | Task 2 |
| KU-08 | Alias Differentiation | Quadratic form alias handling | Medium | Task 2 |
| KU-09 | path_syntax_error | Influx models share common patterns | High | Task 4 |
| KU-10 | path_syntax_error | Alias differentiation fixes path_syntax_error overlap | High | Task 4 |
| KU-11 | path_syntax_error | Concrete element offset fixability | High | Task 4 |
| KU-12 | path_syntax_error | Uncontrolled set reference batch fix | Medium | Task 4 |
| KU-13 | path_syntax_error | Error influx from alias differentiation | Medium | Task 4 |
| KU-14 | model_infeasible | Jacobian accuracy overlap with alias fix | High | Task 5 |
| KU-15 | model_infeasible | bearing Jacobian completeness | High | Task 5 |
| KU-16 | model_infeasible | chenery post-$171 fix root cause | Medium | Task 5 |
| KU-17 | model_infeasible | New influx from alias differentiation | Critical | Task 5 |
| KU-18 | model_infeasible | Category B models fixable without PATH changes | Low | Task 5 |
| KU-19 | Translation | Timeout models fundamentally intractable | Medium | Task 6 |
| KU-20 | Translation | Sparse Jacobian feasibility | Medium | Task 6 |
| KU-21 | Translation | Internal error root cause | Low | Task 6 |
| KU-22 | Sprint 23 Carryforward | Dynamic `.up` bounds resolution (KU-28) | High | Task 4 |
| KU-23 | Sprint 23 Carryforward | Concrete element offsets in stationarity (KU-29) | High | Task 4 |
| KU-24 | Sprint 23 Carryforward | Duplicate `.fx` emission (KU-32) | Medium | Day 10+ |
| KU-25 | Cross-cutting | Error influx budget accuracy (PR10 ~40% rule) | Critical | Task 7 |
| KU-26 | Cross-cutting | Alias differentiation effort estimate | Critical | Task 3 |

---

## Category 1: Alias-Aware Differentiation

### KU-01: Summation-Context Threading Scope

**Priority:** Critical
**Assumption:** Summation-context tracking only needs to be added to `_diff_varref` and `_partial_collapse_sum` (2 functions).

**Research Questions:**
1. Does the context need to flow through `_diff_sum`, `_diff_binary`, `_diff_unary` as well?
2. How does `_diff_call` (for built-in functions) interact with summation context?
3. Does `_add_indexed_jacobian_terms` in stationarity.py need context changes too?
4. Are there other derivative rules that assume free indices?

**How to Verify:**
- Trace the derivative chain for a model with alias in sum: `sum(j, f(x(i,j)))` diff w.r.t. `x(i,j)`
- Identify all functions that receive/pass the index tuple
- Count functions needing modification

**Risk if Wrong:** Underestimate implementation scope by 50%+; mid-sprint redesign needed
**Estimated Research Time:** 2-3h
**Owner:** Task 2
**Verification Results:** :white_check_mark: Status: VERIFIED — Context needs to flow through `_diff_sum` (to collect bound indices), `_diff_varref` (to check alias match), and `_partial_collapse_sum` (to preserve context). `_diff_binary`/`_diff_unary`/`_diff_call` pass through transparently. `_add_indexed_jacobian_terms` in stationarity.py does NOT need changes — it operates at a higher level. **3 existing functions need modification**: `_diff_sum`, `_diff_varref`, and `_partial_collapse_sum`. **2 new helpers should be added**: `_alias_match` and `_same_root_set`.

### KU-02: Single vs. Multi-Pattern Root Cause

**Priority:** Critical
**Assumption:** The 12 alias-differentiation issues (#1137-#1147, #1150) share 1-2 common root cause patterns fixable with a single architectural change.

**Research Questions:**
1. Do all 12 issues fail in `_diff_varref` or do some fail elsewhere (emitter, stationarity)?
2. Is #1150 (distinct sum indices collapse) the same mechanism as #1137-#1147?
3. Are offset-alias issues (#1143 polygon, #1146 himmel16) a distinct pattern from pure alias issues?
4. Do CGE models (#1138) have a different root cause than quadratic models (#1137)?
5. How many distinct fix patterns are needed?

**How to Verify:**
- Reproduce gradient mismatch for each of the 12 issues
- Classify each by the function where the error originates
- Group by pattern

**Risk if Wrong:** Need 4+ separate fixes instead of 1 architectural change; sprint effort doubles
**Estimated Research Time:** 4-5h
**Owner:** Task 2
**Verification Results:** :x: Status: PARTIALLY WRONG — 5 patterns identified, not 1-2. However, Pattern A (summation index) covers 6 of 12 issues (~14 models) and the main architectural change (`bound_indices` + `_alias_match`) addresses Patterns A-C (10 of 12 issues). Pattern D (condition-scope, 1 issue) needs separate investigation. Pattern E (2 issues: catmix, camshape) are non-differentiation bugs. **Net: single architectural change covers 10/12 + 1 post-investigation item + 2 separate PRs.**

### KU-03: Regression Risk for 49 Matching Models

**Priority:** Critical
**Assumption:** Fixing alias differentiation will not regress any of the 49 currently-matching models.

**Research Questions:**
1. How many of the 49 matching models use aliases? (Sprint 23 design says 8 of 47)
2. Do any matching models depend on the current (incorrect) derivative behavior?
3. Can we create golden-file tests for all 49 models' stationarity equations?
4. What's the minimum regression test that catches breakage?

**How to Verify:**
- Count alias usage in matching models
- Generate and store current stationarity output for all 49
- Identify models where derivative changes would alter the equation structure

**Risk if Wrong:** Lose 5-10 matching models; net match rate decreases instead of increases
**Estimated Research Time:** 2-3h
**Owner:** Task 2-3
**Verification Results:** :white_check_mark: Status: VERIFIED — Only 8 of 49 matching models use aliases (16.3%): dispatch, gussrisk, nemhaus, ps2_f, ps3_f, quocge, ship, splcge. The `bound_indices` guard specifically prevents the Sprint 22 dispatch regression. 41 non-alias models have zero risk. **Regression risk is VERY LOW** — 8 exposed models are all protected by the bound_indices guard. dispatch is the critical canary test.

### KU-04: Offset-Alias Interaction Complexity

**Priority:** High
**Assumption:** Offset expressions with aliases (e.g., `x(i+1)` where `i` aliases `n`) can be handled by the same summation-context approach.

**Research Questions:**
1. Does `IndexOffset` interact with alias resolution in `_diff_varref`?
2. Does the circular offset guard (`++`/`--`) affect alias matching?
3. Are polygon (#1143, 100% mismatch) and himmel16 (#1146, 43%) both offset-alias issues?
4. Does `_apply_offset_substitution` need alias awareness?

**How to Verify:**
- Examine polygon and himmel16 stationarity output
- Trace the offset path through the derivative chain
- Test if summation-context alone fixes offset-alias models

**Risk if Wrong:** Offset-alias models need a separate fix path; +4-6h additional effort
**Estimated Research Time:** 2-3h
**Owner:** Task 2
**Verification Results:** :white_check_mark: Status: VERIFIED — Offset-alias is Pattern C, affecting polygon (#1143, 100% mismatch) and himmel16 (#1146, 43%). The `_alias_match()` helper needs `IndexOffset.base` extraction for comparison. This is included in the main fix but is highest-risk — polygon shows complete gradient failure with concrete element offsets (`i1+1`) instead of symbolic. **Effort is included in main 8-10h estimate but success probability is 55-65%.**

### KU-05: sameas Guard Generation Correctness

**Priority:** High
**Assumption:** Free alias indices should generate `sameas(np, n)` guards that GAMS evaluates correctly at runtime.

**Research Questions:**
1. Does GAMS `sameas()` work correctly with all set element types (numeric, string, dotted)?
2. Can `sameas` guards be combined with existing dollar conditions without scope conflicts?
3. How do `sameas` guards interact with `resolve_index_conflicts` in `expr_to_gams.py`?
4. What's the performance impact of `sameas` guards on large models?

**How to Verify:**
- Generate a test MCP with `sameas` guards and compile in GAMS
- Test with numeric, string, and dotted elements
- Benchmark compilation time with/without guards

**Risk if Wrong:** Generated MCPs compile but give wrong results; hard-to-debug correctness issues
**Estimated Research Time:** 1-2h
**Owner:** Task 3
**Verification Results:** :warning: Status: PARTIALLY VERIFIED — Implementation confirmed: `_alias_match()` generates `sameas()` guards via `Call("sameas", (SymbolRef(expr_str), SymbolRef(wrt_str)))`. Guards are combined via `Binary("*", ...)` for multi-dimension aliases, and the emitter handles `sameas()` as a standard GAMS built-in. **Guard generation verified. GAMS compile/runtime validation for numeric, string, and dotted elements, plus compile-time benchmarking with/without guards, remains pending.**

### KU-06: Incremental vs. Big-Bang Rollout

**Priority:** High
**Assumption:** Alias differentiation can be rolled out incrementally (one pattern at a time) without intermediate states causing additional regressions.

**Research Questions:**
1. Can Pattern A (free alias) be fixed independently of Pattern C (offset-alias)?
2. Does fixing some patterns change the error category for unfixed patterns?
3. Is there a natural ordering (easy → hard) for pattern fixes?
4. Can we feature-flag the alias changes per model?

**How to Verify:**
- Design a rollout plan with Pattern A first
- Estimate intermediate metrics after Pattern A only
- Identify models that move between error categories during partial rollout

**Risk if Wrong:** Intermediate states cause cascading regressions; must do all-or-nothing
**Estimated Research Time:** 1-2h
**Owner:** Task 3
**Verification Results:** :white_check_mark: Status: VERIFIED — Incremental rollout is feasible. The architecture is already implemented; Sprint 24 work is debugging edge cases. Pattern A can be debugged independently of Pattern C (offset-alias). Recommended: Phase 1 (Pattern A debug, Days 1-3) → Phase 2 (validate, Days 3-5) → Phase 3 (Pattern C, Days 5-7) → Phase 4 (B/D investigation, Days 7-9). **Decision criteria: proceed if 0 regressions and ≥2 models improve per phase.**

### KU-07: CGE Model Alias Patterns

**Priority:** Medium
**Assumption:** CGE models (irscge, lrgcge, moncge, stdcge — issue #1138) share the same alias pattern and can be fixed together.

**Research Questions:**
1. Do all 4 CGE models use the same alias structure?
2. Is the CGE alias pattern (Armington, CET, production function) a specific subcategory?
3. Do the 4 models have similar relative divergence (1.0%-2.2%) suggesting a common root cause?

**How to Verify:**
- Compare alias usage across the 4 CGE models
- Check if divergence patterns are correlated

**Risk if Wrong:** Need per-model CGE fixes instead of batch fix; +4h effort
**Estimated Research Time:** 1-2h
**Owner:** Task 2
**Verification Results:** :white_check_mark: Status: VERIFIED — All 4 CGE models (irscge 2.2%, lrgcge 1.0%, moncge 1.8%, stdcge ~1%) share Pattern A (summation index not tracked). Small relative divergences (1-2%) suggest near-correctness — the alias fix should bring all 4 to match. **Batch fix confirmed; single Pattern A fix covers all CGE models.**

### KU-08: Quadratic Form Alias Handling

**Priority:** Medium
**Assumption:** Quadratic forms with aliases (qabel/abel #1137, meanvar #1139) are handled by the general alias fix, not a special case.

**Research Questions:**
1. Does `sqr(x(i))` differentiation interact differently with aliases than linear `x(i)`?
2. Does the chain rule in `_diff_call` preserve alias context correctly?
3. Are the 29.8% (abel) and 12.3% (meanvar) divergences from the same mechanism?

**How to Verify:**
- Trace derivative chain for `sqr(x(alias_index))`
- Compare with linear `x(alias_index)` derivative

**Risk if Wrong:** Quadratic alias models need separate handling; +2-3h effort
**Estimated Research Time:** 1h
**Owner:** Task 2
**Verification Results:** :white_check_mark: Status: VERIFIED — Quadratic forms (qabel/abel 29.8%, meanvar 12.3%) are Pattern A — the chain rule in `_diff_call` for `sqr()` passes through transparently, so alias context flows correctly through the quadratic derivative. **No special handling needed; general Pattern A fix covers quadratic forms.**

---

## Category 2: path_syntax_error Reduction

### KU-09: Influx Models Share Common Patterns

**Priority:** High
**Assumption:** The newly-translating models that entered path_syntax_error share subcategory patterns with existing errors (A/B/C/G).

**Research Questions:**
1. Which models entered path_syntax_error from Sprint 23 translate recovery?
2. Do they share GAMS compilation error codes ($141, $149, $171, etc.)?
3. Are any of them fixed by alias differentiation (Priority 1)?
4. How many are in subcategories already analyzed (G, B, C)?

**How to Verify:**
- Compile each new path_syntax_error model's MCP in GAMS
- Classify error codes by subcategory
- Cross-reference with alias differentiation issue list

**Risk if Wrong:** New subcategories require new fix patterns; influx models are harder than expected
**Estimated Research Time:** 2-3h
**Owner:** Task 4
**Verification Results:** :x: Status: WRONG — Influx models do NOT share a single pattern. 11 new models span 3 subcategories: H (concrete offsets, 8 models), A (missing data, 2), C (dynamic sets, 1). The dominant new pattern is subcategory H (concrete element offsets like set(i+1)), which was not in the Sprint 23 triage.

### KU-10: Alias Differentiation Fixes path_syntax_error Overlap

**Priority:** High
**Assumption:** Some path_syntax_error models fail because incorrect derivatives generate invalid GAMS code; fixing aliases will eliminate those errors.

**Research Questions:**
1. How many of the 24 path_syntax_error models use aliases?
2. Which models have compilation errors in stationarity equations (vs. original equations)?
3. Does fixing the derivative change the equation structure enough to eliminate syntax errors?
4. Can we identify the overlap without implementing the full alias fix?

**How to Verify:**
- Check alias usage in path_syntax_error models
- Identify models where syntax errors are in stationarity equations

**Risk if Wrong:** No overlap — all 8+ fixes must come from dedicated path_syntax_error work
**Estimated Research Time:** 1-2h
**Owner:** Task 4
**Verification Results:** :white_check_mark: Status: VERIFIED — 18 of 24 (75%) path_syntax_error models use aliases. All 8 subcategory H models have aliases. Alias differentiation may fix some indirectly by improving derivative accuracy, but the primary fix for subcategory H is IndexOffset handling in set domains, not alias matching.

### KU-11: Concrete Element Offset Fixability

**Priority:** High
**Assumption:** The concrete element offset issue (Sprint 23 KU-29: `i1+1`, `s1-1` in stationarity) can be fixed by converting element offsets to symbolic index offsets in the stationarity builder.

**Research Questions:**
1. How many path_syntax_error models are affected by concrete element offsets?
2. Is the fix in `_apply_offset_substitution` or in `_replace_indices_in_expr`?
3. Does the fix interact with alias differentiation changes?
4. What's the fix effort — surgical or architectural?

**How to Verify:**
- Count models with concrete element references in stationarity output
- Trace the code path that generates concrete elements
- Estimate fix scope

**Risk if Wrong:** Architectural change needed in stationarity builder; +6-8h effort
**Estimated Research Time:** 2h
**Owner:** Task 4
**Verification Results:** :white_check_mark: Status: VERIFIED — 8 models affected by concrete element offsets (subcategory H). The fix is in the stationarity builder/emitter handling of IndexOffset in set domain contexts (e.g., nh(i+1)). Single architectural fix estimated at 4-6h. This is the highest-leverage subcategory for the ≤15 target.

### KU-12: Uncontrolled Set Reference Batch Fix

**Priority:** Medium
**Assumption:** Uncontrolled set references (subcategory A) in path_syntax_error models can be fixed with a single emitter/stationarity change.

**Research Questions:**
1. How many models have uncontrolled set references as their primary error?
2. Is the pattern always `$(set(uncontrolled_var))` on the equation body?
3. Does the fix conflict with dollar condition propagation?

**How to Verify:**
- Count subcategory A models
- Check if a single pattern explains the majority

**Risk if Wrong:** Multiple subcategory A patterns; need per-model fixes
**Estimated Research Time:** 1h
**Owner:** Task 4
**Verification Results:** :white_check_mark: Status: VERIFIED — Subcategory A (missing data) has 9 models but they do NOT share a single uncontrolled-set pattern. Each has different missing parameters/subsets. Batch fix not feasible; per-model fixes needed (2-3h each). Small models (decomp, ramsey, worst) are best candidates.

### KU-13: Error Influx from Alias Differentiation

**Priority:** Medium
**Assumption:** Fixing alias differentiation will not introduce new path_syntax_error models (i.e., changing derivatives won't generate invalid GAMS syntax).

**Research Questions:**
1. Can `sameas` guard generation produce invalid GAMS syntax?
2. Can changing derivative expressions create domain violations ($171)?
3. Does the stationarity builder's equation structure change with new derivatives?

**How to Verify:**
- After alias fix, compile all currently-clean models' MCPs
- Check for new compilation errors

**Risk if Wrong:** Alias fix creates 3-5 new path_syntax_error; net improvement is less than expected
**Estimated Research Time:** 1h (verify during implementation)
**Owner:** Task 4
**Verification Results:** :mag: Status: INCOMPLETE — Cannot verify until alias differentiation is implemented. However, the 8 subcategory H models already have compilation errors, so alias fixes are unlikely to make them worse. Risk is primarily for currently-clean models gaining new errors from changed derivatives.

---

## Category 3: model_infeasible Reduction

### KU-14: Jacobian Accuracy Overlap with Alias Fix

**Priority:** High
**Assumption:** Several model_infeasible models are infeasible because of incorrect Jacobian entries from alias differentiation errors, and fixing aliases will recover them.

**Research Questions:**
1. Which of the 11 model_infeasible models use aliases?
2. Do bearing (#1199) and chenery (#1177) have alias-related Jacobian errors?
3. How many model_infeasible models would move to model_optimal with correct derivatives?
4. Is catmix (#1144) a model_infeasible caused by alias regression?

**How to Verify:**
- Check alias usage in model_infeasible models
- For alias-using infeasible models, check if stationarity equations have incorrect derivative terms

**Risk if Wrong:** No overlap — dedicated Jacobian fixes needed for all 6+ models
**Estimated Research Time:** 2h
**Owner:** Task 5
**Verification Results:** :mag: Status: INCOMPLETE

### KU-15: bearing Jacobian Completeness

**Priority:** High
**Assumption:** bearing's MODEL STATUS 5 is caused by missing or incorrect Jacobian entries that can be fixed by improving derivative accuracy.

**Research Questions:**
1. Which stationarity equations have insufficient multiplier terms?
2. Are the constraint Jacobian entries correct for the nonlinear constraints?
3. Does the variable initialization contribute to infeasibility, or is it structural?
4. Is this an alias issue or a separate derivative bug?

**How to Verify:**
- Compare generated stationarity against hand-computed KKT for bearing's 7 constraints
- Check if all constraint derivatives are present

**Risk if Wrong:** bearing requires warm-start or PATH parameter tuning, not a code fix
**Estimated Research Time:** 2-3h
**Owner:** Task 5
**Verification Results:** :mag: Status: INCOMPLETE

### KU-16: chenery Post-$171 Fix Root Cause

**Priority:** Medium
**Assumption:** chenery's MODEL STATUS 5 after the $171 domain widening fix is caused by incorrect derivative terms, not by the domain widening itself.

**Research Questions:**
1. Did the domain widening change the equation structure in a way that makes the KKT infeasible?
2. Is the infeasibility at the initial point or structural?
3. Does chenery use aliases? If so, would alias differentiation help?

**How to Verify:**
- Compare chenery MCP before and after $171 fix
- Check if infeasibility residuals suggest incorrect Jacobian vs. bad starting point

**Risk if Wrong:** chenery needs domain widening reversal or alternative approach; blocks ≤ 8 target
**Estimated Research Time:** 1-2h
**Owner:** Task 5
**Verification Results:** :mag: Status: INCOMPLETE

### KU-17: New Influx from Alias Differentiation

**Priority:** Critical
**Assumption:** Fixing alias differentiation will not cause currently-solving models to become infeasible.

**Research Questions:**
1. Can changing derivative values make a previously-feasible KKT system infeasible?
2. Does the `sameas` guard change the constraint count or equation structure?
3. Which solving-but-not-matching models are most at risk of becoming infeasible?
4. How can we detect infeasibility regressions early?

**How to Verify:**
- After alias fix, check MODEL STATUS for all 86 currently-solving models
- Compare multiplier values before/after for models near the feasibility boundary

**Risk if Wrong:** Lose 3-5 solving models to infeasibility; net solve decrease
**Estimated Research Time:** 1h (verify during implementation)
**Owner:** Task 5
**Verification Results:** :mag: Status: INCOMPLETE

### KU-18: Category B Models Fixable Without PATH Changes

**Priority:** Low
**Assumption:** Category B model_infeasible models (PATH convergence failures: chain, cpack, mathopt3, lnts, robustlp) cannot be fixed by code changes alone and require PATH parameter tuning or warm-starting.

**Research Questions:**
1. Does warm-starting from the NLP solution help any Category B models?
2. Can PATH tolerances (`major_iteration_limit`, `proximal_perturbation`) recover convergence?
3. Are any Category B models actually KKT formulation bugs misclassified?

**How to Verify:**
- Test warm-start for one Category B model
- Test PATH parameter variations

**Risk if Wrong:** Some Category B models are easily fixable; missed opportunity for ≤ 8 target
**Estimated Research Time:** 2h
**Owner:** Task 5
**Verification Results:** :mag: Status: INCOMPLETE

---

## Category 4: Translation Timeout & Internal Error

### KU-19: Timeout Models Fundamentally Intractable

**Priority:** Medium
**Assumption:** The remaining 6 timeout models (including lop, mexls) are too large for symbolic differentiation within 300s and require algorithmic improvements to the stationarity builder.

**Research Questions:**
1. What are the model sizes (equations, variables, constraint density)?
2. Where does the stationarity builder spend most time (AD, Jacobian assembly, expression simplification)?
3. Is the bottleneck quadratic in model size or worse?
4. Would doubling the timeout to 600s help any models?

**How to Verify:**
- Profile translation for each timeout model
- Measure time breakdown by phase

**Risk if Wrong:** Models are tractable with simple optimization; missed +3 translates
**Estimated Research Time:** 2-3h
**Owner:** Task 6
**Verification Results:** :mag: Status: INCOMPLETE

### KU-20: Sparse Jacobian Feasibility

**Priority:** Medium
**Assumption:** Sparse Jacobian techniques (only computing non-zero entries) can significantly reduce translation time for large models.

**Research Questions:**
1. What fraction of Jacobian entries are structurally zero for timeout models?
2. Can sparsity be determined statically from the equation structure?
3. What's the implementation effort for sparse Jacobian in the stationarity builder?
4. Does sparse Jacobian interact with the LP fast path?

**How to Verify:**
- Count non-zero vs. total Jacobian entries for a timeout model
- Estimate speedup from skipping zero entries

**Risk if Wrong:** Most entries are non-zero; sparse approach doesn't help
**Estimated Research Time:** 2h
**Owner:** Task 6
**Verification Results:** :mag: Status: INCOMPLETE

### KU-21: Internal Error Root Cause

**Priority:** Low
**Assumption:** The 1 internal_error model has a straightforward bug in the translation pipeline that can be fixed with a targeted code change.

**Research Questions:**
1. Which model has the internal error?
2. What exception is raised and where?
3. Is it a known pattern (e.g., unsupported expression type) or new?

**How to Verify:**
- Run the model with verbose logging
- Capture the traceback

**Risk if Wrong:** Internal error is a deep architectural issue; not fixable in Sprint 24
**Estimated Research Time:** 1h
**Owner:** Task 6
**Verification Results:** :mag: Status: INCOMPLETE

---

## Category 5: Sprint 23 Carryforward

### KU-22: Dynamic `.up` Bounds Resolution (Sprint 23 KU-28)

**Priority:** High
**Assumption:** The KKT generator can be enhanced to resolve dynamic `.up`/`.lo` bounds set in loops, enabling correct upper-bound complementarity equations.

**Research Questions:**
1. How many models set bounds dynamically in loops vs. statically?
2. Can we extract the bound value from the loop body at parse time?
3. Does this overlap with the `LoopStatement` processing in `model_ir.py`?

**How to Verify:**
- Count models with dynamic bound assignments
- Check if `VariableDef.up_map`/`lo_map` captures loop-assigned bounds

**Risk if Wrong:** Dynamic bounds require runtime evaluation; can't be resolved at compile time
**Estimated Research Time:** 1-2h
**Owner:** Task 4
**Verification Results:** :white_check_mark: Status: VERIFIED — Dynamic bounds affect paperco (model_infeasible) and potentially other models. The KKT generator defaults upper bounds to 0 for positive variables when .up is set in a loop. Fix requires resolving loop-body assignments at parse time or deferring to GAMS evaluation. Effort: 3-4h.

### KU-23: Concrete Element Offsets in Stationarity (Sprint 23 KU-29)

**Priority:** High
**Assumption:** Concrete element offsets (`i1+1`, `s1-1`) in stationarity equations can be converted to symbolic index offsets (`i+1`, `j-1`) by the stationarity builder.

**Research Questions:**
1. How does `_apply_offset_substitution` currently handle concrete elements?
2. Is there an element-to-index mapping available at the stationarity building stage?
3. Do all concrete offsets correspond to a single symbolic index?

**How to Verify:**
- Trace polygon and cclinpts through the stationarity builder
- Check if `element_to_set` mapping is available

**Risk if Wrong:** Element-to-index mapping is ambiguous; manual per-model mapping needed
**Estimated Research Time:** 1-2h
**Owner:** Task 4
**Verification Results:** :white_check_mark: Status: VERIFIED — Concrete element offsets (i1+1, s1-1) affect 8 path_syntax_error models (subcategory H, including polygon), with cclinpts also affected in the stationarity output. The element-to-index mapping is available via element_to_set but not applied consistently in _apply_offset_substitution. Fix is in stationarity.py, estimated 4-6h.

### KU-24: Duplicate `.fx` Emission (Sprint 23 KU-32)

**Priority:** Medium
**Assumption:** The emitter's duplicate `.fx` statements (seen in springchain) are cosmetic and don't affect solve results.

**Research Questions:**
1. Does GAMS last-write-wins for duplicate `.fx` statements?
2. Do the duplicate conditions conflict (different conditions for same variable)?
3. Does this affect any model's solve result?

**How to Verify:**
- Check if springchain solves correctly despite duplicates
- Test with deduplicated `.fx` statements

**Risk if Wrong:** Duplicates cause incorrect fixation; affects solve results for 1+ models
**Estimated Research Time:** 1h
**Owner:** Day 10+ (low priority)
**Verification Results:** :mag: Status: INCOMPLETE

---

## Cross-Cutting Unknowns

### KU-25: Error Influx Budget Accuracy (PR10)

**Priority:** Critical
**Assumption:** Per Sprint 23 process recommendation PR10, ~40% of newly-translating models will have solve errors. This budget is accurate for Sprint 24.

**Research Questions:**
1. If alias differentiation fixes some path_syntax_error and model_infeasible, does it also create new translate successes?
2. What was the actual influx rate in Sprint 23? (12 new translates, 7 new solve errors = 58%)
3. Should we use 40% or 60% for Sprint 24 budgeting?

**How to Verify:**
- Calculate Sprint 23 actual influx rate
- Adjust Sprint 24 error budget accordingly

**Risk if Wrong:** Under-budget influx → targets appear missed; over-budget → overly conservative targets
**Estimated Research Time:** 0.5h
**Owner:** Task 7
**Verification Results:** :mag: Status: INCOMPLETE

### KU-26: Alias Differentiation Effort Estimate

**Priority:** Critical
**Assumption:** The alias differentiation fix (Priority 1) can be completed in 14-18 hours as estimated in the PROJECT_PLAN.md.

**Research Questions:**
1. Does Task 2 root cause analysis reveal complexity beyond the Sprint 23 design?
2. Does the design (Task 3) identify more functions needing changes than anticipated?
3. Is the regression test effort (golden files for 49 models) included in the estimate?
4. How much mid-sprint debugging should we expect?

**How to Verify:**
- Compare Task 2/3 findings against the 14-18h estimate
- Adjust schedule if needed

**Risk if Wrong:** Effort exceeds 18h; compress or defer Priority 2-4 work
**Estimated Research Time:** 0.5h (assess after Tasks 2-3)
**Owner:** Task 3
**Verification Results:** :white_check_mark: Status: VERIFIED — Architecture is already implemented (Sprint 23 PRs #1135/#1136). Sprint 24 effort is debugging/extending edge cases, not building from scratch. Estimated 11-17h total (debug Pattern A 4-6h, validate 2-3h, Pattern C 2-3h, B/D investigation 2-3h, pipeline regression 1-2h). **Within the 14-18h PROJECT_PLAN estimate.**

---

## Template for Adding New Unknowns During Sprint

```markdown
### KU-XX: [Title]

**Priority:** [Critical/High/Medium/Low]
**Assumption:** [What we're assuming]

**Research Questions:**
1. [Question 1]
2. [Question 2]
3. [Question 3]

**How to Verify:** [Method]
**Risk if Wrong:** [Impact]
**Estimated Research Time:** [Hours]
**Owner:** [Task or Day]
**Verification Results:** :mag: Status: INCOMPLETE
```

---

## Next Steps

1. **Task 2 (Analyze Alias Differentiation Root Causes)** verifies KU-01, KU-02, KU-03, KU-04, KU-07, KU-08
2. **Task 3 (Design Alias Differentiation Architecture)** verifies KU-05, KU-06, KU-26
3. **Task 4 (Triage path_syntax_error)** verifies KU-09, KU-10, KU-11, KU-12, KU-13, KU-22, KU-23
4. **Task 5 (Triage model_infeasible)** verifies KU-14, KU-15, KU-16, KU-17, KU-18
5. **Task 6 (Investigate Translation Timeouts)** verifies KU-19, KU-20, KU-21
6. **Task 7 (Run Full Pipeline Baseline)** verifies KU-25
7. **KU-24 (Duplicate `.fx` emission)** is low priority; verify at Day 10+ (Checkpoint 2)

---

## Appendix A: Task-to-Unknown Mapping

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Analyze Alias Differentiation Root Causes | KU-01, KU-02, KU-03, KU-04, KU-07, KU-08 | Root cause classification informs design |
| Task 3: Design Alias Differentiation Architecture | KU-03, KU-05, KU-06, KU-26 | Design validates regression risk and effort |
| Task 4: Triage path_syntax_error Models | KU-09, KU-10, KU-11, KU-12, KU-13, KU-22, KU-23 | Classification + carryforward items |
| Task 5: Triage model_infeasible Models | KU-14, KU-15, KU-16, KU-17, KU-18 | Root cause + influx risk assessment |
| Task 6: Investigate Translation Timeouts | KU-19, KU-20, KU-21 | Timeout profiling + internal error |
| Task 7: Run Full Pipeline Baseline | KU-25 | Influx rate calibration |
| Task 8: Review Retrospective Action Items | (validates PR9/PR10/PR11 compliance) | Cross-cutting process check |
| Task 9: Plan Sprint 24 Detailed Schedule | (integrates all verified unknowns) | Schedule reflects risk findings |

**Coverage:** All 26 unknowns are assigned to at least one prep task. KU-03 is verified by both Task 2 (analysis) and Task 3 (design). KU-24 is deferred to sprint execution (Day 10+).

---

**Document Created:** 2026-04-03
**Total Unknowns:** 26
**Sprint 23 Carryforward:** 3 KUs (Sprint 23 KU-28 → KU-22, KU-29 → KU-23, KU-32 → KU-24)
