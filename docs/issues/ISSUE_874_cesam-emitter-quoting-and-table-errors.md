# Cesam: Emitter Missing Quotes on Set Elements + Table Comment Data Leak

**GitHub Issue:** [#874](https://github.com/jeffreyhorn/nlp2mcp/issues/874)
**Status:** OPEN
**Severity:** High — Model translates but GAMS compilation fails (57 errors)
**Date:** 2026-02-25
**Affected Models:** cesam

---

## Problem Summary

The cesam model translates to MCP but the emitted GAMS code fails with 57 compilation errors.
Three distinct emitter bugs produce cascading failures:

1. **Missing quotes on `sameas()` element literals** — `sameas(ii, ROW)` instead of
   `sameas(ii, "ROW")` throughout equations and stationarity conditions
2. **Missing quotes on numeric set element indices** — `vbar1(ii,3)` instead of
   `vbar1(ii,"3")` in parameter assignments
3. **Table comment data leak** — a commented-out Table data row (`*  COM  6753.3320 ...`)
   produces a spurious domain element `'6753.3320'` in the SAM parameter data
4. **Quoted set variable in `.l` initialization** — `wbar1(ii,"jwt")` instead of
   `wbar1(ii,jwt)` treats the index variable name as a string literal

---

## Error Details

### Error 1: Unquoted `sameas()` element literals ($120/$149/$340)

```gams
* Emitted (WRONG):
ROWSUM(ii)$((not sameas(ii, ROW))).. ...
stat_m_gdpdef.. ... 1$(sameas(a_jj, fac) and sameas(a_jj, act)) ...
d_ERR2(a_macro).. ... 1$sameas(a_macro, gdpfc2) ...

* Original (CORRECT):
ROWSUM(ii)$(not sameas(ii,"ROW")).. ...
* In stationarity: sameas(a_ii,"fac"), sameas(a_jj,"act"), sameas(a_macro,"gdpfc2"), etc.
```

Affected elements: `ROW`, `fac`, `act`, `gre`, `com`, `gdpfc2`, `gdp2`, `macro`.
GAMS interprets bare `ROW` as a set identifier, not a set element label.

### Error 2: Unquoted numeric set elements ($145)

```gams
* Emitted (WRONG):
vbar1(ii,3) = 0;

* Original (CORRECT):
vbar1(ii,"3") = 0;
```

Set `jwt / 1*5 /` creates elements `"1"` through `"5"`. Bare `3` is a numeric literal,
not a set element reference.

### Error 3: Table comment data leak ($170)

```gams
* Emitted SAM data contains:
'6753.3320'.ACT 1764.5, '6753.3320'.COM 2118.5, ...

* Original Table has a commented-out line:
*  COM      6753.3320   1764.5000  2118.5000  2197.7980
   COM      6953.3320   1564.5000  2518.5000  2597.7980
```

The value `6753.3320` from the comment line becomes a spurious row element. Element
`'6753.3320'` is not in set `i`, causing domain violation $170.

### Error 4: Quoted set variable name in `.l` initialization ($116/$170)

```gams
* Emitted (WRONG):
W1.l(ii,jwt) = wbar1(ii,"jwt");
W2.l(macro,jwt) = wbar2("macro","jwt");

* Should be:
W1.l(ii,jwt) = wbar1(ii,jwt);
W2.l(macro,jwt) = wbar2(macro,jwt);
```

The emitter quotes set index variable names as if they were string literals.

---

## Reproduction Steps

```bash
python -m src.cli data/gamslib/raw/cesam.gms -o /tmp/cesam_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/cesam_mcp.gms action=c
# Expect: 57 errors
```

---

## Root Cause Analysis

### Bug 1 (sameas quoting): Emitter string representation

The `sameas()` function in GAMS takes two arguments: a set variable and an element literal.
The emitter renders the element literal without quotes, but GAMS requires quoted strings
for element references in `sameas()`.

In `src/emit/`, the `sameas` expression is emitted from the IR's `Sameas` node. The second
argument is stored as a string in the IR but the emitter does not add quotes around it.

### Bug 2 (numeric element quoting): Index emission

When emitting parameter assignments like `vbar1(ii,"3") = 0`, the emitter renders numeric-
looking index values without quotes. GAMS requires all set element references to be quoted
when they look like numbers.

### Bug 3 (table comment leak): Table parser

The Table parser (`_handle_table_block`) processes multi-slice tables with `+` continuation
headers. Comment lines within the Table data block (starting with `*`) should be stripped
before data extraction. Either the preprocessor isn't removing comment lines within Table
blocks, or the Table flattening logic is picking up data from comment lines.

### Bug 4 (quoted variable names in .l init): `.l` expression emission

When emitting `.l` initialization expressions like `W1.l(ii,jwt) = wbar1(ii,jwt)`, the
emitter incorrectly quotes the index variable names (producing `wbar1(ii,"jwt")` instead
of `wbar1(ii,jwt)`). This may be caused by the expression emitter treating parameter
reference indices as string literals rather than set variables.

---

## Suggested Fix

1. **sameas quoting**: In the expression emitter, detect `Sameas` nodes and ensure the
   element argument is emitted with quotes: `sameas(setvar, "element")`.

2. **Numeric element quoting**: In parameter assignment emission, detect numeric-looking
   set element indices and emit them with quotes.

3. **Table comment stripping**: In `_handle_table_block`, ensure comment lines (starting
   with `*`) within Table data blocks are excluded from data extraction.

4. **`.l` expression indices**: Fix the `.l` expression emitter to distinguish between
   set variable references (no quotes) and string literal references (quoted).

**Effort estimate:** ~4-6h total (bugs 1-2 are likely the same underlying quoting issue)

---

## Files That Need Changes

| File | Change |
|------|--------|
| `src/emit/emit_gams.py` or `src/emit/equations.py` | Fix `sameas()` element quoting |
| `src/emit/emit_gams.py` | Fix numeric set element quoting in assignments |
| `src/ir/parser.py` | Strip comment lines from Table data processing |
| `src/emit/emit_gams.py` | Fix `.l` expression index variable vs literal quoting |

---

## Related Issues

- **Issue #864** (resolved): cesam multi-solve objective extraction (fixed in this branch)
- **Issue #862** (partial): sambal KKT stationarity — related `sameas` quoting in stationarity
