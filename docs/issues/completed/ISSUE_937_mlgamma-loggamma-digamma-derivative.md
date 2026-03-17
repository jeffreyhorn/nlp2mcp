# mlgamma: loggamma Differentiation Requires Digamma/Psi Function

**GitHub Issue:** [#937](https://github.com/jeffreyhorn/nlp2mcp/issues/937)
**Status:** RESOLVED
**Severity:** Medium — Model parses but could not be translated (missing function derivative)
**Date:** 2026-02-26
**Resolved:** 2026-03-16 (Sprint 22 Day 12)
**Affected Models:** mlgamma

---

## Problem Summary

The `mlgamma.gms` model (GAMSlib SEQ=222, "Maximum Likelihood estimation of parameters of the gamma distribution") parsed successfully but failed during KKT translation because the model uses `loggamma()` in its equations.

---

## Resolution

Fixed by the same digamma approximation implementation as Issue #935 (mingamma). The `_diff_gamma()` derivative rule and `$macro digamma__` GAMS macro handle differentiation of `loggamma()` for the gamma distribution MLE function.

**GAMS verification**: Generated MCP compiles and solves:
- SOLVER STATUS 1 (Normal), MODEL STATUS 1 (Optimal)
- Objective: -155.347 (matches reference -155.3468)

See Issue #935 for full implementation details and files changed.
