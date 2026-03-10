# spatequ: Jacobian Domain Mismatch in Stationarity Equations

**GitHub Issue:** [#1038](https://github.com/jeffreyhorn/nlp2mcp/issues/1038)
**Status:** OPEN
**Severity:** High — produces incorrect KKT system, model infeasible
**Date:** 2026-03-10
**Affected Models:** spatequ (and potentially any model where equation and variable domains differ)

---

## Problem Summary

When a variable with domain `(r,c)` appears inside a `sum()` over a different index in an equation with domain `(r,c)`, the Jacobian derivative w.r.t. that variable is incorrectly emitted as a sum over all equation instances instead of matching the correct index pair.

This produces stationarity equations like:

```gams
stat_qs(r,c).. ... + sum((R,C), (-1) * nu_SX(R,C)) =E= 0;
```

when the correct form should be:

```gams
stat_qs(r,c).. ... + (-1) * nu_SX(r,c) =E= 0;
```

Additionally, `stat_x(r,rr,c)` is missing the `nu_SX(r,c)` contribution entirely, and the `nu_DX` term may have incorrect index binding.

---

## Error Details

Generated stationarity equations (incorrect):
```
stat_qs(r,c).. ((-1) * nu_SUP(r,c)) - nu_SDBAL(c) + sum((r__,c__), (-1) * nu_SX(r__,c__)) =E= 0;
stat_x(r,rr,c).. ((-1) * TCost(r,rr,c)) * nu_TRANSCOST + nu_DX(r,c) - piL_x(r,rr,c) =E= 0;
```

Expected stationarity equations:
```
stat_qs(r,c).. ((-1) * nu_SUP(r,c)) - nu_SDBAL(c) - nu_SX(r,c) =E= 0;
stat_x(r,rr,c).. ((-1) * TCost(r,rr,c)) * nu_TRANSCOST + nu_SX(r,c) + nu_DX(rr,c) - piL_x(r,rr,c) =E= 0;
```

PATH solver result: Model Status 5 (Locally Infeasible) with 85 infeasible equations.

---

## Root Cause

The equations `SX` and `DX` involve variables with mismatched dimensionality:

```gams
SX(R,C)..      sum(RR, X(R,RR,C))  =e= Qs(R,C);
DX(r,c)..      sum(rr, X(rr,r,c))  =e= Qd(r,c);
```

- `X(r,rr,c)` is 3-dimensional
- `Qs(r,c)` and `Qd(r,c)` are 2-dimensional

When computing `∂SX(R,C)/∂Qs(R,C)`, the derivative is `-1` but only for the matching `(R,C)` pair. The AD/Jacobian code appears to be producing a derivative entry that, when assembled into the stationarity equation for `Qs(r,c)`, sums over ALL `(R,C)` instances of SX instead of matching the correct pair.

Similarly, `∂SX(R,C)/∂X(R,RR,C) = 1` and `∂DX(r,c)/∂X(rr,r,c) = 1`, but the index binding in `stat_x` is incorrect — `nu_SX(r,c)` is missing and `nu_DX(r,c)` should be `nu_DX(rr,c)`.

The KKT assembly's `sum()` index binding needs to correctly map equation domain indices to the variable's domain indices when they have different dimensionality.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/spatequ.gms -o /tmp/spatequ_mcp.gms --skip-convexity-check

# Inspect stationarity equations:
grep "stat_qs\|stat_x" /tmp/spatequ_mcp.gms

# Expected: stat_qs should NOT have sum((r__,c__), ...)
# Expected: stat_x should include nu_SX(r,c) term

# Run GAMS:
gams /tmp/spatequ_mcp.gms lo=0 o=/tmp/spatequ_mcp.lst
grep 'MODEL STATUS' /tmp/spatequ_mcp.lst
# Result: MODEL STATUS 5 Locally Infeasible (85 infeasible equations)
```

---

## Suggested Fix

Investigate the KKT assembly code in `src/kkt/assemble.py` where stationarity equations are built from Jacobian entries. When a Jacobian entry `J[eq(R,C), var(R,C)]` has matching indices, the contribution to `stat_var(r,c)` should be a scalar multiplier reference `nu_eq(r,c)`, NOT a `Sum(...)` over all equation instances.

The issue likely stems from how `JacobianEntry` domain matching works when the equation domain `(R,C)` matches a subset of the variable domain or when the variable appears under a `sum()` in the equation body.

Key files to investigate:
- `src/kkt/assemble.py` — stationarity equation assembly
- `src/ad/constraint_jacobian.py` — Jacobian structure computation
- `src/ad/differentiate.py` — symbolic differentiation and domain tracking

---

## Prerequisite

Issue #1026 must be fixed first (model equation selection for MCP solves) to ensure the correct NLP model equations are used.

---

## Files Likely Affected

| File | Change |
|------|--------|
| `src/kkt/assemble.py` | Fix index matching when building stationarity from Jacobian |
| `src/ad/constraint_jacobian.py` | Verify domain tracking for mismatched-dimension entries |
| `src/ad/differentiate.py` | Check derivative domain propagation |

---

## Related Issues

- Issue #1026: spatequ uses wrong model equations (PREREQUISITE — being fixed in same PR)
