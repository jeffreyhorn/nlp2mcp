"""Metrics collection for term reduction benchmarking.

This module provides metrics collection for measuring the effectiveness of
simplification transformations on GAMS expressions. It implements term and
operation counting with minimal performance overhead.

Sprint 12 Day 1: Term Reduction Measurement Infrastructure

Key metrics:
- Operations (ops): Total number of operation nodes in expression tree
- Terms: Additive terms in sum-of-products form (does NOT expand)
- Execution time: Time spent in simplification
- Transformations applied: Count of each transformation invoked

Performance: ~7.5% overhead (validated acceptable for benchmarking mode)
Accuracy: 0% error on manual validation (Sprint 12 Prep Task 7)
"""

from dataclasses import dataclass, field

from src.ir.ast import Binary, Expr


def count_terms(expr: Expr) -> int:
    """Count additive terms in expression (sum-of-products form).

    Does NOT expand expressions - counts terms in current form only.
    This provides insight into structural simplification beyond operation count.

    Algorithm: O(n) recursive traversal of AST
    - Additive operators (+, -): sum of left and right term counts
    - All other expressions: single term (multiplicative, power, etc.)

    Examples:
        x + y → 2 terms
        x*y + x*z → 2 terms (two products)
        x*(y+z) → 1 term (factored form not expanded)
        (a+b)*(c+d) → 1 term (product, not expanded)
        2*x/2 → 1 term (single quotient)
        x - y + z → 3 terms (subtraction counted as addition of negative)

    Performance: ~2.1μs per expression (7.5% overhead, validated in prototype)

    Args:
        expr: Expression to count terms in

    Returns:
        Number of additive terms in the expression

    Validation: 0% error on 15+ test cases (Sprint 12 Prep Task 7)
    """
    if isinstance(expr, Binary) and expr.op in ("+", "-"):
        # Additive expression: recursively count terms on both sides
        # Subtraction is treated as addition of negative for term counting
        return count_terms(expr.left) + count_terms(expr.right)
    else:
        # All other expressions are single terms:
        # - Constants: 5, 3.14
        # - Variables: x, y
        # - Products: x*y, 2*x
        # - Quotients: x/y, a/b
        # - Powers: x^2, (a+b)^3
        # - Functions: sin(x), log(y)
        return 1


@dataclass
class SimplificationMetrics:
    """Metrics for term reduction benchmarking.

    Collects data on expression simplification effectiveness, including
    operation count, term count, timing, and transformation statistics.

    This extends the base SimplificationMetrics in simplification_pipeline.py
    with term counting and per-model tracking for benchmarking purposes.

    Fields:
        model: Model name (e.g., "rbrock.gms" or "rbrock.eq1")
        ops_before: Operation count before simplification
        ops_after: Operation count after simplification
        terms_before: Term count before simplification (sum-of-products)
        terms_after: Term count after simplification
        execution_time_ms: Milliseconds spent in simplification
        transformations_applied: Count of each transformation (e.g., {"CSE": 3})

    Derived metrics (use calculate_reductions()):
        ops_reduction_pct: Percentage reduction in operations
        terms_reduction_pct: Percentage reduction in terms

    Usage:
        >>> metrics = SimplificationMetrics(model="rbrock.eq1")
        >>> metrics.ops_before = count_operations(expr)
        >>> metrics.terms_before = count_terms(expr)
        >>> # ... run simplification ...
        >>> metrics.ops_after = count_operations(simplified)
        >>> metrics.terms_after = count_terms(simplified)
        >>> metrics.execution_time_ms = elapsed_ms
        >>> data = metrics.to_dict()  # For JSON serialization
    """

    model: str
    ops_before: int = 0
    ops_after: int = 0
    terms_before: int = 0
    terms_after: int = 0
    execution_time_ms: float = 0.0
    transformations_applied: dict[str, int] = field(default_factory=dict)

    def calculate_reductions(self) -> dict[str, float]:
        """Calculate reduction percentages for operations and terms.

        Returns:
            Dictionary with keys:
            - ops_reduction_pct: Percentage reduction in operations
            - terms_reduction_pct: Percentage reduction in terms
            - Both are 0.0 if before count is 0 (prevent division by zero)

        Example:
            >>> metrics.ops_before = 10
            >>> metrics.ops_after = 3
            >>> metrics.terms_before = 5
            >>> metrics.terms_after = 2
            >>> metrics.calculate_reductions()
            {'ops_reduction_pct': 70.0, 'terms_reduction_pct': 60.0}
        """
        ops_reduction = (
            (self.ops_before - self.ops_after) / self.ops_before * 100
            if self.ops_before > 0
            else 0.0
        )
        terms_reduction = (
            (self.terms_before - self.terms_after) / self.terms_before * 100
            if self.terms_before > 0
            else 0.0
        )

        return {
            "ops_reduction_pct": round(ops_reduction, 2),
            "terms_reduction_pct": round(terms_reduction, 2),
        }

    def to_dict(self) -> dict:
        """Convert metrics to dictionary for JSON serialization.

        Includes all fields plus calculated reduction percentages.

        Returns:
            Dictionary representation of metrics with all fields

        Example:
            >>> metrics.to_dict()
            {
                'model': 'rbrock.eq1',
                'ops_before': 10,
                'ops_after': 3,
                'terms_before': 5,
                'terms_after': 2,
                'execution_time_ms': 1.23,
                'transformations_applied': {'CSE': 2, 'ConstantFold': 1},
                'ops_reduction_pct': 70.0,
                'terms_reduction_pct': 60.0
            }
        """
        reductions = self.calculate_reductions()
        return {
            "model": self.model,
            "ops_before": self.ops_before,
            "ops_after": self.ops_after,
            "terms_before": self.terms_before,
            "terms_after": self.terms_after,
            "execution_time_ms": round(self.execution_time_ms, 3),
            "transformations_applied": self.transformations_applied.copy(),
            "ops_reduction_pct": reductions["ops_reduction_pct"],
            "terms_reduction_pct": reductions["terms_reduction_pct"],
        }

    def record_transformation(self, name: str) -> None:
        """Record application of a transformation.

        This should be called by each transformation function when it
        successfully modifies an expression.

        Args:
            name: Name of the transformation (e.g., "CSE", "ConstantFold")

        Example:
            >>> metrics = SimplificationMetrics(model="test")
            >>> metrics.record_transformation("CSE")
            >>> metrics.record_transformation("CSE")
            >>> metrics.record_transformation("ConstantFold")
            >>> metrics.transformations_applied
            {'CSE': 2, 'ConstantFold': 1}
        """
        if name not in self.transformations_applied:
            self.transformations_applied[name] = 0
        self.transformations_applied[name] += 1
