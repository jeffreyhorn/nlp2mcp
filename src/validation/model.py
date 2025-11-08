"""
Model structure validation utilities.

This module provides validation for model structure and semantics before
KKT assembly, catching common modeling errors early with helpful feedback.

Sprint 5 Day 4: Task 4.2 - Model Validation Pass
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..ir.ast import Expr
    from ..ir.model_ir import ModelIR

from ..ir.ast import VarRef
from ..utils.errors import ModelError


def _extract_variables(expr: Expr) -> set[str]:
    """
    Extract all variable names from an expression.

    Args:
        expr: Expression to analyze

    Returns:
        Set of variable names referenced in the expression
    """
    vars_found = set()

    if isinstance(expr, VarRef):
        vars_found.add(expr.name)

    # Recursively check children
    for child in expr.children():
        vars_found.update(_extract_variables(child))

    return vars_found


def validate_objective_defined(model_ir: ModelIR) -> None:
    """
    Check that the model has a well-defined objective.

    Args:
        model_ir: The model to validate

    Raises:
        ModelError: If objective is missing or malformed
    """
    if model_ir.objective is None:
        raise ModelError(
            "Model has no objective function defined",
            suggestion=(
                "Add an objective definition to your GAMS model:\n"
                "  Variables z;\n"
                "  Equations obj_def;\n"
                "  obj_def.. z =e= <expression>;\n"
                "  Model mymodel / all /;\n"
                "  Solve mymodel using NLP minimizing z;"
            ),
        )

    if model_ir.objective.objvar is None:
        raise ModelError(
            "Objective variable is not defined",
            suggestion="Specify the objective variable in the Solve statement.",
        )


def validate_variables_used(model_ir: ModelIR) -> None:
    """
    Check that all declared variables appear in at least one equation.

    Issues a warning (not an error) for unused variables, as they may be
    intentional in some modeling contexts.

    Args:
        model_ir: The model to validate

    Note:
        This function currently logs warnings rather than raising errors,
        as unused variables may be intentional (e.g., development models).
    """
    # Collect all variables used in equations
    used_vars = set()

    # Check objective
    if model_ir.objective and model_ir.objective.expr:
        used_vars.update(_extract_variables(model_ir.objective.expr))

    # Check all equations
    for _eq_name, eq_def in model_ir.equations.items():
        lhs, rhs = eq_def.lhs_rhs
        if lhs:
            used_vars.update(_extract_variables(lhs))
        if rhs:
            used_vars.update(_extract_variables(rhs))

    # Find unused variables (scalar only for now)
    unused = []
    for var_name, var_def in model_ir.variables.items():
        if not var_def.domain and var_name not in used_vars:
            # Skip the objective variable itself
            if model_ir.objective and var_name != model_ir.objective.objvar:
                unused.append(var_name)

    # Log warning if we find unused variables (don't fail - might be intentional)
    if unused:
        import logging

        logger = logging.getLogger("nlp2mcp")
        logger.warning(
            f"Found {len(unused)} unused variable(s): {', '.join(sorted(unused)[:5])}"
            + ("..." if len(unused) > 5 else "")
        )
        logger.warning(
            "Unused variables will still be included in the MCP but have no constraints."
        )


def validate_equations_reference_variables(model_ir: ModelIR) -> None:
    """
    Check that all equations reference at least one variable.

    Args:
        model_ir: The model to validate

    Raises:
        ModelError: If an equation contains no variables (constant equation)
    """
    for eq_name, eq_def in model_ir.equations.items():
        vars_in_eq = set()

        lhs, rhs = eq_def.lhs_rhs
        if lhs:
            vars_in_eq.update(_extract_variables(lhs))
        if rhs:
            vars_in_eq.update(_extract_variables(rhs))

        if not vars_in_eq:
            raise ModelError(
                f"Equation '{eq_name}' does not reference any variables",
                suggestion=(
                    f"Equation '{eq_name}' appears to be a constant expression.\n"
                    "This may indicate:\n"
                    "  - Equation was not properly defined\n"
                    "  - All variables were substituted out during preprocessing\n"
                    "  - Equation should be removed or reformulated\n"
                    "\nConstant equations like '5 = 5' or '0 = 1' are not valid NLP constraints."
                ),
            )


def validate_no_circular_definitions(model_ir: ModelIR) -> None:
    """
    Check for circular variable definitions in equality constraints.

    This is a simplified check that looks for direct cycles like:
      x = y
      y = x

    Args:
        model_ir: The model to validate

    Raises:
        ModelError: If circular definitions are detected

    Note:
        This is a heuristic check and may not catch all circular dependencies.
        More sophisticated cycle detection could be added in the future.
    """
    # Build a simple dependency graph: var -> defining equation
    var_definitions: dict[str, tuple[str, set[str]]] = {}

    for eq_name, eq_def in model_ir.equations.items():
        # Only check equality constraints
        if eq_def.relation.name == "EQ":
            # Check if LHS is a simple variable reference
            lhs, rhs = eq_def.lhs_rhs
            if isinstance(lhs, VarRef):
                defined_var = lhs.name
                # Get variables referenced in RHS
                rhs_vars = _extract_variables(rhs) if rhs else set()

                if defined_var in var_definitions:
                    # Multiple definitions - not necessarily circular, but suspicious
                    import logging

                    logger = logging.getLogger("nlp2mcp")
                    logger.warning(
                        f"Variable '{defined_var}' has multiple defining equations: "
                        f"{var_definitions[defined_var]} and {eq_name}"
                    )

                var_definitions[defined_var] = (eq_name, rhs_vars)

    # Check for simple cycles: x = f(y), y = g(x)
    # Note: Self-references (x = f(x)) are valid fixed-point equations, not circular
    for var1, (eq1, deps1) in var_definitions.items():
        for var2 in deps1:
            # Skip self-references (x = x + 1 is valid)
            if var2 == var1:
                continue
            if var2 in var_definitions:
                eq2, deps2 = var_definitions[var2]
                if var1 in deps2:
                    raise ModelError(
                        f"Circular dependency detected: '{var1}' and '{var2}' define each other",
                        suggestion=(
                            f"Equations '{eq1}' and '{eq2}' create a circular definition:\n"
                            f"  {eq1}: {var1} depends on {var2}\n"
                            f"  {eq2}: {var2} depends on {var1}\n"
                            "\nReformulate your model to break the cycle."
                        ),
                    )


def validate_model_structure(model_ir: ModelIR, strict: bool = True) -> None:
    """
    Run all model structure validations.

    Args:
        model_ir: The model to validate
        strict: If True, run all validations. If False, skip optional checks.

    Raises:
        ModelError: If validation fails

    This is the main entry point for model validation, called from the CLI.
    """
    # Critical validations (always run)
    validate_objective_defined(model_ir)
    validate_equations_reference_variables(model_ir)

    # Optional validations (can be skipped with --no-strict flag in future)
    if strict:
        validate_no_circular_definitions(model_ir)
        validate_variables_used(model_ir)  # Only warns, doesn't fail
