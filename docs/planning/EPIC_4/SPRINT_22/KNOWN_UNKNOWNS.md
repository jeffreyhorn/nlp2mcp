# Sprint 22 Known Unknowns

**Created:** 2026-03-05
**Sprint:** 22 (Prep Task 1)
**Status:** Initial version — verify during Sprint 22 Days 0-2
**Last Updated:** 2026-03-05

---

## Purpose

This document catalogs assumptions and unknowns for Sprint 22 (Solve Improvements & Solution Matching). Each unknown has a priority, assumption, research questions, verification method, and risk assessment. The goal is to prevent late discoveries during implementation by surfacing uncertainties early.

**Process:** Sprint 21 Retrospective highlighted the value of proactive investigation (e.g., Day 12 PATH convergence analysis invalidated PATH tuning assumptions). This document follows the pattern established in prior sprints.

---

## Summary Table

| ID | Category | Unknown | Priority | Assumption | Verification Deadline |
|----|----------|---------|----------|------------|-----------------------|
| KU-01 | KKT Correctness | Subcategory C uncontrolled sets are all same root cause | Critical | Yes, single AD/stationarity bug | Day 1 |
| KU-02 | KKT Correctness | Subcategory C fix won't break currently-solving models | Critical | Fix is additive (domain conditioning) | Day 2 |
| KU-03 | KKT Correctness | Subcategory B domain violations share a common emitter bug | High | Yes, single emitter data-filtering fix | Day 1 |
| KU-04 | KKT Correctness | Subcategory G set index reuse can be solved with aliasing | High | Simple alias renaming suffices | Day 2 |
| KU-05 | Starting Point | Category B execution errors are all `.l`-initialization fixable | Critical | Yes, smart initialization prevents domain errors | Day 1 |
| KU-06 | Starting Point | `option domlim` is sufficient to bypass remaining domain errors | High | GAMS continues past domain errors with approximate values | Day 1 |
| KU-07 | Starting Point | etamac log(0)/division-by-zero is solvable with epsilon guards | Medium | `max(x.l, epsilon)` prevents domain errors without distorting KKT | Day 2 |
| KU-08 | PATH Solver | PATH solver tuning is irrelevant for Sprint 22 | High | Confirmed by Day 12 analysis — no convergence issues | Day 0 |
| KU-09 | PATH Solver | Category F locally-infeasible models (chain, rocket) are genuine | Medium | These are non-convexity issues, not KKT bugs | Day 3 |
| KU-10 | PATH Solver | Category C MCP pairing errors are KKT builder bugs | High | Fix in KKT builder, not emitter | Day 2 |
| KU-11 | Divergence Analysis | 35 non-matching models are primarily multi-optima cases | Medium | Most divergence is from non-convexity, not KKT bugs | Day 3 |
| KU-12 | Divergence Analysis | Combined tolerance formula is appropriate for all model types | Medium | `|a-b| <= atol + rtol*max(|a|,|b|)` works across scales | Day 2 |
| KU-13 | Divergence Analysis | Newly-solving models from path_syntax_error fixes will mostly match | Medium | Convex NLP models produce unique KKT points | Day 5 |
| KU-14 | Parse Completion | 3 remaining lexer_invalid_char models are low-effort fixes | Low | Simple grammar additions or preprocessor rules | Day 3 |
| KU-15 | Parse Completion | Parse rate won't regress from solve-focused changes | High | KKT/emitter changes don't affect parser | Day 5 |
| KU-16 | Deferred Subcategories | Subcategory F (mingamma) reserved-word fix is isolated | Low | Renaming `gamma` → `gamma_v` has no side effects | Day 2 |
| KU-17 | Deferred Subcategories | Subcategory I (nemhaus) MCP variable filtering is straightforward | Low | Filter unreferenced variables from model statement | Day 2 |
| KU-18 | Deferred Subcategories | Subcategory J (pdi) dimension mismatch is a pairing logic bug | Low | Fix in MCP pair generation, not KKT | Day 2 |
| KU-19 | Deferred Subcategories | 3 unsubcategorized models (dinam, ferts, tricp) fit existing subcategories | High | No new subcategory needed | Day 1 |
| KU-20 | Deferred Items | #764 (mexss accounting vars) overlaps with Subcategory C work | Medium | Partial overlap — same KKT assembly code | Day 2 |
| KU-21 | Deferred Items | #827 (gtm domain violations) overlaps with Subcategory B work | Medium | Partial overlap — emitter domain filtering | Day 2 |
| KU-22 | Deferred Items | #830 (gastrans Jacobian timeout) is independent of Sprint 22 work | High | No overlap with path_syntax_error or path_solve_terminated fixes | Day 1 |
| KU-23 | Deferred Items | #765 (orani CGE incompatibility) is fundamentally unfixable | High | Model class detection + warning is the correct approach | Day 1 |
| KU-24 | KKT Correctness | Fixing path_syntax_error models may shift them to model_infeasible | High | Some models have secondary KKT issues masked by syntax errors | Day 5 |
| KU-25 | Starting Point | elec self-pair exclusion requires index-level filtering in emitter | Medium | Can filter `i != j` conditions during MCP emission | Day 2 |
| KU-26 | Divergence Analysis | Solution divergence case studies require original NLP solve data | Medium | NLP `.lst` files available in `data/gamslib/raw/` for all models | Day 1 |

