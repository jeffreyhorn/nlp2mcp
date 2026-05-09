# AD: Scalar-Constraint Stationarity Wraps Jacobian Terms in Spurious Sum When ParamRef Domain Is a Strict Subset of Equation Domain

**GitHub Issue:** [#1334](https://github.com/jeffreyhorn/nlp2mcp/issues/1334)
**Status:** CLOSED on GitHub (closed 2026-05-05; this in-repo doc was previously stale and is now updated to match GitHub state per Sprint 26 Prep Task 5 finding)
**Severity:** Medium — Produces a valid local KKT point that differs from the NLP optimum; affects nonconvex models with subset-domain parameters and scalar aggregation constraints
**Date:** 2026-05-02
**Last Updated:** 2026-05-08 (comprehensive fix-site correction + intra-file line resync per Sprint 26 Prep Task 7 PR #1371 review-comment fixes: (1) primary fix site corrected from `_add_jacobian_transpose_terms_scalar` [scalar stationarity only, line 5421] to `_add_indexed_jacobian_terms` [indexed stationarity, line 4228] for the otpop `stat_x(tt)` / `stat_p(tt)` case; (2) ParamRef branch ref updated from `:2413` to `:2448+`; (3) `_preserve_subset_var_indices` ref updated from `:2395–2400` to call-site `:2431` + def `:2739`; (4) `prefer_declared_domain=True` ref updated from `:2477` to `:2470, :2512`; (5) `:5293–5299` Sum-wrapping ref retired (was incorrectly attributed). Earlier 2026-05-07 update was the GitHub-state sync per Sprint 26 Prep Task 5 / Task 4 KNOWN_UNKNOWNS Unknown 2.1 evidence — otpop $141 cascade still observed in current main suggesting the fix may have been incomplete and warranting Sprint 26 Priority 5 investigation.)
**Affected Models:** otpop (confirmed); likely other models with scalar `sum`-aggregation constraints (e.g., `kdef`, `xtrack`, `ptrack`-style) over subset domains

---

## Problem Summary

In `_add_indexed_jacobian_terms` (`src/kkt/stationarity.py:4228+` — corrected 2026-05-08 per Sprint 26 Prep Task 7 PR #1371 review), the cross-term contribution from a scalar constraint (e.g., `kdef`) into an indexed stationarity equation (e.g., `stat_x(tt)`, `stat_p(tt)`) is wrapped in a `Sum(("t__",), ...)` whose body has mixed free indices that should have been unified.

*(Filing-time error: the original 2026-05-02 doc named `_add_jacobian_transpose_terms_scalar` (`:5279–5310`) as the fix site. That function is actually only called from `_build_stationarity_expr` (line 5365) for SCALAR stationarity equations — it does not produce the `stat_x(tt)` / `stat_p(tt)` indexed-stationarity emit. The actual indexed-stationarity Sum-wrapping site is `_add_indexed_jacobian_terms` (line 4228), specifically its scalar-constraint branch where it builds the Jacobian-transpose contribution from a SCALAR equation like `kdef` into an INDEXED stationarity. Sprint 26 Priority 5 fix work should target `_add_indexed_jacobian_terms` rather than `_add_jacobian_transpose_terms_scalar`.)*

The result is an over-counted coefficient by a factor of `|sum-domain|` (~22× for otpop's `t = 1974*1990`), producing nonzero residuals at the NLP solution and making valid local optima of the original NLP NOT be stationary points of the emitted MCP.

---

## Buggy Emit (otpop)

```
stat_x(tt).. (...
    + sum(t__, ((-1) * (del(t__) * 0.365 * (1 - c) * p(tt))) * nu_kdef)$(t(tt))
    + ...) =E= 0;
```

Note: `del(t__)` is summed across all of `t` while `p(tt)` uses the equation's symbolic index. The mathematically correct form has no sum:

```
+ (((-1) * (del(tt) * 0.365 * (1 - c) * p(tt))) * nu_kdef)$(t(tt))
```

`stat_p(tt)` has the same shape: `sum(t__, ((-1) * (del(t__) * x(tt) * 0.365 * (1-c))) * nu_kdef)$(t(tt))` should collapse to `(((-1) * (del(tt) * x(tt) * 0.365 * (1-c))) * nu_kdef)$(t(tt))`.

---

## Diagnostic

After the boundary `_fx_` fix in #1234, otpop reaches MODEL STATUS 1 (Optimal) at `pi=2307.07`. The original NLP finds `pi=4217.80`. Probing the MCP residual at the NLP solution (with `mcp_model.iterlim=0` after a manual NLP solve + dual transfer):

```
FINAL STATISTICS
Inf-Norm of Complementarity . .  7.5965e+02 eqn: (stat_x('1990'))
Inf-Norm of Minimum Map . . . .  2.3498e+02 eqn: (stat_p('1986'))
Inf-Norm of Grad Fischer Fcn. .  2.0135e+05 eqn: (kdef)
```

A hand-edit replacing `del(t__)` with `del(tt)` (and removing the `sum`) reduces stat_x('1990') residual ~60% (from 760 to ~358), confirming this is one of two contributing bugs. The remaining residual is from #1335 (missing time-reversal cross-term).

---

## Root Cause

`_replace_indices_in_expr` (`src/kkt/stationarity.py:2330+ (was :2295–2479 when filed 2026-05-02; resynced 2026-05-07)`) substitutes per-instance Jacobian-entry indices back to symbolic form using each symbol's declared domain:

| Reference | Substitution result | Why |
|-----------|--------------------|----|
| ParamRef `del('1974')` | `del(t)` | Uses parameter's declared domain `(t,)`; `prefer_declared_domain=True` at line 2470 (and 2512) — was claimed `:2477` 2026-05-02; resynced 2026-05-08 |
| VarRef `p('1974')` | `p(tt)` | Uses variable's declared domain `(tt,)`; Issue #666's `_preserve_subset_var_indices` — call-site at line 2431, function def at line 2739 (was claimed `:2395–2400` 2026-05-02; resynced 2026-05-08) — handles VarRef subset/superset |

The two symbols end up with DIFFERENT free indices (`t` vs `tt`) in the same expression. The `_collect_free_indices` step inside `_add_indexed_jacobian_terms` (line 4228+) finds `t` "uncontrolled" relative to `var_domain={tt}` and wraps in `Sum(("t",), term)`. *(Filing-time error: the original 2026-05-02 doc cited line range `:5293–5299` inside `_add_jacobian_transpose_terms_scalar` as the wrap site; that function only handles scalar stationarity. The actual wrap site for the otpop case lies inside `_add_indexed_jacobian_terms` — exact line range deferred to Sprint 26 fix work since the function body is large and the wrap call may have shifted.)*

The `$(t(tt))` guard already restricts the result to `tt ∈ t`, so the sum should collapse. The substitution machinery doesn't recognize this — there is no analog of `_preserve_subset_var_indices` for parameters that PROMOTES a strict-subset declared domain to the equation's superset domain.

---

## Where to Fix

Two candidate locations:

### Approach 1 — fix in `_replace_indices_in_expr`'s ParamRef branch

`src/kkt/stationarity.py:2448+` (the ParamRef match-case start; was `:2413–2479` when filed 2026-05-02; resynced 2026-05-08). When `param_domain` is a strict subset of `equation_domain` AND a parallel VarRef in the same expression has been substituted to use the eq domain variable, align the parameter substitution with the variable substitution (use the eq domain variable, not the parameter's declared domain).

This is the inverse of `_preserve_subset_var_indices`. Either:
- Add a sibling `_promote_subset_param_indices(...)` that returns the eq domain variable when the parameter's domain is a strict subset.
- Fold into the existing function with a flag controlling preserve-vs-promote.

The parameter-side analog should still respect `prefer_declared_domain` for cases where there's no overlapping VarRef context — only promote when the substitution would otherwise leave a free index that the eq-domain guard already restricts.

### Approach 2 — fix in `_add_indexed_jacobian_terms`'s wrap-in-Sum logic

`src/kkt/stationarity.py:4228+` (the `_add_indexed_jacobian_terms` definition; the specific wrap-in-Sum line was claimed at `:5293–5299` in 2026-05-02 but that range was incorrectly attributed to `_add_jacobian_transpose_terms_scalar` — the actual wrap call inside `_add_indexed_jacobian_terms` needs to be located during the Sprint 26 fix work). Before wrapping in `Sum`, check whether the unconstrained indices are exactly those that the eq-domain guard restricts. If so, substitute the eq domain variable into the expression (e.g., `t → tt` in remaining `del(t)` references) and skip the `Sum` wrap.

This is more targeted (only the assembly site) but might miss similar cases in other paths that share `_replace_indices_in_expr`.

**Recommendation:** start with Approach 1 (general) and fall back to Approach 2 if the substitution machinery proves too entangled to safely modify.

---

## Tests to Add

- **Unit test** in `tests/unit/kkt/`: minimal `ModelIR` with a scalar equation `kdef.. k = sum(t, p(t)*x(t))` over `t ⊂ tt`, with `x` and `p` declared on `tt`. Assert that `stat_x(tt)` body has no `sum(t__, ...)` and uses `p(tt)` directly.
- **Integration test** in `tests/integration/emit/test_otpop_*.py`: assert `stat_x(tt)` and `stat_p(tt)` have no `sum(t__, ` substring.
- **Pipeline check**: after fix (combined with #1335), otpop's NLP-warm-started MCP should converge to `pi ≈ 4217.80`.

---

## Files Involved

- `src/kkt/stationarity.py:2330+ (was :2295–2479 when filed 2026-05-02; resynced 2026-05-08)` — `_replace_indices_in_expr` (ParamRef branch at `:2448+`; was `:2413` when filed 2026-05-02)
- `src/kkt/stationarity.py:2431` (call-site) and `:2739` (function definition) — `_preserve_subset_var_indices` (VarRef analog, reference for the new ParamRef logic; was claimed `:2395–2400` 2026-05-02; resynced 2026-05-08)
- `src/kkt/stationarity.py:2470` and `:2512` — `prefer_declared_domain=True` invocation sites (was claimed `:2477` 2026-05-02; resynced 2026-05-08)
- `src/kkt/stationarity.py:4228+` — `_add_indexed_jacobian_terms` (PRIMARY fix site for the indexed-stationarity Sum-wrapping that affects otpop's `stat_x(tt)` / `stat_p(tt)`; was incorrectly attributed to `_add_jacobian_transpose_terms_scalar:5279–5310` in the 2026-05-02 filing — corrected 2026-05-08 per Sprint 26 Prep Task 7 PR #1371 review)
- `src/kkt/stationarity.py:5421+` — `_add_jacobian_transpose_terms_scalar` scalar branch (NOT applicable to the otpop case, which is indexed-stationarity; this function only handles SCALAR stationarity equations via `_build_stationarity_expr` at line 5365. Listed here only because it shares the same Sum-wrapping logic pattern and might benefit from a parallel fix if scalar stationarity exhibits the same bug shape on other models.)
- `data/gamslib/raw/otpop.gms` — primary integration test source

---

## Estimated Effort

**4–8h focused** for the AD fix, plus a corpus regression sweep across gamslib (the substitution machinery is shared by all models with subset-domain parameters; expect regressions to surface).

---

## Related

- #1234 (parent) — partial fixes shipped; this is one of the deferred AD-correctness items.
- #1335 — second AD bug (missing time-reversal cross-term). Both must be fixed to close the otpop objective gap.
- #666 — `_preserve_subset_var_indices` (the analogous fix for VarRef).
