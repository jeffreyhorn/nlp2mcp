"""Fraction combining transformation.

This module implements T2.1: Fraction Combining transformation for
aggressive simplification. It combines fractions with identical denominators.

Pattern: a/c + b/c → (a + b)/c

Example:
    x/a + y/a + z/a → (x + y + z)/a

Priority: HIGH (enables further factoring in numerators)
"""

from src.ir.ast import Binary, Const, Expr


def combine_fractions(expr: Expr) -> Expr:
    """Combine fractions with common denominators.

    Combines multiple division terms in an addition that share the same
    denominator into a single fraction.

    Algorithm:
        1. Check if expression is an addition
        2. Flatten addition into list of terms
        3. Group terms by denominator
        4. For groups with ≥2 terms, combine numerators
        5. Rebuild expression

    Args:
        expr: Expression to transform

    Returns:
        Transformed expression with fractions combined,
        or original expression if no common denominators found

    Example:
        >>> # x/a + y/a → (x + y)/a
        >>> expr = Binary("+", Binary("/", x, a), Binary("/", y, a))
        >>> result = combine_fractions(expr)
        >>> # result = Binary("/", Binary("+", x, y), a)
    """
    # Only apply to addition expressions
    if not isinstance(expr, Binary) or expr.op != "+":
        return expr

    # Flatten addition into list of terms
    terms = _flatten_addition(expr)

    # Need at least 2 terms to have common denominators
    if len(terms) < 2:
        return expr

    # Group terms by denominator
    # denominator_groups: {denominator: [list of numerators]}
    denominator_groups: dict[Expr, list[Expr]] = {}
    non_division_terms: list[Expr] = []

    for term in terms:
        if isinstance(term, Binary) and term.op == "/":
            # This is a division: numerator / denominator
            numerator = term.left
            denominator = term.right

            if denominator not in denominator_groups:
                denominator_groups[denominator] = []
            denominator_groups[denominator].append(numerator)
        else:
            # Not a division, keep as-is
            non_division_terms.append(term)

    # Check if any denominators have ≥2 numerators (can be combined)
    has_combination = any(len(numerators) >= 2 for numerators in denominator_groups.values())

    if not has_combination:
        # No fractions to combine
        return expr

    # Build combined fractions and remaining terms
    combined_terms: list[Expr] = []

    # Process each denominator group
    for denominator, numerators in denominator_groups.items():
        if len(numerators) == 1:
            # Only one term with this denominator, can't combine
            combined_terms.append(Binary("/", numerators[0], denominator))
        else:
            # Multiple terms with same denominator, combine them
            # Build sum of numerators: n1 + n2 + n3 + ...
            combined_numerator = numerators[0]
            for num in numerators[1:]:
                combined_numerator = Binary("+", combined_numerator, num)

            # Build combined fraction: (n1 + n2 + ...) / denominator
            combined_terms.append(Binary("/", combined_numerator, denominator))

    # Add non-division terms
    combined_terms.extend(non_division_terms)

    # Build final expression
    if len(combined_terms) == 0:
        # Shouldn't happen, but handle gracefully
        return Const(0)
    elif len(combined_terms) == 1:
        return combined_terms[0]
    else:
        # Build sum: term1 + term2 + ...
        result = combined_terms[0]
        for term in combined_terms[1:]:
            result = Binary("+", result, term)
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
    result: list[Expr] = []
    result.extend(_flatten_addition(expr.left))
    result.extend(_flatten_addition(expr.right))
    return result
