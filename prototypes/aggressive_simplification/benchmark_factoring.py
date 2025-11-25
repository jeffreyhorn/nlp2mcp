"""
Performance benchmarks for factoring prototype.

Measures execution time and term reduction for various test cases.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from factoring_prototype import count_operations, factor_common_terms

from src.ir.ast import Binary, Const, VarRef


def benchmark_case(name: str, expr, num_iterations: int = 1000):
    """Benchmark a single test case."""
    before_ops = count_operations(expr)

    # Measure execution time
    start_time = time.perf_counter()
    for _ in range(num_iterations):
        result = factor_common_terms(expr)
    end_time = time.perf_counter()

    elapsed_ms = (end_time - start_time) * 1000 / num_iterations
    after_ops = count_operations(result)
    reduction = (before_ops - after_ops) / before_ops * 100 if before_ops > 0 else 0

    print(f"{name}:")
    print(f"  Before: {before_ops} operations")
    print(f"  After:  {after_ops} operations")
    print(f"  Reduction: {reduction:.1f}%")
    print(f"  Time: {elapsed_ms:.4f}ms per expression")
    print()

    return {
        "name": name,
        "before_ops": before_ops,
        "after_ops": after_ops,
        "reduction_pct": reduction,
        "time_ms": elapsed_ms,
    }


def run_benchmarks():
    """Run all performance benchmarks."""
    print("\n=== Factoring Prototype Performance Benchmarks ===\n")

    results = []

    # Benchmark 1: Simple 2-term (x*y + x*z)
    x = VarRef("x")
    y = VarRef("y")
    z = VarRef("z")
    expr1 = Binary("+", Binary("*", x, y), Binary("*", x, z))
    results.append(benchmark_case("Simple 2-term (x*y + x*z)", expr1))

    # Benchmark 2: Three terms (x*y + x*z + x*w)
    w = VarRef("w")
    expr2 = Binary("+", Binary("+", Binary("*", x, y), Binary("*", x, z)), Binary("*", x, w))
    results.append(benchmark_case("Three terms (x*y + x*z + x*w)", expr2))

    # Benchmark 3: Multiple common factors (2*x*y + 2*x*z)
    two = Const(2.0)
    expr3 = Binary("+", Binary("*", Binary("*", two, x), y), Binary("*", Binary("*", two, x), z))
    results.append(benchmark_case("Multiple common (2*x*y + 2*x*z)", expr3))

    # Benchmark 4: PROJECT_PLAN.md example
    exp_x = VarRef("exp_x")
    sin_y = VarRef("sin_y")
    cos_y = VarRef("cos_y")
    expr4 = Binary(
        "+",
        Binary("*", Binary("*", two, exp_x), sin_y),
        Binary("*", Binary("*", two, exp_x), cos_y),
    )
    results.append(benchmark_case("PROJECT_PLAN.md example", expr4))

    # Benchmark 5: Four terms with single common
    a = VarRef("a")
    b = VarRef("b")
    c = VarRef("c")
    d = VarRef("d")
    expr5 = Binary(
        "+",
        Binary("+", Binary("+", Binary("*", x, a), Binary("*", x, b)), Binary("*", x, c)),
        Binary("*", x, d),
    )
    results.append(benchmark_case("Four terms (x*a + x*b + x*c + x*d)", expr5))

    # Benchmark 6: No common factors (should be fast no-op)
    expr6 = Binary("+", Binary("*", x, y), Binary("*", z, w))
    results.append(benchmark_case("No common factors (x*y + z*w)", expr6))

    # Summary
    print("=== Summary ===")
    print()
    avg_reduction = sum(r["reduction_pct"] for r in results if r["reduction_pct"] > 0) / len(
        [r for r in results if r["reduction_pct"] > 0]
    )
    max_time = max(r["time_ms"] for r in results)
    avg_time = sum(r["time_ms"] for r in results) / len(results)

    print(f"Average reduction (when factoring applies): {avg_reduction:.1f}%")
    print(f"Max execution time: {max_time:.4f}ms")
    print(f"Average execution time: {avg_time:.4f}ms")
    print()

    # Check if we meet targets
    target_reduction = 20  # ≥20% reduction target
    target_time = 1  # <1ms target

    print("=== Target Achievement ===")
    print()
    if avg_reduction >= target_reduction:
        print(f"✓ PASS: Average reduction {avg_reduction:.1f}% ≥ {target_reduction}% target")
    else:
        print(f"✗ FAIL: Average reduction {avg_reduction:.1f}% < {target_reduction}% target")

    if max_time < target_time:
        print(f"✓ PASS: Max time {max_time:.4f}ms < {target_time}ms target")
    else:
        print(f"✗ FAIL: Max time {max_time:.4f}ms ≥ {target_time}ms target")

    print()
    return results


if __name__ == "__main__":
    run_benchmarks()
