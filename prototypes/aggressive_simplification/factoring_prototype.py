"""
Factoring Algorithm Prototype for Aggressive Simplification

This prototype implements:
1. Distribution cancellation: x*y + x*z → x*(y + z)
2. Multi-term factoring: a*c + a*d + b*c + b*d → (a + b)*(c + d)

Purpose: Validate algorithms and measure performance before Sprint 11 implementation.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ir.ast import Binary, Const, Expr, VarRef

if TYPE_CHECKING:
    pass


def _flatten_addition(expr: Expr) -> list[Expr]:
    """Flatten nested + operations into a list."""
    if not isinstance(expr, Binary) or expr.op != "+":
        return [expr]

    result = []
    result.extend(_flatten_addition(expr.left))
    result.extend(_flatten_addition(expr.right))
    return result


def _flatten_multiplication(expr: Expr) -> list[Expr]:
    """Flatten nested * operations into a list."""
    if not isinstance(expr, Binary) or expr.op != "*":
        return [expr]

    result = []
    result.extend(_flatten_multiplication(expr.left))
    result.extend(_flatten_multiplication(expr.right))
    return result


def _rebuild_multiplication(factors: list[Expr]) -> Expr:
    """Rebuild a multiplication from a list of factors."""
    if not factors:
        return Const(1.0)
    if len(factors) == 1:
        return factors[0]

    result = factors[0]
    for factor in factors[1:]:
        result = Binary("*", result, factor)
    return result


def _rebuild_addition(terms: list[Expr]) -> Expr:
    """Rebuild an addition from a list of terms."""
    if not terms:
        return Const(0.0)
    if len(terms) == 1:
        return terms[0]

    result = terms[0]
    for term in terms[1:]:
        result = Binary("+", result, term)
    return result


def _get_common_factors(term1_factors: list[Expr], term2_factors: list[Expr]) -> list[Expr]:
    """
    Find common factors between two factor lists.

    Uses AST equality (frozen dataclasses with __eq__).

    Args:
        term1_factors: Factors from first term
        term2_factors: Factors from second term

    Returns:
        List of common factors (intersection)
    """
    common = []
    remaining1 = list(term1_factors)
    remaining2 = list(term2_factors)

    for factor in term1_factors:
        if factor in remaining2:
            common.append(factor)
            remaining1.remove(factor)
            remaining2.remove(factor)

    return common


def factor_common_terms(expr: Expr) -> Expr:
    """
    Distribution cancellation: x*y + x*z → x*(y + z)

    Algorithm:
    1. Flatten addition into terms
    2. For each term, flatten multiplication into factors
    3. Find intersection of factors across all terms
    4. If common factors exist, factor them out
    5. Rebuild: common_factor * (remaining_terms)

    Args:
        expr: Expression to factor

    Returns:
        Factored expression or original if no common factors

    Examples:
        >>> x = VarRef("x")
        >>> y = VarRef("y")
        >>> z = VarRef("z")
        >>> # x*y + x*z
        >>> expr = Binary("+", Binary("*", x, y), Binary("*", x, z))
        >>> result = factor_common_terms(expr)
        >>> # Should be: x * (y + z)
    """
    # Only handle addition at top level
    if not isinstance(expr, Binary) or expr.op != "+":
        return expr

    # Flatten addition into terms
    terms = _flatten_addition(expr)

    # Get factors for each term
    term_factors = [_flatten_multiplication(term) for term in terms]

    # Find common factors across ALL terms
    if not term_factors:
        return expr

    common_factors = set(term_factors[0])
    for factors in term_factors[1:]:
        common_factors &= set(factors)

    # If no common factors, return original
    if not common_factors:
        return expr

    common_factors_list = list(common_factors)

    # Extract remaining factors from each term
    remaining_terms = []
    for factors in term_factors:
        remaining = [f for f in factors if f not in common_factors_list]
        if remaining:
            remaining_terms.append(_rebuild_multiplication(remaining))
        else:
            # All factors were common (e.g., x + x → 2*x case handled elsewhere)
            remaining_terms.append(Const(1.0))

    # Rebuild factored expression: common * (remaining_sum)
    common_part = _rebuild_multiplication(common_factors_list)
    remaining_sum = _rebuild_addition(remaining_terms)

    return Binary("*", common_part, remaining_sum)


def factor_multi_terms(expr: Expr) -> Expr:
    """
    Multi-term factoring: a*c + a*d + b*c + b*d → (a + b)*(c + d)

    Algorithm:
    1. Flatten addition into terms
    2. For each term, flatten multiplication into factors
    3. Group terms by partial common factors
    4. If groups have identical remaining factors, factor again
    5. Rebuild: (sum_of_group_factors) * (remaining_factors)

    This is a 2x2 pattern matcher for now (4 terms).

    Args:
        expr: Expression to factor

    Returns:
        Factored expression or original if pattern doesn't match

    Examples:
        >>> a = VarRef("a")
        >>> b = VarRef("b")
        >>> c = VarRef("c")
        >>> d = VarRef("d")
        >>> # a*c + a*d + b*c + b*d
        >>> expr = Binary("+",
        ...     Binary("+",
        ...         Binary("+", Binary("*", a, c), Binary("*", a, d)),
        ...         Binary("*", b, c)),
        ...     Binary("*", b, d))
        >>> result = factor_multi_terms(expr)
        >>> # Should be: (a + b) * (c + d)
    """
    # Only handle addition at top level
    if not isinstance(expr, Binary) or expr.op != "+":
        return expr

    # Flatten addition into terms
    terms = _flatten_addition(expr)

    # Need exactly 4 terms for 2x2 pattern
    if len(terms) != 4:
        return expr

    # Get factors for each term
    term_factors = [_flatten_multiplication(term) for term in terms]

    # Try to find 2x2 pattern:
    # Group terms by partial common factors
    # Look for two groups of 2 terms each where:
    # - Terms in same group share some factors
    # - Remaining factors are identical across groups

    # Simple approach: try each possible pair of factors as "first group common"
    for i in range(len(term_factors[0])):
        for j in range(i, len(term_factors[0])):
            # Try factors[i] and/or factors[j] as group1 common
            potential_group1_common = {term_factors[0][i]}
            if j != i:
                potential_group1_common.add(term_factors[0][j])

            # Find which terms contain these factors
            group1_indices = []
            group2_indices = []

            for idx, factors in enumerate(term_factors):
                if potential_group1_common.issubset(set(factors)):
                    group1_indices.append(idx)
                else:
                    group2_indices.append(idx)

            # Need 2 terms in each group
            if len(group1_indices) != 2 or len(group2_indices) != 2:
                continue

            # Get remaining factors for each group
            group1_remaining = []
            for idx in group1_indices:
                remaining = [f for f in term_factors[idx] if f not in potential_group1_common]
                group1_remaining.append(set(remaining))

            # Check if group1 terms have identical remaining factors
            if len(group1_remaining) != 2 or group1_remaining[0] != group1_remaining[1]:
                continue

            # Get remaining for group2
            group2_factors_sets = [set(term_factors[idx]) for idx in group2_indices]

            # Find common in group2
            group2_common = group2_factors_sets[0] & group2_factors_sets[1]

            # Get group2 remaining
            group2_remaining = []
            for idx in group2_indices:
                remaining = [f for f in term_factors[idx] if f not in group2_common]
                group2_remaining.append(set(remaining))

            # Check if group2 remaining identical and matches group1 remaining
            if len(group2_remaining) == 2 and group2_remaining[0] == group2_remaining[1]:
                if group1_remaining[0] == group2_remaining[0]:
                    # Found 2x2 pattern!
                    # (group1_common + group2_common) * group1_remaining

                    sum_part = Binary(
                        "+",
                        _rebuild_multiplication(list(potential_group1_common)),
                        _rebuild_multiplication(list(group2_common)),
                    )

                    remaining_part = _rebuild_multiplication(list(group1_remaining[0]))

                    return Binary("*", sum_part, remaining_part)

    # No 2x2 pattern found
    return expr


def count_operations(expr: Expr) -> int:
    """
    Count the number of operations in an expression.

    Args:
        expr: Expression to count

    Returns:
        Number of binary/unary operations
    """
    if isinstance(expr, (Const, VarRef)):
        return 0
    if isinstance(expr, Binary):
        return 1 + count_operations(expr.left) + count_operations(expr.right)
    # Add other node types as needed
    return 0


if __name__ == "__main__":
    # Quick test
    x = VarRef("x")
    y = VarRef("y")
    z = VarRef("z")

    # Test 1: x*y + x*z → x*(y + z)
    print("Test 1: Distribution cancellation")
    expr1 = Binary("+", Binary("*", x, y), Binary("*", x, z))
    print(f"Before: {expr1}")
    print(f"Operations: {count_operations(expr1)}")

    result1 = factor_common_terms(expr1)
    print(f"After:  {result1}")
    print(f"Operations: {count_operations(result1)}")
    print()

    # Test 2: Multi-term (simplified for now)
    print("Test 2: Multi-term factoring (2x2)")
    a = VarRef("a")
    b = VarRef("b")
    c = VarRef("c")
    d = VarRef("d")

    # a*c + a*d + b*c + b*d
    expr2 = Binary(
        "+",
        Binary("+", Binary("+", Binary("*", a, c), Binary("*", a, d)), Binary("*", b, c)),
        Binary("*", b, d),
    )
    print(f"Before: {expr2}")
    print(f"Operations: {count_operations(expr2)}")

    result2 = factor_multi_terms(expr2)
    print(f"After:  {result2}")
    print(f"Operations: {count_operations(result2)}")
