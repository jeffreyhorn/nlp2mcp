# Issue: Numeric Values in Parameter/Set Data Context Not Supported

**GitHub Issue:** [#555](https://github.com/jeffreyhorn/nlp2mcp/issues/555)  
**Status:** Open  
**Priority:** Medium  
**Discovered:** Sprint 16 Day 6 (2026-01-23)  
**Affected Models:** abel, ajax, immun, and potentially others

---

## Summary

The GAMS grammar fails to parse parameter data declarations where set element identifiers are followed by numeric values on the same line. The parser incorrectly interprets the numeric value as part of the identifier context.

## Error Message

```
Parse error at line 54, column 49: Unexpected character: '1'
  uinit(m)    'initial controls'   / 'gov-expend' 110.5, money   147.1 /
                                                  ^
```

## Reproduction Steps

1. Run parse on model `abel`:
   ```bash
   python scripts/gamslib/batch_parse.py --model abel --verbose
   ```

2. Or directly:
   ```python
   from src.ir.parser import parse_model_file
   parse_model_file('data/gamslib/raw/abel.gms')
   ```

## Example GAMS Code

### From abel.gms (line 54)

```gams
Parameter
   c(n)        'constant term'      / consumpt -59.4,   invest -184.7 /
   xinit(n)    'initial value'      / consumpt 387.9,   invest   85.3 /
   uinit(m)    'initial controls'   / gov-expend 110.5, money   147.1 /
```

The syntax `/ gov-expend 110.5, money 147.1 /` is a parameter data initialization where:
- `gov-expend` and `money` are set element identifiers
- `110.5` and `147.1` are the corresponding parameter values

### From immun.gms (lines 74-80)

```gams
Set
   ts 'time points' / 89-07, 89-08, 90-02, 90-08, 91-02
                      91-08, 92-02, 92-08, 93-02, 93-08 /
```

Set elements like `89-07` start with numbers and contain hyphens.

## Root Cause Analysis

The grammar has two related issues:

### Issue 1: Parameter Data Parsing

The `param_data_item` rule expects:
```lark
param_data_item: data_matrix_row                         -> param_data_matrix_row
               | data_indices NUMBER                     -> param_data_scalar

data_indices: range_expr
            | (SET_ELEMENT_ID | NUMBER) ("." (SET_ELEMENT_ID | NUMBER))*
```

When parsing `gov-expend 110.5`, the grammar tries to match `SET_ELEMENT_ID NUMBER` but the space between identifier and number causes issues with tokenization.

### Issue 2: SET_ELEMENT_ID vs NUMBER Disambiguation

After Sprint 16 Day 6, `SET_ELEMENT_ID` was extended to `/[a-zA-Z0-9_][a-zA-Z0-9_+\-]*/` to support `1964-i`. However, this can conflict with `NUMBER` in certain contexts.

The pattern `89-07` could be interpreted as:
- A `SET_ELEMENT_ID` (intended): `89-07` as a single identifier
- Or incorrectly as: `NUMBER` (`89`) followed by something

## Proposed Fix

### Option A: Improve data_indices Rule

Enhance `data_indices` to better handle the identifier-followed-by-number pattern:

```lark
// Current
data_indices: range_expr
            | (SET_ELEMENT_ID | NUMBER) ("." (SET_ELEMENT_ID | NUMBER))*

// Enhanced - explicit handling of quoted and hyphenated identifiers
data_indices: range_expr
            | data_key ("." data_key)*

data_key: SET_ELEMENT_ID
        | NUMBER
        | STRING  // For quoted identifiers like 'gov-expend'
```

### Option B: Use Quoted Identifiers

The abel.gms example uses `'gov-expend'` (quoted) which should work. Investigate why it's still failing - may be a tokenization priority issue.

### Option C: Lexer Priority Adjustment

Adjust terminal priorities to ensure `SET_ELEMENT_ID` is preferred over `NUMBER` in set/parameter data context:

```lark
SET_ELEMENT_ID.3: /[a-zA-Z0-9_][a-zA-Z0-9_+\-]*/  // Higher priority
```

### Recommendation

Start with Option B investigation - if quoted identifiers should work, there may be a simpler fix. Then consider Option A for unquoted hyphenated identifiers.

## Affected Models

| Model | Line | Syntax Example |
|-------|------|----------------|
| abel | 54 | `/ gov-expend 110.5, money 147.1 /` |
| ajax | TBD | Similar parameter data |
| immun | 74-80 | `/ 89-07, 89-08, ... /` (number-start set elements) |

## Testing

After fix, verify:
1. abel, ajax, immun parse successfully
2. No regressions in existing 36 parsing models
3. Parameter data values are correctly captured

## Related Issues

- Sprint 16 Day 6 grammar fixes (PR #553)
- P-2 hyphenated set element fix partially addressed this, but secondary issues remain
- LEXER_ERROR_ANALYSIS.md: "Numeric context issues" category (11 models)

## References

- GAMS Documentation: [Parameter Data](https://www.gams.com/latest/docs/UG_DataEntry.html)
- Model sources: `data/gamslib/raw/abel.gms`, `data/gamslib/raw/immun.gms`
