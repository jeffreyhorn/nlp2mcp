# Issue: Quoted String in Tuple Dot Notation Not Supported

**Status:** Resolved  
**Category:** Parser Grammar  
**Affected Models:** egypt  
**Priority:** Medium  
**GitHub Issue:** [#567](https://github.com/jeffreyhorn/nlp2mcp/issues/567)

## Summary

GAMS allows quoted strings in tuple dot notation for set mappings, like `upper.'u-egypt'`. The parser fails because the grammar expects an unquoted identifier after the dot.

## Reproduction

**Model:** `data/gamslib/raw/egypt.gms`

**Minimal Example:**
```gams
Set z / upper, middle, lower /;
Set r / u-egypt, m-egypt, l-egypt /;
Set zr(z,r) 'map from zones to regions'
    / upper.'u-egypt', middle.'m-egypt', lower.'l-egypt' /;
```

**Error:**
```
Error: Parse error at line 4, column 13: Unexpected character: '''
  / upper.'u-egypt', middle.'m-egypt', lower.'l-egypt' /;
            ^
```

## Root Cause Analysis

The grammar's `set_tuple` rule only accepts `SET_ELEMENT_ID` after the dot:

```lark
?set_member: ...
           | SET_ELEMENT_ID "." SET_ELEMENT_ID STRING -> set_tuple_with_desc
           | SET_ELEMENT_ID "." SET_ELEMENT_ID   -> set_tuple
           ...
```

It doesn't handle `SET_ELEMENT_ID "." STRING` (quoted suffix).

**Location:** `src/gams/gams_grammar.lark` in `set_member` alternatives.

## Expected Behavior

Set tuples should accept quoted strings after the dot: `upper.'u-egypt'` should create tuple `upper.u-egypt`.

## Proposed Fix

Add new alternatives to `set_member`:

```lark
?set_member: ...
           | SET_ELEMENT_ID "." STRING STRING    -> set_tuple_with_desc  // prefix.quoted_suffix 'desc'
           | SET_ELEMENT_ID "." STRING           -> set_tuple            // prefix.quoted_suffix
           | STRING "." SET_ELEMENT_ID           -> set_tuple            // 'quoted_prefix'.suffix
           | STRING "." STRING                   -> set_tuple            // 'quoted_prefix'.'quoted_suffix'
           ...
```

And update the parser's `_expand_set_members()` to strip quotes from STRING tokens.

## Test Case

```python
def test_quoted_string_in_tuple():
    """Test quoted string as tuple suffix."""
    text = dedent("""
        Set z / upper, lower /;
        Set r / u-egypt, l-egypt /;
        Set zr(z,r) / upper.'u-egypt', lower.'l-egypt' /;
        """)
    model = parser.parse_model_text(text)
    assert model.sets["zr"].members == ["upper.u-egypt", "lower.l-egypt"]
```

## Related Files

- `src/gams/gams_grammar.lark`: `set_member` alternatives for `set_tuple`
- `src/ir/parser.py`: `_expand_set_members()` method
- `data/gamslib/raw/egypt.gms`: Line 32
