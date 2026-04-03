# Sprint 23 Retrospective

**Created:** April 2, 2026
**Duration:** 15 sprint days (Day 0 – Day 14)
**Sprint Goal:** Solve ≥ 100, Match ≥ 55, path_solve_terminated ≤ 5, model_infeasible ≤ 8, path_syntax_error ≤ 15, Translate ≥ 93%, Parse ≥ 97.5%, Tests ≥ 4,300

---

## Executive Summary

Sprint 23 met 1 of 8 acceptance criteria on the original 160-scope targets (Tests). Parse and Translate showed strong improvement on the 147-run scope (100% and 95.2%) but fell short of the original 160/156-scope targets. Solve rose from 81 to 86 (+5) and Match from 47 to 49 (+2), both below targets of 100 and 55 respectively. The sprint's most impactful work was in translate recovery (+12 models), LP fast path implementation, subset-superset domain widening, and SetMembershipTest evaluation. However, translate influx masked solve improvements — 12 new translates brought 5 new path_syntax_error and 2 new path_solve_terminated. The alias differentiation (#1111 family) remains the single largest blocker affecting ~20 models. 25 PRs merged with 4,364 tests passing (+155 from baseline).

**Key Outcome:** 86 models solve (up from 81). 49 models match (up from 47). Parse reached 100% (147/147). Translate reached 95.2% (140/147). 1/8 original-scope criteria met. Sprint 23 advanced the pipeline's translate coverage significantly but solve/match gains were modest due to error category influx from newly-translating models.

---

## Goals and Results

### Sprint 23 Objectives

1. :x: Parse ≥ 156/160 (97.5%) — achieved: 147/147 (100% of run scope); 147/160 (91.9% of original scope)
2. :x: Translate ≥ 145/156 (93.0%) — achieved: 140/147 (95.2% of run scope); 140/156 (89.7% of original scope)
3. :x: Solve ≥ 100 — achieved: 86
4. :x: Match ≥ 55 — achieved: 49
5. :x: path_syntax_error ≤ 15 — achieved: 23 (+5 influx from new translates)
6. :x: path_solve_terminated ≤ 5 — achieved: 12 (+2 influx)
7. :x: model_infeasible ≤ 8 — achieved: 11 (-1 net)
8. :white_check_mark: Tests ≥ 4,300 — achieved: 4,364

### Metrics Summary

| Metric | Baseline (Day 0) | Target | Stretch | Final (Day 13) | Status |
|--------|-------------------|--------|---------|----------------|--------|
| Parse Rate | 144/147 (98.0%) | ≥156/160 (97.5%) | — | **147/147 (100.0%)** | :x: 100% run; 91.9% original scope |
| Translate Rate | 128/147 (87.1%) | ≥145/156 (93.0%) | ≥148/156 | **140/147 (95.2%)** | :x: 95.2% run; 89.7% original scope |
| Solve Success | 81 | ≥100 | ≥110 | **86** | :x: Missed by 14 |
| Match | 47 | ≥55 | ≥60 | **49** | :x: Missed by 6 |
| path_syntax_error | 18 | ≤15 | ≤12 | **23** | :x: Influx +5 |
| path_solve_terminated | 10 | ≤5 | ≤3 | **12** | :x: Influx +2 |
| model_infeasible | 12 | ≤8 | ≤6 | **11** | :x: Missed by 3 |
| Tests | 4,209 | ≥4,300 | — | **4,364** | :white_check_mark: Exceeded |

### Final Error Category Breakdown

**Translate Errors (7 failures out of 147 parsed):**

| Category | Baseline | Final | Delta |
|----------|----------|-------|-------|
| timeout | ~17 | 6 | ≈-11 |
| internal_error | 0 | 1 | +1 |

**Solve Errors (54 failures out of 140 translated):**

| Category | Baseline | Final | Delta |
|----------|----------|-------|-------|
| path_syntax_error | 18 | 23 | +5 |
| path_solve_terminated | 10 | 12 | +2 |
| model_infeasible | 12 | 11 | -1 |
| path_solve_license | 7 | 8 | +1 |

### model_infeasible Accounting (PR7)

