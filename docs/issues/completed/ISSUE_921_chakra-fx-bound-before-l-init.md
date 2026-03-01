# chakra: `.fx` Bounds Emitted Before `.l` Initialization

**GitHub Issue:** #921 (https://github.com/jeffreyhorn/nlp2mcp/issues/921)
**Model:** chakra
**Category:** path_syntax_error (compilation error $141)
**Severity:** Model cannot compile
**Sprint:** 21, Day 9
**Status:** RESOLVED

## Problem

The generated MCP file for chakra has `.fx` bounds that reference `.l` values, but these are emitted *before* the `.l` initialization section. GAMS error $141: "Symbol declared but no values have been assigned."

```
y.fx(tb) = y.l(tb);    <- line 78 of chakra_mcp.gms (Variable Bounds section)
...
y.l(t) = y0 * 1.06 ** (ord(t) - 1);   <- line 90 (Variable Initialization section)
```

At line 78, the `.l` element for `y(tb)` is still unassigned, so GAMS reports error $141 ("Symbol declared but no values have been assigned."). (Only with `$onImplicitAssign` would such unassigned `.l` values be treated as 0.)

## Root Cause

In `src/emit/emit_gams.py`, the emission order was:

1. Variable declarations
2. **Expression-based `.lo`/`.up`/`.fx` bounds** — `bound_lines`
3. **`.l` initialization** — `init_lines`

When a `.fx` expression references `.l` (e.g., `y.fx(tb) = y.l(tb)`), it requires `.l` to be initialized first. But bound emission always preceded `.l` initialization.

## Fix

Split bound emission into two passes in `src/emit/emit_gams.py` using `_collect_varref_names()` to detect `.l` references:

1. **`bound_lines`** — bounds that do NOT reference `.l` — emitted before init (unchanged)
2. **`.l` initialization** — `init_lines` (unchanged)
3. **`deferred_bound_lines`** — bounds that DO reference `.l` — emitted after init

The `_collect_varref_names()` helper recursively checks if a bound expression contains any `VarRef` with `.l` attribute. Bounds with `.l` references are placed in `deferred_bound_lines` and emitted after the Variable Initialization section.

### Files Modified

| File | Change |
|------|--------|
| `src/emit/emit_gams.py` | Split `bound_lines` into `.l`-dependent (`deferred_bound_lines`) and `.l`-independent passes; emit deferred bounds after `init_lines` |

### Verification

- chakra MCP compiles with 0 errors (was $141 error)
- SOLVER STATUS 1 (Normal Completion), MODEL STATUS 1 (Optimal)
- Generated MCP now emits `.l` init (line 83) before `.fx` bounds referencing `.l` (line 92)
- All 3877 tests pass
