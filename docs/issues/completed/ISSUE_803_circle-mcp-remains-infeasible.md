# ISSUE #803: Circle MCP Remains Infeasible Despite .l Initialization

**GitHub Issue**: https://github.com/jeffreyhorn/nlp2mcp/issues/803
**Status**: FIXED
**Created**: 2026-02-20
**Fixed**: 2026-02-21
**Epic**: Epic 4 - GAMSlib Catalog Expansion
**Priority**: Medium

## Problem

After implementing expression-based `.l` initialization emission (Sprint 20 Days 1-2), circle.gms still fails to solve with PATH solver returning model_status=5 (Locally Infeasible). The `.l` initialization expressions are correctly captured in the IR and emitted in the MCP output, but this does not resolve the infeasibility.

## Root Cause

**Double negation bug in scalar stationarity equation assembly.**

The KKT stationarity code had two paths for adding Jacobian transpose terms:

1. **Indexed variables** (`_add_indexed_jacobian_terms`): Always used `Binary("+", expr, term)` — correct.
2. **Scalar variables** (`_add_jacobian_transpose_terms_scalar`): Used `Binary("-", expr, term)` when the constraint was negated for MCP form — **incorrect double negation**.

The chain of negations:
- `src/kkt/complementarity.py` lines 96-100: LE constraints are negated for MCP form (`F_lam = -g(x)`, `negated=True`)
- `src/ad/constraint_jacobian.py` lines 470-510: The Jacobian always computes `∂g/∂x` from the **original** constraint (not the MCP form)
- `src/kkt/stationarity.py` lines 1740-1743: When `negated=True`, the code subtracted the Jacobian term: `expr = Binary("-", expr, term)`

This created a double negation: the Jacobian was of the original form `∂g/∂x`, but the stationarity code treated it as if it were the negated MCP form `∂(-g)/∂x` and subtracted it (effectively adding `+∂g/∂x`... wait, no, it subtracted `∂g/∂x`, giving the wrong sign).

The correct KKT stationarity is always `∇f + λᵀ∇g = 0`, regardless of how the complementarity pair is expressed. The negation in complementarity is for the MCP equation form, not for the stationarity contribution.

### Generated MCP Before Fix

```gams
stat_a.. ((-1) * sum(i, 2 * (x(i) - a) * (-1) * lam_e(i))) =E= 0;
stat_r.. 1 - sum(i, ((-1) * (2 * r)) * lam_e(i)) - piL_r =E= 0;
```

The outer `(-1)` and the subtraction of the sum are the spurious double negation.

### Generated MCP After Fix

```gams
stat_a.. sum(i, 2 * (x(i) - a) * (-1) * lam_e(i)) =E= 0;
stat_r.. 1 + sum(i, ((-1) * (2 * r)) * lam_e(i)) - piL_r =E= 0;
```

No spurious outer negation. The `(-1)` inside the derivative is the correct `∂g/∂a = -2(x(i)-a)`.

## Fix

**File**: `src/kkt/stationarity.py`

Removed the `negate` flag logic from `_add_jacobian_transpose_terms_scalar`. The function now always uses `Binary("+", expr, term)` to add Jacobian transpose terms, consistent with the indexed variable path (`_add_indexed_jacobian_terms`).

Changes:
1. Removed `negate` variable computation (lines 1680-1684)
2. Changed `if negate: expr = Binary("-", ...) else: expr = Binary("+", ...)` to always `expr = Binary("+", expr, term)` (line 1740)
3. Removed outdated docstring about negation

## Verification

- circle.gms: PATH solver returns model_status=1 (Optimal), objective=4.071
- port.gms: Also fixed by this change — PATH solver returns model_status=1 (Optimal), objective=0.298
- All 110 translated models retranslate successfully
- Solve count increased from 29 to 31 (circle + port now solving)
- No regressions: all 29 previously-solving models continue to solve
- All 3701 unit tests pass

## Related Issues

- Closes #753 (original issue, which focused on `.l` initialization)
- Sprint 20 Day 2 PR #802 (completed `.l` emission feature)
