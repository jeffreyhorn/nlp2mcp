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
    EquationRef,
    Expr,
    IndexOffset,
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
from src.ir.symbols import AliasDef, EquationDef, Rel
from src.kkt.kkt_system import KKTSystem
from src.kkt.naming import (
    create_eq_multiplier_name,
    create_ineq_multiplier_name,
)
from src.kkt.objective import extract_objective_info

# Sentinel value used in offset keys to mark variable positions that have no
# matching equation index (dimension-mismatch cases, e.g. 1-D equation
# contributing to a 2-D variable).  Deliberately larger than any real offset.
_SENTINEL_UNMATCHED: int = 999


def _compute_lead_lag_conditions(model_ir: ModelIR) -> dict[str, Expr]:
    """Compute implicit lead/lag domain restrictions for equations.

    GAMS silently skips equation instances that reference undefined elements
    via lead/lag indexing (e.g., ``x(n-1)`` when ``n`` is the first element).
    The emitter already infers these restrictions when writing GAMS output.

    This function computes equivalent AST conditions for use by the
    stationarity builder, which wraps multiplier terms with
    ``DollarConditional`` guards.  This allows ``_extract_all_conditioned_guard``
    to detect when ALL stationarity terms are conditional and add a condition
    to the stationarity equation, preventing MCP unmatched-equation errors.

    NOTE: This does NOT modify ``eq_def.condition``.  Modifying the equation
    IR caused regressions (e.g., catmix) because the stationarity builder
    over-restricted variable domains.

    Returns:
        Dict mapping equation name → inferred lead/lag condition AST.
    """
    result: dict[str, Expr] = {}
    for eq_name, eq_def in model_ir.equations.items():
        if not eq_def.domain:
            continue
        lhs, rhs = eq_def.lhs_rhs
        lead_offsets: dict[str, int] = {}
        lag_offsets: dict[str, int] = {}
        domain_map = {d.lower(): d for d in eq_def.domain}
        _collect_lead_lag_offsets(lhs, domain_map, lead_offsets, lag_offsets, set())
        _collect_lead_lag_offsets(rhs, domain_map, lead_offsets, lag_offsets, set())
        cond = _build_lead_lag_condition_expr(lead_offsets, lag_offsets)
        if cond is not None:
            result[eq_name] = cond
    return result


def _collect_lead_lag_offsets(
    expr: Expr,
    domain_map: dict[str, str],
    lead_offsets: dict[str, int],
    lag_offsets: dict[str, int],
    bound_indices: set[str],
) -> None:
    """Walk an expression tree collecting lead/lag offset magnitudes per domain index.

    Only non-circular IndexOffset nodes are considered.  Indices currently
    bound by a Sum or Prod are excluded to avoid false positives when a
    sum-local index shadows an equation-level domain index.
    """
    if isinstance(expr, IndexOffset) and not expr.circular:
        base_lower = expr.base.lower() if isinstance(expr.base, str) else None
        if base_lower and base_lower in domain_map and base_lower not in bound_indices:
            canonical = domain_map[base_lower]
            if isinstance(expr.offset, Const):
                offset_val = int(expr.offset.value)
                if offset_val > 0:
                    lead_offsets[canonical] = max(lead_offsets.get(canonical, 0), offset_val)
                elif offset_val < 0:
                    lag_offsets[canonical] = max(lag_offsets.get(canonical, 0), abs(offset_val))

    if isinstance(expr, (VarRef, ParamRef, EquationRef)):
        for idx in expr.indices:
            if isinstance(idx, IndexOffset):
                _collect_lead_lag_offsets(idx, domain_map, lead_offsets, lag_offsets, bound_indices)

    if isinstance(expr, (Sum, Prod)):
        new_bound = bound_indices | {idx.lower() for idx in expr.index_sets}
        for child in expr.children():
            _collect_lead_lag_offsets(child, domain_map, lead_offsets, lag_offsets, new_bound)
    else:
        for child in expr.children():
            _collect_lead_lag_offsets(child, domain_map, lead_offsets, lag_offsets, bound_indices)


def _build_lead_lag_condition_expr(
    lead_offsets: dict[str, int],
    lag_offsets: dict[str, int],
) -> Expr | None:
    """Build an AST condition expression from lead/lag offset dicts.

    - Lag offset n for index t → ``Binary(">", Call("ord", (SymbolRef(t),)), Const(n))``
    - Lead offset n for index k → ``Binary("<=", Call("ord", (SymbolRef(k),)),
      Binary("-", Call("card", (SymbolRef(k),)), Const(n)))``

    Multiple restrictions are AND-combined.
    """
    parts: list[Expr] = []
    for idx in sorted(lag_offsets):
        mag = lag_offsets[idx]
        parts.append(Binary(">", Call("ord", (SymbolRef(idx),)), Const(float(mag))))
    for idx in sorted(lead_offsets):
        mag = lead_offsets[idx]
        parts.append(
            Binary(
                "<=",
                Call("ord", (SymbolRef(idx),)),
                Binary("-", Call("card", (SymbolRef(idx),)), Const(float(mag))),
            )
        )
    if not parts:
        return None
    combined = parts[0]
    for p in parts[1:]:
        combined = Binary("and", combined, p)
    return combined


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


def _extract_all_conditioned_guard(
    stat_expr: Expr,
    var_domain: tuple[str, ...],
    model_ir: ModelIR,
    lead_lag_conditions: dict[str, Expr] | None = None,
) -> Expr | None:
    """Extract a combined guard when ALL top-level additive terms are DollarConditional.

    Issue #877: When every Jacobian contribution to a stationarity equation is
    wrapped in a DollarConditional (because the source equations all have dollar
    conditions), the stationarity evaluates to 0 =E= 0 for instances where none
    of the conditions hold.  This causes MCP pairing errors.

    If the expression is a tree of Binary("+", ...) whose leaves are all
    DollarConditional or Const(0), return the OR of all conditions — but only
    if the combined condition's free indices are within var_domain.  When a
    condition comes from inside a Sum and has extra indices, lift it into an
    existence check: sum((extra_indices), 1$cond).

    Issue #springchain: Terms containing MultiplierRef nodes for equations with
    implicit lead/lag restrictions (from ``lead_lag_conditions``) are treated as
    implicitly conditioned.  This handles the case where an equation like
    ``delta_x_eq(n).. x(n) - x(n-1)`` has no explicit condition but GAMS
    silently skips instances with out-of-range IndexOffset.
    """
    # Collect (condition, sum_indices) pairs from all leaf terms
    cond_entries: list[tuple[Expr, tuple[str, ...]]] = []

    def _find_multiplier_ll_cond(expr: Expr) -> Expr | None:
        """Check if a term contains a MultiplierRef for a lead/lag equation.

        Returns the lead/lag condition if found, None otherwise.
        """
        if lead_lag_conditions is None:
            return None
        if isinstance(expr, MultiplierRef):
            # MultiplierRef name is nu_EQNAME or lam_EQNAME
            for prefix in ("nu_", "lam_"):
                if expr.name.startswith(prefix):
                    eq_name = expr.name[len(prefix) :]
                    if eq_name in lead_lag_conditions:
                        return lead_lag_conditions[eq_name]
            return None
        for child in expr.children():
            result = _find_multiplier_ll_cond(child)
            if result is not None:
                return result
        return None

    def _collect(expr: Expr, sum_indices: tuple[str, ...] = ()) -> bool:
        """Return True if this sub-tree is all-conditioned (or zero)."""
        if isinstance(expr, Const) and expr.value == 0:
            return True
        if isinstance(expr, DollarConditional):
            cond_entries.append((expr.condition, sum_indices))
            return True
        if isinstance(expr, Sum):
            # Traverse Sum body, attributing any conditions to this Sum's indices
            return _collect(expr.body, expr.index_sets)
        if isinstance(expr, Binary) and expr.op in ("+", "-"):
            return _collect(expr.left, sum_indices) and _collect(expr.right, sum_indices)
        # Issue #springchain: Check for implicit lead/lag condition via MultiplierRef
        ll_cond = _find_multiplier_ll_cond(expr)
        if ll_cond is not None:
            cond_entries.append((ll_cond, sum_indices))
            return True
        return False

    if not _collect(stat_expr, ()):
        return None
    if not cond_entries:
        return None

    domain_set = {d.lower() for d in var_domain}
    valid_conditions: list[Expr] = []
    seen_reprs: set[str] = set()

    for cond, sum_indices in cond_entries:
        free = _collect_free_indices(cond, model_ir)
        cond_repr = repr(cond)

        if free <= domain_set:
            # Condition indices are within equation domain — use directly
            if cond_repr not in seen_reprs:
                valid_conditions.append(cond)
                seen_reprs.add(cond_repr)
        elif sum_indices:
            # Condition has extra indices from a Sum — lift by wrapping
            # in sum((extra_indices), 1$cond) to create an existence check
            extra = tuple(idx for idx in sum_indices if idx.lower() not in domain_set)
            if extra:
                lifted = Sum(
                    index_sets=extra,
                    body=DollarConditional(value_expr=Const(1), condition=cond),
                )
                lifted_repr = repr(lifted)
                if lifted_repr not in seen_reprs:
                    valid_conditions.append(lifted)
                    seen_reprs.add(lifted_repr)

    if not valid_conditions:
        return None

    # Build OR of all valid conditions: c1 or c2 or c3 ...
    combined = valid_conditions[0]
    for c in valid_conditions[1:]:
        combined = Binary("or", combined, c)
    return combined


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
        # cannot be used as-is — it would produce bare/uncontrolled indices in
        # GAMS.  Example: pls(r) accessed in sum(r$(ri(r,i)), pls(r)) produces
        # condition ri(r,i), but 'i' is not in pls's domain (r,).
        #
        # Issue #1005: Use _collect_free_indices() instead of
        # _collect_symbolref_names() to detect uncontrolled indices — the
        # latter misses string indices stored in ParamRef/VarRef nodes (e.g.,
        # ParamRef('ts', ('t','tf')) has no SymbolRef children).  When extra
        # indices are found, lift them into an existential check
        # sum(extra, 1$cond) instead of rejecting the condition outright.
        free_indices = _collect_free_indices(first, model_ir)
        extra_indices = free_indices - {d.lower() for d in var_domain}
        if extra_indices:
            lifted = Sum(
                index_sets=tuple(sorted(extra_indices)),
                body=DollarConditional(value_expr=Const(1), condition=first),
            )
            return lifted
        return first

    return None


def _has_unconditioned_access(
    var_name: str,
    var_domain: tuple[str, ...],
    model_ir: ModelIR,
) -> bool:
    """Check if a variable has any unconditioned access in the model equations.

    Returns True if the variable appears in at least one equation without an
    enclosing dollar condition.  This is used to gate Stage 4 gradient-condition
    fallback: when a variable is accessed unconditionally in some constraint,
    adding an equation-level guard from gradient conditions would incorrectly
    suppress stationarity instances required by those unconditioned constraints.

    Equation-level conditions (``eq(i)$cond..``) are treated as enclosing
    guards: a variable referenced unconditionally in the body of a conditioned
    equation is NOT considered an unconditioned access, since the equation-level
    guard protects all references within it.

    For scalar variables (empty domain), returns True conservatively — the
    domain-overlap heuristic in _collect_access_conditions doesn't apply, so
    we assume unconditioned access to prevent incorrect guard application.
    """
    if not var_domain:
        return True

    var_domain_set = set(var_domain)
    for _eq_name, eq_def in model_ir.equations.items():
        lhs, rhs = eq_def.lhs_rhs
        # Equation-level condition (eq(i)$cond..) acts as enclosing guard
        eq_has_condition = eq_def.condition is not None
        for side_expr in (lhs, rhs):
            conditions = _collect_access_conditions(
                side_expr,
                var_name,
                var_domain_set,
                has_enclosing_condition=eq_has_condition,
            )
            if conditions is not None and not conditions:
                # Variable found with no enclosing condition (body or eq-level)
                if not eq_has_condition:
                    return True
    return False


