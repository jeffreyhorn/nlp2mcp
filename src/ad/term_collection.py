"""
Advanced algebraic simplification through term collection.

This module provides functions to collect constants and like terms in expressions:
- Constant collection: 1 + x + 1 → x + 2
- Like-term collection: x + y + x + y → 2*x + 2*y

The approach:
1. Flatten associative operations (+ and *) into lists
2. Extract terms with coefficients (e.g., 3*x → Term(coeff=3, base=x))
3. Collect terms by their base expression
4. Rebuild simplified expression

This is integrated as an optional pass in the main simplify() function.
"""

from dataclasses import dataclass

from ..ir.ast import Binary, Const, Expr, Unary


@dataclass(frozen=True)
class Term:
    """
    Represents a term as coefficient * base.

    Examples:
        3*x → Term(coeff=3, base=VarRef("x"))
        x → Term(coeff=1, base=VarRef("x"))
        5 → Term(coeff=5, base=Const(1))
    """

    coeff: float
    base: Expr

    def __repr__(self) -> str:
        if isinstance(self.base, Const) and self.base.value == 1:
            return f"Term({self.coeff})"
        return f"Term({self.coeff} * {self.base!r})"


def _flatten_addition(expr: Expr) -> list[Expr]:
    """
    Flatten nested + operations into a list.

    Example:
        Binary("+", Binary("+", Const(1), VarRef("x")), Const(2))
        → [Const(1), VarRef("x"), Const(2)]

    Args:
        expr: Expression to flatten

    Returns:
        List of terms (flattened if expr is addition, [expr] otherwise)
    """
    if not isinstance(expr, Binary) or expr.op != "+":
        return [expr]

    # Recursively flatten left and right
    result = []
    result.extend(_flatten_addition(expr.left))
    result.extend(_flatten_addition(expr.right))
    return result


def _flatten_multiplication(expr: Expr) -> list[Expr]:
    """
    Flatten nested * operations into a list.

    Example:
        Binary("*", Const(2), Binary("*", Const(3), VarRef("x")))
        → [Const(2), Const(3), VarRef("x")]

    Args:
        expr: Expression to flatten

    Returns:
        List of factors (flattened if expr is multiplication, [expr] otherwise)
    """
    if not isinstance(expr, Binary) or expr.op != "*":
        return [expr]

    # Recursively flatten left and right
    result = []
    result.extend(_flatten_multiplication(expr.left))
    result.extend(_flatten_multiplication(expr.right))
    return result


def _extract_term(expr: Expr) -> Term:
    """
    Extract a term from an expression as (coefficient, base).

    Examples:
        Const(5) → Term(coeff=5, base=Const(1))
        VarRef("x") → Term(coeff=1, base=VarRef("x"))
        Binary("*", Const(3), VarRef("x")) → Term(coeff=3, base=VarRef("x"))
        Binary("*", VarRef("x"), Const(3)) → Term(coeff=3, base=VarRef("x"))

    Args:
        expr: Expression to extract term from

    Returns:
        Term with coefficient and base
    """
    # Case 1: Constant → coefficient is the value, base is 1
    if isinstance(expr, Const):
        return Term(coeff=expr.value, base=Const(1))

    # Case 2: Multiplication → look for constant factor
    if isinstance(expr, Binary) and expr.op == "*":
        factors = _flatten_multiplication(expr)

        # Separate constants from non-constants
        constants = [f for f in factors if isinstance(f, Const)]
        non_constants = [f for f in factors if not isinstance(f, Const)]

        # Calculate coefficient from constant factors
        coeff = 1.0
        for c in constants:
            coeff *= c.value

        # Build base from non-constant factors
        if len(non_constants) == 0:
            # All constants: 2 * 3 → Term(coeff=6, base=Const(1))
            return Term(coeff=coeff, base=Const(1))
        elif len(non_constants) == 1:
            # One non-constant: 3 * x → Term(coeff=3, base=x)
            return Term(coeff=coeff, base=non_constants[0])
        else:
            # Multiple non-constants: 3 * x * y → Term(coeff=3, base=x*y)
            base = non_constants[0]
            for factor in non_constants[1:]:
                base = Binary("*", base, factor)
            return Term(coeff=coeff, base=base)

    # Case 3: Other expression → coefficient is 1
    return Term(coeff=1.0, base=expr)


