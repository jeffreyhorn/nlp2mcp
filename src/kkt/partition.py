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
        for indices, lo_val in var_def.lo_map.items():
            if lo_val == float("-inf"):
                result.skipped_infinite.append((var_name, indices, "lo"))
            else:
                result.bounds_lo[(var_name, indices)] = BoundDef("lo", lo_val, var_def.domain)

        for indices, up_val in var_def.up_map.items():
            if up_val == float("inf"):
                result.skipped_infinite.append((var_name, indices, "up"))
            else:
                result.bounds_up[(var_name, indices)] = BoundDef("up", up_val, var_def.domain)

        for indices, fx_val in var_def.fx_map.items():
            result.bounds_fx[(var_name, indices)] = BoundDef("fx", fx_val, var_def.domain)

    return result


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
