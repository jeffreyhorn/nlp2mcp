"""Unit tests for term reduction metrics collection.

Tests count_terms(), count_operations() functions and TermReductionMetrics class.

Sprint 12 Day 1: Measurement Infrastructure Setup
"""

import pytest

from src.ir.ast import (
    Binary,
    Call,
    CompileTimeConstant,
    Const,
    EquationRef,
    IndexOffset,
    MultiplierRef,
    ParamRef,
    Sum,
    SymbolRef,
    Unary,
    VarRef,
)
from src.ir.metrics import TermReductionMetrics, count_operations, count_terms


class TestCountOperations:
    """Test count_operations() function."""

    def test_single_constant(self):
        """Single constant is 1 operation."""
        expr = Const(5.0)
        assert count_operations(expr) == 1

    def test_single_variable(self):
        """Single variable is 1 operation."""
        expr = VarRef("x")
        assert count_operations(expr) == 1

    def test_simple_binary(self):
        """x + y is 3 operations (2 vars + 1 binary op)."""
        expr = Binary("+", VarRef("x"), VarRef("y"))
        assert count_operations(expr) == 3

    def test_nested_binary(self):
        """x*y + x*z is 7 operations (4 vars + 2 products + 1 sum)."""
        expr = Binary(
            "+",
            Binary("*", VarRef("x"), VarRef("y")),
            Binary("*", VarRef("x"), VarRef("z")),
        )
        assert count_operations(expr) == 7

    def test_unary_operation(self):
        """-x is 2 operations (1 var + 1 unary op)."""
        expr = Unary("-", VarRef("x"))
        assert count_operations(expr) == 2

    def test_function_call_single_arg(self):
        """sin(x) is 2 operations (1 var + 1 function call)."""
        expr = Call("sin", [VarRef("x")])
        assert count_operations(expr) == 2

    def test_function_call_multiple_args(self):
        """max(x, y, z) is 4 operations (3 vars + 1 function call)."""
        expr = Call("max", [VarRef("x"), VarRef("y"), VarRef("z")])
        assert count_operations(expr) == 4

    def test_sum_aggregation(self):
        """sum(i, x(i)) is 2 operations (1 var + 1 sum aggregation)."""
        expr = Sum(("i",), VarRef("x", ("i",)))
        assert count_operations(expr) == 2

    def test_symbol_ref(self):
        """SymbolRef is 1 operation (scalar symbol reference)."""
        expr = SymbolRef("pi")
        assert count_operations(expr) == 1

    def test_param_ref(self):
        """ParamRef is 1 operation (parameter reference)."""
        expr = ParamRef("demand", ("i",))
        assert count_operations(expr) == 1

    def test_equation_ref(self):
        """EquationRef is 1 operation (equation attribute access)."""
        expr = EquationRef("eqn1", ("i",), "m")
        assert count_operations(expr) == 1

    def test_multiplier_ref(self):
        """MultiplierRef is 1 operation (KKT multiplier reference)."""
        expr = MultiplierRef("lambda", ("i",))
        assert count_operations(expr) == 1

    def test_compile_time_constant(self):
        """CompileTimeConstant is 1 operation (GAMS %...% constant)."""
        expr = CompileTimeConstant(("system", "date"))
        assert count_operations(expr) == 1

    def test_index_offset_simple(self):
        """i++1 is 2 operations (1 index offset + 1 const)."""
        expr = IndexOffset("i", Const(1.0), circular=True)
        assert count_operations(expr) == 2

    def test_index_offset_expression(self):
        """i+j is 2 operations (1 index offset + 1 symbol ref)."""
        expr = IndexOffset("i", SymbolRef("j"), circular=False)
        assert count_operations(expr) == 2


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

    def test_unary_negation(self):
        """Unary -x is 1 term."""
        expr = Unary("-", VarRef("x"))
        assert count_terms(expr) == 1

    def test_unary_plus(self):
        """Unary +x is 1 term."""
        expr = Unary("+", VarRef("x"))
        assert count_terms(expr) == 1

    def test_sum_aggregation(self):
        """sum(i, x(i) + y(i)) is 1 term (aggregation not expanded)."""
        # Sum node with additive body - the sum itself is 1 term
        expr = Sum(("i",), Binary("+", VarRef("x", ("i",)), VarRef("y", ("i",))))
        assert count_terms(expr) == 1


