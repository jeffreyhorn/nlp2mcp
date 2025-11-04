"""AST to GAMS expression converter.

This module converts IR expression AST nodes to GAMS syntax strings.
Handles operator precedence, function calls, and all AST node types including MultiplierRef.
"""

from src.ir.ast import (
    Binary,
    Call,
    Const,
    Expr,
    MultiplierRef,
    ParamRef,
    Sum,
    SymbolRef,
    Unary,
    VarRef,
)

# Operator precedence levels (higher = tighter binding)
PRECEDENCE = {
    "or": 1,
    "and": 2,
    "=": 3,
    "<>": 3,
    "<": 3,
    ">": 3,
    "<=": 3,
    ">=": 3,
    "+": 4,
    "-": 4,
    "*": 5,
    "/": 5,
    "^": 6,  # Power operator (highest precedence)
    "**": 6,  # Alternative power operator syntax (same precedence as ^)
}


def _format_numeric(value: int | float) -> str:
    """Format numeric value for GAMS, avoiding unnecessary decimals.

    Args:
        value: Numeric value to format

    Returns:
        Formatted string representation

    Examples:
        >>> _format_numeric(3.0)
        '3'
        >>> _format_numeric(3.14)
        '3.14'
        >>> _format_numeric(5)
        '5'
    """
    if isinstance(value, (int, float)) and value == int(value):
        return str(int(value))
    return str(value)


def _quote_indices(indices: tuple[str, ...]) -> list[str]:
    """Quote element labels in index tuples for GAMS syntax.

    This function distinguishes between set indices and element labels using
    a heuristic: identifiers containing digits are assumed to be element labels
    and are quoted, while identifiers without digits are assumed to be set indices
    and are left unquoted.

    **Limitation**: This heuristic may fail if set indices legitimately contain
    digits (e.g., 'i2' as a set name, not an element). In such cases, the set
    index would be incorrectly quoted. A more robust solution would require
    access to the symbol table to determine the actual type.

    Args:
        indices: Tuple of index identifiers

    Returns:
        List of appropriately quoted indices

    Examples:
        >>> _quote_indices(("i",))
        ['i']
        >>> _quote_indices(("i1",))
        ['"i1"']
        >>> _quote_indices(("i", "j"))
        ['i', 'j']
        >>> _quote_indices(("i1", "j2"))
        ['"i1"', '"j2"']
        >>> # LIMITATION: This would fail for a set named "i2"
        >>> _quote_indices(("i2",))  # Incorrectly quotes if i2 is a set index
        ['"i2"']
    """
    return [f'"{idx}"' if any(c.isdigit() for c in idx) else idx for idx in indices]


def _needs_parens(parent_op: str | None, child_op: str | None, is_right: bool = False) -> bool:
    """Determine if child expression needs parentheses.

    Args:
        parent_op: Operator of parent expression (None if no parent)
        child_op: Operator of child expression (None if not a binary op)
        is_right: Whether child is the right operand of parent

    Returns:
        True if parentheses are needed
    """
    if parent_op is None or child_op is None:
        return False

    parent_prec = PRECEDENCE.get(parent_op, 0)
    child_prec = PRECEDENCE.get(child_op, 0)

    # Lower precedence always needs parens
    if child_prec < parent_prec:
        return True

    # Equal precedence on right side needs parens for non-associative ops
    # e.g., a - (b - c) vs a - b - c
    if child_prec == parent_prec and is_right:
        # Subtraction and division are left-associative
        if parent_op in ("-", "/", "^"):
            return True

    return False


