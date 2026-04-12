# bearing: MCP Model Infeasible (MODEL STATUS 5)

**GitHub Issue:** [#1199](https://github.com/jeffreyhorn/nlp2mcp/issues/1199)
**Status:** FIXED (Sprint 24 — `--nlp-presolve` flag)
**Model:** bearing (GAMSlib SEQ=12, "Design of a Stepping Bearing")
**Error category:** `model_infeasible` → `model_optimal` (with `--nlp-presolve`)

## Description

bearing translates and compiles cleanly but PATH returns MODEL STATUS 5
(Locally Infeasible) from cold start. The KKT stationarity equations are
mathematically correct — the infeasibility is caused by PATH's inability
to converge on this highly non-convex model with coefficients spanning 14
orders of magnitude.

## Fix

The `--nlp-presolve` flag (Sprint 24) solves the original NLP first and
transfers primal + dual values to warm-start the MCP. This gives PATH a
starting point near the KKT solution.

```bash
nlp2mcp bearing.gms -o bearing_mcp.gms --nlp-presolve --skip-convexity-check
```

**Result:** MODEL STATUS 1 Optimal, PL = 19517.332 (exact NLP match).

## Root Cause

The bearing NLP is non-convex (bilinear/trilinear terms, 8 nonlinear
equalities). PATH needs both primal and dual initialization simultaneously
to converge — neither alone suffices. The `--nlp-presolve` mechanism
provides this by `$include`-ing the original model, solving the NLP with
CONOPT, then transferring equation marginals to MCP multiplier `.l` values.

## Related Issues

- #757 — Original bearing infeasibility report (same root cause)
- #672 — bearing MCP pairing fix (FIXED, Sprint 19)
- #835 — bearing scale attribute emission (FIXED)
