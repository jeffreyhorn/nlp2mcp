# glider: Variable name collides with set element in emitted indices ($120/$149/$171/$340)

**GitHub Issue:** [#1004](https://github.com/jeffreyhorn/nlp2mcp/issues/1004)
**Model:** glider (GAMSlib SEQ=239)
**Status:** OPEN
**Error category:** `path_syntax_error` (Subcategory C-adjacent — $120/$149/$171/$340)
**Severity:** High — model parses and translates but GAMS compilation fails (100+ errors across complementarity and stationarity equations)

---

## Problem Summary

The glider model declares set `c / x, y /` (coordinates) and also has variables `pos(c,h)`, `vel(c,h)`, etc. When the emitter generates per-instance complementarity equations like `comp_lo_pos_x_h0.. pos(x,"h0")`, the bare `x` is ambiguous — GAMS can't tell if `x` refers to the set element `"x"` of set `c` or something else. GAMS raises Error $120 "Unknown identifier entered as set", $149 "Uncontrolled set entered as constant", $171 "Domain violation for set", and $340 "A label/element with the same name exist".

---

## Error Details

### Lines 846+ — $120/$149/$171/$340 in complementarity equations

```
 846  comp_lo_pos_x_h0.. pos(x,"h0") - 0 =G= 0;
****                         $120,340,149,171
**** 120  Unknown identifier entered as set
**** 149  Uncontrolled set entered as constant
**** 171  Domain violation for set
**** 340  A label/element with the same name exist. You may have forgotten
****         to quote a label/element reference.

 847  comp_lo_pos_x_h1.. pos(x,"h1") - 0 =G= 0;
****                          $149,171
```

The pattern repeats for all ~50 discretization points (h0 through h50) and for all variable types (`pos`, `vel`, `v_dot`), generating 100+ errors.

### Original GAMS Context

```gams
Set
   c 'coordinates' / x 'distance', y 'altitude' /
   h 'step number' / h0*h%nh% /;

Variable
   pos(c,h)   'position x distance y altitude'
   vel(c,h)   'velocity x distance y altitude'
```

Set `c` has elements `x` and `y`. GAMS Error $340 explicitly warns: "A label/element with the same name exist. You may have forgotten to quote a label/element reference."

---

## Root Cause

**Primary file:** `src/emit/original_symbols.py` or `src/emit/expr_to_gams.py`
**Key function:** Per-instance equation emission / index quoting logic

When emitting per-instance complementarity or stationarity equations, the emitter substitutes concrete element values for indices. For `pos(c,h)` with instance `("x", "h0")`:
- `"h0"` is correctly quoted as `"h0"` (it doesn't match a set name)
- `"x"` is NOT quoted because... it matches a set name? Or the quoting logic doesn't detect the collision

The fix should ensure that element labels which collide with other identifiers (set names, variable names, reserved words) are always quoted.

### Expected Fix

When emitting element labels as indices (not set-iterating indices), quote them:
- `pos(x,"h0")` should become `pos("x","h0")`
- The quoting decision should check whether the label could be misinterpreted as a set reference

This is related to the `_quote_indices` logic in `expr_to_gams.py` or the index emission in `original_symbols.py`.

---

## Reproduction Steps

```bash
.venv/bin/python -m src.cli data/gamslib/raw/glider.gms -o /tmp/glider_mcp.gms --quiet
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/glider_mcp.gms lo=2 o=/tmp/glider_mcp.lst
grep '$149' /tmp/glider_mcp.lst | head -10
```

---

## Affected Equations

| Equation Pattern | Count | Error | Problem Index |
|-----------------|-------|-------|---------------|
| `comp_lo_pos_x_h*` | ~50 | $120/$149/$171/$340 | Bare `x` (element of set `c`) |
| `comp_lo_pos_y_h*` | ~50 | $149/$171 | Bare `y` (element of set `c`) |
| `comp_lo_vel_*` | ~100 | $149/$171 | Same pattern |
| `stat_pos(c,h)` | stationarity | may also be affected | `pos(x,...)` in derivative |

---

## Notes

- GAMS Error $340 explicitly identifies this as a quoting issue: "You may have forgotten to quote a label/element reference."
- The element `x` is particularly problematic because it's a very common name; `y` may also cause issues depending on context.
- This is distinct from the stationarity uncontrolled set issue (Subcategory C). The Sprint 22 Day 1 stationarity fix does not address this — it's an element quoting issue in per-instance equation emission.
- Set elements used as indices in per-instance equations should always be quoted (e.g., `pos("x","h0")`) to avoid ambiguity.
