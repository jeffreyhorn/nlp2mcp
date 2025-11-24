"""
Synthetic tests for individual parser features.

Each test validates ONE feature in isolation using minimal GAMS code.
Tests should be fast (<1s each) and have clear pass/fail criteria.

Purpose:
    Validate that individual parser features work correctly in isolation,
    without interference from secondary blockers or complex model interactions.

Sprint 9 Lesson:
    Cannot validate i++1 indexing works when himmel16.gms has secondary blockers.
    Need minimal tests that prove features work independently.

Test States:
    PASS: Feature implemented and working
    SKIP: Feature not yet implemented (expected to fail)
    FAIL: Feature has bugs (unexpected behavior)

Usage:
    # Run all tests
    pytest tests/synthetic/test_synthetic.py -v

    # Run specific test
    pytest tests/synthetic/test_synthetic.py::test_synthetic_feature[i_plusplus_indexing.gms] -v

    # Run only passing tests (skip unimplemented)
    pytest tests/synthetic/test_synthetic.py -v -m "not skip"
"""

from pathlib import Path

import pytest

from src.ir.parser import parse_model_file

SYNTHETIC_DIR = Path(__file__).parent


@pytest.mark.parametrize(
    "test_file,should_parse,feature,sprint",
    [
        # Sprint 9 Features (Should PASS - already implemented)
        ("i_plusplus_indexing.gms", True, "i++1 lead/lag indexing", "9"),
        ("equation_attributes.gms", True, "equation attributes (.l, .m)", "9"),
        ("model_sections.gms", True, "model declaration and solve statements", "9"),
        # Sprint 10 Features - Function Calls
        ("function_calls_parameters.gms", False, "function calls in parameters", "10"),
        ("aggregation_functions.gms", False, "aggregation functions (smin/smax)", "10"),
        ("nested_function_calls.gms", False, "nested function calls", "10"),
        # Sprint 10 Features - Variable Bounds (Bug Fixes)
        ("variable_level_bounds.gms", False, "variable level bounds (.l)", "10"),
        ("mixed_variable_bounds.gms", False, "mixed variable bound types", "10"),
        # Sprint 10 Features - Comma-Separated Declarations
        ("comma_separated_variables.gms", True, "comma-separated variables", "10"),  # Already works
        ("comma_separated_scalars.gms", True, "comma-separated scalars with inline values", "10"),
        ("abort_in_if_blocks.gms", True, "abort$ in if-blocks", "9/10"),  # Already works
        # Deferred Features (Sprint 11+)
        ("nested_subset_indexing.gms", False, "nested/subset indexing in equation domains", "11+"),
    ],
)
def test_synthetic_feature(test_file, should_parse, feature, sprint):
    """
    Test that a specific feature works in isolation.

    Args:
        test_file: Name of synthetic test file
        should_parse: True if feature should parse successfully, False if not yet implemented
        feature: Human-readable feature name
        sprint: Sprint when feature was/will be implemented

    Test Logic:
        - If should_parse=True: Feature should work, test passes if parse succeeds
        - If should_parse=False: Feature not implemented, skip test (will pass after implementation)

    Expected Progression:
        1. Initially: should_parse=False → test skipped
        2. After implementation: change should_parse=True
        3. Then: test runs and should pass
        4. If fails after implementation: feature has bugs
    """
    file_path = SYNTHETIC_DIR / test_file

    if not file_path.exists():
        pytest.fail(f"Synthetic test file not found: {test_file}")

    if should_parse:
        # Feature should work - test that parsing succeeds
        try:
            result = parse_model_file(str(file_path))
            assert (
                result is not None
            ), f"{feature} (Sprint {sprint}) should parse successfully but returned None"
        except Exception as e:
            pytest.fail(
                f"{feature} (Sprint {sprint}) should parse but failed with: {type(e).__name__}: {e}"
            )
    else:
        # Feature not yet implemented - skip test with informative message
        pytest.skip(
            f"{feature} (Sprint {sprint}) not yet implemented - will pass after implementation"
        )


def test_synthetic_directory_exists():
    """Verify synthetic test directory exists and is accessible."""
    assert SYNTHETIC_DIR.exists(), "Synthetic test directory should exist"
    assert SYNTHETIC_DIR.is_dir(), "Synthetic test path should be a directory"


def test_readme_exists():
    """Verify README.md exists explaining the synthetic test framework."""
    readme_path = SYNTHETIC_DIR / "README.md"
    assert readme_path.exists(), "README.md should exist in synthetic test directory"
    assert readme_path.stat().st_size > 0, "README.md should not be empty"


# Test file validation (ensure test files exist before running parametrized tests)
EXPECTED_TEST_FILES = [
    # Sprint 9
    "i_plusplus_indexing.gms",
    "equation_attributes.gms",
    "model_sections.gms",
    # Sprint 10 - Function Calls
    "function_calls_parameters.gms",
    "aggregation_functions.gms",
    "nested_function_calls.gms",
    # Sprint 10 - Variable Bounds
    "variable_level_bounds.gms",
    "mixed_variable_bounds.gms",
    # Sprint 10 - Comma-Separated
    "comma_separated_variables.gms",
    "comma_separated_scalars.gms",
    "abort_in_if_blocks.gms",
    # Deferred
    "nested_subset_indexing.gms",
]


@pytest.mark.parametrize("test_file", EXPECTED_TEST_FILES)
def test_synthetic_file_exists(test_file):
    """Verify all expected synthetic test files exist."""
    file_path = SYNTHETIC_DIR / test_file
    assert file_path.exists(), f"Synthetic test file should exist: {test_file}"
    assert file_path.stat().st_size > 0, f"Synthetic test file should not be empty: {test_file}"


# Helper to list all synthetic test files for debugging
def test_list_synthetic_files():
    """List all .gms files in synthetic directory for debugging."""
    gms_files = sorted(SYNTHETIC_DIR.glob("*.gms"))
    print(f"\nFound {len(gms_files)} synthetic test files:")
    for f in gms_files:
        print(f"  - {f.name}")

    # This test always passes, it's just for information
    assert True
