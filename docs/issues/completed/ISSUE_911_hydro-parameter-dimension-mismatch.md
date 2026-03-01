# hydro: Parameter Dimension Mismatch ($148)

**GitHub Issue:** [#911](https://github.com/jeffreyhorn/nlp2mcp/issues/911)
**Model:** hydro (GAMSlib)
**Sprint:** 21 Day 8
**Error Category:** Compilation — $148 Dimension different
**Status:** RESOLVED

## Problem

The generated MCP emits `load` as a scalar (`Scalars load /1300/`) but references it as `load(t)` in equations, producing GAMS error $148 ("Dimension different").

```gams
comp_demcons(t).. thermal(t) + hydro(t) - (load(t) + loss(t)) =G= 0;
```

## Root Cause

In the original hydro.gms, `load` is declared without an explicit domain but with indexed inline data:

```gams
Parameter load 'mw load for the t-th period' / 1 1200, 2 1500, 3 1100
                                               4 1800, 5  950, 6 1300 /;
```

GAMS allows this pattern — the parameter's dimensionality is inferred from the data keys. However, the parser's `_parse_param_data_items()` method had a bug at the `param_data_scalar` case: when `domain` was empty (no explicit domain declaration), it collapsed all index keys to `()`:

```python
key_tuple: tuple[str, ...] = tuple(key) if domain else ()
```

This caused all 6 entries to map to the same empty key `()`, with only the last value (1300) surviving. The parameter was then treated as a scalar.

## Fix

Two changes in `src/ir/parser.py`:

1. **`_parse_param_data_items()`**: Preserve actual index keys even when `domain` is empty, instead of collapsing to `()`. The dimension check is only applied when `domain` is explicitly provided.

2. **`_parse_param_decl()`**: After parsing data, if domain is empty but values have indexed keys, infer a wildcard domain `('*',) * max_dim` from the key dimensionality.

After fix, `load` is correctly emitted as:
```gams
Parameter
    load(*) /'1' 1200, '2' 1500, '3' 1100, '4' 1800, '5' 950, '6' 1300/
;
```

## Verification

- hydro MCP compiles cleanly: 0 errors
- SOLVER STATUS 1 (Normal Completion), MODEL STATUS 1 (Optimal)
- All 3881 tests pass
