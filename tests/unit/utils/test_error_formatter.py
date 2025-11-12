"""Unit tests for error_formatter module."""

from src.utils.error_formatter import (
    ErrorContext,
    FormattedError,
    create_parse_error,
    create_warning,
    get_source_lines,
)


class TestErrorContext:
    """Test ErrorContext dataclass."""

    def test_create_error_context(self):
        """Test creating an ErrorContext."""
        context = ErrorContext(
            filename="test.gms",
            line=10,
            column=5,
            source_lines=["line 9", "line 10", "line 11"],
        )

        assert context.filename == "test.gms"
        assert context.line == 10
        assert context.column == 5
        assert len(context.source_lines) == 3


class TestFormattedError:
    """Test FormattedError formatting."""

    def test_format_error_with_context(self):
        """Test error formatting with source context."""
        error = FormattedError(
            level="Error",
            title="Test error",
            context=ErrorContext(
                filename="test.gms",
                line=10,
                column=5,
                source_lines=["line 9", "line 10", "line 11"],
            ),
            explanation="This is a test explanation.",
            action="Take this action to fix it.",
            doc_link="docs/TEST.md",
        )

        output = error.format()

        assert "Error: Test error (line 10, column 5)" in output
        assert "  10 | line 10" in output
        assert "^" in output  # Caret pointer
        assert "This is a test explanation" in output
        assert "Take this action to fix it" in output
        assert "See: docs/TEST.md" in output

    def test_format_error_without_context(self):
        """Test error formatting without source context."""
        error = FormattedError(
            level="Warning",
            title="Test warning",
            context=None,
            explanation="Warning explanation.",
            action="Suggested action.",
        )

        output = error.format()

        assert "Warning: Test warning" in output
        assert "line" not in output  # No location
        assert "Warning explanation" in output
        assert "Suggested action" in output

    def test_format_error_without_doc_link(self):
        """Test error formatting without documentation link."""
        error = FormattedError(
            level="Error",
            title="Test error",
            context=None,
            explanation="Explanation.",
            action="Action.",
            doc_link=None,
        )

        output = error.format()

        assert "See:" not in output

    def test_caret_position(self):
        """Test caret is positioned correctly under error column."""
        # Context: line 5 is the error line, with one line before
        # source_lines[0] = line 4, source_lines[1] = line 5
        error = FormattedError(
            level="Error",
            title="Syntax error",
            context=ErrorContext(
                filename="test.gms",
                line=5,
                column=10,
                source_lines=["Equations objdef;", "Variables x, y, z;"],
            ),
            explanation="Missing semicolon.",
            action="Add semicolon.",
        )

        output = error.format()
        lines = output.split("\n")

        # Find the source line and caret line
        source_line_idx = -1
        for i, line in enumerate(lines):
            if "Variables x, y, z;" in line:
                source_line_idx = i
                break

        assert source_line_idx >= 0, "Source line not found in output"

        # Next line should be caret
        caret_line = lines[source_line_idx + 1]

        # Count spaces before caret
        # Format is "{lineno:>4} | {source}"
        # For column 10: 4 spaces + " | " (3 chars) + 9 spaces (column-1) = 16 spaces before ^
        expected_spaces = 4 + 3 + (10 - 1)
        assert caret_line.startswith(" " * expected_spaces + "^")

    def test_multiline_context(self):
        """Test formatting with multiple context lines."""
        error = FormattedError(
            level="Error",
            title="Type error",
            context=ErrorContext(
                filename="test.gms",
                line=15,
                column=20,
                source_lines=[
                    "Variables x, y;",
                    "constraint.. x + y =n= 0;",
                    "Model m /all/;",
                ],
            ),
            explanation="Unsupported equation type.",
            action="Use =e=, =l=, or =g=.",
        )

        output = error.format()

        # Should show all three lines with line numbers
        assert "  14 | Variables x, y;" in output
        assert "  15 | constraint.. x + y =n= 0;" in output
        assert "  16 | Model m /all/;" in output


class TestConvenienceFunctions:
    """Test convenience functions for creating errors."""

    def test_create_parse_error(self):
        """Test create_parse_error convenience function."""
        error = create_parse_error(
            title="Unsupported operator",
            line=10,
            column=15,
            source_lines=["x + y =n= 0;"],
            explanation="Operator =n= not supported.",
            action="Use =e= instead.",
            filename="model.gms",
            doc_link="docs/GAMS_SUBSET.md",
        )

        assert "Error: Unsupported operator (line 10, column 15)" in error
        assert "x + y =n= 0;" in error
        assert "Operator =n= not supported" in error
        assert "Use =e= instead" in error
        assert "See: docs/GAMS_SUBSET.md" in error

    def test_create_warning_with_context(self):
        """Test create_warning with source context."""
        warning = create_warning(
            title="Non-convex problem",
            line=20,
            column=5,
            source_lines=["x**2 + y**2 =e= 4;"],
            explanation="Nonlinear equality detected.",
            action="Consider using inequality instead.",
            doc_link="docs/CONVEXITY.md",
        )

        assert "Warning: Non-convex problem (line 20, column 5)" in warning
        assert "x**2 + y**2 =e= 4;" in warning
        assert "Nonlinear equality detected" in warning

    def test_create_warning_without_context(self):
        """Test create_warning without source context."""
        warning = create_warning(
            title="General warning",
            explanation="This is a general warning.",
            action="Take appropriate action.",
        )

        assert "Warning: General warning" in warning
        assert "line" not in warning  # No location
        assert "This is a general warning" in warning


