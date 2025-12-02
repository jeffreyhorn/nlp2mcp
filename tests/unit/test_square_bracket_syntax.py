"""Unit tests for square bracket syntax in expressions.

Tests GAMS square bracket grouping [expr] as alternative to (expr).

Related to GitHub Issue #362.
"""

from src.ir.parser import parse_text


def test_basic_square_bracket_grouping():
    """Test simple square bracket grouping."""
    source = """
    Variable x;
    Equation eq;
    eq.. x =e= [1 + 2] * 3;
    """
    tree = parse_text(source)
    assert tree is not None


def test_square_brackets_with_subtraction():
    """Test square brackets with subtraction."""
    source = """
    Variable x, y;
    Equation eq;
    eq.. x =e= [10 - 5] * 2;
    """
    tree = parse_text(source)
    assert tree is not None


def test_nested_square_brackets():
    """Test nested square brackets."""
    source = """
    Variable x;
    Equation eq;
    eq.. x =e= [[1 + 2] * 3];
    """
    tree = parse_text(source)
    assert tree is not None


def test_mixed_brackets_and_parens():
    """Test mixing square brackets and parentheses."""
    source = """
    Variable x;
    Equation eq;
    eq.. x =e= (1 + [2 * 3]) * 4;
    """
    tree = parse_text(source)
    assert tree is not None


def test_square_brackets_in_complex_expr():
    """Test square brackets in complex mathematical expression."""
    source = """
    Variable x, y, z;
    Equation eq;
    eq.. x =e= [y + z] / [y - z];
    """
    tree = parse_text(source)
    assert tree is not None


def test_square_brackets_with_functions():
    """Test square brackets with function calls."""
    source = """
    Variable x;
    Equation eq;
    eq.. x =e= sqr([x + 1]);
    """
    tree = parse_text(source)
    assert tree is not None


def test_bearing_gms_pattern():
    """Test actual pattern from bearing.gms."""
    source = """
    Variable Ef, h, N, mu, r, r0;
    Scalar pi;

    Equation friction;
    friction.. Ef*h =e= sqr(2*pi*N/60)*[(2*pi*mu)]*(r**4 - r0**4)/4;
    """
    tree = parse_text(source)
    assert tree is not None


def test_multiple_square_bracket_groups():
    """Test multiple square bracket groups in one expression."""
    source = """
    Variable a, b, c, d;
    Equation eq;
    eq.. a =e= [b + c] * [c + d];
    """
    tree = parse_text(source)
    assert tree is not None


def test_square_brackets_with_division():
    """Test square brackets with division operator."""
    source = """
    Variable x, y;
    Equation eq;
    eq.. x =e= [x + y] / [x - y];
    """
    tree = parse_text(source)
    assert tree is not None


def test_square_brackets_with_power():
    """Test square brackets with exponentiation."""
    source = """
    Variable x;
    Equation eq;
    eq.. x =e= [x + 1]**2;
    """
    tree = parse_text(source)
    assert tree is not None


def test_deeply_nested_square_brackets():
    """Test deeply nested square brackets."""
    source = """
    Variable x;
    Equation eq;
    eq.. x =e= [[[x + 1] * 2] + 3];
    """
    tree = parse_text(source)
    assert tree is not None


def test_square_brackets_precedence():
    """Test that square brackets work like parentheses for precedence."""
    source = """
    Variable x;
    Equation eq;
    eq.. x =e= 1 + [2 * 3];
    """
    tree = parse_text(source)
    assert tree is not None


def test_empty_square_brackets_invalid():
    """Test that empty square brackets cause parse error."""
    source = """
    Variable x;
    Equation eq;
    eq.. x =e= [];
    """
    try:
        parse_text(source)
        raise AssertionError("Should have raised parse error for empty brackets")
    except Exception as e:
        # Expected to fail - verify it's not our AssertionError
        if isinstance(e, AssertionError):
            raise
        pass  # Expected parse error


def test_square_brackets_with_negation():
    """Test square brackets with unary minus."""
    source = """
    Variable x, y;
    Equation eq;
    eq.. x =e= -[y + 1];
    """
    tree = parse_text(source)
    assert tree is not None


def test_square_brackets_in_sum():
    """Test square brackets inside sum expression."""
    source = """
    Set i /1*3/;
    Variable x(i);
    Variable total;
    Equation eq;
    eq.. total =e= sum(i, [x(i) + 1]);
    """
    tree = parse_text(source)
    assert tree is not None
