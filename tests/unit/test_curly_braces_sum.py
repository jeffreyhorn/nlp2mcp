"""Tests for curly braces in sum/aggregation functions (Issue #355)."""

from src.ir.parser import parse_model_text


def test_sum_with_curly_braces():
    """Test sum{i, expr} syntax."""
    source = """
    Set i / a, b, c /;
    Variable x(i);
    Equation eq;
    eq.. sum{i, x(i)} =e= 10;
    """
    model = parse_model_text(source)
    assert "eq" in model.equations


def test_sum_with_parentheses_still_works():
    """Test sum(i, expr) syntax still works (backward compatibility)."""
    source = """
    Set i / a, b, c /;
    Variable x(i);
    Equation eq;
    eq.. sum(i, x(i)) =e= 10;
    """
    model = parse_model_text(source)
    assert "eq" in model.equations


def test_sum_multi_index_with_curly_braces():
    """Test sum{i, sum{j, expr}} syntax for multiple indices (nested)."""
    source = """
    Set i / a, b /;
    Set j / x, y /;
    Variable x(i,j);
    Equation eq;
    eq.. sum{i, sum{j, x(i,j)}} =e= 100;
    """
    model = parse_model_text(source)
    assert "eq" in model.equations


def test_nested_sum_mixed_brackets():
    """Test sum{i, sum(j, x(i,j))} - mixed brackets."""
    source = """
    Set i / a, b /;
    Set j / x, y /;
    Variable x(i,j);
    Equation eq;
    eq.. sum{i, sum(j, x(i,j))} =e= 50;
    """
    model = parse_model_text(source)
    assert "eq" in model.equations


def test_curly_braces_with_complex_expression():
    """Test curly braces with complex expressions inside."""
    source = """
    Set i / a, b, c /;
    Variable x(i);
    Variable y(i);
    Equation eq;
    eq.. sum{i, x(i)*2 + y(i)/3} =e= 100;
    """
    model = parse_model_text(source)
    assert "eq" in model.equations


def test_multiple_sums_with_curly_braces():
    """Test multiple sum expressions in same equation."""
    source = """
    Set i / a, b /;
    Set j / x, y /;
    Variable x(i);
    Variable y(j);
    Equation eq;
    eq.. sum{i, x(i)} + sum{j, y(j)} =e= 50;
    """
    model = parse_model_text(source)
    assert "eq" in model.equations


def test_curly_braces_backward_compatibility():
    """Test that existing parentheses syntax still works after adding curly braces."""
    source = """
    Set i / a, b /;
    Set j / x, y /;
    Variable x(i,j);
    Equation eq1, eq2;
    eq1.. sum(i, sum(j, x(i,j))) =e= 100;
    eq2.. sum{i, sum{j, x(i,j)}} =e= 100;
    """
    model = parse_model_text(source)
    assert "eq1" in model.equations
    assert "eq2" in model.equations
