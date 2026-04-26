"""Equation definition emission for GAMS.

This module emits GAMS equation definitions from KKT system equations.
Each equation is emitted in the form: eq_name(indices).. lhs =E= rhs;

Handles index aliasing to avoid GAMS Error 125 ("Set is under control already")
when an equation's domain index is reused in a nested sum expression.

Also handles automatic domain restriction inference for lead/lag expressions:
- Lead expressions (k + n) with maximum positive offset n require: $(ord(k) <= card(k) - n)
- Lag expressions (t - n) with maximum negative offset magnitude n require: $(ord(t) > n)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.ir.model_ir import ModelIR

from src.emit.expr_to_gams import (
    expr_to_gams,
    resolve_index_conflicts,
)
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
    Sum,
    Unary,
    VarRef,
)
from src.ir.normalize import NormalizedEquation
from src.ir.symbols import EquationDef, Rel
from src.kkt.kkt_system import KKTSystem


def _check_index_offset(
    idx_offset: IndexOffset,
    domain_map: dict[str, str],
    lead_offsets: dict[str, int],
    lag_offsets: dict[str, int],
    bound_indices: set[str],
) -> None:
    """Check an IndexOffset and track maximum offset magnitude.

    Args:
        idx_offset: The IndexOffset to check
        domain_map: Map from lowercase domain index to canonical (original) name
        lead_offsets: Dict mapping canonical index to max positive offset magnitude
        lag_offsets: Dict mapping canonical index to max negative offset magnitude (as positive int)
        bound_indices: Set of lowercase indices currently bound by aggregation expressions
            (e.g., Sum or Prod) to skip
    """
    # Only consider non-circular offsets (linear lead/lag)
    if not idx_offset.circular:
        # Check if this base is in the equation domain (case-insensitive)
        # but not shadowed by an aggregation-local binding
        base_lower = idx_offset.base.lower()
        if base_lower in domain_map and base_lower not in bound_indices:
            # Use canonical domain name for the key
            canonical_name = domain_map[base_lower]
            # Determine offset direction and magnitude
            if isinstance(idx_offset.offset, Const):
                raw_val = idx_offset.offset.value
                if isinstance(raw_val, int):
                    offset_val = raw_val
                elif isinstance(raw_val, float):
                    if not raw_val.is_integer():
                        raise ValueError(
                            f"Non-integer index offset {raw_val!r} for base '{idx_offset.base}' "
                            "is not supported; offsets must be integer-valued."
                        )
                    offset_val = int(raw_val)
                else:
                    raise TypeError(
                        f"Unsupported constant type {type(raw_val)!r} for index offset on "
                        f"base '{idx_offset.base}'. Expected int or float."
                    )
                if offset_val > 0:
                    # Lead: track maximum positive offset
                    current = lead_offsets.get(canonical_name, 0)
                    lead_offsets[canonical_name] = max(current, offset_val)
                elif offset_val < 0:
                    # Lag: track maximum negative offset magnitude
                    current = lag_offsets.get(canonical_name, 0)
                    lag_offsets[canonical_name] = max(current, abs(offset_val))


def _collect_lead_lag_restrictions(
    expr: Expr, domain: tuple[str, ...]
) -> tuple[dict[str, int], dict[str, int]]:
    """Collect domain indices that need lead or lag restrictions with magnitudes.

    Recursively walks an expression to find IndexOffset nodes and determines
    which domain indices need restrictions based on their offset direction
    and magnitude. Indices bound by Sum or Prod expressions are tracked and
    excluded to avoid incorrectly restricting equation-level indices when a
    sum/prod-local index shadows the equation domain.

    For linear (non-circular) offsets:
    - Positive offset (lead, e.g., k+2): needs ord(k) <= card(k) - 2
    - Negative offset (lag, e.g., t-2): needs ord(t) > 2

    Circular offsets (++/--) don't need restrictions as they wrap around.

    Args:
        expr: Expression to analyze
        domain: Tuple of domain indices for the equation

    Returns:
        Tuple of (lead_offsets, lag_offsets) dicts mapping canonical index to max offset
    """
    lead_offsets: dict[str, int] = {}
    lag_offsets: dict[str, int] = {}
    # Map lowercase domain index to canonical (original) name
    domain_map = {d.lower(): d for d in domain}

    def walk(e: Expr, bound_indices: set[str]) -> None:
        # Check for IndexOffset directly in expression
        if isinstance(e, IndexOffset):
            _check_index_offset(e, domain_map, lead_offsets, lag_offsets, bound_indices)

        # Check for IndexOffset in VarRef/ParamRef/EquationRef indices
        # Issue #1045: Skip MultiplierRef — its lead/lag offsets are guarded by
        # DollarConditional at the term level, not by equation-level domain conditions.
        if isinstance(e, (VarRef, ParamRef, EquationRef)):
            for idx in e.indices:
                if isinstance(idx, IndexOffset):
                    _check_index_offset(idx, domain_map, lead_offsets, lag_offsets, bound_indices)

        # Handle Sum and Prod expressions: track bound indices to avoid false positives
        # when sum/prod-local indices shadow equation domain indices
        if isinstance(e, (Sum, Prod)):
            # Add sum/prod indices to bound set for walking the body
            new_bound = bound_indices | {idx.lower() for idx in e.index_sets}
            for child in e.children():
                walk(child, new_bound)
        else:
            # Recursively walk children with current bound set
            for child in e.children():
                walk(child, bound_indices)

    walk(expr, set())
    return lead_offsets, lag_offsets


def _build_domain_condition(
    lead_offsets: dict[str, int], lag_offsets: dict[str, int]
) -> str | None:
    """Build a GAMS domain condition string from lead/lag offset dicts.

    Args:
        lead_offsets: Dict mapping index to max positive offset (e.g., {'k': 2})
        lag_offsets: Dict mapping index to max negative offset magnitude (e.g., {'t': 2})

    Returns:
        GAMS condition string or None if no restrictions needed

    Examples:
        >>> _build_domain_condition({'k': 1}, {})
        'ord(k) <= card(k) - 1'
        >>> _build_domain_condition({'k': 2}, {})
        'ord(k) <= card(k) - 2'
        >>> _build_domain_condition({}, {'t': 1})
        'ord(t) > 1'
        >>> _build_domain_condition({}, {'t': 2})
        'ord(t) > 2'
        >>> _build_domain_condition({'k': 1}, {'t': 1})
        '(ord(k) <= card(k) - 1) and (ord(t) > 1)'
    """
    conditions = []

    for idx in sorted(lead_offsets.keys()):
        offset = lead_offsets[idx]
        conditions.append(f"ord({idx}) <= card({idx}) - {offset}")

    for idx in sorted(lag_offsets.keys()):
        offset = lag_offsets[idx]
        conditions.append(f"ord({idx}) > {offset}")

    if not conditions:
        return None
    elif len(conditions) == 1:
        return conditions[0]
    else:
        return " and ".join(f"({c})" for c in conditions)


def infer_lead_lag_condition(eq_def: EquationDef) -> str | None:
    """Infer a GAMS domain condition from lead/lag offsets in an equation's body.

    Collects lead/lag offsets from both LHS and RHS, keeps the maximum offset
    per index, and builds the combined condition string.

    Returns None if the equation has no domain or no lead/lag offsets.
    """
    if not eq_def.domain:
        return None
    lhs, rhs = eq_def.lhs_rhs
    lead_l, lag_l = _collect_lead_lag_restrictions(lhs, eq_def.domain)
    lead_r, lag_r = _collect_lead_lag_restrictions(rhs, eq_def.domain)
    lead_offsets = {k: max(lead_l.get(k, 0), lead_r.get(k, 0)) for k in set(lead_l) | set(lead_r)}
    lag_offsets = {k: max(lag_l.get(k, 0), lag_r.get(k, 0)) for k in set(lag_l) | set(lag_r)}
    return _build_domain_condition(lead_offsets, lag_offsets)


def _merge_alias_dicts(target: dict[str, list[str]], source: dict[str, list[str]]) -> None:
    """Merge alias mappings from *source* into *target*, avoiding duplicates."""
    for base, aliases in source.items():
        existing = target.setdefault(base, [])
        for a in aliases:
            if a not in existing:
                existing.append(a)


def emit_equation_def(
    eq_name: str,
    eq_def: EquationDef,
    *,
    skip_lead_lag_inference: bool = False,
) -> tuple[str, dict[str, list[str]]]:
    """Emit a single equation definition in GAMS syntax.

    Handles index aliasing to avoid GAMS Error 125 when an equation's domain
    index is reused inside a sum expression.

    Args:
        eq_name: Name of the equation
        eq_def: Equation definition with domain, relation, and LHS/RHS
        skip_lead_lag_inference: If True, do not infer lead/lag domain
            conditions from IndexOffset references. Use this for original
            model equality equations where GAMS evaluates out-of-range lag
            references as 0 (default variable level) rather than skipping
            the equation instance.

    Returns:
        Tuple of (GAMS equation definition string, dict mapping canonical
        lowercase base index names to lists of alias names generated for them)

    Examples:
        >>> # balance(i).. x(i) + y(i) =E= 10;
        >>> # objective.. obj =E= sum(i, c(i) * x(i));
    """
    lhs, rhs = eq_def.lhs_rhs
    domain = eq_def.domain

    # Resolve index conflicts in expressions — also returns generated alias names
    aliases: dict[str, list[str]] = {}
    resolved_lhs, lhs_aliases = resolve_index_conflicts(lhs, domain)
    _merge_alias_dicts(aliases, lhs_aliases)
    resolved_rhs, rhs_aliases = resolve_index_conflicts(rhs, domain)
    _merge_alias_dicts(aliases, rhs_aliases)

    # Convert to GAMS
    # Sprint 18 Day 2: Pass equation domain as domain_vars so domain indices are not quoted
    domain_vars = frozenset(domain) if domain else frozenset()
    lhs_gams = expr_to_gams(resolved_lhs, domain_vars=domain_vars)
    rhs_gams = expr_to_gams(resolved_rhs, domain_vars=domain_vars)

    # Determine relation
    rel_map = {Rel.EQ: "=E=", Rel.LE: "=L=", Rel.GE: "=G="}
    rel_gams = rel_map[eq_def.relation]

    # Detect lead/lag expressions and build domain conditions
    # Issues #649, #652-656: Equations with lead (k+1) or lag (t-1) need restrictions
    # For original model equalities, skip lead/lag inference — GAMS evaluates
    # out-of-range lag references as 0 (default level) rather than skipping
    # the equation instance.
    inferred_condition: str | None = None
    if not skip_lead_lag_inference:
        inferred_condition = infer_lead_lag_condition(eq_def)

    # Combine any parsed equation condition with inferred lead/lag domain bounds
    # Preserve the original parsed $-condition and AND it with the inferred bounds
    all_conditions: list[str] = []
    if eq_def.condition is not None:
        # Convert existing condition to GAMS string
        # Handle both Expr (from parsing) and str (from tests)
        if isinstance(eq_def.condition, str):
            existing_cond = eq_def.condition
        elif isinstance(eq_def.condition, Expr):
            # Apply same conflict resolution as LHS/RHS
            # to avoid GAMS Error 125 if condition has Sum/Prod binding domain indices
            resolved_cond, cond_aliases = resolve_index_conflicts(eq_def.condition, domain)
            _merge_alias_dicts(aliases, cond_aliases)
            existing_cond = expr_to_gams(resolved_cond, domain_vars=domain_vars)
        else:
            # Fallback: try to convert as Expr
            existing_cond = expr_to_gams(eq_def.condition, domain_vars=domain_vars)  # type: ignore[arg-type]
        all_conditions.append(existing_cond)
    if inferred_condition:
        all_conditions.append(inferred_condition)

    if len(all_conditions) == 0:
        final_condition = None
    elif len(all_conditions) == 1:
        final_condition = all_conditions[0]
    else:
        # Combine with 'and' - wrap each in parens for safety
        final_condition = " and ".join(f"({c})" for c in all_conditions)

    # Build equation string
    if domain:
        indices_str = ",".join(domain)
        if final_condition:
            eq_str = (
                f"{eq_name}({indices_str})$({final_condition}).. {lhs_gams} {rel_gams} {rhs_gams};"
            )
        else:
            eq_str = f"{eq_name}({indices_str}).. {lhs_gams} {rel_gams} {rhs_gams};"
    else:
        # Scalar equations can also have conditions (e.g., eq$(cond)..)
        if final_condition:
            eq_str = f"{eq_name}$({final_condition}).. {lhs_gams} {rel_gams} {rhs_gams};"
        else:
            eq_str = f"{eq_name}.. {lhs_gams} {rel_gams} {rhs_gams};"

    # Issue #1292: GAMS rejects input lines longer than 80,000 characters
    # with `Error 98: Non-blank character(s) beyond max input line length`.
    # Some emitted equations (e.g., turkpow's `stat_zt`, where the AD layer
    # enumerates a Cartesian product of `sameas(...)` clauses) easily exceed
    # this — turkpow's pre-fix line was 144,628 chars. Wrap at natural
    # operator boundaries when the line is over the threshold; GAMS accepts
    # newlines anywhere a space would be valid.
    eq_str = _wrap_long_equation_line(eq_str)

    return eq_str, aliases


# Issue #1292: GAMS's input-line limit is 80,000 chars. We use a conservative
# threshold of 60,000 so a wrapped line still fits even after small upstream
# additions (e.g., comment annotations) that the emitter or downstream tools
# might splice in. Each wrapped chunk targets ~10,000 chars, which keeps the
# emission readable in editors and well below GAMS's hard limit.
_GAMS_LINE_WRAP_THRESHOLD = 60000
_GAMS_LINE_WRAP_TARGET = 10000


def _wrap_long_equation_line(eq_str: str) -> str:
    """Insert newlines at natural operator boundaries when an equation line
    exceeds GAMS's 80,000-char input limit.

    Splits at top-level boolean and arithmetic operators in priority order
    (`or`, `and`, `+`, `-`) so the resulting chunks stay below
    ``_GAMS_LINE_WRAP_TARGET`` characters. Splits use plain newlines (no
    indentation); GAMS treats whitespace inside expressions and conditions
    as transparent, so the wrapped form is semantically identical to the
    single-line form.

    The function is a no-op for lines under
    ``_GAMS_LINE_WRAP_THRESHOLD``, so common-case equations (which are far
    below the threshold) are unaffected and Tier 0/1 canaries remain
    byte-identical.
    """
    if len(eq_str) <= _GAMS_LINE_WRAP_THRESHOLD:
        return eq_str

    # Try operators in priority order: `or` is the dominant join in
    # sameas-Cartesian-product cases (turkpow); `and` and ±arithmetic are
    # fallbacks for other shapes. Each separator is bracketed in spaces so
    # we don't split inside identifiers (e.g., `sameas` contains no spaces).
    for sep in (" or ", " and ", " + ", " - "):
        chunks = eq_str.split(sep)
        if len(chunks) <= 1:
            continue

        # Greedy: accumulate chunks into the current line until adding the
        # next chunk would exceed `_GAMS_LINE_WRAP_TARGET`. Then start a
        # new line with `\n` + the separator's leading content (e.g.,
        # `\nor `).
        wrapped: list[str] = []
        current = chunks[0]
        for chunk in chunks[1:]:
            # +len(sep) for the separator we'd add between current and chunk.
            if len(current) + len(sep) + len(chunk) > _GAMS_LINE_WRAP_TARGET:
                # Emit the current line and start a fresh one. The newline
                # replaces the leading space of `sep`, so we keep the
                # operator (e.g., `or`) at the start of the next line.
                wrapped.append(current + "\n" + sep.lstrip())
                current = chunk
            else:
                current = current + sep + chunk
        wrapped.append(current)
        result = "".join(wrapped)
        # If the chosen separator produced any wrap (i.e., the line is
        # actually shorter now), use it. Otherwise fall through and try the
        # next separator.
        if "\n" in result:
            return result

    # No suitable split point — return as-is and let GAMS surface the
    # length error. (In practice this never fires for the emit_equation_def
    # call path: any equation hitting the threshold has at least one of
    # the four boolean/arithmetic operators in it.)
    return eq_str


def _quote_expr_indices(expr: Expr) -> Expr:
    """Pre-quote all string indices in VarRef/ParamRef/MultiplierRef nodes.

    Issue #939: Per-element bound equations are scalar — all indices in VarRef
    and ParamRef are concrete element labels, not domain variables.  By wrapping
    them in double quotes here, ``expr_to_gams`` will see them as already-quoted
    and preserve them verbatim (avoiding the heuristic that treats single-letter
    lowercase identifiers like 'x' as domain variables).

    Only string indices are quoted; IndexOffset objects are left unchanged.
    """

    def _quote_idx(idx: str | IndexOffset) -> str | IndexOffset:
        if isinstance(idx, IndexOffset):
            return idx
        # Already quoted
        if idx.startswith('"') or idx.startswith("'"):
            return idx
        return f'"{idx}"'

    match expr:
        case VarRef():
            new_indices = (
                tuple(_quote_idx(i) for i in expr.indices) if expr.indices else expr.indices
            )
            return VarRef(expr.name, new_indices, attribute=expr.attribute)
        case ParamRef():
            new_indices = (
                tuple(_quote_idx(i) for i in expr.indices) if expr.indices else expr.indices
            )
            return ParamRef(expr.name, new_indices)
        case MultiplierRef():
            new_indices = (
                tuple(_quote_idx(i) for i in expr.indices) if expr.indices else expr.indices
            )
            return MultiplierRef(expr.name, new_indices)
        case Binary(op, left, right):
            return Binary(op, _quote_expr_indices(left), _quote_expr_indices(right))
        case Unary(op, child):
            return Unary(op, _quote_expr_indices(child))
        case Call(func, args):
            return Call(func, tuple(_quote_expr_indices(a) for a in args))
        case DollarConditional(value_expr, condition):
            return DollarConditional(
                _quote_expr_indices(value_expr), _quote_expr_indices(condition)
            )
        case Sum(index_sets, body, condition):
            return Sum(
                index_sets,
                _quote_expr_indices(body),
                _quote_expr_indices(condition) if condition else None,
            )
        case Prod(index_sets, body, condition):
            return Prod(
                index_sets,
                _quote_expr_indices(body),
                _quote_expr_indices(condition) if condition else None,
            )
        case _:
            # Const, SymbolRef, SetMembershipTest, EquationRef, etc. — no indices to quote
            return expr


def emit_normalized_equation_def(eq_name: str, norm_eq: NormalizedEquation) -> str:
    """Emit a normalized equation definition in GAMS syntax.

    Normalized equations have their expression already in canonical form (expr = 0).

    Args:
        eq_name: Name of the equation
        norm_eq: Normalized equation with domain_sets, relation, and expr

    Returns:
        GAMS equation definition string

    Examples:
        >>> # x_fx.. x - 10.0 =E= 0;
        >>> # x_lo.. -(x - 0.0) =L= 0;
    """
    # PR #658: Pass domain_vars so multi-letter domain indices aren't quoted.
    if norm_eq.domain_sets:
        domain_vars: frozenset[str] | None = frozenset(norm_eq.domain_sets)
    else:
        domain_vars = None

    # Issue #939: Per-element bound equations are scalar — all VarRef/ParamRef
    # indices are concrete element labels, not domain variables.  Pre-quote them
    # so expr_to_gams treats them as already-quoted literals (avoids the heuristic
    # that leaves single-letter lowercase identifiers like 'x' unquoted).
    emit_expr = norm_eq.expr
    if norm_eq.index_values and not norm_eq.domain_sets:
        emit_expr = _quote_expr_indices(emit_expr)
    expr_gams = expr_to_gams(emit_expr, domain_vars=domain_vars)

    # Determine relation
    rel_map = {Rel.EQ: "=E=", Rel.LE: "=L=", Rel.GE: "=G="}
    rel_gams = rel_map[norm_eq.relation]

    # Build equation string (normalized equations have RHS = 0)
    if norm_eq.domain_sets:
        indices_str = ",".join(norm_eq.domain_sets)
        return f"{eq_name}({indices_str}).. {expr_gams} {rel_gams} 0;"
    else:
        return f"{eq_name}.. {expr_gams} {rel_gams} 0;"


def _collect_ad_generated_aliases(
    expr: Expr,
    model_ir: ModelIR,
) -> dict[str, list[str]]:
    """Collect AD-generated sum index aliases that need GAMS Alias declarations.

    The AD layer renames remaining sum indices to avoid collisions with matched
    indices (e.g., i → i__, j → j__). These are not known sets or aliases in
    the model_ir, so they need explicit Alias declarations to be valid in GAMS.

    Returns a dict mapping canonical base set name (lowercase) to list of
    generated alias names (e.g., {"i": ["i__", "j__"]}).
    """
    known: set[str] = set()
    for s in model_ir.sets:
        known.add(s.lower())
    for a in model_ir.aliases:
        known.add(a.lower())

    result: dict[str, list[str]] = {}

    def _resolve_root(name: str) -> str:
        """Resolve alias to its root set name (lowercase)."""
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
                break
            current = target
        return current

    def _walk(e: Expr) -> None:
        if isinstance(e, (Sum, Prod)):
            for idx in e.index_sets:
                if idx.lower() not in known:
                    # Try to find the base set by stripping __ suffix
                    base = idx
                    while base.endswith("_"):
                        base = base[:-1]
                    if base and base.lower() in known:
                        root = _resolve_root(base)
                        existing = result.setdefault(root, [])
                        if idx not in existing:
                            existing.append(idx)
            _walk(e.body)
            if e.condition is not None:
                _walk(e.condition)
        elif isinstance(e, Binary):
            _walk(e.left)
            _walk(e.right)
        elif isinstance(e, Unary):
            _walk(e.child)
        elif isinstance(e, Call):
            for arg in e.args:
                _walk(arg)
        elif isinstance(e, DollarConditional):
            _walk(e.value_expr)
            _walk(e.condition)

    _walk(expr)
    return result


def emit_equation_definitions(
    kkt: KKTSystem, suppressed_fx_equations: set[str] | None = None
) -> tuple[str, dict[str, list[str]]]:
    """Emit all equation definitions from KKT system.

    Emits equation definitions for:
    - Stationarity equations (one per primal variable except objvar)
    - Complementarity equations for inequalities
    - Complementarity equations for bounds
    - Original equality equations

    Handles index aliasing to avoid GAMS Error 125 ("Set is under control already")
    when an equation's domain index is reused in a nested sum expression.

    Args:
        kkt: KKT system containing all equations
        suppressed_fx_equations: _fx_ equations to omit from definitions

    Returns:
        Tuple of (GAMS equation definitions as string, dict mapping canonical
        lowercase base index names to lists of alias names generated for them)

    Example output:
        * Stationarity equations
        stat_x(i).. <gradient terms> =E= 0;
        stat_y(j).. <gradient terms> =E= 0;

        * Inequality complementarity
        comp_g1(i).. -g1(i) =E= 0;

        * Bound complementarity
        comp_lo_x(i).. x(i) - x_lo(i) =E= 0;

        * Equality equations
        balance(i).. x(i) + y(i) =E= demand(i);
    """
    lines: list[str] = []
    all_aliases: dict[str, list[str]] = {}

    # Stationarity equations
    if kkt.stationarity:
        lines.append("* Stationarity equations")
        for eq_name in sorted(kkt.stationarity.keys()):
            eq_def = kkt.stationarity[eq_name]
            eq_str, aliases = emit_equation_def(eq_name, eq_def, skip_lead_lag_inference=True)
            lines.append(eq_str)
            _merge_alias_dicts(all_aliases, aliases)
        lines.append("")

    # Skip complementarity equations whose multiplier was simplified away
    # Also skip bound complementarity for unreferenced primal variables
    ref_mults = kkt.referenced_multipliers
    ref_vars = kkt.referenced_variables

    # Inequality complementarity equations (includes min/max complementarity)
    if kkt.complementarity_ineq:
        lines.append("* Inequality complementarity equations")
        for eq_name in sorted(kkt.complementarity_ineq.keys()):
            comp_pair = kkt.complementarity_ineq[eq_name]
            if ref_mults is not None and comp_pair.variable not in ref_mults:
                continue
            eq_str, aliases = emit_equation_def(comp_pair.equation.name, comp_pair.equation)
            lines.append(eq_str)
            _merge_alias_dicts(all_aliases, aliases)
        lines.append("")

    # Lower bound complementarity equations
    if kkt.complementarity_bounds_lo:
        lines.append("* Lower bound complementarity equations")
        for key in sorted(kkt.complementarity_bounds_lo.keys()):
            comp_pair = kkt.complementarity_bounds_lo[key]
            if ref_mults is not None and comp_pair.variable not in ref_mults:
                continue
            if ref_vars is not None and key[0].lower() not in ref_vars:
                continue
            eq_str, aliases = emit_equation_def(comp_pair.equation.name, comp_pair.equation)
            lines.append(eq_str)
            _merge_alias_dicts(all_aliases, aliases)
        lines.append("")

    # Upper bound complementarity equations
    if kkt.complementarity_bounds_up:
        lines.append("* Upper bound complementarity equations")
        for key in sorted(kkt.complementarity_bounds_up.keys()):
            comp_pair = kkt.complementarity_bounds_up[key]
            if ref_mults is not None and comp_pair.variable not in ref_mults:
                continue
            if ref_vars is not None and key[0].lower() not in ref_vars:
                continue
            eq_str, aliases = emit_equation_def(comp_pair.equation.name, comp_pair.equation)
            lines.append(eq_str)
            _merge_alias_dicts(all_aliases, aliases)
        lines.append("")

    # Original equality equations (from model_ir)
    # These include the objective defining equation and fixed variable equalities
    # Note: Equalities can be in either equations dict or normalized_bounds dict
    if kkt.model_ir.equalities:
        from src.kkt.naming import create_eq_multiplier_name
        from src.kkt.objective import extract_objective_info

        try:
            obj_info = extract_objective_info(kkt.model_ir)
            objdef_eq = obj_info.defining_equation
        except ValueError:
            objdef_eq = None

        lines.append("* Original equality equations")
        for eq_name in kkt.model_ir.equalities:
            # Skip _fx_ equations suppressed due to stationarity condition conflict
            if suppressed_fx_equations and eq_name in suppressed_fx_equations:
                continue
            # Skip equations whose multiplier was simplified away,
            # but always keep the objective-defining equation (paired with objvar)
            is_objdef = eq_name == objdef_eq and not kkt.model_ir.strategy1_applied
            if not is_objdef and ref_mults is not None:
                mult_name = create_eq_multiplier_name(eq_name)
                if mult_name not in ref_mults:
                    continue
            # Check both equations dict and normalized_bounds dict
            # Fixed variables (.fx) create equalities stored in normalized_bounds
            if eq_name in kkt.model_ir.equations:
                eq_def = kkt.model_ir.equations[eq_name]
                eq_str, aliases = emit_equation_def(
                    eq_name,
                    eq_def,
                    skip_lead_lag_inference=not eq_def.has_head_domain_offset,
                )
                lines.append(eq_str)
                _merge_alias_dicts(all_aliases, aliases)
            elif eq_name in kkt.model_ir.normalized_bounds:
                norm_eq = kkt.model_ir.normalized_bounds[eq_name]
                lines.append(emit_normalized_equation_def(eq_name, norm_eq))
        lines.append("")

    # Issue #1111: Collect AD-generated sum index aliases (e.g., i__, j__)
    # that need GAMS Alias declarations. These are created by the AD layer's
    # alias-aware partial collapse when differentiating expressions like
    # sum((i,j), p(i)*b(i,j)*p(j)) where Alias(i,j).
    if kkt.stationarity:
        for eq_def in kkt.stationarity.values():
            for side_expr in eq_def.lhs_rhs:
                ad_aliases = _collect_ad_generated_aliases(side_expr, kkt.model_ir)
                _merge_alias_dicts(all_aliases, ad_aliases)

    return "\n".join(lines), all_aliases
