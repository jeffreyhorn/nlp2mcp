"""Matrix Market format export for Jacobian structures.

Matrix Market is a standard sparse matrix format supported by SciPy, MATLAB,
and other numerical software. This module exports KKT Jacobians for external
analysis and debugging.

Format specification: https://math.nist.gov/MatrixMarket/formats.html
"""

from __future__ import annotations

from pathlib import Path

from src.ad.jacobian import JacobianStructure
from src.kkt.kkt_system import KKTSystem


def export_jacobian_matrix_market(kkt: KKTSystem, output_path: Path | str) -> None:
    """Export combined KKT Jacobian to Matrix Market format.

    Exports the full KKT Jacobian structure including:
    - Equality constraint Jacobian (J_eq)
    - Inequality constraint Jacobian (J_ineq)

    The exported matrix uses coordinate format (COO) with 1-based indexing
    as per Matrix Market specification.

    Args:
        kkt: KKT system containing Jacobian structures
        output_path: Path to output .mtx file

    Note:
        This exports only the symbolic structure (all nonzeros set to 1.0).
        For numerical values, the model would need to be evaluated at a point.
    """
    output_path = Path(output_path)

    # Collect all nonzero entries from both Jacobians
    entries: list[tuple[int, int, float]] = []

    # Add equality Jacobian entries
    eq_entries = kkt.J_eq.get_nonzero_entries()
    for row, col in eq_entries:
        # Matrix Market uses 1-based indexing
        entries.append((row + 1, col + 1, 1.0))

    # Add inequality Jacobian entries (offset rows by number of equalities)
    ineq_entries = kkt.J_ineq.get_nonzero_entries()
    row_offset = kkt.J_eq.num_rows
    for row, col in ineq_entries:
        entries.append((row + row_offset + 1, col + 1, 1.0))

    # Determine matrix dimensions
    num_rows = kkt.J_eq.num_rows + kkt.J_ineq.num_rows
    num_cols = max(kkt.J_eq.num_cols, kkt.J_ineq.num_cols)
    num_nonzeros = len(entries)

    # Write Matrix Market file
    with output_path.open("w") as f:
        # Header
        f.write("%%MatrixMarket matrix coordinate real general\n")
        f.write("%% KKT Jacobian from nlp2mcp\n")
        f.write(f"%% Rows: {num_rows}, Cols: {num_cols}, Nonzeros: {num_nonzeros}\n")
        f.write("%% Symbolic structure only (all values = 1.0)\n")

        # Dimensions line
        f.write(f"{num_rows} {num_cols} {num_nonzeros}\n")

        # Data lines (sorted by row, then column for better readability)
        entries.sort(key=lambda x: (x[0], x[1]))
        for row, col, val in entries:
            f.write(f"{row} {col} {val}\n")


