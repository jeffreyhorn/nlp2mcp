"""Equation definition emission for GAMS.

This module emits GAMS equation definitions from KKT system equations.
Each equation is emitted in the form: eq_name(indices).. lhs =E= rhs;

Handles index aliasing to avoid GAMS Error 125 ("Set is under control already")
when an equation's domain index is reused in a nested sum expression.
"""

from src.emit.expr_to_gams import (
    collect_index_aliases,
    expr_to_gams,
    resolve_index_conflicts,
)
from src.ir.normalize import NormalizedEquation
from src.ir.symbols import EquationDef, Rel
from src.kkt.kkt_system import KKTSystem


def emit_equation_def(eq_name: str, eq_def: EquationDef) -> tuple[str, set[str]]:
    """Emit a single equation definition in GAMS syntax.

    Handles index aliasing to avoid GAMS Error 125 when an equation's domain
    index is reused inside a sum expression.

    Args:
        eq_name: Name of the equation
        eq_def: Equation definition with domain, relation, and LHS/RHS

    Returns:
        Tuple of (GAMS equation definition string, set of indices needing aliases)

    Examples:
        >>> # balance(i).. x(i) + y(i) =E= 10;
        >>> # objective.. obj =E= sum(i, c(i) * x(i));
    """
    lhs, rhs = eq_def.lhs_rhs
    domain = eq_def.domain

    # Collect aliases needed from both LHS and RHS
    aliases_needed: set[str] = set()
    aliases_needed.update(collect_index_aliases(lhs, domain))
    aliases_needed.update(collect_index_aliases(rhs, domain))

    # Resolve index conflicts in expressions
    resolved_lhs = resolve_index_conflicts(lhs, domain)
    resolved_rhs = resolve_index_conflicts(rhs, domain)

    # Convert to GAMS
    # Sprint 18 Day 2: Pass equation domain as domain_vars so domain indices are not quoted
    domain_vars = frozenset(domain) if domain else frozenset()
    lhs_gams = expr_to_gams(resolved_lhs, domain_vars=domain_vars)
    rhs_gams = expr_to_gams(resolved_rhs, domain_vars=domain_vars)

    # Determine relation
    rel_map = {Rel.EQ: "=E=", Rel.LE: "=L=", Rel.GE: "=G="}
    rel_gams = rel_map[eq_def.relation]

    # Build equation string
    if domain:
        indices_str = ",".join(domain)
        eq_str = f"{eq_name}({indices_str}).. {lhs_gams} {rel_gams} {rhs_gams};"
    else:
        eq_str = f"{eq_name}.. {lhs_gams} {rel_gams} {rhs_gams};"

    return eq_str, aliases_needed


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
    # Convert expression to GAMS (already normalized as lhs - rhs)
    expr_gams = expr_to_gams(norm_eq.expr)

    # Determine relation
    rel_map = {Rel.EQ: "=E=", Rel.LE: "=L=", Rel.GE: "=G="}
    rel_gams = rel_map[norm_eq.relation]

    # Build equation string (normalized equations have RHS = 0)
    if norm_eq.domain_sets:
        indices_str = ",".join(norm_eq.domain_sets)
        return f"{eq_name}({indices_str}).. {expr_gams} {rel_gams} 0;"
    else:
        return f"{eq_name}.. {expr_gams} {rel_gams} 0;"


def emit_equation_definitions(kkt: KKTSystem) -> tuple[str, set[str]]:
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

    Returns:
        Tuple of (GAMS equation definitions as string, set of indices needing aliases)

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
    all_aliases: set[str] = set()

    # Stationarity equations
    if kkt.stationarity:
        lines.append("* Stationarity equations")
        for eq_name in sorted(kkt.stationarity.keys()):
            eq_def = kkt.stationarity[eq_name]
            eq_str, aliases = emit_equation_def(eq_name, eq_def)
            lines.append(eq_str)
            all_aliases.update(aliases)
        lines.append("")

    # Inequality complementarity equations (includes min/max complementarity)
    if kkt.complementarity_ineq:
        lines.append("* Inequality complementarity equations")
        for eq_name in sorted(kkt.complementarity_ineq.keys()):
            comp_pair = kkt.complementarity_ineq[eq_name]
            eq_str, aliases = emit_equation_def(comp_pair.equation.name, comp_pair.equation)
            lines.append(eq_str)
            all_aliases.update(aliases)
        lines.append("")

    # Lower bound complementarity equations
    if kkt.complementarity_bounds_lo:
        lines.append("* Lower bound complementarity equations")
        for key in sorted(kkt.complementarity_bounds_lo.keys()):
            comp_pair = kkt.complementarity_bounds_lo[key]
            eq_str, aliases = emit_equation_def(comp_pair.equation.name, comp_pair.equation)
            lines.append(eq_str)
            all_aliases.update(aliases)
        lines.append("")

    # Upper bound complementarity equations
    if kkt.complementarity_bounds_up:
        lines.append("* Upper bound complementarity equations")
        for key in sorted(kkt.complementarity_bounds_up.keys()):
            comp_pair = kkt.complementarity_bounds_up[key]
            eq_str, aliases = emit_equation_def(comp_pair.equation.name, comp_pair.equation)
            lines.append(eq_str)
            all_aliases.update(aliases)
        lines.append("")

    # Original equality equations (from model_ir)
    # These include the objective defining equation and fixed variable equalities
    # Note: Equalities can be in either equations dict or normalized_bounds dict
    if kkt.model_ir.equalities:
        lines.append("* Original equality equations")
        for eq_name in kkt.model_ir.equalities:
            # Check both equations dict and normalized_bounds dict
            # Fixed variables (.fx) create equalities stored in normalized_bounds
            if eq_name in kkt.model_ir.equations:
                eq_def = kkt.model_ir.equations[eq_name]
                eq_str, aliases = emit_equation_def(eq_name, eq_def)
                lines.append(eq_str)
                all_aliases.update(aliases)
            elif eq_name in kkt.model_ir.normalized_bounds:
                norm_eq = kkt.model_ir.normalized_bounds[eq_name]
                lines.append(emit_normalized_equation_def(eq_name, norm_eq))
        lines.append("")

    return "\n".join(lines), all_aliases
