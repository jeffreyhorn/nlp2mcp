# Issue: Tuple Expansion in Set Definition Not Supported

**Status:** Resolved  
**Category:** Parser Grammar  
**Affected Models:** clearlak, turkey  
**Priority:** Medium  
**GitHub Issue:** [#562](https://github.com/jeffreyhorn/nlp2mcp/issues/562)

## Summary

GAMS allows tuple expansion syntax in set definitions like `(a,b).c` which expands to `a.c, b.c`. The current grammar only supports tuple expansion in parameter data blocks, not in set member definitions.

## Reproduction

**Model:** `data/gamslib/raw/clearlak.gms`

**Minimal Example (clearlak):**
```gams
Set w / wet, dry /;
Set t / jan, feb, mar /;
Set tw(t,w) 'relates months to weather conditions'
    / (jan,feb).wet, mar.dry /;
```

**Error:**
```
Error: Parse error at line 4, column 7: Unexpected character: '('
  / (jan,feb).wet, mar.dry /;
      ^
```

**Model:** `data/gamslib/raw/turkey.gms`

**Minimal Example (turkey):**
```gams
Set lq / irr-good, irr-poor, dry-good, dry-poor /;
Set sq / irrigated, dry /;
Set lsq(lq,sq) / ('irr-good','irr-poor').irrigated, ('dry-good','dry-poor').dry /;
```

**Error:**
```
Error: Parse error at line 3, column 14: Unexpected character: '('
  /('irr-good','irr-poor').irrigated, ...
   ^
```

## Root Cause Analysis

The grammar has `set_tuple_expansion` but only for the pattern `SET_ELEMENT_ID "." "(" id_list ")"` (e.g., `nw.(w,cc,n)`), not for `"(" id_list ")" "." ID` (e.g., `(jan,feb).wet`).

**Current grammar:**
```lark
?set_member: ...
           | SET_ELEMENT_ID "." "(" id_list ")"  -> set_tuple_expansion
           ...
```

**Missing pattern:** `"(" id_list ")" "." SET_ELEMENT_ID`

**Location:** `src/gams/gams_grammar.lark` in `set_member` rule.

## Expected Behavior

Both tuple expansion patterns should be supported:
- `prefix.(a,b)` → `prefix.a, prefix.b` (currently supported)
- `(a,b).suffix` → `a.suffix, b.suffix` (not supported)

## Proposed Fix

Add new grammar rule for prefix tuple expansion:

```lark
?set_member: ...
           | "(" set_element_id_list ")" "." SET_ELEMENT_ID  -> set_tuple_prefix_expansion
           | SET_ELEMENT_ID "." "(" id_list ")"              -> set_tuple_expansion
           ...
```

And update the parser's `_expand_set_members()` to handle `set_tuple_prefix_expansion`:

```python
elif child.data == "set_tuple_prefix_expansion":
    # Tuple prefix expansion: (id1,id2).suffix (e.g., (jan,feb).wet)
    # Expands to: jan.wet, feb.wet
    prefixes = self._parse_set_element_id_list(child.children[0])
    suffix = _token_text(child.children[1])
    for prefix in prefixes:
        result.append(f"{prefix}.{suffix}")
```

## Test Case

```python
def test_set_tuple_prefix_expansion():
    """Test tuple expansion with prefix: (a,b).c -> a.c, b.c."""
    text = dedent("""
        Set tw / jan.wet, feb.wet, mar.dry /;
        Set tw2 / (jan,feb).wet, mar.dry /;
        """)
    model = parser.parse_model_text(text)
    assert model.sets["tw"].members == ["jan.wet", "feb.wet", "mar.dry"]
    assert model.sets["tw2"].members == ["jan.wet", "feb.wet", "mar.dry"]
```

## Related Files

- `src/gams/gams_grammar.lark`: `set_member` rule
- `src/ir/parser.py`: `_expand_set_members()` method
- `data/gamslib/raw/clearlak.gms`: Line 42
- `data/gamslib/raw/turkey.gms`: Line 58
