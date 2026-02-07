# Sprint 18 Detailed Plan

**Created:** February 6, 2026
**Status:** Ready for Execution
**Baseline:** v1.1.0 — Parse 61/160 (38.1%), Translate 42/61 (68.9%), Solve 12/42 (28.6%)

---

## Executive Summary

Sprint 18 scope has been **significantly adjusted** based on prep task findings. Several originally planned items are unnecessary, while new higher-priority items have been identified.

### Scope Changes Summary

| Original Plan | Finding | Action |
|---------------|---------|--------|
| **Table data emission fix** (4-5h) | Zero models fail due to table data (Task 4) | **REMOVED** — not needed |
| **Syntax Error Report** (2-3h) | Zero GAMS syntax errors found (Task 2) | **SIMPLIFIED** — report confirms all valid |
| **Corpus reclassification** (2h) | No models to exclude (Task 2, 7) | **SIMPLIFIED** — add schema fields only |
| **Infeasible/unbounded docs** (2h) | Both are MCP bugs, not exclusions (Task 7) | **REMOVED** — keep as bugs to fix |
| Set element quoting fix | 6 models blocked (Task 4) — highest ROI | **ADDED** — 2-3h for 6 models |
| Bound multiplier dimension fix | 5 models blocked (Task 4) | **ADDED** — 4-5h for 5 models |
| Put statement models | Only 3 models (not 4) need `:width:decimals` (Task 6) | **ADJUSTED** — 3 models + stdcge needs separate fix |

### Time Reallocation

| Category | Original | Revised | Delta |
|----------|----------|---------|-------|
| Syntactic Validation | 10-12h | 4-5h | **-6h** |
| emit_gams.py Fixes | 10-12h | 10-12h | 0h (rebalanced) |
| Parse Quick Win | 2h | 2.5h | +0.5h |
| MCP Bug Fixes (circle, house) | 0h | 3-4h | **+3.5h** (added) |
| Subset Relationship Preservation | 0h | 4-5h | **+4.5h** (pulled from Sprint 19) |
| Reserved Word Quoting | 0h | 2-3h | **+2.5h** (pulled from Sprint 19) |
| path_syntax_error Investigation | 0h | 4h | **+4h** (pulled from Sprint 19) |
| Lexer Error Deep Analysis | 0h | 5-6h | **+5.5h** (pulled from Sprint 19) |
| Prioritized Fix Roadmap | 0h | 2-3h | **+2.5h** (pulled from Sprint 19) |
| Complex Set Data Syntax (initial) | 0h | 2h | **+2h** (pulled from Sprint 19) |
| **Total Sprint** | **22-26h** | **44-50h** | **+22h expanded scope** |

**Note:** Sprint 18 has been expanded to include items originally planned for Sprint 19. The day-by-day schedule is balanced so no single day exceeds 10h of effort.

---

## Removed Items (Not Needed)

### 1. Table Data Emission Fix
**Original:** 4-5 hours to fix table data emission in `original_symbols.py`
**Finding:** Task 4 analysis found **zero models** fail due to table data emission. Tables are parsed as `ParameterDef` objects and emit correctly.
**Action:** Remove from Sprint 18. No work needed.

### 2. Syntax Error Report with Error Details
**Original:** 2-3 hours to generate `SYNTAX_ERROR_REPORT.md` with error types, messages, line numbers
**Finding:** Task 2 found **zero GAMS syntax errors** in all 160 models. All nlp2mcp parse failures are grammar limitations.
**Action:** Generate a simplified validation report confirming all models compile successfully.

### 3. Infeasible/Unbounded Documentation
**Original:** 2 hours to document excluded infeasible/unbounded models
**Finding:** Task 7 found both `model_infeasible` models (circle, house) are **MCP formulation bugs**, not inherently infeasible. No unbounded models exist.
**Action:** Remove from Sprint 18. These are bugs to fix in later sprints, not exclusion candidates.

