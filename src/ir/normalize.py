from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .ast import Binary, Const, Expr, SymbolRef, VarRef
from .model_ir import ModelIR
from .symbols import EquationDef, Rel


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


def subtract(lhs: Expr, rhs: Expr) -> Expr:
    """Build lhs - rhs as a Binary node."""
    return Binary("-", lhs, rhs)


def _extract_objective_expression(equations: dict[str, EquationDef], objvar: str) -> Expr:
    """
    Extract objective expression from equations before normalization.

    This function searches through equations to find one that defines the objective
    variable and extracts the expression. It should be called BEFORE normalization
    to avoid issues with restructured equations.

    Args:
        equations: Dictionary of equation definitions
        objvar: Name of the objective variable to find

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
    )


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
            ir.objective.expr = _extract_objective_expression(ir.equations, objvar)
        except ValueError:
            # If no defining equation is found, that's OK - the objective might be
            # just a simple variable reference. The AD code will handle this case.
            # Only models with obj =e= expr pattern need extraction.
            pass

    norm: dict[str, NormalizedEquation] = {}
    bounds: dict[str, NormalizedEquation] = {}
    ir.equalities.clear()
    ir.inequalities.clear()

    for name, eq in ir.equations.items():
        n = normalize_equation(eq)
        norm[name] = n
        if n.relation == Rel.EQ:
            ir.equalities.append(name)
        else:
            ir.inequalities.append(name)

    for var_name, var in ir.variables.items():

        def add_bound(
            suffix: str,
            indices: tuple[str, ...],
            kind: Rel,
            expr: Expr,
            domain_sets: Sequence[str],
        ):
            bound_name = _bound_name(var_name, suffix, indices)
            expr = _attach_domain(expr, domain_sets)
            bounds[bound_name] = NormalizedEquation(
                name=bound_name,
                domain_sets=tuple(domain_sets),
                index_values=indices,
                relation=kind,
                expr=expr,
                expr_domain=_expr_domain(expr),
                rank=len(_expr_domain(expr)),
            )
            if kind == Rel.EQ:
                ir.equalities.append(bound_name)
            else:
                ir.inequalities.append(bound_name)

        for indices, value in _iterate_bounds(var.lo_map, var.lo):
            expr = _binary("-", _const(value, var.domain), _var_ref(var_name, indices, var.domain))
            add_bound("lo", indices, Rel.LE, expr, var.domain)
        for indices, value in _iterate_bounds(var.up_map, var.up):
            expr = _binary("-", _var_ref(var_name, indices, var.domain), _const(value, var.domain))
            add_bound("up", indices, Rel.LE, expr, var.domain)
        for indices, value in _iterate_bounds(var.fx_map, var.fx):
            expr = _binary("-", _var_ref(var_name, indices, var.domain), _const(value, var.domain))
            add_bound("fx", indices, Rel.EQ, expr, var.domain)

    ir.normalized_bounds = bounds
    return norm, bounds


def _iterate_bounds(map_bounds: dict[tuple[str, ...], float], scalar: float | None):
    if scalar is not None:
        yield (), scalar
    yield from map_bounds.items()


def _bound_name(var: str, suffix: str, indices: tuple[str, ...]) -> str:
    if not indices:
        return f"{var}_{suffix}"
    joined = ",".join(indices)
    return f"{var}_{suffix}({joined})"


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
