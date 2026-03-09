# cesam2: GAMS Error 187 — Assigned Set Used as Domain

**GitHub Issue:** [#1022](https://github.com/jeffreyhorn/nlp2mcp/issues/1022)
**Status:** FIXED
**Severity:** High — 14 compilation errors block solve
**Date:** 2026-03-08
**Fixed:** 2026-03-09
**Affected Models:** cesam2

---

## Problem Summary

The cesam2 model (cross-entropy SAM estimation, variant 2) translates to MCP, but GAMS reports 14 compilation errors (Error $187: "Assigned set used as domain"). The set `ii(i)` is populated via executable assignment (`ii(i) = 1; ii("Total") = 0;`), and its alias `jj` is used as a domain index in MCP variable and equation declarations. GAMS requires sets used as domains to be defined with static data, not dynamic assignments.

---

## Root Cause (Corrected)

The original issue doc suggested the parser wasn't capturing `ii`'s members. Investigation showed that `ii(i)` is actually declared **without** static data in the original GAMS file — it's purely a dynamic subset assigned via `ii(i) = yes; ii("Total") = no;`.

The existing `_build_dynamic_subset_map()` in `templates.py` (Issue #739) already handles remapping dynamic subsets to their parent sets in variable/equation declarations. It correctly maps `ii -> i`. However, it did **not** handle **aliases** of dynamic subsets. The alias `jj` (alias of `ii`) was NOT remapped, so declarations like `nu_COLSUM(jj)` still referenced the dynamic set `ii` through its alias, triggering Error $187.

---

## Fix

Extended `_build_dynamic_subset_map()` in `src/emit/templates.py` to also remap aliases of dynamic subsets. After building the initial dynamic map for sets, the function now iterates through `model_ir.aliases` and adds any alias whose target is already in the dynamic map. For example, if `ii -> i` is in the map and `jj` is an alias of `ii`, then `jj -> i` is also added.

**File changed:** `src/emit/templates.py` — `_build_dynamic_subset_map()`

**Result:** All 14 $187 errors eliminated. cesam2 now compiles with only 2 residual errors:
- $141: `wbar3` parameter declared but not assigned (pre-existing data emission issue)
- $257: Solve statement not checked due to $141

---

## Related Issues

- Issue #739: Original dynamic subset domain remapping
- Issue #881: cesam missing dollar conditions (sibling model, different error class)
- Issue #860: Set assignment parameter dependency ordering
