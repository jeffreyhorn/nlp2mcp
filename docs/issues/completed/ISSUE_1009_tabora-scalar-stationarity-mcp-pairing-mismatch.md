# tabora: Scalar-Unrolled Stationarity Equations Paired with Indexed Variable

**GitHub Issue:** [#1009](https://github.com/jeffreyhorn/nlp2mcp/issues/1009)
**Status:** FIXED
**Model:** tabora (GAMSlib)
**Error category:** `gams_compilation_error`
**GAMS error:** `$70` — The dimensions of the equ.var pair do not conform

## Description

The `tabora` model has an indexed variable `mat(t)` with 30 elements (y01-y30). The variable has a single per-element upper bound: `mat.up("y01") = tob`.

The MCP emitter creates 30 scalar stationarity equations (`stat_mat_y01`, `stat_mat_y02`, ..., `stat_mat_y30`) instead of one indexed equation `stat_mat(t)`. Each scalar equation is then paired with the indexed variable `mat(t)` in the MCP model statement, producing 30 instances of GAMS Error $70 (dimension mismatch).

This is the same root cause as issue #903 (launch model).

## Fix Applied

Same fix as #1008. Eliminated per-instance scalar unrolling for non-uniform bounds. All stationarity, complementarity, and bound multiplier equations now remain indexed, with per-element bound values encoded via indexed GAMS parameters.

See [ISSUE_1008](ISSUE_1008_paklive-scalar-stationarity-mcp-pairing-mismatch.md) for full implementation details.

### Verification

- All 3961 tests pass
- Quality gate: typecheck, lint, format all pass

## Related Issues

- #903 — Same root cause (launch model: scalar-indexed MCP pairing mismatch)
- #1008 — Same root cause (paklive model)
