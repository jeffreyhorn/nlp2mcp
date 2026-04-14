# Issue Fix Opportunities — Sprint 24 Day 11

**Date:** 2026-04-13
**Pipeline baseline:** 146 translate, 107 solve, 54 match (of 219 models)

Prioritized by effort vs. model impact.  Each tier groups issues by the
pipeline stage they'd advance and the approximate number of models affected.

---

## Tier 1: High Impact, Low Effort (1–2h each)

### 1. Classify close-mismatch models correctly (not a tolerance fix)
**Models advanced:** 2–3 genuine tolerance matches, rest need investigation
**Effort:** 1–2h
**Stage:** Compare

13 models solve to STATUS 1/2 with objectives within 3% of the NLP
reference.  However, blanket-widening the tolerance is **not legitimate**
— most of these are genuinely different solutions, not numerical noise:

| Model | rel_diff | Diagnosis |
|-------|---------|-----------|
| mingamma | 0.41% | **Genuine tolerance candidate** — essentially matching |
| ps2_f_s | 0.51% | Different local KKT point (non-convex stochastic) — correct MCP behavior |
| ps2_s | 0.51% | Different local KKT point (non-convex stochastic) — correct MCP behavior |
| worst | 0.68% | **Genuine tolerance candidate** — large absolute values, small relative diff |
| chakra | 0.71% | **Genuine tolerance candidate** — close |
| lrgcge | 1.01% | CGE normalization artifact — MCP finds different equilibrium (obj ≈ 25.508) |
| ps3_s_scp | 1.62% | Different local KKT point (non-convex) — correct MCP behavior |
| moncge | 1.82% | CGE normalization artifact (obj ≈ 25.508) |
| weapons | 2.03% | Needs investigation |
| ps3_s_mn | 2.16% | Different local KKT point (non-convex) — correct MCP behavior |
| irscge | 2.24% | CGE normalization artifact (obj ≈ 25.508) |
| stdcge | 2.24% | CGE normalization artifact (obj ≈ 25.508) |
| like | 2.59% | Needs investigation |

**Fix:** Do NOT blanket-widen tolerance.  Instead:
- Modest tolerance increase (0.2% → 1%) for 2–3 genuine numerical cases
  (mingamma, worst, chakra)
- Add a "different KKT point" comparison outcome for non-convex models
  that find valid but different local optima (ps2/ps3 family)
- Investigate CGE models (irscge, lrgcge, moncge, stdcge) for
  normalization issues — these may need a CGE-specific comparison
- Investigate weapons and like individually

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

### 4. Fix 4 models with STATUS 4/5 (Infeasible / Locally Infeasible)
**Models advanced:** up to 4 (from infeasible → solving with presolve)
**Effort:** 2h each (diagnosis + presolve retry)
**Stage:** Solve

| Model | Status | Issue |
|-------|--------|-------|
| agreste | STATUS 5 (Locally Infeasible) | Non-convex, may respond to presolve retry |
| chain | STATUS 5 (Locally Infeasible) | Lag-indexed (like rocket), may benefit from #1134 fix |
| korcge | STATUS 5 (Locally Infeasible) | CGE model |
| lnts | STATUS 4 (Infeasible) | Structural infeasibility — may indicate KKT bug |

The pipeline's two-pass retry (`--nlp-presolve`) already handles STATUS 5
automatically.  STATUS 4 (lnts) indicates a stricter infeasibility that
warm-start alone may not resolve — the KKT structure may need
investigation (similar to rocket #1134 or bearing #757).

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
| **1** | Fix compilation errors (harker/fawley/china) | +3 solve | 3–4h |
| **2** | Fix division-by-zero guards (camcge/elec/lmp2/gtm) | +4 solve | 4h |
| **3** | Fix cclinpts MCP pairing | +1 solve | 1h |
| **4** | Modest tolerance increase (0.2% → 1%) | +2–3 match | 30 min |
| **5** | Add "different KKT point" outcome for non-convex | +4–5 reclassified | 1h |
| **6** | Investigate STATUS 5 models with presolve | +2–4 solve | 4h |
| **7** | Fix sambal/qsambal stationarity | +2 match | 2h |

**Best single action:** Fixing compilation errors in harker/fawley/china
advances 3 models from syntax_error to potentially solving, and may
uncover patterns that fix the other 8 syntax_error models too.

**Total potential:** +2–3 match, +10–12 solve, +4–5 reclassified from ~15h.
