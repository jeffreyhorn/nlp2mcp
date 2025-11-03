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

from ..ir.ast import Binary, Const, Expr


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
    # Use repr() as key since Expr is frozen and hashable via dataclass
    base_to_coeff: dict[str, tuple[float, Expr]] = {}

    for term in terms:
        # Use repr of base as dictionary key
        base_key = repr(term.base)

        if base_key in base_to_coeff:
            # Add coefficient to existing term
            existing_coeff, existing_base = base_to_coeff[base_key]
            base_to_coeff[base_key] = (existing_coeff + term.coeff, existing_base)
        else:
            # New term
            base_to_coeff[base_key] = (term.coeff, term.base)

    # Convert back to list of Terms
    collected = [Term(coeff=coeff, base=base) for coeff, base in base_to_coeff.values()]

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
            from ..ir.ast import Unary

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
