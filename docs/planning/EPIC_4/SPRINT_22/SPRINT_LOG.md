# Sprint 22 Log

**Sprint Duration:** 15 days (Day 0 – Day 14)
**Start Date:** 2026-03-06
**Baseline Commit:** `53ac5979` (PR #996 merge commit)

---

## Baseline Metrics (Day 0)

**Test Suite:** 3,957 passed, 10 skipped, 1 xfailed

| Metric | Baseline | Target | Stretch |
|---|---|---|---|
| Parse success | 154/157 (98.1%) | ≥ 154/157 | ≥ 155/157 |
| Translate success | 136/154 (88.3%) | ≥ 139/154 | — |
| Solve success | 65/136 (47.8%) | ≥ 75 | ≥ 85 |
| Match | 30/65 (46.2%) | ≥ 35 | ≥ 40 |
| path_syntax_error | 40 | ≤ 30 | ≤ 25 |
| path_solve_terminated | 12 | ≤ 5 | ≤ 3 |
| model_infeasible | 15 | ≤ 12 | ≤ 10 |
| Tests | 3,957 | ≥ 4,020 | — |

---

## Workstream to Issue Mapping

### WS1: path_syntax_error Subcategory Fixes (C, G, B)
- **Target:** path_syntax_error ≤ 30 (−10 from 40)
- **Subcategory C (10 models):** Uncontrolled set in stationarity ($149 error) — ampl, dyncge, glider, harker, korcge, paklive, robert, shale, tabora, trnspwl (#949)
- **Subcategory G (4 models):** Set index reuse conflict ($125 error) — kand, prolog, spatequ, srkandw (#894)
- **Subcategory B (2 models):** Domain violation in emitted data ($170 error) — cesam, cesam2
- **Effort:** ~5–9h

### WS2: path_solve_terminated Pre-Solver Error Fixes
- **Target:** path_solve_terminated ≤ 5 (−7 from 12)
- **Priority 1:** `_fx_` equation suppression (5 models) — etamac (#984), hhfair, otpop (#915), pak, pindyck (#893)
- **Priority 2:** Unmatched free variables (2 models) — fdesign, trussm
- **Priority 3:** `$` condition preservation (1 model) — tforss (#907)
- **Priority 4:** Stationarity domain conditioning (1 model) — springchain
- **Related:** elec (#983), lands (#986) — execution errors (stretch)
- **Effort:** ~6–10h

### WS3: model_infeasible KKT Bug Fixes
- **Target:** model_infeasible ≤ 12 (−3 from 15)
- **Exclude:** feasopt1, iobalance, meanvar, orani (permanently incompatible)
- **Fix:** whouse (lag conditioning), ibm1 (mixed-bounds), uimp (multi-solve)
- **Related:** #970 twocge (bug), chain, rocket, cpack, lnts, mathopt3, bearing
- **Effort:** ~4–8h

### WS4: Solution Divergence Investigation
- **Target:** Root cause for ≥ 1 Category A mismatch model
- **Models:** apl1p, senstran (Category A); mathopt1 (Category D)
- **Related:** #958–#964 (ps* series objective mismatches)
- **Effort:** ~2–3h

### WS5: Translation Timeout Quick Win
- **Target:** Recover egypt (#927), ferts (#928), dinam (#926)
- **Fix:** Increase subprocess timeout 60s → 150s in `scripts/gamslib/batch_translate.py`
- **Effort:** ~0.5h

### WS6: Deferred Issue #764 (mexss)
- **Target:** mexss no longer model_infeasible
- **Fix:** `sameas` guard in `_add_indexed_jacobian_terms()`
- **Effort:** ~3–4h

---

## Day-by-Day Progress

### Day 0 — Baseline Confirm + Sprint Kickoff

**Status:** COMPLETE
**Effort:** ~0.5h

| Task | Status |
|---|---|
| `make test` baseline | :white_check_mark: 3,957 passed, 10 skipped, 1 xfailed |
| SPRINT_LOG.md initialized | :white_check_mark: Baseline metrics filled, issue mapping added |
| Pipeline baseline confirmed | :white_check_mark: parse 154/157, translate 134/154, solve 64/134, match 30/64 (timing variance: 2 translate timeouts, 1 solve delta vs BASELINE_METRICS.md) |

---

### Day 1 — WS5: Timeout Quick Win + WS1: Subcategory C (Part 1)

**Status:** COMPLETE
**Effort:** ~3h

| Task | Status |
|---|---|
| Timeout increased 60s → 150s | :white_check_mark: `batch_translate.py` updated |
| Subcategory C analysis | :white_check_mark: Two failure modes identified: (1) gradient not checked, (2) scalar Jacobian path lacks check |
| Domain conditioning implemented | :white_check_mark: Two fixes in `stationarity.py`: gradient Sum wrapping + scalar Jacobian extra-index wrapping |
| ≥ 3 C models fixed | :white_check_mark: 5 models fixed (robert, dyncge, korcge, paklive, tabora) — remaining 5 have non-stationarity root causes |
| 4 integration tests | :white_check_mark: `test_stationarity_uncontrolled.py` — gradient subset wrapping, no-false-wrapping regression, scalar extra-index, scalar no-wrapping |
| Issue docs for remaining 4 models | :white_check_mark: #1002 harker, #1003 ampl, #1004 glider, #1005 shale |
| Tests | :white_check_mark: 3,961 passed (+4 from baseline), 10 skipped, 1 xfailed |

**Analysis of remaining 5 subcategory C models:**
- **harker** (#1002): Multi-dim set `arc(n,np)` as Sum domain — emitter expands body indices but not Sum domain
- **ampl** (#1003): Dollar condition `$t(tl)` missing parentheses — needs `$(t(tl))`
- **glider** (#1004): Set element `x` collides with identifier — needs quoting as `"x"`
- **trnspwl** (#949): Existing issue — `ord()` on dynamic set + unquoted labels
- **shale** (#1005): Uncontrolled set `t` in equation condition `$(ts(t,tf))` and `.fx` statements

---

### Day 2 — WS1: Subcategory C (Part 2)

**Status:** NOT STARTED
**Effort:** —

| Task | Status |
|---|---|
| Remaining C models fixed | |
| Regression testing (0 regressions) | |
| model_infeasible influx assessed | |

---

### Day 3 — WS1: Subcategories G + B

**Status:** NOT STARTED
**Effort:** —

| Task | Status |
|---|---|
| 4 subcategory G models fixed | |
| 2 subcategory B models fixed | |
| path_syntax_error ≤ 30 | |

---

### Day 4 — WS2: `_fx_` Suppression

**Status:** NOT STARTED
**Effort:** —

| Task | Status |
|---|---|
| `_fx_` suppression implemented | |
| 5 models fixed | |
| Regression testing | |

---

### Day 5 — Checkpoint 1 + WS2 Part 2

**Status:** COMPLETE
**Effort:** ~2h

**Checkpoint 1 Decision:** CONDITIONAL GO — path_syntax_error (39) and solve (66) miss targets due to WS1 Days 2-3 not completed (work redirected to WS2 cesam2/etamac fixes). Tests pass; WS2 progress is strong. Proceeding with WS2/WS3 fixes while accepting WS1 debt.

| Criterion | Target | Actual | Status |
|---|---|---|---|
| path_syntax_error | ≤ 32 | 39 | :x: (WS1 Days 2-3 not done) |
| Solve success | ≥ 70 | 66 | :x: (pre-WS2 fixes) |
| Tests | All pass | 4,138 passed | :white_check_mark: |

| Task | Status |
|---|---|
| Checkpoint 1 evaluation | :white_check_mark: CONDITIONAL GO |
| Unmatched free variables fixed (2) | :white_check_mark: fdesign (`t`), trussm (`tau`) — `_is_objective_defining_equation` now requires `=E=` and scalar domain |
| `$` condition preservation (1) | :white_check_mark: fawley — parser now wraps LHS conditions in `LhsConditionalAssign` for literal-index assignments |

**Root cause (fdesign/trussm):** `_is_objective_defining_equation()` in `src/kkt/objective.py` accepted inequality constraints (=L=) and indexed equations as "objective defining". For `minimize t` where `passband_up_bnds(i).. sum(..) =L= t`, the inequality was falsely matched. Fix: require `Rel.EQ` and empty domain.

**Root cause (fawley):** `_handle_conditional_assign_general()` in parser.py only wrapped RHS in `LhsConditionalAssign` when ALL indices resolved to sets. For `char(c,"volume")$prop(c,"gravity")`, the literal `"volume"` didn't resolve, so the condition was dropped. Fix: also wrap when indices include literals (non-offset, non-subset cases).

**Pipeline retest (--only-solve):**
- Solve: 67 (+2 from fdesign, trussm)
- Match: 32 (+2 from fdesign, trussm)
- path_solve_terminated: 9 (−3 from baseline)
- fdesign: solve SUCCESS + MATCH (obj=1.046)
- trussm: solve SUCCESS + MATCH (obj=0.45)
- fawley: still path_solve_terminated (parser fix resolved div-by-zero, but solver convergence issue remains)

**PR:** #1052

---

### Day 6 — WS2 Part 3 + Pipeline Retest

**Status:** NOT STARTED
**Effort:** —

| Task | Status |
|---|---|
| Stationarity domain conditioning | |
| Full pipeline retest | |
| model_infeasible influx assessed | |

---

### Day 7 — WS3: model_infeasible Fixes (Part 1)

**Status:** NOT STARTED
**Effort:** —

| Task | Status |
|---|---|
| 4 models permanently excluded | |
| whouse lag conditioning fixed | |
| ibm1 mixed-bounds fixed | |

---

### Day 8 — WS3 Part 2 + WS6: mexss

**Status:** NOT STARTED
**Effort:** —

| Task | Status |
|---|---|
| uimp multi-solve fixed | |
| mexss `sameas` guard fixed (#764) | |
| model_infeasible ≤ 12 | |

---

### Day 9 — WS4: Solution Divergence (Part 1)

**Status:** NOT STARTED
**Effort:** —

| Task | Status |
|---|---|
| apl1p root cause analysis | |
| senstran root cause analysis | |
| Pattern identified | |

---

### Day 10 — Checkpoint 2 + WS4 Part 2

**Status:** NOT STARTED
**Effort:** —

**Checkpoint 2 Decision:** —

| Criterion | Target | Actual | Status |
|---|---|---|---|
| path_syntax_error | ≤ 30 | — | |
| path_solve_terminated | ≤ 6 | — | |
| model_infeasible | ≤ 13 | — | |
| Solve success | ≥ 73 | — | |
| Match | ≥ 33 | — | |
| Tests | All pass | — | |

| Task | Status |
|---|---|
| Checkpoint 2 evaluation | |
| mathopt1 Category D analysis | |
| Fix strategies documented | |

---

### Day 11 — Buffer / Overflow

**Status:** NOT STARTED
**Effort:** —

| Task | Status |
|---|---|
| Overflow tasks completed | |
| Full pipeline retest | |
| Regression testing | |

---

### Day 12 — Sprint Close Prep

**Status:** NOT STARTED
**Effort:** —

| Task | Status |
|---|---|
| GitHub issues filed | |
| KNOWN_UNKNOWNS.md updated | |
| SPRINT_LOG.md updated | |

---

### Day 13 — Final Pipeline Retest + Metrics

**Status:** NOT STARTED
**Effort:** —

| Task | Status |
|---|---|
| Final pipeline retest | |
| Final metrics recorded | |
| Acceptance criteria evaluated | |

---

### Day 14 — Sprint Close + Retrospective

**Status:** NOT STARTED
**Effort:** —

| Task | Status |
|---|---|
| Retrospective written | |
| CHANGELOG.md updated | |
| PROJECT_PLAN.md KPIs updated | |
| Sprint 23 scope outlined | |

---

## Final Metrics (Day 14)

| Metric | Baseline | Target | Actual | Status |
|---|---|---|---|---|
| Parse success | 154/157 | ≥ 154/157 | — | |
| Translate success | 136/154 | ≥ 139/154 | — | |
| Solve success | 65 | ≥ 75 | — | |
| Match | 30 | ≥ 35 | — | |
| path_syntax_error | 40 | ≤ 30 | — | |
| path_solve_terminated | 12 | ≤ 5 | — | |
| model_infeasible | 15 | ≤ 12 | — | |
| Tests | 3,957 | ≥ 4,020 | — | |
