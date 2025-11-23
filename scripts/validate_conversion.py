#!/usr/bin/env python3
"""Validate MCP GAMS conversion output.

This script validates that converted MCP GAMS files are syntactically correct
and have all necessary declarations.

Usage:
    python scripts/validate_conversion.py <output.gms>
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Maximum number of undefined variables to report before suppressing output
# Avoids flooding output with false positives from heuristic matching
MAX_UNDEFINED_TO_REPORT = 10


@dataclass
class CheckResult:
    """Result of a single validation check."""

    name: str
    passed: bool
    message: str


@dataclass
class ValidationResult:
    """Overall validation result."""

    success: bool
    checks: list[CheckResult]


def check_gams_syntax(file_path: Path) -> CheckResult:
    """Verify basic GAMS syntax is valid.

    This is a text-based check since we may not have GAMS compiler available.
    Checks for:
    - Balanced parentheses
    - Valid statement terminators (;)
    - No obvious syntax errors
    """
    try:
        content = file_path.read_text()

        # Check balanced parentheses
        paren_count = content.count("(") - content.count(")")
        if paren_count != 0:
            return CheckResult(
                name="Balanced parentheses",
                passed=False,
                message=f"Unbalanced parentheses: {abs(paren_count)} extra {'(' if paren_count > 0 else ')'}",
            )

        # Check that declarations end with semicolons
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Skip comments and empty lines
            if not stripped or stripped.startswith("*"):
                continue
            # Check if line looks like a declaration or statement
            if any(
                stripped.startswith(kw)
                for kw in [
                    "Variable",
                    "Equation",
                    "Parameter",
                    "Scalar",
                    "Set",
                    "Alias",
                ]
            ):
                if not stripped.endswith(";"):
                    return CheckResult(
                        name="Statement terminators",
                        passed=False,
                        message=f"Line {i} missing semicolon: {stripped[:50]}",
                    )

        return CheckResult(
            name="GAMS syntax",
            passed=True,
            message="Basic syntax checks passed",
        )

    except Exception as e:
        return CheckResult(
            name="GAMS syntax",
            passed=False,
            message=f"Error reading file: {e}",
        )


def check_variables_declared(file_path: Path) -> CheckResult:
    """Check that all referenced variables are declared."""
    try:
        content = file_path.read_text()

        # Extract variable declarations (support multiple names per line)
        var_pattern = r"(?:Free|Positive|Negative|Binary|Integer)\s+Variables?\s+([\w,\s]+)"
        declared_vars = set()
        for match in re.findall(var_pattern, content):
            for var in match.split(","):
                var_name = var.strip()
                if var_name:
                    declared_vars.add(var_name)

        # Extract variable references (simplified - looks for word chars followed by . or in expressions)
        # This is a simple heuristic - matches x1, x2, etc. but not keywords
        ref_pattern = r"\b([a-z]\w*)\b"
        references = set(re.findall(ref_pattern, content, re.IGNORECASE))

        # Filter out known GAMS keywords and functions
        keywords = {
            "sqr",
            "sqrt",
            "power",
            "exp",
            "log",
            "sin",
            "cos",
            "tan",
            "sum",
            "variable",
            "equation",
            "free",
            "positive",
            "negative",
            "binary",
            "integer",
            "declarations",
            "lo",
            "up",
            "fx",
            "l",
            "m",
        }
        references = references - keywords

        # Check for undefined variables
        undefined = references - declared_vars
        # Filter out likely false positives (single letters that are indices, etc.)
        undefined = {v for v in undefined if len(v) > 1}

        if undefined and len(undefined) < MAX_UNDEFINED_TO_REPORT:
            return CheckResult(
                name="Variable declarations",
                passed=True,  # Soft warning
                message=f"{len(declared_vars)} variables declared (potential undeclared refs: {', '.join(sorted(undefined)[:5])})",
            )

        return CheckResult(
            name="Variable declarations",
            passed=True,
            message=f"{len(declared_vars)} variables declared",
        )

    except Exception as e:
        return CheckResult(
            name="Variable declarations",
            passed=False,
            message=f"Error checking variables: {e}",
        )


def check_equations_declared(file_path: Path) -> CheckResult:
    """Check that equations are declared."""
    try:
        content = file_path.read_text()

        # Extract equation declarations (support multiple names per line)
        eq_decl_pattern = r"Equations?\s+([\w,\s]+);"
        declared_eqs = set()
        for match in re.findall(eq_decl_pattern, content):
            for eq in match.split(","):
                eq_name = eq.strip()
                if eq_name:
                    declared_eqs.add(eq_name)

        # Extract equation definitions
        eq_def_pattern = r"(\w+)\.\."
        defined_eqs = set(re.findall(eq_def_pattern, content))

        if not declared_eqs:
            return CheckResult(
                name="Equation declarations",
                passed=False,
                message="No equations declared",
            )

        # Check that all definitions have declarations
        undefined = defined_eqs - declared_eqs
        if undefined:
            return CheckResult(
                name="Equation declarations",
                passed=False,
                message=f"Equations defined but not declared: {', '.join(sorted(undefined))}",
            )

        return CheckResult(
            name="Equation declarations",
            passed=True,
            message=f"{len(declared_eqs)} equations declared, {len(defined_eqs)} defined",
        )

    except Exception as e:
        return CheckResult(
            name="Equation declarations",
            passed=False,
            message=f"Error checking equations: {e}",
        )


def check_no_undefined_refs(file_path: Path) -> CheckResult:
    """Check for obvious undefined references."""
    try:
        content = file_path.read_text()

        # Look for common error patterns
        errors = []

        # Check for .lo, .up, .fx, .l, .m without variable name
        # Use word boundary to avoid false positives
        if re.search(r"\.\s+\.(lo|up|fx|l|m)\b", content):
            errors.append("Double-dot attribute reference found")

        # Check for empty parentheses (invalid indexing)
        if re.search(r"\(\s*\)", content):
            errors.append("Empty parentheses found")

        if errors:
            return CheckResult(
                name="Undefined references",
                passed=False,
                message="; ".join(errors),
            )

        return CheckResult(
            name="Undefined references",
            passed=True,
            message="No obvious undefined references",
        )

    except Exception as e:
        return CheckResult(
            name="Undefined references",
            passed=False,
            message=f"Error checking references: {e}",
        )


def check_structure(file_path: Path) -> CheckResult:
    """Check overall file structure."""
    try:
        content = file_path.read_text()

        has_vars = "Variable" in content
        has_eqs = "Equation" in content
        has_definitions = ".." in content

        if not has_vars:
            return CheckResult(
                name="File structure",
                passed=False,
                message="No variable declarations found",
            )

        if not has_eqs:
            return CheckResult(
                name="File structure",
                passed=False,
                message="No equation declarations found",
            )

        if not has_definitions:
            return CheckResult(
                name="File structure",
                passed=False,
                message="No equation definitions found",
            )

        return CheckResult(
            name="File structure",
            passed=True,
            message="Valid GAMS MCP structure",
        )

    except Exception as e:
        return CheckResult(
            name="File structure",
            passed=False,
            message=f"Error checking structure: {e}",
        )


def validate_conversion(file_path: Path) -> ValidationResult:
    """Validate MCP GAMS conversion output."""
    checks = [
        check_structure(file_path),
        check_gams_syntax(file_path),
        check_variables_declared(file_path),
        check_equations_declared(file_path),
        check_no_undefined_refs(file_path),
    ]

    return ValidationResult(success=all(c.passed for c in checks), checks=checks)


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/validate_conversion.py <output.gms>")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(2)

    print(f"Validating {file_path}")
    print("-" * 60)

    result = validate_conversion(file_path)

    for check in result.checks:
        status = "✓" if check.passed else "✗"
        print(f"{status} {check.name:25} {check.message}")

    print("-" * 60)
    if result.success:
        print("✓ Validation PASSED")
        sys.exit(0)
    else:
        print("✗ Validation FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
