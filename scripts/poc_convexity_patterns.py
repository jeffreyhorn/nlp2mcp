#!/usr/bin/env python3
"""
Proof-of-Concept: Convexity Pattern Detection for GAMS Models

This script implements heuristic pattern matchers to detect common non-convex
structures in GAMS optimization models. It is a research tool to validate the
convexity detection approach before integrating into the main nlp2mcp codebase.

Pattern Detectors:
- detect_nonlinear_equalities: Checks for nonlinear equality constraints
- detect_trig_functions: Checks for trigonometric functions (sin, cos, tan)
- detect_bilinear_terms: Checks for x*y where both are variables
- detect_quotients: Checks for x/y division by variables
- detect_odd_powers: Checks for x^3, x^5, etc.

Usage:
    python scripts/poc_convexity_patterns.py tests/fixtures/convexity/*.gms
    python scripts/poc_convexity_patterns.py --help
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import NamedTuple

# Add src to path to import nlp2mcp modules
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ir.ast import Binary, Call, Const, Expr, ParamRef, Sum, Unary, VarRef
from ir.model_ir import ModelIR
from ir.parser import parse_model_file
from ir.symbols import Rel


class Warning(NamedTuple):
    """A convexity warning found in the model."""

    equation: str
    pattern: str
    message: str


def is_constant(expr: Expr) -> bool:
    """Check if expression contains no variables (only constants/parameters)."""
    match expr:
        case Const(_):
            return True
        case ParamRef(_):
            return True  # Parameters are constants w.r.t. variables
        case VarRef(_):
            return False
        case Binary(_, left, right):
            return is_constant(left) and is_constant(right)
        case Unary(_, operand):
            return is_constant(operand)
        case Call(_, args):
            return all(is_constant(arg) for arg in args)
        case Sum(_, body):
            return is_constant(body)
        case _:
            return None


def is_affine(expr: Expr) -> bool:
    """Check if expression is affine (linear in variables)."""
    match expr:
        case Const(_) | ParamRef(_):
            return True
        case VarRef(_):
            return True
        case Binary(op, left, right) if op in ("+", "-"):
            return is_affine(left) and is_affine(right)
        case Binary("*", left, right):
            # Affine if one side is constant and other is affine
            return (is_constant(left) and is_affine(right)) or (
                is_affine(left) and is_constant(right)
            )
        case Binary("/", left, right):
            # Affine if numerator is affine and denominator is constant
            return is_affine(left) and is_constant(right)
        case Unary("-", operand):
            return is_affine(operand)
        case Unary("+", operand):
            return is_affine(operand)
        case Sum(_, body):
            return is_affine(body)
        case _:
            return None


def has_variable(e: Expr) -> bool:
    """Check if expression contains any variables."""
    match e:
        case VarRef(_):
            return True
        case Binary(_, left, right):
            return has_variable(left) or has_variable(right)
        case Unary(_, operand):
            return has_variable(operand)
        case Call(_, args):
            return any(has_variable(arg) for arg in args)
        case Sum(_, body):
            return has_variable(body)
        case _:
            return None


def find_trig_functions(expr: Expr) -> list[str]:
    """Find all trigonometric function calls in expression."""
    trig_funcs = []

    def traverse(e: Expr) -> None:
        match e:
            case Call(func, args) if func in ("sin", "cos", "tan", "arcsin", "arccos", "arctan"):
                trig_funcs.append(f"{func}(...)")
                for arg in args:
                    traverse(arg)
            case Call(_, args):
                for arg in args:
                    traverse(arg)
            case Binary(_, left, right):
                traverse(left)
                traverse(right)
            case Unary(_, operand):
                traverse(operand)
            case Sum(_, body):
                traverse(body)

    traverse(expr)
    return trig_funcs


def find_bilinear_terms(expr: Expr) -> list[str]:
    """Find bilinear terms (products of two variables) in expression."""
    bilinear_terms = []

    def traverse(e: Expr) -> None:
        match e:
            case Binary("*", left, right):
                # Check if both operands contain variables
                if has_variable(left) and has_variable(right):
                    # This is a bilinear term (or worse)
                    bilinear_terms.append(f"({left}) * ({right})")
                traverse(left)
                traverse(right)
            case Binary(_, left, right):
                traverse(left)
                traverse(right)
            case Unary(_, operand):
                traverse(operand)
            case Call(_, args):
                for arg in args:
                    traverse(arg)
            case Sum(_, body):
                traverse(body)
            case _:
                return None

    traverse(expr)
    return bilinear_terms


def find_variable_quotients(expr: Expr) -> list[str]:
    """Find quotients where denominator contains variables."""
    quotients = []

    def traverse(e: Expr) -> None:
        match e:
            case Binary("/", left, right):
                # Check if denominator contains variables
                if has_variable(right):
                    quotients.append(f"({left}) / ({right})")
                traverse(left)
                traverse(right)
            case Binary(_, left, right):
                traverse(left)
                traverse(right)
            case Unary(_, operand):
                traverse(operand)
            case Call(_, args):
                for arg in args:
                    traverse(arg)
            case Sum(_, body):
                traverse(body)
            case _:
                return None

    traverse(expr)
    return quotients


def find_odd_powers(expr: Expr) -> list[str]:
    """Find odd integer powers of variables (x^3, x^5, etc.)."""
    odd_powers = []

    def traverse(e: Expr) -> None:
        match e:
            case Binary("**", base, Const(exp)) | Binary("^", base, Const(exp)):
                # Check for odd integer powers
                if has_variable(base) and exp == int(exp) and int(exp) % 2 == 1 and exp != 1:
                    odd_powers.append(f"({base})^{int(exp)}")
                traverse(base)
            case Call("power", (base, Const(exp))):
                # Same check for power() function
                if has_variable(base) and exp == int(exp) and int(exp) % 2 == 1 and exp != 1:
                    odd_powers.append(f"power(({base}), {int(exp)})")
                traverse(base)
            case Binary(_, left, right):
                traverse(left)
                traverse(right)
            case Unary(_, operand):
                traverse(operand)
            case Call(_, args):
                for arg in args:
                    traverse(arg)
            case Sum(_, body):
                traverse(body)
            case _:
                return None

    traverse(expr)
    return odd_powers


def detect_nonlinear_equalities(model_ir: ModelIR) -> list[Warning]:
    """
    Check for nonlinear equality constraints.

    Nonlinear equalities (h(x) = 0 where h is not affine) typically define
    non-convex feasible sets, even if h itself might be convex.

    Example: x^2 + y^2 = 4 defines a circle (non-convex set).

    Note: We skip the objective definition equation (e.g., obj =e= f(x))
    because it's not a constraint on the feasible set.
    """
    warnings = []

    # Get the objective variable name to skip its definition equation
    obj_var = model_ir.objective.objvar if model_ir.objective else None

    for eq_name, eq in model_ir.equations.items():
        if eq.relation == Rel.EQ:
            lhs, rhs = eq.lhs_rhs

            # Skip objective definition equations (e.g., obj =e= 2*x + 3*y)
            # These are identified by having the objective variable on the LHS
            if obj_var and isinstance(lhs, VarRef) and lhs.name == obj_var:
                continue

            # Check if the constraint is nonlinear (not affine)
            # We check lhs - rhs for affinity
            diff = Binary("-", lhs, rhs)
            if not is_affine(diff):
                warnings.append(
                    Warning(
                        equation=eq_name,
                        pattern="nonlinear_equality",
                        message=(
                            f"Nonlinear equality constraint. "
                            f"Nonlinear equalities typically define non-convex feasible sets."
                        ),
                    )
                )

    return warnings


def detect_trig_functions(model_ir: ModelIR) -> list[Warning]:
    """
    Check for trigonometric functions (sin, cos, tan, etc.).

    Trigonometric functions are neither convex nor concave, so they
    generally indicate non-convexity.
    """
    warnings = []

    # Check objective
    if model_ir.objective and model_ir.objective.expr:
        trig_funcs = find_trig_functions(model_ir.objective.expr)
        if trig_funcs:
            warnings.append(
                Warning(
                    equation="objective",
                    pattern="trig_function",
                    message=f"Found trigonometric functions: {', '.join(trig_funcs)}. "
                    f"Trig functions are neither convex nor concave.",
                )
            )

    # Check constraints
    for eq_name, eq in model_ir.equations.items():
        lhs, rhs = eq.lhs_rhs
        trig_funcs_lhs = find_trig_functions(lhs)
        trig_funcs_rhs = find_trig_functions(rhs)
        all_trig = trig_funcs_lhs + trig_funcs_rhs

        if all_trig:
            warnings.append(
                Warning(
                    equation=eq_name,
                    pattern="trig_function",
                    message=f"Found trigonometric functions: {', '.join(all_trig)}. "
                    f"Trig functions are neither convex nor concave.",
                )
            )

    return warnings


def detect_bilinear_terms(model_ir: ModelIR) -> list[Warning]:
    """
    Check for bilinear terms (x*y where both are variables).

    Bilinear terms are non-convex. They commonly appear in products,
    complementarity conditions, and nonlinear dynamics.
    """
    warnings = []

    # Check objective
    if model_ir.objective and model_ir.objective.expr:
        bilinear = find_bilinear_terms(model_ir.objective.expr)
        if bilinear:
            warnings.append(
                Warning(
                    equation="objective",
                    pattern="bilinear_term",
                    message=f"Found bilinear terms: {', '.join(bilinear[:3])}{'...' if len(bilinear) > 3 else ''} "
                    f"({len(bilinear)} total). Bilinear terms are non-convex.",
                )
            )

    # Check constraints
    for eq_name, eq in model_ir.equations.items():
        lhs, rhs = eq.lhs_rhs
        bilinear_lhs = find_bilinear_terms(lhs)
        bilinear_rhs = find_bilinear_terms(rhs)
        all_bilinear = bilinear_lhs + bilinear_rhs

        if all_bilinear:
            warnings.append(
                Warning(
                    equation=eq_name,
                    pattern="bilinear_term",
                    message=f"Found bilinear terms: {', '.join(all_bilinear[:3])}{'...' if len(all_bilinear) > 3 else ''} "
                    f"({len(all_bilinear)} total). Bilinear terms are non-convex.",
                )
            )

    return warnings


def detect_quotients(model_ir: ModelIR) -> list[Warning]:
    """
    Check for x/y where y contains variables.

    Quotients with variable denominators are typically non-convex.
    """
    warnings = []

    # Check objective
    if model_ir.objective and model_ir.objective.expr:
        quotients = find_variable_quotients(model_ir.objective.expr)
        if quotients:
            warnings.append(
                Warning(
                    equation="objective",
                    pattern="variable_quotient",
                    message=f"Found variable quotients: {', '.join(quotients[:3])}{'...' if len(quotients) > 3 else ''} "
                    f"({len(quotients)} total). Variable quotients are typically non-convex.",
                )
            )

    # Check constraints
    for eq_name, eq in model_ir.equations.items():
        lhs, rhs = eq.lhs_rhs
        quotients_lhs = find_variable_quotients(lhs)
        quotients_rhs = find_variable_quotients(rhs)
        all_quotients = quotients_lhs + quotients_rhs

        if all_quotients:
            warnings.append(
                Warning(
                    equation=eq_name,
                    pattern="variable_quotient",
                    message=f"Found variable quotients: {', '.join(all_quotients[:3])}{'...' if len(all_quotients) > 3 else ''} "
                    f"({len(all_quotients)} total). Variable quotients are typically non-convex.",
                )
            )

    return warnings


def detect_odd_powers(model_ir: ModelIR) -> list[Warning]:
    """
    Check for odd powers of variables (x^3, x^5, etc.).

    Odd powers are neither convex nor concave (except x^1 which is affine).
    """
    warnings = []

    # Check objective
    if model_ir.objective and model_ir.objective.expr:
        odd_powers = find_odd_powers(model_ir.objective.expr)
        if odd_powers:
            warnings.append(
                Warning(
                    equation="objective",
                    pattern="odd_power",
                    message=f"Found odd powers: {', '.join(odd_powers[:3])}{'...' if len(odd_powers) > 3 else ''} "
                    f"({len(odd_powers)} total). Odd powers are neither convex nor concave.",
                )
            )

    # Check constraints
    for eq_name, eq in model_ir.equations.items():
        lhs, rhs = eq.lhs_rhs
        odd_powers_lhs = find_odd_powers(lhs)
        odd_powers_rhs = find_odd_powers(rhs)
        all_odd_powers = odd_powers_lhs + odd_powers_rhs

        if all_odd_powers:
            warnings.append(
                Warning(
                    equation=eq_name,
                    pattern="odd_power",
                    message=f"Found odd powers: {', '.join(all_odd_powers[:3])}{'...' if len(all_odd_powers) > 3 else ''} "
                    f"({len(all_odd_powers)} total). Odd powers are neither convex nor concave.",
                )
            )

    return warnings


def analyze_model(model_path: Path) -> tuple[ModelIR, list[Warning]]:
    """
    Parse a GAMS model and run all pattern matchers.

    Returns:
        (model_ir, warnings): Parsed model and list of warnings found
    """
    try:
        model = parse_model_file(model_path)
    except Exception as e:
        print(f"ERROR: Failed to parse {model_path}: {e}", file=sys.stderr)
        raise

    # Run all pattern detectors
    warnings = []
    warnings.extend(detect_nonlinear_equalities(model))
    warnings.extend(detect_trig_functions(model))
    warnings.extend(detect_bilinear_terms(model))
    warnings.extend(detect_quotients(model))
    warnings.extend(detect_odd_powers(model))

    return model, warnings


def format_warnings(model_path: Path, warnings: list[Warning]) -> str:
    """Format warnings for display."""
    if not warnings:
        return f"✓ {model_path.name}: No convexity issues detected (0 warnings)\n"

    lines = [f"\n⚠ {model_path.name}: {len(warnings)} warning(s) detected"]
    lines.append("=" * 70)

    for i, w in enumerate(warnings, 1):
        lines.append(f"\n[{i}] Equation: {w.equation}")
        lines.append(f"    Pattern: {w.pattern}")
        lines.append(f"    {w.message}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="POC: Detect non-convex patterns in GAMS models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single model
  python scripts/poc_convexity_patterns.py tests/fixtures/convexity/convex_lp.gms

  # Analyze all test models
  python scripts/poc_convexity_patterns.py tests/fixtures/convexity/*.gms

  # Show detailed help
  python scripts/poc_convexity_patterns.py --help

Pattern Detectors:
  - nonlinear_equalities: Checks for nonlinear equality constraints
  - trig_functions: Checks for sin, cos, tan, etc.
  - bilinear_terms: Checks for x*y where both are variables
  - variable_quotients: Checks for x/y where y contains variables
  - odd_powers: Checks for x^3, x^5, etc.

Exit Codes:
  0 - All models analyzed successfully (may have warnings)
  1 - Error occurred during parsing or analysis
        """,
    )

    parser.add_argument(
        "models",
        nargs="+",
        type=Path,
        help="GAMS model files to analyze (.gms)",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Only show models with warnings",
    )

    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show summary statistics at the end",
    )

    args = parser.parse_args()

    # Track statistics
    total_models = 0
    total_warnings = 0
    models_with_warnings = 0
    failed_models = []

    # Analyze each model
    for model_path in args.models:
        if not model_path.exists():
            print(f"ERROR: File not found: {model_path}", file=sys.stderr)
            failed_models.append(str(model_path))
            continue

        if not model_path.suffix == ".gms":
            print(f"WARNING: Skipping non-GAMS file: {model_path}", file=sys.stderr)
            continue

        total_models += 1

        try:
            model, warnings = analyze_model(model_path)

            if warnings:
                models_with_warnings += 1
                total_warnings += len(warnings)

            # Print results
            if not args.quiet or warnings:
                print(format_warnings(model_path, warnings))

        except Exception as e:
            print(f"ERROR: Analysis failed for {model_path}: {e}", file=sys.stderr)
            failed_models.append(str(model_path))
            continue

    # Print summary if requested
    if args.summary or total_models > 1:
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Total models analyzed: {total_models}")
        print(f"Models with warnings: {models_with_warnings}")
        print(f"Models clean: {total_models - models_with_warnings}")
        print(f"Total warnings: {total_warnings}")
        if failed_models:
            print(f"Failed models: {len(failed_models)}")
            for failed in failed_models:
                print(f"  - {failed}")

    # Exit with error if any models failed
    sys.exit(1 if failed_models else 0)


if __name__ == "__main__":
    main()
