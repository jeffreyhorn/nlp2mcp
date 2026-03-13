# agreste: MCP Structurally Infeasible — Missing Jacobian Terms and Alias Handling Bug

**GitHub Issue:** [#1068](https://github.com/jeffreyhorn/nlp2mcp/issues/1068)
**Model:** agreste (SEQ=88) — Agreste Farm Level Model of NE Brazil
**Type:** LP
**Category:** KKT construction bug (Jacobian / alias index handling)

---

## Summary

The agreste model is structurally infeasible (model_status=4, 0 iterations) because the stationarity equations are missing constraint Jacobian terms. Two bugs: (1) the `lam_landb(s)` multiplier term is entirely absent from `stat_xcrop(p,s)` due to a `$sc(s)` conditional wrapping the sum; (2) `stat_lswitch(s)` uses diagonal `ldp(s,s)` instead of the proper transposed summation `sum(sp, ldp(sp,s))` due to incorrect alias resolution.

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/agreste.gms -o data/gamslib/mcp/agreste_mcp.gms
cd /tmp && gams /path/to/data/gamslib/mcp/agreste_mcp.gms lo=2 o=agreste.lst
# Expected: MODEL STATUS 4 (Infeasible), 0 iterations, 33 INFES markers
```

## Model Structure

- **Sets**: `s` (land types, 9 elements), `sp` alias of `s`, plus `p` (crops), `r` (livestock), `c` (commodities), etc.
- **Objective**: Maximize `yfarm` (farm income)
- **Key constraint**: `landb(s).. sum(p$ps(p,s), a(p)*xcrop(p,s))$sc(s) + sum(sp, ldp(s,sp)*lswitch(sp)) + sum(r, lio(s,r)*xliver(r)) =L= landc(s)`
- **NLP reference objective**: 17706.43

## Root Cause

### Bug 1: Missing `lam_landb(s)` in `stat_xcrop(p,s)`

The `landb(s)` inequality constraint contains `xcrop(p,s)` inside `sum(p$ps(p,s), a(p)*xcrop(p,s))$sc(s)`. The derivative w.r.t. `xcrop(p,s)` should produce `a(p)$ps(p,s)$sc(s) * lam_landb(s)` in the stationarity equation.

**Expected** in `stat_xcrop(p,s)`:
```gams
... + a(p)$(ps(p,s) and sc(s)) * lam_landb(s) ...
```

**Actual**: The `lam_landb(s)` term is **entirely absent** from `stat_xcrop`. The `$sc(s)` conditional wrapping the entire sum likely causes the derivative extraction to fail to recognize that `xcrop(p,s)` participates in `landb(s)`.

### Bug 2: Wrong alias handling in `stat_lswitch(s)`

The `landb(s)` constraint contains `sum(sp, ldp(s,sp)*lswitch(sp))`. Differentiating w.r.t. `lswitch(s)` should give `sum(s', ldp(s',s) * lam_landb(s'))` (transposed sum over the first index).

**Expected**:
```gams
stat_lswitch(s).. sum(sp, ldp(sp,s) * lam_landb(sp)) + ... =E= 0;
```

**Actual**:
```gams
stat_lswitch(s).. ldp(s,s) * lam_landb(s) + (ldp(s,s) * lam_landb(s+1))$(...) + ... =E= 0;
```

The code uses `ldp(s,s)` (diagonal) for all terms instead of properly transposing the parameter indices. The alias `sp` is substituted with `s` throughout, collapsing the summation into a diagonal lookup with manual neighbor enumeration.

## PATH Solver Output

```
MODEL STATUS      4 Infeasible
0 iterations (structural infeasibility detected at preprocessing)
33 INFES markers, 12 labeled INFEASIBLE in solution report
```

Key infeasible equations:
- `stat_cons(one/two/three)`: `(-1)*vsc` = -934 each
- `stat_cropcost/labcost/rationr/revenue/vetcost`: constant +1 or -1 RHS
- `arev`: LHS = 56220 (accounting equation at zero initial point)

## Fix Approach

1. **Bug 1**: Fix the Jacobian builder to correctly detect variable participation inside dollar-conditioned sums. When `sum(p$cond, f(p,s)*x(p,s))$outer_cond` appears in a constraint, the derivative w.r.t. `x(p,s)` must carry both `$cond` and `$outer_cond`.
2. **Bug 2**: Fix alias resolution in the stationarity builder. When differentiating `sum(sp, ldp(s,sp)*lswitch(sp))` w.r.t. `lswitch(s)`, the result should be `sum(s', ldp(s',s))` with proper index transposition, not diagonal `ldp(s,s)`.

## Files

- `data/gamslib/raw/agreste.gms` — original LP model
- `data/gamslib/mcp/agreste_mcp.gms` — generated MCP
- Key MCP equation: `stat_xcrop(p,s)` (missing `lam_landb`), `stat_lswitch(s)` (wrong alias)
