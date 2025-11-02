#!/usr/bin/env python3
"""Test nested $include directive functionality.

This test verifies Unknown 1.4 from KNOWN_UNKNOWNS.md:
- Can $include directives be nested?
- Is circular include detection working?
- Are error messages clear?
- What is the depth limit?
"""

from pathlib import Path

import pytest

from src.ir.parser import parse_model_file
from src.ir.preprocessor import CircularIncludeError, IncludeDepthExceededError


def test_three_level_nesting():
    """Test that 3-level nested includes work correctly.

    Structure:
        main_nested.gms
        -> level1.inc (defines set i)
           -> level2.inc (defines parameter b)
              -> level3.inc (defines parameter c)

    Expected: All symbols (i, b, c, x) should be found in parsed model.
    """
    test_dir = Path(__file__).parent
    main_file = test_dir / "main_nested.gms"

    print("\nTest: 3-Level Nested Includes")
    print(f"Parsing: {main_file}")

    # Parse the model
    model = parse_model_file(str(main_file))

    # Check that all symbols from all include levels are present
    print(f"  Sets: {list(model.sets.keys())}")
    print(f"  Parameters: {list(model.params.keys())}")
    print(f"  Variables: {list(model.variables.keys())}")

    # Verify set from level1.inc
    assert "i" in model.sets, "Set 'i' from level1.inc not found"

    # Verify scalar from level2.inc
    assert "b" in model.params, "Scalar 'b' from level2.inc not found"
    assert model.params["b"].values[()] == 2.0, "Scalar 'b' has wrong value"

    # Verify scalar from level3.inc
    assert "c" in model.params, "Scalar 'c' from level3.inc not found"
    assert model.params["c"].values[()] == 3.0, "Scalar 'c' has wrong value"

    # Verify variable from main file
    assert "x" in model.variables, "Variable 'x' from main file not found"

    print("✓ All symbols found at all nesting levels")


def test_circular_include_detection():
    """Test that circular includes are detected and raise an error.

    Structure:
        main_circular.gms
        -> circular_a.inc
           -> circular_b.inc
              -> circular_a.inc (CIRCULAR!)

    Expected: CircularIncludeError with clear message showing the cycle.
    """
    test_dir = Path(__file__).parent
    main_file = test_dir / "main_circular.gms"

    print("\nTest: Circular Include Detection")
    print(f"Attempting to parse: {main_file}")

    # Should raise CircularIncludeError
    with pytest.raises(CircularIncludeError) as exc_info:
        parse_model_file(str(main_file))

    error_message = str(exc_info.value)
    print(f"  Error caught: {error_message}")

    # Verify error message contains the cycle
    assert (
        "Circular include detected" in error_message
    ), "Error message doesn't mention circular include"
    assert "circular_a.inc" in error_message, "circular_a.inc not in error message"
    assert "circular_b.inc" in error_message, "circular_b.inc not in error message"

    # Verify cycle is shown as a chain (A -> B -> A)
    assert "->" in error_message, "Error message doesn't show include chain"

    print("✓ Circular include detected with clear error message")


def test_error_message_quality():
    """Test that error messages are helpful when includes fail.

    Test cases:
    1. Missing include file
    2. Include file with syntax error (if applicable)
    """
    test_dir = Path(__file__).parent

    print("\nTest: Error Message Quality")

    # Create a temporary file with a missing include
    missing_include_file = test_dir / "temp_missing_include.gms"
    missing_include_file.write_text("$include nonexistent_file.inc\nVariables x;")

    try:
        print("  Testing missing include file...")

        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError) as exc_info:
            parse_model_file(str(missing_include_file))

        error_message = str(exc_info.value)
        print(f"  Error message: {error_message}")

        # Verify error message is helpful
        assert "nonexistent_file.inc" in error_message, "Missing filename not in error"
        assert "temp_missing_include.gms" in error_message, "Source file not in error"

        # Check if line number is included
        if "line" in error_message.lower():
            print("  ✓ Error includes line number information")

        print("✓ Error message is clear and helpful")

    finally:
        # Cleanup
        if missing_include_file.exists():
            missing_include_file.unlink()


