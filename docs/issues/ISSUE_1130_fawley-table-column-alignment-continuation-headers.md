# fawley: Table Column Alignment Bug — Section-Based Path Missing Continuation Offsets

**GitHub Issue:** [#1130](https://github.com/jeffreyhorn/nlp2mcp/issues/1130)
**Status:** OPEN
**Severity:** High — model generates MCP but GAMS aborts with EXECERROR=1 (UNDF propagation)
**Date:** 2026-03-22
**Affected Models:** fawley (and potentially any model with continuation tables + secondary headers)

---

## Problem Summary

The fawley model (`data/gamslib/raw/fawley.gms`) generates an MCP file, but the `ap(c,p)`
parameter table has incorrect column assignments. Specifically, `brega.'d-brega' = -1` in
the original is emitted as `brega.'d-arab-h' = -1` — the value is assigned to the wrong
column. This causes a division-by-zero cascade:

1. `bp(k,p)$(kuse(k,p)) = 1 / sum(c$(ap(c,p) < 0), ...)` — the `sum` evaluates to 0
   for `(pipestill, d-brega)` because no crude has `ap(c, d-brega) < 0` (the brega entry
   was misplaced to `d-arab-h`)
2. `bp(pipestill, d-brega)` becomes UNDF
3. UNDF propagates into `kbal(pipestill)` and `stat_z(d-brega)` equations
4. GAMS aborts the SOLVE with `EXECERROR = 1`

---

## Reproduction

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/fawley.gms -o /tmp/fawley_mcp.gms

# Verify the misaligned data (should be brega.'d-brega' -1, not brega.'d-arab-h' -1)
grep "brega\.'d-" /tmp/fawley_mcp.gms
# Output: brega.'d-arab-h' -1  ← WRONG

# Run GAMS
gams /tmp/fawley_mcp.gms lo=2
# Expected: EXECERROR = 1, UNDF in stat_z(d-brega) and kbal(pipestill)
```

---

## GAMS Error Output

```
**** Exec Error at line 77: division by zero (0)

**** Evaluation error(s) in equation "stat_z(d-brega)"
stat_z(d-brega)..  0.045*nu_mbal(lv-naphtha) + 0.43*nu_mbal(v-heat-oil) +
  0.135*nu_mbal(iv-naphtha) + 0.28*nu_mbal(vacuum-dst) + 0.1*nu_mbal(res-brega)
  + UNDF*nu_kbal(pipestill) - piL_z(d-brega) =E= UNDF ; (LHS = UNDF)

**** Evaluation error(s) in equation "kbal(pipestill)"
kbal(pipestill)..  - 1.165*z(d-arab-l) - 0.585*z(d-arab-h) + UNDF*z(d-brega)
  + cap(pipestill) =E= UNDF ; (LHS = UNDF)

**** SOLVE from line 338 ABORTED, EXECERROR = 1
```

---

## Root Cause

### The Original Table

In fawley.gms, the `ap(c,p)` table uses continuation lines (the `+` character):

```gams
Table ap(c,p)  'process yields  (proportion weight of crude feed)'
               d-arab-l  d-arab-h  d-brega   reform   ho-low-s   ...

   arabian-l     -1.0
   arabian-h               -1.0
   brega                            -1.0
   ...

+              ho-high-s  vd-low-s  vd-high-s
   ...
```

The `brega` row has `-1.0` positioned under the third column `d-brega`.

### The Bug: Section-Based Path Missing `continuation_col_offsets`

The table has both a continuation (`+`) and secondary column headers, triggering the
**section-based processing path** in `_handle_table_block()`. The bug is at two locations:

**1. `src/ir/parser.py` lines 2550-2551** — `_merge_dotted_col_headers()` is called
WITHOUT `continuation_col_offsets`:

```python
# Section-based path (BUGGY):
sec_col_headers = _merge_dotted_col_headers(
    sec_hdr_tokens, source_lines=source_lines
)
# Missing: continuation_col_offsets=continuation_col_offsets
```

Compare with the **correct** non-section path at lines 2648-2651:
```python
# Non-section path (CORRECT):
col_headers = _merge_dotted_col_headers(
    col_tokens, source_lines=source_lines,
    continuation_col_offsets=continuation_col_offsets,
)
```

**2. `src/ir/parser.py` line 2589** — Data value column positions are not adjusted by
`continuation_col_offsets` in the section-based path, unlike the non-section path at
lines 2755-2756.

### Consequence

When continuation tokens from line 112 (`ho-high-s`, `vd-low-s`, `vd-high-s`) are merged
into the header line without position adjustment, the section-based code sees 8 column
headers instead of the correct 3 for the first section. The gap-midpoint column matching
algorithm uses incorrect range boundaries, causing the data value at the `d-brega` column
position to be matched to `d-arab-h` instead.

---

## Suggested Fix

1. Pass `continuation_col_offsets=continuation_col_offsets` to `_merge_dotted_col_headers()`
   at line 2550
2. Apply `continuation_col_offsets` to data value column positions in the section-based
   matching loop around line 2589
3. Alternatively, filter `sec_hdr_tokens` to exclude continuation tokens before processing
   each section (since sections already partition the data by continuation boundaries)

---

## Verification Plan

After fix:
```bash
python -m src.cli data/gamslib/raw/fawley.gms -o /tmp/fawley_mcp.gms
grep "brega\.'d-" /tmp/fawley_mcp.gms
# Should output: brega.'d-brega' -1

gams /tmp/fawley_mcp.gms lo=2
# Should: no UNDF, SOLVE proceeds (PATH solver runs)
```

---

## Files to Modify

| File | Line | Change |
|------|------|--------|
| `src/ir/parser.py` | 2550-2551 | Pass `continuation_col_offsets` to `_merge_dotted_col_headers` |
| `src/ir/parser.py` | ~2589 | Apply `continuation_col_offsets` to data value positions |

---

## Related

- The `execError = 0;` safeguard added in Sprint 23 Day 1 (PR #1129) clears the division-
  by-zero error counter, but UNDF still propagates into equations making SOLVE abort.
  The safeguard is useful for other models but does not fix fawley.
