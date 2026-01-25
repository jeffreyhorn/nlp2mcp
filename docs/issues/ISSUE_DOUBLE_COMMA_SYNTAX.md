# Issue: Double Comma in Set Data Not Supported

**Status:** Open  
**Category:** Parser Grammar  
**Affected Models:** srcpm  
**Priority:** Low  
**GitHub Issue:** [#565](https://github.com/jeffreyhorn/nlp2mcp/issues/565)

## Summary

GAMS allows double commas in set/parameter data as a form of visual alignment or placeholder. The parser treats double comma as a syntax error.

## Reproduction

**Model:** `data/gamslib/raw/srcpm.gms`

**Minimal Example:**
```gams
Set l / b 'base or low cost',, c 'competitive' /;
```

**Error:**
```
Error: Parse error at line 1, column 27: Unexpected character: ','
  Set l / b 'base or low cost',, c 'competitive' /;
                              ^
```

## Root Cause Analysis

The grammar's `set_members` rule expects elements separated by single commas:

```lark
set_members: set_member ("," set_member)*
```

Double commas (`,,`) are not handled.

**Location:** `src/gams/gams_grammar.lark` in `set_members` rule.

## Expected Behavior

Double commas should be treated as a single separator (or ignored), allowing visual alignment in the source code.

## Proposed Fix

Options:

1. **Preprocessor approach:** Replace `,,` with `,` before parsing
2. **Grammar approach:** Allow optional empty elements:
   ```lark
   set_members: set_member? ("," set_member?)*
   ```
   Then filter out None values in the parser.

The preprocessor approach is simpler and less likely to cause ambiguity.

## Test Case

```python
def test_double_comma_in_set():
    """Test double comma treated as single separator."""
    text = dedent("""
        Set l / a,, b, c /;
        """)
    model = parser.parse_model_text(text)
    assert model.sets["l"].members == ["a", "b", "c"]
```

## Related Files

- `src/gams/gams_grammar.lark`: `set_members` rule
- `src/ir/preprocessor.py`: Potential location for double comma handling
- `data/gamslib/raw/srcpm.gms`: Line 60
