"""Detect equation instances with no variable references (empty equations).

Issue #1133: GAMS MCP refuses to pass empty equations (0 =E= 0) to PATH.
This module analyzes equation bodies to find instances where all variable-
referencing terms have zero coefficients, so the emitter can fix the
associated multipliers to 0.

The analysis is conservative: instances are only marked empty when we can
PROVE all variable coefficients are zero. Unknown/unevaluable cases are
left as non-empty (safe default).
"""

from __future__ import annotations

from src.ir.ast import (
    Binary,
    DollarConditional,
    Expr,
    ParamRef,
    SetMembershipTest,
    Sum,
    SymbolRef,
    VarRef,
)
from src.ir.model_ir import ModelIR


def detect_empty_equation_instances(
    model_ir: ModelIR,
    relevant_equations: set[str] | None = None,
) -> dict[str, set[tuple[str, ...]]]:
    """Find equation instances where no variable appears (all coefficients zero).

    For each equality equation, checks every domain instance to see if ALL
    variable-referencing terms have zero coefficients. Returns a mapping from
    equation name to the set of domain-value tuples that are empty.

    Args:
        model_ir: Model IR with equations, sets, parameters

    Returns:
        Dict mapping equation name → set of empty instance tuples.
        Only includes equations that have at least one empty instance.
    """
    result: dict[str, set[tuple[str, ...]]] = {}

    for eq_name in model_ir.equalities:
        if relevant_equations is not None and eq_name not in relevant_equations:
            continue
        eq_def = model_ir.equations.get(eq_name)
        if eq_def is None or not eq_def.domain:
            continue

        # Build the equation body (LHS - RHS)
        lhs, rhs = eq_def.lhs_rhs
        body = Binary("-", lhs, rhs)

        # Collect all VarRef nodes with their access context
        var_accesses = _collect_variable_accesses(body)

        if not var_accesses:
            # No variables at all — entire equation is empty for all instances
            instances = _enumerate_domain_instances(eq_def.domain, model_ir)
            if instances:
                result[eq_name] = instances
            continue

        # Check each domain instance
        instances = _enumerate_domain_instances(eq_def.domain, model_ir)
        empty_instances: set[tuple[str, ...]] = set()

        for inst in instances:
            index_map = dict(zip(eq_def.domain, inst, strict=True))
            if not _instance_has_any_variable(var_accesses, index_map, model_ir):
                empty_instances.add(inst)

        if empty_instances:
            result[eq_name] = empty_instances

    return result


class _VarAccess:
    """Describes how a variable is referenced in an equation."""

    __slots__ = ("var_name", "indices", "conditions", "sum_indices", "sum_coeffs")

    def __init__(
        self,
        var_name: str,
        indices: tuple,
        conditions: list[Expr],
        sum_indices: list[str],
        sum_coeffs: list[str],
    ):
        self.var_name = var_name
        self.indices = indices
        self.conditions = conditions  # Set membership / dollar conditions
        self.sum_indices = sum_indices  # Indices bound by enclosing sums
        self.sum_coeffs = sum_coeffs  # Parameter names that are coefficients


