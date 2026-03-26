from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import cast

from .ast import Binary, Const, Expr, SymbolRef, VarRef
from .model_ir import ModelIR
from .symbols import EquationDef, Rel, SourceLocation


@dataclass
class NormalizedEquation:
    """Holds a canonicalized equation: lhs - rhs with a single relation tag."""

    name: str
    domain_sets: tuple[str, ...]
    index_values: tuple[str, ...]
    relation: Rel
    expr: Expr  # canonicalized as (lhs - rhs)
    expr_domain: tuple[str, ...]
    rank: int
    condition: Expr | None = None  # Optional condition for $ operator filtering
    source_location: SourceLocation | None = None  # Source location of equation definition


def subtract(lhs: Expr, rhs: Expr) -> Expr:
    """Build lhs - rhs as a Binary node."""
    return Binary("-", lhs, rhs)


def _extract_objective_expression(
    equations: dict[str, EquationDef],
    objvar: str,
    model_eq_set: set[str] | None = None,
) -> Expr:
    """
    Extract objective expression from equations before normalization.

    This function searches through equations to find one that defines the objective
    variable and extracts the expression. It should be called BEFORE normalization
    to avoid issues with restructured equations.

    Args:
        equations: Dictionary of equation definitions
        objvar: Name of the objective variable to find
        model_eq_set: Optional set of lowercase equation names to restrict search
            (Issue #1033: only consider equations in the solved model).

    Returns:
        Expression that defines the objective

    Raises:
        ValueError: If objective variable is not defined by any equation

    Examples:
        >>> # Equation: obj =e= x^2 + y
        >>> equations = {"obj_def": EquationDef(...)}
        >>> expr = _extract_objective_expression(equations, "obj")
        >>> # Returns: Binary("+", Call("power", ...), VarRef("y"))
    """
    for _eq_name, eq_def in equations.items():
        # Issue #1033: Skip equations not in the solved model
        if model_eq_set is not None and _eq_name.lower() not in model_eq_set:
            continue
        # Skip indexed equations (objective must be scalar)
        if eq_def.domain:
            continue

        # Check if this equation defines the objective variable
        lhs, rhs = eq_def.lhs_rhs

        # Check if lhs is the objvar (then use rhs as expression)
        # Can be either SymbolRef or VarRef (scalar, with no indices)
        if (isinstance(lhs, SymbolRef) and lhs.name == objvar) or (
            isinstance(lhs, VarRef) and lhs.name == objvar and not lhs.indices
        ):
            return rhs

        # Check if rhs is the objvar (then use lhs as expression)
        if (isinstance(rhs, SymbolRef) and rhs.name == objvar) or (
            isinstance(rhs, VarRef) and rhs.name == objvar and not rhs.indices
        ):
            return lhs

    # No defining equation found - return None (validation will catch this later if needed)
    return None


def normalize_equation(eq: EquationDef) -> NormalizedEquation:
    lhs, rhs = eq.lhs_rhs
    relation = eq.relation
    expr = _binary("-", lhs, rhs)
    if relation == Rel.GE:
        expr = _binary("-", rhs, lhs)
        relation = Rel.LE
    domain_sets = tuple(eq.domain)
    expr_domain = _expr_domain(expr) or tuple(eq.domain)
    return NormalizedEquation(
        name=eq.name,
        domain_sets=domain_sets,
        index_values=(),
        relation=relation,
        expr=expr,
        expr_domain=expr_domain,
        rank=len(expr_domain),
        condition=cast(Expr | None, eq.condition),
        source_location=eq.source_location,
    )


def _collect_vars_in_equations(ir: ModelIR, model_eq_set: set[str]) -> set[str]:
    """Collect variable names referenced in the given equations and the objective.

    Issue #1033: Used to filter out variables that belong to other model
    formulations when equation filtering is active.
    """
    referenced: set[str] = set()

    def _walk(expr: Expr) -> None:
        if isinstance(expr, VarRef):
            referenced.add(expr.name.lower())
        for child in expr.children():
            _walk(child)

    for name, eq in ir.equations.items():
        if name.lower() not in model_eq_set:
            continue
        # EquationDef stores (lhs, rhs) as a tuple in lhs_rhs
        if eq.lhs_rhs:
            for side in eq.lhs_rhs:
                if isinstance(side, Expr):
                    _walk(side)

    # Also include the objective variable
    if ir.objective:
        referenced.add(ir.objective.objvar.lower())
        if ir.objective.expr:
            _walk(ir.objective.expr)

    return referenced