def _find_variable_subset_condition(
    var_name: str,
    var_domain: tuple[str, ...],
    model_ir: ModelIR,
) -> Expr | None:
    """Detect when a variable is consistently accessed via a named subset index.

    Issue #759: A variable declared over domain (m, k) may only be referenced
    inside equations with a subset index like ``u(m, ku)`` where ``ku(k)`` is a
    dynamic subset of ``k``.  In this case GAMS will generate a stationarity
    equation for the terminal ``k`` instance (not in ``ku``), but the Jacobian is
    zero there — creating an unmatched MCP equation.

    This function walks all equations, finds VarRef nodes for *var_name*, and
    checks whether ALL occurrences replace a declared domain index with a
    consistent named subset of that domain index.  When all occurrences agree on
    the same subset for the same domain position, return
    ``SetMembershipTest(subset, (SymbolRef(domain_idx),))`` as the condition.

    Args:
        var_name: Variable name (e.g., "u")
        var_domain: Variable's declared domain (e.g., ("m", "k"))
        model_ir: Model IR

    Returns:
        A SetMembershipTest condition Expr, or None if no consistent subset pattern.
    """
    if not var_domain:
        return None

    # Build a reverse map: parent_set_name → list of subset names.
    # A subset qualifies if it has domain=(parent,) — either a static subset
    # (declared with explicit members, e.g. cf(c) / steel /) or a dynamic
    # subset (assigned via set assignment, e.g. ku(k) = yes$(ord(k)<=...)).
    parent_to_subsets: dict[str, list[str]] = {}
    for set_name, set_def in model_ir.sets.items():
        # Guard against test fixtures that store plain lists instead of SetDef objects
        if not hasattr(set_def, "domain"):
            continue
        if len(set_def.domain) == 1:
            name_lower = set_name.lower()
            parent = set_def.domain[0].lower()
            parent_to_subsets.setdefault(parent, []).append(name_lower)

    # Build alias → canonical target map (e.g., mp → m).
    # Used to treat alias indices as equivalent to their target when comparing
    # against a variable's declared domain indices.
    # model_ir.aliases values may be AliasDef objects or plain strings (in tests).
    alias_to_canonical: dict[str, str] = {}
    for a, a_val in model_ir.aliases.items():
        target = a_val.target if hasattr(a_val, "target") else str(a_val)
        alias_to_canonical[a.lower()] = target.lower()

    def _resolve(name: str) -> str:
        """Resolve an alias to its canonical set name (idempotent)."""
        return alias_to_canonical.get(name, name)

    # Which domain positions could be replaced by a subset?
    # Map: position index → set of subset names seen across all VarRef occurrences
    # None means "seen the declared domain index (no substitution)"
    pos_subsets: dict[int, set[str] | None] = {}

    def _walk_expr(
        expr: Expr,
        skip_declared_at: frozenset[str] = frozenset(),
        dollar_subsets: dict[str, str] | None = None,
    ) -> bool:
        """Walk expr; return True if var_name found at least once.

        Args:
            expr: Expression to walk
            skip_declared_at: Domain indices already restricted by equation lead/lag
            dollar_subsets: Mapping from domain index (lower) → subset name (lower)
                when inside a DollarConditional that restricts that index to a subset.
                Issue #871: Allows ``e(i)$it(i)`` to be treated as restricted to ``it``.
        """
        found = False
        if isinstance(expr, VarRef) and expr.name.lower() == var_name.lower():
            found = True
            indices = expr.indices or ()
            for pos, (decl_idx, actual_idx) in enumerate(zip(var_domain, indices, strict=False)):
                if isinstance(actual_idx, IndexOffset):
                    # Issue #1043: An IndexOffset like k(t+1) means the
                    # variable is accessed across the range of the declared
                    # domain — this IS evidence of full-domain usage.
                    io_base = _resolve(actual_idx.base.lower())
                    decl_lower_io = _resolve(decl_idx.lower())
                    if io_base == decl_lower_io:
                        pos_subsets[pos] = None  # full-domain evidence
                    continue
                if not isinstance(actual_idx, str):
                    continue  # Other non-string index types — skip
                # Resolve aliases so that 'mp' is treated the same as 'm'
                actual_lower = _resolve(actual_idx.lower())
                decl_lower = _resolve(decl_idx.lower())
                if actual_lower == decl_lower:
                    if decl_lower in skip_declared_at:
                        # This equation already has a lead/lag restriction on this
                        # index, so a plain declared-index access here is NOT
                        # evidence that the full domain is needed.
                        pass
                    elif dollar_subsets and decl_lower in dollar_subsets:
                        # Issue #871: Inside a DollarConditional that restricts this
                        # index to a subset (e.g. e(i)$it(i) restricts i to it).
                        # Treat as subset access, not full-domain access.
                        sub_name = dollar_subsets[decl_lower]
                        if pos not in pos_subsets:
                            pos_subsets[pos] = {sub_name}
                        elif pos_subsets[pos] is not None:
                            pos_subsets[pos].add(sub_name)  # type: ignore[union-attr]
                    else:
                        # Used with the declared index — no substitution at this position
                        pos_subsets[pos] = None
                elif actual_lower in (parent_to_subsets.get(decl_lower) or []):
                    # Used with a subset index
                    if pos not in pos_subsets:
                        pos_subsets[pos] = {actual_lower}
                    elif pos_subsets[pos] is not None:
                        pos_subsets[pos].add(actual_lower)  # type: ignore[union-attr]
                    # If pos_subsets[pos] is already None (declared idx seen), leave as None

        # Issue #871: When entering a DollarConditional, extract subset restrictions
        # from the condition (e.g. $it(i) means index i is restricted to subset it).
        if isinstance(expr, DollarConditional):
            new_dollar: dict[str, str] = dict(dollar_subsets) if dollar_subsets else {}
            cond = expr.condition
            if isinstance(cond, SetMembershipTest) and len(cond.indices) == 1:
                idx_expr = cond.indices[0]
                if isinstance(idx_expr, SymbolRef):
                    idx_lower = _resolve(idx_expr.name.lower())
                    sub_lower = cond.set_name.lower()
                    # Check: is sub_lower a known subset of a domain index?
                    for decl_idx in var_domain:
                        decl_lower = _resolve(decl_idx.lower())
                        if idx_lower == decl_lower and sub_lower in (
                            parent_to_subsets.get(decl_lower) or []
                        ):
                            new_dollar[decl_lower] = sub_lower
            # Walk value_expr with the updated dollar_subsets context
            if _walk_expr(expr.value_expr, skip_declared_at, new_dollar or None):
                found = True
            # Walk condition without dollar_subsets (condition itself is not guarded)
            if _walk_expr(expr.condition, skip_declared_at, dollar_subsets):
                found = True
            return found

        for child in expr.children():
            if _walk_expr(child, skip_declared_at, dollar_subsets):
                found = True
        return found

    found_any = False
    for eq_def in model_ir.equations.values():
        # Determine which domain indices of the variable are already restricted
        # by this equation's own lead/lag pattern (e.g. stateq(n,k+1) restricts
        # k to ku implicitly).  Accesses in such equations with the plain declared
        # index are NOT evidence that the full domain is needed.
        restricted_by_eq: set[str] = set()
        if eq_def.domain:
            from src.ir.ast import IndexOffset as _IO

            def _collect_leads(e: Expr, domain_lower: frozenset[str]) -> None:
                if isinstance(e, _IO) and not e.circular:
                    canonical = e.base.lower()
                    if canonical in domain_lower:
                        restricted_by_eq.add(canonical)
                # VarRef.children() does NOT yield indices — check them explicitly
                if isinstance(e, VarRef):
                    for idx in e.indices or ():
                        if isinstance(idx, Expr):
                            _collect_leads(idx, domain_lower)
                for c in e.children():
                    _collect_leads(c, domain_lower)

            domain_lower = frozenset(d.lower() for d in eq_def.domain)
            for side in eq_def.lhs_rhs:
                _collect_leads(side, domain_lower)
            if eq_def.condition is not None:
                _collect_leads(eq_def.condition, domain_lower)
        skip = frozenset(restricted_by_eq)
        for side in eq_def.lhs_rhs:
            if _walk_expr(side, skip):
                found_any = True
        if eq_def.condition is not None:
            _walk_expr(eq_def.condition, skip)

    if not found_any:
        return None

    # Find positions where ALL accesses use a single consistent subset
    # (i.e., the declared index was NEVER used, and exactly one subset appears)
    conditions: list[Expr] = []
    for pos, subsets in pos_subsets.items():
        if subsets is None or len(subsets) != 1:
            continue  # Declared index seen, or multiple subsets — no clean restriction
        (subset_name,) = subsets
        decl_idx = var_domain[pos]
        conditions.append(SetMembershipTest(subset_name, (SymbolRef(decl_idx),)))

    if len(conditions) == 1:
        return conditions[0]
    # Multiple independent conditions — combine with Binary "and"
    if len(conditions) > 1:
        result: Expr = conditions[0]
        for cond in conditions[1:]:
            result = Binary("and", result, cond)
        return result
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

    # Issue #871: Handle DollarConditional as a condition-guarding construct.
    # If a DollarConditional's condition references domain indices, treat it
    # like a conditioned Sum/Prod — the condition guards the variable access.
    if isinstance(expr, DollarConditional):
        cond = expr.condition
        # Check if the dollar condition involves any of the variable's domain indices
        cond_refs = _collect_symbolref_names(cond)
        cond_overlaps = bool(cond_refs & var_domain_set)

        child_result = _collect_access_conditions(
            expr.value_expr,
            var_name,
            var_domain_set,
            has_enclosing_condition=has_enclosing_condition or cond_overlaps,
        )
        if child_result is not None:
            if not child_result and cond_overlaps:
                # Variable found in value_expr with no inner condition,
                # and this DollarConditional's condition restricts a relevant index.
                return [cond]
            return child_result
        return None

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

    # Issue #springchain: Pre-compute implicit lead/lag domain conditions for
    # all equations.  Equations like delta_x_eq(n).. x(n) - x(n-1) have no
    # explicit condition but GAMS silently skips instances with out-of-range
    # IndexOffset.  The stationarity builder needs to guard the Jacobian terms
    # with these implicit conditions so that _extract_all_conditioned_guard can
    # detect when ALL terms are conditional and add a domain restriction.
    lead_lag_conditions = _compute_lead_lag_conditions(kkt.model_ir)

    # Cache for _has_unconditioned_access to avoid re-walking equation ASTs
    # for each variable that reaches Stage 4.
    unconditioned_cache: dict[str, bool] = {}

    # For each variable, generate either indexed or scalar stationarity equation
    for var_name, instances in var_groups.items():
        # Get variable definition to determine domain
        if var_name not in kkt.model_ir.variables:
            continue

        var_def = kkt.model_ir.variables[var_name]

        # Determine which equation to skip in stationarity building.
        # Skip objdef equation ONLY for the objective variable itself,
        # UNLESS Strategy 1 was applied. Issue #1088: Other variables
        # that appear in the defining equation need its Jacobian contribution.
        skip_eq = (
            obj_info.defining_equation
            if not kkt.model_ir.strategy1_applied and var_name.lower() == obj_info.objvar.lower()
            else None
        )

        if var_def.domain:
            # Issue #903/#1008/#1009: Always generate a single indexed stationarity
            # equation for indexed variables. Non-uniform bounds are handled by
            # the complementarity builder using indexed parameters, so bound
            # multipliers are always indexed (keyed at (var_name, ())).
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
            access_cond = _find_variable_access_condition(var_name, var_def.domain, kkt.model_ir)

            # Issue #759: If no dollar-condition was found, check whether the
            # variable is consistently accessed with a named subset index in
            # place of one of its declared domain indices (e.g., u(m,ku) where
            # the declared domain is (m,k)).  Use the subset membership as the
            # stationarity equation condition so the terminal-period instances
            # are excluded from the MCP pairing.
            if access_cond is None:
                access_cond = _find_variable_subset_condition(
                    var_name, var_def.domain, kkt.model_ir
                )

            # Issue #877: If no condition was found via access patterns or
            # subset analysis, check if ALL additive terms in the stationarity
            # expression are DollarConditional.  This happens when every
            # equation referencing the variable has a dollar condition (e.g.,
            # d2 in worst is only defined by dd2$pdata(...,"strike")).  Without
            # a guard, excluded instances produce 0 =E= 0, causing MCP errors.
            if access_cond is None:
                access_cond = _extract_all_conditioned_guard(
                    stat_expr,
                    var_def.domain,
                    kkt.model_ir,
                    lead_lag_conditions=lead_lag_conditions,
                )

            # Stage 4 (Issue #1112): Check gradient conditions.
            # If the objective gradient for this variable was computed from a
            # conditioned sum (e.g., sum((i,j)$xw(i,j), ...)), the gradient
            # carries an embedded condition that should become an equation-level
            # guard on the stationarity equation.
            # Only apply when there are NO unconditioned accesses — if a
            # constraint references the variable without a dollar condition,
            # those stationarity instances are genuinely required and must not
            # be suppressed by a gradient-derived guard.
            # Note: this block is inside `if var_def.domain:` so scalar
            # variables are structurally excluded.  _has_unconditioned_access
            # also conservatively returns True for empty domains as a safeguard.
            if access_cond is None and var_name in kkt.gradient_conditions:
                if var_name not in unconditioned_cache:
                    unconditioned_cache[var_name] = _has_unconditioned_access(
                        var_name, var_def.domain, kkt.model_ir
                    )
                if not unconditioned_cache[var_name]:
                    access_cond = kkt.gradient_conditions[var_name]

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

    # Issue #826: Detect empty stationarity equations (LHS == Const(0.0)).
    # This happens when the stationarity builder can't propagate derivatives
    # through subset access patterns (e.g., decomp's lam(ss) accessed via
    # sum(s, ...) where s ⊂ ss). Record the variables so the emitter can
    # fix them to 0. Keep the equations in the dict so MCP pairing still
    # works (GAMS allows empty equations if the paired variable is fixed).
    empty_stat_vars: set[str] = set()
    for eq_name, eq_def in stationarity.items():
        lhs, _ = eq_def.lhs_rhs
        if isinstance(lhs, Const) and lhs.value == 0.0:
            suffix = eq_name[5:] if eq_name.startswith("stat_") else eq_name
            # Find the variable name: try exact match first, then longest prefix match
            var_name = suffix
            if suffix not in kkt.model_ir.variables:
                candidates = [
                    vn
                    for vn in kkt.model_ir.variables
                    if suffix == vn or suffix.startswith(vn + "_")
                ]
                if candidates:
                    # Use the longest matching variable name to avoid ambiguous prefixes
                    var_name = max(candidates, key=len)
            empty_stat_vars.add(var_name)
    kkt.empty_stationarity_vars = empty_stat_vars

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
        if objvar and var_name.lower() == objvar.lower():
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

    # Issue #949 / #1010: The gradient term may contain free indices not in
    # the variable domain (e.g. subset index 't' when domain uses 'tt').
    # When the uncontrolled index is a subset of a domain index, wrap in
    # sum(t$(sameas(t,tt)), ...) to select the matching element — this
    # preserves per-element semantics instead of summing over all elements.
    # Fall back to unconditional Sum wrapping for indices with no
    # subset→superset mapping.  This must be done BEFORE Jacobian terms are
    # added, because the Jacobian terms have their own Sum wrapping.
    domain_lower = tuple(d.lower() for d in domain)
    var_domain_set = set(domain_lower)
    free_in_grad = _collect_free_indices(expr, kkt.model_ir)
    uncontrolled_grad = free_in_grad - var_domain_set
    if uncontrolled_grad:
        remaining_uncontrolled: set[str] = set()
        for idx in sorted(uncontrolled_grad):
            superset = _find_superset_in_domain(idx, domain_lower, kkt.model_ir)
            if superset is not None:
                # Wrap in sum(idx$(sameas(idx,superset)), ...) to select
                # the single matching element
                sameas_cond: Expr = Call("sameas", (SymbolRef(idx), SymbolRef(superset)))
                expr = Sum((idx,), expr, condition=sameas_cond)
            else:
                remaining_uncontrolled.add(idx)
        if remaining_uncontrolled:
            sum_indices = tuple(sorted(remaining_uncontrolled))
            expr = Sum(sum_indices, expr)

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

    Uses a representative instance with a non-zero gradient component.
    When some instances have zero gradient (e.g., d(n) where the objective
    only depends on d(l) with l ⊂ n), the first instance may have a zero
    gradient.  Scanning for a non-zero representative ensures the gradient
    term is not incorrectly set to zero.

    Issue #1131: When only a strict subset of instances have non-zero
    gradients, the gradient term must be guarded with a sameas() condition
    so it applies only to those instances.  Without this, the gradient
    constant (e.g., -1 from the objective) is applied to ALL instances of
    the indexed stationarity equation, making it infeasible for the
    instances that should have zero gradient.
    """
    if not instances:
        return Const(0.0)

    # Issue #1086: Find a representative instance with non-zero gradient.
    # The first instance may have zero gradient if the objective only
    # depends on a subset of the variable's domain.
    # Also collect ALL non-zero instances for the sameas guard (Issue #1131).
    nonzero_instances: list[tuple[int, tuple[str, ...]]] = []
    seen_nz: set[tuple[int, tuple[str, ...]]] = set()
    col_id, var_indices = instances[0]
    grad_component = kkt.gradient.get_derivative(col_id)

    if grad_component is not None and not (
        isinstance(grad_component, Const) and grad_component.value == 0
    ):
        nonzero_instances.append((col_id, var_indices))
        seen_nz.add((col_id, var_indices))
    else:
        grad_component = None  # Normalize to None for the search below

    for c_id, v_idx in instances[1:]:
        gc = kkt.gradient.get_derivative(c_id)
        if gc is not None and not (isinstance(gc, Const) and gc.value == 0):
            if grad_component is None:
                col_id = c_id
                grad_component = gc
            if (c_id, v_idx) not in seen_nz:
                nonzero_instances.append((c_id, v_idx))
                seen_nz.add((c_id, v_idx))

    if grad_component is None:
        return Const(0.0)

    # Build element-to-set mapping from all instances
    # This maps each element label to its corresponding set name
    element_to_set = _build_element_to_set_mapping(kkt.model_ir, domain, instances)

    # Replace element-specific indices with domain indices in the gradient
    # Issue #620: Pass domain as equation_domain for subset/superset substitution
    expr = _replace_indices_in_expr(
        grad_component, domain, element_to_set, kkt.model_ir, equation_domain=domain
    )

    # Issue #1131: If only a strict subset of instances have non-zero
    # gradients, guard with sameas() so the gradient applies only to those.
    # E.g., for objective "ht('h50')", the gradient is -1 only for h50;
    # without the guard, stat_ht(h) would have -1 for ALL h.
    if len(nonzero_instances) < len(instances) and nonzero_instances:
        guard = _build_sameas_guard_for_instances(
            domain, nonzero_instances, instances, kkt.model_ir
        )
        if guard is not None:
            expr = DollarConditional(value_expr=expr, condition=guard)

    return expr


def _build_sameas_guard_for_instances(
    domain: tuple[str, ...],
    nonzero_instances: list[tuple[int, tuple[str, ...]]],
    all_instances: list[tuple[int, tuple[str, ...]]],
    model_ir: ModelIR,
) -> Expr | None:
    """Build a sameas guard that selects only the non-zero instances.

    Returns None if no guard is needed (all instances are covered).

    Uses per-dimension factorization with named-subset detection when
    possible (compact output for 1D or Cartesian cases), falling back to
    exact OR-of-ANDs via _build_tuple_or_guard() when the non-zero
    entries don't form a Cartesian product over the instance space.
    """
    ndim = len(domain)
    if ndim == 0:
        return None

    nonzero_indices = [idx for _, idx in nonzero_instances]

    nonzero_idx_set = {tuple(v.lower() for v in idx) for idx in nonzero_indices}
    all_idx_set = {tuple(v.lower() for v in idx) for _, idx in all_instances}
    if nonzero_idx_set >= all_idx_set:
        return None

    # Per-dimension analysis: collect unique elements per dimension
    per_dim_nz_lc: list[set[str]] = [set() for _ in range(ndim)]
    per_dim_all_lc: list[set[str]] = [set() for _ in range(ndim)]
    per_dim_nz_orig: list[dict[str, str]] = [{} for _ in range(ndim)]

    for idx in nonzero_indices:
        for d, v in enumerate(idx):
            lc = v.lower()
            per_dim_nz_lc[d].add(lc)
            if lc not in per_dim_nz_orig[d]:
                per_dim_nz_orig[d][lc] = v

    for _, idx in all_instances:
        for d, v in enumerate(idx):
            per_dim_all_lc[d].add(v.lower())

    # Build per-dimension guards (with named-subset detection)
    dim_guards: list[Expr] = []
    for d in range(ndim):
        if per_dim_nz_lc[d] >= per_dim_all_lc[d]:
            continue  # This dimension is fully covered

        dom_idx = domain[d]
        nz_lc = per_dim_nz_lc[d]

        if len(nz_lc) == 1:
            lc_val = next(iter(nz_lc))
            orig_val = per_dim_nz_orig[d][lc_val]
            dim_guards.append(
                Call("sameas", (SymbolRef(dom_idx), SymbolRef(_quote_sameas_uel(orig_val))))
            )
        else:
            # Try to find a matching named subset
            subset_name = _find_matching_subset(dom_idx, nz_lc, model_ir)
            if subset_name is not None:
                dim_guards.append(SetMembershipTest(subset_name, (SymbolRef(dom_idx),)))
            else:
                or_parts: list[Expr] = []
                for lc_val in sorted(nz_lc):
                    orig_val = per_dim_nz_orig[d][lc_val]
                    or_parts.append(
                        Call(
                            "sameas",
                            (SymbolRef(dom_idx), SymbolRef(_quote_sameas_uel(orig_val))),
                        )
                    )
                or_expr: Expr = or_parts[0]
                for part in or_parts[1:]:
                    or_expr = Binary("or", or_expr, part)
                dim_guards.append(or_expr)

    if not dim_guards:
        # Per-dimension says fully covered but tuple-level may not be
        # (non-Cartesian entries). Fall back to exact tuple matching.
        if nonzero_idx_set >= all_idx_set:
            return None
        return _build_tuple_or_guard(domain, nonzero_indices)

    # Validate that per-dimension factorization is exact: the Cartesian
    # product of per-dim selections must equal the nonzero set.  If the
    # nonzero tuples are non-Cartesian, the AND of per-dim guards would
    # over-select (enabling zero-gradient instances).  Fall back to
    # exact tuple-OR in that case.
    # Filter existing tuples through per-dim selections (O(|all_instances|))
    # instead of materializing the full Cartesian product which can explode.
    selected_lc = [
        per_dim_nz_lc[d] if per_dim_nz_lc[d] < per_dim_all_lc[d] else per_dim_all_lc[d]
        for d in range(ndim)
    ]
    filtered_idx_set = {
        idx for idx in all_idx_set if all(idx[d] in selected_lc[d] for d in range(ndim))
    }
    if filtered_idx_set != nonzero_idx_set:
        return _build_tuple_or_guard(domain, nonzero_indices)

    guard: Expr = dim_guards[0]
    for dg in dim_guards[1:]:
        guard = Binary("and", guard, dg)
    return guard


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
            # Protect sum/prod index variables from being replaced.
            # AD-generated indices like "j__" or "i__" are not in the model's
            # element_to_set mapping, so _replace_matching_indices falls through
            # to a default path that replaces them with the declared domain
            # target_set. Adding them as self-mappings prevents this.
            inner_e2s = element_to_set
            if element_to_set is not None and index_sets:
                # ChainMap overlays self-mappings for sum indices on the base mapping.
                # The base is read-only here (only lookups, no mutations), so the
                # cast is safe even when element_to_set is a Mapping.
                inner_e2s = ChainMap(
                    {idx: idx for idx in index_sets}, element_to_set  # type: ignore[arg-type]
                )
            new_body = _replace_indices_in_expr(body, domain, inner_e2s, model_ir, equation_domain)
            new_condition = (
                _replace_indices_in_expr(condition, domain, inner_e2s, model_ir, equation_domain)
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
            # Issue #1086: Use the set's declared domain for positional resolution
            # to avoid ambiguity when an element belongs to multiple sets.
            # E.g., arc(n,np) with domain (n,np): position 1 maps to np, not n.
            smt_domain: tuple[str, ...] | None = None
            if model_ir and smt.set_name in model_ir.sets:
                smt_domain = model_ir.sets[smt.set_name].domain
            # Build equation domain set for checking if element came from equation index
            eq_domain_lower = {d.lower() for d in equation_domain} if equation_domain else set()
            new_idx_list: list[Expr] = []
            for pos, idx in enumerate(smt.indices):
                if (
                    smt_domain
                    and model_ir is not None
                    and pos < len(smt_domain)
                    and isinstance(idx, SymbolRef)
                    and element_to_set
                    and idx.name in element_to_set
                    # Only use positional resolution for concrete element values,
                    # not for indices that are already set/alias names
                    and idx.name not in model_ir.sets
                    and idx.name not in model_ir.aliases
                ):
                    # Issue #1086: If the element maps via element_to_set to a
                    # set name that is in the equation domain, use that mapping
                    # instead of positional resolution. The equation domain
                    # index is authoritative for elements that originated from
                    # equation instance substitution.
                    mapped_set = element_to_set[idx.name]
                    if mapped_set.lower() in eq_domain_lower:
                        new_idx_list.append(SymbolRef(mapped_set))
                    else:
                        # Use set's declared domain for this position
                        new_idx_list.append(SymbolRef(smt_domain[pos]))
                else:
                    new_idx_list.append(
                        _replace_indices_in_expr(
                            idx, domain, element_to_set, model_ir, equation_domain
                        )
                    )
            new_idx = tuple(new_idx_list)
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


def _is_related_to_eq_domain(
    target_set: str,
    equation_domain: tuple[str, ...],
    model_ir: ModelIR | None,
) -> bool:
    """Check if target_set is related to any set in the equation domain.

    Returns True if target_set is an alias of, superset of, or shares an
    alias root with any set in the equation domain.  Used to distinguish
    between truly independent sets (like 'lim' vs. equation domain (cf,q))
    and related sets (like 'mp' which aliases 'm' in the equation domain).
    """
    if not model_ir or not equation_domain:
        return False

    # Resolve alias target of target_set
    target_lower = target_set.lower()
    target_alias = model_ir.aliases.get(target_set) or model_ir.aliases.get(target_lower)
    target_root = target_lower
    if target_alias is not None:
        t = target_alias.target if hasattr(target_alias, "target") else target_alias
        if isinstance(t, str):
            target_root = t.lower()

    # Check if target_root matches any equation domain set or its alias root
    for eq_set in equation_domain:
        eq_lower = eq_set.lower()
        eq_alias = model_ir.aliases.get(eq_set) or model_ir.aliases.get(eq_lower)
        eq_root = eq_lower
        if eq_alias is not None:
            t = eq_alias.target if hasattr(eq_alias, "target") else eq_alias
            if isinstance(t, str):
                eq_root = t.lower()
        if target_root == eq_root:
            return True
        # Check if target_set is a superset of eq_set
        eq_set_def = model_ir.sets.get(eq_set) or model_ir.sets.get(eq_lower)
        if eq_set_def and hasattr(eq_set_def, "domain") and eq_set_def.domain:
            if target_lower in {p.lower() for p in eq_set_def.domain}:
                return True
            if target_root in {p.lower() for p in eq_set_def.domain}:
                return True

    return False


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
    eq_domain_lower: set[str] = {s.lower() for s in equation_domain} if equation_domain else set()
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
                    # Issue #862: When the same element appears at multiple positions
                    # of a variable with aliased domains (e.g., x("h1","h1") with
                    # domain (i,j) where j aliases i), the gradient path's flat dict
                    # loses position info and maps all occurrences to the first set.
                    # Fix: if the mapped set differs from the declared domain target
                    # at this position AND they share the same alias root, use the
                    # declared domain to preserve positional semantics.
                    # Guard: only apply when element_to_set is a plain dict (gradient
                    # path), NOT a ChainMap (Jacobian path has position-specific
                    # overrides that are already correct).
                    if (
                        declared_domain
                        and i < len(declared_domain)
                        and mapped_set.lower() != target_set.lower()
                        and model_ir
                        and not isinstance(element_to_set, ChainMap)
                    ):
                        mapped_alias = model_ir.aliases.get(mapped_set)
                        target_alias = model_ir.aliases.get(target_set)
                        mapped_root = (
                            mapped_alias.target.lower()
                            if mapped_alias is not None
                            else mapped_set.lower()
                        )
                        target_root = (
                            target_alias.target.lower()
                            if target_alias is not None
                            else target_set.lower()
                        )
                        if mapped_root == target_root:
                            mapped_set = target_set
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
                    # Issue #879: When element_to_set is a ChainMap (Jacobian path
                    # with constraint-specific overrides), and the element maps to a
                    # subset of the declared domain target, use the subset index.
                    # E.g., delta("light-ind") with declared_domain=("i",):
                    # ChainMap maps "light-ind" → "it" (subset of i). Use "it".
                    elif (
                        isinstance(element_to_set, ChainMap) and idx in element_to_set and model_ir
                    ):
                        mapped = element_to_set[idx]
                        if mapped != target_set:
                            mapped_def = model_ir.sets.get(mapped)
                            if (
                                mapped_def
                                and mapped_def.domain
                                and target_set.lower() in {p.lower() for p in mapped_def.domain}
                            ):
                                # mapped is a subset of target_set — use subset
                                new_indices.append(mapped)
                            elif (
                                eq_domain_lower
                                and mapped.lower() in eq_domain_lower
                                and _shares_alias_root(mapped, target_set, model_ir)
                            ):
                                # Issue #1111: When the constraint-specific mapping
                                # gives the equation domain index (e.g., p1 → i) but
                                # the declared domain at this position is an alias
                                # (e.g., j), prefer the equation domain index.
                                # Using the alias creates an uncontrolled free index.
                                new_indices.append(mapped)
                            else:
                                new_indices.append(target_set)
                        else:
                            new_indices.append(target_set)
                    else:
                        # Issue #730: When the declared domain target is an alias
                        # or a set not in the equation domain, prefer the
                        # element_to_set mapping if it maps to a set that IS in the
                        # equation domain.  This fixes the case where a sum over an
                        # alias (e.g., j aliasing i) collapses and both positions of
                        # a parameter like a("agricult","agricult") should map to the
                        # same equation-domain index "i", not to the alias "j".
                        # Issue #766: Do NOT apply this override when target_set is a
                        # subset of a set in the equation domain — in that case the
                        # narrower declared domain is intentional (e.g. c(p,t) declared
                        # over t which is a subset of tt in stat_x(p,tt)).
                        target_is_subset_of_eq_domain = False
                        if (
                            equation_domain
                            and model_ir
                            and target_set.lower() not in eq_domain_lower
                        ):
                            target_set_def = model_ir.sets.get(target_set)
                            if (
                                target_set_def
                                and hasattr(target_set_def, "domain")
                                and target_set_def.domain
                            ):
                                if any(p.lower() in eq_domain_lower for p in target_set_def.domain):
                                    target_is_subset_of_eq_domain = True
                        if (
                            not target_is_subset_of_eq_domain
                            and equation_domain
                            and idx in element_to_set
                            and element_to_set[idx].lower() in eq_domain_lower
                            and target_set.lower() not in eq_domain_lower
                        ):
                            new_indices.append(element_to_set[idx])
                        elif (
                            equation_domain
                            and target_set.lower() not in eq_domain_lower
                            and not target_is_subset_of_eq_domain
                            and not _is_related_to_eq_domain(target_set, equation_domain, model_ir)
                        ):
                            # Issue #1099: The declared domain set is completely
                            # independent of the equation domain (not in it, not a
                            # subset of it, not an alias of any eq domain set, not
                            # a superset).  The concrete element (e.g., "upper"
                            # from set lim, or a quoted literal like '"upper"') is
                            # a fixed literal in the equation condition — preserve
                            # it as-is rather than replacing with the set name.
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


def _collect_free_indices(expr: Expr, model_ir: ModelIR) -> set[str]:
    """Collect all free (unbound) symbolic set indices in an expression.

    Walks the expression tree and returns the set of index names that appear
    in VarRef/ParamRef/MultiplierRef indices but are NOT bound by any enclosing
    Sum or Prod node.

    Only names that are known set or alias names (from model_ir) are considered
    indices. Literal strings (e.g. "domestic", "storage-c") are ignored.
    IndexOffset objects are traversed: their ``base`` is treated as a potential
    set index and their ``offset`` expression is walked for nested indices.

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
                elif isinstance(idx, IndexOffset):
                    free |= _walk(idx, bound)
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
        if isinstance(e, IndexOffset):
            # Lead/lag expression: base is a set index; offset may contain SymbolRef
            free = set()
            if _is_known_set(e.base) and e.base.lower() not in bound:
                free.add(e.base.lower())
            free |= _walk(e.offset, bound)
            return free
        # Const, etc. — no indices
        return set()

    return _walk(expr, frozenset())


