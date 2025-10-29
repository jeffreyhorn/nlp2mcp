"""
Tests for AST Evaluator with NaN/Inf Detection (Day 2)

Test Coverage:
-------------
1. Basic expression evaluation
2. Indexed variable/parameter evaluation
3. Binary operations (+, -, *, /)
4. Unary operations (+, -)
5. Function calls (exp, log, sqrt, sin, cos, tan)
6. Division by zero detection
7. Domain violations (log of negative, sqrt of negative)
8. NaN detection
9. Inf detection
"""

import math

import pytest

from src.ad import EvaluationError, evaluate
from src.ir.ast import Binary, Call, Const, ParamRef, Unary, VarRef



pytestmark = pytest.mark.integration

@pytest.mark.integration
class TestBasicEvaluation:
    """Test basic expression evaluation."""

    def test_constant(self):
        """Evaluate a constant"""
        expr = Const(5.0)
        result = evaluate(expr)
        assert result == 5.0

    def test_variable(self):
        """Evaluate a variable with given value"""
        expr = VarRef("x")
        result = evaluate(expr, var_values={("x", ()): 3.0})
        assert result == 3.0

    def test_indexed_variable(self):
        """Evaluate indexed variable"""
        expr = VarRef("x", ("i",))
        result = evaluate(expr, var_values={("x", ("i",)): 7.0})
        assert result == 7.0

    def test_parameter(self):
        """Evaluate a parameter"""
        expr = ParamRef("c")
        result = evaluate(expr, param_values={("c", ()): 2.5})
        assert result == 2.5

    def test_indexed_parameter(self):
        """Evaluate indexed parameter"""
        expr = ParamRef("demand", ("i", "j"))
        result = evaluate(expr, param_values={("demand", ("i", "j")): 10.0})
        assert result == 10.0


@pytest.mark.integration
class TestBinaryOperations:
    """Test binary operation evaluation."""

    def test_addition(self):
        """Evaluate x + y"""
        expr = Binary("+", VarRef("x"), VarRef("y"))
        result = evaluate(expr, var_values={("x", ()): 3.0, ("y", ()): 4.0})
        assert result == 7.0

    def test_subtraction(self):
        """Evaluate x - y"""
        expr = Binary("-", VarRef("x"), VarRef("y"))
        result = evaluate(expr, var_values={("x", ()): 10.0, ("y", ()): 3.0})
        assert result == 7.0

    def test_multiplication(self):
        """Evaluate x * y"""
        expr = Binary("*", VarRef("x"), VarRef("y"))
        result = evaluate(expr, var_values={("x", ()): 6.0, ("y", ()): 7.0})
        assert result == 42.0

    def test_division(self):
        """Evaluate x / y"""
        expr = Binary("/", VarRef("x"), VarRef("y"))
        result = evaluate(expr, var_values={("x", ()): 10.0, ("y", ()): 2.0})
        assert result == 5.0

    def test_power(self):
        """Evaluate x ^ y"""
        expr = Binary("^", VarRef("x"), VarRef("y"))
        result = evaluate(expr, var_values={("x", ()): 2.0, ("y", ()): 3.0})
        assert result == 8.0


@pytest.mark.integration
class TestUnaryOperations:
    """Test unary operation evaluation."""

    def test_unary_plus(self):
        """Evaluate +x"""
        expr = Unary("+", VarRef("x"))
        result = evaluate(expr, var_values={("x", ()): 5.0})
        assert result == 5.0

    def test_unary_minus(self):
        """Evaluate -x"""
        expr = Unary("-", VarRef("x"))
        result = evaluate(expr, var_values={("x", ()): 5.0})
        assert result == -5.0

    def test_double_negation(self):
        """Evaluate -(-x)"""
        expr = Unary("-", Unary("-", VarRef("x")))
        result = evaluate(expr, var_values={("x", ()): 5.0})
        assert result == 5.0


