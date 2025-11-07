"""Stationarity equation builder for KKT system assembly.

Builds stationarity conditions: ∇f + J_h^T ν + J_g^T λ - π^L + π^U = 0

For indexed variables x(i), we generate indexed stationarity equations stat_x(i)
instead of element-specific equations stat_x_i1, stat_x_i2, etc.

This allows proper GAMS MCP Model syntax: stat_x.x

Special handling:
- Skip objective variable (it's defined by an equation, not optimized)
- Skip objective defining equation in stationarity
- Handle indexed bounds correctly (per-instance π terms)
- No π terms for infinite bounds
- Group variable instances to generate indexed equations
"""

from __future__ import annotations

from src.ir.ast import Binary, Call, Const, Expr, MultiplierRef, ParamRef, Sum, Unary, VarRef
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

    For indexed variables, generates indexed equations with domains.
    For scalar variables, generates scalar equations.

    Stationarity condition for variable x(i):
        ∂f/∂x(i) + Σ_j [∂h_j/∂x(i) · ν_j] + Σ_k [∂g_k/∂x(i) · λ_k]
        - π^L(i) + π^U(i) = 0

    Args:
        kkt: KKT system with gradient, Jacobians, and multipliers

    Returns:
        Dictionary mapping stationarity equation names to EquationDef objects

    Example:
        >>> stationarity = build_stationarity_equations(kkt)
        >>> stationarity["stat_x"]  # Stationarity for scalar variable x
        >>> stationarity["stat_y"]  # Stationarity for indexed y(i) - now indexed!
    """
    stationarity = {}
    obj_info = extract_objective_info(kkt.model_ir)

    # Index mapping for looking up variable instances
    if kkt.gradient.index_mapping is None:
        raise ValueError("Gradient must have index_mapping set")

    # Group variable instances by base variable name
    # Skip objective variable UNLESS Strategy 1 was applied
    objvar_to_skip = obj_info.objvar if not kkt.model_ir.strategy1_applied else None
    var_groups = _group_variables_by_name(kkt, objvar_to_skip)

    # For each variable, generate either indexed or scalar stationarity equation
    for var_name, instances in var_groups.items():
        # Get variable definition to determine domain
        if var_name not in kkt.model_ir.variables:
            continue

        var_def = kkt.model_ir.variables[var_name]

        # Determine which equation to skip in stationarity building
        # Skip objdef equation UNLESS Strategy 1 was applied
        skip_eq = obj_info.defining_equation if not kkt.model_ir.strategy1_applied else None

        if var_def.domain:
            # Indexed variable: generate indexed stationarity equation
            stat_name = f"stat_{var_name}"
            stat_expr = _build_indexed_stationarity_expr(
                kkt, var_name, var_def.domain, instances, skip_eq
            )
            stationarity[stat_name] = EquationDef(
                name=stat_name,
                domain=var_def.domain,  # Use same domain as variable
                relation=Rel.EQ,
                lhs_rhs=(stat_expr, Const(0.0)),
            )
        else:
            # Scalar variable: generate scalar stationarity equation
            if len(instances) != 1:
                raise ValueError(f"Scalar variable {var_name} has {len(instances)} instances")

            col_id, var_indices = instances[0]
            stat_name = f"stat_{var_name}"
            stat_expr = _build_stationarity_expr(kkt, col_id, var_name, var_indices, skip_eq)
            stationarity[stat_name] = EquationDef(
                name=stat_name,
                domain=(),  # Empty domain for scalar
                relation=Rel.EQ,
                lhs_rhs=(stat_expr, Const(0.0)),
            )

    return stationarity


def _group_variables_by_name(
    kkt: KKTSystem, objvar: str | None
) -> dict[str, list[tuple[int, tuple[str, ...]]]]:
    """Group variable instances by base variable name.

    Args:
        kkt: KKT system
        objvar: Name of objective variable to skip (None to include all variables)

    Returns:
        Dictionary mapping var_name to list of (col_id, indices) tuples

    Example:
        {
            "x": [(0, ("i1",)), (1, ("i2",)), (2, ("i3",))],
            "y": [(3, ())]  # scalar
        }
    """
    groups: dict[str, list[tuple[int, tuple[str, ...]]]] = {}

    if kkt.gradient.index_mapping is None:
        return groups

    index_mapping = kkt.gradient.index_mapping

    for col_id in range(kkt.gradient.num_cols):
        var_name, var_indices = index_mapping.col_to_var[col_id]

        # Skip objective variable (if specified)
        if objvar and var_name == objvar:
            continue

        if var_name not in groups:
            groups[var_name] = []

        groups[var_name].append((col_id, var_indices))

    return groups


def _build_indexed_stationarity_expr(
    kkt: KKTSystem,
    var_name: str,
    domain: tuple[str, ...],
    instances: list[tuple[int, tuple[str, ...]]],
    obj_defining_eq: str | None,
) -> Expr:
    """Build indexed stationarity expression using set indices.

    For variable x(i), builds expression with symbolic index i instead of
    element-specific expressions for i1, i2, i3, etc.

    Args:
        kkt: KKT system
        var_name: Base variable name
        domain: Variable domain (e.g., ("i",))
        instances: List of (col_id, indices) for all instances
        obj_defining_eq: Name of objective defining equation to skip

    Returns:
        Indexed expression using set indices
    """
    # Build gradient term: ∂f/∂x(i)
    # We use VarRef with domain indices instead of element labels
    expr = _build_indexed_gradient_term(kkt, var_name, domain, instances)

    # Add Jacobian transpose terms as sums
    expr = _add_indexed_jacobian_terms(
        expr,
        kkt,
        kkt.J_eq,
        var_name,
        domain,
        instances,
        kkt.multipliers_eq,
        create_eq_multiplier_name,
        obj_defining_eq,
    )

    expr = _add_indexed_jacobian_terms(
        expr,
        kkt,
        kkt.J_ineq,
        var_name,
        domain,
        instances,
        kkt.multipliers_ineq,
        create_ineq_multiplier_name,
        None,
    )

    # Add bound multiplier terms if they exist
    # Check if any instance has bounds
    has_lower = any((var_name, indices) in kkt.multipliers_bounds_lo for _, indices in instances)
    has_upper = any((var_name, indices) in kkt.multipliers_bounds_up for _, indices in instances)

    if has_lower:
        piL_name = create_bound_lo_multiplier_name(var_name)
        expr = Binary("-", expr, MultiplierRef(piL_name, domain))

    if has_upper:
        piU_name = create_bound_up_multiplier_name(var_name)
        expr = Binary("+", expr, MultiplierRef(piU_name, domain))

    return expr


def _build_indexed_gradient_term(
    kkt: KKTSystem,
    var_name: str,
    domain: tuple[str, ...],
    instances: list[tuple[int, tuple[str, ...]]],
) -> Expr:
    """Build gradient term for indexed variable.

    For now, we use the gradient from the first instance as a placeholder.
    This assumes the gradient structure is uniform across instances.
    """
    if not instances:
        return Const(0.0)

    # Get gradient from first instance
    col_id, _ = instances[0]
    grad_component = kkt.gradient.get_derivative(col_id)

    if grad_component is None:
        return Const(0.0)

    # Replace element-specific indices with domain indices in the gradient
    return _replace_indices_in_expr(grad_component, domain)


def _replace_indices_in_expr(expr: Expr, domain: tuple[str, ...]) -> Expr:
    """Replace element-specific indices with domain indices in expression.

    For example, converts a("i1") to a(i) where domain = ("i",)
    """
    match expr:
        case Const(_):
            return expr
        case VarRef(name, indices):
            if indices and domain and len(indices) == len(domain):
                # Replace element labels with domain indices
                return VarRef(name, domain)
            return expr
        case ParamRef(name, indices):
            if indices and domain and len(indices) == len(domain):
                return ParamRef(name, domain)
            return expr
        case MultiplierRef(name, indices):
            if indices and domain and len(indices) == len(domain):
                return MultiplierRef(name, domain)
            return expr
        case Binary(op, left, right):
            new_left = _replace_indices_in_expr(left, domain)
            new_right = _replace_indices_in_expr(right, domain)
            return Binary(op, new_left, new_right)
        case Unary(op, child):
            new_child = _replace_indices_in_expr(child, domain)
            return Unary(op, new_child)
        case Call(func, args):
            new_args = tuple(_replace_indices_in_expr(arg, domain) for arg in args)
            return Call(func, new_args)
        case Sum(index_sets, body):
            # Recursively process body to replace any element-specific indices
            new_body = _replace_indices_in_expr(body, domain)
            if new_body is not body:
                return Sum(index_sets, new_body)
            return expr
        case _:
            return expr


def _add_indexed_jacobian_terms(
    expr: Expr,
    kkt: KKTSystem,
    jacobian,
    var_name: str,
    var_domain: tuple[str, ...],
    instances: list[tuple[int, tuple[str, ...]]],
    multipliers: dict,
    name_func,
    skip_eq: str | None,
) -> Expr:
    """Add Jacobian transpose terms for indexed variable.

    Builds sum expressions for constraints that depend on the variable.
    """
    if jacobian.index_mapping is None:
        return expr

    # Collect all constraints that depend on this variable
    constraint_entries: dict[str, list[tuple[int, int]]] = {}  # eq_name -> [(row_id, col_id)]

    for col_id, _ in instances:
        for row_id in range(jacobian.num_rows):
            derivative = jacobian.get_derivative(row_id, col_id)
            if derivative is None:
                continue

            eq_name, _ = jacobian.index_mapping.row_to_eq[row_id]

            # Skip objective defining equation
            if skip_eq and eq_name == skip_eq:
                continue

            if eq_name not in constraint_entries:
                constraint_entries[eq_name] = []

            constraint_entries[eq_name].append((row_id, col_id))

    # For each constraint, add the Jacobian term
    for _eq_name, entries in constraint_entries.items():
        # Get first entry to extract structure
        row_id, col_id = entries[0]
        derivative = jacobian.get_derivative(row_id, col_id)
        eq_name_base, eq_indices = jacobian.index_mapping.row_to_eq[row_id]

        # Determine if constraint is indexed
        if eq_indices:
            # Indexed constraint: use sum
            mult_domain = _get_constraint_domain(kkt, eq_name_base)

            if mult_domain:
                # Replace indices in derivative expression
                indexed_deriv = _replace_indices_in_expr(derivative, var_domain)

                # Get base multiplier name (without element suffixes)
                mult_base_name = name_func(eq_name_base)
                mult_ref = MultiplierRef(mult_base_name, mult_domain)
                term: Expr = Binary("*", indexed_deriv, mult_ref)

                # Only use sum if constraint domain is different from variable domain
                # If domains match, it's a direct term: deriv(i) * mult(i)
                # If domains differ and compatible, we need sum: sum(j, deriv * mult(j))
                if mult_domain != var_domain and len(mult_domain) > 0:
                    # Check domain compatibility: mult_domain should be subset of var_domain
                    # or they should be disjoint (independent indexing)
                    mult_domain_set = set(mult_domain)
                    var_domain_set = set(var_domain)
                    if not mult_domain_set.issubset(
                        var_domain_set
                    ) and mult_domain_set.intersection(var_domain_set):
                        # Domains overlap but aren't compatible for summation
                        raise ValueError(
                            f"Incompatible domains for summation: variable domain {var_domain}, "
                            f"multiplier domain {mult_domain}. Multiplier domain must be either "
                            f"a subset of variable domain or completely disjoint."
                        )
                    term = Sum(mult_domain, term)

                expr = Binary("+", expr, term)
        else:
            # Scalar constraint
            mult_name = name_func(eq_name_base)

            if mult_name in multipliers:
                mult_ref = MultiplierRef(mult_name, ())
                # Replace indices in derivative
                indexed_deriv = _replace_indices_in_expr(derivative, var_domain)
                term = Binary("*", indexed_deriv, mult_ref)
                expr = Binary("+", expr, term)

    return expr


def _get_constraint_domain(kkt: KKTSystem, eq_name: str) -> tuple[str, ...]:
    """Get domain for a constraint equation."""
    if eq_name in kkt.model_ir.equations:
        return kkt.model_ir.equations[eq_name].domain
    return ()


def _build_stationarity_expr(
    kkt: KKTSystem,
    col_id: int,
    var_name: str,
    var_indices: tuple[str, ...],
    obj_defining_eq: str | None,
) -> Expr:
    """Build the LHS expression for scalar stationarity equation.

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
    expr = _add_jacobian_transpose_terms_scalar(
        expr, kkt.J_eq, col_id, kkt.multipliers_eq, create_eq_multiplier_name, obj_defining_eq, kkt
    )

    # Add J_ineq^T λ terms (inequality constraint multipliers)
    expr = _add_jacobian_transpose_terms_scalar(
        expr, kkt.J_ineq, col_id, kkt.multipliers_ineq, create_ineq_multiplier_name, None, kkt
    )

    # Subtract π^L (lower bound multiplier, if exists)
    key = (var_name, var_indices)
    if key in kkt.multipliers_bounds_lo:
        piL_name = create_bound_lo_multiplier_name(var_name)
        expr = Binary("-", expr, MultiplierRef(piL_name, var_indices))

    # Add π^U (upper bound multiplier, if exists)
    if key in kkt.multipliers_bounds_up:
        piU_name = create_bound_up_multiplier_name(var_name)
        expr = Binary("+", expr, MultiplierRef(piU_name, var_indices))

    return expr


