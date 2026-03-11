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
from src.ir.symbols import EquationDef, Rel
from src.kkt.kkt_system import KKTSystem
from src.kkt.naming import (
    create_eq_multiplier_name,
    create_ineq_multiplier_name,
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


def _extract_all_conditioned_guard(
    stat_expr: Expr, var_domain: tuple[str, ...], model_ir: ModelIR
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
    """
    # Collect (condition, sum_indices) pairs from all leaf terms
    cond_entries: list[tuple[Expr, tuple[str, ...]]] = []

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
                    stat_expr, var_def.domain, kkt.model_ir
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
                        eq_domain_lower = (
                            {s.lower() for s in equation_domain} if equation_domain else set()
                        )
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


def _rewrite_subset_to_superset(expr: Expr, rename_map: dict[str, str]) -> Expr:
    """Rewrite index names in an expression tree according to rename_map.

    Issue #1010: When a gradient expression uses subset index 't' but the
    stationarity equation is indexed over superset 'tt', rewrite 't' → 'tt'
    so the index is controlled by the equation domain. This preserves
    per-element semantics (c(p,tt) varies with tt) rather than collapsing
    via Sum (sum(t, c(p,t)) is constant across tt).

    String indices in VarRef, ParamRef, MultiplierRef, EquationRef, and
    IndexOffset.base are rewritten. The rename_map keys and values should
    both be lowercase-normalized.
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

    Returns:
        Tuple of integer offsets, one per index dimension. (0,0,...) means same-index.
        Falls back to (0,...) if positions can't be determined.
    """
    from ..ad.index_mapping import resolve_set_members

    if len(eq_indices) != len(var_indices):
        # Different dimensionality — return zeros
        return (0,) * max(len(eq_indices), len(var_indices))

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
        # Resolve both domains to their underlying set names
        try:
            _, eq_resolved = resolve_set_members(eq_set, model_ir)
            _, var_resolved = resolve_set_members(var_set, model_ir)
        except (ValueError, KeyError):
            offsets.append(0)
            continue
        if eq_resolved != var_resolved:
            # Different underlying sets — not a lead/lag pattern
            offsets.append(0)
            continue
        # Same set: compute positional offset
        try:
            members, _ = resolve_set_members(eq_resolved, model_ir)
        except (ValueError, KeyError):
            offsets.append(0)
            continue
        if eq_elem in members and var_elem in members:
            offsets.append(members.index(eq_elem) - members.index(var_elem))
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
    model_ir: ModelIR,
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
        model_ir: Model IR for IndexOffset construction

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
                        entry_eq_indices, entry_var_indices, mult_domain, var_domain, kkt.model_ir
                    )
                    if offset_key not in offset_groups:
                        offset_groups[offset_key] = []
                    offset_groups[offset_key].append((entry_row_id, entry_col_id))

                for offset_key, group_entries in offset_groups.items():
                    group_row_id, group_col_id = group_entries[0]
                    derivative = jacobian.get_derivative(group_row_id, group_col_id)
                    _, group_eq_indices = jacobian.index_mapping.row_to_eq[group_row_id]

                    # Issue #649: Build constraint-specific element-to-set mapping.
                    # When a constraint has multiple indices from the same underlying set
                    # (e.g., maxdist(i,j) where both i,j iterate over the same set), we need
                    # to map element labels to their specific position in the constraint domain.
                    # For example, for maxdist(1,2) with domain (i,j):
                    #   "1" -> "i" (position 0)
                    #   "2" -> "j" (position 1)
                    # This ensures x(1) - x(2) becomes x(i) - x(j), not x(i) - x(i).
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
                    # nu_totalcap(t). We achieve this by using the eq_indices→symbolic
                    # mapping (which naturally produces the shifted index).
                    has_offset = any(o != 0 for o in offset_key)
                    if has_offset:
                        # Build multiplier with shifted indices
                        mult_ref = _build_offset_multiplier(
                            mult_base_name,
                            mult_domain,
                            offset_key,
                            kkt.model_ir,
                        )
                    else:
                        mult_ref = MultiplierRef(mult_base_name, mult_domain)
                    term: Expr = Binary("*", indexed_deriv, mult_ref)

                    # Issue #1045: Guard offset terms with boundary conditions.
                    # nu_totalcap(t-1) is invalid when t is the first element,
                    # nu_totalcap(t+1) is invalid when t is the last element.
                    # Wrap the term in a DollarConditional to prevent out-of-bounds.
                    if has_offset:
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

                # Issue #767: Guard per-instance fx multipliers with $(sameas(...))
                # when only a subset of the indexed variable's instances have a
                # nonzero Jacobian entry.  For example, if b_fx_s1 is a scalar
                # equality that fixes b("s1"), only the column corresponding to
                # b("s1") is nonzero.  Without a guard, nu_b_fx_s1 appears in
                # every row of stat_b(j), making the KKT condition incorrect for
                # j ≠ 's1'.  Build one $(sameas(j,'s1')) factor per domain index.
                if var_domain and len(entries) < len(instances):
                    # Look up the variable indices for the first (and typically only)
                    # nonzero entry to find which instance this scalar constraint fixes.
                    entry_col_id = entries[0][1]
                    assert kkt.gradient.index_mapping is not None  # checked at function entry
                    _var_name_check, fixed_indices = kkt.gradient.index_mapping.col_to_var[
                        entry_col_id
                    ]
                    if fixed_indices and len(fixed_indices) == len(var_domain):
                        # Build sameas condition: sameas(d0,'v0') and sameas(d1,'v1') ...
                        guard: Expr | None = None
                        for dom_idx, fixed_val in zip(var_domain, fixed_indices, strict=True):
                            sameas_call: Expr = Call(
                                "sameas",
                                (SymbolRef(dom_idx), SymbolRef(f"'{fixed_val}'")),
                            )
                            guard = (
                                sameas_call if guard is None else Binary("and", guard, sameas_call)
                            )
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
