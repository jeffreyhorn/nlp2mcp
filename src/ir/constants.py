"""Shared constants for GAMS IR.

This module defines constants used across multiple modules to avoid duplication
and ensure consistency.
"""

# Predefined GAMS constants that are available globally in all GAMS models
# These constants are initialized automatically and should not be emitted or validated
PREDEFINED_GAMS_CONSTANTS = {"pi", "inf", "eps", "na"}

# GAMS reserved constants that must be quoted when used as set elements or indices.
# These identifiers have special meaning in GAMS and would be misinterpreted if unquoted.
# Sprint 19 Day 2: Used by emit layer to quote reserved words in set data and expressions.
GAMS_RESERVED_CONSTANTS = {"inf", "na", "eps", "undf", "yes", "no"}
