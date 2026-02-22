# Bearing MCP: `.scale` Attribute Emission Not Supported

**GitHub Issue:** [#835](https://github.com/jeffreyhorn/nlp2mcp/issues/835)
**Status:** RESOLVED
**Severity:** Medium — MCP generates and compiles but PATH reports locally infeasible (MODEL STATUS 5)
**Date:** 2026-02-22
**Resolved:** 2026-02-22
**Affected Models:** bearing (potentially other models using `.scale`)

---

## Problem Summary

The bearing model (`data/gamslib/raw/bearing.gms`) generates an MCP file that compiles
successfully, but the PATH solver reports locally infeasible. The root cause is that bearing
uses `.scale` variable attributes which are parsed into the IR but not emitted in the MCP output.

Without scaling, the solver sees poorly-scaled variables and equations, leading to convergence
failure.

---

## Fix Applied

Three-part fix across IR, parser, and emitter:

1. **`src/ir/symbols.py`**: Added `scale: Expr | None` and `scale_map: dict[tuple[str, ...], Expr]`
   fields to `VariableDef` to store `.scale` attributes as expressions.

2. **`src/ir/parser.py`**: Updated `attr_access` and `attr_access_indexed` handlers to store
   `.scale` values for variables instead of discarding them (mock/store approach).

3. **`src/emit/emit_gams.py`**: Added `.scale` emission section after variable initialization,
   emitting `var.scale = expr;` for each variable with scaling. Also emits
   `model.scaleOpt = 1;` after the model statement when any variable has `.scale` attributes.

Generated MCP now includes:
```gams
* Variable Scaling
mu.scale = 1e-06;
PL.scale = 10000;
Ef.scale = 10000;
Ep.scale = 10000;
h.scale = hmin;
W.scale = Ws;
...
mcp_model.scaleOpt = 1;
```

---

## Files Modified

| File | Change |
|------|--------|
| `src/ir/symbols.py` | Added `scale` and `scale_map` fields to `VariableDef` |
| `src/ir/parser.py` | Store `.scale` values in `attr_access`/`attr_access_indexed` handlers |
| `src/emit/emit_gams.py` | Emit `.scale` statements and `scaleOpt = 1` |