def export_full_kkt_jacobian_matrix_market(kkt: KKTSystem, output_path: Path | str) -> None:
    """Export full KKT system Jacobian including stationarity structure.

    This exports a more complete view of the KKT Jacobian including:
    - Stationarity equations (gradient + Jacobian transpose terms)
    - Complementarity equations (constraint equations + multiplier terms)

    This provides the complete Jacobian of the MCP system F(z) where z includes
    both primal variables and multipliers.

    Args:
        kkt: KKT system containing full structure
        output_path: Path to output .mtx file

    Note:
        This is a larger, sparser matrix than just the constraint Jacobian.
        Useful for analyzing the full MCP system structure.
    """
    output_path = Path(output_path)

    entries: list[tuple[int, int, float]] = []
    row_idx = 0

    # Count total variables (primal + multipliers)
    num_primal_vars = kkt.gradient.num_cols
    num_multipliers = (
        len(kkt.multipliers_eq)
        + len(kkt.multipliers_ineq)
        + len(kkt.multipliers_bounds_lo)
        + len(kkt.multipliers_bounds_up)
    )
    num_cols = num_primal_vars + num_multipliers

    # Stationarity equations
    # Each stationarity equation has:
    # - Gradient term (wrt primal var)
    # - J_eq^T terms (wrt equality multipliers)
    # - J_ineq^T terms (wrt inequality multipliers)
    # - Bound multiplier terms (if applicable)

    for var_idx in range(num_primal_vars):
        # Gradient contribution
        grad_entry = kkt.gradient.get_derivative(var_idx)
        if grad_entry is not None:
            entries.append((row_idx + 1, var_idx + 1, 1.0))

        # Jacobian transpose contributions (simplified: mark as nonzero)
        # J_eq^T: for each equality, if ∂g_i/∂x_j ≠ 0, then ∂stat_j/∂ν_i ≠ 0
        eq_col = kkt.J_eq.get_col(var_idx)
        for eq_row_idx in eq_col.keys():
            multiplier_col = num_primal_vars + eq_row_idx
            entries.append((row_idx + 1, multiplier_col + 1, 1.0))

        # J_ineq^T: similar for inequalities
        ineq_col = kkt.J_ineq.get_col(var_idx)
        for ineq_row_idx in ineq_col.keys():
            multiplier_col = num_primal_vars + len(kkt.multipliers_eq) + ineq_row_idx
            entries.append((row_idx + 1, multiplier_col + 1, 1.0))

        row_idx += 1

    # Complementarity equations for equalities (h(x) = 0)
    for eq_idx in range(kkt.J_eq.num_rows):
        eq_row = kkt.J_eq.get_row(eq_idx)
        for col_idx in eq_row.keys():
            entries.append((row_idx + 1, col_idx + 1, 1.0))
        row_idx += 1

    # Complementarity equations for inequalities (g(x) ⊥ λ)
    for ineq_idx in range(kkt.J_ineq.num_rows):
        ineq_row = kkt.J_ineq.get_row(ineq_idx)
        for col_idx in ineq_row.keys():
            entries.append((row_idx + 1, col_idx + 1, 1.0))
        row_idx += 1

    # Bound complementarity equations
    # Lower bound equations: (x - lo) ⊥ π^L
    multiplier_col_offset = num_primal_vars + len(kkt.multipliers_eq) + len(kkt.multipliers_ineq)

    # Track multiplier ordering for bounds
    bound_lo_keys = sorted(kkt.complementarity_bounds_lo.keys())
    bound_up_keys = sorted(kkt.complementarity_bounds_up.keys())

    for bound_key in bound_lo_keys:
        var_name, var_indices = bound_key

        # Get primal variable column index
        if kkt.gradient.index_mapping:
            var_col = kkt.gradient.index_mapping.get_col_id(var_name, var_indices)
            if var_col is not None:
                entries.append((row_idx + 1, var_col + 1, 1.0))

        # Get multiplier column index
        multiplier_idx = bound_lo_keys.index(bound_key)
        multiplier_col = multiplier_col_offset + multiplier_idx
        entries.append((row_idx + 1, multiplier_col + 1, 1.0))

        row_idx += 1

    # Upper bound equations: (up - x) ⊥ π^U
    multiplier_col_offset += len(kkt.complementarity_bounds_lo)

    for bound_key in bound_up_keys:
        var_name, var_indices = bound_key

        # Get primal variable column index
        if kkt.gradient.index_mapping:
            var_col = kkt.gradient.index_mapping.get_col_id(var_name, var_indices)
            if var_col is not None:
                entries.append((row_idx + 1, var_col + 1, 1.0))

        # Get multiplier column index
        multiplier_idx = bound_up_keys.index(bound_key)
        multiplier_col = multiplier_col_offset + multiplier_idx
        entries.append((row_idx + 1, multiplier_col + 1, 1.0))

        row_idx += 1

    num_rows = row_idx
    num_nonzeros = len(entries)

    # Write Matrix Market file
    with output_path.open("w") as f:
        f.write("%%MatrixMarket matrix coordinate real general\n")
        f.write("%% Full KKT Jacobian from nlp2mcp\n")
        f.write(f"%% Rows: {num_rows}, Cols: {num_cols}, Nonzeros: {num_nonzeros}\n")
        f.write("%% Includes stationarity + complementarity structure\n")
        f.write("%% Symbolic structure only (all values = 1.0)\n")

        f.write(f"{num_rows} {num_cols} {num_nonzeros}\n")

        entries.sort(key=lambda x: (x[0], x[1]))
        for row, col, val in entries:
            f.write(f"{row} {col} {val}\n")


def export_constraint_jacobian_matrix_market(
    jacobian: JacobianStructure, output_path: Path | str
) -> None:
    """Export a single Jacobian structure to Matrix Market format.

    This is a simpler function for exporting individual Jacobians (J_eq or J_ineq)
    without combining them.

    Args:
        jacobian: Jacobian structure to export
        output_path: Path to output .mtx file
    """
    output_path = Path(output_path)

    entries = []
    for row, col in jacobian.get_nonzero_entries():
        entries.append((row + 1, col + 1, 1.0))

    num_rows = jacobian.num_rows
    num_cols = jacobian.num_cols
    num_nonzeros = len(entries)

    with output_path.open("w") as f:
        f.write("%%MatrixMarket matrix coordinate real general\n")
        f.write("%% Constraint Jacobian from nlp2mcp\n")
        f.write(f"%% Rows: {num_rows}, Cols: {num_cols}, Nonzeros: {num_nonzeros}\n")
        f.write("%% Symbolic structure only (all values = 1.0)\n")

        f.write(f"{num_rows} {num_cols} {num_nonzeros}\n")

        entries.sort(key=lambda x: (x[0], x[1]))
        for row, col, val in entries:
            f.write(f"{row} {col} {val}\n")
