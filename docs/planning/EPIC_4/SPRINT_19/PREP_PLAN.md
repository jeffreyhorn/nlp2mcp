# Sprint 19 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 19 begins
**Timeline:** Complete before Sprint 19 Day 1
**Goal:** Prepare for Major Parse Push (lexer_invalid_char & internal_error), Sprint 18 Deferred Items, and architectural issue resolution (ISSUE_670, ISSUE_392, ISSUE_399, ISSUE_672)

**Key Context from Sprint 18 (v1.2.0):** Baseline metrics — Parse 62/160 (38.8%), Translate 48/62, Solve 20/48 (was 12), Full Pipeline 7/160 (was 4). Sprint 18 reduced path_syntax_error from 22 to 7 via emission-layer fixes. Remaining blockers are architectural (cross-indexed sums, table parsing, MCP pairing) and require parser/KKT changes.

---

## Executive Summary

Sprint 19 is the largest sprint in Epic 4, combining four major workstreams totaling 43-53 hours:

1. **Sprint 18 Deferred Items (~17-21h):** MCP infeasibility bug fixes, subset relationship preservation, reserved word quoting, lexer error deep analysis, put statement format support
2. **lexer_invalid_char Fixes (~14-18h):** Complex set data syntax, compile-time constants in ranges, remaining high-priority clusters
3. **internal_error Investigation (~6-8h):** Error classification and initial fixes for 23 internal_error models
4. **IndexOffset IR Design (~4h):** Design and prototype lead/lag indexing support

Additionally, the FIX_ROADMAP.md from Sprint 18 Day 11 identifies four architectural issues (ISSUE_670 cross-indexed sums, ISSUE_392 table continuation, ISSUE_399 table description, ISSUE_672 MCP pairing) that block 10 models. These overlap with several Sprint 19 components and must be integrated into planning.

This prep plan focuses on research, analysis, and setup tasks that must be completed before Sprint 19 Day 1 to prevent blocking issues and ensure smooth execution.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Unknowns Verified | Sprint 19 Component Addressed |
|---|------|----------|-----------|--------------|-------------------|-------------------------------|
| 1 | Create Sprint 19 Known Unknowns List | Critical | 3-4h | None | — | All components — proactive unknown identification |
| 2 | Classify internal_error Failure Modes | Critical | 3-4h | None | 7.1, 7.2 | internal_error Investigation — scope before implementing |
| 3 | Catalog lexer_invalid_char Subcategories | Critical | 3-4h | None | 4.1, 4.2, 4.3, 6.1, 6.4 | lexer_invalid_char Fixes — prioritize grammar work |
| 4 | Analyze Cross-Indexed Sum Patterns (ISSUE_670) | Critical | 3-4h | None | 8.1, 8.2 | FIX_ROADMAP P1 — design stationarity fix |
| 5 | Audit Sprint 18 Deferred Item Readiness | High | 2-3h | None | 1.1-1.3, 2.1-2.3, 3.1-3.3, 4.3, 5.1-5.2 | Sprint 18 Deferred Items — verify prerequisites |
| 6 | Research IndexOffset IR Design Options | High | 2-3h | None | 7.3, 7.4 | IndexOffset IR Design — evaluate approaches |
| 7 | Analyze Table Parsing Issues (ISSUE_392, ISSUE_399) | High | 2-3h | None | 8.3 | FIX_ROADMAP P2-P3 — understand grammar gaps |
| 8 | Analyze MCP Pairing Issues (ISSUE_672) | Medium | 2-3h | None | 8.4 | FIX_ROADMAP P4 — understand bound edge cases |
| 9 | Verify Sprint 19 Baseline Metrics | High | 1-2h | None | 4.1, 6.4 | All — ensure v1.2.0 baseline is accurate |
| 10 | Plan Sprint 19 Detailed Schedule | Critical | 3-4h | All tasks | All | Sprint 19 planning |

**Total Estimated Time:** ~27h (P50), with a working range of 24-32h (~3-4 working days)

**Critical Path:** Tasks 1 → 2/3/4 (parallel research) → 10 (planning)

---

## Task 1: Create Sprint 19 Known Unknowns List

**Status:** ✅ **COMPLETED** (February 12, 2026)
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 19 Day 1
**Owner:** Development team
**Dependencies:** None

### Objective

Create a comprehensive list of assumptions and unknowns for Sprint 19 to prevent late-discovery issues. This continues the Known Unknowns practice that achieved high ratings in Sprint 18 (24 unknowns documented upfront; all critical/high items verified before implementation; zero late surprises).

### Why This Matters

Sprint 19 is the most complex sprint in Epic 4, combining deferred items, parser work, error investigation, and IR design. Each workstream carries assumptions about GAMS behavior, grammar structure, and code architecture that could derail the sprint if discovered late. Sprint 18 retrospective rated the Known Unknowns process as a top success factor.

### Background

- Sprint 18 Known Unknowns: `docs/planning/EPIC_4/SPRINT_18/KNOWN_UNKNOWNS.md` (24 unknowns, 4 categories)
- Sprint 18 retrospective: Known Unknowns process rated highly; all critical/high items verified before implementation
- Sprint 19 scope from `docs/planning/EPIC_4/PROJECT_PLAN.md` lines 147-264
- FIX_ROADMAP: `docs/planning/EPIC_4/SPRINT_18/FIX_ROADMAP.md` (5 priority items)

### What Needs to Be Done

1. Review Sprint 19 scope in PROJECT_PLAN.md (all 5 components)
2. Review FIX_ROADMAP.md for architectural issue unknowns
3. For each component, brainstorm unknowns across these categories:
   - **Category 1: Grammar & Parser Unknowns** (lexer_invalid_char, internal_error, table parsing)
   - **Category 2: KKT & Stationarity Unknowns** (cross-indexed sums, MCP pairing)
   - **Category 3: Sprint 18 Deferred Item Unknowns** (MCP bugs, subset preservation, reserved words)
   - **Category 4: IR Design Unknowns** (IndexOffset representation, lead/lag semantics)
   - **Category 5: Integration & Regression Unknowns** (test stability, pipeline interactions)
