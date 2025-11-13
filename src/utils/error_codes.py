"""
Central error code registry for nlp2mcp.

This module provides a centralized registry of all error codes, warnings,
and info messages used throughout nlp2mcp, along with their documentation
links and metadata.

Error Code Scheme:
-----------------
- Format: [Level][Category][Number]
  - Level: E (Error), W (Warning), I (Info)
  - Category: 0xx-9xx grouping
  - Number: Sequential within category

Categories:
-----------
- 0xx: Syntax errors (parsing failures)
- 1xx: Validation errors (semantic issues)
- 2xx: Solver errors (PATH/CPLEX issues)
- 3xx: Convexity warnings
- 9xx: Internal errors (bugs in nlp2mcp)

Sprint 6 Convexity Warnings:
----------------------------
- W301: Nonlinear equality (potentially nonconvex)
- W302: Trigonometric function (potentially nonconvex)
- W303: Bilinear term (potentially nonconvex)
- W304: Division/quotient (potentially nonconvex)
- W305: Odd-power polynomial (potentially nonconvex)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ErrorInfo:
    """
    Metadata for an error/warning/info code.

    Attributes:
        code: Error code (e.g., "W301")
        level: Severity level ("Error", "Warning", "Info")
        title: Short title for the error
        doc_anchor: Anchor link for documentation (e.g., "w301-nonlinear-equality")
    """

    code: str
    level: str
    title: str
    doc_anchor: str

    def doc_url(self) -> str:
        """
        Generate documentation URL for this error.

        Returns:
            Full URL to error documentation with anchor
        """
        base_url = (
            "https://github.com/jeffreyhorn/nlp2mcp/blob/main/docs/errors/convexity_warnings.md"
        )
        return f"{base_url}#{self.doc_anchor}"


# Error Registry
# ==============
# Central registry of all error codes used in nlp2mcp.
# Add new codes here to ensure consistent documentation links.

ERROR_REGISTRY: dict[str, ErrorInfo] = {
    # Convexity Warnings (3xx)
    "W301": ErrorInfo(
        code="W301",
        level="Warning",
        title="Nonlinear equality may be nonconvex",
        doc_anchor="w301-nonlinear-equality",
    ),
    "W302": ErrorInfo(
        code="W302",
        level="Warning",
        title="Trigonometric function may be nonconvex",
        doc_anchor="w302-trigonometric-function",
    ),
    "W303": ErrorInfo(
        code="W303",
        level="Warning",
        title="Bilinear term may be nonconvex",
        doc_anchor="w303-bilinear-term",
    ),
    "W304": ErrorInfo(
        code="W304",
        level="Warning",
        title="Division by variable may be nonconvex",
        doc_anchor="w304-variable-quotient",
    ),
    "W305": ErrorInfo(
        code="W305",
        level="Warning",
        title="Odd power may be nonconvex",
        doc_anchor="w305-odd-power",
    ),
}


def get_error_info(code: str) -> ErrorInfo | None:
    """
    Get error metadata by code.

    Args:
        code: Error code (e.g., "W301")

    Returns:
        ErrorInfo if code exists, None otherwise
    """
    return ERROR_REGISTRY.get(code)
