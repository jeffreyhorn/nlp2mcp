"""Tests for floor() function parsing (Issue #445).

The floor() function returns the largest integer less than or equal to x.
This was missing from the FUNCNAME terminal, blocking gasoil.gms parsing.
"""

from src.ir.parser import parse_text


class TestFloorFunctionBasic:
    """Test basic floor() function parsing."""

    def test_floor_simple(self):
        """Test floor with a simple number."""
        code = "Scalar x; x = floor(5.7);"
        tree = parse_text(code)
        assert tree is not None

    def test_floor_variable(self):
        """Test floor with a variable argument."""
        code = "Scalar x, y; x = 5.7; y = floor(x);"
        tree = parse_text(code)
        assert tree is not None

    def test_floor_negative(self):
        """Test floor with negative number."""
        code = "Scalar x; x = floor(-2.3);"
        tree = parse_text(code)
        assert tree is not None


class TestFloorFunctionExpressions:
    """Test floor() with various expressions."""

    def test_floor_with_division(self):
        """Test floor with division - the pattern from gasoil.gms."""
        code = "Scalar tau / 0.5 /, h / 0.1 /, result; result = floor(tau/h);"
        tree = parse_text(code)
        assert tree is not None

    def test_floor_with_multiplication(self):
        """Test floor with multiplication."""
        code = "Scalar x, y; x = floor(3.14 * 2);"
        tree = parse_text(code)
        assert tree is not None

    def test_floor_with_addition(self):
        """Test floor result in addition."""
        code = "Scalar x; x = floor(3.7) + 1;"
        tree = parse_text(code)
        assert tree is not None

    def test_floor_in_complex_expression(self):
        """Test floor in a complex expression."""
        code = "Scalar x; x = 2 * floor(5.5) + floor(3.3);"
        tree = parse_text(code)
        assert tree is not None


class TestFloorFunctionNested:
    """Test floor() nested with other functions."""

    def test_floor_in_min(self):
        """Test floor inside min() - pattern from gasoil.gms."""
        code = "Scalar x; x = min(50, floor(3.7) + 1);"
        tree = parse_text(code)
        assert tree is not None

    def test_floor_in_max(self):
        """Test floor inside max()."""
        code = "Scalar x; x = max(0, floor(-0.5));"
        tree = parse_text(code)
        assert tree is not None

    def test_nested_floor_ceil(self):
        """Test floor and ceil together."""
        code = "Scalar x; x = floor(ceil(3.2) / 2);"
        tree = parse_text(code)
        assert tree is not None

    def test_floor_of_sqrt(self):
        """Test floor of sqrt."""
        code = "Scalar x; x = floor(sqrt(10));"
        tree = parse_text(code)
        assert tree is not None


class TestFloorFunctionIndexed:
    """Test floor() with indexed expressions."""

    def test_floor_with_parameter_index(self):
        """Test floor with indexed parameter - pattern from gasoil.gms."""
        code = """
Set nm / 1*5 /;
Parameter tau(nm) / 1 0.1, 2 0.2, 3 0.3, 4 0.4, 5 0.5 /;
Scalar h / 0.1 /;
Parameter itau(nm);
itau(nm) = floor(tau(nm)/h);
"""
        tree = parse_text(code)
        assert tree is not None

    def test_floor_in_min_with_index(self):
        """Test floor in min with indexed parameter - exact gasoil.gms pattern."""
        code = """
Set nm / 1*3 /;
Parameter tau(nm) / 1 0.1, 2 0.2, 3 0.3 /;
Scalar h / 0.05 /;
Parameter itau(nm);
itau(nm) = min(50, floor(tau(nm)/h) + 1);
"""
        tree = parse_text(code)
        assert tree is not None


class TestFloorCaseInsensitive:
    """Test that floor is case-insensitive like other GAMS functions."""

    def test_floor_lowercase(self):
        """Test lowercase floor."""
        code = "Scalar x; x = floor(5.5);"
        tree = parse_text(code)
        assert tree is not None

    def test_floor_uppercase(self):
        """Test uppercase FLOOR."""
        code = "Scalar x; x = FLOOR(5.5);"
        tree = parse_text(code)
        assert tree is not None

    def test_floor_mixedcase(self):
        """Test mixed case Floor."""
        code = "Scalar x; x = Floor(5.5);"
        tree = parse_text(code)
        assert tree is not None
