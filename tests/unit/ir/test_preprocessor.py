"""Tests for GAMS file preprocessing ($include directive handling)."""

import pytest

from src.ir.preprocessor import (
    CircularIncludeError,
    IncludeDepthExceededError,
    preprocess_gams_file,
    preprocess_includes,
    strip_unsupported_directives,
)


class TestSimpleInclude:
    """Tests for basic $include functionality."""

    def test_simple_include(self, tmp_path):
        """Test simple file inclusion."""
        # Create main file
        main_file = tmp_path / "main.gms"
        main_file.write_text("Sets i /i1, i2/;\n$include data.inc\nVariables x(i);")

        # Create included file
        inc_file = tmp_path / "data.inc"
        inc_file.write_text("Parameters a(i) /i1 1.0, i2 2.0/;")

        # Preprocess
        result = preprocess_includes(main_file)

        # Check that include was expanded
        assert "BEGIN INCLUDE: data.inc" in result
        assert "END INCLUDE: data.inc" in result
        assert "Parameters a(i)" in result
        assert "Sets i" in result
        assert "Variables x(i)" in result

    def test_include_with_quoted_filename(self, tmp_path):
        """Test $include with quoted filename (spaces allowed)."""
        # Create main file
        main_file = tmp_path / "main.gms"
        main_file.write_text('Sets i;\n$include "my data.inc"\nVariables x;')

        # Create included file with spaces in name
        inc_file = tmp_path / "my data.inc"
        inc_file.write_text("Parameters a /1.0/;")

        # Preprocess
        result = preprocess_includes(main_file)

        # Check that include was expanded
        assert "BEGIN INCLUDE: my data.inc" in result
        assert "Parameters a" in result

    def test_include_case_insensitive(self, tmp_path):
        """Test that $include is case-insensitive."""
        # Create main file with various cases
        main_file = tmp_path / "main.gms"
        main_file.write_text(
            "Sets i;\n$INCLUDE data1.inc\n$Include data2.inc\n$include data3.inc\n"
        )

        # Create included files
        (tmp_path / "data1.inc").write_text("Parameters a1;")
        (tmp_path / "data2.inc").write_text("Parameters a2;")
        (tmp_path / "data3.inc").write_text("Parameters a3;")

        # Preprocess
        result = preprocess_includes(main_file)

        # All should be included
        assert "Parameters a1" in result
        assert "Parameters a2" in result
        assert "Parameters a3" in result


class TestNestedIncludes:
    """Tests for nested $include directives."""

    def test_nested_includes_3_levels(self, tmp_path):
        """Test 3-level nested includes."""
        # Level 1: main file
        main_file = tmp_path / "main.gms"
        main_file.write_text("Sets i;\n$include level1.inc\nVariables x;")

        # Level 2
        (tmp_path / "level1.inc").write_text("Parameters a;\n$include level2.inc\nParameters b;")

        # Level 3
        (tmp_path / "level2.inc").write_text("Parameters c;")

        # Preprocess
        result = preprocess_includes(main_file)

        # All levels should be present
        assert "Sets i" in result
        assert "Parameters a" in result
        assert "Parameters b" in result
        assert "Parameters c" in result
        assert "Variables x" in result

    def test_nested_includes_10_levels(self, tmp_path):
        """Test deep nesting (10 levels) - should work with default limit."""
        # Create chain of 10 files
        for i in range(10):
            if i == 0:
                content = f"* Level 0\n$include level{i + 1}.inc\n"
            elif i == 9:
                content = f"* Level {i}\n"
            else:
                content = f"* Level {i}\n$include level{i + 1}.inc\n"

            (tmp_path / f"level{i}.inc").write_text(content)

        # Preprocess
        result = preprocess_includes(tmp_path / "level0.inc")

        # All levels should be present
        for i in range(10):
            assert f"Level {i}" in result