def normalize_model(
    ir: ModelIR,
) -> tuple[dict[str, NormalizedEquation], dict[str, NormalizedEquation]]:
    """
    - Convert each equation to canonical form (lhs - rhs REL 0).
    - Partition equalities vs inequalities; leave direction tags to later pass.
    - Emit additional normalized inequalities/equalities for variable bounds.
    - Return maps: (equations, bounds).

    Note: This function extracts and stores the objective expression BEFORE
    normalization to avoid issues with finding it after equations are restructured.
    See GitHub Issue #19 for details.
    """
    # Issue #1154: When multiple solves use different models, the last non-MCP
    # solve wins. But if the last solve's model is a superset of an earlier
    # solve's model (i.e., it references the earlier model plus extras), the
    # tool should prefer the simpler (earlier) model for KKT conversion.
    # This handles spatequ where P2R3_NonLinear references P2R3_Linear.
    _solve_objectives = ir._solve_objectives
    if _solve_objectives and ir.model_name and len(_solve_objectives) > 1:
        current_eqs = ir.model_equation_map.get(ir.model_name.lower(), [])
        # Check if the current model references another model by name.
        # Treat an entry as a model reference only if it is not also an equation.
        refs_other_model = any(
            (ref_lower := eq.lower()) in ir.model_equation_map and ref_lower not in ir.equations
            for eq in current_eqs
        )
        if refs_other_model:
            # Find the referenced sub-model and use it instead
            for eq in current_eqs:
                ref_lower = eq.lower()
                if (
                    ref_lower in ir.model_equation_map
                    and ref_lower not in ir.equations
                    and ref_lower in _solve_objectives
                ):
                    ir.model_name = eq
                    ir.objective = _solve_objectives[ref_lower]
                    break

    # Issue #1033: Compute model equation set BEFORE objective extraction
    # so that only equations in the solved model are considered.
    model_eq_set: set[str] | None = None
    solved_model_eqs = ir.get_solved_model_equations()
    if solved_model_eqs:
        model_eq_set = {eq.lower() for eq in solved_model_eqs}

    # IMPORTANT: Extract objective expression BEFORE normalization
    # After normalization, equations are restructured and the objective
    # variable may not be easily found. Extract it now while equations
    # are in their original form.
    #
    # Only attempt extraction if:
    # 1. An objective exists
    # 2. The objective expression is not already set (ObjectiveIR.expr is None)
    # 3. There might be a defining equation to extract from
    if ir.objective and not ir.objective.expr and ir.equations:
        objvar = ir.objective.objvar
        try:
            ir.objective.expr = _extract_objective_expression(
                ir.equations, objvar, model_eq_set=model_eq_set
            )
        except ValueError:
            # If no defining equation is found, that's OK - the objective might be
            # just a simple variable reference. The AD code will handle this case.
            # Only models with obj =e= expr pattern need extraction.
            pass

    norm: dict[str, NormalizedEquation] = {}
    bounds: dict[str, NormalizedEquation] = {}
    ir.equalities.clear()
    ir.inequalities.clear()

    for name, eq_def in ir.equations.items():  # type: ignore[assignment]
        if model_eq_set is not None and name.lower() not in model_eq_set:
            continue
        n = normalize_equation(eq_def)  # type: ignore[arg-type]
        norm[name] = n
        if n.relation == Rel.EQ:
            ir.equalities.append(name)
        else:
            ir.inequalities.append(name)

    # Issue #1033: When equations were filtered, also remove variables that
    # are not referenced in any included equation or the objective.  This
    # prevents discrete variables from other formulations from leaking into
    # the MCP model (e.g., SOS2/Binary variables from MIP formulations).
    if model_eq_set is not None:
        referenced_vars = _collect_vars_in_equations(ir, model_eq_set)
        unreferenced = [vn for vn in ir.variables.keys() if vn.lower() not in referenced_vars]
        for vn in unreferenced:
            del ir.variables[vn]

    for var_name, var in ir.variables.items():

        def add_bound(
            suffix: str,
            indices: tuple[str, ...],
            kind: Rel,
            expr: Expr,
            domain_sets: Sequence[str],
        ):
            bnd_name = bound_name(var_name, suffix, indices)
            expr = _attach_domain(expr, domain_sets)
            bounds[bnd_name] = NormalizedEquation(
                name=bnd_name,
                domain_sets=tuple(domain_sets),
                index_values=indices,
                relation=kind,
                expr=expr,
                expr_domain=_expr_domain(expr),
                rank=len(_expr_domain(expr)),
            )
            if kind == Rel.EQ:
                ir.equalities.append(bnd_name)
            else:
                ir.inequalities.append(bnd_name)

        for indices, value in _iterate_bounds(var.lo_map, var.lo):
            expr = _binary("-", _const(value, var.domain), _var_ref(var_name, indices, var.domain))
            # Per-element bounds (indices non-empty) are scalar equations, not indexed
            bound_domain = () if indices else var.domain
            add_bound("lo", indices, Rel.LE, expr, bound_domain)
        for indices, value in _iterate_bounds(var.up_map, var.up):
            expr = _binary("-", _var_ref(var_name, indices, var.domain), _const(value, var.domain))
            # Per-element bounds (indices non-empty) are scalar equations, not indexed
            bound_domain = () if indices else var.domain
            add_bound("up", indices, Rel.LE, expr, bound_domain)
        for indices, value in _iterate_bounds(var.fx_map, var.fx):
            expr = _binary("-", _var_ref(var_name, indices, var.domain), _const(value, var.domain))
            # Per-element bounds (indices non-empty) are scalar equations, not indexed
            bound_domain = () if indices else var.domain
            add_bound("fx", indices, Rel.EQ, expr, bound_domain)

    ir.normalized_bounds = bounds
    return norm, bounds


