"""Tests for special character identifiers (Sprint 12 Day 4 - Blocker #2)."""

import pytest

from src.ir.parser import parse_model_text


def test_hyphen_in_identifier():
    """Test that hyphens are allowed in identifiers."""
    source = """
    Set i / light-ind, heavy-ind /;
    """
    model = parse_model_text(source)
    
    assert "i" in model.sets
    assert "light-ind" in model.sets["i"].members
    assert "heavy-ind" in model.sets["i"].members


def test_plus_in_identifier():
    """Test that plus signs are allowed in identifiers."""
    source = """
    Set i / food+agr, manu+trade /;
    """
    model = parse_model_text(source)
    
    assert "i" in model.sets
    assert "food+agr" in model.sets["i"].members
    assert "manu+trade" in model.sets["i"].members


def test_mixed_special_chars_in_identifier():
    """Test identifiers with multiple special characters."""
    source = """
    Set i / light-ind, food+agr, heavy-ind /;
    """
    model = parse_model_text(source)
    
    assert "i" in model.sets
    assert len(model.sets["i"].members) == 3
    assert "light-ind" in model.sets["i"].members
    assert "food+agr" in model.sets["i"].members


def test_special_chars_in_variable_indexing():
    """Test that special char identifiers work in indexing."""
    source = """
    Set i / light-ind, food+agr /;
    Variable x(i);
    Equation balance(i);
    balance(i).. x(i) =e= 1;
    """
    model = parse_model_text(source)
    
    assert "i" in model.sets
    assert "x" in model.variables
    assert "balance" in model.equations


def test_special_chars_in_parameters():
    """Test special char identifiers in parameters."""
    source = """
    Set i / light-ind, food+agr /;
    Parameter a(i);
    """
    model = parse_model_text(source)
    
    assert "i" in model.sets
    assert "a" in model.params


def test_regular_arithmetic_still_works():
    """Test that normal arithmetic operations still parse correctly."""
    source = """
    Variable x, y;
    Equation sum_eq;
    sum_eq.. x + y =e= 10;
    """
    model = parse_model_text(source)
    
    # Should parse without treating "x + y" as identifier "x+y"
    assert "x" in model.variables
    assert "y" in model.variables
    assert "sum_eq" in model.equations


def test_subtraction_still_works():
    """Test that normal subtraction still parses correctly."""
    source = """
    Variable x, y;
    Equation diff_eq;
    diff_eq.. x - y =e= 5;
    """
    model = parse_model_text(source)
    
    assert "x" in model.variables
    assert "y" in model.variables
    assert "diff_eq" in model.equations


def test_chenery_style_identifiers():
    """Test the exact pattern from chenery.gms."""
    source = """
    Set i 'sectors' / light-ind, food+agr, heavy-ind, services /;
    Set t(i) 'tradables' / light-ind, food+agr, heavy-ind /;
    """
    model = parse_model_text(source)
    
    assert "i" in model.sets
    assert len(model.sets["i"].members) == 4
    assert "services" in model.sets["i"].members


def test_multiple_hyphens_in_identifier():
    """Test identifiers with multiple hyphens."""
    source = """
    Set i / north-east-region, south-west-region /;
    """
    model = parse_model_text(source)
    
    assert "north-east-region" in model.sets["i"].members
    assert "south-west-region" in model.sets["i"].members


def test_multiple_plus_in_identifier():
    """Test identifiers with multiple plus signs."""
    source = """
    Set i / sector+subsector+type /;
    """
    model = parse_model_text(source)
    
    assert "sector+subsector+type" in model.sets["i"].members
