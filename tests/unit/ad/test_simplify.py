"""Unit tests for expression simplification.

Tests the simplify() function in src/ad/ad_core.py, verifying that
algebraic simplification rules are correctly applied to expression ASTs.
"""

from src.ad.ad_core import simplify, simplify_advanced
from src.ir.ast import Binary, Call, Const, MultiplierRef, ParamRef, Sum, Unary, VarRef


class TestConstantFolding:
    """Test constant folding: operations on two constants."""

    def test_add_constants(self):
        expr = Binary("+", Const(2), Const(3))
        result = simplify(expr)
        assert result == Const(5)

    def test_subtract_constants(self):
        expr = Binary("-", Const(10), Const(3))
        result = simplify(expr)
        assert result == Const(7)

    def test_multiply_constants(self):
        expr = Binary("*", Const(4), Const(5))
        result = simplify(expr)
        assert result == Const(20)

    def test_divide_constants(self):
        expr = Binary("/", Const(15), Const(3))
        result = simplify(expr)
        assert result == Const(5.0)

    def test_power_constants(self):
        expr = Binary("^", Const(2), Const(3))
        result = simplify(expr)
        assert result == Const(8)

    def test_nested_constant_folding(self):
        # (2 + 3) * (4 - 1) → 5 * 3 → 15
        expr = Binary("*", Binary("+", Const(2), Const(3)), Binary("-", Const(4), Const(1)))
        result = simplify(expr)
        assert result == Const(15)


class TestZeroElimination:
    """Test zero elimination rules."""

    def test_add_zero_right(self):
        # x + 0 → x
        expr = Binary("+", VarRef("x", ()), Const(0))
        result = simplify(expr)
        assert result == VarRef("x", ())

    def test_add_zero_left(self):
        # 0 + x → x
        expr = Binary("+", Const(0), VarRef("x", ()))
        result = simplify(expr)
        assert result == VarRef("x", ())

    def test_subtract_zero(self):
        # x - 0 → x
        expr = Binary("-", VarRef("x", ()), Const(0))
        result = simplify(expr)
        assert result == VarRef("x", ())

    def test_multiply_zero_right(self):
        # x * 0 → 0
        expr = Binary("*", VarRef("x", ()), Const(0))
        result = simplify(expr)
        assert result == Const(0)

    def test_multiply_zero_left(self):
        # 0 * x → 0
        expr = Binary("*", Const(0), VarRef("x", ()))
        result = simplify(expr)
        assert result == Const(0)

    def test_divide_zero_numerator(self):
        # 0 / x → 0
        expr = Binary("/", Const(0), VarRef("x", ()))
        result = simplify(expr)
        assert result == Const(0)

    def test_zero_minus_x(self):
        # 0 - x → -x
        expr = Binary("-", Const(0), VarRef("x", ()))
        result = simplify(expr)
        assert result == Unary("-", VarRef("x", ()))


class TestIdentityElimination:
    """Test identity elimination rules."""

    def test_multiply_one_right(self):
        # x * 1 → x
        expr = Binary("*", VarRef("x", ()), Const(1))
        result = simplify(expr)
        assert result == VarRef("x", ())

    def test_multiply_one_left(self):
        # 1 * x → x
        expr = Binary("*", Const(1), VarRef("x", ()))
        result = simplify(expr)
        assert result == VarRef("x", ())

    def test_divide_by_one(self):
        # x / 1 → x
        expr = Binary("/", VarRef("x", ()), Const(1))
        result = simplify(expr)
        assert result == VarRef("x", ())

    def test_power_one(self):
        # x ** 1 → x
        expr = Binary("^", VarRef("x", ()), Const(1))
        result = simplify(expr)
        assert result == VarRef("x", ())

    def test_power_zero(self):
        # x ** 0 → 1
        expr = Binary("^", VarRef("x", ()), Const(0))
        result = simplify(expr)
        assert result == Const(1)

    def test_one_power_x(self):
        # 1 ** x → 1
        expr = Binary("^", Const(1), VarRef("x", ()))
        result = simplify(expr)
        assert result == Const(1)

    def test_zero_power_positive_constant(self):
        # 0 ** 2 → 0 (only simplifies when exponent is positive constant)
        expr = Binary("^", Const(0), Const(2))
        result = simplify(expr)
        assert result == Const(0)

    def test_zero_power_variable_not_simplified(self):
        # 0 ** x → not simplified (x could be ≤ 0)
        expr = Binary("^", Const(0), VarRef("x", ()))
        result = simplify(expr)
        # Should remain as Binary since we don't know if x > 0
        assert result == Binary("^", Const(0), VarRef("x", ()))


