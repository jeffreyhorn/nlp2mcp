# Triage: path_solve_terminated Models (10)

**Date:** 2026-03-18
**Branch:** `planning/sprint23-task2`
**Prep Task:** 2 (from PREP_PLAN.md)

## Executive Summary

All 10 path_solve_terminated models were analyzed by running MCP generation and examining GAMS solve output. Key findings:

- **9 of 10 fail before PATH runs** due to execution errors (6 models: division by zero, domain violations, `inf*0` undefined) or MCP pairing errors (2 models: empty equations). Only **elec** actually reaches PATH and fails convergence.
- **1 model (etamac) already solves optimally** — issues #984, #1043, #1045 were fixed in Sprint 22. The gamslib_status.json is stale; a fresh GAMS run produces Solver Status 1 (Normal Completion), Model Status 1 (Optimal), obj=5.090.
- **7 models are fixable in Sprint 23** with targeted effort (estimated 11-18h total for Tiers 1+2).
- **2 CGE models (dyncge, twocge) have MCP pairing errors** requiring empty-equation investigation — moderate effort but high uncertainty.
- The dominant root cause is **Category B: execution error** (6 of 10), mostly division-by-zero from missing dollar conditions or inadequate variable initialization.

## Root Cause Classification

| Model | Type | Category | Error | Issue(s) | Fix Effort | Sprint 23? |
|-------|------|----------|-------|----------|-----------|-----------|
| etamac | NLP | **SOLVED** | Already optimal (obj=5.090) | #984 ✅, #1043 ✅, #1045 ✅ | 0h (re-run pipeline) | Yes |
| sambal | NLP | B | Division by zero: missing `$` conditions in stationarity | #862, #1112 | 4-6h | Yes (needs #1112) |
| qsambal | QCP | B | Division by zero: same pattern as sambal | (none) | 0-1h (after sambal) | Yes (after sambal) |
| maxmin | NLP | B | Division by zero: `1/sqrt(0)` from self-pair `n==nn` in stationarity | #939 ✅ (partial) | 2-3h | Yes |
| fawley | LP | B | Division by zero: `1/sum(...)` where sum evaluates to 0 | (none) | 1-2h | Yes |
| gtm | NLP | B | Division by zero + log(0): supply vars `s(i)` initialized at 0 | #827 | 2-3h | Yes |
| rocket | NLP | B | `+-infinity * 0 undefined`: mass variable has no finite upper bound | (none) | 2-3h | Yes |
| elec | NLP | C | PATH terminated: Solver Status 4, Model Status 6 (Intermediate Infeasible), 503 iterations | #983 | 3-4h | Maybe |
| dyncge | NLP | A | MCP pairing: empty equation `eqpf2` with non-fixed multiplier (4 instances) | (none) | 3-5h | Uncertain |
| twocge | NLP | A | MCP pairing: empty equations `eqpw` (4) + `eqw` (4), 8 total | #906, #970 | 4-6h | Uncertain |

### Category Distribution

| Category | Count | Models |
|----------|-------|--------|
| Already solved | 1 | etamac |
| A: MCP pairing error | 2 | dyncge, twocge |
| B: Execution error | 6 | sambal, qsambal, maxmin, fawley, gtm, rocket |
| C: PATH convergence | 1 | elec |
| D: Pre-solver infeasibility | 0 | (none) |

---

## Per-Model Analysis

### etamac (ALREADY SOLVED)

**Type:** NLP | **GAMS Size:** 18 vars, 13 eqs
**Current gamslib_status.json:** path_solve_terminated (stale — `no_solve_summary`)
**Actual Status:** Solver Status 1 (Normal Completion), Model Status 1 (Optimal), obj=5.090

**History:** Three issues were filed and fixed during Sprint 22:
- #984 (division by zero / log(0)) — fixed via `.l` clamping
- #1043 (8 MCP pairing errors on `totalcap`) — fixed via stationarity domain fix
- #1045 (locally infeasible) — fixed

