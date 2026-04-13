# rocket: Jacobian Explosion — Lag-Indexed Equations Produce Dense Derivatives for Auxiliary Variables

**GitHub Issue:** [#1134](https://github.com/jeffreyhorn/nlp2mcp/issues/1134)
**Status:** FIXED (Sprint 24)
**Severity:** High — PATH reports MODEL STATUS 5 (Locally Infeasible) due to wrong Jacobian structure
**Date:** 2026-03-22
**Affected Models:** rocket (and potentially any model with lag-indexed equations + auxiliary variables)

---

## Problem Summary

The rocket model (`data/gamslib/raw/rocket.gms`) translates to MCP and PATH runs, but
reports MODEL STATUS 5 (Locally Infeasible). The stationarity equations `stat_g(h)` and
`stat_d(h)` contain 52 Jacobian terms from `v_eqn` instead of the correct 2-3.

The constraint Jacobian treats `∂v_eqn(h')/∂g(h)` as non-zero for ALL `h'`, instead of
only the instances where `v_eqn` actually references `g(h)`. This produces dense
stationarity equations that are mathematically incorrect and infeasible.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/rocket.gms -o /tmp/rocket_mcp.gms

# Count nu_v_eqn terms in stat_g — should be 2-3, actually 52
grep "stat_g(h)\.\." /tmp/rocket_mcp.gms | tr '+' '\n' | grep -c "nu_v_eqn"
# Output: 52

gams /tmp/rocket_mcp.gms lo=2
# MODEL STATUS 5 Locally Infeasible
```

---

## GAMS Output

```
**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      5 Locally Infeasible

Inf-Norm of Normal Map. . . . .  6.2385e-01 eqn: (stat_ht(h27))

REPORT SUMMARY: 509 INFEASIBLE
```

---

## Root Cause

### The Original Model Equations

```gams
gf(h)..      g(h)  =e= g_0*sqr(h_0/ht(h));
df(h)..      d(h)  =e= D_c*sqr(v(h))*exp(-h_c*(ht(h) - h_0)/h_0);
v_eqn(h-1).. v(h)  =e= v(h-1) + .5*step*((T(h) - D(h) - m(h)*g(h))/m(h)
                              + (T(h-1) - D(h-1) - m(h-1)*g(h-1))/m(h-1));
```

The `v_eqn(h-1)` equation references `g(h)` and `g(h-1)` — only 2 specific instances
of `g`. The Jacobian `∂v_eqn/∂g` should be:

```
∂v_eqn(h')/∂g(h) = -0.5*step  when h' = h   (via m(h)*g(h)/m(h) term)
                   = -0.5*step  when h' = h+1 (via m(h)*g(h)/m(h) lag term)
                   = 0          otherwise
```

### The Bug: Dense Jacobian

The stationarity equation `stat_g(h)` should be:

```gams
* CORRECT (sparse):
stat_g(h).. nu_gf(h) + (-0.5*step) * nu_v_eqn(h)
          + (-0.5*step) * nu_v_eqn(h+1)$(ord(h) <= card(h)-1)
          - piL_g(h) =E= 0;
```

Instead, the MCP emits:

```gams
* WRONG (dense — 52 terms):
stat_g(h).. nu_gf(h)
  + ((-1) * (0.5 * step * m(h) * ...)) * nu_v_eqn(h)
  + ... * nu_v_eqn(h-1)$(ord(h) > 1)
  + ... * nu_v_eqn(h-2)$(ord(h) > 2)
  + ... * nu_v_eqn(h-3)$(ord(h) > 3)
  ...
  + ... * nu_v_eqn(h-50)$(ord(h) > 50)
  - piL_g(h) =E= 0;
```

Each `v_eqn(h')` instance contributes a Jacobian term for `g(h)`, even though
`v_eqn(h')` only depends on `g(h')` and `g(h'-1)`, not `g(h)`.

### The Same Bug Affects stat_d

`stat_d(h)` also has 52 `nu_v_eqn` terms (should have 2-3).

### Location in AD Code

The constraint Jacobian is computed in `src/ad/constraint_jacobian.py`. The bug likely
occurs when computing `∂v_eqn(h')/∂g(h)`:

1. The AD engine differentiates the `v_eqn` body w.r.t. `g(h)` symbolically
2. Since `g` appears in `v_eqn` with lag indices (`g(h)` and `g(h-1)`), the derivative
   should only be non-zero when the lag instance matches
3. But the engine treats `g(h)` as matching ANY instance, producing a non-zero
   derivative for all lag offsets

This is likely the same class of bug as #1131 (missing sameas guard on concrete-element
references), but in the constraint Jacobian rather than the objective gradient. When
`v_eqn(h-1)` references `g(h)`, the derivative w.r.t. `g(h')` should include a
`sameas(h, h')` or equivalent lag-domain guard.

---

## Suggested Fix

### Approach 1: Lag-aware Jacobian computation

In the constraint Jacobian computation (`src/ad/constraint_jacobian.py`), when the
equation has lag-indexed variables (e.g., `g(h)` and `g(h-1)` in `v_eqn(h-1)`), the
derivative w.r.t. `g(h)` should only produce non-zero entries for the lag offsets
that actually reference `g`:

- `∂v_eqn(h')/∂g(h)` is non-zero only when `h = h'` or `h = h'-1`
- The stationarity should use only `nu_v_eqn(h)` and `nu_v_eqn(h+1)` terms

### Approach 2: Instance-level Jacobian sparsity

Compute the Jacobian at the instance level (for each concrete `h'`) rather than
symbolically, then reconstruct the indexed stationarity equation from the sparse
non-zero entries with appropriate lag/lead offsets.

---

## Verification Plan

```bash
python -m src.cli data/gamslib/raw/rocket.gms -o /tmp/rocket_mcp.gms

# Verify sparse stat_g (should have 2-3 nu_v_eqn terms, not 52)
grep "stat_g(h)\.\." /tmp/rocket_mcp.gms | tr '+' '\n' | grep -c "nu_v_eqn"
# Expected: 2 or 3

gams /tmp/rocket_mcp.gms lo=2
# Expected: MODEL STATUS 1 or 2
```

---

## Resolution (Sprint 24, PR #1257)

**Root cause:** The concrete Jacobian correctly computes only 2 non-zero
entries per row for `v_eqn/g` (offsets 0 and +1), but the boundary row
`v_eqn(h0)` has dense derivatives against all `g(h)` instances due to
how the AD engine handles the degenerate boundary case.  Each of these
51 dense entries creates a singleton offset group (offset −1 through −50),
all originating from the same row (h0).

**Fix:** Added `_filter_boundary_singleton_offset_groups()` in
`src/kkt/stationarity.py`.  When multiple singleton-coverage offset groups
all originate from the same equation row, they are identified as boundary
artifacts and removed.  Legitimate lead/lag offsets from distinct rows are
preserved.

**Result:** `stat_g/d/m/t/v(h)` reduced from 52 to 2 `nu_v_eqn` terms.
With `--nlp-presolve`: STATUS 2, obj=1.0128 (exact NLP match).

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/ad/constraint_jacobian.py` | Jacobian computation — lag-domain handling |
| `src/kkt/stationarity.py` | `_add_indexed_jacobian_terms()` — assembles J^T*nu terms; `_filter_boundary_singleton_offset_groups()` — the fix |
| `src/ad/derivative_rules.py` | `_diff_varref()` — index matching for derivatives |
