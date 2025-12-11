"""Tests for GAMS signpower function parsing (Sprint 12 - Issue #453).

The signpower(x, y) function computes sign(x) * abs(x)^y.
"""

from src.ir.parser import parse_model_text


class TestSignpowerBasic:
    """Test basic signpower function parsing."""

    def test_signpower_simple(self):
        """Test basic signpower: signpower(x, 2)."""
        source = """
Variable x;
Equation eq;
eq.. signpower(x, 2) =e= 0;
"""
        model = parse_model_text(source)
        assert "eq" in model.equations

    def test_signpower_with_expression(self):
        """Test signpower with expression argument: signpower(x + y, 2)."""
        source = """
Variable x, y;
Equation eq;
eq.. signpower(x + y, 2) =e= 0;
"""
        model = parse_model_text(source)
        assert "eq" in model.equations

    def test_signpower_with_variable_exponent(self):
        """Test signpower with variable exponent: signpower(x, n)."""
        source = """
Variable x;
Scalar n /2/;
Equation eq;
eq.. signpower(x, n) =e= 0;
"""
        model = parse_model_text(source)
        assert "eq" in model.equations

    def test_signpower_fractional_exponent(self):
        """Test signpower with fractional exponent: signpower(x, 0.5)."""
        source = """
Variable x;
Equation eq;
eq.. signpower(x, 0.5) =e= 0;
"""
        model = parse_model_text(source)
        assert "eq" in model.equations


class TestSignpowerInExpressions:
    """Test signpower function in various expression contexts."""

    def test_signpower_in_sum(self):
        """Test signpower inside sum expression."""
        source = """
Set i /1*3/;
Variable x(i);
Equation eq;
eq.. sum(i, signpower(x(i), 2)) =e= 0;
"""
        model = parse_model_text(source)
        assert "eq" in model.equations

    def test_signpower_in_binop(self):
        """Test signpower in binary operation: signpower(x, 2) + y."""
        source = """
Variable x, y;
Equation eq;
eq.. signpower(x, 2) + y =e= 0;
"""
        model = parse_model_text(source)
        assert "eq" in model.equations

    def test_signpower_multiplied(self):
        """Test signpower multiplied: c * signpower(x, 2)."""
        source = """
Variable x;
Scalar c /1.5/;
Equation eq;
eq.. c * signpower(x, 2) =e= 0;
"""
        model = parse_model_text(source)
        assert "eq" in model.equations

    def test_signpower_nested(self):
        """Test nested signpower: signpower(signpower(x, 2), 0.5)."""
        source = """
Variable x;
Equation eq;
eq.. signpower(signpower(x, 2), 0.5) =e= 0;
"""
        model = parse_model_text(source)
        assert "eq" in model.equations


class TestSignpowerCaseInsensitive:
    """Test case insensitivity of signpower function."""

    def test_signpower_lowercase(self):
        """Test lowercase: signpower(x, 2)."""
        source = """
Variable x;
Equation eq;
eq.. signpower(x, 2) =e= 0;
"""
        model = parse_model_text(source)
        assert "eq" in model.equations

    def test_signpower_uppercase(self):
        """Test uppercase: SIGNPOWER(x, 2)."""
        source = """
Variable x;
Equation eq;
eq.. SIGNPOWER(x, 2) =e= 0;
"""
        model = parse_model_text(source)
        assert "eq" in model.equations

    def test_signpower_mixedcase(self):
        """Test mixed case: SignPower(x, 2)."""
        source = """
Variable x;
Equation eq;
eq.. SignPower(x, 2) =e= 0;
"""
        model = parse_model_text(source)
        assert "eq" in model.equations


class TestSignpowerIndexed:
    """Test signpower function with indexed variables."""

    def test_signpower_indexed_variable(self):
        """Test signpower with indexed variable: signpower(f(i), 2)."""
        source = """
Set i /1*3/;
Variable f(i);
Equation eq(i);
eq(i).. signpower(f(i), 2) =e= 0;
"""
        model = parse_model_text(source)
        assert "eq" in model.equations

    def test_signpower_multi_indexed(self):
        """Test signpower with multi-indexed variable: signpower(f(i,j), 2)."""
        source = """
Set i /1*3/, j /a, b/;
Variable f(i, j);
Equation eq(i, j);
eq(i, j).. signpower(f(i, j), 2) =e= 0;
"""
        model = parse_model_text(source)
        assert "eq" in model.equations

    def test_signpower_gastrans_style(self):
        """Test gastrans.gms style usage: signpower(f(ap,i,j), 2) =e= c2(ap,i,j)*(pi(i) - pi(j))."""
        source = """
Set i /1*3/, j /1*3/;
Alias(i, ap);
Variable f(ap, i, j), pi(i);
Parameter c2(ap, i, j);
Equation weymouthp(ap, i, j);
weymouthp(ap, i, j).. signpower(f(ap, i, j), 2) =e= c2(ap, i, j) * (pi(i) - pi(j));
"""
        model = parse_model_text(source)
        assert "weymouthp" in model.equations
