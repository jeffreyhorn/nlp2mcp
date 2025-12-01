#!/usr/bin/env python3
"""
Measure parse rate and convert rate across GAMSLIB Tier 1 models.

This script tests parsing, IR generation, and MCP conversion success
for the 10 GAMSLIB Tier 1 models. It calculates:
- parse_rate: % of models that parse successfully
- convert_rate: % of models that complete full parse → IR → MCP pipeline

Usage:
    python scripts/measure_parse_rate.py [--verbose]
    python scripts/measure_parse_rate.py --all-metrics [--output FILE]

Exit codes:
    0: All models converted successfully (100% convert rate)
    1: Some models failed to convert (< 100% convert rate)
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
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
    except Exception:
        # Parse or conversion failed
        # Exceptions during parse indicate parse failure
        # We return (False, False) to indicate both parse and convert failed
        return False, False


def test_convert_with_timing(model_path: Path) -> tuple[bool, bool, float, float]:
    """
    Test if a model completes the full parse → IR → MCP pipeline with timing.

    Args:
        model_path: Path to the GAMS model file

    Returns:
        Tuple of (parse_success, convert_success, parse_time_ms, total_time_ms)
        - parse_success: True if parsing succeeded
        - convert_success: True if full pipeline succeeded
        - parse_time_ms: Parse time in milliseconds
        - total_time_ms: Total time (parse + convert) in milliseconds
    """
    total_start = time.perf_counter()

    # Step 1: Parse with timing
    try:
        parse_start = time.perf_counter()
        ir_model = parse_model_file(str(model_path))
        parse_time_ms = (time.perf_counter() - parse_start) * 1000
    except Exception:
        total_time_ms = (time.perf_counter() - total_start) * 1000
        return False, False, 0.0, total_time_ms

    if ir_model is None:
        total_time_ms = (time.perf_counter() - total_start) * 1000
        return False, False, parse_time_ms, total_time_ms

    # Step 2: Convert to MCP
    try:
        converter = Converter(ir_model)
        result = converter.convert()
        total_time_ms = (time.perf_counter() - total_start) * 1000
        return True, result.success, parse_time_ms, total_time_ms
    except Exception:
        total_time_ms = (time.perf_counter() - total_start) * 1000
        return True, False, parse_time_ms, total_time_ms


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


def measure_all_metrics(verbose: bool = False) -> dict:
    """
    Measure all metrics (parse rate, convert rate, performance) with timing data.

    Args:
        verbose: If True, print detailed results for each model

    Returns:
        Dictionary with per-model and aggregate metrics in multi-metric baseline format
    """
    results = []

    if verbose:
        print("Measuring all metrics for GAMSLIB Tier 1 models...")
        print("=" * 70)

    for model_name in TIER1_MODELS:
        model_path = GAMSLIB_DIR / model_name

        if not model_path.exists():
            if verbose:
                print(f"⚠️  {model_name:20s} - FILE NOT FOUND")
            results.append(
                {
                    "name": model_name,
                    "parse_success": False,
                    "convert_success": False,
                    "parse_time_ms": 0.0,
                    "total_time_ms": 0.0,
                }
            )
            continue

        parse_success, convert_success, parse_time_ms, total_time_ms = test_convert_with_timing(
            model_path
        )
        results.append(
            {
                "name": model_name,
                "parse_success": parse_success,
                "convert_success": convert_success,
                "parse_time_ms": round(parse_time_ms, 2),
                "total_time_ms": round(total_time_ms, 2),
            }
        )

        if verbose:
            if convert_success:
                status = "✅ CONVERT"
            elif parse_success:
                status = "⚠️  PARSE  "
            else:
                status = "❌ FAIL   "
            print(
                f"{status}  {model_name:20s}  Parse: {parse_time_ms:6.2f}ms  Total: {total_time_ms:6.2f}ms"
            )

    # Calculate aggregate statistics
    total_models = len(results)
    parsed_models = sum(1 for r in results if r["parse_success"])
    converted_models = sum(1 for r in results if r["convert_success"])

    parse_rate = parsed_models / total_models if total_models > 0 else 0.0
    convert_rate = converted_models / total_models if total_models > 0 else 0.0

    # Average timing only for successful models
    successful_parse_times = [r["parse_time_ms"] for r in results if r["parse_success"]]
    successful_total_times = [r["total_time_ms"] for r in results if r["convert_success"]]

    avg_parse_time_ms = (
        round(sum(successful_parse_times) / len(successful_parse_times), 2)
        if successful_parse_times
        else 0.0
    )
    avg_total_time_ms = (
        round(sum(successful_total_times) / len(successful_total_times), 2)
        if successful_total_times
        else 0.0
    )

    # Get git commit
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=PROJECT_ROOT,
        ).stdout.strip()
    except subprocess.CalledProcessError:
        commit = "unknown"

    # Build per-model metrics dict
    models_dict = {}
    for r in results:
        models_dict[r["name"]] = {
            "parse_rate": 1.0 if r["parse_success"] else 0.0,
            "convert_rate": 1.0 if r["convert_success"] else 0.0,
            "parse_time_ms": r["parse_time_ms"],
            "total_time_ms": r["total_time_ms"],
        }

    # Build output dictionary
    output = {
        "schema_version": "1.0.0",
        "sprint": "sprint12",
        "checkpoint": "Day 3 - Validation and Analysis",
        "commit": commit,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model_set": "tier1",
        "models": models_dict,
        "summary": {
            "total_models": total_models,
            "parse_rate": parse_rate,
            "parse_rate_pct": round(parse_rate * 100, 2),
            "parsed_models": parsed_models,
            "convert_rate": convert_rate,
            "convert_rate_pct": round(convert_rate * 100, 2),
            "converted_models": converted_models,
            "avg_parse_time_ms": avg_parse_time_ms,
            "avg_total_time_ms": avg_total_time_ms,
        },
    }

    if verbose:
        print("=" * 70)
        print(f"Parse Rate:     {parsed_models}/{total_models} models ({parse_rate * 100:.1f}%)")
        print(
            f"Convert Rate:   {converted_models}/{total_models} models ({convert_rate * 100:.1f}%)"
        )
        print(f"Avg Parse Time: {avg_parse_time_ms:.2f}ms")
        print(f"Avg Total Time: {avg_total_time_ms:.2f}ms")
        print()

    return output


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
    parser.add_argument(
        "--all-metrics",
        action="store_true",
        help="Collect all metrics (parse rate, convert rate, performance) and output JSON",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file for --all-metrics JSON (default: stdout)",
    )

    args = parser.parse_args()

    # Handle --all-metrics mode
    if args.all_metrics:
        metrics = measure_all_metrics(verbose=args.verbose)

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(metrics, f, indent=2)
            if args.verbose:
                print(f"✅ Metrics written to {output_path}")
        else:
            # Print to stdout
            print(json.dumps(metrics, indent=2))

        # Exit with code 0 if all models converted, 1 otherwise
        total = metrics["summary"]["total_models"]
        converted = metrics["summary"]["converted_models"]
        sys.exit(0 if converted == total else 1)

    # Legacy mode (original behavior)
    parse_count, total, parse_pct, convert_count, convert_pct = measure_parse_rate(
        verbose=args.verbose
    )

    # Exit with code 0 if all models converted, 1 otherwise
    sys.exit(0 if convert_count == total else 1)


if __name__ == "__main__":
    main()
