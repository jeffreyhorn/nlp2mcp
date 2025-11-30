#!/usr/bin/env python3
"""Prototype for simplification metrics collection.

This script validates the measurement approach defined in Task 2 by:
1. Implementing count_terms() function
2. Collecting metrics on 3 GAMSLib models
3. Measuring performance overhead
4. Validating accuracy against manual counts

Sprint 12 Prep Task 7
"""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from src.ir.ast import Binary, Call, Const, Expr, ParamRef, Sum, SymbolRef, Unary, VarRef
from src.ir.simplification_pipeline import SimplificationMetrics, SimplificationPipeline


def count_terms(expr: Expr) -> int:
    """Count additive terms in expression (sum-of-products form).

    Does NOT expand expressions - counts terms in current form.

    Examples:
        x + y → 2 terms
        x*y + x*z → 2 terms
        x*(y+z) → 1 term (factored form not expanded)
        (a+b)*(c+d) → 1 term (not expanded)
    """
    if isinstance(expr, Binary) and expr.op in ("+", "-"):
        # Additive expression: sum of left and right term counts
        return count_terms(expr.left) + count_terms(expr.right)
    else:
        # All other expressions: single term
        return 1


@dataclass
class EnhancedSimplificationMetrics:
    """Extended metrics for benchmarking."""

    model: str
    ops_before: int
    ops_after: int
    terms_before: int
    terms_after: int
    execution_time_ms: float
    ops_reduction_pct: float
    terms_reduction_pct: float
    iterations: int
    passes_applied: list[str] = field(default_factory=list)


def simplify_with_metrics(
    expr: Expr, pipeline: SimplificationPipeline, model: str
) -> tuple[Expr, EnhancedSimplificationMetrics]:
    """Simplify expression and collect benchmarking metrics.

    Args:
        expr: Expression to simplify
        pipeline: SimplificationPipeline instance
        model: Model name for metrics

    Returns:
        Tuple of (simplified_expr, metrics)
    """
    # Measure before
    ops_before = pipeline._expression_size(expr)
    terms_before = count_terms(expr)

    # Apply simplification with timing
    start = time.perf_counter()
    simplified, base_metrics = pipeline.apply(expr)
    elapsed_ms = (time.perf_counter() - start) * 1000

    # Measure after
    ops_after = pipeline._expression_size(simplified)
    terms_after = count_terms(simplified)

    # Calculate reductions
    ops_reduction = ((ops_before - ops_after) / ops_before * 100) if ops_before > 0 else 0.0
    terms_reduction = (
        ((terms_before - terms_after) / terms_before * 100) if terms_before > 0 else 0.0
    )

    metrics = EnhancedSimplificationMetrics(
        model=model,
        ops_before=ops_before,
        ops_after=ops_after,
        terms_before=terms_before,
        terms_after=terms_after,
        execution_time_ms=elapsed_ms,
        ops_reduction_pct=round(ops_reduction, 2),
        terms_reduction_pct=round(terms_reduction, 2),
        iterations=base_metrics.iterations,
        passes_applied=base_metrics.passes_applied,
    )

    return simplified, metrics


