"""Tests for GAMS option colon format syntax (Sprint 12 - Issue #446).

Tests the display format syntax: option identifier:d:r:c;
where:
  d = number of decimals
  r = characters for row labels
  c = characters for column labels
"""

from src.ir.parser import parse_model_text
from src.ir.symbols import OptionStatement


def test_option_format_single_number():
    """Test option format with single number: option arep:6;"""
    source = """
Set i /1*3/;
option arep:6;
Scalar x;
"""
    model = parse_model_text(source)

    assert len(model.option_statements) == 1
    opt_stmt = model.option_statements[0]
    assert isinstance(opt_stmt, OptionStatement)
    assert len(opt_stmt.options) == 1
    # Format options are stored as (name, [numbers])
    assert opt_stmt.options[0][0] == "arep"
    assert opt_stmt.options[0][1] == [6]


def test_option_format_two_numbers():
    """Test option format with two numbers: option arep:6:3;"""
    source = """
Set i /1*3/;
option arep:6:3;
Scalar x;
"""
    model = parse_model_text(source)

    assert len(model.option_statements) == 1
    opt_stmt = model.option_statements[0]
    assert len(opt_stmt.options) == 1
    assert opt_stmt.options[0][0] == "arep"
    assert opt_stmt.options[0][1] == [6, 3]


def test_option_format_three_numbers():
    """Test option format with three numbers: option arep:6:3:1;"""
    source = """
Set i /1*3/;
option arep:6:3:1;
Scalar x;
"""
    model = parse_model_text(source)

    assert len(model.option_statements) == 1
    opt_stmt = model.option_statements[0]
    assert len(opt_stmt.options) == 1
    assert opt_stmt.options[0][0] == "arep"
    assert opt_stmt.options[0][1] == [6, 3, 1]


def test_option_format_brep():
    """Test brep format option: option brep:5:2:2;"""
    source = """
Set i /1*3/;
option brep:5:2:2;
Scalar x;
"""
    model = parse_model_text(source)

    assert len(model.option_statements) == 1
    opt_stmt = model.option_statements[0]
    assert opt_stmt.options[0][0] == "brep"
    assert opt_stmt.options[0][1] == [5, 2, 2]


def test_option_format_mixed_with_equals():
    """Test mixing format and equals syntax: option limrow=0, arep:6;"""
    source = """
Set i /1*3/;
option limrow=0, arep:6;
Scalar x;
"""
    model = parse_model_text(source)

    assert len(model.option_statements) == 1
    opt_stmt = model.option_statements[0]
    assert len(opt_stmt.options) == 2
    assert opt_stmt.options[0] == ("limrow", 0)
    assert opt_stmt.options[1][0] == "arep"
    assert opt_stmt.options[1][1] == [6]


def test_option_format_multiple_formats():
    """Test multiple format options: option arep:6, brep:5;"""
    source = """
Set i /1*3/;
option arep:6, brep:5;
Scalar x;
"""
    model = parse_model_text(source)

    assert len(model.option_statements) == 1
    opt_stmt = model.option_statements[0]
    assert len(opt_stmt.options) == 2
    assert opt_stmt.options[0][0] == "arep"
    assert opt_stmt.options[0][1] == [6]
    assert opt_stmt.options[1][0] == "brep"
    assert opt_stmt.options[1][1] == [5]


def test_option_format_case_insensitive():
    """Test case insensitivity: OPTION AREP:6:3:1;"""
    source = """
Set i /1*3/;
OPTION AREP:6:3:1;
Scalar x;
"""
    model = parse_model_text(source)

    assert len(model.option_statements) == 1
    opt_stmt = model.option_statements[0]
    assert opt_stmt.options[0][0] == "AREP"
    assert opt_stmt.options[0][1] == [6, 3, 1]


def test_option_format_zero_decimals():
    """Test format with zero decimals: option arep:0;"""
    source = """
Set i /1*3/;
option arep:0;
Scalar x;
"""
    model = parse_model_text(source)

    assert len(model.option_statements) == 1
    opt_stmt = model.option_statements[0]
    assert opt_stmt.options[0][0] == "arep"
    assert opt_stmt.options[0][1] == [0]


def test_option_format_in_if_block():
    """Test format option inside if block parses correctly."""
    source = """
Set i /1*3/;
Scalar x /1/;
if(x > 0, option arep:6:3:1;);
"""
    model = parse_model_text(source)

    # Options inside if blocks are stored in conditional_statements, not option_statements
    assert len(model.conditional_statements) == 1
    cond_stmt = model.conditional_statements[0]
    assert len(cond_stmt.then_stmts) == 1
    # Verify the option_stmt tree was parsed with option_format
    assert cond_stmt.then_stmts[0].data == "option_stmt"


def test_option_format_in_loop():
    """Test format option inside loop parses correctly."""
    source = """
Set i /1*3/;
loop(i, option arep:6;);
"""
    model = parse_model_text(source)

    # Options inside loops are stored in loop_statements, not option_statements
    assert len(model.loop_statements) == 1
    loop_stmt = model.loop_statements[0]
    assert len(loop_stmt.body_stmts) == 1
    # Verify the option_stmt tree was parsed with option_format
    assert loop_stmt.body_stmts[0].data == "option_stmt"


def test_option_format_large_numbers():
    """Test format with larger numbers: option arep:15:20:25;"""
    source = """
Set i /1*3/;
option arep:15:20:25;
Scalar x;
"""
    model = parse_model_text(source)

    assert len(model.option_statements) == 1
    opt_stmt = model.option_statements[0]
    assert opt_stmt.options[0][0] == "arep"
    assert opt_stmt.options[0][1] == [15, 20, 25]


def test_option_format_crep():
    """Test crep format option: option crep:4:2:1;"""
    source = """
Set i /1*3/;
option crep:4:2:1;
Scalar x;
"""
    model = parse_model_text(source)

    assert len(model.option_statements) == 1
    opt_stmt = model.option_statements[0]
    assert opt_stmt.options[0][0] == "crep"
    assert opt_stmt.options[0][1] == [4, 2, 1]


def test_option_format_with_flag_option():
    """Test mixing format with flag option: option arep:6, clear;"""
    source = """
Set i /1*3/;
option arep:6, clear;
Scalar x;
"""
    model = parse_model_text(source)

    assert len(model.option_statements) == 1
    opt_stmt = model.option_statements[0]
    assert len(opt_stmt.options) == 2
    assert opt_stmt.options[0][0] == "arep"
    assert opt_stmt.options[0][1] == [6]
    assert opt_stmt.options[1] == ("clear", None)
