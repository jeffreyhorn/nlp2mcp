# meanvar: Portfolio Quadratic Alias Gradient Mismatch

**GitHub Issue:** [#1139](https://github.com/jeffreyhorn/nlp2mcp/issues/1139)
**Status:** OPEN
**Severity:** Medium — objective mismatch (12.3%)
**Date:** 2026-03-23
**Parent Issue:** #1111 (Alias-Aware Differentiation)
**Affected Models:** meanvar

---

## Problem Summary

The meanvar (mean-variance portfolio) model uses a classic quadratic form with
aliased indices:

```gams
Alias(i, j);
Variable x(i);
obj.. z =e= sum((i,j), x(i) * q(i,j) * x(j));
```

This is the canonical case that the Sprint 23 Day 3 multi-matching fix was
designed for. The fix works correctly for dispatch (which has the same pattern),
but meanvar still mismatches.

| Model | NLP Objective | MCP Objective | Rel Diff |
|-------|--------------|--------------|----------|
| meanvar | 0.0308 | 0.0270 | 12.3% |

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/meanvar.gms -o /tmp/meanvar_mcp.gms
gams /tmp/meanvar_mcp.gms lo=2
# Objective: 0.027, expected: 0.0308
```

---

## Root Cause Analysis

The meanvar model is structurally similar to dispatch's bilinear term, so the
multi-matching fix should apply. Possible reasons for residual mismatch:

1. **Additional constraints with aliases**: The model may have inequality
   constraints that use aliased indices, producing incorrect complementarity
   equations.

2. **Bound interaction**: Variable bounds combined with alias-aware gradients
   may create inconsistent KKT conditions.

3. **Objective structure differences**: The objective may include terms beyond
   the simple quadratic that interact with the alias fix incorrectly.

### Investigation Steps

1. Generate the MCP and inspect the `stat_x(i)` equation for correctness
2. Compare with the hand-derived gradient: `∂/∂x(i) sum((i,j), x(i)*q(i,j)*x(j)) = sum(j, (q(i,j) + q(j,i)) * x(j))`
3. Check if the meanvar model has additional constraints beyond the portfolio balance
4. Run finite difference validation on specific gradient entries

---

## Files

- `src/ad/derivative_rules.py` — `_partial_collapse_sum`
- `data/gamslib/raw/meanvar.gms` — Source model

## Current Status (2026-03-30)

Translates and solves to MODEL STATUS 1 Optimal, but objective does not match the NLP reference. Same alias differentiation root cause as qabel/abel (#1137): `_alias_match` in `derivative_rules.py` incorrectly handles alias-bound indices in sum contexts.
