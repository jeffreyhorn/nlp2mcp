# prolog: Multiplier Dimension Mismatch — lam_mp Missing Index t

**GitHub Issue:** [#1227](https://github.com/jeffreyhorn/nlp2mcp/issues/1227)
**Status:** FIXED
**Severity:** High — was GAMS Error 148 (now resolved)
**Date:** 2026-04-06
**Affected Models:** prolog
**Supersedes:** #1070 (originally described as CES singular Jacobian)

---

## Problem Summary

The prolog model (GAMS/MPSGE Prototype: Shoven-Whalley, GAMSlib) fails with
GAMS Error 148 during MCP compilation. The root cause is a multiplier dimension
mismatch in the stationarity equation for variable `p(i)`.

Equation `mp(i,t)` references variable `p(i)`. When generating the stationarity
equation `stat_p(i)`, the multiplier `lam_mp` appears in two inconsistent forms:

- `lam_mp(i,t)` — correct, inside `sum(t, ...)` context
- `lam_mp(i)` — incorrect, missing the `t` dimension

This dimension mismatch causes GAMS Error 148 (symbol dimension mismatch).

---

## Root Cause

The equation `mp(i,t)` is 2-dimensional, so its Lagrange multiplier must be
`lam_mp(i,t)`. When building `stat_p(i)`, the stationarity builder must sum
over the extra dimension `t`:

```gams
stat_p(i).. sum(t, lam_mp(i,t) * d_mp_dp(i,t)) + ... =E= 0;
```

However, the current code emits `lam_mp(i)` in some terms (outside the sum or
with incorrect index propagation), creating a dimension conflict:

```gams
* INCORRECT — mixes lam_mp(i,t) and lam_mp(i)
stat_p(i).. sum(t, lam_mp(i,t) * ...) + lam_mp(i) * ... =E= 0;
```

The issue likely occurs in `stationarity.py` when the equation domain `(i,t)`
is partially matched against the variable domain `(i)` — the `t` index from
the equation is not consistently carried through to all multiplier references.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/prolog.gms -o /tmp/prolog_mcp.gms
gams /tmp/prolog_mcp.gms lo=2
# GAMS Error 148: symbol dimension mismatch on lam_mp
```

---

## GAMS Errors

```
*** Error 148: symbol 'lam_mp' has dimension 2 but is used with dimension 1
```

The error occurs in the stationarity equation `stat_p` where `lam_mp(i)` appears
but `lam_mp` was declared as `lam_mp(i,t)`.

---

## Model Structure

- **File**: `data/gamslib/raw/prolog.gms` (~160 lines)
- **Aliases**: `Alias(i,j)`, `Alias(g,gp)`
- **Key equation**: `mp(i,t)` — references variable `p(i)`
- **Key variable**: `p(i)` — prices (1-dimensional)
- **Multiplier**: `lam_mp(i,t)` — must be 2-dimensional to match equation `mp(i,t)`
- **Stationarity**: `stat_p(i)` — must sum over `t` when referencing `lam_mp`

---

## Potential Fix Approaches

1. **Consistent index propagation**: When building stationarity equations, ensure
   that ALL references to `lam_mp` carry the full equation domain `(i,t)`, even
   when the derivative terms have been simplified
2. **Sum wrapping for extra dimensions**: When equation domain has dimensions not
   in the variable domain, wrap ALL multiplier terms in `sum(extra_dims, ...)`
3. **Dimension validation pass**: Add a post-generation check that all multiplier
   references match their declared dimension

---

## FIXED (Sprint 24)

**Fix:** Added `_fix_multiplier_dimensions` post-processing step in
`build_stationarity_equations`. After building each stationarity expression,
the function walks the additive term tree and checks all MultiplierRef nodes
for dimension mismatches. When a MultiplierRef has fewer indices than declared
(e.g., `lam_mp(i)` should be `lam_mp(i,t)`), the term is wrapped in a
`Sum` over the missing dimensions.

**Result:** prolog compiles and solves to MODEL STATUS 1 Optimal (was Error 148).
MCP obj=-73.528. All 4387 tests pass.

## Files Modified

- `src/kkt/stationarity.py` — `_fix_multiplier_dimensions`,
  `_fix_mult_dims_recursive`, `_find_bad_multiplier`, `_replace_mult_indices`

## Related Files

- `data/gamslib/raw/prolog.gms` — Source model (~160 lines)
- `docs/issues/ISSUE_1070_prolog-mcp-infeasible-ces-singular-jacobian.md` — Superseded issue
