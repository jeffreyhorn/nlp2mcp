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

    # Scaling factors (optional, computed when --scale is used)
    scaling_row_factors: list[float] | None = None
    scaling_col_factors: list[float] | None = None
    scaling_mode: str = "none"  # none | auto | byvar