def _iterate_bounds(map_bounds: dict[tuple[str, ...], float], scalar: float | None):
    if scalar is not None:
        yield (), scalar
    yield from map_bounds.items()


def _sanitize_identifier(s: str) -> str:
    """Sanitize a string for use in a GAMS identifier with collision avoidance.

    PR #658 review: Uses the shared sanitize_index_for_identifier from kkt/naming.py
    for consistent sanitization across the pipeline. Adds a hash suffix when the
    string was modified to reduce collision probability (e.g., "q-1" and "q_1" would
    otherwise both become "q_1").

    Args:
        s: Raw string to sanitize

    Returns:
        Sanitized string safe for use in GAMS identifiers, with hash suffix if modified

    Note:
        The 8-character hex hash suffix provides ~4 billion unique values, making
        collisions extremely unlikely for practical model sizes.
    """
    import hashlib

    from ..kkt.naming import sanitize_index_for_identifier

    # Use the shared sanitizer for consistent behavior
    sanitized = sanitize_index_for_identifier(s)

    # If sanitization changed the string, append a hash to reduce collision probability
    if sanitized != s:
        # PR #658 review: Use 8 hex chars (32 bits) for better collision resistance
        # than the original 4 chars. This provides ~4 billion unique values.
        # PR #658 review: Use SHA-256 instead of MD5 for FIPS compatibility.
        # MD5 can be disabled in FIPS mode, causing runtime errors.
        hash_suffix = hashlib.sha256(s.encode("utf-8")).hexdigest()[:8]
        return f"{sanitized}_{hash_suffix}"

    return sanitized


def bound_name(var: str, suffix: str, indices: tuple[str, ...]) -> str:
    if not indices:
        return f"{var}_{suffix}"
    # Use underscores instead of parentheses for valid GAMS identifiers
    # e.g., x_fx_1 instead of x_fx(1) which is invalid GAMS syntax
    # PR #658: Sanitize indices to handle special characters (e.g., "q-1" -> "q_1")
    sanitized = [_sanitize_identifier(idx) for idx in indices]
    joined = "_".join(sanitized)
    return f"{var}_{suffix}_{joined}"


def _expr_domain(expr: Expr) -> tuple[str, ...]:
    return getattr(expr, "domain", ())


def _const(value: float, domain: Sequence[str]) -> Const:
    expr = Const(value)
    return _attach_domain(expr, domain)


def _var_ref(name: str, indices: tuple[str, ...], domain_sets: Sequence[str]) -> VarRef:
    expr = VarRef(name, indices)
    object.__setattr__(expr, "symbol_domain", tuple(domain_sets))
    object.__setattr__(expr, "index_values", tuple(indices))
    return _attach_domain(expr, domain_sets)


def _binary(op: str, left: Expr, right: Expr) -> Binary:
    expr = Binary(op, left, right)
    domain = _merge_domains([left, right])
    return _attach_domain(expr, domain)


def _attach_domain(expr: Expr, domain: Sequence[str]) -> Expr:
    domain_tuple = tuple(domain)
    object.__setattr__(expr, "domain", domain_tuple)
    object.__setattr__(expr, "free_domain", domain_tuple)
    object.__setattr__(expr, "rank", len(domain_tuple))
    return expr


def _merge_domains(exprs: Sequence[Expr]) -> tuple[str, ...]:
    domains = [tuple(getattr(expr, "domain", ())) for expr in exprs if expr is not None]
    if not domains:
        return ()
    first = domains[0]
    for d in domains[1:]:
        if d != first:
            raise ValueError("Domain mismatch during normalization")
    return first
