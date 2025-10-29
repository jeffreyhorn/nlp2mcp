"""
Sparsity Tracking for Jacobian Structure

This module analyzes expressions to determine which variables appear in which equations,
building the sparsity pattern for the Jacobian matrix.

Day 6 Scope:
-----------
- Track variable dependencies in expressions (which vars appear where)
- Build sparsity pattern: set of (row, col) pairs that are nonzero
- Support for indexed variables and sums
- Foundation for efficient Jacobian construction (only compute nonzero entries)

Mathematical Background:
-----------------------
The Jacobian J[i,j] = ∂f_i/∂x_j is sparse when many entries are zero.
This happens when equation i doesn't depend on variable j.

For example:
- Equation g1: x + y ≤ 0    → depends on {x, y}
- Equation g2: z^2 ≤ 0      → depends on {z}
- Jacobian sparsity:
  J[0, :] = [∂g1/∂x, ∂g1/∂y, ∂g1/∂z] = [nonzero, nonzero, zero]
  J[1, :] = [∂g2/∂x, ∂g2/∂y, ∂g2/∂z] = [zero, zero, nonzero]

Only (0,0), (0,1), (1,2) need to be computed and stored.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..ir.ast import Expr

from ..ir.ast import Binary, Call, Const, ParamRef, Sum, SymbolRef, Unary, VarRef


@dataclass
class SparsityPattern:
    """
    Sparsity pattern for Jacobian matrix.

    Tracks which (equation, variable) pairs have nonzero derivatives.

    Attributes:
        nonzero_entries: Set of (row_id, col_id) pairs that are nonzero
        row_dependencies: Map row_id → set of col_ids that appear in that row
        col_dependencies: Map col_id → set of row_ids that depend on that column
    """

    nonzero_entries: set[tuple[int, int]] = field(default_factory=set)
    row_dependencies: dict[int, set[int]] = field(default_factory=dict)
    col_dependencies: dict[int, set[int]] = field(default_factory=dict)

    def add_dependency(self, row_id: int, col_id: int) -> None:
        """
        Mark that equation row_id depends on variable col_id.

        Args:
            row_id: Equation row ID
            col_id: Variable column ID
        """
        self.nonzero_entries.add((row_id, col_id))

        if row_id not in self.row_dependencies:
            self.row_dependencies[row_id] = set()
        self.row_dependencies[row_id].add(col_id)

        if col_id not in self.col_dependencies:
            self.col_dependencies[col_id] = set()
        self.col_dependencies[col_id].add(row_id)

    def get_row_nonzeros(self, row_id: int) -> set[int]:
        """
        Get all column IDs that appear in a given row.

        Args:
            row_id: Row ID

        Returns:
            Set of column IDs
        """
        return self.row_dependencies.get(row_id, set())

    def get_col_nonzeros(self, col_id: int) -> set[int]:
        """
        Get all row IDs that depend on a given column.

        Args:
            col_id: Column ID

        Returns:
            Set of row IDs
        """
        return self.col_dependencies.get(col_id, set())

    def num_nonzeros(self) -> int:
        """Get total number of nonzero entries."""
        return len(self.nonzero_entries)

    def density(self, num_rows: int, num_cols: int) -> float:
        """
        Compute sparsity density (fraction of nonzero entries).

        Args:
            num_rows: Total number of rows
            num_cols: Total number of columns

        Returns:
            Density as fraction (0.0 = all zeros, 1.0 = all nonzeros)
        """
        total_entries = num_rows * num_cols
        if total_entries == 0:
            return 0.0
        return len(self.nonzero_entries) / total_entries


def find_variables_in_expr(expr: Expr) -> set[str]:
    """
    Find all variable names that appear in an expression.

    This traverses the expression AST and collects all VarRef and SymbolRef names.
    Does not distinguish between different indices (x(i) and x(j) both → "x").

    Args:
        expr: Expression to analyze

    Returns:
        Set of variable base names

    Examples:
        >>> # x + y
        >>> find_variables_in_expr(Binary("+", VarRef("x"), VarRef("y")))
        {"x", "y"}

        >>> # sum(i, x(i)*c)  where c is parameter
        >>> find_variables_in_expr(Sum(("i",), Binary("*", VarRef("x", ("i",)), ParamRef("c"))))
        {"x"}

        >>> # exp(x) + log(y)
        >>> find_variables_in_expr(Binary("+", Call("exp", [VarRef("x")]), Call("log", [VarRef("y")])))
        {"x", "y"}
    """
    variables: set[str] = set()
    _collect_variables(expr, variables)
    return variables


def _collect_variables(expr: Expr, variables: set[str]) -> None:
    """
    Recursively collect variable names from expression.

    Args:
        expr: Expression to traverse
        variables: Set to accumulate variable names (modified in-place)
    """
    if isinstance(expr, Const):
        # Constants don't depend on variables
        pass

    elif isinstance(expr, VarRef):
        # Variable reference: add base name (ignore indices)
        variables.add(expr.name)

    elif isinstance(expr, SymbolRef):
        # Symbol reference: treat as variable
        variables.add(expr.name)

    elif isinstance(expr, ParamRef):
        # Parameters are constant w.r.t. variables
        pass

    elif isinstance(expr, Binary):
        # Binary operation: recurse on both operands
        _collect_variables(expr.left, variables)
        _collect_variables(expr.right, variables)

    elif isinstance(expr, Unary):
        # Unary operation: recurse on operand
        _collect_variables(expr.child, variables)

    elif isinstance(expr, Call):
        # Function call: recurse on all arguments
        for arg in expr.args:
            _collect_variables(arg, variables)

    elif isinstance(expr, Sum):
        # Sum aggregation: recurse on body
        _collect_variables(expr.body, variables)

    else:
        # Unknown expression type: conservative approach (assume no variables)
        # Could raise warning or error depending on strictness desired
        pass


def analyze_expression_sparsity(expr: Expr, var_names_to_col_ids: dict[str, list[int]]) -> set[int]:
    """
    Analyze which variable columns an expression depends on.

    Args:
        expr: Expression to analyze
        var_names_to_col_ids: Map from variable base name → list of column IDs

    Returns:
        Set of column IDs that this expression depends on

    Example:
        >>> # Expression: x(i) + y
        >>> # Variables: x has col_ids [0, 1] for x(i1), x(i2)
        >>> #            y has col_id [2] for scalar y
        >>> var_names_to_col_ids = {"x": [0, 1], "y": [2]}
        >>> expr = Binary("+", VarRef("x", ("i",)), VarRef("y"))
        >>> analyze_expression_sparsity(expr, var_names_to_col_ids)
        {0, 1, 2}  # All instances of x and y
    """
    # Find variable names in expression
    var_names = find_variables_in_expr(expr)

    # Map to column IDs
    col_ids: set[int] = set()
    for var_name in var_names:
        if var_name in var_names_to_col_ids:
            # Add all column IDs for this variable
            col_ids.update(var_names_to_col_ids[var_name])

    return col_ids
