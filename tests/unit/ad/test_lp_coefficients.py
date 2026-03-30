"""Tests for LP-specific coefficient extraction."""

from src.ad.lp_coefficients import extract_linear_coefficient
from src.ir.ast import Binary, Const, DollarConditional, ParamRef, Sum, Unary, VarRef


class TestExtractLinearCoefficient:
    """Test extract_linear_coefficient for various linear expression patterns."""

    def test_scalar_variable(self):
        """d/dx (x) = 1"""
        result = extract_linear_coefficient(VarRef("x", ()), "x", None)
        assert isinstance(result, Const) and result.value == 1.0

    def test_scalar_variable_mismatch(self):
        """d/dx (y) = 0"""
        result = extract_linear_coefficient(VarRef("y", ()), "x", None)
        assert isinstance(result, Const) and result.value == 0.0

    def test_constant(self):
        """d/dx (5) = 0"""
        result = extract_linear_coefficient(Const(5.0), "x", None)
        assert isinstance(result, Const) and result.value == 0.0

    def test_parameter(self):
        """d/dx (a) = 0"""
        result = extract_linear_coefficient(ParamRef("a", ()), "x", None)
        assert isinstance(result, Const) and result.value == 0.0

    def test_param_times_var(self):
        """d/dx (a*x) = a"""
        expr = Binary("*", ParamRef("a", ()), VarRef("x", ()))
        result = extract_linear_coefficient(expr, "x", None)
        assert isinstance(result, ParamRef) and result.name == "a"

    def test_var_times_param(self):
        """d/dx (x*a) = a"""
        expr = Binary("*", VarRef("x", ()), ParamRef("a", ()))
        result = extract_linear_coefficient(expr, "x", None)
        assert isinstance(result, ParamRef) and result.name == "a"

    def test_addition(self):
        """d/dx (a*x + b*y) = a"""
        expr = Binary(
            "+",
            Binary("*", ParamRef("a", ()), VarRef("x", ())),
            Binary("*", ParamRef("b", ()), VarRef("y", ())),
        )
        result = extract_linear_coefficient(expr, "x", None)
        assert isinstance(result, ParamRef) and result.name == "a"

    def test_subtraction(self):
        """d/dx (a*x - b*y) = a"""
        expr = Binary(
            "-",
            Binary("*", ParamRef("a", ()), VarRef("x", ())),
            Binary("*", ParamRef("b", ()), VarRef("y", ())),
        )
        result = extract_linear_coefficient(expr, "x", None)
        assert isinstance(result, ParamRef) and result.name == "a"

    def test_negation(self):
        """d/dx (-x) = -1"""
        expr = Unary("-", VarRef("x", ()))
        result = extract_linear_coefficient(expr, "x", None)
        assert isinstance(result, Unary) and result.op == "-"

    def test_unary_plus(self):
        """d/dx (+x) = 1"""
        expr = Unary("+", VarRef("x", ()))
        result = extract_linear_coefficient(expr, "x", None)
        assert isinstance(result, Const) and result.value == 1.0

    def test_division_by_constant(self):
        """d/dx (x/a) = 1/a"""
        expr = Binary("/", VarRef("x", ()), ParamRef("a", ()))
        result = extract_linear_coefficient(expr, "x", None)
        assert isinstance(result, Binary) and result.op == "/"

    def test_indexed_variable(self):
        """d/dx(i) x(i) = 1"""
        result = extract_linear_coefficient(VarRef("x", ("i",)), "x", ("i",))
        assert isinstance(result, Const) and result.value == 1.0

    def test_indexed_variable_mismatch(self):
        """d/dx(i) x(j) = 0"""
        result = extract_linear_coefficient(VarRef("x", ("j",)), "x", ("i",))
        assert isinstance(result, Const) and result.value == 0.0

    def test_sum_with_var(self):
        """d/dx sum(j, a(j)*x) = sum(j, a(j))"""
        expr = Sum(
            index_sets=("j",),
            body=Binary("*", ParamRef("a", ("j",)), VarRef("x", ())),
            condition=None,
        )
        result = extract_linear_coefficient(expr, "x", None)
        assert isinstance(result, Sum)
        assert isinstance(result.body, ParamRef) and result.body.name == "a"

    def test_dollar_conditional(self):
        """d/dx (x$cond) = 1$cond"""
        expr = DollarConditional(value_expr=VarRef("x", ()), condition=ParamRef("cond", ()))
        result = extract_linear_coefficient(expr, "x", None)
        assert isinstance(result, DollarConditional)

    def test_nonlinear_returns_zero(self):
        """d/dx (x*x) = 0 (non-linear, with warning)"""
        expr = Binary("*", VarRef("x", ()), VarRef("x", ()))
        result = extract_linear_coefficient(expr, "x", None)
        assert isinstance(result, Const) and result.value == 0.0
