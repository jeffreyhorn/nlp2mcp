# Issue: Hyphenated Identifier as Tuple Prefix Not Supported

**Status:** Resolved  
**Category:** Parser Grammar  
**Affected Models:** fawley  
**Priority:** Medium  
**GitHub Issue:** [#568](https://github.com/jeffreyhorn/nlp2mcp/issues/568)

## Summary

GAMS allows hyphenated identifiers as tuple prefixes, like `c-cracker.(ho-low-s,ho-high-s)`. The parser fails to recognize the hyphenated prefix in this context.

## Reproduction

**Model:** `data/gamslib/raw/fawley.gms`

**Minimal Example:**
```gams
Set c / c-cracker /;
Set o / ho-low-s, ho-high-s, vd-low-s, vd-high-s /;
Set co(c,o) / c-cracker.(ho-low-s,ho-high-s,vd-low-s,vd-high-s) /;
```

**Error:**
```
Error: Parse error at line 3, column 14: Unexpected character: '-'
  c-cracker.(ho-low-s,ho-high-s,vd-low-s,vd-high-s)   /
               ^
```

## Root Cause Analysis

The issue is complex. After preprocessing, hyphenated identifiers are quoted:
```
'c-cracker'.('ho-low-s','ho-high-s','vd-low-s','vd-high-s')
```

The grammar's `set_tuple_expansion` rule expects:
```lark
SET_ELEMENT_ID "." "(" id_list ")"
```

But after preprocessing:
1. `c-cracker` becomes `'c-cracker'` (STRING, not SET_ELEMENT_ID)
2. Inside the parentheses, we have quoted strings

**Location:** `src/gams/gams_grammar.lark` in `set_tuple_expansion` rule.

## Expected Behavior

Tuple expansion should work with hyphenated (quoted) prefixes and suffixes.

## Proposed Fix

Extend the `set_tuple_expansion` rule to accept STRING tokens:

```lark
?set_member: ...
           | SET_ELEMENT_ID "." "(" id_list ")"      -> set_tuple_expansion
           | STRING "." "(" set_element_id_list ")"  -> set_tuple_expansion  // quoted prefix
           ...
```

Also need to handle the case where elements inside the parentheses are quoted.

## Test Case

```python
def test_hyphenated_tuple_expansion():
    """Test hyphenated identifier as tuple prefix."""
    text = dedent("""
        Set c / c-cracker /;
        Set o / ho-low-s, ho-high-s /;
        Set co(c,o) / c-cracker.(ho-low-s,ho-high-s) /;
        """)
    model = parser.parse_model_text(text)
    assert model.sets["co"].members == ["c-cracker.ho-low-s", "c-cracker.ho-high-s"]
```

## Related Files

- `src/gams/gams_grammar.lark`: `set_tuple_expansion` rule
- `src/ir/parser.py`: `_expand_set_members()` method
- `src/ir/preprocessor.py`: Hyphenated identifier quoting
- `data/gamslib/raw/fawley.gms`: Line 60