@pytest.mark.integration
class TestFunctionCalls:
    """Test function call evaluation."""

    def test_exp(self):
        """Evaluate exp(x)"""
        expr = Call("exp", (VarRef("x"),))
        result = evaluate(expr, var_values={("x", ()): 1.0})
        assert abs(result - math.e) < 1e-10

    def test_log(self):
        """Evaluate log(x)"""
        expr = Call("log", (VarRef("x"),))
        result = evaluate(expr, var_values={("x", ()): math.e})
        assert abs(result - 1.0) < 1e-10

    def test_sqrt(self):
        """Evaluate sqrt(x)"""
        expr = Call("sqrt", (VarRef("x"),))
        result = evaluate(expr, var_values={("x", ()): 16.0})
        assert result == 4.0

    def test_sin(self):
        """Evaluate sin(x)"""
        expr = Call("sin", (VarRef("x"),))
        result = evaluate(expr, var_values={("x", ()): math.pi / 2})
        assert abs(result - 1.0) < 1e-10

    def test_cos(self):
        """Evaluate cos(x)"""
        expr = Call("cos", (VarRef("x"),))
        result = evaluate(expr, var_values={("x", ()): 0.0})
        assert abs(result - 1.0) < 1e-10

    def test_tan(self):
        """Evaluate tan(x)"""
        expr = Call("tan", (VarRef("x"),))
        result = evaluate(expr, var_values={("x", ()): 0.0})
        assert abs(result) < 1e-10

    def test_power_function(self):
        """Evaluate power(x, y)"""
        expr = Call("power", (VarRef("x"), VarRef("y")))
        result = evaluate(expr, var_values={("x", ()): 2.0, ("y", ()): 10.0})
        assert result == 1024.0


@pytest.mark.integration
class TestDivisionByZero:
    """Test division by zero detection."""

    def test_explicit_division_by_zero(self):
        """Division by zero should raise EvaluationError"""
        expr = Binary("/", VarRef("x"), Const(0.0))

        with pytest.raises(EvaluationError) as exc_info:
            evaluate(expr, var_values={("x", ()): 5.0})

        assert "Division by zero" in str(exc_info.value)
        assert "non-zero" in str(exc_info.value)

    def test_division_by_zero_variable(self):
        """Division by variable that evaluates to zero"""
        expr = Binary("/", VarRef("x"), VarRef("y"))

        with pytest.raises(EvaluationError) as exc_info:
            evaluate(expr, var_values={("x", ()): 10.0, ("y", ()): 0.0})

        assert "Division by zero" in str(exc_info.value)


@pytest.mark.integration
class TestDomainViolations:
    """Test domain violation detection."""

    def test_log_of_negative(self):
        """log of negative number should raise EvaluationError"""
        expr = Call("log", (VarRef("x"),))

        with pytest.raises(EvaluationError) as exc_info:
            evaluate(expr, var_values={("x", ()): -1.0})

        assert "log domain error" in str(exc_info.value)
        assert "positive" in str(exc_info.value)

    def test_log_of_zero(self):
        """log(0) should raise EvaluationError"""
        expr = Call("log", (Const(0.0),))

        with pytest.raises(EvaluationError) as exc_info:
            evaluate(expr)

        assert "log domain error" in str(exc_info.value)

    def test_sqrt_of_negative(self):
        """sqrt of negative number should raise EvaluationError"""
        expr = Call("sqrt", (VarRef("x"),))

        with pytest.raises(EvaluationError) as exc_info:
            evaluate(expr, var_values={("x", ()): -4.0})

        assert "sqrt domain error" in str(exc_info.value)
        assert "non-negative" in str(exc_info.value)


