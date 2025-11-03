"""
Curtis-Reid scaling algorithm for improving matrix conditioning.

This module implements geometric mean row/column scaling to normalize
the Jacobian matrix, improving numerical conditioning for the PATH solver.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from ..ad.jacobian import JacobianStructure


def curtis_reid_scaling(
    jacobian: JacobianStructure,
    max_iter: int = 10,
    tol: float = 0.1,
    min_norm: float = 1e-10,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute Curtis-Reid geometric mean scaling factors for a Jacobian.

    The Curtis-Reid algorithm iteratively balances row and column norms
    to approximately 1.0, improving matrix conditioning.

    Algorithm:
        1. Initialize R = I, C = I
        2. For k = 1 to max_iterations:
           a. Compute row norms: r_i = ||J[i,:]||₂
           b. Update row scaling: R[i,i] = 1/√r_i
           c. Scale matrix: J = R @ J
           d. Compute column norms: c_j = ||J[:,j]||₂
           e. Update column scaling: C[j,j] = 1/√c_j
           f. Scale matrix: J = J @ C
           g. If max(|r_i - 1|, |c_j - 1|) < tol, converge
        3. Return R, C such that R @ J @ C has balanced norms

    Args:
        jacobian: Sparse Jacobian structure to scale
        max_iter: Maximum number of iterations (default: 10)
        tol: Convergence tolerance for norm deviation from 1.0 (default: 0.1)
        min_norm: Minimum norm to avoid division by zero (default: 1e-10)

    Returns:
        Tuple of (R, C) where:
            R: Row scaling diagonal matrix (as 1D array of diagonal entries)
            C: Column scaling diagonal matrix (as 1D array of diagonal entries)

    Example:
        >>> J = JacobianStructure(...)
        >>> R, C = curtis_reid_scaling(J)
        >>> # Scaled Jacobian would be: R @ J @ C
    """
    # Convert sparse Jacobian to dense for scaling computation
    # In production, we'd use sparse operations, but dense is simpler for now
    dense_jac = _jacobian_to_dense(jacobian)

    m, n = dense_jac.shape  # m = rows (equations), n = cols (variables)

    # Initialize scaling factors (cumulative product of all iterations)
    R = np.ones(m)
    C = np.ones(n)

    for _ in range(max_iter):
        # Row scaling
        row_norms = np.linalg.norm(dense_jac, axis=1, ord=2)  # L2 norm of each row
        # Avoid division by zero for empty rows
        row_norms = np.where(row_norms > min_norm, row_norms, 1.0)
        R_k = 1.0 / np.sqrt(row_norms)

        # Apply row scaling: each row i is multiplied by R_k[i]
        dense_jac = R_k[:, np.newaxis] * dense_jac
        R = R_k * R  # Accumulate scaling

        # Column scaling
        col_norms = np.linalg.norm(dense_jac, axis=0, ord=2)  # L2 norm of each column
        # Avoid division by zero for empty columns
        col_norms = np.where(col_norms > min_norm, col_norms, 1.0)
        C_k = 1.0 / np.sqrt(col_norms)

        # Apply column scaling: each column j is multiplied by C_k[j]
        dense_jac = dense_jac * C_k[np.newaxis, :]
        C = C_k * C  # Accumulate scaling

        # Check convergence
        # Recompute norms after both row and column scaling to verify balance
        row_norms_post = np.linalg.norm(dense_jac, axis=1, ord=2)
        col_norms_post = np.linalg.norm(dense_jac, axis=0, ord=2)
        max_row_dev = np.abs(row_norms_post - 1.0).max()
        max_col_dev = np.abs(col_norms_post - 1.0).max()

        if max_row_dev < tol and max_col_dev < tol:
            break

    return R, C


def byvar_scaling(jacobian: JacobianStructure) -> np.ndarray:
    """
    Compute per-variable (column) scaling factors.

    Unlike Curtis-Reid which balances both rows and columns, byvar scaling
    only normalizes columns (variables), leaving row scaling at 1.0.

    This is useful when you want to ensure each variable has similar
    magnitude in the Jacobian without affecting equation scaling.

    Args:
        jacobian: Sparse Jacobian structure to scale

    Returns:
        C: Column scaling diagonal matrix (as 1D array of diagonal entries)
            Row scaling R is implicitly np.ones(m)

    Example:
        >>> J = JacobianStructure(...)
        >>> C = byvar_scaling(J)
        >>> # Scaled Jacobian would be: J @ C (no row scaling)
    """
    dense_jac = _jacobian_to_dense(jacobian)

    # Compute column norms
    col_norms = np.linalg.norm(dense_jac, axis=0, ord=2)

    # Avoid division by zero
    col_norms = np.where(col_norms > 1e-10, col_norms, 1.0)

    # Column scaling: normalize to 1.0
    C = 1.0 / np.sqrt(col_norms)

    return C


def _jacobian_to_dense(jacobian: JacobianStructure) -> np.ndarray:
    """
    Convert sparse Jacobian structure to dense numpy array.

    This is a helper function for scaling computation. In the current
    implementation, derivatives are symbolic, so we use a placeholder
    value of 1.0 for all nonzero entries to compute structural scaling.

    Args:
        jacobian: Sparse Jacobian structure

    Returns:
        Dense numpy array with 1.0 for each structurally nonzero entry

    Note:
        For purely structural scaling, we use 1.0 for all entries.
        For value-based scaling (future work), we'd need to evaluate
        the symbolic derivatives at a point.
    """
    # Get dimensions from jacobian structure
    num_rows = jacobian.num_rows
    num_cols = jacobian.num_cols

    # Initialize dense matrix
    dense = np.zeros((num_rows, num_cols))

    # Fill in nonzero entries
    # jacobian.entries is a dict[int, dict[int, Expr]]
    for row_id, row_dict in jacobian.entries.items():
        for col_id, _deriv_expr in row_dict.items():
            # Use 1.0 as placeholder for structural scaling
            # Future: could evaluate deriv_expr at a point for value-based scaling
            dense[row_id, col_id] = 1.0

    return dense


def apply_scaling_to_jacobian(
    jacobian: JacobianStructure, R: np.ndarray, C: np.ndarray
) -> tuple[list[float], list[float]]:
    """
    Store scaling factors for later application during code generation.

    Since our Jacobian stores symbolic expressions, we don't actually scale
    the expressions here. Instead, we return the scaling factors to be
    applied during GAMS code emission.

    Args:
        jacobian: Jacobian structure (not modified)
        R: Row scaling factors (length = number of rows)
        C: Column scaling factors (length = number of columns)

    Returns:
        Tuple of (row_scales, col_scales) as lists for storage
    """
    return R.tolist(), C.tolist()
