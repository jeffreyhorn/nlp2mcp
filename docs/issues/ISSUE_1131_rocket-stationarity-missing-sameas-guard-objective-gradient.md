# rocket: Stationarity Missing sameas Guard on Objective Gradient

**GitHub Issue:** [#1131](https://github.com/jeffreyhorn/nlp2mcp/issues/1131)
**Status:** OPEN
**Severity:** High — MCP generates and PATH runs, but model is structurally infeasible (497 INFES)
**Date:** 2026-03-22
**Affected Models:** rocket (and potentially any model with element-specific variable references in objective)

---

## Problem Summary

The rocket model (`data/gamslib/raw/rocket.gms`) generates an MCP file that compiles and
runs PATH, but PATH reports MODEL STATUS 5 (Locally Infeasible) with 497 infeasible
equations. The root cause is a missing `sameas()` guard in the objective gradient.

The original objective is `Maximize final_velocity; obj.. final_velocity =E= ht("h50");`
which means the objective gradient w.r.t. `ht(h)` should be 1 only when `h = h50` and 0
otherwise. But the stationarity equation emits `-1` unconditionally for all `h`:

```gams
* WRONG (current):
stat_ht(h).. -1 + [constraint derivatives] =E= 0;

* CORRECT:
stat_ht(h).. -1$sameas(h,'h50') + [constraint derivatives] =E= 0;
```

This makes the stationarity equations infeasible for all `h != h50` because the `-1`
constant forces `LHS = -1 + 0 = -1 != 0` when no constraint derivatives contribute.

---

## Reproduction

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/rocket.gms -o /tmp/rocket_mcp.gms

# Run GAMS
gams /tmp/rocket_mcp.gms lo=2

# Expected:
# SOLVER STATUS     1 Normal Completion
# MODEL STATUS      5 Locally Infeasible
# 497 INFEASIBLE equations
```

---

## GAMS Error Output

```
**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      5 Locally Infeasible

RESOURCE USAGE, LIMIT          5.186 10000000000.000
ITERATION COUNT, LIMIT     11646    2147483647

FINAL STATISTICS
Inf-Norm of Complementarity . .  9.9592e-01 eqn: (stat_ht(h50))
Inf-Norm of Normal Map. . . . .  4.6388e+00 eqn: (stat_ht(h45))

REPORT SUMMARY :        0     NONOPT
                       497 INFEASIBLE (INFES)
```

Example infeasible equations:
```
stat_ht(h0)..  (0)*nu_df(h0) + (2)*nu_gf(h0) + nu_h_eqn(h0) - nu_h_eqn(h1)
  + nu_ht_fx_h0 + (0)*v(h0) + (0)*ht(h0) - piL_ht(h0) =E= 1 ;
  (LHS = 0, INFES = 1 ****)

stat_ht(h1)..  (59.5)*nu_df(h1) + (2)*nu_gf(h1) + nu_h_eqn(h1) - nu_h_eqn(h2)
  + (0)*v(h1) + (0)*ht(h1) - piL_ht(h1) =E= 1 ;
  (LHS = 0, INFES = 1 ****)
```

The `-1` from the objective gradient is moved to the RHS as `=E= 1`, but the LHS evaluates
to 0 for all `h != h50` because the constraint Jacobian terms vanish at the initial point.

---

## Root Cause

### The Original Model

```gams
Variables  final_velocity, ht(h), v(h), m(h), t(h), d(h), g(h), step;
...
Equations  obj, df(h), gf(h), h_eqn(h), v_eqn(h), m_eqn(h), ...;
obj..  final_velocity =E= ht("h50");
```

The objective variable `final_velocity` is linked to `ht("h50")` — a specific element
of the indexed variable `ht(h)`.

### The Derivative Bug

When computing `d(obj)/d(ht(h))`:
- The RHS of the objective is `ht("h50")`
- Differentiating `ht("h50")` w.r.t. `ht(h)` should produce a Kronecker delta:
  `1` if `h = h50`, `0` otherwise
- In GAMS syntax: `1$sameas(h, 'h50')`

The AD engine currently produces `Const(1)` unconditionally — it does not generate the
`sameas()` guard needed for element-specific variable references.

### Location in the AD Code

The differentiation of `VarRef('ht', ('h50',))` w.r.t. `VarRef('ht', ('h',))` occurs in:
- `src/ad/derivative_rules.py` — `_diff_varref()` function
- The function checks if indices match, but when one index is a concrete element (`h50`)
  and the other is a set variable (`h`), it should emit a `sameas(h, 'h50')` guard
  instead of either `Const(1)` (always matches) or `Const(0)` (never matches)

The current logic likely treats this as an uncontrolled index and produces `Const(1)` via
`_find_superset_in_domain()` or the fallback path, without the element-specific guard.

---

## Suggested Fix

In `_diff_varref()` (or its callers), when differentiating a concrete-element VarRef
(e.g., `ht("h50")`) w.r.t. a set-indexed VarRef (e.g., `ht(h)`):

1. Detect that the wrt index `h` is a set variable while the expr index `h50` is a
   concrete element
2. Instead of returning `Const(1)`, return a `SetMembershipTest` or equivalent AST node
   that emits `sameas(h, 'h50')` in the GAMS output
3. The stationarity equation then becomes:
   ```gams
   stat_ht(h).. -1$sameas(h,'h50') + ... =E= 0;
   ```

### Alternative Approach

Instead of fixing in the AD engine, handle at the KKT assembly level:
- When the objective references a specific element `ht("h50")`, split the stationarity:
  ```gams
  stat_ht('h50').. -1 + ... =E= 0;    * Only for h50
  stat_ht(h)$(not sameas(h,'h50')).. 0 + ... =E= 0;  * For all other h
  ```

---

## Verification Plan

After fix:
```bash
python -m src.cli data/gamslib/raw/rocket.gms -o /tmp/rocket_mcp.gms

# Verify sameas guard present
grep "stat_ht" /tmp/rocket_mcp.gms
# Should contain: sameas(h,'h50') or equivalent conditional

gams /tmp/rocket_mcp.gms lo=2
# Should: MODEL STATUS 1 or 2 (Optimal or Locally Optimal), not 5 (Infeasible)
```

---

## Files to Investigate

| File | Line | Relevance |
|------|------|-----------|
| `src/ad/derivative_rules.py` | `_diff_varref()` | Concrete-element vs set-variable index matching |
| `src/kkt/stationarity.py` | Objective gradient assembly | Where the `-1` constant enters `stat_ht` |
| `src/emit/equations.py` | Equation emission | Where `sameas` guard would be emitted |

---

## Impact

1 model blocked (rocket: PATH Locally Infeasible). May also affect other models where the
objective references a specific element of an indexed variable (e.g., `z = x("last")`).
