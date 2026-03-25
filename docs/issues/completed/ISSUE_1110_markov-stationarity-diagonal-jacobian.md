# markov: Stationarity Uses Single Representative Derivative for Multi-Pattern Jacobian

**GitHub Issue:** [#1110](https://github.com/jeffreyhorn/nlp2mcp/issues/1110)
**Status:** FIXED (PR #1151)
**Model:** markov (GAMSlib SEQ=82)
**Error category:** `path_solve_terminated` → **solved** (obj=2571.794)
**NLP objective:** 2401.577

## Description

The markov model translates to MCP but PATH immediately exits with infeasibility (0 iterations, residual 1e20). The root cause is that `_add_indexed_jacobian_terms()` in `src/kkt/stationarity.py` picks a single representative Jacobian entry and generalizes its derivative expression to ALL constraint-variable pairings via a sum. This is incorrect when the derivative expression structurally differs across pairings — specifically when some pairings include a Kronecker-delta "+1" term and others do not.

## Root Cause

The original `constr` equation in markov is:

```gams
constr(sp,j).. sum(spp, z(sp,j,spp)) - b * sum((s,i,spp), pi(s,i,sp,j,spp) * z(s,i,spp)) =E= beta;
```

The Jacobian `d constr(sp',j') / d z(s,i,sp)` has two components:

1. **From `sum(spp, z(sp',j',spp))`:** Derivative is `1` **only when** `sp'=s AND j'=i` (i.e., `spp=sp` matches the variable's 3rd index). This is a Kronecker delta: `delta(sp'=s, j'=i)`.

2. **From `-b * sum((s'',i'',spp), pi(s'',i'',sp',j',spp) * z(s'',i'',spp))`:** Derivative is `-b * pi(s,i,sp',j',sp)` for **all** `(sp', j')` pairings.

So the correct full derivative is:

```
d constr(sp',j') / d z(s,i,sp) = delta(sp'=s, j'=i) - b * pi(s,i,sp',j',sp)
```

The AD system computes the derivative for each specific `(constr(sp0,j0), z(s0,i0,sp0_var))` pair individually:
- When `sp0=s0, j0=i0`: returns `1 - b*pi(s0,i0,sp0,j0,sp0_var)`
- When `sp0!=s0` or `j0!=i0`: returns `-b*pi(s0,i0,sp0,j0,sp0_var)`

But `_add_indexed_jacobian_terms()` picks a **single representative entry** (one where `sp0=s0, j0=i0`) and uses its derivative expression `(1 - b*pi(s,i,s__kkt1,j,sp))` for ALL `(s__kkt1, j)` in the sum. This incorrectly adds `+1` to every entry, not just the diagonal.

## Fix (PR #1151)

Implemented **Approach C** (sample multiple representative entries) combined with a correction-term strategy:

1. **`_derivative_structure_key(expr)`**: Computes a structural fingerprint of a derivative AST, normalizing concrete index values to arities. This groups Jacobian entries by derivative *shape* rather than concrete values.

2. **Multi-pattern detection**: After selecting a representative, sub-groups all entries in an offset group by their `_derivative_structure_key()`. If multiple patterns exist, the majority pattern (off-diagonal) drives the main sum and a correction term is computed for the minority pattern (diagonal).

3. **`_substitute_elements(expr, subs)`**: Recursively replaces concrete element names in AST nodes to align two derivative expressions at the same concrete point for comparison.

4. **`_subtract_and_cancel(a, b)`**: Collects additive terms with signs and cancels matching pairs. For markov: `(1 - b*pi) - (-(b*pi)) = 1`, yielding the Kronecker delta correction.

5. **Correction emission**: The correction term (e.g., `Const(1.0)`) is multiplied by `nu_constr(s,i)` and added after the main Jacobian sum.

### Result

```gams
stat_z(s,i,sp).. c(s,sp,i)
    + nu_constr(s,i)
    + sum((s__kkt1,j), ((-1) * (b * pi(s,i,s,i,s__kkt1))) * nu_constr(s__kkt1,j))
    + ...
```

The diagonal correction `nu_constr(s,i)` is correctly separated from the off-diagonal sum. GAMS solves successfully with obj=2571.794.

### Files Changed

- `src/kkt/stationarity.py` — Added `_derivative_structure_key()`, `_substitute_elements()`, `_subtract_and_cancel()` helpers; multi-pattern detection/correction logic in `_add_indexed_jacobian_terms()`
- `tests/unit/kkt/test_multi_pattern_jacobian.py` — 24 unit tests
- `tests/integration/kkt/test_markov_multi_pattern.py` — 1 integration test

## Impact

This bug affects any model where a constraint body contains BOTH:
- A direct VarRef to the decision variable with constraint-domain indices (e.g., `z(sp,j,spp)`)
- A sum over the same variable with independent iteration indices (e.g., `sum((s,i,spp), pi*z(s,i,spp))`)

This is the "self-referential transition" pattern common in Markov/dynamic programming models.

## Related Issues

- #1104 (markov): AD quoted-index fix + dimension-mismatch alias collision (FIXED)
- #914 (markov): Uninitialized pi parameter (FIXED)
