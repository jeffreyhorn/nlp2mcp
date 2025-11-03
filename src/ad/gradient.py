"""
Objective Gradient Computation

This module computes the gradient of the objective function with respect to all variables.

Day 7 Scope:
-----------
- Retrieve objective expression from ObjectiveIR
- Handle both explicit expr and objvar-defined-by-equation cases
- Differentiate objective w.r.t. all variables
- Handle min/max objective sense
- Store in GradientVector structure

Mathematical Background:
-----------------------
For objective function f(x):
- Gradient: ∇f = [∂f/∂x₁, ∂f/∂x₂, ..., ∂f/∂xₙ]
- Minimization: min f(x) → use ∇f as-is
- Maximization: max f(x) = min -f(x) → use -∇f

Objective Expression Retrieval:
-------------------------------
1. If ObjectiveIR.expr is not None: Use directly
2. If ObjectiveIR.expr is None: Find defining equation
   - Look for equation that defines ObjectiveIR.objvar
   - Equation form: objvar =e= expression
   - Extract expression from RHS (or LHS if RHS is objvar)
3. If no defining equation found: Raise error

Index-Aware Differentiation (Implemented):
------------------------------------------
The gradient computation uses index-aware differentiation to properly
distinguish between scalar and indexed variable instances. This ensures
correct sparse Jacobian construction for optimization models.

Key Semantics:
- d/dx x = 1        (scalar matches scalar)
- d/dx x(i) = 0     (indexed doesn't match scalar)
- d/dx(i) x = 0     (scalar doesn't match indexed)
- d/dx(i) x(i) = 1  (exact index match)

Example: For objective sum(i, x(i)^2) where i ∈ {i1, i2}:
- ∂f/∂x(i1) = 2*x(i1)  (only the i1 term contributes)
- ∂f/∂x(i2) = 2*x(i2)  (only the i2 term contributes)
- ∂f/∂x = 0            (scalar x doesn't match any x(i))

Implementation:
1. enumerate_variable_instances() identifies all variable instances:
   - Scalar variables: (var_name, ())
   - Indexed variables: (var_name, (i1,)), (var_name, (i2,)), etc.

2. For each instance, differentiate_expr() is called with wrt_indices:
   derivative = differentiate_expr(obj_expr, var_name, indices)

3. The differentiation engine (src/ad/derivative_rules.py) matches VarRef nodes
   based on both name and exact index tuple, ensuring each variable instance
   has its own distinct derivative.

Backward Compatibility:
- When wrt_indices=None (default), differentiates w.r.t. scalar variable
- Existing code without indexed variables continues to work unchanged
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..config import Config
    from ..ir.ast import Expr
    from ..ir.model_ir import ModelIR

from ..ir.ast import Unary
from ..ir.symbols import ObjSense
from .ad_core import apply_simplification, get_simplification_mode
from .derivative_rules import differentiate_expr
from .index_mapping import build_index_mapping, enumerate_variable_instances
from .jacobian import GradientVector


def find_objective_expression(model_ir: ModelIR) -> Expr:
    """
    Find the objective function expression from ModelIR.

    Strategy:
    1. If ObjectiveIR.expr is set: Use it directly
    2. If ObjectiveIR.expr is None: Find defining equation
       - Look for equation that defines ObjectiveIR.objvar
       - Extract expression from equation

    Args:
        model_ir: Model IR containing objective and equations

    Returns:
        Objective function expression (AST)

    Raises:
        ValueError: If objective not found or objvar not defined

    Examples:
        >>> # Explicit expression
        >>> model_ir.objective = ObjectiveIR(ObjSense.MIN, "obj", expr=Binary("+", ...))
        >>> find_objective_expression(model_ir)  # Returns the Binary(...) expr

        >>> # Objvar defined by equation
        >>> model_ir.objective = ObjectiveIR(ObjSense.MIN, "obj", expr=None)
        >>> model_ir.equations["obj_def"] = EquationDef("obj_def", (), Rel.EQ, (SymbolRef("obj"), expr))
        >>> find_objective_expression(model_ir)  # Returns expr from equation RHS
    """
    if model_ir.objective is None:
        raise ValueError("ModelIR has no objective defined")

    objective = model_ir.objective

    # Case 1: Explicit expression
    if objective.expr is not None:
        return objective.expr

    # Case 2: Find defining equation
    objvar = objective.objvar

    # Search through equations for one that defines objvar
    for _eq_name, eq_def in model_ir.equations.items():
        # Skip indexed equations (objective must be scalar)
        if eq_def.domain:
            continue

        # Check if this equation defines the objective variable
        # Equation form: lhs =e= rhs
        lhs, rhs = eq_def.lhs_rhs

        # Check if lhs is the objvar (then use rhs as expression)
        if _is_symbol_ref(lhs, objvar):
            return rhs

        # Check if rhs is the objvar (then use lhs as expression)
        if _is_symbol_ref(rhs, objvar):
            return lhs

    # No defining equation found
    raise ValueError(
        f"Objective variable '{objvar}' is not defined by any equation. "
        f"ObjectiveIR.expr is None and no defining equation found. "
        f"Available equations: {list(model_ir.equations.keys())}"
    )


def _is_symbol_ref(expr: Expr, name: str) -> bool:
    """
    Check if expression is a SymbolRef with given name.

    Args:
        expr: Expression to check
        name: Symbol name to match

    Returns:
        True if expr is SymbolRef(name)
    """
    from ..ir.ast import SymbolRef

    return isinstance(expr, SymbolRef) and expr.name == name


def compute_objective_gradient(model_ir: ModelIR, config: Config | None = None) -> GradientVector:
    """
    Compute gradient of objective function with respect to all variables.

    Steps:
    1. Find objective expression (handle both explicit and objvar cases)
    2. Build index mapping to enumerate all variable instances
    3. Differentiate objective w.r.t. each variable instance
    4. Apply objective sense (negate for maximization)
    5. Store in GradientVector

    Args:
        model_ir: Model IR with objective, variables, and equations

    Returns:
        GradientVector with gradient components for all variables

    Raises:
        ValueError: If objective not found or objvar not defined

    Examples:
        >>> # min x^2 + y^2
        >>> gradient = compute_objective_gradient(model_ir)
        >>> gradient.get_derivative_by_name("x")  # Returns: 2*x
        >>> gradient.get_derivative_by_name("y")  # Returns: 2*y

        >>> # max x + y (converted to min -(x+y))
        >>> gradient = compute_objective_gradient(model_ir)
        >>> gradient.get_derivative_by_name("x")  # Returns: -1
        >>> gradient.get_derivative_by_name("y")  # Returns: -1
    """
    # Find objective expression
    obj_expr = find_objective_expression(model_ir)

    # Build index mapping for all variables
    index_mapping = build_index_mapping(model_ir)

    # Create gradient vector
    gradient = GradientVector(index_mapping=index_mapping, num_cols=index_mapping.num_vars)

    # Get objective sense
    sense = model_ir.objective.sense if model_ir.objective else ObjSense.MIN

    # Differentiate objective w.r.t. each variable
    for var_name in sorted(model_ir.variables.keys()):
        var_def = model_ir.variables[var_name]

        # Enumerate all instances of this variable
        instances = enumerate_variable_instances(var_def, model_ir)

        for indices in instances:
            # Get column ID for this variable instance
            col_id = index_mapping.get_col_id(var_name, indices)
            if col_id is None:
                continue

            # Differentiate objective w.r.t. this specific variable instance
            # Index-aware differentiation: pass indices to distinguish x(i1) from x(i2)
            derivative = differentiate_expr(obj_expr, var_name, indices, config)

            # Apply objective sense
            if sense == ObjSense.MAX:
                # max f(x) = min -f(x), so gradient is -∇f
                derivative = Unary("-", derivative)

            # Simplify derivative expression based on config
            mode = get_simplification_mode(config)
            derivative = apply_simplification(derivative, mode)

            # Store in gradient vector
            gradient.set_derivative(col_id, derivative)

    return gradient


def compute_gradient_for_expression(
    expr: Expr, model_ir: ModelIR, negate: bool = False, config: Config | None = None
) -> GradientVector:
    """
    Compute gradient of an arbitrary expression with respect to all variables.

    Useful for computing gradients of constraint expressions or sub-expressions.

    Args:
        expr: Expression to differentiate
        model_ir: Model IR with variables
        negate: If True, negate the gradient

    Returns:
        GradientVector with gradient components

    Example:
        >>> # Gradient of x^2 + y
        >>> expr = Binary("+", Call("power", (VarRef("x"), Const(2))), VarRef("y"))
        >>> gradient = compute_gradient_for_expression(expr, model_ir)
        >>> gradient.get_derivative_by_name("x")  # Returns: 2*x
        >>> gradient.get_derivative_by_name("y")  # Returns: 1
    """
    # Build index mapping
    index_mapping = build_index_mapping(model_ir)

    # Create gradient vector
    gradient = GradientVector(index_mapping=index_mapping, num_cols=index_mapping.num_vars)

    # Differentiate w.r.t. each variable
    for var_name in sorted(model_ir.variables.keys()):
        var_def = model_ir.variables[var_name]

        # Enumerate all instances
        instances = enumerate_variable_instances(var_def, model_ir)

        for indices in instances:
            col_id = index_mapping.get_col_id(var_name, indices)
            if col_id is None:
                continue

            # Differentiate w.r.t. this specific variable instance
            # Index-aware differentiation: pass indices to distinguish x(i1) from x(i2)
            derivative = differentiate_expr(expr, var_name, indices, config)

            # Apply negation if requested
            if negate:
                derivative = Unary("-", derivative)

            # Simplify derivative expression based on config
            mode = get_simplification_mode(config)
            derivative = apply_simplification(derivative, mode)

            # Store
            gradient.set_derivative(col_id, derivative)

    return gradient
