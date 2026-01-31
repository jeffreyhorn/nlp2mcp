# Issue: DollarConditional Not Supported in GAMS Emission

**Status:** Open  
**Created:** 2026-01-31  
**Sprint:** 17  
**Category:** Translation Error  
**Error Code:** `unsup_expression_type`  
**GitHub Issue:** #597 (https://github.com/jeffreyhorn/nlp2mcp/issues/597)

---

## Summary

The `expr_to_gams()` function in `src/emit/expr_to_gams.py` does not handle `DollarConditional` AST nodes, causing translation to fail with "Unknown expression type: DollarConditional" for models that use dollar conditional expressions in equations.

## Affected Models

| Model | Type | Error Location |
|-------|------|----------------|
| chenery | NLP | Equation `mb`, `dvv`, `dl`, `dk` |

## Error Message

```
Error: Invalid model - Unknown expression type: DollarConditional
```

## Reproduction

```bash
cd /Users/jeff/experiments/nlp2mcp
.venv/bin/python src/cli.py data/gamslib/raw/chenery.gms
```

## Root Cause

The `expr_to_gams()` function in `src/emit/expr_to_gams.py` uses pattern matching to convert AST nodes to GAMS syntax. It has cases for `Const`, `VarRef`, `ParamRef`, `SymbolRef`, `Binary`, `Unary`, `Call`, and `Sum`, but **no case for `DollarConditional`**.

When a `DollarConditional` node is encountered, execution falls through to the default case which raises:
```python
raise ValueError(f"Unknown expression type: {type(expr).__name__}")
```

### Code Location

**File:** `src/emit/expr_to_gams.py`  
**Lines:** ~310-311

```python
case _:
    # Fallback for unknown node types
    raise ValueError(f"Unknown expression type: {type(expr).__name__}")
```

## GAMS Dollar Conditional Syntax

In GAMS, the dollar conditional `expr$condition` evaluates to `expr` if `condition` is non-zero (true), otherwise 0.

### Examples from chenery.gms

```gams
* Line 127: Dollar conditional on set membership
mb(i)..  x(i) =g= y(i) + sum(j, aio(i,j)*x(j)) + (e(i) - m(i))$t(i);

* Line 145: Dollar conditional with parameter comparison
dvv(i)$(sig(i) <> 0).. vv(i) =e= (pi*(1 - del(i))/del(i))**(-rho(i)/(1 + rho(i)));

* Line 147: Multiple dollar conditionals in expression
dl(i)..  l(i)*efy(i) =e= ((del(i)/vv(i) + (1 - del(i)))**(1/rho(i)))$(sig(i) <> 0) + 1$(sig(i) = 0);

* Line 149: Similar pattern
dk(i)..  k(i)*efy(i) =e= ((del(i) + (1 - del(i))*vv(i))**(1/rho(i)))$(sig(i) <> 0) + del(i)$(sig(i) = 0);
```

## DollarConditional AST Structure

The `DollarConditional` class is defined in `src/ir/ast.py`:

```python
@dataclass(frozen=True)
class DollarConditional(Expr):
    """Dollar conditional operator: expr$condition

    Evaluates to expr if condition is non-zero (true), otherwise 0.

    Examples:
        x$y            → DollarConditional(value_expr=VarRef('x'), condition=VarRef('y'))
        (e - m)$t      → DollarConditional(value_expr=Binary('-', ...), condition=VarRef('t'))
        s(n)$rn(n)     → DollarConditional(value_expr=VarRef('s', ('n',)), condition=ParamRef('rn', ('n',)))

    Attributes:
        value_expr: Expression to evaluate if condition is true
        condition: Condition expression (evaluates to true if non-zero)
    """
    value_expr: Expr
    condition: Expr
```

## Proposed Fix

Add a case for `DollarConditional` in `expr_to_gams()`:

```python
case DollarConditional(value_expr, condition):
    # Dollar conditional: value_expr$condition
    value_str = expr_to_gams(value_expr)
    condition_str = expr_to_gams(condition)
    # Parenthesize if needed to avoid precedence issues
    if isinstance(value_expr, (Binary, Unary)):
        value_str = f"({value_str})"
    return f"{value_str}${condition_str}"
```

### Import Required

Add `DollarConditional` to the imports at the top of `expr_to_gams.py`:

```python
from src.ir.ast import (
    Binary,
    Call,
    Const,
    DollarConditional,  # Add this
    Expr,
    ParamRef,
    Sum,
    SymbolRef,
    Unary,
    VarRef,
)
```

## Testing

1. Unit test for `expr_to_gams()` with DollarConditional:
```python
def test_dollar_conditional_emission():
    expr = DollarConditional(VarRef("x"), VarRef("y"))
    result = expr_to_gams(expr)
    assert result == "x$y"

def test_dollar_conditional_with_complex_value():
    expr = DollarConditional(
        Binary("-", VarRef("e"), VarRef("m")),
        VarRef("t")
    )
    result = expr_to_gams(expr)
    assert result == "(e - m)$t"
```

2. Integration test with chenery.gms model

## Estimated Effort

1-2 hours

## Notes

- The differentiation module (`src/ad/derivative_rules.py`) already handles `DollarConditional` correctly in `_diff_dollar_conditional()`, so this is purely an emission issue.
- The parser correctly creates `DollarConditional` nodes - only the GAMS emitter is missing support.

## Related Issues

- Previous issue (completed): `docs/issues/completed/parser-dollar-conditional-not-supported.md` - This fixed parsing, but emission was not addressed.
