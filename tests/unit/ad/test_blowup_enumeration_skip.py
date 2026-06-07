"""Sprint 27 #1385: translate-time-only short-circuit for the srpchase
dynamic-subset Cartesian blow-up shape.

An equation over a 1-D DYNAMIC subset (0 static members) of a LARGE parent set,
with a single (optionally negated) ``SetMembershipTest`` domain condition, whose
body sums over a 2-D set (``sum(ancestor(srn,n), ...)``), causes a >180s
translate_timeout (the blow-up is in differentiating the enumerated n×n bodies).
``enumerate_equation_instances`` skips AD enumeration for exactly that shape
(returns ``[]``); the stationarity cross-terms are deferred to Sprint 28.
"""

import pytest

from src.ad.index_mapping import (
    _condition_is_single_setmembership,
    _is_blowup_dynamic_subset_equation,
    enumerate_equation_instances,
)
from src.ir.ast import Binary, SetMembershipTest, Sum, SymbolRef, Unary, VarRef
from src.ir.model_ir import ModelIR
from src.ir.symbols import EquationDef, Rel, SetDef


def _srpchase_like_model(parent_size: int = 200) -> ModelIR:
    m = ModelIR()
    # Large parent set n
    m.sets["n"] = SetDef(name="n", members=[f"n{i}" for i in range(parent_size)])
    # Dynamic subsets of n (0 static members, runtime-populated)
    m.sets["srn"] = SetDef(name="srn", members=[], domain=("n",))
    m.sets["leaf"] = SetDef(name="leaf", members=[], domain=("n",))
    # 2-D set (the Cartesian membership filter)
    m.sets["ancestor"] = SetDef(name="ancestor", members=[], domain=("n", "n"))
    # slack(srn)$(not leaf(srn)).. y(srn) =e= x(srn) + sum(ancestor(srn,n), y(n))
    body_sum = Sum(
        ("n",),
        VarRef("y", ("n",)),
        SetMembershipTest("ancestor", (SymbolRef("srn"), SymbolRef("n"))),
    )
    rhs = Binary("+", VarRef("x", ("srn",)), body_sum)
    m.equations["slack"] = EquationDef(
        name="slack",
        domain=("srn",),
        relation=Rel.EQ,
        lhs_rhs=(VarRef("y", ("srn",)), rhs),
        condition=Unary("not", SetMembershipTest("leaf", (SymbolRef("srn"),))),
    )
    return m


@pytest.mark.unit
def test_condition_is_single_setmembership():
    smt = SetMembershipTest("leaf", (SymbolRef("srn"),))
    assert _condition_is_single_setmembership(smt) is True
    assert _condition_is_single_setmembership(Unary("not", smt)) is True
    # A binary/comparison condition is NOT a single set-membership.
    assert _condition_is_single_setmembership(Binary("<", SymbolRef("a"), SymbolRef("b"))) is False


@pytest.mark.unit
def test_gate_fires_for_srpchase_shape_and_skips_enumeration():
    m = _srpchase_like_model()
    eq = m.equations["slack"]
    assert _is_blowup_dynamic_subset_equation("slack", eq.domain, eq.condition, m) is True
    # enumerate_equation_instances must short-circuit to [] (skip AD enumeration).
    assert enumerate_equation_instances("slack", eq.domain, m, eq.condition) == []


@pytest.mark.unit
def test_gate_does_not_fire_when_parent_is_small():
    """The blow-up only matters for a LARGE parent — a small dynamic subset
    must NOT be skipped (its full enumeration is cheap and correct)."""
    m = _srpchase_like_model(parent_size=10)  # below the 100-member threshold
    eq = m.equations["slack"]
    assert _is_blowup_dynamic_subset_equation("slack", eq.domain, eq.condition, m) is False
    # Falls through to normal enumeration (over the parent n's members).
    assert enumerate_equation_instances("slack", eq.domain, m, eq.condition) != []


@pytest.mark.unit
def test_gate_does_not_fire_without_2d_set_sum():
    """A dynamic-subset equation whose body does NOT sum over a 2-D set is a
    normal (cheap) equation and must be enumerated normally."""
    m = _srpchase_like_model()
    # Replace the body with a plain reference (no Cartesian 2-D-set sum).
    eq = m.equations["slack"]
    m.equations["slack"] = EquationDef(
        name="slack",
        domain=eq.domain,
        relation=Rel.EQ,
        lhs_rhs=(VarRef("y", ("srn",)), VarRef("x", ("srn",))),
        condition=eq.condition,
    )
    eq2 = m.equations["slack"]
    assert _is_blowup_dynamic_subset_equation("slack", eq2.domain, eq2.condition, m) is False


@pytest.mark.unit
def test_gate_does_not_fire_for_static_subset():
    """A STATIC subset (with concrete members) is fully enumerable at compile
    time — only the runtime-populated dynamic subset triggers the blow-up."""
    m = _srpchase_like_model()
    # Give srn concrete static members → no longer a dynamic subset.
    m.sets["srn"] = SetDef(name="srn", members=["n0", "n1"], domain=("n",))
    eq = m.equations["slack"]
    assert _is_blowup_dynamic_subset_equation("slack", eq.domain, eq.condition, m) is False
