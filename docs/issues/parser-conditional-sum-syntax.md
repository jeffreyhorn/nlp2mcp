# Parser: Conditional Sum Syntax Not Supported

**GitHub Issue**: #412  
**URL**: https://github.com/jeffreyhorn/nlp2mcp/issues/412  
**Priority**: MEDIUM  
**Complexity**: Medium  
**Estimated Effort**: 2-3 hours  
**Tier 2 Models Blocked**: pool.gms (partially)

## Summary

GAMS supports conditional indexing in sum expressions using the `$` operator, allowing filtering of summation domains based on conditions. The parser currently does not support this syntax, causing parse errors when models use conditional sums.

## Current Behavior

When parsing pool.gms (line 685), the parser fails with:

```
Error: Parse error at line 795, column 1: Unexpected character: 'p'
  pool(pool_) = PoolSize(case,pool_);
  ^
```

The actual issue is on the previous line (685):
```gams
qual(qual_) = sum(comp_$ComponentQuality(case,comp_,qual_), 1);
```

The parser cannot handle `comp_$ComponentQuality(...)` in the sum domain.

## Expected Behavior

The parser should accept conditional indexing in sum domains:
- `sum(i$condition(i), expr)` - sum over i where condition is nonzero
- `sum(i$param(i), x(i))` - sum over i where param(i) is nonzero

## Examples

### Basic Conditional Sum
```gams
Set i / 1*5 /;
Parameter active(i) / 1 1, 2 0, 3 1, 4 0, 5 1 /;
Variable x(i);

* Sum only over active elements
Equation total;
total.. sum(i$active(i), x(i)) =e= 100;
```

### Multi-dimensional Conditional
```gams
Set i, j;
Parameter allowed(i,j);

* Sum over (i,j) pairs where allowed is nonzero
Equation constraint;
constraint.. sum((i,j)$allowed(i,j), x(i,j)) =l= capacity;
```

### Complex Condition
```gams
* Conditional can be any expression
Equation filtered;
filtered.. sum(i$(ord(i) > 2 and ord(i) < 8), x(i)) =e= target;
```

## GAMS Specification

The `$` operator in GAMS provides conditional execution/filtering:

**In sum expressions:**
```gams
sum(index$condition, expression)
```

This means: "sum expression over index where condition is true (nonzero)"

The condition can be:
- A parameter reference: `p(i)`
- A set membership test: `active(i)`
- A logical expression: `ord(i) > 5`
- Any expression evaluating to numeric (0 = false, nonzero = true)

## Reproduction

### Test File: pool.gms (line 685)
```gams
Set comp_ Components and Raw Materials
    qual_ Qualities;
Set comp(comp_) Instance of Components
    qual(qual_) Instance of Qualities;
Parameter ComponentQuality(comp_,qual_);

* This fails to parse:
qual(qual_) = sum(comp_$ComponentQuality(comp_,qual_), 1);
```

### Minimal Test Case
```gams
Set i / 1*5 /;
Parameter p(i) / 1 10, 2 20, 3 30 /;
Variable x(i);
Equation test;

* Should parse but currently fails:
test.. sum(i$p(i), x(i)) =e= 100;

Model m / all /;
```

## Implementation Plan

### Grammar Changes (src/gams/gams_grammar.lark)

Current sum domain syntax:
```lark
sum_expr: SUM_K "(" sum_domain "," expr ")"   -> sum
        | SUM_K "{" sum_domain "," expr "}"   -> sum

sum_domain: index_list
          | "(" index_list ")"  -> tuple_domain
```

Updated to support conditional:
```lark
sum_domain: conditional_index_list
          | index_list
          | "(" conditional_index_list ")"  -> tuple_domain_cond
          | "(" index_list ")"              -> tuple_domain

conditional_index_list: index_list DOLLAR expr
```

Alternative (cleaner):
```lark
sum_domain: index_spec
          | "(" index_spec ")"  -> tuple_domain

index_spec: index_list (DOLLAR expr)?
```

### Parser/IR Changes

Need to decide how to represent conditional sums in the IR:

**Option 1**: Extend Sum node
```python
@dataclass(frozen=True)
class Sum(Expr):
    indices: tuple[str, ...]
    body: Expr
    condition: Expr | None = None  # New field
```

**Option 2**: Transform to equivalent form
```gams
sum(i$cond(i), x(i))
```
Could be transformed to:
```gams
sum(i, cond(i) * x(i))
```

Option 2 is simpler but less semantically accurate.

### Testing Requirements

1. Simple conditional: `sum(i$p(i), x(i))`
2. Multi-dimensional: `sum((i,j)$p(i,j), x(i,j))`
3. Complex condition: `sum(i$(ord(i) > 2), x(i))`
4. Nested sums with conditionals
5. Conditional in equation domain vs sum domain
6. Verify pool.gms line 685 parses

## Impact

**Models Unlocked**: Partial progress on pool.gms  
**Parse Rate Improvement**: TBD (pool.gms would still need additional features)

This feature is common in GAMS models for filtering summations based on data-driven conditions.

## Related Issues

- Issue #409: Infrastructure fix for pool.gms (completed)
- This blocks full parsing of pool.gms but is a separate parser feature

## References

- **GAMS Documentation**: Dollar Control Options and Conditional Expressions
- **Tier 2 Model**: pool.gms (Gas Transmission Problem)
- **GAMS User's Guide**: Section on Conditional Indexing and the $ Operator
- **Related Syntax**: The $ operator is also used for conditional equations, which is already supported

## Notes

- The $ operator has multiple uses in GAMS:
  - Conditional indexing (this issue): `sum(i$condition, ...)`
  - Conditional equations (already supported): `equation$(condition)..`
  - Dollar control directives (already ignored): `$include`, `$set`, etc.
- This implementation should not interfere with existing $ operator handling
- The grammar already has DOLLAR token with high priority (line 421 in grammar)
