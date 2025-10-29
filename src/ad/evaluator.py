"""
AST Evaluator with NaN/Inf Detection

This module provides functionality to evaluate AST expressions by plugging in
concrete values for variables and parameters.

Key Features:
------------
1. **Numerical Evaluation**: Convert symbolic ASTs to numerical values
2. **NaN/Inf Detection**: Catch numeric errors with actionable messages
3. **Domain Validation**: Check for division by zero, log of negative, etc.
4. **Indexed Support**: Handle indexed variables and parameters

Use Cases:
---------
- Finite-difference validation (Day 9)
- Testing derivative correctness
- Debugging expression evaluation

Safety:
------
All arithmetic operations check for NaN/Inf and raise clear errors
with context about where the issue occurred.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..ir.ast import Expr

from ..ir.ast import Binary, Call, Const, ParamRef, Sum, SymbolRef, Unary, VarRef


class EvaluationError(Exception):
    """Raised when expression evaluation fails due to domain violations or NaN/Inf."""

    pass


def evaluate(
    expr: Expr,
    var_values: dict[tuple[str, tuple[str, ...]], float] | None = None,
    param_values: dict[tuple[str, tuple[str, ...]], float] | None = None,
) -> float:
    """
    Evaluate an AST expression with concrete variable and parameter values.

    Args:
        expr: The expression AST to evaluate
        var_values: Dictionary mapping (var_name, indices) → value
                   For scalars, use (name, ())
                   For indexed: (name, ("i_val",)) or (name, ("i_val", "j_val"))
        param_values: Dictionary mapping (param_name, indices) → value
                     Same format as var_values

    Returns:
        The numerical result of evaluating the expression

    Raises:
        EvaluationError: If evaluation encounters NaN, Inf, or domain violations
        KeyError: If required variable or parameter value is missing

    Examples:
        >>> from src.ir.ast import VarRef, Const, Binary
        >>> # Evaluate x + 5 with x=3
        >>> expr = Binary("+", VarRef("x"), Const(5.0))
        >>> evaluate(expr, var_values={("x", ()): 3.0})
        8.0

        >>> # Evaluate x(i) * y with x(1)=2, y=3
        >>> expr = Binary("*", VarRef("x", ("i",)), VarRef("y"))
        >>> evaluate(expr, var_values={("x", ("1",)): 2.0, ("y", ()): 3.0})
        6.0
    """
    if var_values is None:
        var_values = {}
    if param_values is None:
        param_values = {}

    return _evaluate_expr(expr, var_values, param_values)


def _evaluate_expr(
    expr: Expr,
    var_values: dict[tuple[str, tuple[str, ...]], float],
    param_values: dict[tuple[str, tuple[str, ...]], float],
) -> float:
    """Internal recursive evaluator."""

    if isinstance(expr, Const):
        return _check_numeric(expr.value, "constant")

    elif isinstance(expr, VarRef):
        key = (expr.name, expr.indices)
        if key not in var_values:
            raise KeyError(
                f"Missing value for variable {expr.name}"
                f"{'(' + ','.join(expr.indices) + ')' if expr.indices else ''}"
            )
        value = var_values[key]
        return _check_numeric(value, f"variable {expr.name}")

    elif isinstance(expr, SymbolRef):
        key = (expr.name, ())
        if key not in var_values:
            raise KeyError(f"Missing value for symbol {expr.name}")
        value = var_values[key]
        return _check_numeric(value, f"symbol {expr.name}")

    elif isinstance(expr, ParamRef):
        key = (expr.name, expr.indices)
        if key not in param_values:
            raise KeyError(
                f"Missing value for parameter {expr.name}"
                f"{'(' + ','.join(expr.indices) + ')' if expr.indices else ''}"
            )
        value = param_values[key]
        return _check_numeric(value, f"parameter {expr.name}")

    elif isinstance(expr, Binary):
        return _evaluate_binary(expr, var_values, param_values)

    elif isinstance(expr, Unary):
        return _evaluate_unary(expr, var_values, param_values)

    elif isinstance(expr, Call):
        return _evaluate_call(expr, var_values, param_values)

    elif isinstance(expr, Sum):
        # Sum evaluation requires knowing the set members
        # For now, raise an error - will be implemented when needed
        raise NotImplementedError(
            "Sum evaluation requires set member information. "
            "This will be implemented in Days 5-6 when index mapping is complete."
        )

    else:
        raise TypeError(f"Unknown expression type: {type(expr).__name__}")


def _evaluate_binary(
    expr: Binary,
    var_values: dict[tuple[str, tuple[str, ...]], float],
    param_values: dict[tuple[str, tuple[str, ...]], float],
) -> float:
    """Evaluate binary operations with NaN/Inf checking."""
    left = _evaluate_expr(expr.left, var_values, param_values)
    right = _evaluate_expr(expr.right, var_values, param_values)

    op = expr.op

    if op == "+":
        result = left + right
        return _check_numeric(result, f"addition ({left} + {right})")

    elif op == "-":
        result = left - right
        return _check_numeric(result, f"subtraction ({left} - {right})")

    elif op == "*":
        result = left * right
        return _check_numeric(result, f"multiplication ({left} * {right})")

    elif op == "/":
        if right == 0.0:
            raise EvaluationError(
                f"Division by zero: {left} / {right}. Ensure denominator is non-zero."
            )
        result = left / right
        return _check_numeric(result, f"division ({left} / {right})")

    elif op == "^":
        # Power operation (will be more fully implemented in Day 3)
        try:
            result = left**right
            return _check_numeric(result, f"power ({left} ^ {right})")
        except (ValueError, OverflowError) as e:
            raise EvaluationError(f"Power operation failed: {left} ^ {right}. Error: {e}") from e

    else:
        raise ValueError(f"Unsupported binary operation: {op}")


def _evaluate_unary(
    expr: Unary,
    var_values: dict[tuple[str, tuple[str, ...]], float],
    param_values: dict[tuple[str, tuple[str, ...]], float],
) -> float:
    """Evaluate unary operations."""
    child = _evaluate_expr(expr.child, var_values, param_values)

    op = expr.op

    if op == "+":
        return child  # Unary plus is identity

    elif op == "-":
        result = -child
        return _check_numeric(result, f"negation (-{child})")

    else:
        raise ValueError(f"Unsupported unary operation: {op}")


def _evaluate_call(
    expr: Call,
    var_values: dict[tuple[str, tuple[str, ...]], float],
    param_values: dict[tuple[str, tuple[str, ...]], float],
) -> float:
    """Evaluate function calls with domain checking."""
    func = expr.func

    if func == "exp":
        if len(expr.args) != 1:
            raise ValueError(f"exp expects 1 argument, got {len(expr.args)}")
        arg = _evaluate_expr(expr.args[0], var_values, param_values)
        try:
            result = math.exp(arg)
            return _check_numeric(result, f"exp({arg})")
        except OverflowError as e:
            raise EvaluationError(f"exp({arg}) overflow: {e}") from e

    elif func == "log":
        if len(expr.args) != 1:
            raise ValueError(f"log expects 1 argument, got {len(expr.args)}")
        arg = _evaluate_expr(expr.args[0], var_values, param_values)
        if arg <= 0:
            raise EvaluationError(f"log domain error: log({arg}). Argument must be positive (> 0).")
        result = math.log(arg)
        return _check_numeric(result, f"log({arg})")

    elif func == "sqrt":
        if len(expr.args) != 1:
            raise ValueError(f"sqrt expects 1 argument, got {len(expr.args)}")
        arg = _evaluate_expr(expr.args[0], var_values, param_values)
        if arg < 0:
            raise EvaluationError(
                f"sqrt domain error: sqrt({arg}). Argument must be non-negative (>= 0)."
            )
        result = math.sqrt(arg)
        return _check_numeric(result, f"sqrt({arg})")

    elif func == "sin":
        if len(expr.args) != 1:
            raise ValueError(f"sin expects 1 argument, got {len(expr.args)}")
        arg = _evaluate_expr(expr.args[0], var_values, param_values)
        result = math.sin(arg)
        return _check_numeric(result, f"sin({arg})")

    elif func == "cos":
        if len(expr.args) != 1:
            raise ValueError(f"cos expects 1 argument, got {len(expr.args)}")
        arg = _evaluate_expr(expr.args[0], var_values, param_values)
        result = math.cos(arg)
        return _check_numeric(result, f"cos({arg})")

    elif func == "tan":
        if len(expr.args) != 1:
            raise ValueError(f"tan expects 1 argument, got {len(expr.args)}")
        arg = _evaluate_expr(expr.args[0], var_values, param_values)
        result = math.tan(arg)
        return _check_numeric(result, f"tan({arg})")

    elif func == "power":
        if len(expr.args) != 2:
            raise ValueError(f"power expects 2 arguments, got {len(expr.args)}")
        base = _evaluate_expr(expr.args[0], var_values, param_values)
        exponent = _evaluate_expr(expr.args[1], var_values, param_values)
        try:
            result = base**exponent
            return _check_numeric(result, f"power({base}, {exponent})")
        except (ValueError, OverflowError) as e:
            raise EvaluationError(f"power({base}, {exponent}) failed: {e}") from e

    else:
        raise ValueError(f"Unknown function: {func}")


def _check_numeric(value: float, context: str) -> float:
    """
    Check if a value is NaN or Inf and raise clear error if so.

    Args:
        value: The numerical value to check
        context: Description of where this value came from (for error messages)

    Returns:
        The value if it's a valid finite number

    Raises:
        EvaluationError: If value is NaN or Inf
    """
    if math.isnan(value):
        raise EvaluationError(
            f"NaN detected in expression evaluation at {context}. "
            f"This typically indicates an invalid mathematical operation "
            f"(e.g., 0/0, inf-inf, 0*inf)."
        )

    if math.isinf(value):
        infinity_type = "positive" if value > 0 else "negative"
        raise EvaluationError(
            f"{infinity_type.capitalize()} infinity detected in expression evaluation at {context}. "
            f"This typically indicates numerical overflow."
        )

    return value
