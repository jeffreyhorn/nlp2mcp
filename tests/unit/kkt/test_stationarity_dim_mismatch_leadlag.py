"""
Tests for dimension-mismatch lead/lag offset computation in stationarity (Issue #1081).

When a 1D equation references a 2D variable with lead/lag:
    bal4(t).. e(t) = e(t-1) + sum(l, x(t,l) - x(t-ord(l),l))

The stationarity for x(t,l) must include offset multipliers:
    stat_x(t,l).. ... - nu_bal4(t) + nu_bal4(t+ord(l))$(guard) - piL_x(t,l) = 0

This module tests that _compute_index_offset_key correctly computes non-zero
offsets in matched positions during dimension-mismatch, rather than always
returning 0.
"""

from __future__ import annotations

import pytest

from src.ir.model_ir import ModelIR
from src.ir.symbols import SetDef
from src.kkt.stationarity import _SENTINEL_UNMATCHED, _compute_index_offset_key

pytestmark = pytest.mark.unit


def _make_model_ir(sets: dict[str, list[str]]) -> ModelIR:
    """Create a minimal ModelIR with given sets."""
    model = ModelIR()
    for name, members in sets.items():
        model.sets[name] = SetDef(name=name, domain=(), members=members)
    return model


class TestComputeIndexOffsetKeyDimMismatch:
    """Tests for _compute_index_offset_key with dimension mismatch."""

    def test_same_element_zero_offset(self):
        """When matched position has same element, offset is 0."""
        model_ir = _make_model_ir(
            {
                "t": ["1", "2", "3"],
                "l": ["a", "b"],
            }
        )
        result = _compute_index_offset_key(
            eq_indices=("2",),
            var_indices=("2", "a"),
            eq_domain=("t",),
            var_domain=("t", "l"),
            model_ir=model_ir,
        )
        assert result == (0, _SENTINEL_UNMATCHED)

    def test_different_element_positive_offset(self):
        """When matched position has different elements, compute real offset."""
        model_ir = _make_model_ir(
            {
                "t": ["1", "2", "3", "4", "5"],
                "l": ["len-1", "len-2", "len-3", "len-4"],
            }
        )
        # bal4('5') → x('2', 'len-3'): pos('5')=4, pos('2')=1 → offset = 4-1 = 3
        result = _compute_index_offset_key(
            eq_indices=("5",),
            var_indices=("2", "len-3"),
            eq_domain=("t",),
            var_domain=("t", "l"),
            model_ir=model_ir,
        )
        assert result == (3, _SENTINEL_UNMATCHED)

    def test_different_element_negative_offset(self):
        """Negative offset when equation index is before variable index."""
        model_ir = _make_model_ir(
            {
                "t": ["1", "2", "3", "4", "5"],
                "l": ["a", "b"],
            }
        )
        # eq('2') → var('4', 'a'): pos('2')=1, pos('4')=3 → offset = 1-3 = -2
        result = _compute_index_offset_key(
            eq_indices=("2",),
            var_indices=("4", "a"),
            eq_domain=("t",),
            var_domain=("t", "l"),
            model_ir=model_ir,
        )
        assert result == (-2, _SENTINEL_UNMATCHED)

    def test_groups_by_distinct_offsets(self):
        """Entries with different t-offsets should get different offset keys."""
        model_ir = _make_model_ir(
            {
                "t": ["1", "2", "3", "4", "5"],
                "l": ["len-1", "len-2", "len-3", "len-4"],
            }
        )
        # Direct: bal4('3') → x('3', 'len-1') → offset 0
        key_direct = _compute_index_offset_key(
            eq_indices=("3",),
            var_indices=("3", "len-1"),
            eq_domain=("t",),
            var_domain=("t", "l"),
            model_ir=model_ir,
        )
        # Offset-1: bal4('4') → x('3', 'len-1') → offset 1
        key_off1 = _compute_index_offset_key(
            eq_indices=("4",),
            var_indices=("3", "len-1"),
            eq_domain=("t",),
            var_domain=("t", "l"),
            model_ir=model_ir,
        )
        # Offset-2: bal4('5') → x('3', 'len-2') → offset 2
        key_off2 = _compute_index_offset_key(
            eq_indices=("5",),
            var_indices=("3", "len-2"),
            eq_domain=("t",),
            var_domain=("t", "l"),
            model_ir=model_ir,
        )
        assert key_direct == (0, _SENTINEL_UNMATCHED)
        assert key_off1 == (1, _SENTINEL_UNMATCHED)
        assert key_off2 == (2, _SENTINEL_UNMATCHED)
        # All three are distinct
        assert key_direct != key_off1
        assert key_off1 != key_off2


class TestComputeIndexOffsetKeySameDim:
    """Verify same-dimension offset computation still works (regression)."""

    def test_same_dim_offset(self):
        """Basic same-dimension offset."""
        model_ir = _make_model_ir({"t": ["1990", "1995", "2000", "2005"]})
        result = _compute_index_offset_key(
            eq_indices=("1990",),
            var_indices=("1995",),
            eq_domain=("t",),
            var_domain=("t",),
            model_ir=model_ir,
        )
        assert result == (-1,)

    def test_same_dim_zero_offset(self):
        """Same element = offset 0."""
        model_ir = _make_model_ir({"t": ["1990", "1995", "2000"]})
        result = _compute_index_offset_key(
            eq_indices=("1995",),
            var_indices=("1995",),
            eq_domain=("t",),
            var_domain=("t",),
            model_ir=model_ir,
        )
        assert result == (0,)