class TestCircularIncludes:
    """Tests for circular include detection."""

    def test_direct_circular_include(self, tmp_path):
        """Test detection of direct circular include (A includes A)."""
        # File includes itself
        circ_file = tmp_path / "circular.inc"
        circ_file.write_text("Sets i;\n$include circular.inc\n")

        # Should raise CircularIncludeError
        with pytest.raises(CircularIncludeError) as exc_info:
            preprocess_includes(circ_file)

        # Check error message shows the chain
        assert "circular.inc" in str(exc_info.value)
        assert len(exc_info.value.chain) == 2  # [circular.inc, circular.inc]

    def test_indirect_circular_include(self, tmp_path):
        """Test detection of indirect circular include (A → B → A)."""
        # A includes B
        (tmp_path / "a.inc").write_text("Sets i;\n$include b.inc\n")

        # B includes A (creates cycle)
        (tmp_path / "b.inc").write_text("Parameters p;\n$include a.inc\n")

        # Should raise CircularIncludeError
        with pytest.raises(CircularIncludeError) as exc_info:
            preprocess_includes(tmp_path / "a.inc")

        # Check error message shows the full chain
        error_msg = str(exc_info.value)
        assert "a.inc" in error_msg
        assert "b.inc" in error_msg
        assert len(exc_info.value.chain) == 3  # [a.inc, b.inc, a.inc]

    def test_long_circular_chain(self, tmp_path):
        """Test detection of circular include with long chain (A → B → C → A)."""
        # A → B → C → A
        (tmp_path / "a.inc").write_text("$include b.inc\n")
        (tmp_path / "b.inc").write_text("$include c.inc\n")
        (tmp_path / "c.inc").write_text("$include a.inc\n")

        # Should raise CircularIncludeError
        with pytest.raises(CircularIncludeError) as exc_info:
            preprocess_includes(tmp_path / "a.inc")

        # Chain should be [a.inc, b.inc, c.inc, a.inc]
        assert len(exc_info.value.chain) == 4


class TestRelativePaths:
    """Tests for relative path resolution."""

    def test_relative_path_to_parent_directory(self, tmp_path):
        """Test include with parent directory reference (..)."""
        # Create directory structure
        subdir = tmp_path / "models"
        subdir.mkdir()

        # Main file in subdir
        main_file = subdir / "main.gms"
        main_file.write_text("Sets i;\n$include ../common.inc\n")

        # Common file in parent dir
        common_file = tmp_path / "common.inc"
        common_file.write_text("Parameters shared;")

        # Preprocess
        result = preprocess_includes(main_file)

        # Should find the file in parent directory
        assert "Parameters shared" in result

    def test_relative_path_to_sibling_directory(self, tmp_path):
        """Test include from one directory to a sibling directory."""
        # Create directory structure
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()

        # Main file in dir1
        main_file = dir1 / "main.gms"
        main_file.write_text("Sets i;\n$include ../dir2/data.inc\n")

        # Data file in dir2
        data_file = dir2 / "data.inc"
        data_file.write_text("Parameters p;")

        # Preprocess
        result = preprocess_includes(main_file)

        # Should find the file in sibling directory
        assert "Parameters p" in result

    def test_relative_path_in_nested_subdirectory(self, tmp_path):
        """Test include with nested subdirectory path."""
        # Create directory structure
        subdir = tmp_path / "sub1" / "sub2"
        subdir.mkdir(parents=True)

        # Main file at root
        main_file = tmp_path / "main.gms"
        main_file.write_text("Sets i;\n$include sub1/sub2/data.inc\n")

        # Data file in nested subdir
        data_file = subdir / "data.inc"
        data_file.write_text("Parameters p;")

        # Preprocess
        result = preprocess_includes(main_file)

        # Should find the file in nested subdirectory
        assert "Parameters p" in result

    def test_absolute_path(self, tmp_path):
        """Test include with absolute path."""
        # Create main file
        main_file = tmp_path / "main.gms"

        # Create data file
        data_file = tmp_path / "data.inc"
        data_file.write_text("Parameters p;")

        # Use absolute path in include
        main_file.write_text(f"Sets i;\n$include {data_file}\n")

        # Preprocess
        result = preprocess_includes(main_file)

        # Should work with absolute path
        assert "Parameters p" in result


