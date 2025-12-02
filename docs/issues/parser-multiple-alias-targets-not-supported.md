# Parser: Multiple Alias Targets Not Supported

**GitHub Issue:** #377  
**URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/377  
**Priority:** HIGH  
**Tier 2 Models Blocked:** gasoil.gms

## Problem

The parser does not support alias declarations with multiple target sets in a single alias name, such as `Alias (nc,j,k)` which declares `nc` as an alias for both `j` and `k`. Additionally, multiple alias pairs in a single statement like `Alias (a,b), (c,d);` are not supported.

## Example from Tier 2 Model

### gasoil.gms (line 85)
```gams
Alias (nh,i), (nc,j,k), (ne, s);
```

This declares:
- `nh` as an alias for set `i`
- `nc` as an alias for both sets `j` and `k`
- `ne` as an alias for set `s`

## Current Error

```
Error: Parse error at line 85, column 20: Unexpected character: ','
  Alias (nh,i), (nc,j,k), (ne, s);
                     ^

Suggestion: This character is not valid in this context
```

## GAMS Specification

GAMS supports two alias syntax patterns:

### 1. Multiple Alias Pairs (Comma-Separated)
```gams
Alias (a,b), (c,d), (e,f);
```
Declares three separate alias relationships in one statement.

### 2. Multiple Target Sets (Single Alias, Multiple Targets)
```gams
Alias (nc,j,k);
```
Declares `nc` as an alias for both `j` and `k`. This means `nc` can be used interchangeably with either `j` or `k`.

### 3. Combined Syntax
```gams
Alias (nh,i), (nc,j,k), (ne,s);
```
Combines both patterns in a single statement.

## Current Parser Behavior

The parser currently handles only:
```gams
Alias (target, alias_name);
```

A single alias pair per statement, where:
- First identifier is the target set
- Second identifier is the new alias name

## Technical Details

### Grammar Changes Needed

Current grammar (simplified):
```lark
alias_pair: "(" ID "," ID ")"
```

Needed grammar:
```lark
alias_pair: "(" ID "," id_list ")"  // Multiple targets
aliases_statement: alias_pair ("," alias_pair)*  // Multiple pairs
```

### Parser Changes Needed

1. **Grammar:** Extend `alias_pair` to accept multiple target identifiers
2. **Grammar:** Allow multiple `alias_pair` separated by commas
3. **Parser:** Update `_process_alias_pair()` to handle:
   - Multiple targets: Register the alias for each target
   - Multiple pairs: Iterate and process each pair
4. **Validation:** Ensure all target sets exist before creating aliases

### Implementation Approach

```python
def _process_alias_pair(self, pair_node: Tree) -> None:
    """Process alias pair: (target_set, alias_name, ...) or multiple aliases."""
    ids = [_token_text(tok) for tok in pair_node.children if tok.type == "ID"]
    
    if len(ids) >= 2:
        # First ID is the primary target, remaining IDs are aliases
        target = ids[0]
        alias_names = ids[1:]
        
        for alias_name in alias_names:
            self._register_alias(alias_name, target, None, pair_node)
    else:
        raise self._error(f"Alias pair must have at least 2 identifiers", pair_node)

def _handle_aliases_block(self, node: Tree) -> None:
    """Handle Aliases block with potentially multiple pairs."""
    for child in node.children:
        if isinstance(child, Tree) and child.data == "alias_pair":
            self._process_alias_pair(child)
```

### Semantic Considerations

1. **Multiple targets for one alias:** When `Alias (nc,j,k)` is declared, `nc` becomes an alias for both `j` and `k`. This means:
   - `nc` can be used wherever `j` or `k` are valid
   - The sets `j` and `k` should typically have compatible domains
   - In practice, this is often used when `j` and `k` are already aliases or related sets

2. **Alias chains:** If `Alias (a,b)` and `Alias (c,a)`, then `c` is indirectly an alias for `b`

## Impact

- **Blocks:** 1 Tier 2 model (gasoil.gms)
- **Frequency:** Common syntax pattern for declaring multiple related aliases concisely
- **Workaround:** Split into multiple `Alias` statements (but model would need modification)

## Test Cases Needed

1. **Single pair:** `Alias (a,b);`
2. **Multiple pairs:** `Alias (a,b), (c,d);`
3. **Multiple targets:** `Alias (a,b,c);`
4. **Combined:** `Alias (a,b,c), (d,e);`
5. **Validation:** Ensure target sets exist
6. **Usage:** Use aliases in equations and verify correct behavior

## Priority Justification

**HIGH Priority** because:
- Blocks 1 Tier 2 model
- Common syntax pattern for concise alias declarations
- Relatively straightforward to implement
- Improves parser's handling of real-world GAMS models

## Related Issues

- Issue #371: Multiple alias targets (closed) - may have partial implementation
- Current alias implementation already handles basic cases
- Need to extend grammar and parser, not a fundamental redesign
