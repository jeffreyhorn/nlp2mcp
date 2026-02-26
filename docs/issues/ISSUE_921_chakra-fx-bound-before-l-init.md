# chakra: `.fx` Bounds Emitted Before `.l` Initialization

**GitHub Issue:** #921 (https://github.com/jeffreyhorn/nlp2mcp/issues/921)
**Model:** chakra
**Category:** path_syntax_error (compilation error $141)
**Severity:** Model cannot compile
**Sprint:** 21, Day 9

## Problem

The generated MCP file for chakra has `.fx` bounds that reference `.l` values, but these are emitted *before* the `.l` initialization section. GAMS error $141: "Symbol declared but no values have been assigned."

```
y.fx(tb) = y.l(tb);    ← line 78 of chakra_mcp.gms (Variable Bounds section)
...
y.l(t) = y0 * 1.06 ** (ord(t) - 1);   ← line 90 (Variable Initialization section)
```

At line 78, `y.l(tb)` is still uninitialized (default 0 for free variables), so GAMS reports the error.

## Root Cause

In `src/emit/emit_gams.py`, the emission order is:

1. Variable declarations (line ~237)
2. **Expression-based `.lo`/`.up`/`.fx` bounds** — `bound_lines` (lines 241–269)
3. **`.l` initialization** — `init_lines` (lines 271–443)

When a `.fx` expression references `.l` (e.g., `y.fx(tb) = y.l(tb)`), it requires `.l` to be initialized first. But the bound emission always precedes `.l` initialization.

The raw `chakra.gms` does it correctly:
```gams
y.l(t) = y0*(1.06)**(ord(t) - 1);   ← .l assigned first (line 63)
k.l(t) = (y.l(t)/alpha(t))**(1/beta);
c.l(t) = y.l(t) + (1 - delt)*k.l(t) - k.l(t+1);
...
y.fx(tb) = y.l(tb);   ← .fx uses already-assigned .l (line 71)
```

## Reproduction

```bash
python src/cli.py data/gamslib/raw/chakra.gms -o /tmp/chakra_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/chakra_mcp.gms o=/tmp/chakra_mcp.lst
grep '$141' /tmp/chakra_mcp.lst
```

## Affected Models

- **chakra** (confirmed)
- Potentially any model where `.fx(...)` bounds reference `.l(...)` values

## Recommended Fix

Split the bound emission into two passes in `src/emit/emit_gams.py`:

1. Emit `.lo`/`.up`/`.fx` bounds that do NOT reference `.l` — safe before init
2. Emit `.l` initialization (as now, with topological sort for cross-variable chains)
3. Emit `.fx`/`.lo`/`.up` bounds that DO reference `.l` — must follow `.l` init

The existing `_collect_varref_names` helper can detect whether a bound expression contains a `.l` reference. Bounds with `.l` references go into a deferred list emitted after the `init_lines` block.

## Files to Modify

| File | Change |
|------|--------|
| `src/emit/emit_gams.py` | Split bound_lines into .l-dependent and .l-independent passes; emit .l-dependent after init_lines |

## Estimated Effort

~2h
