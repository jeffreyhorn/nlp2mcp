#!/usr/bin/env python3
"""
GAMSLib Model Ingestion Script

Ingests GAMSLib models by attempting to parse each one and recording results.
Generates a JSON report with parse success/failure status and KPI metrics.

Usage:
    python scripts/ingest_gamslib.py \
        --input tests/fixtures/gamslib \
        --output reports/gamslib_ingestion_sprint6.json

Sprint 6 Scope:
    - Parse-only validation (no MCP conversion or PATH solving)
    - 10 Tier 1 models
    - Baseline metrics: parse%, convert%, solve%
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ir.parser import parse_model_file


@dataclass
class ModelResult:
    """Result of ingesting a single GAMS model."""

    model_name: str
    gms_file: str
    parse_status: str  # "SUCCESS" or "FAILED"
    parse_error: str | None = None
    parse_error_type: str | None = None


@dataclass
class IngestionReport:
    """Complete ingestion report with KPI metrics."""

    sprint: str
    total_models: int
    models: list[ModelResult]
    kpis: dict[str, Any]


def parse_model(gms_path: Path) -> ModelResult:
    """
    Attempt to parse a GAMS model file.

    Args:
        gms_path: Path to .gms file

    Returns:
        ModelResult with parse status and error details
    """
    model_name = gms_path.stem

    try:
        # Attempt to parse the model
        parse_model_file(gms_path)

        return ModelResult(
            model_name=model_name,
            gms_file=gms_path.name,
            parse_status="SUCCESS",
            parse_error=None,
            parse_error_type=None,
        )

    except Exception as e:
        # Parse failed - capture error details
        error_message = str(e)
        error_type = type(e).__name__

        return ModelResult(
            model_name=model_name,
            gms_file=gms_path.name,
            parse_status="FAILED",
            parse_error=error_message,
            parse_error_type=error_type,
        )


def calculate_kpis(models: list[ModelResult]) -> dict[str, Any]:
    """
    Calculate KPI metrics from ingestion results.

    KPIs (Sprint 6):
        - parse%: Percentage of models that parsed successfully
        - convert%: N/A (not implemented yet, set to 0)
        - solve%: N/A (not implemented yet, set to 0)

    Args:
        models: List of ModelResult objects

    Returns:
        Dictionary of KPI metrics
    """
    total = len(models)
    parse_success = sum(1 for m in models if m.parse_status == "SUCCESS")

    parse_rate = (parse_success / total * 100) if total > 0 else 0.0

    return {
        "total_models": total,
        "parse_success": parse_success,
        "parse_failed": total - parse_success,
        "parse_rate_percent": round(parse_rate, 1),
        # Sprint 6: Convert and solve not yet implemented
        "convert_success": 0,
        "convert_failed": 0,
        "convert_rate_percent": 0.0,
        "solve_success": 0,
        "solve_failed": 0,
        "solve_rate_percent": 0.0,
        # Sprint 6 targets
        "sprint6_target_models": 10,
        "sprint6_target_parse_rate": 10.0,  # ≥10%
        "sprint6_target_convert_rate": 50.0,  # ≥50% (of parsed)
        "meets_sprint6_targets": parse_success >= 1 and parse_rate >= 10.0,
    }


def ingest_gamslib(input_dir: Path, output_file: Path) -> None:
    """
    Main ingestion function.

    Args:
        input_dir: Directory containing .gms files
        output_file: Path to write JSON report
    """
    print(f"Starting GAMSLib ingestion from: {input_dir}")

    # Find all .gms files
    gms_files = sorted(input_dir.glob("*.gms"))

    if not gms_files:
        print(f"ERROR: No .gms files found in {input_dir}")
        sys.exit(1)

    print(f"Found {len(gms_files)} model(s)")
    print()

    # Parse each model
    results: list[ModelResult] = []
    for gms_file in gms_files:
        print(f"Parsing: {gms_file.name}...", end=" ")
        result = parse_model(gms_file)

        if result.parse_status == "SUCCESS":
            print("✅ SUCCESS")
        else:
            print(f"❌ FAILED ({result.parse_error_type})")

        results.append(result)

    print()

    # Calculate KPIs
    kpis = calculate_kpis(results)

    # Create report
    report = IngestionReport(
        sprint="Sprint 6",
        total_models=len(results),
        models=results,
        kpis=kpis,
    )

    # Write JSON report
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(asdict(report), f, indent=2)

    print(f"Report written to: {output_file}")
    print()

    # Display summary
    print("=" * 60)
    print("INGESTION SUMMARY")
    print("=" * 60)
    print(f"Total Models: {kpis['total_models']}")
    print(f"Parse Success: {kpis['parse_success']}")
    print(f"Parse Failed: {kpis['parse_failed']}")
    print(f"Parse Rate: {kpis['parse_rate_percent']}%")
    print()
    print(f"Sprint 6 Target: ≥{kpis['sprint6_target_parse_rate']}% parse rate")
    print(f"Meets Target: {'✅ YES' if kpis['meets_sprint6_targets'] else '❌ NO'}")
    print("=" * 60)

    # Display parse failures (if any)
    failures = [m for m in results if m.parse_status == "FAILED"]
    if failures:
        print()
        print("PARSE FAILURES:")
        print("-" * 60)
        for failure in failures:
            print(f"  {failure.model_name}: {failure.parse_error_type}")
            if failure.parse_error:
                # Truncate long error messages
                error_preview = failure.parse_error[:80]
                if len(failure.parse_error) > 80:
                    error_preview += "..."
                print(f"    {error_preview}")
        print("-" * 60)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest GAMSLib models and generate metrics report"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("tests/fixtures/gamslib"),
        help="Directory containing .gms files (default: tests/fixtures/gamslib)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/gamslib_ingestion_sprint6.json"),
        help="Output JSON report file (default: reports/gamslib_ingestion_sprint6.json)",
    )

    args = parser.parse_args()

    if not args.input.is_dir():
        print(f"ERROR: Input directory does not exist: {args.input}")
        sys.exit(1)

    ingest_gamslib(args.input, args.output)


if __name__ == "__main__":
    main()