def _resolve_alias_target(name: str, model_ir: ModelIR) -> str:
    """Resolve an alias name transitively to its canonical (non-alias) target.

    Follows ``model_ir.aliases[name].target`` until a non-alias name is
    reached or a cycle is detected.  All names are normalised to lowercase.
    """
    current = name.lower()
    seen: set[str] = set()

    while current not in seen:
        seen.add(current)
        alias_def = model_ir.aliases.get(current)
        if alias_def is None:
            break
        target = (
            alias_def.target.lower() if hasattr(alias_def, "target") else str(alias_def).lower()
        )
        if target == current:
            break  # self-loop
        current = target

    return current


def _shares_alias_root(name_a: str, name_b: str, model_ir: ModelIR) -> bool:
    """Return True if two set/alias names resolve to the same canonical root."""
    return _resolve_alias_target(name_a, model_ir) == _resolve_alias_target(name_b, model_ir)


def _get_or_create_fresh_alias(
    root_set: str,
    used_names: set[str],
    model_ir: ModelIR,
) -> str:
    """Find an existing unused alias or create a fresh one for *root_set*.

    Issue #1104: In dimension-mismatch stationarity, when constraint-domain
    indices are aliases of variable-domain indices, the summation variable
    needs a distinct name that doesn't shadow the outer equation domain.

    Searches existing aliases of *root_set* first.  If all are in *used_names*,
    creates a new alias ``<root_set>__kkt<N>`` and registers it in the model IR.

    Args:
        root_set: Canonical (non-alias) base set name.
        used_names: Set of names already in scope (var_domain, mult_domain,
            other aliases used in the expression) — all **lowercased**.
        model_ir: Model IR (may be mutated to register a new alias).

    Returns:
        A lowercase alias name suitable for use as a summation index.
    """
    # Search existing aliases targeting root_set
    for aname, adef in model_ir.aliases.items():
        target = adef.target if hasattr(adef, "target") else str(adef)
        if target.lower() == root_set.lower() and aname.lower() not in used_names:
            return aname.lower()

    # Create a fresh alias
    counter = 1
    while True:
        candidate = f"{root_set}__kkt{counter}"
        if candidate.lower() not in used_names and candidate.lower() not in model_ir.aliases:
            model_ir.aliases[candidate] = AliasDef(name=candidate, target=root_set)
            return candidate
        counter += 1


