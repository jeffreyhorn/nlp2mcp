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
| **Total Sprint** | **22-26h** | **~56h** | **+30h expanded scope** |

**Note:** Sprint 18 has been expanded to include items originally planned for Sprint 19. The day-by-day schedule totals ~56h balanced across 14 days (no single day exceeds 6h).

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
**Action:** Remove *documentation of exclusions* from Sprint 18. Instead, these bugs are added to Sprint 18 scope as fix targets (see "Added Items" section #4 below).

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
**Location:** `src/kkt/assemble.py`, `src/emit/model.py`
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
**Source:** 99 models fail at parse stage (includes lexer_invalid_char, internal_error, semantic_undefined_symbol)
**Problem:** Need to categorize and prioritize parse error patterns for future fixes
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
- [x] All emit_gams.py fixes merged (set quoting, computed params, bound multipliers, reserved words, subsets)
- [ ] `path_syntax_error` reduced from v1.1.0 baseline 17 (22 in Day 0 due to higher translate coverage) to ≤4 — **NOT MET** (10 remain, 4 architectural)
- [x] 12 original solving models still solve (no regressions) — **MET** (19 now solve)
- [x] New metrics recorded

**Checkpoint 2 Results (Day 6):**
- Solve: 19/50 (target ≥17 **MET**)
- path_syntax_error: 10 (target ≤4 **NOT MET**)
- Architectural blockers identified: abel, qabel, chenery (cross-indexed sums), mingamma (missing GAMS function)
- Investigate candidates: blend, sample, like, robert, mexss, orani (domain violations)

### Day 7: Domain Issue Investigation - Part 1 (4h)

**Focus:** Investigate domain violation errors for tractable fixes

**Note:** *Plan revised based on Checkpoint 2 findings. Original plan targeted MCP infeasibility bugs, but path_syntax_error target (≤4) was not met (10 remain). Prioritizing domain violation investigation.*

| Task | Time | Deliverable |
|------|------|-------------|
| Deep-dive on blend domain violation (E171) | 1h | Root cause analysis |
| Deep-dive on sample domain violation (E171) | 1h | Root cause analysis |
| Deep-dive on like domain violation (E170) | 1h | Root cause analysis |
| Implement fixes for tractable cases | 1h | Quick wins if found |

**Models to investigate:** blend, sample, like (domain violations that may be fixable)

**Acceptance:** Root causes documented, tractable fixes implemented

### Day 8: Domain Issue Investigation - Part 2 (4h)

**Focus:** Continue domain violation investigation

| Task | Time | Deliverable |
|------|------|-------------|
| Deep-dive on robert domain violation (E170) | 1h | Root cause analysis |
| Deep-dive on mexss domain violations (E170/171) | 1h | Root cause analysis |
| Deep-dive on orani dynamic domain extension | 1h | Root cause analysis |
| Implement fixes for tractable cases | 1h | Quick wins if found |

**Models to investigate:** robert, mexss, orani

**Acceptance:** All 6 "investigate" models analyzed, tractable fixes implemented

### Day 9: Issue Documentation + Architectural Analysis (4h)

**Focus:** Document findings and create issue files

| Task | Time | Deliverable |
|------|------|-------------|
| Extend existing ISSUE_*.md for architectural limitations | 1.5h | Updated ISSUE_670/676 with per-model analysis for abel, qabel, chenery, mingamma |
| Create ISSUE_*.md for domain violations | 1.5h | Issue files for remaining unfixable models |
| Update KNOWN_UNKNOWNS.md with findings | 0.5h | Mark resolved/new unknowns |
| Move completed issues to docs/issues/completed/ | 0.5h | Organized issue tracking |

**Acceptance:** All path_syntax_error models documented with root causes

### Day 10: Final Fixes & Testing (4h)

**Focus:** Implement remaining tractable fixes, full testing

| Task | Time | Deliverable |
|------|------|-------------|
| Implement any remaining tractable fixes | 1.5h | Additional models unblocked |
| Full pipeline retest on all 160 models | 1.5h | Updated `gamslib_status.json` |
| Run full test suite | 0.5h | All tests pass |
| Verify no regressions in solving models | 0.5h | 19+ models still solve |

**Acceptance:** Pipeline retest complete, no regressions

### Day 11: Documentation & Checkpoint 3 (4h)

**Focus:** Final documentation, third checkpoint

| Task | Time | Deliverable |
|------|------|-------------|
| Update SPRINT_LOG.md with final metrics | 1h | Complete sprint record |
| Update GAMSLIB_STATUS.md | 0.5h | Reflect new metrics |
| Create `FIX_ROADMAP.md` for Sprint 19+ | 1h | Prioritized future work |
| **Checkpoint 3:** Sprint review | 1.5h | Go/no-go assessment |

**Checkpoint 3 Criteria:**
- [ ] All tractable path_syntax_error fixes merged
- [ ] Architectural issues documented with ISSUE_*.md files
- [ ] Solve count maintained at ≥19 (no regressions)
- [ ] FIX_ROADMAP.md created for future sprints
- [ ] All tests passing

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

**Total Sprint Duration: ~56h** (balanced across 14 days, no day exceeds 6h)

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

### After Each Fix (Optional)

The 12 currently-solving models can be verified after each emit_gams.py change if there is suspicion of a regression. This is not explicitly scheduled in the day-by-day plan but is available as an ad-hoc check:

```bash
# Quick regression check (run ad-hoc if regression suspected)
# Note: We run without --only-solve to ensure translate step re-emits MCP after emit_gams.py changes
for model in apl1p blend himmel11 hs62 mathopt2 mhw4d mhw4dx prodmix rbrock trig trnsport trussm; do
    python scripts/gamslib/run_full_test.py --model "$model"
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
- Solve: ≥22 (improvement from 12)
- `path_syntax_error`: ≤2 (reduced from 17)

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

- **Syntactic Validation:** All 160 models tested (adjusted: confirm all valid)
- **Corpus Defined:** Valid corpus established (adjusted: no exclusions needed)
- **emit_gams.py:** Fixes merged with tests (adjusted: different fixes than planned)
- **Put Statement:** Format syntax supported (adjusted: 3+1 models)
- **Metrics:** `path_syntax_error` reduced (target: from 17 to ≤2)
- **Quality:** All 3204+ tests pass

---

## Document History

- February 6, 2026: Expanded scope to ~56h (14 days) by pulling in Sprint 19 items
- February 6, 2026: Added MCP infeasibility bug fixes for circle/house
- February 6, 2026: Initial creation (Task 10 of PREP_PLAN.md)
