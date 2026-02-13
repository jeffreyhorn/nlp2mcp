# ISSUE_670 Fix Design: Cross-Indexed Sums in KKT Stationarity Equations

**Created:** February 13, 2026
**Sprint:** 19 Prep Task 4
**Issue:** GAMS Error 149 "Uncontrolled set entered as constant"
**Priority:** P1 (highest ROI from FIX_ROADMAP)
**Affected Models:** abel, qabel, chenery, mexss, orani, robert (secondary)

---

## Executive Summary

When a constraint contains a sum over an index that also appears in a cross-referenced parameter (e.g., `sum(np, a(n,np)*x(np,k))`), differentiating with respect to the variable produces derivative expressions with indices not present in the stationarity equation's domain. GAMS rejects these as Error 149: "Uncontrolled set entered as constant."

**Root cause:** The stationarity builder in `src/kkt/stationarity.py` wraps terms in sums based only on the constraint multiplier's domain vs. the variable's domain. It does not analyze which indices actually appear in the derivative expression itself. When the derivative contains indices from the original constraint's sum that are outside both domains, those indices go uncontrolled.

**Recommended fix:** Option A — Add a `_collect_free_indices()` utility that walks the derivative expression tree, then wrap any indices not in the stationarity equation's domain in appropriate sums. This is localized to `stationarity.py` (plus a small helper) and compatible with existing `expr_to_gams.py` index aliasing.

**Refined effort estimate:** 10-14 hours (narrowed from 8-16h).

---

## Per-Model Analysis

### 1. abel (Linear Quadratic Control)

**Source:** `data/gamslib/raw/abel.gms`

**Constraint:**
```gams
criterion..
   j =e= .5*sum((k,n,np), (x(n,k) - xtilde(n,k))*w(n,np,k)*(x(np,k) - xtilde(np,k)))
      +  .5*sum((ku,m,mp), (u(m,ku) - utilde(m,ku))*lambda(m,mp)*(u(mp,ku) - utilde(mp,ku)));
```

**Stationarity equation for x(n,k):**
The derivative of the `criterion` constraint w.r.t. `x(n,k)` produces terms containing `np` (from the sum index). The generated `stat_x(n,k)` equation references `a(n,np)` where `np` is not in the equation domain `(n,k)`.

**Generated output (from `data/gamslib/mcp/abel_mcp.gms`):**
```gams
stat_x(n,k).. ... + ((-1) * (a(n,np) + sum(m, 0))) * nu_stateq(n,k) =E= 0;
```

**Uncontrolled index:** `np` — appears in derivative but not in `stat_x` domain `(n,k)`.

**What it should be:**
```gams
stat_x(n,k).. ... + sum(np, ((-1) * a(n,np)) * nu_stateq(n,k)) =E= 0;
```

---

### 2. qabel (Quadratic Version of abel)

**Source:** `data/gamslib/raw/qabel.gms`

**Constraint:** Identical to abel — same `criterion` equation structure.

**Uncontrolled index:** `np` — same pattern as abel.

---

### 3. chenery (Substitution and Structural Change)

**Source:** `data/gamslib/raw/chenery.gms`

**Constraint:**
```gams
sup(i).. p(i) =e= sum(j, aio(j,i)*p(j)) + v(i);
```

**Stationarity equation for p(i):**
Differentiating `sup(i)` w.r.t. `p(i)` collapses the sum to the diagonal: the current generated output shows `(1 - aio(i,i)) * nu_sup(i)` in `stat_p(i)` with no free `j`. The scalar stationarity equations (`stat_pd`, etc.) show `(-1) * sum(j, 0) * nu_sup(...)` — the cross-derivative simplifies to zero.

**Current status:** The generated `data/gamslib/mcp/chenery_mcp.gms` does not exhibit an uncontrolled index in `stat_p(i)` because the AD system produces a diagonal result. However, chenery is included because (a) the `sup(i)` constraint has the cross-indexed sum pattern, and (b) a more complete AD (producing non-zero off-diagonal derivatives) would expose the uncontrolled `j` index. The proposed `_collect_free_indices()` fix would handle this case if the AD output changes.

