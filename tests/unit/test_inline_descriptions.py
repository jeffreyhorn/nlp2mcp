"""Tests for inline descriptions in set member declarations.

GAMS allows inline descriptions for set members:
    Set i 'atoms' / H 'hydrogen', N 'nitrogen', O 'oxygen' /;
    Set n 'nodes' / nw 'north west reservoir',
                    e 'east reservoir',
                    ne 'north east reservoir' /;

This module tests that the parser correctly handles these patterns.
"""

from src.ir.parser import parse_model_text


def test_single_element_with_description():
    """Test set member with inline description."""
    source = """
    Set i 'atoms' / H 'hydrogen' /;
    """
    model = parse_model_text(source)
    assert "i" in model.sets
    assert "H" in model.sets["i"].members
    assert len(model.sets["i"].members) == 1


def test_multiple_elements_all_with_descriptions():
    """Test multiple set members all with inline descriptions."""
    source = """
    Set i 'atoms' / H 'hydrogen', N 'nitrogen', O 'oxygen' /;
    """
    model = parse_model_text(source)
    assert "i" in model.sets
    assert model.sets["i"].members == ["H", "N", "O"]


def test_mixed_elements_some_with_descriptions():
    """Test set with mixed descriptions (some elements have descriptions, some don't)."""
    source = """
    Set i / a, b 'beta', c, d 'delta' /;
    """
    model = parse_model_text(source)
    assert model.sets["i"].members == ["a", "b", "c", "d"]


def test_multi_line_with_descriptions():
    """Test multi-line set with descriptions (gastrans pattern)."""
    source = """
    Set n 'nodes' /
        nw 'north west reservoir',
        e 'east reservoir',
        ne 'north east reservoir',
        s 'south reservoir' /;
    """
    model = parse_model_text(source)
    assert len(model.sets["n"].members) == 4
    assert "nw" in model.sets["n"].members
    assert "e" in model.sets["n"].members
    assert "ne" in model.sets["n"].members
    assert "s" in model.sets["n"].members


def test_chem_exact_pattern():
    """Test exact pattern from chem.gms."""
    source = """
    Set i 'atoms' / H 'hydrogen', N 'nitrogen', O 'oxygen' /;
    """
    model = parse_model_text(source)
    assert model.sets["i"].members == ["H", "N", "O"]


def test_descriptions_with_special_chars():
    """Test descriptions containing special characters."""
    source = """
    Set i / a 'alpha (A)', b 'beta: B-value' /;
    """
    model = parse_model_text(source)
    assert len(model.sets["i"].members) == 2
    assert "a" in model.sets["i"].members
    assert "b" in model.sets["i"].members


def test_description_with_spaces():
    """Test description with multiple words separated by spaces."""
    source = """
    Set n / nw 'north west reservoir' /;
    """
    model = parse_model_text(source)
    assert "nw" in model.sets["n"].members


def test_empty_description():
    """Test element with empty string description."""
    source = """
    Set i / a '', b /;
    """
    model = parse_model_text(source)
    assert model.sets["i"].members == ["a", "b"]


def test_description_with_numbers():
    """Test description containing numbers."""
    source = """
    Set i / x 'option 1', y 'option 2' /;
    """
    model = parse_model_text(source)
    assert model.sets["i"].members == ["x", "y"]


def test_no_descriptions_still_works():
    """Test that sets without descriptions still work (backward compatibility)."""
    source = """
    Set i / a, b, c /;
    """
    model = parse_model_text(source)
    assert model.sets["i"].members == ["a", "b", "c"]


def test_range_with_description_after():
    """Test that range notation followed by element with description works."""
    source = """
    Set i / 1*5, a 'alpha' /;
    """
    model = parse_model_text(source)
    assert "1" in model.sets["i"].members
    assert "5" in model.sets["i"].members
    assert "a" in model.sets["i"].members


def test_description_before_range():
    """Test element with description before range notation."""
    source = """
    Set i / a 'alpha', 1*3 /;
    """
    model = parse_model_text(source)
    assert "a" in model.sets["i"].members
    assert "1" in model.sets["i"].members
    assert "3" in model.sets["i"].members
