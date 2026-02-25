# Camcge: Subset-Qualified Assignment Emitted as Inline Data + Parameter Ordering

**GitHub Issue:** [#860](https://github.com/jeffreyhorn/nlp2mcp/issues/860)
**Status:** RESOLVED
**Severity:** Medium — Model translates but GAMS compilation fails (path_syntax_error)
**Date:** 2026-02-24
**Resolved:** 2026-02-24
**Affected Models:** camcge

---

## Problem Summary

The camcge model parses and translates to MCP, but the emitted GAMS code fails compilation
with 15 errors. Two distinct emitter bugs are present: (1) subset-qualified parameter
assignments are incorrectly emitted as inline data blocks, and (2) parameter assignment
statements are emitted in the wrong order, causing references to undefined values.

---

## Resolution

Three fixes were applied:

### Fix 1: Subset-qualified value detection (`emit_original_parameters`)

In `emit_original_parameters()`, added logic to detect when a parameter value key element
is a set/alias name (not an element literal). These entries are skipped from inline data
emission and instead handled by a new `emit_subset_value_assignments()` function that
emits them as executable assignment statements after set assignments.

### Fix 2: Topological sort for regular computed parameters

Extended the existing `_topological_sort_params()` helper (originally only for calibration
params) to also sort regular computed parameters in the `"no_varref_attr"` pass. This
ensures parameters like `rhoc`/`rhot` are emitted before `delta` which depends on them.

### Fix 3: Early computed parameter emission for set assignment dependencies

Added `compute_set_assignment_param_deps()` to identify the transitive closure of computed
parameters referenced by set assignments. These are emitted BEFORE set assignments in
`emit_gams.py`, breaking the circular dependency where set assignments like
`it(i) = 1$m0(i)` need `m0(i) = zz("m0",i)` (which only depends on inline data).

### Result

- camcge: 0 compilation errors (was 15), progresses to solve stage
- Solver stage has execution errors (division by zero) due to variable initialization,
  which is a separate issue unrelated to the emitter bugs fixed here
- All 3744 tests pass

---

## Files Changed

| File | Change |
|------|--------|
| `src/emit/original_symbols.py` | Added subset value detection, `emit_subset_value_assignments()`, `_topological_sort_params()` helper, `compute_set_assignment_param_deps()`, `only_params`/`exclude_params` params on `emit_computed_parameter_assignments()` |
| `src/emit/emit_gams.py` | Early computed param emission before set assignments, exclude from later pass |

---

## Related Issues

- Sprint 21 SEMANTIC_ERROR_AUDIT section 2.1 documents the original parse blocker (`sign()`)
