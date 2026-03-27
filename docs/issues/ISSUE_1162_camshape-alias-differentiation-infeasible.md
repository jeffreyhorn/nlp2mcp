# camshape: Incorrect Alias Differentiation Causes MODEL STATUS 5 (Infeasible)

**GitHub Issue:** [#1162](https://github.com/jeffreyhorn/nlp2mcp/issues/1162)
**Status:** OPEN
**Severity:** High — MODEL STATUS 5 (Locally Infeasible)
**Date:** 2026-03-26
**Parent Issue:** #1111 (Alias-Aware Differentiation)
**Affected Models:** camshape (and potentially other models with lead/lag in nonlinear terms and alias indices)

---

## Problem Summary

After fixing compilation errors (#1147) and MCP pairing (#1160), camshape compiles and solves but returns MODEL STATUS 5 (Locally Infeasible). The stationarity equations have incorrect derivatives caused by alias-confused differentiation.

The convexity constraint `convexity(i).. -r(i-1)*r(i) - r(i)*r(i+1) + 2*r(i-1)*r(i+1)*cos(d_theta) =l= 0` contains products of the same variable at different lead/lag positions. When differentiating w.r.t. `r(i)`, the AD system incorrectly treats `r(i-1)` and `r(i+1)` as dependent on `r(i)` because `i` and `j` are aliased.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/camshape.gms -o /tmp/camshape_mcp.gms --skip-convexity-check
gams /tmp/camshape_mcp.gms lo=2
# MODEL STATUS 5 (Locally Infeasible)
```

---

## Root Cause

The convexity constraint:
```gams
convexity(middle(i)).. -r(i-1)*r(i) - r(i)*r(i+1) + 2*r(i-1)*r(i+1)*cos(d_theta) =l= 0;
```

Correct derivative `d/dr(i)` of `-r(i-1)*r(i) - r(i)*r(i+1) + 2*r(i-1)*r(i+1)*cos(d_theta)`:
```
= -r(i-1) - r(i+1) + 0
= -(r(i-1) + r(i+1))
```

(The `2*r(i-1)*r(i+1)*cos(d_theta)` term doesn't depend on `r(i)`, so its derivative is 0.)

**Actual output in stat_r(i):**
```
((-1) * r(i)) - r(i)) * lam_convexity(i)
```
This equals `-2*r(i) * lam_convexity(i)`, which is WRONG. It should be `-(r(i-1) + r(i+1)) * lam_convexity(i)`.

The AD system produces `-r(i) - r(i)` instead of `-r(i-1) - r(i+1)` because after index substitution and differentiation, the lead/lag offset positions `i-1` and `i+1` are collapsed to `i` — likely because the alias relationship between `i` and `j` confuses the offset resolution.

Additionally, the warning `Multi-pattern Jacobian: detected 2 derivative patterns for convex_edge1/r but could not pair a minority entry` suggests the Jacobian has structural issues for these lead/lag alias terms.

---

## Affected Files

- `src/ad/derivative_rules.py` — Lead/lag differentiation through alias indices
- `src/ad/constraint_jacobian.py` — Index substitution and offset resolution for alias-related lead/lag
- `src/ad/ad_core.py` — Core differentiation engine

---

## Fix Approach

1. Investigate how `_substitute_indices` handles `r(i-1)` when `i` is aliased to `j` — the offset should be preserved as `i-1`, not collapsed to `i`
2. Check if `differentiate_expr` correctly distinguishes `r(i)`, `r(i-1)`, and `r(i+1)` as separate variable instances when `i` has aliases
3. The fix likely involves preserving lead/lag offsets during index substitution so that `r(i-1)` and `r(i+1)` are treated as different from `r(i)` during differentiation
4. This is related to parent issue #1111 (Alias-Aware Differentiation) — the alias matching should NOT match across different offset positions

**Effort estimate:** 4-6 hours (deep AD investigation)