---

## Category 1: KKT Correctness Fixes (5 unknowns)

### KU-01: Subcategory C Uncontrolled Sets — Same Root Cause?

**Priority:** Critical
**Assumption:** All 9 Subcategory C models (ampl, dyncge, glider, harker, korcge, paklive, robert, shale, tabora) share the same root cause — the KKT stationarity generator emits equations with set indices outside their controlling domain.

**Research Questions:**
1. Do all 9 models exhibit the same GAMS error pattern ($149: uncontrolled set)?
2. Are the uncontrolled sets always from stationarity equations (∂L/∂x), or do some come from complementarity or feasibility equations?
3. Is the root cause in the AD engine (`src/ad/`) or the stationarity builder (`src/kkt/`)?
4. Do any of the 9 models have multiple distinct uncontrolled-set patterns?

**How to Verify:** Examine GAMS `.lst` error output for 3 representative models (dyncge, glider, harker). Trace the uncontrolled set back to the source code that generates it.

**Risk if Wrong:** If there are multiple distinct root causes, a single fix won't address all 9 models. Sprint 22 would need separate fixes per sub-pattern, increasing effort from 3-5h to potentially 8-12h.

**Estimated Research Time:** 1h
**Owner:** Task 2 (path_syntax_error catalog update)
**Verification Results:** CONFIRMED. All 10 current Subcategory C models share the same root cause (KKT stationarity generator fails to propagate domain requirements). Two sub-patterns identified: (1) scalar stationarity with indexed symbols (ampl, dyncge, glider), (2) domain mismatch in stationarity (harker, korcge, paklive, robert, shale, tabora, trnspwl). Both patterns originate in the same KKT assembly code path. A single fix addressing domain propagation should resolve all 10 models.

---

### KU-02: Subcategory C Fix Regression Risk

**Priority:** Critical
**Assumption:** Fixing uncontrolled sets in stationarity equations is additive — it adds domain conditioning to generated equations without modifying the stationarity logic for models that already solve correctly.

**Research Questions:**
1. Does the fix modify the stationarity equation generation path used by currently-solving models?
2. Could adding domain controls change the mathematical content of stationarity equations for models that currently match?
3. Are there models where the "uncontrolled" set is actually intentional (e.g., scalar equations)?
4. What is the regression test coverage for stationarity equation generation?

**How to Verify:** After implementing the fix, run full pipeline retest. Compare solve/match counts before and after. Run `make test` to check for regressions.

**Risk if Wrong:** If the fix modifies stationarity logic for already-solving models, it could reduce the solve count. This would be a net negative even if it fixes 9 new models.

**Estimated Research Time:** 30min (code review of stationarity builder)
**Owner:** Task 7 (fix design)
**Verification Results:** *To be completed during Task 7*

---

### KU-03: Subcategory B Domain Violations — Common Emitter Bug?

**Priority:** High
**Assumption:** All 5 Subcategory B models (agreste, china, egypt, fawley, gtm) share the same emitter bug — parameter data is emitted with incorrect domain ordering or out-of-domain entries.

**Research Questions:**
1. Do all 5 models show the same GAMS $170 error pattern?
2. Is the domain ordering issue consistent (e.g., always swapped dimensions)?
3. Does the fix require changes only in `src/emit/emit_gams.py` or also in the IR?
4. Is #827 (gtm) a special case requiring additional parser-side work?

**How to Verify:** Examine emitted parameter data sections for 2-3 models. Compare domain ordering against parameter declarations.

**Risk if Wrong:** If gtm requires a fundamentally different fix (parser-side zero-fill), it may need to be addressed separately from the other 4 models.

**Estimated Research Time:** 1h
**Owner:** Task 2 (catalog update)
**Verification Results:** REFUTED. The original 5 Subcategory B models do NOT share a common emitter bug. Sprint 21 fixes changed the compilation context: egypt and fawley moved out of path_syntax_error entirely. The remaining 3 "Subcategory B" models now show completely different errors: agreste=$66 (reclassified to A — missing data), china=$141 (reclassified to A — missing data), gtm=$120/$340 (reclassified to new pattern — unquoted hyphenated labels). Current Subcategory B contains only 2 newly-translating models (cesam, cesam2) with $170 errors. These should be investigated fresh rather than assuming they match the egypt/fawley pattern.

---

### KU-04: Subcategory G Set Index Reuse — Aliasing Sufficient?

**Priority:** High
**Assumption:** The 2 Subcategory G models (kand, prolog) can be fixed by generating alias indices for conflicting sum domains (e.g., `sum((nn,n__), ...)` instead of `sum((nn,n), ...)`).

**Research Questions:**
1. Does the conflict always occur between an outer assignment index and an inner sum index?
2. Could the alias approach create naming collisions with other variables or sets?
3. Does the KKT derivation introduce additional index reuse beyond what's in the original model?
4. Are there other models that use the same sum pattern but currently solve (indicating the fix must be selective)?

