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
- For non-uniform bounds (different values per element), generate per-instance
  stationarity equations to ensure bound multipliers are properly included
"""

from __future__ import annotations

from src.ir.ast import Binary, Call, Const, Expr, MultiplierRef, ParamRef, Sum, Unary, VarRef
from src.ir.model_ir import ModelIR
from src.ir.symbols import EquationDef, Rel
from src.kkt.kkt_system import KKTSystem
from src.kkt.naming import (
    create_eq_multiplier_name,
    create_ineq_multiplier_name,
    sanitize_index_for_identifier,
)
from src.kkt.objective import extract_objective_info


def _has_nonuniform_bounds(kkt: KKTSystem, var_name: str) -> bool:
    """Check if a variable has non-uniform bounds (per-instance multipliers).

    Non-uniform bounds occur when:
    - The variable has per-instance bound multipliers (stored with non-empty indices)
    - AND no uniform bound multiplier (stored with empty indices)

    This indicates the variable has different bound values for different elements,
    requiring per-instance stationarity equations to include the bound multiplier terms.

    Args:
        kkt: KKT system with multiplier definitions
        var_name: Variable name to check

    Returns:
        True if variable has non-uniform bounds requiring per-instance stationarity
    """
    # Check lower bounds
    has_uniform_lo = (var_name, ()) in kkt.multipliers_bounds_lo
    has_perinstance_lo = any(
        key[0] == var_name and key[1] != () for key in kkt.multipliers_bounds_lo.keys()
    )

    # Check upper bounds
    has_uniform_up = (var_name, ()) in kkt.multipliers_bounds_up
    has_perinstance_up = any(
        key[0] == var_name and key[1] != () for key in kkt.multipliers_bounds_up.keys()
    )

    # Non-uniform if we have per-instance multipliers without uniform multipliers
    nonuniform_lo = has_perinstance_lo and not has_uniform_lo
    nonuniform_up = has_perinstance_up and not has_uniform_up

    return nonuniform_lo or nonuniform_up


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
    # Skip objective variable UNLESS:
    # - Strategy 1 was applied, OR
    # - This is a simple variable objective (needs_stationarity=True)
    should_skip_objvar = not kkt.model_ir.strategy1_applied and not obj_info.needs_stationarity
    objvar_to_skip = obj_info.objvar if should_skip_objvar else None
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
            # Indexed variable: check if it has non-uniform bounds
            if _has_nonuniform_bounds(kkt, var_name):
                # Non-uniform bounds: generate per-instance stationarity equations
                # This ensures bound multipliers (piL_x_i1, piL_x_i2, etc.) are included
                for col_id, var_indices in instances:
                    # Create per-instance equation name: stat_x_i1, stat_x_i2, etc.
                    sanitized = [sanitize_index_for_identifier(idx) for idx in var_indices]
                    indices_str = "_".join(sanitized) if sanitized else ""
                    stat_name = (
                        f"stat_{var_name}_{indices_str}" if indices_str else f"stat_{var_name}"
                    )

                    stat_expr = _build_stationarity_expr(
                        kkt, col_id, var_name, var_indices, skip_eq
                    )
                    stationarity[stat_name] = EquationDef(
                        name=stat_name,
                        domain=(),  # Scalar equation for this specific instance
                        relation=Rel.EQ,
                        lhs_rhs=(stat_expr, Const(0.0)),
                    )
            else:
                # Uniform bounds: generate single indexed stationarity equation
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
    # Check for uniform bounds (stored under (var_name, ())) or per-instance bounds
    # Uniform bounds: single indexed multiplier for all instances
    # Non-uniform bounds: per-instance scalar multipliers (handled in scalar stationarity)
    has_lower_uniform = (var_name, ()) in kkt.multipliers_bounds_lo
    has_upper_uniform = (var_name, ()) in kkt.multipliers_bounds_up

    if has_lower_uniform:
        mult_def = kkt.multipliers_bounds_lo[(var_name, ())]
        expr = Binary("-", expr, MultiplierRef(mult_def.name, mult_def.domain))

    if has_upper_uniform:
        mult_def = kkt.multipliers_bounds_up[(var_name, ())]
        expr = Binary("+", expr, MultiplierRef(mult_def.name, mult_def.domain))

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
    col_id, var_indices = instances[0]
    grad_component = kkt.gradient.get_derivative(col_id)

    if grad_component is None:
        return Const(0.0)

    # Build element-to-set mapping from all instances
    # This maps each element label to its corresponding set name
    element_to_set = _build_element_to_set_mapping(kkt.model_ir, domain, instances)

    # Replace element-specific indices with domain indices in the gradient
    return _replace_indices_in_expr(grad_component, domain, element_to_set, kkt.model_ir)


def _build_element_to_set_mapping(
    model_ir, domain: tuple[str, ...], instances: list[tuple[int, tuple[str, ...]]]
) -> dict[str, str]:
    """Build a mapping from element labels to set names.

    Maps element labels from ALL sets in the model to their set names,
    not just the variable's domain. This enables proper index replacement
    for parameters that have indices from multiple sets.

    Also maps set names to themselves, so that domain variables like "desk"
    in price(desk) are preserved as-is rather than being treated as element
    labels that need quoting.

    Args:
        model_ir: Model IR containing set definitions
        domain: Variable domain (tuple of set names) - used for instance inference
        instances: Variable instances (used to infer element-set relationships)

    Returns:
        Dictionary mapping element labels to set names

    Example:
        For model with desk = {d1, d2, d3, d4} and shop = {carpentry, finishing}:
        Returns: {
            "d1": "desk", "d2": "desk", "d3": "desk", "d4": "desk",
            "carpentry": "shop", "finishing": "shop",
            "desk": "desk", "shop": "shop"  # Set names map to themselves
        }

    Note:
        If two different sets contain the same element label (e.g., both set h
        and set i contain "1"), mappings inferred from the variable's own
        instances and domain take precedence. Global set definitions are only
        used as a fallback for elements that have not been mapped yet. To avoid
        ambiguous mappings for parameters indexed by multiple sets, users should
        avoid reusing the same element label in different sets. In future
        enhancements, parameter domains could be leveraged to further disambiguate
        such cases.
    """
    element_to_set: dict[str, str] = {}

    # First, map set names to themselves.
    # This ensures that domain variables like "desk" in price(desk) are recognized
    # as set names (not element labels) and are preserved as unquoted identifiers.
    for set_name in model_ir.sets.keys():
        element_to_set[set_name] = set_name

    # Also map alias names to themselves
    for alias_name in model_ir.aliases.keys():
        element_to_set[alias_name] = alias_name

    # Then, use instances to infer element-set relationships for the variable's domain.
    # This ensures that, for ambiguous elements, the variable-specific domain wins.
    # It also handles cases where set definitions might not be available.
    for _col_id, var_indices in instances:
        if len(var_indices) == len(domain):
            for elem, set_name in zip(var_indices, domain, strict=True):
                if elem not in element_to_set:
                    element_to_set[elem] = set_name

    # Then, map elements from ALL sets in the model as a fallback.
    # This handles parameters like k1(h,j) where both indices need replacement,
    # while preserving any mappings already established from instances.
    for set_name, set_def in model_ir.sets.items():
        # Handle both SetDef objects (normal case) and plain containers
        # (e.g., when model_ir.sets is constructed programmatically without SetDef)
        if isinstance(set_def, (list, tuple, set, frozenset)):
            members = set_def
        else:
            members = set_def.members
        for member in members:
            # Only add if not already mapped (instance/domain-based mapping wins)
            if member not in element_to_set:
                element_to_set[member] = set_name

    return element_to_set


def _replace_indices_in_expr(
    expr: Expr,
    domain: tuple[str, ...],
    element_to_set: dict[str, str] | None = None,
    model_ir: ModelIR | None = None,
) -> Expr:
    """Replace element-specific indices with domain indices in expression.

    For example, converts data("1", "cost") to data(h, "cost") where:
    - domain = ("h",)
    - element_to_set = {"1": "h", "2": "h", "3": "h", "4": "h"}

    This handles cases where:
    - Parameters have more indices than the variable domain (e.g., data(h, *))
    - Only some indices should be replaced (element labels vs literal strings)

    For parameters, uses the parameter's declared domain to disambiguate when
    an element belongs to multiple sets. For example, if parameter a(i,c) has
    indices ('H', 'c') where 'H' belongs to both set i and c, we use the declared
    domain to know that the first index should map to set 'i'.

    Args:
        expr: Expression to process
        domain: Variable domain (e.g., ("h",) or ("i", "j"))
        element_to_set: Mapping from element labels to set names. If None,
                        falls back to simple length-based matching for backward compatibility.
        model_ir: Model IR for looking up parameter domains (optional but recommended)
    """
    match expr:
        case Const(_):
            return expr
        case VarRef() as var_ref:
            if var_ref.indices and domain:
                if element_to_set:
                    # Replace each index that maps to a set in the domain
                    str_indices = var_ref.indices_as_strings()
                    # Use variable domain for disambiguation if available
                    var_domain = None
                    if model_ir and var_ref.name in model_ir.variables:
                        var_domain = model_ir.variables[var_ref.name].domain
                    new_indices = _replace_matching_indices(
                        str_indices, element_to_set, declared_domain=var_domain
                    )
                    return VarRef(var_ref.name, new_indices)
                elif len(var_ref.indices) == len(domain):
                    # Fallback: Replace all indices if lengths match
                    return VarRef(var_ref.name, domain)
            return expr
        case ParamRef() as param_ref:
            if param_ref.indices and domain:
                if element_to_set:
                    str_indices = param_ref.indices_as_strings()
                    # Use parameter domain for disambiguation
                    param_domain = None
                    if model_ir and param_ref.name in model_ir.params:
                        param_domain = model_ir.params[param_ref.name].domain
                    new_indices = _replace_matching_indices(
                        str_indices, element_to_set, declared_domain=param_domain
                    )
                    return ParamRef(param_ref.name, new_indices)
                elif len(param_ref.indices) == len(domain):
                    return ParamRef(param_ref.name, domain)
            return expr
        case MultiplierRef() as mult_ref:
            if mult_ref.indices and domain:
                if element_to_set:
                    str_indices = mult_ref.indices_as_strings()
                    new_indices = _replace_matching_indices(str_indices, element_to_set)
                    return MultiplierRef(mult_ref.name, new_indices)
                elif len(mult_ref.indices) == len(domain):
                    return MultiplierRef(mult_ref.name, domain)
            return expr
        case Binary(op, left, right):
            new_left = _replace_indices_in_expr(left, domain, element_to_set, model_ir)
            new_right = _replace_indices_in_expr(right, domain, element_to_set, model_ir)
            return Binary(op, new_left, new_right)
        case Unary(op, child):
            new_child = _replace_indices_in_expr(child, domain, element_to_set, model_ir)
            return Unary(op, new_child)
        case Call(func, args):
            new_args = tuple(
                _replace_indices_in_expr(arg, domain, element_to_set, model_ir) for arg in args
            )
            return Call(func, new_args)
        case Sum(index_sets, body):
            # Recursively process body to replace any element-specific indices
            new_body = _replace_indices_in_expr(body, domain, element_to_set, model_ir)
            if new_body is not body:
                return Sum(index_sets, new_body)
            return expr
        case _:
            return expr


def _replace_matching_indices(
    indices: tuple[str, ...],
    element_to_set: dict[str, str],
    declared_domain: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    """Replace element labels with their corresponding set names.

    For each index in indices, if it's an element label that maps to a set,
    replace it with the set name. This handles parameters indexed by multiple
    sets (e.g., k1(h,j) where we need to replace both "1"->h and "a"->j).

    When a declared_domain is provided (e.g., from a parameter's domain definition),
    it's used to disambiguate when an element belongs to multiple sets. For example,
    if element 'H' belongs to both set 'c' and set 'i', and the parameter domain
    is ('i', 'c'), the first 'H' should map to 'i', not 'c'.

    Special handling for wildcard domains: If a parameter is declared with a
    wildcard domain like compdat(*,alloy), the "*" in the declared domain means
    "accept any element". In this case, we should NOT replace the concrete index
    (like "price") with "*". Instead, we preserve the original index if it's not
    in element_to_set, or replace it with its set name if it is an element.

    Args:
        indices: Original indices (e.g., ("1", "a") or ("1", "cost"))
        element_to_set: Mapping from element labels to set names
        declared_domain: The declared domain of the symbol (for disambiguation)

    Returns:
        New indices with element labels replaced by set names

    Example:
        >>> _replace_matching_indices(("1", "a"), {"1": "h", "a": "j"})
        ("h", "j")  # Both "1" and "a" replaced with their set names
        >>> _replace_matching_indices(("1", "cost"), {"1": "h"})
        ("h", "cost")  # "1" replaced with "h", "cost" unchanged (not in mapping)
        >>> # With declared_domain for disambiguation:
        >>> _replace_matching_indices(("H", "c"), {"H": "c", "c": "c"}, declared_domain=("i", "c"))
        ("i", "c")  # 'H' maps to 'i' (from declared_domain), 'c' stays as 'c'
        >>> # With wildcard domain - preserve concrete indices:
        >>> _replace_matching_indices(("price", "a"), {"a": "alloy"}, declared_domain=("*", "alloy"))
        ("price", "alloy")  # "price" preserved (wildcard domain), "a" replaced
    """
    new_indices = []
    for i, idx in enumerate(indices):
        # If we have a declared domain, use it to determine the target set
        if declared_domain and i < len(declared_domain):
            target_set = declared_domain[i]
            # Special case: wildcard "*" means the parameter accepts any element
            # at this position. Don't replace with "*" - instead, fall back to
            # element_to_set mapping or preserve the original index.
            if target_set == "*":
                if idx in element_to_set:
                    # The index is an element from a known set - replace it
                    new_indices.append(element_to_set[idx])
                else:
                    # The index is a concrete literal (like "price") - preserve it
                    new_indices.append(idx)
            else:
                # The index should map to the target set from the declared domain
                # BUT: if idx is already a set name (self-mapping in element_to_set),
                # it's a symbolic index that should be preserved, not replaced with
                # the parent set. E.g., 'cg' is a subset of 'genchar' - keep 'cg'.
                if idx in element_to_set and element_to_set[idx] == idx:
                    new_indices.append(idx)
                else:
                    new_indices.append(target_set)
        elif idx in element_to_set:
            # Replace element with its set name
            new_indices.append(element_to_set[idx])
        else:
            # Keep the index unchanged (it's a literal like "cost" or already a set name)
            new_indices.append(idx)
    return tuple(new_indices)


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

    # Build element-to-set mapping for index replacement
    element_to_set = _build_element_to_set_mapping(kkt.model_ir, var_domain, instances)

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
                # Replace indices in derivative expression using element_to_set mapping
                indexed_deriv = _replace_indices_in_expr(
                    derivative, var_domain, element_to_set, kkt.model_ir
                )

                # Get base multiplier name (without element suffixes)
                mult_base_name = name_func(eq_name_base)
                mult_ref = MultiplierRef(mult_base_name, mult_domain)
                term: Expr = Binary("*", indexed_deriv, mult_ref)

                # Determine if we need a sum or a direct term:
                # - If domains match exactly: direct term deriv(i) * mult(i)
                # - If mult_domain is subset of var_domain: direct term deriv(i,j) * mult(i)
                #   (the multiplier indices are shared with the variable - no summation needed)
                # - If mult_domain is disjoint from var_domain: sum over mult_domain
                #   (e.g., sum(k, deriv * mult(k)) where k is independent of variable indices)
                # - If mult_domain partially overlaps var_domain but is not a subset: error
                mult_domain_set = set(mult_domain)
                var_domain_set = set(var_domain)

                if mult_domain == var_domain:
                    # Exact match: direct term, no sum needed
                    pass
                elif mult_domain_set.issubset(var_domain_set):
                    # Subset: constraint domain is contained in variable domain
                    # e.g., supply(i) contributes to stat_x(i,j) with direct term lam_supply(i)
                    # No sum needed - the i index is shared
                    pass
                elif not mult_domain_set.intersection(var_domain_set):
                    # Disjoint: constraint has indices independent of variable
                    # Need to sum over the constraint's domain
                    term = Sum(mult_domain, term)
                else:
                    # Partial overlap that's not a subset - incompatible
                    raise ValueError(
                        f"Incompatible domains for stationarity: variable domain {var_domain}, "
                        f"multiplier domain {mult_domain}. Multiplier domain must be either "
                        f"a subset of variable domain or completely disjoint."
                    )

                expr = Binary("+", expr, term)
        else:
            # Scalar constraint
            mult_name = name_func(eq_name_base)

            if mult_name in multipliers:
                mult_ref = MultiplierRef(mult_name, ())
                # Replace indices in derivative using element_to_set mapping
                indexed_deriv = _replace_indices_in_expr(
                    derivative, var_domain, element_to_set, kkt.model_ir
                )
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
        mult_def = kkt.multipliers_bounds_lo[key]
        # Use the actual multiplier name from the definition (handles both indexed and scalar cases)
        piL_name = mult_def.name
        # Use the multiplier's domain for the indices (empty for scalar multipliers)
        expr = Binary("-", expr, MultiplierRef(piL_name, mult_def.domain))

    # Add π^U (upper bound multiplier, if exists)
    if key in kkt.multipliers_bounds_up:
        mult_def = kkt.multipliers_bounds_up[key]
        # Use the actual multiplier name from the definition (handles both indexed and scalar cases)
        piU_name = mult_def.name
        # Use the multiplier's domain for the indices (empty for scalar multipliers)
        expr = Binary("+", expr, MultiplierRef(piU_name, mult_def.domain))

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
