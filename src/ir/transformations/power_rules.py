"""Power expression consolidation transformation.

This module implements T2.3: Power Expression Consolidation transformation for
aggressive simplification. It applies algebraic rules for power operations.

Patterns:
- x^a * x^b → x^(a+b)
- (x^a)^b → x^(a*b)
- x^1 → x
- x^0 → 1
- x * x^a → x^(1+a)  (implicit exponent of 1)

Example:
    x^2 * x^3 → x^5
    (x^2)^3 → x^6
    x * x^2 → x^3

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
        >>> x = SymbolRef("x")
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

    Also handles implicit exponent of 1 for bare bases:
    - x * x^2 → x^3
    - x^2 * x → x^3

    Args:
        expr: Multiplication expression

    Returns:
        Expression with power products consolidated
    """
    # Flatten multiplication
    factors = flatten_multiplication(expr)

    # Group factors by base for power expressions
    # Treats bare factors as having implicit exponent of 1
    power_groups: dict[tuple, list[tuple[Expr, Expr]]] = {}  # base_key -> [(base, exp), ...]
    non_consolidatable: list[Expr] = []

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
                non_consolidatable.append(factor)
        else:
            # Bare factor: treat as having implicit exponent of 1
            # Only consolidate simple expressions (Const, SymbolRef, VarRef)
            # to avoid complex cases
            if _is_simple_base(factor):
                base_key = _get_base_key(factor)
                if base_key not in power_groups:
                    power_groups[base_key] = []
                power_groups[base_key].append((factor, Const(1)))
            else:
                non_consolidatable.append(factor)

    # Consolidate power groups
    consolidated_factors: list[Expr] = []

    for _base_key, power_list in power_groups.items():
        if len(power_list) == 1:
            # Only one power with this base
            base, exp = power_list[0]
            # If exponent is 1 (from implicit or explicit), return bare base
            if isinstance(exp, Const) and abs(exp.value - 1) < 1e-10:
                consolidated_factors.append(base)
            else:
                consolidated_factors.append(Binary("**", base, exp))
        else:
            # Multiple powers with same base: x^a * x^b → x^(a+b)
            base, _ = power_list[0]  # Use first base

            # Sum exponents
            total_exponent: int | float = 0
            for _, exp in power_list:
                if isinstance(exp, Const):
                    total_exponent += exp.value

            # Build consolidated power with edge case handling
            # Use epsilon comparison for floating-point safety
            if abs(total_exponent) < 1e-10:
                # x^0 = 1
                consolidated_factors.append(Const(1))
            elif abs(total_exponent - 1) < 1e-10:
                # x^1 = x
                consolidated_factors.append(base)
            else:
                consolidated_factors.append(Binary("**", base, Const(total_exponent)))

    # Add non-consolidatable factors
    consolidated_factors.extend(non_consolidatable)

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


def _is_simple_base(expr: Expr) -> bool:
    """Check if an expression is simple enough to treat as a power base.

    Simple bases are those that can safely have an implicit exponent of 1:
    - Constants (numbers)
    - Symbol references (variables)
    - Variable references
    - Parameter references

    Complex expressions like Binary operations are excluded to avoid
    unintended transformations.

    Args:
        expr: Expression to check

    Returns:
        True if expression is a simple base
    """
    from src.ir.ast import Const, ParamRef, SymbolRef, VarRef

    return isinstance(expr, (Const, SymbolRef, VarRef, ParamRef))


def _expr_structural_key(expr: Expr) -> tuple[str, ...]:
    """Recursively generate a structural key for an expression.

    Args:
        expr: Expression to generate key for

    Returns:
        Tuple representing the structural key. Returns a tuple with at least
        one element (the type discriminator), and potentially more elements
        depending on the expression type.
    """
    from src.ir.ast import Binary, Const, SymbolRef

    if isinstance(expr, Binary):
        return (
            "Binary",
            expr.op,
            str(_expr_structural_key(expr.left)),
            str(_expr_structural_key(expr.right)),
        )
    elif isinstance(expr, Const):
        return ("Const", str(expr.value))
    elif isinstance(expr, SymbolRef):
        return ("SymbolRef", expr.name)
    else:
        # Fallback for other types
        return (type(expr).__name__, repr(expr))


def _get_base_key(base: Expr) -> tuple:
    """Get a structural key representing the base expression.

    This is used to group powers by their base. Uses structural equality
    rather than repr() to correctly identify equivalent expressions.

    Args:
        base: Base expression

    Returns:
        Structural key of the base
    """
    return _expr_structural_key(base)
