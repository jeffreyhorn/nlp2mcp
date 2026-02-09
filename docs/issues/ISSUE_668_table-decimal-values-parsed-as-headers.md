# Issue #668: Table parser misinterprets decimal values starting with dot as column headers

**GitHub Issue:** [#668](https://github.com/jeffreyhorn/nlp2mcp/issues/668)
**Status:** Open
**Priority:** High
**Category:** Parser Bug

## Summary

The table parser incorrectly interprets numeric values that start with a decimal point (e.g., `.005`, `.001`) as column headers instead of data values. This causes incorrect table parsing and ultimately fails during MCP emission with "Set element '.001' contains invalid characters" error.

## Reproduction

**Model:** `data/gamslib/raw/chenery.gms`

### Problematic table structure

```gams
Table tdat(lmh,*,t) 'trade parameters'
                     light-ind  food+agr  heavy-ind
   medium.alp            .005      .001      .01
   high  .alp            .0025     .0005     .00178
   (medium,high).gam    1.0       1.1       1.0
   (medium,high).xsi     .005      .0157     .00178;
```

### Expected parsing

Column headers: `light-ind`, `food+agr`, `heavy-ind`

Row labels and values:
- `medium.alp`: `.005`, `.001`, `.01` (values 0.005, 0.001, 0.01)
- `high.alp`: `.0025`, `.0005`, `.00178`
- etc.

### Actual parsing (incorrect)

The parser treats `.005`, `.001`, `.01` as column headers instead of values:

```python
>>> ir = parse_model_text(gams)
>>> for k, v in ir.params['tdat'].values.items():
...     print(f'{k}: {v}')
('high.alp', '.005'): 0.0025    # Wrong! '.005' is treated as column header
('high.alp', '.001'): 0.0005    # Wrong! '.001' is treated as column header
('medium.gam', '.005'): 1.0     # Wrong column headers
```

The correct column headers should be `light-ind`, `food+agr`, `heavy-ind`, not `.005`, `.001`, `.01`.

## Error message

When running `nlp2mcp` on chenery.gms:

```
Error: Invalid model - Set element '.001' contains invalid characters. 
Set elements must start with a letter or digit and contain only letters, 
digits, underscores, hyphens, dots, and plus signs.
```

## Root Cause Analysis

The issue appears to be in the table parsing logic in `src/ir/parser.py`. Two factors contribute:

### 1. Row label with space before dot

The row `high  .alp` (note the space before `.alp`) may be confusing the parser about where the row label ends.

### 2. Decimal values look like dotted labels

Values like `.005` start with a dot, which the parser may interpret as part of a dotted label pattern (used in GAMS for tuple notation like `medium.alp`).

### Parsing steps that likely go wrong:

1. Parser sees column header line: `light-ind  food+agr  heavy-ind`
2. Parser sees data row: `medium.alp  .005  .001  .01`
3. Instead of recognizing `.005` as a numeric value, it may:
   - Think the row continues with more dotted labels, OR
   - Confuse column position matching due to the dot prefix

## Test Case

```python
def test_table_decimal_values_starting_with_dot():
    """Verify table values starting with . are parsed as numbers, not labels."""
    gams = '''
    Set lmh /low, medium, high/;
    Set t /light-ind, food+agr, heavy-ind/;
    
    Table tdat(lmh,*,t)
                         light-ind  food+agr  heavy-ind
       medium.alp            .005      .001      .01
       high.alp              .0025     .0005     .00178;
    '''
    ir = parse_model_text(gams)
    tdat = ir.params['tdat']
    
    # Column headers should be the set elements, not decimal values
    keys = list(tdat.values.keys())
    second_dims = {k[1] for k in keys if len(k) >= 2}
    
    assert 'light-ind' in second_dims, "Expected 'light-ind' as column header"
    assert 'food+agr' in second_dims, "Expected 'food+agr' as column header"
    assert '.005' not in second_dims, "'.005' should be a value, not a column header"
    assert '.001' not in second_dims, "'.001' should be a value, not a column header"
    
    # Values should be correct
    assert tdat.values[('medium.alp', 'light-ind')] == 0.005
    assert tdat.values[('medium.alp', 'food+agr')] == 0.001
```

## Files to investigate

1. `src/ir/parser.py` - Table parsing logic, specifically:
   - `_parse_table_data()` or similar function
   - Column header detection
   - Row label vs value disambiguation
   - Handling of dotted labels vs numeric values

2. `src/gams/gams_grammar.lark` - Grammar rules for:
   - `NUMBER` token (should match `.005`)
   - Table row/value patterns

## Fix Approach

### Option A: Improve column-value disambiguation

When parsing table rows, explicitly check if a token matches the NUMBER pattern before treating it as a label. Tokens like `.005` should be recognized as numbers.

### Option B: Use column position matching

After identifying the column headers (from the header row), use positional matching to assign values. Values that don't align with a known column header position should be associated with the nearest column.

### Option C: Two-pass parsing

1. First pass: identify all column headers from the header row
2. Second pass: for each data row, parse row label(s) then match remaining tokens to columns by position

## Impact

- chenery.gms fails to generate MCP
- Any GAMS model with tables containing decimal values starting with `.` may fail
- This is a common GAMS syntax pattern (`.005` instead of `0.005`)

## Related

- Issue #665 (hyphenated identifiers) - similar table parsing challenges
- The fix may need to coordinate with the column matching algorithm updated in #665
