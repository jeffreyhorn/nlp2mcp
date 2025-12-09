#!/usr/bin/env python3
"""Generate pipeline diagnostics dashboard from JSON artifacts.

This script generates a markdown dashboard showing:
- Pipeline success rate
- Stage timing breakdown
- Model coverage by tier

Usage:
    # Generate from local diagnostics directory
    python scripts/generate_dashboard.py --input diagnostics/

    # Generate fresh diagnostics for tier 1 models
    python scripts/generate_dashboard.py --generate-fresh

    # Output to specific file
    python scripts/generate_dashboard.py --input diagnostics/ --output docs/DASHBOARD.md
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def get_python_executable() -> str:
    """Get the Python executable, preferring venv if available."""
    # Check for venv in current directory
    venv_python = Path(".venv/bin/python")
    if venv_python.exists():
        return str(venv_python)
    # Fall back to current interpreter
    return sys.executable


def load_diagnostics(input_dir: Path) -> list[dict[str, Any]]:
    """Load all JSON diagnostics files from a directory."""
    diagnostics = []
    if not input_dir.exists():
        return diagnostics

    for json_file in sorted(input_dir.glob("*.json")):
        try:
            with open(json_file) as f:
                data = json.load(f)
                diagnostics.append(data)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Failed to load {json_file}: {e}", file=sys.stderr)

    return diagnostics


def generate_fresh_diagnostics(output_dir: Path, tier: str = "tier1") -> list[dict[str, Any]]:
    """Generate fresh diagnostics by running the pipeline on models."""
    # Map tier names to actual directories
    tier_paths = {
        "tier1": Path("tests/fixtures/gamslib"),
        "tier2": Path("tests/fixtures/tier2_candidates"),
    }
    models_dir = tier_paths.get(tier, Path(f"models/{tier}"))
    if not models_dir.exists():
        print(f"Warning: {models_dir} does not exist", file=sys.stderr)
        return []

    output_dir.mkdir(parents=True, exist_ok=True)
    diagnostics = []

    for model_file in sorted(models_dir.glob("*.gms")):
        model_name = model_file.stem
        output_file = output_dir / f"{model_name}.json"

        try:
            # Run CLI with diagnostics
            python_exe = get_python_executable()
            result = subprocess.run(
                [
                    python_exe,
                    "-m",
                    "src.cli",
                    str(model_file),
                    "--diagnostics",
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Diagnostics go to stderr
            if result.stderr:
                try:
                    data = json.loads(result.stderr)
                    with open(output_file, "w") as f:
                        json.dump(data, f, indent=2)
                    diagnostics.append(data)
                except json.JSONDecodeError:
                    print(
                        f"Warning: Failed to parse diagnostics for {model_name}",
                        file=sys.stderr,
                    )
        except subprocess.TimeoutExpired:
            print(f"Warning: Timeout for {model_name}", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Failed to run {model_name}: {e}", file=sys.stderr)

    return diagnostics


def calculate_stats(diagnostics: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate aggregate statistics from diagnostics."""
    if not diagnostics:
        return {
            "total_models": 0,
            "successful_models": 0,
            "success_rate": 0.0,
            "stage_stats": {},
            "avg_total_duration": 0.0,
        }

    total = len(diagnostics)
    successful = sum(1 for d in diagnostics if d.get("overall_success", False))

    # Stage-level stats
    stage_names = [
        "Parse",
        "Semantic Analysis",
        "Simplification",
        "IR Generation",
        "MCP Generation",
    ]
    stage_stats = {}

    for stage in stage_names:
        stage_data = [
            d["stages"].get(stage)
            for d in diagnostics
            if "stages" in d and stage in d.get("stages", {})
        ]

        if stage_data:
            durations = [s["duration_ms"] for s in stage_data if s]
            successes = sum(1 for s in stage_data if s and s.get("success", False))

            stage_stats[stage] = {
                "count": len(stage_data),
                "success_count": successes,
                "success_rate": (successes / len(stage_data) * 100) if stage_data else 0,
                "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
                "min_duration_ms": min(durations) if durations else 0,
                "max_duration_ms": max(durations) if durations else 0,
            }
        else:
            stage_stats[stage] = {
                "count": 0,
                "success_count": 0,
                "success_rate": 0,
                "avg_duration_ms": 0,
                "min_duration_ms": 0,
                "max_duration_ms": 0,
            }

    # Total duration stats
    total_durations = [d.get("total_duration_ms", 0) for d in diagnostics]
    avg_total = sum(total_durations) / len(total_durations) if total_durations else 0

    return {
        "total_models": total,
        "successful_models": successful,
        "success_rate": (successful / total * 100) if total > 0 else 0,
        "stage_stats": stage_stats,
        "avg_total_duration": avg_total,
    }


