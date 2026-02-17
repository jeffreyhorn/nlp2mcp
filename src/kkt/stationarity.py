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

from collections import ChainMap
from collections.abc import Mapping

from src.ad.ad_core import apply_simplification, get_simplification_mode
from src.config import Config
from src.ir.ast import (
    Binary,
    Call,
    Const,
    DollarConditional,
    Expr,
    MultiplierRef,
    ParamRef,
    Prod,
    SetMembershipTest,
    Sum,
    SymbolRef,
    Unary,
    VarRef,
)
from src.ir.model_ir import ModelIR
from src.ir.symbols import EquationDef, Rel
from src.kkt.kkt_system import KKTSystem
from src.kkt.naming import (
    create_eq_multiplier_name,
    create_ineq_multiplier_name,
    sanitize_index_for_identifier,
)
from src.kkt.objective import extract_objective_info


def _collect_referenced_variable_names(model_ir: ModelIR) -> set[str]:
    """Collect names of all variables referenced in equation bodies or the objective.

    Issue #742: Variables declared but never referenced in any equation body
    or objective (like dummy/reporting variables) should be excluded from KKT
    stationarity equation generation. This function walks all equation LHS/RHS
    expressions and the objective to build a set of actually-referenced variable
    names.

    All names are lowercased to match the canonical form used by
    CaseInsensitiveDict keys, ensuring case-insensitive comparison.

    Args:
        model_ir: Model IR containing equation definitions and objective

    Returns:
        Set of variable names (lowercase canonical form) that appear in at
        least one equation or the objective
    """
    referenced: set[str] = set()

    def _walk(expr: Expr) -> None:
        # Record variable references by name (case-insensitive)
        if isinstance(expr, VarRef):
            referenced.add(expr.name.lower())

        # Explicitly traverse any index expressions on reference-like nodes.
        # VarRef.children() (and similar) do not include indices, so we must
        # walk them here to catch variable references used in IndexOffset etc.
        if isinstance(expr, (VarRef, ParamRef, MultiplierRef)):
            for idx in expr.indices:
                if isinstance(idx, Expr):
                    _walk(idx)

        for child in expr.children():
            _walk(child)

    for eq_def in model_ir.equations.values():
        lhs, rhs = eq_def.lhs_rhs
        _walk(lhs)
        _walk(rhs)
        if eq_def.condition is not None:
            _walk(eq_def.condition)

    # Include the objective variable (e.g., 'minimize r' references 'r')
    if model_ir.objective and model_ir.objective.objvar:
        referenced.add(model_ir.objective.objvar.lower())
    # Walk objective expression if present
    if model_ir.objective and model_ir.objective.expr:
        _walk(model_ir.objective.expr)

    return referenced


def _collect_symbolref_names(expr: Expr) -> set[str]:
    """Collect all SymbolRef names in an expression tree.

    Used to determine which free index names appear in a condition expression.
    """
    result: set[str] = set()
    if isinstance(expr, SymbolRef):
        result.add(expr.name)
    for child in expr.children():
        result.update(_collect_symbolref_names(child))
    return result


def _find_variable_access_condition(
    var_name: str,
    var_domain: tuple[str, ...],
    model_ir: ModelIR,
) -> Expr | None:
    """Detect the common dollar condition under which a variable is accessed.

    Walks all equations in the model to find where VarRef(var_name, ...) appears.
    If the variable is consistently accessed inside Sum/Prod nodes whose bound
    indices overlap with the variable's domain AND those Sum/Prod nodes carry a
    dollar condition, that condition is extracted and returned.

    This handles the common GAMS pattern where a variable appears only inside
    conditioned aggregations like::

        sum(w$(td(w,t)), x(w,t))   →  condition td(w,t)
        prod(w$(td(w,t)), f(x))    →  condition td(w,t)

    When ALL appearances of the variable across ALL equations share a common
    condition (structurally identical AST), that condition is returned.

    Args:
        var_name: Name of the variable to check (e.g., "x")
        var_domain: Variable's domain indices (e.g., ("w", "t"))
        model_ir: Model IR with equation definitions

    Returns:
        The common access condition (Expr), or None if no common condition exists.
    """
    if not var_domain:
        return None

    var_domain_set = set(var_domain)
    collected_conditions: list[Expr] = []
    found_unconditioned = False

    for _eq_name, eq_def in model_ir.equations.items():
        lhs, rhs = eq_def.lhs_rhs
        # Check both sides of the equation
        for side_expr in (lhs, rhs):
            conditions = _collect_access_conditions(
                side_expr, var_name, var_domain_set, has_enclosing_condition=False
            )
            if conditions is None:
                # Variable not found in this expression — skip
                continue
            if not conditions:
                # Variable found with no enclosing condition — no common condition possible
                found_unconditioned = True
            else:
                collected_conditions.extend(conditions)

    if found_unconditioned or not collected_conditions:
        return None

    # Check if all conditions are structurally identical
    first = collected_conditions[0]
    if all(repr(c) == repr(first) for c in collected_conditions):
        # Issue #730: Validate that all free indices in the condition are within
        # the variable's domain.  If the condition references indices from the
        # equation domain that are NOT in the variable domain, the condition
        # cannot be used — it would produce bare/uncontrolled indices in GAMS.
        # Example: pls(r) accessed in sum(r$(ri(r,i)), pls(r)) produces
        # condition ri(r,i), but 'i' is not in pls's domain (r,).
        #
        # Issue #730 review: Only consider SymbolRef names that are actual
        # set/alias index variables, not literal element labels.  The parser
        # wraps both free indices and literal elements as SymbolRef, so
        # conditions like arc('a',i) would be incorrectly rejected if 'a'
        # (a constant element) were treated as a free index.
        all_symbolrefs = _collect_symbolref_names(first)
        known_indices = set(model_ir.sets.keys()) | set(model_ir.aliases.keys())
        cond_indices = all_symbolrefs & known_indices
        if cond_indices - var_domain_set:
            return None
        return first

    return None