**How to Verify:** Examine the 2 models' emitted MCP code to identify the exact conflict pattern. Check that alias generation doesn't collide with existing identifiers.

**Risk if Wrong:** If aliasing is insufficient (e.g., the conflict is deeper in the AD engine), the fix may require restructuring sum domain handling — a larger effort.

**Estimated Research Time:** 30min
**Owner:** Task 7 (fix design)
**Verification Results:** *To be completed during Task 7*

---

### KU-24: path_syntax_error Fixes May Shift Models to model_infeasible

**Priority:** High
**Assumption:** Some models currently classified as path_syntax_error have secondary KKT issues that are masked by the primary syntax error. Fixing the syntax error will allow them to reach the solve stage, where they may fail as model_infeasible.

**Research Questions:**
1. How many of the 41 path_syntax_error models are likely to solve vs shift to another error category?
2. Are any of the 9 Subcategory C models known to have KKT correctness issues beyond the uncontrolled set?
3. What is the expected "conversion rate" from path_syntax_error → solving?
4. Should Sprint 22 targets account for model_infeasible growth?

**How to Verify:** After fixing each subcategory, run pipeline retest and track which models solve vs which shift to model_infeasible or path_solve_terminated.

**Risk if Wrong:** If many path_syntax_error models shift to model_infeasible, the model_infeasible count could increase from 15 to 20+, making the ≤12 target impossible. Sprint 22 targets may need adjustment.

**Estimated Research Time:** 30min (review model types in subcategories)
**Owner:** Tasks 2, 4 (catalog + triage)
**Verification Results:** *To be completed during Tasks 2 and 4*

---

## Category 2: Starting Point Improvements (4 unknowns)

### KU-05: Category B Execution Errors Are `.l`-Initialization Fixable

**Priority:** Critical
**Assumption:** All 5 Category B models (cclinpts, elec, etamac, hs62, lands) can be fixed through smarter `.l` initialization or domain-error guards, without requiring fundamental KKT changes.

**Research Questions:**
1. How many of the 5 models fail due to default `.l = 0` values vs other causes?
2. Can `option domlim = 100;` alone unblock some models without `.l` changes?
3. Does etamac's log(0) issue require epsilon guards in the emitter or in the stationarity equations?
4. Is lands' NA/undefined RHS a missing parameter issue (emitter) or a conditional equation issue (KKT)?
5. Is hs62's calibration division-by-zero fixable by removing the post-solve calibration block?

**How to Verify:** For each model, run with `option domlim = 100;` added to the MCP file. If PATH runs (even unsuccessfully), the execution error is bypassable. Then test with improved `.l` values.

**Risk if Wrong:** If some Category B models have fundamental issues (not just initialization), they cannot be fixed with starting point improvements alone. The path_solve_terminated ≤ 5 target may need adjustment.

**Estimated Research Time:** 1.5h
**Owner:** Task 3 (path_solve_terminated classification)
**Verification Results:** *To be completed during Task 3*

---

### KU-06: `option domlim` Sufficiency

**Priority:** High
**Assumption:** Adding `option domlim = 100;` to emitted MCP files allows GAMS to continue past domain evaluation errors (log(0), division by zero, rPower domain) with approximate equation values, enabling PATH to run.

**Research Questions:**
1. Does `option domlim` apply to domain errors in equation generation, or only during solve iterations?
2. Does it produce meaningful (non-NaN) equation values when domain errors are suppressed?
3. Could suppressed domain errors lead to incorrect KKT solutions that appear valid?

**How to Verify:** Add `option domlim = 100;` to one Category B model's MCP file (e.g., etamac) and run GAMS directly. Check if PATH runs and what solution quality results.

**Risk if Wrong:** If `domlim` doesn't apply to equation generation errors, it provides no benefit. Sprint 22 would need model-specific `.l` initialization instead (higher effort per model).

**Estimated Research Time:** 30min
**Owner:** Task 3 (path_solve_terminated classification)
**Verification Results:** *To be completed during Task 3*

---

### KU-07: etamac Epsilon Guards Don't Distort KKT

**Priority:** Medium
**Assumption:** Replacing `log(c)` with `log(max(c, epsilon))` and `1/c` with `1/max(c, epsilon)` in stationarity equations preserves the mathematical correctness of the KKT conditions near the optimal solution.

**Research Questions:**
1. At the NLP optimal solution, are consumption variables (c) strictly positive?
2. Does the epsilon guard affect the KKT gradient at the optimal point?
3. Is the guard applied in the emitter (GAMS-level) or in the AD engine (derivative-level)?
4. Does GAMS have built-in constructs for this (e.g., `errorf`, `sigmoid` smoothing)?

**How to Verify:** Check etamac's NLP `.l` values — if all consumption variables are positive at the optimum, epsilon guards only affect the initial path from `.l = 0` to the solution, not the solution itself.

**Risk if Wrong:** If epsilon guards distort the KKT conditions, the MCP solution would differ from the NLP optimal. The model would "solve" but not "match."

**Estimated Research Time:** 30min
**Owner:** Task 3 (path_solve_terminated classification)
**Verification Results:** *To be completed during Task 3*

---

### KU-25: elec Self-Pair Exclusion Requires Index-Level Filtering

