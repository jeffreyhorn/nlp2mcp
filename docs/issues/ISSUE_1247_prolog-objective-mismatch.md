# prolog: Objective Mismatch (MCP=-73.5 vs NLP=-0.0)

**GitHub Issue:** [#1247](https://github.com/jeffreyhorn/nlp2mcp/issues/1247)
**Status:** OPEN
**Severity:** Medium — Model solves optimally but objective differs from NLP
**Date:** 2026-04-09
**Last Updated:** 2026-04-09
**Affected Models:** prolog

---

## Problem Summary

After fixing the multiplier dimension mismatch (#1227), prolog solves to
MODEL STATUS 1 Optimal but with MCP obj=-73.528 vs NLP obj=-0.0 (or near
zero). The KKT system produces a valid but different optimum.

---

## Current Status

- **Translation**: Success
- **GAMS compilation**: Success
- **PATH solve**: MODEL STATUS 1 Optimal, SOLVER STATUS 1 Normal Completion
- **Objective**: MCP=-73.528, NLP=-0.0
- **Pipeline category**: model_optimal (mismatch)
- **Previous fixes**: #1227 (multiplier dimension mismatch, FIXED)

---

## Root Cause (Investigation Needed)

The prolog model is a general equilibrium model (Shoven-Whalley prototype)
with CES production functions, multiple solve variants (nortone, nortonl,
nortonn), and complex alias structures (Alias(i,j), Alias(g,gp)).

The objective is `zdef.. z =e= sum(h, y(h))` — sum of household demands.
The NLP objective of -0.0 suggests the NLP solver found a boundary solution,
while the MCP finds a different equilibrium point.

Possible causes:
1. **Multi-model structure**: prolog has 3 model variants (nortone, nortonl,
   nortonn). nlp2mcp reformulates the LAST solve which may not be the
   primary one the NLP comparison uses.
2. **Alias-related Jacobian terms**: The model uses `Alias(i,j)` and
   `Alias(g,gp)` extensively. Some Jacobian terms may be incorrect.
3. **CES function derivatives**: Nested power expressions with `epsi(g,h)`
   and `eta(g,gp,h)` parameters may have derivative errors.
4. **Inequality complementarity**: `mp(i,t)` is `=l=` (inequality). The
   complementarity formulation may not match the NLP's active constraint
   handling.

---

## Reproduction

**Prerequisite:** GAMSlib raw sources in `data/gamslib/raw/`.

```bash
.venv/bin/python -m src.cli data/gamslib/raw/prolog.gms -o /tmp/prolog_mcp.gms --quiet
gams /tmp/prolog_mcp.gms lo=0

# Output:
# **** SOLVER STATUS     1 Normal Completion
# **** MODEL STATUS      1 Optimal
# nlp2mcp_obj_val = -73.528 (NLP: -0.0)
```

---

## Files Involved

- `src/kkt/stationarity.py` — Stationarity equation builder
- `src/ad/constraint_jacobian.py` — Jacobian computation
- `data/gamslib/raw/prolog.gms` — Original model (~160 lines)

---

## Related Issues

- #1227 (FIXED) — Multiplier dimension mismatch
- #1070 — Originally described as CES singular Jacobian (superseded by #1227)
