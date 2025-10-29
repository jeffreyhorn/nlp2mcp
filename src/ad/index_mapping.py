"""
Index Mapping and Alias Resolution for Sparse Jacobian Structure

This module provides utilities to map indexed variables and equations to dense
column/row IDs for Jacobian construction. It handles:
- Variable instance enumeration: (var_name, index_tuple) → column_id
- Equation instance enumeration: (eq_name, index_tuple) → row_id
- Alias resolution: Expanding aliased sets to their target set members
- Deterministic ordering: Sorted enumeration for reproducibility

Day 6 Scope:
-----------
- Enumerate all variable instances using ModelIR.sets and ModelIR.variables
- Enumerate all equation instances using ModelIR.equations
- Resolve aliases using ModelIR.aliases (check AliasDef.universe constraints)
- Create bijective mappings for Jacobian structure

Mathematical Background:
-----------------------
For a constraint system with indexed variables and equations:
- Variables: x(i,j) for i in I, j in J → maps to columns
- Equations: g(k) for k in K → maps to rows
- Jacobian J[row, col] = ∂g(k)/∂x(i,j)

The index mapping creates a deterministic ordering for both variables and equations,
allowing sparse storage of derivatives as J[row_id][col_id] = derivative_expr.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..ir.model_ir import ModelIR

from ..ir.symbols import AliasDef, VariableDef


@dataclass
class IndexMapping:
    """
    Bijective mapping between variable/equation instances and dense IDs.

    Attributes:
        var_to_col: Map (var_name, index_tuple) → column_id
        col_to_var: Map column_id → (var_name, index_tuple)
        eq_to_row: Map (eq_name, index_tuple) → row_id
        row_to_eq: Map row_id → (eq_name, index_tuple)
        num_vars: Total number of variable instances (columns)
        num_eqs: Total number of equation instances (rows)
    """

    var_to_col: dict[tuple[str, tuple[str, ...]], int] = field(default_factory=dict)
    col_to_var: dict[int, tuple[str, tuple[str, ...]]] = field(default_factory=dict)
    eq_to_row: dict[tuple[str, tuple[str, ...]], int] = field(default_factory=dict)
    row_to_eq: dict[int, tuple[str, tuple[str, ...]]] = field(default_factory=dict)
    num_vars: int = 0
    num_eqs: int = 0

    def get_col_id(self, var_name: str, indices: tuple[str, ...] = ()) -> int | None:
        """
        Get column ID for a variable instance.

        Args:
            var_name: Variable name
            indices: Index tuple (empty for scalar variables)

        Returns:
            Column ID, or None if not found
        """
        return self.var_to_col.get((var_name, indices))

    def get_row_id(self, eq_name: str, indices: tuple[str, ...] = ()) -> int | None:
        """
        Get row ID for an equation instance.

        Args:
            eq_name: Equation name
            indices: Index tuple (empty for scalar equations)

        Returns:
            Row ID, or None if not found
        """
        return self.eq_to_row.get((eq_name, indices))

    def get_var_instance(self, col_id: int) -> tuple[str, tuple[str, ...]] | None:
        """
        Get variable instance from column ID.

        Args:
            col_id: Column ID

        Returns:
            (var_name, index_tuple), or None if not found
        """
        return self.col_to_var.get(col_id)

    def get_eq_instance(self, row_id: int) -> tuple[str, tuple[str, ...]] | None:
        """
        Get equation instance from row ID.

        Args:
            row_id: Row ID

        Returns:
            (eq_name, index_tuple), or None if not found
        """
        return self.row_to_eq.get(row_id)


def resolve_set_members(set_or_alias_name: str, model_ir: ModelIR) -> tuple[list[str], str]:
    """
    Resolve a set or alias name to its concrete members.

    Handles alias resolution with universe constraints:
    - If name is a set: return its members directly
    - If name is an alias: resolve to target set, respecting universe

    Args:
        set_or_alias_name: Name of set or alias
        model_ir: Model IR containing sets and aliases

    Returns:
        Tuple of (members_list, resolved_set_name)

    Raises:
        ValueError: If set/alias not found or circular alias

    Examples:
        >>> # Direct set
        >>> resolve_set_members("i", model_ir)
        (["i1", "i2", "i3"], "i")

        >>> # Alias without universe
        >>> # alias(j, i) → resolves to i's members
        >>> resolve_set_members("j", model_ir)
        (["i1", "i2", "i3"], "i")

        >>> # Alias with universe
        >>> # alias(k, i) universe u → intersection of i and u
        >>> resolve_set_members("k", model_ir)
        (["i1", "i2"], "i")  # Only members also in u
    """
    # Check if it's an alias
    if set_or_alias_name in model_ir.aliases:
        alias_def = model_ir.aliases[set_or_alias_name]
        return _resolve_alias(alias_def, model_ir, visited=set())

    # Direct set lookup
    if set_or_alias_name in model_ir.sets:
        set_def = model_ir.sets[set_or_alias_name]
        return (set_def.members, set_or_alias_name)

    raise ValueError(
        f"Set or alias '{set_or_alias_name}' not found in ModelIR. "
        f"Available sets: {list(model_ir.sets.keys())}, "
        f"aliases: {list(model_ir.aliases.keys())}"
    )


def _resolve_alias(
    alias_def: AliasDef, model_ir: ModelIR, visited: set[str]
) -> tuple[list[str], str]:
    """
    Recursively resolve an alias to concrete members.

    Handles:
    - Alias chains: alias(a, b), alias(b, c) → resolve to c
    - Universe constraints: Only include members in universe set
    - Circular detection: Raise error if cycle detected

    Args:
        alias_def: Alias definition to resolve
        model_ir: Model IR
        visited: Set of alias names already visited (for cycle detection)

    Returns:
        Tuple of (members_list, target_set_name)

    Raises:
        ValueError: If circular alias or target not found
    """
    # Cycle detection
    if alias_def.name in visited:
        raise ValueError(
            f"Circular alias detected: {alias_def.name} already visited in chain. "
            f"Visited: {visited}"
        )

    visited.add(alias_def.name)

    # Resolve target (may be another alias)
    target_name = alias_def.target

    # If target is an alias, recursively resolve
    if target_name in model_ir.aliases:
        target_members, final_set = _resolve_alias(model_ir.aliases[target_name], model_ir, visited)
    # If target is a set, get its members
    elif target_name in model_ir.sets:
        target_members = model_ir.sets[target_name].members
        final_set = target_name
    else:
        raise ValueError(
            f"Alias '{alias_def.name}' targets '{target_name}' which is not found. "
            f"Available sets: {list(model_ir.sets.keys())}, "
            f"aliases: {list(model_ir.aliases.keys())}"
        )

    # Apply universe constraint if specified
    if alias_def.universe is not None:
        universe_members, _ = resolve_set_members(alias_def.universe, model_ir)
        # Intersection: only keep members that are in universe
        target_members = [m for m in target_members if m in universe_members]

    return (target_members, final_set)


def enumerate_variable_instances(var_def: VariableDef, model_ir: ModelIR) -> list[tuple[str, ...]]:
    """
    Enumerate all instances of a variable.

    For scalar variables: returns [()]
    For indexed variables: returns cross-product of domain set members

    Args:
        var_def: Variable definition with domain
        model_ir: Model IR containing set definitions

    Returns:
        List of index tuples (sorted for deterministic ordering)

    Examples:
        >>> # Scalar variable x
        >>> enumerate_variable_instances(VariableDef("x", ()), model_ir)
        [()]

        >>> # Indexed variable x(i) where i = {i1, i2}
        >>> enumerate_variable_instances(VariableDef("x", ("i",)), model_ir)
        [("i1",), ("i2",)]

        >>> # Two-dimensional x(i,j) where i = {i1, i2}, j = {j1, j2}
        >>> enumerate_variable_instances(VariableDef("x", ("i","j")), model_ir)
        [("i1","j1"), ("i1","j2"), ("i2","j1"), ("i2","j2")]
    """
    if not var_def.domain:
        # Scalar variable
        return [()]

    # Get members for each index set (resolve aliases if needed)
    index_members_list: list[list[str]] = []
    for set_name in var_def.domain:
        members, _ = resolve_set_members(set_name, model_ir)
        if not members:
            raise ValueError(
                f"Variable '{var_def.name}' uses domain set '{set_name}' which has no members"
            )
        index_members_list.append(members)

    # Generate cross-product of all index combinations
    instances = _cross_product(index_members_list)

    # Sort for deterministic ordering (lexicographic order)
    instances.sort()

    return instances


def enumerate_equation_instances(
    eq_name: str, eq_domain: tuple[str, ...], model_ir: ModelIR
) -> list[tuple[str, ...]]:
    """
    Enumerate all instances of an equation.

    Similar to variable enumeration but for equations.

    Args:
        eq_name: Equation name (for error messages)
        eq_domain: Domain tuple of set names
        model_ir: Model IR containing set definitions

    Returns:
        List of index tuples (sorted for deterministic ordering)

    Examples:
        >>> # Scalar equation
        >>> enumerate_equation_instances("obj", (), model_ir)
        [()]

        >>> # Indexed equation g(i)
        >>> enumerate_equation_instances("g", ("i",), model_ir)
        [("i1",), ("i2",)]
    """
    if not eq_domain:
        # Scalar equation
        return [()]

    # Get members for each index set (resolve aliases if needed)
    index_members_list: list[list[str]] = []
    for set_name in eq_domain:
        members, _ = resolve_set_members(set_name, model_ir)
        if not members:
            raise ValueError(
                f"Equation '{eq_name}' uses domain set '{set_name}' which has no members"
            )
        index_members_list.append(members)

    # Generate cross-product
    instances = _cross_product(index_members_list)

    # Sort for deterministic ordering
    instances.sort()

    return instances


def _cross_product(lists: list[list[str]]) -> list[tuple[str, ...]]:
    """
    Compute cross-product of multiple lists.

    Args:
        lists: List of lists to cross-product

    Returns:
        List of tuples representing all combinations

    Example:
        >>> _cross_product([["a", "b"], ["1", "2"]])
        [("a", "1"), ("a", "2"), ("b", "1"), ("b", "2")]
    """
    if not lists:
        return [()]

    if len(lists) == 1:
        return [(item,) for item in lists[0]]

    # Recursive cross-product
    first = lists[0]
    rest_product = _cross_product(lists[1:])

    result: list[tuple[str, ...]] = []
    for item in first:
        for rest_tuple in rest_product:
            result.append((item,) + rest_tuple)

    return result


def build_index_mapping(model_ir: ModelIR) -> IndexMapping:
    """
    Build complete index mapping for all variables and equations.

    Creates bijective mappings:
    - Variables → column IDs (sorted by variable name, then indices)
    - Equations → row IDs (sorted by equation name, then indices)

    Args:
        model_ir: Model IR with variables, equations, sets, and aliases

    Returns:
        IndexMapping with populated mappings

    Example:
        >>> mapping = build_index_mapping(model_ir)
        >>> mapping.get_col_id("x", ("i1",))
        0
        >>> mapping.get_row_id("g", ("i1",))
        0
    """
    mapping = IndexMapping()

    # Enumerate all variables (sorted by name for deterministic ordering)
    col_id = 0
    for var_name in sorted(model_ir.variables.keys()):
        var_def = model_ir.variables[var_name]
        instances = enumerate_variable_instances(var_def, model_ir)

        for indices in instances:
            # Store mappings
            mapping.var_to_col[(var_name, indices)] = col_id
            mapping.col_to_var[col_id] = (var_name, indices)
            col_id += 1

    mapping.num_vars = col_id

    # Enumerate all equations (sorted by name for deterministic ordering)
    row_id = 0
    for eq_name in sorted(model_ir.equations.keys()):
        eq_def = model_ir.equations[eq_name]
        instances = enumerate_equation_instances(eq_name, eq_def.domain, model_ir)

        for indices in instances:
            # Store mappings
            mapping.eq_to_row[(eq_name, indices)] = row_id
            mapping.row_to_eq[row_id] = (eq_name, indices)
            row_id += 1

    mapping.num_eqs = row_id

    return mapping
