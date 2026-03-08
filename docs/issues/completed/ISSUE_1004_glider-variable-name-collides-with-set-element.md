# glider: Variable name collides with set element in emitted indices ($120/$149/$171/$340)

**GitHub Issue:** [#1004](https://github.com/jeffreyhorn/nlp2mcp/issues/1004)
**Model:** glider (GAMSlib SEQ=239)
**Status:** FIXED (resolved by prior work)
**Error category:** `path_syntax_error` (Subcategory C-adjacent — $120/$149/$171/$340)
**Severity:** High — model parses and translates but GAMS compilation fails (100+ errors across complementarity and stationarity equations)

---

## Problem Summary

The glider model declares set `c / x, y /` (coordinates) and also has variables `pos(c,h)`, `vel(c,h)`, etc. When the emitter generates per-instance complementarity equations like `comp_lo_pos_x_h0.. pos(x,"h0")`, the bare `x` is ambiguous — GAMS can't tell if `x` refers to the set element `"x"` of set `c` or something else. GAMS raises Error $120 "Unknown identifier entered as set", $149 "Uncontrolled set entered as constant", $171 "Domain violation for set", and $340 "A label/element with the same name exist".

---

## Resolution

This issue has been resolved by prior work. The emitter no longer generates per-instance complementarity equations with expanded element indices. Instead, it emits indexed equations using set iteration:

- **Before**: `comp_lo_pos_x_h0.. pos(x,"h0") - 0 =G= 0;` (per-instance, bare `x`)
- **After**: `comp_lo_pos(c,h)$(has_pos_lo(c,h)).. pos(c,h) - pos_lo_param(c,h) =G= 0;` (indexed; indices are iterators like `c` and `h`, not concrete element labels)

The complementarity and stationarity equations that triggered the original errors now use set iterators in index positions. Some other equations in the model (e.g., `rdef`, `vx_dot_def`, `obj`) do emit concrete element labels, but these are always properly quoted (e.g., `pos("x",i)`, `vel("x",i)`), so no ambiguity arises.

### Verification

- glider MCP compiles with zero GAMS errors (only demo license limit)
- No `$120`, `$149`, `$171`, or `$340` errors in listing file
- Complementarity/stationarity equations use set iterators (`c`, `h`) — no concrete element labels in index positions
- Other equations that reference specific elements properly quote them (e.g., `pos("x",i)`, `v_dot("y",i)`)
- No code changes required — this issue was resolved by the transition from per-instance to indexed complementarity/stationarity equation emission

---

## Notes

- No code changes were made specifically for this issue
- The fix came from the broader emitter improvements that moved from per-instance equation expansion to indexed equation emission with dollar conditions
