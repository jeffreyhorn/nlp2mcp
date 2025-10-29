"""
Test Finite-Difference Validation for Symbolic Differentiation

This module tests the finite-difference validation utilities against all
derivative rules implemented in src/ad/derivative_rules.py.

Test Strategy:
--------------
1. Generate deterministic test points using fixed seed (42)
2. Compute symbolic derivatives using derivative_rules.py
3. Compute numerical derivatives using finite-difference
4. Validate that symbolic and numerical derivatives match within tolerance (1e-6)

Test Coverage:
--------------
Day 1: Constants, variables, parameters
Day 2: Binary operations (+, -, *, /), unary operations (+, -)
Day 3: Function calls (power, exp, log, sqrt)
Day 4: Trigonometric functions (sin, cos, tan)
Day 5: Sum aggregations

Edge Cases:
-----------
- Constant expressions (zero derivatives)
- Variables that don't appear in expression
- Near-zero values
- Domain boundaries (log near 0, sqrt near 0)
- NaN/Inf detection from Day 2

Deterministic Testing:
---------------------
All tests use fixed random seed (42) for reproducible results.
"""

import math

import pytest

from src.ad.derivative_rules import differentiate_expr
from src.ad.validation import (
    generate_test_point,
    validate_derivative,
    validate_gradient,
)
from src.ir.ast import Binary, Call, Const, ParamRef, Unary, VarRef

pytestmark = pytest.mark.validation

# ============================================================================
# Test Constants and Variable References (Day 1)
# ============================================================================


def test_constant_derivative():
    """Test that derivative of constant is zero."""
    expr = Const(5.0)
    symbolic_deriv = differentiate_expr(expr, "x")
    var_values = {"x": 3.0}

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid, f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}"
    assert abs(sym_val) < 1e-10, "Derivative of constant should be zero"
    assert abs(fd_val) < 1e-6, "FD derivative of constant should be near zero"


def test_variable_derivative_same():
    """Test that d(x)/dx = 1."""
    expr = VarRef("x")
    symbolic_deriv = differentiate_expr(expr, "x")
    var_values = {"x": 3.0}

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid, f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}"
    assert abs(sym_val - 1.0) < 1e-10, "d(x)/dx should be 1"
    assert abs(fd_val - 1.0) < 1e-6, "FD should confirm d(x)/dx = 1"


def test_variable_derivative_different():
    """Test that d(y)/dx = 0."""
    expr = VarRef("y")
    symbolic_deriv = differentiate_expr(expr, "x")
    var_values = {"x": 3.0, "y": 5.0}

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid, f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}"
    assert abs(sym_val) < 1e-10, "d(y)/dx should be 0"
    assert abs(fd_val) < 1e-6, "FD should confirm d(y)/dx = 0"


def test_parameter_derivative():
    """Test that derivative of parameter is zero."""
    expr = ParamRef("c")
    symbolic_deriv = differentiate_expr(expr, "x")
    var_values = {"x": 3.0}
    param_values = {"c": 10.0}

    is_valid, sym_val, fd_val, error = validate_derivative(
        expr, symbolic_deriv, "x", var_values, param_values
    )

    assert is_valid, f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}"
    assert abs(sym_val) < 1e-10, "Derivative of parameter should be zero"
    assert abs(fd_val) < 1e-6, "FD derivative of parameter should be near zero"


# ============================================================================
# Test Binary Operations (Day 2)
# ============================================================================


def test_sum_rule():
    """Test sum rule: d(x+y)/dx = 1."""
    expr = Binary("+", VarRef("x"), VarRef("y"))
    symbolic_deriv = differentiate_expr(expr, "x")

    # Generate deterministic test point
    var_values = generate_test_point(["x", "y"])

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid, f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}"
    assert abs(sym_val - 1.0) < 1e-10, "d(x+y)/dx should be 1"


