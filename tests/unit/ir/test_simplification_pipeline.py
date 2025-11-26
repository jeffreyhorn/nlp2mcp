"""Tests for the SimplificationPipeline class.

Tests the basic infrastructure of the simplification pipeline including:
- Pass registration
- Priority ordering
- Fixpoint iteration
- Size budget enforcement
- Rollback mechanism
- Metrics collection
"""

from src.ir.ast import Binary, Const
from src.ir.simplification_pipeline import SimplificationMetrics, SimplificationPipeline


class TestPipelineInfrastructure:
    """Test basic pipeline setup and configuration."""

    def test_pipeline_initialization(self):
        """Test pipeline can be initialized with default parameters."""
        pipeline = SimplificationPipeline()
        assert pipeline.max_iterations == 5
        assert pipeline.size_budget == 1.5
        assert len(pipeline.passes) == 0

    def test_pipeline_custom_parameters(self):
        """Test pipeline can be initialized with custom parameters."""
        pipeline = SimplificationPipeline(max_iterations=10, size_budget=2.0)
        assert pipeline.max_iterations == 10
        assert pipeline.size_budget == 2.0

    def test_add_pass(self):
        """Test adding transformation passes to the pipeline."""
        pipeline = SimplificationPipeline()

        def identity_pass(expr):
            return expr

        pipeline.add_pass(identity_pass, priority=1, name="Identity")
        assert len(pipeline.passes) == 1
        assert pipeline.passes[0].name == "Identity"
        assert pipeline.passes[0].priority == 1

    def test_passes_sorted_by_priority(self):
        """Test passes are sorted by priority (lower number first)."""
        pipeline = SimplificationPipeline()

        def pass1(expr):
            return expr

        def pass2(expr):
            return expr

        def pass3(expr):
            return expr

        pipeline.add_pass(pass2, priority=5, name="Pass2")
        pipeline.add_pass(pass1, priority=1, name="Pass1")
        pipeline.add_pass(pass3, priority=3, name="Pass3")

        # Should be sorted: Pass1 (pri=1), Pass3 (pri=3), Pass2 (pri=5)
        assert pipeline.passes[0].name == "Pass1"
        assert pipeline.passes[1].name == "Pass3"
        assert pipeline.passes[2].name == "Pass2"


class TestExpressionSize:
    """Test expression size measurement."""

    def test_constant_size(self):
        """Test size of constant expression."""
        pipeline = SimplificationPipeline()
        expr = Const(42)
        assert pipeline._expression_size(expr) == 1

    def test_binary_op_size(self):
        """Test size of binary operation."""
        pipeline = SimplificationPipeline()
        # 1 + 2 has size 3 (Binary + two Consts)
        expr = Binary("+", Const(1), Const(2))
        assert pipeline._expression_size(expr) == 3

    def test_nested_expression_size(self):
        """Test size of nested expression."""
        pipeline = SimplificationPipeline()
        # (1 + 2) * 3 has size 5
        expr = Binary("*", Binary("+", Const(1), Const(2)), Const(3))
        assert pipeline._expression_size(expr) == 5


