"""Objective variable detection for KKT system assembly.

In GAMS NLP models, the objective function is typically represented as:
1. An objective variable (e.g., "obj", "z", "cost")
2. A defining equation that sets the objective variable equal to the
   objective expression (e.g., "objdef.. obj =E= sum(i, c(i)*x(i));")

For KKT transformation, we need to:
- Identify the objective variable and its defining equation
- Include the defining equation in the MCP model
- Decide whether to create a stationarity equation for the objective variable
  (typically no, since it's defined by the equation, not optimized over)
"""

from __future__ import annotations

from dataclasses import dataclass

from src.ir.ast import Expr, VarRef
from src.ir.model_ir import ModelIR
from src.ir.symbols import EquationDef


@dataclass
class ObjectiveInfo:
    """Information about the objective variable and its defining equation.

    Attributes:
        objvar: Name of the objective variable (e.g., "obj", "z")
        objvar_indices: Index tuple for the objective variable (usually empty)
        defining_equation: Name of the equation that defines the objective
        needs_stationarity: Whether to create a stationarity equation for objvar
    """

    objvar: str
    objvar_indices: tuple[str, ...] = ()
    defining_equation: str = ""
    needs_stationarity: bool = False


def extract_objective_info(model_ir: ModelIR) -> ObjectiveInfo:
    """Extract objective variable and its defining equation.

    The objective variable appears in the objective function but is
    defined by an equation (e.g., obj =E= f(x)). We need to:
    1. Include the defining equation in the MCP
    2. Decide whether to create a stationarity row for objvar

    For standard NLP → MCP transformation:
    - The objective variable is free (no bounds)
    - No stationarity equation is needed (objvar is defined by its equation)
    - The gradient is computed w.r.t. the actual decision variables, not objvar

    Args:
        model_ir: NLP model IR

    Returns:
        ObjectiveInfo with objvar and defining equation

    Raises:
        ValueError: If no defining equation is found for the objective variable

    Example:
        >>> obj_info = extract_objective_info(model)
        >>> obj_info.objvar  # 'obj'
        >>> obj_info.defining_equation  # 'defobjective'
        >>> obj_info.needs_stationarity  # False
    """
    if model_ir.objective is None:
        raise ValueError(
            "Model has no objective function. "
            "Ensure your GAMS model includes a SOLVE statement with MINIMIZING or MAXIMIZING."
        )

    obj = model_ir.objective
    objvar = obj.objvar

    # Find defining equation
    # Common patterns: "defobjective", "objdef", "obj_def", "define_obj"
    defining_eq = None
    for eq_name, eq_def in model_ir.equations.items():
        if _is_objective_defining_equation(eq_def, objvar):
            defining_eq = eq_name
            break

    if defining_eq is None:
        raise ValueError(
            f"Could not find defining equation for objective variable '{objvar}'. "
            f"Expected an equation with '{objvar}' on the LHS. "
            f"Example: {objvar}.. {objvar} =E= <objective expression>;"
        )

    # For standard NLP → MCP: objvar is free, no stationarity needed
    # (The gradient is w.r.t. the actual decision variables, not objvar)
    needs_stationarity = False

    return ObjectiveInfo(
        objvar=objvar,
        objvar_indices=(),
        defining_equation=defining_eq,
        needs_stationarity=needs_stationarity,
    )


def _is_objective_defining_equation(eq_def: EquationDef, objvar: str) -> bool:
    """Check if an equation defines the objective variable.

    An objective defining equation has the form:
        objvar =E= expression
    or
        expression =E= objvar

    We check if the LHS or RHS is a simple variable reference to objvar.

    Args:
        eq_def: Equation definition
        objvar: Name of the objective variable

    Returns:
        True if equation defines the objective variable
    """
    lhs, rhs = eq_def.lhs_rhs

    # Check if LHS is objvar
    if _is_var_ref(lhs, objvar):
        return True

    # Check if RHS is objvar (less common but possible)
    if _is_var_ref(rhs, objvar):
        return True

    return False


def _is_var_ref(expr: Expr, var_name: str) -> bool:
    """Check if expression is a variable reference to var_name (any indices).

    Args:
        expr: AST expression
        var_name: Variable name to check

    Returns:
        True if expr is VarRef(var_name, ...) with any indices
    """
    if isinstance(expr, VarRef):
        return expr.name == var_name
    return False
