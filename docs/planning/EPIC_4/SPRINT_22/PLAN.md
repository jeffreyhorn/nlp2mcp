# Sprint 22 Detailed Plan

**Created:** 2026-03-06
**Sprint Duration:** 15 days (Day 0 – Day 14)
**Effort:** Budget ~24–30 hours (~1.6–2.0h/day effective capacity); estimated range ~23.5–38.5h
**Risk Level:** MEDIUM
**Baseline:** `53ac5979` — parse 154/157 (98.1%), translate 136/154 (88.3%), solve 65/136 (47.8%), match 30/65 (46.2%), tests 3,957

---

## Executive Summary

Sprint 22 focuses on reducing pre-solver errors to increase solve count and match rate. The primary workstreams target the three largest solve-failure categories: path_syntax_error (WS1, 16 models from subcategories C/G/B), path_solve_terminated (WS2, 8–12 models from MCP pairing and execution errors), and model_infeasible (WS3, 3–4 models from KKT bugs). A secondary workstream (WS4) investigates existing solution divergence for Category A/D mismatch models. WS5 applies a quick-win subprocess timeout increase to recover 3 translation timeouts. WS6 addresses the single included deferred issue (#764 mexss).

The PATH Solver Tuning component from PROJECT_PLAN.md (4–6h) has been **invalidated** by Sprint 21 findings: all 12 path_solve_terminated models fail before PATH runs (MCP pairing/execution errors, not solver convergence). The budget is redirected to pre-solver error fixes (WS1/WS2).

**Revised total effort from prep findings: ~24–30h** (aligned with PROJECT_PLAN.md estimate; refocused from solver tuning to pre-solver fixes).

### Key Scope Decisions vs. PROJECT_PLAN.md

| Workstream | PROJECT_PLAN.md Estimate | Sprint 22 Plan | Decision |
|---|---|---|---|
| KKT Correctness Fixes | 8–10h | 8–12h (WS1+WS3) | IN SCOPE — redirected to path_syntax_error subcategory C/G/B + model_infeasible Category A |
| PATH Solver Tuning | 4–6h | 0h | INVALIDATED — all path_solve_terminated models fail before PATH runs; budget → WS2 pre-solver fixes |
| MCP-NLP Solution Divergence Analysis | 6–8h | 2–3h (WS4) | REDUCED — Task 9 completed bulk analysis; Sprint 22 investigates 2–3 representative models only |
| Parse Completion Final Push | 4h | 0h | DESCOPED — parse rate already 98.1% (154/157); remaining 3 models are intractable lexer issues |
| Pipeline Retest | 2h | 2h | IN SCOPE — after each major workstream |
| Starting Point Improvements | 2–3h | 0h | DEFERRED — warm-start requires multi-solve infrastructure; defer to Sprint 23 |
| Translation timeout quick win | not planned | 0.5h (WS5) | ADDED — increase subprocess timeout 60s→150s; recovers egypt, ferts, dinam |
| Deferred issue #764 (mexss) | 8–12h | 3–4h (WS6) | INCLUDED — reduced scope per Task 6 decision |

---

## Sprint 22 Targets

| Metric | Baseline | Target | Stretch |
|---|---|---|---|
| path_syntax_error | 40 | ≤ 30 | ≤ 25 |
| path_solve_terminated | 12 | ≤ 5 | ≤ 3 |
| model_infeasible | 15 | ≤ 12 | ≤ 10 |
| Solve success | 65 | ≥ 75 | ≥ 85 |
| Match | 30 | ≥ 35 | ≥ 40 |
| Tests | 3,957 | ≥ 4,020 | — |
| Parse success | 154/157 | ≥ 154/157 | ≥ 155/157 |
| Translate success | 136/154 | ≥ 139/154 | — |

**Solve target rationale:** path_syntax_error fixes (+10 from subcategories C/G/B) + path_solve_terminated fixes (+7 from MCP pairing errors) + model_infeasible fixes (+3 from Category A) = +20 optimistic → target ≥ 75 (conservative: +10 from committed path_syntax_error alone).

**Match target rationale:** +10 newly-solving models × 50% expected match rate = +5 new matches → target ≥ 35. Optimistic: +20 newly-solving × 70% + 2–5 existing mismatch fixes = +19–21 → stretch ≥ 40. See [MATCH_RATE_ANALYSIS](./MATCH_RATE_ANALYSIS.md) Section 4.

**Risk: model_infeasible inflation** — path_syntax_error fixes may expose 7–14 models that shift to model_infeasible (KU-24). Sprint 22 addresses this by scheduling WS3 (model_infeasible fixes) after WS1 (path_syntax_error fixes) and building buffer capacity.

---

## Workstreams

### WS1: path_syntax_error Subcategory Fixes (C, G, B)
**Effort:** ~5–9h
**Target:** path_syntax_error ≤ 30 (−10 models from 40)
**Source:** [PATH_SYNTAX_ERROR_FIX_DESIGN](./PATH_SYNTAX_ERROR_FIX_DESIGN.md)

| Subcategory | Models | Effort | Files |
|---|---|---|---|
| C: Uncontrolled set ($149) | 10 | 3–5h | `src/kkt/stationarity.py` (~110 LOC) |
| G: Set index reuse ($125) | 4 | 1–2h | `src/emit/expr_to_gams.py` (~100 LOC) |
| B: Domain violation ($170) | 2 | 1–2h | `src/emit/original_symbols.py` (~70 LOC) |

**Implementation order:** C → G → B (highest leverage first)

**Acceptance criteria:** path_syntax_error ≤ 30; no regression in existing 65 solving models.

### WS2: path_solve_terminated Pre-Solver Error Fixes
**Effort:** ~6–10h
**Target:** path_solve_terminated ≤ 5 (−7 models from 12)
**Source:** [PATH_SOLVE_TERMINATED_STATUS](./PATH_SOLVE_TERMINATED_STATUS.md)

| Priority | Fix | Models | Effort |
|---|---|---|---|
| 1 | `_fx_` equation suppression | 5 | 2–3h |
| 2 | Unmatched free variable pairing | 2 | 2h |
| 3 | `$` condition preservation | 1 | 1–2h |
| 4 | Stationarity domain conditioning | 1 | 1–2h |

**Acceptance criteria:** path_solve_terminated ≤ 5; all 8 MCP pairing error models addressed.

### WS3: model_infeasible KKT Bug Fixes
**Effort:** ~4–8h
**Target:** model_infeasible ≤ 12 (−3 models from 15)
**Source:** [MODEL_INFEASIBLE_TRIAGE](./MODEL_INFEASIBLE_TRIAGE.md)

| Priority | Fix | Model | Effort |
|---|---|---|---|
| 1 | Lag reference conditioning | whouse | 1–2h |
| 2 | Mixed-bounds multipliers | ibm1 | 2–3h |
| 3 | Multi-solve objective | uimp | 2–3h |
| 4 | `sameas` guard refactor (#764) | mexss | 3–4h (WS6) |

**Permanently exclude 4 models:** feasopt1 (intentionally infeasible), iobalance/meanvar (multi-model incompatible), orani (linearized CGE)

**Acceptance criteria:** model_infeasible ≤ 12 (net, accounting for potential influx from WS1 fixes); whouse, ibm1, uimp no longer infeasible.

### WS4: Solution Divergence Investigation
**Effort:** ~2–3h
**Target:** Investigate 2–3 representative models from Category A/D mismatches
**Source:** [MATCH_RATE_ANALYSIS](./MATCH_RATE_ANALYSIS.md) Sections 2.2, 2.5

| Investigation | Models | Goal |
|---|---|---|
| LP KKT derivation pattern | apl1p, senstran | Identify shared root cause for 7 verified_convex mismatches |
| Zero MCP objective pattern | mathopt1 | Identify why objective terms are missing in MCP |

**Acceptance criteria:** Root cause identified for at least one Category A model; fix strategy documented (implementation in Sprint 23 if complex).

### WS5: Translation Timeout Quick Win
**Effort:** ~0.5h
**Target:** Recover 3 near-miss timeout models
**Source:** [TRANSLATION_TIMEOUT_PROFILE](./TRANSLATION_TIMEOUT_PROFILE.md)

- Increase subprocess timeout from 60s → 150s
- Expected recoveries: egypt (60s), ferts (106s), dinam (135s)

**Acceptance criteria:** egypt, ferts, dinam translate successfully; no regression.

### WS6: Deferred Issue #764 (mexss)
**Effort:** ~3–4h
**Target:** mexss no longer model_infeasible
**Source:** [DEFERRED_ISSUES_DECISION](./DEFERRED_ISSUES_DECISION.md)

- Fix `sameas` guard in `_add_indexed_jacobian_terms()` for accounting variable stationarity
- Part of WS3 model_infeasible Category A fixes

**Acceptance criteria:** mexss solves (PATH status 1); model_infeasible count reduced by 1.

---

## Revised Effort Summary

| Workstream | Revised Estimate | Notes |
|---|---|---|
| WS1: path_syntax_error C/G/B | 5–9h | 16 models; subcategory C is highest leverage |
| WS2: path_solve_terminated fixes | 6–10h | 8–12 models; `_fx_` suppression is highest priority |
| WS3: model_infeasible fixes | 4–8h | 3–4 models + permanent exclusions |
| WS4: Solution divergence investigation | 2–3h | 2–3 representative models |
| WS5: Timeout quick win | 0.5h | One-line change |
| WS6: Deferred #764 (mexss) | 3–4h | Included in WS3 effort (not additive) |
| Pipeline retest | 2h | After each major workstream completion |
| Sprint close + retrospective | 1h | Day 14 |
| **Total (workstreams only)** | **~20.5–33.5h** | WS6 overlaps WS3; counted once |
| Sprint overhead (Day 0 kickoff, checkpoints, buffer) | ~3–5h | |
| **Total (full sprint)** | **~23.5–38.5h** | Budget: 24–30h; contingency plans if over |

---

## 15-Day Schedule

### Day 0 — Baseline Confirm + Sprint Kickoff

**Theme:** Verify clean baseline, read PLAN.md, confirm all tests pass
**Effort:** 1h

| Task | Deliverable |
|---|---|
| `make test` — confirm 3,957 passed | Clean baseline |
| Review PLAN.md and all prep task deliverables | Plan internalized |
| Create SPRINT_LOG.md from template | Sprint log initialized |
| Run pipeline: `.venv/bin/python scripts/gamslib/run_full_test.py --quiet` | Baseline confirmed |

**Day 0 criterion:** All tests pass; SPRINT_LOG.md created; baseline matches BASELINE_METRICS.md.

**Day 0 status:** COMPLETE — `make test` 3,957 passed; pipeline confirmed parse 154/157, translate 134/154 (2 timing-sensitive timeouts vs baseline 136), solve 64/134, match 30/64; SPRINT_LOG.md initialized with baseline metrics and issue mapping.

---

### Day 1 — WS5: Timeout Quick Win + WS1: Subcategory C (Part 1)

**Theme:** Low-hanging fruit first; begin highest-leverage path_syntax_error fix
**Effort:** 2–3h

| Task | Files | Deliverable |
|---|---|---|
| WS5: Increase subprocess timeout 60s → 150s | `scripts/gamslib/batch_translate.py` | egypt, ferts, dinam translate |
| WS1/C: Analyze `_collect_free_indices()` in stationarity.py | `src/kkt/stationarity.py` | Understand uncontrolled set root cause |
| WS1/C: Implement domain conditioning for uncontrolled sets | `src/kkt/stationarity.py` | First 3–5 of 10 subcategory C models fixed |
| Unit tests for domain conditioning | `tests/unit/kkt/` | ≥ 3 tests |

**End of Day 1 criterion:** Timeout increased; ≥ 3 subcategory C models no longer have $149 error.

**Day 1 status:** COMPLETE — Timeout increased 60s→150s; 5/10 subcategory C models fixed (robert, dyncge, korcge, paklive, tabora) via two stationarity.py fixes (gradient Sum wrapping + scalar Jacobian extra-index wrapping); remaining 5 have non-stationarity root causes (issues #1002–#1005, #949); 4 integration tests added; 3,961 tests pass.

---

### Day 2 — WS1: Subcategory C (Part 2)

**Theme:** Complete subcategory C fixes
**Effort:** 2–3h

| Task | Files | Deliverable |
|---|---|---|
| WS1/C: Handle remaining uncontrolled set patterns | `src/kkt/stationarity.py` | All 10 subcategory C models addressed |
| WS1/C: Regression testing on all 65 solving models | pipeline | No regressions |
| Pipeline retest for subcategory C models | `gamslib_status.json` | Updated solve counts |

**End of Day 2 criterion:** All 10 subcategory C models no longer have $149 error; 0 regressions in solving models.

---

### Day 3 — WS1: Subcategories G + B

**Theme:** Complete path_syntax_error fixes
**Effort:** 2–3h

| Task | Files | Deliverable |
|---|---|---|
| WS1/G: Track nested bound indices + case-insensitive collision detection | `src/emit/expr_to_gams.py` | 4 subcategory G models fixed |
| WS1/B: Add `_is_in_domain()` filter | `src/emit/original_symbols.py` | 2 subcategory B models fixed |
| Unit tests for G + B fixes | `tests/unit/emit/` | ≥ 4 tests |
| Full pipeline retest | `gamslib_status.json` | path_syntax_error count updated |

**End of Day 3 criterion:** path_syntax_error ≤ 30; all 16 targeted models addressed.

---

### Day 4 — WS2: path_solve_terminated (Part 1: `_fx_` Suppression)

**Theme:** Fix highest-priority MCP pairing error
**Effort:** 2–3h

| Task | Files | Deliverable |
|---|---|---|
| WS2: Implement `_fx_` equation suppression for fixed variables | `src/kkt/stationarity.py` or `src/emit/emit_gams.py` | 5 models no longer have MCP pairing errors |
| Unit tests for `_fx_` suppression | `tests/unit/kkt/` | ≥ 3 tests |
| Pipeline retest for affected models | pipeline | Updated solve status |

**End of Day 4 criterion:** 5 `_fx_` models solve or advance to next error category.

---

### Day 5 — Checkpoint 1 + WS2: path_solve_terminated (Part 2)

**Theme:** Checkpoint 1 GO/NO-GO; continue path_solve_terminated fixes
**Effort:** 2–3h

#### Checkpoint 1 (Day 5) GO/NO-GO Criteria

| Criterion | GO threshold | NO-GO action |
|---|---|---|
| path_syntax_error | ≤ 32 | Defer WS2; focus on remaining WS1 fixes |
| Solve success | ≥ 70 | Investigate regressions before proceeding |
| Tests | All pass | Block on test failures |
| WS1 PR | Merged | Complete before Day 6 |

**If GO:** Proceed with WS2 Part 2 and WS3.
**If NO-GO (path_syntax_error > 32):** Redirect Days 6–7 to remaining WS1 debugging.

| Task | Files | Deliverable |
|---|---|---|
| Checkpoint 1 evaluation | — | GO/NO-GO decision |
| WS2: Fix unmatched free variable pairing | `src/kkt/stationarity.py` | 2 models fixed |
| WS2: Fix `$` condition preservation | `src/emit/emit_gams.py` | 1 model fixed |

**End of Day 5 criterion:** Checkpoint 1 GO; path_solve_terminated ≤ 7.

---

### Day 6 — WS2: path_solve_terminated (Part 3) + Pipeline Retest

**Theme:** Complete path_solve_terminated fixes; full pipeline retest
**Effort:** 2–3h

| Task | Files | Deliverable |
|---|---|---|
| WS2: Fix stationarity domain conditioning | `src/kkt/stationarity.py` | 1 model fixed |
| WS2: Address execution error models (4) if time | various | Bonus fixes |
| Full pipeline retest | `gamslib_status.json` | Updated metrics |
| Assess model_infeasible influx from WS1/WS2 fixes | pipeline output | Quantify KU-24 impact |

**End of Day 6 criterion:** path_solve_terminated ≤ 5; model_infeasible influx assessed.

---

### Day 7 — WS3: model_infeasible Fixes (Part 1)

**Theme:** Fix highest-priority model_infeasible KKT bugs
**Effort:** 2–3h

| Task | Files | Deliverable |
|---|---|---|
| WS3: Exclude 4 permanently incompatible models from pipeline | `scripts/gamslib/` config | feasopt1, iobalance, meanvar, orani excluded |
| WS3: Fix whouse lag reference conditioning | `src/kkt/stationarity.py` | whouse no longer infeasible |
| WS3: Fix ibm1 mixed-bounds multipliers | `src/kkt/stationarity.py` | ibm1 no longer infeasible |
| Unit tests | `tests/unit/kkt/` | ≥ 2 tests |

**End of Day 7 criterion:** whouse, ibm1 solve; model_infeasible reduced.

---

### Day 8 — WS3: model_infeasible Fixes (Part 2) + WS6: mexss

**Theme:** Complete model_infeasible fixes; address deferred #764
**Effort:** 2–3h

| Task | Files | Deliverable |
|---|---|---|
| WS3: Fix uimp multi-solve objective | `src/ir/parser.py` or `src/emit/emit_gams.py` | uimp no longer infeasible |
| WS6: Fix mexss `sameas` guard (#764) | `src/kkt/stationarity.py` | mexss solves |
| Unit tests | `tests/unit/` | ≥ 2 tests |
| Pipeline retest | `gamslib_status.json` | model_infeasible ≤ 12 |

**End of Day 8 criterion:** model_infeasible ≤ 12; uimp and mexss solve.

---

### Day 9 — WS4: Solution Divergence Investigation (Part 1)

**Theme:** Investigate verified_convex mismatch root causes
**Effort:** 2–3h

| Task | Files | Deliverable |
|---|---|---|
| WS4: Analyze apl1p LP KKT derivation | MCP output + NLP reference | Root cause documented |
| WS4: Analyze senstran transportation model | MCP output + NLP reference | Root cause documented |
| WS4: Compare KKT equations to expected formulation | analysis notes | Pattern identified |

**End of Day 9 criterion:** Root cause identified for ≥ 1 Category A model; fix complexity estimated.

**Day 9 status:** COMPLETE — All 7 Category A models analyzed. 1/7 (jobt) was a genuine KKT bug already fixed on Day 7. 4/7 (senstran, apl1p, apl1pca, aircraft) are multi-solve/stochastic reference comparison issues (#1080). 1/7 (sparta) is multi-solve AND has an additional KKT bug (#1081). 1/7 (mine) is a pre-existing translation error. See [CATEGORY_A_DIVERGENCE_ANALYSIS](./CATEGORY_A_DIVERGENCE_ANALYSIS.md).

---

### Day 10 — Checkpoint 2 + WS4: Solution Divergence (Part 2)

**Theme:** Checkpoint 2 GO/NO-GO; complete divergence investigation
**Effort:** 2–3h

#### Checkpoint 2 (Day 10) GO/NO-GO Criteria

| Criterion | GO threshold | NO-GO action |
|---|---|---|
| path_syntax_error | ≤ 30 | Focus remaining days on WS1 debugging |
| path_solve_terminated | ≤ 6 | Acceptable; continue with WS4 |
| model_infeasible | ≤ 13 | Acceptable; investigate influx models |
| Solve success | ≥ 73 | If < 73: redirect to solve debugging |
| Match | ≥ 33 | If < 33: prioritize match investigation |
| Tests | All pass | Block on failures |

**If GO:** Proceed with WS4 completion and sprint close prep.
**If NO-GO on any metric:** Redirect Days 11–12 to the failing workstream.

| Task | Files | Deliverable |
|---|---|---|
| Checkpoint 2 evaluation | — | GO/NO-GO decision |
| WS4: Investigate mathopt1 zero MCP objective | MCP output | Category D root cause documented |
| WS4: Document fix strategies for Categories A/D | analysis doc | Sprint 23 backlog items |

**End of Day 10 criterion:** Checkpoint 2 evaluated; solution divergence investigation complete.

**Day 10 status:** COMPLETE — Checkpoint 2 CONDITIONAL GO (solve 74 ≥ 73, match 39 ≥ 33, path_syntax_error 27 ≤ 30 pass; path_solve_terminated 15 and model_infeasible 18 miss targets due to 7 regressions from Day 8/9 PRs). Category D analysis complete: mathopt1 is multi-KKT-point divergence, not a bug. 8 issues filed (#1084–#1091).

---

### Day 11 — Buffer / Overflow

**Theme:** Address any overflows from Days 1–10; regression testing
**Effort:** 1–2h

| Task | Deliverable |
|---|---|
| Complete any unfinished workstream tasks | All WS targets met |
| Full pipeline retest | Final pre-close metrics |
| Regression testing on all solving models | No regressions confirmed |
| Address any new issues uncovered by pipeline retest | Issues filed |

**End of Day 11 criterion:** All workstream targets met or documented as blocked; regression-free.

**Day 11 status:** COMPLETE — All 7 Day 10 regressions restored to model_optimal (PRs #1094–#1097); qabel's remaining objective mismatch tracked separately in #1089. Pipeline: solve 80 (≥75 ✓), match 41 (≥40 stretch ✓), model_infeasible 9 (≤10 stretch ✓). path_syntax_error 31 (≤30 miss by 1), path_solve_terminated 7 (≤5 miss by 2). Tests: 4,206 passed.

---

### Day 12 — Sprint Close Prep: Issues + Documentation

**Theme:** File issues for deferred items; update documentation
**Effort:** 1–2h

| Task | Deliverable |
|---|---|
| File issues for all deferred/blocked items | GitHub issues filed with sprint-23 label |
| Document any new known unknowns discovered | KNOWN_UNKNOWNS.md updated |
| Update SPRINT_LOG.md with current metrics | Sprint log current |
| Run `make test` | All tests pass |

**End of Day 12 criterion:** All deferred items have GitHub issues; SPRINT_LOG.md updated.

**Day 12 status:** COMPLETE — 24 issues labeled `sprint-23` (22 existing + 2 new: #1111 alias-aware differentiation, #1112 dollar-condition propagation). KNOWN_UNKNOWNS.md updated with KU-27 through KU-30. SPRINT_LOG.md updated with final metrics. Days 12–13 marked complete in PLAN.md. `make test` passes (4,209 tests).

---

### Day 13 — Sprint Close Prep + Final Pipeline Retest

**Theme:** Combined close prep and final metrics
**Effort:** 1–2h

| Task | Deliverable |
|---|---|
| Final full pipeline retest | Updated `gamslib_status.json` |
| Record final metrics vs. targets | SPRINT_LOG.md complete |
| Verify all acceptance criteria | Criteria checklist |

**End of Day 13 criterion:** Final metrics recorded; all acceptance criteria evaluated.

**Day 13 status:** COMPLETE — Combined with Day 12 close prep. Final metrics recorded in SPRINT_LOG.md. 5/8 targets met (2 beat stretch: Match ≥ 40, model_infeasible ≤ 10). 3 narrow misses (parse 98.0% vs ≥ 98.1%, path_syntax_error by 1, path_solve_terminated by 2).

---

### Day 14 — Sprint Close + Retrospective

**Theme:** Sprint retrospective; Sprint 23 recommendations
**Effort:** 1–2h

| Task | Deliverable |
|---|---|
| Write Sprint 22 Retrospective | `docs/planning/EPIC_4/SPRINT_22/SPRINT_RETROSPECTIVE.md` |
| Update CHANGELOG.md with sprint summary | CHANGELOG.md |
| Update PROJECT_PLAN.md Rolling KPIs | KPI table updated |
| Sprint 23 recommendations | Documented in retrospective |

**End of Day 14 criterion:** Retrospective written; CHANGELOG.md updated; Sprint 23 scope outlined.

---

## Checkpoints Summary

### Checkpoint 1 (Day 5)

| Criterion | Target | Fallback if missed |
|---|---|---|
| path_syntax_error | ≤ 32 | Defer WS2; debug remaining WS1 fixes |
| Solve success | ≥ 70 | Investigate regressions before proceeding |
| WS1 PR merged | Yes | Complete before Day 6 (Day 5 buffer) |
| All tests pass | Yes | Block on failures |

### Checkpoint 2 (Day 10)

| Criterion | Target | Fallback if missed |
|---|---|---|
| path_syntax_error | ≤ 30 | Redirect Days 11–12 to WS1 debugging |
| path_solve_terminated | ≤ 6 | Acceptable; continue sprint close |
| model_infeasible | ≤ 13 | Investigate WS1 influx models |
| Solve success | ≥ 73 | Redirect to solve debugging |
| Match | ≥ 33 | Prioritize match investigation |
| All tests pass | Yes | Block on failures |

---

## Contingency Plans

### Contingency 1: WS1 Subcategory C takes longer than expected (> 5h)

**Trigger:** By end of Day 2, fewer than 7 of 10 subcategory C models fixed.
**Action:** Defer subcategories G and B to Days 11–12. Reduce path_syntax_error target to ≤ 33. Redirect Day 3 to WS2 `_fx_` suppression (highest leverage).

### Contingency 2: model_infeasible influx from WS1 fixes (KU-24)

**Trigger:** After WS1 pipeline retest, model_infeasible increases by > 5 models.
**Action:** Triage newly-infeasible models immediately (Day 3 or 6). Determine if any share root cause with WS3 fixes (whouse/ibm1/uimp patterns). If > 8 new infeasible: accept model_infeasible > 12 and document for Sprint 23.

### Contingency 3: WS2 `_fx_` suppression has broad regression impact

**Trigger:** `_fx_` fix causes > 2 regressions in currently-solving models.
**Action:** Revert; implement narrower fix with model-specific guards. Use Day 5 checkpoint buffer for investigation. If unfixable by Day 6: defer WS2 to Sprint 23.

### Contingency 4: mexss #764 fix is more complex than 3–4h

**Trigger:** By end of Day 8, mexss still infeasible after 4h of work.
**Action:** File updated issue with detailed diagnosis. Defer to Sprint 23. Do not exceed 5h on this single model.

---

## Open Risks

### Risk 1: path_syntax_error → model_infeasible Cascade (KU-24)

**Status:** HIGH — Task 1 confirmed 7–14 models at risk of shifting to model_infeasible when syntax errors are fixed.
**Mitigation:** Schedule WS3 after WS1; triage influx immediately; build buffer in model_infeasible target.

### Risk 2: `_fx_` Equation Suppression Breadth (KU-03)

**Status:** MEDIUM — Fix affects all models with fixed variables; could suppress needed equations.
**Mitigation:** Regression test all 65 solving models; add model-specific guards if needed.

### Risk 3: Subcategory C Fix Complexity (KU-01)

**Status:** LOW — Task 7 design is detailed (~110 LOC); single root cause (KKT domain propagation).
**Mitigation:** Start with simplest model; validate fix pattern before applying to all 10 models.

---

## Acceptance Criteria

### Per-Workstream

| Workstream | Acceptance Criteria |
|---|---|
| WS1: path_syntax_error C/G/B | path_syntax_error ≤ 30; 16 targeted models addressed; no regression in 65 solving models |
| WS2: path_solve_terminated | path_solve_terminated ≤ 5; 8 MCP pairing error models addressed |
| WS3: model_infeasible | model_infeasible ≤ 12 (net); whouse, ibm1, uimp solve; 4 models permanently excluded |
| WS4: Divergence investigation | Root cause identified for ≥ 1 Category A model; fix strategy documented |
| WS5: Timeout | egypt, ferts, dinam translate; timeout increased to 150s |
| WS6: Deferred #764 | mexss solves (PATH status 1) |

### Sprint-Level

- path_syntax_error ≤ 30 (from 40)
- path_solve_terminated ≤ 5 (from 12)
- model_infeasible ≤ 12 (from 15)
- Solve success ≥ 75 (from 65)
- Match ≥ 35 (from 30)
- Tests ≥ 4,020 (from 3,957)
- Parse success ≥ 154/157 (maintained)
- Zero regressions: all existing 65 solving models maintained
- All KKT fixes have unit tests

---

## Files Reference

| File | Purpose |
|---|---|
| [BASELINE_METRICS](./BASELINE_METRICS.md) | Baseline numbers (commit 53ac5979) |
| [PATH_SYNTAX_ERROR_STATUS](./PATH_SYNTAX_ERROR_STATUS.md) | path_syntax_error catalog and subcategory breakdown |
| [PATH_SYNTAX_ERROR_FIX_DESIGN](./PATH_SYNTAX_ERROR_FIX_DESIGN.md) | Fix design for subcategories C, G, B |
| [PATH_SOLVE_TERMINATED_STATUS](./PATH_SOLVE_TERMINATED_STATUS.md) | path_solve_terminated classification |
| [MODEL_INFEASIBLE_TRIAGE](./MODEL_INFEASIBLE_TRIAGE.md) | model_infeasible triage and fix priorities |
| [TRANSLATION_TIMEOUT_PROFILE](./TRANSLATION_TIMEOUT_PROFILE.md) | Translation timeout analysis |
| [DEFERRED_ISSUES_DECISION](./DEFERRED_ISSUES_DECISION.md) | Deferred issues scope decision |
| [MATCH_RATE_ANALYSIS](./MATCH_RATE_ANALYSIS.md) | Match rate improvement opportunities |
| [KNOWN_UNKNOWNS](./KNOWN_UNKNOWNS.md) | Open risks and verified assumptions |
