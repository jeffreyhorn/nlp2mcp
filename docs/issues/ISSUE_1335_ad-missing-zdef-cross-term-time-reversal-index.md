# AD: Missing `∂zdef/∂p` Cross-Term in `stat_p` When `zdef` References `p` via Time-Reversal-Indexed Offset

**GitHub Issue:** [#1335](https://github.com/jeffreyhorn/nlp2mcp/issues/1335)
**Status:** OPEN
**Severity:** Medium — Produces a valid local KKT point that differs from the NLP optimum; affects models that use `card`/`ord` arithmetic on sum index variables to construct time-reversal or end-of-horizon mappings
**Date:** 2026-05-02
**Last Updated:** 2026-05-02
**Affected Models:** otpop (confirmed); any model using `var(t + (card(t) - ord(t)))` or similar non-trivial offset arithmetic to map sum iterates to a fixed boundary element

---

## Problem Summary

When an equation references a variable via an index whose offset is a non-trivial expression involving the sum index variable (e.g., `p(t + (card(t) - ord(t)))`), the AD does not produce a Jacobian entry for the time-reversed mapping target. The corresponding cross-term is then missing from the affected stationarity equation.

For otpop's `zdef`, the offset evaluates to the LAST element of the sum domain for every iterate (i.e., `1990` for all `t ∈ {1974,...,1990}`), so all references should map to `p('1990')`. The AD doesn't generate `(zdef, p('1990'))` in the constraint Jacobian, and `stat_p` is missing its `nu_zdef` cross-term entirely.

---

## Source Pattern (otpop)

```
zdef.. z =E= v * sum(t, 0.365 * (xb(t) - x(t)) * p(t + (card(t) - ord(t))));
```

For each `t' ∈ t`, the offset `t' + (card(t) - ord(t'))` evaluates to position `ord(t') + card(t) - ord(t') = card(t)`, i.e., the LAST element of `t`. For `t = 1974*1990`, that's `1990`. So `p(t + (card(t) - ord(t))) = p(1990)` for every `t`.

**Expected `∂zdef/∂p(p_idx)`:**
```
∂zdef/∂p(1990) = v * 0.365 * sum(t, xb(t) - x(t))
∂zdef/∂p(other) = 0
```

**Expected `stat_p(tt)` cross-term:**
```
+ ((v * 0.365 * sum(t, xb(t) - x(t))) * nu_zdef)$(sameas(tt, '1990'))
```

---

## Buggy Emit (otpop)

```
stat_p(tt).. sum(n, ((-1) * alpha(n)) * nu_pdef(tt)) +
             sum(n, (((-1) * alpha(n)) * nu_pdef(tt+1))$(ord(tt) <= card(tt) - 1)) +
             sum(n, (((-1) * alpha(n)) * nu_pdef(tt+2))$(ord(tt) <= card(tt) - 2)) +
             (((-1) * (db(tt) * p(tt) ** ((-1) * a) * ((-1) * a) / p(tt))) * nu_dem(tt))$(t(tt)) +
             (as(tt) * p(tt) ** b * b / p(tt) * nu_sup(tt))$(t(tt)) +
             sum(t__, ((-1) * (del(t__) * x(tt) * 0.365 * (1 - c))) * nu_kdef)$(t(tt)) -
             piL_p(tt) =E= 0;
```

There is no `nu_zdef` term anywhere. The AD didn't generate `(zdef, p('1990'))` in the constraint Jacobian.

---

## Diagnostic

After the boundary `_fx_` fix in #1234, otpop reaches MODEL STATUS 1 (Optimal) at `pi=2307.07`. The original NLP finds `pi=4217.80`. Probing the MCP residual at the NLP solution:

```
Inf-Norm of Minimum Map . . . .  2.3498e+02 eqn: (stat_p('1986'))
```

After hand-collapsing the `kdef` cross-term sum (#1334), the residual moves to `stat_p('1983')` / similar — confirming this is a separate, additive bug.

---

## Root Cause (suspected)

`_try_eval_offset` in `src/ad/constraint_jacobian.py:133–202` handles `card(<set>)` and `ord(<concrete-element>)` — but the latter only when the argument is already a concrete element via `pos_map` lookup (`:171–192`). For `t + (card(t) - ord(t))` inside `sum(t, ...)`, when the AD enumerates `t' ∈ t`, the substitution `t → t'` should make the offset reduce to a per-element constant.

**Hypothesis to verify:** during AD enumeration of the `zdef` sum body, the offset expression `card(t) - ord(t)` is evaluated BEFORE substituting `t → t'`. Without the substitution, `ord(t)` has no concrete element to look up and `_try_eval_offset` returns `None`. The Jacobian entry for `(zdef, p('1990'))` is then never recorded.

Investigation should start by inspecting `J_eq.get_derivative(zdef_row, p_1990_col)`:
- If `None`: AD never matched the time-reversed target → fix is in the per-instance enumeration path.
- If non-zero but the wrong shape: fix is in symbolic substitution.

---

## Where to Look

- `src/ad/constraint_jacobian.py:133–202` — `_try_eval_offset` (handles `ord`/`card`)
- `src/ad/constraint_jacobian.py:204–260` — `_resolve_idx` (per-instance offset resolution)
- `src/ad/derivative_rules.py:1847+` — `_diff_sum` (where the time-reversal substitution happens during sum body differentiation)

The likely fix is to substitute the loop variable (`t → t'`) into the offset expression BEFORE calling `_try_eval_offset`, OR to handle `ord(<sum-index-bound-to-element>)` directly in `_try_eval_offset` when the sum context is in scope.

---

## Tests to Add

- **Unit test** in `tests/unit/ad/test_constraint_jacobian.py`: a minimal `sum(t, x(t) * p(t + (card(t) - ord(t))))` IR fragment, assert `J_eq.get_derivative(eq_row, p_last_col)` is non-zero with the expected `sum(t, x(t))`-shaped body.
- **Integration test** in `tests/integration/emit/test_otpop_*.py`: assert `stat_p(tt)` body contains `nu_zdef` somewhere (under a `sameas(tt, '1990')` or equivalent guard).
- **Pipeline check**: after fix (combined with #1334), otpop's NLP-warm-started MCP should converge to `pi ≈ 4217.80`.

---

## Files Involved

- `src/ad/constraint_jacobian.py:133–260` — primary fix site
- `src/ad/derivative_rules.py:1847+` — `_diff_sum` (substitution context)
- `data/gamslib/raw/otpop.gms` — primary integration test source

---

## Estimated Effort

**4–8h focused** for the AD fix, plus corpus regression sweep (other models with similar non-trivial offset arithmetic on sum index variables may exist; the fix touches AD-core enumeration logic).

---

## Related

- #1234 (parent) — partial fixes shipped; this is the original "time-reversal AD" hypothesis (it was real, just not the abort cause).
- #1334 — sum-collapse bug; combined with this fix should close the otpop objective gap to `pi ≈ 4217.80`.
