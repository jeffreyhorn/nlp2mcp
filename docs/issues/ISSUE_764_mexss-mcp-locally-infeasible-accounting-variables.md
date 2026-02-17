# Mexss MCP: Locally Infeasible Due to Inconsistent Stationarity Equations for Accounting Variables

**GitHub Issue:** [#764](https://github.com/jeffreyhorn/nlp2mcp/issues/764)
**Status:** OPEN
**Severity:** High — MCP generates and compiles, but PATH solver reports locally infeasible
**Date:** 2026-02-16
**Affected Models:** mexss

---

## Problem Summary

The mexss model (`data/gamslib/raw/mexss.gms`) generates an MCP file without Error 149 or
unmatched equations (after the ISSUE_670 fix), but PATH reports locally infeasible:

```
EXIT - other error
Residual: 3.4551e+00
Inf-Norm of Complementarity: 1.9665e+00
Inf-Norm of Normal Map: 1.3621e+02
```

The stationarity equations for the auxiliary accounting variables `phieps`, `philam`, `phipsi`
are structurally inconsistent: they reduce to `±1 = 0` after simplification.

---

## Original Model Structure

Mexss uses auxiliary accounting variables to decompose the objective:

```gams
obj..    phi    =e= phipsi + philam + phipi - phieps;
apsi..   phipsi =e= sum((cr,i), pd(cr)*u(cr,i));
alam..   philam =e= sum((cf,i,j), muf(i,j)*x(cf,i,j))
                  + sum((cf,j), pic(cf)*v(cf,j))
                  + sum((cf,i), pe(cf)*e(cf,i));
api..    phipi  =e= sum((cf,j), pv(cf)*v(cf,j));
aeps..   phieps =e= sum((cf,i), pe(cf)*e(cf,i));
```

These equations define `phi`, `phipsi`, `philam`, `phipi`, `phieps` as linear cost
aggregators. They are **not free variables** in the usual MCP sense; they are accounting
identities that define the value of the objective decomposition.

---

## Root Cause

The KKT stationarity conditions for `phieps`, `philam`, and `phipsi` are derived from
differentiating all constraints w.r.t. these variables. Since they only appear in the
objective decomposition equations (`obj`, `alam`, `aeps`), the derivatives are:

- ∂L/∂phieps = -1 (from `obj`) + contributions from other constraints ≈ 0
- ∂L/∂philam = +1 (from `obj`) + contributions from other constraints ≈ 0
- ∂L/∂phipsi = +1 (from `obj`) + contributions from other constraints ≈ 0

The "contributions from other constraints" consist of 38+ multiplier terms, all of which
evaluate to zero because none of the other constraints depend on these variables. After
simplification the equations reduce to:

```gams
* Generated (simplified equivalent):
stat_phieps: -1 = 0;   -- always inconsistent
stat_philam:  1 = 0;   -- always inconsistent
stat_phipsi:  1 = 0;   -- always inconsistent
```

The actual generated equations are not simplified (they contain many `sum(..., 0)` terms)
but are semantically equivalent to these inconsistent equations. GAMS evaluates them
correctly as unsatisfied, causing PATH to report infeasibility.

```gams
* Actual generated equations (mexss_mcp.gms):
stat_phieps.. -1 + ((-1) * sum((cr,i), 0)) * nu_apsi + ((-1) * (sum(...0...) + ...)) * nu_alam
              + ... [38 zero-sum terms] =E= 0;
stat_philam.. 1 + ... [same pattern] =E= 0;
stat_phipsi.. 1 + ... [same pattern] =E= 0;
```

---

## Reproduction

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/mexss.gms -o /tmp/mexss_mcp.gms

# Run GAMS:
gams /tmp/mexss_mcp.gms lo=2

# Expected output:
# **** SOLVER STATUS     1 Normal Completion
# **** MODEL STATUS      5 Locally Infeasible
# Residual: 3.4551e+00
# EXIT - other error
```

---

## Why This Happens

The mexss model is formulated as an LP (linear program) with an objective function
expressed via auxiliary accounting variables. In the NLP→MCP transformation:

1. All variables (including `phi`, `phipsi`, etc.) get stationarity equations
2. The stationarity equation for an accounting variable v is: ∂L/∂v = 0
3. Since `phieps` only appears in `obj` (with coefficient -1) and `aeps` (with coefficient 1):
   - ∂L/∂phieps = -ν_obj + ν_aeps = 0 → so ν_aeps = ν_obj
   - But ν_obj = 1 (from the objective), so ν_aeps = 1
   - This should be satisfiable IF the multiplier bounds are handled correctly

The real issue may be that `phieps` is a **positive variable** (implicitly non-negative
via its definition) but the stationarity condition should account for its bounds. The
generated `stat_phieps` treats it as free, producing the inconsistency.

---

## Suggested Fix

**Option A: Detect and exclude pure accounting variables**

Variables that appear only in linear accounting equations (where the equation is a simple
definition, not a constraint) should be excluded from the MCP pairing or handled differently.
Their multipliers (ν_aeps, ν_alam, ν_apsi) should be substituted out via the stationarity
conditions.

**Option B: Strategy 1 / objective variable treatment**

Apply the same "strategy 1" logic used for the objective variable: if a variable is the
subject of a defining equality (like `phieps =e= ...`), its stationarity equation should
be the defining equation itself, not the KKT condition.

**Option C: Simplify zero-sum stationarity expressions before emission**

Apply algebraic simplification to detect when stationarity equations reduce to numeric
constants (impossible to satisfy as equalities) and raise a warning or remove those
variable/equation pairs from the MCP.

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/kkt/stationarity.py` | `build_stationarity_equations()` — how accounting vars are handled |
| `src/ad/objective.py` or similar | How objective structure is detected |
| `src/ir/model_ir.py` | ModelIR — how equalities vs inequalities are classified |
| `data/gamslib/raw/mexss.gms` | Original model with accounting structure |

---

## Related Issues

- **ISSUE_670**: Cross-indexed sums (Error 149) — resolved; this issue is the next blocker
- Similar pattern may affect other models with auxiliary cost-accounting variables
  (e.g., CGE models with decomposed cost functions)