**Priority:** Medium
**Assumption:** The elec model's division-by-zero error (Category B execution error) can be fixed by adding `i != j` conditions to distance calculations in the emitted MCP, filtering self-pairs during emission.

**Research Questions:**
1. Does the original NLP model use `$(ord(i) <> ord(j))` or similar conditional to exclude self-pairs?
2. Can the emitter detect and preserve such conditions from the IR?
3. Would a generic `distance >= epsilon` guard be safer than self-pair exclusion?

**How to Verify:** Examine elec's original GAMS file for self-pair exclusion conditions. Check if the IR preserves dollar conditions on equation terms.

**Risk if Wrong:** If self-pair exclusion requires new IR infrastructure for conditional emission, the fix could take 4-6h instead of 1h.

**Estimated Research Time:** 30min
**Owner:** Task 3 (path_solve_terminated classification)
**Verification Results:** *To be completed during Task 3*

---

## Category 3: PATH Solver Tuning (3 unknowns)

### KU-08: PATH Solver Tuning Is Irrelevant for Sprint 22

**Priority:** High
**Assumption:** Sprint 21 Day 12 PATH Convergence Analysis confirmed that none of the 15 remaining path_solve_terminated models have actual PATH convergence issues. PATH solver tuning (convergence_tolerance, major_iteration_limit) is not applicable.

**Research Questions:**
1. Does the Day 12 analysis cover all 15 models comprehensively?
2. Could newly-solving models (from Sprint 22 fixes) encounter genuine PATH convergence issues?
3. Should Sprint 22 include any PATH options work as contingency?

**How to Verify:** Review PATH_CONVERGENCE_ANALYSIS.md findings. Confirm that PROJECT_PLAN.md's "PATH Solver Tuning" component should be redirected to pre-solver error fixes.

**Risk if Wrong:** If the Day 12 analysis missed genuine convergence cases, Sprint 22 would need to re-scope to include PATH tuning work (4-6h from the original plan).

**Estimated Research Time:** 15min (review existing analysis)
**Owner:** Task 1 (this document)
**Verification Results:** Verified — PATH_CONVERGENCE_ANALYSIS.md explicitly states "None of the 15 still-failing models have actual PATH solver convergence issues" (Section 1). Categories B-E (13 models) never reach PATH; Category F (2 models) reach PATH but terminate as locally infeasible (Normal Completion). PATH options tuning is confirmed irrelevant.

---

### KU-09: Category F Locally-Infeasible Models Are Genuine

**Priority:** Medium
**Assumption:** chain (340 iterations, residual 7.079) and rocket (6,287 iterations, residual 1.309) are genuinely locally infeasible — the issue is non-convexity or incorrect KKT formulation, not PATH configuration.

**Research Questions:**
1. Do chain and rocket have known convexity properties? (Are they convex NLPs?)
2. Could the infeasibility be caused by incorrect bound multipliers in stationarity equations?
3. Would warm-starting from the NLP solution's `.l` values change the outcome?
4. Are these models in the "multiple optima" or "non-convex" category?

**How to Verify:** Check the original NLP model type. Run chain/rocket with `.l` values set to the NLP solution. If still infeasible, the issue is likely KKT formulation.

**Risk if Wrong:** If these models are actually fixable (KKT bug), Sprint 22 misses 2 additional solve opportunities. Low impact on targets but worth investigating.

**Estimated Research Time:** 1h
**Owner:** Task 3 (path_solve_terminated classification)
**Verification Results:** *To be completed during Task 3*

---

### KU-10: Category C MCP Pairing Errors Are KKT Builder Bugs

**Priority:** High
**Assumption:** The 4 Category C models (fdesign, trussm, hhfair, pak) have MCP pairing errors caused by the KKT builder emitting incorrect variable-equation pairs, not by the emitter formatting them incorrectly.

**Research Questions:**
1. Are the "unmatched free variables" in fdesign/trussm caused by missing stationarity equations or extra variables?
2. Are the "unmatched equation" errors in hhfair/pak caused by fixed-value equation elimination issues?
3. Does the MCP model statement generator correctly count variables and equations?
4. Could any of these be emitter issues (correct IR but wrong GAMS output)?

**How to Verify:** For fdesign, compare the IR's variable count to the emitted MCP variable count. Check if any stationarity equations were dropped during emission.

**Risk if Wrong:** If the issue is in the emitter (not KKT builder), the fix location and approach would differ. Lower risk — either way, a fix exists.

**Estimated Research Time:** 1h
**Owner:** Task 3 (path_solve_terminated classification)
**Verification Results:** *To be completed during Task 3*

---

## Category 4: MCP-NLP Solution Divergence Analysis (4 unknowns)

### KU-11: Non-Matching Models Are Primarily Multi-Optima Cases

**Priority:** Medium
**Assumption:** Of the 35 models that solve but don't match, most diverge because the MCP finds a different local optimum than the NLP solver (multiple optima in non-convex models), not because of KKT formulation errors.

**Research Questions:**
1. How many of the 35 non-matching models are known non-convex NLPs?
2. For near-miss models (small objective divergence), is the difference consistent with floating-point precision or genuinely different optima?
3. Are there models where the MCP objective is clearly wrong (e.g., zero when NLP is nonzero)?
4. Can we classify non-matching models by divergence magnitude to prioritize investigation?

