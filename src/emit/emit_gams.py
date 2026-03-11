"""Main GAMS MCP code generator.

This module orchestrates all emission components to generate a complete
GAMS MCP file from a KKT system.
"""

import math
from collections import deque
from itertools import combinations
from typing import cast

from src.config import Config
from src.emit.equations import _build_domain_condition, _collect_lead_lag_restrictions
from src.emit.expr_to_gams import expr_to_gams
from src.emit.model import emit_model_mcp, emit_solve
from src.emit.original_symbols import (
    _compute_set_alias_phases,
    _quote_assignment_index,
    _quote_symbol,
    _sanitize_set_element,
    collect_missing_param_labels,
    compute_set_assignment_param_deps,
    emit_computed_parameter_assignments,
    emit_interleaved_params_and_sets,
    emit_loop_statements,
    emit_original_aliases,
    emit_original_parameters,
    emit_original_sets,
    emit_set_assignments,
    emit_subset_value_assignments,
    has_stochastic_parameters,
)
from src.emit.templates import (
    _build_dynamic_subset_map,
    emit_equation_definitions,
    emit_equations,
    emit_variables,
)
from src.ir.ast import (
    Binary,
    Call,
    Const,
    DollarConditional,
    EquationRef,
    Expr,
    IndexOffset,
    LhsConditionalAssign,
    MultiplierRef,
    ParamRef,
    Prod,
    SetAttrRef,
    SetMembershipTest,
    SubsetIndex,
    Sum,
    Unary,
    VarRef,
)
from src.ir.model_ir import ModelIR
from src.ir.symbols import VariableDef, VarKind
from src.kkt.kkt_system import KKTSystem
from src.kkt.naming import (
    create_bound_lo_multiplier_name,
    create_bound_up_multiplier_name,
    create_eq_multiplier_name,
)
from src.kkt.objective import extract_objective_info


def _merge_exclude_params(*sets: set[str] | None) -> set[str] | None:
    """Merge multiple optional exclude-param sets into one."""
    result: set[str] | None = None
    for s in sets:
        if s is not None:
            if result is None:
                result = set(s)
            else:
                result |= s
    return result


def _collect_model_relevant_params(model_ir: ModelIR) -> set[str] | None:
    """Collect parameter names relevant to the solved model.

    Issue #1036: Parameters only used for post-solve reporting (e.g., referencing
    .l/.m values) should not be emitted before the MCP solve.  This function
    collects all parameters referenced in model equations (and transitively
    through other parameter expressions) so the complement can be excluded.

    Returns None when no model equation filtering is active (all params relevant).
    """
    # Only filter when model equations are restricted
    solved_eqs = model_ir.get_solved_model_equations()
    if not solved_eqs:
        return None

    model_eq_set = {eq.lower() for eq in solved_eqs}
    referenced: set[str] = set()

    def _walk(expr: Expr) -> None:
        if isinstance(expr, ParamRef):
            referenced.add(expr.name.lower())
        for child in expr.children():
            _walk(child)

    # Collect params directly referenced in model equations
    for name, eq in model_ir.equations.items():
        if name.lower() not in model_eq_set:
            continue
        if eq.lhs_rhs:
            for side in eq.lhs_rhs:
                if isinstance(side, Expr):
                    _walk(side)

    # Also include params referenced in the objective expression
    if model_ir.objective and model_ir.objective.expr:
        _walk(model_ir.objective.expr)

    # Also include params referenced in variable initialization (.l, .lo, .up, .fx)
    # and bound expressions — these are critical for solver convergence.
    for var_def in model_ir.variables.values():
        for attr in ("l_expr", "lo_expr", "up_expr", "fx_expr"):
            expr = getattr(var_def, attr, None)
            if expr is not None:
                _walk(expr)
        for attr_map in ("l_expr_map", "lo_expr_map", "up_expr_map", "fx_expr_map"):
            emap = getattr(var_def, attr_map, None)
            if emap:
                for expr in emap.values():
                    _walk(expr)

    # Transitive closure: params referenced by other relevant params' expressions.
    # Use snapshot + difference to correctly detect new refs (sets are unordered).
    queue = deque(referenced)
    visited: set[str] = set()
    while queue:
        pname = queue.popleft()
        if pname in visited:
            continue
        visited.add(pname)
        pdef = model_ir.params.get(pname)
        if pdef is None:
            continue
        before_snapshot = set(referenced)
        for _, expr in pdef.expressions:
            _walk(expr)
        for new_ref in referenced - before_snapshot:
            if new_ref not in visited:
                queue.append(new_ref)

    return referenced


def _quote_uel(label: str) -> str:
    """Quote a UEL (Unique Element Label) for GAMS .fx/.lo/.up emission.

    fx_map/lo_map/up_map keys are always literal element values, never domain
    variables.  Always single-quote them to prevent GAMS from interpreting a
    label that collides with a set/alias name as a running index.

    Uses _sanitize_set_element for consistent handling of special characters,
    then ensures single-quoting with embedded-quote escaping.
    """
    # Sanitize via shared set-element sanitizer for consistent special-char handling
    sanitized = _sanitize_set_element(label)

    # If the sanitizer already returned a quoted element, respect that
    if (sanitized.startswith("'") and sanitized.endswith("'")) or (
        sanitized.startswith('"') and sanitized.endswith('"')
    ):
        return sanitized

    # Escape any embedded single quotes before wrapping in single quotes
    escaped = sanitized.replace("'", "''")
    return f"'{escaped}'"


def _format_map_indices(indices: tuple[str, ...]) -> str:
    """Format *_map keys (l_map, lo_map, fx_map) for GAMS emission.

    All *_map keys are literal element labels after parser expansion
    (_expand_variable_indices), so they are unconditionally quoted via
    _quote_uel().  This prevents GAMS misparse when an element label
    collides with a set/alias name (e.g., element 'i' in set i) or
    contains special characters (e.g., 'h-industry').
    """
    return ",".join(_quote_uel(str(idx)) for idx in indices)


def _index_to_gams_string(idx: str | IndexOffset | SubsetIndex) -> str:
    """Convert an index object to GAMS string representation.

    Args:
        idx: Index object (str, IndexOffset, or SubsetIndex)

    Returns:
        GAMS string representation of the index

    Examples:
        'i' -> 'i'
        IndexOffset('t', Const(1), circular=False) -> 't+1'
        SubsetIndex('subset', ('i', 'j')) -> 'subset(i,j)'
    """
    if isinstance(idx, str):
        return idx
    elif isinstance(idx, IndexOffset):
        return idx.to_gams_string()
    elif isinstance(idx, SubsetIndex):
        # SubsetIndex: subset_name(indices)
        indices_str = ",".join(idx.indices)
        return f"{idx.subset_name}({indices_str})"
    else:
        # Fallback: convert to string
        return str(idx)


def _collect_varref_names(expr: Expr) -> set[str]:
    """Collect variable names referenced as .l in an expression tree and indices."""
    names: set[str] = set()
    if isinstance(expr, VarRef) and expr.attribute == "l":
        names.add(expr.name.lower())
    for child in expr.children():
        names.update(_collect_varref_names(child))
    if isinstance(expr, (VarRef, ParamRef, MultiplierRef)):
        for idx in expr.indices:
            if isinstance(idx, Expr):
                names.update(_collect_varref_names(idx))
    return names


