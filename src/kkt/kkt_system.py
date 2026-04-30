"""KKT system data structures for NLP to MCP transformation.

This module defines the core data structures for representing a complete KKT
(Karush-Kuhn-Tucker) system derived from a nonlinear programming problem.

The KKT system includes:
- Stationarity equations: ∇f + J_g^T λ + J_h^T ν - π^L + π^U = 0
- Complementarity conditions: g(x) ⊥ λ, h(x) = 0 (free ν), bounds ⊥ π
- Multiplier variables for each constraint and bound
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from src.ad.gradient import GradientVector
from src.ad.jacobian import JacobianStructure
from src.ir.ast import Expr
from src.ir.model_ir import ModelIR
from src.ir.symbols import EquationDef


@dataclass
class MultiplierDef:
    """Definition of a Lagrange multiplier variable.

    Multipliers are dual variables associated with constraints:
    - ν (nu): Free multipliers for equality constraints h(x) = 0
    - λ (lambda): Positive multipliers for inequality constraints g(x) ≤ 0
    - π^L (pi_L): Positive multipliers for lower bounds x ≥ lo
    - π^U (pi_U): Positive multipliers for upper bounds x ≤ up

    Attributes:
        name: GAMS variable name (e.g., "nu_balance", "lam_capacity")
        domain: Index sets for indexed multipliers (e.g., ("i", "j"))
        kind: Type of multiplier (eq/ineq/bound_lo/bound_up)
        associated_constraint: Name of the constraint this multiplier is for
    """

    name: str
    domain: tuple[str, ...] = ()
    kind: Literal["eq", "ineq", "bound_lo", "bound_up"] = "eq"
    associated_constraint: str = ""


@dataclass
class ComplementarityPair:
    """A complementarity condition F(x, λ, ...) ⊥ variable.

    In MCP (Mixed Complementarity Problem) format, complementarity means:
    - F ≥ 0, variable ≥ 0, F · variable = 0

    In GAMS MCP syntax:
    - equation_name.variable_name

    Attributes:
        equation: The equation F(x, λ, ...)
        variable: Name of the complementary variable (e.g., "lam_g1")
        variable_indices: Index tuple for indexed variables
        negated: Whether the constraint was negated (g(x) <= 0 becomes -g(x) >= 0)
        is_max_constraint: Whether this is from max reformulation (arg - aux_max <= 0)
    """

    equation: EquationDef
    variable: str
    variable_indices: tuple[str, ...] = ()
    negated: bool = False
    is_max_constraint: bool = False


@dataclass
class KKTSystem:
    """Complete KKT system for an NLP problem.

    Represents the first-order optimality conditions (KKT conditions) for:
        minimize f(x)
        subject to h(x) = 0      (equalities)
                   g(x) ≤ 0      (inequalities)
                   lo ≤ x ≤ up   (bounds)

    KKT conditions are:
    1. Stationarity: ∇f + J_h^T ν + J_g^T λ - π^L + π^U = 0
    2. Primal feasibility: h(x) = 0, g(x) ≤ 0, lo ≤ x ≤ up
    3. Dual feasibility: λ ≥ 0, π^L ≥ 0, π^U ≥ 0
    4. Complementarity: g(x) · λ = 0, (x - lo) · π^L = 0, (up - x) · π^U = 0

    This structure stores all components needed to emit a GAMS MCP model.

    Attributes:
        model_ir: Original NLP model
        gradient: ∇f (objective gradient)
        J_eq: Jacobian of equality constraints
        J_ineq: Jacobian of inequality constraints
        multipliers_eq: ν multipliers for equalities (free variables)
        multipliers_ineq: λ multipliers for inequalities (positive variables)
        multipliers_bounds_lo: π^L multipliers for lower bounds (positive)
        multipliers_bounds_up: π^U multipliers for upper bounds (positive)
        stationarity: Stationarity equations (one per variable instance)
        complementarity_ineq: Complementarity pairs for inequalities
        complementarity_bounds_lo: Complementarity pairs for lower bounds
        complementarity_bounds_up: Complementarity pairs for upper bounds
        skipped_infinite_bounds: List of infinite bounds that were skipped
        duplicate_bounds_excluded: List of inequality names excluded as duplicates
    """

    # Primal problem
    model_ir: ModelIR

    # Derivatives
    gradient: GradientVector
    J_eq: JacobianStructure
    J_ineq: JacobianStructure

    # Multipliers (filtered for infinite bounds, including indexed)
    multipliers_eq: dict[str, MultiplierDef] = field(default_factory=dict)
    multipliers_ineq: dict[str, MultiplierDef] = field(default_factory=dict)
    multipliers_bounds_lo: dict[tuple, MultiplierDef] = field(default_factory=dict)
    multipliers_bounds_up: dict[tuple, MultiplierDef] = field(default_factory=dict)

    # KKT equations
    stationarity: dict[str, EquationDef] = field(default_factory=dict)
    complementarity_ineq: dict[str, ComplementarityPair] = field(default_factory=dict)
    complementarity_bounds_lo: dict[tuple, ComplementarityPair] = field(default_factory=dict)
    complementarity_bounds_up: dict[tuple, ComplementarityPair] = field(default_factory=dict)

    # Metadata
    skipped_infinite_bounds: list[tuple[str, tuple, str]] = field(default_factory=list)
    duplicate_bounds_excluded: list[str] = field(default_factory=list)

    # Issue #724: Variable access conditions for stationarity equations.
    # Maps var_name -> condition Expr for variables whose stationarity equation
    # has a dollar condition (variable is only active under that condition).
    # Used by the emitter to generate .fx statements for excluded instances.
    stationarity_conditions: dict[str, Expr] = field(default_factory=dict)

    # Issue #1192: Bounds-collapse guard conditions for variables with
    # parameter-dependent .lo/.up bounds. Maps var_name -> condition Expr
    # of the form `var.up(d) - var.lo(d) > eps`. Stored separately from
    # `stationarity_conditions` so the lead/lag fix-inactive path
    # (section 1b in emit_gams) does NOT fire for variables whose only
    # condition is a runtime bounds-collapse guard. The body of the
    # stationarity equation IS already wrapped in this condition by the
    # builder; the emitter only needs to emit the corresponding
    # `.fx(d)$(not (cond)) = ...` lines.
    stationarity_bounds_conditions: dict[str, Expr] = field(default_factory=dict)

    # Issue #1112: Dollar conditions extracted from gradient expressions.
    # Maps var_name -> condition Expr for variables whose objective gradient
    # was computed from a conditioned sum. Used by the stationarity builder
    # to add equation-level guards.
    gradient_conditions: dict[str, Expr] = field(default_factory=dict)

    # Issue #742: Variables actually referenced in equations/objective.
    # Populated by build_stationarity_equations() so the emitter can exclude
    # unreferenced variables (e.g., dumshr, dumtg) from declarations and MCP pairs.
    # None means no filtering was performed (backwards compatible).
    referenced_variables: set[str] | None = None

    # Multiplier names that actually appear in simplified stationarity equations.
    # After simplification, some multipliers may vanish (e.g., 0 * nu_foo → 0).
    # Populated by build_stationarity_equations() so the emitter can exclude
    # unreferenced multipliers from declarations and complementarity pairs.
    # None means no filtering was performed (backwards compatible).
    referenced_multipliers: set[str] | None = None

    # Issue #826: Variables whose stationarity equations are entirely empty
    # (LHS == Const(0.0) after simplification). These variables are fixed to 0
    # in the emitted MCP model (via .fx statements). Their stationarity equations
    # are kept for complementarity pairing. Populated by build_stationarity_equations().
    empty_stationarity_vars: set[str] = field(default_factory=set)

    # Issue #903/#1008/#1009: Indexed bound parameters for non-uniform bounds.
    # When a variable has per-element bounds (e.g., x.lo("stage-1") = 125),
    # the complementarity builder creates indexed parameters to hold the
    # per-element values so that complementarity and stationarity equations
    # stay indexed (avoiding scalar-indexed MCP pairing mismatch / GAMS $70).
    # Maps param_name -> (domain, overrides_dict, base_value).
    #   overrides_dict: per-element values that differ from the base
    #   base_value: uniform default (None if no finite base bound)
    # When base_value is set, the emitter uses a domain-wide assignment
    # plus sparse overrides instead of enumerating all instances.
    bound_params: dict[str, tuple[tuple[str, ...], dict[tuple[str, ...], float], float | None]] = (
        field(default_factory=dict)
    )

    # Mask sets for partial bound coverage.  When a variable has per-element
    # bound overrides but no finite base bound, only a subset of indices have
    # finite bounds.  The complementarity equation is conditioned on a mask set
    # so that uncovered indices remain truly unbounded.
    # Maps mask_set_name -> (domain, set of covered index tuples).
    bound_param_masks: dict[str, tuple[tuple[str, ...], set[tuple[str, ...]]]] = field(
        default_factory=dict
    )

    # Issue #1164/#1175: Parameter and variable domain widenings.
    # When a parameter/variable declared over a subset (e.g., alp(t) where t⊂i)
    # is used in a stationarity equation over the superset (stat_e(i)),
    # the emitter must declare the symbol over the superset to avoid $171.
    # Maps symbol_name -> widened_domain.
    param_domain_widenings: dict[str, tuple[str, ...]] = field(default_factory=dict)
    var_domain_widenings: dict[str, tuple[str, ...]] = field(default_factory=dict)

    # Issue #1053: Multiplier domain widenings.
    # When a multiplier's domain is widened from a subset to its parent set
    # (e.g., nu_e2 from (j) to (i) because j⊂i), the emitter must fix
    # instances outside the original subset to 0.
    # Maps mult_name -> (original_domain, widened_domain).
    multiplier_domain_widenings: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = field(
        default_factory=dict
    )

    # Scaling factors (optional, computed when --scale is used)
    scaling_row_factors: list[float] | None = None
    scaling_col_factors: list[float] | None = None
    scaling_mode: str = "none"  # none | auto | byvar

    def subset_filter_for_multiplier(self, mult_name: str, indices: tuple) -> Expr | None:
        """Issue #1245: Return the source equation's body-domain subset
        filter for a multiplier whose domain was widened from a subset
        to a parent set (per `multiplier_domain_widenings`).

        For a multiplier `nu_esupply(i)` widened from `(it,)` to `(i,)`,
        with the equation iterating over index `i`, this returns
        `SetMembershipTest("it", (SymbolRef("i"),))` — i.e., the GAMS
        condition `it(i)` that filters the term to traded-only instances.

        Returns None if the multiplier is not parent-widened (no entry
        in `multiplier_domain_widenings`, or the widening is a no-op).

        For multi-dim multipliers where multiple positions are widened,
        returns the AND of per-position membership tests. Positions
        whose subset and parent match are skipped.
        """
        from src.ir.ast import Binary, IndexOffset, SetMembershipTest, SymbolRef

        widening = self.multiplier_domain_widenings.get(mult_name)
        if widening is None:
            return None
        orig_dom, widened_dom = widening
        if orig_dom == widened_dom:
            return None
        if len(orig_dom) != len(widened_dom) or len(indices) != len(widened_dom):
            return None
        clauses: list[Expr] = []
        for orig_set, wide_set, idx_at_pos in zip(orig_dom, widened_dom, indices, strict=True):
            if orig_set.lower() == wide_set.lower():
                continue
            # Build the membership test using the multiplier's actual
            # index argument at that position (e.g., `i` for `nu_X(i)`,
            # or `IndexOffset("i", 1, ...)` for lead/lag references).
            idx_expr: Expr
            if isinstance(idx_at_pos, str):
                idx_expr = SymbolRef(idx_at_pos)
            elif isinstance(idx_at_pos, IndexOffset):
                # Lead/lag indices are valid in SetMembershipTest's
                # `Expr`-typed indices tuple; preserve the offset so the
                # emitted GAMS condition is e.g. `it(i+1)`.
                idx_expr = idx_at_pos
            elif isinstance(idx_at_pos, Expr):
                # Any other Expr subtype (SubsetIndex, etc.) is also
                # valid — let it through.
                idx_expr = idx_at_pos
            else:
                # Unknown shape; skip JUST this position rather than
                # dropping the whole guard. Other positions may still
                # be guard-able.
                continue
            clauses.append(SetMembershipTest(orig_set, (idx_expr,)))
        if not clauses:
            return None
        guard = clauses[0]
        for clause in clauses[1:]:
            guard = Binary("and", guard, clause)
        return guard
