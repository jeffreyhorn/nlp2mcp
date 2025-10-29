"""
Tests for index-aware differentiation (Phase 1).

This module tests the new wrt_indices parameter added to differentiate_expr()
and all derivative rules to support exact index matching for sparse Jacobians.

Test Coverage:
- Basic index matching for VarRef
- Multi-dimensional index matching
- Index mismatch cases (should return 0)
- Backward compatibility (wrt_indices=None)
- Index-aware differentiation through all derivative rules
- Complex expressions with indexed variables
"""

from __future__ import annotations

from src.ad.derivative_rules import differentiate_expr
from src.ir.ast import Binary, Call, Const, ParamRef, Sum, Unary, VarRef


class TestBasicIndexAwareDifferentiation:
    """Test basic index-aware differentiation with VarRef."""

    def test_exact_index_match_returns_one(self):
        """d/dx(i1) x(i1) = 1"""
        expr = VarRef("x", ("i1",))
        result = differentiate_expr(expr, "x", ("i1",))
        assert isinstance(result, Const)
        assert result.value == 1.0

    def test_index_mismatch_returns_zero(self):
        """d/dx(i1) x(i2) = 0"""
        expr = VarRef("x", ("i2",))
        result = differentiate_expr(expr, "x", ("i1",))
        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_different_variable_with_same_index_returns_zero(self):
        """d/dx(i1) y(i1) = 0"""
        expr = VarRef("y", ("i1",))
        result = differentiate_expr(expr, "x", ("i1",))
        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_scalar_variable_with_indices_specified_returns_zero(self):
        """d/dx(i1) y = 0 (y is scalar, no indices)"""
        expr = VarRef("y")
        result = differentiate_expr(expr, "x", ("i1",))
        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_backward_compatible_none_indices_matches_any(self):
        """d/dx x(i1) = 1 (backward compatible, no indices specified)"""
        expr = VarRef("x", ("i1",))
        result = differentiate_expr(expr, "x", None)
        assert isinstance(result, Const)
        assert result.value == 1.0


class TestMultiDimensionalIndexMatching:
    """Test index-aware differentiation with multi-dimensional indices."""

    def test_two_indices_exact_match(self):
        """d/dx(i1,j2) x(i1,j2) = 1"""
        expr = VarRef("x", ("i1", "j2"))
        result = differentiate_expr(expr, "x", ("i1", "j2"))
        assert isinstance(result, Const)
        assert result.value == 1.0

    def test_two_indices_first_differs(self):
        """d/dx(i1,j2) x(i3,j2) = 0"""
        expr = VarRef("x", ("i3", "j2"))
        result = differentiate_expr(expr, "x", ("i1", "j2"))
        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_two_indices_second_differs(self):
        """d/dx(i1,j2) x(i1,j5) = 0"""
        expr = VarRef("x", ("i1", "j5"))
        result = differentiate_expr(expr, "x", ("i1", "j2"))
        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_two_indices_both_differ(self):
        """d/dx(i1,j2) x(i3,j4) = 0"""
        expr = VarRef("x", ("i3", "j4"))
        result = differentiate_expr(expr, "x", ("i1", "j2"))
        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_three_indices_exact_match(self):
        """d/dx(i1,j2,k3) x(i1,j2,k3) = 1"""
        expr = VarRef("x", ("i1", "j2", "k3"))
        result = differentiate_expr(expr, "x", ("i1", "j2", "k3"))
        assert isinstance(result, Const)
        assert result.value == 1.0

    def test_three_indices_middle_differs(self):
        """d/dx(i1,j2,k3) x(i1,j9,k3) = 0"""
        expr = VarRef("x", ("i1", "j9", "k3"))
        result = differentiate_expr(expr, "x", ("i1", "j2", "k3"))
        assert isinstance(result, Const)
        assert result.value == 0.0


