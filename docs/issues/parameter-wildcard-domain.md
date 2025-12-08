# Issue: Wildcard Domain `*` in Parameter Declarations Not Handled

**Status**: Open  
**Priority**: Medium  
**Component**: Parser (Parameter Declaration Handling)  
**GitHub Issue**: [#425](https://github.com/jeffreyhorn/nlp2mcp/issues/425)  
**Tier 2 Candidate**: pool.gms

## Description

When parsing parameter declarations with wildcard domains (e.g., `rep2(case,*)`), the parser does not correctly recognize the wildcard `*` as a valid domain dimension. This causes subsequent assignments to the parameter to fail with an index mismatch error.

## Example

**File**: `tests/fixtures/tier2_candidates/pool.gms`

```gams
Parameter
   rep1(case,*) 'problem characteristics'
   rep2(case,*) 'solution summary';

* Later in the file:
rep2(case, 'Solstat')   = poolprob.solveStat;
rep2(case, 'Modstat')   = poolprob.modelStat;
rep2(case, 'Obj')       = poolprob.objVal;
rep2(case,'optcr')$(abs(sol(case)) > 1e-6) = round(abs((rep2(case,'Obj') - sol(case))/sol(case)),6);
```

**Error**:
```
Parameter 'rep2' expects 1 index but received 2 [context: assignment] [domain: ('case', 'optcr')] (line 850, column 56)
```

## Root Cause

The parameter `rep2` is declared with domain `(case,*)` where `*` is a wildcard that accepts any set element as the second index. However, the parser appears to be:

1. Not recognizing `*` as a valid domain dimension, OR
2. Treating `rep2(case,*)` as a 1-dimensional parameter instead of 2-dimensional

When the code later assigns `rep2(case, 'optcr') = ...`, the parser expects 1 index (based on its incorrect understanding) but receives 2.

## Grammar Analysis

Looking at the grammar in `src/gams/gams_grammar.lark`, there is support for wildcards in some contexts:

```lark
id_or_wildcard_list: (ID | WILDCARD) ("," (ID | WILDCARD))*
WILDCARD: "*"
```

The `id_or_wildcard_list` rule is used in parameter declarations:

```lark
param_single_item: ID "(" id_or_wildcard_list ")" (STRING | desc_text)? "/" param_data_items "/" param_default? -> param_domain_data
                 | ID "(" id_or_wildcard_list ")" (STRING | desc_text)? param_default?                          -> param_domain
```

The grammar appears to support wildcards, so the issue is likely in how the parser processes the `id_or_wildcard_list` and tracks the parameter's dimensionality.

## Investigation Needed

1. Check how `_id_or_wildcard_list()` processes wildcard tokens
2. Verify how `ParameterDef.domain` is populated when wildcards are present
3. Check the assignment validation logic that compares expected vs received indices
4. Determine if wildcards should be stored as a special marker (e.g., `"*"`) or handled differently

## Minimal Reproduction

```gams
Set i /a, b, c/;
Parameter p(i,*) / a.x 1, b.y 2, c.z 3 /;
```

Or without initial data:

```gams
Set i /a, b, c/;
Parameter p(i,*);
p(i, 'foo') = 10;
```

Expected: `p` is a 2-dimensional parameter where the second dimension accepts any element.

## GAMS Semantics

In GAMS, the wildcard `*` in a domain declaration means:
- The parameter/variable accepts any valid set element in that position
- It's commonly used for "report" parameters that aggregate results across different categories
- The wildcard dimension doesn't need to be pre-declared as a set

## Impact

- **Blocks**: pool.gms from parsing completely (Tier 2 GAMS library file)
- **Severity**: Medium - Wildcard domains are common in GAMS for report parameters
- **Workaround**: Replace `*` with an explicit set containing all needed elements (not practical)

## Related Issues

- Issue #421 (Completed): Parameter data range indices - Fixed range notation in parameter data
- Issue #424 (Completed): Set parsing for newline-separated declarations - Fixed grammar ambiguity
- pool.gms now parses to line 850 (previously failed much earlier)

## Notes

- This issue was discovered after fixing issues #421 and #424
- The file now parses much further than before, with sets and parameter data working correctly
- The wildcard domain issue is the next blocking problem for pool.gms
