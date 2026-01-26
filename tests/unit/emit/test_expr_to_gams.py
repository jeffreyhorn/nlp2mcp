"""Unit tests for AST to GAMS expression conversion.

Tests verify correct conversion of all AST node types to GAMS syntax,
including operator precedence, function calls, and MultiplierRef support.
"""

import pytest

from src.emit.expr_to_gams import _quote_indices, expr_to_gams
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
        """Test indexed variable reference.

        Single lowercase letters are domain variables and not quoted.
        """
        result = expr_to_gams(VarRef("x", ("i",)))
        assert result == "x(i)"

    def test_var_ref_multi_indexed(self):
        """Test multi-indexed variable reference.

        Single lowercase letters are domain variables and not quoted.
        """
        result = expr_to_gams(VarRef("x", ("i", "j", "k")))
        assert result == "x(i,j,k)"

    def test_param_ref_scalar(self):
        """Test scalar parameter reference."""
        result = expr_to_gams(ParamRef("c", ()))
        assert result == "c"

    def test_param_ref_indexed(self):
        """Test indexed parameter reference.

        Single lowercase letters are domain variables and not quoted.
        """
        result = expr_to_gams(ParamRef("c", ("i",)))
        assert result == "c(i)"

    def test_var_ref_element_label(self):
        """Test variable reference with element labels (not domain vars).

        Uppercase or digit-containing indices are element labels and should be quoted.
        """
        result = expr_to_gams(VarRef("x", ("H",)))
        assert result == 'x("H")'
        result = expr_to_gams(VarRef("x", ("H2",)))
        assert result == 'x("H2")'
        result = expr_to_gams(VarRef("x", ("i1",)))
        assert result == 'x("i1")'

    def test_var_ref_multi_letter_domain(self):
        """Test variable reference with multi-letter domain names.

        All-lowercase identifier names like 'nodes', 'years' are domain variables.
        """
        result = expr_to_gams(VarRef("flow", ("nodes",)))
        assert result == "flow(nodes)"
        result = expr_to_gams(VarRef("x", ("years",)))
        assert result == "x(years)"
        result = expr_to_gams(VarRef("y", ("flow_var",)))
        assert result == "y(flow_var)"

    def test_multiplier_ref_scalar(self):
        """Test scalar multiplier reference."""
        result = expr_to_gams(MultiplierRef("lambda_g1", ()))
        assert result == "lambda_g1"

    def test_multiplier_ref_indexed(self):
        """Test indexed multiplier reference.

        Single lowercase letters are domain variables and not quoted.
        """
        result = expr_to_gams(MultiplierRef("nu_balance", ("i",)))
        assert result == "nu_balance(i)"

    def test_multiplier_ref_element_label(self):
        """Test multiplier reference with element label (contains digit)."""
        result = expr_to_gams(MultiplierRef("nu_balance", ("i1",)))
        assert result == 'nu_balance("i1")'


@pytest.mark.unit
class TestUnaryOperators:
    """Test unary operators.

    Note: Unary minus is converted to multiplication form ((-1) * expr) to avoid
    GAMS Error 445 ("More than one operator in a row"). This happens when unary
    minus follows operators like ".." in equation definitions.
    """

    def test_unary_minus(self):
        """Test unary minus converts to multiplication form.

        GAMS Error 445 occurs when unary minus follows operators like ".."
        in equation definitions. Converting to ((-1) * expr) avoids this.
        """
        result = expr_to_gams(Unary("-", VarRef("x", ())))
        assert result == "((-1) * x)"

    def test_unary_plus(self):
        """Test unary plus passes through."""
        result = expr_to_gams(Unary("+", VarRef("x", ())))
        assert result == "+x"

    def test_unary_nested(self):
        """Test nested unary operators.

        Double negation becomes ((-1) * ((-1) * x)).
        """
        result = expr_to_gams(Unary("-", Unary("-", VarRef("x", ()))))
        assert result == "((-1) * ((-1) * x))"

    def test_unary_minus_negative_constant(self):
        """Test unary minus applied to a negative constant.

        -(-5) should become ((-1) * (-5)), not ((-1) * -5) which would
        have two operators in a row.
        """
        result = expr_to_gams(Unary("-", Const(-5)))
        assert result == "((-1) * (-5))"
        # Verify no "* -" pattern (two operators in a row)
        assert "* -" not in result

    def test_unary_minus_complex_expr(self):
        """Test unary minus on complex expression wraps the child.

        For Binary/Call children, the child is wrapped in parentheses
        to ensure correct mathematical interpretation.
        """
        # -(x + y) becomes ((-1) * (x + y))
        result = expr_to_gams(Unary("-", Binary("+", VarRef("x", ()), VarRef("y", ()))))
        assert result == "((-1) * (x + y))"

    def test_unary_minus_function_call(self):
        """Test unary minus on function call."""
        # -sin(x) becomes ((-1) * sin(x))
        result = expr_to_gams(Unary("-", Call("sin", (VarRef("x", ()),))))
        assert result == "((-1) * (sin(x)))"


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

    def test_multiplication_negative_right_operand(self):
        """Test that y * -1 becomes y * (-1) to avoid GAMS Error 445."""
        result = expr_to_gams(Binary("*", VarRef("y", ()), Const(-1)))
        assert result == "y * (-1)"

    def test_multiplication_negative_left_operand(self):
        """Test that -1 * y becomes (-1) * y to avoid GAMS Error 445."""
        result = expr_to_gams(Binary("*", Const(-1), VarRef("y", ())))
        assert result == "(-1) * y"

    def test_division_negative_right_operand(self):
        """Test that x / -2 becomes x / (-2) to avoid GAMS Error 445."""
        result = expr_to_gams(Binary("/", VarRef("x", ()), Const(-2)))
        assert result == "x / (-2)"

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
        """Test sum with single index set.

        Single lowercase letters are domain variables and not quoted.
        """
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
        """Test complementarity slack: -g(x) where g(x) = x - 10.

        Unary minus is converted to multiplication form ((-1) * (x - 10))
        to avoid GAMS Error 445.
        """
        expr = Unary("-", Binary("-", VarRef("x", ()), Const(10)))
        result = expr_to_gams(expr)
        # Unary minus converted to multiplication to avoid GAMS Error 445
        assert result == "((-1) * (x - 10))"


