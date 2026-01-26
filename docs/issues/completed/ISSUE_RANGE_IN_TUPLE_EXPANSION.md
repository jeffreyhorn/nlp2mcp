# Issue: Range Expression in Tuple Expansion Not Supported

**Status:** Resolved  
**Category:** Parser Grammar  
**Affected Models:** pinene  
**Priority:** Low  
**GitHub Issue:** [#563](https://github.com/jeffreyhorn/nlp2mcp/issues/563)

## Summary

GAMS allows range expressions inside tuple expansion parentheses, like `(ne2*ne5) 0`. The current tuple expansion grammar only accepts comma-separated element IDs, not range expressions.

## Reproduction

**Model:** `data/gamslib/raw/pinene.gms`

**Minimal Example:**
```gams
Set ne / ne1*ne5 /;
Parameter bc(ne) 'ODE initial conditions' / ne1 100, (ne2*ne5) 0 /;
```

**Error:**
```
Error: Parse error at line 2, column 48: Unexpected character: '*'
  bc(ne) 'ODE initial conditions' / ne1 100, (ne2*ne5) 0 /
                                                   ^
```

## Root Cause Analysis

The `set_element_id_list` rule in tuple expansion only accepts individual element IDs:

```lark
set_element_id_list: set_element_id_or_string ("," set_element_id_or_string)*
set_element_id_or_string: SET_ELEMENT_ID | STRING
```

It doesn't support range expressions like `ne2*ne5`.

**Location:** `src/gams/gams_grammar.lark` in `set_element_id_list` and `param_data_tuple_expansion` rules.

## Expected Behavior

Tuple expansion should support ranges: `(ne2*ne5) 0` should expand to `ne2 0, ne3 0, ne4 0, ne5 0`.

## Proposed Fix

1. Create a new rule that accepts either individual elements or ranges:

```lark
tuple_expansion_element: range_expr | SET_ELEMENT_ID | STRING
tuple_expansion_list: tuple_expansion_element ("," tuple_expansion_element)*
```

2. Update `param_data_tuple_expansion` to use the new rule:

```lark
param_data_item: ...
               | "(" tuple_expansion_list ")" NUMBER -> param_data_tuple_expansion
               ...
```

3. Update `_parse_param_data_items()` to expand ranges within tuples.

## Test Case

```python
def test_range_in_tuple_expansion():
    """Test range expression inside tuple expansion."""
    text = dedent("""
        Set ne / ne1*ne5 /;
        Parameter bc(ne) / ne1 100, (ne2*ne5) 0 /;
        """)
    model = parser.parse_model_text(text)
    assert model.params["bc"].values[("ne1",)] == 100.0
    assert model.params["bc"].values[("ne2",)] == 0.0
    assert model.params["bc"].values[("ne5",)] == 0.0
```

## Related Files

- `src/gams/gams_grammar.lark`: `set_element_id_list`, `param_data_tuple_expansion`
- `src/ir/parser.py`: `_parse_param_data_items()`, `_parse_set_element_id_list()`
- `data/gamslib/raw/pinene.gms`: Line 51
