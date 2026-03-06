# Sprint 22 Preparation Plan

**Purpose:** Complete preparation tasks for Sprint 22 (Solve Improvements & Solution Matching) before Day 1 begins
**Timeline:** Complete before Sprint 22 Day 1
**Goal:** Address Sprint 21 findings, catalog solve-failure root causes, and prepare for systematic path_syntax_error and path_solve_terminated fixes

**Key Insight from Sprint 21:** PATH convergence analysis (Day 12) revealed that **none** of the 29 path_solve_terminated models had actual PATH convergence issues. All fail before PATH runs (compilation, execution, MCP pairing errors) or are locally infeasible. This redirects Sprint 22 focus from PATH solver tuning toward MCP formulation correctness and emitter fixes.

---

## Executive Summary

Sprint 21 achieved 154/157 parse (98.1%), 65 solve, 30 match — far exceeding all targets. Sprint 22 shifts focus from parse improvements to **solve rate improvement**. The two largest solve failure categories are:

1. **path_syntax_error (43 models):** Emitter and translator bugs produce invalid GAMS MCP code
2. **path_solve_terminated (12 models):** Pre-solver errors (execution, compilation, MCP pairing) prevent PATH from running

Additionally:
- **model_infeasible (15 models):** May contain KKT formulation bugs vs genuine MCP incompatibility
- **Translation failures (17 models):** 11 timeouts + 6 internal_errors block models before solve stage
- **Deferred issues (#764, #765, #827, #830):** Architectural work deferred from Sprint 21

This prep plan focuses on research, root cause cataloging, and design tasks that must complete before Sprint 22 implementation begins.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|----------------------|
| 1 | Create Sprint 22 Known Unknowns List | Critical | 2h | None | Risk identification |
| 2 | Catalog path_syntax_error Remaining Subcategories | Critical | 3h | None | path_syntax_error ≤ 30 |
| 3 | Classify path_solve_terminated Root Causes | Critical | 3h | None | Solve ≥ 75 |
| 4 | Triage model_infeasible Models | High | 3h | None | model_infeasible ≤ 12 |
| 5 | Profile Translation Timeout Bottlenecks | High | 2h | None | Translation improvement |
| 6 | Survey Deferred Issues for Sprint 22 Fit | High | 2h | Tasks 2-4 | Deferred issue planning |
| 7 | Design path_syntax_error Fix Strategy | High | 2h | Task 2 | path_syntax_error ≤ 30 |
| 8 | Establish Sprint 22 Baseline Metrics | High | 1h | None | Metrics tracking |
| 9 | Assess Match Rate Improvement Opportunities | Medium | 2h | Task 3 | Match ≥ 35 |
| 10 | Plan Sprint 22 Detailed Schedule | Critical | 3h | All tasks | Sprint planning |

**Total Estimated Time:** ~23 hours (~3 working days)

**Critical Path:** Tasks 1 → 2 → 7 → 10 (must complete before Sprint 22 Day 1)

---

## Task 1: Create Sprint 22 Known Unknowns List

**Status:** :white_check_mark: COMPLETE
**Priority:** Critical
**Estimated Time:** 2 hours
**Deadline:** Before Sprint 22 Day 1
**Owner:** Sprint planning
**Dependencies:** None

### Objective

Create proactive list of assumptions and unknowns for Sprint 22 to prevent late discoveries during implementation.

### Why This Matters

Sprint 21 Retrospective highlighted that proactive investigation (e.g., Day 12 PATH convergence analysis) prevented wasted effort on incorrect assumptions. Sprint 22's solve-focused work involves complex KKT formulation issues where wrong assumptions can cost days of debugging.

### Background

Sprint 22 shifts from parse improvements to solve improvements. Key areas of uncertainty:
- path_syntax_error fixes may have cascading effects on other error categories
- model_infeasible root causes are not yet classified (KKT bug vs genuine incompatibility)
- Translation timeout optimization may require grammar/parser changes
- Deferred issues (#764, #765, #827, #830) have complex architectural implications

**Reference:** Sprint 21 PATH_CONVERGENCE_ANALYSIS.md found that ALL path_solve_terminated failures are pre-solver errors, not convergence issues. This invalidates the original PROJECT_PLAN.md assumption about "PATH solver tuning."

### What Needs to Be Done

1. **Review Sprint 22 scope** from `docs/planning/EPIC_4/PROJECT_PLAN.md` (lines 509-625)
2. **Extract unknowns** from each Sprint 22 component:
   - path_syntax_error subcategory fixes: Are the deferred subcategories (C, B, G) isolated fixes or interconnected?
   - path_solve_terminated: Do Category B execution errors require `.l` initialization infrastructure?
   - model_infeasible: What fraction are KKT bugs vs MCP-incompatible model types?
   - Translation timeouts: Is the bottleneck in Lark/Earley parsing, KKT derivation, or GAMS emission?
   - Deferred issues: Are any prerequisites for high-leverage solve fixes?
3. **Categorize by topic** (7 categories: KKT correctness, starting point, PATH solver, MCP-NLP divergence, parse completion, deferred path_syntax_error subcategories, Sprint 21 deferred items)
4. **Prioritize by risk** (Critical/High/Medium/Low)
5. **Define verification method** for each unknown
6. **Create document** at `docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md`

### Changes

- Created `docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md` with 26 unknowns across 7 categories
- Each unknown includes: Priority, Assumption, Research Questions, How to Verify, Risk if Wrong, Estimated Research Time, Owner, Verification Results
- Task-to-Unknown mapping table (Appendix A) links each prep task to its unknowns
- KU-08 (PATH tuning irrelevant) verified immediately from existing Day 12 analysis

### Result

26 unknowns identified across 7 categories:
- Category 1: KKT Correctness Fixes (5 unknowns: KU-01 through KU-04, KU-24)
- Category 2: Starting Point Improvements (4 unknowns: KU-05 through KU-07, KU-25)
- Category 3: PATH Solver Tuning (3 unknowns: KU-08 through KU-10)
- Category 4: MCP-NLP Solution Divergence Analysis (4 unknowns: KU-11 through KU-13, KU-26)
- Category 5: Parse Completion Final Push (2 unknowns: KU-14, KU-15)
- Category 6: Deferred path_syntax_error Subcategories (4 unknowns: KU-16 through KU-19)
- Category 7: Sprint 21 Deferred Items (4 unknowns: KU-20 through KU-23)

Priority distribution: 4 Critical, 9 High, 9 Medium, 4 Low (as defined in KNOWN_UNKNOWNS.md Appendix B). All Critical/High unknowns have verification deadlines ≤ Day 3.

### Verification

```bash
# Verify document exists with expected structure
test -f docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md && echo "EXISTS" || echo "MISSING"
grep -c "^### KU-" docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md
# Expected: 26 unknowns
```

### Deliverables

- [x] `docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md` with 26 unknowns across 7 categories
- [x] Each unknown has: assumption, verification method, priority, risk if wrong
- [x] Verification deadlines assigned (Day 0/1/2/3)

### Acceptance Criteria

- [x] Document created with 26 unknowns across 7 categories
- [x] All unknowns have assumption, verification method, priority
- [x] All Critical/High unknowns have verification plan
- [x] Unknowns cover all Sprint 22 components
- [x] Template for runtime updates defined (Appendix C)
- [x] Verification deadlines assigned

---

## Task 2: Catalog path_syntax_error Remaining Subcategories

**Status:** :white_check_mark: COMPLETE
**Priority:** Critical
**Estimated Time:** 3 hours
**Deadline:** Before Sprint 22 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns to Verify:** KU-01, KU-03, KU-16, KU-17, KU-18, KU-19

### Objective

Update the Sprint 21 path_syntax_error catalog with current status and prepare a prioritized fix plan for Sprint 22.

### Why This Matters

path_syntax_error is the single largest solve failure category (43 models per latest pipeline). Sprint 22 targets reducing this to ≤30 (−13 models). The Sprint 21 catalog classified 45 of the 48 baseline models into 9 subcategories (A-G, I, J — no H), but:
- Sprint 21 fixed subcategories E (set quoting), D (negative exponents), and parts of A (emission ordering)
- Historically, 3 models (dinam, ferts, tricp) entered this category as unsubcategorized during Sprint 21; per Task 2 findings, dinam/ferts have since moved to translate_failure (timeout) and tricp was assigned to new Subcategory K
- Subcategory counts were refreshed in Task 2 against the latest pipeline results

### Background

Sprint 21 PATH_SYNTAX_ERROR_CATALOG.md classified errors into 9 subcategories (A-G, I, J — no H). Sprint 21 WS4 fixed the top-leverage subcategories. The deferred subcategories recommended for Sprint 22 are:

| Subcategory | Root Cause | Sprint 21 Count | Est. Effort |
|-------------|-----------|-----------------|-------------|
| C | Uncontrolled set in stationarity equations | 9 | 3-5h |
| B | Domain violation in emitted parameter data | 5 | 2-3h |
| G | Set index reuse conflict in sum | 2 | 1-2h |
| F | GAMS built-in function name collision | 1 | 1h |
| I | MCP variable not referenced in equations | 1 | 1h |
| J | Equation-variable dimension mismatch | 1 | 1h |

**Source:** `docs/planning/EPIC_4/SPRINT_21/PATH_SYNTAX_ERROR_CATALOG.md`

### What Needs to Be Done

1. **Run latest pipeline** to regenerate `data/gamslib/gamslib_status.json`:
   ```bash
   .venv/bin/python scripts/gamslib/run_full_test.py --quiet
   ```
2. **Extract current `path_syntax_error` model list** from the status JSON:
   ```bash
   .venv/bin/python -c "import json; data=json.load(open('data/gamslib/gamslib_status.json')); [print(m) for m,v in sorted(data.items()) if v.get('solve_status')=='path_syntax_error']"
   ```
3. **Diff against Sprint 21 catalog** to identify:
   - Models that moved OUT of path_syntax_error (now solving or in different category)
   - Models that moved INTO path_syntax_error (newly parsing/translating)
   - Models still in path_syntax_error with same subcategory
4. **Reclassify any unsubcategorized models** (dinam, ferts, tricp, and any new entries)
5. **Update subcategory counts** based on current pipeline state
6. **Prioritize subcategories** for Sprint 22 by leverage (models × effort ratio)
7. **Create updated catalog** at `docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_STATUS.md`

### Changes

- Created `docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_STATUS.md` with full updated catalog
- Classified all 43 current path_syntax_error models into subcategories
- Verified 6 Known Unknowns: KU-01 (confirmed), KU-03 (refuted), KU-16 (non-issue), KU-17 (updated), KU-18 (confirmed), KU-19 (partially refuted)
- Identified 6 model reclassifications from Sprint 21 subcategories
- Discovered 5 models with new error patterns not in Sprint 21 catalog, plus 1 pipeline artifact (feedtray: MCP file missing)

### Result

43 current path_syntax_error models classified (down from 48 in Sprint 21):
- **22 moved OUT**: 13 model_optimal, 3 translate_failure, 3 path_solve_terminated, 2 model_infeasible, 1 path_solve_license
- **17 moved IN**: Newly translating models reaching solve stage
- **26 stayed**: Including 6 reclassified to different subcategories
- **Subcategories D and E fully resolved** by Sprint 21
- **Top 3 subcategories** (A=15, C=10, G=4) account for 29/43 models — fixing these reaches ≤14
- **Sprint 22 target (≤30)** achievable with Subcategory A alone (15 models, 4-6h)

### Verification

```bash
# Verify updated catalog exists
test -f docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_STATUS.md && echo "EXISTS" || echo "MISSING"

# Verify all current path_syntax_error models are classified
# (compare pipeline output against catalog)
```

### Deliverables

- [x] `docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_STATUS.md` with current subcategory breakdown
- [x] All 43 models classified into subcategories
- [x] Prioritized fix order for Sprint 22
- [x] Effort estimates per subcategory

### Acceptance Criteria

- [x] All 43 current path_syntax_error models classified
- [x] Subcategory counts updated from Sprint 21 baseline
- [x] New/moved models identified and subcategorized
- [x] Fix priority order documented with rationale
- [x] Effort estimates provided per subcategory
- [x] Sprint 22 target subcategories identified (A alone exceeds −13 target)

---

## Task 3: Classify path_solve_terminated Root Causes

**Status:** :white_check_mark: COMPLETE
**Priority:** Critical
**Estimated Time:** 3 hours
**Deadline:** Before Sprint 22 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns to Verify:** KU-05, KU-06, KU-09, KU-10, KU-25

### Objective

Map the remaining path_solve_terminated models to actionable fix categories using Sprint 21 PATH_CONVERGENCE_ANALYSIS.md findings.

### Why This Matters

Sprint 22 targets path_solve_terminated ≤ 5. Sprint 21 Day 12 analysis classified all 29 original models into categories A-F. Of the 15 still-failing models (~12 classified as `path_solve_terminated` in the pipeline — Category E overlaps `translate_failure`, Category F may be classified separately), most fail before PATH runs — meaning fixes are in the translator/emitter, not PATH tuning.

### Background

Sprint 21 PATH_CONVERGENCE_ANALYSIS.md (Day 12) classified the original 29 models:

| Category | Description | Original Count | Now Solves | Remaining |
|----------|-----------|---------------|------------|-----------|
| A | Now solves (Sprint 21 fixes) | 14 | 14 | 0 |
| B | Execution error (domain errors) | 5 | ~0 | ~5 |
| C | MCP pairing error | 4 | ~0 | ~4 |
| D | Compilation error (missing data) | 2 | ~0 | ~2 |
| E | Translation timeout | 2 | ~0 | overlaps translate failures |
| F | Locally infeasible (genuine) | 2 | ~0 | ~2 |

**Key finding:** Categories B-D are pre-solver errors fixable in the translator/emitter. Category F may be genuine MCP incompatibility.

**Source:** `docs/planning/EPIC_4/SPRINT_21/PATH_CONVERGENCE_ANALYSIS.md`

### What Needs to Be Done

1. **Get current path_solve_terminated model list** from latest pipeline output
2. **Map each model** to Sprint 21 Category (B/C/D/E/F) using PATH_CONVERGENCE_ANALYSIS.md
3. **For each model, identify specific error:**
   - Category B: What domain error? (`.l = 0`, rPower, division by zero?)
   - Category C: What MCP pairing mismatch? (variable count, equation count?)
   - Category D: What data is missing?
   - Category F: Is this genuinely infeasible or a KKT formulation bug?
4. **Cross-reference with issue documents** in `docs/issues/` (e.g., #983 elec, #984 etamac, #986 lands)
5. **Estimate fix effort per model** and group into Sprint 22 fix batches
6. **Create classification document** at `docs/planning/EPIC_4/SPRINT_22/PATH_SOLVE_TERMINATED_STATUS.md`

### Changes

- Created `docs/planning/EPIC_4/SPRINT_22/PATH_SOLVE_TERMINATED_STATUS.md` with full classification of all 12 models
- Updated `KNOWN_UNKNOWNS.md`: Verified KU-05 (partially refuted), KU-06 (refuted), KU-09 (confirmed/moved), KU-10 (confirmed + expanded), KU-25 (confirmed)
- Updated Appendix C verification tracking for all 5 KUs

### Result

12 current path_solve_terminated models classified into 2 error types:
- **MCP pairing errors (8 models):** etamac, fdesign, hhfair, otpop, pak, pindyck, springchain, trussm — dominant sub-pattern is `_fx_` equation suppression (5 models)
- **Execution errors (4 models):** elec, fawley, lands, tforss — diverse causes (conditional domain loss, `$` dropping, loop-dependent parameters)

Key findings:
- All 12 fail before PATH runs; `option domlim` is ineffective (KU-06 refuted)
- `_fx_` equation suppression (single fix) unblocks 5 models — highest leverage
- Sprint 22 target ≤5 achievable with Priority 1-2 fixes (7 models, 4-5h)
- chain/rocket moved to model_infeasible (KU-09 confirmed)
- Category C expanded from 4 to 8 models (KU-10 expanded)

### Verification

```bash
# Verify classification document exists
test -f docs/planning/EPIC_4/SPRINT_22/PATH_SOLVE_TERMINATED_STATUS.md && echo "EXISTS" || echo "MISSING"

# Verify all 12 models classified
grep -c "^|" docs/planning/EPIC_4/SPRINT_22/PATH_SOLVE_TERMINATED_STATUS.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_22/PATH_SOLVE_TERMINATED_STATUS.md`
- Each of 12 models mapped to fix category with specific error details
- Cross-references to existing issue documents
- Fix effort estimates and Sprint 22 batch plan

### Acceptance Criteria

- [x] All 12 remaining path_solve_terminated models classified
- [x] Each model has specific error identified (not just category)
- [x] Cross-references to existing issue docs where applicable
- [x] Fix effort estimates per model
- [x] Sprint 22 fix batches defined (enough for −7 models)
- [x] Genuine infeasibility cases identified and excluded from fix targets

---

## Task 4: Triage model_infeasible Models

**Status:** :white_check_mark: COMPLETE
**Priority:** High
**Estimated Time:** 3 hours
**Deadline:** Before Sprint 22 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns to Verify:** KU-23, KU-24

### Objective

Classify the 15 model_infeasible models into KKT formulation bugs (fixable) vs genuine MCP incompatibility (not fixable).

### Why This Matters

Sprint 22 targets model_infeasible ≤ 12 (−3 models). But the 15 models haven't been classified — some may be KKT bugs that produce infeasible MCPs, while others may be inherently incompatible model types (like CGE models with exogenous variables). Without classification, Sprint 22 cannot prioritize which infeasible models to investigate.

### Background

model_infeasible grew from 12 to 15 during Sprint 21 as more models reached the solve stage. The Sprint 21 retrospective noted this as an expected consequence but flagged it for investigation. Known patterns include:
- Issue #765 (orani): CGE model type with linearized percentage-change formulation — structurally incompatible with NLP→MCP
- Issue #970 (twocge): MCP locally infeasible — may be KKT formulation issue
- Issue #828 (ibm1): Stationarity equation issue — addressed in Sprint 21

**Source:** `docs/planning/EPIC_4/SPRINT_21/SPRINT_RETROSPECTIVE.md` (lines 110-111)

### What Needs to Be Done

1. **Get current model_infeasible list** from latest pipeline output
2. **For each model, examine the GAMS .lst file** to determine:
   - Does PATH report "locally infeasible" or "no feasible solution"?
   - What is the model/solver status code?
   - Are there obvious stationarity/complementarity errors in the MCP?
3. **Classify each model:**
   - **KKT bug:** Stationarity equations have wrong signs, missing terms, or dimensional mismatches
   - **Starting point:** PATH converges to infeasible with default start, may solve with warm-start
   - **Model type incompatible:** CGE, linearized, or non-NLP model structure
   - **Genuine infeasibility:** Original NLP is also infeasible at KKT point
4. **Cross-reference with issue documents** in `docs/issues/`
5. **Identify 3+ models** with likely KKT bugs as Sprint 22 fix candidates
6. **Create triage document** at `docs/planning/EPIC_4/SPRINT_22/MODEL_INFEASIBLE_TRIAGE.md`

### Changes

- Created `docs/planning/EPIC_4/SPRINT_22/MODEL_INFEASIBLE_TRIAGE.md` with full classification of 15 models (12 from committed `gamslib_status.json` + 3 from local pipeline reruns: ibm1, twocge, feasopt1)
- Classified into 4 categories: A (KKT bug, 4), B (nonconvex/starting point, 5), C (model type incompatible, 4), D (needs investigation, 2)
- Identified 4 Sprint 22 fix candidates: whouse, ibm1, uimp, mexss (8-12h total)
- Verified KU-23 (confirmed — orani unfixable) and KU-24 (confirmed — 7-14 models at risk of shifting)
- Cross-referenced 5 existing issue documents (#757, #764, #765, #828, #970)

### Result

- **Sprint 22 target ≤12 is achievable** by fixing 3-4 Category A models (whouse, ibm1, uimp, mexss)
- 4 models permanently excluded (feasopt1 intentionally infeasible, iobalance/meanvar multi-model, orani linearized CGE)
- 5 models deferred (nonconvex NLP, need warm-start infrastructure)
- 2 models need deeper investigation (lnts `_fx_` handling, twocge CGE gradient)
- **KU-24 risk:** 7-14 path_syntax_error models may shift to model_infeasible when fixed (especially 6 CGE models)

### Verification

```bash
# Verify triage document exists
test -f docs/planning/EPIC_4/SPRINT_22/MODEL_INFEASIBLE_TRIAGE.md && echo "EXISTS" || echo "MISSING"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_22/MODEL_INFEASIBLE_TRIAGE.md`
- Each of 15 models classified (KKT bug / starting point / model type / genuine)
- Sprint 22 fix candidates identified (3+ models)
- Effort estimates for fixable models

### Acceptance Criteria

- [x] All 15 model_infeasible models classified
- [x] Each model has PATH solver output examined
- [x] Cross-references to existing issue docs where applicable
- [x] Fix candidates identified with rationale
- [x] Models excluded from Sprint 22 scope documented with justification
- [x] Classification informs Sprint 22 target (≤12 achievable?)

---

## Task 5: Profile Translation Timeout Bottlenecks

**Status:** :white_check_mark: COMPLETE
**Priority:** High
**Estimated Time:** 2 hours
**Deadline:** Before Sprint 22 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns to Verify:** (none — no unknowns specific to timeout profiling)

### Objective

Profile the 11 translation timeout models to identify whether bottlenecks are in Lark/Earley parsing, KKT derivation, or GAMS emission.

### Why This Matters

Translation timeouts (11 models) are the largest translation error category and block models from reaching the solve stage. Sprint 22's PROJECT_PLAN.md doesn't explicitly target translation improvements, but understanding bottlenecks informs whether quick wins exist.

### Background

Sprint 21 identified 11 timeout models and 6 internal_error models at the translation stage. Issue documents exist for several timeout models:
- #885 (sarf): Combinatorial explosion in translation
- #926 (dinam), #927 (egypt), #928 (ferts), #929 (ganges), #930 (gangesx)
- #931 (iswnm), #932 (nebrazil), #933 (tricp)

The 60s translation subprocess timeout is set in `batch_translate.py` (line 260). Some models may be very close to completion (e.g., 106s for ferts) while others may be fundamentally intractable (hours).

**Source:** Sprint 21 SPRINT_RETROSPECTIVE.md (lines 104-105)

### What Needs to Be Done

1. **List all 11 timeout models** from the latest pipeline output
2. **For 3-5 representative models**, run translation with profiling:
   ```bash
   timeout 180 .venv/bin/python -c "
   import sys, time; sys.setrecursionlimit(50000)
   from src.ir.parser import parse_file
   t0 = time.time()
   ir = parse_file('data/gamslib/raw/MODEL.gms')
   print(f'Parse: {time.time()-t0:.1f}s')
   # Continue to translate...
   "
   ```
3. **Identify bottleneck stage** for each: parsing, IR building, KKT derivation, emission
4. **Classify models by tractability:**
   - Near-miss (120-200s): May solve with higher timeout or minor optimization
   - Slow (200-600s): Needs specific optimization
   - Intractable (>600s): Needs architectural change or deferral
5. **Cross-reference with issue documents** for known root causes
6. **Document findings** at `docs/planning/EPIC_4/SPRINT_22/TRANSLATION_TIMEOUT_PROFILE.md`

### Changes

- Created `docs/planning/EPIC_4/SPRINT_22/TRANSLATION_TIMEOUT_PROFILE.md` with comprehensive profiling data
- Profiled 9 of 11 models with full stage-level timing (remaining 2 extrapolated from parse times)
- Classified all 11 models into 3 tractability tiers: Near-Miss (4), Slow (2), Intractable (5)

### Result

- **Jacobian computation is the dominant bottleneck** in 7 of 11 models (57–99% of total time)
- **Earley parsing** bottlenecks the remaining 4 models (egypt, dinam, ganges, gangesx)
- **4 near-misses**: egypt (59.6s), ferts (105.9s), dinam (135.0s), clearlak (191.8s)
- **No quick wins for Sprint 22**: architectural changes needed (sparsity-aware Jacobian or LP fast-path)
- **Trivial timeout increase**: increasing the **60s translation subprocess timeout in `batch_translate.py` to 150s** could recover egypt, ferts, and dinam (reducing timeout count from 11 to 8)
- **Translation timeout reduction NOT recommended** as a Sprint 22 workstream — not aligned with solve-stage focus

### Verification

```bash
# Verify profile document exists
test -f docs/planning/EPIC_4/SPRINT_22/TRANSLATION_TIMEOUT_PROFILE.md && echo "EXISTS" || echo "MISSING"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_22/TRANSLATION_TIMEOUT_PROFILE.md`
- Bottleneck stage identified for 9 profiled models (2 extrapolated)
- Tractability classification for all 11 models
- Quick-win opportunities documented (timeout increase to 150s for 3 models; no code-level quick wins)

### Acceptance Criteria

- [x] All 11 timeout models listed
- [x] 3-5 models profiled with stage-level timing (9 profiled)
- [x] Bottleneck stage identified for profiled models
- [x] Tractability classification complete
- [x] Quick-win recommendations documented (or "none found")
- [x] Findings inform Sprint 22 scope decision (include timeout work or defer?)

---

## Task 6: Survey Deferred Issues for Sprint 22 Fit

**Status:** :large_blue_circle: NOT STARTED
**Priority:** High
**Estimated Time:** 2 hours
**Deadline:** Before Sprint 22 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 2, 3, 4 (need solve-failure classifications to assess overlap)
**Unknowns to Verify:** KU-20, KU-21, KU-22

### Objective

Evaluate the 4 deferred Sprint 21 issues (#764, #765, #827, #830) against Sprint 22 goals and decide which (if any) to include.

### Why This Matters

The deferred issues total 22-30h of architectural work. Sprint 22 has ~24-30h total budget. Including all deferred issues would leave no room for the higher-leverage path_syntax_error and path_solve_terminated fixes. Need to make explicit scope decisions.

### Background

| Issue | Model | Problem | Est. Effort | Sprint 22 Leverage |
|-------|-------|---------|-------------|-------------------|
| #764 | mexss | Accounting variable stationarity | 8-12h | Fixes 1 model |
| #765 | orani | CGE model type incompatible | Detection only | Fixes 0 models (warning) |
| #827 | gtm | Domain violations from zero-fill | 6-8h | Fixes 1 model |
| #830 | gastrans | Jacobian timeout from dynamic subsets | 8-10h | Fixes 1 model |

**Source:** `docs/planning/EPIC_4/SPRINT_21/DEFERRED_ISSUES_TRIAGE.md`

### What Needs to Be Done

1. **Review each deferred issue document** in `docs/issues/`
2. **Assess overlap with Sprint 22 workstreams:**
   - Does #764 overlap with path_syntax_error Subcategory C (uncontrolled sets)?
   - Does #827 overlap with path_syntax_error Subcategory B (domain violations)?
   - Does #830 overlap with translation timeout work?
3. **Calculate leverage ratio:** models_fixed / effort_hours for each issue
4. **Compare to path_syntax_error subcategory leverage:** Subcategory C fixes 9 models in 3-5h
5. **Recommend scope decision:**
   - Include in Sprint 22
   - Defer to Sprint 23 with justification
   - Mark as "won't fix" with rationale (e.g., #765)
6. **Document decision** in `docs/planning/EPIC_4/SPRINT_22/DEFERRED_ISSUES_DECISION.md`

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify decision document exists
test -f docs/planning/EPIC_4/SPRINT_22/DEFERRED_ISSUES_DECISION.md && echo "EXISTS" || echo "MISSING"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_22/DEFERRED_ISSUES_DECISION.md`
- Scope decision (include/defer/won't-fix) for each of 4 deferred issues
- Leverage comparison against path_syntax_error subcategory fixes
- Budget impact analysis

### Acceptance Criteria

- [ ] All 4 deferred issues reviewed against Sprint 22 goals
- [ ] Overlap with Sprint 22 workstreams assessed
- [ ] Leverage ratios calculated
- [ ] Explicit include/defer/won't-fix decision for each
- [ ] Budget impact documented
- [ ] Decision rationale clear and defensible

---

## Task 7: Design path_syntax_error Fix Strategy

**Status:** :large_blue_circle: NOT STARTED
**Priority:** High
**Estimated Time:** 2 hours
**Deadline:** Before Sprint 22 Day 1
**Owner:** Development team
**Dependencies:** Task 2 (need updated subcategory catalog)
**Unknowns to Verify:** KU-02, KU-04

### Objective

Design the implementation approach for fixing Sprint 22's target path_syntax_error subcategories (C, B, G and others as identified in Task 2).

### Why This Matters

path_syntax_error fixes are the highest-leverage Sprint 22 work (−11 models target, addressing the largest solve failure category). Having a design ready before Day 1 prevents wasted exploration time during the sprint.

### Background

From Task 2's catalog update, the priority subcategories for Sprint 22 are:

- **Subcategory C (9 models):** Uncontrolled set in stationarity equations. Root cause: KKT assembly generates stationarity equations with set indices that aren't controlled by a domain. Fix likely in `src/kkt/stationarity.py` or `src/emit/emit_gams.py`.
- **Subcategory B (5 models):** Domain violation in emitted parameter data. Root cause: emitter writes parameter values for domain combinations that don't exist. Fix in `src/emit/emit_gams.py`.
- **Subcategory G (2 models):** Set index reuse conflict in sum. Root cause: translator reuses same index variable in nested sum expressions. Fix in `src/kkt/` or `src/ad/`.

**Source:** `docs/planning/EPIC_4/SPRINT_21/PATH_SYNTAX_ERROR_CATALOG.md`

### What Needs to Be Done

1. **For Subcategory C (uncontrolled sets):**
   - Examine 2-3 representative models' MCP output to identify the uncontrolled set pattern
   - Trace back to KKT assembly code that generates the problematic equations
   - Design fix: add domain conditioning, or emit equations with explicit domain controls
   - Identify which source files need modification
2. **For Subcategory B (domain violations):**
   - Examine 2-3 representative models' parameter data sections
   - Identify which emitter code produces out-of-domain data
   - Design fix: filter parameter data by valid domain combinations
3. **For Subcategory G (set index reuse):**
   - Examine the 2 affected models
   - Identify the sum/prod expression pattern that causes index collision
   - Design fix: rename conflicting indices during KKT derivation
4. **Document implementation plan** with:
   - Files to modify per subcategory
   - Estimated LOC changes
   - Test strategy (what to test, how to verify)
   - Risk assessment (could fix break other models?)
5. **Create design document** at `docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_FIX_DESIGN.md`

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify design document exists
test -f docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_FIX_DESIGN.md && echo "EXISTS" || echo "MISSING"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_FIX_DESIGN.md`
- Implementation approach for subcategories C, B, G
- Files to modify identified per subcategory
- Test strategy documented
- Risk assessment for each fix

### Acceptance Criteria

- [ ] Representative models examined for each target subcategory
- [ ] Root cause traced to specific source code
- [ ] Fix approach designed (not just "fix it" — specific code changes)
- [ ] Files to modify listed per subcategory
- [ ] Test strategy defined (regression + new tests)
- [ ] Risk assessment: could fix break currently-solving models?

---

## Task 8: Establish Sprint 22 Baseline Metrics

**Status:** :large_blue_circle: NOT STARTED
**Priority:** High
**Estimated Time:** 1 hour
**Deadline:** Before Sprint 22 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns to Verify:** KU-14, KU-15

### Objective

Run full pipeline and `make test` to establish the exact Sprint 22 starting baseline, confirming Sprint 21 final metrics.

### Why This Matters

Sprint 22 acceptance criteria are defined relative to baselines. The exact starting metrics need to be captured on the current `main` branch to ensure Sprint 22 improvements are measured accurately.

### Background

Sprint 21 final metrics (from SPRINT_RETROSPECTIVE.md):
- Parse: 154/157 (98.1%)
- Translate: 137/154 (89.0%) — timeout: 11, internal_error: 6
- Solve: 65/137 (47.4%) — path_syntax_error: 41, model_infeasible: 15, path_solve_terminated: 12, path_solve_license: 4
- Match: 30/65 (46.2%)
- Tests: 3,957 passed, 10 skipped, 1 xfailed

### What Needs to Be Done

1. **Checkout main** and ensure it's up to date with Sprint 21 final state
2. **Run full pipeline:**
   ```bash
   .venv/bin/python scripts/gamslib/run_full_test.py --quiet
   ```
3. **Run test suite:**
   ```bash
   make test
   ```
4. **Record exact metrics** in all error categories
5. **Create baseline document** at `docs/planning/EPIC_4/SPRINT_22/BASELINE_METRICS.md`
6. **Verify no regressions** from Sprint 21 final checkpoint

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify baseline document exists
test -f docs/planning/EPIC_4/SPRINT_22/BASELINE_METRICS.md && echo "EXISTS" || echo "MISSING"

# Verify test suite passes
make test
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_22/BASELINE_METRICS.md` with full error category breakdown
- Pipeline results matching Sprint 21 final (or noting any differences)
- Test count confirmed

### Acceptance Criteria

- [ ] Full pipeline run completed on current main
- [ ] All error categories captured (parse, translate, solve, match)
- [ ] Results compared to Sprint 21 final — no regressions
- [ ] Baseline document created with full breakdown
- [ ] Test count and status recorded

---

## Task 9: Assess Match Rate Improvement Opportunities

**Status:** :large_blue_circle: NOT STARTED
**Priority:** Medium
**Estimated Time:** 2 hours
**Deadline:** Before Sprint 22 Day 1
**Owner:** Development team
**Dependencies:** Task 3 (need path_solve_terminated classification for newly-solving model projections)
**Unknowns to Verify:** KU-11, KU-12, KU-13, KU-26

### Objective

Identify which of the current 35 "solve but don't match" models have the best chance of matching with targeted fixes, to inform Sprint 22's Match ≥ 35 target.

### Why This Matters

Sprint 22 targets Match ≥ 35 (from 30, +5 models). Understanding why the 35 non-matching models fail to match helps prioritize which solve improvements will also improve match rate.

### Background

Sprint 21 WS6 improved match rate via tolerance relaxation (DEFAULT_RTOL to 2e-3) and IndexOffset gradient fixes. Of the 65 solving models, 30 match and 35 don't. The non-matching models may have:
- Objective value divergence beyond tolerance
- Multiple optima (KKT point differs from NLP solution)
- Non-convex models where MCP finds different local optimum
- Numerical precision issues in KKT derivatives

**Source:** Sprint 21 WS9 solution comparison framework (`tests/gamslib/test_test_solve.py`)

### What Needs to Be Done

1. **Get current match/mismatch list** from pipeline output
2. **For 5-10 near-miss models** (solve but don't match):
   - Compare MCP objective to NLP objective
   - Classify: tolerance issue, multiple optima, non-convex, or formulation bug
3. **Cross-reference with issue documents** (e.g., #958-#964 are objective mismatch issues)
4. **Identify models likely to start matching** if path_syntax_error/path_solve_terminated fixes are applied (newly solving models that are likely convex)
5. **Estimate Sprint 22 match rate improvement** based on projected solve improvements
6. **Document findings** at `docs/planning/EPIC_4/SPRINT_22/MATCH_RATE_ANALYSIS.md`

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify analysis document exists
test -f docs/planning/EPIC_4/SPRINT_22/MATCH_RATE_ANALYSIS.md && echo "EXISTS" || echo "MISSING"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_22/MATCH_RATE_ANALYSIS.md`
- Classification of 5-10 near-miss models
- Projected match rate from Sprint 22 solve improvements
- Recommendations for targeted match improvements

### Acceptance Criteria

- [ ] Current match/mismatch list captured
- [ ] 5-10 near-miss models classified
- [ ] Non-convex multi-optima models identified
- [ ] Projected match improvement estimated
- [ ] Recommendations documented for Sprint 22

---

## Task 10: Plan Sprint 22 Detailed Schedule

**Status:** :large_blue_circle: NOT STARTED
**Priority:** Critical
**Estimated Time:** 3 hours
**Deadline:** Before Sprint 22 Day 1
**Owner:** Sprint planning
**Dependencies:** All tasks (1-9)
**Unknowns to Verify:** (all remaining — synthesize findings into plan)

### Objective

Create detailed Sprint 22 plan with day-by-day schedule, incorporating all prep task findings.

### Why This Matters

Sprint 22 has complex dependencies between workstreams (path_syntax_error fixes may affect path_solve_terminated counts; model_infeasible fixes require KKT understanding from subcategory C work). A detailed plan prevents mid-sprint re-planning.

### Background

Sprint 22 scope from PROJECT_PLAN.md (lines 509-625):
- KKT Correctness Fixes (~8-10h)
- PATH Solver Tuning (~4-6h) **← Invalidated by Sprint 21 findings; redirect to pre-solver error fixes**
- MCP-NLP Solution Divergence Analysis (~6-8h)
- Parse Completion Final Push (~4h)
- Pipeline Retest (~2h)

Sprint 21 Retrospective recommended targets:
- path_syntax_error ≤ 30 (from 41)
- model_infeasible ≤ 12 (from 15)
- Solve ≥ 75 (from 65)
- Match ≥ 35 (from 30)
- Tests ≥ 4,020 (from 3,957)

### What Needs to Be Done

1. **Synthesize findings** from Tasks 1-9 into Sprint 22 scope
2. **Define workstreams** (revised from PROJECT_PLAN.md based on Sprint 21 findings):
   - WS1: path_syntax_error subcategory fixes (C, B, G)
   - WS2: path_solve_terminated pre-solver error fixes
   - WS3: model_infeasible KKT bug fixes
   - WS4: Solution divergence analysis
   - WS5: Translation timeout investigation (if quick wins found in Task 5)
   - WS6: Deferred issues (if included per Task 6 decision)
3. **Create 15-day schedule** (Day 0 – Day 14) with:
   - Day-by-day tasks and workstream assignments
   - Checkpoint gates (Day 5, Day 10, Day 14)
   - Acceptance criteria per checkpoint
   - Pipeline retest points
4. **Define acceptance criteria** aligned with Sprint 22 targets
5. **Create plan** at `docs/planning/EPIC_4/SPRINT_22/PLAN.md`
6. **Create day-by-day prompts** at `docs/planning/EPIC_4/SPRINT_22/prompts/PLAN_PROMPTS.md`

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify plan documents exist
test -f docs/planning/EPIC_4/SPRINT_22/PLAN.md && echo "EXISTS" || echo "MISSING"
test -f docs/planning/EPIC_4/SPRINT_22/prompts/PLAN_PROMPTS.md && echo "EXISTS" || echo "MISSING"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_22/PLAN.md` with full 15-day schedule
- `docs/planning/EPIC_4/SPRINT_22/prompts/PLAN_PROMPTS.md` with day-by-day execution prompts
- `docs/planning/EPIC_4/SPRINT_22/SPRINT_LOG.md` template with day sections
- Acceptance criteria aligned with Sprint 22 targets
- Checkpoint gates at Days 5, 10, 14

### Acceptance Criteria

- [ ] Plan created with all 15 days defined
- [ ] All workstreams mapped to specific days
- [ ] Checkpoint gates defined with go/no-go criteria
- [ ] Acceptance criteria match Sprint 22 targets
- [ ] Known unknowns referenced
- [ ] Contingency plans for high-risk workstreams
- [ ] Day-by-day prompts created
- [ ] Sprint log template created

---

## Summary: Execution Order and Critical Path

### Phase 1: Research and Cataloging (Can Run in Parallel)

| Task | Time | Dependencies |
|------|------|-------------|
| Task 1: Known Unknowns | 2h | None |
| Task 2: path_syntax_error Catalog | 3h | None |
| Task 3: path_solve_terminated Classification | 3h | None |
| Task 4: model_infeasible Triage | 3h | None |
| Task 5: Translation Timeout Profiling | 2h | None |
| Task 8: Baseline Metrics | 1h | None |

**Subtotal:** ~14h (parallelizable — all can run independently)

### Phase 2: Analysis and Design (Depends on Phase 1)

| Task | Time | Dependencies |
|------|------|-------------|
| Task 6: Deferred Issues Survey | 2h | Tasks 2, 3, 4 |
| Task 7: path_syntax_error Fix Design | 2h | Task 2 |
| Task 9: Match Rate Analysis | 2h | Task 3 |

**Subtotal:** ~6h

### Phase 3: Planning (Depends on All)

| Task | Time | Dependencies |
|------|------|-------------|
| Task 10: Sprint 22 Detailed Schedule | 3h | All tasks |

**Subtotal:** ~3h

### Total Estimated Time: ~23 hours (~3 working days)

### Critical Path: Tasks 1 → 2 → 7 → 10 (~10 hours minimum)

---

## Success Criteria for Prep Phase

Before Sprint 22 Day 1, verify:

### Critical (Must Complete)
- [x] Known Unknowns document created (Task 1)
- [x] path_syntax_error catalog updated (Task 2)
- [x] path_solve_terminated models classified (Task 3)
- [ ] Sprint 22 plan created with day-by-day schedule (Task 10)

### High Priority (Should Complete)
- [ ] model_infeasible models triaged (Task 4)
- [ ] Translation timeout bottlenecks profiled (Task 5)
- [ ] Deferred issues scope decision documented (Task 6)
- [ ] path_syntax_error fix design ready (Task 7)
- [ ] Baseline metrics captured (Task 8)

### Medium Priority (Nice to Have)
- [ ] Match rate improvement opportunities assessed (Task 9)

### Verification Commands

```bash
# Verify all prep documents exist
ls docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md
ls docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_STATUS.md
ls docs/planning/EPIC_4/SPRINT_22/PATH_SOLVE_TERMINATED_STATUS.md
ls docs/planning/EPIC_4/SPRINT_22/MODEL_INFEASIBLE_TRIAGE.md
ls docs/planning/EPIC_4/SPRINT_22/TRANSLATION_TIMEOUT_PROFILE.md
ls docs/planning/EPIC_4/SPRINT_22/DEFERRED_ISSUES_DECISION.md
ls docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_FIX_DESIGN.md
ls docs/planning/EPIC_4/SPRINT_22/BASELINE_METRICS.md
ls docs/planning/EPIC_4/SPRINT_22/MATCH_RATE_ANALYSIS.md
ls docs/planning/EPIC_4/SPRINT_22/PLAN.md

# Verify test suite passes
make test

# Verify pipeline baseline
.venv/bin/python scripts/gamslib/run_full_test.py --only-parse --quiet
```

**Sprint 22 is ready to begin when all Critical items are checked.**

---

## Appendix: Document Cross-References

### Sprint Goals
- `docs/planning/EPIC_4/PROJECT_PLAN.md` (lines 509-625) — Sprint 22 scope and components
- `docs/planning/EPIC_4/PROJECT_PLAN.md` (lines 895-915) — Rolling KPIs with S22 targets

### Epic Goals
- `docs/planning/EPIC_4/GOALS.md` — Epic 4 overall objectives (parse ≥95%, solve ≥70% pipeline)

### Sprint 21 Outputs (Inputs to Sprint 22)
- `docs/planning/EPIC_4/SPRINT_21/SPRINT_RETROSPECTIVE.md` — Sprint 22 recommendations (lines 134-154)
- `docs/planning/EPIC_4/SPRINT_21/PATH_CONVERGENCE_ANALYSIS.md` — Classification of all 29 path_solve_terminated models
- `docs/planning/EPIC_4/SPRINT_21/PATH_SYNTAX_ERROR_CATALOG.md` — Subcategory A-G, I, J classification (no H)
- `docs/planning/EPIC_4/SPRINT_21/DEFERRED_ISSUES_TRIAGE.md` — 4 deferred issues (#764, #765, #827, #830)

### Issue Documents
- `docs/issues/ISSUE_764_mexss-mcp-locally-infeasible-accounting-variables.md`
- `docs/issues/ISSUE_765_orani-mcp-locally-infeasible-fixed-variables-exogenous.md`
- `docs/issues/ISSUE_827_gtm-domain-violation-zero-fill.md`
- `docs/issues/ISSUE_830_gastrans-jacobian-dynamic-subset-timeout.md`
- `docs/issues/ISSUE_983_elec-mcp-division-by-zero-distance.md`
- `docs/issues/ISSUE_984_etamac-mcp-division-by-zero-log-singular.md`
- `docs/issues/ISSUE_986_lands-mcp-rhs-na-equation.md`
- `docs/issues/ISSUE_958_ps2_f_s-objective-mismatch-nonconvex-multi-solve.md` (and #959-#964)

### Research Documents
- `docs/research/minmax_path_validation_findings.md` — Min/max reformulation findings
- `docs/research/CONVEXITY_VERIFICATION_DESIGN.md` — Model convexity classification

### Process Recommendations (from Sprint 21)
- PR1: Standardize pipeline denominator (157 available / 160 catalog) — Continue
- PR2: Record PR numbers immediately — Enforce
- PR3: Full pipeline retest at checkpoints — Continue
- PR4: Targeted solve on newly-parsing models — Continue (extend to newly-solving models)
- PR5: Full error category breakdown at checkpoints — Continue

---

**Document Created:** March 5, 2026
**Sprint 22 Target Start:** TBD (after prep completion)
**Next Steps:** Execute prep tasks in order, verify completion, begin Sprint 22
