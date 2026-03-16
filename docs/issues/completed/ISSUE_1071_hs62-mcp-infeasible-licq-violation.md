# hs62: MCP Locally Infeasible — LICQ Violation from sqr Constraint

**GitHub Issue:** [#1071](https://github.com/jeffreyhorn/nlp2mcp/issues/1071)
**Status:** RESOLVED
**Model:** hs62 (SEQ=182) — Hock-Schittkowski Problem 62
**Type:** NLP
**Category:** KKT numerical conditioning (LICQ violation)
**Date:** 2026-03-14
**Resolved:** 2026-03-16 (Sprint 22 Day 12)

---

## Summary

The hs62 model was locally infeasible (model_status=5, 840 iterations) because the equality constraint `20*sqr(x1+x2+x3-1) = 0` had a vanishing gradient at the feasible point, violating LICQ.

---

## Resolution

Added a sqr equality reformulation pass that detects `c * sqr(expr) =E= 0` constraints and reformulates them to `expr =E= 0` before derivative computation.

1. **New module**: `src/kkt/sqr_reformulation.py` — `reformulate_sqr_equalities(model_ir)`
   - Detects `sqr(expr)`, `c * sqr(expr)`, or `sqr(expr) * c` on LHS with `0` on RHS
   - Replaces with inner expression, preserving all equation metadata
   - Also handles reversed case (0 on LHS, sqr on RHS)

2. **CLI integration**: `src/cli.py` — called after min/max reformulation, before derivatives
   - Re-normalizes model after reformulation so Jacobian uses simplified form
   - Added to both diagnostic and non-diagnostic code paths

3. **Effect on stationarity**: Multiplier term changes from `40*(x1+x2+x3-1)*nu_eq1` (vanishes at feasibility) to `nu_eq1` (constant coefficient 1).

### GAMS Verification
- **Before**: MODEL STATUS 5 (Locally Infeasible), 840 iterations, nu_eq1 ≈ 256048
- **After**: MODEL STATUS 1 (Optimal), objective = -26272.514 (matches NLP reference)

### Files Changed

| File | Change |
|------|--------|
| `src/kkt/sqr_reformulation.py` | New module: `reformulate_sqr_equalities()` |
| `src/cli.py` | Integrated reformulation pass into pipeline |
