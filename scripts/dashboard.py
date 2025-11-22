#!/usr/bin/env python3
"""Generate Sprint 9 dashboard with parse rate and conversion metrics.

This script generates a dashboard showing:
- Parse rate with feature breakdown
- Conversion pipeline progress
- Sprint 9 achievements

Usage:
    python scripts/dashboard.py
"""

import sys
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ir.parser import parse_model_file


def check_model_parses(model_name: str) -> bool:
    """Check if a model parses successfully."""
    model_path = Path(f"tests/fixtures/gamslib/{model_name}.gms")
    if not model_path.exists():
        return False
    try:
        parse_model_file(str(model_path))
        return True
    except Exception:
        return False


def generate_parse_rate_summary() -> dict[str, Any]:
    """Generate parse rate summary with feature breakdown."""
    # Define all test models
    all_models = [
        "circle",
        "himmel16",
        "hs62",
        "mathopt1",
        "maxmin",
        "mhw4d",
        "mhw4dx",
        "mingamma",
        "rbrock",
        "trig",
    ]

    # Check which models parse
    passing_models = [model for model in all_models if check_model_parses(model)]

    # Baseline models from Sprint 8
    baseline_models = ["mathopt1", "mhw4d", "rbrock", "trig"]

    # Sprint 9 target models with their enabling features
    sprint9_targets = {
        "himmel16": "i++1 indexing",
        "hs62": "model sections",
        "mingamma": "equation attributes",
    }

    # Check which Sprint 9 targets are unlocked
    unlocked = {
        model: feature for model, feature in sprint9_targets.items() if check_model_parses(model)
    }

    total_models = len(all_models)
    parse_rate_percent = (len(passing_models) / total_models) * 100

    return {
        "total_models": total_models,
        "passing_models": len(passing_models),
        "parse_rate_percent": parse_rate_percent,
        "baseline_models": baseline_models,
        "sprint9_targets": sprint9_targets,
        "unlocked": unlocked,
        "all_passing": passing_models,
    }


def generate_conversion_summary(passing_count: int) -> dict[str, Any]:
    """Generate conversion pipeline summary.

    Args:
        passing_count: Number of models that parse successfully
    """
    output_dir = Path("output")
    if not output_dir.exists():
        converted_models = []
    else:
        converted_models = [
            p.stem.replace("_mcp", "") for p in output_dir.glob("*_mcp.gms") if p.is_file()
        ]

    conversion_rate = (len(converted_models) / passing_count * 100) if passing_count > 0 else 0

    return {
        "models_converted": len(converted_models),
        "conversion_rate_percent": conversion_rate,
        "converted_list": sorted(converted_models),
        "parseable_models": passing_count,
    }


def generate_dashboard() -> str:
    """Generate the complete dashboard output."""
    parse_summary = generate_parse_rate_summary()
    conversion_summary = generate_conversion_summary(parse_summary["passing_models"])

    output = []
    output.append("# Sprint 9 Dashboard")
    output.append("")
    output.append("## Sprint 9 Parse Rate")
    output.append("")
    output.append(
        f"**Overall:** {parse_summary['parse_rate_percent']:.0f}% "
        f"({parse_summary['passing_models']}/{parse_summary['total_models']} models)"
    )
    output.append("")

    # Baseline models
    output.append("**Baseline models (Sprint 8):**")
    for model in parse_summary["baseline_models"]:
        status = "✅" if model in parse_summary["all_passing"] else "❌"
        output.append(f"- {model} {status}")
    output.append("")

    # Sprint 9 unlocks
    output.append("**Sprint 9 unlocks:**")
    for model, feature in parse_summary["sprint9_targets"].items():
        if model in parse_summary["unlocked"]:
            output.append(f"- {model} ✅ ({feature})")
        else:
            output.append(f"- {model} ❌ ({feature})")
    output.append("")

    # Conversion Pipeline
    output.append("## Conversion Pipeline")
    output.append("")
    output.append(
        f"**Converted:** {conversion_summary['models_converted']}/{conversion_summary['parseable_models']} models "
        f"({conversion_summary['conversion_rate_percent']:.0f}% of parseable models)"
    )
    output.append("")

    if conversion_summary["converted_list"]:
        output.append("**Successfully converted:**")
        for model in conversion_summary["converted_list"]:
            output.append(f"- {model} ✅")
        output.append("")

    output.append("**Known gaps:** See `docs/conversion/gaps.md` (if exists)")
    output.append("")

    # Summary
    output.append("## Sprint 9 Summary")
    output.append("")
    output.append(f"- Parse rate: {parse_summary['parse_rate_percent']:.0f}%")
    output.append(f"- Models unlocked: {len(parse_summary['unlocked'])}/3 Sprint 9 targets")
    output.append(f"- Conversion: {conversion_summary['models_converted']} models converted")
    output.append("")

    return "\n".join(output)


def main():
    """Generate and print the dashboard."""
    dashboard = generate_dashboard()
    print(dashboard)


if __name__ == "__main__":
    main()
