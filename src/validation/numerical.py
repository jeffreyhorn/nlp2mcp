"""
Numerical validation utilities for detecting NaN/Inf values.

This module provides guardrails to catch numerical issues early in the
pipeline, before they propagate to PATH solver or cause cryptic errors.

Sprint 5 Day 4: Task 4.1 - Numerical Guardrails
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from ..ir.model_ir import ModelIR

from ..utils.errors import NumericalError


def validate_parameter_values(model_ir: ModelIR) -> None:
    """
    Check for NaN/Inf in parameter values.

    Raises:
        NumericalError: If any parameter has NaN or Inf value

    Examples:
        >>> model_ir = ModelIR(...)
        >>> model_ir.params['p'].values[('1',)] = float('nan')
        >>> validate_parameter_values(model_ir)  # doctest: +SKIP
        NumericalError: Numerical error in parameter 'p[1]': Invalid value (value is NaN)
    """
    for param_name, param_def in model_ir.params.items():
        for indices, value in param_def.values.items():
            if not math.isfinite(value):
                # Format indices for display
                if indices:
                    index_str = ",".join(str(i) for i in indices)
                    location = f"parameter '{param_name}[{index_str}]'"
                else:
                    location = f"parameter '{param_name}'"

                raise NumericalError(
                    "Invalid value",
                    location=location,
                    value=value,
                    suggestion=(
                        "Check your GAMS model or data file for:\n"
                        "  - Uninitialized parameters\n"
                        "  - Division by zero in parameter calculations\n"
                        "  - Invalid mathematical operations\n"
                        f"  - Correct definition of parameter '{param_name}'"
                    ),
                )


def validate_expression_value(
    expr_value: float, expr_name: str, context: str | None = None
) -> None:
    """
    Check if an evaluated expression result is finite.

    Args:
        expr_value: The computed value to check
        expr_name: Name of the expression (e.g., "objective", "constraint eq1")
        context: Optional additional context

    Raises:
        NumericalError: If value is NaN or Inf

    Examples:
        >>> validate_expression_value(3.14, "objective")  # OK
        >>> validate_expression_value(float('nan'), "objective")  # doctest: +SKIP
        NumericalError: Numerical error in objective: Computed value is not finite
    """
    if not math.isfinite(expr_value):
        location = expr_name
        if context:
            location = f"{expr_name} ({context})"

        raise NumericalError(
            "Computed value is not finite",
            location=location,
            value=expr_value,
            suggestion=(
                "This expression produced an invalid numerical result.\n"
                "Common causes:\n"
                "  - Division by zero\n"
                "  - log(0) or log(negative number)\n"
                "  - sqrt(negative number)\n"
                "  - Overflow from very large intermediate values\n"
                "\nTry adding bounds to variables or reformulating the expression."
            ),
        )


def validate_jacobian_entries(jacobian: Any, name: str) -> None:
    """
    Check Jacobian/Gradient for NaN/Inf entries.

    Args:
        jacobian: The Jacobian matrix or gradient vector to validate
        name: Description of the Jacobian (e.g., "objective gradient", "constraint Jacobian")

    Raises:
        NumericalError: If any Jacobian entry is NaN or Inf

    Note:
        This validates the symbolic Jacobian structure. Entries are Expr objects,
        so we only check if they contain obviously problematic constants.
        Full numerical validation happens during evaluation.
    """
    # Handle GradientVector (1D) vs JacobianStructure (2D)
    is_gradient = not hasattr(jacobian, "num_rows")

    if is_gradient:
        # GradientVector: only has columns (variables)
        for col_id in range(jacobian.num_cols):
            entry = jacobian.get_derivative(col_id)
            if entry is not None:
                # Check if entry is a constant with NaN/Inf
                if hasattr(entry, "value"):  # It's a Const node
                    value = entry.value  # type: ignore
                    if not math.isfinite(value):
                        # Get variable name for context
                        var_name, var_indices = jacobian.index_mapping.col_to_var[col_id]

                        var_str = var_name
                        if var_indices:
                            var_str += f"[{','.join(var_indices)}]"

                        location = f"{name} entry ∂/∂{var_str}"

                        raise NumericalError(
                            "Gradient entry is not finite",
                            location=location,
                            value=value,
                            suggestion=(
                                "A derivative in your model produced an invalid value.\n"
                                "This may indicate:\n"
                                "  - Symbolic differentiation produced NaN/Inf constant\n"
                                "  - Model has structural issues\n"
                                "\nPlease report this as a bug if the model appears valid."
                            ),
                        )
    else:
        # JacobianStructure: has both rows (equations) and columns (variables)
        for row_id in range(jacobian.num_rows):
            for col_id in range(jacobian.num_cols):
                entry = jacobian.get_derivative(row_id, col_id)
                if entry is not None:
                    # Check if entry is a constant with NaN/Inf
                    if hasattr(entry, "value"):  # It's a Const node
                        value = entry.value  # type: ignore
                        if not math.isfinite(value):
                            # Get equation and variable names for context
                            eq_name, eq_indices = jacobian.index_mapping.row_to_eq[row_id]
                            var_name, var_indices = jacobian.index_mapping.col_to_var[col_id]

                            eq_str = eq_name
                            if eq_indices:
                                eq_str += f"[{','.join(eq_indices)}]"
                            var_str = var_name
                            if var_indices:
                                var_str += f"[{','.join(var_indices)}]"

                            location = f"{name} entry ∂{eq_str}/∂{var_str}"

                            raise NumericalError(
                                "Jacobian entry is not finite",
                                location=location,
                                value=value,
                                suggestion=(
                                    "A derivative in your model produced an invalid value.\n"
                                    "This may indicate:\n"
                                    "  - Symbolic differentiation produced NaN/Inf constant\n"
                                    "  - Model has structural issues\n"
                                    "\nPlease report this as a bug if the model appears valid."
                                ),
                            )


def check_value_finite(value: float, context: str) -> None:
    """
    Quick check if a single value is finite.

    Args:
        value: The value to check
        context: Description of what's being checked

    Raises:
        NumericalError: If value is NaN or Inf

    Examples:
        >>> check_value_finite(3.14, "test value")  # OK
        >>> check_value_finite(float('inf'), "test value")  # doctest: +SKIP
        NumericalError: Numerical error in test value: Value is not finite
    """
    if not math.isfinite(value):
        raise NumericalError("Value is not finite", location=context, value=value)


def validate_bounds(lower: float | None, upper: float | None, var_name: str) -> None:
    """
    Validate variable bounds are finite and consistent.

    Args:
        lower: Lower bound (None if unbounded)
        upper: Upper bound (None if unbounded)
        var_name: Variable name for error messages

    Raises:
        NumericalError: If bounds are NaN or inconsistent (lower > upper)

    Examples:
        >>> validate_bounds(0.0, 10.0, "x")  # OK
        >>> validate_bounds(10.0, 0.0, "x")  # doctest: +SKIP
        NumericalError: Lower bound (10.0) is greater than upper bound (0.0) for variable 'x'
    """
    if lower is not None:
        if math.isnan(lower):
            raise NumericalError(
                "Lower bound is NaN",
                location=f"variable '{var_name}'",
                value=lower,
                suggestion=f"Set a finite lower bound for variable '{var_name}' or leave it unbounded.",
            )

    if upper is not None:
        if math.isnan(upper):
            raise NumericalError(
                "Upper bound is NaN",
                location=f"variable '{var_name}'",
                value=upper,
                suggestion=f"Set a finite upper bound for variable '{var_name}' or leave it unbounded.",
            )

    if lower is not None and upper is not None:
        if lower > upper:
            raise NumericalError(
                f"Lower bound ({lower}) is greater than upper bound ({upper})",
                location=f"variable '{var_name}'",
                suggestion=f"Fix the bound declarations for variable '{var_name}'.",
            )
