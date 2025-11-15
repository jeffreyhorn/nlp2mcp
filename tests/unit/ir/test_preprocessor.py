"""Unit tests for GAMS preprocessor directive handling.

Tests the three new preprocessor functions added in Sprint 7 Day 1:
- extract_conditional_sets(): Extract defaults from $if not set directives
- expand_macros(): Expand %macro% references
- strip_conditional_directives(): Replace directives with comments

Based on design from docs/research/preprocessor_directives.md
"""

from src.ir.preprocessor import (
    expand_macros,
    extract_conditional_sets,
    strip_conditional_directives,
)


class TestExtractConditionalSets:
    """Test extract_conditional_sets() function."""

    def test_single_directive_quoted(self):
        """Extract a single $if not set directive with quoted value."""
        source = '$if not set size $set size "10"'
        result = extract_conditional_sets(source)
        assert result == {"size": "10"}

    def test_single_directive_unquoted(self):
        """Extract a single $if not set directive with unquoted value."""
        source = "$if not set size $set size 10"
        result = extract_conditional_sets(source)
        assert result == {"size": "10"}

    def test_multiple_directives(self):
        """Extract multiple $if not set directives."""
        source = """
$if not set size $set size "10"
$if not set name $set name "test"
Set i /1*%size%/;
"""
        result = extract_conditional_sets(source)
        assert result == {"size": "10", "name": "test"}

    def test_case_insensitive_directives(self):
        """$if and $set keywords are case-insensitive."""
        source = '$IF NOT SET size $SET size "10"'
        result = extract_conditional_sets(source)
        assert result == {"size": "10"}

    def test_variable_name_case_preserved(self):
        """Variable names preserve their case."""
        source = '$if not set myVar $set myVar "value"'
        result = extract_conditional_sets(source)
        assert "myVar" in result
        assert result["myVar"] == "value"

    def test_last_value_wins(self):
        """If same variable set multiple times, last value wins."""
        source = """
$if not set size $set size "10"
$if not set size $set size "20"
"""
        result = extract_conditional_sets(source)
        assert result == {"size": "20"}

    def test_empty_source(self):
        """Empty source returns empty dict."""
        result = extract_conditional_sets("")
        assert result == {}

    def test_no_directives(self):
        """Source with no $if not set directives returns empty dict."""
        source = "Set i /1*10/;\nVariables x;"
        result = extract_conditional_sets(source)
        assert result == {}


class TestExpandMacros:
    """Test expand_macros() function."""

    def test_single_macro(self):
        """Expand a single macro reference."""
        source = "Set i /1*%size%/;"
        macros = {"size": "10"}
        result = expand_macros(source, macros)
        assert result == "Set i /1*10/;"

    def test_multiple_macros(self):
        """Expand multiple macro references."""
        source = "Set i /1*%size%/;\nParameter p /%name%/;"
        macros = {"size": "10", "name": "test"}
        result = expand_macros(source, macros)
        assert result == "Set i /1*10/;\nParameter p /test/;"

    def test_macro_used_multiple_times(self):
        """Same macro referenced multiple times gets expanded each time."""
        source = "Set i /1*%size%/;\nSet j /1*%size%/;"
        macros = {"size": "10"}
        result = expand_macros(source, macros)
        assert result == "Set i /1*10/;\nSet j /1*10/;"

    def test_unknown_macro_unchanged(self):
        """Unknown macros are left as-is."""
        source = "Set i /1*%unknown%/;"
        macros = {"size": "10"}
        result = expand_macros(source, macros)
        assert result == "Set i /1*%unknown%/;"

    def test_empty_macros(self):
        """Empty macro dict leaves source unchanged."""
        source = "Set i /1*%size%/;"
        result = expand_macros(source, {})
        assert result == "Set i /1*%size%/;"

    def test_macro_with_special_chars_in_value(self):
        """Macro values with special characters are expanded correctly."""
        source = "Parameter p /%name%/;"
        macros = {"name": "test-value_123"}
        result = expand_macros(source, macros)
        assert result == "Parameter p /test-value_123/;"

    def test_case_sensitive_macro_names(self):
        """Macro names are case-sensitive."""
        source = "Set i /1*%SIZE%/;\nSet j /1*%size%/;"
        macros = {"size": "10"}  # lowercase only
        result = expand_macros(source, macros)
        # %SIZE% should remain, %size% should be replaced
        assert "%SIZE%" in result
        assert "Set j /1*10/;" in result

    def test_system_macro_simulation(self):
        """System macros can be added to macros dict."""
        source = "Parameter status /%modelStat.optimal%/;"
        macros = {"modelStat.optimal": "1"}
        result = expand_macros(source, macros)
        assert result == "Parameter status /1/;"


