"""Logarithm simplification transformation.

This module implements T2.5: Logarithm Simplification transformation for
aggressive simplification. It applies logarithm rules to simplify expressions.

Patterns:
- log(a*b) → log(a) + log(b)
- log(a/b) → log(a) - log(b)
- log(a^n) → n*log(a)
- log(1) → 0
- log(e) → 1 (for natural log)

Example:
    log(x*y) → log(x) + log(y)
    log(x^2) → 2*log(x)

Priority: MEDIUM (useful for derivative expressions with logarithms)

Safety:
    - Only applies to log/ln calls (natural logarithm)
    - Does not check domain (assumes valid inputs)
    - Conservative: avoids increasing expression size significantly
"""

from src.ir.ast import Binary, Call, Const, Expr


def apply_log_rules(expr: Expr) -> Expr:
    """Apply logarithm rules to simplify expressions.

    Applies the following transformations:
    1. log(a*b) → log(a) + log(b)
    2. log(a/b) → log(a) - log(b)
    3. log(a^n) → n*log(a)
    4. log(1) → 0
    5. log(e) → 1 (e ≈ 2.71828)

    Conservative application: Only applies rules that simplify or are neutral.
    Does not apply expansions that significantly increase complexity.

    Algorithm:
        1. Check if expression is a log/ln call
        2. Apply simplification rules based on argument structure
        3. Recursively apply to subexpressions

    Args:
        expr: Expression to transform

    Returns:
        Transformed expression with log rules applied,
        or original if no rules apply

    Example:
        >>> # log(x*y) → log(x) + log(y)
        >>> x, y = SymbolRef("x"), SymbolRef("y")
        >>> expr = Call("log", [Binary("*", x, y)])
        >>> result = apply_log_rules(expr)
        >>> # result = Binary("+", Call("log", [x]), Call("log", [y]))
    """
    # Apply to Call nodes (log/ln)
    if isinstance(expr, Call) and _is_log_function(expr.func):
        result = _simplify_log_call(expr)
        if result != expr:
            return result

    # Recursively apply to subexpressions
    if isinstance(expr, Binary):
        left = apply_log_rules(expr.left)
        right = apply_log_rules(expr.right)
        if left != expr.left or right != expr.right:
            return Binary(expr.op, left, right)

    if isinstance(expr, Call):
        new_args = tuple(apply_log_rules(arg) for arg in expr.args)
        if any(new_arg != old_arg for new_arg, old_arg in zip(new_args, expr.args, strict=True)):
            return Call(expr.func, new_args)

    return expr


def _simplify_log_call(call: Call) -> Expr:
    """Simplify a log/ln function call.

    Args:
        call: Log function call

    Returns:
        Simplified expression or original if no simplification applies
    """
    if not _is_log_function(call.func) or len(call.args) != 1:
        return call

    arg = call.args[0]
    log_fn = call.func

    # Rule 1: log(1) → 0
    if isinstance(arg, Const) and arg.value == 1:
        return Const(0)

    # Rule 2: log(e) → 1 (for natural log)
    # e ≈ 2.71828182845904523536
    if isinstance(arg, Const) and abs(arg.value - 2.71828182845904523536) < 1e-10:
        return Const(1)

    # Rule 3: log(a*b) → log(a) + log(b)
    if isinstance(arg, Binary) and arg.op == "*":
        # Only apply if both operands are "simple" to avoid explosion
        if _is_simple_log_arg(arg.left) and _is_simple_log_arg(arg.right):
            return Binary("+", Call(log_fn, (arg.left,)), Call(log_fn, (arg.right,)))

    # Rule 4: log(a/b) → log(a) - log(b)
    if isinstance(arg, Binary) and arg.op == "/":
        # Only apply if both operands are "simple"
        if _is_simple_log_arg(arg.left) and _is_simple_log_arg(arg.right):
            return Binary("-", Call(log_fn, (arg.left,)), Call(log_fn, (arg.right,)))

    # Rule 5: log(a^n) → n*log(a)
    if isinstance(arg, Binary) and arg.op == "**":
        base = arg.left
        exponent = arg.right

        # Apply power rule: log(a^n) → n*log(a)
        # This is valid for any exponent (constant or variable)
        return Binary("*", exponent, Call(log_fn, (base,)))

    return call


def _is_log_function(name: str) -> bool:
    """Check if function name is a logarithm function.

    Args:
        name: Function name

    Returns:
        True if function is log or ln
    """
    return name in ("log", "ln")


def _is_simple_log_arg(expr: Expr) -> bool:
    """Check if an expression is simple enough for log expansion.

    Simple expressions are those that don't significantly increase complexity
    when log is applied to them separately.

    Simple args:
    - Constants
    - Symbols (variables, parameters)
    - Function calls
    - Powers (but not nested multiplications)

    Not simple:
    - Binary multiplication/division (would cause recursive expansion)

    Args:
        expr: Expression to check

    Returns:
        True if expression is simple for log expansion
    """
    from src.ir.ast import Call, Const, ParamRef, SymbolRef, VarRef

    # Constants, symbols, and function calls are simple
    if isinstance(expr, (Const, SymbolRef, VarRef, ParamRef, Call)):
        return True

    # Powers are simple
    if isinstance(expr, Binary) and expr.op == "**":
        return True

    # Other binary operations (especially * and /) are not simple
    # to avoid recursive expansion
    return False