def _find_matching_subset(parent_set: str, values: set[str], model_ir: ModelIR) -> str | None:
    """Find a named subset whose members exactly match *values*.

    Searches ``model_ir.sets`` for a ``SetDef`` whose ``domain`` references
    *parent_set* (or an alias of it) and whose ``members`` (case-insensitive)
    equal *values*.  Returns the subset name if found, else ``None``.
    """
    canonical_parent = _resolve_alias_target(parent_set, model_ir)
    for set_def in model_ir.sets.values():
        if not set_def.domain or len(set_def.domain) != 1:
            continue
        dom_target = _resolve_alias_target(set_def.domain[0], model_ir)
        if dom_target != canonical_parent:
            continue
        if {m.lower() for m in set_def.members} == {v.lower() for v in values}:
            return set_def.name
    return None


def _quote_sameas_uel(val: str) -> str:
    """Quote a UEL literal for use in ``sameas(dom, '...')``.

    Handles pre-quoted values and doubled-quote normalization consistently
    with ``_quote_uel`` in ``emit_gams.py`` and ``_sanitize_set_element``
    in ``original_symbols.py``.

    - Already single-quoted (e.g. ``'SAE 10'``) → returned as-is.
    - Doubled quotes from parser (e.g. ``''SAE 10''``) → normalized to
      single-quoted ``'SAE 10'``.
    - Unquoted → embedded single quotes escaped by doubling, then wrapped.
    """
    val = val.strip()

    # Normalize doubled single quotes (parser artifact: ''label'' → 'label')
    if len(val) >= 4 and val.startswith("''") and val.endswith("''"):
        val = "'" + val[2:-2] + "'"

    # Already single-quoted → return as-is
    if len(val) >= 2 and val.startswith("'") and val.endswith("'"):
        return val

    # Already double-quoted → return as-is
    if len(val) >= 2 and val.startswith('"') and val.endswith('"'):
        return val

    # Unquoted: escape embedded single quotes and wrap
    escaped = val.replace("'", "''")
    return f"'{escaped}'"


def _build_tuple_or_guard(
    var_domain: tuple[str, ...],
    all_fixed: list[tuple[str, ...]],
) -> Expr:
    """Build an OR-of-ANDs guard over exact entry tuples.

    For each entry tuple, build ``sameas(d0,'v0') and sameas(d1,'v1') ...``,
    then OR all such conjunctions together.
    """
    conjunctions: list[Expr] = []
    # Deduplicate (case-insensitive) and sort for deterministic output.
    # Preserve original casing for emitted sameas guards.
    seen: set[tuple[str, ...]] = set()
    for idx in all_fixed:
        key = tuple(v.lower() for v in idx)
        if key in seen:
            continue
        seen.add(key)
        and_parts: list[Expr] = []
        for dom_idx, fixed_val in zip(var_domain, idx, strict=True):
            and_parts.append(
                Call(
                    "sameas",
                    (SymbolRef(dom_idx), SymbolRef(_quote_sameas_uel(fixed_val))),
                )
            )
        conj: Expr = and_parts[0]
        for part in and_parts[1:]:
            conj = Binary("and", conj, part)
        conjunctions.append(conj)
    # Sort by repr for deterministic output
    conjunctions.sort(key=repr)
    result: Expr = conjunctions[0]
    for c in conjunctions[1:]:
        result = Binary("or", result, c)
    return result


