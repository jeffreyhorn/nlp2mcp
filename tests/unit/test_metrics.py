"""Unit tests for term reduction metrics collection.

Tests count_terms() function and SimplificationMetrics class.

Sprint 12 Day 1: Measurement Infrastructure Setup
"""

import pytest

from src.ir.ast import Binary, Call, Const, VarRef
from src.ir.metrics import SimplificationMetrics, count_terms


class TestCountTerms:
    """Test count_terms() function with 15+ test cases."""

    def test_single_variable(self):
        """Single variable is 1 term."""
        expr = VarRef("x")
        assert count_terms(expr) == 1

    def test_single_constant(self):
        """Single constant is 1 term."""
        expr = Const(5.0)
        assert count_terms(expr) == 1

    def test_simple_addition(self):
        """x + y is 2 terms."""
        expr = Binary("+", VarRef("x"), VarRef("y"))
        assert count_terms(expr) == 2

    def test_three_term_addition(self):
        """x + y + z is 3 terms."""
        # (x + y) + z
        expr = Binary("+", Binary("+", VarRef("x"), VarRef("y")), VarRef("z"))
        assert count_terms(expr) == 3

    def test_subtraction_as_addition(self):
        """x - y is 2 terms (subtraction treated as addition)."""
        expr = Binary("-", VarRef("x"), VarRef("y"))
        assert count_terms(expr) == 2

    def test_mixed_addition_subtraction(self):
        """x + y - z is 3 terms."""
        # (x + y) - z
        expr = Binary("-", Binary("+", VarRef("x"), VarRef("y")), VarRef("z"))
        assert count_terms(expr) == 3

    def test_single_product(self):
        """x*y is 1 term (not expanded)."""
        expr = Binary("*", VarRef("x"), VarRef("y"))
        assert count_terms(expr) == 1

    def test_sum_of_products(self):
        """x*y + x*z is 2 terms."""
        expr = Binary(
            "+",
            Binary("*", VarRef("x"), VarRef("y")),
            Binary("*", VarRef("x"), VarRef("z")),
        )
        assert count_terms(expr) == 2

    def test_factored_expression(self):
        """x*(y+z) is 1 term (factored form not expanded)."""
        expr = Binary("*", VarRef("x"), Binary("+", VarRef("y"), VarRef("z")))
        assert count_terms(expr) == 1

    def test_product_of_sums(self):
        """(a+b)*(c+d) is 1 term (product, not expanded)."""
        expr = Binary(
            "*",
            Binary("+", VarRef("a"), VarRef("b")),
            Binary("+", VarRef("c"), VarRef("d")),
        )
        assert count_terms(expr) == 1

    def test_quotient(self):
        """x/y is 1 term."""
        expr = Binary("/", VarRef("x"), VarRef("y"))
        assert count_terms(expr) == 1

    def test_complex_quotient(self):
        """(2*x)/2 is 1 term (quotient, not simplified)."""
        expr = Binary("/", Binary("*", Const(2.0), VarRef("x")), Const(2.0))
        assert count_terms(expr) == 1

    def test_power_expression(self):
        """x^2 is 1 term."""
        expr = Binary("**", VarRef("x"), Const(2.0))
        assert count_terms(expr) == 1

    def test_sum_of_powers(self):
        """a^2 + b^2 is 2 terms."""
        expr = Binary(
            "+",
            Binary("**", VarRef("a"), Const(2.0)),
            Binary("**", VarRef("b"), Const(2.0)),
        )
        assert count_terms(expr) == 2

    def test_function_call(self):
        """sin(x) is 1 term."""
        expr = Call("sin", [VarRef("x")])
        assert count_terms(expr) == 1

    def test_sum_with_function(self):
        """x + sin(y) is 2 terms."""
        expr = Binary("+", VarRef("x"), Call("sin", [VarRef("y")]))
        assert count_terms(expr) == 2

    def test_complex_nested_expression(self):
        """Complex expression: (a+b)*(c+d) + (a+b)*(e+f) is 2 terms."""
        # Two products being added
        term1 = Binary(
            "*",
            Binary("+", VarRef("a"), VarRef("b")),
            Binary("+", VarRef("c"), VarRef("d")),
        )
        term2 = Binary(
            "*",
            Binary("+", VarRef("a"), VarRef("b")),
            Binary("+", VarRef("e"), VarRef("f")),
        )
        expr = Binary("+", term1, term2)
        assert count_terms(expr) == 2

    def test_deeply_nested_addition(self):
        """((x + y) + z) + w is 4 terms."""
        expr = Binary(
            "+",
            Binary("+", Binary("+", VarRef("x"), VarRef("y")), VarRef("z")),
            VarRef("w"),
        )
        assert count_terms(expr) == 4

    def test_zero_constant(self):
        """Constant 0 is 1 term."""
        expr = Const(0.0)
        assert count_terms(expr) == 1

    def test_zero_multiply_expression(self):
        """0*(x+y) is 1 term (product, not simplified)."""
        expr = Binary("*", Const(0.0), Binary("+", VarRef("x"), VarRef("y")))
        assert count_terms(expr) == 1


