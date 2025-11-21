"""Tests for error message improvements in Sprint 8 Day 5.

This module tests:
1. Lark error wrapping (UnexpectedToken, UnexpectedCharacters)
2. ParseError formatting with source context and caret pointer
3. Semantic errors with actionable suggestions
4. Coverage of line/column information in all errors
"""

import pytest

from src.ir.parser import parse_model_text, parse_text
from src.utils.errors import ParseError


class TestLarkErrorWrapping:
    """Test that Lark syntax errors are wrapped in ParseError with context."""

    def test_unexpected_token_missing_semicolon(self):
        """Test UnexpectedToken wrapping for missing semicolon."""
        source = "Set i / 1*10"  # Missing semicolon

        with pytest.raises(ParseError) as exc_info:
            parse_text(source)

        error = exc_info.value
        assert error.line is not None, "Error should include line number"
        assert error.column is not None, "Error should include column number"
        assert "Unexpected" in str(error), "Error message should mention 'Unexpected'"

    def test_unexpected_characters_invalid_char(self):
        """Test UnexpectedCharacters wrapping for invalid character."""
        source = "Set i @ / 1*10 /;"  # Invalid character @

        with pytest.raises(ParseError) as exc_info:
            parse_text(source)

        error = exc_info.value
        assert error.line == 1, f"Error should be on line 1, got {error.line}"
        assert error.column is not None, "Error should include column number"
        assert "Unexpected character" in str(error), (
            "Error message should mention 'Unexpected character'"
        )


class TestParseErrorFormatting:
    """Test ParseError formatting with source lines and caret pointers."""

    def test_undefined_symbol_has_source_context(self):
        """Test that undefined symbol errors include source line and caret."""
        source = """
Set i / 1*10 /;
Parameter p;
p = undefined_var;
"""

        with pytest.raises(ParseError) as exc_info:
            parse_model_text(source)

        error = exc_info.value
        assert error.line is not None, "Error should include line number"
        assert error.column is not None, "Error should include column number"
        # Check that the error message contains useful information
        assert "undefined_var" in str(error).lower() or "Undefined symbol" in str(error)

    def test_parse_error_has_suggestion(self):
        """Test that ParseError includes actionable suggestions."""
        source = """
Set i / 1*10 /;
Parameter p;
p = unknown_param;
"""

        with pytest.raises(ParseError) as exc_info:
            parse_model_text(source)

        error = exc_info.value
        error_str = str(error)
        # The suggestion should provide guidance
        assert "Declare" in error_str or "suggestion" in error_str.lower()


class TestSemanticErrorsWithSuggestions:
    """Test semantic errors with actionable suggestions."""

    def test_undefined_symbol_has_suggestion(self):
        """Test undefined symbol error provides declaration suggestion."""
        source = """
Set i / 1*10 /;
Variable x;
Equation eq;
eq.. x =e= undefined_var;
"""

        with pytest.raises(ParseError) as exc_info:
            parse_model_text(source)

        error = exc_info.value
        error_str = str(error)
        assert "Declare" in error_str, "Error should suggest declaring the symbol"
        assert error.line is not None, "Error should have line number"

    def test_index_count_mismatch_has_suggestion(self):
        """Test parameter index mismatch provides count guidance."""
        source = """
Set i / i1, i2 /;
Set j / j1, j2 /;
Parameter p(i, j);
p('i1') = 10;
"""

        with pytest.raises(ParseError) as exc_info:
            parse_model_text(source)

        error = exc_info.value
        error_str = str(error)
        assert "expects" in error_str.lower() or "2" in error_str, (
            "Error should mention expected index count"
        )
        assert error.line is not None, "Error should have line number"

    def test_equation_without_declaration_has_suggestion(self):
        """Test undeclared equation error provides declaration suggestion."""
        source = """
Variable x;
undeclared_eq.. x =e= 5;
"""

        with pytest.raises(ParseError) as exc_info:
            parse_model_text(source)

        error = exc_info.value
        error_str = str(error)
        assert "declaration" in error_str.lower() or "Equation" in error_str, (
            "Error should mention equation declaration"
        )
        assert error.line is not None, "Error should have line number"