- **Baseline:** 12 models
- **Gross fixes:** 1 (mine recovered via SetMembershipTest)
- **Gross influx:** 0
- **Net change:** -1 (12 → 11)

---

## What Went Well

### 1. LP Fast Path Recovered 7 Translation Timeouts (PR #1172)
The LP fast path for symbolic differentiation was the single highest-leverage translate fix. By detecting LP models and using simplified derivative computation (constants for linear terms), 7 models moved from timeout to successful translation. This was a clean architectural change that didn't affect NLP/QCP models.

### 2. Parse Reached 100% (147/147)
Three parse fixes (lop grammar #890, model composition #892/#894/#896, grid computing #955) brought parse rate to 100% of the pipeline scope. No model in the 147-run scope fails to parse.

### 3. Subset-Superset Domain Widening Fixed $171 Errors (PR #1176)
The architectural fix for subset-superset domain mismatch resolved $171 compilation errors across 4 models (chenery, shale, otpop, hhfair). The fix added ParamRef subset preservation in `_replace_indices_in_expr` and guards in `_rewrite_subset_to_superset` to prevent rewriting subset-declared parameter/variable indices.

### 4. Alias-Aware Differentiation Made Progress (#1173)
While the full #1111 family wasn't resolved, the alias-aware differentiation work improved derivative accuracy for several models and established the architectural pattern for future fixes.

### 5. SetMembershipTest Evaluation Recovered mine (PR #1198)
Adding `SetMembershipTest` evaluation to `condition_eval.py` enabled proper equation instance enumeration for models with subset membership conditions like `$(cf(c))`, recovering the mine model from translation failure.

### 6. Sprint Planning Infrastructure Continued to Work Well
The 15-day schedule with 2 checkpoints, day-by-day prompts, and known unknowns framework provided effective structure. 14 issues closed during the buffer/overflow period (Days 7-11).

---

## What Could Be Improved

### 1. Solve/Match Targets Were Too Aggressive Given Translate Influx
Targets of ≥100 solve and ≥55 match assumed error categories would only decrease. In practice, recovering 12 new translate successes brought 5 new path_syntax_error and 2 new path_solve_terminated. Future targets should account for error influx proportional to translate recovery: expect ~40% of newly-translating models to have solve errors.

### 2. Alias Differentiation (#1111) Remains the Dominant Blocker
12 open issues in the alias-differentiation family affect ~20 models. This single issue category accounts for the majority of mismatch models and several path_syntax_error/model_infeasible cases. Sprint 23 made architectural progress but didn't resolve the core issue. Sprint 24 should make this the primary workstream.

### 3. Scope Mismatch Between Targets and Pipeline
Targets were set against a 160-model scope, but the pipeline now runs 147 models (13 MIP/other excluded). This created confusion in evaluating acceptance criteria. Future sprints should set targets against the actual pipeline scope, or explicitly document both scopes upfront.

### 4. path_solve_terminated Target Was Again Too Aggressive
For the second consecutive sprint, the ≤5 target was missed (achieved 12, up from 10). Many path_solve_terminated models have genuine solver convergence issues that require architectural changes to the KKT formulation or PATH solver parameter tuning. The target should be ≤10 for Sprint 24.

### 5. Error Category Influx Not Predicted Accurately
The sprint plan didn't account for error category influx from translate recovery. 12 new translates increased path_syntax_error from 18→23 and path_solve_terminated from 10→12. KU-24 from Sprint 22 (cascade prediction) applies here too.

---

## What We'd Do Differently

### 1. Set Targets Relative to Pipeline Scope
Instead of setting targets against the original 160-scope, set them against the actual pipeline scope (147). This eliminates confusion and makes acceptance criteria unambiguous.

### 2. Budget for Error Category Influx
When targeting translate recovery, budget for ~40% of newly-translating models entering solve error categories. If recovering 12 translates, expect ~5 new solve errors. Adjust solve/match targets accordingly.

### 3. Prioritize Alias Differentiation Earlier
The #1111 family was identified as the highest-leverage fix in sprint planning but was addressed only partially (Day 9). Starting this work on Day 1-3 would have given more time for the architectural complexity involved.

### 4. Run Full Pipeline at Every Checkpoint
Day 11 metrics (135 translate) differed from Day 13 definitive metrics (140 translate) because the SetMembershipTest and condition_eval fixes weren't reflected until the full retest. Always use full pipeline for definitive numbers.

---

## Sprint 24 Recommendations

Based on Sprint 23 findings and the 20 issues labeled `sprint-24`:

### Priority 1: Alias-Aware Differentiation (#1111 Family)
12 open issues affecting ~20 models. This is the single highest-leverage workstream for improving both solve and match rates. Key architectural work: summation-context tracking in `_diff_varref`/`_partial_collapse_sum`, alias-to-root-set resolution in Jacobian construction.

### Priority 2: path_syntax_error Reduction (23 → ≤ 15)
23 models with compilation errors. Many are from newly-translating models. Categories: uncontrolled set references, invalid index expressions, empty equation bodies. Subset-superset domain and condition scope issues are the primary subcategories.

### Priority 3: model_infeasible Reduction (11 → ≤ 8)
11 in-scope models. Key issues: #1199 (bearing Jacobian), #1177 (chenery post-$171), #1195 (sambal NA values), #1192 (gtm division by zero). Many require Jacobian accuracy improvements that overlap with Priority 1.

### Priority 4: Translation Timeout Remaining (6 models)
6 models still timeout at 300s. lop and mexls are the largest. May require algorithmic improvements to the stationarity builder (sparse Jacobian, incremental computation).

### Priority 5: Translate Internal Error (1 model)
1 model has an internal error during translation. Low priority but should be triaged.

### Suggested Sprint 24 Targets

| Metric | Sprint 23 Final | Sprint 24 Target |
|--------|-----------------|------------------|
| Parse | 147/147 (100.0%) | ≥ 147/147 (maintain) |
| Translate | 140/147 (95.2%) | ≥ 143/147 (97%) |
| Solve | 86 | ≥ 95 |
| Match | 49 | ≥ 55 |
| path_syntax_error | 23 | ≤ 15 |
| path_solve_terminated | 12 | ≤ 10 |
| model_infeasible | 11 | ≤ 8 |
| Tests | 4,364 | ≥ 4,400 |

---

## Process Recommendation Review

### PR6: Full Pipeline for All Definitive Metrics
**Status:** FOLLOWED. All checkpoint and final metrics used `run_full_test.py --quiet`. Day 11/13 both ran full pipeline.

### PR7: Track model_infeasible Gross Fixes and Gross Influx
**Status:** FOLLOWED. Day 13 recorded: 1 gross fix (mine), 0 gross influx, -1 net change.

### PR8: Absolute Counts and Percentages
**Status:** FOLLOWED. All metrics tables include both absolute counts and percentages.

### New Recommendations for Sprint 24

**PR9:** Set targets against actual pipeline scope (147 models), not historical 160-scope. Document scope changes explicitly.

**PR10:** Budget for error category influx when targeting translate recovery. Rule of thumb: ~40% of newly-translating models will have solve errors.

**PR11:** Prioritize the single highest-leverage architectural fix (alias differentiation) in Days 1-5, before moving to incremental fixes.

---

## Final Metrics Comparison (Sprint 20-23)

| Metric | S20 Final | S21 Final | S22 Final | S23 Final | S23 Delta |
|--------|-----------|-----------|-----------|-----------|-----------|
| Parse | 132/160 (82.5%) | 154/157 (98.1%) | 156/160 (97.5%) | 147/147 (100.0%) | +3 (run scope) |
| Translate | 120/132 (90.9%) | 137/154 (89.0%) | 141/156 (90.4%) | 140/147 (95.2%) | +12 (run scope) |
| Solve | 33/120 (27.5%) | 65/137 (47.4%) | 89/141 (63.1%) | 86/140 (61.4%) | +5 |
| Match | 16/160 (10.0%) | 30/157 (19.1%) | 47/160 (29.4%) | 49/147 (33.3%) | +2 |
| path_syntax_error | 48 | 41 | 20 | 23 | +3 (influx) |
| path_solve_terminated | 29 | 12 | 10 | 12 | +2 (influx) |
| model_infeasible | 12 | 15 | 12 | 11 | -1 |
| Tests | ~3,500 | 3,957 | 4,209 | 4,364 | +155 |
