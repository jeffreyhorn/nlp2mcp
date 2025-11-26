"""Associativity normalization transformation.

This module implements T3.1: Associativity for Constants transformation for
aggressive simplification. It consolidates constants in nested multiplication
and addition operations.

Pattern (Multiplication): (x * c1) * c2 → x * (c1 * c2)
Pattern (Addition): (x + c1) + c2 → x + (c1 + c2)

Example:
    ((x * 2) * 3) * 5 → x * 30

Priority: HIGH (enables further simplification through constant folding)
"""

from src.ir.ast import Binary, Const, Expr


def normalize_associativity(expr: Expr) -> Expr:
    """Normalize associativity to consolidate constants.

    Flattens nested multiplication and addition operations, then groups and
    folds all constants together. This enables like-term collection and
    reduces operation count.

    Algorithm:
        1. Check if expression is multiplication or addition
        2. Flatten operation into list of factors/terms
        3. Separate constants from non-constants
        4. Fold all constants into single value
        5. Rebuild expression with folded constant

    Args:
        expr: Expression to transform

    Returns:
        Transformed expression with constants consolidated,
        or original expression if not applicable

    Example:
        >>> # (x * 2) * 3 → x * 6
        >>> expr = Binary("*", Binary("*", x, Const(2)), Const(3))
        >>> result = normalize_associativity(expr)
        >>> # result = Binary("*", x, Const(6))
    """
    if isinstance(expr, Binary) and expr.op == "*":
        return _normalize_multiplication(expr)
    elif isinstance(expr, Binary) and expr.op == "+":
        return _normalize_addition(expr)
    else:
        return expr


def _normalize_multiplication(expr: Expr) -> Expr:
    """Normalize multiplication to consolidate constants.

    Pattern: (x * c1) * c2 → x * (c1 * c2)

    Args:
        expr: Multiplication expression

    Returns:
        Expression with constants consolidated
    """
    # Flatten multiplication into list of factors
    factors = _flatten_multiplication(expr)

    # Separate constants from non-constants
    constants = []
    non_constants = []

    for factor in factors:
        if isinstance(factor, Const):
            constants.append(factor)
        else:
            non_constants.append(factor)

    # If no constants or only one constant, nothing to consolidate
    if len(constants) <= 1:
        return expr

    # Fold all constants together
    constant_product = constants[0].value
    for const in constants[1:]:
        constant_product *= const.value

    folded_constant = Const(constant_product)

    # Rebuild expression: non_constants * folded_constant
    if len(non_constants) == 0:
        # All factors were constants
        return folded_constant
    elif len(non_constants) == 1:
        # One non-constant factor: non_const * folded_const
        return Binary("*", non_constants[0], folded_constant)
    else:
        # Multiple non-constant factors: (f1 * f2 * ...) * folded_const
        result = non_constants[0]
        for factor in non_constants[1:]:
            result = Binary("*", result, factor)
        return Binary("*", result, folded_constant)


def _normalize_addition(expr: Expr) -> Expr:
    """Normalize addition to consolidate constants.

    Pattern: (x + c1) + c2 → x + (c1 + c2)

    Args:
        expr: Addition expression

    Returns:
        Expression with constants consolidated
    """
    # Flatten addition into list of terms
    terms = _flatten_addition(expr)

    # Separate constants from non-constants
    constants = []
    non_constants = []

    for term in terms:
        if isinstance(term, Const):
            constants.append(term)
        else:
            non_constants.append(term)

    # If no constants or only one constant, nothing to consolidate
    if len(constants) <= 1:
        return expr

    # Fold all constants together
    constant_sum = constants[0].value
    for const in constants[1:]:
        constant_sum += const.value

    folded_constant = Const(constant_sum)

    # Rebuild expression: non_constants + folded_constant
    if len(non_constants) == 0:
        # All terms were constants
        return folded_constant
    elif len(non_constants) == 1:
        # One non-constant term: non_const + folded_const
        return Binary("+", non_constants[0], folded_constant)
    else:
        # Multiple non-constant terms: (t1 + t2 + ...) + folded_const
        result = non_constants[0]
        for term in non_constants[1:]:
            result = Binary("+", result, term)
        return Binary("+", result, folded_constant)


def _flatten_multiplication(expr: Expr) -> list[Expr]:
    """Flatten nested * operations into a list.

    Args:
        expr: Expression to flatten

    Returns:
        List of factors (flattened if expr is multiplication, [expr] otherwise)

    Example:
        >>> # (a * b) * c → [a, b, c]
        >>> expr = Binary("*", Binary("*", a, b), c)
        >>> _flatten_multiplication(expr)
        [a, b, c]
    """
    if not isinstance(expr, Binary) or expr.op != "*":
        return [expr]

    # Recursively flatten left and right
    result = []
    result.extend(_flatten_multiplication(expr.left))
    result.extend(_flatten_multiplication(expr.right))
    return result


def _flatten_addition(expr: Expr) -> list[Expr]:
    """Flatten nested + operations into a list.

    Args:
        expr: Expression to flatten

    Returns:
        List of terms (flattened if expr is addition, [expr] otherwise)

    Example:
        >>> # (a + b) + c → [a, b, c]
        >>> expr = Binary("+", Binary("+", a, b), c)
        >>> _flatten_addition(expr)
        [a, b, c]
    """
    if not isinstance(expr, Binary) or expr.op != "+":
        return [expr]

    # Recursively flatten left and right
    result = []
    result.extend(_flatten_addition(expr.left))
    result.extend(_flatten_addition(expr.right))
    return result
