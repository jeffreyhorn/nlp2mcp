"""
Tests for parse progress tracking utilities.
"""

import pytest

from src.utils.parse_progress import (
    calculate_parse_progress,
    count_logical_lines,
    count_logical_lines_up_to,
    extract_error_line,
    extract_missing_features,
)


class TestCountLogicalLines:
    """Tests for count_logical_lines function."""

    def test_empty_source(self):
        """Empty source has 0 logical lines."""
        assert count_logical_lines("") == 0

    def test_single_line(self):
        """Single code line counts as 1."""
        assert count_logical_lines("Set i / 1*10 /;") == 1

    def test_multiple_lines(self):
        """Multiple code lines are counted."""
        source = """
Set i / 1*10 /;
Set j / a, b, c /;
Parameter x(i);
"""
        assert count_logical_lines(source) == 3

    def test_skip_blank_lines(self):
        """Blank lines are not counted."""
        source = """
Set i / 1*10 /;

Set j / a, b, c /;

"""
        assert count_logical_lines(source) == 2

    def test_skip_comment_lines(self):
        """Lines starting with * are not counted."""
        source = """
* This is a comment
Set i / 1*10 /;
* Another comment
Set j / a, b, c /;
"""
        assert count_logical_lines(source) == 2

    def test_inline_comments(self):
        """Lines with inline comments are counted."""
        source = """
Set i / 1*10 /;  * This is an inline comment
Parameter x(i);  * Another inline comment
"""
        assert count_logical_lines(source) == 2

    def test_comment_only_after_asterisk(self):
        """Lines with only comments after * are not counted."""
        source = """
Set i / 1*10 /;
* Comment
     * Indented comment
Set j;
"""
        assert count_logical_lines(source) == 2

    def test_multiline_comments(self):
        """Multiline comments ($ontext ... $offtext) are skipped."""
        source = """
Set i / 1*10 /;
$ontext
This is a multiline comment
It spans multiple lines
Set j; <- This should not be counted
$offtext
Parameter x(i);
"""
        assert count_logical_lines(source) == 2

    def test_multiline_comments_case_insensitive(self):
        """Multiline comment directives are case-insensitive."""
        source = """
Set i / 1*10 /;
$ONTEXT
Comment content
$OFFTEXT
Parameter x(i);
"""
        assert count_logical_lines(source) == 2

    def test_mixed_comments_and_code(self):
        """Complex source with multiple comment types."""
        source = """
* Header comment
Set i / 1*10 /;

$ontext
Multiline comment block
explaining the model
$offtext

Parameter x(i);  * Inline comment
* Another single-line comment

Variable y;
"""
        assert count_logical_lines(source) == 3


class TestCountLogicalLinesUpTo:
    """Tests for count_logical_lines_up_to function."""

    def test_count_up_to_line_1(self):
        """Count up to line 1 (exclusive) is 0."""
        source = "Set i / 1*10 /;\nSet j / a, b, c /;"
        assert count_logical_lines_up_to(source, 1) == 0

    def test_count_up_to_line_2(self):
        """Count up to line 2 includes line 1."""
        source = "Set i / 1*10 /;\nSet j / a, b, c /;"
        assert count_logical_lines_up_to(source, 2) == 1

    def test_count_up_to_with_blank_lines(self):
        """Blank lines are skipped when counting."""
        source = """
Set i / 1*10 /;

Set j / a, b, c /;

Parameter x(i);
"""
        # Line 1: blank, Line 2: Set i, Line 3: blank, Line 4: Set j
        # Counting up to line 4 (exclusive) includes lines 1-3, which has 1 logical line (Set i)
        assert count_logical_lines_up_to(source, 4) == 1

    def test_count_up_to_with_comments(self):
        """Comment lines are skipped."""
        source = """
* Comment
Set i / 1*10 /;
* Another comment
Set j / a, b, c /;
"""
        # Line 1: blank, Line 2: comment, Line 3: Set i, Line 4: comment, Line 5: Set j
        # Counting up to line 5 (exclusive) includes lines 1-4, which has 1 logical line (Set i)
        assert count_logical_lines_up_to(source, 5) == 1

    def test_count_up_to_beyond_end(self):
        """Count up to line beyond end of file."""
        source = "Set i / 1*10 /;\nSet j / a, b, c /;"
        # Only 2 lines, counting up to line 100 should include both
        assert count_logical_lines_up_to(source, 100) == 2

    def test_count_up_to_with_multiline_comments(self):
        """Multiline comments are properly skipped."""
        source = """
Set i / 1*10 /;
$ontext
Comment line 1
Comment line 2
$offtext
Parameter x(i);
"""
        # Count up to line 7 (Parameter x line, exclusive)
        # Lines: 1: blank, 2: Set i, 3: $ontext, 4-5: comments, 6: $offtext, 7: Parameter
        # Counting up to line 7 (exclusive) includes lines 1-6, which has 1 logical line (Set i)
        assert count_logical_lines_up_to(source, 7) == 1


