# KKT: Empty Stationarity Equations from Conditional Equation Sparsity (weapons)

**GitHub Issue:** [#724](https://github.com/jeffreyhorn/nlp2mcp/issues/724)
**Status:** Open
**Severity:** High — Generated MCP code fails GAMS compilation; 35 EXECERROR instances
**Discovered:** 2026-02-13 (Sprint 19, after Issue #720 fixed the AD condition preservation)
**Affected Models:** weapons

---

## Problem Summary

After the Issue #720 fix (preserving dollar conditions on sum collapse and fixing the condition evaluator), the weapons model now generates MCP code that compiles but fails with 35 instances of:

```
**** MCP pair stat_x.x has empty equation but associated variable is NOT fixed
```

The root cause is that the stationarity equations `stat_x(w,t)` are generated for ALL `(w,t)` pairs, but many `(w,t)` combinations have `td(w,t) = 0`, making all terms in the stationarity equation evaluate to zero. GAMS treats these as "empty" equations, yet the paired variable `x(w,t)` is not fixed to zero, causing the MCP pairing to fail.

This is a broader instance of the same architectural gap identified in Issue #720: the pipeline does not propagate conditional equation sparsity through the KKT system.

---

## Reproduction

**Model:** `weapons` (`data/gamslib/raw/weapons.gms`)

**Command:**
```bash
python -m src.cli data/gamslib/raw/weapons.gms -o /tmp/weapons_mcp.gms
gams /tmp/weapons_mcp.gms
```

**GAMS output (35 errors):**
```
**** MCP pair stat_x.x has empty equation but associated variable is NOT fixed
     x(ICBM,2)

**** MCP pair stat_x.x has empty equation but associated variable is NOT fixed
     x(ICBM,3)

... (35 total instances)

**** SOLVE from line 140 ABORTED, EXECERROR = 35
```

**Affected `(w,t)` pairs (all 35):** These are the `(w,t)` combinations where `td(w,t) = 0`, meaning weapon `w` has no effectiveness against target `t`. Examples: `(ICBM,2)`, `(ICBM,3)`, `(ICBM,4)`, `(F-Bomber,1)` through `(F-Bomber,9)`, etc.

---

## Root Cause

### The weapons model structure

The weapons model has these key equations:

```gams
Equations
   maxw(w)     maximum number of weapons                (ineq, domain: w)
   minw(w,t)   minimum destruction per target per weapon (ineq, domain: w,t, conditional: $tm(t))
   probe(t)    minimum expected survival value           (ineq, domain: t)
   etd         expected total destruction                (eq, scalar)
   etdp        etd proxy definition                      (eq, scalar)
```

The critical equation is `minw`:

```gams
minw(w,t)$(tm(t))..  sum(w1, prob(w,w1,t)*x(w1,t))  =g=  tm(t) ;
```

This equation has domain `(w,t)` but a dollar condition `$(tm(t))` where `tm(t) = td("target",t)`. The `td` table only has nonzero "target" row values for targets 1, 5, 6, 8, 10, 17 (approximately 7 of 20 targets). So `minw` only generates ~35 equation instances (5 weapons × 7 active targets), not 100 (5 × 20).

### What happens in the KKT pipeline

1. **Stationarity computation (`src/kkt/stationarity.py`):** Differentiates each equation w.r.t. each variable. For `stat_x(w,t)` (stationarity of the Lagrangian w.r.t. `x(w,t)`), the derivative of `minw` contributes a term `td(w,t) * lam_minw(t)`. When `td(w,t) = 0`, this term and all other objective/constraint contributions are zero, making the entire stationarity equation empty.

2. **Multiplier declaration:** `lam_minw(t)` is declared over ALL `t` (20 elements), but should only exist for `t` where `tm(t) > 0` (~7 elements).

3. **Complementarity pairing:** The model pairs `comp_minw.lam_minw` over full domain `t`, but `comp_minw(t)$(tm(t))` only generates instances for ~7 targets. This creates a domain mismatch.

4. **Variable `x(w,t)` not fixed:** For `(w,t)` pairs where `td(w,t) = 0`, the stationarity equation is structurally zero but `x(w,t)` is still a free variable. GAMS requires that in an MCP, every variable either appears in a non-empty equation or is fixed.

### Generated code showing the issue

From `/tmp/weapons_mcp.gms`:

```gams
* Multiplier declaration (line 59)
    lam_minw(t)          * over ALL t

* Stationarity equation (line 101)
stat_x(w,t).. 0 + prod(...) * sum(..., 0) * nu_probe(t)
    + ... + td(w,t) * lam_maxw(w) + ((-1) * td(w,t)) * lam_minw(t) =E= 0;

* Complementarity (line 105)
comp_minw(t)$(tm(t)).. sum(w$(td(w,t)), x(w,t)) - tm(t) =G= 0;

* MCP pairing (line 130)
    comp_minw.lam_minw,
```

When `td(w,t) = 0`, the `stat_x(w,t)` equation reduces to `0 =E= 0` (empty).

---

## Fix Approach

### 1. Restrict multiplier domains to match equation conditions

**File:** `src/kkt/stationarity.py`

When an equation has a dollar condition (e.g., `minw(w,t)$(tm(t))`), the generated multiplier should carry the same condition:

```gams
* Current (wrong):
    lam_minw(t)

* Fixed:
    lam_minw(t)$(tm(t))
```

And the complementarity pairing domain must match.

### 2. Restrict stationarity equation domains

**File:** `src/kkt/stationarity.py`

The stationarity equation `stat_x(w,t)` should only be generated for `(w,t)` pairs where `x(w,t)` actually appears in at least one non-trivially-conditioned equation. For `(w,t)` where `td(w,t) = 0`:
- `x(w,t)` does not appear in `minw` (excluded by condition)
- `x(w,t)` does not appear in `maxw` (the `maxw(w)` equation sums over `t` with `$td(w,t)`, so `td(w,t)=0` excludes this term)
- If `x(w,t)` doesn't appear in ANY equation, it should be fixed to its bound value (typically 0) rather than paired with an empty stationarity equation.

### 3. Fix variables with empty stationarity equations

For variables that have no structural presence in any constraint (all coefficients are zero), the MCP requires either:
- **Fixing the variable** to a bound (`.fx = 0` or `.fx = .lo`)
- **Adding a trivial equation** (e.g., `stat_x(w,t)$(not td_active(w,t)).. x(w,t) =E= 0;`)

The cleanest approach is to detect which `(w,t)` pairs yield zero stationarity equations and emit `.fx` statements for those variables.

---

## Additional Context

- The `td(w,t)` table is a 6×20 matrix (6 weapons × 20 targets) with many zero entries
- The sparsity pattern is fully determined at compile time from the `td` Table data
- The `prob(w,w1,t)` parameter is computed from `td` via `prob(w,w1,t) = 1 - (1-td(w,t))**x.l(w1,t)`, so its sparsity follows `td`
- This issue also relates to how `sum(w$(td(w,t)), 0)` terms appear in the generated code — the derivative of `prod(...)` is producing zero-valued sums, suggesting the symbolic differentiation of `prod` may need review
- Similar conditional equation sparsity patterns may appear in other GAMSLib models
