"""Trigonometric identity simplification transformation.

This module implements T2.4: Trigonometric Identities transformation for
aggressive simplification. It applies common trigonometric identities to
simplify expressions.

Patterns:
- sin^2(x) + cos^2(x) → 1
- tan(x) → sin(x)/cos(x)
- sec(x) → 1/cos(x)
- csc(x) → 1/sin(x)
- cot(x) → cos(x)/sin(x)

Example:
    sin^2(x) + cos^2(x) → 1
    tan(x) → sin(x)/cos(x)

Priority: MEDIUM (useful for some derivative expressions)
"""

from src.ir.ast import Binary, Call, Const, Expr
from src.ir.transformations.utils import expressions_equal, flatten_addition


def apply_trig_identities(expr: Expr) -> Expr:
    """Apply trigonometric identities to simplify expressions.

    Applies the following transformations:
    1. sin^2(x) + cos^2(x) → 1 (Pythagorean identity)
    2. tan(x) → sin(x)/cos(x)
    3. sec(x) → 1/cos(x)
    4. csc(x) → 1/sin(x)
    5. cot(x) → cos(x)/sin(x)

    Conservative application: Only applies common identities that reduce
    expression size or are neutral. Does not apply expansions that increase
    complexity.

    Algorithm:
        1. Check for addition (Pythagorean identity)
        2. Check for function calls (tan, sec, csc, cot)
        3. Recursively apply to subexpressions

    Args:
        expr: Expression to transform

    Returns:
        Transformed expression with trig identities applied,
        or original if no identities apply

    Example:
        >>> # sin^2(x) + cos^2(x) → 1
        >>> x = SymbolRef("x")
        >>> sin_x = Call("sin", [x])
        >>> cos_x = Call("cos", [x])
        >>> expr = Binary("+", Binary("**", sin_x, Const(2)), Binary("**", cos_x, Const(2)))
        >>> result = apply_trig_identities(expr)
        >>> # result = Const(1)
    """
    # Check for Pythagorean identity: sin^2(x) + cos^2(x) → 1
    if isinstance(expr, Binary) and expr.op == "+":
        result = _apply_pythagorean_identity(expr)
        if result != expr:
            return result

    # Check for trigonometric function conversions
    if isinstance(expr, Call):
        result = _convert_trig_function(expr)
        if result != expr:
            return result
        # Also recursively apply to arguments
        new_args = tuple(apply_trig_identities(arg) for arg in expr.args)
        if any(new_arg != old_arg for new_arg, old_arg in zip(new_args, expr.args, strict=True)):
            return Call(expr.func, new_args)

    # Recursively apply to subexpressions
    if isinstance(expr, Binary):
        left = apply_trig_identities(expr.left)
        right = apply_trig_identities(expr.right)
        if left != expr.left or right != expr.right:
            return Binary(expr.op, left, right)

    return expr


def _apply_pythagorean_identity(expr: Expr) -> Expr:
    """Apply Pythagorean identity: sin^2(x) + cos^2(x) → 1.

    Args:
        expr: Addition expression

    Returns:
        Const(1) if Pythagorean identity applies, otherwise original expression
    """
    if not isinstance(expr, Binary) or expr.op != "+":
        return expr

    # Flatten addition to handle multi-term sums
    terms = flatten_addition(expr)

    # Look for sin^2(x) and cos^2(x) pairs
    for i, term1 in enumerate(terms):
        if not _is_sin_squared(term1):
            continue

        # Get argument of sin (term1 is sin(x)^2, term1.left is sin(x))
        if isinstance(term1, Binary) and isinstance(term1.left, Call):
            sin_arg = term1.left.args[0]
        else:
            continue

        # Look for matching cos^2 with same argument
        for j, term2 in enumerate(terms):
            if i == j:
                continue

            if not _is_cos_squared(term2):
                continue

            # Get argument of cos (term2 is cos(x)^2, term2.left is cos(x))
            if isinstance(term2, Binary) and isinstance(term2.left, Call):
                cos_arg = term2.left.args[0]
            else:
                continue

            # Check if arguments match (structural equality)
            if expressions_equal(sin_arg, cos_arg):
                # Found a match! Replace sin^2(x) + cos^2(x) with 1
                remaining_terms = [t for k, t in enumerate(terms) if k != i and k != j]
                remaining_terms.append(Const(1))

                # Rebuild sum
                if len(remaining_terms) == 1:
                    return remaining_terms[0]
                else:
                    result = remaining_terms[0]
                    for term in remaining_terms[1:]:
                        result = Binary("+", result, term)
                    return result

    return expr


def _convert_trig_function(call: Call) -> Expr:
    """Convert trigonometric functions to simpler forms.

    Conversions:
    - tan(x) → sin(x)/cos(x)
    - sec(x) → 1/cos(x)
    - csc(x) → 1/sin(x)
    - cot(x) → cos(x)/sin(x)

    Args:
        call: Function call to potentially convert

    Returns:
        Converted expression or original if no conversion applies
    """
    if not isinstance(call, Call) or len(call.args) != 1:
        return call

    arg = call.args[0]

    if call.func == "tan":
        # tan(x) → sin(x)/cos(x)
        return Binary("/", Call("sin", (arg,)), Call("cos", (arg,)))
    elif call.func == "sec":
        # sec(x) → 1/cos(x)
        return Binary("/", Const(1), Call("cos", (arg,)))
    elif call.func == "csc":
        # csc(x) → 1/sin(x)
        return Binary("/", Const(1), Call("sin", (arg,)))
    elif call.func == "cot":
        # cot(x) → cos(x)/sin(x)
        return Binary("/", Call("cos", (arg,)), Call("sin", (arg,)))

    return call


def _is_sin_squared(expr: Expr) -> bool:
    """Check if expression is sin^2(x).

    Args:
        expr: Expression to check

    Returns:
        True if expression is sin(x)^2
    """
    if not isinstance(expr, Binary) or expr.op != "**":
        return False

    base = expr.left
    exponent = expr.right

    # Check if exponent is 2
    if not isinstance(exponent, Const) or exponent.value != 2:
        return False

    # Check if base is sin(x)
    return isinstance(base, Call) and base.func == "sin" and len(base.args) == 1


def _is_cos_squared(expr: Expr) -> bool:
    """Check if expression is cos^2(x).

    Args:
        expr: Expression to check

    Returns:
        True if expression is cos(x)^2
    """
    if not isinstance(expr, Binary) or expr.op != "**":
        return False

    base = expr.left
    exponent = expr.right

    # Check if exponent is 2
    if not isinstance(exponent, Const) or exponent.value != 2:
        return False

    # Check if base is cos(x)
    return isinstance(base, Call) and base.func == "cos" and len(base.args) == 1
