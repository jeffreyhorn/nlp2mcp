#!/usr/bin/env python3
"""Integration health check script for mid-sprint checkpoint.

Tests all 5 example models through the full pipeline and verifies:
1. Generated GAMS includes original symbols
2. No infinite bound multipliers created
3. Objective variable handling correct
4. Duplicate bounds excluded (Finding #1)
5. Indexed bounds handled (Finding #2)
6. Variable kinds preserved (Finding #4)
"""

import sys
from pathlib import Path

from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ad.gradient import compute_objective_gradient
from src.emit.emit_gams import emit_gams_mcp
from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_file
from src.kkt.assemble import assemble_kkt_system


def check_example(example_path: Path) -> dict:
    """Run full pipeline on example and verify all requirements.

    Returns:
        dict with verification results
    """
    print(f"\n{'=' * 60}")
    print(f"Testing: {example_path.name}")
    print(f"{'=' * 60}")

    results = {"example": example_path.name, "success": False, "checks": {}, "issues": []}

    try:
        # Step 1: Parse
        print("  [1/5] Parsing...")
        model = parse_model_file(str(example_path))

        # Step 2: Normalize
        print("  [2/5] Normalizing...")
        normalize_model(model)

        # Step 3: Compute derivatives
        print("  [3/5] Computing derivatives...")
        gradient = compute_objective_gradient(model)
        J_eq, J_ineq = compute_constraint_jacobian(model)

        # Step 4: Assemble KKT
        print("  [4/5] Assembling KKT system...")
        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)

        # Step 5: Emit GAMS
        print("  [5/5] Emitting GAMS MCP...")
        gams_code = emit_gams_mcp(kkt)

        # Verification checks
        print("\n  Verification Checks:")

        # Check 1: Original symbols included
        print("    ✓ Checking original symbols...")
        has_sets = bool(model.sets) and any(s in gams_code for s in model.sets)
        has_params = bool(model.params) and any(p in gams_code for p in model.params)
        has_vars = bool(model.variables) and any(v in gams_code for v in model.variables)

        results["checks"]["original_symbols"] = has_sets or has_params or has_vars
        if results["checks"]["original_symbols"]:
            print(
                f"      ✅ Original symbols present (Sets: {has_sets}, Params: {has_params}, Vars: {has_vars})"
            )
        else:
            print("      ❌ Original symbols missing!")
            results["issues"].append("Original symbols not found in output")

        # Check 2: No infinite bound multipliers
        print("    ✓ Checking infinite bounds...")
        infinite_count = len(kkt.skipped_infinite_bounds)
        has_infinite_multipliers = False

        for var, indices, bound_type in kkt.skipped_infinite_bounds:
            # Check if multiplier exists for infinite bound
            key = (var, indices)
            if bound_type == "lo" and key in kkt.multipliers_bounds_lo:
                has_infinite_multipliers = True
            elif bound_type == "up" and key in kkt.multipliers_bounds_up:
                has_infinite_multipliers = True

        results["checks"]["no_infinite_multipliers"] = not has_infinite_multipliers
        if results["checks"]["no_infinite_multipliers"]:
            print(f"      ✅ No multipliers for {infinite_count} infinite bounds")
        else:
            print("      ❌ Found multipliers for infinite bounds!")
            results["issues"].append("Infinite bound multipliers created")

        # Check 3: Objective variable handling
        print("    ✓ Checking objective variable...")
        objvar = model.objective.objvar
        has_stat_for_objvar = f"stat_{objvar}" in gams_code
        objvar_in_model = f".{objvar}" in gams_code

        results["checks"]["objective_handling"] = objvar_in_model and not has_stat_for_objvar
        if results["checks"]["objective_handling"]:
            print(f"      ✅ Objective variable '{objvar}' handled correctly")
            print(f"         - No stationarity equation for objvar: {not has_stat_for_objvar}")
            print(f"         - Objvar appears in Model MCP: {objvar_in_model}")
        else:
            print("      ❌ Objective variable handling incorrect!")
            results["issues"].append(f"Objective variable '{objvar}' not handled correctly")

        # Check 4: Duplicate bounds excluded (Finding #1)
        print("    ✓ Checking duplicate bounds exclusion...")
        excluded_count = len(kkt.duplicate_bounds_excluded)

        # Verify excluded bounds don't appear in complementarity
        has_excluded_in_comp = False
        for eq_name in kkt.duplicate_bounds_excluded:
            if eq_name in kkt.complementarity_ineq:
                has_excluded_in_comp = True

        results["checks"]["duplicates_excluded"] = not has_excluded_in_comp
        if results["checks"]["duplicates_excluded"]:
            print(f"      ✅ {excluded_count} duplicate bounds excluded from inequalities")
        else:
            print("      ❌ Excluded bounds found in complementarity!")
            results["issues"].append("Duplicate bounds not properly excluded")

        # Check 5: Indexed bounds handled (Finding #2)
        print("    ✓ Checking indexed bounds...")
        indexed_lo = sum(1 for (v, idx) in kkt.multipliers_bounds_lo if idx)
        indexed_up = sum(1 for (v, idx) in kkt.multipliers_bounds_up if idx)
        total_indexed = indexed_lo + indexed_up

        # Check if model has indexed variables with bounds
        model_has_indexed_bounds = False
        for var_def in model.variables.values():
            if var_def.domain and (var_def.lo_map or var_def.up_map):
                model_has_indexed_bounds = True
                break

        results["checks"]["indexed_bounds"] = True  # Assume OK if no errors
        if total_indexed > 0:
            print(f"      ✅ Indexed bounds handled: {indexed_lo} lower, {indexed_up} upper")
        elif model_has_indexed_bounds:
            print("      ⚠️  Model has indexed bounds but none found in KKT")
            results["issues"].append("Indexed bounds may not be handled correctly")
        else:
            print("      ℹ️  No indexed bounds in this model")

        # Check 6: Variable kinds preserved (Finding #4)
        print("    ✓ Checking variable kinds...")
        has_positive_vars = "Positive Variables" in gams_code
        has_binary_vars = "Binary Variables" in gams_code
        has_integer_vars = "Integer Variables" in gams_code

        # Count variable kinds in model
        from src.ir.symbols import VarKind

        model_has_positive = any(v.kind == VarKind.POSITIVE for v in model.variables.values())
        model_has_binary = any(v.kind == VarKind.BINARY for v in model.variables.values())
        model_has_integer = any(v.kind == VarKind.INTEGER for v in model.variables.values())

        kinds_match = True
        if model_has_positive and not has_positive_vars:
            kinds_match = False
        if model_has_binary and not has_binary_vars:
            kinds_match = False
        if model_has_integer and not has_integer_vars:
            kinds_match = False

        results["checks"]["variable_kinds"] = kinds_match
        if kinds_match:
            print("      ✅ Variable kinds preserved")
            print(f"         - Positive: {model_has_positive} → {has_positive_vars}")
            print(f"         - Binary: {model_has_binary} → {has_binary_vars}")
            print(f"         - Integer: {model_has_integer} → {has_integer_vars}")
        else:
            print("      ❌ Variable kinds not preserved!")
            results["issues"].append("Variable kinds not preserved in output")

        # Overall success
        results["success"] = all(results["checks"].values()) and not results["issues"]

        if results["success"]:
            print(f"\n  ✅ All checks passed for {example_path.name}")
        else:
            print(f"\n  ❌ Some checks failed for {example_path.name}")

    except Exception as e:
        print(f"\n  ❌ ERROR: {e}")
        results["issues"].append(f"Exception: {e}")
        import traceback

        traceback.print_exc()

    return results


