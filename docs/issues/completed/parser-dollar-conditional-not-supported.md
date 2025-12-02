# Parser: Dollar Conditional Operator Not Supported

**GitHub Issue:** #376  
**URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/376  
**Priority:** HIGH  
**Tier 2 Models Blocked:** chenery.gms, water.gms

## Problem

The parser does not support dollar conditional operators `$(expr)`, which are fundamental GAMS syntax for conditional inclusion of terms in equations and assignments.

## Examples from Tier 2 Models

### chenery.gms (line 127)
```gams
mb(i)..  x(i) =g= y(i) + sum(j, aio(i,j)*x(j)) + (e(i) - m(i))$t(i);
                                                                   ^
                                                         Dollar conditional
```

### water.gms (line 87)
```gams
cont(n)..  sum(a(np,n), q(a)) - sum(a(n,np), q(a)) + s(n)$rn(n) =e= node(n,"demand");
                                                            ^
                                                   Dollar conditional
```

## Current Error

```
Error: Parse error at line 127, column 65: Unexpected character: '('
  mb(i)..  x(i) =g= y(i) + sum(j, aio(i,j)*x(j)) + (e(i) - m(i))$t(i);
                                                                    ^

Suggestion: This character is not valid in this context
```

## GAMS Specification

The dollar conditional operator `$` has the syntax:
- **Simple form:** `expr$condition` - includes `expr` only if `condition` is true (non-zero)
- **With parentheses:** `expr$(condition)` - same but with explicit grouping
- **In sums:** `sum(i, expr$condition)` - conditionally include terms in aggregation

### Semantics
- If `condition` evaluates to 0 or false, the entire `expr$condition` evaluates to 0
- If `condition` evaluates to non-zero or true, it evaluates to `expr`
- Commonly used with set membership: `x(i)$active(i)` means "x(i) only if i is active"

### Common Use Cases
1. **Conditional terms in equations:** `cost =e= sum(i, price(i)*x(i)$available(i));`
2. **Conditional inclusion:** `total =e= base + adjustment$apply_adjustment;`
3. **Set filtering:** `balance(i)$important(i).. supply(i) =e= demand(i);`

## Technical Details

### Grammar Changes Needed

The dollar operator needs to be parsed as a binary operator with:
- Left operand: the expression to conditionally include
- Right operand: the condition expression
- Precedence: Lower than arithmetic but higher than relational operators

Possible grammar rule:
```lark
?conditional_expr: arithmetic_expr ("$" arithmetic_expr)?
```

### Parser Changes Needed

1. **Lexer:** Ensure `$` token is recognized in expression context (already exists for other uses)
2. **Grammar:** Add conditional expression production
3. **AST:** Create `DollarConditional` node or similar
4. **IR:** Represent as conditional expression in `Expr` type
5. **Converter:** Convert to appropriate conditional logic (if-else or ternary)

### IR Representation

Could be represented as:
```python
@dataclass
class DollarConditional(Expr):
    """Conditional expression: expr$condition"""
    value_expr: Expr  # Expression to include if condition is true
    condition: Expr   # Condition expression
```

Or using existing conditional construct if available.

## Impact

- **Blocks:** 2 Tier 2 models (chenery.gms, water.gms)
- **Frequency:** Very common GAMS feature, likely to appear in many real-world models
- **Workaround:** None - fundamental language feature

## Recommended Approach

1. Add grammar support for `$` as binary operator in expressions
2. Create IR representation for dollar conditionals
3. Implement semantic validation (condition should be boolean-like)
4. Add converter support to translate to conditional logic
5. Add comprehensive tests for:
   - Simple conditionals: `x$y`
   - Parenthesized conditionals: `x$(y > 0)`
   - Nested conditionals: `(a$b)$c`
   - Conditionals in equations and sums
   - Edge cases: multiple conditionals, complex expressions

## Priority Justification

**HIGH Priority** because:
- Blocks 2 Tier 2 models
- Fundamental GAMS language feature
- Very common in real-world models
- Required for model expressiveness and efficiency

## Related Issues

- Dollar operator is already used for other purposes in GAMS (e.g., macro definitions, set operations)
- Need to ensure proper precedence and associativity
- May interact with existing dollar-prefixed identifiers or directives
