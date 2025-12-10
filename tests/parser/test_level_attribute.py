"""Tests for GAMS level attribute (.l) access parsing (GitHub Issue #432).

This file tests parsing of the .l attribute for GAMS variables, including:
- Setting and reading level values for scalar and indexed variables (LHS and RHS)
- Conditional assignment without parentheses (e.g., x.l(i)$cond(i) = value;)
- Other bound attributes (.lo, .up, .fx, .m)
"""

from src.ir.parser import parse_model_text


def test_level_attribute_lhs_scalar():
    """Test setting level attribute on scalar variable: x.l = 5;"""
    source = """
Variable x;
x.l = 5;
"""
    model = parse_model_text(source)
    assert "x" in model.variables


def test_level_attribute_lhs_indexed():
    """Test setting level attribute on indexed variable: x.l(i) = 5;"""
    source = """
Set i / a, b /;
Variable x(i);
x.l(i) = 5;
"""
    model = parse_model_text(source)
    assert "x" in model.variables


def test_level_attribute_rhs_scalar():
    """Test reading level attribute in expression: p = x.l * 2;"""
    source = """
Variable x;
x.l = 5;
Parameter p;
p = x.l * 2;
"""
    model = parse_model_text(source)
    assert "x" in model.variables
    assert "p" in model.params


def test_level_attribute_rhs_indexed():
    """Test reading level attribute with index: p(i) = x.l(i) * 2;"""
    source = """
Set i / a, b /;
Variable x(i);
x.l(i) = 5;
Parameter p(i);
p(i) = x.l(i) * 2;
"""
    model = parse_model_text(source)
    assert "x" in model.variables
    assert "p" in model.params


def test_level_attribute_in_complex_expression():
    """Test level attribute in complex expression like chenery.gms."""
    source = """
Set i / a, b /;
Variable vv(i), pi;
Parameter del(i) / a 0.5, b 0.5 /;
Parameter rho(i) / a 1, b 2 /;
pi.l = 3.5;
vv.l(i) = (pi.l * (1 - del(i)) / del(i)) ** (-rho(i) / (1 + rho(i)));
"""
    model = parse_model_text(source)
    assert "vv" in model.variables
    assert "pi" in model.variables


def test_conditional_assign_without_parens():
    """Test conditional assignment without parentheses: x.l(i)$sig(i) = value;"""
    source = """
Set i / a, b /;
Variable x(i);
Parameter sig(i) / a 1, b 0 /;
x.l(i)$sig(i) = 5;
"""
    model = parse_model_text(source)
    assert "x" in model.variables
    assert "sig" in model.params


def test_conditional_assign_with_parens():
    """Test conditional assignment with parentheses still works: x.l(i)$(sig(i)) = value;"""
    source = """
Set i / a, b /;
Variable x(i);
Parameter sig(i) / a 1, b 0 /;
x.l(i)$(sig(i) > 0) = 5;
"""
    model = parse_model_text(source)
    assert "x" in model.variables


def test_multiple_level_attributes_in_expression():
    """Test multiple level attributes in one expression: v.l(i) = pk.l*k.l(i) + plab*l.l(i);"""
    source = """
Set i / a, b /;
Variable v(i), pk, k(i), l(i);
Scalar plab / 1 /;
pk.l = 3.5;
k.l(i) = 1;
l.l(i) = 2;
v.l(i) = pk.l * k.l(i) + plab * l.l(i);
"""
    model = parse_model_text(source)
    assert "v" in model.variables
    assert "pk" in model.variables
    assert "k" in model.variables
    assert "l" in model.variables


def test_marginal_attribute_m():
    """Test .m (marginal) attribute access."""
    source = """
Variable x;
Parameter dual;
x.m = 0;
dual = x.m;
"""
    model = parse_model_text(source)
    assert "x" in model.variables
    assert "dual" in model.params


def test_other_bound_attributes():
    """Test other bound attributes (.lo, .up, .fx) in expressions."""
    source = """
Variable x;
Parameter lb, ub;
x.lo = 0;
x.up = 10;
lb = x.lo;
ub = x.up;
"""
    model = parse_model_text(source)
    assert "x" in model.variables
    assert "lb" in model.params
    assert "ub" in model.params
