"""Test gradient condition index remapping.

Issue #1062: When a variable's gradient condition uses equation-context
indices (e.g., e(n,i)) that don't match the variable domain (e.g., (n,n)),
_remap_condition_to_domain replaces non-domain indices with the variable's
domain indices at the corresponding position.
"""

import pytest

from src.ir.ast import SetMembershipTest, SymbolRef
from src.kkt.stationarity import _remap_condition_to_domain


@pytest.mark.unit
class TestRemapConditionToDomain:
    def test_replaces_non_domain_index(self):
        """e(n,i) with domain (n,n) → e(n,n)."""
        cond = SetMembershipTest("e", (SymbolRef("n"), SymbolRef("i")))
        result = _remap_condition_to_domain(cond, ("n", "n"))

        assert isinstance(result, SetMembershipTest)
        assert result.set_name == "e"
        assert len(result.indices) == 2
        assert result.indices[0].name == "n"
        assert result.indices[1].name == "n"

    def test_preserves_matching_indices(self):
        """e(i,j) with domain (i,j) → unchanged."""
        cond = SetMembershipTest("e", (SymbolRef("i"), SymbolRef("j")))
        result = _remap_condition_to_domain(cond, ("i", "j"))

        assert result is cond  # Unchanged

    def test_case_insensitive_match(self):
        """E(N,I) with domain (n,n) → E(N,n): N preserved, I replaced."""
        cond = SetMembershipTest("E", (SymbolRef("N"), SymbolRef("I")))
        result = _remap_condition_to_domain(cond, ("n", "n"))

        assert isinstance(result, SetMembershipTest)
        # N matches domain 'n' case-insensitively → preserved as-is
        assert result.indices[0].name == "N"
        # I not in domain → replaced with domain[1] = 'n'
        assert result.indices[1].name == "n"

    def test_non_smt_condition_unchanged(self):
        """Non-SetMembershipTest conditions pass through."""
        from src.ir.ast import Const

        result = _remap_condition_to_domain(Const(1.0), ("n", "n"))
        assert isinstance(result, Const)
