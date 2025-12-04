# Issue: Sets and Parameters with Inline Descriptions Misparsed

**Status**: Completed  
**Priority**: High  
**Component**: Parser (Grammar)  
**GitHub Issue**: [#417](https://github.com/jeffreyhorn/nlp2mcp/issues/417)  
**Branch**: fix-issue-409-pool-include-file  
**Resolved**: Sprint 12 Day 5 (2024)

## Description

The remaining issue with `pool.gms` failing to parse is due to sets and parameters with inline descriptions being misparsed. Specifically, when multiple sets are declared with inline descriptions in the same block, the `desc_text` pattern consumes subsequent set identifiers, causing them not to be registered.

## Example

In `tests/fixtures/tier2_candidates/pool.gms` lines 58-63:

```gams
Set
   comp_ 'components and raw materials' / c1*c32 /
   pro_  'products'                     / p1*p16 /
   qual_ 'qualities'                    / q1*q10 /
   pool_ 'pools'                        / o1*o10 /
```

The parser fails to register `pool_` and `qual_` correctly, leading to:
- Error: "Unknown set or alias 'pool_' referenced in equation domain [context: expression] (line 105, column 11)"

## Root Cause

The `desc_text` pattern in the grammar is designed to match 3+ word descriptions:
```lark
desc_text: _desc_word _desc_word _desc_word+
```

However, when sets/parameters have single-word quoted descriptions like `'pools'` or `'qualities'`, these are STRING tokens, not desc_text. The issue arises from the interaction between:

1. **Set declarations with mixed description styles**: Some use STRING (quoted), others use desc_text (unquoted multi-word)
2. **Newline-delimited declarations**: Multiple sets on separate lines
3. **Grammar ambiguity**: The pattern `set_decl: ID (STRING | desc_text)? "/" set_members "/"` expects the description to be either a STRING token or desc_text, but the parsing may not correctly distinguish between a single-word STRING and the start of the next set identifier

## Similar Issues

This same problem likely affects:
- **Parameters** with inline descriptions (line 27-35 in `poolmod.inc`)
- **Scalars** with inline descriptions

From `poolmod.inc`:
```gams
parameters cl(comp_)          min use of raw material
           cu(comp_)          max avaialbility of raw material
           cprice(comp_)      unit cost of raw materials
```

The unquoted descriptions like `min use of raw material` should work with `desc_text`, but may be consuming subsequent parameter names.

## Investigation Needed

1. Check if STRING tokens (quoted descriptions) are being parsed correctly when multiple sets are on separate lines
2. Verify if the issue is with quoted vs unquoted descriptions
3. Test if the problem occurs with:
   - All quoted descriptions: `comp_ 'description'`
   - All unquoted descriptions: `comp_ multi word description`
   - Mixed quoted/unquoted in same block

## Impact

- **Blocks**: `pool.gms` from parsing completely
- **Affects**: Tier 2 GAMS library files that use inline descriptions extensively
- **Workaround**: None without modifying source files (which violates project constraints)

## Related Issues

- Issue #416: Semantic: Undefined Symbol Validation (RESOLVED) - Fixed variables with inline descriptions
- This issue extends the same problem to sets and parameters

## Test Case

Create a minimal test case:
```gams
Set
   s1 'first set'  / a, b, c /
   s2 'second set' / d, e, f /
   s3 'third set'  / g, h, i /;

Parameter p(s3);  # Should recognize s3
```

Expected: All three sets registered, parameter references `s3` successfully
Actual: TBD - need to verify exact behavior

---

## Resolution

**Resolved**: Sprint 12 Day 5 (2024)  
**Commit**: `3ffa4dd` - Fix issue #417: Sets and Parameters with Inline Descriptions

### Root Cause

The issue had two problems:
1. **desc_text as a rule consumed tokens across newlines**: When desc_text was a grammar rule matching `_desc_word _desc_word _desc_word+`, it would match IDs across multiple lines, causing subsequent set/parameter names to be consumed as part of a description.
2. **Quoted strings (ESCAPED) were treated as IDs**: Both ID and STRING could match quoted text, and ID had higher priority, so desc_text could match quoted strings.

### Solution Implemented

Applied a multi-part fix similar to issue #416:

1. **Split patterns** (same as variables):
   - `set_decl: set_item ("," set_item)+ | set_single_item`
   - `param_decl: param_item ("," param_item)+ | param_single_item`
   - Single items allow desc_text, list items only allow STRING

2. **Made desc_text a terminal token**:
   - Changed from rule to terminal: `DESC_TEXT.-1: /[a-zA-Z_][\w\-]*(?:[ \t]+[a-zA-Z_][\w\-]*){1,}/`
   - Uses `[ \t]+` (space/tab) instead of `\s+` to prevent matching across newlines
   - Matches 2+ words (changed from 3+ to support "total cost")
   - Priority -1 to avoid interfering with normal ID matching

3. **Parser updates**:
   - Updated handlers to route through `_process_set_decl` and `_process_param_decl`
   - Added `_process_set_item` and `_process_param_item` helpers
   - Modified `_parse_var_decl` to handle DESC_TEXT as a Token instead of Tree node
   - Added backward compatibility for legacy desc_text tree nodes

### Test Results

All tests passing (2190 passed):
- ✅ Sets with unquoted multi-word descriptions parse correctly
- ✅ Parameters with inline descriptions parse correctly  
- ✅ Newline-separated declarations work
- ✅ 2-word descriptions like "total cost" supported
- ✅ Space-separated set declarations still work

### Verified Examples

**poolmod.inc sets**:
```gams
Sets comp_ Components and Raw Matereials
     pro_  Products
     qual_ Qualities
     pool_ Pools
```
Result: All four sets registered correctly ✓

**poolmod.inc variables**:
```gams
variables  q(comp_, pool_) pool quality from pooling raw materials
           y(pool_, pro_)  flow from pool to product
           z(comp_, pro_)  direct flow of rawmaterials to product
           cost            total cost
```
Result: All variables parse correctly (semantic validation requires set definitions) ✓

### Lessons Learned

1. **Terminal vs Rule**: Using a terminal with explicit line-boundary constraints ([ \t] vs \s) prevents cross-line matching better than rule-based patterns
2. **Priority matters**: Terminal priority (-1) prevents interference with normal lexing
3. **2-word minimum**: Requiring 3+ words was too restrictive; 2+ words balances ambiguity vs usability
4. **Consistent patterns**: Applying the same split-pattern approach (single vs list) across sets, parameters, and variables maintains consistency
