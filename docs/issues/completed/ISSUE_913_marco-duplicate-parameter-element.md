# marco: Duplicate Element in Parameter Data ($172)

**GitHub Issue:** [#913](https://github.com/jeffreyhorn/nlp2mcp/issues/913)
**Model:** marco (GAMSlib)
**Sprint:** 21 Day 8
**Error Category:** Compilation — $172 Element is redefined
**Status:** RESOLVED (Sprint 22 Day 12)

## Problem

The generated MCP file declares parameter `qs(lim,cf,q)` with a duplicate entry for `upper.'fuel-oil'.sulfur`:

```gams
qs(lim,cf,q) /
    lower.premium.octane 90, ...,
    upper.'fuel-oil'.sulfur 3.5,
    ...,
    upper.'fuel-oil'.sulfur 3.4
/
```

GAMS error $172: "Element is redefined" — the same key `(upper, fuel-oil, sulfur)` appears twice with different values (3.5 and 3.4).

## Error Output

```
**** 172  Element is redefined
```

4 compilation errors (1 primary $172 + downstream $257, $141 errors).

## Root Cause

The original marco.gms defines `qs` via a TABLE (value 3.5 for `upper.fuel-oil.sulfur`) and a later computed assignment `qs("upper","fuel-oil","sulfur") = 3.4;` that overrides it. In the IR, these are stored as two separate entries with different key representations:
- Table data: `('upper.fuel-oil', 'sulfur') = 3.5` (2-tuple with dotted row header)
- Computed assignment: `('upper', 'fuel-oil', 'sulfur') = 3.4` (3-tuple)

The `_expand_table_key()` function expands the 2-tuple to match the 3-element domain, but the emitter used a list (`data_parts`) without deduplication, so both entries were emitted.

## Fix

**Commit:** `5456309c` (Sprint 22 Day 12)
**File:** `src/emit/original_symbols.py`

Replaced the `data_parts` list with a `data_by_key` dict keyed on the normalized GAMS key string. This implements last-write-wins semantics: when multiple entries expand to the same key, only the last value is emitted. The dict preserves insertion order (Python 3.7+) so emission order matches IR iteration order.

## Verification

- marco MCP now has a single entry: `upper.'fuel-oil'.sulfur 3.4`
- All 4,207 tests pass
- No regressions

## Impact

1 model fixed (marco: compilation error → compiles cleanly).
