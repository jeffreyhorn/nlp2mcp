#!/usr/bin/env python3
"""
GAMSLib Parse Rate Regression Checker

This script compares the current parse rate against a baseline to detect regressions.
Used in CI to prevent merging changes that significantly reduce parse rate.

Usage:
    python scripts/check_parse_rate_regression.py \\
        --current reports/gamslib_ingestion_sprint6.json \\
        --baseline origin/main \\
        --threshold 0.10

Exit codes:
    0 - No regression (parse rate stable or improved)
    1 - Regression detected (parse rate dropped >threshold)
    2 - Error (invalid arguments, missing files, etc.)
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def read_parse_rate(json_path: str) -> float:
    """
    Read parse rate from JSON report.

    Args:
        json_path: Path to GAMSLib ingestion JSON report

    Returns:
        Parse rate as percentage (0.0-100.0)

    Raises:
        FileNotFoundError: If JSON file doesn't exist
        KeyError: If 'kpis' or 'parse_rate_percent' not in JSON
        json.JSONDecodeError: If JSON is malformed
    """
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"Report not found: {json_path}")

    with open(path) as f:
        report = json.load(f)

    if "kpis" not in report:
        raise KeyError(f"Missing 'kpis' key in {json_path}")

    if "parse_rate_percent" not in report["kpis"]:
        raise KeyError(f"Missing 'parse_rate_percent' in kpis of {json_path}")

    return float(report["kpis"]["parse_rate_percent"])


def read_baseline_from_git(baseline_ref: str, report_path: str) -> float:
    """
    Read baseline parse rate from a git reference (branch/commit).

    Args:
        baseline_ref: Git reference (e.g., 'origin/main', 'HEAD~1')
        report_path: Path to report file relative to repo root

    Returns:
        Baseline parse rate as percentage (0.0-100.0)

    Raises:
        subprocess.CalledProcessError: If git command fails
        KeyError: If report structure invalid
        json.JSONDecodeError: If JSON is malformed
    """
    # Use git show to read file from baseline ref
    result = subprocess.run(
        ["git", "show", f"{baseline_ref}:{report_path}"],
        capture_output=True,
        text=True,
        check=True,
    )

    baseline_report = json.loads(result.stdout)

    if "kpis" not in baseline_report:
        raise KeyError(f"Missing 'kpis' in baseline report from {baseline_ref}")

    if "parse_rate_percent" not in baseline_report["kpis"]:
        raise KeyError(f"Missing 'parse_rate_percent' in baseline from {baseline_ref}")

    return float(baseline_report["kpis"]["parse_rate_percent"])


def check_regression(current: float, baseline: float, threshold: float) -> bool:
    """
    Check if current parse rate represents a regression from baseline.

    A regression occurs when the relative drop exceeds the threshold:
        (baseline - current) / baseline > threshold

    Args:
        current: Current parse rate (0.0-100.0)
        baseline: Baseline parse rate (0.0-100.0)
        threshold: Regression threshold as fraction (e.g., 0.10 for 10%)

    Returns:
        True if regression detected, False otherwise

    Edge cases:
        - If baseline is 0%, cannot regress (returns False)
        - If current >= baseline, improvement (returns False)
    """
    # Edge case: Can't regress from 0%
    if baseline == 0:
        return False

    # Calculate relative drop
    relative_drop = (baseline - current) / baseline

    # Regression if drop exceeds threshold
    return relative_drop > threshold


def format_models_info(current: float, baseline: float, total_models: int) -> str:
    """
    Format human-readable model count comparison.

    Args:
        current: Current parse rate (0.0-100.0)
        baseline: Baseline parse rate (0.0-100.0)
        total_models: Total number of models tested

    Returns:
        Formatted string showing model counts
    """
    current_count = int(current * total_models / 100)
    baseline_count = int(baseline * total_models / 100)
    delta = current_count - baseline_count

    delta_str = f"{delta:+d}" if delta != 0 else "0"

    return (
        f"  Current:  {current_count}/{total_models} models ({current:.1f}%)\n"
        f"  Baseline: {baseline_count}/{total_models} models ({baseline:.1f}%)\n"
        f"  Delta:    {delta_str} models"
    )


def main() -> int:
    """
    Main entry point for regression checker.

    Returns:
        Exit code (0 = no regression, 1 = regression, 2 = error)
    """
    parser = argparse.ArgumentParser(
        description="Check GAMSLib parse rate for regressions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--current",
        required=True,
        help="Path to current GAMSLib ingestion JSON report",
    )

    parser.add_argument(
        "--baseline",
        required=True,
        help="Git reference for baseline (e.g., 'origin/main', 'HEAD~1')",
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=0.10,
        help="Regression threshold as fraction (default: 0.10 = 10%%)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed comparison even on success",
    )

    args = parser.parse_args()

    try:
        # Read current parse rate
        current_rate = read_parse_rate(args.current)

        # Read baseline from git
        baseline_rate = read_baseline_from_git(args.baseline, args.current)

        # Assume 10 models for Sprint 6 (TODO: read from report)
        total_models = 10

        # Check for regression
        is_regression = check_regression(current_rate, baseline_rate, args.threshold)

        if is_regression:
            # Regression detected - fail CI
            relative_drop = (baseline_rate - current_rate) / baseline_rate
            print("❌ REGRESSION DETECTED")
            print()
            print(f"Parse rate dropped from {baseline_rate:.1f}% to {current_rate:.1f}%")
            print(
                f"Relative drop: {relative_drop * 100:.1f}% (threshold: {args.threshold * 100:.0f}%)"
            )
            print()
            print(format_models_info(current_rate, baseline_rate, total_models))
            print()
            print("This regression blocks CI. Please investigate:")
            print("  1. Check what parser changes may have broken existing models")
            print("  2. Run 'make ingest-gamslib' to see detailed error messages")
            print("  3. Fix the parser or adjust test models if the change is intentional")
            return 1

        elif current_rate > baseline_rate:
            # Improvement - celebrate!
            improvement = (current_rate - baseline_rate) / baseline_rate * 100
            print("✅ IMPROVEMENT!")
            print()
            print(f"Parse rate improved from {baseline_rate:.1f}% to {current_rate:.1f}%")
            print(f"Relative improvement: +{improvement:.1f}%")
            print()
            print(format_models_info(current_rate, baseline_rate, total_models))
            return 0

        elif current_rate == baseline_rate:
            # Unchanged
            if args.verbose:
                print("✅ OK")
                print()
                print(f"Parse rate unchanged: {current_rate:.1f}%")
                print()
                print(format_models_info(current_rate, baseline_rate, total_models))
            else:
                print(f"✅ OK: Parse rate {current_rate:.1f}% (baseline {baseline_rate:.1f}%)")
            return 0

        else:
            # Small drop within threshold
            relative_drop = (baseline_rate - current_rate) / baseline_rate
            if args.verbose:
                print("✅ OK (small drop within threshold)")
                print()
                print(f"Parse rate: {current_rate:.1f}% (baseline {baseline_rate:.1f}%)")
                print(
                    f"Relative drop: {relative_drop * 100:.1f}% (threshold: {args.threshold * 100:.0f}%)"
                )
                print()
                print(format_models_info(current_rate, baseline_rate, total_models))
            else:
                print(
                    f"✅ OK: Parse rate {current_rate:.1f}% (baseline {baseline_rate:.1f}%, "
                    f"drop {relative_drop * 100:.1f}% < threshold {args.threshold * 100:.0f}%)"
                )
            return 0

    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}", file=sys.stderr)
        print(
            "\nMake sure to run 'make ingest-gamslib' before checking for regressions.",
            file=sys.stderr,
        )
        return 2

    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: Failed to read baseline from git", file=sys.stderr)
        print(f"Git command failed: {e}", file=sys.stderr)
        print(
            f"\nMake sure baseline reference '{args.baseline}' exists.",
            file=sys.stderr,
        )
        return 2

    except (KeyError, json.JSONDecodeError) as e:
        print(f"❌ ERROR: Invalid JSON report format", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        return 2

    except Exception as e:
        print(f"❌ ERROR: Unexpected error", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
