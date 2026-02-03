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
    join_multiline_equations,
    preprocess_gams_file,
    preprocess_text,
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
        test_file.write_text("""$title Test Model
$if not set N $set N 10
Set i /1*%N%/;
Variables x;""")

        result = preprocess_gams_file(test_file)

        # Check that preprocessing steps were applied
        assert "* [Stripped: $title Test Model]" in result
        assert "* [Stripped: $if not set N $set N 10]" in result
        assert "Set i /1*10/;" in result  # Macro expanded
        assert "Variables x;" in result

    def test_preprocessing_with_eolcom(self, tmp_path: Path):
        """Test preprocessing a file with $eolCom directive."""
        test_file = tmp_path / "test.gms"
        test_file.write_text("""$eolCom //
Set i /1*10/;  // This is a comment
Variables x;   // Another comment""")

        result = preprocess_gams_file(test_file)

        # $eolCom directive should be stripped
        assert "* [Stripped: $eolCom //]" in result
        # Comments should remain (handled by grammar)
        assert "// This is a comment" in result
        assert "// Another comment" in result

    def test_preprocessing_with_multiple_macros(self, tmp_path: Path):
        """Test preprocessing with multiple macro definitions."""
        test_file = tmp_path / "test.gms"
        test_file.write_text("""$if not set N $set N 10
$if not set M $set M 5
Set i /1*%N%/;
Set j /1*%M%/;
Parameter p(%N%, %M%);""")

        result = preprocess_gams_file(test_file)

        # All macros should be expanded
        assert "Set i /1*10/;" in result
        assert "Set j /1*5/;" in result
        assert "Parameter p(10, 5);" in result

    def test_preprocessing_with_ontext_offtext(self, tmp_path: Path):
        """Test preprocessing with comment blocks."""
        test_file = tmp_path / "test.gms"
        test_file.write_text("""Set i /1*10/;
$ontext
This is a documentation block
that should be removed
$offtext
Variables x;""")

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
        test_file.write_text("""$title Test
$if not set N $set N 10
Set i /1*%N%/;
Variables x;""")

        result = preprocess_gams_file(test_file)
        lines = result.split("\n")

        # Should have same number of lines (directives replaced with comments)
        assert len(lines) == 4

    def test_preprocessing_with_includes(self, tmp_path: Path):
        """Test preprocessing with $include directives."""
        # Create an included file
        included = tmp_path / "data.gms"
        included.write_text("""$if not set size $set size 5
Set k /1*%size%/;""")

        # Create main file
        main_file = tmp_path / "main.gms"
        main_file.write_text("""$title Main Model
$include data.gms
Variables x;""")

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
        included.write_text("""$if not set N $set N 10
$if not set tol $set tol 1e-6""")

        # Create main file
        main_file = tmp_path / "main.gms"
        main_file.write_text("""$title Complex Model
$eolCom //
$include defs.gms
Set i /1*%N%/;  // Index set
Parameter epsilon /%tol%/;  // Tolerance
$ontext
Documentation block
$offtext
Variables x;""")

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
        test_file.write_text("""$eolCom //
$if not set points $set points 13
Set k number of points / 1*%points% /;""")

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
        test_file.write_text("""$if not set nh $set nh 50
Set nh / i0*i%nh% /;""")

        result = preprocess_gams_file(test_file)

        # Macro should be expanded
        assert "Set nh / i0*i50 /;" in result
        assert "%nh%" not in result

    def test_elec_gms_pattern(self, tmp_path: Path):
        """Test dynamic set range from elec.gms: i1*i%np%."""
        test_file = tmp_path / "elec.gms"
        test_file.write_text("""$if not set np $set np 50
Set i 'electrons' /i1*i%np%/;""")

        result = preprocess_gams_file(test_file)

        # Macro should be expanded
        assert "Set i 'electrons' /i1*i50/;" in result
        assert "%np%" not in result

    def test_polygon_gms_pattern(self, tmp_path: Path):
        """Test dynamic set range from polygon.gms: i1*i%nv%."""
        test_file = tmp_path / "polygon.gms"
        test_file.write_text("""$if not set nv $set nv 5
Set i 'sides' / i1*i%nv% /;""")

        result = preprocess_gams_file(test_file)

        # Macro should be expanded
        assert "Set i 'sides' / i1*i5 /;" in result
        assert "%nv%" not in result

    def test_zero_indexed_range(self, tmp_path: Path):
        """Test zero-indexed dynamic range (i0*i%n%)."""
        test_file = tmp_path / "test.gms"
        test_file.write_text("""$set n 10
Set i / i0*i%n% /;""")

        result = preprocess_gams_file(test_file)

        assert "Set i / i0*i10 /;" in result

    def test_one_indexed_range(self, tmp_path: Path):
        """Test one-indexed dynamic range (i1*i%n%)."""
        test_file = tmp_path / "test.gms"
        test_file.write_text("""$set n 100
Set i / i1*i%n% /;""")

        result = preprocess_gams_file(test_file)

        assert "Set i / i1*i100 /;" in result

    def test_custom_prefix_range(self, tmp_path: Path):
        """Test dynamic range with custom prefix (node1*node%count%)."""
        test_file = tmp_path / "test.gms"
        test_file.write_text("""$set count 25
Set nodes / node1*node%count% /;""")

        result = preprocess_gams_file(test_file)

        assert "Set nodes / node1*node25 /;" in result

    def test_multiple_dynamic_sets(self, tmp_path: Path):
        """Test multiple sets with different dynamic ranges."""
        test_file = tmp_path / "test.gms"
        test_file.write_text("""$set m 10
$set n 20
Set i / i1*i%m% /;
Set j / j1*j%n% /;""")

        result = preprocess_gams_file(test_file)

        assert "Set i / i1*i10 /;" in result
        assert "Set j / j1*j20 /;" in result

    def test_nested_macro_reference(self, tmp_path: Path):
        """Test macro referencing another macro."""
        test_file = tmp_path / "test.gms"
        test_file.write_text("""$set base 10
$set derived %base%
Set i / i1*i%derived% /;""")

        result = preprocess_gams_file(test_file)

        # Both macros should be expanded
        assert "Set i / i1*i10 /;" in result