def _collect_access_conditions(
    expr: Expr,
    var_name: str,
    var_domain_set: set[str],
    has_enclosing_condition: bool,
) -> list[Expr] | None:
    """Recursively collect the nearest guarding condition for each variable access.

    Walks the expression tree looking for VarRef nodes matching *var_name*.
    When a variable access is found inside a conditioned Sum/Prod whose bound
    indices overlap the variable's domain, the **nearest** (innermost) such
    condition is returned.

    Note: only the single nearest condition is captured per access point.
    If a variable is nested inside multiple conditioned aggregations
    (e.g., ``sum(i$c1, sum(j$c2, x(i,j)))``), only the innermost
    condition (``c2``) is returned.  The caller in
    ``_find_variable_access_condition`` then checks whether all collected
    conditions are structurally identical before using one as the equation's
    dollar condition.  This is sufficient for the common GAMS pattern where
    a single condition guards all accesses to a variable.

    Returns:
        A list of condition Exprs (one per access point found), or ``None``
        if the variable is not found in this subtree.  An empty list ``[]``
        means the variable was found with no guarding condition.

    Args:
        expr: Expression to walk
        var_name: Variable name to search for
        var_domain_set: Set of the variable's domain index names
        has_enclosing_condition: Whether we are already inside a conditioned
            Sum/Prod that binds a relevant index
    """
    if isinstance(expr, VarRef):
        if expr.name == var_name:
            # Found the variable — empty list signals "found, caller supplies condition"
            return []
        return None

    if isinstance(expr, (Sum, Prod)):
        # Check if this Sum/Prod binds indices that overlap with the variable's domain
        bound_set = set(expr.index_sets)
        overlaps = bool(bound_set & var_domain_set)

        if overlaps and expr.condition is not None:
            # This Sum/Prod has a condition and binds a relevant index.
            # Only walk the body — the condition expression itself is not a
            # variable-access context and must not be searched (Sum.children()
            # yields [condition, body], so we use expr.body directly).
            results: list[Expr] = []
            child_result = _collect_access_conditions(
                expr.body, var_name, var_domain_set, has_enclosing_condition=True
            )
            if child_result is not None:
                if not child_result:
                    # Found variable in body with no extra conditions from further nesting
                    # The condition for this access is the current Sum/Prod condition
                    results.append(expr.condition)
                else:
                    results.extend(child_result)
            return results if results else None
        else:
            # No relevant condition — walk only the body (skip condition child
            # to avoid false positives from variables appearing in conditions).
            child_result = _collect_access_conditions(
                expr.body, var_name, var_domain_set, has_enclosing_condition
            )
            if child_result is None:
                return None  # variable not found
            if not child_result:
                # Variable found with no additional guarding condition from
                # this Sum/Prod context; propagate upward so callers know the
                # variable was found (they will supply the enclosing condition).
                return []
            return child_result

    # For all other expression types, walk children
    other_results: list[Expr] = []
    found_any = False
    for child in expr.children():
        child_result = _collect_access_conditions(
            child, var_name, var_domain_set, has_enclosing_condition
        )
        if child_result is not None:
            found_any = True
            if not child_result and not has_enclosing_condition:
                # Found variable with no condition
                return []
            other_results.extend(child_result)

    if found_any:
        return other_results
    return None


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


