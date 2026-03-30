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
| Gross fix | 1-4 | cpack | OUT (now solving) | 11 |
| Gross fix | 1-4 | prolog | OUT (now solving) | 10 |
| Influx | 1-4 | agreste | IN (was translate fail, now MI) | 11 |
| Influx | 1-4 | cesam | IN (was translate fail, now MI) | 12 |
| Influx | 1-4 | korcge | IN (was translate fail, now MI) | 13 |
| Influx | 1-4 | rocket | IN (was PST, now MI) | 14 |
| Checkpoint 1 | 5 | — | — | **14** |

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

**Status:** COMPLETE (PRs #1123, #1125, #1128, #1130 merged)

| Task | Status |
|---|---|
| rocket INF bound suppression | ✅ Fixed expression-based bound guard |
| fawley zero-denominator guard | ✅ Added `$onImplicitAssign` wrapping |
| gtm variable initialization clamping | ✅ Extended Priority 3 clamping |
| LhsConditionalAssign emission (agreste, ampl, cesam, korcge) | ✅ Added expr_to_gams case (+4 translate) |

---

### Day 2 — WS3 Alias Differentiation (#1111, Part 1)

**Status:** COMPLETE (PR #1134 merged)

| Task | Status |
|---|---|
| `_same_root_set()` and `_alias_match()` helpers | ✅ |
| `bound_indices` parameter threading | ✅ |
| Sum/Prod bound_indices augmentation | ✅ |
| Alias-aware `_diff_varref()` matching | ✅ |
| Unit tests (≥ 5) | ✅ |

---

### Day 3 — WS3 Alias Differentiation Integration

**Status:** COMPLETE (PR #1139 merged)

| Task | Status |
|---|---|
| qabel integration test | ✅ |
| dispatch regression test | ✅ No regression |
| 8 matching alias models check | ✅ |
| Pipeline solve retest | ✅ |

---

### Day 4 — WS3 Dollar-Condition (#1112) + WS1 maxmin

**Status:** COMPLETE (PR #1148 merged)

| Task | Status |
|---|---|
| `_extract_gradient_conditions()` | ✅ Extracts DollarConditional + multiplicative conditions |
| `gradient_conditions` field on KKTSystem | ✅ |
| Stage 4 condition check in stationarity | ✅ With `_has_unconditioned_access()` guard |
| maxmin self-pair fix | ✅ (completed in earlier sprint) |
| Domain condition extraction from nested eq domains | ✅ SetMembershipTest preserved |
| Unary peeling for MAX-objective negation | ✅ |
| enumerate_equation_instances() warn-once fix | ✅ |

---

### Day 5 — Checkpoint 1 + sambal/qsambal

**Status:** COMPLETE

| Task | Status |
|---|---|
| Full pipeline retest (PR6) | ✅ 3738s (~62 min) |
| Checkpoint 1 evaluation | ✅ **CONDITIONAL GO** (see below) |
| sambal verification | ✅ stat_x has $(xw(i,j)) guard from #1112; stat_t NA issue persists (separate) |
| qsambal verification | ✅ Same pattern as sambal |

#### Checkpoint 1 Results

**Pipeline Results (147-scope):**

| Stage | Baseline (Day 0) | Day 5 | Delta |
|---|---|---|---|
| Parse | 144/147 (98.0%) | 144/147 (98.0%) | +0 |
| Translate | 128/144 (88.9%) | 133/144 (92.4%) | **+5** |
| Solve | 81/128 (63.3%) | 84/133 (63.2%) | **+3** |
| Match | 47/147 (32.0%) | 48/147 (32.7%) | **+1** |

**Full Corpus (160 denominator):**

| Stage | Baseline | Day 5 | Delta |
|---|---|---|---|
| Parse | 156/160 (97.5%) | 156/160 (97.5%) | +0 |
| Translate | 139/156 (89.1%) | 145/156 (93.0%) | **+6** |
| Solve | 89 (64.0%) | 92 (63.4%) | **+3** |
| Match | 47/160 (29.4%) | 48/160 (30.0%) | **+1** |

**Solve Error Categories (147-scope):**

| Category | Baseline | Day 5 | Delta |
|---|---|---|---|
| path_syntax_error | 18 | 21 | +3 (influx from newly-translating models) |
| model_infeasible | 12 | 14 | +2 (2 gross fixes, 4 influx) |
| path_solve_terminated | 10 | 8 | **-2** (maxmin, rocket resolved) |
| path_solve_license | 7 | 6 | -1 |

**Checkpoint 1 GO/NO-GO Evaluation:**

| Criterion | GO | CONDITIONAL | Current | Decision |
|---|---|---|---|---|
| Solve | ≥ 95 | ≥ 92 | **92** | CONDITIONAL GO |
| Match | ≥ 50 | ≥ 48 | **48** | CONDITIONAL GO |
| PST | ≤ 7 | ≤ 8 | **8** | CONDITIONAL GO |
| Translate | ≥ 143 | ≥ 141 | **145** | **GO** |
| Tests | All pass | — | 4,273 pass | **GO** |
| #1111 PR | Merged | Open | Open (issue) | CONDITIONAL |

**Overall Decision: CONDITIONAL GO**

Translate exceeded GO threshold. Solve, Match, and PST all meet CONDITIONAL thresholds. #1111 alias differentiation PR was merged but the issue remains open for further work.

**Key Improvements Days 1-4:**
- +6 translate: 4 LhsConditionalAssign fixed (agreste, ampl, cesam, korcge) + 2 borderline timeout recovery (dinam, ferts)
- +3 solve: cpack (MI→solve), prolog (MI→solve), maxmin (PST→solve)
- +1 match: ampl (new translate→solve→match)
- -2 PST: maxmin (now solving), rocket (PST→MI)

**model_infeasible Accounting (PR7):**
- Gross fixes: 2 (cpack, prolog left MI)
- Influx: 4 (agreste, cesam, korcge from translate-fail; rocket from PST)
- Net: +2 (12 → 14)
- PSE influx: +3 (camshape, dinam/ferts/tricp from borderline timeout → translate → PSE)

**sambal/qsambal Verification:**
- stat_x(i,j) now has equation-level `$(xw(i,j))` guard from #1112 dollar-condition propagation
- stat_t(i) still has NA data errors — `tb(h1)=NA` evaluates NA in `tb(i)*tw(i)*...` before the `1$(tw(i))` multiplicative guard can zero it out
- sambal/qsambal remain in path_solve_terminated (2 data errors prevent solve)
- Fix requires expression-level zero-guarding or equation-level `$(tw(i))` guard for stat_t (separate from #1112)

---

### Day 6 — WS2 markov + pak

**Status:** COMPLETE (markov fixed, pak deferred)

| Task | Status |
|---|---|
| markov multi-pattern Jacobian (#1110) | ✅ Fixed: multi-pattern detection + correction term |
| pak lead/lag Jacobian (#1049) | ⏭️ Deferred: 3 interacting bugs (subset domain, gradient template, quoted strings) — separate PR |
| Unit tests (24 new) | ✅ _derivative_structure_key, _substitute_elements, _subtract_and_cancel, integration |
| Quality checks | ✅ 4,294 passed, 10 skipped, 1 xfailed; typecheck/lint/format clean |

**markov Fix Details:**
- Root cause: `_add_indexed_jacobian_terms()` picked one representative Jacobian entry and generalized its derivative to ALL constraint-variable pairings. For `constr(sp,j)`, diagonal (sp=s, j=i) has derivative `1 - b*pi(...)` while off-diagonal has `-b*pi(...)`. The `+1` Kronecker delta was incorrectly applied to all entries.
- Fix: Added multi-pattern detection via `_derivative_structure_key()` fingerprinting. When multiple structural patterns exist, the majority pattern drives the sum and a correction term is added for the minority (diagonal) pattern. Three new helpers: `_subtract_and_cancel()`, `_substitute_elements()`, `_derivative_structure_key()`.
- Result: `stat_z(s,i)` now correctly contains `nu_constr(s,i) + sum((s__kkt1,j), (-b*pi(...)) * nu_constr(s__kkt1,j))` — diagonal correction separated from off-diagonal sum.
- GAMS verification: markov MCP solves successfully (obj=2571.794).

**pak Investigation Summary:**
- 3 interacting bugs identified: (1) subset/superset domain mismatch (t⊂te), (2) first-instance gradient template, (3) quoted string literal mismatch ('1985' vs "1985").
- MCP obj=950.913 vs LP optimal=1075.547 confirms structural incorrectness.
- Requires deep architectural changes — deferred to dedicated PR.

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

**Status:** COMPLETE

| Task | Status |
|---|---|
| Full pipeline retest (PR6) | ✅ Complete (147 models, 5458s) |
| Checkpoint 2 evaluation | ✅ CONDITIONAL NO-GO (see below) |
| otpop alias-as-subset (if GO) | ⏭️ Deferred — subset-superset domain mismatch (#1164 class) |
| hhfair IndexOffset (if GO) | ⏭️ Deferred — same subset-superset domain mismatch |

#### Checkpoint 2 Results (2026-03-30)

| Stage | Count | % | Baseline | Delta |
|---|---|---|---|---|
| Parse | 146/147 | 99.3% | 144/147 (98.0%) | +2 |
| Translate | 138/147 | 94.5% | 128/147 (87.1%) | +10 |
| Solve | 85/138 | 61.6% | 81/128 (63.3%) | +4 |
| Match | 49/147 | 33.3% | 47/147 (32.0%) | +2 |

| Error Category | Count | Baseline | Delta |
|---|---|---|---|
| path_syntax_error | 28 | 18 | +10 (influx from new translating models) |
| model_infeasible | 10 | 12 | -2 (improved) |
| path_solve_terminated | 9 | 10 | -1 |
| path_solve_license | 6 | 7 | -1 |
| translate timeout | 6 | ~17 | -11 (LP fast path) |

#### Checkpoint 2 GO/NO-GO Evaluation

| Criterion | Threshold | Actual | Status |
|---|---|---|---|
| Solve ≥ 98 | 98 | 85 | ❌ Below |
| Match ≥ 53 | 53 | 49 | ❌ Below |
| path_solve_terminated ≤ 5 | 5 | 9 | ❌ Above |
| model_infeasible ≤ 9 | 9 | 10 | ⚠️ Borderline |
| path_syntax_error ≤ 16 | 16 | 28 | ❌ Above (influx) |
| Tests pass | Yes | 4,358 passed | ✅ |

**Decision: CONDITIONAL NO-GO.** Absolute metrics improved (translate +10, solve +4, match +2, model_infeasible -2), but thresholds not met. The path_syntax_error increase from 18→28 is entirely influx from newly-translating models (LP fast path brought 10+ models into translation that previously timed out). These are pre-existing compilation errors now visible.

**otpop and hhfair analysis:** Both have subset-superset domain mismatch in stationarity equations — same class as chenery/shale (#1164). The stationarity equation iterates over the superset but references variables/parameters declared over subsets. This requires the domain restructuring approach identified in #1164, which is a 3-5h effort per model. Deferred to buffer days.

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
