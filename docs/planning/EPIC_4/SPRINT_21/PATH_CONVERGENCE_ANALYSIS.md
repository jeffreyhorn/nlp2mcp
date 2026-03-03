# PATH Convergence Analysis — 29 path_solve_terminated Models

**Created:** 2026-03-03
**Sprint:** 21, Day 12 (WS8)
**Baseline:** 29 models classified as `path_solve_terminated` in Sprint 21 Baseline (`feffaa95`)
**Method:** Full pipeline re-run (`run_full_test.py --model NAME --verbose`) + direct GAMS execution on on-disk MCP files

---

## 1. Executive Summary

Of the 29 models originally classified as `path_solve_terminated` at Sprint 21 baseline, **14 now solve successfully** after Sprint 21 code improvements (Days 1–11). The remaining **15 models still fail**, but the root causes are NOT PATH convergence failures — they are **pre-solver errors** that prevent PATH from ever running.

| Category | Count | Models |
|----------|-------|--------|
| **A: Now solves (Sprint 21 fixes)** | 14 | decomp, jobt, like, polygon, ps2_f, ps2_f_s, ps2_s, ps3_f, ps3_s, ps3_s_gic, ps3_s_mn, ps3_s_scp, ps10_s, solveopt |
| **B: Execution error (starting point)** | 5 | cclinpts, elec, etamac, hs62, lands |
| **C: MCP pairing / dimension mismatch** | 4 | fdesign, hhfair, pak, trussm |
| **D: Compilation error** | 2 | camshape, qsambal |
| **E: Translation timeout** | 2 | ganges, gangesx |
| **F: Locally infeasible** | 2 | chain, rocket |

**Key finding:** None of the 15 still-failing models have actual PATH solver convergence issues. 13 models fail **before PATH runs** — during equation generation (B), model construction (C/D), or translation (E). The `path_solve_terminated` classification was a misnomer for these models; the true error is that GAMS aborts the solve before invoking PATH. The remaining 2 models (chain, rocket) do reach PATH but terminate as **locally infeasible** — PATH completed its algorithm but found no feasible solution near the starting point.

**Relaxed PATH options (convergence_tolerance, major_iteration_limit) are not applicable** to the 13 pre-solver failures because PATH never executes. For the 2 locally infeasible models, PATH did run to completion — the issue is the solution landscape, not solver configuration.

---

## 2. Per-Model Classification Table

### Category A: Now Solves Successfully (14 models)

These models were `path_solve_terminated` at baseline but now solve with Sprint 21 code improvements. The pipeline re-translates the MCP files fresh, incorporating fixes from Days 1–11.

