# Issue: Curly Brace Expressions Not Supported

**GitHub Issue:** #613
**GitHub URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/613
**Status:** Resolved
**Priority:** Low
**Category:** Parser/Grammar
**Resolution:** Fixed in PR #615 (Sprint 17 Day 8)

## Summary

The parser does not support curly braces `{...}` as an alternative grouping syntax to parentheses `(...)` in arithmetic expressions. GAMS allows curly braces for grouping in certain contexts.

## Resolution

Fixed in PR #615 by adding:
1. `brace_expr` rule to the `atom` production in `src/gams/gams_grammar.lark`
2. Handler for `brace_expr` in `src/ir/parser.py` that unwraps the inner expression

The fix treats `{expr}` identically to `(expr)` for expression grouping.

**Note:** The procmean.gms model now parses past the curly braces but encounters a different error related to the external function `betareg` which is not defined in the model. This is a separate issue unrelated to curly brace support.

## Affected Models

- `procmean.gms` - Uses curly braces in equation expressions

## Error Message

```
Error: Parse error at line 46, column 7: Unexpected character: '{'
  -  k1*{(delta + a)*betareg(y,alpha,beta)
        ^

Suggestion: This character is not valid in this context
```

## Reproduction

### Minimal Example
```gams
Variable x, y;
Equation e;
e.. y =e= x*{1 + x};
```

### From procmean.gms (lines 46-48)
```gams
tcdef.. tc =e= k1*T*betareg(y,alpha,beta)
            -  k1*{(delta + a)*betareg(y,alpha,beta)
                  - (delta + b)*[1 - betareg(y,alpha,beta)]}
            +  k2*{(delta + a)*[1 - betareg(y,alpha,beta)]
                  - (delta + b)*betareg(y,alpha,beta)};
```

## Expected Behavior

The parser should treat `{expr}` the same as `(expr)` for grouping in arithmetic expressions.

## Current Grammar

The current `atom` rule in `src/gams/gams_grammar.lark` supports:
- `"(" expr ")"` - parenthesized expressions
- `"[" expr "]" -> bracket_expr` - square bracket expressions

But does NOT support:
- `"{" expr "}"` - curly brace expressions

## Proposed Fix

Add curly brace alternative to the `atom` rule in the grammar.

### Grammar Change
```lark
?atom: NUMBER                             -> number
     | func_call                          -> funccall
     | sum_expr
     | prod_expr
     | compile_time_const                 -> compile_const
     | ref_bound
     | ref_indexed
     | symbol_plain
     | "(" expr ")"
     | "[" expr "]"                       -> bracket_expr
     | "{" expr "}"                       -> brace_expr    // NEW
```

### Files to Modify
- `src/gams/gams_grammar.lark` - Add `"{" expr "}"` to atom rule
- `src/ir/parser.py` - Add handler for `brace_expr` (similar to `bracket_expr`)

## Test Cases

```python
def test_curly_brace_grouping():
    """Test curly braces for expression grouping."""
    code = """
    Variable x, y;
    Equation e;
    e.. y =e= x*{1 + x};
    Model m / all /;
    """
    model = parse_model_text(code)
    assert "e" in model.equations

def test_nested_curly_and_brackets():
    """Test nested curly braces and brackets."""
    code = """
    Variable x, y;
    Equation e;
    e.. y =e= {(x + 1)*[x - 1]};
    Model m / all /;
    """
    model = parse_model_text(code)
    assert "e" in model.equations
```

## Implementation Notes

- Curly braces are already used in the grammar for `sum` and `prod` expressions: `sum{...}` and `prod{...}`
- Need to ensure the new rule doesn't conflict with existing uses
- The `brace_expr` handler should simply unwrap and process the inner expression, same as `bracket_expr`

## Related Issues

- LEXER_IMPROVEMENT_PLAN.md subcategory 2.6: Curly brace expressions (1 model)

## References

- `docs/planning/EPIC_3/SPRINT_17/LEXER_IMPROVEMENT_PLAN.md` - Section 2.6
- `data/gamslib/raw/procmean.gms` - Example model
