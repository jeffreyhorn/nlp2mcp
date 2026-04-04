# Sprint 24 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 24 begins
**Timeline:** Complete before Sprint 24 Day 1
**Goal:** Set up Sprint 24 for success — Alias Differentiation & Error Category Reduction (solve 86 → ≥ 95, match 49 → ≥ 55)

**Key Insight from Sprint 23:** Translate influx masked solve improvements — 12 new translates brought 5 new path_syntax_error and 2 new path_solve_terminated. Sprint 24 prep must budget for error category influx (PR10) and prioritize the highest-leverage architectural fix (alias differentiation, PR11) before incremental fixes. Targets are set against the 147-model pipeline scope (PR9).

**Branching:** All prep task branches should be created from `main` and PRs should target `main`.

---

## Executive Summary

Sprint 24 targets alias-aware differentiation as the single highest-leverage workstream, affecting ~20 models across solve, match, and error categories. The #1111 family (12 open issues) is the dominant blocker for both solve rate and match rate improvement. Secondary priorities address path_syntax_error influx (23 → ≤ 15), model_infeasible reduction (11 → ≤ 8), and translation timeouts (6 remaining).

This prep plan focuses on:
1. **Risk identification** — Known Unknowns for alias differentiation, error influx, and architectural risks
2. **Alias differentiation deep analysis** — Root cause classification across 12 issues, architectural design
3. **Error category triage** — Classify path_syntax_error influx and model_infeasible Jacobian issues
4. **Translation timeout investigation** — Feasibility analysis for remaining 6 timeout models
5. **Baseline establishment** — Full pipeline baseline per PR6
6. **Sprint planning** — Detailed schedule with checkpoints

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|----------------------|
| 1 | Create Sprint 24 Known Unknowns List | Critical | 2-3h | None | All priorities — risk identification |
| 2 | Analyze Alias Differentiation Root Causes (#1111 Family) | Critical | 4-5h | Task 1 | Priority 1: alias differentiation (~20 models) |
| 3 | Design Alias Differentiation Architecture | Critical | 3-4h | Task 2 | Priority 1: summation-context tracking design |
| 4 | Triage path_syntax_error Models (23) | High | 3-4h | Task 1 | Priority 2: path_syntax_error ≤ 15 |
| 5 | Triage model_infeasible Models (11) | High | 2-3h | Task 1 | Priority 3: model_infeasible ≤ 8 |
| 6 | Investigate Translation Timeouts (6 models) | Medium | 2-3h | None | Priority 4: translate ≥ 97% |
| 7 | Run Full Pipeline Baseline (per PR6) | Critical | 1-2h | None | All priorities — baseline metrics |
| 8 | Review Sprint 23 Retrospective Action Items | High | 1h | Tasks 1-7 | Process — ensure nothing missed |
| 9 | Plan Sprint 24 Detailed Schedule | Critical | 3-4h | Tasks 1-8 | All priorities — sprint planning |

**Total Estimated Time:** 21-29 hours (~3 working days)

**Critical Path:** Task 1 → Tasks 2 + 4 + 5 (parallel) → Task 3 → Task 8 → Task 9

Tasks 6 and 7 are independent and can run in parallel with any other task.

---

## Task 1: Create Sprint 24 Known Unknowns List

**Status:** :white_check_mark: COMPLETE
**Priority:** Critical
**Estimated Time:** 2-3 hours
**Deadline:** Before Sprint 24 Day 1
**Owner:** Sprint planning
**Dependencies:** None

### Objective

Create proactive list of assumptions and unknowns for Sprint 24 to prevent late discoveries during implementation. This is the first task because it surfaces risks that inform all other prep tasks.

### Why This Matters

Sprint 23 Known Unknowns (32 entries: 26 original + 6 end-of-sprint discoveries) correctly predicted several outcomes: KU-27 (subset-superset domain) led to a high-impact fix, and KU-31 (LP fast path limitations) proved accurate. Sprint 24's alias differentiation work is architecturally complex and carries regression risk — early documentation of unknowns is critical.

### Background

- Sprint 23 Known Unknowns: `docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md` (32 KUs across 6 sections + end-of-sprint discoveries)
- Sprint 23 Retrospective: `docs/planning/EPIC_4/SPRINT_23/SPRINT_RETROSPECTIVE.md` (5 priorities, 3 new process recommendations PR9-PR11)
- 20 issues labeled `sprint-24` in GitHub (12 alias-differentiation, 5 execution/timeout, 3 infeasibility)
- Sprint 23 end-of-sprint discoveries: KU-27 through KU-32

### What Needs to Be Done

1. **Review Sprint 23 deferred KUs** — KU-28 (dynamic `.up` bounds), KU-29 (concrete element offsets), KU-32 (duplicate `.fx` statements) carry forward
2. **For each Priority area, brainstorm unknowns:**
   - **Priority 1 (alias differentiation):** Does summation-context threading affect all derivative rules or only `_diff_varref`? Will fixing alias derivatives regress currently-matching models? Is the #1150 (distinct sum indices) the same root cause as #1137-#1147?
   - **Priority 2 (path_syntax_error):** Are the 5 influx models from Sprint 23 the same subcategories as existing errors? Do the 23 total share common patterns amenable to batch fixes?
   - **Priority 3 (model_infeasible):** Do Jacobian accuracy fixes overlap with alias differentiation? Will fixing bearing/chenery require architectural changes beyond the #1111 fix?
   - **Priority 4 (translation timeout):** Are the 6 timeout models fundamentally too large for symbolic differentiation? Can sparse Jacobian techniques help?
3. **Categorize by topic, prioritize by risk, define verification method**
4. **Assign verification deadlines** (Day 0-1 for Critical, Day 2-3 for High)
5. **Create document** following Sprint 23 KNOWN_UNKNOWNS.md format

### Changes

- Created `docs/planning/EPIC_4/SPRINT_24/KNOWN_UNKNOWNS.md` with 26 unknowns across 5 categories + cross-cutting
- Sprint 23 KU-28 → KU-22, KU-29 → KU-23, KU-32 → KU-24
- Task-to-Unknown mapping table in Appendix A assigns verification responsibility
- Priority distribution: 7 Critical (27%), 10 High (38%), 7 Medium (27%), 2 Low (8%)

### Result

26 unknowns documented across 6 sections:
- **Category 1: Alias-Aware Differentiation** (8 KUs: KU-01–KU-08) — covers summation-context scope, multi-pattern root cause, regression risk, offset-alias, sameas guards, rollout strategy, CGE patterns, quadratic forms
- **Category 2: path_syntax_error Reduction** (5 KUs: KU-09–KU-13) — covers influx patterns, alias overlap, concrete offsets, batch fixes, error influx from alias fix
- **Category 3: model_infeasible Reduction** (5 KUs: KU-14–KU-18) — covers Jacobian overlap, bearing, chenery, influx risk, Category B fixability
- **Category 4: Translation Timeout & Internal Error** (3 KUs: KU-19–KU-21) — covers intractability, sparse Jacobian, internal error
- **Sprint 23 Carryforward** (3 KUs: KU-22–KU-24) — dynamic bounds, concrete offsets, duplicate `.fx`
- **Cross-cutting** (2 KUs: KU-25–KU-26) — error influx budget, effort estimate

### Verification

```bash
# Verify Known Unknowns document exists and has content
test -f docs/planning/EPIC_4/SPRINT_24/KNOWN_UNKNOWNS.md && echo "EXISTS" || echo "MISSING"
wc -l docs/planning/EPIC_4/SPRINT_24/KNOWN_UNKNOWNS.md
# Should have ≥ 20 unknowns
grep -c "^### KU-" docs/planning/EPIC_4/SPRINT_24/KNOWN_UNKNOWNS.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_24/KNOWN_UNKNOWNS.md` with 26 unknowns across 5 categories
- Task-to-Unknown mapping table (Appendix A)
- Verification deadline assignments

### Acceptance Criteria

- [x] ≥ 20 unknowns documented (26 created)
- [x] All 4 priority areas have at least 3 unknowns each (8, 5, 5, 3)
- [x] Sprint 23 carryforward KUs mapped to Sprint 24 numbers (KU-22, KU-23, KU-24)
- [x] Verification deadlines assigned (Day 0-1 for Critical, Day 2-3 for High)

---

## Task 2: Analyze Alias Differentiation Root Causes (#1111 Family)

**Status:** :white_check_mark: COMPLETE
**Priority:** Critical
**Estimated Time:** 4-5 hours
**Deadline:** Before Sprint 24 Day 1
**Owner:** Sprint planning
**Dependencies:** Task 1 (KU list informs risk areas to investigate)
**Unknowns Verified:** KU-01, KU-02, KU-03, KU-04, KU-07, KU-08

### Objective

Classify all 12 alias-differentiation issues by root cause pattern to determine whether a single architectural fix addresses most/all, or if multiple distinct fixes are needed. This analysis directly informs the design in Task 3.

### Why This Matters

Alias differentiation is Sprint 24's Priority 1 and the single highest-leverage workstream. The 12 issues (#1137-#1147, #1150) may share a common root cause in `_diff_varref`/`_partial_collapse_sum`, or they may represent 3-4 distinct patterns requiring different fixes. Understanding the root cause distribution determines the sprint's architectural approach and effort allocation.

### Background

- Sprint 23 alias-aware differentiation: PRs #1135/#1136 (implementation)
- Design document: `docs/planning/EPIC_4/SPRINT_23/DESIGN_ALIAS_DIFFERENTIATION.md`
- Key source files: `src/ad/derivative_rules.py`, `src/kkt/stationarity.py`
- 12 open issues: #1137 (qabel/abel), #1138 (CGE models), #1139 (meanvar), #1140 (PS-family), #1141 (kand), #1142 (launch), #1143 (polygon), #1144 (catmix), #1145 (cclinpts), #1146 (himmel16), #1147 (camshape), #1150 (AD regression)

### What Needs to Be Done

1. **For each of the 12 issues, reproduce the gradient mismatch:**
   - Translate the model: `python -m src.cli data/gamslib/raw/{model}.gms -o /tmp/{model}_mcp.gms --skip-convexity-check`
   - Compare generated stationarity equations against expected KKT conditions
   - Classify the root cause pattern (summation-context, alias-mapping, offset-alias, condition-scope, etc.)

2. **Identify common root cause patterns:**
   - Pattern A: Summation index not tracked through derivative chain (e.g., `sum(j, f(x(i,j)))` differentiating w.r.t. `x(i,j)` loses the `j` dependency)
   - Pattern B: Alias-to-root-set mapping fails in Jacobian construction
   - Pattern C: Offset + alias interaction (e.g., `x(i+1)` with alias `j` for `i`)
   - Pattern D: Condition-scope shadowing in dollar conditionals
   - Other patterns as discovered

3. **Create classification table** mapping each issue to its pattern(s)
4. **Estimate fix effort per pattern** (single architectural change vs. per-model fix)
5. **Identify regression risk** — which currently-matching models use aliases?

### Changes

- Created `docs/planning/EPIC_4/SPRINT_24/ANALYSIS_ALIAS_DIFFERENTIATION.md` with per-issue classification
- Updated KNOWN_UNKNOWNS.md with verification results for KU-01 (VERIFIED), KU-02 (PARTIALLY WRONG), KU-03 (VERIFIED), KU-04 (VERIFIED), KU-07 (VERIFIED), KU-08 (VERIFIED)

### Result

5 root cause patterns identified across 12 issues:
- **Pattern A (summation index):** 6 issues (#1137-#1140, #1145, #1150), ~14 models — main architectural fix
- **Pattern B (root-set mapping):** 1 issue (kand) — post-investigation
- **Pattern C (offset-alias):** 2 issues (polygon, himmel16) — included in main fix, high risk
- **Pattern D (condition-scope):** 1 issue (launch) — post-investigation
- **Pattern E (non-differentiation):** 2 issues (catmix, camshape) — separate PRs

Main fix (Patterns A-C): 8-10h. Regression risk: VERY LOW (<2%, 8 of 49 matching use aliases).

### Verification

```bash
# Verify analysis document exists
test -f docs/planning/EPIC_4/SPRINT_24/ANALYSIS_ALIAS_DIFFERENTIATION.md && echo "EXISTS" || echo "MISSING"
# Should classify all 12 issues
grep -c "^| #11" docs/planning/EPIC_4/SPRINT_24/ANALYSIS_ALIAS_DIFFERENTIATION.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_24/ANALYSIS_ALIAS_DIFFERENTIATION.md` with per-issue root cause classification
- Pattern distribution table (how many issues per pattern)
- Regression risk assessment for currently-matching models
- Effort estimate per pattern
- Updated KNOWN_UNKNOWNS.md with verification results for KU-01, KU-02, KU-03, KU-04, KU-07, KU-08

### Acceptance Criteria

- [x] All 12 alias-differentiation issues classified by root cause
- [x] Common patterns identified and named (5 patterns: A-E)
- [x] Regression risk for 49 currently-matching models assessed (8 use aliases, very low risk)
- [x] Fix effort estimated per pattern (8-10h main, +4h post-investigation)
- [x] Analysis informs Task 3 design
- [x] KU-01, KU-02, KU-03, KU-04, KU-07, KU-08 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 3: Design Alias Differentiation Architecture

**Status:** :white_check_mark: COMPLETE
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 24 Day 1
**Owner:** Sprint planning
**Dependencies:** Task 2 (root cause analysis informs architecture)
**Unknowns to Verify:** KU-03, KU-05, KU-06, KU-26

### Objective

Design the architectural changes to `_diff_varref`, `_partial_collapse_sum`, and related AD functions needed to fix alias-aware differentiation. Produce a design document with file-level change specifications, regression test plan, and rollout strategy.

### Why This Matters

Alias differentiation is a significant AD architectural change that affects derivative computation for all indexed models. A design-first approach (established in Sprint 20 for IndexOffset) prevents costly mid-sprint rewrites. The design must balance correctness (fixing 12+ issues) with safety (no regressions in 49 matching models).

### Background

- Sprint 23 design: `docs/planning/EPIC_4/SPRINT_23/DESIGN_ALIAS_DIFFERENTIATION.md`
- Sprint 23 implementation: PRs #1135/#1136
- Key source files: `src/ad/derivative_rules.py` (`_diff_varref`, `_diff_sum`, `_partial_collapse_sum`), `src/kkt/stationarity.py` (`_replace_indices_in_expr`, `_add_indexed_jacobian_terms`)
- Task 2 root cause classification provides the pattern inventory

### What Needs to Be Done

1. **Review Sprint 23 design document** — what was implemented, what was deferred
2. **For each root cause pattern from Task 2:**
   - Design the minimal code change needed
   - Identify which functions are affected
   - Design regression guards (how to detect unintended changes)
3. **Design summation-context threading:**
   - How `_diff_varref` receives and uses summation context
   - How `_partial_collapse_sum` preserves or transforms context
   - How the context flows through the full derivative chain
4. **Design regression test strategy:**
   - Golden-file comparison for all 49 matching models
   - Per-issue regression tests for each of the 12 fixes
   - Canary models that exercise alias paths without being in the #1111 family
5. **Document rollout strategy:** incremental (one pattern at a time) vs. big-bang
6. **Create design document** with code-level specifications

### Changes

- Created `docs/planning/EPIC_4/SPRINT_24/DESIGN_ALIAS_DIFFERENTIATION_V2.md` with architecture status, per-pattern design, regression test plan, and incremental rollout strategy
- Updated KNOWN_UNKNOWNS.md with verification results for KU-05 (PARTIALLY VERIFIED), KU-06 (VERIFIED), KU-26 (VERIFIED)

### Result

**Key Discovery:** The core alias differentiation architecture is **already fully implemented** (Sprint 23 PRs #1135/#1136). `bound_indices`, `_alias_match()`, `_same_root_set()` are all wired through the derivative chain. Sprint 24's work is debugging edge cases in the existing implementation, not building new architecture. Estimated effort: 11-17h (within 14-18h budget).

Incremental rollout recommended: Phase 1 debug Pattern A (Days 1-3) → Phase 2 validate (Days 3-5) → Phase 3 Pattern C offset-alias (Days 5-7) → Phase 4 investigate B/D (Days 7-9).

### Verification

```bash
# Verify design document exists
test -f docs/planning/EPIC_4/SPRINT_24/DESIGN_ALIAS_DIFFERENTIATION_V2.md && echo "EXISTS" || echo "MISSING"
wc -l docs/planning/EPIC_4/SPRINT_24/DESIGN_ALIAS_DIFFERENTIATION_V2.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_24/DESIGN_ALIAS_DIFFERENTIATION_V2.md` with:
  - Architecture status (already implemented vs. needs extension)
  - Per-pattern investigation/fix strategy
  - Regression test plan (canary + golden-file + full pipeline)
  - Incremental rollout strategy with decision criteria
- File-level change inventory (2 files: derivative_rules.py, stationarity.py)
- Updated KNOWN_UNKNOWNS.md with verification results for KU-03, KU-05, KU-06, KU-26

### Acceptance Criteria

- [x] Design covers all root cause patterns from Task 2 (A-E addressed)
- [x] Summation-context threading specified at function level (already implemented)
- [x] Regression test plan covers all 49 matching models (canary + golden-file + pipeline)
- [x] Rollout strategy defined with decision criteria (4-phase incremental)
- [x] Design reviewed against Sprint 23 implementation (found already complete)
- [x] KU-03 (verified), KU-05 (partially verified — runtime pending), KU-06 (verified), KU-26 (verified) updated in KNOWN_UNKNOWNS.md

---

## Task 4: Triage path_syntax_error Models (24)

**Status:** :white_check_mark: COMPLETE
**Priority:** High
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 24 Day 1
**Owner:** Sprint planning
**Dependencies:** Task 1 (KU list informs risk areas)
**Unknowns to Verify:** KU-09, KU-10, KU-11, KU-12, KU-13, KU-22, KU-23

### Objective

Classify all 24 path_syntax_error models by error subcategory and estimate fix effort. Identify which models are highest-leverage (shared root cause, overlap with alias differentiation, etc.).

### Why This Matters

path_syntax_error rose from 18 in the Sprint 23 baseline to 24 in the Sprint 24 prep baseline retest, driven by translate-related influx. 11 new models entered this category (from translate recovery/pipeline changes). Understanding the subcategory distribution is essential for targeting the ≤ 15 goal — we need to fix at least 9 models. Some may be fixed automatically by alias differentiation (Priority 1), reducing the dedicated effort needed.

### Background

- Sprint 24 prep baseline retest: 24 path_syntax_error models (up from 18 in Sprint 23 baseline)
- Sprint 22 triage: `docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SYNTAX_ERROR_GB.md` (subcategories G+B)
- Sprint 23 fixed: nonsharp (#956), danwolfe (#1182), fawley (#1133), but 11 new influx
- Known subcategories from Sprint 22: A (uncontrolled set), B (domain violations), C (gradient conditions), G (set index reuse)

### What Needs to Be Done

1. **Run pipeline on all 24 path_syntax_error models** to capture current error messages:
   ```bash
   for model in <list>; do
     python -m src.cli data/gamslib/raw/${model}.gms -o /tmp/${model}_mcp.gms --skip-convexity-check
     (cd /tmp && gams ${model}_mcp.gms lo=2 2>&1) | grep -F '$' | head -5
   done
   ```
2. **Classify each model by error subcategory** (A/B/C/G/new)
3. **Identify the influx models** and determine if they share patterns with existing errors
4. **Estimate fix effort per subcategory** and per model
5. **Identify models that alias differentiation (Priority 1) may fix automatically**
6. **Prioritize: which 8+ models to fix for the ≤ 15 target**
7. **Create triage document**

### Changes

- Created `docs/planning/EPIC_4/SPRINT_24/TRIAGE_PATH_SYNTAX_ERROR.md` with 24-model classification
- Updated KNOWN_UNKNOWNS.md: KU-09 (WRONG), KU-10 (VERIFIED), KU-11 (VERIFIED), KU-12 (VERIFIED), KU-13 (still INCOMPLETE), KU-22 (VERIFIED), KU-23 (VERIFIED)

### Result

24 models classified into 7 subcategories (up from 20 in Sprint 23). New subcategory H (concrete element offsets) is the dominant new pattern with 8 models — all use aliases. 18 of 24 models (75%) use aliases. Priority fix: subcategory H batch fix (4-6h) + 2-3 subcategory A models → ≤ 15 target achievable.

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_24/TRIAGE_PATH_SYNTAX_ERROR.md && echo "EXISTS" || echo "MISSING"
# Count model rows in alias overlap table (should be 24)
grep -c "^| [a-z]" docs/planning/EPIC_4/SPRINT_24/TRIAGE_PATH_SYNTAX_ERROR.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_24/TRIAGE_PATH_SYNTAX_ERROR.md` with per-model classification
- Subcategory distribution table (7 subcategories)
- Fix priority ranking (Tier 1: H batch fix, Tier 2: A quick fixes, Tier 3: other)
- Alias overlap analysis (18/24 = 75%)
- Updated KNOWN_UNKNOWNS.md with verification results for KU-09–KU-13, KU-22, KU-23

### Acceptance Criteria

- [x] All 24 path_syntax_error models classified by subcategory
- [x] 11 influx models identified and classified (up from expected 5)
- [x] Fix effort estimated per subcategory
- [x] Overlap with alias differentiation documented (75% use aliases)
- [x] Priority ranking for ≤ 15 target (H batch fix + 2-3 A models)
- [x] KU-09–KU-13, KU-22, KU-23 verified and updated in KNOWN_UNKNOWNS.md (KU-13 deferred to implementation)

---

## Task 5: Triage model_infeasible Models (14)

**Status:** :white_check_mark: COMPLETE
**Priority:** High
**Estimated Time:** 2-3 hours
**Deadline:** Before Sprint 24 Day 1
**Owner:** Sprint planning
**Dependencies:** Task 1 (KU list informs risk areas)
**Unknowns to Verify:** KU-14, KU-15, KU-16, KU-17, KU-18

### Objective

Update the model_infeasible classification from Sprint 23, incorporating new discoveries (#1177 chenery, #1195 sambal, #1192 gtm, #1199 bearing). Identify which models are fixable vs. inherent limitations, and which overlap with alias differentiation.

### Why This Matters

model_infeasible rose from 12 to 14 in the Sprint 24 prep baseline retest (6 fixed, 8 new influx). The ≤ 8 target requires fixing or excluding at least 6 models. Several models (chenery, cesam, korcge) have alias-related Jacobian issues that may overlap with alias differentiation fixes.

### Background

- Sprint 23 triage: `docs/planning/EPIC_4/SPRINT_23/TRIAGE_MODEL_INFEASIBLE.md`
- Sprint 23 accounting: 1 gross fix (mine), 0 gross influx, net -1
- New issues from Sprint 23: #1199 (bearing), #1177 (chenery), #1195 (sambal), #1192 (gtm)
- Sprint 23 KNOWN_UNKNOWNS KU-27 through KU-32 relevant

### What Needs to Be Done

1. **Update model list** — confirm current 14 infeasible models
2. **For each model, classify root cause:**
   - KKT formulation bug (fixable)
   - Jacobian accuracy (may overlap with alias differentiation)
   - Inherent MCP incompatibility (not fixable)
   - Missing feature (deferred)
3. **For new models (agreste, cesam, chenery, feasopt1, iobalance, korcge, orani, rocket), perform root cause analysis**
4. **Identify overlap with alias differentiation** — which models improve when derivatives are more accurate?
5. **Prioritize: which 6+ models to fix/exclude for ≤ 8 goal**
6. **Track gross fixes/influx budget** per PR7

### Changes

- Created `docs/planning/EPIC_4/SPRINT_24/TRIAGE_MODEL_INFEASIBLE.md` with 14-model classification
- Updated KNOWN_UNKNOWNS.md: KU-14 (VERIFIED), KU-15 (VERIFIED), KU-16 (VERIFIED), KU-17 (INCOMPLETE — deferred), KU-18 (VERIFIED)

### Result

14 models classified (up from 12 in Sprint 23): 6 Category A (KKT bugs), 5 Category B (PATH convergence), 3 Category C (structural incompatibility). 8/14 (57%) use aliases; 4 have HIGH alias-fix potential. Target ≤ 8 achievable via: exclude 3 Category C + fix 3 alias-related Category A = 14 - 6 = 8.

Gross fixes/influx: 6 Sprint 23 models fixed, 8 new models entered (net +2).

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_24/TRIAGE_MODEL_INFEASIBLE.md && echo "EXISTS" || echo "MISSING"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_24/TRIAGE_MODEL_INFEASIBLE.md` with per-model classification
- Root cause analysis for 8 new models (not just 4 — composition changed)
- Alias overlap analysis (4 HIGH, 1 MEDIUM, 2 LOW, 1 NONE among alias-using)
- Priority ranking (Tier 1: exclude 3, Tier 2: fix 3 alias A, Tier 3: fix 3 lead/lag A)
- Gross fixes/influx budget per PR7
- Updated KNOWN_UNKNOWNS.md with verification results for KU-14–KU-18

### Acceptance Criteria

- [x] All 14 model_infeasible models classified (up from expected 11)
- [x] New models root-caused (8 new, not 4 — composition changed significantly)
- [x] Overlap with alias differentiation documented (4 HIGH potential)
- [x] At least 3 models identified as fixable targets (6 Category A fixable + 3 excludable)
- [x] KU-14–KU-18 verified and updated in KNOWN_UNKNOWNS.md (KU-17 deferred to implementation)

---

## Task 6: Investigate Translation Timeouts (6 models + 1 internal error)

**Status:** :white_check_mark: COMPLETE
**Priority:** Medium
**Estimated Time:** 2-3 hours
**Deadline:** Before Sprint 24 Day 1
**Owner:** Sprint planning
**Dependencies:** None
**Unknowns to Verify:** KU-19, KU-20, KU-21

### Objective

Analyze the 6 remaining translation timeout models to determine if they are fixable within Sprint 24 or require algorithmic improvements to the stationarity builder.

### Why This Matters

Sprint 23 recovered 7 timeout models via the LP fast path, but 6 remain. Fixing even 2-3 would push translate from 95.2% toward the 97% target (140/147 → 143/147). Understanding whether the bottleneck is model size, recursion depth, or specific patterns determines the fix approach.

### Background

- Sprint 23 LP fast path: PR #1172 (recovered 7 models)
- Remaining timeouts: 6 models (including lop #1169, mexls #1185)
- Pipeline timeout: 300s
- Sprint 23 KNOWN_UNKNOWNS KU-31 (LP fast path limitations)
- 1 internal_error model also exists

### What Needs to Be Done

1. **List all 6 timeout models** from `gamslib_status.json`
2. **For each model, profile the translation:**
   - Model size (equations, variables, constraints)
   - Time to parse vs. time to translate
   - Where the bottleneck is (stationarity builder, emitter, AD)
3. **Classify by bottleneck pattern:**
   - Large model (too many Jacobian entries)
   - Deep recursion (nested expressions)
   - Specific grammar pattern (e.g., multi-solve, large tables)
4. **Estimate feasibility of optimization** per model
5. **Investigate the 1 internal_error model** — root cause and fix

### Changes

- Created `docs/planning/EPIC_4/SPRINT_24/INVESTIGATION_TRANSLATE_TIMEOUTS.md` with 7-model analysis
- Updated KNOWN_UNKNOWNS.md: KU-19 (PARTIALLY WRONG), KU-20 (INCOMPLETE — needs profiling), KU-21 (VERIFIED)

### Result

6 timeout models profiled: bottleneck is in the translation phase (normalize/KKT assembly for most; ScenRed library expansion for srpchase; MINLP type for gastrans). srpchase (107 lines) and iswnm (691 lines) are tiny models that should not timeout — specific translation patterns (ScenRed library, complex index interactions) are the cause. 2 models feasible to investigate (iswnm, sarf); 3 unlikely fixable without algorithmic changes; 1 MINLP out of scope.

1 internal error (mine): SetMembershipTest domain mismatch — fixable in 2-3h.

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_24/INVESTIGATION_TRANSLATE_TIMEOUTS.md && echo "EXISTS" || echo "MISSING"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_24/INVESTIGATION_TRANSLATE_TIMEOUTS.md` with per-model analysis
- Bottleneck classification table (6 timeout + 1 internal error)
- Feasibility assessment (2 investigate, 3 unlikely, 1 out of scope, 1 fixable)
- Updated KNOWN_UNKNOWNS.md with verification results for KU-19, KU-20, KU-21

### Acceptance Criteria

- [x] All 6 timeout models profiled (size, solve type, aliases, bottleneck)
- [x] Bottleneck classified per model (normalize/KKT for most; ScenRed for srpchase; MINLP for gastrans)
- [x] Internal error model root-caused (mine: SetMembershipTest domain mismatch)
- [x] Feasibility of optimization estimated per model
- [x] KU-19, KU-20, KU-21 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 7: Run Full Pipeline Baseline (per PR6)

**Status:** :white_check_mark: COMPLETE
**Priority:** Critical
**Estimated Time:** 1-2 hours
**Deadline:** Before Sprint 24 Day 1
**Owner:** Sprint planning
**Dependencies:** None
**Unknowns to Verify:** KU-25

### Objective

Run the full pipeline to establish definitive Sprint 24 baseline metrics, following Sprint 23 process recommendation PR6 (full pipeline for all definitive metrics).

### Why This Matters

The Sprint 23 Day 13 final retest provides baseline numbers, but code may have changed since (prep task fixes, merged PRs). A fresh baseline ensures Sprint 24 metrics are measured from the correct starting point. Per PR9, targets are against the 147-model pipeline scope.

### Background

- Sprint 23 final: parse 147/147, translate 140/147, solve 86/140, match 49/147
- Pipeline script: `scripts/gamslib/run_full_test.py`
- Status file: `data/gamslib/gamslib_status.json`
- Process: PR6 (full pipeline), PR8 (absolute counts + percentages)

### What Needs to Be Done

1. **Run full pipeline:** `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
2. **Record all metrics** with absolute counts and percentages
3. **Compare to Sprint 23 final** — identify any changes
4. **Commit updated `gamslib_status.json`**
5. **Create baseline document** with metrics table

### Changes

- Created `docs/planning/EPIC_4/SPRINT_24/BASELINE_METRICS.md` with full pipeline metrics
- Updated `data/gamslib/gamslib_status.json` with fresh pipeline run
- Updated KNOWN_UNKNOWNS.md: KU-25 (WRONG — actual influx 58%, not 40%)

### Result

Baseline identical to Sprint 23 Day 13 final — no code changes between sprints. Parse 147/147 (100%), translate 140/147 (95.2%), solve 86/140 (61.4%), match 49/147 (33.3%). Error influx rate from Sprint 23 was 58.3% (7/12), higher than PR10's ~40% estimate. Sprint 24 should budget 50-60%.

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_24/BASELINE_METRICS.md && echo "EXISTS" || echo "MISSING"
git diff --stat data/gamslib/gamslib_status.json | head -3
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_24/BASELINE_METRICS.md` with full pipeline metrics and target gaps
- Updated `data/gamslib/gamslib_status.json`
- Comparison to Sprint 23 final (identical — 0 deltas)
- Error influx rate analysis (58.3% actual vs 40% PR10 estimate)
- Updated KNOWN_UNKNOWNS.md with verification results for KU-25

### Acceptance Criteria

- [x] Full pipeline run completed (4641s, 147 models)
- [x] All metrics recorded (parse, translate, solve, match, error categories)
- [x] Absolute counts and percentages included (PR8)
- [x] Comparison to Sprint 23 final documented (identical)
- [x] gamslib_status.json committed
- [x] KU-25 verified and updated in KNOWN_UNKNOWNS.md (WRONG — 58% not 40%)

---

## Task 8: Review Sprint 23 Retrospective Action Items

**Status:** :large_blue_circle: NOT STARTED
**Priority:** High
**Estimated Time:** 1 hour
**Deadline:** Before Sprint 24 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1-7 (review after all research/analysis is complete)
**Unknowns to Verify:** (validates PR9/PR10/PR11 compliance — cross-cutting process check)

### Objective

Verify that all Sprint 23 retrospective action items, process recommendations (PR9-PR11), and deferred items are addressed in the Sprint 24 prep plan and schedule.

### Why This Matters

Sprint 23's retrospective identified 5 improvement areas and 3 new process recommendations. Ensuring these are incorporated prevents repeating the same mistakes (e.g., not budgeting for error influx, setting targets against wrong scope).

### Background

- Sprint 23 Retrospective: `docs/planning/EPIC_4/SPRINT_23/SPRINT_RETROSPECTIVE.md`
- Process recommendations: PR9 (pipeline scope targets), PR10 (error influx budget), PR11 (prioritize highest-leverage fix)
- What Could Be Improved: 5 items
- What We'd Do Differently: 4 items
- Sprint 24 Recommendations: 5 priorities with suggested targets

### What Needs to Be Done

1. **Review each "What Could Be Improved" item** — verify it's addressed in Sprint 24 prep/plan
2. **Review each "What We'd Do Differently" item** — verify changes are incorporated
3. **Verify PR9 compliance** — targets set against 147-model scope
4. **Verify PR10 compliance** — error influx budget calculated
5. **Verify PR11 compliance** — alias differentiation is Days 1-5 priority
6. **Check all deferred items** from Sprint 23 KNOWN_UNKNOWNS (KU-28, KU-29, KU-32)
7. **Document any gaps** and adjust Sprint 24 plan accordingly

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify retrospective alignment document exists
test -f docs/planning/EPIC_4/SPRINT_24/RETROSPECTIVE_ALIGNMENT.md && echo "EXISTS" || echo "MISSING"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_24/RETROSPECTIVE_ALIGNMENT.md` with item-by-item review
- Gap analysis (if any items not addressed)
- Confirmation that PR9/PR10/PR11 are incorporated

### Acceptance Criteria

- [ ] All 5 "What Could Be Improved" items reviewed
- [ ] All 4 "What We'd Do Differently" items reviewed
- [ ] PR9/PR10/PR11 compliance verified
- [ ] Sprint 23 deferred KUs addressed
- [ ] No critical gaps identified (or gaps documented with mitigation)

---

## Task 9: Plan Sprint 24 Detailed Schedule

**Status:** :large_blue_circle: NOT STARTED
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 24 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1-8 (all prep research must be complete)
**Unknowns to Verify:** (integrates all verified unknowns into schedule)

### Objective

Create the Sprint 24 detailed schedule (Day 0-14) with daily task assignments, checkpoints, and contingency plans. Integrate findings from all prep tasks into an executable plan.

### Why This Matters

Sprint 23's structured 15-day schedule with 2 checkpoints and day-by-day prompts proved effective. Sprint 24 must replicate this structure while incorporating the new process recommendations (PR9-PR11) and the alias differentiation design-first approach.

### Background

- Sprint 23 plan: `docs/planning/EPIC_4/SPRINT_23/PLAN.md` (15-day schedule, 2 checkpoints)
- Sprint 23 prompts: `docs/planning/EPIC_4/SPRINT_23/prompts/PLAN_PROMPTS.md`
- PROJECT_PLAN.md Sprint 24 section (lines 744-829)
- All prep task outputs (Tasks 1-8)

### What Needs to Be Done

1. **Define workstreams** based on prep task findings:
   - WS1: Alias differentiation (Priority 1, Days 1-7)
   - WS2: path_syntax_error fixes (Priority 2, Days 5-9)
   - WS3: model_infeasible fixes (Priority 3, Days 7-10)
   - WS4: Translation timeout (Priority 4, Days 8-10)
   - WS5: Pipeline retest and sprint close (Days 11-14)
2. **Assign daily tasks** for all 15 days
3. **Define 2 checkpoints:**
   - Checkpoint 1 (Day 5): Alias differentiation progress, regression check
   - Checkpoint 2 (Day 10): Error category progress, GO/NO-GO for close
4. **Define GO/NO-GO criteria** at each checkpoint
5. **Create contingency plans** for common risks (alias diff regression, error influx, etc.)
6. **Budget error influx** per PR10 (~40% of newly-translating models → solve errors)
7. **Create day-by-day execution prompts**
8. **Initialize SPRINT_LOG.md**

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify plan and prompts exist
test -f docs/planning/EPIC_4/SPRINT_24/PLAN.md && echo "EXISTS" || echo "MISSING"
test -f docs/planning/EPIC_4/SPRINT_24/prompts/PLAN_PROMPTS.md && echo "EXISTS" || echo "MISSING"
test -f docs/planning/EPIC_4/SPRINT_24/SPRINT_LOG.md && echo "EXISTS" || echo "MISSING"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_24/PLAN.md` — 15-day detailed schedule
- `docs/planning/EPIC_4/SPRINT_24/prompts/PLAN_PROMPTS.md` — day-by-day execution prompts
- `docs/planning/EPIC_4/SPRINT_24/SPRINT_LOG.md` — initialized sprint log
- Checkpoint criteria and contingency plans

### Acceptance Criteria

- [ ] 15-day schedule with daily task assignments
- [ ] 2 checkpoints with GO/NO-GO criteria defined
- [ ] Contingency plans for top 3 risks
- [ ] Error influx budget calculated per PR10
- [ ] Day-by-day execution prompts created
- [ ] SPRINT_LOG.md initialized with targets and baseline
- [ ] All prep task findings integrated

---

## Summary

### Success Criteria

Sprint 24 prep is complete when:
1. All 9 tasks are complete with deliverables created
2. Alias differentiation root causes classified and architecture designed
3. Error category triage complete for all 3 priority areas
4. Full pipeline baseline established
5. Sprint 23 retrospective action items verified
6. 15-day detailed schedule created with checkpoints and prompts

### Risk Areas Requiring Attention

1. **Alias differentiation complexity** — Task 2 may reveal that the 12 issues have 4+ distinct patterns, making a single sprint fix infeasible
2. **Error influx from alias differentiation** — Fixing derivatives may change equation output, potentially breaking currently-matching models
3. **path_syntax_error overlap** — Some path_syntax_error models may be fixed by alias differentiation, reducing dedicated effort needed (positive risk)
4. **Translation timeout intractability** — Some models may be fundamentally too large for symbolic differentiation within any reasonable timeout

---

## Appendix: Document Cross-References

### Sprint Goals
- `docs/planning/EPIC_4/PROJECT_PLAN.md` — Sprint 24 section (lines 744-829)

### Prior Sprint Documents
- `docs/planning/EPIC_4/SPRINT_23/SPRINT_RETROSPECTIVE.md` — Sprint 24 recommendations
- `docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md` — 32 KUs (carryforward items)
- `docs/planning/EPIC_4/SPRINT_23/SPRINT_LOG.md` — Final metrics
- `docs/planning/EPIC_4/SPRINT_23/DESIGN_ALIAS_DIFFERENTIATION.md` — Sprint 23 partial design
- `docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SYNTAX_ERROR_GB.md` — Subcategories G+B triage
- `docs/planning/EPIC_4/SPRINT_23/TRIAGE_MODEL_INFEASIBLE.md` — Infeasibility classification

### Research Documents
- `docs/research/minmax_objective_reformulation.md` — Solution forcing strategies
- `docs/research/nested_subset_indexing_research.md` — Index handling research

### Epic Goals
- `docs/planning/EPIC_4/GOALS.md` — Full GAMSLIB LP/NLP/QCP Coverage

### GitHub Issues
- 20 issues labeled `sprint-24`: #1137-#1147, #1150, #1169, #1177-#1179, #1185, #1192, #1195, #1199
