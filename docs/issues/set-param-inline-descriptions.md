# Issue: Sets and Parameters with Inline Descriptions Misparsed

**Status**: Open  
**Priority**: High  
**Component**: Parser (Grammar)  
**GitHub Issue**: [#417](https://github.com/jeffreyhorn/nlp2mcp/issues/417)

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

## Next Steps

1. Create GitHub issue
2. Add test case to reproduce the problem
3. Investigate grammar patterns for set_decl and param_decl
4. Consider same solution approach as variables: split into single vs. list patterns
5. Implement fix ensuring all sets/parameters with descriptions are registered correctly
