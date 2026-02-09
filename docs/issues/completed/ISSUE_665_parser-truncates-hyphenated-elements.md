# Issue #665: Parser truncates set element names containing hyphens in Table data

**GitHub Issue:** [#665](https://github.com/jeffreyhorn/nlp2mcp/issues/665)
**Status:** Fixed
**Priority:** Medium
**Category:** Parser Bug

## Summary

The GAMS parser truncates set element names that contain hyphens when parsing Table data. For example, `20-bond-wt` becomes `20` in the parsed parameter data, but is correctly parsed as `20-` in the set declaration (though still missing `bond-wt`).

## Root Cause

Multiple interrelated issues in the preprocessing and parsing pipeline:

1. **Preprocessor pattern incomplete**: The `_quote_special_in_line()` pattern only matched identifiers starting with letters, missing number-starting identifiers like `20-bond-wt`.

2. **Table column headers not quoted**: Column headers couldn't be quoted because the grammar would interpret a leading quoted string as a table description.

3. **`_token_text()` didn't strip quotes from ID tokens**: The ESCAPED pattern in the grammar produces ID tokens (not STRING tokens) for quoted identifiers, but `_token_text()` only stripped quotes from STRING tokens.

4. **Column matching logic too restrictive**: The closest-match algorithm failed when column positions didn't perfectly align with values.

## Fix Details

### 1. Extended preprocessor pattern (`src/ir/preprocessor.py`)

Added support for number-starting hyphenated identifiers:
```python
# Before: Only matched letter-starting identifiers
pattern = r"\b([a-zA-Z_][a-zA-Z0-9_]*(?:[-+][a-zA-Z0-9_]+)+)\b"

# After: Also matches number-starting identifiers like 20-bond-wt
pattern = r"\b((?:[a-zA-Z_][a-zA-Z0-9_]*(?:[-+][a-zA-Z0-9_]+)+)|(?:[0-9]+[-][a-zA-Z0-9_]+(?:[-+][a-zA-Z0-9_]+)*))\b"
```

### 2. Table column headers kept unquoted (`src/ir/preprocessor.py`)

Column headers are NOT quoted because:
- A quoted string at the start would be consumed as a table description
- The DESCRIPTION terminal matches unquoted hyphenated words
- The parser handles DESCRIPTION tokens by splitting them into column headers

### 3. Added `normalize_special_identifiers` to `parse_text()` (`src/ir/parser.py`)

Callers of `parse_text()` directly now get proper preprocessing.

### 4. Extended `_token_text()` to strip quotes from ID tokens (`src/ir/parser.py`)

```python
# Now handles both STRING and escaped ID tokens
if token.type == "ID" and (
    (value[0] == "'" and value[-1] == "'")
    or (value[0] == '"' and value[-1] == '"')
):
    return value[1:-1].strip()
```

### 5. Updated grammar to allow STRING in dotted_label (`src/gams/gams_grammar.lark`)

```lark
dotted_label: (ID | STRING) ("." (ID | STRING | range_expr))*
```

### 6. Improved column matching with range-based algorithm (`src/ir/parser.py`)

Each column "owns" the range from its position up to the next column:
```python
range_start = col_pos - 3  # Allow 3 chars left tolerance
if idx + 1 < len(col_headers):
    range_end = col_headers[idx + 1][1] - 1
else:
    range_end = float("inf")
if range_start <= token_col <= range_end:
    best_match = col_name
```

### 7. Updated parser to accept STRING tokens in table headers and values

- Column headers now accept STRING tokens
- Row label processing includes STRING tokens
- Token collection from table rows includes STRING tokens

## Tests Added

```python
def test_number_starting_hyphenated_set_element():
    """Test set elements like '20-bond-wt' that start with digits (Issue #665)."""

def test_table_row_labels_with_number_hyphenated_elements():
    """Test table with hyphenated row labels starting with numbers (Issue #665)."""

def test_parameter_data_with_number_hyphenated_indices():
    """Test parameter data with indices like '20-bond-wt' (Issue #665)."""
```

## Files Modified

- `src/ir/preprocessor.py` - Extended pattern, kept column headers unquoted
- `src/ir/parser.py` - Multiple fixes for token handling and column matching
- `src/gams/gams_grammar.lark` - Allow STRING in dotted_label
- `tests/unit/gams/test_parser.py` - Added 3 regression tests
- `tests/unit/test_special_identifiers.py` - Updated expectations for unquoted headers
- `tests/unit/test_multiple_alias_declaration.py` - Updated for quote stripping