class TestIndexAwareArithmetic:
    """Test index-aware differentiation through arithmetic operations."""

    def test_addition_with_matching_index(self):
        """d/dx(i1) [x(i1) + y(i1)] = 1 + 0 = Binary("+", Const(1), Const(0))"""
        expr = Binary("+", VarRef("x", ("i1",)), VarRef("y", ("i1",)))
        result = differentiate_expr(expr, "x", ("i1",))
        assert isinstance(result, Binary)
        assert result.op == "+"
        assert isinstance(result.left, Const) and result.left.value == 1.0
        assert isinstance(result.right, Const) and result.right.value == 0.0

    def test_addition_with_mismatched_index(self):
        """d/dx(i1) [x(i2) + y(i2)] = 0 + 0"""
        expr = Binary("+", VarRef("x", ("i2",)), VarRef("y", ("i2",)))
        result = differentiate_expr(expr, "x", ("i1",))
        assert isinstance(result, Binary)
        assert result.op == "+"
        assert isinstance(result.left, Const) and result.left.value == 0.0
        assert isinstance(result.right, Const) and result.right.value == 0.0

    def test_product_with_matching_index(self):
        """d/dx(i1) [x(i1) * y(i2)] = y(i2)*1 + x(i1)*0"""
        expr = Binary("*", VarRef("x", ("i1",)), VarRef("y", ("i2",)))
        result = differentiate_expr(expr, "x", ("i1",))
        assert isinstance(result, Binary)
        assert result.op == "+"
        # First term: y(i2) * 1
        assert isinstance(result.left, Binary)
        assert result.left.op == "*"
        # Second term: x(i1) * 0
        assert isinstance(result.right, Binary)
        assert result.right.op == "*"

    def test_product_with_mismatched_index(self):
        """d/dx(i1) [x(i2) * y(i2)] = y(i2)*0 + x(i2)*0"""
        expr = Binary("*", VarRef("x", ("i2",)), VarRef("y", ("i2",)))
        result = differentiate_expr(expr, "x", ("i1",))
        assert isinstance(result, Binary)
        assert result.op == "+"
        # Both terms should have 0 derivative
        assert isinstance(result.left, Binary)
        assert result.left.op == "*"
        assert isinstance(result.right, Binary)
        assert result.right.op == "*"

    def test_subtraction_mixed_indices(self):
        """d/dx(i1) [x(i1) - x(i2)] = 1 - 0"""
        expr = Binary("-", VarRef("x", ("i1",)), VarRef("x", ("i2",)))
        result = differentiate_expr(expr, "x", ("i1",))
        assert isinstance(result, Binary)
        assert result.op == "-"
        assert isinstance(result.left, Const) and result.left.value == 1.0
        assert isinstance(result.right, Const) and result.right.value == 0.0


class TestIndexAwareUnary:
    """Test index-aware differentiation through unary operations."""

    def test_unary_minus_matching_index(self):
        """d/dx(i1) [-x(i1)] = -1"""
        expr = Unary("-", VarRef("x", ("i1",)))
        result = differentiate_expr(expr, "x", ("i1",))
        assert isinstance(result, Unary)
        assert result.op == "-"
        assert isinstance(result.child, Const)
        assert result.child.value == 1.0

    def test_unary_minus_mismatched_index(self):
        """d/dx(i1) [-x(i2)] = -0"""
        expr = Unary("-", VarRef("x", ("i2",)))
        result = differentiate_expr(expr, "x", ("i1",))
        assert isinstance(result, Unary)
        assert result.op == "-"
        assert isinstance(result.child, Const)
        assert result.child.value == 0.0


class TestIndexAwarePower:
    """Test index-aware differentiation through power function."""

    def test_power_matching_index(self):
        """d/dx(i1) [x(i1)^2] = 2*x(i1)^1 * 1"""
        expr = Call("power", (VarRef("x", ("i1",)), Const(2.0)))
        result = differentiate_expr(expr, "x", ("i1",))
        assert isinstance(result, Binary)
        assert result.op == "*"
        # Left: 2 * x(i1)^1
        assert isinstance(result.left, Binary)
        assert result.left.op == "*"
        # Right: derivative is 1
        assert isinstance(result.right, Const)
        assert result.right.value == 1.0

    def test_power_mismatched_index(self):
        """d/dx(i1) [x(i2)^2] = 2*x(i2)^1 * 0"""
        expr = Call("power", (VarRef("x", ("i2",)), Const(2.0)))
        result = differentiate_expr(expr, "x", ("i1",))
        assert isinstance(result, Binary)
        assert result.op == "*"
        # Right: derivative is 0
        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_power_base_matches_exponent_differs(self):
        """d/dx(i1) [x(i1)^y(i2)] - only base depends on x(i1)"""
        base = VarRef("x", ("i1",))
        exponent = VarRef("y", ("i2",))
        expr = Call("power", (base, exponent))
        result = differentiate_expr(expr, "x", ("i1",))
        # Result should be: x(i1)^y(i2) * (y(i2)/x(i1) * 1 + ln(x(i1)) * 0)
        assert isinstance(result, Binary)
        assert result.op == "*"


