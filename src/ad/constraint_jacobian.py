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
    from ..config import Config
    from ..ir.model_ir import ModelIR

from ..ir.ast import Const, Expr, IndexOffset
from ..ir.normalize import NormalizedEquation
from ..ir.symbols import EquationDef
from .ad_core import apply_simplification, get_simplification_mode
from .derivative_rules import differentiate_expr
from .index_mapping import build_index_mapping, enumerate_variable_instances, resolve_set_members
from .jacobian import JacobianStructure
from .sparsity import find_variables_in_expr


def _precompute_variable_instances(
    model_ir: ModelIR,
) -> list[tuple[str, list[tuple[str, ...]]]]:
    """Precompute all variable instances once, avoiding repeated enumeration.

    Returns:
        List of (var_name, var_instances) tuples, sorted by variable name.
        Each var_instances is a list of index tuples for that variable.
    """
    result = []
    for var_name in sorted(model_ir.variables.keys()):
        var_def = model_ir.variables[var_name]
        var_instances = enumerate_variable_instances(var_def, model_ir)
        result.append((var_name, var_instances))
    return result


def _is_zero_const(expr: Expr | None) -> bool:
    """Check if an expression is a zero constant."""
    return isinstance(expr, Const) and expr.value == 0


def _resolve_index_offsets(
    expr: Expr,
    model_ir: ModelIR,
    _domain_cache: dict[str, tuple[list[str], dict[str, int]] | None] | None = None,
) -> Expr:
    """Resolve IndexOffset nodes in VarRef/ParamRef indices to concrete domain elements.

    After _substitute_indices, an expression like k(t+1) with t→"1990" becomes
    k(IndexOffset("1990", Const(1.0), False)).  This function resolves the offset
    by looking up the variable's/parameter's domain set and finding the element at
    position ord("1990") + 1.

    If the resolved position is out of bounds, the VarRef is replaced with Const(0)
    because the variable instance doesn't exist (GAMS semantics for lead/lag beyond
    set boundaries).

    Args:
        expr: Expression with concrete IndexOffset nodes (after _substitute_indices)
        model_ir: Model IR for domain set lookup
        _domain_cache: Optional shared cache for resolved domain members and
            member→position maps. When provided, avoids redundant resolve_set_members()
            calls across multiple invocations (e.g., across equation instances).

    Returns:
        Expression with IndexOffset nodes resolved to plain string indices
    """
    from ..ir.ast import Binary, Call, ParamRef, Prod, Sum, Unary, VarRef

    # Use provided cache or create a new one for this call tree
    if _domain_cache is None:
        _domain_cache = {}

    def _get_domain_members(domain_set_name: str) -> tuple[list[str], dict[str, int]] | None:
        """Get (members, pos_map) for a domain set, with caching."""
        if domain_set_name in _domain_cache:
            return _domain_cache[domain_set_name]
        try:
            members, _ = resolve_set_members(domain_set_name, model_ir)
            pos_map = {m: i for i, m in enumerate(members)}
            result = (members, pos_map)
        except (ValueError, KeyError):
            result = None
        _domain_cache[domain_set_name] = result
        return result

    def _try_eval_offset(offset_expr) -> Const | None:
        """Try to evaluate a non-Const offset expression to a Const.

        Handles common GAMS intrinsics like ``ord(element)`` and ``card(set)``
        when the argument resolves to a concrete set element or set name, and
        negated forms like ``Unary('-', Call('ord', ...))``.
        """
        from ..ir.ast import Call, SymbolRef, Unary

        if isinstance(offset_expr, Const):
            return offset_expr

        # Handle Unary('-', inner) — e.g. -ord(l) after l is substituted
        if isinstance(offset_expr, Unary) and offset_expr.op == "-":
            inner_val = _try_eval_offset(offset_expr.child)
            if inner_val is not None:
                return Const(-inner_val.value)
            return None

        # Handle Binary('+'/'-'/'*', ...) for expressions like 1 - ord(l)
        if isinstance(offset_expr, Binary):
            left_val = _try_eval_offset(offset_expr.left)
            right_val = _try_eval_offset(offset_expr.right)
            if left_val is not None and right_val is not None:
                lv, rv = left_val.value, right_val.value
                if offset_expr.op == "+":
                    return Const(lv + rv)
                elif offset_expr.op == "-":
                    return Const(lv - rv)
                elif offset_expr.op == "*":
                    return Const(lv * rv)
            return None

        if not isinstance(offset_expr, Call):
            return None

        func_lower = offset_expr.func.lower()

        if func_lower == "ord" and len(offset_expr.args) == 1:
            arg = offset_expr.args[0]
            if isinstance(arg, SymbolRef):
                elem_name = arg.name
                # Search all sets for this element to find its 1-based position.
                # If the element appears in multiple sets at different positions,
                # treat as ambiguous and leave unresolved.
                matches: list[int] = []
                for sdef in model_ir.sets.values():
                    domain_info = _get_domain_members(sdef.name)
                    if domain_info is None:
                        continue
                    members, pos_map = domain_info
                    if elem_name in pos_map:
                        matches.append(pos_map[elem_name])
                if len(matches) == 1:
                    return Const(float(matches[0] + 1))  # 1-based
                if len(matches) > 1 and len(set(matches)) == 1:
                    # Same position in all matching sets — unambiguous
                    return Const(float(matches[0] + 1))  # 1-based
                # 0 matches or ambiguous positions — leave unresolved
                return None

        if func_lower == "card" and len(offset_expr.args) == 1:
            arg = offset_expr.args[0]
            if isinstance(arg, SymbolRef):
                domain_info = _get_domain_members(arg.name)
                if domain_info is not None:
                    return Const(float(len(domain_info[0])))
                return None

        return None

    def _resolve_idx(idx, domain_set_name: str | None):
        """Resolve a single index if it's an IndexOffset with a concrete base."""
        if not isinstance(idx, IndexOffset):
            return idx, True  # (resolved_idx, valid)
        base = idx.base
        offset_expr = idx.offset
        # Only resolve if the base looks like a concrete element (not a symbolic name)
        # and the offset is a numeric constant.
        # Try to evaluate symbolic offsets like ord(element) or -ord(element)
        # to a Const first.
        if not isinstance(offset_expr, Const):
            evaluated = _try_eval_offset(offset_expr)
            if evaluated is not None:
                offset_expr = evaluated
            else:
                return idx, True  # Can't resolve non-constant offset
        if domain_set_name is None:
            return idx, True  # No domain to resolve against
        # Look up domain members (cached)
        domain_info = _get_domain_members(domain_set_name)
        if domain_info is None:
            return idx, True  # Can't resolve this domain
        members, pos_map = domain_info
        if base not in pos_map:
            # base is still symbolic (e.g. "t" not yet substituted), skip
            return idx, True
        # Resolve: find position of base, add offset
        pos = pos_map[base]
        offset_val = offset_expr.value
        # Require an integer-valued numeric constant; avoid silent float→int truncation
        if not isinstance(offset_val, (int, float)):
            return idx, True  # Non-numeric constant offset; leave unresolved
        if isinstance(offset_val, float):
            if not offset_val.is_integer():
                return idx, True  # Non-integer float offset; leave unresolved
            offset_val = int(offset_val)
        new_pos = pos + offset_val
        if idx.circular:
            if not members:
                # Empty domain — no valid target for circular indexing
                return None, False
            new_pos = new_pos % len(members)
        if 0 <= new_pos < len(members):
            return members[new_pos], True
        else:
            # Out of bounds — this variable instance doesn't exist
            return None, False

    def _get_domain_for_ref(name: str, is_var: bool) -> tuple[str, ...]:
        """Get the domain tuple for a variable or parameter."""
        if is_var and name in model_ir.variables:
            return model_ir.variables[name].domain
        if not is_var and name in model_ir.params:
            param = model_ir.params[name]
            if hasattr(param, "domain"):
                return param.domain
        return ()

    if isinstance(expr, VarRef):
        domain = _get_domain_for_ref(expr.name, is_var=True)
        new_indices = []
        for i, idx in enumerate(expr.indices):
            domain_set = domain[i] if i < len(domain) else None
            resolved, valid = _resolve_idx(idx, domain_set)
            if not valid:
                # Out-of-bounds lead/lag → zero (GAMS convention)
                return Const(0)
            new_indices.append(resolved)
        return VarRef(expr.name, tuple(new_indices), expr.attribute)

    elif isinstance(expr, ParamRef):
        domain = _get_domain_for_ref(expr.name, is_var=False)
        new_indices = []
        for i, idx in enumerate(expr.indices):
            domain_set = domain[i] if i < len(domain) else None
            resolved, valid = _resolve_idx(idx, domain_set)
            if not valid:
                return Const(0)
            new_indices.append(resolved)
        return ParamRef(expr.name, tuple(new_indices))

    elif isinstance(expr, Binary):
        new_left = _resolve_index_offsets(expr.left, model_ir, _domain_cache)
        new_right = _resolve_index_offsets(expr.right, model_ir, _domain_cache)
        return Binary(expr.op, new_left, new_right)

    elif isinstance(expr, Unary):
        new_child = _resolve_index_offsets(expr.child, model_ir, _domain_cache)
        return Unary(expr.op, new_child)

    elif isinstance(expr, Call):
        new_args = tuple(_resolve_index_offsets(arg, model_ir, _domain_cache) for arg in expr.args)
        return Call(expr.func, new_args)

    elif isinstance(expr, (Sum, Prod)):
        new_body = _resolve_index_offsets(expr.body, model_ir, _domain_cache)
        new_condition = (
            _resolve_index_offsets(expr.condition, model_ir, _domain_cache)
            if expr.condition is not None
            else None
        )
        return type(expr)(expr.index_sets, new_body, new_condition)

    else:
        # Handle DollarConditional and SetMembershipTest so IndexOffset nodes
        # inside conditional subtrees are also resolved.
        from ..ir.ast import DollarConditional, SetMembershipTest

        if isinstance(expr, DollarConditional):
            new_val = _resolve_index_offsets(expr.value_expr, model_ir, _domain_cache)
            new_cond = _resolve_index_offsets(expr.condition, model_ir, _domain_cache)
            return DollarConditional(value_expr=new_val, condition=new_cond)

        if isinstance(expr, SetMembershipTest):
            new_idx = tuple(
                _resolve_index_offsets(idx, model_ir, _domain_cache) for idx in expr.indices
            )
            return SetMembershipTest(expr.set_name, new_idx)

    # Other expression types pass through unchanged
    return expr


