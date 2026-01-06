"""Configuration for nlp2mcp tool.

This module defines configuration options that affect various stages of the
NLP to MCP conversion pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Config:
    """Configuration options for nlp2mcp conversion.

    Attributes:
        smooth_abs: Enable smooth approximation for abs() function
        smooth_abs_epsilon: Epsilon parameter for abs() smoothing (default: 1e-6)
        scale: Scaling mode - "none", "auto" (Curtis-Reid), or "byvar" (default: "none")
        simplification: Expression simplification mode - "none", "basic", "advanced", or "aggressive" (default: "advanced")
            - "none": No simplification applied
            - "basic": Basic rules (constant folding, zero elimination, identity)
            - "advanced": Basic rules + term collection (1+x+1→x+2, x+y+x+y→2*x+2*y)
            - "aggressive": All advanced + 10 algebraic transformations + CSE (Sprint 11)
                * T1: Factoring (common factors, fractions)
                * T2: Division simplification (division by constants, fraction combining)
                * T3: Associativity normalization
                * T4: Power/logarithm/trig rules
                * T5: Common Subexpression Elimination (nested, multiplicative, aliasing)
        model_ir: Optional ModelIR for set membership lookups during differentiation.
            When set, enables proper handling of arbitrary set element labels
            (e.g., "1", "2" for set "h") instead of relying on naming heuristics.
    """

    smooth_abs: bool = False
    smooth_abs_epsilon: float = 1e-6
    scale: str = "none"
    simplification: str = "advanced"
    model_ir: Any = field(default=None, repr=False)  # Type is ModelIR but use Any to avoid cycles

    def __post_init__(self):
        """Validate configuration values."""
        if self.smooth_abs_epsilon <= 0:
            raise ValueError(f"smooth_abs_epsilon must be positive, got {self.smooth_abs_epsilon}")

        if self.scale not in ("none", "auto", "byvar"):
            raise ValueError(f"scale must be 'none', 'auto', or 'byvar', got '{self.scale}'")

        if self.simplification not in ("none", "basic", "advanced", "aggressive"):
            raise ValueError(
                f"simplification must be 'none', 'basic', 'advanced', or 'aggressive', got '{self.simplification}'"
            )
