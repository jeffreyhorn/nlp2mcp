# MCP: GAMS Error 483 — Multiplier lam_minw Not Referenced in Equations (weapons)

**GitHub Issue:** [#720](https://github.com/jeffreyhorn/nlp2mcp/issues/720)
**Status:** Open
**Severity:** High — Generated MCP code fails GAMS compilation; model cannot be solved
**Discovered:** 2026-02-13 (Sprint 19, after Issue #713 fix corrected table data)
**Affected Models:** weapons

---

## Problem Summary

The weapons model successfully parses and generates MCP code, but the generated code fails GAMS compilation with Error 483: "Mapped variables have to appear in the model." The multiplier `lam_minw` is declared and mapped in the MCP model statement (`comp_minw.lam_minw`) but never appears in any equation body. This means the Jacobian derivative for the `minw` inequality constraint is incorrectly computed as zero.

---

## Reproduction

**Model:** `weapons` (`data/gamslib/raw/weapons.gms`)

**Command to reproduce:**
```bash
source .venv/bin/activate
python -m src.cli data/gamslib/raw/weapons.gms -o /tmp/weapons_mcp.gms
gams /tmp/weapons_mcp.gms lo=0
```

**Pipeline output:** MCP generation succeeds (all 5 stages pass).

**GAMS compilation error:**
```
**** 483  Mapped variables have to appear in the model
**** The following MCP errors were detected in model mcp_model:
**** 483 lam_minw no ref to var in equ.var
```

---

## Root Cause

The original weapons model has this inequality constraint:

```gams
minw(t)$tm(t).. sum(w$td(w,t), x(w,t)) =g= tm(t);
```

This constraint says: for each target `t` where `tm(t) > 0`, the total weapons assigned must be at least `tm(t)`.

The Jacobian of `minw(t)` w.r.t. the primal variable `x(w,t)` should be:
- `d/dx(w,t) [sum(w'$td(w',t), x(w',t))]` = `td(w,t)` (or 1 when `td(w,t) > 0`)

This non-zero Jacobian entry means `lam_minw(t)` (the multiplier for `minw`) should appear in the stationarity equation `stat_x(w,t)` with coefficient `td(w,t)`.

However, the generated MCP code shows the derivative as zero:

**In `stat_x(w,t)` (line 101 of generated MCP):**
```gams
stat_x(w,t).. 0 + prod(w__$(td(w__,t)), ...) * sum(w__$(td(w__,t)), 0) * nu_probe(t) + ... + 1 * lam_maxw(w) =E= 0;
```

Note `sum(w__$(td(w__,t)), 0)` — the derivative inside the sum is 0. And `lam_minw` does not appear at all.

**In `stat_prob(t)` (line 100):**
```gams
stat_prob(t).. ... + sum(w, 0 * lam_maxw(w)) =E= 0;
```

Again, `lam_minw` is absent.

The AD (automatic differentiation) or Jacobian assembly is computing `d/dx(w,t) [sum(w'$td(w',t), x(w',t))] = 0` when it should be the conditional indicator `td(w,t)`. This is likely because:

1. The dollar-conditioned sum `sum(w$td(w,t), x(w,t))` differentiates the body `x(w,t)` w.r.t. the same `x(w,t)`, but the summation index `w` conflicts with the derivative variable's index `w`, and the AD system may not correctly handle the Kronecker delta when the summation index matches the free index.

2. Or the derivative `d/dx(w,t)` of `sum(w'$cond, x(w',t))` is incorrectly evaluated. When `w' = w`, the derivative of `x(w',t)` w.r.t. `x(w,t)` should be 1 (times the condition `td(w,t)`), but the system may be treating the entire sum's derivative as 0.

---

## Relevant Code

- **Jacobian computation:** `src/ad/constraint_jacobian.py` — computes partial derivatives of constraint equations w.r.t. primal variables
- **Stationarity assembly:** `src/kkt/stationarity.py` — assembles `stat_x(w,t)` from gradient + J^T * lambda
- **MCP emission:** `src/emit/mcp_emitter.py` or `src/emit/expr_to_gams.py` — emits the final GAMS code
- **AD core:** `src/ad/ad_core.py` — symbolic differentiation engine

The bug is likely in how the AD handles differentiation of `Sum` expressions where the summation index overlaps with the differentiation variable's index.

---

## Expected Behavior

The stationarity equation `stat_x(w,t)` should include a term like:

```gams
stat_x(w,t).. ... + td(w,t) * lam_minw(t) + ... =E= 0;
```

Or equivalently:

```gams
stat_x(w,t).. ... + 1$td(w,t) * lam_minw(t) + ... =E= 0;
```

This would make `lam_minw` appear in the equation body, satisfying GAMS Error 483 requirements.

---

## Context

The weapons model is a classic GAMSLib NLP model (Bracken & McGill, 1973) that optimizes weapon allocation across targets. It uses `prod()` for survival probabilities and `sum()` for weapon counts. The model structure is:
- Objective: maximize expected damage `tetd = sum(t, mv(t) * (1 - prod(w$td(w,t), (1-td(w,t))^x(w,t))))`
- Constraints: `maxw(w)` (weapon availability), `minw(t)` (minimum weapons per target)
- The `minw` constraint is the one whose multiplier is dropped from the KKT system