**Potential uncontrolled index:** `j` — from `sum(j, aio(j,i)*p(j))`, if the AD produces non-zero off-diagonal terms.

---

### 4. mexss (Mexico Steel — Small Static)

**Source:** `data/gamslib/raw/mexss.gms`

**Constraints:**
```gams
mbf(cf,i).. sum(p, a(cf,p)*z(p,i)) =g= sum(j, x(cf,i,j)) + e(cf,i);
mbi(ci,i).. sum(p, a(ci,p)*z(p,i)) =g= 0;
mbr(cr,i).. sum(p, a(cr,p)*z(p,i)) + u(cr,i) =g= 0;
cc(m,i)..   sum(p, b(m,p)*z(p,i))  =l= k(m,i);
```

**Stationarity equation for z(p,i):**
Differentiating these constraints w.r.t. `z(p,i)` yields terms in `a(c,p)` after index aliasing. In the generated `stat_z(p,i)` equations, the subset indices `cf`, `ci`, `cr`, and `m` are all correctly bound by the outer `sum(cf, ...)`, `sum(ci, ...)`, etc.; the actual uncontrolled index is `c` inside `a(c,p)`, which is not in the stationarity equation's domain.

**Generated output (from `data/gamslib/mcp/mexss_mcp.gms`):**
```gams
stat_z(p,i).. ... + sum(cf, (sum(j, 0) - a(c,p)) * lam_mbf(cf,i))
              + sum(ci, ((-1) * a(c,p)) * lam_mbi(ci,i)) + ...
```