class TestPipelineApplication:
    """Test applying the pipeline to expressions."""

    def test_identity_transformation(self):
        """Test pipeline with identity transformation (no changes)."""
        pipeline = SimplificationPipeline()

        def identity(expr):
            return expr

        pipeline.add_pass(identity, priority=1, name="Identity")

        expr = Const(42)
        result, metrics = pipeline.apply(expr)

        assert result == expr
        assert metrics.initial_size == 1
        assert metrics.final_size == 1
        assert metrics.iterations == 1  # Should stop after 1 iteration (no changes)

    def test_constant_transformation(self):
        """Test pipeline with a simple transformation."""
        pipeline = SimplificationPipeline(max_iterations=1)  # Only 1 iteration

        def double_constants(expr):
            """Transform Const(n) to Const(2*n)."""
            if isinstance(expr, Const):
                return Const(expr.value * 2)
            return expr

        pipeline.add_pass(double_constants, priority=1, name="DoubleConst")

        expr = Const(21)
        result, metrics = pipeline.apply(expr)

        assert isinstance(result, Const)
        assert result.value == 42  # 21 * 2 = 42
        assert metrics.passes_applied == ["Iter1:DoubleConst"]

    def test_fixpoint_iteration(self):
        """Test pipeline stops when no more changes occur (fixpoint)."""
        pipeline = SimplificationPipeline(max_iterations=10)

        # This pass only transforms Const(1) to Const(2)
        # After first application, no more changes will occur
        def increment_one(expr):
            if isinstance(expr, Const) and expr.value == 1:
                return Const(2)
            return expr

        pipeline.add_pass(increment_one, priority=1, name="IncrementOne")

        expr = Const(1)
        result, metrics = pipeline.apply(expr)

        assert result.value == 2
        assert metrics.iterations == 2  # Iter 1: change, Iter 2: no change (fixpoint)
        assert len(metrics.passes_applied) == 1

    def test_max_iterations_limit(self):
        """Test pipeline stops at max iterations even if not at fixpoint."""
        pipeline = SimplificationPipeline(max_iterations=3)

        # This pass always increments - never reaches fixpoint
        def always_increment(expr):
            if isinstance(expr, Const):
                return Const(expr.value + 1)
            return expr

        pipeline.add_pass(always_increment, priority=1, name="AlwaysIncrement")

        expr = Const(0)
        result, metrics = pipeline.apply(expr)

        # Should increment 3 times (max_iterations)
        assert result.value == 3
        assert metrics.iterations == 3


class TestSizeBudget:
    """Test size budget enforcement and rollback."""

    def test_size_budget_enforcement(self):
        """Test transformations that exceed size budget are rolled back."""
        pipeline = SimplificationPipeline(size_budget=1.5)  # Allow 50% growth

        # This pass doubles the expression size
        def double_size(expr):
            """Replace Const(n) with Binary(n + n)."""
            if isinstance(expr, Const):
                return Binary("+", expr, expr)
            return expr

        pipeline.add_pass(double_size, priority=1, name="DoubleSize")

        # Start with size 1
        expr = Const(42)
        result, metrics = pipeline.apply(expr)

        # Transformation would create size 3 (Binary + 2 Consts)
        # Budget allows max size 1.5, so transformation should be rolled back
        assert result == expr  # No change
        assert metrics.rollbacks == 1
        assert metrics.budget_violations == 1

    def test_size_budget_allows_small_growth(self):
        """Test transformations within budget are allowed."""
        pipeline = SimplificationPipeline(size_budget=3.0)  # Allow 200% growth

        # This pass doubles the expression size
        def double_size(expr):
            if isinstance(expr, Const):
                return Binary("+", expr, expr)
            return expr

        pipeline.add_pass(double_size, priority=1, name="DoubleSize")

        # Start with size 1, budget allows up to size 3
        expr = Const(42)
        result, metrics = pipeline.apply(expr)

        # Transformation creates size 3 - should be allowed
        assert isinstance(result, Binary)
        assert metrics.rollbacks == 0
        assert metrics.budget_violations == 0


class TestMetrics:
    """Test metrics collection."""

    def test_metrics_initialization(self):
        """Test metrics are initialized correctly."""
        metrics = SimplificationMetrics()
        assert metrics.initial_size == 0
        assert metrics.final_size == 0
        assert metrics.iterations == 0
        assert metrics.passes_applied == []
        assert metrics.rollbacks == 0
        assert metrics.budget_violations == 0

    def test_metrics_populated(self):
        """Test metrics are populated during simplification."""
        pipeline = SimplificationPipeline()

        def identity(expr):
            return expr

        pipeline.add_pass(identity, priority=1, name="Identity")

        expr = Binary("+", Const(1), Const(2))
        result, metrics = pipeline.apply(expr)

        assert metrics.initial_size == 3
        assert metrics.final_size == 3
        assert metrics.iterations > 0

    def test_metrics_reuse(self):
        """Test can pass existing metrics object."""
        pipeline = SimplificationPipeline()

        def identity(expr):
            return expr

        pipeline.add_pass(identity, priority=1, name="Identity")

        metrics = SimplificationMetrics()
        expr = Const(42)
        result, returned_metrics = pipeline.apply(expr, metrics=metrics)

        assert returned_metrics is metrics  # Same object
        assert metrics.initial_size == 1
