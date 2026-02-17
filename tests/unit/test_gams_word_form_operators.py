"""Unit tests for GAMS word-form comparison operators (ne, eq, lt, gt, le, ge).

Issue #752: GAMS supports both symbolic (<>, <=, >=, <, >) and word-form
(ne, le, ge, lt, gt, eq) comparison operators. The grammar now accepts both
forms and the parser normalizes word forms to their symbolic equivalents.
"""

from src.ir.ast import Binary
from src.ir.parser import parse_model_text


class TestGAMSWordFormOperators:
    """Test that GAMS word-form comparison operators parse correctly."""

    def test_ne_operator(self):
        """Word-form `ne` parses as `<>` operator."""
        source = """
Set i / a, b /;
Parameter x(i) / a 1, b 0 /;
Parameter y(i);
y(i) = 1$(x(i) ne 0);
"""
        model = parse_model_text(source)
        assert "y" in model.params
        assert len(model.params["y"].expressions) > 0
        _key, expr = model.params["y"].expressions[0]
        assert _find_op(expr, "<>")

    def test_eq_operator(self):
        """Word-form `eq` parses as `=` operator."""
        source = """
Set i / a, b /;
Parameter x(i) / a 1, b 0 /;
Parameter y(i);
y(i) = 1$(x(i) eq 0);
"""
        model = parse_model_text(source)
        assert "y" in model.params
        assert len(model.params["y"].expressions) > 0
        _key, expr = model.params["y"].expressions[0]
        assert _find_op(expr, "=")

    def test_lt_operator(self):
        """Word-form `lt` parses as `<` operator."""
        source = """
Set i / a, b /;
Parameter x(i) / a 1, b 5 /;
Parameter y(i);
y(i) = 1$(x(i) lt 3);
"""
        model = parse_model_text(source)
        assert "y" in model.params
        assert len(model.params["y"].expressions) > 0
        _key, expr = model.params["y"].expressions[0]
        assert _find_op(expr, "<")

    def test_gt_operator(self):
        """Word-form `gt` parses as `>` operator."""
        source = """
Set i / a, b /;
Parameter x(i) / a 1, b 5 /;
Parameter y(i);
y(i) = 1$(x(i) gt 3);
"""
        model = parse_model_text(source)
        assert "y" in model.params
        assert len(model.params["y"].expressions) > 0
        _key, expr = model.params["y"].expressions[0]
        assert _find_op(expr, ">")

    def test_le_operator(self):
        """Word-form `le` parses as `<=` operator."""
        source = """
Set i / a, b /;
Parameter x(i) / a 1, b 5 /;
Parameter y(i);
y(i) = 1$(x(i) le 3);
"""
        model = parse_model_text(source)
        assert "y" in model.params
        assert len(model.params["y"].expressions) > 0
        _key, expr = model.params["y"].expressions[0]
        assert _find_op(expr, "<=")

    def test_ge_operator(self):
        """Word-form `ge` parses as `>=` operator."""
        source = """
Set i / a, b /;
Parameter x(i) / a 1, b 5 /;
Parameter y(i);
y(i) = 1$(x(i) ge 3);
"""
        model = parse_model_text(source)
        assert "y" in model.params
        assert len(model.params["y"].expressions) > 0
        _key, expr = model.params["y"].expressions[0]
        assert _find_op(expr, ">=")

    def test_case_insensitive(self):
        """Word-form operators are case-insensitive."""
        source = """
Set i / a /;
Parameter x(i) / a 1 /;
Parameter y(i);
y(i) = 1$(x(i) NE 0);
"""
        model = parse_model_text(source)
        assert "y" in model.params
        assert len(model.params["y"].expressions) > 0
        _key, expr = model.params["y"].expressions[0]
        assert _find_op(expr, "<>")

    def test_symbolic_operators_still_work(self):
        """Symbolic operators still work after adding word-form support."""
        source = """
Set i / a, b /;
Parameter x(i) / a 1, b 0 /;
Parameter y(i);
y(i) = 1$(x(i) <> 0);
"""
        model = parse_model_text(source)
        assert "y" in model.params
        assert len(model.params["y"].expressions) > 0
        _key, expr = model.params["y"].expressions[0]
        assert _find_op(expr, "<>")


def _find_op(expr, op: str) -> bool:
    """Recursively search an expression tree for a Binary node with the given op."""
    if isinstance(expr, Binary) and expr.op == op:
        return True
    for child in expr.children():
        if _find_op(child, op):
            return True
    return False
