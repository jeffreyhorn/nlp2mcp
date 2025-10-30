"""GAMS code generation templates for KKT systems.

This module provides template functions for emitting GAMS code from KKT systems,
with variable kind preservation (Finding #4 from final review).
"""

from src.ir.symbols import VarKind
from src.kkt.kkt_system import KKTSystem


def emit_variables(kkt: KKTSystem) -> str:
    """Emit Variables blocks grouped by VariableDef.kind.

    **CRITICAL (Finding #4)**: Preserves variable kinds from source model.
    Primal variables grouped by their kind (Positive/Binary/Integer/etc.).
    Multipliers added to appropriate groups:
    - Free multipliers (ν for equalities) → CONTINUOUS
    - Positive multipliers (λ, π^L, π^U) → POSITIVE

    Args:
        kkt: KKT system containing variables and multipliers

    Returns:
        GAMS Variables blocks as string

    Example output:
        Variables
            obj           "Objective variable"
            nu_balance    "Multiplier for balance equation"
        ;

        Positive Variables
            x
            lam_g1        "Multiplier for inequality g1"
            piL_x         "Multiplier for lower bound on x"
            piU_x         "Multiplier for upper bound on x"
        ;

        Binary Variables
            y             "Binary decision variable"
        ;
    """
    # Group variables by kind (Finding #4)
    var_groups: dict[VarKind, list[tuple[str, tuple[str, ...]]]] = {
        VarKind.CONTINUOUS: [],
        VarKind.POSITIVE: [],
        VarKind.NEGATIVE: [],
        VarKind.BINARY: [],
        VarKind.INTEGER: [],
    }

    # Group primal variables by kind
    for var_name, var_def in kkt.model_ir.variables.items():
        var_groups[var_def.kind].append((var_name, var_def.domain))

    # Add multipliers to appropriate groups
    # Free multipliers (ν for equalities) → CONTINUOUS
    for mult_name, mult_def in kkt.multipliers_eq.items():
        var_groups[VarKind.CONTINUOUS].append((mult_name, mult_def.domain))

    # Positive multipliers (λ, π^L, π^U) → POSITIVE
    for mult_name, mult_def in kkt.multipliers_ineq.items():
        var_groups[VarKind.POSITIVE].append((mult_name, mult_def.domain))

    # Bound multipliers use tuple keys (var_name, indices)
    for (_var_name, _indices), mult_def in kkt.multipliers_bounds_lo.items():
        var_groups[VarKind.POSITIVE].append((mult_def.name, mult_def.domain))

    for (_var_name, _indices), mult_def in kkt.multipliers_bounds_up.items():
        var_groups[VarKind.POSITIVE].append((mult_def.name, mult_def.domain))

    # Emit blocks
    lines: list[str] = []

    kind_to_block = {
        VarKind.CONTINUOUS: "Variables",
        VarKind.POSITIVE: "Positive Variables",
        VarKind.NEGATIVE: "Negative Variables",
        VarKind.BINARY: "Binary Variables",
        VarKind.INTEGER: "Integer Variables",
    }

    for kind, block_name in kind_to_block.items():
        if var_groups[kind]:
            if lines:  # Add blank line between blocks
                lines.append("")
            lines.append(block_name)
            for var_name, domain in var_groups[kind]:
                if domain:
                    domain_str = ",".join(domain)
                    lines.append(f"    {var_name}({domain_str})")
                else:
                    lines.append(f"    {var_name}")
            lines.append(";")

    return "\n".join(lines)


def emit_kkt_sets(kkt: KKTSystem) -> str:
    """Emit Sets block for KKT system indexing.

    Extracts unique index sets from multiplier and equation domains.

    Args:
        kkt: KKT system

    Returns:
        GAMS Sets block for KKT indices

    Example output:
        Sets
            eq_rows   /balance, flow/
            ineq_rows /capacity, demand/
        ;
    """
    # For now, return empty as this is typically handled by original model sets
    # This placeholder will be expanded in future if needed
    return ""


def emit_equations(kkt: KKTSystem) -> str:
    """Emit Equations block declarations.

    Declares all equation names (stationarity, complementarity, equality).

    Args:
        kkt: KKT system

    Returns:
        GAMS Equations block

    Example output:
        Equations
            stat_x
            stat_y
            comp_g1
            comp_lo_x
            eq_balance
        ;
    """
    lines = ["Equations"]

    # Stationarity equations
    for eq_name in sorted(kkt.stationarity.keys()):
        lines.append(f"    {eq_name}")

    # Inequality complementarity equations
    for eq_name in sorted(kkt.complementarity_ineq.keys()):
        comp_eq_name = kkt.complementarity_ineq[eq_name].equation.name
        lines.append(f"    {comp_eq_name}")

    # Bound complementarity equations
    for key in sorted(kkt.complementarity_bounds_lo.keys()):
        comp_pair = kkt.complementarity_bounds_lo[key]
        lines.append(f"    {comp_pair.equation.name}")

    for key in sorted(kkt.complementarity_bounds_up.keys()):
        comp_pair = kkt.complementarity_bounds_up[key]
        lines.append(f"    {comp_pair.equation.name}")

    lines.append(";")

    return "\n".join(lines)


def emit_equation_definitions(kkt: KKTSystem) -> str:
    """Emit equation definitions (eq_name.. lhs =E= rhs;).

    This is a placeholder for Day 5 implementation.

    Args:
        kkt: KKT system

    Returns:
        Empty string (to be implemented Day 5)
    """
    # Day 5: Will implement AST → GAMS conversion
    return ""


def emit_model(kkt: KKTSystem) -> str:
    """Emit Model MCP block with complementarity pairs.

    This is a placeholder for Day 6 implementation.

    Args:
        kkt: KKT system

    Returns:
        Empty string (to be implemented Day 6)
    """
    # Day 6: Will implement Model MCP syntax
    return ""


def emit_solve(kkt: KKTSystem) -> str:
    """Emit Solve statement.

    This is a placeholder for Day 6 implementation.

    Args:
        kkt: KKT system

    Returns:
        Empty string (to be implemented Day 6)
    """
    # Day 6: Will implement Solve statement
    return ""
