"""AST to GAMS expression converter.

This module converts IR expression AST nodes to GAMS syntax strings.
Handles operator precedence, function calls, and all AST node types including MultiplierRef.
"""

from src.ir.ast import (
    Binary,
    Call,
    Const,
    EquationRef,
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

    This function uses a heuristic to distinguish between domain variables
    (set indices like 'i', 'j', 'nodes') and element labels (specific values like 'i1', 'H2').

    Heuristic:
    - All-lowercase identifier-like names (letters/underscores only) are domain variables → unquoted
    - Names containing digits, uppercase letters, or special chars are element labels → quoted

    This addresses GAMS compilation errors from inconsistent quoting (Error 171,
    Error 340) while preserving correct behavior for indexed equations.

    Args:
        indices: Tuple of index identifiers

    Returns:
        List of appropriately quoted/unquoted indices

    Examples:
        >>> _quote_indices(("i",))
        ['i']
        >>> _quote_indices(("i1",))
        ['"i1"']
        >>> _quote_indices(("i", "j"))
        ['i', 'j']
        >>> _quote_indices(("nodes",))
        ['nodes']
        >>> _quote_indices(("flow_var",))
        ['flow_var']
        >>> _quote_indices(("H", "H2", "H2O"))
        ['"H"', '"H2"', '"H2O"']
        >>> _quote_indices(("c",))
        ['c']
        >>> _quote_indices(("OH",))
        ['"OH"']
    """
    result = []
    for idx in indices:
        # All-lowercase identifier (letters and underscores only) = domain variable, don't quote
        # This handles patterns like sum(i, ...), x(nodes), flow(years)
        # Element labels typically contain digits (i1, H2) or uppercase (H, OH, H2O)
        if idx.replace("_", "").isalpha() and idx.islower():
            result.append(idx)
        else:
            # Everything else is an element label, quote it for consistency
            result.append(f'"{idx}"')
    return result


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

        case VarRef() as var_ref:
            if var_ref.indices:
                quoted_indices = _quote_indices(var_ref.indices_as_strings())
                indices_str = ",".join(quoted_indices)
                return f"{var_ref.name}({indices_str})"
            return var_ref.name

        case ParamRef() as param_ref:
            if param_ref.indices:
                quoted_indices = _quote_indices(param_ref.indices_as_strings())
                indices_str = ",".join(quoted_indices)
                return f"{param_ref.name}({indices_str})"
            return param_ref.name

        case MultiplierRef() as mult_ref:
            if mult_ref.indices:
                quoted_indices = _quote_indices(mult_ref.indices_as_strings())
                indices_str = ",".join(quoted_indices)
                return f"{mult_ref.name}({indices_str})"
            return mult_ref.name

        case EquationRef() as eq_ref:
            # Equation attribute access: eq.m, eq.l('1'), etc.
            if eq_ref.indices:
                quoted_indices = _quote_indices(eq_ref.indices_as_strings())
                indices_str = ",".join(quoted_indices)
                return f"{eq_ref.name}.{eq_ref.attribute}({indices_str})"
            return f"{eq_ref.name}.{eq_ref.attribute}"

        case Unary(op, child):
            child_str = expr_to_gams(child, parent_op=op)
            # GAMS unary operators: +, -
            # For unary minus, ALWAYS convert to multiplication form to avoid GAMS Error 445
            # ("More than one operator in a row"). This happens when unary minus follows
            # other operators like ".." (equation definition), "+", "-", etc.
            # Solution: -(expr) becomes ((-1) * (expr)) which GAMS parses correctly.
            if op == "-":
                # Wrap child in parentheses if it's a complex expression (Binary or Call)
                # or a negative constant (to avoid ((-1) * -5) which has two operators in a row)
                # Simple cases like -x become (-1) * x, complex like -(a+b) become (-1) * (a+b)
                is_negative_const = isinstance(child, Const) and child.value < 0
                if isinstance(child, (Binary, Call)) or is_negative_const:
                    return f"((-1) * ({child_str}))"
                else:
                    return f"((-1) * {child_str})"
            # Unary plus can be passed through directly
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

            # Special handling: wrap negative constants in parentheses to avoid GAMS Error 445
            # ("More than one operator in a row").
            #
            # For multiplication/division, GAMS cannot parse negative constants without parens:
            # - Left operand: "a + -1 * b" is invalid → becomes "a + (-1) * b"
            # - Right operand: "y * -1" is invalid → becomes "y * (-1)"
            #
            # Other operators like exponentiation (**) don't currently need this fix.
            if op in ("*", "/") and isinstance(left, Const) and left.value < 0:
                left_str = f"({left_str})"
            if op in ("*", "/") and isinstance(right, Const) and right.value < 0:
                right_str = f"({right_str})"

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
