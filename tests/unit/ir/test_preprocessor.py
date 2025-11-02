"""Tests for GAMS file preprocessing ($include directive handling)."""

import pytest

from src.ir.preprocessor import (
    CircularIncludeError,
    IncludeDepthExceededError,
    preprocess_gams_file,
    preprocess_includes,
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
