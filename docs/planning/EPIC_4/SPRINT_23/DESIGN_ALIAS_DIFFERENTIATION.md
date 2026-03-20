# Design: Alias-Aware Differentiation with Summation-Context Tracking

**Created:** 2026-03-19
**Issue:** #1111
**Sprint 22 Carryforward:** KU-27
**Sprint 23 Priority:** 3 (Match Rate Improvement)
**Estimated Effort:** 4-6 hours

---

## Executive Summary

The AD engine's `_diff_varref()` does not recognize aliases when differentiating. When computing `d/d(x(n,k))` of `x(np,k)` where `Alias(n, np)`, the derivative returns 0 because exact index-tuple matching fails: `('np','k') != ('n','k')`. This produces incomplete gradients for 21 mismatch models that use aliases in differentiated expressions.

A naive fix (matching aliases unconditionally) was attempted in Sprint 22 and **reverted** because it breaks models where aliases are independent sum iteration variables (regression in dispatch model). The correct fix requires **summation-context tracking**: the AD engine must carry a set of "active iteration indices" (bound by enclosing sums) and only produce alias-based `sameas()` guards when the alias index is NOT in the active iteration set.

**Key finding:** Alias models are massively over-represented in mismatches. Of 33 alias-using solving models, 76% mismatch vs. 30% for non-alias models. All 21 alias mismatch models use aliases within `sum()` expressions. This fix is the highest-leverage match rate improvement available.

---

## 1. Root Cause Analysis

### 1.1 The Bug

**File:** `src/ad/derivative_rules.py:232-309` (`_diff_varref`)

When differentiating `x(np, k)` with respect to `x(n, k)`, the current `_indices_match()` function performs exact string comparison. Since `"np" != "n"`, the derivative returns `Const(0.0)` even though `np` is an alias of `n` (both refer to the same underlying set).

**Concrete example (qabel):**

```gams
Alias(n, np);
Variable x(n,k);
obj.. z =e= sum((k,n,np), (x(n,k)-xtilde(n,k))*w(n,np,k)*(x(np,k)-xtilde(np,k)));
```

When computing `d(obj)/d(x(n,k))`, the AD engine must recognize that `x(np,k)` also depends on `x(n,k)` through the alias relationship. The correct derivative includes a cross-term with a `sameas(np,n)` guard:

```
d/d(x(n,k)) of x(np,k) = sameas(np,n) * 1    (not 0)
```

### 1.2 Why Naive Alias Matching Fails

Sprint 22 attempted a straightforward fix: whenever `_diff_varref` encounters an index from an aliased set, treat it as potentially matching. This was reverted because it produces spurious derivatives in summation contexts:

```gams
Alias(i, j);
sum((i,j), p(i) * b(i,j) * p(j))
```

Here, `i` and `j` are **independent iteration variables** bound by the sum. When computing `d/d(p(i))` of `p(j)`, the answer must be 0 because `j` iterates independently over the same set. The naive fix incorrectly produces `sameas(j,i)` because it doesn't know that `j` is a bound sum variable.

### 1.3 The Correct Fix: Summation-Context Tracking

The key insight is that alias indices should only be matched when they are **free** (not bound by an enclosing sum). The AD engine needs to track which indices are currently bound as sum iteration variables:

- **Free alias index:** `np` appears in an expression but is NOT a sum iteration variable in any enclosing sum. In this case, `np` and `n` refer to the same physical element, and `d/d(x(n,k)) of x(np,k) = sameas(np,n)`.
- **Bound alias index:** `j` is a sum iteration variable in `sum((i,j), ...)`. In this case, `j` iterates independently of `i`, even though both alias the same set. `d/d(p(i)) of p(j) = 0`.

---

## 2. Affected Models

### 2.1 Corpus-Wide Alias Statistics

| Category | Count | Alias-Using | % Alias |
|----------|-------|-------------|---------|
| Total GAMSlib models | 219 | 108 | 49.3% |
| Solving models | 89 | 33 | 37.1% |
| Matching models | 47 | 8 | 17.0% |
| Mismatch models | 36 | 21 | 58.3% |
| Skipped (multi-solve) | 6 | 4 | 66.7% |

**Key insight:** Alias models are over-represented in mismatches (58.3%) relative to their share of solving models (37.1%). Alias-using solving models have a 76% mismatch rate vs. 30% for non-alias models.

