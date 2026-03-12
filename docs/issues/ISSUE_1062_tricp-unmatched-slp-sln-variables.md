# tricp: Unmatched Variables `slp`/`sln` — 760 MCP Errors

**GitHub Issue:** [#1062](https://github.com/jeffreyhorn/nlp2mcp/issues/1062)
**Status:** OPEN
**Severity:** High — execution errors, model fails to solve
**Date:** 2026-03-12
**Affected Models:** tricp

---

## Problem Summary

The tricp model's generated MCP file has 760 "Unmatched variable not free or fixed" errors for variables `slp(i,j)` and `sln(i,j)`. The stationarity equations `stat_slp(n,n)` and `stat_sln(n,n)` are defined over the full `(n,n)` cross product (400 instances for 20 nodes), but these variables only participate in equation `eq1(e(i,j))` which is conditioned on the edge set `e`. Off-edge instances have no corresponding equation in the MCP model.

---

## Error Details

GAMS execution errors (760 total):
```
**** Unmatched variable not free or fixed
     slp(n0,n1)

**** Unmatched variable not free or fixed
     slp(n0,n2)
...
```

380 errors for `slp` + 380 errors for `sln` = 760 total.

Additionally, the model exceeds GAMS demo license limits:
```
**** The model exceeds the demo license limits for nonlinear models of more than 1000 rows or columns
**** SOLVE from line 190 ABORTED, EXECERROR = 760
```

Model size: 779 equations x 1,723 variables (43,836 nonlinear elements).

---

## Root Cause

In the original GAMS model:
```gams
Set e(n,n) 'edge pairs' / n0.n1, n0.n2, ... /;  (* sparse 2D subset *)
Variable slp(n,n) 'positive slack';
Variable sln(n,n) 'negative slack';

eq1(e(i,j))..
   sum(k, sqr(x(i,k) - x(j,k))) =e= sqr(r(i) + r(j)) + slp(e) - sln(e);
```

Key observations:
1. `slp` and `sln` are declared over `(n,n)` (full cross product: 20x20 = 400 instances)
2. But they only appear in `eq1(e(i,j))` which is conditioned on edge set `e` (sparse: ~20 edges)
3. In the original NLP, only `e`-active instances of `slp`/`sln` matter

The MCP transformation generates `stat_slp(n,n)` and `stat_sln(n,n)` over the full `(n,n)` domain. The MCP model definition pairs `stat_slp.slp` and `stat_sln.sln`, but for the ~380 off-edge instances, these stationarity equations are trivially `0 =E= 0` (no gradient terms), while the corresponding `slp`/`sln` variables exist and are positive. GAMS requires every non-free, non-fixed variable to be matched with exactly one equation in MCP.

The fix should either:
1. Condition `stat_slp`/`stat_sln` on `e(n,n)` and fix off-edge `slp`/`sln` instances to 0
2. Or restrict the variable declaration domain to match the active equation domain

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/tricp.gms -o /tmp/tricp_mcp.gms
gams /tmp/tricp_mcp.gms lo=2
# 760 execution errors: "Unmatched variable not free or fixed"
# SOLVE ABORTED, EXECERROR = 760
```

---

## Proposed Fix

The stationarity equation builder needs to detect when a variable only participates in equations conditioned on a subset. For `slp(n,n)` which only appears in `eq1(e(i,j))`, the stationarity `stat_slp` should be conditioned on `e`:

```gams
stat_slp(i,j)$(e(i,j)).. ... =E= 0;
slp.fx(i,j)$(not e(i,j)) = 0;
```

This is similar to the multiplier domain widening pattern but in reverse — here we need to restrict the stationarity domain to match the active equation domain, rather than widen a multiplier domain.

---

## Related

- #1056 tricp: smax emission dimension mismatch (FIXED — separate compilation issue)
- #933 tricp: translation timeout (resolved by timeout increase)
- This is a domain/conditioning issue in the stationarity builder, not the expression emitter
