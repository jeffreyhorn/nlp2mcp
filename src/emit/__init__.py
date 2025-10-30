"""GAMS code emission module.

This module provides functions for emitting GAMS code from KKT systems.
"""

from src.emit.original_symbols import (
    emit_original_aliases,
    emit_original_parameters,
    emit_original_sets,
)

__all__ = [
    "emit_original_sets",
    "emit_original_aliases",
    "emit_original_parameters",
]
