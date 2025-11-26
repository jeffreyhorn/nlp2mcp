"""Power expression consolidation transformation.

This module implements T2.3: Power Expression Consolidation transformation for
aggressive simplification. It applies algebraic rules for power operations.

Patterns:
- x^a * x^b → x^(a+b)
- (x^a)^b → x^(a*b)
- x^1 → x
- x^0 → 1

Example:
    x^2 * x^3 → x^5
    (x^2)^3 → x^6

Priority: MEDIUM (useful for derivative expressions with power rules)
"""

from src.ir.ast import Binary, Const, Expr
from src.ir.transformations.utils import flatten_multiplication


def consolidate_powers(expr: Expr) -> Expr:
    """Consolidate power expressions using algebraic rules.

    Applies the following transformations:
    1. x^a * x^b → x^(a+b)
    2. (x^a)^b → x^(a*b)
    3. x^1 → x
    4. x^0 → 1

    Algorithm:
        1. Check for power-of-power: (x^a)^b
        2. Check for product of powers: x^a * x^b
        3. Check for trivial powers: x^0, x^1

    Args:
        expr: Expression to transform

    Returns:
        Transformed expression with consolidated powers,
        or original if no power rules apply

    Example:
        >>> # x^2 * x^3 → x^5
        >>> x = Var("x")
        >>> expr = Binary("*", Binary("**", x, Const(2)), Binary("**", x, Const(3)))
        >>> result = consolidate_powers(expr)
        >>> # result = Binary("**", x, Const(5))
    """
    # Check for power-of-power: (x^a)^b → x^(a*b)
    if isinstance(expr, Binary) and expr.op == "**":
        base = expr.left
        exponent = expr.right

        # Trivial power rules
        # x^0 → 1
        if isinstance(exponent, Const) and exponent.value == 0:
            return Const(1)

        # x^1 → x
        if isinstance(exponent, Const) and exponent.value == 1:
            return base

        # (x^a)^b → x^(a*b)
        if isinstance(base, Binary) and base.op == "**":
            inner_base = base.left
            inner_exponent = base.right

            # Both exponents must be constants for safe consolidation
            if isinstance(inner_exponent, Const) and isinstance(exponent, Const):
                new_exponent = Const(inner_exponent.value * exponent.value)
                return Binary("**", inner_base, new_exponent)

        return expr

    # Check for product of powers: x^a * x^b → x^(a+b)
    if isinstance(expr, Binary) and expr.op == "*":
        return _consolidate_power_products(expr)

    return expr


def _consolidate_power_products(expr: Expr) -> Expr:
    """Consolidate products of powers with the same base.

    Pattern: x^a * x^b * ... → x^(a+b+...)

    Args:
        expr: Multiplication expression

    Returns:
        Expression with power products consolidated
    """
    # Flatten multiplication
    factors = flatten_multiplication(expr)

    # Group factors by base for power expressions
    power_groups: dict[str, list[tuple[Expr, Expr]]] = {}  # base_key -> [(base, exp), ...]
    non_power_factors: list[Expr] = []

    for factor in factors:
        if isinstance(factor, Binary) and factor.op == "**":
            base = factor.left
            exponent = factor.right

            # Only consolidate if exponent is a constant (safe)
            if isinstance(exponent, Const):
                base_key = _get_base_key(base)
                if base_key not in power_groups:
                    power_groups[base_key] = []
                power_groups[base_key].append((base, exponent))
            else:
                non_power_factors.append(factor)
        else:
            # Not a power expression
            non_power_factors.append(factor)

    # Consolidate power groups
    consolidated_factors: list[Expr] = []

    for _base_key, power_list in power_groups.items():
        if len(power_list) == 1:
            # Only one power with this base, keep as-is
            base, exp = power_list[0]
            consolidated_factors.append(Binary("**", base, exp))
        else:
            # Multiple powers with same base: x^a * x^b → x^(a+b)
            base, _ = power_list[0]  # Use first base

            # Sum exponents
            total_exponent = 0.0
            for _, exp in power_list:
                if isinstance(exp, Const):
                    total_exponent += exp.value

            # Build consolidated power
            consolidated_factors.append(Binary("**", base, Const(total_exponent)))

    # Add non-power factors
    consolidated_factors.extend(non_power_factors)

    # Rebuild multiplication
    if len(consolidated_factors) == 0:
        return Const(1)
    elif len(consolidated_factors) == 1:
        return consolidated_factors[0]
    else:
        result = consolidated_factors[0]
        for factor in consolidated_factors[1:]:
            result = Binary("*", result, factor)
        return result


def _get_base_key(base: Expr) -> str:
    """Get a string key representing the base expression.

    This is used to group powers by their base.

    Args:
        base: Base expression

    Returns:
        String representation of the base
    """
    # Simple approach: use repr()
    # For more sophisticated matching, could use expression hashing
    return repr(base)
