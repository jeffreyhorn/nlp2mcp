# Chenery MCP: Division By Zero in stat_pi Due to del(i) in Denominator

**GitHub Issue:** [#763](https://github.com/jeffreyhorn/nlp2mcp/issues/763)
**Status:** OPEN — Not fixable in Sprint 19 (requires AD condition propagation to guard denominator expressions)
**Severity:** High — MCP generates but GAMS aborts with EXECERROR = 1 (division by zero)
**Date:** 2026-02-16
**Affected Models:** chenery

---

## Problem Summary

The chenery model (`data/gamslib/raw/chenery.gms`) generates an MCP file without
Error 149 (after the ISSUE_670 fix), but GAMS aborts during execution with:

```
**** Exec Error at line 65: division by zero (0)
**** SOLVE from line 378 ABORTED
**** EXECERROR=1
```

---

## Original Model Structure

The chenery model uses a CES (Constant Elasticity of Substitution) production function:

```gams
Parameter
    del(i)  'distribution parameter'
    sig(i)  'elasticity of substitution'
    rho(i)  'CES parameter'   / ... /;

dvv(i)$(sig(i) <> 0)..
    vv(i) =e= (pi*(1 - del(i))/del(i))**(-rho(i)/(1 + rho(i)));
```

The `dvv` equation contains `del(i)` in the denominator: `pi * (1 - del(i)) / del(i)`.
If `del(i) = 0` for any sector, this expression is undefined.

---

## Root Cause

The stationarity equation for `pi` (the price index variable) differentiates `dvv(i)` w.r.t.
`pi`, producing a derivative that contains `del(i)` in the denominator:

```gams
* Generated stat_pi (line ~257 of chenery_mcp.gms):
stat_pi.. nu_fpr + sum(i$(sig(i) <> 0),
    ((-1) * ((pi * (1 - del(i)) / del(i)) ** ((-rho(i)) / (1 + rho(i)))
              * (-rho(i)) / (1 + rho(i)) / (pi * (1 - del(i)) / del(i))
              * del(i) * (1 - del(i)) / del(i) ** 2)) * nu_dvv(i))
    - piL_pi + piU_pi =E= 0;
```

The expression `del(i) ** 2` appears in the denominator. If `del(i) = 0`, this causes a
division by zero at model evaluation time.

The original `dvv` equation uses `$(sig(i) <> 0)` to guard against the singularity, but
the AD-generated derivative does not inherit a guard against `del(i) = 0`. In the chenery
model, the initial values of `del(i)` are set from parameter data and some sectors may
have `del(i) = 0` at initialization.

The generated MCP includes:
```gams
nu_dvv.fx(i)$(not (sig(i) <> 0)) = 0;
```
which correctly fixes multipliers for the excluded instances, but the `stat_pi` equation
still evaluates the derivative expression (including the `del(i)` denominator) before
applying bounds.

---

## Reproduction

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/chenery.gms -o /tmp/chenery_mcp.gms

# Run GAMS:
gams /tmp/chenery_mcp.gms lo=2

# Expected error in chenery_mcp.lst:
# **** Exec Error at line 65: division by zero (0)
# **** SOLVE from line 378 ABORTED
# **** EXECERROR=1
```

---

## Generated MCP (Relevant Sections)

```gams
* Initialization at line 65 (approximate):
p.l(i) = min(max(p.l(i), 1e-6), p.up(i));  * Protects p, not del(i)

* Problematic stationarity equation:
stat_pi.. nu_fpr + sum(i$(sig(i) <> 0),
    ((-1) * ((pi * (1 - del(i)) / del(i)) ** ((-rho(i)) / (1 + rho(i)))
              ...
              * del(i) * (1 - del(i)) / del(i) ** 2)) * nu_dvv(i))
    - piL_pi + piU_pi =E= 0;

* Multiplier fix (correct, but doesn't prevent expression evaluation):
nu_dvv.fx(i)$(not (sig(i) <> 0)) = 0;
```

---

## Suggested Fix

**Option A (Preferred): Add dollar condition to stat_pi**

The stationarity equation for `pi` should inherit the same guard as `dvv`:

```gams
stat_pi.. nu_fpr + sum(i$(sig(i) <> 0 and del(i) <> 0), ...) =E= 0;
```

Or equivalently, add an initialization guard in the MCP prolog:

```gams
del.l(i)$(del.l(i) = 0) = 1e-6;  * Or the original parameter value
```

**Option B: Emit safe initialization for denominator parameters**

At MCP generation time, detect when a parameter appears in a denominator in any equation
and emit a lower-bound guard in the initialization section of the MCP file.

**Option C: Propagate the dollar condition through AD**

When the AD differentiates a conditioned equation `eq(i)$(cond(i))`, the derivative
should inherit `cond(i)` as a guard in the resulting stationarity expression. This would
also fix other models with similar patterns.

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/emit/emit_gams.py` | MCP prolog generation — add safe initialization section |
| `src/ad/derivative_rules.py` | AD differentiation — propagate conditions through derivatives |
| `src/kkt/stationarity.py` | Stationarity equation generation — add condition inheritance |
| `data/gamslib/raw/chenery.gms` | Original model with CES production structure |

---

## Related Issues

- **ISSUE_670**: Cross-indexed sums (Error 149) — resolved, unblocking chenery MCP generation
- Similar pattern may affect other models with CES production functions using `del` parameters
