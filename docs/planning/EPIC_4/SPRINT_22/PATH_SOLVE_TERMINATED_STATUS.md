# path_solve_terminated Status Update (Sprint 22 Prep Task 3)

**Created:** 2026-03-06
**Sprint:** 22 (Prep Task 3)
**Status:** Complete — ready for Sprint 22 fix design (Task 7)
**Data Source:** `data/gamslib/gamslib_status.json` (updated_date=2026-02-12, GAMS 51.3.0; Sprint 21 Day 12 pipeline run)
**Error verification:** GAMS v53 (`/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams`) on on-disk MCP files

---

## 1. Executive Summary

The path_solve_terminated category currently contains **12 models** (down from 29 at Sprint 21 baseline). Since the Sprint 21 baseline, **22 unique models have moved out of this category** (14 to model_optimal / Category A and 8 to other categories), while 5 models have entered from path_syntax_error or as newly-translating models, yielding the net −17 change.

Sprint 22 targets path_solve_terminated **≤ 5** (−7 models). Analysis shows the 12 models break into two dominant failure modes:

| Error Type | Count | Models | Fix Approach |
|-----------|-------|--------|-------------|
| **MCP pairing errors** | 8 | etamac, fdesign, hhfair, otpop, pak, pindyck, springchain, trussm | KKT builder / emitter fixes |
| **Execution errors** | 4 | elec, fawley, lands, tforss | Domain guards, `$` condition preservation, parameter resolution |

**Key finding:** All 12 models fail **before PATH runs** — none have PATH convergence issues. The `path_solve_terminated` classification is a misnomer; the true errors are in GAMS equation generation or model construction. This confirms the Sprint 21 Day 12 analysis finding.

**Sprint 22 target is achievable:** Fixing the `_fx_` equation suppression bug alone would resolve 5 models (etamac, hhfair, otpop, pak, pindyck). Adding fdesign/trussm (unmatched variable) fixes gets to 7, meeting the −7 target without touching execution-error models.

### Key Changes from Sprint 21

| Category | Sprint 21 | Current | Delta | Notes |
|----------|-----------|---------|-------|-------|
| A: Now solves | 14 | — | — | Already solved; removed from category |
| B: Execution error | 5 | 4 | −1 | cclinpts→model_optimal, hs62→model_optimal; +fawley, +tforss new |
| C: MCP pairing | 4 | 8 | +4 | etamac reclassified from B; +otpop, +pindyck, +springchain new |
| D: Compilation error | 2 | 0 | −2 | camshape→path_syntax_error, qsambal→path_syntax_error |
| E: Translation timeout | 2 | 0 | −2 | ganges/gangesx no longer in pipeline (N/A) |
| F: Locally infeasible | 2 | 0 | −2 | chain→model_infeasible, rocket→model_infeasible |
| **Total** | **29** | **12** | **−17** | |

### Model Movement

**Moved OUT (22 unique models; net −17 vs Sprint 21 baseline):**
- **Category A → model_optimal (14):** decomp, jobt, like, polygon, ps2_f, ps2_f_s, ps2_s, ps3_f, ps3_s, ps3_s_gic, ps3_s_mn, ps3_s_scp, ps10_s, solveopt
- **Category B → model_optimal (2):** cclinpts, hs62
- **Category D → path_syntax_error (2):** camshape, qsambal
- **Category E → N/A (2):** ganges, gangesx (not in pipeline)
- **Category F → model_infeasible (2):** chain, rocket

Note: The bullets above list **22 unique models** moved out of `path_solve_terminated` (14 + 2 + 2 + 2 + 2). In the summary table this appears as a **net −17** change because **5 new models** entered the category after the Sprint 21 baseline (see "Moved IN" below).

**Moved IN (5 models):**

| Model | Previous Status | Current Error | Category |
|-------|----------------|---------------|----------|
| fawley | path_syntax_error (B) | Execution: division by zero | B (new) |
| otpop | path_syntax_error (A) | MCP pairing: 9 unmatched `_fx_` eqs | C (new) |
| pindyck | newly translating | MCP pairing: 3 unmatched `_fx_` eqs | C (new) |
| springchain | newly translating | MCP pairing: stationarity domain mismatch | C (new) |
| tforss | path_syntax_error (A) | Execution: 152 NA errors from `rho /na/` | B (new) |

---

## 2. Per-Model Classification (All 12 Models)