### 4. Corpus Reclassification (Exclusions)
**Original:** 2 hours to reclassify models as `excluded_syntax_error`, `excluded_infeasible`, `excluded_unbounded`
**Finding:** No models need exclusion. The schema should support future exclusions but no models currently qualify.
**Action:** Implement schema fields only (supporting infrastructure), no actual exclusions.

---

## Added Items (New Priorities)

### 1. Set Element Quoting Fix
**Source:** Task 4 analysis identified 6 models (ps2_f, ps2_f_eff, ps2_f_inf, ps2_f_s, ps2_s, pollut)
**Problem:** Set elements used as symbols without proper quoting in emitted GAMS code
**Location:** `src/emit/expr_to_gams.py`
**Time:** 2-3 hours
**ROI:** 6 models / 2.5h = **2.4 models/hour** (highest priority)

### 2. Bound Multiplier Dimension Fix
**Source:** Task 4 analysis identified 5 models (alkyl, bearing, + 3 partial overlaps)
**Problem:** Bound multiplier variables (`piL_*`, `piU_*`) have incorrect dimensions for scalar variables
**Location:** `src/kkt/bound_multipliers.py`, `src/emit/model.py`
**Time:** 4-5 hours
**ROI:** 5 models / 4.5h = **1.1 models/hour**

### 3. stdcge `put_stmt_nosemi` Fix
**Source:** Task 6 found stdcge blocked by different issue than `:width:decimals`
**Problem:** Uses `loop(j, put j.tl)` without semicolon before loop close
**Location:** `src/gams/gams_grammar.lark`
**Time:** 0.5 hours (additional to put format fix)
**ROI:** 1 model / 0.5h = **2.0 models/hour**

### 4. MCP Infeasibility Bug Fixes (circle, house)
**Source:** Task 7 found both `model_infeasible` models are MCP formulation bugs, not inherently infeasible
**Problems:**
- **circle**: Uses `uniform()` random data that regenerates differently in MCP context — need to capture original values
- **house**: Likely constraint qualification failure or incorrect Lagrangian formulation
**Location:** `src/kkt/` (investigation needed to pinpoint exact issue)
**Time:** 3-4 hours (investigation + fix)
**ROI:** 2 models / 3.5h = **0.6 models/hour** (lower ROI but moves models from infeasible to optimal)

### 5. Subset Relationship Preservation (Pulled from Sprint 19)
**Source:** Task 4 identified models failing due to subset relationships not preserved in emitted GAMS
**Problem:** When a set is defined as a subset of another, the emitted GAMS loses this relationship
**Location:** `src/emit/emit_gams.py`, `src/emit/model.py`
**Time:** 4-5 hours
**ROI:** ~3 models / 4.5h = **0.7 models/hour**

### 6. Reserved Word Quoting (Pulled from Sprint 19)
**Source:** Task 4 identified models using GAMS reserved words as identifiers
**Problem:** Identifiers that are GAMS reserved words need quoting in emitted code
**Location:** `src/emit/expr_to_gams.py`
**Time:** 2-3 hours
**ROI:** ~2 models / 2.5h = **0.8 models/hour**

### 7. Remaining path_syntax_error Investigation (Pulled from Sprint 19)
**Source:** After initial fixes, ~4-6 models may still have `path_syntax_error`
**Problem:** Need to investigate and categorize remaining syntax errors
**Location:** Various in `src/emit/`
**Time:** 4 hours (investigation + fixes where tractable)
**ROI:** ~4 models / 4h = **1.0 models/hour**

### 8. Lexer Error Deep Analysis (Pulled from Sprint 19)
**Source:** 99 models fail at parse stage with lexer errors
**Problem:** Need to categorize and prioritize lexer error patterns for future fixes
**Deliverable:** `LEXER_ERROR_ANALYSIS.md` with error categories and fix priorities
**Time:** 5-6 hours
**ROI:** Foundation for Sprint 19+ parse improvements

### 9. Prioritized Fix Roadmap (Pulled from Sprint 19)
**Source:** Need to plan future sprints based on analysis findings
**Problem:** No consolidated view of remaining work prioritized by ROI
**Deliverable:** `FIX_ROADMAP.md` with prioritized list of remaining fixes
**Time:** 2-3 hours
**ROI:** Planning efficiency for future sprints

