# Parser: Subset Indexing in Parameter Assignments Not Supported

**GitHub Issue**: #426  
**URL**: https://github.com/jeffreyhorn/nlp2mcp/issues/426  
**Priority**: HIGH  
**Complexity**: Medium  
**Estimated Effort**: 2-4 hours  
**Tier 2 Models Blocked**: water.gms

## Summary

GAMS allows using a subset as an index in parameter assignments to set values for only those elements that belong to the subset. The parser currently raises an error when encountering this pattern.

## Current Behavior

When parsing water.gms, the parser fails with:

```
ParserSemanticError: Subset indexing not supported in parameter assignments
```

The error occurs at line 32 of water.gms:
```gams
dn(rn) = no;
```

## Expected Behavior

The parser should recognize subset indexing and expand the assignment to all elements of the subset. For example:

```gams
Set n / a, b, c, d /;
Set sub(n) / a, c /;
Parameter p(n);

p(sub) = 5;  * Should set p('a') = 5 and p('c') = 5
```

## GAMS Subset Indexing Semantics

When a subset is used as an index in an assignment:
1. The assignment applies to all elements that are members of the subset
2. Elements not in the subset are unaffected
3. The subset must be defined over the same domain as the parameter

### Example from water.gms

```gams
Set n      'nodes'
    rn(n)  'reservoir nodes'  / nw, e /
    dn(n)  'demand nodes';

dn(n)  = yes;   * Set all nodes as demand nodes
dn(rn) = no;    * Override: reservoir nodes are NOT demand nodes
display dn;
```

After execution:
- `dn('nw')` = 0 (no) - because 'nw' is in rn
- `dn('e')` = 0 (no) - because 'e' is in rn  
- All other nodes remain 1 (yes)

## Reproduction

### Minimal Test Case

```gams
Set i / a, b, c, d /;
Set sub(i) / b, c /;
Parameter flag(i);

flag(i) = 1;
flag(sub) = 0;

display flag;
* Expected: flag('a')=1, flag('b')=0, flag('c')=0, flag('d')=1
```

### water.gms (lines 28-33)

```gams
Set n      'nodes'
    rn(n)  'reservoirs'  / nw, e /
    dn(n)  'demand nodes';

dn(n)  = yes;
dn(rn) =  no;
display dn;
```

## Root Cause

In `src/ir/parser.py`, the `_extract_indices` function (line 490) explicitly raises an error when it detects subset indexing:

```python
raise ParserSemanticError("Subset indexing not supported in parameter assignments")
```

The `_handle_assign` method calls `_extract_indices` to get the domain context from the assignment target, but the current implementation doesn't handle the case where the index is a subset rather than a simple domain variable.

## Implementation Plan

### Option 1: Expand Subset at Assignment Time (Recommended)

When processing an assignment like `p(sub) = value`:

1. Detect that `sub` is a subset (exists in `model.sets` and has a domain)
2. Get the members of the subset
3. Expand the assignment to individual element assignments

```python
def _handle_assign(self, node: Tree) -> None:
    # ... existing code ...
    
    # Check if index is a subset
    if index_name in self.model.sets:
        subset = self.model.sets[index_name]
        if subset.members:
            # Expand to individual assignments
            for member in subset.members:
                self._apply_param_value(param_name, (member,), value)
            return
    
    # ... rest of existing code ...
```

### Option 2: Store as Expression

Store the subset assignment as an expression that gets evaluated later during model solving. This preserves the original semantics but defers evaluation.

### Recommendation

Option 1 is preferred because:
- Simpler implementation
- Consistent with how other indexed assignments work
- Values are immediately available in the IR

## Testing Requirements

1. Basic subset assignment: `p(sub) = value`
2. Subset with predefined constants: `flag(sub) = yes`
3. Overwriting previous values: `p(i) = 1; p(sub) = 0`
4. Multi-dimensional subsets: `p(sub1, sub2) = value`
5. Nested subsets: subset of a subset
6. Empty subset (edge case)
7. Verify water.gms parses successfully

## Impact

**Models Unlocked**: 1 (water.gms)  
**Parse Rate Improvement**: Enables full parsing of water.gms after predefined constants fix

## Related Issues

- Issue #407: Predefined Constants (yes/no/inf/eps) - FIXED
  - water.gms uses `yes` and `no` in the subset assignments

## References

- **GAMS Documentation**: Set Operations and Subset Assignments
- **Tier 2 Model**: water.gms (Water Distribution Network Design)
- **Source**: `src/ir/parser.py` lines 490, 2409