def _expand_sums_with_unresolved_offsets(
    expr: Expr,
    model_ir: ModelIR,
    _domain_cache: dict[str, tuple[list[str], dict[str, int]] | None] | None = None,
) -> Expr:
    """Expand Sum nodes whose bodies contain unresolved IndexOffset nodes.

    Issue #1081: When a sum body like ``sum(l, x(t,l) - x(t-ord(l),l))``
    contains IndexOffset nodes that reference the sum variable (e.g.,
    ``ord(l)``), they can't be resolved while the sum variable is symbolic.
    This function expands such sums into explicit terms by iterating over
    the sum domain's members:

        x(t,'len-1') - x(t-1,'len-1') + x(t,'len-2') - x(t-2,'len-2') + ...

    After expansion, each term has a concrete value for the sum variable,
    so ``_resolve_index_offsets`` can resolve the offsets.

    Only expands sums where the body contains IndexOffset nodes with
    non-Const offsets (typically ``Call('ord', ...)`` referencing sum vars).
    """
    from ..ir.ast import Binary, Call, Prod, Sum, Unary

    if _domain_cache is None:
        _domain_cache = {}

    if isinstance(expr, Sum):
        # First, recursively process the body
        new_body = _expand_sums_with_unresolved_offsets(expr.body, model_ir, _domain_cache)
        new_cond = (
            _expand_sums_with_unresolved_offsets(expr.condition, model_ir, _domain_cache)
            if expr.condition is not None
            else None
        )

        # Check if the body contains unresolved IndexOffset nodes
        # that reference any of the sum's index variables
        sum_vars = set(expr.index_sets)
        if _has_unresolved_sum_offsets(new_body, sum_vars):
            # Expand this sum by iterating over domain members
            expanded = _expand_sum_body(
                expr.index_sets, new_body, new_cond, model_ir, _domain_cache
            )
            if expanded is not None:
                return expanded

        # No expansion needed — rebuild with processed children
        if new_body is expr.body and new_cond is expr.condition:
            return expr
        return Sum(expr.index_sets, new_body, new_cond)

    if isinstance(expr, Binary):
        new_left = _expand_sums_with_unresolved_offsets(expr.left, model_ir, _domain_cache)
        new_right = _expand_sums_with_unresolved_offsets(expr.right, model_ir, _domain_cache)
        if new_left is expr.left and new_right is expr.right:
            return expr
        return Binary(expr.op, new_left, new_right)

    if isinstance(expr, Unary):
        new_child = _expand_sums_with_unresolved_offsets(expr.child, model_ir, _domain_cache)
        if new_child is expr.child:
            return expr
        return Unary(expr.op, new_child)

    if isinstance(expr, Call):
        new_args = tuple(
            _expand_sums_with_unresolved_offsets(arg, model_ir, _domain_cache) for arg in expr.args
        )
        if all(n is o for n, o in zip(new_args, expr.args, strict=True)):
            return expr
        return Call(expr.func, new_args)

    if isinstance(expr, Prod):
        new_body = _expand_sums_with_unresolved_offsets(expr.body, model_ir, _domain_cache)
        new_cond = (
            _expand_sums_with_unresolved_offsets(expr.condition, model_ir, _domain_cache)
            if expr.condition is not None
            else None
        )
        if new_body is expr.body and new_cond is expr.condition:
            return expr
        return Prod(expr.index_sets, new_body, new_cond)

    # Leaf nodes (Const, ParamRef, VarRef, etc.) pass through unchanged
    return expr