4. Prioritize each unknown (Critical/High/Medium/Low)
5. Define verification method and deadline for each
6. Create document following Sprint 18 KNOWN_UNKNOWNS.md format

### Changes

Created `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` with 26 unknowns across 8 categories:
- Category 1: MCP Infeasibility Bug Fixes (3 unknowns)
- Category 2: Subset Relationship Preservation (3 unknowns)
- Category 3: Reserved Word Quoting (3 unknowns)
- Category 4: Lexer Error Deep Analysis (3 unknowns)
- Category 5: Put Statement Format Support (2 unknowns)
- Category 6: Complex Set Data Syntax (4 unknowns)
- Category 7: internal_error & IndexOffset (4 unknowns)
- Category 8: Cross-Indexed Sums & Architectural Issues (4 unknowns)

### Result

**26 unknowns** documented with priority distribution: 8 Critical, 13 High, 5 Medium, 0 Low. Estimated research time: 30-38 hours. Task-to-Unknown mapping table created linking each prep task (2-10) to the unknowns it verifies.

### Verification

```bash
# Verify document exists and has expected structure
cat docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md | head -5
# Should show title and metadata

# Count unknowns
grep -c "^## Unknown" docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md
# Target: 25+ unknowns across 8 categories
```

### Deliverables

- ✅ `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` with 26 unknowns across 8 categories
- ✅ All unknowns have assumption, verification method, priority, and research time estimate
- ✅ Verification plan for all Critical/High unknowns
- ✅ Task-to-Unknown mapping table in appendix

### Acceptance Criteria

- [x] Document created with 26 unknowns across 8 categories (exceeds 25+ target)
- [x] All unknowns have assumption, verification method, priority
- [x] All Critical/High unknowns have verification plan
- [x] Unknowns cover all Sprint 19 components (deferred items, lexer, internal_error, IndexOffset, FIX_ROADMAP items)
- [x] Template for mid-sprint updates defined

---

## Task 2: Classify internal_error Failure Modes

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 19 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** 7.1, 7.2

### Objective

Run all 23 `internal_error` models with debug parser output to classify failure modes before Sprint 19 implementation. This directly feeds the "internal_error Investigation" component (6-8h in sprint).

### Why This Matters

Sprint 19 targets reducing internal_error from 23 to below 15. Without upfront classification, the sprint would spend 4-5 hours on Day 1 just understanding the problem space, leaving insufficient time for fixes. Pre-classifying failures allows Sprint 19 to jump straight into implementation.

### Background

- internal_error models: 23 models fail during parsing with internal errors
- Per PROJECT_PLAN.md, these need classification into: grammar ambiguity, missing production, IR construction crash, transformer error
- Sprint 18 focused on emission-layer fixes and deferred all parser work
- Research context: `docs/research/gamslib_parse_errors.md` (Sprint 6 parse error analysis), `docs/research/preprocessor_directives.md` (GAMS preprocessor handling)

### What Needs to Be Done

1. Identify all 23 internal_error models from pipeline results database
2. Run each model with verbose/debug parser output
3. Capture and categorize each error:
   - **Grammar ambiguity:** Multiple parse paths, unexpected token resolution
   - **Missing production:** Syntax construct not in grammar
   - **IR construction crash:** Parser succeeds but IR transformer fails
   - **Transformer error:** Semantic analysis failure during tree transformation
4. Group models by root cause pattern
5. Identify which patterns are quickest to fix (low-hanging fruit)
6. Estimate effort per pattern group
7. Document findings in analysis report

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Verify analysis document exists
test -f docs/planning/EPIC_4/SPRINT_19/INTERNAL_ERROR_ANALYSIS_PREP.md && echo "EXISTS" || echo "MISSING"

