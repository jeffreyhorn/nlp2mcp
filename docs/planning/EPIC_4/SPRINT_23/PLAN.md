# Sprint 23 Detailed Plan

**Created:** 2026-03-20
**Sprint Duration:** 15 days (Day 0 – Day 14)
**Effort:** Estimate ~36–48 hours; Budget ~32–44 hours (~2.1–2.9h/day effective capacity)
**Risk Level:** MEDIUM
**Baseline:** `main @ 2c33989e` — parse 156/160 (97.5%), translate 139/156 (89.1%), solve 89/139 (64.0%), match 47/160 (29.4%), tests 4,209

---

## Executive Summary

Sprint 23 targets the largest combined solve and match improvement in Epic 4 history: solve 89 → ≥ 100 (+11) and match 47 → ≥ 55 (+8). Five priority areas are organized into 5 workstreams:

- **WS1: path_solve_terminated reduction** (10 → ≤ 5) — fix 7 models via execution error fixes + dollar-condition propagation (#1112)
- **WS2: model_infeasible reduction** (12 → ≤ 8) — fix 5 Tier 1 models with diagnosed KKT bugs
- **WS3: Match rate improvement** (47 → ≥ 55) — alias-aware differentiation (#1111) targeting 21 mismatch models
- **WS4: path_syntax_error residual** (18 → ≤ 15) — fix 5 G+B models via parser and emitter fixes
- **WS5: Translate failures** (139 → ≥ 145) — LhsConditionalAssign emission fix recovers 4 models

The sprint introduces two architectural AD changes (#1111 alias differentiation, #1112 dollar-condition propagation) that are architecturally independent (different files, no shared data structures) but carry regression risk. The schedule places #1111 early (Days 2-3) to maximize match rate leverage, followed by #1112 (Days 4-5) to unblock sambal/qsambal.

**Process requirements (from Sprint 22 retrospective):**
- **PR6:** Full pipeline for all definitive metrics at checkpoints and final
- **PR7:** Track model_infeasible gross fixes and gross influx separately
- **PR8:** Use absolute counts alongside percentages for parse success

---

## Sprint 23 Targets

| Metric | Baseline | Target | Stretch |
|---|---|---|---|
| Parse | 156/160 (97.5%) | ≥ 156/160 (97.5%) | — |
| Translate | 139/156 (89.1%) | ≥ 145/156 (93.0%) | ≥ 148/156 |
| Solve | 89 | ≥ 100 | ≥ 110 |
| Match | 47/160 (29.4%) | ≥ 55/160 (34.4%) | ≥ 60 |
| path_syntax_error | 18 | ≤ 15 | ≤ 12 |
| path_solve_terminated | 10 | ≤ 5 | ≤ 3 |
| model_infeasible (in-scope) | 12 | ≤ 8 | ≤ 6 |
| Tests | 4,209 | ≥ 4,300 | — |

**Note:** Baseline path_syntax_error is 18 (from full pipeline baseline run), not 20 (Sprint 22 partial pipeline). Sprint 22 process recommendation PR8 requires reporting both absolute counts and percentages.

---

## Workstreams

### WS1: path_solve_terminated Reduction (10 → ≤ 5)
**Effort:** ~11-18h
**Target:** path_solve_terminated ≤ 5
**Source:** [TRIAGE_PATH_SOLVE_TERMINATED](./TRIAGE_PATH_SOLVE_TERMINATED.md)

| Tier | Models | Fix | Effort | Days |
|---|---|---|---|---|
| 1 | etamac | Re-run pipeline (already solved) | 0h | 0 |
| 1 | rocket | Suppress upper-bound complementarity for INF bounds | 2-3h | 1 |
| 1 | fawley | Parameter guard for zero-denominator sums | 1-2h | 1 |
| 1 | gtm | Variable initialization clamping for log/division | 2-3h | 1-2 |
| 2 | maxmin | Self-pair domain condition propagation | 2-3h | 4-5 |
| 2 | sambal | Dollar-condition propagation (#1112) | 4-6h | 4-5 |
| 2 | qsambal | Inherits sambal fix | 0-1h | 5 |

**Deferred:** elec (PATH convergence — Category C), dyncge/twocge (CGE empty-equation — high uncertainty)

**Cascade risk (KU-05):** 2-3 models may shift to model_infeasible (rocket, gtm, maxmin). Tracked per PR7.

### WS2: model_infeasible Reduction (12 → ≤ 8)
**Effort:** ~14-19h (Tier 1)
**Target:** model_infeasible ≤ 8 (in-scope)
**Source:** [TRIAGE_MODEL_INFEASIBLE](./TRIAGE_MODEL_INFEASIBLE.md)

| Tier | Model | Category | Fix | Effort | Days |
|---|---|---|---|---|---|
| 1 | markov | A (KKT) | Multi-pattern Jacobian fix (#1110) | 3-4h | 6 |
| 1 | pak | A (KKT) | Lead/lag Jacobian entries (#1049) | 3-4h | 6 |
| 1 | paperco | D (feature) | Loop body parameter extraction (#953) | 3-4h | 7 |
| 1 | sparta | A (KKT) | bal4 KKT derivation (#1081) | 2-3h | 7 |
| 1 | spatequ | A (KKT) | Jacobian domain mismatch (#1038) | 3-4h | 8 |
| 2 | bearing | A (KKT) | MCP pairing mismatch (#757) | 3-5h | 11+ |
| 2 | robustlp | B (PATH) | Near-feasible initialization | 2-3h | 11+ |

**Deferred:** prolog, chain, cpack, mathopt3, lnts (require warm-start infrastructure — Tier 3)

**Gross vs. Net (PR7):** Target 5 gross fixes (Tier 1). Expected influx from WS1: 2-3 models. Net reduction target: 12 → ≤ 8 requires 4+ net.

### WS3: Match Rate Improvement (47 → ≥ 55)
**Effort:** ~8-10h
**Target:** match ≥ 55
**Source:** [DESIGN_ALIAS_DIFFERENTIATION](./DESIGN_ALIAS_DIFFERENTIATION.md), [DESIGN_DOLLAR_CONDITION_PROPAGATION](./DESIGN_DOLLAR_CONDITION_PROPAGATION.md)

| Component | Fix | Effort | Models Affected | Days |
|---|---|---|---|---|
| Alias differentiation (#1111) | Add `bound_indices` to AD pipeline; alias-aware `_diff_varref()` | 4-6h | 21 mismatch + 8 matching (regression risk) | 2-3 |
| Dollar-condition propagation (#1112) | Extract gradient conditions; add to KKT stationarity | 4h | sambal, qsambal (primary); 42 dollar-cond models | 4-5 |

**Independence:** #1111 and #1112 are architecturally independent — different files, no shared data structures. #1111 modifies `src/ad/derivative_rules.py` only; #1112 modifies `src/ad/gradient.py`, `src/kkt/kkt_system.py`, `src/kkt/stationarity.py`.

**Implementation order:** #1111 first (higher leverage: 21 models vs 2), then #1112.

**Regression canary:** dispatch model — must remain matching after #1111. The `bound_indices` mechanism specifically handles dispatch's `Alias(i,j); sum((i,j), ...)` pattern.

### WS4: path_syntax_error Residual (18 → ≤ 15)
**Effort:** ~9-14h
**Target:** path_syntax_error ≤ 15
**Source:** [TRIAGE_PATH_SYNTAX_ERROR_GB](./TRIAGE_PATH_SYNTAX_ERROR_GB.md)

| Priority | Model | Subcategory | Fix | Effort | Days |
|---|---|---|---|---|---|
| 1 | srkandw | G | Parser `_handle_aggregation()` subset domain filter | 2-3h | 8 |
| 2 | chenery | B | Extend `resolve_index_conflicts()` for condition-scope | 1-2h | 9 |
| 3 | shale | B | Domain analysis + stationarity condition fix | 2-3h | 9 |
| 4 | otpop | B | Alias-as-subset condition investigation | 2-3h | 10-11 |
| 5 | hhfair | B | IndexOffset emission fix (lag/lead syntax) | 2-3h | 11 |

**Note:** PROJECT_PLAN.md §Priority 4 references "7-model G+B subset" — the authoritative updated count from TRIAGE_PATH_SYNTAX_ERROR_GB.md is 5 models (1 G + 4 B). Sprint 22 fixed 3 of the original G models.

### WS5: Translate Failures (139 → ≥ 145)
**Effort:** ~2-3h (Tier 1 alone exceeds target)
**Target:** translate ≥ 145/156 (93.0%)
**Source:** [CATALOG_TRANSLATE_FAILURES](./CATALOG_TRANSLATE_FAILURES.md)

| Tier | Models | Fix | Effort | Impact |
|---|---|---|---|---|
| 1 | agreste, ampl, cesam, korcge | LhsConditionalAssign statement-level emission | 2-3h | +4 → 143/156 (91.7%) |
| 2 | mine | SetMembershipTest evaluation in condition_eval | 2-3h | +1 → 144/156 |
| 3 | mexls | Universal set `'*'` in ModelIR (#940) | 3-4h | +1 → 145/156 |

**Note:** Baseline is 139 (not 141 from Sprint 22) due to borderline timeout variance. Tier 1 alone reaches 143; Tiers 1+2+3 reach 145 to meet the target. 7 timeout models are architecturally intractable.

---

## Effort Summary

| Workstream | Estimated Effort | Notes |
|---|---|---|
| WS1: path_solve_terminated | 11-18h | Tier 1 (5-8h) + Tier 2 (6-10h, overlaps WS3 #1112) |
| WS2: model_infeasible | 14-19h | Tier 1 only; Tier 2 if schedule permits |
| WS3: Match rate (#1111 + #1112) | 8-10h | #1112 overlaps WS1 Tier 2 |
| WS4: path_syntax_error G+B | 9-14h | 5 individual fixes |
| WS5: Translate failures | 2-3h | Tier 1 only (may extend to Tiers 2-3) |
| Pipeline retest (full, per PR6) | 4h | ~76 min per run × 3 (Checkpoint 1, Checkpoint 2, Final) |
| Sprint close + retrospective | 2h | Day 14 |
| **Total (overlaps removed)** | **~36-48h** | #1112 counted once (WS1+WS3 overlap) |

**Budget:** 32-44h per PROJECT_PLAN.md. The estimate slightly exceeds budget at the upper end. Contingency: defer WS4 models 4-5 (otpop, hhfair) and WS2 Tier 2 if needed.

---

## 15-Day Schedule

### Day 0 — Baseline Confirm + Sprint Kickoff

**Theme:** Verify clean baseline, internalize the plan, confirm all tests pass
**Effort:** 2-2.5h

| Task | Deliverable |
|---|---|
| `make test` — confirm 4,209 passed | Clean baseline |
| Review PLAN.md and all prep task deliverables | Plan internalized |
| Initialize SPRINT_LOG.md from template | Sprint log initialized |
| Run full pipeline (per PR6): `.venv/bin/python scripts/gamslib/run_full_test.py --quiet` | Baseline confirmed against BASELINE_METRICS.md |

**Day 0 criterion:** All tests pass; SPRINT_LOG.md created; baseline matches BASELINE_METRICS.md (parse 156/160, solve 89, match 47).

---

### Day 1 — WS1 Tier 1: Quick Wins (rocket, fawley, gtm) + WS5 Tier 1 (LhsConditionalAssign)

**Theme:** Execution error fixes + translate fix; low-risk, high-leverage
**Effort:** 5-7h

| Task | Files | Deliverable |
|---|---|---|
| WS1: Suppress upper-bound complementarity for INF bounds (rocket) | `src/kkt/stationarity.py` or `src/emit/` | rocket no longer has `+-infinity * 0` |
| WS1: Fix fawley parameter guard (zero-denominator sum) | `src/emit/` | fawley no longer divides by zero |
| WS1: Variable initialization clamping for gtm (log/division at 0) | `src/emit/` | gtm no longer has log(0)/div-by-0 |
| WS5: Add LhsConditionalAssign emission handler | `src/emit/original_symbols.py` or `src/emit/expr_to_gams.py` | agreste, ampl, cesam, korcge translate |
| Unit tests for all fixes | `tests/unit/` | ≥ 6 tests |

**End of Day 1 criterion:** rocket, fawley, gtm advance past execution errors; 4 translate models recover; ≥ 6 new tests.

**Expected metrics shift:** path_solve_terminated -3 to -4 (etamac re-run + rocket + fawley + gtm; net may vary with cascades); translate +4.

---

### Day 2 — WS3: Alias-Aware Differentiation (#1111, Part 1)

**Theme:** Begin highest-leverage match rate fix
**Effort:** 3-4h

| Task | Files | Deliverable |
|---|---|---|
| Add `_same_root_set()` and `_alias_match()` helpers | `src/ad/derivative_rules.py` | Helper functions |
| Add `bound_indices` kwarg to `differentiate_expr()` and all `_diff_*` functions | `src/ad/derivative_rules.py` | Parameter threading |
| Thread `bound_indices` through `_diff_sum()` and `_diff_prod()` | `src/ad/derivative_rules.py` | Sum/Prod augment indices before recursing |
| Add alias-aware matching in `_diff_varref()` | `src/ad/derivative_rules.py` | Free alias → sameas guard; bound alias → 0 |
| Unit tests: alias matching | `tests/unit/ad/test_alias_differentiation.py` | ≥ 5 tests |

**End of Day 2 criterion:** Alias differentiation implemented; unit tests pass; `make test` passes.

---

### Day 3 — WS3: Alias-Aware Differentiation (#1111, Part 2) + Pipeline Retest

**Theme:** Integration testing, regression checks, pipeline validation
**Effort:** 2-3h

| Task | Files | Deliverable |
|---|---|---|
| Integration test: qabel MCP generation (verify fix) | pipeline | qabel gradient includes cross-terms |
| Integration test: dispatch MCP generation (verify no regression) | pipeline | dispatch still matches |
| Smoke-test all 8 currently-matching alias models | pipeline | No regressions |
| Pipeline retest (solve subset): check all 89 solving models | pipeline | No match regressions |
| Fix any edge cases discovered | `src/ad/derivative_rules.py` | Edge cases resolved |

**End of Day 3 criterion:** #1111 verified; dispatch not regressed; ≥ 5 alias mismatch models improve or match; `make test` passes.

---

### Day 4 — WS3: Dollar-Condition Propagation (#1112, Part 1) + WS1 Tier 2 (maxmin)

**Theme:** Second architectural AD change + targeted execution error fix
**Effort:** 3-4h

| Task | Files | Deliverable |
|---|---|---|
| WS3: Add `_extract_gradient_conditions()` to gradient.py | `src/ad/gradient.py` | Condition extraction from gradient expressions |
| WS3: Add `gradient_conditions` field to KKTSystem | `src/kkt/kkt_system.py` | New field (1 line + docstring) |
| WS3: Add Stage 4 gradient condition check in `build_stationarity_equations()` | `src/kkt/stationarity.py` | Gradient conditions applied to stationarity |
| WS1: Fix maxmin self-pair domain propagation | `src/kkt/stationarity.py` | maxmin no longer divides by sqrt(0) |
| Unit tests for gradient condition extraction | `tests/unit/ad/`, `tests/unit/kkt/` | ≥ 4 tests |

**End of Day 4 criterion:** #1112 implemented; maxmin advances past execution error; unit tests pass.

---

### Day 5 — Checkpoint 1 + WS1 Tier 2 (sambal, qsambal)

**Theme:** Checkpoint 1 GO/NO-GO; verify #1112 fixes sambal/qsambal
**Effort:** 3-4h

#### Checkpoint 1 (Day 5) GO/NO-GO Criteria

| Criterion | GO threshold | CONDITIONAL GO | NO-GO action |
|---|---|---|---|
| Solve | ≥ 95 | ≥ 92 | Redirect to debugging |
| Match | ≥ 50 | ≥ 48 | Prioritize #1111 edge cases |
| path_solve_terminated | ≤ 7 | ≤ 8 | Redirect to WS1 fixes |
| Translate | ≥ 143 | ≥ 141 | Debug LhsConditionalAssign fix |
| Tests | All pass | — | Block on failures |
| #1111 PR | Merged | Open | Complete before Day 6 |

**Full pipeline run required per PR6 (~76 min).**

| Task | Files | Deliverable |
|---|---|---|
| Full pipeline retest (per PR6) | pipeline | Checkpoint 1 metrics |
| Checkpoint 1 evaluation | — | GO/CONDITIONAL GO/NO-GO decision |
| WS1: Verify sambal fix from #1112 | pipeline | sambal no longer divides by zero |
| WS1: Verify qsambal inherits sambal fix | pipeline | qsambal solves |
| Track model_infeasible gross/influx (per PR7) | SPRINT_LOG.md | Gross fixes and influx recorded |

**End of Day 5 criterion:** Checkpoint 1 evaluated; sambal + qsambal advance past execution errors.

**Day 5 Status:** COMPLETE — CONDITIONAL GO. stat_x guard works; stat_t NA issue persists (separate fix needed).

---

### Day 6 — WS2: model_infeasible Tier 1, Part 1 (markov, pak)

**Theme:** Begin model_infeasible KKT bug fixes
**Effort:** 6-8h (markov 3-4h, pak 3-4h, tests/smoke-tests overlapping)

| Task | Files | Deliverable |
|---|---|---|
| WS2: Fix markov multi-pattern Jacobian (#1110) | `src/kkt/stationarity.py` | Per-pattern stationarity with sameas guards |
| WS2: Fix pak lead/lag Jacobian entries (#1049) | `src/ad/constraint_jacobian.py`, `src/kkt/stationarity.py` | Lead/lag variable references generate correct Jacobian |
| Unit tests | `tests/unit/kkt/` | ≥ 4 tests |
| Smoke-test: markov MCP + pak MCP | pipeline | Both models advance past pairing/infeasibility |

**End of Day 6 criterion:** markov and pak no longer model_infeasible; ≥ 4 new tests.

---

### Day 7 — WS2: model_infeasible Tier 1, Part 2 (paperco, sparta)

**Theme:** Continue model_infeasible fixes
**Effort:** 6-7h

| Task | Files | Deliverable |
|---|---|---|
| WS2: Fix paperco loop body parameter extraction (#953) | `src/ir/parser.py` | `pp(p)` assigned inside loop body correctly emitted |
| WS2: Fix sparta bal4 KKT derivation (#1081) | `src/kkt/stationarity.py` | sparta KKT correct for bal4 formulation |
| Unit tests | `tests/unit/` | ≥ 3 tests |
| Smoke-test: paperco MCP + sparta MCP | pipeline | Both models advance |

**End of Day 7 criterion:** paperco and sparta no longer model_infeasible; ≥ 3 new tests.

---

### Day 8 — WS2: model_infeasible Tier 1, Part 3 (spatequ) + WS4 Begin

**Theme:** Complete model_infeasible Tier 1; begin path_syntax_error G+B
**Effort:** 5-7h

| Task | Files | Deliverable |
|---|---|---|
| WS2: Fix spatequ Jacobian domain mismatch (#1038) | `src/ad/constraint_jacobian.py`, `src/kkt/assemble.py` | Sum index binding corrected for 3D var / 2D eq |
| WS4: Fix srkandw parser `_handle_aggregation()` (subcategory G) | `src/ir/parser.py` | srkandw no longer has empty sum domain |
| Unit tests | `tests/unit/` | ≥ 3 tests |

**End of Day 8 criterion:** spatequ no longer model_infeasible; srkandw path_syntax_error fixed; ≥ 3 new tests.

---

### Day 9 — WS4: path_syntax_error G+B (chenery, shale)

**Theme:** Continue path_syntax_error fixes
**Effort:** 4-5h

| Task | Files | Deliverable |
|---|---|---|
| WS4: Fix chenery index shadowing (subcategory B) | `src/emit/expr_to_gams.py` | Sum loop index renamed to avoid condition conflict |
| WS4: Fix shale subset condition domain (subcategory B) | `src/kkt/stationarity.py` | `$(cf(c) and t(tf))` domain corrected |
| Unit tests | `tests/unit/` | ≥ 2 tests |

**End of Day 9 criterion:** chenery and shale path_syntax_error fixed; ≥ 2 new tests.

---

### Day 10 — Checkpoint 2 + WS4 Remaining (otpop, hhfair)

**Theme:** Checkpoint 2 GO/NO-GO; complete path_syntax_error G+B if schedule permits
**Effort:** 3-4h

#### Checkpoint 2 (Day 10) GO/NO-GO Criteria

| Criterion | GO threshold | NO-GO action |
|---|---|---|
| Solve | ≥ 98 | Redirect to debugging; defer WS4 remaining |
| Match | ≥ 53 | Investigate #1111 edge cases |
| path_solve_terminated | ≤ 5 | If > 5: investigate remaining models |
| model_infeasible (in-scope) | ≤ 9 | If > 9: investigate influx |
| path_syntax_error | ≤ 16 | Acceptable if ≤ 16; defer remaining to buffer |
| Tests | All pass | Block on failures |

**Full pipeline run required per PR6 (~76 min).**

| Task | Files | Deliverable |
|---|---|---|
| Full pipeline retest (per PR6) | pipeline | Checkpoint 2 metrics |
| Checkpoint 2 evaluation | — | GO/NO-GO decision |
| Track model_infeasible gross/influx (per PR7) | SPRINT_LOG.md | Gross vs influx recorded |
| WS4: Fix otpop alias-as-subset condition (if GO) | `src/kkt/stationarity.py` | otpop path_syntax_error fixed |
| WS4: Fix hhfair IndexOffset emission (if GO) | `src/emit/` | hhfair path_syntax_error fixed |

**End of Day 10 criterion:** Checkpoint 2 evaluated; path_syntax_error ≤ 15 if all fixes landed.

---

### Day 11 — Buffer / Overflow + WS5 Tier 2-3

**Theme:** Address overflows; additional translate fixes if budget permits
**Effort:** 2-3h

| Task | Deliverable |
|---|---|
| Complete any unfinished WS1-WS4 tasks | All WS targets met or documented |
| WS5 Tier 2 (if budget): Fix mine SetMembershipTest evaluation | mine translates (+1) |
| WS5 Tier 3 (if budget): Fix mexls universal set (#940) | mexls translates (+1) |
| WS2 Tier 2 (if budget): Investigate bearing MCP pairing | bearing assessed |
| Pipeline retest for new fixes | Updated metrics |

**End of Day 11 criterion:** All core workstream targets met; stretch fixes attempted.

---

### Day 12 — Sprint Close Prep: Issues + Documentation

**Theme:** File issues for deferred items; update documentation
**Effort:** 1-2h
**Day 12 Status:** COMPLETE

| Task | Deliverable |
|---|---|
| File issues for all deferred/blocked items | GitHub issues with sprint-24 label |
| Document any new known unknowns | KNOWN_UNKNOWNS.md updated |
| Update SPRINT_LOG.md with current metrics | Sprint log current |
| Run `make test` | All tests pass |

**End of Day 12 criterion:** All deferred items have GitHub issues; documentation current.

---

### Day 13 — Final Pipeline Retest + Sprint Close

**Theme:** Final definitive metrics; verify all acceptance criteria
**Effort:** 2-3h

| Task | Deliverable |
|---|---|
| Final full pipeline retest (per PR6) | `gamslib_status.json` updated |
| Record final metrics vs. targets | SPRINT_LOG.md complete |
| Verify all acceptance criteria | Criteria checklist |
| model_infeasible gross vs. influx final accounting (per PR7) | Gross/influx recorded |

**End of Day 13 criterion:** Final metrics recorded; all acceptance criteria evaluated.

---

### Day 14 — Sprint Close + Retrospective

**Theme:** Sprint retrospective; Sprint 24 recommendations
**Effort:** 1-2h

| Task | Deliverable |
|---|---|
| Write Sprint 23 Retrospective | `docs/planning/EPIC_4/SPRINT_23/SPRINT_RETROSPECTIVE.md` |
| Update CHANGELOG.md with sprint summary | CHANGELOG.md |
| Update PROJECT_PLAN.md Rolling KPIs | KPI table updated |
| Sprint 24 recommendations | Documented in retrospective |

**End of Day 14 criterion:** Retrospective written; CHANGELOG.md updated; Sprint 24 scope outlined.

---

## Checkpoints Summary

### Checkpoint 1 (Day 5)

| Criterion | Target | Fallback if missed |
|---|---|---|
| Solve | ≥ 95 | Redirect Days 6-7 to WS1 debugging |
| Match | ≥ 50 | Investigate #1111 edge cases; review alias models |
| path_solve_terminated | ≤ 7 | Acceptable; continue with WS2 |
| Translate | ≥ 143 | Debug LhsConditionalAssign emission |
| #1111 PR merged | Yes | Complete before Day 6 |
| All tests pass | Yes | Block on failures |

**Expected metrics at Checkpoint 1:**
- Solve: ~96-100 (baseline 89 + WS1 Tier 1 ~4 + WS3 #1111 ~3-7)
- Match: ~50-57 (baseline 47 + #1111 alias fixes ~3-10)
- Translate: 143-145 (baseline 139 + LhsConditionalAssign +4)
- path_solve_terminated: ~6-7 (baseline 10 - Tier 1 ~3-4)

### Checkpoint 2 (Day 10)

| Criterion | Target | Fallback if missed |
|---|---|---|
| Solve | ≥ 98 | Redirect Days 11-12 to solving debugging |
| Match | ≥ 53 | Investigate remaining mismatches |
| path_solve_terminated | ≤ 5 | If > 5: investigate Tier 2 |
| model_infeasible (in-scope) | ≤ 9 | Investigate influx; adjust target |
| path_syntax_error | ≤ 16 | Defer remaining to buffer days |
| All tests pass | Yes | Block on failures |

**Expected metrics at Checkpoint 2:**
- Solve: ~100-106 (CP1 + WS2 ~5 + WS4 ~2)
- Match: ~53-58 (CP1 + newly-solving matches)
- model_infeasible: ~8-10 (baseline 12 - WS2 ~5 + influx ~2-3)
- path_syntax_error: ~14-16 (baseline 18 - WS4 ~2-4)

---

## Contingency Plans

### Contingency 1: #1111 Alias Differentiation Causes Regressions

**Trigger:** After #1111 merge, > 2 currently-matching models regress.
**Action:** (a) Immediately check dispatch — if dispatch regresses, the `bound_indices` mechanism has a bug. (b) Bisect failing models to identify the failing pattern. (c) If unfixable by Day 3: revert #1111, redirect Days 4-5 to alternative match rate fixes, reduce match target to ≥ 50.
**Risk level:** MEDIUM. The design specifically handles dispatch's pattern. Most regression risk is in edge cases (nested sums, partial collapse).

### Contingency 2: model_infeasible Influx from WS1 Fixes (KU-05)

**Trigger:** After WS1 pipeline retest, model_infeasible increases by > 3 models.
**Action:** (a) Triage newly-infeasible models immediately (Day 5 or 6). (b) If they share root cause with WS2 Tier 1: absorb into WS2 schedule. (c) If > 5 new infeasible: accept model_infeasible > 8 target miss, document for Sprint 24.
**Risk level:** MEDIUM. Task 2 estimated 2-3 models cascade; budget builds in this headroom.

### Contingency 3: Dollar-Condition Propagation (#1112) Over-Extracts

**Trigger:** #1112 adds guards that break currently-solving models.
**Action:** (a) Check guard-safety criteria (§8.2 of DESIGN_DOLLAR_CONDITION_PROPAGATION.md). (b) Restrict extraction to variables where ALL gradient entries share same condition. (c) If persistent: limit to sambal/qsambal only (model-specific guard).
**Risk level:** LOW. Design uses fallback-only Stage 4 + consistent-condition check.

### Contingency 4: WS4 G+B Fixes Take > 14h

**Trigger:** By end of Day 10, fewer than 3 of 5 G+B models fixed.
**Action:** (a) Defer otpop and hhfair to Sprint 24. (b) Accept path_syntax_error ≤ 16 (vs ≤ 15 target). (c) Redirect Day 11 to WS2 Tier 2 or WS5 Tier 2-3 for higher leverage.
**Risk level:** LOW. srkandw and chenery are highest priority and most tractable.

---

## Issue-to-Day Mapping

### Open Issues (24)

| Issue | Title | Priority | Day(s) | Status |
|---|---|---|---|---|
| #1112 | Dollar-condition propagation | WS3/WS1 | 4-5 | OPEN |
| #1111 | Alias-aware differentiation | WS3 | 2-3 | OPEN |
| #1110 | markov multi-pattern Jacobian | WS2 | 6 | OPEN |
| #1091 | Reclassify Category D models | WS3 | — (informational) | OPEN |
| #1089 | qabel regression | WS3 | 2-3 (verify) | OPEN |
| #1081 | sparta KKT bug | WS2 | 7 | OPEN |
| #1070 | prolog singular Jacobian | WS2 (deferred) | — | OPEN |
| #1062 | tricp sparse edge-set | WS4 (deferred) | — | OPEN |
| #1061 | tforss NA parameter | — | — (backlog) | OPEN |
| #1049 | pak incomplete stationarity | WS2 | 6-7 | OPEN |
| #1041 | cesam2 empty equation | — | — (backlog) | OPEN |
| #1038 | spatequ Jacobian domain mismatch | WS2 | 8 | OPEN |
| #986 | lands NA values | — | — (backlog) | OPEN |
| #983 | elec division by zero | WS1 (deferred) | — | OPEN |
| #956 | nonsharp compilation errors | — | — (backlog) | OPEN |
| #953 | paperco loop body parameter | WS2 | 7 | OPEN |
| #952 | lmp2 empty dynamic subsets | — | — (backlog) | OPEN |
| #945 | launch per-instance stationarity | — | — (backlog) | OPEN |
| #940 | mexls universal set | WS5 (Tier 3) | 11 (stretch) | OPEN |
| #919 | sroute empty stationarity | — | — (backlog) | OPEN |
| #918 | qdemo7 conditionally-absent variables | — | — (backlog) | OPEN |
| #882 | camcge subset bound complementarity | — | — (backlog) | OPEN |
| #871 | camcge stationarity subset conditioning | — | — (backlog) | OPEN |
| #862 | sambal domain conditioning | WS1/WS3 | 4-5 | OPEN |

### Closed Issues (8)

| Issue | Title | Notes |
|---|---|---|
| #939 | maxmin smin() arity | Closed (partial; self-pair issue remains for WS1 Day 4) |
| #1084 | catmix regression | Closed (fixed in Sprint 22) |
| #1085 | fdesign regression | Closed (fixed in Sprint 22) |
| #1086 | harker regression | Closed (fixed in Sprint 22) |
| #1087 | hydro regression | Closed (fixed in Sprint 22) |
| #1088 | pindyck regression | Closed (fixed in Sprint 22) |
| #1090 | port regression | Closed (fixed in Sprint 22) |
| #1105 | robustlp diagonal param | Closed (fixed; residual convergence remains for WS2 Tier 2) |

### Backlog (Not Scheduled)

Issues not targeted in Sprint 23 (defer to Sprint 24): #871, #882, #918, #919, #945, #952, #956, #983, #986, #1041, #1061, #1062, #1070, #1091.

---

## Risk Register

### Risk 1: Alias Differentiation Regression (KU-12)
**Status:** MEDIUM — 8 currently-matching alias models at risk
**Probability:** 20% (design specifically handles dispatch pattern)
**Impact:** HIGH (loss of match count)
**Mitigation:** Run dispatch first; full pipeline regression before merge; Contingency 1

### Risk 2: model_infeasible Influx from path_solve_terminated Fixes (KU-05)
**Status:** MEDIUM — 2-3 models expected to cascade
**Probability:** 70% (Task 2 identified rocket, gtm, maxmin as medium cascade risk)
**Impact:** MEDIUM (net reduction less than expected)
**Mitigation:** Track per PR7; budget for influx; Contingency 2

### Risk 3: Non-Convex Ceiling Limits Match Rate (KU-16)
**Status:** MEDIUM — 8-12 models may be irreducible multi-KKT divergence
**Probability:** 80% (structural limitation)
**Impact:** LOW (stretch target affected, not primary target)
**Mitigation:** Monitor after #1111; re-evaluate match ceiling at Checkpoint 2

### Risk 4: Borderline Timeout Variance (BASELINE_METRICS.md §4)
**Status:** LOW — 4 models (clearlak, dinam, ferts, turkpow) fluctuate at 150s boundary
**Probability:** 50% (run-to-run variance)
**Impact:** LOW (translate count varies ±2-4)
**Mitigation:** Accept variance; report both min/max in checkpoints

---

## Acceptance Criteria

### Per-Workstream

| Workstream | Acceptance Criteria |
|---|---|
| WS1: path_solve_terminated | path_solve_terminated ≤ 5; 7 targeted models addressed; no regression in 89 solving models |
| WS2: model_infeasible | model_infeasible ≤ 8 (in-scope, net); 5 Tier 1 models addressed; gross fixes and influx tracked (PR7) |
| WS3: Match rate | match ≥ 55; #1111 merged without regressions; #1112 fixes sambal/qsambal |
| WS4: path_syntax_error | path_syntax_error ≤ 15; ≥ 3 of 5 G+B models fixed |
| WS5: Translate | translate ≥ 145/156 (93.0%); LhsConditionalAssign emission working |

### Sprint-Level

- Solve ≥ 100 (from 89)
- Match ≥ 55 (from 47)
- path_solve_terminated ≤ 5 (from 10)
- model_infeasible ≤ 8 in-scope (from 12)
- path_syntax_error ≤ 15 (from 18)
- Translate ≥ 145/156 (93.0%) (from 139/156)
- Parse ≥ 156/160 (maintain 97.5%)
- Tests ≥ 4,300 (from 4,209)
- Zero regressions: all existing 89 solving models maintained
- All KKT/AD fixes have unit tests
- Full pipeline at all checkpoints and final (PR6)
- model_infeasible gross fixes and influx tracked separately (PR7)
- Parse metrics report absolute counts and percentages (PR8)

---

## Files Reference

| File | Purpose |
|---|---|
| [BASELINE_METRICS](./BASELINE_METRICS.md) | Baseline numbers (main @ 2c33989e) |
| [TRIAGE_PATH_SOLVE_TERMINATED](./TRIAGE_PATH_SOLVE_TERMINATED.md) | path_solve_terminated root cause classification |
| [TRIAGE_MODEL_INFEASIBLE](./TRIAGE_MODEL_INFEASIBLE.md) | model_infeasible root cause classification |
| [DESIGN_ALIAS_DIFFERENTIATION](./DESIGN_ALIAS_DIFFERENTIATION.md) | #1111 alias-aware differentiation design |
| [DESIGN_DOLLAR_CONDITION_PROPAGATION](./DESIGN_DOLLAR_CONDITION_PROPAGATION.md) | #1112 dollar-condition propagation design |
| [TRIAGE_PATH_SYNTAX_ERROR_GB](./TRIAGE_PATH_SYNTAX_ERROR_GB.md) | path_syntax_error G+B triage |
| [CATALOG_TRANSLATE_FAILURES](./CATALOG_TRANSLATE_FAILURES.md) | Translate failure catalog |
| [KNOWN_UNKNOWNS](./KNOWN_UNKNOWNS.md) | Open risks and evaluated assumptions |
| [RETROSPECTIVE_ALIGNMENT](./RETROSPECTIVE_ALIGNMENT.md) | Sprint 22 retrospective alignment |
| [PREP_PLAN](./PREP_PLAN.md) | Preparation task tracking |
