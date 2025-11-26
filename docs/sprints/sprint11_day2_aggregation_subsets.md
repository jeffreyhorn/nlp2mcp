# Sprint 11 Day 2: Aggregation Over Subset Domains

**Date:** 2025-11-26  
**Goal:** Resolve line 59 blocker by supporting subset domains in aggregation functions  
**Status:** ✅ Complete - Line 59→75, parsing 69% of maxmin.gms!

## Overview

After resolving line 51 (subset expansion), we tackled line 59 which required **aggregation over subset domains**. When aggregation functions like `smin`, `smax`, `sum`, or `prod` use a subset with explicit indices as their domain (e.g., `smin(low(n,nn), expr)`), the parser needs to recognize the subset specification and make the underlying indices available in the aggregated expression.

## Problem Statement

Line 59 of maxmin.gms:
```gams
mindist2a.. mindist =e= smin(low(n,nn), sqrt(sum(d, sqr(point(n,d) - point(nn,d)))));
```

The issue: `smin(low(n,nn), ...)` where:
- `low` is a 2D subset defined as `low(n,n)`
- `low(n,nn)` specifies the aggregation domain with explicit indices
- The expression `sqrt(sum(...))` needs to reference `n` and `nn`

**Error:** "Undefined symbol 'low' with indices ('n', 'nn') referenced"

The parser treated `low(n,nn)` as a symbol reference instead of a domain specification.

## Solution

Extended the aggregation function handling in `_expr()` to recognize and process subset domain specifications:

### Key Implementation

```python
# Sprint 11 Day 2: Handle subset domain like low(n,nn)
if isinstance(first_arg, Tree) and first_arg.data == "symbol_indexed":
    # This is a subset domain like 'low(n,nn)' in smin(low(n,nn), expr)
    # Extract the set name and indices
    set_name = _token_text(first_arg.children[0])
    
    # Check if this is a known set
    if set_name in self.model.sets:
        # Extract the indices from the subset reference
        indices_node = first_arg.children[1]
        indices = _extract_indices(indices_node) if len(first_arg.children) > 1 else ()
        
        # Add the subset reference as a SymbolRef for the aggregation
        # (represents the domain being aggregated over)
        args.append(SymbolRef(set_name))
        
        # Remaining arguments are parsed with the subset indices in scope
        # E.g., smin(low(n,nn), expr) - expr can reference n and nn
        extended_domain = free_domain + indices
        for child in arg_list.children[1:]:
            if isinstance(child, (Tree, Token)):
                args.append(self._expr(child, extended_domain))
        
        # Return with free_domain (the subset indices are bound)
        expr = Call(func_name, tuple(args))
        return self._attach_domain(expr, free_domain)
```

## Pattern Support

### Pattern 1: Simple Set Iterator (Already Supported)
```gams
smin(i, x(i))  // i is a simple set name
```

### Pattern 2: Subset with Explicit Indices (New)
```gams
smin(low(n,nn), expr)  // low is a subset, n,nn are the indices
```

The subset indices `n,nn` become available in the aggregated expression.

### Example from maxmin.gms
```gams
Set n, low(n,n);
Variable dist(n,n), mindist, point(n,d);

mindist2a.. mindist =e= smin(low(n,nn), sqrt(sum(d, sqr(point(n,d) - point(nn,d)))));
//                           ^^^^^^^^^^ domain spec with indices
//                                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
//                                            expression can use n, nn, d
```

## Technical Details

### Domain Scope Management

1. **Extract subset name**: `low` from `low(n,nn)`
2. **Extract indices**: `['n', 'nn']` from the index list
3. **Add to SymbolRef**: Create `SymbolRef('low')` for the aggregation domain
4. **Extend domain**: Add `n, nn` to `free_domain` for the aggregated expression
5. **Return with original domain**: The subset indices are local to the aggregation

### Integration with Existing Code

The implementation integrates seamlessly with the existing simple iterator support:
- First checks for `symbol_indexed` (subset with indices)
- Falls back to `symbol_plain` (simple iterator)
- Maintains backward compatibility with all existing aggregation patterns

## Results

### Parse Progress

| Blocker | Line | Description |
|---------|------|-------------|
| Before fix | 59 | `smin(low(n,nn), ...)` - aggregation over subset |
| After fix | 75 | `point.lo(n,d) = 0` - bounds expansion for sets |

**Progress:** 16 additional lines parsed (line 59→75)

**Parse rate:** ~69% of maxmin.gms (75 of 108 lines)

### Test Results

✅ All 1600 tests passing  
✅ No regressions introduced  
✅ maxmin progress tests updated and passing  

## Files Modified

- `src/ir/parser.py:1750-1810` - Extended aggregation function handling for subset domains
- `tests/integration/test_maxmin_full_parse.py` - Updated expectations to line 75
- `tests/integration/test_maxmin_nested_indexing.py` - Updated expectations to line 75

## Remaining Blocker

**Line 75:** `point.lo(n,d) = 0` where `n` is defined as `/p1*p13/`

This requires **handling variable bounds expansion for sets without explicit members**. The set `n` is defined with a range specification but hasn't been expanded yet, so the parser can't iterate over its members for bounds expansion.

This feature is **out of scope** for Sprint 11 Day 2 as it involves:
- Set range expansion (`/p1*p13/` → `['p1', 'p2', ..., 'p13']`)
- Deferred bounds assignment until sets are fully resolved
- Alternative: mock/store approach for bounds with unresolved sets

## Impact

**Aggregation over subset domains** is a critical feature for GAMS optimization models that:
- Use subsets to define sparse aggregation domains
- Employ conditional aggregation (only over valid pairs/tuples)
- Optimize over subset-defined regions

Common patterns enabled:
- `smin(arcs(i,j), cost(i,j))` - minimum over valid arcs
- `sum(active(t), production(t))` - sum over active time periods  
- `smax(feasible(x,y), distance(x,y))` - maximum over feasible points

### Sprint 11 Day 2 Extended Overall Progress

| Phase | Lines | Feature |
|-------|-------|---------|
| Grammar | 37→51 | Subset indexing, option in exec, solvers |
| Domain context | 51→51 | Indexed set assignments |
| Subset expansion | 51→59 | Subset reference expansion |
| **Aggregation** | **59→75** | **Aggregation over subsets** |

**Total:** Line 37 → Line 75 (38 additional lines, **+69% parse rate**)

## Lessons Learned

1. **Domain Specifications vs. Iterators:** Aggregation domains can be either simple iterators (`i`) or subset specifications (`low(n,nn)`)
2. **Scope Extension:** Subset indices must be added to free_domain for the aggregated expression
3. **First Argument Type:** Need to check both `symbol_plain` and `symbol_indexed` for first argument
4. **Backward Compatibility:** New feature integrates without breaking existing simple iterator support

## Conclusion

Successfully implemented aggregation over subset domains, moving the maxmin.gms parse blocker from line 59 → line 75 (16 additional lines, ~69% parse rate). All tests passing with no regressions.

**Status:** Aggregation over subset domains feature complete ✅
