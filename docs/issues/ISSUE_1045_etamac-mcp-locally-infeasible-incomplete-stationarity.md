# etamac: MCP Locally Infeasible — Incomplete Stationarity for Lead/Lag Variables

**GitHub Issue:** [#1045](https://github.com/jeffreyhorn/nlp2mcp/issues/1045)
**Status:** Open
**Severity:** Medium — Model translates and solver runs, but PATH reports locally infeasible
**Date:** 2026-03-11
**Affected Models:** etamac

---

## Problem Summary

After fixing the structural MCP errors (#984 domain errors, #1043 unmatched equations), the etamac model now reaches the PATH solver but reports **Locally Infeasible** (model status 5, solver status 1). PATH runs 5,682 iterations but cannot converge. The largest infeasibility is at `stat_k('2010')` with a normal map residual of 15.362.

---

## Root Cause

The stationarity equation `stat_k(t)` is **incomplete** — it only captures the Jacobian contribution from `totalcap(t)` with respect to `k(t)`, but misses the contribution from `totalcap(t-1)` with respect to `k(t)` via the lead/lag offset `k(t+1)`.

### The Capital Accumulation Constraint

```gams
totalcap(t)$(ord(t) <= card(t) - 1).. k(t+1) =E= k(t) * spda ** nyper + kn(t+1);
```

This constraint creates two Jacobian entries for variable `k(t)`:
1. `∂totalcap(t)/∂k(t) = -spda^nyper` — from the `k(t)` term on the RHS
2. `∂totalcap(t-1)/∂k(t) = 1` — because `totalcap(t-1)` references `k((t-1)+1) = k(t)` on the LHS

### Current (Incomplete) Stationarity

```gams
stat_k(t).. (-spda^nyper) * nu_totalcap(t) + sum(tlast, (grow(tlast) + 1 - spda) * lam_tc(tlast)) - piL_k(t) =E= 0;
```

This only has the `nu_totalcap(t)` term (contribution 1). The `nu_totalcap(t-1)` term (contribution 2) is missing.

### Correct Stationarity

The full KKT stationarity for `k(t)` should be:

```gams
stat_k(t).. (-spda^nyper) * nu_totalcap(t) + nu_totalcap(t-1) + sum(tlast, (grow(tlast) + 1 - spda) * lam_tc(tlast)) - piL_k(t) =E= 0;
```

(with appropriate handling of boundary conditions where `t-1` doesn't exist)

### Why This Happens

The Jacobian computation in `src/ad/jacobian.py` processes each equation independently. When it encounters `totalcap(t)` containing `k(t+1)`, it computes `∂totalcap/∂k` and records the derivative. However, the lead/lag offset `t+1` means this derivative applies to `k` at index `t+1`, not `t`. The current AD system doesn't properly shift the multiplier index when assembling stationarity equations — it creates `nu_totalcap(t)` instead of the needed `nu_totalcap(t-1)` (or equivalently, it assigns the derivative to `stat_k(t+1)` but misses the `stat_k(t)` contribution).

This is a known limitation of the AD propagation for lead/lag expressions (related to deferred issue #763).

---

## PATH Solver Output

```
SOLVER STATUS     1 Normal Completion
MODEL STATUS      5 Locally Infeasible

FINAL STATISTICS
Inf-Norm of Complementarity . .  4.1154e+00 eqn: (totalcap('1990'))
Inf-Norm of Normal Map. . . . .  1.5362e+01 eqn: (stat_k('2010'))
Inf-Norm of Minimum Map . . . .  4.1154e+00 eqn: (totalcap('1990'))

251 row/cols, 598 non-zeros
5682 iterations
```

---

## How to Reproduce

```bash
python -m src.cli data/gamslib/raw/etamac.gms -o data/gamslib/mcp/etamac_mcp.gms
cd data/gamslib/mcp && gams etamac_mcp.gms
# Check etamac_mcp.lst for: "MODEL STATUS 5 Locally Infeasible"
# and "Inf-Norm of Normal Map... stat_k('2010')"
```

---

## Suggested Fix

The Jacobian/stationarity assembly needs to handle lead/lag variable references correctly. When equation `h(t)` references variable `x(t+k)`, the Jacobian entry `∂h(t)/∂x(t+k)` should contribute to `stat_x(t+k)` with multiplier `nu_h(t)`. Currently the system creates the derivative but may not correctly shift the multiplier index.

This requires changes to:
- `src/ad/jacobian.py` — Track lead/lag offsets in Jacobian entries
- `src/kkt/stationarity.py` — Assemble stationarity equations with shifted multiplier indices

This is related to the deferred AD propagation issue #763.

---

## Related Issues

- #984 — etamac domain errors (division by zero, log(0)) — FIXED
- #1043 — etamac unmatched totalcap equations — FIXED (IndexOffset subset detection)
- #763 — AD propagation for lead/lag expressions (deferred)

---

## Files Involved

- `src/ad/jacobian.py` — Jacobian computation for lead/lag equations
- `src/kkt/stationarity.py` — Stationarity equation assembly
- `data/gamslib/mcp/etamac_mcp.gms` — Generated MCP file
- `data/gamslib/raw/etamac.gms` — Original model
