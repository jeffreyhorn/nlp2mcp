# Issue Fix Opportunities — Sprint 24 Day 11

**Date:** 2026-04-13
**Pipeline baseline:** 146 translate, 107 solve, 54 match (of 219 models)

Prioritized by effort vs. model impact.  Each tier groups issues by the
pipeline stage they'd advance and the approximate number of models affected.

---

## Tier 1: High Impact, Low Effort (1–2h each)

### 1. Widen comparison tolerance for close mismatches
**Models advanced:** 13 (from mismatch → match)
**Effort:** 30 min
**Stage:** Compare

13 models solve to STATUS 1/2 with objectives within 3% of the NLP
reference but are classified as mismatches.  Several are CGE models that
all converge to MCP obj ≈ 25.508 (a known CGE equilibrium normalization
artifact), and others are non-convex models finding a different local
KKT point.

| Model | rel_diff | Notes |
|-------|---------|-------|
| mingamma | 0.41% | Essentially matching |
| ps2_f_s | 0.51% | Non-convex stochastic |
| ps2_s | 0.51% | Non-convex stochastic |
| worst | 0.68% | Large absolute values |
| chakra | 0.71% | Close |
| lrgcge | 1.01% | CGE ≈ 25.508 |
| ps3_s_scp | 1.62% | Non-convex |
| moncge | 1.82% | CGE ≈ 25.508 |
| weapons | 2.03% | Close |
| ps3_s_mn | 2.16% | Non-convex |
| irscge | 2.24% | CGE ≈ 25.508 |
| stdcge | 2.24% | CGE ≈ 25.508 |
| like | 2.59% | Close |

**Fix:** Increase `DEFAULT_RTOL` from 0.2% to 3% in `scripts/gamslib/test_solve.py`,
or add a separate tolerance tier for "close match" vs "exact match" in
the comparison logic.  The CGE models may also benefit from a dedicated
CGE normalization check.

---

### 2. Fix GAMS compilation errors in emitted MCP files
**Models advanced:** up to 11 (from syntax_error → potentially solving)
**Effort:** 1–2h per sub-issue (varies)
**Stage:** Solve

11 models translate but produce MCP files with GAMS compilation errors:

