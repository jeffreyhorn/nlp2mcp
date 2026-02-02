"""Constraint partitioning for KKT system assembly.

This module partitions the constraints of an NLP model into:
- Equality constraints h(x) = 0
- Inequality constraints g(x) ≤ 0
- Variable bounds lo ≤ x ≤ up

Key features:
- Excludes duplicate bounds from inequality list (Finding #1)
- Handles indexed bounds via lo_map/up_map/fx_map (Finding #2)
- Filters infinite bounds (±INF) to avoid meaningless multipliers
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.ad.index_mapping import resolve_set_members
from src.ir.model_ir import ModelIR
from src.ir.symbols import EquationDef


@dataclass
class BoundDef:
    """Definition of a variable bound.

    Attributes:
        kind: Type of bound ('lo', 'up', 'fx')
        value: Bound value
        domain: Variable domain (for indexed variables)
    """

    kind: str  # 'lo', 'up', 'fx'
    value: float
    domain: tuple[str, ...] = ()


@dataclass
class PartitionResult:
    """Result of constraint partitioning.

    Attributes:
        equalities: List of equality constraint names
        inequalities: List of inequality constraint names (EXCLUDES duplicates)
        bounds_lo: Lower bounds keyed by (var_name, indices)
        bounds_up: Upper bounds keyed by (var_name, indices)
        bounds_fx: Fixed values keyed by (var_name, indices)
        skipped_infinite: List of infinite bounds that were skipped
        duplicate_excluded: List of inequality names excluded as duplicates
    """

    equalities: list[str] = field(default_factory=list)
    inequalities: list[str] = field(default_factory=list)
    bounds_lo: dict[tuple[str, tuple], BoundDef] = field(default_factory=dict)
    bounds_up: dict[tuple[str, tuple], BoundDef] = field(default_factory=dict)
    bounds_fx: dict[tuple[str, tuple], BoundDef] = field(default_factory=dict)
    skipped_infinite: list[tuple[str, tuple, str]] = field(default_factory=list)
    duplicate_excluded: list[str] = field(default_factory=list)


def partition_constraints(model_ir: ModelIR) -> PartitionResult:
    """Partition constraints into equalities, inequalities, and bounds.

    This function performs enhanced constraint partitioning with:
    1. Duplicate bound exclusion (Finding #1): User-authored bounds that
       duplicate variable bounds are excluded from the inequality list
    2. Indexed bound support (Finding #2): Processes lo_map/up_map/fx_map
       for indexed variable bounds
    3. Infinite bound filtering: Skips ±INF bounds to avoid meaningless
       multipliers

    Args:
        model_ir: NLP model IR

    Returns:
        PartitionResult with partitioned constraints

    Example:
        >>> result = partition_constraints(model)
        >>> result.equalities  # ['balance', 'flow']
        >>> result.inequalities  # ['capacity', 'demand']
        >>> result.bounds_lo  # {('x', ('i1',)): BoundDef('lo', 0.0, ('i',))}
        >>> result.duplicate_excluded  # ['x_lo_bound']  # User wrote this
        >>> result.skipped_infinite  # [('y', (), 'up')]  # y.up = +INF
    """
    result = PartitionResult()

    # Equalities: equations with Rel.EQ
    result.equalities = list(model_ir.equalities)

    # Inequalities: equations with Rel.LE (normalized to ≤ 0)
    # BUT: EXCLUDE if they duplicate normalized_bounds (Finding #1 fix)
    for name in model_ir.inequalities:
        if name in model_ir.normalized_bounds:
            continue  # Skip auto-generated bound equations

        # Check if this inequality duplicates a bound (Finding #1)
        # Only check if the equation actually exists in the model
        # TODO: Currently non-functional - placeholder functions below always return False
        # TODO: Implement _is_user_authored_bound() to detect single-variable constraints
        # TODO: Implement _duplicates_variable_bound() to check against var bounds
        if name in model_ir.equations:
            if _is_user_authored_bound(model_ir.equations[name]) and _duplicates_variable_bound(
                model_ir, name
            ):
                result.duplicate_excluded.append(name)
                # CRITICAL: Do NOT append to inequalities list
                continue

        result.inequalities.append(name)

    # Bounds: iterate over ALL bound maps (Finding #2 fix)
    for var_name, var_def in model_ir.variables.items():
        # Scalar bounds (if any)
        if var_def.lo is not None:
            if var_def.lo == float("-inf"):
                result.skipped_infinite.append((var_name, (), "lo"))
            else:
                result.bounds_lo[(var_name, ())] = BoundDef("lo", var_def.lo, var_def.domain)

        if var_def.up is not None:
            if var_def.up == float("inf"):
                result.skipped_infinite.append((var_name, (), "up"))
            else:
                result.bounds_up[(var_name, ())] = BoundDef("up", var_def.up, var_def.domain)

        if var_def.fx is not None:
            result.bounds_fx[(var_name, ())] = BoundDef("fx", var_def.fx, var_def.domain)

        # Indexed bounds (Finding #2 fix)
        # Process lower and upper bound maps with shared helper
        _process_indexed_bounds(
            var_name=var_name,
            var_def=var_def,
            bound_map=var_def.lo_map,
            scalar_bound=var_def.lo,
            inf_sentinel=float("-inf"),
            kind="lo",
            target_dict=result.bounds_lo,
            skipped_infinite=result.skipped_infinite,
            model_ir=model_ir,
        )
        _process_indexed_bounds(
            var_name=var_name,
            var_def=var_def,
            bound_map=var_def.up_map,
            scalar_bound=var_def.up,
            inf_sentinel=float("inf"),
            kind="up",
            target_dict=result.bounds_up,
            skipped_infinite=result.skipped_infinite,
            model_ir=model_ir,
        )

        for indices, fx_val in var_def.fx_map.items():
            result.bounds_fx[(var_name, indices)] = BoundDef("fx", fx_val, var_def.domain)

    return result


def _process_indexed_bounds(
    var_name: str,
    var_def,
    bound_map: dict,
    scalar_bound: float | None,
    inf_sentinel: float,
    kind: str,
    target_dict: dict,
    skipped_infinite: list,
    model_ir: ModelIR,
) -> None:
    """Process indexed bounds with uniform consolidation logic.

    Check if all bound_map values are uniform (same finite value for ALL instances).
    If so, consolidate to a single indexed bound entry with () indices.
    Otherwise, create per-instance entries.

    Uniform consolidation is ONLY applied when:
    1. ALL values in bound_map are the same finite value (no infinite bounds)
    2. There is no scalar bound - otherwise keep entries separate
    3. The bound_map covers ALL variable instances (not a subset)

    Args:
        var_name: Variable name
        var_def: Variable definition with domain info
        bound_map: The lo_map or up_map to process
        scalar_bound: Scalar bound value (var_def.lo or var_def.up)
        inf_sentinel: Infinity value to filter (-inf for lo, +inf for up)
        kind: Bound kind ('lo' or 'up')
        target_dict: Target dictionary to store bounds (bounds_lo or bounds_up)
        skipped_infinite: List to append skipped infinite bounds
        model_ir: Model IR (for set definitions)
    """
    if not bound_map:
        return

    values = list(bound_map.values())
    finite_values = [v for v in values if v != inf_sentinel]
    has_infinite = len(finite_values) < len(values)
    # Treat unbounded scalar (lo=-inf or up=+inf) the same as no scalar bound,
    # since partition_constraints() skips these anyway. Note: only same-sign
    # infinity is checked (inf_sentinel is -inf for lo, +inf for up).
    has_scalar_bound = scalar_bound is not None and scalar_bound != inf_sentinel

    # Track infinite bounds (always do this; it is cheap and required for diagnostics)
    for indices, val in bound_map.items():
        if val == inf_sentinel:
            skipped_infinite.append((var_name, indices, kind))

    if finite_values:
        # Check if all finite values are the same
        all_same = all(v == finite_values[0] for v in finite_values)

        # Only attempt expensive coverage check when consolidation is otherwise possible
        covers_all_instances = False
        if all_same and not has_infinite and not has_scalar_bound:
            covers_all_instances = _check_covers_all_instances(var_def, bound_map, model_ir)

        can_consolidate = (
            all_same and not has_infinite and not has_scalar_bound and covers_all_instances
        )

        if can_consolidate:
            # Uniform: create single indexed entry with () indices
            target_dict[(var_name, ())] = BoundDef(kind, finite_values[0], var_def.domain)
        else:
            # Non-uniform: create per-instance entries
            for indices, val in bound_map.items():
                if val != inf_sentinel:
                    target_dict[(var_name, indices)] = BoundDef(kind, val, var_def.domain)


def _check_covers_all_instances(var_def, bound_map: dict, model_ir: ModelIR) -> bool:
    """Check if a bound map covers all instances of an indexed variable.

    Uses an efficient two-step approach:
    1. First, do a cheap cardinality check: compare len(bound_map) to the
       product of set sizes. If they don't match, return False immediately.
    2. If cardinalities match, verify that each key in bound_map corresponds
       to a valid instance (uses short-circuiting iteration).

    This avoids materializing all instances into a set, which can be expensive
    or cause OOM for variables with large domains.

    Handles aliases and list/tuple-backed sets via resolve_set_members().

    Args:
        var_def: Variable definition with domain info
        bound_map: The lo_map or up_map to check
        model_ir: Model IR (for set definitions)

    Returns:
        True if bound_map covers all variable instances, False otherwise
    """
    if not var_def.domain:
        # Scalar variable: bound_map should have exactly one entry with () key
        return len(bound_map) == 1 and () in bound_map

    # Step 1: Cheap cardinality check
    # Compute expected instance count from set sizes using resolve_set_members
    # which handles aliases and list/tuple-backed sets
    try:
        expected_count = 1
        resolved_members: list[set[str]] = []
        for set_name in var_def.domain:
            members, _ = resolve_set_members(set_name, model_ir)
            if not members:
                # Empty set means no instances expected
                return len(bound_map) == 0
            expected_count *= len(members)
            # Convert to set for O(1) membership checks
            resolved_members.append(set(members))

        # If counts don't match, it's definitely not full coverage
        if len(bound_map) != expected_count:
            return False

        # Step 2: Verify all bound_map keys are valid instances
        # Use short-circuiting: check each key exists in the Cartesian product
        # without materializing the full product
        for indices in bound_map.keys():
            if len(indices) != len(var_def.domain):
                return False
            for i, members_set in enumerate(resolved_members):
                if indices[i] not in members_set:
                    return False

        return True

    except (KeyError, AttributeError, ValueError):
        # If we can't access set information, assume not full coverage
        return False


def _is_user_authored_bound(eq_def: EquationDef) -> bool:
    """Check if an equation looks like a user-authored bound constraint.

    User-authored bounds are inequalities that constrain a single variable,
    e.g., "x(i) =L= 10" or "x(i) =G= 0".

    This is a heuristic check. More sophisticated detection could inspect
    the equation structure (single variable reference, constant RHS).

    Args:
        eq_def: Equation definition

    Returns:
        True if equation appears to be a user-authored bound
    """
    # TODO: Implement heuristic detection
    # For now, return False (conservative: don't exclude unless sure)
    # Future: Check if LHS is single VarRef and RHS is Const
    return False


def _duplicates_variable_bound(model_ir: ModelIR, eq_name: str) -> bool:
    """Check if an inequality duplicates a variable bound.

    This checks if the inequality constraint on a variable is redundant
    with the variable's declared bounds.

    Args:
        model_ir: Model IR
        eq_name: Equation name

    Returns:
        True if equation duplicates a variable bound
    """
    # TODO: Implement duplicate detection
    # For now, return False (conservative: don't exclude unless sure)
    # Future: Extract variable from equation, check against var_def.lo/up
    return False
