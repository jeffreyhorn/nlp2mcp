"""Unit tests for AST to GAMS expression conversion.

Tests verify correct conversion of all AST node types to GAMS syntax,
including operator precedence, function calls, and MultiplierRef support.
"""

import pytest

from src.emit.expr_to_gams import expr_to_gams
from src.ir.ast import (
    Binary,
    Call,
    Const,
    MultiplierRef,
    ParamRef,
    Sum,
    SymbolRef,
    Unary,
    VarRef,
)


@pytest.mark.unit
class TestBasicNodes:
    """Test conversion of basic AST nodes."""

    def test_const_integer(self):
        """Test integer constant."""
        result = expr_to_gams(Const(42))
        assert result == "42"

    def test_const_float(self):
        """Test float constant."""
        result = expr_to_gams(Const(3.14))
        assert result == "3.14"

    def test_const_float_as_integer(self):
        """Test float that equals integer (should format as integer)."""
        result = expr_to_gams(Const(5.0))
        assert result == "5"

    def test_symbol_ref(self):
        """Test scalar symbol reference."""
        result = expr_to_gams(SymbolRef("x"))
        assert result == "x"

    def test_var_ref_scalar(self):
        """Test scalar variable reference."""
        result = expr_to_gams(VarRef("x", ()))
        assert result == "x"

    def test_var_ref_indexed(self):
        """Test indexed variable reference."""
        result = expr_to_gams(VarRef("x", ("i",)))
        assert result == "x(i)"

    def test_var_ref_multi_indexed(self):
        """Test multi-indexed variable reference."""
        result = expr_to_gams(VarRef("x", ("i", "j", "k")))
        assert result == "x(i,j,k)"

    def test_param_ref_scalar(self):
        """Test scalar parameter reference."""
        result = expr_to_gams(ParamRef("c", ()))
        assert result == "c"

    def test_param_ref_indexed(self):
        """Test indexed parameter reference."""
        result = expr_to_gams(ParamRef("c", ("i",)))
        assert result == "c(i)"

    def test_multiplier_ref_scalar(self):
        """Test scalar multiplier reference."""
        result = expr_to_gams(MultiplierRef("lambda_g1", ()))
        assert result == "lambda_g1"

    def test_multiplier_ref_indexed(self):
        """Test indexed multiplier reference."""
        result = expr_to_gams(MultiplierRef("nu_balance", ("i",)))
        assert result == "nu_balance(i)"


@pytest.mark.unit
class TestUnaryOperators:
    """Test unary operators."""

    def test_unary_minus(self):
        """Test unary minus."""
        result = expr_to_gams(Unary("-", VarRef("x", ())))
        assert result == "-x"

    def test_unary_plus(self):
        """Test unary plus."""
        result = expr_to_gams(Unary("+", VarRef("x", ())))
        assert result == "+x"

    def test_unary_nested(self):
        """Test nested unary operators."""
        result = expr_to_gams(Unary("-", Unary("-", VarRef("x", ()))))
        assert result == "--x"


@pytest.mark.unit
class TestBinaryOperators:
    """Test binary operators and precedence."""

    def test_addition(self):
        """Test addition."""
        result = expr_to_gams(Binary("+", Const(1), Const(2)))
        assert result == "1 + 2"

    def test_subtraction(self):
        """Test subtraction."""
        result = expr_to_gams(Binary("-", Const(5), Const(3)))
        assert result == "5 - 3"

    def test_multiplication(self):
        """Test multiplication."""
        result = expr_to_gams(Binary("*", Const(3), Const(4)))
        assert result == "3 * 4"

    def test_division(self):
        """Test division."""
        result = expr_to_gams(Binary("/", Const(10), Const(2)))
        assert result == "10 / 2"

    def test_power_operator(self):
        """Test power operator conversion to GAMS ** syntax."""
        result = expr_to_gams(Binary("^", VarRef("x", ()), Const(2)))
        assert result == "x ** 2"

    def test_power_with_variables(self):
        """Test power with variable exponent."""
        result = expr_to_gams(Binary("^", VarRef("x", ()), VarRef("n", ())))
        assert result == "x ** n"

    def test_comparison_eq(self):
        """Test equality comparison."""
        result = expr_to_gams(Binary("=", VarRef("x", ()), Const(0)))
        assert result == "x = 0"

    def test_comparison_lt(self):
        """Test less than comparison."""
        result = expr_to_gams(Binary("<", VarRef("x", ()), Const(10)))
        assert result == "x < 10"


