# Sprint 23 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 23 begins
**Timeline:** Complete before Sprint 23 Day 1
**Goal:** Set up Sprint 23 for success — Solve Rate Push & Error Category Reduction (solve 89 → ≥ 100, match 47 → ≥ 55)

**Key Insight from Sprint 22:** Day 12 quick wins delivered outsized pipeline impact (+9 solve, +6 match) because targeted triage identified high-leverage fixes. Sprint 23 prep must replicate this triage-first approach across all 5 priority areas, and apply Sprint 22 process recommendations PR6 (full pipeline for definitive metrics), PR7 (gross fixes/influx tracking), and PR8 (absolute counts for parse).

**Branching:** All prep task branches should be created from `main` and PRs should target `main`.

---

## Executive Summary

Sprint 23 targets the largest solve and match improvement in Epic 4 history: +11 solve (89 → 100) and +8 match (47 → 55). This requires coordinated work across 5 priority areas: path_solve_terminated (10 → ≤ 5), model_infeasible (12 → ≤ 8), match rate (47 → ≥ 55), path_syntax_error (20 → ≤ 15), and translate failures (15 → ≤ 11). The sprint also introduces two architectural AD changes (alias-aware differentiation #1111, dollar-condition propagation #1112) that carry regression risk.

This prep plan focuses on:
1. **Risk identification** — Known Unknowns for all 5 priority areas
2. **Triage and classification** — Root cause analysis before implementation
3. **Architectural investigation** — AD changes require design before code
4. **Baseline establishment** — Full pipeline baseline per PR6
5. **Sprint planning** — Detailed schedule with checkpoints

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|----------------------|
| 1 | Create Sprint 23 Known Unknowns List | Critical | 2-3h | None | All priorities — risk identification |
| 2 | Triage path_solve_terminated Models (10) | Critical | 3-4h | None | Priority 1: path_solve_terminated ≤ 5 |
| 3 | Triage model_infeasible Models (12) | Critical | 3-4h | None | Priority 2: model_infeasible ≤ 8 |
| 4 | Investigate Alias-Aware Differentiation (#1111) | High | 3-4h | None | Priority 3: match ≥ 55 |
| 5 | Investigate Dollar-Condition Propagation (#1112) | High | 3-4h | None | Priority 3: match ≥ 55 |
| 6 | Triage path_syntax_error Subcategories G+B | High | 2-3h | None | Priority 4: path_syntax_error ≤ 15 |
| 7 | Catalog and Classify Translate Failures (15) | Medium | 2h | None | Priority 5: translate ≥ 93% |
| 8 | Run Full Pipeline Baseline (per PR6) | Critical | 1-2h | None | All priorities — baseline metrics |
| 9 | Review Sprint 22 Retrospective Action Items | High | 1h | Tasks 1-8 | Process — ensure nothing missed |
| 10 | Plan Sprint 23 Detailed Schedule | Critical | 3-4h | Tasks 1-9 | All priorities — sprint planning |

**Total Estimated Time:** 23-31 hours (~3-4 working days)

**Critical Path:** Tasks 1 + 8 → Tasks 2-7 (parallel) → Task 9 → Task 10

---

## Task 1: Create Sprint 23 Known Unknowns List

**Status:** :white_check_mark: COMPLETE
**Priority:** Critical
**Estimated Time:** 2-3 hours
**Deadline:** Before Sprint 23 Day 1
**Owner:** Sprint planning
**Dependencies:** None

### Objective

Create proactive list of assumptions and unknowns for Sprint 23 to prevent late discoveries during implementation. This is the first task because it surfaces risks that inform all other prep tasks.

### Why This Matters

Sprint 22 Known Unknowns (30 entries: 26 across 7 categories + 4 in-sprint discoveries) proved highly effective: KU-24 (path_syntax_error → model_infeasible cascade) correctly predicted the net-zero model_infeasible result. KU-27 and KU-28 (alias differentiation, dollar-condition propagation) were discovered during Sprint 22 and deferred — they are now Sprint 23 Priority 3. Early documentation of unknowns prevents Issue #47-style emergencies.

### Background

- Sprint 22 Known Unknowns: `docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md` (30 KUs: 26 in 7 categories + 4 in-sprint discoveries)
- Sprint 21 Known Unknowns: `docs/planning/EPIC_4/SPRINT_21/KNOWN_UNKNOWNS.md` (27 KUs)
- Sprint 22 Retrospective: `docs/planning/EPIC_4/SPRINT_22/SPRINT_RETROSPECTIVE.md`
- 24 issues labeled `sprint-23` in GitHub

### What Needs to Be Done

1. **Review Sprint 22 deferred KUs** — KU-27 (alias-aware differentiation), KU-28 (dollar-condition propagation), KU-29 (non-convex multi-KKT), KU-30 (multi-solve incomparable) all carry forward
2. **For each Priority area, brainstorm unknowns:**
   - **Priority 1 (path_solve_terminated):** Are the 10 models truly MCP pairing/execution errors or PATH convergence? Will fixing pairing expose new infeasibilities?
   - **Priority 2 (model_infeasible):** Can KKT bugs be fixed without introducing regressions? Will fixes cascade to other error categories?
   - **Priority 3 (match rate):** Does alias-aware differentiation affect all indexed models or only alias-using ones? Does dollar-condition propagation require changes to the gradient, Jacobian, or both?
   - **Priority 4 (path_syntax_error):** Are subcategory G (set index reuse) and B (domain violations) independent? Do the 7 target models share common patterns?
   - **Priority 5 (translate failures):** Are timeouts fixable or inherent to model complexity? Will compilation fixes create new solve-stage errors?
3. **Categorize by topic, prioritize by risk, define verification method**
4. **Assign verification deadlines** (Day 0-1 for Critical, Day 2-3 for High)
5. **Create document** following Sprint 22 KNOWN_UNKNOWNS.md format

### Changes

- Created `docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md` with 26 unknowns across 5 categories + 1 carryforward
- Sprint 22 KU-27 → KU-12, KU-28 → KU-14, KU-29 → KU-16, KU-30 → KU-26
- Task-to-Unknown mapping table in Appendix A assigns verification responsibility
- Priority distribution: 5 Critical, 14 High, 6 Medium, 1 Low

### Result

26 unknowns documented across 6 sections:
- **Category 1: path_solve_terminated Reduction** (5 KUs: KU-01–KU-05) — covers CGE incompatibility risk, dollar-condition dependencies, cascade to model_infeasible
- **Category 2: model_infeasible Reduction** (6 KUs: KU-06–KU-11) — covers KKT bug classification, sameas pattern extension, influx budget, non-convexity
- **Category 3: Match Rate Improvement** (6 KUs: KU-12–KU-17) — covers alias differentiation regression, dollar-condition scope, fix independence, non-convex ceiling
- **Category 4: path_syntax_error Residual** (4 KUs: KU-18–KU-21) — covers aliasing mechanism, diverse B root causes, cascade risk, new subcategories
- **Category 5: Translate Failures** (4 KUs: KU-22–KU-25) — covers compilation vs timeout, target feasibility, loop-body commonality
- **Sprint 22 Carryforward** (1 KU: KU-26) — multi-solve incomparable classification stability

### Verification

```bash
# Verify document exists
ls docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md

# Verify minimum unknown count
grep -c "^### KU-" docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md
# Expected: ≥ 25 → Actual: 26

# Verify all 5 priority categories covered
grep -c "^## Category" docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md
# Expected: ≥ 5 → Actual: 5 (+ 1 carryforward section)
```

### Deliverables

- :white_check_mark: `docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md` with 26 unknowns across 5 categories + 1 carryforward
- :white_check_mark: Summary table with ID, category, unknown, priority, assumption, verification deadline
- :white_check_mark: Verification plan for Critical/High unknowns (assigned to Tasks 2-7)

### Acceptance Criteria

- [x] Document created with ≥ 25 unknowns across ≥ 5 categories (26 unknowns, 5 categories + 1 carryforward)
- [x] All unknowns have assumption, verification method, priority
- [x] All Critical/High unknowns have verification deadline (assigned to Tasks 2-7)
- [x] Sprint 22 deferred KUs (KU-27, KU-28, KU-29, KU-30) carried forward (→ KU-12, KU-14, KU-16, KU-26)
- [x] All 5 Sprint 23 priorities covered
- [x] Template for in-sprint updates defined (Appendix C verification status tracking table)

---

## Task 2: Triage path_solve_terminated Models (10)

**Status:** :white_check_mark: COMPLETE
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 23 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** KU-01, KU-02, KU-03, KU-04, KU-05

### Objective

Classify all 10 path_solve_terminated models by root cause to identify which are fixable in Sprint 23 and which require deeper architectural work or PATH author consultation.

### Why This Matters

Sprint 22 missed the path_solve_terminated target (achieved 10, target ≤ 5) because "most have genuine solver convergence issues or complex MCP pairing problems" (retrospective). Blind implementation wastes time. Triage-first identifies the 5+ highest-leverage models to fix.

### Background

- 10 models remain: dyncge, elec, etamac, fawley, gtm, maxmin, qsambal, rocket, sambal, twocge
- Key issues: #862 (sambal), #983 (elec)
- Sprint 22 WS2 fixed 4 models (fdesign, trussm, springchain, whouse) in ~12h; fawley remains path_solve_terminated
- Sprint 21 PATH convergence analysis (`docs/planning/EPIC_4/SPRINT_21/` Day 12) showed most terminated models have pre-solver issues, not PATH convergence

### What Needs to Be Done

1. **For each of the 10 models, run MCP generation and attempt solve:**
   ```bash
   python -m src.cli data/gamslib/raw/<model>.gms -o /tmp/<model>_mcp.gms
   # Then run with GAMS if available to capture PATH output
   ```
2. **Classify root cause into one of:**
   - **A: MCP pairing error** — wrong variable/equation pairing; fix in KKT builder or emitter
   - **B: Execution error** — division by zero, NA values, domain errors; fix in emitter or starting points
   - **C: PATH convergence** — genuine solver failure; may need reformulation or PATH author consultation
   - **D: Pre-solver infeasibility** — PATH detects infeasibility before iteration; likely KKT formulation bug
3. **For each model, record:**
   - Root cause category (A/B/C/D)
   - Specific error message from PATH/GAMS output
   - Estimated fix effort (hours)
   - Dependencies on other models or architectural changes
   - Relevant GitHub issue number
4. **Rank models by fix leverage** — prioritize models that also improve match count
5. **Create triage document** with recommendation for Sprint 23 day assignment

### Changes

- Created `docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SOLVE_TERMINATED.md` — root cause classification, per-model analysis, fix priority ranking, and Sprint 23 recommendations
- Updated `docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md` — KU-01 through KU-05 verification results + Appendix C tracking table

### Result

**Key finding:** 8 of 10 models fail before PATH runs (6 execution errors, 2 MCP pairing errors). 1 model (etamac) already solves optimally (stale status). 1 model (elec) reaches PATH but fails convergence. Classification: 1 already solved, 6 execution errors (B), 2 MCP pairing errors (A), 1 PATH convergence (C), 0 pre-solver infeasibility (D).

**Recommendation:** Target 7 models in Sprint 23 (Tiers 1+2), reducing path_solve_terminated from 10 to 3:
- Tier 1 (Days 1-3, 5-8h): etamac (re-run), rocket, fawley, gtm — localized fixes
- Tier 2 (Days 5-7, 6-10h): maxmin, sambal, qsambal — requires #1112 dollar-condition propagation
- Tier 3 (deferred): elec (PATH convergence), dyncge/twocge (CGE, high cascade risk)

### Verification

```bash
# Verify triage document exists
ls docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SOLVE_TERMINATED.md

# Verify all 10 models covered (check for per-model headings, not generic ### headings)
for model in dyncge elec etamac fawley gtm maxmin qsambal rocket sambal twocge; do
  grep -qi "### .*$model" docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SOLVE_TERMINATED.md || echo "MISSING: $model"
done
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SOLVE_TERMINATED.md` with root cause classification for all 10 models
- Ranked fix priority list with effort estimates
- Recommendation: which 5+ models to target in Sprint 23
- Verification results for KU-01, KU-02, KU-03, KU-04, KU-05 in KNOWN_UNKNOWNS.md Appendix C

### Acceptance Criteria

- [x] All 10 models attempted (MCP generation + solve)
- [x] Each model classified as A (pairing), B (execution), C (convergence), or D (pre-solver)
- [x] Error messages captured for each model
- [x] Fix effort estimated per model
- [x] Top 5+ highest-leverage models identified
- [x] Triage document created
- [x] KU-01, KU-02, KU-03, KU-04, KU-05 verification results recorded in KNOWN_UNKNOWNS.md

---

## Task 3: Triage model_infeasible Models (12)

**Status:** :white_check_mark: COMPLETE
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 23 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** KU-06, KU-07, KU-08, KU-09, KU-10, KU-11

### Objective

Classify all 12 in-scope model_infeasible models by root cause to identify which are KKT formulation bugs (fixable) versus inherent MCP incompatibilities (permanent exclusions).

### Why This Matters

Sprint 22 model_infeasible was net-zero despite significant work (5 fixed, 5 new entries). Sprint 22 retrospective recommends tracking gross fixes and influx separately (PR7). Without triage, Sprint 23 risks the same net-zero pattern.

### Background

- 12 in-scope models: bearing, chain, cpack, lnts, markov, mathopt3, pak, paperco, prolog, robustlp, sparta, spatequ
- 3 permanently excluded: feasopt1, iobalance, orani
- Key issues: #1049 (pak), #1070 (prolog), #1081 (sparta), #1110 (markov), #1038 (spatequ)
- Sprint 22 WS3 fixed whouse, ibm1, uimp, mexss, pdi via sameas guard refactor and other KKT fixes
- Sprint 22 deferred decision doc: `docs/planning/EPIC_4/SPRINT_22/DEFERRED_ISSUES_DECISION.md`

### What Needs to Be Done

1. **For each of the 12 models, run MCP generation and capture PATH output:**
   ```bash
   python -m src.cli data/gamslib/raw/<model>.gms -o /tmp/<model>_mcp.gms
   ```
2. **Classify root cause:**
   - **A: KKT formulation bug** — incorrect stationarity, missing multiplier terms, wrong signs
   - **B: PATH convergence / locally infeasible** — PATH runs but cannot find feasible point (MODEL STATUS 5)
   - **C: Inherent MCP incompatibility** — model class (CGE, multi-solve, etc.) doesn't convert cleanly
   - **D: Missing feature** — requires grammar/IR feature not yet implemented
3. **For models with filed issues (#1049, #1070, #1081, #1110, #1038), review issue description for root cause clues**
4. **Estimate fix effort per model and identify dependencies**
5. **Recommend which models to target** (Category A/B are highest leverage; C may be permanent exclusions)

### Changes

- Created `docs/planning/EPIC_4/SPRINT_23/TRIAGE_MODEL_INFEASIBLE.md` with full root cause classification
- Updated `KNOWN_UNKNOWNS.md` KU-06 through KU-11 verification results and Appendix C tracking table

### Result

- **Category distribution:** 5 KKT bugs (A), 6 PATH convergence/locally infeasible (B), 0 incompatible (C), 1 missing feature (D)
- **Tier 1 (Sprint 23 targets):** markov (#1110), pak (#1049), paperco (#953), sparta (#1081), spatequ (#1038) — 5 models, 14-19h
- **Tier 2 (investigate mid-sprint):** bearing (#757), robustlp (#1105) — 2 models, 5-8h
- **Tier 3 (deferred, needs warm-start):** prolog, chain, cpack, mathopt3, lnts — 5 models
- **Permanent exclusion candidates:** None — all 12 have identifiable fix paths
- **Key finding:** 2 models (bearing, pak) abort before PATH due to MCP pairing errors; 10 reach PATH but get MODEL STATUS 5
- **KU verification:** KU-06 ⚠️ (5/6/1 split, not "primarily" KKT bugs), KU-07 ⚠️ (different root causes per model), KU-08 ⚠️ (need 4+ gross fixes), KU-09 ✅ (chain confirmed non-convex), KU-10 ✅ (markov well-diagnosed), KU-11 ⚠️ (CES singularity is structural)

### Verification

```bash
# Verify triage document exists
ls docs/planning/EPIC_4/SPRINT_23/TRIAGE_MODEL_INFEASIBLE.md

# Verify all 12 models covered (check for per-model headings)
for model in bearing chain cpack lnts markov mathopt3 pak paperco prolog robustlp sparta spatequ; do
  grep -qi "### .*$model" docs/planning/EPIC_4/SPRINT_23/TRIAGE_MODEL_INFEASIBLE.md || echo "MISSING: $model"
done
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_23/TRIAGE_MODEL_INFEASIBLE.md` with root cause classification for all 12 models
- Gross fix candidates vs. likely permanent exclusions
- Recommendation: which 4+ models to target in Sprint 23
- Verification results for KU-06, KU-07, KU-08, KU-09, KU-10, KU-11 in KNOWN_UNKNOWNS.md Appendix C

### Acceptance Criteria

- [x] All 12 models attempted (MCP generation + review)
- [x] Each model classified as A (KKT bug), B (PATH convergence / locally infeasible), C (incompatible), or D (missing feature)
- [x] Models with existing issues (#1049, #1070, #1081, #1110, #1038) cross-referenced
- [x] Fix effort estimated per model
- [x] Top 4+ highest-leverage models identified
- [x] Permanent exclusion candidates flagged (per PR7 gross/influx tracking)
- [x] KU-06, KU-07, KU-08, KU-09, KU-10, KU-11 verification results recorded in KNOWN_UNKNOWNS.md

---

## Task 4: Investigate Alias-Aware Differentiation (#1111)

**Status:** :white_check_mark: COMPLETE
**Priority:** High
**Estimated Time:** 4-6 hours (investigation: ~2h, implementation per design doc: 4-6h)
**Deadline:** Before Sprint 23 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** KU-12, KU-13, KU-15, KU-16, KU-17

### Objective

Research the alias-aware differentiation architectural change needed for Sprint 23 Priority 3. Determine scope of impact, design approach, and regression risk before implementation.

### Why This Matters

Issue #1111 (alias-aware differentiation) is one of two architectural AD changes in Sprint 23. Sprint 22 KU-27 identified this during Day 11: "Naive fix works; needs iteration-context guard." A poorly designed fix could regress currently-solving models. Design-first prevents mid-sprint emergency refactoring.

### Background

- GitHub Issue: #1111 (AD engine: alias-aware differentiation with summation-context tracking)
- Sprint 22 KU-27: Discovered Day 11, deferred to Sprint 23
- Related research: `docs/research/multidimensional_indexing.md`, `docs/research/nested_subset_indexing_research.md`
- AD engine: `src/ad/` (gradient computation, Jacobian computation)
- Current behavior: AD engine treats aliased set indices as independent, producing incorrect derivatives when the same physical index is referenced through different alias names

### What Needs to Be Done

1. **Read Issue #1111 fully** — understand the specific failure case and proposed fix
2. **Identify affected models** — which of the 42 mismatch models are affected by alias issues?
   ```bash
   # Search for alias usage in mismatch models
   grep -il "alias" data/gamslib/raw/*.gms | head -20
   ```
3. **Map the AD pipeline** — trace how set indices flow through:
   - `src/ad/` gradient/Jacobian computation
   - `src/kkt/stationarity.py` stationarity equation generation
   - `src/emit/` MCP emission
4. **Design the fix** — document:
   - Where alias resolution should happen (AD entry, mid-pipeline, or emission)
   - What "summation-context tracking" means concretely
   - How to detect when aliased indices refer to the same physical set
   - Regression safeguards (which tests cover the affected code paths)
5. **Identify test models** — find 2-3 models that demonstrate the bug and will verify the fix
6. **Estimate regression risk** — how many currently-solving models use aliases?

### Changes

- Created `docs/planning/EPIC_4/SPRINT_23/DESIGN_ALIAS_DIFFERENTIATION.md` with full design: root cause analysis, summation-context tracking design, affected models list (21 alias mismatch + 8 matching alias models), regression risk assessment, test plan, and interaction analysis with #1112
- Updated `KNOWN_UNKNOWNS.md` KU-12 through KU-17 verification results and Appendix C tracking table

### Result

- **Root cause:** `_diff_varref()` in `src/ad/derivative_rules.py` uses exact index-tuple matching; aliases are not recognized, producing incomplete gradients
- **Naive fix failure:** Sprint 22 attempted unconditional alias matching, which was reverted because it incorrectly matches sum-bound alias iteration variables (dispatch regression)
- **Proposed fix:** Add `bound_indices: frozenset[str]` keyword parameter to `differentiate_expr()`, threaded through `_diff_sum()` and `_diff_prod()`. `_diff_varref()` checks aliases only when the alias index is NOT in `bound_indices`. Fully backward compatible (keyword-only with default).
- **Impact:** Of 36 total mismatch models (solving but not matching), 21 use aliases in sum expressions (58.3%). Alias models are 76% likely to mismatch vs. 30% for non-alias models. This is the highest-leverage match rate fix available. (Note: the task prompt references "42 mismatch models" which includes multi-solve skipped models; the 36 figure counts only single-solve mismatches.)
- **Regression risk:** MEDIUM. 8 currently-matching alias models (including dispatch) must not regress. The `bound_indices` mechanism specifically handles dispatch's pattern. 56 non-alias solving models are unaffected.
- **Independence:** #1111 and #1112 are fully independent — orthogonal AD pipeline aspects, no coupling
- **Test models:** qabel (verify fix), dispatch (verify no regression), ps2_f (cross-check)
- **KU verification:** KU-12 ⚠️ (design sound, needs implementation testing), KU-13 ✅ (selective by design), KU-15 ✅ (independent of #1112), KU-16 ⚠️ (8-12 irreducible non-convex), KU-17 ⚠️ (convex subset should match after fix)

### Verification

```bash
# Verify investigation document exists
ls docs/planning/EPIC_4/SPRINT_23/DESIGN_ALIAS_DIFFERENTIATION.md

# Verify design includes regression analysis
grep -c "regression" docs/planning/EPIC_4/SPRINT_23/DESIGN_ALIAS_DIFFERENTIATION.md
# Expected: ≥ 1
```

### Deliverables

- :white_check_mark: `docs/planning/EPIC_4/SPRINT_23/DESIGN_ALIAS_DIFFERENTIATION.md` with root cause analysis, affected models list, proposed fix design with code locations, regression risk assessment, test plan
- :white_check_mark: Verification results for KU-12, KU-13, KU-15, KU-16, KU-17 in KNOWN_UNKNOWNS.md Appendix C

### Acceptance Criteria

- [x] Issue #1111 fully understood with concrete failure case documented
- [x] AD pipeline traced for alias handling
- [x] Fix design documented with specific code locations in `src/ad/`
- [x] Affected models identified (both currently-failing and currently-passing)
- [x] Regression risk assessed (count of alias-using models that currently solve)
- [x] 2-3 test models identified for verification
- [x] KU-12, KU-13, KU-15, KU-16, KU-17 verification results recorded in KNOWN_UNKNOWNS.md

---

## Task 5: Investigate Dollar-Condition Propagation (#1112)

**Status:** :white_check_mark: COMPLETE
**Priority:** High
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 23 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** KU-14, KU-15

### Objective

Research the dollar-condition propagation architectural change needed for Sprint 23 Priority 3. Determine where conditions are lost in the AD pipeline and design the propagation mechanism.

### Why This Matters

Issue #1112 (dollar-condition propagation) is the second architectural AD change. Sprint 22 KU-28 identified this during Day 12: "Gradient conditions extractable from DollarConditional nodes." This affects match rate for models where conditional expressions produce different derivatives depending on the enclosing dollar condition.

### Background

- GitHub Issue: #1112 (KKT: Dollar-condition propagation through AD/stationarity pipeline)
- Sprint 22 KU-28: Discovered Day 12, deferred to Sprint 23
- Dollar conditions in GAMS: `expr$condition` or `$(condition)` syntax
- `condition` rule in grammar: `DOLLAR (paren|bracket|cond_bound|ref_indexed|NUMBER|ID)`
- AD engine preserves `DollarConditional` nodes during differentiation (returns `(df/dx)$cond`), but condition propagation/collection into KKT/stationarity domains is incomplete — objective-gradient scanning and stationarity emission lose these conditions
- Stationarity equations need condition guards to match the original model's conditional structure

### What Needs to Be Done

1. **Read Issue #1112 fully** — understand the specific failure case and examples
2. **Trace dollar conditions through the pipeline:**
   - How are `$`-conditions represented in the IR? (`DollarConditional` AST node?)
   - Where in `src/ad/` are they encountered during differentiation?
   - How should they propagate to stationarity equations in `src/kkt/stationarity.py`?
   - How should they appear in the emitted MCP? (as `$` conditions on stationarity equations)
3. **Identify affected models** — which mismatch models use dollar conditions in objectives, constraint definitions, or other expressions that feed AD/stationarity?
4. **Design the propagation mechanism:**
   - Should conditions be tracked as metadata on derivative expressions?
   - Should the gradient/Jacobian carry condition annotations?
   - How to combine multiple nested conditions?
5. **Assess interaction with Task 4** (alias differentiation) — are the two changes independent or coupled?
6. **Estimate regression risk** — dollar conditions are pervasive in GAMS models

### Changes

- Created `docs/planning/EPIC_4/SPRINT_23/DESIGN_DOLLAR_CONDITION_PROPAGATION.md` with full pipeline trace and propagation design
- Updated `KNOWN_UNKNOWNS.md` KU-14 (REFUTED) and KU-15 (VERIFIED) with detailed findings
- Updated Appendix C verification tracking table with dates and results

### Result

Complete pipeline trace identified 2 gaps:
- **GAP 1:** `compute_objective_gradient()` stores derivatives with embedded conditions but never extracts them
- **GAP 2:** `_find_variable_access_condition()` scans equation bodies only, not gradient expressions

Design proposes 3-file fix:
1. `gradient.py`: Add `_extract_gradient_conditions()` (~40 lines) to extract `DollarConditional`/multiplicative conditions from gradient entries
2. `kkt_system.py`: Add `gradient_conditions: dict[str, Expr]` field
3. `stationarity.py`: Add Stage 4 condition check in `build_stationarity_equations()` (~5-10 lines)

Estimated effort: 4h. Primary targets: sambal, qsambal. 42 models use dollar conditions in corpus; regression risk LOW assuming guard-safety criteria from `DESIGN_DOLLAR_CONDITION_PROPAGATION.md` (guards only safe when other stationarity terms are structurally zero when the guard is false, i.e., they only make equations more restrictive under those conditions).

KU-14: REFUTED — requires both gradient AND Jacobian changes (gradient-only sufficient for Sprint 23).
KU-15: VERIFIED — alias (#1111) and dollar-condition (#1112) fixes are architecturally independent, modifying different files with no shared data structures.

### Verification

```bash
# Verify investigation document exists
ls docs/planning/EPIC_4/SPRINT_23/DESIGN_DOLLAR_CONDITION_PROPAGATION.md

# Verify design addresses interaction with alias differentiation
grep -i "alias" docs/planning/EPIC_4/SPRINT_23/DESIGN_DOLLAR_CONDITION_PROPAGATION.md
# Expected: ≥ 1 mention
```

### Deliverables

- :white_check_mark: `docs/planning/EPIC_4/SPRINT_23/DESIGN_DOLLAR_CONDITION_PROPAGATION.md` with full pipeline trace, 2-gap analysis, 3-file propagation design, interaction analysis with #1111, regression risk assessment, and test plan
- :white_check_mark: Verification results for KU-14, KU-15 in KNOWN_UNKNOWNS.md Appendix C

### Acceptance Criteria

- [x] Issue #1112 fully understood with concrete failure case documented (sambal `sum((i,j)$xw(i,j), .../xb(i,j))`)
- [x] Dollar-condition flow traced through IR → AD → KKT → Emit pipeline (§2: 5-stage trace with 2 gaps identified)
- [x] Propagation mechanism designed with specific code locations (§3: gradient.py:~277, kkt_system.py:~136, stationarity.py:~882)
- [x] Interaction with alias differentiation (#1111) assessed (§5: independent, no code overlap)
- [x] Affected models identified (§4: 2 primary targets, 42 models with dollar conditions in corpus)
- [x] Regression risk assessed (§8: LOW — guards only make equations more restrictive; 42 models use dollar conditions)
- [x] KU-14, KU-15 verification results recorded in KNOWN_UNKNOWNS.md

---

## Task 6: Triage path_syntax_error Subcategories G+B

**Status:** :white_check_mark: COMPLETE
**Priority:** High
**Estimated Time:** 2-3 hours
**Deadline:** Before Sprint 23 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** KU-18, KU-19, KU-20, KU-21

### Objective

Identify the specific models in path_syntax_error subcategories G (set index reuse) and B (domain violations), verify root causes, and estimate fix effort for each.

### Why This Matters

Sprint 22 planned to fix subcategories G+B on Days 2-3 but redirected work to WS2/WS3. These models are explicitly deferred to Sprint 23 Priority 4. Prep triage prevents discovering unexpected complexity during the sprint.

### Background

- 20 path_syntax_error models remain overall; Priority 4 targets the G+B subset
- Subcategory G (set index reuse): 1 model (srkandw) — parser bug in `_handle_aggregation()`
- Subcategory B (domain violations): 4 models (chenery, hhfair, otpop, shale) — diverse root causes
- Key issues: #956 (nonsharp), #1041 (cesam2), #882/#871 (camcge)
- Sprint 22 KU-03 refuted the assumption that subcategory B models share a common emitter bug — "original 5 models dispersed; current B is cesam/cesam2 (new)"
- Sprint 22 KU-04 verified aliasing mechanism is sound for subcategory G

### What Needs to Be Done

1. **Identify the specific G+B models** by running the pipeline on all 20 path_syntax_error models and categorizing the error type
2. **For subcategory G model (srkandw):**
   - Examine the set index reuse pattern in the GAMS source
   - Verify Sprint 22 KU-04 finding (aliasing mechanism works)
   - Estimate fix effort
3. **For subcategory B models (4: chenery, hhfair, otpop, shale):**
   - Note Sprint 22 KU-03 finding — these are NOT a single emitter bug
   - Classify each model's specific domain violation
   - Estimate fix effort per model
4. **Check for overlap** — do any G+B models also appear in path_solve_terminated or model_infeasible lists?
5. **Create ranked fix list** with dependencies

### Changes

- Created `docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SYNTAX_ERROR_GB.md` with full triage of all 20 path_syntax_error models
- Updated `KNOWN_UNKNOWNS.md` KU-18 (PARTIAL), KU-19 (VERIFIED), KU-20 (VERIFIED), KU-21 (PARTIAL)
- Updated Appendix C verification tracking table

### Result

**Revised G+B counts:** 1 subcategory G + 4 subcategory B = **5 models** (not 7 as estimated):
- **G:** srkandw — parser bug in `_handle_aggregation()` filters out subset domain index, producing empty sum domain
- **B:** chenery (index shadowing), hhfair (offset arithmetic), otpop (alias-as-subset condition), shale (subset condition domain mismatch)

Sprint 22 fixed 3/4 original G models and reclassified cesam, reducing the G+B target. All 4 B models have diverse root causes (KU-19 verified). No cross-category overlap with model_infeasible or path_solve_terminated (KU-20 verified: 0 CGE models, cascade risk 0-1).

Total estimated effort: 9-14h (higher than 2-3h prep estimate; individual fixes, not batch-fixable). New subcategories (KU-21): gussrisk already fixed, gtm 1-2h, tricp NOT low-effort (4-6h).

### Verification

```bash
# Verify triage document exists
ls docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SYNTAX_ERROR_GB.md

# Verify both subcategories covered
grep -c "Subcategory" docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SYNTAX_ERROR_GB.md
# Expected: ≥ 2
```

### Deliverables

- :white_check_mark: `docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SYNTAX_ERROR_GB.md` with full classification of all 20 path_syntax_error models, per-model root cause for 5 G+B models, fix effort estimates, cross-category overlap analysis
- :white_check_mark: Verification results for KU-18, KU-19, KU-20, KU-21 in KNOWN_UNKNOWNS.md Appendix C

### Acceptance Criteria

- [x] All G+B models identified by name (5 models: srkandw, chenery, hhfair, otpop, shale — revised from 7)
- [x] Each model's specific error pattern documented (GAMS error codes + root cause analysis)
- [x] Sprint 22 KU-03 and KU-04 findings verified/updated (KU-03 confirmed: diverse B causes; KU-04: mechanism sound but srkandw needs parser fix)
- [x] Fix effort estimated per model (total 9-14h)
- [x] Cross-category overlap checked (no overlap with model_infeasible or path_solve_terminated)
- [x] Ranked fix priority created (5-tier ranking in triage doc §6)
- [x] KU-18, KU-19, KU-20, KU-21 verification results recorded in KNOWN_UNKNOWNS.md

---

## Task 7: Catalog and Classify Translate Failures (13)

**Status:** :white_check_mark: COMPLETE
**Priority:** Medium
**Estimated Time:** 2 hours
**Deadline:** Before Sprint 23 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** KU-22, KU-23, KU-24, KU-25

### Objective

Catalog all translate failures (13 remaining after rerun; originally estimated 15), classify by root cause, and identify the highest-leverage fixes for Sprint 23 Priority 5.

### Why This Matters

Sprint 23 targets reducing translate failures from 13 to ≤ 11 (≥ 145/156). Without knowing which models fail and why, the sprint risks spending time on intractable timeout models instead of quick fixable-error models.

### Background

- 13 translate failures remain (143/156 = 91.7% translate rate; originally estimated 15 but 3 recovered on rerun)
- Mix of timeouts (7), missing IR features (4), and internal errors (2) — no traditional compilation errors
- Sprint 23 acceptance criterion: ≥ 93% of parsed models (≥ 145/156 assuming 156 parsed)
- Pipeline retest script: `.venv/bin/python scripts/gamslib/run_full_test.py`
- Related issues: #940 (mexls universal set), #830 (gastrans Jacobian timeout), #885 (sarf timeout)
- ~~#952 (lmp2), #953 (paperco), #1062 (tricp)~~ — not translate failures (lmp2/paperco refuted by KU-25; tricp is path_syntax_error Priority 4)

### What Needs to Be Done

1. **Run pipeline on all 156 parsed models and capture translate failures:**
   ```bash
   .venv/bin/python scripts/gamslib/run_full_test.py --only-translate --quiet 2>&1 | grep -Ei 'fail|error|timeout'
   ```
2. **For each failure, classify as:**
   - **A: Compilation error** — GAMS can't compile the MCP output; fix in emitter/translator
   - **B: Timeout** — Translation takes too long; may need recursion/complexity optimization
   - **C: Missing IR feature** — Model uses grammar constructs not yet in the IR
   - **D: Internal error** — Python exception during translation
3. **For compilation errors, capture the specific GAMS error message**
4. **Cross-reference with existing issues** (#952, #953, #940, #1062, etc.)
5. **Rank by fix effort** — quick compilation fixes first, then investigate timeouts

### Changes

- Created `docs/planning/EPIC_4/SPRINT_23/CATALOG_TRANSLATE_FAILURES.md` with full classification of all 13 remaining failures
- Updated `KNOWN_UNKNOWNS.md` KU-22 (VERIFIED), KU-23 (VERIFIED), KU-24 (REFUTED), KU-25 (REFUTED)
- Updated Appendix C verification tracking table

### Result

**Revised failure count:** 13 translate failures (not 15 as estimated):
- ferts and turkpow already translate successfully (slow but under 150s timeout)
- clearlak recovered on pipeline rerun (marginal timeout → now completes in ~148s)
- Current baseline: 143/156 = 91.7% (not 141/156 = 90.4%)

**Classification:** 7 timeout (B), 4 missing IR feature (C: LhsConditionalAssign), 2 internal error (D: mexls #940, mine SetMembershipTest)

**Key finding:** The 4 LhsConditionalAssign models (agreste, ampl, cesam, korcge) share a single root cause — missing statement-level emission support for LhsConditionalAssign (currently falls through to `expr_to_gams()` and raises). A single 2-3h fix recovers all 4 → 147/156 (94.2%), exceeding the ≥ 145 target. The 7 timeouts are architecturally intractable (Jacobian computation bottleneck).

**KU-24 REFUTED:** Only 2 fixes needed to reach target (not 4), because baseline is 143 not 141.
**KU-25 REFUTED:** paperco/lmp2 are NOT translate failures — they translate successfully but fail at solve.

Sprint 23 Priority 5 effort: **2-3h** (Tier 1: LhsConditionalAssign fix alone exceeds target).

### Verification

```bash
# Verify catalog document exists
ls docs/planning/EPIC_4/SPRINT_23/CATALOG_TRANSLATE_FAILURES.md

# Verify all 13 current failures covered in catalog tables
for model in agreste ampl cesam ganges gangesx gastrans iswnm korcge mexls mine nebrazil sarf srpchase; do
  grep -qiw "$model" docs/planning/EPIC_4/SPRINT_23/CATALOG_TRANSLATE_FAILURES.md || echo "MISSING: $model"
done

# Verify 3 recovered models documented in §6
for model in ferts turkpow clearlak; do
  grep -qiw "$model" docs/planning/EPIC_4/SPRINT_23/CATALOG_TRANSLATE_FAILURES.md || echo "MISSING recovered: $model"
done
```

### Deliverables

- :white_check_mark: `docs/planning/EPIC_4/SPRINT_23/CATALOG_TRANSLATE_FAILURES.md` with classification for all 13 failures, error details, issue cross-references, ranked fix priority, recovered models list
- :white_check_mark: Verification results for KU-22, KU-23, KU-24, KU-25 in KNOWN_UNKNOWNS.md Appendix C

### Acceptance Criteria

- [x] All 13 translate failures identified by name (revised from 15 — ferts, turkpow, clearlak recovered)
- [x] Each classified as timeout (B), missing feature (C), or internal error (D)
- [x] Error details captured for all failures (no compilation errors in traditional sense)
- [x] Cross-referenced with existing GitHub issues (#830, #885, #929, #930, #931, #932, #940)
- [x] Highest-leverage fix identified: LhsConditionalAssign handler recovers 4 models (2-3h)
- [x] KU-22, KU-23, KU-24, KU-25 verification results recorded in KNOWN_UNKNOWNS.md

---

## Task 8: Run Full Pipeline Baseline (per PR6)

**Status:** :white_check_mark: COMPLETE
**Priority:** Critical
**Estimated Time:** 1-2 hours
**Deadline:** Before Sprint 23 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** KU-26

### Objective

Establish the definitive Sprint 23 baseline using a full pipeline run (per Sprint 22 process recommendation PR6). This provides the starting metrics that all Sprint 23 progress is measured against.

### Why This Matters

Sprint 22 retrospective identified that partial pipeline (`--only-solve`) gave misleading intermediate metrics (Day 11 showed solve 80, match 41; full pipeline showed solve 89, match 47). PR6 mandates full pipeline for all definitive metrics. The Sprint 23 baseline must use the same methodology as checkpoints and final metrics.

### Background

- Sprint 22 final: parse 156/160, translate 141/156, solve 89/141, match 47/160
- Pipeline script: `.venv/bin/python scripts/gamslib/run_full_test.py`
- Status JSON: `data/gamslib/gamslib_status.json`
- PR6: Use full pipeline for all definitive metrics
- PR7: Track model_infeasible gross fixes and gross influx separately
- PR8: Use absolute counts alongside percentages for parse success

### What Needs to Be Done

1. **Run full pipeline** (all stages, no `--only-*` flags):
   ```bash
   .venv/bin/python scripts/gamslib/run_full_test.py --quiet
   ```
2. **Record all metrics per PR6/PR7/PR8:**
   - Parse: X/160 (Y%)
   - Translate: X/Y (Z% of parsed)
   - Solve: X (count) + X/Y (Z% of translated)
   - Match: X (count) + X/160 (Y% of corpus)
   - Error categories: path_syntax_error, path_solve_terminated, model_infeasible, path_solve_license (counts)
   - model_infeasible breakdown: in-scope vs. permanently excluded
3. **Compare against Sprint 22 final metrics** to confirm no regressions since merge
4. **Save baseline metrics** for Sprint 23 checkpoint comparisons
5. **Create baseline document** that will be referenced throughout Sprint 23

### Changes

- Ran full pipeline (`run_full_test.py --quiet`, no `--only-*` flags) on 147 candidate models
- Created `docs/planning/EPIC_4/SPRINT_23/BASELINE_METRICS.md` with full metrics
- Updated `data/gamslib/gamslib_status.json` (fresh results for all 147 candidates)
- Verified KU-26 (multi-solve incomparable stability) — all 6 models confirmed stable
- Updated KNOWN_UNKNOWNS.md: KU-26 marked VERIFIED with details in both body and Appendix C
- Note: Pipeline regenerated MCP files for models whose translate status changed (e.g., borderline timeout models). These MCP file changes are excluded from this PR to keep it purely a baseline-recording commit; the status JSON captures the pipeline results.

### Result

**Sprint 23 Baseline (full corpus, 160 models):**
- Parse: 156/160 (97.5%) — unchanged from Sprint 22
- Translate: 139/156 (89.1%) — -2 vs Sprint 22 (borderline timeout variance)
- Solve: 89/139 (64.0%) — unchanged from Sprint 22
- Match: 47/160 (29.4%) — unchanged from Sprint 22

**Translate delta:** 17 failures vs Sprint 22's 15. Deterministic failures (6) are stable. 11 timeouts vs ~9 in Sprint 22. In the earlier Task 7 spot-check run, clearlak, ferts, and turkpow completed within the 150s limit and were marked as "recovered"; in this full baseline run they land at 150.0-150.2s and are recorded as timeouts, which accounts for the net -2 vs Sprint 22 (dinam is also borderline at 150.2s but does not change the Sprint 22 failure count).

**No functional regressions detected.** Solve (89) and match (47) are identical to Sprint 22.

**KU-26:** VERIFIED — 6 multi-solve models (aircraft, apl1p, apl1pca, ps10_s_mn, ps5_s_mn, senstran) correctly flagged and skipped.

### Verification

```bash
# Verify baseline document exists
ls docs/planning/EPIC_4/SPRINT_23/BASELINE_METRICS.md

# Verify gamslib_status.json is up to date
ls -la data/gamslib/gamslib_status.json
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_23/BASELINE_METRICS.md` with:
  - Full pipeline results (parse, translate, solve, match)
  - Error category breakdown
  - Comparison with Sprint 22 final metrics
  - Confirmation of no regressions
- Updated `data/gamslib/gamslib_status.json`
- Verification results for KU-26 in KNOWN_UNKNOWNS.md Appendix C

### Acceptance Criteria

- [x] Full pipeline run completed (no `--only-*` flags)
- [x] All metrics recorded: parse, translate, solve, match, error categories
- [x] Metrics expressed as both absolute counts and percentages (per PR8)
- [x] model_infeasible split into in-scope and permanently excluded (per PR7)
- [x] No regressions vs Sprint 22 final metrics confirmed
- [x] Baseline document created
- [x] KU-26 verification result recorded in KNOWN_UNKNOWNS.md

---

## Task 9: Review Sprint 22 Retrospective Action Items

**Status:** :white_check_mark: COMPLETE
**Priority:** High
**Estimated Time:** 1 hour
**Deadline:** Before Sprint 23 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1-8 (Known Unknowns identifies gaps; Tasks 2-8 provide KU verification results to cross-check)
**Unknowns Verified:** All 26 KUs cross-checked (12 VERIFIED, 11 PARTIAL, 3 REFUTED)

### Objective

Verify that all Sprint 22 retrospective recommendations and action items are captured in Sprint 23 planning. Confirm nothing is missed.

### Why This Matters

Sprint 22 retrospective identified 5 "What Could Be Improved" items and 3 "What We'd Do Differently" items. Some are process changes (PR6-PR8), others are deferred technical work. All must be explicitly addressed or deferred with justification.

### Background

- Sprint 22 Retrospective: `docs/planning/EPIC_4/SPRINT_22/SPRINT_RETROSPECTIVE.md`
- Process recommendations: PR6 (full pipeline), PR7 (gross fixes/influx), PR8 (absolute counts)
- Sprint 22 deferred items: subcategories G+B, path_solve_terminated residual
- Sprint 23 section in PROJECT_PLAN.md: lines 629-740

### What Needs to Be Done

1. **Read Sprint 22 Retrospective completely** — extract all action items and recommendations
2. **Map each item to Sprint 23 tasks or process changes:**

   | Sprint 22 Recommendation | Sprint 23 Action | Status |
   |--------------------------|------------------|--------|
   | PR6: Full pipeline for definitive metrics | Task 8 baseline + all checkpoints | Planned |
   | PR7: Gross fixes/influx tracking | Acceptance criteria + reporting | Planned |
   | PR8: Absolute counts for parse | Acceptance criteria + reporting | Planned |
   | WS1 G+B deferred | Priority 4 | Planned |
   | path_solve_terminated ≤ 5 | Priority 1 | Planned |
   | model_infeasible influx budget | Priority 2 + PR7 | Planned |
   | Full pipeline at checkpoints | Sprint 23 process | Planned |

3. **Identify any gaps** — items not captured in Sprint 23 planning
4. **Update Known Unknowns** (Task 1) if new risks found
5. **Create alignment document**

### Changes

- Created `docs/planning/EPIC_4/SPRINT_23/RETROSPECTIVE_ALIGNMENT.md` with 8 sections: WCI items (5), WDD items (3), PR6/PR7/PR8 integration evidence, target alignment table, deferred items tracking, PR1-PR5 continuity, KU cross-check, and gap analysis
- Cross-checked all 26 KU verification results from Appendix C in KNOWN_UNKNOWNS.md — all complete (no INCOMPLETE entries)
- Updated KNOWN_UNKNOWNS.md header status from "KU-26 pending (Task 8)" to "Tasks 2-8 complete" — no new risk entries needed

### Result

**All Sprint 22 retrospective items are addressed in Sprint 23 planning. No gaps found.**

- 5 "What Could Be Improved" items: all mapped to Sprint 23 actions (WCI-1 → Task 2 triage-first, WCI-2 → Priority 4 G+B, WCI-3 → PR6, WCI-4 → PR7, WCI-5 → PR8)
- 3 "What We'd Do Differently" items: all addressed (WDD-1 → Task 6 triage + scheduling recommendation, WDD-2 → PR6 mandated, WDD-3 → KU-05/KU-08 influx budgeting)
- 3 new process recommendations (PR6, PR7, PR8): all integrated with specific evidence in PROJECT_PLAN.md, BASELINE_METRICS.md, and PREP_PLAN.md
- 5 continuing recommendations (PR1-PR5): PR3 upgraded to PR6; all others continue
- 8 suggested targets: all aligned between retrospective, PROJECT_PLAN.md, and Sprint 23 planning
- 7 deferred items: 6 addressed, 1 intentionally deferred (non-convex multi-KKT, KU-16)
- 26/26 KUs resolved: 12 VERIFIED, 11 PARTIAL (residual risks documented), 3 REFUTED
- 3 minor observations (non-blocking): translate baseline discrepancy explained, PST target calibration backed by triage, effort estimate inflation noted for Task 10

### Verification

```bash
# Verify alignment document exists
ls docs/planning/EPIC_4/SPRINT_23/RETROSPECTIVE_ALIGNMENT.md

# Verify all 3 process recommendations addressed
grep -c "PR[678]" docs/planning/EPIC_4/SPRINT_23/RETROSPECTIVE_ALIGNMENT.md
# Expected: ≥ 3
```

### Deliverables

- :white_check_mark: `docs/planning/EPIC_4/SPRINT_23/RETROSPECTIVE_ALIGNMENT.md` with mapping of all Sprint 22 retrospective items to Sprint 23 actions, PR6/PR7/PR8 integration evidence, KU cross-check, gap analysis
- :white_check_mark: Cross-check of all 26 KU verification results from Tasks 2-8 (complete, no gaps)

### Acceptance Criteria

- [x] Sprint 22 Retrospective reviewed completely
- [x] All "What Could Be Improved" items mapped to Sprint 23 actions (§1: WCI-1 through WCI-5)
- [x] All "What We'd Do Differently" items addressed (§2: WDD-1 through WDD-3)
- [x] PR6, PR7, PR8 confirmed in Sprint 23 process (§3: integration evidence tables)
- [x] Any deferred items documented with justification (§5: 6 addressed, 1 intentionally deferred)
- [x] Alignment document created (RETROSPECTIVE_ALIGNMENT.md, 8 sections)
- [x] All KU verification results from Tasks 2-8 cross-checked for completeness (§7: 26/26 complete)

---

## Task 10: Plan Sprint 23 Detailed Schedule

**Status:** :white_check_mark: COMPLETE
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 23 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1-9 (all prep tasks inform the plan)
**Unknowns Verified:** (synthesis — all KU verification results incorporated into schedule)

### Objective

Create detailed Sprint 23 plan with day-by-day schedule, checkpoints, and contingency plans, incorporating all findings from prep tasks.

### Why This Matters

Sprint 23 has 5 priority areas and 32-44 hours of estimated work across 15 sprint days (Day 0-14). Without a detailed schedule, work will be unfocused and the ambitious targets (solve +11, match +8) are unlikely to be met. Sprint 22's structured approach (15-day schedule, 2 checkpoints, day-by-day prompts) was effective and should be replicated.

### Background

- Sprint 23 in PROJECT_PLAN.md: `docs/planning/EPIC_4/PROJECT_PLAN.md` lines 629-740
- Sprint 22 Plan format: `docs/planning/EPIC_4/SPRINT_22/PLAN.md` (15-day schedule, 2 checkpoints)
- Sprint 22 Prompts: `docs/planning/EPIC_4/SPRINT_22/prompts/PLAN_PROMPTS.md` (day-by-day execution)
- Estimated effort: 32-44 hours across 5 priorities
- 24 GitHub issues labeled `sprint-23`

### What Needs to Be Done

1. **Synthesize all prep task findings** into a coherent sprint plan:
   - Task 1 Known Unknowns → risk mitigation schedule
   - Task 2 path_solve_terminated triage → Priority 1 day assignments
   - Task 3 model_infeasible triage → Priority 2 day assignments
   - Task 4 alias differentiation design → Priority 3 implementation plan
   - Task 5 dollar-condition design → Priority 3 implementation plan
   - Task 6 G+B triage → Priority 4 day assignments
   - Task 7 translate catalog → Priority 5 day assignments
   - Task 8 baseline → starting metrics for checkpoints
   - Task 9 retrospective alignment → process requirements
2. **Create 15-day schedule (Day 0-14)** with:
   - Day-by-day tasks
   - Which priority area each day addresses
   - Expected metrics improvements per day
   - Integration risks per day
3. **Define 2 checkpoints:**
   - Checkpoint 1 (Day 5): Expected metrics, GO/CONDITIONAL GO/NO-GO criteria
   - Checkpoint 2 (Day 10): Expected metrics, GO/NO-GO criteria
4. **Create day-by-day prompts** for execution (following Sprint 22 format)
5. **Define contingency plans** for high-risk areas (alias differentiation regressions, model_infeasible influx)
6. **Map 32 sprint-23 issues (24 open + 8 closed)** to specific days

### Changes

- Created `docs/planning/EPIC_4/SPRINT_23/PLAN.md` with 15-day schedule (Day 0-14), 5 workstreams, 2 checkpoints, 4 contingency plans, issue-to-day mapping for all 32 sprint-23 issues (24 open + 8 closed), risk register, and acceptance criteria
- Created `docs/planning/EPIC_4/SPRINT_23/prompts/PLAN_PROMPTS.md` with day-by-day execution prompts for all 15 days
- Initialized `docs/planning/EPIC_4/SPRINT_23/SPRINT_LOG.md` with baseline metrics, workstream-to-issue mapping, model_infeasible gross/influx tracking table (PR7), and day-by-day progress template
- Updated CHANGELOG.md with consolidated prep task entries (Tasks 2-10)

### Result

**Sprint 23 plan synthesizes all 9 prep task findings into a coherent 15-day schedule:**

- **5 workstreams** mapped to specific days: WS1 path_solve_terminated (Days 1, 4-5), WS2 model_infeasible (Days 6-8), WS3 match rate (Days 2-5), WS4 path_syntax_error (Days 8-10), WS5 translate (Day 1)
- **2 checkpoints** with GO/CONDITIONAL GO/NO-GO criteria: Checkpoint 1 (Day 5) targets solve ≥ 95, match ≥ 50; Checkpoint 2 (Day 10) targets solve ≥ 98, match ≥ 53
- **Issue mapping:** All 32 sprint-23 issues (24 open + 8 closed) mapped: 10 scheduled to Sprint 23 days, 14 deferred/backlog, 8 closed (Sprint 22 fixes)
- **Schedule key decisions:**
  - #1111 alias differentiation on Days 2-3 (highest leverage: 21 mismatch models)
  - #1112 dollar-condition propagation on Days 4-5 (unblocks sambal/qsambal)
  - WS5 LhsConditionalAssign on Day 1 (quick win: +4 translate, 2-3h)
  - WS2 Tier 1 on Days 6-8 (5 diagnosed KKT bugs)
  - WS4 G+B on Days 8-10 (5 individual fixes)
- **4 contingency plans:** alias regression revert, model_infeasible influx budget, #1112 over-extraction, WS4 effort overflow
- **Process requirements integrated:** PR6 (full pipeline at checkpoints), PR7 (gross/influx tracking table in SPRINT_LOG), PR8 (absolute counts in all metrics)
- **Risk register:** 4 risks tracked with probability, impact, and mitigation
- **Estimated effort:** 36-48h (slightly above 32-44h budget at upper end; contingency: defer WS4 models 4-5 and WS2 Tier 2)

### Verification

```bash
# Verify plan document exists
ls docs/planning/EPIC_4/SPRINT_23/PLAN.md

# Verify prompts exist
ls docs/planning/EPIC_4/SPRINT_23/prompts/PLAN_PROMPTS.md

# Verify 15-day schedule
grep -c "^## Day" docs/planning/EPIC_4/SPRINT_23/PLAN.md
# Expected: ≥ 15 (Day 0 through Day 14)

# Verify checkpoints defined
grep -c "Checkpoint" docs/planning/EPIC_4/SPRINT_23/PLAN.md
# Expected: ≥ 2
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_23/PLAN.md` with:
  - Sprint goals and acceptance criteria
  - 15-day schedule (Day 0-14)
  - 2 checkpoints with GO/NO-GO criteria
  - Risk mitigation plan
  - Issue-to-day mapping
- `docs/planning/EPIC_4/SPRINT_23/prompts/PLAN_PROMPTS.md` with day-by-day execution prompts
- `docs/planning/EPIC_4/SPRINT_23/SPRINT_LOG.md` (initialized, empty)
- All KU verification results synthesized into risk mitigation schedule

### Acceptance Criteria

- [x] Plan created with 15-day schedule (Day 0-14)
- [x] All 5 priority areas assigned to specific days
- [x] 2 checkpoints defined with expected metrics and GO/NO-GO criteria
- [x] Day-by-day prompts created
- [x] All 32 sprint-23 issues mapped to days or backlog (24 open + 8 closed)
- [x] Contingency plans for alias differentiation regressions and model_infeasible influx (4 contingency plans)
- [x] PR6/PR7/PR8 process requirements integrated into plan
- [x] Sprint log initialized
- [x] All KU verification results from Tasks 2-9 incorporated into risk mitigation (4-item risk register)

---

## Summary and Critical Path

### Critical Path (Must Complete Before Sprint 23 Day 1)

```
Task 1 (Known Unknowns) ──┐
                           │
Task 8 (Full Pipeline)  ───┤
                           │  ──→ Task 9 (Retro Alignment) ──→ Task 10 (Detailed Plan)
Tasks 2-7 (Triage, in  ───┤
  parallel)                │
```

**Critical path time (fully parallel):** ~9-12 hours — max(Task 1, Task 8) + max(Tasks 2-7) + Task 9 + Task 10 = (2-3h) + (3-4h) + 1h + (3-4h)
**Critical path time (single person, sequential Tasks 2-7):** ~23-31 hours — Task 1 + Task 8 + Tasks 2-7 + Task 9 + Task 10

1. **Task 1: Known Unknowns** (2-3h) — informs risk identification for all other tasks
2. **Task 8: Full Pipeline Baseline** (1-2h) — provides starting metrics; can run in parallel with Task 1
3. **Tasks 2-7: Triage/Investigation** (16-21h sequential, or 3-4h if fully parallelized) — provide findings for plan
4. **Task 9: Retrospective Alignment** (1h) — confirms nothing missed
5. **Task 10: Detailed Plan** (3-4h) — synthesizes all findings; MUST be last

### Execution Phases

**Phase 1: Research & Baseline (can be parallel)**
- Task 1: Known Unknowns
- Task 8: Full Pipeline Baseline

**Phase 2: Triage & Investigation (can be parallel)**
- Task 2: path_solve_terminated triage
- Task 3: model_infeasible triage
- Task 4: Alias differentiation investigation
- Task 5: Dollar-condition investigation
- Task 6: path_syntax_error G+B triage
- Task 7: Translate failures catalog

**Phase 3: Synthesis & Planning**
- Task 9: Retrospective alignment
- Task 10: Detailed schedule (depends on all above)

### Total Estimated Time: 23-31 hours (~3-4 working days)

---

## Success Criteria for Prep Phase

- [x] Known Unknowns document created with ≥ 25 unknowns
- [x] All 10 path_solve_terminated models triaged with root cause
- [x] All 12 model_infeasible models triaged with root cause
- [x] Alias-aware differentiation (#1111) design documented
- [x] Dollar-condition propagation (#1112) design documented
- [x] 5 path_syntax_error G+B models triaged
- [x] 13 translate failures cataloged and classified (revised from 15)
- [x] Full pipeline baseline established (per PR6)
- [x] Sprint 22 retrospective items confirmed in Sprint 23 plan
- [x] Sprint 23 PLAN.md completed with 15-day schedule and checkpoints

**Overall Goal:** Sprint 23 begins with clear triage, validated designs, and a data-driven plan. No surprises.

---

## Appendix: Document Cross-References

### Sprint Goals
- `docs/planning/EPIC_4/PROJECT_PLAN.md` lines 629-740 — Sprint 23 definition
- `docs/planning/EPIC_4/GOALS.md` — Epic 4 overarching goals

### Prior Sprint Documentation
- `docs/planning/EPIC_4/SPRINT_22/SPRINT_RETROSPECTIVE.md` — Sprint 22 retrospective with Sprint 23 recommendations
- `docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md` — Sprint 22 Known Unknowns (KU-27, KU-28 carry forward)
- `docs/planning/EPIC_4/SPRINT_22/DEFERRED_ISSUES_DECISION.md` — Sprint 22 deferred items
- `docs/planning/EPIC_4/SPRINT_22/PLAN.md` — Sprint 22 plan (template for Sprint 23)
- `docs/planning/EPIC_4/SPRINT_22/prompts/PLAN_PROMPTS.md` — Sprint 22 day-by-day prompts (template)

### Research Documents
- `docs/research/multidimensional_indexing.md` — Relevant to alias differentiation (#1111)
- `docs/research/nested_subset_indexing_research.md` — Relevant to alias differentiation (#1111)

### GitHub Issues (sprint-23 label, 24 total)
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

### Pipeline and Testing
- `.venv/bin/python scripts/gamslib/run_full_test.py` — Full pipeline retest script
- `data/gamslib/gamslib_status.json` — Pipeline status database
- `data/gamslib/raw/` — GAMSlib model files (local only, not in CI)

---

**Document Created:** 2026-03-17
**Sprint 23 Target Start:** TBD (after prep completion)
**Next Steps:** Execute prep tasks in order, verify completion, begin Sprint 23
