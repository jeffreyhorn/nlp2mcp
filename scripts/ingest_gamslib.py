#!/usr/bin/env python3
"""
GAMSLib Model Ingestion Script

Ingests GAMSLib models by attempting to parse each one and recording results.
Generates a JSON report with parse success/failure status and KPI metrics.
Optionally generates a Markdown dashboard for easy viewing.

Usage:
    python scripts/ingest_gamslib.py \
        --input tests/fixtures/gamslib \
        --output reports/gamslib_ingestion_sprint6.json \
        --dashboard docs/status/GAMSLIB_CONVERSION_STATUS.md

Sprint 6 Scope:
    - Parse-only validation (no MCP conversion or PATH solving)
    - 10 Tier 1 models
    - Baseline metrics: parse%, convert%, solve%
    - Markdown dashboard generation
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ir.parser import parse_model_file
from src.utils.parse_progress import (
    calculate_parse_progress_from_file,
    extract_error_line,
    extract_missing_features,
)


@dataclass
class ModelResult:
    """Result of ingesting a single GAMS model."""

    model_name: str
    gms_file: str
    parse_status: str  # "SUCCESS" or "FAILED"
    parse_error: str | None = None
    parse_error_type: str | None = None
    # Sprint 8 Day 7: Partial parse metrics
    parse_progress_percentage: float | None = None
    parse_progress_lines_parsed: int | None = None
    parse_progress_lines_total: int | None = None
    missing_features: list[str] | None = None


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
        ModelResult with parse status, error details, and partial parse metrics
    """
    model_name = gms_path.stem

    try:
        # Attempt to parse the model
        parse_model_file(gms_path)

        # Success - calculate progress (100%)
        progress = calculate_parse_progress_from_file(gms_path, error=None)

        return ModelResult(
            model_name=model_name,
            gms_file=gms_path.name,
            parse_status="SUCCESS",
            parse_error=None,
            parse_error_type=None,
            parse_progress_percentage=progress["percentage"],
            parse_progress_lines_parsed=progress["lines_parsed"],
            parse_progress_lines_total=progress["lines_total"],
            missing_features=[],
        )

    except Exception as e:
        # Parse failed - capture error details and calculate partial progress
        error_message = str(e)
        error_type = type(e).__name__

        # Read source once for both progress calculation and feature extraction
        source = gms_path.read_text()

        # Calculate partial parse progress
        from src.utils.parse_progress import calculate_parse_progress

        progress = calculate_parse_progress(source, error=e)

        # Extract missing features from error
        error_line = extract_error_line(e)
        source_line = None
        if error_line and 0 < error_line <= len(source.split("\n")):
            source_line = source.split("\n")[error_line - 1]

        features = extract_missing_features(error_type, error_message, source_line)

        return ModelResult(
            model_name=model_name,
            gms_file=gms_path.name,
            parse_status="FAILED",
            parse_error=error_message,
            parse_error_type=error_type,
            parse_progress_percentage=progress["percentage"],
            parse_progress_lines_parsed=progress["lines_parsed"],
            parse_progress_lines_total=progress["lines_total"],
            missing_features=features,
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
        sprint="Sprint 8",
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


def generate_dashboard(report: IngestionReport, output_path: Path, json_report_path: Path) -> None:
    """
    Generate Markdown dashboard from ingestion report.

    Args:
        report: IngestionReport with ingestion results
        output_path: Path to write dashboard Markdown file
        json_report_path: Path to JSON report (for reference link)
    """
    sections = []

    # Header
    sections.append(_generate_header(report, json_report_path))

    # KPI Summary
    sections.append(_generate_kpi_summary(report.kpis))

    # Model Results Table
    sections.append(_generate_model_table(report.models))

    # Error Breakdown
    sections.append(_generate_error_breakdown(report.models))

    # Failure Details
    sections.append(_generate_failure_details(report.models))

    # Write dashboard
    output_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_content = "\n\n".join(sections)

    with open(output_path, "w") as f:
        f.write(markdown_content)

    print(f"Dashboard written to: {output_path}")


def _generate_header(report: IngestionReport, json_report_path: Path) -> str:
    """Generate dashboard header section."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""# GAMSLib Conversion Status Dashboard

**Generated:** {timestamp}
**Sprint:** {report.sprint}
**Total Models:** {report.total_models}
**Report:** [`{json_report_path.name}`](../../{json_report_path})

---"""


def _generate_kpi_summary(kpis: dict[str, Any]) -> str:
    """Generate KPI summary table."""
    parse_rate = kpis["parse_rate_percent"]
    convert_rate = kpis["convert_rate_percent"]
    solve_rate = kpis["solve_rate_percent"]

    # Calculate E2E rate (models that successfully parsed, converted, and solved)
    e2e_rate = 0.0  # Sprint 6: No models have completed full pipeline yet

    # Determine status icons
    parse_icon = "✅" if parse_rate >= 10.0 else "❌"
    convert_icon = "⚠️"  # Sprint 6: Not yet implemented
    solve_icon = "⚠️"  # Sprint 6: Not yet implemented
    e2e_icon = "⚠️"  # Sprint 6: Not yet implemented

    # Display "N/A" for solve rate denominator if convert_success is 0
    solve_display = (
        f"{kpis['solve_success']}/{kpis['convert_success']}"
        if kpis["convert_success"] > 0
        else "N/A"
    )

    return f"""## Overall KPIs

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Parse Rate** | {parse_rate}% ({kpis["parse_success"]}/{kpis["total_models"]}) | ≥10% | {parse_icon} |
| **Convert Rate** | {convert_rate}% ({kpis["convert_success"]}/{kpis["parse_success"]}) | ≥50% | {convert_icon} Sprint 6: Not implemented |
| **Solve Rate** | {solve_rate}% ({solve_display}) | TBD | {solve_icon} Sprint 6: Not implemented |
| **End-to-End** | {e2e_rate}% (0/{kpis["total_models"]}) | TBD | {e2e_icon} Sprint 6: Not implemented |

**Sprint 6 Target:** {parse_icon} Parse ≥1 model (≥10% rate) - {"✅ MET" if kpis["meets_sprint6_targets"] else "❌ NOT MET"}

---"""


def _generate_model_table(models: list[ModelResult]) -> str:
    """Generate per-model status table with Sprint 8 enhancements."""

    def determine_status_symbol(model: ModelResult) -> str:
        """Determine color-coded status symbol based on parse percentage."""
        percentage = model.parse_progress_percentage or 0.0

        if model.parse_status == "SUCCESS":
            return "✅ PASS"
        elif percentage >= 75.0:
            return "🟡 MOSTLY PARSED"
        elif percentage >= 25.0:
            return "⚠️ PARTIALLY PARSED"
        else:
            return "❌ FAIL"

    def format_progress(model: ModelResult) -> str:
        """Format progress column."""
        if model.parse_progress_percentage is None:
            return "-"

        pct = model.parse_progress_percentage
        parsed = model.parse_progress_lines_parsed or 0
        total = model.parse_progress_lines_total or 0

        return f"{pct:.0f}% ({parsed}/{total})"

    def format_missing_features(model: ModelResult) -> str:
        """Format missing features column."""
        if not model.missing_features:
            return "-"

        # Join with commas, limit to 2 for readability, indicate if more
        features = model.missing_features[:2]
        more_count = len(model.missing_features) - 2
        if more_count > 0:
            return f"{', '.join(features)} (+{more_count} more)"
        return ", ".join(features)

    rows = []
    for model in models:
        # Sprint 8: Enhanced status with color coding
        status = determine_status_symbol(model)
        progress = format_progress(model)
        missing = format_missing_features(model)

        # Convert/Solve/E2E columns (unchanged)
        convert = "-"  # Not yet implemented
        solve = "-"  # Not yet implemented
        e2e = "❌"  # No complete pipeline yet

        rows.append(
            f"| {model.model_name} | {status} | {progress} | {missing} | {convert} | {solve} | {e2e} |"
        )

    return (
        f"""## Model Status

| Model | Status | Progress | Missing Features | Convert | Solve | E2E |
|-------|--------|----------|------------------|---------|-------|-----|
"""
        + "\n".join(rows)
        + """

**Legend:**
- ✅ PASS: 100% parsed successfully
- 🟡 MOSTLY PARSED: 75-99% parsed
- ⚠️ PARTIALLY PARSED: 25-74% parsed
- ❌ FAIL: <25% parsed
- `-` Not attempted (stage not implemented yet)

---"""
    )


def _generate_error_breakdown(models: list[ModelResult]) -> str:
    """Generate error breakdown by category."""
    # Count parse errors by type
    parse_errors: dict[str, list[str]] = {}
    for model in models:
        if model.parse_status == "FAILED" and model.parse_error_type:
            error_type = model.parse_error_type
            parse_errors.setdefault(error_type, []).append(model.model_name)

    if not parse_errors:
        return """## Error Breakdown

**No errors!** All models parsed successfully. 🎉

---"""

    sections = ["## Error Breakdown", "", "### Parse Errors"]

    # Sort by count (most common first)
    sorted_errors = sorted(parse_errors.items(), key=lambda x: len(x[1]), reverse=True)

    sections.append("| Error Type | Count | Models |")
    sections.append("|------------|-------|--------|")

    for error_type, model_names in sorted_errors:
        count = len(model_names)
        models_str = ", ".join(model_names)
        sections.append(f"| `{error_type}` | {count} | {models_str} |")

    sections.append("")
    sections.append(
        "**Note:** Convert and solve errors will appear here once those stages are implemented."
    )
    sections.append("")
    sections.append("---")

    return "\n".join(sections)


def _generate_failure_details(models: list[ModelResult]) -> str:
    """Generate detailed failure information with Sprint 8 enhancements."""
    failures = [m for m in models if m.parse_status == "FAILED"]

    if not failures:
        return """## Failure Details

**No failures!** All models parsed successfully. 🎉"""

    sections = ["## Failure Details", ""]

    for model in failures:
        sections.append(f"### {model.gms_file}")
        sections.append(f"**Model:** {model.model_name}")
        sections.append(f"**Status:** Parse Failed")

        # Sprint 8: Add parse progress information
        if model.parse_progress_percentage is not None:
            pct = model.parse_progress_percentage
            parsed = model.parse_progress_lines_parsed or 0
            total = model.parse_progress_lines_total or 0
            sections.append(f"**Progress:** {pct:.0f}% ({parsed}/{total} lines parsed)")

        # Sprint 8: Add missing features
        if model.missing_features:
            features_str = ", ".join(model.missing_features)
            sections.append(f"**Missing Features:** {features_str}")

        sections.append(f"**Error Type:** `{model.parse_error_type}`")
        sections.append(f"**Error Message:**")
        sections.append("```")
        sections.append(model.parse_error or "Unknown error")
        sections.append("```")
        sections.append("")

    return "\n".join(sections)


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
    parser.add_argument(
        "--dashboard",
        type=Path,
        help="Optional: Generate Markdown dashboard (e.g., docs/status/GAMSLIB_CONVERSION_STATUS.md)",
    )

    args = parser.parse_args()

    if not args.input.is_dir():
        print(f"ERROR: Input directory does not exist: {args.input}")
        sys.exit(1)

    ingest_gamslib(args.input, args.output)

    # Generate dashboard if requested
    if args.dashboard:
        # Reload the report from JSON to get the report object
        with open(args.output) as f:
            report_data = json.load(f)

        # Reconstruct report object
        models = [ModelResult(**m) for m in report_data["models"]]
        report = IngestionReport(
            sprint=report_data["sprint"],
            total_models=report_data["total_models"],
            models=models,
            kpis=report_data["kpis"],
        )

        generate_dashboard(report, args.dashboard, args.output)
        print()
        print(f"✅ Dashboard generated at: {args.dashboard}")


if __name__ == "__main__":
    main()
