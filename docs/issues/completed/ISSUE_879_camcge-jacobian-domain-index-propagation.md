# camcge: Jacobian Domain Index Not Remapped in Stationarity Sums

**GitHub Issue:** [#879](https://github.com/jeffreyhorn/nlp2mcp/issues/879)
**Status:** FIXED
**Severity:** High — Model compiles but solver aborts with 1 execution error (division by zero)
**Date:** 2026-02-25
**Affected Models:** camcge

---

## Problem Summary

Jacobian derivative expressions from subset-restricted equations used the **outer stationarity
domain index** instead of the **inner sum index** for parameter references. For example,
`delta(i)` and `rhoc(i)` appeared instead of `delta(it)` and `rhoc(it)` inside
`sum(it, ...)` in stationarity equations.

---

## Root Cause

In `_replace_matching_indices()`, when `prefer_declared_domain=True` (for ParamRef), the
code used the parameter's declared domain target (e.g., `"i"` for `delta(i)`) without
consulting the constraint-specific `ChainMap` mapping that correctly maps element labels
to the sum index (e.g., `"light-ind" → "it"`).

The constraint element mapping (a `ChainMap` overlay) maps equation instance elements to
their constraint domain names. When processing `delta("light-ind")` inside `sum(it, ...)`,
the ChainMap correctly maps `"light-ind" → "it"`, but the `prefer_declared_domain` path
ignored this and used the declared domain `("i",)` instead.

---

## Fix Details

Added a new check in `_replace_matching_indices()` for the `prefer_declared_domain` path:
when `element_to_set` is a `ChainMap` (indicating Jacobian path with constraint-specific
overrides), and the element maps to a set that is a subset of the declared domain target,
use the subset mapping instead of the declared domain target.

### Files Changed

| File | Change |
|------|--------|
| `src/kkt/stationarity.py` | Added Issue #879 check in `_replace_matching_indices()`: when ChainMap maps element to a subset of declared domain target, use subset index |

### Result
- camcge: **0 compilation errors**, **0 execution errors from Jacobian indices** (was 1 division by zero)
- Remaining MCP pairing errors (12 "unmatched equation") are pre-existing issues related to variable fixing and equation domain conditioning, not Jacobian index mapping
- All 3783 tests pass
