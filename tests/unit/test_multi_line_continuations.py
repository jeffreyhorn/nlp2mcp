"""Tests for multi-line continuation normalization in preprocessor.

Tests Issue #353: Newline as Implicit Separator
GAMS allows multi-line set/parameter declarations without trailing commas.

Tests Issue #364: Multi-line Parameter Data with Numeric Indices
GAMS allows table continuation markers (+) in multi-line table data.
"""

from src.ir.preprocessor import (
    normalize_multi_line_continuations,
    normalize_table_continuations,
)


def test_simple_set_without_commas():
    """Test basic set declaration with newlines but no commas."""
    source = """Set i /
    a
    b
    c
/;"""
    result = normalize_multi_line_continuations(source)
    expected = """Set i /
    a,
    b,
    c
/;"""
    assert result == expected


def test_set_with_existing_commas():
    """Test that existing commas are preserved."""
    source = """Set i /
    a,
    b,
    c
/;"""
    result = normalize_multi_line_continuations(source)
    # Should be unchanged since commas already present
    assert result == source


def test_set_with_descriptions():
    """Test set with inline descriptions and no commas."""
    source = """Set i /
    a "description a"
    b "description b"
    c "description c"
/;"""
    result = normalize_multi_line_continuations(source)
    expected = """Set i /
    a "description a",
    b "description b",
    c "description c"
/;"""
    assert result == expected


def test_parameter_without_commas():
    """Test parameter declaration without commas."""
    source = """Parameter p /
    a 1.0
    b 2.0
    c 3.0
/;"""
    result = normalize_multi_line_continuations(source)
    expected = """Parameter p /
    a 1.0,
    b 2.0,
    c 3.0
/;"""
    assert result == expected


def test_multiple_data_blocks():
    """Test multiple data blocks in same file."""
    source = """Set i /
    a
    b
/;

Set j /
    x
    y
/;"""
    result = normalize_multi_line_continuations(source)
    expected = """Set i /
    a,
    b
/;

Set j /
    x,
    y
/;"""
    assert result == expected


def test_inline_data_block():
    """Test inline data block (all on one line)."""
    source = """Set i / a, b, c /;"""
    result = normalize_multi_line_continuations(source)
    # Should be unchanged - no newlines to normalize
    assert result == source


def test_mixed_commas():
    """Test data block with some commas present."""
    source = """Set i /
    a, b
    c
    d
/;"""
    result = normalize_multi_line_continuations(source)
    expected = """Set i /
    a, b,
    c,
    d
/;"""
    assert result == expected


def test_comment_in_data_block():
    """Test that comments inside data blocks are preserved."""
    source = """Set i /
    a
    * This is a comment
    b
    c
/;"""
    result = normalize_multi_line_continuations(source)
    expected = """Set i /
    a,
    * This is a comment
    b,
    c
/;"""
    assert result == expected


def test_empty_lines_in_data_block():
    """Test that empty lines in data blocks are handled."""
    source = """Set i /
    a

    b
    c
/;"""
    result = normalize_multi_line_continuations(source)
    expected = """Set i /
    a,

    b,
    c
/;"""
    assert result == expected


def test_non_data_block_code():
    """Test that code outside data blocks is unchanged."""
    source = """Variables
    x
    y
    z
;

Set i / a, b, c /;"""
    result = normalize_multi_line_continuations(source)
    # Should be unchanged - Variables declaration is not a data block
    assert result == source


def test_chem_example():
    """Test actual example from chem.gms (GAMSLib 002)."""
    source = """Set i   plant   /  i-1
                       i-2  /"""
    result = normalize_multi_line_continuations(source)
    expected = """Set i   plant   /  i-1,
                       i-2  /"""
    assert result == expected


def test_water_example():
    """Test actual example from water.gms (GAMSLib 006)."""
    source = """Set c   city   / c-1
                     c-2
                     c-3  /"""
    result = normalize_multi_line_continuations(source)
    expected = """Set c   city   / c-1,
                     c-2,
                     c-3  /"""
    assert result == expected


# Tests for normalize_table_continuations


def test_table_continuation_basic():
    """Test removal of + continuation markers in table data."""
    source = """Table data(i,j)
           col1  col2
       +   col3  col4
       row1  1     2
       row2  3     4
;"""
    result = normalize_table_continuations(source)
    expected = """Table data(i,j)
           col1  col2
           col3  col4
       row1  1     2
       row2  3     4
;"""
    assert result == expected


def test_table_continuation_preserves_indentation():
    """Test that indentation is preserved when removing + markers."""
    source = """Table data(i,j)
       col1  col2
    +  col3  col4
    row1  1     2
;"""
    result = normalize_table_continuations(source)
    expected = """Table data(i,j)
       col1  col2
       col3  col4
    row1  1     2
;"""
    assert result == expected


def test_table_continuation_multiple_plus():
    """Test table with multiple + continuation lines."""
    source = """Table data(i,j)
       col1  col2
    +  col3  col4
    +  col5  col6
    row1  1     2
;"""
    result = normalize_table_continuations(source)
    expected = """Table data(i,j)
       col1  col2
       col3  col4
       col5  col6
    row1  1     2
;"""
    assert result == expected


def test_table_continuation_no_plus():
    """Test table without + continuation markers (should be unchanged)."""
    source = """Table data(i,j)
       col1  col2  col3
    row1  1     2     3
;"""
    result = normalize_table_continuations(source)
    assert result == source


def test_table_continuation_plus_outside_table():
    """Test that + outside table blocks is not affected."""
    source = """Set i / a, b, c /;

Table data(i,j)
       col1  col2
    +  col3  col4
;

* Some comment with + in it
Scalar x / 5 + 3 /;"""
    result = normalize_table_continuations(source)
    expected = """Set i / a, b, c /;

Table data(i,j)
       col1  col2
       col3  col4
;

* Some comment with + in it
Scalar x / 5 + 3 /;"""
    assert result == expected


def test_table_continuation_table_boundaries():
    """Test correct detection of table start and end boundaries."""
    source = """Table data1(i,j)
       col1  col2
    +  col3  col4
;

Set i / a, b /;

Table data2(i,j)
       col1  col2
    +  col3  col4
;"""
    result = normalize_table_continuations(source)
    expected = """Table data1(i,j)
       col1  col2
       col3  col4
;

Set i / a, b /;

Table data2(i,j)
       col1  col2
       col3  col4
;"""
    assert result == expected


def test_table_continuation_like_example():
    """Test actual example from like.gms."""
    source = """Table io(i,j)  'input-output coefficients'
                  light-ind  food+agr  heavy-ind
    +             services   coal
    light-ind     .0         .0        .0
;"""
    result = normalize_table_continuations(source)
    expected = """Table io(i,j)  'input-output coefficients'
                  light-ind  food+agr  heavy-ind
                  services   coal
    light-ind     .0         .0        .0
;"""
    assert result == expected


def test_table_continuation_empty_lines():
    """Test table with empty lines (should be preserved)."""
    source = """Table data(i,j)
       col1  col2

    +  col3  col4
    row1  1     2
;"""
    result = normalize_table_continuations(source)
    expected = """Table data(i,j)
       col1  col2

       col3  col4
    row1  1     2
;"""
    assert result == expected
