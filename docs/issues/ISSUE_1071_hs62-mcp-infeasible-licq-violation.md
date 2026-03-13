# hs62: MCP Locally Infeasible — LICQ Violation from sqr Constraint

**GitHub Issue:** [#1071](https://github.com/jeffreyhorn/nlp2mcp/issues/1071)
**Model:** hs62 (SEQ=182) — Hock-Schittkowski Problem 62
**Type:** NLP
**Category:** KKT numerical conditioning (LICQ violation)

---

## Summary

The hs62 model is locally infeasible (model_status=5, 840 iterations) because the equality constraint `20*sqr(x1+x2+x3-1) = 0` has a vanishing gradient at the feasible point, violating the Linear Independence Constraint Qualification (LICQ). The multiplier `nu_eq1` becomes structurally indeterminate in the KKT system.

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/hs62.gms -o data/gamslib/mcp/hs62_mcp.gms
cd /tmp && gams /path/to/data/gamslib/mcp/hs62_mcp.gms lo=2 o=hs62.lst
# Expected: MODEL STATUS 5 (Locally Infeasible), 840 iterations
```

## Model Structure

- **Variables**: `x1, x2, x3` (positive), `obj` (objective)
- **Objective**: Minimize a nonlinear function involving logarithms
- **Key constraint**: `eq1.. 20*sqr(x1 + x2 + x3 - 1) =E= 0`
- **Redundant constraint**: `eq1x.. x1 + x2 + x3 =E= 1` (linear version of the same constraint)
- **NLP reference**: obj = -26272.514

## Root Cause

### The LICQ Violation

The constraint `eq1: 20*sqr(x1 + x2 + x3 - 1) = 0` enforces `x1 + x2 + x3 = 1` via a squared penalty. At the feasible point:

**Constraint gradient**: `∇(20*sqr(expr)) = 40*(x1+x2+x3-1) * (1, 1, 1)`

At feasibility where `x1+x2+x3 = 1`: **gradient = (0, 0, 0)**

This is a classic LICQ violation — the constraint gradient vanishes at the feasible set, making the KKT multiplier `nu_eq1` indeterminate.

### Effect on Stationarity Equations

The stationarity equations contain terms like:
```gams
stat_x1.. ... + 40*(x1 + x2 + x3 - 1)*nu_eq1 + nu_eq1x - piL_x1 =E= 0;
stat_x2.. ... + 40*(x1 + x2 + x3 - 1)*nu_eq1 + nu_eq1x - piL_x2 =E= 0;
stat_x3.. ... + 40*(x1 + x2 + x3 - 1)*nu_eq1 + nu_eq1x - piL_x3 =E= 0;
```

At feasibility, the coefficient of `nu_eq1` vanishes (equals zero), so `nu_eq1` provides no information. PATH drives `nu_eq1` to extreme values (observed: 256048) trying to compensate, but cannot achieve stationarity.

### Near-Miss

PATH achieves a maximum residual of only 7.77e-06 — essentially a near-miss. The solution is very close to feasible but cannot be certified due to the degenerate constraint.

## PATH Solver Output

```
MODEL STATUS      5 Locally Infeasible
SOLVER STATUS     1 Normal Completion
840 iterations
Maximum residual: 7.77e-06
nu_eq1 ≈ 256048 (blown up due to LICQ violation)
```

## Fix Approach

1. **Constraint reformulation**: Detect `sqr(expr) = 0` constraints and reformulate as `expr = 0` before KKT generation. The squared form adds no information but destroys LICQ.
2. **Accept as known limitation**: The original HS62 problem header notes this constraint qualification issue. The model is deliberately ill-conditioned as a test case.
3. **Redundant constraint detection**: Since both `eq1` (squared) and `eq1x` (linear) enforce the same constraint, detect and use only the well-conditioned linear form.

## Files

- `data/gamslib/raw/hs62.gms` — original NLP model
- `data/gamslib/mcp/hs62_mcp.gms` — generated MCP
- Key equation: `eq1` (LICQ-violating sqr constraint)