**Evidence:** Local GAMS run (2026-03-11) produced the following solve summary:
```
**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal
REPORT SUMMARY: 0 NONOPT, 0 INFEASIBLE, 0 UNBOUNDED
nlp2mcp_obj_val = 5.090
```
Note: `.lst` files are gitignored. To reproduce, run `gams data/gamslib/mcp/etamac_mcp.gms` locally. The committed MCP file (`data/gamslib/mcp/etamac_mcp.gms`) is the input; the pipeline's `gamslib_status.json` entry will be updated on the next full pipeline run.

**Action:** Re-run pipeline to update gamslib_status.json. No code changes needed.

---

### sambal (Category B: Execution Error)

**Type:** NLP | **GAMS Size:** 3 vars, 3 eqs
**Error:** Division by zero in `stat_x(i,j)` stationarity equations (line 88)
**Root Cause:** The stationarity equation contains `xb(i,j) * xw(i,j) * 2 * (xb(i,j) - x(i,j)) * (-1) / sqr(xb(i,j))` terms. When `xb(i,j)` is NA (uninitialized), the original model uses `$(xw(i,j))` dollar conditions to skip those entries. The NLP→MCP AD (automatic differentiation) generates derivatives for all index combinations, but the dollar conditions are not propagated through to the stationarity equations, causing division by `sqr(0)`.

**MCP Generation Warnings:** Clean (no warnings)
**Dependencies:** Requires #1112 (dollar-condition propagation through AD/stationarity)
**Issues:** #862 (open), #1112 (open — umbrella for dollar-condition propagation)
**Fix Effort:** 4-6h (architectural: AD condition propagation)
**Fix Approach:** Implement dollar-condition propagation in stationarity builder so that `$(xw(i,j))` guards appear on the derivative terms

---

### qsambal (Category B: Execution Error)

**Type:** QCP | **GAMS Size:** 3 vars, 3 eqs
**Error:** Division by zero in `stat_x(i,j)` — identical pattern to sambal
**Root Cause:** Same as sambal. qsambal is a quadratic variant of the same model with identical conditional structure.

