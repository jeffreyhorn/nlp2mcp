"""
Tests for unsupported function rejection.

Day 4: Tests for abs() rejection with helpful error messages.
"""

import pytest

from src.ad.derivative_rules import differentiate_expr
from src.ir.ast import Call, VarRef

pytestmark = pytest.mark.unit

# ============================================================================
# abs() Rejection Tests
# ============================================================================


@pytest.mark.unit
class TestAbsRejection:
    """Tests for abs() rejection with helpful error messages."""

    def test_abs_variable_rejected(self):
        """Test abs(x) raises clear error about non-differentiability"""
        # abs(x)
        expr = Call("abs", (VarRef("x"),))

        with pytest.raises(ValueError) as exc_info:
            differentiate_expr(expr, "x")

        error_msg = str(exc_info.value)
        # Check that error message explains the issue
        assert "not differentiable everywhere" in error_msg
        assert "x=0" in error_msg or "undefined at" in error_msg

    def test_abs_rejection_mentions_planned_feature(self):
        """Test abs() error references planned feature for smooth approximations"""
        # abs(x)
        expr = Call("abs", (VarRef("x"),))

        with pytest.raises(ValueError) as exc_info:
            differentiate_expr(expr, "x")

        error_msg = str(exc_info.value)
        # Check that error message mentions planned feature and smoothing
        assert "planned feature" in error_msg.lower() or "smooth" in error_msg.lower()
        assert "smooth" in error_msg.lower()

    def test_abs_rejection_mentions_smooth_abs_flag(self):
        """Test abs() error mentions --smooth-abs flag"""
        # abs(x)
        expr = Call("abs", (VarRef("x"),))

        with pytest.raises(ValueError) as exc_info:
            differentiate_expr(expr, "x")

        error_msg = str(exc_info.value)
        # Check that error message mentions the smooth-abs flag
        assert "smooth-abs" in error_msg or "smooth approximation" in error_msg.lower()

    def test_abs_rejection_suggests_smooth_abs_flag(self):
        """Test abs() error suggests using --smooth-abs flag"""
        # abs(x)
        expr = Call("abs", (VarRef("x"),))

        with pytest.raises(ValueError) as exc_info:
            differentiate_expr(expr, "x")

        error_msg = str(exc_info.value)
        # Check that error message suggests the --smooth-abs flag
        assert "--smooth-abs" in error_msg or "smooth approximation" in error_msg.lower()
        assert "sqrt" in error_msg.lower() or "approximation" in error_msg.lower()

    def test_abs_composite_expression_rejected(self):
        """Test abs(x^2) also raises clear error"""
        # abs(x^2)
        inner = Call("power", (VarRef("x"), Call("const", (2.0,))))
        expr = Call("abs", (inner,))

        with pytest.raises(ValueError) as exc_info:
            differentiate_expr(expr, "x")

        error_msg = str(exc_info.value)
        # Should still explain abs is not differentiable
        assert "not differentiable" in error_msg.lower()

    def test_abs_different_variable_rejected(self):
        """Test abs(y) when differentiating w.r.t. x still raises error"""
        # abs(y) w.r.t. x
        expr = Call("abs", (VarRef("y"),))

        with pytest.raises(ValueError) as exc_info:
            differentiate_expr(expr, "x")

        error_msg = str(exc_info.value)
        # Should still reject abs() regardless of variable
        assert "not differentiable" in error_msg.lower()


# ============================================================================
# Other Unsupported Functions Tests
# ============================================================================


@pytest.mark.unit
class TestOtherUnsupportedFunctions:
    """Tests for other unsupported functions with clear error messages."""

    def test_unsupported_function_has_clear_message(self):
        """Test unknown function raises error with list of supported functions"""
        # hypothetical_func(x) - not implemented
        expr = Call("hypothetical_func", (VarRef("x"),))

        with pytest.raises(ValueError) as exc_info:
            differentiate_expr(expr, "x")

        error_msg = str(exc_info.value)
        # Error should list supported functions
        assert "not yet implemented" in error_msg.lower() or "not implemented" in error_msg.lower()
        assert "power" in error_msg or "exp" in error_msg  # Lists some supported functions

    def test_unsupported_function_mentions_abs_requires_flag(self):
        """Test error for unknown function mentions abs requires --smooth-abs flag"""
        # unknown_func(x)
        expr = Call("unknown_func", (VarRef("x"),))

        with pytest.raises(ValueError) as exc_info:
            differentiate_expr(expr, "x")

        error_msg = str(exc_info.value)
        # Should mention abs() requires --smooth-abs flag
        assert "abs" in error_msg.lower()
        assert "smooth-abs" in error_msg.lower() or "requires" in error_msg.lower()
