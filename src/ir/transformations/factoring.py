"""Common factor extraction transformation.

This module implements T1.1 and T1.2 transformations for aggressive simplification:
- T1.1: Common Factor Extraction (single/multiple terms)
- T1.2: Multi-Term Factoring (2x2 pattern)

Pattern (T1.1): x*y + x*z → x*(y + z)
Pattern (T1.2): a*c + a*d + b*c + b*d → (a + b)*(c + d)

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

        # Remove common factors from this term (one occurrence per match)
        remaining = term_factors.copy()
        for common_factor in common_factors:
            if common_factor in remaining:
                remaining.remove(common_factor)

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


def multi_term_factoring(expr: Expr) -> Expr:
    """Apply multi-term factoring (2x2 pattern).

    Detects and factors expressions of the form:
    a*c + a*d + b*c + b*d → (a + b)*(c + d)

    This is a more advanced factoring pattern that groups terms by
    partial common factors rather than factors common to all terms.

    Algorithm:
        1. Check if expression is addition with exactly 4 terms
        2. Try to find 2x2 grouping structure
        3. Verify that factoring reduces expression size
        4. Apply factoring if beneficial

    Args:
        expr: Expression to transform

    Returns:
        Transformed expression using 2x2 factoring,
        or original expression if pattern not detected or not beneficial

    Example:
        >>> # a*c + a*d + b*c + b*d → (a + b)*(c + d)
        >>> # Terms: [a*c, a*d, b*c, b*d]
        >>> # Group 1 factors: {a, c}, {a, d} → common: {a}, remaining: {c, d}
        >>> # Group 2 factors: {b, c}, {b, d} → common: {b}, remaining: {c, d}
        >>> # Result: (a + b) * (c + d)
    """
    # Only apply to addition expressions
    if not isinstance(expr, Binary) or expr.op != "+":
        return expr

    # Flatten addition into list of terms
    terms = flatten_addition(expr)

    # Multi-term factoring requires exactly 4 terms for 2x2 pattern
    if len(terms) != 4:
        return expr

    # Try to find 2x2 grouping
    factored = _try_2x2_factoring(terms)

    # If factoring succeeded and is beneficial, return it
    if factored is not None:
        # Count operations to verify benefit
        if _count_operations(factored) < _count_operations(expr):
            return factored

    return expr


def _try_2x2_factoring(terms: list[Expr]) -> Expr | None:
    """Attempt to factor 4 terms using 2x2 pattern.

    Tries different groupings to find a 2x2 structure.

    Args:
        terms: Exactly 4 terms from flattened addition

    Returns:
        Factored expression if 2x2 pattern found, None otherwise
    """
    # Try all possible ways to split 4 terms into 2 groups of 2
    # Groupings: (0,1)+(2,3), (0,2)+(1,3), (0,3)+(1,2)
    groupings = [
        ([terms[0], terms[1]], [terms[2], terms[3]]),
        ([terms[0], terms[2]], [terms[1], terms[3]]),
        ([terms[0], terms[3]], [terms[1], terms[2]]),
    ]

    for group1, group2 in groupings:
        # Extract factors from each group
        group1_factors = [_get_multiplication_factors(t) for t in group1]
        group2_factors = [_get_multiplication_factors(t) for t in group2]

        # Find common factor in group 1
        common1 = _find_common_factors(group1)
        if len(common1) == 0:
            continue

        # Find common factor in group 2
        common2 = _find_common_factors(group2)
        if len(common2) == 0:
            continue

        # Check if remaining factors are the same for both groups
        # After factoring out common1 and common2, the remainders should match

        # Get remaining factors for group 1
        remaining1_set = []
        for factors in group1_factors:
            remaining = factors.copy()
            # Remove common factors (one occurrence per match)
            for common_factor in common1:
                if common_factor in remaining:
                    remaining.remove(common_factor)
            remaining1_set.append(remaining)

        # Get remaining factors for group 2
        remaining2_set = []
        for factors in group2_factors:
            remaining = factors.copy()
            # Remove common factors (one occurrence per match)
            for common_factor in common2:
                if common_factor in remaining:
                    remaining.remove(common_factor)
            remaining2_set.append(remaining)

        # Check if remainders match across groups
        # This is the key condition for 2x2 factoring
        if _check_remainder_match(remaining1_set, remaining2_set):
            # Build factored expression: (common1 + common2) * (remainder1 + remainder2)
            # Build (common1 + common2)
            factor1 = _rebuild_product(common1)
            factor2 = _rebuild_product(common2)
            left_factor = Binary("+", factor1, factor2)

            # Build (remainder1 + remainder2) from the two remainders
            # For a*c + a*d + b*c + b*d: remainders are [[c], [d]]
            # We need to build (c + d)
            remainder1 = _rebuild_product(remaining1_set[0])
            remainder2 = _rebuild_product(remaining1_set[1])
            right_factor = Binary("+", remainder1, remainder2)

            return Binary("*", left_factor, right_factor)

    return None


def _check_remainder_match(remaining1: list[list[Expr]], remaining2: list[list[Expr]]) -> bool:
    """Check if remainder factors match across both groups.

    For 2x2 pattern a*c + a*d + b*c + b*d → (a+b)*(c+d):
    - Group 1 remainders: [[c], [d]] after factoring out [a]
    - Group 2 remainders: [[c], [d]] after factoring out [b]

    The remainders should form the same set in both groups (order doesn't matter).

    Args:
        remaining1: Remainder factors from group 1 (2 elements)
        remaining2: Remainder factors from group 2 (2 elements)

    Returns:
        True if both groups have the same set of remainders
    """
    if len(remaining1) != 2 or len(remaining2) != 2:
        return False

    # Check if group1 remainders match group2 remainders (in either order)
    # Pattern 1: rem1[0]==rem2[0] and rem1[1]==rem2[1]
    # Pattern 2: rem1[0]==rem2[1] and rem1[1]==rem2[0]

    pattern1 = _factor_lists_equal(remaining1[0], remaining2[0]) and _factor_lists_equal(
        remaining1[1], remaining2[1]
    )

    pattern2 = _factor_lists_equal(remaining1[0], remaining2[1]) and _factor_lists_equal(
        remaining1[1], remaining2[0]
    )

    return pattern1 or pattern2


def _factor_lists_equal(list1: list[Expr], list2: list[Expr]) -> bool:
    """Check if two factor lists are equal (same elements with same counts).

    Properly handles duplicates by counting occurrences.

    Args:
        list1: First factor list
        list2: Second factor list

    Returns:
        True if lists contain the same factors with same multiplicities
    """
    if len(list1) != len(list2):
        return False

    # Create a copy of list2 to track usage
    list2_copy = list2.copy()

    # Check if all elements in list1 can be matched in list2
    for factor in list1:
        if factor in list2_copy:
            list2_copy.remove(factor)
        else:
            return False

    return True


def _rebuild_product(factors: list[Expr]) -> Expr:
    """Rebuild a product expression from a list of factors.

    Args:
        factors: List of factors to multiply

    Returns:
        Product expression, or Const(1) if empty, or single factor if length 1
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


def _count_operations(expr: Expr) -> int:
    """Count the number of operations in an expression.

    Args:
        expr: Expression to count operations in

    Returns:
        Number of operations (Binary nodes)
    """
    if isinstance(expr, Binary):
        return 1 + _count_operations(expr.left) + _count_operations(expr.right)
    else:
        return 0