class TestErrorCoverage:
    """Test that all parser errors include location information."""

    def test_all_errors_have_line_numbers(self):
        """Verify that parser errors include line/column information."""
        # Test a few different error types to ensure coverage
        test_cases = [
            # Undefined symbol
            ("Set i / 1*10 /;\nParameter p;\np = undefined_var;", "undefined"),
            # Missing semicolon (Lark error)
            ("Set i / 1*10", "Unexpected"),
        ]

        for source, expected_text in test_cases:
            with pytest.raises(ParseError) as exc_info:
                parse_model_text(source) if "\n" in source else parse_text(source)

            error = exc_info.value
            # All errors should have line information
            assert error.line is not None, (
                f"Error for '{expected_text}' missing line number: {error}"
            )
            # Column may be None in some cases, but line should always be present

    def test_semantic_errors_preserve_context(self):
        """Test that semantic errors preserve context information."""
        source = """
Set i / i1, i2 /;
Variable x;
Equation eq;
eq.. x =e= unknown_symbol;
"""

        with pytest.raises(ParseError) as exc_info:
            parse_model_text(source)

        error = exc_info.value
        assert error.line is not None, "Error should have line number"
        # Check that context information is preserved
        error_str = str(error)
        assert "unknown_symbol" in error_str or "Undefined" in error_str


class TestErrorEnhancer:
    """Test ErrorEnhancer providing 'did you mean?' suggestions."""

    def test_keyword_typo_suggestion(self):
        """Test that keyword typos suggest the correct spelling."""
        source = "Scaler x;"  # Common typo: Scaler instead of Scalar

        with pytest.raises(ParseError) as exc_info:
            parse_text(source)

        error = exc_info.value
        error_str = str(error)
        assert "Did you mean 'Scalar'?" in error_str, (
            f"Should suggest 'Scalar' for typo 'Scaler': {error_str}"
        )

    def test_set_bracket_error_suggestion(self):
        """Test that set bracket errors suggest correct syntax."""
        source = "Set i [1*10];"  # Wrong: should use /.../ not [...]

        with pytest.raises(ParseError) as exc_info:
            parse_text(source)

        error = exc_info.value
        error_str = str(error)
        assert "/.../" in error_str or "not [...]" in error_str.lower(), (
            f"Should suggest /.../ syntax: {error_str}"
        )

    def test_missing_semicolon_suggestion(self):
        """Test that missing semicolons are detected and suggested."""
        source = "Set i / 1*10 /\nParameter x"  # Missing semicolon after Set declaration

        with pytest.raises(ParseError) as exc_info:
            parse_text(source)

        error = exc_info.value
        error_str = str(error)
        # Should suggest adding semicolon (the enhancer should detect this pattern)
        assert "semicolon" in error_str.lower() or ";" in error_str, (
            f"Should mention semicolon: {error_str}"
        )

    def test_unsupported_feature_explanation(self):
        """Test that unsupported features get roadmap explanations."""
        # Sprint 9: Lead/lag indexing (i++1) is now supported!
        # Updated test to verify it parses successfully
        source = """
Set i / i1, i2, i3 /;
Parameter x(i);
Equation eq(i);
eq(i).. x(i) =e= x(i++1);
"""  # Lead/lag indexing - NOW SUPPORTED (Sprint 9)

        # Should parse successfully now
        model = parse_model_text(source)
        assert model is not None
        assert len(model.equations) == 1

        # Verify the equation exists
        assert "eq" in model.equations

    def test_error_enhancement_preserves_location(self):
        """Test that error enhancement preserves line/column information."""
        source = "Variabl x;"  # Typo: Variabl instead of Variable

        with pytest.raises(ParseError) as exc_info:
            parse_text(source)

        error = exc_info.value
        # Enhanced errors should still have location information
        assert error.line is not None, "Enhanced error should preserve line number"
        assert error.column is not None, "Enhanced error should preserve column number"
        # And should have a suggestion
        assert error.suggestion is not None, "Enhanced error should have a suggestion"
