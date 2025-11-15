#!/usr/bin/env python3
"""
GAMSLib Parse Rate Regression Checker

Compares current parse rate against baseline to detect regressions.
Used by CI to fail builds if parse rate drops significantly.

Usage:
    python scripts/check_parse_rate_regression.py \\
        --current reports/gamslib_ingestion_sprint6.json \\
        --baseline origin/main \\
        --threshold 0.10

Exit codes:
    0: No regression (pass CI)
    1: Regression detected (fail CI)
    2: Error reading reports or invalid arguments
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def read_parse_rate_from_file(json_path: Path) -> tuple[float, dict[str, Any]]:
    """
    Read parse rate from a JSON ingestion report file.

    Args:
        json_path: Path to JSON report file

    Returns:
        Tuple of (parse_rate_percent, full_kpis_dict)

    Raises:
        FileNotFoundError: If JSON file doesn't exist
        json.JSONDecodeError: If JSON is malformed
        KeyError: If expected fields are missing
    """
    if not json_path.exists():
        raise FileNotFoundError(f"Report file not found: {json_path}")

    with open(json_path) as f:
        report = json.load(f)

    if "kpis" not in report:
        raise KeyError(f"Report missing 'kpis' field: {json_path}")

    kpis = report["kpis"]

    # Validate all required KPI fields
    required_fields = ["parse_rate_percent", "parse_success", "total_models"]
    for field in required_fields:
        if field not in kpis:
            raise KeyError(f"KPIs missing '{field}' field: {json_path}")

    parse_rate = kpis["parse_rate_percent"]

    return parse_rate, kpis


def read_parse_rate_from_git(branch: str, report_path: Path) -> tuple[float, dict[str, Any]]:
    """
    Read parse rate from a JSON report on a different git branch.

    Args:
        branch: Git branch name (e.g., "main", "origin/main")
        report_path: Path to JSON report file (relative to repo root)

    Returns:
        Tuple of (parse_rate_percent, full_kpis_dict)

    Raises:
        subprocess.CalledProcessError: If git command fails
        json.JSONDecodeError: If baseline JSON is malformed
        KeyError: If expected fields are missing
    """
    # Use git show to read file from branch
    result = subprocess.run(
        ["git", "show", f"{branch}:{report_path}"],
        capture_output=True,
        text=True,
        check=True,
    )

    report = json.loads(result.stdout)

    if "kpis" not in report:
        raise KeyError(f"Baseline report missing 'kpis' field (branch: {branch})")

    kpis = report["kpis"]

    # Validate all required KPI fields
    required_fields = ["parse_rate_percent", "parse_success", "total_models"]
    for field in required_fields:
        if field not in kpis:
            raise KeyError(f"Baseline KPIs missing '{field}' field (branch: {branch})")

    parse_rate = kpis["parse_rate_percent"]

    return parse_rate, kpis


def calculate_relative_drop(baseline: float, current: float) -> float:
    """
    Calculate relative drop from baseline to current.

    Args:
        baseline: Baseline parse rate (percentage)
        current: Current parse rate (percentage)

    Returns:
        Relative drop as decimal (e.g., 0.10 for 10% drop)
        Returns 0.0 if baseline is 0 (can't calculate relative drop)
    """
    if baseline == 0:
        return 0.0  # Can't regress from 0%

    return (baseline - current) / baseline


def check_regression(
    current_rate: float,
    baseline_rate: float,
    threshold: float,
    current_kpis: dict[str, Any],
    baseline_kpis: dict[str, Any],
) -> bool:
    """
    Check if current rate represents a regression.

    Args:
        current_rate: Current parse rate (percentage)
        baseline_rate: Baseline parse rate (percentage)
        threshold: Regression threshold (decimal, e.g., 0.10 for 10%)
        current_kpis: Current KPIs (for detailed reporting)
        baseline_kpis: Baseline KPIs (for detailed reporting)

    Returns:
        True if regression detected, False otherwise

    Side effects:
        Prints detailed regression report to stdout
    """
    relative_drop = calculate_relative_drop(baseline_rate, current_rate)

    # Check if regression exceeds threshold
    is_regression = relative_drop >= threshold

    # Print detailed report
    print("=" * 70)
    print("PARSE RATE REGRESSION CHECK")
    print("=" * 70)
    print()

    # Current vs baseline
    print(
        f"Current Parse Rate:  {current_rate}% ({current_kpis['parse_success']}/{current_kpis['total_models']} models)"
    )
    print(
        f"Baseline Parse Rate: {baseline_rate}% ({baseline_kpis['parse_success']}/{baseline_kpis['total_models']} models)"
    )
    print()

    # Calculate change
    absolute_change = current_rate - baseline_rate
    models_change = current_kpis["parse_success"] - baseline_kpis["parse_success"]

    print(f"Absolute Change: {absolute_change:+.1f} percentage points")
    print(f"Models Change:   {models_change:+d} models")
    print(f"Relative Drop:   {relative_drop * 100:+.1f}% (threshold: {threshold * 100:.1f}%)")
    print()

    # Verdict
    if is_regression:
        print("❌ REGRESSION DETECTED")
        print()
        print(
            f"Parse rate dropped by {relative_drop * 100:.1f}%, exceeding threshold of {threshold * 100:.1f}%"
        )
        print()
        print("Action required:")
        print("  1. Review recent parser changes")
        print("  2. Identify which models stopped parsing")
        print("  3. Fix parser or update test expectations")
        print("  4. Re-run ingestion to verify fix")
    elif current_rate > baseline_rate:
        print("✅ IMPROVEMENT: Parse rate increased!")
        print()
        print("No action needed. Great work!")
    elif current_rate == baseline_rate:
        print("✅ STABLE: Parse rate unchanged")
        print()
        print("No action needed.")
    else:
        # Drop within threshold
        print("✅ OK: Minor drop within acceptable threshold")
        print()
        print("No action needed. Variation is within expected range.")

    print("=" * 70)

    return is_regression


def main() -> None:
    """Main entry point for regression checker."""
    parser = argparse.ArgumentParser(
        description="Check for parse rate regressions in GAMSLib ingestion reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare current report against main branch
  python check_parse_rate_regression.py \\
      --current reports/gamslib_ingestion_sprint6.json \\
      --baseline origin/main \\
      --threshold 0.10

  # Compare two local reports
  python check_parse_rate_regression.py \\
      --current reports/current.json \\
      --baseline-file reports/baseline.json \\
      --threshold 0.05

Exit codes:
  0: No regression (pass)
  1: Regression detected (fail)
  2: Error reading reports
        """,
    )

    parser.add_argument(
        "--current",
        type=Path,
        required=True,
        help="Path to current ingestion report (JSON)",
    )

    parser.add_argument(
        "--baseline",
        type=str,
        help="Git branch name for baseline (e.g., 'main', 'origin/main'). The baseline report will be read from the same path as --current on this branch.",
    )

    parser.add_argument(
        "--baseline-file",
        type=Path,
        help="Path to baseline ingestion report (JSON) - alternative to --baseline",
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=0.10,
        help="Regression threshold as decimal (default: 0.10 for 10%%)",
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.baseline and not args.baseline_file:
        print("Error: Must specify either --baseline or --baseline-file", file=sys.stderr)
        sys.exit(2)

    if args.baseline and args.baseline_file:
        print("Error: Cannot specify both --baseline and --baseline-file", file=sys.stderr)
        sys.exit(2)

    if args.threshold < 0 or args.threshold > 1:
        print(f"Error: Threshold must be between 0 and 1 (got {args.threshold})", file=sys.stderr)
        sys.exit(2)

    try:
        # Read current parse rate
        current_rate, current_kpis = read_parse_rate_from_file(args.current)

        # Read baseline parse rate
        if args.baseline:
            # Read from git branch
            baseline_rate, baseline_kpis = read_parse_rate_from_git(args.baseline, args.current)
        else:
            # Read from file
            baseline_rate, baseline_kpis = read_parse_rate_from_file(args.baseline_file)

        # Check for regression
        is_regression = check_regression(
            current_rate,
            baseline_rate,
            args.threshold,
            current_kpis,
            baseline_kpis,
        )

        # Exit with appropriate code
        if is_regression:
            sys.exit(1)  # Fail CI
        else:
            sys.exit(0)  # Pass CI

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    except subprocess.CalledProcessError as e:
        print(f"Error reading baseline from git: {e}", file=sys.stderr)
        print(f"Command: {' '.join(e.cmd)}", file=sys.stderr)
        print(f"Stderr: {e.stderr}", file=sys.stderr)
        sys.exit(2)

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(2)

    except KeyError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