def _has_unresolved_sum_offsets(expr: Expr, sum_vars: set[str]) -> bool:
    """Check if an expression contains IndexOffset nodes referencing sum variables.

    Returns True if any VarRef or ParamRef index contains an IndexOffset
    whose offset is a non-Const expression referencing a sum variable
    (e.g., ``Call('ord', (SymbolRef('l'),))`` when ``l`` is a sum variable).
    """
    from ..ir.ast import (
        Binary,
        Call,
        DollarConditional,
        ParamRef,
        Prod,
        SetMembershipTest,
        Sum,
        SymbolRef,
        Unary,
        VarRef,
    )

    def _offset_refs_sum_var(offset: Expr) -> bool:
        """Check if an offset expression references any sum variable."""
        if isinstance(offset, Const):
            return False
        if isinstance(offset, SymbolRef):
            return offset.name.lower() in {v.lower() for v in sum_vars}
        if isinstance(offset, Call):
            return any(_offset_refs_sum_var(arg) for arg in offset.args)
        if isinstance(offset, Binary):
            return _offset_refs_sum_var(offset.left) or _offset_refs_sum_var(offset.right)
        if isinstance(offset, Unary):
            return _offset_refs_sum_var(offset.child)
        return False

    def _check(e: Expr) -> bool:
        if isinstance(e, (VarRef, ParamRef)):
            if e.indices:
                for idx in e.indices:
                    if isinstance(idx, IndexOffset) and not isinstance(idx.offset, Const):
                        if _offset_refs_sum_var(idx.offset):
                            return True
            return False
        if isinstance(e, Binary):
            return _check(e.left) or _check(e.right)
        if isinstance(e, Unary):
            return _check(e.child)
        if isinstance(e, Sum):
            return _check(e.body) or (e.condition is not None and _check(e.condition))
        if isinstance(e, Prod):
            return _check(e.body) or (e.condition is not None and _check(e.condition))
        if isinstance(e, Call):
            return any(_check(arg) for arg in e.args)
        if isinstance(e, DollarConditional):
            return _check(e.value_expr) or _check(e.condition)
        if isinstance(e, SetMembershipTest):
            return _check(e.element_expr) if hasattr(e, "element_expr") else False
        return False

    return _check(expr)


