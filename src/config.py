"""Configuration for nlp2mcp tool.

This module defines configuration options that affect various stages of the
NLP to MCP conversion pipeline.
"""

from dataclasses import dataclass


@dataclass
class Config:
    """Configuration options for nlp2mcp conversion.

    Attributes:
        smooth_abs: Enable smooth approximation for abs() function
        smooth_abs_epsilon: Epsilon parameter for abs() smoothing (default: 1e-6)
        scale: Scaling mode - "none", "auto" (Curtis-Reid), or "byvar" (default: "none")
        simplification: Expression simplification mode - "none", "basic", or "advanced" (default: "advanced")
            - "none": No simplification applied
            - "basic": Basic rules (constant folding, zero elimination, identity)
            - "advanced": Basic rules + term collection (1+x+1→x+2, x+y+x+y→2*x+2*y)
    """

    smooth_abs: bool = False
    smooth_abs_epsilon: float = 1e-6
    scale: str = "none"
    simplification: str = "advanced"

    def __post_init__(self):
        """Validate configuration values."""
        if self.smooth_abs_epsilon <= 0:
            raise ValueError(f"smooth_abs_epsilon must be positive, got {self.smooth_abs_epsilon}")

        if self.scale not in ("none", "auto", "byvar"):
            raise ValueError(f"scale must be 'none', 'auto', or 'byvar', got '{self.scale}'")

        if self.simplification not in ("none", "basic", "advanced"):
            raise ValueError(
                f"simplification must be 'none', 'basic', or 'advanced', got '{self.simplification}'"
            )
