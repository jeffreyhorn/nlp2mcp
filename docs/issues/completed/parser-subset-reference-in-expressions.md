# Parser: Subset Reference as Variable/Parameter Index in Expressions

**GitHub Issue**: #428  
**URL**: https://github.com/jeffreyhorn/nlp2mcp/issues/428  
**Priority**: HIGH  
**Complexity**: Medium-High  
**Estimated Effort**: 4-6 hours  
**Tier 2 Models Blocked**: water.gms

## Summary

When a subset name is used as an index to a variable or parameter within an expression (e.g., `q(a)` where `a` is a subset), the parser fails because it expects the variable's full domain indices but receives only the subset name.

This is different from Issue #426 (subset indexing in assignments) which has been fixed. This issue is about using subset references in expressions within equations.

## Current Behavior

When parsing water.gms, the parser fails at line 87 with:

```
ParserSemanticError: Variable 'q' expects 2 indices but received 1 
[context: equation 'cont' LHS] [domain: ('n',)] (line 87, column 30)
```

The failing line is:
```gams
cont(n)..  sum(a(np,n), q(a)) - sum(a(n,np), q(a)) + s(n)$rn(n) =e= node(n,"demand");
```

The expression `q(a)` uses subset `a` as an index, where:
- `q` is a variable with domain `(n,n)` (2 indices expected)
- `a` is a set with domain `(n,n)` representing arcs
- `q(a)` should be interpreted as "the q value for arc a" which expands to `q(n,np)` in the sum context

## Expected Behavior

The parser should recognize when a subset name is used as an index and either:
1. Expand the subset reference to the underlying domain indices based on the sum context
2. Store the expression with the subset reference for later resolution

## GAMS Semantics

In GAMS, when you write `q(a)` where `a` is a 2-dimensional set, it's shorthand for accessing `q` using the current iteration values of `a`'s domain. Within `sum(a(np,n), q(a))`:

1. `a(np,n)` iterates over all `(np,n)` pairs in set `a`
2. `q(a)` accesses `q(np,n)` for each iteration
3. The subset `a` acts as both a filter (only iterate over arc pairs) and an index reference

### Examples from water.gms

```gams
Variable q(n,n)  'flow on each arc';
Set a(n,n)       'arcs (arbitrarily directed)';

* In equation - q(a) means q indexed by the current arc
cont(n).. sum(a(np,n), q(a)) - sum(a(n,np), q(a)) + s(n)$rn(n) =e= node(n,"demand");

* Also used with parameters
loss(a(n,np)).. h(n) - h(np) =e= hloss*dist(a)*abs(q(a))**(qpow-1)*q(a)/d(a)**dpow;
```

In `loss(a(n,np))..`, the equation iterates over all arcs, and:
- `dist(a)` accesses the distance parameter for current arc
- `q(a)` accesses the flow variable for current arc
- `d(a)` accesses the diameter parameter for current arc

## Reproduction

### Minimal Test Case

```gams
Set n / a, b, c /;
Set arc(n,n) / a.b, b.c /;

Variable q(n,n) 'flow';
Parameter dist(n,n) / a.b 10, b.c 20 /;

Equation flow_eq(n);

* This fails: q(arc) uses subset as index
flow_eq(n).. sum(arc(i,n), q(arc)) =e= 0;
```

### water.gms (line 87)

```gams
cont(n).. sum(a(np,n), q(a)) - sum(a(n,np), q(a)) + s(n)$rn(n) =e= node(n,"demand");
```

## Root Cause

In `src/ir/parser.py`, the `_make_symbol` method validates that the number of indices matches the variable's domain length. When `q(a)` is parsed:

1. `a` is extracted as a single index
2. `q` has domain `(n,n)` requiring 2 indices
3. Parser raises error: "Variable 'q' expects 2 indices but received 1"

The parser doesn't recognize that `a` is a subset with the same domain structure as `q`, and should be expanded to the underlying domain indices.

## Implementation Plan

### Option 1: Expand Subset at Expression Time (Recommended)

When processing a variable/parameter reference with indices:

1. Check if any index is a subset name
2. If so, get the subset's domain
3. Replace the subset name with the domain indices
4. Validate the expanded indices match the variable's domain

```python
def _make_symbol(self, name, indices, free_domain, node):
    # Check if any index is a subset that should be expanded
    expanded_indices = []
    for idx in indices:
        if idx in self.model.sets:
            subset = self.model.sets[idx]
            if subset.domain:
                # Expand subset to its domain indices
                expanded_indices.extend(subset.domain)
            else:
                expanded_indices.append(idx)
        else:
            expanded_indices.append(idx)
    
    # Now validate with expanded indices
    ...
```

### Option 2: Defer to Runtime

Store the expression with subset references as-is and resolve during model solving. This preserves the original semantics but requires additional runtime handling.

### Recommendation

Option 1 is preferred for consistency with how the parser handles other index expansions.

## Testing Requirements

1. Simple subset as variable index: `q(a)` where `a` is a 2D set
2. Subset in sum expression: `sum(a(i,j), q(a))`
3. Multiple subset references: `dist(a) * q(a)`
4. Nested expressions with subset references
5. Parameter references with subsets: `node(rn, "demand")`
6. Verify water.gms parses successfully

## Impact

**Models Unlocked**: 1 (water.gms)  
**Parse Rate Improvement**: Enables full parsing of water.gms

## Related Issues

- Issue #407: Predefined Constants - FIXED
- Issue #426: Subset Indexing in Assignments - FIXED

Both prerequisite issues have been resolved. This is the final blocker for water.gms.

## References

- **GAMS Documentation**: Set Operations and Indexed Expressions
- **Tier 2 Model**: water.gms (Water Distribution Network Design)
- **Source**: `src/ir/parser.py` - `_make_symbol()` method
