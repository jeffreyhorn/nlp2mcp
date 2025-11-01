"""Main KKT system assembler.

Orchestrates all KKT component builders to create complete KKT system from NLP:
1. Constraint partitioning (with duplicate exclusion and indexed bounds)
2. Objective variable extraction
3. Multiplier definition creation
4. Stationarity equation building
5. Complementarity pair building

This is the main entry point for NLP → MCP transformation.
"""

from __future__ import annotations

import logging

from src.ad.gradient import GradientVector
from src.ad.jacobian import JacobianStructure
from src.ir.model_ir import ModelIR
from src.kkt.complementarity import build_complementarity_pairs
from src.kkt.kkt_system import KKTSystem, MultiplierDef
from src.kkt.naming import (
    create_bound_lo_multiplier_name,
    create_bound_up_multiplier_name,
    create_eq_multiplier_name,
    create_ineq_multiplier_name,
)
from src.kkt.objective import extract_objective_info
from src.kkt.partition import partition_constraints
from src.kkt.stationarity import build_stationarity_equations

logger = logging.getLogger(__name__)


def assemble_kkt_system(
    model_ir: ModelIR,
    gradient: GradientVector,
    J_eq: JacobianStructure,
    J_ineq: JacobianStructure,
) -> KKTSystem:
    """Assemble complete KKT system from NLP model and derivatives.

    This is the main entry point for KKT system assembly. It orchestrates:
    1. Enhanced constraint partitioning (duplicate exclusion, indexed bounds)
    2. Objective variable extraction
    3. Multiplier generation (only for finite bounds)
    4. Stationarity equations (skipping objective variable)
    5. Complementarity pairs (including objective defining equation)

    Args:
        model_ir: NLP model IR
        gradient: Objective gradient ∇f
        J_eq: Jacobian of equality constraints
        J_ineq: Jacobian of inequality constraints

    Returns:
        Complete KKT system ready for MCP emission

    Example:
        >>> # After parsing, normalizing, and computing derivatives:
        >>> kkt = assemble_kkt_system(model_ir, gradient, J_eq, J_ineq)
        >>> len(kkt.stationarity)  # Number of stationarity equations
        >>> len(kkt.complementarity_ineq)  # Number of inequality complementarities
        >>> len(kkt.multipliers_bounds_lo)  # Number of lower bound multipliers
    """
    # Step 1: Enhanced partition with duplicate exclusion and indexed bounds
    logger.info("Partitioning constraints...")
    partition = partition_constraints(model_ir)

    # Log excluded duplicates (Finding #1)
    if partition.duplicate_excluded:
        for eq_name in partition.duplicate_excluded:
            logger.warning(f"Excluding duplicate bound constraint: {eq_name}")

    # Log skipped infinite bounds (including indexed - Finding #2)
    if partition.skipped_infinite:
        for var_name, indices, bound_type in partition.skipped_infinite:
            idx_str = f"({','.join(indices)})" if indices else ""
            logger.info(f"Skipping infinite {bound_type} bound on {var_name}{idx_str}")

    logger.info(
        f"Partitioned: {len(partition.equalities)} equalities, "
        f"{len(partition.inequalities)} inequalities, "
        f"{len(partition.bounds_lo)} lower bounds, "
        f"{len(partition.bounds_up)} upper bounds"
    )

    # Step 2: Extract objective info
    logger.info("Extracting objective information...")
    obj_info = extract_objective_info(model_ir)
    logger.info(
        f"Objective variable: {obj_info.objvar}, defining equation: {obj_info.defining_equation}"
    )

    # Step 3: Create multiplier definitions
    logger.info("Creating multiplier definitions...")
    multipliers_eq = _create_eq_multipliers(partition.equalities, model_ir)
    multipliers_ineq = _create_ineq_multipliers(partition.inequalities, model_ir)
    multipliers_bounds_lo = _create_bound_lo_multipliers(partition.bounds_lo)
    multipliers_bounds_up = _create_bound_up_multipliers(partition.bounds_up)

    logger.info(
        f"Created multipliers: {len(multipliers_eq)} equality, "
        f"{len(multipliers_ineq)} inequality, "
        f"{len(multipliers_bounds_lo)} lower bound, "
        f"{len(multipliers_bounds_up)} upper bound"
    )

    # Step 4: Initialize KKT system
    kkt = KKTSystem(
        model_ir=model_ir,
        gradient=gradient,
        J_eq=J_eq,
        J_ineq=J_ineq,
        multipliers_eq=multipliers_eq,
        multipliers_ineq=multipliers_ineq,
        multipliers_bounds_lo=multipliers_bounds_lo,
        multipliers_bounds_up=multipliers_bounds_up,
        skipped_infinite_bounds=partition.skipped_infinite,
        duplicate_bounds_excluded=partition.duplicate_excluded,
    )

    # Step 5: Build stationarity equations (skips objvar, handles indexed bounds)
    logger.info("Building stationarity equations...")
    kkt.stationarity = build_stationarity_equations(kkt)
    logger.info(f"Built {len(kkt.stationarity)} stationarity equations")

    # Step 6: Build complementarity pairs (includes obj defining eq, indexed bounds)
    logger.info("Building complementarity pairs...")
    (
        kkt.complementarity_ineq,
        kkt.complementarity_bounds_lo,
        kkt.complementarity_bounds_up,
        equality_eqs,
    ) = build_complementarity_pairs(kkt)

    logger.info(
        f"Built complementarity pairs: {len(kkt.complementarity_ineq)} inequality, "
        f"{len(kkt.complementarity_bounds_lo)} lower bound, "
        f"{len(kkt.complementarity_bounds_up)} upper bound, "
        f"{len(equality_eqs)} equality equations"
    )

    # Store equality equations (these are h(x) = 0 without complementarity)
    # Note: We could store these in a separate field if needed
    # For now, they're handled by the complementarity builder

    logger.info("KKT system assembly complete")
    return kkt


