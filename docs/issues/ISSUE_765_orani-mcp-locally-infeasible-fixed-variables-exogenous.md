# Orani MCP: Locally Infeasible Due to Fixed Exogenous Variables in Percentage-Change Model

**GitHub Issue:** [#765](https://github.com/jeffreyhorn/nlp2mcp/issues/765)
**Status:** OPEN
**Severity:** High — MCP generates and compiles, but PATH solver reports locally infeasible
**Date:** 2026-02-16
**Affected Models:** orani

---

## Problem Summary

The orani model (`data/gamslib/raw/orani.gms`) generates an MCP file without Error 149
(after the ISSUE_670 fix), but PATH reports locally infeasible:

```
EXIT - other error
Residual: 3.410015e+00
Inf-Norm of Complementarity: 1.6690e+00
Inf-Norm of Normal Map: 1.6690e+00
```

The orani model is a **percentage-change CGE model** where many variables are fixed to
exogenous values representing policy parameters or shocks. The MCP formulation does not
correctly handle the distinction between endogenous and exogenous variables in this context.

---

## Original Model Structure

Orani uses a linearized (percentage-change) CGE formulation. Many variables are fixed
as exogenous parameters:

```gams
* Policy variables fixed exogenously (from orani.gms):
df.fx(c)    = 1;    * domestic final demand shifts
e.fx(cm)    = 1;    * export demand shifts
kappa.fx(i) = 3;    * capital stock by industry
phi.fx      = 0;    * exchange rate (numeraire)
pm.fx(c)    = -2;   * import prices
t.fx(c)     = 0;    * tariff rates
v.fx(ca)    = 0;    * agricultural variables
ws.fx       = 0;    * wage shifter
ye.fx       = 2;    * household income
```

The model has equations like:
```gams
indc(c,s,i).. x(c,s,i) =e= z(i) - (p(c,s) - sum(sp, alpha(c,sp,i)*p(c,sp)));
pric(i)..     sum(c, r(c,i)*p(c,"domestic")) =e= sum((c,sp), sc(c,sp,i)*p(c,sp)) + ...;
```

---

## Root Cause

**The fundamental issue:** Orani is a percentage-change linearization of a CGE model,
not a standard NLP. Variables like `phi`, `kappa`, `pm`, etc. are fixed to represent
the solution point around which the linearization is taken. When converted to MCP:

1. Fixed variables still get stationarity equations generated for them
2. The stationarity equations for fixed variables often reduce to constants ≠ 0
3. The `.fx` bounds force the variable to a specific value, but the corresponding
   stationarity equation may be unsatisfiable at that point

**Secondary issue:** The stationarity equations contain `sum(..., 0)` terms from
cross-indexed sums where the derivative is zero (same ISSUE_670 pattern but for
different variables), producing large but trivially-zero sums that don't simplify
before PATH sees them.

**Generated MCP structure:**
```gams
* Many variables fixed:
df.fx(c)    = 1;
phi.fx      = 0;
kappa.fx(i) = 3;
...

* Stationarity equations reference all constraint multipliers:
stat_b.. sum((c,s), 0) + ((-1) * sum((cp,sp), 0)) * nu_con(...) + ... [25 zero terms] =E= 0;
```

The `stat_b` equation (and similar for `stat_cn`, `stat_cr`, etc.) contain many zero sums
from constraints that don't depend on `b`, but the constant term from the constraints that
DO depend on `b` may be nonzero, making the equation `constant = 0` infeasible.

---

## Reproduction

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/orani.gms -o /tmp/orani_mcp.gms

# Run GAMS:
gams /tmp/orani_mcp.gms lo=2

# Expected output:
# **** SOLVER STATUS     1 Normal Completion
# **** MODEL STATUS      5 Locally Infeasible
# Residual: 3.410015e+00
# EXIT - other error
```

---

## Why This Happens

Orani is a **linearized CGE model** — the equations represent first-order approximations
around an equilibrium, not the equilibrium conditions themselves. The MCP reformulation
produces stationarity conditions for the nonlinear equations that underlie the
linearization, but:

1. The linearized model's variables are **percentage changes**, not levels
2. The equilibrium for the linearized model is at `all_variables = 0` (no change)
3. The NLP→MCP transformer doesn't recognize this structure

More concretely: orani has many variables fixed (`.fx`) that represent policy choices.
In the original model, fixing these variables is legitimate — the solver finds the
endogenous variables consistent with the fixed exogenous ones. But in the MCP:

- Fixed variables have `x.fx = value`, which forces them to a point
- The stationarity equation `stat_x` is then an equality that must hold at that fixed point
- If `stat_x` evaluates to a nonzero constant at the fixed point, the MCP is infeasible

---

## Suggested Fix

**Option A: Exclude fixed variables from MCP stationarity**

Variables that are fully fixed (`x.l = x.lo = x.up`) should not get stationarity equations
generated for them. Their contribution to the gradient is absorbed by the fixed-variable
bound multipliers. This would eliminate the infeasible stationarity conditions.

**Option B: Detect and warn about linearized CGE models**

Add a heuristic check: if >20% of variables are fixed exogenously before the solve, warn
that the model may be a linearized/percentage-change formulation that is not suitable for
direct NLP→MCP conversion.

**Option C: Simplify trivially-zero sums before PATH**

Apply expression simplification to eliminate `sum(..., 0)` terms from stationarity
equations, which would expose the actual non-zero constant terms that make certain
equations infeasible, and allow detection/handling of inconsistent equations.

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/kkt/stationarity.py` | `build_stationarity_equations()` — handling of fixed variables |
| `src/emit/emit_gams.py` | Detection of fixed variables in prolog |
| `src/ir/model_ir.py` | How variable bounds (.lo, .up, .l) are represented |
| `data/gamslib/raw/orani.gms` | Original model with percentage-change structure |

---

## Related Issues

- **ISSUE_670**: Cross-indexed sums (Error 149) — resolved; this issue is the next blocker
- **mexss issue**: Similar infeasibility pattern from accounting variable stationarity
- Other linearized CGE models (e.g., dyncge, irscge, korcge, lrgcge) may have the same problem
