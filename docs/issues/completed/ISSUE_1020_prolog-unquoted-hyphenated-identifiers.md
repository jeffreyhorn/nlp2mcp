# prolog: Unquoted Hyphenated Identifiers in Variable Level Assignments

**GitHub Issue:** [#1020](https://github.com/jeffreyhorn/nlp2mcp/issues/1020)
**Status:** FIXED
**Severity:** High — 9 compilation errors block solve
**Date:** 2026-03-08
**Fixed:** 2026-03-09
**Affected Models:** prolog

---

## Problem Summary

The prolog model translates to MCP, but GAMS reports 9 compilation errors because hyphenated element names (`h-industry`, `l-industry`) are emitted unquoted in variable `.l` initialization assignments. GAMS interprets `h-industry` as `h` minus `industry`, causing Error 140 (unknown symbol), Error 171 (domain violation), and Error 120 (unknown identifier entered as set).

---

## Root Cause

The `lo_map` per-element clamp emission used `_format_mixed_indices()` → `_quote_indices()` → `_is_index_offset_syntax()` to format index labels. The `_is_index_offset_syntax()` heuristic has a single-letter lag pattern (`^[a-zA-Z]-[A-Za-z_][A-Za-z0-9_]*$`) that matches `h-industry` and `l-industry` as IndexOffset expressions (interpreting `h` as a base index and `industry` as a symbolic offset). This caused these literal element labels to be emitted unquoted.

The same issue affected the `l_map` and `lo_map` init paths, which also used `_format_mixed_indices()`.

---

## Fix Details

Added a new `_format_map_indices()` helper function in `src/emit/emit_gams.py` that formats `*_map` keys (l_map, lo_map, fx_map) without using the `_is_index_offset_syntax()` heuristic. Instead, it unconditionally quotes every index component via `_quote_uel()`, which also avoids set-name collision cases (e.g., an element `i` in set `i`).

Replaced `_format_mixed_indices()` with `_format_map_indices()` at three call sites:
1. **l_map emission** (Priority 1): variable `.l` numeric init
2. **lo_map emission** (Priority 2): variable `.l` init from lower bounds
3. **lo_map clamp** (Issue #984): per-element `max()` clamps

### Result

- All 9 compilation errors eliminated
- `p.l('h-industry')` and `p.l('l-industry')` now correctly single-quoted
- 4036 tests pass

---

## Files Changed

| File | Change |
|------|--------|
| `src/emit/emit_gams.py` | Added `_format_map_indices()` helper; replaced `_format_mixed_indices()` at 3 `*_map` emission sites; removed unused `_format_mixed_indices` import |
| `tests/unit/emit/test_emission_ordering.py` | Updated `test_indexed_lo_map_clamp_per_element` to expect single-quoted UEL labels |

---

## Related Issues

- Issue #874 (fixed): Parameter assignment quoting for hyphenated elements
- Issue #886 (fixed): Set element quoting with special characters
- Issue #912 (fixed): Literal element vs. set name disambiguation
- Issue #1021 (fixed): `_quote_uel()` helper for fx_map emission
