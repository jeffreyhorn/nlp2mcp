# tfordy: Compound Table Headers Dropped + Unquoted Hyphenated Set Elements

**GitHub Issue:** [#886](https://github.com/jeffreyhorn/nlp2mcp/issues/886)
**Status:** RESOLVED (Bug A and Bug B both fixed)
**Severity:** Low — Model compiles cleanly with 0 errors; only blocked by GAMS demo license limit
**Date:** 2026-02-25
**Affected Models:** tfordy (potentially other models with dotted table headers)
**Sprint:** 21 (Day 4 blocker)

---

## Problem Summary

The `tfordy.gms` model parses and translates but the emitted GAMS file had two distinct bugs:

1. **Bug A (Critical)**: Table data for `yef(at,s,cl)` and `ymf(at,k,s,cl)` was silently dropped because compound (dotted) column headers like `nigra.pulplogs` were not parsed correctly
2. **Bug B**: Hyphenated set elements like `period-1` were emitted unquoted, causing GAMS to interpret them as arithmetic (`period minus 1`)

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

The column header `nigra.pulplogs` should map to two domain indices `('nigra', 'pulplogs')` (matching the 2nd and 3rd domain elements `s` and `cl`). The Lark lexer tokenized `nigra.pulplogs` as separate tokens which were treated as individual column headers.

### Fix (RESOLVED)

Fixed in Sprint 21 Day 7 (commit 7f87431e) by adding `_merge_dotted_col_headers()`
helper in `src/ir/parser.py`. This function detects adjacent tokens separated by
dots in the source text and merges them into compound column headers (e.g.,
`nigra.pulplogs`). The merged dotted name is stored as a single key element,
and the existing `_expand_table_key()` in `src/emit/original_symbols.py` correctly
splits it into individual domain elements during emission.

**Verification:**
- `yef` now has 68 entries with 2-tuple keys `('a-10', 'nigra.pulplogs')` which
  expand to 3-tuples `('a-10', 'nigra', 'pulplogs')` matching domain `(at,s,cl)`
- `ymf` now has 96 entries with 2-tuple keys `('a-10.good', 'brutia.pulplogs')`
  which expand to 4-tuples `('a-10', 'good', 'brutia', 'pulplogs')` matching
  domain `(at,k,s,cl)`

**Tests:** `tests/unit/ir/test_table_parsing.py`

---

## Bug B: Unquoted Hyphenated Set Elements

### Fix (RESOLVED)

Fixed in `_quote_assignment_index()` at `src/emit/original_symbols.py` and
additional quoting fixes in PR #951.

---

## Current Status (2026-02-28)

- **Compilation:** 0 errors (clean)
- **Solve:** ABORTED — GAMS demo license limit exceeded (3,166 equations / 3,169 variables)
- **Bug A (compound table headers):** RESOLVED — table data correctly parsed and emitted
- **Bug B (unquoted hyphenated elements):** RESOLVED

---

## Related Issues

- Sprint 21 Day 4 PR #883: Lead/lag in parameter assignment LHS (parsing fix)
- [#901](https://github.com/jeffreyhorn/nlp2mcp/issues/901) — twocge: same dotted column header pattern
