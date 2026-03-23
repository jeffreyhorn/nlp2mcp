# himmel16: Cyclic Offset Alias Gradient Mismatch

**GitHub Issue:** [#1146](https://github.com/jeffreyhorn/nlp2mcp/issues/1146)
**Status:** OPEN
**Severity:** High — objective mismatch (43.0%)
**Date:** 2026-03-23
**Parent Issue:** #1111 (Alias-Aware Differentiation)
**Affected Models:** himmel16

---

## Problem Summary

The himmel16 model (Himmelblau Problem 16) uses `Alias(i, j)` with cyclic
offset patterns where aliased indices wrap around the set boundary. The
large mismatch (43.0%) indicates significant gradient errors.

| Model | NLP Objective | MCP Objective | Rel Diff |
|-------|--------------|--------------|----------|
| himmel16 | 0.675 | 0.385 | 43.0% |

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/himmel16.gms -o /tmp/himmel16_mcp.gms
gams /tmp/himmel16_mcp.gms lo=2
# Objective: ~0.385, expected: ~0.675
```

---

## Root Cause Analysis

The himmel16 model uses:

```gams
Alias(i, j);
```

With cyclic offset patterns where variables at position `i` interact with
variables at position `i+1` (or `j` where `j` is the successor of `i`).
The cyclic (modular) wrapping at the boundary of the set creates additional
complexity.

### Potential Issues

1. **Cyclic IndexOffset handling**: The `circular=True` flag on IndexOffset
   nodes requires special handling in `_partial_collapse_sum` to correctly
   identify which element wraps around.

2. **Alias + offset combination**: When the alias `j` is combined with an
   offset like `i+1`, the AD engine must resolve both the alias relationship
   and the offset, which may not compose correctly.

3. **Index substitution for cyclic references**: After sum collapse, the
   `_apply_index_substitution` may not correctly handle the modular arithmetic
   needed for cyclic offsets.

### Investigation Steps

1. Generate the MCP and inspect stationarity equations
2. Identify the specific cyclic offset pattern in the equations
3. Check if `IndexOffset` with `circular=True` is correctly handled
4. Compare with hand-derived KKT conditions
5. Test if the polygon fix (if implemented) also helps himmel16

---

## Files

- `src/ad/derivative_rules.py` — `_partial_collapse_sum`, `_diff_varref`
- `src/kkt/stationarity.py` — `_replace_indices_in_expr`
- `data/gamslib/raw/himmel16.gms` — Source model