**Uncontrolled index:** `c` (manifest as `cf`, `ci`, `cr` subsets) in `a(c,p)` — the index replacement maps the concrete element to `c` (the parameter's declared domain) rather than to the constraint-specific subset index.

**Note:** Some terms correctly get wrapped in `sum(cf, ...)` etc. by the existing domain-comparison logic (because `cf` is the multiplier domain which is disjoint from `var_domain`). The issue here is the derivative expression itself containing `c` (from the parameter's declared domain) when it should contain the constraint's domain index.

---

### 5. orani (Miniature Version of ORANI-78)

**Source:** `data/gamslib/raw/orani.gms`

**Constraints:**
```gams
indc(c,s,i).. x(c,s,i) =e= z(i) - (p(c,s) - sum(sp, alpha(c,sp,i)*p(c,sp)));
pric(i)..     sum(c, r(c,i)*p(c,"domestic")) =e= sum((c,sp), sc(c,sp,i)*p(c,sp)) + ...;
```

**Stationarity equation for p(c,s):**
Differentiating `indc(c,s,i)` w.r.t. `p(c,s)` produces `1 - alpha(c,sp,i)` terms where `sp` and `i` are in the constraint domain but `sp` is not in the variable domain `(c,s)`. The term `alpha(c,sp,i) * nu_indc(c,s,i)` gets correctly summed over `i` (from the multiplier domain), but `sp` may remain uncontrolled.

**Uncontrolled index:** `sp` — from `sum(sp, alpha(c,sp,i)*p(c,sp))`.

---

### 6. robert (Elementary Production and Inventory Model)

**Source:** `data/gamslib/raw/robert.gms`

**Primary issue:** E170 from table parsing (ISSUE_399).

**Secondary ISSUE_670 constraint:**
```gams
sb(r,tt).. s(r,tt+1) =e= s(r,tt) - sum(p, a(r,p)*x(p,tt));
pd.. profit =e= sum(t, sum(p, c(p,t)*x(p,t)) - sum(r, misc("storage-c",r)*s(r,t)));
```

**Stationarity equation for x(p,tt):**
Differentiating `pd` w.r.t. `x(p,t)` gives `c(p,t)` where `t` is a subset of `tt` (the variable domain), creating a subset/domain mismatch. The term `c(p,t) * nu_pd` has `t` referencing a subset, not the variable's domain `tt`.

**Uncontrolled index:** `t` (subset of `tt`) — a domain mismatch variant of the cross-indexed pattern.

**Note:** robert requires both ISSUE_399 (parser) and ISSUE_670 (KKT) fixes.

---

## Common Pattern

All 6 models share the same fundamental pattern:

1. **Constraint** `eq(d1, d2, ...)` contains an expression `sum(s, f(d1, s) * x(s, d2))` where `s` is the sum index
2. **Differentiation** w.r.t. variable `x(v1, v2)` should, mathematically, yield a derivative term `f(d1, v1)` where:
   - `v1` comes from the variable's domain (correctly controlled)
   - `d1` comes from the constraint's domain (controlled via the multiplier's domain)
   - However, in the current implementation the index-replacement / expression-building step can incorrectly reintroduce a symbolic index derived from `s` (or map it to the wrong symbolic name or set)
3. **Result:** The generated stationarity equation `stat_x(v1, v2)` can contain an apparently free index whose symbol comes from the original sum index `s`, so it is not controlled by the equation's declared domain and GAMS reports it as Error 149

**Variations:**
- **abel/qabel:** Multi-index sum `sum((k,n,np), ...)` with cross-referenced matrix `w(n,np,k)`
- **chenery:** Simple cross-indexed sum `sum(j, aio(j,i)*p(j))`
- **mexss:** Parameter indexed by subset (`a(cf,p)` where `cf` is a subset of `c`)
- **orani:** Multi-level cross-indexing in `sum(sp, alpha(c,sp,i)*p(c,sp))`
- **robert:** Subset/superset domain mismatch (`t` subset of `tt`)

Despite these variations, all are addressable by the same fix: detect uncontrolled free indices in derivative expressions and wrap them in sums.

---

## Root Cause Analysis

### Exact Code Path

1. **Entry:** `build_stationarity_equations()` in `stationarity.py` creates stationarity equations with `domain = var_def.domain`

2. **Jacobian term addition:** `_add_indexed_jacobian_terms()` in `stationarity.py` processes each constraint's Jacobian entry

3. **Index replacement:** `_replace_indices_in_expr()` in `stationarity.py` converts concrete element labels to symbolic set names. For parameters, it uses the parameter's declared domain (`prefer_declared_domain=True`) which can map a variable-domain index to the wrong set name (e.g., `"p1"` mapped to `"np"` instead of `"p"`)

4. **Sum wrapping decision:** Within `_add_indexed_jacobian_terms()`, the logic compares `mult_domain_set` vs `var_domain_set`:
   - Exact match → no sum
   - Subset → no sum
   - Disjoint → wrap in `Sum(mult_domain, ...)`
   - Partial overlap → wrap extra indices in sum

5. **The gap:** This logic only considers the multiplier's domain indices. It does NOT check whether the derivative expression itself contains additional free indices that are outside both `mult_domain` and `var_domain`. Those indices go uncontrolled.

### Two Sub-Problems

**Sub-problem A: Index replacement produces wrong symbolic name**
When `_replace_matching_indices()` processes `a("n1", "p1")` with `declared_domain=("n", "np")`, it maps position 1 to `"np"` (from the parameter's declaration) instead of `"p"` (from the variable's domain). This produces `a(n, np)` when it should produce `a(n, p)`.

**Sub-problem B: No detection of uncontrolled indices in derivative expressions**
Even if index replacement is correct, the sum wrapping logic doesn't analyze the derivative expression for free indices. If a derivative contains indices outside both `mult_domain` and `var_domain`, they are never detected or wrapped.

---

## Fix Options

### Option A: Post-Replacement Free Index Analysis (Recommended)

**Approach:** After the existing `_replace_indices_in_expr()` call, analyze the resulting expression to find all free indices. Any index not in `var_domain ∪ mult_domain` (and not bound by a sum within the expression) gets wrapped in an outer sum.

**Implementation:**

1. Add `_collect_free_indices(expr: Expr, model_ir: ModelIR) -> set[str]` as a private helper in `stationarity.py`. This function walks the expression tree, uses `model_ir.sets` and `model_ir.aliases` to distinguish set indices from element labels, and respects Sum-bound indices. (See full implementation in the "Implementation Sketch" section below.)

2. In `_add_indexed_jacobian_terms()`, after building the term, add:
   ```python
   # Detect uncontrolled indices in derivative expression
   free_indices = _collect_free_indices(indexed_deriv, kkt.model_ir)
   controlled = var_domain_set | mult_domain_set
   uncontrolled = free_indices - controlled
   
   if uncontrolled:
       # Wrap the entire term in sum over uncontrolled indices
       term = Sum(tuple(sorted(uncontrolled)), term)
   ```

**Pros:**
- Localized to `stationarity.py` — no changes to AD, parser, or emit modules
- Works regardless of whether index replacement is perfect (catches any escaping index)
- Compatible with existing `expr_to_gams.py` index aliasing (operates at IR level, before emission)
- Low regression risk — only adds wrapping, never removes existing behavior

**Cons:**
- Doesn't fix Sub-problem A (wrong index replacement) — the sum wrapping only guarantees syntactic control (avoids GAMS Error 149); numeric correctness still depends on index replacement mapping to the intended set (or on an additional mapping step that rewrites indices back to the correct subset)

**Estimated effort:** 10-14 hours
- 3-4h: Implement `_collect_free_indices()` with unit tests
- 2-3h: Integrate into `_add_indexed_jacobian_terms()` sum wrapping logic
- 2-3h: Also handle the scalar stationarity path (`_add_jacobian_transpose_terms_scalar`)
- 3-4h: Validate all 6 models, fix edge cases

---

### Option B: Fix Index Replacement in _replace_matching_indices()

**Approach:** Fix Sub-problem A directly by making `_replace_matching_indices()` aware of the stationarity context. When replacing indices in a derivative expression, distinguish between:
- Indices from the **variable's domain** → map to variable domain set names
- Indices from the **constraint's domain** → map to constraint domain set names
- Indices from the **sum's iteration** → these were collapsed by differentiation and should map to the variable domain (since `sum(np, f(np)) → f(p)` when differentiating w.r.t. `x(p)`)

**Implementation:**
Pass additional metadata to `_replace_matching_indices()`:
```python
def _replace_matching_indices(
    indices, element_to_set,
    declared_domain=None,
    equation_domain=None,
    model_ir=None,
    prefer_declared_domain=False,
    variable_domain=None,        # NEW: the stationarity equation's domain
    constraint_domain=None,      # NEW: the constraint's domain
):
```

Use `variable_domain` and `constraint_domain` to disambiguate: if an element label belongs to a set in `variable_domain`, prefer that mapping over `declared_domain`.

**Pros:**
- Fixes the root cause of wrong index names
- Produces cleaner output (correct symbolic names without unnecessary sums)

**Cons:**
- High complexity — `_replace_matching_indices()` already has 7 parameters and complex branching
- Higher regression risk — changing index replacement affects ALL stationarity equations, not just cross-indexed ones
- Doesn't address Sub-problem B (indices that are genuinely from the constraint's sum domain and need wrapping)
- Would still need Option A's free index detection for completeness

