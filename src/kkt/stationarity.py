"""Stationarity equation builder for KKT system assembly.

Builds stationarity conditions: ∇f + J_h^T ν + J_g^T λ - π^L + π^U = 0

For each variable instance x(i), we need to construct the stationarity equation
that combines:
1. Gradient component ∂f/∂x(i)
2. Jacobian transpose terms J^T multipliers
3. Bound multiplier terms -π^L + π^U (for finite bounds only)

Special handling:
- Skip objective variable (it's defined by an equation, not optimized)
- Skip objective defining equation in stationarity
- Handle indexed bounds correctly (per-instance π terms)
- No π terms for infinite bounds
"""

from __future__ import annotations

from src.ir.ast import Binary, Const, Expr, MultiplierRef
from src.ir.symbols import EquationDef, Rel
from src.kkt.kkt_system import KKTSystem
from src.kkt.naming import (
    create_bound_lo_multiplier_name,
    create_bound_up_multiplier_name,
    create_eq_multiplier_name,
    create_ineq_multiplier_name,
)
from src.kkt.objective import extract_objective_info


def build_stationarity_equations(kkt: KKTSystem) -> dict[str, EquationDef]:
    """Build stationarity equations for all variable instances except objvar.

    Stationarity condition for variable x(i):
        ∂f/∂x(i) + Σ_j [∂h_j/∂x(i) · ν_j] + Σ_k [∂g_k/∂x(i) · λ_k]
        - π^L_i + π^U_i = 0

    Args:
        kkt: KKT system with gradient, Jacobians, and multipliers

    Returns:
        Dictionary mapping stationarity equation names to EquationDef objects

    Example:
        >>> stationarity = build_stationarity_equations(kkt)
        >>> stationarity["stat_x"]  # Stationarity for scalar variable x
        >>> stationarity["stat_y_i1"]  # Stationarity for indexed y(i1)
    """
    stationarity = {}
    obj_info = extract_objective_info(kkt.model_ir)

    # Index mapping for looking up variable instances
    if kkt.gradient.index_mapping is None:
        raise ValueError("Gradient must have index_mapping set")

    index_mapping = kkt.gradient.index_mapping

    # Iterate over all variable instances
    for col_id in range(kkt.gradient.num_cols):
        var_name, var_indices = index_mapping.col_to_var[col_id]

        # Skip objective variable (no stationarity equation for it)
        if var_name == obj_info.objvar:
            continue

        # Build stationarity expression for this variable instance
        stat_expr = _build_stationarity_expr(
            kkt, col_id, var_name, var_indices, obj_info.defining_equation
        )

        # Create equation name
        stat_name = _create_stationarity_name(var_name, var_indices)

        # Create stationarity equation: stat_expr = 0
        stationarity[stat_name] = EquationDef(
            name=stat_name,
            domain=var_indices,
            relation=Rel.EQ,
            lhs_rhs=(stat_expr, Const(0.0)),
        )

    return stationarity


def _build_stationarity_expr(
    kkt: KKTSystem,
    col_id: int,
    var_name: str,
    var_indices: tuple[str, ...],
    obj_defining_eq: str,
) -> Expr:
    """Build the LHS expression for stationarity equation.

    Returns: ∂f/∂x + J_h^T ν + J_g^T λ - π^L + π^U
    """
    # Start with gradient component
    grad_component = kkt.gradient.get_derivative(col_id)
    expr: Expr
    if grad_component is None:
        expr = Const(0.0)
    else:
        expr = grad_component

    # Add J_eq^T ν terms (equality constraint multipliers)
    expr = _add_jacobian_transpose_terms(
        expr, kkt.J_eq, col_id, kkt.multipliers_eq, create_eq_multiplier_name, obj_defining_eq
    )

    # Add J_ineq^T λ terms (inequality constraint multipliers)
    expr = _add_jacobian_transpose_terms(
        expr, kkt.J_ineq, col_id, kkt.multipliers_ineq, create_ineq_multiplier_name, None
    )

    # Subtract π^L (lower bound multiplier, if exists)
    key = (var_name, var_indices)
    if key in kkt.multipliers_bounds_lo:
        piL_name = create_bound_lo_multiplier_name(var_name, var_indices)
        expr = Binary("-", expr, MultiplierRef(piL_name, var_indices))

    # Add π^U (upper bound multiplier, if exists)
    if key in kkt.multipliers_bounds_up:
        piU_name = create_bound_up_multiplier_name(var_name, var_indices)
        expr = Binary("+", expr, MultiplierRef(piU_name, var_indices))

    return expr


def _add_jacobian_transpose_terms(
    expr: Expr,
    jacobian,
    col_id: int,
    multipliers: dict,
    name_func,
    skip_eq: str | None,
) -> Expr:
    """Add J^T multiplier terms to the stationarity expression.

    For each row in the Jacobian that has a nonzero entry at col_id,
    add: ∂constraint/∂x · multiplier
    """
    if jacobian.index_mapping is None:
        return expr

    # Iterate over all rows in the Jacobian
    for row_id in range(jacobian.num_rows):
        # Check if this column appears in this row
        derivative = jacobian.get_derivative(row_id, col_id)
        if derivative is None:
            continue

        # Get constraint name and indices for this row
        eq_name, eq_indices = jacobian.index_mapping.row_to_eq[row_id]

        # Skip objective defining equation (not included in stationarity)
        if skip_eq and eq_name == skip_eq:
            continue

        # Get multiplier name for this constraint
        mult_name = name_func(eq_name, eq_indices)

        # Check if multiplier exists (it should if we built multipliers correctly)
        if mult_name not in multipliers:
            # This shouldn't happen if multiplier generation is correct
            continue

        # Add term: derivative * multiplier
        mult_ref = MultiplierRef(mult_name, eq_indices)
        term = Binary("*", derivative, mult_ref)
        expr = Binary("+", expr, term)

    return expr


def _create_stationarity_name(var_name: str, var_indices: tuple[str, ...]) -> str:
    """Create name for stationarity equation.

    Examples:
        stat_x           (scalar variable x)
        stat_y_i         (indexed variable y(i))
        stat_z_i_j       (two-index variable z(i,j))
    """
    if var_indices:
        indices_str = "_".join(var_indices)
        return f"stat_{var_name}_{indices_str}"
    return f"stat_{var_name}"