**How to Verify:** Extract objective values for all 35 non-matching models. Sort by divergence magnitude. Cross-reference with known model convexity properties.

**Risk if Wrong:** If many non-matching models have KKT bugs (not multi-optima), Sprint 22 needs more KKT fix work to hit Match ≥ 35. Match rate improvement would require KKT debugging, not just new solves.

**Estimated Research Time:** 1.5h
**Owner:** Task 9 (match rate analysis)
**Verification Results:** *To be completed during Task 9*

---

### KU-12: Combined Tolerance Formula Appropriateness

**Priority:** Medium
**Assumption:** The combined tolerance formula `|a - b| <= atol + rtol * max(|a|, |b|)` (with DEFAULT_RTOL = 2e-3) is appropriate for comparing MCP and NLP objective values across all model types and scales.

**Research Questions:**
1. Are there models where the formula is too strict (rejects valid matches)?
2. Are there models where the formula is too lenient (accepts incorrect matches)?
3. Should `atol` and `rtol` be model-specific or global?
4. Does the formula handle edge cases correctly (zero objectives, very large objectives)?

**How to Verify:** Review the 5 "near-miss" models from Category A (ps2_f_s, ps2_s, ps3_s_mn, ps3_s_scp, ps3_s). Check if they would match with slightly relaxed tolerance.

**Risk if Wrong:** If tolerance is too strict, Sprint 22 match count understates progress. If too lenient, it overstates correctness. Low risk — tolerance can be adjusted.

**Estimated Research Time:** 30min
**Owner:** Task 9 (match rate analysis)
**Verification Results:** *To be completed during Task 9*

---

### KU-13: Newly-Solving Models Will Mostly Match

**Priority:** Medium
**Assumption:** Models that start solving after path_syntax_error or path_solve_terminated fixes will mostly match their NLP objectives (because convex NLP models produce unique KKT points).

**Research Questions:**
1. What fraction of currently-solving models match (30/65 = 46.2%)?
2. Are the models in path_syntax_error subcategories more or less likely to be convex?
3. Should Sprint 22 Match ≥ 35 target account for newly-solving models or only existing solvers?

**How to Verify:** After each batch of fixes, compare the match rate of newly-solving models vs existing solvers.

**Risk if Wrong:** If newly-solving models have low match rates (similar to the current 46.2%), Sprint 22 would need +10 new solves to get +5 new matches. Match ≥ 35 target may be optimistic.

**Estimated Research Time:** 15min (review model types)
**Owner:** Task 9 (match rate analysis)
**Verification Results:** *To be completed during Task 9*

---

### KU-26: NLP Solution Data Available for All Models

**Priority:** Medium
**Assumption:** NLP `.lst` files (containing NLP solve results) are available in `data/gamslib/raw/` for all models needed for divergence analysis.

**Research Questions:**
1. Do all 65 solving models have corresponding NLP `.lst` files?
2. Are the NLP `.lst` files from the same GAMS version used for MCP solving?
3. Do the `.lst` files contain objective values in a parseable format?

**How to Verify:** Check for `.lst` files in `data/gamslib/raw/` for representative models.

**Risk if Wrong:** If NLP solution data is missing, Sprint 22 would need to run NLP solves before divergence analysis — adding 2-4h of data collection work.

**Estimated Research Time:** 15min
**Owner:** Task 9 (match rate analysis)
**Verification Results:** *To be completed during Task 9*

---

## Category 5: Parse Completion Final Push (2 unknowns)

### KU-14: Remaining lexer_invalid_char Models Are Low-Effort

**Priority:** Low
**Assumption:** The 3 remaining lexer_invalid_char models can be fixed with simple grammar additions or preprocessor rules, requiring ≤2h total.

**Research Questions:**
1. What specific characters/patterns cause the lexer failures?
2. Are these models worth fixing given the 98.1% parse rate?
3. Could the fixes introduce ambiguities in the grammar?

**How to Verify:** Run the 3 models through the parser in verbose mode to identify the specific lexer error.

**Risk if Wrong:** If the lexer failures require complex grammar changes, the effort would exceed the budget. Low impact — parse rate is already at 98.1%.

**Estimated Research Time:** 30min
**Owner:** Task 8 (baseline metrics — identifies current parse failures)
**Verification Results:** *To be completed during Task 8*

---

### KU-15: Parse Rate Won't Regress from Solve-Focused Changes

**Priority:** High
**Assumption:** Sprint 22's KKT, emitter, and translator changes won't affect the parser or grammar, so parse rate (154/157) will remain stable.

**Research Questions:**
1. Do any Sprint 22 workstreams modify `src/ir/parser.py` or `src/gams/gams_grammar.lark`?
2. Could emitter changes (domain filtering, expression formatting) cause re-parse failures?
3. Is there a regression test that specifically checks parse count?

**How to Verify:** Run parse-only pipeline retest (`--only-parse`) at each checkpoint. Verify 154/157 maintained.

**Risk if Wrong:** If parse rate drops, Sprint 22 would need to allocate time to fix parser regressions, reducing time for solve improvements.