### 2.1 Category B: Execution Errors (4 models)

PATH never runs. GAMS aborts during equation generation due to mathematical domain errors or NA values.

#### elec — Division by Zero (Self-Pair Distance)

**Error:** `Exec Error at line 90/91: division by zero (0)` (4 errors)
**Equations:** `stat_x(i1..i10)`, `stat_y(i1..i8+)`
**Root Cause:** The original model uses `ut(i,j)$(ord(j) > ord(i))` to create an upper-triangular filter excluding self-pairs. The MCP conversion lost this filter entirely — `ut` is set to the full Cartesian product and summations use `sum((i,j), ...)` instead of `sum(ut(i,j), ...)`. When `i == j`, `distance = 0` and `1/distance` causes division by zero.
**Issue doc:** #983 (`docs/issues/ISSUE_983_elec-mcp-division-by-zero-distance.md`)
**Fix:** Restore `ut` conditional domain in emitted MCP summations.
**Effort:** 2-3h (requires parser/IR enrichment to preserve set-filtered domains)

#### fawley — Division by Zero (Dropped Dollar Conditions)

**Error:** `Exec Error at line 74/75: division by zero (0)` (2 errors)
**Equations:** Parameter initialization lines (not stationarity)
**Root Cause:** The original model has `char(c,"volume")$prop(c,"gravity") = 1/prop(c,"gravity")` and `bp(k,p)$kuse(k,p) = 1/sum(...)`. The MCP conversion dropped the `$` conditions on parameter assignment LHS, causing `1/prop(c,"gravity")` to evaluate when `gravity = 0` for 7 components (vacuum-res, res-arab-l, etc.) and `bp` to evaluate when the denominator sum is zero.
**Issue doc:** None
**Fix:** Preserve `$` conditions on parameter assignment statements during MCP conversion.
**Effort:** 1-2h (emitter fix to carry through dollar conditions)

#### lands — NA in Equation RHS

**Error:** `RHS value NA in equation comp_dembal(mode-1)` (1 error)
**Equations:** `comp_dembal(mode-1)`
**Root Cause:** Parameter `d("mode-1")` is intentionally `NA` — in the original model, it is assigned dynamically in a `loop` before each `solve`. The MCP conversion extracts the model at a point where `d("mode-1")` still has its initial `NA` value. The equation `comp_dembal` references `d` without a dollar condition to filter the NA element.
**Issue doc:** #986 (`docs/issues/ISSUE_986_lands-mcp-rhs-na-equation.md`)
**Fix:** Either resolve loop-dependent parameter values at solve-time, or auto-add `$(param <> na)` conditions.
**Effort:** 2-3h (general capability for loop-dependent parameter resolution)

#### tforss — Massive NA Propagation

**Error:** 152 errors — `Matrix error - coefficient in variable below is NA` across `stat_h`, `stat_v`, `ainvc`, `aplnt` equations
**Equations:** Nearly all stationarity and constraint equations
**Root Cause:** Scalar `rho` is declared as `rho /na/` in the MCP file. In the original model, `rho` is assigned inside a `loop(rhoset, rho = rhoval(rhoset); solve forest ...)` — the MCP conversion captured `rho` at declaration time (`na`) rather than at solve time. Every expression containing `rho` evaluates to `NA`, propagating into 152 matrix coefficients.
**Issue doc:** None
**Fix:** Same pattern as lands — resolve loop-dependent parameters at solve-time.
**Effort:** Shares fix with lands (0h incremental once lands fix exists)

**Category B Summary:**

| Model | Error Type | Errors | Root Cause | Fix Approach | Effort |
|-------|-----------|--------|-----------|-------------|--------|
| elec | Division by zero | 4 | Lost `ut` self-pair filter | Restore conditional domain | 2-3h |
| fawley | Division by zero | 2 | Dropped `$` on assignments | Preserve `$` conditions | 1-2h |
| lands | NA in RHS | 1 | Loop-dependent `d("mode-1")` | Resolve params at solve-time | 2-3h |
| tforss | NA propagation | 152 | Loop-dependent `rho /na/` | Same as lands | 0h (shared) |

---

### 2.2 Category C: MCP Pairing Errors (8 models)

The emitted MCP file has structural errors — variable-equation count mismatch or invalid MCP pair references. PATH never runs.

#### Sub-pattern C1: Unmatched `_fx_` Equations (4 models)

