# trnspwl: ord() on dynamic set ($197) + unquoted element labels ($120/$149)

**GitHub Issue:** [#949](https://github.com/jeffreyhorn/nlp2mcp/issues/949)
**Model:** trnspwl (GAMSlib SEQ=385)
**Status:** FIXED
**Error category:** `gams_compilation_error`
**Severity:** Medium — model parses and translates but GAMS compilation fails (59 errors)
**Fixed:** 2026-03-10

---

## Problem Summary

The trnspwl MCP output had two classes of GAMS compilation errors:

1. **`$197` — `ord()` on dynamic set `ss`**: The original GAMS uses `ss.off` where `ss(s)` is a subset (dynamic set). Previously translated to `ord(ss) - 1`, which GAMS rejects on dynamic sets.

2. **`$120/$149/$340` — Unquoted element labels in per-instance assignments**: The emitter generated `nseg(slope0) = p(s+1) - p(s);` instead of a single indexed assignment `nseg(s) = p(s+1) - p(s);`. This was caused by incorrect per-element expansion of subset-indexed assignments.

---

## Root Cause

### Issue 1: ord() on dynamic set
**Already fixed** (prior to this issue) via the `SetAttrRef` IR node. The parser now creates `SetAttrRef(name="ss", attribute="off")` and the emitter outputs `ss.off` directly — no `ord()` translation.

### Issue 2: Incorrect per-element expansion of subset-indexed assignments
The original GAMS `nseg(g(s)) = p(s+1) - p(s)` uses subset notation where `g(s)` means "for all `s` in `g`". The parser's `_handle_assign()` unconditionally expanded this into per-element assignments (one for each member of `g`), losing the running index `s`:

```
nseg('slope0') = p(s+1) - p(s);   # s is unbound — invalid
nseg('s1')     = p(s+1) - p(s);   # s is unbound — invalid
...
```

The expansion should only happen for **constant value** assignments (e.g., `dist(arc(n,np)) = 100`), not for expression-based assignments where the RHS references the running index.

---

## Fix

**File:** `src/ir/parser.py` — `_handle_assign()` method

Added a guard to the subset-indexed expansion at the `if subset_name is not None` branch: only call `_expand_subset_assignment()` when `value is not None and not has_function_call`. For expressions, the code falls through to store a single indexed assignment with the domain variable preserved.

**Before:** `nseg(g(s)) = p(s+1) - p(s)` → 7 per-element assignments with unbound `s`
**After:** `nseg(g(s)) = p(s+1) - p(s)` → single `nseg(s) = p(s+1) - p(s);`

**File:** `src/emit/original_symbols.py`

Also added `domain_lower` parameter to `_quote_assignment_index()` calls in both `emit_computed_parameter_assignments()` and `emit_interleaved_params_and_sets()`. This ensures that any remaining per-element assignments from constant-value subset expansion properly quote element labels.

---

## Remaining: Error 65 (discrete variables)

The model still fails GAMS compilation with Error 65 ("discrete variable not allowed") because trnspwl uses SOS2 variables (`xs`, `gs`), which are discrete/special-ordered-set variables not supported in MCP reformulation. This is an inherent model type limitation, not a translation bug.

---

## Affected Files

| File | Change |
|------|--------|
| `src/ir/parser.py` | Guard subset expansion: only expand for constant values, not expressions |
| `src/emit/original_symbols.py` | Pass `domain_lower` to `_quote_assignment_index` for proper element quoting |
