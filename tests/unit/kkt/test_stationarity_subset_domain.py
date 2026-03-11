"""Tests for _match_subset_domain and _rewrite_subset_to_superset (#1041).

When a constraint is indexed by dynamic subsets (e.g., (ii, jj)) and a
variable is indexed by the parent sets (e.g., (i, j)), the stationarity
builder must match domains via subset/alias relationships and rewrite
indices accordingly, rather than wrapping in Sum().
"""

from __future__ import annotations

import pytest

from src.ir.ast import ParamRef, VarRef
from src.ir.model_ir import ModelIR
from src.ir.symbols import AliasDef, SetDef
from src.kkt.stationarity import _match_subset_domain, _rewrite_subset_to_superset


@pytest.mark.unit
class TestMatchSubsetDomain:
    """Tests for _match_subset_domain()."""

    def _make_model(self) -> ModelIR:
        """Model with set i, dynamic subset ii(i), and alias jj -> ii."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["a", "b", "total"], domain=("*",))
        model.sets["ii"] = SetDef(name="ii", members=[], domain=("i",))
        model.aliases["jj"] = AliasDef(name="jj", target="ii")
        # Also alias j -> i for parent-level aliasing
        model.aliases["j"] = AliasDef(name="j", target="i")
        return model

    def test_subset_to_parent_match(self):
        """(ii, jj) should match (i, j) via subset relationship."""
        model = self._make_model()
        result = _match_subset_domain(("ii", "jj"), ("i", "j"), model)
        assert result is not None
        assert result["ii"] == "i"
        # jj is alias of ii which is subset of i; j is alias of i
        assert "jj" in result

    def test_equal_domains_no_rename(self):
        """(i, j) vs (i, j) should return empty dict (identity match)."""
        model = self._make_model()
        result = _match_subset_domain(("i", "j"), ("i", "j"), model)
        assert result is not None
        assert result == {}

    def test_shorter_mult_domain(self):
        """(ii,) vs (i, j, k) — shorter mult domain can match."""
        model = self._make_model()
        model.sets["k"] = SetDef(name="k", members=["k1"], domain=("*",))
        result = _match_subset_domain(("ii",), ("i", "j", "k"), model)
        assert result is not None
        assert "ii" in result

    def test_longer_mult_domain_fails(self):
        """(ii, jj, k) vs (i, j) — longer mult domain returns None."""
        model = self._make_model()
        model.sets["k"] = SetDef(name="k", members=["k1"], domain=("*",))
        result = _match_subset_domain(("ii", "jj", "k"), ("i", "j"), model)
        assert result is None

    def test_no_relationship_fails(self):
        """(ii,) vs (k,) where ii and k are unrelated returns None."""
        model = self._make_model()
        model.sets["k"] = SetDef(name="k", members=["k1"], domain=("*",))
        result = _match_subset_domain(("ii",), ("k",), model)
        assert result is None

    def test_position_aware_matching(self):
        """(jj,) vs (i, j) should prefer position 0, mapping jj -> i."""
        model = self._make_model()
        result = _match_subset_domain(("jj",), ("i", "j"), model)
        assert result is not None
        # jj at position 0 should match i at position 0
        assert result["jj"] == "i"


@pytest.mark.unit
class TestRewriteSubsetToSuperset:
    """Tests for _rewrite_subset_to_superset()."""

    def test_rewrite_varref_indices(self):
        """VarRef indices should be rewritten according to rename_map."""
        expr = VarRef("x", ("ii", "jj"))
        result = _rewrite_subset_to_superset(expr, {"ii": "i", "jj": "j"})
        assert isinstance(result, VarRef)
        assert result.indices == ("i", "j")

    def test_rewrite_paramref_indices(self):
        """ParamRef indices should be rewritten."""
        expr = ParamRef("p", ("ii", "jj"))
        result = _rewrite_subset_to_superset(expr, {"ii": "i", "jj": "j"})
        assert isinstance(result, ParamRef)
        assert result.indices == ("i", "j")

    def test_empty_rename_map_noop(self):
        """Empty rename_map should return expression unchanged."""
        expr = VarRef("x", ("i", "j"))
        result = _rewrite_subset_to_superset(expr, {})
        assert result is expr