# Verify all 23 models were analyzed
grep -c "^|" docs/planning/EPIC_4/SPRINT_19/INTERNAL_ERROR_ANALYSIS_PREP.md
# Should show 23+ rows (header + models)
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_19/INTERNAL_ERROR_ANALYSIS_PREP.md` with classification of all 23 models
- Error category distribution (count per category)
- Recommended fix order (easiest/highest-ROI first)
- Effort estimates per category
- Unknowns 7.1, 7.2 verified with findings documented

### Acceptance Criteria

- [ ] All 23 internal_error models run with debug output
- [ ] Each model classified into one of: grammar ambiguity, missing production, IR crash, transformer error
- [ ] Models grouped by root cause pattern
- [ ] Fix priority order defined (ROI-based)
- [ ] Effort estimates per pattern group documented
- [ ] Top 8+ "quickest to fix" models identified (to hit <15 target)
- [ ] Unknowns 7.1, 7.2 verified and documented in KNOWN_UNKNOWNS.md

---

## Task 3: Catalog lexer_invalid_char Subcategories

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 19 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** 4.1, 4.2, 4.3, 6.1, 6.4

### Objective

Fully subcategorize the ~95 lexer_invalid_char failures to prioritize grammar work for Sprint 19. This feeds the "lexer_invalid_char Fixes" component (14-18h in sprint) and the deferred "Lexer Error Deep Analysis" item (5-6h).

### Why This Matters

Sprint 19 targets reducing lexer_invalid_char from ~95 to below 50. The PROJECT_PLAN.md identifies three subcategories (complex set data, compile-time constants, remaining clusters), but Sprint 18 only performed initial analysis. A complete subcategorization is needed to correctly scope grammar changes and avoid wasted effort on low-ROI fixes.

### Background

- Sprint 18 initial analysis: `docs/planning/EPIC_4/SPRINT_18/SPRINT_LOG.md` (Days 4-5 path_syntax_error deep dive methodology, applicable here)
- Prior parse error research: `docs/research/gamslib_parse_errors.md`, `docs/research/gamslib_parse_errors_preliminary.md`
- PROJECT_PLAN.md estimates: Complex set data (8-10h, 14+ models), Compile-time constants (3-4h), Remaining clusters (3-4h)
- Grammar file: `src/gams/gams_grammar.lark`
- Sprint 18 GOALS.md context: "Eliminate lexer_invalid_char Errors" — reduce 74 lexer errors (baseline may have shifted)

### What Needs to Be Done

1. Query pipeline results to get current list of all lexer_invalid_char models
2. Run each model with verbose lexer output to capture exact error location
3. Extract the character/token causing the lexer failure
4. Group by failure pattern:
   - **Complex set data syntax** (multi-dimensional assignments, compound operations)
   - **Compile-time constants** (`1*card(s)`, `ord(s)` in ranges)
   - **Dollar control options** (`$ontext/$offtext`, `$if`, `$setglobal`)
   - **Put/display statements** (format specifiers, output routing)
   - **Semicolon/continuation issues** (missing terminators, line continuation)
   - **Other/novel** (patterns not previously identified)
5. Count models per subcategory
6. Cross-reference with PROJECT_PLAN.md estimates — validate or correct
7. Identify which subcategories are addressable with grammar-only changes vs. requiring preprocessor support
8. Prioritize by model count and implementation feasibility

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Verify catalog document exists
test -f docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md && echo "EXISTS" || echo "MISSING"

# Verify model count matches expected
grep -c "lexer_invalid_char" docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md
# Should be ~95 or current count
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` with full subcategorization
- Model count per subcategory (validated against PROJECT_PLAN.md estimates)
- Grammar-change-feasibility assessment per subcategory
- Recommended implementation order for Sprint 19
- Unknowns 4.1, 4.2, 4.3, 6.1, 6.4 verified with findings documented

### Acceptance Criteria

- [ ] All lexer_invalid_char models cataloged with exact error location
- [ ] Models grouped into 5+ subcategories with counts
- [ ] PROJECT_PLAN.md estimates validated or corrected
- [ ] Grammar-only vs. preprocessor-required distinction made
- [ ] Implementation order recommended (highest ROI first)
- [ ] Total addressable count estimated (to validate <50 target)
- [ ] Unknowns 4.1, 4.2, 4.3, 6.1, 6.4 verified and documented in KNOWN_UNKNOWNS.md

---

## Task 4: Analyze Cross-Indexed Sum Patterns (ISSUE_670)

**Status:** ✅ **COMPLETED** (February 13, 2026)
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 19 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** 8.1, 8.2

### Objective

Deeply analyze the cross-indexed sum problem in KKT stationarity equations to produce a concrete fix design before Sprint 19 implementation. This is the highest-ROI item from the FIX_ROADMAP (6 models blocked, P1 priority).

### Why This Matters

ISSUE_670 blocks 6 models (abel, qabel, chenery, mexss, orani, robert-secondary). The FIX_ROADMAP estimates 8-16 hours of implementation effort. Without a pre-sprint design, the risk of mid-sprint redesign is high. Sprint 18 retrospective noted that "Cross-indexed sums (ISSUE_670) are a significant architectural barrier affecting 6 models; requires parser/KKT redesign."

### Background

- FIX_ROADMAP: `docs/planning/EPIC_4/SPRINT_18/FIX_ROADMAP.md` (Priority 1 section)
- Sprint 18 Day 8 investigation: SPRINT_LOG.md documented the pattern — GAMS Error 149 "Uncontrolled set entered as constant"
- KKT stationarity code: `src/kkt/stationarity.py`, `src/kkt/assemble.py`
- Expression-to-GAMS converter: `src/emit/expr_to_gams.py` (already has index aliasing for GAMS Error 125)
- Related research: `docs/research/multidimensional_indexing.md`, `docs/research/nested_subset_indexing_research.md`

### What Needs to Be Done

1. Read `src/kkt/stationarity.py` and trace how stationarity equations are built
2. For each of the 6 affected models, extract the specific constraint causing ISSUE_670:
   - What is the original constraint structure?
   - What does the differentiated stationarity equation look like?
   - Which index becomes "uncontrolled"?
3. Identify the common pattern across all 6 models
4. Design the fix:
   - Option A: Wrap uncontrolled indices in sum expressions during stationarity generation
   - Option B: Add index scoping metadata to the IR during differentiation
   - Option C: Post-process stationarity equations to detect and fix uncontrolled indices
5. Evaluate each option for:
   - Implementation complexity
   - Risk of regression
   - Compatibility with existing index aliasing in `expr_to_gams.py`
6. Recommend preferred approach with implementation sketch
7. Define test strategy (unit tests + model validation)

### Changes

Created `docs/planning/EPIC_4/SPRINT_19/ISSUE_670_DESIGN.md` with complete fix design for the cross-indexed sum problem. Key changes:
- Analyzed all 6 affected models with specific constraint patterns and uncontrolled indices documented
- Traced the exact code path in `src/kkt/stationarity.py` that produces uncontrolled indices
- Identified two sub-problems: wrong index replacement in `_replace_matching_indices()` and missing free index detection in `_add_indexed_jacobian_terms()`
- Evaluated 3 fix options (A: post-replacement free index analysis, B: fix index replacement, C: post-process at emission)
- Recommended Option A with implementation sketch and test strategy
- Updated Unknowns 8.1, 8.2 in `KNOWN_UNKNOWNS.md` with verification results

### Result

**All 6 models share the same fundamental pattern:** a constraint `eq(d)` containing `sum(s, f(d,s)*x(s,v))` produces a derivative term where indices in `var_domain ∪ mult_domain` (often including `d`) are controlled, but the derivative can introduce additional indices not in either domain (typically the original summation index or a mismatched subset/superset index) that remain uncontrolled in `stat_x(v)`.

