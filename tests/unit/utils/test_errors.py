"""
Tests for error message hierarchy and formatting.

Verifies that error messages are user-friendly with actionable suggestions.
"""

import pytest

from src.utils.errors import (
    FileError,
    InternalError,
    ModelError,
    NLP2MCPError,
    ParseError,
    UnsupportedFeatureError,
    UserError,
)


class TestErrorHierarchy:
    """Test that error hierarchy is properly structured."""

    def test_all_errors_inherit_from_base(self):
        """All custom errors should inherit from NLP2MCPError."""
        assert issubclass(UserError, NLP2MCPError)
        assert issubclass(InternalError, NLP2MCPError)
        assert issubclass(ParseError, UserError)
        assert issubclass(ModelError, UserError)
        assert issubclass(UnsupportedFeatureError, UserError)
        assert issubclass(FileError, UserError)

    def test_base_error_is_exception(self):
        """NLP2MCPError should be an Exception."""
        assert issubclass(NLP2MCPError, Exception)


class TestUserError:
    """Test UserError formatting and behavior."""

    def test_user_error_without_suggestion(self):
        """UserError should format message without suggestion."""
        error = UserError("Variable 'x' not found")
        assert "Error: Variable 'x' not found" in str(error)
        assert "Suggestion:" not in str(error)

    def test_user_error_with_suggestion(self):
        """UserError should include suggestion when provided."""
        error = UserError(
            "Variable 'cost' not found",
            suggestion="Did you mean 'costs'? Check variable spelling.",
        )
        msg = str(error)
        assert "Error: Variable 'cost' not found" in msg
        assert "Suggestion:" in msg
        assert "Did you mean 'costs'?" in msg

    def test_user_error_preserves_attributes(self):
        """UserError should preserve message and suggestion attributes."""
        error = UserError("Test message", suggestion="Test suggestion")
        assert error.message == "Test message"
        assert error.suggestion == "Test suggestion"


class TestInternalError:
    """Test InternalError formatting and behavior."""

    def test_internal_error_without_context(self):
        """InternalError should format message without context."""
        error = InternalError("Gradient dimension mismatch")
        msg = str(error)
        assert "Internal Error: Gradient dimension mismatch" in msg
        assert "This is a bug in nlp2mcp" in msg
        assert "github.com/jeffreyhorn/nlp2mcp/issues" in msg
        assert "Context:" not in msg

    def test_internal_error_with_context(self):
        """InternalError should include context when provided."""
        error = InternalError(
            "Gradient dimension mismatch",
            context={"gradient_cols": 10, "jacobian_cols": 12},
        )
        msg = str(error)
        assert "Internal Error" in msg
        assert "Context:" in msg
        assert "gradient_cols" in msg
        assert "10" in msg

    def test_internal_error_preserves_attributes(self):
        """InternalError should preserve message and context attributes."""
        error = InternalError("Test", context={"key": "value"})
        assert error.message == "Test"
        assert error.context == {"key": "value"}


class TestParseError:
    """Test ParseError formatting and behavior."""

    def test_parse_error_without_location(self):
        """ParseError should work without line/column info."""
        error = ParseError("Unexpected token", suggestion="Check syntax")
        msg = str(error)
        assert "Unexpected token" in msg
        assert "Suggestion:" in msg

    def test_parse_error_with_line_only(self):
        """ParseError should format with line number."""
        error = ParseError("Unexpected token", line=5)
        msg = str(error)
        assert "Parse error at line 5" in msg

    def test_parse_error_with_line_and_column(self):
        """ParseError should format with line and column."""
        error = ParseError("Unexpected semicolon", line=5, column=12)
        msg = str(error)
        assert "Parse error at line 5, column 12" in msg

    def test_parse_error_with_source_line(self):
        """ParseError should show source code context."""
        error = ParseError(
            "Unexpected semicolon",
            line=5,
            column=12,
            source_line="x + y =e= 0;",
        )
        msg = str(error)
        assert "x + y =e= 0;" in msg
        assert "^" in msg  # Caret pointing to error

    def test_parse_error_preserves_attributes(self):
        """ParseError should preserve location attributes."""
        error = ParseError("Test", line=5, column=10, source_line="test line")
        assert error.line == 5
        assert error.column == 10
        assert error.source_line == "test line"


class TestModelError:
    """Test ModelError behavior."""

    def test_model_error_is_user_error(self):
        """ModelError should be a UserError."""
        error = ModelError("Objective not defined", suggestion="Add objective")
        assert isinstance(error, UserError)
        msg = str(error)
        assert "Objective not defined" in msg
        assert "Add objective" in msg


