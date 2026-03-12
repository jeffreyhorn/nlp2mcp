# tforss: Domain Violation ($171) in Stationarity — sameas Conditioning

**GitHub Issue:** [#1055](https://github.com/jeffreyhorn/nlp2mcp/issues/1055)
**Status:** FIXED
**Severity:** High — path_syntax_error, model fails to compile
**Date:** 2026-03-11
**Fixed:** 2026-03-12
**Affected Models:** tforss

---

## Problem Summary

The tforss model's generated MCP file contains a domain violation in the stationarity equation for variable `r`. The equation `stat_r(c)$(cl(c))` references `nu_lbal` with a `sameas(c, 'pulplogs')` condition, but the `c` index in this context violates GAMS domain checking because the equation domain expects the subset `cl(c)` while the `sameas` condition references the parent set `c`.

---

## Error Details

GAMS compilation error:
```
stat_r(c)$(cl(c)).. nu_lbal(c) + (((-1) * muc) * nu_acutc)$(sameas(c, 'pulplogs')) =E= 0;
                               $171
**** 171  Domain violation for set
```

The equation is conditioned on `cl(c)` (log types subset), and `nu_lbal` is the multiplier for `lbal(cl)`. The reference `nu_lbal(c)` uses index `c` (the parent set) where `cl` is expected.

---

## Root Cause

In the original model:
```gams
Set c 'commodities' / pulp, pulplogs, sawlogs, sawtimber /
    cl(c) 'log types' / pulplogs, sawlogs /
    cf(c) 'final products' / pulp, sawtimber /;

lbal(cl).. r(cl) =E= sum((s,k,at), ymf(at,k,s,cl)*v(s,k,at));
acutc..    phil =E= muc*sum(cl, r(cl));
```

The variable `r(c)` has domain `c` (parent set), but equation `lbal(cl)` uses domain `cl` (subset). The stationarity for `r(c)` w.r.t. `lbal(cl)` should condition on `cl(c)` and use `nu_lbal(cl)` with the subset index. Instead, the emitter uses `nu_lbal(c)`, causing the domain violation.

---

## Fix

This issue was already resolved by PR #1058 (Fix #1053: multiplier domain widening). The multiplier domain widening mechanism:

1. Detects that `lbal` has domain `cl` which is a subset of variable `r`'s domain `c`
2. Widens `nu_lbal` declaration from `(cl)` to `(c)` so `nu_lbal(c)` is domain-valid
3. Emits `.fx` guard: `nu_lbal.fx(c)$(not (cl(c))) = 0;` to fix inactive instances

The generated MCP now compiles without $171 errors. The model has separate pre-existing issues (NA propagation, execution errors from #907) that prevent it from solving, but the compilation domain violation is resolved.

---

## Verification

```
nu_lbal(c)          — declared over parent set c (widened from cl)
stat_r(c)$(cl(c)).. nu_lbal(c) + ...  — valid reference
nu_lbal.fx(c)$(not (cl(c))) = 0;      — guard for inactive instances
```

No $171 compilation errors in GAMS output.

---

## Related

- #1053 solveopt domain violation (same fix mechanism — multiplier domain widening)
- #907 tforss: NA propagation / KKT bugs / unmatched variable (separate issue, still open)