**Root cause:** `_add_indexed_jacobian_terms()` in `stationarity.py` wraps terms in sums based only on multiplier domain vs. variable domain. It does not analyze free indices in the derivative expression itself.

**Recommended fix (Option A):** Add `_collect_free_indices()` utility that walks the derivative expression tree, then wrap any indices not in `var_domain | mult_domain` in appropriate sums. Localized to `stationarity.py`, compatible with existing `expr_to_gams.py` index aliasing, low regression risk.

**Effort estimate refined:** 10-14 hours (from 8-16h). Single-module fix, no AD/parser/emit changes needed.

### Verification

```bash
# Verify design document exists
test -f docs/planning/EPIC_4/SPRINT_19/ISSUE_670_DESIGN.md && echo "EXISTS" || echo "MISSING"

# Verify all 6 models are covered
grep -c "abel\|qabel\|chenery\|mexss\|orani\|robert" docs/planning/EPIC_4/SPRINT_19/ISSUE_670_DESIGN.md
# Should show 6+ mentions
```

### Deliverables

- ✅ `docs/planning/EPIC_4/SPRINT_19/ISSUE_670_DESIGN.md` with fix design (3 options evaluated, Option A recommended)
- ✅ Per-model analysis of the cross-indexed sum pattern (all 6 models with constraint excerpts, uncontrolled indices)
- ✅ Recommended fix approach with implementation sketch (`_collect_free_indices()` + sum wrapping)
- ✅ Test strategy (unit tests for `_collect_free_indices()`, integration tests for 6 models, regression suite)
- ✅ Effort estimate refined from 8-16h to 10-14h
- ✅ Unknowns 8.1, 8.2 verified with findings documented in KNOWN_UNKNOWNS.md

### Acceptance Criteria

- [x] All 6 affected models analyzed with specific constraint patterns documented
- [x] Common cross-indexed sum pattern identified and described
- [x] At least 2 fix approaches evaluated with pros/cons
- [x] Preferred approach recommended with implementation sketch
- [x] Compatibility with existing expr_to_gams.py index aliasing assessed
- [x] Test strategy defined (unit tests + 6-model validation)
- [x] Effort estimate refined from 8-16h range
- [x] Unknowns 8.1, 8.2 verified and documented in KNOWN_UNKNOWNS.md

---

## Task 5: Audit Sprint 18 Deferred Item Readiness

**Status:** ✅ **COMPLETED** (February 13, 2026)
**Priority:** High
**Estimated Time:** 2-3 hours
**Deadline:** Before Sprint 19 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.3, 5.1, 5.2

### Objective

Verify that all 5 Sprint 18 deferred items have sufficient context, code pointers, and test plans for efficient Sprint 19 implementation. Ensure no prerequisites are missing.

### Why This Matters

Sprint 18 deferred 5 items (~17-21h) when architectural limitations were discovered and the sprint pivoted to emission fixes. These items were documented at varying levels of detail. Some may have stale code references or missing context after Sprint 18 code changes. Auditing now prevents "where was this again?" delays during Sprint 19.

### Background

- PROJECT_PLAN.md Sprint 18 Deferred Items section (lines 155-188)
- Sprint 18 SPRINT_LOG.md documents when and why each item was deferred
- Sprint 18 research docs: `docs/planning/EPIC_4/SPRINT_18/PUT_FORMAT_ANALYSIS.md`, `docs/planning/EPIC_4/SPRINT_18/TABLE_DATA_ANALYSIS.md`, `docs/planning/EPIC_4/SPRINT_18/COMPUTED_PARAM_ANALYSIS.md`
- Source files: `src/emit/emit_gams.py`, `src/emit/model.py`, `src/emit/expr_to_gams.py`, `src/gams/gams_grammar.lark`

### What Needs to Be Done

For each of the 5 deferred items, verify:

#### Item 1: MCP Infeasibility Bug Fixes (3-4h)
1. Confirm circle and house model failure modes are still as documented
2. Verify `uniform()` random data issue in circle is reproducible
3. Check if Sprint 18 emission fixes changed any relevant code paths
4. Identify exact source file locations for fixes

#### Item 2: Subset Relationship Preservation (4-5h)
1. Confirm the ~3 affected models and their specific failures
2. Verify `src/emit/emit_gams.py` and `src/emit/model.py` code locations still valid
3. Check if Sprint 18 emission changes affected set/subset handling
4. Identify test models and expected outcomes

#### Item 3: Reserved Word Quoting (2-3h)
1. Confirm the ~2 affected models and the specific reserved words
2. Verify `src/emit/expr_to_gams.py` is still the right location
3. Check if Sprint 18 quoting fixes (element literal quoting, lag/lead quoting) partially addressed this
4. List all GAMS reserved words that need quoting

#### Item 4: Lexer Error Deep Analysis (5-6h)
1. This overlaps with Task 3 (lexer_invalid_char catalog) — define scope boundary
2. Determine if Task 3 output satisfies this item or if additional work needed
3. Clarify deliverable: `LEXER_ERROR_ANALYSIS.md` — what does "complete" look like?

#### Item 5: Put Statement Format Support (2.5h)
1. Review `docs/planning/EPIC_4/SPRINT_18/PUT_FORMAT_ANALYSIS.md` for implementation details
2. Verify grammar extension location in `src/gams/gams_grammar.lark`
3. Confirm 4 target models: ps5_s_mn, ps10_s, ps10_s_mn, stdcge
4. Check if any of these models have secondary issues beyond put format

### Changes

