"""Integration tests for metrics collection with SimplificationPipeline.

Tests that metrics collection works correctly with actual simplification.

Sprint 12 Day 1: Extended Testing and Validation
"""

import time

import pytest

from src.ir.ast import Binary, Const, VarRef
from src.ir.metrics import TermReductionMetrics, count_operations, count_terms
from src.ir.simplification_pipeline import SimplificationPipeline


class TestMetricsWithSimplificationPipeline:
    """Test metrics collection integrated with SimplificationPipeline."""

    def test_metrics_on_simple_expression(self):
        """Test basic metrics collection on a simple expression."""
        # Create expression: x + y
        expr = Binary("+", VarRef("x"), VarRef("y"))

        # Create pipeline
        pipeline = SimplificationPipeline(max_iterations=5, size_budget=1.5)

        # Collect metrics manually (simulating benchmarking mode)
        metrics = TermReductionMetrics(model="test.eq1")

        # Before simplification
        metrics.ops_before = count_operations(expr)
        metrics.terms_before = count_terms(expr)

        # Apply simplification with timing
        start = time.perf_counter()
        simplified, _ = pipeline.apply(expr)
        metrics.execution_time_ms = (time.perf_counter() - start) * 1000

        # After simplification
        metrics.ops_after = count_operations(simplified)
        metrics.terms_after = count_terms(simplified)

        # Validate metrics
        assert metrics.ops_before == 3  # Binary node + 2 VarRefs
        assert metrics.ops_after == 3  # No transformations applied
        assert metrics.terms_before == 2  # x + y = 2 terms
        assert metrics.terms_after == 2
        assert metrics.execution_time_ms >= 0  # Some small time

    def test_metrics_with_reduction(self):
        """Test metrics show reduction when simplification occurs."""
        # Create expression: 2*x/2 (should simplify to x with constant fold)
        # Note: This requires the actual transformation to be registered
        # For now, we test the metrics collection infrastructure
        expr = Binary("/", Binary("*", Const(2.0), VarRef("x")), Const(2.0))

        pipeline = SimplificationPipeline(max_iterations=5, size_budget=1.5)

        metrics = TermReductionMetrics(model="test.constant_fold")

        # Before
        metrics.ops_before = count_operations(expr)
        metrics.terms_before = count_terms(expr)

        # Simplify
        start = time.perf_counter()
        simplified, _ = pipeline.apply(expr)
        metrics.execution_time_ms = (time.perf_counter() - start) * 1000

        # After
        metrics.ops_after = count_operations(simplified)
        metrics.terms_after = count_terms(simplified)

        # Validate structure (may not reduce without transformations registered)
        assert metrics.ops_before > 0
        assert metrics.ops_after > 0
        assert metrics.terms_before == 1  # Quotient is 1 term
        assert metrics.terms_after == 1

    def test_metrics_to_dict_conversion(self):
        """Test that metrics can be serialized to dict for JSON output."""
        expr = Binary("+", VarRef("x"), VarRef("y"))
        pipeline = SimplificationPipeline()

        metrics = TermReductionMetrics(model="rbrock.eq1")
        metrics.ops_before = count_operations(expr)
        metrics.terms_before = count_terms(expr)

        simplified, _ = pipeline.apply(expr)

        metrics.ops_after = count_operations(simplified)
        metrics.terms_after = count_terms(simplified)
        metrics.execution_time_ms = 1.234

        data = metrics.to_dict()

        # Validate all fields present
        assert "model" in data
        assert "ops_before" in data
        assert "ops_after" in data
        assert "terms_before" in data
        assert "terms_after" in data
        assert "execution_time_ms" in data
        assert "transformations_applied" in data
        assert "ops_reduction_pct" in data
        assert "terms_reduction_pct" in data

    def test_performance_overhead_acceptable(self):
        """Test that term counting adds minimal overhead to actual pipeline usage.

        In practice, we measure metrics before/after pipeline.apply(), so the overhead
        is count_terms relative to the full pipeline execution time, not just _expression_size.
        """
        expr = Binary(
            "+",
            Binary("+", Binary("*", Const(2.0), VarRef("x")), Binary("*", Const(3.0), VarRef("y"))),
            Binary("+", Binary("*", Const(4.0), VarRef("z")), Binary("*", Const(5.0), VarRef("w"))),
        )

        pipeline = SimplificationPipeline(max_iterations=3)

        # Measure baseline (pipeline.apply without metrics)
        num_runs = 100
        start = time.perf_counter()
        for _ in range(num_runs):
            _, _ = pipeline.apply(expr)
        baseline_ms = (time.perf_counter() - start) * 1000

        # Measure with metrics collection (realistic usage)
        start = time.perf_counter()
        for _ in range(num_runs):
            # This is how we actually use it in measure_simplification.py
            _ = count_terms(expr)  # Before
            simplified, _ = pipeline.apply(expr)
            _ = count_terms(simplified)  # After
        with_metrics_ms = (time.perf_counter() - start) * 1000

        # Calculate overhead
        overhead_pct = (
            ((with_metrics_ms - baseline_ms) / baseline_ms * 100) if baseline_ms > 0 else 0
        )

        # The overhead should be minimal since count_terms is fast relative to pipeline.apply
        # Prototype showed 7.53% overhead for count_terms alone, but when measured against
        # full pipeline execution, overhead should be <30% (count_terms is ~2μs, pipeline is ~30μs)
        # Threshold set to 30% to account for CI environment variance (observed: 26.88% in CI)
        assert overhead_pct < 30.0, f"Overhead {overhead_pct:.2f}% exceeds 30% threshold"

    def test_metrics_on_multiple_expressions(self):
        """Test collecting metrics on multiple expressions (batch mode)."""
        test_cases = [
            ("eq1", Binary("+", VarRef("x"), VarRef("y"))),
            ("eq2", Binary("*", Const(2.0), VarRef("x"))),
            (
                "eq3",
                Binary(
                    "+", Binary("*", Const(3.0), VarRef("a")), Binary("*", Const(3.0), VarRef("b"))
                ),
            ),
        ]

        pipeline = SimplificationPipeline()
        all_metrics = []

        for eq_name, expr in test_cases:
            metrics = TermReductionMetrics(model=f"rbrock.{eq_name}")

            metrics.ops_before = count_operations(expr)
            metrics.terms_before = count_terms(expr)

            start = time.perf_counter()
            simplified, _ = pipeline.apply(expr)
            metrics.execution_time_ms = (time.perf_counter() - start) * 1000

            metrics.ops_after = count_operations(simplified)
            metrics.terms_after = count_terms(simplified)

            all_metrics.append(metrics)

        # Validate we collected metrics for all cases
        assert len(all_metrics) == 3
        assert all_metrics[0].model == "rbrock.eq1"
        assert all_metrics[1].model == "rbrock.eq2"
        assert all_metrics[2].model == "rbrock.eq3"

        # All should have positive operation counts
        assert all(m.ops_before > 0 for m in all_metrics)
        assert all(m.ops_after > 0 for m in all_metrics)

    def test_edge_case_very_large_expression(self):
        """Test metrics on large expression (>500 operations)."""
        # Build a deep expression tree: (((...(x + 1) + 1)...) + 1)
        expr = VarRef("x")
        for _ in range(250):  # 250 additions = ~500 operations
            expr = Binary("+", expr, Const(1.0))

        pipeline = SimplificationPipeline()
        metrics = TermReductionMetrics(model="large_expr")

        metrics.ops_before = count_operations(expr)
        metrics.terms_before = count_terms(expr)

        start = time.perf_counter()
        simplified, _ = pipeline.apply(expr)
        elapsed = (time.perf_counter() - start) * 1000
        metrics.execution_time_ms = elapsed

        metrics.ops_after = count_operations(simplified)
        metrics.terms_after = count_terms(simplified)

        # Validate metrics are reasonable
        assert metrics.ops_before > 500
        assert metrics.terms_before == 251  # x + 250 constants
        assert metrics.execution_time_ms < 1000  # Should be fast (<1 second)

    def test_edge_case_deeply_nested_expression(self):
        """Test metrics on deeply nested expression (>10 levels)."""
        # Build nested expression: (((x + y) + z) + w) + ...
        expr = Binary("+", VarRef("x"), VarRef("y"))
        for idx in range(15):  # 15 levels of nesting
            expr = Binary("+", expr, VarRef(f"v{idx}"))

        pipeline = SimplificationPipeline()
        metrics = TermReductionMetrics(model="nested_expr")

        metrics.ops_before = count_operations(expr)
        metrics.terms_before = count_terms(expr)

        simplified, _ = pipeline.apply(expr)

        metrics.ops_after = count_operations(simplified)
        metrics.terms_after = count_terms(simplified)

        # Should count all additive terms correctly
        assert metrics.terms_before == 17  # x + y + 15 variables


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
