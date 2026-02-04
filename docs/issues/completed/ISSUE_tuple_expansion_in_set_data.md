# Issue: Tuple Expansion Syntax in Set Data Not Supported

**GitHub Issue:** #612
**GitHub URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/612
**Status:** Open
**Priority:** Medium
**Category:** Parser/Grammar

## Summary

The parser does not support GAMS tuple expansion syntax `(a,b).c` in set data definitions. This syntax expands to multiple set elements: `(jan,feb).wet` expands to `jan.wet, feb.wet`.

## Affected Models

- `clearlak.gms` - Uses tuple expansion in set definition
- Other models in LEXER_IMPROVEMENT_PLAN.md subcategory 2.5 (8 models total):
  - dinam, egypt, indus, marco, paklive, shale, sparta, turkey

## Error Message

```
Error: Parse error at line 43, column 1: Unexpected character: '('
  (mar,apr).dry  /
  ^

Suggestion: This character is not valid in this context
```

## Reproduction

### Minimal Example
```gams
Set tw / (jan,feb).wet, (mar,apr).dry /;
```

### From clearlak.gms (lines 42-43)
```gams
   tw(t,w)  'relates months to weather conditions' /(jan,feb).wet
                                                    (mar,apr).dry  /
```

## Expected Behavior

The parser should expand tuple notation:
- `(jan,feb).wet` expands to `jan.wet, feb.wet`
- `(mar,apr).dry` expands to `mar.dry, apr.dry`

## Current Grammar

The current `set_member` rule in `src/gams/gams_grammar.lark` supports:
- `SET_ELEMENT_ID "." "(" set_element_id_list ")"` - suffix expansion (e.g., `a.(b,c)`)
- `"(" set_element_id_list ")" "." SET_ELEMENT_ID` - prefix expansion (e.g., `(a,b).c`)

However, the prefix expansion pattern only works when the tuple is NOT at the start of a line or after a comma in certain contexts.

## Proposed Fix

1. Review the grammar rules for `set_members` and `set_member` in `src/gams/gams_grammar.lark`
2. Ensure the `"(" set_element_id_list ")" "." SET_ELEMENT_ID -> set_tuple_prefix_expansion` rule is properly prioritized
3. May need to adjust the grammar to handle line continuation cases where tuple expansion appears at the start of a continuation line

### Files to Modify
- `src/gams/gams_grammar.lark` - Grammar rules for set_member
- `src/ir/parser.py` - Handler for tuple expansion if needed

## Test Cases

```python
def test_tuple_prefix_expansion_multiline():
    """Test tuple prefix expansion across multiple lines."""
    code = """
    Set tw / (jan,feb).wet
             (mar,apr).dry /;
    """
    model = parse_model_text(code)
    assert "tw" in model.sets
    assert "jan.wet" in model.sets["tw"].members
    assert "feb.wet" in model.sets["tw"].members
    assert "mar.dry" in model.sets["tw"].members
    assert "apr.dry" in model.sets["tw"].members
```

## Related Issues

- Issue #562: Tuple prefix expansion (a,b).c in set definitions (partially implemented)
- LEXER_IMPROVEMENT_PLAN.md subcategory 2.5: Tuple expansion syntax

## References

- `docs/planning/EPIC_3/SPRINT_17/LEXER_IMPROVEMENT_PLAN.md` - Section 2.5
- `data/gamslib/raw/clearlak.gms` - Example model
