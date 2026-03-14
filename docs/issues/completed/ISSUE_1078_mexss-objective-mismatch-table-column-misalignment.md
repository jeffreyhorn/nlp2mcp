# MEXSS MCP: Objective Mismatch — Table Column Misalignment in `a(c,p)` Matrix

**GitHub Issue:** [#1078](https://github.com/jeffreyhorn/nlp2mcp/issues/1078)
**Status:** RESOLVED
**Severity:** Medium — MCP solves (STATUS 1 Optimal) but objective is wrong
**Resolution:** Fixed by PR #1079 (table column misalignment fix using gap-midpoint matching).
After fix, MCP objective = 538.811, matching NLP reference exactly.
**Date:** 2026-03-13
**Affected Models:** mexss
**Related:** #1074 (ibm1 table column misalignment — same parser bug class)

---

## Problem Summary

The mexss model generates an MCP that solves optimally, but the objective value is wrong:

```
MCP objective (phi):  506.808
NLP reference (phi):  538.811
Error:                -32.0 (5.9% low)
```

The root cause is that the table parser misaligns values in the `a(c,p)` input-output
coefficients table, placing values one column to the left of their correct position in
rows with leading blank columns.

---

## Reproduction

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/mexss.gms -o /tmp/mexss_mcp.gms

# Run GAMS
gams /tmp/mexss_mcp.gms lo=2

# Expected: MODEL STATUS 1, obj ≈ 538.811
# Actual:   MODEL STATUS 1, obj = 506.808
```

---

## Root Cause

### The Table

```gams
Table a(c,p) 'input-output coefficients'
                      pellet-dr  pellet-hyl  nat-gas-dr  nat-gas-hyl  electric
   iron-ore            -1.58      -1.38
   ite                                                                    1
   pel-dr               1          1
   cite                                                                   1
   ...
   scrap                                       -0.33                   -0.12
   sponge                          -1.09
   ...
```

### Misaligned Values

**Row `scrap`:**
| Column | Correct Value | Parsed Value |
|--------|--------------|-------------|
| `nat-gas-dr` | -0.33 | -0.33 (OK) |
| `steel-el` | 0 | **-0.12** (WRONG — shifted left) |
| `steel-bof` | -0.12 | 0 (WRONG — value was shifted left) |

**Row `sponge`:**
| Column | Correct Value | Parsed Value |
|--------|--------------|-------------|
| `pellet-hyl` | -1.09 | 0 (WRONG — value was shifted left) |
| `steel-oh` | 0 | **-1.09** (WRONG — shifted left) |

Both values are shifted one column to the left. This happens in rows with leading blank
columns followed by values at non-contiguous column positions.

### Impact

- `scrap.steel-bof = -0.12` becomes `scrap.steel-el = -0.12`: changes which steel process
  requires scrap input
- `sponge.pellet-hyl = -1.09` becomes `sponge.steel-oh = -1.09`: changes which process
  requires sponge iron

This fundamentally alters the production technology structure, changing optimal process
selection and resulting in a different (lower) objective value.

---

## Suggested Fix

This is the same bug class as #1074 (ibm1 table column misalignment). The table parser's
non-section path uses **sequential column assignment** as a fallback when distance-based
matching fails, causing values to be assigned to the next unused column rather than the
closest column by character position.

The fix from #1074 should also resolve this issue: use the **distance-based fallback**
from the section-based table parsing path (parser.py lines ~2582-2597) in the non-section
path (parser.py lines ~2758-2764).

```python
# Current (WRONG): sequential assignment
if best_match is None:
    for col_name, _ in col_headers:
        if col_name not in used_columns:
            best_match = col_name
            break

# Correct: distance-based assignment (from section path)
if best_match is None and col_headers:
    best_distance = math.inf
    best_idx = None
    for fidx, (col_label, col_pos) in enumerate(col_headers):
        if col_label in used_columns:
            continue
        distance = abs((col_pos or 0) - val_col)
        if best_idx is None or distance < best_distance:
            best_distance = distance
            best_idx = fidx
    if best_idx is not None:
        best_match = col_headers[best_idx][0]
```

---

## Files to Modify

| File | Change |
|------|--------|
| `src/ir/parser.py:~2758-2764` | Replace sequential fallback with distance-based fallback |

## Verification

1. `make test` — all tests pass
2. Smoke-test mexss: `python -m src.cli data/gamslib/raw/mexss.gms -o /tmp/mexss_mcp.gms`
3. GAMS solve: obj should be ≈ 538.811 (matching NLP reference)
4. Also verify ibm1 (#1074) is fixed by the same change