def _substitute_index(expr: Expr, old_idx: str, new_idx: str) -> Expr:
    """Substitute all occurrences of an index name in an expression AST.

    Used by section 2c to check if a complementarity equation becomes trivial
    on the diagonal (when two same-set indices are equal).
    """

    def _subst_single_index(i: str | IndexOffset) -> str | IndexOffset:
        """Substitute within a single index element (str or IndexOffset)."""
        if isinstance(i, str):
            return new_idx if i == old_idx else i
        if isinstance(i, IndexOffset):
            base = new_idx if i.base == old_idx else i.base
            new_offset = _substitute_index(i.offset, old_idx, new_idx)
            return IndexOffset(base, new_offset, i.circular)
        return i

    if isinstance(expr, Const):
        return expr
    if isinstance(expr, VarRef):
        new_indices = tuple(_subst_single_index(i) for i in expr.indices)
        return VarRef(expr.name, new_indices, expr.attribute)
    if isinstance(expr, ParamRef):
        new_indices = tuple(_subst_single_index(i) for i in expr.indices)
        return ParamRef(expr.name, new_indices)
    if isinstance(expr, MultiplierRef):
        new_indices = tuple(_subst_single_index(i) for i in expr.indices)
        return MultiplierRef(expr.name, new_indices)
    if isinstance(expr, EquationRef):
        new_indices = tuple(_subst_single_index(i) for i in expr.indices)
        return EquationRef(expr.name, new_indices, expr.attribute)
    if isinstance(expr, SetAttrRef):
        name = new_idx if expr.name == old_idx else expr.name
        return SetAttrRef(name, expr.attribute)
    if isinstance(expr, Binary):
        return Binary(
            expr.op,
            _substitute_index(expr.left, old_idx, new_idx),
            _substitute_index(expr.right, old_idx, new_idx),
        )
    if isinstance(expr, Unary):
        return Unary(expr.op, _substitute_index(expr.child, old_idx, new_idx))
    if isinstance(expr, Call):
        new_args = tuple(_substitute_index(a, old_idx, new_idx) for a in expr.args)
        return Call(expr.func, new_args)
    if isinstance(expr, Sum):
        # Don't substitute inside bound indices of aggregation
        if old_idx in expr.index_sets:
            return expr
        new_body = _substitute_index(expr.body, old_idx, new_idx)
        new_cond = (
            _substitute_index(expr.condition, old_idx, new_idx)
            if expr.condition is not None
            else None
        )
        return Sum(expr.index_sets, new_body, new_cond)
    if isinstance(expr, Prod):
        if old_idx in expr.index_sets:
            return expr
        new_body = _substitute_index(expr.body, old_idx, new_idx)
        new_cond = (
            _substitute_index(expr.condition, old_idx, new_idx)
            if expr.condition is not None
            else None
        )
        return Prod(expr.index_sets, new_body, new_cond)
    if isinstance(expr, DollarConditional):
        return DollarConditional(
            _substitute_index(expr.value_expr, old_idx, new_idx),
            _substitute_index(expr.condition, old_idx, new_idx),
        )
    if isinstance(expr, SetMembershipTest):
        smt_indices: tuple[Expr, ...] = tuple(
            _substitute_index(i, old_idx, new_idx) for i in expr.indices
        )
        return SetMembershipTest(expr.set_name, smt_indices)
    if isinstance(expr, IndexOffset):
        base = new_idx if expr.base == old_idx else expr.base
        new_offset = _substitute_index(expr.offset, old_idx, new_idx)
        return IndexOffset(base, new_offset, expr.circular)
    if isinstance(expr, SubsetIndex):
        si_indices: tuple[str, ...] = tuple(new_idx if i == old_idx else i for i in expr.indices)
        return SubsetIndex(expr.subset_name, si_indices)
    # For any other type (SymbolRef, ModelAttrRef, CompileTimeConstant), return as-is
    return expr


def _collect_additive_terms(expr: Expr, sign: int = 1) -> list[tuple[int, Expr]]:
    """Flatten an expression into signed additive terms.

    Returns a list of (sign, term) pairs where sign is +1 or -1.
    Recursively expands Binary(+/-) and Unary(-) to collect leaf terms.

    Used by section 2c to detect cancellation patterns like p(r,c) - p(r,c).
    """
    result: list[tuple[int, Expr]] = []
    _collect_additive_terms_acc(expr, sign, result)
    return result


def _collect_additive_terms_acc(expr: Expr, sign: int, acc: list[tuple[int, Expr]]) -> None:
    """Accumulator helper — appends (sign, term) pairs to *acc* in-place."""
    if isinstance(expr, Binary) and expr.op == "+":
        _collect_additive_terms_acc(expr.left, sign, acc)
        _collect_additive_terms_acc(expr.right, sign, acc)
        return
    if isinstance(expr, Binary) and expr.op == "-":
        _collect_additive_terms_acc(expr.left, sign, acc)
        _collect_additive_terms_acc(expr.right, -sign, acc)
        return
    if isinstance(expr, Unary) and expr.op == "-":
        _collect_additive_terms_acc(expr.child, -sign, acc)
        return
    if isinstance(expr, Binary) and expr.op == "*":
        # Check for (-1) * expr pattern
        if isinstance(expr.left, Const) and expr.left.value == -1.0:
            _collect_additive_terms_acc(expr.right, -sign, acc)
            return
        if isinstance(expr.right, Const) and expr.right.value == -1.0:
            _collect_additive_terms_acc(expr.left, -sign, acc)
            return
    acc.append((sign, expr))


def _contains_variable(expr: Expr) -> bool:
    """Return True if *expr* contains any VarRef or MultiplierRef in its subtree.

    Traverses index expressions (IndexOffset offsets), SetMembershipTest indices,
    and LhsConditionalAssign children to catch nested variable references.
    """
    if isinstance(expr, (VarRef, MultiplierRef)):
        return True
    if isinstance(expr, (ParamRef, EquationRef)):
        # ParamRef/EquationRef are not variables, but their indices may contain
        # IndexOffset with variable expressions in the offset.
        return any(
            isinstance(idx, IndexOffset) and _contains_variable(idx.offset) for idx in expr.indices
        )
    if isinstance(expr, IndexOffset):
        return _contains_variable(expr.offset)
    if isinstance(expr, Binary):
        return _contains_variable(expr.left) or _contains_variable(expr.right)
    if isinstance(expr, Unary):
        return _contains_variable(expr.child)
    if isinstance(expr, Call):
        return any(_contains_variable(a) for a in expr.args)
    if isinstance(expr, (Sum, Prod)):
        if expr.condition is not None and _contains_variable(expr.condition):
            return True
        return _contains_variable(expr.body)
    if isinstance(expr, DollarConditional):
        return _contains_variable(expr.value_expr) or _contains_variable(expr.condition)
    if isinstance(expr, SetMembershipTest):
        return any(_contains_variable(idx) for idx in expr.indices)
    if isinstance(expr, LhsConditionalAssign):
        return _contains_variable(expr.rhs) or _contains_variable(expr.condition)
    return False


def _is_trivial_after_cancellation(
    lhs: Expr,
    rhs: Expr,
    model_ir: ModelIR | None = None,
) -> bool:
    """Check if LHS =G= RHS is trivially satisfied after canceling matching terms.

    Issue #1021: Detects cases like p(r,c) + TCost(r,r,c) - p(r,c) >= 0
    where VarRef terms cancel, leaving only ParamRef terms that evaluate to 0
    on the diagonal.

    Returns True only when provably zero: all VarRef terms cancel AND remaining
    terms are either Const(0) or ParamRef whose diagonal data entries are all 0.
    """
    if not (isinstance(rhs, Const) and rhs.value == 0.0):
        return False

    terms = _collect_additive_terms(lhs)

    # Group terms by their expression (for cancellation detection).
    # Expr nodes are @dataclass(frozen=True), so they are hashable and
    # support structural equality — use the Expr object itself as the key
    # to avoid repr() mismatches (e.g., Const(5) vs Const(5.0)).
    term_counts: dict[Expr, int] = {}
    for sign, term in terms:
        term_counts[term] = term_counts.get(term, 0) + sign

    # Check remaining terms (those that didn't fully cancel)
    for term, count in term_counts.items():
        if count == 0:
            continue  # Fully canceled
        # Reject any remaining term that contains a VarRef or MultiplierRef
        # anywhere in its subtree (not just top-level). E.g., reject
        # Call('exp', (VarRef(...),)) or Binary('*', Const(2), VarRef(...)).
        if _contains_variable(term):
            return False
        # Const(0) is provably zero — accept it
        if isinstance(term, Const) and term.value == 0.0:
            continue
        # Non-zero Const is not trivial
        if isinstance(term, Const):
            return False
        # ParamRef: verify all diagonal entries are zero in actual data.
        # Diagonal entries are those where repeated index symbols have equal
        # values (e.g., TCost(r,r,c) → entries where positions 0 and 1 match).
        if isinstance(term, ParamRef) and model_ir is not None:
            if not _paramref_zero_on_diagonal(term, model_ir):
                return False
            continue
        # Any other non-canceled non-Const term (Call, Binary, etc.) — not provably zero
        return False

    return True


def _paramref_zero_on_diagonal(param: ParamRef, model_ir: ModelIR) -> bool:
    """Check whether a ParamRef evaluates to 0 on all diagonal entries.

    A ParamRef like TCost(r,r,c) has repeated index symbols at positions 0
    and 1.  We check the parameter's data entries where those positions have
    matching values.  Returns True only if ALL such entries are 0.
    """
    pdef = model_ir.params.get(param.name)
    if pdef is None:
        return False  # Unknown param — not provably zero

    # Computed parameters (non-empty expressions) may evaluate to nonzero
    # at runtime — can't verify statically, so reject early.
    if pdef.expressions:
        return False

    # Find positions with repeated index symbols
    idx_symbols = [str(i) for i in param.indices]
    sym_positions: dict[str, list[int]] = {}
    for pos, sym in enumerate(idx_symbols):
        sym_positions.setdefault(sym.lower(), []).append(pos)
    repeated_groups = [positions for positions in sym_positions.values() if len(positions) > 1]
    if not repeated_groups:
        # No repeated indices — we can't prove it's zero without full evaluation
        # Fall back: check if ALL entries in the parameter are zero
        return all(v == 0 for v in pdef.values.values())

    # Check only diagonal entries (where repeated positions have equal values)
    for entry_key, val in pdef.values.items():
        is_diagonal = all(
            all(entry_key[pos] == entry_key[positions[0]] for pos in positions[1:])
            for positions in repeated_groups
        )
        if is_diagonal and val != 0:
            return False

    return True


def _fx_eq_name(var_name: str, indices: tuple[str, ...]) -> str:
    """Reconstruct the _fx_ equation name for a per-element fixed variable.

    Delegates to the canonical bound-name logic in src/ir/normalize.py
    (bound_name) to avoid drift between normalization and emission.
    """
    from src.ir.normalize import bound_name

    return bound_name(var_name, "fx", indices)


