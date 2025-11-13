"""Convexity detection and analysis for optimization models."""

from .pattern_matcher import ConvexityWarning, PatternMatcher
from .patterns import (
    BilinearTermPattern,
    NonlinearEqualityPattern,
    OddPowerPattern,
    QuotientPattern,
    TrigonometricPattern,
)

__all__ = [
    "ConvexityWarning",
    "PatternMatcher",
    "NonlinearEqualityPattern",
    "TrigonometricPattern",
    "BilinearTermPattern",
    "QuotientPattern",
    "OddPowerPattern",
]
