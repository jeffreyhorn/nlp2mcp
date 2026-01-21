#!/usr/bin/env python3
"""
CLI tool for generating pipeline reports.

Generates status and failure analysis reports from baseline metrics.

Usage:
    python -m src.reporting.generate_report --type=status
    python -m src.reporting.generate_report --type=failure
    python -m src.reporting.generate_report --type=all
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.reporting.analyzers.failure_analyzer import FailureAnalyzer
from src.reporting.analyzers.status_analyzer import StatusAnalyzer
from src.reporting.data_loader import DataLoadError, load_baseline_metrics
from src.reporting.renderers.markdown_renderer import MarkdownRenderer, RenderError

# Default paths
DEFAULT_BASELINE_PATH = Path("data/gamslib/baseline_metrics.json")
DEFAULT_OUTPUT_DIR = Path("docs/testing")


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="generate_report",
        description="Generate pipeline status and failure analysis reports.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    Generate status report:
        python -m src.reporting.generate_report --type=status

    Generate failure analysis:
        python -m src.reporting.generate_report --type=failure

    Generate all reports:
        python -m src.reporting.generate_report --type=all

    Specify custom output directory:
        python -m src.reporting.generate_report --type=all --output=reports/
        """,
    )

    parser.add_argument(
        "--type",
        choices=["status", "failure", "all"],
        required=True,
        help="Type of report to generate",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for reports (default: {DEFAULT_OUTPUT_DIR})",
    )

    parser.add_argument(
        "--baseline",
        type=Path,
        default=DEFAULT_BASELINE_PATH,
        help=f"Path to baseline_metrics.json (default: {DEFAULT_BASELINE_PATH})",
    )

    parser.add_argument(
        "--format",
        choices=["markdown"],
        default="markdown",
        # Note: Currently only markdown is supported. This argument is reserved
        # for future expansion to support additional formats (json, html).
        help="Output format (default: markdown)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without writing files",
    )

    return parser


def generate_status_report(
    baseline_path: Path,
    output_dir: Path,
    renderer: MarkdownRenderer,
    verbose: bool = False,
    dry_run: bool = False,
) -> bool:
    """
    Generate the status report.

    Args:
        baseline_path: Path to baseline metrics file
        output_dir: Output directory for report
        renderer: MarkdownRenderer instance
        verbose: Enable verbose output
        dry_run: Don't write files if True

    Returns:
        True if successful, False otherwise
    """
    try:
        if verbose:
            print(f"Loading baseline metrics from {baseline_path}...")

        baseline = load_baseline_metrics(baseline_path)
        analyzer = StatusAnalyzer(baseline)
        summary = analyzer.get_summary()

        if verbose:
            print("Rendering status report...")

        content = renderer.render_status_report(
            baseline=baseline,
            summary=summary,
            data_source=baseline_path.name,
        )

        output_path = output_dir / "GAMSLIB_STATUS.md"

        if dry_run:
            print(f"Would write status report to {output_path}")
            print(f"  Parse rate: {summary.parse_rate * 100:.1f}%")
            print(f"  Translate rate: {summary.translate_rate * 100:.1f}%")
            print(f"  Solve rate: {summary.solve_rate * 100:.1f}%")
            print(f"  Pipeline rate: {summary.pipeline_rate * 100:.1f}%")
        else:
            renderer.render_to_file(content, output_path)
            print(f"Generated: {output_path}")

        return True

    except DataLoadError as e:
        print(f"Error loading data: {e}", file=sys.stderr)
        return False
    except RenderError as e:
        print(f"Error rendering report: {e}", file=sys.stderr)
        return False


def generate_failure_report(
    baseline_path: Path,
    output_dir: Path,
    renderer: MarkdownRenderer,
    verbose: bool = False,
    dry_run: bool = False,
) -> bool:
    """
    Generate the failure analysis report.

    Args:
        baseline_path: Path to baseline metrics file
        output_dir: Output directory for report
        renderer: MarkdownRenderer instance
        verbose: Enable verbose output
        dry_run: Don't write files if True

    Returns:
        True if successful, False otherwise
    """
    try:
        if verbose:
            print(f"Loading baseline metrics from {baseline_path}...")

        baseline = load_baseline_metrics(baseline_path)
        analyzer = FailureAnalyzer(baseline)

        failure_summary = analyzer.get_summary()
        parse_errors = analyzer.get_error_categories("parse")
        translate_errors = analyzer.get_error_categories("translate")
        solve_errors = analyzer.get_error_categories("solve")
        improvements = analyzer.get_prioritized_improvements()

        if verbose:
            print("Rendering failure report...")
            print(f"  Parse failures: {failure_summary.parse_failures}")
            print(f"  Translate failures: {failure_summary.translate_failures}")
            print(f"  Solve failures: {failure_summary.solve_failures}")

        content = renderer.render_failure_report(
            baseline=baseline,
            failure_summary=failure_summary,
            parse_errors=parse_errors,
            translate_errors=translate_errors,
            solve_errors=solve_errors,
            improvements=improvements,
            data_source=baseline_path.name,
        )

        output_path = output_dir / "FAILURE_ANALYSIS.md"

        if dry_run:
            print(f"Would write failure report to {output_path}")
            print(f"  Total failures: {failure_summary.total_failures}")
            print(f"  Unique error types: {failure_summary.unique_error_types}")
            print(f"  Dominant error: {failure_summary.dominant_error}")
        else:
            renderer.render_to_file(content, output_path)
            print(f"Generated: {output_path}")

        return True

    except DataLoadError as e:
        print(f"Error loading data: {e}", file=sys.stderr)
        return False
    except RenderError as e:
        print(f"Error rendering report: {e}", file=sys.stderr)
        return False


def main(args: list[str] | None = None) -> int:
    """
    Main entry point for the report generator.

    Args:
        args: Command-line arguments (uses sys.argv if None)

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Validate baseline file exists
    if not parsed_args.baseline.exists():
        print(f"Error: Baseline file not found: {parsed_args.baseline}", file=sys.stderr)
        return 1

    # Create output directory if needed
    if not parsed_args.dry_run:
        parsed_args.output.mkdir(parents=True, exist_ok=True)

    # Initialize renderer
    try:
        renderer = MarkdownRenderer()
    except RenderError as e:
        print(f"Error initializing renderer: {e}", file=sys.stderr)
        return 1

    success = True

    # Generate requested reports
    if parsed_args.type in ("status", "all"):
        if not generate_status_report(
            baseline_path=parsed_args.baseline,
            output_dir=parsed_args.output,
            renderer=renderer,
            verbose=parsed_args.verbose,
            dry_run=parsed_args.dry_run,
        ):
            success = False

    if parsed_args.type in ("failure", "all"):
        if not generate_failure_report(
            baseline_path=parsed_args.baseline,
            output_dir=parsed_args.output,
            renderer=renderer,
            verbose=parsed_args.verbose,
            dry_run=parsed_args.dry_run,
        ):
            success = False

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