class TestIndexAwareTranscendental:
    """Test index-aware differentiation through transcendental functions."""

    def test_exp_matching_index(self):
        """d/dx(i1) [exp(x(i1))] = exp(x(i1)) * 1"""
        expr = Call("exp", (VarRef("x", ("i1",)),))
        result = differentiate_expr(expr, "x", ("i1",))
        assert isinstance(result, Binary)
        assert result.op == "*"
        # Right: derivative is 1
        assert isinstance(result.right, Const)
        assert result.right.value == 1.0

    def test_exp_mismatched_index(self):
        """d/dx(i1) [exp(x(i2))] = exp(x(i2)) * 0"""
        expr = Call("exp", (VarRef("x", ("i2",)),))
        result = differentiate_expr(expr, "x", ("i1",))
        assert isinstance(result, Binary)
        assert result.op == "*"
        # Right: derivative is 0
        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_log_matching_index(self):
        """d/dx(i1) [log(x(i1))] = (1/x(i1)) * 1"""
        expr = Call("log", (VarRef("x", ("i1",)),))
        result = differentiate_expr(expr, "x", ("i1",))
        assert isinstance(result, Binary)
        assert result.op == "*"
        # Right: derivative is 1
        assert isinstance(result.right, Const)
        assert result.right.value == 1.0

    def test_sqrt_mismatched_index(self):
        """d/dx(i1) [sqrt(x(i2))] = (1/(2*sqrt(x(i2)))) * 0"""
        expr = Call("sqrt", (VarRef("x", ("i2",)),))
        result = differentiate_expr(expr, "x", ("i1",))
        assert isinstance(result, Binary)
        assert result.op == "*"
        # Right: derivative is 0
        assert isinstance(result.right, Const)
        assert result.right.value == 0.0


class TestIndexAwareTrigonometric:
    """Test index-aware differentiation through trigonometric functions."""

    def test_sin_matching_index(self):
        """d/dx(i1) [sin(x(i1))] = cos(x(i1)) * 1"""
        expr = Call("sin", (VarRef("x", ("i1",)),))
        result = differentiate_expr(expr, "x", ("i1",))
        assert isinstance(result, Binary)
        assert result.op == "*"
        # Right: derivative is 1
        assert isinstance(result.right, Const)
        assert result.right.value == 1.0

    def test_cos_mismatched_index(self):
        """d/dx(i1) [cos(x(i2))] = -sin(x(i2)) * 0"""
        expr = Call("cos", (VarRef("x", ("i2",)),))
        result = differentiate_expr(expr, "x", ("i1",))
        assert isinstance(result, Binary)
        assert result.op == "*"
        # Right: derivative is 0
        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_tan_matching_index(self):
        """d/dx(i1) [tan(x(i1))] = (1/cos^2(x(i1))) * 1"""
        expr = Call("tan", (VarRef("x", ("i1",)),))
        result = differentiate_expr(expr, "x", ("i1",))
        assert isinstance(result, Binary)
        assert result.op == "*"
        # Right: derivative is 1
        assert isinstance(result.right, Const)
        assert result.right.value == 1.0