class TestSimplificationMetrics:
    """Test SimplificationMetrics class."""

    def test_initialization(self):
        """Metrics initializes with model name and zero counts."""
        metrics = SimplificationMetrics(model="test.eq1")
        assert metrics.model == "test.eq1"
        assert metrics.ops_before == 0
        assert metrics.ops_after == 0
        assert metrics.terms_before == 0
        assert metrics.terms_after == 0
        assert metrics.execution_time_ms == 0.0
        assert metrics.transformations_applied == {}

    def test_calculate_reductions_normal(self):
        """Calculate reductions with normal values."""
        metrics = SimplificationMetrics(model="test")
        metrics.ops_before = 10
        metrics.ops_after = 3
        metrics.terms_before = 5
        metrics.terms_after = 2

        reductions = metrics.calculate_reductions()
        assert reductions["ops_reduction_pct"] == 70.0
        assert reductions["terms_reduction_pct"] == 60.0

    def test_calculate_reductions_no_reduction(self):
        """Calculate reductions when no simplification occurred."""
        metrics = SimplificationMetrics(model="test")
        metrics.ops_before = 10
        metrics.ops_after = 10
        metrics.terms_before = 5
        metrics.terms_after = 5

        reductions = metrics.calculate_reductions()
        assert reductions["ops_reduction_pct"] == 0.0
        assert reductions["terms_reduction_pct"] == 0.0

    def test_calculate_reductions_zero_before(self):
        """Calculate reductions with zero before count (prevent division by zero)."""
        metrics = SimplificationMetrics(model="test")
        metrics.ops_before = 0
        metrics.ops_after = 0
        metrics.terms_before = 0
        metrics.terms_after = 0

        reductions = metrics.calculate_reductions()
        assert reductions["ops_reduction_pct"] == 0.0
        assert reductions["terms_reduction_pct"] == 0.0

    def test_calculate_reductions_perfect_reduction(self):
        """Calculate reductions with 100% reduction."""
        metrics = SimplificationMetrics(model="test")
        metrics.ops_before = 10
        metrics.ops_after = 0
        metrics.terms_before = 5
        metrics.terms_after = 0

        reductions = metrics.calculate_reductions()
        assert reductions["ops_reduction_pct"] == 100.0
        assert reductions["terms_reduction_pct"] == 100.0

    def test_record_transformation_single(self):
        """Record single transformation application."""
        metrics = SimplificationMetrics(model="test")
        metrics.record_transformation("CSE")

        assert metrics.transformations_applied == {"CSE": 1}

    def test_record_transformation_multiple_same(self):
        """Record multiple applications of same transformation."""
        metrics = SimplificationMetrics(model="test")
        metrics.record_transformation("CSE")
        metrics.record_transformation("CSE")
        metrics.record_transformation("CSE")

        assert metrics.transformations_applied == {"CSE": 3}

    def test_record_transformation_multiple_different(self):
        """Record multiple different transformations."""
        metrics = SimplificationMetrics(model="test")
        metrics.record_transformation("CSE")
        metrics.record_transformation("ConstantFold")
        metrics.record_transformation("CSE")
        metrics.record_transformation("ZeroElimination")

        assert metrics.transformations_applied == {
            "CSE": 2,
            "ConstantFold": 1,
            "ZeroElimination": 1,
        }

    def test_to_dict_complete(self):
        """Convert complete metrics to dictionary."""
        metrics = SimplificationMetrics(model="rbrock.eq1")
        metrics.ops_before = 10
        metrics.ops_after = 3
        metrics.terms_before = 5
        metrics.terms_after = 2
        metrics.execution_time_ms = 1.23456
        metrics.record_transformation("CSE")
        metrics.record_transformation("ConstantFold")

        data = metrics.to_dict()

        assert data["model"] == "rbrock.eq1"
        assert data["ops_before"] == 10
        assert data["ops_after"] == 3
        assert data["terms_before"] == 5
        assert data["terms_after"] == 2
        assert data["execution_time_ms"] == 1.235  # Rounded to 3 decimals
        assert data["transformations_applied"] == {"CSE": 1, "ConstantFold": 1}
        assert data["ops_reduction_pct"] == 70.0
        assert data["terms_reduction_pct"] == 60.0

    def test_to_dict_no_transformations(self):
        """Convert metrics with no transformations to dictionary."""
        metrics = SimplificationMetrics(model="test")
        metrics.ops_before = 5
        metrics.ops_after = 5
        metrics.terms_before = 3
        metrics.terms_after = 3

        data = metrics.to_dict()

        assert data["transformations_applied"] == {}
        assert data["ops_reduction_pct"] == 0.0
        assert data["terms_reduction_pct"] == 0.0

    def test_to_dict_timing_precision(self):
        """Verify execution time is rounded to 3 decimal places."""
        metrics = SimplificationMetrics(model="test")
        metrics.execution_time_ms = 1.23456789

        data = metrics.to_dict()

        assert data["execution_time_ms"] == 1.235


class TestCountTermsValidationCases:
    """Additional validation test cases from Sprint 12 Prep Task 7 prototype."""

    def test_prototype_case_rbrock_eq1(self):
        """From prototype: x + y."""
        expr = Binary("+", VarRef("x"), VarRef("y"))
        assert count_terms(expr) == 2

    def test_prototype_case_rbrock_eq2(self):
        """From prototype: 2*x."""
        expr = Binary("*", Const(2.0), VarRef("x"))
        assert count_terms(expr) == 1

    def test_prototype_case_rbrock_eq3(self):
        """From prototype: 3*a + 3*b."""
        expr = Binary(
            "+",
            Binary("*", Const(3.0), VarRef("a")),
            Binary("*", Const(3.0), VarRef("b")),
        )
        assert count_terms(expr) == 2

    def test_prototype_case_mhw4d_eq1(self):
        """From prototype: x*y + x*z."""
        expr = Binary(
            "+",
            Binary("*", VarRef("x"), VarRef("y")),
            Binary("*", VarRef("x"), VarRef("z")),
        )
        assert count_terms(expr) == 2

    def test_prototype_case_mhw4d_eq3(self):
        """From prototype: 2*x / 2 (should be 1 term, quotient)."""
        expr = Binary("/", Binary("*", Const(2.0), VarRef("x")), Const(2.0))
        assert count_terms(expr) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
