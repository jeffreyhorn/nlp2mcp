# Chenery MCP: Division By Zero From Uninitialized Calibration Parameters

**GitHub Issue:** [#763](https://github.com/jeffreyhorn/nlp2mcp/issues/763)
**Status:** FIXED
**Severity:** High — MCP generates but GAMS aborts with EXECERROR = 1 (division by zero)
**Date:** 2026-02-16
**Fixed:** 2026-02-21
**Affected Models:** chenery

---

## Problem Summary

The chenery model (`data/gamslib/raw/chenery.gms`) generates an MCP file, but GAMS
aborts during execution with division by zero errors. Two root causes were identified:

1. **Calibration parameter ordering**: `rva = cva / cli` was emitted before `cva` and
   `cli` were computed, causing division by zero from uninitialized `cli = 0`.
2. **Variable `.l` initialization ordering**: `.l` expressions with cross-variable
   dependencies (e.g., `l.l(i)` depending on `vv.l(i)`) were emitted in arbitrary
   dictionary order, causing division by zero when a dependency hadn't been initialized.

---

## Root Cause

### Cause 1: Non-transitive calibration parameter detection

The emitter classifies parameters into two passes:
- `no_varref_attr`: emitted before variable declarations (regular parameters)
- `only_varref_attr`: emitted after variable `.l` initialization (calibration parameters)

Parameters like `cva = sum(i, v.l(i) * x.l(i))` were correctly classified as calibration
(they directly reference `.l`). But `rva = cva / cli` was NOT classified as calibration
because it references `cva` and `cli` as `ParamRef` (not `VarRef`), even though those
parameters themselves depend on `.l` values. This caused `rva` to be emitted in the
first pass, before `cva` and `cli` were computed.

### Cause 2: Unsorted variable `.l` initialization

Expression-based `.l` initializations (e.g., `l.l(i) = f(vv.l(i))`) were emitted in
dictionary insertion order. When `l.l(i)` referenced `vv.l(i)` but `vv` appeared later
in the dictionary, `vv.l(i)` was 0 (uninitialized), causing division by zero.

---

## Fix

### Fix 1: Transitive calibration closure (`src/emit/original_symbols.py`)

Added `_collect_param_refs()` helper to collect all `ParamRef` names from an expression
tree. In `emit_computed_parameter_assignments()`, compute the transitive closure of
calibration parameters: if parameter A references parameter B, and B is a calibration
parameter (uses `.l`), then A is also a calibration parameter. Also added topological
sorting (Kahn's algorithm) for the `only_varref_attr` pass to ensure dependencies are
emitted before dependents.

### Fix 2: Variable `.l` topological sort (`src/emit/emit_gams.py`)

Added `_collect_varref_names()` helper to collect variable names referenced as `.l`
in an expression. Refactored variable initialization to group init lines per variable,
detect cross-variable `.l` dependencies, and topologically sort the groups so that
dependencies are initialized first.

### Fix 3: `$onImplicitAssign` wrapping (`src/emit/emit_gams.py`)

Added `$onImplicitAssign` / `$offImplicitAssign` directives around both the variable
initialization section and the calibration parameter section to suppress GAMS Error 141
when `.l` expressions reference variables that have been declared but not yet data-assigned.

---

## Verification

After the fix, chenery MCP:
- Compiles without errors
- Solves successfully (Normal completion)
- Residual: 3.98e-11

```bash
python -m src.cli data/gamslib/raw/chenery.gms -o /tmp/chenery_mcp.gms
gams /tmp/chenery_mcp.gms lo=3
# *** Status: Normal completion
```

---

## Files Modified

| File | Change |
|------|--------|
| `src/emit/original_symbols.py` | Added `_collect_param_refs()`, transitive calibration closure, topological sort |
| `src/emit/emit_gams.py` | Added `_collect_varref_names()`, variable `.l` init topological sort, `$onImplicitAssign` wrapping |
| `data/gamslib/mcp/chenery_mcp.gms` | Regenerated with fixes |
