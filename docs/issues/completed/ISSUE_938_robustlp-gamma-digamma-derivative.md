# robustlp: gamma Differentiation Requires Digamma/Psi Function

**GitHub Issue:** [#938](https://github.com/jeffreyhorn/nlp2mcp/issues/938)
**Status:** RESOLVED
**Severity:** Medium — Model parses but could not be translated (missing function derivative)
**Date:** 2026-02-26
**Resolved:** 2026-03-16 (Sprint 22 Day 12)
**Affected Models:** robustlp

---

## Problem Summary

The `robustlp.gms` model (GAMSlib SEQ=318, "Robust linear programming as an SOCP") parsed successfully but failed during KKT translation with an error about `gamma()` differentiation.

---

## Resolution

Fixed by the same digamma approximation implementation as Issue #935 (mingamma). The derivative rule now handles `gamma()` and `loggamma()` calls.

**Important note**: Investigation revealed that robustlp does NOT actually use the mathematical `gamma()` function. The model declares `gamma(j)` as a **variable name**, not a function call. The parser treats `gamma(j)` as `Call("gamma", (SymbolRef(j),))` which triggered the old `ValueError`. With the digamma fix, differentiation of `Call("gamma", (SymbolRef(j),))` correctly returns zero (via chain rule: `gamma(j) * digamma__(j) * d(j)/dx = 0` since `j` is a set index, not a variable). The digamma macro is NOT emitted for this model since no stationarity equation uses it.

**GAMS verification**: Generated MCP compiles. Model status is Locally Infeasible (5), which is a separate formulation issue unrelated to the gamma/digamma differentiation.

See Issue #935 for full implementation details and files changed.