def test_difference_rule():
    """Test difference rule: d(x-y)/dx = 1."""
    expr = Binary("-", VarRef("x"), VarRef("y"))
    symbolic_deriv = differentiate_expr(expr, "x")

    var_values = generate_test_point(["x", "y"])

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid, f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}"
    assert abs(sym_val - 1.0) < 1e-10, "d(x-y)/dx should be 1"


def test_product_rule():
    """Test product rule: d(x*y)/dx = y."""
    expr = Binary("*", VarRef("x"), VarRef("y"))
    symbolic_deriv = differentiate_expr(expr, "x")

    var_values = generate_test_point(["x", "y"])

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid, f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}"
    # Symbolic derivative should equal y (within evaluation tolerance)
    assert abs(sym_val - var_values["y"]) < 1e-10, f"d(x*y)/dx should be y={var_values['y']}"


def test_quotient_rule():
    """Test quotient rule: d(x/y)/dx = 1/y."""
    expr = Binary("/", VarRef("x"), VarRef("y"))
    symbolic_deriv = differentiate_expr(expr, "x")

    # Avoid near-zero y
    var_values = generate_test_point(["x", "y"], {"y": (1.0, 10.0)})

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid, f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}"
    expected = 1.0 / var_values["y"]
    assert abs(sym_val - expected) < 1e-10, f"d(x/y)/dx should be 1/y={expected}"


# ============================================================================
# Test Unary Operations (Day 2)
# ============================================================================


def test_unary_plus():
    """Test unary plus: d(+x)/dx = 1."""
    expr = Unary("+", VarRef("x"))
    symbolic_deriv = differentiate_expr(expr, "x")

    var_values = generate_test_point(["x"])

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid, f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}"
    assert abs(sym_val - 1.0) < 1e-10, "d(+x)/dx should be 1"


def test_unary_minus():
    """Test unary minus: d(-x)/dx = -1."""
    expr = Unary("-", VarRef("x"))
    symbolic_deriv = differentiate_expr(expr, "x")

    var_values = generate_test_point(["x"])

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid, f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}"
    assert abs(sym_val - (-1.0)) < 1e-10, "d(-x)/dx should be -1"


# ============================================================================
# Test Function Calls - Power, Exp, Log, Sqrt (Day 3)
# ============================================================================


def test_power_rule_constant_exponent():
    """Test power rule: d(x^2)/dx = 2*x."""
    expr = Call("power", (VarRef("x"), Const(2.0)))
    symbolic_deriv = differentiate_expr(expr, "x")

    var_values = generate_test_point(["x"], {"x": (1.0, 5.0)})

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid, f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}"
    expected = 2.0 * var_values["x"]
    assert abs(sym_val - expected) < 1e-10, f"d(x^2)/dx should be 2*x={expected}"


def test_power_rule_variable_exponent():
    """Test power rule with variable exponent: d(x^y)/dx."""
    expr = Call("power", (VarRef("x"), VarRef("y")))
    symbolic_deriv = differentiate_expr(expr, "x")

    # Use positive x to avoid domain issues with non-integer powers
    var_values = generate_test_point(["x", "y"], {"x": (1.0, 5.0), "y": (0.5, 3.0)})

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid, f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}"
    # d(x^y)/dx = y * x^(y-1)
    x, y = var_values["x"], var_values["y"]
    expected = y * (x ** (y - 1))
    assert abs(sym_val - expected) < 1e-9, f"d(x^y)/dx should be y*x^(y-1)={expected}"


def test_exp_rule():
    """Test exponential rule: d(exp(x))/dx = exp(x)."""
    expr = Call("exp", (VarRef("x"),))
    symbolic_deriv = differentiate_expr(expr, "x")

    var_values = generate_test_point(["x"], {"x": (-2.0, 2.0)})

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid, f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}"
    expected = math.exp(var_values["x"])
    assert abs(sym_val - expected) < 1e-9, f"d(exp(x))/dx should be exp(x)={expected}"