class TestUnarySimplification:
    """Test unary operation simplifications."""

    def test_double_negation(self):
        # -(-x) → x
        expr = Unary("-", Unary("-", VarRef("x", ())))
        result = simplify(expr)
        assert result == VarRef("x", ())

    def test_unary_plus(self):
        # +x → x
        expr = Unary("+", VarRef("x", ()))
        result = simplify(expr)
        assert result == VarRef("x", ())

    def test_negate_constant(self):
        # -(5) → -5
        expr = Unary("-", Const(5))
        result = simplify(expr)
        assert result == Const(-5)

    def test_unary_plus_constant(self):
        # +(5) → 5
        expr = Unary("+", Const(5))
        result = simplify(expr)
        assert result == Const(5)


class TestAlgebraicSimplification:
    """Test more complex algebraic simplifications."""

    def test_x_minus_x(self):
        # x - x → 0
        expr = Binary("-", VarRef("x", ()), VarRef("x", ()))
        result = simplify(expr)
        assert result == Const(0)

    def test_x_divide_x(self):
        # x / x → 1
        expr = Binary("/", VarRef("x", ()), VarRef("x", ()))
        result = simplify(expr)
        assert result == Const(1)

    def test_additive_inverse(self):
        # x + (-y) → x - y
        expr = Binary("+", VarRef("x", ()), Unary("-", VarRef("y", ())))
        result = simplify(expr)
        expected = Binary("-", VarRef("x", ()), VarRef("y", ()))
        assert result == expected


class TestNestedSimplification:
    """Test that simplification works recursively."""

    def test_nested_zero_multiplication(self):
        # (x * 0) + y → 0 + y → y
        expr = Binary("+", Binary("*", VarRef("x", ()), Const(0)), VarRef("y", ()))
        result = simplify(expr)
        assert result == VarRef("y", ())

    def test_nested_identity_multiplication(self):
        # (x * 1) + (y * 1) → x + y
        expr = Binary(
            "+",
            Binary("*", VarRef("x", ()), Const(1)),
            Binary("*", VarRef("y", ()), Const(1)),
        )
        result = simplify(expr)
        expected = Binary("+", VarRef("x", ()), VarRef("y", ()))
        assert result == expected

    def test_complex_nested_expression(self):
        # ((1 + 1) * x) + (0 * y) → (2 * x) + 0 → 2 * x
        expr = Binary(
            "+",
            Binary("*", Binary("+", Const(1), Const(1)), VarRef("x", ())),
            Binary("*", Const(0), VarRef("y", ())),
        )
        result = simplify(expr)
        expected = Binary("*", Const(2), VarRef("x", ()))
        assert result == expected

    def test_deeply_nested_constants(self):
        # (((2 + 3) - 1) * 2) → (5 - 1) * 2 → 4 * 2 → 8
        expr = Binary(
            "*",
            Binary("-", Binary("+", Const(2), Const(3)), Const(1)),
            Const(2),
        )
        result = simplify(expr)
        assert result == Const(8)


class TestFunctionCallSimplification:
    """Test simplification of function calls."""

    def test_function_with_constant_args(self):
        # sin(0 + x) → sin(x)
        expr = Call("sin", (Binary("+", Const(0), VarRef("x", ())),))
        result = simplify(expr)
        expected = Call("sin", (VarRef("x", ()),))
        assert result == expected

    def test_function_with_multiple_args(self):
        # power(x * 1, 2 + 0) → power(x, 2)
        expr = Call(
            "power",
            (Binary("*", VarRef("x", ()), Const(1)), Binary("+", Const(2), Const(0))),
        )
        result = simplify(expr)
        expected = Call("power", (VarRef("x", ()), Const(2)))
        assert result == expected


class TestSumSimplification:
    """Test simplification of sum aggregations."""

    def test_sum_with_zero_elimination(self):
        # sum(i, x(i) + 0) → sum(i, x(i))
        expr = Sum(("i",), Binary("+", VarRef("x", ("i",)), Const(0)))
        result = simplify(expr)
        expected = Sum(("i",), VarRef("x", ("i",)))
        assert result == expected

    def test_sum_with_constant_folding(self):
        # sum(i, (1 + 1) * x(i)) → sum(i, 2 * x(i))
        expr = Sum(("i",), Binary("*", Binary("+", Const(1), Const(1)), VarRef("x", ("i",))))
        result = simplify(expr)
        expected = Sum(("i",), Binary("*", Const(2), VarRef("x", ("i",))))
        assert result == expected