class TestErrorHandling:
    """Tests for error handling."""

    def test_missing_file_error(self, tmp_path):
        """Test error when included file doesn't exist."""
        # Create main file that includes non-existent file
        main_file = tmp_path / "main.gms"
        main_file.write_text("Sets i;\n$include missing.inc\n")

        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError) as exc_info:
            preprocess_includes(main_file)

        # Error should mention the missing file
        assert "missing.inc" in str(exc_info.value)

    def test_missing_file_in_nested_include(self, tmp_path):
        """Test error when nested included file doesn't exist."""
        # Create main file
        main_file = tmp_path / "main.gms"
        main_file.write_text("Sets i;\n$include level1.inc\n")

        # Level 1 includes missing file
        (tmp_path / "level1.inc").write_text("$include missing.inc\n")

        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError) as exc_info:
            preprocess_includes(main_file)

        # Error should show where it was referenced from
        error_msg = str(exc_info.value)
        assert "missing.inc" in error_msg
        assert "Referenced from" in error_msg

    def test_depth_limit_exceeded(self, tmp_path):
        """Test that depth limit is enforced."""
        # Create chain that exceeds limit
        for i in range(15):
            content = f"* Level {i}\n"
            if i < 14:
                content += f"$include level{i + 1}.inc\n"
            (tmp_path / f"level{i}.inc").write_text(content)

        # Should raise IncludeDepthExceededError with max_depth=10
        with pytest.raises(IncludeDepthExceededError) as exc_info:
            preprocess_includes(tmp_path / "level0.inc", max_depth=10)

        # Check error details
        assert exc_info.value.max_depth == 10
        assert exc_info.value.depth >= 10

    def test_main_file_not_found(self, tmp_path):
        """Test error when main file doesn't exist."""
        # Try to preprocess non-existent file
        non_existent = tmp_path / "does_not_exist.gms"

        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError):
            preprocess_includes(non_existent)


class TestPreprocessGamsFile:
    """Tests for the preprocess_gams_file wrapper function."""

    def test_with_path_object(self, tmp_path):
        """Test preprocess_gams_file with Path object."""
        # Create test files
        main_file = tmp_path / "main.gms"
        main_file.write_text("Sets i;\n$include data.inc\n")
        (tmp_path / "data.inc").write_text("Parameters p;")

        # Call with Path object
        result = preprocess_gams_file(main_file)

        # Should work
        assert "Parameters p" in result

    def test_with_string_path(self, tmp_path):
        """Test preprocess_gams_file with string path."""
        # Create test files
        main_file = tmp_path / "main.gms"
        main_file.write_text("Sets i;\n$include data.inc\n")
        (tmp_path / "data.inc").write_text("Parameters p;")

        # Call with string path
        result = preprocess_gams_file(str(main_file))

        # Should work
        assert "Parameters p" in result


class TestIncludeBoundaryComments:
    """Tests for debug comments marking include boundaries."""

    def test_boundary_comments_present(self, tmp_path):
        """Test that BEGIN/END INCLUDE comments are added."""
        # Create test files
        main_file = tmp_path / "main.gms"
        main_file.write_text("Sets i;\n$include data.inc\nVariables x;")
        (tmp_path / "data.inc").write_text("Parameters p;")

        # Preprocess
        result = preprocess_includes(main_file)

        # Should have boundary comments
        assert "BEGIN INCLUDE: data.inc" in result
        assert "END INCLUDE: data.inc" in result

    def test_boundary_comments_order(self, tmp_path):
        """Test that boundary comments are in correct order."""
        # Create test files
        main_file = tmp_path / "main.gms"
        main_file.write_text("Sets i;\n$include data.inc\nVariables x;")
        (tmp_path / "data.inc").write_text("Parameters p;")

        # Preprocess
        result = preprocess_includes(main_file)

        # BEGIN should come before content, END after
        begin_pos = result.index("BEGIN INCLUDE: data.inc")
        content_pos = result.index("Parameters p")
        end_pos = result.index("END INCLUDE: data.inc")

        assert begin_pos < content_pos < end_pos