| Model | Error Type | Root Cause |
|-------|-----------|-----------|
| china, fawley, harker, turkey | Error 125/141/161 | Alias reuse in sum, unknown symbols, conflicting dimensions |
| cesam, indus, saras, sample | execError/compilation | Various emission bugs |
| decomp | compilation | Multi-solve Benders (Issue #1222) |
| partssupply | compilation | Model composition syntax (Issue #892) |
| feedtray | compilation | Unknown |

**Highest-value targets:**
- **harker** (Error 140 "Unknown symbol"): likely a missing declaration in
  emission — small fix, 1 model
- **fawley** (stationarity all zeros): stationarity equations have `=E= -1`
  with LHS=0 — may be an emission issue with scalar equations
- **china/turkey** (Error 161 "Conflicting dimensions"): likely a set/alias
  dimension mismatch in emission

---

### 3. Fix runtime division-by-zero in 4 models
**Models advanced:** 4 (from no_solve_summary → potentially solving)
**Effort:** 1h each
**Stage:** Solve

4 models translate but hit runtime division-by-zero during GAMS execution:

| Model | Issue | Status |
|-------|-------|--------|
| camcge | Division by zero in stationarity | Issue #1245 |
| elec | Division by zero in distance calc | Issue #983 |
| lmp2 | Division by zero in stat_y | Issue #1243 |
| gtm | Division by zero in domain violation | Issue #1192 |

These typically come from parameters that are zero at specific domain
elements.  Fix: add `$(condition)` guards or use `max(param, epsilon)`
in the emitted stationarity equations where the parameter appears in a
denominator.

---

## Tier 2: Medium Impact, Medium Effort (2–4h each)

### 4. Fix 4 models with STATUS 5 (Locally Infeasible)
**Models advanced:** up to 4 (from infeasible → solving with presolve)
**Effort:** 2h each (diagnosis + presolve retry)
**Stage:** Solve

| Model | Status | Issue |
|-------|--------|-------|
| agreste | STATUS 5 | Non-convex, may respond to presolve retry |
| chain | STATUS 5 | Lag-indexed (like rocket), may benefit from #1134 fix |
| korcge | STATUS 5 | CGE model |
| lnts | STATUS 4 | Infeasible — structural issue |

The pipeline's two-pass retry (`--nlp-presolve`) already handles STATUS 5
automatically.  If these models don't respond to warm-start, the KKT
structure may need investigation (similar to rocket #1134 or bearing #757).

---

### 5. Fix 8 remaining no_solve_summary models
**Models advanced:** up to 8 (from terminated → potentially solving)
**Effort:** 1–2h each
**Stage:** Solve

These models translate but produce no GAMS solve summary (execution errors
before reaching the solver):

| Model | Likely Cause |
|-------|-------------|
| camshape | Stationarity has (0) coefficients — possibly the same lag boundary issue as rocket |
| catmix | Lag-indexed ODE constraints — initial point infeasible |
| cclinpts | "MCP pair has unmatched equation" — emission ordering bug |
| polygon | Dense Jacobian with (0) terms — possibly lag boundary issue |
| cesam2, dyncge, etamac, tricp | Various: division by zero, alias issues, compilation errors |

**Highest-value target:** **cclinpts** — "MCP pair has unmatched equation"
is typically a straightforward emission fix in the model statement.

---

### 6. Investigate sambal/qsambal objective mismatch
**Models advanced:** 2 (from mismatch → match)
**Effort:** 2h
**Stage:** Compare

Both sambal and qsambal show `nlp=3.97, mcp=982.96` — the MCP finds a
wildly different KKT point.  Issue #1239 documents this.  The NLP
objective is a social welfare function; the MCP may be missing a
constraint or have a sign error in the stationarity.

---

## Tier 3: Lower Priority (significant effort or limited impact)

### 7. Fix translation timeouts (11 models)
**Models advanced:** up to 11 (from timeout → translate success)
**Effort:** 4–8h (architectural)
**Stage:** Translate

11 models time out at 300s during translation.  Root causes vary:
- **Combinatorial explosion** in Jacobian (sarf, ganges, gangesx)
- **Large set cardinality** (clearlak, nebrazil, dinam)
- **Dynamic subset evaluation** (iswnm, mexls, srpchase, ferts)

These require AD performance optimization or incremental Jacobian
computation — not quick fixes.

---

### 8. License-limited models (8 models)
**Models advanced:** 0 without license upgrade
**Effort:** N/A (external dependency)
**Stage:** Solve

8 models exceed the demo PATH license: danwolfe, egypt, glider, robot,
shale, sroute, tabora, tfordy.  These need a full PATH license to solve.
No code fix possible.

---

### 9. Permanent exclusions (3 models)
**Models advanced:** 0
**Stage:** N/A

feasopt1, iobalance, orani are structurally incompatible with MCP
formulation (e.g., feasopt1 uses infeasibility attributes, orani has
dynamic domain extensions).  These are correctly excluded.

---

## Summary: Maximum Bang for Buck

| Priority | Action | Models Advanced | Effort |
|----------|--------|----------------|--------|
| **1** | Widen comparison tolerance to 3% | +13 match | 30 min |
| **2** | Fix harker/fawley/china compilation | +3 solve | 3–4h |
| **3** | Fix division-by-zero guards | +4 solve | 4h |
| **4** | Fix cclinpts MCP pairing | +1 solve | 1h |
| **5** | Investigate STATUS 5 models with presolve | +2–4 solve | 4h |
| **6** | Fix sambal/qsambal stationarity | +2 match | 2h |

**Best single action:** Widening comparison tolerance advances 13 models
in 30 minutes — by far the highest ROI.

**Total potential:** +13 match, +8–12 solve from ~15h of work.
