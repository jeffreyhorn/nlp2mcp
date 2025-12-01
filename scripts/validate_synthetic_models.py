#!/usr/bin/env python3
"""Validate synthetic test models against their design characteristics.

This script validates that synthetic models created for testing have
the expected simplification characteristics.

Sprint 12 Day 2: Extended Validation and Synthetic Testing
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# Synthetic model specifications
SYNTHETIC_MODELS = {
    "model_a_heavy_factorization.gms": {
        "description": "Heavy factorization opportunities",
        "expected_min_reduction": 40.0,
        "characteristics": [
            "Common factor extraction (2*x + 2*y => 2*(x+y))",
            "Variable factorization (x*a + x*b => x*(a+b))",
            "Nested factorization",
        ],
    },
    "model_b_minimal_simplification.gms": {
        "description": "Minimal simplification opportunities",
        "expected_max_reduction": 100.0,  # Accept any reduction for "minimal"
        "characteristics": [
            "Already simplified expressions",
            "No common factors (prime coefficients)",
            "Pre-factored forms",
        ],
    },
    "model_c_mixed_transformations.gms": {
        "description": "Mixed transformation opportunities",
        "expected_min_reduction": 20.0,
        "expected_max_reduction": 60.0,
        "characteristics": [
            "Some factorization opportunities",
            "Mix of factorable and non-factorable expressions",
            "Combination of simple and complex terms",
        ],
    },
}


def run_measurement(model_path: Path) -> dict[str, Any]:
    """Run measure_simplification.py on a model and return results."""
    result = subprocess.run(
        [sys.executable, "scripts/measure_simplification.py", "--model", str(model_path)],
        capture_output=True,
        text=True,
        check=True,
    )

    # Parse JSON output (ignoring stderr messages)
    output_json = json.loads(result.stdout)

    # Extract the model metrics
    model_name = model_path.name
    if model_name in output_json["models"]:
        return output_json["models"][model_name]
    else:
        raise ValueError(f"Model {model_name} not found in output")


def validate_model(
    model_name: str, spec: dict[str, Any], metrics: dict[str, Any]
) -> tuple[bool, list[str]]:
    """Validate a model's metrics against its specification.

    Returns:
        (is_valid, messages) tuple
    """
    messages = []
    is_valid = True

    term_reduction = metrics["terms_reduction_pct"]

    # Check minimum reduction if specified
    if "expected_min_reduction" in spec:
        min_reduction = spec["expected_min_reduction"]
        if term_reduction < min_reduction:
            is_valid = False
            messages.append(
                f"❌ Term reduction {term_reduction:.2f}% below expected minimum {min_reduction:.2f}%"
            )
        else:
            messages.append(
                f"✅ Term reduction {term_reduction:.2f}% meets minimum {min_reduction:.2f}%"
            )

    # Check maximum reduction if specified
    if "expected_max_reduction" in spec:
        max_reduction = spec["expected_max_reduction"]
        if term_reduction > max_reduction:
            is_valid = False
            messages.append(
                f"❌ Term reduction {term_reduction:.2f}% exceeds maximum {max_reduction:.2f}%"
            )
        else:
            messages.append(
                f"✅ Term reduction {term_reduction:.2f}% within maximum {max_reduction:.2f}%"
            )

    # Report metrics
    messages.append(
        f"   Operations: {metrics['ops_before']} → {metrics['ops_after']} (-{metrics['ops_reduction_pct']:.2f}%)"
    )
    messages.append(
        f"   Terms: {metrics['terms_before']} → {metrics['terms_after']} (-{metrics['terms_reduction_pct']:.2f}%)"
    )
    messages.append(f"   Execution time: {metrics['execution_time_ms']:.3f}ms")

    return is_valid, messages


def main() -> int:
    """Main entry point."""
    print("=" * 70)
    print("Synthetic Model Validation")
    print("=" * 70)
    print()

    synthetic_dir = Path("tests/fixtures/synthetic")
    all_valid = True
    results = {}

    for model_name, spec in SYNTHETIC_MODELS.items():
        model_path = synthetic_dir / model_name

        if not model_path.exists():
            print(f"❌ {model_name}: Model file not found")
            all_valid = False
            continue

        print(f"📊 {model_name}")
        print(f"   Description: {spec['description']}")
        print(f"   Characteristics:")
        for char in spec["characteristics"]:
            print(f"     - {char}")

        # Run measurement
        try:
            metrics = run_measurement(model_path)
            results[model_name] = metrics

            # Validate
            is_valid, messages = validate_model(model_name, spec, metrics)
            print()
            for msg in messages:
                print(f"   {msg}")

            if not is_valid:
                all_valid = False

        except Exception as e:
            print(f"   ❌ Error measuring model: {e}")
            all_valid = False

        print()

    # Summary
    print("=" * 70)
    if all_valid:
        print("✅ All synthetic models validated successfully")
        print()
        print("Summary:")
        for model_name, metrics in results.items():
            print(f"  {model_name}: {metrics['terms_reduction_pct']:.2f}% term reduction")
        return 0
    else:
        print("❌ Some synthetic models failed validation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
