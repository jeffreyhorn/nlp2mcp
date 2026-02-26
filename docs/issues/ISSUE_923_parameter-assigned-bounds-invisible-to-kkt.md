# Parameter-Assigned Bounds (lo_expr_map) Invisible to KKT Pipeline

**GitHub Issue:** #923 (https://github.com/jeffreyhorn/nlp2mcp/issues/923)
**Models:** sparta, aircraft (and any model with parameter-expression bounds)
**Category:** match_mismatch (LP models solve but don't match NLP objective)
**Severity:** KKT system incomplete — missing bound multipliers for expression-based bounds
**Sprint:** 21, Day 9

## Problem

When a variable bound is assigned via a parameter expression (e.g., `e.lo(t) = req(t)`), the parser stores the RHS in `var_def.lo_expr_map` because `req(t)` cannot be reduced to a constant. However, the KKT partitioner (`partition_constraints()`) only reads `var_def.lo` and `var_def.lo_map` (numeric storage), ignoring `lo_expr_map` entirely.

The result: no bound multiplier variable (`piL_e(t)`), no complementarity equation (`comp_lo_e(t)`), and no `piL_e(t)` term in the stationarity equation. The KKT system is incomplete.

Note: the emitter *does* correctly emit `e.lo(t) = req(t)` in the Variable Bounds section of the MCP file. The gap is only in the KKT formulation.

## Root Cause

**Parser** (`src/ir/parser.py`): When processing `e.lo(t) = req(t)`, the RHS is a `ParamRef` expression. Since it's not a numeric constant, it goes to `var_def.lo_expr_map` (not `var_def.lo_map`).

**VariableDef fields** (`src/ir/symbols.py`, lines 107–110):
```python
lo_expr: Expr | None = None
lo_expr_map: dict[tuple[str | IndexOffset | SubsetIndex, ...], Expr] = field(default_factory=dict)
```

**Partitioner** (`src/kkt/partition.py`, line 139):
```python
_process_indexed_bounds(
    bound_map=var_def.lo_map,        # ← reads lo_map, NOT lo_expr_map
    ...
)
```

`var_def.lo_map` is empty for `e.lo(t) = req(t)`, so `_process_indexed_bounds()` returns immediately (line 198: `if not bound_map: return`). The `lo_expr_map` is never consulted.

**Grep confirms**: `lo_expr` and `lo_expr_map` appear only in `src/ir/symbols.py` (field definitions) and `src/emit/emit_gams.py` (emitter). Zero references in `src/kkt/`.

## Reproduction

```bash
# sparta: 21.7% objective mismatch despite being verified_convex LP
python src/cli.py data/gamslib/raw/sparta.gms -o /tmp/sparta_mcp.gms

# The bound is emitted correctly:
grep 'e.lo' /tmp/sparta_mcp.gms
# e.lo(t) = req(t);

# But no bound multiplier or complementarity:
grep 'piL_e\|comp_lo_e' /tmp/sparta_mcp.gms
# (no output)
```

## Affected Models

| Model | Type | Rel Diff | Bound Type |
|-------|------|----------|-----------|
| sparta | LP (verified_convex) | 21.7% | `e.lo(t) = req(t)` — parameter-assigned lower bound |
| aircraft | LP (verified_convex) | 78.6% | Possible parameter-assigned bounds (needs verification) |
| Any model with `.lo`/`.up`/`.fx` assigned via parameter expressions | Various | Various | Expression-based bounds |

## Recommended Fix

This requires changes across the KKT pipeline:

1. **`src/kkt/partition.py`** — After processing `lo_map`, also process `lo_expr_map`. For each entry in `lo_expr_map`, generate a `BoundDef` entry. This requires either:
   - Extending `BoundDef` to hold an `Expr` (alongside or instead of a numeric `value`)
   - Using a sentinel value (e.g., `float("nan")`) and carrying the expression separately

2. **`src/kkt/complementarity.py`** — The complementarity equation builder must emit `e(t) - req(t) >=G= 0` (using the expression) rather than `e(t) - <constant> >=G= 0`.

3. **`src/kkt/assemble.py`** — The stationarity assembly must add `- piL_e(t)` to `stat_e(t)`.

Same pattern needed for `up_expr_map` and `fx_expr_map`.

## Files to Modify

| File | Change |
|------|--------|
| `src/kkt/partition.py` | Process `lo_expr_map`/`up_expr_map` in `partition_constraints()` |
| `src/ir/symbols.py` | Possibly extend `BoundDef` to hold `Expr` for expression bounds |
| `src/kkt/complementarity.py` | Generate complementarity equations with expression RHS |
| `src/kkt/assemble.py` | Ensure stationarity includes bound multiplier terms for expr bounds |

## Estimated Effort

~4-5h (cross-cutting change across 3-4 files in the KKT pipeline)
