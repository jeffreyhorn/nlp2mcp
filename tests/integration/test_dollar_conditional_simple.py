"""
Simple tests for dollar conditional operator ($) support.
"""

import pytest

from src.ad.derivative_rules import differentiate_expr
from src.ad.evaluator import evaluate
from src.ir.ast import Const, DollarConditional, VarRef
from src.ir.parser import parse_model_text


@pytest.mark.integration
def test_parse_simple_dollar_conditional():
    """Parse and verify simple dollar conditional: x$y"""
    code = """
    Variables x, y, obj;
    Equations eq1, objdef;
    eq1.. obj =e= x$y;
    objdef.. obj =e= 0;
    Model test /all/;
    """
    model = parse_model_text(code)
    assert "eq1" in model.equations
    print("✓ Parsed x$y")


@pytest.mark.integration
def test_evaluate_dollar_conditional_true():
    """Evaluate x$y when y is non-zero (true)"""
    expr = DollarConditional(VarRef("x"), VarRef("y"))
    var_values = {("x", ()): 5.0, ("y", ()): 1.0}
    result = evaluate(expr, var_values=var_values)
    assert result == 5.0


@pytest.mark.integration
def test_evaluate_dollar_conditional_false():
    """Evaluate x$y when y is zero (false)"""
    expr = DollarConditional(VarRef("x"), VarRef("y"))
    var_values = {("x", ()): 5.0, ("y", ()): 0.0}
    result = evaluate(expr, var_values=var_values)
    assert result == 0.0


@pytest.mark.integration
def test_differentiate_dollar_conditional():
    """d/dx[x$y] = 1$y"""
    expr = DollarConditional(VarRef("x"), VarRef("y"))
    result = differentiate_expr(expr, "x")

    assert isinstance(result, DollarConditional)
    assert isinstance(result.value_expr, Const)
    assert result.value_expr.value == 1.0
    assert isinstance(result.condition, VarRef)
    assert result.condition.name == "y"
