"""Test dotted-key parameter lookup in condition evaluation.

Issue #1223: Table parameters with * wildcard domain store multi-dimensional
row headers as dotted strings. The condition evaluator must try dotted-key
variants when the individual-element tuple lookup fails.
"""

import pytest

from src.ir.condition_eval import _try_dotted_key_lookup


class _FakeParam:
    def __init__(self, domain, values):
        self.domain = domain
        self.values = values


@pytest.mark.unit
class TestDottedKeyLookup:
    def test_dotted_3d_star_domain(self):
        """('a', 'b', 'c', 'type') → ('a.b.c', 'type') lookup."""
        param = _FakeParam(
            domain=("i", "t", "j", "*"),
            values={("a.b.c", "type"): "future", ("a.b.c", "strike"): 100.0},
        )
        result = _try_dotted_key_lookup(param, ("a", "b", "c", "type"))
        assert result == "future"

    def test_dotted_2d_star_domain(self):
        """('x', 'y', 'cost') → ('x.y', 'cost') lookup."""
        param = _FakeParam(
            domain=("i", "j", "*"),
            values={("x.y", "cost"): 42.0},
        )
        result = _try_dotted_key_lookup(param, ("x", "y", "cost"))
        assert result == 42.0

    def test_no_match_returns_none(self):
        """Non-matching indices return None."""
        param = _FakeParam(
            domain=("i", "*"),
            values={("a", "type"): "val"},
        )
        result = _try_dotted_key_lookup(param, ("z", "type"))
        assert result is None

    def test_direct_match_not_needed(self):
        """_try_dotted_key_lookup is only called when direct lookup fails."""
        param = _FakeParam(
            domain=("i", "j"),
            values={("a", "b"): 1.0},
        )
        # _try_dotted_key_lookup tries partial dotting (range(2,2) is empty)
        # and full dotting (("a.b",)), but neither matches ("a","b").
        result = _try_dotted_key_lookup(param, ("a", "b"))
        assert result is None

    def test_full_dotted_string(self):
        """All indices dotted into single-element tuple."""
        param = _FakeParam(
            domain=("i", "j"),
            values={("a.b",): 99.0},
        )
        result = _try_dotted_key_lookup(param, ("a", "b"))
        assert result == 99.0
