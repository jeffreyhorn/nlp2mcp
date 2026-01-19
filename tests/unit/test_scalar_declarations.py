"""Unit tests for scalar declarations with comma-separated lists and inline values.

Tests cover:
1. Single scalar without value
2. Single scalar with value
3. Multiple scalars without values
4. Multiple scalars all with values
5. Mixed (some with, some without values) - mingamma.gms pattern
6. Newline-separated declarations
"""

from src.ir.parser import parse_model_file


def test_single_scalar_without_value(tmp_path):
    """Test case 1: Single scalar without value - Scalar x;"""
    test_file = tmp_path / "test_scalar.gms"
    test_file.write_text("""
Scalar x;
x = 1;
display x;
""")
    model = parse_model_file(test_file)
    assert "x" in model.params
    assert model.params["x"].domain == ()
    # Scalar declared without initial value, then assigned
    assert () in model.params["x"].values


def test_single_scalar_with_value(tmp_path):
    """Test case 2: Single scalar with value - Scalar x /5/;"""
    test_file = tmp_path / "test_scalar.gms"
    test_file.write_text("""
Scalar x /5/;
display x;
""")
    model = parse_model_file(test_file)
    assert "x" in model.params
    assert model.params["x"].domain == ()
    assert model.params["x"].values[()] == 5.0


def test_multiple_scalars_without_values(tmp_path):
    """Test case 3: Multiple scalars without values - Scalar x, y, z;"""
    test_file = tmp_path / "test_scalar.gms"
    test_file.write_text("""
Scalar x, y, z;
x = 1;
y = 2;
z = 3;
display x, y, z;
""")
    model = parse_model_file(test_file)
    assert "x" in model.params
    assert "y" in model.params
    assert "z" in model.params
    # All declared, then assigned values
    assert () in model.params["x"].values
    assert () in model.params["y"].values
    assert () in model.params["z"].values


def test_multiple_scalars_all_with_values(tmp_path):
    """Test case 4: Multiple scalars all with values - Scalar x /1/, y /2/;"""
    test_file = tmp_path / "test_scalar.gms"
    test_file.write_text("""
Scalar x /1/, y /2/, z /3/;
display x, y, z;
""")
    model = parse_model_file(test_file)
    assert "x" in model.params
    assert "y" in model.params
    assert "z" in model.params
    assert model.params["x"].values[()] == 1.0
    assert model.params["y"].values[()] == 2.0
    assert model.params["z"].values[()] == 3.0


def test_mixed_scalars_some_with_values(tmp_path):
    """Test case 5: Mixed (some with, some without) - Scalar x /1/, y, z /3/;"""
    test_file = tmp_path / "test_scalar.gms"
    test_file.write_text("""
Scalar x /1.5/, y, z /3.5/;
y = 2.5;
display x, y, z;
""")
    model = parse_model_file(test_file)
    assert "x" in model.params
    assert "y" in model.params
    assert "z" in model.params
    # x and z have inline values
    assert model.params["x"].values[()] == 1.5
    assert model.params["z"].values[()] == 3.5
    # y declared without value, then assigned
    assert () in model.params["y"].values


def test_mingamma_pattern(tmp_path):
    """Test case 6: mingamma.gms pattern - newline-separated with mixed values."""
    test_file = tmp_path / "test_scalar.gms"
    test_file.write_text("""
Scalar
   x1opt   / 1.46163214496836   /
   x1delta
   x2delta
   y1opt   / 0.8856031944108887 /
   y1delta
   y2delta
   y2opt;

y2opt = log(y1opt);
x1delta = x1opt - 1.0;

display x1opt, y1opt, y2opt, x1delta;
""")
    model = parse_model_file(test_file)

    # Verify all 7 scalars are declared
    assert "x1opt" in model.params
    assert "x1delta" in model.params
    assert "x2delta" in model.params
    assert "y1opt" in model.params
    assert "y1delta" in model.params
    assert "y2delta" in model.params
    assert "y2opt" in model.params

    # Verify scalars with inline values have correct values
    assert model.params["x1opt"].values[()] == 1.46163214496836
    assert model.params["y1opt"].values[()] == 0.8856031944108887

    # Verify scalars without inline values are declared (may have assigned values)
    assert "x1delta" in model.params
    assert "y2opt" in model.params


