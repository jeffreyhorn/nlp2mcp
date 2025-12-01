"""Tests for table wildcard domain support (Issue #354).

GAMS allows wildcard * in table domain specifications to indicate
that dimension names should be inferred from table data.
"""

from src.ir.parser import parse_model_text


def test_table_wildcard_second_dimension():
    """Test table with wildcard in second dimension: (i,*)"""
    source = """
    Set i / a, b /;
    Table dat(i,*) 'basic data'
           y       z
      a    1.5     2.3
      b    4.2     5.1;
    """
    model = parse_model_text(source)
    assert "dat" in model.params
    # Wildcard domain is stored as "*"
    assert model.params["dat"].domain == ("i", "*")
    # Data should be present
    assert ("a", "y") in model.params["dat"].values
    assert model.params["dat"].values[("a", "y")] == 1.5
    assert model.params["dat"].values[("b", "z")] == 5.1


def test_table_wildcard_first_dimension():
    """Test table with wildcard in first dimension: (*,i)"""
    source = """
    Set i / x1, x2 /;
    Table data(*,i) 'data table'
             x1      x2
      y1     100     120
      y2     110     130;
    """
    model = parse_model_text(source)
    assert "data" in model.params
    assert model.params["data"].domain == ("*", "i")
    assert ("y1", "x1") in model.params["data"].values
    assert model.params["data"].values[("y1", "x1")] == 100
    assert model.params["data"].values[("y2", "x2")] == 130


def test_table_wildcard_both_dimensions():
    """Test table with wildcards in both dimensions: (*,*)"""
    source = """
    Table oil(*,*) 'oil properties'
               visc    dens
      oil1     0.5     0.9
      oil2     0.7     0.85;
    """
    model = parse_model_text(source)
    assert "oil" in model.params
    assert model.params["oil"].domain == ("*", "*")
    assert ("oil1", "visc") in model.params["oil"].values
    assert model.params["oil"].values[("oil1", "visc")] == 0.5
    assert model.params["oil"].values[("oil2", "dens")] == 0.85


def test_table_explicit_domain():
    """Test table with explicit domains still works"""
    source = """
    Set i / a, b /;
    Set j / x, y /;
    Table dat(i,j) 'data'
           x    y
      a    1    2
      b    3    4;
    """
    model = parse_model_text(source)
    assert "dat" in model.params
    assert model.params["dat"].domain == ("i", "j")
    assert model.params["dat"].values[("a", "x")] == 1


def test_table_wildcard_with_description():
    """Test wildcard table with description string"""
    source = """
    Table node(*,*) 'node properties and data'
           demand  height
      nw   1.2     6.5
      e    6.0     3.25;
    """
    model = parse_model_text(source)
    assert "node" in model.params
    assert model.params["node"].domain == ("*", "*")
    assert ("nw", "demand") in model.params["node"].values
    assert model.params["node"].values[("nw", "demand")] == 1.2


def test_table_wildcard_sparse_data():
    """Test wildcard table with sparse/missing values"""
    source = """
    Table sparse(*,*) 'sparse data'
           col1    col2    col3
      row1  1.0
      row2          2.0
      row3                  3.0;
    """
    model = parse_model_text(source)
    assert "sparse" in model.params
    # Missing values should be filled with 0.0
    assert model.params["sparse"].values[("row1", "col1")] == 1.0
    assert model.params["sparse"].values[("row1", "col2")] == 0.0
    assert model.params["sparse"].values[("row2", "col2")] == 2.0
    assert model.params["sparse"].values[("row3", "col3")] == 3.0


def test_water_node_table_pattern():
    """Test exact pattern from water.gms"""
    source = """
    Set n / nw, e, cc /;
    Table node(n,*) 'node data'
              demand  height  supply
      nw              6.50    2.500
      e               3.25    6.000
      cc     1.212    3.02;
    """
    model = parse_model_text(source)
    assert "node" in model.params
    assert model.params["node"].domain == ("n", "*")
    # Check some values
    assert ("nw", "height") in model.params["node"].values
    assert model.params["node"].values[("nw", "height")] == 6.50
    assert model.params["node"].values[("e", "supply")] == 6.000
    assert model.params["node"].values[("cc", "demand")] == 1.212
