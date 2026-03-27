# chenery: $171 Domain Violation — Parameters Declared Over Subset Indexed by Superset

**GitHub Issue:** [#1164](https://github.com/jeffreyhorn/nlp2mcp/issues/1164)
**Status:** OPEN
**Severity:** High — MCP fails to compile ($171)
**Date:** 2026-03-27
**Affected Models:** chenery, shale (and potentially any model where parameters/variables are declared over subsets but stationarity equations use the superset domain)

---

## Problem Summary

The stationarity builder maps concrete element indices back to the equation's domain variable (e.g., `i`), but parameters declared over a subset (e.g., `alp(t)` where `Set t(i)`) get indexed as `alp(i)`. GAMS strictly enforces that indices match the declared domain at compile time — `alp(i)` is a domain violation because `i` includes elements not in `t`, regardless of runtime dollar conditions.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/chenery.gms -o /tmp/chenery_mcp.gms --skip-convexity-check
gams /tmp/chenery_mcp.gms lo=2
# $171 Domain violation for set
```

**Error line:**
```gams
stat_e(i).. (alp(i) * nu_dh(i) + ...)$(t(i)) =E= 0;
****                    $171
```

`alp` is declared as `Parameter alp(t)` where `Set t(i)`. Using `alp(i)` violates GAMS domain checking.

**Also affects shale:**
```bash
python -m src.cli data/gamslib/raw/shale.gms -o /tmp/shale_mcp.gms --skip-convexity-check
gams /tmp/shale_mcp.gms lo=2
# $171 Domain violation for set
```

---

## Root Cause

In `_replace_indices_in_expr()` (stationarity.py), the `element_to_set` mapping maps ALL concrete elements to the equation's domain variable. For `stat_e(i)`, element `light-ind` maps to `i` (the equation domain). But `alp` is declared over `t` (a subset of `i`), so `alp(light-ind)` should become `alp(t)` (using the parameter's own domain variable), not `alp(i)`.

The existing `_replace_matching_indices` with `prefer_declared_domain=True` DOES use the declared domain for parameters — but only when the element-to-set mapping doesn't override it. For the stationarity case, `element_to_set` maps `light-ind → i` (the equation domain), and this override wins over the declared domain.

---

## Verified Behavior

```python
# alp(i) where alp has domain (t) and t is subset of i:
# GAMS rejects even within $(t(i)) condition
eq(i).. x(i) + alp(i)$(t(i)) =e= 0;  # $171 error
eq(i)$(t(i)).. x(i) + alp(i) =e= 0;  # $171 error (head condition)
eq(t).. x(t) + alp(t) =e= 0;          # OK (equation domain matches)
```

---

## Fix Approach

The stationarity builder needs to preserve subset domain indices for parameters and variables declared over subsets:

1. **In `_replace_matching_indices`:** When a parameter's declared domain position uses a subset (e.g., `t`) and the element-to-set mapping returns the superset (e.g., `i`), use the subset name instead.

2. **Alternative:** In `_replace_indices_in_expr`, for ParamRef/VarRef, check if the declared domain at each position is a subset of the equation domain. If so, use the subset name (parameter's declared domain variable) instead of the superset (equation's domain variable).

3. **Key check:** `model_ir.sets[t].domain == ('i',)` → `t` is a subset of `i`. When replacing indices for a ParamRef declared over `(t,)`, use `t` instead of `i`.

**Effort estimate:** 2-3 hours

---

## Related Issues

- PR #1163: Fixed sum-index-vs-condition shadowing (partial fix for chenery)
- #1147/#1160: MCP pairing fixes (stationarity condition to body)
