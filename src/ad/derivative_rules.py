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

from ..ir.ast import Const, ParamRef, SymbolRef, VarRef


def differentiate_expr(expr: Expr, wrt_var: str) -> Expr:
    """
    Main dispatcher for symbolic differentiation.

    Routes to the appropriate differentiation rule based on expression type.

    Args:
        expr: Expression to differentiate
        wrt_var: Variable to differentiate with respect to

    Returns:
        Derivative expression (new AST)

    Raises:
        TypeError: If expression type is not supported (yet)
    """
    # Day 1: Constants and variable references
    if isinstance(expr, Const):
        return _diff_const(expr, wrt_var)
    elif isinstance(expr, VarRef):
        return _diff_varref(expr, wrt_var)
    elif isinstance(expr, SymbolRef):
        return _diff_symbolref(expr, wrt_var)
    elif isinstance(expr, ParamRef):
        return _diff_paramref(expr, wrt_var)

    # Day 2+: Other node types (to be implemented)
    # elif isinstance(expr, Binary):
    #     return _diff_binary(expr, wrt_var)
    # elif isinstance(expr, Unary):
    #     return _diff_unary(expr, wrt_var)
    # elif isinstance(expr, Call):
    #     return _diff_call(expr, wrt_var)
    # elif isinstance(expr, Sum):
    #     return _diff_sum(expr, wrt_var)

    raise TypeError(
        f"Differentiation not yet implemented for {type(expr).__name__}. "
        f"This will be added in subsequent days of Sprint 2."
    )


# ============================================================================
# Day 1: Basic Derivative Rules
# ============================================================================


def _diff_const(_expr: Const, _wrt_var: str) -> Const:
    """
    Derivative of a constant.

    Mathematical rule: d(c)/dx = 0

    Args:
        _expr: Constant expression (unused, derivative is always zero)
        _wrt_var: Variable name (unused, derivative is always zero)

    Returns:
        Const(0.0)

    Example:
        >>> _diff_const(Const(5.0), "x")
        Const(0.0)
    """
    return Const(0.0)


def _diff_varref(expr: VarRef, wrt_var: str) -> Const:
    """
    Derivative of a variable reference.

    Mathematical rules:
    - d(x)/dx = 1   (same variable)
    - d(y)/dx = 0   (different variable)

    For indexed variables, we compare the base variable name.
    Index matching will be handled in Day 5-6 for proper sparsity.

    Args:
        expr: Variable reference
        wrt_var: Variable name to differentiate with respect to

    Returns:
        Const(1.0) if same variable name, Const(0.0) otherwise

    Examples:
        >>> _diff_varref(VarRef("x"), "x")
        Const(1.0)
        >>> _diff_varref(VarRef("y"), "x")
        Const(0.0)
        >>> _diff_varref(VarRef("x", ("i",)), "x")  # Indexed, same var
        Const(1.0)
        >>> _diff_varref(VarRef("y", ("i",)), "x")  # Indexed, different var
        Const(0.0)

    Note:
        Full index-aware differentiation (distinguishing x(i) from x(j))
        will be implemented in Days 5-6 when we handle Sum aggregations.
    """
    if expr.name == wrt_var:
        return Const(1.0)
    else:
        return Const(0.0)


def _diff_symbolref(expr: SymbolRef, wrt_var: str) -> Const:
    """
    Derivative of a scalar symbol reference.

    Mathematical rules:
    - d(x)/dx = 1   (same variable)
    - d(y)/dx = 0   (different variable)

    Args:
        expr: Symbol reference
        wrt_var: Variable name to differentiate with respect to

    Returns:
        Const(1.0) if same variable name, Const(0.0) otherwise

    Examples:
        >>> _diff_symbolref(SymbolRef("x"), "x")
        Const(1.0)
        >>> _diff_symbolref(SymbolRef("y"), "x")
        Const(0.0)
    """
    if expr.name == wrt_var:
        return Const(1.0)
    else:
        return Const(0.0)


def _diff_paramref(_expr: ParamRef, _wrt_var: str) -> Const:
    """
    Derivative of a parameter reference.

    Mathematical rule: d(param)/dx = 0

    Parameters are constant with respect to variables in the NLP.

    Args:
        _expr: Parameter reference (unused, derivative is always zero)
        _wrt_var: Variable name (unused, derivative is always zero)

    Returns:
        Const(0.0)

    Example:
        >>> _diff_paramref(ParamRef("c"), "x")
        Const(0.0)
        >>> _diff_paramref(ParamRef("demand", ("i",)), "x")
        Const(0.0)
    """
    return Const(0.0)


# ============================================================================
# Day 2+: Additional Rules (Placeholders)
# ============================================================================

# def _diff_binary(expr: Binary, wrt_var: str) -> Expr:
#     """Derivative of binary operations (+, -, *, /, ^)"""
#     # To be implemented on Day 2
#     pass

# def _diff_unary(expr: Unary, wrt_var: str) -> Expr:
#     """Derivative of unary operations (+, -)"""
#     # To be implemented on Day 2
#     pass

# def _diff_call(expr: Call, wrt_var: str) -> Expr:
#     """Derivative of function calls (exp, log, sin, etc.)"""
#     # To be implemented on Days 3-4
#     pass

# def _diff_sum(expr: Sum, wrt_var: str) -> Expr:
#     """Derivative of sum aggregations"""
#     # To be implemented on Day 5
#     pass
