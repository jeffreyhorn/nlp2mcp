"""Shared utility functions for expression transformations.

This module provides common helper functions used across multiple transformation
passes, including flattening operations for associative operators.
"""

from src.ir.ast import Binary, Expr


def flatten_addition(expr: Expr) -> list[Expr]:
    """Flatten nested + operations into a list.

    Recursively flattens a chain of additions into a flat list of terms.

    Args:
        expr: Expression to flatten

    Returns:
        List of terms (flattened if expr is addition, [expr] otherwise)

    Example:
        >>> # (a + b) + c → [a, b, c]
        >>> expr = Binary("+", Binary("+", a, b), c)
        >>> flatten_addition(expr)
        [a, b, c]
    """
    if not isinstance(expr, Binary) or expr.op != "+":
        return [expr]

    # Recursively flatten left and right
    result: list[Expr] = []
    result.extend(flatten_addition(expr.left))
    result.extend(flatten_addition(expr.right))
    return result


def flatten_multiplication(expr: Expr) -> list[Expr]:
    """Flatten nested * operations into a list.

    Recursively flattens a chain of multiplications into a flat list of factors.

    Args:
        expr: Expression to flatten

    Returns:
        List of factors (flattened if expr is multiplication, [expr] otherwise)

    Example:
        >>> # (a * b) * c → [a, b, c]
        >>> expr = Binary("*", Binary("*", a, b), c)
        >>> flatten_multiplication(expr)
        [a, b, c]
    """
    if not isinstance(expr, Binary) or expr.op != "*":
        return [expr]

    # Recursively flatten left and right
    result: list[Expr] = []
    result.extend(flatten_multiplication(expr.left))
    result.extend(flatten_multiplication(expr.right))
    return result