def expr_to_gams(expr: Expr, parent_op: str | None = None, is_right: bool = False) -> str:
    """Convert an AST expression to GAMS syntax.

    Args:
        expr: Expression AST node
        parent_op: Operator of parent expression (for precedence handling)
        is_right: Whether this is the right operand of parent

    Returns:
        GAMS expression string

    Examples:
        >>> expr_to_gams(Const(3.14))
        '3.14'
        >>> expr_to_gams(VarRef("x", ("i",)))
        'x(i)'
        >>> expr_to_gams(Binary("+", Const(1), Const(2)))
        '1 + 2'
        >>> expr_to_gams(Binary("^", VarRef("x", ()), Const(2)))
        'x ** 2'
    """
    match expr:
        case Const(value):
            return _format_numeric(value)

        case SymbolRef(name):
            return name

        case VarRef(name, indices):
            if indices:
                quoted_indices = _quote_indices(indices)
                indices_str = ",".join(quoted_indices)
                return f"{name}({indices_str})"
            return name

        case ParamRef(name, indices):
            if indices:
                quoted_indices = _quote_indices(indices)
                indices_str = ",".join(quoted_indices)
                return f"{name}({indices_str})"
            return name

        case MultiplierRef(name, indices):
            if indices:
                quoted_indices = _quote_indices(indices)
                indices_str = ",".join(quoted_indices)
                return f"{name}({indices_str})"
            return name

        case Unary(op, child):
            child_str = expr_to_gams(child, parent_op=op)
            # GAMS unary operators: +, -
            # Add parentheses if child is a binary expression to preserve correctness
            # e.g., -(x - 10) not -x - 10
            if isinstance(child, Binary):
                return f"{op}({child_str})"
            # Parenthesize negative unary to avoid double operator issues
            # ONLY when there's a parent operator (e.g., x + -sin(y) becomes x + (-sin(y)))
            # Standalone negative (e.g., -x) doesn't need parentheses
            if op == "-" and parent_op is not None:
                return f"({op}{child_str})"
            return f"{op}{child_str}"

        case Binary(op, left, right):
            # Convert power operator to GAMS syntax
            # Handle both ^ and ** (term collection may generate **)
            if op in ("^", "**"):
                # GAMS uses ** for exponentiation
                left_str = expr_to_gams(left, parent_op=op, is_right=False)
                right_str = expr_to_gams(right, parent_op=op, is_right=True)

                # Determine if we need parentheses for the whole expression
                needs_parens = _needs_parens(parent_op, op, is_right)
                result = f"{left_str} ** {right_str}"
                return f"({result})" if needs_parens else result

            # Special handling for subtraction of negative constants
            # Convert "x - (-5)" to "x + 5" to avoid double operators
            if op == "-" and isinstance(right, Const) and right.value < 0:
                left_str = expr_to_gams(left, parent_op="+", is_right=False)
                # Negate the negative value to get positive
                right_val = -right.value
                right_str = _format_numeric(right_val)
                # Use addition instead
                needs_parens = _needs_parens(parent_op, "+", is_right)
                result = f"{left_str} + {right_str}"
                return f"({result})" if needs_parens else result

            # Other binary operators
            left_str = expr_to_gams(left, parent_op=op, is_right=False)
            right_str = expr_to_gams(right, parent_op=op, is_right=True)

            # Special handling: wrap negative constant in parentheses if it's the left operand
            # of multiplication/division to avoid GAMS "more than one operator in a row" error
            # e.g., "a + -1 * b" becomes "a + (-1) * b"
            #
            # Only multiplication (*) and division (/) require this treatment in GAMS because
            # GAMS parses "-1 * b" without parentheses as two operators in a row, which is invalid.
            # Other operators, such as exponentiation (**), do not currently require this fix.
            # If GAMS syntax changes or other operators are found to have similar issues,
            # consider extending this handling accordingly.
            if op in ("*", "/") and isinstance(left, Const) and left.value < 0:
                left_str = f"({left_str})"

            # Determine if we need parentheses
            needs_parens = _needs_parens(parent_op, op, is_right)
            result = f"{left_str} {op} {right_str}"
            return f"({result})" if needs_parens else result

        case Sum(index_sets, body):
            # GAMS: sum((i,j), body) or sum(i, body)
            body_str = expr_to_gams(body)
            if len(index_sets) == 1:
                return f"sum({index_sets[0]}, {body_str})"
            indices_str = ",".join(index_sets)
            return f"sum(({indices_str}), {body_str})"

        case Call(func, args):
            # Function calls: exp(x), log(x), sqrt(x), etc.
            args_str = ", ".join(expr_to_gams(arg) for arg in args)
            return f"{func}({args_str})"

        case _:
            # Fallback for unknown node types
            raise ValueError(f"Unknown expression type: {type(expr).__name__}")
