#!/usr/bin/env python3
"""Test parsing of all Tier 2 candidate models."""

from pathlib import Path

from src.ir.parser import parse_model_file

models = [
    "bearing.gms",
    "chain.gms",
    "chem.gms",
    "chenery.gms",
    "elec.gms",
    "fct.gms",
    "gasoil.gms",
    "gastrans.gms",
    "haverly.gms",
    "house.gms",
    "inscribedsquare.gms",
    "jbearing.gms",
    "least.gms",
    "like.gms",
    "polygon.gms",
    "pool.gms",
    "process.gms",
    "water.gms",
]

results = []

for model_name in models:
    model_path = Path(f"tests/fixtures/tier2_candidates/{model_name}")
    try:
        result = parse_model_file(model_path)
        results.append({"name": model_name, "status": "✓", "blocker": None})
        print(f"✓ {model_name} - PARSES")
    except Exception as e:
        error_msg = str(e)
        # Truncate very long error messages
        if len(error_msg) > 200:
            error_msg = error_msg[:200] + "..."
        results.append({"name": model_name, "status": "✗", "blocker": error_msg})
        print(f"✗ {model_name} - BLOCKER: {error_msg}")

# Print summary table
print("\n" + "=" * 80)
print("SUMMARY TABLE")
print("=" * 80)
print(f"{'Model Name':<25} {'Status':<10} {'Blocker'}")
print("-" * 80)
for r in results:
    blocker = r["blocker"] if r["blocker"] else "-"
    print(f"{r['name']:<25} {r['status']:<10} {blocker}")

# Count statistics
total = len(results)
passed = sum(1 for r in results if r["status"] == "✓")
failed = total - passed
print("=" * 80)
print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
print("=" * 80)
