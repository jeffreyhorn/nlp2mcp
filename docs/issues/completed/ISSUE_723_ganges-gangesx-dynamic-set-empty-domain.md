# Validation: Dynamic Set `ie` Has No Members at Equation Instantiation (ganges, gangesx)

**GitHub Issue:** [#723](https://github.com/jeffreyhorn/nlp2mcp/issues/723)
**Status:** Fixed
**Severity:** High — Blocks translation of ganges and gangesx models; equations using `ie` domain produce no instances
**Discovered:** 2026-02-13 (Sprint 19, after Issues #714 and #719 fixed conflicting bounds and circular dependency)
**Fixed:** 2026-02-14
**Affected Models:** ganges, gangesx (and any model using dynamic subsets populated via `set(i) = yes$condition`)

---

## Problem Summary

The ganges and gangesx models define dynamic subsets (e.g., `ie(i)`) that are populated at execution time via conditional assignments like `ie(i) = yes$(...)`. The pipeline could not statically resolve the members of these subsets, causing equation instantiation to fail with "uses domain set 'ie' which has no members."

---

## Fix

### Parent set fallback in `resolve_set_members()` (`src/ad/index_mapping.py`)

When a set has no static members but has a declared parent domain (e.g., `ie(i)` with `domain=('i',)`), the function now falls back to the parent set's members. This is correct because:

1. The dynamic set assignment (e.g., `ie(i) = yes$(...)`) is already stored in `ModelIR.set_assignments` and emitted in the generated GAMS code BEFORE equations are defined
2. GAMS will evaluate the set assignment at runtime to determine the actual subset membership
3. Using the parent set for instantiation is conservative — it may generate more equation instances than needed, but the dollar condition on the equation definition (or the set assignment) filters inactive instances at runtime

The function logs a warning when falling back, e.g.:
```
WARNING  Dynamic subset 'ie' has no static members; falling back to parent set 'i' (6 members)
```

### Remaining blocker (separate issue)

After this fix, both ganges and gangesx advance further in the pipeline but encounter a new error:
```
Error: Invalid model - gamma() expects 1 argument, got 2
```
This is a naming collision where the model's parameter `gamma(i,t)` shadows the GAMS built-in `gamma()` math function (which takes 1 argument). This is a separate, pre-existing issue.

### Results

- The "Equation 'export' uses domain set 'ie' which has no members" error is resolved
- Both ganges and gangesx models progress past the dynamic set issue
- All quality gates pass (typecheck, lint, format, 3315 tests)
