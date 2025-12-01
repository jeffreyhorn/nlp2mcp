"""Tests for predefined GAMS constants (Sprint 12 Day 4)."""

import math

import pytest

from src.ir.parser import ParseError, parse_model_text


def test_predefined_constant_pi():
    """Test that 'pi' is available as predefined constant."""
    source = """
    Variable x;
    Equation circle;
    circle.. x =e= pi;
    """
    model = parse_model_text(source)

    # Verify pi is in parameters
    assert "pi" in model.params
    assert model.params["pi"].domain == ()
    assert model.params["pi"].values[()] == math.pi


def test_predefined_constant_inf():
    """Test that 'inf' is available as predefined constant."""
    source = """
    Variable x;
    Equation unbounded;
    unbounded.. x =l= inf;
    """
    model = parse_model_text(source)

    # Verify inf is in parameters
    assert "inf" in model.params
    assert model.params["inf"].domain == ()
    assert model.params["inf"].values[()] == float("inf")


def test_predefined_constant_eps():
    """Test that 'eps' is available as predefined constant."""
    source = """
    Variable x;
    Equation tolerance;
    tolerance.. x =g= eps;
    """
    model = parse_model_text(source)

    # Verify eps is in parameters
    assert "eps" in model.params
    assert model.params["eps"].domain == ()
    assert abs(model.params["eps"].values[()] - 2.220446049250313e-16) < 1e-30


def test_predefined_constant_na():
    """Test that 'na' is available as predefined constant."""
    source = """
    Variable x;
    Equation missing_data;
    missing_data.. x =e= na;
    """
    model = parse_model_text(source)

    # Verify na is in parameters
    assert "na" in model.params
    assert model.params["na"].domain == ()
    assert math.isnan(model.params["na"].values[()])


def test_multiple_predefined_constants():
    """Test using multiple predefined constants in one equation."""
    source = """
    Variable x, y;
    Equation combo;
    combo.. x + y =e= pi + eps;
    """
    model = parse_model_text(source)

    # Verify all predefined constants exist
    assert "pi" in model.params
    assert "eps" in model.params


def test_predefined_constants_in_function():
    """Test predefined constants can be used in function calls."""
    source = """
    Variable aux1;
    Equation trigonometric;
    trigonometric.. aux1 =e= sin(4*pi);
    """
    model = parse_model_text(source)

    # Should parse without error
    assert "trigonometric" in model.equations


def test_predefined_constant_in_mod_function():
    """Test predefined constant 'pi' used in mod function (from fct.gms)."""
    source = """
    Variable aux1, aux1a;
    Equation defaux1a;
    defaux1a.. aux1a =e= abs(sin(4*mod(aux1,pi)));
    """
    model = parse_model_text(source)

    # Should parse without error (this was failing before)
    assert "defaux1a" in model.equations
    assert "pi" in model.params


def test_all_four_predefined_constants():
    """Test all four predefined constants are initialized."""
    source = """
    Variable x;
    """
    model = parse_model_text(source)

    # All four should exist even in minimal model
    assert "pi" in model.params
    assert "inf" in model.params
    assert "eps" in model.params
    assert "na" in model.params


def test_predefined_constant_case_sensitive():
    """Test that predefined constants are case-sensitive (lowercase only)."""
    source = """
    Variable x;
    Equation test;
    test.. x =e= PI;
    """
    # KNOWN LIMITATION: GAMS is case-insensitive, but our parser is case-sensitive.
    # Predefined constants must be referenced in lowercase (pi, inf, eps, na).
    # This is documented as a limitation that may be addressed in future sprints.
    with pytest.raises(ParseError, match="Undefined symbol 'PI'"):
        parse_model_text(source)
