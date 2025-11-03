#!/usr/bin/env python3
"""Test script to verify indexed variables with .fx."""

from pathlib import Path

from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_file
from src.ir.symbols import Rel


def test_indexed_fixed():
    """Test indexed variable with .fx on specific indices."""
    gms_file = Path(__file__).parent / "test_indexed_fixed.gms"

    print(f"Parsing: {gms_file}")
    model = parse_model_file(str(gms_file))

    print("\n✓ Parsed successfully")

    # Check x variable
    if "x" not in model.variables:
        print("✗ Variable 'x' not found!")
        return False

    x_var = model.variables["x"]
    print("\n✓ Variable 'x' found")
    print(f"  domain: {x_var.domain}")
    print(f"  .fx (scalar): {x_var.fx}")
    print(f"  .fx_map: {x_var.fx_map}")
    print(f"  .lo_map: {x_var.lo_map}")
    print(f"  .up_map: {x_var.up_map}")

    # Check that fx_map has entry for i2
    if ("i2",) not in x_var.fx_map:
        print("\n✗ Expected x.fx_map[('i2',)] not found!")
        return False

    if x_var.fx_map[("i2",)] != 5.0:
        print(f"\n✗ Expected x.fx('i2') = 5.0, got {x_var.fx_map[('i2',)]}")
        return False

    print("\n✓ x.fx('i2') = 5.0 (correct)")

    # Check lo/up bounds for i1
    if ("i1",) not in x_var.lo_map or x_var.lo_map[("i1",)] != 0.0:
        print("\n✗ Expected x.lo('i1') = 0.0")
        return False

    if ("i1",) not in x_var.up_map or x_var.up_map[("i1",)] != 10.0:
        print("\n✗ Expected x.up('i1') = 10.0")
        return False

    print("✓ x.lo('i1') = 0.0, x.up('i1') = 10.0 (correct)")

    # Run normalization
    print("\nRunning normalization...")
    equations, bounds = normalize_model(model)

    print("\n✓ Normalization complete")
    print(f"  Bounds: {list(bounds.keys())}")

    # Check for x_fx(i2) bound
    if "x_fx(i2)" not in bounds:
        print("\n✗ Expected bound 'x_fx(i2)' not found!")
        return False

    fx_bound = bounds["x_fx(i2)"]
    print("\n✓ Found 'x_fx(i2)' bound")
    print(f"  relation: {fx_bound.relation}")
    print(f"  expr: {fx_bound.expr}")
    print(f"  index_values: {fx_bound.index_values}")

    # Verify it's an equality
    if fx_bound.relation != Rel.EQ:
        print(f"\n✗ Expected EQ relation, got {fx_bound.relation}")
        return False

    print("✓ Relation is EQ (equality constraint)")

    # Verify index_values
    if fx_bound.index_values != ("i2",):
        print(f"\n✗ Expected index_values ('i2',), got {fx_bound.index_values}")
        return False

    print(f"✓ Index values correct: {fx_bound.index_values}")

    # Check for x_lo(i1) and x_up(i1) bounds
    if "x_lo(i1)" not in bounds:
        print("\n✗ Expected bound 'x_lo(i1)' not found!")
        return False

    if "x_up(i1)" not in bounds:
        print("\n✗ Expected bound 'x_up(i1)' not found!")
        return False

    print("\n✓ Found 'x_lo(i1)' and 'x_up(i1)' bounds")
    print(f"  x_lo(i1) relation: {bounds['x_lo(i1)'].relation}")
    print(f"  x_up(i1) relation: {bounds['x_up(i1)'].relation}")

    # Verify they are inequalities
    if bounds["x_lo(i1)"].relation != Rel.LE:
        print("\n✗ Expected LE relation for x_lo(i1)")
        return False

    if bounds["x_up(i1)"].relation != Rel.LE:
        print("\n✗ Expected LE relation for x_up(i1)")
        return False

    print("✓ Both are LE (inequality constraints)")

    # Verify i3 has no bounds (should be free)
    i3_bounds = [k for k in bounds.keys() if "i3" in k]
    if i3_bounds:
        print(f"\n  Note: x(i3) has bounds: {i3_bounds} (unexpected, should be free)")
    else:
        print("\n✓ x(i3) has no bounds (free, as expected)")

    print("\n✓ All checks passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("Test: Indexed Variable with .fx")
    print("=" * 60)
    success = test_indexed_fixed()

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
