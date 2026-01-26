# Issue: Assignment to Complex Indexed Expression Not Supported

**Status:** Resolved  
**Category:** Parser Grammar  
**Affected Models:** airsp  
**Priority:** Medium  
**GitHub Issue:** [#566](https://github.com/jeffreyhorn/nlp2mcp/issues/566)

## Summary

GAMS allows assignments to indexed expressions with quoted string indices like `drand('route-1',s)`. The parser fails when the assignment target contains quoted strings in the index.

## Reproduction

**Model:** `data/gamslib/raw/airsp.gms`

**Minimal Example:**
```gams
Set j / route-1 /;
Set s / s1 /;
Parameter dd(j,s), drand(j,s);

drand('route-1',s) = dd('route-1',s);
```

**Error:**
```
Error: Parse error at line 5, column 20: Unexpected character: '='
  drand('route-1',s) = dd('route-1',s);
                     ^
```

## Root Cause Analysis

The grammar's `lvalue` rule uses `ref_indexed` which expects ID tokens for indices:

```lark
lvalue: ref_bound | ref_indexed | ID

ref_indexed.2: ID "(" index_list ")"
             | ID "[" index_list "]"

index_list: index_expr ("," index_expr)*
index_expr: ID "(" index_list ")" lag_lead_suffix?
          | ID "[" index_list "]" lag_lead_suffix?
          | ID lag_lead_suffix?
```

The `index_expr` rule only accepts `ID` tokens, not STRING tokens (quoted strings).

**Location:** `src/gams/gams_grammar.lark` in `index_expr` rule.

## Expected Behavior

Assignment targets should accept quoted string indices: `param('quoted-id', set_index) = value;`

## Proposed Fix

Extend `index_expr` to accept STRING tokens:

```lark
index_expr: ID "(" index_list ")" lag_lead_suffix?
          | ID "[" index_list "]" lag_lead_suffix?
          | ID lag_lead_suffix?
          | STRING lag_lead_suffix?  // Add support for quoted indices
```

This is consistent with how we handle quoted indices in data blocks.

## Test Case

```python
def test_quoted_index_in_assignment():
    """Test assignment with quoted string index."""
    text = dedent("""
        Set j / route-1 /;
        Set s / s1 /;
        Parameter dd(j,s) / 'route-1'.s1 10 /;
        Parameter drand(j,s);
        drand('route-1',s) = dd('route-1',s);
        """)
    model = parser.parse_model_text(text)
    assert "drand" in model.params
```

## Related Files

- `src/gams/gams_grammar.lark`: `index_expr`, `lvalue`, `ref_indexed`
- `src/ir/parser.py`: Index extraction in assignments
- `data/gamslib/raw/airsp.gms`: Line 153