def main():
    """Run integration health check on all examples."""
    print("=" * 60)
    print("INTEGRATION HEALTH CHECK")
    print("Sprint 3 Mid-Sprint Checkpoint")
    print("=" * 60)

    examples = [
        "examples/simple_nlp.gms",
    ]

    # Find all .gms files in examples/
    examples_dir = Path("examples")
    if examples_dir.exists():
        examples = sorted(examples_dir.glob("*.gms"))

    all_results = []

    for example_path in examples:
        if not example_path.exists():
            print(f"\n⚠️  Skipping {example_path} (not found)")
            continue

        result = check_example(example_path)
        all_results.append(result)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    total = len(all_results)
    passed = sum(1 for r in all_results if r["success"])
    failed = total - passed

    print(f"\nTotal Examples: {total}")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")

    if failed > 0:
        print("\nFailed Examples:")
        for result in all_results:
            if not result["success"]:
                print(f"  ❌ {result['example']}")
                for issue in result["issues"]:
                    print(f"     - {issue}")

    print("\nVerification Checks:")
    check_names = {
        "original_symbols": "Original symbols included",
        "no_infinite_multipliers": "No infinite bound multipliers",
        "objective_handling": "Objective variable correct",
        "duplicates_excluded": "Duplicate bounds excluded (Finding #1)",
        "indexed_bounds": "Indexed bounds handled (Finding #2)",
        "variable_kinds": "Variable kinds preserved (Finding #4)",
    }

    for check_key, check_name in check_names.items():
        check_results = [r["checks"].get(check_key, False) for r in all_results]
        passed_count = sum(check_results)
        total_count = len(check_results)
        status = "✅" if passed_count == total_count else "❌"
        print(f"  {status} {check_name}: {passed_count}/{total_count}")

    print("\n" + "=" * 60)

    if failed == 0:
        print("✅ INTEGRATION HEALTH CHECK PASSED")
        print("=" * 60)
        return 0
    else:
        print("❌ INTEGRATION HEALTH CHECK FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