### 10. Initial Complex Set Data Syntax Work (Pulled from Sprint 19)
**Source:** Task 4 identified complex set data syntax as a category
**Problem:** Some models use advanced set data syntax not yet supported
**Location:** `src/gams/gams_grammar.lark`
**Time:** 2 hours (initial investigation + simple cases)
**ROI:** Foundation for future parse improvements

---

## Revised Day-by-Day Schedule

### Day 1: Syntactic Validation Infrastructure (4h)

**Focus:** Create test_syntax.py, validate corpus, begin schema work

| Task | Time | Deliverable |
|------|------|-------------|
| Create `scripts/gamslib/test_syntax.py` | 2h | Script that runs `gams action=c` on all 160 models |
| Run validation on full corpus | 0.5h | All models validated (expect 160/160 pass) |
| Update `gamslib_status.json` schema | 0.5h | Add `gams_syntax` field to all entries |
| Add `exclusion` fields to schema.json | 0.5h | Support future exclusions |
| Schema version bump to 2.1.0 | 0.5h | Schema version 2.1.0 |

**Acceptance:** Script runs successfully, all 160 models confirmed valid, schema updated

### Day 2: Set Element Quoting Fix (4h)

**Focus:** Implement highest-ROI emit fix

| Task | Time | Deliverable |
|------|------|-------------|
| Implement set element quoting fix | 2.5h | Fix in `expr_to_gams.py` |
| Complete set element quoting tests | 1h | Regression tests for ps2_* family + pollut |
| Verify 6 models now compile | 0.5h | `gams action=c` passes on all 6 |

**Acceptance:** Set element quoting fix merged, 6 models unblocked

### Day 3: Computed Parameter Skip + Checkpoint 1 (3h)

**Focus:** Skip computed parameter assignments, first checkpoint

| Task | Time | Deliverable |
|------|------|-------------|
| Implement skip in `emit_computed_parameter_assignments()` | 1h | Function returns empty string |
| Add regression tests | 0.5h | Verify 12 solving models still work |
| Verify 5 models now compile | 0.5h | ajax, demo1, mathopt1, mexss, sample |
| **Checkpoint 1:** Syntactic validation + first fixes complete | 1h | Go/no-go for remaining emit fixes |

**Checkpoint 1 Criteria:**
- [ ] test_syntax.py runs on all 160 models
- [ ] Schema updated with `gams_syntax` and `exclusion` fields
- [ ] Set element quoting fix merged (6 models unblocked)
- [ ] Computed parameter skip fix merged (5 models unblocked)

### Day 4: Bound Multiplier Dimension Fix (4h)

**Focus:** Fix bound multiplier variable dimensions

| Task | Time | Deliverable |
|------|------|-------------|
| Analyze bound multiplier generation code | 0.5h | Understand issue in `bound_multipliers.py` |
| Implement dimension fix | 2.5h | Handle scalar variable bound multipliers |
| Add regression tests | 0.5h | Test with alkyl, bearing models |
| Verify models now compile | 0.5h | `gams action=c` passes on affected models |

**Acceptance:** Bound multiplier fix passes tests, 3-5 models unblocked

### Day 5: Parse Quick Win + Reserved Word Quoting (4.5h)

**Focus:** Put statement format + reserved word handling

| Task | Time | Deliverable |
|------|------|-------------|
| Add `put_format` rule to grammar | 1.5h | Support `:width:decimals` syntax |
| Add `put_stmt_nosemi` variant for stdcge | 0.5h | Handle `loop(j, put j.tl)` |
| Add unit tests for put statement parsing | 0.5h | Test all 4 models parse |
| Implement reserved word quoting | 2h | Fix in `expr_to_gams.py` |

**Acceptance:** ps5_s_mn, ps10_s, ps10_s_mn, stdcge parse; reserved words quoted

### Day 6: Subset Relationship Preservation + Checkpoint 2 (5h)

**Focus:** Preserve subset relationships in emitted GAMS