class TestStripConditionalDirectives:
    """Test strip_conditional_directives() function."""

    def test_single_directive(self):
        """Strip a single $if not set directive."""
        source = '$if not set size $set size "10"'
        result = strip_conditional_directives(source)
        assert result == '* [Stripped: $if not set size $set size "10"]'

    def test_preserve_other_lines(self):
        """Other lines remain unchanged."""
        source = """$if not set size $set size "10"
Set i /1*10/;
Variables x;"""
        result = strip_conditional_directives(source)
        lines = result.split("\n")
        assert lines[0].startswith("* [Stripped:")
        assert lines[1] == "Set i /1*10/;"
        assert lines[2] == "Variables x;"

    def test_preserve_line_numbers(self):
        """Line count is preserved (directive replaced with comment)."""
        source = "line1\n$if not set x $set x 1\nline3"
        result = strip_conditional_directives(source)
        assert len(result.split("\n")) == 3

    def test_case_insensitive(self):
        """Directive detection is case-insensitive."""
        source = '$IF NOT SET size $SET size "10"'
        result = strip_conditional_directives(source)
        assert result.startswith("* [Stripped:")

    def test_multiple_directives(self):
        """Multiple directives are all stripped."""
        source = """$if not set size $set size "10"
Set i /1*10/;
$if not set name $set name "test"
Variables x;"""
        result = strip_conditional_directives(source)
        lines = result.split("\n")
        assert lines[0].startswith("* [Stripped:")
        assert lines[1] == "Set i /1*10/;"
        assert lines[2].startswith("* [Stripped:")
        assert lines[3] == "Variables x;"

    def test_empty_source(self):
        """Empty source returns empty string."""
        result = strip_conditional_directives("")
        assert result == ""

    def test_no_directives(self):
        """Source with no directives returns unchanged."""
        source = "Set i /1*10/;\nVariables x;"
        result = strip_conditional_directives(source)
        assert result == source


# Integration test combining all three functions
class TestPreprocessorIntegration:
    """Test the three functions working together."""

    def test_full_preprocessing_flow(self):
        """Test extract -> expand -> strip workflow."""
        source = """$if not set size $set size "10"
Set i /1*%size%/;
Variables x;"""

        # Step 1: Extract macros
        macros = extract_conditional_sets(source)
        assert macros == {"size": "10"}

        # Step 2: Expand macros
        expanded = expand_macros(source, macros)
        assert "Set i /1*10/;" in expanded

        # Step 3: Strip directives
        final = strip_conditional_directives(expanded)
        lines = final.split("\n")
        assert lines[0].startswith("* [Stripped:")
        assert lines[1] == "Set i /1*10/;"
        assert lines[2] == "Variables x;"

    def test_circle_gms_pattern(self):
        """Test pattern found in circle.gms GAMSLib model."""
        # Simplified pattern from circle.gms
        source = """$if not set TESTTOL $set TESTTOL 1e-6
Parameter tol /%TESTTOL%/;"""

        macros = extract_conditional_sets(source)
        expanded = expand_macros(source, macros)
        final = strip_conditional_directives(expanded)

        assert "Parameter tol /1e-6/;" in final

    def test_maxmin_gms_pattern(self):
        """Test pattern found in maxmin.gms GAMSLib model."""
        # Simplified pattern from maxmin.gms
        source = """$if not set N $set N 10
Set i /1*%N%/;"""

        macros = extract_conditional_sets(source)
        assert macros == {"N": "10"}

        expanded = expand_macros(source, macros)
        assert "Set i /1*10/;" in expanded

        final = strip_conditional_directives(expanded)
        assert "Set i /1*10/;" in final
