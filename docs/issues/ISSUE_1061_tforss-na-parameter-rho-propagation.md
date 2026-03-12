# tforss: NA Parameter `rho` Propagation — 152 Execution Errors

**GitHub Issue:** [#1061](https://github.com/jeffreyhorn/nlp2mcp/issues/1061)
**Status:** OPEN
**Severity:** High — execution errors, model fails to solve
**Date:** 2026-03-12
**Affected Models:** tforss

---

## Problem Summary

The tforss model's generated MCP file initializes scalar `rho` to `/na/` (Not Available), causing 152 execution errors from NA propagation into stationarity equations and original model equations. The original model assigns `rho` inside a `loop(rhoset, ...)` block, but the MCP emitter only captures the initial `/na/` declaration value.

---

## Error Details

GAMS execution errors (152 total):
- **48 "RHS value NA" errors** in stationarity and model equations
- **82 "Matrix error - coefficient NA"** errors for variables in NA-affected equations
- **22 infeasibility errors** from missing initial values

Key affected equations:
```
stat_h(m).. (-1) * nu_cap(m) + (-1) * (rho / (1 - (1 + rho) ** (-life)) * nu(m)) * nu_ainvc =E= 0;
stat_v(s,k,at).. ... + (-1) * (mup * (1 + rho) ** age(at)) * nu_aplnt + ... =E= 0;
ainvc.. phik =E= rho / (1 - (1 + rho) ** (-life)) * sum(m, nu(m) * h(m));
aplnt.. phip =E= mup * sum((s,k,at), v(s,k,at) * (1 + rho) ** age(at));
```

All evaluate to NA because `rho = NA`.

Final status:
```
**** SOLVE from line 234 ABORTED, EXECERROR = 152
```

---

## Root Cause

In the original tforss model:
```gams
Scalar rho 'discount rate' / na /;

Set rhoset / rho-03, rho-05, rho-07, rho-10 /;
Parameter rhoval(rhoset) / rho-03 .03, rho-05 .05, rho-07 .07, rho-10 .1 /;

loop(rhoset,
   rho = rhoval(rhoset);
   Solve tforss using nlp minimizing phi;
   ...
);
```

The scalar `rho` is intentionally initialized to `NA` and then assigned a numeric value inside a parametric `loop` before each solve. The MCP emitter:
1. Correctly emits `rho /na/` (the declaration value)
2. Does NOT emit the loop-based assignment `rho = rhoval(rhoset)` or any equivalent

Since the MCP is a single-solve reformulation, it needs a concrete value for `rho`. The emitter should either:
- Emit `rho = rhoval('rho-03');` (first iteration value) before the solve
- Or emit a default value like `rho = 0.03;`

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/tforss.gms -o /tmp/tforss_mcp.gms
gams /tmp/tforss_mcp.gms lo=2
# 152 execution errors, SOLVE ABORTED
```

---

## Proposed Fix

This is a class of problem where the original model uses parametric solves inside loops. The MCP transformation needs to pick a concrete parameter value for the single MCP solve. Options:

1. **Detect loop-assigned scalars**: When a scalar is initialized to `/na/` and assigned inside a `loop` before a `Solve`, emit the first-iteration assignment value
2. **Use the last-assigned value**: Track the final assignment to `rho` before the last Solve statement and use that value
3. **Warn about NA parameters**: At minimum, warn when a parameter used in model equations has NA value

This is related to the broader issue of handling parametric/loop solves in MCP transformation.

---

## Related

- #907 tforss: NA propagation / KKT bugs / unmatched variable (overlapping issue)
- #1055 tforss: Domain violation $171 (FIXED by multiplier domain widening)
