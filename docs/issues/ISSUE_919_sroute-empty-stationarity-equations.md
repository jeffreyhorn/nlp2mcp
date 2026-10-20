# sroute: Empty Stationarity Equations (KKT Gradient Failure)

**GitHub Issue:** [#919](https://github.com/jeffreyhorn/nlp2mcp/issues/919)
**Model:** sroute (GAMSlib)
**Sprint:** 21 Day 8
**Error Category:** Execution — MCP pair empty equation, variable NOT fixed

## Problem

The generated MCP file produces stationarity equations for `x(i,ip,ipp)` that only contain a constant parameter term with no variable references:

```gams
stat_x(i,ip,ipp).. darc(i,ip) =E= 0;
```

This should be the stationarity condition `∂L/∂x = 0`, but instead of containing the objective gradient and constraint multiplier terms, it only has the constant `darc(i,ip)`. GAMS reports 307 "empty equation but variable NOT fixed" errors.

## Error Output

```
**** MCP pair stat_x.x has empty equation but associated variable is NOT fixed
```

307 execution errors (one per `x(i,ip,ipp)` instance). 0 compilation errors.

## Root Cause

The original sroute.gms defines:

```gams
* Objective:
cost.. z =e= sum((i,ip,ipp)$darc(ip,ipp), darc(ip,ipp)*x(i,ip,ipp));

* Node balance constraint:
nb(i,ip)$(not sameas(i,ip))..
    sum(ipp$darc(ipp,ip), x(i,ipp,ip)) =g= sum(ipp$darc(ip,ipp), x(i,ip,ipp)) + 1;
```

The stationarity condition for `x(i,ip,ipp)` should be:
```
∂cost/∂x + λ_nb * ∂nb/∂x - piL_x = 0
```

Which expands to:
```
darc(ip,ipp) + sum(i', λ_nb(i',ipp) * ...) - piL_x(i,ip,ipp) = 0
```

But the emitter only captures `darc(ip,ipp)` (the objective gradient term) and drops the constraint dual terms entirely. The result is an equation with only a constant — no variables — making it "empty" from GAMS MCP's perspective.

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/sroute.gms -o /tmp/sroute_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/sroute_mcp.gms o=/tmp/sroute_mcp.lst
grep 'MCP pair' /tmp/sroute_mcp.lst | wc -l
```

## Suggested Fix

The KKT stationarity equation generator needs to correctly differentiate the Lagrangian with respect to `x(i,ip,ipp)`. The constraint `nb(i,ip)` sums over `x(i,ipp,ip)` and `x(i,ip,ipp)` with dollar conditions on `darc`. The gradient computation must:

1. Correctly handle the 3-index variable `x(i,ip,ipp)` appearing in summations with index permutations
2. Include the dual variable `lam_nb(i,ip)` multiplied by the constraint's gradient
3. Handle the `$darc(...)` conditional in the gradient computation

This is likely a bug in the automatic differentiation or KKT condition generation for models with complex index permutations in constraints.

## Impact

307 execution errors. Model compiles cleanly but SOLVE aborts. The KKT equations are fundamentally incorrect.

## Current Status (2026-10-20) — Sprint 40 Day 4: re-measured licensed, routing note R-B-sroute

Measured at `de0a7186` (Day 3 batch `f1771435`), GAMS 54.2.1 licensed.

- **The original symptom is gone.** The 307 "empty equation but associated variable is NOT fixed" execution errors no longer occur. The MCP compiles and PATH runs: `model_infeasible` (**MS 4**), `MCP-FAILED`, and the presolve retry is also MS 4.
- **The defect this issue named still reproduces, in a new form.** `kkt_residual.py` gives **`case_b`** (emit bug), with a consistent dual transfer (max equality residual 0) and a dual scale of 260:

  | row | raw | relative |
  |---|---|---|
  | `stat_x(portland,chicago,boston)` | 260 | **1.000** |
  | `stat_x(portland,chicago,memphis)` | 239 | 0.919 |
  | `stat_x(portland,chicago,kansas-cty)` | 215 | 0.827 |
  | `stat_x(chicago,portland,losangeles)` | 200 | 0.769 |

- **How to read the numbers (corrected in PR #1777 review).** `kkt_residual.py` normalizes every row by **one global dual scale**: the largest transferred multiplier magnitude, floored at 1 (`dual_scale`, 260 here). A relative 1.000 means only that the raw residual (260) equals that scale. **It does not establish that this row's whole gradient is missing.**
- **The golden already carries `lam_nb`.** `nb` is an `=g=` inequality, so its multiplier is `lam_nb`, not `nu_nb`. The emitted row is

  ```gams
  stat_x(i,ip,ipp).. darc(i,ip) + (1$(darc(ip,ipp)) * lam_nb(i,ip))$((not sameas(i, ipp))) - piL_x(i,ip,ipp) =E= 0;
  ```

  - **Leads, not a diagnosis (hypotheses until traced):**
    - **The objective coefficient's indices.** The source's `cd.. cost =e= sum((i,ip,ipp), darc(ip,ipp)*x(i,ip,ipp))` gives `∂cost/∂x(i,ip,ipp) = darc(ip,ipp)`. The emitted row has **`darc(i,ip)`**.
    - **The `lam_nb` terms.** `x(i,ip,ipp)` is *outgoing* in `nb(i,ip)` (right-hand sum, `darc(ip,ipp)`) and *incoming* in `nb(i,ipp)` (left-hand sum `sum(ipp'$darc(ipp',ipp), x(i,ipp',ipp))` at `ipp' = ip`). That means two `lam_nb` contributions with opposite signs, at `(i,ip)` and `(i,ipp)`. The emitted row has **one**, at `(i,ip)`.
    - Both look like the same index permutation over `(i,ip,ipp)`. Whether that is this issue's original "dual terms dropped under permuted indices" is **provisional**.
- **First step:** hand-derive `∂L/∂x(portland,chicago,boston)` and compare it term by term with the emitted row: the **objective coefficient** (which `darc` index pair), **both** the incoming and outgoing `lam_nb` terms (sign and index), and `piL_x`. Do not attribute the residual to a missing term before this trace.
