"""KKT system assembly for NLP to MCP transformation."""

from .assemble import assemble_kkt_system
from .complementarity import build_complementarity_pairs
from .kkt_system import ComplementarityPair, KKTSystem, MultiplierDef
from .naming import (
    create_bound_lo_multiplier_name,
    create_bound_up_multiplier_name,
    create_eq_multiplier_name,
    create_ineq_multiplier_name,
)
from .objective import ObjectiveInfo, extract_objective_info
from .partition import BoundDef, PartitionResult, partition_constraints
from .stationarity import build_stationarity_equations

__all__ = [
    # Data structures
    "KKTSystem",
    "MultiplierDef",
    "ComplementarityPair",
    "PartitionResult",
    "BoundDef",
    "ObjectiveInfo",
    # Functions
    "assemble_kkt_system",
    "partition_constraints",
    "extract_objective_info",
    "build_stationarity_equations",
    "build_complementarity_pairs",
    "create_eq_multiplier_name",
    "create_ineq_multiplier_name",
    "create_bound_lo_multiplier_name",
    "create_bound_up_multiplier_name",
]
