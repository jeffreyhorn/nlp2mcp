"""
Integration tests for variable bounds with literal indices.

These tests verify that variable bounds with literal string indices
(e.g., x.up("1") = 100) are correctly handled, treating the literal
as a single index rather than expanding to all domain members.

This fixes the bug discovered in himmel16.gms where literal indices
were incorrectly expanded to ALL domain members.
"""

import pytest

from src.ir.parser import ParserSemanticError, parse_model_file


def test_variable_bound_literal_index(tmp_path):
    """Test that literal indices in variable bounds are treated as single values."""
    gams_code = """
Set i / 1*5 /;
Variable x(i);

x.l("1") = 0.5;
x.l("2") = 1.0;
x.up("3") = 100;
x.lo("4") = 0;
x.fx("5") = 2.5;
"""
    test_file = tmp_path / "test_literal_bounds.gms"
    test_file.write_text(gams_code)

    model = parse_model_file(test_file)

    # Verify variable exists
    assert "x" in model.variables
    var = model.variables["x"]
    assert var.domain == ("i",)

    # Verify bounds are set correctly for specific indices only
    # .l (level) bounds
    assert ("1",) in var.l_map
    assert var.l_map[("1",)] == 0.5
    assert ("2",) in var.l_map
    assert var.l_map[("2",)] == 1.0

    # .up (upper bound)
    assert ("3",) in var.up_map
    assert var.up_map[("3",)] == 100

    # .lo (lower bound)
    assert ("4",) in var.lo_map
    assert var.lo_map[("4",)] == 0

    # .fx (fixed value)
    assert ("5",) in var.fx_map
    assert var.fx_map[("5",)] == 2.5

    # Verify other indices are NOT set (bug was setting all indices)
    assert ("3",) not in var.l_map  # Only 1 and 2 have .l
    assert ("1",) not in var.up_map  # Only 3 has .up
    assert ("2",) not in var.lo_map  # Only 4 has .lo
    assert ("1",) not in var.fx_map  # Only 5 has .fx


def test_variable_bound_set_reference_index(tmp_path):
    """Test that set/alias references still expand correctly (no regression)."""
    gams_code = """
Set i / 1*3 /;
Alias (i, j);
Variable x(i);

x.fx(i) = 0;
"""
    test_file = tmp_path / "test_set_bounds.gms"
    test_file.write_text(gams_code)

    model = parse_model_file(test_file)

    # Verify variable exists
    assert "x" in model.variables
    var = model.variables["x"]

    # Verify ALL indices are set (set reference should expand)
    assert ("1",) in var.fx_map
    assert ("2",) in var.fx_map
    assert ("3",) in var.fx_map
    assert var.fx_map[("1",)] == 0
    assert var.fx_map[("2",)] == 0
    assert var.fx_map[("3",)] == 0


def test_variable_bound_mixed_literal_and_set(tmp_path):
    """Test mixed literal and set indices in multi-dimensional variables."""
    gams_code = """
Set i / 1*3 /;
Set j / a, b /;
Variable x(i, j);

* Literal for first index, set for second
x.up("1", j) = 100;

* Set for first index, literal for second
x.lo(i, "a") = 0;

* Both literals
x.fx("2", "b") = 5.0;
"""
    test_file = tmp_path / "test_mixed_bounds.gms"
    test_file.write_text(gams_code)

    model = parse_model_file(test_file)

    # Verify variable exists
    assert "x" in model.variables
    var = model.variables["x"]
    assert var.domain == ("i", "j")

    # x.up("1", j) should set ("1", "a") and ("1", "b") only
    assert ("1", "a") in var.up_map
    assert ("1", "b") in var.up_map
    assert ("2", "a") not in var.up_map  # Not set for other i values
    assert ("3", "a") not in var.up_map

    # x.lo(i, "a") should set ("1", "a"), ("2", "a"), ("3", "a")
    assert ("1", "a") in var.lo_map
    assert ("2", "a") in var.lo_map
    assert ("3", "a") in var.lo_map
    assert ("1", "b") not in var.lo_map  # Not set for other j values

    # x.fx("2", "b") should set only ("2", "b")
    assert ("2", "b") in var.fx_map
    assert var.fx_map[("2", "b")] == 5.0
    assert ("1", "b") not in var.fx_map
    assert ("2", "a") not in var.fx_map


def test_variable_bound_literal_validation(tmp_path):
    """Test that literal indices are validated against domain."""
    gams_code = """
Set i / 1*3 /;
Variable x(i);

x.up("invalid") = 100;
"""
    test_file = tmp_path / "test_invalid_literal.gms"
    test_file.write_text(gams_code)

    with pytest.raises(ParserSemanticError) as exc_info:
        parse_model_file(test_file)

    # Verify error message mentions literal not in domain
    error_msg = str(exc_info.value)
    assert "invalid" in error_msg or "not in domain" in error_msg.lower()


def test_himmel16_pattern(tmp_path):
    """
    Test the specific pattern from himmel16.gms that was failing.

    himmel16.gms uses x.l("1"), x.l("2"), etc. for initial values
    where x is declared over set i / 1*6 /.
    """
    gams_code = """
Set i / 1*6 /;

Variable
   x(i)
   y(i);

x.l("1") = 0;
x.l("2") = 0.5;
x.l("3") = 0.5;
x.l("4") = 0.5;
x.l("5") = 0;
x.l("6") = 0;

y.l("3") = 0.4;
y.l("4") = 0.8;
y.l("5") = 0.8;
y.l("6") = 0.4;
"""
    test_file = tmp_path / "test_himmel16_pattern.gms"
    test_file.write_text(gams_code)

    model = parse_model_file(test_file)

    # Verify x variable
    assert "x" in model.variables
    x = model.variables["x"]

    # Verify all specified x.l values are set
    assert x.l_map[("1",)] == 0
    assert x.l_map[("2",)] == 0.5
    assert x.l_map[("3",)] == 0.5
    assert x.l_map[("4",)] == 0.5
    assert x.l_map[("5",)] == 0
    assert x.l_map[("6",)] == 0

    # Verify y variable
    assert "y" in model.variables
    y = model.variables["y"]

    # Verify only specified y.l values are set (not all indices)
    assert ("1",) not in y.l_map
    assert ("2",) not in y.l_map
    assert y.l_map[("3",)] == 0.4
    assert y.l_map[("4",)] == 0.8
    assert y.l_map[("5",)] == 0.8
    assert y.l_map[("6",)] == 0.4


def test_variable_bound_quoted_string_literals(tmp_path):
    """Test literal indices with both single and double quotes."""
    gams_code = """
Set i / pellets, granular, powder /;
Variable x(i);

x.up("pellets") = 100;
x.lo('granular') = 10;
"""
    test_file = tmp_path / "test_quoted_literals.gms"
    test_file.write_text(gams_code)

    model = parse_model_file(test_file)

    assert "x" in model.variables
    var = model.variables["x"]

    # Both quote styles should work
    assert ("pellets",) in var.up_map
    assert var.up_map[("pellets",)] == 100

    assert ("granular",) in var.lo_map
    assert var.lo_map[("granular",)] == 10

    # powder should not be set
    assert ("powder",) not in var.up_map
    assert ("powder",) not in var.lo_map