class TestMultipleIncludes:
    """Tests for multiple includes in the same file."""

    def test_multiple_includes_in_sequence(self, tmp_path):
        """Test multiple $include directives in sequence."""
        # Create main file with multiple includes
        main_file = tmp_path / "main.gms"
        main_file.write_text(
            "Sets i;\n$include data1.inc\n$include data2.inc\n$include data3.inc\nVariables x;"
        )

        # Create included files
        (tmp_path / "data1.inc").write_text("Parameters a;")
        (tmp_path / "data2.inc").write_text("Parameters b;")
        (tmp_path / "data3.inc").write_text("Parameters c;")

        # Preprocess
        result = preprocess_includes(main_file)

        # All should be included in order
        assert "Sets i" in result
        assert "Parameters a" in result
        assert "Parameters b" in result
        assert "Parameters c" in result
        assert "Variables x" in result

        # Check order
        assert result.index("Parameters a") < result.index("Parameters b")
        assert result.index("Parameters b") < result.index("Parameters c")


class TestStripUnsupportedDirectives:
    """Tests for stripping unsupported compiler directives."""

    def test_strip_title_directive(self):
        """Test that $title directive is stripped."""
        source = "$title My Model\nVariables x;\nEquations eq;"
        result = strip_unsupported_directives(source)

        # $title line should be replaced with comment
        assert "* [Stripped: $title My Model]" in result
        assert "Variables x;" in result
        assert "Equations eq;" in result
        # Original directive line should not be parseable (starts with comment now)
        lines = result.split("\n")
        assert lines[0].startswith("*")

    def test_strip_title_case_insensitive(self):
        """Test that $title is case-insensitive."""
        sources = [
            "$title My Model",
            "$TITLE My Model",
            "$Title My Model",
            "$TiTlE My Model",
        ]

        for source in sources:
            result = strip_unsupported_directives(source)
            assert "* [Stripped:" in result
            # Line should start with comment
            assert result.startswith("*")

    def test_strip_ontext_offtext_block(self):
        """Test that $ontext/$offtext comment blocks are stripped."""
        source = """Variables x;
$ontext
This is a comment block
that spans multiple lines
$offtext
Equations eq;"""

        result = strip_unsupported_directives(source)

        # Content should be commented
        assert "* [Stripped: $ontext]" in result
        assert "* [Stripped: $offtext]" in result
        assert "* This is a comment block" in result
        assert "* that spans multiple lines" in result

        # Regular code preserved
        assert "Variables x;" in result
        assert "Equations eq;" in result

    def test_strip_eolcom_directive(self):
        """Test that $eolcom directive is stripped."""
        source = "$eolcom #\nVariables x; # This is a comment"
        result = strip_unsupported_directives(source)

        # $eolcom line should be replaced with comment
        assert "* [Stripped: $eolcom #]" in result
        lines = result.split("\n")
        assert lines[0].startswith("*")

    def test_preserve_line_numbers(self):
        """Test that line numbers are preserved after stripping."""
        source = """Sets i;
$title Model
Parameters p;
$ontext
Comment
$offtext
Variables x;"""

        result = strip_unsupported_directives(source)
        result_lines = result.split("\n")
        source_lines = source.split("\n")

        # Same number of lines
        assert len(result_lines) == len(source_lines)

        # Line 0: preserved
        assert result_lines[0] == "Sets i;"
        # Line 1: stripped to comment
        assert result_lines[1].startswith("* [Stripped:")
        # Line 2: preserved
        assert result_lines[2] == "Parameters p;"

    def test_mixed_directives_and_code(self):
        """Test file with mixed directives and GAMS code."""
        source = """$title Complex Model
Sets i /i1, i2/;
$ontext
Documentation
$offtext
Parameters p(i);
Variables x, y;"""

        result = strip_unsupported_directives(source)

        # Directives converted to comments
        assert "* [Stripped: $title Complex Model]" in result
        assert "* [Stripped: $ontext]" in result
        assert "* [Stripped: $offtext]" in result

        # Code preserved
        assert "Sets i /i1, i2/;" in result
        assert "Parameters p(i);" in result
        assert "Variables x, y;" in result

    def test_empty_title(self):
        """Test $title with no text."""
        source = "$title\nVariables x;"
        result = strip_unsupported_directives(source)

        assert "* [Stripped: $title]" in result
        lines = result.split("\n")
        assert lines[0].startswith("*")

    def test_title_with_special_characters(self):
        """Test $title with special characters."""
        source = "$title Model: x² + y² ≤ 10\nVariables x;"
        result = strip_unsupported_directives(source)

        assert "* [Stripped: $title Model: x² + y² ≤ 10]" in result
        lines = result.split("\n")
        assert lines[0].startswith("*")

    def test_nested_ontext_blocks_not_supported(self):
        """Test that nested $ontext blocks are handled (not nested in GAMS)."""
        source = """$ontext
Outer comment
$ontext
This would be invalid GAMS anyway
$offtext
Variables x;"""

        result = strip_unsupported_directives(source)

        # First $ontext starts block
        # Everything until $offtext is commented
        lines = result.split("\n")
        assert lines[0] == "* [Stripped: $ontext]"
        assert lines[1] == "* Outer comment"
        # Inner $ontext is inside the comment block, so it gets another Stripped marker
        assert lines[2] == "* [Stripped: $ontext]"
        assert lines[3] == "* This would be invalid GAMS anyway"
        assert lines[4] == "* [Stripped: $offtext]"
        assert lines[5] == "Variables x;"

    def test_include_directive_not_stripped(self):
        """Test that $include directive is NOT stripped (handled elsewhere)."""
        source = "$include data.inc\nVariables x;"
        result = strip_unsupported_directives(source)

        # $include should remain untouched
        assert "$include data.inc" in result
        assert "Variables x;" in result

    def test_no_directives_unchanged(self):
        """Test that source without directives is unchanged."""
        source = """Variables x, y, z;
Equations eq1, eq2;
eq1.. x + y =e= z;"""

        result = strip_unsupported_directives(source)

        # Should be identical
        assert result == source


