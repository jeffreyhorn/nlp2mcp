#!/usr/bin/env python3
"""Test script to verify Table block parsing."""

from pathlib import Path

from src.ir.parser import parse_model_file


def test_simple_table():
    """Test parsing a simple 2D table."""
    gms_file = Path(__file__).parent / "test_table_only.gms"

    print(f"Parsing: {gms_file}")
    model = parse_model_file(str(gms_file))

    # Check that table "data" exists
    if "data" not in model.params:
        print("✗ Table 'data' not found!")
        print(f"  Available parameters: {list(model.params.keys())}")
        return False

    print("✓ Table 'data' found!")

    table = model.params["data"]
    print(f"  Domain: {table.domain}")
    print(f"  Values: {table.values}")

    # Expected values
    expected = {
        ("i1", "j1"): 1.0,
        ("i1", "j2"): 2.0,
        ("i2", "j1"): 3.0,
        ("i2", "j2"): 4.0,
    }

    # Check domain
    if table.domain != ("i", "j"):
        print(f"✗ Domain mismatch: expected ('i', 'j'), got {table.domain}")
        return False

    print("✓ Domain correct")

    # Check values
    if table.values != expected:
        print("✗ Values mismatch")
        print(f"  Expected: {expected}")
        print(f"  Got:      {table.values}")

        # Show differences
        for key in expected:
            if key not in table.values:
                print(f"  Missing key: {key}")
            elif table.values[key] != expected[key]:
                print(f"  Wrong value for {key}: expected {expected[key]}, got {table.values[key]}")

        for key in table.values:
            if key not in expected:
                print(f"  Unexpected key: {key} = {table.values[key]}")

        return False

    print("✓ Values correct")
    print("\n✓ All checks passed!")
    return True


def test_sparse_table():
    """Test parsing a sparse table with missing values (should default to 0)."""
    gms_file = Path(__file__).parent / "test_sparse_table.gms"

    print(f"\nParsing: {gms_file}")
    model = parse_model_file(str(gms_file))

    # Check that table "sparse_data" exists
    if "sparse_data" not in model.params:
        print("✗ Table 'sparse_data' not found!")
        print(f"  Available parameters: {list(model.params.keys())}")
        return False

    print("✓ Table 'sparse_data' found!")

    table = model.params["sparse_data"]
    print(f"  Domain: {table.domain}")
    print(f"  Values: {table.values}")

    # Expected values (missing cells should be 0.0)
    expected = {
        ("i1", "j1"): 1.0,
        ("i1", "j2"): 0.0,  # missing
        ("i1", "j3"): 3.0,
        ("i2", "j1"): 0.0,  # missing
        ("i2", "j2"): 5.0,
        ("i2", "j3"): 0.0,  # missing
        ("i3", "j1"): 7.0,
        ("i3", "j2"): 0.0,  # missing
        ("i3", "j3"): 9.0,
    }

    # Check domain
    if table.domain != ("i", "j"):
        print(f"✗ Domain mismatch: expected ('i', 'j'), got {table.domain}")
        return False

    print("✓ Domain correct")

    # Check values
    if table.values != expected:
        print("✗ Values mismatch")
        print(f"  Expected: {expected}")
        print(f"  Got:      {table.values}")

        # Show differences
        for key in expected:
            if key not in table.values:
                print(f"  Missing key: {key}")
            elif table.values[key] != expected[key]:
                print(f"  Wrong value for {key}: expected {expected[key]}, got {table.values[key]}")

        for key in table.values:
            if key not in expected:
                print(f"  Unexpected key: {key} = {table.values[key]}")

        return False

    print("✓ Values correct (zero-filled for missing cells)")
    print("\n✓ All checks passed!")
    return True


def test_table_with_text():
    """Test parsing a table with descriptive text."""
    gms_file = Path(__file__).parent / "test_table_with_text.gms"

    print(f"\nParsing: {gms_file}")
    model = parse_model_file(str(gms_file))

    # Check that table "data" exists
    if "data" not in model.params:
        print("✗ Table 'data' not found!")
        print(f"  Available parameters: {list(model.params.keys())}")
        return False

    print("✓ Table 'data' found!")

    table = model.params["data"]
    print(f"  Domain: {table.domain}")
    print(f"  Values: {table.values}")

    # Expected values
    expected = {
        ("i1", "j1"): 10.0,
        ("i1", "j2"): 20.0,
        ("i1", "j3"): 30.0,
        ("i2", "j1"): 40.0,
        ("i2", "j2"): 50.0,
        ("i2", "j3"): 60.0,
    }

    # Check domain
    if table.domain != ("i", "j"):
        print(f"✗ Domain mismatch: expected ('i', 'j'), got {table.domain}")
        return False

    print("✓ Domain correct")

    # Check values
    if table.values != expected:
        print("✗ Values mismatch")
        print(f"  Expected: {expected}")
        print(f"  Got:      {table.values}")
        return False

    print("✓ Values correct (descriptive text handled)")
    print("\n✓ All checks passed!")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Test 1: Simple 2D Table")
    print("=" * 60)
    success1 = test_simple_table()

    print("\n" + "=" * 60)
    print("Test 2: Sparse Table (with empty cells)")
    print("=" * 60)
    success2 = test_sparse_table()

    print("\n" + "=" * 60)
    print("Test 3: Table with Descriptive Text")
    print("=" * 60)
    success3 = test_table_with_text()

    if success1 and success2 and success3:
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        exit(0)
    else:
        print("\n" + "=" * 60)
        print("✗ SOME TESTS FAILED")
        print("=" * 60)
        exit(1)
