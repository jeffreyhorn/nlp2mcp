"""Common factor extraction transformation.

This module implements T1.1: Common Factor Extraction transformation for
aggressive simplification. It factors out common multiplicative terms from
additions.

Pattern: x*y + x*z → x*(y + z)

Example:
    2*exp(x)*sin(y) + 2*exp(x)*cos(y) → 2*exp(x)*(sin(y) + cos(y))

Priority: HIGH (primary term reduction mechanism)
"""

from src.ir.ast import Binary, Const, Expr
from src.ir.transformations.utils import flatten_addition, flatten_multiplication


def extract_common_factors(expr: Expr) -> Expr:
    """Extract common factors from addition expressions.

    Factors out multiplicative terms that are common to all addends.
    This is the main entry point for T1.1 transformation.

    Algorithm:
        1. Check if expression is an addition
        2. Flatten addition into list of terms
        3. Find factors common to all terms
        4. If common factors exist, factor them out
        5. Simplify the result

    Args:
        expr: Expression to transform

    Returns:
        Transformed expression with common factors extracted,
        or original expression if no common factors found

    Example:
        >>> # x*y + x*z → x*(y + z)
        >>> expr = Binary("+", Binary("*", x, y), Binary("*", x, z))
        >>> result = extract_common_factors(expr)
        >>> # result = Binary("*", x, Binary("+", y, z))
    """
    # Only apply to addition expressions
    if not isinstance(expr, Binary) or expr.op != "+":
        return expr

    # Flatten addition into list of terms
    terms = flatten_addition(expr)

    # Need at least 2 terms to have common factors
    if len(terms) < 2:
        return expr

    # Find factors common to all terms
    common_factors = _find_common_factors(terms)

    # If no common factors, return original
    if len(common_factors) == 0:
        return expr

    # Build remaining terms after factoring out common factors
    remaining_terms: list[Expr] = []
    for term in terms:
        term_factors = _get_multiplication_factors(term)

        # Remove common factors from this term
        remaining = [f for f in term_factors if f not in common_factors]

        # Build remaining expression for this term
        remaining_expr: Expr
        if len(remaining) == 0:
            # All factors were common, remaining is 1
            remaining_expr = Const(1)
        elif len(remaining) == 1:
            # Single factor remaining
            remaining_expr = remaining[0]
        else:
            # Multiple factors remaining, rebuild multiplication
            remaining_expr = remaining[0]
            for factor in remaining[1:]:
                remaining_expr = Binary("*", remaining_expr, factor)
        remaining_terms.append(remaining_expr)

    # Build sum of remaining terms
    sum_expr: Expr = remaining_terms[0]
    for term in remaining_terms[1:]:
        sum_expr = Binary("+", sum_expr, term)

    # Build factored expression: common_factors * sum_expr
    result = sum_expr
    for factor in common_factors:
        result = Binary("*", factor, result)

    return result


def _get_multiplication_factors(expr: Expr) -> list[Expr]:
    """Get all multiplicative factors from an expression.

    This is a wrapper around flatten_multiplication for clarity.

    Args:
        expr: Expression to extract factors from

    Returns:
        List of factors [x, y, z] if expr is x*y*z, or [expr] otherwise

    Example:
        >>> # x*y*z → [x, y, z]
        >>> # x → [x]
    """
    return flatten_multiplication(expr)


def _find_common_factors(terms: list[Expr]) -> list[Expr]:
    """Find factors that are common to all terms.

    Computes the intersection of factor sets across all terms.

    Args:
        terms: List of terms (from flattened addition)

    Returns:
        List of factors common to all terms, or empty list if none

    Example:
        >>> # Terms: [x*y, x*z]
        >>> # Factors: [[x, y], [x, z]]
        >>> # Common: [x]
        >>> terms = [Binary("*", x, y), Binary("*", x, z)]
        >>> _find_common_factors(terms)
        [x]
    """
    if len(terms) == 0:
        return []

    # Extract factors from each term
    term_factors = [_get_multiplication_factors(term) for term in terms]

    # Find intersection using frozen dataclass equality
    # Start with factors from first term
    common = term_factors[0][:]  # Make a copy

    # For each subsequent term, keep only factors that appear in that term
    for factors in term_factors[1:]:
        # Filter common to keep only factors present in current term
        common = [f for f in common if f in factors]

    return common
