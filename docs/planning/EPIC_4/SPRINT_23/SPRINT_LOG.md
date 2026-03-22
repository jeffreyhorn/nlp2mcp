# Sprint 23 Log

**Sprint Duration:** 15 days (Day 0 – Day 14)
**Start Date:** 2026-03-21
**Baseline Commit:** `main @ 2c33989e` (baseline metrics), kickoff from `main @ 89ff673e` (after prep merge)

---

## Baseline Metrics (Day 0)

**Test Suite:** 4,209 passed

| Metric | Baseline | Target | Stretch |
|---|---|---|---|
| Parse success | 156/160 (97.5%) | ≥ 156/160 (97.5%) | — |
| Translate success | 139/156 (89.1%) | ≥ 145/156 (93.0%) | ≥ 148/156 |
| Solve success | 89 (64.0% of translated) | ≥ 100 | ≥ 110 |
| Match | 47/160 (29.4%) | ≥ 55/160 (34.4%) | ≥ 60 |
| path_syntax_error | 18 | ≤ 15 | ≤ 12 |
| path_solve_terminated | 10 | ≤ 5 | ≤ 3 |
| model_infeasible (in-scope) | 12 | ≤ 8 | ≤ 6 |
| Tests | 4,209 | ≥ 4,300 | — |

---

## Workstream to Issue Mapping