### 2.2 Mismatch Models Using Aliases (21 models)

All 21 use aliases within `sum()` expressions (the exact pattern this fix targets):

| Model | NLP Obj | MCP Obj | Rel Diff | Notes |
|-------|---------|---------|----------|-------|
| abel | 225.19 | 158.15 | 29.8% | |
| camshape | 4.28 | 6.28 | 31.8% | |
| catmix | -0.048 | -0.046 | 4.4% | |
| cclinpts | -3.00 | -9.98 | 69.9% | |
| himmel16 | 0.675 | 0.385 | 43.0% | |
| irscge | 26.09 | 25.51 | 2.2% | CGE model |
| kand | 2613 | 195 | 92.5% | |
| launch | 2257.8 | 2731.7 | 17.4% | |
| lrgcge | 25.77 | 25.51 | 1.0% | CGE model |
| meanvar | 0.031 | 0.027 | 12.3% | |
| moncge | 25.98 | 25.51 | 1.8% | CGE model |
| polygon | 0.780 | 0.0 | 100% | |
| ps10_s | 0.533 | 0.387 | 27.4% | |
| ps2_f_s | 0.865 | 0.861 | 0.5% | |
| ps2_s | 0.865 | 0.861 | 0.5% | |
| ps3_s | 1.162 | 1.056 | 9.1% | |
| ps3_s_gic | 1.162 | 1.056 | 9.1% | |
| ps3_s_mn | 1.052 | 1.029 | 2.2% | |
| ps3_s_scp | -0.607 | -0.617 | 1.6% | |
| qabel | 46965 | 51133 | 8.2% | Primary test model |
| stdcge | 26.09 | 25.51 | 2.2% | CGE model |

### 2.3 Currently Matching Alias Models (8 models, regression risk)

These models already match and must NOT regress:

dispatch, gussrisk, nemhaus, ps2_f, ps3_f, quocge, ship, splcge

**dispatch** is the critical regression test — it was the model that broke with the Sprint 22 naive fix.

### 2.4 Non-Alias Mismatch Models (15 models, unaffected by this fix)

chakra, circle, imsl, like, mathopt1, mathopt4, mexss, mingamma, prodsp2, qdemo7, robert, tforss, trig, trnspwl, weapons

These models mismatch for reasons unrelated to aliasing (dollar conditions, non-convexity, other KKT bugs).

---

## 3. AD Pipeline Trace

### 3.1 Current Call Flow

```
stationarity.py
  → gradient.py (compute_objective_gradient / compute_gradient_for_expression)
  → constraint_jacobian.py (compute_constraint_jacobian)
    → derivative_rules.py (differentiate_expr)
      → _diff_varref()         ← ALIAS BUG HERE
      → _diff_sum()            ← NEEDS TO TRACK BOUND INDICES
      → _diff_prod()           ← NEEDS TO TRACK BOUND INDICES
      → _diff_dollar_conditional()
      → _diff_binary()
      → _diff_call()
```

### 3.2 Key Functions

1. **`differentiate_expr(expr, wrt_var, wrt_indices, config)`** — Main dispatcher. Currently has 4 parameters. The `config` parameter carries `model_ir` (which has `aliases` dict).

2. **`_diff_varref(expr, wrt_var, wrt_indices, config)`** — Lines 232-309. Uses `_indices_match()` for exact string comparison. **No alias awareness.**

3. **`_diff_sum(expr, wrt_var, wrt_indices, config)`** — Lines 1592-1762. Handles sum collapse and partial index matching. **Does not track bound indices for alias purposes.** The sum's `index_sets` (e.g., `("i", "j")`) are the bound variables.

4. **`_diff_prod(expr, wrt_var, wrt_indices, config)`** — Similar to sum, uses product rule with iteration.

5. **`Config.model_ir`** — `src/config.py:40`. The `Config` dataclass carries `model_ir: Any` which provides access to `model_ir.aliases` (`CaseInsensitiveDict[AliasDef]` — values have a `.target` attribute giving the parent set name). See `src/ir/model_ir.py:37` for the definition.

### 3.3 Alias Information in IR

```python
# src/ir/model_ir.py (ModelIR dataclass, line 37)
aliases: CaseInsensitiveDict[AliasDef] = field(default_factory=CaseInsensitiveDict)

# src/ir/symbols.py (AliasDef dataclass, line 58)
@dataclass
class AliasDef:
    name: str        # e.g., "np"
    target: str      # e.g., "n" — the parent set name
    universe: str | None = None
```

