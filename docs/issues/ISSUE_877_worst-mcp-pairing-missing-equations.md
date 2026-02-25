# worst: MCP Model Pairing Error — Dollar-Conditioned Equations Dropped from KKT

**GitHub Issue:** [#877](https://github.com/jeffreyhorn/nlp2mcp/issues/877)
**Status:** OPEN
**Severity:** High — Model compiles but GAMS rejects MCP model ($483)
**Date:** 2026-02-25
**Affected Models:** worst

---

## Problem Summary

The worst model translates to MCP but GAMS rejects it with error $483 ("Mapped variables
have to appear in the model"). The stationarity equation `stat_q(t)` is emitted as
`0 =E= 0` — completely empty — because the original equations `dd1` and `dd2` that
reference variable `q(t)` were dropped entirely from the KKT system.

---

## Error Details

```
 182  Solve mcp_model using MCP;
****                           $483
```

GAMS elaboration:
```
**** 483 q no ref to var in equ.var
```

The MCP model declaration pairs `stat_q.q`, but `stat_q` does not reference variable `q`
because it was generated as `stat_q(t).. 0 =E= 0;`.

---

## Root Cause

The original model has 6 equations, including two dollar-conditioned equations:

```gams
dd1(i,t,j)$pdata(i,t,j,"strike")..
   d1(i,t,j) =e= (log(f(i,t)/pdata(i,t,j,"strike")) + 0.5*sqr(q(t))*tdata(t,"term"))
              /  (q(t)*sqrt(tdata(t,"term")));

dd2(i,t,j)$pdata(i,t,j,"strike")..
   d2(i,t,j) =e= d1(i,t,j) - q(t)*sqrt(tdata(t,"term"));
```

These equations are **completely missing** from the emitted MCP — they don't appear in
the Equations declaration, have no equation definitions, and are absent from the Model
block. Without `dd1` and `dd2`:

1. No multipliers `nu_dd1` or `nu_dd2` are created
2. The stationarity equation for `q` has no Jacobian terms: `d(dd1)/dq * nu_dd1 + d(dd2)/dq * nu_dd2`
3. `stat_q(t)` becomes `0 =E= 0`, which doesn't reference `q`
4. GAMS raises $483 because the MCP pairing `stat_q.q` is invalid

The equations are likely dropped during constraint partitioning or Jacobian computation
because their dollar conditions (`$pdata(i,t,j,"strike")`) involve a parameter-based
condition that the pipeline cannot evaluate at compile time.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/worst.gms -o /tmp/worst_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/worst_mcp.gms action=c

# Verify dd1/dd2 are missing:
grep 'dd1\|dd2' /tmp/worst_mcp.gms
# Expected: nothing (equations completely absent)
```

---

## Suggested Fix

1. **Investigate where dd1/dd2 are lost**: Check `normalize_model()`,
   `compute_constraint_jacobian()`, and `assemble_kkt_system()` to find where
   dollar-conditioned equations with parameter-based conditions are dropped.

2. **Preserve equations with unevaluable conditions**: Even if the condition
   `$pdata(i,t,j,"strike")` can't be evaluated at compile time, the equation should
   still be included in the KKT system. The condition should be propagated to the
   emitted equality constraint and its multiplier.

3. **Alternative**: Emit the equation without the dollar condition over the full domain
   and let GAMS handle the conditional evaluation at runtime.

**Effort estimate:** ~3-4h

---

## Files Likely Affected

| File | Change |
|------|--------|
| `src/kkt/assemble.py` | Preserve dollar-conditioned equations in KKT assembly |
| `src/ad/constraint_jacobian.py` | Handle equations with unevaluable dollar conditions |
| `src/ir/normalize.py` | Ensure dollar-conditioned equations aren't filtered out |

---

## Related Issues

- **Issue #871** (partial): camcge stationarity subset conditioning — related domain filtering