class TestIntegrationWithPreprocessGamsFile:
    """Tests for integration of directive stripping with file preprocessing."""

    def test_title_stripped_in_preprocess_gams_file(self, tmp_path):
        """Test that $title is automatically stripped by preprocess_gams_file."""
        # Create file with $title
        main_file = tmp_path / "main.gms"
        main_file.write_text("$title My Model\nVariables x;\nEquations eq;")

        # Preprocess
        result = preprocess_gams_file(main_file)

        # $title line should be replaced with comment
        assert "* [Stripped: $title My Model]" in result
        assert "Variables x;" in result
        lines = result.split("\n")
        assert lines[0].startswith("*")

    def test_title_and_include_together(self, tmp_path):
        """Test that both $title stripping and $include expansion work together."""
        # Create main file with both directives
        main_file = tmp_path / "main.gms"
        main_file.write_text("$title Main Model\nSets i;\n$include data.inc\nVariables x;")

        # Create included file (also with $title)
        inc_file = tmp_path / "data.inc"
        inc_file.write_text("$title Data File\nParameters p;")

        # Preprocess
        result = preprocess_gams_file(main_file)

        # Both $title directives should be replaced with comments
        assert "* [Stripped: $title Main Model]" in result
        assert "* [Stripped: $title Data File]" in result

        # $include should be expanded
        assert "Parameters p;" in result
        assert "BEGIN INCLUDE: data.inc" in result

        # Regular code preserved
        assert "Sets i;" in result
        assert "Variables x;" in result
