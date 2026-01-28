# Issue: Partial Index Match Returns Wrong Concrete Values for Non-Prefix Matches

**Status:** Fixed  
**Category:** Automatic Differentiation  
**Affected Component:** `src/ad/derivative_rules.py`  
**Priority:** High  
**GitHub Issue:** [#577](https://github.com/jeffreyhorn/nlp2mcp/issues/577)

## Summary

The `_partial_index_match` function in `derivative_rules.py` correctly identifies when a sum index matches a `wrt_index` at a non-prefix position (e.g., position 1 instead of position 0), but it does not return the matched concrete value. The caller then incorrectly assumes prefix matching and takes `wrt_indices[:N]` as the matched concrete values, producing incorrect derivatives for nested sums.

## Reproduction

### Minimal Test Case

Consider differentiating a nested sum expression:

```python
# Expression: sum(g, sum(dl, y(g, dl)))
# Differentiating w.r.t. y(g1, h) where g1 ∈ G and h ∈ DL

# Model setup:
# Sets: G = {g1, g2}, DL = {h, k}
# Variable: y(G, DL)

from src.ad.derivative_rules import differentiate_expr
from src.ir.ast import Sum, VarRef

# Build AST for: sum(g, sum(dl, y(g, dl)))
inner_var = VarRef(name="y", indices=("g", "dl"))
inner_sum = Sum(index_sets=("dl",), body=inner_var)
outer_sum = Sum(index_sets=("g",), body=inner_sum)

# Differentiate w.r.t. y(g1, h)
result = differentiate_expr(
    outer_sum, 
    wrt_var="y", 
    wrt_indices=("g1", "h"),
    config=config  # config with model_ir containing set definitions
)
```

### Expected Behavior

The derivative of `sum(g, sum(dl, y(g, dl)))` w.r.t. `y(g1, h)` should be `1` because:
1. Outer sum over `g`: When `g = g1`, inner expression contributes
2. Inner sum over `dl`: When `dl = h`, `y(g1, h)` matches `y(g, dl)`
3. Result: `∂y(g,dl)/∂y(g1,h) = 1` when `g=g1` and `dl=h`

### Actual Behavior (Before Fix)

The derivative was incorrectly computed because:
1. Outer sum matches `g` with `g1` at position 0 → correct
2. Inner sum receives `wrt_indices = ("g", "h")` (symbolic `g`, concrete `h`)
3. `_partial_index_match(("dl",), ("g", "h"))` finds `dl` matches `h` at position 1
4. Returns `matched_indices = ("dl",)`, `remaining_indices = ("g",)`
5. **BUG:** Caller takes `matched_concrete = wrt_indices[:1] = ("g",)` - WRONG!
6. Should be `matched_concrete = ("h",)` - the actual matched value

This causes `_substitute_sum_indices` to substitute `dl → g` instead of `dl → h`, producing incorrect results.

## Root Cause Analysis

The bug is in the interaction between `_partial_index_match` and its caller in `_diff_sum`:

### Before Fix (Buggy Code)

```python
# In _partial_index_match - finds match at non-prefix position but doesn't return it
if _is_concrete_instance_of(wrt_idx, sum_idx, config):
    remaining = wrt_indices[:i] + wrt_indices[i + 1 :]
    return (sum_idx,), remaining  # Only returns symbolic, not concrete!

# In _diff_sum - assumes prefix matching
matched_indices, remaining_indices = _partial_index_match(...)
matched_concrete = wrt_indices[: len(matched_indices)]  # WRONG for non-prefix!
```

### Problem

When `_partial_index_match` finds a match at position 1 (not 0), the caller's assumption that `matched_concrete = wrt_indices[:N]` is invalid. The matched concrete value is at position 1, not position 0.

## Fix Applied

The fix modifies `_partial_index_match` to return a third tuple containing the matched concrete values:

### After Fix

```python
def _partial_index_match(
    sum_index_sets: tuple[str, ...],
    wrt_indices: tuple[str, ...],
    config: Config | None = None,
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    """
    Returns:
        Tuple of (matched_symbolic_indices, matched_concrete_indices, remaining_indices)
    """
    # ...
    if _is_concrete_instance_of(wrt_idx, sum_idx, config):
        remaining = wrt_indices[:i] + wrt_indices[i + 1 :]
        return (sum_idx,), (wrt_idx,), remaining  # Now returns matched concrete!

# In _diff_sum - uses returned concrete values
matched_indices, matched_concrete, remaining_indices = _partial_index_match(...)
# Use matched_concrete from _partial_index_match (not prefix of wrt_indices)
result_body = _substitute_sum_indices(
    body_derivative, matched_indices, matched_concrete
)
```

## Test Case

A test should verify that nested sums with non-prefix index matching produce correct derivatives:

```python
def test_nested_sum_nonprefix_index_match():
    """Test that nested sums correctly match indices at non-prefix positions."""
    # sum(g, sum(dl, y(g, dl))) differentiated w.r.t. y(g1, h)
    # The inner sum matches dl with h at position 1 (not 0)
    
    config = Config(model_ir=model_ir)  # with G={g1,g2}, DL={h,k}
    
    inner_var = VarRef(name="y", indices=("g", "dl"))
    inner_sum = Sum(index_sets=("dl",), body=inner_var)
    outer_sum = Sum(index_sets=("g",), body=inner_sum)
    
    result = differentiate_expr(outer_sum, "y", ("g1", "h"), config)
    
    # Should produce 1, not an expression with wrong index substitution
    assert isinstance(result, Const)
    assert result.value == 1
```

## Related Files

- `src/ad/derivative_rules.py`: Contains `_partial_index_match` and `_diff_sum`
- `src/ad/index_mapping.py`: Contains `_is_concrete_instance_of` for set membership checks
- `tests/unit/ad/test_derivative_rules.py`: Unit tests for differentiation

## Commit

Fixed in commit `23d3898` on branch `sprint16-day8-solve-fixes`.

## Notes

This bug only manifests with nested sums where the inner sum's index matches a `wrt_index` at a non-prefix position. Simple single-level sums and nested sums where indices match in order (prefix) were unaffected.

The fix is backward compatible - the additional return value is only used when needed, and multi-index prefix matching continues to work as before.