| Task | Time | Deliverable |
|------|------|-------------|
| Analyze subset relationship handling | 1h | Understand current emission logic |
| Implement subset preservation fix | 2.5h | Fix in `emit_gams.py`, `model.py` |
| Add regression tests | 0.5h | Test affected models |
| **Checkpoint 2:** emit_gams.py fixes complete | 1h | Progress report with new metrics |

**Checkpoint 2 Criteria:**
- [ ] All emit_gams.py fixes merged (set quoting, computed params, bound multipliers, reserved words, subsets)
- [ ] `path_syntax_error` reduced from 17 to ≤4
- [ ] 12 original solving models still solve (no regressions)
- [ ] New metrics recorded

### Day 7: MCP Infeasibility Bug Fixes (4h)

**Focus:** Fix circle and house MCP formulation bugs

| Task | Time | Deliverable |
|------|------|-------------|
| Investigate circle random data issue | 1h | Understand `uniform()` regeneration problem |
| Fix circle: capture original random values | 1.5h | circle achieves `model_optimal` |
| Investigate house constraint qualification | 1h | Identify Lagrangian formulation issue |
| Fix house MCP formulation | 0.5h | house achieves `model_optimal` |

**Acceptance:** Both circle and house move from `model_infeasible` to `model_optimal`

### Day 8: Remaining path_syntax_error Investigation (4h)

**Focus:** Investigate and fix remaining syntax errors

| Task | Time | Deliverable |
|------|------|-------------|
| Run pipeline and identify remaining errors | 0.5h | List of models still failing |
| Categorize remaining `path_syntax_error` cases | 1h | Error taxonomy |
| Fix tractable cases | 2h | Additional models unblocked |
| Document intractable cases for future | 0.5h | Notes for future sprints |

**Acceptance:** Remaining errors categorized, tractable cases fixed

### Day 9: Lexer Error Deep Analysis (5.5h)

**Focus:** Analyze 99 lexer error models for future fixes

| Task | Time | Deliverable |
|------|------|-------------|
| Extract lexer error patterns from 99 models | 2h | Pattern frequency analysis |
| Categorize by error type and complexity | 2h | Categories with model counts |
| Identify quick wins vs complex fixes | 1h | Prioritized fix list |
| Create `LEXER_ERROR_ANALYSIS.md` | 0.5h | Analysis document |

**Acceptance:** Comprehensive lexer error analysis complete

### Day 10: Complex Set Data Syntax + Prioritized Roadmap (4h)

**Focus:** Initial complex set syntax work + planning document

| Task | Time | Deliverable |
|------|------|-------------|
| Investigate complex set data syntax patterns | 1h | Pattern identification |
| Implement simple cases in grammar | 1h | Initial grammar additions |
| Create `FIX_ROADMAP.md` with prioritized fixes | 2h | Complete roadmap document |

**Acceptance:** Initial complex set syntax support, roadmap complete

### Day 11: Pipeline Retest + Checkpoint 3 (4h)

**Focus:** Full pipeline retest, third checkpoint

| Task | Time | Deliverable |
|------|------|-------------|
| Run full pipeline on all 160 models | 1.5h | Updated `gamslib_status.json` |
| Analyze results and update metrics | 1h | New baseline numbers |
| Run full test suite (3204+ tests) | 0.5h | All tests pass |
| **Checkpoint 3:** All implementation complete | 1h | Go/no-go for release |

**Checkpoint 3 Criteria:**
- [ ] All Sprint 18 features merged
- [ ] circle and house achieve `model_optimal`
- [ ] `path_syntax_error` minimized
- [ ] Lexer error analysis complete
- [ ] Fix roadmap created

### Day 12: Documentation Updates (4h)

**Focus:** Update all documentation with sprint results

| Task | Time | Deliverable |
|------|------|-------------|
| Update GAMSLIB_STATUS.md | 1h | Reflect new metrics |
| Update FAILURE_ANALYSIS.md | 1h | Updated error categories |
| Update PROJECT_PLAN.md for Sprint 19+ | 1h | Reflect completed work |
| Review and update KNOWN_UNKNOWNS.md | 1h | Mark resolved unknowns |

