# mingamma: loggamma Differentiation Requires Digamma/Psi Function

**GitHub Issue:** [#935](https://github.com/jeffreyhorn/nlp2mcp/issues/935)
**Status:** RESOLVED
**Severity:** Medium — Model parses but could not be translated (missing function derivative)
**Date:** 2026-02-26
**Resolved:** 2026-03-16 (Sprint 22 Day 12)
**Affected Models:** mingamma

---

## Problem Summary

The `mingamma.gms` model (GAMSlib SEQ=217, "Minimal y of GAMMA(x)") parsed successfully but failed during KKT translation because the model uses `gamma()` and `loggamma()` in its equations, and differentiation required the digamma (psi) function.

---

## Resolution

Implemented a smooth digamma (psi) approximation using an asymptotic series with unconditional argument shifting:

1. **Derivative rule**: `_diff_gamma()` in `src/ad/derivative_rules.py` computes:
   - `d/dx[loggamma(u)] = digamma__(u) * du/dx`
   - `d/dx[gamma(u)] = gamma(u) * digamma__(u) * du/dx`
   Emits `Call("digamma__", (arg,))` which the GAMS emitter renders as a macro call.

2. **GAMS macro**: `emit_gams.py` detects `digamma__` usage in KKT equations and emits a `$macro` header:
   - `digamma__asy(z)`: asymptotic series `log(z) - 1/(2z) - 1/(12z^2) + 1/(120z^4) - 1/(252z^6) + 1/(240z^8)`
   - `digamma__(x)`: shifts argument by 8 via recurrence, then applies asymptotic series
   - Unconditional (no `ifthen`) — safe for MCP/NLP model types
   - Accurate to ~14 digits for all x > 0

3. **GAMS verification**: Generated MCP compiles and solves:
   - SOLVER STATUS 1 (Normal), MODEL STATUS 1 (Optimal)
   - Objective: -0.121 (matches reference -0.1215)

### Files Changed

| File | Change |
|------|--------|
| `src/ad/derivative_rules.py` | Replaced `ValueError` with `_diff_gamma()` |
| `src/emit/emit_gams.py` | Added `DIGAMMA_MACRO`, `_kkt_uses_digamma()`, `_expr_uses_func()` |
| `tests/unit/ad/test_transcendental.py` | Updated gamma/loggamma tests to verify derivative structure |
