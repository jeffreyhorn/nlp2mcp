# maxmin: Unquoted Element Labels in .fx Equations (GAMS $120/$340)

**GitHub Issue:** [#939](https://github.com/jeffreyhorn/nlp2mcp/issues/939)
**Status:** FIXED (compiles and solves to Optimal)
**Severity:** Medium
**Date:** 2026-02-26
**Fixed:** 2026-04-01

## Resolution

The compilation errors ($120/$340 from unquoted element labels) were fixed by `_quote_literal_indices()` in normalize.py. The PATH convergence issue (division by zero in stationarity equations) has also been resolved by accumulated fixes.

**Result:** maxmin compiles cleanly (0 errors) and solves to MODEL STATUS 1 Optimal (SOLVER STATUS 1). Objective mismatch with reference is present — likely due to domain condition propagation affecting KKT accuracy for set-filtered sums.

The smin() arity issue noted in the original report does not affect the solved model (`maxmin1a`).