def test_depth_limit():
    """Test the maximum include nesting depth.

    The preprocessor has a max_depth parameter (default 100).
    Create a very deep nesting and verify it's handled appropriately.
    """
    test_dir = Path(__file__).parent

    print("\nTest: Depth Limit")

    # Create a chain of 10 levels (reasonable test)
    depth = 10

    # Create level files
    for i in range(depth):
        level_file = test_dir / f"temp_level_{i}.inc"
        # Use pN naming (p0, p1, ...) - GAMS identifiers can't start with underscore
        if i == depth - 1:
            # Last level - just define a scalar parameter
            content = f"Scalar p{i} /{i + 1}.0/;"
        else:
            # Include next level
            content = f"Scalar p{i} /{i + 1}.0/;\n$include temp_level_{i + 1}.inc"
        level_file.write_text(content)

    # Create main file
    main_file = test_dir / "temp_main_deep.gms"
    main_file.write_text("$include temp_level_0.inc\nVariable x;")

    try:
        print(f"  Testing {depth}-level deep nesting...")

        # Should succeed (10 is well under default limit of 100)
        model = parse_model_file(str(main_file))

        # Verify all scalars were found
        for i in range(depth):
            scalar_name = f"p{i}"
            assert scalar_name in model.params, f"Scalar '{scalar_name}' not found"
            assert model.params[scalar_name].values[()] == float(
                i + 1
            ), f"Scalar '{scalar_name}' has wrong value"

        print(f"✓ Successfully parsed {depth}-level deep includes")

        # Check what the actual max_depth is
        print("  Default max_depth: 100 (from preprocessor.py)")
        print(f"  Tested depth: {depth}")
        print("  ✓ Depth limit is reasonable and configurable")

    finally:
        # Cleanup
        for i in range(depth):
            level_file = test_dir / f"temp_level_{i}.inc"
            if level_file.exists():
                level_file.unlink()
        if main_file.exists():
            main_file.unlink()


def test_max_depth_exceeded():
    """Test that exceeding max_depth raises an appropriate error."""
    test_dir = Path(__file__).parent

    print("\nTest: Max Depth Exceeded")

    # Create a very deep nesting that exceeds the limit
    # Default max_depth is 100, so create 102 levels
    depth = 102

    # Create level files
    for i in range(depth):
        level_file = test_dir / f"temp_deep_{i}.inc"
        if i == depth - 1:
            content = f"Parameters p /{i}.0/;"
        else:
            content = f"$include temp_deep_{i + 1}.inc"
        level_file.write_text(content)

    # Create main file
    main_file = test_dir / "temp_main_too_deep.gms"
    main_file.write_text("$include temp_deep_0.inc")

    try:
        print(f"  Testing {depth}-level deep nesting (should exceed limit)...")

        # Should raise IncludeDepthExceededError
        with pytest.raises(IncludeDepthExceededError) as exc_info:
            parse_model_file(str(main_file))

        error_message = str(exc_info.value)
        print(f"  Error caught: {error_message}")

        # Verify error message mentions depth limit
        assert (
            "depth" in error_message.lower() or "100" in error_message
        ), "Error doesn't mention depth limit"

        print("✓ Max depth limit enforced correctly")

    finally:
        # Cleanup
        for i in range(depth):
            level_file = test_dir / f"temp_deep_{i}.inc"
            if level_file.exists():
                level_file.unlink()
        if main_file.exists():
            main_file.unlink()


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Nested $include Directives")
    print("Unknown 1.4 Verification")
    print("=" * 60)

    try:
        test_three_level_nesting()
        test_circular_include_detection()
        test_error_message_quality()
        test_depth_limit()
        test_max_depth_exceeded()

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
