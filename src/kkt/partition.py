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

import logging
from dataclasses import dataclass, field

from src.ad.index_mapping import resolve_set_members
from src.ir.ast import (
    Binary,
    Expr,
    IndexOffset,
    LhsConditionalAssign,
    SetMembershipTest,
    SubsetIndex,
    SymbolRef,
)
from src.ir.model_ir import ModelIR
from src.ir.symbols import EquationDef, VarKind

logger = logging.getLogger(__name__)


@dataclass
class BoundDef:
    """Definition of a variable bound.

    Attributes:
        kind: Type of bound ('lo', 'up', 'fx')
        value: Numeric bound value. When ``expr`` is set, this is an unused
               placeholder (conventionally 0.0) — downstream code must use
               ``expr`` via :func:`complementarity._bound_expr` instead of
               ``Const(value)``.
        domain: Variable domain (for indexed variables)
        expr: Expression for parameter-assigned bounds (e.g., e.lo(t) = req(t)).
              When set, complementarity equations use this expression instead of
              ``Const(value)``. Currently only ``lo`` and ``up`` bounds support
              expression values; ``fx`` expression-based bounds are not wired
              into the KKT pipeline (see partition_constraints comments).
    """

    kind: str  # 'lo', 'up', 'fx'
    value: float  # placeholder (0.0) when expr is set; see docstring
    domain: tuple[str, ...] = ()
    expr: Expr | None = None


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
    # Use .keys() to get lowercase (canonical) variable names for consistency
    # with index_mapping.py which also uses .keys() for variable iteration.
    # This ensures bound multiplier keys match stationarity equation lookups.
    for var_name in model_ir.variables.keys():
        var_def = model_ir.variables[var_name]
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

        # Issue #923: Process expression-based bounds (lo_expr/lo_expr_map etc.)
        # These are bounds assigned via parameter expressions like e.lo(t) = req(t).
        # Note: fx_expr/fx_expr_map are NOT processed here — fixed variable
        # equalities are handled via normalized_bounds in ir/normalize.py, which
        # does not yet support expression-based .fx values.
        # Scalar expression bounds — skip if scalar or per-instance numeric
        # bounds already exist (per-instance bounds take precedence to avoid
        # a mixed state where the placeholder value=0.0 is used for instances
        # without numeric overrides).
        # Check for per-instance bounds using the variable's own lo_map/up_map
        # keys (O(per-var) instead of scanning the full bounds dict).
        has_indexed_lo = any((var_name, idx) in result.bounds_lo for idx in var_def.lo_map)
        has_indexed_up = any((var_name, idx) in result.bounds_up for idx in var_def.up_map)
        if var_def.lo_expr is not None:
            has_scalar_lo = (var_name, ()) in result.bounds_lo
            if not has_scalar_lo and not has_indexed_lo:
                result.bounds_lo[(var_name, ())] = BoundDef(
                    "lo", 0.0, var_def.domain, expr=var_def.lo_expr
                )
            elif has_scalar_lo:
                logger.warning(
                    "Variable '%s' has both numeric lo (%.6g) and lo_expr; "
                    "keeping numeric bound (last-write-wins not yet implemented).",
                    var_name,
                    result.bounds_lo[(var_name, ())].value,
                )
            elif has_indexed_lo:
                logger.warning(
                    "Skipping scalar lo_expr bound for '%s' because indexed numeric "
                    "lower bounds already exist; per-instance bounds take precedence.",
                    var_name,
                )
        if var_def.up_expr is not None:
            has_scalar_up = (var_name, ()) in result.bounds_up
            if not has_scalar_up and not has_indexed_up:
                result.bounds_up[(var_name, ())] = BoundDef(
                    "up", 0.0, var_def.domain, expr=var_def.up_expr
                )
            elif has_scalar_up:
                logger.warning(
                    "Variable '%s' has both numeric up (%.6g) and up_expr; "
                    "keeping numeric bound (last-write-wins not yet implemented).",
                    var_name,
                    result.bounds_up[(var_name, ())].value,
                )
            elif has_indexed_up:
                logger.warning(
                    "Skipping scalar up_expr bound for '%s' because indexed numeric "
                    "upper bounds already exist; per-instance bounds take precedence.",
                    var_name,
                )
        # Indexed expression bounds — only consolidate when the expr_map has
        # exactly one entry whose key matches var_def.domain (plain strings,
        # no IndexOffset/SubsetIndex). Otherwise warn and skip.
        _process_expr_map_bound(
            var_def.lo_expr_map,
            var_name,
            var_def.domain,
            "lo",
            result.bounds_lo,
            has_per_instance=has_indexed_lo,
            model_ir=model_ir,
        )
        _process_expr_map_bound(
            var_def.up_expr_map,
            var_name,
            var_def.domain,
            "up",
            result.bounds_up,
            has_per_instance=has_indexed_up,
            model_ir=model_ir,
        )

        # Issue #922: Synthesize implicit bounds from variable kind.
        # GAMS Positive Variable has implicit lo=0, Negative has up=0,
        # Binary has lo=0 and up=1. Only add if no explicit scalar bound
        # exists for that direction; indexed bounds may only cover a subset
        # of indices and should not suppress the implicit defaults.
        # Also check whether a consolidated scalar bound entry already exists
        # (e.g., synthesized from uniform indexed bounds). In that case, do
        # not overwrite it with an implicit bound from the variable kind.
        has_lo = var_def.lo is not None
        has_up = var_def.up is not None
        has_lo_scalar_key = (var_name, ()) in result.bounds_lo
        has_up_scalar_key = (var_name, ()) in result.bounds_up
        # If the variable is fixed (either via scalar .fx or an existing scalar
        # fx entry in bounds_fx), additional implicit lo/up bounds are redundant
        # and are therefore not synthesized.
        has_fx_scalar = var_def.fx is not None or (var_name, ()) in result.bounds_fx
        if not has_fx_scalar:
            if var_def.kind == VarKind.POSITIVE and not has_lo and not has_lo_scalar_key:
                result.bounds_lo[(var_name, ())] = BoundDef("lo", 0.0, var_def.domain)
            elif var_def.kind == VarKind.NEGATIVE and not has_up and not has_up_scalar_key:
                result.bounds_up[(var_name, ())] = BoundDef("up", 0.0, var_def.domain)
            elif var_def.kind == VarKind.BINARY:
                if not has_lo and not has_lo_scalar_key:
                    result.bounds_lo[(var_name, ())] = BoundDef("lo", 0.0, var_def.domain)
                if not has_up and not has_up_scalar_key:
                    result.bounds_up[(var_name, ())] = BoundDef("up", 1.0, var_def.domain)

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


