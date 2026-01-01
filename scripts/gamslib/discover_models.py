#!/usr/bin/env python3
"""Discover LP/NLP/QCP models from GAMSLIB and populate the catalog.

This script:
1. Generates the GAMSLIB model list using `gamslib -g`
2. Parses the output to extract model names and descriptions
3. Extracts each model temporarily to parse its solve statement
4. Filters for LP, NLP, and QCP models
5. Populates the catalog with discovered models
6. Generates a discovery report

Usage:
    python scripts/gamslib/discover_models.py [--dry-run] [--verbose]

Options:
    --dry-run   Show what would be discovered without updating catalog
    --verbose   Show detailed progress information
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.gamslib.catalog import GamslibCatalog, ModelEntry

# Model types to include in the catalog
INCLUDED_TYPES = frozenset(["LP", "NLP", "QCP"])

# Model types to exclude (for logging purposes)
EXCLUDED_TYPES = frozenset(
    [
        "MIP",
        "MINLP",
        "MIQCP",
        "RMIQCP",
        "RMINLP",
        "RMIP",
        "MCP",
        "MPEC",
        "CNS",
        "DNLP",
        "EMP",
        "MPSGE",
        "GAMS",
        "DECIS",
    ]
)


@dataclass
class DiscoveryResult:
    """Results from model discovery."""

    total_models: int = 0
    included_models: list[ModelEntry] = field(default_factory=list)
    excluded_models: list[tuple[str, str, str]] = field(
        default_factory=list
    )  # (name, type, reason)
    failed_models: list[tuple[str, str]] = field(default_factory=list)  # (name, error)

    @property
    def included_count(self) -> int:
        return len(self.included_models)

    @property
    def excluded_count(self) -> int:
        return len(self.excluded_models)

    @property
    def failed_count(self) -> int:
        return len(self.failed_models)

    def count_by_type(self) -> dict[str, int]:
        """Count included models by type."""
        counts: dict[str, int] = {}
        for model in self.included_models:
            t = model.gamslib_type
            counts[t] = counts.get(t, 0) + 1
        return counts


def run_gamslib_generate() -> str:
    """Run gamslib -g to generate model list and return the output file path."""
    # Run in a temp directory to avoid polluting the working directory
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["gamslib", "-g"],
            cwd=tmpdir,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"gamslib -g failed: {result.stderr}")

        gamslib_file = Path(tmpdir) / "gamslib.gms"
        if not gamslib_file.exists():
            raise RuntimeError("gamslib.gms not created")

        return gamslib_file.read_text()


def parse_gamslib_index(content: str) -> list[tuple[str, str]]:
    """Parse gamslib.gms to extract model names and descriptions.

    Returns list of (model_name, description) tuples.
    """
    models = []

    # Pattern matches lines like:
    #    TRNSPORT 'A Transportation Problem'
    # or with multiple files:
    #    TSP1.('tsp1.gms', 'br17.inc')
    pattern = re.compile(r"^\s+([A-Z][A-Z0-9_]*)\s+'([^']*)'", re.MULTILINE)

    for match in pattern.finditer(content):
        name = match.group(1).lower()
        description = match.group(2)
        models.append((name, description))

    return models


def extract_model_type(model_name: str) -> tuple[str | None, str | None]:
    """Extract a model and parse its solve statement to get the type.

    Returns (model_type, error_message).
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Extract the model
        result = subprocess.run(
            ["gamslib", model_name],
            cwd=tmpdir,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return None, f"gamslib extraction failed: {result.stderr.strip()}"

        # Find the .gms file
        gms_files = list(Path(tmpdir).glob("*.gms"))
        if not gms_files:
            return None, "No .gms file created"

        # Read and parse the solve statement
        content = gms_files[0].read_text()

        # Pattern: solve <model> [minimizing|maximizing <var>] using <type>;
        # The "using <type>" part is what we need to extract
        # This handles both:
        #   solve m using mcp;  (MCP/CNS style - no objective)
        #   solve m minimizing z using lp;  (optimization style)
        solve_pattern = re.compile(r"solve\s+\w+.*?using\s+(\w+)", re.IGNORECASE)

        match = solve_pattern.search(content)
        if match:
            return match.group(1).upper(), None

        return None, "No solve statement found"


def discover_models(verbose: bool = False) -> DiscoveryResult:
    """Discover all LP/NLP/QCP models from GAMSLIB.

    Args:
        verbose: If True, print progress information

    Returns:
        DiscoveryResult with discovered models
    """
    result = DiscoveryResult()

    if verbose:
        print("Generating GAMSLIB model list...")

    # Get the model list
    gamslib_content = run_gamslib_generate()
    models = parse_gamslib_index(gamslib_content)
    result.total_models = len(models)

    if verbose:
        print(f"Found {len(models)} models in GAMSLIB")
        print("Extracting model types...")

    # Process each model
    for i, (name, description) in enumerate(models):
        if verbose and (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(models)} models...")

        model_type, error = extract_model_type(name)

        if error:
            result.failed_models.append((name, error))
            continue

        if model_type is None:
            result.failed_models.append((name, "Could not determine model type"))
            continue

        if model_type in INCLUDED_TYPES:
            # Create catalog entry
            entry = ModelEntry(
                model_id=name,
                sequence_number=i + 1,  # Approximate sequence number
                model_name=description,
                gamslib_type=model_type,
                source_url=f"https://www.gams.com/latest/gamslib_ml/{name}.{i + 1}",
                web_page_url=f"https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_{name}.html",
                description=description,
                download_status="pending",
            )
            result.included_models.append(entry)
        else:
            reason = f"Model type {model_type} not in included types"
            if model_type in EXCLUDED_TYPES:
                reason = f"Excluded type: {model_type}"
            result.excluded_models.append((name, model_type, reason))

    return result


def generate_report(result: DiscoveryResult, output_path: Path) -> None:
    """Generate a discovery report markdown file."""
    counts = result.count_by_type()

    report = f"""# GAMSLIB Model Discovery Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Summary

| Metric | Count |
|--------|-------|
| Total GAMSLIB models | {result.total_models} |
| Included (LP/NLP/QCP) | {result.included_count} |
| Excluded | {result.excluded_count} |
| Failed to process | {result.failed_count} |

## Included Models by Type

| Type | Count |
|------|-------|
| LP | {counts.get("LP", 0)} |
| NLP | {counts.get("NLP", 0)} |
| QCP | {counts.get("QCP", 0)} |
| **Total** | **{result.included_count}** |

## Included Models

| Model ID | Type | Description |
|----------|------|-------------|
"""

    for model in sorted(result.included_models, key=lambda m: (m.gamslib_type, m.model_id)):
        desc = model.description[:60] + "..." if len(model.description) > 60 else model.description
        report += f"| {model.model_id} | {model.gamslib_type} | {desc} |\n"

    report += """
## Excluded Models by Type

| Type | Count |
|------|-------|
"""

    excluded_by_type: dict[str, int] = {}
    for _, model_type, _ in result.excluded_models:
        excluded_by_type[model_type] = excluded_by_type.get(model_type, 0) + 1

    for model_type, count in sorted(excluded_by_type.items()):
        report += f"| {model_type} | {count} |\n"

    if result.failed_models:
        report += """
## Failed Models

| Model | Error |
|-------|-------|
"""
        for name, error in result.failed_models:
            report += f"| {name} | {error[:80]} |\n"

    report += """
---

## Notes

- LP models are always convex by definition
- NLP and QCP models require convexity verification via solver status
- Excluded types include: MIP, MINLP, MIQCP, MCP, MPEC, CNS, DNLP, EMP, MPSGE, GAMS, DECIS
"""

    output_path.write_text(report)


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover LP/NLP/QCP models from GAMSLIB")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be discovered without updating catalog",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed progress information",
    )
    args = parser.parse_args()

    # Discover models
    print("Discovering models from GAMSLIB...")
    result = discover_models(verbose=args.verbose)

    # Print summary
    counts = result.count_by_type()
    print(f"\nDiscovery complete!")
    print(f"  Total GAMSLIB models: {result.total_models}")
    print(
        f"  Included: {result.included_count} (LP: {counts.get('LP', 0)}, NLP: {counts.get('NLP', 0)}, QCP: {counts.get('QCP', 0)})"
    )
    print(f"  Excluded: {result.excluded_count}")
    print(f"  Failed: {result.failed_count}")

    if args.dry_run:
        print("\n[Dry run - catalog not updated]")
        return

    # Load existing catalog and add models
    catalog_path = Path("data/gamslib/catalog.json")
    if catalog_path.exists():
        catalog = GamslibCatalog.load(catalog_path)
    else:
        catalog = GamslibCatalog()

    # Add discovered models
    added = 0
    for model in result.included_models:
        if catalog.get_model_by_id(model.model_id) is None:
            catalog.add_model(model)
            added += 1

    # Save catalog
    catalog.save(catalog_path)
    print(f"\nCatalog updated: {added} new models added")
    print(f"Total models in catalog: {catalog.total_models}")

    # Generate report
    report_path = Path("data/gamslib/discovery_report.md")
    generate_report(result, report_path)
    print(f"Report generated: {report_path}")


if __name__ == "__main__":
    main()
