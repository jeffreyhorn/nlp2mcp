# iswnm: Translation Timeout — Empty Set nb Causes Instance Explosion

**GitHub Issue:** [#1228](https://github.com/jeffreyhorn/nlp2mcp/issues/1228)
**Status:** OPEN
**Severity:** High — translation timeout (300s)
**Date:** 2026-04-06
**Affected Models:** iswnm
**Supersedes:** #931 (updated with specific root cause: empty set nb)

---

## Problem Summary

The iswnm model (Indus Surface Water Network Submodule, GAMSlib SEQ=164) parses
successfully (~74s) but times out during Jacobian/KKT translation (>300s). The
root cause is that set `nb` has 0 members, which creates an unevaluable
`SetMembershipTest` condition on equation `nbal`. When the instance enumerator
cannot evaluate a condition, it conservatively includes ALL instances by default,
leading to a massive Cartesian product explosion.

| Metric | Value |
|--------|-------|
| Parse Time | ~74s |
| Translate Time | TIMEOUT (>300s) |
| Variables | 4 |
| Equations | 2 |
| Sets | 13 (largest: nn=50, c=43, n=40) |

---

## Root Cause

Set `nb` is defined with 0 members in the model data. Equation `nbal` has a
condition involving `nb` membership (e.g., `nbal(n)$nb(n)` or similar). During
instance enumeration:

1. The `SetMembershipTest` for `nb` cannot be statically evaluated because the
   set is empty (no members to match against)
2. The instance enumerator's fallback behavior is to include all instances when
   a condition cannot be evaluated
3. With large sets (nn=50, c=43, n=40), the Cartesian product of variable
   instances explodes
4. The Jacobian must compute derivatives for every equation-variable instance
   pair, exceeding the 300s timeout

Despite having only 4 variables and 2 equations, the 3-dimensional variable
`f(n,n1,m)` over large network sets creates O(50 * 50 * 12) = 30,000+ variable
instances. Combined with the unconditional equation instances, the Jacobian
computation becomes intractable.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/iswnm.gms -o /tmp/iswnm_mcp.gms
# Parse: ~74s (succeeds)
# Translate: TIMEOUT after 300s
```

---

## Model Structure

- **File**: `data/gamslib/raw/iswnm.gms` (691 lines)
- **Type**: LP (all derivatives are constants)
- **Variables**: `rcont(n,m)`, `canaldiv(c,m)`, `f(n,n1,m)`, `vol`
- **Equations**: `nbal`, plus objective
- **Sets**: 13 total; key sets: `nn` (50 members), `c` (43), `n` (40), `m` (12)
- **Empty set**: `nb` — 0 members, used in condition on `nbal`

---

## Potential Fix Approaches

1. **Empty set detection**: During instance enumeration, detect sets with 0
   members and evaluate `SetMembershipTest` conditions against them as always-false,
   pruning those equation instances entirely
2. **Static condition evaluation**: Before Jacobian computation, pre-evaluate
   conditions that reference empty sets and eliminate dead instances
3. **LP fast path with sparsity**: For LP models, extract coefficients directly
   from the IR without symbolic differentiation, avoiding the instance explosion
4. **Instance count threshold**: Before starting Jacobian computation, estimate
   the instance count and abort early with a diagnostic message if it exceeds
   a threshold

---

## Files Involved

- `data/gamslib/raw/iswnm.gms` — Source model (691 lines)
- `src/kkt/stationarity.py` — Instance enumeration and condition evaluation
- `src/kkt/jacobian.py` — Jacobian computation (bottleneck)
- `src/ir/model_ir.py` — SetMembershipTest condition representation
- `docs/issues/ISSUE_931_iswnm-translation-timeout.md` — Superseded issue
