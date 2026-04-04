# model_infeasible Triage — Sprint 24

**Created:** 2026-04-04
**Sprint:** 24 (Prep Task 5)
**Models Analyzed:** 14

---

## Executive Summary

14 models currently fail with model_infeasible (up from 12 in Sprint 23 baseline). The composition changed significantly: 6 Sprint 23 models were fixed (markov, spatequ, paperco, sparta, prolog, cpack), but 8 new models entered the category. 8 of 14 models (57%) use aliases, with 4 having HIGH alias-fix potential. 3 models are candidates for permanent exclusion (structural incompatibility).

**Target:** Reduce from 14 to ≤ 8 (fix or exclude at least 6 models).

---

## Classification

| Model | Category | Aliases | Root Cause | GitHub Issue | Fix Effort |
|---|---|---|---|---|---|
| bearing | A (KKT bug) | None | MCP pairing mismatch (44 eq ≠ 42 var) | #757, #1199 | 3-5h |
| chenery | A (KKT bug) | [j] | Division by zero in stationarity; alias AD | #763, #1177 | 3-4h |
| pak | A (KKT bug) | None | Lead/lag Jacobian incomplete | #1049 | 3-4h |
| rocket | A (KKT bug) | None | Jacobian explosion from lag-indexed eqs | #1134 | 3-4h |
| cesam | A (KKT bug) | [j, jj, +4] | Alias-heavy; related to cesam2 pairing | #1041 | 4-5h |
| korcge | A (KKT bug) | [j] | CGE alias gradient mismatch | #1138 | 3-4h |
| chain | B (PATH conv.) | [i] | Non-convex catenary; near-feasible (0.11) | #1150 | 2-3h |
| lnts | B (PATH conv.) | None | Degenerate start; 100 zero rows | — | 3-4h |
| mathopt3 | B (PATH conv.) | None | Correct MCP; poor starting point | — | 2-3h |
| robustlp | B (PATH conv.) | [k] | Near-feasible (3.6e-04); initialization | #1105 (closed) | 2-3h |
| agreste | B (PATH conv.) | [sp] | High iteration count; unknown root cause | — | 3-4h |
| orani | C (incompatible) | [cp, sp, ip] | Percentage-change model; structural | #765 | N/A (exclude) |
| feasopt1 | C (incompatible) | None | GAMS test model; structural | — | N/A (exclude) |
| iobalance | C (incompatible) | [j] | Balance model; structural | — | N/A (exclude) |

**Category Distribution:**
- **A (KKT formulation bug):** 6 models — fixable
- **B (PATH convergence):** 5 models — need warm-start or parameter tuning
- **C (structural incompatibility):** 3 models — permanent exclusion candidates

---

## Alias Overlap with Priority 1 (Alias Differentiation)

| Model | Alias Count | Alias-Fix Potential | Notes |
|---|---|---|---|
| cesam | 6 | HIGH | Heavy alias usage; likely alias AD bug |
| chenery | 1 | HIGH | Division by zero may be alias-related |
| korcge | 1 | HIGH | CGE model in #1138 alias family |
| chain | 1 | MEDIUM | Near-feasible; alias fix may help convergence |
| agreste | 1 | LOW | Convergence issue, not derivative |
| robustlp | 1 | LOW | Initialization issue |
| orani | 3 | NONE | Structural incompatibility |
| iobalance | 1 | NONE | Structural incompatibility |

**4 models with HIGH alias-fix potential:** cesam, chenery, korcge, chain. If alias differentiation (Sprint 24 Priority 1) is fixed, these could move to model_optimal.

---

## Changes Since Sprint 23

**Fixed since Sprint 23 (6 models no longer infeasible):**
- markov, spatequ, paperco, sparta, prolog, cpack

**New since Sprint 23 (8 models):**
- agreste, cesam, chenery, feasopt1, iobalance, korcge, orani, rocket

**Retained from Sprint 23 (6 models):**
- bearing, chain, lnts, mathopt3, pak, robustlp

---

## Priority Ranking for ≤ 8 Target

### Tier 1: Permanent Exclusion (3 models)
**Models:** orani, feasopt1, iobalance
**Action:** Exclude from pipeline scope (structural incompatibility)
**Impact:** 14 → 11 immediately

### Tier 2: Category A Fixes Overlapping with Alias Differentiation (3 models)
**Models:** chenery, cesam, korcge
**Action:** Fix via alias differentiation (Priority 1 workstream)
**Impact:** 11 → 8 (meets ≤ 8 target)

### Tier 3: Category A Fixes — Lead/Lag Jacobian (3 models)
**Models:** bearing, pak, rocket
**Action:** Dedicated KKT/Jacobian fixes
**Impact:** 8 → 5 (exceeds target)

### Tier 4: Category B — Warm-Start (deferred)
**Models:** chain, lnts, mathopt3, robustlp, agreste
**Action:** Requires warm-start infrastructure or PATH parameter tuning
**Impact:** Deferred to Sprint 25+

---

## model_infeasible Gross Fixes/Influx Budget (PR7)

| Metric | Sprint 23 Final | Current | Delta |
|---|---|---|---|
| Total infeasible | 12 | 14 | +2 |
| Gross fixes | — | 6 (markov, spatequ, paperco, sparta, prolog, cpack) | — |
| Gross influx | — | 8 (agreste, cesam, chenery, feasopt1, iobalance, korcge, orani, rocket) | — |
| Net change | — | +2 | — |

---

## Recommendations

1. **Exclude 3 Category C models** (orani, feasopt1, iobalance) — immediate 14 → 11
2. **Fix 3 alias-related Category A models** (chenery, cesam, korcge) via Priority 1 — 11 → 8
3. **Fix 3 lead/lag Category A models** (bearing, pak, rocket) if time permits — 8 → 5
4. **Defer 5 Category B models** to Sprint 25+ (need warm-start infrastructure)
5. **Target achievable:** Tier 1 + Tier 2 = 6 models resolved → 14 - 6 = 8 (meets ≤ 8)
