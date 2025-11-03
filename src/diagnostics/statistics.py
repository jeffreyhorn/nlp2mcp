"""Model statistics computation for NLP to MCP transformation.

This module provides functionality to compute and report statistics about the
KKT system, including equation counts, variable counts, and nonzero structure.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.kkt.kkt_system import KKTSystem


@dataclass
class ModelStatistics:
    """Statistics about a KKT system.

    Provides counts of equations, variables, and nonzeros, broken down by type.

    Attributes:
        num_equations: Total number of equations in KKT system
        num_variables: Total number of variables (primal + multipliers)
        num_nonzeros: Total number of nonzero Jacobian entries
        num_stationarity: Number of stationarity equations
        num_complementarity_ineq: Number of inequality complementarity pairs
        num_complementarity_bounds_lo: Number of lower bound complementarity pairs
        num_complementarity_bounds_up: Number of upper bound complementarity pairs
        num_primal_vars: Number of primal variables
        num_multipliers_eq: Number of equality multipliers
        num_multipliers_ineq: Number of inequality multipliers
        num_multipliers_bounds_lo: Number of lower bound multipliers
        num_multipliers_bounds_up: Number of upper bound multipliers
        jacobian_density: Fraction of nonzeros (0.0 to 1.0)
    """

    num_equations: int
    num_variables: int
    num_nonzeros: int
    num_stationarity: int
    num_complementarity_ineq: int
    num_complementarity_bounds_lo: int
    num_complementarity_bounds_up: int
    num_primal_vars: int
    num_multipliers_eq: int
    num_multipliers_ineq: int
    num_multipliers_bounds_lo: int
    num_multipliers_bounds_up: int
    jacobian_density: float

    def format_report(self) -> str:
        """Format statistics as a human-readable report.

        Returns:
            Multiline string with formatted statistics
        """
        lines = [
            "=" * 70,
            "MODEL STATISTICS",
            "=" * 70,
            "",
            "EQUATION BREAKDOWN:",
            f"  Stationarity equations:          {self.num_stationarity:6d}",
            f"  Inequality complementarity:      {self.num_complementarity_ineq:6d}",
            f"  Lower bound complementarity:     {self.num_complementarity_bounds_lo:6d}",
            f"  Upper bound complementarity:     {self.num_complementarity_bounds_up:6d}",
            f"  {'─' * 45}",
            f"  Total equations:                 {self.num_equations:6d}",
            "",
            "VARIABLE BREAKDOWN:",
            f"  Primal variables:                {self.num_primal_vars:6d}",
            f"  Equality multipliers (nu):       {self.num_multipliers_eq:6d}",
            f"  Inequality multipliers (lambda): {self.num_multipliers_ineq:6d}",
            f"  Lower bound multipliers (pi_L):  {self.num_multipliers_bounds_lo:6d}",
            f"  Upper bound multipliers (pi_U):  {self.num_multipliers_bounds_up:6d}",
            f"  {'─' * 45}",
            f"  Total variables:                 {self.num_variables:6d}",
            "",
            "JACOBIAN STRUCTURE:",
            f"  Nonzero entries:                 {self.num_nonzeros:6d}",
            f"  Jacobian density:                {self.jacobian_density:6.2%}",
            f"  Average nonzeros per equation:   {self.num_nonzeros / max(1, self.num_equations):6.1f}",
            "",
            "=" * 70,
        ]
        return "\n".join(lines)


def compute_model_statistics(kkt: KKTSystem) -> ModelStatistics:
    """Compute statistics for a KKT system.

    Args:
        kkt: KKT system to analyze

    Returns:
        ModelStatistics object with all computed statistics
    """
    # Count equations by type
    num_stationarity = len(kkt.stationarity)
    num_complementarity_ineq = len(kkt.complementarity_ineq)
    num_complementarity_bounds_lo = len(kkt.complementarity_bounds_lo)
    num_complementarity_bounds_up = len(kkt.complementarity_bounds_up)

    num_equations = (
        num_stationarity
        + num_complementarity_ineq
        + num_complementarity_bounds_lo
        + num_complementarity_bounds_up
    )

    # Count variables by type
    num_primal_vars = kkt.gradient.num_cols
    num_multipliers_eq = len(kkt.multipliers_eq)
    num_multipliers_ineq = len(kkt.multipliers_ineq)
    num_multipliers_bounds_lo = len(kkt.multipliers_bounds_lo)
    num_multipliers_bounds_up = len(kkt.multipliers_bounds_up)

    num_variables = (
        num_primal_vars
        + num_multipliers_eq
        + num_multipliers_ineq
        + num_multipliers_bounds_lo
        + num_multipliers_bounds_up
    )

    # Count nonzeros in Jacobian
    # Stationarity equations have gradient + Jacobian transpose contributions
    num_nonzeros_stationarity = len(kkt.gradient.get_all_derivatives())

    # Add Jacobian transpose contributions (J_eq^T and J_ineq^T)
    num_nonzeros_stationarity += len(kkt.J_eq.get_nonzero_entries())
    num_nonzeros_stationarity += len(kkt.J_ineq.get_nonzero_entries())

    # Complementarity equations are simpler (constraint equation + multiplier term)
    # Each inequality complementarity: constraint equation (already counted in stationarity)
    # Each bound complementarity: simple bound expression (1-2 nonzeros each)
    num_nonzeros_complementarity = (
        num_complementarity_bounds_lo * 2  # Lower bounds: x - lo
        + num_complementarity_bounds_up * 2  # Upper bounds: up - x
    )

    num_nonzeros = num_nonzeros_stationarity + num_nonzeros_complementarity

    # Compute Jacobian density
    total_entries = num_equations * num_variables
    jacobian_density = num_nonzeros / max(1, total_entries) if total_entries > 0 else 0.0

    return ModelStatistics(
        num_equations=num_equations,
        num_variables=num_variables,
        num_nonzeros=num_nonzeros,
        num_stationarity=num_stationarity,
        num_complementarity_ineq=num_complementarity_ineq,
        num_complementarity_bounds_lo=num_complementarity_bounds_lo,
        num_complementarity_bounds_up=num_complementarity_bounds_up,
        num_primal_vars=num_primal_vars,
        num_multipliers_eq=num_multipliers_eq,
        num_multipliers_ineq=num_multipliers_ineq,
        num_multipliers_bounds_lo=num_multipliers_bounds_lo,
        num_multipliers_bounds_up=num_multipliers_bounds_up,
        jacobian_density=jacobian_density,
    )
