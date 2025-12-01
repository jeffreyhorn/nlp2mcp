"""
Unit tests for tuple notation in table row labels.

Tests support for GAMS tuple notation: (elem1,elem2,elem3).suffix
which expands to multiple rows with the same data.
"""

from src.ir.parser import parse_text


def test_basic_tuple_label():
    """Test basic tuple label with two elements."""
    source = """
    Set lmh / low, medium, high /;
    Set i / a, b /;

    Table data(lmh,i)
                 a    b
    (low,medium).x  1    2
    high.x          3    4;
    """
    tree = parse_text(source)
    assert tree is not None


def test_tuple_label_three_elements():
    """Test tuple label with three elements."""
    source = """
    Set lmh / low, medium, high /;
    Set i / col1, col2, col3 /;

    Table data(lmh,i)
                        col1  col2  col3
    (low,medium,high).x  100   200   300;
    """
    tree = parse_text(source)
    assert tree is not None


def test_mixed_tuple_and_regular_labels():
    """Test table with both tuple labels and regular labels."""
    source = """
    Set i / a, b, c, d /;
    Set j / col1, col2 /;

    Table data(i,j)
               col1  col2
    (a,b).x      1     2
    c.x          3     4
    d.y          5     6;
    """
    tree = parse_text(source)
    assert tree is not None


def test_chenery_gms_pattern_ynot():
    """Test actual pattern from chenery.gms with tuple label."""
    source = """
    Set lmh / low, medium, high /;
    Set i / 'light-ind', 'food+agr', 'heavy-ind', services /;

    Table ddat(lmh,*,i) 'demand parameters'
                                'light-ind'  'food+agr'  'heavy-ind'  services
       (low,medium,high).ynot        100          230         220          450
       medium.pelas                 -.674         -.246       -.587        -.352
       high.pelas                   -1            -1          -1           -1;
    """
    tree = parse_text(source)
    assert tree is not None


def test_chenery_gms_pattern_trade():
    """Test actual pattern from chenery.gms trade table with multiple tuple labels."""
    source = """
    Set lmh / low, medium, high /;
    Set t / 'light-ind', 'food+agr', 'heavy-ind' /;

    Table tdat(lmh,*,t) 'trade parameters'
                         'light-ind'  'food+agr'  'heavy-ind'
       medium.alp            .005         .001        .01
       high.alp              .0025        .0005       .00178
       (medium,high).gam    1.0          1.1         1.0
       (medium,high).xsi     .005         .0157       .00178;
    """
    tree = parse_text(source)
    assert tree is not None


def test_tuple_label_with_nested_suffix():
    """Test tuple label with multi-level dotted suffix."""
    source = """
    Set abc / a, b, c /;
    Set cols / c1, c2 /;

    Table data(abc,cols)
                c1   c2
    (a,b).x.y   10   20
    c.z         30   40;
    """
    tree = parse_text(source)
    assert tree is not None


def test_single_element_tuple():
    """Test tuple with single element (valid but unusual)."""
    source = """
    Set i / a, b /;
    Set j / c1, c2 /;

    Table data(i,j)
             c1  c2
    (a).x    1   2
    b.x      3   4;
    """
    tree = parse_text(source)
    assert tree is not None


def test_multiple_separate_tuple_labels():
    """Test multiple independent tuple labels in same table."""
    source = """
    Set i / a, b, c, d /;
    Set j / col1, col2 /;

    Table data(i,j)
             col1  col2
    (a,b).x   1     2
    (c,d).y   3     4;
    """
    tree = parse_text(source)
    assert tree is not None


def test_tuple_label_sparse_data():
    """Test tuple label with sparse data (some missing values)."""
    source = """
    Set i / a, b, c /;
    Set j / c1, c2, c3 /;

    Table data(i,j)
                   c1    c2    c3
    (a,b,c).val    10          30;
    """
    tree = parse_text(source)
    assert tree is not None


def test_tuple_label_with_wildcards():
    """Test tuple labels in table with wildcard domains."""
    source = """
    Set lmh / low, medium, high /;

    Table data(lmh,*)
                      col1  col2
    (low,medium).x     1     2
    high.y             3     4;
    """
    tree = parse_text(source)
    assert tree is not None


def test_tuple_label_negative_values():
    """Test tuple labels with negative numeric values."""
    source = """
    Set i / a, b /;
    Set j / c1, c2 /;

    Table data(i,j)
              c1     c2
    (a,b).x  -1.5   -2.75;
    """
    tree = parse_text(source)
    assert tree is not None


def test_tuple_label_scientific_notation():
    """Test tuple labels with scientific notation values."""
    source = """
    Set i / a, b /;
    Set j / c1, c2 /;

    Table data(i,j)
              c1      c2
    (a,b).x  1.5e-3  2.0e+2;
    """
    tree = parse_text(source)
    assert tree is not None


def test_tuple_label_four_elements():
    """Test tuple label with four elements."""
    source = """
    Set i / a, b, c, d /;
    Set j / col /;

    Table data(i,j)
                    col
    (a,b,c,d).val   100;
    """
    tree = parse_text(source)
    assert tree is not None


def test_tuple_label_with_quoted_strings():
    """Test tuple labels with quoted string identifiers."""
    source = """
    Set i / 'light-ind', 'food+agr', 'heavy-ind' /;
    Set j / col1, col2 /;

    Table data(i,j)
                                    col1  col2
    ('light-ind','food+agr').val     10    20
    'heavy-ind'.other                30    40;
    """
    tree = parse_text(source)
    assert tree is not None


def test_full_chenery_table():
    """Test complete chenery.gms demand data table."""
    source = """
    Set lmh / low, medium, high /;
    Set i / 'light-ind', 'food+agr', 'heavy-ind', services /;

    Table ddat(lmh,*,i) 'demand parameters'
                                'light-ind'  'food+agr'  'heavy-ind'  services
       (low,medium,high).ynot        100          230         220          450
       medium.pelas                 -.674         -.246       -.587        -.352
       high.pelas                   -1            -1          -1           -1;
    """
    tree = parse_text(source)
    assert tree is not None
