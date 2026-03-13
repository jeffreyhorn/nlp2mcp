"""Tests for multi-index partial matching in _partial_index_match().

Issue #764: When a Sum has multiple index sets (e.g., sum((j,l), ...)) and
wrt_indices has more indices than the sum (e.g., x('a','b','c','d')),
the matching must find positions arbitrarily, not just by prefix.

For example: sum((j,l), x(i,j,k,l)) w.r.t. x('summer','normal','bolts','m1')
- j (={normal,overtime}) should match position 1 ('normal')
- l (={m1,m2,m3}) should match position 3 ('m1')
- NOT prefix: j does NOT match position 0 ('summer')
"""

from __future__ import annotations

import pytest

from src.ad.derivative_rules import _partial_index_match
from src.config import Config
from src.ir.model_ir import ModelIR
from src.ir.symbols import SetDef

pytestmark = pytest.mark.unit


def _make_config_with_sets(sets: dict[str, list[str]]) -> Config:
    """Create a Config with a ModelIR containing the given sets."""
    model_ir = ModelIR()
    for name, members in sets.items():
        model_ir.sets[name] = SetDef(name=name, members=members)
    config = Config()
    config.model_ir = model_ir
    return config


class TestMultiIndexPartialMatch:
    """Tests for arbitrary-position matching in _partial_index_match."""

    def test_prefix_match_still_works(self):
        """Multi-index prefix match: sum((i,k), ...) w.r.t. (a, b, c, d).

        When sum indices are a prefix of wrt_indices, the old prefix matching
        behavior should still work.
        """
        config = _make_config_with_sets(
            {
                "i": ["summer", "winter"],
                "k": ["bolts", "nuts", "washers"],
            }
        )
        matched_sym, matched_conc, remaining, symbolic_wrt = _partial_index_match(
            ("i", "k"), ("summer", "bolts", "normal", "m1"), config
        )
        assert matched_sym == ("i", "k")
        assert matched_conc == ("summer", "bolts")
        assert remaining == ("normal", "m1")
        assert symbolic_wrt == ("i", "k", "normal", "m1")

    def test_nonprefix_match(self):
        """Multi-index non-prefix match: sum((j,l), ...) w.r.t. (summer, normal, bolts, m1).

        j={normal,overtime} matches position 1, l={m1,m2,m3} matches position 3.
        """
        config = _make_config_with_sets(
            {
                "j": ["normal", "overtime"],
                "l": ["m1", "m2", "m3"],
                "i": ["summer", "winter"],
                "k": ["bolts", "nuts", "washers"],
            }
        )
        matched_sym, matched_conc, remaining, symbolic_wrt = _partial_index_match(
            ("j", "l"), ("summer", "normal", "bolts", "m1"), config
        )
        assert matched_sym == ("j", "l")
        assert matched_conc == ("normal", "m1")
        assert remaining == ("summer", "bolts")
        assert symbolic_wrt == ("summer", "j", "bolts", "l")

    def test_no_match_returns_empty(self):
        """No match when sum indices don't match any wrt position."""
        config = _make_config_with_sets(
            {
                "j": ["normal", "overtime"],
                "l": ["m1", "m2", "m3"],
            }
        )
        matched_sym, matched_conc, remaining, symbolic_wrt = _partial_index_match(
            ("j", "l"), ("summer", "bolts"), config
        )
        assert matched_sym == ()
        assert matched_conc == ()
        assert symbolic_wrt is None

    def test_single_index_arbitrary_position(self):
        """Single-index match at non-prefix position (existing behavior)."""
        config = _make_config_with_sets(
            {
                "k": ["bolts", "nuts", "washers"],
            }
        )
        matched_sym, matched_conc, remaining, symbolic_wrt = _partial_index_match(
            ("k",), ("summer", "normal", "bolts", "m1"), config
        )
        assert matched_sym == ("k",)
        assert matched_conc == ("bolts",)
        assert remaining == ("summer", "normal", "m1")
        assert symbolic_wrt == ("summer", "normal", "k", "m1")
