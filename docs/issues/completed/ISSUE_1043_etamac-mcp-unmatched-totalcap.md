# etamac: MCP Unmatched Equation — totalcap(t) Stationarity Domain Eliminates Primal Variable

**GitHub Issue:** [#1043](https://github.com/jeffreyhorn/nlp2mcp/issues/1043)
**Status:** FIXED
**Severity:** Medium — Model translates but PATH solver aborts (path_solve_terminated)
**Date:** 2026-03-10
**Fixed:** 2026-03-11
**Affected Models:** etamac

---

## Problem Summary

The etamac model (energy-technology-aggregate-climate) had 8 MCP pairing errors:

```
**** MCP pair totalcap.nu_totalcap has unmatched equation
     totalcap(1990) through totalcap(2025)
```

---

## Root Cause

The subset condition detection function `_find_variable_subset_condition()` in `src/kkt/stationarity.py` incorrectly restricted `stat_k` to `$(tlast(t))`. The bug was in the handling of `IndexOffset` accesses:

1. `k(t+1)` in the `totalcap` equation is an `IndexOffset` node
2. The function explicitly skipped `IndexOffset` accesses (line 361-362: `if not isinstance(actual_idx, str): continue`)
3. Without counting `k(t+1)` as evidence of full-domain usage, the function only saw `k(tlast)` in the `tc` constraint
4. It incorrectly concluded `k` was subset-restricted to `tlast`
5. This caused `stat_k(t)$(tlast(t))` instead of unconditional `stat_k(t)`
6. The fix-inactive section then emitted `k.fx(t)$(not (tlast(t))) = 0`
7. Fixing `k` to 0 for all non-terminal periods eliminated it from `totalcap`, causing 8 unmatched equations

---

## Fix

Modified `_find_variable_subset_condition()` in `src/kkt/stationarity.py` to treat `IndexOffset` accesses as evidence of full-domain usage. When a variable like `k(t)` is accessed via `k(t+1)` (an `IndexOffset` with base `t`), this means the variable is accessed across the range of the declared domain — which should prevent false subset conditions.

The fix resolves the base of the `IndexOffset` against the declared domain index. If they match, `pos_subsets[pos]` is set to `None` (full-domain evidence), preventing any subset condition from being applied at that position.

**Result:** `stat_k(t)` is now unconditional. No more `.fx` line for `k`. All 8 "unmatched equation" errors are gone.

---

## Files Changed

- `src/kkt/stationarity.py` — Fixed IndexOffset handling in `_find_variable_subset_condition()`
- `tests/unit/kkt/test_fix_inactive.py` — Added 4 unit tests for IndexOffset subset detection
