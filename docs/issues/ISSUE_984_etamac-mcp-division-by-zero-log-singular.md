# etamac: MCP Execution Error — Division by Zero + log(0) Singular

**GitHub Issue:** [#984](https://github.com/jeffreyhorn/nlp2mcp/issues/984)
**Status:** PARTIALLY FIXED
**Severity:** Medium — Model translates but PATH solver never runs (path_solve_terminated)
**Date:** 2026-03-03
**Fixed:** 2026-03-03 (domain errors resolved; MCP matching errors remain)
**Affected Models:** etamac

---

## Problem Summary

The etamac model (energy-technology-aggregate-climate model) parses and translates to MCP successfully, but GAMS aborts during equation generation with `division by zero (0)` and `log: FUNC SINGULAR: x = 0`. The consumption variable `c(t)` appears in `1/c(t)` gradient terms and `log(c(t))` terms. The `.l` initialization `c.l(t) = c0 * l(t)` evaluates to 0 for non-first time periods because `l(t)` is only computed for `tfirst`.

---

## Fix

Added `.l` clamping to `.lo` bounds in `src/emit/emit_gams.py` for variables with expression-based `.l` assignments (Priority 1b). After the `.l` expression is emitted, a `max(.l, lo)` clamping line is added for variables that have declared lower bounds.

For etamac: `c.l(t) = c0 * l(t)` followed by `c.l(t) = max(c.l(t), 3.2)` ensures `c(t) >= 3.2` during equation generation.

**Result:** Domain errors reduced from 20 to 0. However, 8 MCP matching errors remain (`totalcap.nu_totalcap has unmatched equation`) which are a separate issue related to equation conditioning vs. variable fixing. The model still fails to solve.

---

## Remaining Issue

The 8 `MCP pair totalcap.nu_totalcap has unmatched equation` errors indicate that the `totalcap` equation is conditioned on a subset of `t`, but the variable `nu_totalcap` is not properly fixed for excluded instances. This is a separate MCP matching issue, not related to domain errors.

---

## Files Changed

- `src/emit/emit_gams.py` — Added `.l` clamping to `.lo` after expression-based `.l` assignments
