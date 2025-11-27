#!/usr/bin/env python3
"""Performance baseline comparison script.

This script compares current performance metrics against baseline values
and applies thresholds to detect regressions.

Thresholds:
- 20% slower: Warning (log but pass)
- 50% slower: Failure (fail CI)

Usage:
    python scripts/compare_performance.py <current_results.json> <baseline.json>
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_json(filepath: Path) -> dict[str, Any]:
    """Load JSON file."""
    with open(filepath) as f:
        return json.load(f)


def compare_model_performance(
    model_name: str, current: dict[str, Any], baseline: dict[str, Any]
) -> dict[str, Any]:
    """Compare performance metrics for a single model.

    Args:
        model_name: Name of the model
        current: Current performance metrics
        baseline: Baseline performance metrics

    Returns:
        Dictionary with comparison results including deltas and status
    """
    result = {
        "model": model_name,
        "status": "pass",
        "warnings": [],
        "errors": [],
        "metrics": {},
    }

    # Compare parse_time_ms
    if "parse_time_ms" in current and "parse_time_ms" in baseline:
        current_time = current["parse_time_ms"]
        baseline_time = baseline["parse_time_ms"]

        if baseline_time > 0:
            delta_pct = ((current_time - baseline_time) / baseline_time) * 100
            result["metrics"]["parse_time_ms"] = {
                "current": current_time,
                "baseline": baseline_time,
                "delta_pct": delta_pct,
            }

            if delta_pct > 50:
                result["status"] = "fail"
                result["errors"].append(
                    f"Parse time regression: {delta_pct:.1f}% slower (threshold: 50%)"
                )
            elif delta_pct > 20:
                result["warnings"].append(
                    f"Parse time warning: {delta_pct:.1f}% slower (threshold: 20%)"
                )

    # Compare total_time_ms
    if "total_time_ms" in current and "total_time_ms" in baseline:
        current_time = current["total_time_ms"]
        baseline_time = baseline["total_time_ms"]

        if baseline_time > 0:
            delta_pct = ((current_time - baseline_time) / baseline_time) * 100
            result["metrics"]["total_time_ms"] = {
                "current": current_time,
                "baseline": baseline_time,
                "delta_pct": delta_pct,
            }

            if delta_pct > 50:
                result["status"] = "fail"
                result["errors"].append(
                    f"Total time regression: {delta_pct:.1f}% slower (threshold: 50%)"
                )
            elif delta_pct > 20:
                result["warnings"].append(
                    f"Total time warning: {delta_pct:.1f}% slower (threshold: 20%)"
                )

    return result


def compare_performance(
    current_file: Path, baseline_file: Path
) -> tuple[list[dict[str, Any]], bool]:
    """Compare current performance against baseline.

    Args:
        current_file: Path to current results JSON
        baseline_file: Path to baseline JSON

    Returns:
        Tuple of (comparison results, overall pass/fail)
    """
    current_data = load_json(current_file)
    baseline_data = load_json(baseline_file)

    # Get model data from both files
    current_models = current_data.get("models", {})
    baseline_models = baseline_data.get("models", {})

    results = []
    overall_pass = True

    # Compare each model
    for model_name in sorted(set(current_models.keys()) | set(baseline_models.keys())):
        if model_name not in current_models:
            results.append(
                {
                    "model": model_name,
                    "status": "skip",
                    "warnings": [f"Model not found in current results"],
                    "errors": [],
                    "metrics": {},
                }
            )
            continue

        if model_name not in baseline_models:
            results.append(
                {
                    "model": model_name,
                    "status": "new",
                    "warnings": [f"Model not found in baseline (new model)"],
                    "errors": [],
                    "metrics": {},
                }
            )
            continue

        comparison = compare_model_performance(
            model_name, current_models[model_name], baseline_models[model_name]
        )
        results.append(comparison)

        if comparison["status"] == "fail":
            overall_pass = False

    return results, overall_pass


def print_results(results: list[dict[str, Any]], overall_pass: bool) -> None:
    """Print comparison results in a readable format.

    Args:
        results: List of comparison results per model
        overall_pass: Overall pass/fail status
    """
    print("\n" + "=" * 80)
    print("PERFORMANCE BASELINE COMPARISON")
    print("=" * 80 + "\n")

    # Count statuses
    pass_count = sum(1 for r in results if r["status"] == "pass")
    warn_count = sum(1 for r in results if r["warnings"])
    fail_count = sum(1 for r in results if r["status"] == "fail")
    skip_count = sum(1 for r in results if r["status"] in ("skip", "new"))

    print(
        f"Summary: {pass_count} passed, {warn_count} warnings, {fail_count} failed, {skip_count} skipped\n"
    )

    # Print details for each model
    for result in results:
        model = result["model"]
        status = result["status"]

        if status == "pass" and not result["warnings"]:
            # Don't print details for passing models without warnings
            continue

        print(f"Model: {model}")
        print(f"Status: {status.upper()}")

        # Print metrics
        for metric_name, metric_data in result["metrics"].items():
            current = metric_data["current"]
            baseline = metric_data["baseline"]
            delta_pct = metric_data["delta_pct"]
            direction = "slower" if delta_pct > 0 else "faster"
            print(
                f"  {metric_name}: {current} ms (baseline: {baseline} ms, "
                f"{abs(delta_pct):.1f}% {direction})"
            )

        # Print warnings
        for warning in result["warnings"]:
            print(f"  ⚠️  WARNING: {warning}")

        # Print errors
        for error in result["errors"]:
            print(f"  ❌ ERROR: {error}")

        print()

    # Print overall result
    print("=" * 80)
    if overall_pass:
        print("✅ OVERALL RESULT: PASS")
    else:
        print("❌ OVERALL RESULT: FAIL")
    print("=" * 80 + "\n")


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for pass, 1 for fail)
    """
    parser = argparse.ArgumentParser(description="Compare current performance against baseline")
    parser.add_argument("current", type=Path, help="Path to current results JSON")
    parser.add_argument("baseline", type=Path, help="Path to baseline JSON")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    # Validate files exist
    if not args.current.exists():
        print(f"Error: Current results file not found: {args.current}", file=sys.stderr)
        return 1

    if not args.baseline.exists():
        print(f"Error: Baseline file not found: {args.baseline}", file=sys.stderr)
        return 1

    # Run comparison
    try:
        results, overall_pass = compare_performance(args.current, args.baseline)

        if args.json:
            # Output as JSON
            output = {"results": results, "overall_pass": overall_pass}
            print(json.dumps(output, indent=2))
        else:
            # Human-readable output
            print_results(results, overall_pass)

        return 0 if overall_pass else 1

    except Exception as e:
        print(f"Error during comparison: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
