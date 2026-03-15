# port: Regression — Table Gap-Midpoint Boundary Off-by-One

**GitHub Issue:** [#1090](https://github.com/jeffreyhorn/nlp2mcp/issues/1090)
**Status:** FIXED
**Severity:** Medium — match regressed to mismatch (obj sign flip: +0.298 → -0.261)
**Fix:** Changed `token_col < range_end` to `token_col <= range_end` in both table parsing paths (section-based and non-section). Now port translates, solves to optimal, and matches.
**Date:** 2026-03-14
**Affected Models:** port
**Regressing PR:** #1079 (Sprint 22 Day 8)

---

## Problem Summary

The port model (GAMSlib SEQ=50, "Simple Portfolio Model") regressed from match to mismatch
after PR #1079 introduced gap-midpoint column matching for table parsing. The MCP objective
is -0.261 vs NLP reference +0.298, with the wrong sign.

The table `ydat(b,*)` has columns `rating`, `maturity`, `yield`, `tax-rate`. For rows with
hyphenated bond names (municip-a, municip-b, us-ser-e, us-ser-f), the preprocessor adds
quotes, shifting data values right by 2 columns. This causes the value `2` at column 25 to
fall exactly at the gap midpoint between `rating` and `maturity`, and the `<` comparison
misses it.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/port.gms -o /tmp/port_mcp.gms
gams /tmp/port_mcp.gms lo=2
# MODEL STATUS 1 (Optimal)
# Objective: -0.261 (NLP ref: +0.298)
```

---

## Root Cause

### Table Layout

```gams
Table ydat(b,*)  'bond data'
               rating  maturity  yield  tax-rate
  municip-a         2         9   4.30       0.0
  municip-b         2        15   5.40       0.0
  corporate         2         4   5.00       0.5
  us-ser-e          1         3   4.40       0.7
  us-ser-f          1         7   5.00       0.6  ;
```

Column header positions: `rating`(col 18, width 6), `maturity`(col 26), `yield`(col 36),
`tax-rate`(col 42).

### The Preprocessor Quoting Issue

Hyphenated row labels (`municip-a`) are quoted by the preprocessor (`'municip-a'`), adding
2 characters. This shifts data values right. The value `2` (rating for municip-a) shifts
from column ~23 to column 25.

### The Gap-Midpoint Boundary Bug

PR #1079 computes column ranges as:
```python
range_end = (this_right + next_start) / 2
```

For `rating` (right edge 24) and `maturity` (start 26):
- `range_end = (24 + 26) / 2 = 25.0`

The range check uses strict `<`:
```python
if range_start <= token_col < range_end:
```

For value `2` at column 25: `25 < 25.0` → **False**. The value misses `rating` and falls
into `maturity`'s range `[25.0, 35.0)`.

### Impact on Data

For hyphenated rows, all columns shift right by one:
- `rating` value goes to `maturity`
- `maturity` value goes to `yield`
- `yield` value goes to `tax-rate`
- `tax-rate` value is lost

The `corporate` row (no hyphen, no quoting) is unaffected.

With wrong `yield` and `tax-rate` values, the portfolio optimization produces a completely
different (negative) objective.

---

## Suggested Fix

Change the range_end comparison from strict `<` to inclusive `<=`:

```python
# Both section-based and non-section paths:
if range_start <= token_col <= range_end:  # was: token_col < range_end
```

This is safe because columns are iterated left-to-right with `break` on first match.
When a value falls exactly at the midpoint, the left column matches first (correct for
right-aligned GAMS data).

### Verification

- **port**: `2` at col 25, `rating` range [15, 25.0]. `25 <= 25.0` → True. Correct.
- **ibm1** (PR #1079's original fix): `.21` at col 39, `min-use` range [27, 37.5].
  `39 <= 37.5` → False. Falls to `cost` [37.5, inf). Correct. No regression.

---

## Files to Modify

| File | Change |
|------|--------|
| `src/ir/parser.py:~2760` | Change `token_col < range_end` to `token_col <= range_end` |
| `src/ir/parser.py:~2590` | Same change in section-based table parsing path |
