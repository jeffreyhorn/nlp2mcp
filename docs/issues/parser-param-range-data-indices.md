# Issue: Parameter Data Range Indices Not Parsed Correctly

**Status**: Open  
**Priority**: Medium  
**Component**: Parser (Parameter Data Handling)  
**GitHub Issue**: [#421](https://github.com/jeffreyhorn/nlp2mcp/issues/421)  
**Tier 2 Candidate**: pool.gms

## Description

When parsing parameter data with range notation for indices (e.g., `foulds3*foulds5 -8`), the parser fails with a dimension mismatch error. The range notation `*` is used to specify multiple consecutive set elements sharing the same value, but the parser is not expanding or handling this correctly for parameter data.

## Example

**File**: `tests/fixtures/tier2_candidates/pool.gms` (via poolmod.inc)

```gams
Parameter sol(case) 'global solution' / haverly1         -400,
                                        haverly2         -600,
                                        haverly3         -750,
                                        foulds2         -1100,
                                        foulds3*foulds5    -8,   <- Error here
                                        bental4          -450,
                                        bental5         -3500,
                                        rt2             -4391.8258928,
                                        adhya1*adhya2    -549.80305,
                                        adhya3           -561.044687,
                                        adhya4           -877.64574   /;
```

**Error**:
```
Error: Parameter 'sol' data index mismatch: expected 1 dims, got 0 [context: expression] (line 180, column 41)
```

## Root Cause

The parameter `sol` is declared with domain `(case)`, meaning it expects 1-dimensional indices. The line `foulds3*foulds5 -8` uses range notation where `foulds3*foulds5` should expand to `foulds3`, `foulds4`, `foulds5` (all with value -8).

The parser appears to be:
1. Not recognizing the range notation `*` in parameter data indices, OR
2. Treating `foulds3*foulds5` as a single 0-dimensional value instead of a range

## Grammar Analysis

Looking at the grammar in `src/gams/gams_grammar.lark`:

```lark
param_data_item: data_matrix_row                         -> param_data_matrix_row
                 | data_indices NUMBER                   -> param_data_scalar

data_indices: range_expr
            | (SET_ELEMENT_ID | NUMBER) ("." (SET_ELEMENT_ID | NUMBER))*

range_expr: range_bound TIMES range_bound
range_bound: NUMBER | ID
```

The grammar does support `range_expr` for data indices, but the issue may be in how the parser processes this in `_handle_params_block` or related functions.

## Investigation Needed

1. Check if `range_expr` is being matched correctly for parameter data indices
2. Verify how `_handle_param_data_item` processes range expressions
3. Confirm the semantic validation is correctly counting dimensions for range indices
4. Test with a minimal reproduction case

## Minimal Reproduction

```gams
Set i /a, b, c, d, e/;
Parameter p(i) / a*c 10, d 20, e 30 /;
```

Expected: `p('a') = 10, p('b') = 10, p('c') = 10, p('d') = 20, p('e') = 30`

## Impact

- **Blocks**: pool.gms from parsing completely (Tier 2 GAMS library file)
- **Severity**: Medium - Range notation is common in GAMS parameter data
- **Workaround**: Expand ranges manually (not practical for large datasets)

## Related Issues

- Issue #418 (Completed): Variables from include files not visible - Fixed preprocessing and variable kind merging
- The pool.gms file now gets past the variable scope issue but fails on this parameter parsing issue

## Notes

- This issue was discovered while testing the fix for issue #418
- The error occurs at line 180 in the preprocessed content, which corresponds to the `foulds3*foulds5 -8` line in the parameter data block
- Similar range patterns appear later in the file (`adhya1*adhya2 -549.80305`)
