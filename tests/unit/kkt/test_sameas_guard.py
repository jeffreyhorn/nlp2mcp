"""Tests for _build_sameas_guard() and _find_matching_subset().

Issue #767 / #764: The sameas guard restricts scalar-constraint multiplier
terms to only the relevant variable instances.  The original implementation
used only entries[0], which was correct for single-entry .fx patterns but
broke when a scalar equation sums over a subset of the indexed variable.

These tests verify the refactored multi-entry guard logic:
- Single entry → sameas guard (original .fx behavior)
- All entries cover all instances → no guard
- Partial coverage with named subset → subset membership or sameas
- Partial coverage with multiple values → OR-disjunction of sameas
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.ir.ast import Binary, Call
from src.ir.model_ir import ModelIR
from src.ir.symbols import SetDef
from src.kkt.stationarity import _build_sameas_guard, _find_matching_subset

pytestmark = pytest.mark.unit


def _make_kkt(sets: dict[str, SetDef] | None = None):
    """Build a minimal mock KKTSystem with gradient.index_mapping."""
    kkt = MagicMock()
    model_ir = ModelIR()
    if sets:
        for name, sd in sets.items():
            model_ir.sets[name] = sd
    kkt.model_ir = model_ir
    return kkt


class TestFindMatchingSubset:
    """Tests for _find_matching_subset()."""

    def test_exact_match_returns_subset_name(self):
        model_ir = ModelIR()
        model_ir.sets["c"] = SetDef(name="c", members=["steel", "copper", "aluminum"])
        model_ir.sets["cf"] = SetDef(name="cf", members=["steel"], domain=("c",))
        result = _find_matching_subset("c", {"steel"}, model_ir)
        assert result == "cf"

    def test_no_match_returns_none(self):
        model_ir = ModelIR()
        model_ir.sets["c"] = SetDef(name="c", members=["steel", "copper", "aluminum"])
        model_ir.sets["cf"] = SetDef(name="cf", members=["steel"], domain=("c",))
        result = _find_matching_subset("c", {"copper"}, model_ir)
        assert result is None

    def test_case_insensitive_match(self):
        model_ir = ModelIR()
        model_ir.sets["c"] = SetDef(name="c", members=["Steel", "Copper"])
        model_ir.sets["cf"] = SetDef(name="cf", members=["Steel"], domain=("c",))
        result = _find_matching_subset("c", {"steel"}, model_ir)
        assert result == "cf"

    def test_no_subsets_returns_none(self):
        model_ir = ModelIR()
        model_ir.sets["c"] = SetDef(name="c", members=["steel", "copper"])
        result = _find_matching_subset("c", {"steel"}, model_ir)
        assert result is None


class TestBuildSameasGuard:
    """Tests for _build_sameas_guard()."""

    def test_single_entry_produces_sameas(self):
        """Single entry (e.g. .fx) should produce sameas guard."""
        kkt = _make_kkt()
        # Variable x(j) with instances j1, j2, j3
        instances = [(10, ("j1",)), (11, ("j2",)), (12, ("j3",))]
        # Only one entry: col 10 → x('j1')
        entries = [(0, 10)]
        kkt.gradient.index_mapping.col_to_var = {
            10: ("x", ("j1",)),
            11: ("x", ("j2",)),
            12: ("x", ("j3",)),
        }

        guard = _build_sameas_guard(("j",), instances, entries, kkt)
        assert guard is not None
        # Should be sameas(j, 'j1')
        assert isinstance(guard, Call)
        assert guard.func == "sameas"

    def test_full_coverage_no_guard(self):
        """When entries cover all instances, no guard is needed."""
        kkt = _make_kkt()
        instances = [(10, ("j1",)), (11, ("j2",)), (12, ("j3",))]
        # All three entries
        entries = [(0, 10), (1, 11), (2, 12)]
        kkt.gradient.index_mapping.col_to_var = {
            10: ("x", ("j1",)),
            11: ("x", ("j2",)),
            12: ("x", ("j3",)),
        }

        guard = _build_sameas_guard(("j",), instances, entries, kkt)
        assert guard is None

    def test_multi_entry_partial_coverage_or_disjunction(self):
        """Multiple entries covering a subset produce OR-disjunction."""
        kkt = _make_kkt()
        instances = [(10, ("j1",)), (11, ("j2",)), (12, ("j3",))]
        # Two entries: j1, j2
        entries = [(0, 10), (1, 11)]
        kkt.gradient.index_mapping.col_to_var = {
            10: ("x", ("j1",)),
            11: ("x", ("j2",)),
            12: ("x", ("j3",)),
        }

        guard = _build_sameas_guard(("j",), instances, entries, kkt)
        assert guard is not None
        # Should be sameas(j,'j1') or sameas(j,'j2')
        assert isinstance(guard, Binary)
        assert guard.op == "or"

    def test_multi_entry_named_subset_match(self):
        """Single-value subset uses sameas; multi-value subset uses SetMembershipTest."""
        kkt = _make_kkt(
            sets={
                "c": SetDef(name="c", members=["steel", "copper", "aluminum"]),
                "cf": SetDef(name="cf", members=["steel"], domain=("c",)),
            }
        )
        instances = [
            (10, ("steel", "a")),
            (11, ("steel", "b")),
            (12, ("copper", "a")),
            (13, ("copper", "b")),
            (14, ("aluminum", "a")),
            (15, ("aluminum", "b")),
        ]
        # Entries for steel only
        entries = [(0, 10), (1, 11)]
        kkt.gradient.index_mapping.col_to_var = {
            10: ("e", ("steel", "a")),
            11: ("e", ("steel", "b")),
            12: ("e", ("copper", "a")),
            13: ("e", ("copper", "b")),
            14: ("e", ("aluminum", "a")),
            15: ("e", ("aluminum", "b")),
        }

        guard = _build_sameas_guard(("c", "i"), instances, entries, kkt)
        assert guard is not None
        # First dimension: cf={steel} is a single value → sameas(c,'steel')
        # (Named subset cf exists but single-value path uses sameas directly)
        # Second dimension: {a,b} covers all i values, so no guard
        assert isinstance(guard, Call)
        assert guard.func == "sameas"

    def test_multidim_partial_both_dimensions(self):
        """Partial coverage in both dimensions produces AND of guards."""
        kkt = _make_kkt()
        instances = [
            (10, ("a", "x")),
            (11, ("a", "y")),
            (12, ("b", "x")),
            (13, ("b", "y")),
        ]
        # Only one entry: (a, x)
        entries = [(0, 10)]
        kkt.gradient.index_mapping.col_to_var = {
            10: ("v", ("a", "x")),
            11: ("v", ("a", "y")),
            12: ("v", ("b", "x")),
            13: ("v", ("b", "y")),
        }

        guard = _build_sameas_guard(("i", "j"), instances, entries, kkt)
        assert guard is not None
        # Should be sameas(i,'a') and sameas(j,'x')
        assert isinstance(guard, Binary)
        assert guard.op == "and"

    def test_non_cartesian_entries_fallback_to_tuple_or(self):
        """Entries covering all per-dim values but not all tuples get OR-of-ANDs guard.

        Entries {(a,x),(b,y)} cover {a,b}×{x,y} per-dimension but miss
        tuples (a,y) and (b,x).  The guard must not return None.
        """
        kkt = _make_kkt()
        instances = [
            (10, ("a", "x")),
            (11, ("a", "y")),
            (12, ("b", "x")),
            (13, ("b", "y")),
        ]
        # Two entries that cover all dim values but NOT all tuples
        entries = [(0, 10), (1, 13)]  # (a,x) and (b,y)
        kkt.gradient.index_mapping.col_to_var = {
            10: ("v", ("a", "x")),
            11: ("v", ("a", "y")),
            12: ("v", ("b", "x")),
            13: ("v", ("b", "y")),
        }

        guard = _build_sameas_guard(("i", "j"), instances, entries, kkt)
        assert guard is not None
        # Should be OR of two AND-conjunctions:
        # (sameas(i,'a') and sameas(j,'x')) or (sameas(i,'b') and sameas(j,'y'))
        assert isinstance(guard, Binary)
        assert guard.op == "or"
