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

**Status:** COMPLETE
**Effort:** ~8h

**Key Change:** Fixed implicit lead/lag domain conditioning in stationarity builder.
Equations with IndexOffset (e.g., `delta_x_eq(n).. x(n) - x(n-1)`) have no explicit
`$` condition but GAMS silently skips out-of-range instances. The fix teaches
`_extract_all_conditioned_guard` to detect MultiplierRef nodes for lead/lag equations
and treat them as implicitly conditioned. This allows proper domain restriction on
stationarity equations without modifying the actual stationarity expression terms
(avoiding regressions like catmix).

| Task | Status |
|---|---|
| Stationarity domain conditioning (springchain) | DONE — springchain now model_optimal |
| Full pipeline retest | DONE — solve 77/141, match 35 |
| model_infeasible influx assessed | DONE — 20→22 (+2 net); 3 resolved, 5 new (from PR #1064) |

**Pipeline Metrics (Day 6):**

| Metric | Baseline | Day 6 | Delta |
|---|---|---|---|
| Solve success | 65 | 77 | +12 |
| Match | 30 | 35 | +5 |
| path_syntax_error | 40 | 25 | −15 |
| path_solve_terminated | 12 | 10 | −2 |
| model_infeasible | 20 | 22 | +2 |
| Tests | 3,957 | 4,141 | +184 |

---

### Day 7 — WS3: model_infeasible Fixes (Part 1)

**Status:** COMPLETE
**Effort:** ~4h

| Task | Status |
|---|---|
| 4 models permanently excluded | :white_check_mark: feasopt1, iobalance, meanvar, orani |
| whouse lag conditioning fixed | :white_check_mark: solve SUCCESS + MATCH (obj=-600.0) |
| ibm1 mixed-bounds fixed | :white_check_mark: solve SUCCESS, MISMATCH (obj=80.0 vs 287.1; table parsing bug) |
| Unit tests (4) | :white_check_mark: skip_lead_lag_inference (2), expr_bound guard (2) |
| Tests | :white_check_mark: 4,145 passed (+4), 10 skipped, 1 xfailed |

**Root cause (whouse):** Emitter inferred `$(ord(t) > 1)` on equality equation `sb(t)..
stock(t) =E= stock(t-1) + buy(t) - sell(t)` because it detected `stock(t-1)` lag reference.
But GAMS evaluates out-of-range lag refs as 0 (default level value), so the equation is valid
for ALL t. The condition incorrectly excluded `sb('q-1')`, fixing `nu_sb('q-1') = 0`, making
`stat_sell('q-1')` unsatisfiable. Fix: skip lead/lag condition inference for original equality
equations via `skip_lead_lag_inference=True` parameter on `emit_equation_def()`.

**Root cause (ibm1):** Two issues: (1) Double-bounding — emitting `.lo`/`.up` on primal
variables AND explicit bound complementarity equations created over-constrained MCP. Fix:
skip `.lo`/`.up` emission for variables with explicit bound complementarity. (2) Expression-
based bounds with potential infinity — `comp_up_x(s).. sup(s,"inventory") - x(s) =G= 0`
creates degenerate rows when `sup("aluminum","inventory") = INF`. Fix: guard conditions
`$(expr < inf)` / `$(expr > -inf)` on expression-based bound complementarity. Note: objective
mismatch (80 vs 287) due to table parsing bug assigning `sup(aluminum,"cost")` to wrong column.

**Pipeline Metrics (Day 7):**

| Metric | Baseline | Day 6 | Day 7 | Delta (D7-D6) |
|---|---|---|---|---|
| Solve success | 65 | 77 | 78 | +1 |
| Match | 30 | 35 | 36 | +1 |
| path_syntax_error | 40 | 25 | 25 | 0 |
| path_solve_terminated | 12 | 10 | 10 | 0 |
| model_infeasible | 20 | 22 | 17 | −5 |
| Tests | 3,957 | 4,141 | 4,145 | +4 |

---

### Day 8 — WS3 Part 2 + WS6: mexss

**Status:** COMPLETE
**Effort:** ~6h

| Task | Status |
|---|---|
| uimp + mexss `sameas` guard fixed (#764) | :white_check_mark: PR #1076 merged — multi-entry sameas guard refactor |
| ibm1 table column misalignment fixed | :white_check_mark: PR #1079 merged — gap-midpoint column matching |
| ISSUE_828 (ibm1 locally infeasible) resolved | :white_check_mark: Root cause was table misalignment (ISSUE_1074) |
| model_infeasible reduced | :white_check_mark: ibm1 now MODEL STATUS 1 (Optimal), mexss solves |

**Root cause (uimp/mexss):** `_add_indexed_jacobian_terms()` in `stationarity.py` had a
`sameas` guard that restricted scalar-constraint multiplier terms to `entries[0]` only.
For scalar equations summing over indexed variables, this dropped valid multiplier terms
for all but the first Jacobian entry. Fix: multi-entry guard with per-dimension value
collection, OR-disjunction for partial coverage, no guard when all instances covered.

**Root cause (ibm1):** Table column misalignment in `_handle_table_block()` — range-based
column matching used next column start as boundary, causing values in sparse rows to map
to wrong columns. Fix: gap-midpoint matching with source_width for right-edge computation.

**PRs:** #1076 (sameas guard), #1079 (table column alignment)

---

### Day 9 — WS4: Solution Divergence (Part 1)

**Status:** COMPLETE
**Effort:** ~2h

| Task | Status |
|---|---|
| apl1p root cause analysis | :white_check_mark: Stochastic solver (DECIS) — incomparable reference |
| apl1pca root cause analysis | :white_check_mark: Same as apl1p — identical deterministic core, different stochastic scenarios |
| senstran root cause analysis | :white_check_mark: Multi-solve with modified parameters — incomparable reference |
| jobt root cause analysis | :white_check_mark: **FIXED** by Day 7 skip_lead_lag_inference (obj matches: 21343.056) |
| aircraft root cause analysis | :white_check_mark: Multi-solve with bound changes — incomparable reference |
| sparta root cause analysis | :white_check_mark: Multi-solve + actual KKT bug (infeasible) |
| mine root cause analysis | :white_check_mark: Translation error (SetMembershipTest) — not divergence-related |
| Pattern identified | :white_check_mark: 4/7 incomparable (multi-solve/stochastic), 1 also has KKT bug (sparta), 1 already fixed (jobt), 1 translation error (mine) |

**Key Finding:** Of the 7 Category A models, 2 have genuine KKT issues and 5 do not:

- **jobt**: KKT bug — already fixed on Day 7 (skip_lead_lag_inference). Now matches.
- **sparta**: Multi-solve (4 formulations) + open KKT infeasibility bug in bal4 (#1081).
- **senstran, apl1p, apl1pca, aircraft**: Multi-solve or stochastic solver — NLP reference
  captures a different solve iteration/mode. MCP formulations are correct.
- **mine**: Pre-existing translation error (SetMembershipTest not supported).

**Impact:** +1 match (jobt). 4 models should be reclassified as "incomparable" rather than
"mismatch". Full analysis in [CATEGORY_A_DIVERGENCE_ANALYSIS](./CATEGORY_A_DIVERGENCE_ANALYSIS.md).

**Issues filed:** #1080 (multi-solve reference comparison), #1081 (sparta KKT bug)
**PR:** #1082

---

### Day 9 (continued) — ISSUE_1077 + ISSUE_1078 + ISSUE_764 Closure

**Status:** COMPLETE
**Effort:** ~2h

| Task | Status |
|---|---|
| ISSUE_1077 (uimp dollar condition boolean) fixed | :white_check_mark: PR #1083 merged — `_ensure_numeric_condition()` wraps all non-Const conditions as `1$cond` |
| ISSUE_1078 (mexss table column) confirmed fixed | :white_check_mark: Already fixed by PR #1079 |
| ISSUE_764 (mexss infeasible) confirmed fixed | :white_check_mark: Already fixed by PR #1076 |
| uimp verified: MODEL STATUS 1, obj=1571.048 | :white_check_mark: Matches NLP reference |
| mexss verified: MODEL STATUS 1, obj=538.811 | :white_check_mark: Matches NLP reference |
| Issues #764, #1077, #1078 closed | :white_check_mark: Moved to `docs/issues/completed/` |

**PR:** #1083

---

### Day 10 — Checkpoint 2 + WS4 Part 2

**Status:** COMPLETE
**Effort:** ~2h

**Checkpoint 2 Decision:** CONDITIONAL GO — Solve (74) and Match (39) exceed targets. path_syntax_error (27) passes. path_solve_terminated (15) and model_infeasible (18 excl. excluded) miss targets due to 7 regressions from Day 8/9 PRs (#1076 sameas guard, #1083 dollar condition). Regressions filed as #1084–#1090. Proceeding with sprint close while documenting regressions for Sprint 23 investigation.

| Criterion | Target | Actual | Status |
|---|---|---|---|
| path_syntax_error | ≤ 30 | 27 | :white_check_mark: |
| path_solve_terminated | ≤ 6 | 15 | :x: (+5 regressions from Day 8/9 PRs) |
| model_infeasible | ≤ 13 | 18 | :x: (+5 regressions from Day 8/9 PRs) |
| Solve success | ≥ 73 | 74 | :white_check_mark: |
| Match | ≥ 33 | 39 | :white_check_mark: |
| Tests | All pass | 4,173 passed | :white_check_mark: |

| Task | Status |
|---|---|
| Checkpoint 2 evaluation | :white_check_mark: CONDITIONAL GO |
| mathopt1 Category D analysis | :white_check_mark: Not a bug — multi-KKT-point divergence (reclassify to Category B) |
| Fix strategies documented | :white_check_mark: Category D analysis doc + 8 issues filed |

**Pipeline Metrics (Day 10):**

| Metric | Baseline | Day 7 | Day 10 | Delta (D10-D7) |
|---|---|---|---|---|
| Solve success | 65 | 78 | 74 | −4 |
| Match | 30 | 36 | 39 | +3 |
| path_syntax_error | 40 | 25 | 27 | +2 |
| path_solve_terminated | 12 | 10 | 15 | +5 |
| model_infeasible | 20 | 17 | 21 | +4 |
| Tests | 3,957 | 4,145 | 4,173 | +28 |

**Regressions (7 models, from Day 8/9 PRs #1076/#1083):**

| Model | Previous | Current | Issue |
|---|---|---|---|
| catmix | model_optimal | model_infeasible | #1084 |
| fdesign | model_optimal (match) | path_solve_terminated | #1085 |
| harker | model_optimal | path_solve_terminated | #1086 |
| hydro | model_optimal | model_infeasible | #1087 |
| pindyck | model_optimal | model_infeasible | #1088 |
| qabel | model_optimal | path_solve_terminated | #1089 |
| port | match | mismatch (obj sign flip) | #1090 |

**Improvements (6 new matches from Day 8/9 PRs):**

| Model | Previous | Current |
|---|---|---|
| ibm1 | model_infeasible | match (obj=287.1) |
| jobt | mismatch | match (obj=21343.1) |
| mexss | N/A | match (obj=538.8) |
| pdi | model_infeasible | match (obj=294070.0) |
| uimp | model_infeasible | match (obj=1571.0) |
| whouse | model_infeasible | match (obj=−600.0) |

**Net:** +6 new matches, −2 lost matches (fdesign, port) = +4 net matches.

**Category D Analysis (mathopt1):** The MCP transformation is mathematically correct. mathopt1 is a non-convex NLP with bilinear equality constraint `x1 = x1*x2`. Both (1,1) with obj=0 and (0,0) with obj=1 are valid KKT points. NLP finds local minimum (obj=1), MCP/PATH finds global minimum (obj≈0). This is the same multi-KKT-point pattern as Category B. See [CATEGORY_D_DIVERGENCE_ANALYSIS](./CATEGORY_D_DIVERGENCE_ANALYSIS.md).

**Issues filed:** #1084–#1090 (regressions), #1091 (Category D reclassification)
**PR:** #1092

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