def test_log_rule():
    """Test logarithm rule: d(log(x))/dx = 1/x."""
    expr = Call("log", (VarRef("x"),))
    symbolic_deriv = differentiate_expr(expr, "x")

    # Avoid near-zero x (log domain restriction)
    var_values = generate_test_point(["x"], {"x": (0.5, 5.0)})

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid, f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}"
    expected = 1.0 / var_values["x"]
    assert abs(sym_val - expected) < 1e-9, f"d(log(x))/dx should be 1/x={expected}"


def test_sqrt_rule():
    """Test square root rule: d(sqrt(x))/dx = 1/(2*sqrt(x))."""
    expr = Call("sqrt", (VarRef("x"),))
    symbolic_deriv = differentiate_expr(expr, "x")

    # Avoid near-zero x (sqrt domain restriction)
    var_values = generate_test_point(["x"], {"x": (0.5, 5.0)})

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid, f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}"
    expected = 1.0 / (2.0 * math.sqrt(var_values["x"]))
    assert abs(sym_val - expected) < 1e-9, f"d(sqrt(x))/dx should be 1/(2*sqrt(x))={expected}"


# ============================================================================
# Test Trigonometric Functions (Day 4)
# ============================================================================


def test_sin_rule():
    """Test sine rule: d(sin(x))/dx = cos(x)."""
    expr = Call("sin", (VarRef("x"),))
    symbolic_deriv = differentiate_expr(expr, "x")

    var_values = generate_test_point(["x"], {"x": (-math.pi, math.pi)})

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid, f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}"
    expected = math.cos(var_values["x"])
    assert abs(sym_val - expected) < 1e-9, f"d(sin(x))/dx should be cos(x)={expected}"


def test_cos_rule():
    """Test cosine rule: d(cos(x))/dx = -sin(x)."""
    expr = Call("cos", (VarRef("x"),))
    symbolic_deriv = differentiate_expr(expr, "x")

    var_values = generate_test_point(["x"], {"x": (-math.pi, math.pi)})

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid, f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}"
    expected = -math.sin(var_values["x"])
    assert abs(sym_val - expected) < 1e-9, f"d(cos(x))/dx should be -sin(x)={expected}"


def test_tan_rule():
    """Test tangent rule: d(tan(x))/dx = 1/cos^2(x) = sec^2(x)."""
    expr = Call("tan", (VarRef("x"),))
    symbolic_deriv = differentiate_expr(expr, "x")

    # Avoid tan poles at π/2 + nπ
    var_values = generate_test_point(["x"], {"x": (-1.0, 1.0)})

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid, f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}"
    cos_x = math.cos(var_values["x"])
    expected = 1.0 / (cos_x * cos_x)
    assert abs(sym_val - expected) < 1e-9, f"d(tan(x))/dx should be sec^2(x)={expected}"


# ============================================================================
# Test Chain Rule (Composite Functions)
# ============================================================================


def test_chain_rule_exp_quadratic():
    """Test chain rule: d(exp(x^2))/dx = exp(x^2) * 2x."""
    expr = Call("exp", (Call("power", (VarRef("x"), Const(2.0))),))
    symbolic_deriv = differentiate_expr(expr, "x")

    var_values = generate_test_point(["x"], {"x": (-2.0, 2.0)})

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid, f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}"
    x = var_values["x"]
    expected = math.exp(x * x) * 2.0 * x
    assert abs(sym_val - expected) < 1e-8, f"d(exp(x^2))/dx should be exp(x^2)*2x={expected}"


def test_chain_rule_log_quadratic():
    """Test chain rule: d(log(x^2))/dx = (1/x^2) * 2x = 2/x."""
    expr = Call("log", (Call("power", (VarRef("x"), Const(2.0))),))
    symbolic_deriv = differentiate_expr(expr, "x")

    # Use positive x to avoid log domain issues
    var_values = generate_test_point(["x"], {"x": (0.5, 5.0)})

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid, f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}"
    expected = 2.0 / var_values["x"]
    assert abs(sym_val - expected) < 1e-9, f"d(log(x^2))/dx should be 2/x={expected}"