**Acceptance:** All documentation updated and consistent

### Day 13: Sprint Retrospective + Release Prep (3.5h)

**Focus:** Retrospective and release preparation

| Task | Time | Deliverable |
|------|------|-------------|
| Draft Sprint 18 retrospective | 1.5h | Lessons learned, what worked, what didn't |
| Version bump to v1.2.0 | 0.5h | Updated version numbers |
| Create release notes | 1h | Comprehensive release notes |
| Create release PR | 0.5h | PR ready for merge |

**Acceptance:** Retrospective complete, release PR ready

### Day 14: Final Review + Release (2.5h)

**Focus:** Final review and release

| Task | Time | Deliverable |
|------|------|-------------|
| Final review of all changes | 1h | Quality check |
| Address any final issues | 1h | Bug fixes if needed |
| Merge release PR and tag | 0.5h | v1.2.0 released |

**Acceptance:** Sprint 18 complete, v1.2.0 released

**Total Sprint Duration: ~47h** (balanced across 14 days, no day exceeds 6h)

---

## Expected Outcomes

### Metrics Improvement

| Metric | Baseline (v1.1.0) | Expected (v1.2.0) | Change |
|--------|-------------------|-------------------|--------|
| Parse Success | 61/160 (38.1%) | 65/160 (40.6%) | +4 models |
| Translate Success | 42/61 (68.9%) | TBD | — |
| Solve Success | 12/42 (28.6%) | ≥22 models | +10 models |
| `path_syntax_error` | 17 | ≤2 | -15 models |
| `model_infeasible` | 2 | 0 | -2 models (fixed) |

**Note:** Parse improvement is modest (+4 from put statement fix). The major gains are in solve stage from emit_gams.py fixes, MCP bug fixes, and additional investigation of remaining errors.

### Models Unblocked

| Fix | Models Unblocked |
|-----|------------------|
| Set element quoting | ps2_f, ps2_f_eff, ps2_f_inf, ps2_f_s, ps2_s, pollut (6) |
| Computed param skip | ajax, demo1, mathopt1, mexss, sample (5) |
| Bound multiplier dimension | alkyl, bearing, + partial overlaps (3-5) |
| Put statement format | ps5_s_mn, ps10_s, ps10_s_mn, stdcge (4) |
| Reserved word quoting | ~2 models |
| Subset relationship preservation | ~3 models |
| Remaining path_syntax_error investigation | ~4 models |
| MCP infeasibility fixes | circle, house (2) |

**Total potential improvement (net of overlaps):** ~15 models unblocked from `path_syntax_error` (of 17 baseline) + 2 from `model_infeasible`

### Analysis Deliverables

| Document | Description |
|----------|-------------|
| `LEXER_ERROR_ANALYSIS.md` | Comprehensive analysis of 99 lexer error models with categories and priorities |
| `FIX_ROADMAP.md` | Prioritized roadmap for remaining fixes in future sprints |

These analysis deliverables provide the foundation for efficient Sprint 19+ planning.

---

## Contingency Plans

### Risk 1: Set Element Quoting More Complex Than Analyzed
**Trigger:** Fix takes >4 hours or causes regressions
**Mitigation:** Reduce scope to ps2_* family only, defer pollut to Sprint 19
**Impact:** -1 model, +2 hours buffer

### Risk 2: Bound Multiplier Fix Affects KKT Generation
**Trigger:** Changes to `bound_multipliers.py` break other models
**Mitigation:** Implement narrowly-scoped fix for scalar variables only
**Impact:** May defer some partial-overlap models to Sprint 19

### Risk 3: Regression in 12 Solving Models
**Trigger:** Any of the 12 currently-solving models regresses
**Mitigation:** Immediate rollback of offending fix, root cause analysis
**Impact:** Block release until regression fixed

### Risk 4: Put Statement Grammar Conflicts
**Trigger:** `:width:decimals` rule conflicts with existing grammar
**Mitigation:** Use Lark priority rules to disambiguate
**Impact:** +1 hour debugging grammar