def _create_eq_multipliers(equalities: list[str], model_ir: ModelIR) -> dict[str, MultiplierDef]:
    """Create multiplier definitions for equality constraints.

    Handles both user-defined equations and normalized bounds (e.g., fixed variables).
    """
    multipliers = {}
    for eq_name in equalities:
        # Check both equations dict and normalized_bounds dict
        # Fixed variables (.fx) create equalities stored in normalized_bounds
        if eq_name in model_ir.equations:
            eq_def = model_ir.equations[eq_name]
            domain = eq_def.domain
        elif eq_name in model_ir.normalized_bounds:
            norm_eq = model_ir.normalized_bounds[eq_name]
            domain = norm_eq.domain_sets
        else:
            continue

        mult_name = create_eq_multiplier_name(eq_name, domain)
        multipliers[mult_name] = MultiplierDef(
            name=mult_name,
            domain=domain,
            kind="eq",
            associated_constraint=eq_name,
        )
    return multipliers


def _create_ineq_multipliers(
    inequalities: list[str], model_ir: ModelIR
) -> dict[str, MultiplierDef]:
    """Create multiplier definitions for inequality constraints."""
    multipliers = {}
    for eq_name in inequalities:
        if eq_name not in model_ir.equations:
            continue
        eq_def = model_ir.equations[eq_name]
        mult_name = create_ineq_multiplier_name(eq_name, eq_def.domain)
        multipliers[mult_name] = MultiplierDef(
            name=mult_name,
            domain=eq_def.domain,
            kind="ineq",
            associated_constraint=eq_name,
        )
    return multipliers


def _create_bound_lo_multipliers(bounds_lo: dict) -> dict[tuple, MultiplierDef]:
    """Create multiplier definitions for lower bounds (indexed support)."""
    multipliers = {}
    for (var_name, indices), bound_def in bounds_lo.items():
        mult_name = create_bound_lo_multiplier_name(var_name, indices)
        multipliers[(var_name, indices)] = MultiplierDef(
            name=mult_name,
            domain=bound_def.domain,
            kind="bound_lo",
            associated_constraint=var_name,
        )
    return multipliers


def _create_bound_up_multipliers(bounds_up: dict) -> dict[tuple, MultiplierDef]:
    """Create multiplier definitions for upper bounds (indexed support)."""
    multipliers = {}
    for (var_name, indices), bound_def in bounds_up.items():
        mult_name = create_bound_up_multiplier_name(var_name, indices)
        multipliers[(var_name, indices)] = MultiplierDef(
            name=mult_name,
            domain=bound_def.domain,
            kind="bound_up",
            associated_constraint=var_name,
        )
    return multipliers
