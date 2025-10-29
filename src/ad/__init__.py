"""
Automatic Differentiation Module

This module provides symbolic differentiation capabilities for GAMS NLP expressions.

Public API:
-----------
- differentiate(expr, wrt_var) : Compute symbolic derivative of an expression

Example Usage:
-------------
    from src.ir.ast import VarRef, Const
    from src.ad import differentiate

    # Differentiate x with respect to x
    expr = VarRef("x")
    deriv = differentiate(expr, "x")  # Returns Const(1.0)

    # Differentiate constant with respect to x
    expr = Const(5.0)
    deriv = differentiate(expr, "x")  # Returns Const(0.0)

Sprint 2 Development Schedule:
-----------------------------
- Day 1: Constants and variable references ✓
- Day 2: Arithmetic operations (+, -, *, /) and unary operators
- Day 3: Power, exp, log, sqrt
- Day 4: Trigonometric functions (sin, cos, tan)
- Day 5-6: Sum aggregations and indexing
- Day 7-8: Jacobian structure and gradient computation
- Day 9: Finite-difference validation
- Day 10: Integration and documentation
"""

from .ad_core import differentiate, simplify
from .api import compute_derivatives
from .constraint_jacobian import compute_constraint_jacobian
from .evaluator import EvaluationError, evaluate
from .gradient import compute_objective_gradient

__all__ = [
    "differentiate",
    "simplify",
    "evaluate",
    "EvaluationError",
    "compute_objective_gradient",
    "compute_constraint_jacobian",
    "compute_derivatives",  # High-level API (recommended)
]