Created `docs/planning/EPIC_4/SPRINT_19/DEFERRED_ITEMS_AUDIT.md` with per-item readiness assessment for all 5 deferred items. Updated `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` with verification results for 12 unknowns (1.1-1.3, 2.1-2.3, 3.1-3.3, 4.3, 5.1-5.2). Key changes:
- Item 1 (MCP Infeasibility): Confirmed circle `uniform()` root cause; house needs deeper KKT investigation; effort revised to 3.5-6h
- Item 2 (Subset Preservation): IR metadata and emission already implemented in Sprint 17; affected models unidentified; may already be resolved
- Item 3 (Reserved Word Quoting): Fix well-scoped to `expr_to_gams.py` and `original_symbols.py`; GAMS reserved constants list compiled
- Item 4 (Lexer Analysis): Scope overlap with Prep Task 3 clarified; recommend merging deliverables and reallocating budget to grammar fixes
- Item 5 (Put Format): 3 models blocked by `:width:decimals` only; stdcge needs separate `put_stmt_nosemi` fix; effort confirmed at 2-2.5h

### Result

All 5 deferred items have HIGH readiness for Sprint 19 implementation. No blockers identified. Key findings: (1) Subset preservation may already be complete (needs 1h runtime verification), (2) Lexer analysis overlaps with Prep Task 3 (3-4h can be reallocated to grammar fixes), (3) House model MCP infeasibility may require more investigation than originally budgeted. Overall effort estimate: 15-20h expected (original 17-21h), with downside risk to 20-25h if house requires deep KKT analysis.

### Verification

```bash
# Verify audit document exists
test -f docs/planning/EPIC_4/SPRINT_19/DEFERRED_ITEMS_AUDIT.md && echo "EXISTS" || echo "MISSING"

# Verify all 5 items covered
grep -c "^## Item" docs/planning/EPIC_4/SPRINT_19/DEFERRED_ITEMS_AUDIT.md
# Should show 5
```

### Deliverables

- ✅ `docs/planning/EPIC_4/SPRINT_19/DEFERRED_ITEMS_AUDIT.md` — per-item readiness assessment with code pointers, affected models, effort estimates
- ✅ Updated code pointers for each item (source files, key functions)
- ✅ No blockers identified; two items may have reduced scope
- ✅ Effort estimates confirmed or updated with rationale
- ✅ Unknowns 1.1-1.3, 2.1-2.3, 3.1-3.3, 4.3, 5.1-5.2 verified with findings documented in KNOWN_UNKNOWNS.md

### Acceptance Criteria

- [x] All 5 deferred items audited with current code pointers
- [x] Each item has confirmed affected models and failure modes
- [x] Sprint 18 code changes checked for impact on each item
- [x] Overlap between Lexer Error Deep Analysis and Task 3 clarified
- [x] No missing prerequisites identified (or blockers documented)
- [x] Effort estimates confirmed or updated
- [x] Unknowns 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.3, 5.1, 5.2 verified and documented in KNOWN_UNKNOWNS.md

---

## Task 6: Research IndexOffset IR Design Options

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 2-3 hours
**Deadline:** Before Sprint 19 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** 7.3, 7.4

### Objective

Research and evaluate design options for the IndexOffset IR node type, which will support GAMS lead/lag syntax (`t+1`, `t-1`, `t++1`, `t--1`). This feeds the "IndexOffset IR Design" component (4h in sprint).

### Why This Matters

IndexOffset support is needed for 8 models blocked at the translate stage. The IR design affects parser, AD (automatic differentiation), KKT generation, and GAMS emission — all four pipeline stages. A poor design choice will require refactoring across the entire pipeline. Pre-sprint research ensures the 4h sprint allocation is spent on implementation, not design exploration.

### Background

- PROJECT_PLAN.md IndexOffset section (lines 232-242): design + parser spike
- GOALS.md: "Translation Stage: IndexOffset Support — Implement lead/lag indexing (8 models blocked)"
- Existing IR AST: `src/ir/ast.py` (current node types)
- Related research: `docs/research/multidimensional_indexing.md`
- GAMS lead/lag semantics: `x(t+1)` means "x at next period", `x(t-1)` means "x at previous period"
- Circular variants: `x(t++1)` wraps around set boundaries

### What Needs to Be Done

1. Read `src/ir/ast.py` to understand current IR node structure
2. Study GAMS lead/lag syntax and semantics:
   - Linear lead: `x(t+1)` — value at next element in ordered set
   - Linear lag: `x(t-1)` — value at previous element
   - Circular lead: `x(t++1)` — wraps around to first element
   - Circular lag: `x(t--1)` — wraps around to last element
   - Multi-period: `x(t+2)`, `x(t-3)` — arbitrary offsets
3. Evaluate IR design options:
   - **Option A: IndexOffset as child of VarRef** — offset stored as attribute of variable reference
   - **Option B: IndexOffset as wrapper node** — new AST node wrapping index expressions
   - **Option C: IndexOffset as modified index** — transform index in-place with offset metadata
4. For each option, assess:
   - Parser integration (how does lark produce the node?)
   - AD compatibility (how does differentiation handle lead/lag?)
   - KKT generation (do stationarity equations need special handling?)
   - GAMS emission (how to emit `x(t+1)` syntax?)
   - Circular vs linear distinction
5. Recommend preferred design with rationale
6. Sketch parser grammar changes needed in `src/gams/gams_grammar.lark`

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Verify design document exists
test -f docs/planning/EPIC_4/SPRINT_19/INDEX_OFFSET_DESIGN_OPTIONS.md && echo "EXISTS" || echo "MISSING"

