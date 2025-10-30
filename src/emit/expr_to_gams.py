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
}


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
            # Format floats nicely (avoid unnecessary decimals for integers)
            if isinstance(value, (int, float)) and value == int(value):
                return str(int(value))
            return str(value)

        case SymbolRef(name):
            return name

        case VarRef(name, indices):
            if indices:
                indices_str = ",".join(indices)
                return f"{name}({indices_str})"
            return name

        case ParamRef(name, indices):
            if indices:
                indices_str = ",".join(indices)
                return f"{name}({indices_str})"
            return name

        case MultiplierRef(name, indices):
            if indices:
                indices_str = ",".join(indices)
                return f"{name}({indices_str})"
            return name

        case Unary(op, child):
            child_str = expr_to_gams(child, parent_op=op)
            # GAMS unary operators: +, -
            return f"{op}{child_str}"

        case Binary(op, left, right):
            # Convert power operator to GAMS syntax
            if op == "^":
                # GAMS uses ** for exponentiation
                left_str = expr_to_gams(left, parent_op=op, is_right=False)
                right_str = expr_to_gams(right, parent_op=op, is_right=True)

                # Determine if we need parentheses for the whole expression
                needs_parens = _needs_parens(parent_op, op, is_right)
                result = f"{left_str} ** {right_str}"
                return f"({result})" if needs_parens else result

            # Other binary operators
            left_str = expr_to_gams(left, parent_op=op, is_right=False)
            right_str = expr_to_gams(right, parent_op=op, is_right=True)

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
