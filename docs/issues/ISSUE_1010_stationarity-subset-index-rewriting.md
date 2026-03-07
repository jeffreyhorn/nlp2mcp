# Stationarity gradient: rewrite subset indices to controlled domain with membership guard

**GitHub Issue:** [#1010](https://github.com/jeffreyhorn/nlp2mcp/issues/1010)
**Model:** robert (GAMSlib) and similar subset-index patterns
**Component:** `src/kkt/stationarity.py` — `_build_indexed_stationarity_expr()`
**Related PR:** #1006 (Copilot review comments on lines 920 and 105)

## Description

When a variable is declared over a superset (e.g., `x(p,tt)`) but the objective references it via a subset index (e.g., `x(p,t)` where `t(tt)`), the gradient term contains the subset index `t` which is uncontrolled in the stationarity equation `stat_x(p,tt)`.

The current fix (PR #1006 / Issue #949) wraps the gradient in `Sum(t, ...)`, producing:

```gams
stat_x(p,tt)$(t(tt)).. sum(t, (-1) * c(p,t)) + ... =E= 0;
```

This makes the gradient term **constant across all `tt`** — `sum(t, c(p,t))` evaluates to the same value regardless of which `tt` element the stationarity equation is instantiated for. The `$(t(tt))` condition disables the equation for `tt` elements not in `t`, so the result is mathematically correct for models like robert (which solves OPTIMAL).

However, the semantically correct approach would be to **rewrite** the subset index `t` to the controlled domain index `tt` with a membership guard:

```gams
stat_x(p,tt)$(t(tt)).. (-1) * c(p,tt) + ... =E= 0;
```

Here `c(p,tt)` directly uses the controlled index, and `$(t(tt))` ensures the equation only exists for `tt ∈ t`. This preserves the per-element gradient structure and correctly handles cases where the gradient varies across elements.

## Why the current approach works (but is fragile)

For models like robert, the objective is:

```gams
pd.. profit =e= sum(t, sum(p, c(p,t)*x(p,t)) - ...);
```

The derivative ∂(profit)/∂x(p,tt₀) for a specific `tt₀ ∈ t` is `c(p,tt₀)`. The current `sum(t, c(p,t))` produces `Σ_t c(p,t)` which is wrong in general — it sums over ALL `t` elements instead of selecting the single matching one. It only works when:

1. The `$(t(tt))` condition suppresses the equation for `tt ∉ t`, AND
2. The solver treats the over-counted gradient as equivalent (which happens when the gradient is used linearly in the KKT system and the complementarity structure resolves correctly)

This is fragile because a model where the gradient genuinely differs per `tt` element (not just a parameter lookup) could produce incorrect KKT conditions.

## Reproduction

```bash
# Translate robert and inspect the stationarity equation:
.venv/bin/python -m src.cli data/gamslib/raw/robert.gms -o /tmp/robert_mcp.gms
grep 'stat_x' /tmp/robert_mcp.gms
```

Current output shows `sum(t, ...)` wrapping the gradient term:
```gams
stat_x(p,tt)$(t(tt)).. sum(t, (-1) * c(p,t)) + ... =E= 0;
```

Expected output after fix:
```gams
stat_x(p,tt)$(t(tt)).. (-1) * c(p,tt) + ... =E= 0;
```

## Root Cause

In `_build_indexed_stationarity_expr()` (stationarity.py ~line 907-919), the gradient term is built using the indices from the original equation expressions. When the objective references `x(p,t)` (subset), the gradient contains `ParamRef("c", ("p", "t"))`. The code detects `t` as uncontrolled (not in the variable domain `(p, tt)`) and wraps in `Sum(("t",), ...)`.

The correct fix is to **rewrite** subset indices to their superset equivalents:
- Detect that `t` is a subset of `tt` (via `model_ir.sets["t"].domain == ("tt",)`)
- Replace `t` with `tt` in the gradient expression
- Add/verify a `$(t(tt))` membership guard on the stationarity equation

## Fix Approach

1. **In `_build_indexed_stationarity_expr()`**, after collecting uncontrolled indices:
   - For each uncontrolled index, check if it's a subset of any domain index
   - If yes: rewrite the index in the expression (`t` → `tt`) rather than wrapping in Sum
   - If no subset-superset relationship exists: fall back to the current Sum wrapping

2. **Index rewriting utility**: Create a helper that walks an expression tree and substitutes index names in `VarRef`/`ParamRef`/`MultiplierRef` indices.

3. **Membership guard**: Ensure the stationarity equation has a `$(t(tt))` condition to restrict to valid subset elements. (This may already be present from the equation condition propagation.)

4. **Update test**: Modify `test_subset_index_in_gradient_wrapped_in_sum` to assert index rewriting instead of Sum wrapping.

## Related Issues

- #949 — Original uncontrolled set index issue (GAMS Error $149)
- PR #1006 — Current Sum-wrapping fix with Copilot review identifying this improvement