**Error pattern:** `MCP pair XXX_fx_NNN.nu_XXX_fx_NNN has unmatched equation`
**Root Cause:** The KKT builder emits `_fx_` (fix-value) equations for variables that GAMS has already eliminated via `.fx` assignments or domain-exclusion logic. When GAMS sees `x.fx(t) = val`, it removes `x(t)` from the model. But the `x_fx_t` equation still references `x(t)` — since the variable is eliminated, the equation has no matching free variable.

| Model | Errors | Specific Pairs | Fix |
|-------|--------|---------------|-----|
| hhfair | 2 | `a_fx_0.nu_a_fx_0`, `m_fx_0.nu_m_fx_0` | Suppress `_fx_` for `.fx`'d vars |
| otpop | 9 | `x_fx_1965..x_fx_1973` (years outside optimization set `t`) | Suppress `_fx_` for domain-excluded vars |
| pak | 4 | `comp_conl.lam_conl`, `c_fx_1962`, `ks_fx_1962_*` | Suppress `_fx_` for `.fx`'d vars |
| pindyck | 3 | `r_fx_1974`, `s_fx_1974`, `td_fx_1974` | Suppress `_fx_` for domain-excluded vars |

**Fix:** Domain-aware `_fx_` equation suppression — do not emit `_fx_` equations (or include them in the model statement) for indices where the variable is already `.fx`'d by direct assignment or domain-exclusion logic.
**Effort:** 2-3h (systematic fix in KKT builder/emitter)

#### Sub-pattern C2: Unmatched Free Variables (2 models)

**Error pattern:** `Unmatched single free variables: 1`
**Root Cause:** A free variable is included in the model statement but has no matching stationarity equation.

| Model | Errors | Unmatched Variable | Likely Cause |
|-------|--------|-------------------|-------------|
| fdesign | 1 | `t` | Missing stationarity for objective-related variable |
| trussm | 1 | `tau` | Missing stationarity for objective-related variable |

**Fix:** Ensure all free variables in the model statement have corresponding stationarity equations, or remove variables that should be fixed.
**Effort:** 2h (investigate and fix KKT builder variable-equation matching)

#### Sub-pattern C3: Stationarity Domain Mismatch (1 model)

**Error pattern:** `MCP pair stat_delta_x.delta_x has unmatched equation`

| Model | Errors | Specific Error |
|-------|--------|---------------|
| springchain | 2 | `stat_delta_x(n0)` and `stat_delta_y(n0)` — stationarity generated over all `n` but constraint only exists for `ord(n) > 1` |

**Root Cause:** The constraint equations `delta_x_eq(n)$(ord(n) > 1)` and `delta_y_eq(n)$(ord(n) > 1)` only exist for `n` where `ord(n) > 1`. The stationarity equations are generated for ALL `n` including `n0`. At `n0`, `stat_delta_x(n0)` reduces to trivially `nu = 0` with no `delta_x(n0)` term — the variable has no non-zero coefficient, so GAMS cannot match the equation to the variable.
**Fix:** Domain-conditional stationarity — generate stationarity equations only for domains matching the original constraint's conditional domain.
**Effort:** 1-2h (related to Subcategory C in path_syntax_error — same domain propagation issue)

#### Sub-pattern C4: MCP Pairing with Reclassified Error (1 model)

| Model | Errors | Specific Error |
|-------|--------|---------------|
| etamac | 8 | `MCP pair totalcap.nu_totalcap has unmatched equation` for 8 time periods |

**Root Cause:** etamac was originally Category B (execution error: division by zero + log(0)). Sprint 21 added `.l` clamping to `.lo` bounds in `src/emit/emit_gams.py`, which resolved the 20 domain errors. However, this revealed 8 MCP pairing errors that were masked before. The `totalcap` equation is emitted for all time periods but some periods have the variable fixed.
**Issue:** #984 (internal tracking doc — partially, notes the 8 remaining matching errors after `.l` fix)
**Fix:** Same `_fx_` suppression fix as C1.
**Effort:** 0h (shared with C1 fix)

**Category C Summary:**

| Sub-pattern | Models | Errors | Fix | Effort |
|------------|--------|--------|-----|--------|
| C1: Unmatched `_fx_` equations | hhfair, otpop, pak, pindyck | 2-9 each | `_fx_` suppression | 2-3h |
| C2: Unmatched free variable | fdesign, trussm | 1 each | KKT variable-equation matching | 2h |
| C3: Stationarity domain mismatch | springchain | 2 | Domain-conditional stationarity | 1-2h |
| C4: MCP pairing (reclassified) | etamac | 8 | Shared with C1 | 0h |