def _is_subset_or_alias_of(candidate: str, parent: str, model_ir: ModelIR | None) -> bool:
    """Check whether `candidate` is a subset or alias resolving to `parent`.

    Used to accept up_expr_map / lo_expr_map keys that use a subset name
    (e.g., `cup`) where the variable's declared domain has the parent
    (e.g., `c`). Walks `SetDef.domain` parent chains and resolves aliases.
    Case-insensitive.
    """
    if model_ir is None:
        return False
    if candidate.lower() == parent.lower():
        return True
    # Resolve alias chain.
    seen: set[str] = set()
    cur = candidate
    while cur in model_ir.aliases and cur.lower() not in seen:
        seen.add(cur.lower())
        cur = model_ir.aliases[cur].target
    if cur.lower() == parent.lower():
        return True
    # Walk SetDef.domain (subset → parent chain).
    visited: set[str] = set()
    stack = [cur]
    while stack:
        name = stack.pop()
        if name.lower() in visited:
            continue
        visited.add(name.lower())
        set_def = model_ir.sets.get(name)
        if set_def is None:
            continue
        for parent_name in set_def.domain:
            if parent_name.lower() == parent.lower():
                return True
            stack.append(parent_name)
    return False


def _substitute_symbol_in_expr(expr: Expr, mapping: dict[str, str]) -> Expr:
    """Rename free SymbolRef / VarRef / ParamRef / IndexOffset bases using `mapping`.

    Used to rewrite bound expressions when up_expr_map keys use subset names
    (e.g., `upbnds(cup, r)` -> `upbnds(c, r)` so the consolidated bound binds
    against the variable's declared domain). Reuses the AD machinery's
    `_substitute_indices` for consistent behavior across all expression types.
    """
    if not mapping:
        return expr
    from src.ad.constraint_jacobian import _substitute_indices

    symbolic = tuple(mapping.keys())
    concrete = tuple(mapping.values())
    return _substitute_indices(expr, symbolic, concrete)


