"""Equation definition emission for GAMS.

This module emits GAMS equation definitions from KKT system equations.
Each equation is emitted in the form: eq_name(indices).. lhs =E= rhs;
"""

from src.emit.expr_to_gams import expr_to_gams
from src.ir.symbols import EquationDef, Rel
from src.kkt.kkt_system import KKTSystem


def emit_equation_def(eq_name: str, eq_def: EquationDef) -> str:
    """Emit a single equation definition in GAMS syntax.

    Args:
        eq_name: Name of the equation
        eq_def: Equation definition with domain, relation, and LHS/RHS

    Returns:
        GAMS equation definition string

    Examples:
        >>> # balance(i).. x(i) + y(i) =E= 10;
        >>> # objective.. obj =E= sum(i, c(i) * x(i));
    """
    # Convert LHS and RHS to GAMS
    lhs, rhs = eq_def.lhs_rhs
    lhs_gams = expr_to_gams(lhs)
    rhs_gams = expr_to_gams(rhs)

    # Determine relation
    rel_map = {Rel.EQ: "=E=", Rel.LE: "=L=", Rel.GE: "=G="}
    rel_gams = rel_map[eq_def.relation]

    # Build equation string
    if eq_def.domain:
        indices_str = ",".join(eq_def.domain)
        return f"{eq_name}({indices_str}).. {lhs_gams} {rel_gams} {rhs_gams};"
    else:
        return f"{eq_name}.. {lhs_gams} {rel_gams} {rhs_gams};"


def emit_equation_definitions(kkt: KKTSystem) -> str:
    """Emit all equation definitions from KKT system.

    Emits equation definitions for:
    - Stationarity equations (one per primal variable except objvar)
    - Complementarity equations for inequalities
    - Complementarity equations for bounds
    - Original equality equations

    Args:
        kkt: KKT system containing all equations

    Returns:
        GAMS equation definitions as string

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

    # Stationarity equations
    if kkt.stationarity:
        lines.append("* Stationarity equations")
        for eq_name in sorted(kkt.stationarity.keys()):
            eq_def = kkt.stationarity[eq_name]
            lines.append(emit_equation_def(eq_name, eq_def))
        lines.append("")

    # Inequality complementarity equations
    if kkt.complementarity_ineq:
        lines.append("* Inequality complementarity equations")
        for eq_name in sorted(kkt.complementarity_ineq.keys()):
            comp_pair = kkt.complementarity_ineq[eq_name]
            lines.append(emit_equation_def(comp_pair.equation.name, comp_pair.equation))
        lines.append("")

    # Lower bound complementarity equations
    if kkt.complementarity_bounds_lo:
        lines.append("* Lower bound complementarity equations")
        for key in sorted(kkt.complementarity_bounds_lo.keys()):
            comp_pair = kkt.complementarity_bounds_lo[key]
            lines.append(emit_equation_def(comp_pair.equation.name, comp_pair.equation))
        lines.append("")

    # Upper bound complementarity equations
    if kkt.complementarity_bounds_up:
        lines.append("* Upper bound complementarity equations")
        for key in sorted(kkt.complementarity_bounds_up.keys()):
            comp_pair = kkt.complementarity_bounds_up[key]
            lines.append(emit_equation_def(comp_pair.equation.name, comp_pair.equation))
        lines.append("")

    # Original equality equations (from model_ir)
    # These include the objective defining equation
    if kkt.model_ir.equalities:
        lines.append("* Original equality equations")
        for eq_name in kkt.model_ir.equalities:
            if eq_name in kkt.model_ir.equations:
                eq_def = kkt.model_ir.equations[eq_name]
                lines.append(emit_equation_def(eq_name, eq_def))
        lines.append("")

    return "\n".join(lines)
