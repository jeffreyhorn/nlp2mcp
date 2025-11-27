"""Shared utility functions for expression transformations.

This module provides common helper functions used across multiple transformation
passes, including flattening operations for associative operators.
"""

from src.ir.ast import Binary, Call, Const, Expr


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


def expressions_equal(expr1: Expr, expr2: Expr) -> bool:
    """Check if two expressions are structurally identical.

    Args:
        expr1: First expression
        expr2: Second expression

    Returns:
        True if expressions are structurally equal

    Example:
        >>> # Check if sin(x) equals sin(x)
        >>> x = SymbolRef("x")
        >>> expr1 = Call("sin", (x,))
        >>> expr2 = Call("sin", (x,))
        >>> expressions_equal(expr1, expr2)
        True
    """
    # Check type equality
    if type(expr1) is not type(expr2):
        return False

    # Const: compare values
    if isinstance(expr1, Const):
        return isinstance(expr2, Const) and expr1.value == expr2.value

    # Binary: compare operator and operands
    if isinstance(expr1, Binary):
        if not isinstance(expr2, Binary):
            return False
        return (
            expr1.op == expr2.op
            and expressions_equal(expr1.left, expr2.left)
            and expressions_equal(expr1.right, expr2.right)
        )

    # Call: compare function name and arguments
    if isinstance(expr1, Call):
        if not isinstance(expr2, Call):
            return False
        if expr1.func != expr2.func or len(expr1.args) != len(expr2.args):
            return False
        return all(expressions_equal(a1, a2) for a1, a2 in zip(expr1.args, expr2.args, strict=True))

    # For other types (SymbolRef, VarRef, ParamRef), use identity comparison
    # This is safe because frozen dataclasses have structural equality
    return expr1 == expr2