**MCP Generation Warnings:** Skipped param 'rep'
**Dependencies:** Same fix as sambal (#1112)
**Issues:** None (inherits sambal fix)
**Fix Effort:** 0-1h incremental after sambal is fixed
**Fix Approach:** Verify fix automatically applies after sambal fix

**Note:** qsambal uses `$(xb(i,j) = na)` (direct comparison) while sambal uses `$(mapval(xb(i,j)) = mapval(na))`. Both are equivalent GAMS idioms for testing NA. The MCP emitter correctly handles both.

---

### maxmin (Category B: Execution Error)

**Type:** NLP | **GAMS Size:** 3 vars, 2 eqs
**Error:** Division by zero in `stat_point(p1,x)` at line 104
**Root Cause:** The stationarity equation for `point(n,d)` contains distance terms `1 / (2 * sqrt(sum(d__, sqr(point(n,d__) - point(nn,d__)))))`. When `n == nn` (self-pair), the sum of squared differences is zero, giving `1/sqrt(0) = 1/0`. The original `mindist1a` constraint uses `low(n,nn)` (with `ord(n) > ord(nn)`) to exclude self-pairs, but the stationarity builder enumerates all `(n,nn)` combinations when expanding the Jacobian, including self-pairs.

**MCP Generation Warnings:** W301 nonlinear equality (defdist)
**Dependencies:** None (localized fix in stationarity/Jacobian expansion)
**Issues:** #939 (closed — partial fix for smin arity; self-pair issue remains)
**Fix Effort:** 2-3h
**Fix Approach:** Propagate the `low(n,nn)` domain condition from `mindist1a` through the Jacobian to the stationarity equation, adding `$(low(n,nn))` guards on the distance derivative terms. This is a specific instance of the broader dollar-condition propagation problem (#1112) but may be fixable with a targeted approach since the condition is on the constraint domain rather than individual terms.

---

### fawley (Category B: Execution Error)

**Type:** LP | **GAMS Size:** 12 vars, 11 eqs
**Error:** Division by zero at line 77 in parameter initialization
**Root Cause:** The emitted MCP contains `bp(k,p)$(kuse(k,p)) = 1 / sum(c$(ap(c,p) < 0), (-1) * ap(c,p) * prop(c,"gravity"))`. For some `(k,p)` combinations where `kuse(k,p)` is true, the sum over `c$(ap(c,p) < 0)` evaluates to zero (no components with negative `ap` values for that product), causing `1/0`.

**MCP Generation Warnings:** SetMembershipTest evaluation failures in pbal constraint, variable 'u' domain mismatch
**Dependencies:** None (localized fix)
**Issues:** None
**Fix Effort:** 1-2h
**Fix Approach:** The parameter assignment needs a stronger guard: the dollar condition should also check that the denominator is non-zero, or the emitter should preserve the original model's conditional structure that avoids the zero-denominator case. Since fawley is an LP, the MCP transformation is straightforward (linear complementarity) and the fix is in parameter emission, not KKT derivation.

---

### gtm (Category B: Execution Error)

**Type:** NLP | **GAMS Size:** 7 vars, 5 eqs
**Error:** Multiple errors: division by zero, `log: FUNC DOMAIN: x < 0`, `UNDF` in equation `bdef`
**Root Cause:** Supply variables `s(i)` are initialized at zero (`.l = 0`). The objective involves `log(s(i))` terms, and the stationarity equations contain `1/s(i)` derivative terms. With `s(i) = 0`, both `log(0)` and `1/0` are undefined.

**MCP Generation Warnings:** Clean (no warnings during generation)
**Dependencies:** None (initialization fix)
**Issues:** #827 (open — broader issue about domain violations from zero-filled parameters)
**Fix Effort:** 2-3h
**Fix Approach:** Improve variable initialization in the MCP emitter. For variables appearing inside `log()` or as denominators, clamp `.l` values to a small positive value (e.g., 0.01) instead of 0. This is the same pattern that was successfully applied to etamac (#984). Alternatively, use the original model's `.l` values when available.

---

### rocket (Category B: Execution Error)

**Type:** NLP | **GAMS Size:** 6 vars, 6 eqs
**Error:** `+-infinity * 0 is undefined` in `stat_m` equations (lines 213-214)
**Root Cause:** The mass variable `m` has no finite upper bound (upper = +INF). The KKT system generates upper-bound complementarity terms `piU_m * (ub - m)`, but when `ub = +INF`, the bound multiplier `piU_m` should be zero. However, GAMS evaluates `INF * 0` as undefined rather than applying the limit. The emitter needs to suppress upper-bound complementarity terms for variables with infinite bounds.

**MCP Generation Warnings:** 11 nonconvex patterns (W303 bilinear terms, W304 division by variable)
**Dependencies:** None (emitter fix)
**Issues:** None
**Fix Effort:** 2-3h
**Fix Approach:** In the KKT emitter, skip generation of `piU_*` variables and `comp_up_*` equations for variables where the upper bound is `+INF`. Similarly skip `piL_*` / `comp_lo_*` for variables where the lower bound is `-INF`. This is a general fix that would apply to all models.

---

### elec (Category C: PATH Convergence)

**Type:** NLP | **GAMS Size:** 4 symbolic vars, 2 symbolic eqs | **MCP Instantiated:** 101 vars, 101 eqs (25 electrons: x/y/z/nu_ball indexed over i, plus scalar potential and obj)
**Error:** Solver Status 4 (Terminated by Solver), Model Status 6 (Intermediate Infeasible)
**Root Cause:** This is the only model that actually reaches PATH and fails convergence. PATH ran 503 iterations over 6.3 seconds but could not find a complementary solution. The electron placement problem is non-convex (W301 nonlinear equality, W304 division), and the KKT system may have multiple local solutions that PATH cannot navigate.

**MCP Generation Warnings:** W301 nonlinear equality (ball), W304 division (obj)
**Dependencies:** None, but may require PATH parameter tuning or reformulation
**Issues:** #983 (open)
**Fix Effort:** 3-4h (uncertain — may require reformulation)
**Fix Approach:** Options: (1) Try better starting points (use convexity solve's optimal as `.l` initialization), (2) Increase PATH iteration limit or adjust crash method, (3) Reformulate the ball constraint. Since the original NLP solves (obj=243.8), the KKT system should have a solution — the challenge is PATH finding it.

---

### dyncge (Category A: MCP Pairing Error)

**Type:** NLP | **GAMS Size:** 31 vars, 29 eqs
**Error:** MCP pair `eqpf2.nu_eqpf2` has empty equation but associated variable is NOT fixed (4 instances)
**Root Cause:** The equation `eqpf2` is emitted with an empty body for all 4 sector indices. This suggests the stationarity builder produced a zero-gradient for the equation, likely because the Jacobian entries are all zero or the equation involves domain index reuse that the alias workaround doesn't fully resolve (GAMS Error 125 pattern).

**MCP Generation Warnings:** 37 nonconvex patterns (W304 division in eqM, eqD, eqE, eqDs, eqII)
**Dependencies:** Needs investigation of why eqpf2 produces empty stationarity equations
**Issues:** None (no prior investigation)
**Fix Effort:** 3-5h (uncertain — requires understanding CGE equation structure)
**Fix Approach:** Examine the original `eqpf2` equation, its Jacobian entries, and the stationarity builder's processing. The empty equation suggests either (a) the gradient is genuinely zero (unlikely for a production function), (b) the Jacobian evaluator fails to collect terms, or (c) domain aliasing causes terms to be dropped. Fixing requires debugging the stationarity builder for this specific equation pattern.

**CGE Risk:** dyncge is a CGE (Computable General Equilibrium) model. Sprint 22 confirmed orani (another CGE) is permanently incompatible. However, dyncge's error pattern (empty equation) differs from orani's (structural infeasibility from linearized percentage-change formulation). dyncge may be fixable if the empty-equation issue is a builder bug rather than an inherent structural problem.

---

### twocge (Category A: MCP Pairing Error)

**Type:** NLP | **GAMS Size:** 28 vars, 28 eqs
**Error:** MCP pair `eqpw.nu_eqpw` (4 instances) + `eqw.nu_eqw` (4 instances) = 8 empty-equation errors
**Root Cause:** Same class as dyncge. Two equations (`eqpw`, `eqw`) are emitted with empty bodies. twocge is a 2-country CGE model closely related to dyncge, and the empty equations likely share the same stationarity builder bug.

**MCP Generation Warnings:** 37 nonconvex patterns (similar to dyncge — both CGE models)
**Dependencies:** Same fix as dyncge; fix one, likely fixes the other
**Issues:** #906 (open — missing SAM data + trade equations), #970 (open — MCP locally infeasible)
**Fix Effort:** 4-6h (includes investigation shared with dyncge)
**Fix Approach:** Same as dyncge. Since dyncge and twocge are structurally similar, a fix for one should apply to the other. The existing open issues (#906, #970) suggest additional problems beyond the empty-equation bug.

**CGE Risk:** Same as dyncge. twocge is a multi-country CGE with potentially more complex equation structures. Even if the empty-equation bug is fixed, the model may shift to model_infeasible (cascade risk per KU-05).

---

## Fix Priority Ranking

Models ranked by fix leverage (benefit vs. effort), considering dependencies and cascade potential.

### Tier 1: Quick Wins (fix in Sprint 23 Days 1-3)

| Priority | Model | Effort | Benefit | Notes |
|----------|-------|--------|---------|-------|
| 1 | **etamac** | 0h | -1 path_solve_terminated | Already solved; just re-run pipeline |
| 2 | **rocket** | 2-3h | -1 path_solve_terminated | Infinite-bound suppression; general fix benefits all models |
| 3 | **fawley** | 1-2h | -1 path_solve_terminated | Parameter guard fix; LP model so simple MCP |
| 4 | **gtm** | 2-3h | -1 path_solve_terminated | Variable initialization clamping; same pattern as etamac fix |

**Tier 1 total:** 5-8h for 4 models (etamac + 3 fixes)

### Tier 2: Moderate Effort (fix in Sprint 23 Days 3-7)

| Priority | Model | Effort | Benefit | Notes |
|----------|-------|--------|---------|-------|
| 5 | **maxmin** | 2-3h | -1 path_solve_terminated | Domain condition propagation; targeted fix possible |
| 6 | **sambal** | 4-6h | -1 path_solve_terminated | Requires #1112 (dollar-condition propagation) |
| 7 | **qsambal** | 0-1h | -1 path_solve_terminated | Free after sambal fix |

**Tier 2 total:** 6-10h for 3 models (incl. #1112 architectural work)

### Tier 3: High Uncertainty (evaluate mid-sprint)

| Priority | Model | Effort | Benefit | Notes |
|----------|-------|--------|---------|-------|
| 8 | **elec** | 3-4h | -1 path_solve_terminated (uncertain) | PATH convergence; may need reformulation |
| 9 | **dyncge** | 3-5h | -1 path_solve_terminated (uncertain) | CGE empty-equation bug; cascade risk |
| 10 | **twocge** | 4-6h | -1 path_solve_terminated (uncertain) | CGE empty-equation; shared fix with dyncge |

**Tier 3 total:** 10-15h for 3 models (high uncertainty, cascade risk)

---

## Recommendation for Sprint 23

### Target: Fix 7 models (Tiers 1 + 2), reducing path_solve_terminated from 10 to 3

**Rationale:**
- Tier 1 (4 models, 5-8h) includes etamac (free), rocket, fawley, gtm — all localized fixes with no dependencies
- Tier 2 (3 models, 6-10h) includes maxmin, sambal, qsambal — requires #1112 but aligns with Priority 3 (dollar-condition propagation)
- Combined effort: 11-18h, well within the 8-12h Priority 1 budget + Priority 3 overlap
- Achieving 7 fixes exceeds the "≤ 5 remaining" target (10 - 7 = 3 remaining)

**Deferred to Sprint 24:**
- **elec**: PATH convergence issue requires experimentation; low confidence of fix
- **dyncge/twocge**: CGE models with empty-equation bugs + cascade risk; investigate but don't commit to fix

### Schedule Suggestion

| Day | Models | Work |
|-----|--------|------|
| 1-2 | etamac, rocket, fawley | Re-run etamac; implement infinite-bound suppression; fix fawley parameter guard |
| 3-4 | gtm, maxmin | Variable initialization clamping; self-pair domain propagation |
| 5-7 | sambal, qsambal | Dollar-condition propagation (#1112); verify qsambal follows |
| 8+ | elec, dyncge, twocge | Investigation only; fix if time permits |

---

## Cascade Risk Assessment (KU-05)

Models likely to cascade from path_solve_terminated → model_infeasible when primary error is fixed:

| Model | Cascade Risk | Rationale |
|-------|-------------|-----------|
| etamac | None | Already solves optimally |
| rocket | Medium | 11 nonconvex patterns; may be locally infeasible after inf*0 fix |
| fawley | Low | LP model; linear MCP should solve cleanly |
| gtm | Medium | Non-convex (log terms); PATH may fail after initialization fix |
| maxmin | Medium | Non-convex (sqrt); PATH may not converge after self-pair fix |
| sambal | Low | Small model; clean MCP generation |
| qsambal | Low | Same as sambal |
| elec | N/A | Already at PATH convergence stage |
| dyncge | High | CGE model; even if empty equations fixed, may be structurally infeasible |
| twocge | High | Same as dyncge; multiple open issues suggest deeper problems |

**Estimate:** 2-3 models may cascade to model_infeasible (rocket, gtm, and/or maxmin). This should be tracked per PR7 (separate gross fixes from influx).

---

## MCP Generation Summary

All 10 models parse, translate, and generate MCP files successfully. The failures occur at GAMS solve time.

| Model | MCP Lines | Nonconvex Warnings | Generation Issues |
|-------|-----------|-------------------|-------------------|
| dyncge | 547 | 37 (W304 division) | None |
| elec | 129 | 2 (W301, W304) | None |
| etamac | 386 | 4 (W301, W303 bilinear) | Skipped params valuerep/growthrep |
| fawley | 329 | 0 | SetMembershipTest eval failures (non-fatal) |
| gtm | 216 | 0 | None |
| maxmin | 150 | 1 (W301) | None |
| qsambal | 124 | 0 | Skipped param 'rep' |
| rocket | 304 | 11 (W303, W304) | None |
| sambal | 124 | 0 | None |
| twocge | 671 | 37 (W304 division) | None |