# Verify all options evaluated
grep -c "^### Option" docs/planning/EPIC_4/SPRINT_19/INDEX_OFFSET_DESIGN_OPTIONS.md
# Should show 3+ options
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_19/INDEX_OFFSET_DESIGN_OPTIONS.md` with evaluated options
- Recommended IR design with rationale
- Grammar change sketch for `src/gams/gams_grammar.lark`
- Impact assessment across all 4 pipeline stages (parser, AD, KKT, emit)
- Unknowns 7.3, 7.4 verified with findings documented

### Acceptance Criteria

- [ ] Current IR AST node structure documented
- [ ] GAMS lead/lag semantics fully described (linear, circular, multi-period)
- [ ] At least 3 design options evaluated with pros/cons
- [ ] Each option assessed against all 4 pipeline stages
- [ ] Preferred design recommended with rationale
- [ ] Grammar change sketch provided
- [ ] 8 blocked models identified by name
- [ ] Unknowns 7.3, 7.4 verified and documented in KNOWN_UNKNOWNS.md

---

## Task 7: Analyze Table Parsing Issues (ISSUE_392, ISSUE_399)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 2-3 hours
**Deadline:** Before Sprint 19 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** 8.3

### Objective

Analyze the two table parsing issues from the FIX_ROADMAP to understand the grammar gaps and produce fix plans for Sprint 19 implementation.

### Why This Matters

ISSUE_392 (table continuation) blocks the `like` model; ISSUE_399 (table description as header) blocks the `robert` model. While each blocks only 1 model, they represent table parsing correctness issues that may affect future models. Sprint 18 identified these but deferred them as requiring grammar-level work. Understanding the exact grammar gaps now enables efficient Sprint 19 fixes.

### Background

- FIX_ROADMAP: `docs/planning/EPIC_4/SPRINT_18/FIX_ROADMAP.md` (Priority 2-3 sections)
- Sprint 18 table research: `docs/planning/EPIC_4/SPRINT_18/TABLE_DATA_ANALYSIS.md`
- General table syntax research: `docs/research/RESEARCH_SUMMARY_TABLE_SYNTAX.md`
- Grammar file: `src/gams/gams_grammar.lark` (table_block rule)
- Parser: `src/ir/parser.py` (table semantic handler)
- Sprint 18 SPRINT_LOG.md Day 8: robert classified primarily as ISSUE_399

### What Needs to Be Done

#### ISSUE_392: Table Continuation (`+` syntax)
1. Read the `like` model's table block to understand the exact continuation pattern
2. Review current table grammar rule in `src/gams/gams_grammar.lark`
3. Identify where the `+` continuation marker needs to be handled
4. Determine if the grammar already supports `+` but the semantic handler drops data
5. Design grammar and/or handler fix
6. Estimate data recovery (currently 4/62 values captured, 93.5% loss)

#### ISSUE_399: Table Description as Header
1. Read the `robert` model's table block to see the description pattern
2. Trace how the parser processes table headers
3. Identify why quoted descriptions are treated as column headers
4. Design fix to distinguish quoted descriptions from column identifiers
5. Estimate data recovery (currently 4/9 values captured, 55% loss)

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Verify analysis document exists
test -f docs/planning/EPIC_4/SPRINT_19/TABLE_PARSING_ANALYSIS.md && echo "EXISTS" || echo "MISSING"

# Verify both issues covered
grep -c "ISSUE_392\|ISSUE_399" docs/planning/EPIC_4/SPRINT_19/TABLE_PARSING_ANALYSIS.md
# Should show 2+ mentions of each
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_19/TABLE_PARSING_ANALYSIS.md` with per-issue analysis
- Grammar change proposals for each issue
- Fix implementation plans with test strategies
- Confirmed or updated effort estimates (FIX_ROADMAP says 2-4h each)
- Unknown 8.3 verified with findings documented

### Acceptance Criteria

- [ ] `like` model table block analyzed for ISSUE_392
- [ ] `robert` model table block analyzed for ISSUE_399
- [ ] Current grammar rule and semantic handler reviewed
- [ ] Root cause identified for each issue (grammar gap vs. handler bug)
- [ ] Fix approach documented for each issue
- [ ] Test strategy defined (unit tests + model validation)
- [ ] Unknown 8.3 verified and documented in KNOWN_UNKNOWNS.md

---

## Task 8: Analyze MCP Pairing Issues (ISSUE_672)

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 2-3 hours
**Deadline:** Before Sprint 19 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** 8.4

### Objective

Analyze the MCP pairing failures for alkyl and bearing models to understand the bound edge cases causing empty equations, and design a fix plan.

### Why This Matters

ISSUE_672 blocks 2 models (alkyl, bearing) with "MCP pair has empty equation but variable is NOT fixed" errors. The FIX_ROADMAP estimates 4-6h of implementation effort. Understanding the specific bound configurations causing the issue before the sprint enables focused implementation.

### Background

- FIX_ROADMAP: `docs/planning/EPIC_4/SPRINT_18/FIX_ROADMAP.md` (Priority 4 section)
- MCP pairing logic: `src/kkt/partition.py` (or related KKT module)
- Model pair emission: `src/emit/model.py`
- These models reach the solve stage but fail at MCP model construction

### What Needs to Be Done

1. Run alkyl and bearing models through the pipeline to reproduce the exact error
2. Examine the variable bounds in each model:
   - Which variables have unusual bound configurations?
   - Are there variables with `.fx` (fixed), equal `.lo`/`.up`, or missing bounds?
3. Trace through MCP pairing logic to identify where empty equations are generated
4. Determine why the pairing logic doesn't handle these bound configurations
5. Design fix approach:
   - Should empty equations be filtered out?
   - Should the variable be treated as fixed?
   - Should the pairing logic be adjusted for these bound patterns?
6. Define test cases for the fix

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Verify analysis document exists
test -f docs/planning/EPIC_4/SPRINT_19/ISSUE_672_ANALYSIS.md && echo "EXISTS" || echo "MISSING"