def test_chain_rule_sin_product():
    """Test chain rule: d(sin(x*y))/dx = cos(x*y) * y."""
    expr = Call("sin", (Binary("*", VarRef("x"), VarRef("y")),))
    symbolic_deriv = differentiate_expr(expr, "x")

    var_values = generate_test_point(["x", "y"], {"x": (-2.0, 2.0), "y": (-2.0, 2.0)})

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid, f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}"
    x, y = var_values["x"], var_values["y"]
    expected = math.cos(x * y) * y
    assert abs(sym_val - expected) < 1e-9, f"d(sin(x*y))/dx should be cos(x*y)*y={expected}"


# ============================================================================
# Test Gradient Validation
# ============================================================================


def test_gradient_validation_quadratic():
    """Test gradient validation for f(x,y) = x^2 + y^2."""
    expr = Binary(
        "+", Call("power", (VarRef("x"), Const(2.0))), Call("power", (VarRef("y"), Const(2.0)))
    )

    # Compute symbolic gradient
    dx = differentiate_expr(expr, "x")
    dy = differentiate_expr(expr, "y")
    symbolic_gradient = {"x": dx, "y": dy}

    var_values = generate_test_point(["x", "y"])

    results = validate_gradient(expr, symbolic_gradient, var_values)

    # Check that both partial derivatives are valid
    assert results["x"][0], f"∂f/∂x validation failed: {results['x']}"
    assert results["y"][0], f"∂f/∂y validation failed: {results['y']}"

    # Check that symbolic values match expected (2*x and 2*y)
    assert abs(results["x"][1] - 2.0 * var_values["x"]) < 1e-10
    assert abs(results["y"][1] - 2.0 * var_values["y"]) < 1e-10


# ============================================================================
# Test Edge Cases
# ============================================================================


def test_constant_expression_zero_derivative():
    """Test that constant expression has zero derivative everywhere."""
    expr = Binary("+", Const(5.0), Const(3.0))
    symbolic_deriv = differentiate_expr(expr, "x")

    var_values = {"x": 2.0}

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid
    assert abs(sym_val) < 1e-10, "Derivative should be zero"
    assert abs(fd_val) < 1e-6, "FD should also be near zero"


def test_variable_not_in_expression():
    """Test derivative w.r.t. variable that doesn't appear in expression."""
    expr = Binary("*", VarRef("x"), VarRef("y"))
    symbolic_deriv = differentiate_expr(expr, "z")

    var_values = {"x": 2.0, "y": 3.0, "z": 1.0}

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "z", var_values)

    assert is_valid
    assert abs(sym_val) < 1e-10, "Derivative w.r.t. z should be zero"
    assert abs(fd_val) < 1e-6, "FD w.r.t. z should also be near zero"


def test_near_zero_values():
    """Test derivatives near zero."""
    expr = Binary("+", VarRef("x"), Const(1.0))
    symbolic_deriv = differentiate_expr(expr, "x")

    var_values = {"x": 1e-8}

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid
    assert abs(sym_val - 1.0) < 1e-10, "Derivative should still be 1"


def test_large_values():
    """Test derivatives with large values."""
    expr = Call("exp", (VarRef("x"),))
    symbolic_deriv = differentiate_expr(expr, "x")

    # Use moderate values to avoid overflow (exp(10) ≈ 22000)
    var_values = {"x": 10.0}

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    # For large values, relative error might be more appropriate than absolute
    expected = math.exp(10.0)
    if not is_valid:
        relative_error = error / expected if expected != 0 else error
        # Allow slightly larger relative tolerance for large values
        assert relative_error < 1e-4, (
            f"Validation failed: symbolic={sym_val}, fd={fd_val}, error={error}, "
            f"expected={expected}, relative_error={relative_error}"
        )
    assert abs(sym_val - expected) < 1e-5, f"Derivative should be exp(10)={expected}"


