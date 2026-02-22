# Bearing MCP: `.scale` Attribute Emission Not Supported

**GitHub Issue:** [#835](https://github.com/jeffreyhorn/nlp2mcp/issues/835)
**Status:** OPEN — `.scale` attributes parsed into IR but not emitted in MCP output
**Severity:** Medium — MCP generates and compiles but PATH reports locally infeasible (MODEL STATUS 5)
**Date:** 2026-02-22
**Affected Models:** bearing (potentially other models using `.scale`)

---

## Problem Summary

The bearing model (`data/gamslib/raw/bearing.gms`) generates an MCP file that compiles
successfully, but the PATH solver reports locally infeasible. The root cause is that bearing
uses `.scale` variable attributes which are parsed into the IR but not emitted in the MCP output.

Without scaling, the solver sees poorly-scaled variables and equations, leading to convergence
failure.

---

## Reproduction

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/bearing.gms -o /tmp/bearing_mcp.gms

# Run GAMS
gams /tmp/bearing_mcp.gms lo=2

# Result: PATH reports locally infeasible (MODEL STATUS 5)
```

---

## Root Cause

GAMS `.scale` attributes set variable and equation scaling factors that help the solver handle
problems with large differences in magnitude between variables. The bearing model uses these
extensively:

```gams
w.scale(i)   = 1.0e-4;
wr.scale(i)  = 1.0e-6;
```

The current pipeline:
1. Parses `.scale` attributes into the IR (via `VariableDef` attribute handling)
2. Does **not** emit `.scale` assignments in the MCP prolog
3. PATH solver sees unscaled variables and fails to converge

---

## Suggested Fix

Emit `.scale` assignments in the MCP prolog for variables and equations that have scaling
factors. This requires:

1. Check `VariableDef` instances for `.scale` / `.scale_map` attributes
2. Emit `var.scale(indices) = value;` statements after variable declarations
3. Similarly handle equation scaling if present

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/ir/ir.py` | `VariableDef` — check for `.scale` attribute storage |
| `src/emit/emit_gams.py` | MCP prolog emission — add `.scale` output |
| `data/gamslib/raw/bearing.gms` | Original model with `.scale` usage |

---

## Estimated Effort

~2h — emit `.scale` assignments in MCP prolog for variables that have scaling factors
