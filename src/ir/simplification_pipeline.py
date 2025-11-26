"""Simplification pipeline for GAMS expressions.

This module implements a configurable pipeline for applying transformation passes
to simplify GAMS expressions while maintaining semantic correctness.

The pipeline supports:
- Multiple transformation passes with priorities
- Fixpoint iteration (apply until no changes)
- Size budget enforcement (prevent expression growth)
- Rollback on budget violations
- Metrics collection for debugging and optimization
"""

from collections.abc import Callable
from dataclasses import dataclass, field

from src.ir.ast import Expr


@dataclass
class TransformationPass:
    """A single transformation pass in the simplification pipeline."""

    name: str
    transform_fn: Callable[[Expr], Expr]
    priority: int  # Lower number = higher priority


@dataclass
class SimplificationMetrics:
    """Metrics collected during simplification."""

    initial_size: int = 0
    final_size: int = 0
    iterations: int = 0
    passes_applied: list[str] = field(default_factory=list)
    rollbacks: int = 0
    budget_violations: int = 0


class SimplificationPipeline:
    """Pipeline for applying expression simplification transformations.

    The pipeline applies registered transformation passes to expressions in
    priority order, iterating until a fixpoint is reached (no more changes)
    or the maximum iteration limit is hit.

    Size budget enforcement prevents transformations that grow the expression
    beyond a specified multiplier of the original size.

    Example:
        >>> pipeline = SimplificationPipeline(max_iterations=5, size_budget=1.5)
        >>> pipeline.add_pass(constant_folding, priority=1, name="ConstantFold")
        >>> pipeline.add_pass(identity_elimination, priority=2, name="IdentityElim")
        >>> simplified, metrics = pipeline.apply(expr)
    """

    def __init__(self, max_iterations: int = 5, size_budget: float = 1.5):
        """Initialize the simplification pipeline.

        Args:
            max_iterations: Maximum number of fixpoint iterations (default: 5)
            size_budget: Maximum allowed size growth as multiplier of original
                        (default: 1.5 = 150% of original size)
        """
        self.passes: list[TransformationPass] = []
        self.max_iterations = max_iterations
        self.size_budget = size_budget

    def add_pass(self, pass_fn: Callable[[Expr], Expr], priority: int, name: str) -> None:
        """Register a transformation pass.

        Args:
            pass_fn: Function that transforms an expression
            priority: Priority of the pass (lower = higher priority)
            name: Human-readable name for debugging
        """
        pass_obj = TransformationPass(name=name, transform_fn=pass_fn, priority=priority)
        self.passes.append(pass_obj)
        # Keep passes sorted by priority
        self.passes.sort(key=lambda p: p.priority)

    def apply(
        self, expr: Expr, metrics: SimplificationMetrics | None = None
    ) -> tuple[Expr, SimplificationMetrics]:
        """Apply all transformation passes to an expression.

        The pipeline applies passes in priority order, repeating until no more
        changes occur (fixpoint) or max_iterations is reached.

        Size budget is enforced at each step - transformations that cause the
        expression to exceed the budget are rolled back.

        Args:
            expr: The expression to simplify
            metrics: Optional metrics object to populate (creates new if None)

        Returns:
            Tuple of (simplified_expr, metrics)
        """
        if metrics is None:
            metrics = SimplificationMetrics()
        else:
            # Reset metrics fields when reusing an existing metrics object
            # to prevent accumulation across multiple apply() calls
            metrics.initial_size = 0
            metrics.final_size = 0
            metrics.iterations = 0
            metrics.passes_applied.clear()
            metrics.rollbacks = 0
            metrics.budget_violations = 0

        # Record initial size
        initial_size = self._expression_size(expr)
        metrics.initial_size = initial_size

        current_expr = expr
        iteration = 0

        # Fixpoint iteration: apply passes until no changes
        while iteration < self.max_iterations:
            iteration += 1
            changed = False

            # Apply each pass in priority order
            for pass_obj in self.passes:
                # Try applying the transformation
                new_expr = pass_obj.transform_fn(current_expr)

                # Check if transformation changed anything
                # Use both identity and equality checks to handle cases where
                # a pass returns a semantically identical but deep-copied expression
                if new_expr is not current_expr or new_expr != current_expr:
                    # Check size budget
                    new_size = self._expression_size(new_expr)
                    if new_size > initial_size * self.size_budget:
                        # Budget violation - rollback this transformation
                        metrics.rollbacks += 1
                        metrics.budget_violations += 1
                        continue  # Skip this transformation

                    # Accept the transformation
                    current_expr = new_expr
                    changed = True
                    metrics.passes_applied.append(f"Iter{iteration}:{pass_obj.name}")

            # If no passes made changes, we've reached fixpoint
            if not changed:
                break

        # Record final metrics
        metrics.iterations = iteration
        metrics.final_size = self._expression_size(current_expr)

        return current_expr, metrics

    def _expression_size(self, expr: Expr) -> int:
        """Measure the size of an expression.

        Size is measured as the number of AST nodes. This is a simple metric
        that roughly correlates with complexity and evaluation cost.

        Args:
            expr: Expression to measure

        Returns:
            Number of nodes in the expression tree
        """
        # Import here to avoid circular dependency
        from src.ir.ast import Binary, Call, Const, SymbolRef, Unary

        if isinstance(expr, Const):
            return 1
        elif isinstance(expr, SymbolRef):
            return 1
        elif isinstance(expr, Unary):
            return 1 + self._expression_size(expr.child)
        elif isinstance(expr, Binary):
            return 1 + self._expression_size(expr.left) + self._expression_size(expr.right)
        elif isinstance(expr, Call):
            return 1 + sum(self._expression_size(arg) for arg in expr.args)
        else:
            # For unknown expression types, estimate conservatively
            return 1