@pytest.mark.unit
class TestQuoteIndices:
    """Test the _quote_indices function for index quoting behavior.

    This function distinguishes between domain variables (unquoted) and
    element labels (quoted), and also handles indices that may already
    be quoted from the parser.
    """

    def test_single_lowercase_letter_not_quoted(self):
        """Single lowercase letters are domain variables, not quoted."""
        assert _quote_indices(("i",)) == ["i"]
        assert _quote_indices(("j",)) == ["j"]
        assert _quote_indices(("i", "j")) == ["i", "j"]

    def test_multi_letter_lowercase_not_quoted(self):
        """Multi-letter lowercase identifiers are domain variables, not quoted."""
        assert _quote_indices(("nodes",)) == ["nodes"]
        assert _quote_indices(("years",)) == ["years"]
        assert _quote_indices(("flow_var",)) == ["flow_var"]

    def test_element_labels_quoted(self):
        """Element labels (containing digits or uppercase) are quoted."""
        assert _quote_indices(("i1",)) == ['"i1"']
        assert _quote_indices(("H",)) == ['"H"']
        assert _quote_indices(("H2",)) == ['"H2"']
        assert _quote_indices(("H2O",)) == ['"H2O"']

    def test_mixed_indices(self):
        """Mixed domain variables and element labels."""
        assert _quote_indices(("i", "j1")) == ["i", '"j1"']
        assert _quote_indices(("nodes", "H2O")) == ["nodes", '"H2O"']

    def test_already_double_quoted_no_double_quoting(self):
        """Indices already quoted with double quotes should not be double-quoted.

        This is the main fix for GAMS Error 409 where parser stores
        indices like "demand" and emission would produce ""demand"".
        """
        assert _quote_indices(('"demand"',)) == ['"demand"']
        assert _quote_indices(('"x"',)) == ['"x"']
        assert _quote_indices(('"y"',)) == ['"y"']
        assert _quote_indices(('"x"', '"y"')) == ['"x"', '"y"']

    def test_already_single_quoted_no_double_quoting(self):
        """Indices already quoted with single quotes should be re-quoted with double quotes."""
        assert _quote_indices(("'demand'",)) == ['"demand"']
        assert _quote_indices(("'x'",)) == ['"x"']

    def test_quoted_lowercase_word_still_quoted(self):
        """A quoted string like "demand" (lowercase word) should stay quoted.

        Even though "demand" looks like a domain variable when unquoted,
        if it was explicitly quoted in the source, it's an element label.
        """
        # "demand" is stored as '"demand"' by the parser
        assert _quote_indices(('"demand"',)) == ['"demand"']

    def test_quoted_index_stays_quoted_even_if_looks_like_domain(self):
        """A quoted index stays quoted even if the inner value looks like a domain variable.

        If the original GAMS code had a quoted string like "i" or "nodes",
        it's an element label, not a domain variable - keep it quoted.
        """
        # Even though 'i' looks like a domain variable, "i" was explicitly quoted
        assert _quote_indices(('"i"',)) == ['"i"']
        assert _quote_indices(('"nodes"',)) == ['"nodes"']

    def test_param_ref_with_quoted_string_index(self):
        """Test ParamRef with a string literal index from the parser.

        This is the actual use case: dempr(g,"demand") parsed with "demand" stored.
        """
        # The parser stores the index including the quotes
        result = expr_to_gams(ParamRef("dempr", ("g", '"demand"')))
        assert result == 'dempr(g,"demand")'
        # Should NOT produce 'dempr(g,""demand"")'
        assert '""' not in result

    def test_var_ref_with_quoted_string_index(self):
        """Test VarRef with a string literal index."""
        result = expr_to_gams(VarRef("dat", ("i", '"y"')))
        assert result == 'dat(i,"y")'
        assert '""' not in result