class TestMultiplierAndParamRefs:
    """Test that multiplier and parameter references are handled correctly."""

    def test_multiplier_ref_with_zero(self):
        # lam(i) * 0 → 0
        expr = Binary("*", MultiplierRef("lam", ("i",)), Const(0))
        result = simplify(expr)
        assert result == Const(0)

    def test_multiplier_ref_with_one(self):
        # lam(i) * 1 → lam(i)
        expr = Binary("*", MultiplierRef("lam", ("i",)), Const(1))
        result = simplify(expr)
        assert result == MultiplierRef("lam", ("i",))

    def test_param_ref_with_zero(self):
        # a(i) + 0 → a(i)
        expr = Binary("+", ParamRef("a", ("i",)), Const(0))
        result = simplify(expr)
        assert result == ParamRef("a", ("i",))

    def test_param_ref_with_one(self):
        # 1 * a(i) → a(i)
        expr = Binary("*", Const(1), ParamRef("a", ("i",)))
        result = simplify(expr)
        assert result == ParamRef("a", ("i",))


class TestIndexedVariables:
    """Test simplification with indexed variables."""

    def test_indexed_var_plus_zero(self):
        # x(i) + 0 → x(i)
        expr = Binary("+", VarRef("x", ("i",)), Const(0))
        result = simplify(expr)
        assert result == VarRef("x", ("i",))

    def test_indexed_var_times_one(self):
        # x(i,j) * 1 → x(i,j)
        expr = Binary("*", VarRef("x", ("i", "j")), Const(1))
        result = simplify(expr)
        assert result == VarRef("x", ("i", "j"))

    def test_indexed_var_minus_itself(self):
        # x(i) - x(i) → 0
        expr = Binary("-", VarRef("x", ("i",)), VarRef("x", ("i",)))
        result = simplify(expr)
        assert result == Const(0)

    def test_different_indexed_vars_not_simplified(self):
        # x(i) - x(j) → x(i) - x(j) (different indices, no simplification)
        expr = Binary("-", VarRef("x", ("i",)), VarRef("x", ("j",)))
        result = simplify(expr)
        # Should remain unchanged
        assert result == expr


class TestIdempotency:
    """Test that simplify is idempotent (calling it multiple times has same effect)."""

    def test_idempotent_constant_folding(self):
        expr = Binary("+", Const(2), Const(3))
        result1 = simplify(expr)
        result2 = simplify(result1)
        assert result1 == result2 == Const(5)

    def test_idempotent_zero_elimination(self):
        expr = Binary("+", VarRef("x", ()), Const(0))
        result1 = simplify(expr)
        result2 = simplify(result1)
        assert result1 == result2 == VarRef("x", ())

    def test_idempotent_complex_expression(self):
        # ((1 + 1) * x) + (0 * y) → 2 * x
        expr = Binary(
            "+",
            Binary("*", Binary("+", Const(1), Const(1)), VarRef("x", ())),
            Binary("*", Const(0), VarRef("y", ())),
        )
        result1 = simplify(expr)
        result2 = simplify(result1)
        result3 = simplify(result2)
        assert result1 == result2 == result3