def _build_sameas_guard(
    var_domain: tuple[str, ...],
    instances: list[tuple[int, tuple[str, ...]]],
    entries: list[tuple[int, int]],
    kkt: KKTSystem,
) -> Expr | None:
    """Build a guard condition for scalar-constraint multiplier terms.

    Issue #767 / #764: When a scalar constraint references only a subset of
    an indexed variable's instances, the multiplier term must be guarded so
    that it only appears for the relevant instances in the stationarity
    equation.

    The original implementation used only ``entries[0]`` which is correct for
    the single-entry ``.fx`` case but wrong when multiple entries exist (e.g.
    a scalar equation that sums over a subset of the variable's domain).

    This version collects ALL entry indices and builds the minimal guard:
    - If entries cover all instance tuples → no guard needed.
    - For each dimension where entry values are a strict subset:
      - 1 value  → ``sameas(dom, 'val')``
      - multiple → OR-disjunction of sameas calls, or subset membership if
        a named subset matches.
    - Per-dimension guards are ANDed together.
    - If per-dimension analysis says "fully covered" but actual entry tuples
      don't form a Cartesian product over all instance tuples, falls back to
      OR-of-ANDs over exact entry tuples.
    """
    assert kkt.gradient.index_mapping is not None

    # Collect index tuples from ALL entries
    all_fixed: list[tuple[str, ...]] = []
    for _, col_id in entries:
        _, idx = kkt.gradient.index_mapping.col_to_var[col_id]
        if idx and len(idx) == len(var_domain):
            all_fixed.append(idx)

    if not all_fixed:
        return None

    # Compute per-dimension unique values from entries and from all instances.
    # Keep lowercase sets for coverage comparison, but preserve original casing
    # for emitted sameas guards (UELs are case-sensitive in GAMS).
    ndim = len(var_domain)
    per_dim_entry_lc: list[set[str]] = [set() for _ in range(ndim)]
    per_dim_all_lc: list[set[str]] = [set() for _ in range(ndim)]
    # Map lowercase → original-casing representative per dimension
    per_dim_entry_orig: list[dict[str, str]] = [{} for _ in range(ndim)]

    for idx in all_fixed:
        for d, v in enumerate(idx):
            lc = v.lower()
            per_dim_entry_lc[d].add(lc)
            if lc not in per_dim_entry_orig[d]:
                per_dim_entry_orig[d][lc] = v  # first-seen casing wins

    for _, idx in instances:
        for d, v in enumerate(idx):
            per_dim_all_lc[d].add(v.lower())

    # Build per-dimension guards where entry values are a strict subset
    dim_guards: list[Expr] = []
    for d in range(ndim):
        if per_dim_entry_lc[d] >= per_dim_all_lc[d]:
            # Entries cover all values in this dimension — no guard needed
            continue

        dom_idx = var_domain[d]
        entry_vals_lc = per_dim_entry_lc[d]

        if len(entry_vals_lc) == 1:
            # Single value — simple sameas guard (use original casing)
            lc_val = next(iter(entry_vals_lc))
            orig_val = per_dim_entry_orig[d][lc_val]
            dim_guards.append(
                Call("sameas", (SymbolRef(dom_idx), SymbolRef(_quote_sameas_uel(orig_val))))
            )
        else:
            # Multiple values — try to find a matching named subset
            subset_name = _find_matching_subset(dom_idx, entry_vals_lc, kkt.model_ir)
            if subset_name is not None:
                dim_guards.append(SetMembershipTest(subset_name, (SymbolRef(dom_idx),)))
            else:
                # OR-disjunction of sameas calls (use original casing, sorted by lowercase)
                or_parts: list[Expr] = []
                for lc_val in sorted(entry_vals_lc):
                    orig_val = per_dim_entry_orig[d][lc_val]
                    or_parts.append(
                        Call("sameas", (SymbolRef(dom_idx), SymbolRef(_quote_sameas_uel(orig_val))))
                    )
                or_expr: Expr = or_parts[0]
                for part in or_parts[1:]:
                    or_expr = Binary("or", or_expr, part)
                dim_guards.append(or_expr)

    if not dim_guards:
        # Per-dimension analysis says every dimension is fully covered.
        # Verify full tuple coverage: per-dimension factorisation can be
        # incorrect when entries don't form a Cartesian product over the
        # instance space.  E.g., entries {(a,x),(b,y)} cover {a,b}×{x,y}
        # per-dimension but miss tuples (a,y) and (b,x).
        entry_tuples = {tuple(v.lower() for v in idx) for idx in all_fixed}
        instance_tuples = {tuple(v.lower() for v in idx) for _, idx in instances}
        if entry_tuples >= instance_tuples:
            return None
        # Tuples don't cover all instances — fall back to OR-of-ANDs over
        # exact entry tuples.
        return _build_tuple_or_guard(var_domain, all_fixed)

    # AND all dimension guards together
    guard: Expr = dim_guards[0]
    for dg in dim_guards[1:]:
        guard = Binary("and", guard, dg)
    return guard


def _find_superset_in_domain(
    subset_idx: str,
    var_domain: tuple[str, ...],
    model_ir: ModelIR,
) -> str | None:
    """Find the superset domain index for a given subset index.

    Issue #1010: Given an uncontrolled index like 't' and a variable domain
    tuple like ('p', 'tt'), check if 't' is a declared subset of any domain
    index (e.g., t(tt) means t ⊂ tt).  Returns the superset domain index
    name (lowercase) if found, None otherwise.

    The domain is accepted as an ordered tuple so that when multiple domain
    indices resolve to the same canonical target the first positional match
    is selected deterministically.

    Also handles aliases transitively: alias chains (alias→alias) and
    multiple aliases to the same target set are resolved by following
    ``model_ir.aliases`` to their canonical (non-alias) target before
    comparison.
    """
    # Resolve subset_idx through any alias chain to the canonical set name
    canonical_subset = _resolve_alias_target(subset_idx, model_ir)

    # Check if the canonical set has a single-element domain (i.e. is a subset)
    if canonical_subset in model_ir.sets:
        set_def = model_ir.sets[canonical_subset]
        if hasattr(set_def, "domain") and len(set_def.domain) == 1:
            parent = set_def.domain[0]
            if not isinstance(parent, str):
                parent = str(parent)
            # Resolve the parent through alias chains to its canonical target
            canonical_parent = _resolve_alias_target(parent, model_ir)

            # Compare the fully-resolved canonical parent against each
            # domain index's fully-resolved canonical target and return
            # the actual in-scope domain index name when a match is found.
            # Iterating the ordered tuple ensures the first positional
            # match is selected deterministically.
            for dom_idx in var_domain:
                canonical_dom = _resolve_alias_target(dom_idx, model_ir)
                if canonical_dom == canonical_parent:
                    return dom_idx

    return None


def _match_subset_domain(
    mult_domain: tuple[str, ...],
    var_domain: tuple[str, ...],
    model_ir: ModelIR,
) -> dict[str, str] | None:
    """Try to match mult_domain indices to var_domain indices via subset/alias.

    Issue #1041: When a constraint is indexed by a subset (e.g., ``(ii, jj)``)
    and the variable is indexed by the parent set (e.g., ``(i, j)`` or
    ``(i, j, jwt)``), the indices appear disjoint by name but are related
    by set inclusion.

    Handles both equal-length domains (e.g., ``(ii, jj)`` vs ``(i, j)``)
    and shorter mult domains (e.g., ``(ii, jj)`` vs ``(i, j, jwt)``).
    Each mult index must find exactly one matching var index.

    Returns a rename map ``{mult_idx: var_idx}`` if all mult indices match,
    or ``None`` if no full match is possible.

    Keys are lowercased (``str(mult_idx).lower()``); values preserve the
    original ``var_domain`` casing.  Callers should use lowercased index
    names for lookups (e.g., ``_rewrite_subset_to_superset`` normalizes
    via ``idx.lower()``).
    """
    if len(mult_domain) > len(var_domain):
        return None

    rename_map: dict[str, str] = {}
    used_var_positions: set[int] = set()

    # Pre-resolve canonical targets for all var_domain positions.
    var_canons = [_resolve_alias_target(v, model_ir) for v in var_domain]

    for p, mult_idx in enumerate(mult_domain):
        canon_mult = _resolve_alias_target(mult_idx, model_ir)

        # Also resolve the canonical subset parent if mult_idx is a subset
        canon_parent: str | None = None
        if canon_mult in model_ir.sets:
            set_def = model_ir.sets[canon_mult]
            if hasattr(set_def, "domain") and len(set_def.domain) == 1:
                parent = set_def.domain[0]
                if not isinstance(parent, str):
                    parent = str(parent)
                canon_parent = _resolve_alias_target(parent, model_ir)

        def _try_match(k: int) -> bool:
            """Try to match mult_idx at var_domain position k."""
            if k in used_var_positions:
                return False
            canon_var = var_canons[k]
            if canon_mult == canon_var or (canon_parent is not None and canon_parent == canon_var):
                mult_key = str(mult_idx).lower()
                var_key = str(var_domain[k]).lower()
                if mult_key != var_key:
                    rename_map[mult_key] = var_domain[k]
                used_var_positions.add(k)
                return True
            return False

        # Prefer same-position match first when lengths align, to avoid
        # greedy first-match mapping to the wrong position when multiple
        # var_domain positions resolve to the same canonical set.
        matched = False
        if p < len(var_domain):
            matched = _try_match(p)
        if not matched:
            for k in range(len(var_domain)):
                if k == p:
                    continue  # already tried
                if _try_match(k):
                    matched = True
                    break

        if not matched:
            return None

    return rename_map


def _rewrite_subset_to_superset(expr: Expr, rename_map: dict[str, str]) -> Expr:
    """Rewrite index names in an expression tree according to rename_map.

    Issue #1010: When a gradient expression uses subset index 't' but the
    stationarity equation is indexed over superset 'tt', rewrite 't' → 'tt'
    so the index is controlled by the equation domain. This preserves
    per-element semantics (c(p,tt) varies with tt) rather than collapsing
    via Sum (sum(t, c(p,t)) is constant across tt).

    String indices in VarRef, ParamRef, MultiplierRef, EquationRef, and
    IndexOffset.base are rewritten. The rename_map keys must be
    lowercase-normalized (lookups use ``idx.lower()``); values are used
    as-is for replacement and may preserve original casing.
    """
    if not rename_map:
        return expr

    def _rewrite_indices(
        indices: tuple[str | IndexOffset, ...],
    ) -> tuple[str | IndexOffset, ...]:
        result: list[str | IndexOffset] = []
        for idx in indices:
            if isinstance(idx, str) and idx.lower() in rename_map:
                result.append(rename_map[idx.lower()])
            elif isinstance(idx, IndexOffset) and idx.base.lower() in rename_map:
                result.append(IndexOffset(rename_map[idx.base.lower()], idx.offset, idx.circular))
            else:
                result.append(idx)
        return tuple(result)

    if isinstance(expr, VarRef):
        return VarRef(expr.name, _rewrite_indices(expr.indices), expr.attribute)
    if isinstance(expr, ParamRef):
        return ParamRef(expr.name, _rewrite_indices(expr.indices))
    if isinstance(expr, MultiplierRef):
        return MultiplierRef(expr.name, _rewrite_indices(expr.indices))
    if isinstance(expr, EquationRef):
        return EquationRef(expr.name, _rewrite_indices(expr.indices), expr.attribute)
    if isinstance(expr, Binary):
        return Binary(
            expr.op,
            _rewrite_subset_to_superset(expr.left, rename_map),
            _rewrite_subset_to_superset(expr.right, rename_map),
        )
    if isinstance(expr, Unary):
        return Unary(expr.op, _rewrite_subset_to_superset(expr.child, rename_map))
    if isinstance(expr, Sum):
        new_body = _rewrite_subset_to_superset(expr.body, rename_map)
        new_cond = (
            _rewrite_subset_to_superset(expr.condition, rename_map)
            if expr.condition is not None
            else None
        )
        return Sum(expr.index_sets, new_body, new_cond)
    if isinstance(expr, Prod):
        new_body = _rewrite_subset_to_superset(expr.body, rename_map)
        new_cond = (
            _rewrite_subset_to_superset(expr.condition, rename_map)
            if expr.condition is not None
            else None
        )
        return Prod(expr.index_sets, new_body, new_cond)
    if isinstance(expr, Call):
        new_args = tuple(_rewrite_subset_to_superset(a, rename_map) for a in expr.args)
        return Call(expr.func, new_args)
    if isinstance(expr, DollarConditional):
        return DollarConditional(
            _rewrite_subset_to_superset(expr.value_expr, rename_map),
            _rewrite_subset_to_superset(expr.condition, rename_map),
        )
    if isinstance(expr, SetMembershipTest):
        new_indices = tuple(_rewrite_subset_to_superset(i, rename_map) for i in expr.indices)
        return SetMembershipTest(expr.set_name, new_indices)
    if isinstance(expr, SymbolRef):
        if expr.name.lower() in rename_map:
            return SymbolRef(rename_map[expr.name.lower()])
        return expr
    # Const, SetAttrRef, ModelAttrRef, etc. — no indices to rewrite
    return expr