`model_ir.aliases` is conceptually a `CaseInsensitiveDict[AliasDef]` — keys are alias names (case-insensitive), values are `AliasDef` objects with a `.target` attribute giving the parent set. For example, `model_ir.aliases["np"].target == "n"`. **However, some tests/population paths currently assign plain strings as alias values** (e.g., `model.aliases["j"] = "i"` in `tests/integration/kkt/test_stationarity.py:874`), so the effective type is `CaseInsensitiveDict[AliasDef | str]`. Code that consumes `aliases` must therefore be robust to both shapes and resolve the target via `getattr(value, "target", value)` rather than assuming an `AliasDef`.

To check if two indices reference the same set in a way that works with both `AliasDef` and `str` alias values:

```python
def same_root_set(a: str, b: str, aliases) -> bool:
    val_a = aliases[a] if a in aliases else a
    val_b = aliases[b] if b in aliases else b
    root_a = getattr(val_a, "target", val_a)
    root_b = getattr(val_b, "target", val_b)
    return str(root_a).lower() == str(root_b).lower()
```

For multi-level alias chains (e.g., `Alias(n,np); Alias(np,npp)`), resolution must follow `.target` (or the string value) iteratively until a fixed point is reached.

---

## 4. Proposed Fix Design

### 4.1 Add `bound_indices` Parameter

Add an optional `frozenset[str]` parameter to `differentiate_expr` and all `_diff_*` functions that tracks currently-bound sum/prod iteration variables.

**Signature change:**

```python
def differentiate_expr(
    expr: Expr,
    wrt_var: str,
    wrt_indices: tuple[str | IndexOffset, ...] | None = None,
    config: Config | None = None,
    *,
    bound_indices: frozenset[str] = frozenset(),  # NEW
) -> Expr:
```

Using a keyword-only argument with a default value ensures full backward compatibility — no existing call sites need to change unless they are Sum/Prod handlers.

### 4.2 Thread `bound_indices` Through Sum/Prod

In `_diff_sum()`, before recursing into the body, add the sum's index_sets to `bound_indices`:

```python
def _diff_sum(expr, wrt_var, wrt_indices, config, *, bound_indices=frozenset()):
    new_bound = bound_indices | frozenset(expr.index_sets)
    # All recursive differentiate_expr calls pass bound_indices=new_bound
    body_derivative = differentiate_expr(
        expr.body, wrt_var, wrt_indices, config, bound_indices=new_bound
    )
```

Same pattern for `_diff_prod()`.

### 4.3 Alias-Aware Matching in `_diff_varref()`

Modify `_diff_varref()` to check for alias matches when exact matching fails:

```python
def _diff_varref(expr, wrt_var, wrt_indices, config, *, bound_indices=frozenset()):
    if expr.name != wrt_var:
        return Const(0.0)

    if wrt_indices is None:
        return Const(1.0) if expr.indices == () else Const(0.0)

    # Exact match (existing behavior)
    if _indices_match(expr.indices, wrt_indices):
        return Const(1.0)

    # NEW: Alias-aware matching
    if config and config.model_ir and config.model_ir.aliases:
        aliases = config.model_ir.aliases
        guard = _alias_match(expr.indices, wrt_indices, aliases, bound_indices)
        if guard is not None:
            return guard  # Returns a sameas() expression or Const(1.0)

    return Const(0.0)
```

**Return type change:** The current `_diff_varref` has return type annotation `-> Const`. With this change, it may return a `Call("sameas", ...)` expression (a general `Expr`) via `_alias_match()`. The return type annotation must be updated from `-> Const` to `-> Expr`, and any downstream code that assumes a `Const` return (e.g., `isinstance` checks, `.value` access) must be reviewed.

### 4.4 `_alias_match()` Helper