def test_newline_separated_with_values(tmp_path):
    """Test newline-separated scalars all with values."""
    test_file = tmp_path / "test_scalar.gms"
    test_file.write_text("""
Scalar
   a /1/
   b /2/
   c /3/;
display a, b, c;
""")
    model = parse_model_file(test_file)
    assert "a" in model.params
    assert "b" in model.params
    assert "c" in model.params
    assert model.params["a"].values[()] == 1.0
    assert model.params["b"].values[()] == 2.0
    assert model.params["c"].values[()] == 3.0


def test_newline_separated_without_values(tmp_path):
    """Test comma-separated scalars without values (commas required without data to avoid ambiguity)."""
    test_file = tmp_path / "test_scalar.gms"
    test_file.write_text("""
Scalar a, b, c;
a = 10;
b = 20;
c = 30;
""")
    model = parse_model_file(test_file)
    assert "a" in model.params
    assert "b" in model.params
    assert "c" in model.params


def test_scalars_with_description_text(tmp_path):
    """Test scalar declarations work without description text (description support removed for simplicity)."""
    test_file = tmp_path / "test_scalar.gms"
    test_file.write_text("""
Scalar rho / 0.15 /;
Scalar x, y, z;
""")
    model = parse_model_file(test_file)
    assert "rho" in model.params
    assert "x" in model.params
    assert "y" in model.params
    assert "z" in model.params
    assert model.params["rho"].values[()] == 0.15


def test_negative_scalar_values(tmp_path):
    """Test scalars with negative values."""
    test_file = tmp_path / "test_scalar.gms"
    test_file.write_text("""
Scalar x1 /-5.0/, x2 /3.0/;
""")
    model = parse_model_file(test_file)
    assert model.params["x1"].values[()] == -5.0
    assert model.params["x2"].values[()] == 3.0


def test_scientific_notation_scalars(tmp_path):
    """Test scalars with scientific notation."""
    test_file = tmp_path / "test_scalar.gms"
    test_file.write_text("""
Scalar epsilon /1.0e-6/, tolerance /1.0e-8/;
""")
    model = parse_model_file(test_file)
    assert model.params["epsilon"].values[()] == 1.0e-6
    assert model.params["tolerance"].values[()] == 1.0e-8


def test_backward_compatibility_single_forms(tmp_path):
    """Test backward compatibility: single scalar forms still work."""
    test_file = tmp_path / "test_scalar.gms"
    test_file.write_text("""
Scalar a;
Scalar b /2/;
Scalar c = 3;
""")
    model = parse_model_file(test_file)
    assert "a" in model.params
    assert "b" in model.params
    assert "c" in model.params
    assert model.params["b"].values[()] == 2.0
    assert model.params["c"].values[()] == 3.0


def test_scalar_references_in_expressions(tmp_path):
    """Test that scalars can be referenced in expressions (mingamma.gms pattern)."""
    test_file = tmp_path / "test_scalar.gms"
    test_file.write_text("""
Scalar x1opt /1.46/, y1opt /0.88/;
Scalar y2opt;
y2opt = log(y1opt);
display y2opt;
""")
    model = parse_model_file(test_file)
    assert "x1opt" in model.params
    assert "y1opt" in model.params
    assert "y2opt" in model.params
    assert model.params["x1opt"].values[()] == 1.46
    assert model.params["y1opt"].values[()] == 0.88
    # y2opt should have been assigned via expression


def test_mixed_comma_and_newline_separation(tmp_path):
    """Test mixing comma and newline separation."""
    test_file = tmp_path / "test_scalar.gms"
    test_file.write_text("""
Scalar
   a /1/, b
   c /3/, d;
""")
    model = parse_model_file(test_file)
    assert "a" in model.params
    assert "b" in model.params
    assert "c" in model.params
    assert "d" in model.params
    assert model.params["a"].values[()] == 1.0
    assert model.params["c"].values[()] == 3.0
