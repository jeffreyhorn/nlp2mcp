# imsl: Post-solve parameter assignments emitted before MCP solve statement

**GitHub Issue:** [#1036](https://github.com/jeffreyhorn/nlp2mcp/issues/1036)
**Status:** FIXED
**Severity:** Medium — causes GAMS compilation Error 116 ("Label is unknown")
**Date:** 2026-03-10
**Fixed:** 2026-03-10
**Affected Models:** imsl (SEQ=59), potentially any model with post-solve reporting parameters

---

## Problem Summary

The imsl model has parameter assignments that depend on solution values (marginals `.m`) which only exist after a solve statement. The MCP emitter placed **all** parameter assignments before the MCP equations and solve statement, causing GAMS Error 116 because `drep(n,"dev")` references a label that hasn't been computed yet.

---

## Fix

### Option C implemented: Exclude parameters not referenced in any model equation

Added `_collect_model_relevant_params()` in `src/emit/emit_gams.py`:
- Collects parameter names referenced in model equations and objective expression
- Includes parameters referenced in variable `.l`/`.lo`/`.up`/`.fx` initialization expressions (critical for solver convergence)
- Computes transitive closure (params referenced by other relevant params' expressions)
- Returns the set of model-relevant params; complement is excluded from emission

Integrated via `_merge_exclude_params()` helper into:
- `emit_computed_parameter_assignments()` — main pre-solve computed params
- `emit_subset_value_assignments()` — subset-qualified parameter values

Non-model-relevant parameters (e.g., `drep`, `prep`, `test`, `primaldev`, `dualdev`) are excluded from computed assignment emission. Their declarations in the Parameters/Scalars block are harmless and kept.

### Verification

```
$ python -m src.cli data/gamslib/raw/imsl.gms -o /tmp/imsl_mcp.gms
$ gams /tmp/imsl_mcp.gms
# PATH solution found, Normal completion, residual 2.46e-07
```

Post-solve reporting assignments (`drep(n,"t")`, `test(n,"power-ser")`, `dualdev`, etc.) no longer appear in the MCP output.

---

## Affected Files

| File | Change |
|------|--------|
| `src/emit/emit_gams.py` | Added `_collect_model_relevant_params()`, `_merge_exclude_params()`; integrated non-model param filtering |

---

## Context

- LP models are valid MCP targets (KKT conditions are well-defined)
- This fix also benefits any model with post-solve reporting parameters that reference `.l` or `.m` values