def build_stationarity_equations(
    kkt: KKTSystem, config: Config | None = None
) -> dict[str, EquationDef]:
    """Build stationarity equations for all variable instances except objvar.

    For indexed variables, generates indexed equations with domains.
    For scalar variables, generates scalar equations.

    After assembly, each stationarity expression is simplified using the
    configured simplification mode (default: "advanced").  This eliminates
    trivial terms such as ``0 * multiplier``, ``sum(i, 0)``, etc.

    Stationarity condition for variable x(i):
        ∂f/∂x(i) + Σ_j [∂h_j/∂x(i) · ν_j] + Σ_k [∂g_k/∂x(i) · λ_k]
        - π^L(i) + π^U(i) = 0

    Args:
        kkt: KKT system with gradient, Jacobians, and multipliers
        config: Optional configuration (controls simplification level)

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

    # Issue #742: Filter out variables that don't appear in any equation body
    # or the objective. Unreferenced variables (e.g., dummy/reporting variables
    # like dumshr, dumtg) produce trivial 0=0 stationarity equations that cause
    # GAMS Error 69/483. Apply when there are equations or an objective to reference.
    if kkt.model_ir.equations or kkt.model_ir.objective:
        referenced_vars = _collect_referenced_variable_names(kkt.model_ir)
        var_groups = {
            name: insts for name, insts in var_groups.items() if name.lower() in referenced_vars
        }
        # Store on KKT system so the emitter can also filter variable declarations
        kkt.referenced_variables = referenced_vars

    # Resolve simplification mode once for all equations
    simp_mode = get_simplification_mode(config)

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
                    stat_expr = apply_simplification(stat_expr, simp_mode)
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
                stat_expr = apply_simplification(stat_expr, simp_mode)

                # Issue #724: Detect if the variable is only accessed under a
                # common dollar condition (e.g., td(w,t)).  If so, add that
                # condition to the stationarity equation to prevent GAMS from
                # generating empty equation instances, and record that the
                # excluded variable instances need to be fixed.
                access_cond = _find_variable_access_condition(
                    var_name, var_def.domain, kkt.model_ir
                )

                stationarity[stat_name] = EquationDef(
                    name=stat_name,
                    domain=var_def.domain,  # Use same domain as variable
                    relation=Rel.EQ,
                    condition=access_cond,
                    lhs_rhs=(stat_expr, Const(0.0)),
                )

                # Store the condition on the KKT system for the emitter to use
                # when generating .fx statements for excluded variable instances
                if access_cond is not None:
                    kkt.stationarity_conditions[var_name] = access_cond
        else:
            # Scalar variable: generate scalar stationarity equation
            if len(instances) != 1:
                raise ValueError(f"Scalar variable {var_name} has {len(instances)} instances")

            col_id, var_indices = instances[0]
            stat_name = f"stat_{var_name}"
            stat_expr = _build_stationarity_expr(kkt, col_id, var_name, var_indices, skip_eq)
            stat_expr = apply_simplification(stat_expr, simp_mode)
            stationarity[stat_name] = EquationDef(
                name=stat_name,
                domain=(),  # Empty domain for scalar
                relation=Rel.EQ,
                lhs_rhs=(stat_expr, Const(0.0)),
            )

    # Collect multiplier names that actually appear in simplified stationarity equations.
    # After simplification, terms like 0 * nu_foo are eliminated, so those multipliers
    # no longer appear. The emitter uses this set to skip unreferenced multipliers.
    referenced_mults: set[str] = set()
    for eq_def in stationarity.values():
        lhs, _ = eq_def.lhs_rhs
        _collect_multiplier_refs(lhs, referenced_mults)
    kkt.referenced_multipliers = referenced_mults

    return stationarity


def _collect_multiplier_refs(expr: Expr, result: set[str]) -> None:
    """Walk an expression tree and collect all MultiplierRef names."""
    if isinstance(expr, MultiplierRef):
        result.add(expr.name)
        # Explicitly traverse index expressions (MultiplierRef.children()
        # does not yield indices). Mirrors the fix in
        # _collect_referenced_variable_names for consistency.
        for idx in expr.indices:
            if isinstance(idx, Expr):
                _collect_multiplier_refs(idx, result)
    for child in expr.children():
        _collect_multiplier_refs(child, result)


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
    # Issue #620: Pass domain as equation_domain for subset/superset substitution
    return _replace_indices_in_expr(
        grad_component, domain, element_to_set, kkt.model_ir, equation_domain=domain
    )


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


def _build_constraint_element_mapping(
    base_element_to_set: dict[str, str],
    constraint_indices: tuple[str, ...],
    constraint_domain: tuple[str, ...],
) -> ChainMap[str, str]:
    """Build constraint-specific element-to-set mapping.

    Issue #649: When a constraint has multiple indices from the same underlying set
    (e.g., maxdist(i,j) where both i and j iterate over the same set), we need to
    map element labels to their specific position in the constraint domain.

    This function creates a lightweight overlay using ChainMap that checks
    constraint-specific overrides first, then falls back to the base mapping.
    This avoids copying the entire base mapping for each constraint.

    Args:
        base_element_to_set: Base mapping from variable instances
        constraint_indices: Element indices for the constraint row (e.g., ("1", "2"))
        constraint_domain: Constraint domain names (e.g., ("i", "j"))

    Returns:
        ChainMap with constraint overrides checked first, then base mapping

    Example:
        base_element_to_set = {"1": "i", "2": "i", "3": "i", ...}
        constraint_indices = ("1", "2")
        constraint_domain = ("i", "j")

        Returns: ChainMap({"1": "i", "2": "j"}, base_element_to_set)
        # "2" now maps to "j" because it's at position 1 in the constraint
        # "3" still maps to "i" via fallback to base_element_to_set
    """
    # Build constraint-specific overrides (small dict with just the constraint indices)
    overrides: dict[str, str] = {}
    if len(constraint_indices) == len(constraint_domain):
        for elem, domain_name in zip(constraint_indices, constraint_domain, strict=True):
            overrides[elem] = domain_name

    # Use ChainMap for O(1) lookup with lazy fallback to base mapping
    return ChainMap(overrides, base_element_to_set)


def _replace_indices_in_expr(
    expr: Expr,
    domain: tuple[str, ...],
    element_to_set: Mapping[str, str] | None = None,
    model_ir: ModelIR | None = None,
    equation_domain: tuple[str, ...] | None = None,
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
        equation_domain: The stationarity equation's domain for subset substitution
                         (Issue #620). When provided, superset indices are replaced
                         with subset indices from the equation domain.
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
                    # Issue #666: Check if variable is defined over a subset of the
                    # stationarity equation domain. If so, preserve the subset index
                    # rather than substituting the superset index.
                    # E.g., h(t) in stat_e(i) where t(i): keep h(t), don't make h(i).
                    if var_domain and equation_domain and model_ir:
                        preserved_indices = _preserve_subset_var_indices(
                            var_domain, equation_domain, model_ir
                        )
                        if preserved_indices is not None:
                            return VarRef(var_ref.name, preserved_indices)
                    new_indices = _replace_matching_indices(
                        str_indices,
                        element_to_set,
                        declared_domain=var_domain,
                        equation_domain=equation_domain,
                        model_ir=model_ir,
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
                    # Use parameter domain for disambiguation (Issue #572)
                    # For parameters, prefer_declared_domain=True ensures the parameter's
                    # declared domain takes precedence over constraint-specific mappings.
                    param_domain = None
                    if model_ir and param_ref.name in model_ir.params:
                        param_domain = model_ir.params[param_ref.name].domain
                    new_indices = _replace_matching_indices(
                        str_indices,
                        element_to_set,
                        declared_domain=param_domain,
                        equation_domain=equation_domain,
                        model_ir=model_ir,
                        prefer_declared_domain=True,  # Issue #572: Trust parameter domain
                    )
                    return ParamRef(param_ref.name, new_indices)
                elif len(param_ref.indices) == len(domain):
                    return ParamRef(param_ref.name, domain)
            return expr
        case MultiplierRef() as mult_ref:
            if mult_ref.indices and domain:
                if element_to_set:
                    str_indices = mult_ref.indices_as_strings()
                    new_indices = _replace_matching_indices(
                        str_indices,
                        element_to_set,
                        equation_domain=equation_domain,
                        model_ir=model_ir,
                    )
                    return MultiplierRef(mult_ref.name, new_indices)
                elif len(mult_ref.indices) == len(domain):
                    return MultiplierRef(mult_ref.name, domain)
            return expr
        case Binary(op, left, right):
            new_left = _replace_indices_in_expr(
                left, domain, element_to_set, model_ir, equation_domain
            )
            new_right = _replace_indices_in_expr(
                right, domain, element_to_set, model_ir, equation_domain
            )
            return Binary(op, new_left, new_right)
        case Unary(op, child):
            new_child = _replace_indices_in_expr(
                child, domain, element_to_set, model_ir, equation_domain
            )
            return Unary(op, new_child)
        case Call(func, args):
            new_args = tuple(
                _replace_indices_in_expr(arg, domain, element_to_set, model_ir, equation_domain)
                for arg in args
            )
            return Call(func, new_args)
        case Sum(index_sets, body, condition) | Prod(index_sets, body, condition):
            # Recursively process body and condition to replace element-specific indices
            new_body = _replace_indices_in_expr(
                body, domain, element_to_set, model_ir, equation_domain
            )
            new_condition = (
                _replace_indices_in_expr(
                    condition, domain, element_to_set, model_ir, equation_domain
                )
                if condition is not None
                else None
            )
            if new_body is not body or new_condition is not condition:
                return type(expr)(index_sets, new_body, new_condition)
            return expr
        case DollarConditional(value_expr, condition):
            # Issue #720: Handle DollarConditional from collapsed conditional sums
            new_value = _replace_indices_in_expr(
                value_expr, domain, element_to_set, model_ir, equation_domain
            )
            new_cond = _replace_indices_in_expr(
                condition, domain, element_to_set, model_ir, equation_domain
            )
            if new_value is not value_expr or new_cond is not condition:
                return DollarConditional(value_expr=new_value, condition=new_cond)
            return expr
        case SymbolRef() as sym_ref:
            # Issue #730: Handle bare symbol references (e.g., SymbolRef("rural"))
            # that appear as arguments in Call nodes like gamma(j, r).
            # After _substitute_indices converts SymbolRef("r") → SymbolRef("rural"),
            # we need to convert back: SymbolRef("rural") → SymbolRef("r").
            if element_to_set and sym_ref.name in element_to_set:
                mapped = element_to_set[sym_ref.name]
                if mapped != sym_ref.name:
                    return SymbolRef(mapped)
            return expr
        case SetMembershipTest() as smt:
            # Issue #730: Handle set membership tests like im(i) or ri(r,i).
            # The indices are Expr nodes that may contain SymbolRef with concrete
            # element values needing replacement.
            new_idx = tuple(
                _replace_indices_in_expr(idx, domain, element_to_set, model_ir, equation_domain)
                for idx in smt.indices
            )
            if new_idx != smt.indices:
                return SetMembershipTest(smt.set_name, new_idx)
            return expr
        case _:
            return expr


def _preserve_subset_var_indices(
    var_domain: tuple[str, ...],
    equation_domain: tuple[str, ...],
    model_ir: ModelIR,
) -> tuple[str, ...] | None:
    """Preserve subset indices for variables defined over subsets.

    Issue #666: When a variable is defined over a subset (e.g., h(t) where t(i))
    and appears in a stationarity equation indexed over the superset (stat_e(i)),
    we must preserve the subset index rather than substituting the superset.

    This prevents GAMS domain violations like h(i) when h is only defined over t.

    Args:
        var_domain: The variable's declared domain (e.g., ("t",))
        equation_domain: The stationarity equation's domain (e.g., ("i",))
        model_ir: Model IR for looking up set definitions

    Returns:
        The variable's domain if it should be preserved (i.e., if at least one
        of its domain sets is a subset of the equation domain), None otherwise.

    Example:
        Variable h(t) where t(i) is a subset of i.
        In stat_e(i), the derivative includes h("light-ind").
        Instead of replacing with h(i), we preserve h(t).
    """
    # Check if any of the variable's domain sets are subsets of the equation domain.
    # If so, preserve the variable's declared domain indices; otherwise, return None.
    if not equation_domain:
        return None

    equation_domain_lower = {s.lower() for s in equation_domain}

    for var_set in var_domain:
        var_set_def = model_ir.sets.get(var_set)
        if not var_set_def or not hasattr(var_set_def, "domain") or not var_set_def.domain:
            continue
        # var_set is defined as a subset of its domain sets
        for parent_set in var_set_def.domain:
            # Check if parent_set is in the equation domain (case-insensitive)
            if parent_set.lower() in equation_domain_lower:
                # At least one subset/superset relationship found: preserve var_domain
                return var_domain

    # No relevant subset/superset relationship found
    return None


def _replace_matching_indices(
    indices: tuple[str, ...],
    element_to_set: Mapping[str, str],
    declared_domain: tuple[str, ...] | None = None,
    equation_domain: tuple[str, ...] | None = None,
    model_ir: ModelIR | None = None,
    prefer_declared_domain: bool = False,
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

    When equation_domain and model_ir are provided, handles subset/superset
    relationships. If a parameter is indexed over a superset (e.g., mu(s)) but
    the stationarity equation is indexed over a subset (e.g., stat_x(i) where
    i(s) is a subset of s), the superset index is replaced with the subset index.
    This prevents GAMS Error 149 "Set is not under control".

    Args:
        indices: Original indices (e.g., ("1", "a") or ("1", "cost"))
        element_to_set: Mapping from element labels to set names
        declared_domain: The declared domain of the symbol (for disambiguation)
        equation_domain: The domain of the stationarity equation (for subset substitution)
        model_ir: Model IR for looking up subset relationships via SetDef.domain
        prefer_declared_domain: If True, use declared_domain over element_to_set when
            both provide a mapping. Set to True for parameters (Issue #572), False for
            variables (Issue #649).

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
    # Build superset-to-subset mapping from equation domain if available.
    # For each set in the equation domain, check if it's a subset of another set.
    # E.g., if equation domain is ("i",) and i has domain=("s",), then s -> i.
    superset_to_subset: dict[str, str] = {}
    if equation_domain and model_ir:
        for eq_set in equation_domain:
            eq_set_def = model_ir.sets.get(eq_set)
            # Handle both SetDef objects and plain lists (from programmatic tests)
            if eq_set_def and hasattr(eq_set_def, "domain") and eq_set_def.domain:
                for parent_set in eq_set_def.domain:
                    superset_to_subset[parent_set.lower()] = eq_set

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
                    # Issue #620: Check if this set is a superset of an equation
                    # domain set. If so, substitute the subset index.
                    # E.g., mu(s) in stat_x(i) where i(s): replace s -> i.
                    if idx.lower() in superset_to_subset:
                        new_indices.append(superset_to_subset[idx.lower()])
                    else:
                        new_indices.append(idx)
                elif idx in element_to_set and not prefer_declared_domain:
                    # Issue #649: Use the element_to_set mapping for element labels.
                    # This is critical for constraint-specific mappings where the same
                    # element might map to different set names depending on position.
                    # E.g., for maxdist(i,j) with instance (1,2), element "2" should
                    # map to "j" (its constraint position), not "i" (the variable's domain).
                    # NOTE: Only applies when prefer_declared_domain=False (for VarRef).
                    # For ParamRef, we trust declared_domain (Issue #572).
                    mapped_set = element_to_set[idx]
                    # Issue #620: Check if mapped_set is a superset of equation domain
                    if mapped_set.lower() in superset_to_subset:
                        new_indices.append(superset_to_subset[mapped_set.lower()])
                    else:
                        new_indices.append(mapped_set)
                else:
                    # Issue #620: Check if the target_set is a superset of an
                    # equation domain set. If so, use the subset index instead.
                    # E.g., mu("cn") with declared_domain=("s",) in stat_x(i)
                    # where i(s): target_set "s" → substitute "i".
                    if target_set.lower() in superset_to_subset:
                        new_indices.append(superset_to_subset[target_set.lower()])
                    else:
                        # Issue #730: When the declared domain target is an alias
                        # or a set not in the equation domain, prefer the
                        # element_to_set mapping if it maps to a set that IS in the
                        # equation domain.  This fixes the case where a sum over an
                        # alias (e.g., j aliasing i) collapses and both positions of
                        # a parameter like a("agricult","agricult") should map to the
                        # same equation-domain index "i", not to the alias "j".
                        if (
                            equation_domain
                            and idx in element_to_set
                            and element_to_set[idx] in equation_domain
                            and target_set not in equation_domain
                        ):
                            new_indices.append(element_to_set[idx])
                        else:
                            new_indices.append(target_set)
        elif idx in element_to_set:
            # Replace element with its set name
            new_indices.append(element_to_set[idx])
        else:
            # Keep the index unchanged (it's a literal like "cost" or already a set name)
            new_indices.append(idx)
    return tuple(new_indices)


def _collect_free_indices(expr: Expr, model_ir: ModelIR) -> set[str]:
    """Collect all free (unbound) symbolic set indices in an expression.

    Walks the expression tree and returns the set of index names that appear
    in VarRef/ParamRef/MultiplierRef indices but are NOT bound by any enclosing
    Sum or Prod node.

    Only names that are known set or alias names (from model_ir) are considered
    indices. Literal strings (e.g. "domestic", "storage-c") and IndexOffset
    objects are excluded.

    Issue #670: Used to detect uncontrolled indices in stationarity derivative
    expressions that need to be wrapped in Sum nodes.
    """

    def _is_known_set(name: str) -> bool:
        # model_ir.sets and model_ir.aliases are CaseInsensitiveDicts whose
        # __contains__ already lowercases the key, so this is case-safe.
        return name in model_ir.sets or name in model_ir.aliases

    def _walk(e: Expr, bound: frozenset[str]) -> set[str]:
        # bound contains lowercase-normalized names; all returned names are also lowercase
        # so that set arithmetic with IR-derived domains (also lowercase) is correct.
        if isinstance(e, (VarRef, ParamRef, MultiplierRef)):
            free: set[str] = set()
            for idx in e.indices or ():
                if isinstance(idx, str) and _is_known_set(idx) and idx.lower() not in bound:
                    free.add(idx.lower())
            return free
        if isinstance(e, (Sum, Prod)):
            new_bound = bound | frozenset(s.lower() for s in e.index_sets)
            result = _walk(e.body, new_bound)
            if e.condition is not None:
                result |= _walk(e.condition, new_bound)
            return result
        if isinstance(e, Binary):
            return _walk(e.left, bound) | _walk(e.right, bound)
        if isinstance(e, Unary):
            return _walk(e.child, bound)
        if isinstance(e, Call):
            free = set()
            for arg in e.args:
                free |= _walk(arg, bound)
            return free
        if isinstance(e, DollarConditional):
            return _walk(e.condition, bound) | _walk(e.value_expr, bound)
        if isinstance(e, SetMembershipTest):
            # Walk the index expressions inside the membership test (e.g. rn(i) → walk i)
            free = set()
            for child_expr in e.indices:
                free |= _walk(child_expr, bound)
            return free
        if isinstance(e, SymbolRef):
            # A bare symbol reference used as an index (e.g. SymbolRef('i'))
            if _is_known_set(e.name) and e.name.lower() not in bound:
                return {e.name.lower()}
            return set()
        # Const, IndexOffset, etc. — no indices
        return set()

    return _walk(expr, frozenset())


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
                # Issue #649: Build constraint-specific element-to-set mapping.
                # When a constraint has multiple indices from the same underlying set
                # (e.g., maxdist(i,j) where both i,j iterate over the same set), we need
                # to map element labels to their specific position in the constraint domain.
                # For example, for maxdist(1,2) with domain (i,j):
                #   "1" -> "i" (position 0)
                #   "2" -> "j" (position 1)
                # This ensures x(1) - x(2) becomes x(i) - x(j), not x(i) - x(i).
                constraint_element_to_set = _build_constraint_element_mapping(
                    element_to_set, eq_indices, mult_domain
                )

                # Replace indices in derivative expression using constraint-aware mapping
                # Issue #620: Pass var_domain as equation_domain for subset substitution
                indexed_deriv = _replace_indices_in_expr(
                    derivative,
                    var_domain,
                    constraint_element_to_set,
                    kkt.model_ir,
                    equation_domain=var_domain,
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
                    # Partial overlap: domains share some indices but each has unique ones
                    # This happens when a constraint sums over a variable using different indices.
                    # Example: stiffness(j,k).. sum(i, s(i,k)*b(j,i)) =E= f(j,k)
                    #   - Variable s has domain ('i', 'k')
                    #   - Constraint stiffness has domain ('j', 'k')
                    #   - Shared: 'k', Extra in mult: 'j', Extra in var: 'i'
                    # The stationarity term should sum over the extra multiplier indices:
                    #   sum(j, derivative * nu_stiffness(j,k))
                    extra_mult_indices = mult_domain_set - var_domain_set
                    sum_indices = tuple(idx for idx in mult_domain if idx in extra_mult_indices)
                    if sum_indices:
                        term = Sum(sum_indices, term)

                # Issue #670: After domain-based sum wrapping, detect any remaining
                # free indices in the derivative expression that are not controlled by
                # either the stationarity equation domain or the multiplier domain.
                # These arise when the derivative contains indices from the original
                # constraint's inner sum that are outside both domains (cross-indexed
                # sum pattern). Wrap them in an additional Sum to avoid GAMS Error 149.
                controlled = var_domain_set | mult_domain_set
                free_in_deriv = _collect_free_indices(indexed_deriv, kkt.model_ir)
                uncontrolled = free_in_deriv - controlled
                if uncontrolled:
                    sum_indices = tuple(sorted(uncontrolled))
                    term = Sum(sum_indices, term)

                expr = Binary("+", expr, term)
        else:
            # Scalar constraint
            mult_name = name_func(eq_name_base)

            if mult_name in multipliers:
                mult_ref = MultiplierRef(mult_name, ())
                # Replace indices in derivative using element_to_set mapping
                # Issue #620: Pass var_domain as equation_domain for subset substitution
                indexed_deriv = _replace_indices_in_expr(
                    derivative, var_domain, element_to_set, kkt.model_ir, equation_domain=var_domain
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

    Issue #730: For scalar stationarity equations, indexed constraint contributions
    must be wrapped in Sum() over the constraint domain to avoid uncontrolled set
    indices.  Derivatives are converted from per-instance concrete indices to
    symbolic indices using the same element-to-set replacement logic as the
    indexed stationarity path.

    For each constraint that has a nonzero Jacobian entry at col_id:
    - Scalar constraints: add  derivative * multiplier
    - Indexed constraints: add  sum(domain, derivative * multiplier)

    For negated constraints (LE inequalities that complementarity negates),
    negate the Jacobian term to account for the negation.
    """
    if jacobian.index_mapping is None:
        return expr

    # Group Jacobian entries by constraint name (mirrors _add_indexed_jacobian_terms)
    constraint_entries: dict[str, list[tuple[int, int]]] = {}
    for row_id in range(jacobian.num_rows):
        derivative = jacobian.get_derivative(row_id, col_id)
        if derivative is None:
            continue

        eq_name, _ = jacobian.index_mapping.row_to_eq[row_id]

        if skip_eq and eq_name == skip_eq:
            continue

        if eq_name not in constraint_entries:
            constraint_entries[eq_name] = []
        constraint_entries[eq_name].append((row_id, col_id))

    # Build element-to-set mapping for index replacement (same as indexed path)
    # For scalar variables, domain is empty but we still need set membership info
    element_to_set = _build_element_to_set_mapping(kkt.model_ir, (), [(col_id, ())])

    for eq_name_base, entries in constraint_entries.items():
        mult_name = name_func(eq_name_base)
        if mult_name not in multipliers:
            continue

        row_id, _ = entries[0]
        derivative = jacobian.get_derivative(row_id, col_id)
        _, eq_indices = jacobian.index_mapping.row_to_eq[row_id]

        # Determine negation for this constraint
        negate = False
        if eq_name_base in kkt.complementarity_ineq:
            comp_pair = kkt.complementarity_ineq[eq_name_base]
            negate = comp_pair.negated and not comp_pair.is_max_constraint

        if eq_indices:
            # Indexed constraint: use symbolic indices with Sum() wrapping
            mult_domain = _get_constraint_domain(kkt, eq_name_base)
            if mult_domain:
                # Build constraint-specific element mapping
                constraint_element_to_set = _build_constraint_element_mapping(
                    element_to_set, eq_indices, mult_domain
                )
                # Replace concrete indices with symbolic set names.
                # Issue #730 review: pass mult_domain (not empty tuple) so
                # _replace_indices_in_expr's `if indices and domain:` guards
                # are satisfied and VarRef/ParamRef indices are lifted from
                # concrete elements to symbolic set names before Sum wrapping.
                indexed_deriv = _replace_indices_in_expr(
                    derivative,
                    mult_domain,
                    constraint_element_to_set,
                    kkt.model_ir,
                    equation_domain=mult_domain,
                )
                # Issue #730 review: carry the equation's own $-condition into
                # the Sum so that only indices for which a Jacobian row exists
                # contribute.  Without this, summing over the full mult_domain
                # re-introduces contributions for indices excluded by the
                # condition (e.g., taumdet(im)$(not sc(im))).
                eq_def = kkt.model_ir.equations.get(eq_name_base)
                indexed_condition: Expr | None = None
                if eq_def is not None and eq_def.condition is not None:
                    indexed_condition = _replace_indices_in_expr(
                        eq_def.condition,
                        mult_domain,
                        constraint_element_to_set,
                        kkt.model_ir,
                        equation_domain=mult_domain,
                    )
                mult_ref = MultiplierRef(mult_name, mult_domain)
                term: Expr = Binary("*", indexed_deriv, mult_ref)
                # Wrap in Sum over all constraint indices (scalar stationarity
                # has no own domain, so all constraint indices must be summed)
                if indexed_condition is not None:
                    term = Sum(mult_domain, term, condition=indexed_condition)
                else:
                    term = Sum(mult_domain, term)
            else:
                # Fallback: no domain info, use per-instance (shouldn't happen)
                mult_ref = MultiplierRef(mult_name, eq_indices)
                term = Binary("*", derivative, mult_ref)
        else:
            # Scalar constraint: direct term, no sum needed
            mult_ref = MultiplierRef(mult_name, ())
            term = Binary("*", derivative, mult_ref)

        if negate:
            expr = Binary("-", expr, term)
        else:
            expr = Binary("+", expr, term)

    return expr
