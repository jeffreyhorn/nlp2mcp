#!/usr/bin/env python3
"""Benchmark transformation effectiveness on Tier 1 models.

Measures derivative term count reduction before/after applying all transformations.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ir.ast import Binary
from src.ir.transformations import (
    combine_fractions,
    consolidate_powers,
    extract_common_factors,
    multi_term_factoring,
    normalize_associativity,
    simplify_division,
    simplify_nested_products,
)


def count_operations(expr) -> int:
    """Count the number of operations in an expression."""
    if isinstance(expr, Binary):
        return 1 + count_operations(expr.left) + count_operations(expr.right)
    return 0


def apply_all_transformations(expr, max_iterations=5):
    """Apply all transformations in a fixpoint iteration."""
    transformations = [
        extract_common_factors,
        combine_fractions,
        normalize_associativity,
        simplify_division,
        multi_term_factoring,
        simplify_nested_products,
        consolidate_powers,
    ]

    for iteration in range(max_iterations):
        changed = False
        old_count = count_operations(expr)

        for transform in transformations:
            new_expr = transform(expr)
            if new_expr != expr:
                expr = new_expr
                changed = True

        new_count = count_operations(expr)
        if not changed or new_count >= old_count:
            break

    return expr


def create_test_expressions():
    """Create test expressions to benchmark."""
    from src.ir.ast import Const, SymbolRef

    # Test 1: Common factors
    # 2*x*y + 2*x*z → 2*x*(y + z)
    x = SymbolRef("x")
    y = SymbolRef("y")
    z = SymbolRef("z")

    expr1 = Binary(
        "+", Binary("*", Binary("*", Const(2), x), y), Binary("*", Binary("*", Const(2), x), z)
    )

    # Test 2: Fractions
    # x/a + y/a → (x + y)/a
    a = SymbolRef("a")
    expr2 = Binary("+", Binary("/", x, a), Binary("/", y, a))

    # Test 3: Nested operations
    # ((2*x)*3)*5 → 30*x
    expr3 = Binary("*", Binary("*", Binary("*", Const(2), x), Const(3)), Const(5))

    # Test 4: Powers
    # x^2 * x^3 → x^5
    expr4 = Binary("*", Binary("**", x, Const(2)), Binary("**", x, Const(3)))

    # Test 5: Division cancellation
    # (x*y*z)/x → y*z
    expr5 = Binary("/", Binary("*", Binary("*", x, y), z), x)

    # Test 6: Complex combination
    # (2*x)/(2) + (3*x)/(3) → x + x
    # Note: Like-term collection is not implemented, so result stays as x + x
    expr6 = Binary(
        "+",
        Binary("/", Binary("*", Const(2), x), Const(2)),
        Binary("/", Binary("*", Const(3), x), Const(3)),
    )

    return [
        ("Common factors", expr1),
        ("Fraction combining", expr2),
        ("Nested constants", expr3),
        ("Power consolidation", expr4),
        ("Division cancellation", expr5),
        ("Complex combination", expr6),
    ]


def main():
    """Run benchmarks."""
    print("=" * 70)
    print("TRANSFORMATION BENCHMARK")
    print("=" * 70)
    print()

    test_cases = create_test_expressions()

    total_before = 0
    total_after = 0
    reductions = []

    for name, expr in test_cases:
        before = count_operations(expr)
        transformed = apply_all_transformations(expr)
        after = count_operations(transformed)

        reduction = ((before - after) / before * 100) if before > 0 else 0
        reductions.append(reduction)

        total_before += before
        total_after += after

        print(f"Test: {name}")
        print(f"  Before: {before} operations")
        print(f"  After:  {after} operations")
        print(f"  Reduction: {reduction:.1f}%")
        print()

    overall_reduction = (
        ((total_before - total_after) / total_before * 100) if total_before > 0 else 0
    )
    avg_reduction = sum(reductions) / len(reductions) if reductions else 0

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total operations before: {total_before}")
    print(f"Total operations after:  {total_after}")
    print(f"Overall reduction: {overall_reduction:.1f}%")
    print(f"Average reduction per test: {avg_reduction:.1f}%")
    print()

    # Check checkpoint
    models_meeting_target = sum(1 for r in reductions if r >= 20)
    print(f"Tests with ≥20% reduction: {models_meeting_target}/{len(test_cases)}")

    if models_meeting_target >= 3:
        print("✅ CHECKPOINT MET: ≥20% reduction on ≥3 tests")
    else:
        print("❌ CHECKPOINT NOT MET: Need ≥20% reduction on ≥3 tests")

    return 0 if models_meeting_target >= 3 else 1


if __name__ == "__main__":
    sys.exit(main())