**Estimated Research Time:** 15min (review workstream scope)
**Owner:** Task 8 (baseline metrics)
**Verification Results:** *To be completed during Task 8*

---

## Category 6: Deferred path_syntax_error Subcategories (4 unknowns)

### KU-16: Subcategory F Reserved-Word Fix Is Isolated

**Priority:** Low
**Assumption:** Renaming `gamma` → `gamma_v` (and `psi` → `psi_v`) in mingamma's emitted code is an isolated fix that doesn't affect other models.

**Research Questions:**
1. How many other models use variables named `gamma`, `psi`, or other GAMS built-in functions?
2. Should the fix be a general reserved-word renaming system or a one-off for mingamma?
3. What is the complete list of GAMS reserved function names that could collide?

**How to Verify:** Search for `gamma`, `psi`, and other GAMS built-in names across all model IR outputs.

**Risk if Wrong:** If other models also use reserved names, a one-off fix would be incomplete. A general renaming system (1-2h additional) would be needed.

**Estimated Research Time:** 15min
**Owner:** Task 2 (catalog update)
**Verification Results:** NON-ISSUE. `gamma` and `psi` are used as parameter names in many GAMSlib models (e.g., camshape, sambal), but GAMS handles them context-sensitively — as parameters, not built-in function calls. Only mingamma has the collision because its stationarity equations use `gamma(x1)` in an expression context where GAMS interprets it as a function call. The fix (reserved-word renaming) is isolated to mingamma and does not need to be a general system. A general system would be prudent but is not required for Sprint 22.

---

### KU-17: Subcategory I MCP Variable Filtering Is Straightforward

**Priority:** Low
**Assumption:** nemhaus's "MCP variable not referenced in equations" error ($483) can be fixed by filtering unreferenced variables from the MCP model statement, with no impact on other models.

**Research Questions:**
1. Why are `xb` and `y` included in the MCP model statement if they don't appear in equations?
2. Are they stationarity variables that should have equations, or genuinely unused variables?
3. Could filtering them out change the MCP solution dimensionality?

**How to Verify:** Check if `xb` and `y` have stationarity equations in the IR. If not, they should be excluded from the model statement.

