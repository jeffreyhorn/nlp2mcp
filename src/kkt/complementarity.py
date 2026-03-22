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

from src.ad.index_mapping import enumerate_variable_instances
from src.ir.ast import (
    Binary,
    Const,
    Expr,
    LhsConditionalAssign,
    ParamRef,
    SetMembershipTest,
    SymbolRef,
    Unary,
    VarRef,
)
from src.ir.symbols import EquationDef, Rel
from src.kkt.kkt_system import ComplementarityPair, KKTSystem
from src.kkt.naming import (
    create_bound_lo_multiplier_name,
    create_bound_up_multiplier_name,
    create_ineq_multiplier_name,
)
from src.kkt.partition import BoundDef, partition_constraints
from src.kkt.reformulation import MINMAX_MAX_CONSTRAINT_PREFIX


def _bound_expr(bound_def: BoundDef) -> Expr:
    """Return the bound as an Expr: uses bound_def.expr if set, else Const(value).

    If the bound expression is a LhsConditionalAssign, extract only the RHS
    value for use in KKT equation bodies (e.g., ``x - lo =G= 0``).  The LHS
    condition is *not* lost — it is separately incorporated into the guard /
    condition of the complementarity equation by the callers (lo_guard /
    up_guard generation), ensuring the equation is only active where the
    conditional assignment fired.
    """
    if bound_def.expr is not None:
        expr = bound_def.expr
        if isinstance(expr, LhsConditionalAssign):
            return expr.rhs
        return expr
    return Const(bound_def.value)


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
        # Convert LHS REL RHS to normalized form and then to MCP:
        # For LHS <= RHS: normalized is (LHS - RHS) <= 0, MCP needs (RHS - LHS) >= 0
        # For LHS >= RHS: normalized is (LHS - RHS) >= 0, MCP uses (LHS - RHS) >= 0
        lhs_expr, rhs_expr = eq_def.lhs_rhs

        # Build normalized form: LHS - RHS (handling constant RHS optimization)
        if isinstance(rhs_expr, Const) and rhs_expr.value == 0.0:
            # RHS is 0, so LHS - RHS = LHS
            normalized_expr = lhs_expr
        else:
            # General case: LHS - RHS
            normalized_expr = Binary("-", lhs_expr, rhs_expr)

        if eq_def.relation == Rel.LE:
            # (LHS - RHS) <= 0 becomes (RHS - LHS) >= 0 for MCP
            # i.e., -(LHS - RHS) >= 0
            F_lam = Unary("-", normalized_expr)
            negated = True
        elif eq_def.relation == Rel.GE:
            # (LHS - RHS) >= 0 stays as (LHS - RHS) >= 0 for MCP
            F_lam = normalized_expr
            negated = False
        else:
            raise ValueError(f"Expected inequality (LE or GE), got {eq_def.relation}")

        # Create multiplier name
        lam_name = create_ineq_multiplier_name(eq_name)

        # Create complementarity equation
        # Propagate original condition ($-filter) to preserve domain restrictions
        # like $(ord(i) < ord(j)) from the original inequality
        comp_eq = EquationDef(
            name=f"comp_{eq_name}",
            domain=eq_def.domain,
            condition=eq_def.condition,
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
    #
    # Issue #903/#1008/#1009: For indexed variables, ALWAYS create a single
    # indexed equation — even when per-element overrides exist. Non-uniform
    # bounds are encoded via indexed parameters (e.g., x_lo_param(s)) so
    # that the complementarity equation stays indexed and the MCP pairing
    # has matching dimensionality. This avoids GAMS Error $70.
    #
    # First, identify which variables have non-uniform bounds (per-element overrides)
    # and collect their base bounds
    lo_vars_with_overrides: set[str] = set()
    lo_vars_base_bound: dict[str, float] = {}
    for (var_name, indices), bound_def in partition.bounds_lo.items():
        if indices == ():
            lo_vars_base_bound[var_name] = bound_def.value
        else:
            # Per-element override indicates non-uniform bounds
            lo_vars_with_overrides.add(var_name)

    # Process lower bounds
    lo_vars_seen: set[str] = set()
    for (var_name, _indices), bound_def in partition.bounds_lo.items():
        # Get variable domain from model_ir
        var_def = kkt.model_ir.variables.get(var_name)
        var_domain = var_def.domain if var_def else ()

        # Check if this variable has per-element overrides (non-uniform bounds)
        has_overrides = var_name in lo_vars_with_overrides

        if has_overrides and var_domain:
            # Non-uniform bounds on indexed variable: create a single indexed
            # equation using an indexed parameter for the bound values.
            if var_name in lo_vars_seen:
                continue
            lo_vars_seen.add(var_name)

            # Get base bound value (if any) for elements without explicit overrides
            base_bound = lo_vars_base_bound.get(var_name)

            # Create indexed bound parameter.  When a base bound exists,
            # store only the per-element overrides (sparse) — the emitter
            # will use a domain-wide default assignment plus the overrides.
            param_name = f"{var_name}_lo_param"
            param_data: dict[tuple[str, ...], float] = {}

            all_instances = enumerate_variable_instances(var_def, kkt.model_ir)
            for inst_indices in all_instances:
                if (var_name, inst_indices) in partition.bounds_lo:
                    override_val = partition.bounds_lo[(var_name, inst_indices)].value
                    # Only store if different from base (sparse representation)
                    if base_bound is None or override_val != base_bound:
                        param_data[inst_indices] = override_val

            # Store parameter on KKT system for the emitter
            kkt.bound_params[param_name] = (var_domain, param_data, base_bound)

            # When not all indices are covered (no base bound and only some
            # overrides), add a condition to restrict the equation to covered
            # indices and record a mask set for the emitter.
            lo_condition: Expr | None = None
            if base_bound is None and len(param_data) < len(all_instances):
                mask_name = f"has_{var_name}_lo"
                kkt.bound_param_masks[mask_name] = (var_domain, set(param_data.keys()))
                lo_condition = SetMembershipTest(mask_name, tuple(SymbolRef(d) for d in var_domain))

            # Create indexed multiplier and equation
            piL_name = create_bound_lo_multiplier_name(var_name)
            F_piL = Binary("-", VarRef(var_name, var_domain), ParamRef(param_name, var_domain))
            comp_eq = EquationDef(
                name=f"comp_lo_{var_name}",
                domain=var_domain,
                relation=Rel.GE,
                lhs_rhs=(F_piL, Const(0.0)),
                condition=lo_condition,
            )
            comp_bounds_lo[(var_name, ())] = ComplementarityPair(
                equation=comp_eq, variable=piL_name, variable_indices=var_domain
            )
        elif has_overrides and not var_domain:
            # Non-uniform bounds on scalar variable — shouldn't happen, but handle gracefully
            if var_name in lo_vars_seen:
                continue
            lo_vars_seen.add(var_name)

            base_bound = lo_vars_base_bound.get(var_name)
            bound_value = base_bound if base_bound is not None else bound_def.value
            piL_name = create_bound_lo_multiplier_name(var_name)
            F_piL = Binary("-", VarRef(var_name, ()), Const(bound_value))
            comp_eq = EquationDef(
                name=f"comp_lo_{var_name}",
                domain=(),
                relation=Rel.GE,
                lhs_rhs=(F_piL, Const(0.0)),
            )
            comp_bounds_lo[(var_name, ())] = ComplementarityPair(
                equation=comp_eq, variable=piL_name, variable_indices=()
            )
        else:
            # Uniform bounds: create single indexed equation (or scalar equation)
            # Skip if we already created the equation for this variable
            if var_name in lo_vars_seen:
                continue
            lo_vars_seen.add(var_name)

            # Create indexed multiplier name for uniform bounds
            piL_name = create_bound_lo_multiplier_name(var_name)

            # For expression-based bounds (e.g., x.lo(s) = param(s)), some
            # instances may have -INF values — add a guard condition to skip
            # them and avoid degenerate complementarity equations.
            # Applies to both indexed and scalar variables.
            lo_guard: Expr | None = None
            if bound_def.expr is not None:
                guard_expr = bound_def.expr
                if isinstance(guard_expr, LhsConditionalAssign):
                    # Preserve the assignment condition: only generate
                    # complementarity equations where the conditional
                    # assignment is active and the resulting bound is > -INF.
                    rhs_guard = Binary(">", guard_expr.rhs, Const(float("-inf")))
                    lo_guard = Binary("and", guard_expr.condition, rhs_guard)
                else:
                    lo_guard = Binary(">", guard_expr, Const(float("-inf")))

            if var_domain:
                # Indexed variable: create indexed equation comp_lo_x(i).. x(i) - lo =G= 0
                # Use domain indices, not element values
                F_piL = Binary("-", VarRef(var_name, var_domain), _bound_expr(bound_def))
                comp_eq = EquationDef(
                    name=f"comp_lo_{var_name}",
                    domain=var_domain,
                    relation=Rel.GE,
                    lhs_rhs=(F_piL, Const(0.0)),
                    condition=lo_guard,
                )
                # Key by variable name only (single equation for all instances)
                comp_bounds_lo[(var_name, ())] = ComplementarityPair(
                    equation=comp_eq, variable=piL_name, variable_indices=var_domain
                )
            else:
                # Scalar variable: create scalar equation comp_lo_x.. x - lo =G= 0
                F_piL = Binary("-", VarRef(var_name, ()), _bound_expr(bound_def))
                comp_eq = EquationDef(
                    name=f"comp_lo_{var_name}",
                    domain=(),
                    relation=Rel.GE,
                    lhs_rhs=(F_piL, Const(0.0)),
                    condition=lo_guard,
                )
                comp_bounds_lo[(var_name, ())] = ComplementarityPair(
                    equation=comp_eq, variable=piL_name, variable_indices=()
                )

    # Build upper bound complementarity: (up - x) ≥ 0 ⊥ π^U ≥ 0
    # Note: partition.bounds_up only contains finite bounds (Finding #2)
    #
    # Same strategy as lower bounds: indexed parameters for non-uniform bounds.
    #
    # First, identify which variables have non-uniform bounds (per-element overrides)
    # and collect their base bounds
    up_vars_with_overrides: set[str] = set()
    up_vars_base_bound: dict[str, float] = {}
    for (var_name, indices), bound_def in partition.bounds_up.items():
        if indices == ():
            up_vars_base_bound[var_name] = bound_def.value
        else:
            # Per-element override indicates non-uniform bounds
            up_vars_with_overrides.add(var_name)

    # Process upper bounds
    up_vars_seen: set[str] = set()
    for (var_name, _indices), bound_def in partition.bounds_up.items():
        # Get variable domain from model_ir
        var_def = kkt.model_ir.variables.get(var_name)
        var_domain = var_def.domain if var_def else ()

        # Check if this variable has per-element overrides (non-uniform bounds)
        has_overrides = var_name in up_vars_with_overrides

        if has_overrides and var_domain:
            # Non-uniform bounds on indexed variable: single indexed equation
            # with indexed parameter for bound values (Issue #903/#1008/#1009).
            if var_name in up_vars_seen:
                continue
            up_vars_seen.add(var_name)

            base_bound = up_vars_base_bound.get(var_name)

            param_name = f"{var_name}_up_param"
            up_param_data: dict[tuple[str, ...], float] = {}

            all_instances = enumerate_variable_instances(var_def, kkt.model_ir)
            for inst_indices in all_instances:
                if (var_name, inst_indices) in partition.bounds_up:
                    override_val = partition.bounds_up[(var_name, inst_indices)].value
                    if base_bound is None or override_val != base_bound:
                        up_param_data[inst_indices] = override_val

            kkt.bound_params[param_name] = (var_domain, up_param_data, base_bound)

            # When not all indices are covered, add a condition and mask set
            up_condition: Expr | None = None
            if base_bound is None and len(up_param_data) < len(all_instances):
                mask_name = f"has_{var_name}_up"
                kkt.bound_param_masks[mask_name] = (var_domain, set(up_param_data.keys()))
                up_condition = SetMembershipTest(mask_name, tuple(SymbolRef(d) for d in var_domain))

            piU_name = create_bound_up_multiplier_name(var_name)
            F_piU = Binary("-", ParamRef(param_name, var_domain), VarRef(var_name, var_domain))
            comp_eq = EquationDef(
                name=f"comp_up_{var_name}",
                domain=var_domain,
                relation=Rel.GE,
                lhs_rhs=(F_piU, Const(0.0)),
                condition=up_condition,
            )
            comp_bounds_up[(var_name, ())] = ComplementarityPair(
                equation=comp_eq, variable=piU_name, variable_indices=var_domain
            )
        elif has_overrides and not var_domain:
            # Non-uniform bounds on scalar variable — shouldn't happen, but handle gracefully
            if var_name in up_vars_seen:
                continue
            up_vars_seen.add(var_name)

            base_bound = up_vars_base_bound.get(var_name)
            bound_value = base_bound if base_bound is not None else bound_def.value
            piU_name = create_bound_up_multiplier_name(var_name)
            F_piU = Binary("-", Const(bound_value), VarRef(var_name, ()))
            comp_eq = EquationDef(
                name=f"comp_up_{var_name}",
                domain=(),
                relation=Rel.GE,
                lhs_rhs=(F_piU, Const(0.0)),
            )
            comp_bounds_up[(var_name, ())] = ComplementarityPair(
                equation=comp_eq, variable=piU_name, variable_indices=()
            )
        else:
            # Uniform bounds: create single indexed equation (or scalar equation)
            # Skip if we already created the equation for this variable
            if var_name in up_vars_seen:
                continue
            up_vars_seen.add(var_name)

            # Create indexed multiplier name for uniform bounds
            piU_name = create_bound_up_multiplier_name(var_name)

            # For expression-based bounds (e.g., x.up(s) = param(s)), some
            # instances may have INF values — add a guard condition to skip
            # them and avoid degenerate complementarity equations.
            # Applies to both indexed and scalar variables.
            up_guard: Expr | None = None
            if bound_def.expr is not None:
                guard_expr = bound_def.expr
                if isinstance(guard_expr, LhsConditionalAssign):
                    # Preserve the assignment condition: only generate
                    # complementarity equations where the conditional
                    # assignment is active and the resulting bound is < INF.
                    rhs_guard = Binary("<", guard_expr.rhs, Const(float("inf")))
                    up_guard = Binary("and", guard_expr.condition, rhs_guard)
                else:
                    up_guard = Binary("<", guard_expr, Const(float("inf")))

            if var_domain:
                # Indexed variable: create indexed equation comp_up_x(i).. up - x(i) =G= 0
                F_piU = Binary("-", _bound_expr(bound_def), VarRef(var_name, var_domain))
                comp_eq = EquationDef(
                    name=f"comp_up_{var_name}",
                    domain=var_domain,
                    relation=Rel.GE,
                    lhs_rhs=(F_piU, Const(0.0)),
                    condition=up_guard,
                )
                # Key by variable name only (single equation for all instances)
                comp_bounds_up[(var_name, ())] = ComplementarityPair(
                    equation=comp_eq, variable=piU_name, variable_indices=var_domain
                )
            else:
                # Scalar variable: create scalar equation comp_up_x.. up - x =G= 0
                F_piU = Binary("-", _bound_expr(bound_def), VarRef(var_name, ()))
                comp_eq = EquationDef(
                    name=f"comp_up_{var_name}",
                    domain=(),
                    relation=Rel.GE,
                    lhs_rhs=(F_piU, Const(0.0)),
                    condition=up_guard,
                )
                comp_bounds_up[(var_name, ())] = ComplementarityPair(
                    equation=comp_eq, variable=piU_name, variable_indices=()
                )

    return comp_ineq, comp_bounds_lo, comp_bounds_up, equality_eqs
