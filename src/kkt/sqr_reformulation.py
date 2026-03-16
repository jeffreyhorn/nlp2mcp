"""Reformulate sqr(expr) = 0 equality constraints to expr = 0.

Issue #1071: Equality constraints of the form `c * sqr(expr) = 0` cause
LICQ violations because the gradient vanishes at the feasible point.
Reformulating to `expr = 0` preserves feasibility and restores full-rank
constraint Jacobians.

This must be called BEFORE derivative computation so the Jacobian
reflects the simplified form.
"""

from __future__ import annotations

import logging

from src.ir.ast import Binary, Call, Const, Expr
from src.ir.model_ir import ModelIR
from src.ir.symbols import EquationDef, Rel

logger = logging.getLogger(__name__)


def _extract_sqr_inner(expr: Expr) -> Expr | None:
    """Extract the inner expression from sqr(expr) or c*sqr(expr).

    Returns the inner expression if the top-level structure is:
      - Call("sqr", (inner,))
      - Binary("*", Const, Call("sqr", (inner,)))
      - Binary("*", Call("sqr", (inner,)), Const)

    Returns None if the expression doesn't match.
    """
    # Direct sqr(expr)
    if isinstance(expr, Call) and expr.func == "sqr" and len(expr.args) == 1:
        return expr.args[0]

    # c * sqr(expr) or sqr(expr) * c
    if isinstance(expr, Binary) and expr.op == "*":
        if isinstance(expr.right, Call) and expr.right.func == "sqr" and len(expr.right.args) == 1:
            return expr.right.args[0]
        if isinstance(expr.left, Call) and expr.left.func == "sqr" and len(expr.left.args) == 1:
            return expr.left.args[0]

    return None


def _is_zero(expr: Expr) -> bool:
    """Check if an expression is the constant 0."""
    return isinstance(expr, Const) and expr.value == 0


def reformulate_sqr_equalities(model_ir: ModelIR) -> list[str]:
    """Reformulate sqr(expr) =E= 0 constraints to expr =E= 0.

    Modifies model_ir equations in-place. Only processes equality
    constraints where the RHS is zero.

    Args:
        model_ir: Model IR to modify in-place.

    Returns:
        List of equation names that were reformulated.
    """
    reformulated: list[str] = []

    for eq_name in list(model_ir.equations):
        eq_def = model_ir.equations[eq_name]

        # Only process equalities
        if eq_def.relation != Rel.EQ:
            continue

        lhs, rhs = eq_def.lhs_rhs

        # Check: LHS is sqr-pattern and RHS is 0
        inner = _extract_sqr_inner(lhs)
        if inner is not None and _is_zero(rhs):
            model_ir.equations[eq_name] = EquationDef(
                name=eq_def.name,
                domain=eq_def.domain,
                relation=Rel.EQ,
                lhs_rhs=(inner, Const(0.0)),
                condition=eq_def.condition,
                source_location=eq_def.source_location,
                has_head_domain_offset=eq_def.has_head_domain_offset,
            )
            reformulated.append(eq_name)
            logger.info(
                "Issue #1071: Reformulated sqr equality %s: "
                "sqr(expr) =E= 0 -> expr =E= 0 (LICQ fix)",
                eq_name,
            )
            continue

        # Check reversed: LHS is 0 and RHS is sqr-pattern
        inner = _extract_sqr_inner(rhs)
        if inner is not None and _is_zero(lhs):
            model_ir.equations[eq_name] = EquationDef(
                name=eq_def.name,
                domain=eq_def.domain,
                relation=Rel.EQ,
                lhs_rhs=(Const(0.0), inner),
                condition=eq_def.condition,
                source_location=eq_def.source_location,
                has_head_domain_offset=eq_def.has_head_domain_offset,
            )
            reformulated.append(eq_name)
            logger.info(
                "Issue #1071: Reformulated sqr equality %s: "
                "0 =E= sqr(expr) -> 0 =E= expr (LICQ fix)",
                eq_name,
            )

    return reformulated
