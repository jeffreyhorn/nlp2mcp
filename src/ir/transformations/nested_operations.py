"""Nested operation simplification transformation.

This module implements T2.2: Nested Product Simplification transformation for
aggressive simplification. It flattens nested multiplications and consolidates
constants.

Pattern: (a*b)*c → a*b*c with constant consolidation

Example:
    (2*x)*3 → 6*x
    ((x*y)*z)*w → x*y*z*w

Priority: MEDIUM (reduces nesting, enables further simplifications)
"""

from src.ir.ast import Binary, Const, Expr
from src.ir.transformations.utils import flatten_multiplication


def simplify_nested_products(expr: Expr) -> Expr:
    """Simplify nested multiplication expressions.

    Flattens nested multiplications and consolidates constants into a single
    constant factor.

    Algorithm:
        1. Check if expression is multiplication
        2. Flatten into list of factors
        3. Separate constants from non-constants
        4. Multiply all constants together
        5. Rebuild with consolidated constant

    Args:
        expr: Expression to transform

    Returns:
        Transformed expression with flattened multiplication and
        consolidated constants, or original if not applicable

    Example:
        >>> # (2*x)*3 → 6*x
        >>> expr = Binary("*", Binary("*", Const(2), x), Const(3))
        >>> result = simplify_nested_products(expr)
        >>> # result = Binary("*", Const(6), x)
    """
    # Only apply to multiplication expressions
    if not isinstance(expr, Binary) or expr.op != "*":
        return expr

    # Flatten multiplication into list of factors
    factors = flatten_multiplication(expr)

    # If only 1-2 factors, no nesting to simplify
    if len(factors) <= 2:
        return expr

    # Separate constants from non-constants
    constants: list[Const] = []
    non_constants: list[Expr] = []

    for factor in factors:
        if isinstance(factor, Const):
            constants.append(factor)
        else:
            non_constants.append(factor)

    # If no constants or only one constant, just flatten
    if len(constants) <= 1:
        # Still rebuild to flatten nesting
        return _rebuild_multiplication(factors)

    # Consolidate constants
    constant_product = 1.0
    for const in constants:
        constant_product *= const.value

    consolidated_const = Const(constant_product)

    # Rebuild: consolidated_const * non_constants
    if len(non_constants) == 0:
        # All factors were constants
        return consolidated_const
    else:
        # Build: const * (factor1 * factor2 * ...)
        result: Expr = consolidated_const
        for factor in non_constants:
            result = Binary("*", result, factor)
        return result


def _rebuild_multiplication(factors: list[Expr]) -> Expr:
    """Rebuild a flat multiplication from a list of factors.

    Args:
        factors: List of factors to multiply

    Returns:
        Multiplication expression, or single factor if length 1
    """
    if len(factors) == 0:
        return Const(1)
    elif len(factors) == 1:
        return factors[0]
    else:
        result = factors[0]
        for factor in factors[1:]:
            result = Binary("*", result, factor)
        return result