def _collect_variable_accesses(
    expr: Expr,
    conditions: list[Expr] | None = None,
    sum_indices: list[str] | None = None,
    sum_coeffs: list[str] | None = None,
) -> list[_VarAccess]:
    """Walk expression tree to find all VarRef nodes with their context."""
    if conditions is None:
        conditions = []
    if sum_indices is None:
        sum_indices = []
    if sum_coeffs is None:
        sum_coeffs = []

    results: list[_VarAccess] = []

    if isinstance(expr, VarRef):
        results.append(
            _VarAccess(
                expr.name,
                expr.indices,
                list(conditions),
                list(sum_indices),
                list(sum_coeffs),
            )
        )
    elif isinstance(expr, Sum):
        # Track sum indices and look for coefficient parameters
        new_sum_indices = sum_indices + list(expr.index_sets)
        new_sum_coeffs = list(sum_coeffs)
        # Check if sum has a condition (e.g., $bposs(cfq,c))
        new_conditions = list(conditions)
        if expr.condition is not None:
            new_conditions.append(expr.condition)
        # Look for ParamRef coefficients in the body
        _find_param_coeffs(expr.body, new_sum_coeffs)
        results.extend(
            _collect_variable_accesses(expr.body, new_conditions, new_sum_indices, new_sum_coeffs)
        )
    elif isinstance(expr, DollarConditional):
        new_conditions = conditions + [expr.condition]
        results.extend(
            _collect_variable_accesses(expr.value_expr, new_conditions, sum_indices, sum_coeffs)
        )
    elif isinstance(expr, Binary):
        # For multiplication, track ParamRef as coefficient
        new_coeffs = list(sum_coeffs)
        if expr.op == "*":
            _find_param_coeffs(expr, new_coeffs)
        results.extend(_collect_variable_accesses(expr.left, conditions, sum_indices, new_coeffs))
        results.extend(_collect_variable_accesses(expr.right, conditions, sum_indices, new_coeffs))
    else:
        for child in expr.children():
            results.extend(_collect_variable_accesses(child, conditions, sum_indices, sum_coeffs))

    return results


def _find_param_coeffs(expr: Expr, coeffs: list[str]) -> None:
    """Find ParamRef names that act as coefficients in the expression."""
    if isinstance(expr, ParamRef):
        coeffs.append(expr.name)
    elif isinstance(expr, Binary) and expr.op == "*":
        _find_param_coeffs(expr.left, coeffs)
        _find_param_coeffs(expr.right, coeffs)


def _instance_has_any_variable(
    var_accesses: list[_VarAccess],
    index_map: dict[str, str],
    model_ir: ModelIR,
) -> bool:
    """Check if any variable access is active for a given equation instance."""
    for access in var_accesses:
        if _access_is_active(access, index_map, model_ir):
            return True
    return False


def _access_is_active(
    access: _VarAccess,
    index_map: dict[str, str],
    model_ir: ModelIR,
) -> bool:
    """Check if a variable access has nonzero contribution at this instance.

    Conservative: returns True (active) unless we can prove it's zero.
    """
    # Check set membership conditions
    for cond in access.conditions:
        if isinstance(cond, SetMembershipTest):
            if not _check_set_membership(cond, index_map, model_ir):
                return False  # Condition is false → access is inactive
        # Other condition types: conservatively assume active
        # (we can't evaluate arbitrary expressions)

    # Check coefficient parameters
    # If all coefficient parameters are zero for this instance, the access
    # contributes nothing. But we only check this for sum-based accesses
    # where we can enumerate the sum domain.
    if access.sum_coeffs and access.sum_indices:
        if _all_coefficients_zero(access, index_map, model_ir):
            return False

    return True  # Conservatively active


def _check_set_membership(
    cond: SetMembershipTest,
    index_map: dict[str, str],
    model_ir: ModelIR,
) -> bool:
    """Check if a SetMembershipTest condition is true for the given indices.

    Returns True if membership can't be determined (conservative).
    """
    sdef = model_ir.sets.get(cond.set_name)
    if sdef is None:
        # Check alias
        adef = model_ir.aliases.get(cond.set_name)
        if adef:
            sdef = model_ir.sets.get(getattr(adef, "target", ""))
    if sdef is None:
        return True  # Unknown set, assume active

    members = sdef.members if hasattr(sdef, "members") else []
    if not members:
        return True  # Empty/dynamic set, can't evaluate → assume active

    # Resolve index values. For indices not in index_map (e.g., sum variables),
    # we check if ANY value of that index makes the condition true.
    resolved: list[str | None] = []
    for idx in cond.indices:
        if isinstance(idx, SymbolRef):
            val = index_map.get(idx.name) or index_map.get(idx.name.lower())
            resolved.append(val)  # None if from sum variable
        else:
            resolved.append(None)  # Complex index → wildcard

    # Check membership with wildcards
    # For 1D sets with a resolved value:
    if len(resolved) == 1:
        if resolved[0] is not None:
            return resolved[0] in members
        return True  # Can't resolve → assume active

    # Multi-dimensional: check if any member matches the resolved pattern
    for member in members:
        # Members may be stored as "a.b" dotted strings or tuples
        if isinstance(member, str) and "." in member:
            parts = member.split(".")
        elif isinstance(member, tuple):
            parts = list(member)
        else:
            parts = [member]

        if len(parts) != len(resolved):
            continue

        matches = True
        for res, part in zip(resolved, parts, strict=False):
            if res is not None and res != part:
                matches = False
                break
        if matches:
            return True  # Found a matching member

    return False  # No member matches → condition always false