class _MembershipConstraints:
    """Collected membership constraints from stationarity conditions.

    Attributes:
        position_members: Per-position active labels from 1-D membership tests.
            Mapping from domain position (int) to set of active UEL labels.
        tuple_constraints: Full-tuple constraints from multi-D membership tests.
            Each entry is (domain_positions, active_tuples) where domain_positions
            maps the membership test's index ordering to domain positions, and
            active_tuples is the set of member tuples (split from dot-joined).
    """

    __slots__ = ("position_members", "tuple_constraints")

    def __init__(self) -> None:
        self.position_members: dict[int, set[str]] = {}
        self.tuple_constraints: list[tuple[list[int], set[tuple[str, ...]]]] = []

    def is_empty(self) -> bool:
        return not self.position_members and not self.tuple_constraints


def _collect_position_memberships(
    kkt: KKTSystem,
    var_def: VariableDef,
    cond_expr: Expr,
    set_members_cache: dict[str, set[str]] | None = None,
    set_tuples_cache: dict[tuple[str, int], set[tuple[str, ...]]] | None = None,
) -> _MembershipConstraints:
    """Collect membership constraints from a stationarity condition.

    A SetMembershipTest like ``t(tl)`` restricts the domain variable ``tl`` to
    members of set ``t``.  For multi-dimensional variables, only the domain
    position corresponding to the condition's index symbol is constrained.

    For multi-dimensional membership tests like ``td(w,t)``, full-tuple
    membership is tracked to avoid unsound per-position projection.

    Binary("and", ...) conjunctions are traversed to collect multiple membership
    tests (e.g., ``s(i) and t(j)`` restricts two different positions).

    Returns:
        _MembershipConstraints with per-position members (1-D tests) and
        full-tuple constraints (multi-D tests).
    """
    from src.ir.ast import SymbolRef as _SymbolRef

    result = _MembershipConstraints()
    domain = getattr(var_def, "domain", ()) or ()
    unsound = False  # set True if we encounter non-conjunctive operators

    def _visit(expr: Expr) -> None:
        nonlocal unsound
        if unsound:
            return
        if isinstance(expr, SetMembershipTest):
            set_def = kkt.model_ir.sets.get(expr.set_name)
            if set_def is None or not set_def.members:
                return
            if not expr.indices:
                return
            # Map index symbol name -> domain position
            index_pos: dict[str, int] = {}
            ordered_positions: list[int] = []
            for idx_expr in expr.indices:
                idx_name: str | None = None
                if isinstance(idx_expr, _SymbolRef):
                    idx_name = idx_expr.name
                elif isinstance(idx_expr, str):
                    idx_name = idx_expr
                if idx_name is None:
                    continue
                idx_canon = idx_name.lower()
                for i, dom_sym in enumerate(domain):
                    dom_name = (
                        dom_sym if isinstance(dom_sym, str) else getattr(dom_sym, "name", None)
                    )
                    if dom_name is None:
                        continue
                    if dom_name.lower() == idx_canon:
                        index_pos[idx_name] = i
                        ordered_positions.append(i)
                        break
            if not index_pos:
                return
            num_indices = len(expr.indices)
            if num_indices == 1:
                # 1-D membership: store per-position active labels.
                ((_only_name, only_pos),) = index_pos.items()
                cache_key_1d = expr.set_name.lower()
                active: set[str]
                if set_members_cache is not None and cache_key_1d in set_members_cache:
                    active = set_members_cache[cache_key_1d]
                else:
                    active = set()
                    for member in set_def.members:
                        if isinstance(member, str):
                            active.add(member)
                    if set_members_cache is not None:
                        set_members_cache[cache_key_1d] = active
                if active:
                    if only_pos in result.position_members:
                        result.position_members[only_pos] &= active
                    else:
                        result.position_members[only_pos] = active
            else:
                # Multi-D membership: store full-tuple constraints.
                # Members are dot-joined tuples (e.g., "w1.t1").
                cache_key_md = (expr.set_name.lower(), num_indices)
                active_tuples: set[tuple[str, ...]]
                if set_tuples_cache is not None and cache_key_md in set_tuples_cache:
                    active_tuples = set_tuples_cache[cache_key_md]
                else:
                    active_tuples = set()
                    for member in set_def.members:
                        if not isinstance(member, str):
                            continue
                        parts = tuple(member.split("."))
                        if len(parts) == num_indices:
                            active_tuples.add(parts)
                    if set_tuples_cache is not None:
                        set_tuples_cache[cache_key_md] = active_tuples
                if active_tuples and len(ordered_positions) == num_indices:
                    result.tuple_constraints.append((ordered_positions, active_tuples))
        elif isinstance(expr, Binary) and expr.op == "and":
            _visit(expr.left)
            _visit(expr.right)
            return
        elif isinstance(expr, Binary):
            # Disjunctive boolean operators (or, xor) make membership-based
            # pruning unsound.  Bail out only for those; for other Binary ops
            # (arithmetic, comparison), fall through to children() traversal
            # so nested SetMembershipTest nodes can still be collected.
            if expr.op in ("or", "xor"):
                unsound = True
                return

        # Fallback: traverse children of other expression types so that
        # membership tests nested under wrappers (e.g., DollarConditional)
        # are still discovered.
        children_fn = getattr(expr, "children", None)
        if callable(children_fn):
            for child in children_fn():
                if isinstance(child, Expr):
                    _visit(child)

    _visit(cond_expr)
    if unsound:
        return _MembershipConstraints()  # empty — skip suppression
    return result


def _compute_suppressed_fx_equations(kkt: KKTSystem) -> set[str]:
    """Find _fx_ equations whose target index is outside the stationarity condition.

    When a variable has a conditioned stationarity equation (e.g., stat_a(tl)$(t(tl))),
    the emitter generates blanket .fx assignments for inactive instances. If the same
    variable also has per-element _fx_ equations (from fx_map), those equations would
    conflict — GAMS eliminates the fixed variable, leaving the _fx_ equation unmatched.

    This function identifies such _fx_ equations so they can be suppressed from the MCP.
    For 1-D membership tests, per-position checking is used. For multi-D membership
    tests, full-tuple membership is checked to avoid unsound per-position projection.
    """
    suppressed: set[str] = set()
    # Caches for parsed membership data, shared across all variables.
    members_cache: dict[str, set[str]] = {}
    tuples_cache: dict[tuple[str, int], set[tuple[str, ...]]] = {}

    for var_name, cond_expr in kkt.stationarity_conditions.items():
        var_def = kkt.model_ir.variables.get(var_name)
        if var_def is None or not var_def.fx_map:
            continue

        constraints = _collect_position_memberships(
            kkt, var_def, cond_expr, members_cache, tuples_cache
        )
        if constraints.is_empty():
            continue

        for indices, _value in var_def.fx_map.items():
            suppress = False
            # Check 1-D per-position constraints
            for pos, active_members in constraints.position_members.items():
                if pos < len(indices) and indices[pos] not in active_members:
                    suppress = True
                    break
            # Check multi-D full-tuple constraints
            if not suppress:
                for domain_positions, active_tuples in constraints.tuple_constraints:
                    # Extract the index components at the constrained positions
                    idx_tuple = tuple(
                        indices[pos] for pos in domain_positions if pos < len(indices)
                    )
                    if len(idx_tuple) == len(domain_positions) and idx_tuple not in active_tuples:
                        suppress = True
                        break
            if suppress:
                suppressed.add(_fx_eq_name(var_name, indices))

    return suppressed


