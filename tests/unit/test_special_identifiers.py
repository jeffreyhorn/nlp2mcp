"""Unit tests for special character identifier normalization.

Tests the normalize_special_identifiers() preprocessor function that quotes
identifiers containing hyphens (-) and plus signs (+) in data blocks to avoid
ambiguity with arithmetic operators.

Related to GitHub Issue #357.
"""

from src.ir.preprocessor import normalize_special_identifiers


def test_simple_hyphenated_identifier():
    """Test quoting a single identifier with hyphen."""
    source = "Set i / light-ind /;"
    expected = "Set i / 'light-ind' /;"
    assert normalize_special_identifiers(source) == expected


def test_simple_plus_identifier():
    """Test quoting a single identifier with plus sign."""
    source = "Set i / food+agr /;"
    expected = "Set i / 'food+agr' /;"
    assert normalize_special_identifiers(source) == expected


def test_multiple_special_identifiers():
    """Test quoting multiple identifiers with special characters."""
    source = "Set i / light-ind, food+agr, heavy-ind, services /;"
    expected = "Set i / 'light-ind', 'food+agr', 'heavy-ind', services /;"
    assert normalize_special_identifiers(source) == expected


def test_multiple_hyphens_in_identifier():
    """Test identifier with multiple hyphens."""
    source = "Set i / a-b-c, x-y-z /;"
    expected = "Set i / 'a-b-c', 'x-y-z' /;"
    assert normalize_special_identifiers(source) == expected


def test_multiple_plus_in_identifier():
    """Test identifier with multiple plus signs."""
    source = "Set i / a+b+c, x+y+z /;"
    expected = "Set i / 'a+b+c', 'x+y+z' /;"
    assert normalize_special_identifiers(source) == expected


def test_mixed_special_chars():
    """Test identifier with both hyphens and plus signs."""
    source = "Set i / a-b+c, x+y-z /;"
    expected = "Set i / 'a-b+c', 'x+y-z' /;"
    assert normalize_special_identifiers(source) == expected


def test_no_special_chars():
    """Test that normal identifiers are not quoted."""
    source = "Set i / a, b, c, services /;"
    expected = "Set i / a, b, c, services /;"
    assert normalize_special_identifiers(source) == expected


def test_already_quoted():
    """Test that already-quoted identifiers are not double-quoted."""
    source = "Set i / 'light-ind', \"food+agr\" /;"
    expected = "Set i / 'light-ind', \"food+agr\" /;"
    assert normalize_special_identifiers(source) == expected


def test_arithmetic_with_spaces():
    """Test that arithmetic expressions with spaces are preserved."""
    source = "x1 - 1"
    expected = "x1 - 1"
    assert normalize_special_identifiers(source) == expected


def test_arithmetic_subtraction():
    """Test that arithmetic subtraction outside data blocks is preserved."""
    source = "eq.. x1 - 1 =e= 0;"
    expected = "eq.. x1 - 1 =e= 0;"
    assert normalize_special_identifiers(source) == expected


def test_arithmetic_addition():
    """Test that arithmetic addition outside data blocks is preserved."""
    source = "eq.. x + y =e= z;"
    expected = "eq.. x + y =e= z;"
    assert normalize_special_identifiers(source) == expected


def test_multiline_data_block():
    """Test quoting identifiers in multi-line data block."""
    source = """Set i /
    light-ind
    food+agr
    heavy-ind
/;"""
    expected = """Set i /
    'light-ind'
    'food+agr'
    'heavy-ind'
/;"""
    assert normalize_special_identifiers(source) == expected


def test_inline_data_block():
    """Test inline data block (both slashes on same line)."""
    source = "Set i / light-ind, food+agr /;"
    expected = "Set i / 'light-ind', 'food+agr' /;"
    assert normalize_special_identifiers(source) == expected


def test_parameter_data_block():
    """Test quoting in parameter data blocks."""
    source = """Parameter p /
    light-ind 100
    food+agr 200
/;"""
    expected = """Parameter p /
    'light-ind' 100
    'food+agr' 200
/;"""
    assert normalize_special_identifiers(source) == expected


def test_comment_preservation():
    """Test that comments are preserved."""
    source = """Set i /
    * This is a comment
    light-ind  * Another comment
    food+agr
/;"""
    expected = """Set i /
    * This is a comment
    'light-ind'  * Another comment
    'food+agr'
/;"""
    assert normalize_special_identifiers(source) == expected


def test_outside_data_block():
    """Test that identifiers outside data blocks are not quoted."""
    source = "Variable x1-ind;"
    expected = "Variable x1-ind;"
    assert normalize_special_identifiers(source) == expected


def test_chenery_example():
    """Test the actual example from chenery.gms."""
    source = "Set i 'sectors' / light-ind, food+agr, heavy-ind, services /;"
    expected = "Set i 'sectors' / 'light-ind', 'food+agr', 'heavy-ind', services /;"
    assert normalize_special_identifiers(source) == expected


def test_empty_data_block():
    """Test empty data block."""
    source = "Set i / /;"
    expected = "Set i / /;"
    assert normalize_special_identifiers(source) == expected


def test_numeric_values():
    """Test that numeric values are preserved."""
    source = "Parameter p / item-1 3.14, item-2 2.71 /;"
    expected = "Parameter p / 'item-1' 3.14, 'item-2' 2.71 /;"
    assert normalize_special_identifiers(source) == expected


