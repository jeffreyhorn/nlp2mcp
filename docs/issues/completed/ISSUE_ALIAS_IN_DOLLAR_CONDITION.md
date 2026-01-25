# Issue: Alias Not Resolved in Dollar Condition Within Sum

**Status:** Open  
**Category:** Parser Semantic  
**Affected Models:** aircraft  
**Priority:** Medium  
**GitHub Issue:** [#560](https://github.com/jeffreyhorn/nlp2mcp/issues/560)

## Summary

Aliases defined with `Alias (set, alias)` are not being resolved when used inside a dollar condition within a sum expression. The parser reports the alias as an undefined symbol.

## Reproduction

**Model:** `data/gamslib/raw/aircraft.gms`

**Minimal Example:**
```gams
Set h 'demand states' / 1*5 /;
Alias (h, hp);
Parameter gamma(h);
gamma(h) = sum(hp$(ord(hp) >= ord(h)), 1);
```

**Error:**
```
Error: Parse error at line 4, column 18: Undefined symbol 'hp' referenced [context: assignment] [domain: ('h',)]
  gamma(h) = sum(hp$(ord(hp) >= ord(h)), 1);
                       ^

Suggestion: Declare 'hp' as a variable, parameter, or set before using it
```

## Root Cause Analysis

The alias `hp` is correctly registered in `model.aliases`:
```python
{'hp': AliasDef(name='hp', target='h', universe=None)}
```

However, when parsing the dollar condition `$(ord(hp) >= ord(h))` inside the sum, the symbol resolution for `hp` fails because:
1. The sum domain processing adds `hp` to the free domain
2. But inside the dollar condition expression, the symbol resolver doesn't recognize `hp` as a valid set/alias

**Location:** `src/ir/parser.py` in `_expr()` method, specifically the symbol resolution logic for sum domains with dollar conditions.

## Expected Behavior

The alias `hp` should be recognized as equivalent to set `h` and the expression should parse successfully.

## Proposed Fix

In the `_expr()` method when handling sum expressions with dollar conditions:
1. Before processing the dollar condition expression, ensure alias names are added to the valid symbol context
2. Or ensure the alias lookup happens in `_make_symbol()` before raising undefined symbol error

## Test Case

```python
def test_alias_in_sum_dollar_condition():
    """Test alias resolution in dollar condition within sum."""
    text = dedent("""
        Set h / 1*5 /;
        Alias (h, hp);
        Parameter gamma(h);
        gamma(h) = sum(hp$(ord(hp) >= ord(h)), 1);
        """)
    model = parser.parse_model_text(text)
    assert "gamma" in model.params
```

## Related Files

- `src/ir/parser.py`: Symbol resolution in `_expr()` and `_make_symbol()`
- `data/gamslib/raw/aircraft.gms`: Line 62