### Risk 5: MCP Infeasibility Fixes More Complex Than Expected
**Trigger:** circle or house require deeper KKT investigation (>4 hours combined)
**Mitigation:** Fix one model fully, document root cause for other, defer to Sprint 19
**Impact:** -1 model from solve count, but documented investigation accelerates future fix

### Risk 6: Subset Relationship Preservation More Complex
**Trigger:** Fix requires significant refactoring of emit infrastructure (>5 hours)
**Mitigation:** Implement narrowly-scoped fix for most common pattern only
**Impact:** May defer edge cases to Sprint 19

### Risk 7: Reserved Word Conflicts with Existing Grammar
**Trigger:** Quoting reserved words causes parse conflicts or breaks existing models
**Mitigation:** Maintain list of safe-to-quote words vs unsafe words
**Impact:** +1 hour debugging, may need to handle case-by-case

### Risk 8: Lexer Error Analysis Uncovers Massive Scope
**Trigger:** 99 models have >10 distinct error categories requiring major grammar work
**Mitigation:** Focus analysis on highest-frequency categories, document others for future
**Impact:** Analysis complete but roadmap may show longer timeline than expected

---

## Regression Testing Plan

### After Each Fix

The 12 currently-solving models must be verified after each emit_gams.py change:

```bash
# Quick regression check (run after each fix)
for model in apl1p blend himmel11 hs62 mathopt2 mhw4d mhw4dx prodmix rbrock trig trnsport trussm; do
    python scripts/gamslib/run_full_test.py --model "$model" --only-solve
done
```

**Acceptance:** All 12 models still achieve `model_optimal` status

### Day 11 Full Retest

Run complete pipeline on all 160 models:

```bash
python scripts/gamslib/run_full_test.py
```

This command runs Parse, Translate, Solve, and Compare for all models; Compare is currently always executed whenever Solve runs in this script.

**Scope:** All 160 convex models
**Stages:** Parse → Translate → Solve → Compare
**Success Criteria:**
- Parse: ≥61 (no regressions)
- Translate: ≥42 (no regressions)
- Solve: ≥18 (improvement from 12)
- `path_syntax_error`: ≤6 (reduced from 17)

---

## References

### Prep Task Deliverables

| Task | Document | Key Finding |
|------|----------|-------------|
| Task 1 | `KNOWN_UNKNOWNS.md` | 24 unknowns identified |
| Task 2 | `CORPUS_SURVEY.md` | Zero GAMS syntax errors |
| Task 3 | `GAMS_ACTION_C_RESEARCH.md` | Complete `action=c` documentation |
| Task 4 | `TABLE_DATA_ANALYSIS.md` | Failure taxonomy (6 categories) |
| Task 5 | `COMPUTED_PARAM_ANALYSIS.md` | Skip approach (2h fix) |
| Task 6 | `PUT_FORMAT_ANALYSIS.md` | 3 models + stdcge |
| Task 7 | Unknown 1.4, 1.5 | Both infeasible are MCP bugs |
| Task 8 | `SCHEMA_DESIGN.md` | Schema v2.1.0 spec |
| Task 9 | Unknown 4.1, 4.3, 4.4 | Baseline verified |

### Sprint 18 Goals (from PROJECT_PLAN.md)

- **Syntactic Validation:** All 160 models tested ✓ (adjusted: confirm all valid)
- **Corpus Defined:** Valid corpus established ✓ (adjusted: no exclusions needed)
- **emit_gams.py:** Fixes merged with tests ✓ (adjusted: different fixes than planned)
- **Put Statement:** Format syntax supported ✓ (adjusted: 3+1 models)
- **Metrics:** `path_syntax_error` reduced by ≥6 ✓ (target: reduce from 17 to ≤6)
- **Quality:** All 3204+ tests pass ✓

---

## Document History

- February 6, 2026: Expanded scope to 47h (14 days) by pulling in Sprint 19 items
- February 6, 2026: Added MCP infeasibility bug fixes for circle/house
- February 6, 2026: Initial creation (Task 10 of PREP_PLAN.md)
