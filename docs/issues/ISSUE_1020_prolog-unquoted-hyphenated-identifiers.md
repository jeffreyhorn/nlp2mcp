# prolog: Unquoted Hyphenated Identifiers in Variable Level Assignments

**GitHub Issue:** [#1020](https://github.com/jeffreyhorn/nlp2mcp/issues/1020)
**Status:** OPEN
**Severity:** High — 9 compilation errors block solve
**Date:** 2026-03-08
**Affected Models:** prolog

---

## Problem Summary

The prolog model translates to MCP, but GAMS reports 9 compilation errors because hyphenated element names (`h-industry`, `l-industry`) are emitted unquoted in variable `.l` initialization assignments. GAMS interprets `h-industry` as `h` minus `industry`, causing Error 140 (unknown symbol), Error 171 (domain violation), and Error 120 (unknown identifier entered as set).

---

## Error Details

```
 127  p.l(h-industry) = max(p.l(h-industry), 0.2);
****       $171    $140          $171
**** 140  Unknown symbol
**** 171  Domain violation for set
 128  p.l(l-industry) = max(p.l(l-industry), 0.2);
****      $120,340,171           $171
**** 120  Unknown identifier entered as set
**** 171  Domain violation for set
**** 340  A label/element with the same name exist.
```

Total: 9 compilation errors, solve aborted.

---

## Root Cause

The set `i` has elements `food`, `h-industry`, `l-industry` (line 19 of emitted MCP). Inline parameter data correctly quotes these as `'h-industry'` and `'l-industry'`. However, variable `.l` initialization statements emit them bare:

**Emitted (WRONG):**
```gams
p.l(h-industry) = max(p.l(h-industry), 0.2);
p.l(l-industry) = max(p.l(l-industry), 0.2);
```

**Expected (CORRECT):**
```gams
p.l('h-industry') = max(p.l('h-industry'), 0.2);
p.l('l-industry') = max(p.l('l-industry'), 0.2);
```

The emitter code that generates variable `.l` assignments (likely in `src/emit/emit_gams.py` or `src/emit/original_symbols.py`) does not apply `_needs_quoting()` / `_quote_assignment_index()` to index elements in `.l` assignments. The inline data path and parameter assignment path already handle quoting correctly; the variable initialization path does not.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/prolog.gms -o /tmp/prolog_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/prolog_mcp.gms lo=0 o=/tmp/prolog_mcp.lst

# Check for errors:
grep '$171\|$140\|$120' /tmp/prolog_mcp.lst

# Verify unquoted hyphenated identifiers:
grep 'h-industry\|l-industry' /tmp/prolog_mcp.gms | grep -v "'"
```

---

## Suggested Fix

In the variable `.l` initialization emission code, apply `_needs_quoting()` or `_quote_assignment_index()` to each index element. Elements containing hyphens, digits-first patterns, or other special characters must be single-quoted.

The fix should be analogous to how `emit_computed_parameter_assignments()` uses `_quote_assignment_index()` for LHS index elements.

**Effort estimate:** ~1h

---

## Files Likely Affected

| File | Change |
|------|--------|
| `src/emit/emit_gams.py` or `src/emit/original_symbols.py` | Quote index elements in variable `.l` initialization statements |

---

## Related Issues

- Issue #874 (fixed): Parameter assignment quoting for hyphenated elements
- Issue #886 (fixed): Set element quoting with special characters
- Issue #912 (fixed): Literal element vs. set name disambiguation