def test_leading_hyphen():
    """Test identifiers starting with hyphen (should not be quoted)."""
    source = "Set i / -inf, +inf /;"
    expected = "Set i / -inf, +inf /;"
    # Leading - and + are not part of identifier, they're separate tokens
    assert normalize_special_identifiers(source) == expected


def test_trailing_hyphen():
    """Test identifier ending with hyphen."""
    source = "Set i / item- /;"
    # This is unusual but should be handled
    # Pattern requires char after -, so item- won't match
    expected = "Set i / item- /;"
    assert normalize_special_identifiers(source) == expected


def test_nested_data_blocks():
    """Test multiple data blocks in same file."""
    source = """Set i / light-ind, food+agr /;
Set j / raw-mat, fin-goods /;"""
    expected = """Set i / 'light-ind', 'food+agr' /;
Set j / 'raw-mat', 'fin-goods' /;"""
    assert normalize_special_identifiers(source) == expected


def test_data_block_with_descriptions():
    """Test data block with inline descriptions."""
    source = "Set i / light-ind 'Light industry', food+agr 'Food and agriculture' /;"
    expected = "Set i / 'light-ind' 'Light industry', 'food+agr' 'Food and agriculture' /;"
    assert normalize_special_identifiers(source) == expected


def test_table_header_special_chars():
    """Test that table column headers are NOT quoted (Issue #665).

    Column headers are kept unquoted because:
    1. Quoting would make the first header look like a table description
    2. The DESCRIPTION terminal matches multiple hyphenated words
    The parser handles unquoted hyphenated headers via DESCRIPTION token parsing.
    """
    source = """Table aio(i,i)
       light-ind  food+agr  heavy-ind
food+agr      .1
heavy-ind     .2        .1;"""
    # Column headers should NOT be quoted; only row labels are quoted
    expected = """Table aio(i,i)
       light-ind  food+agr  heavy-ind
'food+agr'      .1
'heavy-ind'     .2        .1;"""
    assert normalize_special_identifiers(source) == expected


def test_table_row_labels_special_chars():
    """Test quoting special characters in table row labels (not headers).

    Issue #665: Column headers are NOT quoted, but row labels ARE quoted.
    """
    source = """Table data(i,j)
       col-1  col-2
row-1    1      2
row-2    3      4;"""
    # Column headers (col-1, col-2) NOT quoted; row labels (row-1, row-2) ARE quoted
    expected = """Table data(i,j)
       col-1  col-2
'row-1'    1      2
'row-2'    3      4;"""
    assert normalize_special_identifiers(source) == expected


def test_table_without_special_chars():
    """Test that normal table identifiers are not quoted."""
    source = """Table data(i,j)
       col1  col2
row1    1     2
row2    3     4;"""
    expected = """Table data(i,j)
       col1  col2
row1    1     2
row2    3     4;"""
    assert normalize_special_identifiers(source) == expected


def test_multi_line_set_declaration():
    """Test multi-line Set declaration with special chars (Issue #366)."""
    source = """Set
   i    'sectors'               / light-ind, food+agr, heavy-ind, services /
   t(i) 'tradables'             / light-ind, food+agr, heavy-ind /
   lmh  'possible elasticities' / low, medium, high /;"""
    expected = """Set
   i    'sectors'               / 'light-ind', 'food+agr', 'heavy-ind', services /
   t(i) 'tradables'             / 'light-ind', 'food+agr', 'heavy-ind' /
   lmh  'possible elasticities' / low, medium, high /;"""
    assert normalize_special_identifiers(source) == expected


def test_multi_line_parameter_declaration():
    """Test multi-line Parameter declaration with special chars."""
    source = """Parameter
   p(i) 'prices' / light-ind 100, food+agr 200 /
   q(i) 'quantities' / heavy-ind 50 /;"""
    expected = """Parameter
   p(i) 'prices' / 'light-ind' 100, 'food+agr' 200 /
   q(i) 'quantities' / 'heavy-ind' 50 /;"""
    assert normalize_special_identifiers(source) == expected


def test_multi_line_scalar_declaration():
    """Test multi-line Scalar declaration (edge case)."""
    source = """Scalar
   tax-rate 'tax rate' / 0.15 /
   sub-rate 'subsidy rate' / 0.05 /;"""
    expected = """Scalar
   'tax-rate' 'tax rate' / 0.15 /
   'sub-rate' 'subsidy rate' / 0.05 /;"""
    assert normalize_special_identifiers(source) == expected


def test_chenery_full_example():
    """Test the full chenery.gms Set declaration."""
    source = """Set
   i    'sectors'               / light-ind, food+agr, heavy-ind, services /
   t(i) 'tradables'             / light-ind, food+agr, heavy-ind /
   lmh  'possible elasticities' / low, medium, high /
   sde  'other parameters'      / subst, distr, effic /;"""
    expected = """Set
   i    'sectors'               / 'light-ind', 'food+agr', 'heavy-ind', services /
   t(i) 'tradables'             / 'light-ind', 'food+agr', 'heavy-ind' /
   lmh  'possible elasticities' / low, medium, high /
   sde  'other parameters'      / subst, distr, effic /;"""
    assert normalize_special_identifiers(source) == expected
