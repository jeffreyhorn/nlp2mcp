# spatequ: Jacobian Missing Derivatives for Variables Inside Sum with Alias Index

**GitHub Issue:** [#1157](https://github.com/jeffreyhorn/nlp2mcp/issues/1157)
**Status:** OPEN
**Severity:** High — produces incorrect KKT system, model infeasible (MODEL STATUS 5)
**Date:** 2026-03-26
**Affected Models:** spatequ (and potentially any model where a variable appears inside a sum over an alias of the variable's own domain)

---

## Problem Summary

When a variable `p(r,c)` appears inside `sum(cc, BetaD(r,c,cc)*p(r,c))` where `cc` is an alias of `c`, the Jacobian computation returns zero derivative for `∂DEM/∂p(r,c)`. The correct derivative is `sum(cc, BetaD(r,c,cc))`.

This causes `stat_p(r,c)` to be missing the `nu_DEM` and `nu_SUP` terms, making the KKT system infeasible.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/spatequ.gms -o /tmp/spatequ_mcp.gms --skip-convexity-check
gams /tmp/spatequ_mcp.gms lo=2
# MODEL STATUS 5 (Locally Infeasible), 0 compilation errors
```

**Diagnostic:**
```python
from src.ir.parser import parse_model_file
from src.ir.normalize import normalize_model
from src.ad.constraint_jacobian import _substitute_indices, differentiate_expr
from src.ir.ast import Binary
from src.config import Config

model = parse_model_file('data/gamslib/raw/spatequ.gms')
normalize_model(model)
dem = model.equations.get('dem')
lhs, rhs = dem.lhs_rhs
base_expr = Binary('-', lhs, rhs)

# Substitute for DEM(Reg1, Com1)
subst_expr = _substitute_indices(base_expr, ('r','c'), ('Reg1','Com1'))
# subst_expr contains: Sum((cc), Binary(*, ParamRef(BetaD(Reg1,Com1,cc)), VarRef(p(Reg1,Com1))))

# Differentiate w.r.t. p(Reg1, Com1)
config = Config()
config.model_ir = model
d = differentiate_expr(subst_expr, 'p', ('Reg1', 'Com1'), config)
# RESULT: All zeros — should be Sum((cc), ParamRef(BetaD(Reg1,Com1,cc)))
```

**Current stationarity (incorrect):**
```gams
stat_p(r,c).. sum(rr, lam_PDIF(r,rr,c)) - piL_p(r,c) =E= 0;
```

**Expected stationarity:**
```gams
stat_p(r,c).. sum(cc, BetaD(r,c,cc)) * nu_DEM(r,c)
            + sum(cc, BetaS(r,c,cc)) * nu_SUP(r,c)
            + sum(rr, lam_PDIF(r,rr,c))
            - sum(rr, lam_PDIF(rr,r,c))
            - piL_p(r,c) =E= 0;
```

---

## Root Cause

The `differentiate_expr` function in the AD system does not correctly differentiate through `Sum` nodes when the variable being differentiated (`p(r,c)`) is constant with respect to the sum index (`cc`).

After index substitution, the expression is:
```
Sum((cc), Binary(*, ParamRef(BetaD(Reg1,Com1,cc)), VarRef(p(Reg1,Com1))))
```

The variable `VarRef(p(Reg1,Com1))` does NOT depend on `cc` — it has the same indices regardless of the sum iteration. The AD system should recognize that `∂/∂p(Reg1,Com1)` of `VarRef(p(Reg1,Com1))` = 1 inside the sum, producing `Sum((cc), BetaD(Reg1,Com1,cc))`.

Instead, the derivative is zero. This suggests the AD system either:
1. Evaluates the sum at a specific `cc` value before differentiating (losing the sum structure), or
2. Fails to match `VarRef(p(Reg1,Com1))` against the target variable `p` with indices `(Reg1,Com1)` inside a Sum context, or
3. Has a bug in the Sum differentiation rule that incorrectly applies the chain rule

---

## Affected Equations

The GAMS equations:
```gams
DEM(r,c).. AlphaD(r,c) + sum(cc, BetaD(r,c,cc)*P(r,c)) =e= Qd(r,c);
SUP(r,c).. AlphaS(r,c) + sum(cc, BetaS(r,c,cc)*P(r,c)) =e= Qs(r,c);
```

Both have `p(r,c)` inside `sum(cc, ...)` where `cc` is `Alias(c,cc)`.

---

## Affected Files

- `src/ad/constraint_jacobian.py` — `differentiate_expr()` or `_compute_equality_jacobian()`
- `src/ad/derivative_rules.py` — Sum differentiation rule
- `src/ad/ad_core.py` — Core AD engine

---

## Fix Approach

1. Investigate how `differentiate_expr` handles `Sum` nodes — specifically the case where the differentiation target has concrete indices that don't depend on the sum variable.
2. The fix likely involves the Sum differentiation rule: `d/dx [sum(i, f(i,x))] = sum(i, df/dx(i,x))`. The derivative should pass through the sum when the variable doesn't depend on the sum index.
3. Add a unit test: `d/dp(R1,C1) [sum(cc, B(R1,C1,cc)*p(R1,C1))]` should equal `sum(cc, B(R1,C1,cc))`.

**Effort estimate:** 2-3 hours

---

## Related Issues

- [#1038](https://github.com/jeffreyhorn/nlp2mcp/issues/1038) — spatequ Jacobian domain mismatch (fixed in PR #1153)
- [#1154](https://github.com/jeffreyhorn/nlp2mcp/issues/1154) — spatequ wrong model selection (fixed)
