# etamac: MCP Execution Error — Division by Zero + log(0) Singular

**GitHub Issue:** [#984](https://github.com/jeffreyhorn/nlp2mcp/issues/984)
**Status:** FIXED
**Severity:** Medium — Model translates but PATH solver never runs (path_solve_terminated)
**Date:** 2026-03-03
**Fixed:** 2026-03-11 (domain errors resolved + MCP matching errors resolved)
**Affected Models:** etamac

---

## Problem Summary

The etamac model (energy-technology-aggregate-climate model) parses and translates to MCP successfully, but GAMS aborts during equation generation with `division by zero (0)` and `log: FUNC SINGULAR: x = 0`. The consumption variable `c(t)` appears in `1/c(t)` gradient terms and `log(c(t))` terms. The `.l` initialization `c.l(t) = c0 * l(t)` evaluates to 0 for non-first time periods because `l(t)` is only computed for `tfirst`.

---

## Fix (Phase 1: Domain Errors)

Added `.l` clamping to `.lo` bounds in `src/emit/emit_gams.py` for variables with expression-based `.l` assignments (Priority 1b). After the `.l` expression is emitted, a `max(.l, lo)` clamping line is added for variables that have declared lower bounds.

For etamac: `c.l(t) = c0 * l(t)` followed by `c.l(t) = max(c.l(t), 3.2)` ensures `c(t) >= 3.2` during equation generation.

**Result:** Domain errors reduced from 20 to 0.

## Fix (Phase 2: MCP Matching Errors)

The 8 `MCP pair totalcap.nu_totalcap has unmatched equation` errors were caused by incorrect subset condition detection in `_find_variable_subset_condition()` in `src/kkt/stationarity.py`. The function skipped `IndexOffset` accesses (e.g., `k(t+1)` in `totalcap`), causing it to falsely conclude that variable `k` was only used via subset `tlast`. This led to `stat_k(t)$(tlast(t))` instead of unconditional `stat_k(t)`, which in turn caused fix-inactive to eliminate `k` from `totalcap` equations.

Fixed by treating `IndexOffset` accesses as evidence of full-domain usage in `_find_variable_subset_condition()`.

**Result:** MCP matching errors reduced from 8 to 0. Model now reaches PATH solver.

## Remaining Issue

The model now reaches the PATH solver but reports **Locally Infeasible** (model status 5). This is a separate issue (#1045) related to incomplete stationarity equations for lead/lag variables — the Jacobian doesn't capture cross-period dependencies from `k(t+1)` in `totalcap`.

---

## Files Changed

- `src/emit/emit_gams.py` — Added `.l` clamping to `.lo` after expression-based `.l` assignments
- `src/kkt/stationarity.py` — Fixed IndexOffset handling in `_find_variable_subset_condition()`
