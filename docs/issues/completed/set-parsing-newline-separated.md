# Issue: Set Parsing Fails for Newline-Separated Declarations Without Commas

**Status**: Completed  
**Priority**: Medium  
**Component**: Parser (Set Declaration Handling)  
**GitHub Issue**: [#424](https://github.com/jeffreyhorn/nlp2mcp/issues/424)  
**Tier 2 Candidate**: pool.gms

## Description

When parsing multiple set declarations separated by newlines (without commas), the parser incorrectly splits set definitions. A set's quoted description string can be mistakenly parsed as a new set name, causing the original set to have no members.

## Example

**File**: `tests/fixtures/tier2_candidates/pool.gms`

```gams
Set
   comp_ 'components and raw materials' / c1*c32 /
   pro_  'products'                     / p1*p16 /
   qual_ 'qualities'                    / q1*q10 /
   pool_ 'pools'                        / o1*o10 /
   case  'case index'
          / haverly1*haverly3, foulds2*foulds5, bental4*bental5, rt2, adhya1*adhya4 /
   labels / lo 'lower bound', up 'upper bound', price /;
```

**Expected Parsing**:
- `comp_` with members `c1` to `c32`
- `pro_` with members `p1` to `p16`
- `case` with members `haverly1`, `haverly2`, `haverly3`, `foulds2`, ..., `adhya4`

**Actual Parsing**:
- `comp_` with members `c1` to `c32` (correct)
- `pro_` as empty set (wrong - should have members)
- `'products'` as set name with members `p1` to `p16` (wrong - should be description)
- `case` as empty set (wrong)
- `'case index'` as set name with members `haverly1`, ..., `adhya4` (wrong)

## Root Cause

The grammar defines `set_single_item` patterns that can match either:
1. `ID (STRING | desc_text)? "/" set_members "/"` → `set_simple`
2. `ID (STRING | desc_text)?` → `set_empty`

When the Earley parser encounters newline-separated set declarations like:
```
pro_  'products'   / p1*p16 /
```

It can choose to:
1. Match `pro_` as `set_empty` (ID only)
2. Then match `'products' / p1*p16 /` as a new `set_simple` (treating `'products'` as the set NAME)

This happens because `ID` is defined as `ESCAPED | /[a-zA-Z_][a-zA-Z0-9_]*/` where `ESCAPED` matches quoted strings like `'products'`.

## Grammar Analysis

From `src/gams/gams_grammar.lark`:

```lark
// For single set declarations: allow desc_text or STRING
set_single_item: ID "(" id_list ")" (STRING | desc_text)? "/" set_members "/"     -> set_domain_with_members
               | ID (STRING | desc_text)? "/" set_members "/"                     -> set_simple
               | ID (STRING | desc_text)? alias_opt "/" set_members "/"           -> set_aliased
               | ID "(" id_list ")" (STRING | desc_text)?                         -> set_domain
               | ID (STRING | desc_text)?                                         -> set_empty

ID: ESCAPED | /[a-zA-Z_][a-zA-Z0-9_]*/
ESCAPED: /'[^']*'|\"[^\"]*\"/
```

The ambiguity arises because:
1. `sets_block` allows multiple `set_decl+` in sequence
2. Each `set_decl` can be a `set_single` (single item)
3. The parser greedily matches shorter patterns first

## Minimal Reproduction

```gams
Set
   comp_ 'components' / c1*c32 /
   pro_  'products'   / p1*p16 /;
```

**Expected**:
- `comp_`: members `['c1', ..., 'c32']`
- `pro_`: members `['p1', ..., 'p16']`

**Actual**:
- `comp_`: members `['c1', ..., 'c32']`
- `pro_`: members `[]` (empty)
- `'products'`: members `['p1', ..., 'p16']`

## Potential Solutions

1. **Grammar priority adjustment**: Give `set_simple` (with members) higher priority than `set_empty`

2. **Prevent ESCAPED as set name**: Modify the grammar so that quoted strings cannot be used as set names in certain contexts

3. **Post-processing merge**: After parsing, detect orphaned quoted-string sets and merge them back as descriptions

4. **Require commas**: Enforce comma separation between set declarations (breaks GAMS compatibility)

## Impact

- **Blocks**: pool.gms and potentially other GAMS files using newline-separated set declarations
- **Severity**: Medium - Common GAMS pattern for multi-set declarations
- **Workaround**: Use comma-separated set declarations instead of newline-separated

## Related Issues

- Issue #421 (Completed): Parameter data range indices - Fixed range notation in parameter data
- Issue #417: Allow both space and newline separation for sets - Added the current grammar pattern

## Resolution

Fixed by implementing solution #2 from the potential solutions list:

1. **Added `SYMBOL_NAME` terminal** in `src/gams/gams_grammar.lark`:
   ```lark
   SYMBOL_NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
   ```
   This terminal matches only unquoted identifiers, unlike `ID` which includes `ESCAPED` (quoted strings).

2. **Updated set declaration rules** to use `SYMBOL_NAME` instead of `ID` for set names:
   - `set_single_item` rules now use `SYMBOL_NAME` for the set name
   - `set_item` rules now use `SYMBOL_NAME` for the set name

This prevents quoted description strings like `'products'` from being parsed as set names, ensuring they are correctly associated with their preceding set declaration.

**Test cases added**: 6 tests in `TestNewlineSeparatedSetDeclarations` covering:
- Two sets newline-separated with descriptions
- pool.gms pattern with multiple sets
- Set with multiline members
- Mixed with/without descriptions
- Empty sets newline-separated
- Verification that quoted strings are not set names

## Notes

- This issue was discovered while testing the fix for issue #421
- The issue only occurs with newline-separated declarations; comma-separated declarations work correctly
- Single set declarations with descriptions also work correctly