def _collect_terms(terms: list[Term]) -> list[Term]:
    """
    Collect like terms by summing coefficients.

    Example:
        [Term(3, x), Term(2, y), Term(5, x)] → [Term(8, x), Term(2, y)]

    Args:
        terms: List of terms to collect

    Returns:
        List of collected terms (terms with same base are combined)
    """
    # Group terms by their base expression
    # Use Expr directly as key. This requires all Expr subclasses to be defined
    # with @dataclass(frozen=True) for hashability and immutability.
    # This is a critical requirement enforced in src/ir/ast.py base definitions.
    base_to_coeff: dict[Expr, float] = {}

    for term in terms:
        # Use base Expr as dictionary key
        base_key = term.base

        if base_key in base_to_coeff:
            # Add coefficient to existing term
            base_to_coeff[base_key] += term.coeff
        else:
            # New term
            base_to_coeff[base_key] = term.coeff

    # Convert back to list of Terms
    collected = [Term(coeff=coeff, base=base) for base, coeff in base_to_coeff.items()]

    # Filter out terms with zero coefficient
    collected = [t for t in collected if t.coeff != 0]

    return collected


def _rebuild_sum(terms: list[Term]) -> Expr:
    """
    Rebuild an expression from a list of terms.

    Example:
        [Term(2, x), Term(3, y), Term(5, Const(1))] → 2*x + 3*y + 5

    Args:
        terms: List of terms to rebuild into expression

    Returns:
        Expression representing the sum of terms
    """
    if len(terms) == 0:
        return Const(0)

    # Convert each term to an expression
    expr_terms: list[Expr] = []
    for term in terms:
        # Special case: constant term (base is Const(1))
        if isinstance(term.base, Const) and term.base.value == 1:
            expr_terms.append(Const(term.coeff))
        # Special case: coefficient is 1
        elif term.coeff == 1:
            expr_terms.append(term.base)
        # Special case: coefficient is -1
        elif term.coeff == -1:
            expr_terms.append(Unary("-", term.base))
        # General case: multiply coefficient by base
        else:
            expr_terms.append(Binary("*", Const(term.coeff), term.base))

    # Build sum from left to right
    if len(expr_terms) == 1:
        return expr_terms[0]

    result = expr_terms[0]
    for expr_term in expr_terms[1:]:
        result = Binary("+", result, expr_term)

    return result


def collect_like_terms(expr: Expr) -> Expr:
    """
    Collect constants and like terms in an expression.

    This function handles:
    1. Constant collection: 1 + x + 1 → x + 2
    2. Like-term collection: x + y + x + y → 2*x + 2*y
    3. Nested cases: (1 + x) + (1 + y) → x + y + 2

    Only applies to addition at the top level. Recursively processes
    subexpressions first.

    Examples:
        >>> from src.ir.ast import Const, VarRef, Binary
        >>> expr = Binary("+", Binary("+", Const(1), VarRef("x", ())), Const(1))
        >>> result = collect_like_terms(expr)
        >>> # Result: Binary("+", VarRef("x", ()), Const(2))

    Args:
        expr: Expression to simplify via term collection

    Returns:
        Simplified expression with collected terms
    """
    # Only process addition at top level
    if not isinstance(expr, Binary) or expr.op != "+":
        return expr

    # Step 1: Flatten nested additions into a list
    addends = _flatten_addition(expr)

    # Step 2: Extract each addend as a term (coefficient, base)
    terms = [_extract_term(addend) for addend in addends]

    # Step 3: Collect like terms
    collected = _collect_terms(terms)

    # Step 4: Rebuild expression
    result = _rebuild_sum(collected)

    return result