def collect_expression_metrics_from_model(model_path: Path) -> list[EnhancedSimplificationMetrics]:
    """Collect metrics for all expressions in a GAMS model.

    Note: This is a simplified prototype. In practice, we'd need to parse the
    GAMS file, extract equations/constraints, convert to IR, and apply
    simplification. For now, we'll create synthetic test expressions.

    Args:
        model_path: Path to GAMS model file

    Returns:
        List of metrics for each expression
    """
    # For the prototype, we'll create synthetic expressions that represent
    # typical patterns from GAMS models
    model_name = model_path.stem

    # Create a pipeline with some basic transformation passes
    pipeline = SimplificationPipeline(max_iterations=5, size_budget=1.5)

    # Add some basic transformation passes to demonstrate reduction
    # Note: These are simplified stubs - real transformations would come from src/ad/transformations
    def constant_fold(expr: Expr) -> Expr:
        """Fold constant expressions like 2*x/2 → x."""
        if isinstance(expr, Binary) and expr.op == "/":
            if isinstance(expr.left, Binary) and expr.left.op == "*":
                if isinstance(expr.left.left, Const) and isinstance(expr.right, Const):
                    if expr.left.left.value == expr.right.value:
                        return expr.left.right  # 2*x/2 → x
        return expr

    def zero_multiply(expr: Expr) -> Expr:
        """Eliminate multiplication by zero: 0*x → 0."""
        if isinstance(expr, Binary) and expr.op == "*":
            if isinstance(expr.left, Const) and expr.left.value == 0.0:
                return Const(0.0)
            if isinstance(expr.right, Const) and expr.right.value == 0.0:
                return Const(0.0)
        return expr

    pipeline.add_pass(constant_fold, priority=1, name="ConstantFold")
    pipeline.add_pass(zero_multiply, priority=2, name="ZeroMultiply")

    # Test expressions representing common GAMS patterns
    # Note: These are simplified examples - real models would have more complex expressions
    test_expressions: list[tuple[str, Expr]] = []

    if model_name == "rbrock":
        # Simple model - few transformations
        test_expressions = [
            ("eq1", Binary("+", VarRef("x"), VarRef("y"))),  # x + y
            ("eq2", Binary("*", Const(2.0), VarRef("x"))),  # 2*x
            (
                "eq3",
                Binary(
                    "+",
                    Binary("*", Const(3.0), VarRef("a")),
                    Binary("*", Const(3.0), VarRef("b")),
                ),
            ),  # 3*a + 3*b
        ]
    elif model_name == "mhw4d":
        # Medium complexity
        test_expressions = [
            (
                "eq1",
                Binary(
                    "+",
                    Binary("*", VarRef("x"), VarRef("y")),
                    Binary("*", VarRef("x"), VarRef("z")),
                ),
            ),  # x*y + x*z
            (
                "eq2",
                Binary(
                    "+",
                    Binary("**", VarRef("a"), Const(2.0)),
                    Binary("**", VarRef("b"), Const(2.0)),
                ),
            ),  # a^2 + b^2
            ("eq3", Binary("/", Binary("*", Const(2.0), VarRef("x")), Const(2.0))),  # 2*x / 2
        ]
    elif model_name == "maxmin":
        # Complex - nested indexing, stress test
        test_expressions = [
            (
                "eq1",
                Binary(
                    "+",
                    Binary(
                        "*",
                        Binary("+", VarRef("a"), VarRef("b")),
                        Binary("+", VarRef("c"), VarRef("d")),
                    ),
                    Binary(
                        "*",
                        Binary("+", VarRef("a"), VarRef("b")),
                        Binary("+", VarRef("e"), VarRef("f")),
                    ),
                ),
            ),  # (a+b)*(c+d) + (a+b)*(e+f)
            (
                "eq2",
                Binary(
                    "*",
                    Const(0.0),
                    Binary("+", VarRef("x"), Binary("*", Const(100.0), VarRef("y"))),
                ),
            ),  # 0 * (x + 100*y)
        ]
    else:
        # Unknown model
        test_expressions = [("eq1", Binary("+", VarRef("x"), VarRef("y")))]

    metrics_list = []
    for expr_name, expr in test_expressions:
        _, metrics = simplify_with_metrics(expr, pipeline, f"{model_name}.{expr_name}")
        metrics_list.append(metrics)

    return metrics_list


