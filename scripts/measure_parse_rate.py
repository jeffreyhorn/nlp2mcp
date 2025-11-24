#!/usr/bin/env python3
"""
Measure parse rate across GAMSLIB Tier 1 models.

This script tests parsing success for the 10 GAMSLIB Tier 1 models
and calculates the parse rate percentage. It's used for tracking
Sprint 10 progress and validating parse rate improvements.

Usage:
    python scripts/measure_parse_rate.py [--verbose]

Exit codes:
    0: All models parsed successfully (100% parse rate)
    1: Some models failed to parse (< 100% parse rate)
"""

import argparse
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.ir.parser import parse_model_file

# GAMSLIB Tier 1 models (10 models)
TIER1_MODELS = [
    "circle.gms",
    "himmel16.gms",
    "hs62.gms",
    "mathopt1.gms",
    "maxmin.gms",
    "mhw4d.gms",
    "mhw4dx.gms",
    "mingamma.gms",
    "rbrock.gms",
    "trig.gms",
]

GAMSLIB_DIR = PROJECT_ROOT / "tests" / "fixtures" / "gamslib"


def test_parse(model_path: Path) -> bool:
    """
    Test if a model parses successfully.

    Args:
        model_path: Path to the GAMS model file

    Returns:
        True if parsing succeeded, False otherwise
    """
    try:
        result = parse_model_file(str(model_path))
        return result is not None
    except Exception:
        return False


def measure_parse_rate(verbose: bool = False) -> tuple[int, int, float]:
    """
    Measure parse rate across GAMSLIB Tier 1 models.

    Args:
        verbose: If True, print detailed results for each model

    Returns:
        Tuple of (successful_count, total_count, percentage)
    """
    results = []

    if verbose:
        print("Testing GAMSLIB Tier 1 models...")
        print("=" * 60)

    for model_name in TIER1_MODELS:
        model_path = GAMSLIB_DIR / model_name

        if not model_path.exists():
            if verbose:
                print(f"⚠️  {model_name:20s} - FILE NOT FOUND")
            results.append((model_name, False))
            continue

        success = test_parse(model_path)
        results.append((model_name, success))

        if verbose:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}  {model_name}")

    # Calculate statistics
    successful = sum(1 for _, success in results if success)
    total = len(results)
    percentage = (successful / total * 100) if total > 0 else 0.0

    if verbose:
        print("=" * 60)
        print(f"Parse Rate: {successful}/{total} models ({percentage:.1f}%)")
        print()

        # Show failed models
        failed_models = [name for name, success in results if not success]
        if failed_models:
            print("Failed models:")
            for model_name in failed_models:
                print(f"  - {model_name}")
        else:
            print("🎉 All models parsed successfully!")

    return successful, total, percentage


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Measure parse rate across GAMSLIB Tier 1 models")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed results for each model",
    )

    args = parser.parse_args()

    successful, total, percentage = measure_parse_rate(verbose=args.verbose)

    # Exit with code 0 if all models parsed, 1 otherwise
    sys.exit(0 if successful == total else 1)


if __name__ == "__main__":
    main()