**Risk if Wrong:** If `xb` and `y` should have stationarity equations (and they're missing due to a KKT bug), filtering them hides the real issue. Medium risk — model might solve but produce incorrect results.

**Estimated Research Time:** 15min
**Owner:** Task 2 (catalog update)
**Verification Results:** UPDATED. nemhaus is an MINLP model (has binary variables `xb`, `y`). Binary/integer variables cannot participate in MCP (continuous complementarity), so the MCP translator includes them in the model statement but generates no stationarity equations for them. This is fundamentally a model-type incompatibility issue, not just a filtering bug. Simple filtering of unreferenced variables from the model statement would suppress the $483 error, but nemhaus also has missing parameter data ($141 on the objective). Consider adding MINLP detection with a warning rather than just filtering.

---

### KU-18: Subcategory J Dimension Mismatch Is a Pairing Logic Bug

**Priority:** Low
**Assumption:** pdi's equation-variable dimension mismatch ($70) is a bug in the MCP pair generation logic, fixable by correcting the dimension matching algorithm.

**Research Questions:**
1. Which equation-variable pair has mismatched dimensions in pdi?
2. Is it a stationarity equation paired with the wrong variable, or a complementarity pair?
3. Does the MCP pairing logic work correctly for all other models?

**How to Verify:** Examine pdi's emitted MCP model statement. Compare equation and variable dimensions.

**Risk if Wrong:** If the dimension mismatch is due to a deeper KKT construction issue (e.g., wrong stationarity equation dimensions), the fix would be more complex.

**Estimated Research Time:** 15min
**Owner:** Task 2 (catalog update)
**Verification Results:** CONFIRMED. pdi has 16 systematic $70 errors — a dimension tracking bug in the MCP translator's equation-variable pairing logic. Additionally, launch (previously Subcategory D/$445) now shows $70 errors after Sprint 21's negative-exponent fix resolved the $445 errors, unmasking the underlying dimension mismatch. Subcategory J now contains 2 models (pdi, launch), confirming this is a systematic bug.

---

### KU-19: 3 Unsubcategorized Models Fit Existing Subcategories

**Priority:** High
**Assumption:** The 3 models that entered path_syntax_error after the Sprint 21 catalog (dinam, ferts, tricp) exhibit errors matching existing subcategories (A-G, I, J), requiring no new subcategory definition.

**Research Questions:**
1. What GAMS error codes do dinam, ferts, and tricp produce?
2. Do they match the error patterns of existing subcategories?
3. Were they previously blocked at parse or translate stage (and now reach solve)?
4. If they don't fit existing subcategories, what new pattern do they represent?

**How to Verify:** Run GAMS on each model's MCP file and classify the errors against the subcategory definitions.

**Risk if Wrong:** If a new subcategory is needed, Sprint 22 may need to design additional fixes beyond the planned subcategory C, B, G work.

**Estimated Research Time:** 30min
**Owner:** Task 2 (catalog update)
**Verification Results:** PARTIALLY REFUTED. tricp ($148) does NOT fit existing subcategories — it requires a new Subcategory K (smax/sum domain tuple mismatch). dinam and ferts are NOT path_syntax_error — they moved to translate_failure (timeout) in the latest pipeline run. The Sprint 21 note about "3 unsubcategorized models" is no longer accurate: only tricp was actually path_syntax_error, and it needed a new subcategory. Additionally, 6 other models were reclassified during Task 2 analysis, revealing new error patterns (GUSS dict syntax, duplicate elements, unquoted hyphenated labels) not covered by existing subcategories A-J.

---

## Category 7: Sprint 21 Deferred Items (4 unknowns)

### KU-20: #764 (mexss) Overlaps with Subcategory C

**Priority:** Medium
**Assumption:** The `sameas` guard issue in #764 (accounting variable stationarity) shares code paths with the Subcategory C uncontrolled-set issue. Fixing Subcategory C may partially address #764, or at least inform the fix approach.

**Research Questions:**
1. Does #764's `_add_indexed_jacobian_terms()` guard logic overlap with the code that generates Subcategory C uncontrolled sets?
2. Would fixing Subcategory C change the behavior of mexss's stationarity equations?
3. Can #764 be scoped down by leveraging Subcategory C infrastructure?
4. Is the 8-12h estimate for #764 still accurate if Subcategory C is fixed first?

**How to Verify:** After implementing Subcategory C fix, re-test mexss to see if its infeasibility changes.

**Risk if Wrong:** If there's no overlap, #764 remains a standalone 8-12h item that likely can't fit in Sprint 22.

**Estimated Research Time:** 30min
**Owner:** Task 6 (deferred issues survey)
**Verification Results:** *To be completed during Task 6*

---

### KU-21: #827 (gtm) Overlaps with Subcategory B

**Priority:** Medium
**Assumption:** gtm's domain violation issue (#827) partially overlaps with the Subcategory B emitter fix. The emitter-side domain filtering would address the $170 errors, but the parser-side zero-fill issue would remain.

**Research Questions:**
1. After fixing Subcategory B (emitter domain filtering), does gtm still fail?
2. Is the parser-side zero-fill issue specific to gtm or does it affect other models?
3. Can the zero-fill fix be scoped to 2-3h instead of the original 6-8h estimate?
4. Is topological sort for computed parameters actually needed, or is simple domain filtering sufficient?

**How to Verify:** After implementing Subcategory B fix, re-test gtm. If it still fails, examine the remaining error to assess parser-side work needed.

**Risk if Wrong:** If gtm requires the full 6-8h parser-side fix, including it in Sprint 22 would consume significant budget.

**Estimated Research Time:** 30min
**Owner:** Task 6 (deferred issues survey)
**Verification Results:** *To be completed during Task 6*

---

### KU-22: #830 (gastrans) Is Independent of Sprint 22 Work

**Priority:** High
**Assumption:** gastrans's Jacobian timeout issue (#830) involves dynamic subset member preservation and Jacobian sparsity — infrastructure work that doesn't overlap with any Sprint 22 path_syntax_error or path_solve_terminated workstreams.

**Research Questions:**
1. Do any Sprint 22 workstreams touch `src/ad/index_mapping.py` (where the dynamic subset fallback occurs)?
2. Could Subcategory C fixes (stationarity domain conditioning) reduce the Jacobian combinatorial explosion?
3. Is the 8-10h estimate still accurate?

**How to Verify:** Review Sprint 22 fix designs (Task 7) for overlap with `src/ad/index_mapping.py`. Check if gastrans's timeout is affected by any planned changes.

**Risk if Wrong:** If there is unexpected overlap, gastrans might benefit from Sprint 22 work "for free," or Sprint 22 changes might inadvertently affect gastrans's timeout behavior.

**Estimated Research Time:** 15min
**Owner:** Task 6 (deferred issues survey)
**Verification Results:** *To be completed during Task 6*

---

### KU-23: #765 (orani) Is Fundamentally Unfixable

**Priority:** High
**Assumption:** orani is a linearized percentage-change CGE model with exogenously fixed variables — structurally incompatible with NLP→MCP conversion. The correct approach is model class detection and warning, not a fix.

**Research Questions:**
1. Are there other CGE models in the corpus with the same structural incompatibility?
2. Can model class detection be implemented reliably (e.g., >50% fixed variables → warning)?
3. Should the warning be emitted during translation or during solve?
4. Does this affect Sprint 22 target calculations (should orani be excluded from model_infeasible count)?

**How to Verify:** Review the model_infeasible list for other models with similar characteristics (many fixed variables, linearized formulation).

**Risk if Wrong:** If orani is actually fixable (not fundamentally incompatible), Sprint 22 misses a solve opportunity. Low risk — Issue #765 analysis was thorough.

**Estimated Research Time:** 15min
**Owner:** Task 4 (model_infeasible triage)
**Verification Results:** *To be completed during Task 4*

---

## Appendix A: Task-to-Unknown Mapping

This table maps each PREP_PLAN.md task to the unknowns it should verify during execution.

| Task | Unknowns to Verify | Verification Method |
|------|--------------------|--------------------|
| Task 1 (Known Unknowns) | KU-08 | Review existing Day 12 analysis |
| Task 2 (path_syntax_error Catalog) | KU-01, KU-03, KU-16, KU-17, KU-18, KU-19 | Examine GAMS error output for each subcategory |
| Task 3 (path_solve_terminated Classification) | KU-05, KU-06, KU-09, KU-10, KU-25 | Run models with domlim, examine error details |
| Task 4 (model_infeasible Triage) | KU-23, KU-24 | Classify models, check for CGE patterns |
| Task 5 (Translation Timeout Profiling) | (none — no unknowns specific to timeout profiling) | N/A |
| Task 6 (Deferred Issues Survey) | KU-20, KU-21, KU-22 | Assess overlap after Tasks 2-4 findings |
| Task 7 (Fix Design) | KU-02, KU-04 | Code review of stationarity builder, sum domain handling |
| Task 8 (Baseline Metrics) | KU-14, KU-15 | Run pipeline, verify parse count stable |
| Task 9 (Match Rate Analysis) | KU-11, KU-12, KU-13, KU-26 | Review objective divergence data |
| Task 10 (Detailed Schedule) | (all remaining) | Synthesize all findings into plan |

---

## Appendix B: Priority Distribution

| Priority | Count | Unknowns |
|----------|-------|----------|
| Critical | 4 | KU-01, KU-02, KU-05, KU-08 |
| High | 9 | KU-03, KU-04, KU-06, KU-10, KU-15, KU-19, KU-22, KU-23, KU-24 |
| Medium | 9 | KU-07, KU-09, KU-11, KU-12, KU-13, KU-20, KU-21, KU-25, KU-26 |
| Low | 4 | KU-14, KU-16, KU-17, KU-18 |

**All Critical and High unknowns have verification plans with deadlines ≤ Day 3.**

---

## Appendix C: Verification Status Tracking

Use this template during Sprint 22 to track verification results.

| ID | Verified? | Date | Result | Action Taken |
|----|-----------|------|--------|-------------|
| KU-01 | Yes | 2026-03-05 | Confirmed — 2 sub-patterns, same root cause | Single KKT assembly fix targets all 10 models |
| KU-02 | | | | |
| KU-03 | Yes | 2026-03-05 | Refuted — 3 different errors, not common $170 | Investigate cesam/cesam2 fresh; reclassify agreste/china/gtm |
| KU-04 | | | | |
| KU-05 | | | | |
| KU-06 | | | | |
| KU-07 | | | | |
| KU-08 | Yes | 2026-03-05 | Confirmed — PATH tuning irrelevant | No action; redirect to pre-solver fixes |
| KU-09 | | | | |
| KU-10 | | | | |
| KU-11 | | | | |
| KU-12 | | | | |
| KU-13 | | | | |
| KU-14 | | | | |
| KU-15 | | | | |
| KU-16 | Yes | 2026-03-05 | Non-issue — gamma/psi handled context-sensitively | Fix is isolated to mingamma only |
| KU-17 | Yes | 2026-03-05 | Updated — nemhaus is MINLP (binary vars) | Consider MINLP detection; simple filtering insufficient |
| KU-18 | Yes | 2026-03-05 | Confirmed — 16 systematic $70 errors + launch reclassified | Subcategory J now 2 models; systematic dimension bug |
| KU-19 | Yes | 2026-03-05 | Partially refuted — tricp needs new Subcat K; dinam/ferts are translate timeouts | New subcategory K created; 6 models reclassified |
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
- `docs/planning/EPIC_4/PROJECT_PLAN.md` (lines 509-625) — Sprint 22 scope
- `docs/planning/EPIC_4/SPRINT_21/SPRINT_RETROSPECTIVE.md` (lines 134-154) — Sprint 22 recommendations
- `docs/planning/EPIC_4/SPRINT_21/PATH_CONVERGENCE_ANALYSIS.md` — Category A-F classification
- `docs/planning/EPIC_4/SPRINT_21/PATH_SYNTAX_ERROR_CATALOG.md` — Subcategory A-G, I, J classification (no H)
- `docs/planning/EPIC_4/SPRINT_21/DEFERRED_ISSUES_TRIAGE.md` — 4 deferred issues
- `docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md` — Sprint 22 preparation plan

### Issue Documents
- `docs/issues/ISSUE_764_mexss-mcp-locally-infeasible-accounting-variables.md`
- `docs/issues/ISSUE_765_orani-mcp-locally-infeasible-fixed-variables-exogenous.md`
- `docs/issues/ISSUE_827_gtm-domain-violation-zero-fill.md`
- `docs/issues/ISSUE_830_gastrans-jacobian-dynamic-subset-timeout.md`
- `docs/issues/ISSUE_983_elec-mcp-division-by-zero-distance.md`
- `docs/issues/ISSUE_984_etamac-mcp-division-by-zero-log-singular.md`
- `docs/issues/ISSUE_986_lands-mcp-rhs-na-equation.md`

---

**Document Created:** 2026-03-05
**Total Unknowns:** 26 (across 7 categories)
**Next Steps:** Verify unknowns during Tasks 2-10; update Verification Status Tracking table
