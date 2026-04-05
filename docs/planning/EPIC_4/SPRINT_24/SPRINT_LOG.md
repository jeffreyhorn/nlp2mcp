# Sprint 24 Log

**Sprint:** 24 — Alias Differentiation & Error Category Reduction
**Duration:** 15 days (Day 0 – Day 14)
**Baseline:** parse 147/147, translate 140/147, solve 86, match 49, tests 4,364

---

## Sprint 24 Targets

| Metric | Baseline | Target | Stretch |
|---|---|---|---|
| Parse | 147/147 (100%) | ≥ 147/147 | — |
| Translate | 140/147 (95.2%) | ≥ 143/147 (97%) | ≥ 145/147 |
| Solve | 86 | ≥ 95 | ≥ 100 |
| Match | 49 | ≥ 55 | ≥ 60 |
| path_syntax_error | 23 | ≤ 15 | ≤ 12 |
| path_solve_terminated | 12 | ≤ 10 | ≤ 8 |
| model_infeasible | 11 | ≤ 8 | ≤ 6 |
| Tests | 4,364 | ≥ 4,400 | — |

---

## Daily Progress

### Day 0 — Setup

**Status:** COMPLETE

| Task | Status |
|---|---|
| Verify baseline metrics | ✅ parse 147/147, translate 140/147, solve 86, match 49 |
| Generate golden files for 49 matching models | ✅ 49/49 generated in /tmp/gamslib-golden/ |
| Set up dispatch regression canary | ✅ dispatch matches (rel_diff 5e-05) |

---

### Day 1 — WS1 Phase 1: Debug Pattern A

**Status:** COMPLETE

| Task | Status |
|---|---|
| Debug logging in _diff_varref/_partial_collapse_sum | ✅ Traced via Python inspection |
| Trace qabel derivative computation | ✅ Found root cause |
| Identify edge case | ✅ See findings below |
| Dispatch canary test | ✅ dispatch still matches |

**Root Cause Finding:** The alias differentiation bug is NOT in `_diff_varref` or `_alias_match` — the AD engine correctly computes derivatives. The bug is in the **Jacobian transpose assembly** in `build_stationarity_equations` (lines ~4010-4090). When the constraint domain matches the variable domain (e.g., both `(n,k)`), the code assumes a direct term (no sum). But when the constraint body contains `sum(np, a(n,np)*x(np,k))` where `np` aliases `n`, the derivative creates a cross-term `a(n',n)` that requires summing over the constraint index `n'`. The matching-domain assumption is wrong for alias cross-terms.

**Impact:** This affects ALL Pattern A models — the fix is in `build_stationarity_equations`, not in the AD engine. The `_alias_match`/`bound_indices` mechanism is correct but operates at the wrong level for this bug.

---

### Day 2 — WS1 Phase 1: Fix Pattern A

**Status:** NOT STARTED

| Task | Status |
|---|---|
| Implement Pattern A edge case fix | |
| Validate qabel improvement | |
| Dispatch canary + golden-file regression | |

---

### Day 3 — WS1 Phase 2: Validate Pattern A

**Status:** NOT STARTED

| Task | Status |
|---|---|
| Test all Pattern A models | |
| Full pipeline regression | |
| Document improvements | |

---

### Day 4 — WS1 Phase 2 Continue

**Status:** NOT STARTED

| Task | Status |
|---|---|
| Fix secondary issues | |
| Quality gate | |
| PR for WS1 Phase 1-2 | |

---

### Day 5 — Checkpoint 1 + WS1 Phase 3 + WS2

**Status:** NOT STARTED

| Task | Status |
|---|---|
| Checkpoint 1 evaluation | |
| Begin offset-alias fix (polygon, himmel16) | |
| Begin subcategory H batch fix | |

#### Checkpoint 1 (Day 5)

| Criterion | GO | CONDITIONAL GO | NO-GO |
|---|---|---|---|
| Alias regression | 0 | ≤ 1 | > 1 |
| Pattern A improvement | ≥ 3 | ≥ 1 | 0 |
| Tests | All pass | All pass | Failures |

**Decision:** _pending_

---

### Day 6 — WS1 Phase 3 + WS2 Tier 1

**Status:** NOT STARTED

| Task | Status |
|---|---|
| Complete offset-alias fix | |
| Complete subcategory H batch fix | |

---

### Day 7 — WS2 Complete + WS3 Tier 1

**Status:** NOT STARTED

| Task | Status |
|---|---|
| Complete remaining WS2 fixes | |
| Exclude Category C models (orani, feasopt1, iobalance) | |
| Check alias fix impact on chenery/cesam/korcge | |

---

### Day 8 — WS2 Tier 2 + WS4

**Status:** NOT STARTED

| Task | Status |
|---|---|
| Fix decomp, ramsey, worst | |
| Fix mine internal error | |

---

### Day 9 — WS1 Phase 4 + WS2 Tier 3 + WS4

**Status:** NOT STARTED

| Task | Status |
|---|---|
| Investigate kand (Pattern B) | |
| Investigate launch (Pattern D) | |
| Investigate prolog regression | |
| Profile iswnm timeout | |

---

### Day 10 — Checkpoint 2

**Status:** NOT STARTED

| Task | Status |
|---|---|
| Checkpoint 2 evaluation | |
| Fix bearing/pak/rocket (if time) | |

#### Checkpoint 2 (Day 10)

| Criterion | GO | CONDITIONAL GO | NO-GO |
|---|---|---|---|
| Solve | ≥ 92 | ≥ 89 | < 89 |
| Match | ≥ 52 | ≥ 50 | < 49 |
| path_syntax_error | ≤ 18 | ≤ 20 | > 23 |
| Tests | All pass | All pass | Failures |

**Decision:** _pending_

---

### Day 11 — Buffer / Overflow

**Status:** NOT STARTED

| Task | Status |
|---|---|
| Unfinished tasks from Days 1-10 | |
| Stretch goals | |

---

### Day 12 — Sprint Close Prep

**Status:** NOT STARTED

| Task | Status |
|---|---|
| File deferred issues (sprint-25 label) | |
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
| Sprint 24 Retrospective | |
| CHANGELOG.md update | |
| PROJECT_PLAN.md Rolling KPIs | |
| Sprint 25 recommendations | |
