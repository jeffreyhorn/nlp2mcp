"""Complementarity equation builder for KKT system assembly.

Builds complementarity conditions for:
- Inequalities: g(x) ⊥ λ ≥ 0 (converted to -g(x) ≥ 0 ⊥ λ ≥ 0)
- Lower bounds: (x - lo) ⊥ π^L ≥ 0
- Upper bounds: (up - x) ⊥ π^U ≥ 0
- Equalities: h(x) = 0 with ν free

Key features:
- Includes objective defining equation in equalities
- Handles indexed bounds correctly (per-instance complementarity pairs)
- Only processes finite bounds (infinite bounds already filtered)
- Duplicate bounds already excluded by partition (Finding #1)
"""

from __future__ import annotations

from src.ir.ast import Binary, Const, Unary, VarRef
from src.ir.symbols import EquationDef, Rel
from src.kkt.kkt_system import ComplementarityPair, KKTSystem
from src.kkt.naming import (
    create_bound_lo_multiplier_name,
    create_bound_up_multiplier_name,
    create_ineq_multiplier_name,
)
from src.kkt.partition import partition_constraints
from src.kkt.reformulation import MINMAX_MAX_CONSTRAINT_PREFIX


def build_complementarity_pairs(
    kkt: KKTSystem,
) -> tuple[
    dict[str, ComplementarityPair],
    dict[tuple, ComplementarityPair],
    dict[tuple, ComplementarityPair],
    dict[str, EquationDef],
]:
    """Build complementarity pairs for inequalities, bounds, and equality equations.

    Complementarity in MCP format:
    - Inequalities: -g(x) ≥ 0 ⊥ λ ≥ 0 (negated to positive slack form)
    - Lower bounds: (x - lo) ≥ 0 ⊥ π^L ≥ 0
    - Upper bounds: (up - x) ≥ 0 ⊥ π^U ≥ 0
    - Equalities: h(x) = 0 with ν free (no complementarity, just equation)

    Args:
        kkt: KKT system with model IR and partition results

    Returns:
        Tuple of:
        - comp_ineq: Complementarity pairs for inequalities, keyed by equation name
        - comp_bounds_lo: Complementarity pairs for lower bounds, keyed by (var_name, indices)
        - comp_bounds_up: Complementarity pairs for upper bounds, keyed by (var_name, indices)
        - equality_eqs: Equality equations (including objective defining equation)

    Example:
        >>> comp_ineq, comp_lo, comp_up, eq_eqs = build_complementarity_pairs(kkt)
        >>> comp_ineq["capacity"]  # Inequality constraint
        >>> comp_lo[("x", ())]  # Lower bound on scalar variable x
        >>> comp_lo[("y", ("i1",))]  # Lower bound on indexed variable y(i1)
        >>> eq_eqs["objdef"]  # Objective defining equation
    """
    comp_ineq: dict[str, ComplementarityPair] = {}
    comp_bounds_lo: dict[tuple, ComplementarityPair] = {}
    comp_bounds_up: dict[tuple, ComplementarityPair] = {}
    equality_eqs: dict[str, EquationDef] = {}

    # Partition constraints to get bounds (already filtered and deduplicated)
    partition = partition_constraints(kkt.model_ir)

    # Build inequality complementarity: -g(x) ≥ 0 ⊥ λ ≥ 0
    for eq_name in partition.inequalities:
        if eq_name not in kkt.model_ir.equations:
            continue

        eq_def = kkt.model_ir.equations[eq_name]

        # Handle both <= and >= inequalities
        # For g(x) <= 0: negate to get -g(x) >= 0 for MCP
        # For g(x) >= 0: use as-is for MCP
        g_expr = eq_def.lhs_rhs[0]

        if eq_def.relation == Rel.LE:
            # g(x) <= 0 becomes -g(x) >= 0
            F_lam = Unary("-", g_expr)
            negated = True
        elif eq_def.relation == Rel.GE:
            # g(x) >= 0 stays as g(x) >= 0
            F_lam = g_expr
            negated = False
        else:
            raise ValueError(f"Expected inequality (LE or GE), got {eq_def.relation}")

        # Create multiplier name
        lam_name = create_ineq_multiplier_name(eq_name)

        # Create complementarity equation
        comp_eq = EquationDef(
            name=f"comp_{eq_name}",
            domain=eq_def.domain,
            relation=Rel.GE,
            lhs_rhs=(F_lam, Const(0.0)),
        )

        # Check if this is a max constraint from reformulation
        # Max constraints use pattern: minmax_max_{context}_{index}_arg{i}
        is_max_constraint = eq_name.startswith(MINMAX_MAX_CONSTRAINT_PREFIX)

        comp_ineq[eq_name] = ComplementarityPair(
            equation=comp_eq,
            variable=lam_name,
            variable_indices=eq_def.domain,
            negated=negated,
            is_max_constraint=is_max_constraint,
        )

    # Build equality equations: h(x) = 0 with ν free
    # IMPORTANT: Include objective defining equation and fixed variable equalities
    # Note: Equalities can be in either equations dict or normalized_bounds dict
    for eq_name in partition.equalities:
        # Check both equations dict and normalized_bounds dict
        # Fixed variables (.fx) create equalities stored in normalized_bounds
        if eq_name in kkt.model_ir.equations:
            eq_def = kkt.model_ir.equations[eq_name]
            # Equality equations are simply h(x) = 0
            h_expr = eq_def.lhs_rhs[0]
            domain = eq_def.domain
        elif eq_name in kkt.model_ir.normalized_bounds:
            norm_eq = kkt.model_ir.normalized_bounds[eq_name]
            # Normalized equations already have expr in form (lhs - rhs)
            h_expr = norm_eq.expr
            domain = norm_eq.domain_sets
        else:
            continue

        equality_eq = EquationDef(
            name=f"eq_{eq_name}",
            domain=domain,
            relation=Rel.EQ,
            lhs_rhs=(h_expr, Const(0.0)),
        )

        equality_eqs[eq_name] = equality_eq

    # Build lower bound complementarity: (x - lo) ≥ 0 ⊥ π^L ≥ 0
    # Note: partition.bounds_lo only contains finite bounds (Finding #2)
    for (var_name, indices), bound_def in partition.bounds_lo.items():
        # F_π^L = x(i) - lo
        F_piL = Binary("-", VarRef(var_name, indices), Const(bound_def.value))

        # Create multiplier name
        piL_name = create_bound_lo_multiplier_name(var_name)

        # Create complementarity equation
        comp_eq = EquationDef(
            name=f"comp_lo_{var_name}{'_' + '_'.join(indices) if indices else ''}",
            domain=bound_def.domain,
            relation=Rel.GE,
            lhs_rhs=(F_piL, Const(0.0)),
        )

        comp_bounds_lo[(var_name, indices)] = ComplementarityPair(
            equation=comp_eq, variable=piL_name, variable_indices=indices
        )

    # Build upper bound complementarity: (up - x) ≥ 0 ⊥ π^U ≥ 0
    # Note: partition.bounds_up only contains finite bounds (Finding #2)
    for (var_name, indices), bound_def in partition.bounds_up.items():
        # F_π^U = up - x(i)
        F_piU = Binary("-", Const(bound_def.value), VarRef(var_name, indices))

        # Create multiplier name
        piU_name = create_bound_up_multiplier_name(var_name)

        # Create complementarity equation
        comp_eq = EquationDef(
            name=f"comp_up_{var_name}{'_' + '_'.join(indices) if indices else ''}",
            domain=bound_def.domain,
            relation=Rel.GE,
            lhs_rhs=(F_piU, Const(0.0)),
        )

        comp_bounds_up[(var_name, indices)] = ComplementarityPair(
            equation=comp_eq, variable=piU_name, variable_indices=indices
        )

    return comp_ineq, comp_bounds_lo, comp_bounds_up, equality_eqs
