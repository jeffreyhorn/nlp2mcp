#!/usr/bin/env python3
"""Fixture validation script for Sprint 9 Day 2.

Validates test fixtures against 5 error types identified in Sprint 8:
1. Missing expected_results.yaml
2. Incorrect statement counts
3. Incorrect line numbers
4. Invalid YAML syntax
5. Missing source file

Usage:
    python scripts/validate_fixtures.py                 # Validate all fixtures
    python scripts/validate_fixtures.py -v              # Verbose output
    python scripts/validate_fixtures.py path/to/fixture # Validate specific fixture

Exit Codes:
    0: All fixtures valid
    1: Validation errors found
    2: Script error (missing files, etc.)
"""

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import yaml


@dataclass
class ValidationError:
    """Represents a fixture validation error."""

    fixture_path: Path
    error_type: str
    message: str

    def __str__(self) -> str:
        return f"[{self.error_type}] {self.fixture_path}: {self.message}"


def find_fixture_directories(base_dir: Path) -> Iterator[Path]:
    """Find all fixture directories containing expected_results.yaml files."""
    if base_dir.is_file():
        # Single fixture directory (parent of the file)
        yield base_dir.parent
        return

    for yaml_file in base_dir.rglob("expected_results.yaml"):
        yield yaml_file.parent


def validate_fixture_structure(fixture_dir: Path) -> list[ValidationError]:
    """Validate fixture directory structure.

    Error Type 1: Missing expected_results.yaml
    Error Type 5: Missing source file (.gms)
    """
    errors = []

    # Check for expected_results.yaml
    expected_results = fixture_dir / "expected_results.yaml"
    if not expected_results.exists():
        errors.append(
            ValidationError(
                fixture_path=fixture_dir,
                error_type="MISSING_YAML",
                message="Missing expected_results.yaml file",
            )
        )
        # Can't proceed with other checks without this file
        return errors

    # Check for source file (.gms or other GAMS file)
    source_files = list(fixture_dir.glob("*.gms"))
    if not source_files:
        errors.append(
            ValidationError(
                fixture_path=fixture_dir,
                error_type="MISSING_SOURCE",
                message="Missing source .gms file",
            )
        )

    return errors


def validate_yaml_syntax(fixture_dir: Path) -> list[ValidationError]:
    """Validate YAML syntax.

    Error Type 4: Invalid YAML syntax
    """
    errors = []
    expected_results = fixture_dir / "expected_results.yaml"

    if not expected_results.exists():
        # Already caught by structure validation
        return errors

    try:
        with open(expected_results) as f:
            yaml.safe_load(f)
    except yaml.YAMLError as e:
        errors.append(
            ValidationError(
                fixture_path=fixture_dir,
                error_type="INVALID_YAML",
                message=f"Invalid YAML syntax: {e}",
            )
        )

    return errors


def count_logical_lines(gms_file: Path) -> int:
    """Count logical lines in GAMS file (non-empty, non-comment lines)."""
    logical_lines = 0
    in_multiline_comment = False

    with open(gms_file) as f:
        for line in f:
            stripped = line.strip()

            # Skip blank lines
            if not stripped:
                continue

            # Handle multiline comments
            if "$ontext" in stripped.lower():
                in_multiline_comment = True
                continue
            if "$offtext" in stripped.lower():
                in_multiline_comment = False
                continue
            if in_multiline_comment:
                continue

            # Skip single-line comments
            if stripped.startswith("*"):
                continue

            # Count as logical line
            logical_lines += 1

    return logical_lines