@pytest.mark.integration
class TestNaNDetection:
    """Test NaN detection."""

    def test_nan_in_constant(self):
        """NaN constant should be detected"""
        expr = Const(float("nan"))

        with pytest.raises(EvaluationError) as exc_info:
            evaluate(expr)

        assert "NaN detected" in str(exc_info.value)

    def test_nan_in_variable(self):
        """NaN in variable value should be detected"""
        expr = VarRef("x")

        with pytest.raises(EvaluationError) as exc_info:
            evaluate(expr, var_values={("x", ()): float("nan")})

        assert "NaN detected" in str(exc_info.value)

    def test_nan_from_operation(self):
        """NaN resulting from operation (0*inf) should be detected"""
        # Multiply 0 by inf to get NaN
        expr = Binary("*", Const(0.0), Const(float("inf")))

        with pytest.raises(EvaluationError) as exc_info:
            evaluate(expr)

        # Note: This might get caught as inf in constant first, so accept either
        error_msg = str(exc_info.value).lower()
        assert "nan detected" in error_msg or "infinity detected" in error_msg


@pytest.mark.integration
class TestInfDetection:
    """Test infinity detection."""

    def test_positive_inf_in_constant(self):
        """Positive infinity should be detected"""
        expr = Const(float("inf"))

        with pytest.raises(EvaluationError) as exc_info:
            evaluate(expr)

        assert "infinity detected" in str(exc_info.value)
        assert "Positive" in str(exc_info.value)

    def test_negative_inf_in_constant(self):
        """Negative infinity should be detected"""
        expr = Const(float("-inf"))

        with pytest.raises(EvaluationError) as exc_info:
            evaluate(expr)

        assert "infinity detected" in str(exc_info.value)
        assert "Negative" in str(exc_info.value)

    def test_inf_from_exp_overflow(self):
        """exp overflow to infinity should be detected"""
        expr = Call("exp", (Const(1000.0),))

        with pytest.raises(EvaluationError) as exc_info:
            evaluate(expr)

        assert "overflow" in str(exc_info.value).lower()


@pytest.mark.integration
class TestComplexExpressions:
    """Test evaluation of complex expressions."""

    def test_nested_arithmetic(self):
        """Evaluate (x + y) * (x - y)"""
        sum_expr = Binary("+", VarRef("x"), VarRef("y"))
        diff_expr = Binary("-", VarRef("x"), VarRef("y"))
        expr = Binary("*", sum_expr, diff_expr)

        result = evaluate(expr, var_values={("x", ()): 5.0, ("y", ()): 3.0})
        # (5 + 3) * (5 - 3) = 8 * 2 = 16
        assert result == 16.0

    def test_mixed_variables_and_params(self):
        """Evaluate expression with both variables and parameters"""
        # x * c + y
        term1 = Binary("*", VarRef("x"), ParamRef("c"))
        expr = Binary("+", term1, VarRef("y"))

        result = evaluate(
            expr,
            var_values={("x", ()): 3.0, ("y", ()): 4.0},
            param_values={("c", ()): 2.0},
        )
        # 3 * 2 + 4 = 10
        assert result == 10.0

    def test_function_composition(self):
        """Evaluate exp(log(x))"""
        inner = Call("log", (VarRef("x"),))
        expr = Call("exp", (inner,))

        result = evaluate(expr, var_values={("x", ()): 5.0})
        # exp(log(5)) = 5
        assert abs(result - 5.0) < 1e-10


@pytest.mark.integration
class TestMissingValues:
    """Test error handling for missing variable/parameter values."""

    def test_missing_variable(self):
        """Missing variable value should raise KeyError"""
        expr = VarRef("x")

        with pytest.raises(KeyError) as exc_info:
            evaluate(expr, var_values={})

        assert "Missing value for variable x" in str(exc_info.value)

    def test_missing_parameter(self):
        """Missing parameter value should raise KeyError"""
        expr = ParamRef("c")

        with pytest.raises(KeyError) as exc_info:
            evaluate(expr, param_values={})

        assert "Missing value for parameter c" in str(exc_info.value)

    def test_missing_indexed_variable(self):
        """Missing indexed variable value should raise KeyError"""
        expr = VarRef("x", ("i",))

        with pytest.raises(KeyError) as exc_info:
            evaluate(expr, var_values={})

        assert "Missing value for variable x(i)" in str(exc_info.value)
