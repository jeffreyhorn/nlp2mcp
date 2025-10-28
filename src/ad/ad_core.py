"""
Symbolic Automatic Differentiation Core

This module implements symbolic differentiation (AST → AST transformations)
for computing derivatives of GAMS NLP expressions.

Design Philosophy:
-----------------
We use symbolic differentiation rather than adjoint-style reverse-mode AD because:

1. **Transparency**: Derivative expressions remain as AST nodes that can be
   inspected, simplified, and manipulated before evaluation.

2. **Flexibility**: We can generate GAMS code directly from derivative ASTs
   without needing to evaluate them numerically first.

3. **Simplicity**: For our use case (generating KKT conditions), we need
   symbolic Jacobian entries, not just numerical values.

4. **Debugging**: Symbolic derivatives can be pretty-printed and verified
   against mathematical expectations before any numerical evaluation.

The trade-off is that symbolic differentiation can produce larger expression
trees than strictly necessary, but this is acceptable for our problem sizes
and allows for better debugging and code generation.

Approach:
--------
- differentiate(expr, wrt_var) → new AST representing d(expr)/d(wrt_var)
- Each AST node type has a differentiation rule
- Chain rule applied recursively through expression tree
- Result is always a new AST (never modifies input)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..ir.ast import Expr


def differentiate(expr: Expr, wrt_var: str) -> Expr:
    """
    Compute the symbolic derivative of an expression with respect to a variable.

    Args:
        expr: The expression to differentiate (AST node)
        wrt_var: The variable name to differentiate with respect to
                 (e.g., "x" for scalar, or base name for indexed vars)

    Returns:
        A new AST representing the derivative d(expr)/d(wrt_var)

    Examples:
        >>> from src.ir.ast import Const, VarRef
        >>> differentiate(Const(5.0), "x")  # d(5)/dx = 0
        Const(0.0)
        >>> differentiate(VarRef("x"), "x")  # dx/dx = 1
        Const(1.0)
        >>> differentiate(VarRef("y"), "x")  # dy/dx = 0
        Const(0.0)

    Note:
        This is the main entry point for symbolic differentiation.
        Specific rules are delegated to derivative_rules module.
    """
    from . import derivative_rules

    return derivative_rules.differentiate_expr(expr, wrt_var)


def simplify(expr: Expr) -> Expr:
    """
    Simplify a symbolic expression (basic algebraic simplifications).

    This is a placeholder for future optimization. Currently returns expr unchanged.

    Args:
        expr: The expression to simplify

    Returns:
        A simplified version of the expression

    Future improvements:
        - Constant folding: Const(2) + Const(3) → Const(5)
        - Identity elimination: x + 0 → x, x * 1 → x
        - Zero multiplication: x * 0 → 0
        - Algebraic simplification: (x + y) - y → x
    """
    # TODO: Implement simplification in future sprint if needed
    return expr
