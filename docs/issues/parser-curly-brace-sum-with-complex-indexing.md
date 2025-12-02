# Parser: Curly Brace Sum with Complex Indexing Not Supported

**GitHub Issue:** #379  
**URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/379  
**Priority:** HIGH  
**Tier 2 Models Blocked:** jbearing.gms

## Problem

The parser does not support curly brace `sum{...}` syntax with complex index expressions, particularly nested function calls or arithmetic in the index tuples.

## Example from Tier 2 Model

### jbearing.gms (line 62)
```gams
obj =e= (hx*hy/12)*sum{(nx(i+1),ny(j+1)), (wq[i] + 2*wq[i+1])
                           ^
                    Complex indexing: nx(i+1), ny(j+1)
```

The sum iterates over tuples `(nx(i+1), ny(j+1))` where:
- `nx` and `ny` are sets or mappings
- `i+1` and `j+1` are arithmetic expressions
- The result is a tuple of set elements

## Current Error

```
Error: Parse error at line 62, column 24: Unexpected character: '('
  obj =e= (hx*hy/12)*sum{(nx(i+1),ny(j+1)), (wq[i] + 2*wq[i+1])
                           ^

Suggestion: This character is not valid in this context
```

## GAMS Specification

GAMS supports curly braces `{...}` as an alternative to parentheses `(...)` for sum expressions:

### Basic Syntax
```gams
sum(i, expr)   # Parentheses syntax
sum{i, expr}   # Curly brace syntax (equivalent)
```

### Complex Indexing
```gams
sum{(i,j), expr}              # Tuple iteration
sum{(nx(i),ny(j)), expr}      # Set-based tuples
sum{(nx(i+1),ny(j+1)), expr}  # Tuples with arithmetic in indices
```

The curly brace syntax is often used for:
- Stylistic preference
- Clarity when nesting multiple sums
- Certain modeling patterns

### Semantics of Complex Indexing

`sum{(nx(i+1),ny(j+1)), expr}` means:
- For each value of `i` and `j`
- Look up `nx(i+1)` and `ny(j+1)` (using shifted indices)
- Iterate over the resulting tuple pairs
- Evaluate and sum the expression

This is advanced indexing that involves:
1. Arithmetic on indices (`i+1`, `j+1`)
2. Set element lookup (`nx(...)`, `ny(...)`)
3. Tuple formation
4. Iteration over the cartesian product

## Current Parser Status

The parser currently supports:
- Basic `sum(i, expr)` with parentheses
- Simple `sum{i, expr}` with curly braces (based on previous work)
- Basic tuple iteration `sum((i,j), expr)`

But does NOT support:
- Complex expressions in tuple indices: `sum{(nx(i+1),ny(j+1)), expr}`
- Nested function calls in index expressions
- Arithmetic in index expressions within tuples

## Technical Details

### Grammar Changes Needed

Current grammar likely has:
```lark
sum_expr: "sum" "(" domain "," expr ")"
        | "sum" "{" domain "," expr "}"
domain: ID | "(" id_list ")"
```

Needed grammar:
```lark
sum_expr: "sum" "(" domain "," expr ")"
        | "sum" "{" domain "," expr "}"
domain: ID 
      | "(" id_list ")"
      | "(" index_expr_list ")"  # Add complex indexing

index_expr_list: index_expr ("," index_expr)*
index_expr: ID | function_call | arithmetic_expr
```

### Parser Changes Needed

1. **Grammar:** Extend `domain` to accept complex index expressions
2. **Parser:** Handle index expressions that are not just identifiers
3. **IR:** Represent complex indexing in domain specification
4. **Semantic analysis:** Validate that index expressions are valid
5. **Converter:** Generate appropriate iteration logic

### Challenges

1. **Index arithmetic:** `i+1` needs to be evaluated in the context of set iteration
2. **Set lookup:** `nx(i+1)` performs a lookup into set/mapping `nx` with computed index
3. **Domain validation:** Ensure the resulting tuples are valid for the expression domain
4. **Nested evaluation:** May need to support `nx(ny(i))` style nested lookups

### Possible IR Representation

```python
@dataclass
class ComplexDomain:
    """Domain with complex index expressions"""
    index_exprs: list[Expr]  # Can be ID, FunctionCall, BinaryOp, etc.
```

Or extend existing domain representation to handle expressions beyond simple identifiers.

## Impact

- **Blocks:** 1 Tier 2 model (jbearing.gms)
- **Frequency:** Advanced modeling pattern, less common but used in sophisticated models
- **Workaround:** Difficult - requires model restructuring

## Related Work

- Issue #232 (or similar): Basic curly brace sum support was added previously
- This is an extension to handle more complex indexing patterns
- Similar patterns may appear in product operations: `prod{(nx(i+1)), expr}`

## Test Cases Needed

1. **Simple curly brace:** `sum{i, x(i)}`
2. **Tuple with curly braces:** `sum{(i,j), x(i,j)}`
3. **Set lookup in index:** `sum{(nx(i),ny(j)), expr}`
4. **Arithmetic in index:** `sum{(nx(i+1)), expr}`
5. **Combined:** `sum{(nx(i+1),ny(j-1)), expr}`
6. **Nested:** `sum{(nx(ny(i))), expr}`
7. **With conditionals:** `sum{(nx(i)$active(i)), expr}`

## Priority Justification

**HIGH Priority** because:
- Blocks 1 Tier 2 model
- Extension of existing curly brace sum feature
- Demonstrates advanced GAMS capabilities
- Important for sophisticated engineering models

## Implementation Notes

### Potential Approaches

**Option 1: Extend domain grammar to accept expressions**
- Most flexible
- May complicate domain handling throughout the codebase

**Option 2: Pre-process complex domains into simpler form**
- Convert `sum{(nx(i+1)), expr}` to equivalent nested structure
- May be easier to implement but less elegant

**Option 3: Special handling for set lookups**
- Recognize pattern of `set_name(index_expr)` specifically
- More limited but may be sufficient for common cases

### Recommended Approach

Start with Option 3 for the specific pattern seen in jbearing.gms:
- Recognize `ID(expr)` pattern as set element lookup
- Allow arithmetic expressions inside the lookup
- Extend to more general cases as needed

## Related Issues

- Curly brace sum basic support (previously implemented)
- Set element lookup and indexing
- Arithmetic expressions in domain contexts
- May relate to indexed set operations

## Example Workaround (for reference)

If the model could be rewritten (not ideal):
```gams
* Instead of:
sum{(nx(i+1),ny(j+1)), expr}

* Could potentially use:
sum((i,j)$(ord(i) < card(i) and ord(j) < card(j)), 
    expr_with_explicit_lookups)
```

But this is complex and may not be semantically equivalent.