class TestExtractErrorLine:
    """Tests for extract_error_line function."""

    def test_exception_with_line_attribute(self):
        """Extract line from exception.line attribute."""

        class MockError(Exception):
            def __init__(self):
                self.line = 42

        error = MockError()
        assert extract_error_line(error) == 42

    def test_exception_with_line_none(self):
        """Exception with line=None returns None."""

        class MockError(Exception):
            def __init__(self):
                self.line = None

        error = MockError()
        assert extract_error_line(error) is None

    def test_parse_from_error_message_at_line(self):
        """Extract line number from 'at line N' pattern."""
        error = Exception("Parse error at line 23 col 5")
        assert extract_error_line(error) == 23

    def test_parse_from_error_message_line_only(self):
        """Extract line number from 'line N' pattern."""
        error = Exception("Unexpected token on line 15")
        assert extract_error_line(error) == 15

    def test_no_line_information(self):
        """No line information returns None."""
        error = Exception("Generic error with no line info")
        assert extract_error_line(error) is None


class TestExtractMissingFeatures:
    """Tests for extract_missing_features function."""

    def test_lead_lag_indexing_in_message(self):
        """Detect i++1 or i--1 patterns in error message."""
        error_msg = "Unexpected token at i++1"
        features = extract_missing_features("UnexpectedToken", error_msg)
        assert "lead/lag indexing (i++1, i--1)" in features

    def test_lead_lag_indexing_in_source_line(self):
        """Detect i++1 in source line."""
        error_msg = "Unexpected token"
        source_line = "areadef(i).. area(i) =e= 0.5*(x(i)*y(i++1));"
        features = extract_missing_features("UnexpectedToken", error_msg, source_line)
        assert "lead/lag indexing (i++1, i--1)" in features

    def test_option_statements(self):
        """Detect option statement errors."""
        error_msg = "Unexpected token 'limrow' in option limrow=100"
        features = extract_missing_features("UnexpectedToken", error_msg)
        assert "option statements" in features

    def test_model_sections(self):
        """Detect model section syntax (mx, my)."""
        error_msg = "Unexpected token 'mx' in model declaration"
        features = extract_missing_features("UnexpectedToken", error_msg)
        assert "model sections (mx, my, etc.)" in features

    def test_function_calls_in_assignments(self):
        """Detect function calls in assignments."""
        error_msg = "Assignment must use constants; got Call(uniform, ...)"
        features = extract_missing_features("ParserSemanticError", error_msg)
        assert "function calls in assignments" in features

    def test_indexed_assignments(self):
        """Detect indexed assignment errors."""
        error_msg = "Indexed assignments are not supported yet"
        features = extract_missing_features("ParserSemanticError", error_msg)
        assert "indexed assignments" in features

    def test_nested_indexing_in_message(self):
        """Detect nested indexing patterns."""
        error_msg = "Unexpected syntax at x(y(i))"
        features = extract_missing_features("UnexpectedToken", error_msg)
        assert "nested indexing" in features

    def test_nested_indexing_in_source(self):
        """Detect nested indexing in source line."""
        error_msg = "Parse error"
        source_line = "z = x(y(i));"
        features = extract_missing_features("UnexpectedToken", error_msg, source_line)
        assert "nested indexing" in features

    def test_variable_attributes(self):
        """Detect variable attribute access (.l, .m)."""
        error_msg = "Unexpected token '.l' in expression"
        features = extract_missing_features("UnexpectedToken", error_msg)
        assert "variable attributes (.l, .m, etc.)" in features

    def test_generic_not_supported(self):
        """Extract feature from generic 'not supported' message."""
        error_msg = "Multi-dimensional parameters are not supported"
        features = extract_missing_features("ParserSemanticError", error_msg)
        # The regex captures "Multi-dimensional parameters" but we only check that it's in one of the features
        assert any("dimensional parameters" in f for f in features)

    def test_fallback_for_unknown_error(self):
        """Unknown error types get generic hint."""
        error_msg = "Something went wrong"
        features = extract_missing_features("UnexpectedToken", error_msg)
        assert "syntax error" in features

    def test_semantic_error_fallback(self):
        """Semantic errors without specific pattern get generic hint."""
        error_msg = "Some semantic issue"
        features = extract_missing_features("ParserSemanticError", error_msg)
        assert "semantic error after successful parse" in features

    def test_limit_to_two_features(self):
        """Only top 2 features are returned."""
        error_msg = "Error with i++1 and option limrow and variable.l"
        features = extract_missing_features("UnexpectedToken", error_msg)
        assert len(features) <= 2

    def test_deduplication(self):
        """Duplicate features are removed."""
        error_msg = "Indexed assignments are not supported, indexed assignment failed"
        features = extract_missing_features("ParserSemanticError", error_msg)
        # Should only appear once
        feature_count = sum(1 for f in features if "indexed assignment" in f.lower())
        assert feature_count == 1