def simplify_multiplicative_cancellation(expr: Expr) -> Expr:
    """
    Simplify multiplicative cancellation patterns: (c * x) / c → x.

    Handles patterns:
    - (c * expr) / c → expr
    - (expr * c) / c → expr

    Args:
        expr: Expression to simplify

    Returns:
        Simplified expression

    Examples:
        >>> # 2 * x / 2 → x
        >>> simplify_multiplicative_cancellation(Binary("/", Binary("*", Const(2), VarRef("x")), Const(2)))
        VarRef("x")

        >>> # x * 3 / 3 → x
        >>> simplify_multiplicative_cancellation(Binary("/", Binary("*", VarRef("x"), Const(3)), Const(3)))
        VarRef("x")
    """
    if not isinstance(expr, Binary) or expr.op != "/":
        return expr

    numerator = expr.left
    denominator = expr.right

    # Pattern: (c * expr) / c → expr
    if isinstance(numerator, Binary) and numerator.op == "*":
        left_factor = numerator.left
        right_factor = numerator.right

        # Check if left factor matches denominator
        if isinstance(left_factor, Const) and isinstance(denominator, Const):
            if left_factor.value == denominator.value and denominator.value != 0:
                # (c * expr) / c → expr
                return right_factor

        # Check if right factor matches denominator
        if isinstance(right_factor, Const) and isinstance(denominator, Const):
            if right_factor.value == denominator.value and denominator.value != 0:
                # (expr * c) / c → expr
                return left_factor

    return expr