**Estimated effort:** 14-20 hours

---

### Option C: Post-Process Stationarity Equations at Emission Time

**Approach:** Instead of fixing the IR-level stationarity builder, detect uncontrolled indices when emitting GAMS code in `src/emit/equations.py` or `src/emit/expr_to_gams.py`. Before emitting each stationarity equation, compare the equation's domain with all indices in the expression and wrap uncontrolled ones in sums.

**Implementation:**
Add a pass in the equation emitter that:
1. Collects all index references in the equation body
2. Compares with the equation's declared domain
3. Wraps uncontrolled indices in `sum(idx, ...)` in the GAMS output

**Pros:**
- Completely separate from stationarity builder — zero risk to existing KKT logic
- Could catch other uncontrolled index issues beyond ISSUE_670

**Cons:**
- Wrong abstraction layer — the IR should be semantically correct; emission should not fix semantic errors
- Harder to test — requires full pipeline execution to verify
- May conflict with `expr_to_gams.py`'s existing index aliasing logic
- Doesn't fix the IR representation — downstream consumers of the IR would still see uncontrolled indices

**Estimated effort:** 12-18 hours

---

## Recommended Approach: Option A

**Option A (Post-Replacement Free Index Analysis)** is recommended because:

1. **Correct abstraction layer:** Fixes the IR before emission, keeping the KKT system semantically valid
2. **Localized change:** Only `stationarity.py` needs modification (plus a small utility function)
3. **Robust:** Catches uncontrolled indices regardless of their source (wrong replacement, sum collapse, subset mismatch)
4. **Low regression risk:** Adds wrapping without changing existing replacement logic
5. **Compatible:** The `expr_to_gams.py` index aliasing already extends `domain_vars` with indices introduced by `Sum` nodes (via its Sum-handling / `resolve_index_conflicts()` logic), so new Sum wrappers integrate seamlessly

