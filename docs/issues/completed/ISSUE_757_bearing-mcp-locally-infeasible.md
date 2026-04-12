# Bearing Model MCP is Locally Infeasible (PATH Solver Model Status 5)

**GitHub Issue:** [#757](https://github.com/jeffreyhorn/nlp2mcp/issues/757)
**Status:** FIXED (Sprint 24 — `--nlp-presolve` flag)
**Severity:** Medium — MCP generates correctly; solver needs warm-start for non-convex model
**Date:** 2026-02-16 (opened), 2026-04-12 (fixed)

---

## Problem Summary

The bearing model successfully parses and generates an MCP file, but PATH
returns "Locally Infeasible" (MODEL STATUS 5) from cold-start initialization.
The KKT stationarity equations are mathematically correct (all 13 verified
by hand). The infeasibility is caused by the non-convex nature of the NLP
combined with extreme coefficient ranges (1e-6 to 1e8).

---

## Fix

The `--nlp-presolve` flag solves the original NLP first and transfers both
primal levels and equation marginals to initialize the MCP dual variables:

```bash
nlp2mcp bearing.gms -o bearing_mcp.gms --nlp-presolve --skip-convexity-check
```

**Result:** MODEL STATUS 1 Optimal, PL = 19517.332 (matches NLP exactly).

The mechanism works by emitting a `$onMultiR` / `$include <original.gms>` /
`$offMulti` block before the MCP solve, followed by dual transfer assignments
(`nu_*.l = *.m` for equalities, `lam_*.l = abs(*.m)` for inequalities,
`piL_*/piU_*` for bound multipliers).

---

## Root Cause Analysis

The bearing NLP is **non-convex** with:
- 14 variables, 13 constraints (10 equality + 3 inequality)
- Bilinear and trilinear terms in 6 constraints
- Odd powers in inlet_pressure
- Variable scaling spanning 14 orders of magnitude

Testing confirmed that **neither primal nor dual initialization alone
suffices** — both are needed simultaneously for PATH to converge.

The non-convexity was computationally confirmed: cold-start MCP finds
PL ≈ 1751 while warm-start finds PL = 19517.332. Two distinct KKT points
with different objectives proves the problem is non-convex.

---

## Related Issues

- #1199 — bearing model infeasible (Sprint 24 triage, same root cause)
- #672 — bearing MCP pairing fix (FIXED, Sprint 19)
- #835 — bearing scale attribute emission (FIXED)
- `docs/features/FEATURE_computational_convexity_test.md` — proposed
  feature to automatically detect non-convexity via dual KKT comparison