def _process_expr_map_bound(
    expr_map: dict,
    var_name: str,
    domain: tuple[str, ...],
    kind: str,
    target_dict: dict,
    *,
    has_per_instance: bool = False,
    model_ir: ModelIR | None = None,
) -> None:
    """Process an indexed expression-based bound map (lo_expr_map or up_expr_map).

    Only consolidates to a single (var_name, ()) entry when the expr_map has
    exactly one entry whose key is a tuple of plain strings matching var_def.domain
    (no IndexOffset/SubsetIndex). When the key uses subset/alias names that
    resolve to the variable's declared domain (e.g., `xcrop.up(r, cup)` for
    a variable `xcrop(r, c)` with `cup(c)`), accept the key, rewrite the
    expression to use the parent-domain index names, and wrap in a
    `LhsConditionalAssign` whose condition restricts the bound to the subset.

    Args:
        expr_map: The lo_expr_map or up_expr_map dict
        var_name: Variable name
        domain: Variable domain tuple
        kind: Bound kind ('lo' or 'up')
        target_dict: Target bounds dict (bounds_lo or bounds_up)
        has_per_instance: Whether per-instance numeric bounds already exist
            for this variable (precomputed by caller for O(1) lookup).
        model_ir: Model IR; required for subset/alias resolution. When omitted,
            the historical strict-equality matcher is used.
    """
    if not expr_map:
        return

    # Check for any existing bounds (scalar or per-instance) that would
    # conflict with a consolidated expression-based bound.
    has_scalar = (var_name, ()) in target_dict
    if has_scalar or has_per_instance:
        logger.warning(
            "Variable '%s' has a %s_expr_map override, but %s %s bound(s) "
            "are already recorded in the KKT bounds dictionary. Keeping the "
            "existing bound(s) and ignoring the expression-based bound.",
            var_name,
            kind,
            "a scalar" if has_scalar else "per-instance",
            kind,
        )
        return

    if len(expr_map) != 1:
        logger.warning(
            "Variable '%s' has %d entries in %s_expr_map; "
            "only single-entry uniform bounds are supported in KKT pipeline. Skipping.",
            var_name,
            len(expr_map),
            kind,
        )
        return

    indices, expr = next(iter(expr_map.items()))

    # Validate: all index elements must be plain strings matching the domain
    if len(indices) != len(domain):
        logger.warning(
            "Variable '%s' %s_expr_map key %s has %d indices but domain has %d. Skipping.",
            var_name,
            kind,
            indices,
            len(indices),
            len(domain),
        )
        return

    if any(isinstance(idx, (IndexOffset, SubsetIndex)) for idx in indices):
        logger.warning(
            "Variable '%s' %s_expr_map key %s contains IndexOffset/SubsetIndex; "
            "only plain-string domain indices are supported in KKT pipeline. Skipping.",
            var_name,
            kind,
            indices,
        )
        return

    # Validate that key values match domain names (e.g., key ("t",) matches
    # domain ("t",)). Compare case-insensitively since the IR uses
    # CaseInsensitiveDict and GAMS identifiers are case-insensitive.
    #
    # Subset/alias acceptance: when a key position uses a subset or alias of
    # the corresponding domain set (e.g., `xcrop.up(r, cup)` for a variable
    # declared `xcrop(r, c)` with `cup(c)`), accept the key, rewrite the
    # expression to use the parent index name, and add a SetMembershipTest
    # guard so the bound is only active for elements of the subset. This
    # preserves the GAMS source semantic: `xcrop.up(r, cup) = upbnds(cup, r)`
    # leaves `xcrop.up(r, c)` at its default (+inf) for c ∉ cup.
    rename_map: dict[str, str] = {}
    subset_guards: list[Expr] = []
    for idx, dom in zip(indices, domain, strict=True):
        idx_str = str(idx)
        if idx_str.lower() == dom.lower():
            continue
        if _is_subset_or_alias_of(idx_str, dom, model_ir):
            rename_map[idx_str] = dom
            # Add SetMembershipTest only if the key is a strict subset of
            # the parent (i.e., would actually filter the index space).
            # Aliases of the parent have the same members, so no guard is
            # needed (they're just renamings).
            if model_ir is not None and idx_str not in model_ir.aliases:
                subset_guards.append(SetMembershipTest(idx_str, (SymbolRef(dom),)))
            continue
        # Genuine mismatch — preserve the historical "skip" behavior.
        logger.warning(
            "Variable '%s' %s_expr_map key %s does not match domain %s. Skipping.",
            var_name,
            kind,
            indices,
            domain,
        )
        return

    if rename_map:
        expr = _substitute_symbol_in_expr(expr, rename_map)

    if subset_guards:
        condition: Expr = subset_guards[0]
        for guard in subset_guards[1:]:
            condition = Binary("and", condition, guard)
        expr = LhsConditionalAssign(rhs=expr, condition=condition)

    target_dict[(var_name, ())] = BoundDef(kind, 0.0, domain, expr=expr)


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
