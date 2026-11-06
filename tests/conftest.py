"""Shared test fixtures and utilities.

This module provides pytest fixtures and helper functions used across
multiple test files to reduce duplication and ensure consistency.
"""

import sys
from pathlib import Path

import pytest

from src.ad.index_mapping import IndexMapping

# Add tests directory to sys.path to allow imports from fixtures
tests_dir = Path(__file__).parent
if str(tests_dir) not in sys.path:
    sys.path.insert(0, str(tests_dir))

# Add the project root to sys.path so ``from tests.helpers.anchor_resolver import ...``
# resolves. ``--import-mode=importlib`` (pyproject.toml) deliberately does NOT
# insert the rootdir, and the editable install only exposes ``src*``, so without
# this, the import fails in CI with "'tests' is not a package" -- even though
# it works locally, where CWD leaks in via the entry-point shim.
project_root = tests_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@pytest.fixture
def manual_index_mapping():
    """Fixture that returns a helper function to manually create IndexMapping for tests.

    Returns:
        Function that creates IndexMapping from variable and equation lists

    Example:
        >>> def test_something(manual_index_mapping):
        >>>     mapping = manual_index_mapping([("x", ()), ("y", ("i1",))])
        >>>     assert mapping.var_to_col[("x", ())] == 0
    """

    def _manual_index_mapping(
        vars: list[tuple[str, tuple]], eqs: list[tuple[str, tuple]] | None = None
    ) -> IndexMapping:
        """Helper to manually create IndexMapping for tests.

        Args:
            vars: List of (var_name, indices) tuples for variables
            eqs: Optional list of (eq_name, indices) tuples for equations

        Returns:
            IndexMapping with specified variables and equations
        """
        mapping = IndexMapping()

        for col_id, (var_name, indices) in enumerate(vars):
            mapping.var_to_col[(var_name, indices)] = col_id
            mapping.col_to_var[col_id] = (var_name, indices)
        mapping.num_vars = len(vars)

        if eqs:
            for row_id, (eq_name, indices) in enumerate(eqs):
                mapping.eq_to_row[(eq_name, indices)] = row_id
                mapping.row_to_eq[row_id] = (eq_name, indices)
            mapping.num_eqs = len(eqs)

        return mapping

    return _manual_index_mapping
