"""Tests for case-insensitive set member validation (GitHub Issue #435).

GAMS is case-insensitive, so set members like 'H' and 'h' should be treated
as equivalent when validating parameter data references.
"""

import pytest

from src.ir.parser import ParserSemanticError, parse_model_text


def test_lowercase_member_uppercase_set():
    """Test parameter data with lowercase member referencing uppercase set element."""
    source = """
Set i / A, B, C /;
Parameter p(i) / a 1, b 2, c 3 /;
"""
    model = parse_model_text(source)
    assert "p" in model.params
    assert model.params["p"].values[("a",)] == 1
    assert model.params["p"].values[("b",)] == 2
    assert model.params["p"].values[("c",)] == 3


def test_uppercase_member_lowercase_set():
    """Test parameter data with uppercase member referencing lowercase set element."""
    source = """
Set i / a, b, c /;
Parameter p(i) / A 1, B 2, C 3 /;
"""
    model = parse_model_text(source)
    assert "p" in model.params
    assert model.params["p"].values[("A",)] == 1
    assert model.params["p"].values[("B",)] == 2
    assert model.params["p"].values[("C",)] == 3


def test_mixed_case_members():
    """Test parameter data with mixed case members."""
    source = """
Set c / H, H2, H2O, N, N2, NH, NO, O, O2, OH /;
Parameter gibbs(c) / H -10.021, h2 -21.096, H2O -37.986, n -9.846, N2 -28.653,
                     NH -18.918, NO -28.032, O -14.640, o2 -30.594, OH -26.11 /;
"""
    model = parse_model_text(source)
    assert "gibbs" in model.params
    # Verify some values with different case patterns
    assert model.params["gibbs"].values[("H",)] == -10.021
    assert model.params["gibbs"].values[("h2",)] == -21.096  # lowercase key
    assert model.params["gibbs"].values[("o2",)] == -30.594  # lowercase key


def test_single_character_case_mismatch():
    """Test single character set members with case mismatch (like H vs h)."""
    source = """
Set i / H, N, O /;
Parameter mix(i) / h 2, n 1, o 1 /;
"""
    model = parse_model_text(source)
    assert "mix" in model.params
    assert model.params["mix"].values[("h",)] == 2


def test_case_insensitive_multi_dimensional():
    """Test case-insensitive matching with multi-dimensional parameters."""
    source = """
Set i / A, B /;
Set j / X, Y /;
Parameter p(i,j) / a.x 1, A.Y 2, b.X 3, B.y 4 /;
"""
    model = parse_model_text(source)
    assert "p" in model.params
    assert model.params["p"].values[("a", "x")] == 1
    assert model.params["p"].values[("A", "Y")] == 2
    assert model.params["p"].values[("b", "X")] == 3
    assert model.params["p"].values[("B", "y")] == 4


def test_exact_case_still_works():
    """Test that exact case matching still works."""
    source = """
Set i / alpha, beta, gamma /;
Parameter p(i) / alpha 1, beta 2, gamma 3 /;
"""
    model = parse_model_text(source)
    assert "p" in model.params
    assert model.params["p"].values[("alpha",)] == 1
    assert model.params["p"].values[("beta",)] == 2
    assert model.params["p"].values[("gamma",)] == 3


def test_invalid_member_still_errors():
    """Test that completely invalid members still raise errors."""
    source = """
Set i / A, B, C /;
Parameter p(i) / X 1 /;
"""
    with pytest.raises(ParserSemanticError, match="not present in set"):
        parse_model_text(source)
