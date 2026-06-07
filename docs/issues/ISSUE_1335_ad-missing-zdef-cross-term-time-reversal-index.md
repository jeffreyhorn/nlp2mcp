# AD: Missing `∂zdef/∂p` Cross-Term in `stat_p` When `zdef` References `p` via Time-Reversal-Indexed Offset

**GitHub Issue:** [#1335](https://github.com/jeffreyhorn/nlp2mcp/issues/1335)
**Status:** DEFERRED to Sprint 28 (Sprint 27 Day 0 confirmed #1393's Approach C does NOT subsume #1335 — this is now a DISTINCT fix needing a `card(t)-ord(t)` offset evaluator; see "Sprint 28 carryforward" below). The linked GitHub issue remains open.
**Severity:** Medium — Produces a valid local KKT point that differs from the NLP optimum; affects models that use `card`/`ord` arithmetic on sum index variables to construct time-reversal or end-of-horizon mappings.
**Date:** 2026-05-02
**Last Updated:** 2026-06-07 (Sprint 27 Day 8 — Sprint 28 carryforward filed; confirmed distinct from #1393 per Day 0 REPLAN).
**Affected Models:** otpop (confirmed); any model using `var(t + (card(t) - ord(t)))` or similar non-trivial offset arithmetic to map sum iterates to a fixed boundary element.
**Target Sprint:** ~~Sprint 27~~ → **Sprint 28** (Approach B — extend `_try_eval_offset` to resolve `card(t)-ord(t)` symbolically; independent of #1393).

---

## Sprint 28 carryforward — Sprint 27 Day 0/Day 8 (2026-06-07): distinct fix confirmed, deferred

Sprint 27 carried #1335 as a companion to #1393 under the hypothesis that #1393's Approach C *might* also fix #1335 (by letting `_sum_should_collapse` fire on the `zdef` sum body). **Day 0 disproved Approach C entirely for #1393** (it is inert — the `_is_concrete_instance_of` call path is never reached; see [ISSUE_1393](ISSUE_1393_ad-scalar-eq-sum-collapse-symbolic-superset.md) §"Sprint 28 carryforward" and `PRIORITY_3_RISK_ASSESSMENT.md` §5.6 binding verdict). Consequently:

- **#1335 is now a DISTINCT fix from #1393** — it was never subsumed, and the shared-fix hypothesis is dead. The `nu_zdef` cross-term in `stat_p(tt)` requires resolving the time-reversal offset `card(t)-ord(t)` independently.
- **Sprint 28 fix direction = Approach B** (per the "Corrected fix-surface diagnosis" below): extend `_try_eval_offset` to resolve symbolic-base `IndexOffset`s whose offset arithmetic is fully determined by the iteration set's cardinality (so AD's `_diff_sum` computes the `∂zdef/∂p('1990')` partial **without** Sum expansion — avoiding the |t|×-overcount + `x(t)→x(tt)` re-symbolization defects that sank the Day-9 Approach-A attempt).
- **Estimated effort:** 6–10h + a Phase 0 acceptance gate (hand-derive `stat_p('1990')` KKT against the prototype emit BEFORE committing budget), per the established methodology.

The detailed rolled-back-attempt diagnosis and the three competing approaches (A/B/C) remain valid below — Approach B is the recommended Sprint 28 path.

---

## Sprint 26 Day 9 Update — Fix Attempt Rolled Back

The Sprint 26 Day 9 PR #1394 attempted a narrow gate-relaxation fix at `src/ad/constraint_jacobian.py:986` + `:1107` (move `_resolve_index_offsets` + `_expand_sums_with_unresolved_offsets` outside the `if eq_domain:` predicate) plus an `iter_pos: int | None = None` parameter on `_substitute_single_index` that eagerly substitutes `Call('ord', SymbolRef(var_name))` → `Const(iter_pos + 1)` (to disambiguate the global-set `ord` lookup when an element appears at different positions in multiple sets).

The fix **DID** place `nu_zdef` into otpop's `stat_p` body — the primary bug shape described below resolved. **BUT** introduced a new math-correctness regression:

**Observed (broken) emit on `stat_p(tt)` post-fix:**

```gams
sum(t, ((-1) * (v * (0.365 * (xb(t) - x(tt)) + 0.365 * (xb(t) - x(tt)) + ... 17 copies ...))) * nu_zdef)$(sameas(tt, '1990'))
```

**Expected (hand-derived) cross-term:**

```gams
((-1) * v * sum(t, 0.365 * (xb(t) - x(t)))) * nu_zdef $ (sameas(tt, '1990'))
```

Two distinct defects in the broken emit:

1. **`x(tt)` instead of `x(t)` inside the sum.** The sum iterator is `t`, but downstream re-symbolization in `_add_indexed_jacobian_terms` (`src/kkt/stationarity.py:4432+`) rewrote `x(t)` → `x(tt)` because the eq-domain index `tt` of `stat_p(tt)` aliases the column header `p(tt)`. Breaks per-iteration coupling.
2. **17 duplicated copies of `0.365 * (xb(t) - x(tt))` inside the sum.** `_expand_sum_body` expanded the original `sum(t, body)` into 17 concrete-element terms; downstream re-symbolization collapsed the 17 concrete elements back to the SAME symbolic `t` and wrapped in a spurious outer `sum(t, ...)`, leaving 17 copies of the body inside. Overcounts by ~|t|.

**Root cause class:** AD-vs-emit pipeline assumption mismatch — same class as Sprint 26 #1381 (Pattern C Phase B), #1385 (Option 1 short-circuit), #1390 (kand tree-predicate Sum), and #1334 → #1393 (scalar-eq Sum-collapse w/ symbolic-superset wrt). The expansion-based approach in `_expand_sum_body` is correct for AD differentiation but the downstream symbolic re-emit doesn't preserve the expanded shape; this is an AD/emit pipeline architecture issue.

**Sprint 26 Day 9 PR #1394 action:** revert the `src/ad/constraint_jacobian.py` changes, delete the unit tests (`tests/integration/ad/test_issue_1335_scalar_eq_sum_expansion.py`), restore `data/gamslib/mcp/otpop_mcp.gms` to its pre-fix shape (no `nu_zdef` in `stat_p` — original bug returns, but mathematically consistent). Reopen #1335 with this corrected diagnosis; move this doc back from `docs/issues/completed/` to `docs/issues/` for Sprint 27 carryforward.

**Corrected fix-surface diagnosis (Sprint 27 carryforward):** the narrow gate-relaxation approach was incomplete. A correct #1335 fix must either:

- **(A)** Run `_expand_sums_with_unresolved_offsets` AND fix the downstream re-symbolization in `_add_indexed_jacobian_terms` to handle expanded-Sum shapes — preserves per-iteration var-binding when converting concrete element references back to symbolic for emit.
- **(B)** Resolve the IndexOffset `card(t) - ord(t)` symbolically (without expanding the Sum) so AD's `_diff_sum` can compute the partial without Sum expansion. Requires extending `_try_eval_offset` to handle symbolic-base IndexOffsets when the offset arithmetic is fully resolvable from the iteration set's cardinality alone.
- **(C)** A hybrid where the expansion happens but then collapses back to symbolic-Sum form post-AD with the correct shape.

**Estimated effort:** 6–10h (narrower than the architectural redesigns #1381/#1385/#1390/#1393 — this is a Sum-shape-preservation bug, not a Sum-collapse architecture change). Sprint 27 prep should add a Phase 0 acceptance gate per the established methodology (translate otpop with prototype + hand-derive `stat_p('1990')` KKT against emit BEFORE committing the implementation budget).

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
