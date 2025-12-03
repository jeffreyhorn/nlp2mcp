"""Unit tests for GAMS preprocessor directive handling.

Tests the three new preprocessor functions added in Sprint 7 Day 1:
- extract_conditional_sets(): Extract defaults from $if not set directives
- expand_macros(): Expand %macro% references
- strip_conditional_directives(): Replace directives with comments

Tests the integrated preprocessing pipeline added in Sprint 7 Day 2:
- preprocess_gams_file(): Full preprocessing pipeline including includes

Based on design from docs/research/preprocessor_directives.md
"""

from pathlib import Path

import pytest

from src.ir.preprocessor import (
    expand_macros,
    extract_conditional_sets,
    preprocess_gams_file,
    strip_conditional_directives,
    strip_unsupported_directives,
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


class TestStripUnsupportedDirectives:
    """Test strip_unsupported_directives() function for $title, $ontext, $eolCom."""

    def test_strip_title_directive(self):
        """Strip $title directive."""
        source = """$title My Model
Set i /1*10/;"""
        result = strip_unsupported_directives(source)
        lines = result.split("\n")
        assert lines[0] == "* [Stripped: $title My Model]"
        assert lines[1] == "Set i /1*10/;"

    def test_strip_eolcom_directive(self):
        """Strip $eolCom directive."""
        source = """$eolCom //
Set i /1*10/;  // This is a comment"""
        result = strip_unsupported_directives(source)
        lines = result.split("\n")
        assert lines[0] == "* [Stripped: $eolCom //]"
        assert lines[1] == "Set i /1*10/;  // This is a comment"

    def test_strip_ontext_offtext_block(self):
        """Strip $ontext/$offtext comment blocks."""
        source = """Set i /1*10/;
$ontext
This is a long comment
that spans multiple lines
$offtext
Variables x;"""
        result = strip_unsupported_directives(source)
        # $ontext/$offtext directives are replaced with stripped markers
        # Content inside is converted to GAMS comments (preserves line numbers)
        assert "* [Stripped: $ontext]" in result
        assert "* [Stripped: $offtext]" in result
        assert "* This is a long comment" in result
        assert "* that spans multiple lines" in result
        assert "Set i /1*10/;" in result
        assert "Variables x;" in result

    def test_strip_multiple_directives(self):
        """Strip multiple unsupported directives."""
        source = """$title Test Model
$eolCom //
Set i /1*10/;
$ontext
Comment block
$offtext
Variables x;"""
        result = strip_unsupported_directives(source)
        assert "* [Stripped: $title Test Model]" in result
        assert "* [Stripped: $eolCom //]" in result
        assert "* [Stripped: $ontext]" in result
        assert "* [Stripped: $offtext]" in result
        assert "* Comment block" in result
        assert "Set i /1*10/;" in result

    def test_case_insensitive_directives(self):
        """Directive detection is case-insensitive."""
        source = "$TITLE My Model\n$EOLCOM //"
        result = strip_unsupported_directives(source)
        assert "* [Stripped: $TITLE My Model]" in result
        assert "* [Stripped: $EOLCOM //]" in result

    def test_preserve_other_lines(self):
        """Lines without directives remain unchanged."""
        source = """Set i /1*10/;
Variables x;
Equations eq;"""
        result = strip_unsupported_directives(source)
        assert result == source

    def test_empty_source(self):
        """Empty source returns empty string."""
        result = strip_unsupported_directives("")
        assert result == ""


class TestPreprocessGamsFile:
    """Test the complete preprocess_gams_file() integration function."""

    def test_basic_preprocessing_without_includes(self, tmp_path: Path):
        """Test preprocessing a simple file without includes."""
        # Create a test file
        test_file = tmp_path / "test.gms"
        test_file.write_text(
            """$title Test Model
$if not set N $set N 10
Set i /1*%N%/;
Variables x;"""
        )

        result = preprocess_gams_file(test_file)

        # Check that preprocessing steps were applied
        assert "* [Stripped: $title Test Model]" in result
        assert "* [Stripped: $if not set N $set N 10]" in result
        assert "Set i /1*10/;" in result  # Macro expanded
        assert "Variables x;" in result

    def test_preprocessing_with_eolcom(self, tmp_path: Path):
        """Test preprocessing a file with $eolCom directive."""
        test_file = tmp_path / "test.gms"
        test_file.write_text(
            """$eolCom //
Set i /1*10/;  // This is a comment
Variables x;   // Another comment"""
        )

        result = preprocess_gams_file(test_file)

        # $eolCom directive should be stripped
        assert "* [Stripped: $eolCom //]" in result
        # Comments should remain (handled by grammar)
        assert "// This is a comment" in result
        assert "// Another comment" in result

    def test_preprocessing_with_multiple_macros(self, tmp_path: Path):
        """Test preprocessing with multiple macro definitions."""
        test_file = tmp_path / "test.gms"
        test_file.write_text(
            """$if not set N $set N 10
$if not set M $set M 5
Set i /1*%N%/;
Set j /1*%M%/;
Parameter p(%N%, %M%);"""
        )

        result = preprocess_gams_file(test_file)

        # All macros should be expanded
        assert "Set i /1*10/;" in result
        assert "Set j /1*5/;" in result
        assert "Parameter p(10, 5);" in result

    def test_preprocessing_with_ontext_offtext(self, tmp_path: Path):
        """Test preprocessing with comment blocks."""
        test_file = tmp_path / "test.gms"
        test_file.write_text(
            """Set i /1*10/;
$ontext
This is a documentation block
that should be removed
$offtext
Variables x;"""
        )

        result = preprocess_gams_file(test_file)

        # Comment block directives should be stripped
        assert "* [Stripped: $ontext]" in result
        assert "* [Stripped: $offtext]" in result
        # Content converted to comments (line numbers preserved)
        assert "* This is a documentation block" in result
        # Code should remain
        assert "Set i /1*10/;" in result
        assert "Variables x;" in result

    def test_preprocessing_preserves_line_structure(self, tmp_path: Path):
        """Test that preprocessing preserves line structure for error reporting."""
        test_file = tmp_path / "test.gms"
        test_file.write_text(
            """$title Test
$if not set N $set N 10
Set i /1*%N%/;
Variables x;"""
        )

        result = preprocess_gams_file(test_file)
        lines = result.split("\n")

        # Should have same number of lines (directives replaced with comments)
        assert len(lines) == 4

    def test_preprocessing_with_includes(self, tmp_path: Path):
        """Test preprocessing with $include directives."""
        # Create an included file
        included = tmp_path / "data.gms"
        included.write_text(
            """$if not set size $set size 5
Set k /1*%size%/;"""
        )

        # Create main file
        main_file = tmp_path / "main.gms"
        main_file.write_text(
            """$title Main Model
$include data.gms
Variables x;"""
        )

        result = preprocess_gams_file(main_file)

        # Include should be expanded
        assert "$include" not in result
        # Macros from included file should be expanded
        assert "Set k /1*5/;" in result
        # Main file content preserved
        assert "* [Stripped: $title Main Model]" in result
        assert "Variables x;" in result

    def test_preprocessing_complex_integration(self, tmp_path: Path):
        """Test preprocessing with all features combined."""
        # Create included file with macros
        included = tmp_path / "defs.gms"
        included.write_text(
            """$if not set N $set N 10
$if not set tol $set tol 1e-6"""
        )

        # Create main file
        main_file = tmp_path / "main.gms"
        main_file.write_text(
            """$title Complex Model
$eolCom //
$include defs.gms
Set i /1*%N%/;  // Index set
Parameter epsilon /%tol%/;  // Tolerance
$ontext
Documentation block
$offtext
Variables x;"""
        )

        result = preprocess_gams_file(main_file)

        # All preprocessing applied correctly
        assert "* [Stripped: $title Complex Model]" in result
        assert "* [Stripped: $eolCom //]" in result
        assert "$include" not in result
        assert "Set i /1*10/;" in result
        assert "Parameter epsilon /1e-6/;" in result
        assert "* [Stripped: $ontext]" in result
        assert "* [Stripped: $offtext]" in result
        assert "* Documentation block" in result
        assert "// Index set" in result  # Comments preserved
        assert "Variables x;" in result

    def test_accepts_path_or_string(self, tmp_path: Path):
        """Test that preprocess_gams_file accepts both Path and str."""
        test_file = tmp_path / "test.gms"
        test_file.write_text("Set i /1*10/;")

        # Should work with Path
        result1 = preprocess_gams_file(test_file)
        assert "Set i /1*10/;" in result1

        # Should work with string
        result2 = preprocess_gams_file(str(test_file))
        assert "Set i /1*10/;" in result2

        # Results should be identical
        assert result1 == result2

    def test_file_not_found_error(self):
        """Test that FileNotFoundError is raised for non-existent files."""
        with pytest.raises(FileNotFoundError):
            preprocess_gams_file("/nonexistent/file.gms")

    def test_maxmin_gms_real_world_pattern(self, tmp_path: Path):
        """Test pattern from actual maxmin.gms GAMSLib model."""
        test_file = tmp_path / "maxmin.gms"
        test_file.write_text(
            """$eolCom //
$if not set points $set points 13
Set k number of points / 1*%points% /;"""
        )

        result = preprocess_gams_file(test_file)

        # Check preprocessing
        assert "* [Stripped: $eolCom //]" in result
        assert "* [Stripped: $if not set points $set points 13]" in result
        assert "Set k number of points / 1*13 /;" in result


class TestDynamicSetRanges:
    """Test dynamic set range patterns from Tier 2 models (Issue #387)."""

    def test_chain_gms_pattern(self, tmp_path: Path):
        """Test dynamic set range from chain.gms: i0*i%nh%."""
        test_file = tmp_path / "chain.gms"
        test_file.write_text(
            """$if not set nh $set nh 50
Set nh / i0*i%nh% /;"""
        )

        result = preprocess_gams_file(test_file)

        # Macro should be expanded
        assert "Set nh / i0*i50 /;" in result
        assert "%nh%" not in result

    def test_elec_gms_pattern(self, tmp_path: Path):
        """Test dynamic set range from elec.gms: i1*i%np%."""
        test_file = tmp_path / "elec.gms"
        test_file.write_text(
            """$if not set np $set np 50
Set i 'electrons' /i1*i%np%/;"""
        )

        result = preprocess_gams_file(test_file)

        # Macro should be expanded
        assert "Set i 'electrons' /i1*i50/;" in result
        assert "%np%" not in result

    def test_polygon_gms_pattern(self, tmp_path: Path):
        """Test dynamic set range from polygon.gms: i1*i%nv%."""
        test_file = tmp_path / "polygon.gms"
        test_file.write_text(
            """$if not set nv $set nv 5
Set i 'sides' / i1*i%nv% /;"""
        )

        result = preprocess_gams_file(test_file)

        # Macro should be expanded
        assert "Set i 'sides' / i1*i5 /;" in result
        assert "%nv%" not in result

    def test_zero_indexed_range(self, tmp_path: Path):
        """Test zero-indexed dynamic range (i0*i%n%)."""
        test_file = tmp_path / "test.gms"
        test_file.write_text(
            """$set n 10
Set i / i0*i%n% /;"""
        )

        result = preprocess_gams_file(test_file)

        assert "Set i / i0*i10 /;" in result

    def test_one_indexed_range(self, tmp_path: Path):
        """Test one-indexed dynamic range (i1*i%n%)."""
        test_file = tmp_path / "test.gms"
        test_file.write_text(
            """$set n 100
Set i / i1*i%n% /;"""
        )

        result = preprocess_gams_file(test_file)

        assert "Set i / i1*i100 /;" in result

    def test_custom_prefix_range(self, tmp_path: Path):
        """Test dynamic range with custom prefix (node1*node%count%)."""
        test_file = tmp_path / "test.gms"
        test_file.write_text(
            """$set count 25
Set nodes / node1*node%count% /;"""
        )

        result = preprocess_gams_file(test_file)

        assert "Set nodes / node1*node25 /;" in result

    def test_multiple_dynamic_sets(self, tmp_path: Path):
        """Test multiple sets with different dynamic ranges."""
        test_file = tmp_path / "test.gms"
        test_file.write_text(
            """$set m 10
$set n 20
Set i / i1*i%m% /;
Set j / j1*j%n% /;"""
        )

        result = preprocess_gams_file(test_file)

        assert "Set i / i1*i10 /;" in result
        assert "Set j / j1*j20 /;" in result

    def test_nested_macro_reference(self, tmp_path: Path):
        """Test macro referencing another macro."""
        test_file = tmp_path / "test.gms"
        test_file.write_text(
            """$set base 10
$set derived %base%
Set i / i1*i%derived% /;"""
        )

        result = preprocess_gams_file(test_file)

        # Both macros should be expanded
        assert "Set i / i1*i10 /;" in result
