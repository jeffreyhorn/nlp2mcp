"""LP-specific coefficient extraction for linear expressions.

For LP models, all equation bodies are linear in the variables, so all
partial derivatives are constants (coefficients). Instead of full symbolic
differentiation, we extract coefficients directly from the expression tree
in a single pass. This is O(n) in the expression size, avoiding the
intermediate AST construction and simplification overhead.
"""

from __future__ import annotations

from ..ir.ast import (
    Binary,
    Call,
    Const,
    DollarConditional,
    Expr,
    IndexOffset,
    ParamRef,
    Prod,
    Sum,
    Unary,
    VarRef,
)


def extract_linear_coefficient(
    expr: Expr,
    wrt_var: str,
    wrt_indices: tuple[str | IndexOffset, ...] | None = None,
) -> Expr:
    """Extract the coefficient of a variable in a linear expression.

    For a linear expression like ``a*x(i) + b*y(j) + c``, this returns
    the coefficient of ``wrt_var(wrt_indices)``. For example, extracting
    the coefficient of ``x(i)`` returns ``a``.

    This is equivalent to ``differentiate_expr(expr, wrt_var, wrt_indices)``
    for linear expressions, but much faster since it avoids full symbolic
    differentiation and simplification.

    Returns:
        The coefficient expression (a constant or parameter expression),
        or ``Const(0.0)`` if the variable does not appear.
    """
    return _extract(expr, wrt_var, wrt_indices)


def _var_matches(ref: VarRef, wrt_var: str, wrt_indices: tuple | None) -> bool:
    """Check if a VarRef matches the target variable and indices."""
    if ref.name.lower() != wrt_var.lower():
        return False
    if wrt_indices is None:
        return len(ref.indices) == 0
    if len(ref.indices) != len(wrt_indices):
        return False
    for ri, wi in zip(ref.indices, wrt_indices, strict=True):
        ri_str = str(ri).lower() if not isinstance(ri, str) else ri.lower()
        wi_str = str(wi).lower() if not isinstance(wi, str) else wi.lower()
        if ri_str != wi_str:
            return False
    return True


def _expr_has_var(expr: Expr, wrt_var: str) -> bool:
    """Quick check if expression references the target variable at all."""
    if isinstance(expr, VarRef):
        return expr.name.lower() == wrt_var.lower()
    if isinstance(expr, (Const, ParamRef)):
        return False
    if isinstance(expr, Binary):
        return _expr_has_var(expr.left, wrt_var) or _expr_has_var(expr.right, wrt_var)
    if isinstance(expr, Unary):
        return _expr_has_var(expr.child, wrt_var)
    if isinstance(expr, Sum):
        return _expr_has_var(expr.body, wrt_var)
    if isinstance(expr, Prod):
        return _expr_has_var(expr.body, wrt_var)
    if isinstance(expr, DollarConditional):
        return _expr_has_var(expr.value_expr, wrt_var)
    if isinstance(expr, Call):
        return any(_expr_has_var(a, wrt_var) for a in expr.args)
    # For unknown types, be conservative
    return True


_ZERO = Const(0.0)
_ONE = Const(1.0)


def _extract(
    expr: Expr,
    wrt_var: str,
    wrt_indices: tuple | None,
) -> Expr:
    """Recursively extract the coefficient of wrt_var in a linear expression."""
    # Constants and parameters have zero coefficient
    if isinstance(expr, (Const, ParamRef)):
        return _ZERO

    # Variable reference: coefficient is 1 if it matches, 0 otherwise
    if isinstance(expr, VarRef):
        return _ONE if _var_matches(expr, wrt_var, wrt_indices) else _ZERO

    # Unary negation: -f → -coeff(f)
    if isinstance(expr, Unary) and expr.op == "-":
        inner = _extract(expr.child, wrt_var, wrt_indices)
        if isinstance(inner, Const) and inner.value == 0.0:
            return _ZERO
        return Unary("-", inner)

    # Binary operations
    if isinstance(expr, Binary):
        if expr.op in ("+", "-"):
            left = _extract(expr.left, wrt_var, wrt_indices)
            right = _extract(expr.right, wrt_var, wrt_indices)
            l_zero = isinstance(left, Const) and left.value == 0.0
            r_zero = isinstance(right, Const) and right.value == 0.0
            if l_zero and r_zero:
                return _ZERO
            if l_zero:
                return right if expr.op == "+" else Unary("-", right)
            if r_zero:
                return left
            return Binary(expr.op, left, right)

        if expr.op == "*":
            # For linear expr, at most one side has the variable
            l_has = _expr_has_var(expr.left, wrt_var)
            r_has = _expr_has_var(expr.right, wrt_var)
            if not l_has and not r_has:
                return _ZERO
            if l_has and not r_has:
                # d(f*c)/dx = c * df/dx
                coeff = _extract(expr.left, wrt_var, wrt_indices)
                if isinstance(coeff, Const) and coeff.value == 0.0:
                    return _ZERO
                if isinstance(coeff, Const) and coeff.value == 1.0:
                    return expr.right
                return Binary("*", expr.right, coeff)
            if r_has and not l_has:
                # d(c*f)/dx = c * df/dx
                coeff = _extract(expr.right, wrt_var, wrt_indices)
                if isinstance(coeff, Const) and coeff.value == 0.0:
                    return _ZERO
                if isinstance(coeff, Const) and coeff.value == 1.0:
                    return expr.left
                return Binary("*", expr.left, coeff)
            # Both sides have the variable — not linear, fall through
            return _ZERO

        if expr.op == "/":
            # For linear: f/c where c is constant
            if not _expr_has_var(expr.left, wrt_var):
                return _ZERO
            if _expr_has_var(expr.right, wrt_var):
                return _ZERO  # Not linear
            coeff = _extract(expr.left, wrt_var, wrt_indices)
            if isinstance(coeff, Const) and coeff.value == 0.0:
                return _ZERO
            return Binary("/", coeff, expr.right)

        # Other ops (**, etc.) — if variable is involved, not linear
        return _ZERO

    # Sum: sum(i, body) → sum(i, coeff(body))
    if isinstance(expr, Sum):
        if not _expr_has_var(expr.body, wrt_var):
            return _ZERO
        body_coeff = _extract(expr.body, wrt_var, wrt_indices)
        if isinstance(body_coeff, Const) and body_coeff.value == 0.0:
            return _ZERO
        return Sum(
            index_sets=expr.index_sets,
            body=body_coeff,
            condition=expr.condition,
        )

    # Prod: product of terms — linear only if exactly one factor has the var
    if isinstance(expr, Prod):
        if not _expr_has_var(expr.body, wrt_var):
            return _ZERO
        # Prod is rare in LP; fall back to zero for safety
        return _ZERO

    # DollarConditional: body$cond → coeff(body)$cond
    if isinstance(expr, DollarConditional):
        if not _expr_has_var(expr.value_expr, wrt_var):
            return _ZERO
        body_coeff = _extract(expr.value_expr, wrt_var, wrt_indices)
        if isinstance(body_coeff, Const) and body_coeff.value == 0.0:
            return _ZERO
        return DollarConditional(value_expr=body_coeff, condition=expr.condition)

    # Function calls (e.g., abs, sqrt) — if var is inside, not linear
    if isinstance(expr, (Unary, Call)):
        return _ZERO

    # Unknown expression type — conservatively return zero
    return _ZERO