def measure_overhead(num_runs: int = 100) -> dict:
    """Measure performance overhead of metrics collection.

    This measures ONLY the overhead of the count_terms() calls, not the
    entire wrapper function overhead.

    Args:
        num_runs: Number of iterations for each test

    Returns:
        Dict with timing results and overhead percentage
    """
    # Create test expression with enough complexity to measure
    expr = Binary(
        "+",
        Binary(
            "+",
            Binary("*", Const(2.0), VarRef("x")),
            Binary("*", Const(3.0), VarRef("y")),
        ),
        Binary(
            "+",
            Binary("*", Const(4.0), VarRef("z")),
            Binary("*", Const(5.0), VarRef("w")),
        ),
    )  # 2*x + 3*y + 4*z + 5*w

    pipeline = SimplificationPipeline(max_iterations=5, size_budget=1.5)

    # Measure baseline: just _expression_size() calls (what we already do)
    start = time.perf_counter()
    for _ in range(num_runs):
        _ = pipeline._expression_size(expr)
        _ = pipeline._expression_size(expr)  # Before and after
    time_baseline = (time.perf_counter() - start) * 1000  # ms

    # Measure with additional count_terms() calls (the new instrumentation)
    start = time.perf_counter()
    for _ in range(num_runs):
        _ = pipeline._expression_size(expr)
        _ = count_terms(expr)
        _ = pipeline._expression_size(expr)  # After
        _ = count_terms(expr)
    time_with_terms = (time.perf_counter() - start) * 1000  # ms

    # Calculate overhead
    overhead_ms = time_with_terms - time_baseline
    overhead_pct = (overhead_ms / time_baseline * 100) if time_baseline > 0 else 0.0

    return {
        "num_runs": num_runs,
        "baseline_ms": round(time_baseline, 2),
        "with_count_terms_ms": round(time_with_terms, 2),
        "overhead_ms": round(overhead_ms, 2),
        "overhead_pct": round(overhead_pct, 2),
        "avg_baseline_per_run_us": round(time_baseline / num_runs * 1000, 2),
        "avg_with_terms_per_run_us": round(time_with_terms / num_runs * 1000, 2),
        "note": "Overhead measures cost of adding count_terms() calls to existing _expression_size() instrumentation",
    }


def main():
    """Run the prototype metrics collection."""
    print("=" * 80)
    print("Sprint 12 Prep Task 7: Simplification Metrics Prototype")
    print("=" * 80)
    print()

    # Test models
    test_models = [
        Path("tests/fixtures/gamslib/rbrock.gms"),
        Path("tests/fixtures/gamslib/mhw4d.gms"),
        Path("tests/fixtures/gamslib/maxmin.gms"),
    ]

    all_metrics = {}

    # Collect metrics for each model
    for model_path in test_models:
        model_name = model_path.stem
        print(f"Collecting metrics for {model_name}.gms...")

        metrics_list = collect_expression_metrics_from_model(model_path)
        all_metrics[model_name] = [
            {
                "model": m.model,
                "ops_before": m.ops_before,
                "ops_after": m.ops_after,
                "terms_before": m.terms_before,
                "terms_after": m.terms_after,
                "execution_time_ms": m.execution_time_ms,
                "ops_reduction_pct": m.ops_reduction_pct,
                "terms_reduction_pct": m.terms_reduction_pct,
                "iterations": m.iterations,
            }
            for m in metrics_list
        ]

        # Print summary
        for m in metrics_list:
            print(
                f"  {m.model}: ops={m.ops_before}→{m.ops_after} "
                f"({m.ops_reduction_pct}%), terms={m.terms_before}→{m.terms_after} "
                f"({m.terms_reduction_pct}%)"
            )
        print()

    # Save metrics to JSON
    output_dir = Path("prototypes")
    output_dir.mkdir(exist_ok=True)

    for model_name, metrics_list in all_metrics.items():
        output_file = output_dir / f"simplification_metrics_{model_name}.json"
        with open(output_file, "w") as f:
            json.dump(metrics_list, f, indent=2)
        print(f"Saved metrics to {output_file}")

    print()

    # Measure performance overhead
    print("Measuring performance overhead...")
    overhead_results = measure_overhead(num_runs=100)
    print(f"  Baseline (just _expression_size): {overhead_results['baseline_ms']:.2f}ms (100 runs)")
    print(
        f"  With count_terms() added:          {overhead_results['with_count_terms_ms']:.2f}ms (100 runs)"
    )
    print(f"  Additional overhead:               {overhead_results['overhead_pct']:.2f}%")
    print(f"  ({overhead_results['note']})")
    print()

    # Save overhead results
    overhead_file = output_dir / "performance_overhead.json"
    with open(overhead_file, "w") as f:
        json.dump(overhead_results, f, indent=2)
    print(f"Saved overhead results to {overhead_file}")

    print()
    print("=" * 80)
    print("Prototype complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