def _expand_sum_body(
    index_sets: tuple[str, ...],
    body: Expr,
    condition: Expr | None,
    model_ir: ModelIR,
    _domain_cache: dict[str, tuple[list[str], dict[str, int]] | None],
) -> Expr | None:
    """Expand a Sum by iterating over concrete domain members.

    Returns a Binary(+, ...) chain of expanded terms, or None if expansion fails.
    """
    from ..ir.ast import Binary, Const

    if len(index_sets) != 1:
        # Multi-index expansion is complex; skip for now
        return None

    _MAX_SUM_EXPANSION = 500  # Safety limit to avoid pathological AST blow-up

    sum_var = index_sets[0]
    # Resolve domain members for the sum variable
    try:
        members, _ = resolve_set_members(sum_var, model_ir)
    except (ValueError, KeyError):
        return None
    if not members:
        return None
    if len(members) > _MAX_SUM_EXPANSION:
        return None  # Too many members; keep Sum unexpanded

    terms: list[Expr] = []
    for member in members:
        # Substitute sum variable with concrete member
        term = _substitute_single_index(body, sum_var, member)
        # Resolve IndexOffsets in the substituted term
        term = _resolve_index_offsets(term, model_ir, _domain_cache)
        # Apply condition if present
        if condition is not None:
            cond_sub = _substitute_single_index(condition, sum_var, member)
            cond_resolved = _resolve_index_offsets(cond_sub, model_ir, _domain_cache)
            # Multiply by condition value (0 or 1)
            term = Binary("*", term, cond_resolved)
        terms.append(term)

    if not terms:
        return Const(0.0)

    # Build addition chain
    result = terms[0]
    for t in terms[1:]:
        result = Binary("+", result, t)
    return result


def _substitute_single_index(expr: Expr, var_name: str, value: str) -> Expr:
    """Substitute a single index variable with a concrete value in an expression.

    Replaces occurrences of ``var_name`` in VarRef/ParamRef indices and
    SymbolRef nodes, and evaluates Call('ord', ...) for the substituted value.
    """
    from ..ir.ast import (
        Binary,
        Call,
        DollarConditional,
        ParamRef,
        Prod,
        SetMembershipTest,
        Sum,
        SymbolRef,
        Unary,
        VarRef,
    )

    var_lower = var_name.lower()

    def _sub_index(idx):
        """Substitute in a single index."""
        if isinstance(idx, str):
            if idx.lower() == var_lower:
                return value
            return idx
        if isinstance(idx, IndexOffset):
            new_base = value if idx.base.lower() == var_lower else idx.base
            new_offset = _sub(idx.offset)
            return IndexOffset(new_base, new_offset, idx.circular)
        return idx

    def _sub(e: Expr) -> Expr:
        if isinstance(e, SymbolRef):
            if e.name.lower() == var_lower:
                return SymbolRef(value)
            return e

        if isinstance(e, VarRef):
            if e.indices:
                new_indices = tuple(_sub_index(idx) for idx in e.indices)
                if new_indices != e.indices:
                    return VarRef(e.name, new_indices, e.attribute)
            return e

        if isinstance(e, ParamRef):
            if e.indices:
                new_indices = tuple(_sub_index(idx) for idx in e.indices)
                if new_indices != e.indices:
                    return ParamRef(e.name, new_indices)
            return e

        if isinstance(e, Binary):
            new_left = _sub(e.left)
            new_right = _sub(e.right)
            if new_left is e.left and new_right is e.right:
                return e
            return Binary(e.op, new_left, new_right)

        if isinstance(e, Unary):
            new_child = _sub(e.child)
            if new_child is e.child:
                return e
            return Unary(e.op, new_child)

        if isinstance(e, Call):
            new_args = tuple(_sub(arg) for arg in e.args)
            if all(n is o for n, o in zip(new_args, e.args, strict=True)):
                return e
            return Call(e.func, new_args)

        if isinstance(e, Sum):
            # Don't substitute into nested sums that rebind the same variable
            if var_lower in {s.lower() for s in e.index_sets}:
                return e
            new_body = _sub(e.body)
            new_cond = _sub(e.condition) if e.condition is not None else None
            if new_body is e.body and new_cond is e.condition:
                return e
            return Sum(e.index_sets, new_body, new_cond)

        if isinstance(e, Prod):
            if var_lower in {s.lower() for s in e.index_sets}:
                return e
            new_body = _sub(e.body)
            new_cond = _sub(e.condition) if e.condition is not None else None
            if new_body is e.body and new_cond is e.condition:
                return e
            return Prod(e.index_sets, new_body, new_cond)

        if isinstance(e, DollarConditional):
            new_val = _sub(e.value_expr)
            new_cond = _sub(e.condition)
            if new_val is e.value_expr and new_cond is e.condition:
                return e
            return DollarConditional(new_val, new_cond)

        if isinstance(e, SetMembershipTest):
            new_indices = tuple(_sub(idx) for idx in e.indices)
            if all(n is o for n, o in zip(new_indices, e.indices, strict=True)):
                return e
            return SetMembershipTest(e.set_name, new_indices)

        return e

    return _sub(expr)


