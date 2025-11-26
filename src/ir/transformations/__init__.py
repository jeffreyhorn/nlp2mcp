"""Expression transformation passes for the simplification pipeline.

This module contains transformation passes that simplify GAMS expressions
while preserving semantic correctness.
"""

from src.ir.transformations.associativity import normalize_associativity
from src.ir.transformations.factoring import extract_common_factors
from src.ir.transformations.fractions import combine_fractions

__all__ = ["extract_common_factors", "combine_fractions", "normalize_associativity"]