```python
def _alias_match(
    expr_indices: tuple[str | IndexOffset, ...],
    wrt_indices: tuple[str | IndexOffset, ...],
    aliases: CaseInsensitiveDict[AliasDef],
    bound_indices: frozenset[str],
) -> Expr | None:
    """Check if indices match through alias resolution.

    Returns:
        - None if no alias match possible
        - Const(1.0) if indices match after alias resolution (all alias dims are already matched)
        - A sameas() guard expression if alias dimensions need runtime matching
    """
    if len(expr_indices) != len(wrt_indices):
        return None

    guards = []
    for expr_idx, wrt_idx in zip(expr_indices, wrt_indices):
        # Extract base strings for comparison
        expr_str = expr_idx if isinstance(expr_idx, str) else expr_idx.base
        wrt_str = wrt_idx if isinstance(wrt_idx, str) else wrt_idx.base

        # Exact match (with quote normalization)
        if _strip_quotes(expr_str).lower() == _strip_quotes(wrt_str).lower():
            continue

        # Check if both reference the same root set
        if not _same_root_set(expr_str, wrt_str, aliases):
            return None  # Different sets, no alias relationship

        # Same root set, but different names — alias relationship
        # Check if the expr index is a bound iteration variable
        if expr_str.lower() in {b.lower() for b in bound_indices}:
            return None  # Bound variable: independent iteration, no match

        # Free alias variable: generate sameas() guard
        guards.append(
            Call("sameas", (SymbolRef(expr_str), SymbolRef(wrt_str)))
        )

    if not guards:
        return Const(1.0)  # All dimensions matched exactly or via alias

    # Combine guards with multiplication (AND semantics)
    result: Expr = guards[0]
    for g in guards[1:]:
        result = Binary("*", result, g)
    return result
```

### 4.5 `_same_root_set()` Helper

```python
def _same_root_set(a: str, b: str, aliases) -> bool:
    """Check if two index names reference the same root set.

    Handles both AliasDef objects (with .target) and plain strings
    (used in some tests).
    """
    def resolve(name: str) -> str:
        seen = set()
        while name in aliases:
            if name.lower() in seen:
                break
            seen.add(name.lower())
            val = aliases[name]
            name = getattr(val, "target", val)
        return name.lower()

    return resolve(a) == resolve(b)
```

### 4.6 Code Locations Changed

| File | Function | Change |
|------|----------|--------|
| `src/ad/derivative_rules.py:68-169` | `differentiate_expr()` | Add `bound_indices` kwarg, pass through to all `_diff_*` |
| `src/ad/derivative_rules.py:232-309` | `_diff_varref()` | Add `bound_indices` kwarg, call `_alias_match()` |
| `src/ad/derivative_rules.py:1592-1762` | `_diff_sum()` | Add `bound_indices` kwarg, augment with `expr.index_sets` before recursing |
| `src/ad/derivative_rules.py` (new) | `_alias_match()` | New helper: alias-aware index matching with bound check |
| `src/ad/derivative_rules.py` (new) | `_same_root_set()` | New helper: resolve alias chains to root set |
| `src/ad/derivative_rules.py` | `_diff_prod()` | Add `bound_indices` kwarg, augment before recursing |
| `src/ad/derivative_rules.py` | `_diff_binary()` | Add `bound_indices` kwarg, pass through |
| `src/ad/derivative_rules.py` | `_diff_unary()` | Add `bound_indices` kwarg, pass through |
| `src/ad/derivative_rules.py` | `_diff_call()` | Add `bound_indices` kwarg, pass through |
| `src/ad/derivative_rules.py` | `_diff_dollar_conditional()` | Add `bound_indices` kwarg, pass through |

**Important:** The `bound_indices` parameter is keyword-only with a default, so NO external callers need to change. The gradient/Jacobian/stationarity code calls `differentiate_expr()` without `bound_indices`, which defaults to `frozenset()`. All threading is internal.

---

## 5. Regression Risk Assessment

### 5.1 Risk Level: MEDIUM

The fix is architecturally clean (additive parameter with default value), but the interaction between alias matching and sum collapse is subtle.

### 5.2 Currently Matching Alias Models (Must Not Regress)

8 alias-using models currently match. All must continue matching after the fix:

| Model | Has Aliases in Sums | Regression Risk |
|-------|---------------------|-----------------|
| dispatch | Yes (Alias(i,j) in sum) | **HIGH** — Sprint 22 regression model |
| gussrisk | Yes | Low |
| nemhaus | Yes | Low |
| ps2_f | Yes | Low |
| ps3_f | Yes | Low |
| quocge | Yes | Low |
| ship | Yes | Low |
| splcge | Yes | Low |

