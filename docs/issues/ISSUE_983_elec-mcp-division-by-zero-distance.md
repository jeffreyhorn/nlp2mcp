# elec: MCP PATH Convergence Failure (non-convex)

**GitHub Issue:** [#983](https://github.com/jeffreyhorn/nlp2mcp/issues/983)
**Status:** OPEN — Not fixable (non-convex model, PATH convergence issue)
**Severity:** Low — MCP generates correctly; solver cannot converge
**Date:** 2026-03-03
**Last Updated:** 2026-03-17
**Affected Models:** elec

---

## Problem Summary

The elec model (electrons on a sphere, GAMSlib SEQ=230) parses and translates to MCP
successfully. The original issue described division-by-zero errors, but this has been
resolved — the `$(ut(i,j))` set membership condition IS correctly preserved in the
stationarity equations, filtering out self-pairs.

The remaining issue is that PATH terminates with MODEL STATUS 6 (Intermediate Infeasible).
This is a non-convex model (25 electrons, 75 variables, 25 quadratic ball constraints)
where the KKT system has multiple solutions and PATH cannot converge from the given
initial point.

---

## Current Status (2026-03-17)

- **Translation**: Success — MCP file generates without errors
- **GAMS compilation**: Success — no compilation or execution errors
- **PATH solve**: MODEL STATUS 6 (Intermediate Infeasible), SOLVER STATUS 4 (Terminated by Solver)
- **Stationarity equations**: `stat_x(i).. sum(j$(ut(i,j)), derivative_terms) + ... =E= 0;`
  - The `$(ut(i,j))` condition correctly excludes self-pairs
  - No division-by-zero errors occur during equation generation
- **Large INFES values**: PATH shows massive infeasibilities in all stationarity equations
  (INFES values ranging from 3 to 391), indicating the KKT system solution is unreachable

---

## Why Division-by-Zero No Longer Occurs

The original issue doc stated that `$(ut(i,j))` filtering was lost during differentiation.
This was incorrect — the parser correctly converts `sum{ut(i,j), body}` into
`Sum((i,j), body, condition=SetMembershipTest("ut", (i,j)))`, and the AD engine preserves
the condition through differentiation. The emitted stationarity equations contain
`sum(j$(ut(i,j)), ...)` as expected.

---

## Root Cause of PATH Failure

The elec model is **strongly non-convex**:
- The objective `sum(ut, 1/distance)` is non-convex (reciprocal of Euclidean distance)
- The ball constraints `sqr(x) + sqr(y) + sqr(z) = 1` are nonlinear equalities
- The KKT system has many local solutions (one for each local minimum of the NLP)
- PATH's initial point (random uniform on sphere) is likely far from any KKT solution

This is the same class of issue as #757 (bearing) — non-convex NLP where the MCP is
structurally correct but PATH cannot converge.

---

## Files

- MCP file: `data/gamslib/mcp/elec_mcp.gms`
- Original GAMS model: `data/gamslib/raw/elec.gms`
- Stationarity builder: `src/kkt/stationarity.py`
- AD differentiation: `src/ad/derivative_rules.py`