### WS1: path_solve_terminated Reduction (10 → ≤ 5)
- **Target:** path_solve_terminated ≤ 5
- **Tier 1 (Days 1-2):** rocket (INF bounds), fawley (zero-denom guard), gtm (variable clamping)
- **Tier 2 (Days 4-5):** maxmin (self-pair #939), sambal (#862, #1112), qsambal (inherits sambal)
- **Deferred:** elec (#983), dyncge, twocge (CGE)
- **Effort:** ~11-18h

### WS2: model_infeasible Reduction (12 → ≤ 8)
- **Target:** model_infeasible ≤ 8 (in-scope)
- **Tier 1 (Days 6-8):** markov (#1110), pak (#1049), paperco (#953), sparta (#1081), spatequ (#1038)
- **Tier 2 (Day 11+):** bearing (#757), robustlp (#1105 closed, residual)
- **Deferred:** prolog (#1070), chain, cpack, mathopt3, lnts (warm-start needed)
- **Effort:** ~14-19h (Tier 1)

### WS3: Match Rate Improvement (47 → ≥ 55)
- **Target:** match ≥ 55
- **#1111 Alias differentiation (Days 2-3):** 21 alias mismatch models; regression canary: dispatch
- **#1112 Dollar-condition propagation (Days 4-5):** sambal, qsambal (primary)
- **Effort:** ~8-10h

### WS4: path_syntax_error Residual (18 → ≤ 15)
- **Target:** path_syntax_error ≤ 15
- **G (Day 8):** srkandw (parser aggregation)
- **B (Day 9):** chenery (index shadowing), shale (subset domain)
- **B (Days 10-11):** otpop (alias-as-subset), hhfair (IndexOffset)
- **Effort:** ~9-14h

### WS5: Translate Failures (139 → ≥ 145)
- **Target:** translate ≥ 145/156 (93.0%)
- **Tier 1 (Day 1):** LhsConditionalAssign emission (agreste, ampl, cesam, korcge) — +4
- **Tier 2 (Day 11):** mine SetMembershipTest — +1
- **Tier 3 (Day 11):** mexls universal set (#940) — +1
- **Effort:** ~2-3h (Tier 1), 5-7h (Tiers 2-3)

---

## model_infeasible Gross/Influx Tracking (PR7)

| Event | Day | Model | Direction | Running In-Scope |
|---|---|---|---|---|
| Baseline | 0 | — | — | 12 |

---

## Day-by-Day Progress

### Day 0 — Baseline Confirm + Sprint Kickoff

**Status:** COMPLETE

| Task | Status |
|---|---|
| `make test` baseline | ✅ 4,209 passed, 10 skipped, 1 xfailed |
| SPRINT_LOG.md initialized | ✅ Baseline metrics verified against BASELINE_METRICS.md |
| Issue mapping confirmed | ✅ 24 open issues match PLAN.md table |
| Pipeline baseline confirmed | ✅ All metrics match BASELINE_METRICS.md (see below) |

**Pipeline Results (147-scope, clean re-run):**

| Stage | This Run | Baseline (BASELINE_METRICS.md §4) | Status |
|---|---|---|---|
| Parse | 144/147 (98.0%) | 144/147 (98.0%) | ✅ Exact match |
| Translate | 128/144 (88.9%) | 127/144 (88.2%) | +1 borderline timeout variance |
| Solve | 81/128 (63.3%) | 81/127 (63.8%) | ✅ Same solve count (denominator differs due to +1 translate) |
| Match | 47/147 (32.0%) | 47/147 (32.0%) | ✅ Exact match |

**Solve Error Categories (147-scope; matches BASELINE_METRICS.md §5 after removing feedtray which is excluded):**

| Category | This Run | Baseline (§5) | Match |
|---|---|---|---|
| path_syntax_error | 18 | 18 | ✅ |
| model_infeasible | 12 | 12 (in-scope) | ✅ |
| path_solve_terminated | 10 | 10 | ✅ |
| path_solve_license | 7 | 7 | ✅ |

**Note:** First run (under system load) had 1 extra timeout (translate 127, PSE 17). Clean re-run recovered the borderline model (translate 128, PSE 18), matching BASELINE_METRICS.md 160-scope numbers exactly.

**Pipeline Duration (this run; timing may vary from baseline ~4564s):** 4313s (~72 min)

---

### Day 1 — WS1 Tier 1 Quick Wins + WS5 LhsConditionalAssign

**Status:** NOT STARTED

| Task | Status |
|---|---|
| rocket INF bound suppression | |
| fawley zero-denominator guard | |
| gtm variable initialization clamping | |
| LhsConditionalAssign emission (agreste, ampl, cesam, korcge) | |

---

### Day 2 — WS3 Alias Differentiation (#1111, Part 1)

**Status:** NOT STARTED

| Task | Status |
|---|---|
| `_same_root_set()` and `_alias_match()` helpers | |
| `bound_indices` parameter threading | |
| Sum/Prod bound_indices augmentation | |
| Alias-aware `_diff_varref()` matching | |
| Unit tests (≥ 5) | |

---

### Day 3 — WS3 Alias Differentiation Integration

**Status:** NOT STARTED

| Task | Status |
|---|---|
| qabel integration test | |
| dispatch regression test | |
| 8 matching alias models check | |
| Pipeline solve retest | |

---

### Day 4 — WS3 Dollar-Condition (#1112) + WS1 maxmin

**Status:** NOT STARTED

| Task | Status |
|---|---|
| `_extract_gradient_conditions()` | |
| `gradient_conditions` field on KKTSystem | |
| Stage 4 condition check | |
| maxmin self-pair fix | |

---

### Day 5 — Checkpoint 1 + sambal/qsambal

**Status:** NOT STARTED

| Task | Status |
|---|---|
| Full pipeline retest (PR6) | |
| Checkpoint 1 evaluation | |
| sambal verification | |
| qsambal verification | |

---

### Day 6 — WS2 markov + pak

**Status:** NOT STARTED

| Task | Status |
|---|---|
| markov multi-pattern Jacobian (#1110) | |
| pak lead/lag Jacobian (#1049) | |

---

### Day 7 — WS2 paperco + sparta

**Status:** NOT STARTED

| Task | Status |
|---|---|
| paperco loop body extraction (#953) | |
| sparta bal4 KKT (#1081) | |

---

### Day 8 — WS2 spatequ + WS4 srkandw

**Status:** NOT STARTED

| Task | Status |
|---|---|
| spatequ Jacobian domain (#1038) | |
| srkandw parser aggregation (subcategory G) | |

---

### Day 9 — WS4 chenery + shale

**Status:** NOT STARTED

| Task | Status |
|---|---|
| chenery index shadowing (subcategory B) | |
| shale subset condition domain (subcategory B) | |

---

### Day 10 — Checkpoint 2 + WS4 remaining

**Status:** NOT STARTED

| Task | Status |
|---|---|
| Full pipeline retest (PR6) | |
| Checkpoint 2 evaluation | |
| otpop alias-as-subset (if GO) | |
| hhfair IndexOffset (if GO) | |

---

### Day 11 — Buffer / Overflow

**Status:** NOT STARTED

| Task | Status |
|---|---|
| Unfinished tasks from Days 1-10 | |
| Stretch: mine SetMembershipTest | |
| Stretch: mexls universal set (#940) | |
| Stretch: bearing investigation | |

---

### Day 12 — Sprint Close Prep

**Status:** NOT STARTED

| Task | Status |
|---|---|
| File deferred issues (sprint-24 label) | |
| Update KNOWN_UNKNOWNS.md | |
| Update SPRINT_LOG.md | |

---

### Day 13 — Final Pipeline Retest

**Status:** NOT STARTED

| Task | Status |
|---|---|
| Final full pipeline (PR6) | |
| Acceptance criteria evaluation | |
| model_infeasible final accounting (PR7) | |

---

### Day 14 — Sprint Close + Retrospective

**Status:** NOT STARTED

| Task | Status |
|---|---|
| Sprint 23 Retrospective | |
| CHANGELOG.md update | |
| PROJECT_PLAN.md Rolling KPIs | |
| Sprint 24 recommendations | |
