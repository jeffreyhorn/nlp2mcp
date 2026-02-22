# Mexss MCP: Locally Infeasible Due to Inconsistent Stationarity Equations for Accounting Variables

**GitHub Issue:** [#764](https://github.com/jeffreyhorn/nlp2mcp/issues/764)
**Status:** OPEN — Not fixable (root cause is incorrect `sameas` guard in indexed stationarity builder; see Investigation section below)
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
- **ISSUE_767**: `sameas` guard for per-instance `.fx` multipliers — the guard logic is the root cause
- **ISSUE_765 (orani)**: Similar infeasibility but caused by linearized CGE model structure
- Similar pattern may affect other models with auxiliary cost-accounting variables
  (e.g., CGE models with decomposed cost functions)

---

## Investigation Attempt (2026-02-22)

### Initial Analysis: Stationarity Equations

Generated the MCP for mexss and examined the stationarity equations:

```gams
stat_phieps.. -1 + nu_aeps =E= 0;
stat_philam.. 1 + nu_alam =E= 0;
stat_phipsi.. 1 + nu_apsi =E= 0;
stat_phipi.. 1 + nu_api =E= 0;
```

These are individually satisfiable (nu_aeps=1, nu_alam=-1, nu_apsi=-1, nu_api=-1). The
accounting variable stationarity equations are NOT the primary source of infeasibility.

### Actual Root Cause: Incorrect `sameas` Guard in `_add_indexed_jacobian_terms`

The real problem is in the stationarity equations for indexed primal variables like `e(c,i)`,
`u(c,i)`, `v(c,j)`, and `x(c,i,j)`. These equations have incorrect dollar conditions that
restrict multiplier terms to single instances.

**Example — `stat_e(c,i)`:**

```gams
stat_e(c,i)$(cf(c))..
    (((-1) * mue(i)) * nu_alam)$(sameas(c, 'steel') and sameas(i, 'ahmsa'))
  + (((-1) * pe(c)) * nu_aeps)$(sameas(c, 'steel') and sameas(i, 'ahmsa'))
  + sum(cf, lam_mbf(cf,i))
  + sum(cf, lam_me(cf))
  =E= 0;
```

The `$(sameas(c, 'steel') and sameas(i, 'ahmsa'))` condition restricts the `nu_alam` and
`nu_aeps` multiplier terms to ONLY the instance `e('steel','ahmsa')`. But the scalar equation
`alam` sums over `e(cf,i)` for ALL valid `(cf,i)` combinations — the Jacobian derivative
∂alam/∂e(c,i) = `mue(i)` is nonzero for all 5 instances where `c ∈ cf` (steel × 5 plants),
not just `('steel','ahmsa')`.

**How the bug manifests:**

1. The `alam` equation is scalar (no domain indices)
2. Its Jacobian w.r.t. `e(c,i)` has 5 nonzero entries: `(steel, ahmsa)`, `(steel, fundidora)`,
   `(steel, sicartsa)`, `(steel, hylsa)`, `(steel, hylsap)`
3. Variable `e` has 40 total instances (8 commodities × 5 plants)
4. The Issue #767 guard at `stationarity.py:1543` checks `len(entries) < len(instances)` →
   `5 < 40` → True → applies `sameas` guard
5. But the guard uses `entries[0]` (the FIRST entry only, typically `('steel','ahmsa')`) to
   build the `sameas` condition, ignoring the other 4 valid instances

**The guard is designed for a different case:** It was built for scalar `.fx` constraints like
`b_fx_s1.. b('s1') = value;` where only ONE instance of an indexed variable has a nonzero
Jacobian entry. For such constraints, `len(entries) == 1` and the guard correctly restricts
the multiplier to that single instance.

**But for scalar equations like `alam` that sum over multiple instances of an indexed variable,**
`len(entries) > 1` and the guard incorrectly restricts to the first entry only.

### Same Bug Affects Multiple Stationarity Equations

| Stationarity Eq | Scalar Constraint | Variable | Valid Instances | Guard Restricts To |
|-----------------|-------------------|----------|-----------------|-------------------|
| `stat_e(c,i)` | `alam` | `e(c,i)` | 5 (steel × 5 plants) | `(steel, ahmsa)` only |
| `stat_e(c,i)` | `aeps` | `e(c,i)` | 5 (steel × 5 plants) | `(steel, ahmsa)` only |
| `stat_u(c,i)` | `apsi` | `u(c,i)` | 5 (coke × 5 plants) | `(coke, ahmsa)` only |
| `stat_v(c,j)` | `alam` | `v(c,j)` | 3 (steel × 3 markets) | `(steel, guadalaja)` only |
| `stat_v(c,j)` | `api` | `v(c,j)` | 3 (steel × 3 markets) | `(steel, guadalaja)` only |
| `stat_x(c,i,j)` | `alam` | `x(c,i,j)` | 15 (steel × 5 × 3) | `(steel, ahmsa, guadalaja)` only |

This produces stationarity equations that are too restrictive — the multiplier terms only
contribute to one instance when they should contribute to all valid instances.

### Why This Is Not a Simple Fix

The fix requires changing how `_add_indexed_jacobian_terms()` handles the case where a scalar
constraint has multiple nonzero Jacobian entries for different instances of an indexed variable.
Instead of a single `sameas` guard on `entries[0]`, the code needs to:

1. **Group entries by their element indices** and determine if ALL instances of the variable
   within the constraint's summation domain are present
2. **If all instances in a subset are present**, use a subset condition (e.g., `$(cf(c))`)
   rather than `sameas`
3. **If only some instances are present**, generate a disjunction of `sameas` conditions
   (e.g., `$(sameas(i,'ahmsa') or sameas(i,'fundidora') or ...)`)

This requires:
- Understanding the constraint's summation structure (which sets are being summed over)
- Matching Jacobian entry indices against set membership
- Generating appropriate GAMS conditions (subset membership vs sameas disjunctions)

The Issue #767 guard at `stationarity.py:1536-1563` needs to be refactored from a simple
"first entry" guard to a proper "active domain" guard.

### What Must Be Done Before Attempting Another Fix

1. **Refactor the Issue #767 guard** in `_add_indexed_jacobian_terms()` (stationarity.py:1536-1563):
   - When `len(entries) > 1`, do NOT use `entries[0]` alone
   - Group entries by their variable indices
   - Determine if the entries cover a known subset (e.g., all elements of set `cf`)
   - Generate appropriate conditions: subset membership `$(cf(c))` if entries match a defined
     subset, or an `or`-disjunction of `sameas` calls if entries are arbitrary

2. **Add test cases** for scalar-constraint-to-indexed-variable Jacobian patterns:
   - Scalar equation summing over a subset of an indexed variable
   - Scalar equation summing over multiple subsets
   - Scalar equation with partial instance coverage (not matching any named subset)

3. **Verify mexss solves correctly** after the guard fix — the accounting variable stationarity
   equations (`stat_phieps`, etc.) are individually satisfiable, so fixing the `sameas` guard
   should make the full MCP system feasible.

### Conclusion

**This issue is NOT fixable** with a simple change. The root cause is the Issue #767 `sameas`
guard in `_add_indexed_jacobian_terms()` which incorrectly restricts scalar-constraint multiplier
terms to a single variable instance when the constraint actually references multiple instances.
The fix requires a non-trivial refactor of the guard logic to handle multi-entry Jacobian
patterns. This is an architectural improvement that should be planned as a dedicated workstream.
