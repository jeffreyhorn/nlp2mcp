# elec: MCP Execution Error — Division by Zero (pairwise distances)

**GitHub Issue:** [#983](https://github.com/jeffreyhorn/nlp2mcp/issues/983)
**Status:** OPEN (deferred — requires set-based dollar condition propagation)
**Severity:** Medium — Model translates but PATH solver never runs (path_solve_terminated)
**Date:** 2026-03-03
**Affected Models:** elec

---

## Problem Summary

The elec model (electrons on a sphere) parses and translates to MCP successfully, but GAMS aborts during equation generation with `division by zero (0)`. The KKT stationarity equations contain `1/distance` terms where `distance = sqrt((x_i - x_j)^2 + ...)`, and the `sum(j, ...)` includes the `i == j` case where the self-distance is always zero.

---

## Investigation

The original model uses a filtered set to exclude self-pairs:
```gams
Set ut(i,i) 'upper triangular part';
ut(i,j)$(ord(j) > ord(i)) = yes;
obj.. potential =e= sum{ut(i,j), 1.0/sqrt(sqr(x[i] - x[j]) + ...)};
```

The `sum{ut(i,j), ...}` syntax filters to only `(i,j)` pairs where `ord(j) > ord(i)`. When this is differentiated to produce stationarity equations, the set-based filtering is lost because:

1. The parser treats `ut(i,j)` as a domain reference (set membership), not an explicit dollar condition on the Sum expression
2. The differentiation engine (`src/ad/derivative_rules.py`) correctly preserves explicit `DollarConditional` nodes but cannot recover conditions encoded at the set level
3. The MCP emitter generates `sum(j, ...)` without filtering, including `i == j`

**Complexity:** Medium-to-hard. Requires either:
- Parser/IR enrichment to convert set-domain filtering to explicit Sum conditions, or
- Emitter-level lookup of set definitions to reconstruct dollar conditions

---

## Files

- MCP file: `data/gamslib/mcp/elec_mcp.gms`
- Original GAMS model: `data/gamslib/raw/elec.gms`
- Stationarity builder: `src/kkt/stationarity.py`
- AD differentiation: `src/ad/derivative_rules.py`
