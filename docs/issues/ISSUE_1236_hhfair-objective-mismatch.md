# hhfair: Objective Mismatch (MCP=54.9 vs NLP=87.2)

**GitHub Issue:** [#1236](https://github.com/jeffreyhorn/nlp2mcp/issues/1236)
**Status:** OPEN
**Severity:** Medium — Model solves optimally but objective differs from NLP
**Date:** 2026-04-09
**Last Updated:** 2026-04-09
**Affected Models:** hhfair

---

## Problem Summary

After fixing EXECERROR (#1179), hhfair solves to MODEL STATUS 1 Optimal but
with MCP obj=54.885 vs NLP obj=87.159 (37% mismatch). This indicates an
incorrect KKT formulation — the stationarity conditions produce a different
optimum than the original NLP.

---

## Current Status

- **Translation**: Success
- **GAMS compilation**: Success
- **PATH solve**: MODEL STATUS 1 Optimal, SOLVER STATUS 1 Normal Completion
- **Objective**: MCP=54.885, NLP=87.159 (37% mismatch)
- **Pipeline category**: model_optimal (mismatch)
- **Previous fixes**: #1179 (EXECERROR, domain-widened variable fixing)

---

## Root Cause (Investigation Needed)

The model has complex mathematical features that may cause AD/KKT errors:

1. **Product aggregation objective**: `obj =e= prod(t, u(t)**ufact(t))` —
   the derivative of a product aggregation uses the logarithmic derivative
   approach. If `ufact(t)` or `u(t)` have edge-case values, the derivative
   may be incorrect.

2. **CES utility function**: `u(t) =e= (a1*c(t)**(-a2) + (1-a1)*(th-l(t)-n(t))**(-a2))**(-1/a2)/100`
   — deeply nested power expressions with negative exponents. The chain rule
   through `(-a2)` powers and `(-1/a2)` root is complex.

3. **Domain widening effects**: Variable `n(t)` was widened to `n(tl)`.
   The extra `n(0) = 0` fixup may affect the KKT system structure.

4. **Set hierarchy**: `tl={0,1,2,3}`, `t(tl)={1,2,3}`, `tt(t)={3}` — 
   subset relationships may cause incomplete Jacobian contributions.

---

## Reproduction

**Prerequisite:** GAMSlib raw sources must be downloaded into `data/gamslib/raw/`
(not checked in; run `python scripts/gamslib/download_models.py` or obtain
`hhfair.gms` from https://www.gams.com/latest/gamslib_ml/hhfair.128).

```bash
.venv/bin/python -m src.cli data/gamslib/raw/hhfair.gms -o /tmp/hhfair_mcp.gms --quiet
gams /tmp/hhfair_mcp.gms lo=0

# Output:
# **** SOLVER STATUS     1 Normal Completion
# **** MODEL STATUS      1 Optimal
# nlp2mcp_obj_val = 54.885 (NLP: 87.159)
```

---

## Potential Fix Approaches

1. **Verify product aggregation derivative**: Check that `_diff_prod` correctly
   handles `prod(t, u(t)**ufact(t))` — the logarithmic derivative should produce
   `prod(t, u(t)**ufact(t)) * sum(t, ufact(t) * u(t)**(ufact(t)-1) * du/dx / u(t)**ufact(t))`.

2. **Verify CES utility derivative**: Hand-compute `∂utility/∂c`, `∂utility/∂l`,
   `∂utility/∂n` and compare against the generated stationarity terms.

3. **Check variable initialization**: Poor starting point may cause PATH to
   converge to a different KKT solution (local vs global optimum for non-convex
   utility function).

---

## Files Involved

- `src/ad/derivative_rules.py` — `_diff_prod` for product aggregation
- `src/ad/gradient.py` — Objective gradient computation
- `src/kkt/stationarity.py` — Stationarity equation assembly
- `data/gamslib/raw/hhfair.gms` — Original model (119 lines)

---

## Related Issues

- #1179 (FIXED) — EXECERROR from domain-widened variable
