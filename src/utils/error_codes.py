"""Error code registry for nlp2mcp.

Provides centralized error code management with metadata and documentation links.
Implements the error code scheme from docs/research/doc_link_strategy.md.

Error Code Format: {Level}{Category}{Number}
- Levels: E (Error), W (Warning), I (Info)
- Categories: 0xx (Syntax), 1xx (Validation), 2xx (Solver), 3xx (Convexity), 9xx (Internal)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ErrorInfo:
    """Metadata for an error code.

    Attributes:
        code: Error code (e.g., "E001", "W301")
        level: Error level ("Error", "Warning", or "Info")
        title: Brief description of the error
        doc_anchor: Anchor for documentation link
    """

    code: str
    level: str  # "Error", "Warning", "Info"
    title: str
    doc_anchor: str

    def doc_url(self) -> str:
        """Generate documentation URL for this error.

        Returns:
            Full documentation URL with anchor

        Example:
            >>> error = ERROR_REGISTRY["E001"]
            >>> error.doc_url()
            'https://docs.nlp2mcp.dev/errors/#e001-undefined-variable'
        """
        # For Sprint 6, use GitHub repository link
        # In future sprints, can update to docs.nlp2mcp.dev
        base_url = "https://github.com/jeffreyhorn/nlp2mcp/blob/main/docs/errors"
        return f"{base_url}/README.md#{self.doc_anchor}"


# Error Registry
# Maps error codes to their metadata
ERROR_REGISTRY: dict[str, ErrorInfo] = {
    # Syntax Errors (E0xx)
    "E001": ErrorInfo(
        code="E001",
        level="Error",
        title="Undefined variable",
        doc_anchor="e001-undefined-variable",
    ),
    "E002": ErrorInfo(
        code="E002",
        level="Error",
        title="Undefined equation",
        doc_anchor="e002-undefined-equation",
    ),
    "E003": ErrorInfo(
        code="E003",
        level="Error",
        title="Type mismatch",
        doc_anchor="e003-type-mismatch",
    ),
    "E101": ErrorInfo(
        code="E101",
        level="Error",
        title="Syntax error",
        doc_anchor="e101-syntax-error",
    ),
    # Convexity Warnings (W3xx)
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
        title="Division/quotient may be nonconvex",
        doc_anchor="w304-division-quotient",
    ),
    "W305": ErrorInfo(
        code="W305",
        level="Warning",
        title="Odd-power polynomial may be nonconvex",
        doc_anchor="w305-odd-power-polynomial",
    ),
}


def get_error_info(code: str) -> ErrorInfo | None:
    """Get error metadata by code.

    Args:
        code: Error code (e.g., "E001", "W301")

    Returns:
        ErrorInfo object if code exists, None otherwise

    Example:
        >>> info = get_error_info("E001")
        >>> info.title
        'Undefined variable'
        >>> info.doc_url()
        'https://github.com/jeffreyhorn/nlp2mcp/blob/main/docs/errors/README.md#e001-undefined-variable'
    """
    return ERROR_REGISTRY.get(code)


def get_all_error_codes() -> list[str]:
    """Get list of all registered error codes.

    Returns:
        Sorted list of error codes

    Example:
        >>> codes = get_all_error_codes()
        >>> 'E001' in codes
        True
        >>> 'W301' in codes
        True
    """
    return sorted(ERROR_REGISTRY.keys())
