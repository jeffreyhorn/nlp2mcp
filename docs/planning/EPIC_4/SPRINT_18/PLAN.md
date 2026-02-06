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
| **Total** | **22-26h** | **16-20h** | **-6h saved** |

The saved time can be used for buffer/contingency or to pull forward Sprint 19 work.

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

---

## Revised Day-by-Day Schedule

### Day 1: Syntactic Validation Infrastructure (3h)

**Focus:** Create test_syntax.py and validate corpus

| Task | Time | Deliverable |
|------|------|-------------|
| Create `scripts/gamslib/test_syntax.py` | 2h | Script that runs `gams action=c` on all 160 models |
| Run validation on full corpus | 0.5h | All models validated (expect 160/160 pass) |
| Update `gamslib_status.json` schema | 0.5h | Add `gams_syntax` field to all entries |

**Acceptance:** Script runs successfully, all 160 models confirmed valid

### Day 2: Schema Updates + Set Element Quoting (3h)

**Focus:** Implement schema changes and start highest-ROI emit fix

| Task | Time | Deliverable |
|------|------|-------------|
| Add `gams_syntax` fields to schema.json | 0.5h | Schema version 2.1.0 |
| Add `exclusion` fields to schema.json | 0.5h | Support future exclusions |
| Implement set element quoting fix | 2h | Fix in `expr_to_gams.py` |

**Acceptance:** Schema updated, set element quoting fix passes unit tests

### Day 3: Set Element Quoting + Checkpoint 1 (2h)

**Focus:** Complete set element quoting, verify 6 models unblocked

| Task | Time | Deliverable |
|------|------|-------------|
| Complete set element quoting tests | 1h | Regression tests for ps2_* family + pollut |
| Verify 6 models now compile | 0.5h | `gams action=c` passes on all 6 |
| **Checkpoint 1:** Syntactic validation complete | 0.5h | Go/no-go for emit fixes |

**Checkpoint 1 Criteria:**
- [x] test_syntax.py runs on all 160 models
- [x] Schema updated with `gams_syntax` and `exclusion` fields
- [x] Set element quoting fix merged
- [x] 6 models unblocked (ps2_f, ps2_f_eff, ps2_f_inf, ps2_f_s, ps2_s, pollut)

### Day 4: Computed Parameter Skip Fix (2h)

**Focus:** Skip computed parameter assignments (simple fix per Task 5)

| Task | Time | Deliverable |
|------|------|-------------|
| Implement skip in `emit_computed_parameter_assignments()` | 1h | Function returns empty string |
| Add regression tests | 0.5h | Verify 12 solving models still work |
| Verify 5 models now compile | 0.5h | ajax, demo1, mathopt1, mexss, sample |

**Acceptance:** Skip fix merged, 5 models unblocked, no regressions

### Day 5: Bound Multiplier Dimension Fix (3h)

**Focus:** Fix bound multiplier variable dimensions

| Task | Time | Deliverable |
|------|------|-------------|
| Analyze bound multiplier generation code | 0.5h | Understand issue in `bound_multipliers.py` |
| Implement dimension fix | 2h | Handle scalar variable bound multipliers |
| Add regression tests | 0.5h | Test with alkyl, bearing models |

**Acceptance:** Bound multiplier fix passes tests

### Day 6: Bound Multiplier Completion + Pipeline Retest + Checkpoint 2 (3h)

**Focus:** Complete bound multiplier fix, run full pipeline retest

| Task | Time | Deliverable |
|------|------|-------------|
| Complete bound multiplier fix | 1h | Final testing and edge cases |
| Run full pipeline on all 160 models | 1h | Updated `gamslib_status.json` |
| **Checkpoint 2:** emit_gams.py fixes complete | 1h | Progress report with new metrics |

**Checkpoint 2 Criteria:**
- [x] All emit_gams.py fixes merged (set quoting, computed params, bound multipliers)
- [x] `path_syntax_error` reduced from 17 to ≤6
- [x] 12 original solving models still solve (no regressions)
- [x] New metrics recorded

### Day 7: Parse Quick Win - Put Statement Format (2.5h)

**Focus:** Add `:width:decimals` support + stdcge fix

| Task | Time | Deliverable |
|------|------|-------------|
| Add `put_format` rule to grammar | 1.5h | Support `:width:decimals` syntax |
| Add `put_stmt_nosemi` variant for stdcge | 0.5h | Handle `loop(j, put j.tl)` |
| Add unit tests for put statement parsing | 0.5h | Test all 4 models parse |

**Acceptance:** ps5_s_mn, ps10_s, ps10_s_mn, stdcge all parse successfully

### Day 8: Integration Testing + Buffer (2h)

**Focus:** Full regression testing, fix any issues

| Task | Time | Deliverable |
|------|------|-------------|
| Run full test suite (3204+ tests) | 0.5h | All tests pass |
| Run pipeline on newly-parsing models | 1h | Check translate/solve status |
| Fix any discovered issues | 0.5h | Buffer time |

**Acceptance:** All tests pass, no new regressions

### Day 9: Documentation + Checkpoint 3 (2h)

**Focus:** Documentation updates, retrospective draft

| Task | Time | Deliverable |
|------|------|-------------|
| Update GAMSLIB_STATUS.md | 0.5h | Reflect new metrics |
| Update FAILURE_ANALYSIS.md | 0.5h | Updated error categories |
| Draft Sprint 18 retrospective | 0.5h | Lessons learned |
| **Checkpoint 3:** All components complete | 0.5h | Final review |

**Checkpoint 3 Criteria:**
- [x] All Sprint 18 features merged
- [x] Documentation updated
- [x] Retrospective drafted
- [x] Ready for release

### Day 10: Release Prep + Final Metrics (2h)

**Focus:** Release v1.2.0 with Sprint 18 changes

| Task | Time | Deliverable |
|------|------|-------------|
| Final pipeline metrics | 0.5h | Record final counts |
| Version bump and release notes | 0.5h | v1.2.0 release |
| Create release PR | 0.5h | PR ready for merge |
| Sprint 18 complete | 0.5h | Tag and celebrate |

---

## Expected Outcomes

### Metrics Improvement

| Metric | Baseline (v1.1.0) | Expected (v1.2.0) | Change |
|--------|-------------------|-------------------|--------|
| Parse Success | 61/160 (38.1%) | 65/160 (40.6%) | +4 models |
| Translate Success | 42/61 (68.9%) | TBD | — |
| Solve Success | 12/42 (28.6%) | ≥18/TBD | +6 models |
| `path_syntax_error` | 17 | ≤6 | -11 models |

**Note:** Parse improvement is modest (+4 from put statement fix). The major gains are in solve stage from emit_gams.py fixes.

### Models Unblocked

| Fix | Models Unblocked |
|-----|------------------|
| Set element quoting | ps2_f, ps2_f_eff, ps2_f_inf, ps2_f_s, ps2_s, pollut (6) |
| Computed param skip | ajax, demo1, mathopt1, mexss, sample (5) |
| Bound multiplier dimension | alkyl, bearing, + partial overlaps (3-5) |
| Put statement format | ps5_s_mn, ps10_s, ps10_s_mn, stdcge (4) |

**Total potential improvement:** 14-16 models unblocked from `path_syntax_error`

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

### Day 6 Full Retest

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

- February 6, 2026: Initial creation (Task 10 of PREP_PLAN.md)