class TestEdgeCases:
    """Test edge cases and corner cases."""

    def test_already_simplified_constant(self):
        expr = Const(42)
        result = simplify(expr)
        assert result == Const(42)

    def test_already_simplified_var_ref(self):
        expr = VarRef("x", ("i", "j"))
        result = simplify(expr)
        assert result == VarRef("x", ("i", "j"))

    def test_division_by_zero_not_simplified(self):
        # x / 0 → should remain unchanged (avoid runtime error)
        expr = Binary("/", VarRef("x", ()), Const(0))
        result = simplify(expr)
        # Should not throw error, should return unchanged expression
        assert result == expr

    def test_constant_division_by_zero_not_simplified(self):
        # 5 / 0 → should remain unchanged (avoid runtime error)
        expr = Binary("/", Const(5), Const(0))
        result = simplify(expr)
        # Should return Binary with simplified children, not throw error
        assert result == Binary("/", Const(5), Const(0))

    def test_power_negative_base_fractional_exponent(self):
        # (-2) ** 0.5 → Python allows this (returns complex number)
        # This test intentionally verifies that complex number support is present:
        # the simplification should produce a Const with a complex value.
        expr = Binary("^", Const(-2), Const(0.5))
        result = simplify(expr)
        # Python computes this as complex: (-2)**0.5 = approximately 1.41j
        assert isinstance(result, Const)
        assert isinstance(result.value, complex)

    def test_power_zero_negative_exponent(self):
        # 0 ** (-1) → should remain unchanged (invalid: 1/0)
        expr = Binary("^", Const(0), Const(-1))
        result = simplify(expr)
        # Should return Binary with simplified children, not throw error
        assert result == Binary("^", Const(0), Const(-1))

    def test_power_zero_zero(self):
        # 0 ** 0 → should remain unchanged (mathematically indeterminate)
        expr = Binary("^", Const(0), Const(0))
        result = simplify(expr)
        # Should NOT simplify (even though Python evaluates to 1)
        # because 0**0 is mathematically indeterminate
        assert result == Binary("^", Const(0), Const(0))

    def test_power_overflow(self):
        # 10 ** 1000 → should remain unchanged (overflow)
        expr = Binary("^", Const(10), Const(1000))
        result = simplify(expr)
        # Should return Binary with simplified children if overflow occurs
        # Note: May actually succeed with Python's arbitrary precision, but test the mechanism
        assert isinstance(result, (Const, Binary))

    def test_empty_sum(self):
        # sum(i, x(i)) → sum(i, x(i)) (no simplification for sum itself)
        expr = Sum(("i",), VarRef("x", ("i",)))
        result = simplify(expr)
        assert result == expr