# Verify both models covered
grep -c "alkyl\|bearing" docs/planning/EPIC_4/SPRINT_19/ISSUE_672_ANALYSIS.md
# Should show 2+ mentions of each
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_19/ISSUE_672_ANALYSIS.md` with per-model analysis
- Identified bound configurations causing empty equations
- Fix approach with implementation plan
- Confirmed or updated effort estimate (FIX_ROADMAP says 4-6h)
- Unknown 8.4 verified with findings documented

### Acceptance Criteria

- [ ] Both alkyl and bearing models analyzed with exact error reproduced
- [ ] Bound configurations causing the issue documented
- [ ] MCP pairing logic traced and failure point identified
- [ ] Fix approach designed with test strategy
- [ ] Effort estimate confirmed or updated
- [ ] Unknown 8.4 verified and documented in KNOWN_UNKNOWNS.md

---

## Task 9: Verify Sprint 19 Baseline Metrics

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 1-2 hours
**Deadline:** Before Sprint 19 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** 4.1, 6.4

### Objective

Verify that v1.2.0 baseline metrics are accurate and establish the starting point for Sprint 19 acceptance criteria. Ensure no regressions have occurred since Sprint 18 release.

### Why This Matters

Sprint 19 acceptance criteria are defined relative to baseline numbers (e.g., "lexer_invalid_char reduced from ~95 to below 50", "internal_error from 23 to below 15", "parse rate ≥55%"). If baseline numbers are wrong, Sprint 19 targets are meaningless. Sprint 18 retrospective noted "Day 11 vs final metrics discrepancy" as a lesson learned — verify upfront this time.

### Background

- Sprint 18 final metrics from SPRINT_LOG.md Day 14:
  - Parse: 62/160 (38.8%)
  - Translate: 48
  - Solve: 20
  - path_syntax_error: 7
  - Full Pipeline: 7
  - Test count: 3294
- Release tag: v1.2.0 on commit 6359dec (main)
- Sprint 19 targets from PROJECT_PLAN.md acceptance criteria:
  - lexer_invalid_char: ~95 → below 50
  - internal_error (parse): 23 → below 15
  - Parse rate: ≥55% of valid corpus

### What Needs to Be Done

1. Checkout v1.2.0 tag (or main branch) and run full test suite
2. Run full pipeline on all GAMSLIB models and capture metrics:
   - Parse success count
   - Translate success count
   - Solve success count
   - Full pipeline success count
   - Error category breakdown (lexer_invalid_char, internal_error, path_syntax_error, path_solve_terminated)
3. Compare against Sprint 18 Day 14 reported numbers
4. Document any discrepancies
5. Confirm Sprint 19 acceptance criteria targets are correctly calibrated

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Run test suite (from the repository root)
make test 2>&1 | tail -5
# Expected: 3294 tests passed

# Run pipeline metrics (project-specific command)
# python -m src.cli.pipeline_report --all
# Compare output to Sprint 18 Day 14 numbers
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_19/BASELINE_METRICS.md` with verified numbers
- Error category breakdown (counts per category)
- Confirmation that Sprint 19 targets are correctly calibrated
- Any discrepancies documented with explanation
- Unknowns 4.1, 6.4 verified with findings documented

### Acceptance Criteria

- [ ] Full test suite passes (3294 tests, zero failures)
- [ ] Pipeline metrics verified against Sprint 18 Day 14 numbers
- [ ] Error category breakdown captured (lexer_invalid_char, internal_error counts)
- [ ] Sprint 19 acceptance criteria targets validated
- [ ] Any discrepancies documented and explained
- [ ] Unknowns 4.1, 6.4 verified and documented in KNOWN_UNKNOWNS.md

---

## Task 10: Plan Sprint 19 Detailed Schedule

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 19 Day 1
**Owner:** Development team
**Dependencies:** All tasks (1-9)
**Unknowns Verified:** All

### Objective

Create a detailed day-by-day Sprint 19 plan incorporating all prep work findings, Known Unknowns research, and FIX_ROADMAP priorities. This is the final prep task — it synthesizes all earlier research into an actionable schedule.

### Why This Matters

Sprint 19 is 43-53 hours across 5 workstreams (deferred items, lexer fixes, internal_error investigation, IndexOffset design, FIX_ROADMAP items). Without a detailed schedule, there's high risk of scope creep, context switching, and incomplete workstreams. Sprint 18's checkpoint methodology (Days 1, 6, 11) proved effective and should be continued.

### Background

- PROJECT_PLAN.md Sprint 19 section (lines 147-264): component breakdown and acceptance criteria
- FIX_ROADMAP: `docs/planning/EPIC_4/SPRINT_18/FIX_ROADMAP.md`: recommended week 1/week 2 split
- Sprint 18 retrospective: checkpoint methodology rated highly; emission-over-parser pivot was high-ROI
- All prep task outputs (Tasks 1-9) feed into this plan

### What Needs to Be Done

1. Review all prep task outputs:
   - Task 1: Known Unknowns — which Critical items need Day 1 verification?
   - Task 2: internal_error classification — which patterns to fix first?
   - Task 3: lexer_invalid_char catalog — which subcategories to tackle?
   - Task 4: ISSUE_670 design — how many days for implementation?
   - Task 5: Deferred items audit — any blockers?
   - Task 6: IndexOffset design — ready for implementation?
   - Task 7: Table parsing analysis — grammar changes needed?
   - Task 8: MCP pairing analysis — fix complexity?
   - Task 9: Baseline metrics — targets calibrated?

2. Create day-by-day schedule (14 days):
   - Assign workstreams to specific days
   - Sequence by dependency (deferred items and FIX_ROADMAP P1 first, as they unblock models)
   - Schedule checkpoints (Days 1, 6, 11 following Sprint 18 pattern)
   - Include pipeline retest days

3. Define per-day:
   - Tasks and subtasks
   - Expected deliverables
   - Integration risks
   - Complexity estimates
   - Known Unknowns to verify

4. Create contingency plans:
   - What if ISSUE_670 fix takes longer than estimated?
   - What if grammar changes cause regressions?
   - What if internal_error classification reveals deeper issues?
   - Which items can be descoped if needed?

