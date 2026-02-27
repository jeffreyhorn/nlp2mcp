# Positive Variable Implicit lo=0 Not Propagated to KKT Partition

**GitHub Issue:** #922 (https://github.com/jeffreyhorn/nlp2mcp/issues/922)
**Status:** FIXED
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

## Resolution

**Fixed using Option A (partition.py).** Option B (fixing in `add_var()`) was initially attempted but caused regressions: setting `lo=0.0` on the VariableDef during parsing interfered with models that also set explicit indexed bounds (e.g., `x.lo(c) = 0.001` in `chem.gms`), causing the partitioner to generate per-instance stationarity equations instead of indexed ones.

### Changes Made

**`src/kkt/partition.py`:**
- Added `VarKind` to imports
- After processing explicit scalar/indexed bounds, added implicit bound synthesis:
  - `VarKind.POSITIVE`: adds `lo=0` if no explicit lo bound (scalar or indexed) exists
  - `VarKind.NEGATIVE`: adds `up=0` if no explicit up bound exists
  - `VarKind.BINARY`: adds `lo=0` and `up=1` if no explicit bounds exist
- Only synthesizes bounds when neither `var_def.lo`/`var_def.up` nor `lo_map`/`up_map` have entries, avoiding conflicts with models that set explicit bounds

### Verification

- All 3,815 tests pass, 10 skipped, 1 xfailed
- apl1p: MODEL STATUS 1 Optimal (piL_x, piL_y, piL_s now emitted)
- chem, hhmax: No regression (MODEL STATUS 1 Optimal)
