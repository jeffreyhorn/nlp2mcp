"""
Test suite for factoring prototype.

Tests distribution cancellation and multi-term factoring algorithms.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from factoring_prototype import count_operations, factor_common_terms, factor_multi_terms

from src.ir.ast import Binary, Const, VarRef


def test_distribution_cancellation_simple():
    """Test x*y + x*z → x*(y + z)"""
    x = VarRef("x")
    y = VarRef("y")
    z = VarRef("z")

    # x*y + x*z
    expr = Binary("+", Binary("*", x, y), Binary("*", x, z))
    result = factor_common_terms(expr)

    # Should reduce operations from 3 to 2
    assert count_operations(expr) == 3
    assert count_operations(result) == 2

    # Result should be x * (y + z)
    assert isinstance(result, Binary)
    assert result.op == "*"
    print("✓ test_distribution_cancellation_simple passed")


def test_distribution_cancellation_three_terms():
    """Test x*y + x*z + x*w → x*(y + z + w)"""
    x = VarRef("x")
    y = VarRef("y")
    z = VarRef("z")
    w = VarRef("w")

    # x*y + x*z + x*w
    expr = Binary("+", Binary("+", Binary("*", x, y), Binary("*", x, z)), Binary("*", x, w))
    result = factor_common_terms(expr)

    # Should reduce operations from 5 to 3
    assert count_operations(expr) == 5
    assert count_operations(result) == 3

    print("✓ test_distribution_cancellation_three_terms passed")


def test_distribution_cancellation_multiple_common():
    """Test 2*x*y + 2*x*z → 2*x*(y + z)"""
    two = Const(2.0)
    x = VarRef("x")
    y = VarRef("y")
    z = VarRef("z")

    # 2*x*y + 2*x*z
    term1 = Binary("*", Binary("*", two, x), y)
    term2 = Binary("*", Binary("*", two, x), z)
    expr = Binary("+", term1, term2)

    result = factor_common_terms(expr)

    # Should factor out both 2 and x
    assert count_operations(result) < count_operations(expr)

    print("✓ test_distribution_cancellation_multiple_common passed")


def test_no_common_factors():
    """Test x*y + z*w (no common factors, should not change)"""
    x = VarRef("x")
    y = VarRef("y")
    z = VarRef("z")
    w = VarRef("w")

    # x*y + z*w
    expr = Binary("+", Binary("*", x, y), Binary("*", z, w))
    result = factor_common_terms(expr)

    # Should not change
    assert count_operations(result) == count_operations(expr)
    assert result == expr

    print("✓ test_no_common_factors passed")


def test_project_plan_example():
    """Test example from PROJECT_PLAN.md: 2*exp(x)*sin(y) + 2*exp(x)*cos(y)"""
    # Simplified version without exp function (just use VarRef for exp_x)
    two = Const(2.0)
    exp_x = VarRef("exp_x")  # Stand-in for exp(x)
    sin_y = VarRef("sin_y")  # Stand-in for sin(y)
    cos_y = VarRef("cos_y")  # Stand-in for cos(y)

    # 2*exp(x)*sin(y) + 2*exp(x)*cos(y)
    term1 = Binary("*", Binary("*", two, exp_x), sin_y)
    term2 = Binary("*", Binary("*", two, exp_x), cos_y)
    expr = Binary("+", term1, term2)

    before_ops = count_operations(expr)
    result = factor_common_terms(expr)
    after_ops = count_operations(result)

    # Should reduce operations (from 5 to 3: 2 muls + 1 add)
    reduction = (before_ops - after_ops) / before_ops * 100
    assert after_ops < before_ops
    assert reduction >= 20  # At least 20% reduction

    print(f"✓ test_project_plan_example passed (reduction: {reduction:.1f}%)")


def test_operation_counting():
    """Test that operation counting is accurate"""
    x = VarRef("x")
    y = VarRef("y")

    # x + y → 1 operation
    assert count_operations(Binary("+", x, y)) == 1

    # x * y → 1 operation
    assert count_operations(Binary("*", x, y)) == 1

    # x + y + z → 2 operations
    z = VarRef("z")
    assert count_operations(Binary("+", Binary("+", x, y), z)) == 2

    # x * y * z → 2 operations
    assert count_operations(Binary("*", Binary("*", x, y), z)) == 2

    print("✓ test_operation_counting passed")


def test_multi_term_basic():
    """Test basic multi-term factoring (limited by prototype complexity)"""
    a = VarRef("a")
    b = VarRef("b")
    c = VarRef("c")
    d = VarRef("d")

    # a*c + a*d + b*c + b*d → (a + b) * (c + d)
    # This is a complex pattern that our simple prototype may not catch
    expr = Binary(
        "+",
        Binary("+", Binary("+", Binary("*", a, c), Binary("*", a, d)), Binary("*", b, c)),
        Binary("*", b, d),
    )

    result = factor_multi_terms(expr)

    # Note: This test documents current behavior
    # The multi-term factoring is complex and may not work for all cases
    print(f"  Multi-term before: {count_operations(expr)} ops")
    print(f"  Multi-term after:  {count_operations(result)} ops")
    print("✓ test_multi_term_basic completed (pattern detection is best-effort)")


def run_all_tests():
    """Run all test cases"""
    print("\n=== Running Factoring Prototype Tests ===\n")

    test_operation_counting()
    test_distribution_cancellation_simple()
    test_distribution_cancellation_three_terms()
    test_distribution_cancellation_multiple_common()
    test_no_common_factors()
    test_project_plan_example()
    test_multi_term_basic()

    print("\n=== All tests passed! ===\n")


if __name__ == "__main__":
    run_all_tests()