def _all_coefficients_zero(
    access: _VarAccess,
    index_map: dict[str, str],
    model_ir: ModelIR,
) -> bool:
    """Check if all coefficient parameters are zero for this instance.

    For sum(p, ap(c,p)*z(p)) at c='vacuum-res': checks if
    ap('vacuum-res', p) is zero for ALL p values.

    Returns False (not all zero) if we can't determine (conservative).
    """
    for pname in access.sum_coeffs:
        pdef = model_ir.params.get(pname)
        if pdef is None or not hasattr(pdef, "values") or not pdef.values:
            return False  # Unknown/missing data → conservatively not all-zero

        # Check if any entry with matching equation-domain indices is nonzero
        for key, val in pdef.values.items():
            if not isinstance(key, tuple):
                key = (key,)
            # Check if this entry matches the equation instance
            matches_instance = True
            for idx_name, idx_val in index_map.items():
                # Find which position in the parameter key corresponds
                # to this equation index
                if pdef.domain:
                    for pos, d in enumerate(pdef.domain):
                        if d.lower() == idx_name.lower() and pos < len(key):
                            if key[pos] != idx_val:
                                matches_instance = False
                                break
            if matches_instance and val != 0:
                return False  # Found nonzero coefficient → not all zero

    return True  # All coefficients are zero


def _resolve_set_members(set_name: str, model_ir: ModelIR) -> list[str]:
    """Resolve set members, falling back to parent set for dynamic subsets."""
    sdef = model_ir.sets.get(set_name)
    if sdef is None:
        adef = model_ir.aliases.get(set_name)
        if adef:
            sdef = model_ir.sets.get(getattr(adef, "target", ""))
    if sdef is None:
        return []
    members = list(sdef.members) if hasattr(sdef, "members") else []
    if not members and getattr(sdef, "domain", None):
        # Dynamic subset — fall back to parent set
        for parent in sdef.domain:
            parent_members = _resolve_set_members(parent, model_ir)
            if parent_members:
                return parent_members
    return members


def _enumerate_domain_instances(
    domain: tuple[str, ...],
    model_ir: ModelIR,
) -> set[tuple[str, ...]]:
    """Enumerate all instances of an equation domain."""
    if not domain:
        return set()

    # Get members for each domain dimension, falling back to parent set
    # for dynamic subsets (consistent with resolve_set_members behavior).
    dim_members: list[list[str]] = []
    for d in domain:
        members = _resolve_set_members(d, model_ir)
        if not members:
            return set()  # Can't enumerate → return empty
        dim_members.append(members)

    # Cartesian product
    if len(dim_members) == 1:
        return {(m,) for m in dim_members[0]}

    # Multi-dimensional
    result: set[tuple[str, ...]] = set()
    _cartesian(dim_members, 0, [], result)
    return result


def _cartesian(
    dims: list[list[str]],
    pos: int,
    current: list[str],
    result: set[tuple[str, ...]],
) -> None:
    if pos == len(dims):
        result.add(tuple(current))
        return
    for m in dims[pos]:
        current.append(m)
        _cartesian(dims, pos + 1, current, result)
        current.pop()