def emit_gams_mcp(
    kkt: KKTSystem,
    model_name: str = "mcp_model",
    add_comments: bool = True,
    config: Config | None = None,
) -> str:
    """Generate complete GAMS MCP code from KKT system.

    This function orchestrates all emission components to produce a complete,
    runnable GAMS file containing:
    1. Original model declarations (Sets, Aliases, Parameters)
    2. KKT-specific sets for multiplier indexing
    3. Variable declarations (primal + multipliers, grouped by kind)
    4. Equation declarations
    5. Equation definitions
    6. Model MCP declaration with complementarity pairs
    7. Solve statement

    Args:
        kkt: The KKT system to emit
        model_name: Name for the GAMS model (default: "mcp_model")
        add_comments: Whether to add explanatory comments (default: True)

    Returns:
        Complete GAMS MCP code as a string

    Example:
        ```python
        # After parsing and KKT assembly
        gams_code = emit_gams_mcp(kkt)
        Path("output.gms").write_text(gams_code)
        ```
    """
    sections = []

    # Header comment
    if add_comments:
        sections.append("$onText")
        sections.append("Generated by nlp2mcp")
        sections.append("")
        sections.append("This file contains the KKT (Karush-Kuhn-Tucker) conditions")
        sections.append("for the original NLP model, transformed into MCP format.")
        sections.append("")
        sections.append("KKT System Components:")
        sections.append("  - Stationarity: ∇f + J^T λ + J^T ν - π^L + π^U = 0")
        sections.append("  - Complementarity: g(x) ⊥ λ, h(x) = 0, bounds ⊥ π")
        sections.append("  - Dual feasibility: λ, π^L, π^U ≥ 0")
        sections.append("  - Primal feasibility: g(x) ≤ 0, h(x) = 0, lo ≤ x ≤ up")
        sections.append("$offText")
        sections.append("")

    # Original model symbols
    if add_comments:
        sections.append("* ============================================")
        sections.append("* Original Model Declarations")
        sections.append("* ============================================")
        sections.append("")

    # Sprint 17 Day 10 (Issue #621): Split sets and aliases into phases
    # Correct emit order ensures all dependencies are declared before use.
    # For each phase p: emit phase p sets, then phase p aliases.
    # Supports N phases dynamically based on dependency depth.
    # Compute phases once and pass to both emitters to avoid redundant work.
    phases = _compute_set_alias_phases(kkt.model_ir)
    sets_by_phase = emit_original_sets(kkt.model_ir, precomputed_phases=phases)
    aliases_by_phase = emit_original_aliases(kkt.model_ir, precomputed_phases=phases)

    # Ensure both lists have the same length by padding with empty strings
    if sets_by_phase or aliases_by_phase:
        max_phases = max(len(sets_by_phase), len(aliases_by_phase))
    else:
        max_phases = 0
    while len(sets_by_phase) < max_phases:
        sets_by_phase.append("")
    while len(aliases_by_phase) < max_phases:
        aliases_by_phase.append("")

    # Emit each phase: sets first, then aliases
    for phase_idx in range(max_phases):
        if sets_by_phase[phase_idx]:
            sections.append(sets_by_phase[phase_idx])
            sections.append("")
        if aliases_by_phase[phase_idx]:
            sections.append(aliases_by_phase[phase_idx])
            sections.append("")

    # Issue #877: Emit Acronym declarations before parameters so that
    # acronym values in parameter data are recognized correctly
    if kkt.model_ir.acronyms:
        acronym_names = sorted(kkt.model_ir.acronyms)
        sections.append(f"Acronym {', '.join(acronym_names)};")
        sections.append("")

    params_code = emit_original_parameters(kkt.model_ir)
    if params_code:
        sections.append(params_code)
        sections.append("")

    # Issue #1007: Register UELs for first-dimension labels that were dropped
    # by zero-filtering (Issue #967). A synthetic Set ensures GAMS recognizes
    # these labels in string-indexed lookups like zz("depr",i) without
    # re-introducing explicit zeros into parameter data.
    missing_labels = collect_missing_param_labels(kkt.model_ir)
    if missing_labels:
        quoted = ", ".join(_sanitize_set_element(str(lab)) for lab in sorted(missing_labels))
        # Choose a unique name that doesn't collide with existing symbols.
        uel_name = "nlp2mcp_uel_registry"
        existing_lower = (
            {s.lower() for s in kkt.model_ir.sets}
            | {s.lower() for s in kkt.model_ir.aliases}
            | {s.lower() for s in kkt.model_ir.params}
            | {s.lower() for s in kkt.model_ir.variables}
            | {s.lower() for s in kkt.model_ir.acronyms}
            | {s.lower() for s in kkt.model_ir.equations}
        )
        suffix = 0
        while uel_name.lower() in existing_lower:
            suffix += 1
            uel_name = f"nlp2mcp_uel_registry{suffix}"
        sections.append(f"Set {uel_name} / {quoted} /;")
        sections.append("")

    # Issue #1036: Compute non-model-relevant parameters.
    # Parameters only used for post-solve reporting (e.g., referencing .l/.m
    # solution values) must not be emitted as computed assignments before the
    # MCP solve.  Compute the complement set and merge it into exclude_params
    # for all computed parameter emission calls.
    model_relevant_params = _collect_model_relevant_params(kkt.model_ir)
    non_model_params: set[str] | None = None
    if model_relevant_params is not None:
        all_params_lower = {p.lower() for p in kkt.model_ir.params}
        non_model_params = all_params_lower - model_relevant_params

    # Issue #860/#881: Emit set assignments and their dependent computed params
    # in interleaved order.  When set assignments have complex dependency chains
    # with computed parameters (e.g., T0 → red → redsam → T1 → Abar1 → nonzero),
    # they must be interleaved rather than emitted in separate blocks.
    # The interleaved emitter uses statement-level topological sorting to handle
    # params like SAM that have both early and late expressions.
    interleaved_code, interleaved_params, interleaved_sa_indices = emit_interleaved_params_and_sets(
        kkt.model_ir, varref_filter="no_varref_attr"
    )

    # If no interleaving needed, fall back to the original early-params approach.
    early_params: set[str] = set()
    if not interleaved_code:
        early_params = compute_set_assignment_param_deps(kkt.model_ir)
        if early_params:
            early_code = emit_computed_parameter_assignments(
                kkt.model_ir, varref_filter="no_varref_attr", only_params=early_params
            )
            if early_code:
                sections.append("$onImplicitAssign")
                sections.append(early_code)
                sections.append("$offImplicitAssign")
                sections.append("")
    else:
        early_params = interleaved_params
        sections.append("$onImplicitAssign")
        sections.append(interleaved_code)
        sections.append("$offImplicitAssign")
        sections.append("")

    # PR #658: Emit remaining dynamic set assignments not handled by interleaving.
    # Issue #1007: Split into two passes — assignments referencing .l values
    # (e.g., it(i) = yes$(e.l(i))) must be deferred until after Variables.
    remaining_set_indices = (
        [i for i in range(len(kkt.model_ir.set_assignments)) if i not in interleaved_sa_indices]
        if interleaved_sa_indices
        else None
    )
    set_assignments_code = emit_set_assignments(
        kkt.model_ir,
        varref_filter="no_varref_attr",
        only_indices=remaining_set_indices,
    )
    if set_assignments_code:
        sections.append("$onImplicitAssign")
        sections.append(set_assignments_code)
        sections.append("$offImplicitAssign")
        sections.append("")

    # Issue #860: Emit subset-qualified parameter values as executable assignments
    # AFTER set assignments (dynamic subsets must be populated first).
    # Issue #1036: Also exclude non-model-relevant params (post-solve reporting).
    subset_val_code = emit_subset_value_assignments(
        kkt.model_ir,
        exclude_params=_merge_exclude_params(
            interleaved_params if interleaved_params else None,
            non_model_params,
        ),
    )
    if subset_val_code:
        sections.append(subset_val_code)
        sections.append("")

    # Sprint 17 Day 4: Emit computed parameter assignments
    # Split into two passes: regular assignments go here (before Variables),
    # while .l-referencing calibration assignments are deferred until after
    # Variables are declared (GAMS requires variable declaration before .l access).
    # Issue #860/#881: Exclude params already emitted in the interleaved pass.
    # Issue #1036: Also exclude non-model-relevant params (post-solve reporting).
    computed_params_code = emit_computed_parameter_assignments(
        kkt.model_ir,
        varref_filter="no_varref_attr",
        exclude_params=_merge_exclude_params(
            early_params if early_params else None,
            non_model_params,
        ),
    )
    if computed_params_code:
        # Sprint 19 Day 3: If any computed parameter contains stochastic
        # functions (uniform, normal), fix the random seed so the MCP
        # produces deterministic results across solver invocations.
        if has_stochastic_parameters(kkt.model_ir):
            if add_comments:
                sections.append("* Fix random seed for deterministic MCP evaluation")
            sections.append("execseed = 12345;")
            sections.append("")
        sections.append(computed_params_code)
        sections.append("")

    # Issue #1025: Emit loop statements that contain parameter assignments
    # (e.g., wbar3, vbar3, sigmay3 in cesam2 are assigned inside loops)
    loop_code = emit_loop_statements(kkt.model_ir)
    if loop_code:
        sections.append(loop_code)
        sections.append("")

    # Variables (primal + multipliers)
    if add_comments:
        sections.append("* ============================================")
        sections.append("* Variables (Primal + Multipliers)")
        sections.append("* ============================================")
        sections.append("")
        sections.append("* Primal variables: Original decision variables from the NLP")
        sections.append("* Multipliers:")
        sections.append("*   ν (nu_*): Free multipliers for equality constraints")
        sections.append("*   λ (lam_*): Positive multipliers for inequality constraints")
        sections.append("*   π^L (piL_*): Positive multipliers for lower bounds")
        sections.append("*   π^U (piU_*): Positive multipliers for upper bounds")
        sections.append("")

    # Compute _fx_ equations to suppress (conflict with fix-inactive blanket .fx).
    # Must be done before emit_variables/emit_equations so they can filter.
    # Kept local — passed explicitly to downstream emitters instead of mutating kkt.
    suppressed_fx = _compute_suppressed_fx_equations(kkt)

    variables_code = emit_variables(kkt)
    sections.append(variables_code)
    sections.append("")

    # Issue #873: Emit expression-based variable bounds (.lo/.up/.fx)
    # Issue #921: Split into two passes — bounds that reference .l values must be
    # emitted AFTER .l initialization (deferred), while others come before.
    # Issue #1021: Also emit numeric per-element .fx bounds (fx_map) so that
    # fixed variables are communicated to the MCP solver (e.g., X.fx(r,r,c) = 0).
    bound_lines: list[str] = []
    deferred_bound_lines: list[str] = []
    for var_name, var_def in kkt.model_ir.variables.items():
        if (
            kkt.referenced_variables is not None
            and var_name.lower() not in kkt.referenced_variables
        ):
            continue
        for kind in ("lo", "up", "fx"):
            scalar_expr = getattr(var_def, f"{kind}_expr", None)
            expr_map = getattr(var_def, f"{kind}_expr_map", None)
            if expr_map:
                for indices, bound_expr in expr_map.items():
                    idx_str = ",".join(_index_to_gams_string(i) for i in indices)
                    idx_domain_vars = frozenset(i for i in indices if isinstance(i, str))
                    line = f"{var_name}.{kind}({idx_str}) = {expr_to_gams(bound_expr, domain_vars=idx_domain_vars)};"
                    if _collect_varref_names(bound_expr):
                        deferred_bound_lines.append(line)
                    else:
                        bound_lines.append(line)
            elif scalar_expr is not None:
                line = f"{var_name}.{kind} = {expr_to_gams(scalar_expr)};"
                if _collect_varref_names(scalar_expr):
                    deferred_bound_lines.append(line)
                else:
                    bound_lines.append(line)

        # Issue #1021: Emit numeric per-element .fx bounds from fx_map.
        # These represent X.fx(r,r,c) = 0 style assignments parsed from
        # the source model. Without re-emitting them, the MCP solver
        # complains about empty equations with unfixed paired variables.
        # fx_map keys are always literal UELs (never domain variables),
        # so always quote them to avoid collisions with set/alias names.
        if var_def.fx_map:
            for indices, fx_val in sorted(var_def.fx_map.items()):
                idx_str = _format_map_indices(indices)
                # Format value: use integer form for whole numbers
                val_str = str(int(fx_val)) if fx_val == int(fx_val) else str(fx_val)
                bound_lines.append(f"{var_name}.fx({idx_str}) = {val_str};")
    if bound_lines:
        if add_comments:
            sections.append("* ============================================")
            sections.append("* Variable Bounds")
            sections.append("* ============================================")
            sections.append("")
        sections.extend(bound_lines)
        sections.append("")

    # Sprint 18 Day 3 (P5 fix): Variable initialization to avoid division by zero
    # Variables with level values, lower bounds, or positive type need initialization
    # to prevent division by zero during model generation when they appear in
    # denominators of stationarity equations (e.g., from differentiating log(x) or 1/x)
    # Issue #763: Collect init lines per variable, then topologically sort them
    # so that .l expressions referencing other variables' .l come after their deps.
    var_init_groups: dict[str, list[str]] = {}  # var_name -> init lines
    var_init_order: list[str] = []  # preserve original order for stable sort
    var_l_deps: dict[str, set[str]] = {}  # var_name -> set of var names it depends on
    has_positive_clamp = False  # Track if any POSITIVE variable clamping is done
    has_positive_init = False  # Track if any POSITIVE variable is initialized to 1
    # Issue #874 / Subcategory E: Build set/alias lookup for domain-aware index quoting.
    # When a .l or .lo index is a set/alias name (e.g., J in SAM("TRF",J)), it must be
    # emitted as a bare identifier, not a quoted string literal.
    _sets_aliases_lower = {s.lower() for s in kkt.model_ir.sets} | {
        a.lower() for a in kkt.model_ir.aliases
    }
    for var_name, var_def in kkt.model_ir.variables.items():
        # Issue #742: Skip unreferenced variables (not declared, so no init needed)
        if (
            kkt.referenced_variables is not None
            and var_name.lower() not in kkt.referenced_variables
        ):
            continue
        has_init = False
        emitted_l_expr_init = False
        lines: list[str] = []

        # Priority 1: Check for explicit level values (l_map) - these take precedence
        if var_def.l_map:
            for indices, l_val in var_def.l_map.items():
                if l_val is not None:
                    # Issue #1020: Use _format_map_indices for *_map keys — avoids
                    # false positives from _is_index_offset_syntax for hyphenated
                    # element labels like 'h-industry'.
                    idx_str = _format_map_indices(indices)
                    lines.append(f"{var_name}.l({idx_str}) = {l_val};")
                    has_init = True
        elif var_def.l is not None:
            lines.append(f"{var_name}.l = {var_def.l};")
            has_init = True

        # Priority 1b: Expression-based .l assignments (Sprint 20 Day 2)
        # These are non-constant .l initializations like a.l = (xmin+xmax)/2
        if not has_init and hasattr(var_def, "l_expr_map") and var_def.l_expr_map:
            deps: set[str] = set()
            for indices, expr in var_def.l_expr_map.items():  # type: ignore[assignment]
                idx_str = ",".join(_index_to_gams_string(i) for i in indices)
                # Issue #874: Pass indices as domain_vars so the expression emitter
                # doesn't quote set variable names (e.g., wbar1(ii,jwt) not wbar1(ii,"jwt")).
                # Only include actual set/alias names — element labels must stay quoted.
                idx_domain_vars = frozenset(
                    i for i in indices if isinstance(i, str) and i.lower() in _sets_aliases_lower
                )
                expr_str = expr_to_gams(expr, domain_vars=idx_domain_vars)
                lines.append(f"{var_name}.l({idx_str}) = {expr_str};")
                deps.update(_collect_varref_names(expr))
                has_init = True
                emitted_l_expr_init = True
            deps.discard(var_name.lower())  # remove self-references
            if deps:
                var_l_deps[var_name] = deps
        elif not has_init and hasattr(var_def, "l_expr") and var_def.l_expr is not None:
            expr_str = expr_to_gams(var_def.l_expr)
            lines.append(f"{var_name}.l = {expr_str};")
            deps = _collect_varref_names(var_def.l_expr)
            deps.discard(var_name.lower())
            if deps:
                var_l_deps[var_name] = deps
            has_init = True
            emitted_l_expr_init = True

        # Priority 2: Check for indexed lower bounds (lo_map) if no .l was provided
        if not has_init and var_def.lo_map:
            for indices, lo_val in var_def.lo_map.items():
                if lo_val is not None and lo_val > 0:
                    # Issue #1020: Use _format_map_indices for *_map keys
                    idx_str = _format_map_indices(indices)
                    lines.append(f"{var_name}.l({idx_str}) = {lo_val};")
                    has_init = True
        # Check for scalar lower bound
        elif not has_init and var_def.lo is not None and var_def.lo > 0:
            lines.append(f"{var_name}.l = {var_def.lo};")
            has_init = True

        # Priority 3: Positive variables: ensure all elements have non-zero values
        if var_def.kind == VarKind.POSITIVE:
            if has_init:
                has_positive_clamp = True
                if var_def.domain:
                    domain_str = ",".join(var_def.domain)
                    lines.append(
                        f"{var_name}.l({domain_str}) = min(max({var_name}.l({domain_str}), 1e-6), {var_name}.up({domain_str}));"
                    )
                else:
                    lines.append(f"{var_name}.l = min(max({var_name}.l, 1e-6), {var_name}.up);")
            else:
                has_positive_init = True
                if var_def.domain:
                    domain_str = ",".join(var_def.domain)
                    lines.append(f"{var_name}.l({domain_str}) = 1;")
                else:
                    lines.append(f"{var_name}.l = 1;")

        # Issue #984: Clamp expression-based .l to .lo bounds.
        # When .l is set via an expression (Priority 1b) that may evaluate to 0,
        # ensure .l >= .lo to prevent domain errors (log(0), 1/x division by zero)
        # during equation generation. Only clamp when Priority 1b actually ran —
        # if numeric .l (Priority 1) was used, the values are already correct.
        if emitted_l_expr_init and var_def.lo is not None and var_def.lo > 0:
            if var_def.domain:
                domain_str = ",".join(var_def.domain)
                lines.append(
                    f"{var_name}.l({domain_str}) = max({var_name}.l({domain_str}), {var_def.lo});"
                )
            else:
                lines.append(f"{var_name}.l = max({var_name}.l, {var_def.lo});")
        elif emitted_l_expr_init and var_def.lo_map:
            # Emit per-index clamps only for indices present in lo_map.
            # This avoids changing semantics for indices that are intentionally
            # unbounded (partial lo_map coverage).
            for indices, lo_val in var_def.lo_map.items():
                if lo_val is not None and lo_val > 0:
                    # Issue #1020: Use _format_map_indices for *_map keys
                    idx_str = _format_map_indices(indices)
                    lines.append(
                        f"{var_name}.l({idx_str}) = max({var_name}.l({idx_str}), {lo_val});"
                    )

        if lines:
            var_init_groups[var_name] = lines
            var_init_order.append(var_name)

    # Issue #763: Topological sort of variable init groups so deps come first.
    if var_l_deps:
        name_to_lower = {v: v.lower() for v in var_init_order}
        lower_to_name = {v.lower(): v for v in var_init_order}
        in_deg: dict[str, int] = dict.fromkeys(var_init_order, 0)
        for vname, deps in var_l_deps.items():
            for dep_lower in deps:
                if dep_lower in lower_to_name:
                    in_deg[vname] += 1
        queue = deque(v for v in var_init_order if in_deg[v] == 0)
        sorted_vars: list[str] = []
        while queue:
            node = queue.popleft()
            sorted_vars.append(node)
            node_lower = name_to_lower[node]
            for vname in var_init_order:
                if vname in sorted_vars:
                    continue
                if node_lower in var_l_deps.get(vname, set()):
                    in_deg[vname] -= 1
                    if in_deg[vname] == 0:
                        queue.append(vname)
        # Add any remaining (cycles) in original order
        for v in var_init_order:
            if v not in sorted_vars:
                sorted_vars.append(v)
        var_init_order = sorted_vars

    init_lines: list[str] = []
    for vname in var_init_order:
        init_lines.extend(var_init_groups[vname])

    if init_lines:
        if add_comments:
            sections.append("* ============================================")
            sections.append("* Variable Initialization")
            sections.append("* ============================================")
            sections.append("")
            sections.append(
                "* Initialize variables to avoid division by zero during model generation."
            )
            sections.append(
                "* Variables appearing in denominators (from log, 1/x derivatives) need"
            )
            sections.append("* non-zero initial values.")
            if has_positive_clamp and has_positive_init:
                sections.append("* POSITIVE variables with explicit .l values are")
                sections.append(
                    "* clamped to min(max(value, 1e-6), upper_bound). Others are set to 1."
                )
            elif has_positive_clamp:
                sections.append("* POSITIVE variables with explicit .l values are")
                sections.append("* clamped to min(max(value, 1e-6), upper_bound).")
            elif has_positive_init:
                sections.append("* POSITIVE variables are set to 1.")
            sections.append("")
        # Issue #763: Wrap .l initialization in $onImplicitAssign to suppress
        # GAMS Error 141 when .l expressions reference other variables' .l values
        # that haven't been assigned yet (e.g., v.l(i) = pk.l * k.l(i) + ...).
        has_cross_varref = bool(var_l_deps)
        if has_cross_varref:
            sections.append("$onImplicitAssign")
        sections.extend(init_lines)
        if has_cross_varref:
            sections.append("$offImplicitAssign")
        sections.append("")

    # Issue #1007: Emit deferred set assignments that reference .l values
    # (e.g., it(i) = yes$(e.l(i) or m.l(i))) AFTER variable declarations
    # and .l initialization. These were filtered out of the early pass above.
    deferred_set_assignments_code = emit_set_assignments(
        kkt.model_ir, varref_filter="only_varref_attr"
    )
    if deferred_set_assignments_code:
        sections.append("$onImplicitAssign")
        sections.append(deferred_set_assignments_code)
        sections.append("$offImplicitAssign")
        sections.append("")

    # Issue #921: Emit deferred bounds (.lo/.up/.fx that reference .l values)
    # after .l initialization so that the .l values they depend on exist.
    if deferred_bound_lines:
        if add_comments:
            sections.append("* ============================================")
            sections.append("* Deferred Variable Bounds (depend on .l values)")
            sections.append("* ============================================")
            sections.append("")
        # Wrap deferred bounds in $onImplicitAssign to avoid GAMS Error 141
        # when .l-based bounds read variables whose .l values were never
        # explicitly initialized (treat them as implicitly 0 instead).
        sections.append("$onImplicitAssign")
        sections.extend(deferred_bound_lines)
        sections.append("$offImplicitAssign")
        sections.append("")

    # Issue #835: Emit .scale attributes for variables
    scale_lines: list[str] = []
    for var_name, var_def in kkt.model_ir.variables.items():
        if (
            kkt.referenced_variables is not None
            and var_name.lower() not in kkt.referenced_variables
        ):
            continue
        if var_def.scale is not None:
            scale_lines.append(f"{var_name}.scale = {expr_to_gams(var_def.scale)};")
        if var_def.scale_map:
            for indices, scale_expr in var_def.scale_map.items():  # type: ignore[assignment]
                idx_str = ",".join(_index_to_gams_string(i) for i in indices)  # type: ignore[arg-type]
                scale_lines.append(f"{var_name}.scale({idx_str}) = {expr_to_gams(scale_expr)};")
    if scale_lines:
        if add_comments:
            sections.append("* Variable Scaling")
        sections.extend(scale_lines)
        sections.append("")

    # Additional initialization for smooth_abs (if enabled)
    # Note: This is now largely redundant with Priority 3 initialization above,
    # which already handles POSITIVE variables. Kept for explicit smooth_abs comment.
    if config and config.smooth_abs:
        if add_comments:
            sections.append("* Additional initialization for smooth abs() approximation")
            sections.append("* (POSITIVE variables already initialized above)")
            sections.append("")

    # Issue #985: Post-solve calibration/reporting assignments from the original
    # NLP model (e.g., diff = (global - obj.l) / global) are intentionally
    # skipped — they may divide by zero and are not needed for MCP correctness.

    # Issue #903/#1008/#1009: Emit bound parameters and mask sets for
    # non-uniform bounds.  Indexed parameters hold per-element bound values
    # so complementarity equations stay indexed (avoiding GAMS $70).
    # Mask sets restrict equations to indices with finite bounds when only
    # a subset of indices have overrides and no finite base bound exists.
    if kkt.bound_param_masks:
        if add_comments:
            sections.append("* ============================================")
            sections.append("* Bound Mask Sets (partial bound coverage)")
            sections.append("* ============================================")
            sections.append("")
        for mask_name, (domain, covered) in sorted(kkt.bound_param_masks.items()):
            domain_str = ",".join(domain)
            # Each instance in `covered` may be a multi-dimensional index tuple.
            # Format each instance as a single dot-separated member (e.g., i1.j1),
            # consistent with emit_original_sets and GAMS multi-dimensional syntax.
            members = []
            for inst in sorted(covered):
                member = ".".join(_sanitize_set_element(idx) for idx in inst)
                members.append(member)
            elements = ", ".join(members)
            sections.append(f"Set {mask_name}({domain_str}) / {elements} /;")
        sections.append("")

    if kkt.bound_params:
        if add_comments:
            sections.append("* ============================================")
            sections.append("* Bound Parameters (non-uniform bounds)")
            sections.append("* ============================================")
            sections.append("")
        for param_name, (domain, data, base_value) in sorted(kkt.bound_params.items()):
            domain_str = ",".join(domain)
            sections.append(f"Parameter {param_name}({domain_str});")
            # When a base value exists, emit a domain-wide default assignment
            # followed by sparse overrides (avoids O(|domain|) assignments).
            if base_value is not None:
                if base_value == int(base_value):
                    base_str = str(int(base_value))
                else:
                    base_str = str(base_value)
                sections.append(f"{param_name}({domain_str}) = {base_str};")
            for inst_indices, value in sorted(data.items()):
                idx_str = ",".join(
                    _quote_assignment_index(idx, set(), domain_lower=frozenset())
                    for idx in inst_indices
                )
                if value == int(value):
                    val_str = str(int(value))
                else:
                    val_str = str(value)
                sections.append(f"{param_name}({idx_str}) = {val_str};")
            sections.append("")

    # Equations
    if add_comments:
        sections.append("* ============================================")
        sections.append("* Equations")
        sections.append("* ============================================")
        sections.append("")
        sections.append("* Stationarity: One equation per primal variable (except objvar)")
        sections.append("* Complementarity: Equations for inequalities and bounds")
        sections.append("* Equality constraints: Original equality constraints")
        sections.append("")

    equations_code = emit_equations(kkt, suppressed_fx_equations=suppressed_fx)
    sections.append(equations_code)
    sections.append("")

    # Equation definitions
    if add_comments:
        sections.append("* ============================================")
        sections.append("* Equation Definitions")
        sections.append("* ============================================")
        sections.append("")

    eq_defs_code, index_aliases = emit_equation_definitions(
        kkt, suppressed_fx_equations=suppressed_fx
    )

    # Emit index aliases if any are needed (to avoid GAMS Error 125)
    # These must be declared before the equation definitions that use them
    if index_aliases:
        if add_comments:
            sections.append("* Index aliases to avoid 'Set is under control already' error")
            sections.append("* (GAMS Error 125 when equation domain index is reused in sum)")
        for base in sorted(index_aliases.keys()):
            for alias_name in index_aliases[base]:
                sections.append(f"Alias({_quote_symbol(base)}, {_quote_symbol(alias_name)});")
        sections.append("")

    sections.append(eq_defs_code)
    sections.append("")

    # Issue #724: Fix variables whose paired MCP equation has a dollar condition.
    # When an MCP equation is conditioned (e.g., stat_x(w,t)$(td(w,t)) or
    # comp_minw(t)$(tm(t))), the paired variable must be fixed for excluded
    # instances so GAMS MCP doesn't report unmatched pairs.
    fx_lines: list[str] = []

    # 1. Fix primal variables with conditioned stationarity equations
    ref_mults = kkt.referenced_multipliers
    for var_name, cond_expr in sorted(kkt.stationarity_conditions.items()):
        var_def = kkt.model_ir.variables.get(var_name)
        if var_def and var_def.domain:
            domain_str = ",".join(var_def.domain)
            domain_vars = frozenset(var_def.domain)
            cond_gams = expr_to_gams(cond_expr, domain_vars=domain_vars)
            # Choose a finite fixing value: prefer fx, then lo (if finite),
            # then up (if finite), else 0.  Infinite bounds (-inf/+inf or None)
            # cannot be emitted as GAMS .fx values.
            if var_def.fx is not None and math.isfinite(var_def.fx):
                fix_val = var_def.fx
            elif var_def.lo is not None and math.isfinite(var_def.lo):
                fix_val = var_def.lo
            elif var_def.up is not None and math.isfinite(var_def.up):
                fix_val = var_def.up
            else:
                fix_val = 0
            fx_lines.append(f"{var_name}.fx({domain_str})$(not ({cond_gams})) = {fix_val};")
            # Issue #966: Also fix bound multipliers for this variable.
            # When the primal variable is inactive, its bound multipliers must
            # also be fixed to 0 so GAMS MCP matching doesn't see unmatched pairs.
            piL_name = create_bound_lo_multiplier_name(var_name)
            if (var_name, ()) in kkt.complementarity_bounds_lo:
                comp_pair_lo = kkt.complementarity_bounds_lo[(var_name, ())]
                if ref_mults is None or comp_pair_lo.variable in ref_mults:
                    fx_lines.append(f"{piL_name}.fx({domain_str})$(not ({cond_gams})) = 0;")
            piU_name = create_bound_up_multiplier_name(var_name)
            if (var_name, ()) in kkt.complementarity_bounds_up:
                comp_pair_up = kkt.complementarity_bounds_up[(var_name, ())]
                if ref_mults is None or comp_pair_up.variable in ref_mults:
                    fx_lines.append(f"{piU_name}.fx({domain_str})$(not ({cond_gams})) = 0;")

    # 2. Fix multipliers whose complementarity equation has a condition
    for _eq_name, comp_pair in sorted(kkt.complementarity_ineq.items()):
        if ref_mults is not None and comp_pair.variable not in ref_mults:
            continue
        eq_def = comp_pair.equation
        if eq_def.condition is not None and eq_def.domain:
            mult_name = comp_pair.variable
            domain_str = ",".join(eq_def.domain)
            domain_vars = frozenset(eq_def.domain)
            assert isinstance(eq_def.condition, Expr)
            cond_gams = expr_to_gams(eq_def.condition, domain_vars=domain_vars)
            fx_lines.append(f"{mult_name}.fx({domain_str})$(not ({cond_gams})) = 0;")

    # 2b. Issue #943: Fix inequality multipliers whose complementarity equation
    # has lead/lag expressions (e.g., i+1) that implicitly exclude terminal indices.
    # Same logic as section 3 below but for inequality complementarity equations.
    # Note: We compute lead/lag restrictions even when eq_def.condition is present,
    # because emit_equation_def() ANDs explicit conditions with inferred lead/lag
    # bounds. Section 2 above handles the explicit condition complement; this
    # section handles the lead/lag complement separately.
    for _eq_name, comp_pair in sorted(kkt.complementarity_ineq.items()):
        if ref_mults is not None and comp_pair.variable not in ref_mults:
            continue
        eq_def = comp_pair.equation
        if not eq_def.domain:
            continue
        lhs, rhs = eq_def.lhs_rhs
        lead_l, lag_l = _collect_lead_lag_restrictions(lhs, eq_def.domain)
        lead_r, lag_r = _collect_lead_lag_restrictions(rhs, eq_def.domain)
        lead_offsets = {
            k: max(lead_l.get(k, 0), lead_r.get(k, 0)) for k in set(lead_l) | set(lead_r)
        }
        lag_offsets = {k: max(lag_l.get(k, 0), lag_r.get(k, 0)) for k in set(lag_l) | set(lag_r)}
        inferred_cond = _build_domain_condition(lead_offsets, lag_offsets)
        if inferred_cond is None:
            continue
        mult_name = comp_pair.variable
        domain_str = ",".join(eq_def.domain)
        fx_lines.append(f"{mult_name}.fx({domain_str})$(not ({inferred_cond})) = 0;")

    # 2c. Issue #942: Fix inequality multipliers on diagonal elements when the
    # complementarity equation has 2+ indices from the same set (via aliases)
    # AND the diagonal equation instance is trivially empty.
    # Example: comp_ic(i,j) where j is an alias of i — diagonal (i,i) produces
    # an empty equation (e.g., w(i)-theta(i)*x(i) - (w(i)-theta(i)*x(i)) = 0).
    # We verify emptiness by substituting d_j→d_i in the AST and checking if
    # the constraint becomes trivially satisfied (LHS == RHS or LHS - RHS = 0).
    _alias_target: dict[str, str] = {}
    for alias_def in kkt.model_ir.aliases.values():
        _alias_target[alias_def.name.lower()] = alias_def.target.lower()

    def _resolve_canonical(idx_name: str) -> str:
        """Resolve an index name to its canonical set by following alias chains."""
        current = idx_name.lower()
        visited: set[str] = set()
        while current in _alias_target and current not in visited:
            visited.add(current)
            current = _alias_target[current]
        return current

    for _eq_name, comp_pair in sorted(kkt.complementarity_ineq.items()):
        if ref_mults is not None and comp_pair.variable not in ref_mults:
            continue
        eq_def = comp_pair.equation
        if not eq_def.domain or len(eq_def.domain) < 2:
            continue
        # Resolve each domain index to its canonical set (case-insensitive,
        # with transitive closure over chained aliases)
        canonical = [_resolve_canonical(idx) for idx in eq_def.domain]
        # Find pairs of indices that share the same canonical set
        for idx_a, idx_b in combinations(range(len(eq_def.domain)), 2):
            if canonical[idx_a] != canonical[idx_b]:
                continue
            d_i = eq_def.domain[idx_a]
            d_j = eq_def.domain[idx_b]
            # Verify the diagonal is actually empty: substitute d_j → d_i in the
            # AST and check if the constraint becomes trivially satisfied.
            lhs, rhs = eq_def.lhs_rhs
            subst_lhs = _substitute_index(lhs, d_j, d_i)
            subst_rhs = _substitute_index(rhs, d_j, d_i)
            # Check 1: LHS == RHS after substitution (constraint is x ≥ x)
            is_trivial = subst_lhs == subst_rhs
            # Check 2: LHS = A - B with A == B and RHS = 0 (common pattern:
            # f(i) - f(j) =G= 0 becomes f(i) - f(i) =G= 0, i.e., 0 ≥ 0)
            if (
                not is_trivial
                and isinstance(subst_lhs, Binary)
                and subst_lhs.op == "-"
                and subst_lhs.left == subst_lhs.right
                and isinstance(subst_rhs, Const)
                and subst_rhs.value == 0.0
            ):
                is_trivial = True
            # Check 3 (Issue #1021): Collect additive terms, cancel matching
            # VarRef pairs, and verify remaining terms are provably zero
            # (Const(0) or ParamRef with all-zero diagonal data).
            # Handles: p(r,c) + TCost(r,r,c) - p(r,c) =G= 0
            # where VarRef(p) cancels, leaving ParamRef(TCost) which is 0
            # on the diagonal (verified against actual parameter data).
            if not is_trivial:
                is_trivial = _is_trivial_after_cancellation(
                    subst_lhs, subst_rhs, model_ir=kkt.model_ir
                )
            if not is_trivial:
                continue
            mult_name = comp_pair.variable
            domain_str = ",".join(eq_def.domain)
            fx_lines.append(f"{mult_name}.fx({domain_str})$(ord({d_i}) = ord({d_j})) = 0;")

    # 2d. Fix bound multipliers for partially-covered non-uniform bounds.
    # When a variable has per-element bound overrides but no finite base bound,
    # the complementarity equation is conditioned on a mask set.  The paired
    # multiplier must be fixed to 0 for excluded indices.
    for mask_name, (domain, _covered) in sorted(kkt.bound_param_masks.items()):
        domain_str = ",".join(domain)
        # Determine if this is a lower or upper bound mask and get multiplier name
        # Mask names follow pattern: has_{var_name}_{lo|up}
        if mask_name.endswith("_lo"):
            var_name = mask_name[4:-3]  # strip "has_" and "_lo"
            mult_name = create_bound_lo_multiplier_name(var_name)
        elif mask_name.endswith("_up"):
            var_name = mask_name[4:-3]  # strip "has_" and "_up"
            mult_name = create_bound_up_multiplier_name(var_name)
        else:
            continue
        fx_lines.append(f"{mult_name}.fx({domain_str})$(not {mask_name}({domain_str})) = 0;")

    # 3. Fix equality multipliers (nu_*) whose equation has lead/lag restrictions.
    # Issue #760: stateq(n,k+1) generates rows only for k in ku (ord(k)<=card(k)-1),
    # but nu_stateq(n,k) is declared over the full (n,k) domain.  Fix the terminal
    # instances to 0 so GAMS MCP matching sees no unmatched free variable.
    for eq_name in sorted(kkt.model_ir.equalities):
        if eq_name not in kkt.model_ir.equations:
            continue
        eq_def = kkt.model_ir.equations[eq_name]
        if not eq_def.domain:
            continue
        lhs, rhs = eq_def.lhs_rhs
        lead_l, lag_l = _collect_lead_lag_restrictions(lhs, eq_def.domain)
        lead_r, lag_r = _collect_lead_lag_restrictions(rhs, eq_def.domain)
        lead_offsets = {
            k: max(lead_l.get(k, 0), lead_r.get(k, 0)) for k in set(lead_l) | set(lead_r)
        }
        lag_offsets = {k: max(lag_l.get(k, 0), lag_r.get(k, 0)) for k in set(lag_l) | set(lag_r)}
        # Also incorporate any explicit condition already on the equation
        inferred_cond = _build_domain_condition(lead_offsets, lag_offsets)
        if inferred_cond is None and eq_def.condition is None:
            continue
        mult_name = create_eq_multiplier_name(eq_name)
        if ref_mults is not None and mult_name not in ref_mults:
            continue
        domain_str = ",".join(eq_def.domain)
        if inferred_cond is not None:
            fx_lines.append(f"{mult_name}.fx({domain_str})$(not ({inferred_cond})) = 0;")
        elif eq_def.condition is not None and isinstance(eq_def.condition, Expr):
            domain_vars = frozenset(eq_def.domain)
            cond_gams = expr_to_gams(eq_def.condition, domain_vars=domain_vars)
            fx_lines.append(f"{mult_name}.fx({domain_str})$(not ({cond_gams})) = 0;")

    # 3b. Issue #1041: Fix equality multipliers whose equation domain uses
    # dynamic subsets. When TSAMEQ(ii,jj) is over dynamic subset (ii,jj) but
    # nu_TSAMEQ is declared over parent domain (i,i), instances where i∉ii or
    # j∉jj have no matching equation and must be fixed.
    # Use distinct parent-set aliases per position to avoid GAMS binding both
    # indices together (e.g., .fx(i,j) not .fx(i,i) for 2D coverage).
    dynamic_map = _build_dynamic_subset_map(kkt.model_ir)
    if dynamic_map:
        # Build alias groups: parent_set -> [alias1, alias2, ...]
        # so we can pick distinct names for each domain position
        alias_groups: dict[str, list[str]] = {}
        for aname, adef in kkt.model_ir.aliases.items():
            target = adef.target.lower()
            if target not in alias_groups:
                alias_groups[target] = []
            alias_groups[target].append(aname.lower())
        # Also include base set names
        for sname in kkt.model_ir.sets:
            sl = sname.lower()
            if sl not in alias_groups:
                alias_groups[sl] = []
            alias_groups[sl].insert(0, sl)
        for eq_name in sorted(kkt.model_ir.equalities):
            if eq_name not in kkt.model_ir.equations:
                continue
            eq_def = kkt.model_ir.equations[eq_name]
            if not eq_def.domain:
                continue
            # Check if any domain index is a dynamic subset
            has_dynamic = any(d.lower() in dynamic_map for d in eq_def.domain)
            if not has_dynamic:
                continue
            mult_name = create_eq_multiplier_name(eq_name)
            if ref_mults is not None and mult_name not in ref_mults:
                continue
            # Build parent domain with unique index names per position.
            # When multiple positions share the same parent set, use
            # distinct aliases (e.g., i, j instead of i, i).
            parent_indices: list[str] = []
            guards: list[str] = []
            used_names: dict[str, int] = {}  # parent -> next alias index
            for d in eq_def.domain:
                dl = d.lower()
                parent = dynamic_map.get(dl, dl)
                # Pick a unique name for this parent set position
                avail = alias_groups.get(parent, [parent])
                idx = used_names.get(parent, 0)
                if idx < len(avail):
                    chosen = avail[idx]
                else:
                    chosen = parent  # fallback
                used_names[parent] = idx + 1
                parent_indices.append(chosen)
                if dl in dynamic_map:
                    guards.append(f"{d}({chosen})")
            if guards:
                parent_domain_str = ",".join(parent_indices)
                guard_str = " and ".join(guards)
                fx_lines.append(f"{mult_name}.fx({parent_domain_str})$(not ({guard_str})) = 0;")

    # 4. Issue #826: Fix variables with empty stationarity equations.
    # When the stationarity builder can't propagate derivatives through subset
    # access patterns, the stationarity equation is empty (0 =E= 0).
    # GAMS only rejects this for indexed equations with dollar conditions
    # (conditioned instances expand to empty bodies). Scalar empty equations
    # like "stat_uu.. 0 =E= 0;" are accepted without fixing.
    for var_name in sorted(kkt.empty_stationarity_vars):
        stat_name = f"stat_{var_name}"
        stat_eq = kkt.stationarity.get(stat_name)
        if stat_eq is None:
            continue
        # Only fix if the stationarity equation is conditioned (dollar condition)
        # or if the variable has a stationarity condition (subset access pattern)
        needs_fix = stat_eq.condition is not None or var_name in kkt.stationarity_conditions
        if not needs_fix:
            continue

        # Derive the dollar condition used in the stationarity equation, if any.
        empty_cond: Expr | None = None
        if stat_eq.condition is not None:
            empty_cond = cast(Expr, stat_eq.condition)
        elif var_name in kkt.stationarity_conditions:
            empty_cond = kkt.stationarity_conditions[var_name]

        var_def = kkt.model_ir.variables.get(var_name)
        cond_str: str | None = None
        if empty_cond is not None:
            dv = frozenset(var_def.domain) if var_def and var_def.domain else None
            cond_str = expr_to_gams(empty_cond, domain_vars=dv)

        if var_def and var_def.domain:
            domain_str = ",".join(var_def.domain)
            if cond_str:
                fx_lines.append(f"{var_name}.fx({domain_str})$({cond_str}) = 0;")
            else:
                fx_lines.append(f"{var_name}.fx({domain_str}) = 0;")
        else:
            if cond_str:
                fx_lines.append(f"{var_name}.fx$({cond_str}) = 0;")
            else:
                fx_lines.append(f"{var_name}.fx = 0;")

    # Fix suppressed _fx_ equations: fix their multipliers to 0 and re-emit
    # the correct .fx value (instead of the blanket .fx = 0 from stationarity).
    if suppressed_fx:
        for var_name in sorted(kkt.stationarity_conditions):
            var_def = kkt.model_ir.variables.get(var_name)
            if var_def is None or not var_def.fx_map:
                continue
            for indices, fx_val in sorted(var_def.fx_map.items()):
                eq_name = _fx_eq_name(var_name, indices)
                if eq_name not in suppressed_fx:
                    continue
                # Fix the multiplier for this suppressed equation to 0
                mult_name = create_eq_multiplier_name(eq_name)
                if kkt.referenced_multipliers is None or mult_name in kkt.referenced_multipliers:
                    fx_lines.append(f"{mult_name}.fx = 0;")
                # Re-emit the correct .fx value for this element
                idx_str = _format_map_indices(indices)
                val_str = str(int(fx_val)) if fx_val == int(fx_val) else str(fx_val)
                fx_lines.append(f"{var_name}.fx({idx_str}) = {val_str};")

    if fx_lines:
        if add_comments:
            sections.append("* ============================================")
            sections.append("* Fix inactive variable instances")
            sections.append("* ============================================")
            sections.append("")
            sections.append("* Variables whose paired MCP equation is conditioned must be")
            sections.append("* fixed for excluded instances to satisfy MCP matching.")
            sections.append("")
        sections.extend(fx_lines)
        sections.append("")

    # Model MCP
    if add_comments:
        sections.append("* ============================================")
        sections.append("* Model MCP Declaration")
        sections.append("* ============================================")
        sections.append("")
        sections.append("* Each line pairs an equation with a variable:")
        sections.append("*   equation.variable")
        sections.append("*")
        sections.append("* This defines the complementarity problem:")
        sections.append("*   equation ⊥ variable")
        sections.append("*")
        sections.append("* Meaning: equation = 0 if variable > 0")
        sections.append("*          equation ≥ 0 if variable = 0")
        sections.append("")

    model_code = emit_model_mcp(kkt, model_name, suppressed_fx_equations=suppressed_fx)
    sections.append(model_code)
    sections.append("")

    # Issue #835: Enable scaleOpt when any variable has .scale attributes
    if scale_lines:
        sections.append(f"{model_name}.scaleOpt = 1;")
        sections.append("")

    # Solve statement
    if add_comments:
        sections.append("* ============================================")
        sections.append("* Solve Statement")
        sections.append("* ============================================")
        sections.append("")

    solve_code = emit_solve(model_name)
    sections.append(solve_code)

    # Issue #985: Post-solve calibration skipped (see note near Equations section).

    # Emit NLP objective value capture for pipeline comparison.
    # MCP listings have no "OBJECTIVE VALUE" line, so we assign the NLP objective
    # variable to a fixed-name sentinel scalar after the solve. The pipeline's
    # extract_objective_from_variables() matches "---- PARAMETER nlp2mcp_obj_val".
    # The nlp2mcp_ prefix reduces collision risk with user-defined symbols.
    obj_info = extract_objective_info(kkt.model_ir)
    if obj_info.objvar:
        sections.append("")
        sections.append("Scalar nlp2mcp_obj_val;")
        sections.append(f"nlp2mcp_obj_val = {obj_info.objvar}.l;")
        sections.append("Display nlp2mcp_obj_val;")

    return "\n".join(sections)
