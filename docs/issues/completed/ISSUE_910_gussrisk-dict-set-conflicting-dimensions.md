# gussrisk: GUSS Dict Set Conflicting Dimensions ($161)

**GitHub Issue:** [#910](https://github.com/jeffreyhorn/nlp2mcp/issues/910)
**Status:** FIXED
**Model:** gussrisk (GAMSlib)
**Date:** 2026-02-26
**Fixed:** 2026-03-17
**Error Category:** Compilation — $161 Conflicting dimensions in element

---

## Problem

The generated MCP file declared a `dict` set with the first element incorrectly quoted:

```gams
dict /'rapscenarios.scenario.', rap.param.riskaver, ...
```

The original GAMS has `rapscenarios.scenario.''` (three-component GUSS triple with empty
third component). The parser stored this as `"rapscenarios.scenario."` (trailing dot), and
the emitter quoted the entire string as `'rapscenarios.scenario.'` because the trailing dot
failed the valid-identifier pattern check. This changed the semantic from a 3-tuple to a
single quoted label, causing GAMS $161 errors.

---

## Fix Applied (2026-03-17)

In `src/emit/original_symbols.py`, `_sanitize_set_element()` now detects elements with a
trailing dot and appends `''` to restore the empty third component:

```python
if element.endswith("."):
    return element + "''"
```

**Before:** `'rapscenarios.scenario.'` (single quoted label)
**After:** `rapscenarios.scenario.''` (GUSS 3-tuple with empty third component)

**Result:** MCP compiles and solves to MODEL STATUS 1 (Optimal), SOLVER STATUS 1 (Normal).

---

## Files Modified

| File | Change |
|------|--------|
| `src/emit/original_symbols.py:~313` | Trailing-dot detection in `_sanitize_set_element()` |
