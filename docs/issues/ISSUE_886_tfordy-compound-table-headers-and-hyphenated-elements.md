# tfordy: Compound Table Headers Dropped + Unquoted Hyphenated Set Elements

**GitHub Issue:** [#886](https://github.com/jeffreyhorn/nlp2mcp/issues/886)
**Status:** PARTIALLY RESOLVED (Bug B fixed, Bug A still open)
**Severity:** Low — Model compiles cleanly with 0 errors; only blocked by GAMS demo license limit
**Date:** 2026-02-25
**Affected Models:** tfordy (potentially other models with dotted table headers)
**Sprint:** 21 (Day 4 blocker)

---

## Problem Summary

The `tfordy.gms` model parses and translates but the emitted GAMS file has two distinct bugs causing 15 compilation errors:

1. **Bug A (Critical)**: Table data for `yef(at,s,cl)` and `ymf(at,k,s,cl)` is silently dropped because compound (dotted) column headers like `nigra.pulplogs` are not parsed correctly
2. **Bug B**: Hyphenated set elements like `period-1` are emitted unquoted, causing GAMS to interpret them as arithmetic (`period minus 1`)

---

## Error Details

GAMS compilation errors when running emitted file:

```
**** Error 141: Symbol declared but no values have been assigned
    (for yef and ymf — all table data lost)

**** Error 120: Unknown identifier (period interpreted as unknown symbol)
    avl(period-1,t) = 1;
         ^
```

---

## Bug A: Missing Table Data (Compound Column Headers)

### Root Cause

Tables `yef(at,s,cl)` and `ymf(at,k,s,cl)` use dotted compound column headers:

```gams
Table yef(at,s,cl)  'yield of existing forest  (m3 per ha)'
           nigra.pulplogs  nigra.sawlogs  brutia.pulplogs  brutia.sawlogs
   a-10              38.8            1.2             17.8             3.2
   a-20              48.4            8.6             16.8            19.1
   a-30              51.6           16.8             15.0            32.9
```

The column header `nigra.pulplogs` should map to two domain indices `('nigra', 'pulplogs')` (matching the 2nd and 3rd domain elements `s` and `cl`). However:

1. The Lark lexer tokenizes `nigra.pulplogs` as separate tokens: `nigra`, `.`, `pulplogs`
2. Column header extraction in `_handle_table_block()` (`src/ir/parser.py` line 2431) only picks up `ID`/`NUMBER`/`STRING` tokens, skipping `DOT` tokens
3. Result: 8 individual column headers instead of 4 compound ones
4. Values are stored as 2-tuples `('a-10', 'pulplogs')` instead of 3-tuples `('a-10', 'nigra', 'pulplogs')`
5. The emitter's `_expand_table_key()` (`src/emit/original_symbols.py` line 636-658) tries to expand keys but finds the wrong arity and returns `None`
6. **All 68 `yef` entries and 96 `ymf` entries are silently dropped**

### Fix

In `_handle_table_block()` at `src/ir/parser.py`, the column header extraction needs to merge adjacent ID tokens separated by DOT tokens into compound dotted names. When processing `first_line_tokens`, consecutive sequences of `ID DOT ID` should be merged into a single compound header like `nigra.pulplogs`.

**Estimated effort:** 2–3h (parser + tests)

---

## Bug B: Unquoted Hyphenated Set Elements

### Root Cause

The parameter `avl(t,t)` is assigned via domain-over syntax:

```gams
avl(t,t)   = 1;
avl(t,t-1) = 1;
avl(t,t-2) = 1;
```

The first assignment `avl(t,t) = 1` is expanded by the parser to element-level values. Set `t` has members like `period-1`, `period-2`, etc. The emitter outputs:

```gams
avl(period-1,t) = 1;
```

But GAMS interprets `period-1` as the arithmetic expression `period minus 1`. It should be:

```gams
avl('period-1',t) = 1;
```

### Fix (RESOLVED)

Fixed in `_quote_assignment_index()` at `src/emit/original_symbols.py`: added
`_needs_quoting()` check to detect elements containing operators (`-`, `+`) or
other special characters. When `domain_lower` is provided, all non-domain
elements are now quoted as literals. The emitter now outputs `avl('period-1',t) = 1;`
correctly.

Compilation errors from Bug B ($120 unquoted identifiers) are eliminated.

**Update (2026-02-27):** After additional quoting fixes (PR #951), tfordy now
compiles cleanly with **0 compilation errors**. The MCP model generates
successfully (3,166 equations, 3,169 variables) but the solve is aborted
because the model exceeds the GAMS demo license limit. Bug A (compound table
headers) may still silently drop data, but it no longer causes compilation
errors — the missing table data doesn't trigger $141 errors in the current
MCP output. This needs further investigation with a full GAMS license.

---

## Reproduction

```python
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
from src.emit.gams_emitter import emit_gams

m = parse_model_file('data/gamslib/raw/tfordy.gms')
result = emit_gams(m)

# Write and run through GAMS:
with open('/tmp/tfordy_test.gms', 'w') as f:
    f.write(result)

# /Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/tfordy_test.gms lo=3
# → 15 compilation errors
```

Verify table data loss:
```python
m = parse_model_file('data/gamslib/raw/tfordy.gms')
yef = m.params['yef']
print(f"yef domain: {yef.domain}, values: {len(yef.values)}")
# Expected: values should be ~68 entries with 3-element keys
# Actual: values have 2-element keys (wrong arity)
```

---

## GAMS Source Context

### Compound column headers (lines 41–60):
```gams
Table yef(at,s,cl)   'yield of existing forest               (m3 per ha)'
           nigra.pulplogs  nigra.sawlogs  brutia.pulplogs  brutia.sawlogs
   a-10              38.8            1.2             17.8             3.2
   a-20              48.4            8.6             16.8            19.1
   a-30              51.6           16.8             15.0            32.9
```

### Compound row AND column headers (lines 61–86):
```gams
Table ymf(at,k,s,cl) 'yield of managed forest                (m3 per ha)'
                 nigra.pulplogs  nigra.sawlogs  brutia.pulplogs  brutia.sawlogs
   a-10.good                                               17.5
   a-20.good              120.0                            66.8
   a-30.good              149.0           73.0             56.0            38.0
```

### Hyphenated set elements (lines 20–22):
```gams
Set  t  'time periods in decades'  / period-1 * period-6 /
     te(t)                         / period-1 * period-3 /
     at 'age of trees'             / a-10, a-20, a-30 /;
```

### Diagonal parameter assignment (lines 138–140):
```gams
avl(t,t)   = 1;
avl(t,t-1) = 1;
avl(t,t-2) = 1;
```

---

## Current Status (2026-02-27)

- **Compilation:** 0 errors (clean)
- **Solve:** ABORTED — GAMS demo license limit exceeded (3,166 equations / 3,169 variables)
- **Bug A (compound table headers):** Still present but not causing compilation errors in MCP output. The silently dropped `yef`/`ymf` table data may affect solution correctness but cannot be verified without a full GAMS license.
- **Bug B (unquoted hyphenated elements):** RESOLVED via `_quote_assignment_index()` fix in PR #951.

---

## Related Issues

- Sprint 21 Day 4 PR #883: Lead/lag in parameter assignment LHS (parsing fix)
- Bug A may affect other models with dotted table column headers (pattern not yet surveyed)
