# Issue #668: Table parser misinterprets decimal values starting with dot as column headers

**GitHub Issue:** [#668](https://github.com/jeffreyhorn/nlp2mcp/issues/668)
**Status:** Fixed
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

### Actual parsing (incorrect - before fix)

The parser treats `.005`, `.001`, `.01` as column headers instead of values:

```python
>>> ir = parse_model_text(gams)
>>> for k, v in ir.params['tdat'].values.items():
...     print(f'{k}: {v}')
('high.alp', '.005'): 0.0025    # Wrong! '.005' is treated as column header
('high.alp', '.001'): 0.0005    # Wrong! '.001' is treated as column header
('medium.gam', '.005'): 1.0     # Wrong column headers
```

## Root Cause Analysis

The actual root cause was different from initial analysis:

### The `+` in column headers triggers table continuation parsing

The column header line `light-ind  food+agr  heavy-ind` was being incorrectly parsed because:

1. The grammar's DESCRIPTION terminal only supported `-` in identifiers, not `+`
2. When the lexer encountered `food+agr`, the `+` was interpreted as the start of a `table_continuation` rule
3. This caused the grammar to parse:
   - `light` as a row label
   - `-ind` as a `negative_special` value (MINUS + ID)
   - `food` as a table value
   - `+agr heavy -ind` as a table continuation

4. With the column header row being mis-parsed, the actual column headers were picked up from the FIRST DATA ROW instead, which contained `.005`, `.001`, `.01`

### Why decimal values became column headers

Since the column header detection was applied to the wrong line (due to `+` triggering continuation), the decimal values from the first data row were treated as column headers.

## Fix Implementation

### File: `src/ir/preprocessor.py`

Modified `normalize_special_identifiers()` to detect and quote table column headers when any identifier contains `+`.

**Before:** Column headers were kept unquoted, relying on the DESCRIPTION terminal which only supports `-`.

**After:** When ANY column header contains `+`, the ENTIRE header line is processed and ALL special identifiers (both `+` and `-`) are quoted. This is necessary because:
1. The `+` triggers the table_continuation rule, so we must quote it
2. Once we quote, we can no longer rely on the DESCRIPTION terminal for any identifiers
3. Therefore all special identifiers on the line must be quoted

For example, `light-ind  food+agr  heavy-ind` becomes `'light-ind'  'food+agr'  'heavy-ind'`.

```python
# Issue #668: Column headers with + MUST be quoted because + triggers
# table_continuation parsing. Without quoting, "food+agr" would be parsed
# as "food" followed by a continuation "+agr". When any identifier on
# the line contains +, we quote ALL special identifiers on that line
# (including hyphenated ones) since we can no longer rely on DESCRIPTION.
if not table_header_seen and stripped:
    table_header_seen = True
    # Issue #668: Quote identifiers with + in column headers
    # Check if line contains an identifier with +; identifiers may start
    # with a letter, digit, or underscore and contain letters, digits,
    # underscores, plus, and minus characters.
    if re.search(r"\b[0-9A-Za-z_][0-9A-Za-z_+-]*\+[0-9A-Za-z_+-]+\b", stripped):
        processed = _quote_special_in_line(line)
        result.append(processed)
    else:
        result.append(line)  # Keep original header line
    continue
```

### File: `tests/unit/test_special_identifiers.py`

Updated `test_table_header_special_chars()` to reflect the new behavior:
- When ANY column header contains `+`, ALL special identifiers on the line are quoted
- Column headers with only `-` (no `+` present) continue to work via DESCRIPTION terminal

Added `test_table_plus_header_parsing()` as an end-to-end regression test that verifies:
- Column headers with `+` are correctly identified (not decimal values)
- Decimal values starting with `.` are parsed as numeric values
- The complete table structure is correct after parsing

## Verification

After the fix:

```python
>>> from src.ir.parser import parse_model_text
>>> gams = '''
... Set lmh /low, medium, high/;
... Set t /light-ind, food+agr, heavy-ind/;
...
... Table tdat(lmh,*,t) 'trade parameters'
...                      light-ind  food+agr  heavy-ind
...    medium.alp            .005      .001      .01
...    high.alp              .0025     .0005     .00178;
... '''
>>> model = parse_model_text(gams)
>>> for k, v in model.params['tdat'].values.items():
...     print(f'{k}: {v}')
('medium.alp', 'light-ind'): 0.005   # Correct!
('medium.alp', 'food+agr'): 0.001    # Correct!
('medium.alp', 'heavy-ind'): 0.01    # Correct!
('high.alp', 'light-ind'): 0.0025
('high.alp', 'food+agr'): 0.0005
('high.alp', 'heavy-ind'): 0.00178
```

## Tests

All 3281 tests pass after the fix.

## Related Issues

- Issue #665 (hyphenated identifiers) - established the pattern for quoting special identifiers
