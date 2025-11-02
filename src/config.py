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
    """

    smooth_abs: bool = False
    smooth_abs_epsilon: float = 1e-6
    scale: str = "none"

    def __post_init__(self):
        """Validate configuration values."""
        if self.smooth_abs_epsilon <= 0:
            raise ValueError(f"smooth_abs_epsilon must be positive, got {self.smooth_abs_epsilon}")

        if self.scale not in ("none", "auto", "byvar"):
            raise ValueError(f"scale must be 'none', 'auto', or 'byvar', got '{self.scale}'")