def generate_dashboard_markdown(
    diagnostics: list[dict[str, Any]],
    stats: dict[str, Any],
) -> str:
    """Generate markdown dashboard content."""
    lines = []

    # Header
    lines.append("# Pipeline Diagnostics Dashboard")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Schema Version:** 1.0.0")
    lines.append("")

    # Pipeline Success Rate
    lines.append("## Pipeline Success Rate")
    lines.append("")

    success_emoji = (
        "✅" if stats["success_rate"] >= 90 else "⚠️" if stats["success_rate"] >= 70 else "❌"
    )
    lines.append(
        f"**Overall:** {success_emoji} {stats['success_rate']:.1f}% "
        f"({stats['successful_models']}/{stats['total_models']} models)"
    )
    lines.append("")

    # Success rate bar
    filled = int(stats["success_rate"] / 5)  # 20 chars = 100%
    bar = "█" * filled + "░" * (20 - filled)
    lines.append(f"```")
    lines.append(f"[{bar}] {stats['success_rate']:.1f}%")
    lines.append(f"```")
    lines.append("")

    # Stage Timing Breakdown
    lines.append("## Stage Timing Breakdown")
    lines.append("")
    lines.append("| Stage | Success Rate | Avg (ms) | Min (ms) | Max (ms) |")
    lines.append("|-------|-------------|----------|----------|----------|")

    for stage_name in [
        "Parse",
        "Semantic Analysis",
        "Simplification",
        "IR Generation",
        "MCP Generation",
    ]:
        stage = stats["stage_stats"].get(stage_name, {})
        if stage.get("count", 0) > 0:
            lines.append(
                f"| {stage_name} | {stage['success_rate']:.0f}% ({stage['success_count']}/{stage['count']}) | "
                f"{stage['avg_duration_ms']:.1f} | {stage['min_duration_ms']:.1f} | {stage['max_duration_ms']:.1f} |"
            )
        else:
            lines.append(f"| {stage_name} | N/A | - | - | - |")

    lines.append("")
    lines.append(f"**Average Total Pipeline Duration:** {stats['avg_total_duration']:.1f} ms")
    lines.append("")

    # Model Coverage
    lines.append("## Model Coverage")
    lines.append("")

    # Successful models
    successful_models = [d["model_name"] for d in diagnostics if d.get("overall_success", False)]
    failed_models = [d["model_name"] for d in diagnostics if not d.get("overall_success", False)]

    if successful_models:
        lines.append(f"### Successful Models ({len(successful_models)})")
        lines.append("")
        for model in sorted(successful_models):
            lines.append(f"- ✅ {model}")
        lines.append("")

    if failed_models:
        lines.append(f"### Failed Models ({len(failed_models)})")
        lines.append("")
        for model in sorted(failed_models):
            # Get error info if available
            model_data = next((d for d in diagnostics if d["model_name"] == model), None)
            error_info = ""
            if model_data:
                for stage_name, stage_data in model_data.get("stages", {}).items():
                    if not stage_data.get("success", True) and stage_data.get("error"):
                        error_info = f" - {stage_name}: {stage_data['error'][:50]}..."
                        break
            lines.append(f"- ❌ {model}{error_info}")
        lines.append("")

    # Stage Performance Chart (ASCII)
    lines.append("## Stage Performance")
    lines.append("")
    lines.append("```")
    lines.append("Stage Duration Distribution (avg ms)")
    lines.append("")

    max_duration = max(
        (s.get("avg_duration_ms", 0) for s in stats["stage_stats"].values()),
        default=1,
    )
    if max_duration == 0:
        max_duration = 1

    for stage_name in [
        "Parse",
        "Semantic Analysis",
        "Simplification",
        "IR Generation",
        "MCP Generation",
    ]:
        stage = stats["stage_stats"].get(stage_name, {})
        duration = stage.get("avg_duration_ms", 0)
        bar_len = int((duration / max_duration) * 30) if max_duration > 0 else 0
        bar = "▓" * bar_len
        lines.append(f"{stage_name:15} |{bar:<30}| {duration:.1f} ms")

    lines.append("```")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("*Dashboard generated by `scripts/generate_dashboard.py`*")
    lines.append("*Diagnostics schema: v1.0.0 (see `docs/schemas/diagnostics_v1.0.0.json`)*")

    return "\n".join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate pipeline diagnostics dashboard")
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        help="Directory containing JSON diagnostics files",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("docs/DASHBOARD.md"),
        help="Output markdown file (default: docs/DASHBOARD.md)",
    )
    parser.add_argument(
        "--generate-fresh",
        action="store_true",
        help="Generate fresh diagnostics for tier 1 models",
    )
    parser.add_argument(
        "--tier",
        choices=["tier1", "tier2"],
        default="tier1",
        help="Model tier to process (default: tier1)",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        dest="print_output",
        help="Print dashboard to stdout instead of file",
    )

    args = parser.parse_args()

    # Load or generate diagnostics
    if args.generate_fresh:
        output_dir = Path("diagnostics")
        print(f"Generating fresh diagnostics for {args.tier} models...", file=sys.stderr)
        diagnostics = generate_fresh_diagnostics(output_dir, args.tier)
    elif args.input:
        print(f"Loading diagnostics from {args.input}...", file=sys.stderr)
        diagnostics = load_diagnostics(args.input)
    else:
        # Default: try diagnostics/ directory
        default_input = Path("diagnostics")
        if default_input.exists():
            print(f"Loading diagnostics from {default_input}...", file=sys.stderr)
            diagnostics = load_diagnostics(default_input)
        else:
            print("No input specified and diagnostics/ not found.", file=sys.stderr)
            print("Use --generate-fresh to create new diagnostics.", file=sys.stderr)
            sys.exit(1)

    if not diagnostics:
        print("No diagnostics data found.", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(diagnostics)} diagnostics files.", file=sys.stderr)

    # Calculate stats and generate dashboard
    stats = calculate_stats(diagnostics)
    dashboard = generate_dashboard_markdown(diagnostics, stats)

    # Output
    if args.print_output:
        print(dashboard)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            f.write(dashboard)
        print(f"Dashboard written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