---

## 3. Fix Batches for Sprint 22

Sprint 22 target: path_solve_terminated **≤ 5** (need to fix **≥ 7** models from 12)

| Priority | Fix | Models | Effort | Cumulative Fixed | Rationale |
|----------|-----|--------|--------|-----------------|-----------|
| 1 | `_fx_` equation suppression | etamac, hhfair, otpop, pak, pindyck | 2-3h | 5 | Single fix unblocks 5 models; highest leverage |
| 2 | Unmatched free variable fix | fdesign, trussm | 2h | 7 | **Meets −7 target** |
| 3 | `$` condition preservation | fawley | 1-2h | 8 | Quick emitter fix |
| 4 | Stationarity domain conditioning | springchain | 1-2h | 9 | Related to path_syntax_error Subcategory C |
| 5 | Loop-dependent parameter resolution | lands, tforss | 2-3h | 11 | General capability; helps future models too |
| 6 | Conditional domain restoration (elec) | elec | 2-3h | 12 | Requires parser/IR enrichment |

**Total estimated effort: 10-15h** (for all 12 models)

### Recommended Sprint 22 Approach

**Minimum viable (−7 models, hitting ≤5 target):**
- Fix `_fx_` equation suppression (5 models, 2-3h)
- Fix unmatched free variables (2 models, 2h)
- Total: 7 models, 4-5h

**Recommended scope (−9 models):**
1. `_fx_` equation suppression (5 models, 2-3h)
2. Unmatched free variable (2 models, 2h)
3. `$` condition preservation for fawley (1 model, 1-2h)
4. Stationarity domain conditioning for springchain (1 model, 1-2h)
- Total: 9 models → path_solve_terminated = 3, 6-9h

**Stretch goal (all 12 models):**
Add loop-dependent parameter resolution (lands, tforss) and elec conditional domain restoration.
- Total: 12 models → path_solve_terminated = 0, 10-15h

---

## 4. Cross-References to Existing Issue Documents

| Model | Issue | Status | Notes |
|-------|-------|--------|-------|
| elec | #983 | Open | Division by zero from lost `ut` self-pair filter |
| etamac | #984 | Partially fixed | `.l` clamping resolved domain errors; 8 MCP pairing errors remain |
| lands | #986 | Open | NA parameter from loop-dependent assignment |

**Models without issue documents:** fawley, fdesign, hhfair, otpop, pak, pindyck, springchain, tforss, trussm (9 models — create issues during Sprint 22 execution as needed)

---

## 5. KU Verification Summary

| KU | Status | Finding |
|----|--------|---------|
| KU-05 | **PARTIALLY REFUTED** | Only 2 of the original 5 Category B models (elec, lands) remain in path_solve_terminated. cclinpts and hs62 now solve (model_optimal). etamac shifted to Category C (MCP pairing) after `.l` fix. The "all fixable through `.l` initialization" assumption was partially correct — `.l` clamping helped etamac but didn't fully resolve it. The remaining 4 execution-error models (elec, fawley, lands, tforss) have diverse root causes: conditional domain loss, `$` condition dropping, loop-dependent parameters — not just `.l` initialization. |
| KU-06 | **REFUTED** | `option domlim = 100;` does NOT help any of the 5 tested models (elec, etamac, fawley, lands, tforss). `domlim` controls domain violation tolerance during the solve phase (within PATH), but all models abort before the solve is submitted — errors occur during GAMS equation generation/evaluation or model matrix construction, prior to solver invocation. |
| KU-09 | **CONFIRMED (moved)** | chain and rocket are no longer classified as path_solve_terminated — they are now model_infeasible in the pipeline. This confirms they are genuinely locally infeasible (PATH ran to completion with Normal Completion status). They are excluded from path_solve_terminated fix targets and should be addressed as part of model_infeasible triage (Task 4). |
| KU-10 | **CONFIRMED + EXPANDED** | The original 4 Category C models (fdesign, trussm, hhfair, pak) still have MCP pairing errors. Additionally, 4 new models (etamac, otpop, pindyck, springchain) also have MCP pairing errors — expanding Category C from 4 to 8 models. The dominant sub-pattern is `_fx_` equation suppression (5 models), confirming the KKT builder bug hypothesis. fdesign/trussm are unmatched free variables (different sub-pattern). springchain is a stationarity domain mismatch. |
| KU-25 | **CONFIRMED** | The original elec model uses `ut(i,j)$(ord(j) > ord(i))` for upper-triangular self-pair exclusion. The MCP conversion lost this filter entirely: `ut` is set to the full Cartesian product and summations use `sum((i,j), ...)` instead of `sum(ut(i,j), ...)`. This causes division by zero for all 25 self-pairs. Fix requires parser/IR enrichment to preserve set-filtered domains through differentiation — estimated 2-3h, not the 1h originally assumed. |