def _add_jacobian_transpose_terms_scalar(
    expr: Expr,
    jacobian,
    col_id: int,
    multipliers: dict,
    name_func,
    skip_eq: str | None,
    kkt: KKTSystem,
) -> Expr:
    """Add J^T multiplier terms to the stationarity expression (scalar version).

    For each row in the Jacobian that has a nonzero entry at col_id,
    add: ∂constraint/∂x · multiplier

    For negated constraints (LE inequalities that complementarity negates),
    negate the Jacobian term to account for the negation.
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
        mult_name = name_func(eq_name)

        # Check if multiplier exists (it should if we built multipliers correctly)
        if mult_name not in multipliers:
            # This shouldn't happen if multiplier generation is correct
            continue

        # Add term: derivative * multiplier
        mult_ref = MultiplierRef(mult_name, eq_indices)
        term = Binary("*", derivative, mult_ref)

        # Check if this constraint was negated by complementarity
        # For negated constraints, subtract the term instead of adding it
        # EXCEPTION: Max constraints use arg - aux_max formulation, which already has
        # the correct sign, so negation is not needed. Max constraints should be added, not subtracted.
        #
        # Note: This function is called for both equality (J_eq) and inequality (J_ineq) Jacobians.
        # - Equality constraints: Won't be in complementarity_ineq, so fall through to else (add term)
        # - Inequality constraints: Should be in complementarity_ineq (registered during assembly)
        #   If an inequality is not found, it's added normally (else branch). This is safe because
        #   non-negated inequalities should be added, and any missing registration is a bug elsewhere.
        if eq_name in kkt.complementarity_ineq:
            comp_pair = kkt.complementarity_ineq[eq_name]
            if comp_pair.negated and not comp_pair.is_max_constraint:
                expr = Binary("-", expr, term)
            else:
                expr = Binary("+", expr, term)
        else:
            expr = Binary("+", expr, term)

    return expr
