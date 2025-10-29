"""
Jacobian Structure for Sparse Storage

This module provides the JacobianStructure class for storing sparse Jacobian matrices.
Each entry stores the derivative expression (AST) rather than a numeric value.

Day 7 Scope:
-----------
- JacobianStructure class: Sparse dict-based storage
- Storage format: J[row_id][col_id] = derivative_expr (AST)
- Query interface: get_derivative(eq_instance, var_instance)
- Integration with IndexMapping from Day 6

Mathematical Background:
-----------------------
The Jacobian matrix J represents the derivatives of a system of equations:
- J[i,j] = ∂f_i/∂x_j
- For constraint system: J_g for inequalities, J_h for equalities
- Sparse storage: Only store nonzero entries (most entries are zero)

Example:
--------
For equations:
  g1(x,y): x + y <= 0
  g2(z): z^2 <= 0

Jacobian J_g:
  ∂g1/∂x = 1, ∂g1/∂y = 1, ∂g1/∂z = 0
  ∂g2/∂x = 0, ∂g2/∂y = 0, ∂g2/∂z = 2*z

Sparse storage: {0: {0: Const(1), 1: Const(1)}, 1: {2: Binary(*, Const(2), VarRef(z))}}
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..ir.ast import Expr
    from .index_mapping import IndexMapping


@dataclass
class JacobianStructure:
    """
    Sparse Jacobian matrix structure storing derivative expressions.

    Attributes:
        entries: Nested dict J[row_id][col_id] = derivative_expr (AST)
        index_mapping: IndexMapping for variable/equation instance lookups
        num_rows: Total number of rows (equations)
        num_cols: Total number of columns (variables)
    """

    entries: dict[int, dict[int, Expr]] = field(default_factory=dict)
    index_mapping: IndexMapping | None = None
    num_rows: int = 0
    num_cols: int = 0

    def set_derivative(self, row_id: int, col_id: int, derivative_expr: Expr) -> None:
        """
        Store a derivative expression at (row, col).

        Args:
            row_id: Row index (equation instance)
            col_id: Column index (variable instance)
            derivative_expr: Derivative AST expression
        """
        if row_id not in self.entries:
            self.entries[row_id] = {}
        self.entries[row_id][col_id] = derivative_expr

    def get_derivative(self, row_id: int, col_id: int) -> Expr | None:
        """
        Retrieve derivative expression at (row, col).

        Args:
            row_id: Row index
            col_id: Column index

        Returns:
            Derivative expression, or None if entry doesn't exist (zero derivative)
        """
        if row_id in self.entries:
            return self.entries[row_id].get(col_id)
        return None

    def get_derivative_by_names(
        self, eq_name: str, eq_indices: tuple[str, ...], var_name: str, var_indices: tuple[str, ...]
    ) -> Expr | None:
        """
        Retrieve derivative using equation and variable names.

        Requires index_mapping to be set.

        Args:
            eq_name: Equation name
            eq_indices: Equation index tuple
            var_name: Variable name
            var_indices: Variable index tuple

        Returns:
            Derivative expression, or None if not found

        Raises:
            ValueError: If index_mapping is not set
        """
        if self.index_mapping is None:
            raise ValueError("index_mapping must be set to use get_derivative_by_names")

        row_id = self.index_mapping.get_row_id(eq_name, eq_indices)
        col_id = self.index_mapping.get_col_id(var_name, var_indices)

        if row_id is None or col_id is None:
            return None

        return self.get_derivative(row_id, col_id)

    def get_row(self, row_id: int) -> dict[int, Expr]:
        """
        Get all nonzero entries in a row.

        Args:
            row_id: Row index

        Returns:
            Dict mapping col_id → derivative_expr for nonzero entries
        """
        return self.entries.get(row_id, {})

    def get_col(self, col_id: int) -> dict[int, Expr]:
        """
        Get all nonzero entries in a column.

        Args:
            col_id: Column index

        Returns:
            Dict mapping row_id → derivative_expr for nonzero entries
        """
        col_entries: dict[int, Expr] = {}
        for row_id, row_dict in self.entries.items():
            if col_id in row_dict:
                col_entries[row_id] = row_dict[col_id]
        return col_entries

    def get_nonzero_entries(self) -> list[tuple[int, int]]:
        """
        Get list of all (row, col) pairs with nonzero entries.

        Returns:
            List of (row_id, col_id) tuples
        """
        entries: list[tuple[int, int]] = []
        for row_id, row_dict in self.entries.items():
            for col_id in row_dict.keys():
                entries.append((row_id, col_id))
        return entries

    def num_nonzeros(self) -> int:
        """
        Count total number of nonzero entries.

        Returns:
            Number of stored derivatives
        """
        count = 0
        for row_dict in self.entries.values():
            count += len(row_dict)
        return count

    def density(self) -> float:
        """
        Compute density (fraction of nonzero entries).

        Returns:
            Density as fraction (0.0 = all zeros, 1.0 = all nonzeros)
        """
        total_entries = self.num_rows * self.num_cols
        if total_entries == 0:
            return 0.0
        return self.num_nonzeros() / total_entries

    def __repr__(self) -> str:
        """String representation showing dimensions and sparsity."""
        return (
            f"JacobianStructure({self.num_rows}x{self.num_cols}, "
            f"{self.num_nonzeros()} nonzeros, "
            f"density={self.density():.2%})"
        )


@dataclass
class GradientVector:
    """
    Gradient vector storing derivative expressions for objective function.

    Attributes:
        entries: Dict mapping col_id → derivative_expr
        index_mapping: IndexMapping for variable instance lookups
        num_cols: Total number of variables
    """

    entries: dict[int, Expr] = field(default_factory=dict)
    index_mapping: IndexMapping | None = None
    num_cols: int = 0

    def set_derivative(self, col_id: int, derivative_expr: Expr) -> None:
        """
        Store gradient component for a variable.

        Args:
            col_id: Column index (variable instance)
            derivative_expr: Derivative AST expression
        """
        self.entries[col_id] = derivative_expr

    def get_derivative(self, col_id: int) -> Expr | None:
        """
        Retrieve gradient component for a variable.

        Args:
            col_id: Column index

        Returns:
            Derivative expression, or None if not set
        """
        return self.entries.get(col_id)

    def get_derivative_by_name(
        self, var_name: str, var_indices: tuple[str, ...] = ()
    ) -> Expr | None:
        """
        Retrieve gradient component using variable name.

        Requires index_mapping to be set.

        Args:
            var_name: Variable name
            var_indices: Variable index tuple

        Returns:
            Derivative expression, or None if not found

        Raises:
            ValueError: If index_mapping is not set
        """
        if self.index_mapping is None:
            raise ValueError("index_mapping must be set to use get_derivative_by_name")

        col_id = self.index_mapping.get_col_id(var_name, var_indices)
        if col_id is None:
            return None

        return self.get_derivative(col_id)

    def get_all_derivatives(self) -> dict[int, Expr]:
        """
        Get all gradient components.

        Returns:
            Dict mapping col_id → derivative_expr
        """
        return self.entries.copy()

    def num_nonzeros(self) -> int:
        """
        Count number of nonzero gradient components.

        Returns:
            Number of stored derivatives
        """
        return len(self.entries)

    def __repr__(self) -> str:
        """String representation showing dimension and sparsity."""
        return f"GradientVector({self.num_cols} variables, {self.num_nonzeros()} nonzeros)"