def _compute_index_offset_key(
    eq_indices: tuple[str, ...],
    var_indices: tuple[str, ...],
    eq_domain: tuple[str, ...],
    var_domain: tuple[str, ...],
    model_ir: ModelIR,
    _domain_cache: dict | None = None,
) -> tuple[int, ...]:
    """Compute the positional offset between equation and variable indices.

    Issue #1045: For lead/lag equations, the equation instance and variable instance
    have different elements from the same domain set. This function computes the
    positional difference to group Jacobian entries by their offset pattern.

    For example, if totalcap("1990") has a Jacobian entry for k("1995"), and the
    set t = {"1990","1995","2000","2005","2010"}, then the offset is
    pos("1990") - pos("1995") = 0 - 1 = -1.

    Only computes offsets when the equation and variable share the same domain set
    at corresponding positions. If the domains differ (e.g., cdef(i) vs x(c) where
    i and c are different sets), the offset is 0.

    Args:
        eq_indices: Concrete equation instance indices
        var_indices: Concrete variable instance indices
        eq_domain: Equation domain set names
        var_domain: Variable domain set names
        model_ir: Model IR for set resolution
        _domain_cache: Optional cache dict for resolved set names and member→position
            maps. Populated on first use and reused across calls to avoid redundant
            resolve_set_members() lookups and O(n) list.index() scans.

    Returns:
        Tuple of integer offsets, one per index dimension. (0,0,...) means same-index.
        Falls back to (0,...) if positions can't be determined.
    """
    from ..ad.index_mapping import resolve_set_members

    if len(eq_indices) != len(var_indices):
        # Issue #1086: Different dimensionality (e.g., 1D equation nbal(n)
        # with 2D variable t(n,np)). Determine which variable position the
        # equation index matches, so entries with different alignments are
        # grouped separately. Use a large sentinel offset for the non-matching
        # positions to distinguish groups.
        #
        # Issue #1099/#1100: For dimension-mismatch, use domain/alias-based
        # matching instead of element-value string matching. Element matching
        # fails when independent sets share element labels (marco: "hydro"
        # in both m and p) or aliases share all elements (markov: s/sp/spp).
        #
        # All entries for the same eq→var relationship should be grouped
        # together (single offset_key). The downstream _match_subset_domain()
        # and Sum-wrapping logic correctly handles the multiplier indexing.
        if len(eq_indices) < len(var_indices):
            offsets_list: list[int] = [_SENTINEL_UNMATCHED] * len(var_indices)

            # Use domain-level matching to determine which variable positions
            # correspond to equation positions (alias + subset resolution).
            eq_canons = [_resolve_alias_target(d, model_ir) for d in eq_domain]
            var_canons = [_resolve_alias_target(d, model_ir) for d in var_domain]

            def _canon_or_parent(set_name: str) -> str:
                """Get canonical set or its parent if it's a 1-D subset."""
                canon = _resolve_alias_target(set_name, model_ir)
                sdef = model_ir.sets.get(canon)
                if sdef and hasattr(sdef, "domain") and len(sdef.domain) == 1:
                    return _resolve_alias_target(str(sdef.domain[0]), model_ir)
                return canon

            eq_roots = [_canon_or_parent(d) for d in eq_domain]
            var_roots = [_canon_or_parent(d) for d in var_domain]

            used_var: set[int] = set()
            for ei in range(len(eq_domain)):
                # First pass: prefer exact canonical match (same set/alias)
                matched = False
                for vi in range(len(var_domain)):
                    if vi not in used_var and eq_canons[ei] == var_canons[vi]:
                        offsets_list[vi] = 0
                        used_var.add(vi)
                        matched = True
                        break
                if not matched:
                    # Second pass: match via common root (subset relationships)
                    for vi in range(len(var_domain)):
                        if vi not in used_var and eq_roots[ei] == var_roots[vi]:
                            offsets_list[vi] = 0
                            used_var.add(vi)
                            break

            return tuple(offsets_list)
        # More equation dims than variable dims — return zeros
        return (0,) * len(var_indices)

    if _domain_cache is None:
        _domain_cache = {}

    def _resolve_cached(set_name: str) -> tuple[str, dict[str, int]] | None:
        """Resolve a set name to (underlying_set_name, {member: position}) with caching."""
        if set_name in _domain_cache:
            return _domain_cache[set_name]
        try:
            members, resolved_name = resolve_set_members(set_name, model_ir)
            pos_map = {m: i for i, m in enumerate(members)}
            result = (resolved_name, pos_map)
        except (ValueError, KeyError):
            result = None
        _domain_cache[set_name] = result
        return result

    offsets: list[int] = []
    for i, (eq_elem, var_elem) in enumerate(zip(eq_indices, var_indices, strict=True)):
        if eq_elem == var_elem:
            offsets.append(0)
            continue
        # Only compute offset if both domains reference the same underlying set
        eq_set = eq_domain[i] if i < len(eq_domain) else None
        var_set = var_domain[i] if i < len(var_domain) else None
        if eq_set is None or var_set is None:
            offsets.append(0)
            continue
        eq_info = _resolve_cached(eq_set)
        var_info = _resolve_cached(var_set)
        if eq_info is None or var_info is None:
            offsets.append(0)
            continue
        eq_resolved, eq_pos_map = eq_info
        var_resolved, var_pos_map = var_info
        if eq_resolved != var_resolved:
            # Different underlying sets — not a lead/lag pattern
            offsets.append(0)
            continue
        # Same set: compute positional offset via O(1) dict lookup
        eq_pos = eq_pos_map.get(eq_elem)
        var_pos = var_pos_map.get(var_elem)
        if eq_pos is not None and var_pos is not None:
            offsets.append(eq_pos - var_pos)
        else:
            offsets.append(0)

    return tuple(offsets)


def _build_offset_guard(
    mult_domain: tuple[str, ...],
    offset_key: tuple[int, ...],
) -> Expr | None:
    """Build a boundary guard condition for an offset multiplier term.

    Issue #1045: When a stationarity term uses nu_eq(t-1) or nu_eq(t+1),
    the term must be guarded to prevent out-of-bounds index access:
    - For lag (offset < 0): $(ord(t) > abs(offset))
    - For lead (offset > 0): $(ord(t) <= card(t) - offset)

    Args:
        mult_domain: Multiplier domain indices (e.g., ("t",))
        offset_key: Tuple of integer offsets per domain dimension

    Returns:
        Guard expression or None if no guard needed
    """
    from ..ir.ast import Binary, Call, Const, SymbolRef

    conditions: list[Expr] = []
    for i, domain_idx in enumerate(mult_domain):
        offset = offset_key[i] if i < len(offset_key) else 0
        if offset < 0:
            # Lag: ord(t) > abs(offset)
            conditions.append(
                Binary(">", Call("ord", (SymbolRef(domain_idx),)), Const(float(abs(offset))))
            )
        elif offset > 0:
            # Lead: ord(t) <= card(t) - offset
            conditions.append(
                Binary(
                    "<=",
                    Call("ord", (SymbolRef(domain_idx),)),
                    Binary("-", Call("card", (SymbolRef(domain_idx),)), Const(float(offset))),
                )
            )

    if not conditions:
        return None
    guard = conditions[0]
    for cond in conditions[1:]:
        guard = Binary("and", guard, cond)
    return guard


def _build_offset_multiplier(
    mult_base_name: str,
    mult_domain: tuple[str, ...],
    offset_key: tuple[int, ...],
) -> Expr:
    """Build a multiplier reference with lead/lag offset indices.

    Issue #1045: When a Jacobian entry has an index offset between the equation
    and variable instances, the multiplier needs a corresponding offset.
    E.g., if totalcap(t-1) contributes to stat_k(t), the multiplier should be
    nu_totalcap(t-1), not nu_totalcap(t).

    Args:
        mult_base_name: Base multiplier name (e.g., "nu_totalcap")
        mult_domain: Multiplier domain indices (e.g., ("t",))
        offset_key: Tuple of integer offsets per domain dimension

    Returns:
        MultiplierRef with IndexOffset indices where offset != 0
    """
    from ..ir.ast import Const, IndexOffset

    new_indices: list[str | IndexOffset] = []
    for i, domain_idx in enumerate(mult_domain):
        offset = offset_key[i] if i < len(offset_key) else 0
        if offset != 0:
            new_indices.append(IndexOffset(domain_idx, Const(float(offset)), False))
        else:
            new_indices.append(domain_idx)

    return MultiplierRef(mult_base_name, tuple(new_indices))


def _subtract_and_cancel(a: Expr, b: Expr) -> Expr:
    """Compute *a* − *b*, cancelling structurally equal additive terms.

    Decomposes both expressions into sums of signed terms, removes
    matching pairs, and reconstructs the result.  This handles the
    Kronecker-delta pattern where ``a = 1 + X`` and ``b = X``, giving
    ``a − b = 1`` even when the simplifier can't reduce the AST.
    """

    def _collect_terms(e: Expr, sign: int, out: list[tuple[int, Expr]]) -> None:
        """Flatten additive structure into (sign, term) pairs."""
        if isinstance(e, Binary) and e.op == "+":
            _collect_terms(e.left, sign, out)
            _collect_terms(e.right, sign, out)
        elif isinstance(e, Binary) and e.op == "-":
            _collect_terms(e.left, sign, out)
            _collect_terms(e.right, -sign, out)
        elif isinstance(e, Unary) and e.op == "-":
            _collect_terms(e.child, -sign, out)
        else:
            out.append((sign, e))

    terms_a: list[tuple[int, Expr]] = []
    _collect_terms(a, +1, terms_a)
    terms_b: list[tuple[int, Expr]] = []
    _collect_terms(b, -1, terms_b)  # subtract b

    all_terms = terms_a + terms_b

    # Cancel matching (sign, expr) pairs.
    remaining: list[tuple[int, Expr]] = []
    cancelled: list[bool] = [False] * len(all_terms)
    for i in range(len(all_terms)):
        if cancelled[i]:
            continue
        found = False
        for j in range(i + 1, len(all_terms)):
            if cancelled[j]:
                continue
            si, ei = all_terms[i]
            sj, ej = all_terms[j]
            if si == -sj and ei == ej:
                cancelled[i] = True
                cancelled[j] = True
                found = True
                break
        if not found:
            remaining.append(all_terms[i])

    if not remaining:
        return Const(0.0)

    # Reconstruct expression from remaining terms.
    result: Expr | None = None
    for sign, term in remaining:
        signed = term if sign == +1 else Unary("-", term)
        if result is None:
            result = signed
        else:
            result = Binary("+", result, signed)

    return result if result is not None else Const(0.0)


def _substitute_elements(expr: Expr, subs: dict[str, str]) -> Expr:
    """Replace concrete element names in an AST according to *subs*.

    This performs a shallow structural copy, replacing string index
    values inside ``ParamRef``, ``VarRef``, ``SymbolRef`` etc.
    """
    if not subs:
        return expr

    def _sub_idx(idx: str | IndexOffset) -> str | IndexOffset:
        if isinstance(idx, IndexOffset):
            new_base = subs.get(idx.base, idx.base)
            if new_base == idx.base:
                return idx
            return IndexOffset(new_base, idx.offset, idx.circular)
        return subs.get(idx, idx)

    def _walk(e: Expr) -> Expr:
        if isinstance(e, Const):
            return e
        if isinstance(e, SymbolRef):
            # SymbolRef is a scalar — no indices to substitute.
            return e
        if isinstance(e, ParamRef):
            new_indices = tuple(_sub_idx(i) for i in e.indices) if e.indices else e.indices
            if new_indices == e.indices:
                return e
            return ParamRef(e.name, new_indices)
        if isinstance(e, VarRef):
            new_indices = tuple(_sub_idx(i) for i in e.indices) if e.indices else e.indices
            if new_indices == e.indices:
                return e
            return VarRef(e.name, new_indices, e.attribute)
        if isinstance(e, Binary):
            return Binary(e.op, _walk(e.left), _walk(e.right))
        if isinstance(e, Unary):
            return Unary(e.op, _walk(e.child))
        if isinstance(e, Call):
            return Call(e.func, tuple(_walk(a) for a in e.args))
        if isinstance(e, Sum):
            return Sum(
                e.index_sets,
                _walk(e.body),
                _walk(e.condition) if e.condition else None,
            )
        if isinstance(e, DollarConditional):
            return DollarConditional(_walk(e.value_expr), _walk(e.condition))
        if isinstance(e, Prod):
            return Prod(
                e.index_sets,
                _walk(e.body),
                _walk(e.condition) if e.condition else None,
            )
        if isinstance(e, SetMembershipTest):
            return SetMembershipTest(e.set_name, tuple(_walk(a) for a in e.indices))
        if isinstance(e, MultiplierRef):
            new_indices = tuple(_sub_idx(i) for i in e.indices) if e.indices else e.indices
            if new_indices == e.indices:
                return e
            return MultiplierRef(e.name, new_indices)
        if isinstance(e, EquationRef):
            new_indices = tuple(_sub_idx(i) for i in e.indices) if e.indices else e.indices
            if new_indices == e.indices:
                return e
            return EquationRef(e.name, new_indices, e.attribute)
        # Fallback: return unchanged
        return e

    return _walk(expr)