**dispatch** is the critical regression canary. Its alias pattern (`Alias(i,j); sum((i,j), p(i)*b(i,j)*p(j))`) exercises the exact "bound alias as independent iteration variable" case that the naive fix got wrong. The `bound_indices` mechanism specifically handles this: `j` will be in `bound_indices` when differentiating w.r.t. `p(i)`, so `p(j)` will NOT be matched.

### 5.3 Non-Alias Models (56 solving models)

Zero risk. The "56 non-alias solving models" are models that do not declare any `Alias` statements. For these models, `model_ir.aliases` is empty, so the alias code path is never entered.

**Taxonomy note:** The 33 "alias-using" solving models all declare at least one `Alias` statement, meaning their `model_ir.aliases` dict is non-empty. Of these 33, 8 currently match (including dispatch) and 21 mismatch. The remaining 4 are skipped (multi-solve). The key distinction is:
- **No alias declarations** (56 models): `model_ir.aliases` is empty → alias code path unreachable
- **Has alias declarations** (33 models): `model_ir.aliases` is non-empty → alias code path may be entered when exact `_indices_match()` fails

### 5.4 Regression Safeguards

1. **Unit tests:** Test both the "should match" case (qabel pattern) and "should NOT match" case (dispatch pattern)
2. **Integration tests:** Run dispatch and qabel through full pipeline
3. **Full pipeline regression:** Run all 89 solving models, verify no matches are lost
4. **Targeted tests:** The 8 currently-matching alias models must still match

---

## 6. Test Plan

### 6.1 Primary Test Models

| Model | Role | Expected Change |
|-------|------|-----------------|
| **qabel** | Verify fix works | Mismatch → match (or reduced difference) |
| **dispatch** | Verify no regression | Match → match (unchanged) |
| **ps2_f** | Cross-check alias matching | Match → match (unchanged) |

### 6.2 Unit Tests

```python
# tests/unit/ad/test_alias_differentiation.py

def test_alias_varref_free_index():
    """d/d(x(n,k)) of x(np,k) where Alias(n,np) → sameas(np,n)"""
    # np is NOT in bound_indices → should produce sameas guard

def test_alias_varref_bound_index():
    """d/d(p(i)) of p(j) where Alias(i,j), j is sum-bound → 0"""
    # j IS in bound_indices → should return 0

def test_alias_sum_collapse():
    """sum(np, x(np,k)) w.r.t. x(n,k) should collapse with alias awareness"""

def test_no_alias_unchanged():
    """Models without aliases should produce identical derivatives"""

def test_nested_sum_alias():
    """sum(k, sum(np, f(n,np,k))) w.r.t. x(n,k) — np bound, n free"""

def test_same_root_set_resolution():
    """Alias chain: Alias(n,np); Alias(np,npp) → all resolve to n"""
```

### 6.3 Integration Tests

1. qabel: Generate MCP, check that gradient includes cross-term derivatives
2. dispatch: Generate MCP, verify no `sameas` guards on sum-bound aliases
3. Full pipeline: All 89 solving models, no match regressions

---

## 7. Interaction with Dollar-Condition Propagation (#1112)

### 7.1 Independence Assessment

