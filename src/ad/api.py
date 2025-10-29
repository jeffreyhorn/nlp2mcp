"""
High-Level API for Automatic Differentiation

This module provides a clean, simple interface for computing derivatives
from a parsed NLP model. It hides the internal complexity of index mapping,
symbolic differentiation, and Jacobian construction.

Main Function:
--------------
compute_derivatives(model_ir) → (gradient, J_g, J_h)

This is the primary entry point for users. Given a ModelIR, it returns:
- gradient: GradientVector for the objective function
- J_g: JacobianStructure for inequality constraints g(x) ≤ 0
- J_h: JacobianStructure for equality constraints h(x) = 0

Example Usage:
--------------
    from src.ir.parser import parse_gams_to_ir
    from src.ad.api import compute_derivatives

    # Parse GAMS model
    model_ir = parse_gams_to_ir("model.gms")

    # Compute all derivatives
    gradient, J_g, J_h = compute_derivatives(model_ir)

    # Access gradient components
    for var_name, indices in gradient.mapping.var_instances:
        col_id = gradient.mapping.get_var_id(var_name, indices)
        deriv_expr = gradient.get_derivative(col_id)
        print(f"∂f/∂{var_name}{indices} = {deriv_expr}")

    # Access Jacobian entries
    for row_id, col_id in J_g.get_nonzero_entries():
        deriv_expr = J_g.get_derivative(row_id, col_id)
        eq_name, eq_indices = J_g.mapping.get_equation_info(row_id)
        var_name, var_indices = J_g.mapping.get_var_info(col_id)
        print(f"∂g_{eq_name}{eq_indices}/∂{var_name}{var_indices} = {deriv_expr}")

Design Philosophy:
------------------
1. **Simple Interface**: One function call to get all derivatives
2. **Hide Complexity**: Index mapping, alias resolution handled internally
3. **Graceful Error Handling**: Clear error messages for edge cases
4. **Consistent Types**: All return types well-documented
5. **No Surprises**: Follows principle of least surprise

Internal Pipeline:
------------------
1. Build index mapping (variables and equations to dense IDs)
2. Compute objective gradient using symbolic differentiation
3. Compute constraint Jacobians (equality and inequality)
4. Return structured results with metadata

Error Handling:
---------------
Raises clear exceptions for:
- Missing objective function
- Invalid model structure
- Differentiation errors (unsupported operations)
- Index mapping failures (empty sets, circular aliases)

All exceptions include actionable error messages pointing to the problem.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..ir.model_ir import ModelIR

from .constraint_jacobian import compute_constraint_jacobian
from .gradient import GradientVector, compute_objective_gradient
from .jacobian import JacobianStructure


def compute_derivatives(
    model_ir: ModelIR,
) -> tuple[GradientVector, JacobianStructure, JacobianStructure]:
    """
    Compute all derivatives for an NLP model.

    This is the main entry point for automatic differentiation. Given a parsed
    and normalized NLP model, it computes:

    1. Objective gradient: ∇f(x)
    2. Inequality constraint Jacobian: J_g(x) where g(x) ≤ 0
    3. Equality constraint Jacobian: J_h(x) where h(x) = 0

    All derivatives are computed symbolically using the chain rule, product rule,
    quotient rule, and other standard differentiation rules. The result is
    stored as symbolic AST expressions that can be evaluated at specific points.

    Index Mapping:
    --------------
    The function automatically handles:
    - Enumerating all variable instances (scalar and indexed)
    - Enumerating all equation instances (scalar and indexed)
    - Resolving set aliases and universe constraints
    - Building bijective mappings between instances and dense IDs

    Differentiation:
    ----------------
    Uses index-aware symbolic differentiation:
    - Each variable instance gets its own derivative
    - Sums collapse correctly (∂(sum(i,x(i)))/∂x(i1) = 1)
    - Sparse structure preserved

    Supported Operations:
    ---------------------
    - Arithmetic: +, -, *, /
    - Unary: +, -
    - Functions: power, exp, log, sqrt, sin, cos, tan
    - Aggregations: sum

    Not Supported:
    --------------
    - abs() - rejected as non-differentiable at x=0
      (use smooth approximations instead)

    Args:
        model_ir: Parsed and normalized NLP model from Sprint 1

    Returns:
        Tuple of (gradient, J_g, J_h) where:
        - gradient: GradientVector with objective gradient components
        - J_g: JacobianStructure for inequality constraints g(x) ≤ 0
        - J_h: JacobianStructure for equality constraints h(x) = 0

        All three structures include the same IndexMapping for consistency.

    Raises:
        ValueError: If model has no objective function
        ValueError: If objective variable is not defined
        ValueError: If differentiation encounters unsupported operation
        KeyError: If set not found during index enumeration
        RuntimeError: If circular alias detected

    Examples:
        >>> # Simple quadratic model: min x^2 + y^2 s.t. x + y >= 1
        >>> model_ir = parse_gams_to_ir("simple.gms")
        >>> gradient, J_g, J_h = compute_derivatives(model_ir)
        >>>
        >>> # Gradient has 2 components (∂f/∂x, ∂f/∂y)
        >>> assert gradient.num_nonzeros() == 2
        >>>
        >>> # J_g has 1 row (one inequality), J_h empty (no equalities)
        >>> assert J_g.num_nonzeros() > 0
        >>> assert J_h.num_nonzeros() == 0

        >>> # Indexed model: min sum(i, x(i)^2) s.t. sum(i, x(i)) = 1
        >>> model_ir = parse_gams_to_ir("indexed.gms")
        >>> gradient, J_g, J_h = compute_derivatives(model_ir)
        >>>
        >>> # Gradient has n components (one per x(i))
        >>> # J_h has 1 row (equality constraint) with n columns
        >>> n = len(model_ir.sets["i"].elements)
        >>> assert gradient.num_nonzeros() == n
        >>> assert J_h.num_nonzeros() == n

    Notes:
        - All derivatives are symbolic expressions (AST nodes)
        - To evaluate at a point, use the evaluator module
        - Derivatives are NOT automatically simplified
        - Algebraic simplification is future work (Sprint 3+)

    See Also:
        - compute_objective_gradient(): Gradient computation details
        - compute_constraint_jacobian(): Jacobian computation details
        - build_index_mapping(): Index enumeration details
    """
    # Step 1: Compute objective gradient (builds its own mapping)
    gradient = compute_objective_gradient(model_ir)

    # Step 2: Compute constraint Jacobians (builds its own mapping)
    J_h, J_g = compute_constraint_jacobian(model_ir)

    # Note: gradient.index_mapping, J_h.index_mapping, and J_g.index_mapping are all
    # equivalent since they're built from the same model_ir using the same algorithm.
    # Verify this invariant:
    assert gradient.index_mapping is not None, "Gradient must have index_mapping set"
    assert J_h.index_mapping is not None, "J_h must have index_mapping set"
    assert J_g.index_mapping is not None, "J_g must have index_mapping set"

    assert (
        gradient.index_mapping.num_vars == J_h.index_mapping.num_vars == J_g.index_mapping.num_vars
    ), "Invariant violated: all mappings must have the same number of variables"
    assert (
        gradient.index_mapping.var_to_col
        == J_h.index_mapping.var_to_col
        == J_g.index_mapping.var_to_col
    ), "Invariant violated: all mappings must have identical variable-to-column mappings"

    # Return in order: gradient, inequality Jacobian, equality Jacobian
    return gradient, J_g, J_h


# Export main function
__all__ = ["compute_derivatives"]
