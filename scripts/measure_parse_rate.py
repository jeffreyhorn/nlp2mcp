#!/usr/bin/env python3
"""
Measure parse rate and convert rate across GAMSLIB Tier 1 models.

This script tests parsing, IR generation, and MCP conversion success
for the 10 GAMSLIB Tier 1 models. It calculates:
- parse_rate: % of models that parse successfully
- convert_rate: % of models that complete full parse → IR → MCP pipeline

Usage:
    python scripts/measure_parse_rate.py [--verbose]

Exit codes:
    0: All models converted successfully (100% convert rate)
    1: Some models failed to convert (< 100% convert rate)
"""

import argparse
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.converter.converter import Converter  # noqa: E402
from src.ir.parser import parse_model_file  # noqa: E402

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


def test_convert(model_path: Path) -> tuple[bool, bool]:
    """
    Test if a model completes the full parse → IR → MCP pipeline.

    Args:
        model_path: Path to the GAMS model file

    Returns:
        Tuple of (parse_success, convert_success)
        - parse_success: True if parsing succeeded
        - convert_success: True if full pipeline (parse + IR + MCP) succeeded
    """
    try:
        # Step 1: Parse
        ir_model = parse_model_file(str(model_path))
        if ir_model is None:
            return False, False

        # Step 2: Convert to MCP
        converter = Converter(ir_model)
        result = converter.convert()

        # Conversion succeeds if result.success is True
        return True, result.success
    except Exception as e:
        # Parse failed - log error for debugging if needed
        # Note: Exceptions during parse indicate parse failure
        # We return (False, False) to indicate both parse and convert failed
        del e  # Suppress unused variable warning
        return False, False


def measure_parse_rate(verbose: bool = False) -> tuple[int, int, float, int, float]:
    """
    Measure parse rate and convert rate across GAMSLIB Tier 1 models.

    Args:
        verbose: If True, print detailed results for each model

    Returns:
        Tuple of (parse_count, total_count, parse_percentage, convert_count, convert_percentage)
    """
    results = []

    if verbose:
        print("Testing GAMSLIB Tier 1 models...")
        print("=" * 70)

    for model_name in TIER1_MODELS:
        model_path = GAMSLIB_DIR / model_name

        if not model_path.exists():
            if verbose:
                print(f"⚠️  {model_name:20s} - FILE NOT FOUND")
            results.append((model_name, False, False))
            continue

        parse_success, convert_success = test_convert(model_path)
        results.append((model_name, parse_success, convert_success))

        if verbose:
            if convert_success:
                status = "✅ CONVERT"
            elif parse_success:
                status = "⚠️  PARSE  "
            else:
                status = "❌ FAIL   "
            print(f"{status}  {model_name}")

    # Calculate statistics
    parse_successful = sum(1 for _, parse_ok, _ in results if parse_ok)
    convert_successful = sum(1 for _, _, convert_ok in results if convert_ok)
    total = len(results)
    parse_percentage = (parse_successful / total * 100) if total > 0 else 0.0
    convert_percentage = (convert_successful / total * 100) if total > 0 else 0.0

    if verbose:
        print("=" * 70)
        print(f"Parse Rate:   {parse_successful}/{total} models ({parse_percentage:.1f}%)")
        print(f"Convert Rate: {convert_successful}/{total} models ({convert_percentage:.1f}%)")
        print()

        # Show failed models
        parse_failed = [name for name, parse_ok, _ in results if not parse_ok]
        convert_failed = [
            name for name, parse_ok, convert_ok in results if parse_ok and not convert_ok
        ]

        if parse_failed:
            print("Parse failures:")
            for model_name in parse_failed:
                print(f"  - {model_name}")
            print()

        if convert_failed:
            print("Conversion failures (parsed but didn't convert):")
            for model_name in convert_failed:
                print(f"  - {model_name}")
            print()

        if not parse_failed and not convert_failed:
            print("🎉 All models parsed and converted successfully!")

    return parse_successful, total, parse_percentage, convert_successful, convert_percentage


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Measure parse rate and convert rate across GAMSLIB Tier 1 models"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed results for each model",
    )

    args = parser.parse_args()

    parse_count, total, parse_pct, convert_count, convert_pct = measure_parse_rate(
        verbose=args.verbose
    )

    # Exit with code 0 if all models converted, 1 otherwise
    sys.exit(0 if convert_count == total else 1)


if __name__ == "__main__":
    main()