### Implementation Sketch

```python
# New utility function in stationarity.py

def _collect_free_indices(expr: Expr, model_ir: ModelIR) -> set[str]:
    """Collect all free (unbound) symbolic set indices in an expression.
    
    Returns set index names that appear in VarRef/ParamRef/MultiplierRef
    but are not bound by an enclosing Sum. Literal strings (quoted element
    labels like "domestic") are excluded using model_ir.sets for validation.
    """
    known_sets = set(model_ir.sets.keys()) | set(model_ir.aliases.keys())
    
    def _walk(e: Expr, bound: frozenset[str]) -> set[str]:
        match e:
            case VarRef(_, indices) | ParamRef(_, indices) | MultiplierRef(_, indices):
                free = set()
                for idx in (indices or ()):
                    if isinstance(idx, str) and idx in known_sets and idx not in bound:
                        free.add(idx)
                return free
            case Sum(index_sets, body):
                return _walk(body, bound | frozenset(index_sets))
            case Binary(_, left, right):
                return _walk(left, bound) | _walk(right, bound)
            case Unary(_, child):
                return _walk(child, bound)
            case Call(_, args):
                return set().union(*(_walk(a, bound) for a in args))
            case Const(_):
                return set()
            case _:
                return set()
    
    return _walk(expr, frozenset())


# Integration in _add_indexed_jacobian_terms(), after line ~835:

# After building: term = Binary("*", indexed_deriv, mult_ref)

# Existing domain comparison logic handles mult_domain vs var_domain...
# After that, add:

free_in_deriv = _collect_free_indices(indexed_deriv, kkt.model_ir)
controlled = var_domain_set | mult_domain_set
uncontrolled = free_in_deriv - controlled

if uncontrolled:
    # These indices appear in the derivative but aren't controlled
    # by either the stationarity equation domain or the multiplier.
    # Wrap in a sum to make them controlled.
    sum_indices = tuple(sorted(uncontrolled))
    term = Sum(sum_indices, term)
```

### Handling the Scalar Stationarity Path

The function `_add_jacobian_transpose_terms_scalar()` handles per-instance stationarity equations. This path also needs the same fix — after building the `Binary("*", derivative, mult_ref)` term, check for free indices not in the equation's implicit domain and wrap them. Since scalar stationarity equations have no domain (they are element-specific), any free set index in the derivative is potentially uncontrolled and needs wrapping.

### Edge Cases

1. **Indices that are element labels, not set names:** The `_collect_free_indices()` function uses `model_ir.sets` to distinguish set names from element labels. Strings like `"domestic"` or `"storage-c"` are not in `model_ir.sets` and will be correctly excluded.

2. **Indices already wrapped in sums by the existing logic:** The `_collect_free_indices` function respects Sum boundaries — an index bound by an enclosing Sum is not counted as free. So there's no double-wrapping.

3. **IndexOffset objects (lead/lag):** These are not string indices and will be naturally excluded from the free index set.

4. **Alias indices:** Aliases (e.g., `np` as alias of `n`) are included in `model_ir.aliases` and checked in `_collect_free_indices()`.

---

## Compatibility with expr_to_gams.py Index Aliasing

The existing index aliasing in `expr_to_gams.py` (for GAMS Error 125) handles a different problem: when a Sum's index variable shadows the equation's domain variable. For example:

```gams
stat_x(i).. sum(i, ...) =E= 0;  -- Error 125: i conflicts
-- Fixed by aliasing: sum(i__, ...) =E= 0;
```

The ISSUE_670 fix (Option A) adds new Sum wrappers at the IR level. When these sums are emitted, `expr_to_gams.py`'s `resolve_index_conflicts()` will automatically check for shadowing conflicts and apply aliases if needed. This means:

