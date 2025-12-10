"""Tests for unquoted parameter descriptions (GitHub Issue #433).

GAMS allows unquoted text descriptions after parameter declarations.
This file tests parsing of both single-word and multi-word unquoted
descriptions for parameters.
"""

from src.ir.parser import parse_model_text


def test_single_word_description():
    """Test parameter with single-word unquoted description: t(i) partition"""
    source = """
Set i / a, b /;
Parameter t(i) partition;
"""
    model = parse_model_text(source)
    assert "t" in model.params


def test_multi_word_description():
    """Test parameter with multi-word unquoted description."""
    source = """
Set i / a, b /;
Parameter rho(i) roots of k-th degree Legendre polynomial;
"""
    model = parse_model_text(source)
    assert "rho" in model.params


def test_multi_line_parameter_block():
    """Test multi-line parameter block with mixed descriptions (from copspart.inc)."""
    source = """
Set nh / nh1 /;
Set nc / nc1 /;
Set nm / nm1 /;
Parameter t(nh)   partition
          rho(nc) roots of k-th degree Legendre polynomial
          itau(nm) "itau is the largest integer k";
"""
    model = parse_model_text(source)
    assert "t" in model.params
    assert "rho" in model.params
    assert "itau" in model.params


def test_scalar_parameter_with_single_word_description():
    """Test scalar parameter with single-word description."""
    source = """
Parameter alpha coefficient;
"""
    model = parse_model_text(source)
    assert "alpha" in model.params


def test_parameter_with_hyphenated_description():
    """Test parameter with hyphenated word in description."""
    source = """
Set i / a, b /;
Parameter x(i) k-th order coefficient;
"""
    model = parse_model_text(source)
    assert "x" in model.params


def test_parameter_with_quoted_description():
    """Test that quoted descriptions still work."""
    source = """
Set i / a, b /;
Parameter x(i) "quoted description with special chars!";
"""
    model = parse_model_text(source)
    assert "x" in model.params


def test_parameter_no_description():
    """Test parameter without any description."""
    source = """
Set i / a, b /;
Parameter x(i);
"""
    model = parse_model_text(source)
    assert "x" in model.params


def test_multiple_parameters_different_descriptions():
    """Test multiple parameters with different description styles."""
    source = """
Set i / a, b /;
Set j / c, d /;
Parameter
    alpha(i) cost coefficient
    beta(j) "demand level"
    gamma;
"""
    model = parse_model_text(source)
    assert "alpha" in model.params
    assert "beta" in model.params
    assert "gamma" in model.params
