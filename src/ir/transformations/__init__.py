"""Expression transformation passes for the simplification pipeline.

This module contains transformation passes that simplify GAMS expressions
while preserving semantic correctness.
"""

from src.ir.transformations.associativity import normalize_associativity
from src.ir.transformations.division import simplify_division
from src.ir.transformations.factoring import extract_common_factors, multi_term_factoring
from src.ir.transformations.fractions import combine_fractions
from src.ir.transformations.nested_operations import simplify_nested_products
from src.ir.transformations.power_rules import consolidate_powers
from src.ir.transformations.utils import flatten_addition, flatten_multiplication

__all__ = [
    "extract_common_factors",
    "multi_term_factoring",
    "combine_fractions",
    "normalize_associativity",
    "simplify_division",
    "simplify_nested_products",
    "consolidate_powers",
    "flatten_addition",
    "flatten_multiplication",
]
