#!/usr/bin/env python3
"""Test KKT treatment of fixed variables."""

from pathlib import Path

from src.ad.api import compute_derivatives
from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_file
from src.kkt.assemble import assemble_kkt_system
from src.kkt.partition import partition_constraints


def test_kkt_fixed_variable():
    """Test KKT assembly with fixed variable."""
    gms_file = Path(__file__).parent / "test_fixed_scalar.gms"

    print(f"Parsing: {gms_file}")
    model = parse_model_file(str(gms_file))

    print("\n✓ Parsed successfully")
    print(f"  Variables: {[v for v in model.variables.keys() if not v.startswith('"')]}")

    # Normalize
    print("\nNormalizing...")
    equations, bounds = normalize_model(model)

    # Partition
    print("\nPartitioning constraints...")
    partition = partition_constraints(model)

    print(f"  Equalities: {partition.equalities}")
    print(f"  Inequalities: {partition.inequalities}")
    print(f"  bounds_lo: {list(partition.bounds_lo.keys())}")
    print(f"  bounds_up: {list(partition.bounds_up.keys())}")
    print(f"  bounds_fx: {list(partition.bounds_fx.keys())}")

    # Check that x is in bounds_fx
    if ("x", ()) not in partition.bounds_fx:
        print("\n✗ Expected ('x', ()) in bounds_fx")
        return False

    print("\n✓ Found x in bounds_fx")
    print(f"  Value: {partition.bounds_fx[('x', ())].value}")

    # Compute derivatives
    print("\nComputing derivatives...")
    gradient, jacobian_eq, jacobian_ineq, jacobian_bounds_lo, jacobian_bounds_up = (
        compute_derivatives(model)
    )

    print(f"  Gradient dimensions: {gradient.num_cols} variables")
    print(f"  Variables in gradient: {list(gradient.index_mapping.var_to_col.keys())}")

    # Assemble KKT
    print("\nAssembling KKT system...")
    kkt = assemble_kkt_system(
        model,
        gradient,
        jacobian_eq,
        jacobian_ineq,
        jacobian_bounds_lo,
        jacobian_bounds_up,
    )

    print("\n✓ KKT system assembled")
    print(f"  Stationarity equations: {list(kkt.stationarity.keys())}")
    print(f"  Complementarity equations: {list(kkt.complementarity.keys())}")
    print(f"  Multipliers: {list(kkt.multipliers.keys())}")

    # Check if stat_x exists
    if "stat_x" in kkt.stationarity:
        print("\n  Note: stat_x exists (fixed variable has stationarity)")
        stat_x = kkt.stationarity["stat_x"]
        print(f"    domain: {stat_x.domain}")
        print(f"    lhs_rhs: {stat_x.lhs_rhs}")
    else:
        print("\n  Note: stat_x does NOT exist (fixed variable excluded)")

    # Check if there are pi_L or pi_U multipliers for x
    x_multipliers = [m for m in kkt.multipliers.keys() if m.startswith("pi_") and "_x" in m]
    print(f"\n  Multipliers for x: {x_multipliers}")

    if x_multipliers:
        print("  Note: Fixed variable x has bound multipliers (may be incorrect)")
    else:
        print("  Note: Fixed variable x has NO bound multipliers (correct)")

    # Check if x_fx equality constraint exists
    if "x_fx" in kkt.equalities:
        print("\n✓ x_fx equality constraint found in KKT equalities")
        eq_x_fx = kkt.equalities["x_fx"]
        print(f"  domain: {eq_x_fx.domain}")
        print(f"  lhs_rhs: {eq_x_fx.lhs_rhs}")
    else:
        print("\n✗ x_fx equality constraint NOT found in KKT equalities")
        return False

    print("\n✓ All checks passed!")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Test: KKT Treatment of Fixed Variables")
    print("=" * 60)
    success = test_kkt_fixed_variable()

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
