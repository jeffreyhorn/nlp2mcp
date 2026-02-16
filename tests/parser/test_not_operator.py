"""Tests for GAMS not operator parsing (GitHub Issue #431).

The primary goal is to verify that the parser correctly parses the `not` operator.
Expression storage follows the existing mock/store approach where non-constant
expressions without function calls are parsed but not necessarily stored.
"""

from src.ir.ast import Binary, Const, Unary
from src.ir.parser import parse_model_text


def test_not_operator_basic():
    """Test basic not operator parses without error: ap(a) = not as(a);"""
    source = """
Set a / a1, a2 /;
Parameter as(a) / a1 1, a2 0 /;
Parameter ap(a);
ap(a) = not as(a);
"""
    # Main test: parsing should succeed without error
    model = parse_model_text(source)

    # Verify the parameter was declared
    assert "ap" in model.params
    assert "as" in model.params


def test_not_operator_case_insensitive():
    """Test NOT operator is case insensitive."""
    source = """
Set a / a1 /;
Parameter as(a) / a1 1 /;
Parameter ap(a);
ap(a) = NOT as(a);
"""
    # Should parse without error regardless of case
    model = parse_model_text(source)
    assert "ap" in model.params


def test_not_operator_with_constant():
    """Test not operator with constant: x = not 0;"""
    source = """
Scalar x;
x = not 0;
"""
    model = parse_model_text(source)

    assert "x" in model.params
    x = model.params["x"]

    # Scalar assignment with expression goes to expressions dict
    if x.expressions:
        expr = next(expr for k, expr in x.expressions if k == ())
        assert isinstance(expr, Unary)
        assert expr.op.lower() == "not"
        assert isinstance(expr.child, Const)


def test_not_operator_nested():
    """Test nested not operators: x = not not y;"""
    source = """
Scalar y / 1 /;
Scalar x;
x = not not y;
"""
    model = parse_model_text(source)

    assert "x" in model.params
    x = model.params["x"]

    if x.expressions:
        expr = next(expr for k, expr in x.expressions if k == ())
        assert isinstance(expr, Unary)
        assert expr.op.lower() == "not"
        assert isinstance(expr.child, Unary)
        assert expr.child.op.lower() == "not"


def test_not_operator_in_expression():
    """Test not operator in larger expression: x = (not a) and b;"""
    source = """
Scalar a / 1 /;
Scalar b / 1 /;
Scalar x;
x = (not a) and b;
"""
    model = parse_model_text(source)

    assert "x" in model.params
    x = model.params["x"]

    if x.expressions:
        expr = next(expr for k, expr in x.expressions if k == ())
        # Should be Binary(and, Unary(not, a), b)
        assert isinstance(expr, Binary)
        assert expr.op.lower() == "and"
        assert isinstance(expr.left, Unary)
        assert expr.left.op.lower() == "not"


def test_not_operator_precedence():
    """Test not operator precedence: x = not a or b (should be (not a) or b)."""
    source = """
Scalar a / 0 /;
Scalar b / 1 /;
Scalar x;
x = not a or b;
"""
    model = parse_model_text(source)

    assert "x" in model.params
    x = model.params["x"]

    if x.expressions:
        expr = next(expr for k, expr in x.expressions if k == ())
        # not has higher precedence than or, so: (not a) or b = Binary(or, Unary(not, a), b)
        assert isinstance(expr, Binary)
        assert expr.op.lower() == "or"
        assert isinstance(expr.left, Unary)
        assert expr.left.op.lower() == "not"


def test_not_operator_with_indexed_param():
    """Test not operator with indexed parameter reference."""
    source = """
Set i / i1, i2 /;
Parameter active(i) / i1 1, i2 0 /;
Parameter inactive(i);
inactive(i) = not active(i);
"""
    # Main test: parsing should succeed
    model = parse_model_text(source)

    assert "inactive" in model.params
    assert "active" in model.params


def test_not_operator_in_equation():
    """Test not operator in equation definition."""
    source = """
Set i / i1, i2 /;
Parameter flag(i) / i1 1, i2 0 /;
Positive Variable x(i);
x.lo(i) = 0;
x.up(i) = 10;

Equations eq1(i);
eq1(i).. x(i) =g= 5 * (not flag(i));
"""
    # Main test: parsing should succeed
    model = parse_model_text(source)
    assert "eq1" in model.equations


def test_not_operator_mixed_case():
    """Test not operator with MiXeD case."""
    source = """
Scalar a / 1 /;
Scalar x;
x = NoT a;
"""
    # Should parse without error
    model = parse_model_text(source)
    assert "x" in model.params
