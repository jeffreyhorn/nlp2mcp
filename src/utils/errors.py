"""
Error hierarchy for nlp2mcp.

Provides user-friendly error messages with actionable suggestions.
"""


class NLP2MCPError(Exception):
    """Base exception for all nlp2mcp errors."""

    pass


class UserError(NLP2MCPError):
    """
    Error caused by user input (invalid GAMS model, unsupported constructs, etc.).

    These errors indicate problems with the input that the user can fix.
    """

    def __init__(self, message: str, suggestion: str | None = None):
        """
        Create a user error with an optional suggestion.

        Args:
            message: Clear description of what went wrong
            suggestion: Actionable suggestion for how to fix it
        """
        self.message = message
        self.suggestion = suggestion
        super().__init__(self._format())

    def _format(self) -> str:
        """Format the error message with suggestion."""
        msg = f"Error: {self.message}"
        if self.suggestion:
            msg += f"\n\nSuggestion: {self.suggestion}"
        return msg


class InternalError(NLP2MCPError):
    """
    Internal nlp2mcp bug (assertion failures, inconsistent state, etc.).

    These errors indicate bugs in nlp2mcp that should be reported.
    """

    def __init__(self, message: str, context: dict | None = None):
        """
        Create an internal error with optional debugging context.

        Args:
            message: Description of the internal error
            context: Dictionary of debugging information
        """
        self.message = message
        self.context = context or {}
        super().__init__(self._format())

    def _format(self) -> str:
        """Format the error message with bug report instructions."""
        msg = f"Internal Error: {self.message}\n"
        msg += "\nThis is a bug in nlp2mcp. Please report at:\n"
        msg += "https://github.com/jeffreyhorn/nlp2mcp/issues\n"
        if self.context:
            msg += f"\nContext: {self.context}"
        return msg


class ParseError(UserError):
    """
    Error parsing GAMS model.

    Indicates syntax errors or unsupported GAMS constructs.
    """

    def __init__(
        self,
        message: str,
        line: int | None = None,
        column: int | None = None,
        source_line: str | None = None,
        suggestion: str | None = None,
    ):
        """
        Create a parse error with location information.

        Args:
            message: Description of the parse error
            line: Line number where error occurred (1-indexed)
            column: Column number where error occurred (1-indexed, position in original line)
            source_line: The source code line with the error (should be stripped of leading whitespace)
            suggestion: How to fix the error

        Note:
            source_line should have leading whitespace removed for proper caret alignment.
            The column number should refer to the position in the original source line.
        """
        self.line = line
        self.column = column
        self.source_line = source_line

        # Format message with location
        full_message = message
        if line is not None:
            full_message = f"Parse error at line {line}"
            if column is not None:
                full_message += f", column {column}"
            full_message += f": {message}"

            if source_line:
                full_message += f"\n  {source_line}"
                if column is not None:
                    # Column is 1-indexed position in original source
                    # Add 2 spaces to match source_line indent, then (column-1) for position
                    full_message += f"\n  {' ' * (column - 1)}^"

        super().__init__(full_message, suggestion)


class ModelError(UserError):
    """
    Error in model structure or semantics.

    Indicates undefined variables, missing objectives, inconsistent declarations, etc.
    """

    pass


class UnsupportedFeatureError(UserError):
    """
    GAMS feature not yet supported by nlp2mcp.

    Indicates a valid GAMS construct that nlp2mcp doesn't handle yet.
    """

    def __init__(self, feature: str, suggestion: str | None = None):
        """
        Create an unsupported feature error.

        Args:
            feature: Name of the unsupported feature
            suggestion: Alternative approach or workaround
        """
        message = f"GAMS feature '{feature}' is not yet supported by nlp2mcp"
        if not suggestion:
            suggestion = (
                "This feature may be added in a future release. "
                "Please file an issue at https://github.com/jeffreyhorn/nlp2mcp/issues"
            )
        super().__init__(message, suggestion)


class FileError(UserError):
    """
    Error related to file operations.

    Indicates missing files, permission errors, etc.
    """

    pass


class NumericalError(UserError):
    """
    Error related to numerical issues (NaN, Inf, numerical instability).

    Indicates problems with model parameters, expressions, or computed values
    that result in non-finite numbers.
    """

    def __init__(
        self,
        message: str,
        location: str | None = None,
        value: float | None = None,
        suggestion: str | None = None,
    ):
        """
        Create a numerical error with location and value context.

        Args:
            message: Description of the numerical issue
            location: Where the issue was detected (e.g., "parameter 'p[1]'", "derivative of f")
            value: The problematic value (NaN or Inf)
            suggestion: How to fix the issue
        """
        self.location = location
        self.value = value

        # Format message with location and value
        full_message = message
        if location:
            full_message = f"Numerical error in {location}: {message}"
        if value is not None:
            import math

            if math.isnan(value):
                full_message += " (value is NaN)"
            elif math.isinf(value):
                sign = "+" if value > 0 else "-"
                full_message += f" (value is {sign}Inf)"

        if not suggestion:
            suggestion = (
                "Check your model for:\n"
                "  - Division by zero\n"
                "  - Invalid operations (log of negative, sqrt of negative)\n"
                "  - Parameters with missing or invalid values\n"
                "  - Unbounded variables in nonlinear expressions"
            )

        super().__init__(full_message, suggestion)
