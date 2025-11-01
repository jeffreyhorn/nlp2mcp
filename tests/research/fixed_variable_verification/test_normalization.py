#!/usr/bin/env python3
"""Test script to verify .fx normalization creates equality constraints."""

from pathlib import Path

from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_file


def test_fx_normalization():
    """Test that .fx creates equality constraint in normalization."""
    gms_file = Path(__file__).parent / "test_fixed_scalar.gms"

    print(f"Parsing: {gms_file}")
    model = parse_model_file(str(gms_file))

    print("\n✓ Parsed successfully")
    print(f"  Variables: {list(model.variables.keys())}")
    print(f"  x.fx = {model.variables['x'].fx}")

    # Run normalization
    print("\nRunning normalization...")
    equations, bounds = normalize_model(model)

    print("\n✓ Normalization complete")
    print(f"  Equations: {list(equations.keys())}")
    print(f"  Bounds: {list(bounds.keys())}")

    # Check that x_fx bound exists
    if "x_fx" not in bounds:
        print("\n✗ Expected bound 'x_fx' not found!")
        print(f"  Available bounds: {list(bounds.keys())}")
        return False

    print("\n✓ Found 'x_fx' bound")

    fx_bound = bounds["x_fx"]
    print("  Bound properties:")
    print(f"    name: {fx_bound.name}")
    print(f"    relation: {fx_bound.relation}")
    print(f"    expr: {fx_bound.expr}")
    print(f"    domain_sets: {fx_bound.domain_sets}")

    # Check that it's an equality (Rel.EQ)
    from src.ir.symbols import Rel

    if fx_bound.relation != Rel.EQ:
        print(f"\n✗ Expected relation EQ, got {fx_bound.relation}")
        return False

    print("\n✓ Relation is EQ (equality constraint)")

    # Check that it's in the equalities list
    if "x_fx" not in model.equalities:
        print("\n✗ 'x_fx' not in model.equalities list")
        print(f"  Equalities: {model.equalities}")
        return False

    print("\n✓ 'x_fx' is in equalities list")

    # Check that y does not have fx bound
    if "y_fx" in bounds:
        print("\n✗ Unexpected 'y_fx' bound found (y is not fixed)")
        return False

    print("\n✓ No 'y_fx' bound (y is free, as expected)")

    # Check y bounds (lo and up should be absent since set to -INF/INF)
    y_bounds = [k for k in bounds.keys() if k.startswith("y_")]
    print(f"\n  y bounds: {y_bounds}")

    print("\n✓ All checks passed!")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Test: .fx Normalization to Equality Constraint")
    print("=" * 60)
    success = test_fx_normalization()

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