The alias fix (#1111) and dollar-condition propagation (#1112) modify **different aspects** of the AD pipeline:

| Aspect | #1111 (Alias) | #1112 (Dollar-Condition) |
|--------|---------------|--------------------------|
| Primary function | `_diff_varref()` | `_diff_dollar_conditional()` |
| Data threaded | `bound_indices: frozenset[str]` | Condition metadata on gradient entries |
| Trigger | Alias indices in VarRef | DollarConditional AST nodes |
| Output | `sameas()` guards | `$()` conditions on stationarity equations |

### 7.2 No Coupling

- #1111 adds a `bound_indices` parameter to `differentiate_expr` — #1112 does not touch this parameter
- #1112 modifies how `DollarConditional` derivatives propagate conditions — #1111 does not touch `DollarConditional`
- Both can be implemented and tested independently
- Recommended implementation order: #1111 first (higher leverage, more models affected), then #1112

### 7.3 Models Requiring Both Fixes

Some models may need both alias and dollar-condition fixes. These will need to be tested after BOTH fixes are applied. No models have been identified that require both simultaneously to produce a correct result.

---

## 8. Known Unknowns Verification

### KU-12 (Critical): Can alias-aware differentiation be implemented without regression?

**Result:** ⚠️ PARTIALLY CONFIRMED — The summation-context tracking design specifically addresses the Sprint 22 regression by distinguishing bound vs. free alias indices. The `bound_indices` parameter is threaded only through `_diff_sum()` and `_diff_prod()`, which are the exact locations where iteration variables become bound. dispatch's pattern (`Alias(i,j); sum((i,j), ...)`) will correctly have `j` in `bound_indices`. However, full verification requires implementation and pipeline testing — the design is sound but edge cases in partial collapse and nested sums may emerge.

### KU-13 (High): Does the alias fix only affect alias-using models (selectivity)?

**Result:** ✅ VERIFIED — The alias matching code path is only entered when (1) `config.model_ir.aliases` is non-empty, AND (2) exact `_indices_match()` fails. The 56 non-alias solving models have no `Alias` declarations, so `model_ir.aliases` is empty and condition (1) is never met — the alias code path is unreachable for these models. For the 33 alias-declaring models, condition (2) — exact match failure — is the secondary gate that determines whether alias matching is attempted. In practice, the fix will produce identical output for all currently-matching models because their derivatives already match exactly.

### KU-15 (High): Are alias and dollar-condition fixes independent (no coupling)?

**Result:** ✅ VERIFIED — The two fixes modify orthogonal aspects of the AD pipeline. #1111 adds `bound_indices` threading and alias-aware matching in `_diff_varref()`. #1112 modifies condition metadata propagation in `_diff_dollar_conditional()` and stationarity assembly. No shared data structures, no overlapping code paths, no ordering dependency.

### KU-16 (Medium): Is the non-convex multi-KKT divergence population irreducible (~12 models)?

**Result:** ⚠️ PARTIALLY CONFIRMED — Sprint 22 KU-29 identified ~12 non-convex models as permanently mismatching. The current data shows 36 total mismatch models. Of the 21 alias-using mismatches, some overlap with the non-convex population (e.g., catmix, camshape, polygon, kand, cclinpts have large relative differences suggesting non-convex multi-KKT behavior). The non-convex ceiling may be lower than 12 if some "non-convex" mismatches are actually alias bugs. After the alias fix, the residual non-convex population should become clearer. Expected: 8-12 irreducible non-convex models.

### KU-17 (High): Are verified-convex mismatch models fixable (guaranteed matches if KKT bugs fixed)?

**Result:** ⚠️ PARTIALLY CONFIRMED — For convex models, KKT conditions are sufficient for optimality, so correct KKT derivatives guarantee a match. The CGE models (irscge, lrgcge, moncge, stdcge) have small relative differences (1-2%) suggesting they may become matches with the alias fix. The ps* family (ps2_s, ps2_f_s, ps3_s variants) has small differences (0.5-9%) consistent with partial derivative errors. However, without a formal convexity classification for each model, we cannot guarantee which are truly convex. The alias fix should convert the convex subset; the non-convex subset will remain as multi-KKT divergence.

---

## 9. Implementation Schedule

| Step | Description | Estimated Time |
|------|-------------|----------------|
| 1 | Add `_same_root_set()` and `_alias_match()` helpers | 30 min |
| 2 | Add `bound_indices` parameter to all `_diff_*` functions | 1 hour |
| 3 | Thread `bound_indices` through `_diff_sum()` and `_diff_prod()` | 30 min |
| 4 | Add alias-aware matching in `_diff_varref()` | 30 min |
| 5 | Unit tests for alias matching | 1 hour |
| 6 | Integration tests (qabel, dispatch) | 30 min |
| 7 | Full pipeline regression test | 30 min |
| 8 | Fix any edge cases discovered | 1 hour (buffer) |
| **Total** | | **4-6 hours** |

---

## 10. References

- **Issue #1111:** AD engine: alias-aware differentiation with summation-context tracking
- **Issue #1089:** qabel regression investigation (partial collapse + index order)
- **Sprint 22 KU-27:** Alias-aware differentiation deferred to Sprint 23
- **Sprint 22 KU-29:** Non-convex multi-KKT divergence (~12 models)
- **dispatch regression:** Sprint 22 naive fix reverted — `Alias(i,j); sum((i,j), p(i)*b(i,j)*p(j))` pattern
- **Code:** `src/ad/derivative_rules.py`, `src/config.py` (Config.model_ir carries aliases)

---

**Document Created:** 2026-03-19
**Status:** Design complete, ready for implementation in Sprint 23 Priority 3