---

## 6. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `_fx_` suppression fix has edge cases | Medium | Medium | Test on all 5 affected models; regression on currently-solving models |
| fdesign/trussm fix harder than estimated | Low | Low | Only 2 models; can defer to stretch |
| Loop-dependent parameter resolution is complex | Medium | Medium | Affects only 2 models (lands, tforss); general capability value |
| New models enter path_solve_terminated from path_syntax_error fixes | Medium | Low | Sprint 22 path_syntax_error fixes may unmask execution/pairing errors |
| springchain domain fix conflicts with path_syntax_error Subcat C fix | Low | Low | Same root cause (domain propagation) — likely shared solution |

---

## 7. Per-Model Summary Table

| Model | Error Type | Errors | Sprint 21 Cat | Movement | Fix Batch | Root Cause | Effort |
|-------|-----------|--------|--------------|----------|-----------|------------|--------|
| elec | Div by zero | 4 | B | Stayed | 6 | Lost `ut` self-pair filter | 2-3h |
| etamac | MCP pairing | 8 | B→C | Reclassified | 1 | `_fx_` for `.fx`'d vars | 0h (shared) |
| fawley | Div by zero | 2 | — | New (from path_syntax_error) | 3 | Dropped `$` on assignments | 1-2h |
| fdesign | MCP pairing | 1 | C | Stayed | 2 | Unmatched free var `t` | 2h (shared) |
| hhfair | MCP pairing | 2 | C | Stayed | 1 | `_fx_` for `.fx`'d vars | 0h (shared) |
| lands | NA in RHS | 1 | B | Stayed | 5 | Loop-dependent param NA | 2-3h |
| otpop | MCP pairing | 9 | — | New (from path_syntax_error) | 1 | `_fx_` for domain-excluded vars | 0h (shared) |
| pak | MCP pairing | 4 | C | Stayed | 1 | `_fx_` + comp pairing | 0h (shared) |
| pindyck | MCP pairing | 3 | — | New | 1 | `_fx_` for domain-excluded vars | 0h (shared) |
| springchain | MCP pairing | 2 | — | New | 4 | Stationarity domain mismatch | 1-2h |
| tforss | NA propagation | 152 | — | New (from path_syntax_error) | 5 | Loop-dependent `rho /na/` | 0h (shared) |
| trussm | MCP pairing | 1 | C | Stayed | 2 | Unmatched free var `tau` | 0h (shared) |

---

## 8. Notes

- **GAMS version:** Pipeline data from `gamslib_status.json` uses GAMS 51.3.0. Manual error classification (GAMS compilation of MCP files) used GAMS v53. Error types are consistent across both versions.
- **etamac reclassification:** Sprint 21 `.l` clamping fix (PR #984) resolved etamac's 20 division-by-zero/log(0) errors but revealed 8 MCP pairing errors that were masked before. etamac is now Category C, not B.
- **chain and rocket:** Moved to model_infeasible in the pipeline. They are genuinely locally infeasible (PATH ran to completion) and should be addressed in Task 4 (model_infeasible triage), not here.
- **ganges and gangesx:** No longer appear in the pipeline (translate_failure / N/A). Translation timeout models are handled separately.
- **camshape and qsambal:** Moved to path_syntax_error. Their compilation errors ($141) are handled in Task 2's Subcategory A classification.
- **Overlap with path_syntax_error fixes:** springchain's stationarity domain mismatch shares the same root cause as path_syntax_error Subcategory C (10 models). A single domain propagation fix could address both categories simultaneously.

---

**Document Created:** 2026-03-06
**Next Steps:** Use this classification for Task 7 (Fix Design) and Task 10 (Sprint 22 Detailed Schedule)
