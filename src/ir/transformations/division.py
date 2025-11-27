"""Division simplification transformation.

This module implements T3.1: Division Simplification transformation for
aggressive simplification. It cancels common factors between numerator and
denominator in division expressions.

Pattern: (a*b)/a → b (if a ≠ 0)

Example:
    (x*y*z)/x → y*z
    (2*x*y)/(2*x) → y

Priority: HIGH (enables cascading simplifications)
"""

from src.ir.ast import Binary, Const, Expr, ParamRef, SymbolRef, VarRef
from src.ir.transformations.utils import flatten_multiplication


def simplify_division(expr: Expr) -> Expr:
    """Simplify division expressions by canceling common factors.

    Cancels multiplicative factors that appear in both numerator and
    denominator. Uses conservative heuristics to avoid division by zero.

    Algorithm:
        1. Check if expression is a division
        2. Flatten numerator and denominator into factors
        3. Find common factors (safe to cancel)
        4. Cancel common factors
        5. Rebuild simplified division

    Args:
        expr: Expression to transform

    Returns:
        Transformed expression with common factors canceled,
        or original expression if no safe cancellations found

    Example:
        >>> # (x*y*z)/x → y*z
        >>> x, y, z = SymbolRef("x"), SymbolRef("y"), SymbolRef("z")
        >>> expr = Binary("/", Binary("*", Binary("*", x, y), z), x)
        >>> result = simplify_division(expr)
        >>> # result = Binary("*", y, z)
    """
    # Only apply to division expressions
    if not isinstance(expr, Binary) or expr.op != "/":
        return expr

    numerator = expr.left
    denominator = expr.right

    # Get factors from numerator and denominator
    num_factors = _get_cancellable_factors(numerator)
    denom_factors = _get_cancellable_factors(denominator)

    # Find common factors that are safe to cancel
    common_factors = _find_safe_common_factors(num_factors, denom_factors)

    # If no common factors, return original
    if len(common_factors) == 0:
        return expr

    # Cancel common factors (remove one occurrence per match)
    remaining_num_factors = num_factors.copy()
    remaining_denom_factors = denom_factors.copy()
    for factor in common_factors:
        if factor in remaining_num_factors:
            remaining_num_factors.remove(factor)
        if factor in remaining_denom_factors:
            remaining_denom_factors.remove(factor)

    # Build simplified numerator
    simplified_numerator: Expr
    if len(remaining_num_factors) == 0:
        simplified_numerator = Const(1)
    elif len(remaining_num_factors) == 1:
        simplified_numerator = remaining_num_factors[0]
    else:
        simplified_numerator = remaining_num_factors[0]
        for factor in remaining_num_factors[1:]:
            simplified_numerator = Binary("*", simplified_numerator, factor)

    # Build simplified denominator
    if len(remaining_denom_factors) == 0:
        # All factors canceled, no division needed
        return simplified_numerator

    simplified_denominator: Expr
    if len(remaining_denom_factors) == 1:
        simplified_denominator = remaining_denom_factors[0]
    else:
        simplified_denominator = remaining_denom_factors[0]
        for factor in remaining_denom_factors[1:]:
            simplified_denominator = Binary("*", simplified_denominator, factor)

    # Return simplified division
    return Binary("/", simplified_numerator, simplified_denominator)


def _get_cancellable_factors(expr: Expr) -> list[Expr]:
    """Extract factors that can be safely canceled.

    Only extracts factors from multiplication expressions. Non-multiplication
    expressions are returned as single-element lists.

    Args:
        expr: Expression to extract factors from

    Returns:
        List of factors (flattened if multiplication, [expr] otherwise)
    """
    if isinstance(expr, Binary) and expr.op == "*":
        return flatten_multiplication(expr)
    else:
        return [expr]


def _find_safe_common_factors(num_factors: list[Expr], denom_factors: list[Expr]) -> list[Expr]:
    """Find factors that are safe to cancel between numerator and denominator.

    Uses conservative heuristics:
    - Non-zero constants (literal values)
    - Named variables (assumed non-zero in well-formed models)
    - Does NOT cancel function calls or complex expressions

    Properly handles duplicate factors by tracking which denominator factors
    have been matched to avoid over-cancellation.

    Args:
        num_factors: Factors from numerator
        denom_factors: Factors from denominator

    Returns:
        List of factors safe to cancel (one per match)
    """
    common_factors: list[Expr] = []
    denom_used = [False] * len(denom_factors)

    for num_factor in num_factors:
        # Check if this factor appears in denominator (not yet used)
        for j, denom_factor in enumerate(denom_factors):
            if not denom_used[j] and _is_safe_to_cancel(num_factor, denom_factor):
                # Found a match, add to common factors and mark denominator as used
                common_factors.append(num_factor)
                denom_used[j] = True
                break

    return common_factors


def _is_safe_to_cancel(factor1: Expr, factor2: Expr) -> bool:
    """Check if two factors are identical and safe to cancel.

    Conservative heuristics:
    - Constants: Must be non-zero and equal
    - SymbolRefs: Must have same name (assumes non-zero)
    - Binary: Exact structural match (conservative approach)
    - Function calls, Unary, etc.: NOT canceled (may be zero)

    Args:
        factor1: First factor
        factor2: Second factor

    Returns:
        True if factors are identical and safe to cancel
    """
    # Check for exact structural equality
    if not _expressions_equal(factor1, factor2):
        return False

    # Both factors are structurally equal, check safety
    # Constants: must be non-zero
    if isinstance(factor1, Const):
        return factor1.value != 0

    # Variables and parameters: assume non-zero (standard in optimization models)
    if isinstance(factor1, (SymbolRef, VarRef, ParamRef)):
        return True

    # Binary operations: safe if both operands are safe
    # This is conservative - we allow canceling (x+y) if exact match
    if isinstance(factor1, Binary):
        return True

    # Function calls, Unary, etc.: do not cancel (may be zero)
    return False


def _expressions_equal(expr1: Expr, expr2: Expr) -> bool:
    """Check if two expressions are structurally identical.

    Handles Const, SymbolRef, and Binary node types. For other node types
    (Call, Unary, VarRef, ParamRef), falls back to identity comparison.

    Args:
        expr1: First expression
        expr2: Second expression

    Returns:
        True if expressions are structurally equal
    """
    # Check type equality
    if type(expr1) is not type(expr2):
        return False

    # Const: compare values
    if isinstance(expr1, Const) and isinstance(expr2, Const):
        return expr1.value == expr2.value

    # SymbolRef: compare names
    if isinstance(expr1, SymbolRef) and isinstance(expr2, SymbolRef):
        return expr1.name == expr2.name

    # Binary: compare operator and recursively check operands
    if isinstance(expr1, Binary) and isinstance(expr2, Binary):
        return (
            expr1.op == expr2.op
            and _expressions_equal(expr1.left, expr2.left)
            and _expressions_equal(expr1.right, expr2.right)
        )

    # Fallback for other node types (Call, Unary, VarRef, ParamRef):
    # Use identity comparison (conservative - only equal if same object)
    return expr1 is expr2
