# UIMP MCP: Objective Mismatch — Dollar Condition Used as Multiplier Instead of Boolean

**GitHub Issue:** [#1077](https://github.com/jeffreyhorn/nlp2mcp/issues/1077)
**Status:** RESOLVED
**Severity:** Medium — MCP solves (STATUS 1 Optimal) but objective is wrong
**Resolution:** Fixed `_ensure_numeric_condition()` in `src/ad/derivative_rules.py` to wrap ALL
non-trivial conditions as `1$cond`, not just `SetMembershipTest`. Now emits `1$(mh(l,k))`
instead of `mh(l,k)` as a multiplicative factor.
**Date:** 2026-03-13
**Affected Models:** uimp

---

## Problem Summary

The uimp model generates an MCP that solves optimally, but the objective value is wrong:

```
MCP objective (profit):  1478.857
NLP reference (profit):  1571.048
Error:                   -92.19 (5.9% low)
```

The root cause is that `_ensure_numeric_condition()` in `src/ad/derivative_rules.py` returns
parameter-valued dollar conditions as multiplicative coefficients instead of converting them
to 0/1 boolean indicators.

---

## Reproduction

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/uimp.gms -o /tmp/uimp_mcp.gms

# Run GAMS
gams /tmp/uimp_mcp.gms lo=2

# Expected: MODEL STATUS 1, obj ≈ 1571.048
# Actual:   MODEL STATUS 1, obj = 1478.857
```

---

## Root Cause

### The Equation

```gams
ib(i,k).. sum((j,l)$mh(l,k), x(i,j,k,l)) + y(i-1,k) =E= z(i,k) + y(i,k);
```

The dollar condition `$mh(l,k)` is a **boolean filter** in GAMS: nonzero values include the
term, zero values exclude it. The actual value of `mh(l,k)` (e.g., 4, 7, 6, 3) should NOT
be used as a coefficient.

### What Happens During AD

When differentiating `ib` w.r.t. `x(i,j,k,l)`, the sum collapses via partial index matching:

1. `d/dx(i,j,k,l) [ sum((j,l)$mh(l,k), x(i,j,k,l)) ]`
2. Sum collapses → derivative = `1`, dollar condition `mh(l,k)` is preserved
3. `_ensure_numeric_condition(mh(l,k))` returns `mh(l,k)` as-is (ParamRef, not SetMembershipTest)
4. Result: `1 * mh(l,k)` = `mh(l,k)` (values like 4, 7, 6, 3)

The correct result should be: `1 * (1$mh(l,k))` = 0 or 1

### The Buggy Function

```python
# src/ad/derivative_rules.py, line 1509
def _ensure_numeric_condition(cond: Expr) -> Expr:
    if isinstance(cond, SetMembershipTest):
        return DollarConditional(Const(1.0), cond)
    return cond  # BUG: returns ParamRef as-is, using value instead of 0/1
```

This function was introduced in Issue #730 to handle `SetMembershipTest` conditions, but
it only wraps set membership tests as `1$cond`. For `ParamRef` conditions (like `mh(l,k)`),
it returns the raw parameter, causing the parameter VALUE to be used as a multiplier
instead of a boolean indicator.

### The Stationarity Equation (Wrong)

```gams
stat_x(i,j,k,l).. (-c(i,j,k,l)) * nu_cdef + mh(l,k) * nu_ib(i,k)
  + t(i,j,k,l) * lam_ma(i,j,l) - piL_x(i,j,k,l) =E= 0;
```

### The Correct Stationarity Equation

```gams
stat_x(i,j,k,l).. (-c(i,j,k,l)) * nu_cdef + (1$mh(l,k)) * nu_ib(i,k)
  + t(i,j,k,l) * lam_ma(i,j,l) - piL_x(i,j,k,l) =E= 0;
```

---

## Suggested Fix

Modify `_ensure_numeric_condition()` to wrap ALL non-trivial conditions as
`DollarConditional(Const(1.0), cond)`, not just `SetMembershipTest`:

```python
def _ensure_numeric_condition(cond: Expr) -> Expr:
    """Convert a dollar condition to a numeric 0/1 indicator.

    All GAMS dollar conditions are boolean: nonzero → include (1), zero → exclude (0).
    When a sum collapses and the condition becomes a multiplicative factor, we must
    ensure proper 0/1 semantics by wrapping as DollarConditional(1, cond) → emits "1$cond".
    """
    if isinstance(cond, Const):
        # Numeric constants can be used directly (already 0 or nonzero)
        return Const(1.0) if cond.value != 0 else Const(0.0)
    return DollarConditional(Const(1.0), cond)
```

This is called at three sites in `_diff_sum()` (lines ~1607, ~1644, ~1890).

**Caution**: Verify that existing models using `SetMembershipTest` conditions still work
correctly after the change (the wrapping behavior for those is preserved).

---

## Files to Modify

| File | Change |
|------|--------|
| `src/ad/derivative_rules.py:1509-1521` | Fix `_ensure_numeric_condition()` to wrap all conditions |

## Verification

1. `make test` — all tests pass
2. Smoke-test uimp: `python -m src.cli data/gamslib/raw/uimp.gms -o /tmp/uimp_mcp.gms`
3. GAMS solve: obj should be ≈ 1571.048 (matching NLP reference)
4. Check that other models with dollar conditions in sums are not regressed
