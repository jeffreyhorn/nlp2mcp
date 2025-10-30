"""GAMS code emission module.

This module provides functions for emitting GAMS code from KKT systems.
"""

from src.emit.emit_gams import emit_gams_mcp
from src.emit.equations import emit_equation_def, emit_equation_definitions
from src.emit.expr_to_gams import expr_to_gams
from src.emit.model import emit_model_mcp, emit_solve
from src.emit.original_symbols import (
    emit_original_aliases,
    emit_original_parameters,
    emit_original_sets,
)

__all__ = [
    "emit_original_sets",
    "emit_original_aliases",
    "emit_original_parameters",
    "expr_to_gams",
    "emit_equation_def",
    "emit_equation_definitions",
    "emit_model_mcp",
    "emit_solve",
    "emit_gams_mcp",
]