class TestGetSourceLines:
    """Test get_source_lines utility function."""

    def test_get_source_lines_middle(self):
        """Test extracting source lines from middle of file."""
        source = "line1\nline2\nline3\nline4\nline5"
        start, lines = get_source_lines(source, error_line=3, context_lines=1)

        assert start == 2  # 1-indexed
        assert lines == ["line2", "line3", "line4"]

    def test_get_source_lines_start(self):
        """Test extracting source lines near start of file."""
        source = "line1\nline2\nline3\nline4\nline5"
        start, lines = get_source_lines(source, error_line=1, context_lines=1)

        assert start == 1
        assert lines == ["line1", "line2"]

    def test_get_source_lines_end(self):
        """Test extracting source lines near end of file."""
        source = "line1\nline2\nline3\nline4\nline5"
        start, lines = get_source_lines(source, error_line=5, context_lines=1)

        assert start == 4
        assert lines == ["line4", "line5"]

    def test_get_source_lines_no_context(self):
        """Test extracting only error line (context_lines=0)."""
        source = "line1\nline2\nline3\nline4\nline5"
        start, lines = get_source_lines(source, error_line=3, context_lines=0)

        assert start == 3
        assert lines == ["line3"]

    def test_get_source_lines_large_context(self):
        """Test extracting with large context (clamped to file bounds)."""
        source = "line1\nline2\nline3"
        start, lines = get_source_lines(source, error_line=2, context_lines=10)

        assert start == 1
        assert lines == ["line1", "line2", "line3"]


class TestRealWorldExamples:
    """Test formatting with real-world error scenarios."""

    def test_unsupported_equation_type(self):
        """Test formatting for unsupported equation type error."""
        error = FormattedError(
            level="Error",
            title="Unsupported equation type '=n='",
            context=ErrorContext(
                filename="model.gms",
                line=15,
                column=20,
                source_lines=["constraint.. x + y =n= 0;"],
            ),
            explanation=(
                "nlp2mcp currently only supports:\n"
                "  =e= (equality)\n"
                "  =l= (less than or equal)\n"
                "  =g= (greater than or equal)\n\n"
                "The '=n=' operator (non-binding) is not supported for MCP reformulation."
            ),
            action="Action: Convert to one of the supported equation types.",
            doc_link="docs/GAMS_SUBSET.md#equation-types",
        )

        output = error.format()

        assert "Error: Unsupported equation type '=n='" in output
        assert "constraint.. x + y =n= 0;" in output
        assert "=e= (equality)" in output
        assert "Convert to one of the supported equation types" in output

    def test_convexity_warning(self):
        """Test formatting for convexity warning."""
        warning = FormattedError(
            level="Warning",
            title="Non-convex problem detected",
            context=ErrorContext(
                filename="model.gms",
                line=18,
                column=20,
                source_lines=["circle_constraint.. x**2 + y**2 =e= 4;"],
            ),
            explanation=(
                "Nonlinear equality in equation 'circle_constraint'\n\n"
                "Nonlinear equalities typically define non-convex feasible sets.\n"
                "KKT-based MCP reformulation may not be solvable."
            ),
            action=(
                "Recommendation:\n"
                "  - Use NLP solver (CONOPT, IPOPT) instead of PATH\n"
                "  - Or reformulate as inequality if possible: x**2 + y**2 =l= 4"
            ),
            doc_link="docs/CONVEXITY.md",
        )

        output = warning.format()

        assert "Warning: Non-convex problem detected" in output
        assert "x**2 + y**2 =e= 4" in output
        assert "non-convex feasible sets" in output
        assert "Use NLP solver" in output

    def test_undefined_variable(self):
        """Test formatting for undefined variable error."""
        error = FormattedError(
            level="Error",
            title="Undefined variable 'z'",
            context=ErrorContext(
                filename="model.gms",
                line=24,
                column=15,
                source_lines=[
                    "Equation objdef;",
                    "objdef.. obj =e= x + y + z;",
                ],
            ),
            explanation=("Variable 'z' is used in equation 'objdef' but was never declared."),
            action=(
                "Action: Add variable declaration before use:\n"
                "  Variables x, y, z;\n\n"
                "Or check for typos in variable name."
            ),
        )

        output = error.format()

        assert "Error: Undefined variable 'z'" in output
        assert "objdef.. obj =e= x + y + z;" in output
        assert "was never declared" in output
        assert "Add variable declaration" in output
