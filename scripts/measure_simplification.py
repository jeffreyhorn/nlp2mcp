#!/usr/bin/env python3
"""Measure simplification effectiveness on GAMS models.

This script measures term and operation reduction achieved by Sprint 11's
simplification transformations across Tier 1 GAMSLib models.

Usage:
    # Single model
    ./scripts/measure_simplification.py --model circle

    # Model set
    ./scripts/measure_simplification.py --model-set tier1

    # Output to file
    ./scripts/measure_simplification.py --model-set tier1 --output baselines/simplification/baseline_sprint11.json

Sprint 12 Day 2: Baseline Collection & Multi-Metric Backend
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ir.ast import Expr
from src.ir.metrics import TermReductionMetrics, count_operations, count_terms
from src.ir.parser import parse_model_file
from src.ir.simplification_pipeline import SimplificationPipeline
from src.ir.transformations import (
    apply_log_rules,
    apply_trig_identities,
    combine_fractions,
    consolidate_powers,
    extract_common_factors,
    multi_term_factoring,
    multiplicative_cse,
    nested_cse,
    normalize_associativity,
    simplify_division,
    simplify_nested_products,
)

# Tier 1 models (10 models from Sprint 6-11)
TIER1_MODELS = [
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

# Sprint 11 transformations (11 transformations)
SPRINT11_TRANSFORMATIONS = [
    ("extract_common_factors", extract_common_factors, 1),
    ("multi_term_factoring", multi_term_factoring, 2),
    ("combine_fractions", combine_fractions, 3),
    ("normalize_associativity", normalize_associativity, 4),
    ("simplify_division", simplify_division, 5),
    ("simplify_nested_products", simplify_nested_products, 6),
    ("consolidate_powers", consolidate_powers, 7),
    ("apply_trig_identities", apply_trig_identities, 8),
    ("apply_log_rules", apply_log_rules, 9),
    ("nested_cse", nested_cse, 10),
    ("multiplicative_cse", multiplicative_cse, 11),
]


def create_pipeline() -> SimplificationPipeline:
    """Create simplification pipeline with Sprint 11 transformations."""
    pipeline = SimplificationPipeline(max_iterations=5, size_budget=1.5)

    for name, transform_fn, priority in SPRINT11_TRANSFORMATIONS:
        pipeline.add_pass(transform_fn, priority=priority, name=name)

    return pipeline


def measure_expression(
    expr: Expr, pipeline: SimplificationPipeline, model_name: str, expr_id: str
) -> TermReductionMetrics:
    """Measure simplification metrics for a single expression.

    Args:
        expr: Expression to simplify
        pipeline: Simplification pipeline
        model_name: Model name (e.g., "circle.gms")
        expr_id: Expression identifier (e.g., "eq1", "obj")

    Returns:
        TermReductionMetrics with before/after measurements
    """
    metrics = TermReductionMetrics(model=f"{model_name}.{expr_id}")

    # Measure before simplification
    metrics.ops_before = count_operations(expr)
    metrics.terms_before = count_terms(expr)

    # Apply simplification with timing
    start = time.perf_counter()
    simplified, pipeline_metrics = pipeline.apply(expr)
    metrics.execution_time_ms = (time.perf_counter() - start) * 1000

    # Measure after simplification
    metrics.ops_after = count_operations(simplified)
    metrics.terms_after = count_terms(simplified)

    return metrics


def measure_model(model_path: Path, pipeline: SimplificationPipeline) -> dict[str, Any]:
    """Measure simplification effectiveness for a single model.

    Args:
        model_path: Path to .gms file
        pipeline: Simplification pipeline

    Returns:
        Dictionary with per-expression and aggregate metrics
    """
    model_name = model_path.stem

    try:
        # Parse model to IR
        model_ir = parse_model_file(model_path)
    except Exception as e:
        print(f"Error parsing {model_name}: {e}", file=sys.stderr)
        return {
            "error": str(e),
            "ops_before": 0,
            "ops_after": 0,
            "terms_before": 0,
            "terms_after": 0,
            "ops_reduction_pct": 0.0,
            "terms_reduction_pct": 0.0,
            "execution_time_ms": 0.0,
            "iterations": 0,
            "transformations_applied": {},
        }

    # Collect all expressions from equations and objective
    expressions: list[tuple[str, Expr]] = []

    # Add objective if present
    if model_ir.objective:
        expressions.append(("obj", model_ir.objective.expr))

    # Add all equation expressions (both LHS and RHS)
    for eq_name, equation in model_ir.equations.items():
        lhs, rhs = equation.lhs_rhs
        expressions.append((f"{eq_name}_lhs", lhs))
        expressions.append((f"{eq_name}_rhs", rhs))

    if not expressions:
        print(f"Warning: No expressions found in {model_name}", file=sys.stderr)
        return {
            "error": "No expressions found",
            "ops_before": 0,
            "ops_after": 0,
            "terms_before": 0,
            "terms_after": 0,
            "ops_reduction_pct": 0.0,
            "terms_reduction_pct": 0.0,
            "execution_time_ms": 0.0,
            "iterations": 0,
            "transformations_applied": {},
        }

    # Measure each expression
    total_ops_before = 0
    total_ops_after = 0
    total_terms_before = 0
    total_terms_after = 0
    total_execution_time_ms = 0.0
    all_transformations: dict[str, int] = {}

    for expr_id, expr in expressions:
        expr_metrics = measure_expression(expr, pipeline, model_name, expr_id)

        total_ops_before += expr_metrics.ops_before
        total_ops_after += expr_metrics.ops_after
        total_terms_before += expr_metrics.terms_before
        total_terms_after += expr_metrics.terms_after
        total_execution_time_ms += expr_metrics.execution_time_ms

        # Merge transformation counts
        for trans_name, count in expr_metrics.transformations_applied.items():
            all_transformations[trans_name] = all_transformations.get(trans_name, 0) + count

    # Calculate reduction percentages
    ops_reduction_pct = (
        (total_ops_before - total_ops_after) / total_ops_before * 100
        if total_ops_before > 0
        else 0.0
    )
    terms_reduction_pct = (
        (total_terms_before - total_terms_after) / total_terms_before * 100
        if total_terms_before > 0
        else 0.0
    )

    return {
        "ops_before": total_ops_before,
        "ops_after": total_ops_after,
        "terms_before": total_terms_before,
        "terms_after": total_terms_after,
        "ops_reduction_pct": round(ops_reduction_pct, 2),
        "terms_reduction_pct": round(terms_reduction_pct, 2),
        "execution_time_ms": round(total_execution_time_ms, 3),
        "iterations": pipeline.max_iterations,  # Note: pipeline doesn't expose actual iteration count
        "transformations_applied": all_transformations,
    }


def calculate_aggregate(
    model_results: dict[str, dict[str, Any]], threshold_pct: float = 20.0
) -> dict[str, Any]:
    """Calculate aggregate statistics across all models.

    Args:
        model_results: Dictionary mapping model names to their metrics
        threshold_pct: Threshold for counting "successful" models (default: 20%)

    Returns:
        Aggregate metrics dictionary
    """
    valid_models = [metrics for metrics in model_results.values() if "error" not in metrics]

    if not valid_models:
        return {
            "total_models": 0,
            "ops_avg_reduction_pct": 0.0,
            "terms_avg_reduction_pct": 0.0,
            "models_meeting_threshold": 0,
            "threshold_pct": threshold_pct,
            "total_execution_time_ms": 0.0,
        }

    total_models = len(valid_models)
    ops_avg = sum(m["ops_reduction_pct"] for m in valid_models) / total_models
    terms_avg = sum(m["terms_reduction_pct"] for m in valid_models) / total_models
    models_meeting_threshold = sum(
        1 for m in valid_models if m["terms_reduction_pct"] >= threshold_pct
    )
    total_execution_time = sum(m["execution_time_ms"] for m in valid_models)

    return {
        "total_models": total_models,
        "ops_avg_reduction_pct": round(ops_avg, 2),
        "terms_avg_reduction_pct": round(terms_avg, 2),
        "models_meeting_threshold": models_meeting_threshold,
        "threshold_pct": threshold_pct,
        "total_execution_time_ms": round(total_execution_time, 3),
    }


def get_git_commit() -> str:
    """Get current git commit SHA."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Measure simplification effectiveness on GAMS models"
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Single model name (e.g., 'circle')",
    )
    parser.add_argument(
        "--model-set",
        type=str,
        choices=["tier1"],
        help="Predefined model set (tier1 = 10 Tier 1 models)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output JSON file path (default: stdout)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=20.0,
        help="Term reduction threshold percentage (default: 20.0)",
    )

    args = parser.parse_args()

    # Determine which models to measure
    if args.model_set == "tier1":
        models = TIER1_MODELS
    elif args.model:
        models = [args.model]
    else:
        parser.error("Must specify --model or --model-set")

    # Create simplification pipeline
    pipeline = create_pipeline()

    # Measure each model
    fixtures_dir = Path("tests/fixtures/gamslib")
    model_results: dict[str, dict[str, Any]] = {}

    for model_name in models:
        # Check if model_name is a full path or just a name
        model_path = Path(model_name)
        if not model_path.exists():
            # Try as a name in gamslib
            model_path = fixtures_dir / f"{model_name}.gms"

        if not model_path.exists():
            print(f"Error: Model file not found: {model_path}", file=sys.stderr)
            continue

        # Use just the filename for the results key
        result_key = model_path.name
        print(f"Measuring {result_key}...", file=sys.stderr)
        model_results[result_key] = measure_model(model_path, pipeline)

    # Calculate aggregate statistics
    aggregate = calculate_aggregate(model_results, threshold_pct=args.threshold)

    # Build baseline JSON
    transformation_names = [name for name, _, _ in SPRINT11_TRANSFORMATIONS]

    baseline = {
        "schema_version": "1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "sprint": "sprint11",
        "git_commit": get_git_commit(),
        "description": "Sprint 11 baseline with 11 transformations",
        "transformations_enabled": transformation_names,
        "models": model_results,
        "aggregate": aggregate,
    }

    # Output JSON
    output_json = json.dumps(baseline, indent=2)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output_json)
        print(f"Baseline written to {args.output}", file=sys.stderr)
    else:
        print(output_json)

    return 0


if __name__ == "__main__":
    sys.exit(main())