5. Define acceptance criteria per checkpoint

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Verify plan document exists
test -f docs/planning/EPIC_4/SPRINT_19/PLAN.md && echo "EXISTS" || echo "MISSING"

# Verify 14-day schedule
grep -c "^### Day" docs/planning/EPIC_4/SPRINT_19/PLAN.md
# Should show 14
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` with complete sprint plan
- Day-by-day schedule (14 days)
- Checkpoint criteria (Days 1, 6, 11)
- Contingency plans for scope overruns
- Integration with FIX_ROADMAP priorities
- All unknowns integrated into schedule with verification assignments

### Acceptance Criteria

- [ ] Plan created with all 14 days detailed
- [ ] All 5 workstreams assigned to specific days
- [ ] FIX_ROADMAP items (ISSUE_670, 392, 399, 672) integrated into schedule
- [ ] Checkpoints defined (Days 1, 6, 11) with go/no-go criteria
- [ ] All days have integration risks and complexity estimates
- [ ] Known Unknowns verification schedule included
- [ ] Contingency plans documented for each major risk
- [ ] Pipeline retest scheduled (at least Day 11)
- [ ] All unknowns from KNOWN_UNKNOWNS.md integrated into daily schedule

---

## Summary

### Critical Path (Must Complete Before Sprint 19 Day 1)

1. **Task 1: Known Unknowns** (3-4h) — blocks all other research
2. **Task 2: internal_error Classification** (3-4h) — blocks sprint scoping
3. **Task 3: lexer_invalid_char Catalog** (3-4h) — blocks sprint scoping
4. **Task 4: ISSUE_670 Analysis** (3-4h) — blocks P1 implementation
5. **Task 10: Plan Sprint 19** (3-4h) — synthesizes all research

**Critical Path Time:** ~16-20h

### High Priority (Should Complete Before Sprint 19)

- **Task 5: Deferred Items Audit** (2-3h)
- **Task 6: IndexOffset Research** (2-3h)
- **Task 7: Table Parsing Analysis** (2-3h)
- **Task 9: Baseline Metrics** (1-2h)

**High Priority Time:** ~7-11h

### Medium Priority (Complete If Time Permits)

- **Task 8: MCP Pairing Analysis** (2-3h) — nice to have; lower ROI (2 models)

**Medium Priority Time:** ~2-3h

### Overall Prep Time: ~27h (P50), range 24-32h (~3-4 working days)

### Success Criteria

Sprint 19 prep is complete when:
- [ ] Known Unknowns list created with 26 unknowns across 8 categories
- [ ] All 23 internal_error models classified by failure mode
- [ ] All ~95 lexer_invalid_char models cataloged by subcategory
- [ ] ISSUE_670 fix design documented with implementation sketch
- [ ] All 5 Sprint 18 deferred items audited for readiness
- [ ] IndexOffset IR design options evaluated
- [ ] Table parsing issues (ISSUE_392, ISSUE_399) analyzed
- [ ] Baseline metrics verified against v1.2.0 release
- [ ] 14-day sprint plan created with checkpoints and contingencies

---

## Appendix: Document Cross-References

### Sprint Goals
- `docs/planning/EPIC_4/PROJECT_PLAN.md` (lines 147-264) — Sprint 19 full definition
- `docs/planning/EPIC_4/GOALS.md` — Epic 4 strategic goals and success metrics

### Prior Sprint Context
- `docs/planning/EPIC_4/SPRINT_18/SPRINT_LOG.md` — Day-by-day log, Day 14 retrospective and handoff notes
- `docs/planning/EPIC_4/SPRINT_18/KNOWN_UNKNOWNS.md` — 24 unknowns (template for Sprint 19)
- `docs/planning/EPIC_4/SPRINT_18/PREP_PLAN.md` — Sprint 18 prep plan (format reference)
- `docs/planning/EPIC_4/SPRINT_18/FIX_ROADMAP.md` — Prioritized fixes for Sprint 19+ (ISSUE_670, 392, 399, 672)
- `docs/planning/EPIC_4/SPRINT_18/PLAN.md` — Sprint 18 detailed plan

### Sprint 18 Research Documents
- `docs/planning/EPIC_4/SPRINT_18/TABLE_DATA_ANALYSIS.md` — Table data emission research
- `docs/planning/EPIC_4/SPRINT_18/COMPUTED_PARAM_ANALYSIS.md` — Computed parameter research
- `docs/planning/EPIC_4/SPRINT_18/PUT_FORMAT_ANALYSIS.md` — Put statement format research
- `docs/planning/EPIC_4/SPRINT_18/CORPUS_SURVEY.md` — GAMSLIB corpus validation
- `docs/planning/EPIC_4/SPRINT_18/GAMS_ACTION_C_RESEARCH.md` — GAMS compilation testing

### General Research
- `docs/research/gamslib_parse_errors.md` — Sprint 6 parse error analysis
- `docs/research/gamslib_parse_errors_preliminary.md` — Preliminary parse error patterns
- `docs/research/multidimensional_indexing.md` — Multi-dimensional set indexing
- `docs/research/nested_subset_indexing_research.md` — Nested/subset indexing
- `docs/research/RESEARCH_SUMMARY_TABLE_SYNTAX.md` — GAMS table syntax research
- `docs/research/preprocessor_directives.md` — GAMS preprocessor directives ($if, $include)

### Source Code References
- `src/gams/gams_grammar.lark` — GAMS grammar (lexer/parser rules)
- `src/ir/ast.py` — IR AST node definitions
- `src/ir/parser.py` — GAMS parser and semantic handlers
- `src/kkt/stationarity.py` — KKT stationarity equation generation
- `src/kkt/assemble.py` — KKT system assembly
- `src/emit/emit_gams.py` — Main GAMS MCP code generator
- `src/emit/model.py` — Model MCP declaration emission
- `src/emit/expr_to_gams.py` — AST-to-GAMS expression converter (index aliasing)
