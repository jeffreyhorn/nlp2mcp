"""Shared constants for GAMS IR.

This module defines constants used across multiple modules to avoid duplication
and ensure consistency.
"""

# Predefined GAMS constants that are available globally in all GAMS models
# These constants are initialized automatically and should not be emitted or validated
PREDEFINED_GAMS_CONSTANTS = {"pi", "inf", "eps", "na"}