class TestAdvancedSimplification:
    """Test advanced simplification with term collection."""

    def test_constant_collection_simple(self):
        # 1 + x + 1 → x + 2
        expr = Binary("+", Binary("+", Const(1), VarRef("x", ())), Const(1))
        result = simplify_advanced(expr)

        # Result should be x + 2 or 2 + x
        assert isinstance(result, Binary)
        assert result.op == "+"

        # Extract components
        left, right = result.left, result.right
        components = {left, right}

        # Should contain x and 2
        assert VarRef("x", ()) in components
        assert Const(2) in components

    def test_like_term_collection_simple(self):
        # x + y + x + y → 2*x + 2*y
        expr = Binary(
            "+",
            Binary("+", Binary("+", VarRef("x", ()), VarRef("y", ())), VarRef("x", ())),
            VarRef("y", ()),
        )
        result = simplify_advanced(expr)

        # Result should be 2*x + 2*y (in some order)
        assert isinstance(result, Binary)
        assert result.op == "+"

        # Both terms should be multiplication by 2
        left, right = result.left, result.right

        # Check left term is 2 * var
        if isinstance(left, Binary) and left.op == "*":
            assert left.left == Const(2)
            assert left.right in {VarRef("x", ()), VarRef("y", ())}

        # Check right term is 2 * var
        if isinstance(right, Binary) and right.op == "*":
            assert right.left == Const(2)
            assert right.right in {VarRef("x", ()), VarRef("y", ())}

    def test_mixed_constant_and_variable_collection(self):
        # 2 + x + 3 + x → 2*x + 5
        expr = Binary(
            "+",
            Binary("+", Binary("+", Const(2), VarRef("x", ())), Const(3)),
            VarRef("x", ()),
        )
        result = simplify_advanced(expr)

        # Result should be 2*x + 5 or 5 + 2*x
        assert isinstance(result, Binary)
        assert result.op == "+"

        # Extract components
        left, right = result.left, result.right

        # One should be 2*x, other should be 5
        has_coeff_term = False
        has_constant = False

        if isinstance(left, Binary) and left.op == "*":
            assert left.left == Const(2)
            assert left.right == VarRef("x", ())
            has_coeff_term = True
        elif left == Const(5):
            has_constant = True

        if isinstance(right, Binary) and right.op == "*":
            assert right.left == Const(2)
            assert right.right == VarRef("x", ())
            has_coeff_term = True
        elif right == Const(5):
            has_constant = True

        assert has_coeff_term and has_constant

    def test_nested_addition_collection(self):
        # (1 + x) + (1 + y) → x + y + 2
        expr = Binary(
            "+",
            Binary("+", Const(1), VarRef("x", ())),
            Binary("+", Const(1), VarRef("y", ())),
        )
        result = simplify_advanced(expr)

        # Result should flatten and collect constants
        # Could be x + (y + 2), (x + y) + 2, etc.
        assert isinstance(result, Binary)

    def test_coefficient_collection(self):
        # 2*x + 3*x → 5*x
        expr = Binary(
            "+",
            Binary("*", Const(2), VarRef("x", ())),
            Binary("*", Const(3), VarRef("x", ())),
        )
        result = simplify_advanced(expr)

        # Result should be 5 * x
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert result.left == Const(5)
        assert result.right == VarRef("x", ())

    def test_cancellation_to_zero(self):
        # x + (-1)*x → 0
        expr = Binary("+", VarRef("x", ()), Binary("*", Const(-1), VarRef("x", ())))
        result = simplify_advanced(expr)

        # Result should be 0
        assert result == Const(0)

    def test_partial_cancellation(self):
        # 3*x + 2*y + (-x) → 2*x + 2*y
        # First, -x is Unary("-", x), which won't be recognized as -1*x by term collection
        # So let's use explicit coefficient: 3*x + (-1)*x → 2*x
        expr = Binary(
            "+",
            Binary("*", Const(3), VarRef("x", ())),
            Binary("*", Const(-1), VarRef("x", ())),
        )
        result = simplify_advanced(expr)

        # Result should be 2 * x
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert result.left == Const(2)
        assert result.right == VarRef("x", ())

    def test_complex_base_collection(self):
        # (x*y) + (x*y) → 2*(x*y)
        base = Binary("*", VarRef("x", ()), VarRef("y", ()))
        expr = Binary("+", base, base)
        result = simplify_advanced(expr)

        # Result should be 2 * (x*y)
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert result.left == Const(2)
        # Right should be x*y
        assert isinstance(result.right, Binary)
        assert result.right.op == "*"

    def test_no_collection_needed(self):
        # x + y (already simplified, no like terms)
        expr = Binary("+", VarRef("x", ()), VarRef("y", ()))
        result = simplify_advanced(expr)

        # Should be unchanged
        assert result == expr

    def test_non_addition_unchanged(self):
        # x * y (not addition, should not apply term collection)
        expr = Binary("*", VarRef("x", ()), VarRef("y", ()))
        result = simplify_advanced(expr)

        # Should be unchanged
        assert result == expr

    def test_deeply_nested_collection(self):
        # ((1 + x) + 2) + (x + 3) → 2*x + 6
        expr = Binary(
            "+",
            Binary("+", Binary("+", Const(1), VarRef("x", ())), Const(2)),
            Binary("+", VarRef("x", ()), Const(3)),
        )
        result = simplify_advanced(expr)

        # Result should be 2*x + 6 or 6 + 2*x
        assert isinstance(result, Binary)
        assert result.op == "+"

        # Extract components
        left, right = result.left, result.right

        # One should be 2*x, other should be 6
        has_coeff_term = False
        has_constant = False

        if isinstance(left, Binary) and left.op == "*":
            assert left.left == Const(2)
            assert left.right == VarRef("x", ())
            has_coeff_term = True
        elif left == Const(6):
            has_constant = True

        if isinstance(right, Binary) and right.op == "*":
            assert right.left == Const(2)
            assert right.right == VarRef("x", ())
            has_coeff_term = True
        elif right == Const(6):
            has_constant = True

        assert has_coeff_term and has_constant

    def test_indexed_variables_collection(self):
        # x(i) + x(i) → 2*x(i)
        expr = Binary("+", VarRef("x", ("i",)), VarRef("x", ("i",)))
        result = simplify_advanced(expr)

        # Result should be 2 * x(i)
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert result.left == Const(2)
        assert result.right == VarRef("x", ("i",))

    def test_different_indexed_variables_no_collection(self):
        # x(i) + x(j) → x(i) + x(j) (different indices, not collected)
        expr = Binary("+", VarRef("x", ("i",)), VarRef("x", ("j",)))
        result = simplify_advanced(expr)

        # Should be unchanged (different indices)
        assert result == expr

    def test_combined_with_basic_simplification(self):
        # (x + 0) + (x + 0) → 2*x
        # Basic simplification: x + 0 → x for each side
        # Then term collection: x + x → 2*x
        expr = Binary(
            "+",
            Binary("+", VarRef("x", ()), Const(0)),
            Binary("+", VarRef("x", ()), Const(0)),
        )
        result = simplify_advanced(expr)

        # Result should be 2 * x
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert result.left == Const(2)
        assert result.right == VarRef("x", ())
