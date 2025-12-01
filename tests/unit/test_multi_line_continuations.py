"""Tests for multi-line continuation normalization in preprocessor.

Tests Issue #353: Newline as Implicit Separator
GAMS allows multi-line set/parameter declarations without trailing commas.
"""

from src.ir.preprocessor import normalize_multi_line_continuations


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
