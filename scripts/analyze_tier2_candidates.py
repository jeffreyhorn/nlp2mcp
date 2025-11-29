#!/usr/bin/env python3
"""
Analyze Tier 2 candidate models for parse failures.

For each model, attempts to parse and records:
- Parse status (SUCCESS or FAILED)
- Error message and location
- Model size (lines, variables, equations estimated)
- Blocker category

Usage:
    python scripts/analyze_tier2_candidates.py
"""

import json
import sys
from dataclasses import dataclass
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ir.parser import parse_model_file


@dataclass
class AnalysisResult:
    """Analysis result for a single model."""

    model_name: str
    parse_status: str  # "SUCCESS" or "FAILED"
    error_message: str | None
    error_line: int | None
    file_size_lines: int
    blocker_category: str | None  # e.g., "table", "loop", "alias", "data_statement"


def count_lines(file_path: Path) -> int:
    """Count non-empty, non-comment lines."""
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
        return sum(1 for line in lines if line.strip() and not line.strip().startswith("*"))
    except Exception:
        return 0


def categorize_blocker(error_msg: str) -> str:
    """Categorize the blocker based on error message."""
    if not error_msg:
        return "unknown"

    msg_lower = error_msg.lower()

    # Check for specific patterns
    if "table" in msg_lower:
        return "table_data"
    elif "loop" in msg_lower or "for" in msg_lower:
        return "loop_construct"
    elif "alias" in msg_lower:
        return "alias_statement"
    elif "put" in msg_lower or "file" in msg_lower:
        return "file_io"
    elif "display" in msg_lower:
        return "display_statement"
    elif "abort" in msg_lower:
        return "abort_statement"
    elif "execute" in msg_lower:
        return "execute_statement"
    elif "scalar" in msg_lower and "assignment" in msg_lower:
        return "scalar_assignment"
    elif "parameter" in msg_lower and "assignment" in msg_lower:
        return "parameter_assignment"
    elif "$" in error_msg:
        return "preprocessor_directive"
    elif "no terminal" in msg_lower or "unexpected" in msg_lower:
        return "syntax_error"
    else:
        return "other"


def analyze_model(file_path: Path) -> AnalysisResult:
    """Analyze a single model file."""
    model_name = file_path.stem

    # Count lines
    file_size = count_lines(file_path)

    # Attempt parse
    try:
        result = parse_model_file(str(file_path))
        return AnalysisResult(
            model_name=model_name,
            parse_status="SUCCESS",
            error_message=None,
            error_line=None,
            file_size_lines=file_size,
            blocker_category=None,
        )
    except Exception as e:
        error_msg = str(e)

        # Try to extract line number from error message
        error_line = None
        if "line" in error_msg.lower():
            # Look for patterns like "line 10" or "at line 10"
            import re

            match = re.search(r"line\s+(\d+)", error_msg, re.IGNORECASE)
            if match:
                error_line = int(match.group(1))

        blocker = categorize_blocker(error_msg)

        return AnalysisResult(
            model_name=model_name,
            parse_status="FAILED",
            error_message=error_msg[:200],  # Truncate long messages
            error_line=error_line,
            file_size_lines=file_size,
            blocker_category=blocker,
        )


def main():
    candidates_dir = Path("tests/fixtures/tier2_candidates")

    if not candidates_dir.exists():
        print(f"Error: Directory {candidates_dir} does not exist")
        sys.exit(1)

    # Find all .gms files
    gms_files = sorted(candidates_dir.glob("*.gms"))

    if not gms_files:
        print(f"Error: No .gms files found in {candidates_dir}")
        sys.exit(1)

    print(f"Analyzing {len(gms_files)} Tier 2 candidate models...\n")

    results = []
    success_count = 0
    fail_count = 0

    for gms_file in gms_files:
        print(f"Analyzing: {gms_file.name}...", end=" ")
        result = analyze_model(gms_file)
        results.append(result)

        if result.parse_status == "SUCCESS":
            print("✓ SUCCESS")
            success_count += 1
        else:
            print(f"✗ FAILED ({result.blocker_category})")
            fail_count += 1

    # Print summary
    print(f"\n{'=' * 60}")
    print("ANALYSIS SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total models:     {len(results)}")
    print(f"Parse SUCCESS:    {success_count} ({success_count / len(results) * 100:.1f}%)")
    print(f"Parse FAILED:     {fail_count} ({fail_count / len(results) * 100:.1f}%)")

    # Blocker frequency
    if fail_count > 0:
        print(f"\n{'=' * 60}")
        print("BLOCKER DISTRIBUTION")
        print(f"{'=' * 60}")

        blocker_counts = {}
        for r in results:
            if r.parse_status == "FAILED" and r.blocker_category:
                blocker_counts[r.blocker_category] = blocker_counts.get(r.blocker_category, 0) + 1

        for blocker, count in sorted(blocker_counts.items(), key=lambda x: -x[1]):
            print(f"{blocker:25s}: {count:2d} models")

    # Write detailed results to JSON
    output_file = Path("tests/fixtures/tier2_candidates/analysis_results.json")
    with open(output_file, "w") as f:
        json.dump(
            [
                {
                    "model_name": r.model_name,
                    "parse_status": r.parse_status,
                    "error_message": r.error_message,
                    "error_line": r.error_line,
                    "file_size_lines": r.file_size_lines,
                    "blocker_category": r.blocker_category,
                }
                for r in results
            ],
            f,
            indent=2,
        )

    print(f"\nDetailed results written to: {output_file}")

    # Print failed models with details
    if fail_count > 0:
        print(f"\n{'=' * 60}")
        print("FAILED MODELS DETAIL")
        print(f"{'=' * 60}")

        for r in results:
            if r.parse_status == "FAILED":
                print(f"\n{r.model_name}:")
                print(f"  Size: {r.file_size_lines} lines")
                print(f"  Blocker: {r.blocker_category}")
                if r.error_line:
                    print(f"  Error line: {r.error_line}")
                print(f"  Error: {r.error_message}")


if __name__ == "__main__":
    main()
