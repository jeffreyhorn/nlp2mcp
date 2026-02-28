# twocge: Explicit Zeros in Parameter Emission Destroy GAMS Sparse Semantics

**GitHub Issue:** [#967](https://github.com/jeffreyhorn/nlp2mcp/issues/967)
**Status:** PARTIALLY RESOLVED
**Model:** twocge (GAMSlib)
**Error category:** `gams_error` (EXECERROR = 28)
**GAMS errors:** `division by zero` (26 instances), `rPower: FUNC DOMAIN: x**y, x=0,y<0` (2 instances)

## Description

The twocge MCP emits parameter data (particularly the `SAM(u,v,r)` table) with
**explicit zero values** for entries that were blank/sparse in the original model.
GAMS treats unassigned parameter elements as zero but skips them during division
operations (sparse semantics). When the emitter writes explicit `0` entries, these
sparse semantics are lost.

## Root Cause (Updated 2026-02-28)

Investigation revealed **two distinct issues**:

### Issue A: Explicit zeros in parameter emission (FIXED)

The emitter serialized zero-valued inline parameter data entries. Fixed by skipping
`value == 0` entries in `emit_original_parameters()` in `src/emit/original_symbols.py`.
This preserves GAMS sparse semantics for all models.

### Issue B: Table parser produces wrong data for multi-region continuation sections (OPEN)

The `_merge_dotted_col_headers()` fix (Sprint 21 Day 7, commit 7f87431e) correctly
merges dotted column headers like `BRD.JPN` into compound headers. However, for
the 4-section SAM table:

```
Table SAM(u,v,r)
         BRD.JPN MLK.JPN ...    <-- section 1 (5 JPN columns)
   BRD        21      8
   +     TRF.JPN HOH.JPN ...    <-- section 2 (5 JPN columns)
   BRD                20
   +     BRD.USA MLK.USA ...    <-- section 3 (5 USA columns)
   BRD        40       1
   +     TRF.USA HOH.USA ...    <-- section 4 (5 USA columns)
   BRD                30
```

The parser produces 50 entries, all with `.JPN` keys. The USA data (sections 3-4)
is stored with JPN region keys, **overwriting** JPN values. For example:
- `('BRD', 'BRD.JPN')` = 40 (should be USA value 40, JPN value is 21)
- All USA entries are missing entirely

This means all derived parameters (`F0`, `M0`, etc.) for `r=USA` are zero/unassigned,
causing division-by-zero errors in calibration (lines 117-135) and post-solve
reporting (lines 306-331).

**The 28 execution errors are caused by Issue B, not Issue A.**

## Fix Applied

### Primary fix (Issue A): Skip zero-valued inline parameter data

In `src/emit/original_symbols.py` line ~808, added zero-value filtering:
```python
if isinstance(value, (int, float)) and value == 0:
    continue  # Preserve GAMS sparse semantics
```

This fix is correct and benefits all models, but does not reduce twocge's error count
because the root cause is Issue B.

## Remaining Work (Issue B)

The table parser bug where multi-region `+` continuation sections overwrite earlier
data needs a separate fix in `src/ir/parser.py::_handle_table_block()`. The
`_merge_dotted_col_headers()` function may be incorrectly reusing the first
section's column headers as a template.

See [#968](https://github.com/jeffreyhorn/nlp2mcp/issues/968) for the table parsing bug.

## Related Issues

- [#901](https://github.com/jeffreyhorn/nlp2mcp/issues/901) — twocge dotted table column headers (RESOLVED)
- [#923](https://github.com/jeffreyhorn/nlp2mcp/issues/923) — Parameter-assigned bounds invisible to KKT
- Table parser continuation section bug — new issue needed