| Model | MCP Status | Iterations | MCP Obj | NLP Match | Notes |
|-------|-----------|------------|---------|-----------|-------|
| decomp | Optimal | 19 | 0.0 | MISMATCH (diff=60) | Day 11 empty stationarity fix (#826) |
| jobt | Optimal | 340 | 81,000 | MISMATCH (diff=59,700) | Large objective divergence |
| like | Optimal | 41 | -1,218.4 | MISMATCH (diff=80) | Moderate divergence |
| polygon | Optimal | 294 | 0.0 | MISMATCH (diff=0.78) | Objective is 0 vs NLP nonzero |
| ps2_f | Optimal | 11 | 0.917 | **MATCH** | Fully correct |
| ps2_f_s | Optimal | 146 | 0.861 | MISMATCH (diff=0.0044) | Near-match, small divergence |
| ps2_s | Optimal | 146 | 0.861 | MISMATCH (diff=0.0044) | Near-match, small divergence |
| ps3_f | Optimal | 14 | 1.375 | **MATCH** | Fully correct |
| ps3_s | Optimal | 16 | 1.056 | MISMATCH (diff=0.105) | Moderate divergence |
| ps3_s_gic | Optimal | 133 | 1.056 | MISMATCH (diff=0.105) | Same as ps3_s (variant) |
| ps3_s_mn | Optimal | 19 | 1.029 | MISMATCH (diff=0.023) | Small divergence |
| ps3_s_scp | Optimal | 24 | -0.621 | MISMATCH (diff=0.014) | Small divergence |
| ps10_s | Optimal | 31 | 0.387 | MISMATCH (diff=0.146) | Moderate divergence |
| solveopt | Optimal | 0 | 6.0 | **MATCH** | Trivial MCP (0 iterations) |

**Sub-classification of A models:**
- 3 MATCH (ps2_f, ps3_f, solveopt) — fully correct KKT
- 5 near-match (ps2_f_s, ps2_s, ps3_s_mn, ps3_s_scp, ps3_s) — small objective divergence, likely initialization or KKT accuracy issues
- 6 significant mismatch (decomp, jobt, like, polygon, ps10_s, ps3_s_gic) — KKT formulation or initialization issues

### Category B: Execution Error at Starting Point (5 models)

PATH never runs. GAMS aborts during equation generation due to mathematical domain errors. Three sub-causes exist: (1) default `.l = 0` values causing domain errors in KKT gradient expressions (elec, etamac, lands), (2) rPower domain error on a parameter expression (cclinpts), and (3) division by zero in post-solve calibration code (hs62).

| Model | Error | Equation | Root Cause |
|-------|-------|----------|------------|
| cclinpts | `rPower: FUNC DOMAIN: x**y, x < 0` | stat_b(s1..s30) | Parameter expression `(1-gamma)**2` where `gamma=2` → `(-1)**2` rejected by GAMS rPower (requires non-negative base) |
| elec | `division by zero (0)` | stat_x(i1..i25) | Stationarity has `1/distance` terms; all variables initialized to 0 → zero distances |
| etamac | `division by zero (0)` + `log: FUNC SINGULAR: x = 0` | stat_c(1995..2040) | Consumption variables at 0 → log(0) and 1/c division errors |
| hs62 | `division by zero (0)` | (calibration block) | Post-solve calibration code `diff = (global - obj.l) / global` where `global = 0`; not a `.l` initialization issue |
| lands | `RHS value NA in equation` | (generation phase) | NA/undefined value in equation RHS during generation |

**Fix approach:** Different fixes per sub-cause:
- **elec, etamac, lands** (`.l = 0` domain errors): Initialize primal variables to the NLP solution's `.l` values, or use `max(x.l, epsilon)` for variables in log/power/division terms.
- **cclinpts** (rPower on parameter): Replace `(1-gamma)**2` with `sqr(1-gamma)` or `power(1-gamma, 2)` to avoid rPower domain restriction.
- **hs62** (calibration division by zero): Guard the calibration division with a conditional or remove the post-solve calibration block from the MCP file.

**Priority:** HIGH — 5 models blocked. Requires either:
1. Smarter `.l` initialization (e.g., `max(x.l, epsilon)` for variables appearing in log/power/division terms)
2. GAMS `$onEpsToZero` or `execerr` tolerance settings
3. Adding `option domlim = 100;` to MCP files to allow GAMS to continue past domain errors

### Category C: MCP Pairing / Dimension Mismatch (4 models)

The emitted MCP file has structural errors — the number of variables doesn't match the number of equations, or MCP pair references are invalid.

| Model | Error | Details |
|-------|-------|---------|
| fdesign | `Unmatched free variables = 1` | 1 extra variable with no paired equation |
| trussm | `Unmatched free variables = 1` | 1 extra variable with no paired equation |
| hhfair | `MCP pair has unmatched equation` | `a_fx_0.nu_a_fx_0` and `m_fx_0.nu_m_fx_0` pairs invalid |
| pak | `MCP pair has unmatched equation` | 4 pairs invalid: `comp_conl.lam_conl`, `c_fx_1962.nu_c_fx_1962`, etc. |

**Fix approach:** These are KKT construction or emission bugs:
- fdesign/trussm: An extra variable is emitted without a matching stationarity equation (or vice versa). Likely a variable that should be fixed or an equation that was dropped.
- hhfair/pak: Fixed-value equations (`_fx_`) are being paired with multipliers, but the equations don't appear in the model (likely because the variable is fixed and the equation was eliminated).

**Priority:** MEDIUM — requires investigation of the KKT builder for each model.

### Category D: Compilation Error (2 models)

The MCP `.gms` file fails GAMS compilation — syntax or declaration errors.

| Model | Error | Details |
|-------|-------|---------|
| camshape | `$141: Symbol declared but no values have been assigned` | Missing data assignment for a declared symbol |
| qsambal | `$141: Symbol declared but no values have been assigned` | Same error — undeclared/uninitialized parameter |

**Fix approach:** The emitter declares symbols without populating them. Need to trace which parameter/set is missing data in the emitted file.

**Priority:** MEDIUM — compilation errors in emitted code.

### Category E: Translation Timeout (2 models)

The translation stage times out (>60s) — the KKT derivation is too expensive for these large models.

| Model | Parse Result | Variables | Equations | Translation Time |
|-------|-------------|-----------|-----------|-----------------|
| ganges | SUCCESS | 74 vars | 68 eqs | >60s (timeout) |
| gangesx | SUCCESS | 74 vars | 68 eqs | >60s (timeout) |

**Fix approach:** Optimize the AD/KKT derivation pipeline for large models, or increase the translation timeout.

**Priority:** LOW for Sprint 21 — these are large models requiring significant translation optimization.

### Category F: Locally Infeasible (2 models)

PATH runs successfully (Normal Completion) but finds the system locally infeasible — there is no solution in the neighborhood of the starting point.

| Model | Solver Status | Model Status | Iterations | Residual |
|-------|-------------|-------------|------------|----------|
| chain | Normal Completion | Locally Infeasible | 340 | 7.079 |
| rocket | Normal Completion | Locally Infeasible | 6,287 | 1.309 |

**Fix approach:** These may have KKT formulation issues (incorrect stationarity) or may genuinely have no feasible complementarity solution near the default starting point. Investigation needed:
- chain: A catenary chain model — check if constraint Jacobian is correct
- rocket: Complex model (8 vars, 6 eqs) — 6,287 iterations suggests PATH tried hard; may be a genuine non-convexity issue

**Priority:** LOW — locally infeasible is a meaningful solver result that may indicate formulation issues rather than solver configuration.

---

## 3. Root Cause Distribution

| Root Cause | Count | % of 29 | Actionable? |
|-----------|-------|---------|-------------|
| Fixed by Sprint 21 improvements | 14 | 48% | Already done |
| Starting point / domain errors | 5 | 17% | YES — `.l` initialization improvement |
| MCP pairing bugs | 4 | 14% | YES — KKT builder fixes |
| Compilation errors | 2 | 7% | YES — emitter fixes |
| Translation timeout | 2 | 7% | Optimization needed |
| Locally infeasible | 2 | 7% | Investigation needed |

---

## 4. PATH Options Testing

**Not applicable for 13 of 15 models.** Categories B–E (13 models) never reach the PATH solver — failures occur during GAMS equation generation (B), model construction validation (C), compilation (D), or translation (E). Relaxing `convergence_tolerance` or increasing `major_iteration_limit` cannot help because PATH is never invoked.

The 2 Category F models (chain, rocket) do reach PATH and terminate with Normal Completion — but with "Locally Infeasible" model status, not a convergence failure. PATH completed its algorithm; it simply found no feasible solution. Relaxed tolerances would not change the outcome since PATH already ran to completion.

---

## 5. Recommended Actions

### Sprint 21 (remaining days)

1. **Add `option domlim = 100;`** to emitted MCP files — allows GAMS to continue past domain evaluation errors, potentially enabling PATH to run with approximate equation values. This could unblock Category B models (5 models) with minimal code change.

### Sprint 22

| Priority | Action | Models | Effort |
|----------|--------|--------|--------|
| 1 | `.l` initialization from NLP solution values | cclinpts, elec, etamac, hs62, lands | 3-4h |
| 2 | Fix MCP pairing for fixed-value variables | hhfair, pak | 2-3h |
| 3 | Fix variable/equation count mismatch | fdesign, trussm | 2-3h |
| 4 | Fix compilation errors (missing data) | camshape, qsambal | 2h |
| 5 | Translation timeout optimization | ganges, gangesx | 4-6h |
| 6 | Investigate locally infeasible models | chain, rocket | 2-3h |

**Projected impact:** Fixing priorities 1-4 could unblock 13 of the 15 failing models, adding up to 13 new solve attempts. Combined with the 14 already solving, this would reduce `path_solve_terminated` from 29 to ~2 models.

---

## 6. Methodology

### Data Collection
- **Pipeline runs:** `python scripts/gamslib/run_full_test.py --model NAME --verbose` for each of the 29 models
- **Direct GAMS execution:** `gams data/gamslib/mcp/NAME_mcp.gms o=NAME.lst lo=3` to examine listing file errors
- **Database query:** `data/gamslib/gamslib_status.json` for stored solve results

### Classification Criteria
- **Category A (Now solves):** Pipeline reports `[SOLVE] SUCCESS` with objective value
- **Category B (Execution error):** GAMS listing shows `Exec Error` during equation generation
- **Category C (MCP pairing):** GAMS listing shows `Unmatched` or `MCP pair has unmatched` errors
- **Category D (Compilation error):** GAMS listing shows `$NNN` compilation errors
- **Category E (Translation timeout):** Pipeline reports `[TRANSLATE] FAILURE: timeout`
- **Category F (Locally infeasible):** GAMS solver status = 1 (Normal Completion), model status = 5 (Locally Infeasible)

### Important Note on Database vs. Pipeline Discrepancy
The `gamslib_status.json` database records from `test_solve.py` reflect the **on-disk MCP files** (generated at various points during Sprint 21). The `run_full_test.py` pipeline **re-generates MCP files** from the current source code before solving. Sprint 21 code improvements (semantic errors, macro expansion, internal_error fixes, path_syntax_error reductions, match improvements, deferred issues, libInclude stripping) mean the pipeline produces different (often better) MCP files than those stored on disk. The 14 "now solves" models reflect these cumulative improvements.