class TestTermReductionMetrics:
    """Test TermReductionMetrics class."""

    def test_initialization(self):
        """Metrics initializes with model name and zero counts."""
        metrics = TermReductionMetrics(model="test.eq1")
        assert metrics.model == "test.eq1"
        assert metrics.ops_before == 0
        assert metrics.ops_after == 0
        assert metrics.terms_before == 0
        assert metrics.terms_after == 0
        assert metrics.execution_time_ms == 0.0
        assert metrics.transformations_applied == {}

    def test_calculate_reductions_normal(self):
        """Calculate reductions with normal values."""
        metrics = TermReductionMetrics(model="test")
        metrics.ops_before = 10
        metrics.ops_after = 3
        metrics.terms_before = 5
        metrics.terms_after = 2

        reductions = metrics.calculate_reductions()
        assert reductions["ops_reduction_pct"] == 70.0
        assert reductions["terms_reduction_pct"] == 60.0

    def test_calculate_reductions_no_reduction(self):
        """Calculate reductions when no simplification occurred."""
        metrics = TermReductionMetrics(model="test")
        metrics.ops_before = 10
        metrics.ops_after = 10
        metrics.terms_before = 5
        metrics.terms_after = 5

        reductions = metrics.calculate_reductions()
        assert reductions["ops_reduction_pct"] == 0.0
        assert reductions["terms_reduction_pct"] == 0.0

    def test_calculate_reductions_zero_before(self):
        """Calculate reductions with zero before count (prevent division by zero)."""
        metrics = TermReductionMetrics(model="test")
        metrics.ops_before = 0
        metrics.ops_after = 0
        metrics.terms_before = 0
        metrics.terms_after = 0

        reductions = metrics.calculate_reductions()
        assert reductions["ops_reduction_pct"] == 0.0
        assert reductions["terms_reduction_pct"] == 0.0

    def test_calculate_reductions_perfect_reduction(self):
        """Calculate reductions with 100% reduction."""
        metrics = TermReductionMetrics(model="test")
        metrics.ops_before = 10
        metrics.ops_after = 0
        metrics.terms_before = 5
        metrics.terms_after = 0

        reductions = metrics.calculate_reductions()
        assert reductions["ops_reduction_pct"] == 100.0
        assert reductions["terms_reduction_pct"] == 100.0

    def test_calculate_reductions_increase(self):
        """Calculate reductions when operations/terms increase (negative reduction)."""
        metrics = TermReductionMetrics(model="test")
        metrics.ops_before = 10
        metrics.ops_after = 15  # Increased
        metrics.terms_before = 5
        metrics.terms_after = 7  # Increased

        reductions = metrics.calculate_reductions()
        # Negative percentages indicate increase rather than reduction
        assert reductions["ops_reduction_pct"] == -50.0
        assert reductions["terms_reduction_pct"] == -40.0

    def test_record_transformation_single(self):
        """Record single transformation application."""
        metrics = TermReductionMetrics(model="test")
        metrics.record_transformation("CSE")

        assert metrics.transformations_applied == {"CSE": 1}

    def test_record_transformation_multiple_same(self):
        """Record multiple applications of same transformation."""
        metrics = TermReductionMetrics(model="test")
        metrics.record_transformation("CSE")
        metrics.record_transformation("CSE")
        metrics.record_transformation("CSE")

        assert metrics.transformations_applied == {"CSE": 3}

    def test_record_transformation_multiple_different(self):
        """Record multiple different transformations."""
        metrics = TermReductionMetrics(model="test")
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
        metrics = TermReductionMetrics(model="rbrock.eq1")
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
        metrics = TermReductionMetrics(model="test")
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
        metrics = TermReductionMetrics(model="test")
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