def test_domain_boundary_log_near_zero():
    """Test that log near zero is handled correctly."""
    expr = Call("log", (VarRef("x"),))
    symbolic_deriv = differentiate_expr(expr, "x")

    # Test near (but not at) zero - log is undefined at x=0
    var_values = {"x": 0.01}

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid
    expected = 1.0 / 0.01  # = 100.0
    assert abs(sym_val - expected) < 1e-7, "d(log(x))/dx at x=0.01 should be 100"


def test_domain_boundary_sqrt_near_zero():
    """Test that sqrt near zero is handled correctly."""
    expr = Call("sqrt", (VarRef("x"),))
    symbolic_deriv = differentiate_expr(expr, "x")

    # Test near (but not at) zero - sqrt'(0) is undefined (infinite)
    var_values = {"x": 0.01}

    is_valid, sym_val, fd_val, error = validate_derivative(expr, symbolic_deriv, "x", var_values)

    assert is_valid
    expected = 1.0 / (2.0 * math.sqrt(0.01))  # = 5.0
    assert abs(sym_val - expected) < 1e-7, "d(sqrt(x))/dx at x=0.01 should be 5.0"


# ============================================================================
# Test NaN/Inf Detection (from Day 2 evaluator)
# ============================================================================


def test_nan_detection_log_negative():
    """Test that log of negative number raises an error (better than NaN)."""
    from src.ad.evaluator import EvaluationError, evaluate

    expr = Call("log", (VarRef("x"),))
    var_values = {("x", ()): -1.0}

    # Should raise EvaluationError (log of negative is undefined)
    with pytest.raises(EvaluationError, match="log domain error"):
        evaluate(expr, var_values, {})


def test_inf_detection_division_by_zero():
    """Test that division by zero raises an error (better than Inf)."""
    from src.ad.evaluator import EvaluationError, evaluate

    expr = Binary("/", Const(1.0), VarRef("x"))
    var_values = {("x", ()): 0.0}

    # Should raise EvaluationError (division by zero is undefined)
    with pytest.raises(EvaluationError, match="Division by zero"):
        evaluate(expr, var_values, {})


def test_nan_propagation_through_expression():
    """Test that domain errors propagate through expressions."""
    from src.ad.evaluator import EvaluationError, evaluate

    # sqrt(-1) * x should raise error (sqrt domain error)
    expr = Binary("*", Call("sqrt", (Const(-1.0),)), VarRef("x"))
    var_values = {("x", ()): 5.0}

    # Should raise EvaluationError (sqrt domain error)
    with pytest.raises(EvaluationError, match="sqrt domain error"):
        evaluate(expr, var_values, {})


# ============================================================================
# Test Deterministic Seed Generation
# ============================================================================


def test_generate_test_point_deterministic():
    """Test that generate_test_point produces deterministic results."""
    # Generate same test point twice
    point1 = generate_test_point(["x", "y"], seed=42)
    point2 = generate_test_point(["x", "y"], seed=42)

    assert point1 == point2, "Same seed should produce same test points"


def test_generate_test_point_with_bounds():
    """Test that generate_test_point respects bounds."""
    bounds = {"x": (1.0, 5.0), "y": (10.0, 20.0)}
    point = generate_test_point(["x", "y"], bounds=bounds, seed=42)

    assert 1.0 <= point["x"] <= 5.0, f"x={point['x']} should be in [1.0, 5.0]"
    assert 10.0 <= point["y"] <= 20.0, f"y={point['y']} should be in [10.0, 20.0]"


def test_generate_test_point_avoids_boundaries():
    """Test that generate_test_point avoids exact boundaries."""
    bounds = {"x": (0.0, 10.0)}
    point = generate_test_point(["x"], bounds=bounds, seed=42)

    # Should be away from boundaries (with epsilon buffer = 0.1)
    assert point["x"] > 0.1, "Should avoid lower boundary"
    assert point["x"] < 9.9, "Should avoid upper boundary"