class TestUnsupportedFeatureError:
    """Test UnsupportedFeatureError formatting."""

    def test_unsupported_feature_without_suggestion(self):
        """UnsupportedFeatureError should provide default suggestion."""
        error = UnsupportedFeatureError("dollar control directives")
        msg = str(error)
        assert "dollar control directives" in msg
        assert "not yet supported" in msg
        assert "future release" in msg
        assert "github.com/jeffreyhorn/nlp2mcp/issues" in msg

    def test_unsupported_feature_with_custom_suggestion(self):
        """UnsupportedFeatureError should allow custom suggestions."""
        error = UnsupportedFeatureError(
            "table statements", suggestion="Use parameter declarations instead"
        )
        msg = str(error)
        assert "table statements" in msg
        assert "Use parameter declarations instead" in msg


class TestFileError:
    """Test FileError behavior."""

    def test_file_error_is_user_error(self):
        """FileError should be a UserError."""
        error = FileError("File 'model.gms' not found", suggestion="Check file path")
        assert isinstance(error, UserError)
        msg = str(error)
        assert "model.gms" in msg
        assert "Check file path" in msg


class TestErrorMessageQuality:
    """
    Test that error messages follow best practices.

    These tests document the expected quality of error messages.
    """

    def test_user_error_suggests_fix(self):
        """User errors should suggest how to fix the problem."""
        # Example: Variable not found
        error = UserError(
            "Variable 'cost' not found in model",
            suggestion="Available variables: costs, demand, supply\n\n"
            "Did you mean 'costs'? Variables are case-sensitive.",
        )
        msg = str(error)

        # Should explain what went wrong
        assert "not found" in msg

        # Should list available options
        assert "Available variables" in msg

        # Should suggest likely fix
        assert "Did you mean" in msg

        # Should explain rules
        assert "case-sensitive" in msg

    def test_internal_error_aids_debugging(self):
        """Internal errors should provide debugging context."""
        error = InternalError(
            "Gradient and Jacobian have mismatched dimensions",
            context={
                "gradient_cols": 10,
                "jacobian_cols": 12,
                "gradient_vars": ["x", "y"],
                "jacobian_vars": ["x", "y", "z", "w"],
            },
        )
        msg = str(error)

        # Should indicate it's a bug
        assert "bug" in msg.lower()

        # Should provide reporting instructions
        assert "github" in msg.lower()

        # Should include debugging context
        assert "10" in msg
        assert "12" in msg

    def test_parse_error_shows_location(self):
        """Parse errors should show where the error occurred."""
        error = ParseError(
            "Expected equation name before '=e='",
            line=5,
            column=11,
            source_line="  x + y =e= 0;",
            suggestion="Equation definitions must have a name.\nTry: myeq.. x + y =e= 0;",
        )
        msg = str(error)

        # Should show line number
        assert "line 5" in msg

        # Should show column number
        assert "column 11" in msg

        # Should show the problematic line
        assert "x + y =e= 0;" in msg

        # Should show pointer to error location
        assert "^" in msg

        # Should explain what's expected
        assert "equation name" in msg.lower()

        # Should show correct syntax
        assert "myeq.." in msg

    def test_unsupported_feature_guides_user(self):
        """Unsupported feature errors should guide users to alternatives."""
        error = UnsupportedFeatureError(
            "$include directives",
            suggestion="nlp2mcp currently only supports single-file models.\n"
            "Please combine your files manually before processing.",
        )
        msg = str(error)

        # Should identify the unsupported feature
        assert "$include directives" in msg

        # Should explain the limitation
        assert "not yet supported" in msg

        # Should provide workaround
        assert "combine your files" in msg


class TestErrorCatching:
    """Test that errors can be caught by their hierarchy."""

    def test_catch_all_nlp2mcp_errors(self):
        """Can catch all nlp2mcp errors with base class."""
        with pytest.raises(NLP2MCPError):
            raise UserError("test")

        with pytest.raises(NLP2MCPError):
            raise InternalError("test")

        with pytest.raises(NLP2MCPError):
            raise ParseError("test")

    def test_catch_user_errors(self):
        """Can catch all user errors."""
        with pytest.raises(UserError):
            raise ModelError("test")

        with pytest.raises(UserError):
            raise ParseError("test")

        with pytest.raises(UserError):
            raise FileError("test")

    def test_distinguish_error_types(self):
        """Can distinguish between error types."""
        # User error should not be caught as InternalError
        with pytest.raises(UserError):
            try:
                raise UserError("test")
            except InternalError:
                pytest.fail("UserError should not be caught as InternalError")

        # Internal error should not be caught as UserError
        with pytest.raises(InternalError):
            try:
                raise InternalError("test")
            except UserError:
                pytest.fail("InternalError should not be caught as UserError")
