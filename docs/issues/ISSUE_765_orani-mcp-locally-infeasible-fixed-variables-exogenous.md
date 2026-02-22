# Orani MCP: Locally Infeasible Due to Fixed Exogenous Variables in Percentage-Change Model

**GitHub Issue:** [#765](https://github.com/jeffreyhorn/nlp2mcp/issues/765)
**Status:** OPEN — Not fixable (structurally infeasible linearized CGE model; see Investigation section below)
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
- **ISSUE_764 (mexss)**: Similar infeasibility pattern from accounting variable stationarity
- Other linearized CGE models (e.g., dyncge, irscge, korcge, lrgcge) may have the same problem

---

## Investigation Attempt (2026-02-22)

### Approach: Exclude Fixed Variables from MCP Stationarity (Option A)

**What was tried:**

1. Added a `fixed_variables: set[str]` field to `KKTSystem` in `src/kkt/kkt_system.py`
2. Modified `build_stationarity_equations()` in `src/kkt/stationarity.py` to detect variables
   where `.lo == .up` (fully fixed via `.fx`), skip stationarity equation generation for them,
   and record them in `KKTSystem.fixed_variables`

**Identified fixed variables in orani:**
- `df(c)`, `e(cm)`, `kappa(i)`, `phi`, `pm(c)`, `t(c)`, `v(ca)`, `ws`, `ye` — 9 variables

**Result: Fix did NOT work.**

Two cascading failures prevented this approach:

#### Failure 1: MCP Count Mismatch

Removing stationarity equations for 9 fixed variables (which eliminates 9 equation–variable
pairs from the MCP model statement) produces a count mismatch:

```
*** Error: Counts do not match in model mcp_model
    Unmatched free variables = 13
```

The emitter still declares all variables (including fixed ones), but their paired stationarity
equations are gone. The MCP requires a 1:1 equation–variable pairing. Fixing this would require
also removing the fixed variables from the MCP model statement and adding `.fx` handling in the
emitter — a much deeper change than just skipping stationarity generation.

#### Failure 2: Non-Fixed Variable Stationarity Equations Are Also Infeasible

Even after addressing the count mismatch, the **non-fixed variable** stationarity equations
are themselves structurally infeasible. For example:

```gams
stat_b.. nu_baltrade =E= 0;
stat_cn(c,s).. nu_con(c,s) =E= 0;
stat_cr.. nu_realc =E= 0;
```

These force equality constraint multipliers to zero. But the remaining stationarity equations
for other variables (e.g., `stat_p`, `stat_pk`, `stat_w`) require those same multipliers to
be nonzero to satisfy their own conditions. This creates a cascading infeasibility that cannot
be resolved by simply excluding fixed variables.

**Example cascade:**
- `stat_b.. nu_baltrade =E= 0;` forces `nu_baltrade = 0`
- `stat_et.. nu_exports + ((-1) * C) * nu_baltrade =E= 0;` then forces `nu_exports = 0`
- But other equations need `nu_exports ≠ 0` to satisfy their conditions

### Root Cause Analysis

The orani model is a **linearized percentage-change CGE model**, not a standard NLP. The
equations represent first-order approximations around an equilibrium, and the model's solution
structure is fundamentally different from what the NLP→MCP transformation assumes:

1. All variables represent **percentage changes** from a base equilibrium (not level values)
2. Many variables are fixed to represent exogenous policy shocks
3. The system of equations is a square linear system (N equations, N endogenous variables)
   that should be solved directly, not reformulated as KKT conditions
4. The stationarity equations for this linearized system are trivially constant (since the
   Lagrangian gradients w.r.t. percentage-change variables produce constant multiplier terms),
   making the resulting MCP structurally infeasible

### What Must Be Done Before Attempting Another Fix

1. **Model classification**: Add a pre-transformation heuristic that detects linearized CGE
   models (e.g., >30% of variables fixed, all equations are linear, all constraints are
   equalities). Such models should produce a warning and suggest solving directly as a
   square system rather than converting to MCP.

2. **Fixed-variable MCP handling**: If excluding fixed variables from stationarity is pursued,
   the full pipeline must be updated:
   - `build_stationarity_equations()`: skip fixed variables ✓ (done in attempt)
   - `emit_gams.py`: suppress fixed variable declarations in MCP model statement
   - `emit/model.py`: exclude fixed variables from equation–variable pairing
   - `complementarity.py`: exclude fixed-variable bound complementarity pairs

3. **Fundamental limitation**: Even with perfect fixed-variable handling, the orani model's
   non-fixed variable stationarity equations are structurally infeasible due to the linearized
   CGE nature of the model. This model class is **not suitable for NLP→MCP conversion** and
   should be explicitly excluded or warned about.

### Conclusion

**This issue is NOT fixable** within the current NLP→MCP architecture. The orani model is a
linearized percentage-change CGE model that represents a fundamentally different problem class
from the nonlinear optimization problems that KKT-based MCP conversion is designed for. The
recommended approach is to detect and warn about this model class rather than attempt conversion.
