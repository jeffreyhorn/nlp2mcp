"""Enhanced error message formatter for nlp2mcp.

Provides structured error messages with source context, explanations,
and actionable suggestions to improve user experience.

This module implements the error message template specified in:
docs/planning/EPIC_2/SPRINT_6/ERROR_MESSAGE_TEMPLATE.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass
class ErrorContext:
    """Source code context for an error.

    Attributes:
        filename: Name of the source file
        line: Line number where error occurred (1-indexed)
        column: Column number where error occurred (1-indexed)
        source_lines: List of source code lines for context (typically 3 lines)
            IMPORTANT: source_lines[0] must correspond to line number (line - 1).
            This means if the error is on line 10, source_lines should contain
            line 9 as the first element (if available), line 10 as the second
            element (the actual error line), and line 11 as the third element
            (if available). The formatter will calculate line numbers based on
            this assumption.

            source_lines must not be empty when ErrorContext is created.
    """

    filename: str
    line: int
    column: int
    source_lines: list[str]

    def __post_init__(self):
        """Validate ErrorContext after initialization."""
        if not self.source_lines:
            raise ValueError(
                "ErrorContext.source_lines must not be empty. "
                "Provide at least the error line for context."
            )


@dataclass
class FormattedError:
    """Structured error message with formatting.

    Implements the error message template with components:
    - Error level (Error or Warning)
    - Brief title
    - Source context with caret pointer
    - Detailed explanation
    - Suggested action
    - Optional documentation link

    Attributes:
        level: "Error" or "Warning"
        title: Brief description of the error
        context: Optional source code context
        explanation: Detailed explanation of what went wrong
        action: Suggested action to fix the error
        doc_link: Optional link to documentation
    """

    level: Literal["Error", "Warning"]
    title: str
    context: ErrorContext | None
    explanation: str
    action: str
    doc_link: str | None = None

    def format(self) -> str:
        """Format error for display.

        Returns:
            Formatted error message as a string

        Example output:
            Error: Unsupported equation type '=n=' (line 15, column 20)

              15 | constraint.. x + y =n= 0;
                                        ^^^

            nlp2mcp currently only supports:
              =e= (equality)
              =l= (less than or equal)
              =g= (greater than or equal)

            Action: Convert to one of the supported equation types.
            See: docs/GAMS_SUBSET.md#equation-types
        """
        parts = []

        # Header: Error/Warning level with title and location
        if self.context:
            parts.append(
                f"{self.level}: {self.title} "
                f"(line {self.context.line}, column {self.context.column})"
            )
        else:
            parts.append(f"{self.level}: {self.title}")

        # Source context with caret pointer
        if self.context:
            parts.append("")  # blank line
            parts.append(self._format_source_context())

        # Explanation
        parts.append("")
        parts.append(self.explanation)

        # Action
        parts.append("")
        parts.append(self.action)

        # Documentation link
        if self.doc_link:
            parts.append(f"See: {self.doc_link}")

        return "\n".join(parts)

    def _format_source_context(self) -> str:
        """Format source context with line numbers and caret pointer.

        Returns:
            Formatted source context (typically 3 lines with caret under error)

        Example:
              14 | Variables x, y;
              15 | constraint.. x + y =n= 0;
                                        ^^^
              16 | Model m /all/;
        """
        if not self.context:
            return ""

        lines = []
        error_line_index = -1

        # Determine which lines to show (up to 1 before, error line, up to 1 after)
        start_line = self.context.line - 1  # Line number of first source_lines entry
        for i, source in enumerate(self.context.source_lines):
            line_num = start_line + i
            formatted = f"{line_num:>4} | {source}"
            lines.append(formatted)

            # Track which line is the error line
            if line_num == self.context.line:
                error_line_index = len(lines) - 1

        # Add caret pointer under error line
        if error_line_index >= 0:
            # Calculate position for caret
            # Format is "{lineno:>4} | {source}"
            # So caret needs: 4 spaces + " | " (3 chars) + column-1 spaces + caret
            indent = 4 + 3 + (self.context.column - 1)

            # Determine caret length based on token (for now, just use 1-3 carets)
            # In future, could pass token length for accurate width
            caret = "^"

            # Add caret line after error line
            lines.insert(error_line_index + 1, " " * indent + caret)

        return "\n".join(lines)


def create_parse_error(
    title: str,
    line: int,
    column: int,
    source_lines: list[str],
    explanation: str,
    action: str,
    filename: str = "model.gms",
    doc_link: str | None = None,
) -> str:
    """Convenience function to create a formatted parse error.

    Args:
        title: Brief error description
        line: Line number (1-indexed)
        column: Column number (1-indexed)
        source_lines: Source code lines for context
        explanation: Detailed explanation
        action: Suggested fix
        filename: Source filename
        doc_link: Optional documentation link

    Returns:
        Formatted error message string

    Example:
        >>> error = create_parse_error(
        ...     title="Unsupported equation type '=n='",
        ...     line=15,
        ...     column=20,
        ...     source_lines=["constraint.. x + y =n= 0;"],
        ...     explanation="nlp2mcp only supports =e=, =l=, =g=",
        ...     action="Convert to a supported equation type.",
        ...     doc_link="docs/GAMS_SUBSET.md"
        ... )
    """
    error = FormattedError(
        level="Error",
        title=title,
        context=ErrorContext(
            filename=filename,
            line=line,
            column=column,
            source_lines=source_lines,
        ),
        explanation=explanation,
        action=action,
        doc_link=doc_link,
    )
    return error.format()


def create_warning(
    title: str,
    explanation: str,
    action: str,
    line: int | None = None,
    column: int | None = None,
    source_lines: list[str] | None = None,
    filename: str = "model.gms",
    doc_link: str | None = None,
) -> str:
    """Convenience function to create a formatted warning.

    Args:
        title: Brief warning description
        explanation: Detailed explanation
        action: Recommended action
        line: Optional line number (1-indexed)
        column: Optional column number (1-indexed)
        source_lines: Optional source code lines for context
        filename: Source filename
        doc_link: Optional documentation link

    Returns:
        Formatted warning message string

    Example:
        >>> warning = create_warning(
        ...     title="Non-convex problem detected",
        ...     explanation="Nonlinear equality may cause unsolvable MCP",
        ...     action="Use NLP solver instead of PATH",
        ...     doc_link="docs/CONVEXITY.md"
        ... )

    Note:
        To create context, either provide all three (line, column, source_lines)
        or none. If only some are provided, a ValueError will be raised.
    """
    # Validate that context information is either complete or not provided
    context_fields = [line, column, source_lines]
    provided_count = sum(f is not None for f in context_fields)

    if provided_count not in (0, 3):
        raise ValueError(
            "Context information must be complete: provide either all three "
            "(line, column, source_lines) or none. "
            f"Currently provided: line={line is not None}, "
            f"column={column is not None}, "
            f"source_lines={source_lines is not None}"
        )

    context = None
    if line is not None and column is not None and source_lines:
        context = ErrorContext(
            filename=filename,
            line=line,
            column=column,
            source_lines=source_lines,
        )

    warning = FormattedError(
        level="Warning",
        title=title,
        context=context,
        explanation=explanation,
        action=action,
        doc_link=doc_link,
    )
    return warning.format()


def get_source_lines(
    full_source: str, error_line: int, context_lines: int = 1
) -> tuple[int, list[str]]:
    """Extract source lines around an error for context display.

    Args:
        full_source: Complete source code as string
        error_line: Line number where error occurred (1-indexed)
        context_lines: Number of lines to show before/after error (default: 1)

    Returns:
        Tuple of (start_line_number, list_of_source_lines)
        start_line_number is 1-indexed line number of first returned line

    Example:
        >>> source = "line1\\nline2\\nline3\\nline4\\nline5"
        >>> start, lines = get_source_lines(source, error_line=3, context_lines=1)
        >>> start
        2
        >>> lines
        ['line2', 'line3', 'line4']
    """
    all_lines = full_source.splitlines()

    # Convert to 0-indexed for slicing
    error_idx = error_line - 1

    # Determine range (at most context_lines before and after)
    start_idx = max(0, error_idx - context_lines)
    end_idx = min(len(all_lines), error_idx + context_lines + 1)

    # Extract lines
    context = all_lines[start_idx:end_idx]

    # Return 1-indexed start line number and extracted lines
    return start_idx + 1, context
