# Sprint 24 Detailed Plan

**Created:** 2026-04-04
**Sprint Duration:** 15 days (Day 0 – Day 14)
**Effort:** Estimate ~32–42 hours; Budget ~2.1–2.8h/day effective capacity
**Risk Level:** MEDIUM
**Baseline:** `main @ b6a8def6` — parse 147/147 (100%), translate 140/147 (95.2%), solve 86/140 (61.4%), match 49/147 (33.3%), tests 4,364

---

## Executive Summary

Sprint 24 focuses on alias-aware differentiation as the single highest-leverage workstream, with secondary work on path_syntax_error reduction, model_infeasible fixes, and translation timeout investigation. The alias differentiation architecture is already implemented (Sprint 23 PRs #1135/#1136) — Sprint 24's work is debugging edge cases and extending for offset-alias interactions.

- **WS1: Alias differentiation** (Priority 1, Days 1-7) — debug `_partial_collapse_sum` edge cases, validate across 12 issues
- **WS2: path_syntax_error reduction** (Priority 2, Days 5-9) — subcategory H batch fix (8 models), quick A fixes
- **WS3: model_infeasible reduction** (Priority 3, Days 7-10) — exclude 3 Category C, fix alias-related Category A
- **WS4: Translation timeout/error** (Priority 4, Days 8-10) — fix mine internal error, investigate iswnm/sarf
- **WS5: Pipeline retest and close** (Days 11-14) — checkpoints, sprint close, retrospective

**Process requirements (from Sprint 23 retrospective):**
- **PR6:** Full pipeline for all definitive metrics
- **PR7:** Track model_infeasible gross fixes and gross influx
- **PR8:** Absolute counts and percentages
- **PR9:** Targets against 147-model pipeline scope
- **PR10:** Budget 50-60% error influx from translate recovery
- **PR11:** Highest-leverage fix (alias diff) in Days 1-5

---

## Sprint 24 Targets

| Metric | Baseline | Target | Stretch |
|---|---|---|---|
| Parse | 147/147 (100%) | ≥ 147/147 (100%) | — |
| Translate | 140/147 (95.2%) | ≥ 143/147 (97%) | ≥ 145/147 |
| Solve | 86 | ≥ 95 | ≥ 100 |
| Match | 49 | ≥ 55 | ≥ 60 |
| path_syntax_error | 23 | ≤ 15 | ≤ 12 |
| path_solve_terminated | 12 | ≤ 10 | ≤ 8 |
| model_infeasible | 11 (pipeline) / 14 (triage) | ≤ 8 | ≤ 6 |
| Tests | 4,364 | ≥ 4,400 | — |

**Error influx budget (PR10):** If alias differentiation recovers 3 new translates, expect ~2 new solve errors (50-60% rate).

---

## Workstreams

### WS1: Alias Differentiation (Priority 1)
**Effort:** ~11-17h
**Target:** Fix 10+ of 12 alias-differentiation issues; improve match rate by 6+
**Source:** [ANALYSIS_ALIAS_DIFFERENTIATION](./ANALYSIS_ALIAS_DIFFERENTIATION.md), [DESIGN_ALIAS_DIFFERENTIATION_V2](./DESIGN_ALIAS_DIFFERENTIATION_V2.md)

| Phase | Focus | Models | Effort | Days |
|---|---|---|---|---|
| 1 | Debug Pattern A (_partial_collapse_sum edge cases) | qabel, irscge, meanvar | 4-6h | 1-3 |
| 2 | Validate Pattern A across all models | CGE set, PS-family, cclinpts | 2-3h | 3-5 |
| 3 | Extend Pattern C (offset-alias) | polygon, himmel16 | 2-3h | 5-7 |
| 4 | Investigate Patterns B/D | kand, launch | 2-3h | 7-9 |

**Regression canary:** dispatch must match before/after every phase.

### WS2: path_syntax_error Reduction (24 → ≤ 15)
**Effort:** ~8-12h
**Target:** Fix 9+ models
**Source:** [TRIAGE_PATH_SYNTAX_ERROR](./TRIAGE_PATH_SYNTAX_ERROR.md)

| Tier | Focus | Models | Effort | Days |
|---|---|---|---|---|
| 1 | Subcategory H batch fix (concrete offsets) | catmix, ferts, ganges, gangesx, partssupply, polygon, tricp, turkpow | 4-6h | 5-7 |
| 2 | Subcategory A quick fixes | decomp, ramsey, worst | 2-3h each | 7-9 |
| 3 | Investigate prolog regression | prolog | 2h | 9 |

### WS3: model_infeasible Reduction (14 → ≤ 8)
**Effort:** ~6-10h
**Target:** Fix or exclude 6+ models
**Source:** [TRIAGE_MODEL_INFEASIBLE](./TRIAGE_MODEL_INFEASIBLE.md)

| Tier | Focus | Models | Effort | Days |
|---|---|---|---|---|
| 1 | Permanent exclusion (Category C) | orani, feasopt1, iobalance | 1h | 7 |
| 2 | Alias-related Category A (via WS1) | chenery, cesam, korcge | Included in WS1 | 7-10 |
| 3 | Lead/lag Jacobian Category A | bearing, pak, rocket | 3-4h each | 9-10 |

### WS4: Translation Timeout/Error (Priority 4)
**Effort:** ~4-6h
**Target:** Fix mine internal error; investigate 1-2 timeouts
**Source:** [INVESTIGATION_TRANSLATE_TIMEOUTS](./INVESTIGATION_TRANSLATE_TIMEOUTS.md)

| Task | Model | Effort | Days |
|---|---|---|---|
| Fix mine SetMembershipTest domain mismatch | mine | 2-3h | 8 |
| Profile iswnm timeout | iswnm | 1-2h | 9 |
| Profile sarf timeout | sarf | 1-2h | 10 |

### WS5: Pipeline Retest and Close (Days 11-14)
**Effort:** ~6-8h

| Day | Task |
|---|---|
| 11 | Buffer/overflow + stretch goals |
| 12 | Sprint close prep: file deferred issues, update documentation |
| 13 | Final pipeline retest (per PR6); acceptance criteria evaluation |
| 14 | Sprint retrospective; CHANGELOG; PROJECT_PLAN KPIs |

---

## Daily Schedule

### Day 0 — Setup
- Verify baseline metrics (from BASELINE_METRICS.md)
- Generate golden-file stationarity output for all 49 matching models
- Set up dispatch regression canary test

### Day 1 — WS1 Phase 1: Debug Pattern A (qabel)
- Add debug logging to `_diff_varref` and `_partial_collapse_sum`
- Trace qabel derivative computation end-to-end
- Identify specific edge case preventing correct alias matching
- Run dispatch canary test

### Day 2 — WS1 Phase 1: Fix Pattern A Edge Case
- Implement fix for identified edge case
- Validate qabel gradient improvement
- Run dispatch canary + golden-file regression for 49 matching models

### Day 3 — WS1 Phase 2: Validate Pattern A
- Test all Pattern A models (irscge, meanvar, CGE set, PS-family, cclinpts)
- Run full pipeline regression on solving models
- Document which models improved

### Day 4 — WS1 Phase 2: Continue Validation
- Test remaining Pattern A models
- Fix any secondary issues discovered
- Run quality gate: `make typecheck && make lint && make format && make test`

### Day 5 — Checkpoint 1 + WS1 Phase 3 Start
**Checkpoint 1 evaluation:**

| Criterion | GO | CONDITIONAL GO | NO-GO |
|---|---|---|---|
| Alias regression | 0 regressions | ≤ 1 regression | > 1 regression |
| Pattern A improvement | ≥ 3 models improved | ≥ 1 model improved | 0 models improved |
| Tests | All pass | All pass | Failures |

- Begin WS1 Phase 3: Pattern C (offset-alias) — polygon, himmel16
- Begin WS2 Tier 1: Subcategory H batch fix

### Day 6 — WS1 Phase 3 + WS2 Tier 1
- Continue offset-alias fix for polygon, himmel16
- Continue subcategory H batch fix (concrete offsets)
- Run regression tests

### Day 7 — WS2 Tier 1 + WS3 Tier 1
- Complete subcategory H batch fix
- WS3: Exclude 3 Category C models (orani, feasopt1, iobalance)
- Check if WS1 alias fix resolved any WS3 models (chenery, cesam, korcge)

### Day 8 — WS2 Tier 2 + WS4
- WS2: Fix subcategory A models (decomp, ramsey, worst)
- WS4: Fix mine internal error (SetMembershipTest domain mismatch)
- Run quality gate

### Day 9 — WS1 Phase 4 + WS2 Tier 3 + WS4
- WS1 Phase 4: Investigate kand (Pattern B) and launch (Pattern D)
- WS2 Tier 3: Investigate prolog regression
- WS4: Profile iswnm timeout

### Day 10 — Checkpoint 2 + WS3 Tier 3
**Checkpoint 2 evaluation:**

| Criterion | GO | CONDITIONAL GO | NO-GO |
|---|---|---|---|
| Solve | ≥ 92 | ≥ 89 | < 89 (regression) |
| Match | ≥ 52 | ≥ 50 | < 49 (regression) |
| path_syntax_error | ≤ 18 | ≤ 20 | > 23 (regression) |
| Tests | All pass | All pass | Failures |

- WS3 Tier 3: Fix bearing, pak, rocket (if time permits)
- WS4: Profile sarf timeout (if time permits)

### Day 11 — Buffer / Overflow
- Complete any unfinished tasks from Days 1-10
- Stretch goals: additional model fixes
- Run full pipeline retest

### Day 12 — Sprint Close Prep
- File issues for deferred items (label `sprint-25`)
- Update KNOWN_UNKNOWNS.md with end-of-sprint discoveries
- Update SPRINT_LOG.md with current metrics

### Day 13 — Final Pipeline Retest
- Run `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
- Record definitive final metrics (per PR6)
- Evaluate all acceptance criteria
- Track model_infeasible gross fixes/influx (per PR7)

### Day 14 — Sprint Close + Retrospective
- Write Sprint 24 Retrospective
- Update CHANGELOG.md
- Update PROJECT_PLAN.md Rolling KPIs
- Sprint 25 recommendations

---

## Contingency Plans

### Risk 1: Alias Differentiation Regression
**Trigger:** dispatch or other matching model regresses after WS1 changes
**Action:** Revert the specific change, isolate the regression cause, implement targeted fix with narrower scope
**Fallback:** Skip the pattern that causes regression; focus on patterns that are safe

### Risk 2: Error Influx from Translate Recovery
**Trigger:** > 3 new solve errors from recovered translates
**Action:** Classify new errors; if they're in already-triaged subcategories, add to existing fix queue. If new subcategory, file issues and defer.
**Budget:** 50-60% of new translates → solve errors (per PR10)

### Risk 3: Subcategory H Batch Fix Doesn't Work
**Trigger:** Concrete offset fix doesn't resolve 8 models
**Action:** Fall back to per-model fixes for the simplest H models (catmix, polygon). Redirect effort to subcategory A quick fixes to still reach ≤ 15 target.

---

## Workstream to Issue Mapping

### WS1: Alias Differentiation
- #1137 (qabel/abel), #1138 (CGE models), #1139 (meanvar), #1140 (PS-family)
- #1141 (kand), #1142 (launch), #1143 (polygon), #1144 (catmix)
- #1145 (cclinpts), #1146 (himmel16), #1147 (camshape), #1150 (AD regression)

### WS2: path_syntax_error
- Subcategory H: catmix, ferts, ganges, gangesx, partssupply, polygon, tricp, turkpow
- Subcategory A: decomp, ramsey, worst
- Subcategory G: prolog

### WS3: model_infeasible
- Exclude: orani (#765), feasopt1, iobalance
- Fix via WS1: chenery (#1177), cesam (#1041), korcge (#1138)
- Fix directly: bearing (#1199), pak (#1049), rocket (#1134)

### WS4: Translation
- Fix: mine (SetMembershipTest domain mismatch)
- Investigate: iswnm, sarf
