"""Unit tests for IndexOffset handling in subset condition detection.

Issue #1043: When a variable like k(t) is accessed with an IndexOffset (e.g.,
k(t+1) in an equation), the subset condition detection should treat that as
evidence of full-domain usage. Previously, IndexOffset accesses were silently
skipped, causing variables to be incorrectly restricted to a narrow subset
(e.g., tlast) when they should have had unconditional stationarity.
"""

import pytest

from src.ir.ast import Const, IndexOffset, SetMembershipTest, SymbolRef, VarRef
from src.ir.model_ir import ModelIR
from src.ir.symbols import EquationDef, Rel, SetDef
from src.kkt.stationarity import _find_variable_subset_condition


def _make_model_with_sets(**subsets: list[str]) -> ModelIR:
    """Create a ModelIR with set t and optional subsets."""
    model = ModelIR()
    model.sets["t"] = SetDef(
        name="t",
        members=["1990", "1995", "2000", "2005", "2010"],
    )
    for name, members in subsets.items():
        model.sets[name] = SetDef(name=name, domain=("t",), members=members)
    return model


@pytest.mark.unit
class TestIndexOffsetSubsetDetection:
    """Tests that IndexOffset accesses prevent false subset conditions."""

    def test_offset_access_prevents_subset_condition(self):
        """Variable accessed via k(t+1) should NOT get a subset condition.

        This is the etamac pattern: k(t) appears in totalcap as k(t+1),
        and in tc(tlast) as k(tlast). Without the fix, the function would
        only see k(tlast) and incorrectly restrict stat_k to $(tlast(t)).
        """
        model = _make_model_with_sets(tlast=["2010"])

        # totalcap(t).. k(t+1) =E= k(t) * spda + kn(t+1)
        # Uses IndexOffset for k(t+1) and plain k(t)
        totalcap = EquationDef(
            name="totalcap",
            domain=("t",),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("k", indices=(IndexOffset("t", Const(1), circular=False),)),
                VarRef("k", indices=("t",)),
            ),
        )
        model.equations["totalcap"] = totalcap

        # tc(tlast).. k(tlast) * expr =L= expr
        tc = EquationDef(
            name="tc",
            domain=("t",),
            relation=Rel.LE,
            lhs_rhs=(VarRef("k", indices=("tlast",)), Const(0)),
            condition=SetMembershipTest("tlast", (SymbolRef("t"),)),
        )
        model.equations["tc"] = tc

        result = _find_variable_subset_condition("k", ("t",), model)

        # k is accessed via IndexOffset(t+1) => full-domain usage => no condition
        assert result is None

    def test_subset_only_access_still_gets_condition(self):
        """Variable accessed ONLY via subset indices should still get a condition.

        When a variable is genuinely used only through a subset (no offsets),
        the condition should still be applied.
        """
        model = _make_model_with_sets(tfirst=["1990"])

        # fnewelec(tfirst).. en(tfirst) =E= expr
        eq = EquationDef(
            name="fnewelec",
            domain=("t",),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("en", indices=("tfirst",)), Const(0)),
            condition=SetMembershipTest("tfirst", (SymbolRef("t"),)),
        )
        model.equations["fnewelec"] = eq

        result = _find_variable_subset_condition("en", ("t",), model)

        # en is only accessed via tfirst => should get condition
        assert result is not None
        assert isinstance(result, SetMembershipTest)
        assert result.set_name == "tfirst"

    def test_offset_in_one_equation_overrides_subset_in_another(self):
        """IndexOffset in any equation should override subset access elsewhere.

        Even if one equation uses k(tlast) and another uses k(t+1),
        the IndexOffset evidence should dominate and result in no condition.
        """
        model = _make_model_with_sets(tlast=["2010"])

        # eq_with_offset(t).. k(t+1) =E= expr
        eq1 = EquationDef(
            name="eq_with_offset",
            domain=("t",),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("k", indices=(IndexOffset("t", Const(1), circular=False),)),
                Const(0),
            ),
        )
        model.equations["eq_with_offset"] = eq1

        # eq_with_subset(tlast).. k(tlast) =L= expr
        eq2 = EquationDef(
            name="eq_with_subset",
            domain=("t",),
            relation=Rel.LE,
            lhs_rhs=(VarRef("k", indices=("tlast",)), Const(0)),
            condition=SetMembershipTest("tlast", (SymbolRef("t"),)),
        )
        model.equations["eq_with_subset"] = eq2

        result = _find_variable_subset_condition("k", ("t",), model)
        assert result is None

    def test_non_matching_offset_base_does_not_prevent_condition(self):
        """IndexOffset whose base doesn't match declared domain is ignored.

        If a variable k(m, t) is accessed as k(m, tfirst) and k(m+1, tfirst),
        the IndexOffset on m should not prevent the subset condition on t.
        """
        model = ModelIR()
        model.sets["m"] = SetDef(name="m", members=["a", "b", "c"])
        model.sets["t"] = SetDef(name="t", members=["1990", "1995", "2000"])
        model.sets["tfirst"] = SetDef(name="tfirst", domain=("t",), members=["1990"])

        # eq1(m,t).. x(m+1, tfirst) =E= expr
        eq = EquationDef(
            name="eq1",
            domain=("m", "t"),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("x", indices=(IndexOffset("m", Const(1), circular=False), "tfirst")),
                Const(0),
            ),
        )
        model.equations["eq1"] = eq

        result = _find_variable_subset_condition("x", ("m", "t"), model)

        # IndexOffset is on m (not t), so t can still be subset-restricted
        assert result is not None
        assert isinstance(result, SetMembershipTest)
        assert result.set_name == "tfirst"