def _derivative_structure_key(expr: Expr) -> str:
    """Compute a structural fingerprint of a derivative AST.

    Issue #1110: Captures the AST *shape* — node types, operators, param/set
    names — but replaces concrete index tuples with arity counts, so that
    entries differing only in element values produce the same key while
    structurally different trees (e.g. ``Binary('+', Const(1), X)`` vs ``X``)
    produce different keys.
    """

    def _walk(e: Expr) -> str:
        if isinstance(e, Const):
            return f"C({e.value})"
        if isinstance(e, SymbolRef):
            return f"S({e.name})"
        if isinstance(e, ParamRef):
            arity = len(e.indices) if e.indices else 0
            return f"P({e.name},{arity})"
        if isinstance(e, VarRef):
            arity = len(e.indices) if e.indices else 0
            return f"V({e.name},{arity})"
        if isinstance(e, MultiplierRef):
            arity = len(e.indices) if e.indices else 0
            return f"M({e.name},{arity})"
        if isinstance(e, Binary):
            return f"B({e.op},{_walk(e.left)},{_walk(e.right)})"
        if isinstance(e, Unary):
            return f"U({e.op},{_walk(e.child)})"
        if isinstance(e, Call):
            args = ",".join(_walk(a) for a in e.args)
            return f"F({e.func},{args})"
        if isinstance(e, Sum):
            body = _walk(e.body)
            n = len(e.index_sets) if e.index_sets else 0
            cond = _walk(e.condition) if e.condition else ""
            return f"Sum({n},{body},{cond})"
        if isinstance(e, DollarConditional):
            return f"DC({_walk(e.value_expr)},{_walk(e.condition)})"
        if isinstance(e, Prod):
            body = _walk(e.body)
            n = len(e.index_sets) if e.index_sets else 0
            cond = _walk(e.condition) if e.condition else ""
            return f"Prod({n},{body},{cond})"
        if isinstance(e, SetMembershipTest):
            n = len(e.indices) if e.indices else 0
            return f"SMT({e.set_name},{n})"
        if isinstance(e, EquationRef):
            arity = len(e.indices) if e.indices else 0
            return f"EQ({e.name},{arity},{e.attribute})"
        return type(e).__name__

    return _walk(expr)


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

    # Cache for resolved set names and member→position maps (shared across constraints)
    domain_cache: dict = {}

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
                # Issue #1045: Sub-group entries by their index offset pattern.
                # For lead/lag equations like totalcap(t).. k(t+1) = k(t)*spda + kn(t+1),
                # variable k has two distinct Jacobian patterns in the same constraint:
                #   1. ∂totalcap(t)/∂k(t) = -spda^nyper  (same-index)
                #   2. ∂totalcap(t-1)/∂k(t) = 1          (offset: eq at t-1, var at t)
                # These need separate stationarity terms with different multiplier indices.
                # Group entries by the relationship between eq_indices and var_indices.
                offset_groups: dict[tuple[int, ...], list[tuple[int, int]]] = {}
                for entry_row_id, entry_col_id in entries:
                    _, entry_eq_indices = jacobian.index_mapping.row_to_eq[entry_row_id]
                    _, entry_var_indices = jacobian.index_mapping.col_to_var[entry_col_id]
                    # Compute positional offset between eq and var indices in their domains
                    offset_key = _compute_index_offset_key(
                        entry_eq_indices,
                        entry_var_indices,
                        mult_domain,
                        var_domain,
                        kkt.model_ir,
                        _domain_cache=domain_cache,
                    )
                    if offset_key not in offset_groups:
                        offset_groups[offset_key] = []
                    offset_groups[offset_key].append((entry_row_id, entry_col_id))

                for offset_key, group_entries in offset_groups.items():
                    # Issue #1086: For dimension-mismatch groups, prefer a
                    # representative entry with distinct variable indices so
                    # the element→domain mapping doesn't have key collisions
                    # (e.g., avoid t(five,five) where both map to the same key).
                    group_row_id, group_col_id = group_entries[0]
                    if any(o == _SENTINEL_UNMATCHED for o in offset_key) and len(group_entries) > 1:
                        for _rid, _cid in group_entries:
                            _, _vidx = jacobian.index_mapping.col_to_var[_cid]
                            if len(set(_vidx)) == len(_vidx):
                                group_row_id, group_col_id = _rid, _cid
                                break
                    derivative = jacobian.get_derivative(group_row_id, group_col_id)
                    _, group_eq_indices = jacobian.index_mapping.row_to_eq[group_row_id]

                    # Issue #1110: Detect multi-pattern Jacobian entries.
                    # When a constraint body references a variable both directly
                    # AND inside a sum, diagonal (eq-idx matches var-idx) and
                    # off-diagonal entries have structurally different derivatives.
                    # Use the majority pattern for the main sum and add a
                    # separate correction term for the minority pattern.
                    _multi_pattern_correction: Expr | None = None
                    if len(group_entries) > 1:
                        rep_key = _derivative_structure_key(derivative)
                        # Sub-group by structure key
                        _sg: dict[str, list[tuple[int, int]]] = {}
                        for _rid, _cid in group_entries:
                            _d = jacobian.get_derivative(_rid, _cid)
                            _k = _derivative_structure_key(_d)
                            _sg.setdefault(_k, []).append((_rid, _cid))
                        if len(_sg) > 1:
                            # Multiple patterns detected.  Use the majority
                            # pattern for the full sum (it will be correct for
                            # most entries) and emit a correction for the minority.
                            sorted_groups = sorted(
                                _sg.items(),
                                key=lambda kv: len(kv[1]),
                                reverse=True,
                            )
                            majority_key, majority_entries = sorted_groups[0]
                            _minority_key, minority_entries = sorted_groups[1]
                            if len(sorted_groups) > 2:
                                import warnings

                                warnings.warn(
                                    f"Multi-pattern Jacobian: {len(sorted_groups)} derivative "
                                    f"patterns detected for {eq_name_base}/{var_name}; "
                                    f"only majority + first minority handled. "
                                    f"Remaining patterns ignored.",
                                    stacklevel=2,
                                )
                            # Use majority representative for the main term
                            if majority_key != rep_key:
                                # Current representative is from the minority;
                                # switch to a majority entry.
                                _mr, _mc = majority_entries[0]
                                # Prefer entry with distinct var indices (same
                                # logic as Issue #1086 above).
                                if any(o == _SENTINEL_UNMATCHED for o in offset_key):
                                    for __r, __c in majority_entries:
                                        __vidx = jacobian.index_mapping.col_to_var[__c][1]
                                        if len(set(__vidx)) == len(__vidx):
                                            _mr, _mc = __r, __c
                                            break
                                group_row_id, group_col_id = _mr, _mc
                                derivative = jacobian.get_derivative(group_row_id, group_col_id)
                                _, group_eq_indices = jacobian.index_mapping.row_to_eq[group_row_id]
                            # Build correction for the minority entries.
                            # The minority entries (diagonal) have a derivative
                            # that differs from the majority (off-diagonal).
                            # Find a paired diagonal+off-diagonal entry for the
                            # SAME variable instance.  This avoids element-collision
                            # problems with element-to-set mapping: both entries
                            # share the same var_indices, so only the eq_indices
                            # differ.
                            paired_min: tuple[int, int] | None = None
                            paired_maj: tuple[int, int] | None = None
                            for _mrid, _mcid in minority_entries:
                                for _arid, _acid in majority_entries:
                                    if _mcid == _acid:
                                        paired_min = (_mrid, _mcid)
                                        paired_maj = (_arid, _acid)
                                        break
                                if paired_min is not None:
                                    break
                            if paired_min is not None and paired_maj is not None:
                                min_d = jacobian.get_derivative(*paired_min)
                                maj_d = jacobian.get_derivative(*paired_maj)
                                # Compute correction = min_d - maj_d evaluated
                                # at the diagonal point.  We substitute the
                                # majority eq indices with the minority eq indices
                                # in maj_d so both derivatives are at the same
                                # concrete point, then subtract.
                                _, _pmin_eq_idx = jacobian.index_mapping.row_to_eq[paired_min[0]]
                                _, _pmaj_eq_idx = jacobian.index_mapping.row_to_eq[paired_maj[0]]
                                # Build maj→min element substitution for differing
                                # eq positions only.
                                _elem_sub: dict[str, str] = {}
                                for ei in range(min(len(_pmin_eq_idx), len(_pmaj_eq_idx))):
                                    if _pmaj_eq_idx[ei] != _pmin_eq_idx[ei]:
                                        _elem_sub[_pmaj_eq_idx[ei]] = _pmin_eq_idx[ei]
                                # Guard: if any substitution key also appears in the
                                # paired var indices, the substitution would cause
                                # accidental rewrites.  Skip correction in that case.
                                _, _paired_var_idx = jacobian.index_mapping.col_to_var[
                                    paired_maj[1]
                                ]
                                _var_labels = {str(v) for v in _paired_var_idx}
                                if _elem_sub and _elem_sub.keys() & _var_labels:
                                    _elem_sub = {}  # unsafe — fall through to no correction
                                # Substitute in maj_d AST to align with min_d.
                                maj_d_aligned = _substitute_elements(maj_d, _elem_sub)
                                # Now subtract: both at the same concrete point.
                                # Collect additive terms and cancel matching pairs.
                                raw_correction = _subtract_and_cancel(
                                    min_d,
                                    maj_d_aligned,
                                )
                                if not (
                                    isinstance(raw_correction, Const)
                                    and raw_correction.value == 0.0
                                ):
                                    # Now replace concrete elements → domain names
                                    # for the final correction expression.
                                    # Use standard index replacement on raw_correction.
                                    indexed_correction = _replace_indices_in_expr(
                                        raw_correction,
                                        var_domain,
                                        element_to_set,
                                        kkt.model_ir,
                                        equation_domain=var_domain,
                                    )
                                    # Correction multiplier uses variable-domain indices
                                    # at matched positions (where diagonal eq≡var).
                                    # We use var_domain (not mult_domain) because the
                                    # correction applies at the specific point where
                                    # eq and var indices coincide (the diagonal),
                                    # indexed by the variable's own domain names.
                                    # For offset groups with lead/lag, the offset is
                                    # already zero at matched positions (offset_key[vi]==0),
                                    # so no offset adjustment is needed.
                                    corr_mult_domain = tuple(
                                        var_domain[vi]
                                        for vi, o in enumerate(offset_key)
                                        if vi < len(var_domain) and o != _SENTINEL_UNMATCHED
                                    )
                                    if not corr_mult_domain:
                                        corr_mult_domain = mult_domain
                                    corr_mult = MultiplierRef(
                                        name_func(eq_name_base),
                                        corr_mult_domain,
                                    )
                                    _multi_pattern_correction = Binary(
                                        "*",
                                        indexed_correction,
                                        corr_mult,
                                    )

                    # Issue #649: Build constraint-specific element-to-set mapping.
                    # When a constraint has multiple indices from the same underlying set
                    # (e.g., maxdist(i,j) where both i,j iterate over the same set), we need
                    # to map element labels to their specific position in the constraint domain.
                    # For example, for maxdist(1,2) with domain (i,j):
                    #   "1" -> "i" (position 0)
                    #   "2" -> "j" (position 1)
                    # This ensures x(1) - x(2) becomes x(i) - x(j), not x(i) - x(i).
                    is_dim_mismatch = any(o == _SENTINEL_UNMATCHED for o in offset_key)
                    if is_dim_mismatch:
                        # Issue #1086: For dimension-mismatch (e.g., 1D eq nbal(n) →
                        # 2D var t(n,np)), build element mapping from the representative
                        # entry's VARIABLE indices, so concrete elements map to the
                        # correct variable domain names — not the equation domain names.
                        # Also remap the sum iteration alias (e.g., "np") to the variable
                        # domain name at the unmatched position.
                        _, rep_var_indices = jacobian.index_mapping.col_to_var[group_col_id]
                        overrides: dict[str, str] = {}
                        alias_remap: dict[str, str] = {}
                        for vi, vdom in enumerate(var_domain):
                            if vi < len(rep_var_indices):
                                overrides[rep_var_indices[vi]] = vdom
                            # For unmatched positions (sentinel), the variable
                            # index came from a sum iteration variable (alias). Find
                            # that alias and remap it to the variable domain name.
                            if (
                                vi < len(offset_key)
                                and offset_key[vi] == _SENTINEL_UNMATCHED
                                and vi < len(rep_var_indices)
                            ):
                                # The concrete element at this position came from
                                # an alias/set iteration var. Find which alias it
                                # belongs to and remap that alias name.
                                elem = rep_var_indices[vi]
                                for aname, adef in kkt.model_ir.aliases.items():
                                    target = adef.target if hasattr(adef, "target") else adef
                                    if isinstance(target, str):
                                        tgt_set = kkt.model_ir.sets.get(target)
                                        if tgt_set and hasattr(tgt_set, "members"):
                                            if elem.lower() in [m.lower() for m in tgt_set.members]:
                                                alias_remap[aname] = vdom
                        constraint_element_to_set = ChainMap(overrides, alias_remap, element_to_set)
                    else:
                        constraint_element_to_set = _build_constraint_element_mapping(
                            element_to_set, group_eq_indices, mult_domain
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

                    # Issue #1045: For lead/lag patterns, the multiplier index needs
                    # an offset. E.g., if the Jacobian entry comes from totalcap(t-1)
                    # affecting k(t), the multiplier should be nu_totalcap(t-1), not
                    # nu_totalcap(t). We encode this via the positional `offset_key`
                    # and build an IndexOffset-based multiplier in `_build_offset_multiplier()`.
                    has_offset = any(o != 0 for o in offset_key)
                    mult_ref: Expr
                    if is_dim_mismatch:
                        # Issue #1099/#1100: Use the equation's own domain for
                        # the multiplier. The downstream _match_subset_domain()
                        # and Sum-wrapping logic handles renaming subset indices
                        # to superset and wrapping disjoint indices in sums.
                        mult_ref = MultiplierRef(mult_base_name, mult_domain)
                    elif has_offset:
                        # Build multiplier with shifted indices
                        mult_ref = _build_offset_multiplier(
                            mult_base_name,
                            mult_domain,
                            offset_key,
                        )
                    else:
                        mult_ref = MultiplierRef(mult_base_name, mult_domain)
                    term: Expr = Binary("*", indexed_deriv, mult_ref)

                    # Issue #1045: Guard offset terms with boundary conditions.
                    # nu_totalcap(t-1) is invalid when t is the first element,
                    # nu_totalcap(t+1) is invalid when t is the last element.
                    # Wrap the term in a DollarConditional to prevent out-of-bounds.
                    if has_offset and not is_dim_mismatch:
                        offset_guard = _build_offset_guard(mult_domain, offset_key)
                        if offset_guard is not None:
                            term = DollarConditional(value_expr=term, condition=offset_guard)

                    # Issue #877: Propagate the equation's dollar condition into
                    # the Jacobian term BEFORE Sum wrapping, so that derivative
                    # expressions with undefined values (e.g. division by zero)
                    # are guarded for instances where the condition is false.
                    eq_def = kkt.model_ir.equations.get(eq_name_base)
                    if eq_def is not None and eq_def.condition is not None:
                        indexed_condition = _replace_indices_in_expr(
                            eq_def.condition,
                            var_domain,
                            constraint_element_to_set,
                            kkt.model_ir,
                            equation_domain=var_domain,
                        )
                        term = DollarConditional(value_expr=term, condition=indexed_condition)

                    # Determine if we need a sum or a direct term:
                    # - If domains match exactly: direct term deriv(i) * mult(i)
                    # - If mult_domain is subset of var_domain: direct term deriv(i,j) * mult(i)
                    #   (the multiplier indices are shared with the variable - no summation needed)
                    # - If mult_domain is disjoint from var_domain: sum over mult_domain
                    #   (e.g., sum(k, deriv * mult(k)) where k is independent of variable indices)
                    # - If mult_domain partially overlaps var_domain but is not a subset: error
                    mult_domain_set = set(mult_domain)
                    var_domain_set = set(var_domain)

                    # Issue #1041: Before branching on name-based overlap,
                    # attempt subset/alias matching.  This handles fully
                    # disjoint cases like ('ii','jj') vs ('i','j') AND mixed
                    # cases like ('ii','j') vs ('i','j') where some indices
                    # overlap by name but others are subset/alias-related.
                    subset_rename = _match_subset_domain(mult_domain, var_domain, kkt.model_ir)

                    # Issue #1104: For dimension-mismatch with alias-only
                    # renames, the standard _rewrite_subset_to_superset is
                    # WRONG: it collapses constraint-domain indices (sp,j)
                    # onto variable-domain names (s,i), destroying the
                    # independent summation structure.  Instead, create fresh
                    # aliases for colliding mult indices and wrap in a Sum.
                    _did_dim_mismatch_alias_fix = False
                    if is_dim_mismatch and subset_rename:
                        # Check if ALL renames are pure alias renames
                        all_alias = True
                        for src_name, tgt_name in subset_rename.items():
                            src_canon = _resolve_alias_target(src_name, kkt.model_ir)
                            tgt_canon = _resolve_alias_target(tgt_name, kkt.model_ir)
                            if src_canon != tgt_canon:
                                all_alias = False
                                break

                        # Issue #1104: Check if applying the rename would
                        # corrupt the derivative.  This happens when a renamed
                        # mult index appears as a FREE index in the derivative
                        # with a different meaning (declared-domain position).
                        # E.g., constr(sp,j) → z(s,i,sp): derivative has
                        # pi(s,i,sp,j,spp) where sp/j are constraint-domain
                        # names from pi's declared domain.  Renaming sp→s
                        # and j→i would produce pi(s,i,s,i,spp) — wrong.
                        rename_corrupts_deriv = False
                        if all_alias and subset_rename:
                            free_in_deriv = _collect_free_indices(indexed_deriv, kkt.model_ir)
                            for src_name in subset_rename:
                                if src_name.lower() in free_in_deriv:
                                    rename_corrupts_deriv = True
                                    break

                        if all_alias and rename_corrupts_deriv:
                            _did_dim_mismatch_alias_fix = True
                            # Build a set of all names in scope (lowercased)
                            used_names = (
                                {d.lower() for d in var_domain}
                                | {d.lower() for d in mult_domain}
                                | {a.lower() for a in kkt.model_ir.aliases}
                                | {s.lower() for s in kkt.model_ir.sets}
                            )

                            # Identify which mult_domain indices are RENAMED
                            # by subset_rename (i.e., are independent iteration
                            # variables that should be summed over) vs SHARED
                            # with var_domain (should remain as-is).
                            renamed_mult = {k.lower() for k in subset_rename}

                            # For renamed mult indices: if the mult index name
                            # already collides with a var_domain name, we need
                            # a fresh alias to avoid GAMS variable shadowing.
                            # If it doesn't collide, keep it as a sum variable.
                            var_domain_lower = {v.lower() for v in var_domain}
                            fresh_rename: dict[str, str] = {}
                            sum_indices_list: list[str] = []
                            for md_idx in mult_domain:
                                if md_idx.lower() in renamed_mult:
                                    # This is an independent constraint iteration
                                    # variable. Check for name collision.
                                    if md_idx.lower() in var_domain_lower:
                                        root = _resolve_alias_target(md_idx, kkt.model_ir)
                                        fresh = _get_or_create_fresh_alias(
                                            root, used_names, kkt.model_ir
                                        )
                                        fresh_rename[md_idx.lower()] = fresh
                                        sum_indices_list.append(fresh)
                                        used_names.add(fresh.lower())
                                    else:
                                        # No collision — use as-is
                                        sum_indices_list.append(md_idx)
                                # else: shared index, no sum needed

                            # Also fix alias-domain names from pi's declared
                            # domain that should map to the var_domain index at
                            # unmatched positions.  E.g., pi has declared
                            # domain (..., spp) but position 4 should map to
                            # var_domain[2] = sp.  The alias_remap maps
                            # spp → sp but prefer_declared_domain=True in
                            # _replace_indices_in_expr ignores the ChainMap.
                            # Post-fix: rename those aliases → var_domain name.
                            alias_fix: dict[str, str] = {}
                            for vi, vdom in enumerate(var_domain):
                                if vi < len(offset_key) and offset_key[vi] == _SENTINEL_UNMATCHED:
                                    root = _resolve_alias_target(vdom, kkt.model_ir)
                                    for aname in list(kkt.model_ir.aliases):
                                        aroot = _resolve_alias_target(aname, kkt.model_ir)
                                        if (
                                            aroot == root
                                            and aname.lower() != vdom.lower()
                                            and aname.lower() not in var_domain_lower
                                            and aname.lower() not in fresh_rename
                                            and aname.lower() not in set(fresh_rename.values())
                                            and aname.lower()
                                            not in {s.lower() for s in sum_indices_list}
                                        ):
                                            alias_fix[aname.lower()] = vdom

                            # Combine fresh_rename + alias_fix and rewrite
                            combined_rename = {**fresh_rename, **alias_fix}
                            if combined_rename:
                                term = _rewrite_subset_to_superset(term, combined_rename)

                            # Wrap in Sum over the independent mult indices
                            if sum_indices_list:
                                term = Sum(tuple(sum_indices_list), term)

                    if not _did_dim_mismatch_alias_fix and subset_rename is not None:
                        if subset_rename:
                            # Rewrite the term's indices from subset to superset.
                            # No subset guard needed: the constraint's own dollar
                            # condition already restricts the term to valid instances.
                            term = _rewrite_subset_to_superset(term, subset_rename)

                            # Issue #1053: Widen the multiplier's declared domain
                            # to match the rewritten indices.  When the equation
                            # domain is a strict subset (e.g., j ⊂ i), the
                            # multiplier is declared over (j) but stationarity
                            # references it with parent-set index (i).  GAMS
                            # enforces domain checking, so nu_e2(i) is invalid
                            # when nu_e2 is declared over j.  Widening the
                            # declaration to (i) makes the reference valid;
                            # inactive instances are fixed to 0 by the emitter.
                            if mult_base_name in multipliers:
                                old_dom = multipliers[mult_base_name].domain
                                # Apply the subset→superset rename to the multiplier's
                                # declared domain.  Note: subset_rename keys are
                                # lowercased index names.
                                rename_pairs: list[tuple[str, str]] = []
                                new_dom_list: list[str] = []
                                for d in old_dom:
                                    if isinstance(d, str):
                                        renamed = subset_rename.get(d.lower(), d)
                                        if renamed.lower() != d.lower():
                                            rename_pairs.append((d.lower(), renamed.lower()))
                                        new_dom_list.append(renamed)
                                    else:
                                        new_dom_list.append(d)
                                new_dom = tuple(new_dom_list)
                                if new_dom != old_dom:
                                    multipliers[mult_base_name].domain = new_dom

                                    # Only record widenings for true subset→parent
                                    # relationships, not pure alias renames.  An
                                    # alias-only rename (e.g., ii→i where ii is an
                                    # alias of i) does not need a .fx guard because
                                    # the domains are equivalent.
                                    is_true_subset = False
                                    model_sets = kkt.model_ir.sets
                                    for orig_idx, parent_idx in rename_pairs:
                                        orig_set = model_sets.get(orig_idx)
                                        if orig_set is not None and hasattr(orig_set, "domain"):
                                            orig_domain = orig_set.domain
                                            # Compare case-insensitively: parser may
                                            # preserve original casing.
                                            if (
                                                isinstance(orig_domain, tuple)
                                                and len(orig_domain) == 1
                                                and isinstance(orig_domain[0], str)
                                                and orig_domain[0].lower() == parent_idx.lower()
                                            ):
                                                is_true_subset = True
                                                break
                                    if is_true_subset:
                                        kkt.multiplier_domain_widenings[mult_base_name] = (
                                            old_dom,
                                            new_dom,
                                        )
                        # else: empty rename_map means identity match, no rewrite needed
                    elif not _did_dim_mismatch_alias_fix:
                        if mult_domain == var_domain:
                            # Exact match: direct term, no sum needed
                            pass
                        elif mult_domain_set.issubset(var_domain_set):
                            # Subset: constraint domain is contained in variable domain
                            # e.g., supply(i) contributes to stat_x(i,j) with direct term lam_supply(i)
                            # No sum needed - the i index is shared
                            pass
                        elif not mult_domain_set.intersection(var_domain_set):
                            # Truly disjoint: constraint has indices independent
                            # of variable. Need to sum over the constraint's domain.
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
                            sum_indices = tuple(
                                idx for idx in mult_domain if idx in extra_mult_indices
                            )
                            if sum_indices:
                                term = Sum(sum_indices, term)

                    # Issue #670: After domain-based sum wrapping, detect any remaining
                    # free indices in the derivative expression that are not controlled by
                    # either the stationarity equation domain or the multiplier domain.
                    # These arise when the derivative contains indices from the original
                    # constraint's inner sum that are outside both domains (cross-indexed
                    # sum pattern). Wrap them in an additional Sum to avoid GAMS Error 149.
                    # Skip when _did_dim_mismatch_alias_fix already handled Sum wrapping
                    # and renamed the derivative indices.
                    if not _did_dim_mismatch_alias_fix:
                        controlled = var_domain_set | mult_domain_set
                        free_in_deriv = _collect_free_indices(indexed_deriv, kkt.model_ir)
                        uncontrolled = free_in_deriv - controlled
                        if uncontrolled:
                            sum_indices = tuple(sorted(uncontrolled))
                            term = Sum(sum_indices, term)

                    expr = Binary("+", expr, term)

                    # Issue #1110: Add the diagonal correction term if
                    # multi-pattern was detected earlier.
                    if _multi_pattern_correction is not None:
                        expr = Binary("+", expr, _multi_pattern_correction)
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
                # Issue #670: scalar constraints have no multiplier domain, so any
                # index in the derivative that is not in var_domain is uncontrolled.
                # Wrap such indices in a Sum to avoid GAMS Error 149.
                free_in_deriv = _collect_free_indices(indexed_deriv, kkt.model_ir)
                # Use lowercase comparison to match _collect_free_indices output,
                # consistent with the indexed-constraint branch above.
                uncontrolled = free_in_deriv - {d.lower() for d in var_domain}
                if uncontrolled:
                    sum_indices = tuple(sorted(uncontrolled))
                    term = Sum(sum_indices, term)

                # Issue #767 / #764: Guard multiplier terms with $(sameas(...))
                # when only a subset of the indexed variable's instances have a
                # nonzero Jacobian entry.  Handles both single-entry (.fx) and
                # multi-entry (scalar equation summing over a subset) cases.
                if var_domain and len(entries) < len(instances):
                    guard = _build_sameas_guard(var_domain, instances, entries, kkt)
                    if guard is not None:
                        term = DollarConditional(value_expr=term, condition=guard)

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
        piL_name = mult_def.name
        expr = Binary("-", expr, MultiplierRef(piL_name, mult_def.domain))
    elif (var_name, ()) in kkt.multipliers_bounds_lo:
        # Issue #828: Fallback for mixed bounds — variable has uniform lower bound
        # (stored at key (var_name, ())) but non-uniform upper bound triggered
        # per-instance stationarity. Use concrete instance indices for the
        # indexed multiplier reference (e.g., piL_x("bin-1") not piL_x(s)).
        mult_def = kkt.multipliers_bounds_lo[(var_name, ())]
        expr = Binary("-", expr, MultiplierRef(mult_def.name, var_indices))

    # Add π^U (upper bound multiplier, if exists)
    if key in kkt.multipliers_bounds_up:
        mult_def = kkt.multipliers_bounds_up[key]
        piU_name = mult_def.name
        expr = Binary("+", expr, MultiplierRef(piU_name, mult_def.domain))
    elif (var_name, ()) in kkt.multipliers_bounds_up:
        # Issue #828: Fallback for mixed bounds — same logic as lower bound above.
        mult_def = kkt.multipliers_bounds_up[(var_name, ())]
        expr = Binary("+", expr, MultiplierRef(mult_def.name, var_indices))

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

                # Issue #949: The term (derivative and any carried $-condition)
                # may contain free indices beyond mult_domain (e.g. 'h' in
                # pf(h,j) when mult_domain is ('j',)).  Collect from the full
                # term so condition indices are also checked.
                mult_domain_set = {d.lower() for d in mult_domain}
                free_in_term = _collect_free_indices(term, kkt.model_ir)
                extra_uncontrolled = free_in_term - mult_domain_set
                if extra_uncontrolled:
                    extra_indices = tuple(sorted(extra_uncontrolled))
                    term = Sum(extra_indices, term)
            else:
                # Fallback: no domain info, use per-instance (shouldn't happen)
                mult_ref = MultiplierRef(mult_name, eq_indices)
                term = Binary("*", derivative, mult_ref)
        else:
            # Scalar constraint: direct term, no sum needed
            mult_ref = MultiplierRef(mult_name, ())
            term = Binary("*", derivative, mult_ref)

        # Always add J^T * multiplier terms.  The Jacobian is of the original
        # constraint g(x) and the KKT stationarity is ∇f + λᵀ∇g = 0 regardless
        # of whether the complementarity pair negated g for MCP form.
        expr = Binary("+", expr, term)

    return expr
