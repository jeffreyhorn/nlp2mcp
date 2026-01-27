"""Multiplier variable naming conventions for KKT system.

This module provides functions to generate consistent, collision-free names
for Lagrange multiplier variables in the KKT system.

Naming conventions:
- Equality multipliers (ν): nu_<eqname>
- Inequality multipliers (λ): lam_<eqname>
- Lower bound multipliers (π^L): piL_<varname>
- Upper bound multipliers (π^U): piU_<varname>

For indexed multipliers, the indices are preserved:
- nu_balance(i) for equation balance(i)
- lam_capacity(i,j) for inequality capacity(i,j)
- piL_x(i) for lower bound on x(i)
"""

from __future__ import annotations

import re


def _sanitize_index_for_identifier(index: str) -> str:
    """Sanitize an index value for use in a GAMS identifier.

    GAMS identifiers can only contain letters, digits, and underscores.
    This function replaces invalid characters with underscores.

    Args:
        index: Raw index value (e.g., "i-1", "node.1", "H2O")

    Returns:
        Sanitized index safe for use in identifiers

    Example:
        >>> _sanitize_index_for_identifier("i-1")
        'i_1'
        >>> _sanitize_index_for_identifier("node.1")
        'node_1'
        >>> _sanitize_index_for_identifier("H2O")
        'H2O'
    """
    # Replace any character that's not alphanumeric or underscore with underscore
    return re.sub(r"[^A-Za-z0-9_]", "_", index)


def create_eq_multiplier_name(eq_name: str) -> str:
    """Create multiplier name for an equality constraint.

    Format: nu_<eqname>

    Note: Indexed multipliers use the same base name as scalar ones.
    In GAMS, the multiplier variable inherits the domain from the equation
    it's paired with, so we don't include indices in the variable name.

    Args:
        eq_name: Name of the equality constraint

    Returns:
        Multiplier variable name

    Example:
        >>> create_eq_multiplier_name("balance")
        'nu_balance'
        >>> create_eq_multiplier_name("flow")
        'nu_flow'
    """
    return f"nu_{eq_name}"


def create_ineq_multiplier_name(eq_name: str) -> str:
    """Create multiplier name for an inequality constraint.

    Format: lam_<eqname>

    Note: Indexed multipliers use the same base name as scalar ones.
    In GAMS, the multiplier variable inherits the domain from the equation
    it's paired with, so we don't include indices in the variable name.

    Args:
        eq_name: Name of the inequality constraint

    Returns:
        Multiplier variable name

    Example:
        >>> create_ineq_multiplier_name("capacity")
        'lam_capacity'
        >>> create_ineq_multiplier_name("demand")
        'lam_demand'
    """
    return f"lam_{eq_name}"


def create_bound_lo_multiplier_name(var_name: str) -> str:
    """Create multiplier name for a lower bound constraint.

    Format: piL_<varname>

    Note: Indexed multipliers use the same base name as scalar ones.
    In GAMS, the multiplier variable inherits the domain from the bound
    constraint it's paired with, so we don't include indices in the variable name.

    Args:
        var_name: Name of the variable

    Returns:
        Multiplier variable name

    Example:
        >>> create_bound_lo_multiplier_name("x")
        'piL_x'
        >>> create_bound_lo_multiplier_name("y")
        'piL_y'
    """
    return f"piL_{var_name}"


def create_bound_up_multiplier_name(var_name: str) -> str:
    """Create multiplier name for an upper bound constraint.

    Format: piU_<varname>

    Note: Indexed multipliers use the same base name as scalar ones.
    In GAMS, the multiplier variable inherits the domain from the bound
    constraint it's paired with, so we don't include indices in the variable name.

    Args:
        var_name: Name of the variable

    Returns:
        Multiplier variable name

    Example:
        >>> create_bound_up_multiplier_name("x")
        'piU_x'
        >>> create_bound_up_multiplier_name("z")
        'piU_z'
    """
    return f"piU_{var_name}"


def create_bound_lo_multiplier_name_indexed(var_name: str, indices: tuple[str, ...]) -> str:
    """Create per-instance multiplier name for a lower bound constraint.

    Format: piL_<varname>_<idx1>_<idx2>...

    Used for non-uniform bounds where each element has a different bound value.
    Creates a scalar multiplier for each specific element.

    Index values are sanitized to ensure valid GAMS identifiers (replacing
    characters like '-' and '.' with underscores).

    Args:
        var_name: Name of the variable
        indices: Tuple of index values for this instance

    Returns:
        Per-instance multiplier variable name

    Example:
        >>> create_bound_lo_multiplier_name_indexed("x", ("i1",))
        'piL_x_i1'
        >>> create_bound_lo_multiplier_name_indexed("y", ("a", "b"))
        'piL_y_a_b'
        >>> create_bound_lo_multiplier_name_indexed("z", ("i-1",))
        'piL_z_i_1'
    """
    sanitized_indices = [_sanitize_index_for_identifier(idx) for idx in indices]
    indices_str = "_".join(sanitized_indices)
    return f"piL_{var_name}_{indices_str}"


def create_bound_up_multiplier_name_indexed(var_name: str, indices: tuple[str, ...]) -> str:
    """Create per-instance multiplier name for an upper bound constraint.

    Format: piU_<varname>_<idx1>_<idx2>...

    Used for non-uniform bounds where each element has a different bound value.
    Creates a scalar multiplier for each specific element.

    Index values are sanitized to ensure valid GAMS identifiers (replacing
    characters like '-' and '.' with underscores).

    Args:
        var_name: Name of the variable
        indices: Tuple of index values for this instance

    Returns:
        Per-instance multiplier variable name

    Example:
        >>> create_bound_up_multiplier_name_indexed("x", ("i1",))
        'piU_x_i1'
        >>> create_bound_up_multiplier_name_indexed("y", ("a", "b"))
        'piU_y_a_b'
        >>> create_bound_up_multiplier_name_indexed("z", ("i-1",))
        'piU_z_i_1'
    """
    sanitized_indices = [_sanitize_index_for_identifier(idx) for idx in indices]
    indices_str = "_".join(sanitized_indices)
    return f"piU_{var_name}_{indices_str}"


def detect_naming_collision(multiplier_names: set[str], variable_names: set[str]) -> list[str]:
    """Detect naming collisions between multipliers and existing variables.

    Checks if any generated multiplier name conflicts with an existing
    variable name in the model.

    Args:
        multiplier_names: Set of generated multiplier names
        variable_names: Set of existing variable names from the model

    Returns:
        List of colliding names (empty if no collisions)

    Example:
        >>> detect_naming_collision({"nu_x", "lam_y"}, {"x", "y", "nu_x"})
        ['nu_x']
    """
    collisions = []
    for mult_name in multiplier_names:
        if mult_name in variable_names:
            collisions.append(mult_name)
    return collisions


def resolve_collision(base_name: str, existing_names: set[str]) -> str:
    """Resolve a naming collision by adding a numeric suffix.

    Tries base_name_1, base_name_2, ... until an available name is found.

    Args:
        base_name: Original name that collided
        existing_names: Set of all existing names

    Returns:
        Unique name with numeric suffix

    Example:
        >>> resolve_collision("nu_x", {"nu_x", "nu_x_1"})
        'nu_x_2'
    """
    suffix = 1
    while True:
        candidate = f"{base_name}_{suffix}"
        if candidate not in existing_names:
            return candidate
        suffix += 1