def simplify_power_rules(expr: Expr) -> Expr:
    """
    Simplify power expressions using algebraic rules.

    Handles patterns:
    - x^a * x^b → x^(a+b) when a, b are constants
    - x^a / x^b → x^(a-b) when a, b are constants
    - (x^a)^b → x^(a*b) when a, b are constants

    Args:
        expr: Expression to simplify

    Returns:
        Simplified expression

    Examples:
        >>> # x^2 * x^3 → x^5
        >>> simplify_power_rules(Binary("*", Binary("**", VarRef("x"), Const(2)), Binary("**", VarRef("x"), Const(3))))
        Binary("**", VarRef("x"), Const(5))

        >>> # x^5 / x^2 → x^3
        >>> simplify_power_rules(Binary("/", Binary("**", VarRef("x"), Const(5)), Binary("**", VarRef("x"), Const(2))))
        Binary("**", VarRef("x"), Const(3))

        >>> # (x^2)^3 → x^6
        >>> simplify_power_rules(Binary("**", Binary("**", VarRef("x"), Const(2)), Const(3)))
        Binary("**", VarRef("x"), Const(6))
    """
    # Pattern 1: (x^a)^b → x^(a*b) when both exponents are constants
    if isinstance(expr, Binary) and expr.op == "**":
        base = expr.left
        outer_exp = expr.right

        if isinstance(base, Binary) and base.op == "**":
            inner_base = base.left
            inner_exp = base.right

            # Check if both exponents are constants
            if isinstance(inner_exp, Const) and isinstance(outer_exp, Const):
                # (x^a)^b → x^(a*b)
                new_exp = inner_exp.value * outer_exp.value
                return Binary("**", inner_base, Const(new_exp))

    # Pattern 2: x^a * x^b → x^(a+b) when bases match and exponents are constants
    if isinstance(expr, Binary) and expr.op == "*":
        left = expr.left
        right = expr.right

        # Check if both are power expressions with constant exponents
        if (
            isinstance(left, Binary)
            and left.op == "**"
            and isinstance(right, Binary)
            and right.op == "**"
        ):
            left_base = left.left
            left_exp = left.right
            right_base = right.left
            right_exp = right.right

            # Check if bases match and exponents are constants
            if (
                left_base == right_base
                and isinstance(left_exp, Const)
                and isinstance(right_exp, Const)
            ):
                # x^a * x^b → x^(a+b)
                new_exp = left_exp.value + right_exp.value
                if new_exp == 0:
                    # x^a * x^(-a) → x^0 → 1
                    return Const(1)
                elif new_exp == 1:
                    # x^a * x^(1-a) → x^1 → x
                    return left_base
                else:
                    return Binary("**", left_base, Const(new_exp))

        # Check for x * x^b → x^(1+b)
        if isinstance(right, Binary) and right.op == "**":
            right_base = right.left
            right_exp = right.right
            if left == right_base and isinstance(right_exp, Const):
                # x * x^b → x^(1+b)
                new_exp = 1 + right_exp.value
                if new_exp == 1:
                    return left
                else:
                    return Binary("**", left, Const(new_exp))

        # Check for x^a * x → x^(a+1)
        if isinstance(left, Binary) and left.op == "**":
            left_base = left.left
            left_exp = left.right
            if left_base == right and isinstance(left_exp, Const):
                # x^a * x → x^(a+1)
                new_exp = left_exp.value + 1
                if new_exp == 1:
                    return right
                else:
                    return Binary("**", right, Const(new_exp))

        # Check for x * x → x^2
        if left == right:
            return Binary("**", left, Const(2))

    # Pattern 3: x^a / x^b → x^(a-b) when bases match and exponents are constants
    if isinstance(expr, Binary) and expr.op == "/":
        numerator = expr.left
        denominator = expr.right

        # Check if both are power expressions with constant exponents
        if (
            isinstance(numerator, Binary)
            and numerator.op == "**"
            and isinstance(denominator, Binary)
            and denominator.op == "**"
        ):
            num_base = numerator.left
            num_exp = numerator.right
            denom_base = denominator.left
            denom_exp = denominator.right

            # Check if bases match and exponents are constants
            if (
                num_base == denom_base
                and isinstance(num_exp, Const)
                and isinstance(denom_exp, Const)
            ):
                # x^a / x^b → x^(a-b)
                new_exp = num_exp.value - denom_exp.value
                if new_exp == 0:
                    # x^a / x^a → x^0 → 1
                    return Const(1)
                elif new_exp == 1:
                    # x^(b+1) / x^b → x^1 → x
                    return num_base
                elif new_exp < 0:
                    # x^a / x^b where a < b → 1 / x^(b-a)
                    return Binary("/", Const(1), Binary("**", num_base, Const(-new_exp)))
                else:
                    return Binary("**", num_base, Const(new_exp))

        # Check for x^a / x → x^(a-1)
        if isinstance(numerator, Binary) and numerator.op == "**":
            num_base = numerator.left
            num_exp = numerator.right
            if num_base == denominator and isinstance(num_exp, Const):
                # x^a / x → x^(a-1)
                new_exp = num_exp.value - 1
                if new_exp == 0:
                    return Const(1)
                elif new_exp == 1:
                    return num_base
                elif new_exp < 0:
                    return Binary("/", Const(1), Binary("**", num_base, Const(-new_exp)))
                else:
                    return Binary("**", num_base, Const(new_exp))

        # Check for x / x^b → x^(1-b)
        if isinstance(denominator, Binary) and denominator.op == "**":
            denom_base = denominator.left
            denom_exp = denominator.right
            if numerator == denom_base and isinstance(denom_exp, Const):
                # x / x^b → x^(1-b)
                new_exp = 1 - denom_exp.value
                if new_exp == 0:
                    return Const(1)
                elif new_exp == 1:
                    return numerator
                elif new_exp < 0:
                    return Binary("/", Const(1), Binary("**", numerator, Const(-new_exp)))
                else:
                    return Binary("**", numerator, Const(new_exp))

        # x / x → 1 (already handled by basic simplify, but included for completeness)
        if numerator == denominator:
            return Const(1)

    return expr
