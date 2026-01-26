# Issue: NA Special Value in Tuple Expansion Not Supported

**Status:** Resolved  
**Category:** Parser Grammar  
**Affected Models:** qsambal  
**Priority:** Low  
**GitHub Issue:** [#564](https://github.com/jeffreyhorn/nlp2mcp/issues/564)

## Summary

GAMS allows special values like `na` (not available), `inf`, `eps` in parameter data. When used with tuple expansion, the parser fails because it expects a NUMBER token after the tuple.

## Reproduction

**Model:** `data/gamslib/raw/qsambal.gms`

**Minimal Example:**
```gams
Set i / lab, h1, h2, p1, p2 /;
Parameter tb(i) 'original totals' / lab 220, (h1,h2) na, p1 190, p2 105 /;
```

**Error:**
```
Error: Parse error at line 2, column 43: Unexpected character: 'n'
  tb(i) 'original totals' / lab 220, (h1,h2) na, p1 190, p2 105 /
                                              ^
```

## Root Cause Analysis

The `param_data_tuple_expansion` rule requires a NUMBER after the tuple:

```lark
param_data_item: ...
               | "(" set_element_id_list ")" NUMBER -> param_data_tuple_expansion
               ...
```

Special values like `na`, `inf`, `eps`, `-inf` are identifiers (ID tokens), not NUMBER tokens.

**Location:** `src/gams/gams_grammar.lark` in `param_data_tuple_expansion` rule.

## Expected Behavior

Tuple expansion should accept special values: `(h1,h2) na` should expand to `h1 na, h2 na` (both set to NA).

## Proposed Fix

1. Create a rule for parameter values that includes special values:

```lark
param_value: NUMBER | SPECIAL_VALUE
SPECIAL_VALUE: /(?i:na|inf|eps|undf)\b/
```

2. Update `param_data_tuple_expansion`:

```lark
param_data_item: ...
               | "(" set_element_id_list ")" param_value -> param_data_tuple_expansion
               ...
```

3. Update parser to handle special values (convert `na` to NaN, `inf` to infinity, etc.).

## Test Case

```python
def test_na_in_tuple_expansion():
    """Test NA special value in tuple expansion."""
    text = dedent("""
        Set i / a, b, c /;
        Parameter p(i) / a 1, (b,c) na /;
        """)
    model = parser.parse_model_text(text)
    assert model.params["p"].values[("a",)] == 1.0
    assert math.isnan(model.params["p"].values[("b",)])
    assert math.isnan(model.params["p"].values[("c",)])
```

## Related Files

- `src/gams/gams_grammar.lark`: `param_data_tuple_expansion`
- `src/ir/parser.py`: `_parse_param_data_items()`
- `data/gamslib/raw/qsambal.gms`: Line 32
