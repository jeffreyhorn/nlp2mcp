"""
Derivative Rules for Symbolic Differentiation

This module contains the differentiation rules for each AST node type.

Mathematical Foundation:
-----------------------
Each function implements a specific derivative rule:

1. Constant Rule: d(c)/dx = 0
2. Variable Rule: d(x)/dx = 1, d(y)/dx = 0
3. Sum Rule: d(f+g)/dx = df/dx + dg/dx (Day 2)
4. Product Rule: d(fg)/dx = f(dg/dx) + g(df/dx) (Day 2)
5. Quotient Rule: d(f/g)/dx = (g(df/dx) - f(dg/dx))/g² (Day 2)
6. Chain Rule: d(f(g))/dx = f'(g) * dg/dx (Days 3-4)
7. Power Rule: d(x^n)/dx = n*x^(n-1) (Day 3)
8. Exponential: d(exp(x))/dx = exp(x) (Day 3)
9. Logarithm: d(log(x))/dx = 1/x (Day 3)
10. Trigonometric: d(sin(x))/dx = cos(x), etc. (Day 4)

Day 1 Scope:
-----------
- Const: Always returns Const(0)
- VarRef/SymbolRef: Returns Const(1) if same variable, Const(0) otherwise
- ParamRef: Always returns Const(0) (parameters are constant w.r.t. variables)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..ir.ast import Expr

from ..ir.ast import Binary, Call, Const, ParamRef, Sum, SymbolRef, Unary, VarRef


def differentiate_expr(
    expr: Expr, wrt_var: str, wrt_indices: tuple[str, ...] | None = None
) -> Expr:
    """
    Main dispatcher for symbolic differentiation with index-aware matching.

    Routes to the appropriate differentiation rule based on expression type.
    Supports differentiation with respect to specific variable instances by
    providing optional index tuple.

    Args:
        expr: Expression to differentiate
        wrt_var: Variable name to differentiate with respect to (e.g., "x")
        wrt_indices: Optional variable indices (e.g., ("i1",) or ("i1", "j2"))
                     If None, matches any variable with name wrt_var (backward compatible)
                     If provided, only matches VarRef with exact indices

    Returns:
        Derivative expression (new AST)

    Raises:
        TypeError: If expression type is not supported (yet)

    Examples:
        >>> # Scalar variable (backward compatible)
        >>> differentiate_expr(VarRef("x"), "x")
        Const(1.0)

        >>> # Indexed variable without indices specified (matches any)
        >>> differentiate_expr(VarRef("x", ("i1",)), "x")
        Const(1.0)

        >>> # Index-aware differentiation (exact match)
        >>> differentiate_expr(VarRef("x", ("i1",)), "x", ("i1",))
        Const(1.0)

        >>> # Index-aware differentiation (mismatch)
        >>> differentiate_expr(VarRef("x", ("i2",)), "x", ("i1",))
        Const(0.0)
    """
    # Day 1: Constants and variable references
    if isinstance(expr, Const):
        return _diff_const(expr, wrt_var, wrt_indices)
    elif isinstance(expr, VarRef):
        return _diff_varref(expr, wrt_var, wrt_indices)
    elif isinstance(expr, SymbolRef):
        return _diff_symbolref(expr, wrt_var, wrt_indices)
    elif isinstance(expr, ParamRef):
        return _diff_paramref(expr, wrt_var, wrt_indices)

    # Day 2: Binary and Unary operations
    elif isinstance(expr, Binary):
        return _diff_binary(expr, wrt_var, wrt_indices)
    elif isinstance(expr, Unary):
        return _diff_unary(expr, wrt_var, wrt_indices)

    # Day 3: Function calls (power, exp, log, sqrt, trig)
    elif isinstance(expr, Call):
        return _diff_call(expr, wrt_var, wrt_indices)

    # Day 5: Sum aggregations
    elif isinstance(expr, Sum):
        return _diff_sum(expr, wrt_var, wrt_indices)

    raise TypeError(
        f"Differentiation not yet implemented for {type(expr).__name__}. "
        f"This will be added in subsequent days of Sprint 2."
    )


# ============================================================================
# Day 1: Basic Derivative Rules
# ============================================================================


def _diff_const(_expr: Const, _wrt_var: str, _wrt_indices: tuple[str, ...] | None = None) -> Const:
    """
    Derivative of a constant.

    Mathematical rule: d(c)/dx = 0

    Args:
        _expr: Constant expression (unused, derivative is always zero)
        _wrt_var: Variable name (unused, derivative is always zero)
        _wrt_indices: Optional index tuple (unused, derivative is always zero)

    Returns:
        Const(0.0)

    Example:
        >>> _diff_const(Const(5.0), "x", None)
        Const(0.0)
    """
    return Const(0.0)


def _diff_varref(expr: VarRef, wrt_var: str, wrt_indices: tuple[str, ...] | None = None) -> Const:
    """
    Derivative of a variable reference with index-aware matching.

    Mathematical rules:
    - d(x)/dx = 1   (same variable)
    - d(y)/dx = 0   (different variable)

    Index-aware matching:
    - If wrt_indices is None: Match any indices (backward compatible behavior)
      - d/dx x = 1, d/dx x(i) = 1 (all instances match)
    - If wrt_indices is provided: Exact index tuple matching required
      - d/dx(i1) x(i1) = 1 (exact match)
      - d/dx(i1) x(i2) = 0 (index mismatch)

    Args:
        expr: Variable reference
        wrt_var: Variable name to differentiate with respect to
        wrt_indices: Optional index tuple for specific variable instance.
                     None means match any indices (backward compatible).

    Returns:
        Const(1.0) if variable matches (name and indices), Const(0.0) otherwise

    Examples:
        >>> # Scalar variables (backward compatible)
        >>> _diff_varref(VarRef("x"), "x", None)
        Const(1.0)
        >>> _diff_varref(VarRef("y"), "x", None)
        Const(0.0)

        >>> # Indexed variables without wrt_indices (match any)
        >>> _diff_varref(VarRef("x", ("i",)), "x", None)
        Const(1.0)
        >>> _diff_varref(VarRef("x", ("j",)), "x", None)
        Const(1.0)

        >>> # Index-aware differentiation (exact match)
        >>> _diff_varref(VarRef("x", ("i1",)), "x", ("i1",))
        Const(1.0)
        >>> _diff_varref(VarRef("x", ("i2",)), "x", ("i1",))
        Const(0.0)

        >>> # Multi-dimensional indices
        >>> _diff_varref(VarRef("x", ("i1", "j2")), "x", ("i1", "j2"))
        Const(1.0)
        >>> _diff_varref(VarRef("x", ("i1", "j3")), "x", ("i1", "j2"))
        Const(0.0)
    """
    # Name must match
    if expr.name != wrt_var:
        return Const(0.0)

    # Index matching
    if wrt_indices is None:
        # No indices specified: match any (backward compatible)
        return Const(1.0)

    # Indices specified: must match exactly
    if expr.indices == wrt_indices:
        return Const(1.0)
    else:
        return Const(0.0)


def _diff_symbolref(
    expr: SymbolRef, wrt_var: str, wrt_indices: tuple[str, ...] | None = None
) -> Const:
    """
    Derivative of a scalar symbol reference.

    Mathematical rules:
    - d(x)/dx = 1   (same variable)
    - d(y)/dx = 0   (different variable)

    Note: SymbolRef is used for scalar (non-indexed) symbols, so wrt_indices
    should typically be None. This parameter is included for API consistency
    with other differentiation functions.

    Args:
        expr: Symbol reference
        wrt_var: Variable name to differentiate with respect to
        wrt_indices: Optional index tuple (typically None for scalar symbols)

    Returns:
        Const(1.0) if same variable name, Const(0.0) otherwise

    Examples:
        >>> _diff_symbolref(SymbolRef("x"), "x", None)
        Const(1.0)
        >>> _diff_symbolref(SymbolRef("y"), "x", None)
        Const(0.0)
    """
    if expr.name == wrt_var:
        return Const(1.0)
    else:
        return Const(0.0)


def _diff_paramref(
    _expr: ParamRef, _wrt_var: str, _wrt_indices: tuple[str, ...] | None = None
) -> Const:
    """
    Derivative of a parameter reference.

    Mathematical rule: d(param)/dx = 0

    Parameters are constant with respect to variables in the NLP.

    Args:
        _expr: Parameter reference (unused, derivative is always zero)
        _wrt_var: Variable name (unused, derivative is always zero)
        _wrt_indices: Optional index tuple (unused, derivative is always zero)

    Returns:
        Const(0.0)

    Example:
        >>> _diff_paramref(ParamRef("c"), "x", None)
        Const(0.0)
        >>> _diff_paramref(ParamRef("demand", ("i",)), "x", None)
        Const(0.0)
    """
    return Const(0.0)


# ============================================================================
# Day 2: Binary and Unary Operations
# ============================================================================


def _diff_binary(expr: Binary, wrt_var: str, wrt_indices: tuple[str, ...] | None = None) -> Expr:
    """
    Derivative of binary operations.

    Supports: +, -, *, /

    Mathematical rules:
    - Sum Rule: d(a+b)/dx = da/dx + db/dx
    - Difference Rule: d(a-b)/dx = da/dx - db/dx
    - Product Rule: d(a*b)/dx = b*(da/dx) + a*(db/dx)
    - Quotient Rule: d(a/b)/dx = (b*(da/dx) - a*(db/dx))/b²

    Args:
        expr: Binary expression
        wrt_var: Variable to differentiate with respect to
        wrt_indices: Optional index tuple for specific variable instance

    Returns:
        Derivative expression (new AST)

    Raises:
        ValueError: If operation is not supported

    Examples:
        >>> # d(x+y)/dx = 1 + 0 = 1
        >>> _diff_binary(Binary("+", VarRef("x"), VarRef("y")), "x", None)
        Binary("+", Const(1.0), Const(0.0))

        >>> # d(x*y)/dx = y*1 + x*0 = y
        >>> _diff_binary(Binary("*", VarRef("x"), VarRef("y")), "x", None)
        Binary("+", Binary("*", VarRef("y"), Const(1.0)), Binary("*", VarRef("x"), Const(0.0)))
    """
    op = expr.op

    if op == "+":
        # Sum rule: d(a+b)/dx = da/dx + db/dx
        left_deriv = differentiate_expr(expr.left, wrt_var, wrt_indices)
        right_deriv = differentiate_expr(expr.right, wrt_var, wrt_indices)
        return Binary("+", left_deriv, right_deriv)

    elif op == "-":
        # Difference rule: d(a-b)/dx = da/dx - db/dx
        left_deriv = differentiate_expr(expr.left, wrt_var, wrt_indices)
        right_deriv = differentiate_expr(expr.right, wrt_var, wrt_indices)
        return Binary("-", left_deriv, right_deriv)

    elif op == "*":
        # Product rule: d(a*b)/dx = b*(da/dx) + a*(db/dx)
        a = expr.left
        b = expr.right
        da_dx = differentiate_expr(a, wrt_var, wrt_indices)
        db_dx = differentiate_expr(b, wrt_var, wrt_indices)
        # b * da/dx
        term1 = Binary("*", b, da_dx)
        # a * db/dx
        term2 = Binary("*", a, db_dx)
        return Binary("+", term1, term2)

    elif op == "/":
        # Quotient rule: d(a/b)/dx = (b*(da/dx) - a*(db/dx))/b²
        a = expr.left
        b = expr.right
        da_dx = differentiate_expr(a, wrt_var, wrt_indices)
        db_dx = differentiate_expr(b, wrt_var, wrt_indices)
        # b * da/dx
        term1 = Binary("*", b, da_dx)
        # a * db/dx
        term2 = Binary("*", a, db_dx)
        # numerator: b*da/dx - a*db/dx
        numerator = Binary("-", term1, term2)
        # denominator: b²
        denominator = Binary("*", b, b)
        return Binary("/", numerator, denominator)

    else:
        raise ValueError(
            f"Unsupported binary operation '{op}' for differentiation. "
            f"Supported operations: +, -, *, /. "
            f"Power (^) will be implemented on Day 3."
        )


def _diff_unary(expr: Unary, wrt_var: str, wrt_indices: tuple[str, ...] | None = None) -> Expr:
    """
    Derivative of unary operations.

    Supports: +, -

    Mathematical rules:
    - Unary plus: d(+a)/dx = da/dx
    - Unary minus: d(-a)/dx = -da/dx

    Args:
        expr: Unary expression
        wrt_var: Variable to differentiate with respect to
        wrt_indices: Optional index tuple for specific variable instance

    Returns:
        Derivative expression (new AST)

    Raises:
        ValueError: If operation is not supported

    Examples:
        >>> # d(+x)/dx = dx/dx = 1
        >>> _diff_unary(Unary("+", VarRef("x")), "x", None)
        Const(1.0)

        >>> # d(-x)/dx = -dx/dx = -1
        >>> _diff_unary(Unary("-", VarRef("x")), "x", None)
        Unary("-", Const(1.0))
    """
    op = expr.op

    if op == "+":
        # Unary plus: d(+a)/dx = da/dx
        return differentiate_expr(expr.child, wrt_var, wrt_indices)

    elif op == "-":
        # Unary minus: d(-a)/dx = -da/dx
        child_deriv = differentiate_expr(expr.child, wrt_var, wrt_indices)
        return Unary("-", child_deriv)

    else:
        raise ValueError(
            f"Unsupported unary operation '{op}' for differentiation. Supported operations: +, -"
        )


# ============================================================================
# Day 3: Function Calls (Power, Exp, Log, Sqrt)
# ============================================================================


def _diff_call(expr: Call, wrt_var: str, wrt_indices: tuple[str, ...] | None = None) -> Expr:
    """
    Derivative of function calls using chain rule.

    Supports (Day 3): power, exp, log, sqrt
    Future (Day 4): sin, cos, tan

    General chain rule: d(f(g(x)))/dx = f'(g(x)) * dg/dx

    Args:
        expr: Call expression
        wrt_var: Variable to differentiate with respect to
        wrt_indices: Optional index tuple for specific variable instance

    Returns:
        Derivative expression (new AST)

    Raises:
        ValueError: If function is not supported

    Examples:
        >>> # d(exp(x))/dx = exp(x) * 1 = exp(x)
        >>> _diff_call(Call("exp", [VarRef("x")]), "x", None)
        Binary("*", Call("exp", [VarRef("x")]), Const(1.0))

        >>> # d(log(x))/dx = (1/x) * 1 = 1/x
        >>> _diff_call(Call("log", [VarRef("x")]), "x", None)
        Binary("*", Binary("/", Const(1.0), VarRef("x")), Const(1.0))
    """
    func = expr.func

    if func == "power":
        return _diff_power(expr, wrt_var, wrt_indices)
    elif func == "exp":
        return _diff_exp(expr, wrt_var, wrt_indices)
    elif func == "log":
        return _diff_log(expr, wrt_var, wrt_indices)
    elif func == "sqrt":
        return _diff_sqrt(expr, wrt_var, wrt_indices)
    elif func == "sin":
        return _diff_sin(expr, wrt_var, wrt_indices)
    elif func == "cos":
        return _diff_cos(expr, wrt_var, wrt_indices)
    elif func == "tan":
        return _diff_tan(expr, wrt_var, wrt_indices)
    elif func == "abs":
        # abs() is not differentiable everywhere (non-differentiable at x=0)
        raise ValueError(
            "abs() is not differentiable everywhere (undefined at x=0). "
            "For optimization problems, consider using smooth approximations. "
            "Planned feature: --smooth-abs flag to replace abs(x) with sqrt(x^2 + ε). "
            "See PROJECT_PLAN.md for details on smoothing techniques."
        )
    else:
        # Future: Other functions
        raise ValueError(
            f"Differentiation not yet implemented for function '{func}'. "
            f"Supported functions: power, exp, log, sqrt, sin, cos, tan. "
            f"Note: abs() is intentionally not supported (non-differentiable at x=0). "
            f"Use smooth approximations instead (planned feature)."
        )


def _diff_power(expr: Call, wrt_var: str, wrt_indices: tuple[str, ...] | None = None) -> Expr:
    """
    Derivative of power function: power(base, exponent).

    General formula: d(a^b)/dx = a^b * (b/a * da/dx + ln(a) * db/dx)

    Optimization: If exponent is constant, use simpler power rule:
    d(a^n)/dx = n * a^(n-1) * da/dx

    Args:
        expr: Call("power", [base, exponent])
        wrt_var: Variable to differentiate with respect to
        wrt_indices: Optional index tuple for specific variable instance

    Returns:
        Derivative expression (new AST)

    Examples:
        >>> # d(power(x, 2))/dx = 2 * x^1 * 1 = 2*x
        >>> _diff_power(Call("power", [VarRef("x"), Const(2.0)]), "x", None)
        Binary("*", Binary("*", Const(2.0), Call("power", [VarRef("x"), Const(1.0)])), Const(1.0))

        >>> # d(power(x, y))/dx uses general formula
        >>> _diff_power(Call("power", [VarRef("x"), VarRef("y")]), "x", None)
        # Returns: x^y * (y/x * 1 + ln(x) * 0)
    """
    if len(expr.args) != 2:
        raise ValueError(f"power() expects 2 arguments, got {len(expr.args)}")

    base = expr.args[0]
    exponent = expr.args[1]

    # Check if exponent is constant (optimization case)
    if isinstance(exponent, Const):
        # Power rule: d(a^n)/dx = n * a^(n-1) * da/dx
        n = exponent.value
        da_dx = differentiate_expr(base, wrt_var, wrt_indices)

        # n * a^(n-1)
        n_minus_1 = Const(n - 1.0)
        a_pow_n_minus_1 = Call("power", (base, n_minus_1))
        n_times_power = Binary("*", exponent, a_pow_n_minus_1)

        # (n * a^(n-1)) * da/dx
        return Binary("*", n_times_power, da_dx)

    else:
        # General case: d(a^b)/dx = a^b * (b/a * da/dx + ln(a) * db/dx)
        da_dx = differentiate_expr(base, wrt_var, wrt_indices)
        db_dx = differentiate_expr(exponent, wrt_var, wrt_indices)

        # a^b
        a_pow_b = Call("power", (base, exponent))

        # b/a
        b_over_a = Binary("/", exponent, base)

        # b/a * da/dx
        term1 = Binary("*", b_over_a, da_dx)

        # ln(a)
        ln_a = Call("log", (base,))

        # ln(a) * db/dx
        term2 = Binary("*", ln_a, db_dx)

        # b/a * da/dx + ln(a) * db/dx
        sum_terms = Binary("+", term1, term2)

        # a^b * (...)
        return Binary("*", a_pow_b, sum_terms)


def _diff_exp(expr: Call, wrt_var: str, wrt_indices: tuple[str, ...] | None = None) -> Expr:
    """
    Derivative of exponential function: exp(x).

    Formula: d(exp(a))/dx = exp(a) * da/dx

    Args:
        expr: Call("exp", [arg])
        wrt_var: Variable to differentiate with respect to
        wrt_indices: Optional index tuple for specific variable instance

    Returns:
        Derivative expression (new AST)

    Example:
        >>> # d(exp(x))/dx = exp(x) * 1 = exp(x)
        >>> _diff_exp(Call("exp", [VarRef("x")]), "x", None)
        Binary("*", Call("exp", [VarRef("x")]), Const(1.0))

        >>> # d(exp(x^2))/dx = exp(x^2) * 2x (chain rule)
        >>> _diff_exp(Call("exp", [Call("power", [VarRef("x"), Const(2.0)])]), "x", None)
        # Returns: exp(x^2) * d(x^2)/dx
    """
    if len(expr.args) != 1:
        raise ValueError(f"exp() expects 1 argument, got {len(expr.args)}")

    arg = expr.args[0]
    darg_dx = differentiate_expr(arg, wrt_var, wrt_indices)

    # exp(arg) * darg/dx
    return Binary("*", Call("exp", (arg,)), darg_dx)


def _diff_log(expr: Call, wrt_var: str, wrt_indices: tuple[str, ...] | None = None) -> Expr:
    """
    Derivative of natural logarithm: log(x).

    Formula: d(log(a))/dx = (1/a) * da/dx

    Args:
        expr: Call("log", [arg])
        wrt_var: Variable to differentiate with respect to
        wrt_indices: Optional index tuple for specific variable instance

    Returns:
        Derivative expression (new AST)

    Example:
        >>> # d(log(x))/dx = (1/x) * 1 = 1/x
        >>> _diff_log(Call("log", [VarRef("x")]), "x", None)
        Binary("*", Binary("/", Const(1.0), VarRef("x")), Const(1.0))

        >>> # d(log(x^2))/dx = (1/(x^2)) * 2x (chain rule)
        >>> _diff_log(Call("log", [Call("power", [VarRef("x"), Const(2.0)])]), "x", None)
        # Returns: (1/(x^2)) * d(x^2)/dx
    """
    if len(expr.args) != 1:
        raise ValueError(f"log() expects 1 argument, got {len(expr.args)}")

    arg = expr.args[0]
    darg_dx = differentiate_expr(arg, wrt_var, wrt_indices)

    # 1/arg
    one_over_arg = Binary("/", Const(1.0), arg)

    # (1/arg) * darg/dx
    return Binary("*", one_over_arg, darg_dx)


def _diff_sqrt(expr: Call, wrt_var: str, wrt_indices: tuple[str, ...] | None = None) -> Expr:
    """
    Derivative of square root: sqrt(x).

    Formula: d(sqrt(a))/dx = (1/(2*sqrt(a))) * da/dx
    Alternative: sqrt(x) = x^(1/2), so d/dx = (1/2)*x^(-1/2) = 1/(2*sqrt(x))

    Args:
        expr: Call("sqrt", [arg])
        wrt_var: Variable to differentiate with respect to
        wrt_indices: Optional index tuple for specific variable instance

    Returns:
        Derivative expression (new AST)

    Example:
        >>> # d(sqrt(x))/dx = 1/(2*sqrt(x)) * 1 = 1/(2*sqrt(x))
        >>> _diff_sqrt(Call("sqrt", [VarRef("x")]), "x", None)
        Binary("*", Binary("/", Const(1.0), Binary("*", Const(2.0), Call("sqrt", [VarRef("x")]))), Const(1.0))

        >>> # d(sqrt(x^2))/dx = (1/(2*sqrt(x^2))) * 2x (chain rule)
        >>> _diff_sqrt(Call("sqrt", [Call("power", [VarRef("x"), Const(2.0)])]), "x", None)
        # Returns: (1/(2*sqrt(x^2))) * d(x^2)/dx
    """
    if len(expr.args) != 1:
        raise ValueError(f"sqrt() expects 1 argument, got {len(expr.args)}")

    arg = expr.args[0]
    darg_dx = differentiate_expr(arg, wrt_var, wrt_indices)

    # sqrt(arg)
    sqrt_arg = Call("sqrt", (arg,))

    # 2 * sqrt(arg)
    two_sqrt_arg = Binary("*", Const(2.0), sqrt_arg)

    # 1 / (2 * sqrt(arg))
    one_over_two_sqrt = Binary("/", Const(1.0), two_sqrt_arg)

    # (1/(2*sqrt(arg))) * darg/dx
    return Binary("*", one_over_two_sqrt, darg_dx)


# ============================================================================
# Day 4: Trigonometric Functions
# ============================================================================


def _diff_sin(expr: Call, wrt_var: str, wrt_indices: tuple[str, ...] | None = None) -> Expr:
    """
    Derivative of sine function: sin(x).

    Formula: d(sin(a))/dx = cos(a) * da/dx

    Args:
        expr: Call("sin", [arg])
        wrt_var: Variable to differentiate with respect to
        wrt_indices: Optional index tuple for specific variable instance

    Returns:
        Derivative expression (new AST)

    Example:
        >>> # d(sin(x))/dx = cos(x) * 1 = cos(x)
        >>> _diff_sin(Call("sin", (VarRef("x"),)), "x", None)
        Binary("*", Call("cos", (VarRef("x"),)), Const(1.0))

        >>> # d(sin(x^2))/dx = cos(x^2) * 2x (chain rule)
        >>> _diff_sin(Call("sin", (Call("power", (VarRef("x"), Const(2.0))),)), "x", None)
        # Returns: cos(x^2) * d(x^2)/dx
    """
    if len(expr.args) != 1:
        raise ValueError(f"sin() expects 1 argument, got {len(expr.args)}")

    arg = expr.args[0]
    darg_dx = differentiate_expr(arg, wrt_var, wrt_indices)

    # cos(arg) * darg/dx
    return Binary("*", Call("cos", (arg,)), darg_dx)


def _diff_cos(expr: Call, wrt_var: str, wrt_indices: tuple[str, ...] | None = None) -> Expr:
    """
    Derivative of cosine function: cos(x).

    Formula: d(cos(a))/dx = -sin(a) * da/dx

    Args:
        expr: Call("cos", [arg])
        wrt_var: Variable to differentiate with respect to
        wrt_indices: Optional index tuple for specific variable instance

    Returns:
        Derivative expression (new AST)

    Example:
        >>> # d(cos(x))/dx = -sin(x) * 1 = -sin(x)
        >>> _diff_cos(Call("cos", (VarRef("x"),)), "x", None)
        Binary("*", Unary("-", Call("sin", (VarRef("x"),))), Const(1.0))

        >>> # d(cos(x^2))/dx = -sin(x^2) * 2x (chain rule)
        >>> _diff_cos(Call("cos", (Call("power", (VarRef("x"), Const(2.0))),)), "x", None)
        # Returns: -sin(x^2) * d(x^2)/dx
    """
    if len(expr.args) != 1:
        raise ValueError(f"cos() expects 1 argument, got {len(expr.args)}")

    arg = expr.args[0]
    darg_dx = differentiate_expr(arg, wrt_var, wrt_indices)

    # -sin(arg)
    neg_sin_arg = Unary("-", Call("sin", (arg,)))

    # -sin(arg) * darg/dx
    return Binary("*", neg_sin_arg, darg_dx)


def _diff_tan(expr: Call, wrt_var: str, wrt_indices: tuple[str, ...] | None = None) -> Expr:
    """
    Derivative of tangent function: tan(x).

    Formula: d(tan(a))/dx = sec²(a) * da/dx = (1/cos²(a)) * da/dx

    Note: tan(x) has poles (undefined values) at x = π/2 + nπ where n is any integer.
    The derivative is also undefined at these points. This implementation does not
    check for these domain issues at differentiation time - they will surface during
    evaluation if the input violates the domain.

    Args:
        expr: Call("tan", [arg])
        wrt_var: Variable to differentiate with respect to
        wrt_indices: Optional index tuple for specific variable instance

    Returns:
        Derivative expression (new AST)

    Example:
        >>> # d(tan(x))/dx = (1/cos²(x)) * 1 = 1/cos²(x)
        >>> _diff_tan(Call("tan", (VarRef("x"),)), "x", None)
        Binary("*", Binary("/", Const(1.0), Binary("*", Call("cos", (VarRef("x"),)), Call("cos", (VarRef("x"),)))), Const(1.0))

        >>> # d(tan(x^2))/dx = (1/cos²(x^2)) * 2x (chain rule)
        >>> _diff_tan(Call("tan", (Call("power", (VarRef("x"), Const(2.0))),)), "x", None)
        # Returns: (1/cos²(x^2)) * d(x^2)/dx
    """
    if len(expr.args) != 1:
        raise ValueError(f"tan() expects 1 argument, got {len(expr.args)}")

    arg = expr.args[0]
    darg_dx = differentiate_expr(arg, wrt_var, wrt_indices)

    # cos(arg)
    cos_arg = Call("cos", (arg,))

    # cos²(arg) = cos(arg) * cos(arg)
    cos_squared = Binary("*", cos_arg, cos_arg)

    # 1 / cos²(arg) = sec²(arg)
    sec_squared = Binary("/", Const(1.0), cos_squared)

    # sec²(arg) * darg/dx
    return Binary("*", sec_squared, darg_dx)


# ============================================================================
# Day 5: Sum Aggregations
# ============================================================================


def _diff_sum(expr: Sum, wrt_var: str, wrt_indices: tuple[str, ...] | None = None) -> Expr:
    """
    Derivative of sum aggregation: sum(indices, body_expr).

    Mathematical rule (linearity of differentiation):
    d/dx sum(i, f(x,i)) = sum(i, df(x,i)/dx)

    The derivative of a sum is the sum of the derivatives.

    Strategy:
    1. Differentiate the body expression with respect to wrt_var (and wrt_indices if provided)
    2. Wrap the derivative in a new Sum with the same index variables
    3. The Sum structure is preserved in the derivative

    Index-aware differentiation:
    - When wrt_indices is None: Matches all indexed instances (backward compatible)
    - When wrt_indices is provided: Only matches exact index tuple
    - Example: d/dx(i1) sum(i, x(i))
      - Each x(i) is tested for exact match with wrt_indices
      - Only x(i1) contributes 1, others contribute 0
      - Result: sum(i, [1 if i==i1 else 0])

    Args:
        expr: Sum expression with index_sets (tuple of index names) and body (expression)
        wrt_var: Variable to differentiate with respect to
        wrt_indices: Optional index tuple for specific variable instance

    Returns:
        Sum expression with differentiated body and same index sets

    Examples:
        >>> # d/dx sum(i, x(i)) = sum(i, 1) (backward compatible, no indices specified)
        >>> expr = Sum(("i",), VarRef("x", ("i",)))
        >>> result = _diff_sum(expr, "x", None)
        >>> # result is Sum(("i",), Const(1.0))

        >>> # d/dx sum(i, x(i)^2) = sum(i, 2*x(i))
        >>> expr = Sum(("i",), Call("power", (VarRef("x", ("i",)), Const(2.0))))
        >>> result = _diff_sum(expr, "x", None)
        >>> # result is Sum(("i",), Binary("*", Const(2.0), ...))

        >>> # d/dx sum(i, c*x(i)) where c is a parameter = sum(i, c*1) = sum(i, c)
        >>> expr = Sum(("i",), Binary("*", ParamRef("c"), VarRef("x", ("i",))))
        >>> result = _diff_sum(expr, "x", None)
        >>> # result is Sum(("i",), Binary("*", ParamRef("c"), Const(1.0)))
    """
    # Differentiate the body expression, passing wrt_indices through
    body_derivative = differentiate_expr(expr.body, wrt_var, wrt_indices)

    # Return a new Sum with the same index sets and the differentiated body
    return Sum(expr.index_sets, body_derivative)
