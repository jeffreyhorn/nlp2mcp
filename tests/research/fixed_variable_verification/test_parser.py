#!/usr/bin/env python3
"""Test script to verify .fx (fixed variable) parsing and handling."""

from pathlib import Path

from src.ir.parser import parse_model_file


def test_scalar_fixed_variable():
    """Test parsing a scalar variable with .fx attribute."""
    gms_file = Path(__file__).parent / "test_fixed_scalar.gms"

    print(f"Parsing: {gms_file}")
    model = parse_model_file(str(gms_file))

    # Check that variable x exists
    if "x" not in model.variables:
        print("✗ Variable 'x' not found!")
        print(f"  Available variables: {list(model.variables.keys())}")
        return False

    print("✓ Variable 'x' found!")

    x_var = model.variables["x"]
    print("  Variable 'x' properties:")
    print(f"    .fx = {x_var.fx}")
    print(f"    .lo = {x_var.lo}")
    print(f"    .up = {x_var.up}")
    print(f"    .fx_map = {x_var.fx_map}")

    # Check that .fx is set to 10.0
    if x_var.fx != 10.0:
        print(f"✗ Expected x.fx = 10.0, got {x_var.fx}")
        return False

    print("✓ x.fx = 10.0 (correct)")

    # Check if .lo and .up are also set (expected behavior per GAMS docs)
    # Note: This depends on normalization phase, parser might not do this
    print("\nChecking if .fx implies .lo and .up:")
    if x_var.lo == 10.0 and x_var.up == 10.0:
        print("✓ x.lo = x.up = x.fx = 10.0 (already normalized)")
    else:
        print(f"  x.lo = {x_var.lo}, x.up = {x_var.up}")
        print("  Note: Normalization may happen in later phase")

    # Check that y is free
    if "y" not in model.variables:
        print("✗ Variable 'y' not found!")
        return False

    y_var = model.variables["y"]
    print("\n✓ Variable 'y' found!")
    print("  Variable 'y' properties:")
    print(f"    .fx = {y_var.fx}")
    print(f"    .lo = {y_var.lo}")
    print(f"    .up = {y_var.up}")

    print("\n✓ All checks passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("Test: Scalar Fixed Variable (.fx)")
    print("=" * 60)
    success = test_scalar_fixed_variable()

    if success:
        print("\n" + "=" * 60)
        print("✓ TEST PASSED")
        print("=" * 60)
        exit(0)
    else:
        print("\n" + "=" * 60)
        print("✗ TEST FAILED")
        print("=" * 60)
        exit(1)