class TestCalculateParseProgress:
    """Tests for calculate_parse_progress function."""

    def test_successful_parse(self):
        """Successful parse returns 100%."""
        source = """
Set i / 1*10 /;
Parameter x(i);
Variable y;
"""
        progress = calculate_parse_progress(source, error=None)

        assert progress["percentage"] == 100.0
        assert progress["lines_parsed"] == 3
        assert progress["lines_total"] == 3
        assert progress["error_line"] is None

    def test_parse_error_with_line(self):
        """Parse error calculates partial progress."""
        source = """
Set i / 1*10 /;
Set j / a, b, c /;
Parameter x(i);
Variable y;
"""

        class MockError(Exception):
            def __init__(self):
                self.line = 4  # Error on line 4 (Parameter x)

        error = MockError()
        progress = calculate_parse_progress(source, error)

        # Lines 1-3 parsed (blank, Set i, Set j)
        assert progress["percentage"] == 50.0  # 2/4 lines
        assert progress["lines_parsed"] == 2
        assert progress["lines_total"] == 4
        assert progress["error_line"] == 4

    def test_parse_error_no_line(self):
        """Parse error without line number assumes 0% progress."""
        source = """
Set i / 1*10 /;
Parameter x(i);
"""
        error = Exception("Generic error")
        progress = calculate_parse_progress(source, error)

        assert progress["percentage"] == 0.0
        assert progress["lines_parsed"] == 0
        assert progress["lines_total"] == 2
        assert progress["error_line"] is None

    def test_empty_source(self):
        """Empty source returns 0% even on success."""
        progress = calculate_parse_progress("", error=None)

        assert progress["percentage"] == 100.0  # Success case
        assert progress["lines_parsed"] == 0
        assert progress["lines_total"] == 0

    def test_high_partial_progress(self):
        """Model that parses 92% before error."""
        # 24 logical lines, error on line 23 (22 parsed)
        source = "\n".join([f"Set x{i} / 1*10 /;" for i in range(24)])

        class MockError(Exception):
            def __init__(self):
                self.line = 23

        error = MockError()
        progress = calculate_parse_progress(source, error)

        assert progress["percentage"] == pytest.approx(91.7, abs=0.1)  # 22/24
        assert progress["lines_parsed"] == 22
        assert progress["lines_total"] == 24
        assert progress["error_line"] == 23
