# twocge: Explicit Zeros in Parameter Emission Destroy GAMS Sparse Semantics

**GitHub Issue:** [#967](https://github.com/jeffreyhorn/nlp2mcp/issues/967)
**Status:** RESOLVED
**Model:** twocge (GAMSlib)

## Description

The twocge MCP emits parameter data (particularly the `SAM(u,v,r)` table) with
**explicit zero values** for entries that were blank/sparse in the original model.
GAMS treats unassigned parameter elements as zero but skips them during division
operations (sparse semantics). When the emitter writes explicit `0` entries, these
sparse semantics are lost.

## Root Cause

Investigation revealed **two distinct issues**, both now resolved:

### Issue A: Explicit zeros in parameter emission (FIXED — PR #969)

The emitter serialized zero-valued inline parameter data entries. Fixed by skipping
`value == 0` entries in `emit_original_parameters()` in `src/emit/original_symbols.py`.
This preserves GAMS sparse semantics for all models.

### Issue B: Table parser produces wrong data for multi-region continuation sections (FIXED — #968)

The table parser's secondary header detection only recognized all-NUMBER continuation
lines, missing dotted ID column headers like `BRD.USA MLK.USA`. USA data was stored
under JPN keys, overwriting JPN values. Fixed by extending secondary header detection
to all-ID/STRING lines in `_handle_table_block()`.

## Fixes Applied

1. **Zero-filtering** (PR #969, merged): Skip zero-valued entries in
   `src/emit/original_symbols.py` to preserve GAMS sparse semantics.

2. **Table continuation** (#968, this branch): Extend secondary header detection
   in `src/ir/parser.py::_handle_table_block()` to recognize dotted column headers.

Both fixes together resolve all 28 EXECERROR errors for twocge.

## Related Issues

- [#901](https://github.com/jeffreyhorn/nlp2mcp/issues/901) — twocge dotted table column headers (RESOLVED)
- [#968](https://github.com/jeffreyhorn/nlp2mcp/issues/968) — Table continuation overwrite (RESOLVED)
- [#970](https://github.com/jeffreyhorn/nlp2mcp/issues/970) — twocge MCP locally infeasible (OPEN)