def compute_constraint_jacobian(
    model_ir: ModelIR,
    normalized_eqs: dict[str, NormalizedEquation] | None = None,
    config: Config | None = None,
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
        normalized_eqs: Dictionary of normalized equations (optional for backward compatibility)
        config: Configuration for differentiation (will be augmented with model_ir
                for set membership lookups during differentiation)

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
    # Ensure config has model_ir for set membership lookups during differentiation
    from ..config import ensure_config_with_model_ir

    config = ensure_config_with_model_ir(config, model_ir)

    # Build index mapping for variables (shared across both Jacobians)
    base_index_mapping = build_index_mapping(model_ir)

    # Count equation instances for each constraint type
    # Note: Bounds in normalized_bounds are usually in model.inequalities, but
    # for backward compatibility with tests, we also count any bounds that aren't
    num_equality_rows = _count_equation_instances(model_ir, model_ir.equalities)
    num_inequality_rows = _count_equation_instances(model_ir, model_ir.inequalities)

    # Add count of bounds that aren't in model.inequalities (for test compatibility)
    for bound_name, norm_eq in model_ir.normalized_bounds.items():
        if bound_name not in model_ir.inequalities:
            # If index_values is set, it's a single specific instance
            if norm_eq.index_values:
                num_inequality_rows += 1
            else:
                num_inequality_rows += _count_equation_instances(model_ir, [bound_name])

    # Create separate index mapping for equalities (rows 0..num_equalities-1)
    # This ensures J_h row IDs are independent from global equation ordering
    eq_index_mapping = _build_equality_index_mapping(base_index_mapping, model_ir)

    # Create Jacobian structure for equalities
    J_h = JacobianStructure(
        index_mapping=eq_index_mapping,
        num_rows=num_equality_rows,
        num_cols=base_index_mapping.num_vars,
    )

    # Create separate index mapping for inequalities (rows 0..num_inequalities-1)
    # This includes both regular inequality equations and normalized bounds
    ineq_index_mapping = _build_inequality_index_mapping(base_index_mapping, model_ir)

    J_g = JacobianStructure(
        index_mapping=ineq_index_mapping,
        num_rows=num_inequality_rows,
        num_cols=base_index_mapping.num_vars,
    )

    # Precompute variable instances once (avoids re-enumerating per constraint)
    var_instances_cache = _precompute_variable_instances(model_ir)

    # Process equality constraints
    _compute_equality_jacobian(
        model_ir, eq_index_mapping, J_h, normalized_eqs, config, var_instances_cache
    )

    # Process inequality constraints
    _compute_inequality_jacobian(
        model_ir, ineq_index_mapping, J_g, normalized_eqs, config, var_instances_cache
    )

    # Process bounds from normalized_bounds
    # Note: If bounds are also in model.inequalities, they're already processed above
    # This handles cases where tests manually add to normalized_bounds without updating inequalities
    _compute_bound_jacobian(model_ir, ineq_index_mapping, J_g, config, var_instances_cache)

    return J_h, J_g


def _enumerate_equation_or_bound(eq_name: str, model_ir: ModelIR):
    """
    Helper to enumerate equation instances from either model.equations or model.normalized_bounds.

    Args:
        eq_name: Name of the equation or bound
        model_ir: Model IR with equations and bounds

    Returns:
        List of tuples representing equation instances (indices)
    """
    from .index_mapping import enumerate_equation_instances

    if eq_name in model_ir.equations:
        eq_def = model_ir.equations[eq_name]
        return enumerate_equation_instances(eq_name, eq_def.domain, model_ir, eq_def.condition)
    elif eq_name in model_ir.normalized_bounds:
        norm_eq = model_ir.normalized_bounds[eq_name]
        return enumerate_equation_instances(
            eq_name, norm_eq.domain_sets, model_ir, norm_eq.condition
        )
    else:
        return []


def _build_equality_index_mapping(base_mapping, model_ir: ModelIR):
    """
    Build index mapping for J_h (equality constraints only).

    Creates a mapping where row IDs are numbered 0..num_equalities-1, independent
    of the global equation ordering. This ensures equality constraints get their
    own row space in J_h.

    Args:
        base_mapping: Base index mapping from build_index_mapping() (for variables)
        model_ir: Model IR with equality constraints

    Returns:
        IndexMapping with equality-specific row numbering
    """
    from .index_mapping import IndexMapping

    # Create new mapping with same variable mappings but new equation mappings
    eq_mapping = IndexMapping()
    eq_mapping.var_to_col = base_mapping.var_to_col.copy()
    eq_mapping.col_to_var = base_mapping.col_to_var.copy()
    eq_mapping.num_vars = base_mapping.num_vars

    # Build row mappings for equality constraints only, starting from row 0
    row_id = 0
    for eq_name in model_ir.equalities:
        eq_instances = _enumerate_equation_or_bound(eq_name, model_ir)
        for eq_indices in eq_instances:
            eq_mapping.eq_to_row[(eq_name, eq_indices)] = row_id
            eq_mapping.row_to_eq[row_id] = (eq_name, eq_indices)
            row_id += 1

    eq_mapping.num_eqs = row_id
    return eq_mapping


def _build_inequality_index_mapping(base_mapping, model_ir: ModelIR):
    """
    Build index mapping for J_g (inequality constraints).

    Creates a mapping where row IDs are numbered 0..num_inequalities-1,
    independent of the global equation ordering. This ensures inequality constraints
    get their own row space in J_g.

    Note: Bounds from normalized_bounds are already in model.inequalities, so we
    process them all together.

    Args:
        base_mapping: Base index mapping from build_index_mapping() (for variables)
        model_ir: Model IR with inequality constraints

    Returns:
        IndexMapping with inequality-specific row numbering
    """
    from .index_mapping import IndexMapping

    # Create a new mapping with the same variable mappings but new equation mappings
    ineq_mapping = IndexMapping()
    ineq_mapping.var_to_col = base_mapping.var_to_col.copy()
    ineq_mapping.col_to_var = base_mapping.col_to_var.copy()
    ineq_mapping.num_vars = base_mapping.num_vars

    # Build row mappings for all inequality constraints, starting from row 0
    row_id = 0
    for eq_name in model_ir.inequalities:
        eq_instances = _enumerate_equation_or_bound(eq_name, model_ir)
        for eq_indices in eq_instances:
            ineq_mapping.eq_to_row[(eq_name, eq_indices)] = row_id
            ineq_mapping.row_to_eq[row_id] = (eq_name, eq_indices)
            row_id += 1

    # Add any bounds from normalized_bounds that aren't in model.inequalities
    # This handles backward compatibility with tests that manually add bounds
    for bound_name in sorted(model_ir.normalized_bounds.keys()):
        if bound_name not in model_ir.inequalities:
            norm_eq = model_ir.normalized_bounds[bound_name]

            # If index_values is set, this is a specific instance, not all instances
            if norm_eq.index_values:
                # Single specific instance
                ineq_mapping.eq_to_row[(bound_name, norm_eq.index_values)] = row_id
                ineq_mapping.row_to_eq[row_id] = (bound_name, norm_eq.index_values)
                row_id += 1
            else:
                # Enumerate all instances using helper function
                eq_instances = _enumerate_equation_or_bound(bound_name, model_ir)
                for eq_indices in eq_instances:
                    ineq_mapping.eq_to_row[(bound_name, eq_indices)] = row_id
                    ineq_mapping.row_to_eq[row_id] = (bound_name, eq_indices)
                    row_id += 1

    ineq_mapping.num_eqs = row_id
    return ineq_mapping


def _compute_equality_jacobian(
    model_ir: ModelIR,
    index_mapping,
    J_h: JacobianStructure,
    normalized_eqs: dict[str, NormalizedEquation] | None = None,
    config: Config | None = None,
    var_instances_cache: list[tuple[str, list[tuple[str, ...]]]] | None = None,
) -> None:
    """
    Compute Jacobian for equality constraints: J_h[i,j] = ∂h_i/∂x_j.

    Processes all equations in ModelIR.equalities. Each equation is in normalized
    form (lhs - rhs), and represents h_i(x) = 0.

    Uses sparsity pre-check to skip differentiation for variables that don't
    appear in the constraint expression, and skips storing zero derivatives.

    Note: Equality constraints can come from two sources:
    - model.equations: User-defined equations with Rel.EQ
    - model.normalized_bounds: Bounds like .fx that create equality constraints

    Args:
        model_ir: Model IR with equality constraints
        index_mapping: Index mapping for variables and equations
        J_h: Jacobian structure to populate (modified in place)
        normalized_eqs: Optional normalized equations
        config: Configuration for differentiation
        var_instances_cache: Precomputed variable instances (avoids re-enumeration)
    """
    from .index_mapping import enumerate_equation_instances

    # Precompute variable instances if not provided
    if var_instances_cache is None:
        var_instances_cache = _precompute_variable_instances(model_ir)

    simp_mode = get_simplification_mode(config)

    for eq_name in model_ir.equalities:
        # Prefer normalized equations if provided, otherwise fall back to original
        eq_def: EquationDef | NormalizedEquation
        if normalized_eqs and eq_name in normalized_eqs:
            eq_def = normalized_eqs[eq_name]
        elif eq_name in model_ir.equations:
            eq_def = model_ir.equations[eq_name]
        elif eq_name in model_ir.normalized_bounds:
            eq_def = model_ir.normalized_bounds[eq_name]
        else:
            # Skip if not found in either location (shouldn't happen)
            continue

        # Get all instances of this equation (handles indexed constraints)
        # NormalizedEquation uses 'domain_sets', EquationDef uses 'domain'
        eq_domain = eq_def.domain_sets if isinstance(eq_def, NormalizedEquation) else eq_def.domain
        eq_condition = eq_def.condition if hasattr(eq_def, "condition") else None
        eq_instances = enumerate_equation_instances(eq_name, eq_domain, model_ir, eq_condition)

        # Get equation expression template (before index substitution)
        from ..ir.ast import Binary

        base_expr: Expr
        if isinstance(eq_def, EquationDef):
            lhs, rhs = eq_def.lhs_rhs
            base_expr = Binary("-", lhs, rhs)
        else:
            base_expr = eq_def.expr

        # Sparsity pre-check: find which variables appear in this equation
        referenced_vars = find_variables_in_expr(base_expr)

        # Shared cache for IndexOffset resolution across all instances of this equation
        resolve_cache: dict[str, tuple[list[str], dict[str, int]] | None] = {}

        for eq_indices in eq_instances:
            # Get row ID for this equation instance
            row_id = index_mapping.get_row_id(eq_name, eq_indices)
            if row_id is None:
                continue

            # Substitute symbolic indices with concrete indices for this instance
            constraint_expr = base_expr
            if eq_domain:
                constraint_expr = _substitute_indices(constraint_expr, eq_domain, eq_indices)
                # Issue #1045: Resolve IndexOffset nodes to concrete domain elements.
                # After substitution, k(t+1) with t→"1990" becomes k(IndexOffset("1990",1)).
                # This resolves it to k("1995") so differentiation can match var instances.
                constraint_expr = _resolve_index_offsets(constraint_expr, model_ir, resolve_cache)

                # Issue #1081: Expand sums with unresolved IndexOffset nodes.
                # When a sum body contains offsets like ord(l) that reference the
                # sum variable, expand the sum into explicit terms so each term
                # can have its IndexOffset resolved to a concrete element.
                constraint_expr = _expand_sums_with_unresolved_offsets(
                    constraint_expr, model_ir, resolve_cache
                )

            # Differentiate w.r.t. each variable (only those referenced)
            for var_name, var_instances in var_instances_cache:
                # Sparsity check: skip variables not referenced in this equation
                if var_name not in referenced_vars:
                    continue

                for var_indices in var_instances:
                    col_id = index_mapping.get_col_id(var_name, var_indices)
                    if col_id is None:
                        continue

                    # Differentiate constraint w.r.t. this specific variable instance
                    derivative = differentiate_expr(constraint_expr, var_name, var_indices, config)

                    # Simplify derivative expression based on config
                    derivative = apply_simplification(derivative, simp_mode)

                    # Store in Jacobian only if non-zero
                    if not _is_zero_const(derivative):
                        J_h.set_derivative(row_id, col_id, derivative)


def _compute_inequality_jacobian(
    model_ir: ModelIR,
    index_mapping,
    J_g: JacobianStructure,
    normalized_eqs: dict[str, NormalizedEquation] | None = None,
    config: Config | None = None,
    var_instances_cache: list[tuple[str, list[tuple[str, ...]]]] | None = None,
) -> None:
    """
    Compute Jacobian for inequality constraints: J_g[i,j] = ∂g_i/∂x_j.

    Processes all equations in ModelIR.inequalities. Each equation is in normalized
    form (lhs - rhs ≤ 0), representing g_i(x) ≤ 0.

    Uses sparsity pre-check to skip differentiation for variables that don't
    appear in the constraint expression, and skips storing zero derivatives.

    Note: This now includes bounds from normalized_bounds, which are also in
    model.inequalities.

    Args:
        model_ir: Model IR with inequality constraints
        index_mapping: Index mapping for variables and equations
        J_g: Jacobian structure to populate (modified in place)
        normalized_eqs: Optional normalized equations
        config: Configuration for differentiation
        var_instances_cache: Precomputed variable instances (avoids re-enumeration)
    """
    from .index_mapping import enumerate_equation_instances

    # Precompute variable instances if not provided
    if var_instances_cache is None:
        var_instances_cache = _precompute_variable_instances(model_ir)

    simp_mode = get_simplification_mode(config)

    for eq_name in model_ir.inequalities:
        # Prefer normalized equation if provided, otherwise fall back to original
        eq_def: EquationDef | NormalizedEquation
        if normalized_eqs and eq_name in normalized_eqs:
            eq_def = normalized_eqs[eq_name]
        elif eq_name in model_ir.equations:
            eq_def = model_ir.equations[eq_name]
        elif eq_name in model_ir.normalized_bounds:
            eq_def = model_ir.normalized_bounds[eq_name]
        else:
            continue

        # Get all instances of this equation (handles indexed constraints)
        eq_domain = eq_def.domain_sets if isinstance(eq_def, NormalizedEquation) else eq_def.domain
        eq_condition = eq_def.condition if hasattr(eq_def, "condition") else None
        eq_instances = enumerate_equation_instances(eq_name, eq_domain, model_ir, eq_condition)

        # Get equation expression template (before index substitution)
        from ..ir.ast import Binary

        base_expr: Expr
        if isinstance(eq_def, EquationDef):
            lhs, rhs = eq_def.lhs_rhs
            base_expr = Binary("-", lhs, rhs)
        else:
            base_expr = eq_def.expr

        # Sparsity pre-check: find which variables appear in this equation
        referenced_vars = find_variables_in_expr(base_expr)

        # Shared cache for IndexOffset resolution across all instances of this equation
        resolve_cache: dict[str, tuple[list[str], dict[str, int]] | None] = {}

        for eq_indices in eq_instances:
            # Get row ID for this equation instance
            row_id = index_mapping.get_row_id(eq_name, eq_indices)
            if row_id is None:
                continue

            # Substitute symbolic indices with concrete indices for this instance
            constraint_expr = base_expr
            if eq_domain:
                constraint_expr = _substitute_indices(constraint_expr, eq_domain, eq_indices)
                # Issue #1045: Resolve IndexOffset nodes to concrete domain elements
                constraint_expr = _resolve_index_offsets(constraint_expr, model_ir, resolve_cache)

                # Issue #1081: Expand sums with unresolved IndexOffset nodes
                constraint_expr = _expand_sums_with_unresolved_offsets(
                    constraint_expr, model_ir, resolve_cache
                )

            # Differentiate w.r.t. each variable (only those referenced)
            for var_name, var_instances in var_instances_cache:
                # Sparsity check: skip variables not referenced in this equation
                if var_name not in referenced_vars:
                    continue

                for var_indices in var_instances:
                    col_id = index_mapping.get_col_id(var_name, var_indices)
                    if col_id is None:
                        continue

                    # Differentiate constraint w.r.t. this specific variable instance
                    derivative = differentiate_expr(constraint_expr, var_name, var_indices, config)

                    # Simplify derivative expression based on config
                    derivative = apply_simplification(derivative, simp_mode)

                    # Store in Jacobian only if non-zero
                    if not _is_zero_const(derivative):
                        J_g.set_derivative(row_id, col_id, derivative)


def _compute_bound_jacobian(
    model_ir: ModelIR,
    index_mapping,
    J_g: JacobianStructure,
    config: Config | None = None,
    var_instances_cache: list[tuple[str, list[tuple[str, ...]]]] | None = None,
) -> None:
    """
    Compute Jacobian rows for bound-derived inequality constraints.

    Variable bounds are converted to inequality constraints:
    - Lower bound: x(i) >= lo(i) → -(x(i) - lo(i)) ≤ 0
    - Upper bound: x(i) <= up(i) → x(i) - up(i) ≤ 0

    These contribute simple rows to J_g:
    - d(x(i) - lo(i))/dx(i) = 1, all other derivatives = 0
    - d(x(i) - up(i))/dx(i) = 1, all other derivatives = 0

    Uses sparsity pre-check to skip differentiation for variables that don't
    appear in the bound expression, and skips storing zero derivatives.

    Note: If bounds are also in model.inequalities, they're already processed by
    _compute_inequality_jacobian(), so we skip them here to avoid duplication.

    Args:
        model_ir: Model IR with normalized bounds
        index_mapping: Index mapping for variables and equations
        J_g: Jacobian structure to populate (modified in place)
        config: Configuration for differentiation
        var_instances_cache: Precomputed variable instances (avoids re-enumeration)
    """
    # Precompute variable instances if not provided
    if var_instances_cache is None:
        var_instances_cache = _precompute_variable_instances(model_ir)

    simp_mode = get_simplification_mode(config)

    for bound_name, norm_eq in sorted(model_ir.normalized_bounds.items()):
        # Skip if this bound is already in inequalities (processed by _compute_inequality_jacobian)
        if bound_name in model_ir.inequalities:
            continue

        # Get row ID from index mapping
        # Use index_values if set (specific instance), otherwise use empty tuple (scalar)
        bound_indices = norm_eq.index_values if norm_eq.index_values else ()
        row_id = index_mapping.get_row_id(bound_name, bound_indices)
        if row_id is None:
            continue

        # Get bound expression (already normalized)
        bound_expr = norm_eq.expr

        # Sparsity pre-check: find which variables appear in this bound expression
        referenced_vars = find_variables_in_expr(bound_expr)

        # Differentiate w.r.t. each variable (only those referenced)
        for var_name, var_instances in var_instances_cache:
            # Sparsity check: skip variables not referenced in this bound
            if var_name not in referenced_vars:
                continue

            for var_indices in var_instances:
                col_id = index_mapping.get_col_id(var_name, var_indices)
                if col_id is None:
                    continue

                # Differentiate bound constraint w.r.t. this variable instance
                derivative = differentiate_expr(bound_expr, var_name, var_indices, config)

                # Simplify derivative expression based on config
                derivative = apply_simplification(derivative, simp_mode)

                # Store in Jacobian only if non-zero
                if not _is_zero_const(derivative):
                    J_g.set_derivative(row_id, col_id, derivative)


def _count_equation_instances(model_ir: ModelIR, equation_names: list[str]) -> int:
    """
    Count total number of equation instances (rows) from a list of equation names.

    Handles indexed equations that expand to multiple instances.
    Checks both model.equations and model.normalized_bounds for equation definitions.

    Args:
        model_ir: Model IR with equations and sets
        equation_names: List of equation names to count

    Returns:
        Total number of equation instances
    """
    from .index_mapping import enumerate_equation_instances

    total_count = 0
    for eq_name in equation_names:
        # Check in regular equations first
        if eq_name in model_ir.equations:
            eq_def = model_ir.equations[eq_name]
            eq_instances = enumerate_equation_instances(
                eq_name, eq_def.domain, model_ir, eq_def.condition
            )
            total_count += len(eq_instances)
        # Check in normalized bounds (e.g., fixed variables)
        elif eq_name in model_ir.normalized_bounds:
            norm_eq = model_ir.normalized_bounds[eq_name]
            eq_instances = enumerate_equation_instances(
                eq_name, norm_eq.domain_sets, model_ir, norm_eq.condition
            )
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
    from ..ir.ast import Binary, Call, IndexOffset, ParamRef, Prod, Sum, Unary, VarRef

    def _sub_idx(idx):
        """Substitute a single index, handling both strings and IndexOffset."""
        if isinstance(idx, str):
            if idx in symbolic_indices:
                return concrete_indices[symbolic_indices.index(idx)]
            return idx
        elif isinstance(idx, IndexOffset):
            # Issue #1045: Substitute the base of IndexOffset when it matches
            # a symbolic index. E.g., IndexOffset("t", Const(1)) with t→"1990"
            # becomes IndexOffset("1990", Const(1)), enabling correct
            # differentiation of lead/lag variable references like k(t+1).
            if idx.base in symbolic_indices:
                new_base = concrete_indices[symbolic_indices.index(idx.base)]
                return IndexOffset(new_base, idx.offset, idx.circular)
            return idx
        return idx  # Other types pass through

    if isinstance(expr, VarRef):
        # Substitute indices in VarRef (handles both string and IndexOffset)
        # Preserve VarRef.attribute (e.g., x.l(i)) when reconstructing the node
        new_indices = tuple(_sub_idx(idx) for idx in expr.indices)
        return VarRef(expr.name, new_indices, expr.attribute)

    elif isinstance(expr, ParamRef):
        # Substitute indices in ParamRef (handles both string and IndexOffset)
        new_indices = tuple(_sub_idx(idx) for idx in expr.indices)
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

    elif isinstance(expr, (Sum, Prod)):
        # Don't substitute indices that are bound by the aggregation
        # Only substitute free indices
        free_symbolic = tuple(idx for idx in symbolic_indices if idx not in expr.index_sets)
        free_concrete = tuple(
            concrete_indices[symbolic_indices.index(idx)]
            for idx in symbolic_indices
            if idx not in expr.index_sets
        )
        if free_symbolic:
            new_body = _substitute_indices(expr.body, free_symbolic, free_concrete)
            new_cond = (
                _substitute_indices(expr.condition, free_symbolic, free_concrete)
                if expr.condition is not None
                else None
            )
            return type(expr)(expr.index_sets, new_body, new_cond)
        else:
            return expr

    else:
        # Issue #730: Handle SymbolRef, SetMembershipTest, DollarConditional.
        from ..ir.ast import DollarConditional, SetMembershipTest, SymbolRef

        # SymbolRef – bare index references like SymbolRef("r") that appear as
        # arguments in Call nodes (e.g., gamma(j, r) parsed as
        # Call("gamma", (SymbolRef("j"), SymbolRef("r")))).
        if isinstance(expr, SymbolRef) and expr.name in symbolic_indices:
            concrete = concrete_indices[symbolic_indices.index(expr.name)]
            return SymbolRef(concrete)

        # SetMembershipTest – e.g., im(i) or ri(r,i) in dollar conditions.
        # The indices are Expr nodes (typically SymbolRef) that need substitution.
        if isinstance(expr, SetMembershipTest):
            new_idx = tuple(
                _substitute_indices(idx, symbolic_indices, concrete_indices) for idx in expr.indices
            )
            return SetMembershipTest(expr.set_name, new_idx)

        # DollarConditional – e.g., expr$condition
        if isinstance(expr, DollarConditional):
            new_val = _substitute_indices(expr.value_expr, symbolic_indices, concrete_indices)
            new_cond = _substitute_indices(expr.condition, symbolic_indices, concrete_indices)
            return DollarConditional(value_expr=new_val, condition=new_cond)

        return expr
