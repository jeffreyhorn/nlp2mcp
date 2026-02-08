# Parser: Domain Mismatch Error When Combining Sums with Different Iteration Domains

**GitHub Issue**: #429  
**URL**: https://github.com/jeffreyhorn/nlp2mcp/issues/429  
**Priority**: MEDIUM  
**Complexity**: Medium  
**Estimated Effort**: 2-4 hours  
**Tier 2 Models Blocked**: water.gms

## Summary

When an equation combines multiple sum expressions that iterate over different domains (e.g., `sum(arc(np,n), ...)` and `sum(arc(n,np), ...)`), the parser raises a "domain mismatch" error even though the resulting sums should both reduce to the same outer domain.

## Current Behavior

When parsing water.gms line 87, the parser fails with:

```
ParserSemanticError: Expression domain mismatch [context: equation 'cont' LHS] [domain: ('n',)]
```

The failing line is:
```gams
cont(n).. sum(a(np,n), q(a)) - sum(a(n,np), q(a)) + s(n)$rn(n) =e= node(n,"demand");
```

## Expected Behavior

The parser should recognize that:
1. `sum(a(np,n), q(a))` iterates over `(np,n)` pairs and reduces to domain `(n,)` (np is summed out)
2. `sum(a(n,np), q(a))` iterates over `(n,np)` pairs and reduces to domain `(n,)` (np is summed out)
3. `s(n)` has domain `(n,)`
4. All three terms have the same resulting domain `(n,)` and can be combined

## GAMS Semantics

In GAMS, a sum aggregates over its iteration domain and removes those indices from the result:
- `sum(i, x(i))` → scalar (i is summed out)
- `sum(i, x(i,j))` → domain `(j,)` (i is summed out, j remains)
- `sum((i,j), x(i,j,k))` → domain `(k,)` (i,j summed out)

The key insight is that the **iteration order** within the sum doesn't affect the **result domain**. Both `sum(a(np,n), ...)` and `sum(a(n,np), ...)` sum over the same set `a` and produce results indexed only by indices NOT in the sum's iteration domain.

## Reproduction

### Minimal Test Case

```gams
Set n / a, b, c /;
Alias(n, np);
Set arc(n,n) / a.b, b.c /;
Variable q(n,n), s(n);

Equation test(n);
test(n).. sum(arc(np,n), q(np,n)) + s(n) =e= 0;
```

This fails with "Expression domain mismatch" even though:
- The sum iterates over `(np,n)` pairs filtered by `arc`
- The equation domain is `(n,)`
- Variable `s(n)` has domain `(n,)`

### water.gms (line 87)

```gams
cont(n).. sum(a(np,n), q(a)) - sum(a(n,np), q(a)) + s(n)$rn(n) =e= node(n,"demand");
```

## Root Cause

In `src/ir/parser.py`, the `_merge_domains` method strictly checks that all expression domains are identical:

```python
def _merge_domains(self, exprs: Sequence[Expr], node: Tree | Token) -> tuple[str, ...]:
    domains = [self._expr_domain(expr) for expr in exprs if expr is not None]
    if not domains:
        return ()
    first = domains[0]
    for d in domains[1:]:
        if d != first:
            raise self._error("Expression domain mismatch", node)
    return first
```

The issue is that sum expressions may have different **internal** domains attached but should produce the same **result** domain after aggregation.

## Implementation Plan

### Option 1: Fix Sum Domain Calculation (Recommended)

Ensure that Sum expressions correctly calculate their **result domain** by removing the summed indices:

```python
def _build_sum(self, indices, body, condition, free_domain):
    # Calculate result domain = free_domain - sum_indices
    sum_indices = set(indices)
    result_domain = tuple(d for d in free_domain if d not in sum_indices)
    
    sum_expr = Sum(indices, body, condition)
    # Attach result_domain, not the full free_domain
    return self._attach_domain(sum_expr, result_domain)
```

### Option 2: Relax Domain Matching

Make `_merge_domains` more flexible by checking domain **compatibility** rather than exact equality. Domains are compatible if they represent the same logical indexing after aggregation.

### Recommendation

Option 1 is preferred as it fixes the root cause - Sum expressions should carry their result domain, not their internal iteration domain.

## Testing Requirements

1. Sum with different iteration order: `sum(a(np,n), ...) + sum(a(n,np), ...)`
2. Sum combined with scalar indexed by outer domain: `sum(...) + s(n)`
3. Multiple sums with shared outer domain
4. Nested sums
5. Verify water.gms parses successfully after fix

## Impact

**Models Unlocked**: 1 (water.gms)  
**Parse Rate Improvement**: Enables full parsing of water.gms

## Related Issues

- Issue #407: Predefined Constants - FIXED
- Issue #426: Subset Indexing in Assignments - FIXED
- Issue #428: Subset Reference in Expressions - FIXED

All prerequisite issues have been resolved. This is the final blocker for water.gms.

## References

- **GAMS Documentation**: Summation and Aggregation
- **Tier 2 Model**: water.gms (Water Distribution Network Design)
- **Source**: `src/ir/parser.py` - `_merge_domains()` method (line ~3486)