class TestJoinMultilineEquations:
    """Test join_multiline_equations() function (Issue #561)."""

    def test_single_line_equation_unchanged(self):
        """Single-line equations should remain unchanged."""
        source = "eq.. x + y =e= 10;"
        result = join_multiline_equations(source)
        assert result == source

    def test_multiline_equation_with_plus_continuation(self):
        """Equation with + continuation on next line."""
        source = """labc(tm).. sum((p,s), labor(p,tm)*xcrop(p,s))
            + sum(r, llab(tm,r)*xliver(r))
           =l= flab(tm) + tlab(tm);"""
        result = join_multiline_equations(source)
        # Should be joined into single line
        assert ".." in result
        assert "=l=" in result
        assert result.count("\n") < source.count("\n")
        # Verify the equation is properly joined
        assert "sum((p,s), labor(p,tm)*xcrop(p,s)) + sum(r, llab(tm,r)*xliver(r))" in result

    def test_multiline_equation_with_minus_continuation(self):
        """Equation with - continuation on next line."""
        source = """cost.. totalcost
            - savings
            =e= 100;"""
        result = join_multiline_equations(source)
        assert "totalcost - savings =e= 100;" in result

    def test_multiline_equation_with_relational_on_new_line(self):
        """Equation with relational operator on its own line."""
        source = """balance(i).. supply(i) + imports(i)
            =g=
            demand(i);"""
        result = join_multiline_equations(source)
        assert "supply(i) + imports(i) =g= demand(i);" in result

    def test_multiple_continuation_lines(self):
        """Equation spanning multiple continuation lines."""
        source = """income.. yfarm =e= revenue
            + vsc*sum(dr, cons(dr))
            - labcost
            - rationr
            - vetcost;"""
        result = join_multiline_equations(source)
        # All lines should be joined
        lines = [line for line in result.split("\n") if line.strip()]
        assert len(lines) == 1
        assert "=e=" in lines[0]
        assert lines[0].endswith(";")

    def test_comments_preserved_in_equation(self):
        """Comments during multi-line equation should be preserved."""
        source = """eq.. x
* this is a comment
            + y =e= z;"""
        result = join_multiline_equations(source)
        assert "* this is a comment" in result

    def test_multiple_equations(self):
        """Multiple equations in sequence."""
        source = """eq1.. x
            + y =e= 10;
eq2.. a
            - b =g= 0;"""
        result = join_multiline_equations(source)
        assert "x + y =e= 10;" in result
        assert "a - b =g= 0;" in result

    def test_non_equation_code_unchanged(self):
        """Non-equation code should remain unchanged."""
        source = """Set i / a, b /;
Parameter p(i);
Variable x(i);"""
        result = join_multiline_equations(source)
        assert result == source

    def test_equation_followed_by_model_statement(self):
        """Equation followed by Model statement should not merge them."""
        source = """eq.. x + y
            =e= 10;
Model m / all /;"""
        result = join_multiline_equations(source)
        assert "x + y =e= 10;" in result
        assert "Model m / all /;" in result

    def test_agreste_style_equation(self):
        """Test actual equation pattern from agreste.gms model."""
        source = """labc(tm)..     sum((p,s)$ps(p,s), labor(p,tm)*xcrop(p,s))
            +  sum(r, llab(tm,r)*xliver(r))
           =l= flab(tm) + tlab(tm) + dpm*plab;"""
        result = join_multiline_equations(source)
        # Should be a single line equation
        lines = [line for line in result.split("\n") if line.strip()]
        assert len(lines) == 1
        assert "labc(tm).." in lines[0]
        assert "=l=" in lines[0]
        assert lines[0].endswith(";")

    def test_parenthesized_domain_equation(self):
        """Equation with domain in parentheses."""
        source = """mbalc(c)..     sum((s,p), yield(p,c,s)*xcrop(p,s))/1000
           =g= sales(c) + sum(dr, cbndl(c,dr)*cons(dr));"""
        result = join_multiline_equations(source)
        lines = [line for line in result.split("\n") if line.strip()]
        assert len(lines) == 1
        assert "mbalc(c).." in lines[0]

    def test_equation_with_conditional(self):
        """Equation with $ conditional operator."""
        source = """eq(i)$valid(i).. x(i)
            + y(i) =e= 0;"""
        result = join_multiline_equations(source)
        assert "eq(i)$valid(i).." in result
        assert "x(i) + y(i) =e= 0;" in result


