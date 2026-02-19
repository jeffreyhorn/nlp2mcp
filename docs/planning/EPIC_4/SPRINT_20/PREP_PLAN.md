# Sprint 20 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 20 begins
**Timeline:** Complete before Sprint 20 Day 1
**Goal:** Resolve known unknowns, finalize scope, and establish a reliable baseline so Sprint 20 can execute without mid-sprint surprises

**Key Insight from Sprint 19:** The smoke-test-before-declaring-issues-not-fixable lesson (#671 was already resolved but nearly misjudged) underscores the importance of verifying the current pipeline state before any assessment. Run `python -m src.cli <model>` before making architectural decisions.

---

## Executive Summary

Sprint 20 focuses on four workstreams:
1. **IndexOffset end-to-end pipeline** — AD integration was completed in Sprint 19 (Sprint 19 PRs #779, #785); Sprint 20 focuses on AD index substitution, validation of IndexOffset behavior, and end-to-end testing of all 8 blocked models, including confirming emitter/parser coverage for Subcategory D models and addressing any newly identified issues
2. **Deferred Sprint 19 solver blockers** — `.l` initialization emission (#753/#757), accounting variable detection (#764), AD condition propagation (#763), min/max in objective-defining equations (#789)
3. **Remaining lexer_invalid_char reduction** — 27 remain after Sprint 19; Subcategories G, H, J, K not yet addressed; I requires re-check
4. **Full pipeline match rate** — 9/160 (5.6%); close the gap between solve success (25 models) and full pipeline match by investigating objective value divergence

This prep plan produces the research, catalogs, baselines, and design artifacts needed to begin Sprint 20 Day 1 without context-building overhead.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|----------------------|
| 1 | ✅ Create Sprint 20 Known Unknowns List | Critical | 2–3h | None | All workstreams |
| 2 | ✅ Audit IndexOffset End-to-End Pipeline State | Critical | 2–3h | Task 1 | IndexOffset implementation |
| 3 | ✅ Catalog Remaining lexer_invalid_char Subcategories | High | 2–3h | Task 1 | lexer_invalid_char reduction |
| 4 | ✅ Investigate .l Initialization Emission Gap | High | 2–3h | Task 1 | Deferred Sprint 19 (#753/#757) |
| 5 | ✅ Audit Translate internal_error Models | High | 2–3h | Tasks 1, 2 | Translation error fixes |
| 6 | ✅ Investigate Full Pipeline Match Divergence | High | 2–3h | Task 1 | Full pipeline match rate |
| 7 | Design Accounting Variable Detection (#764) | Medium | 2–3h | Tasks 1, 5 | Deferred Sprint 19 (#764) |
| 8 | ✅ Review Sprint 19 Retrospective Action Items | Medium | 1h | None | Process improvement |
| 9 | Snapshot Baseline Metrics | Medium | 1h | None | All workstreams |
| 10 | Plan Sprint 20 Detailed Schedule | Critical | 3–4h | All tasks | Sprint planning |

**Total Estimated Time:** ~23–29 hours (~3–4 working days)

**Critical Path:** Task 1 → Tasks 2, 3, 4, 5, 6, 7 (parallel) → Task 10

---

## Task 1: Create Sprint 20 Known Unknowns List

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 20 Day 1
**Owner:** Development team
**Dependencies:** None

### Objective

Create `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md` with all significant unknowns for Sprint 20 across the four workstreams. Categorize by domain, assign priority, and identify the verification method for each unknown.

### Why This Matters

The Sprint 19 retrospective rated the Known Unknowns process highly (⭐⭐⭐⭐⭐ in Sprint 5, consistently useful since Sprint 4). Proactively identifying unknowns before Day 1 prevents mid-sprint architectural surprises and allows targeted prep work to resolve the highest-risk unknowns before implementation begins.

### Background

Sprint 19 identified these as the highest-risk unknowns going into Sprint 20:
- **IndexOffset correctness:** Are the 8 blocked models actually blocked by AD gaps or by emit gaps? (Sprint 19 Day 12–13 work closed the AD gap; emit and parser gaps remain)
- **`.l` emission:** Does the IR already store `.l` assignments, or do they need to be captured during parsing?
- **Accounting variable detection:** What heuristic reliably identifies accounting/auxiliary variables without over-triggering?
- **AD condition propagation:** How deep does the `$` condition need to be propagated through derivative expressions?
- **lexer_invalid_char subcategories G–K:** How many models in each? Are there quick wins vs. investigation-heavy cases?
- **Full pipeline match gap:** Is the 25-solve / 9-match gap caused by initialization (`.l`), scaling (`.scale`), or solver tolerance issues?

Previous research documents:
- `docs/planning/EPIC_4/SPRINT_19/INDEX_OFFSET_DESIGN_OPTIONS.md` — confirmed emit layer already handles IndexOffset; AD work was the remaining gap
- `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` — full subcategory breakdown; Subcategories A/B/F/I fixed in Sprint 19
- `docs/issues/ISSUE_753_circle-mcp-locally-infeasible.md` — `.l` initialization gap details
- `docs/issues/ISSUE_764_mexss-mcp-locally-infeasible-accounting-variables.md` — accounting variable detection scope

### What Needs to Be Done

1. **Review Sprint 19 retrospective** (`docs/planning/EPIC_4/SPRINT_19/SPRINT_RETROSPECTIVE.md`) recommendations section
2. **Review deferred issue files** (#753, #757, #763, #764, #765, #789) to extract the "not fixable" reasons as unknowns
3. **Review IndexOffset design document** (`docs/planning/EPIC_4/SPRINT_19/INDEX_OFFSET_DESIGN_OPTIONS.md`) for open questions
4. **Review LEXER_ERROR_CATALOG** Subcategories G–K for unknowns
5. **Draft KNOWN_UNKNOWNS.md** with:
   - 5 categories: IndexOffset, Deferred Solver Blockers, lexer_invalid_char, Pipeline Match, Process
   - For each unknown: assumption, verification method, priority, owner, estimated research time
   - Target: 15–25 unknowns total
6. **Identify which unknowns can be resolved during prep** vs. which are sprint work

### Changes

- Created `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`

### Result

26 unknowns documented across 8 categories (6 Critical, 11 High, 7 Medium, 2 Low). Task-to-Unknown mapping appendix links each prep task (2–10) to its verified unknowns. All four Sprint 20 workstreams covered.

### Verification

```bash
ls docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md
wc -l docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md
```

### Deliverables

- ✅ `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md` with 26 unknowns across 8 categories

### Acceptance Criteria

- [x] Document created with 15+ unknowns across at least 5 categories (26 unknowns, 8 categories)
- [x] All unknowns have: assumption, verification method, priority
- [x] All Critical/High unknowns have a verification plan
- [x] Unknowns cover all four Sprint 20 workstreams
- [x] At least 3 unknowns identified as resolvable during prep phase (Unknowns 1.4, 4.2, 5.4, 6.3, 7.2 are quick/30-min items)

---

## Task 2: Audit IndexOffset End-to-End Pipeline State

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 20 Day 1
**Owner:** Development team
**Dependencies:** Task 1
**Unknowns Verified:** 6.1, 6.2, 6.3

### Objective

Determine the exact current state of IndexOffset support across all pipeline stages (parse → IR → AD → emit) and identify the precise remaining gaps for each of the 8 blocked models.

### Why This Matters

Sprint 20's primary workstream (IndexOffset end-to-end) has a stated estimate of 14–16h in PROJECT_PLAN.md, but the Sprint 19 design audit (`INDEX_OFFSET_DESIGN_OPTIONS.md`) revised this down to ~8h because the emit layer was already complete and the IR node already existed. The AD integration work (Sprint 19 PRs #779, #785) closed the derivative computation gap. Sprint 20 may need significantly less time than estimated — or may have discovered new gaps. An accurate audit before Day 1 prevents scope miscalibration.

### Background

Sprint 19 IndexOffset progress:
- **IR node:** Existed since Sprint 9 Day 3 (`src/ir/ast.py`)
- **Grammar/parser:** `offset_paren`, `offset_func` parser rules added in PR #785
- **AD integration:** `_substitute_index()` + `_apply_index_substitution()` for VarRef/ParamRef/DollarConditional (PR #779); `offset_paren`/`offset_func` callback pattern (PR #785)
- **Emit layer:** `_format_mixed_indices()` already handles IndexOffset (pre-Sprint 19)
- **8 blocked models:** Per `INDEX_OFFSET_DESIGN_OPTIONS.md`: `launch`, `mine`, `sparta`, `tabora`, `ampl`, `otpop`, `robert`, `pak` (with `launch`/`mine`/`sparta`/`tabora` as Subcategory D lead/lag models)

From `INDEX_OFFSET_DESIGN_OPTIONS.md`:
> Effort estimate: 8h total (4h AD index-substitution work + 2h end-to-end pipeline tracing + 2h testing/integration), down from ~14-16h originally estimated

Sprint 19 delivered the 4h AD work. Remaining: ~4h.

### What Needs to Be Done

1. **Run each of the 8 blocked models** through the full pipeline:
   ```bash
   python -m src.cli data/gamslib/raw/<model>.gms
   ```
2. **For each model, classify current failure stage:** parse / translate / solve / none (already works)
3. **Check `ampl` and `otpop`** specifically — both were in Subcategory D (lexer_invalid_char); Sprint 19 PRs #785–#786 fixed the parser for `ampl` (set ordinal attrs) and `otpop` (eqn attr assignment) — verify if lead/lag indexing is still a blocker or if those PRs resolved it
4. **Identify remaining gaps per stage:**
   - Grammar: any remaining lead/lag syntax not covered by `offset_paren`/`offset_func`?
   - AD: any sum-collapse-with-IndexOffset cases (the Sprint 19 xfail)?
   - Emit: any formatting gaps for circular lead/lag (`++`/`--`)?
5. **Document findings** in `docs/planning/EPIC_4/SPRINT_20/INDEXOFFSET_AUDIT.md`

### Changes

- Created `docs/planning/EPIC_4/SPRINT_20/INDEXOFFSET_AUDIT.md`: per-model status table for all 8 blocked models, failure analysis for sparta/tabora/otpop, xfail assessment, emit layer circular audit, revised effort estimate
- Updated `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`: Unknowns 6.1, 6.2, 6.3 → ✅ VERIFIED with detailed findings

### Result

5 of 8 IndexOffset-blocked models (launch, mine, ampl, robert, pak) now translate successfully — Sprint 19 AD work unblocked them. The 3 remaining failures (sparta, tabora, otpop) are all in `IndexOffset.to_gams_string()` in `src/ir/ast.py`: it doesn't handle `Unary("-", Call(...))` offsets (sparta/tabora) or `Binary(op, Call, Call)` offsets (otpop). The xfail test is a cleanup item only. Circular lead/lag (`++`/`--`) is fully supported. Revised IndexOffset effort estimate: **~3h** (was ~4h).

### Verification

```bash
ls docs/planning/EPIC_4/SPRINT_20/INDEXOFFSET_AUDIT.md
# Each of the 8 models should have a current status documented
grep -c "| " docs/planning/EPIC_4/SPRINT_20/INDEXOFFSET_AUDIT.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_20/INDEXOFFSET_AUDIT.md` — per-model status table with current failure stage and remaining work
- Updated effort estimate for Sprint 20 IndexOffset workstream
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 6.1, 6.2, 6.3

### Acceptance Criteria

- [x] All 8 blocked models run through current pipeline and status recorded
- [x] Each model has: current failure stage, specific error, remaining work estimate
- [x] Sprint 20 IndexOffset effort estimate revised based on findings
- [x] The xfail test (sum-collapse-with-IndexOffset-wrt) assessed for scope
- [x] Unknowns 6.1, 6.2, 6.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 3: Catalog Remaining lexer_invalid_char Subcategories

**Status:** ✅ COMPLETE
**Priority:** High
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 20 Day 1
**Owner:** Development team
**Dependencies:** Task 1
**Unknowns Verified:** 4.1, 4.2, 4.3, 4.4

### Objective

Run all remaining `lexer_invalid_char` models (27 after Sprint 19) through the parser with verbose output, verify their subcategory classification, and identify which models have moved between categories or been resolved since the Sprint 19 LEXER_ERROR_CATALOG was written.

### Why This Matters

Sprint 19 fixed Subcategories A (compound set data), B (cascading — resolved indirectly), F (declaration gaps), and I (model/solve statements). The 27 remaining models span Subcategories C (put statement, partially addressed), D (lead/lag), E (special values), G (set element descriptions), H (control flow), J (bracket/brace), and K (miscellaneous). Sprint 20 Priority 4 targets +10–15 more models parsing. A fresh taxonomy pass ensures we're working from accurate data.

### Background

From `LEXER_ERROR_CATALOG.md` Sprint 19 baseline (72 models):
- A (12) + B (15) + F (7) + I (5) = 39 models targeted
- Sprint 19 resolved ~45 models (72 → 27)
- Remaining subcategories with estimated residual counts:
  - C (Put Statement Format): 6 in catalog, ~3–4 remain (some fixed by Sprint 19 PR #745)
  - D (Lead/Lag): 4 in catalog, likely 2 remain (ampl/otpop may now parse)
  - E (Special Values): 7 in catalog, ~3–5 remain
  - G (Set Element Descriptions): 4 in catalog
  - H (Control Flow): 2 in catalog
  - J (Bracket/Brace): 3 in catalog
  - K (Miscellaneous): 7 in catalog

The subcategory counts above are estimates — the actual numbers after Sprint 19 fixes need to be verified.

### What Needs to Be Done

1. **Run the pipeline parse-only** on all models currently classified as `lexer_invalid_char`:
   ```bash
   .venv/bin/python scripts/gamslib/run_full_test.py --only-parse --quiet 2>&1 | grep lexer_invalid_char
   ```
2. **For each of the 27 remaining models**, run with verbose output and capture the specific token/line causing failure
3. **Re-classify into subcategories** using the existing A–K taxonomy from `LEXER_ERROR_CATALOG.md`
4. **Identify new subcategories** if patterns don't fit existing taxonomy
5. **Rank by model count** (highest-ROI fixes first)
6. **Estimate effort per subcategory** for Sprint 20 grammar work
7. **Update or create** `docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md`

### Changes

- Created `docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md`: full 27-model per-model table, per-subcategory summary, new subcategory documentation (L, M), top-3 ROI analysis, quick wins, Subcategory D/IndexOffset overlap assessment, Sprint 20 implementation order
- Updated `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`: Unknowns 4.1, 4.2, 4.3, 4.4 → ✅ VERIFIED with detailed findings

### Result

All 27 remaining `lexer_invalid_char` models rechecked and reclassified. Two new subcategories identified: **L (Set-Model Exclusion)** — `/ all - setname /` and dotted `eq.var` in model/set statements (5 models, 1–2h) — and **M (Unsupported Declarations)** — `File` and `Acronym` keywords (2 models, 1–2h). Subcategory G is fully resolved (0 remaining). Top ROI: L (5 models, 1–2h), A (6 models, 3–4h), B (3 models, 0h cascading). The 2 Subcategory D models (mine, pindyck) will resolve automatically with the Sprint 20 IndexOffset `to_gams_string()` fix — no separate grammar work needed.

### Verification

```bash
ls docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md
# Should list 27 models with subcategory
grep -c "^|" docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md` — updated catalog of 27 remaining models with subcategory, token, and fix estimate
- Prioritized list of subcategories for Sprint 20 grammar work
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.1, 4.2, 4.3, 4.4

### Acceptance Criteria

- [x] All 27 `lexer_invalid_char` models rechecked against current codebase
- [x] Each model has: subcategory, failing token/line, estimated fix effort
- [x] Subcategory counts sum to 27
- [x] Top 3 highest-ROI subcategories identified with effort estimates (L: 5 models 1–2h; A: 6 models 3–4h; B: 3 models 0h)
- [x] At least 2 "quick win" grammar fixes identified (L: 5 models 1–2h; M: 2 models 1–2h; H: 2 models 1–2h)
- [x] Unknowns 4.1, 4.2, 4.3, 4.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 4: Investigate .l Initialization Emission Gap

**Status:** ✅ COMPLETE
**Priority:** High
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 20 Day 1
**Owner:** Development team
**Dependencies:** Task 1
**Unknowns Verified:** 1.1, 1.2, 1.3, 1.4

### Objective

Determine exactly what changes are needed to emit `.l` variable level initialization statements from the IR in the MCP prolog, and verify that this fix would unblock the `circle` (#753) and `bearing` (#757) models.

### Why This Matters

Sprint 20 Priority 1 (`.l` initialization emission) is rated as "low-to-medium effort" with "+2–4 models solving" impact. Before committing sprint days to this workstream, we need to confirm: (a) the IR already captures `.l` assignments during parsing, (b) the emit layer gap is precisely where the fix goes, and (c) the fix actually resolves circle/bearing infeasibility rather than exposing a deeper KKT issue.

### Background

From `docs/issues/ISSUE_753_circle-mcp-locally-infeasible.md`:
- circle.gms uses `.l` assignments to initialize variable levels before solving
- The generated MCP file omits these initializations
- PATH is highly sensitive to starting points — without good initialization, it fails even for correctly-formulated MCPs
- The circle model MCP is mathematically correct (deterministic fix applied in Sprint 19 PR #750 resolved randomness); infeasibility is now purely a starting-point issue

From `docs/issues/ISSUE_757_bearing-mcp-locally-infeasible.md`:
- bearing.gms uses `.l` assignments and also `.scale` for variable scaling
- `.l` emission may partially help; `.scale` emission is a separate (harder) gap
- Both issues contribute to PATH infeasibility

The IR parser (`src/ir/parser.py`) handles many assignment types. The question is whether `.l` assignments are: (a) parsed and stored in the IR (making emission straightforward), (b) silently dropped, or (c) not recognized at all.

### What Needs to Be Done

1. **Check if `.l` assignments are parsed** by the current IR:
   ```bash
   python -c "
   import sys; sys.setrecursionlimit(50000)
   from src.ir.parser import parse_file
   ir = parse_file('data/gamslib/raw/circle.gms')
   print([a for a in ir.assignments if hasattr(a, 'attr') and a.attr == 'l'])
   "
   ```
2. **Search the IR AST** for `.l` assignment representation:
   ```bash
   grep -n "\.l\|var_attr\|level\|assignment.*attr\|AttrAssignment" src/ir/ast.py src/ir/parser.py | head -30
   ```
3. **Check the MCP emit layer** for existing handling of variable attributes:
   ```bash
   grep -n "\.l\|level\|prolog\|init" src/emit/emit_gams.py src/emit/model.py | head -20
   ```
4. **Trace circle.gms `.l` assignments** through parse → IR → emit
5. **Determine fix location:** IR parser (if not capturing), emit layer (if not emitting), or both
6. **Verify against bearing** to confirm the fix would apply there too
7. **Document findings** in `docs/planning/EPIC_4/SPRINT_20/L_INIT_EMISSION_DESIGN.md`

### Changes

- Created `docs/planning/EPIC_4/SPRINT_20/L_INIT_EMISSION_DESIGN.md`: gap analysis, fix strategy with 3-file changes, before/after example for circle, bearing assessment, revised effort estimate
- Updated `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`: Unknowns 1.1, 1.2, 1.3, 1.4 → ✅ VERIFIED with detailed findings

### Result

The `.l` emission gap is a **parser gap**, not an emitter gap. The emitter already has a complete initialization section (Sprint 18 Day 3). The parser silently drops expression-based `.l` assignments (`return` when `_extract_constant()` fails in `_handle_assign`). Fix requires 3 files: `symbols.py` (add `l_expr`/`l_expr_map` fields), `parser.py` (store instead of drop), `emit_gams.py` (emit new fields). Effort revised to ~3.5–4h (was ~2h). Circle fix: high confidence. Bearing: `.l` already emitted; blocked by `.scale` (separate fix). 8 expression-based models missed; 28 constant models already working.

### Verification

```bash
ls docs/planning/EPIC_4/SPRINT_20/L_INIT_EMISSION_DESIGN.md
grep "Fix Location" docs/planning/EPIC_4/SPRINT_20/L_INIT_EMISSION_DESIGN.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_20/L_INIT_EMISSION_DESIGN.md` — design document for `.l` emission fix with code locations, fix strategy, and expected impact on circle/bearing
- Revised effort estimate for Sprint 20 Priority 1
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 1.3, 1.4

### Acceptance Criteria

- [x] Whether `.l` assignments are captured in the IR is determined (partial — constant yes, expression-based no)
- [x] Fix location in codebase identified with file + line range (symbols.py ~86–95, parser.py ~3560–3575, emit_gams.py ~185–195)
- [x] Fix strategy documented with before/after example for circle.gms
- [x] Confirmed whether fix resolves circle infeasibility (yes — warm start, high confidence)
- [x] Bearing assessment: `.scale` is the primary blocker; `.l` already emitted and working
- [x] Effort estimate refined to ~3.5–4h (±0.5h)
- [x] Unknowns 1.1, 1.2, 1.3, 1.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 5: Audit Translate internal_error Models

**Status:** ✅ COMPLETE
**Priority:** High
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 20 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 7.1, 7.2, 8.1

### Objective

Identify the current set of models failing with `internal_error` at the translate stage, classify each by root cause, and determine which are addressable in Sprint 20 vs. require architectural changes.

### Why This Matters

PROJECT_PLAN.md Sprint 20 includes "Translation Internal Error Fixes (~6–8h): debug 5 failing models." But `internal_error` at translate stage is distinct from `internal_error` at parse stage. Sprint 19 reduced parse-stage internal errors from 24 to 6, but the translate-stage population needs a fresh audit. The 5-model count in PROJECT_PLAN.md may be outdated or may refer to a specific subset. Before allocating 6–8h to this workstream, we need the current count and a root-cause classification.

### Background

Sprint 19 `INTERNAL_ERROR_ANALYSIS_PREP.md` focused on parse-stage internal errors (21/24 were already resolved by Sprint 18). The translate-stage internal errors are a separate population caused by: missing derivative rules, IR construction crashes in KKT assembly, or unsupported expression patterns in the AD system.

Models that now parse successfully after Sprint 19's 46-model improvement will enter the translate stage for the first time — some of these may generate translate internal errors.

### What Needs to Be Done

1. **Run the full pipeline** to get current translate failure counts:
   ```bash
   .venv/bin/python scripts/gamslib/run_full_test.py --quiet 2>&1 | grep internal_error
   ```
2. **List all translate-stage internal errors** with stack traces:
   ```bash
   for model in <list>; do
       python -m src.cli data/gamslib/raw/$model.gms 2>&1 | tail -20
   done
   ```
3. **Classify by root cause:**
   - Missing AD rule (e.g., no derivative for a specific function)
   - IR construction crash (e.g., unexpected AST node type)
   - KKT assembly error (e.g., domain mismatch, unsupported expression)
   - IndexOffset-related (would be fixed by IndexOffset workstream)
4. **Determine fixability:** addressable in Sprint 20 vs. requires architectural work
5. **Document findings** in `docs/planning/EPIC_4/SPRINT_20/TRANSLATE_ERROR_AUDIT.md`

### Changes

- Created `docs/planning/EPIC_4/SPRINT_20/TRANSLATE_ERROR_AUDIT.md`: per-model root cause table for all 10 translate failures; stale-JSON correction for 3 now-passing models; model_no_objective_def preprocessor bug analysis (13 models); effort reallocation recommendation
- Updated `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`: Unknowns 7.1, 7.2, 8.1 → ✅ VERIFIED

### Result

True translate `internal_error` count: **2** (not 5 — status JSON was stale). orani, prolog, ramsey now translate successfully. Only maxmin (smin aggregation AD rule, deferred ~4–6h) and mlbeta (loggamma/digamma unavailable, permanently infeasible) remain. PROJECT_PLAN.md "5 models, 6–8h" estimate corrected to 0 S20-addressable. The `model_no_objective_def` category (14 models at parse stage) is the high-ROI target: 13 models share a single preprocessor bug (`process_conditionals` eating the `solve` statement after a `$if set workSpace` directive) — fix effort ~2–3h.

### Verification

```bash
ls docs/planning/EPIC_4/SPRINT_20/TRANSLATE_ERROR_AUDIT.md
grep -c "^|" docs/planning/EPIC_4/SPRINT_20/TRANSLATE_ERROR_AUDIT.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_20/TRANSLATE_ERROR_AUDIT.md` — per-model root cause table for all translate failures; model_no_objective_def pattern analysis
- Count of Sprint-20-addressable vs. deferred models
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 7.1, 7.2, 8.1

### Acceptance Criteria

- [x] Current translate internal_error count confirmed (2, not 5; stale JSON corrected)
- [x] Each failing model has: stack trace excerpt, root cause category, fixability assessment
- [x] IndexOffset-related errors separated (none — no IndexOffset translate errors)
- [x] Sprint 20 addressable count confirmed (0 translate internal errors; PROJECT_PLAN.md corrected)
- [x] At least one fixable model has a specific code pointer (`src/ir/preprocessor.py` `process_conditionals()` for 13 no_objective_def models)
- [x] Unknowns 7.1, 7.2, 8.1 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 6: Investigate Full Pipeline Match Divergence

**Status:** ✅ COMPLETE
**Priority:** High
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 20 Day 1
**Owner:** Development team
**Dependencies:** Task 1
**Unknowns Verified:** 5.1, 5.2, 5.3, 5.4

### Objective

Determine why 16 models solve successfully (PATH model status 1) but fail the full pipeline match check (objective value differs from reference NLP solution), and identify which divergence causes are addressable in Sprint 20.

### Why This Matters

Sprint 20 Priority 5 targets 10+ full pipeline matches (currently 9). With 25 models solving, there are 16 models that solve but don't match. Understanding the breakdown (initialization gap, scaling, tolerance, multiple optima, formulation error) determines whether this is a Sprint 20 win or requires Sprint 21/22 work (PATH consultation, solution forcing). The `.l` initialization emission fix (Priority 1) may resolve several of these automatically.

### Background

Sprint 19 final state:
- **25 models solve** (PATH model status 1 or model_optimal)
- **9 full pipeline matches** (objective value within tolerance of reference)
- **Gap: 16 models** solve but don't match

The 9 matching models: ajax, blend, demo1, himmel11, house, mathopt2, prodmix, rbrock, trnsport

The 16 non-matching models need investigation. Likely causes (from Sprint 19 retrospective):
1. **Missing `.l` initialization** — PATH reaches a local optimum far from the reference solution
2. **Missing `.scale` scaling** — poorly scaled variables cause numerical issues
3. **Multiple optima** — mathematically correct but different optimum found
4. **Solution comparison tolerance** — tolerance too tight for model's numerical precision
5. **KKT formulation error** — model solves but MCP is subtly wrong

### What Needs to Be Done

1. **List the 16 non-matching models** by querying `gamslib_status.json`:
   ```bash
   python -c "
   import json, sys; sys.setrecursionlimit(50000)
   with open('data/gamslib/gamslib_status.json') as f: data = json.load(f)
   # models with solve success but no pipeline match
   "
   ```
2. **For each model, compute the objective value gap:**
   - Reference NLP objective (from GAMS solve)
   - MCP objective at PATH solution
   - Relative gap: `|mcp_obj - nlp_obj| / max(1, |nlp_obj|)`
3. **Classify divergence type** for each model:
   - Small gap (≤1%): tolerance issue → easy fix
   - Large gap, model has `.l` assignments: initialization issue → Fixed by Priority 1
   - Large gap, model uses `.scale`: scaling issue → requires separate fix
   - Large gap, convex problem: potential formulation error → investigate KKT
4. **Document findings** in `docs/planning/EPIC_4/SPRINT_20/PIPELINE_MATCH_ANALYSIS.md`
5. **Identify Sprint 20 wins** — how many could be resolved by `.l` emission alone?

### Changes

- Created `docs/planning/EPIC_4/SPRINT_20/PIPELINE_MATCH_ANALYSIS.md`: 16 non-matching models classified into 4 divergence types with per-model objective gap table, tolerance analysis, `.l`/`.scale` audit, golden-file coverage status, and KKT review candidates
- Updated `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`: Unknowns 5.1, 5.2, 5.3, 5.4 → ✅ VERIFIED

### Result

**16 non-matching models classified** (15 mismatch + 1 comparison error):
- **5 tolerance-too-tight** (chem, dispatch, hhmax, mhw4d, mhw4dx): abs diff 1e-4 to 5e-4; would pass at `rtol=1e-4`
- **2 missing expr-based .l init** (abel, chakra): dropped by IR at `parser.py:3568-3571`
- **5 multiple optima / different local KKT** (alkyl, himmel16, mathopt1, process, trig): `.l` correctly emitted; PATH finds different stationary point
- **3 LP multi-model** (aircraft, apl1p, apl1pca): wrong model selected or multiple solve statements
- **1 obj not tracked** (port): LP model, MCP objective variable not captured

**Predicted matches after `.l` emission fix:** +1 to +2 (9 → 10–11); abel high confidence, chakra medium.

**Tolerance finding:** Raising `rtol` from `1e-6` to `1e-4` would add 5 more matches (→ 14–16 combined, depending on .l fix results).

**No .scale usage** in any of the 16 non-matching models. `.scale` remains Sprint 21+ item.

**Golden-file gap:** None of the 9 currently-matching models have end-to-end test coverage. Regression risk is low but unguarded.

### Verification

```bash
ls docs/planning/EPIC_4/SPRINT_20/PIPELINE_MATCH_ANALYSIS.md
grep -c "^|" docs/planning/EPIC_4/SPRINT_20/PIPELINE_MATCH_ANALYSIS.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_20/PIPELINE_MATCH_ANALYSIS.md` — per-model divergence classification for all 16 non-matching models
- Predicted pipeline match count if `.l` emission is fixed
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 5.1, 5.2, 5.3, 5.4

### Acceptance Criteria

- [x] All 16 non-matching models identified and listed (15 mismatch + 1 comparison error = 16)
- [x] Each model has: objective gap %, divergence type, likely cause
- [x] At least 3 models identified as resolvable in Sprint 20 (5 tolerance + 2 .l init = 7 resolvable)
- [x] Predicted new pipeline match count after `.l` emission fix documented (9 → 10–11)
- [x] Any models with suspiciously large gaps (>100%) flagged for KKT review (abel, himmel16, mathopt1, trig)
- [x] Unknowns 5.1, 5.2, 5.3, 5.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 7: Design Accounting Variable Detection (#764 mexss)

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 20 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 5
**Unknowns Verified:** 2.1, 2.2, 2.3, 2.4

### Objective

Design the algorithm for detecting accounting/auxiliary variables in the IR (variables that should not receive stationarity equations because they are definitional identities, not optimization variables) and evaluate the risk of false positives.

### Why This Matters

Sprint 20 Priority 2 (accounting variable detection, #764 mexss) is rated "medium effort, requires design work first." Getting the design right before implementation prevents a false-positive bug where legitimate optimization variables are incorrectly excluded from the KKT system, producing an under-constrained MCP. The design must be conservative: it is safer to miss an accounting variable (model still infeasible) than to incorrectly exclude an optimization variable (model formulation wrong).

### Background

From `docs/issues/ISSUE_764_mexss-mcp-locally-infeasible-accounting-variables.md`:
> Accounting variables (e.g., `xmarket = sum(p, x(p))`) should not get stationarity equations — they are definitional identities, not optimization variables. Generating stationarity for them produces an over-constrained MCP.

**Proposed heuristic (to be validated):**
A variable `v` is an accounting variable if:
1. `v` appears on the LHS of exactly one equation with `=E=` (equality)
2. `v` does not appear in the objective equation (directly or through a chain)
3. `v`'s equation is of the form `v = f(other_vars)` with no other occurrence of `v` in the RHS

**Risk:** False positives if an equality constraint that looks like an accounting identity is actually a binding constraint that contributes to the optimal solution through dual variables.

### What Needs to Be Done

1. **Study mexss.gms** to understand the actual accounting variable pattern:
   ```bash
   grep -A5 "xmarket\|accounting\|=E=" data/gamslib/raw/mexss.gms | head -40
   ```
2. **Review similar models** — are there other models with the same pattern?
3. **Formalize the detection algorithm:**
   - LHS-only occurrence criterion
   - Objective-reachability criterion (could use the existing dependency graph)
   - Equality-only criterion
4. **Assess false positive risk** on the 25 currently-solving models — would any be incorrectly classified?
5. **Consider conservative vs. aggressive heuristic:**
   - Conservative: only detect if ALL three criteria are met
   - Aggressive: detect if any two are met
6. **Document design** in `docs/planning/EPIC_4/SPRINT_20/ACCOUNTING_VAR_DETECTION_DESIGN.md`

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
ls docs/planning/EPIC_4/SPRINT_20/ACCOUNTING_VAR_DETECTION_DESIGN.md
grep "Algorithm\|False Positive\|Criterion" docs/planning/EPIC_4/SPRINT_20/ACCOUNTING_VAR_DETECTION_DESIGN.md | wc -l
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_20/ACCOUNTING_VAR_DETECTION_DESIGN.md` — algorithm design, false positive risk assessment, and recommended implementation location
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.1, 2.2, 2.3, 2.4

### Acceptance Criteria

- [ ] mexss accounting variable pattern fully characterized
- [ ] Detection algorithm formalized with 3+ criteria
- [ ] False positive risk assessed on ≥3 currently-solving models
- [ ] Implementation location identified (file + function)
- [ ] Conservative vs. aggressive heuristic recommendation made
- [ ] Expected impact confirmed: mexss unblocked, no currently-solving models broken
- [ ] Unknowns 2.1, 2.2, 2.3, 2.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 8: Review Sprint 19 Retrospective Action Items

**Status:** ✅ COMPLETE
**Priority:** Medium
**Estimated Time:** 1 hour
**Deadline:** Before Sprint 20 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** 3.1, 3.2 (partial)

### Objective

Review `docs/planning/EPIC_4/SPRINT_19/SPRINT_RETROSPECTIVE.md` "What Could Be Improved" section and ensure all process recommendations are captured as Sprint 20 setup actions or in the Known Unknowns list.

### Why This Matters

The retrospective identified 6 improvement areas. Some (like the smoke-test lesson and denominator tracking) are process changes that need to be operationalized before Day 1, not just documented. Failing to act on retrospective items means repeating the same mistakes.

### Background

Sprint 19 "What Could Be Improved" items (from retrospective):
1. Full pipeline match target missed — set conservative targets, track "within ε" as leading indicator
2. `lop` exclusion not documented — document denominator changes with dated sprint log entry
3. Day 13 validation exposed 5 issues late — run model validation earlier (Day 10–11)
4. `#671` premature "not fixable" assessment — smoke test before declaring
5. Parse rate denominator confusion — use `gamslib_status.json` count directly
6. Deferred issues accumulating — consider a dedicated "solver quality" sprint

### What Needs to Be Done

1. **Read the full "What Could Be Improved" section** of the Sprint 19 retrospective
2. **For each item, create a concrete action:**
   - Item 1: Add "models within ε of reference solution" as a tracked metric in Sprint 20
   - Item 2: Add denominator-change documentation to Sprint 20 sprint log template
   - Item 3: Schedule model validation for Sprint 20 Day 10–11
   - Item 4: Add smoke-test checklist to "declaring not fixable" process
   - Item 5: Add automated baseline snapshot script invocation to sprint start
   - Item 6: Note for PROJECT_PLAN.md Epic 4 planning
3. **Verify** the Sprint 20 PREP_PLAN and PLAN.md incorporate these actions
4. **Note any unresolved retrospective items** in KNOWN_UNKNOWNS.md

### Changes

- Updated `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md`: Unknowns 3.1, 3.2 → ⚠️ PARTIAL with findings from chenery issue file and AD derivative_rules.py grep

### Result

All 6 Sprint 19 retrospective "What Could Be Improved" items reviewed and actioned. Concrete actions assigned and homes identified:

1. **Full pipeline match target missed** → Sprint 20 PLAN.md (Task 10) to include "models within 1% of reference objective" as a tracked leading indicator alongside full pipeline match
2. **`lop` model exclusion undocumented** → Sprint 20 SPRINT_LOG.md template (Task 10) to include a denominator-change log section; any exclusion must be recorded with date and reason on the day of exclusion
3. **Day 13 validation too late** → Sprint 20 PLAN.md (Task 10) to schedule model validation run on Day 10–11 (two days before sprint close), giving buffer for newly-discovered issues
4. **`#671` premature "not fixable" assessment** → Sprint 20 PLAN.md (Task 10) process note: always run `python -m src.cli <model>` before declaring an issue not fixable; 30-second smoke test prevents false negatives
5. **Parse rate denominator confusion** → Sprint 20 baseline snapshot (Task 9) pins the denominator from `gamslib_status.json` at sprint start; Task 9 captures this count explicitly
6. **Deferred issues accumulating** → PROJECT_PLAN.md Epic 4 already has capacity for a "solver quality" workstream; noted for consideration when planning Sprint 21/22; defer decision to Task 10

Unknowns 3.1 and 3.2 partially verified from issue file and source code inspection:
- **3.1 PARTIAL:** `$` condition in chenery is equation-level (`dvv(i)$(sig(i) <> 0)..`), not inline — the easier case; EXECERROR=1 confirmed from issue file
- **3.2 PARTIAL:** AD system has `_diff_dollar_conditional` (line 154, derivative_rules.py) for expression-level conditions; gap is that equation-level `EquationDef.condition` is not inherited as a guard in the generated stationarity sum — extension of existing code, not a new IR node type

### Verification

```bash
# Verify that each retrospective item has an action captured somewhere
grep -l "smoke.test\|denominator\|validation.*Day 10\|ε.*reference" docs/planning/EPIC_4/SPRINT_20/ 2>/dev/null
```

### Deliverables

- Action items from Sprint 19 retrospective captured in Sprint 20 planning documents (Task 10 PLAN.md)
- Updated KNOWN_UNKNOWNS.md: Unknowns 3.1, 3.2 → ⚠️ PARTIAL

### Acceptance Criteria

- [x] All 6 "What Could Be Improved" items reviewed
- [x] Each item has a concrete action assigned (not just acknowledged)
- [x] At least 3 actions incorporated into Sprint 20 PLAN.md or this PREP_PLAN (items 1–5 all feed into Task 10 PLAN.md / Task 9 baseline)
- [x] Smoke-test checklist created or referenced for "not fixable" declarations (item 4: always run CLI smoke test; 30-second check)
- [x] Unknowns 3.1, 3.2 partially verified and updated in KNOWN_UNKNOWNS.md

---

## Task 9: Snapshot Baseline Metrics

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 1 hour
**Deadline:** Before Sprint 20 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** 4.2 (confirms 27 count)

### Objective

Run the full pipeline on all models and record the exact baseline metrics for Sprint 20, pinning the denominator and per-category counts to a timestamped snapshot. This prevents the denominator confusion that affected Sprint 19 metrics.

### Why This Matters

Sprint 19 retrospective explicitly called out "parse rate denominator confusion" as a process failure: the sprint baseline was recorded as "61/159" when the correct tested count was 160. In Sprint 20, the baseline must be pinned to a specific snapshot of `gamslib_status.json` taken at sprint start, with an explicit record of any excluded models and why.

### Background

Sprint 19 final state:
- 107/160 tested models parse (66.9%)
- 73 translate successfully
- 25 solve (PATH model status 1)
- 9 full pipeline match
- 27 lexer_invalid_char
- 6 internal_error (pipeline)
- 3,579 tests

Any changes made during prep tasks (if any code changes are made) could shift these numbers. The snapshot must be taken after all prep work is complete and before Sprint 20 Day 1 begins.

### What Needs to Be Done

1. **Ensure main branch is clean** and all tests pass:
   ```bash
   make test
   ```
2. **Run the full pipeline retest**:
   ```bash
   .venv/bin/python scripts/gamslib/run_full_test.py --quiet
   ```
3. **Record key metrics** in `docs/planning/EPIC_4/SPRINT_20/BASELINE_METRICS.md`:
   - Parse: N/M tested (X%)
   - lexer_invalid_char: N
   - internal_error (pipeline): N
   - Translate success: N
   - Solve success: N
   - Full pipeline match: N
   - Test count: N
   - Excluded models: list with reason
4. **Timestamp the snapshot** with the date and git commit hash
5. **Record the denominator explicitly**: "M models tested = total catalog (219) minus N untested (compilation errors, license limits, etc.)"

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
ls docs/planning/EPIC_4/SPRINT_20/BASELINE_METRICS.md
grep "Parse\|Translate\|Solve\|Test count\|Baseline date" docs/planning/EPIC_4/SPRINT_20/BASELINE_METRICS.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_20/BASELINE_METRICS.md` — timestamped snapshot of all pipeline metrics with explicit denominator documentation
- Updated KNOWN_UNKNOWNS.md Unknown 4.2 verified (confirms 27 lexer_invalid_char count)

### Acceptance Criteria

- [ ] Full pipeline retest completed after all code-impacting prep tasks
- [ ] Baseline metrics recorded with date and git commit SHA
- [ ] Denominator explicitly documented (tested count and excluded count, with reasons)
- [ ] Metrics match Sprint 19 final state (or discrepancy explained)
- [ ] All excluded models listed individually with exclusion reason
- [ ] Unknown 4.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 10: Plan Sprint 20 Detailed Schedule

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 20 Day 1
**Owner:** Development team
**Dependencies:** All other tasks
**Unknowns Verified:** Integrates all verified unknowns from Tasks 2–9

### Objective

Create `docs/planning/EPIC_4/SPRINT_20/PLAN.md` with a day-by-day schedule for Sprint 20, incorporating the findings from Tasks 1–9, revised effort estimates, checkpoint criteria, and explicit acceptance criteria for each workstream.

### Why This Matters

Sprint 19's plan was revised significantly from the original PROJECT_PLAN.md because prep work revealed that several items had changed scope (IndexOffset already partially done, ISSUE_670 required staged delivery). Sprint 20's PROJECT_PLAN.md estimates are based on pre-Sprint-19 information. After Tasks 1–9, we will have precise current-state information to build an accurate, achievable sprint plan.

### Background

PROJECT_PLAN.md Sprint 20 scope (before prep revisions):
- IndexOffset implementation: 14–16h (likely reduced to ~4–6h after Task 2 audit)
- Translation internal error fixes: 6–8h (count TBD after Task 5 audit)
- Objective extraction enhancement: 4h
- Sprint 19 deferred items (5 priorities): ~24–34h total
- **Total PROJECT_PLAN.md estimate:** 26–30h + 24–34h = ~50–64h

This is likely a 2-week sprint (Weeks 5–6, ~15 working days). The actual scope must be right-sized based on prep task findings.

### What Needs to Be Done

1. **Aggregate findings from Tasks 1–9:**
   - Revised effort estimates from Tasks 2, 4, 5, 7
   - Updated model counts from Tasks 3, 5, 6
   - Process actions from Task 8
   - Baseline from Task 9
2. **Define sprint workstreams and day assignments:**
   - Day 0: baseline + sprint start
   - Days 1–3: highest-priority fixes (`.l` emission, IndexOffset gaps)
   - Days 4–6: accounting variable detection, translate errors
   - Days 7–9: lexer_invalid_char remaining subcategories
   - Days 10–11: model validation run (lesson from Sprint 19 retrospective)
   - Days 12–13: full pipeline match investigation, tolerance adjustments
   - Day 14: sprint close, retrospective
3. **Define two checkpoints:**
   - Checkpoint 1 (Day 6): `.l` emission + IndexOffset complete, solve rate target on track
   - Checkpoint 2 (Day 11): lexer fixes complete, model validation done, GO/NO-GO for remaining workstreams
4. **Set acceptance criteria** for each workstream (specific numbers, not vague targets)
5. **Identify risks and contingencies** based on KNOWN_UNKNOWNS findings
6. **Create PLAN.md** following the format of `docs/planning/EPIC_4/SPRINT_19/PLAN.md`

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
ls docs/planning/EPIC_4/SPRINT_20/PLAN.md
# Should have Day 0 through Day 14 sections
grep -c "^## Day" docs/planning/EPIC_4/SPRINT_20/PLAN.md
grep "Checkpoint" docs/planning/EPIC_4/SPRINT_20/PLAN.md | wc -l
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_20/PLAN.md` — complete day-by-day Sprint 20 plan with checkpoints, acceptance criteria, and contingencies
- Revised effort estimate for each workstream based on prep task findings
- KNOWN_UNKNOWNS.md verification status reviewed and any remaining INCOMPLETE items flagged

### Acceptance Criteria

- [ ] PLAN.md covers Day 0 through Day 14
- [ ] Each workstream has specific acceptance criteria (numbers, not vague)
- [ ] Two checkpoints defined with GO/NO-GO criteria
- [ ] Effort estimates revised from PROJECT_PLAN.md based on Tasks 2–7 findings
- [ ] At least 2 contingency plans documented (scope reduction if behind schedule)
- [ ] Sprint 19 retrospective process improvements incorporated
- [ ] All KNOWN_UNKNOWNS verified/flagged — no INCOMPLETE unknowns remain unaddressed

---

## Summary

### Success Criteria for Prep Phase

All of the following must be true before Sprint 20 Day 1 begins:

1. **KNOWN_UNKNOWNS.md exists** with 15+ unknowns, all Critical/High unknowns have verification plans
2. **IndexOffset audit complete** — exact failure count and remaining effort known
3. **lexer_invalid_char catalog updated** — 27 models rechecked, top subcategories ranked by ROI
4. **`.l` emission design complete** — fix location and strategy documented, circle/bearing impact confirmed
5. **Translate internal errors audited** — current count confirmed, root causes classified
6. **Pipeline match gap analyzed** — 16 non-matching models classified by divergence type
7. **Accounting variable detection designed** — algorithm formalized, false positive risk assessed
8. **Sprint 19 retrospective actions captured** — all 6 items have concrete actions
9. **Baseline metrics snapshotted** — timestamped, denominator explicit
10. **PLAN.md complete** — day-by-day schedule with checkpoints and revised effort estimates

### Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| IndexOffset audit reveals new parser gap | Medium | Medium | Allocate 2h buffer in Days 1–3 |
| `.l` emission doesn't resolve circle/bearing | Medium | Medium | Document as "initialization insufficient"; escalate to scaling/warm-start |
| Accounting variable heuristic has false positives | Low | High | Test against all 25 solving models before enabling |
| lexer_invalid_char subcategories G–K are all preprocessor-required | Low | Medium | Pivot budget to translate errors or pipeline match |
| Prep tasks take longer than 3–4 days | Low | Low | Tasks 3, 6, 7 can be deferred to Day 0–1 of Sprint 20 |

---

## Appendix: Document Cross-References

### Sprint 20 Planning Documents

| Document | Location | Purpose |
|----------|----------|---------|
| Epic 4 Goals | `docs/planning/EPIC_4/GOALS.md` | Overall epic objectives and KPIs |
| Epic 4 Project Plan | `docs/planning/EPIC_4/PROJECT_PLAN.md` | Sprint 20 scope (lines 268–385) |
| Sprint 19 Retrospective | `docs/planning/EPIC_4/SPRINT_19/SPRINT_RETROSPECTIVE.md` | Process improvements and lessons |
| Sprint 19 Plan | `docs/planning/EPIC_4/SPRINT_19/PLAN.md` | PLAN.md format reference |
| Sprint 19 Sprint Log | `docs/planning/EPIC_4/SPRINT_19/SPRINT_LOG.md` | SPRINT_LOG.md format reference |

### Research Documents

| Document | Location | Relevant To |
|----------|----------|-------------|
| IndexOffset Design | `docs/planning/EPIC_4/SPRINT_19/INDEX_OFFSET_DESIGN_OPTIONS.md` | Task 2 |
| Lexer Error Catalog | `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` | Task 3 |
| Internal Error Analysis | `docs/planning/EPIC_4/SPRINT_19/INTERNAL_ERROR_ANALYSIS_PREP.md` | Task 5 |
| Min/Max Reformulation | `docs/research/minmax_objective_reformulation.md` | Issue #789 |
| Multidimensional Indexing | `docs/research/multidimensional_indexing.md` | Task 2 |

### Open Issue Documents (Deferred from Sprint 19)

| Issue | File | Task |
|-------|------|------|
| #753 circle (.l init) | `docs/issues/ISSUE_753_circle-mcp-locally-infeasible.md` | Task 4 |
| #757 bearing (.l + .scale) | `docs/issues/ISSUE_757_bearing-mcp-locally-infeasible.md` | Task 4 |
| #763 chenery (AD condition) | `docs/issues/ISSUE_763_chenery-mcp-division-by-zero-del-parameter.md` | Task 1 |
| #764 mexss (accounting vars) | `docs/issues/ISSUE_764_mexss-mcp-locally-infeasible-accounting-variables.md` | Task 7 |
| #765 orani (exogenous vars) | `docs/issues/ISSUE_765_orani-mcp-locally-infeasible-fixed-variables-exogenous.md` | Task 1 |
| #789 min/max (math infeasible) | `docs/issues/ISSUE_789_minmax-reformulation-spurious-variables.md` | Task 1 |