@pytest.mark.unit
class TestOperatorPrecedence:
    """Test operator precedence and parenthesization."""

    def test_addition_then_multiplication(self):
        """Test (a + b) * c requires parens."""
        expr = Binary("*", Binary("+", Const(1), Const(2)), Const(3))
        result = expr_to_gams(expr)
        assert result == "(1 + 2) * 3"

    def test_multiplication_then_addition(self):
        """Test a * b + c doesn't need parens."""
        expr = Binary("+", Binary("*", Const(1), Const(2)), Const(3))
        result = expr_to_gams(expr)
        assert result == "1 * 2 + 3"

    def test_subtraction_associativity(self):
        """Test a - (b - c) needs parens."""
        expr = Binary("-", Const(10), Binary("-", Const(5), Const(2)))
        result = expr_to_gams(expr)
        assert result == "10 - (5 - 2)"

    def test_division_associativity(self):
        """Test a / (b / c) needs parens."""
        expr = Binary("/", Const(10), Binary("/", Const(5), Const(2)))
        result = expr_to_gams(expr)
        assert result == "10 / (5 / 2)"

    def test_power_associativity(self):
        """Test a ** (b ** c) needs parens."""
        expr = Binary("^", Const(2), Binary("^", Const(3), Const(2)))
        result = expr_to_gams(expr)
        assert result == "2 ** (3 ** 2)"

    def test_complex_expression(self):
        """Test complex nested expression."""
        # (a + b) * (c - d)
        expr = Binary(
            "*",
            Binary("+", VarRef("a", ()), VarRef("b", ())),
            Binary("-", VarRef("c", ()), VarRef("d", ())),
        )
        result = expr_to_gams(expr)
        assert result == "(a + b) * (c - d)"

    def test_power_in_addition(self):
        """Test x**2 + y**2 doesn't need parens."""
        expr = Binary(
            "+",
            Binary("^", VarRef("x", ()), Const(2)),
            Binary("^", VarRef("y", ()), Const(2)),
        )
        result = expr_to_gams(expr)
        assert result == "x ** 2 + y ** 2"


@pytest.mark.unit
class TestFunctionCalls:
    """Test function call conversion."""

    def test_call_single_arg(self):
        """Test function with single argument."""
        result = expr_to_gams(Call("exp", (VarRef("x", ()),)))
        assert result == "exp(x)"

    def test_call_multiple_args(self):
        """Test function with multiple arguments."""
        result = expr_to_gams(Call("power", (VarRef("x", ()), Const(2))))
        assert result == "power(x, 2)"

    def test_call_nested(self):
        """Test nested function calls."""
        inner = Call("log", (VarRef("x", ()),))
        result = expr_to_gams(Call("exp", (inner,)))
        assert result == "exp(log(x))"

    def test_common_functions(self):
        """Test common mathematical functions."""
        assert expr_to_gams(Call("sqrt", (VarRef("x", ()),))) == "sqrt(x)"
        assert expr_to_gams(Call("log", (VarRef("x", ()),))) == "log(x)"
        assert expr_to_gams(Call("sin", (VarRef("x", ()),))) == "sin(x)"
        assert expr_to_gams(Call("cos", (VarRef("x", ()),))) == "cos(x)"


@pytest.mark.unit
class TestSumExpression:
    """Test sum expression conversion."""

    def test_sum_single_index(self):
        """Test sum with single index set."""
        body = Binary("*", ParamRef("c", ("i",)), VarRef("x", ("i",)))
        result = expr_to_gams(Sum(("i",), body))
        assert result == "sum(i, c(i) * x(i))"

    def test_sum_multiple_indices(self):
        """Test sum with multiple index sets."""
        body = VarRef("x", ("i", "j"))
        result = expr_to_gams(Sum(("i", "j"), body))
        assert result == "sum((i,j), x(i,j))"

    def test_sum_nested(self):
        """Test nested sum expressions."""
        inner = Sum(("j",), VarRef("x", ("i", "j")))
        result = expr_to_gams(Sum(("i",), inner))
        assert result == "sum(i, sum(j, x(i,j)))"

    def test_sum_complex_body(self):
        """Test sum with complex body expression."""
        body = Binary(
            "+",
            Binary("*", ParamRef("a", ("i",)), VarRef("x", ("i",))),
            Binary("*", ParamRef("b", ("i",)), VarRef("y", ("i",))),
        )
        result = expr_to_gams(Sum(("i",), body))
        assert result == "sum(i, a(i) * x(i) + b(i) * y(i))"


@pytest.mark.unit
class TestComplexExpressions:
    """Test complex real-world expressions."""

    def test_quadratic_objective(self):
        """Test quadratic objective: x^2 + y^2."""
        expr = Binary(
            "+",
            Binary("^", VarRef("x", ()), Const(2)),
            Binary("^", VarRef("y", ()), Const(2)),
        )
        result = expr_to_gams(expr)
        assert result == "x ** 2 + y ** 2"

    def test_stationarity_equation(self):
        """Test stationarity equation with multipliers."""
        # 2*x + nu_balance
        expr = Binary(
            "+",
            Binary("*", Const(2), VarRef("x", ())),
            MultiplierRef("nu_balance", ()),
        )
        result = expr_to_gams(expr)
        assert result == "2 * x + nu_balance"

    def test_sum_with_power(self):
        """Test sum(i, a(i) * x(i)^2)."""
        body = Binary(
            "*",
            ParamRef("a", ("i",)),
            Binary("^", VarRef("x", ("i",)), Const(2)),
        )
        result = expr_to_gams(Sum(("i",), body))
        assert result == "sum(i, a(i) * x(i) ** 2)"

    def test_complementarity_slack(self):
        """Test complementarity slack: -g(x) where g(x) = x - 10."""
        expr = Unary("-", Binary("-", VarRef("x", ()), Const(10)))
        result = expr_to_gams(expr)
        # GAMS doesn't require parens here - unary minus distributes
        assert result == "-x - 10"
