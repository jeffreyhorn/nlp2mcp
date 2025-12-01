"""Unit tests for advanced table syntax features.

Tests advanced GAMS table features:
1. Multi-dimensional wildcards: Table(*,*)
2. Nested dot notation in row labels: low.a.subst
3. Sparse table data (empty cells/rows)

Related to GitHub Issue #359.
"""

from src.ir.parser import parse_text


def test_wildcard_tuple_two_dimensions():
    """Test Table(*,*) with two-dimensional wildcard."""
    source = """
    Table oil_constants(*,*) 'oil properties'
                C1      n
       SAE5   10.85  -3.91
       SAE10  10.45  -3.72
       SAE20  10.04  -3.55;
    """
    tree = parse_text(source)
    assert tree is not None
    # Table should have domain ('*', '*')
    # Will be inferred from data


def test_wildcard_tuple_three_dimensions():
    """Test Table(*,*,*) with three-dimensional wildcard."""
    source = """
    Table data(*,*,*) 'multi-dimensional data'
           col1  col2
    row1     1     2
    row2     3     4;
    """
    tree = parse_text(source)
    assert tree is not None


def test_nested_dot_notation_two_levels():
    """Test row labels with two-level dot notation: low.a"""
    source = """
    Set i / a, b /;
    Set j / x, y /;

    Table data(i,j)
          x    y
    low.a  1    2
    low.b  3    4
    high.a 5    6
    high.b 7    8;
    """
    tree = parse_text(source)
    assert tree is not None


def test_nested_dot_notation_three_levels():
    """Test row labels with three-level dot notation: low.a.subst"""
    source = """
    Set i / i1, i2 /;

    Table pdat(i,*) 'production data'
              i1     i2
    low.a.subst
    low.a.distr   0.915  0.944
    low.a.effic   3.83   3.24
    low.b.subst
    low.b.distr   0.276  1.034
    medium.a.subst 0.11  0.29
    medium.a.distr 0.326 0.443;
    """
    tree = parse_text(source)
    assert tree is not None


def test_nested_dot_notation_with_numbers():
    """Test dot notation with numbers in labels."""
    source = """
    Set i / col1, col2 /;

    Table data(i,*)
           col1  col2
    v1.0    1     2
    v2.1    3     4
    v10.5   5     6;
    """
    tree = parse_text(source)
    assert tree is not None


def test_sparse_table_empty_cells():
    """Test table with sparse data (missing values)."""
    source = """
    Set i / z, x, y /;

    Table io(i,i) 'input-output'
         z    x    y
    z   0.2  0.4  0.5
    x        0.3  0.1
    y             0.2;
    """
    tree = parse_text(source)
    assert tree is not None


def test_sparse_table_empty_rows():
    """Test table with completely empty rows."""
    source = """
    Set i / a, b, c, d /;

    Table data(i,i)
         a    b    c
    a    1    2    3
    b
    c         5    6
    d;
    """
    tree = parse_text(source)
    assert tree is not None


def test_bearing_gms_pattern():
    """Test actual pattern from bearing.gms."""
    source = """
    Table oil_constants(*,*) 'various oil grades'
                    C1      n
       'SAE 5'   10.85  -3.91
       'SAE 10'  10.45  -3.72
       'SAE 20'  10.04  -3.55
       'SAE 30'   9.88  -3.48
       'SAE 40'   9.64  -3.38
       'SAE 50'   9.37  -3.26;
    """
    tree = parse_text(source)
    assert tree is not None


def test_chenery_gms_pattern():
    """Test actual pattern from chenery.gms with nested dots."""
    source = """
    Set i / 'light-ind', 'food+agr', 'heavy-ind', services /;
    Set lmh / low, medium, high /;
    Set sde / subst, distr, effic /;

    Table pdat(lmh,*,sde,i) 'production data'
                        'light-ind'  'food+agr'  'heavy-ind'  services
       low.a.subst
       low.a.distr           .915      .944      2.60     .80
       low.a.effic          3.83      3.24       4.0     1.8
       low.b.subst
       low.b.distr           .276     1.034      2.60     .77
       low.b.effic          2.551     3.39       4.0     1.77
       medium.a.subst        .11       .29        .2      .05
       medium.a.distr        .326      .443       .991    .00798
       medium.a.effic       3.97      3.33       1.67    1.84;
    """
    tree = parse_text(source)
    assert tree is not None


def test_chem_gms_sparse_pattern():
    """Test actual sparse pattern from chem.gms."""
    source = """
    Set i / z, x, y, w, v /;

    Table io(i,i) 'input-output coefficients'
           z       x       y       w       v
    z             0.2     0.4     0.5     0.4
    x                     0.3     0.1
    y                             0.2     0.1
    w
    v;
    """
    tree = parse_text(source)
    assert tree is not None


def test_mixed_wildcard_and_explicit():
    """Test table with mix of wildcards and explicit domains."""
    source = """
    Set i / a, b /;

    Table data(i,*) 'mixed domain'
         col1  col2
    a      1     2
    b      3     4;
    """
    tree = parse_text(source)
    assert tree is not None


def test_wildcard_with_nested_dots():
    """Test combining wildcard domains with nested dot row labels."""
    source = """
    Table data(*,*)
           col1  col2
    a.x      1     2
    a.y      3     4
    b.x      5     6
    b.y      7     8;
    """
    tree = parse_text(source)
    assert tree is not None


def test_table_with_description_and_wildcards():
    """Test table with description string and wildcards."""
    source = """
    Table data(*,*) 'This is a description'
         x    y
    a    1    2
    b    3    4;
    """
    tree = parse_text(source)
    assert tree is not None


def test_single_wildcard_still_works():
    """Test that single wildcard (not tuple) still works."""
    source = """
    Set i / a, b /;

    Table data(i,*) 'single wildcard'
         col1  col2
    a      1     2
    b      3     4;
    """
    tree = parse_text(source)
    assert tree is not None


def test_empty_table_with_wildcards():
    """Test table with wildcard domains but no data rows (just headers)."""
    source = """
    Table data(*,*)
         col1  col2;
    """
    tree = parse_text(source)
    assert tree is not None


def test_table_with_only_headers():
    """Test table with only column headers, no data rows."""
    source = """
    Set i / a, b /;

    Table data(i,i)
         a    b;
    """
    tree = parse_text(source)
    assert tree is not None