class TestIndexAwareSum:
    """Test index-aware differentiation through sum aggregations."""

    def test_sum_with_matching_index_in_body(self):
        """d/dx(i1) [sum(j, x(i1) * y(j))] = sum(j, 1 * y(j))"""
        # Note: x(i1) is outside the sum domain (j), so it matches x(i1)
        body = Binary("*", VarRef("x", ("i1",)), VarRef("y", ("j",)))
        expr = Sum(("j",), body)
        result = differentiate_expr(expr, "x", ("i1",))

        assert isinstance(result, Sum)
        assert result.index_sets == ("j",)
        # Body should be: 1 * y(j) + x(i1) * 0
        assert isinstance(result.body, Binary)
        assert result.body.op == "+"

    def test_sum_with_mismatched_index_in_body(self):
        """d/dx(i1) [sum(j, x(i2) * y(j))] = sum(j, 0 * y(j))"""
        body = Binary("*", VarRef("x", ("i2",)), VarRef("y", ("j",)))
        expr = Sum(("j",), body)
        result = differentiate_expr(expr, "x", ("i1",))

        assert isinstance(result, Sum)
        assert result.index_sets == ("j",)
        # Body should be: 0 * y(j) + x(i2) * 0
        assert isinstance(result.body, Binary)
        assert result.body.op == "+"

    def test_sum_over_same_index_as_wrt(self):
        """d/dx(i1) [sum(i, x(i))] = sum(i, d/dx(i1) x(i))

        When i=i1: derivative is 1
        When i≠i1: derivative is 0
        Result: sum(i, [1 if i==i1 else 0])
        """
        expr = Sum(("i",), VarRef("x", ("i",)))
        result = differentiate_expr(expr, "x", ("i1",))

        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        # Body is derivative of x(i) w.r.t. x(i1)
        # This will be 0 for all i ≠ i1, and 1 for i = i1
        # But at this symbolic level, we just verify structure
        assert isinstance(result.body, Const)


class TestComplexIndexAwareExpressions:
    """Test index-aware differentiation in complex expressions."""

    def test_nested_function_calls_matching(self):
        """d/dx(i1) [exp(log(x(i1)))] = exp(log(x(i1))) * (1/x(i1)) * 1"""
        inner = Call("log", (VarRef("x", ("i1",)),))
        expr = Call("exp", (inner,))
        result = differentiate_expr(expr, "x", ("i1",))

        assert isinstance(result, Binary)
        assert result.op == "*"
        # Chain rule applies correctly

    def test_nested_function_calls_mismatched(self):
        """d/dx(i1) [exp(log(x(i2)))] = exp(log(x(i2))) * (1/x(i2)) * 0"""
        inner = Call("log", (VarRef("x", ("i2",)),))
        expr = Call("exp", (inner,))
        result = differentiate_expr(expr, "x", ("i1",))

        # Should eventually multiply by 0
        # Navigate through the AST to find the 0
        assert isinstance(result, Binary)
        assert result.op == "*"

    def test_mixed_matched_and_mismatched_indices(self):
        """d/dx(i1) [x(i1) * x(i2) * x(i3)]"""
        # (x(i1) * x(i2)) * x(i3)
        left = Binary("*", VarRef("x", ("i1",)), VarRef("x", ("i2",)))
        expr = Binary("*", left, VarRef("x", ("i3",)))
        result = differentiate_expr(expr, "x", ("i1",))

        # Result: x(i2)*x(i3)*1 + x(i1)*x(i3)*0 + x(i1)*x(i2)*0
        # Only the first term survives
        assert isinstance(result, Binary)
        assert result.op == "+"

    def test_parameter_with_index_always_zero(self):
        """d/dx(i1) [p(i1)] = 0 (parameters are constant)"""
        expr = ParamRef("p", ("i1",))
        result = differentiate_expr(expr, "x", ("i1",))
        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_sum_of_products_with_mixed_indices(self):
        """d/dx(i1) [sum(j, x(i1) * y(j) * z(i2))]"""
        product = Binary(
            "*",
            Binary("*", VarRef("x", ("i1",)), VarRef("y", ("j",))),
            VarRef("z", ("i2",)),
        )
        expr = Sum(("j",), product)
        result = differentiate_expr(expr, "x", ("i1",))

        assert isinstance(result, Sum)
        assert result.index_sets == ("j",)
        # Body derivative should reflect that only x(i1) contributes
