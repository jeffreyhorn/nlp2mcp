"""Tests for GAMS option statement parsing (Sprint 8 Day 1)."""

from src.ir.parser import parse_model_text
from src.ir.symbols import OptionStatement


def test_single_integer_option():
    """Test single option with integer value: option limrow = 0;"""
    source = """
Set i /1*3/;
option limrow = 0;
Scalar x;
"""
    model = parse_model_text(source)

    assert len(model.option_statements) == 1
    opt_stmt = model.option_statements[0]
    assert isinstance(opt_stmt, OptionStatement)
    assert len(opt_stmt.options) == 1
    assert opt_stmt.options[0] == ("limrow", 0)
    assert opt_stmt.location is not None


def test_multi_option_statement():
    """Test multi-option statement: option limrow = 0, limcol = 0;"""
    source = """
Set i /1*3/;
option limrow = 0, limcol = 0;
Scalar x;
"""
    model = parse_model_text(source)

    assert len(model.option_statements) == 1
    opt_stmt = model.option_statements[0]
    assert len(opt_stmt.options) == 2
    assert opt_stmt.options[0] == ("limrow", 0)
    assert opt_stmt.options[1] == ("limcol", 0)


def test_boolean_on_off_option():
    """Test boolean option: option solprint = off;"""
    source = """
Set i /1*3/;
option solprint = off;
Scalar x;
"""
    model = parse_model_text(source)

    assert len(model.option_statements) == 1
    opt_stmt = model.option_statements[0]
    assert len(opt_stmt.options) == 1
    assert opt_stmt.options[0] == ("solprint", "off")


def test_case_insensitive_option():
    """Test case insensitivity: OPTION LimRow = 0;"""
    source = """
Set i /1*3/;
OPTION LimRow = 0;
Scalar x;
"""
    model = parse_model_text(source)

    assert len(model.option_statements) == 1
    opt_stmt = model.option_statements[0]
    assert len(opt_stmt.options) == 1
    # Option name should preserve case from source
    assert opt_stmt.options[0] == ("LimRow", 0)


def test_decimals_option():
    """Test decimals option: option decimals = 8;"""
    source = """
Set i /1*3/;
option decimals = 8;
Scalar x;
"""
    model = parse_model_text(source)

    assert len(model.option_statements) == 1
    opt_stmt = model.option_statements[0]
    assert len(opt_stmt.options) == 1
    assert opt_stmt.options[0] == ("decimals", 8)


def test_multiple_option_statements():
    """Test multiple separate option statements."""
    source = """
Set i /1*3/;
option limrow = 0;
Scalar x;
option decimals = 8;
"""
    model = parse_model_text(source)

    assert len(model.option_statements) == 2
    assert model.option_statements[0].options[0] == ("limrow", 0)
    assert model.option_statements[1].options[0] == ("decimals", 8)


def test_options_keyword_plural():
    """Test 'options' keyword (plural form)."""
    source = """
Set i /1*3/;
options limrow = 0;
Scalar x;
"""
    model = parse_model_text(source)

    assert len(model.option_statements) == 1
    opt_stmt = model.option_statements[0]
    assert opt_stmt.options[0] == ("limrow", 0)


def test_option_with_on_keyword():
    """Test option with 'on' value."""
    source = """
Set i /1*3/;
option solprint = on;
Scalar x;
"""
    model = parse_model_text(source)

    assert len(model.option_statements) == 1
    opt_stmt = model.option_statements[0]
    assert opt_stmt.options[0] == ("solprint", "on")