def count_statements(gms_file: Path) -> int:
    """Count statements in GAMS file.

    A statement ends with ; or .. (equation definition).
    Multi-line statements count as 1.
    """
    statements = 0
    in_multiline_comment = False
    in_statement = False

    with open(gms_file) as f:
        for line in f:
            stripped = line.strip()

            # Handle multiline comments
            if "$ontext" in stripped.lower():
                in_multiline_comment = True
                continue
            if "$offtext" in stripped.lower():
                in_multiline_comment = False
                continue
            if in_multiline_comment:
                continue

            # Skip comments and blank lines
            if not stripped or stripped.startswith("*"):
                continue

            # Check for statement terminators (count all semicolons and double-dots)
            semicolon_count = stripped.count(";")
            double_dot_count = stripped.count("..")
            if semicolon_count > 0 or double_dot_count > 0:
                statements += semicolon_count + double_dot_count
                in_statement = False
            else:
                in_statement = True

    return statements


def validate_expected_results(fixture_dir: Path) -> list[ValidationError]:
    """Validate expected_results.yaml counts match actual file.

    Error Type 2: Incorrect statement counts
    Error Type 3: Incorrect line numbers
    """
    errors = []
    expected_results_path = fixture_dir / "expected_results.yaml"

    if not expected_results_path.exists():
        # Already caught by structure validation
        return errors

    # Load expected results
    try:
        with open(expected_results_path) as f:
            expected = yaml.safe_load(f)
    except yaml.YAMLError:
        # Already caught by YAML syntax validation
        return errors

    # Handle empty/template YAML files
    if expected is None:
        # Empty YAML file (just comments) - skip validation
        return errors

    # Find source file
    source_files = list(fixture_dir.glob("*.gms"))
    if not source_files:
        # Already caught by structure validation
        return errors

    source_file = source_files[0]

    # Count actual values
    actual_lines = count_logical_lines(source_file)
    actual_statements = count_statements(source_file)

    # Validate line count
    expected_lines = expected.get("lines_total")
    if expected_lines is not None and actual_lines != expected_lines:
        errors.append(
            ValidationError(
                fixture_path=fixture_dir,
                error_type="INCORRECT_LINES",
                message=f"Line count mismatch: expected {expected_lines}, actual {actual_lines}",
            )
        )

    # Validate statement count
    expected_statements = expected.get("statements_total")
    if expected_statements is not None and actual_statements != expected_statements:
        errors.append(
            ValidationError(
                fixture_path=fixture_dir,
                error_type="INCORRECT_STATEMENTS",
                message=f"Statement count mismatch: expected {expected_statements}, actual {actual_statements}",
            )
        )

    return errors


def validate_fixture(fixture_dir: Path) -> list[ValidationError]:
    """Validate a single fixture directory."""
    errors = []

    # Run all validation checks
    errors.extend(validate_fixture_structure(fixture_dir))
    errors.extend(validate_yaml_syntax(fixture_dir))
    errors.extend(validate_expected_results(fixture_dir))

    return errors


def validate_fixtures(base_dir: Path, verbose: bool = False) -> list[ValidationError]:
    """Validate all fixtures in directory."""
    all_errors = []
    fixture_count = 0

    for fixture_dir in find_fixture_directories(base_dir):
        fixture_count += 1
        if verbose:
            print(f"Validating: {fixture_dir}")

        errors = validate_fixture(fixture_dir)
        all_errors.extend(errors)

        if verbose and not errors:
            print(f"  ✅ Valid")

    if verbose:
        print(f"\nValidated {fixture_count} fixtures")

    return all_errors


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate test fixtures")
    parser.add_argument(
        "path",
        nargs="?",
        default="tests/fixtures",
        help="Path to fixtures directory or specific fixture (default: tests/fixtures)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose output (show all checked fixtures)"
    )

    args = parser.parse_args()
    base_path = Path(args.path)

    if not base_path.exists():
        print(f"Error: Path not found: {base_path}", file=sys.stderr)
        return 2

    errors = validate_fixtures(base_path, verbose=args.verbose)

    if errors:
        print(f"\n❌ Found {len(errors)} validation errors:\n")
        for error in errors:
            print(f"  {error}")
        return 1

    print("✅ All fixtures valid!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
