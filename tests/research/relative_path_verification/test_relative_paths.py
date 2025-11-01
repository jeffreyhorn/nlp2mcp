#!/usr/bin/env python3
"""Test relative path resolution in $include directives.

This test verifies Unknown 1.5 from KNOWN_UNKNOWNS.md:
- How are relative paths in $include resolved?
- Are they relative to the containing file or working directory?
- Do parent directory (..) paths work?
- Are absolute paths supported?
"""

from pathlib import Path

import pytest

from src.ir.parser import parse_model_file


def test_relative_path_from_main():
    """Test that relative paths are resolved from the main file's directory.

    Directory structure:
        relative_path_verification/
            main_relative.gms
            data/
                params.inc

    main_relative.gms includes: data/params.inc
    Should resolve to: <test_dir>/data/params.inc
    """
    test_dir = Path(__file__).parent
    main_file = test_dir / "main_relative.gms"

    print("\nTest: Relative Path from Main File")
    print(f"Main file: {main_file}")

    # Parse should succeed - the file data/params.inc should be found
    model = parse_model_file(str(main_file))

    # Verify parameter 'a' from data/params.inc was loaded
    print(f"  Parameters found: {list(model.params.keys())}")
    assert "a" in model.params, "Parameter 'a' from data/params.inc not found"
    assert model.params["a"].values[()] == 1.0, "Parameter 'a' has wrong value"

    print("✓ Relative path resolved correctly from main file")


def test_nested_relative_path():
    """Test that nested includes resolve paths relative to containing file.

    Directory structure:
        relative_path_verification/
            main_nested.gms
            data/
                params.inc
                more/
                    extra.inc

    main_nested.gms includes: data/params.inc
    params.inc includes: more/extra.inc

    The path 'more/extra.inc' should be resolved relative to params.inc's location
    (i.e., data/more/extra.inc)
    """
    test_dir = Path(__file__).parent
    main_file = test_dir / "main_nested.gms"

    print("\nTest: Nested Relative Paths")
    print(f"Main file: {main_file}")

    model = parse_model_file(str(main_file))

    print(f"  Parameters found: {list(model.params.keys())}")

    # Verify 'a' from data/params.inc
    assert "a" in model.params, "Parameter 'a' from data/params.inc not found"

    # Verify 'b' from data/more/extra.inc
    assert "b" in model.params, "Parameter 'b' from data/more/extra.inc not found"
    assert model.params["b"].values[()] == 2.0, "Parameter 'b' has wrong value"

    print("✓ Nested relative path resolved correctly")


def test_parent_directory_resolution():
    """Test that parent directory (..) paths work correctly.

    Directory structure:
        relative_path_verification/
            main_parent.gms
            subdir/
                child.inc
            shared/
                common.inc

    main_parent.gms includes: subdir/child.inc
    child.inc includes: ../shared/common.inc

    The path '../shared/common.inc' from subdir/child.inc should resolve to
    <test_dir>/shared/common.inc
    """
    test_dir = Path(__file__).parent
    main_file = test_dir / "main_parent.gms"

    print("\nTest: Parent Directory (..) Resolution")
    print(f"Main file: {main_file}")

    model = parse_model_file(str(main_file))

    print(f"  Parameters found: {list(model.params.keys())}")

    # Verify 'child_param' from subdir/child.inc
    assert "child_param" in model.params, "Parameter 'child_param' not found"

    # Verify 'common_param' from shared/common.inc
    assert "common_param" in model.params, "Parameter 'common_param' not found"
    assert model.params["common_param"].values[()] == 99.0

    print("✓ Parent directory (..) path resolved correctly")


def test_absolute_path_resolution():
    """Test that absolute paths work.

    Create a temporary file with absolute path and verify it can be included.
    """
    test_dir = Path(__file__).parent

    # Create a temp file with absolute path include
    abs_include_file = test_dir / "abs_included.inc"
    abs_include_file.write_text("Scalars\n    abs_param /42.0/;")

    main_file = test_dir / "temp_main_abs.gms"
    # Use absolute path in include
    main_file.write_text(f"$include {abs_include_file.absolute()}\nVariables x;")

    try:
        print("\nTest: Absolute Path Resolution")
        print(f"Main file: {main_file}")
        print(f"Absolute include: {abs_include_file.absolute()}")

        model = parse_model_file(str(main_file))

        print(f"  Parameters found: {list(model.params.keys())}")
        assert "abs_param" in model.params, "Parameter 'abs_param' not found"
        assert model.params["abs_param"].values[()] == 42.0

        print("✓ Absolute path resolved correctly")

    finally:
        # Cleanup
        if main_file.exists():
            main_file.unlink()
        if abs_include_file.exists():
            abs_include_file.unlink()


def test_path_relative_to_file_not_cwd():
    """Test that paths are resolved relative to file, not current working directory.

    This is critical: if we run the test from a different directory,
    the include should still work because it's relative to the file location.
    """
    import os

    test_dir = Path(__file__).parent
    main_file = test_dir / "main_relative.gms"

    # Save current directory
    original_cwd = os.getcwd()

    try:
        # Change to a different directory (parent of test_dir)
        os.chdir(test_dir.parent.parent.parent)

        print("\nTest: Path Relative to File, Not CWD")
        print(f"CWD: {os.getcwd()}")
        print(f"Main file: {main_file}")

        # Even though CWD is different, parsing should work
        # because paths are resolved relative to the file
        model = parse_model_file(str(main_file))

        print(f"  Parameters found: {list(model.params.keys())}")
        assert "a" in model.params, "Parameter 'a' not found"

        print("✓ Path resolved relative to file, not CWD")

    finally:
        # Restore original directory
        os.chdir(original_cwd)


def test_missing_relative_path_error():
    """Test that missing files give clear error messages."""
    test_dir = Path(__file__).parent

    # Create a file with a non-existent include
    main_file = test_dir / "temp_missing.gms"
    main_file.write_text("$include data/nonexistent.inc\nVariables x;")

    try:
        print("\nTest: Missing Relative Path Error")
        print(f"Main file: {main_file}")

        with pytest.raises(FileNotFoundError) as exc_info:
            parse_model_file(str(main_file))

        error_msg = str(exc_info.value)
        print(f"  Error message: {error_msg}")

        # Error should mention the file that doesn't exist
        assert "nonexistent.inc" in error_msg or "data/nonexistent.inc" in error_msg

        # Error should give context about where the include was attempted
        assert "temp_missing.gms" in error_msg

        print("✓ Clear error message for missing file")

    finally:
        if main_file.exists():
            main_file.unlink()


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Relative Path Resolution in $include")
    print("Unknown 1.5 Verification")
    print("=" * 60)

    try:
        test_relative_path_from_main()
        test_nested_relative_path()
        test_parent_directory_resolution()
        test_absolute_path_resolution()
        test_path_relative_to_file_not_cwd()
        test_missing_relative_path_error()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
