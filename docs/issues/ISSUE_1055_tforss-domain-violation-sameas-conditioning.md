# tforss: Domain Violation ($171) in Stationarity — sameas Conditioning

**GitHub Issue:** [#1055](https://github.com/jeffreyhorn/nlp2mcp/issues/1055)
**Status:** OPEN
**Severity:** High — path_syntax_error, model fails to compile
**Date:** 2026-03-11
**Affected Models:** tforss

---

## Problem Summary

The tforss model's generated MCP file contains a domain violation in the stationarity equation for variable `r`. The equation `stat_r(c)$(cl(c))` references `nu_acutc` with a `sameas(c, 'pulplogs')` condition, but the `c` index in this context violates GAMS domain checking because the equation domain expects the subset `cl(c)` while the `sameas` condition references the parent set `c`.

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

Similarly, for `acutc` (scalar equation), the `sameas(c, 'pulplogs')` condition appears, which is from the condition `$cl(c)` or the specific `r(cl)` reference expansion.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/tforss.gms -o /tmp/tforss_mcp.gms
gams /tmp/tforss_mcp.gms lo=2
# Error $171 at stat_r equation
```

---

## Proposed Fix

Same class of bug as solveopt — the stationarity emitter needs to handle domain subset mismatches between variable and equation domains. When the equation domain `cl` is a subset of the variable domain `c`, the multiplier reference must use indices compatible with `cl`, not `c`.

---

## Related

- #907 tforss: NA propagation / KKT bugs / unmatched variable (different issue — about `$` condition propagation)
- Same root cause class as the solveopt domain violation issue
- This is a pre-existing issue on main; re-translation with current code exposes the bug