- If we add `Sum(("np",), term)` and the stationarity equation is `stat_x(np,k)`, the emitter will detect the conflict and alias `np` → `np__`
- This is the correct behavior — the two fixes compose cleanly

**No changes needed in `expr_to_gams.py`.**

---

## Test Strategy

### Unit Tests

1. **`test_collect_free_indices()`**: Test the new utility function with various expression structures:
   - Simple ParamRef with indices → returns those indices
   - Expression with Sum binding some indices → returns only unbound ones
   - Nested sums → respects inner and outer bindings
   - Expressions with literal strings (not set names) → excluded
   - Expressions with IndexOffset → excluded

2. **`test_uncontrolled_index_wrapping()`**: Test that `_add_indexed_jacobian_terms()` wraps uncontrolled indices:
   - Construct a minimal KKT system where the derivative contains an uncontrolled index
   - Verify the resulting expression has a Sum wrapper

3. **`test_no_spurious_wrapping()`**: Test that correctly controlled indices are NOT wrapped:
   - Derivative with only var_domain and mult_domain indices → no extra Sum
   - Derivative with Sum-bound indices → no extra wrapping

### Integration Tests (Model Validation)

For each of the 6 affected models, run the full pipeline and verify:

```bash
# For each model: abel, qabel, chenery, mexss, orani, robert
python -m src.cli data/gamslib/raw/{model}.gms -o output/{model}_mcp.gms
gams output/{model}_mcp.gms
# Verify: no Error 149
```

**Specific validation checks:**
- **abel/qabel:** Verify `stat_x(n,k)` contains `sum(np, ...)` wrapping the derivative term
- **chenery:** Verify `stat_p(i)` contains `sum(j, ...)` for the `aio(j,i)` term
- **mexss:** Verify `stat_z(p,i)` correctly sums over subset indices
- **orani:** Verify `stat_p(c,s)` contains `sum(sp, ...)` and `sum(i, ...)` as needed
- **robert:** Verify after ISSUE_399 is also fixed (robert needs both fixes)

### Regression Tests

Run the full test suite to ensure no existing models break:
```bash
make test  # All 3294 tests must pass
```

Run the 61 currently-passing gamslib models to verify no regressions:
```bash
python scripts/gamslib/run_full_test.py
# All 61 models must still pass (see scripts/gamslib/ for options)
```

---

## Effort Estimate

**Refined estimate: 10-14 hours** (from 8-16h)

| Task | Hours | Notes |
|------|-------|-------|
| Implement `_collect_free_indices()` | 2-3h | Utility + unit tests |
| Integrate into `_add_indexed_jacobian_terms()` | 2-3h | Main fix + edge cases |
| Handle scalar stationarity path | 1-2h | `_add_jacobian_transpose_terms_scalar()` |
| Test with abel/qabel (simplest) | 1h | First validation |
| Test with chenery, mexss, orani | 2-3h | More complex patterns |
| Test robert (needs ISSUE_399 too) | 1h | Verify ISSUE_670 portion |
| Regression testing | 1-2h | Full suite + 61 gamslib models |

**Risk factors that could push toward 14h:**
- Edge cases in `_collect_free_indices()` for models with unusual naming
- Interaction with subset/superset logic in `_replace_matching_indices()` (Issue #620)
- robert requiring coordination with ISSUE_399 fix

---

## Dependencies

- No external dependencies
- ISSUE_399 (table parsing) must be fixed separately for robert to fully pass
- The fix is independent of other Sprint 19 work items (lexer, IndexOffset, etc.)

---

## Cross-References

- **ISSUE_670 doc:** `docs/issues/ISSUE_670_cross-indexed-sums-error-149.md`
- **FIX_ROADMAP:** `docs/planning/EPIC_4/SPRINT_18/FIX_ROADMAP.md` (Priority 1)
- **Sprint 18 Day 7-8 log:** `docs/planning/EPIC_4/SPRINT_18/SPRINT_LOG.md`
- **Known Unknowns:** 8.1 (code path), 8.2 (common pattern)
- **Related issues:** ISSUE_399 (robert), GAMS Error 125 (index aliasing in expr_to_gams.py)
