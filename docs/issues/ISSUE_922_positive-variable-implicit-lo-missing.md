# Positive Variable Implicit lo=0 Not Propagated to KKT Partition

**GitHub Issue:** #922 (https://github.com/jeffreyhorn/nlp2mcp/issues/922)
**Models:** apl1p, apl1pca (and any model with `Positive Variable` declarations)
**Category:** match_mismatch (LP models solve but don't match NLP objective)
**Severity:** KKT system incomplete — missing non-negativity bound multipliers
**Sprint:** 21, Day 9

## Problem

In GAMS, `Positive Variable x` implicitly means `x.lo = 0`. However, the parser creates `VariableDef(kind=VarKind.POSITIVE)` without setting `lo=0.0`. The KKT partitioner (`partition_constraints()`) only checks `var_def.lo` (which is `None`) and skips generating lower-bound multiplier variables (`piL_x`) and complementarity equations (`comp_lo_x`).

For LP models, these bound multipliers are exactly the reduced costs (shadow prices on non-negativity constraints). Without them, the stationarity conditions don't hold at the LP optimum, causing the MCP solution to diverge.

## Root Cause

**Parser** (`src/ir/parser.py`, lines 2761–2770): Sets `kind=VarKind.POSITIVE` via `_VAR_KIND_MAP` but never sets `var_def.lo = 0.0`.

**Partitioner** (`src/kkt/partition.py`, line 119):
```python
if var_def.lo is not None:          # ← lo is None for Positive vars → skipped
    if var_def.lo == float("-inf"):
        result.skipped_infinite.append(...)
    else:
        result.bounds_lo[...] = BoundDef("lo", var_def.lo, var_def.domain)
```

Since `var_def.lo is None`, the implicit `lo=0` of a Positive Variable is never added to `result.bounds_lo`.

**Impact on emitted MCP**: The stationarity equations (e.g., `stat_x(g)`, `stat_y(g,dl)`, `stat_s(dl)`) have no `- piL_x(g)` terms. No `comp_lo_x` complementarity equations are generated. The KKT system is under-constrained for these variables.

## Reproduction

```bash
# apl1p: 3.3% objective mismatch despite being verified_convex LP
python src/cli.py data/gamslib/raw/apl1p.gms -o /tmp/apl1p_mcp.gms
grep 'piL_x\|comp_lo_x\|piL_y\|piL_s' /tmp/apl1p_mcp.gms
# Expected: piL variables and comp_lo equations
# Actual: none found
```

## Affected Models

| Model | Type | Rel Diff | Variables Missing piL |
|-------|------|----------|----------------------|
| apl1p | LP (verified_convex) | 3.3% | x(g), y(g,dl), s(dl) |
| apl1pca | LP (verified_convex) | 32.9% | Same as apl1p (variant) |
| Any model with `Positive Variable` | Various | Various | All positive vars without explicit `.lo` |

## Recommended Fix

**Option A (preferred — single-point fix in partition.py):**

After the `if var_def.lo is not None:` block (line 123), add:
```python
elif var_def.kind == VarKind.POSITIVE and (var_name, ()) not in result.bounds_lo:
    result.bounds_lo[(var_name, ())] = BoundDef("lo", 0.0, var_def.domain)
```

Requires importing `VarKind` in `partition.py`.

**Option B (fix in parser):** Set `var_def.lo = 0.0` when `kind == VarKind.POSITIVE` in `add_var()`. This makes existing partition logic work automatically.

Also need to handle `Negative Variable` (implicit `up=0`) and `Binary Variable` (implicit `lo=0`, `up=1`) similarly.

## Files to Modify

| File | Change |
|------|--------|
| `src/kkt/partition.py` | Add `VarKind.POSITIVE` check after line 123 to synthesize lo=0 bound entries |
| OR `src/ir/parser.py` | Set `lo=0.0` in `add_var()` when kind is POSITIVE |

## Estimated Effort

~2h (including tests and pipeline retest for apl1p, apl1pca)
