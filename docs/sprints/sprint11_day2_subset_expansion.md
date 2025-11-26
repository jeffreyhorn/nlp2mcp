# Sprint 11 Day 2: Subset Reference Expansion

**Date:** 2025-11-26  
**Goal:** Resolve line 51 blocker by implementing subset reference expansion  
**Status:** ✅ Complete - Line 51→59, parsing 55% of maxmin.gms!

## Overview

After resolving the line 37 blocker (indexed set assignments with domain context), we tackled line 51 which required **subset reference expansion**. When a multi-dimensional set is used as an index (e.g., `dist(low)` where `low` is defined as `low(n,n)`), it should expand to its underlying domain indices.

## Problem Statement

Line 51 of maxmin.gms:
```gams
defdist(low(n,nn)).. dist(low) =e= sqrt(sum(d, sqr(point(n,d) - point(nn,d))));
```

The issue: `dist(low)` where:
- `dist` is declared as `dist(n,n)` - expects 2 indices
- `low` is a set defined as `low(n,n)` - represents pairs
- When used as `dist(low)`, should expand to `dist(n,n)`

**Error:** "Variable 'dist' expects 2 indices but received 1"

## Solution

Implemented automatic subset expansion in `_make_symbol()` method that:

1. **Checks each index** to see if it's a set reference
2. **Expands multi-dimensional sets** whose members are other sets (domain indices)
3. **Preserves regular sets** with element values (like `d` with members `['x', 'y']`)
4. **Respects domain context** - doesn't expand sets already in the free domain

### Key Logic

```python
# Sprint 11 Day 2 Extended: Expand set references in indices
# When we see dist(low) where low is a 2D set, expand to dist(n,nn)

expanded_indices = []
for idx in indices:
    if isinstance(idx, str) and idx in self.model.sets:
        set_def = self.model.sets[idx]
        
        # Check if this set's members are domain indices (other sets) or element values
        # E.g., low(n,n) has members ['n', 'n'] - domain indices (should expand)
        # E.g., d has members ['x', 'y'] - element values (should NOT expand)
        members_are_sets = set_def.members and all(
            m in self.model.sets for m in set_def.members
        )
        
        # Check if this is a multi-dimensional set reference with set-based domain
        if members_are_sets and len(set_def.members) > 1:
            # Multi-dimensional set with domain indices - always expand
            # E.g., low(n,n) expands to (n, n)
            expanded_indices.extend(set_def.members)
        elif idx in free_domain:
            # Set that's in domain - don't expand
            # E.g., n in point(n,d) where domain is (n,nn)
            expanded_indices.append(idx)
        else:
            # Set with element values or single-dim not in domain - don't expand
            expanded_indices.append(idx)
    else:
        # Not a set reference, keep as-is
        expanded_indices.append(idx)
```

## Examples

### Example 1: Subset Expansion
```gams
Set n, low(n,n);
Variable dist(n,n);
Equation test(low(n,nn));

test(low(n,nn)).. dist(low) =e= 0;  // dist(low) expands to dist(n,n) ✓
```

### Example 2: Element-Based Sets (No Expansion)
```gams
Set d /x, y/;
Variable point(n,d);

point(n,d)  // d has element values, not expanded ✓
```

### Example 3: Domain Variables (No Expansion)
```gams
Equation test(n,nn);

test(n,nn).. point(n,d) =e= 0;  // n is in domain, not expanded ✓
```

## Technical Details

### Distinguishing Set Types

The key insight is that sets can have two types of members:

1. **Domain indices** (references to other sets):
   - `low(n,n)` has members `['n', 'n']`
   - Used for defining subset domains
   - **Should expand** when used as indices

2. **Element values** (literal elements):
   - `d` has members `['x', 'y']`
   - Used for indexing over concrete values
   - **Should NOT expand** when used as indices

The check: `all(m in self.model.sets for m in set_def.members)`

### Preventing Over-Expansion

Three safeguards prevent incorrect expansion:

1. **Multi-dimensional check**: Only expand if `len(members) > 1`
2. **Domain context check**: Don't expand if `idx in free_domain`
3. **Set-based members check**: Only expand if members are other sets

## Results

### Parse Progress

| Blocker | Line | Description |
|---------|------|-------------|
| Before fix | 51 | `dist(low)` - subset expansion needed |
| After fix | 59 | `smin(low(n,nn), ...)` - aggregation over subsets |

**Progress:** 8 additional lines parsed (line 51→59)

**Parse rate:** ~55% of maxmin.gms (59 of 108 lines)

### Test Results

✅ All 1600 tests passing  
✅ No regressions introduced  
✅ maxmin progress tests updated and passing  

## Files Modified

- `src/ir/parser.py:1985-2022` - Added subset expansion logic in `_make_symbol()`
- `tests/integration/test_maxmin_full_parse.py` - Updated expectations to line 59
- `tests/integration/test_maxmin_nested_indexing.py` - Updated expectations to line 59

## Remaining Blocker

**Line 59:** `smin(low(n,nn), sqrt(...))`

This requires support for **aggregation over subset domains**, where the subset `low(n,nn)` is used as the aggregation domain in `smin`. This is a more advanced feature requiring:
- Parsing subset specifications in aggregation functions
- Understanding subset membership in aggregation context
- Proper domain handling for subset-based aggregation

This feature is **out of scope** for Sprint 11 Day 2.

## Impact

**Subset expansion** is a critical feature for GAMS models that:
- Use subsets to define sparse variable/equation indices
- Reference subsets as shorthand for their underlying domains
- Employ common patterns like `dist(low)` for subset-indexed variables

This implementation enables a whole class of GAMS patterns commonly used in optimization models for:
- Network flow problems (subset of arcs)
- Sparse matrices (subset of valid index pairs)
- Conditional variable definitions (subset of active indices)

## Lessons Learned

1. **Set Membership Types:** Sets can have either domain indices or element values as members
2. **Context Matters:** Must check free_domain to avoid expanding domain variables
3. **Multi-dimensional Detection:** Only multi-dimensional sets need expansion
4. **Incremental Progress:** Each fix reveals the next blocker systematically

## Conclusion

Successfully implemented subset reference expansion, moving the maxmin.gms parse blocker from line 51 → line 59 (8 additional lines, ~55% parse rate). All tests passing with no regressions.

**Status:** Subset expansion feature complete ✅
