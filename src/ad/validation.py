"""
Finite-Difference Validation for Symbolic Differentiation

This module provides utilities for validating symbolic derivatives using
finite-difference approximations.

Day 9 Scope:
-----------
- Deterministic seed point generation for reproducible tests
- Finite-difference numerical derivative computation
- Comparison utilities for symbolic vs. numeric derivatives
- Tolerance checking and validation

Finite-Difference Method:
------------------------
Central difference approximation:
    f'(x) ≈ (f(x+h) - f(x-h))/(2h)

Step size: h = 1e-6
Tolerance: 1e-6 (symbolic and FD should match within this)

Seed Point Strategy:
-------------------
For reproducible testing, seed points are generated deterministically:
- Fixed random seed: np.random.seed(42)
- Bounded variables: sample uniformly within [lo, up]
- Unbounded variables: sample from [-10, 10]
- Avoids domain boundaries for log, sqrt, etc.

This ensures tests are repeatable and CI/CD runs are deterministic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..ir.ast import Expr

import numpy as np

from .evaluator import evaluate

# Fixed random seed for deterministic test point generation
DEFAULT_SEED = 42

# Default step size for finite-difference approximation
DEFAULT_FD_STEP = 1e-6

# Default tolerance for comparing symbolic vs numeric derivatives
DEFAULT_TOLERANCE = 1e-6

# Default range for unbounded variables
DEFAULT_UNBOUNDED_RANGE = (-10.0, 10.0)


def _convert_to_evaluator_format(
    simple_dict: dict[str, float],
) -> dict[tuple[str, tuple[str, ...]], float]:
    """
    Convert simple string-keyed dict to evaluator's tuple-keyed format.

    The evaluator expects keys as (name, indices) tuples, where indices
    is a tuple of index strings (empty tuple for scalar variables).

    Args:
        simple_dict: Dict with string keys like {"x": 3.0, "y": 5.0}

    Returns:
        Dict with tuple keys like {("x", ()): 3.0, ("y", ()): 5.0}

    Examples:
        >>> _convert_to_evaluator_format({"x": 3.0, "y": 5.0})
        {("x", ()): 3.0, ("y", ()): 5.0}
    """
    return {(name, ()): value for name, value in simple_dict.items()}


def generate_test_point(
    var_names: list[str],
    bounds: dict[str, tuple[float | None, float | None]] | None = None,
    seed: int = DEFAULT_SEED,
) -> dict[str, float]:
    """
    Generate deterministic test point for variables.

    Uses fixed random seed for reproducibility. Respects variable bounds
    when provided.

    Args:
        var_names: List of variable names
        bounds: Optional dict mapping var_name → (lower, upper)
                None values mean unbounded in that direction
        seed: Random seed for reproducibility (default: 42)

    Returns:
        Dict mapping var_name → test value

    Examples:
        >>> # Unbounded variables
        >>> generate_test_point(['x', 'y'])
        {'x': -3.245, 'y': 7.891}  # (deterministic with seed=42)

        >>> # Bounded variables
        >>> generate_test_point(['x'], bounds={'x': (0.0, 10.0)})
        {'x': 6.472}  # sampled within [0, 10]

        >>> # Mixed bounded/unbounded
        >>> generate_test_point(['x', 'y'], bounds={'x': (0.0, None)})
        {'x': 5.234, 'y': -2.456}
    """
    rng = np.random.RandomState(seed)
    test_point = {}

    for var_name in var_names:
        # Get bounds for this variable
        if bounds and var_name in bounds:
            lo, up = bounds[var_name]
        else:
            lo, up = None, None

        # Determine effective bounds
        if lo is None and up is None:
            # Unbounded: use default range
            lo, up = DEFAULT_UNBOUNDED_RANGE
        elif lo is None:
            # Only upper bound: use [up - 20, up - 0.1]
            assert up is not None  # Type narrowing for mypy
            lo = up - 20.0
            up = up - 0.1  # Stay away from boundary
        elif up is None:
            # Only lower bound: use [lo + 0.1, lo + 20]
            assert lo is not None  # Type narrowing for mypy
            up = lo + 20.0
            lo = lo + 0.1  # Stay away from boundary
        else:
            # Both bounds: use [lo + ε, up - ε] to avoid boundaries
            assert lo is not None and up is not None  # Type narrowing for mypy
            range_width = up - lo
            if range_width > 0.2:
                lo = lo + 0.1
                up = up - 0.1
            else:
                # Very narrow range, just use midpoint
                mid = (lo + up) / 2.0
                test_point[var_name] = mid
                continue

        # Sample uniformly in the range
        test_point[var_name] = rng.uniform(lo, up)

    return test_point


def finite_difference(
    expr: Expr,
    wrt_var: str,
    var_values: dict[str, float],
    param_values: dict[str, float] | None = None,
    step: float = DEFAULT_FD_STEP,
) -> float:
    """
    Compute numerical derivative using central finite-difference.

    Uses central difference: f'(x) ≈ (f(x+h) - f(x-h))/(2h)

    Args:
        expr: Expression to differentiate
        wrt_var: Variable to differentiate with respect to
        var_values: Current variable values (including wrt_var)
        param_values: Parameter values (if any)
        step: Finite-difference step size (default: 1e-6)

    Returns:
        Numerical derivative approximation

    Raises:
        KeyError: If wrt_var not in var_values
        EvaluationError: If expression evaluation fails

    Examples:
        >>> # f(x) = x^2, f'(x) = 2x
        >>> expr = Call('power', (VarRef('x'), Const(2.0)))
        >>> finite_difference(expr, 'x', {'x': 3.0})
        6.0  # ≈ 2*3 = 6

        >>> # f(x,y) = x*y, ∂f/∂x = y
        >>> expr = Binary('*', VarRef('x'), VarRef('y'))
        >>> finite_difference(expr, 'x', {'x': 2.0, 'y': 5.0})
        5.0  # = y
    """
    if wrt_var not in var_values:
        raise KeyError(f"Variable '{wrt_var}' not in var_values")

    if param_values is None:
        param_values = {}

    # Convert to evaluator format
    param_values_eval = _convert_to_evaluator_format(param_values) if param_values else {}

    # Evaluate at x + h
    var_values_plus = var_values.copy()
    var_values_plus[wrt_var] = var_values[wrt_var] + step
    var_values_plus_eval = _convert_to_evaluator_format(var_values_plus)
    f_plus = evaluate(expr, var_values_plus_eval, param_values_eval)

    # Evaluate at x - h
    var_values_minus = var_values.copy()
    var_values_minus[wrt_var] = var_values[wrt_var] - step
    var_values_minus_eval = _convert_to_evaluator_format(var_values_minus)
    f_minus = evaluate(expr, var_values_minus_eval, param_values_eval)

    # Central difference
    return (f_plus - f_minus) / (2.0 * step)


def validate_derivative(
    expr: Expr,
    symbolic_deriv: Expr,
    wrt_var: str,
    var_values: dict[str, float],
    param_values: dict[str, float] | None = None,
    tolerance: float = DEFAULT_TOLERANCE,
    fd_step: float = DEFAULT_FD_STEP,
) -> tuple[bool, float, float, float]:
    """
    Validate symbolic derivative against finite-difference approximation.

    Compares the evaluated symbolic derivative with numerical FD result.

    Args:
        expr: Original expression
        symbolic_deriv: Symbolic derivative expression
        wrt_var: Variable differentiated with respect to
        var_values: Variable values for evaluation
        param_values: Parameter values (if any)
        tolerance: Acceptable absolute difference (default: 1e-6)
        fd_step: FD step size (default: 1e-6)

    Returns:
        Tuple of (is_valid, symbolic_value, fd_value, absolute_error):
        - is_valid: True if |symbolic - fd| <= tolerance
        - symbolic_value: Evaluated symbolic derivative
        - fd_value: Finite-difference approximation
        - absolute_error: |symbolic - fd|

    Examples:
        >>> # Validate d(x^2)/dx = 2x
        >>> expr = Call('power', (VarRef('x'), Const(2.0)))
        >>> deriv = Binary('*', Const(2.0), VarRef('x'))  # 2*x
        >>> is_valid, sym, fd, err = validate_derivative(
        ...     expr, deriv, 'x', {'x': 3.0}
        ... )
        >>> is_valid
        True
        >>> abs(sym - 6.0) < 1e-6  # 2*3 = 6
        True
        >>> abs(fd - 6.0) < 1e-6
        True
    """
    if param_values is None:
        param_values = {}

    # Convert to evaluator format
    var_values_eval = _convert_to_evaluator_format(var_values)
    param_values_eval = _convert_to_evaluator_format(param_values) if param_values else {}

    # Evaluate symbolic derivative
    symbolic_value = evaluate(symbolic_deriv, var_values_eval, param_values_eval)

    # Compute finite-difference approximation
    fd_value = finite_difference(expr, wrt_var, var_values, param_values, fd_step)

    # Check tolerance
    absolute_error = abs(symbolic_value - fd_value)
    is_valid = absolute_error <= tolerance

    return is_valid, symbolic_value, fd_value, absolute_error


def validate_gradient(
    expr: Expr,
    symbolic_gradient: dict[str, Expr],
    var_values: dict[str, float],
    param_values: dict[str, float] | None = None,
    tolerance: float = DEFAULT_TOLERANCE,
) -> dict[str, tuple[bool, float, float, float]]:
    """
    Validate gradient (all partial derivatives) against finite-difference.

    Args:
        expr: Expression to differentiate
        symbolic_gradient: Dict mapping var_name → symbolic derivative expr
        var_values: Variable values for evaluation
        param_values: Parameter values (if any)
        tolerance: Acceptable absolute difference

    Returns:
        Dict mapping var_name → (is_valid, symbolic, fd, error)
        Same format as validate_derivative return value

    Examples:
        >>> # Validate gradient of f(x,y) = x^2 + y^2
        >>> # ∇f = (2x, 2y)
        >>> expr = Binary('+',
        ...     Call('power', (VarRef('x'), Const(2.0))),
        ...     Call('power', (VarRef('y'), Const(2.0)))
        ... )
        >>> gradient = {
        ...     'x': Binary('*', Const(2.0), VarRef('x')),
        ...     'y': Binary('*', Const(2.0), VarRef('y'))
        ... }
        >>> results = validate_gradient(expr, gradient, {'x': 3.0, 'y': 4.0})
        >>> results['x'][0]  # is_valid for x
        True
        >>> results['y'][0]  # is_valid for y
        True
    """
    if param_values is None:
        param_values = {}

    results = {}
    for var_name, deriv_expr in symbolic_gradient.items():
        if var_name in var_values:
            results[var_name] = validate_derivative(
                expr, deriv_expr, var_name, var_values, param_values, tolerance
            )

    return results
