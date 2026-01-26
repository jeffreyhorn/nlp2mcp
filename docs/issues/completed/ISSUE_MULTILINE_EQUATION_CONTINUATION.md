# Issue: Multi-line Equation Continuation Not Supported

**Status:** Resolved  
**Category:** Parser Grammar  
**Affected Models:** agreste, mine, pdi, korcge, nebrazil  
**Priority:** High  
**GitHub Issue:** [#561](https://github.com/jeffreyhorn/nlp2mcp/issues/561)

## Summary

GAMS allows equations to span multiple lines without explicit continuation characters. The parser fails when an equation definition continues on a subsequent line, treating the continuation as a new statement.

## Reproduction

**Model:** `data/gamslib/raw/agreste.gms`

**Minimal Example:**
```gams
Set tm / jan, feb /;
Set r / rec-1 /;
Variable tlab(tm), flab(tm), plab, xliver(r);
Parameter labor(tm), llab(tm,r), dpm;

Equation labc(tm);
labc(tm)..     sum(r, labor(tm)*xliver(r))
            +  sum(r, llab(tm,r)*xliver(r))
           =l= flab(tm) + tlab(tm) + dpm*plab;
```

**Error:**
```
Error: Parse error at line 3, column 1: Unexpected character: '+'
  +  sum(r, llab(tm,r)*xliver(r))
  ^

Suggestion: This character is not valid in this context
```

## Root Cause Analysis

The grammar's `equation_def` rule expects the entire equation on a single logical line:
```lark
equation_def: ID "(" domain_list ")" condition? ".." expr REL_K expr SEMI
```

When the expression spans multiple lines, the parser treats the continuation line starting with `+` as a new statement, which fails because `+` is not a valid statement start.

**Location:** `src/gams/gams_grammar.lark` in `equation_def` rule.

## Expected Behavior

Equations should be able to span multiple lines. The parser should continue parsing the expression until it encounters the relation operator (`=e=`, `=l=`, `=g=`) and then the semicolon.

## Proposed Fix

Options:
1. **Preprocessor approach:** Detect equation definitions (`..`) and merge continuation lines until semicolon
2. **Grammar approach:** Modify how NEWLINE is handled within equation expressions
3. **Lexer approach:** Make the equation body a special context where newlines are ignored

The preprocessor approach is likely safest as it doesn't require grammar changes.

## Test Case

```python
def test_multiline_equation():
    """Test equation spanning multiple lines."""
    text = dedent("""
        Set i / a, b /;
        Variable x(i), y;
        Equation eq;
        eq.. sum(i, x(i))
           + y
           =e= 0;
        """)
    model = parser.parse_model_text(text)
    assert "eq" in model.equations
```

## Affected Models Details

| Model | Line | Context |
|-------|------|---------|
| agreste | 269 | `+ sum(r, llab(tm,r)*xliver(r))` continuation |
| mine | 62 | `pr(k,l+1,i,j)$c(l,i,j)..` equation on new line after previous |
| pdi | 115 | `at..` equation on new line |
| korcge | 346 | `profitmax(i,lc)$wdist(i,lc)..` equation on new line |
| nebrazil | 612 | `pl(p) = sum(...)` assignment on new line |

## Related Files

- `src/gams/gams_grammar.lark`: `equation_def` rule
- `src/ir/preprocessor.py`: Potential location for line continuation handling
