"""
Constraint Jacobian Computation

This module computes Jacobians for equality and inequality constraints.

Day 8 Scope:
-----------
- Compute J_h (equality constraints Jacobian)
- Compute J_g (inequality constraints Jacobian)
- Include bound-derived equations in J_g
- Handle indexed constraints correctly
- Use normalized constraint form from Sprint 1

Mathematical Background:
-----------------------
For constraints h(x) = 0 and g(x) ≤ 0:
- Equality Jacobian: J_h[i,j] = ∂h_i/∂x_j
- Inequality Jacobian: J_g[i,j] = ∂g_i/∂x_j

Constraint Forms:
- Equality: h(x) = 0 (from equations with =e= relation)
- Inequality: g(x) ≤ 0 (from equations with =l= or =g= relations, normalized)
- Bounds: Variable bounds are converted to inequality constraints

Normalized Forms (from Sprint 1):
---------------------------------
All constraints are normalized to standard form:
- Equality: lhs - rhs = 0
- Inequality: lhs - rhs ≤ 0 (after normalization)
- Bounds: Stored in ModelIR.normalized_bounds

Bound Equations:
---------------
Variable bounds are critical for KKT conditions. They appear as inequality constraints:
- Lower bound: x(i) >= lo(i) → normalized to -(x(i) - lo(i)) ≤ 0
- Upper bound: x(i) <= up(i) → normalized to x(i) - up(i) ≤ 0

These bound equations contribute rows to J_g with simple structure:
- d(x(i) - lo(i))/dx(i) = 1
- d(x(i) - lo(i))/dx(j) = 0 for j ≠ i

Index-Aware Differentiation:
----------------------------
Uses index-aware differentiation from Phase 1-5 to properly distinguish
between different instances of indexed variables and constraints.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..ir.model_ir import ModelIR

from .derivative_rules import differentiate_expr
from .index_mapping import build_index_mapping, enumerate_variable_instances
from .jacobian import JacobianStructure


def compute_constraint_jacobian(
    model_ir: ModelIR,
) -> tuple[JacobianStructure, JacobianStructure]:
    """
    Compute Jacobians for all constraints (equalities and inequalities).

    This function computes both J_h (equality constraints) and J_g (inequality
    constraints) including bound-derived constraints.

    Steps:
    1. Build index mapping to enumerate all variable and equation instances
    2. Process equality constraints (h(x) = 0)
    3. Process inequality constraints (g(x) ≤ 0)
    4. Include bound-derived equations in J_g
    5. Differentiate each constraint w.r.t. all variables using index-aware matching

    Args:
        model_ir: Model IR with constraints, variables, and normalized bounds

    Returns:
        Tuple of (J_h, J_g):
        - J_h: JacobianStructure for equality constraints
        - J_g: JacobianStructure for inequality constraints (includes bounds)

    Examples:
        >>> # Simple equality: x + y = 5 (normalized to x + y - 5 = 0)
        >>> J_h, J_g = compute_constraint_jacobian(model_ir)
        >>> J_h.get_derivative(0, 0)  # ∂h_0/∂x = 1
        >>> J_h.get_derivative(0, 1)  # ∂h_0/∂y = 1

        >>> # Simple inequality: x <= 10 (normalized to x - 10 <= 0)
        >>> J_h, J_g = compute_constraint_jacobian(model_ir)
        >>> J_g.get_derivative(0, 0)  # ∂g_0/∂x = 1
    """
    # Build index mapping for variables and equations
    index_mapping = build_index_mapping(model_ir)

    # Count equation instances for each constraint type
    num_equality_rows = _count_equation_instances(model_ir, model_ir.equalities)
    num_inequality_rows = _count_equation_instances(model_ir, model_ir.inequalities)
    num_bound_rows = len(model_ir.normalized_bounds)

    # Create Jacobian structures
    J_h = JacobianStructure(
        index_mapping=index_mapping,
        num_rows=num_equality_rows,
        num_cols=index_mapping.num_vars,
    )
    J_g = JacobianStructure(
        index_mapping=index_mapping,
        num_rows=num_inequality_rows + num_bound_rows,
        num_cols=index_mapping.num_vars,
    )

    # Process equality constraints
    _compute_equality_jacobian(model_ir, index_mapping, J_h)

    # Process inequality constraints
    _compute_inequality_jacobian(model_ir, index_mapping, J_g)

    # Include bound-derived equations
    _compute_bound_jacobian(model_ir, index_mapping, J_g)

    return J_h, J_g


def _compute_equality_jacobian(model_ir: ModelIR, index_mapping, J_h: JacobianStructure) -> None:
    """
    Compute Jacobian for equality constraints: J_h[i,j] = ∂h_i/∂x_j.

    Processes all equations in ModelIR.equalities. Each equation is in normalized
    form (lhs - rhs), and represents h_i(x) = 0.

    Args:
        model_ir: Model IR with equality constraints
        index_mapping: Index mapping for variables and equations
        J_h: Jacobian structure to populate (modified in place)
    """
    from .index_mapping import enumerate_equation_instances

    for eq_name in model_ir.equalities:
        eq_def = model_ir.equations[eq_name]

        # Get all instances of this equation (handles indexed constraints)
        eq_instances = enumerate_equation_instances(eq_name, eq_def.domain, model_ir)

        for eq_indices in eq_instances:
            # Get row ID for this equation instance
            row_id = index_mapping.get_row_id(eq_name, eq_indices)
            if row_id is None:
                continue

            # Get equation expression (normalized form: lhs - rhs)
            lhs, rhs = eq_def.lhs_rhs
            from ..ir.ast import Binary

            constraint_expr = Binary("-", lhs, rhs)

            # Substitute symbolic indices with concrete indices for this instance
            if eq_def.domain:
                constraint_expr = _substitute_indices(constraint_expr, eq_def.domain, eq_indices)

            # Differentiate w.r.t. each variable
            for var_name in sorted(model_ir.variables.keys()):
                var_def = model_ir.variables[var_name]

                # Enumerate all instances of this variable
                var_instances = enumerate_variable_instances(var_def, model_ir)

                for var_indices in var_instances:
                    col_id = index_mapping.get_col_id(var_name, var_indices)
                    if col_id is None:
                        continue

                    # Differentiate constraint w.r.t. this specific variable instance
                    # Use index-aware differentiation
                    derivative = differentiate_expr(constraint_expr, var_name, var_indices)

                    # Store in Jacobian (only if non-zero - sparsity optimization happens in simplification)
                    J_h.set_derivative(row_id, col_id, derivative)


def _compute_inequality_jacobian(model_ir: ModelIR, index_mapping, J_g: JacobianStructure) -> None:
    """
    Compute Jacobian for inequality constraints: J_g[i,j] = ∂g_i/∂x_j.

    Processes all equations in ModelIR.inequalities. Each equation is in normalized
    form (lhs - rhs ≤ 0), representing g_i(x) ≤ 0.

    Note: Bounds (e.g., 'x_lo', 'x_up') are in inequalities but not in equations.
    They are handled separately by _compute_bound_jacobian(), so we skip them here.

    Args:
        model_ir: Model IR with inequality constraints
        index_mapping: Index mapping for variables and equations
        J_g: Jacobian structure to populate (modified in place)
    """
    from .index_mapping import enumerate_equation_instances

    for eq_name in model_ir.inequalities:
        # Skip bounds - they're handled by _compute_bound_jacobian()
        if eq_name in model_ir.normalized_bounds:
            continue

        eq_def = model_ir.equations[eq_name]

        # Get all instances of this equation (handles indexed constraints)
        eq_instances = enumerate_equation_instances(eq_name, eq_def.domain, model_ir)

        for eq_indices in eq_instances:
            # Get row ID for this equation instance
            row_id = index_mapping.get_row_id(eq_name, eq_indices)
            if row_id is None:
                continue

            # Get equation expression (normalized form: lhs - rhs)
            lhs, rhs = eq_def.lhs_rhs
            from ..ir.ast import Binary

            constraint_expr = Binary("-", lhs, rhs)

            # Substitute symbolic indices with concrete indices for this instance
            if eq_def.domain:
                constraint_expr = _substitute_indices(constraint_expr, eq_def.domain, eq_indices)

            # Differentiate w.r.t. each variable
            for var_name in sorted(model_ir.variables.keys()):
                var_def = model_ir.variables[var_name]

                # Enumerate all instances of this variable
                var_instances = enumerate_variable_instances(var_def, model_ir)

                for var_indices in var_instances:
                    col_id = index_mapping.get_col_id(var_name, var_indices)
                    if col_id is None:
                        continue

                    # Differentiate constraint w.r.t. this specific variable instance
                    derivative = differentiate_expr(constraint_expr, var_name, var_indices)

                    # Store in Jacobian
                    J_g.set_derivative(row_id, col_id, derivative)


def _compute_bound_jacobian(model_ir: ModelIR, index_mapping, J_g: JacobianStructure) -> None:
    """
    Compute Jacobian rows for bound-derived inequality constraints.

    Variable bounds are converted to inequality constraints:
    - Lower bound: x(i) >= lo(i) → -(x(i) - lo(i)) ≤ 0
    - Upper bound: x(i) <= up(i) → x(i) - up(i) ≤ 0

    These contribute simple rows to J_g:
    - d(x(i) - lo(i))/dx(i) = 1, all other derivatives = 0
    - d(x(i) - up(i))/dx(i) = 1, all other derivatives = 0

    Args:
        model_ir: Model IR with normalized bounds
        index_mapping: Index mapping for variables
        J_g: Jacobian structure to populate (modified in place)
    """
    # Bound rows come after regular inequality constraints
    bound_row_offset = _count_equation_instances(model_ir, model_ir.inequalities)

    for bound_idx, (_bound_name, norm_eq) in enumerate(sorted(model_ir.normalized_bounds.items())):
        row_id = bound_row_offset + bound_idx

        # Get bound expression (already normalized)
        bound_expr = norm_eq.expr

        # Differentiate w.r.t. each variable
        for var_name in sorted(model_ir.variables.keys()):
            var_def = model_ir.variables[var_name]

            # Enumerate all instances of this variable
            var_instances = enumerate_variable_instances(var_def, model_ir)

            for var_indices in var_instances:
                col_id = index_mapping.get_col_id(var_name, var_indices)
                if col_id is None:
                    continue

                # Differentiate bound constraint w.r.t. this variable instance
                # For bounds, we need to pass the correct indices from the normalized equation
                derivative = differentiate_expr(bound_expr, var_name, var_indices)

                # Store in Jacobian
                J_g.set_derivative(row_id, col_id, derivative)


def _count_equation_instances(model_ir: ModelIR, equation_names: list[str]) -> int:
    """
    Count total number of equation instances (rows) from a list of equation names.

    Handles indexed equations that expand to multiple instances.

    Args:
        model_ir: Model IR with equations and sets
        equation_names: List of equation names to count

    Returns:
        Total number of equation instances
    """
    from .index_mapping import enumerate_equation_instances

    total_count = 0
    for eq_name in equation_names:
        if eq_name not in model_ir.equations:
            continue
        eq_def = model_ir.equations[eq_name]
        eq_instances = enumerate_equation_instances(eq_name, eq_def.domain, model_ir)
        total_count += len(eq_instances)

    return total_count


def _substitute_indices(expr, symbolic_indices: tuple[str, ...], concrete_indices: tuple[str, ...]):
    """
    Substitute symbolic indices with concrete indices in an expression.

    For indexed constraints like balance(i), the equation definition uses symbolic
    indices (e.g., VarRef('x', ('i',))). When differentiating a specific instance
    like balance(i1), we need to substitute 'i' → 'i1' in the expression.

    Args:
        expr: Expression with symbolic indices
        symbolic_indices: Tuple of symbolic index names (e.g., ('i', 'j'))
        concrete_indices: Tuple of concrete index values (e.g., ('i1', 'j2'))

    Returns:
        Expression with concrete indices substituted

    Example:
        >>> # balance(i): x(i) + y(i) = demand(i)
        >>> # For instance balance(i1), substitute i → i1:
        >>> # VarRef('x', ('i',)) → VarRef('x', ('i1',))
    """
    from ..ir.ast import Binary, Call, ParamRef, Sum, Unary, VarRef

    if isinstance(expr, VarRef):
        # Substitute indices in VarRef
        new_indices = tuple(
            concrete_indices[symbolic_indices.index(idx)] if idx in symbolic_indices else idx
            for idx in expr.indices
        )
        return VarRef(expr.name, new_indices)

    elif isinstance(expr, ParamRef):
        # Substitute indices in ParamRef
        new_indices = tuple(
            concrete_indices[symbolic_indices.index(idx)] if idx in symbolic_indices else idx
            for idx in expr.indices
        )
        return ParamRef(expr.name, new_indices)

    elif isinstance(expr, Binary):
        # Recursively substitute in both sides
        new_left = _substitute_indices(expr.left, symbolic_indices, concrete_indices)
        new_right = _substitute_indices(expr.right, symbolic_indices, concrete_indices)
        return Binary(expr.op, new_left, new_right)

    elif isinstance(expr, Unary):
        # Recursively substitute in child
        new_child = _substitute_indices(expr.child, symbolic_indices, concrete_indices)
        return Unary(expr.op, new_child)

    elif isinstance(expr, Call):
        # Recursively substitute in arguments
        new_args = tuple(
            _substitute_indices(arg, symbolic_indices, concrete_indices) for arg in expr.args
        )
        return Call(expr.func, new_args)

    elif isinstance(expr, Sum):
        # Don't substitute indices that are bound by the sum
        # Only substitute free indices
        free_symbolic = tuple(idx for idx in symbolic_indices if idx not in expr.index_sets)
        free_concrete = tuple(
            concrete_indices[symbolic_indices.index(idx)]
            for idx in symbolic_indices
            if idx not in expr.index_sets
        )
        if free_symbolic:
            new_body = _substitute_indices(expr.body, free_symbolic, free_concrete)
            return Sum(expr.index_sets, new_body)
        else:
            return expr

    else:
        # Const, SymbolRef, etc. - no indices to substitute
        return expr