class TestPreprocessText:
    """Tests for preprocess_text() function (Sprint 17 Day 8 - Issue #614)."""

    def test_set_directive_expansion(self):
        """Test $set directive and %variable% expansion in set range."""
        source = """$set N 5
Set i / i1*i%N% /;"""
        result = preprocess_text(source)
        assert "i1*i5" in result
        assert "%N%" not in result

    def test_multiple_set_directives(self):
        """Test multiple $set directives."""
        source = """$set X 10
$set Y 20
Parameter a / %X% /, b / %Y% /;"""
        result = preprocess_text(source)
        assert "/ 10 /" in result
        assert "/ 20 /" in result

    def test_set_directive_in_expression(self):
        """Test %var% expansion in expressions."""
        source = """$set N 100
Parameter scale / %N% /;
Scalar factor / 1.0 / %N% /;"""
        result = preprocess_text(source)
        assert "%N%" not in result
        # N should be expanded to 100 in the actual code lines (not just in stripped comment)
        lines = [line for line in result.split("\n") if not line.strip().startswith("*")]
        code_text = "\n".join(lines)
        assert "Parameter scale / 100 /" in code_text
        assert "Scalar factor / 1.0 / 100 /" in code_text

    def test_include_directive_stripped(self):
        """Test that $include directives are stripped to comments."""
        source = """$set N 5
$include "somefile.gms"
Set i / i1*i%N% /;"""
        result = preprocess_text(source)
        # $include should be converted to comment (stripped marker)
        lines = result.split("\n")
        include_line = [line for line in lines if "somefile.gms" in line][0]
        assert include_line.startswith("* [Stripped:")
        # But %N% should still be expanded
        assert "i1*i5" in result

    def test_batinclude_directive_stripped(self):
        """Test that $batInclude directives are stripped to comments."""
        source = """$set N 5
$batInclude "somefile.gms" arg1 arg2
Set i / i1*i%N% /;"""
        result = preprocess_text(source)
        # $batInclude should be converted to comment (stripped marker)
        lines = result.split("\n")
        batinclude_line = [line for line in lines if "somefile.gms" in line][0]
        assert batinclude_line.startswith("* [Stripped:")
        # But %N% should still be expanded
        assert "i1*i5" in result

    def test_conditional_if_set(self):
        """Test $if set conditional processing with block-form conditionals."""
        source = """$set DEBUG 1
$if set DEBUG
Parameter debug_mode / 1 /;
$endif
$if not set DEBUG
Parameter debug_mode / 0 /;
$endif"""
        result = preprocess_text(source)
        # Since DEBUG is set, the "$if set DEBUG" branch content should be kept
        # and the "$if not set DEBUG" branch content should be removed
        # The kept branch should appear as actual code, not just in a comment
        lines = [line for line in result.split("\n") if not line.strip().startswith("*")]
        code_text = "\n".join(lines)
        assert "debug_mode / 1 /" in code_text
        # The "not set" branch should NOT appear as code (only in stripped comments)
        assert "debug_mode / 0 /" not in code_text

    def test_unsupported_directives_stripped(self):
        """Test that unsupported directives are stripped."""
        source = """$title My Model
$ontext
This is a comment block
$offtext
Set i / a, b, c /;"""
        result = preprocess_text(source)
        # $title should be converted to comment (stripped marker)
        lines = result.split("\n")
        title_line = lines[0]
        assert title_line.startswith("* [Stripped:")
        # Set statement should remain
        assert "Set i" in result

    def test_preserves_line_numbers_for_stripped_include(self):
        """Test that stripped includes preserve line numbers."""
        source = """Line1
$include "file.gms"
Line3"""
        result = preprocess_text(source)
        lines = result.split("\n")
        # Should have same number of lines
        assert len(lines) == 3
        # Line 2 should be a comment
        assert lines[1].startswith("*")

    def test_empty_source(self):
        """Test with empty source."""
        result = preprocess_text("")
        assert result == ""

    def test_no_preprocessing_needed(self):
        """Test source that doesn't need preprocessing."""
        source = """Set i / a, b, c /;
Variable x(i);"""
        result = preprocess_text(source)
        # Should be essentially unchanged (may have normalized whitespace)
        assert "Set i" in result
        assert "Variable x" in result

    def test_inline_include_directive_stripped(self):
        """Test that inline include directives (after $if) are also stripped."""
        source = """$set N 5
$if set X $include "conditional.gms"
$if not set Y $batInclude "another.gms" arg1
Set i / i1*i%N% /;"""
        result = preprocess_text(source)
        # Both inline includes should be stripped to comments
        lines = result.split("\n")
        # Should preserve line count
        assert len(lines) == 4
        # Lines with include directives should be comments
        conditional_include = [line for line in lines if "conditional.gms" in line][0]
        assert conditional_include.strip().startswith("* [Stripped:")
        batinclude_line = [line for line in lines if "another.gms" in line][0]
        assert batinclude_line.strip().startswith("* [Stripped:")
        # %N% should still be expanded in non-include lines
        assert "i1*i5" in result

    def test_include_in_quoted_string_not_stripped(self):
        """Test that $include inside quoted strings is NOT stripped."""
        source = """Set i / i1, i2 /;
Parameter p / "contains $include text" /;
Scalar s / 1 /;"""
        result = preprocess_text(source)
        # The line with $include in quotes should NOT be stripped
        lines = result.split("\n")
        param_line = [line for line in lines if "Parameter p" in line][0]
        # Should still contain the original quoted text, not be a stripped comment
        assert "Parameter p" in param_line
        assert '"contains $include text"' in param_line
        assert not param_line.strip().startswith("* [Stripped:")

    def test_include_in_comment_not_stripped(self):
        """Test that $include in comment lines is left alone."""
        source = """* This comment mentions $include for documentation
Set i / i1, i2 /;"""
        result = preprocess_text(source)
        lines = result.split("\n")
        # Comment line should be unchanged (not double-stripped)
        comment_line = lines[0]
        assert comment_line.startswith("* This comment mentions $include")
        # Should NOT have [Stripped: marker
        assert "[Stripped:" not in comment_line
