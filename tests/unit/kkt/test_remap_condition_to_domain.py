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

    def test_repeated_set_domain_claims_each_slot_once(self):
        """Issue #1062: `e(n,i)` against the DE-DUPLICATED domain `(n,n__)`.

        `e` is itself declared `e(n,n)`, so #1350's parent-set lookup asks for
        "the var_domain index whose root is `n`" at BOTH positions.  A
        first-match scan answers `n` twice and re-collapses the guard onto the
        diagonal — `e(n,n)` — which is exactly the row-generation failure
        `dedupe_repeated_variable_domains` was introduced to remove.  Each
        var_domain slot must be claimed by at most one condition index.
        """
        from src.ir.model_ir import ModelIR
        from src.ir.symbols import AliasDef, SetDef

        model_ir = ModelIR()
        model_ir.add_set(SetDef(name="n", members=["n0", "n1"]))
        model_ir.add_set(SetDef(name="e", members=[], domain=("n", "n")))
        model_ir.add_alias(AliasDef(name="i", target="n"))
        model_ir.add_alias(AliasDef(name="n__", target="n"))

        cond = SetMembershipTest("e", (SymbolRef("n"), SymbolRef("i")))
        result = _remap_condition_to_domain(cond, ("n", "n__"), model_ir)

        assert isinstance(result, SetMembershipTest)
        assert [ix.name for ix in result.indices] == ["n", "n__"]

    def test_distinct_root_positions_are_unaffected(self):
        """#1350's srkandw shape still remaps by parent set, not by position."""
        from src.ir.model_ir import ModelIR
        from src.ir.symbols import SetDef

        model_ir = ModelIR()
        for s in ("t", "n", "j"):
            model_ir.add_set(SetDef(name=s, members=[]))
        model_ir.add_set(SetDef(name="tn", members=[], domain=("t", "n")))

        # tn(t,sn) against y's domain (j,t,n): `sn` must become `n`, NOT `t`.
        cond = SetMembershipTest("tn", (SymbolRef("t"), SymbolRef("sn")))
        result = _remap_condition_to_domain(cond, ("j", "t", "n"), model_ir)

        assert isinstance(result, SetMembershipTest)
        assert [ix.name for ix in result.indices] == ["t", "n"]
